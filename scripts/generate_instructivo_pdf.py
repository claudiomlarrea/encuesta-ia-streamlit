#!/usr/bin/env python3
"""Genera el instructivo PDF de Encuesta Clara (misma lógica/estética que EvaluAR)."""

from __future__ import annotations

import shutil
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "instructivo"
LOGO = ROOT / "assets" / "logo_observatorio_ia.png"
OUTPUT = ROOT / "assets" / "instructivo_encuesta_clara.pdf"
DOCS_OUTPUT = Path.home() / "Documents" / "EncuestaClara" / "instructivo-encuesta-clara-uccuyo.pdf"
OBS_OUTPUT = (
    Path.home()
    / "Projects"
    / "observatorio-ia"
    / "docs"
    / "instructivos"
    / "instructivo-encuesta-clara.pdf"
)

URL_UCCUYO = "https://uccuyo.edu.ar/"
URL_OBS = "https://claudiomlarrea.github.io/observatorio-ia/"
URL_HERR = "https://claudiomlarrea.github.io/observatorio-ia/#herramientas"
URL_APP = "https://cuantitativo-cualitativo-encuesta.streamlit.app/"
URL_MAIL = "observatorioia@uccuyo.edu.ar"

GREEN = colors.HexColor("#044A30")
GREEN_BANNER = colors.HexColor("#064a38")
MAROON = colors.HexColor("#7a1532")
MAROON_DARK = colors.HexColor("#4a0c1f")
GRAY = colors.HexColor("#64748b")
TEXT = colors.HexColor("#1e293b")
WHITE = colors.white


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "cover_title",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=28,
            textColor=WHITE,
            spaceAfter=12,
            alignment=TA_CENTER,
            leading=34,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle",
            parent=base["Normal"],
            fontSize=13,
            textColor=WHITE,
            alignment=TA_CENTER,
            spaceAfter=10,
            leading=18,
        ),
        "cover_muted": ParagraphStyle(
            "cover_muted",
            parent=base["Normal"],
            fontSize=11,
            textColor=colors.Color(1, 1, 1, alpha=0.9),
            alignment=TA_CENTER,
            spaceAfter=8,
            leading=16,
        ),
        "cover_body": ParagraphStyle(
            "cover_body",
            parent=base["Normal"],
            fontSize=10.5,
            textColor=colors.Color(1, 1, 1, alpha=0.92),
            alignment=TA_CENTER,
            spaceAfter=6,
            leading=15,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=GREEN,
            spaceBefore=14,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=MAROON_DARK,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=TEXT,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            leftIndent=14,
            spaceAfter=4,
        ),
        "url": ParagraphStyle(
            "url",
            parent=base["Normal"],
            fontSize=9,
            textColor=GREEN,
            spaceAfter=4,
        ),
        "caption": ParagraphStyle(
            "caption",
            parent=base["Normal"],
            fontSize=8.5,
            textColor=GRAY,
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "step": ParagraphStyle(
            "step",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=MAROON_DARK,
            spaceBefore=8,
            spaceAfter=4,
        ),
    }


