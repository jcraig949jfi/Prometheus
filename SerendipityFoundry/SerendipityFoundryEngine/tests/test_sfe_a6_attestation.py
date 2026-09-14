"""A6 acceptance: the thirteen rows of 2026-09-11, reproduced.

WRITTEN BEFORE THE IMPLEMENTATION, on the operator's instruction (2026-09-11).
Half of it passed then as live evidence that the gap was real; the other half
was `xfail(strict=True)` as the acceptance criterion. A6 LANDED 2026-09-12
(sfe/attestation.py, wired in the api middleware): the markers are gone and
the same assertions are now regressions. The wiring and the epistemic rule
(UNKNOWN stays UNKNOWN until independently reconciled) are covered in
tests/test_sfe_a6_wiring_and_health.py.

THE FAILURE THIS ENCODES. On 2026-09-11 a seventeen-minute engine stall cost 13
rows of `cs-h5-1` arm `map`, rules 143-155. Two systems each saw part of it and
NEITHER could attest what happened:

  * the engine could not record its own lock failure, because recording needs
    the lock that just failed (A6); and
  * the producer's register recorded 13 failed rows with NO failure class,
    because the failure landed inside a window where the class had not been
    decided yet.

So for thirteen rows there was no authoritative record on either side. The truth
was recovered only by a human joining two records by hand -- and the first
attempt got it wrong, reporting all 13 as `create_world` because a frame-matching
pattern also matched Python's own `http/client.py`.

THE THREE SHAPES, verified against the live ledger (Vivarium,
roles/Archaeon/INBOX_VIVARIUM_H5_MAP_GAP_CORRECTION_2026-09-11.md):

    rules 147-154 (8)   died at create_world          NO effect in the ledger
    rule  146     (1)   commit call TIMED OUT         effect PRESENT -- it landed
    rules 143-145,155(4) died at audit_envelope       effect PRESENT

RULE 146 IS THE CANONICAL WRITE-TIMEOUT CASE and the reason "did the client see
an error" can never stand in for "did the write happen". A timeout means the
outcome is UNKNOWN. It must be reconciled before any retry, and never assumed
to have failed.
"""
import os
import sqlite3
import sys
import threading
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sfe.runtime import Foundry                                   # noqa: E402
from sfe.store import Store                                       # noqa: E402

#: The incident, exactly as filed. (rule, shape, effect_expected_in_ledger)
THE_THIRTEEN = (
    [(r, "create_world", False) for r in range(147, 155)] +        # 8
    [(146, "commit_timeout", True)] +                              # 1
    [(r, "post_commit_step", True) for r in (143, 144, 145, 155)]  # 4
)


@pytest.fixture
def eng(tmp_path):
    f = Foundry(str(tmp_path / "a6.db"))
    yield f
    f.close()


def _world(f, name):
    c = f.create_client(name + "-c")
    s = f.create_session(c, name + "-s")
    w = f.create_world(s, name)["world_id"]
    f.start_world(w, c)
    return c, w


def test_the_incident_is_thirteen_rows_in_three_shapes():
    """The fixture is the incident, not a paraphrase of it."""
    assert len(THE_THIRTEEN) == 13
    by_shape = {}
    for _r, shape, _e in THE_THIRTEEN:
        by_shape[shape] = by_shape.get(shape, 0) + 1
    assert by_shape == {"create_world": 8, "commit_timeout": 1,
                        "post_commit_step": 4}
    # and the gap is CONTIGUOUS -- which is what made it readable as a fact
    # about rule space rather than as an instrument failure
    rules = sorted(r for r, _s, _e in THE_THIRTEEN)
    assert rules == list(range(143, 156))
    assert rules[-1] - rules[0] + 1 == len(rules)


# ===========================================================================
# LIVE EVIDENCE THAT THE GAP IS REAL. These pass today.
# ===========================================================================
def test_a_lock_timeout_writes_NOTHING_to_the_ledger(tmp_path):
    """Shape 1 (8 rows). The engine refuses, and the refusal leaves no trace.

    This is A6 in one assertion: the hash chain is silent precisely when the
    engine is the thing that failed.
    """
    db = str(tmp_path / "lock.db")
    holder_up = threading.Event()
    release = threading.Event()

    def holder():
        h = Store(db)
        h.initialize()
        with h.write() as cx:
            cx.execute("SELECT 1")
            holder_up.set()
            release.wait(30)

    threading.Thread(target=holder, daemon=True).start()
    holder_up.wait(10)

    victim = Store(db)
    victim.initialize()
    victim._conn.execute("PRAGMA busy_timeout=700")     # a 30s wait, compressed
    before = victim._conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    with pytest.raises(sqlite3.OperationalError) as ei:
        with victim.write() as cx:
            cx.execute("SELECT 1")
    assert "locked" in str(ei.value)
    after = victim._conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    release.set()

    assert after == before, (
        "the refusal wrote something -- if it ever does, A6 is already closed")


