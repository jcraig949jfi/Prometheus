"""Tests for QR-1.2.0 / AF-1.1.0 / EX-1.0.0 / FP-1.0.0 (2026-09-18, HARM-01/02/04/05..10/28/29/30/34).

Every refusal is proved to FIRE on the defect and to be SILENT on a clean case.
Run from the repo root:  python -m pytest roles/Harmonia/qualification/h0h5/tests -q
"""
from __future__ import annotations

import json
import math
import os
import random
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
H0H5 = os.path.dirname(HERE)
ROOT = os.path.abspath(os.path.join(H0H5, "..", "..", "..", ".."))
sys.path.insert(0, H0H5)

import qualification_rules as q          # noqa: E402
import adversarial_fixtures as af        # noqa: E402
import exchangeability as ex             # noqa: E402
import floor_precheck as fp              # noqa: E402

DOSSIER = os.path.join(ROOT, "archaeon", "docs", "h0h5", "D3_LIVE_DOSSIER_2026-09-10.json")
C3_2 = os.path.join(ROOT, "archaeon", "docs", "h0h5", "C3_2_READOUT.json")


def _plan(**kw):
    base = dict(lane="H0", plan_version="t", unit_definition="paired seed x task_block",
                n_blocks=12, assigned_tasks_per_block=8, denominator_rule="all_assigned_tasks",
                exclusion_rule="identical_across_arms", retry_rule="identical_across_arms",
                paired=True, primary_contrasts=["G", "I"], practical_threshold=0.05,
                threshold_status="PROPOSED", uncertainty_procedure="paired t + Bonferroni",
                multiplicity="BONFERRONI", pilot_task_ids=(1, 2), confirmation_task_ids=(3, 4))
    base.update(kw)
    return q.LanePlan(**base)


# ------------------------------------------------------------ versions

def test_versions():
    assert q.RULES_VERSION == "QR-1.2.1"
    assert af.FIXTURES_VERSION == "AF-1.1.0"
    assert ex.EX_VERSION == "EX-1.0.0"
    assert fp.FP_VERSION == "FP-1.0.0"


# -------------------------------------------------- HARM-02: exchangeability

def test_cuts_are_band_derived_not_chosen():
    lo, hi = ex.band_derived_cuts(3.0)
    assert abs(lo - ex.CUT_SUSPECT) < 1e-3 and abs(hi - ex.CUT_VIOLATED) < 1e-3
    assert abs(1 / (1 - ex.CUT_SUSPECT ** 2) - 1.5) < 0.01
    assert abs(1 / (1 - ex.CUT_VIOLATED ** 2) - 3.0) < 0.02


@pytest.mark.skipif(not os.path.exists(DOSSIER), reason="live dossier not present")
def test_live_dossier_reproduces_12_5_23():
    out = ex.classify_dossier(DOSSIER)
    assert out["n_regions"] == 40
    assert out["counts"][ex.EXCHANGEABLE] == 12
    assert out["counts"][ex.SUSPECT] == 5
    assert out["counts"][ex.VIOLATED] == 23
    assert out["counts"][ex.INDETERMINATE] == 0


def test_exchangeability_silent_on_clean_and_fires_on_trend():
    rng = random.Random(1)
    seqs = list(range(10, 130, 10))
    assert ex.diagnose(seqs, [rng.gauss(0, 1) for _ in seqs]).label in (ex.EXCHANGEABLE, ex.SUSPECT)
    assert ex.diagnose(seqs, [0.01 * s for s in seqs]).label == ex.VIOLATED
    assert ex.diagnose([1, 2], [0.1, 0.2]).label == ex.INDETERMINATE
    assert ex.diagnose(seqs, [0.5] * len(seqs)).label == ex.INDETERMINATE


# ----------------------------------------------- HARM-34: no relabelling

