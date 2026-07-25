"""
Pestaña «Análisis automático»: configurar cruces → frecuencias → cruces por ítem → informes.
"""
from __future__ import annotations

import hashlib
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
    normalize_user_crosses,
)
from survey_intel import ColumnProfile

CHAPTER_ORDER = (
    "sociodemografico",
    "adopcion",
    "usos",
    "actitudes",
    "institucional",
    "otros",
)


def _wid(prefix: str, col: str) -> str:
    h = hashlib.md5(col.encode("utf-8")).hexdigest()[:10]
    return f"{prefix}_{h}"


def _crosstab_safe(df: pd.DataFrame, row_col: str, col_col: str) -> pd.DataFrame | None:
    try:
        ct = pd.crosstab(df[row_col], df[col_col])
    except Exception:  # noqa: BLE001
        return None
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return None
    if ct.shape[0] > 15:
        ct = ct.iloc[:15]
    if ct.shape[1] > 10:
        ct = ct.iloc[:, :10]
    return ct


def _clear_auto_results() -> None:
    for k in (
        "auto_freq_sections",
        "auto_freq_src",
        "auto_analysis_ready",
        "auto_cross_computed",
        "auto_exec_bytes",
        "auto_inst_bytes",
        "auto_exec_err",
        "auto_inst_err",
        "auto_exec_n_cross",
        "auto_inst_n_cross",
    ):
        st.session_state.pop(k, None)


