"""H0-H5 iteration 1: authorized artifact resolution and cost events.

The five fixtures the brief requires, plus the one exact end-to-end receipt.

NOTHING HERE IS A SECOND ARTIFACT STORE OR BUDGET ENGINE. get_artifact_content
was already the authorized resolver and (world_id, artifact_id) was already the
locator; _debit_budget was already the only primitive that moves a counter and
already hit both the local row and the lineage root. What was missing was an
expected-digest gate on the READ side, a size ceiling anywhere at all, a
reservation phase, and idempotence on the generic charge path.

Three fixtures the brief names ALREADY EXIST and are cited rather than
re-authored:
  * permission denied  -- test_G11_probe1_no_content_without_import,
                          test_G11_probe2_3_origin_id_and_guess_denied
                          (tests/test_sfe_gen21.py), and
                          test_H6_01_no_transitive_reexport
                          (tests/test_sfe_requalification.py)
  * wrong hash (WRITE) -- the D-CIDGATE-1 tests
  * fork budget        -- test_H3_01_fork_cannot_mint_scientific_budget
                          (tests/test_sfe_requalification.py)
What is new below is the READ-side half of each, which did not exist.
"""
import hashlib
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sfe.errors import (AccessDenied, BudgetExhausted, ConflictError,  # noqa: E402
                        NotFound, ValidationError)
from sfe.runtime import (DEFAULT_MAX_ARTIFACT_BYTES, Foundry)          # noqa: E402


def sha(b):
    return "sha256:" + hashlib.sha256(b).hexdigest()


@pytest.fixture
def f(tmp_path):
    g = Foundry(str(tmp_path / "h.db"))
    yield g
    g.close()


def _world(f, name="w", client=None, budget=None):
    c = client or f.create_client(name + "-owner")
    s = f.create_session(c, name + "-s")
    w = f.create_world(s, name, budget=budget)["world_id"]
    f.start_world(w, c)
    return c, w


# ===========================================================================
# FIXTURE 1 -- permission denied (READ side of resolution)
# ===========================================================================
def test_fixture_permission_denied_on_resolution(f):
    """A foreign client cannot resolve, and neither ownership nor a correct
    digest changes that."""
    a, wa = _world(f, "a")
    b, _wb = _world(f, "b")
    art = f.create_artifact(wa, "blob", b"secret", client_id=a)
    with pytest.raises(AccessDenied):
        f.get_artifact_content(wa, art["artifact_id"], client_id=b)
    with pytest.raises(AccessDenied):
        f.get_artifact_content(wa, art["artifact_id"], client_id=b,
                               expected_digest=art["blob_hash"])


def test_fixture_a_digest_alone_never_authorizes(f):
    """THE RULE, stated as a test. Knowing the exact digest of another
    client's artifact yields nothing: the digest is checked AFTER
    authorization and after a world-scoped lookup, so it can only ever say
    WHICH object you meant -- never that you may have it."""
    a, wa = _world(f, "a")
    b, wb = _world(f, "b")
    art = f.create_artifact(wa, "blob", b"secret", client_id=a)
    digest = art["blob_hash"]

    # b knows the digest exactly, and owns a world of its own
    with pytest.raises(AccessDenied):
        f.get_artifact_content(wa, art["artifact_id"], client_id=b,
                               expected_digest=digest)
    # and cannot pull it into its OWN world by naming the digest there
    with pytest.raises(NotFound):
        f.get_artifact_content(wb, art["artifact_id"], client_id=b,
                               expected_digest=digest)


def test_fixture_imported_artifact_still_cannot_be_re_exported(f):
    """PRESERVED, not re-implemented: the H6 rule already forbids A->B->C.
    Resolution must not become a way around it."""
    a = f.create_client("origin")
    b = f.create_client("middle")
    c = f.create_client("third")
    grp = f.create_topology_group(a)
    sa = f.create_session(a, "sa")
    wa = f.create_world(sa, "wa", topology_group=grp,
                        sharing_policy="FULLY_SHARED")["world_id"]
    f.start_world(wa, a)
    sb = f.create_session(b, "sb")
    wb = f.create_world(sb, "wb", topology_group=grp,
                        sharing_policy="FULLY_SHARED")["world_id"]
    f.start_world(wb, b)
    sc = f.create_session(c, "sc")
    wc = f.create_world(sc, "wc", topology_group=grp,
                        sharing_policy="FULLY_SHARED")["world_id"]
    f.start_world(wc, c)

    art = f.create_artifact(wa, "blob", b"shared",
                            meta={"info_kind": "artifact"}, client_id=a)
    imp = f.import_artifact(wb, wa, art["artifact_id"], client_id=b)
    # B can resolve its legally imported copy
    got = f.get_artifact_content(wb, imp["artifact_id"], client_id=b)
    assert got["origin"] == "IMPORTED"
    assert got["resolution"]["visibility_basis"]["visibility"] == "IMPORTED"
    # but C cannot obtain it THROUGH B
    with pytest.raises(AccessDenied):
        f.import_artifact(wc, wb, imp["artifact_id"], client_id=c)


