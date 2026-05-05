"""Tests for prometheus_math.bsd_rich_features and bsd_rich_env.

The substantive question: do richer features break the modal-class
ceiling that linear+MLP both saturated at on raw a_p?

These tests verify the *rich-features pipeline* is correct (the
empirical lift question lives in BSD_RICH_FEATURES_RESULTS.md). Math-
TDD rubric, >=3 tests in every category.

Authority    -- rich corpus matches base corpus on every label;
                three named curves carry the expected published
                rich-feature values; vectorize_rich is fixed-length.

Property     -- determinism with fixed seed; vector dimension is
                consistent across all curves; all numerical features
                are finite.

Edge         -- missing optional metadata (no LMFDB row) -> defaults;
                Sato-Tate / unknown categorical input -> "OTHER" bucket;
                rare rank>=4 entry handled (vectorizer doesn't crash).

Composition  -- pilot harness produces a well-formed report dict;
                3-arm + significance tests well-formed; end-to-end
                corpus -> vectorize -> train -> test -> log.
"""
from __future__ import annotations

import math

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Skip-with-message gates
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def _bsd_available():
    from prometheus_math import _bsd_corpus
    ok, reason = _bsd_corpus.is_available()
    if not ok:
        pytest.skip(f"BSD corpus unavailable: {reason}")
    return True


@pytest.fixture(scope="module")
def small_rich_corpus(_bsd_available):
    """Stratified 100-curve rich corpus for fast tests.

    Uses cache=True to avoid re-querying LMFDB on every test session.
    """
    from prometheus_math import _bsd_rich_features
    return _bsd_rich_features.load_bsd_rich_corpus(
        n_total=100,
        seed=7,
        conductor_max=10000,
        use_cache=False,  # this small corpus does NOT hit the prod cache
    )


@pytest.fixture(scope="module")
def base_corpus_for_rich(_bsd_available):
    """Same parameters as small_rich_corpus, base-only — for comparison."""
    from prometheus_math import _bsd_corpus
    return _bsd_corpus.load_bsd_corpus(
        n_total=100, seed=7, conductor_max=10000,
    )


# ---------------------------------------------------------------------------
# Authority -- rich agrees with base; named curves are correct
# ---------------------------------------------------------------------------


def test_authority_rich_corpus_subsumes_base(small_rich_corpus, base_corpus_for_rich):
    """Every label in the base 100-entry corpus has a matching label in
    the rich 100-entry corpus, with same rank and conductor."""
    rich_by_label = {e.label: e for e in small_rich_corpus}
    base_by_label = {e.label: e for e in base_corpus_for_rich}
    # Stratification is deterministic, so the same seed -> same labels.
    assert set(rich_by_label) == set(base_by_label), (
        "rich and base corpora disagree on labels"
    )
    for lbl, base_e in base_by_label.items():
        rich_e = rich_by_label[lbl]
        assert rich_e.rank == base_e.rank, f"rank mismatch on {lbl}"
        assert rich_e.conductor == base_e.conductor, f"conductor mismatch on {lbl}"
        assert tuple(rich_e.a_p) == tuple(base_e.a_p), f"a_p mismatch on {lbl}"


