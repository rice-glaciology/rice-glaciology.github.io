"""Multi-element radar: swath imaging of the bed and repeat-pass vertical velocity.

A sled-towed multi-element radar crosses a synthetic subglacial landscape.
Because the array can tell where off-nadir echoes come from, each position
maps a swath of bed rather than the single nadir point a one-element radar
gives (A). The echogram along the track shows internal layers draped over the
bed (B). Coregistering this pass with a repeat pass and differencing the phase
of each layer gives the vertical velocity through the ice column under the
sled (C), compared with a Lliboutry-shape profile that includes flow over the
bed topography.
"""
import numpy as np
from scipy.ndimage import gaussian_filter, gaussian_filter1d

import common as c

LX, LY = 30.0, 12.0           # km
SWATH = 2.6                   # km half-width imaged by the array
SURF = 1000.0                 # m, flat ice surface elevation
U_B = 15.0                    # m/yr basal sliding along x
ACC = 0.15                    # m/yr ice-equivalent accumulation


def landscape(nx=300, ny=120, seed=7):
    rng = np.random.default_rng(seed)
    x = np.linspace(0, LX, nx)
    y = np.linspace(-LY / 2, LY / 2, ny)
    X, Y = np.meshgrid(x, y)
    rough = gaussian_filter(rng.standard_normal((ny, nx)), 6) * 900
    trough = -450 * np.exp(-((Y - 1.2 * np.sin(X / 5.0)) / 2.0) ** 2)
    hill = 380 * np.exp(-(((X - 19) / 3.0) ** 2 + ((Y + 3.5) / 2.2) ** 2))
    b = -700 + 8 * X + trough + hill + rough
    return x, y, b


def track(xs):
    return 1.6 * np.sin(2 * np.pi * xs / LX + 0.4)


def lliboutry(zeta, p=3.0):
    """Shape of vertical velocity with height above the bed (0 at bed, 1 at surface)."""
    s = 1 - zeta
    return 1 - (p + 2) / (p + 1) * s + s ** (p + 2) / (p + 1)


