# AUDIT Z2 -- spec-vs-code conformance of the probed Hecate worlds

Date: 2026-10-01T01:46Z (clock). Auditor: Claude agent (lead) + 7 read-only sub-auditors.
Read-only; this file is the only repo write. No git writes, no model/API calls.
Scratch reruns (copies only) in the session scratchpad Z2/.

Question: does each probed world's code implement its FROZEN spec?
- Round 1/2 worlds: the program.json experiments[] entry.
- Round-3 probes: spec.json + revisions.json + ATTAINABILITY.json + controls.py.
Drift classes checked:
- (a) statistic computed differently from the stated one
- (b) seeds / n / levels differ from the spec
- (c) null twin built differently
- (d) positive control (PC) not the stated construction
- (e) criterion_as_applied differs from the frozen text
- (f) treatment differs from the spec
Not repeated: AUDIT_B_world_evaluators.md (items A1-F7, X1-X4) and
INV_J_v2_clause_reachability.md (discriminability and Goodharting). Overlaps are cited by ID.

COVERAGE: 37/37 probed evaluations (29 round-1/2 OUTCOME.json + 8 round-3 probe/OUTCOME.json).
Pass-4 attacks are out of scope.

Severity:
- BLOCKING: the recorded outcome is wrong as recorded.
- MAJOR: material drift, or a reading that decides the class.
- MINOR: drift that cannot change the reading.
- NOTE: observation only.
"disc" = disclosed in NOTES; "undisc" = undisclosed. "Changes outcome" means changes the
recorded class (YES/NO/UNKNOWN).

## 0. Mechanical check of criterion_as_applied (e)

All 37 OUTCOME.json carry criterion_as_applied. None is byte-identical to the frozen text:
- round 1/2: a prose reading;
- round 3: clause dicts or lists.
Each sub-auditor compared them in substance (thresholds, quantifiers, seed counts,
added/dropped clauses). No silent threshold change was found. Every quantifier or aggregation
reading that differs from the spec is listed per world below. Most are disclosed in the NOTES.

## 1. Per-world table

