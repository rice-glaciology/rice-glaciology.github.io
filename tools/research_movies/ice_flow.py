"""Ice flow: one glacier, one ocean forcing, two sliding laws.

A marine glacier is spun up with a Weertman sliding law until its grounding
line rests seaward of a bedrock ridge, held there by the buttressing of a
confined ice shelf. The friction coefficient of a Coulomb-limited law is then
inverted so that both laws give the same basal stress, and so the same glacier,
at the start. Ocean melt thins the shelf from year 0. The two glaciers start
identical and diverge only because of what is assumed about slip at the bed.
"""
import numpy as np

import common as c
import flowline as fl

YEARS = 600.0
MELT = 60.0
X0, X1 = 100e3, 640e3
Z0, Z1 = -1250.0, 2600.0


def simulate():
    H, u = fl.spin_up(years=8000, dt=0.5)
    Cc = fl.coulomb_coefficient(H, u)
    runs = {"weertman": fl.run(H, u, "weertman", fl.C_W, YEARS, MELT),
            "coulomb": fl.run(H, u, "coulomb", Cc, YEARS, MELT)}
    n = min(len(r) for r in runs.values())
    return {k: v[:n] for k, v in runs.items()}


@c.movie("ice-flow", 1, seconds=14.0)
def build(fig):
    runs = simulate()
    n = len(runs["weertman"])
    zgrid = np.linspace(Z0, Z1, 400)
    xs = fl.XC
    vis = (xs >= X0) & (xs <= X1)
    cmap, norm = c.banded("viridis", 0, 2000)
    cmap = cmap.copy()
    cmap.set_over(cmap(0.999))
    t_all = np.array([s[0] for s in runs["weertman"]])
    xg = {k: np.array([s[3] for s in v]) / 1e3 for k, v in runs.items()}
    colors = {"weertman": c.fs.BLUE, "coulomb": c.fs.RED}
    labels = {"weertman": "Weertman sliding", "coulomb": "Coulomb-limited sliding"}

    axA = fig.add_axes([0.095, 0.56, 0.535, 0.33])
    axB = fig.add_axes([0.095, 0.13, 0.535, 0.33])
    axC = fig.add_axes([0.80, 0.13, 0.185, 0.76])
    cax = fig.add_axes([0.645, 0.13, 0.012, 0.76])
    c.colorbar(fig, cax, cmap, norm, "ice speed (m yr$^{-1}$)", ticks=[0, 500, 1000, 1500, 2000])
    bed = fl.bed(np.linspace(X0, X1, 400))

    def section(ax, snap, key, show_x):
        t, H, u, x_g, melt = snap
        s = fl.surface(H)
        base = s - H
        un = 0.5 * (u[1:] + u[:-1])
        field = np.where((zgrid[:, None] >= base[None, :]) & (zgrid[:, None] <= s[None, :]),
                         un[None, :], np.nan)
        xb = np.linspace(X0, X1, 400) / 1e3
        ax.fill_between(xb, Z0, 0, color=c.OCEAN, lw=0, zorder=0)
        ax.imshow(field[:, vis], extent=[xs[vis][0] / 1e3, xs[vis][-1] / 1e3, Z0, Z1],
                  origin="lower", aspect="auto", cmap=cmap, norm=norm, interpolation="nearest",
                  zorder=1)
        ax.plot(xs[vis] / 1e3, s[vis], color=c.INK, lw=0.9, zorder=2)
        ax.plot(xs[vis] / 1e3, base[vis], color=c.INK, lw=0.9, zorder=2)
        ax.fill_between(xb, Z0, bed, color=c.BED, lw=0, zorder=3)
        ax.plot(xb, bed, color="0.3", lw=0.8, zorder=3)
        ax.plot(x_g / 1e3, fl.bed(x_g), marker="^", color=colors[key], ms=8,
                mec=c.INK, mew=0.8, zorder=5, clip_on=False)
        ax.set_xlim(X0 / 1e3, X1 / 1e3)
        ax.set_ylim(Z0, Z1)
        ax.set_ylabel("elevation (m)")
        ax.set_yticks([-1000, 0, 1000, 2000])
        if show_x:
            ax.set_xlabel("distance from ice divide (km)")
        else:
            ax.set_xticklabels([])
        ax.text(0.985, 0.88, labels[key], transform=ax.transAxes, ha="right", va="center",
                fontsize=c.FS, color=colors[key],
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=colors[key], lw=0.8))

    def draw(t):
        k = int(round(t * (n - 1)))
        for ax in (axA, axB, axC):
            ax.clear()
        section(axA, runs["weertman"][k], "weertman", False)
        section(axB, runs["coulomb"][k], "coulomb", True)
        c.letter(axA, "A", 0.03, 0.85)
        c.letter(axB, "B", 0.03, 0.85)
        c.title(axA, "SSA flowline: ocean melt removes the shelf's buttressing", y=1.03)
        yr, melt = runs["weertman"][k][0], runs["weertman"][k][4]
        axA.text(0.985, 0.62, f"shelf melt {melt:.0f} m yr$^{{-1}}$", transform=axA.transAxes,
                 ha="right", fontsize=c.FS_SMALL, color=c.INK)

        for key in ("weertman", "coulomb"):
            axC.plot(xg[key][:k + 1], t_all[:k + 1], color=colors[key])
            axC.plot(xg[key][k], t_all[k], "^", color=colors[key], mec=c.INK, mew=0.8, ms=7)
        axC.axvspan(470, 530, color=c.BED, alpha=0.45, lw=0)
        axC.text(500, 590, "ridge", ha="center", va="bottom", fontsize=c.FS_SMALL, color="0.3")
        axC.set_xlim(120, 570)
        axC.set_xticks([200, 300, 400, 500])
        axC.set_ylim(YEARS, 0)
        axC.set_xlabel("grounding line (km)")
        axC.set_ylabel("model year")
        c.grid(axC)
        c.letter(axC, "C", 0.09, 0.96)
        c.title(axC, "retreat", y=1.01)
        c.readout(axC, 0.35, 0.2, f"year {yr:4.0f}")

    return draw