def test_authority_known_curves_have_correct_rich_features(_bsd_available):
    """For three published Cremona curves, rich-feature values match
    LMFDB/Cremona ground truth.

    Reference values (LMFDB ec_curvedata, snapshot 2026-05-04):
      11.a2  : rank=0, regulator=1.0,        cm=0, bad_primes=(11,)
      37.a1  : rank=1, regulator≈0.0511114,  cm=0, bad_primes=(37,)
      5077.a1: rank=3, regulator≈0.4171436,  cm=0, bad_primes=(5077,)
    """
    from prometheus_math import _bsd_corpus, _bsd_rich_features
    from prometheus_math._bsd_corpus import BSDEntry

    # Pull the three curves directly via Cremona; build rich entries
    # by hand (so we don't depend on stratification including them).
    from prometheus_math.databases import cremona
    targets = ["11a1", "37a1", "5077a1"]  # Cremona labels
    cremona_rows = {}
    for cl in targets:
        rows = cremona.elliptic_curves(label=cl, limit=1, fall_back_to_lmfdb=False)
        if rows:
            cremona_rows[cl] = rows[0]
    if len(cremona_rows) < 3:
        pytest.skip(f"Cremona mirror missing one of {targets}")

    # Construct minimal BSDEntry stubs for each, then run the rich
    # builder.
    lmfdb_labels = [r.get("lmfdb_label") for r in cremona_rows.values()]
    lmfdb_rows = _bsd_rich_features._fetch_lmfdb_rich(lmfdb_labels, timeout=30)
    if not lmfdb_rows:
        pytest.skip("LMFDB mirror unreachable for authority test")

    # 11.a2 (Cremona 11a1, LMFDB 11.a2): rank 0, regulator 1.0
    # NOTE: Cremona 11a1 == LMFDB 11.a2 due to historical relabeling.
    r = cremona_rows["11a1"]
    base = BSDEntry(
        label=str(r["lmfdb_label"]),
        cremona_label="11a1",
        ainvs=tuple(int(x) for x in r["ainvs"]),
        conductor=int(r["conductor"]),
        a_p=(-2, -1, 1, -2, 1, 4, -2, 0, -1, 0, 7, 3, -8, -6, 8,
             -6, 5, 12, -7, -3),  # placeholder; not under test here
        rank=int(r["rank"]),
    )
    rich = _bsd_rich_features._build_rich_entry(
        base, r, lmfdb_rows.get(str(r["lmfdb_label"]), {})
    )
    assert rich.rank == 0
    assert rich.rich.regulator == pytest.approx(1.0, rel=1e-6)
    assert rich.rich.cm == 0
    assert tuple(rich.rich.bad_primes) == (11,)

    # 37.a1: rank 1, regulator ≈ 0.0511114
    r = cremona_rows["37a1"]
    base = BSDEntry(
        label=str(r["lmfdb_label"]),
        cremona_label="37a1",
        ainvs=tuple(int(x) for x in r["ainvs"]),
        conductor=int(r["conductor"]),
        a_p=(0,) * 20,
        rank=int(r["rank"]),
    )
    rich = _bsd_rich_features._build_rich_entry(
        base, r, lmfdb_rows.get(str(r["lmfdb_label"]), {})
    )
    assert rich.rank == 1
    assert rich.rich.regulator == pytest.approx(0.0511114, rel=1e-3)
    assert tuple(rich.rich.bad_primes) == (37,)

    # 5077.a1: rank 3, regulator ≈ 0.4171436
    r = cremona_rows["5077a1"]
    base = BSDEntry(
        label=str(r["lmfdb_label"]),
        cremona_label="5077a1",
        ainvs=tuple(int(x) for x in r["ainvs"]),
        conductor=int(r["conductor"]),
        a_p=(0,) * 20,
        rank=int(r["rank"]),
    )
    rich = _bsd_rich_features._build_rich_entry(
        base, r, lmfdb_rows.get(str(r["lmfdb_label"]), {})
    )
    assert rich.rank == 3
    assert rich.rich.regulator == pytest.approx(0.4171436, rel=1e-3)
    assert tuple(rich.rich.bad_primes) == (5077,)


def test_authority_vectorize_rich_fixed_length(small_rich_corpus):
    """vectorize_rich must produce the same shape for every entry."""
    from prometheus_math.bsd_rich_features import vectorize_rich, feature_dim
    expected = (feature_dim(20),)
    for e in small_rich_corpus:
        v = vectorize_rich(e, n_ap=20)
        assert v.shape == expected, (
            f"label={e.label}: shape {v.shape} != {expected}"
        )


# ---------------------------------------------------------------------------
# Property -- determinism / dimension consistency / finiteness
# ---------------------------------------------------------------------------


def test_property_determinism_same_seed_same_corpus(_bsd_available):
    """Same parameters -> same label list, every time."""
    from prometheus_math import _bsd_rich_features
    a = _bsd_rich_features.load_bsd_rich_corpus(
        n_total=50, seed=99, conductor_max=5000, use_cache=False
    )
    b = _bsd_rich_features.load_bsd_rich_corpus(
        n_total=50, seed=99, conductor_max=5000, use_cache=False
    )
    assert [e.label for e in a] == [e.label for e in b]


def test_property_vector_dimension_consistent(small_rich_corpus):
    """Every vector has dim == feature_dim(20). Must hold over the
    entire corpus."""
    from prometheus_math.bsd_rich_features import vectorize_rich, feature_dim
    n = feature_dim(20)
    for e in small_rich_corpus:
        v = vectorize_rich(e, n_ap=20)
        assert v.shape == (n,)


def test_property_all_features_finite(small_rich_corpus):
    """No NaN/Inf in any vector. Production training cannot tolerate
    these; the vectorizer guarantees finiteness."""
    from prometheus_math.bsd_rich_features import vectorize_rich
    for e in small_rich_corpus:
        v = vectorize_rich(e, n_ap=20)
        assert np.isfinite(v).all(), f"non-finite vector at label {e.label}"


