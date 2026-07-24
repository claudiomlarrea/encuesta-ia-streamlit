#!/usr/bin/env python3
"""Genera Excel de prueba con 20 respuestas ficticias del cuestionario docentes IA UCCuyo."""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

FREQ = [
    "Nunca",
    "Menos de una vez por mes",
    "Entre 1 y 3 veces por mes",
    "Entre 1 y 3 veces por semana",
    "Cuatro o más veces por semana",
]

LIKERT = [
    "Totalmente en desacuerdo",
    "En desacuerdo",
    "Ni de acuerdo ni en desacuerdo",
    "De acuerdo",
    "Totalmente de acuerdo",
]

UA = [
    "FBOSCO- Facultad Don Bosco de Enología y Ciencias de la Alimentación - Sede Rodeo del Medio",
    "FCEESJ- Facultad de Ciencias Económicas y Empresariales Sede San Juan",
    "FCEESL- Facultad de Ciencias Económicas y Empresariales Sede San Luis",
    "FEDSJ- Facultad de Educación San Juan",
    "FFyHSJ- Facultad de Filosofía y Humanidades",
    "FDCSSJ- Facultad de Derecho y Ciencias Sociales Sede San Juan",
    "FDCSSL- Facultad de Derecho y Ciencias Sociales Sede San Luis",
    "FCMSJ- Facultad de Ciencias Médicas San Juan",
    "FCMSL- Facultad de Ciencias Médicas Sede San Luis",
    "FCQyTSJ- Facultad de Ciencias Químicas y Tecnológicas San Juan",
    "FCVSL- Facultad de Ciencias Veterinarias Sede San Luis",
    "ISB - Instituto San Buenaventura",
    "ESEGSJ- Escuela de Seguridad",
    "ISDSM- Instituto Universitario Santa María",
    "ECRyPSJ- Escuela de Cultura Religiosa y Pastoral",
]

