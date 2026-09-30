+==============================================================================+
|  REVIEW PACKET -- ENSORAIN INSTRUMENT LINE CLOSE-OUT                          |
|  PKG-F observability gate + PKG-F-HIER + LM02 bounded window assay            |
|  Author: Ensorain (Foundry seat), M2 / SPECTREX5, instance m2-a466d709         |
|  Date: 2026-09-30                                                             |
|  For: operator (HITL) + external reviewers                                    |
|  Status: DONE (dev). Line FROZEN at fd582afb2. LM01 HOLD.                     |
|  Self-contained: no repo access needed; every load-bearing number is inline.  |
+==============================================================================+

-----
0. SUMMARY
-----

Mandate (operator, 2026-09-30):
- Finish the drift gate, so that low power never means "unchanged".
- Run LM02 as a BOUNDED instrument test of whether a finite window preserves the conclusions that matter.
- Then freeze the line and move the seat to the substrate collider (WTP-04 Habitable Islands).
- A second ruling added a separate population-evidence arm (PKG-F-HIER) and fixed the LM02 framing.

Verdicts:
- Strict PKG-F gate: REPAIRED. Stale-record leak 3e-4 vs .30 / .70 for the old soft gate. In these worlds it behaves
  as a recent window.
- LM02: WINDOW_NOT_SUPPORTED. No window size preserves >= 6/8 worlds in ANY of 11 regimes. STOPPED, no tuning.
- PKG-F-HIER: POP_VALUE_REQUIRES_REPRESENTATIVENESS (falsified by HIDDEN):
  - it recovers 76% of the stationary value the strict gate forfeits;
  - it is safe (<= .022 stale) in every regime except the adversarial one;
  - in the adversarial one it is .124 stale, above p_max .10.
- Instrument self-check: the held-out reference replicate was preserved in 83/88 worlds (94%).

-----
1. WHAT WAS BUILT, AND WHAT WAS COMMITTED BEFORE MEASUREMENT
-----

Common set-up (all worlds):
- 12x12x12 tensor field, standardized (SD 1).
- One exposure walk of N = 6400 records (each step changes one coordinate; 2% teleports).
- Observation noise SD .1.
- A record is STALE iff |true value when recorded - final value| > DELTA = .25.

(a) Strict observability gate (pkgf_obs.obs_keep).
- Old soft gate leak paths:
  - "unchanged" = failure to reject;
  - cells with no recent record admitted on a point-estimated changed fraction < .5;
  - no detected change -> all history admitted.
- New rule:
  - a cell's pre-boundary records are admitted iff it has >= 1 post-boundary record AND
    |mean_pre - mean_post| + 1.645 se <= .25 (one-sided 5% equivalence test);
  - the boundary is the detected change point, else the last N/6.
- Precommit 5a9d58345 -> result fe6393297. 48 fresh worlds.

(b) PKG-F-HIER (population arm; the strict gate is untouched and asserted equal).
- States: CERTIFIED_FRESH / POPULATION_SUPPORTED / QUARANTINED / CHANGED. Supported is never merged into certified.
- Bound (distribution-free Markov): over a stratum's tested cells, q_i = d_i^2 - se_i^2 estimates Delta_i^2, and the
  stale fraction is <= E[Delta^2] / DELTA^2. The one-sided 95% UCB must be <= p_max = .10 (governing); .05 and .20
  are also reported.
- Strata: 8 octants of the grid, declared before data. A global single-stratum pool is the weak baseline.
- Coverage: >= 30 tested cells AND >= 20% of the stratum's cells tested; otherwise QUARANTINED.

(c) LM02 bounded assay.
- 11 regimes x 8 worlds = 88 eval worlds.
- 14 memory policies + 4 final-field reference replicates.
- 8 substrates fitted on the kept records only:
  - cheap: CONST, per-cell TABLE, additive MARGINAL;
  - WTP online learners: lowrank, CP, TT, DCT, additive.
- Prereg, assay code AND scorer were committed at 8b49a4456 BEFORE the eval run.

-----
2. THE CLAIM AND WHY IT MATTERS
-----

Every later collider experiment runs on retained history. A drift gate that silently readmits stale records would
contaminate every substrate comparison. A window policy that looks fine on statistics but moves the conclusions would
bias every phase diagram.