def _p(text: str, style: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(text, styles[style])


def _bullets(items: list[str], styles: dict[str, ParagraphStyle]) -> list:
    return [_p(f"• {item}", "bullet", styles) for item in items]


def _image(path: Path, width: float = 165 * mm, max_height: float = 95 * mm) -> Image | Spacer:
    if not path.is_file():
        return Spacer(1, 6)
    reader = ImageReader(str(path))
    iw, ih = reader.getSize()
    if iw <= 0 or ih <= 0:
        return Spacer(1, 6)
    height = width * (ih / iw)
    if height > max_height:
        height = max_height
        width = height * (iw / ih)
    img = Image(str(path), width=width, height=height)
    img.hAlign = "CENTER"
    return img


def _url_block(label: str, url: str, styles: dict[str, ParagraphStyle]) -> list:
    return [
        _p(f"<b>{label}</b>", "body", styles),
        _p(f'<link href="{url}"><u>{url}</u></link>', "url", styles),
        Spacer(1, 4),
    ]


def _section(title: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    return _p(title, "h1", styles)


def build_story(styles: dict[str, ParagraphStyle]) -> list:
    story: list = []

    # Portada
    story.append(Spacer(1, 48 * mm))
    if LOGO.is_file():
        logo = Image(str(LOGO), width=36 * mm, height=36 * mm)
        logo.hAlign = "CENTER"
        story += [logo, Spacer(1, 10 * mm)]
    story += [
        _p("UNIVERSIDAD CATÓLICA DE CUYO", "cover_muted", styles),
        _p("Observatorio de Inteligencia Artificial", "cover_subtitle", styles),
        Spacer(1, 8 * mm),
        _p("Instructivo Encuesta Clara", "cover_title", styles),
        _p("Del Excel de Google Forms a tablas, cruces y temas", "cover_subtitle", styles),
        Spacer(1, 14 * mm),
        _p(
            "Guía paso a paso para docentes e investigadores:<br/>"
            "acceso, carga de respuestas, análisis cuantitativo<br/>"
            "y cualitativo, y descarga de informes.",
            "cover_body",
            styles,
        ),
        Spacer(1, 28 * mm),
        _p(URL_MAIL, "cover_muted", styles),
        PageBreak(),
    ]

    # Índice
    story.append(_section("Índice", styles))
    toc = [
        "1. ¿Qué es Encuesta Clara?",
        "2. Cómo acceder desde la web de la UCCuyo",
        "3. Pantalla de inicio y barra lateral",
        "4. Cargar el Excel de respuestas",
        "5. Resumen de ítems",
        "6. Limpieza de datos",
        "7. Análisis automático (modo guiado)",
        "8. Análisis cuantitativo",
        "9. Análisis cualitativo",
        "10. Descargas e informes",
        "11. Contacto institucional",
        "12. Consejos útiles",
        "13. URLs de referencia",
    ]
    story += [_p(line, "bullet", styles) for line in toc]
    story.append(PageBreak())

    # 1
    story.append(_section("1. ¿Qué es Encuesta Clara?", styles))
    story += _bullets(
        [
            "Herramienta del Observatorio de IA de la UCCuyo para analizar encuestas institucionales.",
            "Carga un Excel exportado de Google Forms (u otro similar).",
            "Clasifica automáticamente ítems estructurados (cerrados) y abiertos (texto libre).",
            "Ofrece análisis cuantitativo: frecuencias, cruces χ², pruebas, Cronbach, PCA/AFE, clustering, predictivos.",
            "Ofrece análisis cualitativo: temas (NMF), sentimiento y vocabulario del discurso.",
            "Incluye interpretaciones orientativas automáticas (no IA generativa).",
            "Los datos quedan en la sesión del navegador; no se almacenan de forma permanente en el servidor.",
        ],
        styles,
    )
    story.append(PageBreak())

    # 2 Acceso
    story.append(_section("2. Cómo acceder desde la web de la UCCuyo", styles))
    story.append(
        _p(
            "Podés entrar directo con el enlace del paso 4, o seguir la ruta institucional:",
            "body",
            styles,
        )
    )
    access_steps = [
        (
            "Paso 1 — Sitio de la Universidad",
            URL_UCCUYO,
            "01-uccuyo.jpg",
            "Ingresá a la página principal de la UCCuyo. En el menú o en <b>Accesos</b>, "
            "buscá <b>Observatorio de Inteligencia Artificial</b>.",
        ),
        (
            "Paso 2 — Observatorio de IA",
            URL_OBS,
            "02-observatorio-inicio.jpg",
            "En la portada usá el menú superior o el botón <b>Herramientas de análisis</b>.",
        ),
        (
            "Paso 3 — Herramientas de análisis",
            URL_HERR,
            "03-herramientas-clara.jpg",
            "En la tarjeta <b>Encuesta Clara</b> hacé clic en <b>Abrir Encuesta Clara</b> "
            "(también podrás descargar este instructivo en PDF).",
        ),
        (
            "Paso 4 — Encuesta Clara",
            URL_APP,
            "04-encuesta-clara-inicio.jpg",
            "Llegás a la pantalla de inicio. Si la app estaba dormida (Streamlit Cloud), "
            "tocá <b>Yes, get this app back up!</b> y esperá unos segundos.",
        ),
    ]
    for title, url, img, desc in access_steps:
        story.append(_p(title, "step", styles))
        story += _url_block("URL:", url, styles)
        story.append(_p(desc, "body", styles))
        story.append(_image(ASSETS / img))
        story.append(_p(f"Figura: {title}", "caption", styles))
    story.append(PageBreak())

    # 3 Inicio
    story.append(_section("3. Pantalla de inicio y barra lateral", styles))
    story.append(_p("En la pantalla principal", "h2", styles))
    story += _bullets(
        [
            "Badge <b>Herramienta de análisis</b> y título <b>Encuesta Clara</b>.",
            "Tagline: del Excel de Google Forms a tablas, cruces y temas del texto libre.",
            "Expander con ejemplos de análisis cuantitativos habituales.",
            "Botón / enlace <b>Instructivo</b> (abre este PDF).",
            "Enlace <b>← Sitio del Observatorio de IA</b>.",
        ],
        styles,
    )
    story.append(_p("Barra lateral (siempre)", "h2", styles))
    story += _bullets(
        [
            "Sección <b>Datos</b> → <b>Subí el Excel de respuestas</b>.",
            "Toggle opcional: modelo de sentimiento RoBERTuito (si está disponible).",
            "Slider <b>Cantidad de temas (NMF)</b> (3 a 10).",
            "Formulario <b>Contacto institucional</b>.",
        ],
        styles,
    )
    story.append(_p("Con datos cargados aparecen además:", "h2", styles))
    story += _bullets(
        [
            "Selector de <b>Pestañas del panel</b> a mostrar.",
            "Selector de módulos dentro de <b>Análisis cuantitativo</b>.",
            "Botón <b>Quitar archivo y reiniciar sesión</b>.",
        ],
        styles,
    )
    story.append(PageBreak())

    # 4 Carga
    story.append(_section("4. Cargar el Excel de respuestas", styles))
    story += _bullets(
        [
            "En Google Forms: Responses → descarga / exportá a Excel (.xlsx).",
            "En la barra lateral: <b>Subí el Excel de respuestas</b>.",
            "Formatos: .xlsx o .xls (se lee la primera hoja).",
            "Columna de tiempo típica («Marca temporal», «Timestamp») se excluye del análisis.",
            "Matrices Likert de Forms (encabezados con […]) se agrupan automáticamente.",
            "Al cargar verás: filas × columnas y un mensaje de clasificación de ítems.",
            "Privacidad: los datos viven en tu sesión del navegador hasta reiniciar.",
        ],
        styles,
    )
    story.append(PageBreak())

    # 5 Resumen
    story.append(_section("5. Resumen de ítems", styles))
    story += _bullets(
        [
            "Primera pestaña tras cargar el archivo.",
            "Muestra ítems estructurados (cerrados) e ítems abiertos (texto).",
            "Útil para verificar que la clasificación automática es correcta.",
            "Podés descargar listados / bloques en CSV si lo necesitás.",
        ],
        styles,
    )
    story.append(PageBreak())

    # 6 Limpieza
    story.append(_section("6. Limpieza de datos", styles))
    story += _bullets(
        [
            "Botón <b>Activar limpieza de datos</b> (activar solo cuando haga falta).",
            "Subpestañas: Calidad de la planilla · Coherencia · Valores aberrantes · Respuestas basura.",
            "Generá tablas de completitud, incoherencias y filas con alertas.",
            "Descargas típicas: calidad_columnas.csv, incoherencias_encuesta.csv, "
            "valores_aberrantes.csv, respuestas_basura.csv, filas_con_alertas_limpieza.csv.",
        ],
        styles,
    )
    story.append(PageBreak())

    # 7 Automático
    story.append(_section("7. Análisis automático (modo guiado)", styles))
    story.append(
        _p(
            "Es el recorrido recomendado la primera vez. Elegí modo "
            "<b>Guiado (recomendado)</b>.",
            "body",
            styles,
        )
    )
    story += _bullets(
        [
            "<b>1. Pregunta del cuestionario</b> — elegí el ítem a analizar.",
            "<b>2. Filtrar la muestra (opcional)</b> — unidad académica, año, edad, género, etc.",
            "<b>3. Tipo de análisis</b> — frecuencias, cruce χ², conteo de categorías, "
            "o muestra de texto abierto.",
            "Clic en <b>Ver resultados</b>.",
            "Descargá con <b>Descargar informe (CSV)</b>.",
            "Métricas: Total encuesta · Tras filtros · % de la muestra.",
        ],
        styles,
    )
    story.append(PageBreak())

    # 8 Cuanti
    story.append(_section("8. Análisis cuantitativo", styles))
    story.append(
        _p(
            "Para profundidad metodológica. Podés filtrar por categoría o fechas "
            "y marcar ítems invertidos antes de escalas.",
            "body",
            styles,
        )
    )
    story.append(_p("Módulos", "h2", styles))
    story += _bullets(
        [
            "<b>1. Descriptivos</b> — frecuencias, porcentajes, estadísticos ordinales; CSV.",
            "<b>2. Cruces + χ²</b> — tabla cruzada, p-valor, Cramér V.",
            "<b>3. Pruebas de significancia</b> — t Welch, Mann–Whitney, ANOVA, Kruskal–Wallis.",
            "<b>4. Alfa Cronbach</b> — consistencia interna de escalas Likert/frecuencia.",
            "<b>5. PCA / AFE</b> — componentes y factorial exploratorio (Varimax).",
            "<b>6. Clustering</b> — K-means, DBSCAN, jerárquico.",
            "<b>7. Predictivos + SHAP</b> — logística, árboles, RF (SHAP si está disponible).",
            "<b>8. CFA – semopy</b> — CFA simple (puede no estar en Cloud).",
        ],
        styles,
    )
    story.append(
        _p(
            "<b>Consejo:</b> Cronbach / PCA / AFE solo con ítems Likert del mismo bloque; "
            "no mezclar género o edad con escalas de actitud.",
            "body",
            styles,
        )
    )
    story.append(PageBreak())

    # 9 Cuali
    story.append(_section("9. Análisis cualitativo", styles))
    story += _bullets(
        [
            "Elegí la <b>Columna abierta</b> a analizar.",
            "<b>1. Análisis temático (NMF)</b> — temas, palabras clave y citas; "
            "slider de cantidad de temas en la barra lateral.",
            "<b>2. Sentimiento</b> — polaridad orientativa (léxico ES; RoBERTuito opcional).",
            "<b>3. Discurso y vocabulario</b> — bigramas, trigramas y concordancias.",
            "Al final: <b>Descargar informe completo (Word)</b>.",
            "Temas y sentimiento son apoyos exploratorios, no reemplazan codificación teórica.",
        ],
        styles,
    )
    story.append(PageBreak())

    # 10 Descargas
    story.append(_section("10. Descargas e informes", styles))
    story += _bullets(
        [
            "Casi todos los módulos tienen <b>Descargar informe (CSV)</b>.",
            "Cualitativo: CSV de temas y sentimiento + Word integrado.",
            "Guardá los archivos en tu computadora: son tu respaldo del análisis.",
            "Al terminar: <b>Quitar archivo y reiniciar sesión</b>.",
        ],
        styles,
    )
    story.append(PageBreak())

    # 11 Contacto
    story.append(_section("11. Contacto institucional", styles))
    story += _bullets(
        [
            "En la barra lateral: Nombre, Apellido, Email, Teléfono (opcional) y Mensaje.",
            "Botón <b>Enviar mensaje</b> (o Abrir en mi correo).",
            f"Destino: {URL_MAIL}",
        ],
        styles,
    )
    story.append(PageBreak())

    # 12 Consejos
    story.append(_section("12. Consejos útiles", styles))
    story += _bullets(
        [
            "Empezá por <b>Análisis automático → Guiado</b>.",
            "Marcá ítems invertidos antes de Alfa Cronbach o análisis factorial.",
            "Si la app muestra la cara dormida de Streamlit, despertála y esperá 20–40 s.",
            "En Cloud pueden faltar CFA (semopy), SHAP o RoBERTuito; el núcleo sí está.",
            "Las interpretaciones son orientativas: no sustituyen marco teórico ni asesoría estadística.",
            "No subas datos sensibles sin autorización institucional.",
        ],
        styles,
    )
    story.append(PageBreak())

    # 13 URLs
    story.append(_section("13. URLs de referencia", styles))
    for label, url in [
        ("Universidad Católica de Cuyo", URL_UCCUYO),
        ("Observatorio de IA", URL_OBS),
        ("Herramientas de análisis", URL_HERR),
        ("Encuesta Clara (acceso directo)", URL_APP),
        (f"Correo: {URL_MAIL}", f"mailto:{URL_MAIL}"),
    ]:
        story += _url_block(label, url, styles)

    story += [
        Spacer(1, 20),
        _p(
            "Encuesta Clara · Observatorio de Inteligencia Artificial · Universidad Católica de Cuyo",
            "caption",
            styles,
        ),
    ]
    return story


def _draw_cover_background(canvas, doc) -> None:
    w, h = A4
    canvas.saveState()
    canvas.setFillColor(MAROON)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    canvas.setFillColor(MAROON_DARK)
    canvas.setFillAlpha(0.35)
    canvas.rect(w * 0.55, 0, w * 0.45, h, fill=1, stroke=0)
    canvas.setFillAlpha(1)
    canvas.setFillColor(GREEN_BANNER)
    canvas.rect(0, h - 14 * mm, w, 14 * mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 8)
    canvas.drawCentredString(
        w / 2,
        h - 9 * mm,
        "UNIVERSIDAD CATÓLICA DE CUYO  ·  OBSERVATORIO DE INTELIGENCIA ARTIFICIAL",
    )
    canvas.setFillColor(GREEN_BANNER)
    canvas.rect(0, 0, w, 6 * mm, fill=1, stroke=0)
    canvas.restoreState()


def _header_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(20 * mm, 12 * mm, "Encuesta Clara · Instructivo UCCuyo · Observatorio de IA")
    canvas.drawRightString(190 * mm, 12 * mm, f"Página {canvas.getPageNumber()}")
    canvas.restoreState()


def _first_page(canvas, doc) -> None:
    _draw_cover_background(canvas, doc)


def main() -> None:
    styles = _styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DOCS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OBS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=18 * mm,
        title="Instructivo Encuesta Clara",
        author="Observatorio de Inteligencia Artificial - UCCuyo",
    )
    doc.build(build_story(styles), onFirstPage=_first_page, onLaterPages=_header_footer)

    shutil.copy2(OUTPUT, DOCS_OUTPUT)
    if OBS_OUTPUT.parent.is_dir():
        shutil.copy2(OUTPUT, OBS_OUTPUT)
    print(f"Generado: {OUTPUT}")
    print(f"Copia:    {DOCS_OUTPUT}")
    if OBS_OUTPUT.is_file():
        print(f"Obs:      {OBS_OUTPUT}")


if __name__ == "__main__":
    main()
