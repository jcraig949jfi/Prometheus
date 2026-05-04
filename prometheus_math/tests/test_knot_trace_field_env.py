"""Tests for prometheus_math.knot_trace_field_env (knot trace-field class).

Cross-domain validation #3: same substrate (sigma kernel + BIND/EVAL +
class-prediction action table) as BSDRankEnv and ModularFormEnv, but
the ground truth lives in KnotInfo + a hand-curated trace-field table
sourced from Maclachlan-Reid "Arithmetic of Hyperbolic 3-Manifolds"
and Snap (Coulson-Goodman-Hodgson-Neumann).

Math-tdd skill rubric (>= 3 in every category).

Authority -- ground truth comes from canonical references; verify
known-knot data agrees with classical sources.

Property -- well-formedness of trace-field metadata, determinism,
non-zero hyperbolic volume on the hyperbolic subset.

Edge -- empty corpus, missing metadata, action outside the class set.

Composition -- 3-algorithm comparison, pipeline records, end-to-end
pipeline through corpus / env / REINFORCE / test / record.
"""
from __future__ import annotations

import math

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def _knot_available():
    from prometheus_math import _knot_trace_field_corpus
    ok, reason = _knot_trace_field_corpus.is_available()
    if not ok:
        pytest.skip(f"knot trace-field corpus unavailable: {reason}")
    return True


@pytest.fixture(scope="module")
def hyp_corpus(_knot_available):
    """Hyperbolic-only corpus (the env's training distribution)."""
    from prometheus_math import _knot_trace_field_corpus
    return _knot_trace_field_corpus.load_knot_trace_field_corpus(
        include_non_hyperbolic=False, use_cache=False,
    )


@pytest.fixture(scope="module")
def full_corpus(_knot_available):
    """Full corpus including non-hyperbolic torus knots."""
    from prometheus_math import _knot_trace_field_corpus
    return _knot_trace_field_corpus.load_knot_trace_field_corpus(
        include_non_hyperbolic=True, use_cache=False,
    )


@pytest.fixture
def hyp_env(hyp_corpus):
    from prometheus_math.knot_trace_field_env import KnotTraceFieldEnv
    env = KnotTraceFieldEnv(corpus=hyp_corpus, split="all", seed=0)
    yield env
    env.close()


# ---------------------------------------------------------------------------
# Authority -- ground truth alignment with canonical references
# ---------------------------------------------------------------------------


def test_authority_corpus_contains_figure_8(hyp_corpus):
    """Corpus must contain 4_1 (figure-8 knot), the simplest hyperbolic
    knot. Authority: every textbook on hyperbolic 3-manifolds (Thurston,
    Maclachlan-Reid, Benedetti-Petronio).
    """
    names = {e.name for e in hyp_corpus}
    assert "4_1" in names, (
        f"figure-8 (4_1) missing from corpus of size {len(hyp_corpus)}; "
        f"sample names: {sorted(list(names))[:8]}"
    )


def test_authority_figure_8_trace_field_is_complex_quadratic(hyp_corpus):
    """The figure-8 knot has trace field Q(sqrt(-3)) = Q(omega), a
    complex-quadratic number field. Its minimal polynomial generator is
    x^2 + x + 1 (or equivalently x^2 + 3 for the related
    discriminant-(-3) field).

    Authority: Riley (1975) "A quadratic parabolic group", followed by
    Thurston's notes; codified in Maclachlan-Reid Table 4.4. The trace
    field of the figure-8 is the canonical first example in every
    treatment of arithmetic hyperbolic 3-manifolds.
    """
    from prometheus_math._knot_trace_field_corpus import (
        TRACE_FIELD_CLASSES, classify_trace_field,
    )
    rec = next((e for e in hyp_corpus if e.name == "4_1"), None)
    assert rec is not None, "4_1 not in corpus"
    # Class should be complex_quadratic = 2.
    assert TRACE_FIELD_CLASSES[rec.trace_field_class] == "complex_quadratic"
    assert rec.trace_field_class == 2
    # Min poly is degree 2.
    assert rec.trace_field_degree == 2
    # Signature (0, 1) -- one pair of complex embeddings, no real.
    assert rec.trace_field_signature == (0, 1)
    # The classify helper agrees with the stored class.
    assert classify_trace_field(
        rec.trace_field_min_poly, rec.trace_field_signature
    ) == rec.trace_field_class
    # NF discriminant -3.
    assert rec.nf_discriminant == -3


