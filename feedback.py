"""Formulario de contacto institucional — devolución de usuarios."""
from __future__ import annotations

import html
import re
import smtplib
import ssl
from email.message import EmailMessage
from typing import Any
from urllib.parse import quote

import streamlit as st

from ui_theme import GREEN, GREEN_DARK

FEEDBACK_TO = "obserbatorioia@uccuyo.edu.ar"
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _smtp_settings() -> dict[str, Any] | None:
    try:
        sec = st.secrets.get("email", st.secrets.get("smtp", {}))
    except Exception:
        return None
    if not sec or not sec.get("smtp_server"):
        return None
    return dict(sec)


def _send_via_smtp(
    *,
    settings: dict[str, Any],
    nombre: str,
    apellido: str,
    email: str,
    telefono: str,
    mensaje: str,
) -> None:
    to_addr = str(settings.get("to", FEEDBACK_TO))
    from_addr = str(settings.get("from_addr", settings.get("username", to_addr)))
    subject = f"[Encuesta Clara] {nombre} {apellido}".strip()
    body = (
        f"Nombre: {nombre}\n"
        f"Apellido: {apellido}\n"
        f"Email: {email}\n"
        f"Teléfono: {telefono or '—'}\n\n"
        f"Mensaje:\n{mensaje}\n"
    )
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Reply-To"] = email
    msg.set_content(body)

    server = str(settings["smtp_server"])
    port = int(settings.get("smtp_port", 587))
    user = str(settings.get("username", ""))
    password = str(settings.get("password", ""))
    use_tls = bool(settings.get("use_tls", True))

    if use_tls and port == 465:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(server, port, context=context) as smtp:
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(server, port, timeout=30) as smtp:
            if use_tls:
                smtp.starttls(context=ssl.create_default_context())
            if user:
                smtp.login(user, password)
            smtp.send_message(msg)


def _mailto_url(
    *,
    nombre: str,
    apellido: str,
    email: str,
    telefono: str,
    mensaje: str,
) -> str:
    subject = quote(f"Encuesta Clara — {nombre} {apellido}".strip())
    body = quote(
        f"Nombre: {nombre}\n"
        f"Apellido: {apellido}\n"
        f"Email: {email}\n"
        f"Teléfono: {telefono or '—'}\n\n"
        f"Mensaje:\n{mensaje}\n"
    )
    return f"mailto:{FEEDBACK_TO}?subject={subject}&body={body}"


def render_institutional_contact() -> None:
    """Formulario en la barra lateral (siempre visible)."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {GREEN_DARK} 0%, {GREEN} 100%);
            border-radius: 10px;
            padding: 0.85rem 1rem 0.5rem 1rem;
            margin: 1rem 0 0.65rem 0;
        ">
            <p style="color: #fff; font-weight: 700; font-size: 1.05rem; margin: 0 0 0.2rem 0;">
                Contacto institucional
            </p>
            <p style="color: rgba(255,255,255,0.9); font-size: 0.78rem; margin: 0;">
                Consultas y sugerencias · {html.escape(FEEDBACK_TO)}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("institutional_contact", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre *", max_chars=80)
            email = st.text_input("Email *", max_chars=120)
        with c2:
            apellido = st.text_input("Apellido *", max_chars=80)
            telefono = st.text_input("Teléfono", max_chars=40)
        mensaje = st.text_area("Mensaje *", height=100, max_chars=4000)
        sent = st.form_submit_button("Enviar mensaje", type="primary", use_container_width=True)

    if not sent:
        return

    nombre = nombre.strip()
    apellido = apellido.strip()
    email = email.strip()
    telefono = telefono.strip()
    mensaje = mensaje.strip()

    if not nombre or not apellido or not email or not mensaje:
        st.error("Completá los campos obligatorios (*).")
        return
    if not _EMAIL_RE.match(email):
        st.error("El email no tiene un formato válido.")
        return

    smtp = _smtp_settings()
    if smtp:
        try:
            _send_via_smtp(
                settings=smtp,
                nombre=nombre,
                apellido=apellido,
                email=email,
                telefono=telefono,
                mensaje=mensaje,
            )
            st.success(
                f"Tu mensaje fue enviado a **{FEEDBACK_TO}**. "
                "Te responderemos al correo que indicaste."
            )
            return
        except Exception as exc:
            st.warning(
                f"No se pudo enviar por el servidor de correo ({exc}). "
                "Usá el botón de abajo para enviar desde tu cliente de email."
            )

    mailto = _mailto_url(
        nombre=nombre,
        apellido=apellido,
        email=email,
        telefono=telefono,
        mensaje=mensaje,
    )
    st.info(
        "Para completar el envío, abrí tu correo con el mensaje ya redactado "
        f"(destino: **{FEEDBACK_TO}**)."
    )
    st.link_button("Abrir en mi correo", mailto, use_container_width=True)
    st.caption(
        "Si el enlace no funciona en tu navegador, copiá el texto y envialo manualmente "
        f"a {FEEDBACK_TO}."
    )
