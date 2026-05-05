"""prometheus_math.withheld_benchmark — §6.2.5 of
``harmonia/memory/architecture/discovery_via_rediscovery.md``.

The withheld-rediscovery benchmark: stage-2 validation ladder before
the open-discovery pilot in §6.2.

How it works
------------
1. Take Mossinghoff's 178-entry snapshot.
2. Randomly partition: ~80% remain visible to the catalog-check; ~20%
   are withheld and treated as 'unknown' during evaluation.
3. Run the discovery agent (REINFORCE on DiscoveryEnv) with a
   ``WithheldDiscoveryPipeline`` whose catalog-check is monkey-patched
   on the **instance** to return ``catalog_miss=True`` for any
   polynomial whose Mahler measure matches a withheld entry within
   ``1e-5``. (Note: the patch is *instance-scoped*; the regular
   ``DiscoveryPipeline``'s module-level check is untouched.)
4. The env's own ``_check_mossinghoff`` is also temporarily patched
   for the duration of a pilot — otherwise the env classifies the
   withheld polynomial as ``known_salem`` and the pipeline never sees
   it. We restore the patch in a ``try/finally`` so concurrent
   ``DiscoveryEnv`` users are not affected after the pilot ends.
5. Measure:

   - ``withheld_rediscovery_count``: how many of the N withheld
     entries the agent's M-values matched at least once across all
     episodes, all seeds.
   - ``withheld_PROMOTE_count``: of those, how many had at least one
     pipeline ``DiscoveryRecord`` with ``terminal_state in
     {PROMOTED, SHADOW_CATALOG}``.

Why it matters
--------------
The withheld set provides a 'discovery-shaped' target where ground
truth is known. The rediscovery rate is a *calibration estimate* for
what stage-3's open-discovery pilot in §6.2 should produce as an
upper bound. If the agent rediscovers e.g. 1 of 36 withheld entries
in 1000 episodes, that's the rough ceiling for genuine open-discovery
in the same regime.

Honest framing: this is harder than it sounds. The agent has to
rediscover SPECIFIC polynomials whose M lands in a 1e-5 band, not
just any sub-Lehmer M-value. A low rediscovery rate is still
informative — it sets a realistic upper bound for §6.2.
"""
from __future__ import annotations

import math
import random
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from prometheus_math.discovery_pipeline import (
    DiscoveryPipeline,
    DiscoveryRecord,
)


# ---------------------------------------------------------------------------
# Partition
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WithheldPartition:
    """A 80/20-style split of the Mossinghoff snapshot.

    Each set is a list of ``(coeffs, mahler_measure)`` tuples (no
    references to the original dicts; the partition is a clean
    self-contained record).
    """

    visible_set: List[Tuple[List[int], float]]
    withheld_set: List[Tuple[List[int], float]]
    partition_seed: int
    n_visible: int
    n_withheld: int


def _load_default_corpus() -> List[Tuple[List[int], float]]:
    """Load the Mossinghoff snapshot as ``(coeffs, M)`` tuples."""
    from prometheus_math.databases.mahler import MAHLER_TABLE
    out: List[Tuple[List[int], float]] = []
    for entry in MAHLER_TABLE:
        coeffs = list(entry["coeffs"])
        m = float(entry["mahler_measure"])
        out.append((coeffs, m))
    return out


