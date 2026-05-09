"""
Informes cualitativos narrativos extendidos (Markdown) a partir de resultados automáticos.
No sustituyen el juicio del investigador; amplían la síntesis con evidencias del corpus.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any

import numpy as np
import pandas as pd

# --- Lexicones orientativos para mapear temas / textos a “dimensiones” interpretables ---
DOMAIN_LEXICON: dict[str, set[str]] = {
    "Utilidad, eficiencia y apoyo al aprendizaje": {
        "útil",
        "utilidad",
        "ayuda",
        "aprender",
        "aprendizaje",
        "comprender",
        "entender",
        "estudiar",
        "resumen",
        "resumir",
        "tiempo",
        "rápido",
        "rapido",
        "eficiencia",
        "organizar",
        "ideas",
        "información",
        "consulta",
        "explicar",
        "explicación",
        "tutor",
        "acompañar",
        "facilitar",
        "mejorar",
        "desempeño",
    },
    "Riesgos, dependencia y pensamiento crítico": {
        "riesgo",
        "riesgos",
        "miedo",
        "temor",
        "preocupación",
        "preocupaciones",
        "dependencia",
        "acostumbr",
        "pensamiento",
        "crítico",
        "crítica",
        "autonomía",
        "autonomia",
        "propio",
        "reemplazar",
        "comodidad",
        "vago",
    },
    "Ética académica, plagio y normativa": {
        "plagio",
        "copiar",
        "honestidad",
        "sanción",
        "sanciones",
        "desaprobar",
        "evaluación",
        "examen",
        "trabajo",
        "autoría",
        "indebido",
        "fraude",
        "ética",
        "etica",
        "académico",
        "academico",
    },
    "Formación, lineamientos y uso responsable": {
        "formación",
        "formacion",
        "capacitación",
        "capacitacion",
        "enseñar",
        "ensenar",
        "lineamiento",
        "normativa",
        "regla",
        "reglas",
        "institucional",
        "universidad",
        "profesor",
        "docente",
        "orientación",
        "orientacion",
        "alfabetización",
        "alfabetizacion",
        "responsable",
        "criterio",
        "validar",
        "verificar",
    },
    "Confiabilidad, veracidad y calidad de la información": {
        "verdad",
        "veraz",
        "error",
        "incorrecto",
        "confiable",
        "fiabilidad",
        "información",
        "informacion",
        "fuentes",
        "contrastar",
        "verificar",
        "alucina",
    },
}


def _tokens(s: str) -> list[str]:
    return re.findall(r"[\wáéíóúñü]+", s.lower())


def _stop_es() -> set[str]:
    from survey_intel import SPANISH_STOP

    return set(SPANISH_STOP)


def domain_scores_for_string(text: str) -> dict[str, float]:
    """Puntuación bruta por presencia de vocablos de dominio en el texto (minúsculas)."""
    low = text.lower()
    scores: dict[str, float] = {}
    for dom, lex in DOMAIN_LEXICON.items():
        s = 0.0
        for w in lex:
            if w in low:
                s += float(low.count(w)) * (1.15 if len(w) > 5 else 1.0)
        scores[dom] = s
    return scores


def top_content_words(texts: list[str], n: int = 14) -> list[tuple[str, int]]:
    sw = _stop_es()
    ctr: Counter[str] = Counter()
    for t in texts:
        for w in _tokens(t):
            if len(w) < 4 or w in sw:
                continue
            ctr[w] += 1
    return ctr.most_common(n)


def deep_thematic_markdown(
    question_label: str,
    topics: list[dict[str, Any]],
    dominant: list[int],
    quotes: dict[int, list[str]],
    texts_nmf: list[str],
) -> str:
    ql = question_label.strip()
    n = len(texts_nmf)
    k = len(topics)
    if not topics or not dominant or not texts_nmf:
        return (
            "## Informe cualitativo temático\n\n"
            f"**Pregunta abierta:** «{ql}»  \n\n"
            "_No se generó el modelado temático: pocas respuestas válidas, texto demasiado corto o "
            "vocabulario insuficiente para factorizar. Probá aumentar la muestra, relajar el número de temas o "
            "revisar la columna seleccionada._\n"
        )

    lines: list[str] = [
        f"## Informe cualitativo temático (exploratorio, NMF + TF‑IDF)\n",
        f"**Pregunta abierta:** «{ql}»  \n",
        f"Se trabajó con **{n}** respuestas analizables en el modelo y **{k}** temas automáticos. "
        "Las etiquetas de tema son **asistidas por algoritmo**; conviene renombrarlas con tus categorías teóricas "
        "y contrastarlas con las citas.\n",
    ]

    vc = Counter(dominant)
    lines.append("### Distribución por tema (asignación dominante por respuesta)\n")
    for tid in sorted(vc.keys()):
        pct = 100.0 * vc[tid] / max(1, n)
        lines.append(f"- **Tema {tid}:** {vc[tid]} respuestas ({pct:.1f} % del corpus modelado)\n")

    lines.append("\n### Descripción por tema automático\n")
    for t in topics:
        tid = int(t["tema"])
        kw = str(t.get("palabras_clave", ""))
        ev = " ".join(quotes.get(tid, [])[:3])
        dscores = domain_scores_for_string(kw + " " + ev)
        dom_top = max(dscores, key=dscores.get) if dscores else ""
        lines.append(f"#### Tema {tid}\n")
        lines.append(f"- **Palabras fuertemente asociadas (TF‑IDF agregado):** {kw}\n")
        if dom_top and dscores.get(dom_top, 0) > 0:
            lines.append(
                f"- **Afinidad léxica preliminar (solapamiento con diccionario de dominios):** "
                f"«{dom_top}» (indicación débil; validá con lectura).\n"
            )
        if quotes.get(tid):
            lines.append("- **Fragmentos ilustrativos (orden de relevancia aproximada en el modelo):**\n")
            for j, ex in enumerate(quotes[tid][:4], 1):
                excerpt = ex[:420] + ("…" if len(ex) > 420 else "")
                lines.append(f"  {j}. _{excerpt}_\n")
        lines.append("\n")

    # Dimensión agregada por dominio
    dom_aggregate: Counter[str] = Counter()
    for t in topics:
        tid = int(t["tema"])
        blob = str(t.get("palabras_clave", "")) + " " + " ".join(quotes.get(tid, []))
        ds = domain_scores_for_string(blob)
        best = max(ds, key=ds.get) if ds else None
        if best is not None and ds[best] > 0:
            dom_aggregate[best] += int(vc.get(tid, 0))

    lines.append("### Lectura integrada: dimensiones temáticas tentativas\n")
    lines.append(
        "A continuación se **agrupan** los temas según coincidencia léxica heurística con familias de sentido "
        "(utilidad, riesgo, ética, formación, fiabilidad). Es una **aproximación** para orientar la narrativa; "
        "no reemplaza tu codificación.\n\n"
    )
    if dom_aggregate:
        for dom, weight in dom_aggregate.most_common():
            lines.append(f"- **{dom}** (ponderación aproximada por volumen de respuestas en temas asociados): índice {weight}.\n")
    else:
        lines.append(
            "_No se obtuvo contraste claro entre dominios con el léxico disponible; revisá citas y renombrá temas manualmente._\n"
        )

    lines.append("\n### Dimensiones sugeridas (agrupación temática → familias de sentido)\n")

    inv: dict[str, list[int]] = defaultdict(list)
    for t in topics:
        tid = int(t["tema"])
        blob = str(t.get("palabras_clave", "")) + " " + " ".join(quotes.get(tid, []))
        ds = domain_scores_for_string(blob)
        if ds and max(ds.values()) > 0:
            dom_t = max(ds, key=ds.get)
        else:
            dom_t = "Mezcla o formulación diversa / revisar citas"
        inv[dom_t].append(tid)

    for dom in sorted(inv.keys(), key=lambda d: -sum(vc.get(ti, 0) for ti in inv[d])):
        tids = sorted(inv[dom])
        mass = sum(vc.get(ti, 0) for ti in tids)
        lines.append(f"#### {dom}\n")
        lines.append(
            f"Agrupa los **temas automáticos {', '.join(str(x) for x in tids)}**, que concentran **{mass}** respuestas "
            f"como tema dominante (~{100.0 * mass / max(1, n):.1f} % del corpus modelado). "
            "Podés nombrar esta dimensión en el informe (p. ej. “ventajas percibidas”, “alertas académicas”) según lectura fina de los fragmentos.\n\n"
        )

    lines.append("\n### Síntesis interpretativa orientativa\n")
    top_tid, top_n = vc.most_common(1)[0]
    tp = next((x for x in topics if int(x["tema"]) == top_tid), {})
    kw_t = tp.get("palabras_clave", "")[:200]
    lines.append(
        f"El **tema más frecuente como dominante** en las respuestas es el **{top_tid}** ({top_n} casos), "
        f"asociado léxicamente a: _{kw_t}_. En conjunto, el corpus modelado sugiere **varias líneas de sentido** "
        f"({k} particiones) que conviene etiquetar conceptualmente en el informe final. "
        "Recomendación metodológica: triangulá esta partición automática con **codificación manual** sobre un subconjunto "
        "y con el marco teórico de tu investigación.\n"
    )
    return "".join(lines)


def deep_sentiment_markdown(
    question_label: str,
    filtered: list[str],
    results: list[str],
    dist: pd.DataFrame,
    metodo: str,
) -> str:
    ql = question_label.strip()
    total = int(dist["n"].sum()) if not dist.empty else 0
    lines: list[str] = [
        f"## Informe de sentimiento (tono orientativo)\n",
        f"**Pregunta abierta:** «{ql}»  \n",
        f"**Método:** {metodo}. **Respuestas clasificadas:** {total}.\n\n",
        "Este informe describe **tono léxico/emocional aproximado**; las categorías no miden actitudes latentes ni "
        "intención comunicativa plena.\n\n",
        "### Distribución global\n",
    ]
    if dist.empty:
        return "".join(lines) + "_Sin datos suficientes._\n"

    for _, row in dist.sort_values("n", ascending=False).iterrows():
        lines.append(
            f"- **{row['sentimiento']}:** n = {int(row['n'])} ({float(row['pct']):.1f} %)\n"
        )

    by_lab: dict[str, list[str]] = {"positivo": [], "neutral": [], "negativo": []}
    for t, lab in zip(filtered, results):
        if lab in by_lab:
            by_lab[lab].append(t)

    lines.append("\n### Desarrollo por categoría de polaridad\n")
    for lab, title in [
        ("positivo", "Tono favorable o valoración positiva"),
        ("neutral", "Tono neutro, descriptivo o ambivalente"),
        ("negativo", "Tono de preocupación, crítica o rechazo parcial"),
    ]:
        texts = by_lab.get(lab, [])
        if not texts:
            lines.append(f"#### {title}\n_No hay casos en esta categoría._\n\n")
            continue
        lines.append(f"#### {title}\n")
        lines.append(
            f"Frecuencia relativa en la clasificación: **{len(texts)}** textos. "
            "Términos léxicos más recurrentes (excluye stopwords):\n\n"
        )
        terms = top_content_words(texts, n=12)
        if terms:
            lines.append("- " + ", ".join(f"**{w}** ({c})" for w, c in terms[:10]) + "\n\n")
        lines.append("_Ejemplos (aleatorización fija opcional en la app): revisá la tabla y ejemplos en la pestaña._\n\n")

    dom = dist.sort_values("n", ascending=False).iloc[0]
    dom_name = str(dom["sentimiento"])
    dom_pct = float(dom["pct"])

    lines.append("### Interpretación integrada\n")
    lines.append(
        f"La categoría **{dom_name}** aparece como **mayoritaria** (~{dom_pct:.1f} % de las clasificaciones). "
    )
    if dom_name == "positivo":
        lines.append(
            "Esto suele indicar un discurso donde predominan evaluaciones de utilidad, facilidad o apoyo al estudio; "
            "debe leerse junto con la consigna: preguntas “desde el beneficio” sesgan hacia polaridad positiva.\n"
        )
    elif dom_name == "neutral":
        lines.append(
            "Un predominio **neutral** suele reflejar respuestas descriptivas, prudentes o balanceadas entre riesgos y ventajas. "
            "Valorá si la redacción de la pregunta invitaba a matizar.\n"
        )
    else:
        lines.append(
            "Un predominio de tono **negativo o de alerta** muestra preocupación léxica (riesgo, plagio, miedo, dependencia). "
            "No implica rechazo total a la tecnología: a menudo expresa cautela.\n"
        )

    lines.append(
        "\n**Conclusión operativa:** usá esta distribución como **mapa preliminar del clima expresivo** del corpus; "
        "cruzala con el análisis temático y con lectura cualitativa fina antes de politizar resultados.\n"
    )
    return "".join(lines)


def deep_discourse_markdown(
    question_label: str,
    filtered: list[str],
    bi: pd.DataFrame,
    tri: pd.DataFrame,
    needle: str,
    kwic_hits: list[str],
) -> str:
    ql = question_label.strip()
    corpus = "\n".join(filtered)
    d_full = domain_scores_for_string(corpus)
    lines: list[str] = [
        f"## Informe orientativo de lectura del discurso\n",
        f"**Pregunta abierta:** «{ql}»  \n",
        f"**Corpus:** {len(filtered)} respuestas con longitud suficiente para insumos léxicos.\n\n",
        "Este apartado **no** realiza análisis del discurso epistémico completo (orden del discurso, ideología, posicionamientos); "
        "reúne **regularidades léxicas y de co-ocurrencia** como puntos de partida hermenéuticos.\n\n",
        "### Regularidades de formulación (n-gramas)\n",
    ]

    if not bi.empty:
        topb = bi.head(12)
        lines.append("**Bigramas frecuentes** (indicios de motivos recurrentes de enunciación):\n\n")
        for _, row in topb.iterrows():
            lines.append(f"- «{row['secuencia']}» — frecuencia {int(row['frecuencia'])}\n")
        lines.append("\n")
    else:
        lines.append("_No hay bigramas lo suficientemente estables en este subconjunto._\n\n")

    if not tri.empty:
        ttop = tri.head(10)
        lines.append("**Trigramas frecuentes** (patrones de secuencia algo más específicos):\n\n")
        for _, row in ttop.iterrows():
            lines.append(f"- «{row['secuencia']}» — frecuencia {int(row['frecuencia'])}\n")
        lines.append("\n")
    else:
        lines.append("_Trigramas poco repetidos o corpus breve para esta granularidad._\n\n")

    nq = (needle or "").strip()
    if nq:
        lines.append("### Concordancias (KWIC) focalizadas\n")
        lines.append(
            f"Búsqueda activa: **«{nq}»** — **{len(kwic_hits)}** apariciones contextuales listadas en la interfaz. "
            "Sirven para ver **cómo se enmarca** semánticamente el término en el discurso estudiantil "
            "(condena, justificación, condicionalidad, etc.).\n\n"
        )

    lines.append("### Tensiones y ejes discursivos inferidos (heurística léxica)\n")
    sorted_dom = sorted(d_full.items(), key=lambda x: -x[1])[:5]
    for dom, sc in sorted_dom:
        if sc <= 0:
            continue
        lines.append(
            f"- **{dom}**: intensidad relativa de vocablos afines en el corpus completo (puntuación bruta **{sc:.0f}**). "
            "Compará entre submuestras si tu diseño lo permite.\n"
        )

    u = d_full.get("Utilidad, eficiencia y apoyo al aprendizaje", 0)
    r = d_full.get("Riesgos, dependencia y pensamiento crítico", 0) + d_full.get(
        "Ética académica, plagio y normativa", 0
    )
    lines.append("\n**Lectura de tensiones (tentativa):** ")
    if u > 0 and r > 0:
        if u >= r * 1.2:
            lines.append(
                "el corpus muestra un **peso algo mayor** de formulaciones centradas en utilidad/apoyo que de alerta "
                "ética o de riesgo; ello no invalida la preocupación, que puede aparecer de forma más sutil.\n"
            )
        elif r >= u * 1.1:
            lines.append(
                "las **voces de alerta** (riesgo, ética, dependencia) tienen presión léxica **comparable o superior** "
                "a la de la utilidad; sugiere un discurso **fuertemente mediatizado** por la regulación académica y el miedo al uso indebido.\n"
            )
        else:
            lines.append(
                "conviven en intensidad **parecida** registros de utilidad y de riesgo/ética: un discurso típicamente **ambivalente**, "
                "coherente con debates sobre IA en educación.\n"
            )
    else:
        lines.append("los dominios léxicos no contrastan lo suficiente: revisá manualmente citas extensas.\n")

    lines.append(
        "\n### Síntesis crítica\n"
        "Los patrones automáticos apuntan a **cómo se dice** más que al sentido profundo final. "
        "Para aproximarte a un análisis del discurso robusto, articulá estos insumos con **teoría**, **entrevistas** o "
        "**categorías inductivas** y explicitá posiciones del analista.\n"
    )
    return "".join(lines)
