"""Google Analytics 4 (secrets o ID por defecto del Observatorio)."""
from __future__ import annotations

import os

import streamlit as st
import streamlit.components.v1 as components

# Mismo ID que el sitio publicado en GitHub Pages (Observatorio de IA).
DEFAULT_MEASUREMENT_ID = "G-C55ZPTW8C2"


def _measurement_id() -> str | None:
    mid = ""
    try:
        sec = st.secrets.get("analytics", {})
        mid = str(sec.get("measurement_id", "")).strip()
    except Exception:
        pass
    if not mid:
        mid = os.environ.get("GA4_MEASUREMENT_ID", DEFAULT_MEASUREMENT_ID).strip()
    if mid and mid.upper().startswith("G-"):
        return mid
    return None


def inject_google_analytics() -> None:
    """Inserta gtag.js en la página principal (Streamlit corre en iframe)."""
    mid = _measurement_id()
    if not mid:
        return

    if st.session_state.get("_ga_injected"):
        return
    st.session_state["_ga_injected"] = True

    components.html(
        f"""
        <script>
        (function () {{
            const mid = "{mid}";
            const doc = window.parent.document;
            if (doc.getElementById("ec-ga-loader")) return;
            const loader = doc.createElement("script");
            loader.id = "ec-ga-loader";
            loader.async = true;
            loader.src = "https://www.googletagmanager.com/gtag/js?id=" + mid;
            doc.head.appendChild(loader);
            const inline = doc.createElement("script");
            inline.id = "ec-ga-inline";
            inline.text = [
                "window.dataLayer = window.dataLayer || [];",
                "function gtag(){{dataLayer.push(arguments);}}",
                "gtag('js', new Date());",
                "gtag('config', '" + mid + "', {{ anonymize_ip: true }});"
            ].join("\\n");
            doc.head.appendChild(inline);
        }})();
        </script>
        """,
        height=0,
    )
