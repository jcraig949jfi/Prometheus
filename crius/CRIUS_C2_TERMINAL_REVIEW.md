# CRIUS -- Campaign 2 terminal review (Accessibility Frontier)

CRIUS DISPOSITION: CLOSED -- ACCESSIBILITY FRONTIER MAPPED

Seat Crius, instance m2-8d43bbf9, host M2. Round opened 2026-09-23 from the
PARKED state at CRIUS-33; closed 2026-09-23T10:23:47Z (receipt time). Prereg:
`crius/CRIUS_C2_TERMINAL_PREREG.md` (commit cbf30a726, sha256/16
9c8e0855c8d6a719), written before any decisive run. Machine-readable
disposition: `crius/runs/C2_TERMINAL_DISPOSITION.json` (scorer output) and
`crius/runs/C2_TERMINAL_DISPOSITION_RECEIPT.json` (every input fingerprinted).
Cross-rung summary: `crius/runs/C2_SUMMARY.md`. Interim packet:
`roles/Crius/REVIEW_PACKET_C2_TERMINAL_INTERIM_2026-09-23.md`.

## 0. The claim, and what the round tested

Campaign 2 asked whether the reuse mechanism that the world rewards (record a
procedure relative to an argument, retain it, invoke it with a new argument,
compose invocations) is ACCESSIBLE to an evolving population, given a
substrate ladder that makes each chain link cheaper to express:

- C2-A: the C1b substrate (no link local).
- C2-B: typed procedures (PREC_BEGIN/END, PINVOKE h,a) + a substrate-maintained
  calibration artifact.
- C2-C: + PSIM/PMATCH (mental application: composition in the head).
- C2-D: C2-C + recombination donors = population + the frozen PARTS
  (P_REC, P_INV, P_PLAN), never as population members.

Existence was never in doubt at any rung: the block control PROCEDURE_REUSE_C1
and the 64-instruction bytecode control P_REC_INV_PLAN both use the mechanism
and both benefit (gate witnesses E-H). The question was accessibility: does a
gradient exist from ENUMERATE_VM or random initial programs to the mechanism,
under (8+24) mutation-and-selection with segment splice, 300 iterations, on
paired common-random streams with an independent takeover check.

The frozen predictions that decided this round (verbatim in the prereg):

- R4 (rung C): PARTS with transplant have large positive value; seeded and
  recombination searches do NOT assemble PSIM planning in 300 iterations in
  3/3 seeds each.
- R5 (rung D): splice from PARTS donors produces at least one lineage with
  reproducible ACCUMULATED > FRESH and competence kept in >= 1 of 3 seeds.

Disposition rule (prereg s VI): UNPARK -> CONTINUE required ALL of (a) gate C
v2 TRUE, (b) R4 and R5 survive, (c) a selectable recorder/invoker PARTIAL
before complete reuse in >= 2 of 3 seeds of the winning arm, (d) the effect
reproducible on the sealed streams 201-203, (e) ablation removes it and
ARTIFACT transplant beats CODE_ONLY, (f) the content test (synthetic stores
do not reproduce the transplant), (g) no single edit > 8 instructions
accounts for the mechanism. Anything less -> CLOSED.

## 1. Steps I-IV: reconstruction, control separation, instrument audit, gate

**I. Reconstruction** -- `CRIUS_C2_TERMINAL_PREREG.md` s I quotes the rungs,
gates A-H with exact thresholds, R1-R6 verbatim, the meanings of
FRESH/ACCUMULATED/PARTS/typed artifacts/recorder/invoker/the two controls,
the causal claim of F/G and the accessibility claim of E/H, the rung-C
failure of 2026-09-19 verbatim (E 12 pct vs 20 pct on stream 302; H 1/0/1
rich blocks vs 2; F/G pass; C/D never searched; receipts deleted), and the
prior frontier evidence (18 null runs at A/B; PARTS valley at B and cliff at
C; exploit lineages E1-E4).

