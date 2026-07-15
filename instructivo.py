"""Botón para abrir el instructivo en PDF."""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from ui_theme import GREEN, GREEN_MID, SURFACE

_PDF_PATH = Path(__file__).resolve().parent / "assets" / "instructivo_encuesta_clara.pdf"
_GITHUB_PDF_URL = (
    "https://claudiomlarrea.github.io/observatorio-ia/docs/instructivos/"
    "instructivo-encuesta-clara.pdf"
)


def render_instructivo_button() -> None:
    """Enlace al PDF (sin embeber el archivo entero en cada carga de página)."""
    if not _PDF_PATH.is_file():
        st.caption("Instructivo PDF no encontrado en el servidor.")
        return

    st.markdown(
        f"""
        <a href="{_GITHUB_PDF_URL}" target="_blank" rel="noopener noreferrer"
           style="
             display:inline-block;
             background:{GREEN};
             color:{SURFACE};
             padding:0.7rem 1.75rem;
             border-radius:10px;
             font-weight:600;
             font-size:1rem;
             text-decoration:none;
             font-family:Montserrat,system-ui,sans-serif;
             box-shadow:0 2px 8px rgba(4,74,48,0.22);
           "
           onmouseover="this.style.background='{GREEN_MID}'"
           onmouseout="this.style.background='{GREEN}'">
           Instructivo
        </a>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Se abre el instructivo en PDF en una pestaña nueva del navegador.")
