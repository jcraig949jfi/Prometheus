# INV_Z4 -- gpt-oss-120b partial blind run: coverage, abstention, paired scores, n

Status: DESCRIPTIVE ONLY. Run incomplete (48/100). No hypothesis decision is
stated or implied; intervals describe a partial subset and are not tests.

Analysis clock (`date -u`): 2026-10-01T01:38Z. Z4 subagent for Hecate; read-only,
no model/API calls, no git writes. Script/output: <scratchpad>/Z4/z4.py, out.txt.

Inputs (as found in worktree hecate-base-role):
- hecate/alien/runs/gptoss/blind.jsonl: 49 lines, 48 unique SIDs.
  SYS-33425 appears twice. Line 25 failed (ok=False, 8 attempts, 429s), and
  line 31 is a successful re-ask. read() keeps the latest row, so 48 are scored.
- hecate/alien/runs/claude/blind.jsonl: 100 rows (comparison).
- Scoring: hecate.alien.analyze.per_system(), which calls the frozen
  hecate.alien.score per-item functions (structure_score, score_t2, score_t3,
  score_claims, score_code) and the prereg LEARNED and behav_score definitions.
  I imported both modules and modified neither.

## 1. Coverage by group (Q1)

Run order is SID-sorted. The 48 scored systems are exactly the first 48 SIDs
in sorted order. The next SID is SYS-52089. dataset.py draws the SIDs at random
(rng.choice over 10000..99998) independently of class, so the sample is
a random prefix with respect to class. It is not ordered by class or by family.

| group        | population | covered | frac | expected at 48/100 |
|--------------|-----------:|--------:|-----:|-------------------:|
| K            | 20 | 10 | .50 | 9.6 |
| A (std)      | 32 | 13 | .41 | 15.4 |
| AADV (adv)   |  8 |  6 | .75 | 3.8 |
| INCOMP total | 30 | 14 | .47 | 14.4 |
| N_DESTROY    | 10 |  5 | .50 | 4.8 |
INCOMP by type (covered/pop): CONJ 4/7, DSCRAMBLE 3/11, SCRAMBLE 2/4, SEDUCTIVE 5/8.

Hypergeometric check (48 draws from 100): AADV at >=6 of 8 has P=.11, and
A std at <=13 of 32 has P=.21. Both are within chance, but the chance tilt
points toward the hardest group. Adversarial aliens are over-represented and
standard aliens slightly under-represented. Pooled-A ("Aall") numbers from
this prefix will therefore look worse than a full-run Aall. H1 uses A-std
only, so it is unaffected by the AADV tilt.
- Covered A std by family: graph 3/8, rewrite 2/8, vm 3/6, map 3/5, tab 2/5;
  K: vm 3, graph 2, rewrite 2, tab 2, map 1 (of 4 each).
- Matched alien-null pairs with both members covered: 5 of 32 std and
  3 of 8 adv. Paired alien-vs-own-null contrasts are therefore mostly unavailable.
- The old RESULTS.json "n" field per group is the population count
  (e.g. A n=32), not the number scored. Its rates are over scored rows only
  (n_blind=29). Read "n" there as the denominator of the population.

## 2. Abstention by group (Q2)

