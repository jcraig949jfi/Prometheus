# RB-2 -- TASK-WORLD AUDIT AND THE SUCCESSOR INSTRUMENT T4 (2026-09-27)

Program: ABSTRACTION COMPOUNDING (reference abstraction G1 = (acc + {H})).
Worker: RB-2 block, host M4, worktree aphrodite-base-role, branch
aphrodite/compounding-2026-09-27. FORENSIC, NOT A DISPOSITION. Nothing here is
Campaign 1 evidence. No frozen file was modified: meta_tribunal.py, a17.py and
every AMENDMENT and *_RESULTS_* file are untouched. The only engine change is a
NEW file, engine/tribunal_t4.py. Seed: APHRODITE/COMPOUNDING/RB2/v1 only.

Operator ruling (2026-09-27), applied: the successor instrument has its own
identity and module; one bridge panel compares the old and new instruments; a
bad task world is not preserved merely for comparability.

## 0. HEADLINE

1. The old regime (V0) yields 0.76 genuinely non-additive, Q2-qualified,
   solvable families per 1,000 draws. Under T4 every one of its non-G1
   survivors is junk: gcd folds whose answer ignores the list's middle and
   last elements.
2. Dropping the permutation test (V1/V2/V6) raises the raw yield to about 47
   per 1,000, but 68% of those solvable survivors are junk: middle-insensitive,
   near-constant, copying an input value, or pow-guard artifacts. The clean
   remainder is about 15 per 1,000. Multiplicative families are still missing,
   because stress at length 200 kills them.
3. The successor world W_T4 uses T4 as Q3, with no permutation test, a
   declared growth domain and junk rejection. It yields 22.7 per 1,000 with
   widened inits (V7) and 29.1 per 1,000 with H1 inits (V8), and every
   survivor is junk-free by T4's checks. That is 30-38x V0.
   - 19.9 / 24.5 per 1,000 are also NOT extensionally G1.
   - Six or seven distinct non-additive schema families have >= 2 solvable
     members each: multiplicative-affine, constant-slope/alternating,
     first/last-slope affine, gcd, mod, fdiv, plus mul in V8.
4. The weak point of the successor world is LEARNABILITY. Only 11-13% of
   survivors fall in the PRISTINE window 0 < p < 1 (1-3 of 4 cells). Most
   survivors are either trivially solved (4/4) or not solved at all, and
   L1-only solves are rare: 23 in V7, 21 in V8.
5. Bridge panel (13 families): 10 disagreements, all explained.
   - T4 rejects 4 of the 5 AMENDMENT 17 catalog-A families as junk. That
     includes BOTH non-G1 OBSERVE families of E1 (hA_fdiv_bf, hA_gcd_al) and
     the G1 OBSERVE family hA_sub_az.
   - T4 admits the order-sensitive and length-bounded-growth families the old
     tribunal cannot certify.
   - Neither instrument admitted a wrong artifact among the 38 near-misses
     tested.

## 1. METHOD

Scripts (all in this directory):

- rb2_common.py. The parameterised copy of k1_supply_census.witness_row, plus
  these helpers:
  - the task-grounded body class;
  - the cached exact Q2;
  - the K7 extensional G1 test;
  - K2 solvability cells, optionally checked by a tribunal.
- rb2_census.py. Stage A reproduces K1: V0's parameters on K1's own sample
  and seed give K1's witness-level counts EXACTLY (all 7 strata, all flags;
  see RB2_CENSUS_ROWS.json "k1_reproduction"). Stage B draws 1,500 per
  stratum from the RB-2 seed. The draws are PAIRED: each draw fixes (op, body,
  final) and one uniform number that picks the init both in H1 = {0, 1} and in
  the widened set {0, 1, 2, first, last}.
- rb2_qualify.py. Runs Q2, the G1 test, solvability and aggregation, and
  writes RB2_AUDIT.json.
- rb2_t4_q3check.py. Checks that the full T4 score of the witness artifact
  agrees with the census-side family profile: 80/80 agree (RB2_T4_Q3CHECK.json).
- rb2_bridge.py. Writes RB2_BRIDGE_PANEL.json.

Definitions:

- **ADMISSIBLE.** For V0-V6: the variant's structural preconditions plus K1's
  non-degeneracy (>= 3 distinct outputs, depends on the last list element, no
  None). For V7/V8: tribunal_t4.family_profile(witness) is admissible.
