# AUDIT Z1 -- executable semantics of the Pass-4 attacks (rounds 1 and 2)

Auditor: subagent for Hecate, 2026-09-30. Read-only except this file. No
git writes, no model/API calls. Scratch re-runs in
.../scratchpad/Z1/ (copies of each pass4/ dir and, where imports need it,
the whole world dir).

Scope: the 5 programs that reached Pass 4.
  Round 1 (roles/Hecate/prereg/2026-09-30_pass4_round1/PREREG.md):
    HT-71b65251aa W3, HT-321a8fd8e0 W1, HT-5b0b3ebb8d W4
  Round 2 (roles/Hecate/prereg/2026-09-30_pass4_round2/PREREG.md):
    HT-8a87057933 W5, HT-55162c0ac0 W6
Known, not re-reported: K1 (5516 ORIG at one carrier), C2 (321a ALT fixed
by counting). K13 noted "5516's failed Pass-4 replication is a case the
table does not cover" -- see F1, which resolves it.

## Re-run summary (all within 2 min CPU each)

| world | scripts re-run | rows vs committed | outcome fields vs committed |
|---|---|---|---|
| 71b6 W3 | attack.py, evaluate.py | byte-identical | R, ORIG, ALT, controls, predicate identical |
| 321a W1 | attack.py, evaluate.py | identical except per-row cpu_seconds | identical |
| 5b0b W4 | attack.py, evaluate.py | identical except _META cpu row | identical |
| 8a87 W5 | alt_controls.py, attack.py, evaluate.py | byte-identical (rows, alt_control_rows) | identical incl. ALT_ATTAINABILITY |
| 5516 W6 | alt_controls.py, attack.py, evaluate.py | identical except cpu_seconds | identical |

Completeness: every specified seed/level/arm row is present (71b6 170 =
10x7 + 2x10x5; 321a 302 = 15 arms x 20 seeds + 2 exhaustive; 5b0b 481 =
60x4 + 60x4 + meta; 8a87 160 + 50 control rows = 16 arm-sets x 10 + 5 x 10;
5516 441 = 70x4 ALT + 3 ORIG variants x 4 x 10 + R 4x10 + runinfo). No
error/failed rows, no silently dropped runs found. Every world records
attempts = 1.

## Per-attack table

Defect classes: OK; TAUT = outcome fixed by construction/counting
(round-2 PREREG item 2 forbids admitting such attacks); READ = an
implementer's reading turns the recorded value against its substance;
UNREACH = the clause is unattainable in the world as built (design);
OPER = operationalisation narrower than the attack text; KNOWN = K1/C2.

| program | attack | recorded | re-derived | class |
|---|---|---|---|---|
| 71b6 W3 | R | reproduced (acc 0.7437 = L2, depth 1.307 <= 1.4, rho 0.735 >= 0.4; twin acc 0.7009 fails) | same | OK |
| 71b6 W3 | ORIG | fired (L1 0.74355 >= 0.7437-0.005; depth 1.0 <= 1.307) | same; fires at all 4 thetas, not one-level-only | OK |
| 71b6 W3 | ALT | NOT_ELIGIBLE x2 (gap V1 0.0000, V2 0.00035 < 0.02) | same; gap <= 0.0043 for every one of 42 speaker variants probed | UNREACH (F4) |
| 321a W1 | R | reproduced (k1-3 rate 0, k4 0.589 ... k8 1.0) | same | OK |
| 321a W1 | ORIG | fired (d3: 0 at k1, 1.0 at k2; d5: 0 at k<=2, 0.882 at k3) | same; exact integer zeros | TAUT, benign (F3) |
| 321a W1 | ALT | PASS (K code 3 > K maj 0) | same | KNOWN C2 |
| 5b0b W4 | R | reproduced (MH OR 2.06, p 2.2e-9; twin OR 1.08) | same | OK |
| 5b0b W4 | ORIG | fired (0/20 strata with outcome variance; fail 1.0 iff endpoint in disabled interior) | same, on round-1 and R rows | OK (fixed by round-1 world, which was the claim under attack) |
| 5b0b W4 | ALT | FAIL (OR 0.443, p 6.5e-5; twin 1.11) | same; FAIL/NOT_ELIGIBLE under every alternative reading | OPER (F5) |
| 8a87 W5 | R | reproduced (pooled 0.330, 10/10 seeds <= 0.50) | same | OK |
| 8a87 W5 | ORIG | fired (1278 vs 1278, ratio 1.000 <= 1.10) | same; equal per seed AND in valid_deleted | TAUT (F2) |
| 8a87 W5 | ALT | FAIL (A1 2361/3926 = 0.601 > 0.50; A2 2361/2759 = 0.856 > 0.80) | same; control-first attainability verified (PC 0.093/0.132, twin 0.856/1.217) | OK |
| 5516 W6 | R | NOT reproduced (mean ari_corr -0.111, |.| > 0.1) | ari_ftle 1.0 on 10/10; S2 diff 1.111 >= 0.5 | READ (F1) |
| 5516 W6 | ORIG | fired: false (r 0.2 only) | -- | KNOWN K1 |
| 5516 W6 | ALT | FAIL (A1 = 1.0 - 1.0 = 0.0 < 0.2; A2 pooled rho 0.369 < 0.6) | same; all 7 levels x 10 seeds present | OK |

