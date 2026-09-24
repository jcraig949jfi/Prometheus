# Nestor findings ledger

Currency: 2026-09-24 (section E added by the S1-S4 pass). One row per finding that survived adjudication or that
corrected a claim. Newest campaign first. Every entry names where the evidence
lives so a fresh context can verify rather than trust this file.

Status vocabulary: **HOLDS** (adjudicated, evidence-backed), **NARROWED** (true but
smaller than first stated), **WITHDRAWN** (claimed then refuted), **OPEN** (measured,
unexplained), **DEFECT** (an instrument fault, recorded not silently patched).

---

## A. Z80 x Atlas 72-hour campaign (`campaigns/z80atlas-2026-09-19`)

Frozen 2026-09-22. 23,471 runs, 0 failed, 0 voided, 20,638 families, grammar
`570c8037ccf4f86d`. Evidence: `observatory/PACKET.json`, `observatory/ADJUDICATION.json`,
`REPORT.html` revision 2, `AUDIT_RECEIPT.json`.

### A-1 Spontaneous replication from random bytes -- NARROWED, three times (third: E-3)

1,031 randomly initialised unseeded populations produced at least one birth backed by
evidence that the organism placed the child's bytes, fidelity 0.906 to 0.990. All 1,031
adjudicate ADMISSIBLE.

Two narrowings, both found after the first report:

- **Events are not lineages.** Reconstructed ancestry gives maximum chain depth 1 in
  **911 of 1,031** runs: one parent, several children, no grandchild. Depth >= 2 in 120,
  depth 3 in 9. No admissible run exceeded the 400-event lineage tail, so these depths
  are exact, not floors. Event counts are far more generous (>= 2: 952, >= 3: 872,
  >= 10: 308) because one parent replicating repeatedly inflates events without
  extending a lineage.
- **C9-D01: zero reproduction diversity.** Every one of the 1,031 is `PAIR_EXECUTION`.
  Not a majority -- all of them, with zero from `ENDOGENOUS_COPY`,
  `ENDOGENOUS_PARTIAL`, `CONSTRUCTIVE`, `OVERWRITE` or `EXTERNAL`. Pair-tape
  replication is detected by a different code path from the ALLOC/BIRTH evidence gate:
  a tape half counts as replicated when the donor wrote at least 25% of it.

So the honest statement is: *in the one physics where two organisms share a tape, one
half overwrites the other at high fidelity, and it rarely propagates.* This is the
finding that generated the next campaign's central question.

### A-2 Matched-pair effects -- HOLDS

10,741 pairs, all Hamming distance 1, and in every pair the single differing factor is
the declared control axis, so the grammar's repair path never produced an impure pair.
Recomputation from the index reproduces the packet exactly across all 28 axes.
Excluding impure pairs changes nothing because there are none.

Effect is experiment minus control and the axis label reads experiment then control, so
a positive value means the LEFT level scored higher.

| axis | pairs | mean d | higher |
|---|---|---|---|
| pressure EXPLICIT_FITNESS -> NONE_IMPLICIT | 513 | +0.3036 | EXPLICIT_FITNESS |
| reproduction PAIR_EXECUTION -> EXTERNAL | 2258 | -0.1197 | EXTERNAL |
| read_order ANSWER_BEFORE_READ -> FORCED_READ | 334 | +0.1029 | ANSWER_BEFORE_READ |
| read_order FORCED_READ -> ANSWER_BEFORE_READ | 304 | -0.0687 | ANSWER_BEFORE_READ |

### A-3 The cycle-8 read-order discrepancy -- OPEN

Both read-order rows are independent pair sets and both favour `ANSWER_BEFORE_READ`.
This campaign does **not** reproduce a forced-read advantage.

Also **WITHDRAWN**: the claim that cycle 8 established one. Cycle 8 established the
answer-before-read obstruction; its successor worlds did not cross, and forcing the ask
read was a proposed continuation, never a result. The first report misattributed a
proposal as a finding.