- **GENUINELY NON-ADDITIVE.** Body b is ADDITIVE iff b(acc,v,f,l) - acc does
  not depend on acc on the grid:
  - acc in {0,1,2,3,4,5,7,10,16,31,97,1000};
  - v in {2,3,5,7,12,30}, f in {2,5,17}, l in {1,3,41,97}.

  Bodies that ignore acc entirely (ACC_FREE) are junk and are not counted.
  The rest are classed by mechanism:
  - AFFINE_SCALE_V: slope depends on v, e.g. acc*v;
  - AFFINE_CONST_SLOPE: e.g. v - acc, 2acc + v;
  - AFFINE_SLOPE_FL: slope depends on first or last, e.g. acc*first + v;
  - NA_<op>: the first non-additive operator on the shallowest acc path.

  These classes are the "schema families" of section 5.
- **Q2.** Exactly a17.qualify(Prov({name: spec}), name, "RB2") for one fixed
  digit-free family name. It is the same computation with the PRISTINE vector
  matrix cached. Checked against a17.qualify: 40/40 identical.
  Caveat: Q2 depends on the family name through the probe pool; hA_fdiv_bf
  passes at size 24 under its catalog name but fails under the RB-2 name.
- **Non-G1 (extensional).** Not equal, on 150 task-domain inputs, to any
  program in G1's coverage: derived_0 bodies x finals, with inits from H1 plus
  the widened set (conservative). This is K7's test.
- **Solvability.** K2 cells: 4 cells per arm, escrow 250k.
  - "Solved" means a dev-consistent hit (K2's upper bound).
  - For T4-world programs we also record the T4-QUALIFIED solve: the first of
    up to 5 hits whose emitted artifact T4 qualifies, as in a17.run_recipient.
  - For V0 programs we record the old-tribunal-qualified solve.
- **Window.** The share of tested survivors with PRISTINE solving 1-3 of its
  4 cells, i.e. 0 < p < 1.
- **Coverage.** Solvability was run on every Q2-passing, genuinely
  non-additive admissible program (union over variants), plus 12 additive
  Q2-passing programs per variant x stratum: 2,567 programs in total.

## 2. THE AUDIT TABLE (all strata; per-stratum detail in RB2_AUDIT.json "table")

N = 10,500 draws per variant.

| Variant | Adm | Non-add | Q2 rate | Non-add Q2 | Not G1 | Solvable (P or L1) | L1-only | Window | Yield /1000 | Not-G1 yield /1000 | Junk (T4 reasons) | Families >= 2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V0 current | 704 | 127 | 0.79 | 13 | 9 | 8 | 4 | 0.19 | 0.76 | 0.38 | 195 | 1 |
| V1 no permutation test | 1902 | 1157 | 0.82 | 879 | 777 | 487 | 54 | 0.19 | 46.4 | 36.7 | 1065 | 6 |
| V2 prefix-extension | 1894 | 1151 | 0.82 | 879 | 777 | 491 | 54 | 0.20 | 46.8 | 37.1 | 1058 | 6 |
| V3 stress 60 | 726 | 144 | 0.78 | 17 | 13 | 10 | 4 | 0.20 | 0.95 | 0.57 | 212 | 1 |
| V4 mod-P values | 974 | 301 | 0.82 | 162 | 146 | 97 | 10 | 0.16 | 9.2 | 8.2 | 389 (+267 wrap) | 3 |
| V5 wide inits | 760 | 181 | 0.75 | 27 | 24 | 8 | 3 | 0.21 | 0.76 | 0.48 | 255 | 2 |
| V6 = V1+V3+V5 | 2108 | 1361 | 0.81 | 1027 | 865 | 507 | 70 | 0.19 | 48.3 | 35.2 | 1238 | 6 |
| V7 T4, wide inits | 1153 | 651 | 0.98 | 649 | 593 | 238 | 23 | 0.13 | 22.7 | 19.9 | 0 | 6 |
| V8 T4, H1 inits | 1092 | 585 | 0.98 | 581 | 533 | 305 | 21 | 0.12 | 29.1 | 24.5 | 0 | 7 |

Column notes:

- "Not G1" = non-additive Q2-passing survivors that are not extensionally G1.
- "Window" = the window fraction over all tested survivors.
- "Yield /1000" = genuinely non-additive, Q2-qualified, solvable families per
  1,000 draws. "Not-G1 yield /1000" is the same, restricted to programs that
  are not extensionally G1.
- "Junk (T4 reasons)" = admitted programs that fail at least one T4 family
  check.
- "Families >= 2" = distinct non-G1 schema families with >= 2 solvable
  behaviours.

The cleaned yields make the comparison fair. Removing the programs T4 calls
junk from the solvable survivors leaves:

| Variant | Solvable | Junk | Clean | Clean per 1000 |
|---|---|---|---|---|
| V1 | 487 | 331 (68%) | 156 | 14.9 |
| V6 | 507 | 377 (74%) | 130 | 12.4 |
| V4 | 97 | 33 | 64 | 6.1 |
| V7 | 238 | 0 | 238 | 22.7 |
| V8 | 305 | 0 | 305 | 29.1 |

The clean V1 remainder has NO multiplicative family (AFFINE_SCALE_V = 0),
because stress at length 200 still removes every product. T4 keeps 55-68
distinct solvable non-G1 multiplicative behaviours.

T4-qualified solves (P or L1): 205/238 in V7 and 285/305 in V8. Most
dev-consistent hits survive T4, so K2's upper bound is close for this world.

Per-stratum yields per 1,000 draws (V7 / V8, non-add Q2 solvable):

| Stratum | V7 | V8 |
|---|---|---|
| add | 44.0 | 52.0 |
| sub | 48.0 | 76.0 |
| mul | 52.7 | 58.7 |
| fdiv | 2.7 | 2.7 |
| mod | 6.0 | 7.3 |
| gcd | 5.3 | 6.7 |
| powr | 0 | 0 |

The "add" and "sub" strata contribute non-additive bodies such as
(v + (acc % first)), (1 + (v - acc)) and (v + gcd(acc, last)). The stratum is
the top operator, not the mechanism.

## 3. WHAT EACH VARIANT ADMITS (JUNK), AND VERDICT

Junk classes use tribunal_t4.family_profile on the admitted witness:

- CONST: < 5 distinct outputs on 60 dev inputs, or modal output > 50%.
- MIDDLE_INSENSITIVE / LAST_INSENSITIVE: changing that list element changes
  the answer in < 20% of probes (input-ignoring, or absorbed by a fixed point).
- COPIES_INPUT: the answer equals some input value in > 90% of probes (leaky).
- FIXED_POINT: the accumulator is constant from step 5 on in >= 90% of
  length-30 probes.
- POW_GUARD: the answer depends on G4's pow guard (an exponent outside 0..32
  silently gives 0).
