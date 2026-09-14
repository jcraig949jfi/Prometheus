"""Tests for the H3 retention adapter. Concrete risks only.

The bulk of these fire the validator in the FAILING direction, one property at a time. A
validator that has only ever been seen to pass is an assumption; each of the five declared
properties gets a mutation that must be refused, so the passing case means something.

Requires `ribs`, which lives in the isolated env, not the live interpreter. Run with:

    PYTHONPATH=<repo> <tool_cache>/envs/h0h5_tools/Scripts/python -m pytest \
        techne/tests/test_h3_retention.py

Under the live interpreter the archive tests skip and the stream tests still run, because the
stream contract has no pyribs dependency at all -- which is itself worth preserving.
"""
from __future__ import annotations

import copy
import json
import pathlib

import pytest

from techne.h3_retention import build_fixture as F
from techne.h3_retention import stream as S

ribs = pytest.importorskip("ribs", reason="pyribs lives in the isolated env h0h5_tools")
from techne.h3_retention import adapter as A  # noqa: E402

FIXTURE = pathlib.Path(A.__file__).resolve().parent / "fixture" / "stream_v0.jsonl"
DIMS = (4, 4)


@pytest.fixture
def raw():
    lines = [ln for ln in FIXTURE.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return json.loads(lines[0]), [json.loads(ln) for ln in lines[1:]]


def _mutate(raw, idx, fn):
    header, rows = raw
    rows = copy.deepcopy(rows)
    fn(rows[idx])
    return header, rows


# ------------------------------------------------------- the five properties, each refused
def test_property_1_refuses_non_contiguous_seq(raw):
    h, r = _mutate(raw, 3, lambda row: row.__setitem__("seq", 99))
    with pytest.raises(S.StreamError, match=r"ordered_ids"):
        S.validate(h, r)


def test_property_1_refuses_duplicate_candidate_id(raw):
    h, r = _mutate(raw, 3, lambda row: row.__setitem__("candidate_id", "c000"))
    with pytest.raises(S.StreamError, match=r"ordered_ids"):
        S.validate(h, r)


def test_property_2_refuses_a_digest_that_does_not_match_its_payload(raw):
    h, r = _mutate(raw, 2, lambda row: row["payload"].__setitem__("arity", 999))
    with pytest.raises(S.StreamError, match=r"digests"):
        S.validate(h, r)


def test_property_3_refuses_seeded_with_parents(raw):
    h, r = _mutate(raw, 0, lambda row: row["birth"].__setitem__("parent_ids", ["c001"]))
    with pytest.raises(S.StreamError, match=r"birth"):
        S.validate(h, r)


def test_property_3_refuses_a_parent_that_appears_later(raw):
    # c002's parent is c000 (seq 0); point it at c007 (seq 7) instead
    h, r = _mutate(raw, 2, lambda row: row["birth"].__setitem__("parent_ids", ["c007"]))
    with pytest.raises(S.StreamError, match=r"birth"):
        S.validate(h, r)


def test_property_4_refuses_a_row_whose_assay_differs_from_the_header(raw):
    h, r = _mutate(raw, 5, lambda row: row["assay_ref"].__setitem__("assay_version", "0.2.0"))
    with pytest.raises(S.StreamError, match=r"fixed_assay"):
        S.validate(h, r)


def test_property_5_refuses_a_result_ref_whose_bytes_are_wrong(raw):
    h, r = _mutate(raw, 4, lambda row: row["result_ref"].__setitem__("bytes", 1))
    with pytest.raises(S.StreamError, match=r"recoverable"):
        S.validate(h, r, resolver=F.resolver)


def test_property_5_without_a_resolver_the_record_says_the_check_was_structural(raw):
    st = S.validate(*raw)
    assert st.validation["result_refs_resolved"] is False
    assert "STRUCTURAL ONLY" in st.validation["recoverability_check"]


def test_measures_outside_the_declared_range_are_refused(raw):
    h, r = _mutate(raw, 1, lambda row: row.__setitem__("measures", [1.5, 0.1]))
    with pytest.raises(S.StreamError, match=r"measures"):
        S.validate(h, r)


def test_the_unmutated_fixture_validates(raw):
    st = S.validate(*raw, resolver=F.resolver)
    assert st.validation["n_rows"] == 10
    assert st.validation["result_refs_resolved"] is True


def test_duplicate_content_under_two_ids_is_detected_but_not_refused(raw):
    st = S.validate(*raw, resolver=F.resolver)
    dupes = st.validation["duplicate_digests_under_distinct_ids"]
    assert len(dupes) == 1
    assert sorted(next(iter(dupes.values()))) == ["c000", "c009"]


# ------------------------------------------------------- tie policy
def test_tie_policy_is_declared_and_verified_at_both_granularities():
    out = A.verify_tie_policy()
    assert out["declared"] == "FIRST_WRITER_WINS"
    assert out["sequential"]["first_writer_won"]
    assert out["batch"]["first_writer_won"]
    assert out["verified"]


def test_an_exact_tie_leaves_the_incumbent_in_place():
    st = S.read_jsonl(FIXTURE, resolver=F.resolver)
    res = A.replay(st, A.Caps(16, 100_000), dims=DIMS, verify_ties=False)
    tie_row = next(d for d in res.log if d.candidate_id == "c004")
    assert tie_row.disposition == "REJECTED_BY_ARCHIVE"
    assert "c001" in res.retained_ids and "c004" not in res.retained_ids


# ------------------------------------------------------- caps
def test_count_cap_refuses_new_cells_but_not_improvements():
    st = S.read_jsonl(FIXTURE, resolver=F.resolver)
    # a count cap of 2 with an enormous byte budget: only the first two cells survive, and
    # c002's IMPROVEMENT of cell 0 must still be admitted, because it does not grow occupancy
    res = A.replay(st, A.Caps(max_retained=2, max_bytes=10**9), dims=DIMS, verify_ties=False)
    assert res.caps["retained"] == 2
    improved = [d for d in res.log if d.disposition == "RETAINED_IMPROVED_CELL"]
    assert any(d.candidate_id == "c002" for d in improved), \
        "an improvement of an already-occupied cell must not be blocked by the COUNT cap"
    assert res.counts["CAP_REFUSED_COUNT"] > 0
    assert "COUNT" in res.binding_constraint


def test_byte_cap_is_evaluated_on_the_delta_and_a_negative_delta_is_admitted():
    st = S.read_jsonl(FIXTURE, resolver=F.resolver)
    res = A.replay(st, A.Caps(max_retained=16, max_bytes=100_000), dims=DIMS, verify_ties=False)
    # c008 replaces c005 (2400 B) with 300 B -- a negative delta, which must be admitted and
    # must reduce the running total rather than being treated as a 300 B addition
    d = next(x for x in res.log if x.candidate_id == "c008")
    assert d.disposition == "RETAINED_IMPROVED_CELL"
    assert d.bytes_delta == 300 - 2400 < 0
    assert res.retained_bytes == sum(
        x.payload_bytes for x in res.log
        if x.candidate_id in res.retained_ids)


def test_both_caps_bind_on_the_declared_binding_configuration():
    st = S.read_jsonl(FIXTURE, resolver=F.resolver)
    res = A.replay(st, A.Caps(max_retained=4, max_bytes=4_000), dims=DIMS, verify_ties=False)
    assert res.counts["CAP_REFUSED_COUNT"] > 0
    assert res.counts["CAP_REFUSED_BYTES"] > 0
    assert res.binding_constraint == "COUNT+BYTES"


def test_a_run_where_no_cap_binds_says_so_rather_than_implying_the_caps_were_tested():
    st = S.read_jsonl(FIXTURE, resolver=F.resolver)
    res = A.replay(st, A.Caps(max_retained=16, max_bytes=100_000), dims=DIMS, verify_ties=False)
    assert res.binding_constraint == "NONE"
    assert any("NOT exercised" in n for n in res.notes)


def test_zero_caps_are_refused_as_a_refusal_to_run_not_a_budget():
    with pytest.raises(A.AdapterError):
        A.Caps(max_retained=0, max_bytes=10)
    with pytest.raises(A.AdapterError):
        A.Caps(max_retained=1, max_bytes=0)


# ------------------------------------------------------- recoverability and guards
def test_every_non_retained_candidate_keeps_a_resolvable_result_ref():
    st = S.read_jsonl(FIXTURE, resolver=F.resolver)
    res = A.replay(st, A.Caps(4, 4_000), dims=DIMS, verify_ties=False)
    dropped = [d for d in res.log if not d.disposition.startswith("RETAINED")]
    assert dropped, "this configuration must drop something or the test proves nothing"
    for d in dropped:
        assert F.resolver(d.result_ref) is not None, d.candidate_id


def test_no_emitter_or_scheduler_instance_exists_and_the_gate_is_instance_level():
    st = S.read_jsonl(FIXTURE, resolver=F.resolver)
    res = A.replay(st, A.Caps(16, 100_000), dims=DIMS, verify_ties=False)
    g = res.emitter_guard
    assert g["pass"] and not g["live_emitter_instances"] and not g["live_scheduler_instances"]
    # the gate must NOT be on module presence -- importing ribs.archives imports these eagerly
    assert g["modules_imported"] > 0, (
        "if no emitter/scheduler module is imported, a module-presence gate would look like it "
        "passes for the wrong reason; this asserts the unreachable gate stays rejected")


def test_capped_batch_replay_is_refused_rather_than_silently_run_sequentially():
    st = S.read_jsonl(FIXTURE, resolver=F.resolver)
    with pytest.raises(A.AdapterError, match="reimplementing"):
        A.replay(st, A.Caps(4, 4_000), dims=DIMS, granularity="batch", verify_ties=False)


def test_batch_equivalence_reports_whether_the_comparison_was_meaningful():
    st = S.read_jsonl(FIXTURE, resolver=F.resolver)
    loose = A.replay_batch_equivalence(st, A.Caps(16, 100_000), dims=DIMS)
    assert loose["identical"] and loose["comparison_is_meaningful"]
    tight = A.replay_batch_equivalence(st, A.Caps(4, 4_000), dims=DIMS)
    assert tight["caps_bound_on_the_sequential_side"]
    assert tight["comparison_is_meaningful"] is False, (
        "a batch-vs-sequential comparison where one side ran capped and the other did not is a "
        "cap effect, and must not be reported as a granularity effect")
    assert tight["caveat_if_caps_bound"]


def test_determinism_same_stream_same_retained_ids():
    st = S.read_jsonl(FIXTURE, resolver=F.resolver)
    a = A.replay(st, A.Caps(4, 4_000), dims=DIMS, verify_ties=False)
    b = A.replay(st, A.Caps(4, 4_000), dims=DIMS, verify_ties=False)
    assert a.retained_ids == b.retained_ids
    assert [d.disposition for d in a.log] == [d.disposition for d in b.log]


# ---------------------------------------------------------------- the Archaeon seam
def _arch_record(sid, score=1.0, parents=(), status="evaluated", assay="a@v1"):
    import hashlib
    return {"stream_id": sid,
            "candidate_digest": "sha256:" + hashlib.sha256(str(sid).encode()).hexdigest(),
            "birth_status": status, "assay_ref": assay, "score": score,
            "descriptors": [float(sid % 8), float((sid * 3) % 8)],
            "byte_size": 100 + sid, "replay_ref": f"sfe:w0/obs{sid}@{sid}",
            "parent_ids": list(parents)}


EDGES = [[2.0, 4.0, 6.0], [2.0, 4.0, 6.0]]


def test_seam_derives_lineage_kind_from_parent_count():
    from techne.h3_retention import archaeon_seam as SEAM
    recs = [_arch_record(0), _arch_record(1, parents=(0,)), _arch_record(2, parents=(0, 1))]
    st, seam = SEAM.from_candidates(recs, edges=EDGES, stream_id="t")
    assert seam["lineage_kind_derived_from_parent_ids"] == {
        "SEEDED": 1, "MUTATED": 1, "RECOMBINED": 1}
    assert [r.birth_status for r in st.rows] == ["SEEDED", "MUTATED", "RECOMBINED"]


def test_seam_structures_the_assay_string_and_keeps_the_parameter_tail():
    from techne.h3_retention import archaeon_seam as SEAM
    a = SEAM.structured_assay("ca_density_v0@v3:seed_root=930001:n_ic=100:steps=320")
    assert a["assay_id"] == "ca_density_v0"
    # the parameter tail identifies the instrument; dropping it would let two different
    # measurement configurations share an assay identity
    assert a["assay_version"] == "v3:seed_root=930001:n_ic=100:steps=320"
    assert a["version_includes_parameter_tail"]
    assert a["digest"].startswith("sha256:")


def test_seam_refuses_a_stream_whose_assay_changes():
    from techne.h3_retention import archaeon_seam as SEAM
    recs = [_arch_record(0, assay="a@v1"), _arch_record(1, assay="a@v2")]
    with pytest.raises(SEAM.SeamError, match="assay_ref changes"):
        SEAM.from_candidates(recs, edges=EDGES, stream_id="t")


def test_seam_refuses_a_failed_candidate_that_carries_a_score():
    from techne.h3_retention import archaeon_seam as SEAM
    with pytest.raises(SEAM.SeamError, match="failed candidate"):
        SEAM.from_candidates([_arch_record(0, score=0.5, status="failed")],
                             edges=EDGES, stream_id="t")


def test_a_failed_candidate_is_logged_not_inserted_and_charges_nothing():
    from techne.h3_retention import archaeon_seam as SEAM
    recs = [_arch_record(0), _arch_record(1, score=None, status="failed"), _arch_record(2)]
    st, _ = SEAM.from_candidates(recs, edges=EDGES, stream_id="t")
    res = A.replay(st, A.Caps(16, 100_000), dims=[4, 4], verify_ties=False)
    d = next(x for x in res.log if x.seq == 1)
    assert d.disposition == "SKIPPED_NO_SCORE"
    assert d.bytes_delta == 0 and d.result_ref["ref"]
    assert "cand-00001" not in res.retained_ids
    assert res.counts["SKIPPED_NO_SCORE"] == 1


def test_seam_mode_names_its_weakenings_rather_than_hiding_them():
    from techne.h3_retention import archaeon_seam as SEAM
    st, seam = SEAM.from_candidates([_arch_record(0)], edges=EDGES, stream_id="t")
    ids = {w["id"] for w in seam["WEAKENED_AT_THE_SEAM"]}
    assert ids == {"W1", "W2"}
    assert st.validation["seam_mode"] is True
    assert st.validation["digests_carried_not_recomputed"] == 1
    assert st.validation["result_refs_without_a_content_digest"] == 1


def test_a_digestless_result_ref_is_refused_outside_seam_mode():
    rows = [{"seq": 0, "candidate_id": "c0", "candidate_digest": S.digest({"a": 1}),
             "payload": {"a": 1}, "birth": {"status": "SEEDED", "parent_ids": []},
             "assay_ref": {"assay_id": "a"}, "measures": [0.5, 0.5], "objective": 1.0,
             "result_ref": {"kind": "k", "ref": "r", "digest": None, "bytes": 1},
             "payload_bytes": 1}]
    header = {"schema": S.SCHEMA, "stream_id": "t", "n_rows": 1, "measure_dim": 2,
              "measure_ranges": [[0, 1], [0, 1]], "assay_ref": {"assay_id": "a"}}
    with pytest.raises(S.StreamError, match="seam-mode"):
        S.validate(header, rows)
    S.validate(header, rows, seam_mode=True)   # allowed, and recorded


# --------------------------------------------------------------------------- TECHNE-23
# The seam's two named weaknesses, fired in the FAILING direction. A seam that only ever
# sees well-formed input has not shown it can refuse anything.

def _rec_with_digest(sid, digest):
    r = _arch_record(sid)
    r["candidate_digest"] = digest
    return r


@pytest.mark.parametrize("bad", [
    "sha256:notahash",                              # wrong length
    "md5:" + "a" * 32,                              # wrong algorithm label
    "sha256:" + "A" * 64,                           # upper-case hex is not the declared form
    "",                                             # empty
    "sha256:" + "0" * 63,                           # one short
])
def test_w1_a_carried_digest_of_the_wrong_shape_is_refused(bad):
    from techne.h3_retention import archaeon_seam as SEAM
    with pytest.raises(S.StreamError, match="declared shape"):
        SEAM.from_candidates([_rec_with_digest(0, bad)], edges=EDGES, stream_id="t")


def test_w1_shape_check_is_not_vacuous_on_the_real_stream():
    import json, pathlib, re
    p = pathlib.Path("techne/h3_retention/c3_2/candidates.json")
    if not p.exists():
        pytest.skip("real stream not on this tree")
    rows = json.loads(p.read_text(encoding="utf-8"))
    rows = rows if isinstance(rows, list) else rows.get("candidates") or rows.get("rows")
    assert rows and all(S.CARRIED_DIGEST_SHAPE.fullmatch(r["candidate_digest"]) for r in rows)


def test_w2_a_result_ref_whose_bytes_disagree_with_the_resolver_is_refused():
    from techne.h3_retention import archaeon_seam as SEAM
    rec = _arch_record(0)                        # declares byte_size 100
    short = lambda rref: b"x" * 99
    with pytest.raises(S.StreamError, match="declares 100 bytes, resolver returned 99"):
        SEAM.from_candidates([rec], edges=EDGES, stream_id="t", resolver=short)
    with pytest.raises(S.StreamError, match="does not resolve"):
        SEAM.from_candidates([rec], edges=EDGES, stream_id="t", resolver=lambda rref: None)


def test_w2_positive_a_resolver_that_agrees_on_length_passes_and_says_what_it_checked():
    from techne.h3_retention import archaeon_seam as SEAM
    rec = _arch_record(0)
    st, _ = SEAM.from_candidates([rec], edges=EDGES, stream_id="t",
                                 resolver=lambda rref: b"x" * int(rref["bytes"]))
    assert st.validation["result_refs_resolved"] is True
    assert st.validation["result_refs_without_a_content_digest"] == 1


def test_w2_the_weakness_itself_wrong_content_of_the_right_length_is_NOT_caught():
    """This is W2 stated as a test: in seam mode a result_ref has no content digest, so a
    resolver returning the right NUMBER of bytes with the wrong CONTENT passes. The seam
    record says so ('lost: content verification'); this test pins that the loss is real,
    so nobody reads 'resolver checked' as 'content verified'."""
    from techne.h3_retention import archaeon_seam as SEAM
    rec = _arch_record(0)
    st, seam = SEAM.from_candidates([rec], edges=EDGES, stream_id="t",
                                    resolver=lambda rref: b"?" * int(rref["bytes"]))
    assert st.rows[0].result_ref["digest"] is None
    w2 = next(w for w in seam["WEAKENED_AT_THE_SEAM"] if w["id"] == "W2")
    assert "content verification" in w2["lost"]
