"""D3 — triangulation-seeds generator (MCTS-flavored multi-resample).

Consumes INCONCLUSIVE records from the corpus (A4's three-state verdict
pathway introduced in Fire #5). For each INCONCLUSIVE parent, runs N
independent resamples at the same parameters and reports verdict
spread: if all resamples agree → triangulated (high confidence
inconclusive); if they disagree → genuinely INCONCLUSIVE, surfaces a
true substrate boundary.

MCTS-flavored: each resample is a child node in the triangulation tree.
The tree expansion is uniform-random at v0.1 (simple resampling). Tier 1
will add UCT-style child selection biased toward unresolved branches.
Polu/Sutskever pattern for inconclusive-driven exploration.

Verdict mapping:
- SHADOW_CATALOG if all resamples agree on SHADOW (triangulated up)
- REJECTED if all resamples agree on REJECTED (triangulated down)
- INCONCLUSIVE if resamples disagree (genuinely boundary)

The substrate now has a closed-loop triangulation path:
  A4 emits INCONCLUSIVE → D3 picks up → tree expansion → terminal verdict
"""
from __future__ import annotations

import math
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from theseus.config import CORPUS_DIR, KNOTS_DB_PATH, BSD_RICH_DB_PATH
from theseus.emit.corpus_reader import CorpusReader
from theseus.emit.record_schema import (
    TheseusRecord,
    ClaimKind,
    Verdict,
    StepRecord,
)
from theseus.generators.base import Generator, GeneratorStatus
from theseus.generators.a1_catalog_cross_product import (
    _load_catalog,
    _get_int,
)
from theseus.generators.a4_symbolic_regression import (
    A4SymbolicRegressionGenerator,
    _polyfit_r2,
    STRONG_R2,
    WEAK_R2,
    DEGREES,
)


DEFAULT_TREE_BRANCHES = 5
DEFAULT_INCONCLUSIVE_BUFFER = 500


