# Research-page movies

Code for the five short movies on the Research page, one per research area.
They use the group's figure style (`figstyle.py`, copied from the
[glaciology book](https://github.com/rice-glaciology/glaciology-book)), so they
match the book's figures and animations.

```bash
pip install numpy scipy matplotlib        # plus ffmpeg on the PATH
python tools/research_movies/make_movies.py --list                       # what exists
python tools/research_movies/make_movies.py                              # render all (~7 min)
python tools/research_movies/make_movies.py firn                         # one movie
python tools/research_movies/make_movies.py --preview 0.5 --out /tmp/p   # stills only
```

Each movie is written to `static/media/research/<slug>.mp4` with a poster frame
`<slug>.jpg`. Use `--out` with `--preview`, so preview stills don't land in the
site's `static/` folder.

All five are model experiments or synthetic examples, built to show the method
rather than a specific result. The website captions say so.

| Slug | File | Contents |
|---|---|---|
| `ice-flow` | `ice_flow.py`, `flowline.py` | 1D shallow-shelf flowline model of a marine glacier on a bed with a ridge. Ocean melt removes the shelf's buttressing (parameterized as lateral drag). Weertman and Coulomb-limited sliding start from the same state: the Coulomb coefficient is inverted from the Weertman basal stress. |
| `multi-element-radar` | `radar.py` | A sled survey over a synthetic bed. The array maps a swath, not a nadir line. The echogram builds along-track, and repeat-pass vertical velocity is compared with a Lliboutry-shape profile that includes flow over the bed. |
| `firn` | `firn.py` | Lagrangian Herron–Langway firn column, spun up and then forced with 4 K warming and 20 % more accumulation. Shows isochrones, the density profile and the change in firn air content. |
| `submarine-melt` | `shelf_melt.py` | A steady ice shelf with a basal melt channel. Stereo DEM strips arrive over six years; a Lagrangian Dh/Dt for one parcel, plus flux divergence and SMB, gives its melt rate; the melt map fills in where two or more strips overlap. |
| `sea-level-geophysics` | `subsidence.py` | An invented coastline. InSAR and GNSS observe subsidence over 2016–2026; a delayed inelastic-compaction model, with posterior samples of storage and drainage time, projects it to 2050 for two pumping scenarios; relative sea level is shown at a GNSS-IR tide gauge. |

To add or replace a movie, write a function decorated with
`@movie("slug", order)` in a new module (see `common.py`) that adds its axes to
the figure and returns `draw(t)` for normalized time `t` in [0, 1]. Then import
the module in `make_movies.py`. The frame is 8 × 4.5 in at 160 dpi
(1280 × 720), so text stays readable at the page's ~680 px width.
