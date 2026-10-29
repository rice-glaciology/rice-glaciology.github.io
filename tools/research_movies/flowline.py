"""A 1D shallow-shelf (SSA) flowline model of a marine glacier, used by ice_flow.py.

Thickness lives on cell centres and velocity on cell edges (nodes). The ice
divide is at x = 0 (u = 0) and the calving front is fixed at x = L. Where ice
floats, a lateral-drag term stands in for the buttressing of a confined ice
shelf, so thinning the shelf with basal melt reduces the back stress on the
grounded ice. Grounded nodes feel basal friction scaled by the sub-grid
grounded fraction.

Two sliding laws:
    weertman  tau_b = C |u|^(m-1) u
    coulomb   tau_b = min(C |u|^m, f N) u/|u|   (Tsai et al., 2015, smoothed),
              with N the effective pressure from a fully connected ocean.
The Coulomb friction coefficient is inverted from the spun-up Weertman state so
both laws start from the same glacier with the same basal stress.
"""
import numpy as np
from scipy.linalg import solve_banded

RHO_I, RHO_W, G = 917.0, 1028.0, 9.81
N_GLEN, M = 3.0, 1.0 / 3.0
L, NX = 640e3, 320
DX = L / NX
XC = (np.arange(NX) + 0.5) * DX          # cell centres
XN = np.arange(NX + 1) * DX              # nodes
A_GLEN = 1.0e-17                         # Pa^-3 yr^-1, about -10 C ice
B_GLEN = A_GLEN ** (-1 / N_GLEN)
C_W = 1.0e4                              # Pa (m/yr)^-1/3
F_COUL = 0.15
WIDTH = 50e3                             # channel width for lateral drag
ACC = 0.4                                # m/yr


def bed(x):
    """Seaward-deepening bed with a ridge at 500 km and a deeper basin inland of it."""
    return (-150.0 - 1.1e-3 * x
            + 220.0 * np.exp(-((x - 500e3) / 55e3) ** 2)
            - 120.0 * np.exp(-((x - 400e3) / 60e3) ** 2))


BC = bed(XC)
BN = bed(XN)


def surface(H, b=BC):
    return np.maximum(b + H, (1 - RHO_I / RHO_W) * H)


def floating(H, b=BC):
    return H * RHO_I / RHO_W < -b


def grounded_fraction(H):
    """Grounded fraction at nodes from linear interpolation of the flotation height."""
    hf = H + RHO_W / RHO_I * np.minimum(BC, 0.0)        # > 0 grounded
    hl = np.concatenate([[hf[0]], hf])
    hr = np.concatenate([hf, [hf[-1]]])
    phi = np.where((hl > 0) & (hr > 0), 1.0, 0.0)
    cross = (hl > 0) != (hr > 0)
    a = np.clip(np.where(cross, np.maximum(hl, hr) / (np.abs(hl - hr) + 1e-12), 0), 0, 1)
    return np.where(cross, a, phi)


def node_H(H):
    return np.concatenate([[H[0]], 0.5 * (H[1:] + H[:-1]), [H[-1]]])


