"""Narrativa automática del informe ejecutivo (sin tablas), estilo Observatorio UCCuyo."""
from __future__ import annotations

import re
from typing import Any

import pandas as pd

from report_common import classify_chapter, display_label, top_category
from survey_intel import ColumnProfile, classify_columns, frequency_table


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def _find_col(profiles: list[ColumnProfile], *needles: str) -> ColumnProfile | None:
    for p in profiles:
        n = _norm(p.name)
        if all(k in n for k in needles):
            return p
    return None


def _ft(df: pd.DataFrame, col: str) -> pd.DataFrame | None:
    try:
        return frequency_table(df[col])
    except Exception:  # noqa: BLE001
        return None


def _pct_matching(ft: pd.DataFrame, *keys: str) -> float:
    if ft is None or ft.empty:
        return 0.0
    body = ft[ft["categoría"].astype(str).str.upper() != "TOTAL"] if "categoría" in ft.columns else ft
    total = 0.0
    for _, row in body.iterrows():
        cat = _norm(row.get("categoría", ""))
        if any(k in cat for k in keys):
            total += float(row.get("porcentaje", 0) or 0)
    return round(total, 2)


def _pct_top(ft: pd.DataFrame) -> tuple[str, float, int]:
    return top_category(ft) if ft is not None and not ft.empty else ("", 0.0, 0)


def _agree_pct(ft: pd.DataFrame) -> float:
    return _pct_matching(ft, "totalmente de acuerdo", "de acuerdo")


def _use_recurrent_pct(ft: pd.DataFrame) -> float:
    """Frecuente / siempre / a menudo / 1–3 veces por semana / cuatro o más."""
    return _pct_matching(
        ft,
        "siempre",
        "frecuentemente",
        "a menudo",
        "casi siempre",
        "cuatro o más",
        "1 y 3 veces por semana",
        "1–3 veces por semana",
        "entre 1 y 3 veces por semana",
    )


