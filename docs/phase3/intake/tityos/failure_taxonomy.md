# False-signal taxonomy -- Tityos territory (Phase 3 intake)

Crawler: Tityos (instance m1-48555b76), 2026-10-01. Repository read at origin/main 5c98f59f1.
Territory: Harmonia, Nyx, Techne, Hecate, Artemis, Nemesis, Kairos, Elenchus, Charon, Skopos, Clymene,
Hypatia, Coeus, Eos, Pheme, plus the shared surfaces attacks/, falsification/, cartography/,
evidence_wiki/, and the Necropolis tool registry.

## How to read this file

- This is a DESCRIPTIVE taxonomy recovered from the repository's own history: audits, corrections,
  calibration ledgers, retractions, code, and defects this crawl found by reading code. It is not a
  verdict on which phenomena were real.
- Every class names its direction:
  - FP: the class manufactures signal.
  - FN: the class hides signal, or turns "could not see" into "is not there".
  - FP/FN: the class can do either.
- Instances cite repo-relative paths and short SHAs. The detail and the epistemic labels live in
  seats/<Seat>.md.
- The crawl's own discoveries carry a tag:
  - "[crawl]" marks a defect this crawl found that is not on the record. Its epistemic category is
    IMPLEMENTATION FACT where the line was read, and CODE-INFERRED CAPABILITY where the behaviour was
    inferred.
  - None of these defects has been confirmed by the owning seat.
- Severity labels are not used. What matters for Phase 3 is three things:
  - how often a class recurred;
  - how long it survived before anyone caught it;
  - who caught it.
- The 24 classes below absorb about 230 seat-level failure entries from six crawl lanes. Where the
  operator's starter list named a class, the name is kept; the name is given in parentheses where it
  maps to a broader class here.

The single most important pattern across the territory is: **the measurement carried its own answer**.
Harmonia's own phrase for it was "one failure primitive at three altitudes". It shows up as metadata
inside the measured vector, as an answer key inside the probe, as a generator writing its own verdict,
as a label prefix inside the variable under test, and as a calibration that ran the producer's own
generator, null and detector. Classes T01, T02, T05 and T16 are all versions of it.

----------------------------------------------------------------------------------------------------

## T01. Measurement carries its own answer (seeded witness, label leakage, provenance leakage) -- FP

Definition: the quantity being tested contains, by construction, the label, the answer or the
outcome. Any test then "finds" it.

Instances:
- **Metadata read as zeros.** charon/src/ingest_zeros.py:107 builds zeros_vector = 20 zeros +
  [root_number, analytic_rank, degree, log_cond]. harmonia/scripts/survivor_kill_protocol.py:45 sorts
  every positive slot as a zero.
  - Downstream results: the 04-13 "8/8 survivor" spectral-tail signal (8e2be1c64) and "rank from
    zeros 92.1%" (ebd7e8ab3, harmonia/paper/spectral_bsd.md).
  - The general problem was detected 04-16 (thesauros/proposals.md P-009, 8744918bf).
  - The retroactive audit (thesauros/cleanup_queue.md) is still OPEN, and its grep patterns miss this
    form. Never retracted. [crawl, line verified]
- **Rank in the clustered vector.** charon/tests/zero_battery.py clustered a 24-dim vector that
  contained analytic_rank and root_number against rank.
  - Fixed in charon/scripts/full_audit.py:1102-1108, in the same commit 9e189d683.
  - It is unknown which numbers the LLM council saw.
- **Answer key shipped inside the probe.** harmonia/services/grading_oracle.py R6 probes carry
  data["truth"].
  - A 3-line cheat reader scores 100%.
  - The oracle was advertised as "non-gameable" (MEASUREMENT_FLEET_2026-06-27.md) and broken ~6 weeks
    later by Harmonia's own lens B (REVIEW_20260812_program_and_instrument_audit.md s2).
  - Necropolis marks it NT-001 UNTRUSTED.
- **Generator prefix inside the label.** Charon swarm Hecate MI(kill_pattern, generator_id) z = 946-952
  was framed as emergent operator structure, but the kill patterns were prefix-tagged by generator.
  - Cross-generator MI was 0.0 (1aaad0277). After the prefix strip, z = 0.489 (43b094552).
- **ATK-014.** Ergon's H(kp|cell) = 0 because kill_pattern embeds generator_id (106c0bd5f; caught by
  Techne). attacks/REGISTRY.md ATK-014.
- **Instrument state as the outcome.** Coeus y = forged/scrap counted api_call_failed rows (2,176-2,553)
  as scrap, while the trap battery changed from 15 to 186 traps on 03-27.
  - Leave-one-forge-day-out AUC 0.461 / 0.338: Coeus learned the forge calendar.
  - Source: engine/necropolis/dossiers/coeus.dossier.json (Mnemosyne, 2026-09-10).
- **Pipeline state as the outcome.** 327/347 Stygian rows carry not_yet_implemented / no_loader kill
  patterns (pivot/sprint1/phase3/PHASE3_0_SMOKE_VERDICT_2026-05-30.md).
  - 73.8% of the PROMOTED G15 MI (1.41 nats) was control-flow circularity (cdf30e26a).
- **Magnitude or units encode the generator.** P149: abs_diff_le_N between a small knot invariant and a
  4-digit conductor can never hold; generator identity predicts ~98% of outcomes
  (aporia/docs/CYCLE_150N_MAGNITUDE_TAUTOLOGY_2026-08-24.md, c9af3911b).
  - Killed Aporia's 147-K/148-L arc, and Charon extended it to Diomedes' 75% headline (99b05311c).
- **Detector tells planted by their own generators.** Harmonia AF F1-F5 detectors read exactly the tell
  their own generators plant (roles/Harmonia/qualification/h0h5/adversarial_fixtures.py). Only F4 and
  F7-F9 have clean twins. [crawl]

Who caught them: mostly later adversarial self-audit or a sibling seat, with lags of 3 days (zeros) to
6 weeks (oracle) to never (spectral_bsd). No pre-registered test asks "can the label be read off the
input?".

Recurrence: at least 9 independent instances across Charon, Harmonia, Coeus, Ergon/Theseus, Aporia.

## T02. Self-verdicting and caller-asserted verdicts (no detector in the kill path) -- FP

Definition: the component that generates or asserts a claim also writes its verdict, or the
"falsifier" checks a number supplied by the claimant.

Instances:
- **Generators verdict their own records.** 99.98% (658,302,367 / 658,454,531) of Theseus records were
  verdicted by the generator that authored them, e.g.
  theseus/generators/a1_catalog_cross_product.py:182-183.
  - Harmonia D emission-path census (roles/Harmonia/audits/AUDIT_20260819_detector_band.md, 7ad201fb3).
- **Falsification oracle over a caller-supplied number.** sigma_kernel/omega_oracle.py:39-69 FALSIFY
  compares a caller-supplied true_mean with the hypothesis.
  - Its only non-demo caller (a149_obstruction.py:342) supplies its own rate. [crawl, verified]
- **Synthetic CLEAR verdict written by SQL.** prometheus_math/discovery_pipeline.py ~478-510 UPDATEs a
  synthetic CLEAR into the claims table, bypassing FALSIFY, then PROMOTEs. [crawl, verified]
