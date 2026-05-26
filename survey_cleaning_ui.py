"""UI Streamlit para la pestaña de limpieza de datos.

Los escaneos pesados NO usan ``st.cache_data`` con ``DataFrame`` (hash del Excel cada rerun puede
congelar la app). Solo se ejecutan con botón explícito o trabajo barato/al acotado.
"""
from __future__ import annotations

from typing import Callable

import pandas as pd
import streamlit as st

from survey_intel import ColumnProfile

from survey_cleaning import (
    BUILTIN_COHERENCE_RULES,
    GARBAGE_KIND_LABELS,
    build_flagged_rows_export,
    column_values_look_like_career_year,
    dataset_quality_overview,
    garbage_summary_by_type,
    guess_age_columns,
    infer_text_columns_for_junk,
    quality_summary_table,
    scan_coherence,
    scan_garbage_responses,
    scan_numeric_outliers,
)

_ALL_RULE_IDS = tuple(r.rule_id for r in BUILTIN_COHERENCE_RULES)


def render_data_cleaning_tab(
    df: pd.DataFrame,
    *,
    format_col: Callable[[str], str],
    widget_key: Callable[[str], str],
    column_profiles: list[ColumnProfile] | None = None,
) -> None:
    st.subheader("Limpieza y control de calidad")
    st.caption(
        "Revisá la planilla **antes** del análisis: faltantes, incoherencias entre ítems, valores "
        "numéricos fuera de rango y **respuestas basura** (tecleteo, insultos, copy-paste, relleno). "
        "Todo es **heurístico** — validá casos dudosos antes de excluir filas."
    )

    active_key = widget_key("clean_module_on")
    if not st.session_state.get(active_key):
        st.warning(
            "Para que la app **no se cuelgue** al cargar el Excel, la limpieza pesada queda "
            "**apagada** hasta que la actives. El resto del panel (cruces, descriptivos, etc.) "
            "sigue funcionando."
        )
        if st.button(
            "Activar limpieza de datos",
            type="primary",
            key=widget_key("clean_turn_on"),
        ):
            st.session_state[active_key] = True
            st.rerun()
        return

    overview = dataset_quality_overview(df)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Filas", overview["filas"])
    m2.metric("Columnas", overview["columnas"])
    dup_disp = overview.get("filas_duplicadas_exactas")
    if dup_disp is None:
        m3.metric("Filas duplicadas (exactas)", "—", help="Omitido en datasets muy grandes (ahorra RAM).")
    else:
        m3.metric("Filas duplicadas (exactas)", int(dup_disp))
    m4.metric("Columnas vacías", overview["columnas_totalmente_vacías"])

    text_cols_key = widget_key("clean_text_cols")
    text_cols_default: list[str] = st.session_state.get(text_cols_key, [])

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
        "Columna para revisar edad u otro número (años cumplidos, horas, etc.)",
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
    min_age = int(
        o1.number_input(
            "Mínimo plausible (p. ej. edad 16)",
            value=16,
            min_value=0,
            max_value=120,
            help="Rango pensado para **edad en años**, no para «1º año de la carrera».",
        )
    )
    max_age = int(
        o2.number_input(
            "Máximo plausible (p. ej. edad 100)",
            value=100,
            min_value=1,
            max_value=130,
        )
    )

    tab_calidad, tab_coherencia, tab_aberrantes, tab_basura = st.tabs(
        [
            "Calidad de la planilla",
            "Coherencia entre ítems",
            "Valores aberrantes",
            "Respuestas basura",
        ]
    )

    outliers = pd.DataFrame()

    with tab_calidad:
        st.markdown("##### Completitud por columna")
        if df.shape[0] * df.shape[1] > 2_000_000:
            st.warning(
                "Planilla muy grande: la tabla de completitud puede tardar. Podés ejecutarla abajo "
                "y mientras esperá usar otras pestañas en la siguiente recarga si hace falta."
            )
        if st.button(
            "Generar tabla de completitud por columna",
            type="primary",
            key=widget_key("clean_run_quality_tbl"),
        ):
            st.session_state[widget_key("clean_quality_cached")] = quality_summary_table(df)

        qdf = st.session_state.get(widget_key("clean_quality_cached"))
        if qdf is None:
            st.info(
                "Pulsá **Generar tabla de completitud** para ver faltantes y valores únicos por columna "
                "(así evitamos trabajar con el archivo entero hasta que vos lo pidas)."
            )
        else:
            st.dataframe(qdf, width="stretch", hide_index=True)
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
            options=list(_ALL_RULE_IDS),
            default=list(_ALL_RULE_IDS),
            format_func=lambda rid: next(r.name for r in BUILTIN_COHERENCE_RULES if r.rule_id == rid),
            key=widget_key("clean_coherence_rules"),
        )

        active_rules = tuple(r for r in BUILTIN_COHERENCE_RULES if r.rule_id in enabled_ids)

        st.warning(
            "La coherencia compara **muchos ítems × filas** y puede tardar **varios minutos**. "
            "Solo corre al pulsar el botón."
        )
        if st.button(
            "Ejecutar revisión de coherencia",
            type="primary",
            key=widget_key("clean_run_coherence_btn"),
        ):
            sig = "|".join(sorted(enabled_ids)) + "|" + (row_id or "")
            cache_store = widget_key("clean_coh_store")
            with st.spinner("Revisando coherencia entre ítems…"):
                st.session_state[cache_store] = (sig, scan_coherence(df, active_rules, row_id_column=row_id))

        cache_store = widget_key("clean_coh_store")
        coh_bundle = st.session_state.get(cache_store)
        expect_sig = "|".join(sorted(enabled_ids)) + "|" + (row_id or "")

        coherence: pd.DataFrame | None = None
        coherence_stale = False
        if isinstance(coh_bundle, tuple) and len(coh_bundle) == 2:
            sig_exp, coherence_df = coh_bundle
            if sig_exp != expect_sig:
                coherence_stale = True
            else:
                coherence = coherence_df

        if coh_bundle is None:
            st.info(
                "Pulsá **Ejecutar revisión de coherencia**. Con muchos ítems y filas "
                "puede tardar; el navegador puede parecer quieta hasta que termine."
            )
        elif coherence_stale:
            st.caption("Cambiaron reglas o columna ID: pulsá **Ejecutar revisión de coherencia** otra vez.")
        elif coherence is None or coherence.empty:
            st.metric("Pares incoherentes detectados", 0)
            st.success(
                "No se detectaron incoherencias con las reglas activas. "
                "Si esperabas casos, revisá que los encabezados contengan palabras clave (IA, uso, ChatGPT…)."
            )
        else:
            st.metric("Pares incoherentes detectados", len(coherence))
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
            st.dataframe(show, width="stretch", hide_index=True)
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
        st.caption(
            "Sirve para detectar **edad** (u otro número continuo) fuera de un rango que definas. "
            "**No** aplica a «1º año / 2º año de la carrera»: esas son categorías ordinales, no edad."
        )
        if col_pick != "(ninguna)" and column_values_look_like_career_year(df, col_pick):
            st.error(
                f"La columna **{format_col(col_pick)}** parece ser **año de la carrera**, no edad. "
                "Elegí la pregunta de **edad** (si existe) o dejá el mínimo/máximo acorde al ítem "
                "(p. ej. 1–6 solo si el ítem es realmente numérico)."
            )

        out_store = widget_key("clean_outlier_store")
        if st.button(
            "Buscar valores aberrantes",
            type="primary",
            key=widget_key("clean_run_outliers_btn"),
            disabled=col_pick == "(ninguna)",
        ):
            outliers = scan_numeric_outliers(
                df, col_pick, min_value=float(min_age), max_value=float(max_age)
            )
            st.session_state[out_store] = (
                f"{col_pick}|{min_age}|{max_age}",
                outliers,
            )

        out_bundle = st.session_state.get(out_store)
        outliers = pd.DataFrame()
        if isinstance(out_bundle, tuple) and len(out_bundle) == 2:
            sig_o, outliers = out_bundle
            if sig_o != f"{col_pick}|{min_age}|{max_age}":
                outliers = pd.DataFrame()
                st.caption("Cambiaste columna o rango: volvé a **Buscar valores aberrantes**.")

        st.metric("Valores fuera de rango", len(outliers))

        if col_pick == "(ninguna)":
            st.info("Elegí una columna (por ejemplo **Edad**) para buscar valores aberrantes.")
        elif out_bundle is None:
            st.info("Pulsá **Buscar valores aberrantes**.")
        elif outliers.empty:
            if col_pick != "(ninguna)" and column_values_look_like_career_year(df, col_pick):
                st.info(
                    "No se aplicó rango de edad a esta columna (parece **año de carrera**). "
                    "Cambiá de columna si querés revisar edad."
                )
            else:
                st.success(
                    f"No hay valores numéricos (edad u otro número interpretable) "
                    f"fuera de [{min_age}, {max_age}] en esa columna."
                )
        else:
            st.dataframe(outliers, width="stretch", hide_index=True)
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

        if st.button(
            "Identificar columnas de texto a revisar",
            key=widget_key("clean_detect_text_cols"),
        ):
            with st.spinner("Detectando ítems abiertos…"):
                st.session_state[text_cols_key] = infer_text_columns_for_junk(
                    df, column_profiles
                )
                text_cols_default = st.session_state[text_cols_key]

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
        scan_cols = tuple(dict.fromkeys(text_cols_default + list(forced)))

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

        junk_sig_key = widget_key("clean_junk_sig")
        kinds_sorted = "|".join(sorted(kinds_on))
        st.session_state[junk_sig_key] = "|".join(
            [
                kinds_sorted,
                str(cp_min_len),
                str(cp_min_rep),
                ",".join(scan_cols),
                row_id or "",
            ]
        )

        st.warning(
            "El escaneo de texto recorre **todas las filas** por columna seleccionada. "
            "En encuestas grandes puede tardar; solo corre al pulsar el botón."
        )
        if st.button(
            "Escanear respuestas basura / copy-paste",
            type="primary",
            key=widget_key("clean_run_garbage_btn"),
        ):
            kinds = set(kinds_on)
            junk_store = widget_key("clean_garbage_store")
            sig_ev = st.session_state[junk_sig_key]
            with st.spinner("Escaneando respuestas de texto…"):
                gb = scan_garbage_responses(
                    df,
                    list(scan_cols) if scan_cols else None,
                    copy_paste_min_len=cp_min_len,
                    copy_paste_min_occurrences=cp_min_rep,
                    row_id_column=row_id,
                    check_insults="insulto" in kinds,
                    check_random="caracteres_aleatorios" in kinds,
                    check_nonsense="texto_sin_sentido" in kinds,
                    check_absurd="respuesta_absurda" in kinds,
                    check_copy_paste=(
                        "copy_paste_repetido" in kinds or "copy_paste_en_fila" in kinds
                    ),
                )
                if kinds:
                    gb = gb[gb["tipo_alerta"].isin(kinds)]
                st.session_state[junk_store] = (sig_ev, gb)

        junk_store = widget_key("clean_garbage_store")
        gb_bundle = st.session_state.get(junk_store)
        garbage = pd.DataFrame()
        junk_stale = False
        if isinstance(gb_bundle, tuple) and len(gb_bundle) == 2:
            sig_h, garbage_df = gb_bundle
            cur_sig = st.session_state.get(junk_sig_key, "")
            if sig_h != cur_sig:
                junk_stale = True
            else:
                garbage = garbage_df

        if gb_bundle is None:
            st.info("Pulsá **Escanear respuestas basura / copy-paste** para ver resultados.")
        elif junk_stale:
            st.caption("Cambiaron columnas / umbrales / tipos: volvé a **Escanear**.")
        else:
            n_alertas = len(garbage)
            n_filas = garbage["fila_excel"].nunique() if not garbage.empty else 0
            b1, b2 = st.columns(2)
            b1.metric("Alertas de basura", n_alertas)
            b2.metric("Filas con al menos una alerta", n_filas)

            if garbage.empty:
                st.success(
                    "No se detectaron respuestas basura con la configuración actual."
                )
            else:
                summary = garbage_summary_by_type(garbage)
                st.markdown("##### Resumen por tipo")
                st.dataframe(
                    summary[["etiqueta", "casos"]],
                    width="stretch",
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
                    width="stretch",
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
    st.caption(
        "Genera CSV combinando incoherencias (todas las reglas), aberrantes de la columna elegida arriba "
        "y barrido de basura con columnas inferidas por defecto (primera corrida)."
    )
    flagged_key = widget_key("clean_flagged_df")
    if st.button(
        "Generar tabla de filas marcadas",
        type="primary",
        key=widget_key("clean_flagged_btn"),
    ):
        kinds_set = set(GARBAGE_KIND_LABELS.keys())
        with st.spinner("Armando tabla unificada (puede tardar varios minutos)…"):
            coherence_all = scan_coherence(df, tuple(BUILTIN_COHERENCE_RULES), row_id_column=row_id)
            txt_cols = text_cols_default or infer_text_columns_for_junk(df, column_profiles)
            garbage_all = scan_garbage_responses(df, tuple(txt_cols) or None)
            garbage_all = garbage_all[
                garbage_all["tipo_alerta"].isin(list(kinds_set))
            ].copy()

            outliers_all = outliers
            if col_pick != "(ninguna)":
                outliers_all = scan_numeric_outliers(
                    df,
                    col_pick,
                    min_value=float(min_age),
                    max_value=float(max_age),
                )

            flagged = build_flagged_rows_export(df, coherence_all, outliers_all, garbage_all)
            st.session_state[flagged_key] = flagged

    flagged = st.session_state.get(flagged_key)
    if flagged is not None:
        if flagged.empty:
            st.caption("No hay filas marcadas.")
        else:
            st.caption(
                f"{len(flagged)} fila(s) con al menos una alerta (columna `_alertas_limpieza`)."
            )
            st.dataframe(flagged.head(50), width="stretch")
            st.download_button(
                "Descargar filas marcadas (CSV)",
                flagged.to_csv(index=False).encode("utf-8"),
                file_name="filas_con_alertas_limpieza.csv",
                mime="text/csv",
                type="primary",
                key=widget_key("clean_flagged_csv"),
            )