def extract_metrics(df: pd.DataFrame) -> dict[str, Any]:
    profiles = classify_columns(df)
    n = len(df)
    m: dict[str, Any] = {"n": n, "profiles": profiles}

    know = _find_col(profiles, "conocés o usaste") or _find_col(profiles, "conoces o usaste")
    freq = _find_col(profiles, "frecuencia utiliz")
    where = _find_col(profiles, "dónde conociste") or _find_col(profiles, "donde conociste")
    norma = _find_col(profiles, "normativa")
    advert = _find_col(profiles, "advert")
    falta = _find_col(profiles, "trabajos completos") or _find_col(profiles, "debería considerarse")
    capa = _find_col(profiles, "capacitaciones") or _find_col(profiles, "espacios formativos")
    mas_form = _find_col(profiles, "más formación") or _find_col(profiles, "mas formacion") or _find_col(
        profiles, "gustaría tener más formación"
    )

    if know:
        ft = _ft(df, know.name)
        m["adopcion_pct"] = _pct_matching(ft, "sí", "si")
        m["adopcion_top"] = _pct_top(ft)
    if freq:
        ft = _ft(df, freq.name)
        m["freq_ft"] = ft
        m["freq_alguna"] = 100.0 - _pct_matching(ft, "nunca")
        m["freq_frecuente"] = _pct_matching(ft, "frecuentemente", "a menudo")
        m["freq_siempre"] = _pct_matching(ft, "siempre")
        m["freq_nunca"] = _pct_matching(ft, "nunca")
        m["freq_top"] = _pct_top(ft)
    if where:
        ft = _ft(df, where.name)
        m["entrada_redes"] = _pct_matching(ft, "redes")
        m["entrada_pares"] = _pct_matching(ft, "compañ", "pares", "amigo")
        m["entrada_docente"] = _pct_matching(ft, "docente", "clase", "profesor")
        m["entrada_top"] = _pct_top(ft)

    # Usos grid
    usos = [p for p in profiles if classify_chapter(p) == "usos"]
    uso_stats = []
    for p in usos:
        ft = _ft(df, p.name)
        if ft is None:
            continue
        lab = display_label(p.name)
        rec = _use_recurrent_pct(ft)
        never = _pct_matching(ft, "nunca")
        always = _pct_matching(ft, "siempre")
        uso_stats.append({"label": lab, "recurrent": rec, "nunca": never, "siempre": always, "ft": ft})
    uso_stats.sort(key=lambda x: -x["recurrent"])
    m["usos"] = uso_stats

    # Likert / actitudes
    acts = [p for p in profiles if classify_chapter(p) == "actitudes"]
    act_stats = []
    for p in acts:
        ft = _ft(df, p.name)
        if ft is None:
            continue
        lab = display_label(p.name)
        act_stats.append({"label": lab, "agree": _agree_pct(ft), "ft": ft, "top": _pct_top(ft)})
    m["actitudes"] = act_stats

    # Open advantages / risks for benefits section
    opens = [p for p in profiles if p.kind == "abierta"]
    m["open_cols"] = opens

    if norma:
        ft = _ft(df, norma.name)
        m["norma_si"] = _pct_matching(ft, "sí", "si")
        m["norma_no"] = _pct_matching(ft, "no", "no sé", "no se", "desconoz")
        # counts
        body = ft[ft["categoría"].astype(str).str.upper() != "TOTAL"] if ft is not None else None
        if body is not None and "frecuencia" in body.columns:
            m["norma_counts"] = {
                str(r["categoría"]): int(r["frecuencia"]) for _, r in body.iterrows()
            }
    if advert:
        ft = _ft(df, advert.name)
        m["advert_si"] = _pct_matching(ft, "sí", "si")
        m["advert_no"] = _pct_matching(ft, "no")
    if falta:
        ft = _ft(df, falta.name)
        m["falta_si"] = _pct_matching(ft, "sí", "si")
        m["falta_talvez"] = _pct_matching(ft, "tal vez", "quizá", "quiza", "depende")
        m["falta_no"] = _pct_matching(ft, "no")
    if capa:
        ft = _ft(df, capa.name)
        m["capa_no"] = _pct_matching(ft, "no")
        m["capa_si"] = 100.0 - m["capa_no"] if m.get("capa_no") is not None else _pct_matching(ft, "sí", "si")
    if mas_form:
        ft = _ft(df, mas_form.name)
        m["form_si"] = _pct_matching(ft, "sí", "si")
        m["form_quiza"] = _pct_matching(ft, "quizá", "quiza", "tal vez", "depende")
        m["form_no"] = _pct_matching(ft, "no")

    # critical thinking concern from likert
    for a in act_stats:
        lab = _norm(a["label"])
        if "pensamiento crítico" in lab or "reemplace" in lab:
            m["riesgo_critico_agree"] = a["agree"]
            break

    return m


def _fmt(pct: float | None) -> str:
    if pct is None:
        return "—"
    # spanish decimal comma
    s = f"{pct:.2f}".rstrip("0").rstrip(".")
    return s.replace(".", ",")


