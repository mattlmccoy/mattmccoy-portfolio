# LinkedIn banner

Regenerates `linkedin-banner.png` (1584×396) from real HEATR output.

The banner is **re-illustrated, not screenshotted**. `extract_cross.py` pulls only
scalar fields and masks out of published RFAM figures; `make_banner3.py` redraws
everything else — ground, colour ramps, part outlines, electrode bars, hot/cold
markers, type. No matplotlib chrome or baked-in callouts survive into the output.

## Run

```bash
python3 tools/banner/extract_cross.py     # writes build/*.npz
python3 tools/banner/make_banner3.py      # writes linkedin-banner.png
```

Needs `numpy`, `scipy`, `pillow`, `matplotlib` (matplotlib only for the inferno LUT).

### Fonts

The site's own faces, both SIL OFL. Not committed — fetch once into
`tools/banner/fonts/` (gitignored), or install them system-wide:

```bash
mkdir -p tools/banner/fonts
curl -sSL -o "tools/banner/fonts/SpaceGrotesk-Medium.ttf" "https://github.com/google/fonts/raw/main/ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf"
curl -sSL -o "tools/banner/fonts/SpaceMono-Regular.ttf" "https://github.com/google/fonts/raw/main/ofl/spacemono/SpaceMono-Regular.ttf"
curl -sSL -o "tools/banner/fonts/SpaceMono-Bold.ttf" "https://github.com/google/fonts/raw/main/ofl/spacemono/SpaceMono-Bold.ttf"
```

## Panels

| Panel | Source |
|---|---|
| RF HEATING | `sources/fig_reentrant_shadow_c.png`, cross panel, uniform dopant |
| PREDICTED MELT · UNIFORM DOPANT | `assets/decks/rfam-sintering/figures/solve/fig_cross_static_uniform_thumb.webp` |
| ADJOINT-DESIGNED DOPANT MAP | `assets/decks/rfam-sintering/figures/ch3/fig_printer_fgm_maps.webp`, cross panel |

`sources/fig_reentrant_shadow_c.png` is vendored because the deck authoring folder
it normally lives in (`assets/documents/Geometry-Dependent .../`) is gitignored.
Without it the repo could not regenerate the banner. The other two sources are
tracked deck figures and are read in place.

## Honesty constraints

These are load-bearing. Changing them changes what the banner claims.

- **Three campaigns, not one run.** The three panels come from three separate runs
  of the same nominal cross section. `compare()` prints aspect and solidity for each
  so the shared-geometry assumption stays checkable — they agreed to within
  0.96/1.00/1.00 aspect and 0.54/0.54/0.57 solidity. The banner labels them as one
  geometry and never as one part progressing through three stages. Do not add copy
  that implies a single chained run.
- **No fabricated fields.** Every field is extracted from a published figure. Nothing
  is synthesised, and one run's field is never mapped onto another's mask.
- **Simulation only.** The provenance line says `HEATR SIMULATION`. These are solver
  outputs, not measured prints.

## Two extraction traps

Both of these once shipped a plausible-looking, wrong panel. The guards that catch
them are in the code; leave them in.

1. **The cold recess is real signal, not annotation.** An early chrome filter cut
   `lum < 42` to remove the source's baked-in white `shadow` tag, and swallowed 65%
   of the actual field — the recess is legitimately dark purple. The filter now keys
   on light, low-saturation pixels only, and raises if it exceeds 45% of the part.
2. **`scipy.ndimage.distance_transform_edt(return_indices=True)` did not return
   self-indices for background cells here.** It rewrote all 3080 valid pixels and
   flooded the part with the annotation's brightness, rendering a flat cream cross
   that looked fine and was entirely wrong. Replaced by an explicit diffusion
   `inpaint()`, guarded by a check that fails if filled pixels exceed the pre-fill
   p99 (currently 2.6%, threshold 10%).

Related: the scalar is recovered by **inverting the inferno LUT**, not from
luminance. Luminance is not a faithful inverse of a perceptual ramp and saturated
the field once the bright part outline left the normalisation.

## Layout guards

`make_banner3.py` raises instead of shipping a broken layout:

- bullet lines wider than the left column (640 px)
- a left column extending past y=292, where LinkedIn's profile photo covers it
- a caption strip whose text would run under the provenance label

After changing copy, confirm the avatar zone is still empty:

```bash
python3 -c "
from PIL import Image; import numpy as np
a=np.asarray(Image.open('tools/banner/linkedin-banner.png').convert('RGB')).astype(int).sum(2)
yy,xx=np.mgrid[0:396,0:1584]
print('avatar disc max brightness:', int(a[((xx-168)**2+(yy-396)**2)<105**2].max()), '(background = 30)')"
```

## Other geometries

`extract_heat()` takes the middle of three panels in the reentrant sheet — the
reading order is L-shape, cross, T-shape. Index `boxes[0]` or `boxes[2]` to switch.
Note the melt and dopant panels are cross-only, so changing the heat panel alone
would break the shared-geometry claim above.
