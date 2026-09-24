# CW01 priority loop - boundary report, cycle 5 (CYCLE5_2026-09-19)

Scope: computational artificial-life / algorithm-search research on integer programs, GA policies and
tree/tape genomes in software worlds. No biological material, organisms, sequences or wet procedures.
No external model or service was called; INFRASTRUCTURE_BOUNDARY count 0.

Governing principle this cycle: rulers, interventions and price functions are candidate mechanisms.
An instrument node (T-R01, the damage ruler) was added to the pool; the prioritizer gained a
`requires` rule so a reread cannot run before its ruler qualifies.

## 1. Reconcile and freeze

Six RECONCILE-5 notes; batch G added 11 candidates and re-posed P-F02 as a manifold measurement; 29
competed. Slots: deformation B (P-G05), O (P-G07), R (P-G01); serendipity P-G09, P-G12; anti-gravity
P-G08, P-G10; by score P-G03, P-G02 (requires P-G01, satisfied), P-F02. P-G04 (price dose x load,
46.0) tied with P-F02 and lost the id tie-break; it waits first in line. P-G11 (alternative response
ruler, 45.0) waits.

| rank | id | parent | slot | why it survived |
|---|---|---|---|---|
| 1 | P-G05 | T-X17 | deformation B | neutral transplant (no selection) + C4-08 under selection |
| 2 | P-G07 | T-ARCH4/M1 | deformation O | operand slot / category transfer, HALT-probe reach, held-out additivity |
| 3 | P-G01 | T-R01 | deformation R | qualification of the scattered ruler before any use |
| 4 | P-G09 | T-X18 | serendipity | load: elite vs population, sharing on/off, generations |
| 5 | P-G12 | T-X18 | serendipity | load read in Proteus |
| 6 | P-G08 | T-R01 | anti-gravity | does the scattered ruler have its own geometry |
| 7 | P-G10 | T-X16 | anti-gravity | price decomposition (units vs registers) |
| 8 | P-G03 | T-X15 | score | graded persistence with a function window |
| 9 | P-G02 | T-ARCH4/M1 | score (requires P-G01) | reread of P-D01 / P-E05 / P-F06 |
| 10 | P-F02 | T-X17 | score | response-geometry census as a manifold |

## 2. Results and deformation events

Ten of ten ran under their preregistrations; no re-runs; the ruler qualified first.

- **P-G01 INSTRUMENT_QUALIFIED.** Hit counts match Binomial(n, f) (25,200 draws; mean z -.011, var
  .991, Monte Carlo chi-square p .49); no positional clustering (100 percent inside band); hit fraction
  independent of length (slope 2.8e-5 inside band); masks reproducible; sham path clean on 126/126.
- **P-G08 RULER_DEPENDENT, and the dependence is the diagnosis.** On 122 programs at f .10: Bernoulli
  scattered gives no length effect (+.04) and no set effect (+.01); reached-only and disable-to-NOP
  agree. The exact-count scattered ruler (round(f n)) reproduces the old coordinates (length -.107,
  tops -.19) exactly as the contiguous window does (-.143, -.178): round(f n)/n is larger for short
  programs, so every count-fixing ruler manufactures "length protects" and "tops are robust".
- **P-G02 ruler reread** (table in section 3): four of seven fixed-count claims disappear, one
  survives, two shrink.
- **P-G03 STATE_CORRELATED by rule; substantively ENTANGLED.** Reducing persistence below q=1
  destroys function in 112/121 programs (reward .71 -> .43 at q=.75; nothing survives q <= .5). Among
  the 9 programs with an eligible lower dose, damage loss is identical (paired difference 0.000). The
  residual correlation of persistent words with loss is weak (rho -.13, just outside band). Carried
  state is not a separable robustness coordinate here.
- **P-G07 MATERIAL.** The operand-slot ordering a > b > c transfers across all strata with disjoint
  bands (parents .42/.15/.07; walkers .38/.13/.05; tops .22/.02/.00) and holds on held-out families
  wherever the held-out baseline is above the floor. Reach (HALT probe) is a coordinate: reached
  instructions lose .22, unreached .04. halt_yield's low loss is not reach (reached halt_yield .087 vs
  grand .167). Slot x category not additive on held-out deltas. The grammar-level mechanism is not
  promoted by the rule (one degenerate held-out cell), recorded as supported where measurable.
