# AUDIT B -- Hecate world evaluators (probe rounds 1-3, Pass 4 rounds 1-2)

Date: 2026-09-30. Auditor: Claude agent (read-only; this file is the only write).
Scope: 42 evaluations -- 29 round-1/2 OUTCOME.json, 8 round-3 probe/OUTCOME.json,
5 pass4/PASS4_OUTCOME.json. Governing PREREGs: roles/Hecate/prereg/
{2026-09-29_probe_round1, 2026-09-30_probe_round2, 2026-09-30_pass3_v2,
2026-09-30_pass4_round1, 2026-09-30_pass4_round2}/PREREG.md.

Method: for each world, read the spec (the program.json experiment entry, or
spec.json + ATTAINABILITY.json), NOTES/IMPLEMENTATION_NOTES, evaluate.py
(or pilot_eval.py) and the rows; then recompute the deciding statistics from
the rows with independent python.

Evaluators were re-run only on scratch copies, never in place. Groups C and D
and HT-55162c0ac0 were re-run in full. Group B was re-run in full except
37e3/W4 (rows recounted instead). Groups A and E were recomputed from rows
only, not re-run.

Every re-run reproduced the committed outcome class or predicate. Where
anything differed it was core_minutes, an env-driven `attempts` field, or
anomaly/notes text. So none of the defects below is an arithmetic slip in
committed files; they lie in readings, controls, class logic and attack
design.

No git was used. File mtimes are mostly checkout or append times. That makes
"parameter chosen after results" checkable only where the NOTES themselves
log it.

Severity: BLOCKING = recorded outcome/verdict is wrong as recorded;
MAJOR = outcome/verdict or a recorded label is wrong or unsupported;
MINOR = defect that does not change the reading; NOTE = observation.

## 1. One line per evaluation

