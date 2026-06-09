"""Reasoning-Quality Emit primitive (Reasoning-Quality Emit Spec v0.1).

The minimal substrate change that lets the *validated* relational H-R1 instrument
finally test the reasoning claim on real data.

Root cause it fixes (spec §0): the substrate computes per-head reasoning scores,
COMBINES them into one scalar/verdict, and persists only the combined value -- the
per-evaluator VECTOR (the only thing the relational H-R1 instrument and the curl
diagnostic can read) is discarded at write time. See
``feedback_no_naive_score_combination``.

The one-sentence change (spec §1): wherever >= 2 heads / judges / scorers evaluate the
same reasoning candidate, persist the per-evaluator score VECTOR -- before any
combination -- alongside whatever combined value is produced. The combine step stays;
we just stop throwing the vector away.

This module is the canonical emitter + the adapter that surfaces the vector to the
UNCHANGED validated runner (it reads ``record["margins"]``; ``evaluator_scores`` IS that
vector). It is no-inference to SPECIFY and to LOG -- the heads already run.

Anti-patterns guarded (spec §7):
  - single evaluator / empty vector  -> ValueError (a lone score is not a vector).
  - non-string evaluator ids         -> ValueError (the family-holdout null and the
                                        per-evaluator screen need STABLE names).
  - uniform sampling                 -> ``mark_contested`` + ``contested_only`` give the
                                        importance-sampling-toward-disagreement lever.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional, Sequence

__all__ = [
    "EMITTER_VERSION",
    "EvalRecord",
    "candidate_id_for",
    "make_record",
    "is_task_contested",
    "top_candidate_per_evaluator",
    "mark_contested",
    "append_records",
    "load_records",
    "to_relational_records",
]

EMITTER_VERSION = "reasoning_quality_emit/v0.1"


def candidate_id_for(text: str) -> str:
    """Stable content-address for a reasoning state / step / solution (spec §2)."""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class EvalRecord:
    """One (candidate, evaluation) line. ``evaluator_scores`` is THE vector (spec §2)."""

    candidate_id: str
    task_id: str
    evaluator_scores: Mapping[str, float]
    combined: Optional[float] = None
    outcome: Optional[str] = None
    contested: Optional[bool] = None
    provenance: dict = field(default_factory=dict)
    emitter_version: str = EMITTER_VERSION

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "task_id": self.task_id,
            "evaluator_scores": dict(self.evaluator_scores),
            "combined": self.combined,
            "outcome": self.outcome,
            "contested": self.contested,
            "provenance": dict(self.provenance),
            "emitter_version": self.emitter_version,
        }

    def to_json_line(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    @classmethod
    def from_json(cls, d: Mapping) -> "EvalRecord":
        return cls(
            candidate_id=d["candidate_id"],
            task_id=d["task_id"],
            evaluator_scores=dict(d["evaluator_scores"]),
            combined=d.get("combined"),
            outcome=d.get("outcome"),
            contested=d.get("contested"),
            provenance=dict(d.get("provenance", {})),
            emitter_version=d.get("emitter_version", EMITTER_VERSION),
        )


def _validate_vector(evaluator_scores: Mapping) -> dict:
    if not isinstance(evaluator_scores, Mapping):
        raise ValueError("evaluator_scores must be a mapping evaluator_id -> float")
    if len(evaluator_scores) < 2:
        # "wherever >= 2 heads evaluate" -- a lone evaluator is not a vector (spec §1).
        raise ValueError(
            f"need >= 2 evaluators to persist a vector, got {len(evaluator_scores)}"
        )
    out = {}
    for k, v in evaluator_scores.items():
        if not isinstance(k, str) or not k:
            # STABLE string names are required for the family-holdout null (spec §2).
            raise ValueError(f"evaluator_id must be a non-empty str, got {k!r}")
        out[k] = float(v)
    return out


def make_record(
    candidate_id: str,
    task_id: str,
    evaluator_scores: Mapping[str, float],
    *,
    combined: Optional[float] = None,
    outcome: Optional[str] = None,
    contested: Optional[bool] = None,
    scorer_versions: Optional[Mapping[str, str]] = None,
    born_at: Optional[str] = None,
) -> EvalRecord:
    """Build one validated emit record.

    ``born_at`` is injected (not auto-stamped) so records are reproducible and tests are
    deterministic; production callers pass an ISO-8601 timestamp.
    """
    scores = _validate_vector(evaluator_scores)
    provenance: dict = {}
    if scorer_versions is not None:
        provenance["scorer_versions"] = dict(scorer_versions)
    if born_at is not None:
        provenance["born_at"] = born_at
    return EvalRecord(
        candidate_id=candidate_id,
        task_id=task_id,
        evaluator_scores=scores,
        combined=None if combined is None else float(combined),
        outcome=outcome,
        contested=contested,
        provenance=provenance,
    )


def top_candidate_per_evaluator(
    candidates: Mapping[str, Mapping[str, float]],
) -> dict:
    """For each evaluator, the candidate it scores highest.

    ``candidates`` maps candidate_id -> evaluator_scores. Ties break on sorted
    candidate_id (deterministic, order-independent).
    """
    evaluators = set().union(*[set(v) for v in candidates.values()]) if candidates else set()
    tops: dict = {}
    for ev in sorted(evaluators):
        best_cid = None
        best_score = None
        for cid in sorted(candidates):
            if ev not in candidates[cid]:
                continue
            s = candidates[cid][ev]
            if best_score is None or s > best_score:
                best_score, best_cid = s, cid
        tops[ev] = best_cid
    return tops


def is_task_contested(candidates: Mapping[str, Mapping[str, float]]) -> bool:
    """True iff the evaluators do not agree on the top candidate (spec §4).

    Curl concentrates on contested candidates; this is the importance-sampling lever.
    A single-candidate task cannot be contested.
    """
    if len(candidates) < 2:
        return False
    tops = top_candidate_per_evaluator(candidates)
    distinct = {cid for cid in tops.values() if cid is not None}
    return len(distinct) > 1


def mark_contested(records: Sequence[EvalRecord]) -> list:
    """Return records with ``contested`` set per task (spec §4).

    Records are grouped by ``task_id``; every candidate in a contested task is flagged
    contested=True (the disagreement is a task-level property of the candidate set).
    """
    by_task: dict = {}
    for r in records:
        by_task.setdefault(r.task_id, {})[r.candidate_id] = dict(r.evaluator_scores)
    contested_task = {t: is_task_contested(c) for t, c in by_task.items()}
    out = []
    for r in records:
        out.append(
            EvalRecord(
                candidate_id=r.candidate_id,
                task_id=r.task_id,
                evaluator_scores=dict(r.evaluator_scores),
                combined=r.combined,
                outcome=r.outcome,
                contested=contested_task[r.task_id],
                provenance=dict(r.provenance),
                emitter_version=r.emitter_version,
            )
        )
    return out


def append_records(path, records: Sequence[EvalRecord]) -> Path:
    """Append-only JSONL writer (spec §2). One line per (candidate, evaluation)."""
    path = Path(path)
    with path.open("a", encoding="utf-8") as fh:
        for r in records:
            fh.write(r.to_json_line() + "\n")
    return path


def load_records(path) -> list:
    """Load emitted records in file order (append-only => emission order)."""
    path = Path(path)
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(EvalRecord.from_json(json.loads(line)))
    return out


def to_relational_records(
    records: Sequence[EvalRecord], *, contested_only: bool = False
) -> list:
    """Adapter: surface the per-evaluator vector as ``margins`` for the UNCHANGED
    validated relational H-R1 runner (it reads ``record["margins"]``).

    ``contested_only`` keeps only candidates in contested tasks -- the
    importance-sampling-toward-disagreement path (spec §4); requires ``mark_contested``
    to have been applied first.
    """
    out = []
    for r in records:
        if contested_only and not r.contested:
            continue
        out.append(
            {
                "margins": dict(r.evaluator_scores),
                "candidate_id": r.candidate_id,
                "task_id": r.task_id,
                "outcome": r.outcome,
                "contested": r.contested,
            }
        )
    return out
