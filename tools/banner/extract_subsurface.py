"""Extract the three panels of the 10-20 sintering run for the LinkedIn banner.

Source: sources/subsurface_553s.png -- the collapse-moment frame of
`10-20_subsurface_film_v3.mp4`, the "what the camera sees vs what the model says
is underneath" film.

Panels, left to right in the source:
  camera   thermal camera, top surface   MEASURED
  temp     HEATR 3-D temperature cutaway MODEL
  density  HEATR 3-D relative density    MODEL

The camera panel is already a dark raster and is kept as pixels. The two cutaways
sit on white paper, so the paper is keyed out and only the render survives.

Honesty note carried into the banner: the model's top face was FITTED to the
camera. The banner therefore contrasts measured surface against modelled interior
and never claims a validated subsurface prediction.

Usage:  python3 tools/banner/extract_subsurface.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = Path(__file__).resolve().parent
SRC = HERE / "sources/subsurface_553s.png"
OUT = HERE / "build"

# Measured from the source frame (1920x1080) by connected-component analysis of
# the non-white ink, then trimmed past titles, colourbars and leader lines.
BOXES: Dict[str, Tuple[int, int, int, int]] = {
    "camera": (108, 712, 40, 640),      # y0, y1, x0, x1
    "temp": (252, 545, 796, 1272),
    "density": (150, 352, 1495, 1762),
}


def key_white(a: np.ndarray, thresh: int = 736, feather: float = 40.0) -> Image.Image:
    """Drop the white paper, keep the render, with a soft edge."""
    lum = a.astype(int).sum(2)
    keep = lum < thresh
    if keep.sum() < 500:
        raise SystemExit("white key removed everything; threshold is wrong")
    keep = ndimage.binary_closing(keep, np.ones((3, 3)))
    ys, xs = np.where(keep)
    m = 4
    a = a[max(0, ys.min() - m): ys.max() + m, max(0, xs.min() - m): xs.max() + m]
    lum = a.astype(int).sum(2)
    alpha = np.clip((thresh + 6 - lum) / feather, 0.0, 1.0)
    return Image.fromarray(
        np.dstack([a, (alpha * 255).astype(np.uint8)]), "RGBA"
    )


def extract() -> None:
    if not SRC.is_file():
        raise SystemExit(
            f"missing {SRC}\nThe frame lives in the deck folder outside this repo; "
            "it is vendored under tools/banner/sources/."
        )
    img = Image.open(SRC).convert("RGB")
    if img.size != (1920, 1080):
        raise SystemExit(
            f"frame is {img.size}, expected (1920, 1080); BOXES would be wrong"
        )

    OUT.mkdir(exist_ok=True)
    for name, (y0, y1, x0, x1) in BOXES.items():
        a = np.asarray(img.crop((x0, y0, x1, y1))).astype(np.uint8)
        if name == "camera":
            # Already a dark raster on a dark ground; keep every pixel.
            rgba = np.dstack([a, np.full(a.shape[:2], 255, np.uint8)])
            tile = Image.fromarray(rgba, "RGBA")
        else:
            tile = key_white(a)
        tile.save(OUT / f"sub_{name}.png")
        arr = np.asarray(tile)
        cover = (arr[..., 3] > 10).mean()
        print(f"  {name:8} {tile.size[0]:4}x{tile.size[1]:4}  coverage {cover:5.2f}")

    sheet()


def sheet() -> None:
    """Contact sheet on the banner's ground, so the panels can be eyeballed."""
    cell = 300
    s = Image.new("RGB", (cell * 3 + 40, cell + 20), (10, 10, 10))
    for i, name in enumerate(BOXES):
        t = Image.open(OUT / f"sub_{name}.png").convert("RGBA")
        k = min(cell / t.width, cell / t.height)
        t = t.resize((int(t.width * k), int(t.height * k)), Image.LANCZOS)
        s.paste(t, (10 + i * (cell + 10) + (cell - t.width) // 2,
                    10 + (cell - t.height) // 2), t)
    s.save(OUT / "_subsurface_sheet.png")
    print(f"contact sheet: {OUT / '_subsurface_sheet.png'}")


if __name__ == "__main__":
    extract()
