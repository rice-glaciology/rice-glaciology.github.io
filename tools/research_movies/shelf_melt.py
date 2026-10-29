"""Submarine ice-shelf melt from repeat stereo DEMs.

A synthetic ice shelf flows away from its grounding line while ocean melt,
strongest near the grounding line and inside a basal channel, thins it. The
shelf is in steady state, so the channel stays put while surface features ride
through it. Stereo DEM strips arrive every few months (A). Following ice
parcels through successive DEMs gives the Lagrangian rate of surface-elevation
change; with hydrostatic thickness, flux divergence and surface mass balance
this gives the basal melt rate wherever two or more strips overlap (B). One
parcel's elevation record through the channel is shown in (C).
"""
import numpy as np
from scipy.ndimage import gaussian_filter

import common as c

RHO_I, RHO_W = 917.0, 1028.0
F = 1 - RHO_I / RHO_W                 # surface elevation = F * thickness
LX, LY = 50.0, 30.0                   # km
U0, K = 2.0, 0.008                     # km/yr at the grounding line, strain rate 1/yr
ACC = 0.5                             # m/yr
YEARS = 6.0
N_EPOCHS = 16
YC = 2.0                              # channel centre (km)


def velocity(x):
    return U0 + K * x                 # km/yr


def melt_rate(X, Y):
    yc = YC + 1.0 * np.sin(X / 9.0)
    return 28 * np.exp(-X / 14.0) * (0.5 + 2.2 * np.exp(-((Y - yc) / 1.6) ** 2)) + 1.0


def steady_thickness(x, y, H0=900.0):
    X, Y = np.meshgrid(x, y)
    m = melt_rate(X, Y)
    H = np.empty_like(X)
    H[:, 0] = H0
    dx = (x[1] - x[0]) * 1e3
    for i in range(1, len(x)):
        u = velocity(x[i - 1]) * 1e3
        dH = (ACC - m[:, i - 1] - H[:, i - 1] * K) / u
        H[:, i] = np.maximum(H[:, i - 1] + dx * dH, 80.0)
    return gaussian_filter(H, 1.0), m


def texture(X, Y, seed=11):
    """Surface roughness that is carried with the ice (a function of the upstream position)."""
    rng = np.random.default_rng(seed)
    n = 400
    base = gaussian_filter(rng.standard_normal((150, n)), (2.5, 4.0))
    base /= base.std()
    # Index by the Lagrangian coordinate (where the ice was at t = 0).
    xi = np.clip((X + 60) / 120 * (n - 1), 0, n - 1)
    yi = np.clip((Y + LY / 2) / LY * 149, 0, 149)
    return base[yi.astype(int), xi.astype(int)]


def upstream(X, t):
    """Where the ice now at X (km) was t years ago, for u = U0 + K x."""
    return (X + U0 / K) * np.exp(-K * t) - U0 / K


def strips(seed=5):
    """Strip footprints. Most are tasked over the fast-thinning zone near the grounding line."""
    rng = np.random.default_rng(seed)
    out = []
    for k in range(N_EPOCHS):
        t = (k + 0.5) / N_EPOCHS * YEARS
        w = rng.uniform(13, 17)
        if rng.uniform() < 0.75:
            x0 = parcel(t) - rng.uniform(2, w - 2)
        else:
            x0 = rng.uniform(-5, LX - 10)
        ang = rng.uniform(-0.25, 0.25)
        out.append((t, x0, w, ang))
    return out


def parcel(t, x0=2.0):
    """Along-flow position (km) of the parcel launched at x0 in the channel."""
    return (x0 + U0 / K) * np.exp(K * t) - U0 / K


def channel_y(x):
    return YC + 1.0 * np.sin(x / 9.0)


def in_strip(X, Y, s):
    _, x0, w, ang = s
    xr = (X - x0) - Y * np.tan(ang)
    return (xr >= 0) & (xr <= w)


