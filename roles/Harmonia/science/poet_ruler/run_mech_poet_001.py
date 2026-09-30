"""Harmonia executor for Nyx packet MECH-POET-NOVELTY-ESTIMATOR-001 (freeze 291a22ed..., nyx/atlas/predictions/).

Harmonia[m2-475d761f], 2026-09-30. Taken over from offline instance gandalf-6cd1348b (Nyx #494, #1059).
Committed BEFORE its first run (STANDING_RULES B1). It implements the frozen packet literally; nothing is tuned.

The body is the fossil's own bytes: poet_distributed/novelty.py from uber-research/poet @0b40743d
(sha256 0575d92b..., Techne UPSTREAM_HASHES). It is imported from a STAGED copy outside the repository (B5), and its hash
is re-checked at import (the packet's CUT_KILL clause).

Order (B2): runtime witness (B7) -> packet hash -> body hash -> controls (cheat, positive, negative; abort on a mandatory
failure) -> cut_kill checks -> I1..I4 -> indeterminate checks -> verdicts.

Usage: python run_mech_poet_001.py --body <dir containing poet_distributed/novelty.py> --out RESULTS.json
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import random
import sys
from collections import namedtuple
from pathlib import Path

PACKET = "nyx/atlas/predictions/MECH-POET-NOVELTY-ESTIMATOR-001.json"
PACKET_SHA = "291a22ed0cbf8bea324ffc567cdd0104dbb877c9f2782285e24f4e51645cbe3a"
BODY_SHA = "0575d92b17f4a3204729f4cc4b1ec303325c4451e4bd5d9d737bd299463ad232"
TOL = 1e-12
K = 5

# POET's Env_config carries more fields; novelty.py reads only these three (its env2array).
Env = namedtuple("Env", ["ground_roughness", "pit_gap", "stump_height"])


def E(r=0.0, pit=(), stump=()):
    return Env(float(r), list(pit), list(stump))


def packet_hash(repo: Path) -> str:
    d = json.loads((repo / PACKET).read_text(encoding="utf-8"))
    b = (json.dumps(d, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def load_body(body_dir: Path):
    f = body_dir / "poet_distributed" / "novelty.py"
    h = hashlib.sha256(f.read_bytes()).hexdigest()
    spec = importlib.util.spec_from_file_location("fossil_novelty", f)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m, h


def archive_of(envs):
    return {i: e for i, e in enumerate(envs)}          # POET passes a dict; the function iterates .values()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--body", required=True)
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[4]))
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    repo = Path(a.repo)
    import numpy as np
    out = {"witness": {"python": sys.version.split()[0], "numpy": np.__version__, "platform": platform.platform(),
                       "host": platform.node()}}

    ph = packet_hash(repo)
    out["packet_sha256"] = ph
    if ph != PACKET_SHA:
        out["verdict"] = "ABORT_PACKET_HASH"
        Path(a.out).write_text(json.dumps(out, indent=1))
        return 2
    m, bh = load_body(Path(a.body))
    out["body_sha256"] = bh

    # ---- cut_kill instrumentation: env2array length and the ragged branch
    lengths, ragged = set(), []
    orig_e2a, orig_dist = m.env2array, m.euclidean_distance

    def e2a(env):
        r = orig_e2a(env)
        lengths.add(len(r))
        return r

    def dist(nx, ny, normalize=False):
        if len(orig_e2a(nx)) != len(orig_e2a(ny)):
            ragged.append(1)
        return orig_dist(nx, ny, normalize=normalize)
    m.env2array = e2a
    m.euclidean_distance = dist
    nov = m.compute_novelty_vs_archive

    # ---- controls (B2): cheat, positive, negative
    base5 = [E(r) for r in (1, 2, 3, 4, 5)]
    shuffled = base5[:]
    random.Random(20260930).shuffle(shuffled)
    cand = E(4.0)
    c_cheat = (nov(archive_of(base5), cand, K), nov(archive_of(shuffled), cand, K))
    c_pos = (nov(archive_of(base5), E(500.0), K), nov(archive_of(base5), E(3.0), K))
    ident = [E(2.0, (1.0, 1.0), (0.5, 0.5))] * 5
    c_neg = nov(archive_of(ident), E(2.0, (1.0, 1.0), (0.5, 0.5)), K)
    controls = {"C-ORDER-INVARIANCE": {"values": c_cheat, "pass": c_cheat[0] == c_cheat[1]},
                "C-POS-FAR-CANDIDATE": {"values": c_pos, "pass": c_pos[0] > c_pos[1]},
                "C-NEG-IDENTICAL": {"value": c_neg, "pass": c_neg == 0.0}}
    out["controls"] = controls
    if not all(c["pass"] for c in controls.values()):
        out["verdict"] = "ABORT_CONTROL_FAILURE"
        Path(a.out).write_text(json.dumps(out, indent=1, default=float))
        return 3

    rows, ties = {}, []

    def ksel(ds):
        s = sorted(ds)
        if len(s) > K and abs(s[K - 1] - s[K]) <= TOL:
            ties.append(True)       # index-level tie at the k boundary; the selected VALUES are still unique
        return s

    # ---- I1 regime change
    ok = True
    detail = []
    for n in range(1, 21):
        arc = [E(i) for i in range(1, n + 1)]
        v = nov(archive_of(arc), E(4.0), K)
        ds = [abs(i - 4.0) for i in range(1, n + 1)]
        s = ksel(ds)
        whole, near = sum(ds) / len(ds), sum(s[:K]) / min(K, len(s))
        exp = whole if n < K else near
        hit = abs(v - exp) <= TOL
        ok &= hit
        detail.append({"n": n, "value": v, "whole_mean": whole, "k_nearest_mean": near, "match": hit})
    rows["I1-ESTIMATOR-REGIME-CHANGE"] = {"observed": 1.0 if ok else 0.0, "band": [1.0, 1.0], "detail": detail}

    # ---- I2 unnormalised range dominance
    R = E(0.0, (), ())
    A = E(2.0, (), ())
    B = E(0.0, (), (0.75, 0.0))
    r2 = m.euclidean_distance(R, A) / m.euclidean_distance(R, B)
    r2n = orig_dist(R, A, normalize=True) / orig_dist(R, B, normalize=True)
    rows["I2-UNNORMALIZED-RANGE-DOMINANCE"] = {"observed": r2, "band": [2.6666, 2.6667], "normalized_reference": r2n}

    # ---- I3 absence equals zero presence
    P = E(0.0, (), ())
    Q = E(0.0, (0.0, 0.0), ())
    rows["I3-ABSENCE-EQUALS-ZERO-PRESENCE"] = {"observed": float(m.euclidean_distance(P, Q)), "band": [0.0, 0.0]}

    # ---- I4 deflation monotone
    series = []
    for n in range(5, 41):
        arc = [E((i * 0.37) % 8.0) for i in range(1, n + 1)]
        series.append(nov(archive_of(arc), E(4.0), K))
        ksel([abs(x.ground_roughness - 4.0) for x in arc])
    inc = sum(1 for x, y in zip(series, series[1:]) if y - x > TOL)
    rows["I4-NOVELTY-DEFLATION-MONOTONE"] = {"observed": inc, "band": [0, 0],
                                             "series_first_last": [series[0], series[-1]]}

    # ---- cut_kill and indeterminate
    kill = {"env2array_len_not_5": lengths != {5}, "ragged_branch_executed": bool(ragged),
            "body_hash_mismatch": bh != BODY_SHA, "lengths_seen": sorted(lengths)}
    out["cut_kill"] = kill
    fired = kill["env2array_len_not_5"] or kill["ragged_branch_executed"] or kill["body_hash_mismatch"]

    verdicts = {}
    for rid, r in rows.items():
        lo, hi = r["band"]
        x = r["observed"]
        edge = min(abs(x - lo), abs(x - hi)) <= TOL and not (lo == hi == x)
        if edge:
            verdicts[rid] = "PREDICTION_INDETERMINATE"
        else:
            verdicts[rid] = "CUT_SUPPORTED" if lo - TOL <= x <= hi + TOL else "PREDICTION_FAILED"
    out["rows"] = rows
    out["k_boundary_index_ties"] = len(ties)
    out["row_verdicts"] = verdicts
    if fired:
        out["verdict"] = "CUT_KILL"
    elif all(v == "CUT_SUPPORTED" for v in verdicts.values()):
        out["verdict"] = "CUT_SUPPORTED"
    elif any(v == "PREDICTION_FAILED" for v in verdicts.values()):
        out["verdict"] = "PREDICTION_FAILED"
    else:
        out["verdict"] = "PREDICTION_INDETERMINATE"
    Path(a.out).write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(json.dumps({"verdict": out["verdict"], "row_verdicts": verdicts, "controls_pass": True,
                      "cut_kill": {k: v for k, v in kill.items() if k != "lengths_seen"},
                      "k_boundary_index_ties": len(ties)}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