def test_authority_figure_8_volume_is_2_0299(hyp_corpus):
    """The figure-8 knot complement has hyperbolic volume
    2.029883212819... (the smallest cusped hyperbolic 3-manifold volume,
    along with its sister manifold).

    Authority: Cao-Meyerhoff (2001) Inventiones; Adams "The Knot Book"
    chapter 6. The exact value is 2*Im(Li_2(e^(i*pi/3))).
    """
    rec = next((e for e in hyp_corpus if e.name == "4_1"), None)
    assert rec is not None
    expected = 2.0298832128193
    assert abs(rec.hyperbolic_volume - expected) < 1e-3, (
        f"4_1 hyperbolic volume {rec.hyperbolic_volume} differs from "
        f"published {expected}"
    )


def test_authority_5_2_trace_field_complex_cubic(hyp_corpus):
    """The two-bridge knot 5_2 has trace field of degree 3, signature
    (1, 1) -- a complex cubic.

    Authority: Maclachlan-Reid Table 4.4 -- 5_2 is one of the canonical
    "small" hyperbolic two-bridge knots whose trace fields are
    explicitly tabulated. The discriminant is -23.
    """
    rec = next((e for e in hyp_corpus if e.name == "5_2"), None)
    assert rec is not None, "5_2 not in corpus"
    assert rec.trace_field_degree == 3
    assert rec.trace_field_signature == (1, 1)
    from prometheus_math._knot_trace_field_corpus import TRACE_FIELD_CLASSES
    assert TRACE_FIELD_CLASSES[rec.trace_field_class] == "complex_cubic"
    assert rec.nf_discriminant == -23


def test_authority_predicting_correct_class_yields_full_reward(hyp_env):
    """Predicting the true trace-field class must pay out REWARD_HIT.
    Authority: env reward contract.
    """
    from prometheus_math.knot_trace_field_env import REWARD_HIT
    env = hyp_env
    obs, info = env.reset(seed=12345)
    true_class = int(info["true_class"])
    _, r, term, _, info2 = env.step(true_class)
    assert math.isclose(r, REWARD_HIT)
    assert info2["hit"] is True
    assert term is True
    assert info2["trace_field_class"] == true_class
    assert info2["predicted_class"] == true_class


# ---------------------------------------------------------------------------
# Property -- well-formedness, determinism
# ---------------------------------------------------------------------------


def test_property_min_polys_are_irreducible_or_linear(hyp_corpus):
    """For each trace field minimal polynomial f(x) with deg >= 2, the
    polynomial must be irreducible over Q. We verify the lightweight
    necessary condition: f has no rational roots (rational root
    theorem) AND the leading coefficient is +/-1 (monic up to sign,
    which is what we get from a defining polynomial of an algebraic
    integer).

    Property: a defining polynomial for the trace field must be
    irreducible over Q. Linear (degree 1) polys for non-hyperbolic
    placeholder rows are exempt since they encode "Q" as the field.
    """
    for e in hyp_corpus:
        f = list(e.trace_field_min_poly)
        deg = len(f) - 1
        if deg <= 1:
            # Non-hyperbolic placeholder; nothing to check.
            continue
        # Leading coefficient must be +/-1 (monic / antimonic).
        assert abs(f[-1]) == 1, (
            f"{e.name}: leading coefficient of trace-field poly "
            f"must be +/-1; got {f[-1]} in poly {f}"
        )
        # Constant must be nonzero (else 0 is a root -> reducible).
        assert f[0] != 0, (
            f"{e.name}: constant term of trace-field poly is 0 "
            f"(makes 0 a root, contradicting irreducibility): {f}"
        )
        # No rational roots: by RRT, only candidates are p/q where
        # p | f[0] and q | f[-1] (= +/-1). So candidates are the
        # divisors of f[0]. We try +/-1 and +/-f[0] only (the simple
        # checks; full RRT would enumerate all divisors).
        c = f[0]
        candidates = {1, -1, c, -c}
        for r in candidates:
            val = sum(coef * (r ** i) for i, coef in enumerate(f))
            assert val != 0, (
                f"{e.name}: rational root {r} found in trace-field "
                f"poly {f}; not irreducible over Q"
            )


