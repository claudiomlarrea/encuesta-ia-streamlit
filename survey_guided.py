"""
Modo guiado: elegir pregunta del cuestionario, filtros y tipo de análisis sin lenguaje natural.
"""
from __future__ import annotations

import hashlib
import io
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

import pandas as pd
import streamlit as st

from quant_advanced import (
    GroupComparisonResult,
    bracket_sub_item_label,
    crosstab_chi_square_smart,
    descriptive_one_column,
    detect_survey_ordinals_and_question_blocks,
    prepare_crosstab_for_display,
    questionnaire_parent_stem,
)
from quant_summaries import chi_square_explanatory, descriptive_explanatory
from survey_intel import ColumnProfile, frequency_table, is_timestamp_column

AnalysisKind = Literal["freq", "crosstab", "count_values", "open_text"]

ANALYSIS_KIND_LABELS: dict[AnalysisKind, str] = {
    "freq": "Frecuencias y porcentajes",
    "crosstab": "Cruce con otra pregunta (χ²)",
    "count_values": "Contar categorías elegidas",
    "open_text": "Respuestas de texto (muestra)",
}

FILTER_SPECS: list[tuple[str, list[str]]] = [
    ("Unidad académica", ["unidad academica", "unidad académica", "cursando"]),
    ("Año de carrera", ["año de la carrera", "ano de la carrera"]),
    ("Edad", ["edad:"]),
    ("Género", ["género", "genero"]),
    ("¿Trabaja actualmente?", ["trabajás", "trabajas actualmente"]),
]

# (etiqueta del filtro, frase si están todas las opciones, prefijo si son algunas)
_COHORT_FILTER_PHRASES: dict[str, tuple[str, str]] = {
    "Unidad académica": ("Todas las unidades académicas", "Unidades académicas"),
    "Año de carrera": ("Todos los años de la carrera", "Años de carrera"),
    "Edad": ("Todas las edades", "Edades"),
    "Género": ("Todos los géneros", "Género"),
    "¿Trabaja actualmente?": ("Todas las respuestas sobre trabajo actual", "Trabajo actual"),
}


@dataclass
class ColumnChoice:
    label: str
    column: str
    block_id: int
    kind: str
    subtype: str
    n_valid: int
    full_text: str = ""


@dataclass
class FilterColumn:
    label: str
    column: str
    options: list[str]


@dataclass
class GuidedSpec:
    primary_column: str
    analysis: AnalysisKind
    secondary_column: str | None = None
    cohort_filters: dict[str, list[str]] = field(default_factory=dict)
    value_pick: list[str] = field(default_factory=list)


@dataclass
class GuidedResult:
    ok: bool
    analysis: AnalysisKind
    n_total: int
    n_cohort: int
    n_result: int
    tables: dict[str, pd.DataFrame]
    metrics: dict[str, Any]
    error: str | None = None


def _normalize_question_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text).strip().replace("\n", " "))


def _full_item_text(column_name: str) -> str:
    sub = bracket_sub_item_label(column_name)
    if sub:
        return _normalize_question_text(sub)
    return _normalize_question_text(questionnaire_parent_stem(column_name))


def _column_score(col: str, hints: list[str]) -> float:
    lc = col.lower().replace("\n", " ")
    return sum(1.0 + len(h) / 40 for h in hints if h in lc)


def discover_filter_columns(df: pd.DataFrame) -> list[FilterColumn]:
    out: list[FilterColumn] = []
    used: set[str] = set()
    for label, hints in FILTER_SPECS:
        best_col: str | None = None
        best_sc = 0.0
        for c in df.columns:
            if is_timestamp_column(c) or c in used:
                continue
            sc = _column_score(str(c), hints)
            if sc > best_sc:
                best_sc = sc
                best_col = str(c)
        if not best_col or best_sc <= 0:
            continue
        used.add(best_col)
        opts = (
            df[best_col]
            .dropna()
            .astype(str)
            .str.strip()
            .replace({"nan": ""})
        )
        opts = opts[opts.astype(bool)]
        top = opts.value_counts().head(25).index.astype(str).tolist()
        if not top:
            continue
        out.append(FilterColumn(label=label, column=best_col, options=top))
    return out