@c.movie("multi-element-radar", 2, seconds=13.0)
def build(fig):
    x, y, b = landscape()
    nx = len(x)
    from scipy.interpolate import RegularGridInterpolator
    interp = RegularGridInterpolator((y, x), b)
    ty = track(x)
    bed_t = gaussian_filter1d(interp(np.column_stack([ty, x])), 1.5)
    thick = SURF - bed_t                                 # m
    dbdx = np.gradient(gaussian_filter1d(bed_t, 8), x * 1e3)

    # Swath mask: distance from each map point to the track.
    X, Y = np.meshgrid(x, y)
    dist = np.abs(Y - np.interp(X, x, ty))

    # Synthetic echogram along the track.
    rng = np.random.default_rng(3)
    nz = 260
    depth = np.linspace(0, 2400, nz)
    img = np.zeros((nz, nx))
    zeta_layers = np.sort(rng.uniform(0.18, 0.95, 14))
    amps = rng.uniform(0.35, 1.0, len(zeta_layers))
    for zl, a in zip(zeta_layers, amps):
        # Layers drape over the bed, more so near it.
        smooth_bed = gaussian_filter1d(bed_t, 4 + 18 * zl)
        dl = (SURF - smooth_bed) * (1 - zl)
        img += a * np.exp(-((depth[:, None] - dl[None, :]) / 9.0) ** 2)
    img += 4.0 * np.exp(-((depth[:, None] - thick[None, :]) / 14.0) ** 2)
    img *= np.exp(-depth / 1400.0)[:, None]
    img += 0.06 * np.abs(rng.standard_normal(img.shape))
    img[depth[:, None] > thick[None, :] + 25] *= 0.25
    img = 10 * np.log10(img + 1e-3)

    bmap, bnorm = c.banded("terrain", -1200, 0)

    axA = fig.add_axes([0.085, 0.53, 0.38, 0.36])
    axB = fig.add_axes([0.085, 0.12, 0.38, 0.32])
    axC = fig.add_axes([0.66, 0.12, 0.31, 0.77])
    cax = fig.add_axes([0.48, 0.53, 0.011, 0.36])
    c.colorbar(fig, cax, bmap, bnorm, "bed (m)", ticks=[-1200, -600, 0])

    wb_all = U_B * dbdx
    span = max(np.abs(wb_all).max(), ACC) * 1.15
    wlim = (min(-span, -ACC * 1.3), max(span, 0.05))

    def draw(t):
        for ax in (axA, axB, axC):
            ax.clear()
        k = max(1, int(round(t * (nx - 1))))
        xs = x[k]

        # A: bed map, revealed in a swath behind the sled
        seen = (dist <= SWATH) & (X <= xs)
        axA.imshow(np.where(seen, b, np.nan), extent=[0, LX, -LY / 2, LY / 2], origin="lower",
                   cmap=bmap, norm=bnorm, aspect="auto", interpolation="bilinear")
        axA.imshow(np.where(~seen, 1.0, np.nan), extent=[0, LX, -LY / 2, LY / 2], origin="lower",
                   cmap="Greys", vmin=0, vmax=8, aspect="auto")
        axA.plot(x[:k + 1], ty[:k + 1], color=c.INK, lw=1.0, ls="--")
        axA.plot(x, ty + SWATH, color=c.MUTED, lw=0.5, ls=":")
        axA.plot(x, ty - SWATH, color=c.MUTED, lw=0.5, ls=":")
        axA.plot(xs, ty[k], "s", color=c.fs.RED, mec=c.INK, ms=7, zorder=10)
        axA.set_xlim(0, LX)
        axA.set_ylim(-LY / 2, LY / 2)
        axA.set_xticklabels([])
        axA.set_ylabel("across (km)")
        c.letter(axA, "A", 0.04, 0.86)
        c.title(axA, "bed imaged in a swath, not a line", y=1.02)
        axA.text(0.98, 0.07, "dashed: nadir track", transform=axA.transAxes, ha="right",
                 fontsize=c.FS_SMALL - 1, color=c.INK)

        # B: echogram
        axB.imshow(np.where(np.arange(nx)[None, :] <= k, img, np.nan),
                   extent=[0, LX, depth[-1], 0], cmap="Greys_r", vmin=-14, vmax=4, aspect="auto",
                   interpolation="bilinear")
        axB.set_facecolor("0.92")
        axB.axvline(xs, color=c.fs.RED, lw=1.0)
        axB.set_xlim(0, LX)
        axB.set_ylim(depth[-1], 0)
        axB.set_xlabel("along track (km)")
        axB.set_ylabel("depth (m)")
        c.letter(axB, "B", 0.04, 0.86)

        # C: vertical velocity from two coregistered passes
        H = thick[k]
        zeta = np.linspace(0, 1, 100)
        wb = U_B * dbdx[k]                                      # flow over the bed
        w = wb + (-ACC - wb) * lliboutry(zeta)
        zl = zeta_layers
        wl = wb + (-ACC - wb) * lliboutry(zl)
        noise = np.random.default_rng(k).normal(0, 0.04 * span, len(zl))
        z_m = H * (1 - zeta)
        axC.plot(w, z_m, color=c.fs.BLUE, label="model")
        axC.errorbar(wl + noise, H * (1 - zl), xerr=0.06 * span, fmt="o", ms=4.5, color=c.fs.RED,
                     mec=c.INK, mew=0.6, elinewidth=0.8, capsize=0, label="repeat-pass radar")
        axC.axvline(0, color=c.MUTED, lw=0.7)
        axC.axhline(H, color=c.INK, lw=1.2)
        axC.fill_between([-5, 5], H, 2400, color=c.BED, lw=0)
        axC.set_xlim(*wlim)
        axC.set_ylim(2400, 0)
        axC.set_xlabel("vertical velocity (m yr$^{-1}$)")
        axC.set_ylabel("depth (m)")
        axC.legend(loc="upper right", fontsize=c.FS_SMALL, frameon=True, bbox_to_anchor=(1.0, 0.93))
        c.grid(axC)
        c.letter(axC, "C", 0.07, 0.96)
        c.title(axC, "englacial deformation under the sled", y=1.01)
        c.readout(axC, 0.5, 0.06, f"{xs:4.1f} km along track")

    return draw