Further, `FORCED_READ` is not a read-order change at all: `tasks.episodes()` sets
`base = v XOR key` and passes a three-element input vector, so the two arms score
different targets. Cycle-9 H1 replaces it with a true same-task intervention.

### A-4 Endogenous-only accessibility -- WITHDRAWN (see E-4: unmatched control, non-reproducing population)

One ADMISSIBLE instance, `64dea50f417efb02-s1203-tL-a0`, final held 1.0 against a
matched external control at 0.0. Of the other 64 instances, 50 are below threshold at
final state and 14 have the exogenous control finishing ahead.

Suspicion recorded: in smoke the endogenous arm of this cell ran 0.62 s against the
external arm's 2.46 s at equal epochs, which may mean early extinction rather than
competence. Cycle-9 H4 decomposes it into four blocks.

### A-5 Reservoir stepping stones -- WITHDRAWN as unanswerable from this record

All 124 reservoir flags inadmissible in two exact groups: 117 seeded instruments, 7
exogenous controls. Zero weak, so no near misses.

The claim that this was "answerable from per-run lineage records" was itself wrong and
is withdrawn. The predecessor keeps the last 400 lineage events, thinned to 50 under
disk pressure, stores only the parent's niche at the birth instant, and counts
migrations without logging them. A lineage that migrated between two births leaves no
trace of having done so.

### A-6 First-replication timing identifies nothing -- WITHDRAWN

The inference that the epoch range implies no sharp accessibility cliff is removed. The
true range is 0 to 3,946 across two tiers with different epoch budgets (979 at L, 52 at
M) and 35 distinct reproduction/structure/representation combinations.

### A-7 Campaign-layer defects -- DEFECT, recorded not patched in flight

| id | defect |
|---|---|
| Z80A-D01 | flags mix a historical crossing event with a final-state measurement |
| Z80A-D02 | the reservoir flag never checks the reservoir contributed |
| Z80A-D03 | the index whitelist omits the replication evidence; the first adjudicator read it there and wrongly declared every spontaneity flag inadmissible |

---

## B. Reporting-integrity findings (`REPORT.html` rev 1 -> rev 2)

Four defects, one root cause: **a human-readable summary was sourced from another
human-readable summary instead of from the machine-readable record.**

| id | defect |
|---|---|
| R-01 | sign inversion in two headline effects; the prose stated both backwards |
| R-02 | named a run that adjudicates WEAK as the sole admissible instance, taken from the preregistered SPECIALS stream, which carries no verdict |
| R-03 | categorical claims the record cannot support (reservoir answerability, accessibility cliff) |
| R-04 | effect table showed 24 of 28 axes, inherited from what the packet happened to print |

Repair: `report_audit.py` recomputes every load-bearing number from the record and
verifies the claims the report declares about itself; `test_report_audit.py` reinjects
twelve defects and requires each to be caught. 40 checks, 0 failed.

### B-1 C9-D03 -- the audit receipt certified a deleted temp file

`report_audit.py` wrote its receipt next to itself rather than next to the report it
audited, so the negative-control test -- which audits mutated copies in a temp directory
-- overwrote the real receipt with the last mutation's FAIL. The committed receipt named
a file that no longer existed. Same failure mode as R-01 through R-04, one level up: a
record produced by the right process, pointing at the wrong object. Fixed at the cause
in `b05a34f1b`.

---

## C. Cycle-9 repair pass (`campaigns/z80atlas-verify-2026-09-22`)

Repair commit `f13a563b4`. NOT FROZEN, NOT LAUNCHED.

### C-1 Six substrate defects found by reading, all repaired

