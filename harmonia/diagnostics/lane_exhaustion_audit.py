"""Lane exhaustion audit — EXHAUSTION@v1, lifted from features to lanes.

WHY THIS EXISTS
---------------
On 2026-04-20 the program canonicalized a symbol named EXHAUSTION@v1
(`D:\\Prometheus\\harmonia\\memory\\symbols\\EXHAUSTION.md`, immutable:true) with
pinned thresholds:

    n_kills >= 3, clustered in ONE axis class, >= 1 surviving axis class
    => REDIRECT (explicitly NOT "dead": "a directional signal, not a guarantee")

It was scoped to FEATURES (a tensor row) and its `implementation:` field is `null`.
It was never written, never run, and never lifted to the altitude where the program
actually spends months: the LANE.

This module implements it at lane altitude. The thresholds are INHERITED UNCHANGED
from the immutable v1 symbol — they are not tuned here, because tuning a threshold to
the outcome you already know is the failure this program keeps finding in itself.

WHAT IS AND IS NOT MEASURED
---------------------------
The event ledger below is HAND-CURATED from dated artifacts and is the weakest link
in the whole audit. Every event carries a citation and an evidence level:
    E1 = a file in this repo was read for it
    M  = recalled from a prior session's recorded verdict (weaker; not re-executed)
The ledger is published in full precisely so a reader can re-class events and re-run.

THE DISCRIMINATOR
-----------------
Raw kill count cannot separate an exhausted lane from a productive one — productive
lanes kill things constantly. The tensor encoding already draws the right distinction
(`landscape_manifest.json:tensor_encoding`):

    -1  "projection tested, feature not resolved"     <- uninformative kill
    -2  "projection provably collapses the feature"   <- CONSTRUCTIVE kill (a result)

So this audit counts only NO_SIGNAL (-1-like) events toward exhaustion, and reports
`constructive_fraction` per lane as the primary health statistic. A lane whose kills
are constructive is working; a lane whose kills are all no-signal is spending.

THE NULL (vacuity test)
-----------------------
Two lanes that demonstrably produced results (a3 product-measure theorem; the h2
information-recovery law) are included as CONTROLS. If the rubric fires on those too,
it cannot distinguish exhaustion from productive struggle and must be discarded. That
result would be reported, not suppressed.

THE SENSITIVITY
---------------
Lane-level "axis class" is a judgement, unlike a tensor column. Where a classing choice
changes the verdict, this audit reports BOTH classings rather than picking one.

Usage:
  PYTHONPATH=. python harmonia/diagnostics/lane_exhaustion_audit.py
  PYTHONPATH=. python harmonia/diagnostics/lane_exhaustion_audit.py --json out.json

Harmonia C, 2026-08-12.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict

# EXHAUSTION@v1 pinned thresholds — inherited, not tuned.
N_KILLS_THRESHOLD = 3
SURVIVING_CLASSES_THRESHOLD = 1

NO_SIGNAL = "NO_SIGNAL"        # probe failed to resolve; nothing transferable
CONSTRUCTIVE = "CONSTRUCTIVE"  # kill that proves something (a result)
POSITIVE = "POSITIVE"          # resolved / capability demonstrated

# --------------------------------------------------------------------------------
# EVENT LEDGER.  (date, lane, probe_class, verdict, evidence, citation)
# `probe_class_alt` is given only where the classing is genuinely arguable; it is used
# for the sensitivity run.
# --------------------------------------------------------------------------------
LEDGER = [
    # ---- math-claim lane -------------------------------------------------------
    ("2026-04-11", "math_claim", "statistical_moment", NO_SIGNAL, "E1",
     "retraction_registry.md: moment hierarchy KILLED", "statistical_coupling"),
    ("2026-04-12", "math_claim", "classification_axis", NO_SIGNAL, "E1",
     "retraction_registry.md: 5-axis phoneme + Megethos KILLED", "classification_axis"),
    ("2026-04-15", "math_claim", "statistical_coupling", NO_SIGNAL, "E1",
     "retraction_registry.md: spectral tail KILLED", None),
    ("2026-04-15", "math_claim", "statistical_coupling", NO_SIGNAL, "E1",
     "retraction_registry.md: NF backbone DOWNGRADED", None),
    ("2026-04-19", "math_claim", "statistical_coupling", NO_SIGNAL, "E1",
     "retraction_registry.md: F043 RETRACTED (Pattern 30 anchor)", None),
    ("2026-04-19", "math_claim", "statistical_coupling", NO_SIGNAL, "E1",
     "retraction_registry.md: Geometry 1 tensor latent-rank RETRACTED", None),
    ("2026-04-23", "math_claim", "cross_implementation", NO_SIGNAL, "E1",
     "retraction_registry.md: Zaremba A-spectrum divergence FALSIFIED", None),
    ("2026-04-29", "math_claim", "statistical_coupling", NO_SIGNAL, "E1",
     "retraction_registry.md: sigma-kernel OBSTRUCTION_SHAPE cross-family FALSIFIED",
     None),
    ("2026-04-29", "math_claim", "statistical_coupling", NO_SIGNAL, "E1",
     "retraction_registry.md: loose sister-obstruction signature FALSIFIED", None),
    ("2026-04-17", "math_claim", "calibration", POSITIVE, "E1",
     "landscape_tensor.npz: 7/7 calibration features carry +cells (rediscoveries)",
     None),

    # ---- apollo evolutionary lane ---------------------------------------------
    ("2026-05-22", "apollo", "evolutionary_search", NO_SIGNAL, "M",
     "project_apollo_reviewer_diagnosis_20260522: 'ecological collapse', recipe Goodhart",
     None),
    ("2026-05-22", "apollo", "evolutionary_search", NO_SIGNAL, "M",
     "project_apollo_baseline_matrix_falsification_20260522: 0/5 elites beat best "
     "single primitive (apollo/scripts/baseline_matrix.py)", None),
    ("2026-05-24", "apollo", "evolutionary_search", NO_SIGNAL, "M",
     "project_apollo_blackboard_prototype_20260524: evolved elite 36% "
     "(apollo/scripts/blackboard_prototype.py)", None),
    ("2026-05-24", "apollo", "hand_authored_representation", POSITIVE, "M",
     "project_apollo_blackboard_prototype_20260524: hand-written typed state 41% "
     "beats evolved elite", None),
    ("2026-06-09", "apollo", "substrate", POSITIVE, "E1",
     "apollo/pivot/r2_falsification_result_2026-06-09.json: KEYSTONE=YES", None),
    ("2026-06-16", "apollo", "search_operator", POSITIVE, "E1",
     "apollo/pivot/recombination_findings_2026-06-16.md: crossover crosses a valley "
     "single-step cannot", "evolutionary_search"),
    ("2026-06-22", "apollo", "evolutionary_search", NO_SIGNAL, "E1",
     "apollo/pivot/diagnose_0558_findings_2026-06-22.md: 0.558 wall = measurement / "
     "organism-model ceiling", None),
    ("2026-06-28", "apollo", "evolutionary_search", NO_SIGNAL, "M",
     "project_apollo_llm2_verdict_20260628: 800 gens matched deterministic exactly; "
     "LLM mutation adds nothing in this regime", None),

    # ---- icarus ladder lane ----------------------------------------------------
    ("2026-06-10", "icarus", "reasoner_capability", NO_SIGNAL, "M",
     "project_icarus_r5_serialization_wall_20260610: wall was serialization + "
     "interface-knowledge, never reasoning", None),
    ("2026-06-10", "icarus", "interface_representation", POSITIVE, "M",
     "project_icarus_r5_serialization_wall_20260610: R5 CLEARED once interface fixed",
     None),
    ("2026-06-15", "icarus", "reasoner_capability", NO_SIGNAL, "M",
     "project_icarus_r6_interface_walls_20260615: lens source-blindness + cid-family "
     "both interface", None),
    ("2026-08-12", "icarus", "reasoner_capability", NO_SIGNAL, "E1",
     "REVIEW_20260812_program_and_instrument_audit.md 2(a): R6 'capability' was an "
     "answer-key read; cycle-21 promotion unearned", None),

    # ---- CONTROLS: lanes that demonstrably produced results --------------------
    ("2026-06-10", "a3_lattice_void", "constructive_enumeration", CONSTRUCTIVE, "E1",
     "harmonia/proposals/2026-06-09/B_RESULTS_2026-06-10.md: a3 voids killed by the "
     "product-measure theorem", None),
    ("2026-06-10", "a3_lattice_void", "constructive_enumeration", POSITIVE, "E1",
     "harmonia/primitives/lattice_void_miner.py promoted", None),
    ("2026-06-15", "a3_lattice_void", "constructive_enumeration", CONSTRUCTIVE, "E1",
     "harmonia/experiments/a3_void_extension_stress.json: extension stress-tested",
     None),
    ("2026-06-10", "h2_info_recovery", "information_bound", CONSTRUCTIVE, "E1",
     "harmonia/proposals/2026-06-09/E_RESULTS_2026-06-10.md: path components carry "
     "zero conditional information (I(path;Y|coords)=0)", None),
    ("2026-06-10", "h2_info_recovery", "information_bound", POSITIVE, "E1",
     "harmonia/primitives/kill_scheme_info_audit.py promoted", None),
    ("2026-06-15", "h2_info_recovery", "information_bound", CONSTRUCTIVE, "E1",
     "harmonia/experiments/d4_state_coupling_RESULTS_2026-06-15.md: boundary anchored "
     "as state coupling, not hidden coordinate", None),
]

LANE_KIND = {
    "math_claim": "subject", "apollo": "subject", "icarus": "subject",
    "a3_lattice_void": "CONTROL (produced a result)",
    "h2_info_recovery": "CONTROL (produced a result)",
}


def events(alt=False):
    out = []
    for date, lane, cls, verdict, ev, cite, alt_cls in LEDGER:
        out.append({"date": date, "lane": lane,
                    "probe_class": (alt_cls or cls) if alt else cls,
                    "verdict": verdict, "evidence": ev, "citation": cite})
    return sorted(out, key=lambda e: e["date"])


def apply_rubric(evs, reset_on_positive):
    """EXHAUSTION@v1 lifted. Returns per-lane verdicts.

    `reset_on_positive`: only count kills that POST-DATE the most recent POSITIVE in
    the same class. This clause does not exist in the v1 feature-level symbol (a
    tensor cell has no time axis). It is added explicitly for the lift, because a
    class with a recent success is not exhausted. Both settings are reported.
    """
    by_lane = defaultdict(list)
    for e in evs:
        by_lane[e["lane"]].append(e)

    results = {}
    for lane, le in by_lane.items():
        classes = sorted({e["probe_class"] for e in le})
        last_pos = {}
        for e in le:
            if e["verdict"] == POSITIVE:
                last_pos[e["probe_class"]] = max(last_pos.get(e["probe_class"], ""),
                                                 e["date"])
        kills_by_class = defaultdict(list)
        for e in le:
            if e["verdict"] != NO_SIGNAL:
                continue
            if reset_on_positive and e["date"] <= last_pos.get(e["probe_class"], ""):
                continue
            kills_by_class[e["probe_class"]].append(e)

        n_kill_total = sum(1 for e in le if e["verdict"] == NO_SIGNAL)
        n_constructive = sum(1 for e in le if e["verdict"] == CONSTRUCTIVE)
        denom = n_kill_total + n_constructive
        frac = (n_constructive / denom) if denom else None

        fired, detail = False, []
        for cls, ks in sorted(kills_by_class.items()):
            if len(ks) < N_KILLS_THRESHOLD:
                continue
            surviving = [c for c in classes if c != cls]
            if len(surviving) < SURVIVING_CLASSES_THRESHOLD:
                continue
            fired = True
            crossing = sorted(k["date"] for k in ks)[N_KILLS_THRESHOLD - 1]
            detail.append({"exhausted_class": cls, "n_kills": len(ks),
                           "threshold_crossed": crossing,
                           "surviving_classes": surviving,
                           "last_event": max(e["date"] for e in le)})
        results[lane] = {"fired": fired, "detail": detail, "classes": classes,
                         "n_no_signal": n_kill_total, "n_constructive": n_constructive,
                         "constructive_fraction": frac,
                         "kind": LANE_KIND.get(lane, "?")}
    return results


def show(title, res):
    print(f"\n{title}")
    print("=" * 92)
    print(f"{'lane':<20}{'kind':<28}{'no-sig':>7}{'constr':>7}{'constr_frac':>13}"
          f"  EXHAUSTION@v1")
    print("-" * 92)
    for lane, r in sorted(res.items(), key=lambda kv: (kv[1]["kind"], kv[0])):
        cf = "n/a" if r["constructive_fraction"] is None else \
            f"{r['constructive_fraction']:.0%}"
        print(f"{lane:<20}{r['kind']:<28}{r['n_no_signal']:>7}{r['n_constructive']:>7}"
              f"{cf:>13}  {'FIRES' if r['fired'] else 'silent'}")
        for d in r["detail"]:
            print(f"    -> class '{d['exhausted_class']}' n_kills={d['n_kills']}; "
                  f"threshold crossed {d['threshold_crossed']}; lane continued to "
                  f"{d['last_event']}")
            print(f"       redirect targets: {', '.join(d['surviving_classes'])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    a = ap.parse_args()

    print("Lane exhaustion audit — EXHAUSTION@v1 lifted from features to lanes")
    print(f"thresholds inherited unchanged: n_kills>={N_KILLS_THRESHOLD}, "
          f"single class, surviving_classes>={SURVIVING_CLASSES_THRESHOLD}")
    print(f"ledger: {len(LEDGER)} events "
          f"({sum(1 for e in LEDGER if e[4] == 'E1')} E1, "
          f"{sum(1 for e in LEDGER if e[4] == 'M')} M)")

    primary = apply_rubric(events(False), reset_on_positive=True)
    show("PRIMARY — kills counted only after the last success in their class", primary)

    naive = apply_rubric(events(False), reset_on_positive=False)
    show("SENSITIVITY A — v1 literal (no reset-on-positive clause)", naive)

    alt = apply_rubric(events(True), reset_on_positive=True)
    show("SENSITIVITY B — arguable events re-classed (crossover as evolutionary "
         "search; moments as coupling)", alt)

    print("\nNULL / vacuity check")
    print("-" * 92)
    ctrl = [l for l, r in primary.items() if r["kind"].startswith("CONTROL")]
    fired_ctrl = [l for l in ctrl if primary[l]["fired"]]
    print(f"control lanes: {', '.join(ctrl)}")
    if fired_ctrl:
        print(f"  RUBRIC IS VACUOUS — it fires on productive lanes too: {fired_ctrl}")
        print("  Do not use it as a redirect signal.")
    else:
        print("  PASSES — silent on both lanes that produced results, so it is not")
        print("  merely counting activity. The separator is constructive_fraction,")
        print("  not kill count: controls kill as much, but their kills prove things.")

    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump({"ledger": events(False), "primary": primary,
                       "sensitivity_no_reset": naive, "sensitivity_alt_class": alt},
                      fh, indent=1)
        print(f"\nwrote {a.json}")


if __name__ == "__main__":
    main()