def render_analisis_automatico_tab(
    df: pd.DataFrame,
    profiles: list[ColumnProfile],
    *,
    source_name: str = "",
) -> None:
    st.subheader("Análisis automático")
    st.caption(
        "1) Configurá los cruces de **todas** las preguntas · "
        "2) Calculá · "
        "3) Revisá frecuencia general y luego los cruces de cada ítem · "
        "4) Generá los informes Word."
    )

    structured = [p for p in profiles if p.kind == "estructurada" and p.n_non_null > 0]
    if not structured:
        st.warning("No hay ítems estructurados detectados en el archivo cargado.")
        return

    if st.session_state.get("auto_data_src") != source_name:
        _clear_auto_results()
        st.session_state.pop("auto_cross_plan", None)
        st.session_state.auto_data_src = source_name

    # Etiquetas únicas
    label_to_col: dict[str, str] = {}
    for i, p in enumerate(structured):
        lab = display_label(p.name)
        key = lab if lab not in label_to_col else f"{lab}  (ítem {i + 1})"
        label_to_col[key] = p.name
    col_to_label = {v: k for k, v in label_to_col.items()}
    all_labels = list(label_to_col.keys())

    by_chapter: dict[str, list[ColumnProfile]] = {k: [] for k in CHAPTER_ORDER}
    for p in structured:
        by_chapter.setdefault(classify_chapter(p), []).append(p)

    dem_labels = [
        col_to_label[p.name]
        for p in by_chapter.get("sociodemografico", [])
        if p.name in col_to_label
    ]

    # ------------------------------------------------------------------
    # 1. Configurar cruces (antes de calcular)
    # ------------------------------------------------------------------
    st.markdown("### 1. Configurar cruces (todas las preguntas)")
    st.caption(
        "Para cada pregunta, marcá con qué otras variables querés cruzarla. "
        "Podés usar el atajo demográfico y después ajustar ítem por ítem."
    )

    if "auto_cross_plan" not in st.session_state:
        st.session_state.auto_cross_plan = {p.name: [] for p in structured}

    def _sync_plan_from_widgets() -> dict[str, list[str]]:
        plan: dict[str, list[str]] = {}
        for p in structured:
            wkey = _wid("auto_x", p.name)
            labels = st.session_state.get(wkey, [])
            if not isinstance(labels, list):
                labels = []
            plan[p.name] = [label_to_col[x] for x in labels if x in label_to_col]
        st.session_state.auto_cross_plan = plan
        return plan

    def _write_plan_to_widgets(plan: dict[str, list[str]]) -> None:
        for p in structured:
            partners = plan.get(p.name, [])
            st.session_state[_wid("auto_x", p.name)] = [
                col_to_label[c] for c in partners if c in col_to_label
            ]

    # Inicializar widgets si faltan
    for p in structured:
        wkey = _wid("auto_x", p.name)
        if wkey not in st.session_state:
            partners = st.session_state.auto_cross_plan.get(p.name, [])
            st.session_state[wkey] = [col_to_label[c] for c in partners if c in col_to_label]

    with st.expander("Atajos de configuración", expanded=True):
        a1, a2, a3 = st.columns([2, 1, 1])
        with a1:
            dem_pick = st.selectbox(
                "Corte demográfico a aplicar",
                dem_labels or all_labels[:1],
                key="auto_dem_shortcut",
                help="Se usa como variable de cruce para las preguntas que indiques abajo.",
            )
        with a2:
            apply_non_dem = st.button(
                "Aplicar a no demográficas",
                use_container_width=True,
                key="auto_apply_nondem",
                help="Agrega el corte demográfico a todas las preguntas que no son sociodemográficas.",
            )
        with a3:
            clear_plan = st.button(
                "Limpiar todos los cruces",
                use_container_width=True,
                key="auto_clear_plan",
            )

        if clear_plan:
            plan = {p.name: [] for p in structured}
            st.session_state.auto_cross_plan = plan
            _write_plan_to_widgets(plan)
            _clear_auto_results()
            st.rerun()

        if apply_non_dem and dem_pick:
            dem_col = label_to_col[dem_pick]
            plan = _sync_plan_from_widgets()
            for p in structured:
                if classify_chapter(p) == "sociodemografico":
                    continue
                partners = list(plan.get(p.name, []))
                if dem_col not in partners and dem_col != p.name:
                    partners.insert(0, dem_col)
                plan[p.name] = partners
            st.session_state.auto_cross_plan = plan
            _write_plan_to_widgets(plan)
            _clear_auto_results()
            st.rerun()

    for ch_key in CHAPTER_ORDER:
        items = by_chapter.get(ch_key) or []
        if not items:
            continue
        with st.expander(
            f"Cruces · {CHAPTER_TITLES.get(ch_key, ch_key)} ({len(items)} ítems)",
            expanded=(ch_key == "sociodemografico"),
        ):
            for p in items:
                own_label = col_to_label[p.name]
                other_labels = [lab for lab in all_labels if label_to_col[lab] != p.name]
                st.multiselect(
                    f"Cruzar «{own_label}» con",
                    other_labels,
                    key=_wid("auto_x", p.name),
                    help="Elegí una o más preguntas para la tabla de contingencia.",
                )

    plan_now = _sync_plan_from_widgets()
    planned_n = sum(len(v) for v in plan_now.values())
    st.info(
        f"Plan actual: **{planned_n}** cruce(s) definidos en **{len(structured)}** preguntas. "
        "Cuando termines de elegir, calculá el análisis."
    )

    calc = st.button("Calcular frecuencias y cruces", type="primary", key="auto_calc_all")
    if calc:
        with st.spinner("Calculando frecuencias y cruces…"):
            plan = _sync_plan_from_widgets()
            freq_sections = build_frequency_sections(df, profiles)
            freq_by_col = {sec["column"]: sec for sec in freq_sections}

            computed: list[dict[str, Any]] = []
            for p in structured:
                partners = plan.get(p.name, [])
                crosses = []
                for partner in partners:
                    if partner == p.name:
                        continue
                    ct = _crosstab_safe(df, p.name, partner)
                    if ct is None:
                        continue
                    crosses.append(
                        {
                            "partner": partner,
                            "partner_label": col_to_label.get(partner, display_label(partner)),
                            "table": ct,
                        }
                    )
                sec = freq_by_col.get(p.name)
                computed.append(
                    {
                        "column": p.name,
                        "label": col_to_label.get(p.name, display_label(p.name)),
                        "chapter": classify_chapter(p),
                        "subtype": p.subtype,
                        "freq": sec,
                        "crosses": crosses,
                    }
                )
            st.session_state.auto_freq_sections = freq_sections
            st.session_state.auto_cross_computed = computed
            st.session_state.auto_analysis_ready = True
            st.session_state.auto_freq_src = source_name
        st.rerun()
    # ------------------------------------------------------------------
    # 2–3. Resultados: frecuencia general + cruces de cada pregunta
    # ------------------------------------------------------------------
    if not st.session_state.get("auto_analysis_ready"):
        st.markdown("### 2. Resultados")
        st.caption("Todavía no hay resultados. Configurá los cruces y pulsá **Calcular frecuencias y cruces**.")
    else:
        computed = st.session_state.get("auto_cross_computed") or []
        st.markdown("### 2. Resultados por pregunta")
        st.caption(
            "Para cada ítem: primero la **frecuencia general** y, debajo, los **cruces** que elegiste."
        )
        st.success(
            f"Análisis listo: **{len(computed)}** preguntas · "
            f"**{sum(len(x.get('crosses') or []) for x in computed)}** cruces calculados."
        )

        for ch_key in CHAPTER_ORDER:
            block = [x for x in computed if x.get("chapter") == ch_key]
            if not block:
                continue
            with st.expander(
                f"Resultados · {CHAPTER_TITLES.get(ch_key, ch_key)} ({len(block)} ítems)",
                expanded=(ch_key in {"sociodemografico", "adopcion"}),
            ):
                for item in block:
                    st.markdown(f"#### {item['label']}")
                    if item.get("subtype"):
                        st.caption(item["subtype"])

                    st.markdown("**Frecuencia general**")
                    sec = item.get("freq")
                    if not sec:
                        st.warning("Sin tabla de frecuencias para este ítem.")
                    else:
                        st.caption(f"N = {sec['n']}")
                        ft = sec["table"].copy()
                        if "categoría" in ft.columns:
                            show = ft[ft["categoría"].astype(str).str.upper() != "TOTAL"].copy()
                        else:
                            show = ft
                        st.dataframe(show, use_container_width=True, hide_index=True)
                        st.markdown(f"*Conclusión:* {sec['conclusion']}")

                    crosses = item.get("crosses") or []
                    if crosses:
                        st.markdown("**Cruces elegidos**")
                        for j, cr in enumerate(crosses, start=1):
                            st.markdown(f"{j}. `{item['label']}` × `{cr['partner_label']}`")
                            st.dataframe(cr["table"], use_container_width=True)
                    else:
                        st.caption("Sin cruces configurados para esta pregunta.")
                    st.divider()

    # ------------------------------------------------------------------
    # 4. Informes
    # ------------------------------------------------------------------
    st.markdown("### 3. Informes institucionales (Word)")
    st.caption(
        "El **institucional** incluye cada cruce elegido una sola vez, como subapartado "
        "de la pregunta donde lo configuraste (p. ej. 1.2.1). El **ejecutivo** integra "
        "esas lecturas en la narrativa del apartado temático correspondiente "
        "(hallazgos, beneficios, riesgos o brechas), sin un capítulo aparte."
    )

    def _crosses_for_reports() -> list[dict[str, Any]]:
        return normalize_user_crosses(st.session_state.get("auto_cross_computed") or [])

    if not st.session_state.get("auto_analysis_ready"):
        st.warning(
            "Para incluir tus cruces en los Word, primero pulsá **Calcular frecuencias y cruces**."
        )

    gen1, gen2 = st.columns(2)
    with gen1:
        if st.button("Generar informe ejecutivo", type="primary", key="auto_gen_exec", use_container_width=True):
            with st.spinner("Generando informe ejecutivo…"):
                try:
                    crosses = _crosses_for_reports()
                    st.session_state.auto_exec_bytes = build_executive_report_docx(
                        df,
                        cohort_label="Análisis automático · Encuesta Clara",
                        source_name=source_name,
                        user_crosses=crosses,
                    )
                    st.session_state.auto_exec_err = None
                    st.session_state.auto_exec_n_cross = len(crosses)
                except Exception as e:  # noqa: BLE001
                    st.session_state.auto_exec_err = str(e)
                    st.session_state.auto_exec_bytes = None
    with gen2:
        if st.button("Generar informe institucional", type="primary", key="auto_gen_inst", use_container_width=True):
            with st.spinner("Generando informe institucional extenso…"):
                try:
                    crosses = _crosses_for_reports()
                    st.session_state.auto_inst_bytes = build_institutional_report_docx(
                        df,
                        source_name=source_name,
                        cohort_label="Análisis automático · Encuesta Clara",
                        user_crosses=crosses,
                    )
                    st.session_state.auto_inst_err = None
                    st.session_state.auto_inst_n_cross = len(crosses)
                except Exception as e:  # noqa: BLE001
                    st.session_state.auto_inst_err = str(e)
                    st.session_state.auto_inst_bytes = None

    d1, d2 = st.columns(2)
    if st.session_state.get("auto_exec_err"):
        d1.error(st.session_state.auto_exec_err)
    elif st.session_state.get("auto_exec_bytes"):
        n_x = st.session_state.get("auto_exec_n_cross", 0)
        d1.caption(f"Incluye {n_x} cruce(s) seleccionados.")
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
        n_x = st.session_state.get("auto_inst_n_cross", 0)
        d2.caption(f"Incluye {n_x} cruce(s) seleccionados.")
        d2.download_button(
            "Descargar informe institucional (Word)",
            data=st.session_state.auto_inst_bytes,
            file_name="informe_institucional_encuesta_clara.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key="auto_dl_inst",
        )

    if st.button("Generar ambos informes", key="auto_gen_both"):
        with st.spinner("Generando ejecutivo e institucional…"):
            crosses = _crosses_for_reports()
            try:
                st.session_state.auto_exec_bytes = build_executive_report_docx(
                    df,
                    cohort_label="Análisis automático · Encuesta Clara",
                    source_name=source_name,
                    user_crosses=crosses,
                )
                st.session_state.auto_exec_err = None
                st.session_state.auto_exec_n_cross = len(crosses)
            except Exception as e:  # noqa: BLE001
                st.session_state.auto_exec_err = str(e)
            try:
                st.session_state.auto_inst_bytes = build_institutional_report_docx(
                    df,
                    source_name=source_name,
                    cohort_label="Análisis automático · Encuesta Clara",
                    user_crosses=crosses,
                )
                st.session_state.auto_inst_err = None
                st.session_state.auto_inst_n_cross = len(crosses)
            except Exception as e:  # noqa: BLE001
                st.session_state.auto_inst_err = str(e)
        st.rerun()
