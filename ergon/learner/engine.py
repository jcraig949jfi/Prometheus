"""ergon.learner.engine — top-level Trial 2 search loop.

Per pivot/ergon_learner_proposal_v8.md §6 + Trial 2 spec:

The engine ties everything together:
  1. Scheduler picks operator class for each episode
  2. Operator mutates a parent (sampled from archive) -> child genome
  3. Trivial-pattern detector runs F_TRIVIAL_BAND_REJECT on child
  4. (v0.5+) BindEvalKernelV2 evaluates child; produces reward components
  5. (MVP) substrate_pass evaluator stub returns kill-path verdicts
  6. Reward computed; cell coordinate computed; archive submission
  7. Diagnostics tracked (operator_call_counts, F_TRIVIAL_BAND_REJECT
     trigger_rate, archive coverage, etc.)

At MVP scope: BindEvalKernelV2 integration is stubbed. The engine runs
end-to-end with a synthetic substrate-pass evaluator that produces
realistic-but-fake kill verdicts (mostly BLOCK, with random-but-rare
CLEAR/WARN). This validates the loop's structure without requiring the
full BindEvalKernelV2 pipeline; v0.5 wires the real evaluator.

Trial 2 dry-run: engine.run(n_episodes=N) with N=10 (smoke), 100 (small
pilot), 1K (full Trial 2). Outputs cumulative archive snapshot +
per-operator-class diagnostic + F_TRIVIAL_BAND_REJECT statistics.
"""
from __future__ import annotations

import random
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ergon.learner.archive import ArchiveEntry, FitnessTuple, MAPElitesArchive
from ergon.learner.descriptor import (
    CellCoordinate,
    EvaluationResult,
    compute_cell_coordinate,
    compute_magnitude_bucket,
    OUT_OF_BAND_BUCKET,
)
from ergon.learner.genome import Genome, MutationOperatorClass
from ergon.learner.operators.anti_prior import AntiPriorOperator
from ergon.learner.operators.base import make_mvp_atom_pool
from ergon.learner.operators.structural import StructuralOperator
from ergon.learner.operators.structured_null import StructuredNullOperator
from ergon.learner.operators.symbolic import SymbolicOperator
from ergon.learner.operators.uniform import UniformOperator
from ergon.learner.reward import (
    MVP_REWARD_WEIGHTS,
    RewardComponents,
    compute_reward,
    evaluate_substrate_pass,
    is_promotable,
)
from ergon.learner.scheduler import OperatorScheduler
from ergon.learner.triviality import (
    ClaimDescriptor,
    TrivialMatch,
    f_trivial_band_reject,
)


@dataclass
class EpisodeResult:
    """Outcome of one engine episode (one mutation + evaluation)."""
    episode_idx: int
    operator_class: MutationOperatorClass
    genome_hash: str
    parent_hash: Optional[str]
    cell_coordinate: CellCoordinate
    fitness: FitnessTuple
    reward: float
    promoted_to_archive: bool
    f_trivial_match: TrivialMatch
    kill_path_verdicts: Dict[str, str]
    elapsed_seconds: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineRunReport:
    """Summary statistics from a full engine.run(n_episodes) invocation.

    Two distinct "promotion" counts are tracked separately:
    - n_substrate_passed: episodes where the kill battery (F1+F6+F9+F11) all
        returned CLEAR or WARN. This is the load-bearing PROMOTE rate.
        At Path B configurations: empirically 0/30000.
    - n_won_cell: episodes where the genome won its archive cell
        (became / replaced the elite). This counts archive growth, NOT
        substrate-PROMOTE. Most episodes win cells in early MVP because
        cells are empty.
    """
    n_episodes: int
    n_substrate_passed: int  # the substrate-PROMOTE count
    n_won_cell: int          # the archive-cell-claim count
    n_trivial_rejects: int
    f_trivial_band_reject_rate: float
    archive_n_cells_filled: int
    operator_call_counts: Dict[MutationOperatorClass, int]
    operator_fill_counts: Dict[MutationOperatorClass, int]
    elapsed_seconds: float
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# MVP substrate-pass evaluator stub
# ---------------------------------------------------------------------------
#
# At MVP scope we don't run the real F1+F6+F9+F11 battery against arsenal-
# composed genomes (that requires the full BindEvalKernelV2 + DiscoveryEnv
# integration). Instead we use a calibrated stub that produces realistic
# kill rates aligned with Techne's Path B finding (0/30000 PROMOTEs across
# 90K episodes).
#
# v0.5 swaps this stub for the real BindEvalKernelV2 evaluator pipeline.


