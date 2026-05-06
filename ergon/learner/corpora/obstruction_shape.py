"""OBSTRUCTION_SHAPE corpus loader (W5.1) — chart-aware stub.

Wraps Techne's ``prometheus_math.obstruction_env`` corpus into the
v0.5 substrate-v2.2-shaped contract: each record carries
``coordinate_chart_id`` + ``chart_status`` so cross-corpus chart
alignment (W5.3) can resolve charts after Techne ships Tier 0 P0
registration (joint sprint Day 3-4).

Until P0 lands, every record gets the provisional placeholder
``obstruction_shape_provisional_v0`` with ``chart_status="provisional"``.
Re-bind on real registration; the constant below + the loader are the
only call sites that need updating.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterator, List, Optional

from prometheus_math._obstruction_corpus import (
    OBSTRUCTION_CORPUS,
    OBSTRUCTION_SIGNATURE,
    SECONDARY_SIGNATURE,
    CorpusEntry,
)


PROVISIONAL_CHART_ID = "obstruction_shape_provisional_v0"
PROVISIONAL_CHART_STATUS = "provisional"


@dataclass(frozen=True)
class ObstructionRecord:
    """Chart-aware OBSTRUCTION_SHAPE record.

    Pre-falsification shape per substrate v2.2 §6.3 P5 contract:
    object features + canonical_form (the planted-signature label) +
    raw invariants. The ``kill_verdict`` field is the ground-truth
    label; downstream consumers in W5 use it as supervision for the
    transfer probe (W5.4) but it does NOT participate in
    pre-falsification training input.
    """

    coordinate_chart_id: str
    chart_status: str
    record_index: int
    features: Dict[str, Any]
    kill_verdict: bool
    matches_obstruction_signature: bool
    matches_secondary_signature: bool
    sequence_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _matches(features: Dict[str, Any], signature: Dict[str, Any]) -> bool:
    return all(features.get(k) == v for k, v in signature.items())


def load_obstruction_shape_corpus(
    corpus: Optional[List[CorpusEntry]] = None,
    chart_id: str = PROVISIONAL_CHART_ID,
    chart_status: str = PROVISIONAL_CHART_STATUS,
    limit: Optional[int] = None,
) -> Iterator[ObstructionRecord]:
    """Yield ObstructionRecord objects with chart bindings.

    Defaults to the synthetic OBSTRUCTION_CORPUS. Pass ``corpus`` to
    override (e.g., live OEIS-grade data via
    ``prometheus_math._obstruction_corpus_live.load_live_corpus``).
    """
    source = corpus if corpus is not None else OBSTRUCTION_CORPUS
    for i, entry in enumerate(source):
        if limit is not None and i >= limit:
            break
        feats = entry.features()
        sid = getattr(entry, "sequence_id", None)
        yield ObstructionRecord(
            coordinate_chart_id=chart_id,
            chart_status=chart_status,
            record_index=i,
            features=feats,
            kill_verdict=bool(entry.kill_verdict),
            matches_obstruction_signature=_matches(feats, OBSTRUCTION_SIGNATURE),
            matches_secondary_signature=_matches(feats, SECONDARY_SIGNATURE),
            sequence_id=str(sid) if sid is not None else None,
            metadata={
                "corpus_source": "synthetic" if corpus is None else "external",
                "n_corpus": len(source),
            },
        )


__all__ = [
    "ObstructionRecord",
    "load_obstruction_shape_corpus",
    "PROVISIONAL_CHART_ID",
    "PROVISIONAL_CHART_STATUS",
]


if __name__ == "__main__":
    import json

    records = list(load_obstruction_shape_corpus(limit=100))
    print(f"loaded {len(records)} records")
    sample = records[0].to_dict()
    print(json.dumps(sample, indent=2, default=str))
    n_kill = sum(1 for r in records if r.kill_verdict)
    n_obs = sum(1 for r in records if r.matches_obstruction_signature)
    n_sec = sum(1 for r in records if r.matches_secondary_signature)
    print(f"kill_verdict=True: {n_kill}/{len(records)}")
    print(f"matches OBSTRUCTION_SIGNATURE: {n_obs}/{len(records)}")
    print(f"matches SECONDARY_SIGNATURE: {n_sec}/{len(records)}")
    assert all(r.coordinate_chart_id == PROVISIONAL_CHART_ID for r in records)
    assert all(r.chart_status == PROVISIONAL_CHART_STATUS for r in records)
    print("OK: every record carries provisional chart_id + chart_status")
