"""prometheus_math.discovery_env_v2 — GA-style reciprocal-polynomial RL env.

Sibling to ``discovery_env.py``.  Where v1 builds a polynomial coefficient-
by-coefficient from a uniform-enumeration prior (7^6 ≈ 117K trajectories
at degree 10, no inductive bias), v2 maintains a *population* of low-M
reciprocal polynomials and the agent's actions are *mutation operators*
applied to the population.  This is the GA-style generator Mossinghoff
used to find his original Salem polynomials, lifted into the substrate-
mediated RL framing.

Selection strategies (anti-elitist additions, 2026-05-04)
----------------------------------------------------------
The original V2 selection rule was strict elitist replacement (child
displaces worst iff child.M < worst.M).  The DISCOVERY_V2_RESULTS pilot
showed this collapses to the cyclotomic basin (M=1 exactly) — by
generation 50 ~87% of the population is cyclotomic and the search is
stuck.  To explore the diversity-preservation question we now offer
four selection strategies, switched via ``selection_strategy``:

  * ``"elitist"`` — the original (regression baseline).
  * ``"tournament_novelty"`` — child only displaces worst if it scores
    higher on a (negative-fitness + novelty) composite.  Novelty is
    Euclidean distance from the population centroid in half-coefficient
    space; this rewards polys that explore *different* regions.
  * ``"crowding"`` — NSGA-II crowding-distance penalty on dense regions.
    The replacement target is whichever member has the smallest crowding
    distance (most crowded), provided child improves the (M, novelty)
    pareto frontier.
  * ``"restart_collapse"`` — vanilla elitist by default, but if M-variance
    drops below ``collapse_threshold`` for ``collapse_window`` consecutive
    generations, half the population is randomly reinitialized.

Why a different generator?
--------------------------
The v1 four-counts pilot ran 216K episodes across 7 ablation cells and
produced 0 PROMOTEs.  That bounds the discovery rate of *uniform
enumeration* — but tells us nothing about whether a richer generator
(one with structural inductive bias toward known low-M neighborhoods)
can break the ceiling.  v2 is the generator-richness ablation.

Population shape
----------------
* ``population_size`` reciprocal polynomials, each represented by a
  half-coefficient vector ``half = [a_0, ..., a_k]`` of length
  ``half_len = ceil(degree/2) + 1`` over alphabet ``{-3..3}``.
* Population is initialized either (a) uniform-random over the alphabet
  or (b) seeded from a small canonical low-M set (Lehmer + first few
  Salem-deg-10 entries from the Mossinghoff snapshot, perturbed if
  population exceeds seed size).
* Each member has a cached Mahler measure; the population is sorted
  ascending by M so ``population[0]`` is the elite and
  ``population[-1]`` is the eviction target.

Action space
------------
``Discrete(n_operators)`` where ``n_operators ≈ 5-8``.  Each action
indexes a mutation operator that:

  1. picks a population member (random or worst, depending on op),
  2. applies a coefficient-level edit (palindromic constraint preserved
     by construction — we mutate the half-vector and mirror),
  3. evaluates M,
  4. replaces the current worst if M < worst-M (elitist replacement).

The operator menu (defined in ``MUTATION_OPERATORS``):

  * ``mutate_single_coef`` — flip one coefficient to a fresh random alphabet entry.
  * ``mutate_two_coefs`` — flip two coefficients independently.
  * ``swap_palindromic_pairs`` — swap two half-coefficients (so the mirrored pair swaps too).
  * ``increment_at_index`` — bump one coefficient by +1 (clipped to alphabet max).
  * ``decrement_at_index`` — bump one coefficient by -1 (clipped to alphabet min).
  * ``zero_at_index`` — set one coefficient to 0.
  * ``crossover`` — pick two parents, take half from each (preserves palindromic).

Episode shape
-------------
``n_mutations_per_episode`` mutations are applied (default = ``population_size * 2``).
At episode end the population's elite (``population[0]``) is the
"best of generation" candidate; if its M lies in the sub-Lehmer band
(``1.001 < M < 1.18``), the candidate is routed through
``DiscoveryPipeline.process_candidate`` for catalog cross-check + the
F1+F6+F9+F11 battery.  Per-episode reward is the (negated) elite M
plus a bonus if the elite improved over the previous episode's elite
plus a +50 bonus if elite is sub-Lehmer.

Reward shape
------------
Reward computation is *non-negative* (so the property test below holds
for non-degenerate polys).  Components::

    base       = max(0, 5 - elite_M)         # gradient toward low M
    improve_bonus = max(0, prev_elite_M - elite_M) * 10  # learning signal
    band_bonus = +50 if elite_M in (1.001, 1.18) else 0  # sub-Lehmer
    catalog_bonus = +20 if catalog_miss + survives battery (SHADOW_CATALOG)

Authority anchor
----------------
Mossinghoff's original GA-style search recovered the Salem cluster +
extended Lehmer's list out to higher degrees by *exactly* this kind of
mutation-driven population search.  The v2 env is faithful to that
mechanism — it just adds (a) substrate-mediated EVAL through SigmaKernel,
(b) a learnable policy over mutation operators, (c) the kill-path
battery as the survival filter.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.bind_eval import (
    BindEvalExtension,
    BudgetExceeded,
    CostModel,
)


# ---------------------------------------------------------------------------
# Coefficient alphabet (matches v1)
# ---------------------------------------------------------------------------


COEFFICIENT_CHOICES_V2: Tuple[int, ...] = (-3, -2, -1, 0, 1, 2, 3)


# ---------------------------------------------------------------------------
# Mutation operators
# ---------------------------------------------------------------------------
#
# Each operator is a pure function `op(half: List[int], rng,
# alphabet) -> List[int]` that returns a new half-vector (the operator
# does NOT touch the population data structure; that's the env's job).
# All operators preserve the half-vector length (palindromic mirroring
# happens downstream of the half-vector — every half-vector mirrors to
# a valid palindromic full polynomial).


def _mutate_single_coef(
    half: List[int], rng: np.random.Generator, alphabet: Tuple[int, ...]
) -> List[int]:
    """Flip one half-coefficient to a fresh random alphabet entry."""
    out = list(half)
    if not out:
        return out
    idx = int(rng.integers(0, len(out)))
    new_val = int(alphabet[int(rng.integers(0, len(alphabet)))])
    out[idx] = new_val
    return out


def _mutate_two_coefs(
    half: List[int], rng: np.random.Generator, alphabet: Tuple[int, ...]
) -> List[int]:
    """Flip two half-coefficients independently."""
    out = _mutate_single_coef(half, rng, alphabet)
    return _mutate_single_coef(out, rng, alphabet)


def _swap_palindromic_pairs(
    half: List[int], rng: np.random.Generator, alphabet: Tuple[int, ...]
) -> List[int]:
    """Swap two half-coefficients (the mirrored pair swaps automatically)."""
    out = list(half)
    if len(out) < 2:
        return out
    i, j = rng.choice(len(out), size=2, replace=False)
    out[int(i)], out[int(j)] = out[int(j)], out[int(i)]
    return out


def _increment_at_index(
    half: List[int], rng: np.random.Generator, alphabet: Tuple[int, ...]
) -> List[int]:
    """Bump one coefficient by +1, clipped to alphabet max."""
    out = list(half)
    if not out:
        return out
    idx = int(rng.integers(0, len(out)))
    a_max = max(alphabet)
    out[idx] = int(min(a_max, out[idx] + 1))
    return out


def _decrement_at_index(
    half: List[int], rng: np.random.Generator, alphabet: Tuple[int, ...]
) -> List[int]:
    """Bump one coefficient by -1, clipped to alphabet min."""
    out = list(half)
    if not out:
        return out
    idx = int(rng.integers(0, len(out)))
    a_min = min(alphabet)
    out[idx] = int(max(a_min, out[idx] - 1))
    return out


def _zero_at_index(
    half: List[int], rng: np.random.Generator, alphabet: Tuple[int, ...]
) -> List[int]:
    """Set one half-coefficient to 0."""
    out = list(half)
    if not out:
        return out
    idx = int(rng.integers(0, len(out)))
    out[idx] = 0
    return out


def _identity(
    half: List[int], rng: np.random.Generator, alphabet: Tuple[int, ...]
) -> List[int]:
    """No-op (used when mutation_rate == 0; documents the agent state).

    Returns an exact copy.  Useful as a property anchor: agent that
    only ever picks identity gets identity reward (0 improvement).
    """
    return list(half)


MutationOp = Callable[
    [List[int], np.random.Generator, Tuple[int, ...]], List[int]
]


MUTATION_OPERATORS: Tuple[Tuple[str, MutationOp], ...] = (
    ("mutate_single_coef", _mutate_single_coef),
    ("mutate_two_coefs", _mutate_two_coefs),
    ("swap_palindromic_pairs", _swap_palindromic_pairs),
    ("increment_at_index", _increment_at_index),
    ("decrement_at_index", _decrement_at_index),
    ("zero_at_index", _zero_at_index),
    ("identity", _identity),
)


N_MUTATION_OPERATORS = len(MUTATION_OPERATORS)


# ---------------------------------------------------------------------------
# Selection-strategy registry (anti-elitist diversity preservation)
# ---------------------------------------------------------------------------
#
# Each strategy is a free function with signature
#   strategy(population, child, state, rng) -> (replaced_idx | None,
#                                                strategy_info)
# and operates on the population list IN PLACE if it decides to replace.
# The returned ``replaced_idx`` is the slot that was overwritten (or
# None if the child was rejected); the ``strategy_info`` dict is folded
# into the env's step() info so callers can inspect strategy behavior.


SELECTION_STRATEGIES: Tuple[str, ...] = (
    "elitist",
    "tournament_novelty",
    "crowding",
    "restart_collapse",
)


def _half_centroid(population: List["PopulationMember"]) -> np.ndarray:
    """Centroid of the half-coefficient space (NaN-safe; returns zeros on empty)."""
    if not population:
        return np.zeros(0, dtype=np.float64)
    arr = np.asarray([m.half for m in population], dtype=np.float64)
    return arr.mean(axis=0)


def _half_distance_to_centroid(
    half: List[int], centroid: np.ndarray
) -> float:
    """Euclidean distance from a half-vector to a centroid; 0 if centroid empty."""
    if centroid.size == 0:
        return 0.0
    v = np.asarray(half, dtype=np.float64)
    if v.shape != centroid.shape:
        return 0.0
    return float(np.linalg.norm(v - centroid))


def _population_m_variance(population: List["PopulationMember"]) -> float:
    """Variance of finite M values in the population.  Inf if all members
    are non-finite (degenerate case) so the collapse-trigger does NOT
    treat all-inf as collapsed."""
    ms = [m.m_value for m in population if math.isfinite(m.m_value)]
    if len(ms) < 2:
        return float("inf")
    return float(np.var(ms))


# ---------------------------------------------------------------------------
# Polynomial helpers (same conventions as v1)
# ---------------------------------------------------------------------------


def _palindromic_from_half(half: List[int], degree: int) -> List[int]:
    """Mirror a half-vector into a palindromic polynomial.

    Same convention as v1: ``out[i] = half[i]`` for ``i <= degree//2``,
    ``out[degree-i] = half[i]`` for the mirrored entries.
    """
    if degree < 2:
        raise ValueError(f"degree must be >= 2; got {degree}")
    n = degree + 1
    out = [0] * n
    half_len = (degree // 2) + 1
    if len(half) < half_len:
        raise ValueError(
            f"need {half_len} half-coeffs for degree {degree}; got {len(half)}"
        )
    for i in range(half_len):
        out[i] = half[i]
        out[degree - i] = half[i]
    return out


def _is_reciprocal(coeffs: List[int]) -> bool:
    n = len(coeffs)
    return all(coeffs[i] == coeffs[n - 1 - i] for i in range(n // 2))


# ---------------------------------------------------------------------------
# Reward shape (v2-specific; non-negative for non-degenerate polys)
# ---------------------------------------------------------------------------


def _compute_reward_v2(
    elite_m: float,
    prev_elite_m: float,
    is_sub_lehmer: bool,
    is_signal_class: bool,
) -> Tuple[float, str]:
    """Episode-level reward for v2.  Non-negative on non-degenerate polys.

    Components:
      * ``base = max(0, 5 - elite_m)`` — gradient toward low M.
      * ``improve_bonus = max(0, prev_elite_m - elite_m) * 10`` — explicit
        learning signal (rewards population improvement).
      * ``band_bonus = +50`` iff ``1.001 < elite_m < 1.18``.
      * ``catalog_bonus = +20`` iff the candidate landed in
        SHADOW_CATALOG / PROMOTED.
    """
    if not math.isfinite(elite_m) or elite_m < 1.0 - 1e-9:
        return 0.0, "non_finite_or_artifact"
    base = max(0.0, 5.0 - elite_m)
    if math.isfinite(prev_elite_m):
        improve_bonus = max(0.0, prev_elite_m - elite_m) * 10.0
    else:
        improve_bonus = 0.0
    band_bonus = 50.0 if is_sub_lehmer else 0.0
    catalog_bonus = 20.0 if is_signal_class else 0.0
    total = base + improve_bonus + band_bonus + catalog_bonus
    if is_signal_class:
        label = "shadow_catalog"
    elif is_sub_lehmer:
        label = "sub_lehmer"
    elif elite_m < 1.5:
        label = "salem_cluster"
    elif elite_m < 2.0:
        label = "low_m"
    else:
        label = "functional"
    return float(total), label


# ---------------------------------------------------------------------------
# Population dataclass
# ---------------------------------------------------------------------------


@dataclass
class PopulationMember:
    """One reciprocal polynomial in the population.

    The half-vector is the *truth*; the full polynomial is derived by
    mirroring; the M-value is cached.  Mutation operators rewrite
    ``half``, and the env recomputes M after every mutation.
    """

    half: List[int]
    m_value: float = float("inf")

    def full(self, degree: int) -> List[int]:
        return _palindromic_from_half(self.half, degree)


# ---------------------------------------------------------------------------
# Seeding helpers
# ---------------------------------------------------------------------------


# A small canonical low-M Salem set (degree 10).  Used as default seeds
# when ``seed_with_known=True`` and degree=10.  Pulled from the
# Mossinghoff snapshot (lehmer + first few Salem-deg-10 entries).
LEHMER_HALF: Tuple[int, ...] = (1, 1, 0, -1, -1, -1)
KNOWN_SEEDS_DEG10: Tuple[Tuple[int, ...], ...] = (
    LEHMER_HALF,
    (1, 0, 0, 0, -1, 1),  # Salem deg 10 #2 (M ≈ 1.216)
    (1, 0, 0, 1, 0, 1),   # Salem deg 10 #3 (M ≈ 1.230)
    (1, 0, -1, 0, 0, 1),  # Salem deg 10 #4 (M ≈ 1.261)
)


def _initial_population(
    population_size: int,
    half_len: int,
    alphabet: Tuple[int, ...],
    rng: np.random.Generator,
    seed_with_known: bool,
    degree: int,
) -> List[PopulationMember]:
    """Build the initial population.

    If ``seed_with_known`` and degree=10, seed the first
    ``min(population_size, len(KNOWN_SEEDS_DEG10))`` slots with the
    canonical Salem-deg-10 set; fill the rest with random half-vectors.
    Otherwise, all slots are random.
    """
    members: List[PopulationMember] = []
    if seed_with_known and degree == 10:
        for h in KNOWN_SEEDS_DEG10[:population_size]:
            members.append(PopulationMember(half=list(h)))
    while len(members) < population_size:
        h = [
            int(alphabet[int(rng.integers(0, len(alphabet)))])
            for _ in range(half_len)
        ]
        members.append(PopulationMember(half=h))
    return members


# ---------------------------------------------------------------------------
# Episode result
# ---------------------------------------------------------------------------


@dataclass
class EpisodeRecordV2:
    """One episode's outcome — substrate-grade audit record."""

    elite_coeffs: List[int]
    elite_m: float
    reward: float
    reward_label: str
    n_mutations: int
    population_m_summary: Tuple[float, float, float]  # (min, median, max)
    is_signal_class: bool
    pipeline_terminal_state: Optional[str] = None
    pipeline_kill_pattern: Optional[str] = None


