# PREREG_WTP_LM01 -- Lossless Memorizer Challenge (v0.3)

Seat: Ensorain[m2-32b65655], M2. STATUS: FROZEN v0.3. The freeze commit is the commit that introduced this line. Its
full SHA and the hash of every frozen file are recorded in ensorain/lm01/FREEZE.json, committed right after. The
per-stratum numbers are in PREREG_WTP_LM01_TABLES.md (generated; frozen with this file). No campaign row exists at the
freeze.

Authority and provenance:
- Directive: roles/Ensorain/prompts/2026-09-25_wtp_lm01_directive/ (Cyclops; sha256 ab204631...).
- Steward-era design record: ensorain/lm01/STEWARD_RULINGS.md. Everything adopted there is built into the code.
- OPERATOR RULINGS 2026-09-26: roles/Ensorain/prompts/2026-09-26_lm01_operator_rulings/ (verbatim + MANIFEST). They
  govern wherever they differ from the record.
- Operator rulings of 2026-09-26 (#732/#733): steward management via comms is frozen; no Aporia/Cyclops sign-off.

## 1. Claim under test

The candidate law is s1 of the program directive (frozen text held by Harmonia). LM01 tests its PERSISTENT-STATE reading
(#591 R1a):
- A system that keeps its admitted experience exactly in PERSISTENT STATE does not reach the held-out / fresh-field
  competence of systems whose persistent state is a bounded, coarse-grained representation, under honestly accounted
  resources.
- A contraction done transiently at readout and then discarded (L-R) is not persistent contraction. An L-R win is
  labelled LOSSLESS_TRANSIENT_CONTRACTION. It damages the persistent-state reading only and says nothing either way about
  a computation-inclusive law.
- "Accessible" means operationally accessible to the acting system within its per-query budget (#608), tested by index
  ablation (6.4).
- WHETHER SELECTIVITY ITSELF IS CAUSALLY REQUIRED REMAINS UNTESTED in LM01 (operator ruling item 5; D11).

## 2. Worlds

- WTP generators; LATENT_GENS = (lowrank, cp, tt, pairwise, spectral, sum), FROZEN.
- Families (ensorain/lm01/families.py):
  - F1 episodic: a branch trigger; UNTESTED for the headline.
  - F2 latent.
  - F3 switch: 3 episodes; scored on the last.
  - F4 fresh-field transfer: w = .6.
  - F5 nuisance mode: nuis_p = .5; nuis_p = 1 is a declared "everyone falls" control, never in the headline.
- Levels: L1 8^3, L2 12^3, L3 16^3. life_mult = 4 for all. Observation noise SD .1. Exposure is a tensor-index walk with
  no carrier learner.
- STRATUM = family x level x generator (75). Verdicts are per stratum. The pooled verdict is secondary (uniform mixture).
  A split across strata reads GENERATOR_DEPENDENT.
- F5 RESERVOIR SCALE (operator ruling item 3): GOVERNED by "real_cells". The capacity denominator c excludes the
  nuisance mode (campaign.RUNG_SCALE).
  - OLD interpretation, documented and not governing: "all_cells" counted the 4-level nuisance mode, so B = c/2 held
    ~73% of an F5 history vs ~18% elsewhere, and the E6 positive control failed for that reason
    (dev/margins/F5_* rows).
  - The repaired dev rows are dev/margins_f5real/.
- Full-coverage cells (L1-F2: all 6 strata EMPTY) go to a "LOSSLESS = table" regime table and never enter the
  headline.

## 3. Test sets

- The headline is read on never-seen (F1-F3), fresh-field (F4) and OOD never-seen (F5) cells, at coverage < 1 only.
- Exact-hit cells are reported separately.

## 4. Arms (ensorain/lm01/arms.py)

- LOSSLESS: exact append-only store (bit-recoverable).
  - Readouts: L-K (unlearned min-Hamming kernel over the full store); L-R (converged ridge ALS refit on the FULL store
    per query, discarded after); L-K-rec / L-R-rec (recency from stored steps).
  - Per-query refit charged.
  - Cheat fixtures FLAG a kept fit and a subsample on L-R and on every -rec arm (H2). The record-read counter is
    separate from timestamp reads (D8).
- SELECTIVE-proper: WTP online substrates; capacity ladder cells/16 x 2^k up to LOSSLESS bytes (INCOMPATIBLE recorded).
  It needs no recency variant (adapts online).
- HYBRID: exact store + online-SGD low-rank key (the ALS rule does not apply; B10); H-rec.
- RESERVOIR-REFIT (BufferALS): bounded rank-3 factors + a reservoir of B exact records, with warm ALS every >= 64
  admissions. It is an intermediate mechanism, named and not forced into a category.
  - Eviction: random (the reference) or the 2 DECLARED candidates keep_worst / residual_reservoir. Losing to random is a
    result.
  - Recency-blind (a limitation on F3).
- IM-rate / IM-bytes: RandomMerge bisected to HR2 (the D2/D4 readouts).
- ALS: one convergence rule (relative 1e-4, max 80) for every ALS fit. Iterations and cap-hit fraction are reported;
  cap-bound rungs are flagged as lower bounds.
- Arm formation: dev-only selection v2 (seeds 9_410_000-015), with an equal budget of 8/8/8 and 2 eviction candidates.
  - FROZEN in ensorain/lm01/FROZEN_SELECTION.json (source sha256 0091e59959cdc7ff...).
  - v2 was the last grid change; later changes are fixture-demonstrated defects only (D7, D8).

## 5. Measurement

- AC = -log10(MSE/V0), V0 = 1, clipped to [-3, 6].
- Resources MEASURED per arm: persistent (peak), written, read, store-record read, ops, replay ops, wall, external. There
  is no exchange-rate scalar; comparisons are Pareto.
- HR2 is the matched quantity (RECOVERABLE tier; never decides alone). REPORTED: HR2_signal (labelled "not a
  certificate"), R(tau), distinguishability.
- Reconstruction maps are declared (record / readout / bin mean). Selectivity is read relative to K = 5 HR2-matched blind
  references (threshold .0155; UNMATCHED means no reading).
- Relevance comes from the generator only.

## 6. Decision rule and readings

6.0 GOVERNING TOLERANCE (operator ruling item 2): DELTA = 0.30 AC (a 2x MSE ratio).
  - Noise enters only through the CI: a 90% two-sided t-interval over worlds of the PAIRED per-world difference, i.e.
    one-sided alpha .05 per direction (TOST for equivalence).
  - EQUIVALENT: the CI lies inside (-0.30, +0.30).
  - WIN: the CI lies entirely beyond +0.30 in the stated direction.
  - Anything else is UNRESOLVED.
  - No margin is derived from any arm's own instability; the v1 replicate-derived margin (#691) is RETIRED (D10).
  - SENSITIVITY at 0.15 and 0.60 AC is computed for every reading and reported beside it. It is DESCRIPTIVE ONLY and
    never changes a verdict.
  - Stability diagnostics (replicate p97.5, the fraction of worlds with |a - b| > 1 AC) are reported per arm; they
    decide nothing.
  - TESTABLE per stratum = ELIGIBLE (N_MIN: the smallest n in {16, 32, 64, 128, 256, the stratum's n_test} with 1.96 x
    bootstrap SD(n) <= 0.15; D9 extends the scan to the actual test size) AND LEARNABLE (the CI lower bound of the
    max-arm gain over N1 > 0.30, arm-symmetric).
  - Values are in the TABLES file. No reading uses a campaign world to decide eligibility.
6.1 HEADLINE: the same-optimizer RESERVOIR curve, random eviction, rank 3, B in {c/8, c/4, c/2, c, 2c, full}.
  ENDPOINTS (operator ruling item 4), BOTH reported side by side:
  - (a) L-R, the declared lossless endpoint: per-query converged refit on the full store, recency-blind in every
    stratum. It can suffer optimization / local-minimum variance (dev: seed p97.5 up to 1.11 AC); that noise stays in
    its CI.
  - (b) the warm full-store reservoir, a persistent learned-state endpoint. It is more stable but not computationally
    equivalent to L-R. It is never substituted for (a).
  Readings:
  - EXACT_RETENTION_PAYS: a WIN of L-R over EVERY bounded rung.
    - STRICT form: additionally L-K EQUIVALENT to L-R -> COUNTERMODEL_SIGNAL (F-B).
    - Otherwise -> LOSSLESS_TRANSIENT_CONTRACTION.
  - BOUNDED_SUFFICES: B* < full, with (L-R - AC(B*)) EQUIVALENT. B* is governed against endpoint (a); B* against (b) is
    also reported. REPORTED with NO verdict weight: every rung carries a fixed selective factor model.
  - Otherwise UNRESOLVED.
6.2 SECONDARY, labelled "optimizer confounded (SGD vs ALS)": SELECTIVE-proper vs LOSSLESS. It never gates a falsifier.
  - SELECTIVE_ADVANTAGE: some ladder point at <= bytes and <= reads WINS over the frozen LOSSLESS.
  - COUNTERMODEL_SIGNAL (secondary): LOSSLESS WINS over EVERY ladder point at <= LOSSLESS bytes. An L-R choice is
    labelled LOSSLESS_TRANSIENT_CONTRACTION.
6.3 EVICTION: RESERVOIR-SELECTIVE (the frozen candidate) vs RESERVOIR-RANDOM at B = c/4 and c. EACH B POINT IS ITS OWN
    READING: labels, falsifier firings and supports are named with the point (e.g. F-C@c/4). Multiplicity counts both
    points.
  - Read (i) at matched B and (ii) at matched HR2 (random B interpolated; 3 seeds; bytes charged).
  - INDISCRIMINATE_EQUIVALENT: EQUIVALENT under (i) AND (ii), plus E6 positive control PASS.
  - SELECTIVE_BUYS_BYTES: a WIN at (i) only.
  - RESERVOIR_SELECTIVE_ADVANTAGE: a WIN at (i) and (ii).
  - RANDOM_BEATS_SELECTIVE: random WINS at (i).
  - Otherwise UNRESOLVED.
6.4 HYBRID ACCESS: the index-ablation gap of the frozen HYBRID. HYBRID_REQUIRED on a WIN (intact over ablated).
  "No collapse" reads UNRESOLVED unless the positive-control HYBRID collapses under the same ablation (it does: dev gap
  1.23).
6.5 INTERVENTION: DEFERRED (operator ruling item 5; D11).
  - As specified, the swap target (an HR2-matched blind merge) is a lookup table that cannot predict unseen cells, so the
    arm could not falsify.
  - The subsample repair would measure data value, not requirement. intervention.py is kept, flagged NOT USED.
6.6 AGGREGATION:
  - GENERATOR_DEPENDENT: holds in some generator strata of a family x level only.
  - CROSSOVER: switches with level within a generator.
  - NULL: TESTABLE, positive control PASS, and EQUIVALENT among the compared arms.
  - INSTRUMENT_FAILURE: a fixture or positive control fails where the instrument itself was the target.
  - UNTESTED: gated out (reported with dev values).
  - UNREPLICATED: see 6.7.
6.7 FALSIFIERS, written before data. Each fires on its own, PER STRATUM, and is reported with its scope.
  - F-B (lossless): COUNTERMODEL_SIGNAL (6.1 strict). An L-R-only result is LOSSLESS_TRANSIENT_CONTRACTION (damages the
    persistent-state reading only).
  - F-C (indiscriminate): INDISCRIMINATE_EQUIVALENT or RANDOM_BEATS_SELECTIVE (6.3). SCOPE: with the factor model
    fixed, this tests relevance-selective retention of EXACT RECORDS, not selective contraction as a whole.
  - No falsifier conjoins an absence.
  - Neither an UNFIRED F-B nor an UNFIRED F-C is support for the law. In particular F-B strict has near-zero power in
    latent families: L-K ~0 AC on never-seen cells (operator ruling item 5).
  - REPLICATION (symmetric for falsifiers and SUPPORT labels SELECTIVE_ADVANTAGE / RESERVOIR_SELECTIVE_ADVANTAGE):
    - a firing must reproduce the same reading on the held-out block of N_REP worlds for that stratum (TABLES; 80%
      power at a true effect of 2 x DELTA; floor 8; cap 64);
    - above the cap it reads UNREPLICATED (neither falsifier nor support).
  - MULTIPLICITY: for each label, report the strata TESTED and the EXPECTED chance firings (one-sided .05 per WIN
    reading; TOST .05 per EQUIVALENCE reading).

## 7. Controls and fixtures (status at freeze)

- Instrument trio F-L / F-S / F-B under the relative selectivity reading: PASS at 0.8 / 1.6 / 2.9 visits/cell.
- Reservoir curve fixture: monotone; full = L-R. PASS after D7.
- Eviction positive control (oracle beats random at matched B): PASS (+.91). The two system candidates LOSE to random
  there (a dev finding).
- R1c/R1d cheat fixtures on L-R, L-R-rec, H-rec: FLAGGED (PASS).
- R1e ablation positive-control HYBRID: PASS (gap 1.23).
- Intervention controls fire, but the arm is deferred (D11).
- Launch-gate negative controls: PASS, including the operator's own ruling text with its "<hash>" placeholder.
- Per-stratum E6 positive control: PASS/FAIL per stratum in the TABLES. Where it fails, 6.3 reads UNRESOLVED by rule.

## 8. Derived quantities -> PREREG_WTP_LM01_TABLES.md (generated by ensorain/lm01/prereg_tables.py from
dev/margins_reduced_v2.json; rules in ensorain/lm01/margins_reduce_v2.py).

## 9. Seeds and LAUNCH GATE (operator ruling item 6)

- Dev ranges used: 9_1xx_xxx .. 9_6xx_xxx (listed in DEV_SWEEP_LOG.jsonl and the code). make_world refuses any other
  seed below 10^9.
- AUTHORITY: OPERATOR ONLY, in direct chat. Aporia and Cyclops are REMOVED; no second seat; no comms approval.
- The instruction "LAUNCH WTP-LM01 using frozen prereg <hash>" is recorded VERBATIM as a committed prompt file with a
  verifying MANIFEST.
  - launch_gate.campaign_seeds() opens only if that committed, verified file contains the instruction with a hex hash
    (7-40 chars) that is a prefix of the FREEZE COMMIT SHA in ensorain/lm01/FREEZE.json.
  - Any text lacking the matching hash does not launch.
- CAMPAIGN seeds: 10^9 + (sha256(f"{FREEZE_COMMIT}|LM01-campaign|{stratum}|{i}")[:12 hex] mod 4 x 10^8); a collision
  aborts.
- REPLICATION seeds: 2 x 10^9 + (the same with LM01-replication). Disjoint by construction; used only for a firing
  stratum after the campaign verdict.

## 10. Campaign size, runtime, concurrency

- N = 48 worlds per TESTABLE stratum. 41 TESTABLE strata gives 1,968 campaign worlds.
- Compute estimate from the dev walls: ~72 worker-hours = ~9 h wall at 8 workers.
- Plus replication blocks (N_REP per firing stratum: 8-58 worlds each; TABLES).
- Concurrency: 8 workers, 1 BLAS thread, BELOW_NORMAL priority, a stop at < 6 GB free RAM, rows written per stratum
  from Python, start/end logged.
- M2 must be free of other heavy jobs at launch (checked by process census, not assumed).

## 11. Limitations (written before data)

- Finite horizon.
- Synthetic, generator-conditional: "SELECTIVE wins where its inductive bias matches the generator" is a candidate
  reading.
- The secondary comparison is optimizer-confounded.
- v1 selection data was seen before two redesigns (R-a withdrawn, R-c adopted).
- F5-lowrank split-rule artefact.
- The reservoir is recency-blind (F3).
- L-R has seed-sensitive local minima.
- S-cp is bimodal across learner seeds.
- F-B strict has near-zero power in latent families; an unfired F-B is not support.
- REQUIREMENT (causal necessity of selectivity) is UNTESTED.
- F-C covers exact-record retention with a fixed factor model only.
- LOW-POWER REGIONS (from the TABLES):
  - L1-F2 is EMPTY;
  - F2-L2 is UNTESTED at 0.30 (66 never-seen cells);
  - the E6 positive control FAILS in F3 (all), F4 (all), and F2 pairwise/sum, so INDISCRIMINATE readings there are
    UNRESOLVED by rule;
  - F5-L1 UNTESTED (only 2 usable dev worlds). F5-L2 UNTESTED at 0.30 (65 never-seen cells).
  - F5-L3 is TESTABLE in 6/6 strata, with the E6 control passing in 5/6 (all but lowrank) under the repaired scale.
  - Totals at 0.30: 41 of 75 strata TESTABLE; E6 passes in 10 of those 41.
- The dev decision rule was changed after dev rows were read: D9 and D10 were ruled by the operator on disclosed
  grounds; the sensitivity columns show how much hangs on 0.30.

## 12. Dev design findings (kept out of results)

- The rank-2 55x byte gap.
- The noise lever: null.
- Eviction candidates losing to random on the positive-control world.
- The selection "dev pictures".
- Replay not closing the SGD/ALS gap.
- Competence tracking retained exact records under an equalised optimizer.
- Warm full reservoir more stable than cold L-R.
- Learned-key HYBRID collapses under ablation.
- L-K ~0 on never-seen cells.

## 13. Defect ledger (self-reported; direction each cut)

- D1: R(tau) non-monotone -> HR2 matched (neutral).
- D2: rate vs bytes -> IM-rate primary (neutral).
- D3: life 4x full coverage at L1 -> derived min count (against LOSSLESS's easiest wins).
- D4: absolute selectivity readout certified a blind merge -> relative reading (had favoured SELECTIVE).
- D5: revisit-density power limit -> per-stratum positive control.
- D6: the O3 replay SELECTIVE never built -> R-c headline (the confound had favoured LOSSLESS).
- D7: L-R under-converged -> one convergence rule (had cut AGAINST LOSSLESS).
- D8: R1d byte counter masked by timestamp reads -> store-record counter (had hidden a LOSSLESS cost).
- D9: N_MIN grid capped at 256 -> scan to the actual n_test (neutral; more strata testable).
- D10: noise-derived pooled margin made equivalence easy for unstable arms (tilted toward F-C/NULL) -> fixed DELTA 0.30.
- D11: intervention decided by construction -> deferred.
- Operator-ruled scale defect: F5 all_cells rung scale -> real_cells (the positive control was failing for scale
  reasons).
- Also self-reported during the build: a fabricated commit hash in chat (corrected); an estimated heartbeat time
  (corrected); an unverified contention claim (corrected, #704).
- Lever provenance (H6): life 4x helped SELECTIVE on F3 and was mixed elsewhere; nuis_p .5 mixed; noise null; min
  count now fixed-delta-derived.

## 14. Checklist self-check (programs/selective_irreversibility/reviews/LM01_PREREG_CHECKLIST.md)

Marked against this file.
- Row groups:
  - A1 s1 | A2 s1, 6.1 | A3 6.7 | A4 6.0 (EQUIVALENT needs the CI inside +-.30; positive control 6.3) | A5 6.1-6.6 |
    A6 6.7 | A7 s11: PASS.
  - B1-B4 s4 | B5 6.4 + s7 | B6 s4 | B7-B8 s4 | B9 s4 (cap-bound flags in the TABLES) | B10 s4: PASS.
  - C1 6.1 (L-R endpoint, warm reservoir beside it) | C2 6.2 | C3 6.1 B* | C4 6.3 | C5 s4 | C6 s7: PASS.
  - D1-D5 s5: PASS.
  - E1 s2 | E2 s2 | E3 s3 | E6 s7 + TABLES | E7 s2 | E8 s2 | E9 (16 dev worlds per stratum): PASS.
  - F1 6.5: N/A (deferred by operator ruling item 5; limitation stated).
  - G1 s9 | G2 s5 | G3 s5 | G4 DEV_SWEEP_LOG | G5 s10 + TABLES: PASS.
  - H1 6.0 | H2 s4/s7 | H3 not run | H4 s12 | H5 s13 | H6 s13: PASS or N/A as stated.
- AMENDED BY OPERATOR RULING (the checklist text predates it):
  - E4 min count: now derived from the fixed DELTA, not a noise margin.
  - E5 gate threshold: now DELTA, not a dev-noise X.
  - G6/H7 Harmonia freeze: the operator froze steward process; Harmonia's freeze is not a launch precondition unless the
    operator says so.
  - G7 steward-added readouts each passed a fixture (HR2_signal is reported, labelled "not a certificate", after D4).
- H3 (the O6 exploratory stratum): NOT RUN in LM01; stated.
