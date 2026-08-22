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
    "fiber_search", "UniformAdversaryReport", "uniform_adversary", "OutOfDomain",
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


class OutOfDomain(ValueError):
    """The search was not run because the input could not support it.

    Distinct from "searched and found nothing" — a distinction this module SHIPPED WITHOUT for
    ten cycles, and which the cycle-036 instrument contract caught on its first pass over the
    arsenal. It is the same defect cycle 029 fixed in `structural_constancy` (an all-raising
    probe space reading as constancy); the lesson was fixed there and never propagated here.
    """


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

    Raises `OutOfDomain` when there are fewer than two instances: with nothing to compare, "no
    witness" would be a statement about the input rather than about the projection.
    """
    if len(instances) < 2:
        raise OutOfDomain(
            f"aliasing needs at least two instances to compare; got {len(instances)}. "
            "Returning None here would report 'the projection separates everything' when "
            "nothing was compared")
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

    **ELEVENTH INSTANCE of the answering-outside-your-domain class, cycle 041 — and the first one
    PREDICTED rather than stumbled on.** An empty family returned
    `all_members_err=True, all_members_aliased=True`: every member of a family with no members
    errs, vacuously, and the caller reads that as the theorem confirmed. Two `all()` calls over an
    empty mapping, which is the same VACUOUS_QUANTIFIER idiom as `is_refinement_chain`.

    It was found by asking the mechanism classifier which functions carry the idiom and checking
    the four it named. It also sat in cycle 040's UNPROBED bucket, which that cycle reported as a
    virtue of the audit; the bucket was concealing a live instance, so UNPROBED needs hand-checks
    rather than a count.
    """
    family = list(family)
    if not family:
        raise OutOfDomain(
            "an empty family cannot demonstrate incapacity: `all_members_err` would be True "
            "because there are no members to err, and this module's whole argument is that "
            "absence of a counterexample is not evidence of impossibility")
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
    if len(instances) < 2:
        raise OutOfDomain(
            f"factorization needs at least two instances to compare; got {len(instances)}. "
            "Returning True here would report 'the coarse view factors through the fine one' "
            "when nothing was checked (sixth instance of the answering-outside-your-domain bug "
            "class, cycle 039)")
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
    in_fiber = 0
    for candidate in mutate(seed):
        if steps >= max_steps:
            break
        steps += 1
        if projection(candidate) != fiber_value:
            continue                       # left the fiber: the evaluator could tell them apart
        in_fiber += 1
        if truth(candidate) != seed_truth:
            return AliasingWitness(seed, candidate, fiber_value, seed_truth, truth(candidate),
                                   note=f"synthesised by fiber search in {steps} steps")
    if in_fiber == 0:
        raise OutOfDomain(
            f"no candidate stayed inside the fiber ({steps} mutations tried). Returning None "
            "would report 'the truth never varies in this fiber' when the fiber was never "
            "sampled — the same conflation the contract caught in find_aliasing_witness")
    return None


# =============================================================================================
# Uniform adversaries (cycle 032, external review round 8).
#
# Cycle 022 found that FIFO and LIFO observation classes are incomparable, and concluded that
# incapacity must be proved per observation class. Round 8 pointed out the failure mode that
# invites: with infinitely many incomparable classes — E_n = "observe the first n symbols", or
# worse E_S = "observe x restricted to S" for every finite S — per-class enumeration cannot
# finish, and it is tempting to conclude "we could not enumerate, so the family might be
# sufficient."
#
# **Enumeration is one proof technique, not the only one.** A UNIFORM ADVERSARY CONSTRUCTOR
# kills an infinite family with a single schema:
#
#     for every parameter S,  construct (x_S, y_S)  with  pi_S(x_S) = pi_S(y_S)  and
#     T(x_S) != T(y_S)
#
# The proof hierarchy, weakest evidence last:
#
#     single shared projection      one witness kills the family
#     finite observation classes    one witness per class
#     parameterised constructor     one schema kills infinitely many classes
#     none of the above             no family-wide result — and say so, rather than implying
#                                   sufficiency from a failure to enumerate
# =============================================================================================


@dataclass(frozen=True)
class UniformAdversaryReport:
    """Result of checking an adversary SCHEMA across sampled parameters.

    **This is refutation-capable and never a proof.** "The constructor works for every parameter"
    is a UNIVERSAL claim over the parameter space (cycle 031's taxonomy), so it is monotone
    DOWNWARD: sampling can break it by finding one parameter where the construction fails, and
    can never establish it. A clean run means the schema survived the parameters tried.

    What it does buy: if the schema is correct, ONE argument covers infinitely many observation
    classes, and the "could not enumerate, therefore possibly sufficient" fallacy is closed.
    """

    family: str
    n_parameters: int
    failures: Tuple[Any, ...]
    witnesses: Tuple[Any, ...] = ()

    @property
    def schema_survived(self) -> bool:
        """Raises on an empty parameter set.

        SEVENTH instance of the bug class, and the worst-placed of the seven: this module's own
        docstring warns against concluding sufficiency from a failure to enumerate, and this
        property did exactly that — reporting a schema as SURVIVING when it had never run.
        """
        if self.n_parameters == 0:
            raise ValueError(
                "no parameters were tried, so the schema neither survived nor failed. Reporting "
                "True here is the very fallacy this module exists to close: concluding a family "
                "is unthreatened from a failure to test it")
        return not self.failures

    @property
    def proves_family_incapacity(self) -> bool:
        """Always False. Kept as an attribute so no caller can quietly upgrade the verdict."""
        return False

    def report(self) -> str:  # pragma: no cover - reporting only
        state = "survived" if self.schema_survived else f"FAILED on {self.failures[:3]}"
        return (f"{self.family}: adversary schema {state} across {self.n_parameters} sampled "
                f"parameters (refutation-capable; not a proof of family incapacity)")


def uniform_adversary(family: str, parameters: Sequence[Any],
                      construct: Callable[[Any], Tuple[Any, Any]],
                      projection_for: Callable[[Any], Callable[[Any], Hashable]],
                      truth: Callable[[Any], Any]) -> UniformAdversaryReport:
    """Check one adversary SCHEMA against many parameters of an evaluator family.

    `construct(param) -> (x, y)` must build a pair that the parameter's own projection cannot
    separate and whose truths differ. A parameter where that fails is recorded as a failure of
    the SCHEMA, not as evidence that the family is sound there.
    """
    failures, witnesses = [], []
    for param in parameters:
        try:
            x, y = construct(param)
            pi = projection_for(param)
            aliased = pi(x) == pi(y)
            differs = truth(x) != truth(y)
        except Exception:
            failures.append(param)
            continue
        if aliased and differs:
            witnesses.append((param, x, y))
        else:
            failures.append(param)
    return UniformAdversaryReport(family, len(parameters), tuple(failures), tuple(witnesses))
