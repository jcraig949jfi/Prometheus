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

## 7. dev-3: binding budget (1120 runs, 0.58 CPU core-hours; chiasma/runs/e1b-dev-3/)

pevict on (arms.py): after N and U, whole cells are evicted (lowest support, then
oldest), the same rule for every arm. Caps sit below O0's natural P: PW-H 240/270/300/330,
PW-H3 420/470/520/570 (O0's median P at the end of B is 313 and 546). One new test
(the cap holds with pevict and is overrun without it, for O0/O1/O3W/O4LW); mutants 15/15
(chiasma/runs/e1b-dev-3/MUTATION.txt).

Wins out of 10 on err_CDE, caps in the order listed:

| world | O3W>O0 | O4LW>O0 | O4LW>O3W | O4LW>O1 |
|---|---|---|---|---|
| R21 240/270/300/330 | 9/6/4/4 | 9/3/0/2 | 1/0/2/7 | 6/8/9/7 |
| R11 240/270/300/330 | 10/7/6/5 | 9/5/3/5 | 0/0/3/8 | 8/9/8/6 |
| R12 240/270/300/330 | 10/10/9/9 | 9/8/8/8 | 1/0/1/4 | 9/8/8/5 |
| H3 420/470/520/570 | 10/9/5/4 | 9/8/2/1 | 2/2/2/5 | 10/10/10/10 |

Median err_CDE O0 / O3W / O4LW at the tightest and loosest caps: R11 8626/7503/8180 and
2146/2241/2355; H3 17396/14223/15176 and 4020/4742/5051.

Reading (dev, sizing):
1. The predicted window exists. Compression (O3W) beats never-compressing (O0) when
   the budget binds, 9-10/10 at the tightest cap in every world. The advantage fades as
   the cap approaches O0's natural P. In R12 (decoys dominate, so dropping f is right)
   it holds at every cap.
2. The window is a regime of heavy loss. At the tightest caps every arm's err_CDE is
   many times its unbounded value. Compression wins by losing less, not by keeping
   knowledge.
3. Provenance repair HURTS under a binding budget. O4LW beats O3W at most 3/10 at the
   three tightest caps of every world. Its provenance bytes and restored literals cost
   cells. The dual mesh's revision machinery is a byte cost that the budget charges for.
4. With no N memory, O1 has more room for P. It wins R12 cap 330 (median 1398, the
   lowest of any arm there).

## 8. Where this leaves CHIASMA's discrete form (dev only; nothing frozen)

| regime | best arm | dual mesh + revision (O4LW) |
|---|---|---|
| unbounded (E1 caps) | O0 (no compression) where true dependents are common; O4LW where decoys dominate | loses to O0 on R21 and PW-H3 |
| binding budget | O3W (compression, no provenance) | loses to O3W at tight caps |

No tested regime has the charter's O4-family arm as the best organism. Each of its
two parts wins somewhere: repair when bytes are free, compression when bytes are
scarce. They do not win together, because repair spends exactly the resource that makes
compression worth having.

What a frozen E1b should test, if it is run (proposal; the freeze waits on G3):
- C1 (unbounded, PW-H3): O0 beats O4LW on err_CDE in at least 8/10 eval seeds at every
  cap. Dev: 9/10 at each cap.
- C2 (binding, every world): O3W beats O0 at the tightest cap. O4LW does NOT beat O3W
  at the tightest two caps.
- Prediction: both confirm. A confirmed pair supports KILL of the discrete O4 design,
  REVISE toward the untested factoring lever (one shared vertex for Y = c & f), or
  both. The operator decides which.

The factoring lever is the one charter mechanism these worlds have not tried. In PW-H3
about 54 cells depend on 3 abstractions. One shared vertex per abstraction would save
a vertex in each dependent cell, against literal pruning's 8-9% of P. It is the only
remaining way for compression to pay without destroying knowledge. Next design item:
HADES-28.

## 9. dev-4: the factoring lever (HADES-28; 480 runs, 0.58 CPU core-hours; chiasma/runs/e1b-dev-4/)

factor.py stores premises with shared abstraction vertices: Re-Pair over the multiset
of premises; a rule costs 3 bytes and is kept only if 4 or more premises use it. It is
LOSSLESS by construction. Predictions, welds and retractions use the flat masks; only
the byte ruler changes. Arms O0F, O3WF, O4LWF are O0, O3W, O4LW with factored storage.

Checks: uncapped endpoints identical to the flat twin (PW-H and PW-H3, all three pairs);
every factored premise expands back to its flat mask (hand set and a full PW-H3 run);
the factored byte ruler matches a hand count. Mutants 19/19 killed. First pass 16/19:
E16 (rules cost nothing) and E19 (substitution into premises that lack one vertex)
SURVIVED, and E17 did not apply. The expansion and hand-count tests were added after
that pass. Six dev-4 receipts were re-run after the factor.py refactor; all six
reproduce byte for byte.

Ceiling before running (dev seed 910001, uncapped): factoring saves 26 bytes of P
before the shock on PW-H (314 -> 288, 8%) and 43 on PW-H3 (548 -> 505), with 4-5 rules.
Y = c & f is two literals, and per-cell overhead (length and support counter) plus the
implication table make up most of P, so there is little shared structure to factor in
PW worlds.

Wins out of 10 on err_CDE under the binding budget (pevict), caps tightest to loosest:

| world | O0F>O0 | O3WF>O3W | O4LWF>O4LW | O4LWF>O3WF |
|---|---|---|---|---|
| R21 240/270/300/330 | 10/10/7/5 | 9/10/8/5 | 10/10/10/6 | 2/0/7/6 |
| R11 240/270/300/330 | 10/9/5/8 | 10/10/4/6 | 9/10/9/8 | 1/0/5/6 |
| R12 240/270/300/330 | 10/10/3/2 | 10/10/2/3 | 10/10/5/6 | 2/0/5/6 |
| H3 420/470/520/570 | 10/10/9/6 | 9/10/9/4 | 10/10/9/9 | 2/1/4/4 |

Reading (dev, sizing):
1. Lossless factoring pays wherever the budget binds hard: 9-10/10 over the flat twin
   at the two tightest caps in every world, for every arm. It is the only compression
   in CHIASMA so far that saves bytes without changing what the organism knows.
2. Its saving is small, so it pays only in the same heavy-loss regime as dev-3.
3. Provenance repair still loses to plain compression where the budget binds hard
   (O4LWF beats O3WF at most 2/10 at the two tightest caps). Factoring does not rescue
   the revision half of the dual mesh.

## 10. Conclusion of the E1b dev series (DEV_NOTES s3-s9; AUTHOR_TESTED, dev seeds)

- E1's "compression" was premature commitment. It enlarged P (s3).
- On PW worlds, every real compression (literal pruning without freezing, lossless
  factoring) saves at most about 8-9% of P. It buys accuracy only when the budget is so
  tight that every organism has lost most of its knowledge.
- Provenance repair, the revision half of the charter's O4, helps only when bytes are
  free. Then the organism that never compresses (O0) is as good or better wherever
  true dependents are common. Repair loses whenever bytes are scarce.
- No discrete CHIASMA arm tested here is best in any regime. The charter's s7
  condition for evolution is not met, and these worlds cannot meet it.

What would have to change for CHIASMA's premise to be testable at all: worlds whose
abstractions are deep and widely shared (Y over many literals, reused by many cells,
nested), so that shared structure is a large fraction of the representation and a
compressing organism can keep its knowledge under a budget that ruins a flat one. That
is a new world family (PW-D, "deep abstractions"), not a new organism. It is the seat's
REVISE default (HADES-29, dev design first), unless the operator rules KILL.