# ===========================================================================
# FIXTURE 2 -- wrong hash (the READ side, which did not exist)
# ===========================================================================
def test_fixture_wrong_hash_on_read_returns_nothing(f):
    c, w = _world(f, "w")
    art = f.create_artifact(w, "blob", b"the real bytes", client_id=c)
    wrong = sha(b"different bytes")
    with pytest.raises(ValidationError) as ei:
        f.get_artifact_content(w, art["artifact_id"], client_id=c,
                               expected_digest=wrong)
    assert "expected digest" in str(ei.value)
    # PAIRED: the right digest resolves, and the engine says it verified it
    ok = f.get_artifact_content(w, art["artifact_id"], client_id=c,
                                expected_digest=art["blob_hash"])
    assert ok["resolution"]["digest_verified"] == art["blob_hash"]
    assert ok["resolution"]["digest_asserted_by_caller"] is True


def test_fixture_read_gate_accepts_the_same_forms_as_the_write_gate(f):
    """The two sides must not disagree about the same string."""
    c, w = _world(f, "w")
    art = f.create_artifact(w, "blob", b"x", client_id=c)
    bare = art["blob_hash"].split(":", 1)[1]
    for form in (art["blob_hash"], bare, bare.upper()):
        got = f.get_artifact_content(w, art["artifact_id"], client_id=c,
                                     expected_digest=form)
        assert got["blob_hash"] == art["blob_hash"]
    with pytest.raises(ValidationError):
        f.get_artifact_content(w, art["artifact_id"], client_id=c,
                               expected_digest="not-a-digest")


def test_fixture_expected_bytes_is_checked_too(f):
    c, w = _world(f, "w")
    art = f.create_artifact(w, "blob", b"12345", client_id=c)
    assert f.get_artifact_content(w, art["artifact_id"], client_id=c,
                                  expected_bytes=5)["bytes"] == 5
    with pytest.raises(ValidationError):
        f.get_artifact_content(w, art["artifact_id"], client_id=c,
                               expected_bytes=6)


# ===========================================================================
# FIXTURE 3 -- double billing refused
# ===========================================================================
def test_fixture_a_settled_reservation_is_never_billed_again(f):
    c, w = _world(f, "w",
                  budget={"cpu_s": {"limit": 100, "enforcement": "enforceable"}})
    res = f.reserve_budget(w, "cpu_s", 10, stage="execution",
                           attempt_id="att-1", client_id=c)
    assert res["state"] == "OPEN"
    ce = f.record_cost_event(
        w, stage="execution", attempt_id="att-1",
        reservation_id=res["reservation_id"],
        resources=[{"resource": "cpu_s", "quantity": 10, "unit": "s",
                    "method": "clock", "scope": "attempt"}], client_id=c)
    assert ce["cost_event_id"].startswith("cost_")
    # the SAME reservation cannot be billed a second time
    with pytest.raises(ConflictError) as ei:
        f.record_cost_event(
            w, stage="execution", reservation_id=res["reservation_id"],
            resources=[{"resource": "cpu_s", "quantity": 10}], client_id=c)
    assert "never billed again" in str(ei.value)
    assert f.budget_status(w)["consumed"]["cpu_s"] == 10


