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

### E-7 The depth-1 wall under energy economies is newborn starvation -- HOLDS (CONFIRM)
Graph: X-ERROR-THRESHOLD (no dose effect; failure is per-cell) -> X-ENERGY-INHERIT -> C-ENERGY.
An endogenous newborn starts with energy 0, and energy-economy pressures cap its slice at
its energy, so it cannot afford its own copy: the seeded copier replicates once and stops.
A conserved half-energy transfer at birth: **CONFIRMED on 40 fresh cells** - child
replication 20/40 vs 4/40, sign p = 7.2e-5. My declared side-prediction that
RESOURCE_GATED would not respond was **falsified** (2 -> 6 of 12). This is directive
hypothesis (d), "a first faithful child that immediately dies", in mechanical form, and
the same depth-1 wall the 72-hour record showed. Evidence:
`campaigns/c9x-explore-2026-09-24/c_energy_confirm/`.

### E-8 Spontaneous non-pair heredity: the discovery barrier is encoding length -- HOLDS (CONFIRM)
Graph: X-SPONTANEOUS (CLEAN_NULL, 0/47 with every confirmed barrier relieved) -> X-NEARMISS
(near-misses were slot residue: no partial copying exists) -> X-DENSE-OPS (INVALID: VM module
leaked across reused pool workers, control contaminated; preserved) -> X-DENSE-OPS-R (23/47 vs
0/47) -> C-DENSE. In the permissive FREE non-pair world (in-place search, free self-location,
energy inheritance), giving ALLOC/LDIR/BIRTH ADDITIONAL 1-byte encodings (semantics
unchanged, no program supplied) yields evidence-backed replication from random bytes:
**CONFIRMED 13/40 vs 0/40 fresh cells, Fisher p = 3.8e-5** (depth >= 2 in 4; max 5). The
remaining probability mass is consumed by assembling a 6-byte ordered op chain; at 3 bytes it
is found. Scope: this permissive world; which relieved barriers remain necessary is
X-DENSE-ABLATE. Evidence: `campaigns/c9x-explore-2026-09-24/c_dense_confirm/`.
**Ablations under dense encodings (X-DENSE-ABLATE -> C-ABLATE, 40 fresh cells, frozen):** free
self-location is NECESSARY (replication cells 15 -> 1, p = 6.1e-5) and in-place search is
NECESSARY (15 -> 6, p = 0.0059) - CONFIRMED. The exploratory claim that energy inheritance
matters for depth in SPONTANEOUS replicators did NOT confirm (depth >= 2: 3 vs 3); E-7
(seeded copier) is unaffected.

### E-9 Cycle 9 outcome
C9 (frozen, protocol 5819bc6d; 1,200/1,200 runs; audit PASS 21/21). Frozen verdicts stand in
`observatory/REPORT_C9.md`; mining classified them (`C9_OUTCOME_AND_ADDENDUM.md`):
- **H1 -- INVALID in C9 (C9-D16)**: `world.Runner` never passed output_gate/cue_cost into the
  task spec; all four arms were one experiment (identical to the last decimal). Repaired and
  rerun as **C9-H1R** (fresh seeds, rule unchanged, fail-on-old-code gate PASS):
  **COST_INTERACTION_ONLY** -- I = +0.20, M = -0.10. Gating the answer on cue consumption abolishes
  competence when consuming the cue costs instructions (0.000 vs 0.200; crossings 0 vs 11.7%)
  and is harmless when the cue is free (0.197 vs 0.197). The cycle-8 answer-before-read
  obstruction is the price of reading the cue, not the ordering itself.
  Transplanted (EXPLORE) to all 4 other transforms (I = +0.20..+0.34; gate+VM competence 0.000
  everywhere; positive control: a correct reader scores identically under the gate, so the
  zeros are evolutionary). Mechanism (EXPLORE): ungated competence is carried entirely by
  answer-before-read guessers and no reader ever evolves; the gate removes the guessers and
  paid reading stays rare and weak (my literal flat-landscape prediction failed: 3.8% weak
  readers exist).
- **H2 -- REPLICATION_EVENTS_WITHOUT_PROPAGATION** (both authorship readings); WEAK_SIGNAL
  concentrated in one specimen, `7ae3f9c1437c8000`: implanted genome reaches depth >= 5 in 4/16
  seeds, random bytes 0/16, in situ 0/16.
