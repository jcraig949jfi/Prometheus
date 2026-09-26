"""WTP-LM01 selectivity reading relative to the rate-matched blind reference (D4, JOINT #652/#653).

  refs     = K independently seeded IM-rate merges, each bisected to the arm's HR2 (fixtures.im_rate)
  matched  = the refs within MATCH_TOL of the arm's HR2. With fewer than K_MIN matched, the reading is UNMATCHED.
  gap      = HR2_signal(arm) - median(HR2_signal(matched refs))
  SELECTIVE_LOSS iff gap > THRESHOLD, where THRESHOLD is DERIVED here from the spread of reference-minus-reference
  differences (independent seeds at matched HR2) on dev planted worlds. It is the 99th percentile of |difference|,
  committed with its inputs in dev/selectivity_threshold.json.
derive_threshold() is the committed calculation. Its inputs: planted-world seeds 9_310_000.., revisit densities
0.8/1.6/2.9 visits/cell, K=5 references each."""
import json
import os

import numpy as np

from .fixtures import im_rate, planted, _feed, OracleProjector, LOSSLESS_HR2, MATCH_TOL
from .arms import LosslessK
from .recover import recoverability

K_REFS, K_MIN = 5, 3
REF_SEED0 = 7_000
OUT = os.path.join(os.path.dirname(__file__), "dev", "selectivity_threshold.json")


def references(dims, A, y, target, rr, base_seed, k=K_REFS):
    return [im_rate(dims, A, y, target, rr, base_seed + REF_SEED0 + i) for i in range(k)]


def read(arm_r, refs, threshold):
    if arm_r["HR2"] >= LOSSLESS_HR2:
        return dict(verdict="NO_LOSS", gap=None, n_matched=0)
    m = [r for r in refs if abs(r["HR2"] - arm_r["HR2"]) <= MATCH_TOL]
    if len(m) < K_MIN:
        return dict(verdict="UNMATCHED", gap=None, n_matched=len(m))
    gap = arm_r["HR2_signal"] - float(np.median([r["HR2_signal"] for r in m]))
    return dict(verdict="SELECTIVE_LOSS" if gap > threshold else "BLIND_LOSS", gap=gap, n_matched=len(m))


def derive_threshold(seeds=range(9_310_000, 9_310_010), densities=(0.8, 1.6, 2.9), cells=512, q=99):
    """Reference-minus-reference spread at matched HR2. The target HR2 is the oracle F-S's HR2 on each world (the rate
    at which the selective reading will actually be made in the fixtures)."""
    diffs, rows = [], []
    for sd in seeds:
        for dens in densities:
            w = planted(sd, n=int(dens * cells))
            A, y, sg = w["A"], w["y"], w["signal"]
            rr = lambda arm: recoverability(arm, A, y, tau=0.1, rng=np.random.default_rng(sd + 1), signal=sg)
            fs = rr(_feed(OracleProjector(w["dims"], w["U"], w["s"]), A, y))
            refs = [r for r in references(w["dims"], A, y, fs["HR2"], rr, sd) if abs(r["HR2"] - fs["HR2"]) <= MATCH_TOL]
            sig = [r["HR2_signal"] for r in refs]
            for i in range(len(sig)):
                for j in range(i + 1, len(sig)):
                    diffs.append(abs(sig[i] - sig[j]))
            rows.append(dict(seed=int(sd), density=dens, target=fs["HR2"], n_matched=len(refs), ref_signal=sig,
                             oracle_signal=fs["HR2_signal"]))
    thr = float(np.percentile(diffs, q)) if diffs else None
    out = dict(threshold=thr, q=q, n_pairs=len(diffs), seeds=[seeds.start, seeds.stop - 1], densities=list(densities),
               k_refs=K_REFS, match_tol=MATCH_TOL, rows=rows)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    return out


def load_threshold():
    with open(OUT) as f:
        return json.load(f)["threshold"]


def calibrate_relative(seed=9_300_000, n=800, threshold=None):
    """Directive s11 / method rule: the D4 reading must itself pass the known-answer trio."""
    threshold = load_threshold() if threshold is None else threshold
    w = planted(seed, n=n)
    A, y, sg = w["A"], w["y"], w["signal"]
    rr = lambda arm: recoverability(arm, A, y, tau=0.1, rng=np.random.default_rng(seed + 1), signal=sg)
    fl = rr(_feed(LosslessK(w["dims"]), A, y))
    fs = rr(_feed(OracleProjector(w["dims"], w["U"], w["s"]), A, y))
    fb = im_rate(w["dims"], A, y, fs["HR2"], rr, seed + 3)
    out = {"F-L": dict(read(fl, [], threshold), expect="NO_LOSS"),
           "F-S": dict(read(fs, references(w["dims"], A, y, fs["HR2"], rr, seed), threshold), expect="SELECTIVE_LOSS"),
           "F-B": dict(read(fb, references(w["dims"], A, y, fb["HR2"], rr, seed + 50), threshold), expect="BLIND_LOSS")}
    out["PASS"] = all(v["verdict"] == v["expect"] for v in out.values() if isinstance(v, dict))
    out["threshold"] = threshold
    return out