def build_column_choices(df: pd.DataFrame, profiles: list[ColumnProfile]) -> list[ColumnChoice]:
    prof_map = {p.name: p for p in profiles}
    detail, _blocks = detect_survey_ordinals_and_question_blocks(df)
    seen_labels: dict[str, int] = {}

    def _append_choice(
        choices: list[ColumnChoice],
        col: str,
        blk: int,
        item_n: int,
        kind: str,
        subtype: str,
    ) -> None:
        full = _full_item_text(col)
        label = f"#{blk} · {full}" if blk else full
        if label in seen_labels:
            seen_labels[label] += 1
            label = f"{label} (ítem {item_n})"
        else:
            seen_labels[label] = 1
        choices.append(
            ColumnChoice(
                label=label,
                column=col,
                block_id=blk,
                kind=kind,
                subtype=subtype,
                n_valid=int(df[col].notna().sum()),
                full_text=full,
            )
        )

    if detail.empty or "_columna_interna" not in detail.columns:
        choices: list[ColumnChoice] = []
        for i, c in enumerate(df.columns):
            if is_timestamp_column(c):
                continue
            col = str(c)
            p = prof_map.get(col)
            _append_choice(
                choices,
                col,
                0,
                i + 1,
                p.kind if p else "estructurada",
                p.subtype if p else "",
            )
        return choices

    choices: list[ColumnChoice] = []
    for _, row in detail.iterrows():
        col = str(row["_columna_interna"])
        if col not in df.columns:
            continue
        p = prof_map.get(col)
        blk = int(row.get("#_bloque", 0))
        item_n = int(row.get("ítem_en_el_bloque", 1))
        _append_choice(
            choices,
            col,
            blk,
            item_n,
            p.kind if p else "estructurada",
            p.subtype if p else str(row.get("esquema_detectado", "")),
        )
    return choices


def _filter_column_by_label(filter_cols: list[FilterColumn], label: str) -> FilterColumn | None:
    return next((fc for fc in filter_cols if fc.label == label), None)


def cohort_filters_display_lines(
    filter_cols: list[FilterColumn],
    active: dict[str, list[str]],
    *,
    max_items: int = 8,
) -> list[str]:
    """
    Texto legible por dimensión de filtro.
    Si se eligieron todas las opciones del multiselect → frase tipo «Todas las unidades…».
    """
    lines: list[str] = []
    for label, picked in active.items():
        if not picked:
            continue
        fc = _filter_column_by_label(filter_cols, label)
        all_phrase, partial_prefix = _COHORT_FILTER_PHRASES.get(
            label, (f"Todas las categorías de {label}", label)
        )
        opts = list(fc.options) if fc else []
        picked_clean = [str(v).strip() for v in picked if str(v).strip()]
        if opts and set(picked_clean) >= set(opts) and len(picked_clean) >= len(opts):
            lines.append(all_phrase)
            continue
        shown = picked_clean[:max_items]
        tail = f" (+{len(picked_clean) - max_items} más)" if len(picked_clean) > max_items else ""
        lines.append(f"{partial_prefix}: {', '.join(shown)}{tail}")
    return lines


def short_choice_label(label: str, *, max_len: int = 88) -> str:
    """Quita prefijo «#n ·» del selector para leerlo en leyendas."""
    s = str(label).strip()
    if "·" in s:
        s = s.split("·", 1)[1].strip()
    return s[:max_len] + ("…" if len(s) > max_len else "")


