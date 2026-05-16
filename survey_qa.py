"""
Consultas en lenguaje natural sobre la encuesta cargada.
Planifica filtros y análisis con heurísticas en español; ejecuta con utilidades del panel (sin LLM obligatorio).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np
import pandas as pd

from quant_advanced import (
    crosstab_chi_square,
    descriptive_one_column,
    detect_best_ordinal,
)
from quant_summaries import chi_square_explanatory, descriptive_explanatory
from survey_intel import ColumnProfile, _normalize_cell, is_timestamp_column

IntentKind = Literal[
    "count_filtered",
    "describe",
    "crosstab",
    "open_text",
    "unsupported",
]

# Alias de unidades académicas (código o fragmento de texto en respuesta)
UNIT_ALIASES: dict[str, list[str]] = {
    "FBOSCO": ["don bosco", "fbosco", "enología", "enologia", "alimentación", "alimentacion"],
    "FCEESJ": ["económicas san juan", "economicas san juan", "fceesj"],
    "FEDSJ": ["educación san juan", "educacion san juan", "fedsj"],
    "FFYHSJ": ["filosofía", "filosofia", "humanidades", "ffyhsj"],
    "FDCSSJ": ["derecho", "ciencias sociales san juan", "fdcssj"],
    "FCMSJ": ["ciencias médicas", "ciencias medicas", "fcmsj"],
    "FCQYTSJ": ["química", "quimica", "tecnológicas", "fcqytsj"],
    "FCVSL": ["veterinarias", "fcvsl"],
    "ESEGSJ": ["seguridad", "esegsj"],
    "ISB": ["buenaventura", " instituto san buen"],
    "ISDSM": ["santa maría", "santa maria", "isdsm"],
}

FREQ_HIGH_TERMS = frozenset(
    {
        "frecuentemente",
        "siempre",
        "habitualmente",
        "a diario",
        "casi siempre",
        "muchas veces",
    }
)

FREQ_LOW_TERMS = frozenset({"nunca", "rara vez", "pocas veces"})


@dataclass
class FilterSpec:
    column: str
    op: str  # contains_text | equals_norm | ordinal_at_least | not_working
    value: Any
    label: str


@dataclass
class QueryPlan:
    intent: IntentKind
    question: str
    filters: list[FilterSpec] = field(default_factory=list)
    primary_column: str | None = None
    secondary_column: str | None = None
    confidence: float = 0.0
    warnings: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class QueryResult:
    ok: bool
    intent: IntentKind
    n_total: int
    n_match: int
    tables: dict[str, pd.DataFrame]
    metrics: dict[str, Any]
    filters_applied: list[str]
    error: str | None = None


def _tokens(question: str) -> set[str]:
    return set(re.findall(r"[\wáéíóúñü]+", question.lower()))


def _column_score(col: str, hints: list[str]) -> float:
    lc = col.lower().replace("\n", " ")
    score = 0.0
    for h in hints:
        if h in lc:
            score += 1.0 + len(h) / 40.0
    return score


def _best_column(
    df: pd.DataFrame,
    profiles: list[ColumnProfile],
    hints: list[str],
    *,
    structured_only: bool = True,
    subtype_hint: str | None = None,
) -> str | None:
    best: tuple[float, str] | None = None
    prof_map = {p.name: p for p in profiles}
    for c in df.columns:
        if is_timestamp_column(c):
            continue
        p = prof_map.get(c)
        if structured_only and p and p.kind != "estructurada":
            continue
        if subtype_hint and p and subtype_hint not in p.subtype.lower():
            pass  # soft hint
        sc = _column_score(str(c), hints)
        if subtype_hint and p and subtype_hint in p.subtype.lower():
            sc += 0.5
        if sc <= 0:
            continue
        if best is None or sc > best[0]:
            best = (sc, str(c))
    return best[1] if best else None


def _usage_frequency_columns(df: pd.DataFrame, profiles: list[ColumnProfile]) -> list[str]:
    out: list[str] = []
    for c in df.columns:
        if is_timestamp_column(c):
            continue
        lc = str(c).lower()
        if "frecuencia" in lc and "inteligencia artificial" in lc.replace("\n", " "):
            out.append(str(c))
        elif "indicá con qué frecuencia" in lc or "indica con qué frecuencia" in lc:
            out.append(str(c))
    return out


def _extract_unit_filter(question: str, df: pd.DataFrame, col: str) -> FilterSpec | None:
    ql = question.lower()
    codes: list[str] = []
    for code, aliases in UNIT_ALIASES.items():
        if code.lower() in ql:
            codes.append(code)
        for a in aliases:
            if a in ql:
                codes.append(code)
                break
    # genérico facultad + nombre propio
    if not codes and ("facultad" in ql or "unidad" in ql or "escuela" in ql):
        for code, aliases in UNIT_ALIASES.items():
            for a in aliases:
                if len(a) > 6 and a in ql:
                    codes.append(code)
                    break
    if not codes:
        return None
    code = codes[0]
    return FilterSpec(
        column=col,
        op="contains_text",
        value=code,
        label=f"Unidad académica contiene «{code}» (o nombre asociado)",
    )


def _work_filter(question: str, col: str) -> FilterSpec | None:
    ql = question.lower()
    if not any(
        x in ql
        for x in (
            "no trabaj",
            "sin trabaj",
            "no trabaja",
            "sin empleo",
            "no tiene trabajo",
            "no tienen trabajo",
        )
    ):
        if "trabaj" in ql and re.search(r"\bno\b", ql):
            pass  # puede ser "no trabajan"
        else:
            return None
    return FilterSpec(
        column=col,
        op="not_working",
        value=None,
        label="No trabaja (respuesta «No» o equivalente, sin ocupación declarada)",
    )


def _freq_filter(question: str, col: str, *, high: bool) -> FilterSpec | None:
    ql = question.lower()
    if high:
        if not any(
            x in ql
            for x in (
                "frecuent",
                "habitual",
                "seguido",
                "siempre",
                "mucho uso",
                "usan ia",
                "utilizan ia",
                "uso alto",
            )
        ):
            return None
        return FilterSpec(
            column=col,
            op="ordinal_at_least",
            value=4.0,
            label="Uso de IA en nivel alto (frecuencia codificada ≥ 4 o etiqueta «frecuentemente»/«siempre»)",
        )
    return None


def plan_question(
    question: str,
    df: pd.DataFrame,
    profiles: list[ColumnProfile],
) -> QueryPlan:
    q = (question or "").strip()
    if not q:
        return QueryPlan(intent="unsupported", question=q, confidence=0.0, warnings=["Escribí una pregunta."])

    tok = _tokens(q)
    ql = q.lower()
    warnings: list[str] = []
    notes: list[str] = []
    filters: list[FilterSpec] = []

    # --- Intent ---
    intent: IntentKind = "count_filtered"
    if any(
        w in ql
        for w in (
            "qué dicen",
            "que dicen",
            "opinan",
            "opinion",
            "ventaja",
            "riesgo",
            "preocup",
            "recomend",
            "texto",
            "comentario",
            "palabras",
            "temas",
        )
    ):
        intent = "open_text"
    elif any(w in ql for w in ("cruce", "cruzar", "asociación", "asociacion", "relación entre", "chi")):
        intent = "crosstab"
    elif any(w in ql for w in ("distribución", "distribucion", "porcentaje", "moda", "desglose")) and not any(
        w in ql for w in ("cuántos", "cuantos", "cuántas", "cuantas")
    ):
        intent = "describe"
    elif any(w in ql for w in ("cuántos", "cuantos", "cuántas", "cuantas", "cantidad", "número", "numero", "cuenta")):
        intent = "count_filtered"
    elif "cuánt" in ql or "cuant" in ql:
        intent = "count_filtered"

    # --- Columns ---
    col_unit = _best_column(
        df,
        profiles,
        ["unidad academica", "unidad académica", "cursando", "facultad"],
        subtype_hint="categórica",
    )
    col_work = _best_column(df, profiles, ["trabajás", "trabajas", "trabajo"], subtype_hint="binaria")
    if not col_work:
        col_work = _best_column(df, profiles, ["trabaj"])

    freq_cols = _usage_frequency_columns(df, profiles)
    col_freq_global = freq_cols[0] if freq_cols else _best_column(
        df, profiles, ["frecuencia", "inteligencia artificial", "actividades académicas"],
        subtype_hint="frecuencia",
    )

    # --- Filters from question ---
    if col_unit:
        uf = _extract_unit_filter(q, df, col_unit)
        if uf:
            filters.append(uf)
    elif any(w in ql for w in ("facultad", "unidad", "bosco", "educación", "humanidades")):
        warnings.append("No se encontró la columna de unidad académica en el archivo.")

    if col_work:
        wf = _work_filter(q, col_work)
        if wf:
            filters.append(wf)

    want_high_freq = _freq_filter(q, col_freq_global or "", high=True) is not None
    if want_high_freq:
        if col_freq_global:
            ff = _freq_filter(q, col_freq_global, high=True)
            if ff:
                filters.append(ff)
        else:
            warnings.append(
                "No se encontró columna global de frecuencia de IA; se intentará con la rejilla de usos."
            )
            notes.append("Rejilla_usos_alta_frecuencia")

    # open text: pick column
    primary: str | None = None
    secondary: str | None = None
    if intent == "open_text":
        for hints in (
            ["ventaja"],
            ["riesgo", "preocup"],
            ["recomend"],
            ["capacit", "formación", "formacion"],
            ["temas", "gustaría", "gustaria"],
        ):
            primary = _best_column(df, profiles, list(hints), structured_only=False)
            if primary:
                break
        if not primary:
            open_cols = [p.name for p in profiles if p.kind == "abierta" and p.n_non_null > 20]
            primary = open_cols[0] if open_cols else None
        intent = "open_text"
    elif intent == "crosstab":
        primary = col_unit or _best_column(df, profiles, ["unidad"])
        secondary = col_freq_global or col_work
    elif intent == "describe":
        primary = col_freq_global or col_unit
    else:
        primary = col_freq_global

    conf = 0.35
    if filters:
        conf += 0.2 * min(len(filters), 3)
    if intent == "count_filtered" and filters:
        conf += 0.15
    if intent == "open_text" and primary:
        conf += 0.2
    if warnings:
        conf -= 0.1

    if intent == "count_filtered" and not filters:
        warnings.append(
            "No detecté filtros claros (facultad, trabajo, frecuencia). "
            "Probá: «¿Cuántos de Don Bosco…?», «…no trabajan…», «…usan IA frecuentemente…?»"
        )
        conf = 0.25

    return QueryPlan(
        intent=intent,
        question=q,
        filters=filters,
        primary_column=primary,
        secondary_column=secondary,
        confidence=min(0.95, conf),
        warnings=warnings,
        notes=notes,
    )


def _apply_filter(df: pd.DataFrame, spec: FilterSpec) -> pd.Series:
    s = df[spec.column]
    if spec.op == "contains_text":
        code = str(spec.value).upper()
        aliases = UNIT_ALIASES.get(code, [code.lower()])
        raw = s.fillna("").astype(str)
        mask = pd.Series(False, index=df.index)
        for a in [code] + aliases:
            mask |= raw.str.contains(re.escape(a), case=False, na=False)
        return mask
    if spec.op == "not_working":
        norm = s.map(_normalize_cell)
        mask = norm.str.match(r"^no\s*$", na=False)
        mask |= norm.str.contains(r"no\s+trabaj", na=False)
        mask |= norm.str.contains(r"solo\s+estudio", na=False)
        mask &= ~norm.str.contains(r"tiempo\s+completo|tiempo\s+parcial|s[ií],", na=False)
        return mask
    if spec.op == "ordinal_at_least":
        thr = float(spec.value)
        coded, _ = detect_best_ordinal(s, min_cover=0.2)
        num = pd.to_numeric(coded, errors="coerce")
        text_high = s.map(_normalize_cell).isin(FREQ_HIGH_TERMS)
        return (num >= thr) | text_high
    if spec.op == "equals_norm":
        target = _normalize_cell(spec.value)
        return s.map(_normalize_cell) == target
    return pd.Series(True, index=df.index)


def _grid_high_frequency_mask(df: pd.DataFrame, profiles: list[ColumnProfile]) -> pd.Series:
    """Al menos un ítem de la rejilla de usos con frecuencia alta."""
    cols = _usage_frequency_columns(df, profiles)
    # columnas bajo enunciado de usos (no la global si ya está en cols)
    grid = [
        c
        for c in df.columns
        if not is_timestamp_column(c)
        and ("usos posibles" in str(c).lower() or "indicá con qué frecuencia" in str(c).lower())
        and "[" in str(c)
    ]
    if not grid:
        grid = [c for c in cols if "[" in str(c)]
    if not grid:
        return pd.Series(False, index=df.index)

    any_high = pd.Series(False, index=df.index)
    for c in grid:
        coded, _ = detect_best_ordinal(df[c], min_cover=0.15)
        num = pd.to_numeric(coded, errors="coerce")
        text_high = df[c].map(_normalize_cell).isin(FREQ_HIGH_TERMS)
        any_high |= (num >= 4.0) | text_high
    return any_high


def run_plan(
    df: pd.DataFrame,
    plan: QueryPlan,
    profiles: list[ColumnProfile],
) -> QueryResult:
    n_total = len(df)
    tables: dict[str, pd.DataFrame] = {}
    metrics: dict[str, Any] = {}
    applied: list[str] = []

    if plan.intent == "unsupported":
        return QueryResult(
            ok=False,
            intent=plan.intent,
            n_total=n_total,
            n_match=0,
            tables=tables,
            metrics=metrics,
            filters_applied=applied,
            error="Pregunta vacía o no interpretable.",
        )

    if plan.intent == "open_text":
        col = plan.primary_column
        if not col or col not in df.columns:
            return QueryResult(
                ok=False,
                intent=plan.intent,
                n_total=n_total,
                n_match=0,
                tables=tables,
                metrics=metrics,
                filters_applied=applied,
                error="No se encontró una columna de texto abierto para analizar.",
            )
        texts = df[col].dropna().astype(str).str.strip()
        texts = texts[texts.astype(bool)]
        tables["muestra_respuestas"] = pd.DataFrame({"respuesta": texts.head(12)})
        metrics["n_respuestas"] = int(len(texts))
        metrics["columna"] = col
        return QueryResult(
            ok=True,
            intent=plan.intent,
            n_total=n_total,
            n_match=int(len(texts)),
            tables=tables,
            metrics=metrics,
            filters_applied=[f"Texto abierto: {col[:80]}…"],
        )

    mask = pd.Series(True, index=df.index)
    for f in plan.filters:
        mask &= _apply_filter(df, f)
        applied.append(f.label)

    if plan.notes and "Rejilla_usos_alta_frecuencia" in plan.notes and not any(
        f.op == "ordinal_at_least" for f in plan.filters
    ):
        grid_m = _grid_high_frequency_mask(df, profiles)
        mask &= grid_m
        applied.append("Al menos un uso académico con frecuencia alta en la rejilla de ítems")

    if plan.intent == "count_filtered":
        n_match = int(mask.sum())
        metrics["n"] = n_match
        metrics["pct"] = round(100.0 * n_match / n_total, 2) if n_total else 0.0
        metrics["n_resto"] = n_total - n_match
        # desglose por unidad si hay filtro de trabajo/frecuencia sin unidad
        if plan.filters and plan.filters[0].column:
            uc = _best_column(df, profiles, ["unidad academica", "unidad académica"])
            if uc and not any(f.column == uc for f in plan.filters):
                sub = df.loc[mask, uc].astype(str).value_counts().head(8)
                tables["desglose_unidad"] = sub.reset_index()
                tables["desglose_unidad"].columns = ["unidad", "n"]
        return QueryResult(
            ok=True,
            intent=plan.intent,
            n_total=n_total,
            n_match=n_match,
            tables=tables,
            metrics=metrics,
            filters_applied=applied,
        )

    if plan.intent == "describe" and plan.primary_column:
        col = plan.primary_column
        desc = descriptive_one_column(df[col])
        tables["frecuencias"] = pd.DataFrame(
            {"categoría": desc["valor_counts"].index, "n": desc["valor_counts"].values}
        )
        metrics["desc"] = desc
        return QueryResult(
            ok=True,
            intent=plan.intent,
            n_total=n_total,
            n_match=int(df[col].notna().sum()),
            tables=tables,
            metrics=metrics,
            filters_applied=applied or [f"Columna: {col[:70]}"],
        )

    if plan.intent == "crosstab" and plan.primary_column and plan.secondary_column:
        r, c = plan.primary_column, plan.secondary_column
        res = crosstab_chi_square(df, r, c)
        tables["cruce"] = res["tabla"]
        metrics["chi2"] = res
        return QueryResult(
            ok=True,
            intent=plan.intent,
            n_total=n_total,
            n_match=int(res["n"]),
            tables=tables,
            metrics=metrics,
            filters_applied=[f"Cruce: {r[:50]} × {c[:50]}"],
        )

    return QueryResult(
        ok=False,
        intent=plan.intent,
        n_total=n_total,
        n_match=0,
        tables=tables,
        metrics=metrics,
        filters_applied=applied,
        error="No se pudo ejecutar el análisis con la interpretación actual de la pregunta.",
    )


def interpret_result(
    plan: QueryPlan,
    result: QueryResult,
    df: pd.DataFrame,
    *,
    col_labels: dict[str, str] | None = None,
) -> str:
    col_labels = col_labels or {}
    parts: list[str] = []

    if not result.ok:
        return (
            f"No se pudo responder con las reglas actuales.\n\n"
            f"**Detalle:** {result.error or '—'}\n\n"
            f"**Sugerencia:** reformulá la pregunta mencionando facultad/unidad, trabajo (sí/no), "
            f"frecuencia de uso de IA, o pedí distribución de una variable concreta."
        )

    q_short = plan.question[:120] + ("…" if len(plan.question) > 120 else "")

    if result.intent == "count_filtered":
        n, pct = result.metrics.get("n", 0), result.metrics.get("pct", 0)
        parts.append(
            f"### Respuesta cuantitativa\n\n"
            f"Sobre **{result.n_total}** respuestas en el archivo, **{n}** personas "
            f"({pct:.1f} %) cumplen **todas** las condiciones detectadas en tu pregunta:\n\n"
        )
        for line in result.filters_applied:
            parts.append(f"- {line}\n")
        parts.append(
            f"\nEl resto (**{result.n_total - n}**) no cumple al menos un criterio o tiene dato faltante en alguna columna usada.\n"
        )
        if "desglose_unidad" in result.tables and not result.tables["desglose_unidad"].empty:
            parts.append("\n**Desglose por unidad** (entre quienes cumplen el filtro):\n\n")
            for _, row in result.tables["desglose_unidad"].iterrows():
                u = str(row["unidad"])[:70]
                parts.append(f"- {u}: **{int(row['n'])}**\n")

        parts.append("\n### Lectura cualitativa (muestral)\n\n")
        if n == 0:
            parts.append(
                "En esta muestra **nadie** cumple simultáneamente todos los criterios. "
                "Revisá si la facultad está escrita distinto en el Excel, si «no trabajan» debe incluir "
                "«solo estudio», o si «frecuentemente» debe aplicarse a otra columna (uso global vs rejilla de usos).\n"
            )
        elif pct < 5:
            parts.append(
                f"Es un **grupo pequeño** ({n} personas): útil para ilustrar un perfil, "
                "pero evitá generalizar a toda la facultad sin intervalos de confianza.\n"
            )
        elif pct > 40:
            parts.append(
                f"Es un **segmento amplio** ({pct:.0f} % de la muestra total): el patrón es frecuente "
                "entre quienes respondieron la encuesta bajo estos criterios.\n"
            )
        else:
            parts.append(
                f"El perfil es **moderadamente frecuente** en la muestra ({pct:.0f} %). "
                "Conviene contrastar con otros filtros (otra facultad, quienes sí trabajan) en una segunda pregunta.\n"
            )
        parts.append(
            "\n*Datos transversales y autoinformados: conteo descriptivo, no prueba causal.*\n"
        )
        return "".join(parts)

    if result.intent == "open_text":
        col = result.metrics.get("columna", "")
        label = col_labels.get(col, col)
        n = result.metrics.get("n_respuestas", 0)
        parts.append(
            f"### Respuesta cuantitativa\n\n"
            f"Hay **{n}** respuestas no vacías en «{label[:90]}».\n\n"
            f"### Lectura cualitativa (muestral)\n\n"
            f"A continuación conviene revisar la **muestra de citas** y, si querés profundidad, "
            f"usar la pestaña **Análisis cualitativo** (temas NMF o sentimiento) sobre esa misma columna.\n"
        )
        if "muestra_respuestas" in result.tables:
            parts.append("\n**Ejemplos literales (hasta 12):**\n\n")
            for t in result.tables["muestra_respuestas"]["respuesta"].head(8):
                snippet = str(t).replace("\n", " ")[:200]
                parts.append(f"- «{snippet}»\n")
        return "".join(parts)

    if result.intent == "describe" and "desc" in result.metrics:
        col = plan.primary_column or ""
        label = col_labels.get(col, col)
        parts.append(f"### Distribución — {label[:90]}\n\n")
        parts.append(descriptive_explanatory(result.metrics["desc"]))
        return "".join(parts)

    if result.intent == "crosstab" and "chi2" in result.metrics:
        res = result.metrics["chi2"]
        rlab = col_labels.get(plan.primary_column or "", plan.primary_column or "")
        clab = col_labels.get(plan.secondary_column or "", plan.secondary_column or "")
        parts.append(
            chi_square_explanatory(
                chi2=res["chi2"],
                gl=res["gl"],
                p_valor=res["p_valor"],
                cramers_v=res["cramers_v"],
                n=res["n"],
                row_lab=rlab,
                col_lab=clab,
                tabla=res.get("tabla"),
            )
        )
        return "".join(parts)

    return "Análisis ejecutado; revisá las tablas mostradas arriba."


def example_questions() -> list[str]:
    return [
        "¿Cuántos alumnos de la Facultad Don Bosco utilizan IA frecuentemente y no trabajan?",
        "¿Cuántos responden de Educación San Juan (FEDSJ)?",
        "Distribución de la frecuencia de uso de IA para actividades académicas",
        "¿Qué ventajas encuentran los estudiantes en el uso de la IA?",
        "Cruce entre unidad académica y si trabaja actualmente",
    ]
