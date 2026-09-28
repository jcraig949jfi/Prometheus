# PREREG_WTP_LM01 -- Lossless Memorizer Challenge (v0.3.2)

Seat: Ensorain[m2-32b65655], M2.

STATUS: DRAFT v0.3.2 (the freeze commit changes this word to FROZEN). It supersedes v0.3.1 (freeze 768ea8ce9) BEFORE
any campaign row, by operator amendment 2026-09-28. Pre-freeze review: ensorain/arc3/reviews/LM01_V032_PREFREEZE_REVIEW.md
(required fixes R1-R4 applied; diff rows 17-25).
- The freeze commit is the commit that introduced this line. Its full SHA and the hash of every frozen file are in
  ensorain/lm01/FREEZE.json, committed right after.
- Per-stratum numbers: PREREG_WTP_LM01_TABLES.md (generated, frozen with this file).
- Every change from v0.3.1 is listed in ensorain/LM01_DIFF_v031_to_v032.md, with its reason.
- v0.3.1, the independent pre-result review, and the pre-data adjudication addendum are preserved unchanged as the audit
  trail (ensorain/lm01/archive_v031/; ensorain/arc3/reviews/; ensorain/arc3/LM01_ADJUDICATION_ADDENDUM.md).
- No campaign seed has ever been derived.

Authority and provenance:
- Directive: roles/Ensorain/prompts/2026-09-25_wtp_lm01_directive/ (Cyclops; sha256 ab204631...).
- Operator rulings: roles/Ensorain/prompts/2026-09-26_lm01_operator_rulings/ (DELTA .30, D9, F5 scale, endpoints, D11
  deferred, operator-only launch).
- Amendment: roles/Ensorain/prompts/2026-09-28_lm01_v032_amend/.
- Design record: ensorain/lm01/STEWARD_RULINGS.md.

## 1. Claim under test

The candidate law is s1 of the program directive (frozen text held by Harmonia). LM01 tests its PERSISTENT-STATE reading:
- A system that keeps its admitted experience exactly in persistent state does not reach the held-out / fresh-field
  competence of systems whose persistent state is a bounded, coarse-grained representation, under honestly accounted
  resources.
- A contraction done transiently at readout and then discarded (L-R) is not persistent contraction. An L-R win is
  labelled LOSSLESS_TRANSIENT_CONTRACTION (LTC). SCOPE, narrowed pre-freeze (review R2):
  - LTC means "exact retention + a transient rank-3 refit beats a RANDOM-SUBSAMPLE exact-record reservoir with the same
    fixed factor model";
  - it does NOT damage the persistent-state reading in general: a per-cell (sum, count) sufficient-statistic table,
    bounded by the cell count, reproduces L-R's fit exactly by a weighted-least-squares identity (s11; reported as
    SUFFSTAT, s6.1);
  - it says nothing either way about a computation-inclusive law.
- "Accessible" means operationally accessible to the acting system within its per-query budget; tested by index
  ablation (6.4).
