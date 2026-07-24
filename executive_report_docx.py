"""
Informe EJECUTIVO (Word) — narrativo, sin tablas.

Estructura alineada al informe ejecutivo institucional del Observatorio:
portada estética + 8 secciones de interpretación y recomendaciones.
"""
from __future__ import annotations

import io

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
import pandas as pd

from executive_narrative import build_executive_sections
from report_common import (
    MUTED,
    add_aesthetic_cover,
    add_heading,
    add_para,
    setup_margins,
)
from survey_intel import classify_columns


def _infer_audience(source_name: str, profiles) -> str:
    blob = " ".join([source_name or ""] + [p.name for p in profiles[:20]]).lower()
    if "docente" in blob:
        return "docentes"
    if "alumno" in blob or "estudiante" in blob or "unidad academica estás cursando" in blob:
        return "estudiantes"
    return "la comunidad universitaria"


def build_executive_report_docx(
    df: pd.DataFrame,
    *,
    title: str = "",
    subtitle: str = "",
    cohort_label: str = "",
    source_name: str = "",
) -> bytes:
    profiles = classify_columns(df)
    audience = _infer_audience(source_name, profiles)
    cover_title = title.strip() or (
        f"Diagnóstico institucional sobre el uso de Inteligencia Artificial en {audience} "
        "de la Universidad Católica de Cuyo"
    )
    cover_sub = subtitle.strip() or (
        "Documento de síntesis para presentación a la comunidad educativa de la UCCuyo."
    )

    sections = build_executive_sections(df, audience=audience)

    doc = Document()
    # Portada a página completa; add_aesthetic_cover crea la sección de cuerpo
    add_aesthetic_cover(
        doc,
        kicker="INFORME EJECUTIVO INSTITUCIONAL",
        title=cover_title,
        subtitle=cover_sub,
    )
    # Asegurar márgenes del cuerpo (última sección)
    setup_margins(doc, section=doc.sections[-1])

    add_heading(doc, "INFORME EJECUTIVO", 1)
    add_para(
        doc,
        f"Uso de Inteligencia Artificial en {audience} de la Universidad Católica de Cuyo",
        size=13,
        bold=True,
        space_after=10,
    )
    if cohort_label:
        add_para(doc, f"Cohorte / instrumento: {cohort_label}.", size=10, color=MUTED)

    add_heading(doc, "ÍNDICE", 1)
    for name in sections:
        add_para(doc, name, size=11, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=3)

    for name, paras in sections.items():
        add_heading(doc, name, 1)
        for para in paras:
            # recomendaciones numeradas: menos justificado / más listado
            if para[:2].isdigit() and para[1] == ".":
                add_para(doc, para, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
            else:
                add_para(doc, para)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
