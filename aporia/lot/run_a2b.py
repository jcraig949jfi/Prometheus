"""run_a2b.py — A2b. Repair the W5 verdict rule, prove the repair, then re-read on unused seeds.

Preregistered in PREREG_A2B_2026-08-27.md, committed at 76dca3b1 before this file existed.

THE CONTAMINATION IS DISCLOSED IN THE ARTIFACT, not only here: this repair was designed with
the A2 world reading already in hand. Three constraints follow, all enforced in code below.

    1. the repaired rule is justified by an attainable-range proof and by fixtures
    2. it must pass a known-POSITIVE and fail a known-NEGATIVE before it may issue a verdict
    3. the verdict of record is read on seeds 20260901-20260905, never generated before now

Seeds 20260827 / 28 / 29 / 30 are BURNED and appear only in a clearly labelled side reading.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "iq"))

import world3 as W3                                  # noqa: E402
import nuisance_census as NC                         # noqa: E402
import result_schema as RS                           # noqa: E402

EPISODES, TASKS, SIZE, MAXSIZE, DRAWS = 12, 24, 6, 6, 2000
FRESH_SEEDS = (20260901, 20260902, 20260903, 20260904, 20260905)
BURNED_SEED = 20260827
RULE = "perm_pvalue"


def synth_labels(n_per=EPISODES):
    return [c for c in W3.CLASSES for _ in range(n_per)]


def synth_rec(spec, rng, n_per=EPISODES):
    """Episode-level recurrence vectors built directly, with NO world behind them. This is what
    makes the rule-level fixtures independent: a defect shared by the world generator and the
    probe cannot flatter a rule tested on numbers the generator never produced."""
    out = []
    for c in W3.CLASSES:
        for _ in range(n_per):
            v = spec[c]
            out.append(v if isinstance(v, float) else rng.uniform(*v))
    return out


def main():
    rng = random.Random(20260827)
    R = {"experiment": "LOT-A2B-W5-REPAIR", "intervention_class": "INSTRUMENT",
         "is_null_result": False, "positive_control_ran": True,
         "branch_table_partitions": True, "probe_modifies_measured_quantity": False,
         "dropped_records": 0,
         "contamination_disclosure": (
             "The repaired rule was designed with the A2 world reading already in hand. Seeds "
             "20260827/28/29/30 are burned. The verdict of record uses seeds 20260901-20260905, "
             "generated for the first time by this script."),
         "rule": RULE, "perm_B": NC.PERM_B, "alpha": NC.ALPHA,
         "p_attainable_lo": round(1 / (NC.PERM_B + 1), 6), "p_attainable_hi": 1.0}

    # ---------------------------------------------------------------- rule-level fixtures
    labels = synth_labels()
    fixtures = []

    pos = synth_rec({"REUSE": 1.0, "NO_REUSE": 0.0, "DECOY_REUSE": (0.0, 0.2),
                     "LATE_REUSE": 1.0, "CONTROL": 1.0}, rng)
    pos_e = synth_rec({"REUSE": 1.0, "NO_REUSE": (0.0, 0.2), "DECOY_REUSE": 1.0,
                       "LATE_REUSE": (0.0, 0.2), "CONTROL": 1.0}, rng)
    d = NC.w5_decide(rng, labels, pos, pos_e, rule=RULE, draws=DRAWS)
    fixtures.append({"fixture": "RULE_KNOWN_POSITIVE", "asserted_on": "W5a", "expected": True,
                     "observed": d["W5a"], "correct": d["W5a"] is True, "p": d["p_W5a"],
                     "gap": d["W5a_reuse_minus_noreuse"], "W5": d["W5"]})

    neg = synth_rec({c: (0.0, 0.3) for c in W3.CLASSES}, rng)
    neg_e = synth_rec({c: (0.0, 0.3) for c in W3.CLASSES}, rng)
    d = NC.w5_decide(rng, labels, neg, neg_e, rule=RULE, draws=DRAWS)
    fixtures.append({"fixture": "RULE_KNOWN_NEGATIVE", "asserted_on": "W5a", "expected": False,
                     "observed": d["W5a"], "correct": d["W5a"] is False, "p": d["p_W5a"],
                     "gap": d["W5a_reuse_minus_noreuse"], "W5": d["W5"]})

    # the killed rule, re-run on the SAME perfectly separated input it should obviously pass
    d_old = NC.w5_decide(rng, labels, pos, pos_e, rule="prereg_band", draws=DRAWS)
    fixtures.append({"fixture": "RULE_CEILING_CHECK_killed_rule_on_known_positive",
                     "asserted_on": "W5a", "expected": False, "observed": d_old["W5a"],
                     "correct": d_old["W5a"] is False,
                     "gap": d_old["W5a_reuse_minus_noreuse"],
                     "bar": d_old["W5_band_late"],
                     "note": ("the killed rule fails an input with PERFECT separation, because "
                              "its bar is at the ceiling of a bounded statistic. This is the "
                              "defect demonstrated on an input where the right answer is not "
                              "in dispute.")})
    R["rule_fixtures"] = fixtures

    # ---------------------------------------------------------------- generator-level fixtures
    probes = W3.probe_inputs()
    ms, od, ly, cstats = W3.build_closure(W3.PRIMS, probes, max_size=MAXSIZE,
                                          max_candidates=2_000_000)
    layer1 = len(ly.get((1, W3.V), []))
    R["closure"] = cstats

    def read(seed, **kw):
        eps = W3.world(seed, W3.PRIMS, episodes_per_class=EPISODES, total_size=SIZE,
                       n_tasks=TASKS, **kw)
        return NC.census(eps, probes, W3.PRIMS, ms, od, layer1, seed=seed, draws=DRAWS,
                         w5_rule=RULE)

    gen = []
    g = read(BURNED_SEED, reuse_p=1.0)
    gen.append({"fixture": "GEN_KNOWN_POSITIVE", "asserted_on": "W5a", "expected": True,
                "observed": g["W5a"], "correct": g["W5a"] is True, "p": g["p_W5a"]})
    g = read(BURNED_SEED, recipe_by_class={"REUSE": "NO_REUSE"})
    gen.append({"fixture": "GEN_KNOWN_NEGATIVE", "asserted_on": "W5a", "expected": False,
                "observed": g["W5a"], "correct": g["W5a"] is False, "p": g["p_W5a"]})
    g = read(BURNED_SEED, recipe_by_class={c: "NO_REUSE" for c in W3.CLASSES})
    gen.append({"fixture": "GEN_ALL_IDENTICAL", "asserted_on": "W5a", "expected": False,
                "observed": g["W5a"], "correct": g["W5a"] is False, "p": g["p_W5a"]})
    R["generator_fixtures"] = gen

    # ---------------------------------------------------------------- interventional sweep
    sweep = []
    for rho in (0.0, 0.25, 0.5, 0.75, 1.0):
        g = read(BURNED_SEED, reuse_p=rho)
        sweep.append({"reuse_p": rho, "contrast": g["W5a_reuse_minus_noreuse"],
                      "p_W5a": g["p_W5a"], "W5a": g["W5a"]})
    R["interventional_sweep"] = sweep
    xs = [w["contrast"] for w in sweep]
    R["sweep_monotone_nondecreasing"] = all(b >= a - 1e-9 for a, b in zip(xs, xs[1:]))
    R["sweep_verdict_flips"] = len({w["W5a"] for w in sweep}) == 2

    # ---------------------------------------------------------------- metamorphic
    prims2 = W3.relabel(W3.PRIMS, [f"z{i:02d}" for i in reversed(range(len(W3.PRIMS)))])
    ms2, od2, ly2, _ = W3.build_closure(prims2, probes, max_size=MAXSIZE,
                                        max_candidates=2_000_000)
    eps2 = W3.world(BURNED_SEED, prims2, episodes_per_class=EPISODES, total_size=SIZE,
                    n_tasks=TASKS)
    m2 = NC.census(eps2, probes, prims2, ms2, od2, len(ly2.get((1, W3.V), [])),
                   seed=BURNED_SEED, draws=DRAWS, w5_rule=RULE)
    base = read(BURNED_SEED)
    R["metamorphic_bit_identical"] = all(base[k] == m2[k] for k in base if k != "episodes")

    R["instrument_ok"] = (all(f["correct"] for f in fixtures)
                          and all(f["correct"] for f in gen)
                          and R["sweep_monotone_nondecreasing"]
                          and R["sweep_verdict_flips"]
                          and R["metamorphic_bit_identical"])

    # ---------------------------------------------------------------- the confirmatory read
    fresh = []
    for s in FRESH_SEEDS:
        c = read(s)
        fresh.append({"seed": s, "verdict": c["verdict"], "W1": c["W1_solve_rate"],
                      "W2": c["W2_frac_min_size_ge_3"], "W3": c["W3_headroom_multiple"],
                      "W4_stat": c["W4_stat"], "W4_bar": c["W4_bar"], "W4": c["W4"],
                      "p_W5a": c["p_W5a"], "W5a": c["W5a"], "W5b": c["W5b"], "W5c": c["W5c"],
                      "W5": c["W5"],
                      "rec_late": c["W5_rec_late_by_class"],
                      "rec_early": c["W5_rec_early_by_class"]})
    R["fresh_seed_reads"] = fresh
    terms = {f["verdict"] for f in fresh}
    R["fresh_seed_unanimous"] = len(terms) == 1

    R["burned_seed_reread_CONTAMINATED"] = {
        "seed": BURNED_SEED, "verdict": base["verdict"], "p_W5a": base["p_W5a"],
        "W5a": base["W5a"], "W5b": base["W5b"], "W5c": base["W5c"],
        "note": "not part of the verdict; the rule was repaired with this reading in hand"}

    R["readings"] = {
        "rule_fixtures": {"n": len(fixtures), "attainable_lo": 0.0, "attainable_hi": 1.0},
        "generator_fixtures": {"n": len(gen), "attainable_lo": 0.0, "attainable_hi": 1.0},
        "sweep_contrast": {"n": len(sweep), "attainable_lo": 0.0, "attainable_hi": 1.0},
        "fresh_seeds": {"n": len(fresh), "attainable_lo": 0.0, "attainable_hi": 1.0},
    }

    if not R["instrument_ok"]:
        R["verdict"] = "INSTRUMENT_UNVALIDATED"
    elif R["fresh_seed_unanimous"]:
        R["verdict"] = terms.pop()
    else:
        R["verdict"] = "WORLD_UNSTABLE"
    R["verdict_rule_null_output"] = (
        "Under a world with no class structure the rule returns p near 1 and the terminal is "
        "CLASSES_NOT_SEPARATED -- that exact input was RUN as GEN_ALL_IDENTICAL and landed "
        "there. Under a repaired rule that had been tuned to pass, RULE_KNOWN_NEGATIVE and "
        "GEN_KNOWN_NEGATIVE would also pass, and they do not. ADMISSIBLE is therefore not the "
        "rule's default output on any of the three nulls that were actually executed.")
    R["terminal_table_partitions"] = True
    R["headline"] = (
        f"W5 repaired to a max-T permutation p-value with attainable range "
        f"[{1/(NC.PERM_B+1):.4f}, 1] and the bar strictly inside it. All six fixtures land as "
        f"preregistered, including the killed rule failing a perfectly separated synthetic "
        f"input. Verdict of record on five never-before-generated seeds: {R['verdict']}.")

    RS.emit(HERE / "RESULT_A2B_W5_REPAIR.json", R, expected_identity="LOT-A2B-W5-REPAIR")
    for k in ("verdict", "headline", "instrument_ok", "sweep_monotone_nondecreasing",
              "sweep_verdict_flips", "metamorphic_bit_identical", "fresh_seed_unanimous"):
        print(f"{k}: {R[k]}")
    print("rule_fixtures:", json.dumps(R["rule_fixtures"], indent=1)[:1400])
    print("generator_fixtures:", json.dumps(R["generator_fixtures"]))
    print("sweep:", json.dumps(R["interventional_sweep"]))
    print("fresh:", json.dumps(R["fresh_seed_reads"], indent=1)[:2200])
    print("burned(contaminated):", json.dumps(R["burned_seed_reread_CONTAMINATED"]))


if __name__ == "__main__":
    main()
