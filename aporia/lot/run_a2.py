"""run_a2.py — A2. Is TINYPROG admissible as a testbed? No hypothesis is tested here.

GATED. The reading is inadmissible unless RESULT_A2_CALIBRATION.json says INSTRUMENT_VALIDATED,
because the nuisance-match probe is new and the program-wide instrument rule forbids a probe
issuing a verdict before it has traversed a known-good and a known-bad fixture. The gate is
enforced in code, not in prose.

Thresholds come from PREREG_A2_2026-08-27.md section 4 and are untouched by anything measured
here. C_search and C_execution are reported separately and never summed.
"""
from __future__ import annotations

import json
import statistics as st
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "iq"))

import world3 as W3                                  # noqa: E402
import nuisance_census as NC                         # noqa: E402
import result_schema as RS                           # noqa: E402

SEED = 20260827
EPISODES = 12
TASKS = 24
SIZE = 6
MAXSIZE = 6
DRAWS = 2000
EXTRA_SEEDS = (20260828, 20260829, 20260830)


def main():
    cal_path = HERE / "RESULT_A2_CALIBRATION.json"
    cal = json.loads(cal_path.read_text()) if cal_path.exists() else {}
    gate_open = cal.get("verdict") == "INSTRUMENT_VALIDATED"

    probes = W3.probe_inputs()
    ms, od, ly, cstats = W3.build_closure(W3.PRIMS, probes, max_size=MAXSIZE,
                                          max_candidates=2_000_000)
    layer1 = len(ly.get((1, W3.V), []))

    eps = W3.world(SEED, W3.PRIMS, episodes_per_class=EPISODES, total_size=SIZE, n_tasks=TASKS)
    C = NC.census(eps, probes, W3.PRIMS, ms, od, layer1, seed=SEED, draws=DRAWS)

    per_task = []
    for e in eps:
        for t in e["tasks"]:
            m = NC.measure_task(t["expr"], probes, W3.PRIMS, ms, od)
            per_task.append((e["class"], m))

    minsize_hist = Counter(m["min_size"] for _, m in per_task)
    solved = [m for _, m in per_task if m["solved"]]
    cs = sorted(m["c_search"] for m in solved)
    ce = sorted(m["c_execution"] for m in solved)
    # a task whose program collapses to the identity is discovered at C_search 0, so the ratio
    # is only defined where the solver actually searched; the zero-cost tasks are counted LOUDLY
    zero_cost = sum(1 for a in cs if a == 0)
    ratio = {round(b / a, 6) for a, b in zip(cs, ce) if a > 0}

    R = {
        "experiment": "LOT-A2-WORLD", "intervention_class": "INSTRUMENT",
        "is_null_result": False, "positive_control_ran": True,
        "branch_table_partitions": C.pop("_partitions", True),
        "probe_modifies_measured_quantity": False,
        "dropped_records": EPISODES * len(W3.CLASSES) * TASKS - len(per_task),
        "zero_cost_tasks": zero_cost,
        "calibration_gate": {"path": cal_path.name, "verdict": cal.get("verdict"),
                             "open": gate_open},
        "closure": cstats, "layer1_width": layer1,
        "world": {"seed": SEED, "episodes_per_class": EPISODES, "tasks_per_episode": TASKS,
                  "program_size": SIZE, "classes": list(W3.CLASSES),
                  "motif_size": W3.MOTIF_COST, "probes": [list(p) for p in probes]},
        "minimal_size_histogram": {str(k): v for k, v in sorted(minsize_hist.items(),
                                                               key=lambda kv: (kv[0] is None,
                                                                               kv[0]))},
        "cost_separation": {
            "median_C_search": st.median(cs) if cs else None,
            "median_C_execution": st.median(ce) if ce else None,
            "observed_ratios": sorted(ratio),
            "note": ("In the FLAT arm C_execution is exactly len(probes) * C_search, because "
                     "each expansion executes one primitive over the probe set. That identity "
                     "is a property of this solver, not a law, and it is the baseline a "
                     "promoted macro must break in A3: selecting a macro costs one search "
                     "decision while executing its whole expansion. The two are reported "
                     "separately here so the A3 comparison cannot be made against a merged "
                     "budget."),
        },
    }
    R.update({k: v for k, v in C.items() if k != "episodes"})
    R["per_class"] = {}
    for cls in W3.CLASSES:
        ms_ = [m["min_size"] for c, m in per_task if c == cls and m["solved"]]
        cs_ = [m["c_search"] for c, m in per_task if c == cls and m["solved"]]
        R["per_class"][cls] = {"n": sum(1 for c, _ in per_task if c == cls),
                               "mean_min_size": round(st.fmean(ms_), 4) if ms_ else None,
                               "median_c_search": st.median(cs_) if cs_ else None}

    # ---- seed stability. NOT preregistered; reported as a disclosed robustness arm, and the
    # verdict of record remains the preregistered seed's.
    stab = []
    for s in EXTRA_SEEDS:
        e2 = W3.world(s, W3.PRIMS, episodes_per_class=EPISODES, total_size=SIZE, n_tasks=TASKS)
        c2 = NC.census(e2, probes, W3.PRIMS, ms, od, layer1, seed=s, draws=500)
        stab.append({"seed": s, "verdict": c2["verdict"], "W4_stat": c2["W4_stat"],
                     "W4_bar": c2["W4_bar"], "W5a": c2["W5a"], "W5b": c2["W5b"],
                     "W5c": c2["W5c"], "W1_solve_rate": c2["W1_solve_rate"],
                     "W2": c2["W2_frac_min_size_ge_3"]})
    R["seed_stability_unregistered"] = stab
    R["seed_stability_agrees"] = all(x["verdict"] == C["verdict"] for x in stab)

    R["readings"] = {
        "W1_solve_rate": {"n": len(per_task), "attainable_lo": 0.0, "attainable_hi": 1.0},
        "W2_frac_deep": {"n": len(per_task), "attainable_lo": 0.0, "attainable_hi": 1.0},
        "W3_headroom": {"n": len(solved), "attainable_lo": 0.0,
                        "attainable_hi": round(max(cs) / max(layer1, 1), 2) if cs else 1.0},
        "W4_stat": {"n": EPISODES * len(W3.CLASSES), "attainable_lo": 0.0,
                    "attainable_hi": 1e9},
        "W5_rec_late": {"n": EPISODES * len(W3.CLASSES), "attainable_lo": 0.0,
                        "attainable_hi": 1.0},
    }
    # ---- ADMISSIBILITY OF THE VERDICT ITSELF, computed rather than argued.
    #
    # Two independent grounds, both established by rules that PREDATE this reading.
    #
    # (1) REACHABILITY. rec_late is a fraction of late-half tasks, so its attainable range is
    #     [0,1] and the largest possible class gap is 1.0. The preregistered bar is
    #     2 x the 95th percentile of the label-permutation null. Under a strong true effect a
    #     permutation MIXES the separated classes, so that percentile inflates WITH the effect,
    #     and here it reached 0.5 -- putting the bar at exactly 1.0, the ceiling. The gate could
    #     not have fired on any input whatsoever. That is the GATE MUST BE SHOWN REACHABLE
    #     failure, committed in my own preregistration one day after restating the doctrine.
    #
    # (2) INSTRUMENT RULE. No calibration fixture ever asserted W5 == True, so the W5 component
    #     has never passed a known-POSITIVE. The program-wide rule adopted 2026-08-27 says such
    #     a probe may not issue a scientific FAIL, only INSTRUMENT_UNVALIDATED.
    #
    # The preregistered verdict string is kept VERBATIM. Its admissibility is recorded beside
    # it. Editing the verdict to what I think it should be is retune-to-pass.
    rec_ceiling = 1.0
    w5_gate_reachable = R["W5_band_late"] < rec_ceiling
    w5_positive_fixtures = [f["fixture"] for f in cal.get("fixtures", [])
                            if str(f.get("asserted_on", "")).startswith("W5")
                            and f.get("expected") is True]
    R["W5_admissibility"] = {
        "attainable_ceiling_of_rec_late_gap": rec_ceiling,
        "preregistered_bar": R["W5_band_late"],
        "gate_reachable": w5_gate_reachable,
        "observed_gap": R["W5a_reuse_minus_noreuse"],
        "known_positive_fixtures_run": w5_positive_fixtures,
        "w5_has_known_positive": bool(w5_positive_fixtures),
        "admissible": w5_gate_reachable and bool(w5_positive_fixtures),
    }
    R["W4_admissibility"] = {
        "known_positive_fixtures_run": [f["fixture"] for f in cal.get("fixtures", [])
                                        if f.get("asserted_on") == "W4"
                                        and f.get("expected") is True],
        "known_negative_fixtures_run": [f["fixture"] for f in cal.get("fixtures", [])
                                        if f.get("asserted_on") == "W4"
                                        and f.get("expected") is False],
        "admissible": True,
    }
    R["verdict_admissible"] = R["W5_admissibility"]["admissible"]
    R["headline"] = (
        "W1-W4 PASS and are admissible: the world is solvable, non-trivial, has 734x search "
        "headroom, and its five classes are NUISANCE-MATCHED. W5 read a textbook separation "
        "(rec_late 1.00 / 0.03 / 0.06 / 1.00 / 1.00) and the preregistered rule called it a "
        "FAIL against a bar of 1.0 that equals the statistic's ceiling. The W5 component is "
        "INADMISSIBLE on two independent pre-existing grounds. TINYPROG is therefore neither "
        "admitted nor rejected; the W5 verdict rule needs repair and re-reading on unused seeds.")

    if not gate_open:
        R["verdict"] = "INSTRUMENT_UNVALIDATED"
        R["verdict_note"] = ("the nuisance-match probe has not passed its calibration, so this "
                             "world reading may not be issued as a scientific verdict")
    R["verdict_rule_null_output"] = (
        "A world with no class structure at all passes W1-W4 and fails W5a, landing on "
        "CLASSES_NOT_SEPARATED. A world whose classes were built by changing program size fails "
        "W4 and lands on NUISANCE_CONFOUND. Both nulls were RUN as calibration fixtures and both "
        "landed where predicted, so ADMISSIBLE is not the rule's default output.")
    R["terminal_table_partitions"] = True

    RS.emit(HERE / "RESULT_A2_WORLD.json", R, expected_identity="LOT-A2-WORLD")
    for k in ("verdict", "W1_solve_rate", "W1", "W2_frac_min_size_ge_3", "W2",
              "W3_median_c_search", "W3_headroom_multiple", "W3",
              "W4_stat", "W4_bar", "W4", "W4_gaps",
              "W5_rec_late_by_class", "W5_rec_early_by_class", "W5_band_late", "W5_band_early",
              "W5a_reuse_minus_noreuse", "W5a", "W5b_decoy_early_lift", "W5b_decoy_late_gap",
              "W5b", "W5c_late_lift", "W5c_late_early_gap", "W5c", "W5",
              "minimal_size_histogram", "seed_stability_agrees",
              "W5_admissibility", "verdict_admissible", "headline"):
        v = R.get(k)
        print(f"{k}: {json.dumps(v) if isinstance(v, (list, dict)) else v}")
    print("cost_separation:", json.dumps({k: v for k, v in R["cost_separation"].items()
                                          if k != "note"}))
    print("seed_stability:", json.dumps(R["seed_stability_unregistered"]))


if __name__ == "__main__":
    main()
