"""Return-value coverage for sigma_kernel.sigma_kernel core dataclasses.

Closes ST-fire61-002 part 2: substrate-tester fire #61 Lane 16
mutation testing on sigma_kernel/sigma_kernel.py surfaced 2 GENUINE
return-value gaps:
  - line 68: `Symbol.ref` property `return f"{self.name}@v{self.version}"`
    → `return None` survived
  - line 125: `Capability.consume()` `return Capability(...)` → `return None`
    survived

Tests verify the documented return-value contracts so mutations to
`return None` fail.

**Sister files:**
  - test_method_spec_factory_returns.py (fire #51, MethodSpec.from_string + to_string)
  - test_exclusion_certificate_returns.py (fire #54, feeds_negative_space_axis)
  - test_triangulation_protocol_returns.py (fire #55, INDEPENDENCE_TO_METHOD_CLASS + is_proof_bearing + can_certify + threshold)

**Source ticket:** T-2026-05-09-ST-fire62-001 (Techne; closes ST-fire61-002).
"""
from __future__ import annotations

import pytest

from sigma_kernel.sigma_kernel import (
    Capability,
    CapabilityError,
    Symbol,
    Tier,
)


# ---------------------------------------------------------------------------
# Symbol.ref property — line 68 mutation site
# ---------------------------------------------------------------------------


def _make_symbol(name: str = "test_lemma", version: int = 1) -> Symbol:
    """Build a minimal Symbol for return-value testing."""
    return Symbol(
        name=name,
        version=version,
        def_hash="0" * 64,
        def_blob="{}",
        provenance=[],
        tier=Tier.WorkingTheory,
    )


class TestSymbolRefReturnContract:
    """Catches `return f"{self.name}@v{self.version}"` → `return None`."""

    def test_ref_returns_non_None(self):
        sym = _make_symbol()
        result = sym.ref
        assert result is not None

    def test_ref_returns_str_type(self):
        sym = _make_symbol()
        assert isinstance(sym.ref, str)

    def test_ref_format_matches_name_at_v_version(self):
        sym = _make_symbol(name="example", version=3)
        assert sym.ref == "example@v3"

    def test_ref_includes_name(self):
        sym = _make_symbol(name="my_lemma_42", version=1)
        assert "my_lemma_42" in sym.ref

    def test_ref_includes_version(self):
        sym = _make_symbol(name="x", version=99)
        assert "v99" in sym.ref


# ---------------------------------------------------------------------------
# Capability.consume() — line 125 mutation site
# ---------------------------------------------------------------------------


class TestCapabilityConsumeReturnContract:
    """Catches `return Capability(self.cap_id, self.cap_type, True)` →
    `return None`."""

    def test_consume_returns_non_None(self):
        cap = Capability(cap_id="cap_test_1")
        result = cap.consume()
        assert result is not None

    def test_consume_returns_Capability_instance(self):
        cap = Capability(cap_id="cap_test_2")
        result = cap.consume()
        assert isinstance(result, Capability)

    def test_consume_preserves_cap_id(self):
        cap = Capability(cap_id="preserved_id")
        consumed = cap.consume()
        assert consumed.cap_id == "preserved_id"

    def test_consume_preserves_cap_type(self):
        cap = Capability(cap_id="x", cap_type="CustomCap")
        consumed = cap.consume()
        assert consumed.cap_type == "CustomCap"

    def test_consume_sets_consumed_True(self):
        cap = Capability(cap_id="x")
        assert cap.consumed is False  # initial state
        consumed = cap.consume()
        assert consumed.consumed is True

    def test_consume_does_not_mutate_original(self):
        """Capability is frozen; consume() returns a NEW instance."""
        cap = Capability(cap_id="x")
        consumed = cap.consume()
        assert cap.consumed is False  # original unchanged
        assert consumed is not cap  # different object

    def test_consume_twice_raises_CapabilityError(self):
        """Linearity check: consuming an already-consumed cap raises."""
        cap = Capability(cap_id="x")
        consumed = cap.consume()
        with pytest.raises(CapabilityError):
            consumed.consume()