class MVPSubstrateEvaluator:
    """Stub substrate evaluator producing realistic kill-rate distributions.

    Calibrated against Path B: at degree 10 + ±3, 0 PROMOTEs in 30K
    episodes per arm. The stub returns ~99.9% BLOCK kills with rare
    (<0.1%) CLEAR/WARN combinations.

    Per-operator behavior matches Path B's finding:
      structural: low PROMOTE rate but high band-concentration
      symbolic: similar
      uniform: ~uniform random across bands
      structured_null: ~uniform with type-respecting structure
      anti_prior: explores low-corpus territory but rare passes
    """

    def __init__(self, seed: Optional[int] = None,
                 promote_rate: float = 0.001):
        self._rng = random.Random(seed)
        self.promote_rate = promote_rate

    def evaluate(
        self,
        genome: Genome,
    ) -> Dict[str, str]:
        """Return kill-path verdicts for one genome.

        Returns: {test_id: "CLEAR"|"WARN"|"BLOCK"}
        """
        # Per-operator-tuned promote rates (mimicking Path B distribution)
        per_op_rates = {
            "structural": self.promote_rate * 1.2,
            "symbolic": self.promote_rate * 1.0,
            "uniform": self.promote_rate * 0.3,
            "structured_null": self.promote_rate * 0.5,
            "anti_prior": self.promote_rate * 0.4,
            "neural": self.promote_rate * 1.5,  # v0.5+
            "external_llm": self.promote_rate * 1.5,
        }
        rate = per_op_rates.get(genome.mutation_operator_class, self.promote_rate)
        passes = self._rng.random() < rate

        if passes:
            return {"F1": "CLEAR", "F6": "CLEAR", "F9": "CLEAR", "F11": "CLEAR"}

        # Pick a random kill-test to be the BLOCK reason
        block_test = self._rng.choice(["F1", "F6", "F9", "F11"])
        verdicts = {"F1": "CLEAR", "F6": "CLEAR", "F9": "CLEAR", "F11": "CLEAR"}
        verdicts[block_test] = "BLOCK"
        return verdicts

    def evaluate_magnitude(self, genome: Genome) -> float:
        """Stub magnitude evaluation — log-uniform across all 5 bounded buckets.

        Maps content_hash to log-magnitude in [0, 14] so all 5 buckets
        ([10^0, 10^3), ..., [10^12, inf)) are reachable. Without this all
        genomes land in buckets 0-2 only; archive coverage stalls at <5%.
        """
        import hashlib
        digest = hashlib.sha256(genome.content_hash().encode()).hexdigest()
        h = int(digest[:16], 16)
        frac = h / (16 ** 16)  # uniform in [0, 1)
        log_mag = frac * 14.0  # log-uniform across [0, 14]
        return 10.0 ** log_mag

    def evaluate_canonicalizer_subclass(self, genome: Genome) -> str:
        """Stub canonicalizer subclass — derives from content_hash for diversity."""
        import hashlib
        digest = hashlib.sha256(genome.content_hash().encode()).hexdigest()
        idx = int(digest[16:24], 16) % 4
        return ("group_quotient", "partition_refinement",
                "ideal_reduction", "variety_fingerprint")[idx]

    def evaluate_canonical_form_distance(self, genome: Genome) -> float:
        """Stub catalog-distance — log-uniform across [1e-4, 1e2]."""
        import hashlib
        digest = hashlib.sha256(genome.content_hash().encode()).hexdigest()
        h = int(digest[24:40], 16)
        frac = h / (16 ** 16)
        log_d = -4.0 + frac * 6.0
        return 10.0 ** log_d


# ---------------------------------------------------------------------------
# The engine
# ---------------------------------------------------------------------------


