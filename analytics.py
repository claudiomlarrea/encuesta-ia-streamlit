"""Google Analytics 4 (opcional, vía secrets)."""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components


def _measurement_id() -> str | None:
    try:
        sec = st.secrets.get("analytics", {})
        mid = str(sec.get("measurement_id", "")).strip()
    except Exception:
        mid = ""
    if mid and mid.upper().startswith("G-"):
        return mid
    return None


def inject_google_analytics() -> None:
    """Inserta gtag.js si hay measurement_id en st.secrets['analytics']."""
    mid = _measurement_id()
    if not mid:
        return

    components.html(
        f"""
        <!DOCTYPE html>
        <html><head>
        <script async src="https://www.googletagmanager.com/gtag/js?id={mid}"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){{dataLayer.push(arguments);}}
            gtag('js', new Date());
            gtag('config', '{mid}', {{
                'anonymize_ip': true,
                'page_path': window.location.pathname
            }});
        </script>
        </head><body></body></html>
        """,
        height=0,
    )
