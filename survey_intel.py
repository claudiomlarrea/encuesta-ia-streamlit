"""
Heurísticas y análisis para encuestas exportadas (p. ej. Google Forms → Excel).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
import pandas as pd
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


# --- Clasificación estructurada vs abierta ---

TIMESTAMP_HINTS = ("marca temporal", "timestamp", "fecha de respuesta")

# Preguntas abiertas típicas (prioridad sobre heurísticas de cardinalidad)
OPEN_QUESTION_HINTS = (
    "qué ventajas",
    "que ventajas",
    "qué riesgos",
    "que riesgos",
    "preocupaciones te genera",
    "qué recomendaciones",
    "que recomendaciones",
    "buena práctica",
    "buena practica",
    "experiencia concreta",
    "si querés, mencioná",
    "si queres, menciona",
    "comentarios adicionales",
    "opinión libre",
)

LIKERT_TERMS = frozenset(
    {
        "totalmente de acuerdo",
        "de acuerdo",
        "ni de acuerdo ni en desacuerdo",
        "en desacuerdo",
        "totalmente en desacuerdo",
        "completamente de acuerdo",
    }
)

FREQ_TERMS = frozenset(
    {
        "nunca",
        "rara vez",
        "a veces",
        "frecuentemente",
        "siempre",
        # Escala temporal docente (0–4)
        "menos de una vez por mes",
        "entre 1 y 3 veces por mes",
        "entre 1 y 3 veces por semana",
        "cuatro o más veces por semana",
    }
)

BINARY_SI_NO = frozenset(
    {
        "si",
        "sí",
        "no",
        "sí.",  # ruido menor
        "no.",
    }
)


def _normalize_cell(x: Any) -> str:
    if pd.isna(x):
        return ""
    s = str(x).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def _short_label(col: str) -> str:
    s = col.replace("\n", " ").strip()
    if len(s) > 90:
        return s[:87] + "…"
    return s


def _longest_common_prefix(strings: list[str]) -> str:
    """Prefijo compartido por todas las cadenas (para quitar encabezados idénticos en matrices)."""
    if len(strings) < 2:
        return ""
    a = min(strings)
    b = max(strings)
    for i, c in enumerate(a):
        if i >= len(b) or c != b[i]:
            return a[:i]
    return a


def choice_label(column_name: str, position: int, peer_columns: list[str]) -> str:
    """
    Etiqueta distinguible para selectores: «n. …» con fragmento que diferencia ítems
    (subítem tipo Google Forms tras «[», o texto sin prefijo común largo, o cola).
    """
    s = column_name.replace("\n", " ").strip()
    peers = [p.replace("\n", " ").strip() for p in peer_columns] if peer_columns else [s]
    tag: str
    if "[" in s:
        tag = s[s.index("[") :].strip()
    else:
        lcp = _longest_common_prefix(peers)
        if len(lcp) >= 35 and s.startswith(lcp):
            tag = s[len(lcp) :].strip()
        else:
            tag = s
        if len(tag) < 6 and len(s) > 50:
            tag = s
    return f"{position}. {tag}"


def build_column_label_map(columns: list[str]) -> dict[str, str]:
    """Mapa nombre interno de columna → etiqueta para UI (orden + fragmento distintivo)."""
    if not columns:
        return {}
    return {c: choice_label(c, i + 1, columns) for i, c in enumerate(columns)}


SPANISH_STOP = frozenset(
    """
    el la los las un una unos unas y o u de del al a en con por para sin sobre entre
    hacia hasta desde que como cuando donde quien cual cuales esto esa esos esas ese
    esta este son somos soy eres es han he ha muy mas menos todo toda todos todas
    algo alguien nada nadie mismo misma mismos mismas tambien tampoco solo sola tan
    ya sea sei ser sido siendo fue fueron será serán podría puede pueden podemos
    hay había haber tener tengo tiene tienen hacer hace hacen dicho dije otros otra
    otro entre más menos bien mal no sí si yo tu él ella nos vos ellos ellas mi tu su
    nuestro vuestra cualquier cada qué cómo cuál quién
    """.split()
)


def lexicon_sentiment_es(text: str) -> tuple[str, float]:
    """Sentimiento muy simple sin modelos (respaldo). Retorna etiqueta y score -1..1."""
    POS = frozenset(
        """
        bueno buena buenos buenas mejor mejores útil utiles facil fácil rapido rápido
        ayuda ayudar aprendo aprender entiendo entender claro claros positivo positiva
        ventaja ventajas motiva motivar interesante feliz satisfecho satisfecha
        recomiendo recomendable eficiente productivo genial excelente buenísimo
        confianza confiable innovación oportunidad oportunidades beneficio beneficios
        """.split()
    )
    NEG = frozenset(
        """
        malo mala malos malas peor peores difícil dificil complicado complicada
        problema problemas riesgo riesgos miedo preocupa preocupación preocupaciones
        negativo negativa error errores fraude trampa engaña engaño copiar copiado
        dependencia adicción prohibido sanción sanciones desventaja desventajas
        académica deshonestidad plagiarism plagio rechazo desapruebo desaprueban
        reemplazo miedo horrible terrible malísimo
        """.split()
    )

    tokens = re.findall(r"[\wáéíóúñü]+", text.lower())
    p = sum(1 for t in tokens if t in POS)
    n = sum(1 for t in tokens if t in NEG)
    score = (p - n) / max(1, p + n)
    if score > 0.15:
        return "positivo", score
    if score < -0.15:
        return "negativo", score
    return "neutral", score


class SentimentModel:
    _pipe = None

    @classmethod
    def pipe(cls):
        if cls._pipe is None:
            from transformers import pipeline

            cls._pipe = pipeline(
                "sentiment-analysis",
                model="pysentimiento/robertuito-sentiment-analysis",
                truncation=True,
                max_length=256,
            )
        return cls._pipe

    @classmethod
    def predict_batch(cls, texts: list[str], batch_size: int = 16) -> list[dict[str, Any]]:
        """Etiquetas del modelo: NEG, NEU, POS (robertuito)."""
        pipe = cls.pipe()
        out: list[dict[str, Any]] = []
        for i in range(0, len(texts), batch_size):
            chunk = texts[i : i + batch_size]
            out.extend(pipe(chunk))
        return out

    @classmethod
    def map_label(cls, raw: str) -> str:
        u = raw.upper()
        if "POS" in u:
            return "positivo"
        if "NEG" in u:
            return "negativo"
        return "neutral"


@dataclass
class ColumnProfile:
    name: str
    short_name: str
    kind: Literal["estructurada", "abierta"]
    subtype: str
    n_non_null: int
    n_unique: int
    avg_len: float
    max_len: int


def likert_frequency_column_names(profiles: list[ColumnProfile]) -> list[str]:
    """Columnas aptas para Cronbach / PCA: escalas Likert o de frecuencia detectadas."""
    out: list[str] = []
    for p in profiles:
        if p.kind != "estructurada" or p.n_non_null <= 0:
            continue
        st = (p.subtype or "").lower()
        if "likert" in st or "frecuencia" in st:
            out.append(p.name)
    return out


def is_timestamp_column(name: str) -> bool:
    n = name.lower().strip()
    return any(h in n for h in TIMESTAMP_HINTS)


def classify_columns(df: pd.DataFrame) -> list[ColumnProfile]:
    profiles: list[ColumnProfile] = []
    for col in df.columns:
        if is_timestamp_column(col):
            continue
        s = df[col]
        non_null = s.dropna()
        nn = len(non_null)
        if nn == 0:
            profiles.append(
                ColumnProfile(
                    name=col,
                    short_name=_short_label(col),
                    kind="abierta",
                    subtype="sin respuestas",
                    n_non_null=0,
                    n_unique=0,
                    avg_len=0.0,
                    max_len=0,
                )
            )
            continue

        str_s = non_null.astype(str).str.strip()
        lens = str_s.str.len()
        avg_len = float(lens.mean())
        max_len = int(lens.max())
        n_unique = int(str_s.nunique())
        norm = str_s.map(_normalize_cell)

        ratio_likert = norm.isin(LIKERT_TERMS).mean()
        ratio_freq = norm.isin(FREQ_TERMS).mean()
        ratio_bin = norm.isin(BINARY_SI_NO).mean()

        comma_ratio = str_s.str.contains(",").mean()
        card_ratio = n_unique / max(nn, 1)
        col_l = str(col).lower()

        # Subtipo y decisión
        subtype = "mixta / revisar"
        kind: Literal["estructurada", "abierta"] = "estructurada"

        # Priorizar enunciados típicos de respuesta abierta (evita falsos multi-select por comas)
        if any(h in col_l for h in OPEN_QUESTION_HINTS) and avg_len >= 35:
            subtype = "Texto libre (respuesta abierta)"
            kind = "abierta"
        elif ratio_likert >= 0.45:
            subtype = "Escala tipo Likert (acuerdo)"
            kind = "estructurada"
        elif ratio_freq >= 0.45:
            subtype = "Escala de frecuencia"
            kind = "estructurada"
        elif ratio_bin >= 0.85 and n_unique <= 4:
            subtype = "Binaria (Sí/No u opciones cerradas)"
            kind = "estructurada"
        elif n_unique <= 80 and card_ratio < 0.25:
            # Listas cerradas con etiquetas largas (ej. facultades) u opciones repetidas.
            if comma_ratio >= 0.35:
                subtype = "Selección múltiple (valores separados por comas)"
            else:
                subtype = "Categórica (lista cerrada)"
            kind = "estructurada"
        elif n_unique <= 28 and avg_len <= 62:
            subtype = "Categórica (opción única o poca cardinalidad)"
            kind = "estructurada"
        elif comma_ratio >= 0.35 and avg_len <= 140:
            subtype = "Selección múltiple (valores separados por comas)"
            kind = "estructurada"
        elif max_len >= 220 or (avg_len >= 55 and card_ratio > 0.35):
            subtype = "Texto libre (respuesta abierta)"
            kind = "abierta"
        elif n_unique > 70 and avg_len >= 42:
            subtype = "Alta cardinalidad (texto libre o respuestas muy heterogéneas)"
            kind = "abierta"
        else:
            subtype = "Categórica / escala (revisar visualmente)"
            kind = "estructurada"

        profiles.append(
            ColumnProfile(
                name=col,
                short_name=_short_label(col),
                kind=kind,
                subtype=subtype,
                n_non_null=nn,
                n_unique=n_unique,
                avg_len=avg_len,
                max_len=max_len,
            )
        )
    return profiles


def explode_multiselect(series: pd.Series, sep: str = ",") -> pd.Series:
    """Divide respuestas tipo 'ChatGPT, Gemini' en filas."""
    rows: list[str] = []
    for v in series.dropna().astype(str):
        parts = [p.strip() for p in v.split(sep) if p.strip()]
        rows.extend(parts)
    return pd.Series(rows)


def add_total_count_row(
    df: pd.DataFrame,
    *,
    label_col: str | None = None,
    value_col: str = "n",
    total_label: str = "TOTAL",
) -> pd.DataFrame:
    """Añade fila TOTAL sumando la columna numérica (tablas categoría × conteo)."""
    if df.empty or value_col not in df.columns:
        return df
    label = label_col or df.columns[0]
    if label in df.columns and (df[label].astype(str) == total_label).any():
        return df
    total = int(pd.to_numeric(df[value_col], errors="coerce").fillna(0).sum())
    return pd.concat(
        [df, pd.DataFrame([{label: total_label, value_col: total}])],
        ignore_index=True,
    )


def frequency_table(series: pd.Series, top_n: int = 25) -> pd.DataFrame:
    vc = series.dropna().astype(str).value_counts()
    total = int(vc.sum())
    out = vc.head(top_n).rename_axis("categoría").reset_index(name="frecuencia")
    if total > 0:
        out["porcentaje"] = (out["frecuencia"] / total * 100).round(2)
        out = pd.concat(
            [
                out,
                pd.DataFrame(
                    [{"categoría": "TOTAL", "frecuencia": total, "porcentaje": 100.0}]
                ),
            ],
            ignore_index=True,
        )
    else:
        out["porcentaje"] = 0.0
    return out


def thematic_nmf(
    texts: list[str], n_topics: int = 5, max_features: int = 2000
) -> tuple[list[dict[str, Any]], np.ndarray, list[int], dict[int, list[str]], list[str]]:
    """
    Temas vía NMF + TF‑IDF (exploratorio, no sustituye codificación manual).
    Devuelve tablas de temas, matriz W, tema dominante por respuesta (1..K), citas por tema, y la lista de textos alineada con esos índices.
    """
    clean = [t.strip() for t in texts if t and len(t.strip()) > 3]
    empty_ret: tuple[list[dict[str, Any]], np.ndarray, list[int], dict[int, list[str]], list[str]] = (
        [],
        np.array([]),
        [],
        {},
        [],
    )
    if len(clean) < max(10, n_topics * 5):
        return empty_ret

    n_topics = min(n_topics, len(clean) // 3, 12)
    if n_topics < 2:
        return empty_ret

    def _preprocess(t: str) -> str:
        toks = re.findall(r"[\wáéíóúñü]{3,}", t.lower())
        return " ".join(w for w in toks if w not in SPANISH_STOP)

    processed = [_preprocess(t) for t in clean]
    if not any(processed):
        return empty_ret

    min_df_eff = 2 if len(clean) >= 40 else 1
    vectorizer = TfidfVectorizer(max_df=0.9, min_df=min_df_eff, max_features=max_features)
    X = vectorizer.fit_transform(processed)
    if X.shape[1] < 5:
        return empty_ret

    nmf = NMF(n_components=n_topics, init="random", random_state=42, max_iter=800)
    W = nmf.fit_transform(X)
    H = nmf.components_
    feat = np.array(vectorizer.get_feature_names_out())

    topics: list[dict[str, Any]] = []
    for i in range(n_topics):
        top_idx = H[i].argsort()[::-1][:12]
        topics.append(
            {
                "tema": i + 1,
                "palabras_clave": ", ".join(feat[top_idx]),
                "peso_tema_documento_medio": float(W[:, i].mean()),
            }
        )

    dominant = [int(np.argmax(W[i])) + 1 for i in range(len(clean))]
    quotes: dict[int, list[str]] = {}
    for ti in range(n_topics):
        order = np.argsort(W[:, ti])[::-1][:6]
        excerpts = [clean[j] for j in order if W[j, ti] > 1e-5]
        quotes[ti + 1] = excerpts[:5]

    return topics, W, dominant, quotes, clean


def ngram_top_table(
    texts: list[str],
    ngram_range: tuple[int, int] = (2, 3),
    top_n: int = 45,
    min_freq: int = 2,
) -> pd.DataFrame:
    """Bigramas / trigramas más frecuentes (apoyo para lectura léxica del discurso)."""
    clean = [t.strip() for t in texts if t and len(t.strip()) > 4]
    if len(clean) < 8:
        return pd.DataFrame()

    def _tok_line(t: str) -> str:
        toks = re.findall(r"[\wáéíóúñü]+", t.lower())
        return " ".join(w for w in toks if w not in SPANISH_STOP and len(w) > 2)

    corpus = [_tok_line(t) for t in clean if _tok_line(t)]
    if len(corpus) < 6:
        return pd.DataFrame()

    min_df_use = min_freq if len(corpus) >= 40 else 1
    try:
        cv = CountVectorizer(
            ngram_range=ngram_range,
            min_df=min_df_use,
            max_df=0.92,
            token_pattern=r"(?u)\b[\wáéíóúñü]{2,}\b",
        )
        Xm = cv.fit_transform(corpus)
        sums = np.asarray(Xm.sum(axis=0)).ravel()
        names = cv.get_feature_names_out()
        ix = np.argsort(sums)[::-1][:top_n]
        out = pd.DataFrame(
            {"secuencia": [names[i] for i in ix], "frecuencia": [int(sums[i]) for i in ix]}
        )
        out["porcentaje"] = (out["frecuencia"] / out["frecuencia"].sum() * 100).round(2)
        return out
    except ValueError:
        return pd.DataFrame()


def kwic_snippets(
    texts: list[str],
    needle: str,
    *,
    max_hits: int = 40,
    half_window: int = 60,
) -> list[str]:
    """
    Concordancias tipo KWIC: fragmentos centrados alrededor de una palabra o frase buscada.
    """
    q = needle.lower().strip()
    if len(q) < 2:
        return []
    out: list[str] = []
    for t in texts:
        tl = t.lower()
        pos = 0
        while True:
            i = tl.find(q, pos)
            if i == -1:
                break
            a = max(0, i - half_window)
            b = min(len(t), i + len(q) + half_window)
            frag = " ".join(t[a:b].split())
            if a > 0:
                frag = "… " + frag
            if b < len(t):
                frag = frag + " …"
            out.append(frag)
            if len(out) >= max_hits:
                return out
            pos = i + max(1, len(q))
    return out