def test_property_well_formed_metadata(hyp_corpus):
    """Every entry has well-formed metadata.

    Property: schema sanity.
    """
    from prometheus_math._knot_trace_field_corpus import (
        N_CLASSES, TRACE_FIELD_CLASSES,
    )
    assert len(TRACE_FIELD_CLASSES) == N_CLASSES
    for e in hyp_corpus:
        assert isinstance(e.name, str) and e.name
        assert isinstance(e.crossing_number, int) and e.crossing_number >= 0
        assert isinstance(e.signature, int)
        assert isinstance(e.determinant, int) and e.determinant >= 1
        assert isinstance(e.three_genus, int) and e.three_genus >= 0
        assert isinstance(e.hyperbolic_volume, float)
        assert isinstance(e.alexander_coeffs, tuple)
        assert isinstance(e.trace_field_min_poly, tuple)
        assert len(e.trace_field_min_poly) >= 2
        assert isinstance(e.trace_field_signature, tuple)
        assert len(e.trace_field_signature) == 2
        # r1 + 2*r2 = degree of poly.
        r1, r2 = e.trace_field_signature
        assert r1 + 2 * r2 == e.trace_field_degree
        assert 0 <= e.trace_field_class < N_CLASSES


def test_property_determinism_with_fixed_seed(hyp_corpus):
    """The reset/sample/step pipeline is deterministic given seed."""
    from prometheus_math.knot_trace_field_env import KnotTraceFieldEnv
    env_a = KnotTraceFieldEnv(corpus=hyp_corpus, split="all", seed=0)
    env_b = KnotTraceFieldEnv(corpus=hyp_corpus, split="all", seed=0)
    obs_a, info_a = env_a.reset(seed=99)
    obs_b, info_b = env_b.reset(seed=99)
    np.testing.assert_array_equal(obs_a, obs_b)
    assert info_a["name"] == info_b["name"]
    assert info_a["true_class"] == info_b["true_class"]
    env_a.close()
    env_b.close()


def test_property_all_hyperbolic_knots_have_nonzero_volume(hyp_corpus):
    """Every hyperbolic knot in the trained corpus must have
    ``hyperbolic_volume > 0``. Mostow rigidity makes the volume an
    invariant of the knot.

    Property: filtering ``include_non_hyperbolic=False`` must actually
    drop the placeholder torus-knot rows.
    """
    zero_vol = [e for e in hyp_corpus if e.hyperbolic_volume <= 0.0]
    assert not zero_vol, (
        f"{len(zero_vol)} entries with non-positive volume in the "
        f"hyperbolic corpus: {[(e.name, e.hyperbolic_volume) for e in zero_vol[:5]]}"
    )


def test_property_obs_shape_consistent(hyp_env):
    """Observation vector has fixed dimension across resets."""
    from prometheus_math.knot_trace_field_env import _obs_dim
    env = hyp_env
    expected = _obs_dim(env.alexander_len())
    for s in (1, 2, 3, 4, 5):
        obs, _info = env.reset(seed=s)
        assert obs.shape == (expected,), (
            f"obs shape mismatch at seed={s}: "
            f"{obs.shape} vs ({expected},)"
        )


# ---------------------------------------------------------------------------
# Edge -- empty corpus, missing metadata, action out of range
# ---------------------------------------------------------------------------


def test_edge_empty_corpus_raises_value_error(_knot_available):
    """Constructing an env with an empty corpus must raise ValueError."""
    from prometheus_math.knot_trace_field_env import KnotTraceFieldEnv
    with pytest.raises(ValueError):
        KnotTraceFieldEnv(corpus=[], split="all")


def test_edge_action_out_of_range(hyp_env):
    """Predicting a class outside [0, N_CLASSES) is rejected."""
    from prometheus_math.knot_trace_field_env import N_CLASSES
    env = hyp_env
    env.reset(seed=1)
    with pytest.raises(ValueError):
        env.step(N_CLASSES)
    env.reset(seed=2)
    with pytest.raises(ValueError):
        env.step(-1)


