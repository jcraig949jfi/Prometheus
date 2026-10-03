# Harmonia -- forensic dossier (Tityos Phase 3 intake, lane g1)

Reader: Tityos g1 worker (Opus 5.5), 2026-10-01, with three read-only helper passes (math era; qualification code;
Elenchus/Kairos) whose load-bearing claims were spot-checked against source.
Repo: F:/Prometheus-worktrees/tityos-phase3 at origin/main (5c98f59f1 / 36ffe8073).
Hygiene: every search excluded **/*holdout*/** and **/nestor_secrets/**; no such path was opened. RECORD_D2_* (path
without "holdout") discusses the D2 holdout protocol; only its public firewall/order sections were read.
Executed: 50 pure unit tests under roles/Harmonia/qualification (h0h5, campaign1, campaign6; 50 passed, run by a helper
with -p no:cacheprovider). Nothing else was executed.

Labels: [IMPLEMENTATION FACT] [DESIGN INTENT] [HISTORICAL CLAIM] [REPORTED RESULT -- UNVERIFIED]
[LATER CORRECTION / CONTRADICTION] [CODE-INFERRED CAPABILITY] [UNKNOWN / AMBIGUOUS].
"Nothing is true because Harmonia approved it." This dossier inspects Harmonia as an instrument.

## 0. Summary

- Harmonia had three lives, all under one seat name and many concurrent Claude instances
  (roles/Harmonia/INSTANCES.md).
- **Era 1, 2026-04-12 to 2026-04-23: "cross-domain cartographer".**
  - Work: a tensor-train (TT-Cross) coupling engine over LMFDB-derived mathematical domains (harmonia/src/), a
    landscape tensor of features x projections, and the NULL_BSWCD block-shuffle null family (harmonia/nulls/).
  - It was a consumer of Charon's falsification battery (cartography/shared/scripts/falsification_battery.py,
    F1-F14, plus battery_v2 F15-F32 and one-off F33-F38). It was not the battery's author.
  - The famous "38-test battery calibrated against 3.8M objects at 100.000%" does not correspond to one instrument.
    [IMPLEMENTATION FACT]
    - The test count varies by document: 14, 38, 40 or 97.
    - "F33" means three different tests in three different files.
    - The 3.8M calibration (harmonia/results/mass_calibration.json, 73b4d453a; generating script not committed)
      checks database consistency against theorems (rank = analytic rank, Mazur, etc.). It never runs the battery,
      so it shows nothing about the battery's error rates. [CODE-INFERRED CAPABILITY]
  - The honest output was "40+ kills and zero novel bridges".
- **Era 2, 2026-06 to 2026-08-31: instrument auditor of the whole program.**
  - Reviews, run as four instances with assigned lenses A/B/C/D, found:
    - instrument monoculture: the EC void-miner covers 4/16 known laws (AUDIT_20260622_instrument_monoculture.md);
    - sigma_kernel.PROMOTE never re-runs the battery (verified here: sigma_kernel/sigma_kernel.py:822);
    - Harmonia's OWN "non-gameable" grading oracle ships the answer key in the R6 probe (REVIEW_20260812_*);
    - 99.98% of 658M Theseus records were verdicted by the generator that wrote them (AUDIT_20260819_detector_band.md);
    - Theseus survivors sit on their chance floor, 45.9% vs 46.1% (RETRODICTIONS_20260819_harmonia_C.md).
  - It also published and retracted three of its own statistical claims:
    - a sampling-manufactured false positive (64bba4111);
    - a chance "floor" that was a ceiling (1be87a0fe);
    - a winner's-curse effect size (28d58afbb).
- **Era 3, 2026-09-04 to 2026-10-01: SFE/PEW "scientific audit and qualification" seat.**
  - Instruments: about 3,000 LOC of executable qualification code (QR-1.2.1, AF-1.1.0, EX-1.0.0, FP-1.0.0, PR-1.0.0,
    OQ-1.0.0, HA-1.0.1, AP-1.1.0), about 9.5k LOC of science rulers, an SFE conformance contract and gate, 30
    rulings/records, STANDING_RULES A-F, and a vacuous-readings register.
  - From 09-30, under an operator CWO, it ran a sampled evidence-system audit (13 packages) and a ruler-quality audit.
    These produced the Hecate audit #1037 (3 MAJOR, all later confirmed by Hecate) and one BLOCKING finding
    (Bellerophon E-003 VALIDATED rests on an undisclosed post-exposure amendment).
- How strong the machinery really was:
  - The strongest parts are re-derivation, eligibility/reachability accounting, and cheat controls that actually
    fired on Harmonia's own code (rank-tie defect; single-relabel miss; float-exact cheat; C-ORDER tie-break).
  - Weaknesses found in code:
    - several controls cannot fail (tautological ablations; a hard-coded "pass": True negative control; None
      controls treated as not-failed);
    - mildly anti-conservative t quantiles; Bonferroni coverage wrong for 3 or more primaries;
    - an eligibility gate inconsistent with its decision rule;
    - fixtures co-written with their detectors;
    - heavy shared implementation with the audited producers (Archaeon's synth, null and detector inside d3.v2
      calibration; Techne's port and observer inside the ASAL ruler; Daedalus committing the contract Harmonia's
      gate pins).
  - Most era-3 gates never touched a live confirmatory campaign. The seat itself asked "should this seat keep building
    gates, or stop until a lane uses one?" (RESUME_20260925_m2-ca1148a0.md Q8).
  - Independence was by write-permission and role only. Harmonia, its audit agents, many audited seats and some
    audited instruments (Hecate's detector) are the same model family. Harmonia B named this the "single most
    important open question": "It cannot be closed at one author" (REVIEW_20260812_program_and_instrument_audit.md
    s3).

## 1. Charter and role evolution

Era 1 (cartographer)
- [IMPLEMENTATION FACT] 2026-04-12, 98ae574eb: Harmonia born as a TT-Cross engine (harmonia/src/engine.py,
  coupling.py, phonemes.py, domain_index.py).
- [IMPLEMENTATION FACT] 2026-04-16, 2052e5d7c: RESPONSIBILITIES.md. 2026-04-17, 36a3f74cb: CHARTER.md under
  docs/landscape_charter.md "Landscape is Singular".
  - "The cross-domain bridge concept is dead"; kills reinterpreted as "measurements of terrain through the wrong
    coordinate system".
  - Preserved verbatim at roles/Harmonia/superseded/CHARTER_pre_2026-09-14_superseded.md and
    RESPONSIBILITIES_pre_2026-09-14_superseded.md.
- [DESIGN INTENT] Relations: Aporia generates probe designs; Kairos challenges ("I challenge Kairos's challenges");
  Mnemosyne guards data; Ergon generates at scale; Charon is "my predecessor"; Koios builds indexes; the "Council of
  Titans" (frontier LLMs) reviews.
- Aliases:
  - worker personas "Harmonia-C Gap-filler", "Harmonia-D Re-auditor", "Kairos Query-runner" in conductor waves
    (worker_journal_sessionA_20260417.md:627);
  - later Harmonia_M2_A/B/C/D/E (lens-assigned instances), and operator labels "Harmonia B" and "Harmonia F".
  - Hosts: M1 SKULLPORT, M2 SPECTREX5, M3 GANDALF.

Era 2 (program auditor)
- [HISTORICAL CLAIM] 2026-06-22: program reassessment ("stalled out a bit -- diminishing returns, monocultures").
- 2026-06-27: MEASUREMENT_FLEET_2026-06-27.md. Harmonia owns the "only trustworthy, non-gameable 'are we closer?'
  instrument" (grading oracle). [DESIGN INTENT]
- 2026-08-12: four-lens panel (A architecture, B instrument integrity, C counterfactual, D permanence). Phase-1 blind,
  phase-2 cross-attack (SYNTHESIS_20260812_harmonia_panel.md). Harmonia C declared its Phase 1 not independent
  ("I read both A's and B's reviews"). [HISTORICAL CLAIM]

Era 3 (SFE/PEW audit and qualification)
- [HISTORICAL CLAIM] About 2026-09-04: the seat stopped mathematical discovery.
- 2026-09-11: operator D-23 base-role inheritance; the multi-instance tag convention (INSTANCES.md, instance.py).
- 2026-09-14, Harmonia[m2-f541bed9]: new CHARTER.md. Ten principles, each cited to a ruling:
  - eligible count before the gate;
  - a constant is not a result;
  - nothing is a replicate for a deterministic payload;
  - plan before run;
  - every instrument can fail, can see success, can see cheating;
  - admission per condition;
  - thresholds from downstream need;
  - correct your own rulings beside the original;
  - name what would falsify a ruling;
  - audit, do not mutate.
- 2026-09-16: second lane, the Mechanism Archaeology Pipeline (TECHNE -> NYX -> HARMONIA -> THEOPHRASTUS). Harmonia
  is the resurrection/equivalence stage (RESPONSIBILITIES.md s8). [DESIGN INTENT]
- 2026-09-18:
  - operator "refinery" directive, giving packet rules PR-1.0.0 and STANDING_RULES A1-A10;
  - "Harmonia f owns asal" (gandalf-6cd1348b owns ASAL, POET and Avida rulers);
  - Campaign 6 observatory lane (OQ-1.0.0).
- 2026-09-25: operator reset. Instances m2-ca1148a0, gandalf-6cd1348b and m2-038758c6 closed; m2-475d761f carried
  forward.
- 2026-09-28 to 09-30: under MWO-0001..0004, recorder and adjudication-layer custodian for the Cosmos C3 holdout D2
  firewall audit (RECORD_D2_GOVERNING_AUDIT_AND_SEAL_GATE_2026-09-29.md).
- 2026-09-30: operator CWO (ops/fleet/CWO_2026-09-30_FLEET_ACTIVATION.md:349-374): "Evidence-system audit ... Harmonia
  is an auditor, not a routine permission gate ... Ruler quality: saturated, gameable, unreachable or
  non-discriminating rulers".
- Terminal state, ops/fleet/CENSUS.json (09-30): host SPECTREX5 m2-475d761f, model claude-opus-5-5, state HOLD
  ("waiting: Nyx ASAL prereg packet; E-003 BEE verdict").
- Last commit seen: 0c1f2afab (2026-10-01).

Activity by month (git log --all, subject mentions "Harmonia"):
2026-04 142, 05 23, 06 28, 08 100, 09 412, 10 1. [IMPLEMENTATION FACT]

## 2. Code/system architecture

Era 1 [IMPLEMENTATION FACT unless marked]
- The battery is owned by Charon/cartography, not Harmonia.
  - cartography/shared/scripts/falsification_battery.py: F1-F14, a6eb42b93 (04-06), ba34f1ca4 (04-08).
    run_battery(values_a, values_b, confounds, dose_levels, subgroups, n_hypotheses_tested=3, index_values) returns
    SURVIVES or KILLED. classify_kill() labels kill types.
  - battery_v2.py: F15-F32. battery_unified.py: F1-F23 runner with tiers LAW...KILLED; only F17, F18, F21 and F23
    can kill in the unified classifier.
  - kill_ec_maass.py: F33-F38 (23f6dbef0), one finding only.
  - It is imported by 79 files: the producers (research_cycle.py calls run_battery inline), ergon/tensor_executor.py,
    forge/v3, charon/agents, techne, and harmonia.
- harmonia/src (7,883 lines): domain_index.py (14 domain loaders), coupling.py/phonemes.py (4 scorers), engine.py
  (tntorch TT-Cross), validate.py, tensor_falsify.py, landscape.py, sweep.py, adversarial.py.
  - Data flow: domain features -> scorer -> TT bond dimension -> validate/tensor_falsify -> report.
- harmonia/memory/build_landscape_tensor.py (710 lines): FEATURES F001-F045 x PROJECTIONS P001-P104, cells -2..+2.
  Pushed to Redis. Last changed 2026-04-23 (37a971380), later declared dead.
- harmonia/nulls/:
  - block_shuffle.py, NULL_BSWCD@v1/v2: decile qcut of a stratifier, within-stratum permutation, n_perms 300, seed
    20260417, |z| >= 3 means DURABLE;
  - plain.py, bootstrap.py; frame.py and model.py are scaffolds.
  - 043ba7821, 7c2a8d467.
- Specimen scripts: harmonia/wsw_F0xx*.py, reaudit_*.py, rank*_*.py. Results are written to cartography/docs/.
- Data: LMFDB Postgres 192.168.1.176 (credentials hard-coded in specimen scripts); prometheus_fire.zeros;
  charon/data/charon.duckdb.
  - The 24-slot zeros_vector layout comes from charon/src/ingest_zeros.py:107:
    `vec = normalized + [rn, float(order_of_vanishing or 0), float(degree), log_cond]`.

Era 2 [IMPLEMENTATION FACT]
- harmonia/services/grading_oracle.py, with tiers from harmonia/experiments/reasoning_phase0.py.
- harmonia/experiments/hypothesis_class_coverage_audit.py; validate_* validators.
- harmonia/diagnostics/detector_band_audit.py (--test 4/4), kill_resurrection_audit.py,
  shadow_catalog_chance_floor.py.
- harmonia/experiments/bprime_generate.py and bprime_negative_control.py (bb2037496): a held-out B-prime benchmark
  authored by gemini-3.6-flash.
- harmonia/soak/ (the "Harmonia-A soak" P1-P10 trap probes over ec_curvedata). Not read in detail.

Era 3, all under roles/Harmonia/ [IMPLEMENTATION FACT]
- qualification/h0h5/:
  - qualification_rules.py (QR-1.2.1, 999 lines): LanePlan, validate_plan, refuse_relabel, paired_contrast,
    Estimate.decide, h0_estimands, sizing, validate_cell_payloads, lane_gate(H0..H5), refuse_endpoint, H5 reach
    bounds, program_family;
  - adversarial_fixtures.py (AF-1.1.0, F1-F9 plus detect_f6);
  - exchangeability.py (EX-1.0.0); floor_precheck.py (FP-1.0.0); packet_rules.py (PR-1.0.0);
  - run_qualification.py (entry point) writing ledgers/h0h5_qualification.json;
  - h1h0_phase2_analysis.py;
  - tests/test_qr_1_2_0.py and test_packet_rules.py (33 pass).
- qualification/campaign1/c1_hostile_adjudication.py (HA-1.0.1, a88410dde): an in-process toy world with HMAC
  receipts, 7 cheat improvers and detectors D1-D5. Campaign 1 itself is FROZEN and UNRUN.
- qualification/campaign6/c6_observatory.py (OQ-1.0.0, 0260735bb): sealed fixtures, recall with Wilson intervals,
  escalation order, forbidden-conclusion refusal. 11 synthetic tests. No Campaign 6 world exists.
- qualification/primitives/audit_primitives.py (AP-1.0.0 db6897ecf / AP-1.1.0 8819423e4): reachability,
  absence_control, baseline_gaming, ceiling, null_pass_binomial, freeze_precedes. Fixtures are real 09-30 defects.
- qualification/session_affinity_qualification.py plus t1..t6: an HTTP harness against two SFE engines and PEW.
  Committed result: NOT_RUN (3 PASS / 0 FAIL / 5 INDETERMINATE).
- contracts/:
  - generate_sfe_contract.py: probes a scratch engine; refuses same-ledger, non-loopback or build-mismatch.
  - conformance_check.py: exit 0 CONFORMANT / 1 DRIFT / 2 UNREACHABLE / 3 INCOMPLETE.
  - verify_gate_states.sh, promote_candidate_contract.py, verify_pre_deploy_contract.py, ledger_parity_check.py
    (LP-1.0.0), workspace_guard.py.
  - Consumers: archaeon/conformance.py and vivarium/viv/conformance.py subprocess this gate.
- science/: d3v2_calibration.py, c3_3_* scripts, asal_ruler/ (73 files, about 18 MB of npz), particles_ruler/,
  rs_ruler/ (C, docker), ancestry_ruler/ (synthetic), poet_ruler/, proteus audit, S-series s1-s18 and se1 (09-05).
- rulings/: 30 files. audits/: EVIDENCE_AUDIT_2026-09-30 (+SAMPLE2-4), RULER_QUALITY_2026-09-30.
- Persistence: JSON/JSONL/npz in git; no database.
- No Harmonia commit touches the audited engines (sfe/, archaeon/detectors, archaeon/producer, evidence_wiki/ew).

## 3. Inputs and outputs

- Era 1:
  - Inputs: LMFDB tables (ec_curvedata 3.8M, lfunc, g2c, NF, knots, Maass, materials, NIST); DuckDB zeros; battery
    outputs; Agora/Redis.
  - Outputs: landscape tensor cells, journals, papers (harmonia/paper/harmonia.md, spectral_bsd.md), pattern library,
    retraction registry.
- Era 2:
  - Inputs: the program's own code and corpora (Theseus lifetime_stats, generator registry, oracle).
  - Outputs: review/audit markdown plus runnable diagnostics with --test self-checks.
- Era 3:
  - Inputs:
    - producer readouts (archaeon/docs/h0h5/*.json: D3_LIVE_DOSSIER, C3_2_READOUT, H1H0_PHASE2_READOUT);
    - Nyx prediction packets (nyx/atlas/predictions/*.json);
    - Techne fossils, ports and observers;
    - other seats' preregs and result commits (for the audits);
    - SFE engines over HTTP (contracts, affinity);
    - comms messages.
  - Outputs: rulings (posted --kind ruling), ledgers, STANDING_RULES, VACUOUS_READINGS, typed returns to Nyx/Techne,
    audit reports with severity BLOCKING/MAJOR/MINOR, and findings routed to owners. It never edits audited objects
    (base rule 6).

## 4. Claim class it was meant to police

- Era 1: "cross-domain bridges" and landscape features in arithmetic statistics. The claims police themselves via the
  battery and NULL_BSWCD.
- Era 2: the program's instruments (meters, gates, generators, selection principles).
- Era 3:
  - units of analysis and replicates;
  - preregistration order and exposure;
  - eligibility and attainable range;
  - detector calibration per geometry and null family;
  - claim boundaries (what a readout may be quoted as);
  - H0-H5 lane qualification;
  - SFE route/scoping conformance;
  - mechanism-archaeology resurrection equivalence;
  - from 09-30, the correctness of dispositions against frozen rules, and ruler quality (saturated, gameable,
    unreachable, non-discriminating).
- Explicitly not: running the science, gating releases, or editing the audited object (RESPONSIBILITIES.md s2).
  [DESIGN INTENT]

## 5. Measurement methodology

- Era 1: permutation z-scores (|z| >= 3 or p < 0.001); within-stratum block shuffles; Cohen bands; dose-response;
  subgroup sign consistency; fit-based estimates (F011 eps_0); stratification patterns (Patterns 20, 26, 30).
- Era 2: "executing lens" (re-run everything, E1/E3 evidence typing); enumeration not sampling (detector-band:
  56 generators instantiated, 7,914 records executed); controls asserted in code (a1 positive, a3 cheat).
- Era 3:
  - paired-block contrasts with t intervals against a practical threshold, with a permutation-lattice eligibility
    gate;
  - Monte Carlo chance floors;
  - exact binomials;
  - Pearson trend against commit order (exchangeability);
  - modal-mass floor;
  - hash-chained amendments;
  - cheat/positive/negative controls first, with abort (STANDING_RULES B2);
  - git ancestry checks (freeze precedes result; F6);
  - re-execution of others' committed analyses;
  - attainable-set enumeration (F1).
- 09-30 audits:
  - "read-only audits (three independent agents, each re-executing the committed analysis where possible)", then
    "every MAJOR/BLOCKING finding ... re-verified by Harmonia (HV)" (EVIDENCE_AUDIT_2026-09-30.md);
  - RULER_QUALITY used "exact binomials or small simulations; scripts in Harmonia's scratchpad". Those scripts are
    not committed, so the Tyche H3 0/20 simulation is not reproducible from the repo. [IMPLEMENTATION FACT]

## 6. Null/control generation

- NULL_BSWCD block shuffle within stratifier deciles. [IMPLEMENTATION FACT]
  - Defect: if sd < 1e-12 and obs != mean it returns z = inf, which reads as DURABLE. A degenerate null certifies
    survival.
  - The same defect is in plain.py. [IMPLEMENTATION FACT, helper-read]
- NULL_BOOT scores a bootstrap with a null-style z. Its spec reports F011 z = 8.92 DURABLE, which a centred bootstrap
  cannot produce. [UNKNOWN / AMBIGUOUS]
- Era-1 ad hoc nulls [REPORTED RESULT -- UNVERIFIED]: conductor-matched shuffles (50 bins, 500 permutations);
  column-shuffle with 30 permutations; "synthetic null 0% FP across 800 trials".
- The tensor-speed F1 null (harmonia/src/tensor_falsify.py:64) always uses KosmosCoupling while the observed value
  uses the passed scorer: 5 permutations, max of two z-scores, z > 2. [IMPLEMENTATION FACT, helper-read]
- Era 2: random-pairing null for Theseus survivors; the "payload-reading negative control" (a cheat allowed to read
  the probe payload); cheat control a3 (predicate_kind).
- Era 3: synthetic generators for every qualification fixture (AF F1-F9, C1 cheats); D3/C3 Monte Carlo under i.i.d.
  tables; d3.v2 corpora built with archaeon.synth (the producer's generator); ancestry degradation arms; garbage and
  blank frames for ASAL.

## 7. Positive controls

- Era 1 "surveyor's pins" F001-F009 (Mazur, modularity, BSD parity, Hasse, Scholz, ...). These are positive controls
  for the DATA, not the battery. [CODE-INFERRED CAPABILITY]
  - F003 "full BSD identity at 1e-12" is circular for rank >= 2, since Sha is computed via BSD. Pattern 30 later
    grades it Level 4. [LATER CORRECTION / CONTRADICTION]
- Battery calibration 1cc2e0f3d (2026-04-12), F24/F25 only: cartography/shared/scripts/m1_battery_calibration.py and
  v2/battery_calibration_results.json. [REPORTED RESULT -- UNVERIFIED]
  - 2 false positives in 300 synthetic-null trials. The commit headline "99.3% precision" is really 1 - FPR.
  - An eta^2 injection of 0.01 was missed; injections of 0.10-0.14 measured about 0.07 (underestimated).
  - A random-walk half-split produced a false positive (eta^2 = 0.166 on noise). That led to a stationarity gate
    (m1_f33_stationarity.py, yet another "F33").
  - This is the only demonstrated detectability curve for the era-1 battery, and it is synthetic.
- Battery self-test: 4 synthetic cases in falsification_battery.py __main__; no committed run output.
  [IMPLEMENTATION FACT]
- Era 2:
  - detector-band positive control a1 = REPRESENTABLE;
  - Harmonia D's "can anything pass?" control, which named a control pair nobody had noticed was half-open
    (SYNTHESIS_20260812 s1).
- Era 3, each verified by helper reading or tests:
  - F4 recovers a planted +0.20 effect;
  - the h1h0 POSITIVE control (planted G = +0.5, lo 0.114 > 0);
  - floor_precheck reproduces C3-2 f = 0.000;
  - d3.v2 w03 positive 0.98;
  - ASAL C-POS-SEARCH reaches 0.7949 < 0.8167;
  - ancestry C-POS (D5 recall 0.904);
  - particles C-POS, which FAILED in 001 (5,463 vs band [10, 1000]);
  - Harmonia's first gate in each audit is "re-run the committed analysis to the committed outcome".
- Missing: positive-control detectability for the audit process itself. No planted defect was ever slipped into a
  package to see whether the 09-30 audit catches it. [UNKNOWN / AMBIGUOUS: none found]

## 8. Negative controls

Real, able to fail [IMPLEMENTATION FACT]:
- validate_plan's five refusing plans;
- refuse_relabel cases;
- F4, F7, F8 and F9 clean twins;
- the PR rules silent on clean inputs;
- the conformance DRIFT negative on the superseded candidate (contracts/verify_landed_2026-09-18/);
- the ASAL C-NEG-BLANK zero world (0.8749995, NOT_ALIVE);
- the C1 7/7 honest twins quiet;
- the LP selftest.

Cosmetic, cannot fail [IMPLEMENTATION FACT]:
- the h1h0 NEGATIVE control has "pass": True hard-coded;
- F1, F2, F3 and F5 in AF have no clean twin, so an always-fire detector passes;
- the C1 and AP "ablation" checks set a disabled detector's output to [] / flag=False, so "the cheat escapes when the
  detector is disabled" is true by construction (c1_hostile_adjudication.py:318-321, :443-446; audit_primitives.py
  chk);
- the d3.v2 always/never stubs test only the counting harness;
- the exchangeability "positive control" is a regression pin on the producer's dossier, not planted truth.

Audited elsewhere:
- Harmonia found the Proteus V0.5 negative control "PASSES, BUT CANNOT FAIL" (max |J| 2.168e-19)
  (RULING_PROTEUS_CURRENT_INSTRUMENT_AND_R4_2026-09-18.md).

## 9. Neutral/intermediate controls

- Three-valued and labelled-indeterminate outcomes are a design centrepiece:
  - INCONCLUSIVE / INELIGIBLE / NOTHING_COULD_FIRE / STRUCTURALLY_VOID / UNREACHABLE_BY_DESIGN /
    INDETERMINATE_BY_RULE_GAP / SANITY_CHECK_ONLY / VOID_BY_CONSTRUCTION / NO_INFORMATION;
  - the VACUOUS_READINGS.md register (V-001..V-008), "never quoted as a null".
  [DESIGN INTENT, partly IMPLEMENTATION FACT in QR/AP]
- Defects in how intermediates are counted:
  - T3_2 and T3_3 in t3_strict_cutover_rehearsal.py:85-86 record "n/a" as pass, contrary to the frozen spec;
  - harm56_map.py authorises replication when C-SELF / C-STATIC are None ("is not False"). Disclosed in the RECORD;
    not fixed in code.
  [IMPLEMENTATION FACT]

## 10. Qualification criteria / gates / thresholds

Era 1:
- F1 p < 0.001 (10K shuffles); F2 4/5 splits; F3 |d| >= 0.2; F4 confound absorbs > 50%; F6 p < 0.05/n (n defaults
  to 3); F7 |rho| > 0.8; F8 75%; F9 95th percentile of 1000 shuffles; F11 accuracy > 0.55; F14 lag retains > 90%.
- NULL_BSWCD |z| >= 3.
- F24 eta^2 at p < 0.001 and z > 3; F25 out-of-sample R2 > 0.15 means UNIVERSAL.
- [IMPLEMENTATION FACT, helper-read]

Era 3:
- QR:
  - min attainable p = 2/2^n <= alpha (plan level) vs alpha/n_primary (decision level);
  - gates min_blocks 6;
  - Bonferroni within a lane; alpha/6 across the program (FWER 0.265 printed);
  - pool >= 2K for H1;
  - H5 excess over the 8/12 reach bounds.
- EX: |r| < 0.577 EXCHANGEABLE, < 0.816 SUSPECT, else VIOLATED.
- FP: p_mode > 0.50 refuses (HARD_FLOOR_N8 0.688 is defined but unused).
- PR: a stochastic comparative row needs a power statement for strong verdicts; extensions use disjoint seeds.
- C1: D4 seen-minus-fresh gap > 0.03; 5 relabels.
- C6: VACUOUS when false-escalation >= 0.5 AND detection == 1.0.
- D3 band [1/3, 3]; d3.v2 2-SE rules over 600 corpora per cell.
- Audit severities: BLOCKING (disposition wrong or unsupported / verdict predetermined or unreachable), MAJOR
  (material evidence gap, wrong secondary claim, non-discriminating ruler), MINOR (hygiene).
- Verdict vocabulary for audited packages: SUPPORTED / SUPPORTED_WITH_DEFECTS / NOT_SUPPORTED as labelled.
- [IMPLEMENTATION FACT / DESIGN INTENT]

## 11. Statistical methods

- Era 1: permutation z (assumed normal, so z = -348, 111.78 and -383 were quoted from 300-permutation or
  Gaussian-SE nulls that cannot resolve such tails); Bonferroni with small n; BH available (F26); Cohen bands;
  Spearman/partial correlations; decay-ansatz fits (F011 joint fit under-determined: alpha 0.49 +/- 0.52, eps_0
  -4.07 +/- 56.08). [IMPLEMENTATION FACT / CODE-INFERRED CAPABILITY]
- Era 3 [IMPLEMENTATION FACT, verified in qualification_rules.py:229-282]:
  - paired t intervals from a hand table;
  - t_crit returns the first tabulated df >= df (df 11 uses t(12) 2.179 vs true 2.201): mildly anti-conservative;
  - paired_contrast passes 0.025 to t_crit whenever alpha/n_primary != 0.05, so for 3 primaries (H2, H3) the
    interval uses the 0.025 quantile while alpha_used records 0.0167: Bonferroni coverage wrong;
  - eligibility via the sign-flip permutation lattice while the interval is parametric (mixed estimators);
  - helper-verified by execution: lane gates say 6 blocks ELIGIBLE, but Estimate.decide returns INELIGIBLE at 6
    blocks with 2 primaries (0.03125 > 0.025).
- Other era-3 methods: Monte Carlo power; c' Sigma c contrast variance; Wilson intervals; exact binomial tails;
  F-intervals for variance ratios; Spearman without tie handling.
- No permutation test sits in any decision path. [IMPLEMENTATION FACT]
- The H0 sqrt(2) "for any rho" claim was superseded in QR-1.1.0 and HARM-32 [LATER CORRECTION / CONTRADICTION], but
  run_qualification.py section 2 still prints it, and its simulation generates exactly the case that confirms it
  (measured 1.4613 vs 1.4142). [IMPLEMENTATION FACT]

## 12. Independence assumptions

Shared code (auditor imports producer) [IMPLEMENTATION FACT]:
- science/d3v2_calibration.py and d3v2_adjudicate.py import archaeon.config, archaeon.synth (_row/_wrap),
  archaeon.calibrate_d3_null.f_cdf and archaeon.detectors.d3_variance_anomaly. Generator, exact reference and
  detector all come from the producer, so a shared error is invisible.
- science/c3_3_baseline_ic_sample_check.py runs through archaeon.producer.campaign_c3_3. Contrast
  c3_3_region_recompute.py, which is stdlib-independent.
- h1h0_phase2_analysis.py imports archaeon.workspace.
- The ASAL ruler loads techne/scripts/techne107_asal_observer.py; thresholds are Techne's receipt numbers.
  "Observer-stable" (HARM-55/56) is the same CLIP ViT-B/32 weights through torch and Flax.
- The particles oracle comes from the package under test.

Producer imports auditor (circular) [IMPLEMENTATION FACT]:
- archaeon/producer/exchangeability_table.py (7017dc79e) imports Harmonia's exchangeability.py to produce the table
  Harmonia relies on (0 eligible).
- archaeon/config.py copies the cuts with the retracted "log terms" wording.

Audited party writes the auditor's input [IMPLEMENTATION FACT]:
- Daedalus committed roles/Harmonia/contracts/sfe_contract.json (a1dd1458c, fbfcfb276, 2983bd548). Harmonia re-gated
  it (60f710042) but did not re-derive scoping.

Era-1 judge = producer:
- Charon wrote both the battery and the research_cycle producer loop that calls it inline.
- Harmonia, Ergon and forge import the same battery.
- Shared DuckDB zeros layout (Charon).
- [IMPLEMENTATION FACT]

Authorship:
- Generators and detectors for AF F1-F5, the C1 cheats and the AP fixtures are written by one instance in one commit.
  [IMPLEMENTATION FACT]
- Model family:
  - Harmonia instances are claude-opus-5 / claude-opus-5-5 (CENSUS.json).
  - Its 09-30 "three independent agents" are Claude subagents.
  - Fabric merge reviewers are claude-opus-5-5 workers (Atlas digest cites #1006).
  - Hecate's gravity detector is MODEL = "claude-opus-5-5" (hecate/gravity/run.py:19) [IMPLEMENTATION FACT].
  - So an audit of an LLM-labelled absence claim was performed by the same model family that produced the labels.
- Harmonia B's own statement (08-12): "Code-independence is proven across all of them. Author-independence is not ...
  These two hypotheses are currently observationally identical ... It cannot be closed at one author." [HISTORICAL
  CLAIM]
- The only cross-family artifact found is the B-prime held-out benchmark authored by gemini-3.6-flash (bb2037496).
  No later commit grades it. [UNKNOWN / AMBIGUOUS]

Instance independence:
- Sibling instances cannot message each other (comms inbox filters sender != agent; #417). They rewrote each other's
  files (HARM-31, 72bc70365).
- "Many Harmonias" are not independent reviewers either, since they share the seat's files and rules.

Panel independence:
- The 08-12 four-lens panel was blind in phase 1 except Harmonia C, which declared its contamination.

## 13. Provenance tracking

Wins:
- [IMPLEMENTATION FACT] Freeze-before-result checks executed by git ancestry: F6 and audit_primitives.freeze_precedes
  flag the real Ananke W-O plan (PLAN.md first added with the results in 93e2e544b).
- [HISTORICAL CLAIM] The sealed-then-frozen interlock in ASAL: results sealed unread (ffd11a1c0) before Nyx froze
  the prediction (360a33931). The operator endorsed it as "an interlock, not a substitute for preregistration"
  (STANDING_RULES A8).
- [HISTORICAL CLAIM] E-003: the chain dry run 8262c32f2 -> amendment C4.2 at 567762a15 (17 min later) -> production
  lower bounds was reconstructed entirely from commits, and the owner accepted it (errata d06059735).
- [IMPLEMENTATION FACT] DEF-HARM-D2-001: executing the public protocol status found the SEAL gate unpassable on real
  history; three integration merges carry the unchanged blob 10c7b600.
- [IMPLEMENTATION FACT] SIGNATURE@v1 null hashes; commit SHAs in results; harmonia/memory/retraction_registry.md;
  prompts committed verbatim with sha256 manifests (significant-prompt rule).

Failures:
- [LATER CORRECTION / CONTRADICTION] The 3.8M calibration script was never committed.
- [IMPLEMENTATION FACT] The zeros_vector contamination (charon/src/ingest_zeros.py:107 appends root_number,
  analytic_rank, degree and log N to the zeros).
  - harmonia/scripts/survivor_kill_protocol.py:45 and unified_spectral_bsd.py:45 sort every positive slot as a "zero"
    (verified line 45 here).
  - So the 04-13 "8/8 survivor" spectral-tail signal (8e2be1c64) and "rank from zeros 92.1%" (ebd7e8ab3) likely
    consumed metadata. [CODE-INFERRED CAPABILITY]
  - The 04-16 detection (thesauros/proposals.md P-009, 8744918bf) renamed the tables. The retroactive audit item in
    thesauros/cleanup_queue.md is still [OPEN], and harmonia/paper/spectral_bsd.md has no retraction.
- [LATER CORRECTION / CONTRADICTION] The F044 retraction was recommended (04-23) and never applied; the tensor was
  abandoned.
- [IMPLEMENTATION FACT] Era 3:
  - the ASAL run is not re-runnable at HEAD (the search refuses; accept.json executable = False);
  - two HARM-55/56 hashes were CRLF host bytes, not blobs (ERRATUM E-1, 646cbcda8);
  - RULER_QUALITY simulation scripts live only in a scratchpad;
  - Harmonia's own commit 8eafe8afe carried an embargoed verdict into a blind replication branch (CORRECTION C-2,
    d3f99cfdc);
  - Hecate's calibration file overwrite by case collision was seen by Harmonia only as a MINOR portability issue;
    Hecate itself found the content loss (CORRECTIONS K3).

## 14. Known defects

Era 1 (code-read; not executed):
- validate.py battery hook: `battery.test_correlation(values_a, values_b, claim=...)` against the signature
  (finding_id, claim, values_a, values_b, ...) raises TypeError (claim given twice), so it always returns
  "UNTESTED". The TT path never ran the battery. [IMPLEMENTATION FACT, verified harmonia/src/validate.py:221 and
  battery_unified.py:196]
- Nulls map a degenerate null to DURABLE (z = inf).
- The tensor-speed F1 scorer mismatch.
- F12-F14 pair unpaired groups by row index, so verdicts depend on row order. [IMPLEMENTATION FACT, helper-read]
- F1, F9 and F6 are not independent tests and F11 is another location test, so "N tests survived" overstates the
  evidence. [CODE-INFERRED CAPABILITY]
- The F33 id collision makes "killed by F33" unresolvable.
- Pseudo-replication: isogenous curves have identical zeros, and survivor_kill_protocol does not deduplicate by
  isogeny class (n = 31,073; p = 1.89e-86). [CODE-INFERRED CAPABILITY]

Era 2:
- The grading oracle's R6 answer leak (Harmonia's own).
- The B-prime sandbox rejected 20/20 true claims on first run (regex import screen). Fixed with ast. [HISTORICAL
  CLAIM]

Era 3 [IMPLEMENTATION FACT unless marked]:
- t_crit rounding; the Bonferroni quantile for k >= 3; the eligibility mismatch at 6 blocks.
- run_qualification.py dead 09-10..09-18 (KeyError after the rename) with no CI; fixed f58d4bd36.
- generate_sfe_contract.py NameError 09-11..09-14 (7d302b5ae -> 671378c47).
- The conformance gate "NOT WIRED" on 09-10 (RULING_CONFORMANCE_GATE_SPLIT_2026-09-10.md). Every 09-10 corpus was
  produced without a conformance check.
- A required-field change being DRIFT exists in prose only.
- Archaeon's consumer_routes contain only GET /v2/version, so INCOMPLETE never halts it.
- workspace_guard fails open on ImportError or with HARMONIA_ALLOW_CANONICAL=1.
- [CODE-INFERRED CAPABILITY] Substring-matched self-declarations in validate_plan / refuse_endpoint / C6
  forbidden-conclusion (evadable by renaming).
- [CODE-INFERRED CAPABILITY] C1 D3: answers flagged "local": True skip receipt verification.
- [CODE-INFERRED CAPABILITY] freeze_precedes uses only the plan's FIRST add, so a later edit of the plan passes.
- [CODE-INFERRED CAPABILITY] EX is linear-only (a step change or AR(1) without trend reads EXCHANGEABLE).
- [CODE-INFERRED CAPABILITY] FP passes at p_mode exactly 0.5.
- [LATER CORRECTION / CONTRADICTION] Corrections not propagated: the "log terms" phrase survives in
  archaeon/config.py:241; sqrt(2) prose survives in run_qualification.py.

## 15. Historical audits performed (by and on this seat)

By Harmonia (selected):
- 2026-04-15: permutation null killed Kairos's NF backbone (z = 0.0); conductor conditioning killed the OQ1 spectral
  tail; BSD parity over 3,844,373 curves with zero disagreements (SESSION_JOURNAL_20260415.md, c275e973e).
  [HISTORICAL CLAIM]
- 2026-04-18/22: NULL_BSWCD re-audit of 28 cells (043ba7821); reaudit_10 stratifier mismatch; F041a Euler-deflation
  sign inversion; F044 sampling frame (worker_journal_auditor_20260423.md). [HISTORICAL CLAIM]
- 2026-06-22: instrument monoculture; stall map (PROMOTE trusts caller-asserted survival).
- 2026-08-12: four-lens program review; grading-oracle R6 leak (self-attack).
- 2026-08-19: detector-band audit; kill-resurrection retrodiction (0/92 resurrect).
- 2026-09-05: boundary-depth qualification packets. 48/64 SFE specimens are WORLD-BLIND; composition destroys
  world-coupling in 94% of cases; 7 of 4,032 ordered pairs usable (BOUNDARY_DEPTH_PACKET_01_2026-09-05.txt).
- 2026-09-06..09-18: about 25 rulings on Archaeon/Daedalus/Herakles/Nyx/Techne/Proteus designs and readouts.
  - Examples: D3 30/77 fires a denominator artifact; D3 upper fires trend artifacts; C3-3 region gate printed 10 vs
    expected 8.46 (NO-GO as printed); C3-2 H2-over-D3 STRUCTURALLY_VOID; the Proteus negative control cannot fail;
    ASAL CUT_SUPPORTED with 650/1,045 draws unexecuted.
- 2026-09-29: holdout D2 governing firewall audits v2..v13 recorded (Odysseus auditor of record; 12 FAIL then PASS);
  DEF-HARM-D2-001.
- 2026-09-30:
  - Evidence-system audit, 13 packages over samples 1-4: Hecate x3, Odysseus S3, Aphrodite A23, Ensorain T25,
    Ananke W-O/W-Q/W-Y, Bellerophon E-003 and E-BEL-REPL-01, Aether E-010, Nestor X-MAT.
  - Ruler-quality audit: Tyche v0, Hecate autopsy, Hecate alien-lawful rule.
  - Rulings on IQ-NULL, gap_prospective_v1 custody, POET novelty estimator, R19 rollout fossil grade.

On Harmonia:
- [HISTORICAL CLAIM] 2026-04-18: an external frontier-model methodological review caught F043 as an algebraic
  identity, so the retraction was external (df20f900c).
- [HISTORICAL CLAIM] Aporia Report 1: F011 bulk = the Duenez-HKMS excised ensemble.
- [HISTORICAL CLAIM] 2026-08-12: the panel's phase-2 attacks killed two of Harmonia A's proposals (SYNTHESIS s4).
- [HISTORICAL CLAIM] Elenchus: ELEN-HARMA-TRIAGE-01 found Harmonia-A filled self_identified_weaknesses to a quota of
  six in all 24 passes; ELEN-CAMPAIGN-P51-P62 found the headline Katz-Sarnak symplectic split (p = 1e-4) not
  reproducible from the repo (engine/shadow/REVIEWS.jsonl).
- [HISTORICAL CLAIM] Archaeon caught a direction error in Harmonia's S17 narrative (b5498c162).
- [HISTORICAL CLAIM] Tyche #1047 refuted Harmonia's H4 reachability rating (C-1). Bellerophon #1113 plus two Fabric
  reviews refuted Harmonia's audit J (C-2). Techne #1072 found the CRLF hash erratum.
- [HISTORICAL CLAIM] The operator's review of the ASAL packet narrowed Harmonia's I3 and I0 readings
  (prompts/2026-09-18_asal_review/OPERATOR_REVIEW_verbatim.md).
- [REPORTED RESULT -- UNVERIFIED] Artemis R-11 census (roles/Artemis/selftest/runs/R-11/REPORT.md) showed the August
  Harmonia "54.5%" gate figure was a keyword proxy (72% agreement with hand labels). The Campaign 6 detectors 1-2
  "admitted" in Harmonia's lane fire 3/12 and 0/12 at frozen population thresholds.
- [REPORTED RESULT -- UNVERIFIED] Aphrodite's defect harvest (roles/Aphrodite/harvest_2026-09-30/evidence/
  findings_A1_defects.md) lists Harmonia episodes D01, D04, D07 (self-caught STAT, "3rd time"), D79 and D87
  ("auditor commits the class it audits") and D85 (CRLF).

## 16. Historical findings (labels on the record)

| finding | date | label |
|---|---|---|
| F001-F009 calibration anchors (Mazur, modularity, BSD parity, ...) | 04-13 | REPORTED POSITIVE as data/theorem checks; not battery calibration; F003 circular |
| "3.8M objects at 100.000%" battery calibration | 04-13 | REPORTED RESULT -- UNVERIFIED; mis-scoped (database consistency), never corrected, still cited 08-12 |
| Spectral tail -> isogeny class size, "8/8 survive" | 04-13 | CONTAMINATED (likely: zeros_vector metadata + pseudo-replication); ARI version KILLED 04-15 |
| Spectral-BSD "rank from zeros 92.1%" (paper) | 04-13 | CONTAMINATED (likely) and known mathematics; no retraction found |
| F010 NF backbone via Galois label | 04-17 | LATER OVERTURNED (block null z = -0.86, n = 51; low power) |
| F011 GUE first-gap deficit 14% -> 38% | 04-13..19 | MIXED: bulk = known excised ensemble; rank-0 residual eps_0 22.90 +/- 0.78% kept; z_block 10.46 -> 4.19 (degenerate stratifier); unfolding dependence unresolved; never independently replicated |
| F012 Moebius bias, genus-2 aut groups (z 6.15) | 04-17 | LATER OVERTURNED (did not reproduce, max |z| 0.52) |
| F013 zero-spacing rigidity vs rank | 04-17 | REPORTED POSITIVE, downgraded (mixture; downstream of F011) |
| F014 Lehmer/Salem gap | 04-17 | REPORTED POSITIVE (descriptive, after sample-bias correction) |
| F015 Szpiro vs conductor sign | 04-17 | REPORTED POSITIVE (sign only) |
| F041a rank-2 nbp ladder | 04-18/22 | MIXED -> LATER CONTRADICTED (Euler deflation sign flip), unreconciled |
| F042 CM disc -27 | 04-18 | known (calibration refinement), n = 14 |
| F043 BSD-Sha anticorrelation z_block -348 | 04-18 | LATER OVERTURNED (algebraic identity), external catch |
| F044 rank-4 corridor | 04-23 | LATER OVERTURNED (recommended; LMFDB sampling frame); not applied |
| Knot GUE | 04-13 | INSTRUMENT FAILURE / KILLED (preprocessing) |
| EC torsion predicts NF class number rho 0.76 | 04-12 | LATER OVERTURNED (within-bin rho 0.033) |
| "40+ kills, zero novel bridges" | 04 | REPORTED NEGATIVE/NULL (several kills plausibly underpowered, see s21) |
| EC void-miner "0 novel laws" | 06-22 | INCONCLUSIVE (instrument ceiling: 4/16 coverage, out-of-class 0/12) |
| Grading oracle R6 tier | 08-12 | INSTRUMENT FAILURE (answer key in probe) |
| Theseus nulls are detector blindness | 08-19 | REPORTED NEGATIVE (fails; 99.98% self-verdict; nulls class-relative) |
| Theseus survivors | 08-19 | REPORTED NEGATIVE (45.9% vs 46.1% chance floor) |
| Soak P9 "verdicts unaffected by sampling" | 08-20 | LATER OVERTURNED (P10: sampling made adelic_genus false positive) |
| Action-divergence excess (+7.8 pp over "floor") | 08-25 | LATER OVERTURNED (floor is a ceiling; 1be87a0fe) |
| SE-1b hill-climbing d = 0.60 | 09-05 | LATER OVERTURNED (winner's curse; d 0.37 [0.28, 0.45]) |
| SFE menagerie 75% world-blind | 09-05 | REPORTED NEGATIVE (instrument/population finding) |
| D3 30/77 fires; upper fires trend artifacts; 9 survivors "a LEAD" | 09-10 | INSTRUMENT FAILURE (producer detector) |
| C3-2 H2 via D3 | 09-10 | INCONCLUSIVE (STRUCTURALLY_VOID) |
| H1/H0 phase 2 | 09-14 | INCONCLUSIVE ("measures the instrument, not H0"; cross-deploy) |
| d3.v2 LIVE geometry admitted | 09-14 | REPORTED POSITIVE (synthetic); never used live |
| H5 learned decoder reach | 09-18 | REPORTED NEGATIVE (11.7305 = random permutation 11.72) |
| particles 002 boundary; claim (c) | 09-17 | REPORTED POSITIVE (boundary); INCONCLUSIVE (c) |
| ASAL legit search I0-I3 | 09-18 | MIXED (I1/I2 by witness; I3 on executed subset only; I0 weak) |
| HARM-55/56 observer stability | 09-30 | REPORTED POSITIVE (same model twice; validity unaddressed) |
| POET novelty estimator structural cut | 09-30 | REPORTED POSITIVE, NOT CONFIRMATORY |
| Evidence audit A-E, F-J, S3 | 09-30 | dispositions mostly SUPPORTED(_WITH_DEFECTS); E-003 NOT_SUPPORTED as labelled (accepted by owner) |
| Hecate #1037 (3 MAJOR) | 09-30 | confirmed by Hecate CORRECTIONS K1/K2 (+K3 found deeper) |
| Tyche H1/H6 unreachable | 09-30 | applied by Tyche; H4 rating LATER OVERTURNED (C-1) |
| Audit J (E-BEL-REPL-01 SUPPORTED) | 09-30 | LATER OVERTURNED to SUPPORTED_WITH_DEFECTS (C-2) |

## 17. Later corrections (timelines)

- F043:
  - Claim: "durable", z_block -348 (9fc257064, 04-18).
  - Challenge: an external LLM review (log A contains -log Sha by definition).
  - Correction: retracted df20f900c the same evening; Pattern 30 and null_protocol v1.1 (db37c2c2a).
  - Status: closed. The block null passed a tautology; only an outside reader caught it.
- F011:
  - Claim: 14% then 38% GUE deficit.
  - Challenge: literature (excised ensemble).
  - Correction: layered calibration plus residual; z_block corrected 10.46 -> 4.19 (812c34221); language narrowed
    (c9d2276e1); Track D (independent pipeline) deferred (2651570bb).
  - Status: open, never independently replicated.
- zeros_vector:
  - Layout 04-01 (Charon); 04-13 consumers; 04-16 detection and table rename; 04-18 retroactive audit OPEN.
  - Status: the 04-13 Harmonia survivors are unaudited.
  - Discrepancy: Mnemosyne decoded slot 22 as "not analytic_rank" but ingest_zeros.py writes order_of_vanishing
    there. [UNKNOWN / AMBIGUOUS]
- "3.8M at 100.000%":
  - Claim 04-13 (aporia/README.md, harmonia_method.md).
  - Never challenged in any review read. Re-asserted as the "unique Tier 4 asset" in POSITION_20260812.
  - Status: uncorrected. [LATER CORRECTION / CONTRADICTION absent]
- Grading oracle:
  - "Non-gameable" (06-27).
  - Harmonia B self-attack (08-12): R6 leak, cheat_reader 100%, the reference "falsifier" reads the payload.
  - Status: recorded; no fix commit traced in this pass. [UNKNOWN / AMBIGUOUS]
- sqrt(2):
  - "For any rho" (RULING_H0_H5 09-08).
  - Archaeon reproduced Appendix A; QR-1.1.0 corrected it (789ce4fdd).
  - The ruling was annotated only 09-17 (HARM-32, 22d5c7432).
  - Still printed by run_qualification.py.
- Tyche H4:
  - Harmonia: "nearly unattainable" (e72508448).
  - Tyche #1047 showed the evolving baseline (1.000 -> 0.547 -> 0.518).
  - C-1 (68c6e7f68); F1 amended.
- Audit J:
  - Harmonia: SUPPORTED (51f1e7abc).
  - Fabric adversarial reviews plus Bellerophon #1113: K3 unreachable; exposure via a merge carrying Harmonia's own
    commit subject; "chance-level" false.
  - C-2 (d3f99cfdc); F8 amended; commit-subject practice changed.
- E-003:
  - Bellerophon VALIDATED.
  - Harmonia sample 2 H BLOCKING (cffcfc64b).
  - Owner errata d06059735 (ALTERED confirmatory, VALIDATED conditional).
  - Verdict of record open with the operator.
- Hecate #1037:
  - Three MAJOR (adbf7fdb5).
  - Hecate verified all three (roles/Hecate/harvest_w2/CORRECTIONS_2026-10-01.md K1, K2, and K3 deeper).
  - Note the latency: the Atlas digest (roles/Atlas/inference_harvest_2026-09-30/ATLAS_BURIED_SIGNALS_AND_RESIDUALS.md
    E7) recorded it as unanswered as of #1177. Corrections landed 2026-10-01.
- ASAL I3:
  - CUT_SUPPORTED (2ead5e011).
  - Operator review: SUPPORTED_ON_EXECUTED_SUBSET, because 650/1,045 draws were refused by the port.
  - New standing rule A4: executor-domain acceptance before a packet is executable.

## 18. Pivots

1. 2026-04-17 "Landscape is singular": from bridges to coordinate systems. A kill became "terrain seen through the
   wrong projection" (docs/landscape_charter.md). [DESIGN INTENT]
   - Risk recorded: kills stop being falsifications (Pattern 6: a kill "does NOT mean the feature is absent").
2. 2026-04-29 to 06: Agora died; the landscape tensor was abandoned after 04-23.
3. 2026-06-10..22: constructive enumeration (void-miner, the a3 product-measure theorem, "a proof, not a
   measurement").
4. 2026-06-22..08-19: audit of the program's instruments rather than of mathematics.
5. 2026-09-04..11: SFE/PEW qualification seat (CHARTER rewritten 09-14). April queue classified, not resumed
   (RESPONSIBILITIES.md s7: nothing STILL_LIVE).
6. 2026-09-16: mechanism archaeology lane added.
7. 2026-09-30: CWO auditor-of-the-fleet ("auditor, not a gate").

## 19. Journals / TODOs / backlogs

- Journals: roles/Harmonia/journal/*.md (9 instance files 09-11..09-29); SESSION_JOURNAL_*, SESSION_STATE_*,
  worker_journal_* (April-June); RESUME_20260615_*, RESUME_20260925_m2-ca1148a0.md.
- Backlog: roles/Harmonia/BACKLOG_H0H5.md (58 HARM ids). At 09-18: 26 closed, 4 superseded, 1 delegated, about 24
  open, each blocked on another seat. todo_20260901/0904/0925.md.
- What they reveal:
  - Many gates were built ahead of consumers. RESUME Q8: no lane consumed lane_gate, MULTIPLICITY or SIZING_RULE;
    "Not worth continuing is a legitimate answer for HARM-24".
  - The d3.v2 live count is blocked because the 09-10 corpus exists only in M1's SQLite archive.
  - Instance collisions.
  - M3 GANDALF had no fossil world (no WSL2/Docker/compilers), so archaeology was reading-only there.
  - The seat spent 2026-09-25..27 on operator infrastructure (Ubuntu swarm nodes), not science
    (journal/2026-09-27_m2-475d761f.md).

## 20. Research reports (paths + one line)

- roles/Harmonia/AUDIT_20260622_instrument_monoculture.md: the EC void-miner covers 4/16 known laws; "0 novel" is a
  ceiling, not exhaustion.
- roles/Harmonia/AUDIT_20260622_program_stall_map_of_disagreement.md: six-lens stall map; PROMOTE trusts
  caller-asserted survival.
- roles/Harmonia/MEASUREMENT_FLEET_2026-06-27.md: the grading oracle, M0 coverage (verify() certifies 0
  novel-shaped truths alone).
- roles/Harmonia/REVIEW_20260812_program_and_instrument_audit.md: the R6 leak; "builds instruments faster than it
  audits them"; author-independence.
- roles/Harmonia/REVIEW_20260812_syntactic_router.md: verify() rejects unregistered kinds; B-prime built; sandbox
  self-demonstration.
- roles/Harmonia/REVIEW_20260812_harmonia_C.md and _D.md: counterfactual / permanence lenses (P0-P4 ladder).
- roles/Harmonia/SYNTHESIS_20260812_harmonia_panel.md: a map of disagreement; the positive/cheat control pair.
- roles/Harmonia/POSITION_20260812_north_star_reset.md: 12,666 markdown docs vs 8 typed objects, 1 survives.
- roles/Harmonia/AUDIT_20260819_detector_band.md: 99.98% self-verdicted; nulls class-relative.
- roles/Harmonia/RETRODICTIONS_20260819_harmonia_C.md: 0/92 kills resurrect; survivors at the chance floor;
  repairs station-local.
- roles/Harmonia/BOUNDARY_DEPTH_PACKET_01_2026-09-05.txt and _02_2026-09-11.txt: SFE population is world-blind.
- roles/Harmonia/AUDIT_20260918_number_scope.md: every load-bearing number's population.
- roles/Harmonia/VACUOUS_READINGS.md: register of questions a corpus could not answer.
- roles/Harmonia/STANDING_RULES.md: rules A-F with citations and executable forms.
- roles/Harmonia/audits/EVIDENCE_AUDIT_2026-09-30*.md and RULER_QUALITY_2026-09-30.md: fleet audits.
- roles/Harmonia/rulings/*.md: 30 adjudications.
- roles/Harmonia/REVIEW_PACKET_*_2026-09-17/18.txt: external review packets (particles, ASAL, ancestry).
- roles/Harmonia/archaeology/TRIAGE_STAGE_A_2026-09-18.md: 107 cuts triaged. Trusts self-reported fields
  (helper-read).
- harmonia/memory/pattern_library.md, retraction_registry.md, symbols/protocols/null_protocol_v1.md: era-1 doctrine.
- harmonia/paper/harmonia.md and spectral_bsd.md: era-1 papers. Not read; the second is likely contaminated (s13).

## 21. Failure cases (false positives AND plausible false negatives)

False positives (historical):
- F043 identity at z -348;
- the spectral-tail and spectral-BSD survivors (zeros metadata);
- F012 6.15 (irreproducible);
- the EC torsion -> class number transfer;
- Knot GUE;
- the soak adelic_genus trap hit;
- the action-divergence excess;
- SE-1b magnitude;
- the grading oracle staircase (cheat 100% ties the reference falsifier);
- D3 30/77 fires;
- Theseus survivors at chance.

False positives the auditor itself made in era 3:
- audit J SUPPORTED;
- H4 "nearly unattainable";
- "chance-level" repeated without checking;
- an embargoed verdict in its commit subject.

Plausible false negatives:
- FN-1: spectral tail killed by "all 4 conductor bins p > 0.05" at about 1,000 curves per bin. Underpowered for rho
  about 0.05. Rank-dependent zero repulsion is real mathematics. [CODE-INFERRED CAPABILITY]
- FN-2: F010 killed at n = 51 (z = -0.86). [CODE-INFERRED CAPABILITY]
- FN-3: F3 |d| >= 0.2 and F11 > 55% kill small real effects by design (murmurations and Chebyshev-type biases are
  small). classify_kill's "resolution_limit" still yields KILLED. [IMPLEMENTATION FACT]
- FN-4: F6 cannot pass once n_hypotheses > 500 at F1's p-floor of about 1e-4. [CODE-INFERRED CAPABILITY]
- FN-5: F12-F14 row-order dependence. [CODE-INFERRED CAPABILITY]
- FN-6: kills 15/16 rested on cosine scorers later called blind to object-level pairing. [UNKNOWN / AMBIGUOUS]
- FN-7: validate.py "UNTESTED" silently replaced every TT battery verdict. [IMPLEMENTATION FACT]
- FN-8: era 3.
  - Every VACUOUS_READINGS row (C3-2 H2, H1 relevance at 3 bits, H5, D3 live, particles (c), Proteus TV) is a question
    never answered. That is a false-negative reservoir, labelled correctly.
  - Also: the 75% world-blind SFE population, and d3.v2 never measured on the real corpus (0 eligible on M2).
- FN-9: an ASAL I3 domain extremum over 650 unexecuted draws; 9 GENUINE crossers buried under the METRIC_EXPLOIT
  headline (Atlas buried-signal A7). [UNKNOWN / AMBIGUOUS]
- FN-10: the audit sample covers 13 packages chosen by Harmonia from CWO categories. Unsampled packages carry
  unknown defect rates.

## 22. Mechanism archaeology (relevant: second lane)

- [DESIGN INTENT] Definition used: Harmonia is the resurrection/equivalence stage. Its four stages:
  - R1 oracle construction, grading oracle data by provenance class (EXECUTION ... MODERN_REFERENCE_IMPLEMENTATION);
  - R2 behavioural differential tests, historical vs surrogate;
  - R3 mechanistic equivalence by ablation/substitution "where experimentally possible";
  - R4 divergence ledger.
- [HISTORICAL CLAIM] Causal lesions:
  - particles ESS-trigger: I1 R = 0 on all seeds, V ratio 17,039;
  - POET novelty estimator: four structural rows on the fossil's own bytes;
  - gzip level table: the switch at deflate.c:672, while the packet said 667 (PREDICTION_PACKET_CHALLENGE).
- [HISTORICAL CLAIM] The verdicts are explicitly "executed structural identity ... NOT CONFIRMATORY" when the rows
  were seen first and the payload is deterministic (RULING_MECH_POET_NOVELTY_ESTIMATOR_001_2026-09-30.md).
- Transplantability:
  - deferred to Theophrastus;
  - RS ruler calibrated on a pair (R-DIV-1 1865/2000, plus a 33/2000 word-level divergence nobody had listed);
  - the ancestry ruler is synthetic only;
  - R19 graded 39 ASAL rollout fossils DERIVED_RECOVERY_ARTIFACT, not ORIGINAL_AUTHORITATIVE_RELEASE.
- Donor/fossil selection: Techne/Nyx chose fossils (gzip 1.2.4, POET, ASAL Lenia, particles, Avida). Harmonia ruled
  on packets, not on selection.
- Correlation-only? The cuts are interventions on code (lesions), but a deterministic payload gives one measurement
  per label (CHARTER s3).

## 23. Novelty/prior-art audit (relevant via audits of Hecate)

- Harmonia did not run a prior-art corpus.
- It ruled that Hecate's "zero UNFAMILIAR" absence was uninstrumented. No UNFAMILIAR positive control existed, and
  Hecate later found the calibration file never held its controls.
- It ruled that NOVELTY_DETECTOR_VALIDATED is passable by a lookup table, so it validates lawful-vs-noise, not
  novelty (rule F3).
- The prior-art classification KNOWN_ANALOGUE_FOUND was triggered by the packet's own data.
- In era 1, rediscoveries of known mathematics (excised ensemble, CM -27, rank-dependent zero repulsion) were
  repeatedly first reported as features and only later relabelled as calibration. "Unfamiliar to Prometheus" vs "new
  to science" was resolved by literature found after the fact (Aporia Report 1; external reviews), not by a
  pre-search. [HISTORICAL CLAIM]

## 24. Lens inventory (descriptive)

- Qualification rule library (QR/PR/AP/FP/EX):
  - Reusable pre-run design checks: eligibility lattice, attainable set, freeze-precedes, chance floor, ceiling,
    baseline gaming.
  - Resolution ceiling: self-declared plan fields, substring matching, and a t-table with known defects.
  - Reusable core is AP-1.1.0 (fixtures from real defects).
- Vacuous-reading register plus label vocabulary: reusable epistemic bookkeeping. Low noise; depends on humans or
  agents entering rows.
- Re-execution audit of dispositions (EVIDENCE_AUDIT method):
  - Strong when the analysis is committed and deterministic.
  - Ceiling: sample size (13 packages), same-family agents, and no planted-defect calibration of the auditor.
- Detector-band / emission-path audit: a reusable "who issued the verdict" census. Demonstrated with positive and
  cheat controls.
- Conformance contract and four-state gate: engineering-grade and real. Weak as science control, because consumers
  only pin /v2/version.
- NULL_BSWCD and the era-1 battery:
  - Generic association tests on tabular arithmetic data.
  - Toy-grade calibration (4 synthetic cases).
  - Several row-order and pairing defects.
  - Reusable only after re-validation on planted positives and negatives.
- ASAL / particles / RS / ancestry rulers: specimen-specific, with controls first. Their transfer is unknown or
  synthetic-only.
- Unknowns:
  - whether any QR lane gate ever governed a real confirmatory run;
  - the audit process's own false-negative rate.

## 25. What I did not read / open questions

Not read:
- harmonia/tmp, soak, experiments, agents, runners, proposals, sweeps, primitives, composers, router, corpus, probe
  (except where cited);
- most worker journals;
- harmonia/paper/*;
- the full bodies of about 20 era-3 rulings;
- science/ s1-s18 bodies;
- the full sfe_contract.json;
- the comms DB;
- the SFE engine internals;
- the D2 protocol code (custody area, deliberately not opened beyond the record).

Not executed:
- any era-1 battery code;
- audit_primitives tests (they run git init);
- live harnesses.

Open questions:
- Was the grading-oracle R6 leak ever fixed?
- Were the 04-13 DuckDB-era survivors ever re-audited for zeros_vector metadata?
- What produced NULL_BOOT z = 8.92?
- Was B-prime ever graded?
- Did any H0-H5 lane plan ever reach a confirmatory run under QR?
- What is the verdict of record for E-003 (operator)?