- WHETHER SELECTIVITY ITSELF IS CAUSALLY REQUIRED REMAINS UNTESTED in LM01 (operator 2026-09-26 item 5; D11).
- LM01 records three COMPRESSION LOCI separately for every arm (s5):
  - stored exact records;
  - persistent learned (hypothesis) state;
  - query/readout computation (incl. L-R's transient per-query fit).

## 2. Worlds (unchanged from v0.3.1)

- WTP generators; LATENT_GENS = (lowrank, cp, tt, pairwise, spectral, sum), FROZEN.
- Families:
  - F1 episodic: branch trigger, UNTESTED for the headline;
  - F2 latent;
  - F3 switch: 3 episodes; scored on the last;
  - F4 fresh-field transfer: w = .6;
  - F5 nuisance mode: nuis_p .5; nuis_p 1 is a declared control, never in the headline.
- Levels: L1 8^3, L2 12^3, L3 16^3. life_mult 4. Noise SD .1. Exposure: a tensor-index walk with no carrier learner.
- STRATUM = family x level x generator (75). Verdicts are per stratum. The pooled verdict is secondary. A split reads
  GENERATOR_DEPENDENT.
- F5 capacity scale: "real_cells" (the nuisance mode is excluded from c), for the reservoir AND, from v0.3.2, for the
  SELECTIVE ladder. The "all_cells" interpretation is documented and does not govern.
- Full-coverage cells (L1-F2: all 6 strata EMPTY) go to a "LOSSLESS = table" regime table, never the headline.

## 3. Test sets (unchanged)

- The headline: never-seen (F1-F3), fresh-field (F4), OOD never-seen (F5) cells, at coverage < 1.
- Exact-hit cells are reported separately.

## 4. Arms (ensorain/lm01/arms.py)

- LOSSLESS: exact append-only store.
  - Readouts:
    - L-K: unlearned min-Hamming kernel;
    - L-R: converged ridge ALS refit on the FULL store per query, discarded after;
    - -rec variants use recency from the stored steps.
  - Cheat fixtures FLAG a kept fit and a subsample (R1c/R1d) on L-R, L-R-rec, H-rec. The record-read counter is separate
    from timestamp reads (D8).
- SELECTIVE-proper: WTP online substrates. The capacity ladder starts at cells/16 x 2^k (real cells for F5) and runs up
  to the frozen LOSSLESS arm's bytes. It needs no recency variant.
- HYBRID: exact store + an online-SGD low-rank key (k-NN in key space); H-rec.
- RESERVOIR-REFIT (BufferALS): bounded rank-3 factors + B exact records.
  - Warm ALS refit every >= 64 admissions, plus an END-OF-LIFE REFIT before any prediction (v0.3.2).
  - Eviction policies:
    - random (the reference);
    - FIFO (v0.3.2 RECENCY reference: the most recent B records), at the two eviction points;
    - the frozen per-stratum candidate, one of the 2 declared SURPRISE-DRIVEN heuristics: keep_worst (keep the records
      the current factors predict worst) or residual_reservoir (residual-weighted reservoir).
  - Neither candidate uses relevance, and results are labelled as heuristic results (6.3).
- ALS: one convergence rule (rel 1e-4, max 80) for every ALS fit; iterations and cap-hit fraction are reported.
- Arm formation: dev-only selection v2, frozen in FROZEN_SELECTION.json (sha256 0091e599...), unchanged.

## 5. Measurement

- AC = -log10(MSE/V0), V0 = 1, clipped [-3, 6].
- RESOURCES are measured per arm: persistent (peak), written, record_reads, state reads, store-record reads, ops,
  query_ops, replay ops, wall.
  - COMMON READ CONVENTION (v0.3.2): record_reads = admitted records touched x (2D + 8) bytes x passes/iterations, the
    same for every arm:
    - SGD: batch records x passes;
    - ALS: records x 2 half-sweeps x iterations used;
    - kernel/kNN readouts: records scanned per query.
  - QUERY CONVENTION: Q = 1 evaluation of the full headline test set per life. L-R pays one full-store refit per query.
    query_ops = ops inside predict(); fit ops = ops - query_ops.
- COMPRESSION LOCI per arm (v0.3.2):
  - stored_record_bytes: exact records kept;
  - hypothesis_bytes: persistent learned or summary state;
  - transient_hypothesis_bytes: state built at query time and discarded (L-R's fit).
  - query_ops.
- Recoverability: HR2 is the matched quantity for 6.3(ii). The RESERVOIR's reconstruction map is MEMORY-BASED (the
  buffered exact record at the cell where retained, else the factor readout). HR2_signal, R(tau) and distinctness are
  reported.
- The RandomMerge IM-rate/IM-bytes arms and the K = 5 relative selectivity reading are INSTRUMENT CALIBRATION (fixtures;
  s7). They are not campaign measurements (corrected in v0.3.2).
- Relevance comes from the generator only.

## 6. Decision rule and readings (implemented in ensorain/lm01/analysis.py v0.3.2; every gate is in that file)

6.0 GOVERNING TOLERANCE DELTA = 0.30 AC.
- Per-world PAIRED differences with a 90% t-interval.
  - EQUIVALENT: the CI lies inside (-.30, +.30).
  - WIN: the CI lies entirely beyond +.30.
  - Otherwise UNRESOLVED.
- No margin from an arm's own instability.
- SENSITIVITY at .15 / .60 is descriptive only and uses each delta's own dev frame.
- TESTABLE per stratum (dev; unchanged): ELIGIBLE (N_MIN scan up to the stratum's test size, bootstrap half-width
  <= .15) AND LEARNABLE (the CI lower bound of the best frozen arm's gain over N1 > .30).
6.1 HEADLINE: the same-optimizer RESERVOIR curve, random eviction, rank 3, B in {c/8, c/4, c/2, c, 2c, full}.
- ENDPOINTS, both reported: (a) L-R, the declared endpoint (noisier; local minima); (b) the warm full-store reservoir.
- G1 HEADLINE-PAIR LEARNABILITY (v0.3.2): 6.1 is read only if CI.lo(L-R - N1) > .30 on the campaign rows. Otherwise
  UNTESTED_HEADLINE_NOT_LEARNABLE.
- EXACT_RETENTION_PAYS: L-R WINS over EVERY genuinely BOUNDED rung, B <= c (c/8, c/4, c/2, c), AND each of those rungs
  is itself above the N1 floor (CI.lo(rung - N1) > 0; review R1, the same floor as the sufficiency readings).
  - This is v0.3.2 diff #16/#17. Under v0.3.1 the set included 2c (37-73% of the history), and the headline positive
    control could not fire.
  - DEV PROJECTION, disclosed (review R3; committed dev rows, v0.3.1 reservoir without the end-of-life refit): 4 of the
    9 G1-learnable dev strata change from UNRESOLVED to LTC under the v0.3.2 rule (F2-L3-spectral, F5-L3 cp / tt /
    spectral). Their bounded rungs are above N1, so the differences are real. No other dev label changes.
  - The v0.3.1-set label is reported as a DESCRIPTIVE column (v031_set_label).
  - 2c is still measured and reported.
- SUFFSTAT (reported only, never in a verdict): the per-cell sufficient-statistic table refit by the same count-weighted
  ALS. suffstat_minus_LR is reported beside the endpoints.
  - With L-K EQUIVALENT to L-R -> COUNTERMODEL_SIGNAL (F-B).
  - Otherwise -> LOSSLESS_TRANSIENT_CONTRACTION.
- HEADLINE POSITIVE CONTROL (v0.3.2; dev/fixtures_v032.json): planted noisy rank<=3 worlds per level. If it does not
  fire EXACT_RETENTION_PAYS at a level, a non-firing headline at that level reads UNRESOLVED_INSTRUMENT_CANNOT_FIRE.
  Per-level status: s7.
- BOUNDED_SUFFICES (reported, no verdict weight): B* = the smallest rung from which ALL larger rungs are EQUIVALENT to
  L-R and above the N1 floor (monotone). B* against the warm endpoint is also reported.
- Otherwise UNRESOLVED.
6.2 SECONDARY, optimizer confounded (SGD vs ALS); it never gates a falsifier.
- ELIGIBLE ladder point: persistent bytes <= LOSSLESS AND record_reads <= LOSSLESS (the common convention), in the
  majority of worlds.
- SELECTIVE_ADVANTAGE: an eligible point WINS over the frozen LOSSLESS.
- Secondary COUNTERMODEL: the frozen LOSSLESS WINS over EVERY eligible point (an L-R choice is labelled
  LOSSLESS_TRANSIENT_CONTRACTION).
6.3 EVICTION at B = c/4 and c; each point is its own reading.
- E6 on the CAMPAIGN rows: CI.lo(oracle - random) > .30. Else EVERY 6.3 label is UNRESOLVED_E6.
- HEADROOM: CI.lo(random@full - random@B) > .30. Else UNTESTED_NO_HEADROOM.
- Comparisons: (i) candidate - random at matched B; (ii) candidate - random at matched memory-based HR2 (3 seeds; bytes
  charged; UNMATCHED if the interpolation clamps at the full store in most worlds); (f) candidate - FIFO.
- Labels:
  - RECENCY: WIN(i) but not WIN(f).
  - HEURISTIC_ADVANTAGE: WIN(i), WIN(ii), WIN(f).
  - HEURISTIC_BUYS_BYTES: WIN(i) and WIN(f), not WIN(ii).
  - RANDOM_BEATS_HEURISTIC: random WINS at (i), unless the loss is attributable to recency.
  - RECENCY_LOSES: random WINS over the heuristic AND over FIFO, and the heuristic is EQUIVALENT to FIFO. This is
    symmetric recency attribution (pre-freeze review), and it is not a falsifier.
  - HEURISTIC_EQUIVALENT_TO_RANDOM: EQUIVALENT at (i) and (ii).
  - UNRESOLVED otherwise.
6.4 HYBRID ACCESS:
- HYBRID_REQUIRED: the index-ablation gap WINS.
- INDEX_NOT_REQUIRED: the gap is EQUIVALENT to 0 AND the ablation positive control passes.
- Else UNRESOLVED.
6.5 INTERVENTION: DEFERRED (D11); intervention.py is NOT USED.
6.6 AGGREGATION:
- GENERATOR_DEPENDENT: computed for every reading type, over LIVE readings only. Gate outcomes (UNTESTED_*,
  UNRESOLVED_E6, UNRESOLVED_INSTRUMENT_CANNOT_FIRE, UNRESOLVED_UNMATCHED) are not verdicts.
- CROSSOVER: the headline switches with level within a generator (live readings only).
- The multiplicity denominators count LIVE readings only.
- GATES THAT READ CAMPAIGN ROWS, disclosed: G1 (headline-pair learnability), E6, and headroom use the campaign rows of
  the stratum. They are control and learnability gates on quantities other than the reading's own contrast. The v0.3.1
  statement "no campaign world decides eligibility" applies to the dev TESTABLE frame only.
- NULL: the headline pair is learnable, the headline positive control passes at the level, and EVERY rung is EQUIVALENT
  to L-R.
- INSTRUMENT_FAILURE: a calibration check fails (e.g. the F1 trigger).
- UNTESTED and UNREPLICATED as defined.
- The campaign-vs-dev E6 disagreement is reported.
6.7 FALSIFIERS (written before data; per stratum; each on its own; none conjoins an absence):
- F-B (lossless): COUNTERMODEL_SIGNAL (6.1).
- An L-R-only result is LOSSLESS_TRANSIENT_CONTRACTION. It is not a falsifier. Its scope: a random-subsample reservoir
  is a poor bounded state. It does not show that exact retention is necessary (the SUFFSTAT identity).
- F-C (surprise-driven retention): HEURISTIC_EQUIVALENT_TO_RANDOM or RANDOM_BEATS_HEURISTIC (6.3). SCOPE: whether the
  two declared surprise-driven eviction heuristics beat random retention of exact records with the factor model fixed.
  It is not a test of relevance-selective contraction.
- Neither an unfired F-B nor an unfired F-C is support for the law.
- REPLICATION (symmetric for falsifiers and supports):
  - N_REP per reading, from THAT reading's paired SD on the campaign rows: win readings one-sided 80% power at
    2 x DELTA; equivalence readings TOST 80% power.
  - Floor 8, cap 64. Above the cap: UNREPLICATED.
  - Each firing/support carries PENDING_REPLICATION(n) until the held-out block (s9) is run.
- MULTIPLICITY: per label, the readings tested and the expected chance firings (.05 each).
6.8 CURVES (v0.3.2): per stratum, ALWAYS emitted, including UNTESTED strata.
- Rung AC CIs, B as a fraction of history, HR2, the three loci, record_reads, query/fit ops.
- They are the primary descriptive object where a verdict is unresolved.

## 7. Controls and fixtures (status at freeze; rerun under v0.3.2 code)

Rerun under v0.3.2 code (log: ensorain/lm01/dev/FIXTURE_RERUN_v032.json, 2026-09-28T09:10Z):
- ensorain/lm01/tests: 56 passed. This includes the R1c/R1d cheat fixtures on L-R, L-R-rec and H-rec (FLAGGED) and the
  known-answer tests for every v0.3.2 gate and label path.
- Instrument trio (relative selectivity reading): PASS at 0.8 / 1.6 / 2.9 visits/cell.
- Reservoir curve fixture: monotone; full store 2.65 vs converged L-R 2.62. PASS.
- Eviction positive control (oracle beats random at matched B): PASS, gap +.63. It was +.91 before the one-ALS-
  convergence rule (#677); the change is from that rule, not v0.3.2.
- R1e ablation positive control (oracle-key HYBRID): PASS, gap 1.23.
- HEADLINE POSITIVE CONTROL (dev/fixtures_v032.json; planted rank<=3 worlds, dev seeds 9_890_000-007):
  - The first run at noise SD 1.0 was DEGENERATE (the bounded rungs sat below N1, so the control "fired" against broken
    arms; review R1).
  - Rerun at the declared SD 0.3 under the floor rule: L2 PASS and L3 PASS, NON-DEGENERATE: every bounded rung is above N1 (L2 rungs .16-1.04 vs N1 -.02; L3 .23-1.17 vs
    -.02), and L-R WINS over c/8..c (L2 CI.lo 1.53/1.39/1.17/.73; L3 1.46/1.28/.92/.52). L1 FAILS (only 2 of 8 dev
    worlds have enough never-seen cells). A level that fails reads
    UNRESOLVED_INSTRUMENT_CANNOT_FIRE for a non-firing headline.
- Launch-gate negative controls: rejected (tests), including the operator's amendment text with its
  "<NEW_V0.3.2_HASH>" placeholder and the v0.3.1 hash.
- Per-stratum E6 is evaluated on the campaign rows (6.3).

## 8. Derived quantities: PREREG_WTP_LM01_TABLES.md (unchanged dev frame; generated from dev/margins_reduced_v2.json)

## 9. Seeds and LAUNCH GATE (operator 2026-09-26 item 6; unchanged mechanism)

- OPERATOR ONLY, in direct chat.
- The instruction "LAUNCH WTP-LM01 using frozen prereg <hash>", recorded verbatim with a MANIFEST, must carry a hex
  prefix (7-40) of the v0.3.2 FREEZE COMMIT. Any other hash, including v0.3.1's, is rejected.
- CAMPAIGN seeds: 10^9 + (sha256(FREEZE|LM01-campaign|stratum|i) mod 4e8).
- REPLICATION seeds: 2 x 10^9 + (... LM01-replication ... mod 4e8). Disjoint by construction.

## 10. Campaign size, runtime, concurrency

- 41 TESTABLE strata x 48 worlds = 1,968 worlds.
- v0.3.2 adds the FIFO reference (2 fits per world) and end-of-life refits: estimated +10-15% over v0.3.1's ~9 h, so
  ~10 h at 8 workers.
- 8 workers, BELOW_NORMAL, 6 GB RAM stop, the shared cpu8 lease taken at actual launch.
- M2 must be free of other heavy jobs (process census).

## 11. Limitations (written before data)

- Finite horizon; synthetic generators; generator-conditional.
- The secondary is optimizer-confounded.
- v1 selection was seen before two redesigns.
- The F5-lowrank split-rule artefact.
- The reservoir is recency-blind (F3; FIFO is now the reference, not a readout).
- L-R has seed local minima; S-cp is bimodal.
- F-B strict has near-zero power in latent families.
- EXACT_RETENTION_PAYS power per level is as the headline positive control shows (s7). It is judged against rungs
  <= c. The 2c comparison is reported but cannot carry a verdict: no dev stratum, and not even the planted control, had
  CI.lo(L-R - 2c) > .30.
- SUFFICIENT-STATISTIC IDENTITY (review R2): L-R's count-weighted ridge-ALS objective equals, up to a constant, the
  objective on per-cell means. A bounded (sum, count) table (<= c cells) therefore reproduces the L-R endpoint's fit
  exactly (review probe p_suffstat.py: AC within .007 at ~1/3 of the bytes).
  - Any LTC or COUNTERMODEL result is therefore a statement about the RANDOM-RECORD reservoir as the bounded comparator.
  - It is not evidence that exact records are needed. LM02 carries the sufficient-statistic arm.
- The secondary (6.2) is confounded by optimizer, model class, regularization and tuning point.
- In the 4 strata whose frozen LOSSLESS is L-K, no SELECTIVE ladder point is eligible under the one-query read
  convention (L-K reads each record once; any 3-pass learner reads 3n). The secondary there reads UNRESOLVED by
  construction.
- The fixed rank-3 readout means 6.1 cannot distinguish memory from readout capacity (review F11; a data-adaptive
  lossless readout belongs to LM02).
- F-C covers surprise-driven heuristics only.
- REQUIREMENT is untested.
- Low-power regions per TABLES.

## 12. Dev design findings (kept out of results): as in v0.3.1

## 13. Defect ledger

- D1-D12 as in v0.3.1.
- D13 (v0.3.2): the independent pre-result review findings F1-F15, repaired or declared per
  ensorain/LM01_DIFF_v031_to_v032.md.
- D14 (v0.3.2 pre-freeze review): R1-R4 plus the recommended items (diff rows 17-25).

## 14. Checklist self-check

- As in v0.3.1.
- Additionally:
  - A4 (a no-difference verdict needs a positive control): now satisfied for the headline by the headline positive
    control;
  - B9/C4/C5/D1/D2: amended per the diff;
  - E6: computed on the campaign rows.