def test_fixture_a_retried_charge_with_a_key_bills_once(f):
    """consume_budget took no idempotency key, so a timeout retry
    double-billed with no way for the caller to prevent it."""
    c, w = _world(f, "w",
                  budget={"calls": {"limit": 10, "enforcement": "enforceable"}})
    for _ in range(4):
        f.consume_budget(w, "calls", 1, client_id=c, idem_key="charge-1",
                         request_hash="h1")
    assert f.budget_status(w)["consumed"]["calls"] == 1
    # PAIRED: without a key the engine cannot tell them apart, and says so by
    # billing each one
    for _ in range(3):
        f.consume_budget(w, "calls", 1, client_id=c)
    assert f.budget_status(w)["consumed"]["calls"] == 4


def test_fixture_a_negative_charge_is_refused(f):
    """It used to walk the counter back down and could clear an exhaustion."""
    c, w = _world(f, "w",
                  budget={"calls": {"limit": 5, "enforcement": "enforceable"}})
    f.consume_budget(w, "calls", 5, client_id=c)
    with pytest.raises(ValidationError) as ei:
        f.consume_budget(w, "calls", -5, client_id=c)
    assert "never negative" in str(ei.value)
    assert f.budget_status(w)["consumed"]["calls"] == 5
    with pytest.raises(BudgetExhausted):
        f.consume_budget(w, "calls", 1, client_id=c)


# ===========================================================================
# FIXTURE 4 -- fork budget not multiplied (reservations included)
# ===========================================================================
def test_fixture_a_fork_cannot_multiply_a_reservation_allowance(f):
    """The existing test proves SPENDING cannot escape the lineage root. This
    proves RESERVING cannot either -- a reservation held only on the local row
    would have been exactly the escape hatch."""
    c, w = _world(f, "parent",
                  budget={"cpu_s": {"limit": 10, "enforcement": "enforceable"}})
    ck = f.checkpoint(w, client_id=c)["checkpoint_id"]
    kids = f.fork(w, ck, [{"name": "k1"}, {"name": "k2"}], client_id=c)
    k1, k2 = kids[0]["world_id"], kids[1]["world_id"]
    for k in (k1, k2):
        f.start_world(k, c)
        assert f.budget_status(k)["budget_root"] == w

    f.reserve_budget(k1, "cpu_s", 8, stage="execution", client_id=c)
    # the lineage root has 8 of 10 spoken for; the sibling cannot reserve 5
    with pytest.raises(BudgetExhausted):
        f.reserve_budget(k2, "cpu_s", 5, stage="execution", client_id=c)
    # nor can the parent
    with pytest.raises(BudgetExhausted):
        f.reserve_budget(w, "cpu_s", 5, stage="execution", client_id=c)
    # and 2 still fits, at either scope
    assert f.reserve_budget(k2, "cpu_s", 2, stage="execution",
                            client_id=c)["state"] == "OPEN"


def test_fixture_releasing_returns_the_allowance_to_the_whole_lineage(f):
    c, w = _world(f, "parent",
                  budget={"cpu_s": {"limit": 10, "enforcement": "enforceable"}})
    ck = f.checkpoint(w, client_id=c)["checkpoint_id"]
    k = f.fork(w, ck, [{"name": "k"}], client_id=c)[0]["world_id"]
    f.start_world(k, c)
    res = f.reserve_budget(k, "cpu_s", 9, stage="execution", client_id=c)
    with pytest.raises(BudgetExhausted):
        f.reserve_budget(w, "cpu_s", 5, stage="execution", client_id=c)
    f.release_budget(res["reservation_id"], reason="job never started",
                     client_id=c)
    assert f.reserve_budget(w, "cpu_s", 5, stage="execution",
                            client_id=c)["state"] == "OPEN"
    # releasing twice does not credit twice
    again = f.release_budget(res["reservation_id"], reason="again",
                             client_id=c)
    assert again["state"] == "RELEASED"
    assert f.budget_status(w)["consumed"]["cpu_s"] == 5


def test_fixture_reserve_is_idempotent_on_its_key(f):
    c, w = _world(f, "w",
                  budget={"cpu_s": {"limit": 10, "enforcement": "enforceable"}})
    a = f.reserve_budget(w, "cpu_s", 4, stage="execution", idem_key="r1",
                         client_id=c)
    b = f.reserve_budget(w, "cpu_s", 4, stage="execution", idem_key="r1",
                         client_id=c)
    assert b["reservation_id"] == a["reservation_id"]
    assert b["already_reserved"] is True
    assert f.budget_status(w)["consumed"]["cpu_s"] == 4


