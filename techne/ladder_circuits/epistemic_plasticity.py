"""Band G: epistemic-rule plasticity + retroactive revalidation (round 4, item 3).

Their sharpening of "evaluator as state", adopted: coordinates 1-7 all assume a FIXED
meta-rule E(claim, evidence) -> {survive, kill, abstain}. Open-ended research discovers the
evaluator itself was wrong. The killer is not the switch E_0 -> E_1; it is RETROACTIVE
REVALIDATION — unwinding everything the old regime certified, including downstream
consequences.

**This is not hypothetical for Prometheus.** It is the June 2026 finding in general form:
the substrate's "2,351 promotions" turned out to be a fossil of a superseded gate — claims
certified under E_0 that nothing ever revalidated when the formula changed. A fixed-evaluator
history reports the old count forever. Their construction is the executable version of that
failure, which is why it is built here rather than filed.

Their hard constraint is implemented as a first-class gate:
    evaluator revisions need an EVALUATOR-INDEPENDENT WARRANT.
Otherwise the terminal cheat: "my experiment failed, therefore I revise failure to mean
success." `revise` REFUSES a revision whose only justification is a disliked verdict.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

import sympy as sp

Verdict = str  # "survive" | "kill" | "abstain"


@dataclass(frozen=True)
class Claim:
    """An identity claim p == q, plus the claims its justification depends on."""

    id: str
    lhs: sp.Expr
    rhs: sp.Expr
    depends_on: Tuple[str, ...] = ()


#: E_0 — the weak evaluator: sample integers from a bounded pool and accept on agreement.
def sampling_evaluator(pool: Sequence[int]) -> Callable[[Claim], Verdict]:
    def evaluate(claim: Claim) -> Verdict:
        x = sorted(claim.lhs.free_symbols | claim.rhs.free_symbols, key=sp.default_sort_key)
        if not x:
            return "survive" if sp.simplify(claim.lhs - claim.rhs) == 0 else "kill"
        v = x[0]
        for n in pool:
            if sp.simplify((claim.lhs - claim.rhs).subs(v, n)) != 0:
                return "kill"
        return "survive"
    return evaluate


#: E_1 — the corrected evaluator: exact symbolic normalization.
def symbolic_evaluator(claim: Claim) -> Verdict:
    return "survive" if sp.expand(claim.lhs - claim.rhs) == 0 else "kill"


class UnwarrantedRevision(RuntimeError):
    """Raised when an evaluator revision is justified only by a verdict someone disliked."""


@dataclass
class Warrant:
    """An evaluator-independent justification: a concrete instance where the OLD evaluator's
    verdict is demonstrably wrong, checkable without appealing to either evaluator's
    authority. Here: a witness value at which a 'surviving' identity numerically fails."""

    claim_id: str
    witness_point: int
    old_verdict: Verdict

    def is_independent(self, claim: Claim, old_eval: Callable[[Claim], Verdict]) -> bool:
        """Sound iff (a) the old evaluator really said `survive`, and (b) an explicit
        computation at the witness point contradicts it. No appeal to the NEW evaluator."""
        if old_eval(claim) != "survive" or self.old_verdict != "survive":
            return False
        x = sorted(claim.lhs.free_symbols | claim.rhs.free_symbols, key=sp.default_sort_key)
        if not x:
            return False
        diff = sp.simplify((claim.lhs - claim.rhs).subs(x[0], self.witness_point))
        return diff != 0


@dataclass
class ResearchCorpus:
    """A corpus certified under some evaluator, with or without the power to revise it."""

    evaluator: Callable[[Claim], Verdict]
    claims: Dict[str, Claim] = field(default_factory=dict)
    certified: Set[str] = field(default_factory=set)
    retracted: List[str] = field(default_factory=list)
    evaluator_fixed: bool = False
    revisions: int = 0

    def submit(self, claim: Claim) -> Verdict:
        self.claims[claim.id] = claim
        verdict = self.evaluator(claim)
        if verdict == "survive":
            self.certified.add(claim.id)
        return verdict

    def revise(self, new_evaluator, warrant: Warrant) -> None:
        """Swap the evaluator — ONLY with an evaluator-independent warrant."""
        if self.evaluator_fixed:
            raise UnwarrantedRevision("this system cannot revise its evaluator")
        claim = self.claims.get(warrant.claim_id)
        if claim is None or not warrant.is_independent(claim, self.evaluator):
            raise UnwarrantedRevision(
                "revision refused: no evaluator-independent warrant "
                "(a disliked verdict is not a reason to change what counts as evidence)"
            )
        self.evaluator = new_evaluator
        self.revisions += 1

    def revalidate(self) -> List[str]:
        """RETROACTIVE revalidation: re-judge every certified claim under the CURRENT
        evaluator and propagate retraction to everything that depended on a retracted claim.
        Returns the retracted ids, in retraction order."""
        newly: List[str] = []
        for cid in sorted(self.certified):
            if self.evaluator(self.claims[cid]) != "survive":
                newly.append(cid)
        # transitive closure over dependencies
        changed = True
        while changed:
            changed = False
            for cid in sorted(self.certified - set(newly)):
                deps = self.claims[cid].depends_on
                if any(d in newly for d in deps):
                    newly.append(cid)
                    changed = True
        for cid in newly:
            self.certified.discard(cid)
            self.retracted.append(cid)
        return newly

    def trusted_count(self) -> int:
        return len(self.certified)
