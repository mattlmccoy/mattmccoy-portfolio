"""LinkedIn banner (1584x396): what the camera measures vs what the model says.

Run `extract_subsurface.py` first. This reads only the three extracted panels and
redraws the rest -- ground, frames, labels, type.

The claim the banner makes is deliberately narrow. The left panel is MEASURED, the
two right panels are MODEL, and the labels say so. The model's top face was fitted
to the camera, so the banner never implies the subsurface field was validated; it
contrasts what a surface instrument can see against what the forward model says is
happening underneath, which is the actual argument for having the model.

Caption number: at ~473 s the first model cell passes the 171 C nylon melt onset
while the camera reads ~88 C. Both figures are from the source frame.

Usage:  python3 tools/banner/make_banner_rfam.py [output.png]
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from make_banner3 import (  # noqa: E402  (path must be set first)
    BG, DIM, FAINT, TEAL, WHITE, H, W,
    LEFT_COL_MAX_W, LEFT_COL_MAX_Y,
    load, text_w, tracked,
)

DATA = HERE / "build"

PANELS: List[Tuple[str, str, Tuple[int, int, int]]] = [
    ("sub_camera.png", "THERMAL CAMERA · MEASURED", (255, 198, 122)),
    ("sub_temp.png", "TEMPERATURE · MODEL", DIM),
    ("sub_density.png", "DENSIFICATION · MODEL", DIM),
]

EYEBROW = "PhD RESEARCH  ·  GEORGIA TECH"
TITLE = ("Radio Frequency", "Additive Manufacturing")
SUBTITLE = "A new polymer powder-bed process for volumetric sintering"
BULLETS = (
    ("Invented the process and built the custom machine",),
    ("Developed the materials, jetting, controls, and matched RF system",),
    ("Built the physics and inverse-design tools that turn geometry",
     "into printable material and exposure maps"),
)
CAPTION = "FIRST MODEL CELL PASSES 171 °C AT ~473 S · CAMERA READS ~88 °C"
PROVENANCE = "HEATR 3-D"

PANEL_H = 172
STRIP_X0, STRIP_X1 = 800, W - 64
PTOP = 86


def build(out: Path) -> None:
    for _f, _l, _c in PANELS:
        if not (DATA / _f).is_file():
            raise SystemExit(
                f"missing {DATA / _f}\nRun: python3 tools/banner/extract_subsurface.py"
            )

    f_title = load(("SpaceGrotesk-Medium.ttf",), 36)
    f_subtitle = load(("SpaceGrotesk-Medium.ttf",), 17)
    f_sub = load(("SpaceMono-Regular.ttf",), 14)
    f_eyebrow = load(("SpaceMono-Bold.ttf",), 14)
    f_tick = load(("SpaceMono-Regular.ttf",), 11)
    f_plabel = load(("SpaceMono-Bold.ttf",), 11)
    f_arrow = load(("SpaceMono-Bold.ttf",), 17)

    # Uniform panel height, width follows each panel's own aspect, so the strip
    # reads as one figure row rather than three boxes of unrelated scale.
    tiles = []
    for fname, label, colour in PANELS:
        im = Image.open(DATA / fname).convert("RGBA")
        w = max(1, round(im.width * PANEL_H / im.height))
        tiles.append((im.resize((w, PANEL_H), Image.LANCZOS), label, colour))

    total_w = sum(t.width for t, _l, _c in tiles)
    gap = (STRIP_X1 - STRIP_X0 - total_w) / (len(tiles) - 1)
    if gap < 12:
        raise SystemExit(f"panel strip overflows: gap would be {gap:.1f}px")

    card = Image.new("RGBA", (W, H), BG + (255,))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = STRIP_X0
    placed = []
    for tile, label, colour in tiles:
        glow.paste(tile, (int(x), PTOP), tile)
        layer.paste(tile, (int(x), PTOP), tile)
        placed.append((int(x), tile.width, label, colour))
        x += tile.width + gap

    card = Image.alpha_composite(card, glow.filter(ImageFilter.GaussianBlur(18)))
    card = Image.alpha_composite(card, layer).convert("RGB")
    draw = ImageDraw.Draw(card)

    for i, (px, pw, label, colour) in enumerate(placed):
        tw = text_w(draw, label, f_plabel, 0.9)
        tracked(draw, (px + (pw - tw) / 2, PTOP - 22), label, f_plabel, colour, 0.9)
        if i < len(placed) - 1:
            draw.text((px + pw + gap / 2 - 7, PTOP + PANEL_H / 2 - 13), "→",
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
    cy = PTOP + PANEL_H + 42
    draw.line((STRIP_X0, cy, STRIP_X1, cy), fill=(44, 48, 48), width=1)
    lw = text_w(draw, CAPTION, f_tick, 0.7)
    tw = text_w(draw, PROVENANCE, f_tick, 0.7)
    if STRIP_X0 + lw + 24 > STRIP_X1 - tw:
        raise SystemExit("caption strip overflows; shorten the caption")
    tracked(draw, (STRIP_X0, cy + 18), CAPTION, f_tick, DIM, 0.7)
    tracked(draw, (STRIP_X1 - tw, cy + 18), PROVENANCE, f_tick, FAINT, 0.7)

    card.save(out, "PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size:,} bytes, {W}x{H})  panel gap {gap:.1f}px")


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "linkedin-banner-rfam.png")