- NONE_ON_DEV: the witness fails on dev-length inputs.
- WRAP (V4 only): the mod-P answer differs from exact arithmetic (an overflow
  artifact).

Variant findings:

- **V0.** 195/704 junk. Examples: MIDDLE_INSENSITIVE 140, FIXED_POINT 98,
  CONST 97, COPIES 40, POW_GUARD 9. Its only non-G1 Q2 survivors are 9 gcd
  folds, all MIDDLE/LAST_INSENSITIVE. The old regime is simultaneously too
  strict (no order-sensitive or multiplicative tasks) and too lax (junk).
- **V1.** 1065/1902 junk: MIDDLE_INSENSITIVE 932, CONST 351, COPIES 96,
  POW_GUARD 65, and 166 bodies that ignore acc. Dropping the test without
  replacing it lets through tasks whose answer is a function of the last
  element, first and query. REJECT as a world.
- **V2.** Prefix-extension consistency had 0 violations over 10,500 witnesses.
  For a fold witness it is TRUE BY CONSTRUCTION, so as a generator-side check
  it is vacuous and V2 equals V1 up to rng. As an artifact-side oracle-free
  check it would need the hidden accumulator. Hence T4 has no oracle-free
  metamorphic relation (section 4). REJECT.
- **V3.** Stress 60 with counterexample lengths {2, 3, 40, 60} barely moves
  anything, because the permutation test binds first. Junk 212. REJECT.
- **V4.** Mod-P ring semantics admit 138 mul-stratum tasks, but 267 of 974
  admitted are WRAP-dependent overflow artifacts. The G4 artifact cannot
  express reduction mod P, so these are unsolvable or silently different from
  what the DSL computes. 158 fail even at dev lengths under exact semantics.
  REJECT: it changes the DSL's semantics rather than the task world.
- **V5.** Widening the inits alone does little (0.76 per 1,000); the tribunal
  structure dominates. Junk 255, with FIXED_POINT 143 from inits like "first"
  combined with gcd/mod. Useful only together with T4.
