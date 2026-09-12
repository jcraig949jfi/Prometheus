"""B1 recurrence: new eligible owner worlds become readable to the grantee
without anyone remembering to run a command (viv/scope.py; operator,
2026-09-12 "make new fossils stay visible").

Engine-level tests run against an IN-PROCESS Foundry (sfe.runtime), the same
fixture shape Daedalus's tool tests use, so the engine's own scope semantics
are exercised -- owner-only membership, INSERT OR IGNORE, granted read -- and
nothing reaches the production engine.

  POSITIVE     create an eligible owner world -> reconcile -> the grantee's
               read_worlds sees it.
  NEGATIVE     a foreign-owned world named viv-* is never added (the owner
               never lists it; the engine would refuse it anyway).
  NEGATIVE     an owner world failing the name filter is not added.
  IDEMPOTENCE  a second reconcile adds 0, same scope, same grant.
  CHEAT        skip the reconcile after creating a world: the grantee does
               NOT see it -- the stale-scope state the test exists to catch.
  REMOVAL      nothing already in the scope is ever removed by a reconcile.

Daemon-level tests use a scripted Vivarium: the reconcile runs once at
start, once at each productive->IDLE boundary, never on IDLE->IDLE, and a
raising reconcile never stops the loop.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

VIVARIUM = Path(__file__).resolve().parent.parent
REPO = VIVARIUM.parent
ENGINE = REPO / "SerendipityFoundry" / "SerendipityFoundryEngine"
for p in (str(VIVARIUM), str(ENGINE), str(ENGINE / "deploy")):
    if p not in sys.path:
        sys.path.insert(0, p)

from viv import daemon as _daemon                                  # noqa: E402
from viv import scope as _scope                                    # noqa: E402
from viv.loop import EXECUTED, IDLE, TickReport                    # noqa: E402

sfe_runtime = pytest.importorskip("sfe.runtime")
Foundry = sfe_runtime.Foundry


class _Owner:
    """What ensure_grant needs, backed by Foundry for one client id."""

    def __init__(self, f, client_id):
        self.f, self.client_id = f, client_id

    def list_worlds(self):
        return self.f.list_worlds(client_id=self.client_id)

    def read_scopes(self):
        return self.f.list_read_scopes(self.client_id)

    def create_read_scope(self, name, *, note=None):
        return self.f.create_read_scope(self.client_id, name=name, note=note)

    def add_scope_worlds(self, scope_id, world_ids):
        return self.f.add_scope_worlds(scope_id, list(world_ids), client_id=self.client_id)

    def grant_read(self, scope_id, grantee_client_id, *, note=None):
        return self.f.grant_read(scope_id, grantee_client_id=grantee_client_id,
                                 granted_by=self.client_id, note=note)


@pytest.fixture
def eco(tmp_path):
    f = Foundry(str(tmp_path / "b1.db"))
    owner = f.create_client("vivarium")
    sess = f.create_session(owner, "viv")
    initial = [f.create_world(sess, "viv-%d" % i)["world_id"] for i in range(3)]
    other = f.create_client("harmonia")
    so = f.create_session(other, "harm")
    grantee = f.create_client("archaeon-reader")
    scopes = [{"scope_name": "archaeon-campaigns", "grantee": grantee, "name_prefix": "viv-"}]
    yield {"f": f, "owner": owner, "sess": sess, "initial": initial, "other": other,
           "so": so, "grantee": grantee, "scopes": scopes, "client": _Owner(f, owner)}
    f.close()


def _visible(eco, scope_id):
    return {w["world_id"] for w in eco["f"].read_worlds(eco["grantee"], group_id=scope_id)["worlds"]} \
        if isinstance(eco["f"].read_worlds(eco["grantee"], group_id=scope_id), dict) \
        else {w["world_id"] for w in eco["f"].read_worlds(eco["grantee"], group_id=scope_id)}


def _scope_id(rec):
    return rec["scopes"][0]["scope_id"]


def test_positive_new_owner_world_becomes_visible_after_reconcile(eco):
    r0 = _scope.reconcile(eco["client"], eco["scopes"], trigger="test")
    assert r0["added_total"] == 3 and r0["productive"]
    sid = _scope_id(r0)
    assert set(eco["initial"]) <= _visible(eco, sid)

    new = eco["f"].create_world(eco["sess"], "viv-new-fossil")["world_id"]
    assert new not in _visible(eco, sid), "visible before any reconcile -- the scope is not enumerated"
    r1 = _scope.reconcile(eco["client"], eco["scopes"], trigger="batch_boundary")
    assert r1["added_total"] == 1 and r1["productive"]
    assert r1["scopes"][0]["worlds_in_scope_after"] == 4
    assert new in _visible(eco, sid)


def test_negative_foreign_owned_viv_world_is_never_added(eco):
    r0 = _scope.reconcile(eco["client"], eco["scopes"], trigger="test")
    sid = _scope_id(r0)
    foreign = eco["f"].create_world(eco["so"], "viv-looks-like-ours")["world_id"]
    r1 = _scope.reconcile(eco["client"], eco["scopes"], trigger="test")
    assert r1["added_total"] == 0
    assert foreign not in _visible(eco, sid)
    # and even a direct owner-side attempt is refused by the engine
    add = eco["client"].add_scope_worlds(sid, [foreign])
    assert foreign in (add.get("not_yours") or []), add
    assert foreign not in _visible(eco, sid)


def test_negative_owner_world_failing_the_filter_is_not_added(eco):
    r0 = _scope.reconcile(eco["client"], eco["scopes"], trigger="test")
    sid = _scope_id(r0)
    pack = eco["f"].create_world(eco["sess"], "h1h0-phase2-packs-test")["world_id"]
    r1 = _scope.reconcile(eco["client"], eco["scopes"], trigger="test")
    assert r1["added_total"] == 0
    assert pack not in _visible(eco, sid)
    assert r1["scopes"][0]["worlds_in_scope_after"] == 3


def test_idempotence_second_reconcile_adds_zero_same_scope_same_grant(eco):
    r0 = _scope.reconcile(eco["client"], eco["scopes"], trigger="test")
    r1 = _scope.reconcile(eco["client"], eco["scopes"], trigger="test")
    assert r1["added_total"] == 0 and not r1["productive"]
    assert r1["scopes"][0]["scope_id"] == r0["scopes"][0]["scope_id"]
    assert r1["scopes"][0]["grant_id"] == r0["scopes"][0]["grant_id"]
    assert r1["scopes"][0]["worlds_in_scope_after"] == r0["scopes"][0]["worlds_in_scope_after"] == 3
    assert r1["scopes"][0]["scope_created"] is False


def test_cheat_skipping_the_reconcile_leaves_the_new_world_invisible(eco):
    """The stale-scope state. If this test could not fail, the positive
    test above would be measuring nothing."""
    r0 = _scope.reconcile(eco["client"], eco["scopes"], trigger="test")
    sid = _scope_id(r0)
    new = eco["f"].create_world(eco["sess"], "viv-orphan-fossil")["world_id"]
    # ... a campaign ends, nobody reconciles ...
    assert new not in _visible(eco, sid)
    assert len(_visible(eco, sid)) == 3


def test_a_reconcile_never_removes_a_member(eco):
    r0 = _scope.reconcile(eco["client"], eco["scopes"], trigger="test")
    sid = _scope_id(r0)
    before = _visible(eco, sid)
    # a world the filter would now exclude cannot be produced by renaming
    # (names are immutable), so the strongest removal pressure available is
    # a reconcile with a NARROWER filter: it must add nothing and drop nothing
    narrower = [dict(eco["scopes"][0], name_prefix="viv-0")]
    r1 = _scope.reconcile(eco["client"], narrower, trigger="test")
    assert r1["added_total"] == 0
    assert _visible(eco, sid) == before


def test_no_declared_scopes_is_an_explicit_no_op(eco):
    r = _scope.reconcile(eco["client"], [], trigger="test")
    assert r["no_op"] == "no scopes declared in config" and r["added_total"] == 0


def test_receipt_is_written_per_call(eco, tmp_path):
    r = _scope.reconcile(eco["client"], eco["scopes"], trigger="test")
    p = _scope.write_receipt(r, tmp_path / "var")
    assert p and p.exists() and p.name.startswith("scope_reconcile-")


# ------------------------------------------------------------ daemon hook
class _FakeViv:
    def __init__(self, outcomes):
        self.worker_id = "scope-test"; self.schema = "viv_test"; self.cfg = {}
        self._out = list(outcomes); self.ticks = 0; self.counters = {}
        self.reconciles = []; self.raise_on = set()

    def recover(self, _c):
        class _R: safe = True; stranded = (); note = ""
        return _R()

    def tick(self, _c):
        self.ticks += 1
        return TickReport(outcome=self._out.pop(0) if self._out else IDLE)

    def reconcile_scopes(self, *, trigger, dry_run=False):
        self.reconciles.append(trigger)
        if trigger in self.raise_on:
            raise RuntimeError("engine unreachable")
        return {"added_total": 0}

    def heartbeat(self, *_a, **_k):
        pass

    def health(self, *_a, **_k):
        return {}


def _make_daemon(monkeypatch, viv, tmp_path):
    d = _daemon.Daemon.__new__(_daemon.Daemon)
    d.viv = viv; d.log = lambda *_a: None; d.idle_interval = 0.0; d.busy_interval = 0.0
    d._stop = False; d._reports = []; d._scope_reconciles = []; d._productive_run = False
    d._preflight_pew = lambda: None; d._sleep = lambda _s: None; d.var = tmp_path
    d.notify = lambda rec, **_k: {"posted": False}
    d.configure_bound({_daemon.BOUND_KEY: 10_000, _daemon.SEAT_KEY: "Archaeon"})

    class _Conn:
        def close(self): pass
        def rollback(self): pass
    monkeypatch.setattr(_daemon._db, "connect", _Conn)
    return d


def test_daemon_reconciles_once_at_start_and_once_per_batch_boundary(monkeypatch, tmp_path):
    viv = _FakeViv([IDLE, EXECUTED, EXECUTED, IDLE, IDLE, IDLE, EXECUTED, IDLE, IDLE])
    d = _make_daemon(monkeypatch, viv, tmp_path)
    assert d.run(install_signals=False, max_ticks=9) == _daemon.EXIT_OK
    # start; boundary after the first productive run (tick 4); boundary
    # after the second (tick 8); NOT on the idle->idle ticks 5, 6, 9, and
    # NOT on the leading idle tick 1 (nothing was produced yet)
    assert viv.reconciles == ["start", "batch_boundary", "batch_boundary"]


def test_daemon_survives_a_raising_reconcile(monkeypatch, tmp_path):
    viv = _FakeViv([EXECUTED, IDLE, EXECUTED, IDLE])
    viv.raise_on = {"start", "batch_boundary"}
    d = _make_daemon(monkeypatch, viv, tmp_path)
    assert d.run(install_signals=False, max_ticks=4) == _daemon.EXIT_OK
    assert viv.ticks == 4 and viv.reconciles == ["start", "batch_boundary", "batch_boundary"]


def test_daemon_without_a_reconcile_method_is_unaffected(monkeypatch, tmp_path):
    viv = _FakeViv([EXECUTED, IDLE])
    del _FakeViv.reconcile_scopes
    try:
        d = _make_daemon(monkeypatch, viv, tmp_path)
        assert d.run(install_signals=False, max_ticks=2) == _daemon.EXIT_OK
    finally:
        _FakeViv.reconcile_scopes = lambda self, *, trigger, dry_run=False: self.reconciles.append(trigger) or {"added_total": 0}
