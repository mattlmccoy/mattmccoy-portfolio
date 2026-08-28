"""Render the LinkedIn banner (1584x396) from the extracted cross-section fields.

Run `extract_cross.py` first; this script reads only the .npz field data it wrote
and redraws everything else -- ground, colour ramps, part outlines, electrode bars,
hot/cold markers, type. No matplotlib chrome, no baked-in callouts, no figure
screenshots.

  warm ramp  = physics, what the RF does to the part
  cool ramp  = design, what we choose to deposit

Layout is checked at render time rather than by eye: overlong copy and any left
column that would run under LinkedIn's profile photo raise instead of shipping
silently broken.

Usage:  python3 tools/banner/make_banner3.py [output.png]
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Sequence, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

HERE = Path(__file__).resolve().parent
DATA = HERE / "build"

W, H = 1584, 396                  # LinkedIn cover image
LEFT_COL_MAX_W = 640              # copy wider than this collides with the panels
LEFT_COL_MAX_Y = 292              # below this the profile photo covers the column

BG = (10, 10, 10)
TEAL = (60, 187, 177)
WHITE = (250, 250, 250)
DIM = (150, 157, 157)
FAINT = (100, 106, 106)

FONT_DIRS = [HERE / "fonts", Path.home() / "Library/Fonts", Path("/Library/Fonts")]
FONT_HELP = """
Missing a brand font: {names}

Space Grotesk and Space Mono are the site's own faces (see css/styles.css). Both
are SIL OFL. Fetch them into tools/banner/fonts/ with:

  mkdir -p tools/banner/fonts
  curl -sSL -o "tools/banner/fonts/SpaceGrotesk-Medium.ttf" \\
    "https://github.com/google/fonts/raw/main/ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf"
  curl -sSL -o "tools/banner/fonts/SpaceMono-Regular.ttf" \\
    "https://github.com/google/fonts/raw/main/ofl/spacemono/SpaceMono-Regular.ttf"
  curl -sSL -o "tools/banner/fonts/SpaceMono-Bold.ttf" \\
    "https://github.com/google/fonts/raw/main/ofl/spacemono/SpaceMono-Bold.ttf"