- **V6.** Inherits V1's junk (1238/2108). REJECT.
- **V7 / V8 (T4).** 0 junk by construction. Residual risk: the thresholds
  are declared parameters (section 7).

## 4. THE SUCCESSOR INSTRUMENT: TRIBUNAL_T4_ORDER_AWARE_v1

Module: roles/Aphrodite/engine/tribunal_t4.py, NEW, sha256
62aecd9a05dca7e8192c0cf0d99f7904e26150964fe32590d23a0aeebdbc69e2 (declared
final to the Aphrodite seat; any fix becomes a separately named v2).
Self-test: `python roles/Aphrodite/engine/tribunal_t4.py` gives 15/15 PASS:
- the evaluator equals run_program;
- the alternating sum qualifies under T4 and is rejected by the old
  permutation test;
- a commutative decoy is rejected;
- the product qualifies with L_max = 25 and fails the old stress test;
- constant, input-ignoring, overflowing and pow-guard families are rejected
  with the right reason;
- plain sum is qualified by both;
- the None-artifact boundary raises;
- digit-bearing names are rejected;
- the profile is deterministic.

Interface (same shape as MetaTribunal):
- use_provider(prov): the provider only needs witness(family);
- TribunalT4.after_freeze(artifact, family), with the same boundary checks:
  frozen generation, None artifact;
- .score(artifact) -> dict;
- .qualified(score) -> bool.

Components (all golds come from the hidden witness):

1. **held_out_extrapolation.** 150 inputs, lengths [20, min(60, L_max)].
2. **stress_at_domain_max.** 40 inputs at length L_max (200 for bounded
   families).
3. **counterexample_accuracy.** 40 inputs; lengths {2, 3, min(80, L_max),
   L_max}; constant runs every third input; query in {1, 2, random}.
4. **order_battery_accuracy.** 30 base lists x 8 follow-ups:
   - reversal, ascending sort, descending sort;
   - an adjacent swap of two middle elements;
   - prefix extension, prefix truncation;
   - a middle-value change, a duplicated middle element.

   These are metamorphic FOLLOW-UP INPUTS checked against the oracle, never
   assumed equal. Valid for every fold, order-sensitive or not.
5. **family_admissible.** tribunal_t4.family_profile (section 3 junk
   classes) plus the declared-domain rule, plus no None and no pow-guard hit
   on any battery gold (NONE_ON_DOMAIN, GUARD_ON_DOMAIN).

qualified = family_admissible AND components 1-4 each >= 0.99.

Why there is NO oracle-free metamorphic relation:

- The only relations valid for ALL left folds final(fold(init, body, xs)) are
  statements about the hidden state, e.g. prefix-continuation
  fold(xs+[y]) = final(body(state(xs), y)).
- A black-box artifact returns final(state), not state, so the relation
  cannot be checked from the outside.
- Checked on the emitted fold itself, it is true by construction (V2: 0
  violations in 10,500).
- An oracle-free test earns its keep only where gold is unavailable. The
  declared domain removes that region: gold exists everywhere T4 tests.
- So T4 spends that budget on oracle-checked follow-ups, which catch
  order-blind near-misses. Example: (v + 1)*first near-misses of the census
  gcd family score 0.68 on the order battery.

Growth, handled honestly:

- L_max is the largest rung of (20, 25, 30, 40, 60, 80, 100, 150, 200) such
  that the witness is total, with no None, ceiling or pow-guard hit, on 46
  probes at that rung and at every lower rung. The probes are 6 extreme lists
  x 5 queries plus 16 random ones. The dev lengths 2-9 must also be total.
- L_max < 20 gives DOMAIN_TOO_SHORT: the family cannot show extrapolation
  beyond 2x the dev length.
- Products therefore get L_max = 25 (30^25 < 1e40 <= 30^28) and are tested
  honestly on that declared domain.
- Overflow artifacts cannot be admitted: any None or guard gold anywhere on
  the batteries rejects the family.
- Measured L_max over V7 admissions: 200: 837, 100: 26, 60: 6, 30: 1,
  25: 249, 20: 34.

Hazard found and fixed in T4 (and still latent in the old tribunal):

- The emitted artifact extracts EVERY integer in the prompt, including digits
  in "Family <name> over:". A family name with a digit silently prepends
  list elements.
- My first stage-2 run used names like rb2q3_7 and produced a spurious
  41/80 profile-vs-Q3 disagreement. That run was discarded and redone with
  letter-only names.
