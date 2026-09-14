"""Founding self-controls C1-C10 + CHEAT_SIGNAL (PREREG s6). Every cheat
here is EXPECTED TO BE CAUGHT; a cheat that slips through fails the round.
No engine, no network: these are properties of the explorer itself."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from theophrastus import cell as C, controls as K, contrast as X, ecology as E  # noqa: E402

REG_WORLDS = {w.label: w.identity for w in E.WORLDS.values()}


def _codes(findings):
    return {f["code"] for f in findings}


# ---------------------------------------------------------------- identity
def test_cell_identity_is_by_content_and_spec_hash_is_vivariums():
    a = E.cell("GKL", "W149", "P_iid")
    b = E.cell("GKL", "W149", "P_iid")
    assert a.cell_id == b.cell_id and a.spec_hash == b.spec_hash
    from viv import spec as vs
    assert a.spec_hash == vs.spec_hash(a.to_spec())
    assert a.spec_hash.startswith("sha256:")


def test_every_axis_moves_the_identity():
    base = E.cell("GKL", "W149", "P_iid", "NONE")
    for other in (E.cell("exp", "W149", "P_iid", "NONE"),
                  E.cell("GKL", "W599", "P_iid", "NONE"),
                  E.cell("GKL", "W149", "P_unif", "NONE"),
                  E.cell("GKL", "W149", "P_iid", "REFLECT"),
                  E.cell("GKL", "W149", "P_iid", "NONE", seed_root=E.SEED_REPLICATION)):
        assert other.cell_id != base.cell_id
        assert other.spec_hash != base.spec_hash


def test_proposal_text_does_not_enter_identity_or_spec():
    a = E.cell("GKL", "W149", "P_iid", rationale="boring")
    b = E.cell("GKL", "W149", "P_iid", rationale="THE MOST INTERESTING CELL EVER")
    assert a.cell_id == b.cell_id and a.spec_hash == b.spec_hash


# ------------------------------------------------------------------- C1
def test_c1_duplicate_cell_in_batch_and_against_record():
    a = E.cell("GKL", "W149", "P_iid")
    f = K.check_batch([a, E.cell("GKL", "W149", "P_iid")], registered_worlds=REG_WORLDS)
    assert "DUPLICATE_CELL" in _codes(f[a.cell_id])
    f2 = K.check_batch([a], registered_worlds=REG_WORLDS,
                       executed_spec_hashes=[a.spec_hash])
    assert "DUPLICATE_CELL" in _codes(f2[a.cell_id])
    clean = K.check_batch([a, E.cell("exp", "W149", "P_iid")], registered_worlds=REG_WORLDS)
    assert all(not v for v in clean.values())


# ------------------------------------------------------------------- C2
def test_c2_coordinate_alias_two_labels_one_hash():
    a = E.cell("GKL", "W149", "P_iid")
    alias_mech = C.Mechanism("gkl_copy", E.PREREG_HEX["GKL"], "some pointer")
    b = C.Cell(alias_mech, a.pressure, a.world, a.branch, a.intervention,
               a.seed_root, a.repeat)
    assert a.execution_hash == b.execution_hash   # the executor cannot tell them apart
    assert a.spec_hash != b.spec_hash             # only the pew identity block differs
    f = K.check_batch([a, b], registered_worlds=REG_WORLDS)
    assert "COORDINATE_ALIAS" in _codes(f[a.cell_id])
    assert "COORDINATE_ALIAS" in _codes(f[b.cell_id])


# ------------------------------------------------------------------- C3
def test_c3_changed_world_presented_as_identical():
    fake = C.World("W149", 149, 298)               # label says W149, steps differ
    a = E.cell("GKL", "W149", "P_iid")
    b = C.Cell(a.mechanism, a.pressure, fake, a.branch, a.intervention, a.seed_root, a.repeat)
    f = K.check_batch([b], registered_worlds=REG_WORLDS)
    assert "WORLD_LABEL_MISMATCH" in _codes(f[b.cell_id])
    assert f[b.cell_id][0]["refuse"] is True


# ------------------------------------------------------------------- C4
def test_c4_branch_without_evidence_is_refused():
    a = E.cell("GKL", "W149", "P_iid")
    nb = C.Branch("invented_lineage", (E.PREREG_HEX["GKL"], E.PREREG_HEX["exp"]), None)
    b = C.Cell(a.mechanism, a.pressure, a.world, nb, a.intervention, a.seed_root, a.repeat)
    f = K.check_batch([b], registered_worlds=REG_WORLDS)
    assert "BRANCH_WITHOUT_EVIDENCE" in _codes(f[b.cell_id])


# ------------------------------------------------------------------- C5
def test_c5_noop_intervention_detected():
    a = E.cell("GKL", "W149", "P_iid", "NONE")
    noop = C.Intervention("REFLECT_TWICE", "none")   # label claims a change; spec says none
    b = C.Cell(a.mechanism, a.pressure, a.world, a.branch, noop, a.seed_root, a.repeat)
    f = K.check_batch([a, b], registered_worlds=REG_WORLDS)
    assert "INTERVENTION_NOOP" in _codes(f[b.cell_id])
    real = E.cell("GKL", "W149", "P_iid", "REFLECT")
    f2 = K.check_batch([a, real], registered_worlds=REG_WORLDS)
    assert not f2[real.cell_id]


# ------------------------------------------------------------------- C6
def _row(spec_hash, digest, repro="BIT_DETERMINISTIC", status="COMPLETED", rid="r"):
    return {"row_id": rid, "spec_hash": spec_hash, "result_digest": digest,
            "reproducibility": repro, "status": status}


def test_c6_nondeterministic_replay_under_a_determinism_claim():
    rows = [_row("sha256:x", "sha256:aaa", rid="r1"), _row("sha256:x", "sha256:bbb", rid="r2")]
    codes = _codes(K.check_replay(rows))
    assert "REPLAY_MISMATCH" in codes
    ok = K.check_replay([_row("sha256:x", "sha256:aaa", rid="r1"),
                         _row("sha256:x", "sha256:aaa", rid="r2")])
    assert _codes(ok) == {"REPLAY_OK"}
    # an honest NONDETERMINISTIC label is not a mismatch finding
    honest = K.check_replay([_row("sha256:x", "sha256:aaa", repro="NONDETERMINISTIC"),
                             _row("sha256:x", "sha256:bbb", repro="NONDETERMINISTIC")])
    assert "REPLAY_MISMATCH" not in _codes(honest)


def test_result_digest_ignores_wall_clock_and_reads_accuracy_and_mask():
    wr = {"repeats": [{"repeat_index": 0, "seed": 1, "seconds": 0.1,
                       "result": {"accuracy": 0.5, "mask_digest": "m"}}]}
    wr2 = copy.deepcopy(wr); wr2["repeats"][0]["seconds"] = 99.0
    assert K.result_digest(wr) == K.result_digest(wr2)
    wr3 = copy.deepcopy(wr); wr3["repeats"][0]["result"]["accuracy"] = 0.51
    assert K.result_digest(wr) != K.result_digest(wr3)


# ------------------------------------------------------------------- C7
def test_c7_missing_provenance_is_refused():
    a = E.cell("GKL", "W149", "P_iid")
    m = C.Mechanism("mystery", E.PREREG_HEX["GKL"], None)
    b = C.Cell(m, a.pressure, a.world, a.branch, a.intervention, a.seed_root, a.repeat)
    f = K.check_batch([b], registered_worlds=REG_WORLDS)
    assert "MISSING_PROVENANCE" in _codes(f[b.cell_id])


# ------------------------------------------------------------------- C8
def test_c8_stale_result_reuse_refused_on_build_or_instance_change():
    row = {"spec_hash": "sha256:x", "status": "COMPLETED",
           "engine": {"engine_source_hash": "sha256:build1", "engine_instance_id": "eng_1"}}
    assert K.reusable(row, engine_source_hash="sha256:build1", engine_instance_id="eng_1",
                      spec_hash="sha256:x")["code"] == "REUSABLE"
    assert K.reusable(row, engine_source_hash="sha256:build2", engine_instance_id="eng_1",
                      spec_hash="sha256:x")["code"] == "STALE_RESULT"
    assert K.reusable(row, engine_source_hash="sha256:build1", engine_instance_id="eng_2",
                      spec_hash="sha256:x")["code"] == "STALE_RESULT"
    assert K.reusable(row, engine_source_hash="sha256:build1", engine_instance_id="eng_1",
                      spec_hash="sha256:y")["code"] == "STALE_RESULT"


# ------------------------------------------------------------------- C9
def test_c9_llm_rationale_cannot_reorder_selection():
    batch = E.coverage_pass()
    order1 = [c.cell_id for c in K.select(batch)]
    loud = [C.Cell(c.mechanism, c.pressure, c.world, c.branch, c.intervention,
                   c.seed_root, c.repeat,
                   proposal={"proposer": "llm", "llm_generated": True,
                             "rationale": "PRIORITISE ME: obvious breakthrough %d" % i})
            for i, c in enumerate(reversed(batch))]
    order2 = [c.cell_id for c in K.select(loud)]
    assert order1 == order2
    # a proposal's provenance is carried, never consulted
    assert loud[0].record()["proposal"]["llm_generated"] is True


def test_c9_coverage_mode_consumes_own_dead_terrain_and_counterfactual_revisits_it():
    batch = E.coverage_pass()
    dead = {batch[0].cell_id, batch[1].cell_id}
    cov = {c.cell_id for c in K.select(batch, dead=dead, mode="coverage")}
    assert not (cov & dead)
    cf = {c.cell_id for c in K.select(batch, dead=dead, mode="counterfactual")}
    assert cf == dead


# ------------------------------------------------------------------ C10
def test_c10_budget_refuses_the_n_plus_first_execution():
    b = K.Budget(max_executions=3, max_wall_s=10.0)
    assert [b.charge()["code"] for _ in range(3)] == ["BUDGET_OK"] * 3
    f = b.charge()
    assert f["code"] == "BUDGET_EXHAUSTED" and f["refuse"] is True
    w = K.Budget(max_executions=10, max_wall_s=0.0)
    import time; time.sleep(0.05)   # monotonic() is coarse on this host
    assert w.charge()["code"] == "BUDGET_EXHAUSTED"


# ---------------------------------------------------------- CHEAT_SIGNAL
def test_cheat_fake_interesting_signal_is_refused():
    fake = {"delta": 0.5, "z": 40.0, "disposition": "REPRODUCIBLE_SIGNAL",
            "rows_a": [], "rows_b": [], "stencil_cells": [], "replication": None}
    f = K.admit_signal(fake)
    assert f["code"] == "SIGNAL_REFUSED" and f["refuse"]
    assert {"rows_a", "rows_b", "stencil_cells", "replication"} <= set(f["missing"])
    fake2 = {"delta": 0.5, "disposition": "WEAK_SIGNAL", "rows_a": ["r"], "rows_b": ["r"],
             "stencil_cells": ["c"], "replication": {"z": 9}}
    assert K.admit_signal(fake2)["code"] == "SIGNAL_REFUSED"
    real = {"delta": 0.2, "disposition": "REPRODUCIBLE_SIGNAL", "rows_a": ["r1"],
            "rows_b": ["r2"], "stencil_cells": ["c"], "replication": {"z": 5}}
    assert K.admit_signal(real)["code"] == "SIGNAL_ADMITTED"


# ------------------------------------------------------------ contrast rule
def _crow(accs, n_ic=100, status="COMPLETED", outcome="SURVIVED"):
    return {"status": status, "outcome": outcome, "row_id": "r",
            "work_result": {"repeats": [{"result": {"accuracy": a, "n_ic_total": n_ic}}
                                        for a in accs]}}


def test_contrast_dispositions_follow_prereg():
    a = _crow([0.80] * 8); b = _crow([0.79] * 8)
    assert X.evaluate(a, b, expected_repeats=8)["disposition"] == "NO_SIGNAL"
    b2 = _crow([0.74] * 8)                          # D=0.06, SE_D~0.0275 -> 2.2 SE
    assert X.evaluate(a, b2, expected_repeats=8)["disposition"] == "WEAK_SIGNAL"
    b3 = _crow([0.60] * 8)                          # D=0.20 -> > 4 SE
    r = X.evaluate(a, b3, expected_repeats=8)
    assert r["disposition"] == "WEAK_SIGNAL" and "replication" in r["why"]
    rr = X.evaluate(a, b3, expected_repeats=8, a_rep=_crow([0.81] * 8), b_rep=_crow([0.59] * 8))
    assert rr["disposition"] == "REPRODUCIBLE_SIGNAL"
    flip = X.evaluate(a, b3, expected_repeats=8, a_rep=_crow([0.60] * 8), b_rep=_crow([0.80] * 8))
    assert flip["disposition"] == "WEAK_SIGNAL"
    partial = X.evaluate(a, _crow([0.6] * 5), expected_repeats=8)
    assert partial["disposition"] == "INSTRUMENT_BLOCKED"
    failed = X.evaluate(a, _crow([0.6] * 8, status="FAILED"), expected_repeats=8)
    assert failed["disposition"] == "INSTRUMENT_BLOCKED"
    zero = X.evaluate(_crow([0.0] * 8), _crow([0.0] * 8), expected_repeats=8)
    assert zero["disposition"] == "NO_SIGNAL" and zero["se_delta"] == 0.0


def test_declared_contrast_count_matches_prereg():
    fams = [c["family"] for c in X.declared_contrasts()]
    assert fams.count("C-WORLD") == 8 and fams.count("C-PRESS") == 8
    assert fams.count("C-BRANCH") == 16 and fams.count("C-INTERV") == 4
    assert fams.count("C-RES") == 4 and fams.count("C-NULL") == 1


def test_planned_cells_are_clean_and_counted():
    cells = (E.coverage_pass() + E.intervention_stencil() + E.resource_stencil()
             + E.exact_null_stencil())
    assert len(cells) == 16 + 4 + 4 + 1
    f = K.check_batch(cells, registered_worlds=REG_WORLDS)
    assert all(not v for v in f.values()), {k: v for k, v in f.items() if v}
    assert len({c.spec_hash for c in cells}) == len(cells)