def partition_mossinghoff(
    holdout_fraction: float = 0.2,
    seed: int = 42,
    _corpus: Optional[List[Tuple[List[int], float]]] = None,
) -> WithheldPartition:
    """Randomly partition the Mossinghoff snapshot into visible + withheld.

    Parameters
    ----------
    holdout_fraction : float, default 0.2
        Fraction of entries to withhold. Must be in [0, 1).
        ``holdout_fraction=1.0`` is rejected because a zero-size visible
        catalog breaks the benchmark contract.
    seed : int, default 42
        Random seed for the partition. Same seed -> same partition.
    _corpus : list of (coeffs, M), optional
        Override the corpus (used by tests for deterministic small-case
        validation). When ``None``, the embedded Mossinghoff snapshot is
        used.

    Returns
    -------
    WithheldPartition
        With ``n_withheld = round(len(corpus) * holdout_fraction)``.

    Raises
    ------
    ValueError
        If ``holdout_fraction`` is outside ``[0, 1)`` (1.0 rejected) or
        the corpus is empty.
    """
    if not (0.0 <= holdout_fraction < 1.0):
        if math.isclose(holdout_fraction, 1.0):
            raise ValueError(
                f"holdout_fraction=1.0 is degenerate (visible set would "
                f"be empty); choose < 1.0"
            )
        raise ValueError(
            f"holdout_fraction must be in [0, 1); got {holdout_fraction}"
        )

    corpus = _corpus if _corpus is not None else _load_default_corpus()
    if not corpus:
        raise ValueError(
            "empty Mossinghoff snapshot; cannot partition"
        )

    n = len(corpus)
    n_withheld = int(round(n * float(holdout_fraction)))
    n_withheld = max(0, min(n_withheld, n))
    n_visible = n - n_withheld

    rng = random.Random(int(seed))
    indices = list(range(n))
    rng.shuffle(indices)
    withheld_indices = set(indices[:n_withheld])

    visible_set: List[Tuple[List[int], float]] = []
    withheld_set: List[Tuple[List[int], float]] = []
    for i, (coeffs, m) in enumerate(corpus):
        # Defensive copy of the coeffs list.
        item = (list(coeffs), float(m))
        if i in withheld_indices:
            withheld_set.append(item)
        else:
            visible_set.append(item)

    return WithheldPartition(
        visible_set=visible_set,
        withheld_set=withheld_set,
        partition_seed=int(seed),
        n_visible=n_visible,
        n_withheld=n_withheld,
    )


# ---------------------------------------------------------------------------
# Withheld pipeline (instance-scoped catalog-check override)
# ---------------------------------------------------------------------------


@dataclass
class WithheldDiscoveryPipeline(DiscoveryPipeline):
    """Subclass of DiscoveryPipeline whose catalog-check is overridden
    on the instance.

    The override is *instance-scoped* — we shadow ``_check_catalog_miss``
    by using a method-bound version. The module-level function on
    ``prometheus_math.discovery_pipeline`` is untouched, so concurrent
    regular-pipeline users are not affected.

    Treats any polynomial whose M is within ``tol`` (default 1e-5) of
    a withheld entry's M as ``catalog_miss=True``. Visible entries
    are treated as in-catalog (catalog_miss=False), so the agent
    can't claim 'rediscovery' for an already-visible polynomial.
    """

    partition: Optional[WithheldPartition] = None
    tol: float = 1e-5

    def _withheld_catalog_check(
        self, coeffs: List[int], mahler_measure: float
    ) -> Tuple[bool, str, List[str]]:
        """Catalog miss iff M matches a withheld entry within ``tol``
        AND does NOT match any visible entry within ``tol``.

        Visible match is evaluated first because if both match, the
        polynomial is genuinely 'in catalog' from the agent's
        perspective — it didn't have to rediscover anything.
        """
        catalogs_checked = ["Mossinghoff(visible)"]
        if self.partition is None:
            return True, "no partition; trivially miss", catalogs_checked

        # Phase 1: visible match? Treat as 'known in catalog'.
        for _, vm in self.partition.visible_set:
            if abs(vm - mahler_measure) < self.tol:
                return (
                    False,
                    f"matches visible Mossinghoff entry M={vm:.6f}",
                    catalogs_checked,
                )

        # Phase 2: withheld match? Treat as 'catalog miss' (rediscovery
        # candidate).
        for _, wm in self.partition.withheld_set:
            if abs(wm - mahler_measure) < self.tol:
                return (
                    True,
                    f"matches WITHHELD Mossinghoff entry M={wm:.6f}",
                    catalogs_checked + ["Mossinghoff(withheld)"],
                )

        # Phase 3: matches no entry. Genuine catalog miss.
        return (
            True,
            "missing from visible AND withheld Mossinghoff",
            catalogs_checked,
        )

    def process_candidate(
        self,
        coeffs: List[int],
        mahler_measure: float,
    ) -> DiscoveryRecord:
        """Process a candidate using the withheld catalog override.

        We monkey-patch ``_check_catalog_miss`` in the module namespace
        ONLY for the duration of this call (using a context manager),
        then call ``super().process_candidate``. The module-level
        function is restored on exit even if exceptions occur.
        """
        from prometheus_math import discovery_pipeline as dp_module
        original = dp_module._check_catalog_miss

        # Bind self into the override closure so it picks up the partition.
        def _override(c: List[int], m: float, tol: float = 1e-5):
            return self._withheld_catalog_check(c, m)

        dp_module._check_catalog_miss = _override
        try:
            return super().process_candidate(coeffs, mahler_measure)
        finally:
            dp_module._check_catalog_miss = original