def test_diagnostic_cannot_become_confirmatory_after_data_read():
    diag = _plan(purpose="DIAGNOSTIC", n_blocks=4)      # 4 blocks: fine for a diagnostic
    frozen = q.freeze_plan(diag, "2026-09-18")
    q.validate_plan(diag, frozen=frozen, data_opened=True)   # still diagnostic: allowed
    relabelled = _plan(purpose="CONFIRMATORY", n_blocks=12)
    with pytest.raises(q.PlanRefused, match="relabelled CONFIRMATORY"):
        q.validate_plan(relabelled, frozen=frozen, data_opened=True)
    # before the data is opened, moving to confirmatory is a plan change, not selection
    q.validate_plan(relabelled, frozen=frozen, data_opened=False)
    # a plan frozen CONFIRMATORY stays valid after its data is opened
    conf = _plan(purpose="CONFIRMATORY")
    q.validate_plan(conf, frozen=q.freeze_plan(conf), data_opened=True)


def test_validate_plan_without_frozen_is_qr_1_1_0():
    assert "unit_is_paired_seed_x_task_block" in q.validate_plan(_plan())
    with pytest.raises(q.PlanRefused, match="INELIGIBLE by HA-1.6"):
        q.validate_plan(_plan(n_blocks=4))


# ------------------------------------------ HARM-30: shared-arm correlation

def test_shared_arm_correlation_is_half_for_any_rho():
    for rho in (0.0, 0.3, 0.7):
        assert abs(q.shared_arm_correlation_exchangeable(q.C_TRANSPORT, q.C_G, rho) - 0.5) < 1e-12
        assert abs(q.shared_arm_correlation_exchangeable(q.C_G, q.C_I, rho)) < 1e-12


def test_paired_contrasts_shared_arm_reports_correlation():
    rng = random.Random(3)
    blocks = []
    for _ in range(12):
        b = rng.uniform(0.2, 0.5)
        blocks.append({"S00": b, "S10": b + 0.1 + rng.gauss(0, .02), "S01": b + rng.gauss(0, .02),
                       "S11": b + 0.15 + rng.gauss(0, .02)})
    out = q.paired_contrasts_shared_arm(blocks, {"G": q.C_G, "transport": q.C_TRANSPORT})
    assert set(out["estimates"]) == {"G", "transport"}
    c = out["induced_correlation"]["G|transport"]
    assert -1.0 <= c <= 1.0 and c == c
    assert out["estimates"]["G"].alpha_used == 0.025      # Bonferroni over the two


# --------------------------------------------- HARM-01: payload identity

def test_cell_payload_refusals_and_alias():
    plan = {"cells": {"S00": {"payload_hash": "a"}, "S10": {"payload_hash": "b"},
                      "S01": {"payload_hash": "c"}, "S11": {"payload_hash": "d"}},
            "aliases": {"fresh": "S00"}}
    rec = q.validate_cell_payloads(plan)
    assert rec["distinct_payloads"] == 4 and rec["baselines_under_two_labels"] == [("fresh", "S00")]
    plan["cells"]["fresh"] = {"payload_hash": "a"}          # the defect: alias promoted to a cell
    with pytest.raises(q.PlanRefused, match="one payload hash under two cell labels"):
        q.validate_cell_payloads(plan)
    # Charon A1: identical content, different hashes
    plan2 = {"cells": {"S00": {"payload_hash": "x", "declared_payload": {"t": 0}},
                       "fresh": {"payload_hash": "y", "declared_payload": {"t": 0}}}}
    with pytest.raises(q.PlanRefused, match="identical declared payload"):
        q.validate_cell_payloads(plan2)
    with pytest.raises(q.PlanRefused, match="names no cell"):
        q.validate_cell_payloads({"cells": {"S00": {"payload_hash": "a"}}, "aliases": {"fresh": "S99"}})


def test_h0_analysis_plan_file_is_consistent():
    with open(os.path.join(H0H5, "h0_analysis_plan.json"), encoding="ascii") as f:
        plan = json.load(f)
    rec = q.validate_cell_payloads(plan)
    assert rec["distinct_payloads"] == 4 and len(plan["cells"]) == 4
    assert plan["aliases"] == {"fresh": "S00", "random_pack": "S10"}
    assert plan["shared_arm_correlation"]["exchangeable_equal_variance_reference"]["G|transport"] == 0.5


# ------------------------------------------ HARM-28: replay attestation

