+==============================================================================================+
| WTP-LM01 LOSSLESS MEMORIZER CHALLENGE -- PREREG v0.3.1 FROZEN: OPERATOR REVIEW PACKET        |
| Author: Ensorain[m2-32b65655], Foundry seat, M2 (SPECTREX5)        Date: 2026-09-26           |
| For: the operator (launch authority) and any external reviewer                               |
| Status: FROZEN, NOT LAUNCHED. No campaign seed or row exists. The gate is closed.            |
| Self-contained: every load-bearing number is inline; no repo access needed.                  |
+==============================================================================================+

-----
0. SUMMARY
-----
- Question (directive s2): under honestly accounted bounded resources, can a system that keeps its admitted history
  EXACTLY reach the held-out / fresh-field competence of systems that keep a bounded coarse-grained representation?
- The design is frozen: prereg v0.3.1 at commit 768ea8ce9e84a1a078bba34813908d4fafbb268b (supersedes v0.3 at 47526ff86,
  before any row; defect D12, s6).
  - 75 strata (5 families x 3 sizes x generators).
  - 41 strata TESTABLE at the governing tolerance: 38 carry the headline, and 3 are F1 branch triggers.
  - 48 campaign worlds per TESTABLE stratum, i.e. 1,968 worlds.
  - Estimated ~9 h wall at 8 workers on M2 (72 worker-hours from the dev walls), plus replication blocks.
- My lean: launchable as frozen. The informative outputs are the reservoir curve and the LOSSLESS_TRANSIENT_CONTRACTION
  reading. The eviction (F-C) reading has power in only ~10 strata, and REQUIREMENT is untested by design.

-----
1. HYPOTHESES AND FALSIFIERS (written before data)
-----
Claim under test: the PERSISTENT-STATE reading of the law.
- A contraction done transiently at readout and then discarded (L-R) is not persistent contraction.
- WHETHER SELECTIVITY IS CAUSALLY REQUIRED REMAINS UNTESTED in LM01 (ruling item 5).

Headline, per stratum: a same-optimizer RESERVOIR curve.
- Rank-3 factors refit by converged ALS, plus B exact records under random eviction, for B in
  {c/8, c/4, c/2, c, 2c, full store}.
- Two endpoints, both reported side by side (ruling item 4):
  (a) L-R, the declared lossless endpoint: a per-query refit on the full store. It can hit local minima (dev seed
      p97.5 up to 1.11 AC).
  (b) the warm full-store reservoir, a persistent learned fit. It is more stable (dev p97.5 .09 in the same stratum) and
      never substituted for (a).

Readings:
- EXACT_RETENTION_PAYS: L-R WINS over every bounded rung.
  - With L-K EQUIVALENT to L-R (L-K = an unlearned min-Hamming kernel, no fit at all) -> COUNTERMODEL_SIGNAL = F-B.
  - Otherwise -> LOSSLESS_TRANSIENT_CONTRACTION. This damages the persistent-state reading only.
- BOUNDED_SUFFICES (some B* < full is EQUIVALENT to L-R): reported with NO verdict weight. Every rung carries a fitted
  selective factor model.
- F-C: at B = c/4 and at B = c, each its own reading. A reservoir that evicts by its own residuals vs random eviction:
  - INDISCRIMINATE_EQUIVALENT, which needs equivalence at matched B AND at matched recoverability (HR2), plus a passing
    per-stratum positive control;
  - or RANDOM_BEATS_SELECTIVE.
  - Scope: this tests relevance-selective retention of exact records with the model fixed, not selective contraction
    as a whole.
- Supports (SELECTIVE_ADVANTAGE, RESERVOIR_SELECTIVE_ADVANTAGE) and falsifiers must REPLICATE on a pre-declared held-out
  block before they are sent. N_REP = 8-11 worlds in TESTABLE strata (80% power at 2 x delta), cap 64; above the cap,
  UNREPLICATED.