The question: can bounded temporal memory preserve
- competence (the attainable level),
- substrate ORDERING,
- the ANOMALY flag (the best non-cheap substrate beats the best cheap competitor by > .10 AC),
at <= 10% stale contamination?

AC = -log10(MSE / field variance).

-----
3. DESIGN AS EXECUTED
-----

Regimes:

| regime | change |
|---|---|
| STAT | none |
| ABRUPT | all cells, step at 2/3 |
| DIFFUSE | 30% random cells |
| RAMP05 / RAMP20 / RAMP50 | linear ramps of width .05 / .2 / .5 of the life |
| MULTI | 5 switches, each rho in {1, .5, .1, 0} |
| LOCAL_BLOCK | one octant, ALIGNED with the strata |
| LOCAL_BOX | a 7^3 box, MISALIGNED |
| MODE_SLAB | 3 index values of one mode, through every stratum |
| HIDDEN | ADVERSARIAL: only cells NOT revisited after the switch change (p .5) |

Policies:
- FULL, ORACLE (truly non-stale; diagnostic);
- WINDOW last N/12, N/6, N/3, N/2;
- STRICT and HIER at the detected boundary (_det) and at the oracle boundary (_orc);
- POPG (global pool); HIER at p .05 / .20.

Preservation per world requires all four:
- competence: best AC >= ATTAINABLE - .10, where ATTAINABLE = max(FULL, ORACLE);
- ordering: Kendall tau >= .60 vs the consensus of 3 final-field references;
- anomaly: the world flag equals the consensus flag (a consensus margin within +-.05 of .10 counts as ambiguous);
- contamination: stale fraction of kept records <= .10.

Verdict rules:
- WINDOW_SUFFICIENT: two adjacent windows each >= 6/8 in every regime.
- WINDOW_REGIME_DEPENDENT: some window reaches >= 6/8 in >= 9/11 regimes, and the best window differs across regimes.
- WINDOW_NOT_SUPPORTED: otherwise.
- POPULATION_EVIDENCE_ADDS_VALUE needs both:
  - STAT recovery >= 50% of the STALE-split gap between STRICT and the reference;
  - realized stale fraction among supported records <= .10 in EVERY regime INCLUDING HIDDEN.

-----
4. DEV CALIBRATION (DISCLOSED; non-eval seeds only, before the precommit)
-----

The criteria were changed three times before 8b49a4456:
1. A single reference -> a consensus of 3 + a held-out 4th as the noise control. One substrate's AC moves ~.2 between
   noise draws of the SAME world; FULL "failed" against one reference in a stationary world.
2. Per-substrate anomaly flags -> one world-level flag, for the same noise reason.
3. Competence vs a full-life current-world reference -> vs ATTAINABLE. Against the full-life reference every policy,
   ORACLE included, failed every changed world. That is data availability, not memory policy. The data-availability
   gap is now reported separately.

A reviewer should ask whether these changes made the test easier. They made windows EASIER to pass. Windows still
failed everywhere.

-----
5. RESULTS (EXACT)
-----

5a. Strict gate (48 worlds). Stale records admitted / stale records:

| family | old soft gate | strict gate |
|---|---|---|
| DRIFT | 23850/79854 = .299 | 24/79854 = .0003 |
| MULTI | 23579/33774 = .698 | 6/33774 = .0002 |

- Under drift, the strict gate is the only readout never harmed. Mean STALE-split dAC at ramp width .5: all-history
  -1.28, old soft -.77, strict +.01.
- Price: it verifies only 4% of valid old records, so it acts as a recent window. In stationary worlds it forfeits
  the entire +.60 AC gain from old records.
- Of the precommitted checks, one ("no worse than quarantining everything") failed in stationary worlds by .006. Two
  price predictions came out as predicted.

5b. LM02 preservation (worlds of 8):

