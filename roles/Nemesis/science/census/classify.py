"""NEM-14 -- the HAND-READ classification, recorded as data.

The screen (floor_census.py) extracts evidence lines. It does NOT classify,
because the cheapest way to fake this census is to grep for "null" and call
every hit a floor. Every state below was assigned by reading the module and
its emitted output keys; the evidence that decided each one is in the row.

States are fixed in PREREGISTRATION_NEM14.md (commit 0548bde84):
    F3 explicit empirical/null floor   F2 analytically justified floor
    F1 implicit but unpublished        F0 no defensible baseline
    NA emits no headline number

KIND is the distinction this census discovered and the preregistration did
not anticipate. A floor-shaped number is not automatically a chance floor:

    CHANCE     what NOTHING scores -- a null draw, a permutation, a random
               arm, a degenerate responder. This is what the commission asked
               about.
    RELEVANCE  the smallest effect that would MATTER if real (Harmonia's
               relevance_floor, smd 0.2/0.5). A materiality threshold. It
               says nothing about what nothing scores.
    CHANNEL    a positive and/or cheat control proving the MEASUREMENT
               CHANNEL can see success and can catch a fraud, without a
               baseline for the headline metric itself.

Conflating RELEVANCE with CHANCE is precisely the error this seat exists to
catch, so the two are never merged in a count.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO))
from archaeon.workspace import assert_not_canonical, receipt  # noqa: E402

OUT = HERE / "classification.json"

# path -> (state, kind, headline metric, terminal?, evidence that decided it)
C = {
 # ---- F3: a computed null/baseline value emitted beside the headline ----
 "roles/Coeus/science/trace_defects.py": ("F3", "CHANCE", "F4 selection-trace effect vs matched noise", False,
   "emits null_mean/null_max/null_p95 and p_value_observed_ge_null; NULL_DRAWS=200; magnitude-matched noise null"),
 "roles/Arachne/science/emergence.py": ("F3", "CHANCE", "emergence/ARI statistics", False,
   "emits c_nulls, null_aris, null_min/mean/max; a 'controls' entry point runs instrument controls alone"),
 "roles/Arachne/science/branch_fitness.py": ("F3", "CHANCE", "child_greater rate over eligible branches", False,
   "MIN_ELIGIBLE=20 with an explicit INDETERMINATE branch; emits eligible and ties; null_discounted_nodes"),
 "roles/Arachne/science/specimen.py": ("F3", "CHANCE", "reconstructed lineage counts", False,
   "null_p per step; positive control computes the same function two ways"),
 "roles/Harmonia/science/se1_first_preregistered_experiment.py": ("F3", "CHANCE", "hill-climb effect d", False,
   "ARM_NULL_A/ARM_NULL_B known-null arms + ARM_SAMPLE random sampler; emits null_d, null_arms_quiet"),
 "roles/Harmonia/science/s1_known_null_campaign.py": ("F3", "CHANCE", "celebrated cells on a null grid", False,
   "ground truth null BY CONSTRUCTION; permutation test; emits null_grid_celebrated/comparisons"),
 "roles/Harmonia/science/s14_truthful_records_false_science.py": ("F3", "CHANCE", "false-positive science rate", False,
   "generator is NULL, both arms from one distribution; null_score()"),
 "roles/Harmonia/science/s17_prospective_fragility.py": ("F3", "CHANCE", "fragility ranking top-1", False,
   "four baselines scored on the same population: random, empirical base rate, n, CI width; emits random_top1"),
 "roles/Harmonia/science/s18_fossil_directed_selection.py": ("F3", "CHANCE", "policy-C selection yield", False,
   "A_random = uniform over unexecuted pairs, named as the strongest simple fossil baseline"),
 "roles/Harmonia/science/s7_transportability.py": ("F3", "CHANCE", "transported effect d", False,
   "emits baseline_d, baseline_sd, delta_vs_baseline"),
 "roles/Harmonia/science/d3_live_corpus_calibration.py": ("F3", "CHANCE", "D3 fire rate on the live corpus", False,
   "coin-flip null rng.random()<0.5; prints 30 fires / 77 eligible = 0.390 with the eligible count"),
 "roles/Talos/science/characterize_corpus.py": ("F3", "CHANNEL", "corpus duplication / characterisation", False,
   "planted-row positive control and a cheat control run on a synthetic shard BEFORE the real shards"),
 "roles/Talos/science/semantic_faithfulness.py": ("F3", "CHANNEL", "semantic faithfulness rate", False,
   "controls() runs first and ABORTS on failure: positive (planted docstring) and execution control"),
 "roles/Clymene/science/model_audit.py": ("F3", "CHANNEL", "model integrity pass rate", False,
   "INTEGRITY_CHANNEL_CHEAT: the channel must detect a deliberate corruption"),
 "roles/Clymene/science/weights_probe.py": ("F3", "CHANNEL", "weights reachability", False,
   "control: a known-open file must be 200 and a fabricated one must not; prints CONTROL PASS"),
 "roles/Hypatia/science/seam_contract_test.py": ("F3", "CHANNEL", "seam contract confirmed", False,
   "emits claim_confirmed + positive_control + cheat_control together; cheat is a smuggled dict payload"),
 "roles/Hermes/science/convergence/probe.py": ("F3", "CHANNEL", "convergence collision rate", False,
   "collides_with_a_control() with three named control kinds (non_failure, different_failure, same_symptom)"),

 "roles/Harmonia/science/s5_hidden_moderators.py": ("F3", "CHANCE", "sign-flip count across 36 cells", False,
   "the contrast ITSELF is hill-climbing vs RANDOM SAMPLING, so the chance arm is one of the two arms "
   "rather than a separate emitted key; inherited from SE-1b (d=0.60 vs random). Bonferroni threshold "
   "for the full grid is reported beside the descriptive count"),

 # ---- F2: a justified floor that is NOT a chance floor ----
 "roles/Harmonia/science/s6_selection_bias.py": ("F2", "RELEVANCE", "promotion rate under selection", True,
   "FLOOR=0.5 relevance floor; promoted() gates on p<alpha AND |d|>=floor; emits reject_below_floor"),
 "roles/Harmonia/science/s12_organism2_estimation.py": ("F2", "RELEVANCE", "organism-2 effect d", False,
   "FLOOR, ALPHA = 0.5, 0.05; true d=0.329 reported as BELOW the 0.5 floor"),
 "roles/Harmonia/science/s11_v6_redteam.py": ("F2", "RELEVANCE", "red-team survival", False,
   "relevance_floor smd 0.2 declared; no chance arm emitted"),
 "roles/Harmonia/science/s16_boundary_inventory.py": ("F2", "RELEVANCE", "boundary inventory counts", False,
   "relevance_floor smd 0.2; the module's own text asks what baseline/reference set applies"),
 "roles/Harmonia/science/s9_expressiveness.py": ("F2", "RELEVANCE", "expressiveness coverage", False,
   "relevance_floor smd 0.5; A4 crossover treatment-then-control ordering recorded"),
 "roles/Harmonia/science/c3size.py": ("F2", "ANALYTIC", "floor rate after aggregating repeats", False,
   "simulates whether aggregating 4 repeats restores the floor rate; analytic/simulated, not a null draw"),

 # ---- F1: the floor is computable from what is committed, but unpublished ----
 "roles/Harmonia/science/s8_does_c7_transport.py": ("F1", "NONE", "does C7 transport (effect d)", False,
   "FLOOR, ALPHA defined at module level but neither a chance arm nor a baseline value is emitted"),
 "roles/Harmonia/science/s10_second_organism.py": ("F1", "NONE", "second-organism effect", False,
   "seeded RNG throughout for simulation, but no baseline/null key in the emitted payload"),
 "roles/Harmonia/science/s3_player_classes_and_replay.py": ("F1", "NONE", "player-class effect", False,
   "notes loops 1-2 were null by construction; THIS loop emits no null arm of its own"),
 "roles/Harmonia/science/s4_interactions_and_truncation.py": ("F1", "NONE", "interaction / truncation effect", False,
   "seeded RNG for simulation only; observes that a surviving subset is not random, without a random arm"),
 "roles/Harmonia/science/s13_family_reconciliation.py": ("F1", "NONE", "family reconciliation outcome", False,
   "asks whether control relocates; no baseline emitted"),
 "roles/Harmonia/science/s15_fossilization_boundary.py": ("F1", "NONE", "fossilization boundary", False,
   "compares projections modulo random ids; no baseline emitted"),
 "roles/Harmonia/science/d3_dossier_adjudication.py": ("F1", "WITHDRAWN", "D3 fires / eligible", True,
   "prints 'Both D3 nulls were calibrated on I.I.D. draws. They do not apply here.' -- the null is WITHDRAWN "
   "in place and the fire count is still reported; honest, and it leaves the headline without a floor"),
 "roles/Hermes/science/convergence/signature.py": ("F1", "NONE", "signature collision behaviour", False,
   "names a 'null strategy: what you get if you hash everything verbatim' in prose; no value emitted"),
 "roles/Hermes/science/convergence/record.py": ("F1", "NONE", "convergence record counts", False,
   "no floor vocabulary anywhere in the module"),
 "roles/Polyhymnia/science/lincode_decoders.py": ("F1", "NONE", "decoder success rate", False,
   "make_random()/random_rows() build a RANDOM DECODER that would serve as a chance arm; it is not "
   "emitted as a baseline beside the headline"),
 "roles/Kairos/science/claim_lint.py": ("F1", "NONE", "lint findings by severity", False,
   "checks whether OTHER seats' packets carry null/controls/eligible_count; publishes no floor for its "
   "own finding counts. Conflict noted: this seat and Kairos are adjacent lanes"),

 # ---- F0: headline with no baseline published and none derivable without new work ----
 "roles/Harmonia/contracts/conformance_check.py": ("F0", "NONE", "four-state conformance verdict (DRIFT/UNREACHABLE/INCOMPLETE/OK)", True,
   "NO floor vocabulary anywhere in 276 lines. TERMINAL: D-22 and WORKING_CONTRACT s8 make every consumer "
   "run this before work and HALT on DRIFT or a wrong engine_instance_id. Nothing establishes the rate at "
   "which it would emit OK on an engine it has never seen"),
 "roles/Harmonia/science/s2_ablation_honesty.py": ("F0", "NONE", "ablation honesty", True,
   "NO floor vocabulary anywhere in 240 lines despite three terminal-vocabulary hits"),
}

# modules the screen found to emit no headline number: NA, recorded for the denominator
NA_REASON = "emits no headline number (enumeration, IO, schema, or a pure transform)"


def main() -> int:
    assert_not_canonical()
    screen = json.loads((HERE / "census_screen.json").read_text(encoding="utf-8"))
    rows = screen["rows"]
    numeric = [r["path"] for r in rows if r["emits_number"]]
    kw_pos = {r["path"] for r in rows if r["floor_hits"]}

    unclassified = [p for p in numeric if p not in C]
    extra = [p for p in C if p not in numeric]

    out = []
    for r in rows:
        p = r["path"]
        if p in C:
            st, kind, metric, terminal, ev = C[p]
        elif r["emits_number"]:
            st, kind, metric, terminal, ev = ("UNCLASSIFIED", "NONE", "?", False, "not reached in this pass")
        else:
            st, kind, metric, terminal, ev = ("NA", "NONE", "-", False, NA_REASON)
        out.append({"path": p, "seat": r["seat"], "state": st, "floor_kind": kind,
                    "headline_metric": metric, "terminal": terminal,
                    "keyword_positive": p in kw_pos, "evidence": ev})

    scoring = [r for r in out if r["state"] not in ("NA",)]
    by_state = {s: sum(1 for r in scoring if r["state"] == s) for s in ("F3", "F2", "F1", "F0", "UNCLASSIFIED")}
    by_kind = {k: sum(1 for r in scoring if r["floor_kind"] == k) for k in
               ("CHANCE", "RELEVANCE", "CHANNEL", "ANALYTIC", "WITHDRAWN", "NONE")}

    f0f1 = by_state["F0"] + by_state["F1"]
    q1 = f0f1 / len(scoring)
    kw_scoring = [r for r in scoring if r["keyword_positive"]]
    kw_good = [r for r in kw_scoring if r["state"] in ("F2", "F3")]
    q2 = len(kw_good) / len(kw_scoring) if kw_scoring else 0.0
    terminal_low = [r for r in scoring if r["terminal"] and r["state"] in ("F0", "F1")]

    payload = {
        "census": "NEM-14", "workspace": receipt(),
        "tier1_total": len(rows), "scoring_instruments": len(scoring),
        "na": len(out) - len(scoring),
        "by_state": by_state, "by_floor_kind": by_kind,
        "chance_floor_count": by_kind["CHANCE"],
        "Q1_f0_plus_f1_fraction": round(q1, 4),
        "Q1_verdict": "HELD" if q1 >= 0.50 else "LOST",
        "Q2_keyword_positive_reaching_F2_F3": round(q2, 4),
        "Q2_verdict": "HELD" if q2 < 0.60 else "LOST",
        "Q3_terminal_instruments_at_F0_F1": [r["path"] for r in terminal_low],
        "Q3_verdict": "HELD" if terminal_low else "LOST",
        "audit_the_auditor": screen["audit_the_auditor"],
        "unclassified": unclassified, "classified_but_not_numeric": extra,
        "rows": out,
    }
    with OUT.open("w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2)
        fh.flush()

    for k in ("scoring_instruments", "na", "by_state", "by_floor_kind",
              "Q1_f0_plus_f1_fraction", "Q1_verdict",
              "Q2_keyword_positive_reaching_F2_F3", "Q2_verdict", "Q3_verdict"):
        print("{:42s} {}".format(k, payload[k]))
    print("Q3 terminal at F0/F1:", payload["Q3_terminal_instruments_at_F0_F1"])
    print("unclassified numeric:", unclassified or "none")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
