# WTP-LM01 v0.3.2 DRAFT: pre-freeze adversarial review

Reviewer: the same independent reviewer who wrote LM01_ADVERSARIAL_REVIEW.md (findings F1-F15), 2026-09-28.
Target: D:\Prometheus-worktrees\ensorain-base-role at commit 426337ce6 (read-only; nothing modified).
No campaign seed was derived and launch.py was not run. Probes used dev seeds 9_700_030..9_700_032 and the committed dev
rows / dev fixture rows (a few CPU-minutes). Probe scripts are next to this file (v032_proj.py, p_suffstat.py).
The analysis known-answer tests pass (15/15, test_lm01_analysis.py, run with -p no:cacheprovider).

RECOMMENDATION: FREEZE AFTER LISTED FIXES (section E). Four of the fixes are required before freeze: R1, R2, R3, R4.
None of them adds a world, an arm or a campaign measurement.

---

## A. Status of F1-F15 (code checked, not only prose)

| F | v0.3.2 status | Correct in code? | Note |
|---|---|---|---|
| F1 tail / warm-cold path | PARTLY FIXED | yes, finalize() is called on every BufferALS (campaign.py ladder, dual, posctl; fixtures_v032.py) | The unfitted tail is fixed. The warm-vs-cold path and the ~20x compute difference between the endpoints are only recorded (loci, query_ops). There is no decomposition control and no limitation sentence. Acceptable if declared (R7). |
| F2 secondary confound breadth | UNADDRESSED | - | 6.2 is still labelled only "optimizer confounded (SGD vs ALS)". This now matters, because 6.2 has become LIVE (F6 fix) and SELECTIVE_ADVANTAGE is a support label. See N7. |
| F3 | n/a | - | - |
| F4 headline-pair learnability | FIXED | yes (analysis.py:96-99) | G1 is evaluated on campaign rows, not dev; see N8. Dev projection: 30 of 38 headline strata become UNTESTED_HEADLINE_NOT_LEARNABLE. |
| F5 headline power | CHANGED (diff #16 + HPC) | the code does what the diff says | The positive control that justifies #16 is degenerate (N1). #16 turns ~0 projected firings into ~4 (N3). Scope of LTC (N2). |
| F6 read accounting | FIXED | yes (record_reads in arms.py; analysis.py:143-144) | 6.2 is now eligible wherever LOSSLESS is L-R (2 x iters >= 3 passes). The 4 strata whose frozen LOSSLESS is L-K / L-K-rec stay permanently ineligible under the Q = 1 convention (N7). |
| F7 keep_worst = recency | FIXED (support side only) | FIFO ring buffer correct (arms.py, j = (seen-1) % B overwrites the oldest) | Recency attribution is asymmetric: it can withhold support but never withholds a falsifier (N5). |
| F8 headroom | FIXED | yes (analysis.py:185-186) | - |
| F9 N_REP | FIXED | yes; the TOST constant z.95 + z.90 is correct for a true difference of 0 | Normal approximation; t at n ~ 8-12 makes it slightly optimistic. S3. |
| F10 matched HR2 | FIXED | memory-based _reconstruct; upper clamp flagged | The lower-end clamp is not flagged. "most recent buffered value" is really slot order (N10). |
| F11 fixed rank-3 readout | DECLARED (s11, LM02) | - | Acceptable, but see N2: a bounded state that equals L-R exists inside the design. |
| F12 F5 scale / F1 max | FIXED | yes | - |
| F13 capacity reporting | FIXED | curves() emits B_frac and loci | loci for BufferALS omit bkey (8 B/record), which peak_persistent counts. S3. |
| F14 compute | PARTLY | query_ops and loci are recorded; Q = 1 is declared | No verdict uses compute. s1 still says "honestly accounted resources". Declare this (R7). |
| F15a NULL control | FIXED | NULL now needs HPC (analysis.py:254-255) | - |
| F15b E6 on every 6.3 label | FIXED | yes (analysis.py:183-184) | E6 moved to campaign rows (N8). |
| F15c secondary eligibility | FIXED | the same eligibility is used for both labels | - |
| F15d CROSSOVER etc. | IMPLEMENTED | yes | Aggregation counts gating labels as splits (N6). |
| F15e prose readouts | FIXED (prose) | - | - |
| F15f sensitivity frame | FIXED | yes (analysis.py:284-286) | The HPC is only computed at .30 and is reused at .15 / .60. S3. |
| F15g replication markers | FIXED | yes | - |
| F15h B* monotone | FIXED | yes (analysis.py:107-111) | - |
| F15i campaign vs dev E6 | FIXED (reported) | e6_disagreement | - |

## B. Diff row #16: repair or tilt?

Verdict: the CHANGE is a legitimate definitional repair. Its STATED JUSTIFICATION is unsound, and its CONSEQUENCE is
material and undisclosed. It can freeze only with R1-R3.

1. The design argument is sound, and it predates the fixture. In v0.3.1, 2c held 37 / 54 / 73% of the history as exact
   records. It is not a "bounded, coarse-grained" state in the sense of s1. My F5 recommended judging the win against
   rungs <= c on these design grounds. (The code comment "at most one record per cell" is inaccurate: a buffer of c
   records can repeat cells. Say "at most c records".)

2. The positive control cited as the reason is degenerate. It fires only because every rung <= c performs WORSE THAN THE
   CONSTANT BASELINE N1. From dev/fixtures_v032.json rows (8 worlds per level, 90% CI of rung minus N1):

   ```
   L2: c/8 -0.20 [-0.28,-0.12]  c/4 -0.53 [-0.66,-0.41]  c/2 -0.60 [-0.72,-0.48]  c -0.21 [-0.31,-0.11]
       2c +0.31 [+0.16,+0.46]   full +0.59   L-R +0.73
   L3: c/8 -0.35 [-0.42,-0.28]  c/4 -0.52 [-0.57,-0.47]  c/2 -0.47 [-0.53,-0.42]  c -0.07 [-0.24,+0.11]
       2c +0.64 [+0.59,+0.69]   full +0.78   L-R +0.83
   ```

   With noise SD 1.0 and ridge 0.1, the small-buffer rank-3 fits overfit, and the curve is non-monotone (c/2 is worst).
   The fixture shows that the WIN rule fires against BROKEN bounded arms. It does not show that it can detect retention
   paying over a FUNCTIONAL bounded arm, which is the scientific claim. The only rung in the fixture that works at all
   (2c) is exactly the one #16 removed.

3. The asymmetry that #16 creates. v0.3.2 requires rung - N1 lo > 0 ("above floor") for every EQUIVALENCE reading
   (analysis.py:103-109), but not for the WIN rule (analysis.py:113-114). So a sub-floor rung can help produce LTC, but
   cannot help produce sufficiency. This is a tilt toward the lossless label.

4. The consequence, projected with the frozen v0.3.2 headline() on the committed dev rows (v032_proj.py; L-K set to N1
   because dev rows lack L-K, so COUNTERMODEL cannot appear):
   - F2-L3-spectral, F5-L3-cp, F5-L3-tt and F5-L3-spectral change from UNRESOLVED (v0.3.1 set) to
     LOSSLESS_TRANSIENT_CONTRACTION (v0.3.2 set).
   - F2-L3 lowrank/cp/tt stay UNRESOLVED on 16 worlds. At N = 48 they could also flip (dev L-R - c = +0.25..+0.38).
   - In those 4 strata every rung <= c is above the floor. The DEV flips are real differences on functional rungs, not
     overfitting artefacts.

   The dev rows that show this were committed and quoted in my review (the LR-c column) before #16 was written. The
   diff justifies #16 only by the fixture. It must also state the dev projection, so that a reader can see the change
   was not blind to its effect (R3).

5. Direction. The headline can only fire AGAINST the law: LTC and COUNTERMODEL fire, while BOUNDED_SUFFICES carries no
   weight. #16 raises the power of that one-sided test. Under falsification-first that is acceptable, IF the label's
   meaning is scoped correctly. In v0.3.2 it is not (N2).

## C. New defects introduced or exposed by v0.3.2

N1. (S1) The headline positive control is degenerate (B.2), and the WIN rule has no floor (B.3).
   Resolve (R1):
   - add above_floor[g] to the WIN rule for each g in WIN_RUNGS (one line, symmetric with equivalence);
   - re-run the HPC fixture (calibration only, no campaign world) with a noise level at which the rungs <= c are above N1
     (for example SD 0.3-0.5, declared before the rerun);
   - if no such fixture fires, set headline_pc false and declare "retention-pays power over functional bounded rungs is
     undemonstrated". The dev projection above suggests the floor condition changes no dev label, so the cost is low.

N2. (S1, interpretation; the most likely source of a misleading frozen verdict) A BOUNDED coarse-grained persistent state
   inside the design reproduces the L-R endpoint exactly.
   - L-R's objective (sum over records of (y - u.v)^2, with ridge) equals, up to a constant, the count-weighted
     objective on per-cell means. A persistent per-cell (sum, count) table therefore gives the same ALS fit from the
     same init.
   - Probe p_suffstat.py (dev seeds; 11,200-record L3 histories):

     ```
     F2-L3-spectral  L-R AC 2.937  table AC 2.944  table 82.7 KB vs store 246.4 KB  (3758 cells <= c = 4096)
     F5-L3-tt        L-R AC 2.670  table AC 2.671  table 171.7 KB vs store 268.8 KB (7154 keys incl. nuisance)
     F2-L3-lowrank   L-R AC 1.989  table AC 1.989  max |dpred| 1e-12
     ```

   - The table is lossy with respect to the history (individual observations and order are gone). Its size is bounded
     by the cell count, not by life length.
   - So LOSSLESS_TRANSIENT_CONTRACTION ("L-R beats every random-reservoir rung <= c") shows only that a
     RANDOM-RECORD-SUBSAMPLE reservoir is a poor bounded state. The prereg's text for LTC, "damages the persistent-state
     reading", overclaims: a bounded state that ties L-R exists at about 1/3 of the bytes.
   - This predates v0.3.2. #16 makes it bite, because LTC becomes likely (B.4).
   - It is not an argument for adding an arm (the operator forbids expansion). The table is a closed-form identity
     (exact for the recency-blind L-R endpoint; not for the -rec arms).
   Resolve (R2):
   - Rescope LTC in s1, 6.1 and 6.7: "LTC: exact retention + transient refit beats a random-subsample exact-record
     reservoir with a fixed rank-3 factor model. It does NOT damage the persistent-state reading in general. A per-cell
     sufficient-statistic table (bounded by c) reproduces L-R by a weighted-least-squares identity."
   - Optionally report the table's AC in curves(). It is a deterministic function of the stored records, so it needs no
     new world.

N3. (S2) Disclosure of #16's dev consequence (B.4) is missing. Resolve (R3):
   - add the dev projection (4 strata flip) to the diff row and to s11;
   - report the v0.3.1-set label (incl. 2c) as a descriptive column beside the governing one, as for the sensitivity
     columns.

N4. (S2, procedural; blocks a clean freeze) Freeze mechanics:
   a. analysis.analyse() reads dev/fixtures_v032.json, which governs HPC, NULL and INDEX_NOT_REQUIRED. freeze.py FILES
      does not include it (only the prereg, TABLES, FROZEN_SELECTION.json, margins_reduced_v2.json and *.py). A changed
      fixture file would therefore pass verify(). Worse, if the file is missing, analyse() silently uses {}:
      - every non-firing headline becomes UNRESOLVED_INSTRUMENT_CANNOT_FIRE;
      - NULL is impossible;
      - INDEX_NOT_REQUIRED is impossible.
   b. The draft prereg at 426337ce6 already says "STATUS: FROZEN v0.3.2 ... The freeze commit is the commit that
      introduced this line". By that definition the draft under review is the freeze commit.
   c. FREEZE.json still records v0.3.1 (768ea8ce9) with v0.3.1 hashes. Harmless now (verify fails), but it must be
      regenerated.
   Resolve (R4):
   - mark the draft status as DRAFT, and flip it in the freeze commit;
   - add dev/fixtures_v032.json and dev/FIXTURE_RERUN_v032.json to FILES;
   - make analyse() raise if the fixtures file is absent;
   - regenerate FREEZE.json.

N5. (S2) Recency attribution applies to one side only.
   - RECENCY (WIN over random, but not over FIFO) withholds the SUPPORT label HEURISTIC_ADVANTAGE.
   - RANDOM_BEATS_HEURISTIC (F-C) is never checked against FIFO. So a keep_worst loss caused by its recency behaviour in
     a stationary world still fires a falsifier, while a keep_worst gain caused by recency is discounted.
   Resolve (R5), either way is defensible if stated:
   - apply FIFO attribution to both directions: RECENCY_LOSS when FIFO also loses to random and the candidate is
     EQUIVALENT to FIFO; or
   - drop the FIFO filter from support and only report (f).

N6. (S2) Aggregation treats gating labels as verdicts.
   - GENERATOR_DEPENDENT (analysis.py:313-314) and CROSSOVER (315-319) compare raw label strings, including
     UNTESTED_HEADLINE_NOT_LEARNABLE, UNRESOLVED_E6, UNTESTED_NO_HEADROOM and UNRESOLVED_INSTRUMENT_CANNOT_FIRE.
   - Dev projection: F2|L3 headline = {UNRESOLVED, UNTESTED_HEADLINE_NOT_LEARNABLE, LTC}, which reads
     GENERATOR_DEPENDENT partly because of gating.
   - Multiplicity denominators (analysis.py:290-301) count gated-out strata and points as "readings". For the headline:
     38 instead of ~8 live readings, so expected_by_chance is 1.9 instead of ~0.4, which makes real firings look like
     chance.
   Resolve (R6): compute aggregation and multiplicity over live readings only (labels that are a verdict or UNRESOLVED
   after all gates pass), and report the gated counts separately.

N7. (S2) 6.2 is now live, but its confound statement is too narrow, and 4 strata are structurally excluded.
   - The confounds are optimizer, regularization, model class, tuning point and reads convention (my F2), not only
     SGD vs ALS.
   - Under Q = 1, L-K / L-K-rec read n records once, while every 3-pass SELECTIVE reads 3n. SELECTIVE is therefore never
     eligible in F2-L3-pairwise, F4-L2-pairwise, F4-L3-pairwise and F5-L3-pairwise.
   - L-K actually compares every query with every record, so "records scanned per query" with Q = 1 undercounts it.
   Resolve (R7): widen the 6.2 confound label, and name those 4 strata as structurally ineligible under the declared
   query convention.

N8. (S3) Two campaign-row gates replace dev gates without a diff row saying so.
   - v0.3.1's "No reading uses a campaign world to decide eligibility" was removed.
   - G1 conditions on L-R, which is one side of the gated comparison.
   - E6 on 48 campaign worlds will pass in more strata than dev's 10.
   The selection effect is small at N = 48, and the dev projection of G1 matches. Resolve: either compute G1 from the
   dev rows (they exist), or add a diff row and a sentence acknowledging campaign-row gating.

N9. (S3) Two label changes are not in the diff table:
   - INDEX_NOT_REQUIRED (6.4; it makes explicit an implicit v0.3.1 outcome);
   - UNRESOLVED_UNMATCHED (in code, not in prose 6.3).
   Resolve: add both to the diff.

N10. (S3) Small items:
   - the lower-end HR2 interpolation clamp (target below random's minimum gives c/8) is not flagged UNMATCHED;
   - _reconstruct says "most recent buffered value", but the dict is filled in buffer-slot order;
   - the HPC is evaluated at DELTA .30 only and reused at the .15 / .60 sensitivity labels;
   - BufferALS loci omit bkey bytes.

## D. What could make a frozen v0.3.2 verdict misleading (ranked)

1. An LTC firing reported as "damages the persistent-state reading" when a bounded table ties L-R (N2). Likely: 4 dev
   strata project to LTC.
2. "HPC PASS" read as "the instrument can see retention pay", when it was shown only against sub-floor rungs (N1).
3. GENERATOR_DEPENDENT / CROSSOVER / multiplicity driven by gate labels (N6).
4. A silently missing or changed fixtures file flipping every headline to INSTRUMENT_CANNOT_FIRE (N4).
5. SELECTIVE_ADVANTAGE (a support label) read as memory evidence despite the broad 6.2 confound (N7).

## E. Fixes, in priority order

REQUIRED before freeze:
- R1 (N1): add the floor condition to the WIN rule. Re-run the HPC with a declared non-degenerate noise level, and
  record the result as it falls.
- R2 (N2): rescope LTC in s1, 6.1, 6.7 and s11 as a random-record-reservoir result. State the sufficient-statistic
  identity as a limitation.
- R3 (N3): disclose #16's dev projection; report the v0.3.1-set label descriptively.
- R4 (N4): add the fixtures file to FREEZE FILES, fail loudly if it is missing, set the status line to DRAFT until the
  freeze commit, and regenerate FREEZE.json.

RECOMMENDED (each is a line or a sentence):
- R5 (N5): symmetric recency attribution, or none.
- R6 (N6): aggregation and multiplicity over live readings only.
- R7 (F1, F14, N7): declare the warm/cold path + compute confound of the endpoints, and that verdicts ignore compute.
  Widen the 6.2 confound label and name the 4 L-K strata.
- N8-N10 as listed.

## F. What v0.3.2 does well

- Every gate now lives in analysis.py with known-answer tests. Rows #1-#15 are genuine repairs that map one-to-one to
  pre-result findings.
- None of them adds a world, a family or a campaign arm. The FIFO reference and the end-of-life refit are measurement
  repairs.
- The common read convention makes 6.2 readable where it had been dead by convention.
- The headroom gate, per-point E6, per-reading N_REP and monotone B* are correct in code.
- #16 is flagged openly as the one headline-criterion change, and the audit trail (archive_v031, the review, the
  addendum) is preserved.