class TrialTwoEngine:
    """Top-level Trial 2 search loop.

    Wires scheduler + operators + archive + descriptor + triviality +
    reward + evaluator stub together. Each episode:
      1. scheduler.next_operator_class() -> operator
      2. parent <- archive sample (or None for null operators)
      3. operator.mutate(parent, rng, atom_pool) -> child
      4. f_trivial_band_reject(child) -> trivial check
         - if matched: skip evaluation, count as kill
      5. otherwise: evaluator(child) -> kill_path_verdicts + magnitude
      6. compute reward components + cell coordinate + fitness
      7. archive.submit(child, cell, fitness) -> bool
      8. log EpisodeResult
    """

    def __init__(
        self,
        seed: int = 42,
        scheduler: Optional[OperatorScheduler] = None,
        evaluator: Optional[MVPSubstrateEvaluator] = None,
    ):
        self.rng = random.Random(seed)
        self.scheduler = scheduler or OperatorScheduler(seed=seed)
        self.evaluator = evaluator or MVPSubstrateEvaluator(seed=seed)
        self.atom_pool = make_mvp_atom_pool()
        self.archive = MAPElitesArchive()

        # Operator instances
        self._operators = {
            "structural": StructuralOperator(),
            "symbolic": SymbolicOperator(),
            "uniform": UniformOperator(),
            "structured_null": StructuredNullOperator(),
            "anti_prior": AntiPriorOperator(),
        }

        # Recent claim history (for triviality.recurrence_density temporal sig)
        self._recent_claim_history: List[ClaimDescriptor] = []
        self._recent_history_max = 200  # rolling window

        # Episode log
        self.episodes: List[EpisodeResult] = []

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self, n_episodes: int, log_every: int = 100) -> EngineRunReport:
        """Run n_episodes; return summary report."""
        t_start = time.time()
        n_substrate_passed = 0
        n_won_cell = 0
        n_trivial_rejects = 0

        for episode_idx in range(n_episodes):
            result = self._run_episode(episode_idx)
            self.episodes.append(result)

            if result.promoted_to_archive:
                n_won_cell += 1
            if result.fitness.battery_survival_count > 0:
                n_substrate_passed += 1
            if result.f_trivial_match.matched:
                n_trivial_rejects += 1

            if log_every and (episode_idx + 1) % log_every == 0:
                pass  # silent

        elapsed = time.time() - t_start
        return EngineRunReport(
            n_episodes=n_episodes,
            n_substrate_passed=n_substrate_passed,
            n_won_cell=n_won_cell,
            n_trivial_rejects=n_trivial_rejects,
            f_trivial_band_reject_rate=(n_trivial_rejects / n_episodes) if n_episodes > 0 else 0.0,
            archive_n_cells_filled=self.archive.n_cells_filled(),
            operator_call_counts=dict(self.scheduler._cumulative_counts),
            operator_fill_counts=self.archive.operator_fill_count(),
            elapsed_seconds=elapsed,
        )

    # ------------------------------------------------------------------
    # One episode
    # ------------------------------------------------------------------

    def _run_episode(self, episode_idx: int) -> EpisodeResult:
        t_start = time.time()

        # 1. Scheduler picks operator
        op_class = self.scheduler.next_operator_class(episode_idx, archive=self.archive)
        operator = self._operators[op_class]

        # 2. Sample a parent from the archive (random elite); or None for null operators
        parent = None
        if op_class in ("structural", "symbolic") and self.archive.n_cells_filled() > 0:
            elite = self._sample_random_elite()
            if elite is not None:
                parent = self.archive.get_genome(elite.content_hash)

        # 3. Mutate
        child = operator.mutate(parent, self.rng, self.atom_pool)

        # 4. Trivial-pattern detector
        magnitude = self.evaluator.evaluate_magnitude(child)
        claim_desc = ClaimDescriptor(
            claim_id=f"ep_{episode_idx}",
            content_hash=child.content_hash(),
            lineage_id=f"{op_class}:{child.parent_hash or 'fresh'}",
            output_magnitude=magnitude,
            output_type_signature=None,
        )
        trivial_result = f_trivial_band_reject(claim_desc, recent_history=self._recent_claim_history)
        # Update history
        self._recent_claim_history.append(claim_desc)
        if len(self._recent_claim_history) > self._recent_history_max:
            self._recent_claim_history = self._recent_claim_history[-self._recent_history_max:]

        # 5. Evaluate (skip if trivial-rejected)
        if trivial_result.matched:
            kill_verdicts = {
                "F1": "BLOCK",
                "F6": "CLEAR", "F9": "CLEAR", "F11": "CLEAR",
                "F_TRIVIAL_BAND_REJECT": "BLOCK",
            }
            substrate_pass_value = 0.0
        else:
            kill_verdicts = self.evaluator.evaluate(child)
            substrate_pass_value = evaluate_substrate_pass(kill_verdicts)

        # 6. Compute cell coordinate + fitness + reward.
        # Evaluator stub wires diversity into all 3 post-EVAL axes so the
        # archive's 5,000-cell capacity is reachable; v0.5 swaps in real
        # BindEvalKernelV2 outputs.
        eval_result = EvaluationResult(
            output_canonicalizer_subclass=(
                self.evaluator.evaluate_canonicalizer_subclass(child)
            ),
            output_magnitude=magnitude,
            output_type_signature=None,  # genome-inferred from callable_ref
            canonical_form_distance_to_catalog=(
                self.evaluator.evaluate_canonical_form_distance(child)
            ),
        )
        cell = compute_cell_coordinate(child, evaluation=eval_result)

        components = RewardComponents(substrate_pass=substrate_pass_value)
        reward = compute_reward(components, weights=MVP_REWARD_WEIGHTS)

        # Compute band concentration tier
        if cell.magnitude_bucket in (1, 2):
            band_tier = 2  # full-weight buckets
        elif cell.magnitude_bucket in (0, 3, 4):
            band_tier = 1  # downweighted but in-band
        else:
            band_tier = 0  # out_of_band

        elapsed = time.time() - t_start

        fitness = FitnessTuple(
            battery_survival_count=int(substrate_pass_value),
            band_concentration_tier=band_tier,
            cost_amortized_score=1.0 / (1.0 + elapsed),
        )

        # 7. Submit to archive
        promoted = self.archive.submit(child, cell, fitness)

        return EpisodeResult(
            episode_idx=episode_idx,
            operator_class=op_class,
            genome_hash=child.content_hash(),
            parent_hash=child.parent_hash,
            cell_coordinate=cell,
            fitness=fitness,
            reward=reward,
            promoted_to_archive=promoted,
            f_trivial_match=trivial_result,
            kill_path_verdicts=kill_verdicts,
            elapsed_seconds=elapsed,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _sample_random_elite(self) -> Optional[ArchiveEntry]:
        """Sample a random elite from the archive (for parent-based mutation)."""
        cells = list(self.archive.cells.keys())
        if not cells:
            return None
        chosen_key = self.rng.choice(cells)
        return self.archive.cells[chosen_key]
