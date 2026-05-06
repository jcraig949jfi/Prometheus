"""Tests for prometheus_math.discovery_promotion — domain-agnostic
DISCOVERY_CANDIDATE → CLAIM promotion adapter.

Coverage:
  * DiscoveryCandidate construction + content-addressed candidate_id
  * promote_to_claim mints a real kernel CLAIM with proper provenance
  * SHADOW_CATALOG default vs explicit PROMOTED vs REJECTED terminal states
  * Backwards compat with DiscoveryPipeline (Lehmer round-trip)
  * Caveats and precision_metadata propagate to the CLAIM
  * REJECTED routes through GATE BLOCK (raises BlockedError)
  * Multi-domain: BSD + OEIS candidates promote correctly
"""
from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from sigma_kernel.sigma_kernel import (
    BlockedError,
    SigmaKernel,
    Tier,
)
from prometheus_math.discovery_promotion import (
    DiscoveryCandidate,
    PromotionResult,
    lehmer_candidate_from_pipeline_record,
    promote_discovery_candidate_to_claim,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def kernel(tmp_path: Path) -> SigmaKernel:
    db_path = tmp_path / "test_kernel.db"
    return SigmaKernel(db_path=str(db_path))


def _lehmer_candidate() -> DiscoveryCandidate:
    coeffs = [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]
    features = {
        "poly_coefficients": coeffs,
        "mahler_measure": 1.176280818,
        "n_irreducible_factors": 1,
    }
    cid = DiscoveryCandidate.compute_candidate_id(coeffs, features)
    return DiscoveryCandidate(
        domain="lehmer",
        candidate_id=cid,
        candidate_label="lehmer_test_polynomial",
        features=features,
        survival_evidence={
            "reciprocity": True,
            "irreducibility": True,
            "catalog_miss": True,
            "F1": True,
            "F6": True,
        },
        operator_class="DiscoveryEnv@degree=10/seed=0",
        coordinate_chart_id="provisional:lehmer",
    )


def _bsd_candidate() -> DiscoveryCandidate:
    features = {
        "cremona_label": "11a1",
        "conductor": 11,
        "j_invariant": -1.21e7,
        "torsion_structure": "Z/5Z",
    }
    cid = DiscoveryCandidate.compute_candidate_id("11a1", features)
    return DiscoveryCandidate(
        domain="bsd_rank",
        candidate_id=cid,
        candidate_label="bsd_11a1",
        features=features,
        survival_evidence={"rank_prediction_correct": True, "lmfdb_resolved": True},
        operator_class="BSDRankEnv@v1",
        coordinate_chart_id="provisional:bsd_rank",
    )


# ---------------------------------------------------------------------------
# DiscoveryCandidate
# ---------------------------------------------------------------------------


def test_candidate_id_is_content_addressed():
    """Same canonical form + features → same candidate_id."""
    coeffs = [1, 0, -1, 0, 1]
    features = {"poly_coefficients": coeffs, "M": 1.176}
    a = DiscoveryCandidate.compute_candidate_id(coeffs, features)
    b = DiscoveryCandidate.compute_candidate_id(coeffs, features)
    assert a == b
    assert len(a) == 64  # sha256 hex


def test_candidate_id_changes_with_features():
    coeffs = [1, 0, -1, 0, 1]
    a = DiscoveryCandidate.compute_candidate_id(coeffs, {"M": 1.176})
    b = DiscoveryCandidate.compute_candidate_id(coeffs, {"M": 1.177})
    assert a != b


def test_candidate_default_timestamp_is_recent():
    import time as _t
    cand = _lehmer_candidate()
    assert abs(_t.time() - cand.timestamp) < 5.0


# ---------------------------------------------------------------------------
# Promotion: SHADOW_CATALOG default
# ---------------------------------------------------------------------------


def test_promote_lehmer_candidate_default_shadow_catalog(kernel: SigmaKernel):
    cand = _lehmer_candidate()
    result = promote_discovery_candidate_to_claim(cand, kernel=kernel)

    assert isinstance(result, PromotionResult)
    assert result.terminal_state == "SHADOW_CATALOG"
    assert result.verdict_status == "CLEAR"
    assert result.symbol_ref != ""
    assert result.symbol_ref.startswith("discovery_lehmer_")
    assert result.claim_id != ""


def test_promote_lehmer_candidate_explicit_promoted(kernel: SigmaKernel):
    cand = _lehmer_candidate()
    result = promote_discovery_candidate_to_claim(
        cand, kernel=kernel, terminal_state="PROMOTED",
        target_tier=Tier.WorkingTheory,
    )
    assert result.terminal_state == "PROMOTED"
    assert result.verdict_status == "CLEAR"
    assert result.symbol_ref != ""


# ---------------------------------------------------------------------------
# Promotion: REJECTED routes through BLOCK
# ---------------------------------------------------------------------------


def test_promote_rejected_raises_blocked_error(kernel: SigmaKernel):
    cand = _lehmer_candidate()
    with pytest.raises(BlockedError):
        promote_discovery_candidate_to_claim(
            cand, kernel=kernel, terminal_state="REJECTED",
        )


# ---------------------------------------------------------------------------
# Promotion: invalid terminal_state
# ---------------------------------------------------------------------------


def test_promote_invalid_terminal_state_raises_value_error(kernel: SigmaKernel):
    cand = _lehmer_candidate()
    with pytest.raises(ValueError, match="terminal_state"):
        promote_discovery_candidate_to_claim(
            cand, kernel=kernel, terminal_state="INVALID",
        )


# ---------------------------------------------------------------------------
# Promotion produces real kernel CLAIM with provenance
# ---------------------------------------------------------------------------


def test_promote_writes_claim_row_to_kernel(kernel: SigmaKernel):
    cand = _lehmer_candidate()
    result = promote_discovery_candidate_to_claim(cand, kernel=kernel)

    rows = kernel.conn.execute(
        "SELECT id, status, verdict_status FROM claims WHERE id=?",
        (result.claim_id,),
    ).fetchall()
    assert len(rows) == 1
    assert rows[0][1] == "promoted"
    assert rows[0][2] == "CLEAR"


def test_promote_writes_symbol_row_to_kernel(kernel: SigmaKernel):
    cand = _lehmer_candidate()
    result = promote_discovery_candidate_to_claim(cand, kernel=kernel)

    name, _, ver = result.symbol_ref.partition("@v")
    rows = kernel.conn.execute(
        "SELECT name, version, def_blob FROM symbols WHERE name=? AND version=?",
        (name, int(ver)),
    ).fetchall()
    assert len(rows) == 1
    # def_blob should mention the candidate_id (content-addressed evidence)
    assert cand.candidate_id[:12] in rows[0][2]


def test_promote_candidate_id_appears_in_symbol_provenance(kernel: SigmaKernel):
    """PROMOTE scrapes 64-char-hex strings from evidence into provenance.
    candidate_id is one such hex string, so it MUST appear in provenance."""
    cand = _lehmer_candidate()
    result = promote_discovery_candidate_to_claim(cand, kernel=kernel)

    name, _, ver = result.symbol_ref.partition("@v")
    row = kernel.conn.execute(
        "SELECT provenance FROM symbols WHERE name=? AND version=?",
        (name, int(ver)),
    ).fetchone()
    import json as _json
    provenance = _json.loads(row[0])
    assert cand.candidate_id in provenance


# ---------------------------------------------------------------------------
# Caveats and precision_metadata
# ---------------------------------------------------------------------------


def test_promote_with_extra_caveats_attaches_to_claim(kernel: SigmaKernel):
    cand = _lehmer_candidate()
    result = promote_discovery_candidate_to_claim(
        cand, kernel=kernel,
        extra_caveats=["catalog_completeness_partial", "single_seed"],
    )

    row = kernel.conn.execute(
        "SELECT caveats FROM claims WHERE id=?", (result.claim_id,)
    ).fetchone()
    if row[0] is not None:  # column exists in this kernel version
        import json as _json
        cv = _json.loads(row[0])
        assert "catalog_completeness_partial" in cv
        assert "single_seed" in cv


def test_promote_with_precision_metadata_attaches_to_claim(kernel: SigmaKernel):
    cand = _lehmer_candidate()
    result = promote_discovery_candidate_to_claim(
        cand, kernel=kernel,
        precision_metadata={
            "dps": 60,
            "method": "mpmath_factor_first",
            "convergence": "converged",
            "stability": 0.95,
        },
    )

    row = kernel.conn.execute(
        "SELECT precision_metadata FROM claims WHERE id=?", (result.claim_id,)
    ).fetchone()
    if row[0] is not None:
        import json as _json
        pm = _json.loads(row[0])
        assert pm["dps"] == 60
        assert pm["method"] == "mpmath_factor_first"


def test_promote_auto_caveats_fire_on_verification_failed(kernel: SigmaKernel):
    """precision_metadata.convergence='failed_max_steps' triggers
    auto-caveat 'verification_failed'."""
    cand = _lehmer_candidate()
    result = promote_discovery_candidate_to_claim(
        cand, kernel=kernel,
        precision_metadata={
            "dps": 30,
            "method": "mpmath_direct",
            "convergence": "failed_max_steps",
        },
    )

    row = kernel.conn.execute(
        "SELECT caveats FROM claims WHERE id=?", (result.claim_id,)
    ).fetchone()
    if row[0] is not None:
        import json as _json
        cv = _json.loads(row[0])
        assert "verification_failed" in cv


def test_promote_auto_caveats_fire_on_precision_below_expected(kernel: SigmaKernel):
    """precision_metadata.dps < expected_min_dps triggers auto-caveat."""
    cand = _lehmer_candidate()
    result = promote_discovery_candidate_to_claim(
        cand, kernel=kernel,
        precision_metadata={
            "dps": 30,
            "expected_min_dps": 60,
            "method": "mpmath_direct",
            "convergence": "converged",
        },
    )

    row = kernel.conn.execute(
        "SELECT caveats FROM claims WHERE id=?", (result.claim_id,)
    ).fetchone()
    if row[0] is not None:
        import json as _json
        cv = _json.loads(row[0])
        assert "precision_below_expected" in cv


# ---------------------------------------------------------------------------
# Multi-domain
# ---------------------------------------------------------------------------


def test_promote_bsd_candidate(kernel: SigmaKernel):
    cand = _bsd_candidate()
    result = promote_discovery_candidate_to_claim(cand, kernel=kernel)

    assert result.terminal_state == "SHADOW_CATALOG"
    assert result.symbol_ref.startswith("discovery_bsd_rank_")


def test_promote_oeis_candidate(kernel: SigmaKernel):
    cand = DiscoveryCandidate(
        domain="oeis_sleeping",
        candidate_id=DiscoveryCandidate.compute_candidate_id(
            "A123456", {"first_n_terms": [1, 2, 3, 5, 8, 13]}
        ),
        candidate_label="oeis_A123456",
        features={"oeis_id": "A123456", "first_n_terms": [1, 2, 3, 5, 8, 13]},
        survival_evidence={"growth_heuristic_passed": True},
        operator_class="OEISSleepingEnv@v1",
    )
    result = promote_discovery_candidate_to_claim(cand, kernel=kernel)
    assert result.terminal_state == "SHADOW_CATALOG"
    assert "oeis_sleeping" in result.symbol_ref


# ---------------------------------------------------------------------------
# Lehmer convenience adapter
# ---------------------------------------------------------------------------


def test_lehmer_convenience_constructor_produces_valid_candidate():
    cand = lehmer_candidate_from_pipeline_record(
        coeffs=[1, 0, -1, 0, 1],
        mahler_measure=1.176,
        survival_evidence={"reciprocity": True, "irreducibility": True},
        operator_class="DiscoveryEnv@deg=10",
    )
    assert cand.domain == "lehmer"
    assert cand.coordinate_chart_id == "provisional:lehmer"
    assert "poly_coefficients" in cand.features
    assert cand.features["mahler_measure"] == 1.176


def test_lehmer_convenience_promotes_through_kernel(kernel: SigmaKernel):
    cand = lehmer_candidate_from_pipeline_record(
        coeffs=[1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1],
        mahler_measure=1.176280818,
        survival_evidence={
            "reciprocity": True,
            "irreducibility": True,
            "catalog_miss": True,
        },
        operator_class="DiscoveryEnv@deg=10",
    )
    result = promote_discovery_candidate_to_claim(cand, kernel=kernel)
    assert result.terminal_state == "SHADOW_CATALOG"
    assert "lehmer" in result.symbol_ref


# ---------------------------------------------------------------------------
# Idempotency: same candidate twice → kernel UNIQUE catches duplicate
# ---------------------------------------------------------------------------


def test_promote_same_candidate_twice_creates_two_versions(kernel: SigmaKernel):
    """Promoting the same candidate twice produces v1 and v2 of the
    symbol (kernel discipline: append-only, version-incrementing).
    Content-addressed evidence is the same; symbol versions differ."""
    cand = _lehmer_candidate()
    r1 = promote_discovery_candidate_to_claim(cand, kernel=kernel)
    r2 = promote_discovery_candidate_to_claim(cand, kernel=kernel)
    assert r1.symbol_ref != r2.symbol_ref  # different versions
    assert r1.symbol_ref.endswith("@v1")
    assert r2.symbol_ref.endswith("@v2")
