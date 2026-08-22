"""STAGE TAXONOMY — two coordinates, four partition motions, and why. (Cycle 035.)

Cycles 025–027 found three stage types by tripping over them: rewrite (instruments blind),
select (instruments work), filter/accumulate (instruments inverted). Round-9 review said the
three-way derivation was still missing a case and that one categorical label is the wrong shape
anyway. Both are right.

## Coordinate 1 — partition motion

Comparing the partition `P` a stage's input induces on the instance set with the partition `Q`
its output induces, there are four relations, not three:

    Q < P     COARSENING      information destruction    (truncation, selection)
    Q > P     REFINEMENT      information acquisition    (accumulating verdict bits)
    Q = P     PRESERVING      partition untouched        (identity, reorder, redact, hash)
    Q ∥ P     INCOMPARABLE    information SUBSTITUTION   (transverse re-encoding)

The fourth is the one I missed, and it is not hypothetical: R10's two verdict coordinates —
`assumption_status` and `conclusion_status` — induce partitions of the live battery with block
sizes [6, 8] and [5, 9] and **neither refines the other**. A real transverse pair, not a
synthetic construction.

## Coordinate 2 — content transformation

Partition motion cannot be the whole description, because identity, reordering, redaction,
hashing and semantic rewriting all satisfy `Q = P` and are obviously different operations.
Partition theory cannot separate them — which is exactly what cycle 025 established when the
composition instruments reported identical numbers with redaction replaced by the identity.

So a stage wants **two** coordinates, `(partition motion, content transformation)`, and the three
live findings get clean homes:

    selection / truncation      COARSENING     content preserved
    accumulating verdict bits   REFINEMENT     content extended
    redaction                   PRESERVING     content changed        <- cycle 025's blind spot

## The derivation — which cell a stage CAN occupy is fixed by its information access

This is the part that makes the taxonomy a derivation rather than a longer list.

**A stage that is a pure function of its predecessor's output can only COARSEN or PRESERVE.**
If `Q = f(P-output)`, then any two instances agreeing on the predecessor's output agree on this
one, so `Q` is a union of `P`-blocks. Refinement and incomparability are impossible — not
unlikely, impossible.

So a stage reaching REFINEMENT or INCOMPARABLE is *proof* that it read something beyond its
predecessor. That explains the cycle 024 / 027 split exactly:

- cycle 024's transform pipeline: each stage saw only the previous output, so the chain could
  only coarsen, and the profile's monotonicity assumptions held.
- cycle 027's falsification battery: each check reads the ORIGINAL candidate, not the previous
  check's verdict, so the state refines and every monotonicity ran backwards.

The stage's cell is a fact about its **information access**, not about what it computes.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Hashable, Optional, Sequence, Tuple

from prometheus_math.partition import induced_partition, refines

__all__ = ["COARSENING", "REFINEMENT", "PRESERVING", "INCOMPARABLE", "StageDescriptor",
           "partition_motion", "describe_stage", "function_of_predecessor_can_only_coarsen"]

COARSENING = "COARSENING"        # Q < P  : information destruction
REFINEMENT = "REFINEMENT"        # Q > P  : information acquisition
PRESERVING = "PRESERVING"        # Q = P  : partition untouched
INCOMPARABLE = "INCOMPARABLE"    # Q || P : information substitution


def partition_motion(before: Sequence[Any], after: Sequence[Any],
                     n: Optional[int] = None) -> str:
    """Classify the motion from one partition to another. `before`/`after` are partitions."""
    n = n if n is not None else sum(len(b) for b in before)
    after_refines_before = refines(after, before, n)
    before_refines_after = refines(before, after, n)
    if after_refines_before and before_refines_after:
        return PRESERVING
    if before_refines_after:
        return COARSENING          # every input block sits inside an output block
    if after_refines_before:
        return REFINEMENT          # output splits input blocks
    return INCOMPARABLE


@dataclass(frozen=True)
class StageDescriptor:
    """The two coordinates. One label was never enough."""

    name: str
    motion: str
    content_changed: bool

    @property
    def instruments_apply(self) -> str:
        """What cycles 024-027 measured, indexed by the cell rather than remembered per case."""
        if self.motion == COARSENING:
            return "profile applies as written (cycle 026)"
        if self.motion == REFINEMENT:
            return "profile INVERTS — check chain_direction first (cycle 027)"
        if self.motion == PRESERVING and self.content_changed:
            return "profile is BLIND — use the pipeline's own predicate (cycle 025)"
        if self.motion == INCOMPARABLE:
            return "no chain argument available; partition into observation classes (cycle 022)"
        return "identity: nothing to measure"

    def render(self) -> str:  # pragma: no cover - reporting only
        return (f"{self.name}: ({self.motion}, "
                f"content {'changed' if self.content_changed else 'preserved'}) — "
                f"{self.instruments_apply}")


def describe_stage(name: str, instances: Sequence[Any],
                   before_key: Callable[[Any], Hashable],
                   after_key: Callable[[Any], Hashable],
                   content_before: Optional[Callable[[Any], Any]] = None,
                   content_after: Optional[Callable[[Any], Any]] = None) -> StageDescriptor:
    """Describe a stage on both coordinates from its behaviour over an instance set."""
    items = list(instances)
    n = len(items)
    motion = partition_motion(induced_partition(items, before_key),
                              induced_partition(items, after_key), n)
    changed = False
    if content_before is not None and content_after is not None:
        changed = any(content_before(i) != content_after(i) for i in items)
    return StageDescriptor(name, motion, changed)


def function_of_predecessor_can_only_coarsen(
        instances: Sequence[Any],
        predecessor: Callable[[Any], Hashable],
        f: Callable[[Hashable], Hashable]) -> str:
    """THE DERIVATION, as an executable check.

    If a stage is `f` applied to its predecessor's output, then instances agreeing on the
    predecessor agree here too, so the new partition is a union of old blocks. Returns the
    measured motion, which must be COARSENING or PRESERVING for any `f` whatsoever — so a stage
    measuring REFINEMENT or INCOMPARABLE has proved it read beyond its predecessor.
    """
    items = list(instances)
    return partition_motion(induced_partition(items, predecessor),
                            induced_partition(items, lambda i: f(predecessor(i))),
                            len(items))