| policy | STAT | ABR | DIFF | R05 | R20 | R50 | MULTI | LBLK | LBOX | SLAB | HIDDEN |
|---|---|---|---|---|---|---|---|---|---|---|---|
| REF_HOLD | 8 | 8 | 8 | 7 | 7 | 6 | 8 | 8 | 8 | 7 | 8 |
| FULL | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 5 |
| ORACLE | 8 | 4 | 8 | 4 | 6 | 1 | 5 | 7 | 8 | 5 | 8 |
| WIN_12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| WIN_6 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 |
| WIN_3 | 0 | 3 | 0 | 5 | 4 | 0 | 1 | 1 | 0 | 0 | 0 |
| WIN_2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| STRICT_det | 0 | 2 | 0 | 4 | 5 | 0 | 3 | 0 | 0 | 1 | 0 |
| HIER_det | 6 | 2 | 0 | 4 | 5 | 0 | 3 | 3 | 0 | 1 | 0 |
| HIER_orc | 8 | 2 | 0 | 4 | 1 | 0 | 5 | 5 | 0 | 1 | 2 |
| POPG_det | 7 | 2 | 0 | 4 | 5 | 0 | 3 | 0 | 0 | 1 | 2 |

Failure shape: a squeeze, not a tuning gap. Component passes over 88 worlds:

| window | competence | ordering | anomaly | contamination |
|---|---|---|---|---|
| N/12 | 0 | 47 | 61 | 88 |
| N/6 | 4 | 76 | 70 | 88 |
| N/3 | 23 | 82 | 83 | 69 |
| N/2 | 25 | 84 | 73 | 49 |

- Short windows are clean but lose competence. In STAT, N/2 reaches 1.76 AC and N/6 reaches .92, vs 2.05 attainable.
- Long windows regain competence only with .26-.39 stale records in abrupt / slow-ramp / multi worlds.
- ORDERING and the ANOMALY flag are much more robust than competence.

Data availability (attainable vs a full life of current-world data), in AC:

| STAT | ABRUPT | DIFFUSE | RAMP05 | RAMP20 | RAMP50 | MULTI | LBLK | LBOX | SLAB | HIDDEN |
|---|---|---|---|---|---|---|---|---|---|---|
| -.003 | .52 | .57 | .65 | .61 | .75 | .95 | .45 | .46 | .36 | .61 |

This is the largest loss in every changed world, and it belongs to no memory policy.

5c. PKG-F-HIER.

Value:
- STAT: recovery .76 of the STALE gap. Best AC 1.97 vs strict 1.08 vs 2.05 attainable; retains 88% of valid records vs
  36%.
- LOCAL_BLOCK: recovery .25. Best AC 1.12 vs .80; retains 93% vs 48%.
- ABRUPT / DIFFUSE / RAMP / MULTI: the bound never passed (0 supported records). HIER equals STRICT: conservative.

Safety (stale / supported records, pooled):

| regime | HIER_det | fraction |
|---|---|---|
| STAT | 0/26807 | 0 |
| LOCAL_BLOCK | 0/21375 | 0 |
| LOCAL_BOX | 2/281 | .007 |
| MODE_SLAB | 91/4186 | .022 |
| HIDDEN | 3372/27212 | .124 (FAIL; > .10) |

HIDDEN at the other settings: HIER_orc .210, p05 .126, p20 .125, global pool .125.

Global pool vs strata (prediction L4 REFUTED, in the safe direction):
- The global pool supported records ONLY in STAT and HIDDEN.
- Localized change inflated its global bound, so it supported nothing. It fails CONSERVATIVE, not unsafe.
- The cost of global pooling is lost value: LOCAL_BLOCK preservation 0/8 global vs 3/8 HIER_det vs 5/8 HIER_orc.

5d. Gradual drift, detector placement vs memory policy (preserved worlds, STRICT; HIER is the same):

| ramp | detected boundary | oracle boundary |
|---|---|---|
| RAMP05 | 4/8 | 4/8 |
| RAMP20 | 5/8 | 1/8 |
| RAMP50 | 0/8 | 0/8 |

- The mid-ramp detector does BETTER than the oracle ramp-end boundary: it trades a little contamination for data.
- The ramp failures are memory/data failures, not detector failures. The detector was NOT repaired.

-----
6. INCIDENTS, AND WHAT THEY VALIDATED
-----

- The first eval launch crashed at task 1. A runpy/multiprocessing pickling error in the launcher; no rows were
  produced. It was relaunched unchanged through an importable wrapper. Verified: the results directory was empty
  before the relaunch.
- The smoke test's false-CHANGED rate in stationary worlds was 10.4% at a 10% two-sided null. The per-cell z-test is
  calibrated; this is not a bug.