def crosstab_table_caption(
    row_label: str,
    col_label: str,
    *,
    multiselect_note: str | None = None,
) -> str:
    """
    Explica la tabla de cruce: por qué hay varias filas y columnas (categorías de cada pregunta).
    """
    row = short_choice_label(row_label)
    col = short_choice_label(col_label)
    base = (
        f"**Filas ({row}):** cada fila es **una opción de respuesta** a la pregunta elegida arriba "
        f"(por eso ves tantas filas como categorías distintas tenga esa pregunta). "
        f"**Columnas ({col}):** cada columna es **una opción** de la pregunta con la que cruzaste "
        f"(p. ej. Nunca, A veces, Siempre…). "
        f"**Cada número** en la tabla = **personas** de la muestra filtrada con esa combinación fila×columna. "
        f"**Total fila** / **Total columna** suman conteos."
    )
    if multiselect_note:
        base += f"\n\n{multiselect_note}"
    return base


def cohort_filter_scope_markdown(
    filter_cols: list[FilterColumn],
    active: dict[str, list[str]],
    *,
    n_cohort: int | None = None,
    n_total: int | None = None,
) -> str:
    """Bloque corto para la UI: qué submuestra se está analizando."""
    lines = cohort_filters_display_lines(filter_cols, active)
    if not lines:
        base = "**Muestra analizada:** toda la encuesta (sin filtros de cohorte)."
    else:
        base = "**Muestra analizada:** " + " · ".join(lines) + "."
    if n_cohort is not None and n_total is not None:
        base += f" (**{n_cohort}** de **{n_total}** encuestados)."
    return base


def _csv_cell(value: Any) -> str:
    s = str(value).replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    if any(ch in s for ch in (",", '"', ";")):
        return '"' + s.replace('"', '""') + '"'
    return s


def _csv_row(*cells: Any) -> str:
    return ",".join(_csv_cell(c) for c in cells)


def build_guided_report_csv(
    *,
    spec: GuidedSpec,
    result: GuidedResult,
    primary_label: str,
    primary_full_text: str,
    table: pd.DataFrame,
    table_kind: str,
    filter_cols: list[FilterColumn] | None = None,
    secondary_label: str | None = None,
    secondary_full_text: str | None = None,
) -> bytes:
    """
    CSV con encabezado legible (preguntas, filtros, tipo de análisis) y luego la tabla.
    """
    buf = io.StringIO()
    w = buf.write

    w(_csv_row("Encuesta Clara — Informe de consulta guiada"))
    w("\n")
    w(_csv_row("1. Pregunta analizada", primary_full_text or short_choice_label(primary_label)))
    w("\n")
    w(_csv_row("Tipo de análisis", ANALYSIS_KIND_LABELS.get(spec.analysis, spec.analysis)))
    w("\n")

    if spec.analysis == "crosstab":
        sec_txt = secondary_full_text or (
            short_choice_label(secondary_label) if secondary_label else ""
        )
        w(_csv_row("2. Pregunta de cruce (columnas de la tabla)", sec_txt or "—"))
        w("\n")
    elif spec.analysis == "count_values" and spec.value_pick:
        w(_csv_row("2. Categorías contadas", ", ".join(spec.value_pick[:20])))
        if len(spec.value_pick) > 20:
            w(_csv_row("", f"(+{len(spec.value_pick) - 20} más)"))
        w("\n")

    w(_csv_row("3. Filtros de muestra aplicados"))
    filt_lines = (
        cohort_filters_display_lines(filter_cols or [], spec.cohort_filters)
        if spec.cohort_filters
        else []
    )
    if filt_lines:
        for fl in filt_lines:
            w(_csv_row("", fl))
    else:
        w(_csv_row("", "Toda la encuesta (sin filtros de cohorte)"))
    w("\n")
    w(
        _csv_row(
            "Casos en la muestra",
            f"{result.n_cohort} de {result.n_total} encuestados",
        )
    )
    w("\n\n")

    if table_kind == "cruce":
        row_hdr = f"Opción · {short_choice_label(primary_label, max_len=120)}"
        show = prepare_crosstab_for_display(table, index_label=row_hdr)
    else:
        show = table.copy()

    w(_csv_row("4. Tabla de resultados"))
    w("\n")
    show.to_csv(buf, index=False, lineterminator="\n")

    return ("\ufeff" + buf.getvalue()).encode("utf-8")