SEDE = ["San Juan", "San Luis", "Mendoza / Rodeo del Medio", "Otra / virtual multisede"]
CATEGORIA = [
    "Titular",
    "Asociado/a",
    "Adjunto/a",
    "Jefe/a de trabajos prácticos",
    "Ayudante / auxiliar",
    "Invitado/a / contrato",
    "Autoridad académica (además de docencia)",
]
ANTIG = [
    "Menos de 2 años",
    "Entre 2 y 5 años",
    "Entre 6 y 10 años",
    "Entre 11 y 20 años",
    "Más de 20 años",
]
EDAD = [
    "menos de 30 años",
    "entre 30 y 40 años",
    "entre 41 y 50 años",
    "entre 51 y 60 años",
    "más de 60 años",
    "Prefiero no decirlo",
]
GENERO = ["Femenino", "Masculino", "Prefiero no decirlo", "Otro"]
SI_NO = ["Sí", "No"]
HERRAMIENTAS = [
    "ChatGPT",
    "Gemini",
    "Copilot",
    "NotebookLM",
    "DeepSeek",
    "Grammarly",
    "DALL·E / generadores de imagen",
    "Eduaide.AI",
    "MagicSchool AI",
    "Otras",
]
DONDE = [
    "En redes sociales",
    "Por recomendación de colegas o pares",
    "En medios de comunicación tradicionales",
    "En capacitaciones institucionales / UCCuyo",
    "En clase / con estudiantes (ellos me mostraron)",
    "Por iniciativa propia / exploración",
    "Otros",
]
USOS = [
    "Diseñar presentaciones o materiales para clase",
    "Buscar o elaborar explicaciones de conceptos teóricos para enseñar",
    "Preparar resúmenes, guías o fichas de estudio para estudiantes",
    "Generar o editar consignas, enunciados o textos académicos de cátedra",
    "Traducir textos académicos o materiales de lectura",
    "Corregir ortografía o gramática de materiales propios",
    "Formular preguntas de práctica, repaso o examen",
    "Analizar bases de datos, resultados numéricos o evidencias de aprendizaje",
    "Obtener ideas para actividades, trabajos prácticos o proyectos",
    "Simular casos, role-play o situaciones profesionales para clase",
    "Mejorar redacciones de informes, dictámenes o documentos institucionales",
    "Crear esquemas o mapas conceptuales para enseñar",
    "Consultar ejemplos de modelos, fórmulas o casos disciplinares",
    "Buscar información actualizada de fuentes confiables",
    "Resolver o chequear ejercicios o problemas para preparar clases o correcciones",
    "Rediseñar consignas de evaluación para reducir usos indebidos de IA",
    "Detectar o sospechar usos problemáticos de IA en entregas de estudiantes",
    "Explicar en clase criterios de uso responsable y ético de la IA",
    "Utilizar IA para brindar retroalimentación formativa a los estudiantes",
]
ACTITUDES = [
    "El uso de IA puede mejorar el aprendizaje de mis estudiantes.",
    "La IA me ayuda a enseñar o preparar clases de manera más eficiente.",
    "Usar IA me permite ahorrar tiempo en tareas docentes.",
    "A veces uso IA sin validar del todo el contenido que me brinda.",
    "Me gustaría que la Universidad ofrezca formación docente sobre uso académico de IA.",
    "Usar IA me motiva a innovar en mis prácticas de enseñanza.",
    "Considero que el uso de IA puede generar dependencia si no se regula.",
    "Sé distinguir cuándo está bien usar IA y cuándo no, en mi práctica docente.",
    "Me resulta difícil saber si lo que genera la IA es correcto o confiable.",
    "Me preocupa que la IA debilite el pensamiento crítico de los estudiantes.",
    "Me preocupa que la IA debilite mi propio juicio profesional docente.",
    "Puedo detectar con razonable confianza cuando un trabajo fue generado mayormente con IA.",
    "Mis criterios de evaluación ya contemplan explícitamente el uso de IA.",
    "La inteligencia artificial es una tecnología que seguirá expandiéndose en el ámbito educativo.",
    "Considero que no incorporar el uso de IA en mi práctica docente puede representar una desventaja profesional.",
    "El uso de IA debería formar parte de la formación obligatoria de los futuros profesionales.",
    "Creo que aprender sobre IA mejora mis oportunidades académicas o laborales.",
    "Puedo desarrollar mis asignaturas sin necesidad de incorporar IA.",
]
NORMATIVA = ["Sí", "No", "No estoy seguro/a"]
ADVERT = [
    "Sí, de manera sistemática (en consignas / programa / clase)",
    "Sí, de manera ocasional",
    "No todavía",
    "No lo considero necesario",
]
FALTA = ["Sí", "Tal vez", "No"]
DECLARACION = [
    "Sí, siempre que se use",
    "A veces, según la actividad",
    "No",
    "Aún no defino un criterio",
]
POSTURA = [
    "Prohibición general",
    "Permitido con condiciones y declaración",
    "Permitido como apoyo, sin declaración formal",
    "Sin criterio unificado todavía",
    "Depende de cada actividad / evaluación",
]
CAPA = ["Sí", "Sí, pero no cubrió mis expectativas", "No", "No, pero me gustaría ser capacitado/a"]
MAS_FORM = ["Sí", "Tal vez", "No"]
TEMAS = [
    "IA para la Investigación Académica",
    "Automatización de Tareas y Productividad",
    "Análisis de Datos con IA",
    "Prompt Engineering (Ingeniería de Prompts)",
    "Ética y Detección de Contenido IA",
    "IA Generativa Multimedia",
    "Rediseño de consignas y evaluación auténtica",
    "Integridad académica y declaración de uso de IA",
    "Didáctica de la IA en el aula",
    "Otro",
]

