"""Carga de respuestas desde Google Sheets (CSV público o export)."""
from __future__ import annotations

import io
import re
from typing import Any
from urllib.parse import parse_qs, urlparse

import pandas as pd
import requests

_SHEET_ID_RE = re.compile(r"/spreadsheets/d/([a-zA-Z0-9-_]+)")
_GID_RE = re.compile(r"[#&?]gid=(\d+)")


def extract_sheet_id(url_or_id: str) -> str | None:
    raw = (url_or_id or "").strip()
    if not raw:
        return None
    if re.fullmatch(r"[a-zA-Z0-9-_]{20,}", raw):
        return raw
    m = _SHEET_ID_RE.search(raw)
    return m.group(1) if m else None


def extract_gid(url_or_id: str, default: int = 0) -> int:
    raw = (url_or_id or "").strip()
    m = _GID_RE.search(raw)
    if m:
        return int(m.group(1))
    try:
        qs = parse_qs(urlparse(raw).query)
        if "gid" in qs and qs["gid"]:
            return int(qs["gid"][0])
    except (TypeError, ValueError):
        pass
    return default


def sheets_export_urls(sheet_id: str, gid: int = 0) -> list[str]:
    """URLs candidatas (la hoja debe estar compartida al menos como «cualquiera con el enlace»)."""
    return [
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}",
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&gid={gid}",
    ]


def load_google_sheet(url_or_id: str, gid: int | None = None, timeout: int = 45) -> tuple[pd.DataFrame, str]:
    sheet_id = extract_sheet_id(url_or_id)
    if not sheet_id:
        raise ValueError(
            "No se reconoció un ID de Google Sheets. Pegá la URL completa "
            "(docs.google.com/spreadsheets/d/…) o el ID de la hoja."
        )
    use_gid = extract_gid(url_or_id) if gid is None else int(gid)
    last_err: Exception | None = None
    for url in sheets_export_urls(sheet_id, use_gid):
        try:
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            content = resp.content
            if not content or len(content) < 5:
                raise ValueError(
                    "La hoja respondió vacía. Publicá o compartí el Sheets como "
                    "«Cualquier persona con el enlace → Lector» y verificá que haya respuestas."
                )
            # Si Google redirige a HTML de login, fallar con mensaje claro
            ctype = (resp.headers.get("content-type") or "").lower()
            head = content[:200].lstrip().lower()
            if "text/html" in ctype or head.startswith(b"<!doctype") or head.startswith(b"<html"):
                raise ValueError(
                    "Google devolvió HTML (login o sin permiso). "
                    "Compartí la hoja: Cualquier persona con el enlace puede ver."
                )
            df = pd.read_csv(io.BytesIO(content))
            if df.shape[0] == 0 and df.shape[1] == 0:
                raise ValueError("CSV sin columnas. Revisá gid y permisos de la hoja.")
            label = f"sheets:{sheet_id}:gid{use_gid}"
            return df.copy(), label
        except Exception as e:  # noqa: BLE001 — probar siguiente URL
            last_err = e
            continue
    raise ValueError(str(last_err) if last_err else "No se pudo cargar el Google Sheet.")


def dataframe_fingerprint(df: pd.DataFrame, source: str) -> str:
    return f"{source}|{int(df.shape[0])}|{int(df.shape[1])}|{len(df.columns)}"
