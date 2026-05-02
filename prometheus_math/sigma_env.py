"""prometheus_math.sigma_env — Gymnasium-compatible RL env over the substrate.

Wraps the sigma kernel + BIND/EVAL extension + arsenal registry as a
standard RL environment. An agent's action is "pick an arsenal op + an
arg from the small discrete arg set"; the reward signal is whether the
output satisfies the chosen objective predicate.

Design:
- Observation: a fixed-size feature vector summarising substrate state
  (n_bindings, n_evaluations, n_successful_evaluations, last_reward,
  best_objective_value_so_far). Enough for a small RL agent to learn
  whether actions are productive.
- Action: an integer in [0, n_actions) selecting (op_id, arg_id) from
  the action table the env builds at reset.
- Reward: derived from the objective predicate. The default predicate
  ``"minimize_mahler_measure"`` rewards finding integer reciprocal
  polynomials with M(P) close to (but above) 1. Agents that learn to
  pick mahler_measure with palindromic-coefficient args get reward.
- Done: when ``max_steps`` reached or objective threshold hit.

The env is Gymnasium-spec but does NOT depend on gymnasium at import
time. If gymnasium is installed, ``register_with_gymnasium()`` exposes
``"prometheus/SigmaMath-v0"``. If not, the bare env works directly via
``reset()`` / ``step()``.
"""
from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.bind_eval import (
    BindEvalExtension,
    CostModel,
    BudgetExceeded,
)
from .arsenal_meta import ARSENAL_REGISTRY, ArsenalMeta


# ---------------------------------------------------------------------------
# Action table
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ActionRow:
    """One concrete action: a bound arsenal op + a chosen argument."""

    op_id: int  # index into the action table
    callable_ref: str
    binding_name: str  # name of the live binding
    binding_version: int
    arg_label: str  # human-readable arg description
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]


# ---------------------------------------------------------------------------
# Objective predicates
# ---------------------------------------------------------------------------


def _objective_minimize_mahler_measure(
    eval_result: Any,
    args: Tuple[Any, ...],
    arg_label: str,
) -> Tuple[float, bool]:
    """Reward for finding low-M reciprocal polys.

    Returns (reward, hit_target).

    Reward shape:
    - +1.0 for any M finite in [1, 5)
    - +5.0 if M < 2.0
    - +20.0 if M < 1.5 (Lehmer-territory)
    - +100.0 if M < 1.18 (sub-Lehmer; would be a real find)
    - 0.0 otherwise (NaN, M>=5, etc.)
    """
    try:
        m = float(eval_result)
    except (TypeError, ValueError):
        return 0.0, False
    if not math.isfinite(m):
        return 0.0, False
    if m < 1.0 - 1e-9:
        # Reciprocal poly with M < 1 should not exist; numerical artifact.
        return 0.0, False
    hit = m < 1.18
    if m < 1.18:
        return 100.0, True
    if m < 1.5:
        return 20.0, False
    if m < 2.0:
        return 5.0, False
    if m < 5.0:
        return 1.0, False
    return 0.0, False


def _objective_riemann_zeros(
    eval_result: Any,
    args: Tuple[Any, ...],
    arg_label: str,
) -> Tuple[float, bool]:
    """Reward for evaluating Li_2 close to known reference values."""
    try:
        v = complex(eval_result)
    except (TypeError, ValueError):
        return 0.0, False
    target = math.pi * math.pi / 6.0
    if not args:
        return 0.0, False
    try:
        z = float(args[0])
    except (TypeError, ValueError):
        return 0.0, False
    if abs(z - 1.0) < 1e-9 and abs(v.real - target) < 1e-6 and abs(v.imag) < 1e-6:
        return 50.0, True
    if abs(z) < 1e-9 and abs(v) < 1e-9:
        return 5.0, False
    return 1.0, False


