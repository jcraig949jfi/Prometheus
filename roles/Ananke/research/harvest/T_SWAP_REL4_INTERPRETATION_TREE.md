# T-SWAP-REL4 interpretation tree (inference harvest, 2026-09-30)

Status at writing: REL4 has ALREADY RUN (E-ANANKE-W-W; plan frozen by commit 017259a48 before the first
run). Its follow-up check REL5 passed (E-ANANKE-W-X, plan 22b9bbd51), and the chosen rule is promoted as
prometheus/ananke/swap_rel.py. AUDIT3 (E-ANANKE-W-Z, plan 6f25dc642) then applied it to 124 of the 249
audited groups. So this tree is written as the pre-registered outcome space, with the realized branch
marked. Its main use is to decide whether ANY further PTE observation on this line is worth making, and
if only one more is made, which one.

What REL4 is (one line): a false-certificate-rate (FC) and power comparison of interval constructions for
the relative carrier-swap certificate (FLIP_REL / NO_EFFECT_REL / CHANCE_REL on paired pair statistics
DF, DN). It is a STATISTICS experiment on synthetic pair data plus known-answer engine plants. It
measures no new PTE mechanism.

## Level 0 -- what REL4 can and cannot discriminate at all
- CAN: whether a given interval rule keeps FC <= 1% at the modelled boundary truths for P >= 32 pairs,
  and how much power it has near normal accuracy ~ 1.
- CANNOT:
  - whether the models (W-Q worst/realistic/hetero, W-X DEGEN) cover the dependence structure of REAL
    specimen pair statistics;
  - whether any specimen's carrier reading is mechanistically right. A certificate is a statement about
    swap-follow rates, not about mechanism;
  - anything about search, physics or retention.
- STRONGEST GENERAL ALTERNATIVE for every branch: the result is a property of the simulation models,
  not of real PTE data. Real pairs are dependent within specimen x offset groups, clustered by clock
  phase (W-R) and seed-sensitive near thresholds (W-Z).

## Level 1 -- pre-registered outcome branches (PLAN s4)
B1 no hybrid FC-eligible (all fail FC somewhere)
B2 a hybrid eligible but none meets the power bar (FLIP/NO_EFFECT power >= .80 at p=.99, P64 K11)
B3 a hybrid eligible and promotable  <-- REALIZED (H2, variance-floored BOOTT)
B4 H0 (REL3) wins ties / nothing beats it
B5 controls fail (H0 does not reproduce W-U; T90 or PCT does not fail) -> harness defect, no conclusion

### B3 (realized): H2 promotable
- DISCRIMINATES:
  - REL3's high-accuracy "blind spot" (p_min 1.0 for FLIP/NO_EFFECT at P32-64) came from the interval
    construction (infinite t* on degenerate resamples), not from the data. H2 removes it: P64 K3 realistic
    p=.99 FLIP power goes from .157 to 1.000.
- DOES NOT ESTABLISH:
  - FC control where H2 actually differs from REL3. The REL4 grid never produced degenerate resamples at
    the boundary truths; H2 = H0 at 1295/1296 point-verdicts. This gap motivated REL5.
- STRONGEST ALTERNATIVE: H2's floor is anti-conservative in a degenerate regime the grid did not visit.
- EVIDENCE STRONGER: the W-U finding that BOOTT is the only candidate at P32. EVIDENCE WEAKER: any claim
  resting on REL3's NOT_ELIGIBLE at high accuracy.
- SMALLEST NEXT EXPERIMENT: a targeted FC check on near-degenerate boundary truths, with a must-fail
  zero-width control = REL5. WORTH IT: yes, and it was run.

### REL5 sub-branches
R5a H2 FC <= 1% on DEGEN and the zero-width control fails  <-- REALIZED (max FC .22% F/N, .40% C; ZW
    fails at 9 point-verdicts, all P32 d=.95)
R5b H2 fails FC on DEGEN -> promote REL3 with the documented blind spot
R5c ZW does not fail -> the check is uninformative
- R5a DISCRIMINATES: the floor does not cause false certificates where it acts, in the one regime that
  reaches degeneracy (P32, d = .95).
- R5a DOES NOT ESTABLISH:
  - anything at P64+ (degeneracy essentially unreachable there, so H2 = H0 on tested data);
  - heavier-skew nulls, e.g. a near-constant block balanced by rare extreme pairs, like W-W's synthetic
    case.
- STRONGEST ALTERNATIVE: an untested skew pattern exists in real specimens for which the floor inflates
  FC.
- EVIDENCE CHANGE: the promotion of swap_rel.py is justified within the tested envelope; its scope note
  is necessary, not decorative.
- SMALLEST NEXT EXPERIMENT: none on synthetic data. The next useful question is empirical. Do real
  specimen pair arrays ever sit in the degenerate regime? The W-Z pair arrays (workers/W-Z/out/pairs/,
  124 groups) answer this with ZERO new engine compute: count resamples with sd* = 0 per real group.
  WORTH IT: yes (minutes of CPU, inference-grade). If they never reach it, H2 = H0 on all real data and
  the promotion changed nothing observable, which is itself a finding.