def test_the_engine_has_exactly_one_channel_that_survives_a_failed_lock(eng):
    """The constraint that shaped the design: every durable record the engine
    kept went through `store.write()`, the thing that failed. Until A6 landed
    this test asserted NO non-SQLite sink existed in sfe/. A6 IS that sink,
    and it must be the only one -- a second one would be a second place for
    the truth to live.

    (Flipped 2026-09-12 when sfe/attestation.py landed; the old assertion is
    kept as the complement: every other module is still ledger-only.)"""
    src = open(os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "sfe", "runtime.py"),
        encoding="utf-8").read()
    assert "events.append" in src
    assert "with self.store.write()" in src
    sfe_dir = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "sfe")
    sinks = []
    for n in sorted(p for p in os.listdir(sfe_dir) if p.endswith(".py")):
        body = open(os.path.join(sfe_dir, n), encoding="utf-8").read()
        if "open(" in body and "blobs" not in body and n != "store.py":
            sinks.append(n)
    assert sinks == ["attestation.py"], (
        "the only non-ledger durable sink must be the A6 journal: %s" % sinks)


def test_a_committed_effect_is_indistinguishable_from_an_abandoned_one(eng):
    """Shapes 2 and 3 (5 rows). After the fact the ledger shows a committed
    experiment with no observation -- and cannot say whether the run died or is
    still coming. That is why orphaned_commits.py reports and does not
    classify."""
    c, w = _world(eng, "shape23")
    e = eng.create_experiment(w, {"spec_version": 1, "rule": 146}, client_id=c)
    exp = e["exp_id"] if isinstance(e, dict) else e
    eng.commit_experiment(w, exp, client_id=c)

    cx = eng.store.read()
    committed = cx.execute(
        "SELECT committed_seq FROM experiments WHERE exp_id=?",
        (exp,)).fetchone()["committed_seq"]
    obs = cx.execute("SELECT COUNT(*) FROM observations WHERE exp_id=?",
                     (exp,)).fetchone()[0]
    assert committed is not None and obs == 0

    # NOTHING in the ledger distinguishes "the client died after this" from
    # "the observation is still coming". Both are exactly this state.
    assert True, "the point is that there is no third field to assert on"


# ===========================================================================
# ACCEPTANCE. What A6 made true on 2026-09-12; regressions from here.
# ===========================================================================
@pytest.mark.parametrize("rule,shape,effect", THE_THIRTEEN)
def test_A6_every_one_of_the_thirteen_is_attestable(rule, shape, effect,
                                                    tmp_path):
    """THE ACCEPTANCE CRITERION, one case per row.

    After A6, for each of the thirteen there must exist a durable record --
    written WITHOUT the ledger's write lock -- from which a later reader can
    answer, without a human joining two systems by hand:

        did the attempt reach the engine?      (intent)
        did it take effect?                    (outcome, or reconciliation)
        if unknown, is it RECONCILABLE?        (and against what)

    `effect` is the ground truth from the live ledger: False for the eight that
    died at create_world, True for the five that committed.
    """
    from sfe import attestation                     # noqa: PLC0415  -- A6
    j = attestation.Journal(str(tmp_path / "incidents"))
    rid = j.intent(route="POST /v2/worlds", client="viv", idem_key="r%d" % rule)
    if shape == "create_world":
        j.refused(rid, reason="lock timeout")
    else:
        j.effected(rid, kind="experiment", ref="exp_%d" % rule)
        if shape == "commit_timeout":
            pass                                   # client never saw the reply
    verdict = j.attest(rid)
    assert verdict["reached_engine"] is True
    assert verdict["took_effect"] is effect
    assert verdict["state"] in ("CONFIRMED_EFFECT", "CONFIRMED_NO_EFFECT")


def test_A6_a_timeout_never_reports_the_write_as_failed(tmp_path):
    """RULE 146, the canonical case. The client timed out ON the commit and the
    commit had landed. An attestation that reported 'failed' because the caller
    saw an error would be wrong in the one case it exists for.

    UNKNOWN is a permitted verdict. 'Failed' is not, without evidence.
    """
    from sfe import attestation                     # noqa: PLC0415
    j = attestation.Journal(str(tmp_path / "incidents"))
    rid = j.intent(route="POST /v2/worlds/{w}/experiments", client="viv",
                   idem_key="rule-146")
    # the effect landed; the process died before recording the outcome
    verdict = j.attest(rid, ledger_has_effect=True)
    assert verdict["state"] == "CONFIRMED_EFFECT"
    assert verdict["took_effect"] is True
    verdict_unknown = j.attest(rid, ledger_has_effect=None)
    assert verdict_unknown["state"] == "UNKNOWN_RECONCILABLE"
    assert verdict_unknown["took_effect"] is None, \
        "a timeout must never be reported as a failed write"


def test_A6_the_channel_fails_OPEN(tmp_path):
    """If the incident channel cannot be written, the request must still be
    served. An attestation mechanism that can take the engine down has made
    availability worse in exchange for evidence."""
    from sfe import attestation                     # noqa: PLC0415
    j = attestation.Journal("/nonexistent/path/that/cannot/be/created")
    rid = j.intent(route="POST /v2/worlds", client="viv", idem_key="k")
    assert rid is not None
    assert j.degraded is True, (
        "the journal must say it is degraded rather than raise")