OBJECTIVES = {
    "minimize_mahler_measure": _objective_minimize_mahler_measure,
    "riemann_zeros": _objective_riemann_zeros,
}


# ---------------------------------------------------------------------------
# Env
# ---------------------------------------------------------------------------


def _default_action_table_for_lehmer() -> List[Dict[str, Any]]:
    """Action table for the Lehmer / Mahler-measure objective.

    Each entry: a callable_ref + a concrete args list. The agent picks
    a row index. Args are integer reciprocal polynomials of small
    coefficient-range so that an agent learning random selection has a
    real shot at productive picks (and a learning agent has a clean
    gradient between productive and non-productive choices).
    """
    mm_ref = "techne.lib.mahler_measure:mahler_measure"
    rows: List[Dict[str, Any]] = []
    # Cyclotomic-like and known-low-M reciprocal polys. Includes Lehmer's
    # poly itself as the "best" possible action.
    candidates = [
        ("Lehmer 1.176", [1, 1, 0, -1, -1, -1, -1, -1, 0, 1, 1]),
        ("salem-deg10-low", [1, 0, 0, 0, -1, -1, 0, 0, 0, 0, 1]),
        ("phi_5", [1, 1, 1, 1, 1]),
        ("phi_6", [1, -1, 1]),  # x^2 - x + 1
        ("phi_8", [1, 0, 0, 0, 1]),  # x^4 + 1
        ("simple-recip-deg4-A", [1, 2, 3, 2, 1]),
        ("simple-recip-deg4-B", [1, -2, 3, -2, 1]),
        ("simple-recip-deg6", [1, 1, 1, 1, 1, 1, 1]),
        ("noisy-deg4-A", [1, 3, 5, 3, 1]),
        ("noisy-deg6", [1, 2, 3, 4, 3, 2, 1]),
    ]
    for label, coeffs in candidates:
        rows.append({
            "callable_ref": mm_ref,
            "arg_label": label,
            "args": [coeffs],
            "kwargs": {},
        })
    # Dilogarithm at known anchor values for cross-domain.
    dl_ref = "prometheus_math.numerics_special_dilogarithm:dilogarithm"
    for label, z in [("Li2(1)=zeta(2)", 1.0), ("Li2(0)=0", 0.0), ("Li2(0.5)", 0.5)]:
        rows.append({
            "callable_ref": dl_ref,
            "arg_label": label,
            "args": [z],
            "kwargs": {},
        })
    return rows