def build_significance_report_csv(
    *,
    y_label: str,
    g_label: str,
    ordinal_scheme: str,
    n_pairs: int,
    n_work: int,
    n_dataset: int,
    res: GroupComparisonResult,
    sample: pd.DataFrame,
    inverted: bool = False,
) -> bytes:
    """CSV: variables, tamaños de grupo, resumen descriptivo y pruebas (Welch / MW / ANOVA / K-W)."""
    buf = io.StringIO()
    w = buf.write

    w(_csv_row("Encuesta Clara — Informe prueba de significancia"))
    w("\n")
    w(_csv_row("1. Variable respuesta (ordinal)", y_label))
    w(_csv_row("2. Variable de agrupación", g_label))
    w(_csv_row("Esquema ordinal inferido", ordinal_scheme.replace("\n", " ")[:500]))
    if inverted:
        w(_csv_row("", "Escala invertida (ítem marcado en protocolo inverso)"))
    w(
        _csv_row(
            "Casos analizados",
            f"{n_pairs} filas válidas (respuesta + grupo) · submuestra {n_work} · encuesta {n_dataset}",
        )
    )
    w(_csv_row("Número de grupos (k)", res.n_groups))
    if res.message:
        w(_csv_row("Nota", res.message))
    w("\n")

    w(_csv_row("3. Tamaños de grupo"))
    w("\n")
    sizes_df = pd.DataFrame(
        [{"Grupo": k, "n": v} for k, v in res.group_sizes.items()]
    )
    sizes_df.to_csv(buf, index=False, lineterminator="\n")
    w("\n")

    w(_csv_row("4. Resumen por grupo (escala ordinal codificada)"))
    w("\n")
    desc = (
        sample.groupby("g", dropna=False)["y"]
        .agg(["count", "mean", "median", "std"])
        .round(3)
        .reset_index()
    )
    desc.columns = ["Grupo", "n", "Media ordinal", "Mediana", "Desv. típica"]
    desc.to_csv(buf, index=False, lineterminator="\n")
    w("\n")

    w(_csv_row("5. Pruebas estadísticas"))
    w("\n")
    test_rows: list[dict[str, Any]] = []
    if res.n_groups == 2:
        if res.t_stat is not None and res.t_p is not None:
            test_rows.append(
                {
                    "Prueba": "t de Student (Welch)",
                    "Estadístico": round(res.t_stat, 4),
                    "p_valor": round(res.t_p, 6),
                }
            )
        if res.mw_U is not None and res.mw_p is not None:
            test_rows.append(
                {
                    "Prueba": "Mann–Whitney U",
                    "Estadístico": round(res.mw_U, 4),
                    "p_valor": round(res.mw_p, 6),
                }
            )
    if res.anova_F is not None and res.anova_p is not None:
        test_rows.append(
            {
                "Prueba": "ANOVA",
                "Estadístico": round(res.anova_F, 4),
                "p_valor": round(res.anova_p, 6),
            }
        )
    if res.kruskal_H is not None and res.kruskal_p is not None:
        test_rows.append(
            {
                "Prueba": "Kruskal–Wallis",
                "Estadístico": round(res.kruskal_H, 4),
                "p_valor": round(res.kruskal_p, 6),
            }
        )
    if test_rows:
        pd.DataFrame(test_rows).to_csv(buf, index=False, lineterminator="\n")
    else:
        w(_csv_row("", "No hay pruebas disponibles con los datos actuales."))

    return ("\ufeff" + buf.getvalue()).encode("utf-8")