def build_executive_sections(df: pd.DataFrame, audience: str = "estudiantes") -> dict[str, list[str]]:
    """Devuelve secciones 1–8 como listas de párrafos (sin tablas)."""
    m = extract_metrics(df)
    n = m["n"]
    out: dict[str, list[str]] = {}

    adop = m.get("adopcion_pct")
    freq_alguna = m.get("freq_alguna")
    freq_frec = m.get("freq_frecuente")
    freq_siemp = m.get("freq_siempre")
    freq_nunca = m.get("freq_nunca")

    out["1. Propósito del informe"] = [
        (
            f"El presente informe ejecutivo sintetiza los principales hallazgos del estudio institucional "
            f"sobre el uso de herramientas de inteligencia artificial (IA) por parte de {audience} de la "
            f"Universidad Católica de Cuyo. Su finalidad es ofrecer a la comunidad educativa de la Universidad "
            f"una lectura clara, estratégica y orientada a la toma de decisiones, a partir de evidencia "
            f"relevada en una encuesta aplicada a {n} {audience} de distintas carreras, unidades académicas y sedes."
        ),
        (
            "El diagnóstico confirma que la IA ya forma parte de la vida académica cotidiana. "
            "No se trata de una tendencia emergente ni de una práctica marginal, sino de un fenómeno "
            "extendido, transversal y consolidado. Esta realidad obliga a la Universidad a pasar de una "
            "lógica de observación o reacción aislada a una política institucional explícita, coherente y formativa."
        ),
        (
            "La información analizada permite concluir que la IA ofrece oportunidades concretas para "
            "fortalecer procesos de aprendizaje, mejorar la comprensión de contenidos y optimizar tiempos "
            "de estudio. Sin embargo, también plantea desafíos significativos en materia de pensamiento "
            "crítico, autonomía intelectual, integridad académica, formación docente, criterios de evaluación "
            "y comunicación normativa."
        ),
        (
            "En este contexto, el desafío institucional ya no consiste en debatir si la inteligencia artificial "
            "debe estar o no presente en la universidad. La cuestión central es cómo gobernar pedagógica, ética "
            "y académicamente un fenómeno que ya está instalado en las prácticas de estudio y que seguirá "
            "profundizándose en el corto plazo."
        ),
    ]

    hallazgos: list[str] = []
    if adop is not None:
        hallazgos.append(
            f"El primer dato de relevancia institucional es el nivel de adopción de estas tecnologías. "
            f"El {_fmt(adop)} % de los {audience} manifestó conocer o haber utilizado alguna herramienta "
            f"de inteligencia artificial."
            + (
                f" A su vez, el {_fmt(freq_alguna)} % declaró utilizarla con algún nivel de frecuencia en "
                f"actividades académicas."
                if freq_alguna is not None
                else ""
            )
            + " Esto indica una incorporación prácticamente universal, con presencia en el conjunto de perfiles relevados."
        )
    if freq_frec is not None or freq_siemp is not None:
        hallazgos.append(
            f"El estudio muestra además que el uso de la IA no es ocasional. "
            f"El {_fmt(freq_frec or 0)} % indicó utilizarla frecuentemente y un {_fmt(freq_siemp or 0)} % "
            f"afirmó usarla siempre"
            + (f", mientras que sólo un {_fmt(freq_nunca)} % señaló no emplearla nunca" if freq_nunca is not None else "")
            + ". Estos valores demuestran que la IA ya se integró a las rutinas ordinarias de estudio, "
            "búsqueda de información, apoyo conceptual y organización del trabajo universitario."
        )

    usos = m.get("usos") or []
    if usos:
        top5 = usos[:5]
        bullets = "; ".join(u["label"].rstrip(".") for u in top5)
        hallazgos.append(f"Entre los principales usos académicos se destacan: {bullets}.")
        best = usos[0]
        hallazgos.append(
            f"En particular, «{best['label']}» aparece entre los usos más extendidos: el {_fmt(best['recurrent'])} % "
            f"declara un uso recurrente o intensivo. "
        )
        # production writing sensitivity
        prod = next(
            (
                u
                for u in usos
                if any(k in _norm(u["label"]) for k in ("ensayo", "editar", "trabajos p", "textos académicos", "redaccion"))
            ),
            None,
        )
        if prod:
            hallazgos.append(
                f"Cuando el foco se desplaza a la producción escrita («{prod['label']}»), el panorama se vuelve "
                f"más sensible: el {_fmt(prod['recurrent'])} % declara uso recurrente, el {_fmt(prod['nunca'])} % "
                f"afirma no hacerlo nunca y el {_fmt(prod['siempre'])} % lo hace siempre. Este dato exige atención "
                f"institucional porque toca autoría, evaluación e integridad académica."
            )
    if m.get("entrada_redes") is not None:
        hallazgos.append(
            f"Otro hallazgo relevante es que la puerta de entrada a estas tecnologías no está siendo "
            f"principalmente la universidad. El {_fmt(m.get('entrada_redes'))} % conoció estas herramientas "
            f"a través de redes sociales y el {_fmt(m.get('entrada_pares'))} % por recomendación de pares. "
            f"En contraste, sólo el {_fmt(m.get('entrada_docente'))} % tuvo su primer acercamiento en clase "
            f"con docentes. La apropiación inicial se produce, en general, fuera de los circuitos formales "
            f"de enseñanza, lo que incrementa el riesgo de usos intuitivos o escasamente orientados."
        )
    out["2. Hallazgos principales del diagnóstico"] = hallazgos or [
        f"El relevamiento (N={n}) permite caracterizar patrones de adopción y uso de IA en la población encuestada."
    ]

    beneficios = [
        (
            "Desde la perspectiva de quienes respondieron, la inteligencia artificial es valorada mayormente "
            "como una herramienta de apoyo al aprendizaje. Los usos de mayor recurrencia se concentran en "
            "comprender contenidos, organizar materiales y acceder a información, más que en una lógica "
            "exclusiva de atajo para resolver consignas."
        )
    ]
    if usos:
        beneficios.append(
            "Los datos permiten interpretar que el estudiantado no percibe a la IA únicamente como un recurso "
            "para completar tareas, sino también como tutor informal, asistente de síntesis y facilitador de "
            "explicaciones. Ese rol cognitivo ya instalado exige orientación institucional para que mejore "
            "genuinamente el aprendizaje y no sustituya la elaboración propia."
        )
    beneficios.append(
        "En términos pedagógicos, la evidencia no sugiere prohibiciones generales ni respuestas defensivas. "
        "Lo que muestra es la necesidad de integrar la IA a marcos didácticos claros, capaces de distinguir "
        "entre usos valiosos para comprender, explorar, comparar, resumir o planificar, y usos problemáticos "
        "cuando reemplazan la producción intelectual, desdibujan la autoría o debilitan la reflexión crítica."
    )
    # qualitative hint if open advantage column exists
    for p in m.get("open_cols") or []:
        if any(k in _norm(p.name) for k in ("ventaja", "beneficio", "aport")):
            beneficios.insert(
                1,
                f"Las respuestas abiertas sobre «{display_label(p.name)}» refuerzan la lectura de la IA como "
                f"apoyo a la comprensión, la eficiencia y el acceso a información, con matices según carrera y trayectoria.",
            )
            break
    out["3. Beneficios percibidos y valor académico de la IA"] = beneficios

    riesgos = [
        (
            "Aunque la evaluación global suele ser favorable, el estudio detecta tensiones importantes que "
            "deben abordarse sin demora. La principal preocupación recurrente se vincula con la dependencia "
            "tecnológica y el posible debilitamiento del pensamiento crítico."
        )
    ]
    if m.get("riesgo_critico_agree") is not None:
        riesgos.append(
            f"De manera complementaria, el {_fmt(m['riesgo_critico_agree'])} % se manifestó de acuerdo o "
            f"totalmente de acuerdo con enunciados que asocian la IA al riesgo de reemplazar o debilitar el "
            f"pensamiento crítico. Esta distribución revela que no existe consenso pleno, pero sí una "
            f"preocupación significativa: se percibe al mismo tiempo el valor funcional de la IA y el riesgo "
            f"de usos no regulados sobre la autonomía intelectual."
        )
    riesgos.append(
        "La tensión pedagógica puede sintetizarse así: la IA asiste, agiliza y amplía posibilidades, pero "
        "también puede simplificar en exceso procesos que, en educación superior, deben seguir siendo "
        "complejos, argumentativos y formativos. Si se delega en la herramienta la búsqueda, la escritura, "
        "la síntesis y la interpretación, la ganancia operativa puede convertirse en pérdida formativa."
    )
    if m.get("falta_si") is not None:
        riesgos.append(
            f"También emergen desafíos de ética académica. El {_fmt(m.get('falta_si'))} % considera que usar IA "
            f"para realizar trabajos completos sin intervención propia constituye una falta, pero un "
            f"{_fmt(m.get('falta_talvez'))} % responde con ambigüedad («tal vez»/equivalentes) y un "
            f"{_fmt(m.get('falta_no'))} % no lo considera inapropiado. El problema no radica sólo en la "
            f"conducta individual, sino también en la ausencia de definiciones institucionales suficientemente "
            f"claras, homogéneas y visibles."
        )
    out["4. Riesgos, tensiones pedagógicas y desafíos institucionales"] = riesgos

    brechas = [
        (
            "Uno de los hallazgos más consistentes es la distancia entre la rápida adopción de la IA y la "
            "todavía insuficiente respuesta institucional en materia de formación, normativa y comunicación."
        )
    ]
    if m.get("norma_no") is not None or m.get("norma_counts"):
        counts = m.get("norma_counts") or {}
        neg = sum(v for k, v in counts.items() if any(x in _norm(k) for x in ("no", "desconoz")))
        pos = sum(v for k, v in counts.items() if _norm(k) in {"sí", "si"} or _norm(k).startswith("sí"))
        if neg or pos:
            brechas.append(
                f"La mayoría desconoce o niega la existencia de normativa visible sobre el uso de IA en su "
                f"unidad académica (aproximadamente {neg} respuestas en sentido negativo frente a {pos} "
                f"afirmativas). El nivel de visibilidad normativa es bajo y la comunicación institucional no "
                f"está llegando con claridad."
            )
        else:
            brechas.append(
                f"El {_fmt(m.get('norma_no'))} % indica desconocimiento o ausencia percibida de normativa "
                f"sobre IA, frente a un {_fmt(m.get('norma_si'))} % afirmativo."
            )
    if m.get("advert_si") is not None:
        brechas.append(
            f"Si bien el {_fmt(m.get('advert_si'))} % afirma haber recibido advertencias sobre el uso indebido "
            f"de estas herramientas, el {_fmt(m.get('advert_no'))} % no las ha recibido. Existen acciones de "
            f"sensibilización, pero con alcance desigual según docentes, cátedras o carreras."
        )
    if m.get("capa_no") is not None:
        brechas.append(
            f"La brecha formativa es evidente: el {_fmt(m.get('capa_no'))} % no participó en instancias de "
            f"capacitación sobre inteligencia artificial durante su trayectoria académica."
        )
    if m.get("form_si") is not None:
        brechas.append(
            f"La receptividad hacia más formación es alta: el {_fmt(m.get('form_si'))} % desea explícitamente "
            f"incorporar más capacitación en IA y un {_fmt(m.get('form_quiza'))} % responde con apertura "
            f"condicional. La Universidad cuenta con legitimidad, necesidad objetiva y predisposición para "
            f"intervenir de manera orgánica."
        )
    out["5. Brechas institucionales: formación, normativa y comunicación"] = brechas

    out["6. Implicancias estratégicas para la Universidad"] = [
        (
            "La evidencia relevada permite afirmar que la incorporación de la inteligencia artificial no puede "
            "tratarse como un asunto exclusivamente tecnológico. Se trata de una cuestión académica, pedagógica, "
            "ética e institucional: alcanza la enseñanza, el aprendizaje, la evaluación, la producción de "
            "conocimiento, la formación profesional y la cultura universitaria."
        ),
        (
            "Por ello, la respuesta institucional debe superar las medidas aisladas y avanzar hacia una estrategia "
            "integral con conducción política clara. Esa estrategia debería sostener al menos cinco criterios "
            "rectores: (1) reconocer el carácter irreversible del fenómeno; (2) colocar el aprendizaje en el centro; "
            "(3) diferenciar asistencia legítima y sustitución indebida; (4) fortalecer la alfabetización digital "
            "crítica; y (5) asegurar coherencia institucional entre unidades académicas y sedes."
        ),
        (
            "Las políticas sobre IA deben ser comprensibles, visibles y aplicables, evitando respuestas "
            "fragmentadas que generen inequidad entre carreras, asignaturas y sedes. La cuestión no es si se "
            "usa IA, sino para qué se usa, bajo qué condiciones y con qué efectos sobre la comprensión, el "
            "razonamiento y la producción propia."
        ),
    ]

    out["7. Recomendaciones para la toma de decisiones"] = [
        "En función de los resultados, se recomienda una agenda institucional de corto y mediano plazo con estos ejes:",
        "1. Definir una política universitaria marco sobre inteligencia artificial, con criterios comunes de usos permitidos, declaración, integridad académica, evaluación y responsabilidad docente.",
        "2. Diseñar un programa transversal de alfabetización en IA para estudiantes: uso crítico, validación de fuentes, sesgos, citación, ética y aprovechamiento pedagógico.",
        "3. Fortalecer la capacitación docente sobre rediseño de consignas, evaluación auténtica, detección de usos problemáticos y didáctica de la IA.",
        "4. Revisar criterios de evaluación y producción académica priorizando argumentación, oralidad, procesos, trazabilidad y aplicación situada del conocimiento.",
        "5. Mejorar la comunicación normativa para que cada estudiante conozca con claridad qué espera su unidad académica respecto del uso de IA.",
        "6. Impulsar pilotos por facultad con seguimiento institucional, para identificar buenas prácticas y aprendizajes transferibles.",
        "7. Consolidar un sistema de monitoreo permanente, repitiendo el relevamiento y construyendo indicadores de evolución de usos, percepciones y efectos pedagógicos.",
    ]

    out["8. Consideraciones finales"] = [
        (
            f"La Universidad Católica de Cuyo se encuentra ante una coyuntura decisiva. La inteligencia artificial "
            f"ya no es una innovación periférica, sino una dimensión constitutiva del ecosistema académico "
            f"contemporáneo. El relevamiento (N={n}) muestra una población que usa intensamente estas herramientas, "
            f"reconoce beneficios y, al mismo tiempo, advierte riesgos vinculados con la autonomía, el pensamiento "
            f"crítico y la ética."
        ),
        (
            "Este escenario no debe interpretarse en clave alarmista ni celebratoria, sino institucional. La IA abre "
            "oportunidades reales para enriquecer los procesos formativos, pero sólo podrá hacerlo de manera "
            "consistente si la Universidad asume un rol activo en su orientación. La ausencia de política explícita "
            "no produce neutralidad; produce dispersión, ambigüedad y desigualdad de criterios."
        ),
        (
            "Por ello, el momento actual exige conducción académica, capacidad de articulación entre Rectorado, "
            "Consejo Superior y unidades académicas, y decisión para construir un marco universitario común. Formar "
            "profesionales capaces de interactuar críticamente con la inteligencia artificial será, cada vez más, "
            "una condición de calidad educativa, responsabilidad institucional y pertinencia social."
        ),
        (
            "La evidencia disponible permite sostener una conclusión central: la Universidad no necesita optar entre "
            "innovación y formación humanista. Su desafío es integrar ambas dimensiones en un proyecto educativo que "
            "aproveche el potencial de la inteligencia artificial sin renunciar al pensamiento crítico, la autoría, "
            "la ética y la centralidad del conocimiento universitario."
        ),
    ]
    return out


