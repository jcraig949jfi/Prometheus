# Salvage digest: meas-a (Measurement A: controls, baselines, statistics, qualification tooling)

Evaluator: Epimetheus salvage pass, OPUS-5.5, 2026-10-01. Frozen baseline: commit 77d3c99c3.
Question asked of every component: does it satisfy a Phase 3 requirement better than rebuilding it?
Target slot: R2 measurement bench (qualification dossiers MEA-01, plants MEA-02, baseline ladder and
chance floor MEA-03/04, controls wired to abort and mutation-tested checkers MEA-05, known-answer
statistics library MEA-11, canary injector MEA-17, null-certificate checker SCI-08/13/14,
anti-calibration SCI-07, attainability before freeze SCI-05).

Method: located components through evidence/*.md (tit-a, tit-b, tan-a, tan-b, sis-c, ixi), then read
the source and tests. Pure unit tests were run from the scratch directory with PYTHONDONTWRITEBYTECODE=1
and `-p no:cacheprovider`; `git status` was clean after every run. Nothing was committed.

Tests run here (all from a temp cwd, timeout <= 300 s):

    charon/probe/tests/test_c1c2_checks.py ............ 17 pass
    roles/Harmonia/.../primitives/tests (AP-1.1.0) .... 9 pass
    roles/Harmonia/.../h0h5/tests (QR-1.2.1, PR) ...... 33 pass
    roles/Nemesis/science/tests/test_cheatlib.py ...... 11 pass, 1 FAIL (forgery test, see s3)
    hecate/tests/test_shadow_decisions.py ............. all pass
    prometheus/cosmos/tests/test_locate.py ............ 1 pass
    theseus/tests/test_content_aware_promote.py ....... all but 1 pass (missing knots.json.gz)
    ensorain/wtp3/tests/test_wtp3.py .................. 5 pass
    roles/Ananke/.../W2-F/tests (stats, attainable,
      controls, metamorphic) .......................... 16 pass, 1 skip
    attacks/preflight.py --selftest ................... 9/9 PASS
    adversarial_fixtures.run_battery_1_1_0() .......... 12/12; F6 thr=0 false-support 0.015 (G),
                                                        0.010 (I) vs expected 0.0125
    prometheus_math/tests/test_modal_collapse_*.py .... NOT COLLECTABLE (package __init__ imports
                                                        cypari); module exercised directly instead
    Not run (write into the repository, need ergon/ live code, or rewrite source in place):
    exit_review_3_attack.py, gatefire_p3.py, cheat_control.py, mde_p3.py, mutation_harness.py,
    hecate/metamorphic/harness.py, xpol floors.py.

Holdout directories seen in the index (listed by name only, never opened):
prometheus/cosmos/c3_holdout_D, prometheus/cosmos/c3_holdout_D2, prometheus/cosmos/holdout, plus one
holdout-named file under roles/Cosmos/campaigns/c0b/run_21fd1b2cc/ (read by t_i1_fragments.py; not opened).

---------------------------------------------------------------------------------------------------
## 1. Bottom line

There is no measurement bench to salvage. There is a scattered set of good IDEAS, about a dozen small
primitives worth lifting (a few hundred lines each), and several instruments whose own controls are
broken. No component here is KEEP. Nothing here is a ruler with a qualification dossier in the MEA-01
sense (sensitivity curve over effect sizes on authored and generated plants, matched-negative FP rate,
label-permutation invariance, closure hash). Every R2 component must be built. The salvage reduces
design risk (the right checks and failure classes are known and have test triads), not build cost.

    component                                   category            R2 need                  cost
    Charon c1c2_checks                          EXTRACT             MEA-09, PRV-01/04 shape    S
    Charon exit-review-3 arm-leak classifier    REBUILD             MEA-01 metadata clf, WLD-07 S
    Nemesis cheatlib                            EXTRACT             MEA-03/04/05, CAU-10       S
    Harmonia AP-1.1.0 audit primitives          EXTRACT (+harden)   SCI-05, SCI-04, MEA-03     S
    Harmonia QR-1.2.1 qualification_rules       EXTRACT (rebuild    SCI-06, SCI-15, MEA-11     S
                                                stats part)
    Harmonia AF-1.1.0 fixtures + FP-1.0.0       EXTRACT (2 pieces)  MEA-05, SCI-05             S
    Harmonia STANDING_RULES.md                  HISTORICAL_CONTROL  spec rationale             NA
    Harmonia VACUOUS_READINGS.md                HISTORICAL_CONTROL  SCI-03/SCI-08 fixtures     NA
    Harmonia nulls (PLAIN/BSWCD/BOOT)           HISTORICAL_CONTROL  defective-null fixture     NA
    prometheus_math stats wrappers              RETIRE              (use scipy)                NA
    Techne modal-collapse synthetic null        HISTORICAL_CONTROL  WLD-02, MEA-03 fixture     NA
    Theseus F2 planted-relation gate            RETIRE              none                       NA
    Hecate exact shadow evaluator               EXTRACT             MEA-11, MEA-05             S
    Hecate metamorphic evaluator harness        EXTRACT             MEA-05, MEA-01 invariance  S
    Ergon bounded-null machinery (gen3)         EXTRACT (+harden)   SCI-14, SCI-08, SCI-13     M
    Ensorain N0-N6 ladder / collider            EXTRACT             MEA-03, WLD-03, TRF-02     S
    Cosmos location attack                      EXTRACT             CAU-03, SCI-13             S
    Cosmos zero-parameter definition rung       HISTORICAL_CONTROL  MEA-03, MEA-16 fixture     NA
    xpol floors (hephaestus)                    EXTRACT             MEA-03/04 gate null-pass   S
    Necropolis admissibility ladder             HISTORICAL_CONTROL  instrument catalogue       NA
    attacks/REGISTRY.md                         HISTORICAL_CONTROL  MEA-17 failure classes     NA
    attacks/preflight.py                        EXTRACT             SCI-05, MEA-06, PRV-04/09  S
    attacks/mutation_harness.py                 REBUILD             MEA-05 mutation in CI      S
    Ananke explib W2-F (attainable/controls/    EXTRACT             MEA-01, MEA-05, SCI-06     S
      stats) [found under "stats anywhere"]
    statistics code repo-wide                   REBUILD             MEA-11                     M

---------------------------------------------------------------------------------------------------
## 2. R2 need -> what exists -> gap

    need                       best existing material                         gap (blocking)
    MEA-01 dossier             explib.attainable.certify_gate (G1-G4,         no sensitivity CURVE over
                               fail-closed); AP reachability/absence/         effect sizes; no generated
                               baseline_gaming; c1c2 Verdict shape            plants; no closure hash; no
                                                                              label-permutation test
    MEA-02 plants              none (plants everywhere are author-built,      everything; independence
                               I0 relative to ruler authors)                  class not computed anywhere
    MEA-03/04 ladder+floor     cheatlib (constant/majority/payload),          no same-class tuned batch
                               xpol (position-majority, P(random passes       rung anywhere except
                               gate)), Ensorain N0-N5 (+N6 post hoc),         Ensorain N6 (post-data);
                               modal-collapse authority (lstsq)               denominators unchecked
    MEA-05 controls+mutation   c1c2 test triads; Hecate metamorphic M1-M7;    in-place mutator unsafe for
                               AF battery; preflight selftest+ratchet;        CI; no abort wiring into a
                               explib.controls A1-A4                          verdict job
    MEA-11 stats library       Hecate exact AUC/Clopper-Pearson; Ergon        NO shared library; ~60
                               sign-flip with +1; explib cluster bootstrap    ad hoc stats/null modules;
                                                                              known quantile bugs (s3.5)
    MEA-17 canaries            attacks/REGISTRY 20 failure classes            no injector exists
    SCI-08/13/14 null cert     Ergon decide() (INDETERMINATE first, bounded   MDE not through pipeline;
                               two-sided null), gatefire worlds, MDE sim      SESOI not anchored to a
                                                                              constructive organism
    SCI-05 attainability       AP reachability; explib attainable_labels;     needs enumeration contract
                               preflight degenerate/constant; FP-1.0.0        for stochastic designs
    SCI-07 anti-calibration    none                                            everything

---------------------------------------------------------------------------------------------------
## 3. Components

### 3.1 Charon c1c2_checks (charon/probe/c1c2_checks.py, tests/test_c1c2_checks.py) -- EXTRACT, S

What it really does. Two design-agnostic checks over RAW artifacts. C1 (lines 157-229) recomputes
sha256 over LF-normalised pool bytes and the non-blank record count and FAILs when a receipt omits a
pool fingerprint, quotes one that differs from the bytes, or differs from the preregistration; the
cheat "receipt copies the preregistered sha over different bytes" FAILs because the bytes are hashed
(test lines 90-100). C2 (236-352) enumerates transport-failed rep-1 rows and FAILs if the supplied loader
renders any as residue, judging by row (uid, seq), not uid; INDETERMINATE when nothing could have fired,
when rows lack a status, or when the loader admits nothing (exclude-everything is a cheat, not a pass).
An ordering predicate (366-386) requires both verdicts in the run receipt before collection. Every
verdict carries rows, eligible_count and fired_count (Verdict, 65-86).

Correctness. 17 tests, each check has positive, negative and cheat controls; run here, all pass.
Live gate-fire (c1c2_gate_fire_2026-09-11.json) fired on real ledgers (per evidence tit-b s3.1).

Phase 3. In R0 the content-addressed ledger and receipts make C1 structural (PRV-01, PRV-04), and the
MEA-09 schema separation makes C2 structural. The CHECKS are therefore not needed as code; the SHAPE is:
three-valued verdict with rows, INDETERMINATE-with-reason, "nothing could have fired" as its own label,
and the positive/negative/cheat test triad. That shape should be the template for every R2 check.

Coupling. Stdlib only; loader is injected. The gate-fire script imports ergon.probe.assemble and
archaeon.workspace and writes into charon/probe/. Windows/Linux neutral.

Defects. None material in the checks. Scope is one JSONL pool contract.

### 3.2 Charon exit-review-3 arm-leak classifier (charon/probe/exit_review_3_attack.py) -- REBUILD, S

What it really does. Renders every arm's packets through ergon.probe.campaign (line 59), strips content
two ways (STRICT word->class token, SHAPE char->class), then a char 1-4-gram TF-IDF + 21 numeric layout
features + logistic regression with GroupKFold(3) by task uid; permutation null (10 refits) only when
observed < 0.999 (177-187); reports exact separability.

Correctness. NOT DEMONSTRATED for the decisive contrast. The mandatory positive control (233-238)
plants one trailing space on F-answer versus F0, a pair the live evidence shows already separable at
1.0 with token means 35 vs 42; the comment says "F-null only". The control reads 1.0 with or without
the plant. The decisive length-matched pair (F-null | F-prom-retrieved) read 0.50 and was never planted.
Null: 10 refits with a Gaussian 1.96-sd band; labels are permuted across all 2N items rather than
swapped within uid pairs. No tests. Writes its output into the repository (OUT, line 51; 243).

Phase 3. The need is real and required: MEA-01 "content-stripped metadata classifier at chance" and
WLD-07 differential all-channel leak audit (planted leak on each channel must be detected). Rebuild
with a planted-leak detection CURVE (leak size x channel) on the hardest matched pair, within-pair
sign-swap null, exact permutation p with the +1 rule. Small (~300 lines + tests).

### 3.3 Nemesis cheatlib (roles/Nemesis/science/cheatlib.py, tests/test_cheatlib.py) -- EXTRACT, S

What it really does. Incapable responders (DegenerateConstant, MajorityClass, PayloadReader), predicate
forgeries (borrow_real_path, token_from_file, filler, absent_marker), chance_floor (majority and
uniform-over-candidates rates, 148-174) and shrink, a greedy-to-fixpoint reducer toward the cheapest
crossing cheat (255-300). No model, reads nothing semantically.

Correctness. 12 tests: firing fixture pinned to the April ledger via `git show HEAD:` (62/92 = 0.674;
292/294 tools at or below it). Run here: 11 pass, 1 FAIL:
test_cheat_forgeries_satisfy_their_predicates_without_meaning (test 144-159). Cause: token_from_file
returns None when its single random character is whitespace (line 215) instead of redrawing, and the
fixed seed is applied to a mutable repo file (roles/base-role/RESPONSIBILITIES.md) whose content has
changed. The 292/294 figure counts missing evaluations as wrong (evidence tit-b s3.3: 120/122 is the
defensible number).

Defects. Uniform floor is biased LOW when some items lack candidate counts: the numerator drops them
but the denominator n keeps them (163-167). No binomial interval beside any floor. Floors depend on
the population definition, which the library cannot see. Repertoire is three responders.

Phase 3. chance_floor and shrink are generic and belong in the baseline-ladder library (MEA-03/04) and
in the cheapest-cheat battery (MEA-01, MEA-05); shrink is also a seed for CAU-10 minimisation. The
responder interface must be re-expressed as POLICIES acting in POMDP worlds (constant action, marginal
action, payload-reader = reads a leaked channel), which is new code.

### 3.4 Harmonia AP-1.1.0 audit primitives (roles/Harmonia/qualification/primitives/) -- EXTRACT, S

What it really does. reachability (46-60): attainable verdict set over an enumerated design space and
the gated labels nothing reaches. absence_control (64-75): a "zero X" claim needs a calibration item that
expected X and got X. baseline_gaming (79-83): which committed non-construct baselines pass the rule.
ceiling (87-94): non-inferiority within one margin of the maximum is SANITY_CHECK_ONLY. freeze_precedes
(98-117): plan's first-add commit must be a strict ancestor of every result's first-add commit.
null_pass_binomial (36-42).

Correctness. 9 tests run, pass; freeze_precedes flags the real Ananke W-O plan.

Defects (confirmed).
- The ablation leg is tautological: run_fixtures(disabled=code) forces flag=False (160-165), so
  "defect_escapes_when_disabled" (185-190) is true by construction and tests nothing.
- Fixtures are transcribed constants (HECATE_BASELINES 148-152), not recomputed from data.
- freeze_precedes uses only the FIRST add of the plan (102-106): a plan edited after its results
  still passes; no --follow for renames.
- null_pass_binomial raises OverflowError for n >~ 1030 (verified: n=1100 and n=2000 raise; Python
  int comb() times float). Replace with scipy.stats.binom.sf.

Phase 3. reachability + absence_control + baseline_gaming + ceiling are exactly the prereg linter's
SCI-05 attainability checks and part of the MEA-01 dossier ("attainable verdict set") and MEA-03.
freeze_precedes is redundant once R0 has prediction-before-observation in an append-only ledger
(PRV-03, SCI-04) but is a useful audit of git-era claims. Lift the four functions (about 60 lines).

### 3.5 Harmonia QR-1.2.1 qualification_rules.py (roles/Harmonia/qualification/h0h5/) -- EXTRACT, S

What it really does. LanePlan validation (unit must be paired seed x task_block, denominator all
assigned, pilot/confirmation disjoint, multiplicity declared, minimum attainable paired p <= alpha,
138-200); paired t intervals with Bonferroni (273-284); contrast variance c'Sigma c and induced
correlation for shared arms (294-305, 562-594); simulated power under the actual interval rule
(400-432); refuse relabel of a DIAGNOSTIC plan as CONFIRMATORY (523-544); one payload under two cell
labels refused (607-644); bit-identical replay is an attestation, not a replicate (649-679); H0-H5
lane gates (743-879).

Correctness. 33 tests run, pass. No known-answer test of the t quantiles.

Defects (confirmed by comparing with scipy).
- ANTI-CONSERVATIVE QUANTILES. t_crit (242-247) picks the first tabulated df >= the true df, i.e. the
  SMALLER quantile. Examples (two-sided .05): df 11 -> 2.179 (exact 2.201), df 13 -> 2.131 (2.160),
  df 16 -> 2.086 (2.120), df 25 -> 2.042 (2.060), df 41 -> 2.000 (2.020), df 121-998 -> 1.960
  (1.980 at 121). Same pattern in the .025 column (df 16: 2.423 vs 2.473).
- WRONG BONFERRONI ABOVE TWO CONTRASTS. paired_contrast (282) uses the alpha .025 table for ANY
  n_primary >= 2 and for any alpha != .05. H3 declares three primaries: at df 9 the code uses 2.685,
  the exact alpha/3 quantile is 2.933 (interval 8.5% too narrow), while Estimate.alpha_used records
  0.0167, so the record misreports the interval it carries.
- Multiplicity count is caller-supplied (SCI-15 requires it derived from the ledger).
- min_attainable_p_paired returns 0.0 for n > 30 (an approximation; harmless).
- The AF F6 known-answer leg reads 0.015 +/- 0.0019 against an expected 0.0125 at df 11, consistent
  with the quantile defect, though not decisive at 4,000 trials.

Phase 3. Keep the IDEAS as code: refuse_replay_as_replicate and validate_cell_payloads (SCI-06,
PRV-01), contrast_variance/correlation, the eligibility gate (minimum attainable p before issue),
freeze/relabel refusal. Rebuild every interval and quantile on scipy inside the MEA-11 library with
known-answer tests. Lane gates (H0-H5) RETIRE with their engines.

### 3.6 Harmonia AF-1.1.0 adversarial fixtures + FP-1.0.0 floor precheck -- EXTRACT (two pieces), S

What it really does. Nine generated-defect fixtures with clean twins (adversarial_fixtures.py);
detectors are equalities, counts, signs, rates. floor_precheck (floor_precheck.py 39-69) refuses a corpus
whose modal mass p_mode > 0.50 and reports support size and non-degenerate fraction.

Correctness. Battery run here: 12/12. Most fixtures are toys whose "tell" is hard-coded by the
fixture author (F1: oracle_calls == 0, lines 47-74; F2: digest mismatch). F6 (214-257) is a genuine
known-answer calibration: false-support rate at threshold 0 must equal alpha/2 per contrast, and it
reports the practical-threshold zero as vacuous (thr / se > 2), which is the right self-diagnosis.

Phase 3. Lift F6 as a known-answer test pattern for MEA-11 and F7/floor_precheck as SCI-05 degeneracy
lints. Retire the rest.

### 3.7 Harmonia STANDING_RULES.md -- HISTORICAL_CONTROL

A cited index of ~60 rules (A1-A10, B1-B10, C1-C8, HA/QR/R-C3/F1-F8) with "executable form" columns,
most "--" (applied by reading). Its substance is already in the frozen requirements (MEA-01/03/05,
SCI-04/05/06/14, PRV-04). Use as rationale when a requirement is questioned; not machinery.

### 3.8 Harmonia VACUOUS_READINGS.md -- HISTORICAL_CONTROL

Eight rows (V-001..V-008) of questions a corpus could not answer in either direction (constant
criterion, 3-bit task with 8 inputs, cross-deploy confound, reach at the analytic bound, non-exchangeable
regions, 50 seeds where ~11,700 were needed, a quoted floor). This is the right bookkeeping and the
distinction "vacuous != null" must exist in the Phase 3 null typing (SCI-03). Each row is a ready-made
negative fixture for the null-certificate checker: it must refuse to type any of them as a phenomenon
null (SCI-08).

### 3.9 Harmonia nulls (harmonia/nulls/*.py, harmonia/runners/null_family.py) -- HISTORICAL_CONTROL

What it really does. NULL_PLAIN (global column permutation), NULL_BSWCD (block shuffle), NULL_BOOT
(stratified bootstrap) each return z = (obs - null mean)/null sd and DURABLE iff |z| >= 3.

Defects (confirmed).
- NULL_BOOT cannot fire for any linear statistic: a bootstrap of the observed data is centred on the
  observed statistic. Verified: n 500, value ~ N(5, 1) (a huge effect) -> z 0.01, COLLAPSES
  (bootstrap.py 61-87).
- NULL_PLAIN's default statistic is the mean of the very column it permutes (plain.py 17-18, 54-56),
  so z is identically 0 unless the caller supplies a pairing statistic.
- Gaussian |z| >= 3 on 300 draws; no exact p.
- null_family.py lines 32-33 hard-code a Redis host and password default in tracked source (PRV-11).

Phase 3. No production role. NULL_BOOT is a valuable planted "null that cannot fire": use it as a
mutation/anti-calibration fixture that the MEA-05 checks and the null-certificate checker must reject.

### 3.10 prometheus_math statistics (statistics_distributions.py, research/bootstrap.py) -- RETIRE

statistics_distributions.py (899 lines) is a renaming wrapper over scipy.stats distributions;
research/bootstrap.py wraps scipy.stats.bootstrap and adds matched-null z/p helpers. Nothing verdict-
specific. Importing prometheus_math pulls cypari through the package __init__ (test collection fails
on this host). Use scipy directly inside the MEA-11 library.

### 3.11 Techne modal-collapse synthetic null (prometheus_math/modal_collapse_synthetic.py) -- HISTORICAL_CONTROL

What it really does. A contextual bandit y = w.x + b + e, 21 bins, reward 100/0, episode length 1;
REINFORCE-linear and PPO-MLP ports versus a random agent; a least-squares "authority" test shows V3 is
learnable (>= 60%); _classify_verdict (708-746) calls Case A if both trainers are below 2x RANDOM.

Correctness. The headline (trainers learn the prior, not the map) survives, but the instrument has the
defect it was written to expose:
- "BALANCED" means equal-WIDTH bins, not equal mass. Measured here on 20,000 draws: the V3 majority-
  class floor is 0.0948, twice the uniform 1/21 = 0.0476 that every comparison and the Case-A rule
  use. REINFORCE seed 0 on V3 reaches 0.0958 with ONE active bin: exactly the majority floor, which the
  code would call 2.06x random. The majority-class rung is missing from the diagnostic.
- Accuracy is measured on training rollouts; there is no held-out evaluation of the trained policies
  (evaluate_random_agent_test covers only the random agent, 581-613).
- 3 seeds. Tests named "reinforce_beats_random" (270-293) and "exhibits_modal_signature" (235-251)
  assert nothing about those properties (top2 <= 1.0; accuracy >= 1/42).

Phase 3. Keep as a known-answer fixture: a learnable world plus a familiar learner that recovers only
the class prior. It belongs in WLD-02 (solvability witness beside the organism) and MEA-03 (marginal /
majority rung and same-class tuned batch estimator) qualification. Not production code.

### 3.12 Theseus F2 planted-relation contrast gate (theseus/scoring/content_aware_promote.py) -- RETIRE

What it really does. Score = |observed hold-rate - random-pairing hold-rate| >= 0.10 promotes.

Correctness. The production path is not the calibrated path.
- theseus/daemon.py:432-435 calls maybe_promote_by_f2 (293-330), which scores PER RECORD (127-190).
  With observed in {0, 1} the score is |1 - null| or |null|, so every record clears 0.10 whenever its
  relation's null hold-rate lies in (0.1, 0.9). The per-record gate does not discriminate content.
- The test author saw this (test lines 111-125: "Score will be high here") and weakened the assertion
  to 0 <= score <= 1, a vacuous test.
- The calibration (theseus/scripts/calibration_v0/v1) uses a separate per-source group scorer
  reimplemented inside the script, so the 0/8-decoy result does not cover the production function.
- Two families, one seed, unseeded default rng, no uncertainty. One test fails here (missing
  prometheus_math/databases/knots.json.gz).

Phase 3. Catalogue relation mining has no role. The "marginal-matched random-pairing null" idea is
already MEA-03's shuffled-pairing control.

### 3.13 Hecate exact shadow evaluator (hecate/alien/shadow_decisions.py) -- EXTRACT, S

What it really does. An independent exact-arithmetic re-implementation of a frozen decision layer:
recovers rationals from frozen floats (q, 67-75), decides thresholds on Fractions (decide, 88-96),
Mann-Whitney AUC with ties as a Fraction (99-108), replays the bootstrap with the same stream (116-132),
Clopper-Pearson and conservative interval-arithmetic fallbacks for degenerate bootstrap CIs (135-157),
and reports recorded-vs-shadow divergence per hypothesis.

Correctness. Tests run, all pass; found the real 0.2 - 0.1 = 0.0999... < 0.10 float defect (H3) and the
H4 rule-form divergence; reproduces recorded bootstrap CIs to 1e-12.

Phase 3. Lift auc_exact, clopper_pearson, cp_rate_diff and the exact-threshold rule into MEA-11, and the
"dual implementation of every verdict rule, divergence is a CI failure" pattern into MEA-05. The assay-
specific per_item/shadow code retires.

### 3.14 Hecate metamorphic evaluator harness (hecate/metamorphic/harness.py) -- EXTRACT, S

What it really does. Copies each world evaluator to scratch, corrupts its input rows with nine operators
(65-75: swap treatment/null-twin, twin := treatment, treatment := control, drop positive controls, drop
cheat rows, cheat := treatment, all seeds := seed 0, payload permuted across arms within seed), re-runs
the evaluator, and judges the reaction against a fixed expectation table (judge, 403-533).

Correctness. No unit tests of the harness. Reported run: 42 evaluators, 42/42 baselines reproduced,
many INSENSITIVE/BLIND cells (roles/Hecate/harvest_w2/INV_F_metamorphic_results.md). Brittle parts:
hard-coded world paths and role aliases (49-63); M6 "detection" is a keyword search of anomaly text
(DUP_WORDS, 536-552); copy mutations need a lenient re-run when schemas differ.

Phase 3. The operator set and expectation table are exactly what MEA-05 needs to mutation-test verdict
code and what MEA-01 needs for label-permutation invariance. Re-implement against the Phase 3 row
schema (where arm labels are excluded from ruler inputs by manifest), as a CI suite.

### 3.15 Ergon bounded-null machinery (ergon/gen3/p3_analyze.py, mde_p3.py, gatefire_p3.py, cheat_control*.py) -- EXTRACT + HARDEN, M

What it really does. decide (p3_analyze.py 81-147): INDETERMINATE checked FIRST (eligible pairs below
n_required, validity failures, all tied, SE > T/2), then two-sided paired sign-flip permutation with
the +1 rule (64-71), 95% percentile bootstrap (74-78), and six labels including a BOUNDED null (CI
inside (-T, T)) and UNDERPOWERED. mde_p3 (50-68) bisects an MDE80/90 by simulation. gatefire_p3 feeds
constructed CFR vectors with known truth through the exact decide(). cheat_control plants oracle
witnesses into the real execution path.

Correctness. Gate-fire: 5 worlds, all called correctly. BUT only 4 of 6 labels are exercised
(MRU_HARMFUL, RETENTION..._NOT_MEASURABLY_MATTER, MRU_BETTER, INDETERMINATE); UNDERPOWERED,
MRU_HARMFUL_BELOW_USEFUL_SCALE and the validity-failure branch never fire (gatefire_p3.json read here;
the evidence's "exercised every verdict branch" is wrong). Cheat control: PLANT2 n 30 MRU_HARMFUL;
PLANT1 n 30 returned INDETERMINATE, outside its own preregistered pass set, and was re-run at n 100
(MRU_HARMFUL, +3.38 pp, p 2e-5). No unit tests; not run here.

Defects.
- MDE is computed by a separate vectorised normal simulation (mde_p3.py 50-56), not through decide()
  and not on the k/42 lattice with ~20% ties. SCI-14 requires scaled planted positives through the
  actual pipeline.
- Float tie comparisons on a lattice: p moves 0.1895 vs 0.1776 depending on rounding (documented at
  p3_analyze.py 213-216). Use integer counts.
- SESOI T = "one task in 42" is a convention, not anchored to a constructive organism (SCI-14).
- The planted witness is a CONTENT plant used to validate an ORDER (retention-policy) null.
- Pure-Python permutation loops; all names domain-specific.

Phase 3. decide() is the best-shaped null decision rule in the repository and the gate-fire-world
pattern (constructed truths through the exact path, one per label) is the right qualification for the
null-certificate checker (SCI-08 element R, SCI-13, SCI-14). Lift the skeleton; rebuild MDE through the
pipeline; require one gate-fire world per label.

### 3.16 Ensorain N0-N6 null ladder (ensorain/wtp3/collider.py, n6_check.py) -- EXTRACT, S

What it really does. One experience stream per world; every substrate and every null learns from it at
matched memory. Ladder (164-204): N0 zero, N1 constant (and recent), N2 marginal (ridge one-hot), N3
linear, N4 bounded nearest-cell lookup; N5 = online simple substrates. XC = AC - max over the ladder
(321-329). holdout (126-147) builds a pair-block recombination split: every held-out value is seen
alone, no pair of held-out values ever is. marginal_surrogate (36-48) preserves mean, variance and every
per-mode marginal exactly while destroying interactions.

Correctness. 5 tests run, pass (surrogate exactness, no pair in the holdout, constant XC <= 0,
intervention support). Fatal historical defect: no same-class batch rung; N6 (batch low-rank/CP ALS,
tuned in hindsight) was added post-data and beat all 9 promoted specimens by .22-2.28 AC.

Phase 3. Lift holdout() into the world forge's split builder (WLD-03, TRF-02, F6 pair-block holdout),
marginal_surrogate as an interaction-destroying control, and the XC-over-ladder definition into MEA-03,
with the same-class tuned batch estimator mandatory from the start. Tensor-completion specifics retire.

### 3.17 Cosmos location attack (prometheus/cosmos/locate.py) -- EXTRACT, S

What it really does. For confidently-positive base worlds, sweeps a cost knob over 33 points around the
law's predicted flip with common random numbers, fits a logistic location by ML, and reports
delta = log2(f_obs / f_pred) per family and pooled; LOCATION_BIASED if |mean| > max(2 SE, 0.05).

Correctness. 1 test (test_locate.py) covers only _summ; it documents that cancelling per-family biases
read LOCATION_OK pooled. With n as small as 4 bases the 2 SE rule is a z rule (t at 3 df is 3.18).
Found real per-family offsets (regs -.147, ca -.105, ring +.142) invisible to balanced accuracy.

Phase 3. The method (dose ladder on one knob, CRN, logistic location, per-family report) is the core of
the CAU-03 dose ruler and of SCI-13 bracket location. Re-implement in ~100 lines on the R0 runner.

### 3.18 Cosmos zero-parameter definition rung -- HISTORICAL_CONTROL

There is no reusable rung code. research_check.py (29, 110-112) only checks by regex that a RESULTS
entry's baselines text mentions "definition rung" and accepts "NOT MEASURED". The rung values were
computed ad hoc and recorded in prose (roles/Cosmos/research/RESULTS.md R-0001: D .973, E .971, F .887;
McNemar law vs rung p .688/.688/.125). t_i1_fragments.py adds a marginal-matched random-expression null
for "atom re-expresses the rung" (reads a holdout-named campaign file; not opened). MEA-03 already
mandates "the label's definition as a zero-parameter rule" as a rung: the requirement is the salvage.
R-0001 (a law indistinguishable from its own certificate) is a known-answer case for MEA-16 and MEA-03.

### 3.19 xpol floors (hephaestus/xpol_2026/floors.py) -- EXTRACT, S

What it really does. Before any model call: candidate-count chance floor, constant-first and constant-
last decoys, the in-sample position-majority decoy, the NCD baseline, and 200 random-ranking tools
with P(random tool passes the 1.0 gate) (52-76). It exposed that the "1.0" ruler sits below a decoy.

Coupling. Imports agents/hephaestus/src trap_generator_extended and test_harness; writes floors.json
beside itself. Not run.

Phase 3. "P(incapable generator passes the gate)" by Monte Carlo is the general form of a gate's chance
floor (MEA-03/04) and equals explib G1. Merge with cheatlib.chance_floor into one baseline module.

### 3.20 Necropolis admissibility ladder (engine/necropolis/workshop/registry_source.py) -- HISTORICAL_CONTROL

What it really does. admissibility (603-657) computes PATH_EXISTS -> IMPORTS -> EXECUTES -> CONTROLLED
-> ADMISSIBLE per registry tool from recorded measurements. TOOLS.jsonl: 45 of 93 admissible.

Defects. The ladder certifies that a tool ran under Keeper controls, not that it detects anything (no
effect size, power or planted magnitude). One rung reads a hand-written status string (646). The
validator passes 7/8 CHEAT cases unchecked (evidence sis-c s2.5). Phase 3's MEA-01 dossier supersedes
it; TOOLS.jsonl is a useful catalogue of historical instruments and their control state.

### 3.21 attacks/REGISTRY.md -- HISTORICAL_CONTROL

Twenty defect classes (ATK-001..020) with signature, probe status and kill record; about half
EXECUTABLE, all of those instance-specific (attacks/probes/atk013/014/015 target ergon files). This is
the best available list of failure classes for the MEA-17 canary injector ("at least one canary per
covered failure class") and for the MEA-05 cheat battery. ATK-002's lesson (sampling windows flatter
instruments) and ATK-020 (detector scored on planted positives only) must be canary classes.

### 3.22 attacks/preflight.py -- EXTRACT, S

What it really does. Five deterministic checks with a selftest and a ratchet: dead_field (47-67; a gate
input no row carries), degenerate_strata (72-105; outcome pinned by stratum identity), constant_within_
group (110-135; a ranking feature constant inside groups gives AUC 0.5 by construction), frame (140-168;
declared glob vs directory contents), unsourced (173-195; aggregate whose ledger is untracked); ratchet
(274-299) blocks new failures and stale known-failing entries.

Correctness. --selftest run here: 9/9. Reported field miss: ATK-013 silent on a live instance.
Defect: degenerate_strata and constant_within_group FAIL OPEN on small inputs (return ok=True with
"not informative", 94-96 and 127-129). Thresholds (10%, 50%) are arbitrary.

Phase 3. dead_field -> MEA-06 schema validation (a missing input must raise); degenerate/constant ->
SCI-05 attainability lints (must fail closed: NOT_VERIFIED blocks); frame -> PRV-09; unsourced is
structural in R0. Ratchet pattern is good CI practice.

### 3.23 attacks/mutation_harness.py -- REBUILD, S

What it really does. AST mutation (comparison swaps, arithmetic swaps, return None, function-name swap)
of a target file IN PLACE with a .mutation_bak copy, re-running its tests; refuses truncated runs unless
sample_ok (159-200), a lesson from a cap=20 window that read 100% vs 85.2% full.

Phase 3. MEA-05 requires gating checkers to be mutation-tested in CI. In-place rewriting of tracked
source is unsafe under concurrent sessions and CI. Use an off-the-shelf mutator (mutmut / cosmic-ray)
or an import-hook mutator; carry over the "report sampled/total, never a bare score" rule. Not run.

### 3.24 Ananke explib W2-F (roles/Ananke/research/harvest/wave2/W2-F/explib/) -- EXTRACT, S

Found under "statistics code anywhere"; it is the closest existing thing to an R2 qualification
library. attainable.certify_gate (104-125): G1 null false-pass rate with an exact one-sided Clopper-
Pearson upper bound (33-68), G2 adversaries, G3 plants, G4 per-cell eligibility, attainable labels;
fail-closed (missing evidence is NOT_VERIFIED and blocks). controls.py: a control is evidence only if
NOT_NO_OP, NOT_CONSTANT, NO_DESIGN_IDENTITY and CAN_FAIL (witness). stats.py: every interval requires
a declared independence Units object; cluster bootstrap; joint arm CIs that keep pairing; Simpson
guard; ratio guard. Tests run here: 16 pass, 1 skip.

Defects. G3 passes on ONE passing plant (no sensitivity curve across effect sizes, MEA-01); percentile
cluster bootstrap only; triplicated across harvest directories (W2-F, W2-AE pkg, W2-AE scratch_apply);
lives in a research harvest directory, not a package.

Phase 3. Seed for the MEA-01 dossier checks, MEA-05 control-competence audit and SCI-06 unit
declaration. Extend G3 to a curve over effect sizes on authored and generated plants.

### 3.25 Statistics code repo-wide -- REBUILD, M

There is no shared statistics library. About 60 independent stats/null/power/MDE/bootstrap modules
exist (e.g. archaeon/stats.py, harmonia/nulls, harmonia/router/power_analysis.py, ergon/gen1/
mde_under_multiplicity.py, proteus/v0_5/multiplicity.py, SerendipityFoundry/*/stats.py,
roles/Lexis/instruments/permutation_null.py, cartography battery_*). Confirmed defects in this group
alone: hand-tabulated anti-conservative t quantiles and wrong Bonferroni (QR-1.2.1), overflowing
binomial tail (AP-1.1.0), nulls that cannot fire (NULL_BOOT, default NULL_PLAIN), float tie handling on
lattices (Ergon), Gaussian z bands on 10 permutation refits (exit-review-3). MEA-11 needs one library on
scipy with known-answer tests: t/normal quantiles vs tables, exact binomial and Clopper-Pearson,
exact sign-flip enumeration for small n, permutation +1 rule, TOST/bounded nulls, Bonferroni/Holm with
ledger-derived family size, cluster bootstrap, power and MDE by simulation through a supplied pipeline.
Salvage into it: Hecate auc_exact/clopper_pearson, Ergon decide skeleton, explib Units/cluster
bootstrap, QR contrast_variance and replay refusal.

