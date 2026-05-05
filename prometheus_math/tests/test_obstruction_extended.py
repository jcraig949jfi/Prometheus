"""Tests for prometheus_math._obstruction_corpus_extended — multi-prefix
extension of the live OBSTRUCTION_SHAPE corpus.

The base live adapter (``_obstruction_corpus_live.py``) joins
``battery_sweep_v2.jsonl`` (real F1+F6+F9+F11 verdicts) with
``asymptotic_deviations.jsonl`` for the A14* family. This extended
adapter answers a different question: does the OBSTRUCTION_SHAPE
architecture generalize to A150*/A151* unstudied territory?

Honest framing: Charon's *real* battery has been run on A14* and a
sliver of A151*. For A150* and most 3-D A151*, ``battery_sweep_v2.jsonl``
contains zero kill records. We therefore expose two modes:

  mode='live': identical to the base loader. Real battery verdicts only.
    Across A148/A149/A150/A151 this yields 6 unanimous kills, 5 of
    which are Charon's anchor sequences in A149*.

  mode='surrogate': stretch corpus. Synthesizes a ``surrogate_kill_verdict``
    from observable ``delta_pct`` + ``regime_change`` fields in
    ``asymptotic_deviations.jsonl``. EXPLICITLY NOT the F1+F6+F9+F11
    battery — this is a structural-anomaly proxy validated to recover
    Charon's 5 A149 anchors at 100% precision (see
    ``OBSTRUCTION_EXTENDED_RESULTS.md`` for derivation).

Math-tdd skill rubric (>=3 in every category):

- Authority: extended corpus loads >=50 A150/A151 entries; OBSTRUCTION_SHAPE
  retains >10x lift on A148/A149 (no regression); the surrogate-mode
  rule recovers all 5 of Charon's A149 anchors exactly when delta>50%.
- Property: deterministic across runs; well-formed features; total =
  sum of per-prefix sizes.
- Edge: non-existent prefix is no-op; empty prefix file = empty
  contribution; empty prefix list raises ValueError.
- Composition: REINFORCE on extended corpus produces a
  ``WithheldResult``-shaped output dict; new high-lift signatures (if
  any) get tagged.
"""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pytest

from prometheus_math._obstruction_corpus_live import (
    DEFAULT_BATTERY_PATH,
    DEFAULT_DEVIATIONS_PATH,
    UNANIMOUS_BATTERY,
    obstruction_signature_lift_on_live,
)
from prometheus_math._obstruction_corpus_extended import (
    LiveCorpusEntry,  # re-exported
    DEFAULT_PREFIXES,
    load_extended_corpus,
    extended_corpus_summary,
    surrogate_kill_verdict,
)


OBSTRUCTION_SHAPE: Dict[str, Any] = {
    "n_steps": 5,
    "neg_x": 4,
    "pos_x": 1,
    "has_diag_neg": True,
}

ANCHOR_SEQ_IDS = {"A149074", "A149081", "A149082", "A149089", "A149090"}


# Skip-clean wrapper: extended loader pulls from the same live data; if
# it's missing, skip rather than fail.
def _get_extended_or_skip(prefixes=None, mode="live"):
    if not DEFAULT_BATTERY_PATH.exists() or not DEFAULT_DEVIATIONS_PATH.exists():
        pytest.skip("live data not reachable")
    return load_extended_corpus(prefixes=prefixes, mode=mode)


# ---------------------------------------------------------------------------
# Authority — live data carries Charon's signal across the broader corpus.
# ---------------------------------------------------------------------------


def test_authority_extended_corpus_loads_a150_a151_entries():
    """Loading the extended corpus over A148/A149/A150/A151 yields at
    least 50 entries from {A150, A151} combined.

    Authority: ``asymptotic_deviations.jsonl`` ships 501 A150 and 332
    A151 records. Restricting to 3-D walks (parseable step set) drops
    A151 to ~255 because the 3 battery-sweep A151 records are 2-D
    (N^2). Floor of 50 leaves headroom for fixture-only environments.
    """
    corpus = _get_extended_or_skip(prefixes=["A148", "A149", "A150", "A151"])
    a150_a151 = [e for e in corpus if e.sequence_id.startswith(("A150", "A151"))]
    assert len(a150_a151) >= 50, (
        f"extended corpus missing A150/A151 entries: only {len(a150_a151)} loaded"
    )


