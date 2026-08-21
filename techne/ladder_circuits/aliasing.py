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

**Two preconditions the formulation needs** (the second corrects an overclaim I made in
cycle 018).

1. **Factorization.** When family members differ in *how much* they observe (a horizon-h
   searcher sees more as h grows), `π` must be a projection every member's view FACTORS
   THROUGH: `π_i = f_i ∘ π`. Only then is each member's view a coarsening, and only then does
   a witness under `π` bind the whole family. Two *incomparable* observation sets may admit no
   useful common projection except the full input — which destroys the argument. In that case
   partition the family into observation classes and prove incapacity class by class.
   `verify_factorization` checks the precondition instead of assuming it.

2. **What the witness proves.** A witness shows that any deterministic evaluator factoring
   through `π` is wrong on **at least one member of the pair** — NOT on both. Cycle 018's
   write-up said "every member errs on each witness", which is loose: a member returning the
   correct answer for `x₁` is thereby wrong on `x₂`, and vice versa. The code always tested the
   correct disjunction; the prose did not.

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
    "family_cannot_be_correct", "verify_family_incapacity", "verify_factorization",
    "fiber_search",
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
    on AT LEAST ONE — never necessarily both, since a member answering `left` correctly is
    thereby wrong on `right`. `all_members_err` is the theorem's actual prediction;
    `all_members_aliased` checks the premise that each member really did return one answer for
    both, which is what "factors through π" buys.
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


def verify_factorization(
    instances: Sequence[Any],
    coarse: Callable[[Any], Hashable],
    fine: Callable[[Any], Hashable],
) -> bool:
    """Does `coarse` factor through `fine` on these instances — i.e. `coarse = f ∘ fine`?

    Checked as: `fine(x) == fine(y)` implies `coarse(x) == coarse(y)`. This is the precondition
    for treating `fine` as the family's finest projection. Empirical over `instances`, so a True
    result is evidence on this battery rather than a proof of the functional identity.
    """
    for a, b in combinations(instances, 2):
        if fine(a) == fine(b) and coarse(a) != coarse(b):
            return False
    return True


def fiber_search(
    seed: Any,
    mutate: Callable[[Any], Iterable[Any]],
    projection: Callable[[Any], Hashable],
    truth: Callable[[Any], Any],
    max_steps: int = 500,
) -> Optional[AliasingWitness]:
    """Synthesise an aliasing witness instead of finding one in a battery you already have.

    The move (external review, round 7): stay inside ONE fiber of `π` and vary until the truth
    flips. Mutations that leave the fiber are discarded, so the search is constrained to an
    evaluator-equivalence class rather than wandering the whole input space — strictly better
    than random adversarial search, because every candidate is already indistinguishable to the
    evaluator and only the truth is in question.

        find x₁ ≠ x₂ with π(x₁) = π(x₂) and T(x₁) ≠ T(x₂)

    For R10 this is exactly "fix the world pair, mutate only the technique". No general
    termination guarantee — emptiness of the target set inherits the undecidability already
    recorded for agreement regions — but it is complete on bounded domains, and it turns the
    instrument from an audit into an attack.

    Returns the first witness found, or None if `max_steps` candidates stayed inside the fiber
    without the truth ever flipping.
    """
    fiber_value = projection(seed)
    seed_truth = truth(seed)
    steps = 0
    for candidate in mutate(seed):
        if steps >= max_steps:
            break
        steps += 1
        if projection(candidate) != fiber_value:
            continue                       # left the fiber: the evaluator could tell them apart
        if truth(candidate) != seed_truth:
            return AliasingWitness(seed, candidate, fiber_value, seed_truth, truth(candidate),
                                   note=f"synthesised by fiber search in {steps} steps")
    return None