**II. CRIUS-33 resolved by a declared control separation** (gate version 2,
`crius/gate_c1.py`, `--positive-control` for E/H and `--causal-control` for
F/G). E and H are facts about the WORLD under the rung's substrate and are
witnessed by the block control PROCEDURE_REUSE_C1 (the block channel is a
strict subset of rung C's substrate). F and G are facts about the NEW typed
channel and are witnessed by P_REC_INV_PLAN. The typed control's own E/H are
reported as non-gating diagnostics. No floor changed. Validity fixtures
(`crius/tests/test_c2_terminal.py`): the accessibility control passes E and
TABLE_MEMO_C1 fails it; the causal control passes F and the decorative
P_REC (records, never invokes) fails it; H reads the effective argument;
TABLE_MEMO fails H's transplant clause; allocation is not rewarded; paired
streams are aligned; typed receipts replay; PARTS accounting holds.

**III. Instrument audit** -- one defect found and repaired before the gate
re-ran: the invocation log recorded register R0 as the "argument" for every
block; typed PINVOKE carries its argument in the VM slot `parg`, so the
2026-09-19 H count for the typed control was computed on a loop register.
Repair in `vm.invoke_block` / `artifacts.log_invocation` (commit a3f6a4be0)
with a regression test (args 0..3 logged while R0 is held at 9). Effect:
stream 302 now shows 2 rich blocks for the typed control where the defective
count showed 0; 301/303 still 1. The E failure on 302 was NOT instrumentation:
the typed control genuinely solves 27/50 there (swap-heavy library; its
recorded procedures are start-specific and it has no witness rule) -- a
property of a 64-instruction control, not of the world.

**IV. Rung-C gate v2, clean re-run** (`crius/runs/gate_c2c_v2/`, config
416bbe8b9be34706, world 7c53db874324b532, generator 624728b00fdd3f2f, code
a3f6a4be0): A PASS (QUIT 20.47/17.41/20.48 < ENUMERATE 21.47/19.41/22.48);
B PASS (29/31/28 unsolved, all charged); C PASS; D PASS (TABLE_MEMO replays
0/0/0; NOCAL 0/0/0 of 29 chains); E PASS (ACC 50/49/50 vs FRESH 21/18/22;
reuse_gain 891.7/744.0/897.4 = 61/50/63 pct of FRESH cost, floor 20);
F PASS (ARTIFACT_TRANSPLANT 6/6/6 vs CODE_ONLY 1/1/0 solved; cost
147.5/153.7/152.3 vs 190.5/191.6/193.0); G PASS (ablation == CODE_ONLY);
H PASS (template blocks 3/5/4; rich 2/3/4; TABLE_MEMO FULL 1/1/0 <= CODE
1/1/0). Diagnostics, typed control: E would pass on 301/303 (38 vs 21/22)
and not on 302 (27 vs 22); H would pass on 302 only. C-GATE TRUE.
Rung D's gate v2 (`gate_c2d_v2`, config 7ab056c39e1821fd, code 52c58d0d4)
produced identical witness values (same substrate; only `parts_donors`
differs) and ALL PASS.

## 2. Step V: the decisive C and D searches

18 runs: rungs C and D x arms random / seeded(ENUMERATE_VM) / recombination x
seeds 1-3; 300 iterations each; 7208 candidates per run (129,744 total),
each evaluated on 2 paired streams with a takeover check on a third; the
final population qualified on sealed streams 201-203 with the full A-J
battery; PATH.md (path evidence) and LINEAGE.md per run.

Determinism check: rung D's random and seeded arms reproduce rung C's
byte-for-byte (same best candidate ids per seed: 0ea16407.., 48549100..,
b398c43e.., 4fa36c3f.., 1e4b4964..). The configs differ only in
`parts_donors`, which feeds the recombination arm, so rung D's new
information is its three recombination runs.

### 2.1 Qualification on the sealed streams (all 18 runs)

| run | top1 fitA | fitF | solved A/F | reuse_gain | blocks | invocations | reproducible candidates |
|---|---|---|---|---|---|---|---|
| C random s1/s2/s3 | 0.16 / 0.16 / 2.16 | same | 0/0, 0/0, 2/2 | 0, 0, 5.4 | 0/0/1 | 0 | 0 |
| C seeded s1/s2/s3 | 21.08 / 21.09 / 21.45 | same | 20.7, 20.7, 21.0 (A=F) | 7.3/7.1/7.1 | 1 | 0 | 0 |
| C recomb s1/s2/s3 | 22.10 / 22.45 / 18.05 | same | 21.7, 22.0, 17.7 (A=F) | 7.2 | 1/32/1 | 0/49/0 | 0 |
| D random s1/s2/s3 | (= rung C) | | | | | | 0 |
| D seeded s1/s2/s3 | (= rung C) | | | | | | 0 |
| D recomb s1/s2/s3 | 21.75 / 22.11 / 22.10 | same | 21.3, 21.7, 21.7 (A=F) | 7.2/7.1/7.1 | 1 | 0 | 0 |
| PROCEDURE_REUSE_C1 (control, same streams) | 46.13 | 20.74 | 45.7 / 20.3 | 7315.4 | 5.3 | 74.7 | -- |
| ENUMERATE_VM_C1 (the seed) | 19.74 | 19.74 | 19.3 | 7.2 | 1 | 0 | -- |

"Reproducible" = reuse_gain > 5 pct of FRESH charged cost AND ACC solved >=
FRESH solved on all three sealed streams (the prereg's clause d). Zero
candidates in 18 runs (30 qualified rows per run: top-3, contemporaries,
ancestors). The constant reuse_gain of 7.0-7.3 carried by every
typed-substrate candidate with blocks = 1.0 is the substrate-maintained
calibration object, not an organism-made artifact; the floor is two orders
of magnitude above it.

One row is not exactly A = F: rung D recombination s2 top2/top3 (fitA
22.116, fitF 22.115, fitR 21.782, reuse_gain 86.8, under the floor). The
exploit probe on it (`probe_c4cfc03b70faa9c3.json`): TRANSPLANT = ARTIFACT_only
= CODE_ONLY = ID_ONLY = RECORD_IDS_ONLY at 10/12/13 solved on 201/202/203;
nothing is carried. Its RESET sensitivity is the reset itself costing it,
not retained content.

Two qualified tops invoke blocks with zero effect ("invocation without
content"): rung C seeded s3 top3 (32 blocks, 43 invocations) and rung C
recombination s2 top1 (32 blocks, 49 invocations), both with fitness
identical under ACCUMULATED / FRESH / RESET / SCRAMBLED. The block store is
filled to capacity and invoked; the invoked bodies do nothing the caller
could not do.

### 2.2 Path evidence (PATH.md per run; c2_path.py)

Time to first complete mechanism (recorder + invoker + own invocation +
solved > 22 on the search streams): **None in 18/18 runs**. The strict form
(success_in_block on a chain with reproducible ACC > FRESH) is empty too,
since no candidate reached clause d.

Survival of partial structures in the elite (longest consecutive run of
iterations in which at least one of the top-8 executed the op) and the
selectable-foothold rate (fraction of children NEWLY carrying the op that
improved on their parent, vs. the same fraction for all other edits; coarse,
unpaired):

| run | recorder | invoker | planner | rec-improve | inv-improve | other-improve | splice children | > parent and donor |
|---|---|---|---|---|---|---|---|---|
| C random s1 | 5 | 7 | 28 | 2.0 | 1.0 | 4.8 | 0 | 0 |
| C random s2 | 5 | 12 | 10 | 2.5 | 0.9 | 2.6 | 0 | 0 |
| C random s3 | 28 | 9 | 11 | 12.1 | 18.4 | 15.7 | 0 | 0 |
| C seeded s1 | 6 | 6 | 17 | 5.8 | 12.6 | 21.2 | 0 | 0 |
| C seeded s2 | 5 | 5 | 30 | 7.7 | 11.1 | 24.1 | 0 | 0 |
| C seeded s3 | 2 | 4 | 55 | 16.7 | 16.1 | 23.4 | 0 | 0 |
| C recomb s1 | 84 | 4 | 146 | 19.4 | 34.2 | 31.3 | 2143 | 431 |
| C recomb s2 | 2 | 5 | 4 | 14.9 | 22.0 | 31.8 | 1862 | 403 |
| C recomb s3 | 2 | 1 | 2 | 6.4 | 6.8 | 26.9 | 2182 | 377 |
| D recomb s1 | 1 | 46 | 12 | 26.7 | 12.5 | 30.2 | 2159 | 465 |
| D recomb s2 | 2 | 23 | 3 | 8.8 | 9.2 | 24.8 | 2176 | 353 |
| D recomb s3 | 1 | 6 | 2 | 7.0 | 14.6 | 20.4 | 2244 | 286 |

(D random/seeded rows equal C's.) Children newly carrying a recorder improve
on their parent LESS often than other edits in every one of the 12 distinct
runs; children newly carrying an invoker do so in 10 of 12 (the exceptions,
C random s3 and C recomb s1, are within a few points). Typed ops persist in
the elite as hitchhikers (planner up to 146 iterations in C recomb s1,
recorder 84 there, invoker 46 in D recomb s1) with no fitness consequence.
Splice children exceeding both parent and donor are common (286-465 per
recombination run) and none of them is a mechanism: the unpaired comparison
counts stream luck, which is why clause c is scored below by paired
re-evaluation.

### 2.3 Clause c, scored honestly: paired re-evaluation of every recorder / invoker step

The search's own fitness values are not paired across iterations (a parent
carries fitness from earlier streams) and the takeover check compares the
child with the DISPLACED elite member with ties counting as takeover, so
`c2_terminal.py` re-evaluates every ancestry step of a qualified top whose
edit newly executes a recorder or invoker op, parent vs child, on the same
sealed streams 201-203 under ACCUMULATED, before that lineage's first own
invocation. A step is "selectable" if the child beats the parent on the mean
and on >= 2 of 3 streams.

- Rung C: 13 such steps across the tops of 9 runs; 6 "selectable" -- all at
  +0.0004 to +0.0011 fitness with a solved delta of 0 on every stream.
- Rung D recombination: 6 steps; 3 "selectable" -- +0.001 fitness, 0 solved.
- Base-rate null (same rule applied to 8 ancestry steps per top1 that carry
  NO new typed op): 0-3 of 8 neutral edits also count as "selectable";
  |delta| median 0.0000-0.0007. The typed-op steps sit inside the neutral-edit
  distribution. Clause c is therefore FALSE in every arm (`c_partial_ok`
  false; the literal count is 1 seed per arm at most, never 2).

### 2.4 The PARTS donors at rung D (what R5 actually tested)

PART-fragment splice children per run (P_INV / P_PLAN / P_REC): s1
203/197/182, s2 189/194/209, s3 205/195/197 -- 1,771 children carrying a
fragment of a part. Won the takeover check: s1 15/7/10, s2 9/8/8, s3 1/4/1
(63 of 1,771). Fragment executes the part's own typed op: s1 35/10/3,
s2 21/4/4, s3 7/12/3. Best fitness of any PART child on its search streams:
26.4-28.0 (the seed is ~21.5; the control is ~46).

PART fragments that survived into a final top's ancestry, re-evaluated
paired on the sealed streams:

| run | iteration | donor fragment | instructions | child executes | paired fitness delta (201/202/203) | solved delta |
|---|---|---|---|---|---|---|
| D recomb s1 | 32 | P_INV[22:26] | 4 | no typed op | +0.0003 / +0.0005 / +0.0006 | 0 / 0 / 0 |
| D recomb s2 | 62 | P_INV[7:8] = `CONST R6, 4` | 1 | no typed op | +0.9994 / +1.0005 / +0.0008 | +1 / +1 / 0 |
| D recomb s2 | 64 | P_PLAN[42:47] = MUL, MUL, LT, BRZ, ACT | 5 | PINVOKE (no effect) | 0 / 0 / 0 | 0 / 0 / 0 |
| D recomb s2 | 93 | P_REC[9:16] = MOD, ACT, DIV, MOD, ACT, DIV, MOD | 7 | no typed op | -0.0026 / +0.0008 / +0.0001 | 0 / 0 / 0 |
| D recomb s3 | 50 | P_PLAN[42:45] | 3 | no typed op | +2.03 / -3.08 / -0.99 | +2 / -3 / -1 |

The only fragment that paid was a bare constant; the enumeration scaffold of
P_REC (an ACT/DIV/MOD digit loop, i.e. the same primitive the seed already
has) was neutral; the P_PLAN fragment that made the child execute PINVOKE
had exactly zero effect; the s3 fragment is stream-dependent and net
negative. No retained fragment contains a recorder, invoker or planner op
that executes with an effect. R5 is LOST: no lineage in any seed has
reproducible ACCUMULATED > FRESH with competence kept.

### 2.5 R4

No qualified candidate of rung C's seeded or recombination arm solves a
chain inside an invoked block with reproducible content-bearing ACC > FRESH
(0 candidates reached clause d). R4 SURVIVES -- which is the null, and by the
prereg only R5 could have earned CONTINUE.

### 2.6 The mechanical verdict (`c2_terminal.py`, from receipts)

```
a_gate_C               true
R4_survives            true      R4_hits []
R5_survives            false     R5_hits []
c_partial_seeds_by_arm {c2c/random 1, c2c/recombination 1, c2c/seeded 0,
                        c2d/random 1, c2d/recombination 1, c2d/seeded 0}
c_partial_ok           false
d_repro_candidates     0
e_causal_candidates    0
g_single_large_edit    []
f_content_test         not applicable (no candidate reached e)
disposition            CLOSED -- ACCESSIBILITY FRONTIER MAPPED
```

## 3. Existence vs accessibility (step VI)

EXISTS and is EXECUTABLE by the substrate, at three levels of construction:
the Python block control (46.1 vs 20.7 on the sealed streams, 74.7
invocations per lifetime, reuse_gain 7315); the 64-instruction bytecode
control on the rung's own opset (transplant 6/6/6 vs code-only 1/1/0);
and the PARTS transplant (P_PLAN from scratch -0.057 at 0/10 streams, with
the procedures pre-loaded +16.741; P_REC_INV_PLAN +15.974 at 10/10, 47
edits from P_BASE).

NOT ACCESSIBLE, under the charter's search, at any rung A-D: 36 runs in
total across the ladder (18 at A/B, 18 at C/D), 0 candidates with
reproducible acquired-state value, 0 complete mechanisms, 0 selectable
partials above the neutral-edit null. Rung D was the most favourable
condition the charter allowed (the parts themselves as splice donors) and
the fragments selected were the parts' generic scaffolding, never their
typed links.

## 4. Where the frontier is (the map)

1. The value landscape of the mechanism measured by construction (PARTS,
   same for rungs C and D): recorder alone -0.001 (0/10 streams), invoker
   alone -0.002 (0/10), recorder+invoker +1.138 (7/10, +1.1 tasks) at 26
   edits, planner alone -0.057 (0/10) at 41 edits, everything +15.974
   (10/10) at 47 edits. A one-link valley at B and a cliff at C.
2. What selection does with the links: recorder = neutral hitchhiker
   (persists up to 84-103 iterations in an elite, never pays); invoker =
   mildly deleterious on arrival; planner = neutral. Children that newly
   carry a link improve on their parent less often than other edits.
3. What selection does with donated parts: it keeps their constants and
   digit loops and discards or neutralises their typed ops (1 of 5 retained
   fragments paid, a `CONST`).
4. What it finds instead: compressed enumerators (A-D), record-id clocks and
   counters (E1-E4 at A/B; none at C/D), and at C/D the "invocation without
   content" shape -- a full block store invoked dozens of times per lifetime
   with zero effect.
5. The gate's map of what the world rewards is intact and repaired: E/H by
   the block control, F/G by the typed control, TABLE_MEMO and NOCAL fail
   where they must.

## 5. Why closure and not continuation (step VII)

The disposition rule was written before the runs and is met on none of
(b, c, d, e). The forbidden rescue moves (s VIII) are exactly the moves that
could change this: lower the E/H floors, add E2/H2, raise the iteration
budget, seed parts INTO the population, or add a C3 rung. The result is not
a budget shortfall that another 300 iterations would fix -- the same shape
(neutral or deleterious partials, whole-mechanism value only at ~47 edits,
scaffolding kept and links dropped) appears identically at every rung and
in every arm, and the takeover-checked paired streams rule out stream luck.
Further search under this substrate would test search budget, not
accessibility structure, and the charter forbids it.

## 6. What the opposite disposition would have required (step VII)

UNPARK -> CONTINUE needed, in rung D's recombination arm: at least one
lineage in >= 1 seed whose ACCUMULATED beats FRESH on all three sealed
streams by more than 5 pct of the FRESH charged cost with competence kept
(observed: 0 candidates; best under-floor row 86.8 carrying nothing on
probe); whose ARTIFACT transplant is cheaper than CODE_ONLY by 5 pct and
whose ablation removes the gain (never reached); whose synthetic-count
stores do NOT reproduce the transplant (never reached); whose ancestry has a
recorder/invoker step that beats its parent on the sealed streams by more
than neutral edits do, in >= 2 of 3 seeds (observed: 9 steps of +0.001 with
0 solved, inside the neutral null; 1 seed per arm at most); and no single
edit > 8 instructions accounting for the mechanism (moot).

## 7. Instrument and process notes

- Receipts for every run carry `code_dirty_crius: true`; the flag is
  `git status --porcelain -- crius` and was set by the untracked run
  directories being written, not by any modified tracked file (verified: no
  tracked crius file was modified during the round).
- Rung C receipts of 2026-09-19 (searched under a failed gate) were deleted
  then and are not evidence; this round's C receipts were produced under the
  passing gate v2, driver keyed on the gate verdict.
- `c2_summary.py` now prefers the gate v2 receipt when present and prints
  both control names.
- Tests: `crius/tests` 41 passed (39 + 2 scorer tests).
- No world, budget, pressure, fitness or floor changed in this round.

## 8. Forbidden moves not taken

No lowered E/H floors; no E2/H2; no iteration or population increase; no
parts seeded into the population; no C3. The ladder ends at D.
