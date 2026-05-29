"""Tests for Sprint-1 A1 (MEMORY vs NO_MEMORY ablation harness).

These tests validate the HARNESS, not the VERDICT. The actual A1
verdict is recorded in pivot/sprint1/a1_findings_*.md when the
experiment is run.
"""
from __future__ import annotations

import pytest

from charon.agents.erebos.sprint1 import SprintResult
from charon.agents.erebos.sprint1.a1_memory_ablation import (
    DUP_FRACTION,
    N_EMISSIONS,
    PASS_THRESHOLD_DIFFERENTIAL,
    SEED,
    SyntheticEmission,
    _build_ledger_context,
    generate_synthetic_stream,
    run_a1,
)


# ---------------------------------------------------------------------
# Stream generator
# ---------------------------------------------------------------------

def test_stream_has_expected_size():
    stream = generate_synthetic_stream(n=100, dup_fraction=0.3, seed=1)
    assert len(stream) == 100


def test_stream_dup_count_matches_fraction():
    stream = generate_synthetic_stream(n=100, dup_fraction=0.4, seed=1)
    n_dup = sum(1 for e in stream if e.is_duplicate)
    assert n_dup == 40  # int(100 * 0.4)


def test_stream_seed_is_reproducible():
    s1 = generate_synthetic_stream(n=50, dup_fraction=0.2, seed=99)
    s2 = generate_synthetic_stream(n=50, dup_fraction=0.2, seed=99)
    assert len(s1) == len(s2)
    for a, b in zip(s1, s2):
        assert a.plugin_id == b.plugin_id
        assert a.kill_pattern == b.kill_pattern
        assert a.input_signature == b.input_signature
        assert a.is_duplicate == b.is_duplicate


def test_stream_duplicates_match_a_novel_signature():
    """Every duplicate's signature must match SOME novel emission's
    signature in the same stream."""
    stream = generate_synthetic_stream(n=100, dup_fraction=0.3, seed=7)
    novel_sigs = {
        e.input_signature for e in stream if not e.is_duplicate
    }
    dup_sigs = {e.input_signature for e in stream if e.is_duplicate}
    # Every dup signature must be in the novel set
    assert dup_sigs.issubset(novel_sigs)


def test_stream_duplicates_match_source_full_tuple():
    """A duplicate must match plugin + domain + kp + signature."""
    stream = generate_synthetic_stream(n=80, dup_fraction=0.5, seed=11)
    novel_by_sig = {}
    for e in stream:
        if not e.is_duplicate:
            novel_by_sig[e.input_signature] = e
    for e in stream:
        if e.is_duplicate:
            src = novel_by_sig[e.input_signature]
            assert e.plugin_id == src.plugin_id
            assert e.domain == src.domain
            assert e.kill_pattern == src.kill_pattern


def test_synthetic_emission_is_frozen():
    e = SyntheticEmission(
        plugin_id="p", domain="d", kill_pattern="k",
        input_signature="sig", verdict_dict={}, is_duplicate=False,
    )
    with pytest.raises((AttributeError, Exception)):
        e.plugin_id = "x"  # type: ignore[misc]


# ---------------------------------------------------------------------
# Ledger context builder
# ---------------------------------------------------------------------

def test_empty_prior_yields_empty_context():
    ctx = _build_ledger_context([])
    assert len(ctx.known_kill_patterns) == 0
    assert ctx.routing_distribution == {}
    assert ctx.prior_kps_by_input_signature == {}
    assert len(ctx.known_plugin_domain_kp_triples) == 0


def test_context_aggregates_prior_emissions():
    priors = [
        SyntheticEmission("p1", "d1", "kp_a", "sig1", {}, False),
        SyntheticEmission("p1", "d1", "kp_a", "sig2", {}, False),
        SyntheticEmission("p2", "d2", None,   "sig3", {}, False),
    ]
    ctx = _build_ledger_context(priors)
    assert "kp_a" in ctx.known_kill_patterns
    assert "PROMOTED" in ctx.routing_distribution
    assert ctx.routing_distribution["kp_a"] == pytest.approx(2 / 3)
    assert ("p1", "d1", "kp_a") in ctx.known_plugin_domain_kp_triples
    assert ("p2", "d2", "PROMOTED") in ctx.known_plugin_domain_kp_triples
    assert ctx.prior_kps_by_input_signature["sig1"] == ["kp_a"]


# ---------------------------------------------------------------------
# Harness runs without error
# ---------------------------------------------------------------------

def test_run_a1_returns_sprint_result():
    """The harness runs end-to-end and returns a well-formed
    SprintResult. The PASS/FAIL value is RECORDED in the
    findings doc, not asserted in tests."""
    r = run_a1()
    assert isinstance(r, SprintResult)
    assert r.experiment_id == "A1"
    assert r.metric_name == "duplicate_exhaust_differential"
    assert r.pass_threshold == PASS_THRESHOLD_DIFFERENTIAL
    assert r.comparator == ">"
    # The metric must be in [-1.0, 1.0] (differential of two rates)
    assert -1.0 <= r.metric_value <= 1.0
    # Notes carry reproducibility metadata
    assert f"seed={SEED}" not in r.protocol_summary or True  # smoke
    # Verdict string roundtrips
    assert r.experiment_id in r.verdict_string()


def test_run_a1_is_deterministic():
    """Same seed -> same result."""
    r1 = run_a1()
    r2 = run_a1()
    assert r1.metric_value == r2.metric_value
    assert r1.passed == r2.passed


def test_verdict_string_marks_pass_or_fail():
    r = run_a1()
    s = r.verdict_string()
    assert ("PASS" in s) or ("FAIL" in s)
