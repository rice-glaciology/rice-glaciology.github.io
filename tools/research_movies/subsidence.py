"""Sea-level geophysics: land subsidence on a (synthetic) Gulf Coast.

From 2016 to 2026 the vertical-land-motion map builds up as InSAR and GNSS
see two subsidence bowls over groundwater pumping centres (A). A delayed
poromechanical model, compaction relaxing toward the skeletal storage times
the head decline with a clay drainage time, is fit to the GNSS record at one
station, and posterior samples of its two parameters project subsidence to
2050 for two scenarios: pumping continues, or pumping is cut and aquifers
recharge (B). At a GNSS interferometric-reflectometry tide gauge on the coast,
relative sea level is global-mean rise plus local subsidence (C).

The geography is invented; it is not a map of any real place.
"""
import numpy as np

import common as c

Y0, Y_OBS, Y1 = 2016.0, 2026.0, 2050.0
LX, LY = 60.0, 40.0
CENTRES = [(22.0, 24.0, 7.0, 1.0), (40.0, 14.0, 5.0, 0.6)]    # x, y, radius (km), weight
STATIONS = [(22.5, 23.0), (33.0, 30.0), (12.0, 12.0), (44.0, 22.0), (40.5, 12.5)]
GAUGE = (47.0, 8.0)
N_SAMPLES = 60


def coast_y(x):
    """Shoreline: land above, Gulf below; a bay cuts in at the right."""
    return 6.0 + 2.0 * np.sin(x / 7.0) + 10.0 * np.exp(-((x - 52.0) / 5.0) ** 2)


def year_of(t):
    """The first 55 % of the clip covers the observations, the rest the projection."""
    if t <= 0.55:
        return Y0 + (Y_OBS - Y0) * t / 0.55
    return Y_OBS + (Y1 - Y_OBS) * (t - 0.55) / 0.45


RATE = 1.8                    # m/yr of head decline while pumping
T_PUMP = 1990.0               # pumping began


def head(yr, scenario):
    """Hydraulic-head decline (m) at the pumping centre."""
    obs = RATE * (np.minimum(yr, Y_OBS) - T_PUMP)
    after = np.maximum(yr - Y_OBS, 0)
    if scenario == "continue":
        return obs + RATE * after
    return obs - 20 * (1 - np.exp(-after / 6.0))          # pumping cut, aquifer recharges


def compaction(years, Sk, tau, scenario, ske_frac=0.08):
    """Subsidence (m, positive down) since the first year.

    Inelastic clay compaction relaxes toward Sk * head with drainage time tau and
    never reverses; a small elastic part follows the head both ways.
    """
    h0 = head(years[0], scenario)
    s_in = Sk * (h0 - RATE * tau)          # lagging steady state for steady pumping
    S = np.empty_like(years)
    for i, yr in enumerate(years):
        if i:
            dt = years[i] - years[i - 1]
            s_in += dt * max(Sk * head(yr, scenario) - s_in, 0.0) / tau
        S[i] = s_in + ske_frac * Sk * head(yr, scenario)
    return S - S[0]


def simulate():
    rng = np.random.default_rng(4)
    yrs = np.arange(Y0, Y1 + 1e-9, 1 / 12)
    Sk_true, tau_true = 0.012, 6.0
    truth = compaction(yrs, Sk_true, tau_true, "continue")
    obs = yrs <= Y_OBS
    gnss_t = yrs[obs]
    gnss = truth[obs] + rng.normal(0, 0.004, obs.sum()) + 0.003 * np.sin(2 * np.pi * gnss_t)
    # Posterior samples (a stand-in for the Bayesian fit): parameters scattered
    # around the truth, kept if they fit the GNSS record.
    samples = {"continue": [], "recharge": []}
    while len(samples["continue"]) < N_SAMPLES:
        Sk = Sk_true * np.exp(rng.normal(0, 0.25))
        tau = tau_true * np.exp(rng.normal(0, 0.35))
        cont = compaction(yrs, Sk, tau, "continue")
        if np.sqrt(np.mean((cont[obs] - gnss) ** 2)) < 0.012:
            samples["continue"].append(cont)
            samples["recharge"].append(compaction(yrs, Sk, tau, "recharge"))
    return yrs, truth, gnss_t, gnss, {k: np.array(v) for k, v in samples.items()}


def gmsl(yr):
    """Global-mean sea-level rise since 2016 (m), an intermediate-scenario-like curve."""
    d = yr - Y0
    return 0.0042 * d + 0.00006 * d ** 2


