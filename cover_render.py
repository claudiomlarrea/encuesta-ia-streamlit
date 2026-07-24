"""Portada institucional (PNG) — tipografía grande y fuentes embebidas (Cloud + local)."""
from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parent / "assets"
LOGO_PATH = ASSETS / "logo_observatorio_ia.png"
FONTS_DIR = ASSETS / "fonts"

# A4 @ 240 dpi — letras grandes al abrir el Word a página completa
DPI = 240
W, H = int(210 / 25.4 * DPI), int(297 / 25.4 * DPI)  # ≈ 1984 × 2806
GREEN = (6, 74, 56)
WHITE = (255, 255, 255)
MARGIN = 100


def _font(size: int, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Prioriza fuentes embebidas (Streamlit Cloud no tiene las de macOS)."""
    bundled: list[Path] = []
    if serif:
        bundled += [
            FONTS_DIR / ("DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"),
            FONTS_DIR / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
        ]
    else:
        bundled += [
            FONTS_DIR / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
            FONTS_DIR / ("DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"),
        ]

    # Matplotlib (si está instalado) — mismo set DejaVu
    try:
        import matplotlib

        mpl = Path(matplotlib.__file__).resolve().parent / "mpl-data" / "fonts" / "ttf"
        if serif:
            bundled += [
                mpl / ("DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"),
                mpl / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
            ]
        else:
            bundled += [
                mpl / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
            ]
    except Exception:  # noqa: BLE001
        pass

    system: list[str] = []
    if bold:
        system += [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
    else:
        system += [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Georgia.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]

    for path in [*bundled, *map(Path, system)]:
        try:
            if Path(path).exists():
                return ImageFont.truetype(str(path), size=size)
        except OSError:
            continue

    # Último recurso: truetype default de Pillow 10+ con size
    try:
        return ImageFont.load_default(size=size)  # type: ignore[call-arg]
    except TypeError:
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
    img = Image.new("RGB", (W, H))
    px = img.load()
    c0 = (74, 12, 31)
    c1 = (156, 39, 72)
    for y in range(H):
        ty = y / max(H - 1, 1)
        for x in range(0, W, 3):
            tx = x / max(W - 1, 1)
            u = min(1.0, max(0.0, 0.62 * ty + 0.38 * tx))
            rgb = (
                int(c0[0] + (c1[0] - c0[0]) * u),
                int(c0[1] + (c1[1] - c0[1]) * u),
                int(c0[2] + (c1[2] - c0[2]) * u),
            )
            for dx in range(3):
                if x + dx < W:
                    px[x + dx, y] = rgb
    return img


def _paste_circular_logo(base: Image.Image, logo_path: Path, xy: tuple[int, int], size: int) -> None:
    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((size, size), Image.Resampling.LANCZOS)
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

    # barra verde
    bar_h = 110
    draw.rectangle((0, 0, W, bar_h), fill=GREEN)
    f_bar = _font(40, bold=True)
    bar_txt = "UNIVERSIDAD CATÓLICA DE CUYO  ·  OBSERVATORIO DE INTELIGENCIA ARTIFICIAL"
    tw = draw.textlength(bar_txt, font=f_bar)
    draw.text(((W - tw) / 2, 34), bar_txt, fill=WHITE, font=f_bar)

    # logo + marca
    logo_x, logo_y = MARGIN, bar_h + 44
    logo_size = 210
    if LOGO_PATH.exists():
        _paste_circular_logo(img, LOGO_PATH, (logo_x, logo_y), logo_size)
        draw = ImageDraw.Draw(img)

    f_uni = _font(48, bold=True)
    f_obs = _font(58, bold=True)
    brand_x = logo_x + logo_size + 44
    draw.text((brand_x, logo_y + 48), "Universidad Católica de Cuyo", fill=WHITE, font=f_uni)
    draw.text((brand_x, logo_y + 112), "Observatorio de Inteligencia Artificial", fill=WHITE, font=f_obs)

    # títulos
    main_top = logo_y + logo_size + 72
    f_kick = _font(48, bold=True)
    draw.text((MARGIN, main_top), kicker.upper(), fill=WHITE, font=f_kick)

    f_title = _font(86, bold=True, serif=True)
    title_lines = _wrap(draw, title, f_title, W - 2 * MARGIN)
    y = main_top + 78
    for line in title_lines:
        draw.text((MARGIN, y), line, fill=WHITE, font=f_title)
        y += 100

    f_sub = _font(48)
    y += 30
    for line in _wrap(draw, subtitle, f_sub, int(W * 0.90)):
        draw.text((MARGIN, y), line, fill=(245, 245, 245), font=f_sub)
        y += 58

    # caja elaboración
    y += 50
    box1_h = 180
    box1 = (MARGIN, y, W - MARGIN, y + box1_h)
    draw.rounded_rectangle(box1, radius=28, outline=WHITE, width=4, fill=(90, 20, 40))
    f_box = _font(44, bold=True)
    f_box_body = _font(42)
    draw.text((MARGIN + 40, y + 40), "Elaboración técnica:", fill=WHITE, font=f_box)
    draw.text(
        (MARGIN + 40, y + 104),
        f"Observatorio de Inteligencia Artificial — UCCuyo    Fecha: {year}",
        fill=WHITE,
        font=f_box_body,
    )

    # caja equipo
    y += box1_h + 40
    box2_h = 400
    box2 = (MARGIN, y, W - MARGIN, y + box2_h)
    draw.rounded_rectangle(box2, radius=28, outline=WHITE, width=4, fill=(95, 22, 45))
    f_team_t = _font(42, bold=True)
    draw.text((MARGIN + 40, y + 36), "DIRECCIÓN Y EQUIPO RESPONSABLE", fill=WHITE, font=f_team_t)
    f_role = _font(42, bold=True)
    f_people = _font(42)
    rows = [
        ("Dirección general:", "Claudio Larrea Arnau"),
        (
            "Equipo ejecutivo:",
            "Belén Arias · Javier Coria · José La Malfa · Laura Pizarro · Stefania Young",
        ),
        ("Asesor externo:", "Frederic Marimon"),
    ]
    yy = y + 110
    for role, people in rows:
        draw.text((MARGIN + 40, yy), role, fill=(230, 230, 230), font=f_role)
        rw = int(draw.textlength(role + "  ", font=f_role))
        people_lines = _wrap(draw, people, f_people, W - 2 * MARGIN - 90 - rw)
        draw.text((MARGIN + 40 + rw, yy), people_lines[0], fill=WHITE, font=f_people)
        yy += 54
        for extra in people_lines[1:]:
            draw.text((MARGIN + 40, yy), extra, fill=WHITE, font=f_people)
            yy += 50
        yy += 18

    # pie
    foot_y = H - 300
    draw.line((MARGIN, foot_y, W - MARGIN, foot_y), fill=WHITE, width=4)
    f_foot = _font(40)
    mission = (
        "Promovemos el análisis, la formación, la investigación y la vinculación institucional "
        "sobre el impacto y las aplicaciones de la inteligencia artificial, con enfoque académico, ético y regional."
    )
    yy = foot_y + 40
    for line in _wrap(draw, mission, f_foot, W - 2 * MARGIN):
        draw.text((MARGIN, yy), line, fill=(240, 240, 240), font=f_foot)
        yy += 50

    draw.rectangle((0, H - 44, W, H), fill=WHITE)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