- **H3 -- NOT_DEMONSTRATED** (R3 material certificates 1/1/0 of 64): crossings are frequent in
  one cell but made of hard-niche material; the easy niche does not raise them.

### E-10 The recombination splice prevents runaway pair-tape heredity -- HOLDS (CONFIRM)
Graph: X-H2-TERMINATION (causal children overwritten a median 3 epochs after birth) ->
X-H2-NORECOMB -> C-NORECOMB (threshold endpoint NOT confirmed, 5/48 vs 5/48) -> X-RUNAWAY
(runaways are population-wide copying ecologies: 70-97% of organisms descend through P-11
copies, ~75 causal copies/epoch for 1,800+ epochs, the implanted sequence itself lost) ->
C-RUNAWAY. **CONFIRMED on 150 fresh seeds per arm:** runaway causal heredity (P-11 depth >= 20)
in 7/150 implants with the world's RECOMBINATION splice off vs 0/150 with it on, Fisher
p = 0.0073; max depth 549 vs 13. The operator that manufactured ~88% of the predecessor's
"replicators" (Z80A-D05) is the operator that prevents real ones from running away.
Scope: specimen 7ae3's cell, single founder. Evidence:
`campaigns/c9x-explore-2026-09-24/c_runaway_confirm/`.

Follow-ups (EXPLORE, hypotheses only): X-RUNAWAY-TRANSPLANT (0/7 other specimens run away);
X-STATE / X-SUFFICIENCY (runaway copies are genome-sufficient, but so are stalled seeds' copies
- sufficiency does not separate them; scale does: 3,901-13,298 P-11 copies by epoch 200 vs
<= 31); X-CRITICAL-MASS (**WEAK_SIGNAL**: 4 founders vs 1, runaways 9/64 vs 0/64, depth >= 5
32/64 vs 8/64, max depth 385 vs 10; the declared SIGNAL bar of 10 runaways missed by one).
**C-CRITICAL-MASS CONFIRMED (frozen at e2bcf6e2b, 80 fresh seeds per arm):** 4 founders vs 1
raise P-11 depth >= 5 from 5/80 to 41/80 (Fisher p = 8e-11; secondary runaways 15/80 vs 2/80,
p = 7e-4). Pair-tape causal heredity in this cell is **establishment-limited**. Whether founders
are superadditive (a true critical mass) is NOT yet claimed: post hoc, k=4 exceeds the
independent-founders prediction (41 vs 18), and X-DOSE-CURVE tests it by declared LRT.
**X-DOSE-CURVE (EXPLORE, CLEAN_NULL): founders are independent lottery tickets.** Over k = 1, 2,
4, 8 (64 seeds each) the 1-parameter model s(k) = 1-(1-p)^k with p = 0.13 fits (LRT p = 0.42;
runaways p = 0.57). No critical mass: the post-hoc excess was a noisy single-founder rate.
X-TICKET (EXPLORE, WEAK_SIGNAL): the lottery is decided in ~12 epochs. Of 118 losing tickets,
49 lose the causal lineage by epoch 5 (36 at epoch 1) and 69 keep it alive but stop copying (37
never copy; the rest stop by epoch 11). Even 6 of 10 depth >= 5 "wins" are early bursts that stop
by epoch 12; only the runaways keep copying. The dominant loss is cessation, not extinction.
X-DECAY (WEAK_SIGNAL): in-place mutation is a minor factor (wins 6 -> 8/64 with it off, p = 0.39).
X-STALL (SIGNAL): at epoch 100, 177/192 live lineage members cannot copy even from a fresh state,
where the founder genome passes 166/192 in the same contexts: stalled lineages are genomically
STERILE. P-11 certifies a causal rebuild of the victim half, not a fertile child. When sterility
arises (at birth, or by accumulated mutation) is under test (X-STERILE).
X-STERILE (CLEAN_NULL on copy error): children are FERTILE at birth (75-80%). X-STALL-F0 (SIGNAL):
with in-place mutation OFF, 187/192 members are still sterile at epoch 100; 57% of their
interactions change their genome (~5.5 bytes) because the pair tape writes BOTH halves back after
every interaction - the member's own writes and its partner's (no change without a write). This
tape-write EROSION is a ~5%/byte/epoch mutation, ~25x the nominal rate. Under test: X-ATOMIC.
X-ATOMIC (EXPLORE, SIGNAL): making write-back atomic (a half changes only by an accepted copy, plus
nominal mutation) raises runaways from 3/64 to 36/64 (p = 4e-11) and copy duration from 4 to 38
epochs. Under CONFIRM: C-ATOMIC (fresh 7ae3 seeds, and generality over the other 15 specimens).
**C-ATOMIC C1 CONFIRMED (frozen at the C-ATOMIC freeze commit, 80 fresh seeds per arm):** with
atomic write-back, runaway causal heredity in 46/80 vs 1/80 (Fisher p = 4e-17; depth >= 5 49 vs 9).
**Tape-write erosion is what stops pair-tape heredity in 7ae3's cell (splice off).** C2
(generality over the other 15 panel specimens) is **NOT CONFIRMED**: 1/120 vs 0/120 runaways; 13 of 15
specimens reach depth 5 in neither arm. Scope of the confirmed claim: 7ae3's cell. Post hoc, the
other donors rarely make even one causal copy (36/120 vs 9/120 runs with any), so erosion is the
barrier only once copying starts. Localization: X-DONOR-RATE.
X-DONOR-RATE (SIGNAL): fresh-state P-11 pass rate 7ae3 0.96, cb7f and 4931 0.29, twelve donors 0.0;
donor copy competence is the first barrier, erosion the second. X-DONOR-SWAP (EXPLORE, WEAK_SIGNAL):
7ae3's genome implanted into the 11 eligible foreign cells (ATOMIC, 8 seeds each) runs away in 3 of 11
(ffa6 4/8, 9cba 1/8, e160 1/8; pooled 6/88) vs its own cell 3/8; the declared SIGNAL bar was 4 cells.
The genome's fresh-state assay rate is 0.955 only in 7ae3 and ffa6 (which differ only in representation and
structure) and 0.0 in the ten other cells: **competence is a property of genome x cell, not of the genome.**
Post hoc (hypothesis only): 9cba and e160 ran away although the founder's assay rate there is 0, so descendants
can acquire competence the founder lacks.
**X-SWAP-ORIGIN (CLEAN_NULL) withdraws that post hoc:** replayed with founder causal-lineage tracking, the 9cba and
e160 runaways are NATIVE (founder depth 8 and 1 vs world depth 120 and 110); in ffa6 2 of 4 are founder-rooted.
**Scope note (endpoint):** `max_causal_replication_depth` is WORLD-level. In 7ae3's own cell the world depth far
exceeds the founder lineage's depth in 2 of 3 runaways (382 vs 71, 386 vs 27). C-RUNAWAY, C-CRITICAL-MASS and
C-ATOMIC C1 are therefore claims about heredity in the cell carrying the implant, not about the implant's own
lineage, until audited on a founder-rooted endpoint (X-ROOT-AUDIT, for C-ATOMIC C1).
**X-ROOT-AUDIT (WEAK_SIGNAL):** on the founder-rooted endpoint C-ATOMIC C1 is 12/80 vs 0/80 (p = 1.6e-4, gap 0.15;
C1's 0.25 effect bar missed). 34 of the 46 ATOMIC runaways are carried by lineages outside the founder's causal
lineage. The frozen C1 verdict stands for its declared world-level endpoint; the reading that erosion stops the
IMPLANT's heredity is supported only at 12/80. Missing null under test: ATOMIC without the genome (X-ATOMIC-RANDOM).
**X-ATOMIC-RANDOM (SIGNAL) reverses that qualification:** with a random 64-byte implant in place of the genome, ATOMIC
gives 0/80 runaways vs 46/80 (p = 1.3e-18), and in every genome runaway 100% of the final population carries the
founder's ancestry marker. The runaways ARE the implant's descendants; the P-11-certified causal chain from the
founder breaks at uncertified births, so founder causal depth undercounts the lineage. C-ATOMIC C1 reads as stated.
**Correction to X-SWAP-ORIGIN:** its NATIVE labels mean 'outside the certified causal lineage', not native ancestry;
the random implant gave 0/8 runaways in 9cba and e160 too. The withdrawn post hoc is reopened, under test in
X-SWAP-ANCESTRY. Open instrument question: which births break certification, and how often.
**X-SWAP-ANCESTRY (SIGNAL):** all five foreign runaways are founder-descended (anc0 share 0.99-1.0), including
9cba and e160 where the founder genome cannot copy from a fresh state. Exploratory (one run per cell). Under
CONFIRM: C-SWAP-ACQUIRE (240 fresh seeds per arm vs random implant). Mechanism under test: X-ACQUIRE.
**C-SWAP-ACQUIRE NOT CONFIRMED** (frozen at 82b6caeb3): 9/240 vs 0/240 founder-descended runaways, p = 0.0018; the
rule needed 10 vs 0. The claim is not made. X-ACQUIRE (WEAK_SIGNAL): 9-15% (lower bound) of the runaway populations
carry genomes that copy from a fresh state where the founder cannot. **Caveat on every anc-based statement above:** the
most frequent descendant genomes differ from the founder at 58-62 of 64 bytes. anc == 0 passes through overwrite
events, so 'founder-descended' may mean slot lineage, not inherited content; byte-level provenance (z8taint) is next.
**X-CONTENT (WEAK_SIGNAL) answers it:** in anc-descended runaway populations only a minority of bytes is founder material
(z8taint, median 13% in 7ae3's cell, 25% in 9cba/e160; anc0 share ~1.0 everywhere), and in 17 of 19 populations no organism
is even half founder bytes. **Every 'founder-descended' statement above (X-ATOMIC-RANDOM, X-SWAP-ANCESTRY, C-SWAP-ACQUIRE's
endpoint) is lineage descent, not content inheritance.** What IS required is the genome at the start (random implant 0/80,
0/240). Where the surviving founder bytes sit: X-CORE.
X-CORE (WEAK_SIGNAL; the declared contiguous-core rule failed): post hoc, in all 5 own-cell runaways the founder bytes kept by
>= 80% of the population include exactly the two world-op instructions, ED 32 (OP_SELF, positions 23-24) and ED B0 (LDIR,
52-53), with most other bytes turned over. Hypothesis only; under CONFIRM in C-CORE (64 fresh seeds).
**C-CORE CONFIRMED (frozen at 1c982e7e7, 64 fresh seeds):** in 7ae3's cell with atomic write-back, runaway pair-tape
heredity conserves the founder's two world-op instructions as MATERIAL -- OP_SELF (ED 32, positions 23-24) and LDIR
(ED B0, 52-53) -- and little else: 17/27 runaways meet the frozen CORE4-and-SPECIFIC endpoint (bar 60%); position 23 is
conserved in 27/27, 52 in 23/27, and no other position in more than 13/27. What is inherited in a runaway is the
self-location and copy instructions; the rest of the founder is replaced. Scope: 7ae3's cell, ATOMIC, single founder;
thin margin over the bar.
Scope: specimen 7ae3's cell, splice off. Evidence: `campaigns/c9x-explore-2026-09-24/c_critical_mass/`.

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
9. **An intervention must be tested at the measurement, not only at the mechanism.** C9-D16:
   the H1 gate worked in the VM and in the task code, and was never handed from the world to
   the task; four arms were one experiment. Identical arms are a defect signature, not a null.
10. **A swapped module in a reused worker leaks.** X-DENSE-OPS: set every run's configuration
    explicitly, one job per process when modules are swapped.
11. **Before building a mechanism on a measurement, reproduce the discrepancy with the real
    inputs.** X-POSITION "showed" copying needs register state; a captured real event with
    fresh registers passed. The cause was partner sabotage in the assay draw. Withdrawn.
12. **A baseline plugged in from a small arm can manufacture an interaction.** C-CRITICAL-MASS
    k=4 "beat" the independent-founders prediction at p = 1e-6, using p1 = 5/80 as if exact. A
    declared dose curve fitting p1 jointly (X-DOSE-CURVE) found no excess (LRT p = 0.42). Fit
    the null model's parameters on all arms before calling anything superadditive.