# ===========================================================================
# FIXTURE 5 -- oversized artifact refused at the configured limit
# ===========================================================================
def test_fixture_oversized_artifact_refused_on_write(tmp_path):
    g = Foundry(str(tmp_path / "s.db"), max_artifact_bytes=1024)
    c, w = _world(g, "w")
    with pytest.raises(ValidationError) as ei:
        g.create_artifact(w, "blob", b"x" * 2048, client_id=c)
    assert "size limit" in str(ei.value)
    # PAIRED: at the limit it is accepted
    ok = g.create_artifact(w, "blob", b"x" * 1024, client_id=c)
    assert ok["blob_hash"] == sha(b"x" * 1024)
    g.close()


def test_fixture_oversized_artifact_refused_on_read(tmp_path):
    """A blob stored under a looser ceiling must not become unreadable-but-
    served when the ceiling tightens: resolution refuses it too."""
    p = str(tmp_path / "s.db")
    big = Foundry(p, max_artifact_bytes=8192)
    c, w = _world(big, "w")
    art = big.create_artifact(w, "blob", b"y" * 4096, client_id=c)
    big.close()

    tight = Foundry(p, max_artifact_bytes=1024)
    with pytest.raises(ValidationError) as ei:
        tight.get_artifact_content(w, art["artifact_id"], client_id=c)
    assert "size limit" in str(ei.value)
    tight.close()


def test_fixture_a_caller_may_tighten_the_ceiling_but_never_loosen_it(tmp_path):
    g = Foundry(str(tmp_path / "s.db"), max_artifact_bytes=4096)
    c, w = _world(g, "w")
    art = g.create_artifact(w, "blob", b"z" * 2048, client_id=c)
    with pytest.raises(ValidationError):
        g.get_artifact_content(w, art["artifact_id"], client_id=c,
                               max_bytes=1024)          # tighter: refused
    got = g.get_artifact_content(w, art["artifact_id"], client_id=c,
                                 max_bytes=10 ** 9)     # looser: ignored
    assert got["resolution"]["size_limit_applied"] == 4096
    g.close()


def test_the_engine_has_a_default_ceiling_at_all(f):
    """There was none before v8, which is why 'check the configured limit' had
    nothing to check against."""
    assert f.max_artifact_bytes == DEFAULT_MAX_ARTIFACT_BYTES == 16 * 1024 * 1024


# ===========================================================================
# Cost-event semantics
# ===========================================================================
def test_unavailable_is_not_zero(f):
    c, w = _world(f, "w")
    ce = f.record_cost_event(
        w, stage="execution",
        resources=[{"resource": "cpu_s", "quantity": 3, "unit": "s",
                    "method": "clock"},
                   {"resource": "gpu_s", "quantity": None, "method": "declared"}],
        client_id=c)
    gpu = [e for e in ce["resources"] if e["resource"] == "gpu_s"][0]
    assert gpu["quantity"] is None and gpu["available"] is False
    rep = f.cost_report(w, client_id=c)
    assert "gpu_s" not in rep["additive_totals"], \
        "an unavailable measurement must never be summed as zero"
    assert rep["unavailable_counts"]["gpu_s"] == 1
    assert rep["additive_totals"]["cpu_s"] == 3


def test_peaks_are_maxima_never_sums(f):
    c, w = _world(f, "w")
    for q in (100, 400, 250):
        f.record_cost_event(w, stage="execution",
                            resources=[{"resource": "peak_memory_bytes",
                                        "quantity": q, "method": "sampler"}],
                            client_id=c)
    rep = f.cost_report(w, client_id=c)
    assert rep["peaks"]["peak_memory_bytes"] == 400
    assert "peak_memory_bytes" not in rep["additive_totals"]


def test_the_enforcement_class_comes_from_the_limit_not_the_caller(f):
    """A caller that could name its own class could opt out of a cap it was
    given. The vector has no enforcement field at all; the engine resolves it."""
    c, w = _world(f, "w",
                  budget={"cpu_s": {"limit": 5, "enforcement": "enforceable"},
                          "wall_s": {"limit": None,
                                     "enforcement": "unavailable"}})
    with pytest.raises(ValidationError):
        f.record_cost_event(w, stage="execution",
                            resources=[{"resource": "cpu_s", "quantity": 1,
                                        "enforcement": "measured"}],
                            client_id=c)
    ce = f.record_cost_event(
        w, stage="execution",
        resources=[{"resource": "cpu_s", "quantity": 1},
                   {"resource": "wall_s", "quantity": 2}], client_id=c)
    got = {e["resource"]: e["enforcement"] for e in ce["resources"]}
    assert got == {"cpu_s": "enforceable", "wall_s": "unavailable"}
    # and the enforceable one really did block when exceeded
    with pytest.raises(BudgetExhausted):
        f.record_cost_event(w, stage="execution",
                            resources=[{"resource": "cpu_s", "quantity": 99}],
                            client_id=c)


