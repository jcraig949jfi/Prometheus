"""Tests for prometheus_math.bsd_rank_mlp -- non-linear MLP policy.

The team review's #6 refinement asked: "linear policy with one-hot
features may be saturating; an MLP with 2-4 hidden layers might
extract more from the same features." This suite verifies the MLP
backend's correctness, not (per se) its lift over linear -- the lift
question lives in BSD_MLP_RESULTS.md.

Math-tdd skill rubric (>=3 in every category).

Authority    -- forward pass yields a valid distribution; gradient
                matches finite-difference numerical gradient on a small
                example; trained MLP beats random baseline on held-out.

Property     -- determinism with fixed seed; reproducible accuracy;
                output dimension matches n_actions.

Edge         -- empty batch handled (zero-length tensor); all-zero
                features produce ~uniform output (untrained init);
                a very-rare rank class does not crash.

Composition  -- training loop returns a well-formed log dict; 6-cell
                hyperparameter sweep returns a well-formed dict;
                end-to-end pipeline env -> MLP -> train -> test -> log.
"""
from __future__ import annotations

import math

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Skip-with-message gates
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def _torch_available():
    try:
        import torch  # noqa: F401
    except ImportError:
        pytest.skip("PyTorch not installed; skipping MLP suite")
    return True


@pytest.fixture(scope="module")
def _bsd_available(_torch_available):
    from prometheus_math import _bsd_corpus
    ok, reason = _bsd_corpus.is_available()
    if not ok:
        pytest.skip(f"BSD corpus unavailable: {reason}")
    return True


@pytest.fixture(scope="module")
def small_corpus(_bsd_available):
    """Stratified 200-curve corpus for fast tests."""
    from prometheus_math import _bsd_corpus
    return _bsd_corpus.load_bsd_corpus(
        n_total=200,
        seed=42,
        conductor_max=20000,
    )


@pytest.fixture(scope="module")
def small_split(small_corpus):
    from prometheus_math import _bsd_corpus
    train, test = _bsd_corpus.split_train_test(
        small_corpus, train_frac=0.7, seed=42
    )
    return {"train": train, "test": test}


# ---------------------------------------------------------------------------
# Authority -- forward pass / gradient / beats random
# ---------------------------------------------------------------------------


def test_authority_forward_produces_valid_distribution(_torch_available):
    """``softmax(forward(x))`` must be a valid probability vector
    (non-negative, sums to 1) for any input.

    Authority: standard softmax property; failure means the layer
    stack is broken.
    """
    import torch
    from prometheus_math.bsd_rank_mlp import BSDPolicyMLP
    policy = BSDPolicyMLP(obs_dim=26, n_actions=5, seed=0)
    rng = np.random.default_rng(0)
    for _ in range(8):
        x = rng.normal(size=26).astype(np.float32)
        probs = policy.action_dist(torch.as_tensor(x))
        probs_np = probs.detach().cpu().numpy()
        assert np.all(probs_np >= 0.0), f"negative prob: {probs_np}"
        assert math.isclose(
            float(probs_np.sum()), 1.0, abs_tol=1e-5
        ), f"sum != 1: {probs_np.sum()}"


def test_authority_analytic_gradient_matches_numerical(_torch_available):
    """REINFORCE-style gradient of ``log pi(a|s)`` w.r.t. the input
    weights must match finite-difference numerical gradient on a small
    example.

    Authority: autograd correctness is the foundation; if torch's
    backward gives the wrong gradient on this simple log-prob loss,
    the trainer is unreliable.
    """
    import torch
    from prometheus_math.bsd_rank_mlp import BSDPolicyMLP
    torch.manual_seed(7)
    policy = BSDPolicyMLP(obs_dim=4, n_actions=3, hidden=(8,), seed=7)

    x = torch.tensor([0.5, -0.3, 0.1, 0.2], dtype=torch.float32)
    a = 1

    def loss_fn(pol):
        logits = pol(x)
        log_probs = torch.log_softmax(logits, dim=-1)
        return -log_probs[a]  # we MINIMIZE this -> -log pi

    # Analytic gradient via autograd.
    loss = loss_fn(policy)
    loss.backward()
    # First-layer weight gradient.
    first_linear = next(m for m in policy.net if isinstance(m, torch.nn.Linear))
    grad_analytic = first_linear.weight.grad.detach().cpu().numpy().copy()

    # Numerical gradient: central difference on two random entries.
    eps = 1e-3
    rng = np.random.default_rng(42)
    n_check = 5
    for _ in range(n_check):
        i = int(rng.integers(0, grad_analytic.shape[0]))
        j = int(rng.integers(0, grad_analytic.shape[1]))
        with torch.no_grad():
            orig = first_linear.weight[i, j].item()
            first_linear.weight[i, j] = orig + eps
            l_plus = float(loss_fn(policy).item())
            first_linear.weight[i, j] = orig - eps
            l_minus = float(loss_fn(policy).item())
            first_linear.weight[i, j] = orig
        num_grad = (l_plus - l_minus) / (2.0 * eps)
        analytic = float(grad_analytic[i, j])
        # Tolerate a generous absolute tolerance: with hidden=8 and
        # eps=1e-3, second-order errors O(eps^2 * |H|) can reach ~1e-3.
        assert abs(num_grad - analytic) < 5e-3, (
            f"grad mismatch at ({i},{j}): analytic={analytic:.6f} "
            f"vs numerical={num_grad:.6f}"
        )


