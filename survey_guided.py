"""
Modo guiado: elegir pregunta del cuestionario, filtros y tipo de análisis sin lenguaje natural.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal

import pandas as pd

from quant_advanced import (
    bracket_sub_item_label,
    crosstab_chi_square_smart,
    descriptive_one_column,
    detect_survey_ordinals_and_question_blocks,
    questionnaire_parent_stem,
)
from quant_summaries import chi_square_explanatory, descriptive_explanatory
from survey_intel import ColumnProfile, frequency_table, is_timestamp_column

AnalysisKind = Literal["freq", "crosstab", "count_values", "open_text"]

FILTER_SPECS: list[tuple[str, list[str]]] = [
    ("Unidad académica", ["unidad academica", "unidad académica", "cursando"]),
    ("Año de carrera", ["año de la carrera", "ano de la carrera"]),
    ("Edad", ["edad:"]),
    ("Género", ["género", "genero"]),
    ("¿Trabaja actualmente?", ["trabajás", "trabajas actualmente"]),
]


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
        tables["conteo"] = pd.DataFrame(
            {"categoría": spec.value_pick, "n_en_muestra_filtrada": [int((norm == v).sum()) for v in spec.value_pick]}
        )
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
) -> str:
    if not result.ok:
        return (
            f"**No se pudo completar el análisis.**\n\n{result.error or ''}\n\n"
            "Revisá los filtros o elegí otra pregunta del listado."
        )

    filt_txt = ""
    if spec.cohort_filters:
        parts = [f"**{k}:** {', '.join(v[:3])}{'…' if len(v) > 3 else ''}" for k, v in spec.cohort_filters.items()]
        filt_txt = "\n\n**Filtros de muestra activos:** " + "; ".join(parts) + f"\n\n**Casos en la cohorte:** {result.n_cohort} de {result.n_total} encuestados."

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
