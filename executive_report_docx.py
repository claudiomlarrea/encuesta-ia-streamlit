"""
Informe EJECUTIVO (Word) — narrativo.

Portada + índice clicable (con subpuntos de recomendaciones) + numeración de páginas.
Los cruces del Análisis automático se integran en la narrativa del apartado temático
correspondiente (hallazgos, beneficios, riesgos o brechas), sin un capítulo aparte.
"""
from __future__ import annotations

import io
import re
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
import pandas as pd

from executive_narrative import build_executive_sections, weave_crosses_into_executive_sections
from report_common import (
    MUTED,
    add_aesthetic_cover,
    add_heading,
    add_para,
    add_toc_hyperlink,
    normalize_user_crosses,
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


def _rec_bookmark(sec_idx: int, rec_n: int) -> str:
    return f"bm_ex_{sec_idx}_r{rec_n}"


def build_executive_report_docx(
    df: pd.DataFrame,
    *,
    title: str = "",
    subtitle: str = "",
    cohort_label: str = "",
    source_name: str = "",
    user_crosses: list[dict[str, Any]] | None = None,
    auto_analysis: list[dict[str, Any]] | None = None,
) -> bytes:
    import report_common as rc

    rc._bookmark_seq = 0

    profiles = classify_columns(df)
    audience = _infer_audience(source_name, profiles)
    cover_title = title.strip() or (
        f"Diagnóstico institucional sobre el uso de Inteligencia Artificial en {audience} "
        "de la Universidad Católica de Cuyo"
    )
    cover_sub = subtitle.strip() or (
        "Documento de síntesis para presentación a la comunidad educativa de la UCCuyo."
    )

    if user_crosses is not None:
        crosses = list(user_crosses)
    elif auto_analysis is not None:
        crosses = normalize_user_crosses(auto_analysis)
    else:
        crosses = []

    sections = build_executive_sections(df, audience=audience)
    sections = weave_crosses_into_executive_sections(sections, crosses, profiles)
    section_items = list(sections.items())

    # Subpuntos: recomendaciones numeradas del apartado 7 (si existen)
    rec_subpoints: dict[int, list[tuple[int, str]]] = {}
    for idx, (name, paras) in enumerate(section_items, start=1):
        subs: list[tuple[int, str]] = []
        for para in paras:
            m = re.match(r"^(\d+)\.\s+(.+)$", para.strip())
            if m and len(m.group(2)) > 12:
                subs.append((int(m.group(1)), para.strip()))
        if subs and ("recomend" in name.lower() or idx == 7):
            rec_subpoints[idx] = subs

    doc = Document()
    add_aesthetic_cover(
        doc,
        kicker="INFORME EJECUTIVO INSTITUCIONAL",
        title=cover_title,
        subtitle=cover_sub,
    )
    setup_margins(doc, section=doc.sections[-1])

    add_heading(doc, "INFORME EJECUTIVO", 1, bookmark="bm_ex_titulo")
    add_para(
        doc,
        f"Uso de Inteligencia Artificial en {audience} de la Universidad Católica de Cuyo",
        size=13,
        bold=True,
        space_after=10,
    )
    if cohort_label:
        add_para(doc, f"Cohorte / instrumento: {cohort_label}.", size=10, color=MUTED)

    add_heading(doc, "ÍNDICE", 1, bookmark="bm_ex_indice")
    add_para(
        doc,
        "Hacé clic en cada ítem para ir al apartado correspondiente.",
        size=9,
        color=MUTED,
        align=WD_ALIGN_PARAGRAPH.LEFT,
        space_after=6,
    )
    for idx, (name, _paras) in enumerate(section_items, start=1):
        add_toc_hyperlink(doc, name, f"bm_ex_{idx}", bold=True, space_after=2)
        # Los subpuntos (p. ej. recomendaciones 1–7) quedan en el cuerpo, no en el índice.

    for idx, (name, paras) in enumerate(section_items, start=1):
        add_heading(doc, name, 1, bookmark=f"bm_ex_{idx}")
        for para in paras:
            m = re.match(r"^(\d+)\.\s+(.+)$", para.strip())
            if m and idx in rec_subpoints:
                rec_n = int(m.group(1))
                add_heading(doc, para.strip(), 2, bookmark=_rec_bookmark(idx, rec_n))
            elif m and len(para) > 1 and para[1] == ".":
                add_para(doc, para, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6)
            else:
                add_para(doc, para)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