def build_cronbach_report_csv(
    *,
    item_labels: list[str],
    n_work: int,
    n_dataset: int,
    diag_sum: pd.DataFrame,
    diag_tbl: pd.DataFrame,
    alpha: float | None = None,
    n_cases: int = 0,
    n_items: int = 0,
    rep_cron: pd.DataFrame | None = None,
    mat_describe: pd.DataFrame | None = None,
    warnings: list[str] | None = None,
) -> bytes:
    """CSV: ítems elegidos, diagnóstico de codificación, α y tablas auxiliares."""
    buf = io.StringIO()
    w = buf.write

    w(_csv_row("Encuesta Clara — Informe Alfa de Cronbach"))
    w("\n")
    w(_csv_row("1. Ítems incluidos en el análisis"))
    for lab in item_labels:
        w(_csv_row("", lab))
    w("\n")
    w(_csv_row("Casos en submuestra / encuesta", f"{n_work} / {n_dataset}"))
    if alpha is not None and alpha == alpha:
        w(_csv_row("Alfa de Cronbach", f"{alpha:.4f}"))
        w(_csv_row("Filas list‑wise (todas las escalas codificadas)", n_cases))
        w(_csv_row("Cantidad de ítems", n_items))
    else:
        w(_csv_row("Alfa de Cronbach", "No calculable (pocos casos completos o varianza nula)"))
    if warnings:
        w(_csv_row("Advertencias", " | ".join(warnings[:6])))
    w("\n")

    w(_csv_row("2. Resumen de superposición (list‑wise)"))
    w("\n")
    diag_sum.to_csv(buf, index=False, lineterminator="\n")
    w("\n")

    w(_csv_row("3. Diagnóstico por ítem (codificación ordinal)"))
    w("\n")
    diag_tbl.to_csv(buf, index=False, lineterminator="\n")
    w("\n")

    if rep_cron is not None and not rep_cron.empty:
        w(_csv_row("4. Escala efectiva por ítem"))
        w("\n")
        rep_cron.to_csv(buf, index=False, lineterminator="\n")
        w("\n")

    if mat_describe is not None and not mat_describe.empty:
        w(_csv_row("5. Estadísticos por ítem (escala codificada, casos completos)"))
        w("\n")
        mat_describe.to_csv(buf, lineterminator="\n")
        w("\n")

    return ("\ufeff" + buf.getvalue()).encode("utf-8")


def build_pca_efa_report_csv(
    *,
    item_labels: list[str],
    n_work: int,
    n_dataset: int,
    n_pc_requested: int,
    n_factors_requested: int,
    latent_name: str,
    use_poly: bool,
    diag_sum: pd.DataFrame,
    diag_tbl: pd.DataFrame,
    n_complete: int,
    rep_pca: pd.DataFrame | None = None,
    scale_warnings: list[str] | None = None,
    loadings_pca: pd.DataFrame | None = None,
    var_pca: list[float] | None = None,
    loadings_efa: pd.DataFrame | None = None,
    eigenvalues: list[float] | None = None,
    status_note: str = "",
) -> bytes:
    """CSV: ítems, diagnóstico ordinal, cargas PCA/AFE si se calcularon."""
    buf = io.StringIO()
    w = buf.write

    w(_csv_row("Encuesta Clara — Informe PCA / AFE"))
    w("\n")
    w(_csv_row("1. Ítems incluidos"))
    for lab in item_labels:
        w(_csv_row("", lab))
    w("\n")
    w(_csv_row("Casos en submuestra / encuesta", f"{n_work} / {n_dataset}"))
    w(_csv_row("Casos list-wise (todos los ítems codificados)", n_complete))
    w(_csv_row("Dimensiones PCA solicitadas", n_pc_requested))
    w(_csv_row("Factores AFE solicitados", n_factors_requested))
    w(_csv_row("Correlaciones policóricas", "Sí" if use_poly else "No"))
    w(_csv_row("Nombre factor (export lavaan)", latent_name))
    if status_note:
        w(_csv_row("Estado del análisis", status_note))
    if scale_warnings:
        w(_csv_row("Avisos de escala", " | ".join(scale_warnings[:6])))
    w("\n")

    w(_csv_row("2. Resumen de superposición (list-wise)"))
    w("\n")
    diag_sum.to_csv(buf, index=False, lineterminator="\n")
    w("\n")

    w(_csv_row("3. Diagnóstico por ítem (codificación ordinal)"))
    w("\n")
    diag_tbl.to_csv(buf, index=False, lineterminator="\n")
    w("\n")

    if rep_pca is not None and not rep_pca.empty:
        w(_csv_row("4. Escala efectiva por ítem (casos completos)"))
        w("\n")
        rep_pca.to_csv(buf, index=False, lineterminator="\n")
        w("\n")

    if var_pca:
        w(_csv_row("5. Varianza explicada (PCA)"))
        w("\n")
        for i, v in enumerate(var_pca, start=1):
            w(_csv_row(f"PC{i}", f"{float(v):.6f}"))
        w("\n")

    if loadings_pca is not None and not loadings_pca.empty:
        w(_csv_row("6. Cargas PCA"))
        w("\n")
        loadings_pca.round(4).to_csv(buf, lineterminator="\n")
        w("\n")

    if loadings_efa is not None and not loadings_efa.empty:
        w(_csv_row("7. Cargas AFE rotadas (Varimax)"))
        w("\n")
        loadings_efa.round(4).to_csv(buf, lineterminator="\n")
        w("\n")

    if eigenvalues:
        w(_csv_row("8. Autovalores AFE"))
        w("\n")
        w(_csv_row("Autovalor", " | ".join(f"{v:.4f}" for v in eigenvalues[:12])))
        w("\n")

    return ("\ufeff" + buf.getvalue()).encode("utf-8")


