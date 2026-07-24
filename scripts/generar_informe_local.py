#!/usr/bin/env python3
"""Genera informe ejecutivo y/o institucional desde un Excel/CSV local."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from executive_report_docx import build_executive_report_docx  # noqa: E402
from institutional_report_docx import build_institutional_report_docx  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", required=True, help="Ruta al Excel/CSV de respuestas")
    ap.add_argument("--out-dir", required=True, help="Carpeta de salida")
    ap.add_argument("--title", default="", help="Subtítulo (vacío = detección automática)")
    args = ap.parse_args()

    src = Path(args.xlsx)
    if not src.exists():
        raise SystemExit(f"No existe: {src}")
    if src.suffix.lower() == ".csv":
        df = pd.read_csv(src)
    else:
        df = pd.read_excel(src)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    exec_path = out_dir / "informe_ejecutivo_encuesta_clara.docx"
    inst_path = out_dir / "informe_institucional_encuesta_clara.docx"

    exec_bytes = build_executive_report_docx(
        df,
        title=args.title,
        cohort_label="Prueba local Encuesta Clara",
        source_name=src.name,
    )
    exec_path.write_bytes(exec_bytes)
    print(f"OK ejecutivo → {exec_path} ({len(exec_bytes)} bytes)")

    inst_bytes = build_institutional_report_docx(
        df,
        source_name=src.name,
        cohort_label="Prueba local Encuesta Clara",
    )
    inst_path.write_bytes(inst_bytes)
    print(f"OK institucional → {inst_path} ({len(inst_bytes)} bytes; {len(df)} filas)")


if __name__ == "__main__":
    main()