def test_replay_is_attestation_not_replicate():
    rows = [{"spec_hash": "h1", "output_digest": "o1"}, {"spec_hash": "h1", "output_digest": "o1"},
            {"spec_hash": "h2", "output_digest": "o2"}]
    att = q.replay_attestation(rows)
    assert att == [{"payload_hash": "h1", "n_rows": 2, "n_distinct_outputs": 1,
                    "attests_determinism": True, "counts_as_units": 1}]
    with pytest.raises(q.PlanRefused, match="replay rows offered as replicates"):
        q.refuse_replay_as_replicate(rows)
    assert q.refuse_replay_as_replicate(rows[1:]) == 2
    bad = [{"spec_hash": "h1", "output_digest": "o1"}, {"spec_hash": "h1", "output_digest": "o9"}]
    assert q.replay_attestation(bad)[0]["attests_determinism"] is False


# ------------------------------------------------ HARM-29: floor precheck

def test_floor_precheck_refuses_floor_and_passes_clean():
    with pytest.raises(fp.CorpusRefused, match="p_mode 1.000"):
        fp.floor_precheck([0.0] * 20, 0.0, 1.0)
    rec = fp.floor_precheck([0.1 * (i % 9 + 1) for i in range(90)], 0.0, 1.0)
    assert rec["label"] == "PASS" and rec["non_degenerate_fraction_f"] == 1.0
    rec = fp.floor_precheck([0.0, 0.0, 0.3, 0.4, 0.5, 0.6], 0.0, 1.0)
    assert rec["n_degenerate"] == 2 and abs(rec["non_degenerate_fraction_f"] - 4 / 6) < 1e-12
    assert rec["corpus_size_for_120_nondegenerate"] == 180


@pytest.mark.skipif(not os.path.exists(C3_2), reason="C3-2 readout not present")
def test_floor_precheck_reproduces_c3_2_f_zero():
    rows = fp.c3_2_acq_rows(C3_2)
    assert len(rows) == 120
    with pytest.raises(fp.CorpusRefused) as e:
        fp.floor_precheck([r["mean"] for r in rows], 0.0, 1.0, [r["accuracy_by_sample"] for r in rows])
    assert "f 0.000" in str(e.value) and "support 1" in str(e.value)


# -------------------------------------------------- HARM-04: AF-1.1.0

def test_battery_1_1_0_all_pass_including_controls():
    res = af.run_battery_1_1_0()
    names = [r["fixture"] for r in res]
    for f in ("F7_degenerate_replicate", "F8_structural_floor", "F9_non_exchangeable_rows"):
        assert f in names and f.split("_")[0] + "_control" in " ".join(names)
    assert all(r["pass"] for r in res), [r for r in res if not r["pass"]]
    assert sum(1 for r in res if r["defect_present"]) == 8      # F1-F5 + F7-F9
    assert sum(1 for r in res if not r["defect_present"]) == 4  # F4, F7, F8, F9 controls


# ------------------------------------------- HARM-05..10: lane gates

def test_every_lane_gate_names_its_quantity_range_and_eligibility():
    for lane in ("H0", "H1", "H2", "H3", "H4", "H5"):
        g = q.lane_gate(lane)
        for gate in (g.beta, g.one_point_zero):
            assert gate.promised_quantity in q.THREE_QUANTITIES
            assert gate.attainable_range == (-1.0, 1.0)
            assert gate.min_blocks == 6
            assert gate.eligibility(5)["label"] == "NOTHING_COULD_FIRE"
            assert gate.eligibility(6)["label"] == "ELIGIBLE"
            assert len(gate.primary_contrasts) == 1 or gate.multiplicity == "BONFERRONI"
        assert g.beta.promised_quantity == q.PRECISION and g.one_point_zero.promised_quantity == q.POWER
    with pytest.raises(q.PlanRefused):
        q.lane_gate("H6")


def test_h2_keeps_three_results_separate():
    g = q.lane_gate("H2")
    assert g.beta.primary_contrasts == ("a_computation", "b_causal_contribution", "c_frozen_reuse")


def test_h3_refuses_diversity_endpoint():
    with pytest.raises(q.PlanRefused, match="diversity"):
        q.refuse_endpoint("H3", "archive_diversity")
    with pytest.raises(q.PlanRefused, match="diversity"):
        q.refuse_endpoint("H3", "QD_score_final")
    q.refuse_endpoint("H3", "future_task_solve_fraction")       # silent