# ---------------------------------------------------------------------------
# Env-side override (so the env's _check_mossinghoff doesn't classify a
# withheld polynomial as already-known and skip the pipeline path).
# ---------------------------------------------------------------------------


@contextmanager
def _patched_env_mossinghoff_check(partition: WithheldPartition, tol: float = 1e-5):
    """Temporarily patch ``discovery_env._check_mossinghoff`` so that
    withheld entries are reported as ``is_known=False`` (they should
    look like 'undiscovered' to the env), while visible entries stay
    ``is_known=True``.

    Restored on exit even under exceptions.
    """
    from prometheus_math import discovery_env as de_module
    original = de_module._check_mossinghoff

    def _override(coeffs, m_value):
        # Visible match -> still known.
        for _, vm in partition.visible_set:
            if abs(vm - m_value) < tol:
                return True, f"visible_M={vm:.6f}"
        # Withheld match -> treat as 'not known' so the env sends it
        # to the pipeline branch (which our WithheldDiscoveryPipeline
        # will then process as a rediscovery candidate).
        for _, wm in partition.withheld_set:
            if abs(wm - m_value) < tol:
                return False, None
        return False, None

    de_module._check_mossinghoff = _override
    try:
        yield
    finally:
        de_module._check_mossinghoff = original


# ---------------------------------------------------------------------------
# Pilot result
# ---------------------------------------------------------------------------


@dataclass
class WithheldResult:
    """Aggregated outcome of running the withheld-rediscovery pilot."""

    n_visible: int
    n_withheld: int
    withheld_rediscovery_count: int
    withheld_PROMOTE_count: int
    withheld_rediscovery_rate: float  # in [0, 1]
    withheld_PROMOTE_rate: float  # in [0, 1]
    episodes_per_rediscovery: float  # inf if no rediscoveries
    by_seed: Dict[int, Dict[str, Any]] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Pilot
# ---------------------------------------------------------------------------


def _make_withheld_env_and_run_seed(
    partition: WithheldPartition,
    n_episodes: int,
    seed: int,
    agent: str = "reinforce",
    tol: float = 1e-5,
) -> Dict[str, Any]:
    """Run a single seed and return its rediscovery info.

    Returns a dict with:
        ``rediscovered``: set of withheld-entry indices the agent's
            M-values matched at least once.
        ``promoted``: set of withheld-entry indices whose pipeline
            record had terminal_state in {PROMOTED, SHADOW_CATALOG}.
        ``rediscovery_count``, ``promote_count``, ``n_episodes_run``.
    """
    # Lazy imports — keep test-time module-load fast and avoid pulling
    # heavy deps when the user only wants the partitioner.
    from prometheus_math.discovery_env import DiscoveryEnv
    from prometheus_math.demo_discovery import (
        train_random,
        train_reinforce_contextual,
    )

    if n_episodes <= 0:
        return {
            "rediscovered": set(),
            "promoted": set(),
            "rediscovery_count": 0,
            "promote_count": 0,
            "n_episodes_run": 0,
        }

    # The env will call its own _check_mossinghoff; we patch it to
    # treat withheld polys as 'unknown' so they reach the pipeline.
    env = DiscoveryEnv(
        degree=10,
        max_episodes=n_episodes,
        kernel_db_path=":memory:",
        seed=seed,
        log_discoveries=True,
        reward_shape="shaped",
        enable_pipeline=False,  # we attach our own pipeline below
    )

    rediscovered: set = set()
    promoted: set = set()

    with _patched_env_mossinghoff_check(partition, tol=tol):
        # Reset env so the kernel is wired up. Then attach our pipeline.
        env.reset()
        # Inject the withheld pipeline so that DISCOVERY_CANDIDATE polys
        # land here instead of the regular pipeline.
        env._enable_pipeline = True
        env._pipeline = WithheldDiscoveryPipeline(
            kernel=env._kernel,
            ext=env._ext,
            partition=partition,
            tol=tol,
        )

        # Run the agent.
        if agent == "random":
            train_random(env, n_episodes, seed=seed)
        elif agent == "reinforce":
            train_reinforce_contextual(env, n_episodes, seed=seed)
        else:
            raise ValueError(
                f"unknown agent {agent!r}; expected 'random' or 'reinforce'"
            )

        # Inspect: for each rewarded episode, check whether any of its
        # M-values match a withheld entry. The env's discoveries() list
        # holds sub-Lehmer + Salem-cluster episodes; we check each.
        # Also walk pipeline_records to collect promoted withheld matches.
        for record in env.discoveries():
            m_value = record.mahler_measure
            for idx, (_, wm) in enumerate(partition.withheld_set):
                if abs(wm - m_value) < tol:
                    rediscovered.add(idx)
                    break  # one withheld match per polynomial is enough

        for prec in env.pipeline_records():
            m_value = prec.mahler_measure
            survived = prec.terminal_state in ("PROMOTED", "SHADOW_CATALOG")
            if not survived:
                continue
            for idx, (_, wm) in enumerate(partition.withheld_set):
                if abs(wm - m_value) < tol:
                    promoted.add(idx)
                    break

    env.close()

    return {
        "rediscovered": rediscovered,
        "promoted": promoted,
        "rediscovery_count": len(rediscovered),
        "promote_count": len(promoted),
        "n_episodes_run": n_episodes,
    }