| world | outcome | drift items (new) | sev | changes outcome |
|---|---|---|---|---|
| 056d/W1 r1 | INSTRUMENT_FAIL | Lasso on stacked series, not time-mean (disc); PC gate AUC>=0.80 reading (disc) | NOTE | NO |
| 056d/W4 r2 | NULL | "200 trials" run as 5 seeds x 200, every cell (disc); kernel-energy over ker(P) dim 28, not "kernel_dim 8" (disc) | MINOR | NO |
| 056d/W5 probe | NULL | none; treatment pre-change FA 0.028 vs nominal 0.05 | NOTE | NO |
| 2a8a/W1 r2 | NULL | rank-1 terms max-normalised (disc); S1 "every r" applied per (r,lambda) cell (disc) | NOTE | NO |
| 2a8a/W4 r1 | NULL | spec gaps filled (first-exit LMDP, ratio of medians); alt reading per-goal ratio 1.01-1.08 < 1.2 | NOTE | NO |
| 321a/W1 r1 SIGNAL | SIGNAL | Z1: k>=4 ">=0.5" clause carried by coset-leader tie-break order (see 2.1) | MAJOR | UNKNOWN (YES under tie-robust decode) |
| 37e3/W1 r1 | INSTRUMENT_FAIL | twin = scaled+clipped ramp, flat after m=53 (disc); diff taken vs CONTROL not twin (disc) | MINOR | NO |
| 37e3/W4 r2 | SPEC_UNATTAINABLE | sanction fitness = -cost, medians at gen 400, rate matched on mean prob (disc) | NOTE | NO |
| 37e3/W5 probe | NULL | all arms initialised at x_good; spec silent (half-disc) | NOTE | UNKNOWN (low risk) |
| 47f4/W1 r2 | NULL | Z2: control "predict prime-density only" built as r(0)=1 by construction (see 2.2) | MINOR (lead) / MAJOR (sub) | NO (lead) |
| 47f4/W4 r1 | CONFOUNDED | none new (pooled-mean ratio, window-1 prior: disc) | NOTE | NO |
| 5b0b/W4 r1 SIGNAL | SIGNAL | "grounded" = contiguous-trace reading (disc); edge-wise reading OR 1.541, p 2.2e-4 | NOTE | NO |
| 55162/W2 r2 | SPEC_UNATTAINABLE | 50 trials pooled to 5x50 (disc); open-loop U(-delta,delta) drive, not "uncontrolled" (disc) | MINOR | NO (D2 probably NO) |
| 55162/W3 r1 | INSTRUMENT_FAIL | Z3: twin per-site noise gives 100 singleton clusters, retention 0.0: twin clause passes by construction (undisc); loop-area test two-sided (disc) | MINOR | NO |
| 55162/W6 probe SIGNAL | SIGNAL | none; evaluator additionally requires no F clause (stricter) | NOTE | NO |
| 71b6/W3 r1 SIGNAL | SIGNAL | S2 speaker sampled not argmax (disc; argmax rerun keeps SIGNAL, rho 0.773); twin-fail clause per theta (disc) | MINOR | NO |
| 79e9/W1 r2 | NULL | Z4: no fold exists in the gLV build; the -0.01 eigenvalue is a transcritical (extinction) boundary (part-disc); decline = diff of medians, not paired (undisc, 0.021 vs 0.024) | MAJOR | UNKNOWN |
| 79e9/W4 r1 | NULL | Spearman over 8 level means (disc; pooled 0.200, all < 0.5); r scaled per arm domain (disc) | MINOR | NO |
| 8a87/W1 r1 | NOT_BUILT | twin not yoked to treatment UNSAT times (1013 vs 482 events) (disc); 2200 vs 2000 steps (disc) | NOTE | NO |
| 8a87/W4 r2 | SPEC_UNATTAINABLE | PC is a hybrid (true-model planning, own probe trigger) (disc) | NOTE | NO |
| 8a87/W5 probe SIGNAL | SIGNAL | none new (MUS-size-2 / channel-reset tie = AUDIT_B C8/C9, INV_J) | NOTE | NO |
| 974471/W1 r2 | SPEC_UNATTAINABLE | probe v ~ U[-1,1]^N, not W_in direction (disc; W_in rerun 2.3%/2.4% vs 15%) | MINOR | NO |
| 974471/W3 r1 | NULL | Z5: implementer-chosen regime (distractor sd 3, leak 1.0, rho 0.9 tanh) gives k=50 pressure; tanh-saturation explanation uncontrolled (post-run disc) | MINOR | UNKNOWN |
| 974471/W6 probe | NULL | elites keep their one-life fitness, not re-lived (disc; re-live rerun I_perp 0.463 < 0.60) | MINOR | NO |
| a9e2/W3 r2 | NULL (corr. K4: SPEC_UNATTAINABLE) | twin = finest graph + ~58% random edges (part-disc); osc>comp coded as diff of medians (undisc) | MINOR | NO (AUDIT_B D1 governs) |
| a9e2/W4 r1 | NULL | twin carrier spectrum matched only at w=0, not "same spectra" (part-disc); 1 pulse/cycle, 10x size (disc) | MINOR | NO |
| ae38/W3 r1 | NULL | Z6: intervention inert: d=1,3,6 give identical N(delta), beta on every seed (undisc) | NOTE | NO |
| ae38/W4 r2 | SPEC_UNATTAINABLE | PC checked on 16/24 configs (disc); PC denominator = ground-truth area, not sound-test area (part-disc) | MINOR | NO |
| ae38/W5 probe | NULL | none; S1 0.33359, S2 0.27664 reproduced (INCONCLUSIVE band = AUDIT_B D2) | NOTE | NO |
| e106/W1 r2 | NULL | twin eps fitted to non-empty avalanche mean: 0.85x on the spec's all-injection mean (disc, understated); 5 seeds vs "4-seed bootstrap" | MINOR | NO |
| e106/W2 r1 | INSTRUMENT_FAIL | crossing requires all 5 per-seed fitted crossings in [0.01,0.2] + slopes > 0; spec: "a crossing exists" (undisc); pooled: none either way | MINOR | NO |
| e106/W5 probe | NULL | none; PC/twin formulas and G features match exactly | NOTE | NO |
| e743/W1 r1 | NULL | control fixes clone gain a, not kill gain k*C (disc); twin surrogate C not mean-matched after clip (median 1.10x) (part-disc); twin onsets = treatment onsets (non-discriminating) | MINOR | NO |
| e743/W3 r2 | NULL | re-tracking uses clone mean/sd, not posterior (disc); twin sd pool from own run (disc) | MINOR | NO |
| faa9/W1 r2 | SPEC_UNATTAINABLE | low-low edge g unspecified (g=1) + cutoff z>1 repair (disc); alt readings r -0.25..0.26, all < 0.5 | MINOR | NO |
| faa9/W2 r1 | INSTRUMENT_FAIL | Z7: twin "centres random from input range" read as on-manifold u(x*); 2-D box reading flips class (see 2.3) | MAJOR | UNKNOWN (YES under box reading; program PARK unchanged) |
| faa9/W6 probe | NULL | none; criterion_as_applied matches S1-S4/F1-F3 verbatim | NOTE | NO |