---------------------------------------------------------------------------------------------------
## 4. Cross-cutting findings

1. Controls that cannot fail were the commonest defect in the measurement lane itself: the AP ablation
   leg, the exit-review positive control, NULL_BOOT, default NULL_PLAIN, F2's per-record score, the
   weakened F2 test, the modal-collapse tests. A Phase 3 rule worth enforcing mechanically: every
   control's own "can fail" witness is part of the dossier (explib A4, AF clean twins).
2. Calibrated path != production path (F2; Ergon MDE vs decide). The qualification hash covering the
   full closure (MEA-01) is the fix; nothing historical has it.
3. Missing baseline rungs were found post-data in every lane audited here: majority-class (modal
   collapse), same-class batch (Ensorain N6), definition rung (Cosmos), constant (Ensorain WTP-02).
   MEA-03's ladder must be frozen in the preregistration with all rungs computed before any data read.
4. Every plant and cheat in this group was authored by the instrument's author or seat (I0). MEA-02's
   independence class and generated plants have no historical precedent to salvage.
5. Host specifics: CUDA_VISIBLE_DEVICES and drive-letter paths appear in harvest code; a Redis
   password default sits in tracked source (harmonia/runners/null_family.py 33). prometheus_math
   cannot be imported without cypari. None of the salvaged primitives needs a GPU.