VENTAJAS = [
    "Me permite preparar materiales más rápido y diversificar ejemplos para distintas carreras.",
    "Ahorro de tiempo en la redacción de consignas y en la búsqueda de explicaciones alternativas.",
    "Sirve como apoyo para diseñar actividades situadas y actualizar bibliografía de manera ágil.",
    "Facilita la traducción de textos y la generación de esquemas previos a la clase.",
    "Ayuda a innovar en la enseñanza y a ofrecer retroalimentación más frecuente a los estudiantes.",
    "Es útil para simular casos profesionales y preparar instancias de práctica en el aula.",
    "Mejora la productividad en gestión académica y en la producción de guías de estudio.",
    "Permite chequear ideas y enriquecer la planificación didáctica sin reemplazar el criterio docente.",
    "Acelera la preparación de presentaciones y me deja más tiempo para acompañar a los estudiantes.",
    "Me ayuda a reformular contenidos complejos en versiones más claras para primer año.",
    "Puedo generar variantes de ejercicios y adaptar el nivel de dificultad con mayor rapidez.",
    "Es un recurso valioso para explorar enfoques didácticos nuevos en asignaturas numerosas.",
    "Reduce tiempos de búsqueda de ejemplos actualizados en mi disciplina.",
    "Complementa la planificación semanal y la organización de materiales del campus virtual.",
    "Me permite contrastar explicaciones y detectar lagunas antes de la clase.",
    "Facilita la elaboración de rúbricas iniciales que luego ajusto con el equipo de cátedra.",
    "Apoya la comunicación con estudiantes al redactar orientaciones más claras.",
    "Sirve para bosquejar itinerarios de aprendizaje y secuencias didácticas.",
    "Me ayuda a preparar materiales inclusivos con distintas vías de acceso al contenido.",
    "Como docente principiante acelera mi curva de aprendizaje en diseño de clases.",
]

RIESGOS = [
    "Me preocupa la pérdida de pensamiento crítico y la dependencia de respuestas automáticas.",
    "El riesgo mayor es la opacidad de autoría y la dificultad para evaluar aprendizajes genuinos.",
    "Sin lineamientos claros cada cátedra improvisa y se generan inequidades entre asignaturas.",
    "Temo la desinformación los sesgos algorítmicos y el uso de fuentes no verificadas.",
    "Puede debilitar la escritura académica y la argumentación si se usa sin mediación pedagógica.",
    "La detección de trabajos enteramente generados con IA sigue siendo incierta en la corrección.",
    "Sin formación docente se amplía la brecha entre quienes adoptan la herramienta y quienes la evitan.",
    "Existe un riesgo ético de plagio encubierto y de banalización de la evaluación universitaria.",
    "Me inquieta que los estudiantes prioricen velocidad por sobre comprensión profunda.",
    "Puede erosionar la autoría intelectual si no hay criterios compartidos de declaración de uso.",
    "La heterogeneidad de criterios entre docentes genera confusión y conflictividad en las aulas.",
    "Riesgo de sobreconfianza en salidas incorrectas o superficialmente persuasivas.",
    "Preocupa la desigualdad de acceso a herramientas pagos entre estudiantes de distintas sedes.",
    "Sin acompañamiento la IA puede sustituir procesos formativos centrales de la carrera.",
    "La presión por 'estar al día' puede llevar a usos acríticos también entre docentes.",
    "Me preocupa la privatización del conocimiento y la dependencia de plataformas externas.",
    "Hay tensión entre innovación y control de calidad académica en evaluaciones domiciliarias.",
    "El uso intensivo puede reducir el tiempo de lectura profunda de bibliografía obligatoria.",
    "Riesgo reputacional institucional si no hay respuesta normativa visible y coherente.",
    "Temo que se debilite el juicio profesional docente al delegar tareas de diseño y corrección.",
]

