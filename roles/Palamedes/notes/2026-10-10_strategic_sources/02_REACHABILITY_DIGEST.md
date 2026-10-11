# Source digest 2 -- Atlas reachability/Go-Explore series (G1-G6), Nyx's attack, follow-through

Prepared for Palamedes (Strategic Expansion Directive 2026-10-10) by a read-only research subagent at db64f110e.
A/ = roles/Atlas/proposals/2026-10-02_reachability_go_explore/; N = roles/Nyx/ATTACK_reachability_go_explore_2026-10-03.md;
D = nyx/atlas/experiments/reach_archive/DESIGN_G1_ARCHIVE_ARMS.md. Citations re-read before use in a deliverable.

## Atlas G1-G6 (proposal only; nothing run; operator go required -- A/01:3-4)
G1 archive vs current searches as hitting times (arms S1 native, S2 strict greedy, S3 neutral walk, S4 archive with
fingerprint cells + count selection + random exploration from restored state, S5 reward-bin archive; descent from the
plant with d components removed and ascent from random; endpoint certified lineages/n; 0/n reported as <3/n); G2 cell
definitions (C1 reward bins, C2 behaviour fingerprint, C3 genotype features, C4 random hash, C5 oracle prefix cells);
G3 path vs policy (robustness); G4 breadcrumb dose; G5 LLM generator concentration; G6 census ground truth (1e8-1e10
programs). Non-licence: "substrates are deserts" and importing Go-Explore into a live engine (A/01:274-279).

## Nyx's attack
- B1 (blocking): S4 bundles retention, novelty (count) selection and new-cell acceptance; detachment index is zero by
  construction. Correction verbatim: "S4-greedy: same archive and same cells, but select the highest-scoring cell ...
  S4-uniform: uniform selection over cells ... retention effect = S4-greedy vs S2; novelty-selection effect = S4 vs
  S4-uniform; the neutral-acceptance effect is already isolated by S3 vs S2. Only if S4-greedy carries the gain is
  'detachment' the right word" (N:52-61).
- B2 (blocking): return is free in genome space -- the archived object IS the program; call it population-genetic loss;
  "'Go-Explore' should not appear in any result claim drawn from G1" (N:77-81). Possible exception: Tyche T4 (unchecked).
- M1 G3 is a vocabulary merge ("survival of the flattest"); M2 C4 is a structure-free BASELINE with bucket count matched
  to C2, and intermediates must be genomes on a shortest edit path under the arm's own operator; M3 G4 dose confounded
  with selection priority (seed visit counts at the archive median or report share of selections on seeded cells).
- A2 stochastic fitness: re-evaluate a cell on fresh lives before replacement; A3 use a pedigreed QD library or call it
  MAP-Elites with count selection; A4 fingerprint must fail on a planted near-miss (Harmonia: reference "CANNOT FAIL").
- A7 cheapest decisive G1: add S4, S4-greedy, S4-uniform to the existing p1_slice reach harness; d = 0,1,2,3,8; 24
  lineages; budget 200,000; same certification; existing grid 425.8 s. m1 power: 0/24 vs 6/24 p = 0.022.

## Five distinctions -> tests
retaining genomes: Nyx X1 vs chain, S4-greedy vs S2; neutral stepping stones: S3 vs S2, G4, G2 visibility; restoring
environment states (true Go-Explore): NOTHING in G1-G6 on checked targets (Crius named by Hestia as the host with real
world states; Tyche T4 unchecked); genotype paths: G2-C5/G4 once corrected to shortest edit paths; populations around
incomplete mechanisms: S1 only, no isolating arm (Fable prescription for a population arm unmet).

## Status
G1-G6 designed only; Atlas DRAINED 2026-10-03 (#1294), reply to the attack owed. Nyx 3318a2098: ladder design D (chain,
X1 retention, X2 count selection, X3 new-cell acceptance; cells C-BEH per-type correct counts, C-FIT, C-GENO-HASH matched
to C-BEH; target T5, d = 1,2,3,8, 24 lineages, budget 200k; read a contrast only if an arm reaches >= 6/24), pure-Python
archive_arms.py, 4 toy tests. Owed: operator go, numba port + differential test, preregistration. Gaps (subagent
inference): no post-hoc certification wrapper (archive_arms.py:80 stops at training fitness); X2 weight is only the
"chosen" term; retention control asserts only x1 >= ch.

## Candidate deserts with a known constructed solution
1. T5 FABLE-5.1 p1_slice reach world (BEST; fully instrumented): 8-instruction minimal builder; RECEIPT_reach.json
   d=1 margin 24/24, strict 9/24, neutral 1/24; d=2 0/0/1; d=3 0/1/0; d=8 0/1/0; 0 of 2,000,000 random programs >= 0.9;
   grid 425.8 s; census-able. POWER: chain baseline = neutral at 1/24, so an arm needs 8/24 for p = 0.023 (7/24 p = 0.048;
   6/24 p = 0.097) -- Nyx's 6/24 threshold was computed against 0/24.
2. T3 CW01 4-instruction XOR (witness; every prefix scores 0; 12,880-edit census 0 improving edits).
3. T2 Proteus two_key (5-edit duplicate-then-diverge path, quick mode only).
4. T1 PTE/Ananke (16-line plant; FLIP in Hestia's terms).
5. T4 Tyche parity-3 (possible world-state target, unchecked).
6. Hestia's extras: SFE W2_K2, z80atlas COND_ONE, Crius reuse (real world states).

## Unresolved
Atlas's reply to B1/B2/M1-M3; G3 mapping; Tyche T4 world-state status; pedigreed library vs re-implementation;
fingerprint validity (planted near-miss); no frozen must-fail control replacing C4 / restore-disabled; no population arm;
no operator go for any run.
