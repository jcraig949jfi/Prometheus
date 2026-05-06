"""The deg14 ±5 palindromic Lehmer brute-force exclusion certificate.

Per substrate v2.3 §6.3 prototype:
    certificate_type = exhaustive_enumeration
    initial_verdict   = INCONCLUSIVE with 17 borderline near-cyclotomic entries
    strength          = complete (earned via Path A/B/C/D triangulation)

Path A: high-precision mpmath at dps=60 verified all 17 borderline
        entries factor cleanly (no novel band hits).
Path B: symbolic factorization via sympy.factor_list confirmed the
        cyclotomic + composite split.
Path C: factorization-aware catalog lookup matched all entries against
        Mossinghoff and Lehmer × Φ_n^k composites.
Path D: Lehmer × Φ_n^k composite-detection algorithm classified all 17
        entries as Lehmer × Φ_n^k composites for k ≥ 2.

Hash placeholders
-----------------
``code_hash``, ``data_hash``, ``environment_hash`` are placeholder sha256
digests. The point of this module is the certificate *schema*, not the
historical re-execution; populating real hashes would require attaching
the brute-force run's actual code/data fingerprint, which is a separate
concern (Path-D-replay tooling).

The MethodSpec entries are also schema placeholders — they record the
``independence_class`` (which is the load-bearing field for triangulation
independence) but use stub engine/strategy strings rather than the real
implementation handles.
"""
from __future__ import annotations

import hashlib

# Importing the chart package ensures the Lehmer chart is registered before
# this certificate registers (the chart_id validation in register_certificate
# would otherwise fail on cold-load).
from sigma_kernel import coordinate_charts  # noqa: F401  (side-effect import)
from sigma_kernel.exclusion_certificate import (
    Boundary,
    CertificateStrength,
    CertificateType,
    ExclusionCertificate,
    ExclusionClaim,
    RegionSpec,
    ReplayInfo,
    TriangulationPathRef,
    VerifierSet,
    register_certificate,
)
from sigma_kernel.method_spec import IndependenceClass, MethodSpec


# ---------------------------------------------------------------------------
# Placeholder hash utility
# ---------------------------------------------------------------------------


