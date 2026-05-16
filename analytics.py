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