def test_settlement_reconciles_against_the_reservation(f):
    """Reserve high, spend low: the difference comes back. Reserve low, spend
    high: the difference is charged, and refused if it does not fit."""
    c, w = _world(f, "w",
                  budget={"cpu_s": {"limit": 100, "enforcement": "enforceable"}})
    r1 = f.reserve_budget(w, "cpu_s", 20, stage="execution", client_id=c)
    f.record_cost_event(w, stage="execution", reservation_id=r1["reservation_id"],
                        resources=[{"resource": "cpu_s", "quantity": 5}],
                        client_id=c)
    assert f.budget_status(w)["consumed"]["cpu_s"] == 5      # 20 reserved -> 5

    r2 = f.reserve_budget(w, "cpu_s", 10, stage="execution", client_id=c)
    f.record_cost_event(w, stage="execution", reservation_id=r2["reservation_id"],
                        resources=[{"resource": "cpu_s", "quantity": 30}],
                        client_id=c)
    assert f.budget_status(w)["consumed"]["cpu_s"] == 35     # 5 + 30

    r3 = f.reserve_budget(w, "cpu_s", 1, stage="execution", client_id=c)
    with pytest.raises(BudgetExhausted):
        f.record_cost_event(w, stage="execution",
                            reservation_id=r3["reservation_id"],
                            resources=[{"resource": "cpu_s", "quantity": 500}],
                            client_id=c)


def test_a_reservation_is_taken_BEFORE_the_operation(f):
    """The whole point: an enforceable limit stops the operation before it
    starts. A post-hoc debit is not enforcement."""
    c, w = _world(f, "w",
                  budget={"cpu_s": {"limit": 10, "enforcement": "enforceable"}})
    with pytest.raises(BudgetExhausted) as ei:
        f.reserve_budget(w, "cpu_s", 11, stage="execution", client_id=c)
    assert "BEFORE the operation" in str(ei.value)
    assert f.budget_status(w)["consumed"].get("cpu_s", 0) == 0


def test_closed_vocabularies_fail_closed(f):
    c, w = _world(f, "w")
    with pytest.raises(ValidationError):
        f.record_cost_event(w, stage="wishing",
                            resources=[{"resource": "cpu_s", "quantity": 1}],
                            client_id=c)
    with pytest.raises(ValidationError):
        f.record_cost_event(w, stage="execution",
                            resources=[{"resource": "cpu_s", "quantity": 1,
                                        "method": "vibes"}], client_id=c)
    with pytest.raises(ValidationError):
        f.record_cost_event(w, stage="execution",
                            resources=[{"resource": "cpu_s", "quantity": -1}],
                            client_id=c)
    with pytest.raises(ValidationError):
        f.record_cost_event(w, stage="execution", resources=[], client_id=c)