class D3TriangulationSeedsGenerator(Generator):
    generator_id = "d3"
    claim_kind = ClaimKind.KILL_NEIGHBORHOOD.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        seed: int = 60,
        corpus_dir: Optional[Path] = None,
        n_branches: int = DEFAULT_TREE_BRANCHES,
        buffer_size: int = DEFAULT_INCONCLUSIVE_BUFFER,
    ) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._corpus_dir = corpus_dir if corpus_dir is not None else CORPUS_DIR
        self._reader = CorpusReader(self._corpus_dir)
        self._n_branches = n_branches
        self._buffer = buffer_size
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        self._inconclusive_parents: List[TheseusRecord] = []
        self._loaded = False
        # Bootstrap A4 for when corpus has no INCONCLUSIVE records yet
        self._seed_gen = A4SymbolicRegressionGenerator(
            batch_id=batch_id + ":d3seed", seed=seed + 700, sample_size=15
        )

    def description(self) -> str:
        return (
            f"d3: triangulation-seeds (MCTS-flavored multi-resample on "
            f"INCONCLUSIVE records; {self._n_branches} branches per tree)"
        )

    def _load_inconclusive(self) -> None:
        if self._loaded:
            return
        try:
            for r in self._reader.iter_records():
                if r.verdict == Verdict.INCONCLUSIVE.value:
                    p = r.claim_payload
                    if "knot_invariant" in p and "ec_invariant" in p:
                        self._inconclusive_parents.append(r)
                        if len(self._inconclusive_parents) >= self._buffer:
                            break
        except Exception:
            pass
        self._loaded = True

    def add_parent(self, record: TheseusRecord) -> None:
        """Accept INCONCLUSIVE records emitted within the same batch."""
        if record.verdict != Verdict.INCONCLUSIVE.value:
            return
        p = record.claim_payload
        if "knot_invariant" in p and "ec_invariant" in p:
            self._inconclusive_parents.append(record)
            if len(self._inconclusive_parents) > self._buffer * 2:
                self._inconclusive_parents = self._inconclusive_parents[-self._buffer:]

    def _bootstrap_parent(self) -> Optional[TheseusRecord]:
        for _ in range(50):
            r = self._seed_gen.next()
            if r is None:
                return None
            if r.verdict == Verdict.INCONCLUSIVE.value:
                return r
        return None

    def _resample_polyfit(
        self, ki: str, ei: str, degree: int, seed: int, n: int = 30
    ) -> Optional[float]:
        """One resample; returns R² of best polyfit at given degree."""
        rng = random.Random(seed)
        xs: List[float] = []
        ys: List[float] = []
        for _ in range(n * 3):
            if len(xs) >= n:
                break
            k = rng.choice(self._knots)
            e = rng.choice(self._ecs)
            kv = _get_int(k, ki)
            ev = _get_int(e, ei)
            if kv is None or ev is None:
                continue
            xs.append(float(kv))
            ys.append(float(ev))
        if len(xs) < 10:
            return None
        _, r2 = _polyfit_r2(xs, ys, degree)
        return r2

    def _r2_to_verdict(self, r2: float) -> str:
        if r2 >= STRONG_R2:
            return Verdict.SHADOW_CATALOG.value
        if r2 >= WEAK_R2:
            return Verdict.INCONCLUSIVE.value
        return Verdict.REJECTED.value

    def next(self) -> Optional[TheseusRecord]:
        if not self._loaded:
            self._load_inconclusive()

        for _ in range(10):
            if self._inconclusive_parents:
                parent = self._rng.choice(self._inconclusive_parents)
            else:
                parent = self._bootstrap_parent()
                if parent is None:
                    return None

            p = parent.claim_payload
            ki = p["knot_invariant"]
            ei = p["ec_invariant"]
            parent_degree = p.get("best_degree", 2)

            # MCTS tree expansion: N independent resamples.
            # Each resample is a step in the process-supervised trace.
            child_r2s: List[float] = []
            child_verdicts: List[str] = []
            step_trace: List[dict] = []
            for branch_idx in range(self._n_branches):
                child_seed = self._rng.randint(0, 2**31)
                r2 = self._resample_polyfit(
                    ki, ei, parent_degree, child_seed
                )
                if r2 is None:
                    continue
                child_v = self._r2_to_verdict(r2)
                child_r2s.append(r2)
                child_verdicts.append(child_v)
                # Step info-density: strong fits (high |R²| from 0.5)
                # carry more info; INCONCLUSIVE mid-range carries less.
                step_info = min(1.0, abs(r2 - 0.5) * 2.0)
                step_trace.append(
                    StepRecord(
                        step_id=f"step_{branch_idx}",
                        step_kind="resample",
                        step_method="numpy_polyfit",
                        step_input={
                            "knot_invariant": ki,
                            "ec_invariant": ei,
                            "polynomial_degree": parent_degree,
                            "child_seed": child_seed,
                        },
                        step_output={
                            "r2": r2,
                            "child_verdict": child_v,
                        },
                        step_info_density=step_info,
                        step_convergence="exact",
                    ).to_dict()
                )

            if len(child_verdicts) < 2:
                self.attempts += 1
                continue

            # Triangulation: vote across children
            verdict_counts = Counter(child_verdicts)
            top_verdict, top_count = verdict_counts.most_common(1)[0]
            agreement = top_count / len(child_verdicts)

            mean_r2 = sum(child_r2s) / len(child_r2s)
            var_r2 = sum((r - mean_r2) ** 2 for r in child_r2s) / len(child_r2s)
            stdev_r2 = math.sqrt(var_r2)

            if agreement >= 0.8:
                # Triangulated: high agreement across children
                triangulated_verdict = top_verdict
                kill_pattern = (
                    None if triangulated_verdict != Verdict.REJECTED.value
                    else f"d3_triangulated_reject_mean_r2={mean_r2:.3f}"
                )
            else:
                # Disagreement → genuinely inconclusive (substrate boundary)
                triangulated_verdict = Verdict.INCONCLUSIVE.value
                kill_pattern = None

            canonical = (
                f"D3_TRIANG[parent={parent.record_id[:8]}, branches={len(child_verdicts)}] "
                f"{ei}(ec) ≈ poly_{parent_degree}({ki}(knot)) "
                f"| R²: mean={mean_r2:.3f} stdev={stdev_r2:.3f} "
                f"| verdicts={dict(verdict_counts)} agreement={agreement:.2f} "
                f"→ {triangulated_verdict}"
            )
            payload = {
                "parent_record_id": parent.record_id,
                "knot_invariant": ki,
                "ec_invariant": ei,
                "polynomial_degree": parent_degree,
                "n_branches_evaluated": len(child_verdicts),
                "child_r2_values": child_r2s,
                "child_verdicts": child_verdicts,
                "mean_r2": mean_r2,
                "stdev_r2": stdev_r2,
                "agreement_fraction": agreement,
                "verdict_counts": dict(verdict_counts),
                "triangulated_verdict": triangulated_verdict,
            }

            record_id = TheseusRecord.compute_record_id(
                canonical_claim_text=canonical,
                generator_id=self.generator_id,
            )
            r = TheseusRecord(
                record_id=record_id,
                generator_id=self.generator_id,
                batch_id=self.batch_id,
                emitted_at=datetime.now(timezone.utc).isoformat(),
                claim_kind=self.claim_kind,
                claim_payload=payload,
                canonical_claim_text=canonical,
                verdict=triangulated_verdict,
                kill_pattern=kill_pattern,
                parent_record_id=parent.record_id,
                method="mcts_multi_resample_polyfit",
                convergence_status="triangulated" if agreement >= 0.8 else "boundary",
                step_trace=step_trace,
                extras={
                    "frontier_technique": "mcts_inconclusive_triangulation_with_process_supervision",
                    "agreement_threshold": 0.8,
                },
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