RECOM = [
    "Definir una política institucional clara con declaración de uso y criterios de evaluación auténtica.",
    "Capacitar a docentes y estudiantes en prompt crítico verificación de fuentes e integridad académica.",
    "Rediseñar consignas orales procesuales y situadas evitando entregas únicamente textuales domiciliarias.",
    "Exigir transparencia del uso de IA y enseñar citación o declaración en cada materia.",
    "Crear lineamientos comunes por unidad académica y espacios de intercambio de buenas prácticas.",
    "Priorizar formación ética y didáctica antes que herramientas aisladas o detectores mágicos.",
    "Monitorear periódicamente usos y percepciones y ajustar la normativa con evidencia empírica.",
    "Permitir usos de apoyo (explicar resumir planificar) y restringir la sustitución de la producción propia.",
    "Incorporar en los programas de asignatura un apartado explícito sobre usos permitidos y prohibidos.",
    "Promover evaluación auténtica con defensa oral portafolios y evidencias de proceso.",
    "Ofrecer microcertificaciones docentes en alfabetización crítica de IA.",
    "Acompañar a las cátedras con ejemplos de consignas rediseñadas por disciplina.",
    "Comunicar de forma visible la normativa en campus virtual y en la primera clase.",
    "Construir rúbricas que valoren argumentación fuentes y revisión crítica del output de IA.",
    "Crear un observatorio interno de incidentes y consultas sobre integridad académica.",
    "Articular Rectorado unidades académicas y biblioteca en una estrategia formativa común.",
    "Enseñar a contrastar salidas de distintos modelos y a documentar el proceso de validación.",
    "Evitar prohibiciones absolutas sin alternativa pedagógica; preferir gobernanza formativa.",
    "Incluir a estudiantes en el diseño de lineamientos para aumentar legitimidad y cumplimiento.",
    "Publicar guías breves por facultad con ejemplos de usos legítimos e ilegítimos.",
]

BUENAS = [
    "Pedí a los estudiantes que declaren el uso de IA y que entreguen un anexo de prompts y revisión crítica.",
    "Usé ChatGPT para generar borradores de casos clínicos y luego los validé con el equipo de cátedra.",
    "Rediseñé el parcial con defensa oral breve para contrastar comprensión frente a textos asistidos por IA.",
    "En clase comparamos salidas de distintos modelos y trabajamos sesgos y errores factuales.",
    "Elaboré rúbricas que puntúan argumentación fuentes y proceso no solo el producto final.",
    "",
    "Armé guías de estudio con IA y las corregí con bibliografía de la materia antes de publicarlas.",
    "",
    "Diseñé un taller de 30 minutos sobre integridad académica y uso declarado de IA al inicio del cuatrimestre.",
    "Pedí un diario de proceso donde el estudiante explica qué hizo la IA y qué corrigió él o ella.",
    "Usé NotebookLM para organizar lecturas y luego construí preguntas de comprensión en clase.",
    "",
    "Generé variantes de un mismo caso y asigné versiones distintas para desalentar copias literales.",
    "Implementé coevaluación entre pares sobre la calidad de la revisión crítica del material asistido.",
    "",
    "Preparé un checklist de verificación factual obligatorio antes de aceptar entregas con apoyo de IA.",
    "En TP integrador exigí fuentes primarias y una sección de limitaciones del uso de IA.",
    "",
    "Organicé una clase invertida donde los estudiantes critican un texto generado y proponen mejoras.",
    "Documenté en el programa la política de la cátedra y la comenté en la primera reunión.",
]

GRID_USOS_PREFIX = (
    "A continuación, se presentan diferentes usos posibles de herramientas de inteligencia artificial "
    "en la práctica docente. Indicá con qué frecuencia realizás cada uno de ellos.\n [{}]"
)
GRID_LIKERT_PREFIX = "Señalá tu nivel de acuerdo con las siguientes afirmaciones. [{}]"


def _choice(rng: random.Random, options: list[str], weights: list[float] | None = None) -> str:
    if weights is None:
        return rng.choice(options)
    return rng.choices(options, weights=weights, k=1)[0]


