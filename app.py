"""
Panel Streamlit: encuestas Excel → clasificación de ítems, cuantitativo y cualitativo.
"""
from __future__ import annotations

import io
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from survey_intel import (
    ColumnProfile,
    SentimentModel,
    classify_columns,
    explode_multiselect,
    frequency_table,
    is_timestamp_column,
    lexicon_sentiment_es,
    thematic_nmf,
)

st.set_page_config(
    page_title="Análisis de encuesta",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner=True)
def _load_sentiment_pipeline():
    return SentimentModel.pipe()


def load_table(uploaded: Any, path: str | None) -> tuple[pd.DataFrame, str]:
    if uploaded is not None:
        raw = uploaded.read()
        bio = io.BytesIO(raw)
        df = pd.read_excel(bio)
        return df, uploaded.name
    if path and path.strip():
        df = pd.read_excel(path.strip())
        return df, path.strip().split("/")[-1]
    raise ValueError("No hay archivo.")


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
    st.title("Encuestas — estructura, cuantitativo y cualitativo")
    st.caption(
        "Detecta preguntas estructuradas vs abiertas, resume el cuantitativo y "
        "explora temas y sentimiento en texto libre (español)."
    )

    with st.sidebar:
        st.header("Datos")
        up = st.file_uploader(
            "Subí el Excel de respuestas",
            type=["xlsx", "xls"],
        )
        default_path = (
            "/Users/claudiolarrea/Downloads/Copia de Encuesta IA - Alumnos (respuestas).xlsx"
        )
        manual_path = st.text_input(
            "O ruta local al Excel (solo en tu máquina)",
            value="",
            placeholder=default_path,
        )

        toggle_hf = st.toggle(
            "Usar modelo de sentimiento robertuito (transformers)",
            value=True,
            help="Primera ejecución descarga pesos (~400 MB). Si falla o es lento, desactivalo y usa el léxico español incluido.",
        )
        topic_k = st.slider("Cantidad de temas (NMF)", 3, 10, 5)

    try:
        if up is not None:
            df, fname = load_table(up, None)
        elif manual_path.strip():
            df, fname = load_table(None, manual_path.strip())
        else:
            st.info("Subí un archivo Excel o indicá una ruta local en la barra lateral.")
            with st.expander("Qué análisis cuantitativos suelen usarse en encuestas como la tuya"):
                st.markdown(
                    """
- **Distribución de frecuencias y porcentajes** por cada ítem cerrado (categorías, Sí/No, escalas).
- **Moda y percentiles** en escalas ordinales (Likert, frecuencia de uso).
- **Tablas cruzadas** entre dos variables (por ejemplo Unidad Académica × uso de IA), con prueba chi‑cuadrado cuando aplica.
- **Puntajes compuestos**: promedios de subescalas (p. ej. ítems de actitudes hacia la IA) y su fiabilidad (alfa de Cronbach) si tenés bloques homogéneos.
- **Correlaciones** entre escalas o entre uso autodeclarado y actitudes.
- **Comparaciones entre grupos** (año de carrera, género, etc.): pruebas no paramétricas o modelos lineales según supuestos.

Esta app implementa **frecuencias, porcentajes y gráficos** para ítems estructurados; el resto podés exportar a CSV y continuar en SPSS, R o Python.
                    """
                )
            return
    except Exception as e:
        st.error(f"No se pudo leer el archivo: {e}")
        return

    st.success(f"Archivo cargado: **{fname}** — {df.shape[0]} filas × {df.shape[1]} columnas")

    profiles = classify_columns(df)
    prof_df = profiles_to_frame(profiles)
    structured = [p for p in profiles if p.kind == "estructurada" and p.n_non_null > 0]
    open_items = [p for p in profiles if p.kind == "abierta" and p.n_non_null > 0]

    tab0, tab1, tab2, tab3 = st.tabs(
        ["Resumen de ítems", "Análisis cuantitativo", "Análisis cualitativo", "Guía metodológica"]
    )

    with tab0:
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

    with tab1:
        st.subheader("Frecuencias y porcentajes")
        if not structured:
            st.warning("No se detectaron ítems estructurados con datos.")
        else:
            choice = st.selectbox(
                "Elegí un ítem estructurado",
                options=[p.name for p in structured],
                format_func=lambda x: next(p.short_name for p in structured if p.name == x),
            )
            col_series = df[choice]
            prof = next(p for p in structured if p.name == choice)

            multiselect_mode = st.checkbox(
                "Tratar como selección múltiple (separar por comas)",
                value="múltiple" in prof.subtype.lower() or "comas" in prof.subtype.lower(),
            )

            if multiselect_mode:
                exploded = explode_multiselect(col_series)
                st.caption(f"Tokens tras separar comas: {len(exploded)} menciones.")
                ft = frequency_table(exploded, top_n=30)
                work_series = exploded
            else:
                ft = frequency_table(col_series, top_n=30)
                work_series = col_series.dropna().astype(str)

            st.dataframe(ft, use_container_width=True, hide_index=True)
            fig = px.bar(
                ft.head(20),
                x="frecuencia",
                y="categoría",
                orientation="h",
                title="Top categorías",
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

            csv = ft.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Descargar tabla (CSV)",
                data=csv,
                file_name="frecuencias.csv",
                mime="text/csv",
            )

    with tab2:
        st.subheader("Temas + sentimiento (respuestas abiertas)")
        if not open_items:
            st.warning("No hay columnas marcadas como abiertas con datos.")
        else:
            oc = st.selectbox(
                "Columna abierta",
                options=[p.name for p in open_items],
                format_func=lambda x: next(p.short_name for p in open_items if p.name == x),
            )
            texts = df[oc].dropna().astype(str).tolist()

            filtered = [t.strip() for t in texts if len(t.strip()) > 4]

            results: list[str] = []
            hf_ok = False
            if toggle_hf:
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
            dist["pct"] = (dist["n"] / dist["n"].sum() * 100).round(1)

            cc1, cc2 = st.columns(2)
            with cc1:
                st.markdown("### Distribución de sentimiento")
                st.dataframe(dist, hide_index=True, use_container_width=True)
                fig2 = px.pie(dist, names="sentimiento", values="n", hole=0.35)
                st.plotly_chart(fig2, use_container_width=True)

            topics, _W = thematic_nmf(filtered, n_topics=topic_k)
            with cc2:
                st.markdown("### Temas (NMF + TF‑IDF)")
                if topics:
                    st.dataframe(pd.DataFrame(topics), hide_index=True, use_container_width=True)
                else:
                    st.caption("Pocos textos o vocabulario muy disperso para extraer temas estables.")

            with st.expander("Ejemplos por sentimiento"):
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
            )

    with tab3:
        st.markdown(
            """
### Análisis cuantitativos típicos en encuestas

- **Descriptivos**: n, %, moda en escalas; gráficos de barras ordenadas.
- **Asociación entre dos categóricas**: tablas cruzadas, chi‑cuadrado.
- **Escalas Likert**: ítems a numéricos, promedios por bloque, fiabilidad (alfa).
- **Comparación de grupos**: medianas y pruebas no paramétricas (Kruskal‑Wallis / Mann‑Whitney) si las distribuciones son asimétricas.
- **Modelado**: regresión ordinal o logit para predecir actitud según año de carrera, acceso a PC, etc.

### Análisis cualitativos en esta app

- **Temático automático (NMF)**: agrupa palabras frecuentes co‑ocurrentes; sirve para una primera lectura, no reemplaza codificación cualitativa rigurosa.
- **Sentimiento**: modelo **RoBERTuito** (`pysentimiento/robertuito-sentiment-analysis`) entrenado en español social; modo respaldo por **léxico** si no hay GPU o falla la descarga.

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