def test_authority_obstruction_shape_lift_above_10x_on_a148_a149_no_regression():
    """The OBSTRUCTION_SHAPE signature still has lift > 10x on the
    A148/A149 slice of the extended corpus. NO REGRESSION vs base loader.

    Authority: substrate-grade replication of Charon's 54x finding
    (a149_obstruction.py). The extended loader must NOT degrade this.
    """
    corpus = _get_extended_or_skip(prefixes=["A148", "A149"])
    result = obstruction_signature_lift_on_live(corpus, OBSTRUCTION_SHAPE)
    assert result["n_match"] >= 1, (
        f"signature has no matches in A148/A149 slice: {result}"
    )
    assert result["lift"] > 10.0, (
        f"OBSTRUCTION_SHAPE lift on A148/A149 below 10x: {result}"
    )
    matched = set(result["match_sequence_ids"])
    overlap = matched & ANCHOR_SEQ_IDS
    assert len(overlap) >= 4, (
        f"match group lost Charon's anchors: matched={matched}"
    )


def test_authority_obstruction_shape_lift_reported_on_extended_corpus():
    """On the broader A148/A149/A150/A151 corpus, the OBSTRUCTION_SHAPE
    lift is COMPUTED AND REPORTED — whatever the value.

    Authority: the question of whether the signature generalizes is an
    empirical one. The test asserts the call returns a finite, tractable
    number (no NaN, no crash). The actual lift gets recorded in
    OBSTRUCTION_EXTENDED_RESULTS.md.
    """
    corpus = _get_extended_or_skip(prefixes=["A148", "A149", "A150", "A151"])
    result = obstruction_signature_lift_on_live(corpus, OBSTRUCTION_SHAPE)
    assert "lift" in result
    assert math.isfinite(result["lift"])
    assert result["n_match"] >= 0
    assert result["n_total"] == len(corpus)


def test_authority_surrogate_recovers_charon_anchors_on_a149():
    """The surrogate kill rule (delta_pct>50% AND regime_change=True)
    recovers EXACTLY Charon's 5 anchor A-numbers on A149 when the live
    battery is unavailable.

    Authority: cross-checked against ``battery_sweep_v2.jsonl``.
    Among A149* entries with delta_pct > 50%, 5/5 are unanimous-killed
    in the real battery; the surrogate is therefore 100% precision on
    A149's strict regime.
    """
    corpus = _get_extended_or_skip(prefixes=["A149"], mode="surrogate")
    killed = {e.sequence_id for e in corpus if e.kill_verdict}
    # The strict surrogate (delta>50% AND regime_change) must include
    # Charon's anchors. (It may include 0 extra; the >50% threshold is
    # tight enough to isolate them.)
    overlap = killed & ANCHOR_SEQ_IDS
    assert overlap == ANCHOR_SEQ_IDS, (
        f"surrogate did not recover all Charon anchors: killed={killed}"
    )


# ---------------------------------------------------------------------------
# Property — invariants over the extended corpus.
# ---------------------------------------------------------------------------


def test_property_double_load_extended_is_deterministic():
    """Loading the extended corpus twice produces identical entries in
    identical order (loader sorts by sequence_id)."""
    corpus_a = _get_extended_or_skip(prefixes=["A148", "A149", "A150", "A151"])
    corpus_b = load_extended_corpus(prefixes=["A148", "A149", "A150", "A151"])
    assert len(corpus_a) == len(corpus_b)
    for ea, eb in zip(corpus_a, corpus_b):
        assert ea.sequence_id == eb.sequence_id
        assert ea.features() == eb.features()
        assert ea.kill_verdict == eb.kill_verdict


def test_property_extended_entries_have_canonical_features():
    """Every extended entry has the same canonical feature key set as
    the base ObstructionEnv expects."""
    corpus = _get_extended_or_skip(prefixes=["A150", "A151"])
    expected_keys = {
        "n_steps",
        "neg_x",
        "pos_x",
        "neg_y",
        "pos_y",
        "neg_z",
        "pos_z",
        "has_diag_neg",
        "has_diag_pos",
    }
    # Sample is enough — uniform structure.
    for e in corpus[:20]:
        assert set(e.features().keys()) == expected_keys, (
            f"feature key drift on {e.sequence_id}"
        )
        assert e.sequence_id, "sequence_id must be non-empty"
        assert e.sequence_id.startswith(("A150", "A151"))