def _checkbox_key(session_key: str, column: str) -> str:
    digest = hashlib.md5(column.encode("utf-8")).hexdigest()[:16]
    return f"{session_key}__chk__{digest}"


def pick_likert_columns(
    options: list[str],
    label_fn: Callable[[str], str],
    *,
    session_key: str,
    filter_input_key: str,
    select_all_key: str,
    clear_all_key: str,
) -> list[str]:
    """
    Selector de ítems sin st.multiselect (evita el banner flotante «No results» de Streamlit).
    """
    if session_key not in st.session_state:
        st.session_state[session_key] = []

    st.markdown("**Ítems Likert / frecuencia** (marcá al menos 2)")
    filt = st.text_input(
        "Buscar en la lista",
        key=filter_input_key,
        placeholder="Filtrá por palabra (p. ej. «IA», «frecuencia», «uso»)…",
    )
    q = filt.strip().lower()
    visible = [
        o
        for o in options
        if not q or q in label_fn(o).lower() or q in str(o).lower()
    ]

    b1, b2, _ = st.columns([1, 1, 2])
    with b1:
        if st.button("Marcar visibles", key=select_all_key, use_container_width=True):
            cur = set(st.session_state[session_key])
            cur.update(visible)
            st.session_state[session_key] = [o for o in options if o in cur]
            st.rerun()
    with b2:
        if st.button("Limpiar selección", key=clear_all_key, use_container_width=True):
            st.session_state[session_key] = []
            for k in list(st.session_state.keys()):
                if str(k).startswith(f"{session_key}__chk__"):
                    st.session_state.pop(k, None)
            st.rerun()

    prev: list[str] = list(st.session_state[session_key])
    picked_visible: list[str] = []
    with st.container(height=340):
        c1, c2 = st.columns(2)
        for i, opt in enumerate(visible):
            with (c1 if i % 2 == 0 else c2):
                ck = _checkbox_key(session_key, opt)
                if st.checkbox(
                    label_fn(opt),
                    value=opt in prev,
                    key=ck,
                ):
                    picked_visible.append(opt)

    hidden = [o for o in prev if o not in visible]
    merged = hidden + [o for o in picked_visible if o not in hidden]
    st.session_state[session_key] = merged
    st.caption(f"**{len(merged)}** ítems seleccionados.")
    if merged:
        preview = ", ".join(label_fn(o)[:48] for o in merged[:8])
        if len(merged) > 8:
            preview += f" … (+{len(merged) - 8} más)"
        st.caption(preview)
    return merged


def apply_cohort_filters(df: pd.DataFrame, filters: dict[str, list[str]]) -> pd.DataFrame:
    out = df
    for col, values in filters.items():
        if not values or col not in out.columns:
            continue
        norm = out[col].astype(str).str.strip()
        mask = norm.isin([str(v) for v in values])
        out = out.loc[mask]
    return out


