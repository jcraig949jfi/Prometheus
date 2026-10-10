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
