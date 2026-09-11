"""Classifying an experiment the engine committed and nobody observed.

WHY THE VERDICT IS THIS SEAT'S. Daedalus's `deploy/orphaned_commits.py` finds
the scar -- committed, unobserved -- and their first cut classified it on
whether the world still held outstanding work. That returned all five runs I
had already confirmed abandoned as "pending", because every one of those worlds
still holds a QUEUED work item nobody will ever claim. Holding work is not
evidence of progress. They made the scan report-only and handed the verdict
here, which is right: whether a queued item will ever be claimed is a fact
about this register.

THE PENDING TESTS ARE THE POINT. A classifier that only ever says ABANDONED has
not been shown to detect anything, and it would be the same failure as theirs
with the sign flipped.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

VIVARIUM = Path(__file__).resolve().parent.parent
if str(VIVARIUM) not in sys.path:
    sys.path.insert(0, str(VIVARIUM))

from viv import queue as _q                                    # noqa: E402
from viv import spec as _spec                                  # noqa: E402
from viv import stalls                                         # noqa: E402

from conftest import make_spec                                 # noqa: E402


def _admit(conn, schema, **kw):
    sp = make_spec(**{k: v for k, v in kw.items()
                      if k in ("bits", "seed_root", "kind")})
    eid = _q.enqueue(conn, created_by="test", source_reason="orphan-verdicts",
                     experiment_spec=sp,
                     arm_id=kw.get("arm_id"),
                     candidate_set_id=kw.get("candidate_set_id"),
                     status=kw.get("status", "queued"), schema=schema)
    conn.commit()
    return eid, _spec.spec_hash(sp)


def _run_to(conn, schema, eid, end, *, sfe_experiment_id=None):
    """Drive a row to a terminal state through the real transitions."""
    _q.claim_next(conn, "w1", schema=schema)
    _q.mark_running(conn, eid, worker_id="w1",
                    sfe_experiment_id=sfe_experiment_id, schema=schema)
    if end == "completed":
        _q.mark_completed(conn, eid, worker_id="w1",
                          result_summary={"ok": True},
                          sfe_experiment_id=sfe_experiment_id, schema=schema)
    else:
        _q.mark_failed(conn, eid, worker_id="w1", error="TimeoutError: boom",
                       schema=schema)
    conn.commit()


def _orphan(spec_hash, exp_id="exp_deadbeef", world="wld_1", **kw):
    d = {"exp_id": exp_id, "world_id": world, "spec_hash": spec_hash,
         "age_hours": 1.0, "created": "2026-09-11T00:00:00",
         "outstanding_work": [{"status": "QUEUED", "claimed_by": None,
                               "idle_hours": 1.0}],
         "unclaimed_work": 1}
    d.update(kw)
    return d


def _verdict(r):
    return r["verdicts"][0]["verdict"]


# ===========================================================================
# It says ABANDONED -- and says it about the STATE MACHINE, not a likelihood
# ===========================================================================

def test_a_terminal_failed_row_means_abandoned(conn, schema):
    eid, sh = _admit(conn, schema, bits="1" * 8, kind="evaluate_bitstring")
    _run_to(conn, schema, eid, "failed")
    r = stalls.classify_orphans([_orphan(sh)], conn, schema=schema)
    assert _verdict(r) == stalls.ABANDONED
    assert r["counts"] == {stalls.ABANDONED: 1}


def test_abandoned_holds_even_though_the_world_still_has_queued_work(conn,
                                                                    schema):
    """The exact case that broke the first classifier. The orphan reports an
    unclaimed QUEUED work item idling -- and the answer is still abandoned,
    because the register's row for that spec is terminal."""
    eid, sh = _admit(conn, schema, bits="0" * 8, kind="evaluate_bitstring")
    _run_to(conn, schema, eid, "failed")
    o = _orphan(sh, unclaimed_work=1,
                outstanding_work=[{"status": "QUEUED", "claimed_by": None,
                                   "idle_hours": 0.9}])
    r = stalls.classify_orphans([o], conn, schema=schema)
    assert _verdict(r) == stalls.ABANDONED
    assert "terminal" in r["verdicts"][0]["why"]


def test_a_cancelled_row_is_also_terminal(conn, schema):
    eid, sh = _admit(conn, schema, bits="01" * 4, kind="evaluate_bitstring")
    _q.cancel(conn, eid, actor="test", reason="unchosen", schema=schema)
    conn.commit()
    r = stalls.classify_orphans([_orphan(sh)], conn, schema=schema)
    assert _verdict(r) == stalls.ABANDONED


def test_a_completed_row_naming_a_DIFFERENT_experiment_is_a_rerun(conn, schema):
    """Two rows, one spec: the first was orphaned, the spec was re-run. Seen
    twice in the real scan (cs-c3-2 -> cs-c3-2-r1)."""
    e1, sh = _admit(conn, schema, bits="11" * 4, kind="evaluate_bitstring")
    _run_to(conn, schema, e1, "failed")
    e2, sh2 = _admit(conn, schema, bits="11" * 4, kind="evaluate_bitstring")
    assert sh2 == sh, "byte-identical specs must seal identically"
    _run_to(conn, schema, e2, "completed", sfe_experiment_id="exp_the_rerun")
    r = stalls.classify_orphans([_orphan(sh, exp_id="exp_the_orphan")], conn,
                                schema=schema)
    assert _verdict(r) == stalls.ABANDONED
    assert "re-run" in r["verdicts"][0]["why"]


# ===========================================================================
# It says PENDING -- the half that makes ABANDONED mean something
# ===========================================================================