def analysis_options_for_column(choice: ColumnChoice) -> list[tuple[str, AnalysisKind]]:
    if choice.kind == "abierta":
        return [("Ver respuestas de texto (muestra)", "open_text")]
    opts = [
        ("Frecuencias y porcentajes", "freq"),
        ("Cruce con otra pregunta (χ²)", "crosstab"),
        ("Contar categorías elegidas", "count_values"),
    ]
    return opts


def run_guided_analysis(
    df_full: pd.DataFrame,
    df_cohort: pd.DataFrame,
    spec: GuidedSpec,
) -> GuidedResult:
    n_total = len(df_full)
    n_cohort = len(df_cohort)
    tables: dict[str, pd.DataFrame] = {}
    metrics: dict[str, Any] = {}
    col = spec.primary_column

    if n_cohort == 0:
        return GuidedResult(
            ok=False,
            analysis=spec.analysis,
            n_total=n_total,
            n_cohort=0,
            n_result=0,
            tables=tables,
            metrics=metrics,
            error="No queda ningún caso con los filtros elegidos. Ampliá la muestra o quitá filtros.",
        )

    if col not in df_cohort.columns:
        return GuidedResult(
            ok=False,
            analysis=spec.analysis,
            n_total=n_total,
            n_cohort=n_cohort,
            n_result=0,
            tables=tables,
            metrics=metrics,
            error="La columna elegida no está en los datos.",
        )

    if spec.analysis == "freq":
        ft = frequency_table(df_cohort[col])
        tables["frecuencias"] = ft
        metrics["desc"] = descriptive_one_column(df_cohort[col])
        return GuidedResult(
            ok=True,
            analysis=spec.analysis,
            n_total=n_total,
            n_cohort=n_cohort,
            n_result=int(df_cohort[col].notna().sum()),
            tables=tables,
            metrics=metrics,
        )

    if spec.analysis == "open_text":
        texts = df_cohort[col].dropna().astype(str).str.strip()
        texts = texts[texts.astype(bool)]
        tables["muestra"] = pd.DataFrame({"respuesta": texts.head(15)})
        metrics["n_text"] = int(len(texts))
        return GuidedResult(
            ok=True,
            analysis=spec.analysis,
            n_total=n_total,
            n_cohort=n_cohort,
            n_result=int(len(texts)),
            tables=tables,
            metrics=metrics,
        )

    if spec.analysis == "count_values":
        if not spec.value_pick:
            return GuidedResult(
                ok=False,
                analysis=spec.analysis,
                n_total=n_total,
                n_cohort=n_cohort,
                n_result=0,
                tables=tables,
                metrics=metrics,
                error="Elegí al menos una categoría para contar.",
            )
        norm = df_cohort[col].astype(str).str.strip()
        mask = norm.isin([str(v) for v in spec.value_pick])
        n_match = int(mask.sum())
        metrics["values"] = spec.value_pick
        metrics["pct_cohort"] = round(100.0 * n_match / n_cohort, 2) if n_cohort else 0.0
        metrics["pct_total"] = round(100.0 * n_match / n_total, 2) if n_total else 0.0
        conteo_rows = [
            {"categoría": v, "n_en_muestra_filtrada": int((norm == v).sum())}
            for v in spec.value_pick
        ]
        if len(spec.value_pick) > 1:
            conteo_rows.append(
                {
                    "categoría": "TOTAL (personas con al menos una categoría elegida)",
                    "n_en_muestra_filtrada": n_match,
                }
            )
        else:
            conteo_rows.append(
                {"categoría": "TOTAL", "n_en_muestra_filtrada": n_match}
            )
        tables["conteo"] = pd.DataFrame(conteo_rows)
        return GuidedResult(
            ok=True,
            analysis=spec.analysis,
            n_total=n_total,
            n_cohort=n_cohort,
            n_result=n_match,
            tables=tables,
            metrics=metrics,
        )

    if spec.analysis == "crosstab":
        col2 = spec.secondary_column
        if not col2 or col2 == col:
            return GuidedResult(
                ok=False,
                analysis=spec.analysis,
                n_total=n_total,
                n_cohort=n_cohort,
                n_result=0,
                tables=tables,
                metrics=metrics,
                error="Elegí otra pregunta para el cruce.",
            )
        res = crosstab_chi_square_smart(df_cohort, col, col2)
        tables["cruce"] = res["tabla"]
        metrics["chi2"] = res
        return GuidedResult(
            ok=True,
            analysis=spec.analysis,
            n_total=n_total,
            n_cohort=n_cohort,
            n_result=int(res["n"]),
            tables=tables,
            metrics=metrics,
        )

    return GuidedResult(
        ok=False,
        analysis=spec.analysis,
        n_total=n_total,
        n_cohort=n_cohort,
        n_result=0,
        tables=tables,
        metrics=metrics,
        error="Tipo de análisis no reconocido.",
    )


