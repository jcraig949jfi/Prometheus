# Restart Decisions — 2026-05-09

**Context:** Both Ergon and Techne (the latter via role-pivot to Substrate-Tester) closed their loops 2026-05-08. Three coupled decisions needed before restart. This doc resolves all three and provides paste-ready addenda for the producer restart prompts.

---

## Decision 1 — Substrate-Tester pivot (resolves T-2026-05-08-ST-fire45-002 P1)

**Proposal:** Pivot Substrate-Tester from matrix-filling lane-12 representation-pressure → test-suite design starting fire #46.

**Decision: ACCEPTED.**

Rationale:
- Eight HARD-6 fires (#38-#45) crystallized the 5-tier capability-gap model (Tier A existing, Tier B uniqueness/witness/inequality certificates, Tier C, Tier D distributional, Tier E representation-theoretic).
- Fire #45 declared "STRONGEST SATURATION SIGNAL YET" — the eighth fire produced refinements only, not new tiers.
- Tier-B/Tier-D composition confirmed twice. The model is robust.
- Per HARD-6: the saturation signal IS substrate-grade output. The substrate has reached the boundary of what matrix-filling exploration can produce; further fires of the same kind have diminishing marginal value.

**What Substrate-Tester does next (fires #46+):**
- Lane 12 mode shifts: rather than picking new catalog entries to discover new tier candidates, the lane writes test-suite stubs probing whether the 5 tiers have CONSISTENT coverage across catalog entries already classified.
- File a `pivot/substrate_v3_proposal.md` stub doc capturing the 5-tier framework as the starting design input for the next contract-change window.
- Write test-suite skeletons (one module per tier) that any new primitive landing in the contract window must satisfy.
- Lane 11 (canonicalization-fuzz) continues unchanged — it's the regression layer.
- Other lanes (1-10, 13-18) continue rotation as usual.

**T-2026-05-08-ST-fire45-002 status:** mark RESOLVED-PIVOT-ACCEPTED in `aporia/meta/queue/aporia_inbox.jsonl` with this doc as the resolution pointer. (Substrate-Tester's first fire after restart will read this doc and execute the pivot; Aporia closes its own ticket in parallel.)

---

## Decision 2 — Techne next sequence

Techne's queue stands at 27 OPEN tickets, dominated by 2 distinct workstreams. Sequence them in this order:

### Phase 1 — Strategic input (Aporia-seeded; doc-only)

**T-2026-05-08-T038 (P1) — Classify 104 tensor open problems by substrate-primitive needs.**

Within file ownership; doc-only. Cross-reference with Substrate-Tester's 5-tier model (already in fire-log #38-#45 + the saturation summary). Produces:
- Per-problem mapping → which existing primitive applies, or which new primitive is needed
- Top-5 most-foundational primitives identified (Aporia's prediction: TensorNetwork, ConstructiveExistenceWitness/StructuredEquivalenceClass, GenericityAlmostEverywhereCert, RepresentationTheoreticInvariant, MomentPolytope/SecantVarietyEquation)
- Cross-references to the 8+ open capability-gap tickets, showing how each maps into the 5-tier framework

This is the design input for Phase 2.

### Phase 2 — Full contract-change window (meta-primitive design)

After T038 lands and James reviews it, open a full contract-change window targeting **unified meta-primitives, one per tier**, rather than 8 one-off capability-gap implementations.

Specifically:
- **TensorNetwork primitive** (Tier A++ — extends CoordinateChart with index-contraction structure). Covers: P30 attack paradigm; catalog #49-51, #75-78, #82-84.
- **ConstructiveExistenceWitness / StructuredEquivalenceClass** (Tier B — uniqueness/witness/inequality certificates). Covers: catalog #34, #40-42, #79; absorbs T-ST-fire1-002 (homotopy class), T-ST-fire1-003 (BlockDesign), T-ST-fire21-001 (SymbolicLaurentPolynomial), T-ST-fire21-002 (ArityGradedOperationFamily), T-ST-fire35-001 (finite-group rep), T-ST-fire40-001 (tensor isomorphism / GroupAction), T-ST-fire41-001 (border-rank variety membership).
- **GenericityAlmostEverywhereCert** (Tier D — distributional / generic-property primitives). Covers: catalog #38-39, #66, #73; absorbs T-ST-fire42-001 (Z-eigenvalue distribution), T-ST-fire43-001 (Tensor PCA threshold).
- **RepresentationTheoreticInvariant** (Tier E — Schur/Kronecker/plethysm certificates). Covers: catalog #95-100; absorbs T-ST-fire44-001 (Kronecker positivity).
- **MomentPolytope / SecantVarietyEquation** (Tier C — algebraic-geometric primitives). Covers: catalog #26-35.

All 8 currently-pending P1 capability-gap tickets collapse into instances of one of these 5 meta-primitives. This is dramatically cheaper than 8 separate primitive designs and forces compositional consistency.

**Tradeoff:** The meta-primitive design is multi-day work and expensive to roll back. The alternative (8 one-off primitives) is also multi-day work AND will produce primitives that don't compose, requiring a future unifying refactor. Meta-design first is the longer-but-saner path.

### Phase 3 — Test-infrastructure pile (loop pickup, parallel)

The 9 P2 / P3 substrate-hardening tickets (T016/T017/T019/T022/T031-T037 + minor) are within file ownership and don't require contract changes. Let them run as standard loop pickup in parallel with Phases 1-2. They'll drain over a week of normal 2h cadence.

### Suggested addendum to Techne restart prompt

Paste this AFTER step 7 of the canonical Techne loop prompt (or before step 1, James's call):

```
## First fire after 2026-05-09 restart

Read pivot/restart_decisions_2026-05-09.md before step 1.

Phase 1 priority: pick T-2026-05-08-T038 first (Aporia-seeded P1
classification ticket). Doc-only; produces input for Phase 2.

Phase 2 priority: after T038 lands and James acknowledges, OPEN A
FULL CONTRACT-CHANGE WINDOW for the 5-tier meta-primitive design.
Do NOT begin meta-primitive implementation in the regular loop —
this needs an explicit pause/resume per the contract-lock discipline.

Phase 3: in parallel with Phases 1-2, drain the test-infrastructure
P2 pile (T016/T017/T019/T022/T031-T037) as normal loop pickup. These
are within file ownership, no contract change needed.

The 8 P1 capability-gap tickets (homotopy, BlockDesign,
SymbolicLaurentPolynomial, ArityGradedOperationFamily, finite-group
rep, M⟨3⟩ MM, optimal contraction order, tensor isomorphism, plus
Tier-B fire-41-001, Tier-D fire-42/43-001, Tier-E fire-44-001) STAY
BLOCKED in the regular loop. They get addressed in the Phase 2
meta-window, not as one-offs.
```

---

## Decision 3 — Ergon next sequence

Ergon's queue is sparse: 1 OPEN (E009 tensor probe-shape audit). Plus 1 ABLE-TO-ADVANCE (E001 eval-protocol fix, superseded by E006). Plus the Aporia-filed `T-2026-05-07-A001` P1 flag noting that **E007 (single-fact decomposition wrapper) hasn't shipped yet**.

### Phase 1 — Ship E007 FIRST (not E009)

Charon's 6-fire arc proved E007 is a free win that gates accurate v1.0 baseline measurement. Without it, Learner-Tester probes measure base-Qwen against a degraded prompt format, and any v1.0 training will be measured against the wrong null. The Aporia A001 ticket already flags this.

E007 is doc-only-prep + a small inference-time wrapper; ~1-2 fires of work within file ownership. No contract change.

### Phase 2 — E009 tensor probe-shape audit

After E007 lands, pick up E009. This is doc-only:
- For each entry in `aporia/mathematics/tensor_open_problems_v1.md` with computational hooks, design a Learner-Tester probe template
- Classify probe-shaped vs too-specialist using the calibration-axis hypothesis (canonicality + era + specificity from `SESSION_SYNTHESIS_2026-05-07.md`)
- Cross-reference with `learner_known_correct_v1.json` and `learner_known_blind_spots_v1.json` to predict tier landing per problem

E009 feeds Techne's T038 classification AND v1.0 corpus design. ~1-2 fires of work.

### Phase 3 — Defer training runs

Do NOT start any new training runs until Techne's contract-change window settles. The KillVector v2 schema may shift if the meta-primitive design pulls KillVector into the equivalence-class abstraction. Training against soon-stale schema is throwaway work.

### Suggested addendum to Ergon restart prompt

Paste this BEFORE step 1 of the canonical Ergon loop prompt:

```
## First fire after 2026-05-09 restart

Read pivot/restart_decisions_2026-05-09.md before step 1.

Phase 1 priority: ship T-2026-05-07-E007 (single-fact decomposition
prompt protocol wrapper). Per Aporia ticket T-2026-05-07-A001, this
hasn't shipped and is gating accurate v1.0 baseline measurement.
Charon's 6-fire arc proved it's a free win.

Phase 2 priority: after E007 lands, pick T-2026-05-08-E009 (tensor
probe-shape audit). Doc-only; feeds Techne T038 + v1.0 corpus design.

Phase 3: NO new training runs until Techne's meta-primitive contract
window settles. KillVector v2 schema may shift; training against
soon-stale schema is throwaway work.

After E007 + E009 both land, the loop is saturated against current
inputs. Subsequent fires likely run quiet-tick mode per HARD-2
discipline (rejecting drift toward proactive busywork) until either
Learner-Tester surfaces new tickets or Techne's window settles.
```

---

## Coupled effects across the 3 decisions

- **Substrate-Tester pivot (Decision 1)** writes test-suite skeletons that **Techne's Phase 2 meta-primitives (Decision 2)** must satisfy. Tester drives spec; producer satisfies spec.
- **Ergon's E009 (Decision 3 Phase 2)** feeds **Techne's T038 (Decision 2 Phase 1)** with which tensor problems the Learner can engage with — useful for prioritizing which catalog entries become primitive-design exemplars.
- **Today's Gemini 20 deep-research dispatch** (separate doc: `aporia/docs/gemini_tensor_priority_dispatch_2026-05-09.md`) directly supplies all three above with literature backing for tensor catalog entries.

The four artifacts (this doc + Gemini dispatch + 2 producer addenda) are the restart payload.

— Aporia, 2026-05-09
