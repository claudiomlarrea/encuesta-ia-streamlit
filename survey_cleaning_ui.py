"""UI Streamlit para la pestaña de limpieza de datos."""
from __future__ import annotations

from typing import Callable

import pandas as pd
import streamlit as st

from survey_cleaning import (
    BUILTIN_COHERENCE_RULES,
    GARBAGE_KIND_LABELS,
    build_flagged_rows_export,
    dataset_quality_overview,
    garbage_summary_by_type,
    guess_age_columns,
    infer_text_columns_for_junk,
    quality_summary_table,
    scan_coherence,
    scan_garbage_responses,
    scan_numeric_outliers,
)


def render_data_cleaning_tab(
    df: pd.DataFrame,
    *,
    format_col: Callable[[str], str],
    widget_key: Callable[[str], str],
) -> None:
    st.subheader("Limpieza y control de calidad")
    st.caption(
        "Revisá la planilla **antes** del análisis: faltantes, incoherencias entre ítems, valores "
        "numéricos fuera de rango y **respuestas basura** (tecleteo, insultos, copy-paste, relleno). "
        "Todo es **heurístico** — validá casos dudosos antes de excluir filas."
    )

    overview = dataset_quality_overview(df)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Filas", overview["filas"])
    m2.metric("Columnas", overview["columnas"])
    m3.metric("Filas duplicadas (exactas)", overview["filas_duplicadas_exactas"])
    m4.metric("Columnas vacías", overview["columnas_totalmente_vacías"])

    text_cols_default = infer_text_columns_for_junk(df)

    id_opts = ["(ninguna)"] + [c for c in df.columns if not c.lower().startswith("marca")]
    id_col = st.selectbox(
        "Columna identificadora (opcional, para localizar filas)",
        options=id_opts,
        index=0,
        format_func=lambda x: format_col(x) if x != "(ninguna)" else x,
        key=widget_key("clean_id_col"),
    )
    row_id = None if id_col == "(ninguna)" else id_col

    age_guess = guess_age_columns(list(df.columns))
    default_age = age_guess[0] if age_guess else "(ninguna)"
    col_pick = st.selectbox(
        "Columna numérica para aberrantes (edad, etc.)",
        options=["(ninguna)"] + [c for c in df.columns],
        index=(
            (["(ninguna)"] + list(df.columns)).index(default_age)
            if default_age in df.columns
            else 0
        ),
        format_func=lambda x: format_col(x) if x != "(ninguna)" else x,
        key=widget_key("clean_outlier_col"),
    )
    o1, o2 = st.columns(2)
    min_age = int(o1.number_input("Mínimo plausible", value=16, min_value=0, max_value=120))
    max_age = int(o2.number_input("Máximo plausible", value=100, min_value=1, max_value=130))

    tab_calidad, tab_coherencia, tab_aberrantes, tab_basura = st.tabs(
        [
            "Calidad de la planilla",
            "Coherencia entre ítems",
            "Valores aberrantes",
            "Respuestas basura",
        ]
    )

    with tab_calidad:
        st.markdown("##### Completitud por columna")
        qdf = quality_summary_table(df)
        st.dataframe(qdf, use_container_width=True, hide_index=True)
        st.download_button(
            "Descargar resumen de calidad (CSV)",
            qdf.to_csv(index=False).encode("utf-8"),
            file_name="calidad_columnas.csv",
            mime="text/csv",
            key=widget_key("clean_quality_csv"),
        )
        high_miss = qdf[qdf["%_faltante"] >= 50]
        if not high_miss.empty:
            st.warning(
                f"{len(high_miss)} columna(s) con **≥50 %** de respuestas faltantes. "
                "Podrían ser ítems opcionales o errores de exportación."
            )

    with tab_coherencia:
        st.markdown("##### Reglas automáticas (encuestas sobre IA y tecnología)")
        for rule in BUILTIN_COHERENCE_RULES:
            st.markdown(f"- **{rule.name}:** {rule.description} *Ej.: {rule.example}*")

        enabled_ids = st.multiselect(
            "Reglas a aplicar",
            options=[r.rule_id for r in BUILTIN_COHERENCE_RULES],
            default=[r.rule_id for r in BUILTIN_COHERENCE_RULES],
            format_func=lambda rid: next(r.name for r in BUILTIN_COHERENCE_RULES if r.rule_id == rid),
            key=widget_key("clean_coherence_rules"),
        )
        active_rules = tuple(r for r in BUILTIN_COHERENCE_RULES if r.rule_id in enabled_ids)

        coherence = scan_coherence(df, active_rules, row_id_column=row_id)
        st.metric("Pares incoherentes detectados", len(coherence))

        if coherence.empty:
            st.success(
                "No se detectaron incoherencias con las reglas activas. "
                "Si esperabas casos, revisá que los enunciados del Excel contengan palabras clave "
                "relacionadas (IA, ChatGPT, computadora, etc.)."
            )
        else:
            show = coherence.copy()
            if "identificador" in show.columns:
                cols_order = [
                    "fila_excel",
                    "identificador",
                    "regla",
                    "columna_a",
                    "respuesta_a",
                    "columna_b",
                    "respuesta_b",
                    "detalle",
                ]
                show = show[[c for c in cols_order if c in show.columns]]
            st.dataframe(show, use_container_width=True, hide_index=True)
            st.caption(
                "Una misma fila puede aparecer varias veces si hay más de un par de columnas conflictivas."
            )
            st.download_button(
                "Descargar incoherencias (CSV)",
                coherence.to_csv(index=False).encode("utf-8"),
                file_name="incoherencias_encuesta.csv",
                mime="text/csv",
                type="primary",
                key=widget_key("clean_coherence_csv"),
            )

    with tab_aberrantes:
        st.markdown("##### Rangos numéricos plausibles")
        st.caption("Usá los controles de columna y rango que están arriba de las pestañas.")

        outliers = pd.DataFrame()
        if col_pick != "(ninguna)":
            outliers = scan_numeric_outliers(
                df,
                col_pick,
                min_value=float(min_age),
                max_value=float(max_age),
            )
        st.metric("Valores fuera de rango", len(outliers))

        if col_pick == "(ninguna)":
            st.info("Elegí una columna (por ejemplo **Edad**) para buscar valores aberrantes.")
        elif outliers.empty:
            st.success(f"No hay valores numéricos fuera de [{min_age}, {max_age}] en esa columna.")
        else:
            st.dataframe(outliers, use_container_width=True, hide_index=True)
            st.download_button(
                "Descargar aberrantes (CSV)",
                outliers.to_csv(index=False).encode("utf-8"),
                file_name="valores_aberrantes.csv",
                mime="text/csv",
                key=widget_key("clean_outlier_csv"),
            )

    with tab_basura:
        st.markdown("##### Respuestas automáticas, basura o copy-paste")
        st.caption(
            "Se analizan ítems de **texto libre** (y columnas con respuestas largas heterogéneas). "
            "No se revisan escalas Likert cerradas."
        )

        if not text_cols_default:
            st.warning(
                "No se detectaron columnas de texto libre. Podés forzar columnas abajo "
                "o revisar que el Excel tenga respuestas abiertas con suficiente longitud."
            )

        with st.expander("Columnas que se escanean por defecto", expanded=False):
            if text_cols_default:
                for c in text_cols_default:
                    st.markdown(f"- {format_col(c)}")
            else:
                st.caption("(ninguna detectada)")

        forced = st.multiselect(
            "Agregar columnas al escaneo",
            options=[c for c in df.columns if c not in text_cols_default],
            default=[],
            format_func=format_col,
            key=widget_key("clean_garbage_extra_cols"),
        )
        scan_cols = list(dict.fromkeys(text_cols_default + list(forced)))

        g1, g2, g3 = st.columns(3)
        kinds_on = g1.multiselect(
            "Tipos de alerta",
            options=list(GARBAGE_KIND_LABELS.keys()),
            default=list(GARBAGE_KIND_LABELS.keys()),
            format_func=lambda k: GARBAGE_KIND_LABELS[k],
            key=widget_key("clean_garbage_kinds"),
        )
        cp_min_len = int(
            g2.number_input(
                "Mín. caracteres (copy-paste)",
                min_value=25,
                max_value=200,
                value=40,
                key=widget_key("clean_cp_len"),
            )
        )
        cp_min_rep = int(
            g3.number_input(
                "Mín. repeticiones (copy-paste)",
                min_value=2,
                max_value=50,
                value=3,
                key=widget_key("clean_cp_rep"),
            )
        )

        garbage = scan_garbage_responses(
            df,
            scan_cols if scan_cols else None,
            copy_paste_min_len=cp_min_len,
            copy_paste_min_occurrences=cp_min_rep,
            row_id_column=row_id,
            check_insults="insulto" in kinds_on,
            check_random="caracteres_aleatorios" in kinds_on,
            check_nonsense="texto_sin_sentido" in kinds_on,
            check_absurd="respuesta_absurda" in kinds_on,
            check_copy_paste=(
                "copy_paste_repetido" in kinds_on or "copy_paste_en_fila" in kinds_on
            ),
        )
        if kinds_on:
            garbage = garbage[garbage["tipo_alerta"].isin(kinds_on)]

        n_alertas = len(garbage)
        n_filas = garbage["fila_excel"].nunique() if not garbage.empty else 0
        b1, b2 = st.columns(2)
        b1.metric("Alertas de basura", n_alertas)
        b2.metric("Filas con al menos una alerta", n_filas)

        if garbage.empty:
            st.success(
                "No se detectaron respuestas basura con la configuración actual. "
                "Si esperabas casos, probá bajar el umbral de copy-paste o agregar columnas."
            )
        else:
            summary = garbage_summary_by_type(garbage)
            st.markdown("##### Resumen por tipo")
            st.dataframe(
                summary[["etiqueta", "casos"]],
                use_container_width=True,
                hide_index=True,
            )

            show_g = garbage.copy()
            show_g["tipo"] = show_g["tipo_alerta"].map(
                lambda k: GARBAGE_KIND_LABELS.get(k, k)
            )
            cols_show = [
                c
                for c in [
                    "fila_excel",
                    "identificador",
                    "tipo",
                    "columna",
                    "respuesta",
                    "detalle",
                ]
                if c in show_g.columns or c == "tipo"
            ]
            st.markdown("##### Detalle")
            st.dataframe(
                show_g[cols_show],
                use_container_width=True,
                hide_index=True,
            )
            st.download_button(
                "Descargar respuestas basura (CSV)",
                garbage.to_csv(index=False).encode("utf-8"),
                file_name="respuestas_basura.csv",
                mime="text/csv",
                type="primary",
                key=widget_key("clean_garbage_csv"),
            )

    st.markdown("---")
    st.markdown("##### Exportar filas marcadas")
    coherence_all = scan_coherence(df, tuple(BUILTIN_COHERENCE_RULES))
    out_col = col_pick if col_pick != "(ninguna)" else ""
    outliers_all = (
        scan_numeric_outliers(df, out_col, min_value=float(min_age), max_value=float(max_age))
        if out_col
        else pd.DataFrame()
    )
    garbage_all = scan_garbage_responses(df)
    flagged = build_flagged_rows_export(df, coherence_all, outliers_all, garbage_all)
    if flagged.empty:
        st.caption("No hay filas marcadas con las reglas por defecto.")
    else:
        st.caption(f"{len(flagged)} fila(s) con al menos una alerta (columna `_alertas_limpieza`).")
        st.dataframe(flagged.head(50), use_container_width=True)
        st.download_button(
            "Descargar filas marcadas (CSV)",
            flagged.to_csv(index=False).encode("utf-8"),
            file_name="filas_con_alertas_limpieza.csv",
            mime="text/csv",
            type="primary",
            key=widget_key("clean_flagged_csv"),
        )