## Level 2 -- what the promoted rule has since produced (AUDIT3), and its branches
A3a predictions Pa, Pb held; consistency >= 95%          (not realized)
A3b predictions held; consistency < 95%                  <-- REALIZED (92.7%, 279/301)
A3c predictions failed                                   (not realized)
- A3b DISCRIMINATES: relative verdicts near the certificate threshold (|z| ~ .34-.62, normal lo99 .62-.75)
  flip between a certificate and INDETERMINATE across seeds. There are ~10 group-level events. No
  certificate flips into a different certificate.
- A3b DOES NOT ESTABLISH:
  - whether those groups carry a partial transfer or none; that is exactly what is seed-unstable;
  - anything about the 125 uncovered groups.
- STRONGEST ALTERNATIVE: the seed sensitivity comes from within-group dependence (arms share one normal
  run). The pair bootstrap treats the 256 pairs as independent, but trials within a pair and arms within
  a group are not. Intervals near the threshold are then too narrow, and label flips are expected. This
  would make near-threshold certificates, not just labels, unreliable.
- EVIDENCE CHANGE:
  - WEAKER: every carrier claim resting on a single certificate at intermediate z. That covers 19
    PARTIAL FLIP_REL rows, the 22 CARRIER-PARTIAL groups, and the W-O/W-Q/W-U counts in that z band.
  - UNCHANGED: COMPLETE transfers (z CI containing -1), which never flipped class.
- SMALLEST NEXT EXPERIMENT: a REPLICATE-SEED re-run of only the ~10 seed-sensitive groups plus a matched
  set of ~10 stable intermediate-z groups. Two further namespaces, same frozen rule.
  - Estimand: the per-group label agreement rate across 3 seeds.
  - Kill criterion: if the stable controls also flip at a similar rate, near-threshold labels are
    seed noise, and the correct instrument change is a replicate-seed requirement (or a group-level
    interval) for any claim at |z| < .7.
  - ~2-3 core-h.
  - WORTH IT: yes, IF anyone will make carrier claims at intermediate z. Otherwise the cheaper decision
    is policy only: forbid single-draw carrier claims at |z| < .7 and stop.

## Level 3 -- if REL4's line produced the LAST PTE observation for a while
The single most valuable next observation on this line is NOT a bigger sweep. It is the ZERO-COMPUTE
degeneracy census on W-Z's saved pair arrays (Level 1, R5a), followed only if needed by the ~10+10 group
replicate-seed check (Level 2). Together they decide whether the promoted instrument's two known gaps
(untested degenerate regime at P>=64; seed sensitivity near threshold) matter for real data.
Neither needs a campaign.

What REL4 should NOT be used to claim, even after all this:
- that any specimen's MECHANISM is known (a FLIP_REL means the swap moves the readout toward the
  partner, not how);
- that intermediate-z (PARTIAL) groups carry a partial transfer (seed-unstable);
- that the 84% "stay CHANCE" rate from W-O generalizes. It was an absolute-rule figure; under the relative
  rule 48 of 314 covered absolute-CHANCE rows are FLIP_REL (W-Z).

## Decision summary
| branch | realized | next step | worth it |
|---|---|---|---|
| REL4 B3 | yes | REL5 targeted FC check | done |
| REL5 R5a | yes | degeneracy census on real pair arrays (no engine compute) | yes (minutes) |
| AUDIT3 A3b | yes | 10+10 group replicate-seed check, OR a policy ban on single-draw claims at abs(z) < .7 | only if intermediate-z claims will be made |
| bigger sweep over the 125 uncovered groups | -- | -- | NO (adds counts, not discrimination) |

## RESULT OF THE ZERO-COMPUTE DEGENERACY CENSUS (run during the harvest, 2026-09-30 ~23:00Z)
The census recommended in Level 1 / Level 3 was run on W-Z's saved real pair arrays
(workers/W-Z/out/pairs/, 124 groups, 439 group-arms with >= 32 valid pairs):
- group-arms with ANY zero-SD resample on DF or DN: 0 / 439 (max share 0.0);
- group-arms where the H2 certificate differs from REL3's BOOTT certificate: 0 / 439.
CONCLUSION: on every real PTE group examined, H2 = REL3. The REL4 -> REL5 -> promotion chain was
statistically sound but EMPIRICALLY INERT so far: the regime in which H2 differs (near-constant pair
statistics at P ~ 32) is not reached by real specimens at M = 512 (P = 256). REL3's "power collapse at
normal ~1" was a property of synthetic near-deterministic pairs, not of observed data.
This strengthens the Level 3 recommendation. The only open question on this line with consequences for
real claims is the NEAR-THRESHOLD SEED SENSITIVITY (AUDIT3 A3b), not the interval construction.
Code for the census (numpy + prometheus.ananke.swap_rel, CPU, < 2 min): per group-arm, pair means of the
saved per-trial scores (4x-encoded, 255 = unscored), DF/DN, then the share of seed-0 resamples with
sd* <= 1e-9, and certificate(a, s, K, method="H2") vs method="BOOTT".