- The old soft gate's apparent multi-switch "win" (+.184 vs +.134) was bought by admitting 70% of the stale records.
  It was luck with partial switches, not a property of the gate.

-----
7. WHAT THIS DOES AND DOES NOT ESTABLISH
-----

Does:
- In walk-exposure tensor worlds at noise .1, a per-cell drift gate can be made leak-free, and then it is a recent
  window.
- No fixed window preserves attainable competence under any of the 11 regimes.
- Ordering and anomaly conclusions are far more robust than competence.
- Population evidence recovers real value, and is safe exactly as far as the tested cells represent the untested ones.

Does NOT:
- Generalize beyond this geometry, noise level, walk and substrate set. There are 8 worlds per regime; one world is
  12.5 points of a rate.
- Show that no OTHER bounded memory (e.g. graded weights, learned relevance) could pass. Graded reuse was not built
  (optional per the ruling).
- Certify the preservation thresholds (.10 AC, tau .60, flag margin .10). They were fixed on dev seeds; a reviewer may
  judge them arbitrary.
- The Markov bound is valid only for TESTED cells. Its use on untested cells is an exchangeability ASSUMPTION, and
  HIDDEN shows exactly where it breaks.

-----
8. DECISION / RECOMMENDATION
-----

Done, per the operator's step 3:
- Freeze the line.
- The strict gate stays the gate of record. PKG-F-HIER stays a LABELED arm, valid only under a declared
  representativeness assumption.
- LM01 stays on HOLD.
- Collider rule: any claim on retained history names the gate that built its record set, and compares memory policies
  against ATTAINABLE.

Seat lean:
- Move to WTP-04 Habitable Islands now.
- The data-availability finding is itself a habitability variable: after a change, 1/3 of a life of current data is
  the binding constraint. The learning-time / lifetime ratio should be a primary axis of the habitability map.

-----
9. QUESTIONS FOR THE REVIEWER (answer these against us, not with us)
-----

1. The three pre-commit criterion changes (s4) all made windows easier to pass. Is there a remaining criterion choice
   that made them HARDER? Would a reasonable choice have produced WINDOW_REGIME_DEPENDENT?
2. Is "competence vs max(FULL, ORACLE)" the right attainable reference? In ramp worlds ORACLE < FULL because stale
   records are still informative. Should the reference be higher, e.g. a tuned recency-weighted fit?
3. Is HIDDEN a fair falsifier, or a strawman no real world produces? Name a mechanism by which real environments hide
   drift in unrevisited cells, or argue that none exists.
4. The Markov bound is loose. Would a tighter bound, using the change-size distribution, have admitted more AND stayed
   safe? Or would it only have moved the HIDDEN failure?
5. Should the strict gate's recent-window behaviour count as "the drift problem solved", or as the drift problem
   renamed?
6. Is this whole line worth having done, or should the operator have skipped straight to the collider? "Not worth it"
   is an acceptable answer.

-----
10. ARTIFACTS (branch ensorain/base-role-adopt-2026-09-23; worktree D:/Prometheus-worktrees/ensorain-base-role)
-----

Operator texts (verbatim + MANIFEST):
- roles/Ensorain/prompts/2026-09-30_operator_direction/ (c3525f647)
- roles/Ensorain/prompts/2026-09-30_pkgf_pop_lm02_ruling/ (8b49a4456)

Strict gate:
- ensorain/arc3/pkgf_obs.py
- ensorain/arc3/RESULTS_PKGF_PROBE.md (section "Observability gate")
- ensorain/arc3/results/pkgf_obs.json
- precommit 5a9d58345, result fe6393297

LM02:
- ensorain/arc3/lm02/{assay.py, score.py, PREREG_LM02_ASSAY.md} (precommit 8b49a4456)
- ensorain/arc3/lm02/RESULTS_LM02_ASSAY.md
- results/lm02_assay.json, results/lm02_verdict.json (bf90a73bb)

Freeze: ensorain/arc3/INSTRUMENT_LINE_FREEZE_2026-09-30.md (fd582afb2)

Parked: ensorain/arc3/packages/PKG_LM02_DESIGN.md (v0.2 research design)

+==============================================================================+
|  END OF PACKET. Reviewer: "not worth continuing" and "the criteria were      |
|  rigged" are both first-class answers. Say which, and why.                    |
+==============================================================================+
