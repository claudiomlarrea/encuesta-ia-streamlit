"""
Encuesta Clara — panel Streamlit: Excel de encuestas → cuantitativo y cualitativo.
"""
from __future__ import annotations

import importlib.util
import io
import os
from pathlib import Path
from typing import Any

_HAS_SEMOPY = importlib.util.find_spec("semopy") is not None
_HAS_TRANSFORMERS = importlib.util.find_spec("transformers") is not None
_HAS_SHAP = importlib.util.find_spec("shap") is not None

import pandas as pd
import plotly.express as px
import streamlit as st

import matplotlib.pyplot as plt
import numpy as np

from quant_advanced import (
    aggregate_shap_table_by_question,
    compare_numeric_across_groups,
    cronbach_encoding_diagnostics,
    crosstab_chi_square,
    crosstab_chi_square_smart,
    format_contingency_table_for_display,
    prepare_crosstab_for_display,
    cronbach_alpha,
    dbscan_profiles,
    detect_survey_ordinals_and_question_blocks,
    descriptive_one_column,
    detect_best_ordinal,
    resolve_ordinal_for_group_tests,
    filter_dataframe_comparison,
    fit_predictive_suite,
    hierarchical_linkage_plot,
    invert_ordinal_series,
    kmeans_profiles,
    lavaan_export_snippet,
    likert_numeric_matrix,
    optional_sem_estimate,
    ordinal_scaling_report,
    pca_loadings_from_correlation_matrix,
    polychoric_correlation_matrix,
    prepare_feature_matrix,
    relabel_corr_for_export,
    run_efa,
    run_efa_from_correlation_matrix,
    run_pca_with_loadings,
    decision_tree_rules_text,
    plot_decision_tree_figure,
    shap_diagnostic_bundle,
)
from quant_summaries import (
    academic_exploratory_factor_reading,
    chi_square_explanatory,
    clustering_explanatory,
    kmeans_cluster_reading_hints,
    cronbach_explanatory,
    descriptive_explanatory,
    efa_explanatory,
    group_comparison_explanatory,
    loading_row_choice_labels,
    pca_explanatory,
    predictive_explanatory,
    predictive_academic_explanatory,
    cfa_explanatory_short,
)
from qualitative_deep import (
    deep_discourse_markdown,
    deep_sentiment_markdown,
    deep_thematic_markdown,
)
from survey_intel import (
    ColumnProfile,
    SentimentModel,
    add_total_count_row,
    build_column_label_map,
    classify_columns,
    explode_multiselect,
    frequency_table,
    is_timestamp_column,
    likert_frequency_column_names,
    kwic_snippets,
    lexicon_sentiment_es,
    ngram_top_table,
    thematic_nmf,
)
from feedback import render_institutional_contact
from survey_guided import (
    analysis_options_for_column,
    apply_cohort_filters,
    build_column_choices,
    build_guided_report_csv,
    build_significance_report_csv,
    build_cronbach_report_csv,
    build_pca_efa_report_csv,
    build_clustering_report_csv,
    cohort_filter_scope_markdown,
    crosstab_table_caption,
    discover_filter_columns,
    short_choice_label,
    interpret_guided,
    pick_likert_columns,
    run_guided_analysis,
    GuidedSpec,
)
from survey_qa import example_questions, interpret_result, plan_question, run_plan
from ui_theme import (
    apply_plotly_style,
    configure_matplotlib,
    inject_theme,
    render_brand_header,
    render_institutional_header,
)

APP_NAME = "Encuesta Clara"
APP_TAGLINE = (
    "Del Excel de Google Forms a tablas, cruces y temas del texto libre. "
    "Clasifica ítems estructurados y abiertos; análisis cuantitativo y cualitativo en español."
)

st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme()
configure_matplotlib()

def _bloque_interpretacion_cuantitativa(texto_md: str) -> None:
    st.markdown("---")
    st.markdown("##### Interpretación orientativa (incluye lectura cualitativa muestral automática donde aplica)")
    st.caption(
        "El texto siguiente se arma **solo** con los valores mostrados arriba (sin IA generativa). "
        "Incorpora **bloques cualitativos** (descripciones número‑a‑número) en cruces χ², descriptivos, grupos, Cronbach, PCA/AFE cuando corresponda, clustering K‑means, predictivos.\n\n"
        "Complementalo con el marco teórico del estudio y, si corresponde, asesoría estadística institucional."
    )
    st.markdown(texto_md)


def _bloque_lectura_academica_factores(texto_md: str) -> None:
    st.markdown("---")
    st.markdown("##### Lectura académica exploratoria")
    st.caption(
        "Traducción a lenguaje de informe (**PCA / factorial exploratorio**), referida explícitamente al bloque seleccionado. "
        "**No** usa IA generativa: combina tus tablas y las etiquetas de ítems de la interfaz; **no equivale** a CFA confirmatorio."
    )
    st.markdown(texto_md)


def _bloque_lectura_academica_predictivos(texto_md: str) -> None:
    st.markdown("---")
    st.markdown("##### Lectura académica (modelos predictivos)")
    st.caption(
        "Marco metodológico para informes: **clasificación supervisada** sobre datos de encuesta. "
        "**No** usa IA generativa; se arma con esta configuración, el tamaño efectivo muestral tras alinear predictor–objetivo y la tabla de *accuracy*."
    )
    st.markdown(texto_md)


MAIN_TABS_ORDER = [
    "Resumen de ítems",
    "Análisis automático",
    "Análisis cuantitativo",
    "Análisis cualitativo",
    "Guía metodológica",
]
MAIN_TABS_PUBLIC_HIDDEN = frozenset({"Guía metodológica"})
QUANT_MODULE_ORDER = [
    "1. Descriptivos",
    "2. Cruces + χ²",
    "3. Pruebas de significancia",
    "4. Alfa Cronbach",
    "5. PCA / AFE",
    "6. Clustering",
    "7. Predictivos + SHAP",
    "8. CFA – semopy",
    "9. Notas metodológicas",
]
QUANT_MODULES_PUBLIC_HIDDEN = frozenset({"9. Notas metodológicas"})


def _is_streamlit_cloud() -> bool:
    if os.environ.get("STREAMLIT_RUNTIME_ENV", "").lower() == "cloud":
        return True
    return Path("/mount/src").is_dir()


def is_public_deployment() -> bool:
    """
    Modo público (p. ej. Streamlit Cloud / LinkedIn): sin guía interna, notas técnicas ni ruta local.
    Forzá con secrets.toml: APP_MODE = "public" | "local"
    """
    try:
        mode = str(st.secrets.get("APP_MODE", "")).strip().lower()
    except Exception:
        mode = ""
    if mode in ("public", "cloud", "production"):
        return True
    if mode in ("local", "dev", "development"):
        return False
    return _is_streamlit_cloud()


def main_tabs_for_ui(*, public: bool) -> list[str]:
    if public:
        return [t for t in MAIN_TABS_ORDER if t not in MAIN_TABS_PUBLIC_HIDDEN]
    return list(MAIN_TABS_ORDER)


def quant_modules_for_ui(*, public: bool) -> list[str]:
    if public:
        return [m for m in QUANT_MODULE_ORDER if m not in QUANT_MODULES_PUBLIC_HIDDEN]
    return list(QUANT_MODULE_ORDER)


def _sanitize_ui_tab_picks(*, public: bool) -> None:
    """Quita pestañas/módulos internos si quedaron en sesión tras un deploy público."""
    main_key = _widget_key("pick_main_sections")
    quant_key = _widget_key("pick_quant_modules")
    allowed_main = set(main_tabs_for_ui(public=public))
    allowed_quant = set(quant_modules_for_ui(public=public))
    if main_key in st.session_state:
        st.session_state[main_key] = [x for x in st.session_state[main_key] if x in allowed_main]
    if quant_key in st.session_state:
        st.session_state[quant_key] = [x for x in st.session_state[quant_key] if x in allowed_quant]


_UI_WIDGET_KEYS = (
    "pick_main_sections",
    "pick_quant_modules",
    "survey_qa_mode",
    "survey_qa_question",
    "guided_primary_label",
    "guided_analysis_pick",
    "guided_secondary_label",
    "guided_value_pick",
    "guided_run_results",
    "sig_test_download_csv",
    "cronbach_items",
    "cronbach_download_csv",
    "desc_pick",
    "desc_multi",
    "chi_row",
    "chi_col",
    "sig_y",
    "sig_g",
    "pca_items",
    "lav_lat",
    "slider_pca_dims",
    "slider_efa_factors",
    "clust_feat",
    "tgt",
    "pred_feats",
    "cfa_items",
    "inverted_protocol_items",
    "date_filter_col",
    "cmp_from",
    "cmp_to",
)


def _clear_analysis_ui_state() -> None:
    """Restablece pestañas, módulos y widgets al cambiar o quitar la encuesta."""
    for key in _UI_WIDGET_KEYS:
        st.session_state.pop(key, None)
    st.session_state.pop("guided_result_bundle", None)
    st.session_state.pop("_guided_primary_col", None)
    for key in list(st.session_state.keys()):
        k = str(key)
        if (
            k.startswith("guided_filter_")
            or k.startswith("pick_main_sections")
            or k.startswith("pick_quant_modules")
            or k.startswith("cronbach_selected__")
            or "__chk__" in k
        ):
            st.session_state.pop(key, None)


def _dataset_session_token() -> str:
    df = st.session_state.get("loaded_df")
    name = st.session_state.get("loaded_name") or ""
    if df is None:
        return ""
    return f"{name}|{int(df.shape[0])}|{int(df.shape[1])}|{len(df.columns)}"


def _widget_key(base: str) -> str:
    """Claves de widgets atadas al archivo cargado (nueva encuesta → estado limpio)."""
    token = st.session_state.get("_ui_bound_to") or "sin_datos"
    safe = "".join(c if c.isalnum() else "_" for c in token)[:80]
    return f"{base}__{safe}"


def _bind_ui_to_dataset() -> bool:
    """
    Si cambió la encuesta cargada, limpia widgets y devuelve True si hubo cambio
    (conviene st.rerun() antes de dibujar multiselects).
    """
    token = _dataset_session_token()
    prev = st.session_state.get("_ui_bound_to")
    if prev == token:
        return False
    _clear_analysis_ui_state()
    st.session_state._ui_bound_to = token
    return True


@st.cache_resource(show_spinner=True)
def _load_sentiment_pipeline():
    return SentimentModel.pipe()


def load_table(uploaded: Any, path: str | None) -> tuple[pd.DataFrame, str]:
    if uploaded is not None:
        # Cada rerun del script reutiliza el mismo UploadedFile; sin rebobinar,
        # .read() puede devolver b'' y vaciar la sesión si el except global borra loaded_df.
        try:
            uploaded.seek(0)
        except (OSError, AttributeError, io.UnsupportedOperation):
            pass
        raw = uploaded.read()
        if not raw:
            raise ValueError(
                "No se pudieron leer bytes del archivo subido (buffer vacío). "
                "Probá «Quitar archivo» y volvé a subirlo."
            )
        bio = io.BytesIO(raw)
        df = pd.read_excel(bio)
        return df, uploaded.name
    if path and path.strip():
        df = pd.read_excel(path.strip())
        return df, path.strip().split("/")[-1]
    raise ValueError("No hay archivo.")


def _safe_int_slider(
    label: str,
    *,
    min_value: int,
    max_value: int,
    default: int,
    key: str,
) -> int:
    """Slider entero sin error cuando min==max o el valor guardado en sesión queda fuera de rango."""
    lo, hi = int(min_value), int(max_value)
    if hi < lo:
        hi = lo
    if key in st.session_state:
        try:
            st.session_state[key] = max(lo, min(hi, int(st.session_state[key])))
        except (TypeError, ValueError):
            st.session_state.pop(key, None)
    if hi <= lo:
        st.caption(f"**{label}:** {lo} (único valor posible con los ítems elegidos).")
        return lo
    val = max(lo, min(hi, int(default)))
    return int(
        st.slider(
            label,
            min_value=lo,
            max_value=hi,
            value=val,
            key=key,
        )
    )


