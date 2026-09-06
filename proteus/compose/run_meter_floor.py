"""T2 -- the chance floor for the meter observable.

    python proteus/compose/run_meter_floor.py

WHY THIS EXISTS. The closure pass found the probe transcript degenerate (3 classes over 56
segment players, 87.5% in one) and proposed the meter vector instead (37 classes at 10.7%).
TODO T2 records the objection against that proposal: 37-at-10.7% is uninterpretable without a
null, in exactly the way the transcript result is. A richer observable is not automatically a
better one -- it can be richer because it responds to something the experiment does not care
about.

The thing it most obviously responds to is SIZE. `ops` counts executed instructions, and a
composition A+B is twice the length of A. So `meter(A+B) != meter(A)` is very nearly guaranteed
for a reason that has nothing to do with B contributing anything. The integration directive names
this confound directly: an A+B claim must be distinguishable from "larger program size" and
"extra compute". This script measures that.

WHAT IS MEASURED

  PART 0  Determinism gate. The meter is only usable as an identity-bearing observable if it
          reproduces. Also run as a NEGATIVE CONTROL on the full meter INCLUDING wall_s/cpu_s,
          to show the exclusion of the timing fields is necessary rather than decorative.

  PART 1  Population structure floor. Resample populations of random 2-instruction segment
          players and count distinct classes under each observable. Answers: is "37 classes" a
          property of the meter, or just what any arbitrary population of this shape yields?

  PART 2  Discrimination floor -- the decisive part. Five rates on matched pairs:

            identity      meter(A)        vs meter(A)          must be 0.000
            SIZE FLOOR    meter(A)        vs meter(A + NOPpad) same behaviour, bigger program
            treatment     meter(A)        vs meter(A + B)      what the experiment wants to use
            size-matched  meter(A+NOPpad) vs meter(A + B)      does B add beyond its length?
            independent   meter(A)        vs meter(A')         unrelated player, same size

          READING: if `treatment` is not clearly above `SIZE FLOOR`, then the meter's apparent
          sensitivity to composition is sensitivity to length. `size-matched` is the honest
          number for "can this observable see B at all".

CAVEAT, STATED NOT BURIED. NOP padding is inert as INSTRUCTIONS but not as DATA: the genome is
copied into the tape, so a padding word is also a datum an LD can read. This is the same
NOP-alias differential the ablation work documented. The size floor is therefore a LOWER bound on
size-driven differences; the padding is run under all three NOP aliases and disagreement is
reported rather than averaged away.

NOTHING HERE SELECTS, SCORES OR INTERPRETS A PLAYER. All rates are over an arbitrary ensemble.
"""
from __future__ import annotations

import json
import os
import statistics
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from proteus.compose.segments import (IW, NOP_ALIASES, compose, segment_from_instructions)  # noqa: E402
from proteus.foundry.identity import hash_obj  # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from  # noqa: E402
from proteus.foundry.probes import DEFAULT_ENSEMBLE, build_probes, run_ensemble  # noqa: E402
from proteus.foundry.vm import Meter  # noqa: E402

REG_PATH = os.path.join(ROOT, "proteus", "integration", "PLAYER_REGISTRY.json")
OUT = os.path.join(ROOT, "proteus", "v0_7", "RESULT_METER_FLOOR.json")

ENVELOPE = {"n_regs": 8, "tape_words": 256, "code_writable": False,
            "persist": "none", "tick_budget": 256, "out_cap": 4}
SEGMENT_INSTRUCTIONS = 2
POP_SIZE = 56          # matches the population the 37-class figure was measured on
N_POPULATIONS = 200    # resamples for the structure floor
N_PAIRS = 200          # matches run_ab_readiness

#: Timing fields are excluded because they are not deterministic. `gpu` is a constant string.
NONDETERMINISTIC = ("wall_s", "cpu_s")
CONSTANT = ("gpu",)


def meter_vector(m: Meter, manifest=None) -> dict:
    d = m.as_dict(manifest)
    return {k: v for k, v in d.items() if k not in NONDETERMINISTIC and k not in CONSTANT}


def run_player(manifest, probes):
    m = Meter()
    ts, th = run_ensemble(manifest, probes, DEFAULT_ENSEMBLE, meter=m)
    full = m.as_dict(manifest)
    det = {k: v for k, v in full.items() if k not in NONDETERMINISTIC and k not in CONSTANT}
    return {"transcript_hash": th,
            "meter_full_hash": hash_obj(full),
            "meter_hash": hash_obj(det),
            "ops_by_category_hash": hash_obj(det["ops_by_category"]),
            "ops": det["ops"]}


