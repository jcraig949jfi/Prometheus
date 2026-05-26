"""TDD tests for G11 Exception-Miner."""
from __future__ import annotations

import pytest

from charon.agents.erebos.generators._base import ComposedClaim
from charon.agents.erebos.generators.g11_exception_miner import (
    ExceptionMinerGenerator,
    MIN_KILL_FRACTION,
    MIN_SURVIVORS,
    MIN_TOTAL,
)
from charon.agents.erebos.tests._fixtures import empty_swarm_state


def _erebos_row(rid: str, plugin: str, verdict: str,
                payload_keys: list[str]) -> dict:
    payload = {k: 1.0 for k in payload_keys}
    return {
        "record_id": rid,
        "canonical_claim_text": f"composition {rid}",
        "verdict": verdict,
        "kill_pattern": "erebos_test_pattern",
        "kill_vector": None,
        "generator_id": "erebos",
        "emitted_at": "2026-05-26T00:00:00+00:00",
        "claim_payload": {"plugin_id": plugin, "composed_id": f"EREBOS-{rid}"},
        "extras": {"composition_payload": payload},
    }


@pytest.fixture
def gen():
    return ExceptionMinerGenerator()


def test_g11_not_applicable_with_empty_state(gen):
    assert gen.applicable(empty_swarm_state()) is False


def test_g11_not_applicable_below_min_total(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("r1", "g02_contrast", "REJECTED", ["x"]),
        _erebos_row("r2", "g02_contrast", "PROMOTED", ["x", "secret"]),
    ]
    assert gen.applicable(state) is False  # only 2 < MIN_TOTAL=5


def test_g11_not_applicable_without_enough_kill_rate(gen):
    state = empty_swarm_state()
    # 5 rows, 1 rejected, 4 promoted -> kill rate 20% < 50% threshold
    state.erebos_self_ledger = [
        _erebos_row(f"r{i}", "g02_contrast", "PROMOTED", ["common"])
        for i in range(4)
    ] + [_erebos_row("r5", "g02_contrast", "REJECTED", ["common"])]
    assert gen.applicable(state) is False


def test_g11_applicable_with_high_kill_and_survivors_with_secret(gen):
    state = empty_swarm_state()
    # 5 rows: 3 rejected (common only), 2 promoted (common + secret)
    state.erebos_self_ledger = [
        _erebos_row("r1", "g02_contrast", "REJECTED", ["common"]),
        _erebos_row("r2", "g02_contrast", "REJECTED", ["common"]),
        _erebos_row("r3", "g02_contrast", "REJECTED", ["common"]),
        _erebos_row("r4", "g02_contrast", "PROMOTED", ["common", "secret"]),
        _erebos_row("r5", "g02_contrast", "PROMOTED", ["common", "secret"]),
    ]
    assert gen.applicable(state) is True


def test_g11_identifies_hidden_property(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row("r1", "g02_contrast", "REJECTED", ["common"]),
        _erebos_row("r2", "g02_contrast", "REJECTED", ["common"]),
        _erebos_row("r3", "g02_contrast", "REJECTED", ["common"]),
        _erebos_row("r4", "g02_contrast", "PROMOTED", ["common", "secret"]),
        _erebos_row("r5", "g02_contrast", "PROMOTED", ["common", "secret"]),
    ]
    claim = gen.generate(state)
    assert claim is not None
    assert "secret" in claim.composition_payload["hidden_property_keys"]


def test_g11_expected_kill_pattern(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row(f"r{i}", "g02_contrast", "REJECTED", ["x"])
        for i in range(3)
    ] + [
        _erebos_row(f"p{i}", "g02_contrast", "PROMOTED", ["x", "secret"])
        for i in range(2)
    ]
    claim = gen.generate(state)
    assert claim.expected_kill_pattern == "out_of_sample_failure"


def test_g11_six_field_compliance(gen):
    state = empty_swarm_state()
    state.erebos_self_ledger = [
        _erebos_row(f"r{i}", "g02_contrast", "REJECTED", ["x"])
        for i in range(3)
    ] + [
        _erebos_row(f"p{i}", "g02_contrast", "PROMOTED", ["x", "secret"])
        for i in range(2)
    ]
    claim = gen.generate(state)
    assert claim.input_provenance
    assert claim.transformation_description.strip()
    assert claim.output_claim_text.strip()
    assert claim.falsification_route.strip()


def test_g11_metadata():
    g = ExceptionMinerGenerator()
    assert g.id == "g11_exception_miner"
    assert g.feasibility_tier == "B"
    assert g.reasoning_tier == "R3"
