"""Henon-Heiles Poincare section to find empirical chaos threshold.

Hamiltonian: H = (1/2)(p_x^2 + p_y^2) + (1/2)(x^2 + y^2) + x^2*y - y^3/3

Bounded below by the cubic; orbits trapped iff E < 1/6 (boundary at v(x,y)=1/6).

Procedure:
  - Vary energy E from 0.05 to 0.16 in fine steps.
  - For each energy, choose initial conditions on the y-px slice (x=0).
  - Integrate orbits; record (y, p_y) crossings of x=0 with p_x>0 (Poincare section).
  - Estimate fraction of trajectories that look chaotic (large fluctuation
    in successive section points distance from origin) vs regular (KAM-tori like).

Output: data file with (energy, frac_chaotic_estimate).
"""
import json
import time
import numpy as np
from scipy.integrate import solve_ivp


def hh_rhs(t, z):
    x, y, px, py = z
    dx = px
    dy = py
    dpx = -x - 2 * x * y
    dpy = -y - x * x + y * y
    return [dx, dy, dpx, dpy]


def total_energy(z):
    x, y, px, py = z
    return 0.5 * (px**2 + py**2) + 0.5 * (x**2 + y**2) + x * x * y - y**3 / 3.0


def section_crossings(E, y0, py0, t_max=2000.0, max_crossings=100):
    """Compute Poincare section crossings (x=0, px>0).

    Initial: x=0, y=y0, py=py0; px from energy conservation (positive root).
    """
    px0_sq = 2 * (E - 0.5 * y0**2 + y0**3 / 3.0) - py0**2
    if px0_sq < 0:
        return None
    px0 = np.sqrt(px0_sq)
    z0 = [0.0, y0, px0, py0]

    crossings = []

    def crossing_event(t, z):
        return z[0]
    crossing_event.direction = 1.0

    sol = solve_ivp(
        hh_rhs, (0, t_max), z0,
        method="DOP853",
        events=crossing_event,
        rtol=1e-10, atol=1e-12,
        dense_output=False,
        max_step=0.5,
    )
    if sol.t_events[0].size == 0:
        return None
    yp = sol.y_events[0]
    pts = np.column_stack([yp[:, 1], yp[:, 3]])
    return pts[: max_crossings]


def chaos_score(pts):
    """Heuristic: regular orbit -> section sits on a smooth curve;
    chaotic orbit -> section spreads. Score = std of pairwise distances
    from centroid (normalized by sqrt of number of points).
    Larger means more chaotic.
    """
    if pts is None or len(pts) < 10:
        return None
    c = pts.mean(axis=0)
    r = np.linalg.norm(pts - c, axis=1)
    return float(r.std())


def sweep(energies, n_ic=8, t_max=1500.0):
    out = []
    for E in energies:
        # sample initial conditions in (y, py) at x=0 within the energy ellipse
        # py^2/2 + y^2/2 - y^3/3 < E
        # pick a few random points within
        rng = np.random.default_rng(42)
        scores = []
        for _ in range(n_ic):
            for _try in range(50):
                y = rng.uniform(-0.7, 0.9)
                # max py given y at x=0, px=0:
                bound_sq = 2 * (E - 0.5 * y**2 + y**3 / 3.0)
                if bound_sq <= 0:
                    continue
                py_max = np.sqrt(bound_sq)
                py = rng.uniform(-0.95 * py_max, 0.95 * py_max)
                pts = section_crossings(E, y, py, t_max=t_max)
                if pts is not None and len(pts) >= 20:
                    s = chaos_score(pts)
                    scores.append(s)
                    break
        if scores:
            out.append({
                "E": E,
                "n_orbits": len(scores),
                "median_chaos_score": float(np.median(scores)),
                "max_chaos_score": float(max(scores)),
                "scores": [float(s) for s in scores],
            })
            print(f"E={E:.3f}  n={len(scores):2d}  med={np.median(scores):.3f}  max={max(scores):.3f}")
    return out


if __name__ == "__main__":
    t0 = time.time()
    energies = np.linspace(0.05, 0.165, 12)
    out = sweep(energies, n_ic=6, t_max=800.0)
    elapsed = time.time() - t0
    payload = {
        "elapsed_sec": elapsed,
        "energies_swept": [float(e) for e in energies],
        "results": out,
    }
    with open("D:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/_scratch_B/kam_results.json", "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Done in {elapsed:.1f}s")