- **Promotion without re-execution.** sigma_kernel/sigma_kernel.py:822 PROMOTE only checks that a
  verdict exists and is not BLOCK, and never re-runs the battery.
  - Its provenance check accepts any 64-char string in the evidence.
  - Flagged by Harmonia A (AUDIT_20260622_program_stall_map_of_disagreement.md, 3e13f736c). The
    prescribed re-execute audit was not found executed.
- **Promotion on record shape.** Theseus promoted 2,351 records with training_weight >= 0.6.
  - 1,991 of them were parity tautologies (1321ba7c3).
  - The count is a "formula fossil" that the current code cannot reproduce (promotion replay b092b86ac,
    1f86b2590).
- **Self-declared independence.** claim_record's independent_of_generator is an author-set flag
  (d36f8c3fe). The triangulation independence_class is a declared enum
  (sigma_kernel/method_spec.py:286).

Consequence: everything downstream of the May substrate is class-relative at best. Harmonia's own
reading is that Theseus nulls are "sound within 33 claim kinds, not detector blindness". That is a
statement about the generators, not about mathematics.

## T03. Controls and guards that cannot fail (cosmetic safeguards) -- FP and FN

Definition: a control, guard, ablation or gate whose outcome is fixed by construction. It certifies
every input the same way.

FP side (a control that always passes):
- **Hard-coded PASS in tallies.**
  - charon/scripts/bsd_battery.py:213 hard-codes "verdict": "PASS" inside the "5/5 PASS" tally.
  - charon/scripts/abc_battery.py:237 and :336 do the same inside "7/7 PASS". [crawl, verified]
- **Hard-coded negative control.** roles/Harmonia/qualification/h0h5/h1h0_phase2_analysis.py returns
  its NEGATIVE control as "pass": True. [crawl]
- **Ablations that force silence.** c1_hostile_adjudication.py:318-321, :443-446 and the
  audit_primitives `chk` replace a detector's output with [] / False to "show" that disabling the
  detector lets the cheat escape. The 5/5 ablation headline cannot fail. [crawl]
- **Indeterminate counted as pass.**
  - qualification/t3_strict_cutover_rehearsal.py:85-86 counts "n/a" as pass, contradicting
    SESSION_AFFINITY_QUALIFICATION_SPEC_2026-09-05.md. [crawl]
  - harm56_map.py authorises replication when its controls are None. Disclosed, not fixed.
- **Vacuous cheat controls.**
  - Nyx hypothesis_shrinker P-a5: all() over an empty generator.
  - Nyx SPIN indicator: matched pan's summary line on every run.
  - Particles 002: "V == 0.0" on a float variance of 1e-27. Harmonia replaced it (3db0b83c7).
- **Negative control at numerical zero.** The Proteus V0.5 negative control cannot fail: the reference
  |J| is 2.168e-19 (RULING_PROTEUS_CURRENT_INSTRUMENT_AND_R4_2026-09-18.md).
- **Gate whose inputs were identical by construction.** leakage_gate.json read PASS while its inputs
  were arm-identical by construction (charon/probe/RULINGS_2026-08-25.md item 5).
- **Zero-variance gate.** ATK-017: 200/200 tasks had one distinct payload, and 12 PASS rows had
  p05 == p95 == max.

FN side (a detector that can never fire, read as "nothing there"):
- **Nemesis blind_spot.** The predicate "all tools wrong" fired 0 times in 3,013 cycles over 150-294
  tools and was read as "no blind spots" (agents/nemesis/src/evaluator.py).
  - Caught by Aporia P69 (engine/ledger/AGENT_AUTOPSIES.jsonl) and by Nemesis 09-11.
- **Constant correlation.** Pollux corr_raw = Spearman(sorted, sorted) is identically 1
  (engine/necropolis/dossiers/pollux_evidence/README.md).
- **Dead field.** drip_coldband truncation_rate read completion_tokens, a field its writer never
  writes, so the rate was identically 0 (charon/probe/ADDENDUM_2026-08-23_drip_truncation.md,
  37483e68b). Charon withdrew its own "met".
- **Pronoia detectors.** zero_output (len(stdout) < 20) could not fire, knowledge_growth had no
  predicate, and the health line read "HEALTHY ... Errors: 0" (roles/base-role/MONITORS.md Pronoia
  row).
- **Wrong-signature call reads as UNTESTED.** harmonia/src/validate.py:221 calls the battery with the
  wrong signature, so a TypeError always yields "UNTESTED". The TT-engine bonds were never
  battery-tested through it. [crawl, verified]
- **Battery runs only on synthetic fixtures.** attacks/preflight.py data checks C1-C5 run only in
  --selftest on synthetic fixtures. `--ledgers` is documented and not implemented. [crawl]
- **Vacuous pass when inputs move.** attacks/probes/atk015_unsourced_verdict.py does
  `if not verdict.exists(): continue` over 3 hard-coded pairs, so it prints "Defect ABSENT" if they
  move. [crawl]

Who caught them: mostly nobody until a later archaeology pass. The base role's own rule ("a guard that
cannot fire") is prose. archaeon/tests/test_base_role.py checks ASCII, banners and gitignore, not
whether any control can fail.

## T04. Positive control absent, aimed beside the instrument, or degenerate (ruler unable to detect positive control) -- FN, and FP by implication

Definition: the instrument was never shown able to output the class it is used to rule on.

Instances:
- **"Known truths calibrate the pipeline" was aimed beside the instrument.**
  - cartography/shared/scripts/known_truth_battery.py ("38/39 validated ... pipeline TRUSTWORTHY",
    12f4403aa; later "180/180") imports no battery module and runs its own permutation test on
    theorem-strength effects. [crawl, verified]
  - The F1-F14 kill battery it is cited as calibrating never had a planted-signal control.
  - The only planted-signal calibration (1cc2e0f3d) covers battery_v2 F24, single seed:
    - it missed eta2 = 0.01;
    - it underestimated 0.10-0.14 by ~30%;
    - it gave a false positive on random-walk half-splits.
- **Data consistency mislabelled as ruler calibration.** The "3.8M objects at 100.000%"
  (harmonia/results/mass_calibration.json, 73b4d453a) checks database consistency against theorems,
  never runs an F-test, and its script is uncommitted. It was still cited as the program's unique asset
  on 2026-08-12.
- **Novelty detector never shown able to say UNFAMILIAR.** Hecate's gravity detector had no
  coherent-unfamiliar control (hecate/gravity/controls_v1.json).
  - It called 0/32 mechanically alien rules UNFAMILIAR (autopsy e4a05ba3b).
  - "Zero UNFAMILIAR in 399 items" was reported as a result (d80c5cc4c).
- **Planted signal missed.** The Erebos pair-aware null detected 0/3 planted partner-conditioned
  linkages at N = 699 (Necropolis 22a155201).
  - Its earlier "underdetermined" verdict was a property of the instrument. Later readings turned it
    into "realized ~0".
- **Search loop never shown able to find a known positive.** The withheld benchmark recovered 0/36 in
  3,000 episodes (prometheus_math/WITHHELD_BENCHMARK_RESULTS.md).
- **Metric ranks garbage above life.** The ASAL CLIP open-endedness score ranks garbage (0.817) above
  living Lenia (0.847) (44d109558). Coherent genuine rollouts land in the garbage band (850fec325).
- **Positive band from an unchecked model.** Nyx particles 001's positive band [10, 1000] came from an
  unchecked model; the instrument measured 5,463 (RULING_PARTICLES_ESSTRIGGER_001_2026-09-17.md).