def test_property_layout_partition_covers_full_dim():
    """The block layout must partition the vector dim with no gaps."""
    from prometheus_math.bsd_rich_features import (
        feature_block_layout, feature_dim,
    )
    layout = feature_block_layout(20)
    spans = sorted(layout.values())
    # Spans should be contiguous: [0,a), [a,b), [b,c), ... [_, n)
    assert spans[0][0] == 0
    for prev, nxt in zip(spans, spans[1:]):
        assert prev[1] == nxt[0], f"gap between {prev} and {nxt}"
    assert spans[-1][1] == feature_dim(20)


# ---------------------------------------------------------------------------
# Edge -- missing data / unknown categories / rare ranks
# ---------------------------------------------------------------------------


def test_edge_missing_lmfdb_row_falls_back_to_defaults(_bsd_available):
    """If the LMFDB enrichment is unreachable (empty lmfdb_rows), the
    builder produces a RichBSDEntry with default values for those
    fields and the vectorizer still works."""
    from prometheus_math import _bsd_rich_features
    from prometheus_math._bsd_corpus import BSDEntry
    from prometheus_math.bsd_rich_features import vectorize_rich, feature_dim

    base = BSDEntry(
        label="11.a2",
        cremona_label="11a1",
        ainvs=(0, -1, 1, -10, -20),
        conductor=11,
        a_p=tuple([-2, -1, 1, -2, 1, 4, -2, 0, -1, 0, 7, 3, -8, -6, 8,
                   -6, 5, 12, -7, -3]),
        rank=0,
    )
    # Empty lmfdb_row simulates "mirror unreachable".
    rich = _bsd_rich_features._build_rich_entry(base, {}, {})
    assert rich.rich.regulator == 0.0
    assert rich.rich.bad_primes == ()
    assert rich.rich.torsion_structure == ()
    assert rich.rich.cm == 0
    v = vectorize_rich(rich)
    assert v.shape == (feature_dim(20),)
    assert np.isfinite(v).all()


def test_edge_unknown_torsion_structure_routes_to_other_bucket():
    """Torsion structures we don't enumerate (e.g. (3, 6) or (4, 8))
    must route to the OTHER bucket without raising."""
    from prometheus_math.bsd_rich_features import (
        _torsion_structure_idx, _TS_SHAPES,
    )
    other_idx = _TS_SHAPES.index("other")
    assert _torsion_structure_idx((3, 6)) == other_idx
    assert _torsion_structure_idx((4, 8)) == other_idx
    # Unknown 3-tuple structure also routes to OTHER (we never see this
    # for elliptic curves over Q, but the bucket must be defensive).
    assert _torsion_structure_idx((2, 2, 2)) == other_idx


def test_edge_high_rank_curve_does_not_crash(_bsd_available):
    """A constructed entry with rank >= 4 must vectorize without raising.

    We don't have an N<=20000 rank-4 curve in the Cremona allbsd mirror,
    so we synthesize one from the lowest-conductor rank-4 curve that
    LMFDB ships (234446.a1), but with a stub a_p that's all zeros.
    """
    from prometheus_math._bsd_rich_features import (
        RichBSDEntry, RichFeatures,
    )
    from prometheus_math._bsd_corpus import BSDEntry
    from prometheus_math.bsd_rich_features import vectorize_rich, feature_dim
    base = BSDEntry(
        label="234446.a1",
        cremona_label="234446a1",
        ainvs=(1, -1, 0, -79, 289),
        conductor=234446,
        a_p=tuple([0] * 20),
        rank=4,
    )
    rf = RichFeatures(
        regulator=54.6488, real_period=0.4117, L1=0.0,
        tamagawa_product=1, torsion=1, sha_an=1.0,
        torsion_structure=(), bad_primes=(2, 7, 11, 1523),
        cm=0, num_bad_primes=4, semistable=True, signD=1,
        faltings_height=2.5, abc_quality=1.5, szpiro_ratio=4.5,
        j_invariant_log=8.0, conductor_radical=234446,
    )
    e = RichBSDEntry(base=base, rich=rf)
    v = vectorize_rich(e)
    assert v.shape == (feature_dim(20),)
    assert np.isfinite(v).all()


