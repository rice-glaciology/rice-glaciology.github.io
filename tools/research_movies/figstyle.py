r"""Figure style for every figure, animation and lab plot in the book.

Usage (a script or notebook anywhere in the repository):

    import sys; sys.path.insert(0, "../..")   # path to the repository root
    import figstyle as fs
    fs.apply_rc()

The framework of Morrow, Ghelichkhan & Kramer (2026), as written in their
figure code (github.com/sghelichkhani/morrow2026 @ 832e49f):

``parallel_scaling/plot_paper_figures.py``, ``reported.py``
    Times serif with STIX math at 15 pt text, 17 pt titles and axis labels,
    13 pt ticks, 15 pt legend; series in a fixed colour + marker (red
    #d62728, blue #3182bd, black, green #2ca02c, purple #9467bd), line width
    1.9 / marker size 8.5; ``grid(which="both", alpha=0.3)``; upper-case panel
    letters in light-grey circles at the top left; titles in light-yellow
    rounded boxes; one framed legend across the top of the figure.
``verification/tracy/plot_solution.py``
    field panels attached with no ticks; ``N_LEVELS`` = 10 discrete colour
    bands in panels and colour bars alike, bar labels 17 pt and rotated;
    boxed, rotated row labels; times in light-blue rounded boxes on a strip.
``parallel_scaling/figstyle.py``
    figures written without creation timestamps.

Their figures are drawn 9.6 to 12 in wide, and so are ours: the type sizes
above are meant for that width (``WIDTH``), and the book scales the images to
the page. ``s(x)`` converts a print-size line width (in points, for a 17.8 cm
figure) to this native size.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap, ListedColormap
from matplotlib.ticker import MaxNLocator

# -- series (reported.py) --------------------------------------------------------
RED, BLUE, BLACK, GREEN, PURPLE = "#d62728", "#3182bd", "#000000", "#2ca02c", "#9467bd"
ORANGE = "#ff7f0e"
GREY = "gray"
LW, MS = 1.9, 8.5

# -- type (plot_paper_figures.py) and boxes ------------------------------------------
FS, FS_TITLE, FS_LABEL, FS_TICK, FS_LEGEND = 15, 17, 17, 13, 15
FS_CBAR_TICK = 12
N_LEVELS = 10
DPI = 200
LETTER_BOX = dict(boxstyle="circle,pad=0.3", facecolor="lightgrey", edgecolor="black")
TITLE_BOX = dict(boxstyle="round,pad=0.4", facecolor="lightyellow", edgecolor="black")
TIME_BOX = dict(boxstyle="round,pad=0.4", facecolor="lightblue", edgecolor="black")
MINUS = "\N{MINUS SIGN}"

WIDTH = 9.6                        # in, a full-width figure (fig_murr_weak)
SERIES = (RED, BLUE, BLACK, GREEN, PURPLE)
MARKERS = ("o", "s", "D", "^", "v")

# Print-size line widths (17.8 cm figure) scale to these native sizes by this factor.
FULL = 17.8 / 2.54
NATIVE = 12.8 / FULL


def s(x):
    """A print-size length in points, at the native size of these figures."""
    return x * NATIVE


def apply_rc():
    """Morrow et al. rcParams (plot_paper_figures.py), on a white page."""
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Times", "STIXGeneral", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": FS, "axes.titlesize": FS_TITLE, "axes.labelsize": FS_LABEL,
        "legend.fontsize": FS_LEGEND, "xtick.labelsize": FS_TICK, "ytick.labelsize": FS_TICK,
        "lines.linewidth": LW, "lines.markersize": MS, "axes.unicode_minus": True,
        "axes.prop_cycle": cycler(color=SERIES),
        "figure.figsize": (WIDTH, 0.62 * WIDTH),
        "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
        "text.color": BLACK, "axes.edgecolor": BLACK,
        "figure.dpi": 100, "savefig.dpi": DPI, "pdf.fonttype": 42, "ps.fonttype": 42,
    })


def grid(ax):
    ax.grid(True, which="both", alpha=0.3, zorder=0)
    ax.set_axisbelow(True)


def panel_letter(ax, letter, x=0.04, y=0.94):
    """Upper-case panel letter in a light-grey circle at the top left (plot_paper_figures.panel_letter)."""
    ax.text(x, y, letter, transform=ax.transAxes, ha="center", va="center",
            fontsize=FS, zorder=20, bbox=LETTER_BOX)


def title_box(ax, text, pad=12):
    """Panel title in a light-yellow rounded box (fig_murr_weak)."""
    ax.set_title(text, fontsize=FS_TITLE, bbox=TITLE_BOX, pad=pad)


def time_box(ax, x, y, text, transform=None):
    """A time or progress readout in a light-blue rounded box (tracy/plot_solution.py)."""
    ax.text(x, y, text, transform=transform or ax.transAxes, ha="center", va="center",
            fontsize=FS, zorder=20, bbox=TIME_BOX)


def num(x, spec="g"):
    """A number for figure text with a true minus sign."""
    return format(x, spec).replace("-", MINUS)


# -- c-axis orientation colours -----------------------------------------------
# Orientation is axial (0 and 180 degrees are the same), so the map is cyclic.
# It runs through the series colours, lightened so basal-plane traces drawn on
# top stay legible, in N_LEVELS discrete bands.
_CYCLE = [RED, ORANGE, "#e5c100", GREEN, BLUE, PURPLE, RED]
_ORIENT_SMOOTH = LinearSegmentedColormap.from_list("orient", _CYCLE)
_LIGHTEN = 0.45


def _lighten(rgb, f=_LIGHTEN):
    rgb = np.asarray(rgb, float)
    out = rgb.copy()
    out[..., :3] = (1 - f) * rgb[..., :3] + f
    return out


ORIENT_BANDS = _lighten(np.array([_ORIENT_SMOOTH((i + 0.5) / N_LEVELS) for i in range(N_LEVELS)]))
ORIENT_CMAP = ListedColormap(ORIENT_BANDS, name="orient_bands")


def orient_color(theta, alpha=1.0):
    """Band colour for a c-axis at angle ``theta`` (radians, axial)."""
    u = (np.asarray(theta, float) % np.pi) / np.pi
    k = np.minimum((u * N_LEVELS).astype(int), N_LEVELS - 1)
    c = ORIENT_BANDS[k].copy()
    c[..., 3] = alpha
    return c


def orient_colorbar(fig, cax, label="c-axis angle (°)"):
    """Discrete-band colour bar for c-axis orientation, 0 to 180 degrees."""
    norm = BoundaryNorm(np.linspace(0, 180, N_LEVELS + 1), N_LEVELS)
    sm = plt.cm.ScalarMappable(norm=norm, cmap=ORIENT_CMAP)
    cb = fig.colorbar(sm, cax=cax)
    cb.set_label(label, rotation=90, fontsize=FS_LABEL, labelpad=10)
    cb.ax.tick_params(labelsize=FS_CBAR_TICK)
    cb.set_ticks([0, 45, 90, 135, 180])
    return cb


def nice_ticks(ax, axis="both", n=5):
    loc = lambda: MaxNLocator(n, steps=[1, 2, 2.5, 5, 10])  # noqa: E731
    if axis in ("x", "both"):
        ax.xaxis.set_major_locator(loc())
    if axis in ("y", "both"):
        ax.yaxis.set_major_locator(loc())


# -- output ----------------------------------------------------------------------
_PDF_METADATA = {"CreationDate": None, "Producer": None, "Creator": None}
_PNG_METADATA = {"Software": ""}


def save(fig, path, pad_inches=0.2, formats=("png",)):
    """Write the figure with no embedded timestamp (parallel_scaling/figstyle.py),
    as PNG at ``DPI`` and any other ``formats`` (e.g. "pdf") beside it."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = {"png": _PNG_METADATA, "pdf": _PDF_METADATA}
    for ext in formats:
        fig.savefig(str(path.with_suffix(f".{ext}")), bbox_inches="tight",
                    pad_inches=pad_inches, metadata=dict(meta.get(ext, {})))
    plt.close(fig)
    print(f"Saved {path.with_suffix('')}.{{{','.join(formats)}}}", flush=True)
