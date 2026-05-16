"""Botón y enlace al instructivo en PDF."""
from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from ui_theme import GREEN, GREEN_MID, SURFACE

_PDF_PATH = Path(__file__).resolve().parent / "assets" / "instructivo_encuesta_clara.pdf"
_GITHUB_PDF_URL = (
    "https://github.com/claudiomlarrea/encuesta-ia-streamlit/raw/main/"
    "assets/instructivo_encuesta_clara.pdf"
)


def _button_styles() -> str:
    return f"""
        background: {GREEN};
        color: {SURFACE};
        padding: 0.7rem 1.75rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        border: none;
        cursor: pointer;
        font-family: Montserrat, system-ui, sans-serif;
        box-shadow: 0 2px 8px rgba(4, 74, 48, 0.22);
    """


def render_instructivo_button() -> None:
    """Abre el PDF en pestaña nueva (blob local) con respaldo de descarga y enlace GitHub."""
    if not _PDF_PATH.is_file():
        st.caption("Instructivo PDF no encontrado en el servidor.")
        return

    pdf_bytes = _PDF_PATH.read_bytes()
    pdf_b64 = base64.b64encode(pdf_bytes).decode("ascii")

    # Streamlit elimina enlaces data: → about:blank; abrimos el PDF con blob en el navegador.
    components.html(
        f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"></head>
        <body style="margin:0;padding:0;">
        <button type="button" id="ec-instructivo-btn" style="{_button_styles()}">
            Instructivo
        </button>
        <script>
        (function () {{
            const b64 = "{pdf_b64}";
            const fallback = "{_GITHUB_PDF_URL}";
            const btn = document.getElementById("ec-instructivo-btn");
            btn.addEventListener("mouseover", function () {{
                btn.style.background = "{GREEN_MID}";
            }});
            btn.addEventListener("mouseout", function () {{
                btn.style.background = "{GREEN}";
            }});
            btn.addEventListener("click", function () {{
                try {{
                    const raw = atob(b64);
                    const arr = new Uint8Array(raw.length);
                    for (let i = 0; i < raw.length; i++) {{
                        arr[i] = raw.charCodeAt(i);
                    }}
                    const blob = new Blob([arr], {{ type: "application/pdf" }});
                    const url = URL.createObjectURL(blob);
                    const opener = window.top || window.parent || window;
                    const w = opener.open(url, "_blank", "noopener,noreferrer");
                    if (!w) {{
                        alert("Permití ventanas emergentes para ver el instructivo, o usá «Descargar instructivo» debajo.");
                    }}
                }} catch (e) {{
                    (window.top || window.parent || window).open(fallback, "_blank", "noopener,noreferrer");
                }}
            }});
        }})();
        </script>
        </body>
        </html>
        """,
        height=52,
    )

    st.caption(
        "Se abre el instructivo en PDF en una pestaña nueva. "
        f"Si no carga, [abrilo desde GitHub]({_GITHUB_PDF_URL}) o descargalo abajo."
    )

    st.download_button(
        "Descargar instructivo (PDF)",
        data=pdf_bytes,
        file_name="instructivo_encuesta_clara.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=False,
        key="download_instructivo_pdf",
    )