def test_edge_missing_trace_field_metadata_raises(_knot_available):
    """A knot entry with an out-of-range ``trace_field_class`` must be
    rejected at construction.

    Edge: defensive contract for hand-built corpora that may have
    bad / partial trace-field rows.
    """
    from prometheus_math._knot_trace_field_corpus import (
        KnotTraceFieldEntry, DEFAULT_ALEXANDER_LEN,
    )
    from prometheus_math.knot_trace_field_env import KnotTraceFieldEnv
    bad = KnotTraceFieldEntry(
        name="X_1", crossing_number=4, signature=0, determinant=5,
        three_genus=1, hyperbolic_volume=2.03,
        alexander_coeffs=tuple([0] * DEFAULT_ALEXANDER_LEN),
        trace_field_min_poly=(1, 1, 1),
        trace_field_signature=(0, 1),
        trace_field_class=99,  # out of range
        nf_label=None, nf_discriminant=None, nf_class_number=None,
        source="test",
    )
    with pytest.raises(ValueError):
        KnotTraceFieldEnv(corpus=[bad], split="all")


def test_edge_unknown_split_raises(hyp_corpus):
    """An invalid ``split`` value is rejected at construction."""
    from prometheus_math.knot_trace_field_env import KnotTraceFieldEnv
    with pytest.raises(ValueError):
        KnotTraceFieldEnv(corpus=hyp_corpus, split="bogus")


def test_edge_inconsistent_alexander_length_raises(_knot_available):
    """If two corpus rows have different Alexander vector lengths the
    env must reject the corpus at construction.

    Edge: schema-consistency contract.
    """
    from prometheus_math._knot_trace_field_corpus import KnotTraceFieldEntry
    from prometheus_math.knot_trace_field_env import KnotTraceFieldEnv
    a = KnotTraceFieldEntry(
        name="A", crossing_number=4, signature=0, determinant=5,
        three_genus=1, hyperbolic_volume=2.03,
        alexander_coeffs=(1, -3, 1, 0),
        trace_field_min_poly=(1, 1, 1),
        trace_field_signature=(0, 1),
        trace_field_class=2,
        nf_label=None, nf_discriminant=None, nf_class_number=None,
        source="test",
    )
    b = KnotTraceFieldEntry(
        name="B", crossing_number=5, signature=-2, determinant=7,
        three_genus=1, hyperbolic_volume=2.83,
        alexander_coeffs=(2, -3, 2),  # length 3, mismatched with A's 4
        trace_field_min_poly=(1, 0, -1, 1),
        trace_field_signature=(1, 1),
        trace_field_class=4,
        nf_label=None, nf_discriminant=None, nf_class_number=None,
        source="test",
    )
    with pytest.raises(ValueError):
        KnotTraceFieldEnv(corpus=[a, b], split="all")


# ---------------------------------------------------------------------------
# Composition -- multi-algorithm pilot, comparison dict, growth invariant
# ---------------------------------------------------------------------------


def test_composition_pilot_random_produces_well_formed_report(hyp_env):
    """``train_random`` returns a dict with the expected keys and
    sensible values.
    """
    from prometheus_math.knot_trace_field_env import train_random, N_CLASSES
    out = train_random(hyp_env, n_episodes=80, seed=0)
    for key in ("rewards", "mean_reward", "accuracy", "n_episodes",
                "agent", "pred_counts"):
        assert key in out, f"missing key {key} in output"
    assert out["n_episodes"] == 80
    assert out["agent"] == "random"
    assert 0.0 <= out["accuracy"] <= 1.0
    # Random over N_CLASSES classes: accuracy in roughly [0, 1/N_CLASSES + 0.2].
    assert out["accuracy"] <= 0.4
    # pred_counts should sum to n_episodes.
    assert sum(out["pred_counts"]) == 80