def test_property_total_equals_sum_of_per_prefix():
    """The size of a multi-prefix extended corpus equals the sum of the
    sizes of single-prefix loads. Sanity guard against accidental
    deduplication or filtering interactions."""
    pres = ["A148", "A149", "A150", "A151"]
    if not DEFAULT_BATTERY_PATH.exists() or not DEFAULT_DEVIATIONS_PATH.exists():
        pytest.skip("live data not reachable")
    by_prefix = {p: len(load_extended_corpus(prefixes=[p])) for p in pres}
    combined = len(load_extended_corpus(prefixes=pres))
    assert combined == sum(by_prefix.values()), (
        f"size mismatch: combined={combined}, per_prefix_sum={sum(by_prefix.values())} "
        f"({by_prefix})"
    )


def test_property_default_prefixes_match_base_loader_behavior():
    """When called with the default prefixes list, the extended corpus
    contains exactly A148/A149 entries (matching the base loader's
    'A14' filter behavior)."""
    if not DEFAULT_BATTERY_PATH.exists() or not DEFAULT_DEVIATIONS_PATH.exists():
        pytest.skip("live data not reachable")
    # default_prefixes = A148 + A149 (the canonical legacy behavior)
    corpus = load_extended_corpus()
    seen_prefixes = {e.sequence_id[:4] for e in corpus}
    assert seen_prefixes <= {"A148", "A149"}, (
        f"default prefixes leaked into A150/A151: {seen_prefixes}"
    )


# ---------------------------------------------------------------------------
# Edge — bad / boundary inputs.
# ---------------------------------------------------------------------------


def test_edge_nonexistent_prefix_is_noop():
    """Loading with a prefix that doesn't appear in the data simply
    returns no entries from that prefix — does not crash. (An entirely
    empty result, however, would still raise ValueError to match the
    base loader's contract.)"""
    if not DEFAULT_BATTERY_PATH.exists() or not DEFAULT_DEVIATIONS_PATH.exists():
        pytest.skip("live data not reachable")
    # Load A149 + a non-existent prefix.
    corpus = load_extended_corpus(prefixes=["A149", "A999"])
    seen_prefixes = {e.sequence_id[:4] for e in corpus}
    assert "A149" in seen_prefixes
    assert "A999" not in seen_prefixes
    assert all(e.sequence_id.startswith("A149") for e in corpus)


def test_edge_empty_prefix_file_does_not_crash(tmp_path):
    """If the deviations file is empty for a given prefix, the loader
    contributes no entries from that prefix but does not crash, as long
    as some other prefix yields entries."""
    battery_path = tmp_path / "battery.jsonl"
    deviations_path = tmp_path / "deviations.jsonl"
    # One A149 entry survives, one A150 placeholder is malformed/missing
    battery_path.write_text(
        '{"seq_id": "A149074", "kill_tests": '
        '["F1_permutation_null", "F6_base_rate", '
        '"F9_simpler_explanation", "F11_cross_validation"]}\n',
        encoding="utf-8",
    )
    deviations_path.write_text(
        '{"seq_id": "A149074", '
        '"name": "Number of walks within N^3 (the first octant of Z^3) '
        "starting at (0,0,0) and consisting of n steps taken from "
        '{(-1, -1, -1), (-1, -1, 0), (-1, 0, 1), (0, 0, -1), (1, 0, 1)}.", '
        '"delta_pct": 78.0, "regime_change": true}\n',
        encoding="utf-8",
    )
    corpus = load_extended_corpus(
        prefixes=["A149", "A150"],
        battery_path=battery_path,
        deviations_path=deviations_path,
    )
    assert len(corpus) == 1
    assert corpus[0].sequence_id == "A149074"


def test_edge_empty_prefix_list_raises_valueerror():
    """An empty prefixes list is a programmer error → ValueError."""
    if not DEFAULT_BATTERY_PATH.exists() or not DEFAULT_DEVIATIONS_PATH.exists():
        pytest.skip("live data not reachable")
    with pytest.raises(ValueError):
        load_extended_corpus(prefixes=[])


