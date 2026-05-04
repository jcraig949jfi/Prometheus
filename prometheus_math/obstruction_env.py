"""prometheus_math.obstruction_env — predicate-discovery RL env.

The second discovery env (sequel to ``DiscoveryEnv``). Where
``DiscoveryEnv`` rediscovers the known Salem cluster on the Lehmer-
Mahler problem, this env asks the inverse question:

  Can an RL agent learn to PROPOSE structural-signature predicates
  whose held-out predictive lift on a synthetic OEIS-shaped battery
  exceeds the random baseline by a discovery-grade margin?

The env's ground truth is documented in
``prometheus_math._obstruction_corpus``: 150 synthetic records with
two signatures planted as deterministic-kill predicates. The RL
agent's job is to find them via the lift signal alone.

Key design points (mirroring the DiscoveryEnv pattern that worked):

1. Combinatorial action space, not bandit. Each step picks one
   ``(feature, value)`` conjunct; episodes accumulate up to
   ``max_predicate_complexity`` conjuncts. STOP terminates early.
2. Continuous reward signal. Per ``DISCOVERY_RESULTS.md``, step rewards
   trap REINFORCE in local optima; the working pattern is a single
   terminal lift score plus tagged bonuses on the matching-pattern.
3. Train/test split. The agent's terminal reward is HELD-OUT lift, so
   over-fitting to in-sample noise pays nothing; this is the
   selection-bias guard.
4. Substrate-conditioned obs. The observation exposes the partial
   predicate (one-hot over actions), step count, current in-sample
   lift estimate, and substrate eval count.
5. BIND/EVAL through the kernel. Every predicate evaluation goes
   through ``BindEvalExtension.EVAL`` so the substrate sees a fresh
   evaluation symbol per terminal step. Same architecture as
   ``DiscoveryEnv``.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import numpy as np

from sigma_kernel.sigma_kernel import SigmaKernel
from sigma_kernel.bind_eval import (
    BudgetExceeded,
    CostModel,
)
from sigma_kernel.bind_eval_v2 import BindEvalKernelV2

from ._obstruction_corpus import (
    CorpusEntry,
    OBSTRUCTION_CORPUS,
    OBSTRUCTION_SIGNATURE,
    SECONDARY_SIGNATURE,
)


CorpusSource = Literal["synthetic", "live"]


def _load_live_corpus_as_corpus_entries() -> List["CorpusEntry"]:
    """Adapter: load the live corpus and return entries that quack like
    synthetic ``CorpusEntry``.

    The env's evaluate_predicate / _predicate_matches paths only need
    ``.features()``, ``.kill_verdict``, and ``.to_dict()`` — all of
    which ``LiveCorpusEntry`` provides. We therefore return the live
    objects directly and rely on duck typing; the ``sequence_id``
    field tags along, used by ``ObstructionEnv.discoveries()`` for
    OEIS-grade evidence reporting.

    Raises FileNotFoundError if the live data isn't reachable; caller
    decides whether to fall back to synthetic.
    """
    from ._obstruction_corpus_live import load_live_corpus

    return load_live_corpus()  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Action space
# ---------------------------------------------------------------------------


# Numeric features and their value range.
NUMERIC_FEATURE_VALUES: Tuple[int, ...] = tuple(range(8))  # 0..7

NUMERIC_FEATURES: Tuple[str, ...] = (
    "n_steps",
    "neg_x",
    "pos_x",
    "neg_y",
    "pos_y",
    "neg_z",
    "pos_z",
)

BOOL_FEATURES: Tuple[str, ...] = ("has_diag_neg", "has_diag_pos")

FEATURES: Tuple[str, ...] = NUMERIC_FEATURES + BOOL_FEATURES


def _build_action_table() -> List[Tuple[str, Any]]:
    """Build the canonical (feature, value) table.

    Action layout:
      [0..7]    n_steps in {0..7}
      [8..15]   neg_x in {0..7}
      ...
      [56..57]  has_diag_neg in {False, True}
      [58..59]  has_diag_pos in {False, True}
      [60]      STOP
    """
    table: List[Tuple[str, Any]] = []
    for feat in NUMERIC_FEATURES:
        for v in NUMERIC_FEATURE_VALUES:
            table.append((feat, int(v)))
    for feat in BOOL_FEATURES:
        for v in (False, True):
            table.append((feat, bool(v)))
    return table


_ACTION_TABLE: List[Tuple[str, Any]] = _build_action_table()
_ACTION_INDEX: Dict[Tuple[str, Any], int] = {
    (f, v): i for i, (f, v) in enumerate(_ACTION_TABLE)
}

# STOP is the last index.
N_CONJUNCT_ACTIONS: int = len(_ACTION_TABLE)
STOP_ACTION: int = N_CONJUNCT_ACTIONS  # one past the last conjunct action
N_ACTIONS: int = N_CONJUNCT_ACTIONS + 1  # conjuncts + STOP


def encode_action(feature: str, value: Any) -> int:
    """Return the action index for a ``(feature, value)`` pair.

    Raises KeyError if the pair is not in the action table.
    """
    return _ACTION_INDEX[(feature, value)]


def decode_action(action: int) -> Tuple[str, Any]:
    """Return the ``(feature, value)`` pair for an action index.

    Raises ValueError on STOP (which has no conjunct meaning) or
    out-of-range indices.
    """
    if action == STOP_ACTION:
        raise ValueError("STOP action has no (feature, value)")
    if action < 0 or action >= N_CONJUNCT_ACTIONS:
        raise ValueError(f"action {action} out of [0, {N_CONJUNCT_ACTIONS})")
    return _ACTION_TABLE[action]


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------


REDISCOVERED_OBSTRUCTION_SHAPE_TAG = "REDISCOVERED_OBSTRUCTION_SHAPE"
REDISCOVERED_SECONDARY_TAG = "REDISCOVERED_SECONDARY"


# ---------------------------------------------------------------------------
# Episode record
# ---------------------------------------------------------------------------


@dataclass
class ObstructionEpisodeRecord:
    """A complete episode's outcome, suitable for downstream auditing.

    When ``corpus_source == "live"`` and the env tags a rediscovery,
    ``match_sequence_ids`` is populated with the OEIS A-numbers in the
    match group (substrate-grade evidence — these are the actual
    sequences the predicate captured).
    """

    predicate: Dict[str, Any]
    in_sample_lift: float
    held_out_lift: float
    match_group_size_train: int
    match_group_size_test: int
    reward: float
    tags: List[str] = field(default_factory=list)
    terminated_via: str = "max_complexity"
    match_sequence_ids: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Predicate evaluation (the substrate-bindable callable)
# ---------------------------------------------------------------------------


def _predicate_matches(entry: CorpusEntry, predicate: Dict[str, Any]) -> bool:
    """Conjunctive AND match: every key in predicate must equal the
    feature value on the entry. Empty predicate matches everything."""
    if not predicate:
        return True
    feats = entry.features()
    for k, v in predicate.items():
        if feats.get(k) != v:
            return False
    return True


def evaluate_predicate(
    predicate: Dict[str, Any],
    corpus: List[CorpusEntry],
) -> Dict[str, Any]:
    """Evaluate a predicate's predictive lift on a corpus slice.

    The lift convention here is the Charon ratio (mirrors
    ``sigma_kernel/a149_obstruction.py``):

        lift = matched_kill_rate / baseline_kill_rate

    where ``baseline_kill_rate`` is the kill rate of records that do
    NOT match the predicate. This is the right denominator: with an
    all-records baseline, lift is upper-bounded by 1/baseline, which
    crushes the signal as the match group grows.

    Returns a dict with:
      - match_group_size: # of records matching the predicate
      - nonmatch_group_size: # of records NOT matching
      - matched_kill_rate: fraction of match-group with kill_verdict=True
      - baseline_kill_rate: fraction of non-match group with
        kill_verdict=True
      - lift: ratio matched_rate / baseline_rate (1.0 = no signal,
        > 1 = predicate is enriched, < 1 = predicate is depleted; 0 if
        match-group empty)
      - lift_excess: max(0, lift - 1.0) — the reward-shaped excess
        above null-hypothesis; this is what the env's reward uses
        (matches the spec's `(matched - baseline)/baseline` form when
        baseline > 0)
      - n_corpus: total corpus size used

    Edge cases:
      - Empty match-group → lift=0, lift_excess=0.
      - Empty non-match group (predicate matches all records, e.g.
        empty predicate {}) → matched_rate equals the corpus kill rate;
        lift=1.0 by convention (no comparison group, no signal); same
        result for tautological predicate.
      - All-positive corpus (every kill_verdict=True) → matched=1,
        baseline=1, lift=1, lift_excess=0 (no signal).
    """
    n = len(corpus)
    matches = []
    nonmatches = []
    for e in corpus:
        if _predicate_matches(e, predicate):
            matches.append(e)
        else:
            nonmatches.append(e)
    n_match = len(matches)
    n_nonmatch = len(nonmatches)

    matched_kill_rate = (
        sum(1 for e in matches if e.kill_verdict) / n_match
        if n_match > 0 else 0.0
    )
    baseline_kill_rate = (
        sum(1 for e in nonmatches if e.kill_verdict) / n_nonmatch
        if n_nonmatch > 0 else 0.0
    )

    if n_match == 0:
        lift = 0.0
        lift_excess = 0.0
    elif n_nonmatch == 0:
        # Tautological match (e.g. empty predicate); no baseline group
        # to compare. By convention lift = 1.0 (null), excess = 0.
        lift = 1.0
        lift_excess = 0.0
    elif baseline_kill_rate <= 1e-9:
        # No kills among non-matches. If matched_rate > 0, lift is
        # technically infinite; cap it at a large finite value (e.g.
        # 1000) so the reward channel doesn't NaN. If matched_rate is
        # also 0, lift = 0 (no signal at all).
        if matched_kill_rate > 0:
            lift = matched_kill_rate / 1e-6  # implicit cap via 1e-6 floor
            lift_excess = max(0.0, lift - 1.0)
        else:
            lift = 0.0
            lift_excess = 0.0
    else:
        lift = matched_kill_rate / baseline_kill_rate
        lift_excess = max(0.0, lift - 1.0)

    return {
        "match_group_size": n_match,
        "nonmatch_group_size": n_nonmatch,
        "matched_kill_rate": matched_kill_rate,
        "baseline_kill_rate": baseline_kill_rate,
        "lift": lift,
        "lift_excess": lift_excess,
        "n_corpus": n,
    }


# ---------------------------------------------------------------------------
# The env
# ---------------------------------------------------------------------------


class ObstructionEnv:
    """Predicate-discovery env on a synthetic OEIS-shaped battery.

    Parameters
    ----------
    corpus : list[CorpusEntry], optional
        The dataset to discover predicates over. Defaults to the
        module-level OBSTRUCTION_CORPUS.
    held_out_fraction : float
        Fraction of records held out for terminal-reward computation
        (selection-bias guard). Must be strictly in (0, 1).
    max_predicate_complexity : int
        Maximum number of conjuncts in a predicate. Episode terminates
        on STOP or when this limit is reached.
    kernel_db_path : str
        SQLite path for the substrate (defaults to in-memory).
    seed : int, optional
        Seed for the train/test split AND any randomness in the env's
        observation broadcast.
    cost_seconds : float
        Per-EVAL budget for the predicate-evaluation callable.
    lift_cap : float
        Cap the lift component of the terminal reward. Default 50.0;
        prevents unbounded lift from dominating the bonus.
    obstruction_bonus : float
        Bonus added if the final predicate equals OBSTRUCTION_SIGNATURE.
    secondary_bonus : float
        Bonus added if the final predicate equals SECONDARY_SIGNATURE.
    log_discoveries : bool
        Whether to keep an in-memory list of rewarded episodes.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        corpus: Optional[List[CorpusEntry]] = None,
        held_out_fraction: float = 0.3,
        max_predicate_complexity: int = 3,
        kernel_db_path: str = ":memory:",
        seed: Optional[int] = None,
        cost_seconds: float = 1.0,
        lift_cap: float = 50.0,
        obstruction_bonus: float = 50.0,
        secondary_bonus: float = 20.0,
        log_discoveries: bool = True,
        corpus_source: CorpusSource = "synthetic",
    ):
        # Resolve corpus_source if no corpus explicitly provided.
        if corpus is None:
            if corpus_source == "live":
                # Load from Charon's data dir. Caller wanted live; if the
                # files aren't reachable, raise loud (don't silently fall
                # back to synthetic — that would mask the integration).
                corpus = _load_live_corpus_as_corpus_entries()
            elif corpus_source == "synthetic":
                corpus = OBSTRUCTION_CORPUS
            else:
                raise ValueError(
                    f"corpus_source must be 'synthetic' or 'live'; "
                    f"got {corpus_source!r}"
                )
        if not isinstance(corpus, list):
            corpus = list(corpus)
        if len(corpus) == 0:
            raise ValueError("corpus must be non-empty")
        self.corpus_source: CorpusSource = corpus_source
        if not (0.0 < held_out_fraction < 1.0):
            raise ValueError(
                f"held_out_fraction must be in (0, 1); got {held_out_fraction}"
            )
        if max_predicate_complexity < 0:
            raise ValueError(
                f"max_predicate_complexity must be >= 0; got {max_predicate_complexity}"
            )

        self.corpus = corpus
        self.held_out_fraction = float(held_out_fraction)
        self.max_predicate_complexity = int(max_predicate_complexity)
        self.kernel_db_path = str(kernel_db_path)
        self.seed = seed
        self.cost_seconds = float(cost_seconds)
        self.lift_cap = float(lift_cap)
        self.obstruction_bonus = float(obstruction_bonus)
        self.secondary_bonus = float(secondary_bonus)
        self.log_discoveries = bool(log_discoveries)

        # Train/test split (deterministic in seed).
        self._train_corpus, self._test_corpus = self._split(self.corpus, self.seed)

        # Substrate state — created lazily in reset().
        self._kernel: Optional[SigmaKernel] = None
        self._ext: Optional[BindEvalKernelV2] = None
        self._binding_name: Optional[str] = None
        self._binding_version: Optional[int] = None

        # Episode state.
        self._partial: Dict[str, Any] = {}
        self._step_count: int = 0
        self._n_evals_overall: int = 0
        self._discoveries: List[ObstructionEpisodeRecord] = []
        self._episode_count: int = 0
        self._last_reward: float = 0.0
        self._last_in_sample_lift: float = 0.0
        self._last_match_size_train: int = 0

        # Spaces.
        try:
            from gymnasium import spaces  # noqa: F401

            self.observation_space = spaces.Box(
                low=-1e9,
                high=1e9,
                shape=(self._obs_dim(),),
                dtype=np.float64,
            )
            self.action_space = spaces.Discrete(N_ACTIONS)
        except ImportError:
            from .sigma_env import _BoxStub, _DiscreteStub  # local fallback

            self.observation_space = _BoxStub((self._obs_dim(),))
            self.action_space = _DiscreteStub(N_ACTIONS)

    # ------------------------------------------------------------------
    # Train/test split
    # ------------------------------------------------------------------

    def _split(
        self,
        corpus: List[CorpusEntry],
        seed: Optional[int],
    ) -> Tuple[List[CorpusEntry], List[CorpusEntry]]:
        """Deterministic split based on seed."""
        rng = np.random.default_rng(seed if seed is not None else 0)
        n = len(corpus)
        idx = np.arange(n)
        rng.shuffle(idx)
        n_test = int(round(n * self.held_out_fraction))
        # Guarantee both sides non-empty when corpus has at least 2 records.
        if n_test == 0 and n >= 2:
            n_test = 1
        if n_test >= n:
            n_test = n - 1
        test_idx = set(int(i) for i in idx[:n_test])
        train: List[CorpusEntry] = []
        test: List[CorpusEntry] = []
        for i, e in enumerate(corpus):
            if i in test_idx:
                test.append(e)
            else:
                train.append(e)
        return train, test

    # ------------------------------------------------------------------
    # Observation
    # ------------------------------------------------------------------

    def _obs_dim(self) -> int:
        """Obs vector layout:
          [0..N_ACTIONS-1]   one-hot of conjuncts in current predicate
                             (last entry = whether STOP slot is set;
                             always 0 mid-episode)
          [N_ACTIONS]        step_count
          [N_ACTIONS+1]      in-sample lift estimate (current partial)
          [N_ACTIONS+2]      match-size train (current partial)
          [N_ACTIONS+3]      n_evals overall
          [N_ACTIONS+4]      max_predicate_complexity
        """
        return N_ACTIONS + 5

    def _obs(self) -> np.ndarray:
        v = np.zeros(self._obs_dim(), dtype=np.float64)
        # One-hot of current conjuncts in partial predicate.
        for feature, value in self._partial.items():
            try:
                idx = encode_action(feature, value)
                v[idx] = 1.0
            except KeyError:
                pass
        # Normalize all scalar features into roughly [0, 1] so the
        # linear policy doesn't get dominated by large lift values
        # (a 50x lift would otherwise produce a logit update 50x
        # larger than the one-hot indicator of partial predicate).
        v[N_ACTIONS] = (
            float(self._step_count)
            / max(self.max_predicate_complexity, 1)
        )
        v[N_ACTIONS + 1] = math.tanh(float(self._last_in_sample_lift) / 10.0)
        v[N_ACTIONS + 2] = math.tanh(float(self._last_match_size_train) / 10.0)
        v[N_ACTIONS + 3] = math.tanh(float(self._n_evals_overall) / 1000.0)
        v[N_ACTIONS + 4] = (
            float(self.max_predicate_complexity)
            / 10.0  # cap visualization at 10
        )
        return v

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        if seed is not None:
            self.seed = int(seed)
            self._train_corpus, self._test_corpus = self._split(self.corpus, self.seed)

        if self._kernel is None:
            self._kernel = SigmaKernel(self.kernel_db_path)
            self._ext = BindEvalKernelV2(self._kernel)
            cap = self._kernel.mint_capability("BindCap")
            binding = self._ext.BIND(
                callable_ref="prometheus_math.obstruction_env:_evaluate_predicate_pair",
                cost_model=CostModel(max_seconds=self.cost_seconds),
                postconditions=[
                    "lift >= 0",
                    "match_group_size >= 0",
                    "match_group_size <= len(corpus_train)",
                ],
                authority_refs=[
                    "OBSTRUCTION_SIGNATURE planted in _obstruction_corpus.py",
                    "Mirror of sigma_kernel/a149_obstruction.py",
                ],
                cap=cap,
            )
            self._binding_name = binding.symbol.name
            self._binding_version = binding.symbol.version

        self._partial = {}
        self._step_count = 0
        self._last_reward = 0.0
        self._last_in_sample_lift = 0.0
        self._last_match_size_train = 0

        info = {
            "episode": self._episode_count,
            "n_actions": N_ACTIONS,
            "stop_action": STOP_ACTION,
            "n_train": len(self._train_corpus),
            "n_test": len(self._test_corpus),
            "max_predicate_complexity": self.max_predicate_complexity,
        }
        return self._obs(), info

    def step(
        self,
        action: int,
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        if self._kernel is None or self._ext is None:
            raise RuntimeError("env.step() called before env.reset()")
        if action < 0 or action >= N_ACTIONS:
            raise ValueError(f"action {action} out of [0, {N_ACTIONS})")

        self._step_count += 1
        info: Dict[str, Any] = {
            "step": self._step_count,
            "action": int(action),
        }

        # STOP action — terminate immediately.
        if action == STOP_ACTION:
            info["terminated_via"] = "stop"
            return self._terminate(info)

        # Conjunct action.
        feature, value = decode_action(action)
        # Allow re-picks; later conjunct on same feature overrides earlier.
        self._partial[feature] = value
        info["chosen_conjunct"] = (feature, value)
        info["partial"] = dict(self._partial)

        # Update in-sample lift estimate (cheap; used for obs).
        try:
            in_sample = evaluate_predicate(self._partial, self._train_corpus)
            self._last_in_sample_lift = float(in_sample["lift"])
            self._last_match_size_train = int(in_sample["match_group_size"])
        except Exception:
            pass

        # Continue if we haven't hit max_predicate_complexity.
        if self._step_count < self.max_predicate_complexity:
            return self._obs(), 0.0, False, False, info

        info["terminated_via"] = "max_complexity"
        return self._terminate(info)

    # ------------------------------------------------------------------
    # Termination
    # ------------------------------------------------------------------

    def _terminate(
        self,
        info: Dict[str, Any],
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """Compute terminal reward by EVALing the predicate on test set."""
        predicate = dict(self._partial)
        # In-sample lift on train.
        in_sample = evaluate_predicate(predicate, self._train_corpus)

        # Held-out evaluation through the substrate (BIND/EVAL).
        held_out: Dict[str, Any]
        if self._kernel is not None and self._ext is not None:
            cap = self._kernel.mint_capability("EvalCap")
            try:
                ev = self._ext.EVAL(
                    binding_name=self._binding_name,
                    binding_version=self._binding_version,
                    args=[predicate, _corpus_to_list(self._test_corpus)],
                    cap=cap,
                    eval_version=self._n_evals_overall + 1,
                )
                self._n_evals_overall += 1
                if ev.success:
                    # Parse the dict back from repr().
                    try:
                        held_out = eval(ev.output_repr, {"__builtins__": {}}, {})
                        if not isinstance(held_out, dict):
                            held_out = evaluate_predicate(predicate, self._test_corpus)
                    except Exception:
                        held_out = evaluate_predicate(predicate, self._test_corpus)
                else:
                    held_out = evaluate_predicate(predicate, self._test_corpus)
            except BudgetExceeded:
                held_out = evaluate_predicate(predicate, self._test_corpus)
        else:
            held_out = evaluate_predicate(predicate, self._test_corpus)

        # Reward:
        #   - 0 if test match-group empty (no signal)
        #   - 0 if predicate is tautological (empty predicate or all-
        #     positive corpus, both yield lift_excess = 0)
        #   - else min(lift_excess, lift_cap) + bonuses on signature match
        held_out_lift = float(held_out.get("lift", 0.0))
        held_out_excess = float(held_out.get("lift_excess", 0.0))
        match_size_test = int(held_out.get("match_group_size", 0))
        match_size_train = int(in_sample.get("match_group_size", 0))
        in_sample_lift = float(in_sample.get("lift", 0.0))

        tags: List[str] = []
        reward = 0.0
        if match_size_test > 0 and len(predicate) > 0:
            reward = min(held_out_excess, self.lift_cap)

            # Signature rediscovery bonuses.
            #
            # We use a *tolerance-by-equivalence* match: a predicate is
            # tagged if it is exactly the planted signature, OR if its
            # train match-group equals the planted signature's match-
            # group (i.e. it's structurally equivalent on this corpus).
            # The latter catches parsimonious supersets/equivalents
            # the agent finds — over-specification is sometimes
            # redundant given the corpus and a good agent will
            # discover the minimal equivalent predicate.
            if self._is_signature_match(predicate, OBSTRUCTION_SIGNATURE):
                reward += self.obstruction_bonus
                tags.append(REDISCOVERED_OBSTRUCTION_SHAPE_TAG)
            if self._is_signature_match(predicate, SECONDARY_SIGNATURE):
                reward += self.secondary_bonus
                tags.append(REDISCOVERED_SECONDARY_TAG)

        # Empty predicate: lift is 0 by construction, reward is 0.
        # All-positive corpus: lift is 0 by construction, reward is 0.

        # Capture OEIS A-numbers in the match group when running on live
        # data. These are substrate-grade evidence: a tagged discovery on
        # live data names the actual sequences the predicate caught.
        match_sequence_ids: List[str] = []
        if predicate:
            for e in self._train_corpus + self._test_corpus:
                sid = getattr(e, "sequence_id", None)
                if sid is None:
                    continue
                if _predicate_matches(e, predicate):
                    match_sequence_ids.append(str(sid))

        record = ObstructionEpisodeRecord(
            predicate=predicate,
            in_sample_lift=in_sample_lift,
            held_out_lift=held_out_lift,
            match_group_size_train=match_size_train,
            match_group_size_test=match_size_test,
            reward=reward,
            tags=tags,
            terminated_via=info.get("terminated_via", "max_complexity"),
            match_sequence_ids=match_sequence_ids,
        )
        if self.log_discoveries and (reward > 0.0 or tags):
            self._discoveries.append(record)

        info.update(
            {
                "predicate": predicate,
                "match_group_size_test": match_size_test,
                "match_group_size_train": match_size_train,
                "in_sample_lift": in_sample_lift,
                "held_out_lift": held_out_lift,
                "tags": tags,
                "reward": reward,
                "match_group_size": match_size_test,  # alias
                "match_sequence_ids": match_sequence_ids,
                "corpus_source": self.corpus_source,
            }
        )

        self._last_reward = float(reward)
        self._episode_count += 1
        return self._obs(), float(reward), True, False, info

    # ------------------------------------------------------------------
    # Signature equivalence
    # ------------------------------------------------------------------

    def _is_signature_match(
        self,
        predicate: Dict[str, Any],
        signature: Dict[str, Any],
    ) -> bool:
        """Return True if ``predicate`` matches ``signature`` either
        exactly or by train-set match-group equivalence.

        This implements the spec's 'within tolerance' clause: a
        parsimonious predicate that filters the same training records
        as the planted signature is considered structurally equivalent.
        """
        if predicate == dict(signature):
            return True
        # Structural equivalence: identical train match-groups.
        # Only meaningful if both predicates have non-empty match-group;
        # the empty predicate matches everything and is never a
        # signature match.
        if not predicate:
            return False
        train_match_pred = frozenset(
            i for i, e in enumerate(self._train_corpus)
            if _predicate_matches(e, predicate)
        )
        train_match_sig = frozenset(
            i for i, e in enumerate(self._train_corpus)
            if _predicate_matches(e, signature)
        )
        if not train_match_sig:
            return False
        # Predicate must induce the same train match-group as signature
        # AND be implied by signature (signature ⇒ predicate; equivalently
        # signature's match-group ⊆ predicate's match-group). With
        # equality on match-groups, both directions hold.
        return train_match_pred == train_match_sig

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def discoveries(self) -> List[ObstructionEpisodeRecord]:
        """Return all rewarded / tagged episodes."""
        return list(self._discoveries)

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


# ---------------------------------------------------------------------------
# BIND-able helper
# ---------------------------------------------------------------------------


def _corpus_to_list(corpus: List[CorpusEntry]) -> List[Dict[str, Any]]:
    """Serialize corpus entries to dicts (for EVAL args_blob JSON-ability)."""
    return [e.to_dict() for e in corpus]


def _evaluate_predicate_pair(
    predicate: Dict[str, Any],
    corpus_serialized: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """BIND-able callable wrapper around evaluate_predicate.

    Accepts the corpus as a serialized list of dicts (EVAL needs JSON-
    serializable args). Reconstructs CorpusEntry-compatible objects
    (live entries get reconstructed as plain CorpusEntry — sequence_id
    is dropped since this path only needs features + kill_verdict for
    the lift computation), evaluates, returns a plain dict.
    """
    corpus = [
        CorpusEntry(
            n_steps=int(d["n_steps"]),
            neg_x=int(d["neg_x"]),
            pos_x=int(d["pos_x"]),
            neg_y=int(d["neg_y"]),
            pos_y=int(d["pos_y"]),
            neg_z=int(d["neg_z"]),
            pos_z=int(d["pos_z"]),
            has_diag_neg=bool(d["has_diag_neg"]),
            has_diag_pos=bool(d["has_diag_pos"]),
            kill_verdict=bool(d["kill_verdict"]),
        )
        for d in corpus_serialized
    ]
    return evaluate_predicate(predicate, corpus)


__all__ = [
    "ObstructionEnv",
    "ObstructionEpisodeRecord",
    "evaluate_predicate",
    "encode_action",
    "decode_action",
    "N_ACTIONS",
    "N_CONJUNCT_ACTIONS",
    "STOP_ACTION",
    "FEATURES",
    "NUMERIC_FEATURES",
    "BOOL_FEATURES",
    "NUMERIC_FEATURE_VALUES",
    "REDISCOVERED_OBSTRUCTION_SHAPE_TAG",
    "REDISCOVERED_SECONDARY_TAG",
]
