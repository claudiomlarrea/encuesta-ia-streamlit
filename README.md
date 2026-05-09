# Encuesta IA — panel Streamlit

Carga respuestas en Excel (formularios tipo Google Forms), clasifica ítems en **estructurados** vs **abiertos**, muestra **frecuencias** y opcionalmente **temas (NMF)** y **sentimiento** en español (modelo RoBERTuito o léxico de respaldo).

## Uso local

```bash
cd encuesta-ia-streamlit
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

En la barra lateral podés **subir el `.xlsx`** o pegar una ruta local.

La primera vez que activás el modelo de Hugging Face se descargan pesos grandes; si falla, desactivá el interruptor y se usa el **léxico** incluido (menos preciso).

## Datos sensibles

Por defecto `.gitignore` excluye `*.xlsx`. Versioná sólo datos anonimizados o quitá esa regla si corresponde.
