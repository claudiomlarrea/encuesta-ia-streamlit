"""Estética global de Encuesta Clara: tema claro, tipografía y gráficos Plotly."""
from __future__ import annotations

import html

import streamlit as st

# Paleta: claridad (azul cielo) + calidez (ámbar suave)
PRIMARY = "#0284C7"
PRIMARY_DARK = "#0369A1"
ACCENT = "#0D9488"
WARM = "#F59E0B"
TEXT = "#1E3A5F"
TEXT_MUTED = "#64748B"
SURFACE = "#FFFFFF"
BG = "#FDF8F3"

CHART_SEQUENCE = [PRIMARY, ACCENT, WARM, "#8B5CF6", "#EC4899", "#14B8A6", "#F97316"]


def inject_theme() -> None:
    """CSS complementario al config.toml (hero, tabs, métricas, espaciado)."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
        }}

        .block-container {{
            padding-top: 1.25rem;
            padding-bottom: 2.5rem;
            max-width: 1180px;
        }}

        .ec-hero {{
            background: linear-gradient(135deg, #E0F2FE 0%, #F0FDFA 42%, #FFF7ED 100%);
            border: 1px solid #BAE6FD;
            border-radius: 16px;
            padding: 1.35rem 1.6rem 1.2rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 4px 24px rgba(2, 132, 199, 0.08);
        }}
        .ec-hero h1 {{
            margin: 0 0 0.35rem 0;
            font-size: 1.85rem;
            font-weight: 700;
            color: {TEXT};
            letter-spacing: -0.02em;
        }}
        .ec-hero p {{
            margin: 0;
            font-size: 1.02rem;
            line-height: 1.55;
            color: {TEXT_MUTED};
        }}
        .ec-hero .ec-badge {{
            display: inline-block;
            background: {SURFACE};
            color: {PRIMARY_DARK};
            font-size: 0.78rem;
            font-weight: 600;
            padding: 0.2rem 0.65rem;
            border-radius: 999px;
            border: 1px solid #7DD3FC;
            margin-bottom: 0.55rem;
        }}

        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
            border-right: 1px solid #E2E8F0;
        }}
        [data-testid="stSidebar"] .stMarkdown h2, [data-testid="stSidebar"] .stMarkdown h3 {{
            color: {TEXT};
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
            background: #E0F2FE !important;
            color: {PRIMARY_DARK} !important;
        }}

        [data-testid="stMetric"] {{
            background: {SURFACE};
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 0.65rem 0.85rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        }}
        [data-testid="stMetric"] label {{
            color: {TEXT_MUTED} !important;
        }}
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: {PRIMARY_DARK} !important;
        }}

        .stButton > button[kind="primary"] {{
            border-radius: 10px;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(2, 132, 199, 0.25);
        }}
        .stButton > button[kind="secondary"] {{
            border-radius: 10px;
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            overflow: hidden;
        }}

        div[data-testid="stAlert"] {{
            border-radius: 10px;
        }}

        h2, h3, h4, h5 {{
            color: {TEXT} !important;
        }}
        .stCaption {{
            color: {TEXT_MUTED} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header(app_name: str, subtitle: str) -> None:
    safe_name = html.escape(app_name)
    safe_sub = html.escape(subtitle)
    st.markdown(
        f"""
        <div class="ec-hero">
            <span class="ec-badge">Análisis de encuestas</span>
            <h1>{safe_name}</h1>
            <p>{safe_sub}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_plotly_style(fig):  # noqa: ANN001 — fig de Plotly
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, system-ui, sans-serif", color=TEXT, size=13),
        title_font=dict(size=16, color=TEXT, family="Plus Jakarta Sans, system-ui, sans-serif"),
        margin=dict(l=16, r=16, t=48, b=16),
        colorway=CHART_SEQUENCE,
    )
    fig.update_xaxes(gridcolor="#E2E8F0", linecolor="#CBD5E1", zerolinecolor="#E2E8F0")
    fig.update_yaxes(gridcolor="#E2E8F0", linecolor="#CBD5E1", zerolinecolor="#E2E8F0")
    return fig


def configure_matplotlib() -> None:
    import matplotlib as mpl

    mpl.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "axes.edgecolor": "#CBD5E1",
            "axes.labelcolor": TEXT,
            "text.color": TEXT,
            "xtick.color": TEXT_MUTED,
            "ytick.color": TEXT_MUTED,
            "grid.color": "#E2E8F0",
            "font.family": "sans-serif",
        }
    )
