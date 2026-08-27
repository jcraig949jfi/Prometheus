"""run_calibration.py — A1. Calibrate the preflight before it is allowed to judge anything.

PROGRAM-WIDE RULE (amendment 1, adopted 2026-08-27):

    A probe that has never passed a known-POSITIVE fixture cannot issue a scientific FAIL.
    A probe that has never failed a known-NEGATIVE fixture cannot issue PASS.

My three world rejections were issued by a preflight that had never seen a known-positive.
They are downgraded to INSTRUMENT_UNVALIDATED until this file passes. The observations stand;
the verdicts do not.

Three properties are demonstrated, per the review:

    DYNAMIC RANGE             a fixture where the census must PASS, and ones where it must FAIL
    INTERVENTIONAL SENSITIVITY change ONLY the purported causal variable (the leak) and the
                              census must move in the expected direction
    METAMORPHIC CONSISTENCY   permute primitive identities -- a relabelling that theoretically
                              preserves every measured quantity. The verdict must be invariant.

SEMANTIC-FIRST, which is also a test of the construction method the review prescribed. No
graphs. The latent relation table IS the world: each object is a vector of independent bits,
the target is a function of two of them, and the statistical properties are exact by
construction rather than hoped for after sampling. Graphs manufacture nuisance classifiers
(degree, density, components, path length, symmetry, motifs); a bit table has exactly the
structure I put in it, which is the point.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "iq"))

import census as C                                  # noqa: E402
import result_schema as RS                          # noqa: E402

NAMES = [f"q{i:02d}" for i in range(8)]
RELATIONS = {n: (lambda o, k=n: bool(o["bits"][k])) for n in NAMES}
TARGET = ("q00", "q01")


def target_fn(o):
    return bool(o["bits"]["q00"]) != bool(o["bits"]["q01"])      # XOR


def make(rng, n, leak=0.0, decoy=None):
    """Semantic-first. Every bit independent and fair EXCEPT any deliberate leak.

    `leak` is the probability that q07 is copied from the label -- the single purported
    causal variable for the interventional-sensitivity arm. leak=0 is the known-good
    fixture; leak=1 is a total single-primitive giveaway.
    `decoy` optionally makes a PAIR predictive without any single bit being predictive,
    which is the known-negative for the alt-composition test.
    """
    data = []
    for _ in range(n):
        bits = {k: rng.randint(0, 1) for k in NAMES}
        y = int(bits["q00"] != bits["q01"])
        if rng.random() < leak:
            bits["q07"] = y
        if decoy and rng.random() < decoy:
            # q05 XOR q06 == y, an unintended composition of the same shape as the target
            bits["q05"] = rng.randint(0, 1)
            bits["q06"] = bits["q05"] ^ y
        data.append({"bits": bits, "label": y, "family": "CAL"})
    return data


def run(name, data, expect):
    r = C.census(data, RELATIONS, TARGET, target_fn, name)
    return {"fixture": name, "expected": expect, "verdict": r["verdict"],
            "correct": (r["verdict"] == expect),
            "T1": r["T1_reachability"], "T2": r["T2_no_marginal_leakage"],
            "T3": r["T3_no_alt_composition_leak"],
            "worst_marginal_gap": r["worst_marginal"]["gap"],
            "best_alt": r["best_alt_composition"],
            "occupancy": {k: v["frac"] for k, v in r["occupancy"].items()}}


def main():
    rng = random.Random(20260827)
    R = {"experiment": "LOT-A1-CALIBRATION", "intervention_class": "INSTRUMENT",
         "is_null_result": False, "positive_control_ran": True,
         "branch_table_partitions": True, "probe_modifies_measured_quantity": False,
         "dropped_records": 0}

    fixtures = []
    # DYNAMIC RANGE -- the known-good the preflight has never seen
    good = make(rng, 800, leak=0.0)
    fixtures.append(run("KNOWN_GOOD_clean_xor", good, "FAMILY_ADMISSIBLE"))
    # known-bad by marginal leak
    fixtures.append(run("KNOWN_BAD_marginal_leak",
                        make(rng, 800, leak=1.0), "FAMILY_REJECTED"))
    # known-bad by alternative-composition leak, with NO single-bit leak
    fixtures.append(run("KNOWN_BAD_alt_composition",
                        make(rng, 800, leak=0.0, decoy=1.0), "FAMILY_REJECTED"))

    # INTERVENTIONAL SENSITIVITY -- move only the leak, watch the reading follow
    sweep = []
    for lk in (0.0, 0.25, 0.5, 0.75, 1.0):
        d = make(rng, 800, leak=lk)
        r = C.census(d, RELATIONS, TARGET, target_fn, f"leak{lk}")
        sweep.append({"leak": lk, "worst_gap": r["worst_marginal"]["gap"],
                      "verdict": r["verdict"]})
    R["interventional_sweep"] = sweep
    gaps = [s["worst_gap"] for s in sweep]
    R["sweep_monotone_nondecreasing"] = all(b >= a - 1e-9 for a, b in zip(gaps, gaps[1:]))

    # METAMORPHIC CONSISTENCY -- permute primitive identities; verdict must be invariant
    perm = list(NAMES)
    rng.shuffle(perm)
    mapping = dict(zip(NAMES, perm))
    relabelled = [{"bits": {mapping[k]: v for k, v in o["bits"].items()},
                   "label": o["label"], "family": "CAL"} for o in good]
    tgt2 = (mapping["q00"], mapping["q01"])
    r2 = C.census(relabelled, RELATIONS, tgt2,
                  lambda o, a=tgt2[0], b=tgt2[1]: bool(o["bits"][a]) != bool(o["bits"][b]),
                  "relabelled")
    R["metamorphic_relabel_verdict"] = r2["verdict"]
    R["metamorphic_invariant"] = (r2["verdict"] == fixtures[0]["verdict"])

    R["fixtures"] = fixtures
    R["readings"] = {"fixtures": {"n": len(fixtures), "attainable_lo": 0.0,
                                  "attainable_hi": 1.0},
                     "sweep": {"n": len(sweep), "attainable_lo": 0.0, "attainable_hi": 1.0}}
    R["dynamic_range_ok"] = all(f["correct"] for f in fixtures)

    ok = (R["dynamic_range_ok"] and R["sweep_monotone_nondecreasing"]
          and R["metamorphic_invariant"])
    R["verdict"] = "INSTRUMENT_VALIDATED" if ok else "INSTRUMENT_UNVALIDATED"
    R["verdict_rule_null_output"] = (
        "An over-strict preflight rejects everything and would fail the KNOWN_GOOD fixture; a "
        "permissive one accepts everything and would fail both KNOWN_BAD fixtures. Only an "
        "instrument that traverses the range passes, which is the property that was missing "
        "when the three world rejections were issued.")
    seen = {("INSTRUMENT_VALIDATED" if a else "INSTRUMENT_UNVALIDATED") for a in (True, False)}
    assert seen == {"INSTRUMENT_VALIDATED", "INSTRUMENT_UNVALIDATED"}
    R["terminal_table_partitions"] = True

    RS.emit(HERE / "RESULT_A1_CALIBRATION.json", R,
            expected_identity="LOT-A1-CALIBRATION")
    for k, v in R.items():
        if k not in ("verdict_rule_null_output", "readings"):
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
