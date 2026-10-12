# BEL-48H Window 3 -- Replication reachability and construction pathways

Campaign BEL-48H-2026-10-08, Bellerophon[ubu005-0eb14d49]. Prereg s6 (W3a frozen 4995e8b45; classification
tools/analyze_w3.py committed bdbf8215d before the replays were read) + amendment 2 (independence). Instrument
tools/origin.py: eager change tags (m mutation, s self-construction, u uptake = own code copies PARTNER bytes into its
own tape, v self-move, i inherited at birth), dissection of the event that first made any organism FUNC, per-byte
reversion. Receipts: receipts/W3A_ANALYSIS.json; raw ~/bel48h_runs/w3a.

## 1. Data and replay receipt

W3a = deterministic REPLAY of the 27 W2-H1 runs that reached FUNC (2 workers, 2,348 s active, 0 voids). Every replay
reproduced its W2 end-state hash: 27/27 byte-identical (W3-P3 HOLDS) -- a determinism receipt for the kernel on real
data and an invariance receipt for the origin hook. Independence (amendment 2): the 27 runs come from 21 distinct
initial populations (the four H1 cells share seeds); counts below are per run with the per-seed figure beside them.
DISCOVERY set: these origins were already seen in W2; confirmation on unseen populations is W6.

## 2. Frozen predictions

| id | prediction | result | verdict |
|---|---|---|---|
| W3-P1 | the completing event needs exactly 1 necessary byte change in >= 60% | 18/27 (Wilson 48-81%); steps 0:5, 1:18, 2:1, 3:2, 7:1 | HOLDS |
| W3-P2 | an incremental precursor (partial own-copier) in >= 40% | 5/27 [8-37%]; the pre-event tape copied 0 own bytes in 21/27 | FALSIFIED |
| W3-P3 | replay identity 27/27 | 27/27 | HOLDS |
| W3-P4 | LDIR critical in all; NOP-slide dependence in >= 50% | LDIR 27/27; FUNC lost when zeros become HALT 17/27 | HOLDS |

## 3. How the first replicator arises (21 independent populations)

**Cause of the completing event.** Per run: MUTATION 20, UPTAKE 5, SELF_MOVE 1, SELF_CONSTRUCT 1; none was born
functional once changes are tagged eagerly (the 3 W2 'BORN_ASSEMBLY' first-FUNC tapes were preceded by an in-place
completion the lazy tags had missed). Per distinct seed: mutation only 14, uptake only 3, both (different cells) 2,
self-move 1, self-construction 1.

**Pathway.** SINGLE_STEP_FROM_NOTHING 16, INCREMENTAL 5, ASSEMBLY (uptake) 5, ATOMIC 1. The typical precursor is a
CRYPTIC near-machine: it copies nothing (copy extent 0), carries most of a copy routine, and one change switches it on.
In 19/27 the carrier was copy-born and inherited most of its critical bytes at birth (ASSISTED): other organisms'
imperfect copying assembles the cryptic precursor; a single change completes it. This sharpens the grounding round's
"short ramp ending in a small step": the ramp is mostly not a graded partial copier (W3-P2 falsified) but a non-copying
precursor built by others' copying.

**The machine is tiny and context-dependent.** Minimal critical sets: LD T,n (2 bytes, n in {0x40, 0x41, 0x42, 0xA0})
plus LDIR (0x15), sometimes LDI (0x14) or a 7-byte variant (29 c1 .. 4d .. 34 ed .. 48 15 -- one founder machine
shared by the four runs of seed k = 31). It relies on the zero entry registers (S = 0, C = 0 -> a 256-byte sweep) and,
in 17/27, on neutral filler (zeros executing as NOPs): replacing the zeros with HALT kills it.

**UPTAKE: horizontal assembly of a replicator from material that was not functional where it came from.** In 5 runs
(3 seeds only uptake) the organism's OWN code copied partner bytes into its own tape and thereby became the first
replicator in its world -- so the source arrangement was by definition not a working replicator.
- w2_00345 (ENDOGENOUS_COPY, tick 127): one execution imported 08 a0 .. 15 into positions 4, 5, 10 (LD T,0xA0 ... LDIR);
  each of the three bytes had been made by a different mutation event in other organisms; all three are individually
  necessary (reverting any one kills FUNC). Three scattered mutations, assembled horizontally in one step.
- w2_00040 / w2_00205 (PARTIAL, PAIR): the decisive byte (LDI) was constructed in a partner and taken up next to an
  inherited LD T + LDIR.
- w2_00181 (PAIR, seed k = 31): the organism rearranged its own founder bytes (self-moves) into the 7-byte machine --
  RELOCATION ACTIVATION: the same bytes, inert in one arrangement, become a replicator when moved.
Classification: uptake origins CAUSALLY_CONFIRMED per specimen (reversion of the taken-up bytes kills FUNC in
w2_00345 / w2_00205 / w2_00040); as a population-level route PROVISIONAL (5 runs / 5 seeds; W6 confirmation).

## 4. Answers to the directive's W3 questions (this window's evidence)

- Required transitions: usually ONE decisive change (18/27), on a precursor assembled by others' copying.
- Mutational distance: 1 necessary byte in 18/27; 0 necessary single bytes in 5 (several redundant changes); 2-7 in 4.
- Neutral intermediates: the precursor copies nothing -- the intermediates are reproductively neutral (they do not
  self-copy); whether they were selectively favoured is in the writer-chain output: median share of chain ancestors
  that out-reproduced their contemporaries 0.87-0.90 per cell (W2 reach summary) -- the CARRIER lineages are prolific
  writers, i.e. ecological assistance by productive non-replicating copiers.
