# CW01 priority loop - boundary report, cycle 4 (CYCLE4_2026-09-19)

Scope: computational artificial-life / algorithm-search research on integer programs, GA policies and
tree/tape genomes in software worlds. No biological material, organisms, sequences or wet procedures.
No external model or service was called; INFRASTRUCTURE_BOUNDARY count 0.

Emphasis this cycle: portability of cycle 3's coordinates (T-X15, T-X16, T-X17, the P-E03 selection
effect) over local reproduction. The goal was to break, move and transplant them.

## 1. Reconcile and freeze

Seven RECONCILE-4 notes; batch F added 11 candidates (separations, transplants, economics reversals,
cross-substrate reads); 27 competed. Slots: one per deformation family (A: P-F01, B: P-F03, C: none
tagged this batch -> the third deformation slot fell to score), two serendipity (P-F10, P-F09), two
anti-gravity (P-F11, P-F08), then score under MAX_PER_PARENT 2 / MAX_PER_FAMILY 3.

| rank | id | parent | slot | why it survived |
|---|---|---|---|---|
| 1 | P-F01 | T-X15 | deformation A | single-coordinate manipulations (pad / duplicate / persist=none) x fixed-k vs fraction-matched damage; persistent-words census |
| 2 | P-F03 | T-X17 | deformation B | evolution under idle ticks in W0 and W2 + transplant |
| 3 | P-F10 | T-X16 | serendipity | price-mediated pruning transplanted into Proteus |
| 4 | P-F09 | T-X15 | serendipity | T-X15 read in e06's TAPE/TREE bodies |
| 5 | P-F11 | T-X17 | anti-gravity | temporal class after damage / manipulation (are T-X15 and T-X17 one node?) |
| 6 | P-F08 | T-E03 | anti-gravity (stasis escape) | heritable mask gene, attainability first |
| 7 | P-F04 | T-X16 | score | price 0 x damage x fraction x rate window |
| 8 | P-F05 | T-E06 | score | pre-adapted vs from-scratch residents; geometry x rate |
| 9 | P-F06 | T-ARCH4/M1 | score | P-E03 replicated over 6 seeds with a competent neutral-band drift control |
| 10 | P-E04 | T-ARCH4/M1 | score | operand role map, pairwise site interaction, held-out families |

Waiting: P-F02 (raw response geometry census, 46.0; T-X17 parent cap), P-F07 (T-X13 dose), P-A02, ...

## 2. Results and deformation events

Ten of ten ran under their own preregistrations; no re-runs.

- **P-F01 (T-X15) MATERIAL; rule reading [CARRIED_STATE, BROKEN], corrected by D084/D085.** NOP-pad
  (identity-preserving 70/70) lowers loss under fixed-k (-.23) AND under the contiguous fraction-matched
  window (-.20): both are dilution of a contiguous damage window - the ruler's geometry (D084: my
  fraction-matched cell was not dilution-neutral). Duplication changes behaviour in 30/70 and halves
  reward; among identity-preserving duplicates fixed-k loss falls (-.20) and fraction-matched does not
  (-.03): the copy is load-bearing when hit, not redundant. persist=none destroys function (reward .72 ->
  .03), so its loss is trivial (D085). Census (271 archived programs): at fixed k the depth effect is
  carried by log length (-.148, band +-.03), persistent words inside band; under fraction-matched, length
  carries nothing and persistent words a small effect (-.032, band +-.027).
- **P-F11 (T-X17 x T-X15) MATERIAL, ONE_NODE.** Pad preserves the temporal class 70/70; duplication
  70 percent; deletion that destroys reward preserves it 41-42 percent (95 percent when reward kept):
  partly structural, partly functional. persist=none sends 99 percent to immunity - but also destroys
  function (D085), so "carried state is the timing coordinate" is entangled with "carried state is the
  function".
- **P-F03 (T-X17) MATERIAL.** W0 selection under idle ticks yields fully immune tops in 40 generations
  at unchanged reward (.80); plain W0 selection yields ask-time-bound tops (.65-.69). W2 selection in
  this evolver yields immune tops - the cycle-3 "schedule-bound" class belongs to the C4-08 lineage,
  not to the W2 world. Transplant: immune W2 tops moved to plain W0 for 20 generations stay near
  immunity in one seed (24/32) and move halfway to W0's class in the other (15/32): the host world under
  selection reconstructs the class at a seed-dependent rate.