| repair | defect in the predecessor |
|---|---|
| P-1 | migration counted, never logged; lineage a 400-event tail; only the parent's niche at birth stored. No ancestry certificate constructible |
| P-2 | every birth is a lineage edge regardless of whether copying occurred, so ordinary descent inflates apparent lineage depth |
| P-3 | `crossed` historical beside `held_max` final-state, and flags read one as evidence for the other |
| P-8 | `run()` calls `_place(g, anc)` whose niche defaults to 0, so the entire initial population starts in niche 0. Under `NICHES_ISOLATED` three niches can never be filled; under `RESERVOIR` every organism starts in the easy niche |
| P-9 | `_env_spec_for()` returns the coevolution spec and never calls the niche modifier, so `COEVO_ENV` silently bypasses the reservoir's easy niche. The sole A-4 instance sits in a `COEVO_ENV` cell |
| P-10 | `ENV_MIG` gates migration on `env_difficulty(niche) < 0.5`, but that function returns 1.0 for every structure except `RESERVOIR`, so the gate can never fire and the factor is semantically inert |

### C-2 VM equivalence under the H1 gate -- HOLDS

With the output gate unrestricted the repaired VM is bit-identical to the predecessor:
400 random programs compared on outputs, op count, input reads and final arena bytes,
zero differences.

### C-3 C9-D02 -- P-10 and the H2 specimen panel collide

177 of the 1,031 admissible specimens sit in `ENV_MIG` cells and cannot be instantiated
once `ENV_MIG` is removed. They are excluded from the panel rather than repaired into a
neighbouring cell, which would make a specimen a different experiment from the one it
was selected for. 854 candidates remain.

### C-4 Gate state

All five gates exit 0: 18 checks on the substrate repairs with 5 injected defects
caught, 8 on the reservoir flag, 9 on index-only adjudication, 18 on bundle integrity
with 4 injected defects caught, 15 on the report audit. Calibration 10 of 10 in 8.8 s.
Manifest 252 bundles / 752 runs, 0 validation problems, projecting 2.23 wall-hours
against 20.40 usable.

---

## E. S1-S4 pass (`campaigns/z80atlas-forensics-2026-09-23`, 2026-09-23/24)

Forensic replays are a new assay, not retroactive 72-hour evidence. Every replay was checked
field for field against its frozen summary: 256/256 funnel, 1,031/1,031 P-11, 3/3 H4.

### E-1 Non-pair physics never searched -- HOLDS
All 907 FREE-policy random-start runs (ENDOGENOUS_COPY/PARTIAL, CONSTRUCTIVE) produced zero
births; mutation happens only at birth, so those populations never varied. In 192 replays,
114,485 BIRTH calls all had no pending allocation: allocators never declare, declarers never
allocated. OVERWRITE: 656 replayed births, none at fidelity >= 0.90. PAIR_EXECUTION mutates
every organism every epoch. Evidence: `S1A_FUNNEL.md`.

### E-2 P-11 causal-copy criterion -- HOLDS as an instrument
Randomized-victim assay, 3 draws, majority 2; T-P11 14/14; committed `f28e5fd72` before the
1,031 were inspected. C5 is nearly implied by C2 and C4 (decisive in 2 of 7,919 events).

### E-3 The 1,031 under P-11 -- 57 survive
Predecessor criterion: 1,031 admissible (frozen, unchanged). P-11 reassay: **57** (48 under
the literal authorship reading); 69 of 7,919 events causal; max P-11 depth **2** (55 at 1,
2 at 2). Evidence: `S1C_P11_REASSAY.md`.

### E-4 H4 source run -- A-4 WITHDRAWN
`64dea50f417efb02-s1203-tL-a0` had 0 births, 0 deaths, 0 mutations in 4,000 epochs; its held
moves only with COEVO_ENV. The exact matched control (new run, s1203 L) crossed at epoch 48,
before it (636). The 4x runtime is execution and validation-cache cost of a frozen population,
not extinction. Evidence: `H4_AUTOPSY.md`.