@c.movie("sea-level-geophysics", 5, seconds=14.0)
def build(fig):
    yrs, truth, gnss_t, gnss, samples = simulate()
    x = np.linspace(0, LX, 240)
    y = np.linspace(0, LY, 160)
    X, Y = np.meshgrid(x, y)
    shape = sum(w * np.exp(-((X - xc) ** 2 + (Y - yc) ** 2) / (2 * r ** 2)) for xc, yc, r, w in CENTRES)
    shape += 0.06 * np.exp(-((X - 30) ** 2 + (Y - 10) ** 2) / 600)     # regional background
    sea = Y < coast_y(X)
    rng = np.random.default_rng(9)
    from scipy.ndimage import gaussian_filter
    atmos = gaussian_filter(rng.standard_normal(X.shape), 8) * 0.6

    def shape_at(px, py):
        return sum(w * np.exp(-((px - xc) ** 2 + (py - yc) ** 2) / (2 * r ** 2))
                   for xc, yc, r, w in CENTRES) + 0.06 * np.exp(-((px - 30) ** 2 + (py - 10) ** 2) / 600)

    st_scale = shape_at(*STATIONS[0])
    g_scale = shape_at(*GAUGE) / st_scale
    med = {k: np.median(v, axis=0) for k, v in samples.items()}

    cmap, norm = c.banded("magma_r", 0, 100)               # cm of subsidence
    cmap = cmap.copy()
    cmap.set_under(cmap(0.0))
    axA = fig.add_axes([0.065, 0.20, 0.39, 0.62])
    axB = fig.add_axes([0.60, 0.565, 0.375, 0.325])
    axC = fig.add_axes([0.60, 0.12, 0.375, 0.325])
    c.colorbar(fig, fig.add_axes([0.465, 0.278, 0.011, 0.465]), cmap, norm,
               "subsidence since 2016 (cm)", ticks=[0, 20, 40, 60, 80, 100])
    cols = {"continue": c.fs.RED, "recharge": c.fs.BLUE}
    names = {"continue": "pumping continues", "recharge": "pumping cut"}

    def draw(t):
        yr = year_of(t)
        i = int(np.searchsorted(yrs, yr - 1e-9))
        i = min(i, len(yrs) - 1)
        for ax in (axA, axB, axC):
            ax.clear()

        # A: map of cumulative subsidence (median of the continue scenario after 2026)
        S_st = truth[i] if yr <= Y_OBS else med["continue"][i]
        field = 100 * S_st * shape / st_scale
        if yr <= Y_OBS:
            field = field + 1.5 * atmos * min(1.0, (yr - Y0) / 2)   # InSAR noise in the observations
        field = np.where(sea, np.nan, field)
        axA.set_facecolor(c.OCEAN)
        axA.imshow(field, extent=[0, LX, 0, LY], origin="lower", cmap=cmap, norm=norm,
                   aspect="equal", interpolation="bilinear")
        axA.plot(x, coast_y(x), color=c.INK, lw=1.0)
        sx, sy = zip(*STATIONS)
        axA.plot(sx, sy, "^", color="white", mec=c.INK, ms=7, mew=0.9, ls="none")
        axA.plot(*STATIONS[0], "^", color=c.fs.GREEN, mec=c.INK, ms=9, mew=0.9)
        axA.plot(*GAUGE, "*", color="gold", mec=c.INK, ms=13, mew=0.8)
        axA.text(GAUGE[0] + 1.5, GAUGE[1] - 0.3, "GNSS-IR\ntide gauge", fontsize=c.FS_SMALL - 1,
                 va="top", color=c.INK)
        axA.text(4, 2.5, "Gulf", fontsize=c.FS_SMALL, color="0.25", style="italic")
        axA.set_xlim(0, LX)
        axA.set_ylim(0, LY)
        axA.set_xlabel("km")
        axA.set_ylabel("km")
        c.letter(axA, "A", 0.05, 0.95)
        c.title(axA, "InSAR + GNSS (observed)" if yr <= Y_OBS else "poromechanical projection",
                y=1.015)
        c.readout(axA, 0.82, 0.93, f"{yr:.0f}")

        # B: GNSS station record and projections
        def projections(ax, scale, offset=None):
            for key in ("continue", "recharge"):
                if yr <= Y_OBS:
                    continue
                j = (yrs >= Y_OBS) & (yrs <= yr)
                v = 100 * samples[key][:, j] * scale
                if offset is not None:
                    v = v + 100 * offset[j]
                lo, hi = np.percentile(v, [5, 95], axis=0)
                ax.fill_between(yrs[j], lo, hi, color=cols[key], alpha=0.22, lw=0)
                ax.plot(yrs[j], np.median(v, axis=0), color=cols[key], lw=1.5, label=names[key])

        sel = gnss_t <= yr
        axB.plot(gnss_t[sel], 100 * gnss[sel], ".", color=c.fs.GREEN, ms=3.5, label="GNSS")
        jj = yrs <= min(yr, Y_OBS)
        axB.plot(yrs[jj], 100 * truth[jj], color=c.INK, lw=1.0, label="InSAR")
        projections(axB, 1.0)
        axB.axvline(Y_OBS, color=c.MUTED, lw=0.7, ls=":")
        axB.set_xlim(Y0, Y1)
        axB.set_ylim(90, -8)
        axB.set_xticklabels([])
        axB.set_ylabel("subsidence (cm)")
        axB.legend(loc="lower left", fontsize=c.FS_SMALL - 1, ncol=2, frameon=True,
                   handlelength=1.2, columnspacing=0.8)
        c.grid(axB)
        c.letter(axB, "B", 0.05, 0.85)
        c.title(axB, "GNSS station (green) and projections", y=1.03)

        # C: relative sea level at the tide gauge
        g_obs = yrs <= min(yr, Y_OBS)
        rsl_obs = 100 * (gmsl(yrs[g_obs]) + truth[g_obs] * g_scale)
        axC.plot(yrs[g_obs][::2], rsl_obs[::2] + np.random.default_rng(1).normal(0, 1.2, len(rsl_obs[::2])),
                 "*", color="gold", mec=c.INK, mew=0.4, ms=5, ls="none", label="GNSS-IR")
        axC.plot(yrs[yrs <= yr], 100 * gmsl(yrs[yrs <= yr]), color=c.MUTED, ls="--", lw=1.1,
                 label="global mean")
        projections(axC, g_scale, offset=gmsl(yrs))
        axC.axvline(Y_OBS, color=c.MUTED, lw=0.7, ls=":")
        axC.set_xlim(Y0, Y1)
        axC.set_ylim(-3, 50)
        axC.set_xlabel("year")
        axC.set_ylabel("relative sea level (cm)")
        axC.legend(loc="upper left", fontsize=c.FS_SMALL - 1, frameon=True, handlelength=1.2)
        c.grid(axC)
        c.letter(axC, "C", 0.95, 0.15)

    return draw