---------------------------------------------------------------------------------------------------
## 5. Files read (source and tests opened)

charon/probe/c1c2_checks.py; charon/probe/tests/test_c1c2_checks.py; charon/probe/exit_review_3_attack.py;
charon/probe/c1c2_gate_fire_2026-09-11.py (header); roles/Nemesis/science/cheatlib.py;
roles/Nemesis/science/tests/test_cheatlib.py; roles/Harmonia/qualification/primitives/audit_primitives.py;
roles/Harmonia/qualification/primitives/tests/test_audit_primitives.py;
roles/Harmonia/qualification/h0h5/qualification_rules.py; .../h0h5/adversarial_fixtures.py;
.../h0h5/floor_precheck.py; roles/Harmonia/STANDING_RULES.md; roles/Harmonia/VACUOUS_READINGS.md;
harmonia/nulls/bootstrap.py; harmonia/nulls/plain.py (parts); harmonia/router/permutation_null.py;
harmonia/runners/null_family.py (parts); prometheus_math/statistics_distributions.py (outline);
prometheus_math/research/bootstrap.py (outline); prometheus_math/modal_collapse_synthetic.py (parts);
prometheus_math/tests/test_modal_collapse_synthetic.py (parts); prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md;
theseus/scoring/content_aware_promote.py; theseus/tests/test_content_aware_promote.py;
theseus/scripts/calibration_v0_murasugi.py (grep); hecate/alien/shadow_decisions.py;
hecate/tests/test_shadow_decisions.py; hecate/metamorphic/harness.py (parts);
roles/Hecate/harvest_w2/INV_F_metamorphic_results.md (head); ergon/gen3/p3_analyze.py; ergon/gen3/mde_p3.py;
ergon/gen3/gatefire_p3.py; ergon/gen3/cheat_control.py (header); ergon/gen3/*.json (parsed);
ensorain/wtp3/collider.py; ensorain/wtp3/n6_check.py (head); ensorain/wtp3/tests/test_wtp3.py;
prometheus/cosmos/locate.py; prometheus/cosmos/tests/test_locate.py; prometheus/cosmos/research_check.py;
prometheus/cosmos/tests/conftest.py; roles/Cosmos/research/analysis/t_i1_fragments.py (head);
roles/Cosmos/research/RESULTS.md (grep); hephaestus/xpol_2026/floors.py;
engine/necropolis/workshop/registry_source.py (parts); attacks/REGISTRY.md; attacks/preflight.py;
attacks/mutation_harness.py (parts); attacks/probes/atk013, atk014 (headers);
roles/Ananke/research/harvest/wave2/W2-F/explib/{stats,attainable,controls,authority}.py (parts) and tests/conftest.py;
docs/phase3/design/OPUS-5.5/{RSE_ARCHITECTURE.md, requirements.jsonl, evidence/tit-a.md, tit-b.md,
tan-a.md, tan-b.md, sis-c.md, ixi.md} (locator sections).
