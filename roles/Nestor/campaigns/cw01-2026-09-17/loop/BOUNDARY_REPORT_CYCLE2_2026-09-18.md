# CW01 priority loop - boundary report, cycle 2 (CYCLE2_2026-09-18)

Scope: computational artificial-life / algorithm-search research on integer programs, GA policies and
tree/tape genomes in software worlds. No biological material, organisms, sequences or wet procedures.
No external model or service was called in this cycle; no safeguard refusal occurred
(INFRASTRUCTURE_BOUNDARY count: 0).

## 1. The ten frozen selections and why each survived prioritization

Pool at freeze: 28 trajectories (31 after this cycle), 80 candidate lines in PERTURBATIONS.jsonl (batch D
added 11 real descendants of the T-ARCH4 deformations A/B/C with continuation lists). Scoring was opportunity
(weighted 0-3 criteria + anti-gravity bonus), not truth. Three slots were reserved one per deformation family
so the material deformations of T-ARCH4 could not be diluted by global scoring; two serendipity, two awkward
(anti-gravity), and the rest global. MAX_PER_PARENT 2, MAX_PER_FAMILY 3. Executed candidates and stasis
parents without an escape clause were excluded before scoring.

| rank | id | parent | slot | deformation | why it survived |
|---|---|---|---|---|---|
| 1 | P-D01 | T-ARCH4/M1 | dose surface | A (locality law -> dose surface) | a surface (k x s x kind x placement x decode x genotype set), not another binary comparison; held-out world |
| 2 | P-D02 | T-ARCH4/W1 | switch probe | B (delay as a switch) | delay variants never tried; per-step trace to find the switch step |
| 3 | P-D03 | T-ARCH4/M1 | mechanism break | C (acceptance-filter mechanism) | mechanism stated; each cell removes one support (rule, trap, proposal mix) |
| 4 | P-D13 | T-E06 | serendipity | - | e07's damage family meets e06's ecology; the two never met |
| 5 | P-B07 | T-E03 | serendipity | - | both modules existed; burden pressure on a learnability substrate |
| 6 | P-D12 | T-X05 | exploratory dose | - | amputation interval never varied; tax removed to isolate one factor |
| 7 | P-B10 | T-X11 | anti-gravity | - | a residual nobody had named; seconds per run |
| 8 | P-D11 | T-X01 | cross-material | - | cross of two independent material findings (tournament size x recombination rate) |
| 9 | P-D05 | T-E06 | replication | - | replication IS the question after a 1-cell mutual-invasibility finding |
| 10 | P-D07 | T-E07 | reposed confirmatory | - | new ruler (absolute retained score) and new dose on a world already material |

## 2. Results and deformation events

Ten of ten ran under their own preregistrations (PREREG.json hashed before each run; hashes stamped in each
RESULT.json). Two runs crashed once and were re-run after fixes recorded in the ledger (D074, D075).

- **P-D01 (A) MATERIAL - a dose surface exists.** 57,536 rows over 360 cells and 126 programs, held-out
  W2_K2d1. Loss per doubling of units lost (k) +.145 versus per doubling of sites (s) +.024: the locality law
  is mostly a dose in units with a small locality term (k=8 in one site .66 vs in 8 sites .77, +.05, outside
  the paired band; k 2->8 at one site .43->.66, +.40). Kind: operand damage .36 versus delete/opcode/move
  .72-.75 - operands are the soft coordinate. Decode trap and placement are inert. Genotype set: parents and
  16-step walkers lose about .20 more than C4-08 selected tops. Deformation A moved from a law to a surface
  with a named soft coordinate.
- **P-D02 (B) NARROWED, cells vacuous (D073).** Per-tag delay, interleave and ask-timing knobs are inert at
  K=1, so half the grid scored identical episodes and is not evidence. Live cells: an inserted deterministic
  NOISE tick between the last PUT and the ask makes silent W0 drift loud (.001 -> .118 at delay 1, 2 and 4
  alike); NOISE words inside the same tick do not (.009); interleaved .07. The switch is an extra TICK, not
  extra input. Delay-evolved walkers are nearly immune (.017); C4-08 selected descendants react most (.332).
  10/60 walkers show one distinct loud step, mixed operators, no broken references. Promoted to node T-X12.
- **P-D03 (C) MATERIAL - mechanism confirmed and controllable.** Growth under trap-NOP (+1.8) reverses
  under a no-growth acceptance rule (-3.1 frozen, -6.0 deletion-heavy), a length cost (-1.4/-3.1), symmetric
  deletion with deletion-heavy proposals (-3.5) and under trap-HALT (-.76); length-balanced proposals still
  grow (+2.35). When growth reverses, exaptation rises (.064-.074 vs .032) and structural diversity rises
  (1.56-1.64 vs 1.19): length accumulation was suppressing exaptation.
- **P-D13 MATERIAL (read DAMAGE vs SHAM; D076).** Blind deletion of 10% of body units per generation tilts
  e06's ecology toward TAPE (final TREE .43 vs .885 under sham; growth -.006 vs +.044), raises coexistence
  (2/4 vs 1/4) and shrinks TREE bodies (8.5 vs 13-16 units). Representation-blind damage is not
  substrate-neutral in effect. Defect: the sham consumed shared RNG draws so SHAM != STATIC; STATIC is
  reported as a third arm only.
- **P-B07 INERT (instrument).** Non-zero-weight share .985 at every lambda: clipped Gaussian mutation never
  drives a weight below the .05 threshold, so the burden coordinate cannot move. The e08 lesson again.
  T-E03 enters scoped stasis.
