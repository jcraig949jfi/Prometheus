"""Evaluator aliasing — the general instrument behind claim v11. (Cycle 018.)

Cycle 017 measured that no setting of a feature-sensitivity dial reaches the honest operating
point at canon R10, and I filed it as *"a battery parameter that does not read the instance
cannot separate instances that differ."* External review (round 6) supplied the sharper and
provable form, and it is the form that belongs in the arsenal:

> Let an evaluator family `E_θ` observe only a projection `π(x)`. Then for all θ,
> `π(x₁) = π(x₂)` implies `E_θ(x₁) = E_θ(x₂)`. If the ground truth differs — `Y(x₁) ≠ Y(x₂)` —
> then **no θ is correct on both**.

That is an impossibility proof against an entire evaluator family, not another bad-
hyperparameter result. It also yields a battery-design rule that is executable:

> **Find two probes in the same equivalence class under everything the evaluator can see, with
> different correct verdicts.**

`find_aliasing_witness` does exactly that search, and `verify_family_incapacity` confirms the
theorem empirically by sweeping the family — theorem and measurement, as the loop requires.

**One refinement the formulation needs.** When family members differ in *how much* they observe
(a horizon-h searcher sees more as h grows), `π` must be the **finest** projection any member
can see. A witness under the finest projection kills every member, since each member's view is
a coarsening of it. `finest_projection_note` in each retrofit records which projection was used
and why it is the finest.

Retrofitted this cycle to canon R6, R9 and R10 (see `tests/test_aliasing.py`). R3's capacity
width is claimed in the ledger as a fourth instance but is **not** retrofitted here; it is
listed as unverified until it is.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any, Callable, Dict, Hashable, Iterable, List, Optional, Sequence, Tuple

__all__ = [
    "AliasingWitness", "find_aliasing_witness", "all_aliasing_witnesses",
    "family_cannot_be_correct", "verify_family_incapacity",
]


@dataclass(frozen=True)
class AliasingWitness:
    """Two instances an evaluator family provably cannot separate.

    `projection_value` is what every member of the family sees for BOTH instances; the truths
    differ, so any member returning one answer is wrong on one of them.
    """

    left: Any
    right: Any
    projection_value: Hashable
    left_truth: Any
    right_truth: Any
    note: str = ""

    def __str__(self) -> str:  # pragma: no cover - reporting only
        return (f"aliased under π = {self.projection_value!r}: "
                f"{self.left!r} (truth {self.left_truth!r}) vs "
                f"{self.right!r} (truth {self.right_truth!r})")


def find_aliasing_witness(
    instances: Sequence[Any],
    projection: Callable[[Any], Hashable],
    truth: Callable[[Any], Any],
    note: str = "",
) -> Optional[AliasingWitness]:
    """Search for two instances with equal projections and different truths.

    `projection` must be the FINEST view any member of the evaluator family can obtain. A
    witness proves that no member — at any parameter setting — is correct on both instances.
    Returns None when the projection is sufficient to separate every pair in `instances`, which
    is evidence of adequacy on this battery only, never a proof of it.
    """
    for a, b in combinations(instances, 2):
        if projection(a) == projection(b) and truth(a) != truth(b):
            return AliasingWitness(a, b, projection(a), truth(a), truth(b), note)
    return None


def all_aliasing_witnesses(
    instances: Sequence[Any],
    projection: Callable[[Any], Hashable],
    truth: Callable[[Any], Any],
) -> List[AliasingWitness]:
    """Every aliased pair, for reporting how badly a projection collapses a battery."""
    return [AliasingWitness(a, b, projection(a), truth(a), truth(b))
            for a, b in combinations(instances, 2)
            if projection(a) == projection(b) and truth(a) != truth(b)]


def family_cannot_be_correct(
    instances: Sequence[Any],
    projection: Callable[[Any], Hashable],
    truth: Callable[[Any], Any],
) -> bool:
    """THE THEOREM. True iff an aliasing witness exists, i.e. iff no member of any evaluator
    family restricted to `projection` can be correct on all of `instances`."""
    return find_aliasing_witness(instances, projection, truth) is not None


def verify_family_incapacity(
    family: Iterable[Any],
    evaluate: Callable[[Any, Any], Any],
    witness: AliasingWitness,
) -> Dict[str, Any]:
    """THE MEASUREMENT that must agree with the theorem.

    For each member θ of `family`, evaluate both halves of the witness and confirm that θ errs
    on at least one. Returns per-member outcomes plus `all_members_err`, which the theorem says
    must be True whenever the witness is genuine.
    """
    outcomes: Dict[Any, Dict[str, Any]] = {}
    for theta in family:
        left, right = evaluate(theta, witness.left), evaluate(theta, witness.right)
        outcomes[theta] = {
            "left": left,
            "right": right,
            "agreed_as_predicted": left == right,
            "errs": (left != witness.left_truth) or (right != witness.right_truth),
        }
    return {
        "per_member": outcomes,
        "all_members_err": all(o["errs"] for o in outcomes.values()),
        "all_members_aliased": all(o["agreed_as_predicted"] for o in outcomes.values()),
    }
