"""Firn: a transient Herron-Langway firn column under warming and more snowfall.

A Lagrangian column of sub-annual layers is spun up to steady state for a
cold, dry site, then forced with a 4 K warming and a 20 % accumulation
increase between years 20 and 80. The movie shows the column (density and
dated isochrones moving down), the density profile against the spun-up one,
and the change in firn air content, which is the part of surface-height
change that altimetry has to correct for.
"""
import numpy as np

import common as c

RHO_I, RHO_W, RHO_S, R = 917.0, 1000.0, 350.0, 8.314
DT = 0.25                   # yr
T0, A0 = 253.15, 0.30       # K, m w.e. / yr
YEARS = 240
DEPTH = 90.0                # m shown


def forcing(year):
    f = np.clip((year - 20) / 60, 0, 1)
    f = f * f * (3 - 2 * f)
    return T0 + 4.0 * f, A0 * (1 + 0.2 * f)


def hl_rate(rho, T, A):
    """Herron & Langway (1980) densification rate (kg m-3 yr-1)."""
    k0 = 11.0 * np.exp(-10160.0 / (R * T))
    k1 = 575.0 * np.exp(-21400.0 / (R * T))
    return np.where(rho < 550.0, k0 * A, k1 * np.sqrt(A)) * (RHO_I - rho)


def step(rho, mass, birth, year, T, A):
    rho = np.minimum(rho + DT * hl_rate(rho, T, A), RHO_I - 1e-3)
    # New snow on top, then drop layers far below the shown depth.
    rho = np.concatenate([[RHO_S], rho])
    mass = np.concatenate([[A * RHO_W * DT], mass])
    birth = np.concatenate([[year], birth])
    z = np.cumsum(mass / rho)
    keep = z < 160.0
    return rho[keep], mass[keep], birth[keep]


def fac(rho, mass, depth=150.0):
    h = mass / rho
    z = np.cumsum(h)
    k = z < depth
    return float(np.sum(h[k] * (1 - rho[k] / RHO_I)))


def simulate():
    rho, mass, birth = np.array([RHO_S]), np.array([A0 * RHO_W * DT]), np.array([-1e4])
    year = -1500.0
    while year < 0:                      # spin up under steady climate
        rho, mass, birth = step(rho, mass, birth, year, T0, A0)
        year += DT
    snaps = []
    year = 0.0
    while year <= YEARS + 1e-9:
        T, A = forcing(year)
        snaps.append((year, rho.copy(), mass.copy(), birth.copy(), T, A, fac(rho, mass)))
        rho, mass, birth = step(rho, mass, birth, year, T, A)
        year += DT
    return snaps


@c.movie("firn", 3, seconds=13.0)
def build(fig):
    snaps = simulate()
    years = np.array([s[0] for s in snaps])
    facs = np.array([s[6] for s in snaps])
    dT = np.array([s[4] - T0 for s in snaps])
    dA = np.array([100 * (s[5] / A0 - 1) for s in snaps])
    rho0, m0 = snaps[0][1], snaps[0][2]
    z0 = np.cumsum(m0 / rho0) - 0.5 * m0 / rho0
    cmap, norm = c.banded("Blues", 350, 850)

    axA = fig.add_axes([0.065, 0.11, 0.11, 0.78])
    axB = fig.add_axes([0.355, 0.11, 0.225, 0.78])
    axC1 = fig.add_axes([0.685, 0.62, 0.295, 0.27])
    axC2 = fig.add_axes([0.685, 0.11, 0.295, 0.40])
    cax = fig.add_axes([0.235, 0.11, 0.012, 0.78])
    c.colorbar(fig, cax, cmap, norm, "density (kg m$^{-3}$)", ticks=[350, 450, 550, 650, 750, 850])

    def draw(t):
        k = int(round(t * (len(snaps) - 1)))
        year, rho, mass, birth, T, A, F = snaps[k]
        h = mass / rho
        ztop = np.cumsum(h) - h
        for ax in (axA, axB, axC1, axC2):
            ax.clear()

        # A: the column
        for zt, hh, r in zip(ztop, h, rho):
            if zt > DEPTH:
                break
            axA.add_patch(c.plt.Rectangle((0, zt), 1, hh, color=cmap(norm(r)), lw=0))
        # isochrones every 10 years of deposition
        for y in np.arange(np.floor(year / 10) * 10, year - 400, -10):
            j = np.searchsorted(-birth, -y)
            if 0 < j < len(ztop) and ztop[j] < DEPTH:
                heavy = (y % 50 == 0)
                axA.plot([0, 1], [ztop[j]] * 2, color=c.INK, lw=1.1 if heavy else 0.45,
                         alpha=0.9 if heavy else 0.55)
                if heavy and ztop[j] > 3:
                    axA.text(1.04, ztop[j], c.fs.num(y, '.0f'),
                             va="center", fontsize=c.FS_SMALL - 1.5, color=c.MUTED, clip_on=False)
        axA.set_xlim(0, 1)
        axA.set_ylim(DEPTH, 0)
        axA.set_xticks([])
        axA.set_ylabel("depth (m)")
        c.letter(axA, "A", 0.18, 0.96)
        c.title(axA, "firn column", y=1.015)

        # B: density profile
        zc = ztop + 0.5 * h
        axB.plot(rho0, z0, color=c.INK, ls="--", lw=1.2, label="spun-up")
        axB.fill_betweenx(z0, rho0, np.interp(z0, zc, rho), color=c.fs.RED, alpha=0.35, lw=0)
        axB.plot(rho, zc, color=c.fs.RED, label=f"year {year:.0f}")
        axB.axvline(830, color=c.MUTED, lw=0.8, ls=":")
        axB.text(826, 4, "pore\nclose-off", ha="right", va="top", fontsize=c.FS_SMALL - 1, color=c.MUTED)
        axB.set_xlim(330, 900)
        axB.set_ylim(DEPTH, 0)
        axB.set_xlabel("density (kg m$^{-3}$)")
        axB.legend(loc="lower left", frameon=True, fontsize=c.FS_SMALL)
        c.grid(axB)
        c.letter(axB, "B", 0.06, 0.96)
        c.title(axB, "Herron–Langway densification", y=1.015)

        # C: forcing and firn-air-content response
        axC1.plot(years[:k + 1], dT[:k + 1], color=c.fs.RED)
        axC1.set_ylabel("ΔT (K)", color=c.fs.RED)
        axC1.set_xlim(0, YEARS)
        axC1.set_ylim(-0.4, 5)
        axC1.set_xticklabels([])
        axC1.text(0.98, 0.12, f"accumulation +{dA[k]:.0f} %", transform=axC1.transAxes,
                  ha="right", fontsize=c.FS_SMALL, color=c.fs.BLUE)
        c.grid(axC1)
        c.letter(axC1, "C", 0.05, 0.82)
        c.title(axC1, "climate forcing and response", y=1.03)

        dF = facs - facs[0]
        axC2.plot(years[:k + 1], dF[:k + 1], color=c.fs.BLUE)
        axC2.plot(years[k], dF[k], "o", color=c.fs.BLUE, ms=5)
        axC2.set_xlim(0, YEARS)
        lo, hi = dF.min(), dF.max()
        pad = 0.1 * (hi - lo + 1e-6)
        axC2.set_ylim(lo - pad, hi + pad)
        axC2.set_xlabel("model year")
        axC2.set_ylabel("Δ firn air (m)")
        c.grid(axC2)
        c.readout(axC2, 0.78, 0.82, f"year {year:5.0f}")

    return draw