def interpret_guided(
    spec: GuidedSpec,
    result: GuidedResult,
    *,
    col_labels: dict[str, str],
    primary_label: str,
    secondary_label: str | None = None,
    filter_cols: list[FilterColumn] | None = None,
) -> str:
    if not result.ok:
        return (
            f"**No se pudo completar el análisis.**\n\n{result.error or ''}\n\n"
            "Revisá los filtros o elegí otra pregunta del listado."
        )

    filt_txt = ""
    if spec.cohort_filters:
        parts = (
            cohort_filters_display_lines(filter_cols, spec.cohort_filters)
            if filter_cols
            else [
                f"{k}: {', '.join(v[:4])}{'…' if len(v) > 4 else ''}"
                for k, v in spec.cohort_filters.items()
            ]
        )
        filt_txt = (
            "\n\n**Filtros de muestra:** "
            + " · ".join(parts)
            + f"\n\n**Casos en la cohorte:** {result.n_cohort} de {result.n_total} encuestados."
        )

    if result.analysis == "freq":
        desc = result.metrics.get("desc", {})
        ft = result.tables.get("frecuencias")
        body = descriptive_explanatory(desc, ft)
        return (
            f"### Resultado — «{primary_label}»\n\n"
            f"Distribución sobre **{result.n_cohort}** personas"
            f"{filt_txt}\n\n{body}"
        )

    if result.analysis == "count_values":
        n = result.n_result
        pct_c = result.metrics.get("pct_cohort", 0)
        pct_t = result.metrics.get("pct_total", 0)
        vals = ", ".join(f"«{v[:40]}»" for v in spec.value_pick[:5])
        return (
            f"### Resultado — conteo\n\n"
            f"En la muestra filtrada (**{result.n_cohort}** personas), **{n}** "
            f"({pct_c:.1f} % de esa cohorte) respondieron en la pregunta elegida con: {vals}.\n\n"
            f"Sobre el total del archivo (**{result.n_total}**), son **{pct_t:.1f} %**."
            f"{filt_txt}\n\n"
            "*Conteo descriptivo; no implica causalidad.*"
        )

    if result.analysis == "open_text":
        n = result.metrics.get("n_text", 0)
        return (
            f"### Respuestas abiertas — «{primary_label}»\n\n"
            f"Hay **{n}** textos no vacíos en la cohorte"
            f"{filt_txt}\n\n"
            "Revisá la tabla de ejemplos. Para temas o sentimiento automático usá **Análisis cualitativo**."
        )

    if result.analysis == "crosstab" and "chi2" in result.metrics:
        res = result.metrics["chi2"]
        sec = secondary_label or spec.secondary_column or ""
        ms_note = ""
        if res.get("multiselect_note"):
            ms_note = f"\n\n{res['multiselect_note']}\n"
        return (
            f"### Cruce — «{primary_label}» × «{sec}»\n{filt_txt}{ms_note}\n"
            + chi_square_explanatory(
                chi2=res["chi2"],
                gl=res["gl"],
                p_valor=res["p_valor"],
                cramers_v=res["cramers_v"],
                n=res["n"],
                row_lab=primary_label,
                col_lab=sec,
                tabla=res.get("tabla"),
            )
        )

    return "Análisis completado; revisá las tablas."