- **Only the dumbest cheat tested.**
  - Hypatia CHEAT-2 is a 1-step payload. A 2-step payload passes G1-G7 by code inspection
    (roles/Hypatia/science/season1/verify_ladder.py G5 L143-160, G6 L178-205). [crawl]
  - Hecate's gravity calibration used free-prose controls while the arm items were field-formatted. A
    two-rule lexical labeller passes the gate (roles/Hecate/harvest_w2/AUDIT_W_gravity_gate.md).
- **Positives without a false-alarm denominator.** The Techne #424 canary harness was scored on planted
  positives only, with no false-alarm denominator (ATK-020). Charon rejected it before build.
- **Attack operators never validated.** Nemesis 1.0's 12 metamorphic relations were never checked
  against a planted broken tool (NEM-04 open).
  - The Campaign-6 planted blind fixtures assigned to Nemesis have no delivery on record.
- **Auditor never measured.** No planted-defect calibration of any auditor (Harmonia, Elenchus,
  Charon) exists. Elenchus's one plant (two misattributed arXiv ids, ffee58f3a) was on day one and only
  weakly blinded.

Recurrence: this is the most common class in the territory. Of 146 distinct rulers in
ruler_inventory.jsonl, 60 records say detectability was NOT demonstrated, 56 PARTIAL (mostly
synthetic-only), and 30 YES.

## T05. Invalid null, missing chance floor, or degenerate null -- FP mostly

Definition: the comparison distribution does not represent "nothing is happening", or no "what nothing
scores" figure is published beside the headline.

Instances:
- **Wrong reference ensemble.**
  - F011 compared against bulk GUE, but the excised SO(even) Duenez-HKMS ensemble applies
    (cartography/docs/dhkms_prediction_F011_rank0_analysis.md).
  - Charon still declared it DURABLE four days after Aporia's downgrade. The residual eps_0 22.90% was
    never independently replicated (Track D deferred, 2651570bb).
- **Wrong size.** charon/src/rmt_simulation.py N_MATRIX = 60 against an effective N ~1.3 produced
  "sign inversion beyond RMT".