def _executive_section_for_cross(cr: dict[str, Any], profiles_by_col: dict[str, ColumnProfile]) -> str:
    """Elige el apartado temático del ejecutivo donde integrar la lectura bivariada."""
    chapters: list[str] = []
    for col in (cr.get("row_column"), cr.get("col_column")):
        p = profiles_by_col.get(col) if col else None
        if p is not None:
            chapters.append(classify_chapter(p))
    chs = set(chapters)
    blob = _norm(f"{cr.get('row_label', '')} {cr.get('col_label', '')}")

    if "institucional" in chs:
        return "5. Brechas institucionales: formación, normativa y comunicación"
    if "actitudes" in chs:
        if any(k in blob for k in ("riesgo", "preocup", "dependen", "crítico", "critico", "falta", "integridad")):
            return "4. Riesgos, tensiones pedagógicas y desafíos institucionales"
        return "3. Beneficios percibidos y valor académico de la IA"
    # sociodemográfico × adopción/usos, o usos/adopción solos → hallazgos
    return "2. Hallazgos principales del diagnóstico"


def weave_crosses_into_executive_sections(
    sections: dict[str, list[str]],
    crosses: list[dict[str, Any]] | None,
    profiles: list[ColumnProfile] | None = None,
) -> dict[str, list[str]]:
    """
    Incorpora las lecturas bivariadas elegidas dentro de la narrativa de cada apartado
    (sin capítulo aparte ni la palabra «cruce»).
    """
    if not crosses:
        return sections

    from report_common import narrative_for_crosstab

    profiles_by_col = {p.name: p for p in (profiles or [])}
    # Copiar para no mutar el dict original inesperadamente
    out = {k: list(v) for k, v in sections.items()}

    by_section: dict[str, list[dict[str, Any]]] = {}
    for cr in crosses:
        key = _executive_section_for_cross(cr, profiles_by_col)
        if key not in out:
            key = "2. Hallazgos principales del diagnóstico"
        by_section.setdefault(key, []).append(cr)

    for key, crs in by_section.items():
        paras = out.setdefault(key, [])
        if len(crs) == 1:
            paras.append(narrative_for_crosstab(crs[0], executive=True))
        else:
            paras.append(
                "Complementando la lectura univariada, el análisis conjunto de variables "
                "seleccionadas aporta matices relevantes para la conducción académica:"
            )
            for cr in crs:
                paras.append(narrative_for_crosstab(cr, executive=True))
    return out
