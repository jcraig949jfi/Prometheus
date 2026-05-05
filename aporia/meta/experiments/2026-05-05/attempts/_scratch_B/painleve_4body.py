"""Simulate 4-body planar Newton problem with candidate near-singular
configurations and measure rate of energy / radius divergence.

Goal: produce real numerical data about whether a candidate
non-collision singularity scenario for n=4 actually shows divergence
(it shouldn't fully — the construction is open — but we can document
how close orbits come to escape in finite time).

We try a planar 2+2 configuration: two binary pairs counter-orbiting
at large distance, with deliberately tuned phases to feed energy from
internal binding to translational motion.
"""
import json
import time
import numpy as np
from scipy.integrate import solve_ivp

G = 1.0


def n_body_rhs(t, state, masses):
    n = len(masses)
    pos = state[: 2 * n].reshape(n, 2)
    vel = state[2 * n :].reshape(n, 2)
    acc = np.zeros_like(pos)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            r = pos[j] - pos[i]
            d2 = np.dot(r, r)
            if d2 < 1e-16:
                d2 = 1e-16
            d = np.sqrt(d2)
            acc[i] += G * masses[j] * r / (d2 * d)
    return np.concatenate([vel.flatten(), acc.flatten()])


def total_energy(state, masses):
    n = len(masses)
    pos = state[: 2 * n].reshape(n, 2)
    vel = state[2 * n :].reshape(n, 2)
    K = 0.5 * sum(masses[i] * np.dot(vel[i], vel[i]) for i in range(n))
    U = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            r = np.linalg.norm(pos[j] - pos[i])
            U -= G * masses[i] * masses[j] / max(r, 1e-12)
    return K + U


def min_separation(state, n=4):
    pos = state[: 2 * n].reshape(n, 2)
    return min(np.linalg.norm(pos[j] - pos[i]) for i in range(n) for j in range(i + 1, n))


def max_distance_from_origin(state, n=4):
    pos = state[: 2 * n].reshape(n, 2)
    return max(np.linalg.norm(pos[i]) for i in range(n))


def run_2plus2_config(R=10.0, r=0.3, v_pair=1.5, v_sep=0.4, t_max=200.0,
                      masses=(1.0, 1.0, 1.0, 1.0)):
    """Two binaries at +R and -R on x-axis; each binary tight, internal
    speed v_pair perpendicular to x-axis; binary CMs moving outward at
    v_sep along x-axis (away from each other)."""
    masses = np.array(masses)
    pos = np.array([
        [+R + r/2, 0.0],
        [+R - r/2, 0.0],
        [-R - r/2, 0.0],
        [-R + r/2, 0.0],
    ])
    vel = np.array([
        [+v_sep, +v_pair],
        [+v_sep, -v_pair],
        [-v_sep, -v_pair],
        [-v_sep, +v_pair],
    ])
    state = np.concatenate([pos.flatten(), vel.flatten()])
    E0 = total_energy(state, masses)

    # collision detection event
    def near_collision(t, z):
        return min_separation(z, 4) - 1e-3
    near_collision.terminal = True
    near_collision.direction = -1.0

    sol = solve_ivp(
        lambda t, s: n_body_rhs(t, s, masses),
        (0.0, t_max), state,
        method="DOP853",
        events=near_collision,
        rtol=1e-11, atol=1e-13,
        max_step=0.05,
    )
    Es = [total_energy(sol.y[:, k], masses) for k in range(sol.y.shape[1])]
    rmaxs = [max_distance_from_origin(sol.y[:, k]) for k in range(sol.y.shape[1])]
    rmins = [min_separation(sol.y[:, k]) for k in range(sol.y.shape[1])]
    return {
        "t_final": float(sol.t[-1]),
        "t_max_requested": float(t_max),
        "terminated_by_collision": bool(sol.status == 1),
        "n_steps": int(sol.y.shape[1]),
        "E_initial": float(E0),
        "E_final": float(Es[-1]),
        "E_drift_relative": float(abs(Es[-1] - E0) / max(abs(E0), 1e-12)),
        "rmax_initial": float(rmaxs[0]),
        "rmax_final": float(rmaxs[-1]),
        "rmax_growth_rate_at_end": float((rmaxs[-1] - rmaxs[-min(20, len(rmaxs))]) / max(sol.t[-1] - sol.t[-min(20, len(sol.t))], 1e-9)),
        "min_separation_seen": float(min(rmins)),
        "params": {"R": R, "r": r, "v_pair": v_pair, "v_sep": v_sep, "t_max": t_max},
    }


