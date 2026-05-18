"""H2 — multi-method triangulation protocol generator.

Variant of D3 that explores INCONCLUSIVE records along the METHOD axis
rather than the RESAMPLE axis. For each A4 INCONCLUSIVE parent, runs
the same fit at 3 different (sample_size, polynomial_degree) METHOD
VARIANTS and reports the verdict spread.

Method variants:
  M1: n=20, degree=1   — linear small-sample
  M2: n=50, degree=2   — quadratic mid-sample
  M3: n=80, degree=3   — cubic large-sample

If ≥ 2 of 3 methods agree on terminal verdict → triangulated up/down
to terminal. Otherwise → genuinely INCONCLUSIVE (the methods disagree,
indicating an interesting boundary).

Pulls from frontier "process supervision" (per-step scoring) and IRIS-
style hypothesis-search-over-methods. Distinguished from D3:
  D3: vary random seeds (resampling noise)
  H2: vary method (sample size + degree axis)
Together they bound the "INCONCLUSIVE → terminal" pathway from two
orthogonal directions.
"""
from __future__ import annotations

import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

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
)


METHOD_VARIANTS = (
    ("linear_small", 20, 1),
    ("quadratic_mid", 50, 2),
    ("cubic_large", 80, 3),
)


class H2TriangulationProtocolGenerator(Generator):
    generator_id = "h2"
    claim_kind = ClaimKind.KILL_NEIGHBORHOOD.value
    status = GeneratorStatus.ACTIVE

    def __init__(
        self,
        batch_id: str,
        seed: int = 250,
        corpus_dir: Optional[Path] = None,
    ) -> None:
        super().__init__(batch_id)
        self._rng = random.Random(seed)
        self._corpus_dir = corpus_dir if corpus_dir is not None else CORPUS_DIR
        self._reader = CorpusReader(self._corpus_dir)
        self._knots = _load_catalog(KNOTS_DB_PATH)
        self._ecs = _load_catalog(BSD_RICH_DB_PATH)
        self._inconclusive_parents: List[TheseusRecord] = []
        self._loaded = False
        self._seed_gen = A4SymbolicRegressionGenerator(
            batch_id=batch_id + ":h2seed", seed=seed + 1300, sample_size=15
        )

    def description(self) -> str:
        return (
            f"h2: multi-method triangulation on INCONCLUSIVE A4 records "
            f"({len(METHOD_VARIANTS)} method variants)"
        )

    def add_parent(self, record: TheseusRecord) -> None:
        if record.verdict != Verdict.INCONCLUSIVE.value:
            return
        p = record.claim_payload
        if "knot_invariant" in p and "ec_invariant" in p:
            self._inconclusive_parents.append(record)

    def _load_inconclusive(self) -> None:
        if self._loaded:
            return
        try:
            for r in self._reader.iter_records():
                if r.verdict == Verdict.INCONCLUSIVE.value:
                    p = r.claim_payload
                    if "knot_invariant" in p and "ec_invariant" in p:
                        self._inconclusive_parents.append(r)
        except Exception:
            pass
        self._loaded = True

    def _bootstrap_parent(self) -> Optional[TheseusRecord]:
        for _ in range(50):
            r = self._seed_gen.next()
            if r is None:
                return None
            if r.verdict == Verdict.INCONCLUSIVE.value:
                return r
        return None

    def _polyfit_at_method(
        self, ki: str, ei: str, sample_size: int, degree: int, seed: int
    ) -> Tuple[Optional[float], int]:
        """Run polyfit at given method parameters; returns (r2, n_actual)."""
        rng = random.Random(seed)
        xs: List[float] = []
        ys: List[float] = []
        for _ in range(sample_size * 4):
            if len(xs) >= sample_size:
                break
            k = rng.choice(self._knots)
            e = rng.choice(self._ecs)
            kv = _get_int(k, ki)
            ev = _get_int(e, ei)
            if kv is None or ev is None:
                continue
            xs.append(float(kv))
            ys.append(float(ev))
        if len(xs) < 5:
            return None, len(xs)
        _, r2 = _polyfit_r2(xs, ys, degree)
        return r2, len(xs)

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

            step_trace: List[dict] = []
            child_r2s: List[float] = []
            child_verdicts: List[str] = []
            for i, (method_name, n_target, degree) in enumerate(METHOD_VARIANTS):
                child_seed = self._rng.randint(0, 2**31)
                r2, n_actual = self._polyfit_at_method(
                    ki, ei, n_target, degree, child_seed
                )
                if r2 is None:
                    continue
                child_verdict = self._r2_to_verdict(r2)
                child_r2s.append(r2)
                child_verdicts.append(child_verdict)
                step_info = min(1.0, abs(r2 - 0.5) * 2.0)
                step_trace.append(
                    StepRecord(
                        step_id=f"step_{i}",
                        step_kind="method_variant",
                        step_method=f"polyfit_{method_name}",
                        step_input={
                            "knot_invariant": ki,
                            "ec_invariant": ei,
                            "sample_size_target": n_target,
                            "sample_size_actual": n_actual,
                            "degree": degree,
                            "child_seed": child_seed,
                        },
                        step_output={"r2": r2, "child_verdict": child_verdict},
                        step_info_density=step_info,
                        step_convergence="exact",
                    ).to_dict()
                )

            if len(child_verdicts) < 2:
                self.attempts += 1
                continue

            counts = Counter(child_verdicts)
            top_v, top_n = counts.most_common(1)[0]
            agreement = top_n / len(child_verdicts)

            if agreement >= 2 / 3:
                triangulated = top_v
                kill_pattern = (
                    None if triangulated != Verdict.REJECTED.value
                    else f"h2_method_triangulated_reject"
                )
            else:
                triangulated = Verdict.INCONCLUSIVE.value
                kill_pattern = None

            mean_r2 = sum(child_r2s) / len(child_r2s)
            canonical = (
                f"H2_METHOD[parent={parent.record_id[:8]}] "
                f"{ei}(ec) ≈ poly_var({ki}(knot)) | "
                f"methods={dict(counts)} | mean_R²={mean_r2:.3f} "
                f"agreement={agreement:.2f} → {triangulated}"
            )
            payload = {
                "parent_record_id": parent.record_id,
                "knot_invariant": ki,
                "ec_invariant": ei,
                "n_methods_evaluated": len(child_verdicts),
                "method_r2s": child_r2s,
                "method_verdicts": child_verdicts,
                "method_counts": dict(counts),
                "mean_r2": mean_r2,
                "agreement_fraction": agreement,
                "triangulated_verdict": triangulated,
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
                verdict=triangulated,
                kill_pattern=kill_pattern,
                parent_record_id=parent.record_id,
                method="multi_method_triangulation_polyfit",
                convergence_status="triangulated" if agreement >= 2 / 3 else "boundary",
                step_trace=step_trace,
                extras={"frontier_technique": "multi_method_triangulation_orthogonal_to_d3"},
            )
            self.attempts += 1
            self.emitted.append(record_id)
            return r

        return None