- Copying errors that enable replication: yes -- the 19 ASSISTED origins inherit cryptic machines through copying.
- Dependence on LDIR: total (27/27). On permissive NOP-like filler: 17/27.
- Independent origins: 21 populations; distinct machine variants >= 6 (LD T operand 0x40/0x41/0x42/0xA0, LDI-prefixed,
  7-byte).
- Atomic vs incremental: neither a long selectable ramp nor a lucky whole-machine jump; a single-step activation of a
  cryptic, copy-assembled precursor, sometimes by horizontal uptake.

## 5. Limits

Discovery set (seen in W2). FUNC is single-generation (Review B); TRB-chaining and FUNCK are used for persistence. The
history kept per carrier is capped at 40 snapshots. A 'u' byte keeps the founder/novel tag of the moved byte; uptake of
a byte that was itself moved twice inside the partner is attributed to its last move (multi-hop within an execution,
one record per byte across executions).

## 6. Addendum -- W3b (EXPLORATORY; planner 3f5125ec7, chosen after reading W2)

Replay of the 75 W2-H2 runs that reached FUNC in the COPY_AB (60), B (6) and none (8) arms (+1 B with no event):
75/75 byte-identical end states, 0 voids, 3,645 s active. Raw ~/bel48h_runs/w3b; receipts/W3B_ANALYSIS.json.

Why COPY/AB reached FUNC in 61/100 although ENDOGENOUS_COPY abolishes complementation (W2-P5): founder attribution of
the critical bytes of each COPY_AB origin (founder id -> slot -> transplant index) gives A-fragment bytes in 60/60
origins and B bytes in 0/60; 36/60 origins are built from A's bytes ALONE with no new mutation (19 add one mutation,
4 a self-construction). Causes: BORN_ASSEMBLY 23, MUTATION 29, SELF_MOVE 7, SELF_CONSTRUCT 1.

Direct test of the fragment's neighbourhood (one-off computation, scratch, 2026-10-08 ~09:45-10:05Z):
  single-byte SUBSTITUTIONS that make A FUNC:          0 / 16,320   (B: 0 / 16,320)
  single SEGMENT MOVES (copy a <= 16-byte segment of the tape to another offset) that make A FUNC: 8 / 50,512
  (all move A's stored 08 40 data block to the front); B: 0 / 50,512; 30 random 64-byte tapes: 0 / 1,515,360.
EPISTEMIC FAULT-LINE (CAUSALLY_CONFIRMED for this specimen): substitution distance said A was > 1 step from a
replicator; under the physics' own operator (copying segments with offsets) it is 1 step. Mutational-neighbourhood
rulers built on byte substitution (geometry.scan / scan_paired, the historical G4 beneficial-neighbourhood analysis)
cannot see the rearrangement neighbourhood that copy-based physics explores; reachability claims made with them are
lower bounds. B/none origins (14 runs): mutation 12 (incl. 4 incremental), uptake 1, self-move 2 -- the same picture as
the random worlds of W3a, at a lower rate.

## 7. CONFIRMATION on unseen independent populations (W6 block 1, prereg s9, frozen da6ddcd29)

1,200 fresh RANDOM WELL_MIXED runs, ONE distinct seed per run (amendment 2), PARTIAL / PAIR / COPY 400 each; 1,300 runs
in the block with C2; 0 voids; 3.90 h active (6 workers, 14:17 -> 18:11:57Z). 85 independent origins (PARTIAL 36,
PAIR 37, COPY 12). Classification unchanged from W3a (analyze_w3.classify). Receipt receipts/W6B1_ANALYSIS.json.

| id | prediction (from W3a discovery) | result | verdict |
|---|---|---|---|
| C1-P1 | completing event is a MUTATION in >= 50% | 53/85 [51.7, 71.9] | HOLDS |
| C1-P2 | one necessary changed byte in >= 50% of in-place origins | 54/75 [61.0, 80.9] | HOLDS |
| C1-P3 | cryptic precursor (copies 0 own bytes) in >= 60% | 60/85 [60.2, 79.2] | HOLDS |
| C1-P4 | >= 1 reversion-confirmed UPTAKE origin | 13/85 uptake origins, all 13 with individually necessary taken-up bytes | HOLDS |
| C1-P5 | ASSISTED in >= 50% | 56/85 [55.3, 75.1] | HOLDS |
| C1-P6 | LDIR critical in >= 95% | as written (reach summary's lazily detected tape): 77/85 FALSIFIED; corrected to the origin event's own tape: LDIR critical 83/85, the other 2 carry REDUNDANT LDIRs (removing all of them kills FUNC; single knockout cannot see redundancy); LDIR writes the window in 85/85 | FALSIFIED as written (field mismatch, recorded); HOLDS as corrected |

Causes on fresh populations: MUTATION 53, UPTAKE 13, BORN_ASSEMBLY 10, SELF_MOVE 7, SELF_CONSTRUCT 2. Pathways:
SINGLE_STEP_FROM_NOTHING 43, ASSEMBLY 23, INCREMENTAL 13, ATOMIC 6.
Classification upgrade: CL-06 (single-step activation of a copy-assembled cryptic precursor) PROVISIONAL -> REPRODUCED on
85 independent populations; CL-07 (uptake as a route to the first replicator) PROVISIONAL -> REPRODUCED (13/85 = 15%,
each reversion-confirmed). New limit: knockout criticality misses REDUNDANT elements (2/85 machines carry two LDIRs).
