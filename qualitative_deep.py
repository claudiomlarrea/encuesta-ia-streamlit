"""
Informes cualitativos narrativos (Markdown) alineados a informes institucionales.
Amplía NMF, léxico y concordancias con tablas, interpretaciones y ejes discursivos.
No sustituyen la codificación manual del investigador.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

# --- Lexicones de dominio (discurso general) ---
DOMAIN_LEXICON: dict[str, set[str]] = {
    "Utilidad, eficiencia y apoyo al aprendizaje": {
        "útil", "utilidad", "ayuda", "aprender", "aprendizaje", "comprender", "entender",
        "estudiar", "resumen", "resumir", "tiempo", "rápido", "rapido", "eficiencia",
        "organizar", "ideas", "información", "consulta", "explicar", "explicación",
        "tutor", "acompañar", "facilitar", "mejorar", "desempeño",
    },
    "Riesgos, dependencia y pensamiento crítico": {
        "riesgo", "riesgos", "miedo", "temor", "preocupación", "preocupaciones",
        "dependencia", "acostumbr", "pensamiento", "crítico", "crítica", "autonomía",
        "autonomia", "propio", "reemplazar", "comodidad", "vago",
    },
    "Ética académica, plagio y normativa": {
        "plagio", "copiar", "honestidad", "sanción", "sanciones", "desaprobar",
        "evaluación", "examen", "trabajo", "autoría", "indebido", "fraude", "ética",
        "etica", "académico", "academico",
    },
    "Formación, lineamientos y uso responsable": {
        "formación", "formacion", "capacitación", "capacitacion", "enseñar", "ensenar",
        "lineamiento", "normativa", "regla", "reglas", "institucional", "universidad",
        "profesor", "docente", "orientación", "orientacion", "alfabetización",
        "alfabetizacion", "responsable", "criterio", "validar", "verificar",
    },
    "Confiabilidad, veracidad y calidad de la información": {
        "verdad", "veraz", "error", "incorrecto", "confiable", "fiabilidad",
        "información", "informacion", "fuentes", "contrastar", "verificar", "alucina",
    },
}


@dataclass(frozen=True)
class ThemeCategory:
    name: str
    keywords: tuple[str, ...]
    description: str
    interpretation: str


@dataclass(frozen=True)
class DiscourseAxis:
    title: str
    bullets: tuple[str, ...]
    interpretation: str
    keywords: tuple[str, ...]


CAPACITACION_THEMES: tuple[ThemeCategory, ...] = (
    ThemeCategory(
        "IA para la Investigación Académica",
        (
            "investig", "bibliograf", "paper", "artículo", "articulo", "informe",
            "revisión", "revision", "científic", "cientific", "académic", "academic",
            "tesis", "monograf", "referenc", "cita", "literatura", "publi",
        ),
        "Interés en utilizar IA para búsqueda de información científica, revisión bibliográfica, "
        "elaboración de trabajos académicos, redacción de informes e investigación.",
        "Los estudiantes perciben a la IA principalmente como herramienta de apoyo para la "
        "producción y gestión del conocimiento académico, más que como recurso exclusivamente tecnológico.",
    ),
    ThemeCategory(
        "Automatización de Tareas y Productividad",
        (
            "automatiz", "productividad", "eficiencia", "tarea", "organiz", "ahorr",
            "optimiz", "rutina", "gestión", "gestion", "planific", "agenda",
        ),
        "Interés por optimizar tareas rutinarias, mejorar la organización del trabajo y "
        "aumentar la eficiencia en actividades académicas.",
        "Los estudiantes valoran la IA como herramienta para ahorrar tiempo y mejorar el "
        "rendimiento personal, asociando su uso con mayor productividad.",
    ),
    ThemeCategory(
        "Análisis de Datos con IA",
        (
            "dato", "análisis", "analisis", "estadíst", "estadist", "machine learning",
            "big data", "procesamiento", "tabla", "excel", "spss", "python", "r ",
            "visualiz", "gráfico", "grafico",
        ),
        "Demanda vinculada con el procesamiento, interpretación y análisis de información mediante IA.",
        "Indica interés por competencias analíticas y de manejo de datos, relevante en carreras "
        "científicas, tecnológicas y de investigación.",
    ),
    ThemeCategory(
        "Prompt Engineering (Ingeniería de Prompts)",
        (
            "prompt", "prompts", "ingeniería de prompt", "ingenieria de prompt",
            "instruccion", "instrucción", "formular", "chatgpt", "gemini", "copilot",
            "interactuar", "consulta efectiva",
        ),
        "Interés en aprender a formular instrucciones eficaces para obtener mejores resultados "
        "de sistemas de IA generativa.",
        "Muestra que parte de los encuestados reconoce que la calidad de los resultados depende "
        "de la capacidad del usuario para interactuar estratégicamente con la herramienta.",
    ),
    ThemeCategory(
        "Ética y Detección de Contenido IA",
        (
            "ética", "etica", "responsable", "detecc", "plagio", "contenido generado",
            "límite", "limite", "norma", "regul", "dependencia", "uso indebido",
            "verificar", "autentic",
        ),
        "Orientación hacia el uso responsable, identificación de contenidos generados "
        "automáticamente y comprensión de límites éticos.",
        "Evidencia preocupación por las implicancias académicas y éticas del uso de IA, "
        "aunque con menor frecuencia que las categorías instrumentales.",
    ),
    ThemeCategory(
        "IA Generativa Multimedia",
        (
            "imagen", "video", "diseño", "multimedia", "presentacion", "presentación",
            "audio", "foto", "ilustr", "canva", "powerpoint", "infograf",
        ),
        "Interés por herramientas que generan imágenes, videos, presentaciones y contenidos multimedia.",
        "La baja frecuencia relativa sugiere que se priorizan aplicaciones académicas e "
        "investigativas antes que usos creativos o audiovisuales.",
    ),
)

VENTAJAS_THEMES: tuple[ThemeCategory, ...] = (
    ThemeCategory(
        "Apoyo al aprendizaje y comprensión",
        ("aprender", "comprender", "entender", "estudiar", "explic", "resumen", "claridad", "tutor"),
        "La IA facilita comprender contenidos, resolver dudas y organizar el estudio.",
        "Predomina una lectura de la IA como complemento cognitivo del proceso de aprendizaje.",
    ),
    ThemeCategory(
        "Ahorro de tiempo y eficiencia",
        ("tiempo", "rápido", "rapido", "eficiencia", "productividad", "automatiz", "organiz"),
        "Ventajas vinculadas a optimizar tareas y reducir carga de trabajo.",
        "Los estudiantes asocian la IA con mayor rendimiento y gestión eficiente del tiempo académico.",
    ),
    ThemeCategory(
        "Acceso a información y actualización",
        ("información", "informacion", "acceso", "actualiz", "consulta", "investig", "fuente"),
        "Facilita el acceso rápido al conocimiento y la exploración de temas.",
        "La IA amplía el acceso inmediato a información, con expectativas de actualización continua.",
    ),
    ThemeCategory(
        "Creatividad y generación de ideas",
        ("idea", "creativ", "inspir", "redact", "escribir", "borrador", "brainstorm"),
        "Apoyo en la generación de ideas, redacción y elaboración de borradores.",
        "Se valora la IA como catalizador de producción textual e ideación.",
    ),
)

RIESGOS_THEMES: tuple[ThemeCategory, ...] = (
    ThemeCategory(
        "Plagio, deshonestidad y uso indebido",
        ("plagio", "copiar", "deshonest", "fraude", "indebido", "sanción", "sancion", "trampa"),
        "Preocupación por el uso académico incorrecto y la integridad de las evaluaciones.",
        "El discurso de alerta se centra en la ética académica y las consecuencias institucionales.",
    ),
    ThemeCategory(
        "Dependencia y debilitamiento del pensamiento crítico",
        ("dependencia", "pensamiento", "crítico", "critico", "autonomía", "autonomia", "reemplaz", "vago"),
        "Temor a delegar tareas cognitivas y perder autonomía intelectual.",
        "Surge tensión entre asistencia tecnológica y desarrollo de competencias propias.",
    ),
    ThemeCategory(
        "Errores, desinformación y falta de confiabilidad",
        ("error", "incorrect", "confiable", "mentira", "falso", "alucin", "verificar", "desinform"),
        "Desconfianza respecto a la veracidad y calidad de las respuestas generadas.",
        "Los estudiantes demandan criterios para validar información producida por IA.",
    ),
    ThemeCategory(
        "Desigualdad de acceso y brecha digital",
        ("acceso", "brecha", "desigual", "privileg", "exclus", "pago", "licencia"),
        "Riesgo de ampliar diferencias entre quienes pueden o no usar herramientas.",
        "La IA puede reproducir o intensificar desigualdades en el acceso al capital digital.",
    ),
)

RECOMENDACIONES_THEMES: tuple[ThemeCategory, ...] = (
    ThemeCategory(
        "Formación institucional y alfabetización en IA",
        ("formación", "formacion", "capacit", "enseñar", "ensenar", "curso", "taller", "alfabet"),
        "Demanda de programas formativos integrados a la currícula universitaria.",
        "Los estudiantes esperan acompañamiento institucional para un uso competente y crítico.",
    ),
    ThemeCategory(
        "Normas claras y políticas de uso",
        ("norma", "regla", "política", "politica", "lineamiento", "regul", "código", "codigo"),
        "Necesidad de marcos explícitos sobre qué está permitido en cada asignatura.",
        "La regulación institucional es percibida como condición para un uso responsable.",
    ),
    ThemeCategory(
        "Uso crítico, verificación y transparencia",
        ("crítico", "critico", "verificar", "validar", "transparen", "declarar", "citar", "responsable"),
        "Recomendaciones orientadas a la honestidad académica y la revisión humana.",
        "Se promueve un uso reflexivo que combine IA con juicio y responsabilidad del estudiante.",
    ),
    ThemeCategory(
        "Integración pedagógica con docentes",
        ("docente", "profesor", "cátedra", "catedra", "clase", "evaluación", "evaluacion", "tarea"),
        "Sugerencias para articular IA en la enseñanza y la evaluación con orientación docente.",
        "La legitimación del uso de IA pasa por el rol activo de las unidades académicas y docentes.",
    ),
)

CAPACITACION_DISCOURSE: tuple[DiscourseAxis, ...] = (
    DiscourseAxis(
        "La IA como herramienta para potenciar el aprendizaje",
        (
            "Comprensión de contenidos.",
            "Apoyo al aprendizaje.",
            "Resolución de dudas.",
            "Síntesis de información.",
            "Mejora del rendimiento académico.",
        ),
        "La inteligencia artificial no es representada como sustituto del estudiante, sino como un "
        "apoyo cognitivo. El estudiante se posiciona como sujeto activo que busca aprender más "
        "eficientemente mediante nuevas herramientas tecnológicas.",
        ("aprender", "comprender", "estudiar", "apoyo", "rendimiento", "duda", "síntesis", "sintesis"),
    ),
    DiscourseAxis(
        "La IA como capital profesional para el futuro",
        (
            "Automatización.",
            "Programación.",
            "Análisis de datos.",
            "Herramientas profesionales.",
            "Aplicaciones específicas de cada disciplina.",
        ),
        "La IA se construye como competencia necesaria para la inserción laboral. La capacitación "
        "se percibe como inversión en capital humano y ventaja competitiva.",
        ("profesional", "laboral", "emple", "carrera", "futuro", "trabajo", "mercado"),
    ),
    DiscourseAxis(
        "La IA como herramienta que requiere alfabetización especializada",
        (
            "No basta con utilizar la IA.",
            "Aprender a interactuar correctamente.",
            "Competencias específicas para resultados de calidad.",
        ),
        "Emerge una alfabetización digital centrada en la interacción humano-algoritmo; el rendimiento "
        "depende de las capacidades del usuario (prompts, criterios, verificación).",
        ("prompt", "alfabet", "competenc", "instrucc", "interact", "chatgpt"),
    ),
    DiscourseAxis(
        "La IA como oportunidad que requiere regulación ética",
        (
            "Ética.",
            "Uso responsable.",
            "Verificación de información.",
            "Riesgos de dependencia.",
            "Limitaciones de la IA.",
        ),
        "Coexiste un discurso de cautela que reconoce la necesidad de criterios éticos. La preocupación "
        "apunta a cómo se utiliza la tecnología, no a su existencia.",
        ("ética", "etica", "responsable", "riesgo", "dependencia", "límite", "limite"),
    ),
    DiscourseAxis(
        "La transformación del rol del estudiante",
        (
            "Gestionar información.",
            "Dialogar con sistemas inteligentes.",
            "Optimizar procesos de aprendizaje.",
            "Integrar tecnología en la construcción del conocimiento.",
        ),
        "Las respuestas sugieren un estudiante que gestiona información y articula tecnología con "
        "construcción del conocimiento, más que un receptor pasivo de contenidos.",
        ("gestionar", "integrar", "construir", "proceso", "autonom", "dialog"),
    ),
)


def _tokens(s: str) -> list[str]:
    return re.findall(r"[\wáéíóúñü]+", s.lower())


def _stop_es() -> set[str]:
    from survey_intel import SPANISH_STOP

    return set(SPANISH_STOP)


def _pct_str(n: int, total: int) -> str:
    if total <= 0:
        return "0,0"
    return f"{100.0 * n / total:.1f}".replace(".", ",")


def _norm_q(label: str) -> str:
    return re.sub(r"\s+", " ", label.lower().strip())


def detect_question_profile(question_label: str) -> str:
    q = _norm_q(question_label)
    if any(k in q for k in ("capacit", "temas te gustaría", "temas te gustaria", "gustaría capacit", "gustaria capacit")):
        return "capacitacion"
    if "ventaja" in q:
        return "ventajas"
    if any(k in q for k in ("riesgo", "preocup", "temor", "miedo")):
        return "riesgos"
    if any(k in q for k in ("recomend", "suger", "propuesta")):
        return "recomendaciones"
    return "general"


def _themes_for_profile(profile: str) -> tuple[ThemeCategory, ...]:
    return {
        "capacitacion": CAPACITACION_THEMES,
        "ventajas": VENTAJAS_THEMES,
        "riesgos": RIESGOS_THEMES,
        "recomendaciones": RECOMENDACIONES_THEMES,
    }.get(profile, ())


def _score_theme(text: str, cat: ThemeCategory) -> float:
    low = text.lower()
    score = 0.0
    for kw in cat.keywords:
        if kw in low:
            score += 1.5 if len(kw) > 6 else 1.0
    return score


def classify_texts_to_themes(
    texts: list[str],
    themes: tuple[ThemeCategory, ...],
) -> tuple[Counter[str], dict[str, list[str]]]:
    """Una categoría dominante por respuesta; el resto va a «Otras respuestas»."""
    counts: Counter[str] = Counter()
    examples: dict[str, list[str]] = defaultdict(list)
    otros = "Otras respuestas"

    for raw in texts:
        t = raw.strip()
        if len(t) < 2:
            continue
        best_name = otros
        best_score = 0.0
        for cat in themes:
            sc = _score_theme(t, cat)
            if sc > best_score:
                best_score = sc
                best_name = cat.name
        counts[best_name] += 1
        if len(examples[best_name]) < 5:
            examples[best_name].append(t[:280])

    return counts, dict(examples)


def _is_preference_question(question_label: str) -> bool:
    q = _norm_q(question_label)
    return any(
        k in q
        for k in (
            "capacit",
            "temas te gustaría",
            "temas te gustaria",
            "gustaría",
            "gustaria",
            "te gustaría",
            "preferencia",
            "interés en",
            "interes en",
        )
    )


def domain_scores_for_string(text: str) -> dict[str, float]:
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


def _quote_block(texts: list[str], n: int = 4) -> str:
    if not texts:
        return ""
    picks: list[str] = []
    for t in sorted(texts, key=len):
        if t not in picks:
            picks.append(t)
        if len(picks) >= n:
            break
    for t in texts:
        if len(picks) >= n:
            break
        if t not in picks:
            picks.append(t)
    lines = []
    for t in picks[:n]:
        excerpt = t[:220] + ("…" if len(t) > 220 else "")
        lines.append(f'> "{excerpt}"\n\n')
    return "".join(lines)


def _thematic_table_md(counts: Counter[str], total: int) -> str:
    rows = []
    otros = "Otras respuestas"
    ordered = [c for c in counts if c != otros]
    ordered.sort(key=lambda x: -counts[x])
    if otros in counts:
        ordered.append(otros)
    for name in ordered:
        n = counts[name]
        rows.append(f"| {name} | {n} | {_pct_str(n, total)} % |")
    body = "\n".join(rows)
    return (
        "| Tema | Frecuencia | % |\n"
        "| --- | ---: | ---: |\n"
        f"{body}\n"
        f"| **Total** | **{total}** | **100 %** |\n"
    )


def _thematic_report_taxonomy(
    question_label: str,
    texts: list[str],
    profile: str,
) -> str:
    themes = _themes_for_profile(profile)
    counts, examples = classify_texts_to_themes(texts, themes)
    total = sum(counts.values()) or len(texts)
    ql = question_label.strip()

    lines = [
        "### Análisis temático\n\n",
        f'**Pregunta:** *"{ql}"*  \n',
        f"**N = {total} estudiantes**\n\n",
    ]

    intro = {
        "capacitacion": (
            "A partir de las respuestas, se identificaron grandes temas dominantes relacionados "
            "con las expectativas de formación en inteligencia artificial.\n\n"
        ),
        "ventajas": (
            "A partir de las respuestas, se identificaron dimensiones recurrentes en la percepción "
            "de ventajas del uso de IA en el ámbito estudiantil.\n\n"
        ),
        "riesgos": (
            "A partir de las respuestas, se identificaron preocupaciones y riesgos asociados al "
            "uso de inteligencia artificial en la universidad.\n\n"
        ),
        "recomendaciones": (
            "A partir de las respuestas, se identificaron recomendaciones para un uso responsable "
            "de la IA en el ámbito académico.\n\n"
        ),
    }.get(profile, "A partir de las respuestas, se identificaron temas dominantes en el corpus analizado.\n\n")
    lines.append(intro)
    lines.append(_thematic_table_md(counts, total))
    lines.append("\n---\n\n")

    theme_map = {t.name: t for t in themes}
    otros = "Otras respuestas"
    ordered_names = [n for n in counts if n != otros]
    ordered_names.sort(key=lambda x: -counts[x])
    if otros in counts:
        ordered_names.append(otros)

    for i, name in enumerate(ordered_names, 1):
        n = counts[name]
        if n == 0:
            continue
        pct = _pct_str(n, total)
        lines.append(f"## Tema {i}. {name} ({pct} %)\n\n")
        if name in theme_map:
            lines.append(f"{theme_map[name].description}\n\n")
            if examples.get(name):
                lines.append("### Ejemplos representativos\n\n")
                lines.append(_quote_block(examples[name]))
            lines.append("### Interpretación\n\n")
            lines.append(f"{theme_map[name].interpretation}\n\n")
            lines.append("---\n\n")
        else:
            lines.append(
                "Respuestas que no coinciden de forma clara con las categorías temáticas "
                "predefinidas; conviene revisarlas manualmente para subclasificar.\n\n"
            )
            if examples.get(name):
                lines.append(_quote_block(examples[name]))
            lines.append("---\n\n")

    lines.append("## Interpretación general\n\n")
    if profile == "capacitacion":
        lines.append(
            "El análisis temático muestra que los estudiantes no demandan únicamente capacitación "
            "en el uso básico de herramientas de inteligencia artificial. Sus intereses se concentran "
            "principalmente en la **aplicación de la IA a la investigación académica**, la **mejora de "
            "la productividad** y el **análisis de datos**. Aspectos como la ética, la detección de "
            "contenido generado por IA y las aplicaciones multimedia aparecen como intereses "
            "complementarios. Esto sugiere diseñar programas formativos que prioricen investigación "
            "asistida por IA, análisis de datos y uso estratégico de herramientas generativas.\n"
        )
    elif profile == "ventajas":
        lines.append(
            "El corpus articula la IA como recurso para **aprender mejor**, **ahorrar tiempo** y "
            "**acceder a información**. Predomina una valoración instrumental favorable vinculada al "
            "desempeño académico.\n"
        )
    elif profile == "riesgos":
        lines.append(
            "Las preocupaciones se organizan en torno a **integridad académica**, **dependencia "
            "cognitiva**, **confiabilidad de la información** y, en menor medida, **brechas de acceso**. "
            "El tono es de alerta reguladora más que de rechazo tecnológico.\n"
        )
    elif profile == "recomendaciones":
        lines.append(
            "Las recomendaciones apuntan a **formación institucional**, **normas claras**, **uso crítico** "
            "y **acompañamiento docente**. Los estudiantes esperan marcos compartidos para legitimar el uso de IA.\n"
        )
    else:
        top = counts.most_common(3)
        if top:
            tops = ", ".join(f"**{n}** ({_pct_str(c, total)} %)" for n, c in top)
            lines.append(
                f"Los temas con mayor peso relativo son: {tops}. Contrastá esta lectura automática "
                "con codificación manual y tu marco teórico.\n"
            )

    return "".join(lines)


def _thematic_report_nmf(
    question_label: str,
    topics: list[dict[str, Any]],
    dominant: list[int],
    quotes: dict[int, list[str]],
    texts_nmf: list[str],
) -> str:
    n = len(texts_nmf)
    k = len(topics)
    ql = question_label.strip()
    vc = Counter(dominant)

    lines = [
        "### Análisis temático (exploratorio — NMF + TF‑IDF)\n\n",
        f'**Pregunta:** *"{ql}"*  \n',
        f"**N = {n} respuestas** incluidas en el modelo ({k} particiones automáticas).\n\n",
        "_Las etiquetas provienen de un algoritmo; renombrá cada tema con categorías teóricas._\n\n",
    ]

    rows = []
    for tid in sorted(vc.keys()):
        cnt = vc[tid]
        rows.append(f"| Tema automático {tid} | {cnt} | {_pct_str(cnt, n)} % |")
    lines.append("| Tema (NMF) | Frecuencia | % |\n| --- | ---: | ---: |\n")
    lines.append("\n".join(rows) + f"\n| **Total** | **{n}** | **100 %** |\n\n---\n\n")

    for t in topics:
        tid = int(t["tema"])
        cnt = vc.get(tid, 0)
        pct = _pct_str(cnt, n)
        kw = str(t.get("palabras_clave", ""))
        lines.append(f"## Tema {tid} ({pct} % del corpus modelado)\n\n")
        lines.append(f"**Palabras asociadas:** {kw}\n\n")
        if quotes.get(tid):
            lines.append("### Ejemplos representativos\n\n")
            lines.append(_quote_block(quotes[tid]))
        dscores = domain_scores_for_string(kw + " " + " ".join(quotes.get(tid, [])))
        if dscores and max(dscores.values()) > 0:
            dom = max(dscores, key=dscores.get)
            lines.append(f"### Interpretación orientativa\n\n")
            lines.append(
                f"Por afinidad léxica, este tema se acerca a la dimensión «{dom}». "
                "Validá con lectura fina antes de incorporarlo al informe.\n\n"
            )
        lines.append("---\n\n")

    top_tid, top_n = vc.most_common(1)[0]
    lines.append("## Interpretación general\n\n")
    lines.append(
        f"El tema automático **{top_tid}** concentra **{top_n}** respuestas como dominante. "
        "Triangulá con codificación manual y, si la pregunta es de capacitación, ventajas o riesgos, "
        "compará con las categorías institucionales del Observatorio.\n"
    )
    return "".join(lines)


def deep_thematic_markdown(
    question_label: str,
    topics: list[dict[str, Any]],
    dominant: list[int],
    quotes: dict[int, list[str]],
    texts_nmf: list[str],
    *,
    corpus: list[str] | None = None,
) -> str:
    texts = [t.strip() for t in (corpus or texts_nmf) if t and len(t.strip()) > 1]
    if not texts:
        return (
            "### Análisis temático\n\n"
            f'**Pregunta:** *"{question_label.strip()}"*  \n\n'
            "_No hay respuestas analizables en esta columna._\n"
        )

    profile = detect_question_profile(question_label)
    themed = _themes_for_profile(profile)
    if themed:
        return _thematic_report_taxonomy(question_label, texts, profile)
    if topics and dominant and texts_nmf:
        return _thematic_report_nmf(question_label, topics, dominant, quotes, texts_nmf)
    return _thematic_report_taxonomy(question_label, texts, "general")


def deep_sentiment_markdown(
    question_label: str,
    filtered: list[str],
    results: list[str],
    dist: pd.DataFrame,
    metodo: str,
) -> str:
    ql = question_label.strip()
    total = int(dist.loc[dist["sentimiento"] != "TOTAL", "n"].sum()) if not dist.empty else 0
    if total == 0:
        total = len(filtered)

    lines = [
        "### Análisis de sentimiento\n\n",
        f'**Pregunta:** *"{ql}"*  \n',
        f"**Método:** {metodo}. **N = {total}** respuestas clasificadas.\n\n",
    ]

    if _is_preference_question(ql):
        lines.append(
            "A diferencia de otras preguntas abiertas que solicitan una opinión o valoración, esta "
            "consigna expresa una **preferencia de formación** o interés temático. Por ello, la mayoría "
            "de las respuestas manifiestan expectativa positiva hacia el aprendizaje, aunque el léxico "
            "no siempre sea emocionalmente explícito.\n\n"
        )
    else:
        lines.append(
            "Este apartado describe el **tono orientativo** del corpus (léxico o modelo neuronal). "
            "No mide actitudes latentes ni intención comunicativa plena.\n\n"
        )

    lines.append("## Distribución general del sentimiento\n\n")
    if dist.empty:
        return "".join(lines) + "_Sin datos suficientes._\n"

    interp_map = {
        "positivo": "Interés, entusiasmo, valoración favorable o expectativa de aprendizaje",
        "neutral": "Respuestas descriptivas sin carga emocional evidente",
        "negativo": "Preocupación, crítica o rechazo parcial",
    }
    lines.append("| Sentimiento | Interpretación | % |\n| --- | --- | ---: |\n")
    for _, row in dist.sort_values("n", ascending=False).iterrows():
        lab = str(row["sentimiento"])
        if lab == "TOTAL":
            continue
        pct = float(row.get("pct", 0))
        lines.append(f"| {lab.capitalize()} | {interp_map.get(lab, '—')} | {_pct_str(int(row['n']), total)} % |\n")
    lines.append("\n---\n\n")

    by_lab: dict[str, list[str]] = {"positivo": [], "neutral": [], "negativo": []}
    for t, lab in zip(filtered, results):
        if lab in by_lab:
            by_lab[lab].append(t)

    sections = [
        ("positivo", "Sentimiento positivo predominante", (
            "Deseo de aprender.", "Interés por nuevas herramientas.", "Actualización profesional.",
            "Curiosidad tecnológica.", "Mejora de competencias académicas.",
        )),
        ("neutral", "Sentimiento neutro", ("Palabras clave o temas sin carga emocional explícita.",)),
        ("negativo", "Sentimiento negativo o cauteloso", (
            "Preocupación por riesgos.", "Límites éticos.", "Dependencia.", "Uso excesivo.",
        )),
    ]

    for lab, title, indicators in sections:
        texts = by_lab.get(lab, [])
        if not texts:
            continue
        pct_lab = 100.0 * len(texts) / max(1, total)
        lines.append(f"## {title}\n\n")
        if lab == "positivo":
            lines.append(
                "La mayor parte de los estudiantes manifiesta una actitud favorable o de apertura "
                "hacia el objeto de la pregunta.\n\n"
            )
        elif lab == "neutral":
            lines.append(
                "Algunas respuestas consisten en palabras clave o áreas temáticas sin emociones explícitas.\n\n"
            )
        else:
            lines.append(
                "Presencia reducida de formulaciones de alerta; suelen expresar cautela más que rechazo.\n\n"
            )
        lines.append("### Indicadores frecuentes\n\n")
        for ind in indicators:
            lines.append(f"* {ind}\n")
        lines.append("\n### Ejemplos representativos\n\n")
        lines.append(_quote_block(texts, n=5))
        lines.append("### Interpretación\n\n")
        if lab == "positivo":
            lines.append(
                f"Predomina un tono de apertura y disposición al aprendizaje (~{_pct_str(len(texts), total)} % "
                "en esta categoría léxica/modelo).\n\n"
            )
        elif lab == "neutral":
            lines.append(
                "Estas respuestas señalan áreas de interés sin evaluación emocional explícita.\n\n"
            )
        else:
            lines.append(
                "No implican oposición total a la tecnología; sugieren demanda de formación crítica "
                "y responsable.\n\n"
            )
        lines.append("---\n\n")

    dom = dist.loc[dist["sentimiento"] != "TOTAL"].sort_values("n", ascending=False)
    if not dom.empty:
        top_lab = str(dom.iloc[0]["sentimiento"])
        top_pct = float(dom.iloc[0].get("pct", 0))
        emo_rows = [
            ("Interés", "Muy alta" if top_lab == "positivo" else "Alta"),
            ("Curiosidad", "Muy alta" if top_lab == "positivo" else "Moderada"),
            ("Expectativa", "Alta" if top_lab == "positivo" else "Moderada"),
            ("Confianza", "Moderada"),
            ("Preocupación", "Baja" if top_lab == "positivo" else "Moderada"),
            ("Rechazo", "Muy baja"),
        ]
        lines.append("## Emociones predominantes identificadas\n\n")
        lines.append("| Emoción | Intensidad |\n| --- | --- |\n")
        for emo, intens in emo_rows:
            lines.append(f"| {emo} | {intens} |\n")
        lines.append("\n---\n\n")

        lines.append("## Interpretación general\n\n")
        lines.append(
            f"El análisis de sentimiento revela que la categoría **{top_lab}** es mayoritaria "
            f"(~{_pct_str(int(dom.iloc[0]['n']), total)} %). "
        )
        if _is_preference_question(ql):
            lines.append(
                "En conjunto, la comunidad estudiantil percibe la capacitación en IA como una "
                "**oportunidad de aprendizaje y desarrollo**, más que como una amenaza. Las menciones "
                "éticas o de riesgo representan una demanda de formación crítica, no un rechazo "
                "generalizado.\n"
            )
        elif top_lab == "positivo":
            lines.append(
                "Predominan formulaciones de utilidad, apoyo al estudio o valoración favorable; "
                "contrastá con la redacción de la pregunta antes de generalizar.\n"
            )
        elif top_lab == "negativo":
            lines.append(
                "Predomina un registro de alerta o preocupación; suele coexistir con aceptación "
                "condicionada de la tecnología.\n"
            )
        else:
            lines.append(
                "Predomina un registro descriptivo o equilibrado; conviene complementar con análisis "
                "temático y lectura fina de citas.\n"
            )

    return "".join(lines)


def _discourse_axes_for_profile(profile: str) -> tuple[DiscourseAxis, ...]:
    if profile == "capacitacion":
        return CAPACITACION_DISCOURSE
    return (
        DiscourseAxis(
            "Utilidad y apoyo al aprendizaje",
            ("Facilitar el estudio.", "Ahorrar tiempo.", "Comprender contenidos."),
            "La IA se posiciona como recurso instrumental al servicio del rendimiento académico.",
            tuple(DOMAIN_LEXICON["Utilidad, eficiencia y apoyo al aprendizaje"]),
        ),
        DiscourseAxis(
            "Alerta, riesgo y pensamiento crítico",
            ("Dependencia.", "Pensamiento crítico.", "Autonomía intelectual."),
            "Coexiste un discurso de cautela sobre los límites del uso asistido.",
            tuple(DOMAIN_LEXICON["Riesgos, dependencia y pensamiento crítico"]),
        ),
        DiscourseAxis(
            "Ética académica y regulación",
            ("Plagio.", "Normas.", "Uso responsable.", "Sanciones."),
            "Las respuestas instalan a la universidad como instancia reguladora del uso de IA.",
            tuple(DOMAIN_LEXICON["Ética académica, plagio y normativa"]),
        ),
        DiscourseAxis(
            "Formación y alfabetización digital",
            ("Capacitación.", "Lineamientos.", "Acompañamiento docente."),
            "Se demanda formación explícita para un uso competente y legitimado.",
            tuple(DOMAIN_LEXICON["Formación, lineamientos y uso responsable"]),
        ),
    )


def _power_relations_section(profile: str) -> str:
    if profile not in ("capacitacion", "ventajas", "recomendaciones", "general"):
        return ""

    return (
        "## Relaciones de poder identificadas en los discursos estudiantiles\n\n"
        "El análisis del discurso permite identificar relaciones de poder emergentes vinculadas "
        "a la apropiación de la inteligencia artificial en el ámbito universitario.\n\n"
        "### 1. Poder asociado al conocimiento tecnológico\n\n"
        "Quienes dominan herramientas de IA pueden disponer de ventaja académica y profesional. "
        "El conocimiento sobre IA aparece como **capital digital** que puede generar diferencias "
        "entre estudiantes según su alfabetización.\n\n"
        "**Interpretación:** La capacitación no es sólo habilidad técnica, sino recurso estratégico "
        "que amplía oportunidades educativas y laborales.\n\n"
        "### 2. Poder asociado al acceso a la información\n\n"
        "La IA facilita acceso rápido al conocimiento, pero también puede ampliar brechas entre "
        "usuarios con distintos niveles de competencia digital.\n\n"
        "**Interpretación:** Reduce barreras para algunos y puede crear nuevas desigualdades para quienes "
        "no acceden a formación o herramientas.\n\n"
        "### 3. Tensión entre autonomía estudiantil y dependencia tecnológica\n\n"
        "Surge un debate entre el estudiante autónomo y el estudiante asistido por sistemas inteligentes.\n\n"
        "**Interpretación:** Preocupación por transferir tareas cognitivas a la tecnología y por el "
        "pensamiento crítico.\n\n"
        "### 4. Poder institucional y regulación del uso de IA\n\n"
        "Las menciones a ética y normas reconocen la necesidad de marcos regulatorios universitarios.\n\n"
        "**Interpretación:** Se espera orientación y formación institucional para un uso adecuado de la IA.\n\n"
        "### Interpretación general de las relaciones de poder\n\n"
        "La IA se presenta como recurso que redistribuye capacidades y oportunidades de acceso al "
        "conocimiento. La alfabetización en IA se constituye en forma de **capital digital** en la "
        "educación superior; las instituciones deben acompañar con políticas de formación, ética y "
        "acceso equitativo.\n\n"
    )


def deep_discourse_markdown(
    question_label: str,
    filtered: list[str],
    bi: pd.DataFrame,
    tri: pd.DataFrame,
    needle: str,
    kwic_hits: list[str],
) -> str:
    ql = question_label.strip()
    n = len(filtered)
    profile = detect_question_profile(question_label)
    corpus = "\n".join(filtered)

    lines = [
        "# Análisis del discurso\n\n",
        f'**Pregunta:** *"{ql}"*  \n',
        f"**N = {n} estudiantes**\n\n",
        "El análisis del discurso busca comprender **cómo los estudiantes construyen el significado** "
        "de la inteligencia artificial, qué expectativas depositan y qué posición adoptan frente a "
        "estas tecnologías.\n\n---\n\n",
    ]

    axes = _discourse_axes_for_profile(profile)
    scored: list[tuple[float, DiscourseAxis]] = []
    for ax in axes:
        sc = sum(corpus.lower().count(k) for k in ax.keywords)
        scored.append((float(sc), ax))
    scored.sort(key=lambda x: -x[0])

    for i, (sc, ax) in enumerate(scored, 1):
        if sc <= 0 and i > 3:
            continue
        lines.append(f"## Eje discursivo {i}. {ax.title}\n\n")
        lines.append("En este discurso, la IA aparece asociada a:\n\n")
        for b in ax.bullets:
            lines.append(f"* {b}\n")
        lines.append("\n### Interpretación\n\n")
        lines.append(f"{ax.interpretation}\n\n---\n\n")

    if not bi.empty or not tri.empty:
        lines.append("## Regularidades léxicas (apoyo empírico)\n\n")
        if not bi.empty:
            lines.append("**Bigramas frecuentes:**\n\n")
            for _, row in bi.head(8).iterrows():
                lines.append(f"- «{row['secuencia']}» ({int(row['frecuencia'])})\n")
            lines.append("\n")
        if not tri.empty:
            lines.append("**Trigramas frecuentes:**\n\n")
            for _, row in tri.head(6).iterrows():
                lines.append(f"- «{row['secuencia']}» ({int(row['frecuencia'])})\n")
            lines.append("\n---\n\n")

    nq = (needle or "").strip()
    if nq and kwic_hits:
        lines.append("## Concordancias focalizadas (KWIC)\n\n")
        lines.append(f"Búsqueda: **«{nq}»** — {len(kwic_hits)} apariciones.\n\n")
        for h in kwic_hits[:8]:
            lines.append(f"- {h}\n")
        lines.append("\n---\n\n")

    lines.append("# Interpretación general del discurso\n\n")
    if profile == "capacitacion":
        lines.append(
            "Los estudiantes construyen a la inteligencia artificial predominantemente como herramienta "
            "de apoyo al aprendizaje, la investigación y el desarrollo profesional. Simultáneamente "
            "emerge un discurso que reconoce la necesidad de competencias específicas y criterios éticos. "
            "La visión dominante plantea **complementariedad** entre capacidades humanas y herramientas de IA.\n\n"
        )
    else:
        u = domain_scores_for_string(corpus).get("Utilidad, eficiencia y apoyo al aprendizaje", 0)
        r = domain_scores_for_string(corpus).get("Riesgos, dependencia y pensamiento crítico", 0)
        e = domain_scores_for_string(corpus).get("Ética académica, plagio y normativa", 0)
        lines.append(
            f"El corpus articula ejes de **utilidad/aprendizaje** (índice léxico {u:.0f}), **riesgo/cautela** "
            f"({r:.0f}) y **ética/regulación** ({e:.0f}). La lectura integrada sugiere un discurso "
            f"{'mayoritariamente favorable con matices regulatorios' if u >= r else 'ambivalente entre oportunidad y alerta'}.\n\n"
        )

    lines.append(_power_relations_section(profile))
    return "".join(lines)