def test_edge_extreme_tamagawa_routes_to_overflow_bucket():
    """A tamagawa product way above the highest enumerated bucket
    (e.g. 200) must route to the overflow slot, not crash."""
    from prometheus_math.bsd_rich_features import _tamagawa_idx, _TAMAGAWA_BUCKETS
    overflow_idx = len(_TAMAGAWA_BUCKETS)
    assert _tamagawa_idx(200) == overflow_idx
    assert _tamagawa_idx(50) == overflow_idx
    # Common values still hit their exact bucket.
    assert _tamagawa_idx(1) == 0
    assert _tamagawa_idx(8) == 7


# ---------------------------------------------------------------------------
# Composition -- pilot harness / report shape / end-to-end
# ---------------------------------------------------------------------------


def test_composition_short_pilot_returns_well_formed_report(_bsd_available):
    """A tiny 3-arm pilot (50 episodes, 2 seeds) must produce a dict
    with the keys downstream consumers depend on."""
    from prometheus_math import _bsd_rich_features
    from prometheus_math.bsd_rich_env import (
        BSDRichRankEnv,
        train_random_rich,
        train_reinforce_rich,
        evaluate_linear_on_test,
    )
    corpus = _bsd_rich_features.load_bsd_rich_corpus(
        n_total=80, seed=11, conductor_max=5000, use_cache=False,
    )
    train, test = _bsd_rich_features.split_train_test_rich(
        corpus, train_frac=0.7, seed=11
    )
    env = BSDRichRankEnv(corpus=train, split="all", seed=0)
    rep_random = train_random_rich(env, n_episodes=50, seed=0)
    env.close()
    for k in ("rewards", "mean_reward", "accuracy", "n_episodes",
              "agent", "pred_counts"):
        assert k in rep_random, f"missing key {k} in random report"
    env = BSDRichRankEnv(corpus=train, split="all", seed=0)
    rep_lin = train_reinforce_rich(env, n_episodes=50, seed=0)
    env.close()
    for k in ("policy_W_final", "policy_b_final", "mean_reward", "accuracy"):
        assert k in rep_lin
    ev = evaluate_linear_on_test(
        rep_lin["policy_W_final"], rep_lin["policy_b_final"], test,
        seed=42, n_episodes=20,
    )
    for k in ("mean_reward", "accuracy", "pred_counts"):
        assert k in ev


def test_composition_welch_p_value_is_finite_and_bounded():
    """The p-value helper must stay in [0, 1] on synthetic data."""
    from prometheus_math.bsd_rank_mlp import welch_one_sided
    rng = np.random.default_rng(0)
    a = rng.normal(50, 5, size=10)
    b = rng.normal(40, 5, size=10)
    p_a_gt_b = welch_one_sided(a, b)
    p_b_gt_a = welch_one_sided(b, a)
    assert math.isfinite(p_a_gt_b) and math.isfinite(p_b_gt_a)
    assert 0.0 <= p_a_gt_b <= 1.0
    assert 0.0 <= p_b_gt_a <= 1.0
    # If a > b strongly, p(a>b) should be small.
    assert p_a_gt_b < 0.05


def test_composition_end_to_end_corpus_to_train_to_eval(_bsd_available):
    """Smallest end-to-end: build rich corpus -> vectorize -> train
    linear-rich -> argmax eval -> get a hit count.

    Just verifies the wires are connected; the lift question is in
    the results doc.
    """
    from prometheus_math import _bsd_rich_features
    from prometheus_math.bsd_rich_features import vectorize_rich
    from prometheus_math.bsd_rich_env import (
        BSDRichRankEnv,
        train_reinforce_rich,
        evaluate_linear_on_test,
    )
    corpus = _bsd_rich_features.load_bsd_rich_corpus(
        n_total=60, seed=21, conductor_max=5000, use_cache=False,
    )
    # Vectorization works on every entry.
    for e in corpus:
        v = vectorize_rich(e, n_ap=20)
        assert v.shape[0] > 0

    train, test = _bsd_rich_features.split_train_test_rich(
        corpus, train_frac=0.7, seed=21
    )
    env = BSDRichRankEnv(corpus=train, split="all", seed=42)
    out = train_reinforce_rich(env, n_episodes=200, seed=42)
    env.close()
    ev = evaluate_linear_on_test(
        out["policy_W_final"], out["policy_b_final"], test,
        seed=4242, n_episodes=20,
    )
    # Reward in [0, 100] per episode; mean must be in that range too.
    assert 0.0 <= ev["mean_reward"] <= 100.0
    assert 0.0 <= ev["accuracy"] <= 1.0
    # Trained linear policy should not collapse below random (5 actions
    # uniform = 20% acc), but we don't enforce this here -- the empirical
    # claim lives in the results doc, not in test-suite expectations.