class SigmaMathEnv:
    """Gymnasium-compatible env wrapping sigma kernel + arsenal.

    No hard dependency on gymnasium; if gymnasium is installed the env
    can be registered (see ``register_with_gymnasium``). Otherwise use
    directly: ``env.reset()`` returns ``(obs, info)``, ``env.step(action)``
    returns ``(obs, reward, terminated, truncated, info)``.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        objective: str = "minimize_mahler_measure",
        action_table: Optional[List[Dict[str, Any]]] = None,
        max_steps: int = 50,
        kernel_db_path: str = ":memory:",
        seed: Optional[int] = None,
    ):
        if objective not in OBJECTIVES:
            raise ValueError(
                f"unknown objective {objective!r}; choose from {sorted(OBJECTIVES)}"
            )
        self.objective_name = objective
        self._objective_fn = OBJECTIVES[objective]
        self._action_table_raw = action_table or _default_action_table_for_lehmer()
        self.max_steps = int(max_steps)
        self._kernel_db_path = kernel_db_path
        self._rng = random.Random(seed)
        self._kernel: Optional[SigmaKernel] = None
        self._ext: Optional[BindEvalExtension] = None
        self._actions: List[ActionRow] = []
        self._step_count = 0
        self._best_reward = 0.0
        self._best_value: Optional[float] = None
        self._n_success = 0
        self._n_total = 0
        self._last_reward = 0.0
        self._last_terminated = False

        # Gymnasium-style spec mirrors. We declare our own minimal Box/
        # Discrete proxies if gymnasium isn't available, so the env is
        # usable standalone.
        # Start the action space at the raw-table size so gymnasium's
        # Discrete(n>0) check passes; reset() rebuilds it once any
        # dedupe-driven sizing changes are known.
        n_actions_initial = max(1, len(self._action_table_raw))
        try:
            import gymnasium as gym  # noqa: F401
            from gymnasium import spaces

            self.observation_space = spaces.Box(
                low=-1e9, high=1e9, shape=(5,), dtype=np.float64
            )
            self.action_space = spaces.Discrete(n_actions_initial)
            self._gym_spaces = spaces
        except ImportError:
            self.observation_space = _BoxStub((5,))
            self.action_space = _DiscreteStub(n_actions_initial)
            self._gym_spaces = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def reset(
        self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        if seed is not None:
            self._rng = random.Random(seed)

        # Fresh kernel + extension per episode. (For multi-episode
        # training in one process, callers can pass a persistent
        # kernel_db_path; the table state survives in that case.)
        self._kernel = SigmaKernel(self._kernel_db_path)
        self._ext = BindEvalExtension(self._kernel)
        self._actions = []
        self._step_count = 0
        self._best_reward = 0.0
        self._best_value = None
        self._n_success = 0
        self._n_total = 0
        self._last_reward = 0.0
        self._last_terminated = False

        # Build the live action table by BIND-ing each unique callable_ref
        # to a binding-symbol. Dedupe so each callable is bound once.
        bind_cache: Dict[str, Tuple[str, int]] = {}
        for op_id, row in enumerate(self._action_table_raw):
            cref = row["callable_ref"]
            if cref in bind_cache:
                bname, bver = bind_cache[cref]
            else:
                meta = ARSENAL_REGISTRY.get(cref)
                cost = CostModel(**(meta.cost if meta else {}))
                cap = self._kernel.mint_capability("BindCap")
                binding = self._ext.BIND(
                    callable_ref=cref,
                    cost_model=cost,
                    postconditions=list(meta.postconditions) if meta else [],
                    authority_refs=list(meta.authority_refs) if meta else [],
                    cap=cap,
                )
                bname = binding.symbol.name
                bver = binding.symbol.version
                bind_cache[cref] = (bname, bver)
            self._actions.append(
                ActionRow(
                    op_id=op_id,
                    callable_ref=cref,
                    binding_name=bname,
                    binding_version=bver,
                    arg_label=row["arg_label"],
                    args=tuple(row["args"]),
                    kwargs=dict(row["kwargs"]),
                )
            )

        # Resize action_space if the live count differs from what we
        # initialized with.
        n_actions = len(self._actions)
        if self._gym_spaces is not None:
            if n_actions != getattr(self.action_space, "n", -1):
                self.action_space = self._gym_spaces.Discrete(max(1, n_actions))
        else:
            if n_actions != getattr(self.action_space, "n", -1):
                self.action_space = _DiscreteStub(max(1, n_actions))

        info = {"n_actions": n_actions, "objective": self.objective_name}
        return self._obs(), info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        if self._kernel is None or self._ext is None:
            raise RuntimeError("env.step() called before env.reset()")
        if action < 0 or action >= len(self._actions):
            raise ValueError(
                f"action {action} out of range [0, {len(self._actions)})"
            )
        row = self._actions[action]
        cap = self._kernel.mint_capability("EvalCap")

        truncated = False
        info: Dict[str, Any] = {
            "callable_ref": row.callable_ref,
            "arg_label": row.arg_label,
            "step": self._step_count,
        }
        try:
            ev = self._ext.EVAL(
                binding_name=row.binding_name,
                binding_version=row.binding_version,
                args=list(row.args),
                kwargs=row.kwargs,
                cap=cap,
                eval_version=self._step_count + 1,
            )
        except BudgetExceeded as e:
            self._step_count += 1
            self._last_reward = -1.0
            info["error"] = f"budget_exceeded: {e}"
            terminated = self._step_count >= self.max_steps
            return self._obs(), -1.0, terminated, False, info

        # Parse the output back from repr(); for the Lehmer objective the
        # output is a float so eval(repr(x)) round-trips. For richer
        # objectives we'd need a structured channel.
        try:
            output_value: Any = eval(ev.output_repr, {"__builtins__": {}}, {})
        except Exception:
            output_value = ev.output_repr

        reward, hit_target = self._objective_fn(
            output_value, row.args, row.arg_label
        )
        self._n_total += 1
        if ev.success:
            self._n_success += 1
        self._last_reward = float(reward)
        if reward > self._best_reward:
            self._best_reward = float(reward)
        if isinstance(output_value, (int, float)) and math.isfinite(output_value):
            v = float(output_value)
            if (
                self.objective_name == "minimize_mahler_measure"
                and v >= 1.0
                and (self._best_value is None or v < self._best_value)
            ):
                self._best_value = v

        self._step_count += 1
        terminated = bool(hit_target) or self._step_count >= self.max_steps
        info.update(
            {
                "output_value": output_value,
                "reward_breakdown": {
                    "magnitude": float(reward),
                    "hit_target": bool(hit_target),
                },
                "actual_cost": ev.actual_cost,
                "n_success": self._n_success,
                "n_total": self._n_total,
            }
        )
        self._last_terminated = terminated
        return self._obs(), float(reward), terminated, truncated, info

    # ------------------------------------------------------------------
    # Observation
    # ------------------------------------------------------------------

    def _obs(self) -> np.ndarray:
        best_val = self._best_value if self._best_value is not None else -1.0
        return np.array(
            [
                float(self._step_count),
                float(self._n_success),
                float(self._n_total),
                float(self._last_reward),
                float(best_val),
            ],
            dtype=np.float64,
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def action_table(self) -> List[ActionRow]:
        """Return the live action table (after reset)."""
        return list(self._actions)

    def kernel(self) -> SigmaKernel:
        """Return the underlying kernel (after reset). Useful for tests."""
        if self._kernel is None:
            raise RuntimeError("env not reset yet")
        return self._kernel

    def close(self) -> None:
        if self._kernel is not None:
            try:
                self._kernel.conn.close()
            except Exception:
                pass
        self._kernel = None
        self._ext = None


# ---------------------------------------------------------------------------
# Stubs (used when gymnasium is not installed)
# ---------------------------------------------------------------------------


class _BoxStub:
    def __init__(self, shape):
        self.shape = tuple(shape)
        self.dtype = np.float64

    def contains(self, x) -> bool:
        return isinstance(x, np.ndarray) and x.shape == self.shape


class _DiscreteStub:
    def __init__(self, n: int):
        self.n = int(n)

    def sample(self) -> int:
        if self.n <= 0:
            raise RuntimeError("action_space empty (call reset() first)")
        return random.randrange(self.n)

    def contains(self, x) -> bool:
        return isinstance(x, int) and 0 <= x < self.n


# ---------------------------------------------------------------------------
# Optional gymnasium registration
# ---------------------------------------------------------------------------


def register_with_gymnasium() -> Optional[str]:
    """Register ``"prometheus/SigmaMath-v0"`` with gymnasium.

    Returns the env_id on success, ``None`` if gymnasium isn't installed.
    """
    try:
        import gymnasium as gym
    except ImportError:
        return None
    env_id = "prometheus/SigmaMath-v0"
    try:
        gym.register(
            id=env_id,
            entry_point="prometheus_math.sigma_env:SigmaMathEnv",
        )
    except Exception:
        # Already registered or gymnasium changed signature; ignore.
        pass
    return env_id


__all__ = [
    "SigmaMathEnv",
    "ActionRow",
    "OBJECTIVES",
    "register_with_gymnasium",
]