Abstention here means T2 prediction strings of "?" or "unknown". When gpt-oss
abstains it usually abstains on all 12 T2 queries and all T3 steps, and puts a
placeholder identity step(s) in T5 ("rule could not be inferred... return
list(s)"). The frozen scorer gives 0 for each abstained T2/T3 prediction, as
the prereg requires. The T5 identity placeholder scores whatever identity
scores on the eval set, so behav_score for an abstainer is ~<= 0.

| group     | n  | abstain (all 12) | abstain (any) | T1 RULE/UNC/RANDOM |
|-----------|---:|-----------------:|--------------:|--------------------|
| K         | 10 | 0 | 0 (0%)  | 7 / 3 / 0  |
| A std     | 13 | 2 | 3 (23%) | 1 / 11 / 1 |
| AADV      |  6 | 3 | 3 (50%) | 0 / 5 / 1  |
| INCOMP    | 14 | 8 | 8 (57%) | 2 / 11 / 1 |
| N_DESTROY |  5 | 1 | 1 (20%) | 0 / 5 / 0  |
INCOMP by type (abstain any/n): CONJ 3/4, DSCRAMBLE 2/3, SCRAMBLE 2/2,
SEDUCTIVE 1/5. Partial abstention: SYS-19722 (A, vm) has 9/12 "unknown".

Overall 15/48; on the first 29 scored rows 9 (+1 partial), matching "~10/29".
- Ordering: K 0% < DESTROY 20% ~ A 23% < AADV 50% ~ INCOMP 57%. Abstention
  tracks "no rule found" (aliens between K and noise), not aliens specifically.
- Abstention and T1 are loosely coupled: 4 abstainers gave confident T1
  (SYS-13028 RULE .78, SYS-33425 RULE .87, SYS-14535 RANDOM .87, SYS-46959 A
  RANDOM .85); most A non-abstainers were still UNCERTAIN (scored 0.5).
- Mechanism note: abstention lowers T2/T3 and the behav score. It does not
  move the T1 score, which comes only from the verdict. The T1-based H1
  contrast is driven by the RULE-vs-UNCERTAIN verdict mix (K 7/10 RULE,
  A 1/13 RULE) and not by abstention as such.

## 3. Frozen-scorer results and paired comparison with Claude (Q3)

Same SIDs for both models (Claude's rows for the 48 covered systems). Means
over systems. diff = gpt-oss minus Claude, paired on SID.

| group  | metric      | gpt-oss | Claude | diff   |
|--------|-------------|--------:|-------:|-------:|
| K (10) | T1 score    | .806 | .944 | -.138 |
|        | T2 comp     | .814 | .994 | -.181 |
|        | behav score | .268 | .397 | -.130 |
|        | LEARNED     | 6/10 | 10/10 | -.400 |
| A (13) | T1 score    | .510 | .879 | -.369 |
|        | T2 comp     | .352 | .921 | -.569 |
|        | behav score | -.006 | .487 | -.493 |
|        | LEARNED     | 1/13 | 11/13 | -.769 |
| AADV (6) | T1 score  | .447 | .722 | -.275 |
|        | T2 comp     | .071 | .271 | -.200 |
|        | behav score | -.101 | .060 | -.162 |
|        | LEARNED     | 0/6 | 1/6 | -.167 |
| INCOMP (14) | T1 score | .520 | .593 | -.073 |
|        | T2 comp     | .185 | .279 | -.094 |
|        | behav score | -.044 | .012 | -.055 |
|        | LEARNED     | 1/14 | 0/14 | +.071 |
| DESTROY (5) | T1 score | .500 | .806 | -.306 |
|        | T2 comp     | .197 | .729 | -.532 |
|        | behav score | -.094 | .352 | -.445 |
|        | LEARNED     | 0/5 | 2/5 | -.400 |

Mean trivial T2 bar: K .616, A .464, AADV .236, INCOMP .305, DESTROY .393;
gpt-oss T2 comp is below it on every group except K. Claude T1 on same SIDs:
K/A/DESTROY all RULE; AADV 5 RULE 1 RANDOM; INCOMP 10 RULE 3 UNC 1 RANDOM.

Descriptive pattern: the paired gap to Claude is largest on A std
(LEARNED -.77, behav -.49) and smallest on K and INCOMP. gpt-oss learns
6/10 K systems but 1/13 std aliens. Claude learns 11/13 std aliens on these
same systems.

H1 contrast on this subset, descriptive only. Formula:
AUC(K vs INCOMP) - AUC(A vs INCOMP), with the prereg bootstrap (2000, seed
20260930) applied to these 10/13/14 systems.

| model / score       | AUC K | AUC A | est  | boot 95% interval | boot sd |
|---------------------|------:|------:|-----:|-------------------|--------:|
| gpt-oss / T1        | .829 | .475 | .353 | (.162, .546)  | .098 |
| gpt-oss / behav     | .829 | .607 | .221 | (-.015, .455) | .119 |
| Claude same / T1    | 1.00 | .992 | .008 | (.000, .038)  | .011 |
| Claude same / behav | 1.00 | 1.00 | .000 | (.000, .000)  | .000 |
| Claude all 100 / T1 | 1.00 | .981 | .019 | (.000, .048)  | .014 |
| Claude all 100 / behav | 1.00 | .974 | .026 | (.002, .064) | .016 |

Not decisions. The gpt-oss T1 contrast mostly reflects the verdict mix (A std
11/13 UNCERTAIN = 0.5); ties at 0.5 also widen intervals.

## 4. What n would make H1 decidable at the prereg threshold (Q4)

Prereg rule: SUPPORTED iff est >= .10 and CI lower > 0. NOT_SUPPORTED iff
est <= 0 and CI upper < .05. Otherwise INDETERMINATE.

Method: resample the observed gpt-oss per-group score distributions (10 K,
13 A, 14 INCOMP) at group sizes multiplied from the prereg 20/32/30. Take 400
draws and report the sd of the H1 estimate. Caveat: this treats the observed
partial distributions as the truth. Small-sample distributions under-represent
tails, so the sd is optimistic.

| sizes (K,A,N)      | sd T1 | sd behav |
|--------------------|------:|---------:|
| 20,32,30 (prereg)  | .073 | .082 |
| 40,64,60 (x2)      | .047 | .058 |
| 80,128,120 (x4)    | .034 | .040 |
| 160,256,240 (x8)   | .024 | .027 |

sd scales roughly as 1/sqrt(n). Derived requirements:
- SUPPORTED reachable with ~80% power when the true gap is d. This needs
  d - 0.84*sd >= max(.10, 1.96*sd), so sd <= d/2.8 (and <= (d-.10)/0.84).
  - d = .35 (observed T1 point): sd <= .125. The prereg n=100 suffices.
  - d = .22 (observed behav point): sd <= .079. About the prereg n=100
    (sd .082). Simulated P(SUPPORTED-shaped) = .79 at x1 and .97 at x2.
  - d = .15: sd <= .054 (T1) -> ~1.8x prereg (~180 systems). Behav needs ~2.3x.
  - d = .10 (at threshold): P(est >= .10) <= ~50% at any n. Not decidable
    as SUPPORTED with high power.
- NOT_SUPPORTED requires CI upper < .05, i.e. 1.96*sd < .05 -> sd <= .0255.
  That is ~8x the prereg sizes for T1 ((.073/.0255)^2 = 8.2) and ~10x for behav
  (~800-1000 systems). It also requires est <= 0, which a true gap of exactly
  0 gives only ~50% of the time at any n. Under the frozen rule a null
  outcome can only be reached as NOT_SUPPORTED by a model with a negative
  true gap or a very large n. A null at n=100 resolves as INDETERMINATE.
- Claude's sd at full n=100 is .014-.016 (AUC ceiling); gpt-oss is mid-range,
  where AUC variance is largest.

Descriptive implication: the remaining 52 rows reach prereg n; the T1 contrast
would be resolvable at n=100 if the partial effect persists, behav is near the
edge. Nothing here predicts the full-run decision.

## 5. Caveats

- 48% prefix. AADV is over-represented (6/8) and A std slightly
  under-represented (13/32). There are few complete matched pairs (8/40).
- Free-tier trickle across two sessions (09-30 05:40-08:27Z, then 10-01
  00:28-01:06Z, as recorded in the rows). Many 429 retries. The model id
  string is the same in every row. I did not test for drift across sessions.
- Abstention is scored 0 per the prereg; no abstention-excluded rescore was made.
- Only the T1/T2/T5 fields needed for abstention were inspected.
