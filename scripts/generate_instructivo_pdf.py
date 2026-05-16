#!/usr/bin/env python3
"""Genera assets/instructivo_encuesta_clara.pdf (ejecutar tras editar el texto)."""
from __future__ import annotations

from pathlib import Path

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "instructivo_encuesta_clara.pdf"

SECTIONS: list[tuple[str, list[str]]] = [
    (
        "Encuesta Clara — Instructivo de uso",
        [
            "Observatorio de Inteligencia Artificial · Universidad Católica de Cuyo",
            "Herramienta web para analizar respuestas de encuestas exportadas desde Excel (Google Forms y similares).",
        ],
    ),
    (
        "1. Primeros pasos",
        [
            "En la barra lateral, pulsá «Subí el Excel de respuestas» y elegí el archivo .xlsx.",
            "Los datos quedan solo en tu sesión del navegador; no se guardan en el servidor.",
            "Para empezar de cero: «Quitar archivo y reiniciar sesión».",
        ],
    ),
    (
        "2. Pestañas principales",
        [
            "Resumen de ítems: vista general del cuestionario.",
            "Análisis automático: elegís una pregunta, filtros opcionales y obtenés tablas con interpretación.",
            "Análisis cuantitativo: descriptivos, cruces χ², pruebas de significancia, Cronbach, PCA/AFE, clustering, predictivos.",
            "Análisis cualitativo: temas (NMF), sentimiento y lectura de respuestas abiertas.",
        ],
    ),
    (
        "3. Consejos para análisis fiables",
        [
            "Cronbach, PCA y AFE: usá ítems Likert o frecuencia del mismo bloque (no mezclar género/edad con escalas de actitud).",
            "Clustering: las variables se codifican automáticamente; interpretá los centroides antes de nombrar los segmentos.",
            "Muchos módulos incluyen botón «Descargar informe (CSV)» para guardar resultados.",
        ],
    ),
    (
        "4. Contacto y limitaciones en la nube",
        [
            "Consultas: observatorioia@uccuyo.edu.ar (formulario en la barra lateral).",
            "En Streamlit Cloud pueden no estar CFA (semopy), SHAP o RoBERTuito; el análisis núcleo sí está disponible.",
        ],
    ),
]


def _draw_page(pdf: PdfPages, title: str, lines: list[str]) -> None:
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.patch.set_facecolor("white")
    y = 0.92
    fig.text(0.08, y, title, fontsize=14, fontweight="bold", color="#033B26", wrap=True)
    y -= 0.06
    for line in lines:
        fig.text(0.08, y, f"• {line}", fontsize=10, color="#1A2E28", wrap=True, va="top")
        y -= 0.045 + 0.012 * max(0, (len(line) // 85))
        if y < 0.08:
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.patch.set_facecolor("white")
            y = 0.92
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with PdfPages(OUT) as pdf:
        for title, lines in SECTIONS:
            _draw_page(pdf, title, lines)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
