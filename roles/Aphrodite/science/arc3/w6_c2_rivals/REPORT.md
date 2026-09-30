# ARC3 / W6 -- C2 STATIC RIVAL DISCRIMINATORS (R1 horizon, R2 selection, R3 non-specificity, W1-E1)
(Deposited verbatim by the principal from worker W6's final message; the harness blocked
the worker's own Write of this file. Provenance: WORKER_MANIFEST.md row W6.)

Worker W6, 2026-09-28. Forensic only: I did not re-adjudicate C2 (G1_STEPPING_STONE = NO
stands). Everything ran on 1 core. My lease request (2 cores) returned QUEUE (7/8 leased), so
I did not compete and ran serially on one core.

Files (all in roles/Aphrodite/science/arc3/w6_c2_rivals/):
- w6_common.py: extensional cover, battery, and C2 loaders.
- w6_r1_horizon.py: R1. Output W6_R1_HORIZON.json, log r1.log.
- w6_r2_e1.py: R2 and E1. Output W6_R2_E1.json, log r2.log.
  - W6_R2_E1_run1_partial.json is an aborted first run: same E1 rows, but inert wraps were
    ranked first. It is kept only because the second run resumed E1 rows from it.
- w6_r3_nonspec.py: R3. Output W6_R3_NONSPEC.json, log r3.log.

## 0. INSTRUMENT

**COVER(S, F).** Some W5 instance b of schema S, some init in H1_SPACE and some final in
FINAL_SPACE give a program ('fold', i, b, f) equal to F's witness. Equality is checked on every
input of a 100-input task-domain battery where the witness is defined. The battery is drawn
exactly as a17.Prov.task draws inputs: length 4-9, values 2..30, query 3..97.
- This is what the library entry [schema_entry(S)] can express. It is not a cost claim.
- Sanity checks:
  - Every CON:G1 family is at distance <= 1 from G1, as its construction requires.
  - CON1's qoda and qyba are found at distance 1 via (v - (acc + {H})), the CON1 G2.
  - The G1 wrap covers 14/14 CON1 families.

**Validation pricing.** I rebuilt each donor's frozen VALIDATE cells exactly as a18.donor
builds them:
- a17.R_VAL = 4, label A19-CONr-val/rr, index r*4+j, Prov over the replicate's families;
- exact fast_cost, with A18_FASTCOST=1 as in C2.

**Reproduction gate.** For all 18 non-INHERITED selections, the recomputed mean paired saving
equals the frozen selection_table value (18/18 repro_ok).

**Transfer pricing.** Frozen TRANSFER cells (A19-CONr-rx, 4 cells), T4-qualified with
a18_c1.t4_qualified, compared with the frozen START row. Transfer pricing is at escrow (250k);
there is no 10M ladder.

## 1. R1 COMPOSITION HORIZON (Nestor)

This is the minimum number of a18.compositions moves from the panel schema to a schema that
covers the family. W5 has depth 3, so the possible distances are 0, 1, 2 or INF: depth 4 has
no in-space instances.

The 80 distinct VALIDATE and TRANSFER families (use-weighted: 32 VAL + 64 TRANSFER):

| From   | d=0 | d=1 | d=2 | INF |
|--------|-----|-----|-----|-----|
| G1     | 14  | 39  | 5   | 22  |
| SHAM_0 | 19  | 12  | 14  | 35  |
| SHAM_1 | 17  | 30  | 7   | 26  |
| OFF_0  | 9   | 0   | 7   | 64  |

- Best over all panel schemas: d0 35, d1 40, d2 3, INF 2.
- From G1, TRANSFER uses only: 8 / 36 / 5 / 15.
- Of the 58 families G1 can reach at all, 53 need <= 1 move and 5 need 2.
- The G1-unreachable families (22) are 9 CON:SHAM_0, 9 CON:SHAM_1 and 4 NAT. They need a
  negated or role-swapped filler that does not fit in depth 3, for example
  qica = (v - (acc - (acc*v))). No number of moves reaches them.
- Per replicate, 3-6 of the 8 transfer families are at d = 1 from G1, but they need DIFFERENT
  compositions. The best single composition covers at most 1-3 of them beyond what G1 itself
  covers (see R2).

**Verdict R1: NOT SUPPORTED.** Only 5/80 families sit at distance 2 from G1; most reachable
families are at distance 0-1. The binding constraints are:
- the W5 depth wall (INF), which composition cannot cross at any move count;
- fragmentation: distance-1 families need different wraps, while selection keeps one.

## 2. R2 SELECTION OBJECTIVE (Crius)

For each replicate and each composing arm with a held schema (G1, SHAM_0, SHAM_1, OFF_0; 32 in
all), I ranked the held schema's compositions:
- first by MARGINAL transfer cover, meaning families the held schema itself does not cover
  (inert wraps such as (S + 0) and (S * 1) equal S and are excluded by this ranking);
- then by total cover.

I priced the top ones on the frozen VAL cells, as a17.select does.

G1 arm (the interpretation's arm). "newF" = transfer families where the best composition
T4-qualifies at escrow and the frozen START failed.

| Rep | C2 choice (transfer fams solved vs START)        | Transfer-best composition (newF)             | Fate in selection                               |
|-----|--------------------------------------------------|----------------------------------------------|-------------------------------------------------|
| 0   | gcd(first, acc+H), mean saving 59.9k (0)         | ((acc+H)+first) / ((acc+H)+v) (1: qiaa)      | eligible, 57.9k, ranked BELOW                   |
| 1   | (v-(acc+H)), 59.3k (2: qoda, qyba)               | same class; also ((acc+H)+v) (2: quba, qwha) | chosen, or not a candidate (no VAL hit)         |
| 2   | (first+(acc+H)), 56.4k (0)                       | ((acc+H)+v) (3: qbaa, qnea, qrga)            | NOT A CANDIDATE (no VAL hit)                    |
| 3   | INHERITED (0)                                    | ((acc+H)+v) (3: qbaa, qnea, qwha)            | candidate, mean +3.1k, lower95 -1.0k, REJECTED  |
| 4   | INHERITED (0)                                    | (v-(acc+H)) (2: qjca, qsba)                  | candidate, -6.3k, REJECTED                      |
| 5   | INHERITED (0)                                    | (v-(acc+H)) (3: qada, qgaa, qrda)            | no VAL hit; costs -29k                          |
| 6   | INHERITED (0)                                    | 1 family only                                | --                                              |
| 7   | ((acc+H)*v), 59.9k (0)                           | ((acc+H)+v) (2: qbaa, qtda)                  | eligible, 54.4k, ranked BELOW                   |

- A single G1 composition that solves >= 2 transfer families where START fails exists in 6/8
  replicates (CON1, CON2, CON3, CON4, CON5, CON7). C2 kept one in 1/6 (CON1).
- In the other 5, the composition was:
  - eligible but ranked below: 1 (CON7, by 5.5k of about 60k);
  - rejected on validation: 2 (CON3, CON4);
  - never a candidate, because no validation cell exercises it: 2 (CON2, CON5).
- The same composition class, ((acc + {H}) + v) ~ acc + v + h, is transfer-best in 5/8 G1
  replicates. Extensionally, a recurring reusable composition is present in the supply.
- Own-group (CON:G1) families among newF are <= 1 in every replicate. Even the transfer-best
  composition would give frozen REUSABLE (own group, >= 2 families) = 0/8. The frozen rung is
  structurally near-unreachable with 2 own-group transfer families per replicate.
- SHAM_1 shows the same picture:
  - ((H+v)+acc) has the same covers and the same newF as G1's ((acc+H)+v) in CON1, CON2,
    CON3 and CON7;
  - selection kept it in CON4 and CON5 (1 family each);
  - it rejected it in CON1 (-29k) and CON3.
- The SHAM_0 and OFF_0 transfer-best compositions solve <= 1 new family. They are never priced
  positive.

**Verdict R2: SUPPORTED (partially).** The bottleneck is not ABSENCE: a reusable composition
exists in 6/8 G1 replicates. The mechanism, though, is mostly that the validation set gives no
signal:
- 4 of the 5 missed cases are "not a candidate" or "not eligible";
- only 1 is ranked below the chosen composition by the mean-saving objective.

So the fix is a validation set or objective that sees breadth, not only a re-ranking.

## 3. R3 NON-SPECIFICITY (Archaeon)

**Pool.** 60 random clean schemas (a18._random_schema seeded "ARC3/W6/R3-POOL/v1"; a20_c3
clean() logic; 366 tries):
- 12 have 2 leaves, the same size as G1: 161 instances each;
- 48 have 3 leaves: their wrap has only 6 in-space instances.

**Targets.** qyba, qoda and the 12 fresh G2 families. freaa and frfaa are trivial: their body
reduces to v - acc (H = 0 % first, 0 // last).

**Wrap (v - (S)) covers:**
- G1: 14/14.
- Pool:
  - 0/60 cover qyba or qoda;
  - 0/60 cover any of the 10 non-trivial fresh families;
  - 7/60 cover only freaa and frfaa.
- Size-matched 2-leaf subset: 0/12 on the payoff families.

**Secondary readings:**
- S alone:
  - SHAM_0 covers both payoff families; pool ((last - {H}) + v) covers qoda.
- Any one-move composition of S:
  - pool (v - {H}) covers both qyba and qoda;
  - ({H} + v) and (v + {H}) cover qyba;
  - 16/60 cover >= 1 target, but only freaa, frfaa, frcaa, qyba and qoda (frcaa ~ v - acc - 1).

**Verdict R3: NOT SUPPORTED** for the specific wrap: no random, size-matched, clean schema
reproduces the (v - (.)) route. The claim remains weak in two ways:
- the extensional class is already occupied by SHAM_0 itself, which is the W3 confound;
- 1/60 random clean schemas, (v - {H}), reaches both payoff families by some other single
  composition.

So the credit is "G1 or its sign re-expression". It is not "any broad inner schema", and it is
also not uniquely G1.

## 4. W1-E1: EFFICIENCY vs CAPABILITY OF THE VALIDATION SAVING (18 non-INHERITED C2 selections)

- **Capability.** 13/18 selections are paid >= 79% by cells where START failed at escrow (12 of
  them at >= 100%). Each rests on exactly ONE validation family (3-4 cells) newly solved.
- **Efficiency.** 5/18 are paid 100% by efficiency: 3 MEMORISE, CON1 SHAM_0 (LGG) and CON5
  SHAM_1.
- **G1 arm (CON0/1/2/7).** 4/4 are pure capability; START solved 0/16 validation cells in each.
  The paying family came from ANOTHER group in 4/4:
  - CON0: qhea (SHAM_1);
  - CON1: qrda (SHAM_0);
  - CON2: qzha (NAT);
  - CON7: qkfa (SHAM_1).
- **G1_NC.** 2/2 capability.
- **Caveats:**
  - "START failed" is at 250k, not the 10M ladder;
  - validation hits are not T4-checked, which is also true of select().

## EVIDENCE AGAINST APHRODITE'S CURRENT INTERPRETATION

**X1. Reuse is present in the world; the selector misses it.**
- In 6/8 G1 replicates, one composition of G1 solves >= 2 held-out transfer families where
  START fails, at escrow and T4-qualified.
- The same class, ((acc+H)+v), recurs as transfer-best in 5/8.
- C2 selected such a composition in 1/8.
- "A selected composition rarely recurs" describes the selector plus a 4-family validation
  set. It does not describe the supply.

**X2. Selection is driven by a single cross-group validation family.**
- Every G1 selection was paid by exactly one validation family, and in 4/4 it came from a
  non-G1 group.
- Transfer-good compositions were invisible (no validation hit) or ineligible in 4/5 misses.
- The mean-saving objective ranks near-ties by about 5-10%, which is charge-order noise.

**X3. The frozen REUSABLE rung is nearly unreachable by design.** It requires both own-group
transfer families to be covered by the one selected composition. With the oracle-best
composition, own-group newF is <= 1 in 8/8 replicates. REUSABLE = 0/8 is largely definitional;
this agrees with W1-E2 and W3-E1.

**X4. The paired E1 claim in W1 does not reproduce for the G1 arm.** W1 wrote "4/8 selections
paid by efficiency on cells the start library already solved". On the frozen cells, G1's 4
selections are 100% capability-at-escrow (START 0/16). Efficiency-paid selections are the
MEMORISE/LGG ones (5/18). This favours Aphrodite's side on "SOLVED is the first broken rung",
but it undercuts it on validation: selection saw capability.

**X5. The horizon is depth, not moves.** 22/80 families are unreachable from G1 at any move
count in W5, mostly the other shams' families. A reuse-controlled assay in W5 cannot fix that.

**X6. For balance (supports the interpretation).**
- R1 finds no 2-move horizon.
- R3 finds that the (v - .) wrap route to CON1's payoffs is not produced by random clean
  schemas.
- The SHAM_0 and OFF_0 arms have no multi-family composition at all.

## ONE-LINE VERDICTS

- **R1 composition horizon: NOT SUPPORTED.** 5/80 families at d=2; reachable families are
  mostly d <= 1. The residual barrier is the depth wall (22 INF), plus fragmentation across
  wraps.
- **R2 selection objective: SUPPORTED (partial).** A transfer-better composition exists in 6/8
  G1 replicates. It was lost to "no validation signal / ineligible" (4) more often than to
  ranking (1). This is a selection/validation valley, not absence.
- **R3 non-specificity: NOT SUPPORTED.**
  - 0/60 random clean wraps (0/12 size-matched) cover CON1's payoff families.
  - The credit is shared with G1's sign re-expression SHAM_0, and 1/60 schemas reaches the
    payoffs by another one-move composition. So "causal" means G1's extensional class, not G1
    alone.

## CAVEATS

- Transfer and validation "capability" are measured at escrow only, with no 10M ladder.
- The R2 "transfer-best" composition is chosen with oracle knowledge of the transfer families.
  It measures existence, not what an achievable selector would find.
- The top-6 cap per arm and replicate means other tied compositions were not priced.
- The cover battery is 100 inputs of length 4-9 (the search domain). T4's longer domains (up
  to 200) were not used for equality; T4 was applied only to the priced transfer hits.
- NAT catalogs were untestable in C2 (roles ok = False), so nothing here speaks to NAT.
