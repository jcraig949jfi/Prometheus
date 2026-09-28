# LM01 adjudication addendum (PRE-DATA; committed before any campaign row exists)

Status: written 2026-09-28 after the independent pre-result review (ensorain/arc3/reviews/LM01_ADVERSARIAL_REVIEW.md,
15 findings), BEFORE LM01 has launched.
- The frozen prereg v0.3.1 (768ea8ce9) and its analysis.py stay UNCHANGED and are run exactly as frozen (operator
  ARC3 ruling: "Run LM01 as frozen at v0.3.1").
- This addendum defines ADJUDICATION readings reported BESIDE the frozen verdicts, never replacing them. Every frozen
  label is still printed.
- Where this addendum and a frozen label differ, both appear, with the reason. Nothing here uses campaign data to
  choose a rule.

## A. Response to the review (every finding; spot-checks by Ensorain marked [checked])

| finding | severity | accepted? | handling |
|---|---|---|---|
| F1 arm differences beyond B (cold vs warm path, stale factors of evicted rows, unfitted tail) | S2 | yes | addendum G1 caveat; LM02 end-of-life refit + cold-refit-on-rung control |
| F2 SELECTIVE vs LOSSLESS differ in optimizer/model | S2 | yes (already declared "optimizer confounded") | none |
| F3 HYBRID / eviction details | S3 | yes | none |
| F4 headline pair not learnable in 29/38 strata | S1 | yes | gate G1 |
| F5 EXACT_RETENTION_PAYS ~0 power (2c = 37-73% of history) | S1 | yes | G2 statement + curve-shape reading (LM01_CURVE_ANALYSIS_PLAN) as the informative object; LM02 headline redesign |
| F6 read accounting excludes SELECTIVE in 6.2 | S1 | yes [checked arms.py:223 vs :98/:152] | G3 |
| F7 keep_worst is a recency buffer; residual policies are surprise heuristics | S1 | yes | G4 relabel; LM02 recency reference |
| F8 F-C@c equivalence from saturation (no headroom) | S1 | yes | gate G5 |
| F9 N_REP from the wrong variance / not TOST | S2 | yes | G6 |
| F10 matched-HR2 on an outcome-correlated quantity | S2 | yes | G7 |
| F11 lossless endpoint is a fixed rank-3 contraction | S2 | yes | G2 caveat; LM02 data-adaptive lossless readout |
| F12 F5 SELECTIVE ladder cells include the nuisance mode; F1 max-over-caps | S3 | yes | G8 |
| F13 "bounded" misnomer at upper rungs | S2 | yes | curve plan reports B as a fraction of history + bytes ratios |
| F14 compute measured, unused; one query | S2 | yes | curve plan (trade surface); LM02 declared query count |
| F15 code-vs-prose inconsistencies (a-i) | S1 (b) / S2-S3 | yes [checked F15b: analysis.py:106 vs prereg line 174] | G9 |

## B. Adjudication rules (fixed now)

- G1 HEADLINE-PAIR LEARNABILITY (F4):
  - Before any 6.1 reading, require CI.lo(L-R - N1) > DELTA on the CAMPAIGN rows of the stratum; and for any
    equivalence reading (B*, BOUNDED_SUFFICES, NULL), also CI.lo(rung - N1) > 0.
  - Otherwise the adjudicated 6.1 reading is UNTESTED (headline pair not learnable), whatever the frozen label says.
  - Dev expectation (from the review): only ~9 of 38 headline strata pass.
- G2 HEADLINE POWER STATEMENT (F5, F11): EXACT_RETENTION_PAYS (both forms) is recorded in advance as ~0-power in every
  stratum.
  - No dev stratum has CI.lo(L-R - 2c) > .30.
  - Its non-firing is NOT evidence for compression. The informative 6.1 output is the curve shape (plan s1), read on
    G1-passing strata only.
  - Any L-R vs 2c difference is read as a statement about a rank-3 contraction, not about exact retention.
- G3 SECONDARY READ CONVENTION (F6): the adjudicated 6.2 drops the reads filter and uses persistent bytes only (as the
  6.2 COUNTERMODEL prose states). It reports the Pareto front over (bytes, AC) with query ops beside it. The frozen 6.2
  label is printed, marked "read-accounting convention asymmetric".
- G4 EVICTION RELABEL (F7): every 6.3 reading involving keep_worst or residual_reservoir is adjudicated as a statement
  about a SURPRISE/RECENCY HEURISTIC, not about relevance-selective retention.
  - SELECTIVE_BUYS_BYTES and RESERVOIR_SELECTIVE_ADVANTAGE become "HEURISTIC_BEATS_RANDOM".
  - RANDOM_BEATS_SELECTIVE becomes "RANDOM_BEATS_HEURISTIC".
  - F-C firings are adjudicated as "F-C (heuristic scope)". They damage the law only to the extent the heuristic is
    what a selective learner would do. This is stated, not assumed.
  - For each such reading, the buffer's recency is reported: the fraction of the buffer from the last quarter of the
    stream, computed from the stored rows where available, else flagged as unmeasured.
- G5 HEADROOM (F8): an eviction reading at point B is adjudicated only if CI.lo(warm full - random@B) > DELTA on the
  campaign rows. Otherwise it is UNTESTED (no headroom).
- G6 REPLICATION SIZING (F9): for any firing, N_REP is recomputed from THAT reading's own dev paired SD.
  - Win readings: one-sided power 80% at 2 x DELTA.
  - Equivalence readings: a TOST sample-size formula at 80% power with a true difference of 0.
  - Capped at 64; UNREPLICATED above. The frozen N_REP is printed beside it.
- G7 MATCHED-HR2 (F10): (ii) readings whose interpolation clamps at the ladder end are UNMATCHED. (ii) is otherwise
  reported with the caveat that HR2 here is the factor readout's in-sample fit.
- G8 (F12): F1 lossless_must_win is re-read against the per-stratum FIXED cap (the frozen SELECTIVE cap, cells // 4),
  not the per-world max. The F5 SELECTIVE ladder's nuisance-inclusive scale is noted.
- G9 PROSE GOVERNS WHERE CODE CONTRADICTS IT (F15):
  - b: every 6.3 label is adjudicated UNRESOLVED where E6 fails (prose s7).
  - c: 6.2 COUNTERMODEL is bytes-only.
  - g: falsifier firings are "pending replication", as supports are.
  - d: CROSSOVER / INSTRUMENT_FAILURE / UNREPLICATED are computed in the adjudication script per the prose definitions.
  - e: the RandomMerge/selectivity readouts are ABSENT from the campaign rows; recorded as not measured, and the
    prereg s4/s5 mention is a documentation defect.
  - f: sensitivity frames use each delta's own dev frame (TABLES).
  - h: B* is the smallest rung from which ALL larger rungs are EQUIVALENT (monotone definition).
  - i: campaign-vs-dev E6 disagreement is reported.

## C. What the review changes about LM01's scientific value

- LM01's frozen verdicts will largely be UNRESOLVED/UNTESTED by construction. That was already true of F-B strict, and
  the review shows it holds for the whole 6.1 WIN rule.
- The value of the run is its per-world measurements: reservoir curves, the endpoints, meters, E6 and ablation, on 1,968
  worlds. The descriptive curve analysis (plan) and G1-G9 read those.
- The successor LM02 (thread T24) carries the measurement additions the review asks for.

## D. Adjudication script

ensorain/arc3/lm01_adjudicate.py implements G1-G9 on campaign rows. It is to be written and tested on synthetic rows and
dev rows BEFORE the campaign rows exist, then committed.