- **P-F02 MATERIAL; two unseen shapes promoted.** 412 programs, six stable shapes (silhouette .90):
  immune (227), ask-time (79 + 9), input-schedule (37; C4-08 tops and shelf), and two new: T-X19
  start-anchored (34; the delay_general lineage: immune everywhere except an idle tick before the
  first PUT, .94) and T-X20 periodic (21; displaced at every position with a parity dose response
  .77/.41/.41/.41 and order sensitivity .99 vs .43). Dose responses saturate at one tick for 97.7
  percent of sensitive positions. Shapes are heritable along neutral walks.
- **P-G05 MATERIAL.** Under a neutral walk in the host world: the ask-time W0 lineage keeps its
  geometry in W2 unchanged (TRAVELS; the rule read MIXED on a threshold below the lineage's own
  spread, D087); the immune W0-idle lineage stays immune in W2 (TRAVELS); the immune W2 lineage
  DECAYS toward W0's ask-time class without selection (ask components 0 -> .30/.23/.25); the C4-08
  schedule lineage also drifts toward the host in W0. Under selection every class is REBUILT in
  20-40 generations (C4-08 -> immune under idle-tick W2; -> ask-time under plain W0).
- **P-G09 ORGANISM_PROPERTY by rule; substantively SHARING PREVENTS PURGING.** With sharing on,
  the fitness elite's raw score rises under one-unit deletion in 40-83 percent of cases; with sharing
  off, 0-13 percent. Random gen-0 bodies rise 33-39 percent in both regimes: load is initial junk that
  selection without sharing purges and selection with sharing does not.
- **P-G12 NO_LOAD in Proteus** (reward rises in 1-3 percent under scattered f .05; elite 0 percent):
  deleterious load is not cross-substrate.
- **P-G10 STRUCTURAL_PRICE** (3 ids, bimodal finals; a direction, not a magnitude): the pruning
  signature follows the per-unit price (units_only +.67, both +.67) not the register price (-.33).

## 3. RULER AUDIT

| reread | old ruler | new ruler | old conclusion | new conclusion | disposition | defect |
|---|---|---|---|---|---|---|
| P-D01 length | fixed k (2/4/8) contiguous windows | scattered Bernoulli f .05/.10/.20 (P-G01) | loss +.145 per doubling of k at fixed n: longer programs lose less | slope of loss on log n +.03 / +.01 / +.00, inside +-.07 | DISAPPEARS | D084 |
| P-D01 operand softness | fixed k operand windows | scattered operand f .10 | operand .36 vs delete .72 | operand - delete -.19, below p05 (124 pairs) | SURVIVES_RULER_CHANGE | - |
| P-D01 set effect | fixed k | scattered f .10 | tops ~.20 more robust than parents / walkers | tops .32 vs rest .41 (-.09, below p05; length-conditioned -.12 at the band edge); P-G08's independent draws +.01 | SHRINKS (draw-sensitive; UNRESOLVED as a coordinate) | D084 |
| P-E05 depth under orig rule | fixed k4 s1/s4 + operand | scattered f .10 | loss falls with depth .60 -> .50 | .423 -> .419 (+.003, band +-.07) | DISAPPEARS | D084 |
| P-E05 depth under no_growth | fixed k | scattered f .10 | loss rises .67 -> .84 | .439 -> .442 (+.003) | DISAPPEARS | D084 |
| P-E05 rule effect at 64 | fixed k | scattered f .10 | no_growth products lose +.27 more | +.02 (band +-.07) | DISAPPEARS | D084 |
| P-F06 selection effect | fixed k cells (P-D01) | scattered f .10 / .20 | select .31 vs ndrift .62 vs ancestor .65; length-conditioned -.144; 6/6 seeds | select .355 vs ndrift .436 vs ancestor .474; length-conditioned -.071 (band +-.05); 0/6 seeds hold both contrasts | SHRINKS (not promotable) | D084 |
| (control) P-G08 exact-count and contiguous | count-fixing variants | same programs | - | reproduce the old length (-.11 / -.14) and set (-.19 / -.18) effects | ruler artefact confirmed | D084 |

## 4. COORDINATE STATUS