- Multiplicity: the readings tested and the chance-expected firings (.05 each) are reported per label.
- No falsifier conjoins an absence. An UNFIRED F-B or F-C is NOT support for the law.

-----
2. GOVERNING DECISION RULE: DELTA = 0.30 AC (ruling item 2)
-----
- AC = -log10(MSE / field variance). 0.30 AC = a 2x MSE ratio.
- Every comparison uses the per-world paired difference with a 90% t-interval over worlds (one-sided .05 per
  direction):
  - EQUIVALENT: the CI lies inside (-0.30, +0.30);
  - WIN: the CI lies entirely beyond +0.30;
  - otherwise UNRESOLVED.
- No margin is derived from an arm's own instability. The v1 noise-derived margin reached 1.8 AC for unstable arms,
  which made equivalence nearly automatic; it is retired (D10).
- Known-answer tests confirm that a very noisy arm with a matching mean reads UNRESOLVED, not EQUIVALENT.
- Also governed by 0.30: eligibility (bootstrap CI half-width of AC <= 0.15 at the stratum's test size) and the
  learnability gate (CI lower bound of the best-arm gain over the best constant > 0.30).

-----
3. SENSITIVITY 0.15 / 0.60 (descriptive only)
-----
- Every reading is recomputed at 0.15 and 0.60 and reported beside the 0.30 verdict. The sensitivity readings never
  change a verdict.
- Dev frame counts: TESTABLE 16 at 0.15 / 41 at 0.30 / 37 at 0.60. Small delta fails eligibility; large delta fails the
  learnability gate.

-----
4. REPAIRS RULED 2026-09-26
-----
- D9 (minimum test size): the scan now runs to each stratum's actual test size. The F3/F4 strata with 512-cell test
  sets became eligible. No arm changed.
- F5 reservoir scale: capacity is computed from the real dimensions, excluding the nuisance mode.
  - OLD interpretation (documented): at c/2 the reservoir held ~73% of an F5 history vs ~18% elsewhere, and the
    positive control failed (oracle - random .06-.13 AC).
  - REPAIRED (dev re-run, 288 worlds): F5 L2/L3 look like the other families, and the positive control passes in
    F5-L3 in 5 of 6 generators.
- Also found and fixed during the build, before the freeze:
  - D8: the full-read audit counter was fooled by timestamp reads (it would have hidden a LOSSLESS cost);
  - D11: the intervention arm was decided by construction, so it is deferred.
- D12, found AFTER the v0.3 freeze and BEFORE any row: the frozen analysis would have produced headline labels and
  falsifier firings for the 3 F1 strata from EXACT-HIT cells, contradicting the prereg. Fixed, then re-frozen as
  v0.3.1. The superseded v0.3 hash is rejected by the gate.

-----
5. POSITIVE CONTROLS AND FIXTURES (status at freeze)
-----
  PASS  instrument trio (no-loss / selective / blind), relative selectivity reading, at 0.8 / 1.6 / 2.9 visits/cell
  PASS  reservoir curve: monotone in B; full store matches converged L-R (after D7, the L-R under-convergence fix)
  PASS  eviction positive control: oracle beats random by +.91 AC. NOTE: both declared self-signal eviction rules LOSE
        to random there; they keep noisy records. That is recorded as a dev finding, not repaired.
  PASS  cheat fixtures: a kept fit and a subsampled refit are FLAGGED on L-R, L-R-rec, H-rec
  PASS  hybrid index-ablation positive control: gap 1.23 AC
  PASS  launch-gate negative controls: 8/8 rejected. These include your own ruling text with "<hash>", a wrong hash,
        the old comms token, and the superseded v0.3 hash.
  PASS  analysis known-answer tests: all label paths; 49 tests in total
  PER-STRATUM positive control (E6): passes in 10 of the 41 TESTABLE strata (F2-L3 x4, F5-L3 x5, F1-L1).
        Where it fails, F-C reads UNRESOLVED by rule.

-----
6. KNOWN LOW-POWER / UNTESTED REGIONS
-----
- UNTESTED at 0.30:
  - L1-F2: all 6 strata (full coverage, <8 never-seen cells);
  - F5-L1: 2 usable dev worlds;
  - F2-L2 and F5-L2: 65-66 never-seen cells, CI too wide;
  - some pairwise/sum strata fail the learnability gate.
- F-C (eviction) is effectively UNRESOLVED outside ~10 strata: the positive control fails in all of F3 and F4 and in
  F2 pairwise/sum.
- F-B strict has near-zero power in latent families: L-K scores ~0 AC on never-seen cells. The informative lossless
  reading there is LOSSLESS_TRANSIENT_CONTRACTION.
- F3 switch: the reservoir is recency-blind and mixes episodes. S-cp is bimodal across learner seeds. L-R has seed
  local minima.
- The secondary SELECTIVE-proper vs LOSSLESS comparison is optimizer-confounded (online SGD vs ALS).
- F5-lowrank: every arm is weak (a split-rule artefact).

-----
7. CAMPAIGN SIZE / RUNTIME / CONCURRENCY
-----
- 41 strata x 48 worlds = 1,968 worlds; ~72 worker-hours = ~9 h wall at 8 workers.
- Plus replication blocks for firing strata only (8-11 worlds each among TESTABLE strata).
- 8 workers, 1 BLAS thread, BELOW_NORMAL priority, a stop if free RAM < 6 GB, rows written per stratum from Python,
  start/end logged.
- The launcher refuses unless:
  (1) all 51 frozen files still hash to FREEZE.json;
  (2) your directive is committed verbatim with a verifying MANIFEST, and it contains
      "LAUNCH WTP-LM01 using frozen prereg <prefix of 768ea8ce9e84...>";
  (3) a process census finds no other heavy job on M2.
- No Aporia or Cyclops step is involved.

-----
8. WHAT THIS CAN AND CANNOT ESTABLISH
-----
CAN:
- per-stratum evidence whether exact retention buys generalization over bounded reservoirs with the same optimizer;
- whether that gain needs a transient learned fit (L-R) or survives an unlearned readout (L-K);
- whether residual-driven eviction beats random eviction at matched bytes AND matched recoverability, where the
  control has power.
CANNOT:
- causal REQUIREMENT of selectivity (untested);
- anything beyond the declared synthetic generators;
- unbounded horizons;
- a computation-inclusive version of the law (an L-R win says nothing either way about it).

-----
9. QUESTIONS FOR THE REVIEWER (written to resist agreement)
-----
- Q1. With F-B strict near-powerless in latent families, is LM01 mostly a test of LOSSLESS_TRANSIENT_CONTRACTION? If
  so, is that worth ~9 h, or should the campaign be cut to the 10 strata where the eviction control has power plus the
  headline strata?
- Q2. Is 48 worlds per stratum right, given N_REP of only 8-11? It could be halved for ~4.5 h at some loss of CI width.
- Q3. Should F1 (3 strata, 144 worlds of branch trigger) run at all, now that it can never fire?
- Q4. "Do not launch" remains a first-class answer.

-----
10. ARTIFACTS
-----
- Frozen prereg: ensorain/PREREG_WTP_LM01.md (sha256 f2da3195...dcb2); tables: ensorain/PREREG_WTP_LM01_TABLES.md
  (sha256 8091cf3d...02e3).
- FREEZE COMMIT: 768ea8ce9e84a1a078bba34813908d4fafbb268b. FREEZE.json: commit 87d06770c.
- Code: ensorain/lm01/ (campaign.py, analysis.py, launch.py, launch_gate.py, freeze.py). Rulings:
  roles/Ensorain/prompts/2026-09-26_lm01_operator_rulings/.
- Dev logs: ensorain/lm01/DEV_SWEEP_LOG.jsonl.

+==============================================================================================+
| To launch: "LAUNCH WTP-LM01 using frozen prereg 768ea8ce9" (any 7-40 character prefix).      |
| Or say "not worth continuing": that remains a first-class answer.                            |
+==============================================================================================+