- T4 now raises ValueError on digit-bearing names. Catalog names such as
  hA_add_ah are unaffected. Keep W5 names letter-only.

## 5. THE SUCCESSOR TASK WORLD W_T4 (recommended) AND QUALIFICATION CHAIN

Candidate distribution:

- per stratum op in {add, sub, mul, fdiv, mod, gcd, powr}: G4 bodies whose top
  operator is op and which mention acc and v;
- finals from FINAL_SPACE that mention acc;
- inits from {0, 1, (1 + 1), first, last};
- inputs as today: values 2-30, query 3-97, dev lengths 4-9.

Recommendation on inits: widening is OPTIONAL.

- V8 (H1 inits) yields MORE solvable survivors (29.1 vs 22.7 per 1,000),
  because PRISTINE searches H1 inits only.
- V7 adds init diversity. Its extra families are mostly reformulable (e.g.
  init first).
- Take widened inits only if the campaign wants tasks that PRISTINE
  under-covers. That is a design choice to freeze, not a free improvement.
- powr gives about 0 admissible under T4 in both. pow bodies either explode,
  hit the guard, or collapse to 0/1. Drop powr from the strata or accept
  that it is empty.

Qualification chain:

- **Q1 (unchanged).** The witness is a program in the declared grammar.
- **Q2 (unchanged).** Exact a17.qualify: dev size <= 24 discriminates the
  witness from all PRISTINE-reachable wrong vectors. The pass rate in W_T4 is
  0.98, because T4's non-degeneracy removes most of what Q2 used to kill.
- **Q3 = T4** on the witness artifact.
- **Q4 replaced by a LEARNABILITY WINDOW WITH A FLOOR.** In a 16-recipient
  PRISTINE pilot, 1 <= T4-qualified solves <= 12.
  - The old Q4 had a ceiling (<= 8/16) but NO floor, so E1's non-G1 OBSERVE
    families were unsolvable by construction.
  - Optional reference-free floor extension: also accept families that
    PRISTINE solves at 16x escrow (4M charges; K4 shows the 8-3,527x gap).
    Never define the floor using L1 or any library under test.
- **Stratification for a compounding assay.** Draw OBSERVE and VALIDATE
  families so that at least 2 schema families each contribute >= 2 members
  (section 2 shows 6-7 such families exist).

Measured expectation per 1,000 draws per stratum (V7 / V8):
- non-additive, Q2, solvable: add 44/52, sub 48/76, mul 53/59, fdiv 2.7/2.7,
  mod 6.0/7.3, gcd 5.3/6.7, powr 0/0;
- inside the 4-cell PRISTINE window: about 11-13% of these.

With 32 draws per stratum (the A17 foundry size), expect about 1-2 window
families per productive stratum. The foundry needs roughly 4-8x more draws
per stratum for 4 accepted families per stratum.

## 6. BRIDGE PANEL (RB2_BRIDGE_PANEL.json)

The witness artifact was scored under both instruments. Near-misses are up to
5 PRISTINE hits on a size-4 dev set, scored under both.

