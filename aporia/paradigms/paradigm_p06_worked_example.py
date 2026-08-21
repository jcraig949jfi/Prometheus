"""PARADIGM-P06 worked example — Geometric Flow, executed.

The paradigm's move: continuously deform an object until it reaches canonical
form; the flow does the work. Executable instance: discrete curve-shortening
flow (Gage-Hamilton-Grayson at polygon level). Any embedded closed curve,
however wild, flows to a round point; normalizing scale, the isoperimetric
ratio L^2/(4*pi*A) descends toward its absolute minimum 1 (the circle), and
that monotone descent IS the canonicalization.

Discrete flow DERIVED, not transcribed (P82 lesson): each vertex moves toward
the midpoint of its neighbors (discrete Laplacian smoothing = curvature-normal
motion for polygons); after each step the polygon is rescaled to unit area so
the flow shows SHAPE evolution, not shrinkage.

Instrument gates, each with its own gate (P82 lesson):
  - area/length computed by shoelace + norm sums; VALIDATED first on a square
    (L^2/4piA = 16/(4pi) = 4/pi, known exact) before flowing anything.
  - step size fixed at 0.25 (midpoint blend), resampling to uniform arc-length
    every step to prevent vertex clustering (the discrete flow's known failure).

Pre-stated readings (BEFORE run):
  FLOW-CANONICALIZES  isoperimetric ratio strictly decreasing (up to 1e-12
                      tolerance) at every recorded step AND final ratio < 1.01
                      from a wildly non-convex start.
  FLOW-DIVERGES       any increase or blow-up — instrument-first: resampling,
                      step size, area sign (orientation).
"""
from __future__ import annotations
import json
import math
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p06_results.json"
rng = np.random.default_rng(20260883)


def area(P):
    x, y = P[:, 0], P[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def length(P):
    return float(np.sum(np.linalg.norm(np.roll(P, -1, axis=0) - P, axis=1)))


def iso_ratio(P):
    return length(P) ** 2 / (4 * math.pi * area(P))


def resample(P, n):
    seg = np.linalg.norm(np.roll(P, -1, axis=0) - P, axis=1)
    t = np.concatenate([[0.0], np.cumsum(seg)])
    total = t[-1]
    targets = np.linspace(0, total, n, endpoint=False)
    Q = np.empty((n, 2))
    j = 0
    for i, tt in enumerate(targets):
        while t[j + 1] < tt:
            j += 1
        f = (tt - t[j]) / max(t[j + 1] - t[j], 1e-15)
        Q[i] = P[j % len(P)] * (1 - f) + P[(j + 1) % len(P)] * f
    return Q


# --- gate for the measuring instruments: exact square ------------------------
sq = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=float)
want = 4.0 / math.pi
got = iso_ratio(sq)
assert abs(got - want) < 1e-12, f"instrument gate FAILS on square: {got} vs {want}"
print(f"instrument gate: square iso ratio {got:.12f} == 4/pi (exact) — PASS", flush=True)

# --- wild initial curve: star-burst polygon ----------------------------------
n = 400
ang = np.linspace(0, 2 * math.pi, n, endpoint=False)
radii = 1.0 + 0.7 * np.sin(9 * ang) + 0.25 * rng.standard_normal(n)
radii = np.clip(radii, 0.15, None)
P = np.stack([radii * np.cos(ang), radii * np.sin(ang)], axis=1)
P /= math.sqrt(area(P))

trace = [iso_ratio(P)]
STEPS = 4000
for step in range(STEPS):
    P = 0.75 * P + 0.25 * 0.5 * (np.roll(P, 1, axis=0) + np.roll(P, -1, axis=0))
    P = resample(P, n)
    P /= math.sqrt(area(P))
    if (step + 1) % 400 == 0:
        trace.append(iso_ratio(P))
        print(f"step {step+1:5d}: iso ratio {trace[-1]:.6f}", flush=True)

decreasing = all(trace[i + 1] <= trace[i] + 1e-12 for i in range(len(trace) - 1))
final = trace[-1]
verdict = "FLOW-CANONICALIZES" if (decreasing and final < 1.01) else "FLOW-DIVERGES"
print(f"start ratio {trace[0]:.4f} -> final {final:.6f}, monotone={decreasing} -> {verdict}", flush=True)

OUT.write_text(json.dumps({
    "protocol": "discrete curve-shortening (Laplacian blend 0.25, uniform-arc resample, unit-area renormalization), star-burst n=400 seed 20260883, square instrument gate",
    "instrument_gate_square": got, "trace_iso_ratio": [round(t, 6) for t in trace],
    "monotone": decreasing, "final_ratio": final, "verdict": verdict}, indent=1),
    encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