- **Degenerate null mapped to certainty.** harmonia/nulls/*.py returns z = inf -> DURABLE when null
  sd < 1e-12.
  - F011 class_size z_block went from 10.46 to 4.19 once this was spotted (812c34221).
  - Fixed in prose (null_protocol v1.1), not in code.
- **Floor that was a ceiling.** The chance "floor" 2p(1-p) given to Charon is a ceiling by Jensen's
  inequality. Withdrawn 1be87a0fe.
- **No chance floor.**
  - Nemesis 1.0 published no constant responder. "Not enough information" is correct on 62/92 tasks,
    so a constant string scores 0.674 (agents/nemesis/adversarial/adversarial_results.jsonl).
  - The NEM-14 census found 25 of 37 tier-1 scoring instruments publish no chance floor
    (roles/Nemesis/science/census/ATTACK_SURFACE.md).
- **Marginals not preserved.** falsification/test_12 nulls LLM-populated, marginal-heavy matrices
  against uniform random matrices.
- **Null that reproduces the signature.** The R7 F-null build #1 manufactured the very signature it was
  meant to remove (classifier 0.662). The topic-preserving null was identical to the treatment
  (charon/probe/R7_CONSTRUCTION_2026-08-16.md).
- **Null aimed at the weak comparison.** The weak per-plugin baseline was nulled, while the
  load-bearing pair-aware comparison stayed un-nulled (d7120eb5a).
- **Invalid null found only via literature.** "Random eviction" is distribution matching, a strong
  structured policy (Artemis roles/Artemis/backlog/prior_art/PA_memory_and_sagacity.md W08).
- **Survivors on their chance floor.** 84/84 non-promoted Theseus survivors re-evaluate TRUE at 45.9%
  against a 46.1% random-pairing null (RETRODICTIONS_20260819_harmonia_C.md).
- **Different estimator for null and observed.** harmonia/src/tensor_falsify.py F1 scores the null with
  KosmosCoupling while scoring the observed value with the passed scorer. [crawl]

## T06. Tautology and algebraic identity passing as a finding -- FP

Definition: the "relationship" is a definition, an identity, or a shared term. Permutation and block
nulls preserve definitions, so they cannot detect it.

Instances:
- **Definitional identities.**
  - F043 BSD-Sha anticorrelation, z_block = -348: declared durable (9fc257064), then retracted the same
    evening (df20f900c) after an EXTERNAL frontier-model review, because log A contains -log Sha by
    definition.
  - Also F028 Szpiro x Faltings, and F003 BSD identity.
- **Shared term.** H40 Szpiro-Faltings rho = 0.969 was 97% a shared log|disc| term (eb6d31dfe). The
  Harmonia auditor's log|Delta| covariate collapsed it to 0.13 (db37c2c2a).
- **Same L-function compared with itself.** Z.4 bridge-pair separability compared only shared slots,
  so an elliptic curve and its modular form (same L-function) collapsed to distance 0. It was counted
  as PASS and praised by the council.
- **Answer derived from the tested quantity.** charon/scripts/bsd_at_scale.py 1646/1646 uses LMFDB
  sha_an, plausibly derived from the BSD quotient. [code-inferred, not verified]
- **Reciprocal invariant as cross-validation.** prometheus_math/discovery_pipeline.py F11
  "cross-validation" compares M(p) with M(reversed p), which are equal for every polynomial. F9 returns
  True unconditionally. [crawl, verified]
- **Possible tautology never re-checked.** Kairos NF backbone (object-keyed z = 3.64, 8676d635b)
  correlates NF discriminant with Artin conductor. This is an algebraic-tautology candidate that was
  never re-checked. [code-inferred]

Practice that emerged: Pattern 30 / null_protocol v1.1 (db37c2c2a) requires X to be written in atomic
variables before testing. Harmonia AP-1.1.0 has executable forms of related checks.

## T07. Artifacts of normalisation, construction, catalogue or sampling frame read as structure -- FP

Definition: the "signal" is a property of how the data or the world was built, sampled or scaled.

Instances:
- **Scale read as structure.** Charon's spectral tail "RESIDUAL SURVIVES" (charon/docs/north_star.md,
  04-04) went to ~0 under its own mean-spacing normalisation on 04-05
  (charon/docs/journal_2026-04-05_finale.md).
  - The collapse documents entered git from a stash only on 08-18 (cf2438a5d).
  - north_star.md is unmarked at HEAD.
- **Catalogue construction read as mathematics.** Erebos Salem moderation PROMOTED 41.7x null, and the
  M = 1.26 "phase transition" is the Mossinghoff catalogue's enumeration band
  (pivot/erebos_finding_reclassification_2026-05-27.md: 0 mathematical findings).
- **Sampling frame read as structure.**
  - F044 rank-4 disc = conductor is an artifact of LMFDB high-conductor sourcing.
  - F014 used an ORDER BY disc_abs biased sample.
  - Pooled-mixture artifacts F013, F010, F015 (Pattern 20).
- **Instrument sampling read as a finding.** Charon Hecate v0.1 read theseus/corpus alphabetically
  with a 5,000-record cap. The first (monoculture) batch exhausted the cap, and the result was framed
  as "Theseus corpus is a monoculture". Techne caught it within hours (8b373fa9d).
- **Signals live where worlds are degenerate.** Hecate Pass 4: 5/9 valid worlds under 0.05 core-min
  SIGNAL vs 0/16 above, p 0.012 two-sided. All 5 kills were identities, ties, textbook bounds or
  degenerate dynamics (roles/Hecate/harvest_w2/INV_N_cheap_world_signals.md).
- **Signal passes by construction.** Both Hecate round-3 SIGNALs pass by construction: the spec-named
  simpler alternative scores 1.000 (INV_J_v2_clause_reachability.md).
- **Mutation inheritance read as contrast.** Theseus v2 sweep: 198/1,068 groups with F2 contrast, ~91%
  explained by mutation inheritance; 0/96 under uniform sampling (c59d782de).
- **Synthetic structure read as validation.** Erebos Sprint-1 10/10 PASS (c922a6f3c) ran on synthetic
  data that baked in the tested structure. Phase 3.0 then found 0/13 deltas against a counter.
- **Finite data against asymptotic claims.** "0/253K violations SURVIVES" (H80) and "Lehmer PROMOTED
  +2" set finite databases against asymptotic claims. The disagreement atlas "Type B" 27,279 candidate
  discoveries are graph incompleteness (charon/reports/type_b_characterization.md).

## T08. Baseline omitted / cheap predictor outperforms the organism -- FP

Definition: the headline compares against a weak or absent baseline, and a trivial predictor matches
or beats the system.

Instances:
- **Lift over random with nothing to learn.** Six-domain RL "transport" lifts of +1.37x..+18x over
  uniform random. The synthetic null gave REINFORCE 4.91% vs random 4.84%, and a V2 5.8x lift with
  nothing to learn (prometheus_math/MODAL_COLLAPSE_SYNTHETIC_RESULTS.md). Retracted 7339269a1.
- **Constant answer beats the tools.** Nemesis 1.0: a constant answer beats 120 of 122
  full-coverage tools (T05).
  - [crawl] The "292 of 294" headline is partly a denominator artifact: 172 tools were scored on fewer
    than 92 tasks.
- **Lookup table passes the novelty rule.** Hecate's NOVELTY_DETECTOR_VALIDATED rule is passed by
  committed lookup-table baselines (AUC 0.844-0.852) (Harmonia RULER_QUALITY_2026-09-30.md s2, rule
  F3).
- **Unlike subsets compared.** "Affine baseline 0.44 beats Claude 0.33" compared 5 vs 8 systems on
  different metrics; like-for-like it is 0.51 vs 0.49 (Hecate CORRECTIONS K2).
- **Coverage mistaken for learning.** Alien "learned 28/32" was mostly table coverage: pooled 0.50 vs a
  coverage oracle at 0.58 (INV_E_induction_vs_coverage.md).
- **Forecasts worse than a constant.** Artemis priority forecasts scored worse than a constant (Brier
  0.470 vs 0.391). Artemis withdrew them itself (roles/Artemis/selftest/RESULT.md).

## T09. Selection effects -- FP and FN

Definition: what got measured was chosen by something correlated with the outcome. The chooser may be
the cost of a world, its position in a list, what a host can run, which executor domain accepts it, or
which draw was highest.

FP side:
- **Winner's curse.** SE-1b "d = 0.60, p = 0.0005" was the highest of 12 draws; the mean was
  d = +0.37 (retracted 28d58afbb).
- **Sampling an extremum.** Harmonia-A soak P4 dropped the 96 rows carrying '97' and manufactured a
  trap hit (64bba4111).
- **Small-n extremes steered sampling.** 11 of 16 concepts got 2.5x Nous sampling weight from survival
  rates on n <= 5 (Coeus FINDINGS F2, F6).
- **Fit in-sample, used live.** Coeus's 1,009 pair synergies were fit on 352 positives (in-sample AUC
  0.887, no holdout) and wired into _forge_priority.

FN side:
- **Host runnability decides which mechanisms get verdicts.** M3 has no docker, WSL2 or C compiler, so
  only pure-Python mechanisms reached a verdict. The gzip pilot was never adjudicated, and 100+
  C/Fortran fossils have no route to a verdict (roles/Nyx/STATUS.md).
- **Executor domain shrinks the search.** Techne's Lenia port refused 650 of 1,045 preregistered ASAL
  draws. The verdict was narrowed to SUPPORTED_ON_EXECUTED_SUBSET (Harmonia STANDING_RULES A4).
- **List position decides which mechanisms get a world.** 126/243 Hecate mechanisms were never placed in
  any world. Placement was predicted by list position (M1-M3 0.83 vs M4+ 0.39), not by strangeness
  (INV_H_world_specification_filter.md).
- **Eligibility window misread as rejection.** Skopos judged 1 of 448 eligible entities. 99.78% were
  never observed, yet the threads were labelled STARVING (agents/skopos/src/skopos.py:130-136).
- **Undisclosed corpus boundary.** Hecate's corpus = git-tracked Nous runs only. 11 gitignored runs
  (4,187 responses) would select a different 16 (roles/Hecate/harvest_w2/AUDIT_Z5_provenance.md).

## T10. Statistical malpractice inside gates (insufficient power, multiple testing, non-independence) -- FP and FN

Instances:
- **Underpowered kills (FN).**
  - OQ1 spectral tail killed at ~1,000 curves per bin for rho ~ -0.07.
  - F010 killed at n = 51.
  - F3 |d| >= 0.2 and F11 > 55% kill small real biases by design.
  - Particles claim (c) needs ~11,700 seeds per arm and ran at 50, then 400.
- **Underpowered positives (FP).** CM gradient inversion at n = 18, retracted at n = 2,134.
  "V-CM-Scaling NEW LAW" rested on 12 points.
- **Unattainable or defaulted multiple-testing correction.**
  cartography/shared/scripts/falsification_battery.py F6 takes p from F1 (floor ~1e-4) with a
  caller-supplied n_hypotheses, default 3.
  - With an honest n (18K hypotheses in research memory) it can never pass.
  - With the default it barely corrects. [crawl]
- **Skipped tests read as survival.** F4, F7, F8 and F12-F14 SKIP without optional inputs, and
  "survives battery" counts only non-skipped tests. [crawl]
- **Row-order dependence.** F12-F14 pair values_a[i] with values_b[i] for unpaired groups, so verdicts
  depend on row order. [crawl]
- **Pseudo-replication.** survivor_kill_protocol.py does no isogeny-class dedup: p = 1.89e-86 on
  n = 31,073. [crawl]
- **Correlated tests counted as independent.** F1, F9 and F6 share one permutation null, so "8/8
  survived" overstates independence. [code-inferred]
- **Anti-conservative gate library.** roles/Harmonia qualification_rules.py:
  - t_crit maps df to the next larger tabulated df;
  - the Bonferroni quantile is wrong for 3 or more primaries;
  - lane_gate and decide() disagree on eligibility at 6 blocks. [crawl, lines 229-282 read]
- **Tie handling and float thresholds.**
  - Lexis D001-07: 57/572 = 0.0997 with ties in vs 0.1018 with ties out (INDETERMINATE_BY_RULE_GAP,
    5702e9fa3).
  - Hecate alien H3: 0.2 - 0.1 = 0.0999... < 0.10 in floating point. An exact shadow evaluator was
    built (264854c4b).
- **Estimated mean frozen as an exact cutoff.** ASAL garbage-mean 0.8167 from 5 seeds was used as a hard
  band edge, and I0 failed on a 1.1 sd margin (rule A7).

## T11. Post-hoc interpretation and post-exposure changes -- FP

Instances:
- **Amendment after seeing the outcome.** E-003 BEE leg: a dry run showed ALTERED, and 17 minutes later
  amendment C4.2 (567762a15) removed that route. The verdict became VALIDATED.
  - The amendment was omitted from the post-exposure list.
  - Both Fabric reviews were instructed to accept it.
  - Caught by Harmonia SAMPLE2 H (cffcfc64b); owner errata d06059735.
- **Seen rows offered as predictions.** Nyx POET 001: four rows scouted before freeze were offered as
  predictions; predictions_tested = 0 (RULING_MECH_POET_NOVELTY_ESTIMATOR_001_2026-09-30.md).
- **Freeze not provable.**
  - Ananke W-O PLAN.md was first committed with its results (93e2e544b).
  - Nestor X-MAT pilot began ~10 minutes before the freeze, undisclosed.
- **Claim strengthened before the test.** falsification/prompt_falsification_battery.md says "UPDATE
  BEFORE RUNNING" and strengthens claims for tests 4, 7 and 10 before execution.
- **Threshold fitted to the output.** The Moros convergence threshold was lowered from 0.40 to 0.25
  after 29 ticks never exceeded 0.190 (charon/agents/moros/daemon.py:48-56).
- **Frozen battery silently extended.** The battery was declared "FROZEN at 25 tests", then F25-F32 were
  added on 04-12 (40435dd7a).
- **Operationalisation moved into notes.** Hecate W6 "stays at chance" became |mean ARI| <= 0.1 in
  NOTES.md.
- **Replication agents told the expected sign.** Prompts in charon/TheFive told five replication agents
  "Negative = tighter (our phenomenon)".
- **Paper before control.** Spectral-tail paper drafts v1-v3 were written before the mean-spacing test.
- **Gates retuned after seeing output.** Techne's fossil smoke gates were widened after seeing output
  (minpack, twice). The Spacewar! behaviour gate was judged by eye (17443dcc8 -> feab5d00e).
- **Frozen gate overridden by narrative.** evidence_wiki/FROZEN.md G21 read false and was judged "an
  instrumentation artifact"; V3 was accepted anyway.
- **Kill and reversal on the same instrument.** Kairos Kill 1 and its reversal Kill 2 used the same
  battery and rows in one session.

## T12. Unreachable design, structural zero, vacuous reading (FN; the "null that was never a test")

Definition: given its inputs, the design could not return the outcome it is reported as not finding.

Instances:
- **Founder snapshot cannot return SURVIVES.** Bellerophon E-BEL-REPL-01's K3 founder snapshot cannot
  return SURVIVES, because content turns over in every arm. Harmonia first rated it SUPPORTED and missed
  this; correction C-2 (d3f99cfdc).
- **Fixed seeds void conditions in advance.** Tyche H1/H6: fixed seeds made P3/P4/P6 VOID before any
  generation (RULER_QUALITY_2026-09-30 s1; UNREACHABLE_BY_DESIGN bdeba9865).
- **VACUOUS_READINGS V-001..V-008.**
  - C3-2 H2 STRUCTURALLY_VOID (f = 0.000 everywhere).
  - H1 relevance at 3 bits cannot differ at any n.
  - H5 reach equals a random permutation.
  - Particles needs ~11,700 seeds.
  - The register was created only 09-18, though V-001/V-002 had been asked for on 09-10.
- **Unattainable thresholds or empty inputs.**
  - Techne E1: every arm n_pairs = 0 (468a1f9ba).
  - Cartography TX-003 needs 12/23 where the maximum is 7.
  - LIM-003 fix made hole kills impossible (683467597).
- **Structural zero refused.** Charon M-004 targeted archives with 0/35,395,316 'unknown_kind' rows.
  Charon refused to publish the structural zero (charon/probe/VERDICT_M004_2026-08-18.md, 2ea9b10cb).
- **Six cells, four conditions.** campaign_h1h0.py:356-358 gives S00 and S10 identical inputs.
- **Family cannot reach the signature.** A148 walks reach max neg_x = 3 while the signature needs 4.
- **Detector cannot represent the target.** Hecate's UNFAMILIAR is unreachable for any finite rule
  (universal-formalism absorption; hecate/autopsy/AUTOPSY.md Part B C6).
- **Deciding clause unattainable.** The Hecate W3 pilot repair made the deciding clause unattainable
  for the positive control and the treatment alike (CORRECTIONS K4).

Practice that emerged: Harmonia STANDING_RULES F1 (reachability first, including evolving baselines),
VACUOUS_READINGS and the label vocabulary NOTHING_COULD_FIRE / STRUCTURALLY_VOID / UNREACHABLE_BY_DESIGN
/ INDETERMINATE_BY_RULE_GAP. This is the most important FN-side doctrine in the repository. Its
reach-back to April-era kills has not been run.

## T13. Task, world or organism too weak (FN)

Instances:
- **World-blind specimens.** 48/64 (75%) of SFE menagerie specimens are WORLD-BLIND, and composition
  destroys world-coupling in 94% of cases (BOUNDARY_DEPTH_PACKET_01_2026-09-05.txt).
- **Saturated or too-small worlds.**
  - The Hecate C3 entropy observable saturates by T ~ 6-9.
  - The 71b6 world is 4 words.
  - Selection favoured the cheapest worlds (T07).
- **Nothing in the region of interest.** Ensorain FR-081: 0/181 admitted worlds have lifetime <= 600,
  so the learning-time ratio is unobservable (roles/Artemis/dispatch/D004/RESULT.md D004-09).
- **Search loop with no reach.** RL modal collapse rediscovered 0/36 withheld targets.
- **Lesions blind to part of the mechanism.** Ares W4 node ablation never removes output nodes, which
  hides a third of the carrier ring (roles/Nyx/reports/ARES_W4_READING_2026-09-25.md).
- **Pressures never testable.** Nyx pressures and organs had no substrate owner or consumer (Vivarium
  #182, Archaeon #200 INTERFACE_INSUFFICIENT). They were never shown false; they were never testable.
- **Questions with no answer to find.** The Hypatia premise had 532/537 catalogue problems open.

## T14. Classifier and label failure (scoring proxy mistaken for mechanism) -- FP and FN

Definition: a label, keyword, LLM judgement or uncalibrated class rule stands in for the property it
names.

Instances:
- **Keyword relevance scorer.** Eos: a content-free string of its own keywords scored 100/100 and a
  relevant item 8/100. It promoted a pavement skid-resistance paper (roles/Eos/intake/FIRST_SEASON_
  2026-09-11.md). In use ~4 months.
- **Self-report counted as novelty.** Nous assess_novelty counts "novel"/"original" in the generator's
  own answer: 5,462/5,918 labelled "novel" (agents/nous/src/scorer.py).
- **Class rule from one rollout.** The ASAL class rule was calibrated on one Orbium rollout, leaving
  47/105 crossers UNCLASSIFIED; the disjoint calibration has been owed since 09-18.
- **Intermediate class absorbs the signal.** In Hecate's COMPOSITE sink the gate counted 2 composites
  called FAMILIAR as "2/2 detected" (hecate/gravity/run.py:83-94).
- **Regularity read as law.** Claude said RULE on 19/30 incompressible nulls (REPORT_pilot s2).
- **Naming credited as mechanism.** The alien analogy classifier credits naming a formalism
  (CORRECTIONS K8, K11).
- **Proxy scored as target.** The cartography tagger placed 1.9% correctly (146917ac4). The H27 proxy
  scored as root number still reads SURVIVES at HEAD
  (charon/data/frontier_batch_20260417_summary.json).
- **Shape scored as content.** Theseus yield_score / info_density is a fixed lookup on verdict strings.
- **Label-for-property selection.** Hypatia A-2 load_bearing_unit chose prescriptions over
  observations.
- **Same model twice read as stability.** HARM-55/56 "observer stable" is the same CLIP weights in two
  ports.

## T15. Novelty conflation: absence of prior-art detection treated as novelty -- FP for novelty, FN for prior art

Definition: "unfamiliar to Prometheus, or to the model" is treated as "new to science", or "not found
by this search" as "no precedent". Also the reverse: known mathematics treated as an anomaly until
literature arrived.

Instances:
- **No external search, by prompt.** Hecate never searched any external corpus.
  - Every prompt forbids search (hecate/programs/_prompts/pass0_3_v1.md:29).
  - HECATE-14 never ran.
  - 2/396 hypotheses carry a prior-art label, named from model memory with no citation
    (hecate/pass4_report.py:79).
- **Same-model familiarity.** The generator, detector, matcher and subject are all Claude, so
  "familiar" means familiar to Claude (hecate/meta/REPORT_v1.md header).
- **Network errors counted as novelty.** prometheus_math/catalog_consistency.py counts LMFDB/OEIS/arXiv
  network errors as catalogue misses, so absence of a match is read as novelty.
- **Circular catalogue check.** Techne's five-catalogue novelty check: Mossinghoff and
  lehmer_literature share a curator, and 16 arXiv probe rows were promoted into the catalogue.
- **Unlogged "no precedent".** Artemis "genuinely unexplored" U-lists rest on one pass of unlogged web
  queries by Claude-family delegates, with no recall measurement.
- **Literature presence used as verification.** falsification/independent_verification.md (March)
  "verified" operator-to-technique predictions by finding that the technique exists. That is
  retrodiction.
- **Known mathematics read as anomaly (the reverse error).**
  - F011 (excised ensemble).
  - F042 (CM -27).
  - Rank-dependent zero repulsion in harmonia/paper/spectral_bsd.md.
  - Artemis's "random eviction" null; H-D3-33 is a known result (Isele and Cosgun 2018).
- **Doctrine pressure.** aporia/doctrine/critical_memories.md HARD-2 (2026-05-06, boot-mandatory) tells
  agents to excise "you should validate by comparing to [existing thing]" as a gravitational-well
  reflex. [interpretive]
- **The one designed fix was never built.** Hecate's mechanical template-reducibility ruler was
  withdrawn under CWO-B before start (roles/Hecate/journal/2026-09-30.md).

## T16. Mechanism analysis that is description, not measurement -- FP for mechanism claims, FN for real mechanisms

Instances:
- **Atlas rests on reading, not running.** Nyx atlas: 549 organ fragments.
  - 546 rest on SOURCE_READ/METADATA; 3 on execution or intervention.
  - 0 of 10,431 coverage cells MEASURED.
  - Portability YES for 533/549, untested.
  - Ablation NOT_RUN for 546 (nyx/atlas/fossils/*.json; nyx/atlas/out/ATLAS_COVERAGE.json).
  - Nyx's own summary: "READ layer ... NO MEASURED layer".
- **Independence controls designed and never run.** Blind cut and second Chopper: n = 0
  (nyx/atlas/out/BLIND_CUT_COMPARISON.json).
- **Transplant never tested.** 0 mechanisms SURVIVED_TRANSPLANT; one transplant offered, never accepted
  (nyx/atlas/gates/MECHANISMS.json). The MKW-1 wager was never frozen.
- **Causal labels on a regression.** Coeus "causal discovery" was Lasso, and "interventional" a raw
  rate difference (agents/coeus/src/causal_graph.py:530-577). The README advertised
  NOTEARS/GES/LiNGAM/FCI/DAGMA.
- **Packet validators check form only.** Techne's FOSSIL_PACKET validator accepts an all-zero tree
  hash, a fabricated world id, evidence "x" and README.md as a receipt (techne/fossils/packet.py;
  in-memory probe by this crawl). [crawl]
- **Bytes verified, not anatomy.** "bodies MATCH" receipts verify bytes, not anatomy
  (nyx/atlas/samples/stageA_bodies_*.json).
- **Hidden machinery in a "null".** lean_simp c23 closed anyway because `simp only` always loads
  eq_self (KNIFE K5/K6).
- **Mechanism story before measurement.** MVG K7 was attributed to detector breadth; it was actually a
  bounded outcome (withdrawn dacbff9f5).

## T17. Improper independence (shared implementation, shared model, shared author, shared brief) -- FP

Definition: "independent" checks share code, model family, data, prompt, or authorship with the thing
they check.

Instances:
- **Same model family everywhere.** Nearly every generator, implementer, scorer, attacker, auditor and
  reviewer in the territory is a Claude-family session.
  - Fabric reviewers, Harmonia audit agents, Hecate detector and subject, Artemis delegates, Eos and
    Nemesis.
  - "Independent" mostly means "fresh session".
  - The only cross-family instrument found, B-prime (gemini-3.6-flash, bb2037496, 2026-08-12), was
    never graded.
- **Auditor imports the producer, and the producer imports the auditor.**
  - harmonia science/d3v2_calibration.py imports archaeon.synth, f_cdf and the detector (ca0dd0fd7).
  - archaeon/producer/exchangeability_table.py imports Harmonia's exchangeability.py (7017dc79e).
  - Daedalus commits the contract Harmonia's gate pins.
- **Attacker's validator is a member of the population under test.** Nemesis
  agents/nemesis/src/validators.py:17-24 filters ground truth with the forge's execution_evaluator,
  which is one of the 294 tools scored.
  - Seeds came from the same trap generator as the static battery. [crawl]
- **One prompt to four vendors.** Charon's four-vendor council (charon/src/fire_council.py) sent one
  prompt and one system message, with one same-family member.
  - "Every council round demanded tests that confirmed the narrative. None demanded the mean-spacing
    test that killed it" (charon/docs/retrospective.md lesson 7).
- **Closed loop generating and falsifying.** Charon swarm: Erebos composes claims, and Stygian
  falsifies them with loaders from the same commits. The Substrate-Tester was a Techne instance testing
  Techne's kernel.
- **Kill authority over its own instruments.** Charon authored F-null, R7, the band rule and preflight,
  then ruled on runs that used them (conflict stated; mitigated by Aporia re-run 71403839d).
- **Reviewers briefed by the audited party.** Fabric reviewers were briefed to accept E-003's C4.2.
- **Same author writes and grades.**
  - Hypatia season 1: the same session wrote the gate, the ladders and the controls, and named the
    files by expected outcome.
  - Kairos claim_lint fixtures were written with the code in the same commit.
  - Pheme's corpus, labels and gate are by one instance.
- **Observer stability measured on one model.** HARM-56 compared two ports of one CLIP model.

Most independent signals actually observed:
- external frontier-model review (F043);
- the operator's ASAL review;
- external literature (F011, Artemis);
- Techne's batch check of the Charon swarm;
- Aporia's re-run of Charon C1/C2 from another worktree;
- the audited seat's own verification (Hecate K1-K3, Tyche #1047);
- Necropolis Keeper (non-author) controls.

## T18. Provenance failures -- FP and FN

Where provenance FAILED:
- **Hashes of host bytes, not git blobs.**
  - HARM-55/56 hashes were computed on CRLF host files (ERRATUM E-1, 646cbcda8), a recurrence of the
    09-11 Archaeon manifest defect.
  - [crawl] PAYLOAD_MANIFEST_ID for the gzip, spacewar and lisp packets is the sha256 of the CRLF copy
    of UPSTREAM_HASHES.txt (gzip d36d57f2 vs LF blob 86ba4fe2), while asal uses LF.
- **Output file overwrote its input.** On a case-insensitive filesystem, CALIBRATION_v1.json
  overwrote calibration_v1.json. Commit b15a475b8 claimed "+14 controls" that were never committed
  (Hecate CORRECTIONS K3; the auditor saw only a path issue).
- **Gitignored outputs consumed downstream.**
  - Skopos reports were ignored by .gitignore and still read by Metis (agents/metis/src/metis.py:94-103).
  - Hypatia rows were caught by **/results/ (D-30 allowlist after four instances).
  - Swarm ledgers were lost.
  - Note for the Phase 3 merge: docs/* is also gitignored (.gitignore:292). This package is
    force-added.
- **Stashes and destroyed files.**
  - The April-5 collapse documents sat in a stash for more than 3 months (cf2438a5d).
  - The 2026-04-22 negative-control data are absent from all branches.
  - The ceiling_v0 preregistered SPEC was destroyed and reconstructed from transcript.
  - ATK-015 ledgers were destroyed by stash -u + drop and recovered by git fsck.
- **Scripts behind headline numbers never committed.** The mass-calibration script, RULER_QUALITY sims
  (scratchpad), and the Nemesis log and 3,014 reports.
- **Corrections not propagated.**
  - north_star.md, spectral_tail_paper.md and the H27 summary are stale at HEAD.
  - The 127,000x ratio (prometheus_math/NATIVE_KILL_VECTOR_PILOT_RESULTS.md) was never retracted.
  - DISCOVERY_PIPELINE_VALIDATION.md still headlines lifts and says PROMOTED, which the code cannot
    reach.
  - The F044 retraction never reached the abandoned tensor.
  - AGENT_AUTOPSIES.jsonl still says "4 dispatches" for Hypatia; the true figure is 8.
  - Hecate has 14 STALE prose claims (AUDIT_O).
- **Identity collisions.** "F33" has four meanings, and F-tests collide with specimens F001-F045. The
  ledger_id#seq key collided on 200/206 records.
- **Provenance labels that lied.**
  - 23/57 fossil bodies were dirtied while receipts said PASS.
  - 39 in-house Lenia rollouts were recorded as ORIGINAL_AUTHORITATIVE_RELEASE (regraded c7b9e10f9).
  - NO_NETWORK_FETCH_DETECTED was applied where no scan could run.
  - acquire.py could not have produced its receipt (3463f9003).
- **Stamp blind to the transform.** ATK-016: the leakage_gate manifest hash matched while 6/6 figures no
  longer reproduced.
- **Shape-only digest checks.** [crawl] evidence_wiki/ew/refs.py validates content_digest for sha256
  format only. Derived-view quarantine is a URI substring test (evidence_wiki/ew/store.py L63-83).
- **Judge identity unrecorded.** The Skopos scores.db has no model column, across a three-provider
  fallback. [crawl]
- **Steering fields never recorded.** The forge ledger lacked priority, enrichment_used and
  battery-version fields, so the Coeus effect is permanently unrecoverable.
- **Rows existed only in live databases.** April Kairos rows lived only in Redis/Postgres.

Where provenance SAVED the program:
- **Payload hashes made a reading checkable.** Harmonia caught deflate.c:667 vs 672 before execution.
- **Git ancestry proved timing.** It proved the E-003 amendment came 17 minutes after exposure, and
  Ananke W-O's freeze order.
- **Fossil hashing caught dirty bodies.** 23/57 bodies (7c5bfcb08); rematerialisation caught 11 CRLF
  records (47e13ef65).
- **Replay exposed a formula fossil.** The promotion replay showed the 2,351 count is not reproducible
  under current code.
- **Registry hashes rebuilt archives.** Clymene's registry commit hashes made 26/26 repo snapshots
  reproducible though 97.5% of files were missing; HF etags verified 9/9 payloads.
- **git fsck recovered destroyed ledgers.** The ATK-015 ledgers were recovered and all 13 figures
  reproduced.
- **Committed reports corrected an autopsy.** Hypatia's 8 committed DR reports corrected Aporia's
  autopsy count.
- **Per-call prompt hashes allowed byte-exact reproduction.** Hecate AUDIT_L reproduced RESULTS
  byte-for-byte.
- **Verbatim prompt MANIFESTs.** They made operator intent checkable fleet-wide.

## T19. Status read from the wrong layer; counts over the wrong population; absence from a partial search -- FP and FN

Instances:
- **Exit code or HTTP status read as a property.**
  - Clymene THOR: checkout failed, then `git pull` exited 0, so status=updated with a 123 MB .git only.
  - A gated model README returned HTTP 200 and was read as REPRODUCIBLE while the weights returned 401
    (CLY-CAL-009).
  - Solver status read as correctness: SCS "OPTIMAL" was 188% wrong (Elenchus ELEN-TECHNE-38).
- **Wrong population or wrong unit.**
  - Clymene "Models: 14" (9 real).
  - Skopos "5 scored entities" (1).
  - Charon "~50K clean rows" vs 411,580, "132M" vs 555.8M, and four wrong-population errors in a week.
- **Absence from a partial search.**
  - Eos and Nemesis: a sparse worktree held 43 vs 97 files, and the census found 376 modules in the
    index vs 40 on disk. Fixed with git grep --cached and floor_census._forbid_filesystem.
  - Coeus C-06: `grep | head` was read as "no consumer".
  - Elenchus: a grep of a non-existent path was read as absence.
  - Kairos's 09-11 archaeology missed Harmonia's records of tests that had actually run. [crawl]
- **Wrong object addressed.** `git -C vault/repos/<name>` walked up to the enclosing repo (CLY-CAL-003).
  Hypatia's stall check was pointed at gitdir size during a merge.

## T20. Safeguards that were never wired, never installed, never staffed, or never consumed -- FN mainly

Instances:
- **"ADMISSIBLE" certifies three probes.** attacks/preflight.py --probes runs 3 hard-coded probes
  hard-wired to specific Ergon ledgers or one synthetic corpus; the data checks never run on real
  data. [crawl]
  - The hook is unversioned. It was absent on M2, so all M2 commits went in ungated
    (charon/probe/RULINGS_2026-09-01.md L255-265).
  - This crawl observed the M1 hook print "REGISTRY PROBES (baseline-ratcheted) ... ADMISSIBLE" on its
    own pushes, which touched none of the probed ledgers.
- **Conformance gate not wired.** "THE GATE IS NOT WIRED" (RULING_CONFORMANCE_GATE_SPLIT_2026-09-10.md).
  Archaeon later pinned only /v2/version.
- **Gates without consumers.** "No lane has yet consumed lane_gate, MULTIPLICITY.md or SIZING_RULE.md"
  (Harmonia RESUME_20260925 Q8). run_qualification.py was dead for 8 days and nobody noticed.
- **Veto held by a dormant seat.** The Kairos "veto_authority" was assigned in kairos/patterns/*.md
  while the seat was dormant.
- **Reviews required from dormant reviewers.** Kairos and Elenchus reviews blocked Ananke until the
  operator removed the requirement on 09-26.
- **Reviewer dormant while its input resumed.** Elenchus went dormant on 09-11 while its input stream
  resumed, leaving 187+ passes unreviewed.
- **Adjudication stalled on an offline instance.** The Nyx POET packet waited 11 days on an offline
  Harmonia instance, then resolved in 25 minutes.
- **Guard fails open.** workspace_guard is skipped on ImportError, and HARMONIA_ALLOW_CANONICAL=1
  bypasses it.
- **Independence measurement never produced data.** The watcher scorecard, the only designed measure of
  watcher independence, never produced a committed row.
- **Designed and never executed.**
  - Pheme P1 is blocked on PHEME-03.
  - Hecate's mechanical novelty ruler was withdrawn.
  - The Campaign-6 blind fixtures were never delivered.
  - Organism-Zero was never built.

## T21. Liveness or activity read as productivity; dead inputs read as noise -- FP for health, FN for alarms

Instances:
- **Null ticks graded as health.** Hypatia's May daemon wrote 169 null-tick artifacts vs 8 work
  artifacts, and was graded "clean, 1 problem/day" in at least 4 program documents (Aporia P63; base
  rule 8, 58fe2fc57).
- **Report per tick with nothing placed.** Nemesis 1.0 placed zero tasks in 97.3% of cycles while
  writing a report every cycle.
- **Identical reports passed health checks.** Skopos daily reports were byte-identical below the date
  line while the health check said "skopos: OK". Eos had 3/8 digests byte-identical, and a success=true
  row pointed at an uncollected digest.
- **Missing input read as noise.** Pheme ran 354 ticks with UPSTREAM_NOT_FOUND and the alarm was read
  as noise (pivot/orchestration_monitoring_2026-05-24.md).
- **Output never self-checked.** Hypatia emitted unparseable JSON for 105 days unchecked (13/63 steps
  parse).
- **Snapshot read as trend.** Two healthy worktrees were destroyed after an entry count did not move
  between two looks (Hypatia L-04, leading to "SLOW IS NOT CORRUPT").

## T22. The auditor commits the class it audits; correction bias -- FP and FN

Instances:
- **Harmonia committed the classes it audits.**
  - It rated Bellerophon audit J SUPPORTED while missing its own F1 (C-2).
  - It judged Tyche H4 unreachable at t = 0 (C-1, 68c6e7f68).
  - Its own commit subject leaked an embargoed verdict into a blind replication branch (8eafe8afe).
  - It published three statistical claims it later retracted itself (T05, T09).
- **Corrector bias.** Hecate's REDTEAM_Y found Hecate's corrections numerically sound but readings
  biased toward Hecate: favourable items APPLY, unfavourable items ANNOTATE-ONLY (2dc4fbb01).
- **Attacker severity inflation.** Charon CALIBRATION records that 3 of 5 errors on 09-01 pushed toward
  a bigger finding.
- **Quota-filled self-critique.** Harmonia-A's self_identified_weaknesses holds exactly 6 entries in all
  24 passes (ELEN-HARMA-TRIAGE-01).
- **Auditor near-misses.** Elenchus recorded near-misses: a hex string read as a rule table, and a
  ratio read before its denominator.
- **Adversary failure read as instrument strength.** NEMESIS-01 run 2's 0.00 came from an empty builder
  and looked like a strong gate. This led to assert_builder_built_something.

## T23. Validated configuration differs from deployed configuration; executed rule differs from frozen rule -- FP

Instances:
- **Validated renderer is not the deployed renderer.** R7 validated a .text/.text renderer, while the
  pilot deployed .body vs .text with a JSON header. The arms were separable at 1.000, and +9.6pp was
  withdrawn (charon/probe/TIER_A_EXIT_REVIEW_CHARON_2026-08-19.md).
- **Executed rule is not the frozen rule.** aporia/iq/run_iq_null.py adds N6, has no PARK branch and
  zero asserts, while documentation claimed "the code asserted it" (Harmonia 5702e9fa3, found by
  Artemis U-02).
- **Smoke pass used as equivalence.** The scaffold control called 15/20 accommodations "decorative"
  because smoke runs passed, not because outputs matched (75ace4405).
- **Prose not updated after correction.** run_qualification.py still prints the superseded sqrt(2)
  claim. archaeon/config.py:241 keeps a retracted phrase.

## T24. LLM-specific measurement hazards -- FP and FN

Instances:
- **Structural compliance under impossibility.** The Hypatia MATH-0008 report decomposed a different
  reduction "to fulfill the structural requirements". This was disclosed in prose at L110.
- **Mandated vocabulary.** Prompts require citing named patterns, so counts of those patterns measure
  the prompt (agents/hypatia/CHARTER.md).
- **LLM output presented as analysis.** An Eos digest printed a Nemotron scratchpad about a repo it
  never opened.
- **Harness asymmetry across families.** "Isolated" `claude -p` calls still carry harness residue that
  only Claude subjects see (roles/Hecate/harvest_w2/AUDIT_X_call_isolation.md).
- **Parser accepts truncated output.** extract_json accepted the inner object of truncated Gemini
  replies.
- **Scorer crash filed as UNTESTABLE.** set() on lists crashed the alien scorer (Hecate K10).
- **Refused call silently changes a denominator.** One refused detector call made it 9 vs 10, which
  flips M1 vs P (Hecate C8).
- **Blinding scrubber erases the content.** The scrubber erased rewrite rules and literal "novel/new"
  (Hecate INV_G, K6).
- **One-provider ground truth used as gold.** Batch 17 fossil facts were written by ten same-model
  reader agents. Cartography reference labels were single-annotator with no kappa.

----------------------------------------------------------------------------------------------------

## Cross-cutting observations

1. **Latency of detection.** Defects caught by an executed control were usually caught the same day:
   - Nyx and Harmonia packets;
   - Charon's own drip addendum;
   - Nemesis run 1/2.

   Defects caught only by reading or archaeology survived for months:
   - Nemesis README 162 days;
   - Skopos yield 163 days;
   - Eos scorer about 4 months;
   - the Lehmer precision verdict 3 months;
   - the April zeros contamination, never retracted.

   The repository's best evidence that EXECUTED controls are what matters is this latency gap.
2. **Who caught what.**
   - Self-audit on re-seating (the 2026-09-11 archaeology wave) caught the largest number of historical
     defects.
   - Sibling seats caught the most consequential live ones: Harmonia on Hecate and Bellerophon,
     Techne on Charon, Charon on Ergon and Techne, Nemesis on Eos, Elenchus on Techne, Artemis on
     Nestor and Aporia.
   - External or cross-family signals (frontier-model review, literature, the operator) caught the
     classes no internal seat caught: tautology by definition, known ensembles, and the ASAL observer
     problem.
3. **The territory's immune system mostly fought the symptoms of T01-T04 one instance at a time.**
   - The few artifacts that generalise into executable checks are:
     - Harmonia AP-1.1.0;
     - attacks/REGISTRY.md with preflight probes;
     - Nemesis cheatlib;
     - Charon c1c2_checks;
     - the Necropolis admissibility ladder.
   - All of them are recent (Aug-Sep 2026), and none has been retroactively applied to the era-1 or
     era-2 record.
4. **This crawl is itself a Claude-family audit** of a Claude-family program (T17). Its "[crawl]" defects
   are code readings by the same model family and are unconfirmed by owners. The same latency and
   independence caveats apply to it.