def test_authority_trained_mlp_beats_random_on_holdout(small_split):
    """A trained MLP, evaluated argmax on the held-out test split,
    must beat the uniform-random baseline by a clear margin.

    Authority: the whole point of the policy is to learn ANYTHING from
    the features. The bar is generous -- random ~20%, modal-class ~50%,
    we just require the trained MLP to break random's ceiling. (The
    deeper "does it beat linear?" lives in the results doc, not here.)
    """
    from prometheus_math.bsd_rank_env import (
        BSDRankEnv,
        train_random_bsd,
    )
    from prometheus_math.bsd_rank_mlp import (
        evaluate_mlp_on_corpus,
        train_mlp_bsd,
    )

    train = small_split["train"]
    test = small_split["test"]

    # Train MLP for a small but credible budget.
    env = BSDRankEnv(corpus=train, split="all", seed=17)
    out = train_mlp_bsd(
        env, n_episodes=600, lr=5e-4, entropy_coef=0.01, seed=17,
    )
    env.close()

    # Eval MLP on test split.
    ev = evaluate_mlp_on_corpus(
        out["policy"], BSDRankEnv, test, seed=12345,
    )
    mlp_acc = ev["accuracy"]

    # Eval random on test split (same number of episodes).
    e = BSDRankEnv(corpus=test, split="all", seed=4321)
    rnd = train_random_bsd(e, n_episodes=len(test), seed=4321)
    e.close()
    rnd_acc = rnd["accuracy"]

    assert mlp_acc > rnd_acc + 0.10, (
        f"MLP did not clearly beat random: mlp_acc={mlp_acc:.3f} "
        f"vs random_acc={rnd_acc:.3f}"
    )


# ---------------------------------------------------------------------------
# Property -- determinism, reproducibility, output dim
# ---------------------------------------------------------------------------


def test_property_determinism_with_fixed_seed(_torch_available):
    """Two MLPs constructed with the same seed produce identical
    forward outputs on the same input.

    Property: seed -> initial weights, deterministically.
    """
    import torch
    from prometheus_math.bsd_rank_mlp import BSDPolicyMLP
    pol_a = BSDPolicyMLP(obs_dim=26, n_actions=5, seed=99)
    pol_b = BSDPolicyMLP(obs_dim=26, n_actions=5, seed=99)
    x = torch.zeros(26, dtype=torch.float32)
    out_a = pol_a(x).detach().cpu().numpy()
    out_b = pol_b(x).detach().cpu().numpy()
    assert np.allclose(out_a, out_b), (
        f"same-seed MLPs disagree: {out_a} vs {out_b}"
    )


def test_property_same_features_same_labels_reproducible_accuracy(small_split):
    """Same env + same MLP seed + same training schedule -> same
    final accuracy. Reproducibility is non-negotiable for a research
    instrument.

    Property: end-to-end determinism of the learning loop.
    """
    from prometheus_math.bsd_rank_env import BSDRankEnv
    from prometheus_math.bsd_rank_mlp import (
        evaluate_mlp_on_corpus,
        train_mlp_bsd,
    )

    train = small_split["train"]
    test = small_split["test"]

    def run_once():
        env = BSDRankEnv(corpus=train, split="all", seed=11)
        out = train_mlp_bsd(
            env, n_episodes=200, lr=5e-4, entropy_coef=0.01, seed=11,
        )
        env.close()
        ev = evaluate_mlp_on_corpus(
            out["policy"], BSDRankEnv, test, seed=11,
        )
        return out["mean_reward"], ev["mean_reward"]

    a_train, a_test = run_once()
    b_train, b_test = run_once()
    assert math.isclose(a_train, b_train, abs_tol=1e-6), (
        f"non-deterministic train mean: {a_train} vs {b_train}"
    )
    assert math.isclose(a_test, b_test, abs_tol=1e-6), (
        f"non-deterministic test mean: {a_test} vs {b_test}"
    )


