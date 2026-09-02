# D15-A DESIGN AMENDMENTS R1 (review verdict, 2026-09-02)
Amends D15A_DESIGN_PACKET.md (commit 85e50a619). No scientific
falsifier relaxed. Amended design hash journaled below; the campaign
freeze will embed the pair (packet sha, this sha).

## A1 — G7 refined: coverage-CONTROLLED, not coverage-tripwired
The 1.1x coverage ratio becomes a TRIPWIRE (reported, flags the
comparison), not the ontology. Every principal active-vs-control
comparison records: probe budget, unique states reached, total
state-visits, new transitions observed, version-space contraction,
oracle repair entropy, synthesis outcome. Preregistered
coverage-controlled analysis: compare active vs control branches
MATCHED/CONDITIONED on comparable unique-state coverage (nearest-
coverage pairing within instances; band |cov_a - cov_c| <= 10%).
Interpretations (frozen):
  advantage survives coverage control  -> information-selection claim
                                          alive (even if coverage
                                          ratio > 1.1 -- report the
                                          exploration asymmetry, do
                                          NOT downgrade on the
                                          tripwire alone);
  advantage disappears under control   -> COVERAGE_MEDIATED; the
                                          strong active-identifiability
                                          claim FAILS.

## A2 — G2 strengthened: the FULL chain, counterfactually
Sibling forks from the SAME (world, event_seq, KnowledgeSet,
hypotheses, version-space state, remaining budget) consuming
IDENTICAL probe budgets but achieving DIFFERENT uncertainty
reductions. Preregistered question: does the branch that removes
more legitimate repair hypotheses subsequently achieve greater
synthesis advantage? Minimum reported per fork-pair: delta repair
entropy; delta effective candidate-set size; delta (FAILGUIDED -
BLIND) synthesis lift; delta final solution rate; delta abstention
calibration. A positive G1 with a failed chain adjudicates
D15A_CHAIN_BROKEN -- a first-class result ("learned about its
uncertainty but could not convert it"), never partial support.

## A3 — Epistemic replay is a HARD GEN-2.1 qualification condition
Every consequential decision (SEARCH_MORE / OBSERVE_MORE /
SYNTHESIZE / ABSTAIN) records a machine-readable declaration of its
exact epistemic inputs, deterministically derivable from: world
ledger + ancestry + legal imports + KnowledgeSet(decision_seq) +
versioned/hashed feature transforms. Forbidden as unreconstructible
hidden state: client caches, mutable accumulators, ambient process
memory, unprovenanced feature tables, post-seq observations,
imports outside KnowledgeSet, unversioned transform code.
REPLAY TEST (Phase 0, hard gate): pick a recorded decision; destroy
the client process/state; reconstruct legal knowledge from ledger +
KnowledgeSet at that seq; rerun the declared pipeline; require
BIT-IDENTICAL input vector and decision. Exact-replay failure =>
ENGINE defect (F10 insufficient) filed BEFORE science proceeds.
Doctrine: Prometheus must be able to prove "this conclusion was
generated from exactly the information legally available at this
moment."

## A4 — Phase 0 issues TWO INDEPENDENT verdicts (never collapsed)
D15A_PHASE0_SCIENCE_INSTRUMENT in {SCIENCE_READY, SCIENCE_NOT_READY}
D15A_PHASE0_GEN21            in {ENGINE_QUALIFIED, ENGINE_NOT_QUALIFIED}
Confirmatory D15-A proceeds ONLY on SCIENCE_READY + ENGINE_QUALIFIED.

## A5 — Topology-2 boundary
T2 stays frozen at 6/90 under the prior pin. After Phase 0: a
SEPARATE recommendation (restart/resume/abandon); any F3/F5/F10
defect that could alter its epistemic history forbids resumption
from existing state. No silent continuation across a qualification
boundary.
