r"""Certification provenance, negative dependencies, and the immutable-observation bottom.

Round 5 items 12.1-12.3, adopted. Three corrections to cycle 011's Band-G build:

12.1 — "evaluator_version + consumed evidence" is NECESSARY BUT NOT SUFFICIENT. Their
soundness hole: a short-circuiting evaluator consumes only e1; a new evaluator changes the
meaning of e2; storing consumed evidence alone means you do not even know the claim is
affected. What must be stored is the PROOF OF CERTIFICATION — the predicates and assumptions
invoked — so revision becomes a build-system dirty-set computation over evaluator COMPONENTS.
Plus **negative dependencies**: "accepted because no counterexample existed under query Q at
snapshot v" consumes no evidence record, yet a later snapshot can invalidate it.

12.2 — justificatory dependency vs discovery provenance. Their test, implemented literally:
A ∈ JustDeps(B) iff Verify(B | Evidence_B \ A) fails. Retraction propagates ONLY through the
justification graph; the influence graph is kept for audits. Otherwise one bad early
heuristic annihilates a lineage that later became independently certified.

12.3 — the constitutional bottom, and it is deliberately thin and boring:
**the historical relation between declared predictions and observed outcomes is immutable.**
You may reinterpret importance, replace metrics, discover a test was confounded. You may not
alter "we predicted y; under protocol P we observed z." That is enough to stop the regress
without freezing scientific doctrine. Their smallest separator is implemented: a
constitutional amendment whose SOLE effect is to make a recorded failure stop counting is
rejected.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple


# ---- 12.1: certification provenance ---------------------------------------------------------

@dataclass(frozen=True)
class NegativeDep:
    """'No record matching query Q existed at snapshot v.' Consumes no evidence id, and is
    invalidated by GROWTH of the database — the nasty hole 12.1 names."""

    query: str
    snapshot: int


@dataclass(frozen=True)
class Certificate:
    """The proof of certification, not merely its inputs (build-system shaped):
        cert(C) = E_v[ p_i(e_j), ..., assumptions, negative deps ]
    """

    claim_id: str
    evaluator_version: str
    predicates: FrozenSet[str]          # evaluator COMPONENTS invoked
    assumptions: FrozenSet[str]
    evidence: FrozenSet[str]
    negative_deps: Tuple[NegativeDep, ...] = ()


@dataclass
class CertificateIndex:
    """Component -> certificates depending on it, so revision is a dirty-set computation."""

    certs: Dict[str, Certificate] = field(default_factory=dict)
    db_snapshot: int = 0
    db_records: Set[str] = field(default_factory=set)   # queries with a matching record

    def add(self, cert: Certificate) -> None:
        self.certs[cert.claim_id] = cert

    def dirty_from_evaluator_change(self, changed_components: Set[str]) -> Set[str]:
        """D0 = {c : deps(c) ∩ ΔE ≠ ∅}. Note this catches certificates whose PREDICATES
        changed even when the evidence they consumed did not — the short-circuit hole."""
        return {
            cid for cid, c in self.certs.items()
            if (c.predicates | c.assumptions) & changed_components
        }

    def add_db_record(self, query: str) -> Set[str]:
        """Database GROWTH: any certificate resting on the absence of a matching record for
        this query is now dirty, though it consumed no evidence at all."""
        self.db_records.add(query)
        self.db_snapshot += 1
        return {
            cid for cid, c in self.certs.items()
            if any(nd.query == query for nd in c.negative_deps)
        }


# ---- 12.2: justificatory dependency vs discovery influence ----------------------------------

@dataclass
class ClaimGraph:
    """Two graphs, deliberately separate. G_J propagates retraction; G_D never does."""

    #: claim -> the evidence ids its certificate verifies against
    evidence: Dict[str, Set[str]] = field(default_factory=dict)
    #: claim -> upstream claims that INSPIRED the search (audit only)
    influence: Dict[str, Set[str]] = field(default_factory=dict)
    #: verifier: (claim, available evidence) -> True iff the certificate still verifies
    verifier: Callable[[str, Set[str]], bool] = lambda c, ev: True

    def just_deps(self, claim: str, candidates: Sequence[str]) -> Set[str]:
        """Their operational test: A is a justificatory dependency of B iff removing A's
        contribution makes B's certificate fail to verify."""
        out: Set[str] = set()
        full = self.evidence.get(claim, set())
        for a in candidates:
            reduced = {e for e in full if not e.startswith(f"{a}:")}
            if not self.verifier(claim, reduced):
                out.add(a)
        return out

    def propagate_retraction(self, retracted: Set[str], universe: Sequence[str]) -> Set[str]:
        """Retraction flows through JUSTIFICATION only. Influence-only descendants survive."""
        out = set(retracted)
        changed = True
        while changed:
            changed = False
            for claim in universe:
                if claim in out:
                    continue
                if self.just_deps(claim, sorted(out)):
                    out.add(claim)
                    changed = True
        return out


# ---- 12.3: the immutable-observation constitution --------------------------------------------

@dataclass(frozen=True)
class Observation:
    """'We predicted y; under protocol P we observed z.' The immutable bottom."""

    trial_id: str
    protocol: str
    predicted: str
    observed: str

    @property
    def failed(self) -> bool:
        return self.predicted != self.observed


class ConstitutionalViolation(RuntimeError):
    """Raised when a proposed amendment would erase or reinterpret a recorded observation."""


@dataclass
class Constitution:
    """Thin, non-revisable meta-contract: bookkeeping physics, not scientific doctrine.

    Amendments may change metrics, thresholds, what counts as important, even what counts as
    evidence — but may NOT alter the historical prediction/observation record, and may not
    have the sole effect of making an already-recorded failure stop counting as one.
    """

    observations: Dict[str, Observation] = field(default_factory=dict)
    amendments: List[str] = field(default_factory=list)

    def record(self, obs: Observation) -> None:
        if obs.trial_id in self.observations:
            raise ConstitutionalViolation(
                f"observation {obs.trial_id} already recorded; history is append-only"
            )
        self.observations[obs.trial_id] = obs

    def amend(self, name: str, rewrites_observations: bool,
              sole_effect_clears_failures: Sequence[str] = ()) -> None:
        """Accept an amendment only if it neither rewrites history nor exists purely to
        un-fail a recorded failure."""
        if rewrites_observations:
            raise ConstitutionalViolation(
                f"amendment {name!r} would rewrite recorded observations — refused"
            )
        cleared = [t for t in sole_effect_clears_failures
                   if t in self.observations and self.observations[t].failed]
        if cleared:
            raise ConstitutionalViolation(
                f"amendment {name!r} exists only to make recorded failures {cleared} stop "
                "counting; the prediction/observation relation is immutable"
            )
        self.amendments.append(name)

    def failures(self) -> List[str]:
        return sorted(t for t, o in self.observations.items() if o.failed)