def test_property_output_dim_matches_n_actions(_torch_available):
    """For any (obs_dim, n_actions, hidden), forward output last axis
    has length exactly ``n_actions``.

    Property: head dimension contract.
    """
    import torch
    from prometheus_math.bsd_rank_mlp import BSDPolicyMLP
    for n_actions in (2, 5, 7):
        for hidden in [(8,), (16, 8), (32, 16, 8)]:
            policy = BSDPolicyMLP(
                obs_dim=10, n_actions=n_actions, hidden=hidden, seed=0,
            )
            out = policy(torch.zeros(10))
            assert out.shape[-1] == n_actions, (
                f"head dim mismatch for n_actions={n_actions}, "
                f"hidden={hidden}: got {out.shape[-1]}"
            )
            # Batched too.
            out_b = policy(torch.zeros(3, 10))
            assert out_b.shape == (3, n_actions), (
                f"batched head dim mismatch: got {out_b.shape}"
            )


# ---------------------------------------------------------------------------
# Edge -- empty batch / all-zero features / very-rare rank
# ---------------------------------------------------------------------------


def test_edge_empty_batch_handled(_torch_available):
    """A zero-length batch -- shape ``(0, obs_dim)`` -- must be
    accepted and produce a zero-length output, not crash.

    Edge: degenerate-dimension contract.
    """
    import torch
    from prometheus_math.bsd_rank_mlp import BSDPolicyMLP
    policy = BSDPolicyMLP(obs_dim=26, n_actions=5, seed=0)
    x = torch.zeros((0, 26), dtype=torch.float32)
    out = policy(x)
    assert out.shape == (0, 5), f"empty batch broke head: {out.shape}"


def test_edge_all_zero_features_produce_normalized_distribution(_torch_available):
    """All-zero features go through the MLP; the resulting softmax is
    still a valid distribution (this is the most basic numerical-
    stability check). We do NOT require it to be uniform: an untrained
    MLP with random biases will tilt slightly, and that's fine.

    Edge: degenerate-input contract.
    """
    import torch
    from prometheus_math.bsd_rank_mlp import BSDPolicyMLP
    policy = BSDPolicyMLP(obs_dim=26, n_actions=5, seed=0)
    x = torch.zeros(26, dtype=torch.float32)
    probs = policy.action_dist(x).detach().cpu().numpy()
    assert math.isclose(float(probs.sum()), 1.0, abs_tol=1e-5)
    assert np.all(probs >= 0.0)
    # Sanity: MLP output is finite even on a zero vector.
    assert np.all(np.isfinite(probs))


def test_edge_very_rare_rank_class_does_not_crash(_bsd_available):
    """The corpus has rank-2+ but very few rank-3 / rank-4 examples.
    Train the MLP on a corpus that includes the rare rank stratum and
    verify it terminates cleanly with a well-formed log dict.

    Edge: long-tail rank class -- the gradient signal for rank-4 is
    sparse but must not crash.
    """
    from prometheus_math import _bsd_corpus
    from prometheus_math.bsd_rank_env import BSDRankEnv
    from prometheus_math.bsd_rank_mlp import train_mlp_bsd

    # Bias the corpus towards rank-2+ to actually see the tail.
    corpus = _bsd_corpus.load_bsd_corpus(
        n_total=120,
        seed=7,
        conductor_max=50000,
        rank0_share=0.3,
        rank1_share=0.3,
        rank2plus_share=0.4,
    )
    env = BSDRankEnv(corpus=corpus, split="all", seed=7)
    out = train_mlp_bsd(env, n_episodes=80, lr=1e-3, seed=7)
    env.close()
    assert out["n_episodes"] == 80
    assert math.isfinite(out["mean_reward"])
    # ``pred_counts`` covers all 5 action slots even if rare classes
    # never get used.
    assert len(out["pred_counts"]) == 5


# ---------------------------------------------------------------------------
# Composition -- log dicts, sweep, end-to-end pipeline
# ---------------------------------------------------------------------------


def test_composition_training_loop_produces_well_formed_log(small_split):
    """``train_mlp_bsd`` returns a dict with all the keys a downstream
    consumer expects. Names + types verified.

    Composition: trainer -> consumer contract.
    """
    from prometheus_math.bsd_rank_env import BSDRankEnv
    from prometheus_math.bsd_rank_mlp import train_mlp_bsd
    env = BSDRankEnv(corpus=small_split["train"], split="all", seed=3)
    out = train_mlp_bsd(env, n_episodes=50, lr=5e-4, seed=3)
    env.close()

    required = {
        "rewards", "mean_reward", "accuracy", "n_episodes", "agent",
        "policy", "pred_counts", "lr", "entropy_coef", "hidden",
    }
    missing = required - set(out)
    assert not missing, f"missing keys in train log: {missing}"
    assert out["agent"] == "mlp_reinforce"
    assert out["n_episodes"] == 50
    assert isinstance(out["pred_counts"], list)
    assert len(out["pred_counts"]) == 5
    assert math.isfinite(out["mean_reward"])
    assert 0.0 <= out["accuracy"] <= 1.0


