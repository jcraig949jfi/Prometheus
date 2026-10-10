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

## 11. dev-5: PW-D, deep shared abstractions (HADES-29; 300 runs, 0.61 CPU core-hours; chiasma/runs/e1b-dev-5/)

world_d.py: PW-H3's three staged false foundations and loads (12:4, 8:8, 4:12), with each
abstraction Y_j = core_j & f_j and core_j = 4 primitives. Cores are instantiated as
blocks (p = 1/3) or partially (each literal 1/4). f_j is independent at 1/2, forced on
whole cores in A-C, removed in C exceptions, and free in D-F. m = 32.

Sampler draft corrected on dev seed 910001 before any sweep. The first draft set f_j
ONLY with a whole core in A-C. Then f_j implies all four core literals, consolidation
prunes the core down to the marker f_j (O3W err_CDE 14772 vs O0 1720), and a second
false foundation appears beside the first. That variant (PW-Dm) is kept for its own
single-variable run later.

Checks: 7 new known-answer tests (determinism; 4-literal disjoint cores; f forced on
whole cores in A-B only and present without a whole core in A-C; at an exception rate
of 1000 every C object breaks exactly one core; crit probes separate ydep from decoy;
O0 ends with exactly the true term count, 67; factoring saves more than 20% of P with
identical errors). Mutants 25/25. First pass 23/25 (chiasma/runs/e1b-dev-5/
MUTATION_first_pass.txt): E21 (marker variant) and E22 (exceptions keep f) SURVIVED.
Two tests were tightened.

Uncapped, dev seed 910001: O0 and O0F both 1977 err_CDE. P at the end of B: 743 vs
579 (-22%, 16 rules). With no single literal implying f, consolidation prunes nothing:
O3W, O4LW and their factored twins equal O0/O0F exactly. **In PW-D the revision half of
the dual mesh does not engage. PW-D tests compression only.**

Binding budget (pevict), caps between and around the two P sizes, wins out of 10:

| cap | O0F>O0 | O0F>O1 | O0F>O2 | median err_CDE O0 / O0F / O1 | cells evicted O0 / O0F |
|---|---|---|---|---|---|
| 550 | 10 | 10 | 10 | 16310 / 8038 / 23400 | 10636 / 3897 |
| 600 | 10 | 10 | 10 | 13107 / 7079 / 21915 | 8233 / 515 |
| 650 | 10 | 10 | 10 | 10609 / 6809 / 20775 | 5945 / 1 |
| 700 | 10 | 10 | 10 | 7696 / 5266 / 20449 | 3097 / 0 |
| 800 | 5 | 10 | 10 | 3338 / 3735 / 18529 | 28 / 0 |

Reading (dev, sizing):
1. This is the first regime in CHIASMA where compression keeps knowledge. At caps 650
   and 700 the factored organism keeps its whole positive geometry (0-1 cells evicted),
   while the flat organism loses 3,000-6,000 cells over the run. It wins 10/10.
