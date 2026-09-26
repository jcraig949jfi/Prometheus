# PREREG_WTP_LM01 -- Lossless Memorizer Challenge (DRAFT v0.2, NOT FROZEN)

Seat: Ensorain[m2-32b65655], M2. Directive: roles/Ensorain/prompts/2026-09-25_wtp_lm01_directive/
01_CYCLOPS_WTP_LM01_DIRECTIVE_verbatim.md (sha256 ab204631...). Steward rulings: ensorain/lm01/STEWARD_RULINGS.md
(the comms ids are cited per line). Review checklist: programs/selective_irreversibility/reviews/LM01_PREREG_CHECKLIST.md;
the self-check table is s14.

STATUS: DRAFT. Fields marked [MARGINS] are filled mechanically from dev/margins_reduced.json when the dev margin sweep
(lm01_margins_v1) finishes. Fields marked [BUILD] name code that does not exist yet. No campaign seed exists. Nothing
here may be read as a result.

## 1. Claim under test (A1, A2)

The candidate law is s1 of the program directive; its frozen text is held by Harmonia (HYPOTHESIS.md). LM01 tests the
PERSISTENT-STATE reading (#591 R1a): "a system that preserves its admitted experience exactly in PERSISTENT STATE does
not reach the held-out / fresh-field competence of systems whose persistent state is a bounded, coarse-grained
representation, under honestly accounted resources."
- Contraction performed transiently at readout and discarded (L-R) is NOT persistent contraction. A win by L-R is
  labelled LOSSLESS_TRANSIENT_CONTRACTION. It damages the persistent-state reading only and says nothing either way about
  a computation-inclusive law (sentence fixed in advance, A2).
- "Accessible" means operationally accessible to the acting system within its per-query budget (#608). Operational
  access is tested by index ablation (s6.4).

## 2. Worlds (E1, E2, E7, E8)

- WTP field generators (ensorain.wtp.world.base_field). LATENT_GENS = (lowrank, cp, tt, pairwise, spectral, sum) is
  FROZEN (#655/#656).
- Families (ensorain/lm01/families.py):
  - F1 episodic (random field, revisit walk). The LOSSLESS-must-win branch trigger; UNTESTED for the headline.
  - F2 latent.
  - F3 switch: 3 episodes; scored on the last.
  - F4 fresh-field transfer: shared component w = .6.
  - F5 nuisance mode: nuis_p = .5 in the headline; nuis_p = 1 is a declared "everyone falls" control, never in the
    headline.
- Levels: L1 8^3 / L2 12^3 / L3 16^3. life_mult = 4 for all (P1). Observation noise SD .1.
- Exposure: a walk on WTP's tensor-index geometry with no carrier learner (declared design choice).
- STRATUM = family x level x generator; 75 strata. Verdicts are per stratum. The pooled verdict is secondary, with the
  declared uniform mixture. A split across strata reads GENERATOR_DEPENDENT.
- Full-coverage cells (coverage ~1, too few never-seen cells) go to a separate "LOSSLESS = table" regime table and never
  enter the headline (#648). On v2 dev data, all six L1-F2 strata are EMPTY.

## 3. Test sets (E3)

- The headline is read on never-seen cells (F1-F3), fresh-field cells (F4) and OOD never-seen cells (F5), only where
  coverage < 1.
- Exact-hit cells are reported separately and never carry the headline.

## 4. Arms (B1-B10, H2) -- ensorain/lm01/arms.py

- LOSSLESS: exact append-only store (int16 cells, float64 values, int64 admission step), bit-recoverable.
  - Readouts:
    - L-K: min-Hamming kernel over the FULL store;
    - L-R: ridge ALS refit on the FULL store at each query, discarded after;
    - L-K-rec / L-R-rec: recency weights from the stored steps.
  - The per-query refit is charged (ops, reads, wall; R1b).
  - Cheat fixtures (tests): LRCache (a fit kept between queries) -> persist_growth_on_query; LRSubsample -> full-read
    violation. [BUILD] The same two cheat fixtures on L-R-rec and H-rec (H2).
- SELECTIVE-proper: WTP-native online substrates (organism.py) at cap = cells/4. The capacity ladder is [BUILD, s6.2].
  It needs no recency variant, since it adapts online (stated, B6).
- HYBRID: exact store + an online-SGD low-rank key (k-NN in key space); H-rec. The key is SGD, not ALS, so no ALS rule
  applies (B10).
- RESERVOIR-REFIT (BufferALS; the intermediate mechanism, named, not forced into a category; #666/#667): bounded rank-3
  factors + a reservoir of B exact records, warm ALS refit every >= 64 admissions (~100 at batch 50).
  - Eviction: random (the reference) or one of the 2 DECLARED system candidates keep_worst / residual_reservoir (C5).
  - The reservoir stores no admission step, so it is recency-blind; F3 limitation (s11).
- IM-rate / IM-bytes: RandomMerge with bins bisected to HR2 (D2).
- ALS convergence (B9): every ALS fit iterates until the relative loss change is < 1e-4, max 80. Iterations and the
  cap-hit fraction are reported per arm and per rung; a rung with median cap-hit > .1 is flagged as a lower bound.
- Arm formation (B7, B8): dev-only selection v2 on seeds 9_410_000-015, with an equal budget of 8 per family
  (SELECTIVE, LOSSLESS, HYBRID) and 2 for the eviction candidates. The criterion is the median headline AC.
  - The choice is frozen per stratum in ensorain/lm01/FROZEN_SELECTION.json (source selection_v2.json sha256
    0091e59959cdc7ff...).
  - v2 is the LAST grid change; only fixture-demonstrated defects may change the grid afterwards.

## 5. Measurement (D1-D5, G2, G3)

- AC = -log10(MSE / V0), V0 = 1 (standardised fields), clipped to [-3, 6].
- Resources are MEASURED per arm: persistent bytes (peak), bytes written, bytes read, ops, replay ops, wall, and
  external bytes (accounting.py). There is no exchange-rate scalar; comparisons are Pareto (G3).
- Recoverability (recover.py):
  - HR2 is the MATCHED quantity (RECOVERABLE tier; never decides a verdict alone);
  - HR2_signal is REPORTED, and its gap is labelled "not a certificate";
  - R(tau) and distinguishability are REPORTED.
  - Declared reconstruction maps: store record / substrate readout / bin mean.
- Selectivity is read RELATIVE to K = 5 seeded HR2-matched blind references. Threshold .0155 (99th percentile of
  |ref-ref|, dev/selectivity_threshold.json). UNMATCHED means no reading; its frequency per arm is reported (D3).
- Relevance comes from the GENERATOR only (D4).

## 6. Readings and verdict mapping (A3, A4, A5, C1-C4, H1) -- JOINT after review (#697, #698, #700; #693)

TESTABLE per stratum = ELIGIBLE (derived min count, E4) AND LEARNABLE (gate X, E5); otherwise UNTESTED, with dev ACs.
- MARGIN (per stratum [MARGINS]) is REPLICATE-based: learner seed + an independent test bootstrap of the same world.
  - This is a NAMED DEVIATION from #591 R2a's "across seeds" (#691/#698). The margin measures INSTRUMENT noise.
    World-to-world spread enters each comparison's CI instead; counting it in both places would make "matched" too
    permissive.
  - The between-world SD is reported beside the MARGIN per stratum.
- MATCH = within MARGIN; WIN = beyond 2 x MARGIN (H1).
- Every no-difference reading needs a PASSING equivalence test (the 90% CI of the paired difference over worlds lies
  inside +-MARGIN) plus a positive control detected by the same analysis. Otherwise UNRESOLVED (A4).
- No verdict conjoins an absence (#697.1).

6.1 HEADLINE: the same-optimizer RESERVOIR-REFIT curve (C1).
  - Random eviction, rank 3, B in {c/8, c/4, c/2, c, 2c, full}.
  - The full-store END is the recency-BLIND converged L-R (rank 3) in EVERY stratum, including F3 (#693), so the endpoint
    is the rungs' readout family.
  - The frozen LOSSLESS choice (e.g. L-R-rec on F3) vs the reservoir is reported separately, labelled
    "recency-aware vs recency-blind" where it applies.
  - EXACT_RETENTION_PAYS: AC(full) exceeds EVERY bounded rung by > 2 x MARGIN (a demonstrated win over each rung).
    - STRICT form: additionally L-K is within MARGIN of full (equivalence passing) -> COUNTERMODEL_SIGNAL (F-B).
    - Otherwise (the full end needs L-R's transient fit) -> LOSSLESS_TRANSIENT_CONTRACTION. It damages the
      persistent-state reading only (A1/A2).
  - BOUNDED_SUFFICES: B* < full with equivalence passing. REPORTED ONLY, with NO verdict weight either way (#697.2):
    every rung carries a fixed, fitted, relevance-selective factor model, so "bounded suffices" means "a selective model
    plus some blind exact records is enough".
  - Otherwise UNRESOLVED.
6.2 SECONDARY (C2): SELECTIVE-proper vs LOSSLESS, labelled "optimizer confounded (SGD vs ALS)". It never gates a
    falsifier.
  - SELECTIVE_ADVANTAGE: some SELECTIVE ladder point with <= bytes and <= reads beats the frozen LOSSLESS choice by more
    than 2 x MARGIN.
  - COUNTERMODEL_SIGNAL (secondary): for EVERY SELECTIVE ladder point at <= LOSSLESS bytes, LOSSLESS exceeds it by more
    than 2 x MARGIN (a demonstrated win; #697). An L-R choice is labelled LOSSLESS_TRANSIENT_CONTRACTION.
  - [BUILD] the SELECTIVE capacity ladder (cells/16 .. LOSSLESS bytes).
6.3 EVICTION (C4, C5): RESERVOIR-SELECTIVE (the frozen candidate) vs RESERVOIR-RANDOM.
  - Read (i) at matched B (primary) and (ii) at matched HR2 (random B interpolated, 3 seeds, extra bytes charged), at
    B = c/4 and B = c.
  - INDISCRIMINATE_EQUIVALENT: equivalence PASSES under (i) AND (ii), plus positive-control PASS (E6). Otherwise
    UNRESOLVED.
  - SELECTIVE_BUYS_BYTES: a win at (i), not at (ii).
  - RESERVOIR_SELECTIVE_ADVANTAGE (added): a win at (i) AND (ii).
  - RANDOM_BEATS_SELECTIVE (added): random wins at (i) by more than 2 x MARGIN (#673: a legitimate s4C result).
6.4 HYBRID ACCESS (B5):
  - Index ablation of the frozen HYBRID, within the same per-query budget. HYBRID_REQUIRED on a collapse > 2 x MARGIN.
  - "No collapse" reads UNRESOLVED unless the positive-control HYBRID collapses under the same ablation.
  - [BUILD]
6.5 INTERVENTION (F1; secondary): the clone/swap design of #625.
  - Caveat, verbatim: "the selective state was needed for the rest of THIS life", not "selectivity in general".
  - [BUILD]
6.6 AGGREGATION AND NULL:
  - GENERATOR_DEPENDENT: a reading holds in some generator strata of a family x level only.
  - CROSSOVER: a reading switches with level within a generator.
  - NULL: TESTABLE, the positive control passes, and equivalence PASSES among the compared arms (demonstrated no
    difference, #697.4). Within-margin without a passing equivalence test is UNRESOLVED.
  - INSTRUMENT_FAILURE: a fixture or positive control fails where the instrument itself was the target.
6.7 FALSIFIERS (A6), written before data. Split by countermodel; each fires, and is reported, on its own.
  - F-B (lossless, s4B): a stratum reads COUNTERMODEL_SIGNAL (6.1 strict).
  - F-C (indiscriminate, s4C): a stratum reads INDISCRIMINATE_EQUIVALENT or RANDOM_BEATS_SELECTIVE (6.3).
    SCOPE, in advance: with the factor model held fixed, this tests relevance-selective retention of EXACT RECORDS, not
    selective contraction as a whole.
  - LOSSLESS_TRANSIENT_CONTRACTION is reported as damage to the persistent-state reading only. It is not an F-B firing.
  - PER STRATUM: one clean stratum is a SCOPED counterexample, reported with family x level x generator (#697.5).
  - REPLICATION (symmetric; #697.5, #698b): any firing of F-B / F-C AND any SUPPORT label (SELECTIVE_ADVANTAGE,
    RESERVOIR_SELECTIVE_ADVANTAGE) must replicate on the pre-declared HELD-OUT block (s9) before it is sent as a
    falsifier or a support.
    - The block size per stratum gives the replication test >= 80% power for an effect of 2 x MARGIN, using the dev
      between-world SD of the relevant paired difference [MARGINS].
    - If that size exceeds 64 worlds per stratum (declared cap), the firing reads UNREPLICATED (neither falsifier nor
      support).
    - The replication is one-sided at alpha .05 in the firing's direction.
  - MULTIPLICITY (#698a): beside the results, per label, report the number of strata TESTED and the number EXPECTED to
    fire by chance at the label's error rate.
    - Declared rates: WIN readings one-sided alpha .05 on the paired difference.
    - EQUIVALENCE readings via TOST at .05 each side.

## 7. Controls and fixtures (G7, C6, E6)

- Instrument trio F-L / F-S / F-B passes under the relative reading at 0.8 / 1.6 / 2.9 visits/cell (selectivity.py).
- Reservoir fixtures: the curve is monotone and the full store matches L-R; the eviction positive control fires
  (oracle +.91) (dev/fixture_reservoir.json).
- Per-stratum eviction positive control at the stratum's own density [MARGINS].
- [BUILD] the R1e positive-control HYBRID; the intervention controls; H2 cheat fixtures on the -rec variants.

## 8. Derived quantities [MARGINS]

Per stratum:
- MARGIN;
- the win threshold 2 x MARGIN;
- N_MIN;
- the gate X;
- LEARNABLE / ELIGIBLE;
- B*;
- END_OK;
- the positive-control pass;
- cap-bound rungs;
- visits/cell.
Rules: ensorain/lm01/margins_reduce.py (committed before the sweep rows are read).

## 9. Seeds (G1)

- Dev ranges used:
  - 9_100_000.. (families/coverage);
  - 9_200_000.. (learnability);
  - 9_210_000.. (nuisance);
  - 9_220_000.. (P2);
  - 9_300_000.. / 9_310_000.. / 9_320_000.. / 9_330_000.. (fixtures);
  - 9_400_000.. (selection v1, seen);
  - 9_410_000.. (selection v2);
  - 9_500_000.. (margins).
- LAUNCH GATE and SEEDS: ensorain/lm01/launch_gate.py (#699/#700 exact-token pattern).
  - A release is a comms message with subject starting EXACTLY "WTP-LM01 LAUNCH:", kind ruling, from Cyclops (or the
    operator), Ensorain among the recipients, created after the freeze commit, and carrying the freeze SHA.
  - Negative controls on real messages (#592, #610, #698, #699, #701 and Ensorain's own #590/#625/#664/#692) are
    rejected; a synthetic well-formed release is accepted. These were run against the live comms DB before the freeze.
- CAMPAIGN seeds: 10^9 + (int(sha256(f"{FREEZE_SHA}|LM01-campaign|{stratum}|{i}")[:12 hex], 16) mod 4 x 10^8).
  Materialised only by campaign_seeds(release_id, ...), which re-checks the release against the DB; a collision aborts.
- HELD-OUT REPLICATION seeds: 2 x 10^9 + (the same hash with tag LM01-replication, mod 4 x 10^8). Disjoint from the
  campaign range by construction. Materialised only for a firing stratum, after the campaign verdict.
- make_world refuses any seed below 10^9 outside the dev range.

## 10. Campaign size, runtime, concurrency (G5) [MARGINS]

- Proposal: N = 48 worlds per TESTABLE stratum (3 x dev).
- Per-world cost is taken from the margin sweep (~83 s L3 / ~34 s L2 / a few s L1 at 1 worker, without replicate b).
- Estimated ~4-6 h at 8 workers BELOW_NORMAL on M2, under Cyclops's envelope at launch.

## 11. Limitations (A7), written before data

- Finite horizon: a LOSSLESS win does not show that indefinitely reusable bounded lossless intelligence exists.
- Synthetic families: every verdict is conditional on the declared generators. "SELECTIVE wins where its inductive bias
  matches the generator" is a candidate reading (#655.4).
- The secondary comparison is optimizer-confounded (SGD vs ALS).
- v1 selection data was seen before two redesigns (R-a proposed and withdrawn after a dev probe; R-c adopted). Neither
  used campaign seeds.
- F5-lowrank: every arm fails on dev, a likely artefact of the fixed fewest-parameter mode-split rule (#686).
- The RESERVOIR is recency-blind (no stored step). On F3 the headline mechanism mixes episodes; its endpoint is the
  recency-blind L-R (#693/#698).
- SELECTIVE-proper stability: S-cp shows bimodal learner-seed convergence (dev smoke F3-L2-cp: 1.90 vs -.04). The
  fraction per mode per stratum is reported [MARGINS].
- The margin is replicate-based (a named deviation from R2a; s6).
- F-C scope: exact-record retention with a fixed factor model, not selective contraction as a whole.
- L1's headline rests only on the families that are TESTABLE there [MARGINS]. L1-F2 is EMPTY.
- The intervention arm shows necessity for the rest of THIS life only.

## 12. Dev design findings -- kept OUT of results (H4)

- The rank-2 "55x" byte gap.
- The noise lever: no effect.
- Eviction losing to random on the positive-control world.
- The selection "dev pictures" of #685.
- Replay not closing the SGD/ALS gap.
- Competence tracking retained exact records under an equalised optimizer (#666). This motivated R-c; it is not a
  result.

## 13. Defect ledger (H5) and lever provenance (H6)

- D1 R(tau) non-monotone -> HR2 matched (neutral).
- D2 rate vs bytes -> IM-rate primary (neutral).
- D3 life 4x full coverage at L1 -> derived min count; L1 table regime (cuts against LOSSLESS's easiest wins).
- D4 absolute selectivity readout certifies a blind merge -> relative reading (cut FOR SELECTIVE before the fix).
- D5 revisit-density power limit -> per-stratum positive control.
- D6 O3 replay SELECTIVE never built -> R-c (the optimizer confound cut FOR LOSSLESS).
- D7 L-R under-converged -> convergence rule (cut AGAINST LOSSLESS).
- Levers:
  - life_mult 4 helped SELECTIVE on F3 and mixed elsewhere;
  - nuis_p .5 mixed;
  - noise: no effect;
  - min count: derived [MARGINS].

## 14. Checklist self-check (A1-H7)

[Filled at v0.2, once the [MARGINS] and [BUILD] items close. Each row cites the section above.]
