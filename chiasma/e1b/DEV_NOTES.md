# E1b development notes (dev seeds only; sizing, NOT results)

Seat: Hades[m1-ca525615]. Started 2026-10-10. Claim level: AUTHOR_TESTED.
Nothing here is frozen. Development seeds: 910001-910010 (disjoint from E1's dev seeds
900001-900005 and eval seeds 2187867196-205).

## 0. Why E1b exists

The operator gave no ruling on HADES-10 between 10-07 and 10-10. Under MWO-0004 R1 the
seat took REVISE as the reversible default (journal 2026-10-10). REPORT_E1 s6 named
the first revision: O4L (provenance repair) as the primary subject, a counterfeit
provenance control, a ceiling one variable away from O3, and a world in which no single
global bet wins.

## 1. Code (new, under chiasma/e1b/; the frozen E1 files are imported, not edited)

- world_h3.py: PW-H3, three staged false abstractions Y_j = c_j & f_j with loads
  (ydep, decoy) = (12,4), (8,8), (4,12); m = 24. In C, each exception breaks ONE pair.
- arms.py: O3U (O3, uncapped) and O4LR (O4L whose provenance names a random literal from
  outside the anchor: same entry count, same U bytes, wrong content).
- run.py: E1's runner with the world family passed in. A test checks that it reproduces
  chiasma.runner.run's endpoints AND receipt sha256 on PW-H.
- sweep.py, verdict.py (DRAFT mapping), mutation.py.
- tests/test_e1b.py: 11 known-answer tests. mutation.py: 12 planted one-line defects,
  12 killed on the first pass. This gate has been tried only by its author.

## 2. dev-1 (880 runs, 0.48 CPU core-hours; chiasma/runs/e1b-dev-1/)

Caps: PW-H 600/1000/3000 (as E1). PW-H3 1800/3000/9000. Decision taken on dev seed
910001 before dev-1: PW-H3's P is about 3x PW-H's (1442 vs 481 bytes at the end of F),
so PW-H's caps would leave P alone over budget.

The draft primary (O4L beats O1, O2, O3 on err_CDE) holds in 12/12 cells. O4L beats
O4LR in 12/12. The draft mapping would say PASS / MECHANISM_ATTRIBUTED for both
families. **This would mean little.** Section 3 explains why.

O0 (never consolidates) against O4L, wins out of 10: PW-H3 0/10 in every cap (O0 better
everywhere; median err_CDE 2464 vs 3309-3376); R21 0/10; R11 5/10; R12 9/10.

## 3. FINDING: E1's "compression" operator does not compress

Consolidation is labelled compression (DESIGN_E1 s3: "That compression is where the
false foundation comes from"). Measured property: it makes the positive geometry
LARGER.

| rows | arm | P bytes at end of E (median) | cells | consolidations |
|---|---|---|---|---|
| E1 eval (frozen), R11 | O0 | 304 | 44 | 0 |
| E1 eval (frozen), R11 | O3 | 391 | 56 | 73 |
| E1 eval (frozen), R11 | O4L | 379 | 55 | 57 |
| e1b-dev-1, PW-H3 | O0 | 522 | 68 | 0 |
| e1b-dev-1, PW-H3 | O3 | 1197 | 161 | 216 |
| e1b-dev-1, PW-H3 | O4L | 1335 | 174 | 176 |

Paired, in the frozen E1 evaluation rows at cap 3000: O0's P is smaller than O3's in
30/30 (ratio, seed) pairs, and smaller than O4L's in 30/30. O0's cell count is 44 in
30/30. 44 is exactly the number of true conjunctive terms in a PW-H world (24 ydep+decoy,
11 unrel terms, 3 invalid laws, 6 new). PW-H3 has 75 true terms; O0's median is 68 cells.

Mechanism (from organisms.py, not yet tested in isolation): a cell consolidates after
S_CONS = 6 supporting positives and drops its anchor. A consolidated cell can no longer
be welded (`_on_fn` skips consolidated cells), so it freezes before welding has reduced
it to the true term. Later positives that it does not cover open new cells. Pruning
one implied literal saves 1 byte per cell; the fragmentation costs about 4 bytes per
extra cell. **Consolidation is premature commitment, not compression.**

Consequences:
- E1's verdict (O4 FAIL) stands as measured. Its narrative needs a correction: the
  false foundation in E1 comes from an operator that costs bytes rather than saving
  them, and the no-compression counter-organism O0 is both smaller and, in most cells,
  more accurate. Added as an addendum to REPORT_E1.md (the prereg is not edited).
- O4L's gain is repair of damage that consolidation inflicts itself. "O4L beats O1-O3"
  is therefore not evidence for the charter's question (equal knowledge at lower
  storage/search cost). E1b as drafted in s0 is withdrawn before freezing.