def run_withheld_pilot(
    partition: WithheldPartition,
    n_episodes: int,
    seeds: Tuple[int, ...] = (0, 1, 2),
    agent: str = "reinforce",
    tol: float = 1e-5,
) -> WithheldResult:
    """Run the withheld-rediscovery benchmark across ``seeds`` seeds.

    Parameters
    ----------
    partition : WithheldPartition
        Visible/withheld split (typically from ``partition_mossinghoff``).
    n_episodes : int
        Episodes per seed. The total budget is ``n_episodes * len(seeds)``.
        ``n_episodes=0`` is allowed and trivially returns 0 rediscoveries.
    seeds : tuple of int
        Random seeds to run. The aggregate rediscovery count is the
        UNION across seeds (a withheld entry rediscovered in any seed
        counts once).
    agent : str
        ``'reinforce'`` or ``'random'``.
    tol : float
        M-match tolerance. Default 1e-5 (matches env / pipeline).

    Returns
    -------
    WithheldResult
    """
    if n_episodes < 0:
        raise ValueError(f"n_episodes must be >= 0; got {n_episodes}")

    by_seed: Dict[int, Dict[str, Any]] = {}
    union_rediscovered: set = set()
    union_promoted: set = set()
    total_episodes = 0

    for s in seeds:
        out = _make_withheld_env_and_run_seed(
            partition, n_episodes, seed=int(s), agent=agent, tol=tol
        )
        by_seed[int(s)] = {
            "rediscovery_count": out["rediscovery_count"],
            "promote_count": out["promote_count"],
            "rediscovered_indices": sorted(out["rediscovered"]),
            "promoted_indices": sorted(out["promoted"]),
            "n_episodes_run": out["n_episodes_run"],
        }
        union_rediscovered |= out["rediscovered"]
        union_promoted |= out["promoted"]
        total_episodes += out["n_episodes_run"]

    n_w = partition.n_withheld
    rediscovery_count = len(union_rediscovered)
    promote_count = len(union_promoted)
    rediscovery_rate = (
        float(rediscovery_count) / float(n_w) if n_w > 0 else 0.0
    )
    promote_rate = (
        float(promote_count) / float(n_w) if n_w > 0 else 0.0
    )
    episodes_per = (
        float(total_episodes) / float(rediscovery_count)
        if rediscovery_count > 0
        else float("inf")
    )

    return WithheldResult(
        n_visible=partition.n_visible,
        n_withheld=partition.n_withheld,
        withheld_rediscovery_count=rediscovery_count,
        withheld_PROMOTE_count=promote_count,
        withheld_rediscovery_rate=rediscovery_rate,
        withheld_PROMOTE_rate=promote_rate,
        episodes_per_rediscovery=episodes_per,
        by_seed=by_seed,
    )


__all__ = [
    "WithheldPartition",
    "WithheldDiscoveryPipeline",
    "WithheldResult",
    "partition_mossinghoff",
    "run_withheld_pilot",
]
