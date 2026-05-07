"""E003 — regression-lock the W4.7 LR-control trivial-feature ceiling.

The trivial-feature ceiling (cls_post_fold 17/17 = 1.000; cls 16/17 = 0.941)
is the headroom benchmark for v0.5 / v0.5b LoRA tire-kicks (LoRA must
clear 0.941 on 4-way to demonstrate non-trivial learning). If the LR
baseline drifts silently, every downstream verdict is mis-anchored.

These tests verify:
1. LR-control output is byte-identical across 3 fresh runs (deterministic
   given fixture + sklearn random_state=42).
2. The headroom-benchmark numbers match the v0.5 finding documented in
   TIRE_KICK_v0.5_RESULT_2026-05-06.md §4.4 (cls_post_fold acc=1.000;
   cls acc=0.941).
3. Reproducibility metadata block is present (python/sklearn/numpy
   versions + fixture content hash + lr_random_state).

Test file matches the ticket-specified name `test_lr_control_reproducibility.py`.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ergon.pipeline_d.lr_control import (
    _LR_RANDOM_STATE,
    _fixture_content_hash,
    run_lr_control,
)


@pytest.fixture(scope="module")
def three_runs(tmp_path_factory):
    """Run lr_control 3 times in fresh temp directories so we don't
    pollute the canonical results JSON. Each run is a fresh process-
    boundary-equivalent: fresh fixture load, fresh classifier instance,
    fresh JSON write."""
    runs = []
    for i in range(3):
        out_dir = tmp_path_factory.mktemp(f"lr_control_run_{i}")
        result = run_lr_control(out_dir=out_dir)
        runs.append(result)
    return runs


def test_three_runs_byte_identical_per_label_field(three_runs):
    """Acceptance criterion 1: fresh runs produce identical accuracies.

    LR is deterministic given (fixture, sklearn random_state). Three runs
    must yield byte-identical accuracy + n_correct + n_total + per-class
    breakdown for both label fields."""
    keys_to_check = (
        "train_accuracy",
        "heldout_accuracy",
        "n_correct",
        "n_total",
        "majority_class_rate",
        "per_class_heldout_accuracy",
        "n_features",
        "n_train",
    )
    for label_field in ("cls_post_fold", "cls"):
        block_a = three_runs[0][label_field]
        for run_idx in (1, 2):
            block_b = three_runs[run_idx][label_field]
            for k in keys_to_check:
                assert block_a[k] == block_b[k], (
                    f"reproducibility broken on {label_field}.{k}: "
                    f"run0={block_a[k]!r} vs run{run_idx}={block_b[k]!r}"
                )


def test_v0_5_headroom_benchmark_locked(three_runs):
    """Acceptance criterion 2: numbers match the v0.5 tire-kick finding.

    Per TIRE_KICK_v0.5_RESULT_2026-05-06.md §4.4: cls_post_fold = 17/17 =
    1.000; cls = 16/17 = 0.941. If a future fixture / LR-config / sklearn
    upgrade silently drifts these, every downstream LoRA-vs-LR comparison
    is mis-anchored."""
    r = three_runs[0]
    pf = r["cls_post_fold"]
    assert pf["heldout_accuracy"] == 1.0, (
        f"cls_post_fold ceiling drifted from 1.000 to {pf['heldout_accuracy']:.4f}"
    )
    assert pf["n_correct"] == 17 and pf["n_total"] == 17

    cls = r["cls"]
    assert cls["n_correct"] == 16 and cls["n_total"] == 17
    assert abs(cls["heldout_accuracy"] - 16.0 / 17.0) < 1e-12

    # phi_4_singleton is the singleton class that LR misses (per v0.5
    # finding). Locking that specific failure mode so we notice if it
    # changes (e.g., a new fixture entry breaks the singleton structure).
    per_class_4way = cls["per_class_heldout_accuracy"]
    assert per_class_4way.get("phi_4_singleton") == 0.0, (
        "phi_4_singleton miss is the locked v0.5 failure mode; "
        f"got {per_class_4way.get('phi_4_singleton')}"
    )


def test_reproducibility_metadata_block_present(three_runs):
    """Acceptance criterion 3 (E003 spec extension): JSON now carries
    a `reproducibility` block that lets future runs detect environmental
    drift without re-running the fit."""
    for run in three_runs:
        repro = run.get("reproducibility")
        assert isinstance(repro, dict), f"missing reproducibility block: {run.keys()}"
        for k in (
            "python_version",
            "platform",
            "numpy_version",
            "sklearn_version",
            "lr_random_state",
            "fixture_content_hash_sha256",
        ):
            assert k in repro, f"reproducibility missing {k!r}; got {repro.keys()}"
        assert repro["lr_random_state"] == _LR_RANDOM_STATE
        # Hash must be 64 hex chars (SHA-256)
        h = repro["fixture_content_hash_sha256"]
        assert isinstance(h, str) and len(h) == 64
        assert all(c in "0123456789abcdef" for c in h.lower())


def test_fixture_hash_stable_across_calls():
    """The fixture hash is itself deterministic — re-computing yields
    the same value as long as the fixture data is unchanged."""
    h1 = _fixture_content_hash()
    h2 = _fixture_content_hash()
    assert h1 == h2


def test_three_runs_have_same_fixture_hash(three_runs):
    """All 3 runs see the same fixture; hash must match."""
    hashes = [run["reproducibility"]["fixture_content_hash_sha256"] for run in three_runs]
    assert len(set(hashes)) == 1, f"fixture hash drifted across runs: {hashes}"


def test_jsonl_write_round_trip(three_runs, tmp_path):
    """Each fresh-tmp run wrote a JSON file; load + re-encode round-trips
    cleanly. Catches non-JSON-native fields that default=str would obscure."""
    for i, run in enumerate(three_runs):
        path = run.get("written_to")
        assert path and Path(path).exists()
        loaded = json.loads(Path(path).read_text(encoding="utf-8"))
        # Round-trip the content we care about
        for label_field in ("cls_post_fold", "cls"):
            assert loaded[label_field]["heldout_accuracy"] == run[label_field]["heldout_accuracy"]
        assert loaded["reproducibility"]["lr_random_state"] == _LR_RANDOM_STATE


def test_canonical_results_file_exists():
    """The canonical (committed) results JSON must exist post-fire-1 commit."""
    canonical = Path("ergon/pipeline_d/runs/lr_control/lr_control_results.json")
    assert canonical.exists(), "canonical lr_control_results.json missing on disk"
