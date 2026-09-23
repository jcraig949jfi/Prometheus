"""The smallest successor world family (constructed, NOT run in cycle 7): the invariant plateau found by
P-I01/P-I02 is IDENTITY with the regime word ingested but unused. The successor keeps every property of
A / B / C (the regime changes the answer; no privileged signal; invariant ceiling .5) and changes ONE
thing: the regime-1 transform is v XOR 1 (the low bit flipped) instead of 15 - v, so that the
conditional answer is one instruction (XOR of two registers the program already holds) away from
identity. Ceilings are computed here and the candidate P-J01 is preregistered for cycle 8."""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
sys.path.insert(0, str(HERE.parent / "experiments" / "cw01-arch4"))
import recordsafety as RS      # noqa: E402
import ctxworlds as CW         # noqa: E402

OUT = HERE / "PERTURBATIONS.jsonl"


def f_xor(r, v):
    return v ^ r


def ceilings_xor(n_sets=200):
    """Invariant ceilings for the XOR family: identical to the complement family by construction (a fixed
    transform of v matches one regime per v), verified numerically on regenerated regimes."""
    out = {}
    for w in "ABC":
        acc = []
        for i in range(n_sets):
            eps = CW.make(w, 7, i)
            R = [r for e in eps for r in e.meta["regime"]]
            # best fixed transform among {identity, xor 1}: matches regime 0 or regime 1 asks
            acc.append(max(np.mean([r == 0 for r in R]), np.mean([r == 1 for r in R])))
        out[w] = {"invariant_best": {"mean": float(np.mean(acc)), "p95": float(np.percentile(acc, 95))}, "one_step_from_identity": "XOR r_reg, v_reg (regime word already held in a register per P-I02)"}
    return out


def main():
    ceil = ceilings_xor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    cand = dict(id="P-J01", parent="T-X21", family="context_worlds", axis="successor worlds: one-instruction regime transform", type="world-construction", deformation="W", batch="J", recorded=ts,
                delta="SUCCESSOR WORLDS A' / B' / C' (constructed in cycle 7, run in cycle 8): identical to A / B / C except that regime 1 expects v XOR 1 (the low bit flipped) instead of 15 - v. Invariant ceiling unchanged (.5 mean; %s); the conditional answer is ONE instruction (XOR of the regime register and the value register) away from the identity plateau on which P-I01's populations sat with the regime word already in a register. Same evolution, controls, thresholds and forensics as P-I01 / P-I02. Loophole record: the P-I01 plateau (identity + ingested-but-unused regime word) is provably still the invariant optimum here, but a single mutation now has a fitness path off it." % json.dumps({w: round(v["invariant_best"]["mean"], 3) for w, v in ceil.items()}),
                unchanged="worlds' structure, cue placement, no privileged signal, thresholds", attacks="the zero-gradient plateau found in P-I01 / P-I02", nonredundant="the only change is the transform's step size from identity", cost_minutes=10,
                continuation=["if crossed: regime transforms of increasing mutational distance (XOR 3, XOR 15, 15 - v) to measure the reachable step", "if not crossed: population / episode-count doses"],
                scores=dict(attacks_old_assumption=3, failure_surface_perturbable=3, unexplained_structure=3, independent_intersection=3, regime_newly_reachable=3, information_gain=3, delta_novelty=2, mechanism_discrimination=3, cost_now_lower=2, null_becomes_contrast=3, inconclusive_now_posable=3, underexplored_hard_to_operationalise=2),
                ceilings=ceil)
    existing = {json.loads(l)["id"] for l in OUT.read_text(encoding="utf-8").splitlines() if l.strip()}
    if cand["id"] not in existing:
        with OUT.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(cand, ensure_ascii=True) + "\n")
    RS.require_ascii_safe(OUT)
    (HERE / "SUCCESSOR_WORLDS_CYCLE7.json").write_text(json.dumps({"written": ts, "plateau": "identity with the regime word ingested but unused (P-I02)", "successor": cand["delta"], "ceilings": ceil}, indent=1, ensure_ascii=True), encoding="utf-8")
    print("successor constructed; P-J01 preregistered; ceilings", {w: round(v["invariant_best"]["mean"], 3) for w, v in ceil.items()})


if __name__ == "__main__":
    main()
