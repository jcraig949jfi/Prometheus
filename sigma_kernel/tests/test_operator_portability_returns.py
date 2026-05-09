"""Return-value coverage for sigma_kernel.operator_portability.

Closes ST-fire65-001: substrate-tester fire #65 Lane 16 mutation
testing on sigma_kernel/operator_portability.py surfaced 7 GENUINE
coverage gaps (lines 94, 204, 205, 229, 256, 261) on the substrate
v2.3 §6.3 P6 primitive bundling OperatorPortabilityCertificate +
PortabilityEvidence + PortabilityReplay + OperatorPortabilityRegistry.

**Sister files (same return-value pattern):**
  - test_method_spec_factory_returns.py (fire #51)
  - test_exclusion_certificate_returns.py (fire #54)
  - test_triangulation_protocol_returns.py (fire #55)
  - test_sigma_kernel_core_returns.py (fire #62)
  - test_coordinate_chart_returns.py (fire #64)

**Source ticket:** T-2026-05-09-ST-fire66-001 (Techne; closes ST-fire65-001).
"""
from __future__ import annotations

import pytest

from sigma_kernel.operator_portability import (
    OperatorPortabilityCertificate,
    OperatorPortabilityRegistry,
    PortabilityCollisionError,
    PortabilityEvidence,
    PortabilityReplay,
    PortabilityVerdict,
    TransferMethod,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _evidence(n: int = 5, summary: dict | None = None) -> PortabilityEvidence:
    return PortabilityEvidence(
        n_objects_tested=n,
        signature_summary=summary if summary is not None else {"sig_a": 1.0, "sig_b": 2.0},
        sample_object_ids=("obj1", "obj2"),
    )


def _replay() -> PortabilityReplay:
    return PortabilityReplay(
        code_hash="a" * 64, data_hash="b" * 64, seed=42, environment_hash="c" * 64,
    )


def _make_cert(
    operator_id: str = "test_op",
    source: str = "src:a",
    target: str = "tgt:b",
) -> OperatorPortabilityCertificate:
    return OperatorPortabilityCertificate(
        operator_id=operator_id,
        source_chart_id=source,
        target_chart_id=target,
        transfer_method=TransferMethod.DIRECT_APPLICATION,
        evidence_pre=_evidence(n=5, summary={"sig": 1.0}),
        evidence_post=_evidence(n=5, summary={"sig": 1.0}),
        equivalence_relation="exact",
        verdict=PortabilityVerdict.PORTABLE,
        rationale="test rationale",
        replay=_replay(),
    )


# ---------------------------------------------------------------------------
# Line 94: PortabilityEvidence.n_objects_tested boundary
# ---------------------------------------------------------------------------


class TestPortabilityEvidenceBoundary:
    """Catches line 94 mutations:
      - `< 0` -> `> 0` flip (if `> 0` then n=0 should raise; n=1 ok)
      - `0` -> `1` (if compared to 1, n=0 should raise)
    """

    def test_negative_n_objects_raises(self):
        with pytest.raises(ValueError):
            PortabilityEvidence(n_objects_tested=-1, signature_summary={})

    def test_zero_n_objects_accepted(self):
        """n=0 is valid (no objects tested but the structure is still
        sound). Catches `< 0` -> `> 0` flip (which would reject n=0)."""
        ev = PortabilityEvidence(n_objects_tested=0, signature_summary={})
        assert ev.n_objects_tested == 0

    def test_one_n_objects_accepted(self):
        """Sanity. Catches `0 -> 1` mutation if n=1 is the boundary."""
        ev = PortabilityEvidence(n_objects_tested=1, signature_summary={})
        assert ev.n_objects_tested == 1

    def test_large_n_objects_accepted(self):
        ev = PortabilityEvidence(n_objects_tested=1_000_000, signature_summary={})
        assert ev.n_objects_tested == 1_000_000

    def test_non_int_raises(self):
        with pytest.raises(ValueError):
            PortabilityEvidence(n_objects_tested=3.14, signature_summary={})  # type: ignore


# ---------------------------------------------------------------------------
# Line 204: sort_keys=True (canonical-hash stability)
# ---------------------------------------------------------------------------


class TestCertificateIdSortKeyStability:
    """Catches `sort_keys=True` -> `False` mutation. The certificate_id
    must be stable across dict iteration order; sort_keys=False would
    make it depend on insertion order."""

    def test_id_stable_across_signature_key_orders(self):
        """Two certificates with structurally identical signature_summaries
        but different dict key insertion orders MUST have equal ids."""
        sig_a = {"k_alpha": 1.0, "k_beta": 2.0, "k_gamma": 3.0}
        sig_b = {"k_gamma": 3.0, "k_alpha": 1.0, "k_beta": 2.0}
        c1 = OperatorPortabilityCertificate(
            operator_id="op", source_chart_id="s:a", target_chart_id="t:b",
            transfer_method=TransferMethod.DIRECT_APPLICATION,
            evidence_pre=_evidence(summary=sig_a),
            evidence_post=_evidence(summary=sig_a),
            equivalence_relation="exact",
            verdict=PortabilityVerdict.PORTABLE,
            rationale="r", replay=_replay(),
        )
        c2 = OperatorPortabilityCertificate(
            operator_id="op", source_chart_id="s:a", target_chart_id="t:b",
            transfer_method=TransferMethod.DIRECT_APPLICATION,
            evidence_pre=_evidence(summary=sig_b),
            evidence_post=_evidence(summary=sig_b),
            equivalence_relation="exact",
            verdict=PortabilityVerdict.PORTABLE,
            rationale="r", replay=_replay(),
        )
        assert c1.certificate_id == c2.certificate_id


# ---------------------------------------------------------------------------
# Line 205: certificate_id return-value contract
# ---------------------------------------------------------------------------


class TestCertificateIdReturn:
    """Catches `return hashlib.sha256(...).hexdigest()` -> `return None`."""

    def test_certificate_id_returns_non_None(self):
        cert = _make_cert()
        cid = cert.certificate_id
        assert cid is not None

    def test_certificate_id_returns_str(self):
        assert isinstance(_make_cert().certificate_id, str)

    def test_certificate_id_is_64_hex_chars(self):
        cid = _make_cert().certificate_id
        assert len(cid) == 64
        assert all(c in "0123456789abcdef" for c in cid)

    def test_different_operator_id_different_cert_id(self):
        c1 = _make_cert(operator_id="op_alpha")
        c2 = _make_cert(operator_id="op_beta")
        assert c1.certificate_id != c2.certificate_id


# ---------------------------------------------------------------------------
# Line 229: Registry.register replace=False default
# ---------------------------------------------------------------------------


class TestRegistryReplaceDefault:
    """Catches `replace: bool = False` (default) -> `True` mutation.
    With default=True, the collision check is bypassed."""

    def test_default_replace_is_False_collision_raises(self):
        """Default behavior: registering twice without replace=True must
        raise PortabilityCollisionError. If the default were True, this
        test would FAIL."""
        registry = OperatorPortabilityRegistry()
        cert = _make_cert()
        registry.register(cert)
        with pytest.raises(PortabilityCollisionError):
            registry.register(cert)

    def test_explicit_replace_True_allows_re_registration(self):
        """Sanity: passing replace=True works."""
        registry = OperatorPortabilityRegistry()
        cert = _make_cert()
        registry.register(cert)
        registry.register(cert, replace=True)
        assert registry.by_id(cert.certificate_id) is cert


# ---------------------------------------------------------------------------
# Lines 256, 261: registry removal-path filter `x != cid`
# ---------------------------------------------------------------------------


class TestRegistryRemovalPath:
    """Catches `x != cid` -> `x == cid` flip on registry list-comp
    filters during replace. With == flip, the OLD index entry is KEPT
    and the new one ALSO appended → corrupted index."""

    def test_replace_scrubs_old_by_operator_index(self):
        """After replace, _by_operator must contain ONE entry for the
        operator (not duplicated)."""
        registry = OperatorPortabilityRegistry()
        cert = _make_cert(operator_id="op_x")
        registry.register(cert)
        # Replace with a structurally-identical cert (same id)
        registry.register(cert, replace=True)
        ops_for_op_x = registry._by_operator.get("op_x", [])
        assert len(ops_for_op_x) == 1, (
            f"expected exactly 1 entry for 'op_x' after replace; "
            f"got {len(ops_for_op_x)} ({ops_for_op_x!r}). "
            f"`x != cid` filter likely flipped to `==`, breaking "
            f"removal-path bookkeeping."
        )

    def test_replace_scrubs_old_by_chart_pair_index(self):
        """Sister to above; _by_chart_pair index too."""
        registry = OperatorPortabilityRegistry()
        cert = _make_cert(source="src:1", target="tgt:1")
        registry.register(cert)
        registry.register(cert, replace=True)
        pair = ("src:1", "tgt:1")
        certs_for_pair = registry._by_chart_pair.get(pair, [])
        assert len(certs_for_pair) == 1, (
            f"expected exactly 1 entry for {pair!r} after replace; "
            f"got {len(certs_for_pair)} ({certs_for_pair!r})."
        )