# ===========================================================================
# THE END-TO-END RECEIPT
# ===========================================================================
def test_end_to_end_producer_artifact_resolved_by_reader_and_charged_once(f):
    """One producer-created artifact, resolved by an authorized reader against
    its sealed digest, charged exactly once, with every identifier real."""
    c, w = _world(f, "e2e",
                  budget={"cpu_s": {"limit": 60, "enforcement": "enforceable"},
                          "retrieval_calls": {"limit": 100,
                                              "enforcement": "enforceable"}})
    payload = b'{"inputs": [[0,0],[0,1],[1,0],[1,1]]}'
    digest = sha(payload)

    # PRODUCE, with the write-side gate asserting the identity
    art = f.create_artifact(w, "failure_input_set", payload,
                            meta={"info_kind": "artifact",
                                  "interface_id": "boolean-inputs-v1"},
                            expected_blob_hash=digest, client_id=c)
    assert art["blob_hash"] == digest

    # RESERVE before the read
    res = f.reserve_budget(w, "retrieval_calls", 1, stage="retrieval",
                           attempt_id="attempt-e2e", idem_key="e2e-retrieval",
                           client_id=c)

    # RESOLVE, asserting digest and size at the engine's gate
    got = f.get_artifact_content(w, art["artifact_id"], client_id=c,
                                 expected_digest=digest,
                                 expected_bytes=len(payload))
    assert got["resolution"]["digest_verified"] == digest
    assert got["resolution"]["authorization"] == "owner"

    # SETTLE, once
    ce = f.record_cost_event(
        w, stage="retrieval", attempt_id="attempt-e2e",
        reservation_id=res["reservation_id"],
        source_artifacts=[digest],
        resources=[{"resource": "retrieval_calls", "quantity": 1,
                    "unit": "calls", "method": "counter", "scope": "attempt"},
                   {"resource": "cpu_s", "quantity": 0.01, "unit": "s",
                    "method": "clock", "scope": "attempt"},
                   {"resource": "gpu_s", "quantity": None,
                    "method": "declared", "scope": "attempt"}],
        environment={"stratum": "cpu-only", "host": "test"}, client_id=c)

    # CHARGED ONCE
    st = f.budget_status(w)
    assert st["consumed"]["retrieval_calls"] == 1
    with pytest.raises(ConflictError):
        f.record_cost_event(w, stage="retrieval",
                            reservation_id=res["reservation_id"],
                            resources=[{"resource": "retrieval_calls",
                                        "quantity": 1}], client_id=c)
    assert f.budget_status(w)["consumed"]["retrieval_calls"] == 1

    # SEALED, and readable back
    back = f.get_cost_event(ce["cost_event_id"], client_id=c)
    assert back["sealed"]["cost_event_id"] == ce["cost_event_id"]
    assert back["entry_hash"] == ce["entry_hash"]
    assert digest in back["artifacts"], "the source artifact is in the seal"
    rep = f.cost_report(w, client_id=c)
    assert rep["additive_totals"]["retrieval_calls"] == 1
    assert rep["unavailable_counts"]["gpu_s"] == 1
    assert rep["open_reservations"] == []
    assert f.verify_world(w, client_id=c)["ok"] is True


# ===========================================================================
# TRACK A part 1 -- the engine-issued principal, and one name for one field
# ===========================================================================
def test_the_read_path_accepts_the_write_paths_name(f):
    """expected_blob_hash is the write path's name. Having a second name on
    the read path for the same field is exactly what trips a headless
    consumer, so the read path takes it too; expected_digest stays as the
    shipped alias."""
    c, w = _world(f, "w")
    art = f.create_artifact(w, "blob", b"payload", client_id=c)
    for kw in ({"expected_blob_hash": art["blob_hash"]},
               {"expected_digest": art["blob_hash"]}):
        got = f.get_artifact_content(w, art["artifact_id"], client_id=c, **kw)
        assert got["resolution"]["digest_asserted_by_caller"] is True
    for kw in ({"expected_blob_hash": sha(b"other")},
               {"expected_digest": sha(b"other")}):
        with pytest.raises(ValidationError):
            f.get_artifact_content(w, art["artifact_id"], client_id=c, **kw)


def test_the_client_retains_the_engine_issued_principal(tmp_path):
    """register() returned the token and threw the client_id away, so a caller
    that needed to be NAMED -- granted read on a scope, attributed in a cost
    event, reconciled in a receipt -- had nothing to say. There is no
    /v2/clients/me route, so it is RETAINED, never reconstructed."""
    import sys as _sys
    _sys.path.insert(0, os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), "SerendipityFoundryClient"))
    from fastapi.testclient import TestClient
    from sfclient.client import EngineClient
    from sfe.api import create_app

    app = TestClient(create_app(str(tmp_path / "p.db")))
    issued = app.post("/v2/clients", json={"name": "trackA"}).json()

    ec = EngineClient("http://x", token=issued["token"],
                      client_id=issued["client_id"])
    assert ec.client_id == issued["client_id"]

    # a client built from a BARE TOKEN knows it does not know who it is, and
    # says so rather than deriving a substitute principal
    bare = EngineClient("http://x", token=issued["token"])
    assert bare.client_id is None

    # and the credential never appears in the object's own repr
    r = repr(ec)
    assert issued["token"] not in r
    assert issued["client_id"] in r
    assert "authenticated=True" in r