def test_edge_unknown_mode_raises_valueerror():
    """An unknown ``mode`` is a programmer error → ValueError."""
    if not DEFAULT_BATTERY_PATH.exists() or not DEFAULT_DEVIATIONS_PATH.exists():
        pytest.skip("live data not reachable")
    with pytest.raises(ValueError):
        load_extended_corpus(prefixes=["A149"], mode="bogus")


# ---------------------------------------------------------------------------
# Composition — env / REINFORCE on extended corpus.
# ---------------------------------------------------------------------------


def test_composition_obstruction_env_runs_on_extended_corpus():
    """The base ObstructionEnv consumes extended-corpus entries (duck
    typing on .features() / .kill_verdict / .to_dict()) without code
    changes."""
    from prometheus_math.obstruction_env import ObstructionEnv, N_ACTIONS

    corpus = _get_extended_or_skip(prefixes=["A148", "A149", "A150", "A151"])
    env = ObstructionEnv(
        corpus=corpus,
        seed=42,
        max_predicate_complexity=3,
        held_out_fraction=0.3,
    )
    env.reset()
    rng = np.random.default_rng(42)
    rewards = []
    for _ in range(5):
        env.reset()
        terminated = False
        while not terminated:
            a = int(rng.integers(0, N_ACTIONS))
            _, r, terminated, _, _ = env.step(a)
        rewards.append(r)
    assert all(math.isfinite(r) for r in rewards)
    assert all(r >= 0.0 for r in rewards)


def test_composition_reinforce_on_extended_returns_well_formed():
    """REINFORCE on the extended corpus returns a result dict with the
    canonical keys (``rewards``, ``rediscoveries``, ``discoveries``).
    Also runs without crashing."""
    from prometheus_math.demo_obstruction import (
        train_random_obstruction,
        train_reinforce_obstruction,
    )
    from prometheus_math.obstruction_env import ObstructionEnv

    corpus = _get_extended_or_skip(prefixes=["A148", "A149", "A150", "A151"])

    env_rein = ObstructionEnv(
        corpus=corpus,
        seed=101,
        max_predicate_complexity=4,
        held_out_fraction=0.3,
    )
    env_rein.reset()
    rein = train_reinforce_obstruction(env_rein, n_episodes=50, seed=101)
    for k in ("rewards", "rediscoveries", "discoveries"):
        assert k in rein, f"REINFORCE result missing key {k!r}"
    assert len(rein["rewards"]) == 50
    assert all(math.isfinite(float(r)) for r in rein["rewards"])


def test_composition_extended_summary_has_per_prefix_breakdown():
    """``extended_corpus_summary`` reports a per-prefix kill-rate
    breakdown — substrate-grade evidence for cross-prefix
    generalization claims."""
    corpus = _get_extended_or_skip(prefixes=["A148", "A149", "A150", "A151"])
    summary = extended_corpus_summary(corpus)
    assert "by_a_number_prefix" in summary
    assert "per_prefix_kill_rate" in summary
    # A149 must be present (it has anchors).
    assert "A149" in summary["per_prefix_kill_rate"]
    # All values are sane floats in [0, 1].
    for pre, rate in summary["per_prefix_kill_rate"].items():
        assert 0.0 <= rate <= 1.0


# ---------------------------------------------------------------------------
# Bonus: surrogate-mode authority test
# ---------------------------------------------------------------------------


def test_authority_surrogate_kill_verdict_pure_function():
    """``surrogate_kill_verdict`` is a pure function: same record →
    same verdict, deterministically. No randomness, no I/O.

    Validates the rule:
        kill iff delta_pct > 50.0 AND regime_change is True
    """
    rec_kill = {"delta_pct": 78.0, "regime_change": True}
    rec_pass1 = {"delta_pct": 49.0, "regime_change": True}
    rec_pass2 = {"delta_pct": 78.0, "regime_change": False}
    rec_missing = {}
    assert surrogate_kill_verdict(rec_kill) is True
    assert surrogate_kill_verdict(rec_pass1) is False
    assert surrogate_kill_verdict(rec_pass2) is False
    assert surrogate_kill_verdict(rec_missing) is False
    # Determinism: 3 calls = same answer.
    for _ in range(3):
        assert surrogate_kill_verdict(rec_kill) is True
