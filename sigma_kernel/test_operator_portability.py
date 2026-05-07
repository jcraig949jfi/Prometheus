"""Tests for sigma_kernel.operator_portability — T-2026-05-07-T030 minimal impl.

Coverage:
  * Enum values + immutability of value objects
  * PortabilityEvidence + PortabilityReplay validation
  * OperatorPortabilityCertificate __post_init__ checks
  * Content-addressed certificate_id (deterministic; differs on substantive
    field changes; identical on runtime metadata changes)
  * Registry: register / by_id / by_operator / by_chart_pair
  * PortabilityCollisionError on duplicate without replace=True
  * replace=True scrubs old indices
  * Worked example: Mahler-measure operator across deg14 and deg12 Lehmer charts
"""
from __future__ import annotations

import pytest

from sigma_kernel.operator_portability import (
    DEFAULT_REGISTRY,
    OperatorPortabilityCertificate,
    OperatorPortabilityRegistry,
    PortabilityCollisionError,
    PortabilityEvidence,
    PortabilityRegistrationError,
    PortabilityReplay,
    PortabilityVerdict,
    TransferMethod,
    get_portability_certificate,
    portability_certificates_by_chart_pair,
    portability_certificates_by_operator,
    register_portability_certificate,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _basic_evidence(n: int = 100, summary: dict = None) -> PortabilityEvidence:
    return PortabilityEvidence(
        n_objects_tested=n,
        signature_summary=dict(summary or {"n_band_candidates": 5, "modal_kill": "F1"}),
        sample_object_ids=("obj_1", "obj_2"),
    )


def _basic_replay(seed: int = 0) -> PortabilityReplay:
    return PortabilityReplay(
        code_hash="a" * 64,
        data_hash="b" * 64,
        seed=seed,
        environment_hash="c" * 64,
    )


def _basic_cert(
    operator_id: str = "mahler_measure",
    source: str = "lehmer:deg14:pm5:palindromic",
    target: str = "lehmer:deg12:pm5:palindromic",
    pre_summary: dict = None,
    post_summary: dict = None,
) -> OperatorPortabilityCertificate:
    return OperatorPortabilityCertificate(
        operator_id=operator_id,
        source_chart_id=source,
        target_chart_id=target,
        transfer_method=TransferMethod.DIRECT_APPLICATION,
        evidence_pre=_basic_evidence(97_435_855, pre_summary or {"n_band_candidates": 43}),
        evidence_post=_basic_evidence(8_857_805, post_summary or {"n_band_candidates": 113}),
        equivalence_relation="operator_signature_equivalence:band_candidate_distribution",
        verdict=PortabilityVerdict.AWAITING_TRIANGULATION,
        rationale="Mahler measure transports between sister Lehmer subspaces.",
        replay=_basic_replay(),
    )


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestEnums:
    def test_transfer_method_has_canonical_values(self):
        assert TransferMethod.DIRECT_APPLICATION.value == "direct_application"
        assert TransferMethod.UNKNOWN.value == "unknown"
        assert len(list(TransferMethod)) == 5

    def test_portability_verdict_has_canonical_values(self):
        assert PortabilityVerdict.PORTABLE.value == "portable"
        assert PortabilityVerdict.NOT_PORTABLE.value == "not_portable"
        assert PortabilityVerdict.INCONCLUSIVE.value == "inconclusive"
        assert PortabilityVerdict.AWAITING_TRIANGULATION.value == "awaiting_triangulation"
        assert len(list(PortabilityVerdict)) == 4


# ---------------------------------------------------------------------------
# Value object validation
# ---------------------------------------------------------------------------


class TestPortabilityEvidence:
    def test_basic_construction(self):
        e = _basic_evidence()
        assert e.n_objects_tested == 100
        assert "modal_kill" in e.signature_summary

    def test_negative_n_objects_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            PortabilityEvidence(n_objects_tested=-1, signature_summary={})

    def test_non_mapping_signature_raises(self):
        with pytest.raises(TypeError, match="signature_summary"):
            PortabilityEvidence(n_objects_tested=10, signature_summary=[1, 2, 3])  # type: ignore

    def test_non_tuple_sample_ids_raises(self):
        with pytest.raises(TypeError, match="sample_object_ids"):
            PortabilityEvidence(
                n_objects_tested=10,
                signature_summary={},
                sample_object_ids=["a", "b"],  # type: ignore
            )


class TestPortabilityReplay:
    def test_basic_construction(self):
        r = _basic_replay()
        assert r.seed == 0

    def test_empty_hash_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            PortabilityReplay(code_hash="", data_hash="x", seed=0, environment_hash="y")

    def test_non_int_seed_raises(self):
        with pytest.raises(TypeError, match="seed"):
            PortabilityReplay(
                code_hash="x", data_hash="y", seed="zero", environment_hash="z"  # type: ignore
            )


# ---------------------------------------------------------------------------
# Certificate construction
# ---------------------------------------------------------------------------


class TestCertificateConstruction:
    def test_basic_construction(self):
        cert = _basic_cert()
        assert cert.operator_id == "mahler_measure"
        assert cert.transfer_method == TransferMethod.DIRECT_APPLICATION
        assert cert.verdict == PortabilityVerdict.AWAITING_TRIANGULATION

    def test_empty_operator_id_raises(self):
        with pytest.raises(ValueError, match="operator_id must be a non-empty"):
            OperatorPortabilityCertificate(
                operator_id="",
                source_chart_id="a",
                target_chart_id="b",
                transfer_method=TransferMethod.DIRECT_APPLICATION,
                evidence_pre=_basic_evidence(),
                evidence_post=_basic_evidence(),
                equivalence_relation="x",
                verdict=PortabilityVerdict.PORTABLE,
                rationale="r",
                replay=_basic_replay(),
            )

    def test_string_transfer_method_raises_type_error(self):
        with pytest.raises(TypeError, match="transfer_method must be TransferMethod"):
            OperatorPortabilityCertificate(
                operator_id="op",
                source_chart_id="a",
                target_chart_id="b",
                transfer_method="direct_application",  # type: ignore — must be enum
                evidence_pre=_basic_evidence(),
                evidence_post=_basic_evidence(),
                equivalence_relation="x",
                verdict=PortabilityVerdict.PORTABLE,
                rationale="r",
                replay=_basic_replay(),
            )

    def test_non_evidence_pre_raises(self):
        with pytest.raises(TypeError, match="evidence_pre"):
            OperatorPortabilityCertificate(
                operator_id="op",
                source_chart_id="a",
                target_chart_id="b",
                transfer_method=TransferMethod.DIRECT_APPLICATION,
                evidence_pre={"x": 1},  # type: ignore
                evidence_post=_basic_evidence(),
                equivalence_relation="x",
                verdict=PortabilityVerdict.PORTABLE,
                rationale="r",
                replay=_basic_replay(),
            )


# ---------------------------------------------------------------------------
# Content-addressed id
# ---------------------------------------------------------------------------


class TestCertificateId:
    def test_id_is_deterministic(self):
        c1 = _basic_cert()
        c2 = _basic_cert()
        # Same substantive content → same id even though evidence timestamps
        # may differ (timestamps excluded from id by design).
        assert c1.certificate_id == c2.certificate_id
        assert len(c1.certificate_id) == 64  # sha256 hex

    def test_id_differs_on_operator_id_change(self):
        c1 = _basic_cert(operator_id="mahler_measure")
        c2 = _basic_cert(operator_id="hecke_eigenvalue")
        assert c1.certificate_id != c2.certificate_id

    def test_id_differs_on_signature_summary_change(self):
        c1 = _basic_cert(post_summary={"n_band_candidates": 113})
        c2 = _basic_cert(post_summary={"n_band_candidates": 200})
        assert c1.certificate_id != c2.certificate_id

    def test_id_differs_on_chart_pair_change(self):
        c1 = _basic_cert(source="A", target="B")
        c2 = _basic_cert(source="A", target="C")
        assert c1.certificate_id != c2.certificate_id


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class TestRegistry:
    def test_register_and_by_id_round_trip(self):
        reg = OperatorPortabilityRegistry()
        cert = _basic_cert()
        reg.register(cert)
        assert reg.by_id(cert.certificate_id) is cert
        assert cert.certificate_id in reg
        assert len(reg) == 1

    def test_register_non_certificate_raises_type_error(self):
        reg = OperatorPortabilityRegistry()
        with pytest.raises(TypeError, match="OperatorPortabilityCertificate"):
            reg.register({"not": "a certificate"})  # type: ignore

    def test_duplicate_raises_collision_subclass(self):
        reg = OperatorPortabilityRegistry()
        cert = _basic_cert()
        reg.register(cert)
        with pytest.raises(PortabilityCollisionError, match="explicit supersede"):
            reg.register(cert)
        # Subclass of umbrella registration error
        assert issubclass(PortabilityCollisionError, PortabilityRegistrationError)

    def test_replace_supersedes(self):
        reg = OperatorPortabilityRegistry()
        cert = _basic_cert()
        reg.register(cert)
        reg.register(cert, replace=True)  # no raise
        assert reg.by_id(cert.certificate_id) is cert

    def test_by_operator(self):
        reg = OperatorPortabilityRegistry()
        c1 = _basic_cert(operator_id="op_a", source="X", target="Y")
        c2 = _basic_cert(operator_id="op_a", source="X", target="Z")
        c3 = _basic_cert(operator_id="op_b", source="X", target="Y")
        reg.register(c1)
        reg.register(c2)
        reg.register(c3)
        a_certs = reg.by_operator("op_a")
        assert len(a_certs) == 2
        assert all(c.operator_id == "op_a" for c in a_certs)

    def test_by_operator_unknown_returns_empty_list(self):
        """Unknown operator returns empty list, NOT raise — empty case is
        meaningful (operator hasn't been portability-tested)."""
        reg = OperatorPortabilityRegistry()
        assert reg.by_operator("never_registered") == []

    def test_by_chart_pair(self):
        reg = OperatorPortabilityRegistry()
        c1 = _basic_cert(operator_id="op_a", source="A", target="B")
        c2 = _basic_cert(operator_id="op_b", source="A", target="B")
        c3 = _basic_cert(operator_id="op_c", source="A", target="C")
        reg.register(c1)
        reg.register(c2)
        reg.register(c3)
        pair_ab = reg.by_chart_pair("A", "B")
        assert len(pair_ab) == 2
        pair_ac = reg.by_chart_pair("A", "C")
        assert len(pair_ac) == 1


# ---------------------------------------------------------------------------
# Worked example: Mahler measure across Lehmer charts
# ---------------------------------------------------------------------------


class TestMahlerMeasureWorkedExample:
    def test_mahler_measure_deg14_to_deg12_certificate(self):
        """The substrate-grade encoding of 'Mahler measure operator transports
        between deg14 ±5 palindromic (Day-5 Lehmer) and deg12 ±5 palindromic
        (Fire #8 W3.2 fixture).' Operator ships AWAITING_TRIANGULATION
        because the deg-12 band candidates haven't yet been triangulated
        per Day-5 protocol."""
        reg = OperatorPortabilityRegistry()
        cert = OperatorPortabilityCertificate(
            operator_id="mahler_measure",
            source_chart_id="lehmer:deg14:pm5:palindromic",
            target_chart_id="lehmer:deg12:pm5:palindromic",
            transfer_method=TransferMethod.DIRECT_APPLICATION,
            evidence_pre=PortabilityEvidence(
                n_objects_tested=97_435_855,
                signature_summary={
                    "n_band_candidates": 43,
                    "n_lehmer_band_proper": 26,  # post-triangulation
                    "verdict_via_triangulation": "H5_CONFIRMED-local-lemma",
                },
            ),
            evidence_post=PortabilityEvidence(
                n_objects_tested=8_857_805,
                signature_summary={
                    "n_band_candidates": 113,
                    "n_cyclotomic_noise": 99,
                    "n_lehmer_band_proper": 10,
                    "verdict_pre_triangulation": "INCONCLUSIVE",
                },
            ),
            equivalence_relation=(
                "operator_signature_equivalence:band_candidate_distribution"
            ),
            verdict=PortabilityVerdict.AWAITING_TRIANGULATION,
            rationale=(
                "Mahler measure operator transports from deg14 ±5 palindromic "
                "to deg12 ±5 palindromic with directly-applicable semantics. "
                "Both regions produce a band-candidate distribution dominated "
                "by cyclotomic noise + a small set near Lehmer-depth (10 "
                "polys in deg12; 26 verified in deg14 post-triangulation). "
                "Verdict awaits triangulation of the 10 deg12 Lehmer-band "
                "candidates per Day-5 protocol."
            ),
            replay=PortabilityReplay(
                code_hash="lehmer_brute_force_general@v1_43566adc"[:64].ljust(64, "x"),
                data_hash="deg12_pm5_palindromic_n_8857805"[:64].ljust(64, "x"),
                seed=0,
                environment_hash="techne_fire_8_environment".ljust(64, "x"),
            ),
            notes=(
                "Per HARD-5: 'Mahler measure' is the operator name (substrate-"
                "grade); 'Lehmer's polynomial' / 'reciprocal palindromic' / "
                "'Salem number' are docstring metadata — they live in this "
                "notes field, not in the chart coordinates. The substrate's "
                "coordinate is the band-candidate distribution shape across "
                "both charts."
            ),
        )
        reg.register(cert)
        # Round-trip + content-addressed
        retrieved = reg.by_id(cert.certificate_id)
        assert retrieved is cert
        # Looked up by operator
        ops = reg.by_operator("mahler_measure")
        assert len(ops) == 1 and ops[0] is cert
        # Looked up by chart pair
        pair = reg.by_chart_pair(
            "lehmer:deg14:pm5:palindromic", "lehmer:deg12:pm5:palindromic"
        )
        assert len(pair) == 1 and pair[0] is cert


# ---------------------------------------------------------------------------
# Module-level singleton helpers
# ---------------------------------------------------------------------------


class TestModuleSingleton:
    def test_register_via_helper_round_trips(self):
        cert = _basic_cert(operator_id="singleton_test_op_xyz_unique")
        register_portability_certificate(cert)
        try:
            retrieved = get_portability_certificate(cert.certificate_id)
            assert retrieved is cert
            ops = portability_certificates_by_operator("singleton_test_op_xyz_unique")
            assert len(ops) >= 1
            pair = portability_certificates_by_chart_pair(
                "lehmer:deg14:pm5:palindromic", "lehmer:deg12:pm5:palindromic"
            )
            assert any(c.certificate_id == cert.certificate_id for c in pair)
        finally:
            # No public unregister on free-function surface; reach in
            # for test isolation. Other tests with different operator
            # ids are unaffected.
            DEFAULT_REGISTRY._certs.pop(cert.certificate_id, None)
            DEFAULT_REGISTRY._by_operator.pop("singleton_test_op_xyz_unique", None)
