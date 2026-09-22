"""Translation manifest for one adaptation (directive Phase 3).

Every aspect of a source experiment is mapped to EXACTLY ONE relation to its BEE instantiation, and anything that
is not IDENTICAL carries a reason. Anything BEE cannot state at all is an explicit OMITTED or UNREPRESENTABLE entry
with a structured refusal -- never a silent approximation.

  IDENTICAL       BEE states the same thing the same way (e.g. a Proteus player-VM program; BIT replay).
  ANALOGOUS       BEE states a faithful counterpart in its own terms (e.g. SFE's E episodes -> n_seeds x episodes).
  MODIFIED        represented, but deliberately changed (e.g. a smaller budget, a different but honest world param).
  OMITTED         a source aspect intentionally dropped (e.g. the scientific-conclusion layer BEE never authors).
  UNREPRESENTABLE BEE has no object for it (e.g. SFE ask/answer streams, an offspring cap, in-life damage to an
                  organism's HIDDEN state). The adaptation still runs; the manifest records what it could not carry.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import List

RELATIONS = ("IDENTICAL", "ANALOGOUS", "MODIFIED", "OMITTED", "UNREPRESENTABLE")
_NEEDS_REASON = tuple(r for r in RELATIONS if r != "IDENTICAL")


@dataclass
class Entry:
    aspect: str          # what is being translated: world / organism / intervention / objective / control / ...
    source: str          # how the source engine states it
    bee: str             # how BEE states it, or "-" when not represented
    relation: str        # one of RELATIONS
    reason: str = ""     # required for every relation except IDENTICAL

    def __post_init__(self) -> None:
        if self.relation not in RELATIONS:
            raise ValueError("relation %r not in %s" % (self.relation, RELATIONS))
        if self.relation in _NEEDS_REASON and not self.reason:
            raise ValueError("aspect %r is %s and must carry a reason" % (self.aspect, self.relation))


def refusal(aspect: str, source: str, reason: str, kind: str = "UNREPRESENTABLE") -> Entry:
    """A structured refusal: a source aspect BEE will not approximate. kind is OMITTED or UNREPRESENTABLE."""
    if kind not in ("OMITTED", "UNREPRESENTABLE"):
        raise ValueError("a refusal is OMITTED or UNREPRESENTABLE, not %r" % kind)
    return Entry(aspect=aspect, source=source, bee="-", relation=kind, reason=reason)


@dataclass
class Manifest:
    adaptation_id: str
    source_experiment: str            # the Atlas key of the source experiment
    entries: List[Entry] = field(default_factory=list)

    def add(self, aspect: str, source: str, bee: str, relation: str, reason: str = "") -> "Manifest":
        self.entries.append(Entry(aspect=aspect, source=source, bee=bee, relation=relation, reason=reason))
        return self

    def add_refusal(self, aspect: str, source: str, reason: str, kind: str = "UNREPRESENTABLE") -> "Manifest":
        self.entries.append(refusal(aspect, source, reason, kind))
        return self

    def refusals(self) -> List[Entry]:
        return [e for e in self.entries if e.relation in ("OMITTED", "UNREPRESENTABLE")]

    def counts(self) -> dict:
        return {r: sum(1 for e in self.entries if e.relation == r) for r in RELATIONS}

    def to_dict(self) -> dict:
        return {"adaptation_id": self.adaptation_id, "source_experiment": self.source_experiment,
                "counts": self.counts(), "entries": [asdict(e) for e in self.entries]}