def test_h4_refuses_training_task_endpoint():
    with pytest.raises(q.PlanRefused, match="TRAINING"):
        q.refuse_endpoint("H4", "solve_rate", computed_on="training")
    q.refuse_endpoint("H4", "solve_rate", computed_on="frozen_final_suite")   # silent
    assert "training-task solve rate as an endpoint in ANY arm" in q.lane_gate("H4").beta.refusals


def test_h5_bounds_are_constants_and_only_excess_counts():
    g = q.lane_gate("H5")
    assert g.beta.constants["H5_DIRECT_REACH_BOUND"] == 8
    assert g.beta.constants["H5_PERMUTED_REACH_BOUND"] == 12
    # the live H5_1 readout numbers: direct 8.0000, balanced_7 11.7305, scrambled 8.0000
    assert q.h5_excess_over_construction(8.0, "direct")["label"] == "AT_OR_UNDER_BOUND_NO_EVIDENCE"
    assert q.h5_excess_over_construction(11.7305, "learned")["label"] == "AT_OR_UNDER_BOUND_NO_EVIDENCE"
    assert q.h5_excess_over_construction(12.5, "learned")["excess_over_construction"] == pytest.approx(0.5)


def test_h1_gate_carries_pool_precondition():
    g = q.lane_gate("H1")
    assert any("pool >= 2K" in p for p in g.beta.preconditions)
    assert any("3 bits with K = 4" in r for r in g.beta.refusals)


def test_h0_worked_sizing_sizes_g_and_i_separately():
    rng = random.Random(5)
    blocks = []
    for _ in range(10):
        b = rng.uniform(0.3, 0.5)
        blocks.append({c: b + rng.gauss(0, 0.05) for c in q.CELLS})
    out = q.h0_worked_sizing(blocks)
    assert out["I"]["block_sd"] > out["G"]["block_sd"]
    assert out["I"]["blocks_for_interval_clearance_at_null"] >= out["G"]["blocks_for_interval_clearance_at_null"]
    assert set(out["G"]["quantities"]) == set(q.THREE_QUANTITIES)


# ------------------------------------------------ HARM-11: program family

def test_program_family_states_both_rates():
    f = q.program_family()
    assert f["n_lanes"] == 6
    assert abs(f["program_fwer_if_uncorrected"] - (1 - 0.95 ** 6)) < 1e-12
    assert abs(f["program_level_alpha_per_lane"] - 0.05 / 6) < 1e-12
    assert abs(f["expected_false_supports_if_uncorrected"] - 0.30) < 1e-12


# ----------------------------------------------- HARM-25: H3 manifest

def test_h3_manifest_carries_the_ten_fields_and_shared_caps():
    with open(os.path.join(H0H5, "h3_prospective_utility_analysis_v1.json"), encoding="ascii") as f:
        m = json.load(f)
    for fld in ("source_refs", "source_set_digest", "analysis_version", "unit_of_analysis",
                "measurement_identity", "declared_null", "mode", "eligible_count",
                "min_attainable_p", "exclusions"):
        assert fld in m, fld
    arms = {k: v for k, v in m["arms"].items() if isinstance(v, dict)}
    assert set(arms) == {"top_k", "uniform", "behavioral", "hybrid"}
    assert len({(a["cap_items"], a["cap_bytes"]) for a in arms.values()}) == 1
    assert arms["hybrid"]["reserve"] == 16 and arms["hybrid"]["cap_items"] == 64
    assert m["mode"] == "FROZEN"
    assert m["eligible_count"]["min_attainable_p_at_n"]["6"] == q.min_attainable_p_paired(6)
    for c in m["primary_contrasts"]:
        if c in ("multiplicity", "estimator"):
            continue
        q.refuse_endpoint("H3", c)       # none of the primaries is a diversity measure


# ----------------------------------------- HARM-24: PEW encounter manifests