def test_composition_six_cell_hyperparameter_sweep_returns_well_formed_dict(small_split):
    """The ``hyperparameter_sweep`` must return a dict with one cell
    per (lr, entropy_coef) combination, each with mean+std fields and
    an aggregate ``best_cell`` summary.

    Composition: 6-cell grid -> result schema.
    """
    from prometheus_math.bsd_rank_env import BSDRankEnv
    from prometheus_math.bsd_rank_mlp import hyperparameter_sweep

    out = hyperparameter_sweep(
        train_corpus=small_split["train"],
        test_corpus=small_split["test"],
        env_cls=BSDRankEnv,
        n_episodes=40,        # tiny for unit test
        n_seeds=2,            # tiny for unit test (2 < 5 production)
        learning_rates=(1e-3, 5e-4, 1e-4),
        entropy_coefs=(0.01, 0.001),
        base_seed=11,
    )
    assert "cells" in out and len(out["cells"]) == 6, (
        f"expected 6 cells, got {len(out.get('cells', []))}"
    )
    for cell in out["cells"]:
        for k in ("lr", "entropy_coef", "train_means", "test_means",
                  "train_mean_grand", "train_std_grand",
                  "test_mean_grand", "test_std_grand"):
            assert k in cell, f"cell missing {k}: {cell}"
        assert len(cell["train_means"]) == 2
        assert len(cell["test_means"]) == 2
        assert math.isfinite(cell["test_mean_grand"])
    assert "best_cell" in out
    assert math.isfinite(out["best_cell"]["test_mean_grand"])


def test_composition_end_to_end_pipeline_env_mlp_train_test_record(small_split):
    """End-to-end: build env -> train MLP -> evaluate on test ->
    record well-formed comparison dict (ready for a results doc).

    Composition: full producer-consumer chain.
    """
    from prometheus_math.bsd_rank_env import BSDRankEnv, train_random_bsd
    from prometheus_math.bsd_rank_mlp import (
        evaluate_mlp_on_corpus,
        train_mlp_bsd,
        welch_one_sided,
    )

    train = small_split["train"]
    test = small_split["test"]

    # --- Train MLP ---
    env = BSDRankEnv(corpus=train, split="all", seed=23)
    mlp_out = train_mlp_bsd(
        env, n_episodes=300, lr=5e-4, entropy_coef=0.01, seed=23,
    )
    env.close()

    # --- Evaluate on test ---
    mlp_eval = evaluate_mlp_on_corpus(
        mlp_out["policy"], BSDRankEnv, test, seed=23 + 100000,
    )

    # --- Random baseline on test ---
    e = BSDRankEnv(corpus=test, split="all", seed=23 + 200000)
    rnd_eval = train_random_bsd(
        e, n_episodes=len(test), seed=23 + 200000,
    )
    e.close()

    # --- Build the comparison record (the artifact a results doc consumes) ---
    record = {
        "mlp": {
            "train_mean_reward": mlp_out["mean_reward"],
            "train_accuracy": mlp_out["accuracy"],
            "test_mean_reward": mlp_eval["mean_reward"],
            "test_accuracy": mlp_eval["accuracy"],
            "pred_counts": mlp_eval["pred_counts"],
        },
        "random": {
            "test_mean_reward": rnd_eval["mean_reward"],
            "test_accuracy": rnd_eval["accuracy"],
        },
        "p_value_mlp_vs_random": welch_one_sided(
            mlp_eval["rewards"], rnd_eval["rewards"]
        ),
        "n_test": int(mlp_eval["n_episodes"]),
    }

    # Schema check on the record.
    assert "mlp" in record and "random" in record
    for k in ("train_mean_reward", "train_accuracy",
             "test_mean_reward", "test_accuracy", "pred_counts"):
        assert k in record["mlp"], f"missing record['mlp'][{k!r}]"
    for k in ("test_mean_reward", "test_accuracy"):
        assert k in record["random"], f"missing record['random'][{k!r}]"
    assert math.isfinite(record["mlp"]["test_mean_reward"])
    assert math.isfinite(record["random"]["test_mean_reward"])
    # The p-value should be a finite real in [0, 1] (or NaN if the
    # rewards happen to be degenerate, which they shouldn't be at this
    # corpus size).
    p = record["p_value_mlp_vs_random"]
    if not math.isnan(p):
        assert 0.0 <= p <= 1.0, f"p-value out of range: {p}"
