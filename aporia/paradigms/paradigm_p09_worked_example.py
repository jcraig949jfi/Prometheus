"""PARADIGM-P09 worked example — Exhaustive Computation, executed.

The paradigm's move: reduce to finitely many cases and verify each by
machine — the computer IS the proof. Executable instance: a complete machine
proof of R(3,3) = 6, both directions, full enumeration (no sampling, no
symmetry shortcuts — the point is the exhaustion):

  LOWER (R(3,3) > 5): enumerate ALL 2^C(5,2) = 1,024 colorings of K_5; count
    those with no monochromatic triangle. A nonzero count proves the bound;
    the exact count is reported raw (its symmetry structure is a free
    observable, not an assumption).
  UPPER (R(3,3) <= 6): enumerate ALL 2^C(6,2) = 32,768 colorings of K_6;
    EVERY one must contain a monochromatic triangle. Zero exceptions = the
    theorem, by machine.

Pre-stated readings (BEFORE run):
  EXHAUSTION-PROVES  K_5 triangle-free-coloring count > 0 AND K_6 exceptions
                     == 0 over the full 32,768.
  ENCODING-FAULT     otherwise — instrument-first: edge indexing, triangle
                     enumeration, bit order. Gate on a known: the all-red
                     coloring of K_5 must report C(5,3)=10 monochromatic
                     triangles or the counter is broken.
"""
from __future__ import annotations
import json
import pathlib
from itertools import combinations
from math import comb

import numpy as np

HERE = pathlib.Path(__file__).parent
OUT = HERE / "paradigm_p09_results.json"


def build(n):
    edges = list(combinations(range(n), 2))
    eidx = {e: i for i, e in enumerate(edges)}
    tris = [[eidx[(a, b)], eidx[(a, c)], eidx[(b, c)]]
            for a, b, c in combinations(range(n), 3)]
    return edges, np.array(tris)


def mono_count(colbits, tris, m):
    col = (colbits >> np.arange(m)) & 1
    t = col[tris]
    return int(np.sum(np.all(t == 1, axis=1) | np.all(t == 0, axis=1)))


# --- instrument gate on an exact known ---------------------------------------
edges5, tris5 = build(5)
m5 = len(edges5)
gate = mono_count(0, tris5, m5)          # all-zero coloring = all one color
assert gate == comb(5, 3), f"counter gate FAILS: {gate} vs {comb(5,3)}"
print(f"instrument gate: all-red K5 reports {gate} == C(5,3) mono triangles — PASS", flush=True)

# --- LOWER: full enumeration of K_5 ------------------------------------------
good5 = sum(1 for c in range(2 ** m5) if mono_count(c, tris5, m5) == 0)
print(f"LOWER: {good5} of {2**m5} K5 colorings have NO mono triangle "
      f"(raw count; nonzero proves R(3,3) > 5)", flush=True)

# --- UPPER: full enumeration of K_6 ------------------------------------------
edges6, tris6 = build(6)
m6 = len(edges6)
exceptions = sum(1 for c in range(2 ** m6) if mono_count(c, tris6, m6) == 0)
print(f"UPPER: {exceptions} of {2**m6} K6 colorings lack a mono triangle "
      f"(zero = theorem proven by machine)", flush=True)

verdict = "EXHAUSTION-PROVES" if (good5 > 0 and exceptions == 0) else "ENCODING-FAULT"
print(f"R(3,3) = 6 {'PROVEN' if verdict=='EXHAUSTION-PROVES' else 'NOT proven'} "
      f"by full enumeration -> {verdict}", flush=True)

OUT.write_text(json.dumps({
    "protocol": "complete enumeration both directions (1,024 K5 + 32,768 K6 colorings), all-red counter gate, no sampling, no symmetry reduction",
    "gate_all_red_K5": gate, "K5_triangle_free_colorings": good5,
    "K5_total": 2 ** m5, "K6_exceptions": exceptions, "K6_total": 2 ** m6,
    "verdict": verdict}, indent=1), encoding="utf-8")
print(f"-> {OUT.name}", flush=True)
