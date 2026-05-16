"""Estética Encuesta Clara alineada al manual UCCuyo y al Observatorio de IA."""
from __future__ import annotations

import base64
import html
from pathlib import Path

import streamlit as st

# Colores institucionales UCCuyo (verde del manual / muestreado del logo Observatorio IA)
GREEN = "#044A30"
GREEN_DARK = "#033B26"
GREEN_LIGHT = "#E8F3EF"
GREEN_MID = "#0A5C3E"
ORANGE = "#EAA958"
MAROON = "#934B3F"
TEXT = "#1A2E28"
TEXT_MUTED = "#4A5F56"
SURFACE = "#FFFFFF"
BG = "#FAFCFA"

PRIMARY = GREEN
PRIMARY_DARK = GREEN_DARK
ACCENT = ORANGE
WARM = MAROON

CHART_SEQUENCE = [GREEN, ORANGE, MAROON, GREEN_MID, "#6B9080", "#C9A227", "#2D6A4F"]

LOGO_PATH = Path(__file__).resolve().parent / "assets" / "logo_observatorio_ia.png"
OBSERVATORIO_NAME = "Observatorio de Inteligencia Artificial"
INSTITUTION_NAME = "Universidad Católica de Cuyo"


def _logo_data_uri() -> str | None:
    if not LOGO_PATH.is_file():
        return None
    raw = LOGO_PATH.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:image/png;base64,{b64}"


def inject_theme() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Montserrat', system-ui, -apple-system, sans-serif;
        }}

        .block-container {{
            padding-top: 0.85rem;
            padding-bottom: 2.5rem;
            max-width: 1180px;
        }}

        .ec-institutional {{
            display: flex;
            align-items: center;
            gap: 1.1rem;
            padding: 0.85rem 1rem 1rem;
            margin-bottom: 0.75rem;
            border-bottom: 3px solid {GREEN};
            background: {SURFACE};
        }}
        .ec-institutional img {{
            width: 88px;
            height: 88px;
            object-fit: contain;
            flex-shrink: 0;
        }}
        .ec-institutional h2 {{
            margin: 0;
            font-size: 1.22rem;
            font-weight: 700;
            color: {GREEN};
            line-height: 1.25;
            letter-spacing: 0.01em;
        }}
        .ec-institutional .ec-uccuyo {{
            margin: 0.2rem 0 0;
            font-size: 0.88rem;
            font-weight: 600;
            color: {TEXT_MUTED};
        }}

        .ec-hero {{
            background: linear-gradient(135deg, {GREEN_LIGHT} 0%, #FFFFFF 55%, #FFF8EE 100%);
            border: 1px solid #B8D4C8;
            border-left: 5px solid {GREEN};
            border-radius: 14px;
            padding: 1.2rem 1.5rem 1.1rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 4px 20px rgba(4, 74, 48, 0.07);
        }}
        .ec-hero h1 {{
            margin: 0 0 0.35rem 0;
            font-size: 1.65rem;
            font-weight: 700;
            color: {GREEN_DARK};
            letter-spacing: -0.02em;
        }}
        .ec-hero p {{
            margin: 0;
            font-size: 0.98rem;
            line-height: 1.55;
            color: {TEXT_MUTED};
        }}
        .ec-hero .ec-badge {{
            display: inline-block;
            background: {GREEN};
            color: {SURFACE};
            font-size: 0.72rem;
            font-weight: 600;
            padding: 0.18rem 0.6rem;
            border-radius: 999px;
            margin-bottom: 0.5rem;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #FFFFFF 0%, {GREEN_LIGHT} 100%);
            border-right: 1px solid #C5D9CE;
        }}
        [data-testid="stSidebar"] .stMarkdown h2, [data-testid="stSidebar"] .stMarkdown h3 {{
            color: {GREEN_DARK};
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.35rem;
            background: transparent;
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px 8px 0 0;
            padding: 0.45rem 0.9rem;
            font-weight: 500;
        }}
        .stTabs [aria-selected="true"] {{
            background: {GREEN_LIGHT} !important;
            color: {GREEN_DARK} !important;
            border-bottom: 2px solid {GREEN} !important;
        }}

        [data-testid="stMetric"] {{
            background: {SURFACE};
            border: 1px solid #C5D9CE;
            border-top: 3px solid {GREEN};
            border-radius: 12px;
            padding: 0.65rem 0.85rem;
            box-shadow: 0 1px 3px rgba(4, 74, 48, 0.05);
        }}
        [data-testid="stMetric"] label {{
            color: {TEXT_MUTED} !important;
        }}
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: {GREEN_DARK} !important;
        }}

        .stButton > button[kind="primary"] {{
            background-color: {GREEN} !important;
            border-color: {GREEN} !important;
            border-radius: 10px;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(4, 74, 48, 0.22);
        }}
        .stButton > button[kind="primary"]:hover {{
            background-color: {GREEN_MID} !important;
            border-color: {GREEN_MID} !important;
        }}
        .stButton > button[kind="secondary"] {{
            border-radius: 10px;
            color: {GREEN_DARK} !important;
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid #C5D9CE;
            border-radius: 10px;
            overflow: hidden;
        }}

        div[data-testid="stAlert"] {{
            border-radius: 10px;
        }}

        h2, h3, h4, h5 {{
            color: {GREEN_DARK} !important;
        }}
        .stCaption {{
            color: {TEXT_MUTED} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_institutional_header() -> None:
    """Cabecera: logo y nombre del Observatorio de IA — UCCuyo."""
    logo_uri = _logo_data_uri()
    name = html.escape(OBSERVATORIO_NAME)
    inst = html.escape(INSTITUTION_NAME)
    if logo_uri:
        logo_html = f'<img src="{logo_uri}" alt="Logo {name}" />'
    else:
        logo_html = ""
    st.markdown(
        f"""
        <div class="ec-institutional">
            {logo_html}
            <div>
                <h2>{name}</h2>
                <p class="ec-uccuyo">{inst}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header(app_name: str, subtitle: str) -> None:
    safe_name = html.escape(app_name)
    safe_sub = html.escape(subtitle)
    st.markdown(
        f"""
        <div class="ec-hero">
            <span class="ec-badge">Herramienta de análisis</span>
            <h1>{safe_name}</h1>
            <p>{safe_sub}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_plotly_style(fig):  # noqa: ANN001
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Montserrat, system-ui, sans-serif", color=TEXT, size=13),
        title_font=dict(size=16, color=GREEN_DARK, family="Montserrat, system-ui, sans-serif"),
        margin=dict(l=16, r=16, t=48, b=16),
        colorway=CHART_SEQUENCE,
    )
    fig.update_xaxes(gridcolor="#D4E4DB", linecolor="#B8CFC4", zerolinecolor="#D4E4DB")
    fig.update_yaxes(gridcolor="#D4E4DB", linecolor="#B8CFC4", zerolinecolor="#D4E4DB")
    return fig


def configure_matplotlib() -> None:
    import matplotlib as mpl

    mpl.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "axes.edgecolor": "#B8CFC4",
            "axes.labelcolor": TEXT,
            "text.color": TEXT,
            "xtick.color": TEXT_MUTED,
            "ytick.color": TEXT_MUTED,
            "grid.color": "#D4E4DB",
            "font.family": "sans-serif",
        }
    )
