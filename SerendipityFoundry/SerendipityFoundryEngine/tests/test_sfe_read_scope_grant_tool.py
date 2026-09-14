"""B1 tool: deploy/read_scope_grant.py, driven in-process through a thin
adapter over Foundry with the OWNER's client id, so the test exercises the
same engine semantics the HTTP client would (owner-only scope, INSERT OR
IGNORE membership, idempotent grant, not_yours reporting).

Controls:
  positive    first run creates the scope, adds every owned world, grants
  idempotent  second run adds 0 and returns the SAME grant id
  extend      a world created later is added by a re-run (the lifecycle)
  isolation   a world the owner does NOT own is never added (not_yours), and
              the grantee sees only granted worlds through read_worlds
  cheat       granting to yourself is refused by the engine, so the tool
              cannot manufacture a self-grant that looks like cross-seat read
  dry-run     writes nothing
"""
from __future__ import annotations

import os
import sys

import pytest

_ENGINE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ENGINE_ROOT not in sys.path:
    sys.path.insert(0, _ENGINE_ROOT)
sys.path.insert(0, os.path.join(_ENGINE_ROOT, "deploy"))

from read_scope_grant import ensure_grant   # noqa: E402
from sfe.errors import ValidationError      # noqa: E402
from sfe.runtime import Foundry             # noqa: E402


class _OwnerAdapter:
    """What the tool needs, backed by Foundry for one client id."""

    def __init__(self, f: Foundry, client_id: str):
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
def world(tmp_path):
    f = Foundry(str(tmp_path / "b1.db"))
    owner = f.create_client("vivarium")
    s = f.create_session(owner, "viv")
    owned = [f.create_world(s, "viv-%d" % i)["world_id"] for i in range(3)]
    other = f.create_client("harmonia")
    so = f.create_session(other, "harm")
    foreign = f.create_world(so, "harm-1")["world_id"]
    grantee = f.create_client("archaeon-reader")
    yield f, owner, s, owned, foreign, grantee
    f.close()


def test_positive_then_idempotent_then_extend(world):
    f, owner, s, owned, foreign, grantee = world
    c = _OwnerAdapter(f, owner)
    r1 = ensure_grant(c, scope_name="archaeon-campaigns", grantee_client_id=grantee)
    assert r1["scope_created"] is True
    assert r1["worlds_added_this_run"] == 3 and r1["worlds_in_scope_after"] == 3
    assert r1["not_yours"] == []
    r2 = ensure_grant(c, scope_name="archaeon-campaigns", grantee_client_id=grantee)
    assert r2["scope_created"] is False
    assert r2["scope_id"] == r1["scope_id"]
    assert r2["worlds_added_this_run"] == 0
    assert r2["grant_id"] == r1["grant_id"]          # same unrevoked grant
    f.create_world(s, "viv-later")
    r3 = ensure_grant(c, scope_name="archaeon-campaigns", grantee_client_id=grantee)
    assert r3["worlds_added_this_run"] == 1 and r3["worlds_in_scope_after"] == 4
    assert r3["grant_id"] == r1["grant_id"]


def test_isolation_foreign_world_never_enters_the_scope(world):
    f, owner, s, owned, foreign, grantee = world
    c = _OwnerAdapter(f, owner)
    r = ensure_grant(c, scope_name="archaeon-campaigns", grantee_client_id=grantee)
    # the owner cannot even see the foreign world, so it is not in the list;
    # try to smuggle it in by id and the engine reports, never adds
    add = f.add_scope_worlds(r["scope_id"], [foreign], client_id=owner)
    assert foreign in add.get("not_yours", [])
    seen = {w["world_id"] for w in f.read_worlds(grantee)["worlds"]}
    assert seen == set(owned)
    assert foreign not in seen


def test_name_prefix_filter_limits_the_scope(world):
    f, owner, s, owned, foreign, grantee = world
    f.create_world(s, "probe-noop")
    c = _OwnerAdapter(f, owner)
    r = ensure_grant(c, scope_name="viv-only", grantee_client_id=grantee,
                     world_filter=lambda w: w["name"].startswith("viv-"))
    assert r["worlds_in_scope_after"] == 3


def test_cheat_control_self_grant_is_refused_by_the_engine(world):
    f, owner, s, owned, foreign, grantee = world
    c = _OwnerAdapter(f, owner)
    with pytest.raises(ValidationError):
        ensure_grant(c, scope_name="self", grantee_client_id=owner)


def test_dry_run_writes_nothing(world):
    f, owner, s, owned, foreign, grantee = world
    c = _OwnerAdapter(f, owner)
    r = ensure_grant(c, scope_name="dry", grantee_client_id=grantee, dry_run=True)
    assert r["dry_run"] is True and r["scope_existed"] is False and r["would_add"] == 3
    assert f.list_read_scopes(owner) == []
    assert f.read_worlds(grantee)["worlds"] == []