2. It is not lossless at the organism level. O0F's err_CDE at 650-700 is still 3-3.5x its
   uncapped value. The cap squeezes the failure memory N (O0's natural N is about 17 KB),
   so weld checks run against an emptied shadow. In PW-D the binding resource is the
   shadow, not the geometry.
3. Loose end, not chased: O4LW differs from O0 on 17/50 binding-cap rows (identical
   uncapped). Under eviction churn, cells reach 6 supports and consolidate; rarely
   something is pruned (one repair event in the row inspected).

## 12. What PW-D changes

The charter's question has two halves: (i) compression that keeps knowledge, and (ii)
failure geometry and revision that retract false abstractions with less damage.
- (i) has its first positive dev signal: lossless factoring on deep shared
  abstractions, under a budget between the factored and flat sizes.
- (ii) has none. In PW-H/H3 revision only helps when bytes are free, where not
  compressing is as good. In PW-D nothing is pruned, so nothing needs revising.
- N, the charter's negative mesh, is now the binding resource. A compressed shadow (the
  charter's O3 idea) has a real job in PW-D for the first time: keep the weld checks
  alive inside the cap. That is the next dev variable (HADES-30): shadow compression
  {raw-FIFO, projected-maximal, factored} under PW-D binding caps, with O0F's geometry
  fixed.
- A confirmatory prereg for (i) can be drafted now (O0F beats O0 at caps 600-700 on
  PW-D, 8/10 per cap). Its freeze waits on G3 like the rest.

## 13. dev-6: shadow compression under PW-D binding caps (HADES-30; 250 runs, 4.57 CPU core-hours; chiasma/runs/e1b-dev-6/)

One variable: the failure memory N. The geometry is fixed (O0's, factored, never
consolidating). The cap binds with pevict. Arms (arms.py):
- S0F: no N.
- SRF: raw failures, FIFO.
- O0F: projected maximal shadow, the charter's compressed failure boundary.
- SPFF: projected shadow, itself factored (lossless; exact cap loop, oldest negative
  first).
- SXF: counterfeit shadow, random masks of the same size.
Four new tests (memory kinds; the counterfeit differs in content; the factored shadow is lossless, expands back and is
smaller with identical P; its cap is exact). Mutants 29/29; first pass 28/29 (E27, counterfeit keeps true content, SURVIVED; content test added; MUTATION_first_pass.txt).

Uncapped (dev seed 910001): SPFF halves N with identical errors (16989 -> 8845 bytes,
460 rules). It costs about 40x the CPU of O0F, which is why dev-6 used 4.57 core-hours.

Wins out of 10 on err_CDE (ties in brackets where they matter):

| cap | O0F>SRF | O0F>SXF | O0F>S0F | SRF>S0F | SPFF>O0F | median err S0F / SRF / O0F / SPFF / SXF |
|---|---|---|---|---|---|---|
| 600 | 6 | 5 | 6 | 0 | 2 (6 ties) | 8343 / 8343 / 7079 / 7122 / 8040 |
| 650 | 9 | 9 | 9 | 2 | 6 (2 ties) | 8343 / 7847 / 6809 / 5071 / 8023 |
| 700 | 9 | 8 | 9 | 4 | 6 (2 ties) | 8343 / 7560 / 5266 / 3763 / 8025 |
| 800 | 9 | 8 | 9 | 6 | 7 (2 ties) | 8343 / 7079 / 3735 / 2513 / 7424 |
| 1200 | 10 | 10 | 10 | 10 | 1 (9 ties) | 8343 / 5486 / 1747 / 1747 / 5343 |

Reading (dev, sizing):
1. The charter's O3 claim has its first positive signal. A compressed failure boundary
   beats raw failure memory at matched bytes, 9/10 at caps 650-800 and 10/10 at 1200.
   It also beats its random counterfeit (content matters) and no failure memory. E1
   never showed this (O3 beat O2 at most 2/10 there, where N never bound).
2. Raw failure memory is close to useless under these caps. Whole objects are too
   expensive, so SRF holds a handful and matches no-memory at 600.
3. Factoring the shadow lowers the median further (2513 vs 3735 at cap 800). Per seed it
   is mixed (6-7/10, below the 8/10 bar), and it is expensive in CPU. Not a claim yet.
4. Together with s11: on PW-D under a binding budget, lossless compression of BOTH
   meshes (factored geometry, projected shadow) beats every flat or raw alternative
   tested. The positive mesh and the negative mesh compress differently: factoring for
   one, projection onto support for the other.
5. Still absent: the revision half (provenance, seams). In PW-D nothing is pruned, so
   nothing is revised. The charter's "retract entrenched false abstractions with less
   collateral" is untested in the one world where compression pays.

## 14. Candidate confirmatory package (draft; freeze waits on G3)

On PW-D, fresh evaluation seeds, pevict, caps 650/700/800:
- D1: O0F beats O0 (factored vs flat geometry), at least 8/10 per cap.
- D2: O0F beats SRF and SXF (projected vs raw and counterfeit shadow), at least 8/10 per cap.
- D3 (secondary, not deciding): SPFF vs O0F.
Plus the E1b C1/C2 pair (s8) on PW-H/H3. Predictions: D1, D2, C1, C2 confirm; D3 mixed.
The revision question needs a world where compression pays AND is wrong somewhere:
PW-Dm (the marker variant, s11) is that world, where pruning the core down to its
marker is cheap and false. HADES-31 sizes the revision arms there.
