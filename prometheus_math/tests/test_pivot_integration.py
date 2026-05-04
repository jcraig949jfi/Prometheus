"""Cross-module integration tests for the eight-week-pivot stack.

These tests are intentionally cross-cutting: each one exercises at
least two of the six modules audited on 2026-04-29
(sigma_kernel.bind_eval, sigma_kernel.residuals, prometheus_math.
sigma_env, prometheus_math.arsenal_meta, prometheus_math.sigma_env_ppo,
prometheus_math.discovery_env). The per-module test files cover the
math-tdd four-categories rubric for individual ops; this file covers
the *seams* — the place where bugs that pass per-module unit tests
typically live.

Three integration spines (per audit deliverable):

  1. BIND/EVAL → arsenal_meta → SigmaMathEnv → REINFORCE end-to-end.
  2. BIND/EVAL → DiscoveryEnv → contextual REINFORCE.
  3. residuals.REFINE composing with bind_eval-bound callables.

Budget cap: each test runs in <2s on a stock workstation. RL-ish
tests cap n_steps <= 500.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from sigma_kernel.sigma_kernel import (
    Capability,
    SigmaKernel,
    Tier,
)
from sigma_kernel.bind_eval import (
    BindEvalExtension,
    CostModel,
)
from sigma_kernel.residuals import (
    ResidualExtension,
)
from prometheus_math.arsenal_meta import ARSENAL_REGISTRY
from prometheus_math.sigma_env import SigmaMathEnv
from prometheus_math.sigma_env_ppo import (
    train_baseline_random,
    train_reinforce,
)
from prometheus_math.discovery_env import (
    DiscoveryEnv,
    COEFFICIENT_CHOICES,
    N_COEFFICIENT_ACTIONS,
)


# ---------------------------------------------------------------------------
# Spine 1 — BIND/EVAL → arsenal_meta → SigmaMathEnv → REINFORCE
# ---------------------------------------------------------------------------


def test_integration_arsenal_meta_drives_sigma_env_costs():
    """ARSENAL_REGISTRY's cost models flow into SigmaMathEnv's BIND
    invocations. After env.reset() the bindings table contains a row
    whose cost_model JSON matches the registered ArsenalMeta cost.

    Spine 1, seam 1: arsenal_meta ↔ sigma_env (cost-injection path).
    """
    env = SigmaMathEnv(max_steps=3, seed=0)
    env.reset()
    k = env.kernel()
    # Pull the binding row for techne.lib.mahler_measure:mahler_measure.
    cur = k.conn.execute(
        "SELECT callable_ref, cost_model FROM bindings "
        "WHERE callable_ref=?",
        ("techne.lib.mahler_measure:mahler_measure",),
    )
    row = cur.fetchone()
    assert row is not None, "mahler_measure should be bound by reset()"
    callable_ref, cost_model_json = row
    import json
    cost = json.loads(cost_model_json)
    # Cost should match the registered ArsenalMeta cost (within small
    # serialization tolerance for the float fields).
    meta = ARSENAL_REGISTRY[callable_ref]
    assert math.isclose(
        cost["max_seconds"], meta.cost["max_seconds"], rel_tol=1e-9
    )
    assert cost["max_oracle_calls"] == meta.cost["max_oracle_calls"]


def test_integration_bind_eval_through_sigma_env_step():
    """A single env.step() exercises the full BIND/EVAL pipeline: cap
    minted → EVAL invoked → output_repr parsed → reward computed.

    Spine 1, seam 2: bind_eval ↔ sigma_env (per-step opcode path). If
    BIND/EVAL's symbol-write or capability discipline drifts, this
    catches it via env-level effects.
    """
    env = SigmaMathEnv(max_steps=5, seed=1)
    env.reset()
    k = env.kernel()
    n_caps_before = k.conn.execute(
        "SELECT COUNT(*) FROM capabilities"
    ).fetchone()[0]
    n_evals_before = k.conn.execute(
        "SELECT COUNT(*) FROM evaluations"
    ).fetchone()[0]
    # Pick the Lehmer action for a deterministic +100 reward.
    table = env.action_table()
    lehmer_idx = next(
        (i for i, r in enumerate(table) if "Lehmer" in r.arg_label), 0
    )
    obs, r, term, trunc, info = env.step(lehmer_idx)
    n_caps_after = k.conn.execute(
        "SELECT COUNT(*) FROM capabilities"
    ).fetchone()[0]
    n_evals_after = k.conn.execute(
        "SELECT COUNT(*) FROM evaluations"
    ).fetchone()[0]
    # One eval cap minted by the env + one internal PromoteCap minted by
    # BindEvalKernelV2 to drive kernel.PROMOTE (the dual-cap pattern
    # documented in sigma_kernel/BIND_EVAL_V2_NOTES.md). One evaluation
    # row written. Migration 2026-05-04 from v1 (n=+1) to v2 (n=+2).
    assert n_caps_after == n_caps_before + 2
    assert n_evals_after == n_evals_before + 1
    assert r >= 100.0


def test_integration_reinforce_concentrates_on_real_arsenal_op():
    """A 300-step REINFORCE run on SigmaMathEnv learns to favor an
    arsenal_meta-registered callable (Mahler measure) over a less-
    productive one (dilogarithm at irrelevant inputs). The env action
    table includes both; after training, the policy puts more mass on
    the Mahler-measure family.

    Spine 1, seam 3: arsenal_meta + bind_eval + sigma_env + REINFORCE.
    Budget capped at 300 steps (<2s on a stock host).
    """
    def factory():
        return SigmaMathEnv(
            objective="minimize_mahler_measure", max_steps=200, seed=0,
        )
    result = train_reinforce(factory, n_steps=300, seed=0, lr=0.05)
    probs = np.asarray(result["policy_probs"])
    # Action table has 13 entries; first 10 are mahler_measure callables,
    # last 3 are dilogarithm. Sum the probability mass on each side.
    mass_mahler = float(probs[:10].sum())
    mass_dilog = float(probs[10:].sum())
    assert mass_mahler > mass_dilog, (
        f"REINFORCE should put more mass on mahler_measure family "
        f"({mass_mahler:.3f}) than dilogarithm family ({mass_dilog:.3f})"
    )


# ---------------------------------------------------------------------------
# Spine 2 — BIND/EVAL → DiscoveryEnv → contextual REINFORCE
# ---------------------------------------------------------------------------


def test_integration_discovery_env_uses_bind_eval_substrate():
    """DiscoveryEnv's M-evaluation is a BIND/EVAL through the kernel.
    After a single completed episode, the substrate has 1 binding
    (for mahler_measure) and 1 evaluation (the result of the EVAL).

    Spine 2, seam 1: bind_eval ↔ discovery_env (substrate-as-action).
    """
    env = DiscoveryEnv(degree=6, seed=0)
    env.reset()
    actions = [4, 4, 3, 4]  # arbitrary half (degree 6 has half_len=4)
    for a in actions:
        _, _, term, _, info = env.step(a)
    assert term is True
    k = env.kernel()
    n_bindings = k.conn.execute(
        "SELECT COUNT(*) FROM bindings"
    ).fetchone()[0]
    n_evals = k.conn.execute(
        "SELECT COUNT(*) FROM evaluations"
    ).fetchone()[0]
    assert n_bindings >= 1, "DiscoveryEnv must BIND mahler_measure on reset"
    assert n_evals == 1, "exactly one EVAL per completed episode"


def test_integration_discovery_env_reinforce_short_run():
    """A 200-step REINFORCE on DiscoveryEnv runs end-to-end without
    crashing and produces a finite policy distribution. The action
    space is N_COEFFICIENT_ACTIONS=7 (cardinality test); rewards are
    bounded.

    Spine 2, seam 2: discovery_env ↔ sigma_env_ppo. Budget capped at
    200 steps to stay <2s. Short runs don't necessarily converge,
    so we don't assert lift > 0.
    """
    def factory():
        return DiscoveryEnv(degree=6, seed=0)
    result = train_reinforce(factory, n_steps=200, seed=0, lr=0.05)
    probs = np.asarray(result["policy_probs"])
    assert probs.shape == (N_COEFFICIENT_ACTIONS,)
    assert math.isclose(float(probs.sum()), 1.0, rel_tol=1e-9)
    assert math.isfinite(result["mean_reward"])


def test_integration_discovery_env_random_baseline_substrate_grows():
    """A 50-step random-baseline run on DiscoveryEnv writes the right
    number of evaluations to the substrate. With degree=6 (half_len=4)
    and 50 steps, ~12 episodes complete (with auto-reset), so the
    substrate accumulates ~12 evaluations.

    Spine 2, seam 3: bind_eval ↔ discovery_env ↔ random baseline.
    Tolerates auto-reset's kernel-recreation: we check the env's own
    n_evals counter, which persists across the *current* env instance.
    """
    # Use a single env directly (factory-based runs auto-reset, which
    # resets the kernel because DiscoveryEnv.reset only re-binds if
    # _kernel is None — so substrate persists across episodes within
    # one env instance).
    env = DiscoveryEnv(degree=6, seed=2)
    env.reset()
    rng = np.random.default_rng(2)
    n_episodes = 0
    for _ in range(50):
        a = int(rng.integers(0, N_COEFFICIENT_ACTIONS))
        _, _, term, _, _ = env.step(a)
        if term:
            n_episodes += 1
            env.reset()
    k = env.kernel()
    n_evals = k.conn.execute(
        "SELECT COUNT(*) FROM evaluations"
    ).fetchone()[0]
    # n_evals matches the count of completed episodes (each episode
    # ends in exactly one EVAL through the substrate).
    assert n_evals == n_episodes


# ---------------------------------------------------------------------------
# Spine 3 — residuals.REFINE composing with bind_eval-bound callables
# ---------------------------------------------------------------------------


def test_integration_refine_chained_after_bind_eval():
    """A residual recorded against a CLAIM whose target was originally
    a BIND output composes correctly: BIND → EVAL → record_residual →
    REFINE produces a refined claim with cost_budget halved.

    Spine 3, seam 1: bind_eval ↔ residuals. Even though residuals
    operate on Claim objects (not Symbols/Bindings directly), the
    pipeline is meant to compose: an EVAL that "almost passes" should
    be recordable as a non-uniform residual.
    """
    k = SigmaKernel(":memory:")
    bind_ext = BindEvalExtension(k)
    res_ext = ResidualExtension(k)

    # BIND a callable.
    cap_b = k.mint_capability("BindCap")
    binding = bind_ext.BIND(
        callable_ref="prometheus_math.numerics_special_dilogarithm:dilogarithm",
        cost_model=CostModel(max_seconds=2.0),
        cap=cap_b,
    )
    # EVAL it (sanity).
    cap_e = k.mint_capability("EvalCap")
    ev = bind_ext.EVAL(
        binding_name=binding.symbol.name,
        binding_version=binding.symbol.version,
        args=[1.0],
        cap=cap_e,
    )
    assert ev.success
    # Now claim something about the EVAL output, then record a residual.
    parent_claim = k.CLAIM(
        target_name=binding.symbol.name,
        hypothesis="Li_2(1) approximated by mpmath polylog within 1e-9",
        evidence={"binding_ref": f"{binding.symbol.name}@v{binding.symbol.version}",
                  "output_repr": ev.output_repr},
        kill_path="bind_eval_kill",
        target_tier=Tier.Conjecture,
    )
    residual = res_ext.record_residual(
        parent_claim_id=parent_claim.id,
        test_id="bind_eval_residual",
        magnitude=0.05,
        surviving_subset={"items": ["Li2_1"], "n": 1},
        failure_shape={
            "kind": "polynomial_residual",
            "variety_signature": "dilog_anchor",
            "coeff_variance": 0.9,
        },
        instrument_id="bind_eval_test",
        cost_budget=10.0,
    )
    assert residual.classification == "signal"
    cap_r = k.mint_capability("RefineCap")
    refined = res_ext.REFINE(parent_claim, residual, cap=cap_r)
    assert math.isclose(refined.cost_budget_remaining, 5.0, rel_tol=1e-9)
    # Refined claim provenance points back to the BIND-output claim.
    assert refined.parent_claim_id_or_root == parent_claim.id


def test_integration_residual_extension_coexists_with_bind_eval():
    """Both extensions can attach to the same kernel without conflict.
    Tables `bindings`, `evaluations`, `residuals`, `refinements` all
    coexist; the kernel's _TABLES list is patched coherently.

    Spine 3, seam 2: bind_eval + residuals share the same kernel.
    Catches schema-clash / table-creation-order regressions.
    """
    k = SigmaKernel(":memory:")
    bind_ext = BindEvalExtension(k)
    res_ext = ResidualExtension(k)
    # All four tables exist (SQLite path).
    for tbl in ("bindings", "evaluations", "residuals", "refinements"):
        cur = k.conn.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (tbl,),
        )
        assert cur.fetchone() is not None, f"table {tbl} missing"


def test_integration_arsenal_meta_authority_refs_consumed_by_bind():
    """authority_refs declared in ArsenalMeta are stored in the bindings
    table when SigmaMathEnv.reset() does the BIND. End-to-end: ArsenalMeta
    → BindEvalExtension.BIND → bindings.authority_refs column.

    Spine 1+3 cross: arsenal_meta ↔ bind_eval (provenance flow). If the
    decorator metadata doesn't reach the BIND row, downstream consumers
    (audit tools, residual classifier) lose authority context.
    """
    env = SigmaMathEnv(max_steps=2, seed=3)
    env.reset()
    k = env.kernel()
    cur = k.conn.execute(
        "SELECT callable_ref, authority_refs FROM bindings WHERE callable_ref=?",
        ("techne.lib.mahler_measure:mahler_measure",),
    )
    row = cur.fetchone()
    assert row is not None
    import json
    auth = json.loads(row[1])
    meta_auth = ARSENAL_REGISTRY[row[0]].authority_refs
    # Authority refs from ArsenalMeta should equal what's stored in DB.
    assert auth == meta_auth


def test_integration_random_vs_reinforce_lift_finite_on_discovery():
    """The lift comparison wires through cleanly between the
    random baseline (sigma_env_ppo) and DiscoveryEnv. We don't assert
    lift > 0 at low budget — we DO assert the comparison framework
    closes the loop.

    Spine 2 closing test: end-to-end discovery_env + sigma_env_ppo.
    Budget capped at 200 steps × 1 seed (<2s).
    """
    def factory():
        return DiscoveryEnv(degree=6, seed=0)
    rand = train_baseline_random(factory, n_steps=200, seed=0)
    learn = train_reinforce(factory, n_steps=200, seed=0, lr=0.05)
    assert math.isfinite(rand["mean_reward"])
    assert math.isfinite(learn["mean_reward"])
    # Both rewards live in the bounded reward set.
    valid_rewards = {-1.0, 0.0, 1.0, 5.0, 20.0, 100.0,
                     # shaped rewards live in [0, ~98]; default env is 'step'
                     }
    for r in np.unique(rand["rewards"]):
        assert float(r) in valid_rewards, f"unexpected random reward {r}"