def test_composition_three_algorithm_comparison(hyp_corpus):
    """Running random / REINFORCE / PPO on the same corpus yields a
    comparison dict with all three reports present and shape-matched.
    """
    from prometheus_math.knot_trace_field_env import (
        KnotTraceFieldEnv, train_random, train_reinforce, train_ppo,
    )
    e1 = KnotTraceFieldEnv(corpus=hyp_corpus, split="all", seed=0)
    e2 = KnotTraceFieldEnv(corpus=hyp_corpus, split="all", seed=0)
    e3 = KnotTraceFieldEnv(corpus=hyp_corpus, split="all", seed=0)
    rep_random = train_random(e1, n_episodes=80, seed=0)
    rep_lrn = train_reinforce(e2, n_episodes=80, lr=0.02, seed=0)
    rep_ppo = train_ppo(e3, n_episodes=80, lr=0.005, hidden=16, seed=0)
    e1.close(); e2.close(); e3.close()
    comparison = {
        "random": rep_random,
        "reinforce": rep_lrn,
        "ppo": rep_ppo,
    }
    for arm, rep in comparison.items():
        assert "mean_reward" in rep and "accuracy" in rep
        assert rep["n_episodes"] == 80
    assert comparison["random"]["agent"] == "random"
    assert comparison["reinforce"]["agent"] == "reinforce"
    assert comparison["ppo"]["agent"] == "ppo"


def test_composition_pilot_records_match_expectation(hyp_corpus):
    """A 200-episode REINFORCE run on the small corpus produces:
      - a numpy rewards array of length 200,
      - a finite mean reward in [0, REWARD_HIT],
      - pred_counts summing to 200.
    """
    from prometheus_math.knot_trace_field_env import (
        KnotTraceFieldEnv, train_reinforce, REWARD_HIT,
    )
    env = KnotTraceFieldEnv(corpus=hyp_corpus, split="all", seed=0)
    rep = train_reinforce(env, n_episodes=200, lr=0.02, seed=0)
    env.close()
    rewards = rep["rewards"]
    assert isinstance(rewards, np.ndarray)
    assert rewards.shape == (200,)
    assert 0.0 <= rep["mean_reward"] <= REWARD_HIT
    assert sum(rep["pred_counts"]) == 200


def test_composition_substrate_growth_one_binding_one_eval(hyp_env):
    """Each step produces exactly one binding + one evaluation row in
    the sigma kernel. Mirrors the BSDRankEnv / ModularFormEnv invariant.
    """
    env = hyp_env
    env.reset(seed=5)
    k = env.kernel()

    def _count(table: str) -> int:
        return int(k.conn.execute(
            f"SELECT COUNT(*) FROM {table}").fetchone()[0])

    n_b_before = _count("bindings")
    n_e_before = _count("evaluations")
    env.step(0)
    n_b_after = _count("bindings")
    n_e_after = _count("evaluations")
    assert n_b_after - n_b_before == 1, (
        f"expected 1 new binding, got {n_b_after - n_b_before}"
    )
    assert n_e_after - n_e_before == 1, (
        f"expected 1 new evaluation, got {n_e_after - n_e_before}"
    )


def test_composition_end_to_end_pipeline(hyp_corpus):
    """End-to-end: corpus -> env -> REINFORCE -> held-out test eval ->
    pipeline record. Mirrors the pilot driver's lifecycle.
    """
    from prometheus_math import _knot_trace_field_corpus
    from prometheus_math.knot_trace_field_env import (
        KnotTraceFieldEnv, train_reinforce,
    )
    train, test = _knot_trace_field_corpus.split_train_test(
        hyp_corpus, train_frac=0.7, seed=0
    )
    assert len(train) > 0 and len(test) > 0
    env_train = KnotTraceFieldEnv(corpus=train, split="all", seed=0)
    rep = train_reinforce(env_train, n_episodes=300, lr=0.02, seed=0)
    env_train.close()
    # Now evaluate on test set with deterministic argmax.
    env_test = KnotTraceFieldEnv(corpus=test, split="all", seed=0)
    W, b = rep["policy_W_final"], rep["policy_b_final"]
    rng = np.random.default_rng(1234)
    test_rewards = []
    for _ in range(100):
        obs, _info = env_test.reset(seed=int(rng.integers(0, 2**31 - 1)))
        logits = W @ obs + b
        a = int(np.argmax(logits))
        _, r, _, _, _ = env_test.step(a)
        test_rewards.append(r)
    env_test.close()
    test_mean = float(np.asarray(test_rewards).mean())
    # The pipeline record schema: trained accuracy + held-out test mean.
    record = {
        "train_accuracy": rep["accuracy"],
        "test_mean_reward": test_mean,
        "n_train": len(train),
        "n_test": len(test),
    }
    assert 0.0 <= record["train_accuracy"] <= 1.0
    assert 0.0 <= record["test_mean_reward"] <= 100.0
    assert record["n_train"] > 0 and record["n_test"] > 0