### E-5 Defects -- DEFECT, recorded
| id | defect |
|---|---|
| Z80A-D04 | scheduler keeps control_summary per family: 64 of 65 endogenous-reach flags were judged against a control not run for them |
| Z80A-D05 | pair-tape fidelity read after `_mutate`; under RECOMBINATION the splice made the match in 6,287 of 6,547 events |
| C9-D05 | controls.py wrote the freeze artifact CALIBRATION.json by default (fixed: --freeze) |
| C9-D06 | P-6, specimens, smoke depended on gitignored per-run files (Z80A_FROZEN_OBS; P-6 sandboxed) |
| C9-D07 | H4 endogenous arm cannot reproduce, so H4 cannot test accessibility (not enlarged) |
| C9-D08 | rev-B proposed_protocol_hash had no derivation (replaced by proposed_hashes.py) |
| C9-D09 | H3 cells were re-derived from the H2 panel (fixed: pinned) |
| C9-D10 | H2 arm B resolved implant bytes at run time from the predecessor first_replicator (fixed: embedded) |
| C9-D11 | H3 certificate walks non-causal pair edges in RECOMBINATION cells (NOT repaired; operator decision) |
| C9-D12 | H2 bar depth >= 5 has no precedent: max P-11 depth over 1,031 runs is 2 |
| C9-D13 | H3 arm B (NICHES_HIGH_MIG) migrated at 0.08 vs the reservoir's 0.02; "identical migration" was false (fixed as ruled: RESERVOIR, easy niche off) |
| C9-D14 | **validity, open, freeze stopped**: on the pair tape an organism keeps its id while its bytes are replaced (identity to its birth genome 0.97 after 1 epoch, 0.00 by 600, with no lineage event); the H3 certificate follows id, so it certifies identity, not heredity |

### E-6 Non-pair heredity: self-location is the gate, discovery is the barrier -- HOLDS (CONFIRM)
Autonomous-loop chain, 2026-09-24 (graph: X-NONPAIR-SEARCH -> X-NONPAIR-FIDELITY -> X-SELFLOC-FREE
-> X-SELFLOC-SEEDED -> C-SELFLOC). In the FREE non-pair physics, per-epoch in-place mutation
(search) unlocks declared births (0 -> 87) but none carries parent bytes (all 231 fid < 0.06);
free self-location alone still yields no faithful copy (CLEAN_NULL). An IMPLANTED
ALLOC;LDIR;BIRTH copier with free self-location sustains causal lineages; without
self-location it never replicates. **CONFIRMED on fresh cells/seeds under a frozen rule:**
depth >= 3 in 13/36 cells (max 23) vs 0/36, Fisher p = 1.6e-10. Scope: implanted copier
only; says nothing about spontaneous discovery, which remains the barrier.
Evidence: `campaigns/c9x-explore-2026-09-24/c_selfloc_confirm/`.

---

## D. Standing methodological lessons

These generalise beyond either campaign and should survive into any successor.

1. **A guard that cannot fire proves nothing.** Three predecessor flags had conditions
   that could not discriminate. Every test now ships with an injected-defect negative
   control, and a mutation whose target string is absent fails as VACUOUS.
2. **Similarity is not copying.** A 90% byte-identity test called convergence
   replication and fired the campaign's top flag on junk. Heredity detectors must gate
   on bytes the donor actually wrote -- and P-11 now says even that is not enough.
3. **Never source a claim from a summary.** Source it from the machine-readable record,
   and make a test assert the sourcing.
4. **A historical event and a final-state measurement are different quantities.** Keep
   both, name which one each claim reads, and never report one as evidence for the other.
5. **Preserve rather than patch under a freeze.** Editing a flag rule mid-run makes the
   two halves of the record incomparable. Record the defect, adjudicate afterwards with
   rules declared in one place.
6. **Selection on the outcome is easy to do by accident.** Specimen panels, cells and
   thresholds are chosen by a rule that runs before any result exists, and committed.
7. **Measure a copy where it happens.** A heredity detector that reads the genome after the
   world's own variation operator will credit that operator. Z80A-D05 turned 910 of 1,031
   "replicators" into splice artifacts.
8. **A control inherited from a sibling is not a control.** Match seed and tier per run, and
   store the pairing on the run, not on the family (Z80A-D04).
