"""
Limpieza y control de calidad para planillas Excel de encuestas (Google Forms).
Coherencia entre ítems, valores aberrantes, respuestas basura y reportes exportables.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
import pandas as pd

from quant_advanced import (
    FREQ_SCORE,
    LIKERT_SCORE,
    detect_best_ordinal,
    normalize_text,
    series_spanish_ai_tool_exposure_ordinal,
)
from survey_intel import LIKERT_TERMS, FREQ_TERMS, classify_columns, is_timestamp_column

GarbageKind = Literal[
    "insulto",
    "caracteres_aleatorios",
    "texto_sin_sentido",
    "respuesta_absurda",
    "copy_paste_repetido",
    "copy_paste_en_fila",
    "automatizada",
]

Intensity = Literal["bajo", "medio", "alto", "desconocido"]


@dataclass(frozen=True)
class CoherenceRuleTemplate:
    rule_id: str
    name: str
    description: str
    keywords_a: tuple[str, ...]
    keywords_b: tuple[str, ...]
    example: str


BUILTIN_COHERENCE_RULES: tuple[CoherenceRuleTemplate, ...] = (
    CoherenceRuleTemplate(
        rule_id="ia_nunca_vs_uso_frecuente",
        name="IA: «nunca» vs uso frecuente",
        description=(
            "Uso general de IA en nivel bajo (nunca / no uso) pero otra columna indica uso "
            "frecuente de herramientas (ChatGPT, etc.)."
        ),
        keywords_a=(
            "inteligencia artificial",
            "uso de ia",
            "herramientas de ia",
            "uso ia",
            "ia generativa",
            " de ia",
            "sobre ia",
        ),
        keywords_b=(
            "chatgpt",
            "gemini",
            "copilot",
            "bard",
            "claude",
            "frecuencia",
            "con qué frecuencia",
            "uso diario",
            "herramienta",
        ),
        example="«Nunca usó IA» + «Usa ChatGPT diariamente».",
    ),
    CoherenceRuleTemplate(
        rule_id="acceso_pc_bajo_vs_ia_datos_alto",
        name="Acceso a PC bajo vs análisis de datos con IA",
        description=(
            "Acceso o uso de computadora declarado como bajo, pero otra respuesta indica "
            "análisis de bases de datos o trabajo intensivo con IA."
        ),
        keywords_a=(
            "computadora",
            "ordenador",
            "pc ",
            "equipo inform",
            "acceso a",
            "dispositivo",
        ),
        keywords_b=(
            "base de datos",
            "bases de datos",
            "analiz",
            "datos con ia",
            "big data",
            "machine learning",
            "modelo predict",
        ),
        example="«No tiene acceso frecuente a computadora» + «Analiza bases de datos con IA».",
    ),
    CoherenceRuleTemplate(
        rule_id="no_conoce_ia_vs_uso_habitual",
        name="No conoce IA vs uso habitual",
        description="Declaración de no conocer o no usar IA frente a uso habitual o diario en otro ítem.",
        keywords_a=(
            "conoc",
            "experiencia con ia",
            "inteligencia artificial",
            "herramientas de ia",
        ),
        keywords_b=(
            "frecuencia",
            "uso",
            "chatgpt",
            "ia ",
            "herramienta",
        ),
        example="«No conozco herramientas de IA» + «Las uso a diario».",
    ),
)

_LOW_PHRASES = (
    "nunca",
    "no uso",
    "no utilizo",
    "no utilicé",
    "no he usado",
    "no he utilizado",
    "no tengo acceso",
    "sin acceso",
    "no conozco",
    "no conocía",
    "jamás",
    "nada",
    "ninguna",
    "ningún",
    "no, nunca",
    "muy poco",
    "casi nunca",
    "rara vez",
    "poco frecuente",
    "no tengo",
    "no dispongo",
)

_HIGH_PHRASES = (
    "diariamente",
    "a diario",
    "todos los días",
    "cada día",
    "siempre",
    "frecuentemente",
    "muy frecuente",
    "habitualmente",
    "uso habitual",
    "a menudo",
    "muchas veces",
    "casi siempre",
    "constantemente",
    "todo el tiempo",
)


def _norm_col(name: str) -> str:
    return normalize_text(str(name).replace("\n", " "))


def columns_matching_keywords(
    columns: list[str],
    keywords: tuple[str, ...],
    *,
    match_any: bool = True,
) -> list[str]:
    """Columnas cuyo enunciado contiene alguna (o todas) las palabras clave."""
    out: list[str] = []
    for col in columns:
        if is_timestamp_column(col):
            continue
        nc = _norm_col(col)
        hits = [kw in nc for kw in keywords]
        if match_any and any(hits):
            out.append(col)
        elif not match_any and hits and all(hits):
            out.append(col)
    return out


def _ordinal_level_from_maps(text: str) -> float | None:
    """Escala 0 (bajo) … 1 (alto) a partir de etiquetas Likert/frecuencia cerradas."""
    if not text:
        return None
    for mapping in (FREQ_SCORE, LIKERT_SCORE):
        if text in mapping:
            v = float(mapping[text])
            span = max(mapping.values()) - min(mapping.values())
            if span <= 0:
                return None
            return (v - min(mapping.values())) / span
    return None


def response_intensity(value: Any, *, series_hint: pd.Series | None = None) -> tuple[Intensity, float | None]:
    """
    Clasifica intensidad de una respuesta (uso, frecuencia, acuerdo).
    series_hint: columna completa para codificación ordinal automática si la celda es ambigua.
    """
    if pd.isna(value):
        return "desconocido", None
    raw = str(value).strip()
    if not raw:
        return "desconocido", None

    parts = [normalize_text(p) for p in re.split(r"[,;]", raw) if normalize_text(p)]
    if not parts:
        parts = [normalize_text(raw)]

    scores: list[float] = []
    for text in parts:
        mapped = _ordinal_level_from_maps(text)
        if mapped is not None:
            scores.append(mapped)
            continue
        if any(p in text for p in _LOW_PHRASES):
            scores.append(0.0)
        elif any(p in text for p in _HIGH_PHRASES):
            scores.append(1.0)
        elif re.search(r"\bno\b", text) and not re.search(r"\bno,?\s*s[ií]\b", text):
            if any(w in text for w in ("acceso", "uso", "conozco", "conoc", "tengo", "utilizo")):
                scores.append(0.15)

    if not scores and series_hint is not None and len(series_hint) >= 5:
        idx = series_hint.index[series_hint.astype(str) == raw]
        if len(idx):
            coded, _ = detect_best_ordinal(series_hint, min_cover=0.35)
            if idx[0] in coded.index and pd.notna(coded.loc[idx[0]]):
                v = float(coded.loc[idx[0]])
                lo, hi = float(coded.min()), float(coded.max())
                if hi > lo:
                    scores.append((v - lo) / (hi - lo))

    if not scores:
        if series_hint is not None and len(series_hint) >= 5:
            ai_ord, _ = series_spanish_ai_tool_exposure_ordinal(series_hint.astype(str))
            idx = series_hint.index[series_hint.astype(str) == raw]
            if len(idx) and pd.notna(ai_ord.loc[idx[0]]):
                v = float(ai_ord.loc[idx[0]])
                scores.append((v - 1.0) / 4.0)

    if not scores:
        return "desconocido", None

    avg = float(np.mean(scores))
    if avg <= 0.28:
        return "bajo", avg
    if avg >= 0.72:
        return "alto", avg
    return "medio", avg


def _is_low(intensity: Intensity, score: float | None) -> bool:
    return intensity == "bajo" or (score is not None and score <= 0.30)


def _is_high(intensity: Intensity, score: float | None) -> bool:
    return intensity == "alto" or (score is not None and score >= 0.70)


def scan_coherence(
    df: pd.DataFrame,
    rules: tuple[CoherenceRuleTemplate, ...] | None = None,
    *,
    row_id_column: str | None = None,
) -> pd.DataFrame:
    """Filas con posibles incoherencias entre pares de columnas según reglas heurísticas."""
    rules = rules or BUILTIN_COHERENCE_RULES
    cols = [c for c in df.columns if not is_timestamp_column(c)]
    records: list[dict[str, Any]] = []

    for rule in rules:
        cols_a = columns_matching_keywords(cols, rule.keywords_a)
        cols_b = columns_matching_keywords(cols, rule.keywords_b)
        if not cols_a or not cols_b:
            continue

        for ca in cols_a:
            for cb in cols_b:
                if ca == cb:
                    continue
                sa = df[ca]
                sb = df[cb]
                for idx in df.index:
                    va, vb = sa.loc[idx], sb.loc[idx]
                    if pd.isna(va) or pd.isna(vb):
                        continue
                    ia, sc_a = response_intensity(va, series_hint=sa)
                    ib, sc_b = response_intensity(vb, series_hint=sb)
                    if not (_is_low(ia, sc_a) and _is_high(ib, sc_b)):
                        continue
                    row_num = int(idx) + 1 if isinstance(idx, (int, np.integer)) else idx
                    rec: dict[str, Any] = {
                        "fila_excel": row_num,
                        "regla": rule.name,
                        "regla_id": rule.rule_id,
                        "columna_a": ca,
                        "respuesta_a": str(va)[:200],
                        "columna_b": cb,
                        "respuesta_b": str(vb)[:200],
                        "detalle": rule.example,
                    }
                    if row_id_column and row_id_column in df.columns:
                        rec["identificador"] = df.loc[idx, row_id_column]
                    records.append(rec)

    if not records:
        return pd.DataFrame(
            columns=[
                "fila_excel",
                "regla",
                "regla_id",
                "columna_a",
                "respuesta_a",
                "columna_b",
                "respuesta_b",
                "detalle",
            ]
        )
    out = pd.DataFrame(records)
    return out.drop_duplicates(
        subset=["fila_excel", "regla_id", "columna_a", "columna_b", "respuesta_a", "respuesta_b"]
    )


def guess_age_columns(columns: list[str]) -> list[str]:
    keys = ("edad", "age", "años", "anos", "año")
    out: list[str] = []
    for c in columns:
        if is_timestamp_column(c):
            continue
        nc = _norm_col(c)
        if any(k in nc for k in keys):
            out.append(c)
    return out


def parse_numeric_age(value: Any) -> float | None:
    if pd.isna(value):
        return None
    if isinstance(value, (int, float, np.integer, np.floating)):
        v = float(value)
        return v if np.isfinite(v) else None
    t = normalize_text(str(value))
    if not t:
        return None
    m = re.search(r"(\d{1,3})\s*(?:años|anos)?", t)
    if m:
        return float(m.group(1))
    return None


def scan_numeric_outliers(
    df: pd.DataFrame,
    column: str,
    *,
    min_value: float,
    max_value: float,
) -> pd.DataFrame:
    """Filas con edad u otro número fuera de rango plausible."""
    if column not in df.columns:
        return pd.DataFrame()
    ages = df[column].map(parse_numeric_age)
    mask = ages.notna() & ((ages < min_value) | (ages > max_value))
    if not mask.any():
        return pd.DataFrame()

    rows = []
    for idx in df.index[mask]:
        v = ages.loc[idx]
        row_num = int(idx) + 1 if isinstance(idx, (int, np.integer)) else idx
        rows.append(
            {
                "fila_excel": row_num,
                "columna": column,
                "valor_original": str(df.loc[idx, column])[:120],
                "valor_numérico": float(v),
                "problema": (
                    f"Por debajo de {min_value:g}"
                    if v < min_value
                    else f"Por encima de {max_value:g}"
                ),
            }
        )
    return pd.DataFrame(rows)


def quality_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """Resumen por columna: faltantes, únicos, posibles problemas."""
    rows: list[dict[str, Any]] = []
    n = len(df)
    for col in df.columns:
        if is_timestamp_column(col):
            continue
        s = df[col]
        nn = int(s.notna().sum())
        miss_pct = round(100.0 * (1 - nn / max(n, 1)), 1)
        n_unique = int(s.dropna().astype(str).nunique())
        rows.append(
            {
                "columna": col,
                "respuestas_válidas": nn,
                "%_faltante": miss_pct,
                "valores_únicos": n_unique,
            }
        )
    return pd.DataFrame(rows).sort_values("%_faltante", ascending=False)


def dataset_quality_overview(df: pd.DataFrame) -> dict[str, Any]:
    n = len(df)
    dup = int(df.duplicated().sum()) if n else 0
    all_missing_cols = [
        c
        for c in df.columns
        if not is_timestamp_column(c) and df[c].notna().sum() == 0
    ]
    return {
        "filas": n,
        "columnas": len(df.columns),
        "filas_duplicadas_exactas": dup,
        "columnas_totalmente_vacías": len(all_missing_cols),
    }


# --- Respuestas basura / automatizadas ---

_KEYBOARD_WALKS = (
    "qwerty",
    "qwertyuiop",
    "asdf",
    "asdfgh",
    "zxcv",
    "wasd",
    "qwer",
    "1234",
    "abcd",
    "abcdef",
)

_ABSURD_EXACT = frozenset(
    {
        "x",
        "xx",
        "xxx",
        "xxxx",
        "na",
        "n/a",
        "n.a",
        "no",
        "si",
        "sí",
        ".",
        "..",
        "...",
        "-",
        "--",
        "—",
        "nose",
        "no se",
        "no sé",
        "zzz",
        "asd",
        "asdf",
        "asdasd",
        "q",
        "a",
        "b",
        "1",
        "11",
        "111",
        "123",
        "1234",
        "test",
        "testing",
        "prueba",
        "dummy",
        "ninguno",
        "ninguna",
        "nada",
        "null",
        "none",
        "nop",
        "no aplica",
        "sin comentarios",
        "sin comentario",
        "no comment",
        "paso",
        "no quiero",
        "no sé qué poner",
        "no se que poner",
        "no tengo nada",
        "no tengo opinion",
        "no tengo opinión",
        "bla",
        "ble",
        "blah",
    }
)

_INSULT_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bput[ao]s?\b",
        r"\bmierda\b",
        r"\bbolud[ao]s?\b",
        r"\bpelotud[ao]s?\b",
        r"\bforr[ao]s?\b",
        r"\bgiles?\b",
        r"\bhuevon(es|a|as)?\b",
        r"\bhdp\b",
        r"\bhijo\s+de\s+puta\b",
        r"\bconcha\s+(de\s+)?(tu|su)\b",
        r"\b(la\s+)?concha\b",
        r"\bcarajo\b",
        r"\bverga\b",
        r"\bpendej[ao]s?\b",
        r"\bimbecil(es)?\b",
        r"\bestupid[ao]s?\b",
        r"\bmalparid[ao]s?\b",
        r"\bchinga(r|da|do)?\b",
        r"\bputo\b",
    )
)

_AUTOMATED_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"lorem\s+ipsum",
        r"dolor\s+sit\s+amet",
        r"inserte\s+texto",
        r"escriba\s+aqu[ií]",
        r"your\s+answer\s+here",
        r"respuesta\s+de\s+prueba",
    )
)


def _excel_row_num(idx: Any) -> Any:
    return int(idx) + 1 if isinstance(idx, (int, np.integer)) else idx


def _normalize_garbage_key(text: str) -> str:
    return re.sub(r"\s+", " ", normalize_text(text)).strip()


def infer_text_columns_for_junk(df: pd.DataFrame) -> list[str]:
    """Columnas donde tiene sentido buscar basura (abiertas o texto largo heterogéneo)."""
    profiles = classify_columns(df)
    names: list[str] = []
    seen: set[str] = set()
    for p in profiles:
        if p.n_non_null <= 0:
            continue
        use = p.kind == "abierta" or (p.max_len >= 80 and p.avg_len >= 22 and p.n_unique >= 8)
        if use and p.name not in seen:
            names.append(p.name)
            seen.add(p.name)
    return names


def _is_likely_closed_answer(text: str) -> bool:
    t = normalize_text(text)
    if not t:
        return True
    if t in LIKERT_TERMS or t in FREQ_TERMS:
        return True
    if t in _ABSURD_EXACT:
        return False
    if len(t) <= 48 and t.count(" ") <= 6:
        if t in FREQ_SCORE or t in LIKERT_SCORE:
            return True
    return False


def _detect_insult(text: str) -> str | None:
    for pat in _INSULT_PATTERNS:
        m = pat.search(text)
        if m:
            return f"Posible insulto o lenguaje ofensivo («{m.group(0)}»)"
    return None


def _detect_automated_template(text: str) -> str | None:
    t = normalize_text(text)
    for pat in _AUTOMATED_PATTERNS:
        if pat.search(t):
            return "Texto tipo plantilla automática o relleno (lorem ipsum, «inserte texto», etc.)"
    if re.match(r"^https?://\S+$", t) and len(t) < 120:
        return "Solo URL sin desarrollo (posible relleno)"
    return None


def _detect_random_chars(text: str) -> str | None:
    raw = str(text).strip()
    if len(raw) < 5:
        return None
    t = normalize_text(raw)
    if any(w in t for w in _KEYBOARD_WALKS):
        return "Secuencia tipo teclado (qwerty, asdf, etc.)"
    if re.search(r"(.)\1{4,}", raw, flags=re.IGNORECASE):
        return "Carácter repetido muchas veces (aaaa, 1111, etc.)"
    letters = [c for c in t if c.isalpha()]
    if len(raw) >= 6:
        alnum_ratio = sum(ch.isalnum() for ch in raw) / len(raw)
        if alnum_ratio < 0.45:
            return "Muchos símbolos o caracteres especiales"
    if len(letters) >= 6:
        vowels = sum(1 for c in letters if c in "aeiouáéíóú")
        if vowels / len(letters) < 0.12:
            return "Casi sin vocales (posible tecleo aleatorio)"
    if len(raw) >= 8 and sum(ch.isdigit() for ch in raw) / len(raw) > 0.65:
        return "Predominan números sin contenido textual"
    if re.fullmatch(r"[a-z0-9]{6,}", t) and not re.search(r"[aeiouáéíóú]{2}", t):
        return "Cadena alfanumérica sin patrón de palabra"
    return None


def _detect_nonsense(text: str) -> str | None:
    t = normalize_text(text)
    if len(t) < 18:
        return None
    tokens = re.findall(r"[a-záéíóúñü]{3,}", t)
    if not tokens:
        return "Sin palabras reconocibles"
    vowel_ok = 0
    for tok in tokens:
        if sum(c in "aeiouáéíóú" for c in tok) / len(tok) >= 0.28:
            vowel_ok += 1
    if len(tokens) >= 3 and vowel_ok / len(tokens) < 0.22:
        return "Palabras con estructura poco natural en español"
    long_weird = [tok for tok in tokens if len(tok) >= 7 and not re.search(r"[aeiouáéíóú]", tok)]
    if long_weird:
        return f"Palabra larga sin vocales («{long_weird[0][:20]}»)"
    if len(set(tokens)) <= 2 and len(t) > 40:
        return "Muy pocas palabras distintas en texto largo"
    return None


def _detect_absurd_short(text: str) -> str | None:
    t = _normalize_garbage_key(text)
    if not t:
        return None
    if t in _ABSURD_EXACT:
        return "Respuesta vacía o evasiva típica (test, xxx, n/a, etc.)"
    if re.fullmatch(r"[x\.\-_,;:!?0-9]{2,12}", t):
        return "Solo signos o letras sin contenido (x, ---, ...)"
    if re.fullmatch(r"(no\s*(se|sé|lo\s*se)|nose|na|n/?a)", t):
        return "Evasiva sin aporte («no sé», n/a)"
    if len(t) <= 4 and t.isalpha() and t not in {"si", "sí", "no"}:
        return "Texto demasiado corto para un ítem abierto"
    return None


def classify_cell_garbage(
    value: Any,
    *,
    min_open_len: int = 10,
) -> list[tuple[GarbageKind, str]]:
    """Devuelve lista de (tipo, detalle) para una celda de texto."""
    if pd.isna(value):
        return []
    raw = str(value).strip()
    if not raw or _is_likely_closed_answer(raw):
        return []

    t = _normalize_garbage_key(raw)
    if len(t) < 3:
        return []

    hits: list[tuple[GarbageKind, str]] = []

    insult = _detect_insult(raw)
    if insult:
        hits.append(("insulto", insult))

    auto = _detect_automated_template(raw)
    if auto:
        hits.append(("automatizada", auto))

    absurd = _detect_absurd_short(raw)
    if absurd and len(t) < min_open_len:
        hits.append(("respuesta_absurda", absurd))
    elif absurd and len(t) < 25:
        hits.append(("respuesta_absurda", absurd))

    rnd = _detect_random_chars(raw)
    if rnd:
        hits.append(("caracteres_aleatorios", rnd))

    if len(t) >= min_open_len:
        nonsense = _detect_nonsense(raw)
        if nonsense:
            hits.append(("texto_sin_sentido", nonsense))
        elif len(t) >= 14 and absurd:
            hits.append(("respuesta_absurda", absurd))

    return hits


def find_repeated_long_texts(
    df: pd.DataFrame,
    text_columns: list[str],
    *,
    min_len: int = 40,
    min_occurrences: int = 3,
) -> dict[str, int]:
    """Textos largos idénticos (normalizados) que se repiten en la muestra."""
    counter: Counter[str] = Counter()
    for col in text_columns:
        if col not in df.columns:
            continue
        for v in df[col].dropna().astype(str):
            key = _normalize_garbage_key(v)
            if len(key) >= min_len:
                counter[key] += 1
    return {k: n for k, n in counter.items() if n >= min_occurrences}


def scan_garbage_responses(
    df: pd.DataFrame,
    text_columns: list[str] | None = None,
    *,
    min_open_len: int = 10,
    copy_paste_min_len: int = 40,
    copy_paste_min_occurrences: int = 3,
    row_id_column: str | None = None,
    check_insults: bool = True,
    check_random: bool = True,
    check_nonsense: bool = True,
    check_absurd: bool = True,
    check_copy_paste: bool = True,
) -> pd.DataFrame:
    """
    Escanea ítems de texto libre en busca de basura, insultos, copy-paste y respuestas absurdas.
    """
    text_columns = text_columns or infer_text_columns_for_junk(df)
    if not text_columns:
        return pd.DataFrame(
            columns=[
                "fila_excel",
                "columna",
                "tipo_alerta",
                "respuesta",
                "detalle",
            ]
        )

    repeated: dict[str, int] = {}
    if check_copy_paste:
        repeated = find_repeated_long_texts(
            df,
            text_columns,
            min_len=copy_paste_min_len,
            min_occurrences=copy_paste_min_occurrences,
        )

    records: list[dict[str, Any]] = []
    kind_enabled = {
        "insulto": check_insults,
        "caracteres_aleatorios": check_random,
        "texto_sin_sentido": check_nonsense,
        "respuesta_absurda": check_absurd,
        "automatizada": True,
        "copy_paste_repetido": check_copy_paste,
        "copy_paste_en_fila": check_copy_paste,
    }

    for idx in df.index:
        row_texts: list[str] = []
        for col in text_columns:
            val = df.loc[idx, col]
            if pd.isna(val):
                continue
            raw = str(val).strip()
            if not raw:
                continue

            key = _normalize_garbage_key(raw)
            if check_copy_paste and key in repeated:
                records.append(
                    {
                        "fila_excel": _excel_row_num(idx),
                        "columna": col,
                        "tipo_alerta": "copy_paste_repetido",
                        "respuesta": raw[:200],
                        "detalle": (
                            f"Mismo texto largo repetido {repeated[key]} veces en la encuesta "
                            f"(≥{copy_paste_min_len} caracteres)."
                        ),
                    }
                )

            flags = classify_cell_garbage(val, min_open_len=min_open_len)
            for kind, detail in flags:
                if not kind_enabled.get(kind, True):
                    continue
                records.append(
                    {
                        "fila_excel": _excel_row_num(idx),
                        "columna": col,
                        "tipo_alerta": kind,
                        "respuesta": raw[:200],
                        "detalle": detail,
                    }
                )

            if check_copy_paste and len(key) >= copy_paste_min_len:
                row_texts.append(key)

        if check_copy_paste and len(row_texts) >= 2:
            uniq = set(row_texts)
            if len(uniq) == 1:
                records.append(
                    {
                        "fila_excel": _excel_row_num(idx),
                        "columna": "(varias)",
                        "tipo_alerta": "copy_paste_en_fila",
                        "respuesta": row_texts[0][:200],
                        "detalle": (
                            "El mismo texto largo aparece copiado en varios ítems abiertos de esta fila."
                        ),
                    }
                )

    if not records:
        return pd.DataFrame(
            columns=["fila_excel", "columna", "tipo_alerta", "respuesta", "detalle"]
        )

    out = pd.DataFrame(records)
    if row_id_column and row_id_column in df.columns:
        id_map = {_excel_row_num(i): df.loc[i, row_id_column] for i in df.index}
        out["identificador"] = out["fila_excel"].map(id_map)

    return out.drop_duplicates(
        subset=["fila_excel", "columna", "tipo_alerta", "respuesta", "detalle"]
    )


GARBAGE_KIND_LABELS: dict[str, str] = {
    "insulto": "Insulto / lenguaje ofensivo",
    "caracteres_aleatorios": "Caracteres aleatorios",
    "texto_sin_sentido": "Texto sin sentido",
    "respuesta_absurda": "Respuesta absurda o evasiva",
    "copy_paste_repetido": "Copy-paste repetido en la muestra",
    "copy_paste_en_fila": "Copy-paste entre ítems de la misma fila",
    "automatizada": "Plantilla automática / relleno",
}


def garbage_summary_by_type(garbage: pd.DataFrame) -> pd.DataFrame:
    if garbage.empty:
        return pd.DataFrame(columns=["tipo_alerta", "etiqueta", "casos"])
    g = garbage.copy()
    g["etiqueta"] = g["tipo_alerta"].map(lambda k: GARBAGE_KIND_LABELS.get(k, k))
    return (
        g.groupby(["tipo_alerta", "etiqueta"], as_index=False)
        .size()
        .rename(columns={"size": "casos"})
        .sort_values("casos", ascending=False)
    )


def build_flagged_rows_export(
    df: pd.DataFrame,
    coherence: pd.DataFrame,
    outliers: pd.DataFrame,
    garbage: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Marca filas con al menos una alerta de limpieza."""
    flags: dict[int, list[str]] = {}

    def _add(idx_raw: Any, msg: str) -> None:
        try:
            idx = int(idx_raw) - 1
        except (TypeError, ValueError):
            return
        flags.setdefault(idx, []).append(msg)

    for _, r in coherence.iterrows():
        _add(r["fila_excel"], f"Coherencia: {r['regla']}")
    for _, r in outliers.iterrows():
        _add(r["fila_excel"], f"Aberrante: {r['columna']} ({r['problema']})")
    if garbage is not None and not garbage.empty:
        for _, r in garbage.iterrows():
            lbl = GARBAGE_KIND_LABELS.get(str(r["tipo_alerta"]), r["tipo_alerta"])
            _add(r["fila_excel"], f"Basura: {lbl}")

    if not flags:
        return pd.DataFrame()

    out = df.copy()
    out.insert(0, "_alertas_limpieza", "")
    for idx, msgs in flags.items():
        if 0 <= idx < len(out):
            out.iloc[idx, out.columns.get_loc("_alertas_limpieza")] = " | ".join(msgs)
    return out[out["_alertas_limpieza"].astype(str).str.len() > 0]
