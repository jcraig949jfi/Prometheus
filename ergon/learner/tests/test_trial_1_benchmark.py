"""Tests for Trial 1 residual benchmark assembly."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ergon.learner.trials.trial_1_residual_benchmark import (
    BenchmarkSample,
    assemble_benchmark,
    generate_obvious_noise_samples,
    generate_synthetic_structured_noise_samples,
    serialize_benchmark,
)


# ---------------------------------------------------------------------------
# Authority — sample counts match v8 spec
# ---------------------------------------------------------------------------


def test_obvious_noise_count():
    """Pass A: 50 obvious-noise samples (10 per sub-class * 5 sub-classes)."""
    samples = generate_obvious_noise_samples(seed=0)
    assert len(samples) == 50
    assert all(s.sample_class == "obvious_noise" for s in samples)
    assert all(s.true_label == "noise" for s in samples)


def test_synthetic_structured_noise_count():
    """Pass C: 100 synthetic structured-noise samples (30+30+20+20)."""
    samples = generate_synthetic_structured_noise_samples(seed=1)
    assert len(samples) == 100
    assert all(s.sample_class == "synthetic_structured_noise" for s in samples)
    assert all(s.true_label == "noise" for s in samples)


def test_full_day1_seed_assembly():
    """Day 1 produces obvious + 2-sample borderline seed + synthetic = 152 samples."""
    samples = assemble_benchmark()
    n_obvious = sum(1 for s in samples if s.sample_class == "obvious_noise")
    n_borderline = sum(1 for s in samples if s.sample_class == "borderline_signal")
    n_synthetic = sum(1 for s in samples if s.sample_class == "synthetic_structured_noise")
    assert n_obvious == 50
    assert n_borderline == 2  # Day 1 seed; Day 2 fills to 50
    assert n_synthetic == 100
    assert len(samples) == 152


# ---------------------------------------------------------------------------
# Property — failure_shape carries classifier-relevant fields
# ---------------------------------------------------------------------------


def test_obvious_noise_has_no_canonicalizer_subclass():
    """Obvious noise should never carry a canonicalizer subclass tag."""
    samples = generate_obvious_noise_samples(seed=0)
    for s in samples:
        assert s.failure_shape.get("canonicalizer_subclass") is None


def test_synthetic_structured_noise_carries_subclass_collisions():
    """Sub-class C2 (subclass collision) should have one of four canonicalizer subclasses."""
    samples = generate_synthetic_structured_noise_samples(seed=1)
    c2_samples = [s for s in samples if s.sample_id.startswith("C2_")]
    assert len(c2_samples) == 30
    valid_subclasses = {
        "group_quotient", "partition_refinement",
        "ideal_reduction", "variety_fingerprint",
    }
    for s in c2_samples:
        assert s.failure_shape["canonicalizer_subclass"] in valid_subclasses


def test_high_variance_synthetic_above_classifier_threshold():
    """Sub-class C1 should have coeff_variance > 0.5 (the classifier signal threshold)."""
    samples = generate_synthetic_structured_noise_samples(seed=1)
    c1_samples = [s for s in samples if s.sample_id.startswith("C1_")]
    assert len(c1_samples) == 30
    # All samples should be designed to TRIGGER the classifier (false positives expected)
    for s in c1_samples:
        assert s.failure_shape["coeff_variance"] > 0.5


# ---------------------------------------------------------------------------
# Edge — determinism via seed
# ---------------------------------------------------------------------------


def test_seed_determinism_obvious():
    """Same seed produces same samples."""
    s1 = generate_obvious_noise_samples(seed=42)
    s2 = generate_obvious_noise_samples(seed=42)
    assert s1 == s2


def test_seed_determinism_synthetic():
    """Same seed produces same samples (synthetic class)."""
    s1 = generate_synthetic_structured_noise_samples(seed=42)
    s2 = generate_synthetic_structured_noise_samples(seed=42)
    assert s1 == s2


def test_different_seeds_produce_different_samples():
    """Different seeds produce different random content."""
    s1 = generate_obvious_noise_samples(seed=0)
    s2 = generate_obvious_noise_samples(seed=1)
    # Sample IDs are deterministic from index, but failure_shape values should differ
    f1 = s1[0].failure_shape
    f2 = s2[0].failure_shape
    assert f1 != f2


# ---------------------------------------------------------------------------
# Composition — serialization roundtrip
# ---------------------------------------------------------------------------


def test_serialize_benchmark_roundtrip(tmp_path: Path):
    """Benchmark serializes to JSON; -inf magnitudes encode as sentinel."""
    samples = assemble_benchmark()
    out_path = tmp_path / "benchmark.json"
    serialize_benchmark(samples, out_path)
    assert out_path.exists()
    data = json.loads(out_path.read_text())
    assert len(data) == 152
    # Verify -inf magnitude encoded as None sentinel for empty/zero samples
    a5_entries = [d for d in data if d["sample_id"].startswith("A5_")]
    assert len(a5_entries) == 10
    # Half of A5 samples have magnitude -inf; should be encoded as None
    none_magnitude_count = sum(
        1 for d in a5_entries if d["failure_shape"].get("magnitude_log10") is None
    )
    assert none_magnitude_count == 5  # half of 10
