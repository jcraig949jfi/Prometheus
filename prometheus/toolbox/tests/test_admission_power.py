"""Admission POWER (overnight C98; the C95/C97 lesson applied to admission): every named check of admit_world must
have been SEEN to fail on a component built to fail it, or its green is decoration. Before this file the suite had
shown conformance, reference, and the observer/substrate/control slot checks failing; provenance, capabilities,
extensions, replay and controls (cheat) had only ever passed."""
from __future__ import annotations

import itertools

import pytest

from prometheus.toolbox.admission import admit
from prometheus.toolbox.registry import default_registry, ComponentRecord
from prometheus.toolbox.ref.worlds import IntegerWorld

REG = default_registry()


def _reg(kind, cls, caps=None, **row):
    R = REG.fork()
    kw = dict(route="write", provenance={"author": "test"}, license="repository"); kw.update(row)
    R.register(ComponentRecord(kind, "world", cls, caps if caps is not None else IntegerWorld.capabilities, **kw))
    return R


def test_provenance_check_fails_a_row_without_author_or_license():
    class W(IntegerWorld):
        kind = "world.noprov.test"
    res = admit("world.noprov.test", _reg("world.noprov.test", W, provenance={}, license="repository"))
    assert res.state == "UNAVAILABLE" and "provenance" in res.failed and res.checks["provenance"]["ok"] is False
    res = admit("world.noprov.test", _reg("world.noprov.test", W, license="UNSPECIFIED"))
    assert "provenance" in res.failed
    res = admit("world.noprov.test", _reg("world.noprov.test", W, route="stolen"))
    assert "provenance" in res.failed


def test_capabilities_check_fails_a_malformed_id():
    class W(IntegerWorld):
        kind = "world.badcap.test"
    res = admit("world.badcap.test", _reg("world.badcap.test", W, caps=IntegerWorld.capabilities | {"events"}))
    assert "capabilities" in res.failed and res.checks["capabilities"]["malformed"] == ["events"]


def test_extensions_check_fails_a_declared_but_undemonstrable_extension():
    class NoEvents(IntegerWorld):                    # declares ext.events.v1, returns garbage
        kind = "world.noevents.test"
        def events(self):
            return "not a list"
    res = admit("world.noevents.test", _reg("world.noevents.test", NoEvents))
    assert "extensions" in res.failed and res.checks["extensions"]["undemonstrable"] == ["ext.events.v1"]

    class BadSnapshot(IntegerWorld):                 # declares ext.snapshot.v1, restore() does nothing
        kind = "world.badsnap.test"
        def restore(self, snapshot):
            pass
    res = admit("world.badsnap.test", _reg("world.badsnap.test", BadSnapshot))
    assert "extensions" in res.failed and res.checks["extensions"]["undemonstrable"] == ["ext.snapshot.v1"]


def test_replay_check_fails_a_world_that_declares_bit_and_drifts():
    counter = itertools.count()

    class Drifting(IntegerWorld):
        kind = "world.drift.test"
        def reset(self, seed, keep=False):
            super().reset(seed + next(counter) * 1000003, keep)
    res = admit("world.drift.test", _reg("world.drift.test", Drifting))
    assert "replay" in res.failed and res.checks["replay"]["ok"] is False and res.checks["replay"]["class"] == "BIT"


def test_controls_check_fails_a_world_whose_cheat_changes_nothing():
    class CheatBlind(IntegerWorld):
        kind = "world.cheatblind2.test"
        def __init__(self, **params):
            params.pop("_cheat_skip_dynamics", None); super().__init__(**params)
    res = admit("world.cheatblind2.test", _reg("world.cheatblind2.test", CheatBlind))
    assert "controls" in res.failed and res.checks["controls"]["trace_changed"] is False


def test_conformance_check_fails_a_world_whose_trace_is_not_a_hash():
    class ShortTrace(IntegerWorld):
        kind = "world.shorttrace.test"
        def trace_hash(self):
            return "abc"
    res = admit("world.shorttrace.test", _reg("world.shorttrace.test", ShortTrace))
    assert "conformance" in res.failed


def test_a_well_formed_world_passes_every_check_by_name():
    res = admit("world.integer.v1", REG.fork())
    assert res.state == "ADMITTED" and res.failed == []
    assert {k for k, v in res.checks.items() if v.get("ok") is True} >= {"registry", "provenance", "capabilities", "conformance", "extensions", "replay", "reference", "controls", "performance"}
