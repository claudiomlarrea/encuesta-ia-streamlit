"""Portada institucional (PNG) — estética bordo/verde del informe ejecutivo UCCuyo."""
from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parent / "assets"
LOGO_PATH = ASSETS / "logo_observatorio_ia.png"

# A4 @ 150 dpi
W, H = 1240, 1754
GREEN = (6, 74, 56)
WHITE = (255, 255, 255)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = []
    if bold:
        candidates += [
            "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/Library/Fonts/Arial Bold.ttf",
        ]
    else:
        candidates += [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Georgia.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
        ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = (text or "").split()
    if not words:
        return [""]
    lines: list[str] = []
    cur = words[0]
    for w in words[1:]:
        trial = f"{cur} {w}"
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def _gradient_bg() -> Image.Image:
    """Fondo degradé bordo (#4a0c1f → #9c2748), diagonal suave."""
    img = Image.new("RGB", (W, H))
    px = img.load()
    c0 = (74, 12, 31)
    c1 = (156, 39, 72)
    for y in range(H):
        ty = y / max(H - 1, 1)
        for x in range(W):
            tx = x / max(W - 1, 1)
            u = min(1.0, max(0.0, 0.62 * ty + 0.38 * tx))
            r = int(c0[0] + (c1[0] - c0[0]) * u)
            g = int(c0[1] + (c1[1] - c0[1]) * u)
            b = int(c0[2] + (c1[2] - c0[2]) * u)
            px[x, y] = (r, g, b)
    return img


def _paste_circular_logo(base: Image.Image, logo_path: Path, xy: tuple[int, int], size: int) -> None:
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((size, size), Image.Resampling.LANCZOS)
    # círculo blanco + logo
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    white = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    canvas.paste(white, (0, 0), mask)
    canvas.paste(logo, (0, 0), mask)
    base.paste(canvas, xy, canvas)


def render_cover_png(
    *,
    kicker: str,
    title: str,
    subtitle: str,
    year: int | None = None,
) -> bytes:
    year = year or datetime.now().year
    img = _gradient_bg()
    draw = ImageDraw.Draw(img)

    # barra verde superior
    bar_h = 64
    draw.rectangle((0, 0, W, bar_h), fill=GREEN)
    f_bar = _font(17, bold=True)
    bar_txt = "UNIVERSIDAD CATÓLICA DE CUYO  ·  OBSERVATORIO DE INTELIGENCIA ARTIFICIAL"
    tw = draw.textlength(bar_txt, font=f_bar)
    draw.text(((W - tw) / 2, 22), bar_txt, fill=WHITE, font=f_bar)

    # logo + marca
    logo_x, logo_y = 78, 100
    logo_size = 118
    if LOGO_PATH.exists():
        _paste_circular_logo(img, LOGO_PATH, (logo_x, logo_y), logo_size)
        draw = ImageDraw.Draw(img)

    f_uni = _font(26, bold=True)
    f_obs = _font(32, bold=True)
    brand_x = logo_x + logo_size + 26
    draw.text((brand_x, logo_y + 28), "Universidad Católica de Cuyo", fill=WHITE, font=f_uni)
    draw.text((brand_x, logo_y + 66), "Observatorio de Inteligencia Artificial", fill=WHITE, font=f_obs)

    # bloque título
    main_top = 360
    f_kick = _font(20, bold=True)
    draw.text((78, main_top), kicker.upper(), fill=(255, 255, 255), font=f_kick)

    f_title = _font(42, bold=True)
    title_lines = _wrap(draw, title, f_title, W - 160)
    y = main_top + 48
    for line in title_lines:
        draw.text((78, y), line, fill=WHITE, font=f_title)
        y += 52

    f_sub = _font(23)
    y += 12
    for line in _wrap(draw, subtitle, f_sub, int(W * 0.84)):
        draw.text((78, y), line, fill=(245, 245, 245), font=f_sub)
        y += 32

    # caja elaboración
    y += 40
    box1 = (78, y, 780, y + 96)
    draw.rounded_rectangle(box1, radius=18, outline=(255, 255, 255), width=2, fill=(90, 20, 40))
    f_box = _font(21, bold=True)
    f_box_body = _font(20)
    draw.text((98, y + 18), "Elaboración técnica:", fill=WHITE, font=f_box)
    draw.text(
        (98, y + 52),
        f"Observatorio de Inteligencia Artificial — UCCuyo    Fecha: {year}",
        fill=WHITE,
        font=f_box_body,
    )

    # caja equipo
    y += 124
    box2 = (78, y, W - 78, y + 220)
    draw.rounded_rectangle(box2, radius=18, outline=(255, 255, 255), width=2, fill=(95, 22, 45))
    f_team_t = _font(19, bold=True)
    draw.text((98, y + 18), "DIRECCIÓN Y EQUIPO RESPONSABLE", fill=WHITE, font=f_team_t)
    f_role = _font(19, bold=True)
    f_people = _font(19)
    rows = [
        ("Dirección general:", "Claudio Larrea Arnau"),
        (
            "Equipo ejecutivo:",
            "Belén Arias · Javier Coria · José La Malfa · Laura Pizarro · Stefania Young",
        ),
        ("Asesor externo:", "Frederic Marimon"),
    ]
    yy = y + 58
    for role, people in rows:
        draw.text((98, yy), role, fill=(230, 230, 230), font=f_role)
        rw = int(draw.textlength(role + "  ", font=f_role))
        people_lines = _wrap(draw, people, f_people, W - 200 - rw)
        draw.text((98 + rw, yy), people_lines[0], fill=WHITE, font=f_people)
        yy += 30
        for extra in people_lines[1:]:
            draw.text((98, yy), extra, fill=WHITE, font=f_people)
            yy += 26
        yy += 10

    # pie
    foot_y = H - 170
    draw.line((78, foot_y, W - 78, foot_y), fill=WHITE, width=2)
    f_foot = _font(19)
    mission = (
        "Promovemos el análisis, la formación, la investigación y la vinculación institucional "
        "sobre el impacto y las aplicaciones de la inteligencia artificial, con enfoque académico, ético y regional."
    )
    yy = foot_y + 20
    for line in _wrap(draw, mission, f_foot, W - 160):
        draw.text((78, yy), line, fill=(240, 240, 240), font=f_foot)
        yy += 28

    # franja blanca inferior (como el PDF de referencia)
    draw.rectangle((0, H - 28, W, H), fill=WHITE)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
