# PREREG_WTP_LM01 -- Lossless Memorizer Challenge (DRAFT v0.1, NOT FROZEN)

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

## 6. Readings and verdict mapping (A3, A4, A5, C1-C4, H1) -- PROPOSED, for steward review

Per stratum, a reading is made only if the stratum is TESTABLE: eligible (derived min count, E4) AND learnable (gate X,
E5). Otherwise it is UNTESTED (reported with dev ACs). Margins are per stratum [MARGINS]: MATCH = within MARGIN; WIN =
beyond 2 x MARGIN (H1). Every no-difference reading needs an equivalence test (the CI of the difference inside the
MARGIN) plus a positive control detected by the same analysis; otherwise UNRESOLVED (A4).

6.1 HEADLINE: the same-optimizer RESERVOIR-REFIT curve (C1). Random eviction, B in {c/8, c/4, c/2, c, 2c, full};
    full = L-R.
  - EXACT_RETENTION_PAYS: AC(full) - AC(largest bounded rung below full) > 2 x MARGIN, AND B* = none (no bounded rung
    within MARGIN of full). Label LOSSLESS_TRANSIENT_CONTRACTION, because the full end is L-R (A2). It is
    COUNTERMODEL_SIGNAL (strict) only if L-K (no transient contraction) is itself within MARGIN of full.
  - BOUNDED_SUFFICES (added label): B* < full, with equivalence of AC(B*) and AC(full) inside MARGIN and a positive
    control (the curve fixture's monotone detection at this stratum's density).
    - This neither supports nor damages the law by itself: the reservoir discards relevance-blindly.
    - It is reported with B*/n (the retained fraction) and bytes.
  - UNRESOLVED otherwise.
6.2 SECONDARY (C2): SELECTIVE-proper vs LOSSLESS, labelled "optimizer confounded (SGD vs ALS)".
  - SELECTIVE_ADVANTAGE: some SELECTIVE ladder point with <= bytes and <= reads beats the frozen LOSSLESS choice by more
    than 2 x MARGIN.
  - COUNTERMODEL_SIGNAL (secondary): the frozen LOSSLESS choice is matched or beaten by no SELECTIVE ladder point
    (R2), with an L-R choice labelled LOSSLESS_TRANSIENT_CONTRACTION.
  - [BUILD] the SELECTIVE capacity ladder (cells/16 .. up to LOSSLESS bytes).
6.3 EVICTION (C4, C5): RESERVOIR-SELECTIVE (the frozen candidate) vs RESERVOIR-RANDOM.
  - (i) matched B (primary) and (ii) matched HR2: the random B is interpolated, 3 seeds, extra bytes charged.
  - INDISCRIMINATE_EQUIVALENT: equivalence under (i) AND (ii), plus positive-control PASS (E6); otherwise UNRESOLVED.
  - SELECTIVE_BUYS_BYTES: the selective candidate wins at (i) but not at (ii).
  - RESERVOIR_SELECTIVE_ADVANTAGE (added label): it wins at both (i) and (ii).
  - RANDOM_BEATS_SELECTIVE (added label): random wins at (i) by more than 2 x MARGIN. A legitimate s4C result (#673).
6.4 HYBRID ACCESS (B5): index ablation of the frozen HYBRID within the same per-query budget.
  - HYBRID_REQUIRED if competence collapses by more than 2 x MARGIN.
  - "No collapse" reads UNRESOLVED unless the positive-control HYBRID collapses under the same ablation.
  - [BUILD] the ablation run + positive-control HYBRID.
6.5 INTERVENTION (F1; secondary): clone the frozen SELECTIVE at t* = life/2, then swap in an IM-rate merge of the same
    prefix (HR2-matched).
  - Negative control: an independently seeded SELECTIVE of equal HR2. Positive control: a planted must-hurt world.
  - Caveat, verbatim: "the selective state was needed for the rest of THIS life", not "selectivity in general".
  - [BUILD].
6.6 AGGREGATION:
  - GENERATOR_DEPENDENT when a reading holds in some generator strata of a family x level only.
  - CROSSOVER when it switches with level (complexity/horizon) within a generator.
  - NULL: testable, the positive control passes, and every reading is within MARGIN without the equivalence CI passing.
  - INSTRUMENT_FAILURE: a fixture or a positive control fails where the instrument itself was the target.
6.7 FALSIFIER (A6), written before data: "In WTP, selective contraction is not necessary for the tested form of reusable
    generalization" is sent to the stewards if, in at least one TESTABLE stratum per family among F2-F5 at L2 or L3:
    - (a) the headline reads EXACT_RETENTION_PAYS or BOUNDED_SUFFICES with RANDOM eviction; AND
    - (b) the secondary shows no SELECTIVE_ADVANTAGE; AND
    - (c) the eviction reading is INDISCRIMINATE_EQUIVALENT or RANDOM_BEATS_SELECTIVE.
    [Steward review: this is my proposal. The stewards may tighten it to "a majority of strata".]

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
- CAMPAIGN seeds: seed(stratum, i) = 10^9 + int(sha256(f"{PREREG_SHA}|LM01-campaign|{stratum}|{i}").hexdigest()[:8], 16),
  i = 0..N-1. PREREG_SHA is the commit that freezes this file.
  - make_world refuses any seed outside the dev range below 10^9.
  - The derivation code is committed with the freeze, and no campaign seed is materialised before the launch prompt.
  - [BUILD] campaign runner.

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
- The RESERVOIR is recency-blind (no stored step). On F3 its curve mixes episodes (#692; pending ruling).
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