"""

# Warm ramp: what the RF does to the part.
THERMAL: Sequence[Tuple[float, Tuple[int, int, int]]] = (
    (0.00, (14, 10, 34)), (0.28, (86, 22, 92)), (0.55, (198, 58, 68)),
    (0.78, (245, 140, 42)), (1.00, (255, 232, 170)),
)
# Cool ramp: what we choose to deposit.
MATERIAL: Sequence[Tuple[float, Tuple[int, int, int]]] = (
    (0.00, (9, 22, 28)), (0.30, (18, 74, 84)), (0.60, (52, 152, 152)),
    (0.82, (132, 216, 202)), (1.00, (232, 252, 245)),
)

EYEBROW = "PhD RESEARCH  ·  GEORGIA TECH"
TITLE = ("Radio Frequency", "Additive Manufacturing")
SUBTITLE = "A new polymer powder-bed process for volumetric sintering"
BULLETS = (
    ("Invented the process and built the custom machine",),
    ("Developed the materials, jetting, controls, and matched RF system",),
    ("Built the physics and inverse-design tools that turn geometry",
     "into printable material and exposure maps"),
)
CAPTION = "UNIFORM DOPANT → NONUNIFORM MELT → PRINTABLE GRADED DOPANT MAP"
PROVENANCE = "HEATR SIMULATION"


def find_font(*names: str) -> Optional[Path]:
    for d in FONT_DIRS:
        if d.is_dir():
            for n in names:
                if (d / n).is_file():
                    return d / n
    return None


def load(names: Tuple[str, ...], size: int) -> ImageFont.FreeTypeFont:
    p = find_font(*names)
    if p is None:
        raise SystemExit(FONT_HELP.format(names=", ".join(names)))
    return ImageFont.truetype(str(p), size)


def ramp(values: np.ndarray, stops: Sequence) -> np.ndarray:
    xs = np.array([s[0] for s in stops])
    cols = np.array([s[1] for s in stops], dtype=float)
    out = np.zeros((*values.shape, 3))
    for c in range(3):
        out[..., c] = np.interp(values, xs, cols[:, c])
    return out.astype(np.uint8)


def tracked(draw, xy, text, font, fill, tracking=0.0) -> float:
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x - xy[0]


def text_w(draw, text, font, tracking=0.0) -> float:
    return sum(draw.textlength(c, font=font) + tracking for c in text)


def outline_of(mask: np.ndarray, width: int = 2) -> np.ndarray:
    return mask & ~ndimage.binary_erosion(mask, np.ones((3, 3)), iterations=width)


def render_field(
    field: np.ndarray,
    mask: np.ndarray,
    stops: Sequence,
    cell: int,
    stroke: Optional[Tuple[int, int, int]] = TEAL,
    fill_mask: Optional[np.ndarray] = None,
    base: Optional[Tuple[int, int, int]] = None,
) -> Image.Image:
    """Draw one part on transparent ground in the banner's own language."""
    ys, xs = np.where(mask)
    pad = 6
    sy = slice(max(0, ys.min() - pad), ys.max() + pad + 1)
    sx = slice(max(0, xs.min() - pad), xs.max() + pad + 1)
    field, mask = field[sy, sx], mask[sy, sx]
    if fill_mask is not None:
        fill_mask = fill_mask[sy, sx]

    body = fill_mask if fill_mask is not None else mask
    rgb = np.where(body[..., None], ramp(np.clip(field, 0, 1), stops), 0).astype(np.uint8)

    if base is not None:
        # Unmelted material is still material: give it a quiet tone so the
        # silhouette reads instead of collapsing into an empty outline.
        rgb = np.where((mask & ~body)[..., None], np.array(base, np.uint8), rgb)
        alpha = np.where(mask, 255, 0).astype(np.uint8)
    else:
        alpha = np.where(body, 255, 0).astype(np.uint8)

    if stroke is not None:
        edge = outline_of(mask, 2)
        rgb = np.where(edge[..., None], np.array(stroke, np.uint8), rgb)
        alpha = np.where(edge, 255, alpha)

    im = Image.fromarray(np.dstack([rgb, alpha]), "RGBA")
    h, w = mask.shape
    s = min(cell / w, cell / h)
    im = im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)
    tile = Image.new("RGBA", (cell, cell), (0, 0, 0, 0))
    tile.paste(im, ((cell - im.width) // 2, (cell - im.height) // 2), im)
    return tile


def extreme_points(field: np.ndarray, mask: np.ndarray, cell: int):
    """Hottest and coldest cell of the part, in tile coordinates."""
    ys, xs = np.where(mask)
    pad = 6
    y0, x0 = max(0, ys.min() - pad), max(0, xs.min() - pad)
    sub_f = field[y0: ys.max() + pad + 1, x0: xs.max() + pad + 1]
    sub_m = mask[y0: ys.max() + pad + 1, x0: xs.max() + pad + 1]
    h, w = sub_m.shape
    s = min(cell / w, cell / h)
    ox, oy = (cell - int(w * s)) // 2, (cell - int(h * s)) // 2

    inner = ndimage.binary_erosion(sub_m, np.ones((3, 3)), iterations=3)
    if inner.sum() < 20:
        inner = sub_m
    vals = np.where(inner, sub_f, np.nan)
    hot = np.unravel_index(np.nanargmax(vals), vals.shape)
    cold = np.unravel_index(np.nanargmin(vals), vals.shape)
    to_tile = lambda p: (int(p[1] * s + ox), int(p[0] * s + oy))
    return to_tile(hot), to_tile(cold)


def marker(draw, point, label, anchor, font, colour, align="left"):
    """Ring on the located cell, elbow leader out to a free corner of the tile."""
    x, y = point
    ax, ay = anchor
    r = 5
    tw = text_w(draw, label, font, 0.8)
    lx = ax if align == "left" else ax - tw
    ly = ay + 5

    draw.line((x, y + (r if ly > y else -r), x, ly), fill=colour, width=1)
    draw.line((x, ly, (lx + tw + 5) if align == "left" else (lx - 5), ly),
              fill=colour, width=1)
    draw.ellipse((x - r, y - r, x + r, y + r), outline=colour, width=2)
    draw.ellipse((x - 1, y - 1, x + 1, y + 1), fill=colour)
    tracked(draw, (lx, ay), label, font, colour, 0.8)


def build(out: Path) -> None:
    for name in ("heat.npz", "melt.npz", "dopant.npz"):
        if not (DATA / name).is_file():
            raise SystemExit(
                f"missing {DATA / name}\nRun: python3 tools/banner/extract_cross.py"
            )

    f_title = load(("SpaceGrotesk-Medium.ttf",), 36)
    f_subtitle = load(("SpaceGrotesk-Medium.ttf",), 17)
    f_sub = load(("SpaceMono-Regular.ttf",), 14)
    f_eyebrow = load(("SpaceMono-Bold.ttf",), 14)
    f_tick = load(("SpaceMono-Regular.ttf",), 11)
    f_plabel = load(("SpaceMono-Bold.ttf",), 12)
    f_arrow = load(("SpaceMono-Bold.ttf",), 17)

    heat = np.load(DATA / "heat.npz")
    melt = np.load(DATA / "melt.npz")
    dop = np.load(DATA / "dopant.npz")

    px0, px1 = 800, W - 64
    cell = 218
    gap = (px1 - px0 - cell * 3) / 2
    ptop = 78

    panels = [
        ("RF HEATING", render_field(heat["field"], heat["mask"], THERMAL, cell)),
        ("PREDICTED MELT · UNIFORM DOPANT",
         render_field(melt["field"], melt["mask"], THERMAL, cell,
                      fill_mask=melt["melt"], base=(38, 42, 54))),
        ("ADJOINT-DESIGNED DOPANT MAP",
         render_field(dop["dopant"], dop["mask"], MATERIAL, cell)),
    ]

    card = Image.new("RGBA", (W, H), BG + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for i, (_lab, tile) in enumerate(panels):
        x = int(px0 + i * (cell + gap))
        glow.paste(tile, (x, ptop), tile)
        layer.paste(tile, (x, ptop), tile)
    card = Image.alpha_composite(card, glow.filter(ImageFilter.GaussianBlur(18)))
    card = Image.alpha_composite(card, layer).convert("RGB")
    draw = ImageDraw.Draw(card)

    # electrode bars, drawn here rather than inherited from the source figure
    for i in range(2):                                     # physics panels only
        x = int(px0 + i * (cell + gap))
        for yy, tag in ((ptop - 6, "+V"), (ptop + cell + 4, "GND")):
            draw.line((x, yy, x + cell, yy), fill=(64, 70, 70), width=2)
            tracked(draw, (x, yy - 15 if tag == "+V" else yy + 5), tag,
                    f_tick, (96, 102, 102), 0.8)

    # hot / cold markers, located from the field itself rather than hard-coded
    hot, cold = extreme_points(heat["field"], heat["mask"], cell)
    marker(draw, (px0 + hot[0], ptop + hot[1]), "HOT TIP",
           (px0 + cell - 2, ptop + cell - 14), f_tick, (255, 198, 122), align="right")
    marker(draw, (px0 + cold[0], ptop + cold[1]), "COLD RECESS",
           (px0 + 4, ptop + 5), f_tick, (132, 198, 236), align="left")

    for i, (label, _t) in enumerate(panels):
        x = int(px0 + i * (cell + gap))
        colour = TEAL if i == 2 else DIM
        tw = text_w(draw, label, f_plabel, 0.9)
        tracked(draw, (x + (cell - tw) / 2, ptop - 40), label, f_plabel, colour, 0.9)
        if i < 2:
            draw.text((x + cell + gap / 2 - 7, ptop + cell / 2 - 13), "→",
                      font=f_arrow, fill=(112, 119, 119))

    # --- left column ------------------------------------------------------
    mx = 64
    y = 40
    draw.line((mx, y + 8, mx + 34, y + 8), fill=TEAL, width=3)
    tracked(draw, (mx + 48, y), EYEBROW, f_eyebrow, TEAL, 1.4)

    y = 70
    for line in TITLE:
        draw.text((mx, y), line, font=f_title, fill=WHITE)
        y += 42

    draw.text((mx, 162), SUBTITLE, font=f_subtitle, fill=(186, 193, 193))

    y = 194
    for group in BULLETS:
        draw.line((mx, y + 9, mx + 9, y + 9), fill=TEAL, width=2)
        for line in group:
            if text_w(draw, line, f_sub) > LEFT_COL_MAX_W:
                raise SystemExit(f"bullet line overflows the left column: {line!r}")
            draw.text((mx + 21, y), line, font=f_sub, fill=(166, 173, 173))
            y += 21
        y += 2
    if y > LEFT_COL_MAX_Y:
        raise SystemExit(f"left column runs into the avatar zone (ends {y})")

    # --- caption strip ----------------------------------------------------
    cy = ptop + cell + 40
    draw.line((px0, cy, px1, cy), fill=(44, 48, 48), width=1)
    lw = text_w(draw, CAPTION, f_tick, 0.7)
    tw = text_w(draw, PROVENANCE, f_tick, 0.7)
    if px0 + lw + 24 > px1 - tw:
        raise SystemExit("caption strip overflows; shorten the caption or provenance")
    tracked(draw, (px0, cy + 18), CAPTION, f_tick, DIM, 0.7)
    tracked(draw, (px1 - tw, cy + 18), PROVENANCE, f_tick, FAINT, 0.7)

    card.save(out, "PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size:,} bytes, {W}x{H})")


if __name__ == "__main__":
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "linkedin-banner.png"
    build(dest)