# ---------------------------------------------------------------------------
# The env
# ---------------------------------------------------------------------------


class DiscoveryEnvV2:
    """GA-style discovery env with mutation-operator action space.

    Gymnasium-compatible (same step/reset/spaces interface as v1); does
    not hard-depend on gymnasium.

    Action space:
        ``Discrete(n_mutation_operators)`` per step.

    Observation space:
        ``Box(shape=(8,))`` —
            [step, mutations_used, elite_m, median_m, worst_m,
             best_m_overall, prev_elite_m, episode_done_flag]

    Episode:
        ``n_mutations_per_episode`` mutation steps; final step triggers
        elite extraction, catalog cross-check + battery for sub-Lehmer
        candidates, reward computation.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        degree: int = 10,
        population_size: int = 16,
        n_mutations_per_episode: Optional[int] = None,
        mutation_rate: float = 1.0,
        seed_with_known: bool = False,
        kernel_db_path: str = ":memory:",
        cost_seconds: float = 0.5,
        seed: Optional[int] = None,
        coefficient_choices: Optional[Tuple[int, ...]] = None,
        enable_pipeline: bool = True,
        selection_strategy: str = "elitist",
        novelty_weight: float = 1.0,
        collapse_threshold: float = 1e-3,
        collapse_window: int = 5,
    ):
        if degree < 2:
            raise ValueError(f"degree must be >= 2; got {degree}")
        if population_size < 1:
            raise ValueError(f"population_size must be >= 1; got {population_size}")
        if mutation_rate < 0.0:
            raise ValueError(f"mutation_rate must be >= 0; got {mutation_rate}")
        if mutation_rate > 1.0:
            raise ValueError(
                f"mutation_rate must be in [0, 1]; got {mutation_rate} (use clip-to-1 upstream if needed)"
            )
        if selection_strategy not in SELECTION_STRATEGIES:
            raise ValueError(
                f"selection_strategy must be one of {SELECTION_STRATEGIES}; "
                f"got {selection_strategy!r}"
            )
        if novelty_weight < 0.0:
            raise ValueError(f"novelty_weight must be >= 0; got {novelty_weight}")
        if collapse_window < 1:
            raise ValueError(
                f"collapse_window must be >= 1; got {collapse_window}"
            )

        self.degree = int(degree)
        self.half_len = (self.degree // 2) + 1
        self.population_size = int(population_size)
        self.mutation_rate = float(mutation_rate)
        if n_mutations_per_episode is None:
            n_mutations_per_episode = self.population_size * 2
        if n_mutations_per_episode < 1:
            raise ValueError(
                f"n_mutations_per_episode must be >= 1; got {n_mutations_per_episode}"
            )
        self.n_mutations_per_episode = int(n_mutations_per_episode)
        self.seed_with_known = bool(seed_with_known)
        self.kernel_db_path = str(kernel_db_path)
        self.cost_seconds = float(cost_seconds)
        self.seed = seed
        self._enable_pipeline = bool(enable_pipeline)

        if coefficient_choices is None:
            self.coefficient_choices: Tuple[int, ...] = COEFFICIENT_CHOICES_V2
        else:
            cc = tuple(int(c) for c in coefficient_choices)
            if len(cc) == 0:
                raise ValueError("coefficient_choices must be non-empty")
            if len(set(cc)) != len(cc):
                raise ValueError(f"coefficient_choices must be unique; got {cc}")
            self.coefficient_choices = cc

        # Selection strategy state.
        self.selection_strategy = str(selection_strategy)
        self.novelty_weight = float(novelty_weight)
        self.collapse_threshold = float(collapse_threshold)
        self.collapse_window = int(collapse_window)
        self._collapse_streak: int = 0
        self._restart_count: int = 0
        self._strategy_event_log: List[Dict[str, Any]] = []

        # Operator menu is fixed (module-level); referenced by index.
        self.n_actions = N_MUTATION_OPERATORS
        self._operators: Tuple[Tuple[str, MutationOp], ...] = MUTATION_OPERATORS

        # Substrate handles (lazy-init).
        self._kernel: Optional[SigmaKernel] = None
        self._ext: Optional[BindEvalExtension] = None
        self._mm_binding_name: Optional[str] = None
        self._mm_binding_version: Optional[int] = None
        self._pipeline = None  # type: ignore  # forward-ref to DiscoveryPipeline
        self._pipeline_records: List[Any] = []

        # Population state.
        self._population: List[PopulationMember] = []
        self._rng: Optional[np.random.Generator] = None
        self._step_count = 0
        self._mutations_used = 0
        self._episode_count = 0
        self._best_m_overall: float = float("inf")
        self._prev_elite_m: float = float("inf")
        self._discoveries: List[EpisodeRecordV2] = []
        self._sub_lehmer_candidates: List[EpisodeRecordV2] = []
        self._n_evals = 0
        self._operator_call_counts: Dict[str, int] = {
            name: 0 for name, _ in self._operators
        }

        # Spaces (Gymnasium if available, stubs otherwise).
        try:
            import gymnasium as gym  # noqa: F401
            from gymnasium import spaces

            self.observation_space = spaces.Box(
                low=-1e9,
                high=1e9,
                shape=(8,),
                dtype=np.float64,
            )
            self.action_space = spaces.Discrete(self.n_actions)
            self._gym_spaces = spaces
        except ImportError:
            from .sigma_env import _BoxStub, _DiscreteStub  # local fallback

            self.observation_space = _BoxStub((8,))
            self.action_space = _DiscreteStub(self.n_actions)
            self._gym_spaces = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def reset(
        self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Re-seed (if seed provided), rebuild population, eval all M's."""
        if seed is not None:
            self.seed = int(seed)
        self._rng = np.random.default_rng(self.seed)

        # Lazy-init kernel + binding (only on first reset of this env).
        if self._kernel is None:
            self._kernel = SigmaKernel(self.kernel_db_path)
            self._ext = BindEvalExtension(self._kernel)
            cap = self._kernel.mint_capability("BindCap")
            binding = self._ext.BIND(
                callable_ref="techne.lib.mahler_measure:mahler_measure",
                cost_model=CostModel(max_seconds=self.cost_seconds),
                postconditions=["M(P) >= 1 for any non-zero integer poly"],
                authority_refs=["Mossinghoff Mahler tables", "Lehmer 1933"],
                cap=cap,
            )
            self._mm_binding_name = binding.symbol.name
            self._mm_binding_version = binding.symbol.version

        # Build a fresh population for this episode.
        # On every reset() we rebuild from scratch — episodes are
        # independent populations so the random-vs-REINFORCE comparison
        # is at the population-search-trajectory level.
        self._population = _initial_population(
            self.population_size,
            self.half_len,
            self.coefficient_choices,
            self._rng,
            self.seed_with_known,
            self.degree,
        )
        # Evaluate all members up front (one EVAL each).
        for m in self._population:
            m.m_value = self._evaluate_m(m)
        self._sort_population()

        # Track previous elite for the improvement-bonus computation.
        # First episode: no previous elite, leave inf.
        self._prev_elite_m = (
            self._population[0].m_value if self._episode_count > 0 else float("inf")
        )

        self._step_count = 0
        self._mutations_used = 0

        info = {
            "episode": self._episode_count,
            "degree": self.degree,
            "population_size": self.population_size,
            "n_mutations_per_episode": self.n_mutations_per_episode,
            "n_actions": self.n_actions,
            "operator_names": [name for name, _ in self._operators],
            "elite_m_initial": self._population[0].m_value,
        }
        return self._obs(), info

    def step(
        self, action: int
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        if self._kernel is None or self._ext is None or self._rng is None:
            raise RuntimeError("env.step() called before env.reset()")
        if action < 0 or action >= self.n_actions:
            raise ValueError(f"action {action} out of [0, {self.n_actions})")

        op_name, op_fn = self._operators[action]
        self._operator_call_counts[op_name] = (
            self._operator_call_counts.get(op_name, 0) + 1
        )
        self._step_count += 1

        info: Dict[str, Any] = {
            "step": self._step_count,
            "operator": op_name,
        }

        # Apply the mutation if mutation_rate triggers.  mutation_rate=0
        # → never mutate (population stays put; reward = 0 except band
        # bonus if a seeded member was already sub-Lehmer).
        if self._rng.random() < self.mutation_rate and op_name != "identity":
            # Pick a random parent.  Mutate.  Evaluate child.  Apply the
            # configured selection strategy.
            if not self._population:
                # Defensive: empty population — re-seed with one random
                # member so the env can keep running.  This is the
                # "catastrophic event" edge case.
                seed_half = [
                    int(self.coefficient_choices[
                        int(self._rng.integers(0, len(self.coefficient_choices)))
                    ])
                    for _ in range(self.half_len)
                ]
                seeded = PopulationMember(half=seed_half)
                seeded.m_value = self._evaluate_m(seeded)
                self._population.append(seeded)
                info["empty_population_reseeded"] = True
            parent_idx = int(self._rng.integers(0, len(self._population)))
            parent = self._population[parent_idx]
            child_half = op_fn(parent.half, self._rng, self.coefficient_choices)
            child = PopulationMember(half=child_half)
            child.m_value = self._evaluate_m(child)
            strat_info = self._maybe_replace_worst(child)
            self._sort_population()
            info["mutated"] = True
            info["child_m"] = child.m_value
            info["strategy_info"] = strat_info
        else:
            info["mutated"] = False

        self._mutations_used += 1
        if self._mutations_used < self.n_mutations_per_episode:
            return self._obs(), 0.0, False, False, info

        # Episode complete — extract elite, route through pipeline if
        # sub-Lehmer, compute reward, log.
        elite = self._population[0]
        elite_full = elite.full(self.degree)
        elite_m = elite.m_value
        is_sub_lehmer = (
            math.isfinite(elite_m)
            and 1.001 < elite_m < 1.18
            and not all(c == 0 for c in elite_full)
        )

        is_signal_class = False
        pipeline_terminal: Optional[str] = None
        pipeline_kill: Optional[str] = None
        if is_sub_lehmer and self._enable_pipeline:
            try:
                from .discovery_pipeline import DiscoveryPipeline

                if self._pipeline is None:
                    self._pipeline = DiscoveryPipeline(
                        kernel=self._kernel, ext=self._ext
                    )
                rec = self._pipeline.process_candidate(elite_full, elite_m)
                self._pipeline_records.append(rec)
                pipeline_terminal = rec.terminal_state
                pipeline_kill = rec.kill_pattern
                is_signal_class = rec.is_signal_class
            except Exception as e:  # pragma: no cover - defensive
                pipeline_terminal = f"pipeline_error:{type(e).__name__}"

        reward, reward_label = _compute_reward_v2(
            elite_m=elite_m,
            prev_elite_m=self._prev_elite_m,
            is_sub_lehmer=is_sub_lehmer,
            is_signal_class=is_signal_class,
        )

        if math.isfinite(elite_m) and elite_m < self._best_m_overall:
            self._best_m_overall = elite_m

        # Population summary.
        ms = [m.m_value for m in self._population if math.isfinite(m.m_value)]
        if ms:
            ms_sorted = sorted(ms)
            pop_summary = (
                ms_sorted[0],
                ms_sorted[len(ms_sorted) // 2],
                ms_sorted[-1],
            )
        else:
            pop_summary = (float("inf"), float("inf"), float("inf"))

        record = EpisodeRecordV2(
            elite_coeffs=elite_full,
            elite_m=elite_m,
            reward=float(reward),
            reward_label=reward_label,
            n_mutations=self._mutations_used,
            population_m_summary=pop_summary,
            is_signal_class=is_signal_class,
            pipeline_terminal_state=pipeline_terminal,
            pipeline_kill_pattern=pipeline_kill,
        )
        self._discoveries.append(record)
        if is_sub_lehmer and not is_signal_class:
            # Sub-Lehmer but battery-killed → still worth logging for
            # diagnosis (which battery member fired).
            self._sub_lehmer_candidates.append(record)
        if is_signal_class:
            self._sub_lehmer_candidates.append(record)

        info.update(
            {
                "elite_coeffs": elite_full,
                "elite_m": elite_m,
                "is_sub_lehmer": is_sub_lehmer,
                "is_signal_class": is_signal_class,
                "pipeline_terminal_state": pipeline_terminal,
                "pipeline_kill_pattern": pipeline_kill,
                "reward_label": reward_label,
                "best_m_overall": self._best_m_overall,
                "population_m_summary": pop_summary,
                "operator_call_counts": dict(self._operator_call_counts),
            }
        )
        self._prev_elite_m = elite_m
        self._episode_count += 1
        return self._obs(), float(reward), True, False, info

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _evaluate_m(self, member: PopulationMember) -> float:
        """EVAL the Mahler measure of a member through the substrate."""
        if self._kernel is None or self._ext is None:
            raise RuntimeError("env not reset; cannot eval")
        full = member.full(self.degree)
        if all(c == 0 for c in full):
            return float("inf")
        cap = self._kernel.mint_capability("EvalCap")
        try:
            ev = self._ext.EVAL(
                binding_name=self._mm_binding_name,
                binding_version=self._mm_binding_version,
                args=[full],
                cap=cap,
                eval_version=self._n_evals + 1,
            )
            self._n_evals += 1
        except BudgetExceeded:
            return float("inf")
        if not ev.success:
            return float("inf")
        try:
            return float(ev.output_repr)
        except (TypeError, ValueError):
            return float("inf")

    def _maybe_replace_worst(self, child: PopulationMember) -> Dict[str, Any]:
        """Strategy-dispatched replacement.  Returns a per-step diagnostic
        dict (always populated) so callers can inspect the decision."""
        strat = self.selection_strategy
        if strat == "elitist":
            return self._select_elitist(child)
        if strat == "tournament_novelty":
            return self._select_tournament_novelty(child)
        if strat == "crowding":
            return self._select_crowding(child)
        if strat == "restart_collapse":
            return self._select_restart_collapse(child)
        # Defensive — constructor validated; reraising would be more
        # informative than silently falling back.
        raise RuntimeError(
            f"unknown selection_strategy at runtime: {strat!r}"
        )

    # ------------------------------------------------------------------
    # Strategy implementations
    # ------------------------------------------------------------------

    def _select_elitist(self, child: PopulationMember) -> Dict[str, Any]:
        """Original V2 rule: child displaces worst iff child.M < worst.M."""
        if not self._population:
            self._population.append(child)
            return {"strategy": "elitist", "replaced": True, "reason": "empty_pop"}
        worst = self._population[-1]
        if math.isfinite(child.m_value) and child.m_value < worst.m_value:
            self._population[-1] = child
            return {
                "strategy": "elitist",
                "replaced": True,
                "reason": "child_better_than_worst",
            }
        return {
            "strategy": "elitist",
            "replaced": False,
            "reason": "child_not_better",
        }

    def _select_tournament_novelty(
        self, child: PopulationMember
    ) -> Dict[str, Any]:
        """Tournament-with-novelty: child displaces a random tournament-loser
        iff its (negative-fitness + novelty * weight) score exceeds the
        loser's score.

        Composite score = -M + novelty_weight * dist_to_centroid.
        Higher is better.  This rewards both good fitness AND distance
        from the population centroid in coefficient space — a partial
        antidote to the elitist cyclotomic basin (cyclotomic members
        cluster tightly so their novelty term is small)."""
        if not self._population:
            self._population.append(child)
            return {
                "strategy": "tournament_novelty",
                "replaced": True,
                "reason": "empty_pop",
            }
        if not math.isfinite(child.m_value):
            return {
                "strategy": "tournament_novelty",
                "replaced": False,
                "reason": "child_non_finite",
            }
        centroid = _half_centroid(self._population)
        # Run a 3-way tournament for the *replacement target*; pick the
        # worst-scoring of the three.  This is the diversity-preserving
        # half of the rule (we don't always evict the M-worst).
        n = len(self._population)
        k = min(3, n)
        idxs = self._rng.choice(n, size=k, replace=False).tolist()
        scores = []
        for i in idxs:
            mem = self._population[int(i)]
            d = _half_distance_to_centroid(mem.half, centroid)
            m = mem.m_value if math.isfinite(mem.m_value) else 1e9
            scores.append(-m + self.novelty_weight * d)
        loser_local = int(np.argmin(scores))
        loser_idx = int(idxs[loser_local])
        loser = self._population[loser_idx]
        loser_score = scores[loser_local]
        child_d = _half_distance_to_centroid(child.half, centroid)
        child_score = -child.m_value + self.novelty_weight * child_d
        if child_score > loser_score:
            self._population[loser_idx] = child
            return {
                "strategy": "tournament_novelty",
                "replaced": True,
                "reason": "child_score_higher",
                "child_score": float(child_score),
                "loser_score": float(loser_score),
                "loser_idx": loser_idx,
                "child_dist": float(child_d),
            }
        return {
            "strategy": "tournament_novelty",
            "replaced": False,
            "reason": "child_score_lower",
            "child_score": float(child_score),
            "loser_score": float(loser_score),
            "loser_idx": loser_idx,
        }

    def _select_crowding(self, child: PopulationMember) -> Dict[str, Any]:
        """NSGA-II-style crowding-distance penalty.

        For each member, compute crowding distance in the (M, novelty)
        2D objective space (sum of normalized neighbour-gap distances
        per objective).  Members in dense regions have small crowding
        distance.  Replacement target = member with the smallest
        crowding distance (the "most crowded").  Child accepts the
        slot iff its M is finite and strictly less than the target's M
        OR its novelty exceeds the target's novelty (preserves
        Pareto-frontier additions)."""
        if not self._population:
            self._population.append(child)
            return {
                "strategy": "crowding",
                "replaced": True,
                "reason": "empty_pop",
            }
        if not math.isfinite(child.m_value):
            return {
                "strategy": "crowding",
                "replaced": False,
                "reason": "child_non_finite",
            }
        n = len(self._population)
        if n == 1:
            # Trivial; defer to elitist semantics.
            return self._select_elitist(child)
        centroid = _half_centroid(self._population)
        ms = np.asarray(
            [
                m.m_value if math.isfinite(m.m_value) else 1e9
                for m in self._population
            ],
            dtype=np.float64,
        )
        ds = np.asarray(
            [_half_distance_to_centroid(m.half, centroid) for m in self._population],
            dtype=np.float64,
        )
        # Per-objective crowding distance: sum over objectives of
        # neighbour-gap normalized by objective range.
        def _crowding(values: np.ndarray) -> np.ndarray:
            order = np.argsort(values)
            cd = np.zeros_like(values)
            rng_v = float(values[order[-1]] - values[order[0]])
            if rng_v <= 0.0:
                return cd
            cd[order[0]] = float("inf")
            cd[order[-1]] = float("inf")
            for k in range(1, len(values) - 1):
                cd[order[k]] = (
                    float(values[order[k + 1]] - values[order[k - 1]]) / rng_v
                )
            return cd

        cd_total = _crowding(ms) + _crowding(ds)
        target_idx = int(np.argmin(cd_total))
        target = self._population[target_idx]
        # Acceptance: child improves M OR novelty over the target.
        child_d = _half_distance_to_centroid(child.half, centroid)
        improves_m = child.m_value < target.m_value - 1e-12
        improves_d = child_d > ds[target_idx] + 1e-12
        if improves_m or improves_d:
            self._population[target_idx] = child
            return {
                "strategy": "crowding",
                "replaced": True,
                "reason": "improves_m_or_d",
                "target_idx": target_idx,
                "improves_m": bool(improves_m),
                "improves_d": bool(improves_d),
                "child_dist": float(child_d),
            }
        return {
            "strategy": "crowding",
            "replaced": False,
            "reason": "no_improvement",
            "target_idx": target_idx,
        }

    def _select_restart_collapse(
        self, child: PopulationMember
    ) -> Dict[str, Any]:
        """Vanilla elitist replacement, plus a collapse detector that
        reinitializes half the population if M-variance has been below
        ``collapse_threshold`` for ``collapse_window`` consecutive steps."""
        info = self._select_elitist(child)
        # Update collapse streak based on current variance.
        var = _population_m_variance(self._population)
        if math.isfinite(var) and var < self.collapse_threshold:
            self._collapse_streak += 1
        else:
            self._collapse_streak = 0
        info["m_variance"] = float(var) if math.isfinite(var) else None
        info["collapse_streak"] = int(self._collapse_streak)
        if self._collapse_streak >= self.collapse_window:
            self._trigger_restart_half()
            info["restart_triggered"] = True
            info["restart_count"] = self._restart_count
            self._collapse_streak = 0
        else:
            info["restart_triggered"] = False
        info["strategy"] = "restart_collapse"
        return info

    def _trigger_restart_half(self) -> None:
        """Randomly reinitialize half the population (rounded down).
        The elite half is preserved (population is sorted ascending by
        M), so the best polys we've found are kept while the bottom
        half gets reseeded."""
        if self._rng is None or not self._population:
            return
        n = len(self._population)
        k = max(1, n // 2)
        # Sort first so we keep the elite half.
        self._sort_population()
        for j in range(n - k, n):
            new_half = [
                int(self.coefficient_choices[
                    int(self._rng.integers(0, len(self.coefficient_choices)))
                ])
                for _ in range(self.half_len)
            ]
            new_member = PopulationMember(half=new_half)
            new_member.m_value = self._evaluate_m(new_member)
            self._population[j] = new_member
        self._restart_count += 1
        self._strategy_event_log.append(
            {
                "event": "restart_half",
                "step": self._step_count,
                "restart_count": self._restart_count,
                "members_replaced": k,
            }
        )

    def _sort_population(self) -> None:
        """Keep population sorted ascending by M (population[0] = elite)."""
        self._population.sort(key=lambda m: m.m_value)

    # ------------------------------------------------------------------
    # Observation
    # ------------------------------------------------------------------

    def _obs(self) -> np.ndarray:
        if not self._population:
            elite_m = -1.0
            median_m = -1.0
            worst_m = -1.0
        else:
            ms = [m.m_value for m in self._population if math.isfinite(m.m_value)]
            if ms:
                ms_sorted = sorted(ms)
                elite_m = ms_sorted[0]
                median_m = ms_sorted[len(ms_sorted) // 2]
                worst_m = ms_sorted[-1]
            else:
                elite_m = -1.0
                median_m = -1.0
                worst_m = -1.0
        best_overall = (
            self._best_m_overall if math.isfinite(self._best_m_overall) else -1.0
        )
        prev_elite = (
            self._prev_elite_m if math.isfinite(self._prev_elite_m) else -1.0
        )
        episode_done_flag = (
            1.0 if self._mutations_used >= self.n_mutations_per_episode else 0.0
        )
        return np.array(
            [
                float(self._step_count),
                float(self._mutations_used),
                float(elite_m),
                float(median_m),
                float(worst_m),
                float(best_overall),
                float(prev_elite),
                float(episode_done_flag),
            ],
            dtype=np.float64,
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def discoveries(self) -> List[EpisodeRecordV2]:
        return list(self._discoveries)

    def sub_lehmer_candidates(self) -> List[EpisodeRecordV2]:
        return list(self._sub_lehmer_candidates)

    def pipeline_records(self) -> List[Any]:
        return list(self._pipeline_records)

    def population_snapshot(self) -> List[Tuple[List[int], float]]:
        """Return a copy of the current population as (half, M) tuples."""
        return [(list(m.half), float(m.m_value)) for m in self._population]

    def best_m_overall(self) -> float:
        return float(self._best_m_overall)

    def operator_call_counts(self) -> Dict[str, int]:
        return dict(self._operator_call_counts)

    def population_diversity(self) -> Dict[str, float]:
        """Diagnostic: variance of M values + mean pairwise half-vector
        distance + cyclotomic fraction.  Used by the anti-elitist
        comparison harness to monitor mode-collapse."""
        if not self._population:
            return {
                "m_variance": float("inf"),
                "mean_pairwise_dist": 0.0,
                "cyclotomic_fraction": 0.0,
                "n_members": 0,
            }
        ms = [m.m_value for m in self._population if math.isfinite(m.m_value)]
        m_var = float(np.var(ms)) if len(ms) >= 2 else float("inf")
        # Mean pairwise distance in half-coefficient space.
        halves = np.asarray(
            [m.half for m in self._population], dtype=np.float64
        )
        n = len(halves)
        if n >= 2:
            d = 0.0
            cnt = 0
            for i in range(n):
                for j in range(i + 1, n):
                    d += float(np.linalg.norm(halves[i] - halves[j]))
                    cnt += 1
            mean_d = d / cnt if cnt else 0.0
        else:
            mean_d = 0.0
        # Cyclotomic fraction: members with M = 1.0 ± 1e-9.
        cyclo = sum(
            1
            for m in self._population
            if math.isfinite(m.m_value) and abs(m.m_value - 1.0) < 1e-9
        )
        return {
            "m_variance": float(m_var) if math.isfinite(m_var) else float("inf"),
            "mean_pairwise_dist": float(mean_d),
            "cyclotomic_fraction": float(cyclo) / float(n),
            "n_members": int(n),
        }

    def restart_count(self) -> int:
        """How many times restart-on-collapse fired in this env's lifetime."""
        return int(self._restart_count)

    def strategy_event_log(self) -> List[Dict[str, Any]]:
        """Copy of the strategy event log (restart events, etc.)."""
        return list(self._strategy_event_log)

    def kernel(self) -> SigmaKernel:
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


__all__ = [
    "DiscoveryEnvV2",
    "EpisodeRecordV2",
    "PopulationMember",
    "MUTATION_OPERATORS",
    "N_MUTATION_OPERATORS",
    "COEFFICIENT_CHOICES_V2",
    "SELECTION_STRATEGIES",
    "KNOWN_SEEDS_DEG10",
    "LEHMER_HALF",
    "_palindromic_from_half",
    "_is_reciprocal",
    "_compute_reward_v2",
    "_mutate_single_coef",
    "_mutate_two_coefs",
    "_swap_palindromic_pairs",
    "_increment_at_index",
    "_decrement_at_index",
    "_zero_at_index",
    "_identity",
    "_half_centroid",
    "_half_distance_to_centroid",
    "_population_m_variance",
]