- **P-D12 NOT MATERIAL.** Amputation alone at intervals 2/5/10/20 lowers burden (.81-1.52 vs 1.87) without
  moving held64 (139-162 vs 156, inside the band). One factor of e08's association excluded.
- **P-B10 SEARCH LIMIT.** Bayes-optimal router precision 1.0/1.0/.96/.80 at overlap .1/.2/.35/.5 versus
  evolved .55/.56/.50/.43; the gap shrinks only slightly by generation 240. The plateau is the search, not
  the task.
- **P-D11 NOT MATERIAL by rule, but a regime appeared.** 80-generation runs seeded 50/50 coexist in 2/4
  (baseline), 1/4, 2/4, 3/4 cells. e06's "coexistence unreachable" was a statement about invasion from 10%,
  not about coexistence from parity. Tournament 2 x recombination 1.0 gives the most coexistence (3/4).
- **P-D05 NOT_REPLICATED - a reversal.** Mutual invasibility 1/12 cells at rate 1.0, 0/12 at 0.5. TREE
  invades TAPE in 8/12 at rate 1.0 versus 4/12 at 0.5 while TAPE's invasion collapses: the recombination rate
  sets the direction of dominance; P-A07's cell sat at a crossing. Promoted to node T-X14.
- **P-D07 MATERIAL - a reversal.** Absolute retained score is lower under weather at every dose (.0011 vs
  .0032 at f=.1 down to .0001 vs .0004 at .45, outside the band); the intact margin under weather is a
  third of static (.0019 vs .0061). Weather selects for state AVOIDANCE in a one-parameter organism. The
  ability-adjusted contrast flips sign across doses by covariate extrapolation (D071). Promoted to T-X13.

Deformation events this cycle: A -> surface (P-D01); B -> inserted-tick switch (P-D02, T-X12); C -> confirmed
and reversible by two independent levers (P-D03). Reversals: P-D05, P-D07. New regime: P-D11 parity
coexistence. Cross-substrate effect: P-D13.

## 3. Continuation manifolds opened by material results

- T-ARCH4/M1 (A): instruction-role map of the operand softness; pairwise site epistasis at fixed k; other
  held-out families; C4-08 tops versus their own ancestors (was selection or drift the source of robustness).
- T-X12 (B): content of the inserted tick (empty / NOISE / repeated PUT); K=2 worlds where per-tag delays are
  live; revert-and-replay of the loud step; persist flag off.
- T-ARCH4/M1 (C): depth 32/64 under no_growth + deletion-heavy (the highest-exaptation cell); band width;
  C5 representation B.
- T-E06: damage dose f; damage one substrate only; draw-matched sham; 240 generations from parity;
  seeded-frequency sweep; fine recombination-rate sweep .5-1.0 to locate the crossing (T-X14).
- T-X13: an organism with a redundancy channel so protection is representable; damage severity and timing
  during evolution.
- T-X11: population 256 / 1000 generations / a nonlinear activation policy.
- T-X05: tax alone at matched burden, then tax x amputation at matched burden.

## 4. Exact scopes of new stasis

- T-E07 -> TEMPORAL_STASIS[world=e01-retention x organism=5-gene]. Two rulers and two dose designs strike
  the same surface. Escapes: any organism that can represent protection; any other world.
- T-E03 -> TEMPORAL_STASIS[burden=L0-threshold on continuous weights x mutation=clipped-gaussian]. Escapes:
  a mutation operator that can zero weights, or a magnitude-based burden.
- No other state changed to stasis. Stasis total 7 (4 scoped: the two above plus T-ARCH4/R1 and T-ARCH4/S1
  from the reactivation; 3 bare: T-E09, T-X06, T-X08). T-ARCH4 remains ACTIVE; M1 and W1 are ACTIVE.

## 5. Anomalies promoted into trajectory nodes

- T-X12 the inserted-tick switch (from P-C14 / P-D02).
- T-X13 weather selects state avoidance (from P-B03 / P-D07).
- T-X14 recombination rate flips invasion asymmetry (from P-A07 / P-D05).

## 6. What the global pool now believes is worth deepening

1. The damage dose surface in the Proteus substrate (A) has a named soft coordinate (operands) and a
   selection-built robustness gap; both are cheap to deepen and connect to the acceptance-filter mechanism (C).
2. The inserted-tick switch (B) is a cross-tick-state phenomenon; the content-of-tick and K=2 probes decide
   whether it is a timing artefact of the world or a property of the programs.
3. e06's ecology is richer than e06 concluded: parity coexistence exists, damage tilts the winner, and the
   recombination rate sets the direction of invasion. The three findings share a world and can be posed in
   one factorial.
4. The e01/e07 retention line is exhausted for the one-parameter organism; the next informative step is a
   representable protection channel, and that is a new organism, not a rerun.
5. Search-limit findings (P-B10) and instrument-inert findings (P-B07, e08's lesson) recur; a standing
   attainability check on every burden or pressure coordinate before freezing is now the rule.

## 7. Defects

Ledger: 79 entries (D073-D078 this cycle). D073 vacuous cells; D074 latent crash in frozen world_e06;
D075 unbounded sampler hang (FIXED); D076 sham not draw-matched; D077 mark_executed tag collision (FIXED);
D078 scoped stasis miscount at close (FIXED). Tally derived from the ledger; consistency check PASS.

## 8. Teardown

All drivers exited (process census: no cw01 python processes). No git write was made while any RowWriter
held the tree; the writer lock was checked before the commit and the commit gated on its exit code.
Production seats untouched. Archaeon originals unedited; the execution worktree nestor-arch4 read only at
9cd33ff1e.