- WT-0 lacked a check that would have caught this: **a compression operator must be
  shown to reduce bytes at equal knowledge on a known-answer world.** Added to the
  E1b plan as a G0 item.

## 4. Revised E1b plan (draft; one variable per contrast)

1. WT-0 addition (G0): on the PW-H known-answer world, report P bytes and cell count
   against the true term count for every arm. An operator labelled compression must
   reach P <= O0's P at equal or lower error, or it is renamed.
2. 2x2 on dev seeds before naming any mechanism: consolidation {freezes (E1),
   does not freeze (prunes, stays weldable)} x provenance repair {off, on}.
3. Primary bar for any compressing arm: O0 (the cheapest counter-organism), not only
   O1-O3. The charter's s7 bar (O1, O2) stays as a co-condition.
4. The real compression lever in the charter is a shared abstraction (one vertex for
   Y = c & f reused by many cells: factoring), not pruning one literal per cell. That is
   a separate variable, tested after (2).
5. The freeze still waits on the G3 first-sight challenge of E1 (requested from Hestia,
   comms #2046).

## 5. dev-2: the 2x2, freeze x repair (240 runs, 0.13 CPU core-hours; chiasma/runs/e1b-dev-2/)

New arms (arms.py): O3W and O4LW. Consolidation prunes the implied literals but the
cell stays weldable, with its pruned premise as the anchor. Tests: 13. Mutants: 14/14
killed (chiasma/runs/e1b-dev-2/MUTATION.txt). Same dev seeds 910001-010; the other
arms' rows are dev-1's.

Wins out of 10 on err_CDE (identical across the caps of a world unless shown):

| world | O3W>O3 | O4L>O3 | O4LW>O3W | O4LW>O4L | O4LW>O0 | O3W>O0 | O4LW>O1 | O4LW>O2 |
|---|---|---|---|---|---|---|---|---|
| H:R21 | 7 | 10 | 10 | 3-4 | 0 | 0 | 10 | 10 |
| H:R11 | 7 | 9 | 9 | 3-4 | 5 | 3 | 10 | 9 |
| H:R12 | 4-5 | 9 | 9 | 2 | 9 | 8 | 10 | 9 |
| H3 | 10 | 10 | 10 | 10 | 1 | 1 | 10 | 10 |

Median err_CDE, PW-H3 cap 1800: O0 2464, O3 3690, O3W 3050, O4L 3376, O4LW 2834.
P bytes, median: end of B, O3W 289 vs O0 313 (PW-H) and 498 vs 546 (PW-H3). End of E:
equal (O3W = O0 in every world). Cell count at end of E: O3W = O0.

Reading (dev, sizing):
1. Freezing is the cause of the extra bytes. Removing it gives O0's geometry exactly.
   On PW-H3 it also costs about 640 errors (O3 vs O3W); on PW-H it costs little.
2. Provenance repair helps independently of freezing (O4LW beats O3W 9-10/10 in every
   world).
3. Neither change beats never compressing where true dependents are common (R21,
   PW-H3). The pre-shock bet survives repair. On mixed loads (PW-H3), O0 beats O4LW
   9/10.
4. Compression's byte saving is about 8-9% of P before the shock and zero after it. No
   cap in E1 or dev forces P out (P is never evicted; over_budget = 0 everywhere), so
   the saving buys nothing. In these worlds, at these caps, the charter's premise ("equal
   knowledge with lower storage cost") is never put under pressure.

## 6. Next variable: a binding budget (draft)

E1b is redrawn around the one condition under which compression can pay: a budget that
the no-compression organism cannot meet without losing knowledge.
- A cap below O0's natural P (sized on dev as fractions of O0's median P at the end of
  B), with ONE P-eviction rule shared by every arm (evict the cell with the lowest
  support, then the oldest).
- Arms: O0, O3W, O4LW, O1, O2 (and O4LR-W, a counterfeit for O4LW, if O4LW wins on dev).
- Primary bar: O0. Charter co-condition: O1 and O2.
- World: PW-H3 primary (mixed loads, no single global bet); PW-H ratios reported.
- Prediction before sizing: compressed arms gain only when the cap is below O0's P and
  above the compressed P (a window of about 8-9% of P). If dev shows that window is
  empty or noise-sized, that is itself the answer: in PW worlds, literal pruning cannot
  pay, and the charter's compression claim needs the factoring lever (DEV_NOTES s4
  item 4).