def test_a_queued_row_means_pending(conn, schema):
    _eid, sh = _admit(conn, schema, bits="1010" * 2, kind="evaluate_bitstring")
    r = stalls.classify_orphans([_orphan(sh)], conn, schema=schema)
    assert _verdict(r) == stalls.PENDING


def test_a_running_row_means_pending(conn, schema):
    eid, sh = _admit(conn, schema, bits="0101" * 2, kind="evaluate_bitstring")
    _q.claim_next(conn, "w1", schema=schema)
    _q.mark_running(conn, eid, worker_id="w1", schema=schema)
    conn.commit()
    r = stalls.classify_orphans([_orphan(sh)], conn, schema=schema)
    assert _verdict(r) == stalls.PENDING


def test_one_live_row_among_terminal_ones_is_enough(conn, schema):
    """A spec re-admitted after a failure is pending, not abandoned. Deciding
    on ANY row rather than the newest keeps this from depending on a
    timestamp ordering the register does not guarantee."""
    e1, sh = _admit(conn, schema, bits="1100" * 2, kind="evaluate_bitstring")
    _run_to(conn, schema, e1, "failed")
    _admit(conn, schema, bits="1100" * 2, kind="evaluate_bitstring")
    r = stalls.classify_orphans([_orphan(sh)], conn, schema=schema)
    assert _verdict(r) == stalls.PENDING


# ===========================================================================
# The boundary, and the verdict about myself
# ===========================================================================

def test_a_spec_no_row_seals_is_not_this_registers_to_judge(conn, schema):
    r = stalls.classify_orphans([_orphan("sha256:" + "f" * 64)], conn,
                                schema=schema)
    assert _verdict(r) == stalls.NOT_OURS


def test_a_viv_named_world_with_no_row_is_MINE_and_unregistered(conn, schema):
    """7 of these were real: `evaluate_bitstring` and `noop_v0` runs from
    2026-09-06 executed straight against the engine with no queue row. Folding
    them into NOT_FROM_THIS_REGISTER would file my own unaccountable writes
    under someone else's problem."""
    sh = "sha256:" + "a" * 64
    o = _orphan(sh, world="wld_x")
    r = stalls.classify_orphans([o], conn, schema=schema,
                                world_names={"wld_x": _spec.world_name(sh)})
    assert _verdict(r) == stalls.UNREGISTERED


def test_a_foreign_world_name_stays_NOT_OURS(conn, schema):
    sh = "sha256:" + "b" * 64
    o = _orphan(sh, world="wld_y")
    r = stalls.classify_orphans([o], conn, schema=schema,
                                world_names={"wld_y": "v6live-primary-3"})
    assert _verdict(r) == stalls.NOT_OURS
    assert r["world_names_supplied"] is True


def test_without_world_names_the_two_cannot_be_separated_and_it_says_so(
        conn, schema):
    r = stalls.classify_orphans([_orphan("sha256:" + "c" * 64)], conn,
                                schema=schema)
    assert r["world_names_supplied"] is False
    assert "without world_names" in r["verdicts"][0]["why"]


def test_a_completed_row_naming_THIS_experiment_is_inconsistent(conn, schema):
    """The register says completed; the ledger holds no observation. Neither
    record is self-evidently wrong, so this is not quietly called abandoned."""
    eid, sh = _admit(conn, schema, bits="1" * 6, kind="evaluate_bitstring")
    _run_to(conn, schema, eid, "completed", sfe_experiment_id="exp_same")
    r = stalls.classify_orphans([_orphan(sh, exp_id="exp_same")], conn,
                                schema=schema)
    assert _verdict(r) == stalls.INCONSISTENT


def test_an_empty_scan_classifies_to_nothing(conn, schema):
    r = stalls.classify_orphans([], conn, schema=schema)
    assert r["n"] == 0 and r["counts"] == {}


# ===========================================================================
# The frame reader, which has now been wrong twice
# ===========================================================================

H5_TRACE = (
    'Traceback (most recent call last):\n'
    '  File "F:\\Prometheus-worktrees\\vivarium-consumer\\vivarium\\viv\\'
    'loop.py", line 1, in dispatch\n'
    '  File "F:\\Prometheus-worktrees\\vivarium-consumer\\vivarium\\viv\\'
    'runner.py", line 2, in run\n'
    '  File "F:\\Prometheus-worktrees\\vivarium-consumer\\vivarium\\viv\\'
    'runner.py", line 3, in audit_envelope\n'
    '  File "F:\\x\\SerendipityFoundryClient\\sfclient\\client.py", '
    'line 4, in _req\n'
    '  File "H:\\Python312\\Lib\\http\\client.py", line 5, in getresponse\n'
    '  File "H:\\Python312\\Lib\\http\\client.py", line 6, in begin\n'
    '  File "H:\\Python312\\Lib\\http\\client.py", line 7, in _read_status\n'
    'TimeoutError: The read operation timed out\n')


def test_the_failing_call_is_the_one_that_names_the_operation():
    """`_req` says "an HTTP request". `audit_envelope` says the run had
    ALREADY COMMITTED. The first version of this reported `begin` -- an
    http.client internal -- and the second reported `_req`."""
    assert stalls._failing_call(H5_TRACE) == "audit_envelope"


def test_a_public_client_frame_still_wins():
    t = H5_TRACE.replace("in _req", "in create_world")
    assert stalls._failing_call(t) == "create_world"


def test_an_executor_rejection_is_not_an_engine_failure():
    """24 of the 33 abandoned orphans died like this -- the kind refused the
    payload AFTER the commit. Reading them as stall casualties would have
    invented a stall that never happened."""
    e = ("EXECUTOR_ERROR: executor raised: ic_density_set must be a "
         "non-empty list")
    assert stalls._shape(e) is None
