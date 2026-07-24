# Encuesta Clara

Panel Streamlit para encuestas: carga respuestas en Excel (formularios tipo Google Forms), clasifica ítems en **estructurados** vs **abiertos** y ejecuta un bloque amplio de **cuantitativo**: descriptivos, cruces con χ² y Cramér V, pruebas (t Welch, Mann–Whitney, ANOVA, Kruskal–Wallis), Alfa de Cronbach, PCA/AFE con Varimax, K‑means / DBSCAN / jerárquico, modelos (logística, árboles, Random Forest, XGBoost) con **SHAP**, CFA simplificado con **semopy**. Incluye además temas (**NMF**) y **sentimiento** en español (RoBERTuito o léxico de respaldo).

## Streamlit Cloud

El archivo `requirements.txt` incluye sólo paquetes ligeros (sin **semopy**, PyTorch, transformers, XGBoost ni SHAP) para que [Community Cloud](https://streamlit.io/cloud) no falle en la instalación. **CFA** y matriz policórica en PCA/AFE requieren `semopy`; en Cloud la app muestra CFA deshabilitado y PCA/AFE clásicos (o fallback si marcás policórico). Tras hacer push en `main`, pulsá **Manage app** si algo sigue fallando y revisá el terminal.

Confirmá que el despliegue en Streamlit apunta al mismo repositorio de GitHub que actualizás (la URL `.streamlit.app` puede tener otro nombre).

Versión de Python para Cloud: `runtime.txt` (3.11).

## Uso local

```bash
cd encuesta-ia-streamlit
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-full.txt   # SHAP, XGBoost y sentimiento HF
# o sólo núcleo: pip install -r requirements.txt
streamlit run app.py
```

En la barra lateral podés **subir el `.xlsx`**, pegar una **URL/ID de Google Sheets** (compartido con enlace) o una ruta local.

Pestañas principales:

- **Análisis automático**: frecuencias de todos los ítems, cruces que elijas e **Informe ejecutivo** + **Informe institucional** (Word).
- **Análisis semiautomático**: modo guiado ítem por ítem (consultas individuales, filtros y cruces puntuales).

También podés abrir la app con query params:

```
http://localhost:8501/?sheet=ID_DE_LA_HOJA
http://localhost:8501/?sheets_url=https://docs.google.com/spreadsheets/d/ID/...
```

Tras cargar datos, aparece **Descargar informe ejecutivo (Word)** con frecuencias de ítems estructurados y síntesis cualitativa de abiertas.

Informe por consola:

```bash
python scripts/generar_informe_local.py --xlsx /ruta/respuestas.xlsx --out /ruta/informe.docx
```

La primera vez que activás el modelo de Hugging Face se descargan pesos grandes; si falla, desactivá el interruptor y se usa el **léxico** incluido (menos preciso).

## Datos sensibles

Por defecto `.gitignore` excluye `*.xlsx`. Versioná sólo datos anonimizados o quitá esa regla si corresponde.

## Protocolo estadístico en la app

- **Ítems invertidos:** marcálos en el expander de la pestaña cuantitativa (misma convención antes de ver resultados).
- **4 vs 5 categorías:** el codificador elige texto Likert/Frec **de cuatro o cinco niveles** según la cobertura; la inversión usa el rango observado por columna.
- **Policórico + R:** en *PCA / AFE* podés descargar `cor_poly.csv` y copiar el ejemplo `lavaan` (revisá estimadores y muestra según tu diseño).