@c.movie("submarine-melt", 4, seconds=13.0)
def build(fig):
    x = np.linspace(0, LX, 250)
    y = np.linspace(-LY / 2, LY / 2, 150)
    X, Y = np.meshgrid(x, y)
    H, m = steady_thickness(x, y)
    s0 = F * H
    S = strips()
    rng = np.random.default_rng(2)
    melt_obs = gaussian_filter(m + rng.normal(0, 3, m.shape), 1.5)
    from scipy.interpolate import RegularGridInterpolator
    s_at = RegularGridInterpolator((y, x), s0)
    H_at = RegularGridInterpolator((y, x), H)

    def surface_at(t):
        return s0 + 0.6 * texture(upstream(X, t), Y)

    smap = c.plt.get_cmap("Blues_r")
    snorm = c.matplotlib.colors.Normalize(30, 100)
    mmap, mnorm = c.banded("inferno_r", 0, 80)
    ls = c.matplotlib.colors.LightSource(azdeg=315, altdeg=35)

    axA = fig.add_axes([0.065, 0.53, 0.36, 0.36])
    axB = fig.add_axes([0.065, 0.11, 0.36, 0.36])
    axC = fig.add_axes([0.62, 0.11, 0.355, 0.78])
    c.colorbar(fig, fig.add_axes([0.435, 0.53, 0.011, 0.36]), smap, snorm, "surface (m)",
               ticks=[30, 50, 70, 90])
    c.colorbar(fig, fig.add_axes([0.435, 0.11, 0.011, 0.36]), mmap, mnorm,
               "melt (m yr$^{-1}$)", ticks=[0, 20, 40, 60, 80])

    # The parcel's record: surface elevation at each epoch whose strip covers it.
    rec_t, rec_s = [], []
    for s in S:
        px = parcel(s[0])
        yc = channel_y(px)
        if in_strip(np.array(px), np.array(yc), s):
            rec_t.append(s[0])
            rec_s.append(s_at([[yc, px]])[0] + 0.6 * texture(np.array(upstream(px, s[0])), np.array(yc))
                         + rng.normal(0, 0.5))
    rec_t, rec_s = np.array(rec_t), np.array(rec_s)
    tt = np.linspace(0, YEARS, 200)
    px_t = parcel(tt)
    true_s = s_at(np.column_stack([channel_y(px_t), px_t]))

    def draw(t):
        yr = t * YEARS
        for ax in (axA, axB, axC):
            ax.clear()
        surf = surface_at(yr)
        rgb = ls.shade(surf, cmap=smap, norm=snorm, blend_mode="soft", vert_exag=30)
        axA.imshow(rgb, extent=[0, LX, -LY / 2, LY / 2], origin="lower", aspect="auto")
        cov = np.zeros_like(X, dtype=int)
        done = [s for s in S if s[0] <= yr]
        for s in done:
            cov += in_strip(X, Y, s)
        if done:                                # the latest strip, outlined
            last = done[-1]
            fresh = 1 - c.smooth(yr - last[0], 0, 0.35)
            for edge in (0, last[2]):
                yy = np.array([-LY / 2, LY / 2])
                axA.plot(last[1] + edge + yy * np.tan(last[3]), yy, color=c.fs.RED,
                         lw=1.0 + 1.5 * fresh, alpha=0.5 + 0.5 * fresh)
        p = parcel(yr)
        axA.plot(p, channel_y(p), "o", color=c.fs.RED, mec=c.INK, ms=6, zorder=10)
        axA.axvline(0, color=c.INK, lw=2)
        axA.set_xlim(-1, LX)
        axA.set_ylim(-LY / 2, LY / 2)
        axA.set_xticklabels([])
        axA.set_ylabel("y (km)")
        axA.text(1.0, LY / 2 - 2, "grounding\nline", fontsize=c.FS_SMALL - 1, va="top", color=c.INK)
        c.letter(axA, "A", 0.95, 0.87)
        c.title(axA, f"stereo DEM strips: {len(done)} of {N_EPOCHS}", y=1.02)

        axB.imshow(np.where(cov >= 2, melt_obs, np.nan), extent=[0, LX, -LY / 2, LY / 2],
                   origin="lower", aspect="auto", cmap=mmap, norm=mnorm, interpolation="nearest")
        axB.set_facecolor("0.9")
        axB.axvline(0, color=c.INK, lw=2)
        axB.set_xlim(-1, LX)
        axB.set_ylim(-LY / 2, LY / 2)
        axB.set_xlabel("x, along flow (km)")
        axB.set_ylabel("y (km)")
        c.letter(axB, "B", 0.95, 0.87)
        axB.text(0.5, 0.06, f"basal melt where ≥ 2 strips overlap ({100 * np.mean(cov >= 2):.0f} % of shelf)",
                 transform=axB.transAxes, ha="center", fontsize=c.FS_SMALL - 1,
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8))

        axC.plot(tt, true_s, color=c.MUTED, lw=1.0, ls="--", label="true surface")
        sel = rec_t <= yr
        axC.plot(rec_t[sel], rec_s[sel], "o", color=c.fs.RED, mec=c.INK, mew=0.6, label="DEM epochs")
        if sel.sum() >= 2:
            pf = np.polyfit(rec_t[sel], rec_s[sel], 1)
            axC.plot(tt[tt <= yr], np.polyval(pf, tt[tt <= yr]), color=c.fs.RED, lw=1.4)
            dhdt = pf[0]
            pxx = parcel(rec_t[sel].mean())
            mest = ACC - dhdt / F - H_at([[channel_y(pxx), pxx]])[0] * K
            axC.text(0.95, 0.80,
                     f"$Dh/Dt$ = {c.fs.num(dhdt, '.1f')} m yr$^{{-1}}$\nmelt ≈ {mest:.0f} m yr$^{{-1}}$",
                     transform=axC.transAxes, ha="right", va="top", fontsize=c.FS,
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=c.fs.RED, lw=0.8))
        lo, hi = true_s.min(), true_s.max()
        axC.set_xlim(0, YEARS)
        axC.set_ylim(lo - 0.15 * (hi - lo) - 1, hi + 0.25 * (hi - lo) + 1)
        axC.set_xlabel("year")
        axC.set_ylabel("parcel surface elevation (m)")
        axC.legend(loc="lower left", fontsize=c.FS_SMALL)
        c.grid(axC)
        c.letter(axC, "C", 0.06, 0.96)
        c.title(axC, "one parcel, followed down the channel", y=1.01)
        c.readout(axC, 0.78, 0.55, f"year {yr:3.1f}")

    return draw