| Family | Source | OLD | T4 | Why they differ |
|---|---|---|---|---|
| hA_add_ah | A17-A OBSERVE, G1 | Q | Q | agree |
| hA_sub_az | A17-A OBSERVE, G1 | Q | reject | acc - v//last: v//last = 0 whenever last > 30, so the output is near-constant (mode 0.77) and middle sensitivity is 0.17. T4 calls it junk. |
| hA_fdiv_bf | A17-A OBSERVE, non-G1 | Q | reject | Init 1, acc // gcd(v, last) is absorbed at 0 after the first shared factor. Output is in {1, first}: FIXED_POINT, MIDDLE/LAST_INSENSITIVE. |
| hA_gcd_al | A17-A OBSERVE, non-G1 | Q | reject | gcd(last, v*acc) saturates at a divisor of last. MIDDLE/LAST_INSENSITIVE. |
| hA_gcd_bf | A17-A VALIDATE | Q | reject | CONST plus insensitive (gcd collapses to 1). |
| kb_mod_onemodaccv | K2 pool | Q | Q | agree (non-additive body, but extensionally G1 per K7) |
| kb_powr_lastdivv | K2 pool | Q | reject | pow(acc, last//v) with init 0 gives 0/1 dynamics; the pow guard is hit when last//v > 32; L_max is None. The old tribunal passed it because the guard makes the answer total and permutation-invariant. |
| kb_mul_gcdvacc | K2 pool (Q2 fails) | Q | reject | gcd(v, acc) from 0 collapses to gcd of all: FIXED_POINT, insensitive. |
| kb_gcd_absaccv | K2 pool | Q | Q | agree (the |acc+v| family) |
| s_alt_sum | designed, (v - acc) | reject | Q | Order-sensitive: OLD fails permutation invariance only; accuracy is 1.0 everywhere. |
| s_product | designed, acc*v | reject | Q | OLD: stress 0.0, extrapolation 0.39, counterexamples 0.45 (overflow golds are "None", artifact says "overflow"). T4: L_max = 25, all 1.0. |
| s_census_na_gcd | V7 survivor (1, v + gcd(first, acc), first*acc) | reject | Q | Order-sensitive gcd recurrence: OLD fails permutation only. |
| s_census_affine_scale_v | V7 survivor (0, last + v*acc, acc) | reject | Q | OLD fails both growth and permutation. |

Summary:

- 10 disagreements. The OLD tribunal admits 6 families that T4 calls junk,
  including BOTH non-G1 OBSERVE families of E1. T4 admits 4 legitimate
  families (order-sensitive or length-bounded growth) that OLD cannot certify.
- Near-misses: 38 hit artifacts scored.
  - No wrong artifact was admitted by either instrument.
  - The 10 near-miss disagreements (s_alt_sum, s_product) are all
    EXTENSIONALLY CORRECT programs that OLD rejects for the same structural
    reasons as their witness.
  - The s_census_na_gcd near-misses, (v + 1) sums times first, are rejected
    by both. T4 rejects them on accuracy and on the order battery (0.68).

Consequence for E1: its OBSERVE set was two G1 families plus two T4-junk
non-G1 families. So "no NEW abstraction" was already forced by the task world
before any improver ran.

## 7. OPEN RISKS

- **Declared thresholds.** K_DISTINCT = 5, MODE_MAX = 0.5, SENS_MIN = 0.2,
  COPY_MAX = 0.9, ABSORB_MAX = 0.9 are judgement calls, not derived.
  - hA_sub_az sits near the line (sensitivity 0.17-0.18).
  - A threshold sweep was not run. It should be, before freezing, if the seat
    wants robustness evidence.
- **Learnability is the new bottleneck.** The window fraction is 0.11-0.13
  and L1-only solves are 21-23. W_T4 fixes supply, not the compounding signal.
  The within-G1-span efficiency result of K5 may simply reappear.
- **Mechanism classes are coarse.** The body class groups bodies by operator
  and affine shape. Two AFFINE_SCALE_V members can still be one schema up to
  the finals.
- **Metric caveats.**
  - Solvability is 4 cells per arm, so the window estimate is noisy.
  - "Solved" is a dev-consistent hit. T4-qualified solves are also reported
    and are close (205/238, 285/305).
- **Q2 and the family name.** Q2 depends on the probe pool, which depends on
  the family name. Near-threshold families flip.
- **No depth-3 measurement.** Nothing here measures W5 (depth-3 G5 bodies).
  T4 does not depend on the grammar, but W5 yields, guard rates and L_max
  distributions are unmeasured.
- **RB-1 dependency.** The novelty ruler (tier3e key) is not repaired here.
  "Not G1" in this report is the K7 extensional test, not the ruler.

## 8. EXACT HOOK FOR THE APHRODITE SEAT (new amendment; no existing file edited)

a17.py is frozen, so the switch belongs in the successor driver (e.g. a new
engine/a18.py frozen under AMENDMENT 18). The seat said it will freeze against
the sha256 above. Replace the two tribunal constructions:

```python
import tribunal_t4 as T4
TRIBUNAL = "T4"            # frozen in the amendment

def make_tribunal(prov, fam, art):
    if TRIBUNAL == "T4":
        T4.use_provider(prov)
        return T4.TribunalT4.after_freeze(art, fam)
    M.use_provider(prov)
    return M.MetaTribunal.after_freeze(art, fam)
```

Use it in job_q23 (Q3 on the witness) and in run_recipient (per-hit
qualification): `tr = make_tribunal(prov, fam, art); ok = tr.qualified(tr.score(art))`.

- Keep M.artifact_for(fam, prog, EMITTER=2) for emission.
- Family names must be letter-only.
- Q4 becomes: `1 <= sum(r["qualified"] for r in pilot) <= 12` (16 recipients).