- **P-F10 (T-X16 in Proteus) MATERIAL, REVERSED.** At lambda 0 weather costs no reward and lowers top
  loss (-.066, below p05; P-E09's seed pair gave -.024 inside band). At lambda 1/128 the price alone
  collapses length 44 -> 5-6 at unchanged top reward (the length was junk) and weather lengthens programs
  (+5.7) and raises persistent words (+57); at lambda 1/32 weather is lethal (reward .18 -> .02).
  Price-mediated pruning does not transplant: under a length price damage is a growing cost.
- **P-F04 (T-X16 in e06) MATERIAL, REVERSED; none == sham verified.** Pruning signature (tree-damaged
  minus tape-damaged final TREE) +.25 at price .01 (above p95) and -.32 at price 0 (below p05): without
  the price, damaging TAPE helps TREE (+.18/.21/.35) and damaging TREE hurts it (-.05/-.19) - the natural
  sign; the price reverses it. Also: without the price TREE loses its dominance (rare TREE fails at .55,
  .65, .70; finals .33/.33/.00) - TREE's cheapness per unit was its advantage.
- **P-F09 (T-X15 in e06 bodies) UNRESOLVED by rule; ruler ill-conditioned (D086).** Blind deletion
  IMPROVES raw score on average (TAPE -.14 relative, TREE -.04): evolved bodies carry score-harmful
  units. TREE: loss falls with size and rises with depth under both doses; TAPE: no coefficient clears
  its outlier-widened band. Promoted to T-X18 (deleterious load).
- **P-F06 (P-E03 replication) SELECTED_REPLICATED 6/6.** Selected tops .31 vs own ancestors .65 vs
  competent neutral-band drift .62 (final reward .35-.52); dose monotone .455 -> .353 -> .312;
  length-conditioned: log length -.294, select -.144 (both outside bands); within length bands select <
  ndrift. The EFFECT is promoted; the MECHANISM is not (the ruler still contains dilution).
- **P-E04 (surface coordinates) MATERIAL.** Operand SLOT is a coordinate (register field .36, b .11, c
  .05; bands disjoint); opcode CATEGORY a second (comparison .24, control .22 vs halt_yield .035).
  Pairwise sites are ADDITIVE (epistasis -.007, band +-.01, 708 pairs). Held-out exaptation <= .017.
- **P-F08 (T-E03 mask gene) SPARSITY_ONLY; stasis ESCAPED.** The heritable mask moves the effective
  non-zero share by .34 under drift; the tax at H lowers it (.54 -> .44, below p05) with MI excess,
  precision, sparsity and score inside their bands. T-E03 returns to ACTIVE with its question answered
  on this organism: burden pressure changes what is carried, not conditionality.
- **P-F05 (protocols x geometry) MATERIAL.** The rate window exists in every protocol but moves (.55
  from scratch with new ids; .65-.70 pre-adapted; .6-.7 in cycle 3); protocols disagree at 3/7 rates;
  geometry (phi) flips the direction map at 2-3 of 6 rates. Geometry is portable; the rate is local.

Deformation events: T-X15's fixed-count length effect -> dilution geometry (BROKEN as a mechanism;
carried state survives as a small residual); T-X16 -> reversed twice (price 0 in e06, price in
Proteus); T-X17 -> selectable, lineage-borne, world-reconstructible; T-X14 -> broken as portable;
T-X04 -> confirmed cross-world; T-E03 -> escaped; the damage surface gained slot and category
coordinates and lost site interaction; the P-E03 effect replicated.

## 3. COORDINATE_STATUS

| coordinate | LOCAL | CROSS_WORLD | CROSS_LINEAGE | CROSS_SUBSTRATE | CAUSAL_SUPPORTED | BROKEN | UNRESOLVED |
|---|---|---|---|---|---|---|---|
| T-X15 length / carried state | yes (P-D01, P-E05, P-F01 census) | - | yes (parents, walkers, tops) | partial: TREE size effect exists but depth is the coordinate there; TAPE unresolved (D086) | length: NO - the fixed-count effect is dilution of a contiguous window (pad -.23/-.20; price removes 39/44 instructions at no reward loss); carried state: small residual (-.032) | BROKEN as "length = robustness"; the factorisation (dilution / redundancy / carried state) was mis-posed by the ruler (D084) and persist=none is not a manipulation (D085) | carried state vs function; redundancy untested (duplicates are load-bearing) |
| T-X16 damage as pruning | yes (P-E06, P-F04 at price .01) | - | - | NO (P-F10: Proteus reverses) | yes for PRICE-MEDIATION: the sign reverses at price 0 (+.25 -> -.32); damage itself is a cost to the damaged substrate | BROKEN as "damage robustness"; the correct statement is "the price list sets the sign of damage" | how much of the price-.01 benefit is deleterious-load removal (T-X18) |
| T-X17 temporal response class | yes | partial: the class reads the same on every construction (P-E02 cross-world reads), but W2 does not impose "schedule-bound" | yes: lineage-borne (C4-08 vs evolver tops differ in the same world) | - | yes: selection under idle ticks removes the class in 40 generations at no cost; a host world rebuilds it under selection | BROKEN as a world phenotype ("W2 -> schedule-bound") | whether the class travels without selection (neutral transplant); class vs persistence entangled with function |
| P-E03 selection effect | yes | - | yes (6 seeds, 6 winning lineages) | - | EFFECT yes: replicated 6/6 vs a competent control, monotone in generations, survives length conditioning (-.144) | - | MECHANISM: the ruler still contains dilution; which structure selection acts on |
| (added) target geometry T-X04 | yes | yes (phi x rate) | - | - | - | - | - |
| (added) rate window T-X14 | yes | - | - | - | - | BROKEN as portable (position moves with id / protocol / length) | - |
| (added) operand slot / category (M1) | yes | - | yes | - | - | - | slot x category interaction |