Exact-vs-float check: every firing comparison above clears its threshold
by a margin far larger than float error (closest: 8a87 ORIG ratio 1.000
vs 1.10, integer counts; 321a zero rates are integer counts). No C5-type
float-boundary case found.

## Findings

F1 -- 5516 W6 R "reproduced: false" is a reading artefact (READ).
  Changes a recorded outcome: YES for the R field; NO for the predicate or
  the verdict (PARK rests on ALT FAIL).
  The implementer read "correlation grouping stays at chance" as
  |mean ari_corr| <= 0.1 (NOTES.md, frozen before the run). Treatment
  ari_corr mean is -0.111 (sd 0.103 over 10 seeds): correlation grouping is
  BELOW chance, i.e. it does not group at all. The FTLE readout groups at
  ARI 1.0 on 10/10 seeds; the round-3 frozen statistic S2
  mean(ari_ftle - ari_corr) = 1.111 >= 0.5 (spec.json) holds; the null twin
  does not group (-0.014). The evaluator itself logs the anomaly ("fails
  ... because it is BELOW chance"). In substance the replication
  reproduced. This answers K13's open item ("5516's failed Pass-4
  replication is a case the table does not cover"): no uncovered case
  exists in substance -- the table's ALT-fail -> PARK row applies.
  Sibling of K1 (a recorded boolean wrong in substance because of a
  one-sided operationalisation). Recommend annotation: "R reproduced in
  substance (S2 1.11); recorded false under a two-sided |ARI| <= 0.1
  reading". A ruling is not needed for the verdict.

F2 -- 8a87 W5 ORIG is fixed by construction (TAUT), contrary to the
  round-2 PREREG's own admission rule.
  Changes a recorded outcome: NO (fired is correct; SAT adds nothing in the
  original world).
  In the original world every stored clause is a single-channel equality
  and the window is SAT before each append, so all older clauses on the
  new observation's channel k hold one value v != new value. Core-guided
  repair (delete oldest clause of a 2-clause MUS, repeat until SAT) and
  channel-reset (delete all older k-clauses) therefore delete exactly the
  same set at every UNSAT event. Re-run confirms: errors equal per seed
  (133,126,...,122; total 1278 = 1278) and valid_deleted 2775 = 2775. The
  PREREG justified "expected FIRE" empirically ("round 3 found every MUS
  was a same-channel pair") and wrote an arithmetic check only for ALT;
  item 2 ("for each attack ... no attack is admitted whose outcome is fixed
  by counting or construction") was not applied to ORIG. The ALT (relational
  world) is the informative test and it FAILed, so nothing rests on ORIG.
  Recommend annotation: "ORIG identical-by-construction; ratio 1.000 is a
  logical identity, not a measurement".

F3 -- 321a W1 ORIG is fixed by construction (TAUT, benign; round 1 had no
  admission rule).
  Changes a recorded outcome: NO.
  The attacker decodes the two further codes with the same coset-leader
  (nearest-codeword) decoder; "0 for k <= t" is then a theorem for any
  code of minimum distance d, and the k = t+1 step is near-certain with
  exhaustive 2^k reports (d3 rate 1.0, d5 0.882). The attack can only
  fail through a bug. Its conclusion ("the rule is minimum-distance
  decoding") is true by round-1 construction (world.py decodes by coset
  leader), so KNOWN_ANALOGUE_FOUND stands. Together with C2, BOTH 321a
  Pass-4 attacks were decided by construction; the PROBING verdict carries
  no measured content beyond R. Supports C2's recommendation.

F4 -- 71b6 W3 ALT eligibility gate is unreachable for speaker variants in
  this lexicon (UNREACH).
  Changes a recorded outcome: NO (NOT_ELIGIBLE twice -> PARK, correct;
  the PARK reason K13 asked for is this).
  Scratch probe (attack.run_seed, 3 seeds x 1000 contexts): alpha in
  {0.25,0.5,1,2,4,8,16} x 6 cost vectors on ALL/SOME (42 variants): the
  largest L2 - L1 accuracy gap is 0.0043 (alpha 1, cost 0.5 on ALL_*),
  < 0.02 by ~5x. With 4 utterances over 3-4 objects, L1 already resolves
  the implicature; L2 is the exact Bayes inverse of the sampled S2 but
  rarely changes the argmax. The PREREG allowed "one other speaker
  variant", so the ALT was effectively decided by the world's lexicon
  before any listener ran. Round 1 had no control-first rule; round 2's
  would have caught it. Recommend the PARK reason read: "ALT NOT_ELIGIBLE
  twice; eligibility gap unattainable for speaker variants in this
  lexicon (max 0.004 over 42 variants, audit Z1)".
  Also noted (OK, not a defect): treatment accuracy is 0.7437 = fixed L2
  at every theta, so the ORIG accuracy clause is decided by L1 vs L2
  (0.74355 vs 0.7437), the 0.39% argmax-disagreement rate.

F5 -- 5b0b W4 ALT measures supporting-path exposure, not belief failure
  (OPER).
  Changes a recorded outcome: NO.
  fail := any transition of the BFS-shortest TRUE pre-shift path is
  removed. In the ALT world no belief ever becomes false (reach_fail
  0/1788; the evaluator logs this), so "fragile" is exposure only, a
  property of (s, t) and path length, independent of the agent's witness.
  Re-derived under the alternative readings from the committed rows,
  stratified as the PREREG says:
    supporting path x (decile, support_len): OR 0.443  (recorded) -> FAIL
    agent witness x (decile, witness_len):   OR 0.201, p ~0   -> FAIL
    agent witness x (decile, support_len):   OR 0.229, p ~0   -> FAIL
    reach_fail (belief false after shift):   OR undefined     -> NOT_ELIGIBLE
  Every reading gives PARK. The ALT world as built cannot exhibit belief
  failure, so even a true fragility mechanism could only show as exposure;
  record as "ALT world cannot falsify beliefs (reach_fail 0)".

F6 -- Checks that came back clean (no defect).
  - K1 sibling search (attack run at one level only): 71b6 ORIG fires at
    all 4 thetas; 321a ran both further codes over k 1..8; 5b0b ORIG on
    round-1 AND R rows; 8a87 single-condition attack by PREREG design;
    5516 ALT ran all 7 levels x 10 seeds. Only K1 itself is one-level.
  - C2 sibling search (pass fixed by counting): no other ALT PASS exists;
    the ALT FAILs in 8a87 and 5516 passed control-first attainability
    (positive control meets, twin fails each clause) and were re-derived
    exactly; 5516 A1 = 0.0 arises from data (non-chaotic r 0.65/0.8 group
    at ARI 1.0), not from the ARI cap alone.
  - Thresholds, seeds and levels match the PREREGs in code: 71b6
    (0.005/0.02/0.01/0.8/0.5, seeds 100-109), 321a (seeds 100-119, 200
    coalitions, exact zero), 5b0b (OR 1.5, p 0.01, 60 seeds, null twin
    same count), 8a87 (0.50/1.10/0.50/0.80, 10 seeds), 5516 (0.8 on 9/10,
    >= 5 levels, 0.2, 0.6).
  - Controls are computed and printed before treatment statistics in all
    five evaluators; cheats are injected and detected by the same rule as
    the treatment.

## Bottom line

No recorded predicate or verdict changes. One recorded field is wrong in
substance (F1: 5516 R reproduced). Two ORIG attacks are logical identities
(F2 under a PREREG that forbade them; F3 in round 1), one ALT gate was
unreachable by design (F4), one ALT measures exposure because its world
cannot make beliefs false (F5). Annotations recommended for F1, F2, F4;
F3 strengthens C2.