program/world             round  stated                audited        defects
HT-056d3ac561/W1          r1     INSTRUMENT_FAIL       same           A1 A2
HT-056d3ac561/W4          r2     NULL                  same           A3 A4
HT-056d3ac561/W5 probe    r3     NULL                  same           A5
HT-2a8a3aedeb/W4          r1     NULL                  same           A7 A8 A9
HT-2a8a3aedeb/W1          r2     NULL                  same           A5 A6
HT-321a8fd8e0/W1          r1     SIGNAL                same           A5 A10
HT-321a8fd8e0/W1 pass4    P4r1   ORIG_FOSSIL_ALT_PASS  same predicate; verdict PROBING indeterminate  A11
HT-37e311ce05/W1          r1     INSTRUMENT_FAIL       same           B3
HT-37e311ce05/W4          r2     SPEC_UNATTAINABLE     same (reason overstated)  B2
HT-37e311ce05/W5 probe    r3     NULL                  same           B4
HT-47f4c02be4/W4          r1     CONFOUNDED            same           B7
HT-47f4c02be4/W1          r2     NULL                  same (see B1: fork's flip rejected)  B1
HT-5b0b3ebb8d/W4          r1     SIGNAL                same           B5
HT-5b0b3ebb8d/W4 pass4    P4r1   PARK                  same           B6
HT-55162c0ac0/W3          r1     INSTRUMENT_FAIL       same           F6
HT-55162c0ac0/W2          r2     SPEC_UNATTAINABLE     same           F7
HT-55162c0ac0/W6 probe    r3     SIGNAL                same           F5
HT-55162c0ac0/W6 pass4    P4r2   PARK (ORIG not fired) predicate same; ORIG DIFFERENT (fired)  F1 F2 F3 F4
HT-71b65251aa/W3          r1     SIGNAL                same           C1
HT-71b65251aa/W3 pass4    P4r1   PARK                  same           C2
HT-79e904e13a/W4          r1     NULL                  indeterminate (leans NULL)  C4 C5
HT-79e904e13a/W1          r2     NULL                  same (see C3: fork's flip rejected)  C3
HT-8a87057933/W1          r1     NOT_BUILT             same           C6
HT-8a87057933/W4          r2     SPEC_UNATTAINABLE     same           C7
HT-8a87057933/W5 probe    r3     SIGNAL                same           C8
HT-8a87057933/W5 pass4    P4r2   PARK                  same (ORIG is a tautology)  C9 C10
HT-974471f045/W3          r1     NULL                  same           D8 D9
HT-974471f045/W1          r2     SPEC_UNATTAINABLE     same           D7
HT-974471f045/W6 probe    r3     NULL                  same           D10
HT-a9e2ba7618/W4          r1     NULL                  same           D6 D9
HT-a9e2ba7618/W3          r2     NULL                  DIFFERENT -> SPEC_UNATTAINABLE (likely)  D1
HT-ae38c641b1/W3          r1     NULL                  same class, fragile path  D3
HT-ae38c641b1/W4          r2     SPEC_UNATTAINABLE     indeterminate  D4
HT-ae38c641b1/W5 probe    r3     NULL                  indeterminate (spec's INCONCLUSIVE band)  D2
HT-e106e1603b/W2          r1     INSTRUMENT_FAIL       same           E1 E2
HT-e106e1603b/W1          r2     NULL                  same           E3 E4
HT-e106e1603b/W5 probe    r3     NULL                  same (spec premise false)  E5
HT-e743909f97/W1          r1     NULL                  same           E6 E7 E8
HT-e743909f97/W3          r2     NULL                  same           E9 E10 E11
HT-faa9277e02/W2          r1     INSTRUMENT_FAIL       same class, reason indeterminate  E14 E15 E16
HT-faa9277e02/W1          r2     SPEC_UNATTAINABLE     same           E12 E13
HT-faa9277e02/W6 probe    r3     NULL                  same           (none found)

Totals: 42 evaluations.
- 35 same.
- 1 different outcome class: a9e2/W3.
- 1 different recorded attack result inside an unchanged predicate:
  55162/W6 pass4 ORIG.
- 4 indeterminate: 79e9/W4, ae38/W4, ae38/W5, and the 321a pass4 verdict.
- 1 same class with a fragile path: ae38/W3.

## 2. Cross-cutting findings

X1 MAJOR. The round-2 pilot gate is read inconsistently across implementers.
The PREREG says "the positive control meets the spec's success criterion".
Implementers read this in two ways:
- Some checked only the positive control's own threshold: 47f4/W1, 79e9/W1,
  a9e2/W3, faa9/W1.
- Others checked the whole success conjunction, including twin-only and
  relative clauses: 55162/W2 reading A9; ae38/W4 "every k".
The same situation was therefore classed SPEC_UNATTAINABLE in one world and
NULL in another. Fix: one written rule. Run every success clause on PC +
real twin in the pilot; a clause fixed by a twin or by construction makes
the pilot fail.

X2 MINOR (recurring). Many CHEAT arms write a constant into the observable or
inject a twin value. Seen in 321a/W1, 2a8a/W1, 056d/W5, 47f4/W1, 79e9/W1,
a9e2/W4, 974471/W3 and e743/W3. Such a CHEAT tests only that the evaluator
thresholds can fire, not that the world's code path can reach them. In two
worlds (47f4/W1, 79e9/W1) the cheat used a different twin from the
treatment.

X3 MAJOR. Pass 4 attacks are admitted even when their outcome is fixed by
construction:
- 321a ALT: majority vote has K = 0 by counting (A11).
- 8a87 ORIG: channel-reset is identical to MUS-by-deletion (C9).
The pass4_round2 PREREG forbids this, but the evaluators have no check for it.

X4 MAJOR. Spec-defined bands outside the PREREG classes are collapsed to NULL.
- ae38/W5: the spec's INCONCLUSIVE band (D2).
- 55162/W6 probe: the same reading, stated in its NOTES.
The program reports then count these as "valid NULL readings" when deciding
PARK.

## 3. Defect detail -- groups A-E (findings verified from rows by sub-auditors;
##    lead auditor spot-checked the outcome-changing ones, see marks [LC])
A1 MINOR. HT-056d3ac561/worlds/W1/world.py:158-161. The null-twin statistic
d_null is normalised by the same-time variance, not by the variance of the
mismatched pair.
- Evidence: CONTROL mean_D_null 23624 against D 4.03; recomputed median D_null
  8664 (mismatched) vs 23096 (matched).
- Flip: none (outcome is INSTRUMENT_FAIL).
- Fix: normalise by the empirical variance of x1_t' - x2_t.
A2 NOTE. 056d/W1: the positive-control oracle compares matched seeds 0-49
against mismatched seeds 1000-1049 (unpaired; the spec allows this). PC AUC
0.490 and AUC(D) 0.493 recomputed. The INSTRUMENT_FAIL is correct.
A3 MINOR. 056d/W4 NOTES "Repair". The repaired PC is oracle-support least
squares, not the treatment's Lasso path; the spec's own PC is unattainable
via its min-norm clause.
- Mitigation: treatment Lasso reaches 0.975 at k=1, so the instrument visibly
  works.
- Without the repair the class would be SPEC_UNATTAINABLE; the program route
  is the same either way.
A4 NOTE. 056d/W4: the NULL holds under any per-k reading. k=3 Lasso success
per seed is 0.58, 0.67, 0.54, 0.645, 0.655 (all < 0.80). Only pooling over k
(0.823) would give SIGNAL, and that reading was rejected in NOTES.
A5 NOTE. CHEAT rows bypass the world code in 056d/W5, 321a/W1 and 2a8a/W1
(see X2). In 2a8a/W1, the planted z combined with the twin's V makes S1
trivially true.
A6 NOTE. 2a8a/W1: the pilot repair (centring tanh) also changed the
comparator in the treatment's S2. It was made before any treatment code, so
it is allowed.
- NULL is robust: S1 is 0/10 in every cell; bond(z) 17.9 vs bond(V) 10.4 (the
  opposite direction).
A7 MAJOR (procedural, no flip). 2a8a/W4 IMPLEMENTATION_NOTES "Attempt log".
The goal construction (the F_m, O_m factors) was changed after treatment
numbers had been printed. The breach is disclosed.
- Both attempts are NULL: attempt 1 has 0 seeds, median in 1.05, off 1.033;
  attempt 2 has 0 seeds, median in 24.3, off 1.022.
A8 MINOR. 2a8a/W4 evaluate.py, the `fl` anomaly. It reports 5805 floored
entries for "all rules"; they are actually orth-c 2924 and in-c 2881 (0 for
the other rules). Fix: report the count per rule.
A9 NOTE. 2a8a/W4: the "orthogonal" goals share the constant direction (an
effect of the repair). The related stupid explanation is recorded as not
addressable.
A10 NOTE. 321a/W1: the PC is read on a 16-agent pool while the treatment uses
31 agents. This reading is declared, because ">= 0.99 at k=1" is impossible
at 31 agents.
- SIGNAL reproduced from rows: k <= 3 rate 0; k=4 rate 0.588 (seed min 0.535).
A11 MAJOR (verdict). HT-321a8fd8e0/worlds/W1/pass4/evaluate.py, line
`alt_pass = Kc > Km`. The ALT cannot fail.
- MAJ31 manipulation rate at k=1 is 0.511 (18/31 coalitions, exhaustive), so
  K_maj = 0 for any allocation; K_code = 3. The NOTES and the program note
  both say the result is fixed by counting.
- R reproduced on seeds 100-119 (disjoint from 0-19). ORIG fired correctly
  (d=3: 0 then 1.0; d=5: 0, 0, 0.882).
- The predicate is correct under the round-1 PREREG, which has no counting
  rule. Under the round-2 rule the ALT is NOT_ELIGIBLE, which gives PARK.
- Flip: the PROBING verdict is indeterminate (it rests on no falsifiable
  attack).
- Fix: re-adjudicate the ALT under the counting-check rule, or annotate
  PROBING as "degenerate ALT".
B1 (sub-auditor rated BLOCKING; lead auditor REJECTS the flip; MINOR remains).
HT-47f4c02be4/W1.
- The sub-auditor's case: the pilot checked only the PC's own field
  (pilot_eval.py:14). The CHEAT injects twin_ratio = 1.0 (pilot_eval.py:15,
  evaluate.py:15), a different path from the treatment's real twin
  (evaluate.py:19-21). The twin ratio is 0.21 on 10/10 seeds, which defeats
  clause B. Hence SPEC_UNATTAINABLE, and the program goes SPECULATIVE.
- [LC] What the lead auditor read: OUTCOME.json has clause_A_real_stream True
  (max dev 0.0042), clause_B_twin_ratio False, twin_ratio per seed 0.2098-0.2127.
  The spec's failure_criterion explicitly includes "the twin achieves
  r(20)/r(0) < 0.9 (structure not arithmetic)".
- So the twin depleting is a falsifier the spec wrote in advance: a stream
  with matched density shows the same residual decay. That is a substantive
  NULL (CONFOUNDED-like), and the PREREG counts CONFOUNDED as NULL. The class
  and the program PARK stand.
- Remaining defect (MINOR): the cheat injects the twin value; it should run
  through the real twin path.
B2 MAJOR (reason text; no flip). HT-37e311ce05/W4.
- The repaired PC (pilot.py:100-115) builds only the M13 conjunct. M3
  (overlap <= 0.05) was left to the dynamics: 0/10 after repair vs 6/10 in
  attempt 1.
- M3 is geometrically reachable: the minimum eigenvalue over random 6-column
  spans is 0.001-0.014.
- So "spec unattainable" overstates the cause. The class is mechanically
  correct (two pilot fails), and the program end state is unchanged (PARK
  via W5).
B3 NOTE. 37e3/W1. INSTRUMENT_FAIL is correct: CONTROL success is 0.990, so
clause (b) (diff >= 0.3) is unreachable (evaluate.py:27-28, 52). Read as a
treatment, it would be NULL (0/10 seeds; diff -0.007).
B4 MINOR. 37e3/W5 controls.py:91-95. The denominator gbar(m_max) is negative
only in the treatment (-0.045), a case no control exercised.
- Completion is 0.732; floored at 0 it is 0.781. Both are < 0.8, so no flip.
- The PC (LP optimum) bypasses the evolutionary search, and the treatment L1
  is about 13 vs the LP's 10, so convergence is not shown.
B5 NOTE. 5b0b/W4: the CMH test treats about 29 beliefs per seed as
independent. A seed-cluster bootstrap 99% CI for the OR is 1.24-2.02; 28.6%
of draws fall below 1.5 (point estimate 1.58). Not a flip.
B6 MINOR. 5b0b/W4 pass4.
- ORIG fired correctly: 0/20 strata have outcome variance.
- In the ALT world, reach_fail is 0/1788 for the treatment, so "fail" means
  "a removed transition lay on the supporting path", not that a belief
  became false.
- PARK is robust: the OR is at most 1.47 under every alternative reading.
B7 NOTE. 47f4/W4: the spec's shuffled twin stays inside the s=1 index band
(R_null 0.186), so CONFOUNDED was close to forced by the spec. Flagged by
the implementer before the run.
C1 NOTE. 71b6/W3 world.py:94-98: the PC is tautological (one referent, so
the L0 max posterior is 1 >= theta always). Part of the depth-ambiguity
Spearman is built in.
- The SIGNAL is faithful to the spec text; Pass 4 ORIG later caught the
  fixed-L1 tie.
C2 NOTE. 71b6 pass4: ORIG fired on the data (L1 acc 0.74355 >= 0.7437-0.005;
depth 1.0 <= 1.307). ALT L2-L1 gaps were 0.0000 and 0.00035, so
NOT_ELIGIBLE twice. PARK is correct.
C3 (sub-auditor rated MAJOR with a flip to SPEC_UNATTAINABLE; lead auditor
REJECTS the flip; MINOR remains). HT-79e904e13a/W1, pilot_eval.py:110,
evaluate.py:15.
- What is true: the repaired CHEAT is judged against an injected chance twin
  (CHEAT_NULL), while the treatment is judged against the real twin, so the
  twin clause (<= 0.2) has never been met by any construction.
- [LC] But the OUTCOME clauses show the treatment fails a treatment-side
  clause independently: decline_-0.5_minus_-0.01 is 0.024 (< 0.3), and the
  spec's failure clause "decline < 0.1" FIRES on the treatment. The PREREG
  defines NULL as "treatment fails the criterion (or meets the
  failure_criterion)", so the NULL stands.
- Fix: run the cheat through the real twin, and record the twin clause as
  unattainable at this configuration.
C4 MAJOR (indeterminate). 79e9/W4 evaluate.py:18-20, 45 (OLS slope over
T=1..30).
- The entropy observable saturates at 0.767-0.770 of the grid by T of about
  6-9 in the treatment regime. The PC (0.154 nats/step, 1.6% of the grid)
  and the cheat (linear) never reach the ceiling.
- Treatment contraction is 0.5-2.3 nats/step, but fitted slopes are only
  0.026-0.115.
- A post-hoc fit on the unsaturated window T=1..5 gives Spearman 0.476
  (< 0.5), so NULL is likely but not demonstrated by a control in range.
- Fix: a PC at about 1-2 nats/step on the same grid, or fit only before
  saturation.
C5 MINOR. 79e9/W4 evaluate.py:62, 158-159. lambda_max is matched within 10%
only at levels 0-1. At levels 2-7 the treatment is <= 0 while the twin is
about 0.011, yet the output says addressed=True. Fix: mark it not addressed.
C6 NOTE. 8a87/W1: the instrument repair was chosen after the treatment
medians were printed (disclosed). No effect: the PC still fails (median 3 vs
3), and the second INSTRUMENT_FAIL becomes NOT_BUILT (evaluate.py:56).
C7 MINOR. 8a87/W4 sim.py:149-154. The "upper-bound" oracle ranks safety
before bits, so it is not the bits-maximising bound claimed in NOTES item 5.
A bits-first oracle (seeds 0-2) gives 1.167 < 1.5, so SPEC_UNATTAINABLE
stands; only the justification is wrong.
C8 NOTE. 8a87/W5 probe: re-run matches (S1 0.322, S2 1.0, S3 0.147). The
twin is not matched on deletion count (disclosed). The pre-freeze revisions
tightened the thresholds.
C9 MINOR (label). 8a87/W5 pass4: ORIG is an identity, not an empirical kill.
- Rows: CHANNEL_RESET and TREATMENT both have 1278 errors, identical per
  seed, with valid_deleted 2775 each.
- The pass4_round2 PREREG forbids attacks fixed by construction; its
  arithmetic check covered ALT only.
- PARK comes from ALT FAIL (A1 0.601 > 0.50; A2 0.856 > 0.80). Fix: relabel
  the fossil as "tautological".
C10 MINOR. 8a87/W5 pass4 evaluate.py:34, 83-84. R_twin_fails_all is computed
but never gates controls_ok. Currently harmless: the twin fails every clause.
D1 MAJOR (outcome flip, likely). HT-a9e2ba7618/W3, pilot_eval.py:17-19 and
NOTES reading 6 / "Repair".
- The pilot checked only absolute ARI >= 0.95. The repair set KC = 1.6, above
  the locking bound for every clique, so oscillator clusters coincide with
  graph components by construction.
- Rows: osc > comp + 0.02 on 0/50 seeds for the PC and 0/50 for the
  treatment; the maximum difference is 0.0.
- [LC] OUTCOME.json: parts {abs: true, gap: true, osc_over_comp: false};
  failure_met true via the osc <= comp + 0.02 clause.
- That failure clause is met by the repaired construction, not by the
  mechanism. A NULL whose deciding clause is fixed by construction is not a
  valid reading.
- Flip: NULL -> SPEC_UNATTAINABLE. The program goes from PARK ("two NULL")
  to SPECULATIVE, with W4 as its one valid NULL, and becomes eligible for the
  pass3_v2 revival.
- Fix: run every success clause on the PC in the pilot.
D2 MAJOR (indeterminate). HT-ae38c641b1/W5 probe, evaluate.py:128, 143-149.
- [LC] The frozen spec.json and DESIGN_NOTES item 6 say "Values between the
  F1 and S1 thresholds (0.15 to 0.40) are INCONCLUSIVE". OUTCOME has S1 0.334,
  S2 0.277, no F clause met, and spec_reading "INCONCLUSIVE band per spec ...
  not a falsification of M2".
- The pass3_v2 PREREG says round 3 classifies with the round-1 classes, which
  have no INCONCLUSIVE, so NULL is the literal class.
- But PROBE_ROUND3_REPORT PARKs ae38 on "two valid NULL readings (W3, W5)",
  and by the spec's own text W5 is not a falsification.
- Flip if the spec band governs: the program's PARK becomes SPECULATIVE.
- Fix: decide in the PREREG whether a frozen spec's INCONCLUSIVE band
  overrides NULL in the counting of valid readings (see X4).
D3 MAJOR (no flip). ae38/W3 evaluate.py:47-77, 89-91.
- The breakpoint counter scales as finite_frac/delta (seed 0: N = 9472, about
  0.1445 x 65536), so beta is about 1 by construction. CONTROL
  (continuous) also gives beta 1.000.
- NULL was decided only by the saturating-model comparison (dAIC_sat 5.0-8.0
  vs a threshold of 10). A shift of about 3 AIC units would have produced a
  SIGNAL on an artefact.
- Fix: count jumps that do not shrink with delta, or treat CONTROL
  beta >= 0.2 as INSTRUMENT_FAIL.
D4 MAJOR (indeterminate). ae38/W4 common.py:321, pilot_eval.py:57.
- SPEC_UNATTAINABLE rests on the readings "S1 for EVERY k (undefined ratio
  = False)" and "all 16 PC configs within 10%".
- Attempt 1: PC passed 16/16. The cheat failed only because gamma_oracle at
  (4,2,0) is undefined. Attempt 2's repair raised PC error to 11.3% at
  (k=8, t=0); the mean error 0.063 would pass.
- Fix: treat undefined cells as not eligible, and state the aggregation rule.
D6 MINOR. a9e2/W4 world.py:44-52, 87-106: the Morlet w0=6 decoder smooths
over the warp-knot spacing; the clock clause misses at 0.287 vs 0.3. NULL
holds on both counts.
D7 NOTE. 974471/W1: PC reduction is 2.5%, then 1.6%, vs 15%. The MWU tests
treat matched elites as independent; not decisive.
D8 MINOR. 974471/W3 evaluate.py:37: the PC is detected on a pooled mean of
0.1085 vs 0.10, but only 3/8 seeds are >= 0.10. NULL is independent: the
treatment's k=50 masked fraction is 1.0, so the failure clause fires.
D9 NOTE. Synthetic CHEAT rows in a9e2/W4 (world.py:149-161) and 974471/W3
(world.py:118-120); see X2.
D10 NOTE. 974471/W6: the twin uses different random streams (1000+s vs
2000+s), so it is matched in distribution only. S1 = 0.4505, max 0.554 <
0.60, so NULL is robust.
E1 NOTE. e106/W2: the 4-cycle repair changed every arm's graph ensemble
after attempt-1 seed-0 treatment rows existed (declared unread). Fix: hash
and seal such rows.
E2 NOTE. e106/W2 world.py:311: the PC failure is real -- per-seed crossings
are 0.0013-0.0087, all < 0.01, with the bit-flip decoder. W2 is unattainable
as specified.
E3 MINOR. e106/W1 NOTES pilot log says twin s95 = 1; PILOT.json and the rows
give 2.0. Correct the note.
E4 NOTE. e106/W1 core.py:103: burn-in may be short at L=64 (density 0.102 ->
0.088), but the ratio is 1.00 and robust (R_cons 1.0 vs R_btw 14.2).
E5 MAJOR (label; no flip). e106/W5 spec premise "p ~ U[0.02,0.12] straddles
the threshold" is false.
- The decoder's waterfall is near p 0.035-0.04, so 79% of blocks are capped
  at t=60.
- Treatment t verified 30/30 by an independent min-sum.
- Post hoc (inadmissible), at p < 0.05 the treatment G is 0.26-0.30 vs twin
  about 0.
- Fix: label it "NULL (spec premise false)". A re-spec needs a new prereg.
E6 MINOR. e743/W1 world.py:76: cv_of returns False when the mean is <= 0, so
the unstable linear PC reads "stable" at tau 28-30. tau_obs = 26 is
unaffected.
E7 NOTE. e743/W1: the invented exhaustion parameters (T=22, eta=0.5) set the
onset ratio (0.348). The fixed-gain control's ratio is 1.0 by construction.
The NULL holds only at this configuration.
E8 NOTE. e743/W1 evaluate.py:114-122: anomaly lines were added post-result
(disclosed). Recomputed tau_obs values match OUTCOME.
E9 MINOR. e743/W3 core.py:112: the PC and cheat bypass the bin_index
histogram path used by the treatment's KL. Fix: sample 256 clones from the
PC's q and bin them.
E10 MINOR. e743/W3 pilot_eval.py:259: the null-twin check `rt_n <= 0.7*rt_n`
is always False, so the pilot gate was vacuous (disclosed). Phase-2 twin vs
control ratio is 0.968, so no effect.
E11 NOTE. e743/W3 core.py:11: the invented K = 0.01 makes re-tracking
diffusion-limited. Ratios 0.874 / 0.903; 4/30 seeds at T <= 0.7xC. NULL is
specific to this configuration.
E12 MINOR. faa9/W1 criteria.py:16: cheat detection requires the PC clause, so
the cheat cannot be detected on its own. The PC failed both attempts
(-0.047, 0.282).
E13 NOTE. faa9/W1 sim.py:98: invented kinetics (mu, D0, Dh, eta).
Unattainability is shown only for this choice.
E14 MAJOR (reason). faa9/W2 evaluate.py:37: the PC margin "PC - twin >= 0.5
bits" is invented.
- Bayes 2.230, uniform quantiser 2.232 and random centres 2.002 bits, so
  clause (b) is unattainable by any readout.
- Read as detected, the class is NULL (Hebb 1.638 fails 10/10). The honest
  label is spec-unattainable.
- The program ends at PARK either way.
E15 MAJOR (no outcome effect). faa9/W2 world.py:179: dw = eta*y*(u - y*w) has
fixed point u/y, so prototypes leave the manifold (only 4/8 outputs used).
Hebb (1.64) is worse than random centres (2.00). Fix: dw = eta*y*(u - w).
E16 NOTE. faa9/W2: the cheat repair came after attempt-1 treatment stats were
printed (round-1 breach class). It touched only the cheat; no effect.

## 4. Defect detail -- HT-55162c0ac0 (lead auditor; every item run or read directly)
F1 MAJOR -- the ORIG kill criterion is met by the attacker's own rows but recorded as NOT fired.
- Where: W6/pass4/attack.py:15-16, 42-43 fix ORIG at r = 0.2. evaluate.py:112
  reads only the r0.2_* variants. evaluate.py:144-151 is the anomaly block
  that notices the hit yet says "ORIG as preregistered (r = 0.2) did not fire".
- PREREG pass4_round2: "non-chaotic carrier with the same coupling graph and
  noise (a contracting map, largest Lyapunov exponent < 0). Kill if the same
  perturbation-spread readout also groups >= 0.8" (R rule: >= 9/10 seeds).
- Evidence (python over pass4/rows.jsonl, ALT_TREATMENT rows). Partners,
  kappa 0.1, eps_g 0.05 and sigma 0.05 are identical to ORIG variant
  r0.2_sigma0.05 (checked row by row).
  - r=0.65: per-seed LLE -0.853 to -0.956 (10/10 < 0); ari_ftle >= 0.8 on
    10/10 seeds, mean 1.000; ALT_NULL_TWIN 0/10, mean -0.033.
  - r=0.80: LLE -0.034 to -0.057 (10/10 < 0); 10/10 seeds, mean 1.000;
    twin 0/10.
  - Both levels are frozen "non-chaotic" in ALT_ATTAINABILITY.json, before
    attack.py ran.
- The r = 0.2 restriction does not rescue "not fired":
  - NOTES.md:60-61 call r = 0.2 contracting because the slope at the origin
    is 0.85 x 0.2 x 3 = 0.51. But |T'| reaches 9, so the Lipschitz constant
    is 1.53. Even r = 0.2 is "contracting" only in the measured-LLE sense,
    the same sense in which r = 0.65 and 0.8 qualify.
  - NOTES calls ORIG an existence test, "refuted by ANY non-chaotic carrier
    that groups".
  - The readability gate (an ORIG-style PC with eps_g 0, not run at 0.65 or
    0.8) protects a NOT-fired reading. It cannot void a 10/10 ARI = 1.0 hit
    against a 0/10 twin.
  - r = 0.2 is a weak carrier: traj_std 0.058 at sigma 0.05, so the product
    coupling (about 3e-3) is swamped by the 0.05 leak. It tested amplitude,
    not stability; program.json's own note concedes "the readout tracks
    carrier amplitude, not chaos".
- Flip: ORIG.fired false -> TRUE (fired_by: ALT r=0.65 and 0.8, sigma 0.05).
  - The original-world claim becomes FOSSIL, with prior art labelled
    KNOWN_ANALOGUE_FOUND (perturbation-response network inference).
  - The predicate stays PARK (ALT FAIL; evaluate.py:154).
  - Calibration LEDGER.md:13 records the author's "ORIG would FIRE"
    prediction as wrong. It was right at matched noise.
- Residual ambiguity: under a strict global-Lipschitz reading no tested level
  qualifies, r = 0.2 included. ORIG would then be NOT ASSESSABLE -- still not
  "not fired".
- Fix: evaluate ORIG over every non-chaotic, matched-coupling, matched-noise
  carrier the attack produced (or rerun r = 0.65 with its own PC), then
  relabel and amend calibration row 13.
F2 MINOR -- R "not reproduced" is an artefact of a two-sided chance band.
- Where: pass4/evaluate.py:22, 36-38 (|mean ari_corr| <= 0.1).
- Evidence: R treatment mean ari_corr is -0.111 (9/10 seeds negative). PC
  -0.049, twin +0.031, round 3 -0.083.
- A value below chance carries no grouping information, and spec S2
  (ftle - corr) is 1.111.
- The reading was frozen pre-run, so this is not a breach.
- Flip: R becomes reproduced under a one-sided reading. Predicate unchanged.
- Fix: one-sided chance, or a band calibrated on the twin.
F3 NOTE -- pass4/evaluate.py:130 anomaly block was added after evaluate run 1 (disclosed).
- Re-run on a scratch copy reproduces PASS4_OUTCOME.json exactly, except
  core_minutes.
F4 NOTE -- the ALT PC and cheat do not exercise the treatment parameters.
- The PC uses eps_g 0 at chaotic levels and random partners at non-chaotic
  levels; its rows there equal ALT_NULL_TWIN.
- ALT FAIL is robust: A1 = 1.0 - 1.0 = 0 < 0.2; A2 pooled 0.369 and
  level-mean 0.453, both < 0.6.
F5 NOTE -- the W6 probe SIGNAL is verified.
- probe/evaluate.py re-run on a scratch copy: identical OUTCOME.
- S1 1.0, S2 1.083; twin 0.019 / 0.024; PC and cheat 1.0 / 0.979.
- Seeds 0-9, disjoint from Pass 4's 100-109.
F6 MINOR -- W3 (round 1) INSTRUMENT_FAIL: correct class, but the treatment was read anyway.
- W3/evaluate.py:44-78 publishes treatment statistics despite pc_det False.
  The PREREG says "no reading of the treatment is made". No repair followed,
  so no breach resulted.
- The "amplitude 0.02 = peak-to-peak [0, 0.02]" reading may cause the PC
  failure (mean ARI 0.024); this was not tested.
- The NOTES mtime equals OUTCOME's, so the pre-run order cannot be verified.
- Re-run on a scratch copy: INSTRUMENT_FAIL, PC 0.024, cheat detected.
  No flip.
F7 NOTE -- W2 (round 2) SPEC_UNATTAINABLE is verified.
- pilot_eval.py re-run on a scratch copy: PC 1.0 at p = 1..4; cheat
  detected; twin p_max 0; pooled twin fraction 0.4 at p >= 2, against the
  spec's twin bound of 0.1.
- NOTES A9 (a twin-clause violation counts as "null meets success") is sound,
  since no treatment can succeed on these seeds.
- The cheat uses an uncontrolled twin. The one repair (an intercept in the
  shared fit) came before any treatment code. No flip.

## 5. What changes

Recorded outcomes or labels that change:
- HT-55162c0ac0 W6 Pass 4 (F1): ORIG fired = TRUE, triggered by the attacker's
  own ALT rows. At r = 0.65 and r = 0.8 the LLE is < 0 on 10/10 seeds, ARI is
  1.0 on 10/10 seeds, and the twin groups on 0/10. Coupling graph, kappa,
  eps_g and sigma all match.
  - The original-world claim becomes FOSSIL / KNOWN_ANALOGUE_FOUND.
  - Calibration LEDGER row 13 should record the prediction as correct at
    matched noise.
  - The predicate stays PARK (ALT FAIL).
- HT-a9e2ba7618 W3 (D1): NULL -> SPEC_UNATTAINABLE. The program goes from PARK
  to SPECULATIVE and becomes eligible for the Pass 3 v2 revival.

Contested (decision needed, no recorded change asserted):
- HT-ae38c641b1 W5 (D2): the spec's INCONCLUSIVE band vs the PREREG's NULL.
  If the band governs, the program's PARK becomes SPECULATIVE.
- HT-321a8fd8e0 Pass 4 (A11): the PROBING verdict rests on an ALT fixed by
  counting. Under the round-2 counting rule it would be PARK.
- HT-79e904e13a W4 (C4): entropy-ceiling saturation; NULL is likely but not
  instrument-validated.
- HT-ae38c641b1 W4 (D4): SPEC_UNATTAINABLE rests on aggregation readings.

Flips proposed by sub-auditors and rejected by the lead auditor, with
reasons:
- HT-47f4c02be4 W1 (B1): the spec's own failure clause fires on the twin.
- HT-79e904e13a W1 (C3): the treatment meets the spec's failure clause
  "decline < 0.1".