def test_pew_encounter_manifests_carry_the_ten_fields():
    with open(os.path.join(H0H5, "pew_encounter_analyses_v1.json"), encoding="ascii") as f:
        fam = json.load(f)
    assert len(fam["manifests"]) == 5
    for m in fam["manifests"]:
        for fld in ("analysis_version", "unit_of_analysis", "measurement_identity", "declared_null",
                    "eligible_count", "min_attainable_p", "exclusions", "reading_bound"):
            assert fld in m, (m["id"], fld)
        assert set(m["declared_null"]["controls"]) == {"positive", "negative", "cheat"}, m["id"]
    assert fam["common"]["mode"].startswith("FROZEN")
    assert fam["common"]["eligible_count_printed_first"] is True


# ------------------------------------------ HARM-32: sqrt(2) is conditional

def test_h4_protocol_reporting_is_conditional_and_versioned():
    assert q.H4_PROTOCOL_VERSION == "H4-ADAPTIVE-1.0.1"
    rep = q.H4_ADAPTIVE_PROTOCOL["reporting"]
    assert "ONLY under" in rep and "by construction" not in rep


# ============================== QR-1.2.1: self-attack on 1.2.0 (review packet Q1, Q2)

def test_relabel_admits_a_new_plan_on_disjoint_tasks_and_refuses_overlap():
    # 12 blocks so the relabel path, not HA-1.6, is what fires on the same-body case
    diag = _plan(purpose="DIAGNOSTIC", n_blocks=12, pilot_task_ids=(1, 2, 3), confirmation_task_ids=(4, 5))
    frozen = q.freeze_plan(diag, "2026-09-18")
    assert frozen["task_ids"] == [1, 2, 3, 4, 5]
    fresh = _plan(purpose="CONFIRMATORY", plan_version="t2", pilot_task_ids=(6, 7), confirmation_task_ids=(8, 9))
    assert "no_relabel_after_data_opened" in q.validate_plan(fresh, frozen=frozen, data_opened=True)
    reused = _plan(purpose="CONFIRMATORY", plan_version="t2", pilot_task_ids=(6, 7), confirmation_task_ids=(5, 9))
    with pytest.raises(q.PlanRefused, match="1 confirmation task"):
        q.validate_plan(reused, frozen=frozen, data_opened=True)
    same = _plan(purpose="CONFIRMATORY", n_blocks=12, pilot_task_ids=(1, 2, 3), confirmation_task_ids=(4, 5))
    with pytest.raises(q.PlanRefused, match="same plan body"):
        q.validate_plan(same, frozen=frozen, data_opened=True)
    legacy = {k: v for k, v in frozen.items() if k != "task_ids"}     # a pre-1.2.1 record
    with pytest.raises(q.PlanRefused, match="no task ids"):
        q.validate_plan(fresh, frozen=legacy, data_opened=True)


def test_alias_chains_resolve_and_cycles_are_refused():
    cells = {"S00": {"payload_hash": "a"}, "S10": {"payload_hash": "b"}}
    rec = q.validate_cell_payloads({"cells": cells, "aliases": {"fresh": "S00", "baseline": "fresh"}})
    assert rec["aliases"]["baseline"]["cell"] == "S00"
    with pytest.raises(q.PlanRefused, match="alias cycle"):
        q.validate_cell_payloads({"cells": cells, "aliases": {"x": "y", "y": "x"}})
    with pytest.raises(q.PlanRefused, match="both an alias and a cell"):
        q.validate_cell_payloads({"cells": cells, "aliases": {"S10": "S00"}})


def test_h5_bounds_are_computed_and_the_definition_is_the_non_parent_one():
    r = q.h5_reach_bounds_computed(n_permutations=1)
    assert r["direct_reach_excl_parent"] == {"min": 8, "max": 8, "mean": 8.0}
    assert r["direct_reach_incl_parent"]["max"] == 9          # the parent's own rule counts as a ninth
    assert r["direct_neutral_mean"] == 4.0                    # the live readout's mean_neutral 4.0000
    assert r["direct_bound_holds"] and r["permuted_bound_is_neighbour_count"]
    # a balanced RANDOM permutation reaches ~11.72; the live learned balanced_7 read 11.7305
    assert 11.6 < r["balanced_random_permutation_mean_reach_excl_parent"][0] < 11.85
