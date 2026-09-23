# Nestor findings ledger

Currency: 2026-09-23. One row per finding that survived adjudication or that
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

### A-1 Spontaneous replication from random bytes -- NARROWED, twice

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

### A-4 Endogenous-only accessibility -- OPEN, n = 1

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
