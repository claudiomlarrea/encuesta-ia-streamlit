"""Botón y enlace al instructivo en PDF."""
from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from ui_theme import GREEN, GREEN_MID, SURFACE

_PDF_PATH = Path(__file__).resolve().parent / "assets" / "instructivo_encuesta_clara.pdf"


def render_instructivo_button() -> None:
    """Botón verde que abre el PDF del instructivo en una pestaña nueva."""
    if not _PDF_PATH.is_file():
        st.caption("Instructivo PDF no encontrado en el servidor.")
        return

    pdf_b64 = base64.b64encode(_PDF_PATH.read_bytes()).decode("ascii")
    st.markdown(
        f"""
        <div style="margin-top: 1.75rem; margin-bottom: 0.5rem;">
            <a href="data:application/pdf;base64,{pdf_b64}"
               target="_blank"
               rel="noopener noreferrer"
               style="
                   display: inline-block;
                   background: {GREEN};
                   color: {SURFACE};
                   padding: 0.7rem 1.75rem;
                   border-radius: 10px;
                   font-weight: 600;
                   font-size: 1rem;
                   text-decoration: none;
                   box-shadow: 0 2px 8px rgba(4, 74, 48, 0.22);
               "
               onmouseover="this.style.background='{GREEN_MID}'"
               onmouseout="this.style.background='{GREEN}'">
                Instructivo
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Se abre el instructivo en PDF en una pestaña nueva del navegador.")
