"""RIE-01 launch preflight (directive C2/C7/C10): PASS or FAIL only.
    python -m archaeon.rie.preflight
"""
from __future__ import annotations

import itertools
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

from archaeon.lineage import core as LC
from archaeon.rie import physics as P
from archaeon.rie import campaign as CP
from archaeon.rie.world import run_world, spec_id, INFLOW, DWELL

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


class _Count:
    def __init__(self): self.n = 0
    def randbelow(self, k): self.n += 1; return 0
    def next_u32(self): self.n += 1; return 0


def regimes():
    out = {}; ok = True
    w = LC.World("pf", 4, ("pf.w", 0), ("pf.m", 0), lambda *a: [(0,)]); cw, cm = _Count(), _Count(); w.rng, w.mrng = cw, cm
    w.genomes[0] = bytes(range(32))
    for reg in P.REGIMES:
        f = P.make_inputs(reg, "rie01.pf"); vals = []; det = True
        for cell in range(0, 128, 9):
            for e in range(0, 900, 7):
                a = f(w, cell if reg != "SELF_COND" else 0, e); b = f(w, cell if reg != "SELF_COND" else 0, e); det = det and a == b
                assert len(a) == P.NC and all(len(c) == 1 and 0 <= c[0] <= 255 for c in a); vals += [c[0] for c in a]
        c = Counter(vals); n = len(vals); chk = True
        if reg == "IID": chk = len(c) > 240
        if reg == "SPARSE": chk = abs(c[0] / n - (1 - 1 / P.SPARSE_P)) < 0.02
        if reg == "SHIFTING": chk = all((f(w, 5, e)[0][0] // 64) == (f(w, 9, e)[0][0] // 64) for e in range(0, 3000, 37))
        if reg == "TEMPORAL": chk = sum(f(w, 3, e) == f(w, 3, e + 1) for e in range(0, 2000)) > 1700
        if reg == "LOCAL": chk = all(f(w, 8, e) == f(w, 15, e) for e in range(0, 500, 13))
        if reg == "PERIODIC": chk = all(f(w, 2, e) == f(w, 2, e + 256) for e in range(0, 500, 11))
        if reg == "HETERO": chk = len(Counter(f(w, 7, e)[0][0] for e in range(500))) <= 2 * P.HETERO_W + 1
        if reg == "SELF_COND": chk = all(f(w, 0, e)[k][0] == (e + k) % 32 for e in range(64) for k in range(P.NC))
        out[reg] = {"deterministic": det, "property_check": chk, "distinct_values": len(c)}; ok = ok and det and chk
    return {"PASS": ok and cw.n == 0 and cm.n == 0, "regimes": out, "world_rng_draws": cw.n, "mutation_rng_draws": cm.n}


def exposure():
    out = {}
    for inf in INFLOW:
        spec = {"regime": "IID", "inflow": inf, "topology": "WELL_MIXED", "substrate": "z80", "T": 700}
        r = run_world(spec, 1); out[inf] = {"arrivals": r["arrivals"], "expected": r["expected_arrivals"], "ok": r["exposure_ok"], "wall_s": r["wall_s"]}
    return {"PASS": all(v["ok"] for v in out.values()), "levels": out}


def case0_equivalence():
    from archaeon.z80atlas.census import copier_census as C
    spec = {"regime": "TEMPORAL", "inflow": "REPLACE", "topology": "GRID", "substrate": "vmcopy", "T": 600}; tapes = [bytes.fromhex(C.SPECIMEN)] * 2000
    a = run_world(spec, 2, tapes=iter(tapes), all_cases=True); b = run_world(spec, 2, tapes=iter(tapes))
    return {"PASS": a["births"] == b["births"] and a["telemetry"] == b["telemetry"] and a["births"] > 0, "births": a["births"]}


def design():
    cells = CP.CELLS; ids = {spec_id(c) for c in cells}
    return {"PASS": len(cells) == 96 and len(ids) == 96, "cells": len(cells), "structural_zeros": 0, "reason": "full factorial; no constraint couples any factor pair",
            "wave0_worlds_per_cell": CP.WAVE0_SEEDS, "wave0_pairs_per_contrast": {f: 96 * CP.WAVE0_SEEDS // len(set(c[f] for c in cells)) for f in ("regime", "inflow", "topology", "substrate")},
            "unbiased_share_after_wave0": CP.UNBIASED_SHARE}


def throughput_storage():
    t = time.time(); r = run_world({"regime": "IID", "inflow": "STRONG", "topology": "WELL_MIXED", "substrate": "vmcopy", "T": 500}, 3)
    per_epoch = (time.time() - t) / 500; world_s = per_epoch * CP.T_EPOCHS; b = len(json.dumps(r, default=str))
    worlds_max = CP.WALL_HOURS * 3600 / 120 * CP.WORKERS                         # generous upper bound: a world every 2 min per worker
    return {"PASS": b * 40 * worlds_max / 1e9 < CP.STORAGE_GB, "strong_world_s_estimate": round(world_s), "bytes_per_empty_world": b,
            "storage_upper_bound_gb": round(b * 40 * worlds_max / 1e9, 2), "note": "populated worlds are up to ~40x an empty world's JSON"}


def attribution_tests():
    p = subprocess.run([sys.executable, "-m", "pytest", "archaeon/tests/test_lineage_attribution.py", "archaeon/tests/test_rie.py", "-q", "-p", "no:cacheprovider"],
                       cwd=REPO, capture_output=True, text=True)
    last = [l for l in p.stdout.strip().splitlines() if "passed" in l or "failed" in l][-1:]
    return {"PASS": p.returncode == 0, "summary": last}


def run():
    out = {"schema": "archaeon.rie.preflight.v1", "campaign": "RIE-01"}
    for k, f in (("design_support", design), ("regimes_and_rng_isolation", regimes), ("exposure_accounting", exposure), ("case0_equivalence", case0_equivalence),
                 ("controls", lambda: {"PASS": all((c := CP.controls(0)).values()), "result": c}), ("attribution_and_rie_tests", attribution_tests),
                 ("throughput_storage", throughput_storage)):
        out[k] = f(); print(k, out[k]["PASS"], flush=True)
    out["verdict"] = "PASS" if all(v["PASS"] for k, v in out.items() if isinstance(v, dict) and "PASS" in v) else "FAIL"
    return out


if __name__ == "__main__":
    p = run(); (HERE / "PREFLIGHT.json").write_text(json.dumps(p, indent=1, default=str) + "\n", encoding="utf-8", newline="\n"); print(p["verdict"]); sys.exit(0 if p["verdict"] == "PASS" else 4)