def profiles_to_frame(profiles: list[ColumnProfile]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ítem": p.short_name,
                "tipo": p.kind.title(),
                "subtipo": p.subtype,
                "respuestas": p.n_non_null,
                "valores_únicos": p.n_unique,
                "longitud_media": round(p.avg_len, 1),
                "longitud_máx": p.max_len,
                "_col": p.name,
            }
            for p in profiles
        ]
    )


def main() -> None:
    if "loaded_df" not in st.session_state:
        st.session_state.loaded_df = None
        st.session_state.loaded_name = None

    render_institutional_header()
    render_brand_header(APP_NAME, APP_TAGLINE)

    public_ui = is_public_deployment()
    _sanitize_ui_tab_picks(public=public_ui)

    with st.sidebar:
        st.header("Datos")
        up = st.file_uploader(
            "Subí el Excel de respuestas",
            type=["xlsx", "xls"],
        )
        manual_path = ""
        if not public_ui:
            manual_path = st.text_input(
                "O ruta local al Excel (solo si corrés streamlit en tu PC)",
                value="",
                placeholder="Ej.: /ruta/a/respuestas.xlsx",
                help="En Streamlit Cloud este campo no sirve: usá siempre «Subí el archivo».",
            )
        st.caption(
            "**Nube:** subí el Excel con el botón de arriba; los datos quedan en esta sesión "
            "hasta que pulsás «Quitar archivo»."
            + (
                ""
                if public_ui
                else " Al **cambiar de encuesta**, las pestañas y módulos vuelven a mostrarse todos."
            )
        )

        toggle_hf = st.toggle(
            "Usar modelo de sentimiento robertuito (transformers)",
            value=_HAS_TRANSFORMERS,
            disabled=not _HAS_TRANSFORMERS,
            help=(
                "Sólo disponible si el servidor tiene `transformers`+`torch` (instalación local con requirements-full). "
                "En Streamlit Cloud suele faltar: se usa léxico sin aviso de error."
                if not _HAS_TRANSFORMERS
                else "Primera ejecución descarga pesos (~400 MB). Podés desactivar y usar el léxico."
            ),
        )
        topic_k = st.slider("Cantidad de temas (NMF)", 3, 10, 5)

        st.markdown("---")
        render_institutional_contact()

    load_error: str | None = None
    path_load_warning: str | None = None
    try:
        if up is not None:
            df_new, fname_new = load_table(up, None)
            new_token = f"{fname_new}|{int(df_new.shape[0])}|{int(df_new.shape[1])}|{len(df_new.columns)}"
            if new_token != _dataset_session_token():
                _clear_analysis_ui_state()
                st.session_state._ui_bound_to = None
            st.session_state.loaded_df = df_new
            st.session_state.loaded_name = fname_new
        elif manual_path.strip():
            try:
                df_new, fname_new = load_table(None, manual_path.strip())
                new_token = f"{fname_new}|{int(df_new.shape[0])}|{int(df_new.shape[1])}|{len(df_new.columns)}"
                if new_token != _dataset_session_token():
                    _clear_analysis_ui_state()
                    st.session_state._ui_bound_to = None
                st.session_state.loaded_df = df_new
                st.session_state.loaded_name = fname_new
            except Exception as pe:
                # En la nube una ruta tipo /Users/... falla; no borrar un Excel ya cargado por subida.
                path_load_warning = str(pe)
                if st.session_state.loaded_df is None:
                    st.session_state.loaded_df = None
                    st.session_state.loaded_name = None
                    load_error = path_load_warning
    except Exception as e:
        load_error = str(e)
        st.session_state.loaded_df = None
        st.session_state.loaded_name = None

    if path_load_warning and st.session_state.loaded_df is not None:
        st.sidebar.caption(
            "La ruta del cuadro «O ruta local al Excel» no es legible en este servidor (típico en la nube); "
            "se **mantienen** los datos de la sesión. Usá «Subí el Excel» o corregí la ruta si corrés en tu PC."
        )

    if load_error:
        st.error(f"No se pudo leer el archivo: {load_error}")
        st.info(
            "Si estás en **Streamlit Cloud**, la ruta tipo `/Users/...` **no existe** en el servidor. "
            "Usá **Subí el Excel** en la barra lateral."
        )
        return

    if st.session_state.loaded_df is None:
        if st.session_state.get("_ui_bound_to"):
            _clear_analysis_ui_state()
            st.session_state.pop("_ui_bound_to", None)
        st.info(
            "**Subí el archivo** con el botón «Browse files» en la barra lateral. "
            "En la nube **no funciona** pegar una carpeta local; sólo la subida de archivos."
        )
        with st.expander("Qué análisis cuantitativos suelen usarse en encuestas como la tuya"):
            st.markdown(
                """
- **Distribución de frecuencias y porcentajes** por cada ítem cerrado (categorías, Sí/No, escalas).
- **Moda y percentiles** en escalas ordinales (Likert, frecuencia de uso).
- **Tablas cruzadas** entre dos variables (por ejemplo Unidad Académica × uso de IA), con prueba chi‑cuadrado cuando aplica.
- **Puntajes compuestos**: promedios de subescalas (p. ej. ítems de actitudes hacia la IA) y su fiabilidad (alfa de Cronbach) si tenés bloques homogéneos.
- **Correlaciones** entre escalas o entre uso autodeclarado y actitudes.
- **Comparaciones entre grupos** (año de carrera, género, etc.): pruebas no paramétricas o modelos lineales según supuestos.

Cuando cargues un archivo, esta app incluye **descriptivos, pruebas inferenciales, Alfa de Cronbach, PCA/AFE, clustering, modelos predictivos con SHAP** y un bloque básico de CFA vía `semopy`.
                """
            )
        return

    if _bind_ui_to_dataset():
        st.rerun()

    df = st.session_state.loaded_df
    fname = st.session_state.loaded_name or "datos.xlsx"
    st.success(f"Archivo cargado: **{fname}** — {df.shape[0]} filas × {df.shape[1]} columnas")

    main_tab_opts = main_tabs_for_ui(public=public_ui)
    quant_mod_opts = quant_modules_for_ui(public=public_ui)

    with st.sidebar:
        if public_ui:
            st.caption("Vista pública: análisis listos para usar (sin documentación interna).")
        main_sections = st.multiselect(
            "Pestañas del panel que querés ver",
            main_tab_opts,
            default=main_tab_opts,
            key=_widget_key("pick_main_sections"),
            help="Ocultá lo que no uses para ir directo a lo que necesitás.",
        )
        quant_modules = st.multiselect(
            "Módulos dentro de «Análisis cuantitativo»",
            quant_mod_opts,
            default=quant_mod_opts,
            key=_widget_key("pick_quant_modules"),
            help="Mostrá sólo los análisis que quieras hacer ahora (menos pestañas = más claro).",
        )
        st.markdown("---")
        if st.button("Quitar archivo y reiniciar sesión", type="secondary"):
            st.session_state.loaded_df = None
            st.session_state.loaded_name = None
            st.session_state.pop("_ui_bound_to", None)
            _clear_analysis_ui_state()
            st.rerun()

    profiles = classify_columns(df)
    prof_df = profiles_to_frame(profiles)
    structured = [p for p in profiles if p.kind == "estructurada" and p.n_non_null > 0]
    open_items = [p for p in profiles if p.kind == "abierta" and p.n_non_null > 0]

    all_analysis_cols = [c for c in df.columns if not is_timestamp_column(c)]
    col_labels = build_column_label_map(all_analysis_cols)

    def _fmt_analysis_col(x: str) -> str:
        if x == "(ninguno)":
            return x
        return col_labels.get(x, x)

    _TAB_RENAME = {"Pregunta a la encuesta": "Análisis automático"}
    main_sections = [_TAB_RENAME.get(t, t) for t in main_sections]
    main_ordered = [t for t in MAIN_TABS_ORDER if t in main_sections]
    if not main_ordered:
        st.warning(
            "Elegí al menos una **pestaña principal** en la barra lateral "
            "(«Pestañas del panel que querés ver»)."
        )
        return

    T_main = dict(zip(main_ordered, st.tabs(main_ordered)))

    if "Análisis automático" in T_main:
        with T_main["Análisis automático"]:
            st.subheader("Consultas sobre la encuesta")
            st.caption(
                "Elegí la pregunta del formulario, opcionalmente filtrá la muestra y obtené tablas "
                "con interpretación — sin ir pestaña por pestaña."
            )

            if public_ui:
                qa_mode = "Guiado (recomendado)"
            else:
                qa_mode = st.radio(
                    "Modo",
                    ["Guiado (recomendado)", "Pregunta libre (experimental)"],
                    horizontal=True,
                    key="survey_qa_mode",
                    label_visibility="collapsed",
                )

            if qa_mode.startswith("Guiado"):
                col_choices = build_column_choices(df, profiles)
                if not col_choices:
                    st.warning("No hay columnas analizables en el archivo cargado.")
                else:
                    label_to_choice = {c.label: c for c in col_choices}
                    labels_sorted = sorted(label_to_choice.keys(), key=lambda x: label_to_choice[x].block_id)

                    st.markdown("##### 1. Pregunta del cuestionario")
                    sel_label = st.selectbox(
                        "Columna / ítem",
                        labels_sorted,
                        format_func=lambda x: x,
                        key="guided_primary_label",
                        help="Listado por número de bloque (#) y enunciado completo del ítem.",
                    )
                    choice = label_to_choice[sel_label]
                    st.caption("Enunciado completo")
                    st.write(choice.full_text or choice.label)
                    ic1, ic2, ic3 = st.columns(3)
                    ic1.caption(f"Tipo: **{choice.kind}** · {choice.subtype[:48]}")
                    ic2.caption(f"Respuestas válidas: **{choice.n_valid}**")
                    ic3.caption(f"Bloque **#{choice.block_id}**")

                    st.markdown("##### 2. Filtrar la muestra (opcional)")
                    st.caption("Solo se analizan filas que cumplan **todos** los filtros que marques.")
                    filter_cols = discover_filter_columns(df)
                    cohort_filters: dict[str, list[str]] = {}
                    cohort_labels: dict[str, list[str]] = {}
                    if filter_cols:
                        nf = len(filter_cols)
                        cols_f = st.columns(min(nf, 3))
                        for i, fc in enumerate(filter_cols):
                            with cols_f[i % len(cols_f)]:
                                picked = st.multiselect(
                                    fc.label,
                                    fc.options,
                                    key=f"guided_filter_{fc.column}",
                                )
                                if picked:
                                    cohort_filters[fc.column] = picked
                                    cohort_labels[fc.label] = picked
                    else:
                        st.caption("No se detectaron columnas típicas de filtro en este archivo.")

                    df_cohort = apply_cohort_filters(df, cohort_filters)
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Total encuesta", len(df))
                    m2.metric("Tras filtros", len(df_cohort))
                    m3.metric("% de la muestra", f"{100 * len(df_cohort) / max(len(df), 1):.1f}%")
                    st.markdown(
                        cohort_filter_scope_markdown(
                            filter_cols,
                            cohort_labels,
                            n_cohort=len(df_cohort),
                            n_total=len(df),
                        )
                    )

                    if st.session_state.get("_guided_primary_col") != choice.column:
                        st.session_state.pop("guided_result_bundle", None)
                        st.session_state.pop("guided_secondary_label", None)
                    st.session_state._guided_primary_col = choice.column

                    a_opts = analysis_options_for_column(choice)
                    a_labels = [t[0] for t in a_opts]
                    a_map = {t[0]: t[1] for t in a_opts}

                    st.markdown("##### 3. Tipo de análisis")
                    other_labels = [
                        lb for lb in labels_sorted if label_to_choice[lb].column != choice.column
                    ]

                    sel_an = st.selectbox(
                        "Tipo de análisis",
                        a_labels,
                        key="guided_analysis_pick",
                        help="Si elegís cruce, usá el desplegable de abajo para la segunda pregunta.",
                    )
                    analysis_kind = a_map[sel_an]
                    is_crosstab = analysis_kind == "crosstab"
                    is_count = analysis_kind == "count_values"

                    secondary_col: str | None = None
                    value_pick: list[str] = []
                    sec_label: str | None = None

                    if is_crosstab and not other_labels:
                        st.warning("No hay otra columna para cruzar.")
                    if is_crosstab:
                        st.info(
                            "↓ Elegí la **segunda pregunta** en «Cruzar con» (tabla: filas = paso 1, columnas = paso 2)."
                        )

                    sec_pick = st.selectbox(
                        "Cruzar con (segunda pregunta)",
                        options=other_labels if other_labels else ["(sin otras columnas)"],
                        key="guided_secondary_label",
                        disabled=not is_crosstab or not other_labels,
                        help="Solo activo con «Cruce con otra pregunta (χ²)».",
                    )
                    if is_crosstab and other_labels and sec_pick in label_to_choice:
                        sec_choice = label_to_choice[sec_pick]
                        secondary_col = sec_choice.column
                        sec_label = sec_pick
                        with st.expander("Enunciado de la variable de cruce"):
                            st.write(sec_choice.full_text or sec_choice.label)

                    vals = (
                        df_cohort[choice.column]
                        .dropna()
                        .astype(str)
                        .str.strip()
                        .replace({"nan": ""})
                    )
                    vals = vals[vals.astype(bool)]
                    uniq = vals.value_counts().head(30).index.astype(str).tolist()
                    value_pick = st.multiselect(
                        "Contar categorías (si elegiste «Contar categorías elegidas»)",
                        options=uniq if uniq else ["(sin categorías)"],
                        key="guided_value_pick",
                        disabled=not is_count or not uniq,
                    )

                    run_guided = st.button(
                        "Ver resultados",
                        type="primary",
                        use_container_width=True,
                        key="guided_run_results",
                    )

                    if run_guided:
                        if is_count:
                            value_pick = list(
                                st.session_state.get("guided_value_pick", value_pick or [])
                            )
                        if is_crosstab and not secondary_col:
                            st.warning("Elegí la pregunta con la que querés cruzar.")
                        elif is_count and not value_pick:
                            st.warning("Elegí al menos una categoría para contar.")
                        else:
                            spec = GuidedSpec(
                                primary_column=choice.column,
                                analysis=analysis_kind,
                                secondary_column=secondary_col,
                                cohort_filters=cohort_labels,
                                value_pick=value_pick,
                            )
                            g_res = run_guided_analysis(df, df_cohort, spec)
                            if secondary_col and not sec_label:
                                sec_label = next(
                                    (lb for lb, c in label_to_choice.items() if c.column == secondary_col),
                                    col_labels.get(secondary_col, secondary_col[:60]),
                                )
                            st.session_state.guided_result_bundle = {
                                "g_res": g_res,
                                "spec": spec,
                                "sel_label": sel_label,
                                "sec_label": sec_label,
                                "filter_cols": filter_cols,
                            }

                    st.markdown("---")
                    st.markdown('<div class="guided-results-block">', unsafe_allow_html=True)
                    st.markdown("##### Resultados")

                    bundle = st.session_state.get("guided_result_bundle")
                    if bundle is None:
                        st.caption(
                            "Elegí el tipo de análisis y pulsá **Ver resultados**. "
                            "Las tablas aparecen aquí abajo, sin tapar los controles."
                        )
                    else:
                        g_res = bundle["g_res"]
                        spec = bundle["spec"]
                        sec_label = bundle.get("sec_label")
                        result_filter_cols = bundle.get("filter_cols", filter_cols)

                        if not g_res.ok:
                            st.error(g_res.error or "No se pudo completar el análisis.")
                        else:
                            st.markdown(
                                cohort_filter_scope_markdown(
                                    result_filter_cols,
                                    spec.cohort_filters,
                                    n_cohort=g_res.n_cohort,
                                    n_total=g_res.n_total,
                                )
                            )
                            if g_res.analysis == "count_values":
                                st.metric("Personas que cumplen", g_res.n_result)
                            elif g_res.analysis == "freq":
                                st.metric("Respuestas analizadas", g_res.n_result)

                            for tname, tbl in g_res.tables.items():
                                st.markdown(f"**{tname.replace('_', ' ').title()}**")
                                if tname == "cruce":
                                    row_cap = bundle.get("sel_label", sel_label)
                                    col_cap = sec_label or spec.secondary_column or ""
                                    ms_note = (g_res.metrics.get("chi2") or {}).get(
                                        "multiselect_note"
                                    )
                                    st.caption(
                                        crosstab_table_caption(
                                            row_cap,
                                            col_cap,
                                            multiselect_note=ms_note,
                                        )
                                    )
                                    row_col = (
                                        f"Opción · {short_choice_label(row_cap, max_len=72)}"
                                    )
                                    show_tbl = prepare_crosstab_for_display(
                                        tbl,
                                        index_label=row_col,
                                    )
                                else:
                                    show_tbl = tbl
                                if tname == "cruce":
                                    st.table(show_tbl)
                                else:
                                    st.dataframe(
                                        show_tbl,
                                        use_container_width=True,
                                        hide_index=True,
                                    )
                                if tname == "frecuencias" and not tbl.empty:
                                    ft_plot = tbl[tbl["categoría"].astype(str) != "TOTAL"]
                                    fig = px.bar(
                                        ft_plot.head(15),
                                        x="categoría",
                                        y="frecuencia",
                                        title="Frecuencias (top 15)",
                                    )
                                    fig.update_layout(xaxis_tickangle=-35, height=420)
                                    st.plotly_chart(apply_plotly_style(fig), use_container_width=True)

                            _bloque_interpretacion_cuantitativa(
                                interpret_guided(
                                    spec,
                                    g_res,
                                    col_labels=col_labels,
                                    primary_label=bundle.get("sel_label", sel_label),
                                    secondary_label=sec_label,
                                    filter_cols=result_filter_cols,
                                )
                            )

                            if g_res.tables:
                                first_key = next(iter(g_res.tables))
                                sec_lbl_dl = bundle.get("sec_label") or sec_label
                                sec_full_dl = ""
                                if sec_lbl_dl and sec_lbl_dl in label_to_choice:
                                    sc = label_to_choice[sec_lbl_dl]
                                    sec_full_dl = sc.full_text or sc.label
                                report_csv = build_guided_report_csv(
                                    spec=spec,
                                    result=g_res,
                                    primary_label=bundle.get("sel_label", sel_label),
                                    primary_full_text=choice.full_text or choice.label,
                                    table=g_res.tables[first_key],
                                    table_kind=first_key,
                                    filter_cols=result_filter_cols,
                                    secondary_label=sec_lbl_dl,
                                    secondary_full_text=sec_full_dl or None,
                                )
                                st.download_button(
                                    "Descargar informe (CSV)",
                                    report_csv,
                                    file_name="consulta_guiada.csv",
                                    mime="text/csv",
                                    type="primary",
                                    use_container_width=True,
                                    key="guided_download_csv",
                                )

                    st.markdown("</div>", unsafe_allow_html=True)

            else:
                st.markdown("##### Pregunta en lenguaje natural")
                st.caption(
                    "Experimental: el sistema intenta adivinar columnas y filtros. "
                    "Para resultados exactos usá **modo guiado**."
                )
                question = st.text_area(
                    "Tu pregunta",
                    height=100,
                    placeholder="Ej.: ¿Cuántos de Don Bosco usan IA frecuentemente y no trabajan?",
                    key="survey_qa_question",
                )
                run_q = st.button("Analizar pregunta", type="primary", key="survey_qa_run")

                if run_q and question.strip():
                    plan = plan_question(question.strip(), df, profiles, use_llm=False)
                    result = run_plan(df, plan, profiles)
                    if plan.warnings:
                        for w in plan.warnings:
                            st.warning(w)
                    if result.ok and result.intent == "count_filtered":
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Casos que cumplen", result.n_match)
                        c2.metric("Total", result.n_total)
                        c3.metric("%", f"{result.metrics.get('pct', 0):.1f}%")
                    for name, tbl in result.tables.items():
                        if tbl is not None and not (hasattr(tbl, "empty") and tbl.empty):
                            if name == "cruce":
                                st.table(
                                    prepare_crosstab_for_display(
                                        tbl,
                                        index_label="Opción (pregunta principal)",
                                    )
                                )
                            else:
                                st.dataframe(tbl, use_container_width=True, hide_index=True)
                    _bloque_interpretacion_cuantitativa(
                        interpret_result(plan, result, df, col_labels=col_labels)
                    )
                elif run_q:
                    st.info("Escribí una pregunta.")

            st.caption(
                "Análisis avanzados (PCA, SHAP, clustering, CFA): pestaña **Análisis cuantitativo**. "
                "Temas y sentimiento en texto: **Análisis cualitativo**."
            )

    if "Resumen de ítems" in T_main:
        with T_main["Resumen de ítems"]:
            st.subheader("Clasificación automática")
            st.dataframe(
                prof_df.drop(columns=["_col"], errors="ignore"),
                use_container_width=True,
                hide_index=True,
            )
            c1, c2, c3 = st.columns(3)
            c1.metric("Ítems estructurados", len(structured))
            c2.metric("Ítems abiertos", len(open_items))
            c3.metric("Total analizados", len(profiles))
    
            st.subheader("Detección: escalas ordinales y cantidad de ítems por pregunta")
            st.caption(
                "Agrupamos por el **texto antes del primer corchete** `[` que suelen tener las matrices de Google Forms "
                "(un mismo enunciado, varios sub‑ítems). Luego clasificamos columna por columna con esquema Likert/frecuencia (4 ó 5 niveles)."
            )
            det_ord, blk_ord = detect_survey_ordinals_and_question_blocks(df)
            if not blk_ord.empty:
                b1, b2, b3, b4 = st.columns(4)
                n_bloques = int(blk_ord.shape[0])
                n_ord = int((det_ord["¿ordinal?_auto"] == "Sí").sum()) if not det_ord.empty else 0
                n_col = int(det_ord.shape[0]) if not det_ord.empty else 0
                b1.metric("Bloques pregunta (grupos)", n_bloques)
                b2.metric("Columnas analizadas", n_col)
                b3.metric("Columnas ordinal (auto)", n_ord)
                b4.metric(
                    "Bloques 100% ordinal",
                    int((blk_ord["clasificación"] == "Todos ordinales").sum()),
                )
                st.markdown("##### Por pregunta (bloque)")
                st.dataframe(
                    blk_ord,
                    use_container_width=True,
                    hide_index=True,
                )
                show_det = det_ord.drop(columns=["_columna_interna"], errors="ignore")
                with st.expander("Detalle automático ítem × ítem"):
                    st.dataframe(show_det, use_container_width=True, hide_index=True)
                csv_b = blk_ord.to_csv(index=False).encode("utf-8")
                csv_d = det_ord.to_csv(index=False).encode("utf-8")
                d1, d2 = st.columns(2)
                d1.download_button(
                    "Descargar resumen bloques (CSV)",
                    csv_b,
                    file_name="bloques_pregunta_ordinales.csv",
                    mime="text/csv",
                    type="primary",
                )
                d2.download_button(
                    "Descargar detalle columnas (CSV)",
                    csv_d,
                    file_name="detalle_ordinales_por_columna.csv",
                    mime="text/csv",
                    type="primary",
                )
            else:
                st.info("No hay columnas para analizar (revisá el archivo y la marca temporal).")

    if "Análisis cuantitativo" in T_main:
        with T_main["Análisis cuantitativo"]:
            st.subheader("Análisis cuantitativo")
            timestamp_cols = [c for c in df.columns if is_timestamp_column(c)]
    
            with st.expander("Filtro comparativo (cohorte / fechas)", expanded=False):
                fc1, fc2, fc3 = st.columns(3)
                strata_col = fc1.selectbox(
                    "Filtrar por categoría (opcional)",
                    options=["(ninguno)"] + all_analysis_cols,
                    index=0,
                    format_func=_fmt_analysis_col,
                )
                strata_vals = []
                if strata_col != "(ninguno)":
                    opts = sorted(df[strata_col].dropna().astype(str).unique())
                    strata_vals = fc2.multiselect(
                        "Valores a incluir",
                        options=opts,
                        default=opts[: min(5, len(opts))],
                    )
                date_pick = fc3.selectbox(
                    "Columna de fecha (opcional)",
                    options=["(ninguno)"] + timestamp_cols,
                    index=0,
                    key="date_filter_col",
                    format_func=_fmt_analysis_col,
                )
                df1, dt2 = st.columns(2)
                d_from = df1.date_input("Desde", value=None, key="cmp_from")
                d_to = dt2.date_input("Hasta", value=None, key="cmp_to")
    
            df_work = df
            if strata_col != "(ninguno)" and strata_vals:
                df_work = filter_dataframe_comparison(
                    df_work,
                    strata_col,
                    strata_vals,
                    date_pick if date_pick != "(ninguno)" else None,
                    d_from,
                    d_to,
                )
            elif date_pick != "(ninguno)" and (d_from or d_to):
                df_work = filter_dataframe_comparison(
                    df_work,
                    None,
                    [],
                    date_pick,
                    d_from,
                    d_to,
                )
    
            if len(df_work) < len(df):
                st.caption(f"Submuestra activa: **{len(df_work)}** respondentes (dataset completo {len(df)}).")
    
            with st.expander("Protocolo estadístico: ítems con formulación invertida", expanded=False):
                st.markdown(
                    "Seleccioná **antes** del análisis las columnas Likert formuladas en sentido contrario "
                    "(p. ej. riesgos o impedimentos). Se aplica \\(mín+máx-x\\) con **mín y máx propios por ítem** "
                    "(válido si mezclas escalas de **4 vs 5** categorías o anchuras distintas)."
                )
            invert_pick = st.multiselect(
                "Invertir estos ítems en escalas codificadas",
                options=all_analysis_cols,
                default=[],
                key="inverted_protocol_items",
                format_func=_fmt_analysis_col,
            )
            invert_set: set[str] = set(invert_pick)
    
            q_ord = [m for m in QUANT_MODULE_ORDER if m in quant_modules]
            if not q_ord:
                st.warning(
                    "Elegí al menos un **módulo cuantitativo** en la barra lateral "
                    "(«Módulos dentro de «Análisis cuantitativo»»)."
                )
                Q = {}
            else:
                Q = dict(zip(q_ord, st.tabs(q_ord)))

            structured_work = classify_columns(df_work)
            structured_w = [
                p
                for p in structured_work
                if p.kind == "estructurada"
                and p.n_non_null > 0
                and p.subtype != "sin respuestas"
            ]
    
            # --- Subtab descriptivos ---
            if "1. Descriptivos" in Q:
                with Q["1. Descriptivos"]:
                    if not structured_w:
                        st.warning("No hay ítems estructurados en la submuestra.")
                    else:
                        _sw_names = [p.name for p in structured_w]
                        _sw_lab = build_column_label_map(_sw_names)
                        choice = st.selectbox(
                            "Ítem para descriptivos",
                            options=_sw_names,
                            format_func=lambda x: _sw_lab.get(x, x),
                            key="desc_pick",
                            help="Cada opción muestra «n.» + fragmento distintivo (p. ej. texto tras «[» en matrices Google Forms).",
                        )
                        with st.expander("Texto completo del ítem seleccionado"):
                            st.write(choice)
                        col_series = df_work[choice]
                        prof = next(p for p in structured_w if p.name == choice)
                        multi = st.checkbox(
                            "Separar selección múltiple por comas",
                            value="múltiple" in prof.subtype.lower() or "comas" in prof.subtype.lower(),
                            key="desc_multi",
                        )
                        if multi:
                            exploded = explode_multiselect(col_series)
                            ft = frequency_table(exploded, top_n=40)
                        else:
                            ft = frequency_table(col_series, top_n=40)
        
                        st.markdown("#### Frecuencias y porcentajes")
                        st.dataframe(ft, use_container_width=True, hide_index=True)
                        ft_plot = ft[ft["categoría"].astype(str) != "TOTAL"]
                        fig = px.bar(
                            ft_plot.head(20),
                            x="frecuencia",
                            y="categoría",
                            orientation="h",
                            title="Top categorías",
                        )
                        fig.update_layout(yaxis={"categoryorder": "total ascending"})
                        st.plotly_chart(apply_plotly_style(fig), use_container_width=True)
        
                        desc = descriptive_one_column(col_series, inverted=(choice in invert_set))
                        st.markdown("#### Estadísticos (si el ítem es ordinal reconocible)")
                        mcols = st.columns(4)
                        mcols[0].metric("n válidos", desc["n_no_na"])
                        mcols[1].metric("Categorías", desc["n_categorías"])
                        if desc.get("media") is not None:
                            mcols[2].metric("Media ordinal", f"{desc['media']:.2f}")
                            mcols[3].metric("Mediana", f"{desc['mediana']:.2f}")
                        st.caption(
                            f"Moda: **{desc['moda_etiqueta'][:90]}** — "
                            f"Esquema inferido: {desc.get('esquema_ordinal_inferido') or 'no aplica'}"
                        )
                        if desc.get("desv_std") is not None and desc["desv_std"] == desc["desv_std"]:
                            st.write(
                                f"Desv. estándar: **{desc['desv_std']:.2f}** — "
                                f"Rango [{desc.get('mínimo')}, {desc.get('máximo')}]"
                            )
                        st.download_button(
                            "Descargar frecuencias (CSV)",
                            data=ft.to_csv(index=False).encode("utf-8"),
                            file_name="frecuencias.csv",
                            mime="text/csv",
                            type="primary",
                        )
                        _bloque_interpretacion_cuantitativa(descriptive_explanatory(desc, ft))
        
            # --- χ² ---
            if "2. Cruces + χ²" in Q:
                with Q["2. Cruces + χ²"]:
                    st.markdown("#### Tabla cruzada y Chi-cuadrado")
                    cleft, cright = st.columns(2)
                    rcol = cleft.selectbox(
                        "Variable fila",
                        all_analysis_cols,
                        key="chi_row",
                        format_func=_fmt_analysis_col,
                    )
                    ccol = cright.selectbox(
                        "Variable columna",
                        all_analysis_cols,
                        index=min(1, len(all_analysis_cols) - 1),
                        key="chi_col",
                        format_func=_fmt_analysis_col,
                    )
                    if rcol == ccol:
                        st.warning("Elegí dos variables distintas.")
                    else:
                        out = crosstab_chi_square_smart(df_work, rcol, ccol)
                        if out.get("multiselect_note"):
                            st.info(out["multiselect_note"])
                        row_cap = _fmt_analysis_col(rcol)
                        col_cap = _fmt_analysis_col(ccol)
                        st.caption(
                            crosstab_table_caption(
                                row_cap,
                                col_cap,
                                multiselect_note=out.get("multiselect_note"),
                            )
                        )
                        st.table(
                            prepare_crosstab_for_display(
                                out["tabla"],
                                index_label=f"Opción · {short_choice_label(row_cap, max_len=72)}",
                            )
                        )
                        st.write(
                            f"χ² = {out['chi2']:.3f}, gl = {out['gl']}, p = {out['p_valor']:.4f}, "
                            f"Cramér V = {out['cramers_v']:.3f}, n = {out['n']}"
                        )
                        _bloque_interpretacion_cuantitativa(
                            chi_square_explanatory(
                                chi2=out["chi2"],
                                gl=out["gl"],
                                p_valor=out["p_valor"],
                                cramers_v=out["cramers_v"],
                                n=out["n"],
                                row_lab=_fmt_analysis_col(rcol),
                                col_lab=_fmt_analysis_col(ccol),
                                tabla=out["tabla"],
                            )
                        )
        
            # --- Significancia grupal ---
            if "3. Pruebas de significancia" in Q:
                with Q["3. Pruebas de significancia"]:
                    st.markdown("#### Comparar escala numérica (ordinal inferida) entre grupos")
                    g1, g2 = st.columns(2)
                    ycol = g1.selectbox(
                        "Variable respuesta (ordinal)",
                        all_analysis_cols,
                        key="sig_y",
                        format_func=_fmt_analysis_col,
                    )
                    gcol = g2.selectbox(
                        "Variable de agrupación",
                        all_analysis_cols,
                        key="sig_g",
                        format_func=_fmt_analysis_col,
                    )
                    ynum, _sch = resolve_ordinal_for_group_tests(df_work[ycol], min_cover=0.40)
                    if ycol in invert_set:
                        ynum = invert_ordinal_series(ynum)
                    sub = pd.DataFrame({"y": ynum, "g": df_work[gcol]}).dropna()
                    n_y_ok = int(pd.to_numeric(ynum, errors="coerce").notna().sum())
                    _sch_dsp = str(_sch).replace("\n", " ").strip()
                    if len(_sch_dsp) > 240:
                        _sch_dsp = _sch_dsp[:237] + "…"
                    st.caption(
                        f"Código ordinal efectivo («{_sch_dsp}»): cobertura columnas respuesta antes de fusionar grupo **≈ "
                        f"{100.0 * n_y_ok / max(len(df_work), 1):.1f}%**; filas válidas **y+g** después de quitar vacíos:"
                        f" **{len(sub)}**."
                    )
                    if len(sub) < 12:
                        st.warning(
                            "Pocos casos con codificación ordinal válida y grupo informado después de fusionar datos."
                            " Probá invertir grupo/respuesta (p. ej. **agrupador = Edad** y **ordinal = acceso a PC**, o usar **χ² categoría‑a‑categoría**)."
                        )
                    else:
                        res = compare_numeric_across_groups(sub["y"], sub["g"])
                        st.write("Tamaños de grupo:", res.group_sizes)
                        if res.message:
                            st.caption(res.message)
                        if res.n_groups == 2:
                            st.write(
                                f"**t de Student (Welch)** t = {res.t_stat:.3f}, p = {res.t_p:.4f}  \n"
                                f"**Mann–Whitney U** U = {res.mw_U:.3f}, p = {res.mw_p:.4f}"
                            )
                        anova_txt = (
                            f"**ANOVA** F = {res.anova_F:.4f}, p = {res.anova_p:.4f}"
                            if res.anova_F is not None and res.anova_p is not None
                            else "**ANOVA** no disponible."
                        )
                        kw_txt = (
                            f"**Kruskal–Wallis** H = {res.kruskal_H:.4f}, p = {res.kruskal_p:.4f}"
                            if res.kruskal_H is not None and res.kruskal_p is not None
                            else "**Kruskal–Wallis** no disponible."
                        )
                        st.markdown(anova_txt + "  \n" + kw_txt)
                        _bloque_interpretacion_cuantitativa(
                            group_comparison_explanatory(
                                res,
                                _fmt_analysis_col(ycol),
                                _fmt_analysis_col(gcol),
                                sample=sub,
                            )
                        )
                        sig_csv = build_significance_report_csv(
                            y_label=_fmt_analysis_col(ycol),
                            g_label=_fmt_analysis_col(gcol),
                            ordinal_scheme=_sch_dsp,
                            n_pairs=len(sub),
                            n_work=len(df_work),
                            n_dataset=len(df),
                            res=res,
                            sample=sub,
                            inverted=ycol in invert_set,
                        )
                        st.download_button(
                            "Descargar informe (CSV)",
                            sig_csv,
                            file_name="prueba_significancia.csv",
                            mime="text/csv",
                            type="primary",
                            use_container_width=True,
                            key="sig_test_download_csv",
                        )
        
            # --- Cronbach ---
            if "4. Alfa Cronbach" in Q:
                with Q["4. Alfa Cronbach"]:
                    st.markdown("#### Consistencia interna (Alfa de Cronbach)")
                    cronbach_opts = likert_frequency_column_names(structured_w)
                    if not cronbach_opts:
                        cronbach_opts = [p.name for p in structured_w]
                    st.caption(
                        "Solo se listan ítems detectados como **Likert** o **frecuencia**. "
                        "No uses género, edad ni categorías cerradas sueltas: el α no aplica y rompe la codificación."
                    )
                    _cron_sel_key = _widget_key("cronbach_selected")
                    items_c = pick_likert_columns(
                        cronbach_opts,
                        _fmt_analysis_col,
                        session_key=_cron_sel_key,
                        filter_input_key=_widget_key("cronbach_filter"),
                        select_all_key=_widget_key("cronbach_sel_all"),
                        clear_all_key=_widget_key("cronbach_clear"),
                    )
                    if len(items_c) >= 2:
                        diag_tbl, diag_sum, enc_mat_cron = cronbach_encoding_diagnostics(
                            df_work, items_c, inverted_cols=invert_set
                        )
                        mat = enc_mat_cron.dropna(how="any")
                        rep_cron: pd.DataFrame | None = None
                        warns_cron: list[str] = []
                        alpha_val: float | None = None
                        mat_desc: pd.DataFrame | None = None

                        with st.expander(
                            "Diagnóstico: codificación y superposición (antes del list‑wise)",
                            expanded=len(mat) < 20,
                        ):
                            st.markdown(
                                "**List‑wise** descarta cualquier fila con **codificación incompleta** (texto fuera del diccionario Likert/Frecuencia del panel). "
                                "Si la cobertura de una columna es baja pero el Excel sí tiene texto, esa columna aporta muchos NaN tras mapear — y la intersección colapsa."
                            )
                            st.dataframe(diag_sum, hide_index=True, use_container_width=True)
                            st.dataframe(diag_tbl, hide_index=True, use_container_width=True)

                        ds0 = diag_sum.iloc[0].to_dict() if len(diag_sum) else {}
                        raw_pair_n = int(ds0.get("respuestas_texto_sin_vacio_todas", 0))

                        if len(mat) < 20:
                            st.warning("Muy pocos casos completos tras listwise deletion.")
                            extra = ""
                            if len(mat) == 0 and raw_pair_n > 5:
                                extra = (
                                    f"Las columnas muestran **{raw_pair_n}** personas con texto no vacío en **todas** las preguntas seleccionadas, "
                                    "pero ninguna pasó codificación ordinal en todas: revisá etiquetas típicas (p. ej. frecuencia distinta de «nunca / rara vez / …», "
                                    "opciones cerradas‑largas, múltiple elección)."
                                )
                            elif len(mat) == 0 and raw_pair_n == 0:
                                extra = (
                                    "Prácticamente **nadie** tiene simultáneamente respuesta de texto útil en **todas** las columnas: saltos/lógico del Google Form o columnas muy faltantes."
                                )
                            _bloque_interpretacion_cuantitativa(
                                f"Hay **{len(mat)}** filas completas sobre **{mat.shape[1]}** ítems (solo casos donde **todas** las escalas quedaron mapeadas a número). "
                                "Con pocas personas en esa intersección, el **α de Cronbach** fluctúa mucho; el panel oculta el resultado destacado. "
                                "**No indica necesariamente un fallo**: suele venir de mezclas de tipo de ítem / etiquetas fuera del diccionario / omisión combinada entre columnas.\n\n"
                                + extra
                                + ("\n\n" if extra else "")
                                + "Preferí **homogeneizar opciones Likert‑like**, filtrar cohortes donde el bloque sea completo, o usar otros bloques cuando corresponda."
                            )
                        else:
                            rep_cron, warns_cron = ordinal_scaling_report(mat)
                            st.markdown("##### Escala efectiva por ítem")
                            st.dataframe(rep_cron, use_container_width=True, hide_index=True)
                            for w in warns_cron:
                                st.info(w)
                            alpha_val = cronbach_alpha(mat)
                            if np.isnan(alpha_val):
                                st.warning(
                                    "α no es calculable con esta matriz (pocas filas completas, varianza total nula o ítems casi constantes tras codificar)."
                                )
                            else:
                                st.metric(
                                    "Alfa de Cronbach",
                                    f"{alpha_val:.3f}",
                                    help="Con mezclas 4 vs 5 categorías interpretá con cautela si no pertenecen al mismo bloque teórico.",
                                )
                            st.caption(f"Casos usados: {len(mat)} — ítems: {mat.shape[1]}")
                            mat_desc = mat.describe().T
                            st.dataframe(mat_desc, use_container_width=True)
                            _bloque_interpretacion_cuantitativa(
                                cronbach_explanatory(
                                    alpha_val, len(mat), mat.shape[1], warns_cron, mat=mat
                                )
                            )

                        cron_csv = build_cronbach_report_csv(
                            item_labels=[_fmt_analysis_col(c) for c in items_c],
                            n_work=len(df_work),
                            n_dataset=len(df),
                            diag_sum=diag_sum,
                            diag_tbl=diag_tbl,
                            alpha=alpha_val if mat.shape[0] >= 20 else None,
                            n_cases=len(mat),
                            n_items=mat.shape[1],
                            rep_cron=rep_cron,
                            mat_describe=mat_desc,
                            warnings=warns_cron,
                        )
                        st.download_button(
                            "Descargar informe (CSV)",
                            cron_csv,
                            file_name="alfa_cronbach.csv",
                            mime="text/csv",
                            type="primary",
                            use_container_width=True,
                            key="cronbach_download_csv",
                        )
                    else:
                        st.info("Seleccioná al menos dos ítems Likert/frecuencia del mismo bloque.")
        
            # --- PCA / AFE ---
            if "5. PCA / AFE" in Q:
                with Q["5. PCA / AFE"]:
                    st.markdown("#### Componentes principales + análisis factorial exploratorio")
                    pca_opts = likert_frequency_column_names(structured_w)
                    if not pca_opts:
                        pca_opts = [p.name for p in structured_w]
                    st.caption(
                        "Solo ítems **Likert/frecuencia** del mismo bloque (p. ej. usos de IA). "
                        "No uses género, edad ni trabajo: no son escalas ordinales y dejan 0 casos completos."
                    )
                    items_p = pick_likert_columns(
                        pca_opts,
                        _fmt_analysis_col,
                        session_key=_widget_key("pca_selected"),
                        filter_input_key=_widget_key("pca_filter"),
                        select_all_key=_widget_key("pca_sel_all"),
                        clear_all_key=_widget_key("pca_clear"),
                    )
                    use_poly = st.checkbox(
                        "Usar correlaciones policóricas (semopy / hetcor) para PCA y AFE",
                        value=_HAS_SEMOPY,
                        disabled=not _HAS_SEMOPY,
                        help="Mejor coherencia ordinal. En Cloud suele estar desactivado (sin semopy). Local: pip install -r requirements-full.txt",
                    )
                    if not _HAS_SEMOPY:
                        st.caption("En este servidor no está instalado **semopy**; PCA/AFE usan método clásico. CFA con semopy también queda omitido hasta instalar dependencias extras.")
                    latent_lavaan = st.text_input("Nombre ejemplo del factor latente (export lavaan)", value="FactUtil", key="lav_lat")
                    if len(items_p) < 3:
                        st.info("Seleccioná al menos tres ítems correlacionados conceptualmente.")
                    else:
                        n_items = len(items_p)
                        max_dims = max(3, n_items)
                        n_pc = _safe_int_slider(
                            "Dimensiones PCA",
                            min_value=2,
                            max_value=min(12, max_dims),
                            default=min(6, max_dims),
                            key="slider_pca_dims",
                        )
                        max_factors = min(8, n_items - 1)
                        nf = _safe_int_slider(
                            "Factores AFE",
                            min_value=2,
                            max_value=max(2, max_factors),
                            default=min(4, max(2, max_factors)),
                            key="slider_efa_factors",
                        )
                        if n_items < 4:
                            st.caption(
                                "Con **3 ítems** el AFE admite como máximo **2 factores**; "
                                "para elegir más factores, incluí al menos **4** columnas del mismo bloque."
                            )
                        diag_tbl_p, diag_sum_p, enc_mat_p = cronbach_encoding_diagnostics(
                            df_work, items_p, inverted_cols=invert_set
                        )
                        Xnum = enc_mat_p.dropna(how="any")
                        min_cases_pca = max(10, 3 * n_items)
                        with st.expander(
                            "Diagnóstico de codificación por ítem",
                            expanded=len(Xnum) < min_cases_pca,
                        ):
                            st.dataframe(diag_sum_p, use_container_width=True)
                            st.dataframe(diag_tbl_p, use_container_width=True, hide_index=True)

                        rep_pca = pd.DataFrame()
                        warns_pca: list[str] = []
                        if len(Xnum) > 0:
                            rep_pca, warns_pca = ordinal_scaling_report(Xnum)
                        elif not enc_mat_p.empty:
                            rep_pca, warns_pca = ordinal_scaling_report(enc_mat_p)

                        st.markdown("##### Escala efectiva por ítem (mezclas 4 vs 5 categorías)")
                        if not rep_pca.empty:
                            st.dataframe(rep_pca, use_container_width=True, hide_index=True)
                        for w in warns_pca:
                            st.info(w)

                        out_load_pca: pd.DataFrame | None = None
                        out_var_pca: list[float] | None = None
                        out_load_efa: pd.DataFrame | None = None
                        out_eig: list[float] | None = None
                        pca_status = "No ejecutado"

                        if len(Xnum) == 0:
                            st.error(
                                "Ningún encuestado tiene **todos** los ítems codificados (intersección list-wise = 0). "
                                "Revisá el diagnóstico: elegí ítems del **mismo bloque** y con cobertura suficiente."
                            )
                            _bloque_interpretacion_cuantitativa(
                                f"Seleccionaste **{n_items}** ítems; **0** encuestados con datos completos en ese bloque."
                            )
                            pca_status = "Sin casos list-wise"
                        elif len(Xnum) < min_cases_pca:
                            st.error(
                                f"Solo **{len(Xnum)}** casos completos; se requieren al menos **{min_cases_pca}** "
                                f"para PCA/AFE con {n_items} ítems."
                            )
                            _bloque_interpretacion_cuantitativa(
                                f"**{len(Xnum)}** encuestados con datos completos; insuficiente para el mínimo ({min_cases_pca})."
                            )
                            pca_status = f"Casos insuficientes ({len(Xnum)} < {min_cases_pca})"
                        else:
                            if len(Xnum) < 40:
                                st.warning(
                                    f"**{len(Xnum)}** casos completos (menos de 40): interpretá los factores como exploratorios."
                                )
                            pca_status = "Ejecutado"
                            n_pc_eff = min(int(n_pc), Xnum.shape[1])
                            nf_eff = min(int(nf), max(2, Xnum.shape[1] - 1))
                            lab_ld = loading_row_choice_labels(items_p)
                            ran_poly = False
                            if use_poly:
                                try:
                                    with st.spinner("Calculando matriz policórica (pairwise ordinal)..."):
                                        R_poly = polychoric_correlation_matrix(Xnum.astype(float), nearest=True)
                                    ran_poly = True
                                    loadings_pca, var_pc = pca_loadings_from_correlation_matrix(R_poly, n_pc_eff)
                                    st.success("PCA y AFE basados en matriz policórica (PD aprox.).")
                                    st.markdown("##### Varianza explicada (PCA sobre correlaciones policóricas)")
                                    st.bar_chart(
                                        pd.Series(var_pc, index=[f"PC{i+1}" for i in range(len(var_pc))])
                                    )
                                    st.markdown("##### Cargas PCA")
                                    st.dataframe(loadings_pca.round(3), use_container_width=True)
                                    load_efa, eig = run_efa_from_correlation_matrix(R_poly, n_factors=nf_eff)
                                    st.markdown("##### Cargas AFE rotadas (Varimax, entrada = R policórica)")
                                    st.dataframe(load_efa.round(3), use_container_width=True)
                                    if eig is not None and eig[0] is not None:
                                        ev = np.asarray(eig[0]).ravel()
                                        st.caption("Autovalores (AFE): " + ", ".join(f"{v:.2f}" for v in ev[: min(8, ev.size)]))
                                    rel_r, sane_names = relabel_corr_for_export(R_poly)
                                    st.download_button(
                                        "Descargar matriz para lavaan (`cor_poly.csv`)",
                                        data=rel_r.to_csv(encoding="utf-8"),
                                        file_name="cor_poly.csv",
                                        mime="text/csv",
                                        type="primary",
                                    )
                                    st.code(lavaan_export_snippet(latent_lavaan, sane_names, len(Xnum)), language="r")
                                    with st.expander("Matriz policórica (vista rápida, nombres originales abreviados)"):
                                        st.dataframe(R_poly.round(4), use_container_width=True)
                                    _bloque_interpretacion_cuantitativa(
                                        pca_explanatory(
                                            loadings_pca,
                                            var_pc,
                                            len(Xnum),
                                            method="policórica",
                                            row_labels=lab_ld,
                                        )
                                        + "\n\n---\n\n"
                                        + efa_explanatory(
                                            load_efa,
                                            eig,
                                            len(Xnum),
                                            nf_eff,
                                            method_note=(
                                                "Rotación **Varimax**, factores desde **correlaciones policóricas** "
                                                "(mejor vínculo con ítems ordinales; requiere **semopy**)."
                                            ),
                                            row_labels=lab_ld,
                                        )
                                    )
                                    _bloque_lectura_academica_factores(
                                        academic_exploratory_factor_reading(
                                            selected_columns=items_p,
                                            row_labels_matrix_index=lab_ld,
                                            loadings_pca=loadings_pca,
                                            var_ratio=var_pc,
                                            loadings_efa=load_efa,
                                            eig=eig,
                                            n_factors_requested=nf_eff,
                                            n_obs=len(Xnum),
                                            pca_engine_description="PCA sobre correlaciones policóricas aprox.",
                                            efa_engine_description=(
                                                "AFE (minres / principal desde R policórico) rotado ortogonalmente (Varimax)"
                                            ),
                                        )
                                    )
                                    out_load_pca = loadings_pca
                                    out_var_pca = [float(v) for v in np.asarray(var_pc).ravel()]
                                    out_load_efa = load_efa
                                    if eig is not None and eig[0] is not None:
                                        out_eig = [float(v) for v in np.asarray(eig[0]).ravel()[:20]]
                                    pca_status = "Policórica (PCA + AFE)"
                                except Exception as exc:
                                    st.warning(f"No se pudo usar la policórica ({exc}). Se muestra método clásico (Pearson/sklearn).")
                                    ran_poly = False
                            if not ran_poly:
                                _scores, loadings, var = run_pca_with_loadings(
                                    Xnum, n_components=n_pc_eff
                                )
                                st.markdown("##### Varianza explicada (PCA clásico, datos tipificados)")
                                st.bar_chart(pd.Series(var, index=[f"PC{i+1}" for i in range(len(var))]))
                                st.markdown("##### Cargas PCA")
                                st.dataframe(loadings.round(3), use_container_width=True)
                                try:
                                    load_efa, eig, _ = run_efa(Xnum, n_factors=nf_eff)
                                    st.markdown("##### Cargas AFE rotadas (Varimax, datos continuos estándar)")
                                    st.dataframe(load_efa.round(3), use_container_width=True)
                                    if eig[0] is not None:
                                        ev_fallback = np.asarray(eig[0]).ravel()
                                        st.caption(
                                            "Autovalores (AFE): "
                                            + ", ".join(f"{v:.2f}" for v in ev_fallback[: min(8, ev_fallback.size)])
                                        )
                                    _bloque_interpretacion_cuantitativa(
                                        pca_explanatory(
                                            loadings,
                                            var,
                                            len(Xnum),
                                            method="PCA clásico",
                                            row_labels=lab_ld,
                                        )
                                        + "\n\n---\n\n"
                                        + efa_explanatory(
                                            load_efa,
                                            eig,
                                            len(Xnum),
                                            nf_eff,
                                            method_note=(
                                                "**Varimax**, factores tras estandarización de respuestas (tratamiento ordinal continuado)."
                                            ),
                                            row_labels=lab_ld,
                                        )
                                    )
                                    _bloque_lectura_academica_factores(
                                        academic_exploratory_factor_reading(
                                            selected_columns=items_p,
                                            row_labels_matrix_index=lab_ld,
                                            loadings_pca=loadings,
                                            var_ratio=var,
                                            loadings_efa=load_efa,
                                            eig=eig,
                                            n_factors_requested=nf_eff,
                                            n_obs=len(Xnum),
                                            pca_engine_description="PCA estándar (pearson después de tipificar respuestas).",
                                            efa_engine_description=(
                                                "AFE (factor_analyzer, principal/minres típico) + Varimax en datos tipificados"
                                            ),
                                        )
                                    )
                                    out_load_pca = loadings
                                    out_var_pca = [float(v) for v in np.asarray(var).ravel()]
                                    out_load_efa = load_efa
                                    if eig[0] is not None:
                                        out_eig = [float(v) for v in np.asarray(eig[0]).ravel()[:20]]
                                    pca_status = "Clásico (PCA + AFE)"
                                except Exception as exc:
                                    st.warning(f"AFE no convergió o faltan datos: {exc}")
                                    _bloque_interpretacion_cuantitativa(
                                        pca_explanatory(
                                            loadings,
                                            var,
                                            len(Xnum),
                                            method="PCA clásico",
                                            row_labels=lab_ld,
                                        )
                                        + "\n\n*AFE omitido*: revisá errores previos en pantalla "
                                        "(versiones de paquetes, casos incompletos, varianzas nulas) o ejecutá sólo PCA."
                                    )
                                    _bloque_lectura_academica_factores(
                                        academic_exploratory_factor_reading(
                                            selected_columns=items_p,
                                            row_labels_matrix_index=lab_ld,
                                            loadings_pca=loadings,
                                            var_ratio=var,
                                            loadings_efa=None,
                                            eig=None,
                                            n_factors_requested=nf_eff,
                                            n_obs=len(Xnum),
                                            pca_engine_description="PCA estándar (Pearson después de tipificar respuestas).",
                                            efa_engine_description=(
                                                "AFE omitido tras error (ver mensaje técnico en pantalla)"
                                            ),
                                        )
                                    )
                                    out_load_pca = loadings
                                    out_var_pca = [float(v) for v in np.asarray(var).ravel()]
                                    pca_status = "Clásico (solo PCA; AFE omitido)"

                        pca_csv = build_pca_efa_report_csv(
                            item_labels=[_fmt_analysis_col(c) for c in items_p],
                            n_work=len(df_work),
                            n_dataset=len(df),
                            n_pc_requested=int(n_pc),
                            n_factors_requested=int(nf),
                            latent_name=latent_lavaan,
                            use_poly=use_poly,
                            diag_sum=diag_sum_p,
                            diag_tbl=diag_tbl_p,
                            n_complete=len(Xnum),
                            rep_pca=rep_pca if not rep_pca.empty else None,
                            scale_warnings=warns_pca or None,
                            loadings_pca=out_load_pca,
                            var_pca=out_var_pca,
                            loadings_efa=out_load_efa,
                            eigenvalues=out_eig,
                            status_note=pca_status,
                        )
                        st.download_button(
                            "Descargar informe (CSV)",
                            pca_csv,
                            file_name="pca_afe.csv",
                            mime="text/csv",
                            type="primary",
                            use_container_width=True,
                            key="pca_download_csv",
                        )
        
            # --- Clustering ---
            if "6. Clustering" in Q:
                with Q["6. Clustering"]:
                    st.markdown("#### Segmentación (K-means, DBSCAN, jerárquico)")
                    feat_c = st.multiselect(
                        "Variables para perfiles",
                        options=all_analysis_cols,
                        key="clust_feat",
                        format_func=_fmt_analysis_col,
                        help="Podés usar **una** variable (segmentación 1D: p. ej. acceso sí/no o Likert) o varias para perfiles multivariados.",
                    )
                    mode = st.radio("Algoritmo", ["K-means", "DBSCAN", "Jerárquico (dendrograma)"], horizontal=True)
                    if len(feat_c) == 1:
                        st.caption(
                            "**Una sola variable:** el clúster opera en **una dimensión** (la codificación ordinal o dummies de esa columna). "
                            "Tiene sentido para cortar la muestra en grupos a lo largo de ese eje; agregá más variables si buscás perfiles **multivariados**."
                        )
                    if len(feat_c) >= 1:
                        Xf, expl, _ = prepare_feature_matrix(df_work, feat_c, inverted_cols=invert_set)
                        enc_notes = [f"{k[:60]}: {v}" for k, v in list(expl.items())[:12]]
                        st.caption("Codificación: " + " | ".join(enc_notes[:6]))
                        clust_status = "No ejecutado"
                        clust_vc: pd.DataFrame | None = None
                        clust_centers: pd.DataFrame | None = None
                        clust_inertia: float | None = None
                        clust_noise: float | None = None
                        clust_k: int | None = None
                        clust_eps: float | None = None
                        clust_ms: int | None = None
                        clust_hints = ""
                        clust_interp = ""
                        n_clust_obs = 0

                        if Xf.empty:
                            st.error("No se pudo construir la matriz de rasgos (revisá cardinalidades).")
                            clust_status = "Matriz vacía"
                        else:
                            Xf = Xf.astype(float).fillna(Xf.median(numeric_only=True))
                            n_clust_obs = len(Xf)
                            if mode == "K-means":
                                k = st.slider("k (grupos)", 2, 9, 3)
                                clust_k = k
                                lbl, centers, inertia, _ = kmeans_profiles(Xf, k=k)
                                clust_inertia = inertia
                                clust_centers = centers.round(2)
                                st.metric("Inercia final", f"{inertia:,.1f}")
                                st.dataframe(clust_centers, use_container_width=True)
                                vc = add_total_count_row(
                                    lbl.value_counts()
                                    .sort_index()
                                    .rename_axis("cluster")
                                    .reset_index(name="n"),
                                    label_col="cluster",
                                    value_col="n",
                                )
                                clust_vc = vc
                                st.dataframe(vc, hide_index=True)
                                clust_hints = kmeans_cluster_reading_hints(
                                    centers,
                                    vc,
                                    df_source=df_work,
                                    feat_columns=feat_c,
                                    feat_display_labels=[_fmt_analysis_col(c) for c in feat_c],
                                    inverted_cols=invert_set,
                                )
                                with st.expander(
                                    "**Clúster 0 vs 1 vs 2:** qué significan y cómo nombrarlos",
                                    expanded=True,
                                ):
                                    st.markdown(clust_hints)
                                clust_interp = clustering_explanatory(
                                    "K-means",
                                    k=k,
                                    inertia=inertia,
                                    vc=vc,
                                    n_feats=len(feat_c),
                                    n_obs=len(Xf),
                                )
                                _bloque_interpretacion_cuantitativa(clust_interp)
                                clust_status = "K-means ejecutado"
                            elif mode == "DBSCAN":
                                eps = st.slider("eps", 0.3, 2.5, 0.85, step=0.05)
                                ms = st.slider("min_samples", 3, 20, 7)
                                clust_eps = eps
                                clust_ms = ms
                                lbl, noise_rate, _ = dbscan_profiles(Xf, eps, ms)
                                clust_noise = noise_rate
                                st.metric("Observaciones ruido (-1)", f"{noise_rate*100:.1f}%")
                                clust_vc = add_total_count_row(
                                    lbl.value_counts().rename_axis("cluster").reset_index(name="n"),
                                    label_col="cluster",
                                    value_col="n",
                                )
                                st.dataframe(clust_vc, hide_index=True)
                                clust_interp = clustering_explanatory(
                                    "DBSCAN",
                                    noise_rate=noise_rate,
                                    n_feats=len(feat_c),
                                    n_obs=len(Xf),
                                )
                                _bloque_interpretacion_cuantitativa(clust_interp)
                                clust_status = "DBSCAN ejecutado"
                            else:
                                st.warning("Jerárquico: sólo muestra hasta 120 respondentes seleccionados al azar (legibilidad).")
                                samp = Xf.sample(min(120, len(Xf)), random_state=7)
                                n_clust_obs = len(samp)
                                fig = hierarchical_linkage_plot(samp)
                                st.pyplot(fig)
                                plt.close(fig)
                                clust_interp = clustering_explanatory(
                                    "Jerárquico (dendrograma)",
                                    n_feats=len(feat_c),
                                    n_obs=len(samp),
                                )
                                _bloque_interpretacion_cuantitativa(clust_interp)
                                clust_status = "Dendrograma (muestra aleatoria)"

                        clust_csv = build_clustering_report_csv(
                            algorithm=mode,
                            feature_labels=[_fmt_analysis_col(c) for c in feat_c],
                            n_work=len(df_work),
                            n_dataset=len(df),
                            n_obs=n_clust_obs,
                            encoding_notes=enc_notes,
                            k=clust_k,
                            eps=clust_eps,
                            min_samples=clust_ms,
                            inertia=clust_inertia,
                            noise_rate=clust_noise,
                            cluster_counts=clust_vc,
                            centers=clust_centers,
                            reading_hints=clust_hints,
                            interpretation=clust_interp,
                            status_note=clust_status,
                        )
                        st.download_button(
                            "Descargar informe (CSV)",
                            clust_csv,
                            file_name="clustering.csv",
                            mime="text/csv",
                            type="primary",
                            use_container_width=True,
                            key="clustering_download_csv",
                        )
                    else:
                        st.info("Elegí al menos **una** variable para segmentar.")
        
            # --- Predictivos ---
            if "7. Predictivos + SHAP" in Q:
                with Q["7. Predictivos + SHAP"]:
                    st.markdown("#### Modelos predictivos + interpretabilidad SHAP (tipo Shapley)")
                    st.caption(
                        "**SHAP** permite ver **contribución marginal** por variable sobre el modelo elegido "
                        "(gráfico de barras + tabla de pesos relativos en la muestra de test). Si el entorno "
                        "**no tiene** instalado `shap`, igual podés usar el **árbol de decisión** más abajo."
                        + (" **Paquete `shap` detectado.**" if _HAS_SHAP else "")
                    )
                    target = st.selectbox(
                        "Variable objetivo (categoría a predecir)",
                        all_analysis_cols,
                        key="tgt",
                        format_func=_fmt_analysis_col,
                    )
                    feats = st.multiselect(
                        "Predictores",
                        options=[c for c in all_analysis_cols if c != target],
                        default=[],
                        key="pred_feats",
                        format_func=_fmt_analysis_col,
                    )
                    shap_pick = st.selectbox(
                        "Modelo para explicación SHAP",
                        ["Random Forest", "Regresión logística", "Árbol de decisión", "XGBoost"],
                    )
                    if len(feats) >= 2:
                        Xm, expl, Xm_enc_map = prepare_feature_matrix(df_work, feats, inverted_cols=invert_set)
                        y_series = df_work[target].astype(str)
                        if Xm.empty:
                            st.error("Matriz predictores vacía.")
                        else:
                            Xm = Xm.astype(float).fillna(Xm.median())
                            Xm = Xm.loc[y_series.notna()].copy()
                            y_series = y_series.loc[Xm.index]
                            try:
                                res, _ = fit_predictive_suite(Xm, y_series)
                                pred_acc_tbl = pd.DataFrame(
                                    [{"modelo": k, "accuracy_val": round(v["accuracy"], 3)} for k, v in res.items()]
                                )
                                st.dataframe(
                                    pred_acc_tbl,
                                    hide_index=True,
                                    use_container_width=True,
                                )
                                if shap_pick not in res and shap_pick == "XGBoost":
                                    st.caption("XGBoost omitido si no está disponible.")
                                model_key = shap_pick if shap_pick in res else next(iter(res))
                                mcidx = None
                                if hasattr(res[model_key]["encoder"], "classes_") and len(res[model_key]["encoder"].classes_) > 2:
                                    mcidx = st.slider(
                                        "Clase SHAP (índice)",
                                        0,
                                        len(res[model_key]["encoder"].classes_) - 1,
                                        0,
                                    )
                                X_te = res[model_key]["X_test"]
                                sample_rows = min(400, len(X_te))
                                Xs = X_te.sample(sample_rows, random_state=17)
                                shap_mostro = False
                                if _HAS_SHAP:
                                    try:
                                        st.caption(
                                            "El gráfico resume **columnas que entran al modelo** (cada nivel one‑hot u ordinal por separado). "
                                            "**Abajo**, la tabla *Por pregunta del cuestionario* suma esos niveles bajo **la misma pregunta** original."
                                        )
                                        st.markdown("##### Resumen visual SHAP (barras por columna modelo)")
                                        fig, tabla_shap = shap_diagnostic_bundle(
                                            res[model_key]["model"],
                                            Xs,
                                            multiclass_class=mcidx,
                                            top_n_tabla=96,
                                        )
                                        st.pyplot(fig)
                                        plt.close(fig)
                                        tabla_preg = aggregate_shap_table_by_question(
                                            tabla_shap,
                                            Xm_enc_map,
                                            format_source=_fmt_analysis_col,
                                        )
                                        st.markdown(
                                            "##### Por pregunta del cuestionario (peso relativo agregando niveles dicotómicos / ordinal)"
                                        )
                                        st.caption(
                                            "Se **suman** los **|SHAP| medio** de todas las ramas codificadas de una misma pregunta Excel y los "
                                            "**contribución_relativa_%** se **renormalizan a 100 %** sobre las preguntas listadas "
                                            "(lectura orientativa, no causa)."
                                        )
                                        st.dataframe(
                                            tabla_preg,
                                            hide_index=True,
                                            use_container_width=True,
                                        )
                                        st.download_button(
                                            label="Descargar SHAP agrupado por pregunta (.csv)",
                                            data=tabla_preg.to_csv(index=False).encode("utf-8"),
                                            file_name="shap_importancia_por_pregunta.csv",
                                            mime="text/csv",
                                            type="primary",
                                            key="dl_shap_by_question",
                                            help="Filas fusionadas desde la tabla detallada; misma muestra que el gráfico.",
                                        )
                                        with st.expander(
                                            "Detalle por columna del modelo (cada nivel one‑hot u ordinal)",
                                            expanded=False,
                                        ):
                                            st.caption(
                                                "Los **%** siguen ponderando **solo** entre columnas modelo (son los que aparecen en barras)."
                                            )
                                            st.dataframe(
                                                tabla_shap,
                                                hide_index=True,
                                                use_container_width=True,
                                            )
                                            st.download_button(
                                                label="Descargar tabla SHAP detalle por columna (.csv)",
                                                data=tabla_shap.to_csv(index=False).encode("utf-8"),
                                                file_name="shap_importancia_por_columna_modelo.csv",
                                                mime="text/csv",
                                                type="primary",
                                                key="dl_shap_rel_pct",
                                                help="Misma muestra que el gráfico (subconjunto del conjunto de test).",
                                            )
                                        shap_mostro = True
                                    except Exception as exc:
                                        st.warning(f"SHAP omitido: {exc}")
                                else:
                                    st.info(
                                        "**Sin paquete `shap`** en esta instalación. "
                                        "En el despliegue estándar del repo viene en `requirements.txt`; "
                                        "si igual no aparece, localmente podés ejecutar `pip install shap` "
                                        "o `pip install -r requirements-full.txt`. "
                                        "Mientras tanto usá **Árbol de decisión — figura y reglas** más abajo."
                                    )

                                if "Árbol de decisión" in res:
                                    with st.expander("**Árbol de decisión** — figura y reglas (`sklearn`, sin SHAP)", expanded=True):
                                        dtp = res["Árbol de decisión"]
                                        enc_dt = dtp["encoder"]
                                        cl_nom = [str(x) for x in enc_dt.classes_]
                                        ddepth = st.slider(
                                            "Profundidad máxima en el dibujo",
                                            min_value=2,
                                            max_value=10,
                                            value=5,
                                            key="viz_dt_depth",
                                            help="Acortá si tenés muchas categorías objetivo y el gráfico se satura.",
                                        )
                                        try:
                                            fdt = plot_decision_tree_figure(
                                                dtp["model"],
                                                list(dtp["features"]),
                                                cl_nom,
                                                max_depth=ddepth,
                                            )
                                            st.pyplot(fdt)
                                            plt.close(fdt)
                                        except Exception as exc:
                                            st.warning(f"No se pudo dibujar el árbol: {exc}")
                                        try:
                                            rules = decision_tree_rules_text(dtp["model"], list(dtp["features"]))
                                            st.download_button(
                                                "Descargar reglas del árbol (.txt)",
                                                data=rules.encode("utf-8"),
                                                file_name="arbol_decision_reglas.txt",
                                                mime="text/plain",
                                                type="primary",
                                            )
                                            with st.expander("Ver reglas en texto (primeras líneas)"):
                                                st.code(rules[:8000] + ("…" if len(rules) > 8000 else ""), language="text")
                                        except Exception as exc:
                                            st.caption(f"Exportación texto del árbol no disponible: {exc}")

                                n_cls = len(res[model_key]["encoder"].classes_)
                                interp_pred = predictive_explanatory(
                                    pred_acc_tbl,
                                    model_key if model_key else shap_pick,
                                    n_clases_objetivo=int(n_cls),
                                    shap_disponible=_HAS_SHAP and shap_mostro,
                                )
                                if interp_pred:
                                    _bloque_interpretacion_cuantitativa(interp_pred)
                                    acad_pred = predictive_academic_explanatory(
                                        objetivo_etiqueta=_fmt_analysis_col(target),
                                        predictor_etiquetas=[_fmt_analysis_col(c) for c in feats],
                                        n_muestra=int(len(Xm)),
                                        n_columnas_codificadas=int(Xm.shape[1]),
                                        n_clases=int(n_cls),
                                        accuracy_por_modelo=pred_acc_tbl,
                                        explicacion_codificacion=expl,
                                    )
                                    if acad_pred:
                                        _bloque_lectura_academica_predictivos(acad_pred)
                            except Exception as exc:
                                st.error(str(exc))
                    else:
                        st.info("Seleccioná al menos dos predictores.")
        
            # --- CFA semopy ---
            if "8. CFA – semopy" in Q:
                with Q["8. CFA – semopy"]:
                    st.markdown("#### CFA simple (un factor latente)")
                    lat = st.text_input("Nombre del factor latente (sin espacios raros)", value="CompetDig")
                    cfa_items = st.multiselect(
                        "Índicadores observados",
                        options=all_analysis_cols,
                        key="cfa_items",
                        format_func=_fmt_analysis_col,
                    )
                    if len(cfa_items) >= 3:
                        model, tabla, err = optional_sem_estimate(
                            df_work, lat, cfa_items, inverted_cols=invert_set
                        )
                        if model is None:
                            st.warning(err or "No se pudo estimar el CFA.")
                            msg_cfa = str(err or "No se pudo estimar.")
                            _bloque_interpretacion_cuantitativa(
                                f"**CFA no ejecutado:** {msg_cfa[:380]}"
                                "\n\nEn instalaciones mínimas (p. ej. Community Cloud sin `semopy`), usá CFA localmente con `-r requirements-full.txt` "
                                "o bien exportá la matriz de correlaciones hacia **lavaan**/R."
                            )
                        else:
                            st.success("Modelo estimado.")
                            st.dataframe(tabla.head(), use_container_width=True)
                            try:
                                from semopy.stats import calc_stats  # noqa: PLC0415
        
                                stat_df = calc_stats(model)
                                st.dataframe(stat_df, use_container_width=True)
                            except Exception as exc:
                                st.caption(f"Métricas globales desde semopy no disponibles: {exc}")
                            _bloque_interpretacion_cuantitativa(cfa_explanatory_short())
                    else:
                        st.info("Seleccioná tres o más ítems para especificar la ecuación de medición.")
        
            if "9. Notas metodológicas" in Q:
                with Q["9. Notas metodológicas"]:
                    st.markdown(
                        """
        **Protocolo de ítems invertidos:** documentá y marcá en el expander superior las columnas con redacción invertida; el mismo criterio se aplica a Alfa, factores, CFA, comparaciones y segmentación (con **min/max por ítem**, compatible con mezclas 4 vs 5 categorías).
        
        **Escalas 4 vs 5 categorías:** el motor compara etiquetas texto Likert **de cuatro y cinco niveles** (y variantes cortas de frecuencias) y elige la mejor cobertura; en Cronbach/AFE verás una **tabla de diagnóstico** si combinás ítems heterogéneos.
        
        **Policórico + lavaan:** PCA y AFE pueden basarse en **`semopy.polycorr.hetcor`** (matriz semi‑definida proyectada con `corr_nearest`). El CSV `cor_poly.csv` y el ejemplo de **lavaan** son orientativos — validá `sample.nobs` (= casos tras listwise deletion) y el tipo de estimador (p. ej. WLSMV con `ordered`) con tu asesor estadístico.
        
        También están descriptivos, cruces χ², pruebas clásicas, Cronbach, clustering, modelos predictivos + **SHAP**, y **CFA de un factor** en `semopy`.
        
        **SEM complejo** sigue siendo más defendible en **lavaan**, **SmartPLS** o **AMOS**. **Longitudinal:** por ahora sólo **filtros** cohorte/fecha.
                        """
                    )
        
    if "Análisis cualitativo" in T_main:
        with T_main["Análisis cualitativo"]:
            st.subheader("Respuestas abiertas: temas, tono y lectura del discurso")
            st.caption(
                "El **análisis temático** profundo y el **análisis de discurso** (en sentido escolar) son "
                "interpretativos y suelen exigir codificación. Acá tenés **apoyos automáticos** (NMF, n‑gramas, concordancias) "
                "y polaridad por léxico o modelo neuronal si está instalado."
            )
            if not open_items:
                st.warning("No hay columnas marcadas como abiertas con datos.")
            else:
                _oi_names = [p.name for p in open_items]
                _oi_lab = build_column_label_map(_oi_names)
                oc = st.selectbox(
                    "Columna abierta",
                    options=_oi_names,
                    format_func=lambda x: _oi_lab.get(x, x),
                    help="«n.» indica el orden en el archivo; el texto tras «[» suele ser el subítem de la matriz.",
                )
                q_label = _oi_lab.get(oc, oc)
                texts = df[oc].dropna().astype(str).tolist()

                filtered = [t.strip() for t in texts if len(t.strip()) > 4]

                qa1, qa2, qa3 = st.tabs(
                    [
                        "1. Análisis temático (NMF)",
                        "2. Sentimiento",
                        "3. Discurso y vocabulario",
                    ]
                )

                with qa1:
                    st.markdown("##### Exploración temática (NMF + TF‑IDF)")
                    st.caption(
                        "Agrupa palabras que co‑ocurren; **etiquetá vos** cada tema para el informe. "
                        "Revisá las citas debajo de cada tema."
                    )
                    topics, _W, dominant, quotes, texts_nmf = thematic_nmf(filtered, n_topics=topic_k)
                    if topics:
                        st.dataframe(pd.DataFrame(topics), use_container_width=True, hide_index=True)
                        dom_ser = pd.Series(dominant, name="tema_asignado")
                        st.markdown("###### Frecuencia de respuestas por tema (dominante)")
                        st.bar_chart(dom_ser.value_counts().sort_index())
                        st.caption(f"Respuestas incluidas en el modelo: **{len(texts_nmf)}** (se excluyen vacías o demasiado cortas).")
                        for tid, exs in quotes.items():
                            with st.expander(f"Tema {tid} — palabras clave y citas representativas"):
                                kw = next((t["palabras_clave"] for t in topics if t["tema"] == tid), "")
                                if kw:
                                    st.caption(kw)
                                for j, ex in enumerate(exs, 1):
                                    st.markdown(f"**{j}.** {ex[:520]}{'…' if len(ex) > 520 else ''}")
                        st.download_button(
                            "Descargar asignación tentativa tema→respuesta (CSV)",
                            data=pd.DataFrame({"texto": texts_nmf, "tema_dominante_nmf": dominant})
                            .to_csv(index=False)
                            .encode("utf-8"),
                            file_name="temas_nmf_por_respuesta.csv",
                            mime="text/csv",
                            type="primary",
                        )
                        st.markdown("---")
                        st.markdown(
                            deep_thematic_markdown(
                                q_label,
                                topics,
                                dominant,
                                quotes,
                                texts_nmf,
                            )
                        )
                    else:
                        st.info(
                            "No se extrajeron temas estables: pocas respuestas largas, texto muy repetido o "
                            "vocabulario demasiado disperso. Probá más respuestas o bajá la cantidad de temas en la barra lateral."
                        )
                        st.markdown("---")
                        st.markdown(
                            deep_thematic_markdown(
                                q_label,
                                [],
                                [],
                                {},
                                [],
                            )
                        )

                with qa2:
                    st.markdown("##### Polaridad / tono (orientativo)")
                    if not _HAS_TRANSFORMERS:
                        st.info(
                            "En este servidor **no está instalado** `transformers` (típico en Streamlit Community Cloud). "
                            "La polaridad usa el **léxico en español** integrado. Para RoBERTuito instala dependencias pesadas en local: "
                            "`pip install -r requirements-full.txt`."
                        )
                    results: list[str] = []
                    hf_ok = False
                    if toggle_hf and _HAS_TRANSFORMERS:
                        try:
                            _load_sentiment_pipeline()
                            preds = SentimentModel.predict_batch(filtered)
                            for pred in preds:
                                label_raw = pred.get("label", "NEU")
                                results.append(SentimentModel.map_label(str(label_raw)))
                            hf_ok = len(results) == len(filtered)
                        except Exception as e:
                            st.warning(
                                "No se pudo usar el modelo Hugging Face; se usará el léxico en español. "
                                f"Detalle: {e}"
                            )
                    if not hf_ok or len(results) != len(filtered):
                        results = [lexicon_sentiment_es(t)[0] for t in filtered]

                    dist = pd.Series(results).value_counts().rename_axis("sentimiento").reset_index(name="n")
                    total_n = int(dist["n"].sum())
                    dist["pct"] = (dist["n"] / total_n * 100).round(1) if total_n else 0.0
                    dist = add_total_count_row(dist, label_col="sentimiento", value_col="n")
                    dist.loc[dist["sentimiento"] == "TOTAL", "pct"] = 100.0

                    c_sent1, c_sent2 = st.columns(2)
                    with c_sent1:
                        st.dataframe(dist, use_container_width=True, hide_index=True)
                        fig2 = px.pie(dist, names="sentimiento", values="n", hole=0.35)
                        st.plotly_chart(apply_plotly_style(fig2), use_container_width=True)
                    with c_sent2:
                        with st.expander("Ejemplos aleatorios por tono (léxico o modelo)"):
                            samp = pd.DataFrame({"texto": filtered, "sentimiento": results})
                            for lab in ["positivo", "neutral", "negativo"]:
                                pool = samp.loc[samp["sentimiento"] == lab, "texto"]
                                if pool.empty:
                                    continue
                                k = min(5, len(pool))
                                sub = pool.sample(k, random_state=1)
                                st.markdown(f"**{lab.capitalize()}**")
                                for row in sub:
                                    st.write(f"- {row[:400]}…" if len(row) > 400 else f"- {row}")

                    out = pd.DataFrame({"texto": filtered, "sentimiento": results})
                    st.download_button(
                        "Descargar clasificación de sentimiento (CSV)",
                        data=out.to_csv(index=False).encode("utf-8"),
                        file_name="sentimiento_abiertas.csv",
                        mime="text/csv",
                        type="primary",
                    )
                    used_hf = hf_ok and toggle_hf and _HAS_TRANSFORMERS
                    metodo_sent = (
                        "modelo neuronal RoBERTuito (Hugging Face)"
                        if used_hf
                        else "léxico en español basado en listas orientativas"
                    )
                    st.markdown("---")
                    st.markdown(
                        deep_sentiment_markdown(
                            q_label,
                            filtered,
                            results,
                            dist,
                            metodo_sent,
                        )
                    )

                with qa3:
                    st.markdown("##### Apoyos para lectura del discurso")
                    st.caption(
                        "Bigramas/trigramas y **concordancias** (KWIC) sirven para ver patrones léxicos; "
                        "no constituyen por sí solos un análisis de discurso epistémico completo."
                    )
                    g1, g2 = st.columns(2)
                    bi = ngram_top_table(filtered, ngram_range=(2, 2), top_n=40)
                    tri = ngram_top_table(filtered, ngram_range=(3, 3), top_n=35)
                    with g1:
                        st.markdown("**Bigramas frecuentes**")
                        if bi.empty:
                            st.caption("Sin bigramas repetidos suficientes.")
                        else:
                            st.dataframe(bi, use_container_width=True, hide_index=True)
                    with g2:
                        st.markdown("**Trigramas frecuentes**")
                        if tri.empty:
                            st.caption("Sin trigramas repetidos suficientes.")
                        else:
                            st.dataframe(tri, use_container_width=True, hide_index=True)

                    needle = st.text_input(
                        "Buscar palabra o frase (concordancias en contexto)",
                        placeholder="ej. plagio, copiar, ética, miedo",
                    )
                    kwic_hits: list[str] = []
                    if needle.strip():
                        kwic_hits = kwic_snippets(filtered, needle.strip(), max_hits=35)
                        if not kwic_hits:
                            st.caption("Sin coincidencias (probá otra forma o menos caracteres).")
                        else:
                            st.markdown(f"**Coincidencias ({len(kwic_hits)})**")
                            for h in kwic_hits:
                                st.markdown(f"- {h}")

                    st.markdown("---")
                    st.markdown(
                        deep_discourse_markdown(
                            q_label,
                            filtered,
                            bi,
                            tri,
                            needle or "",
                            kwic_hits,
                        )
                    )

    if "Guía metodológica" in T_main:
        with T_main["Guía metodológica"]:
            st.markdown(
                """
### Cobertura de la pestaña *Análisis cuantitativo*

1. **Descriptivos** (frecuencias, porcentajes, media/mediana/desv. cuando la escala ordinal se reconoce).
2. **Pruebas de significancia**: χ², t de Student (Welch), Mann–Whitney, ANOVA, Kruskal–Wallis.
3. **Alfa de Cronbach** sobre bloques Likert codificados.
4. **Análisis factorial**: PCA más AFE exploratorio rotado Varimax (`factor_analyzer`).
5. **Clustering**: K‑means, DBSCAN, dendrograma jerárquico.
6. **Modelos predictivos** multinivel (accuracy en hold‑out): logística, árboles, Random Forest, XGBoost.
7. **XAI**: gráficos SHAP tipo *summary bar*.
8. **CFA factor único** vía `semopy` — modelos estructurales completos siguen mejor en lavaan/SmartPLS/AMOS.
9. **Comparativo/longitudinal inicial**: filtros por categorías y fechas (marca temporal) sobre la muestra antes de cualquier modelo.

### Análisis cualitativos en esta app

- **Temático (NMF)**: temas exploratorios, frecuencias por tema y citas; descarga CSV de asignación tentativa. No reemplaza codificación manual ni categorías teóricas.
- **Sentimiento**: **RoBERTuito** si instalás `transformers`+`torch` (local / `requirements-full`); en Cloud suele usarse sólo **léxico** en español.
- **Discurso y vocabulario**: bigramas/trigramas y concordancias KWIC como apoyo a la lectura; un análisis de discurso pleno sigue siendo trabajo interpretativo fuera de la app.

### Próximo paso sugerido

Exportá CSV desde acá y subí el proyecto a GitHub (`git init`, `.gitignore` ya ignora `.xlsx` por defecto; podés sacar esa línea si querés versionar datos anonimizados).
                """
            )

    with st.sidebar:
        st.markdown("---")
        st.caption(f"Hojas disponibles tras lectura única — filas útiles: {len(df)}")
        cols_ts = [c for c in df.columns if not is_timestamp_column(c)]
        st.caption(f"Columnas (sin marca temporal): {len(cols_ts)}")


if __name__ == "__main__":
    main()