def solve_velocity(H, u, law="weertman", C=C_W, iters=40, tol=1e-3):
    s = surface(H)
    Hn = node_H(H)
    phi = grounded_fraction(H)
    sx = np.zeros(NX + 1)
    sx[1:-1] = (s[1:] - s[:-1]) / DX
    tau_d = RHO_I * G * Hn * sx
    # Effective pressure at nodes for the Coulomb law.
    Nn = np.maximum(RHO_I * G * Hn + RHO_W * G * np.minimum(BN, 0.0), 0.0)
    flt = np.concatenate([[0.0], 0.5 * (floating(H)[1:] + floating(H)[:-1]), [1.0]])
    d = max(H[-1] - s[-1], 0.0)                               # draft at the front
    front = 0.5 * G * (RHO_I * H[-1] ** 2 - RHO_W * d ** 2)
    u = u.copy()
    for _ in range(iters):
        ux = np.diff(u) / DX
        nu = 0.5 * B_GLEN * (np.abs(ux) + 1e-6) ** ((1 - N_GLEN) / N_GLEN)
        k = 4 * nu * H / DX ** 2                              # per cell
        ua = np.abs(u) + 1.0
        if law == "weertman":
            beta = C * ua ** (M - 1)
        else:
            beta = (C * ua ** M * F_COUL * Nn / (C * ua ** M + F_COUL * Nn + 1e-9)) / ua
        beta = beta * phi
        # Lateral drag where the ice floats (linearized Glen-law side shear).
        lat = flt * 2 * Hn / WIDTH * B_GLEN * (2 * ua / WIDTH) ** (1 / N_GLEN) / ua
        ab = np.zeros((3, NX + 1))
        rhs = tau_d.copy()
        ab[1, 1:-1] = -(k[1:] + k[:-1]) - beta[1:-1] - lat[1:-1]
        ab[0, 2:] = k[1:]
        ab[2, :-2] = k[:-1]
        ab[1, 0], ab[0, 1], rhs[0] = 1.0, 0.0, 0.0             # divide
        # Calving front: 4 nu H u_x = front stress.
        ab[1, -1] = k[-1] * DX
        ab[2, -2] = -k[-1] * DX
        rhs[-1] = front
        unew = solve_banded((1, 1), ab, rhs)
        unew = np.maximum(unew, 0.0)
        if np.max(np.abs(unew - u)) < tol * (np.max(np.abs(unew)) + 1):
            u = unew
            break
        u = 0.5 * u + 0.5 * unew
    return u, beta * np.abs(u)


def step_thickness(H, u, dt, melt=0.0):
    q = np.concatenate([[0.0], u[1:] * H])
    dH = ACC - np.diff(q) / DX - melt * floating(H)
    return np.maximum(H + dt * dH, 1.0)


def cfl_dt(u, dt_max, courant=0.5):
    return min(dt_max, courant * DX / (np.max(np.abs(u)) + 1e-9))


def grounding_line(H):
    hf = H + RHO_W / RHO_I * np.minimum(BC, 0.0)
    j = np.where(hf <= 0)[0]
    if len(j) == 0:
        return L
    j = j[0]
    if j == 0:
        return 0.0
    a = hf[j - 1] / (hf[j - 1] - hf[j])
    return XC[j - 1] + a * DX


def spin_up(years=15000, dt=1.0, verbose=False):
    # Start grounded everywhere and let the grounding line find its place.
    H = np.maximum(1500 * np.sqrt(np.clip(1 - XC / 700e3, 0, 1)),
                   1.1 * RHO_W / RHO_I * np.maximum(-BC, 0) + 50)
    u = np.zeros(NX + 1)
    t, next_print = 0.0, 0.0
    while t < years:
        u, _ = solve_velocity(H, u)
        h = cfl_dt(u, dt)
        H = step_thickness(H, u, h)
        t += h
        if verbose and t >= next_print:
            next_print += 1000
            print(f"t={t:6.0f}  xg={grounding_line(H)/1e3:6.1f} km  umax={u.max():6.0f}")
    return H, u


def coulomb_coefficient(H, u):
    """Coulomb-law C that reproduces the Weertman basal stress of the spun-up state."""
    _, taub = solve_velocity(H, u, "weertman")
    Hn = node_H(H)
    Nn = np.maximum(RHO_I * G * Hn + RHO_W * G * np.minimum(BN, 0.0), 0.0)
    ua = np.abs(u) + 1.0
    tw = C_W * ua ** M                       # what Weertman gives (grounded)
    fN = F_COUL * Nn
    # Invert tw = C ua^m fN / (C ua^m + fN) for C, capped where fN <= tw.
    denom = np.maximum(fN - tw, 0.05 * fN + 1.0)
    return tw * fN / denom / ua ** M


def run(H, u, law, C, years, melt_max, ramp=30.0, every=2.0):
    """Force a spun-up state with shelf melt ramping to melt_max (m/yr); snapshots every ``every`` yr."""
    H, u = H.copy(), u.copy()
    t, nxt, out = 0.0, 0.0, []
    while t <= years:
        melt = melt_max * min(t / ramp, 1.0)
        u, _ = solve_velocity(H, u, law, C)
        if t >= nxt - 1e-9:
            out.append((t, H.copy(), u.copy(), grounding_line(H), melt))
            nxt += every
        dt = cfl_dt(u, 0.25)
        dt = min(dt, max(nxt - t, 1e-3))
        H = step_thickness(H, u, dt, melt)
        t += dt
    return out
