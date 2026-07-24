"""
Pestaña «Análisis automático»: frecuencias, cruces elegibles e informes Word.
"""
from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from executive_report_docx import build_executive_report_docx
from institutional_report_docx import build_institutional_report_docx
from report_common import (
    CHAPTER_TITLES,
    build_frequency_sections,
    classify_chapter,
    display_label,
)
from survey_intel import ColumnProfile

def render_analisis_automatico_tab(
    df: pd.DataFrame,
    profiles: list[ColumnProfile],
    *,
    source_name: str = "",
) -> None:
    st.subheader("Análisis automático")
    st.caption(
        "Pipeline completo del Observatorio: frecuencias de todos los ítems estructurados, "
        "cruces que vos elijas, y generación de **Informe ejecutivo** + **Informe institucional** (Word)."
    )

    structured = [p for p in profiles if p.kind == "estructurada" and p.n_non_null > 0]
    if not structured:
        st.warning("No hay ítems estructurados detectados en el archivo cargado.")
        return

    if st.session_state.get("auto_data_src") != source_name:
        for k in (
            "auto_freq_sections",
            "auto_freq_src",
            "auto_cross_results",
            "auto_exec_bytes",
            "auto_inst_bytes",
            "auto_exec_err",
            "auto_inst_err",
        ):
            st.session_state.pop(k, None)
        st.session_state.auto_data_src = source_name

    label_to_col: dict[str, str] = {}
    for i, p in enumerate(structured):
        lab = display_label(p.name)
        key = lab if lab not in label_to_col else f"{lab}  (ítem {i + 1})"
        label_to_col[key] = p.name
    col_to_label = {v: k for k, v in label_to_col.items()}

    # --- 1. Frecuencias ---
    st.markdown("### 1. Análisis de frecuencias")
    st.caption("Se calculan automáticamente para todos los ítems estructurados detectados.")

    if "auto_freq_sections" not in st.session_state or st.session_state.get("auto_freq_src") != source_name:
        with st.spinner("Calculando tablas de frecuencia…"):
            st.session_state.auto_freq_sections = build_frequency_sections(df, profiles)
            st.session_state.auto_freq_src = source_name

    freq_sections: list[dict[str, Any]] = st.session_state.auto_freq_sections or []
    by_ch: dict[str, list] = {}
    for sec in freq_sections:
        by_ch.setdefault(sec.get("chapter", "otros"), []).append(sec)

    st.success(f"Listo: **{len(freq_sections)}** ítems con tabla de frecuencias.")

    for ch_key in (
        "sociodemografico",
        "adopcion",
        "usos",
        "actitudes",
        "institucional",
        "otros",
    ):
        secs = by_ch.get(ch_key) or []
        if not secs:
            continue
        with st.expander(f"{CHAPTER_TITLES.get(ch_key, ch_key)} ({len(secs)} ítems)", expanded=False):
            for sec in secs:
                st.markdown(f"**{display_label(sec['label'])}**")
                st.caption(f"N = {sec['n']} · {sec.get('subtype') or ''}")
                ft = sec["table"].copy()
                if "categoría" in ft.columns:
                    show = ft[ft["categoría"].astype(str).str.upper() != "TOTAL"].copy()
                else:
                    show = ft
                st.dataframe(show, use_container_width=True, hide_index=True)
                st.markdown(f"*Conclusión:* {sec['conclusion']}")
                st.divider()

    # --- 2. Cruces elegibles ---
    st.markdown("### 2. Cruces entre preguntas")
    st.caption(
        "Elegí una variable de fila (típicamente demográfica) y una o más variables de columna. "
        "El sistema arma las tablas de contingencia."
    )

    all_labels = list(label_to_col.keys())
    dem_labels = [
        col_to_label[p.name]
        for p in structured
        if classify_chapter(p) == "sociodemografico" and p.name in col_to_label
    ]
    default_row = dem_labels[0] if dem_labels else all_labels[0]

    c1, c2 = st.columns(2)
    with c1:
        row_label = st.selectbox(
            "Variable de fila (eje demográfico / corte)",
            all_labels,
            index=all_labels.index(default_row) if default_row in all_labels else 0,
            key="auto_cross_row",
        )
    with c2:
        sug = [
            col_to_label[p.name]
            for p in structured
            if classify_chapter(p) in {"adopcion", "usos", "institucional", "actitudes"}
            and p.name in col_to_label
        ][:8]
        col_labels = st.multiselect(
            "Variables de columna (podés marcar varias)",
            [x for x in all_labels if x != row_label],
            default=[x for x in sug if x != row_label][:3],
            key="auto_cross_cols",
            help="Marcá las preguntas con las que querés cruzar la variable de fila.",
        )

    run_cross = st.button("Calcular cruces seleccionados", type="primary", key="auto_run_cross")
    if run_cross:
        row_col = label_to_col[row_label]
        results = []
        for lab in col_labels:
            col_col = label_to_col[lab]
            if col_col == row_col:
                continue
            try:
                ct = pd.crosstab(df[row_col], df[col_col])
                if ct.shape[0] < 2 or ct.shape[1] < 2:
                    continue
                if ct.shape[0] > 15:
                    ct = ct.iloc[:15]
                if ct.shape[1] > 10:
                    ct = ct.iloc[:, :10]
                results.append({"row": row_label, "col": lab, "table": ct})
            except Exception as e:  # noqa: BLE001
                st.warning(f"No se pudo cruzar «{lab}»: {e}")
        st.session_state.auto_cross_results = results

    results = st.session_state.get("auto_cross_results") or []
    if results:
        st.markdown(f"**{len(results)}** cruce(s) calculado(s):")
        for i, cr in enumerate(results, start=1):
            with st.expander(f"{i}. {cr['row']} × {cr['col']}", expanded=i == 1):
                st.dataframe(cr["table"], use_container_width=True)
    elif col_labels:
        st.info("Marcá «Calcular cruces seleccionados» para ver las tablas.")

    # --- 3. Informes ---
    st.markdown("### 3. Informes institucionales (Word)")
    st.caption(
        "El **ejecutivo** es narrativo (sin tablas). El **institucional** es extenso "
        "(introducción → tabla → conclusión por ítem, cruces automáticos y cualitativo)."
    )

    gen1, gen2 = st.columns(2)
    with gen1:
        if st.button("Generar informe ejecutivo", type="primary", key="auto_gen_exec", use_container_width=True):
            with st.spinner("Generando informe ejecutivo…"):
                try:
                    st.session_state.auto_exec_bytes = build_executive_report_docx(
                        df,
                        cohort_label="Análisis automático · Encuesta Clara",
                        source_name=source_name,
                    )
                    st.session_state.auto_exec_err = None
                except Exception as e:  # noqa: BLE001
                    st.session_state.auto_exec_err = str(e)
                    st.session_state.auto_exec_bytes = None
    with gen2:
        if st.button("Generar informe institucional", type="primary", key="auto_gen_inst", use_container_width=True):
            with st.spinner("Generando informe institucional extenso…"):
                try:
                    st.session_state.auto_inst_bytes = build_institutional_report_docx(
                        df,
                        source_name=source_name,
                        cohort_label="Análisis automático · Encuesta Clara",
                    )
                    st.session_state.auto_inst_err = None
                except Exception as e:  # noqa: BLE001
                    st.session_state.auto_inst_err = str(e)
                    st.session_state.auto_inst_bytes = None

    d1, d2 = st.columns(2)
    if st.session_state.get("auto_exec_err"):
        d1.error(st.session_state.auto_exec_err)
    elif st.session_state.get("auto_exec_bytes"):
        d1.download_button(
            "Descargar informe ejecutivo (Word)",
            data=st.session_state.auto_exec_bytes,
            file_name="informe_ejecutivo_encuesta_clara.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key="auto_dl_exec",
        )
    if st.session_state.get("auto_inst_err"):
        d2.error(st.session_state.auto_inst_err)
    elif st.session_state.get("auto_inst_bytes"):
        d2.download_button(
            "Descargar informe institucional (Word)",
            data=st.session_state.auto_inst_bytes,
            file_name="informe_institucional_encuesta_clara.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key="auto_dl_inst",
        )

    # Atajo: generar ambos
    if st.button("Generar ambos informes", key="auto_gen_both"):
        with st.spinner("Generando ejecutivo e institucional…"):
            try:
                st.session_state.auto_exec_bytes = build_executive_report_docx(
                    df,
                    cohort_label="Análisis automático · Encuesta Clara",
                    source_name=source_name,
                )
                st.session_state.auto_exec_err = None
            except Exception as e:  # noqa: BLE001
                st.session_state.auto_exec_err = str(e)
            try:
                st.session_state.auto_inst_bytes = build_institutional_report_docx(
                    df,
                    source_name=source_name,
                    cohort_label="Análisis automático · Encuesta Clara",
                )
                st.session_state.auto_inst_err = None
            except Exception as e:  # noqa: BLE001
                st.session_state.auto_inst_err = str(e)
        st.rerun()