| coordinate | LOCAL | CROSS_WORLD | CROSS_LINEAGE | CROSS_SUBSTRATE | RULER_INVARIANT | RULER_DEPENDENT | CAUSAL_SUPPORTED | BROKEN | UNRESOLVED |
|---|---|---|---|---|---|---|---|---|---|
| T-X15 length / carried state | yes | - | - | TREE depth only (P-F09) | no | YES: length exists only under count-fixing rulers | no: state cannot be moved without destroying function (P-G03) | BROKEN (retired; scoped stasis) | state under subset persistence |
| T-X16 damage as pruning | yes (e06) | - | - | no (Proteus reverses) | - | price-dependent by definition | price-mediation supported: sign follows the per-unit price (P-F04, P-G10) | BROKEN as "damage robustness" | magnitude of the structural-price effect (n=3) |
| T-X17 temporal class | yes | vector reads all worlds; class travels under a neutral band in W2, erodes in W0 | yes: heritable along walks, lineage-specific | - | not yet tested (P-G11 waits) | - | yes: selection removes and rebuilds; neutral drift erodes in a world whose band admits sensitivity | BROKEN as three classes (six shapes) | the ruler test (P-G11) |
| T-X18 deleterious load | yes (e06 with sharing) | - | - | no (Proteus: none) | yes: absolute ruler | - | yes: sharing on/off flips the elite's load (0-13 -> 40-83 percent) | BROKEN as "accumulated load" (it is unpurged initial junk) | price x sharing (P-G04 waits) |
| P-E03 selection effect | yes | - | yes (6 seeds) | - | no | YES: -.144 -> -.071, 6/6 -> 0/6 seeds | weak residual, not promotable | - | which structure selection acts on |
| operand slot / category | yes | held-out where measurable | yes (three strata, disjoint bands) | - | operand softness SURVIVES the ruler change | - | slot: yes; category: reach x semantics; not additive with slot | - | promotion rule with a floor-conditioned held-out family |
| (new) reach | yes | - | yes | - | - | - | HALT probe moves it directly (.22 vs .04) | - | reach-weighted damage |
| (new) T-X19 start-anchored, T-X20 periodic | yes | - | yes (heritable along walks) | - | - | - | - | - | mechanism |

## 5. Continuation manifolds

- T-R01: reach-weighted damage; the ruler family as a dose (count-fixing vs fraction-fixing) as a
  standing positive control; absolute-score rulers for e06.
- T-ARCH4/M1: slot x category interaction; the promotion rule with a floor-conditioned held-out family.
- T-X17 / T-X19 / T-X20: P-G11 (alternative response rulers); transplant of the start-anchored and
  periodic lineages; doses to 8 for the period; neutral band width as a dose.
- T-X16 / T-X18: P-G04 price dose x load with sharing tolerance; whether damage's price-0 sign tracks
  unpurged load.
- T-X15 (stasis): subset persistence (registers only / tape only) with a function window.

## 6. Stasis

- T-X15 -> TEMPORAL_STASIS[coordinate=length-retired x state=entangled-with-function]; escape: a
  subset-persistence or bounded-duration intervention that keeps reward inside its band for >= 30
  programs, or a representation in which state and function separate.
- Total 6 (T-ARCH4/R1, T-E07, T-X15 scoped; T-E09, T-X06, T-X08 bare). T-ARCH4 ACTIVE.

## 7. Nodes

- T-R01 (instrument: the damage ruler), T-X19 (start-anchored temporal geometry), T-X20 (periodic
  temporal geometry). Pool: 38.

## 8. POOL TOPOLOGY CHANGE

Connected: T-R01 <-> T-ARCH4/M1, T-X15, P-E03 (four of seven damage claims were the ruler); T-X18 <->
T-E06's sharing rule (load is unpurged junk that sharing protects) <-> T-X01; T-X17 <-> T-X19 / T-X20
(one manifold of at least five non-immune geometries) <-> T-ARCH4/W1 (the delay_general lineage's
start anchoring); T-X16 <-> the per-unit price component.
Broke: T-X15 (length ruler-generated; state entangled); the P-E05 depth-robustness coupling; most of
the P-E03 selection effect; "three temporal classes"; "accumulated load"; T-X18's portability.
New dimensions: the ruler family (count-fixing vs fraction-fixing) as a variable; reach; start-anchored
and periodic temporal response; sharing as the keeper of load.

## 9. Defects

Ledger 88 (D087 transplant threshold below within-lineage spread). D084/D085/D086 (cycle 4) are now
closed by construction of the qualified ruler and the function-window rule. Tally from ledger; PASS.

## 10. Campaign 6 interface

loop/SPECIMENS_CYCLE3_4.json now holds ten public specimens including the ruler-induced false
coordinate (SPEC-R01-FALSE-COORDINATE), the price-set sign reversal, the intervention/function
entanglement (a probe UNABLE outside its domain), and the lineage-carried temporal geometries with
representative genomes. Public controls, not hidden fixtures; not for threshold tuning after freeze.
Campaign 6 machinery untouched.

## 11. Teardown

All drivers exited (process census: no cw01 python processes). Writer lock checked before the
commit; commit gated on its exit code. Production seats untouched. Archaeon originals unedited
(nestor-arch4 read only at 9cd33ff1e).
