# ARC3 / W3 -- NOVELTY-RULER ATTACK + WHAT COUNTS AS REUSE
(Deposited verbatim by the principal from worker W3's final message. The harness blocked
the worker's own Write of this file. Provenance: WORKER_MANIFEST.md row W3.)

Worker W3, 2026-09-28. Single core, no lease. Forensic only; no label re-adjudicated.
Scripts/JSON: w3_adversarial.py (W3_ADVERSARIAL_{G4,W5}.json), w3_baserate.py
(W3_BASERATE_{G4_100,G4_400,W5_200}.json + _ROWS_), w3_domain.py (W3_DOMAIN_W5.json),
w3_relclosure.py (W3_RELCLOSURE.json), w3_selnovelty.py (W3_SELECTION_NOVELTY.json),
w3_reuse.py (W3_REUSE_C2.json), w3_con1.py (W3_CON1_VS_SHAM0.json).
Checks: RB-1 junk100 reproduced exactly (16/100); frozen C2 S/R/C counts reproduced, all arms.

PART 1 -- RULER v2 vs G1
Error tally (W5 | G4), out of 48:
  (a) re-expressions 4 FN/14 | 5 FN
  (b) domain-equivalent 3 FN/5 | 4 FN
  (c) inert additions 0/10 | 0
  (d) specialisations 2 FP/7 | 0
  (e) enabling compositions 4 FN/7 | 5 FN
  (f) efficiency-only 1 FN/4 | 1 FN
F1 FP: (acc - ({H} * first)) and ((acc - {H}) + v) are NEW_FINAL, although they are
   refinements of (acc - {H}); (acc + ({H} * v)) is correctly REFINES.
   Causes: relations() matches literal G1 only (the re-expression closure is applied to
   SPAN, not to relations); acc-containing deep fillers; grid- and trajectory-novel
   witnesses can be disjoint (4/43 shared for the first case).
   Repair: close relations over reexpressions(R); require the same witness instances.
F2 Under closed relations, SHAM_0 = (v - (acc - {H})) COMPOSES G1, and so do all 4
   SHAM_0-arm selections. The C2-2 panel rule would have rejected SHAM_0.
F3 Shape FN: ((v - acc) - {H}), ((v - {H}) - acc) and ((acc*v) + ({H}*v)) have 1-2
   instances, so they are not NEW, although they compute the same functions as NEW
   forms. Novelty depends on how a schema is written relative to G5's
   prim(atom, depth-2) shape.
F4 Product FN (T29): ((acc + {H}) * v) is grid 144/144 novel but trajectory 0/144
   novel; the median share of battery folds that overflow is 21%. With <= 25% None
   allowed: 117/144, NEW. The C2 G1 NOVELTY count would be 3/8, not 2/8.
F5 The grid assumes acc >= 0, but 447/2489 (18%) of random W5 instances reach acc < 0 on
   the battery. |acc| - H is a constructible FN, but it is barely instantiable, and 0
   random-schema cases were found.
F6 Inert additions are handled: normalise() removes *1, //1, pow(.,1), +0, x-x, 0*x,
   pow(v,0); the other wrappers have 0 accumulating instances. However, inert wraps are
   COMPOSES = True, so they could earn COMPOUNDING credit if ever selected.
F7 Efficiency-only schemas ((acc * {H}), gcd(acc, {H})) are NEW. In a finite grammar
   every schema's benefit is efficiency; NEW means "differs from R", not "unreachable".
BASE RATE (frozen convention):
  G4 n=100: 16.0% (CI 10.1-24.4%)
  G4 n=400: 10.3% (7.6-13.6%)
  W5 n=200: 23.0% (17.7-29.3%)
  Range over 288 conventions: G4 2.8-31.5%, W5 6.5-47%.
  W5 one-at-a-time:
    floor 0/5/10/20/33/50% -> 24/23.5/23/17.5/14/8%
    min count 1/2/3 -> 29.5/23/21.5%
    distinct >= 2/3/5/10 -> 26.5/24/23/21.5%
    battery lengths 2-10/2-40/2-200 -> 24.5/23/21%
    None tolerance 25% -> 28%
    same-witness -> 23%
  The 10% floor is nearly inert. The minimum count of 2 and the instantiation world
  dominate.
SCALAR NOVELTY: not useful. In C2 it dissociates both ways:
  - G1_NC CON7: REFINES (not novel), yet capability on 2 families;
  - G1 CON0 and CON7: novel, zero capability;
  - random W5 schemas: 23% novel.
MINIMAL SET:
  J1 behavioural novelty: repaired ruler, reported with the world base rate and shams.
  J2 reach: there is a T4-admissible family whose program is extensionally equal (T4
     domain) to an (init, S-instance, final) program and to none from the reference
     library's instances at equal depth.
  J3 capability: on >= k held-out families the S-library qualifies at escrow where START
     and PRISTINE fail at M x escrow; report M; net of lost/dearer families.
  J4 causal dependence: extensional class not selected or capability-bearing in the
     sham, PRISTINE and move-ablated arms; report sufficiency vs necessity.
  TAG: EQUAL/REFINES/COMPOSES (closed) as provenance. "Compositional novelty" =
     J1 AND TAG = COMPOSES; it is not a separate judgement.

PART 2 -- REUSE
Levels:
  L1 literal recurrence;
  L2 in-sample instance reuse;
  L3 held-out transfer (L3a same generating group, L3b other group);
  L4 nesting in a later selected abstraction;
  L5 stepping stone.
WEAKEST MEANINGFUL CLAIM (L3, k=1): on at least one held-out family the selected
library qualifies at escrow where START fails, via the entry's coordinate, at a rate
above the sham and PRISTINE arms; lost and dearer families reported beside it.
C2 frozen REUSABLE:
  too strict: own group only, >= 2 families, COMPOSES required;
  too loose: no START counterfactual.
Spec/code deviation: SOLVED is computed on own-group TRANSFER cells by the selected
library of any origin (AMENDMENT 18 says VALIDATE cells, composed library); G1_NC shows
SOLVED 2 > REACHABLE 0.
Re-scored:
  G1: S/R/C frozen 0/0/0 -> any-group 1/1/1 (CON1); k=1 reuse 1/8.
  G1_NC: 2/0/0; k=1 reuse 2/8 (CON0, CON7); without the COMPOSES requirement R 1, C 1
     (CON7: qbaa, qtda; START and PRISTINE fail at up to 10M).
  SHAM_1: 1/0/0 -> 3/1/0; k=1 reuse 3/8.
  SHAM_0, OFF_0, P: 0.
H1 is unchanged under every definition (G1 max 1/8 vs 5/8 required).
Negative transfer: about 58k extra charges on families START already solved (CON1 G1
quaa 46k -> 104k); SHAM_1 CON5 loses qpga.
L4/L5 are unmeasurable (one generation).

PART 3 -- CON1
- Selection margin was tight: 5 eligible candidates with mean saving 54.8-59.3k; winner
  lower95 15.6k vs 14.3k.
- The only validation family it represents is qrda (CON:SHAM_0).
- Payoff families are literal SHAM_0 instances: qyba (H = v - last), qoda
  (H = last - acc).
- SHAM_0's START library solves both 4/4 at 4.7-54.5k, vs 4.5-52k for G1-composed.
- (v - (acc + {H})) and SHAM_0 are sign re-expressions at the inner node; the ruler
  calls each NEW vs the other (closure is root-only); 59/134 instances share
  trajectories.
Judgements:
  J1 vs G1: yes. J1 vs SHAM_0: yes as written, no semantically.
  TAG: COMPOSES G1.
  J2 vs G1: yes. J2 vs the panel: no.
  J3 vs L1 and PRISTINE: yes (>= 190x). J3 vs the best inherited library: no.
  J4: G1 + composition sufficient, G1 not necessary.
  Reuse: L3a only.
Opinion: composition converted G1 into SHAM_0's extensional class on SHAM_0-built
supply. This is not a G1-specific stepping stone.

EVIDENCE AGAINST APHRODITE'S CURRENT INTERPRETATION
E1 Reuse at k=1 with a counterfactual: 6/48 CON arm-replicates (G1 1, G1_NC 2,
   SHAM_1 3). The "bottleneck" is partly the frozen conjunction of conditions.
E2 The composition-OFF control G1_NC matched or beat G1 on capability. In CON0 and CON7,
   composition ON displaced a useful refinement with a useless composition. This
   contradicts "composition is the lever".
E3 CON1 is a SHAM_0 re-derivation: paid by a SHAM_0 validation family; payoff families
   are literal SHAM_0 instances solved equally by SHAM_0's library.
E4 The base rate is 23% in W5, not 16% (G4 n=400: 10.3%). The floor is inert; the world
   dominates.
E5 The relation-closure gap produces false positives and admitted the SHAM_0 confound.
E6 Products are undercounted (NOVELTY 3/8, not 2/8), and novelty depends on how a schema
   is written.
E7 The ladder's SOLVED code deviates from the spec; the G1_NC ladder is non-monotone.
E8 The reuse-controlled assay needs a composition-OFF arm scored without the COMPOSES
   filter, closed-relation shams, and net reuse accounting.
NOT TESTED: program-level J2 on random schemas; the Ananke panel-ablation cross-check;
L4/L5.
