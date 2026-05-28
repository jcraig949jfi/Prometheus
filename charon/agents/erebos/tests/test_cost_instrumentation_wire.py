"""Tests for the cost-instrumentation daemon wire (Phase 1B ITER-37).

Validates that time_plugin_generate() populates generation_cost_seconds
on returned claims and that populate_falsification_cost() writes the
field into stygian executor result dicts.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

import pytest

from charon.agents.erebos._cost_instrumentation import (
    is_instrumented,
    populate_falsification_cost,
    time_plugin_generate,
)


@dataclass
class _FakeClaim:
    """Minimal stand-in for ComposedClaim with the cost field."""
    plugin_id: str = "test"
    composed_id: str = "TEST-0001"
    generation_cost_seconds: float = 0.0


class _FakePluginEmits:
    id = "fake_emits"
    sleep_seconds = 0.01

    def generate(self, state):
        time.sleep(self.sleep_seconds)
        return _FakeClaim()


class _FakePluginNone:
    id = "fake_none"

    def generate(self, state):
        return None


class _FakePluginRaises:
    id = "fake_raises"

    def generate(self, state):
        raise RuntimeError("simulated generator failure")


# ---------------------------------------------------------------------
# time_plugin_generate
# ---------------------------------------------------------------------

def test_time_plugin_generate_populates_cost_on_returned_claim():
    plugin = _FakePluginEmits()
    claim, elapsed = time_plugin_generate(plugin, state=None)
    assert claim is not None
    # generation_cost_seconds must be set to the measured elapsed
    assert claim.generation_cost_seconds == pytest.approx(elapsed, abs=1e-9)
    # And the elapsed must be >= the sleep
    assert claim.generation_cost_seconds >= plugin.sleep_seconds * 0.9


def test_time_plugin_generate_returns_elapsed_when_claim_is_none():
    """Even when the plugin returns None, the caller gets the
    elapsed timing back."""
    plugin = _FakePluginNone()
    claim, elapsed = time_plugin_generate(plugin, state=None)
    assert claim is None
    assert elapsed >= 0.0


def test_time_plugin_generate_does_not_swallow_exceptions():
    """Plugin exception propagates so the daemon can record it."""
    plugin = _FakePluginRaises()
    with pytest.raises(RuntimeError, match="simulated generator failure"):
        time_plugin_generate(plugin, state=None)


def test_time_plugin_generate_skips_field_set_when_claim_lacks_it():
    """A claim object without generation_cost_seconds should not
    cause the daemon to crash (cost telemetry is observational)."""
    class _ClaimNoCostField:
        pass

    class _PluginEmitsBare:
        id = "bare"
        def generate(self, state):
            return _ClaimNoCostField()

    # Should not raise — field-setting is best-effort
    claim, elapsed = time_plugin_generate(_PluginEmitsBare(), state=None)
    assert claim is not None
    assert elapsed >= 0.0


# ---------------------------------------------------------------------
# populate_falsification_cost
# ---------------------------------------------------------------------

def test_populate_falsification_cost_writes_field():
    result_dict = {"verdict": "REJECTED", "kill_pattern": "kp"}
    populate_falsification_cost(result_dict, 0.123)
    assert result_dict["falsification_cost_seconds"] == 0.123


def test_populate_falsification_cost_overwrites_existing_value():
    result_dict = {"falsification_cost_seconds": 0.5}
    populate_falsification_cost(result_dict, 1.5)
    assert result_dict["falsification_cost_seconds"] == 1.5


def test_populate_falsification_cost_safe_on_non_dict():
    """Non-dict input returns unchanged (does not crash)."""
    sentinel = "not a dict"
    out = populate_falsification_cost(sentinel, 0.5)  # type: ignore[arg-type]
    assert out == sentinel


def test_populate_falsification_cost_returns_same_dict_for_chaining():
    """Returns the (same) dict for caller ergonomics."""
    d = {}
    out = populate_falsification_cost(d, 0.1)
    assert out is d
    assert d["falsification_cost_seconds"] == 0.1


# ---------------------------------------------------------------------
# is_instrumented
# ---------------------------------------------------------------------

def test_is_instrumented_true_for_populated_claim():
    claim = _FakeClaim(generation_cost_seconds=0.05)
    assert is_instrumented(claim) is True


def test_is_instrumented_false_for_default_zero_claim():
    claim = _FakeClaim(generation_cost_seconds=0.0)
    assert is_instrumented(claim) is False


def test_is_instrumented_true_for_populated_result_dict():
    d = {"falsification_cost_seconds": 0.2}
    assert is_instrumented(d) is True


def test_is_instrumented_false_for_none():
    assert is_instrumented(None) is False


def test_is_instrumented_false_for_random_object():
    assert is_instrumented("not a claim") is False
    assert is_instrumented(42) is False


# ---------------------------------------------------------------------
# End-to-end: instrumented plugin claim becomes instrumented
# ---------------------------------------------------------------------

def test_end_to_end_pipeline_populates_both_costs():
    """A plugin emits a claim (gen cost set), a stygian executor
    times the loader (falsification cost set onto result dict).
    Both costs are observable downstream."""
    # 1. Daemon-side: plugin emits a claim with generation cost set
    claim, gen_elapsed = time_plugin_generate(_FakePluginEmits(), state=None)
    assert claim is not None
    assert claim.generation_cost_seconds > 0.0

    # 2. Stygian-side: result dict gets falsification cost set
    result_dict = {"verdict": "PROMOTED"}
    populate_falsification_cost(result_dict, 0.42)

    # 3. Both observable: claim AND result dict both report
    #    is_instrumented == True
    assert is_instrumented(claim)
    assert is_instrumented(result_dict)