def run_1plus3_oscillator(R=12.0, r=0.4, v_pair=1.6, v_osc=0.3, t_max=250.0):
    """1 + 3 configuration: outer binary at +R, isolated body moving
    near triple Lagrange-equilateral with two outer bodies."""
    # not Xia's; just exploratory
    masses = np.array([1.0, 1.0, 1.0, 1.0])
    pos = np.array([
        [+R + r/2, 0.0],
        [+R - r/2, 0.0],
        [-R, +R * 0.866],
        [-R, -R * 0.866],
    ])
    vel = np.array([
        [+0.0, +v_pair],
        [+0.0, -v_pair],
        [+v_osc, +0.2],
        [+v_osc, -0.2],
    ])
    state = np.concatenate([pos.flatten(), vel.flatten()])
    E0 = total_energy(state, masses)

    def near_collision(t, z):
        return min_separation(z, 4) - 1e-3
    near_collision.terminal = True
    near_collision.direction = -1.0

    sol = solve_ivp(
        lambda t, s: n_body_rhs(t, s, masses),
        (0.0, t_max), state,
        method="DOP853",
        events=near_collision,
        rtol=1e-11, atol=1e-13,
        max_step=0.05,
    )
    Es = [total_energy(sol.y[:, k], masses) for k in range(sol.y.shape[1])]
    rmaxs = [max_distance_from_origin(sol.y[:, k]) for k in range(sol.y.shape[1])]
    rmins = [min_separation(sol.y[:, k]) for k in range(sol.y.shape[1])]
    return {
        "t_final": float(sol.t[-1]),
        "terminated_by_collision": bool(sol.status == 1),
        "E_initial": float(E0),
        "E_final": float(Es[-1]),
        "E_drift_relative": float(abs(Es[-1] - E0) / max(abs(E0), 1e-12)),
        "rmax_initial": float(rmaxs[0]),
        "rmax_final": float(rmaxs[-1]),
        "min_separation_seen": float(min(rmins)),
        "params": {"R": R, "r": r, "v_pair": v_pair, "v_osc": v_osc, "t_max": t_max},
    }


if __name__ == "__main__":
    t0 = time.time()
    results = {}
    print("Run 2+2:")
    results["2+2_run"] = run_2plus2_config()
    print(f"  t_final={results['2+2_run']['t_final']:.2f}  rmax: {results['2+2_run']['rmax_initial']:.2f} -> {results['2+2_run']['rmax_final']:.2f}")
    print(f"  E drift: {results['2+2_run']['E_drift_relative']:.2e}")
    print(f"  min_sep: {results['2+2_run']['min_separation_seen']:.2e}")
    print(f"  collision_terminated: {results['2+2_run']['terminated_by_collision']}")

    print("\nRun 1+3:")
    results["1+3_run"] = run_1plus3_oscillator()
    print(f"  t_final={results['1+3_run']['t_final']:.2f}  rmax: {results['1+3_run']['rmax_initial']:.2f} -> {results['1+3_run']['rmax_final']:.2f}")
    print(f"  E drift: {results['1+3_run']['E_drift_relative']:.2e}")
    print(f"  min_sep: {results['1+3_run']['min_separation_seen']:.2e}")
    print(f"  collision_terminated: {results['1+3_run']['terminated_by_collision']}")

    # Vary v_sep to see if any fast-escape regime emerges
    print("\nv_sep sweep on 2+2:")
    sweep_results = []
    for vs in [0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.2]:
        r = run_2plus2_config(v_sep=vs, t_max=100.0)
        sweep_results.append({"v_sep": vs, **r})
        print(f"  v_sep={vs:.2f}  rmax_final={r['rmax_final']:.2f}  E_drift={r['E_drift_relative']:.2e}")
    results["v_sep_sweep"] = sweep_results

    elapsed = time.time() - t0
    payload = {"elapsed_sec": elapsed, "results": results}
    with open("D:/Prometheus/aporia/meta/experiments/2026-05-05/attempts/_scratch_B/painleve_results.json", "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nDone in {elapsed:.1f}s")
