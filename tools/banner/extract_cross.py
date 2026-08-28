"""Extract the cross-section fields the LinkedIn banner is drawn from.

Reads published RFAM figures and writes three small .npz field/mask pairs into
`build/`. `make_banner3.py` then re-illustrates those fields; it never touches the
source images itself.

Sources -- three runs of the same nominal cross section, NOT one chained run:

  heat    sources/fig_reentrant_shadow_c.png       cross panel, RF heating Q,
                                                   uniform dopant
  melt    assets/decks/.../solve/                  predicted melt region,
          fig_cross_static_uniform_thumb.webp      uniform dopant
  dopant  assets/decks/.../ch3/                    adjoint-designed dopant map,
          fig_printer_fgm_maps.webp                4 bpp printable raster

`compare()` prints each source's aspect and solidity so the assumption that they
share a geometry stays checkable rather than assumed. They agreed to within
0.96/1.00/1.00 aspect and 0.54/0.54/0.57 solidity when the banner was made.

The reentrant sheet is vendored under sources/ because the deck authoring folder
it normally lives in (assets/documents/Geometry-Dependent .../) is gitignored, so
the repo could not otherwise regenerate the banner.

Usage:  python3 tools/banner/extract_cross.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from matplotlib import colormaps
from PIL import Image
from scipy import ndimage
from scipy.spatial import cKDTree

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DECK = REPO / "assets/decks/rfam-sintering/figures"
OUT = HERE / "build"

# Panel geometry of fig_printer_fgm_maps.webp: a 4x3 grid of square axes.
FGM_PANEL_SIDE = 327
FGM_FRAME_PX = 2600
FGM_FRAME_TOL = 60
FGM_ORDER = [
    "circle", "ellipse", "hexagon", "octagon",
    "pentagon", "rectangle", "square", "diamond",
    "triangle", "star", "lshape", "cross",
]


def invert_colormap(rgb: np.ndarray, name: str = "inferno") -> np.ndarray:
    """Recover the scalar field behind a colour-mapped image.

    Luminance is not a faithful inverse of a perceptual ramp like inferno; using it
    made the field saturate once the bright part outline was excluded from the
    normalisation. Nearest-neighbour lookup against the real LUT recovers the
    underlying 0-1 value instead.
    """
    lut = colormaps[name](np.linspace(0, 1, 256))[:, :3] * 255.0
    _, idx = cKDTree(lut).query(rgb.reshape(-1, 3).astype(float), k=1)
    return (idx.reshape(rgb.shape[:2]) / 255.0).astype(np.float32)


def inpaint(data: np.ndarray, valid: np.ndarray, passes: int = 40) -> np.ndarray:
    """Fill invalid cells by diffusing neighbouring valid values inward.

    scipy's distance_transform_edt(return_indices=True) did not return self-indices
    for background cells here -- it rewrote all 3080 valid pixels and flooded the
    part with the annotation's brightness -- so the fill is explicit and the caller
    checks the result.
    """
    work = np.where(valid, data, 0.0).astype(float)
    known = valid.astype(float)
    for _ in range(passes):
        if known.all():
            break
        num = ndimage.uniform_filter(work, size=3, mode="nearest")
        den = ndimage.uniform_filter(known, size=3, mode="nearest")
        newly = (known == 0) & (den > 1e-6)
        if not newly.any():
            break
        work = np.where(newly, np.divide(num, np.maximum(den, 1e-6)), work)
        known = np.where(newly, 1.0, known)
    return work


def panels_on_dark(path: Path, min_side: int = 150):
    """Find the dark navy field panels in the reentrant-shadow sheet."""
    a = np.asarray(Image.open(path).convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    navy = (b > r) & (b < 90) & (r < 60) & (g < 70)
    navy = ndimage.binary_closing(navy, np.ones((5, 5)))
    lab, _ = ndimage.label(navy)
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if h >= min_side and w >= min_side:
            out.append((sl[0].start, sl[0].stop, sl[1].start, sl[1].stop))
    out.sort(key=lambda t: t[0])
    return out


def extract_heat() -> None:
    """Cross panel of the reentrant sheet: warm ink on navy, white outline."""
    src = HERE / "sources/fig_reentrant_shadow_c.png"
    boxes = panels_on_dark(src)
    print(f"  reentrant panels found: {len(boxes)}")
    if len(boxes) != 3:
        raise SystemExit("expected 3 panels (L, cross, T); refusing to guess")
    y0, y1, x0, x1 = boxes[1]          # reading order: L, cross, T

    a = np.asarray(Image.open(src).convert("RGB").crop((x0, y0, x1, y1))).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]

    # The part is everything warmer than the navy ground, plus its light outline.
    warm = (r - b) > 18
    light = (r > 150) & (g > 150) & (b > 150)
    part = ndimage.binary_fill_holes(
        ndimage.binary_closing(warm | light, np.ones((5, 5)))
    )
    part = ndimage.binary_opening(part, np.ones((3, 3)))
    lab, n = ndimage.label(part)                 # drop the +V / GND electrode bars
    if n:
        sizes = ndimage.sum(part, lab, range(1, n + 1))
        part = lab == (int(np.argmax(sizes)) + 1)

    lum = a.sum(2) / 3.0
    sat = a.max(2) - a.min(2)

    # The source bakes a white "shadow" tag and two ring markers onto the part.
    # Those are annotation, not field. No low-luminance clause here: the cold
    # recess is legitimately dark purple, and an earlier `lum < 42` term swallowed
    # 65% of the real field.
    chrome = part & (lum > 165) & (sat < 60)
    chrome = ndimage.binary_dilation(chrome, np.ones((3, 3)), iterations=1) & part
    frac = chrome.sum() / max(part.sum(), 1)
    print(f"  heat   annotation pixels removed from field: {frac:.1%}")
    if frac > 0.45:      # ~22% of this is the part's own outline, which we redraw
        raise SystemExit("chrome mask ate the field; thresholds are wrong")

    scalar = invert_colormap(a.astype(np.uint8), "inferno")
    valid = part & ~chrome
    ref_lo, ref_hi = np.percentile(scalar[valid], [1.0, 99.0])
    scalar = inpaint(scalar, valid)

    # The annotation ink was the brightest thing in the panel, so a leaking fill
    # shows up as part pixels far above the real field's range.
    over = (scalar[part] > ref_hi + 0.05).mean()
    print(f"  heat   part above pre-fill p99 after inpaint: {over:.1%}")
    if over > 0.10:
        raise SystemExit("inpaint leaked annotation brightness into the field")

    q = np.clip((np.where(part, scalar, 0.0) - ref_lo) / max(ref_hi - ref_lo, 1e-6), 0, 1)
    np.savez_compressed(OUT / "heat.npz", field=q.astype(np.float32), mask=part)
    print(f"  heat   {part.shape[1]}x{part.shape[0]}  fill {part.mean():.3f}")


def extract_melt() -> None:
    """Static uniform cross thumb: melt region on black, cyan nominal outline."""
    src = DECK / "solve/fig_cross_static_uniform_thumb.webp"
    a = np.asarray(Image.open(src).convert("RGB")).astype(int)
    a = a[:560]                      # drop the baked-in "IoU 0.55" corner tag
    r, g, b = a[..., 0], a[..., 1], a[..., 2]

    cyan = (b > 150) & (g > 150) & (r < 150)          # nominal part outline
    nominal = ndimage.binary_fill_holes(ndimage.binary_closing(cyan, np.ones((5, 5))))
    melt = ndimage.binary_opening((r > 90) & (r >= b), np.ones((3, 3)))

    lum = a.sum(2) / 3.0
    field = np.where(nominal, lum, 0.0)
    hi = np.percentile(field[nominal], 99.0)
    field = np.clip(field / max(hi, 1e-6), 0, 1)

    np.savez_compressed(
        OUT / "melt.npz",
        field=field.astype(np.float32), mask=nominal, melt=melt,
    )
    print(f"  melt   {nominal.shape[1]}x{nominal.shape[0]}  fill {nominal.mean():.3f}  "
          f"melted/part {melt.sum() / max(nominal.sum(), 1):.3f}")


def extract_dopant() -> None:
    """Cross panel of the printable FGM dopant-map sheet.

    Dark ink = high binder level, enclosed by a red nominal contour. The contour
    alone is not a usable barrier -- where the dopant saturates, black ink covers
    the thin red line and breaks it into fragments -- so the barrier is taken as
    "red OR non-white", which is continuous by construction.
    """
    src = DECK / "ch3/fig_printer_fgm_maps.webp"
    img = Image.open(src).convert("RGB")
    rgb = np.asarray(img).astype(int)
    gray = np.asarray(img.convert("L")).astype(np.float32)

    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    neutral = (abs(r - g) < 6) & (abs(g - b) < 6)
    frame = neutral & (r > 140) & (r < 175)

    labels, _ = ndimage.label(frame, structure=np.ones((3, 3)))
    panels = []
    for i, sl in enumerate(ndimage.find_objects(labels)):
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        count = int((labels[sl] == i + 1).sum())
        if (abs(h - FGM_PANEL_SIDE) < 12 and abs(w - FGM_PANEL_SIDE) < 12
                and abs(count - FGM_FRAME_PX) < FGM_FRAME_TOL):
            panels.append((sl[0].start, sl[0].stop, sl[1].start, sl[1].stop))
    panels.sort(key=lambda p: (round(p[0] / 100), p[2]))
    print(f"  dopant panels found: {len(panels)}")
    if len(panels) != len(FGM_ORDER):
        raise SystemExit(
            f"expected {len(FGM_ORDER)} FGM panels, found {len(panels)} -- "
            "refusing to guess the mapping"
        )

    y0, y1, x0, x1 = panels[FGM_ORDER.index("cross")]
    inset = 5
    sy, sx = slice(y0 + inset, y1 - inset), slice(x0 + inset, x1 - inset)
    sub_gray = gray[sy, sx]
    redness = ((r - g) + (r - b))[sy, sx]

    barrier = (redness > 50) | (sub_gray < 245)
    free = ~barrier
    seed = np.zeros_like(free)
    seed[0, :], seed[-1, :] = free[0, :], free[-1, :]
    seed[:, 0], seed[:, -1] = free[:, 0], free[:, -1]
    interior = ~ndimage.binary_propagation(seed, mask=free)
    interior = ndimage.binary_opening(ndimage.binary_fill_holes(interior),
                                      np.ones((3, 3)))
    if interior.sum() < 500:
        raise SystemExit("cross dopant fill produced an empty interior")

    dopant = np.where(interior, 1.0 - sub_gray / 255.0, 0.0)
    hi = np.percentile(dopant[interior], 99.5)
    dopant = np.clip(dopant / max(hi, 1e-6), 0.0, 1.0)

    np.savez_compressed(OUT / "dopant.npz",
                        dopant=dopant.astype(np.float32), mask=interior)
    print(f"  dopant {interior.shape[1]}x{interior.shape[0]}  "
          f"fill {interior.mean():.3f}  mean {dopant[interior].mean():.3f}")


def compare() -> None:
    """Print each source's cross geometry so the shared-shape claim stays checkable."""
    masks = {
        "reentrant heat": np.load(OUT / "heat.npz")["mask"],
        "static melt": np.load(OUT / "melt.npz")["mask"],
        "fgm dopant": np.load(OUT / "dopant.npz")["mask"],
    }
    print("\n  cross geometry by source (different campaigns, same nominal shape):")
    for name, m in masks.items():
        ys, xs = np.where(m)
        sub = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        aspect = (xs.max() - xs.min() + 1) / (ys.max() - ys.min() + 1)
        print(f"    {name:16} aspect {aspect:.3f}   solidity {sub.mean():.3f}")
    print("  The banner labels these as one geometry, never as one run.")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    extract_heat()
    extract_melt()
    extract_dopant()
    compare()
    print(f"\nwrote field data to {OUT}")
