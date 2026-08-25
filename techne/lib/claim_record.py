"""A factual finding as a typed record, so that markdown becomes a rendering layer.

WHY. Cycles 049-059 produced ~17 errors of my own. External review (2026-08-25) identified
what they have in common more precisely than I had: they are not bad mathematics, they are
**semantic binding failures** -- the computation did what the code asked, and the research
claim silently changed underneath it. The referent was not preserved across

    Q -> P -> S -> T -> M -> C

    Q  question              what was actually being asked
    P  declared population   which rows the answer is about
    S  sample                which rows were touched
    T  transformation        the code path
    M  measurement           the number
    C  claim                 the prose that leaves the building

My existing instruments validate T -> M heavily (positive controls, arms-can-differ). My
failures cluster at **Q -> P**, **P -> S** and **M -> C**, which is why more unit tests do not
fix this. Every arrow below therefore carries its own field, and the ones I keep breaking are
REQUIRED rather than optional.

THE PROMOTION RULE, which supersedes the earlier "adjudication must not be synthetic":

    No claim may be promoted by the same epistemic path that generated it.

The relevant property is **epistemic independence**, not synthetic-versus-human. A human is
also inferential; a second implementation is still synthetic; an independent algorithm may share
an assumption. What made this record's strong results strong was a *different failure mode* on
the adjudicating side -- theorem vs implementation, symbolic route vs verifier, known answer vs
measurement, failing test vs proposed fix. What made self-audit weak was sharing model, context
and ontology with the thing audited.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Optional, Sequence


class Adjudicator(IntEnum):
    """Ordered by epistemic strength. The ordering is the point.

    Same-model review sits at the bottom deliberately: cycles 049-059 measured it catching
    six of seven bad measurements only via IMPLAUSIBILITY, i.e. only when the wrong answer
    looked absurd. It contributes almost nothing against a plausible wrong answer.
    """

    SAME_MODEL_AUDIT = 0        # the generator checking itself -- near-zero strength
    HUMAN_REVIEW = 1
    DIFFERENTIAL_TEST = 2       # weak if implementations share an assumption
    METAMORPHIC_INVARIANT = 3
    KNOWN_ANSWER_CONTROL = 4
    INDEPENDENT_IMPLEMENTATION = 5
    FORMAL_PROOF = 6


MIN_PROMOTABLE = Adjudicator.KNOWN_ANSWER_CONTROL


@dataclass(frozen=True)
class Population:
    """WHICH rows -- as an object, never a human sentence.

    Eight wrong-population errors in eleven cycles all shared one enabling condition: the
    population existed only as prose, so nothing could compare what was claimed against what
    was touched. `selection_predicate` and `sampling_method` are required because
    "first 40 of an ordered table" and "120 drawn at random" are indistinguishable in English
    and decisive in fact.
    """

    population_id: str
    source: str                       # file, table or module the rows came from
    row_count: int
    selection_predicate: str          # the filter, verbatim
    sampling_method: str              # "full-scan" | "random(seed=N)" | "first-N-ordered" | ...
    source_hash: Optional[str] = None
    strata: dict = field(default_factory=dict)
    first_id: Optional[str] = None
    last_id: Optional[str] = None

    def fingerprint(self) -> str:
        payload = json.dumps(dataclasses.asdict(self), sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def is_positional(self) -> bool:
        """True if the sample was taken by ORDER -- the syntactic cause of the failure class."""
        m = self.sampling_method.lower()
        return any(k in m for k in ("first", "head", "top", "ordered", "sorted"))


@dataclass(frozen=True)
class MeasurementContract:
    """What observable result corresponds to the proposition -- fixed BEFORE execution.

    Without this the prose can slide between interpretations after the number is known, which
    is the M -> C failure. Numerator and denominator are stated as predicates so that "resolves
    previously-indeterminate cases" cannot quietly become "resolves cases".
    """

    numerator_predicate: str
    denominator_predicate: str
    population_id: str

    def describes(self, pop: Population) -> bool:
        return self.population_id == pop.population_id


@dataclass(frozen=True)
class Adjudication:
    kind: Adjudicator
    detail: str
    passed: bool
    independent_of_generator: bool     # False for anything sharing the generating path


@dataclass
class Claim:
    """One exported factual finding. Markdown is rendered FROM this, never instead of it."""

    claim_id: str
    proposition: str                   # C
    question: str                      # Q -- the thing actually being asked
    population: Population             # P and S
    contract: MeasurementContract
    measurement_command: str           # T, reproducibly
    value: Any                         # M
    adjudications: list = field(default_factory=list)
    counterfactual: Optional[str] = None   # what input change MUST move the number
    caveats: list = field(default_factory=list)
    source_artifacts: list = field(default_factory=list)

    # ---- the checks that make this more than a dataclass -----------------------------

    def binding_errors(self) -> list[str]:
        """Decidable defects in the Q->P->S->T->M->C chain. No judgement applied."""
        out = []
        if not self.contract.describes(self.population):
            out.append(
                f"POPULATION MISMATCH: contract measures '{self.contract.population_id}' but "
                f"the claim declares '{self.population.population_id}'")
        if not self.measurement_command.strip():
            out.append("NO COMMAND: the number cannot be reproduced")
        if self.population.is_positional() and "ordered" not in self.proposition.lower():
            out.append(
                f"POSITIONAL SAMPLE UNDISCLOSED: sampling_method is "
                f"'{self.population.sampling_method}' but the proposition does not say so")
        if self.counterfactual is None:
            out.append("NO COUNTERFACTUAL: no stated input change that must move this number")
        return out

    def strength(self) -> Adjudicator:
        """Strongest INDEPENDENT adjudication that passed. Dependent ones score zero."""
        ok = [a.kind for a in self.adjudications
              if a.passed and a.independent_of_generator]
        return max(ok) if ok else Adjudicator.SAME_MODEL_AUDIT

    def promotable(self) -> tuple[bool, str]:
        """THE PROMOTION RULE. A claim may not be promoted by its own generating path."""
        errs = self.binding_errors()
        if errs:
            return False, f"binding errors: {'; '.join(errs)}"
        s = self.strength()
        if s < MIN_PROMOTABLE:
            return False, (f"strongest independent adjudication is {s.name}, below "
                           f"{MIN_PROMOTABLE.name}; generation and promotion share a path")
        return True, f"adjudicated by {s.name}"


def render(claim: Claim) -> str:
    """Markdown FROM the record. The prose cannot say anything the record does not carry."""
    ok, why = claim.promotable()
    lines = [
        f"### {claim.claim_id} — {'PROMOTABLE' if ok else 'HELD'}",
        f"**Proposition.** {claim.proposition}",
        f"**Question.** {claim.question}",
        f"**Population.** {claim.population.population_id} "
        f"(n={claim.population.row_count}, {claim.population.sampling_method}, "
        f"fingerprint {claim.population.fingerprint()})",
        f"**Measured.** {claim.value!r} via `{claim.measurement_command}`",
        f"**Contract.** {claim.contract.numerator_predicate} / "
        f"{claim.contract.denominator_predicate}",
        f"**Counterfactual.** {claim.counterfactual or '(none stated)'}",
        f"**Adjudication.** {why}",
    ]
    if claim.caveats:
        lines.append("**Caveats.** " + "; ".join(claim.caveats))
    return "\n".join(lines)