Totals (37):
- BLOCKING: 0.
- MAJOR: 3 (321a/W1, 79e9/W1, faa9/W2). 47f4/W1 was MAJOR per the sub-auditor; the lead
  auditor downgraded it (2.2).
- MINOR: 19. NOTE-only: 15.
- Changes outcome: YES 0, UNKNOWN 5 (321a/W1, 79e9/W1, faa9/W2, 974471/W3, 37e3/W5), NO 32.
- Of the 5 SIGNAL worlds, only 321a/W1 has outcome-relevant drift.

## 2. Detail on the outcome-relevant items

### 2.1 Z1 -- HT-321a8fd8e0/W1 (SIGNAL): tie-breaking carries the k>=4 clause. MAJOR, UNKNOWN.
The spec says "outcome = nearest-codeword decode". It is silent on ties.

What the code does (world.py:137-162):
- It decodes via a coset-leader table built in itertools.combinations order.
- At distance 4 from the true codeword, a weight-8 codeword can sit at a tied distance 4.
- The fixed order then hands the coalition a "win".

Lead-auditor rerun of the sub-auditor's script on the exact sampled coalitions (seeds 0-19,
rng [1,seed]; w321.py is identical to world.py modulo line endings):

| k | recorded wins | strict-nearer wins | strict but not recorded | won only on a tie |
|---|---|---|---|---|
| 4 | 2353/4000 = 0.588 | 692/4000 = 0.173 | 0 | 0.415 |
| 5 | 3682/4000 = 0.920 | 1919/4000 = 0.480 | 0 | 0.440 |

What this means:
- The k<=3 half (rate 0) is untouched.
- The ">=0.5 for k>=4" half holds only through deterministic tie resolution that the
  coalition can exploit.
- Under random tie-breaking (expected tie-win about 0.5 x tie fraction: k=4 about 0.38),
  or strict wins only, k=4 and k=5 fall below 0.5. SIGNAL would become NULL.
- NOTES disclose a deterministic decoder. They do not disclose that the SIGNAL depends on it.

This is not in AUDIT_B (A10/A11 cover the PC pool and the Pass-4 ALT).
Fix: declare the tie rule in a re-adjudication. Strict or random ties gives NULL; the recorded
reading stands only if "a fixed public tie order" is accepted as part of the rule.

### 2.2 Z2 -- HT-47f4c02be4/W1 (NULL): control construction. Sub-auditor MAJOR; lead auditor MINOR, NO.
The sub-auditor's case:
- The control "depth frozen at 0 (predict prime-density only)" is coded so that every
  non-silent n is residual: r(0) = 1 by construction (agent.py:24-31).
- So clause B, r(20)/r(0) >= 0.9, reduces to r(20) >= 0.9.
- With a hard-decision density predictor (always "composite"), r(0) is about 0.097, the
  ratio about 2.2, and clause B passes. Clause A passes (max deviation 0.0042) and the
  twin fails clause A, so NULL -> SIGNAL.

Lead-auditor reading:
- Clause A's own formula is prod_{p<=p_K}(1-1/p), and at K=0 the empty product is 1.
- So the frozen spec itself defines r(0) = 1. r(K) is the unexplained-by-sieve fraction,
  not a classifier error.
- A hard-decision predictor would make r(0) a different observable from r(K>=1). Clause A
  would then be inconsistent at K=0.
- The code's r(0) = 1 conforms to the spec's observable.
- The twin depleting (0.21) is the spec's written falsifier (AUDIT_B B1).
- Recorded as MINOR: the control text "predict prime-density" is under-specified. NULL stands.

### 2.3 Z7 -- HT-faa9277e02/W2 (INSTRUMENT_FAIL): twin reading decides the class. MAJOR, UNKNOWN.
- The spec's twin is "tuning centres drawn at random from the input range".
- NOTES:40 read this as the noiseless manifold u(x*), x* ~ U[0,99]. That reading is
  disclosed, but NOTES:117 then attributes the PC failure to "the spec".
