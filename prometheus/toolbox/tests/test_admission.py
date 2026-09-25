"""Admission for every slot (overnight C28; directive s19): a machine predicate over an implementation, no
approver; failure = that component UNAVAILABLE, nothing else affected. Every reference row must be ADMITTED
on this host; deliberately broken implementations must be refused with the failing check named."""
from __future__ import annotations

import pytest

from prometheus.toolbox.admission import admit, admit_all
from prometheus.toolbox.registry import default_registry, ComponentRecord
from prometheus.toolbox.ref.observers import TraceObserver
from prometheus.toolbox.ref.substrates import FlatInProcessSubstrate
from prometheus.toolbox.ref.controls import ReplayControl
from prometheus.toolbox.ref.players import random_statemachine

REG = default_registry()


def test_every_reference_component_is_admitted_on_this_host():
    assert all(r["provenance"].get("author") == "Bellerophon" for r in REG.rows()), "a test-only or foreign row leaked into the default registry (C62)"
    res = admit_all(REG)
    bad = {k: v.failed for k, v in res.items() if v.state != "ADMITTED" and not k.endswith(".playtest")}
    # components whose machinery is absent on this host are UNAVAILABLE with an import reason, never a kernel failure
    allowed = {k for k, v in res.items() if v.checks.get("registry", {}).get("note") == "absent machinery"}
    assert not (set(bad) - allowed), bad
    assert res["world.integer.v1"].state == "ADMITTED" and res["substrate.kv.v1"].state == "ADMITTED" and res["observer.series.v1"].state == "ADMITTED"


def test_broken_observer_is_refused_with_the_check_named():
    class BadObserver(TraceObserver):
        kind = "observer.bad.v1"

        def measure(self):
            return {"set": {1, 2}}                        # not JSON-serialisable: a receipt could not carry it
    R = REG.fork(); R.register(ComponentRecord("observer.bad.v1", "observer", BadObserver, frozenset(), route="write", provenance={"author": "test"}, license="repository"))
    r = admit("observer.bad.v1", R)
    assert r.state == "UNAVAILABLE" and "serialisable" in r.failed


def test_nondeterministic_observer_is_refused():
    class Jitter(TraceObserver):
        kind = "observer.jitter.v1"

        def measure(self):
            import os
            return {"noise": os.urandom(2).hex()}
    R = REG.fork(); R.register(ComponentRecord("observer.jitter.v1", "observer", Jitter, frozenset(), route="write", provenance={"author": "test"}, license="repository"))
    assert "determinism" in admit("observer.jitter.v1", R).failed


def test_substrate_that_lies_about_representations_is_refused():
    class Liar(FlatInProcessSubstrate):
        kind = "substrate.liar.v1"

        def __init__(self):
            super().__init__(); self.representations = frozenset(self.representations | {"rewrite.v9"})
    R = REG.fork(); R.register(ComponentRecord("substrate.liar.v1", "substrate", Liar, FlatInProcessSubstrate.capabilities, route="write", provenance={"author": "test"}, license="repository"))
    r = admit("substrate.liar.v1", R)
    assert r.state == "UNAVAILABLE" and "representations" in r.failed


def test_control_whose_arm_is_invalid_is_refused():
    class BadControl(ReplayControl):
        kind = "replay"

        def arm(self, exp, rng_seed):
            e = super().arm(exp, rng_seed); e.family = "a/b"; return e            # invalid IR out of a control
    R = REG.fork(); R.register(ComponentRecord("control.bad.v1", "control", BadControl, frozenset(), route="write", provenance={"author": "test"}, license="repository"))
    assert "arm" in admit("control.bad.v1", R).failed


def test_unknown_kind_is_a_registry_failure_not_an_exception():
    r = admit("world.nope.v1", REG)
    assert r.state == "UNAVAILABLE" and r.failed == ["registry"]


# C70: the "reference agreement" admission check had never run against a real second implementation -- the
# family was derived from the kind string, so a second implementation could only be named like a new version.
# A row now declares `implements` (the reference family it claims to reproduce); admission compares traces
# with the reference over the probe seeds; a subtly different implementation is UNAVAILABLE on "reference".
def test_second_implementation_is_checked_against_the_reference_and_a_wrong_one_is_refused():
    from prometheus.toolbox.ref.worlds import IntegerWorld
    from prometheus.toolbox.ref.worlds_integer_alt import IntegerWorldAlt

    class Wrong(IntegerWorldAlt):                 # same code path, one constant off: actions land x*98 instead of x*97
        kind = "world.integer_wrong.v1"
        ACT_MUL = 98
    R = REG.fork()
    R.register(ComponentRecord("world.integer_alt.v1", "world", IntegerWorldAlt, IntegerWorldAlt.capabilities, implements="world.integer", route="write", provenance={"author": "test"}, license="repository"))
    R.register(ComponentRecord("world.integer_wrong.v1", "world", Wrong, IntegerWorldAlt.capabilities, implements="world.integer", route="write", provenance={"author": "test"}, license="repository"))
    ok = admit("world.integer_alt.v1", R); bad = admit("world.integer_wrong.v1", R)
    assert ok.state == "ADMITTED" and ok.checks["reference"]["reference"] == "world.integer.v1" and ok.checks["reference"]["ok"] is True
    assert bad.state == "UNAVAILABLE" and "reference" in bad.failed and bad.checks["reference"]["ok"] is False
