"""Per-entry cost provenance, and the one key inside it the engine enforces.

WHY THIS EXISTS. The resource-entry allowlist is five names on purpose: a
caller must not be able to smuggle semantics -- enforcement above all -- into
the one vector the engine is the authority on. But a producer's real provenance
(which counter, whose process, which upstream event) had nowhere to go, so it
was dropped in translation, and two ledgers that have both dropped it cannot be
reconciled afterwards. TRACKA-VECTOR-1 was exactly this: Archaeon's vector was
refused for `enforcement_class`, then for its prose method, then for its scope,
and the fix put the provenance in a per-entry `refs` -- which was refused too,
being a sixth key.

So there is now one opaque slot, opaque in BOTH directions: sealed, returned,
never branched on. And exactly one key inside it means something --
`refs.artifact_digest`, the join key TRACKA-RECON-2 asked for -- which is
checked against the event's own declared artifacts, because a join key nothing
verifies is decoration.

Every detector below is PAIRED: the thing fires, and the neighbouring thing
that must not fire doesn't.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sfe.errors import ValidationError                            # noqa: E402
from sfe.runtime import (ENTRY_REFS_DIGEST_KEY,                   # noqa: E402
                         MAX_ENTRY_REFS_BYTES, Foundry)


@pytest.fixture
def f(tmp_path):
    g = Foundry(str(tmp_path / "r.db"))
    yield g
    g.close()


def _world(f, name="w", budget=None):
    c = f.create_client(name + "-owner")
    s = f.create_session(c, name + "-s")
    w = f.create_world(s, name, budget=budget)["world_id"]
    f.start_world(w, c)
    return c, w


def _art(f, w, c, body=b"payload"):
    a = f.create_artifact(w, "blob", body, client_id=c)
    return a["artifact_id"], a["blob_hash"]


# ===========================================================================
# the slot itself
# ===========================================================================
def test_provenance_survives_the_trip_and_comes_back_verbatim(f):
    c, w = _world(f, "w")
    prov = {"producer_cost_event_id": "cost:27d60c2e0f21010dfa4c31e3",
            "producer_stage": "generation",
            "producer_method": "time.perf_counter delta",
            "producer_enforcement_class": "measured",
            "producer_scope": "producer", "children": []}
    ce = f.record_cost_event(
        w, stage="generation", attempt_id="cs-h1h0-1-p1",
        resources=[{"resource": "wall_seconds", "quantity": 0.097, "unit": "s",
                    "method": "clock", "scope": "campaign", "refs": prov}],
        client_id=c)
    assert ce["resources"][0]["refs"] == prov
    back = f.get_cost_event(ce["cost_event_id"], client_id=c)
    assert back["sealed"]["resources"][0]["refs"] == prov


def test_the_engine_never_reads_provenance_for_a_decision(f):
    """The whole point of the slot being opaque. A caller that puts
    'enforcement' in refs must not thereby change its enforcement, which is the
    exact escape the five-name allowlist exists to prevent."""
    c, w = _world(f, "w", budget={"cpu_s": {"limit": 100,
                                            "enforcement": "enforceable"}})
    ce = f.record_cost_event(
        w, stage="execution",
        resources=[{"resource": "cpu_s", "quantity": 1.0, "unit": "s",
                    "method": "clock",
                    "refs": {"enforcement": "unavailable",
                             "enforcement_class": "estimated",
                             "quantity": 0.0}}],
        client_id=c)
    e = ce["resources"][0]
    assert e["enforcement"] == "enforceable"      # from the LIMIT, not refs
    assert e["quantity"] == 1.0                   # not the 0.0 in refs
    assert f.budget_status(w)["consumed"]["cpu_s"] == 1.0


@pytest.mark.parametrize("bad", ["a string", 7, ["a", "list"], True])
def test_provenance_must_be_a_mapping(f, bad):
    c, w = _world(f, "w")
    with pytest.raises(ValidationError):
        f.record_cost_event(w, stage="analysis",
                            resources=[{"resource": "items", "quantity": 1,
                                        "refs": bad}], client_id=c)
    # PAIRED: a mapping, and an absent one, both go through
    for ok in ({"note": "fine"}, None):
        f.record_cost_event(w, stage="analysis",
                            resources=[{"resource": "items", "quantity": 1,
                                        "refs": ok}], client_id=c)


def test_provenance_is_bounded(f):
    """An opaque dict on every entry is an unbounded write channel into the
    hash chain if nothing caps it."""
    c, w = _world(f, "w")
    too_big = {"pad": "x" * (MAX_ENTRY_REFS_BYTES + 64)}
    with pytest.raises(ValidationError) as ei:
        f.record_cost_event(w, stage="analysis",
                            resources=[{"resource": "items", "quantity": 1,
                                        "refs": too_big}], client_id=c)
    assert "refs exceeds" in str(ei.value)
    # PAIRED: comfortably under the cap is accepted
    ok = {"pad": "x" * 512}
    ce = f.record_cost_event(w, stage="analysis",
                             resources=[{"resource": "items", "quantity": 1,
                                         "refs": ok}], client_id=c)
    assert ce["resources"][0]["refs"] == ok


def test_provenance_that_cannot_be_sealed_is_refused(f):
    """It is serialized into the world's hash chain verbatim, so a value that
    will not serialize must be refused at the door rather than crash the
    append."""
    c, w = _world(f, "w")
    with pytest.raises(ValidationError):
        f.record_cost_event(w, stage="analysis",
                            resources=[{"resource": "items", "quantity": 1,
                                        "refs": {"o": {1, 2, 3}}}],
                            client_id=c)


# ===========================================================================
# the one key that means something
# ===========================================================================
def test_the_join_key_is_checked_against_what_the_event_declared(f):
    c, w = _world(f, "w")
    _aid, digest = _art(f, w, c, b"the bytes that moved")
    other = _art(f, w, c, b"some other artifact")[1]

    # FIRES: a claim on an artifact this event never declared
    with pytest.raises(ValidationError) as ei:
        f.record_cost_event(
            w, stage="retrieval", source_artifacts=[digest],
            resources=[{"resource": "artifact_bytes", "quantity": 20,
                        "unit": "bytes", "method": "counter",
                        "refs": {ENTRY_REFS_DIGEST_KEY: other}}],
            client_id=c)
    assert "did not declare" in str(ei.value)

    # DOES NOT FIRE: the same claim once the event declares it
    ce = f.record_cost_event(
        w, stage="retrieval", source_artifacts=[digest],
        resources=[{"resource": "artifact_bytes", "quantity": 20,
                    "unit": "bytes", "method": "counter",
                    "refs": {ENTRY_REFS_DIGEST_KEY: digest}}],
        client_id=c)
    assert ce["resources"][0]["refs"][ENTRY_REFS_DIGEST_KEY] == digest


def test_an_output_artifact_counts_as_declared_too(f):
    c, w = _world(f, "w")
    _aid, digest = _art(f, w, c, b"produced here")
    ce = f.record_cost_event(
        w, stage="generation", output_artifacts=[digest],
        resources=[{"resource": "output_bytes", "quantity": 13,
                    "unit": "bytes", "method": "counter",
                    "refs": {ENTRY_REFS_DIGEST_KEY: digest}}],
        client_id=c)
    assert ce["resources"][0]["refs"][ENTRY_REFS_DIGEST_KEY] == digest


def test_the_join_key_has_one_spelling(f):
    """The write gate accepts a bare hex digest; the join key must normalize to
    the same string either way, or two spellings of one artifact produce two
    rows in an index whose whole job is to bring them together."""
    c, w = _world(f, "w")
    _aid, digest = _art(f, w, c, b"x")
    bare = digest.split(":", 1)[1]
    ce = f.record_cost_event(
        w, stage="retrieval", source_artifacts=[bare],
        resources=[{"resource": "artifact_bytes", "quantity": 1,
                    "unit": "bytes", "method": "counter",
                    "refs": {ENTRY_REFS_DIGEST_KEY: bare.upper()}}],
        client_id=c)
    assert ce["resources"][0]["refs"][ENTRY_REFS_DIGEST_KEY] == digest


def test_a_reference_that_is_not_a_digest_is_kept_verbatim(f):
    """A producer names experiment ids, not hashes. Normalizing the declared
    set would reject every such event; the claim must match the raw string."""
    c, w = _world(f, "w")
    exp = "01dab91c-e09f-474c-b680-9b24f4196dd4"
    ce = f.record_cost_event(
        w, stage="generation", output_artifacts=[exp],
        resources=[{"resource": "items", "quantity": 24, "unit": "count",
                    "method": "counter",
                    "refs": {ENTRY_REFS_DIGEST_KEY: exp}}],
        client_id=c)
    assert ce["resources"][0]["refs"][ENTRY_REFS_DIGEST_KEY] == exp


def test_no_claim_at_all_is_always_fine(f):
    """Most cost lines do not move bytes. The key is optional, and an event
    with no artifacts must not become unrecordable."""
    c, w = _world(f, "w")
    ce = f.record_cost_event(w, stage="analysis",
                             resources=[{"resource": "cpu_s", "quantity": 0.5,
                                         "unit": "s", "method": "clock"}],
                             client_id=c)
    assert ce["resources"][0]["refs"] == {}


# ===========================================================================
# the index
# ===========================================================================
def test_the_report_answers_what_moving_these_bytes_cost(f):
    c, w = _world(f, "w")
    _aid, d1 = _art(f, w, c, b"first")
    _bid, d2 = _art(f, w, c, b"second")
    for stage, d, q in (("retrieval", d1, 5.0), ("execution", d1, 0.25),
                        ("retrieval", d2, 6.0)):
        f.record_cost_event(
            w, stage=stage, attempt_id="a1", source_artifacts=[d],
            resources=[{"resource": "artifact_bytes", "quantity": q,
                        "unit": "bytes", "method": "counter",
                        "refs": {ENTRY_REFS_DIGEST_KEY: d}}],
            client_id=c)
    rep = f.cost_report(w, client_id=c)
    assert set(rep["by_artifact"]) == {d1, d2}
    assert len(rep["by_artifact"][d1]) == 2
    assert {r["stage"] for r in rep["by_artifact"][d1]} == {"retrieval",
                                                            "execution"}
    assert rep["by_artifact"][d2][0]["quantity"] == 6.0
    # the index reports, it does not re-bill: the totals are unchanged by it
    assert rep["additive_totals"]["artifact_bytes"] == 11.25


def test_an_unclaimed_line_is_absent_from_the_index_not_zero_in_it(f):
    c, w = _world(f, "w")
    f.record_cost_event(w, stage="analysis",
                        resources=[{"resource": "cpu_s", "quantity": 1.0,
                                    "unit": "s", "method": "clock"}],
                        client_id=c)
    assert f.cost_report(w, client_id=c)["by_artifact"] == {}


# ===========================================================================
# TRACKA-VECTOR-1, closed: the real receipt, over the real models
# ===========================================================================
def _receipt_entries():
    here = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))
    p = os.path.join(here, "archaeon", "docs", "h0h5",
                     "ISSUE_RECEIPTS_2026-09-10.h1h0_p1.json")
    if not os.path.exists(p):
        pytest.skip("Archaeon's receipt is not in this checkout: %s" % p)
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)["engine_entries"]


def test_archaeons_engine_entries_are_accepted_as_they_stand(f):
    """TRACKA-VECTOR-1 end to end, against the committed receipt rather than a
    vector written here to pass."""
    entries = _receipt_entries()
    c, w = _world(f, "w", budget={
        "wall_seconds": {"limit": None, "enforcement": "measured"},
        "cpu_seconds": {"limit": 600, "enforcement": "enforceable"},
        "items": {"limit": None, "enforcement": "measured"}})
    ce = f.record_cost_event(w, stage="generation",
                             attempt_id="cs-h1h0-1-p1",
                             resources=entries, client_id=c)
    got = {e["resource"]: e for e in ce["resources"]}
    # the engine stamped the class from the LIMIT, in every case
    assert got["wall_seconds"]["enforcement"] == "measured"
    assert got["cpu_seconds"]["enforcement"] == "enforceable"
    assert got["items"]["enforcement"] == "measured"
    assert got["gpu_seconds"]["enforcement"] == "unavailable"
    # and never took one from the caller
    for e in ce["resources"]:
        assert "enforcement_class" not in e
        assert e["refs"]["producer_enforcement_class"] in (
            "measured", "unavailable")
    # unavailable is not zero
    assert got["gpu_seconds"]["quantity"] is None
    rep = f.cost_report(w, client_id=c)
    assert "gpu_seconds" not in rep["additive_totals"]
    assert rep["unavailable_counts"]["gpu_seconds"] == 1


def test_the_api_request_model_accepts_the_same_entries():
    """The runtime and the request model must agree; the first cut of this
    field was refused by the model while the runtime would have taken it."""
    from sfe.api import CostEventCreate
    entries = _receipt_entries()
    m = CostEventCreate(stage="generation", resources=entries)
    assert [e.refs["producer_method"] for e in m.resources] == [
        e["refs"]["producer_method"] for e in entries]


# ===========================================================================
# C7 -- a 200 that indexed nothing must not look like a 200 that did
# ===========================================================================
def test_the_response_says_what_it_indexed(f):
    c, w = _world(f, "w")
    _aid, digest = _art(f, w, c, b"the bytes")
    ce = f.record_cost_event(
        w, stage="retrieval", source_artifacts=[digest],
        resources=[{"resource": "artifact_bytes", "quantity": 9,
                    "unit": "bytes", "method": "counter",
                    "refs": {ENTRY_REFS_DIGEST_KEY: digest}}],
        client_id=c)
    assert ce["indexed_artifacts"] == [digest]
    # and it agrees with what the report will actually show
    assert sorted(f.cost_report(w, client_id=c)["by_artifact"]) == [digest]


def test_refs_on_the_EVENT_indexes_nothing_and_the_response_says_so(f):
    """THE EXACT CASE THAT COST A DAY. Event-level refs is legitimate, opaque,
    sealed and echoed -- and feeds no index. Before this field the only tell
    was an entry-level refs echoing back as {}, which nobody thinks to compare
    against a 200."""
    c, w = _world(f, "w")
    _aid, digest = _art(f, w, c, b"the bytes")
    ce = f.record_cost_event(
        w, stage="retrieval", source_artifacts=[digest],
        refs={ENTRY_REFS_DIGEST_KEY: digest},        # <- on the EVENT
        resources=[{"resource": "artifact_bytes", "quantity": 9,
                    "unit": "bytes", "method": "counter"}],
        client_id=c)
    assert ce["indexed_artifacts"] == []             # says so, out loud
    assert ce["resources"][0]["refs"] == {}
    assert f.cost_report(w, client_id=c)["by_artifact"] == {}


def test_indexed_artifacts_is_deduped_and_ordered(f):
    """Two lines paying for the same bytes are one indexed artifact, and the
    order is not the order the caller happened to send."""
    c, w = _world(f, "w")
    _a1, d1 = _art(f, w, c, b"one")
    _a2, d2 = _art(f, w, c, b"two")
    hi, lo = sorted([d1, d2], reverse=True)
    ce = f.record_cost_event(
        w, stage="retrieval", source_artifacts=[d1, d2],
        resources=[
            {"resource": "artifact_bytes", "quantity": 3, "unit": "bytes",
             "method": "counter", "refs": {ENTRY_REFS_DIGEST_KEY: hi}},
            {"resource": "engine_fetches", "quantity": 1, "unit": "count",
             "method": "counter", "refs": {ENTRY_REFS_DIGEST_KEY: hi}},
            {"resource": "artifact_bytes", "quantity": 3, "unit": "bytes",
             "method": "counter", "refs": {ENTRY_REFS_DIGEST_KEY: lo}},
        ], client_id=c)
    assert ce["indexed_artifacts"] == sorted([hi, lo])


def test_an_event_with_no_join_key_reports_an_empty_list_not_absence(f):
    """Most cost lines move no bytes. The field is always present, so a caller
    can test it without knowing whether to expect it."""
    c, w = _world(f, "w")
    ce = f.record_cost_event(w, stage="analysis",
                             resources=[{"resource": "cpu_s", "quantity": 0.5,
                                         "unit": "s", "method": "clock"}],
                             client_id=c)
    assert ce["indexed_artifacts"] == []


def test_the_field_reports_and_does_not_decide(f):
    """It is DERIVED. It must not become a second place that grants or refuses
    anything -- the declared-artifact check still governs."""
    c, w = _world(f, "w")
    _aid, digest = _art(f, w, c, b"x")
    with pytest.raises(ValidationError):
        f.record_cost_event(
            w, stage="retrieval",           # nothing declared at all
            resources=[{"resource": "artifact_bytes", "quantity": 1,
                        "unit": "bytes", "method": "counter",
                        "refs": {ENTRY_REFS_DIGEST_KEY: digest}}],
            client_id=c)