def rand_segment(rng, n_instr=SEGMENT_INSTRUCTIONS):
    return segment_from_instructions([rng.next_u32() for _ in range(n_instr * IW)])


def nop_segment(null_word, n_instr=SEGMENT_INSTRUCTIONS):
    return segment_from_instructions([null_word] * (n_instr * IW))


def manifest_of(*segs):
    """compose() takes (component_name, segment) pairs; names are local slot handles only."""
    named = [(f"c{i}", s) for i, s in enumerate(segs)]
    return compose(named, ENVELOPE)["manifest"]


def main():
    with open(REG_PATH, encoding="utf-8") as f:
        reg = json.load(f)
    probes = build_probes(DEFAULT_ENSEMBLE)
    seed = seed_from("proteus.t2.meter_floor.v0", reg["registry_id"])
    rng = SplitMix64(seed)

    out = {
        "schema_version": "proteus.meter_floor.v1",
        "purpose": "chance floor for the meter observable proposed by TODO T1; see T2",
        "registry_id": reg["registry_id"],
        "seed_derivation": "seed_from('proteus.t2.meter_floor.v0', registry_id)",
        "envelope": ENVELOPE, "segment_instructions": SEGMENT_INSTRUCTIONS,
        "excluded_from_meter": {"nondeterministic": list(NONDETERMINISTIC),
                                "constant": list(CONSTANT)},
    }

    # ---------------------------------------------------------------- PART 0
    det_ok, full_ok = 0, 0
    n_det = 40
    for _ in range(n_det):
        man = manifest_of(rand_segment(rng), rand_segment(rng))
        a, b = run_player(man, probes), run_player(man, probes)
        det_ok += (a["meter_hash"] == b["meter_hash"])
        full_ok += (a["meter_full_hash"] == b["meter_full_hash"])
    out["part0_determinism"] = {
        "players_tested": n_det,
        "deterministic_meter_reproduces": f"{det_ok}/{n_det}",
        "full_meter_including_timings_reproduces": f"{full_ok}/{n_det}",
        "gate": "PASS" if det_ok == n_det else "FAIL",
        "note": ("The second row is a NEGATIVE CONTROL. If the full meter also reproduced, "
                 "excluding wall_s/cpu_s would be unnecessary caution; a shortfall there is the "
                 "evidence that the exclusion is load-bearing."),
    }
    print(f"PART 0 determinism: deterministic {det_ok}/{n_det} | "
          f"with timings {full_ok}/{n_det}", flush=True)
    if det_ok != n_det:
        out["verdict"] = "METER_NOT_DETERMINISTIC_UNUSABLE"
        _write(out)
        return 2

    # ---------------------------------------------------------------- PART 1
    counts = {"transcript": [], "ops_by_category": [], "meter": []}
    for _ in range(N_POPULATIONS):
        pop = [run_player(manifest_of(rand_segment(rng)), probes) for _ in range(POP_SIZE)]
        counts["transcript"].append(len({p["transcript_hash"] for p in pop}))
        counts["ops_by_category"].append(len({p["ops_by_category_hash"] for p in pop}))
        counts["meter"].append(len({p["meter_hash"] for p in pop}))
    out["part1_population_structure_floor"] = {
        "populations_resampled": N_POPULATIONS, "population_size": POP_SIZE,
        "observed_in_closure_pass": {"transcript": 3, "ops_by_category": 37, "meter": 39},
        "null_distribution_of_distinct_classes": {
            k: {"min": min(v), "median": statistics.median(v), "mean": round(statistics.fmean(v), 2),
                "max": max(v)} for k, v in counts.items()},
        "reading": ("These are RANDOM segment players of the same shape. If the null median sits "
                    "at the observed value, then class richness is a property of arbitrary "
                    "programs under this observable, not a discovery about the population."),
    }
    for k, v in counts.items():
        print(f"PART 1 {k:<16} null classes min {min(v)} median "
              f"{statistics.median(v)} max {max(v)}", flush=True)

    # ---------------------------------------------------------------- PART 2
    conds = {"identity": 0, "size_floor": 0, "treatment": 0, "size_matched": 0,
             "order": 0, "partner_identity": 0, "independent": 0}
    ops_delta = {"size_floor": [], "treatment": []}
    alias_disagreements = 0
    for _ in range(N_PAIRS):
        A, B = rand_segment(rng), rand_segment(rng)
        Aother = rand_segment(rng)
        mA = run_player(manifest_of(A), probes)
        mA2 = run_player(manifest_of(A), probes)
        mAB = run_player(manifest_of(A, B), probes)
        mAo = run_player(manifest_of(Aother), probes)
        mBA = run_player(manifest_of(B, A), probes)
        Bother = rand_segment(rng)
        mABo = run_player(manifest_of(A, Bother), probes)

        pads = [run_player(manifest_of(A, nop_segment(w)), probes) for w in NOP_ALIASES]
        if len({p["meter_hash"] for p in pads}) > 1:
            alias_disagreements += 1
        mApad = pads[0]

        conds["identity"] += (mA["meter_hash"] != mA2["meter_hash"])
        conds["size_floor"] += (mA["meter_hash"] != mApad["meter_hash"])
        conds["treatment"] += (mA["meter_hash"] != mAB["meter_hash"])
        conds["size_matched"] += (mApad["meter_hash"] != mAB["meter_hash"])
        conds["order"] += (mAB["meter_hash"] != mBA["meter_hash"])
        conds["partner_identity"] += (mAB["meter_hash"] != mABo["meter_hash"])
        conds["independent"] += (mA["meter_hash"] != mAo["meter_hash"])
        ops_delta["size_floor"].append(mApad["ops"] - mA["ops"])
        ops_delta["treatment"].append(mAB["ops"] - mA["ops"])

    rates = {k: round(v / N_PAIRS, 4) for k, v in conds.items()}
    out["part2_discrimination_floor"] = {
        "pairs": N_PAIRS,
        "differs_rate": rates,
        "definitions": {
            "identity": "meter(A) vs meter(A) -- sanity, must be 0.0",
            "size_floor": "meter(A) vs meter(A + NOP padding) -- same behaviour, bigger program",
            "treatment": "meter(A) vs meter(A + B) -- what the experiment proposes to use",
            "size_matched": "meter(A + NOP padding) vs meter(A + B) -- B beyond its length",
            "order": "meter(A+B) vs meter(B+A) -- can the observable see ORDER at all? A "
                     "prerequisite for any A->B ordered-composition question",
            "partner_identity": "meter(A+B) vs meter(A+B') -- does it respond to WHICH partner, "
                                "or merely to a second component being present?",
            "independent": "meter(A) vs meter(A') unrelated, same size -- discrimination ceiling",
        },
        "ops_delta_median": {k: statistics.median(v) for k, v in ops_delta.items()},
        "nop_alias_disagreements": alias_disagreements,
        "alias_note": ("Padding was run under all three NOP aliases. A disagreement means the "
                       "padding acted as DATA, so the size floor is a lower bound for that pair."),
    }
    for k in ("identity", "size_floor", "treatment", "size_matched", "order",
              "partner_identity", "independent"):
        print(f"PART 2 {k:<14} differs rate {rates[k]:.4f}", flush=True)
    print(f"PART 2 nop-alias disagreements {alias_disagreements}/{N_PAIRS}", flush=True)

    # ---------------------------------------------------------------- verdict
    excess = round(rates["treatment"] - rates["size_floor"], 4)
    out["verdict_inputs"] = {
        "treatment_minus_size_floor": excess,
        "size_matched_rate": rates["size_matched"],
        "order_sensitive": rates["order"] > 0.0,
        "partner_sensitive": rates["partner_identity"] > 0.0,
    }
    if rates["identity"] != 0.0:
        v = "METER_NOT_DETERMINISTIC_UNUSABLE"
    elif rates["size_floor"] >= rates["treatment"]:
        v = "METER_COMPOSITION_RESPONSE_FULLY_EXPLAINED_BY_SIZE"
    elif rates["size_matched"] <= 0.05:
        v = "METER_CANNOT_SEE_B_BEYOND_ITS_LENGTH"
    else:
        v = "METER_DISCRIMINATES_BEYOND_SIZE"
    out["verdict"] = v
    out["what_this_is_not"] = (
        "No specimen was selected, scored, ranked or interpreted. Every rate is over an arbitrary "
        "random ensemble. A rate is a property of the OBSERVABLE, not a capability claim about "
        "any player, and nothing here says composition does or does not produce synergy.")
    _write(out)
    print(f"\nVERDICT {v}")
    return 0


def _write(out):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print(f"wrote {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