def _multi(rng: random.Random, options: list[str], k_min: int = 1, k_max: int = 4) -> str:
    k = rng.randint(k_min, min(k_max, len(options)))
    return ", ".join(rng.sample(options, k=k))


def _freq(rng: random.Random, heavy_user: bool) -> str:
    if heavy_user:
        return _choice(rng, FREQ, [0.05, 0.10, 0.25, 0.35, 0.25])
    return _choice(rng, FREQ, [0.35, 0.25, 0.20, 0.15, 0.05])


def _likert(rng: random.Random, favorable: bool = True) -> str:
    if favorable:
        return _choice(rng, LIKERT, [0.05, 0.10, 0.20, 0.40, 0.25])
    return _choice(rng, LIKERT, [0.10, 0.25, 0.30, 0.25, 0.10])


def build_rows(n: int = 20, seed: int = 2026) -> pd.DataFrame:
    rng = random.Random(seed)
    rows: list[dict] = []
    base_ts = datetime(2026, 7, 10, 9, 0, 0)

    for i in range(n):
        # 2 docentes no usuarios de IA
        conoce = "No" if i in {3, 14} else "Sí"
        heavy = conoce == "Sí" and i % 3 == 0
        row: dict = {}
        row["Marca temporal"] = (base_ts + timedelta(hours=i * 5, minutes=i * 7)).strftime("%Y-%m-%d %H:%M:%S")
        row["¿En qué Unidad Académica dictás clases principalmente?"] = UA[i % len(UA)]
        row["Sede principal de dictado"] = _choice(
            rng, SEDE, [0.45, 0.30, 0.15, 0.10]
        )
        row["Categoría / vínculo principal"] = _choice(
            rng, CATEGORIA, [0.15, 0.15, 0.30, 0.15, 0.10, 0.05, 0.10]
        )
        row["Antigüedad en la docencia universitaria"] = _choice(
            rng, ANTIG, [0.10, 0.20, 0.25, 0.30, 0.15]
        )
        row["Edad"] = _choice(rng, EDAD, [0.05, 0.25, 0.30, 0.25, 0.10, 0.05])
        row["Género"] = _choice(rng, GENERO, [0.50, 0.42, 0.06, 0.02])
        row["¿Tenés acceso frecuente a una computadora personal o notebook para tu trabajo docente?"] = _choice(
            rng, SI_NO, [0.92, 0.08]
        )
        row["¿Conocés o usaste alguna vez una herramienta de inteligencia artificial?"] = conoce

        if conoce == "Sí":
            row["¿Cuáles de estas herramientas de IA conocés o usaste alguna vez?"] = _multi(
                rng, HERRAMIENTAS, 2, 5
            )
            # forzar ChatGPT frecuente
            tools = row["¿Cuáles de estas herramientas de IA conocés o usaste alguna vez?"].split(", ")
            if "ChatGPT" not in tools:
                tools = ["ChatGPT"] + tools
                row["¿Cuáles de estas herramientas de IA conocés o usaste alguna vez?"] = ", ".join(tools[:5])
            row["¿Con qué frecuencia utilizás herramientas de IA para actividades docentes o académicas?"] = _freq(
                rng, heavy
            )
            row["¿Dónde conociste por primera vez una herramienta de IA?"] = _choice(
                rng, DONDE, [0.20, 0.25, 0.05, 0.15, 0.10, 0.20, 0.05]
            )
        else:
            row["¿Cuáles de estas herramientas de IA conocés o usaste alguna vez?"] = ""
            row["¿Con qué frecuencia utilizás herramientas de IA para actividades docentes o académicas?"] = "Nunca"
            row["¿Dónde conociste por primera vez una herramienta de IA?"] = ""

        for uso in USOS:
            col = GRID_USOS_PREFIX.format(uso)
            row[col] = "Nunca" if conoce == "No" else _freq(rng, heavy)

        for aff in ACTITUDES:
            col = GRID_LIKERT_PREFIX.format(aff)
            # riesgo / dependencia: más acuerdo; "sin necesidad de IA": mixto
            if any(k in aff.lower() for k in ("dependencia", "preocupa", "difícil saber")):
                row[col] = _likert(rng, favorable=True)
            elif "sin necesidad de incorporar ia" in aff.lower():
                row[col] = _likert(rng, favorable=conoce == "No")
            elif "sin validar" in aff.lower():
                row[col] = _likert(rng, favorable=False)
            else:
                row[col] = _likert(rng, favorable=True)

        row["¿Sabés si tu Unidad Académica tiene alguna normativa o lineamiento sobre el uso de inteligencia artificial?"] = _choice(
            rng, NORMATIVA, [0.15, 0.55, 0.30]
        )
        row["En tus asignaturas, ¿advertís o orientás a los estudiantes sobre el uso indebido de estas herramientas?"] = _choice(
            rng, ADVERT, [0.30, 0.35, 0.30, 0.05]
        )
        row["¿Creés que usar IA para hacer trabajos completos sin intervención propia del estudiante debería considerarse una falta?"] = _choice(
            rng, FALTA, [0.55, 0.30, 0.15]
        )
        row["Cuando permitís o sugerís usar IA, ¿pedís declaración / transparencia del uso?"] = _choice(
            rng, DECLARACION, [0.20, 0.35, 0.20, 0.25]
        )
        row["¿Cuál es tu postura predominante frente al uso de IA por estudiantes en tus materias?"] = _choice(
            rng, POSTURA, [0.05, 0.40, 0.15, 0.20, 0.20]
        )
        row["¿Tuviste capacitaciones o espacios formativos sobre el uso de IA para la docencia?"] = _choice(
            rng, CAPA, [0.15, 0.10, 0.40, 0.35]
        )
        row["¿Te gustaría tener más formación sobre inteligencia artificial para tu práctica docente?"] = _choice(
            rng, MAS_FORM, [0.60, 0.30, 0.10]
        )
        row["En qué temas te gustaría capacitarte"] = _multi(rng, TEMAS, 2, 5)

        row["¿Qué ventajas encontrás en el uso de la inteligencia artificial como docente?"] = (
            "" if conoce == "No" else VENTAJAS[i % len(VENTAJAS)]
        )
        row["¿Qué riesgos o preocupaciones te genera el uso de estas herramientas en la universidad?"] = RIESGOS[
            i % len(RIESGOS)
        ]
        row[
            "¿Qué recomendaciones harías para un uso responsable de la IA en el ámbito académico (enseñanza, aprendizaje y evaluación)?"
        ] = RECOM[i % len(RECOM)]
        row["Si querés, mencioná una buena práctica o experiencia concreta con IA en tu cátedra (opcional)."] = (
            "" if conoce == "No" else BUENAS[i % len(BUENAS)]
        )

        rows.append(row)

    return pd.DataFrame(rows)


def main() -> None:
    df = build_rows(20)
    outs = [
        Path("/Users/claudiolarrea/Documents/Observatorio/local-lab/datos/encuesta_ia_docentes_20_ficticias.xlsx"),
        Path(
            "/Users/claudiolarrea/Library/CloudStorage/OneDrive-Personal/16 Secretaría de Investigación/"
            "60 Observatorio de Inteligencia Artificial/Encuestas docentes 2026/"
            "encuesta_ia_docentes_20_ficticias.xlsx"
        ),
        Path("/Users/claudiolarrea/Downloads/encuesta_ia_docentes_20_ficticias.xlsx"),
    ]
    for out in outs:
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(out, index=False)
        print(f"OK {out} ({df.shape[0]}×{df.shape[1]})")


if __name__ == "__main__":
    main()