- On-manifold random centres score 2.002 bits against Bayes 2.230. This is the root of
  E14's unattainable "PC - twin >= 0.5".
- Sub-auditor scratch rerun with centres uniform over the 2-D input box: twin 1.455-1.502.
  - PC - twin is >= 0.5 on 10/10 seeds (0.53-0.96), so the instrument is detected.
  - The twin fails clause (a); the treatment fails (b) (1.638 - 1.455 = 0.18).
  - The class becomes NULL, not INSTRUMENT_FAIL.
- The lead auditor checked the code and spec text (world.py:106-107, NOTES:39-40). The rerun
  numbers were not re-run by the lead.
- Program verdict PARK either way (consistent with AUDIT_B E14).

### 2.4 Z4 -- HT-79e904e13a/W1 (NULL): no fold in the world. MAJOR, UNKNOWN.
- The spec's hypothesis is early warning before a "fold".
- The gLV build reaches eigenvalue -0.01 by driving one species to near-extinction:
  - min x* 0.0065-0.014 against a median of about 0.9 (seeds 0-9);
  - a transcritical boundary, with no alternative stable state.
- The slow mode puts 23-52% of its weight on that species, whose press flux is tiny.
- The ORACLE scores 1.0 at every distance.
- The NULL is therefore a NULL for "extinction boundary". Whether it transfers to a fold
  is untested.
- The undisclosed median-difference vs paired statistic (0.024 vs 0.021) is immaterial:
  F "< 0.1" fires either way.
- Distinct from AUDIT_B C3 (twin-clause path).

### 2.5 Other UNKNOWN / undisclosed items
- 974471/W3 (Z5):
  - The deciding failure clause |k3-k50| = 0 < 0.2 arises in an implementer-chosen
    parameter regime.
  - The hand mask gain is 0.897 at k=50 vs 0.108 at k=3, and the treatment masks 1.0 at
    both k.
  - The spec's tanh-saturation stupid explanation was never controlled. Not tested.
- 37e3/W5: an initialisation the spec does not give. Low risk: the twin and PC share it.
- 55162/W3 (Z3) twin, and e743/W1 twin: built so that the twin clause cannot discriminate.
  No effect, because those worlds failed on other clauses.
- ae38/W3 (Z6): the intervention d has zero effect on N(delta) and beta (identical across
  d on every seed). This is undisclosed and supports AUDIT_B D3: the observable is
  insensitive.

## 3. Cross-cutting

Z-X1. Spec silences become outcome-deciding readings: tie rule (321a), "input range"
(faa9/W2), "fold" realisation (79e9/W1), regime parameters (974471/W3, e743/W1). Every one is
disclosed as a reading, but none was flagged as a reading that decides the class.
Fix: at implementation time, rerun each disclosed reading's nearest alternative when it
touches a deciding clause, and record the alternative's class.

Z-X2. Null twins are the commonest drift site: about 11/37 worlds (37e3/W1, 55162/W3, 79e9/W4, 8a87/W1, 8a87/W4, a9e2/W3, a9e2/W4, e106/W1, e743/W1, e743/W3, faa9/W2). Recurring forms:
- matched on a different statistic than the spec names (e106/W1, e743/W1, a9e2/W4);
- not yoked to the treatment (8a87/W1);
- degenerate by construction (55162/W3);
- padded with random structure (a9e2/W3).
None changed an outcome here, but in three worlds the twin could not have discriminated.

Z-X3. Aggregation readings ("over 10 seeds", "paired", "for every k") are mostly disclosed.
Two are undisclosed: 79e9/W1 median-difference, and a9e2/W3 median-difference. Neither
decides.

## 4. What should change (no edits made)
- 321a/W1: re-adjudicate SIGNAL under an explicit tie rule (2.1). This is the only SIGNAL
  world with outcome-relevant drift.
- faa9/W2: record the class as reading-dependent (INSTRUMENT_FAIL on-manifold, NULL on the
  box reading). Program PARK unchanged.
- 79e9/W1: annotate the NULL as "transcritical, no fold". The spec's fold claim is untested.
- 974471/W3: annotate the NULL as regime-specific, with the tanh-saturation explanation open.
- 47f4/W1: no change. Note that r(0) = 1 follows from clause A's empty product.