## 4. Continuation manifolds

- T-X15: scattered fraction-matched damage (delete each instruction with probability f) as the
  dilution-neutral ruler; persist dose on programs whose reward survives; census of persistent words vs
  loss under the neutral ruler; re-read P-D01 / P-E05 / P-F06 with it.
- T-X16 / T-X18: price dose (0, .0025, .005, .01) x damage; load vs generation and vs sharing; absolute
  score ruler with a floor.
- T-X17: transplant without selection (neutral walk in the host world); the C4-08 lineage under idle-tick
  selection; P-F02's raw geometry census (waiting at 46.0).
- T-ARCH4/M1: P-F06 re-scored on the dilution-neutral ruler; slot x category interaction; HALT-probe reach.
- T-E06: window position over 6 ids at .05 steps; geometry x rate x price; TREE's dominance vs price dose.
- T-E03: mask-gene flip dose; magnitude burden; the coalition question is answered SPARSITY_ONLY here.

## 5. Stasis

- T-E03 LEAVES stasis (its refined escape held: a heritable mask moves the L0 coordinate).
- No new stasis. Total 5 (T-ARCH4/R1, T-E07 scoped; T-E09, T-X06, T-X08 bare). T-ARCH4 ACTIVE.

## 6. Anomalies promoted

- T-X18 deleterious load: evolved e06 bodies carry score-harmful structure (blind deletion raises raw
  score). Pool: 35 nodes.

## 7. POOL TOPOLOGY CHANGE

Connected: T-X16 <-> T-E06's dominance question (TREE wins because it is cheap; price 0 removes its
dominance and reverses damage's sign) <-> T-X18 (load); T-X17 <-> selection (T-ARCH4/P1's evolver) and
lineage (C4-08) rather than world; T-E03 <-> T-X05 (burden pressure changes what is carried, not
capability, in a second substrate); T-X04 <-> T-X14 (geometry survives the crossing, rate does not).
Broke: T-X15 as "length = robustness" (dilution of the ruler); T-X16 as "damage robustness"
(price-set sign, not portable to Proteus); T-X17 as a world phenotype; T-X14 as a portable rate axis;
the site-interaction term of the damage surface (sites additive).
New dimensions: damage-window geometry (contiguous vs scattered) as a property of the RULER that
generated a coordinate; the price list as the sign-setting variable of an intervention; deleterious
load at mutation-selection balance; operand slot and opcode category as surface coordinates.

## 8. Defects

Ledger 87 (D084 contiguous fraction-matched window not dilution-neutral; D085 persist=none destroys
function; D086 relative-loss ruler ill-conditioned). All three are ruler / manipulation defects found
by the runs' own baseline checks; none were repaired silently. Tally derived from the ledger; PASS.

## 9. Campaign 6 interface

loop/SPECIMENS_CYCLE3_4.json catalogues six public phenomena (idle-tick sensitivity, temporal
classes with genomes, length/state manipulations, price-set damage sign, rate window, selection vs
ancestors) with locations, rulers and expected effects, for use as detector positive controls, Nyx
recognition specimens, observatory adversarial examples and post-freeze comparison cases. They are
not hidden fixtures and are not to be used for detector threshold tuning after thresholds freeze.
Campaign 6 machinery untouched.

## 10. Teardown

All drivers exited (process census: no cw01 python processes). Writer lock checked before the commit;
commit gated on its exit code. Production seats untouched. Archaeon originals unedited; execution
worktree nestor-arch4 read only at 9cd33ff1e.
