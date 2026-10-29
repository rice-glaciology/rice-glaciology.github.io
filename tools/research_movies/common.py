"""Shared frame and MP4 writer for the research-page movies.

Each movie is a 1280 x 720 frame (8 x 4.5 in at 160 dpi) in the group's figure
style (``figstyle.py``, copied from the glaciology book). The frame is smaller
in inches than the book's videos so that the text stays readable when the
website shows the movie at about 680 px wide.

A movie module registers a builder with ``@movie("slug", order)``. The builder
takes the figure, adds its axes, and returns ``draw(t)``, which redraws every
panel for normalized time t in [0, 1].
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.animation import FFMpegWriter  # noqa: E402
from matplotlib.colors import BoundaryNorm  # noqa: E402

import figstyle as fs  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT_DIR = os.path.join(REPO, "static", "media", "research")

FRAME_W, FRAME_H, FRAME_DPI = 8.0, 4.5, 160
fs.apply_rc()
plt.rcParams.update({
    "font.size": 11, "axes.labelsize": 11, "axes.titlesize": 12,
    "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "legend.fontsize": 10,
    "lines.linewidth": 1.6,
})
FS, FS_SMALL = 11, 9.5

INK = fs.BLACK
MUTED = "0.4"
ICE = "#eef3f7"
OCEAN = "#9ecae1"
BED = "#c9b79c"
LETTER_BOX = dict(boxstyle="circle,pad=0.25", facecolor="lightgrey", edgecolor="black", lw=0.8)
TIME_BOX = dict(boxstyle="round,pad=0.3", facecolor="lightblue", edgecolor="black", lw=0.8)
TITLE_BOX = dict(boxstyle="round,pad=0.3", facecolor="lightyellow", edgecolor="black", lw=0.8)


def smooth(t, a=0.0, b=1.0):
    """Smoothstep from 0 (t <= a) to 1 (t >= b)."""
    if b <= a:
        return float(t >= a)
    x = np.clip((t - a) / (b - a), 0.0, 1.0)
    return float(x * x * (3 - 2 * x))


def banded(cmap, vmin, vmax, n=fs.N_LEVELS):
    """A colormap and norm split into n discrete bands, as in the book's field panels."""
    cm = plt.get_cmap(cmap, n)
    return cm, BoundaryNorm(np.linspace(vmin, vmax, n + 1), n)


def letter(ax, s, x=0.035, y=0.92):
    ax.text(x, y, s, transform=ax.transAxes, ha="center", va="center",
            fontsize=FS, zorder=30, bbox=LETTER_BOX)


def title(ax, s, x=0.5, y=1.0, **kw):
    ax.text(x, y, s, transform=ax.transAxes, ha="center", va="bottom",
            fontsize=FS, zorder=30, bbox=TITLE_BOX, **kw)


def readout(ax, x, y, s, transform=None):
    ax.text(x, y, s, transform=transform or ax.transAxes, ha="center", va="center",
            fontsize=FS, zorder=30, bbox=TIME_BOX)


def grid(ax):
    ax.grid(True, which="both", alpha=0.3, zorder=0)
    ax.set_axisbelow(True)


def colorbar(fig, cax, cmap, norm, label, ticks=None, orientation="vertical"):
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    cb = fig.colorbar(sm, cax=cax, orientation=orientation)
    cb.set_label(label, fontsize=FS_SMALL)
    cb.ax.tick_params(labelsize=FS_SMALL - 1)
    if ticks is not None:
        cb.set_ticks(ticks)
    cb.outline.set_linewidth(0.8)
    return cb


# -- registry -------------------------------------------------------------------
MOVIES = {}


def movie(slug, order, seconds=12.0, fps=24, hold=0.05, poster_at=0.85):
    """Register a movie builder. ``hold`` freezes that fraction of the clip at each end."""
    def deco(fn):
        MOVIES[slug] = dict(order=order, build=fn, seconds=seconds, fps=fps,
                            hold=hold, poster_at=poster_at)
        return fn
    return deco


def render(slug, out_dir=OUT_DIR, preview_at=None):
    spec = MOVIES[slug]
    os.makedirs(out_dir, exist_ok=True)
    fig = plt.figure(figsize=(FRAME_W, FRAME_H), dpi=FRAME_DPI)
    draw = spec["build"](fig)

    if preview_at is not None:
        draw(preview_at)
        path = os.path.join(out_dir, f"{slug}-preview.png")
        fig.savefig(path, dpi=FRAME_DPI)
        plt.close(fig)
        return path

    n = int(round(spec["seconds"] * spec["fps"]))
    hold = spec["hold"]
    writer = FFMpegWriter(fps=spec["fps"], codec="libx264", bitrate=-1,
                          extra_args=["-pix_fmt", "yuv420p", "-crf", "28", "-preset", "slow",
                                      "-movflags", "+faststart", "-an"],
                          metadata={"title": slug})
    path = os.path.join(out_dir, f"{slug}.mp4")
    with writer.saving(fig, path, dpi=FRAME_DPI):
        for i in range(n):
            u = i / (n - 1)
            t = float(np.clip((u - hold) / (1 - 2 * hold), 0, 1))
            draw(t)
            writer.grab_frame()
    # Poster frame shown before the video loads (and when motion is reduced).
    draw(spec["poster_at"])
    fig.savefig(os.path.join(out_dir, f"{slug}.jpg"), dpi=FRAME_DPI * 0.6,
                pil_kwargs={"quality": 82, "optimize": True})
    plt.close(fig)
    return path