def _placeholder_hash(label: str) -> str:
    """Deterministic sha256 placeholder keyed off a label.

    Stable across runs (same label → same hash) so the certificate_id is
    reproducible in tests, but obviously not the *real* code/data hash —
    populating those is downstream Path-D-replay tooling work."""
    return hashlib.sha256(f"PLACEHOLDER:{label}".encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# MethodSpec stubs for each of the four triangulation paths
# ---------------------------------------------------------------------------


_PATH_A_METHOD = MethodSpec(
    engine="mpmath",
    strategy="factor_first",
    precision_dps=60,
    version="1.0.0",
    parameters={"dps": 60, "factor_first": True},
    independence_class=IndependenceClass.MPMATH_POLYNOMIAL_FACTORIZATION,
)

_PATH_B_METHOD = MethodSpec(
    engine="sympy",
    strategy="factor_list",
    version="1.0.0",
    parameters={"domain": "ZZ"},
    independence_class=IndependenceClass.SYMPY_SYMBOLIC_FACTORIZATION,
)

_PATH_C_METHOD = MethodSpec(
    engine="catalog",
    strategy="mahler_lookup",
    version="1.0.0",
    parameters={"catalog": "Mossinghoff+LehmerPhiNK"},
    independence_class=IndependenceClass.MAHLER_LOOKUP_CATALOG,
)

_PATH_D_METHOD = MethodSpec(
    engine="custom",
    strategy="phi_n_k_composite_detection",
    version="1.0.0",
    parameters={"min_k": 2, "phi_family": "cyclotomic"},
    # Composite-detection is a literature-cross-check style verifier — it
    # cross-references known Lehmer × Φ_n^k composites in the literature.
    independence_class=IndependenceClass.LITERATURE_CROSS_CHECK,
)


# ---------------------------------------------------------------------------
# TriangulationPathRefs (P6 placeholder structure)
# ---------------------------------------------------------------------------


# Frozen-in-time placeholder timestamp for reproducibility (the real run
# happened across the 2026-05-01 → 2026-05-05 sprint, but that timestamp
# is recorded in trial ledgers; the certificate id should not drift on it).
_FROZEN_TS = 0.0

_PATH_A_REF = TriangulationPathRef(
    path_id="path_a_high_precision_mpmath_dps60",
    method_spec=_PATH_A_METHOD,
    verdict="verified",
    timestamp=_FROZEN_TS,
    summary=(
        "Path A: high-precision mpmath at dps=60 verified all 17 borderline "
        "entries factor cleanly (no novel band hits)."
    ),
)

_PATH_B_REF = TriangulationPathRef(
    path_id="path_b_symbolic_factorization",
    method_spec=_PATH_B_METHOD,
    verdict="verified",
    timestamp=_FROZEN_TS,
    summary=(
        "Path B: symbolic factorization via sympy.factor_list confirmed "
        "cyclotomic + composite split."
    ),
)

_PATH_C_REF = TriangulationPathRef(
    path_id="path_c_factorization_aware_catalog",
    method_spec=_PATH_C_METHOD,
    verdict="verified",
    timestamp=_FROZEN_TS,
    summary=(
        "Path C: factorization-aware catalog lookup matched all 17 entries "
        "to Mossinghoff + Lehmer × Φ_n^k catalog."
    ),
)

_PATH_D_REF = TriangulationPathRef(
    path_id="path_d_lehmer_phi_n_k_composite_detection",
    method_spec=_PATH_D_METHOD,
    verdict="verified",
    timestamp=_FROZEN_TS,
    summary=(
        "Path D: composite detection algorithm identified all 17 borderline "
        "entries as Lehmer × Φ_n^k composites for k ≥ 2."
    ),
)


# ---------------------------------------------------------------------------
# The certificate
# ---------------------------------------------------------------------------


LEHMER_DEG14_PM5_PALINDROMIC_EXCLUSION = ExclusionCertificate(
    region_spec=RegionSpec(
        coordinate_chart_id="lehmer:deg14:pm5:palindromic",
        constraints={"degree": 14, "coefficient_bound": 5, "palindromic": True},
        bounds={"n_polynomials_enumerated": 97_435_855},
    ),
    exclusion_claim=ExclusionClaim(
        excluded_property=(
            "novel Lehmer band hit beyond known cyclotomic x Phi_n^k composites "
            "(M in (1.001, 1.18))"
        ),
        result_class="novel_lehmer_band_hit",
        reason=(
            "Exhaustive enumeration of 97,435,855 deg-14 +/-5 palindromic "
            "polynomials. 253 raw band candidates -> 210 cyclotomic-noise "
            "filtered -> 43 verified band hits, all classifiable as known "
            "cyclotomic x Phi_n^k composites after Path A/B/C/D triangulation."
        ),
    ),
    certificate_type=CertificateType.EXHAUSTIVE_ENUMERATION,
    strength=CertificateStrength.COMPLETE,
    verifier_set=VerifierSet(
        methods=(
            _PATH_A_METHOD,
            _PATH_B_METHOD,
            _PATH_C_METHOD,
            _PATH_D_METHOD,
        ),
        # Auto-derived from the four MethodSpecs' independence_class fields.
        independence_classes=frozenset(),
    ),
    replay=ReplayInfo(
        code_hash=_placeholder_hash("lehmer_deg14_pm5_palindromic:code"),
        data_hash=_placeholder_hash("lehmer_deg14_pm5_palindromic:data"),
        seed=0,
        environment_hash=_placeholder_hash("lehmer_deg14_pm5_palindromic:env"),
    ),
    triangulation_history=(
        _PATH_A_REF,
        _PATH_B_REF,
        _PATH_C_REF,
        _PATH_D_REF,
    ),
    initial_verdict=(
        "INCONCLUSIVE with 17 borderline near-cyclotomic entries; substrate "
        "refused to overclaim until triangulation completed"
    ),
    upgrade_path_summary=(
        "Path A: high-precision mpmath at dps=60 verified all 17 entries factor cleanly",
        "Path B: symbolic factorization via sympy.factor_list confirmed cyclotomic + composite split",
        "Path C: factorization-aware catalog lookup matched all entries to Mossinghoff + Lehmer x Phi_n^k",
        "Path D: composite detection algorithm identified all 17 as Lehmer x Phi_n^k for k>=2",
    ),
    boundary=Boundary(
        adjacent_regions=(
            "lehmer:deg12:pm5:palindromic",
            "lehmer:deg14:pm3:palindromic",
        ),
        known_escape_hatches=(
            "non-palindromic deg-14 not enumerated",
            "coefficients > 5 not enumerated",
        ),
    ),
)
"""The Lehmer ``deg14:pm5:palindromic`` exclusion certificate. Registered
at module import time. Substrate v2.3 §6.3 prototype."""


# Register at import time -----------------------------------------------------
register_certificate(LEHMER_DEG14_PM5_PALINDROMIC_EXCLUSION)


__all__ = [
    "LEHMER_DEG14_PM5_PALINDROMIC_EXCLUSION",
]
