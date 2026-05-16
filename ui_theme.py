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
TEXT_MUTED = "#666666"
GRAY_INST = "#E8E8E8"
GRAY_INST_SOFT = "#F0F0F0"
SURFACE = "#FFFFFF"
BG = GRAY_INST

PRIMARY = GREEN
PRIMARY_DARK = GREEN_DARK
ACCENT = ORANGE
WARM = MAROON

CHART_SEQUENCE = [GREEN, ORANGE, MAROON, GREEN_MID, "#6B9080", "#C9A227", "#2D6A4F"]

LOGO_PATH = Path(__file__).resolve().parent / "assets" / "logo_observatorio_ia.png"
OBSERVATORIO_NAME = "Observatorio de Inteligencia Artificial"
INSTITUTION_NAME = "Universidad Católica de Cuyo"


def inject_theme() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Montserrat', system-ui, -apple-system, sans-serif;
        }}

        [data-testid="stAppViewContainer"] {{
            background-color: {GRAY_INST};
        }}
        [data-testid="stHeader"] {{
            background-color: {GRAY_INST_SOFT};
        }}

        [data-testid="stAppViewContainer"] [data-testid="stMain"] .block-container {{
            padding-top: 2.75rem;
            padding-bottom: 2.5rem;
            padding-left: 1.5rem;
            padding-right: 1.5rem;
            max-width: 1180px;
        }}

        .ec-header-box {{
            box-sizing: border-box;
            width: 100%;
            max-width: 100%;
            margin: 0.5rem 0 0.85rem 0;
            padding: 0.65rem 0 0.85rem 0;
            overflow: visible;
            border-bottom: 3px solid {GREEN};
        }}
        .ec-header-inner {{
            display: flex;
            align-items: center;
            gap: 1rem;
            width: 100%;
            max-width: 100%;
        }}
        .ec-header-logo {{
            flex: 0 0 84px;
            width: 84px;
            min-width: 84px;
        }}
        .ec-header-logo img {{
            display: block;
            width: 84px;
            height: 84px;
            object-fit: contain;
        }}
        .ec-header-text {{
            flex: 1 1 auto;
            min-width: 0;
        }}
        .ec-institutional-title {{
            margin: 0.15rem 0 0;
            font-size: 1.22rem;
            font-weight: 700;
            color: {GREEN};
            line-height: 1.25;
        }}
        .ec-institutional-sub {{
            margin: 0.25rem 0 0;
            font-size: 0.88rem;
            font-weight: 600;
            color: {TEXT_MUTED};
        }}

        .ec-hero {{
            background: linear-gradient(135deg, {SURFACE} 0%, {GREEN_LIGHT} 45%, {GRAY_INST_SOFT} 100%);
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
            background: linear-gradient(180deg, {GRAY_INST_SOFT} 0%, {GRAY_INST} 100%);
            border-right: 1px solid #C8C8C8;
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

        [data-testid="stDownloadButton"] > button {{
            background-color: {GREEN} !important;
            color: {SURFACE} !important;
            border: 1px solid {GREEN} !important;
            border-radius: 10px;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(4, 74, 48, 0.22);
        }}
        [data-testid="stDownloadButton"] > button:hover {{
            background-color: {GREEN_MID} !important;
            border-color: {GREEN_MID} !important;
            color: {SURFACE} !important;
        }}
        [data-testid="stDownloadButton"] > button:focus-visible {{
            outline: none;
            box-shadow: 0 0 0 0.2rem rgba(4, 74, 48, 0.35) !important;
        }}
        [data-testid="stDownloadButton"] > button p,
        [data-testid="stDownloadButton"] > button span,
        [data-testid="stDownloadButton"] > button div {{
            color: {SURFACE} !important;
        }}
        [data-testid="stDownloadButton"] > button svg {{
            fill: {SURFACE} !important;
            stroke: {SURFACE} !important;
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

        [data-testid="stForm"] {{
            margin-bottom: 1.25rem;
            padding-bottom: 0.35rem;
        }}
        [data-testid="stForm"] [data-testid="stMultiSelect"] {{
            margin-bottom: 0.35rem;
        }}
        [data-testid="stMultiSelect"] [data-baseweb="select"] > div {{
            min-height: 2.75rem;
        }}
        [data-testid="stMultiSelect"] [data-baseweb="popover"] {{
            z-index: 100002 !important;
        }}
        .guided-form-actions {{
            display: flex;
            align-items: flex-end;
            justify-content: flex-end;
            min-height: 5.5rem;
            padding-top: 0.5rem;
        }}
        .guided-results-block {{
            margin-top: 1.75rem;
            padding-top: 0.75rem;
            clear: both;
            border-top: 1px solid #C8C8C8;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _logo_base64() -> str:
    if not LOGO_PATH.is_file():
        return ""
    return base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")


def render_institutional_header() -> None:
    """Cabecera: logo y nombre del Observatorio de IA — UCCuyo."""
    name = html.escape(OBSERVATORIO_NAME)
    inst = html.escape(INSTITUTION_NAME)
    b64 = _logo_base64()
    logo_html = (
        f'<img src="data:image/png;base64,{b64}" alt="Logo {name}" />' if b64 else ""
    )
    st.markdown(
        f"""
        <div class="ec-header-box">
            <div class="ec-header-inner">
                <div class="ec-header-logo">{logo_html}</div>
                <div class="ec-header-text">
                    <p class="ec-institutional-title">{name}</p>
                    <p class="ec-institutional-sub">{inst}</p>
                </div>
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
