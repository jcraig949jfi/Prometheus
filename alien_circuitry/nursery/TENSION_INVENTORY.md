# Raw tension inventory (2026-09-13, repository survey for the AC-01 nursery)

Sixty-five recorded tensions from three read-only surveys of the repository (seat directories A-H, I-Z, and
math/docs/whitepapers), plus one tension tested in this task. Every line cites its file; OBSERVED means the numbers
are in that file, INFERRED means the shape is my reading. Nothing here was re-derived except the CP-vs-C6 line.
Category letters follow the harvest brief: A tiny artifact captures an oracle; B expensive oracle / cheap shadow;
C same score, different failures; D known invariant + residual; E representation inversion; F failure compression;
G local indistinguishability / global divergence; H representational ceiling; I composition surprise; J fossil
reversal; K repeated trajectory; L plasticity.

## Category distribution

A 9 | B 3 | C 5 | D 13 | E 5 | F 6 | G 7 | H 10 | I 3 | J 4 | K 2 | L 3   (some lines carry two letters; 65 lines)

## Lines that fed nursery entries

- [E] Lehmer: direct root-finding 0/17 at dps 30-100; factor-over-Z-first 17/17 at dps 30 (prometheus_math/LEHMER_PRECISION_LADDER_RESULTS.md) OBSERVED -> NUR-006
- [E/K] incubation: meet-in-the-middle operator A2/A0 = 0.0115 (~87x), v3 R3/R2 = 0.0008; experienced learner finds SEQ(o0001,o0001) at candidate #2 vs naive 1,200 candidates; random length-matched macro 3.3x WORSE (incubation/v2,v3/README.md; docs/LESSONS.md) OBSERVED -> NUR-002
- [E/F] tensor-QD: invariant-tuple canonicalisation validated 50/50 and removed the isotropy-enumeration scaling barrier; yet "mutation geometry is the proven bottleneck, not canonicalization" across 9 pilots (exploratory/tensor_decomp_qd/META_REPORT_DIRECTION_2.md; whitepapers/orbit_canonicalization.md) OBSERVED -> NUR-001 failure geometry (independent inert recurrence)
- [G] whitepapers/orbit_canonicalization.md: Strassen rank-7 rediscovered on 6/20 seeds, naive canonicaliser hashed them to 4 distinct forms OBSERVED -> NUR-001 lineage
- [C/D] Diomedes: global 5-feature 0.5633 vs single input 0.5626; within-pair 0.6600, pair x relation 0.7101; per-pair cosine 0.065; cross-relation anti-predictive 0.4885 (roles/Diomedes/CYCLE_001,003,004) OBSERVED -> NUR-004
- [D] Diomedes b2: marginal 0.789 -> conditional 0.974, PARK (CYCLE_005) OBSERVED -> NUR-004 failure geometry
- [A] pivot phase3: 13-row counter reproduces 100% of motif extractor routing, z 9.8 (pivot/sprint1/phase3/PHASE3_0_SMOKE_VERDICT) OBSERVED -> NUR-005
- [A] ergon heuristic floor 0.5225 vs LLM 0.4794 (ergon/probe/FINDING_heuristic_floor_2026-08-24.md) OBSERVED -> NUR-005
- [A/B] Ludus myopic STOP retains 98.7% of optimal EV (ludus/ledgers/cycle002_axis_ablation.json) OBSERVED -> NUR-005
- [I] Rhea/Ignis keep_gate_and_v 0.833 vs gate 0.0 / v 0.722 (rhea/runs/ablation_20260324_093552) OBSERVED -> NUR-008
- [I] Charon rules 0.254 + memo 0.254 -> 0.364 (charon/ceiling_v0/ITERATION_LOG.md) OBSERVED -> NUR-008
- [I-inverse] cross-domain T13 = 1.9x vs adjacent 11.9x, 18.9x (whitepapers/cross_domain_discovery_instrument.md) OBSERVED -> NUR-008 counter-instance
- [H] Lexis: 0.8333 = exact closure ceiling of 18 operators (484,218 states); escaping primitives 4 claimed -> 0 after permutation null (roles/Lexis/notes) OBSERVED -> NUR-009
- [H] Apollo O1: 1,737,000 pipelines, nothing above 0.833, 537x cost (apollo/cycles/o1_enumeration/FINDINGS.md) OBSERVED -> NUR-009
- [H] Harmonia monoculture: hypothesis class expresses 4/16 known structure, 2/2 found, 0/12 inexpressible (roles/Harmonia/AUDIT_20260622) OBSERVED -> NUR-009
- [G] incubation: two operators tie at 1.000 clean, split 33x vs 2x under trap (incubation/docs/LESSONS.md 11-12) OBSERVED -> NUR-010
- [G] herakles maj: exactly 0.0 under two criteria, 0.5736 vs [0.494,0.510] under a third (herakles/evca/MAJ_STRUCTURAL_ZERO.md) OBSERVED -> NUR-010
- [F] gradient archaeology: top-1 kill pattern 41.3%, top-3 86.4% of 314,971 kills (prometheus_math/GRADIENT_ARCHAEOLOGY_RESULTS.md) OBSERVED -> NUR-007
- [F/D] kill diagnosis: 64.3% confound_artifact of 3,988 (aporia/docs/FINDING_2026-08-18) OBSERVED -> NUR-007
- [F] 21 autopsies -> 5 clusters + 1 (engine/ledger/AUTOPSY_TAXONOMY.md) OBSERVED -> NUR-007
- [A, family-scoped] obstruction signature 54x lift in A149, 0 matches in A148/A150/A151 (harmonia/memory/retraction_registry.md; sigma_kernel/*validation*.json) OBSERVED -> NUR-007 failure geometry
- [C] TESTED THIS TASK: CP r16 vs C6 error correlation 0.82, stacking +0.01 R^2 (alien_circuitry/results/ac01d/nursery/cp_vs_c6_failure_geometry.json) OBSERVED -> NUR-003 (negative)
- [C] zoo GP: aggregate top-5 vs Pareto front promote complementary sets (zoo/conjecture_gp/results_2026-04-25.md) OBSERVED -> NUR-003
- [J/G] Ludus r0011: 0.25 in Martian Dice, 0.94 in Can't Stop; r0003 0.0/1.0 by partner (ludus/atlas/CIRCUIT_MATURITY.md) OBSERVED -> NUR-003

## Lines examined and NOT admitted (with the reason)

- [A/D] harmonia E: 87K h2 kills carry ~4 bits total; 44% of volume = ~0% information (harmonia/proposals/2026-06-09/E_RESULTS) OBSERVED. Reason: instrument constancy, not a mechanism; feeds NUR-007's boring explanation.
- [D] L-function gap effects 100% scale / 0% shape; residual 0.74% at t = -14.4 (charon/docs/journal_2026-04-05_finale.md) OBSERVED. Reason: residual survives in a domain with no search problem; no consumer for a search organism.
- [D] isogeny class-size signal decays N^(-0.46); later KILLED (harmonia/docs/survivor_kill_results.md; retraction_registry) OBSERVED. Reason: killed.
- [G/A] Apollo E9: 0.0667 on blind tasks, 40/42 abstentions, cause a startswith("is ") precondition (apollo/cycles/campaign_20260825/E9_FINDINGS.md) OBSERVED. Reason: battery co-adaptation; an instrument defect, feeds NUR-009's boring explanation.
- [C] aporia transfer: 0.0000 on 197 tasks because one regex (aporia/iq/FINDINGS_TRANSFER_1) OBSERVED. Reason: single regex; not a mechanism tension.
- [G] 9/10 scorers fall through to candidates[0], removal costs 0 tasks (aporia/iq/FINDINGS_CEILING_ABSTAIN) OBSERVED. Reason: inert guessing; the earlier probe perturbed what it measured (a lesson, not an organism).
- [D->refuted] oracle-ceiling predictor refuted when the ceiling moved via action count (charon/ceiling_v0/RESULTS.md) OBSERVED. Reason: refuted.
- [E/F] Q045: 20/20 LOST targets reached once p05 is named (hephaestus/prereg/READOUT_Q045_specimen3) OBSERVED. Reason: same-author caveat and a degenerate bool() gauntlet (counterfeit exhibit 008); would need re-verification before use.
- [A] counterfeit museum exhibits 001-007 (hephaestus/counterfeit_museum/README.md) OBSERVED. Reason: catalogue of instrument artifacts; consumed as boring explanations.
- [A] forge T2: NCD baseline 29.2% > mean tool 25.0%; threshold lowered (forge/STATUS_T1_T2_20260403.md) OBSERVED. Reason: recalibration, not capability.
- [H/E] Genesis D15A: I2 empty in every substrate by theorem (genesis/harmonia_a/d15a) OBSERVED + theorem. Reason: closed.
- [H] Apollo S1: map_elites fills 13 cells on a DEAD-RANDOM world (apollo/cycles/S1_archive_value) OBSERVED. Reason: coverage != value; a known lesson.
- [I/E] type-bridge: crossover 3/5 vs 0/5 (apollo/cycles/type_bridge/RESULT.json) OBSERVED. Reason: a search-operator finding inside one substrate; admitted only as context for NUR-002.
- [B] D3 null rates reconciled by exact F-tail 0.1088 vs 2.4e-8 (archaeon/docs/D3_NULL_RECONCILIATION.md) OBSERVED. Reason: statistics, not mechanism.
- [C] q100 frontiers share 32/100 (aporia/q100/OVERLAP_ANALYSIS) OBSERVED. Reason: hand-coded mapping; LLM-generated content.
- [D] tensor latent-rank ~52% attributable to density marginals; Megethos killed (harmonia/memory/retraction_registry.md) OBSERVED. Reason: killed.
- [L] Ergon landscape descriptors R^2 0.69 (ergon/meta/PHASE_2B_REPORT.md) OBSERVED. Reason: predictive, not consequential; no search reduction measured.
- [E, INFERRED] cartography kill sweep, 8 claims killed by the right null. Reason: nulls, not mechanisms.
- [D] pivot phase3 D/EFG: deltas fail pair-aware null p 0.105 (PHASE3_D/EFG verdicts) OBSERVED. Reason: feeds NUR-005 failure geometry.
- [D] kill topography: EC kill rate matches catalog volume; only a3's lattice voids carry information (pivot/kill_topography_findings) OBSERVED. Reason: volume-driven; the voids idea overlaps NUR-007 and is unmeasured as search reduction.
- [H] model sweep: 4/424 tools beat NCD; same skeleton from every model (pivot/model_sweep_results) OBSERVED. Reason: prompt-template ceiling; LLM-content.
- [A/F] Ergon single conjunct {neg_x: 4} == Charon's 4-conjunct signature (stoa/discussions/2026-05-04) OBSERVED. Reason: folded into NUR-007's transfer failure.
- [J/L] residual classifier 30/30 -> 59.5% adversarial (sigma_kernel/RESIDUAL_PRIMITIVE.md) OBSERVED. Reason: heuristic-rule brittleness; no oracle.
- [J] techne ladder 'cheaper-mechanism' instances; v1 law withdrawn (techne/loop/rung_notes/LADDER_CLAIMS_LEDGER.md) OBSERVED. Reason: a ledger, not a tension; cited as NUR-006's descendant sink.
- [J/G] Ludus circuit partner-dependence 1.0 -> 0.04 with a decoy (roles/Ludus/CYCLE_004) OBSERVED. Reason: exposure confound, see CYCLE_005 demotion.
- [D] Ludus variance share 0.10/0.23/0.62 by state weighting (roles/Ludus/CYCLE_005) OBSERVED. Reason: measurement-frame effect; a known lesson (feedback_onpolicy_score_conflates_exposure_and_competence).
- [D] greedy LoRA gain decomposes format >> prior >> template >> reasoning; shuffled labels 0.681 (roles/Ergon/GREEDY_LORA_RESULT) OBSERVED. Reason: known negative.
- [H] Harmonia 99.98% of records verdicted by their own generator (roles/Harmonia/AUDIT_20260819) OBSERVED. Reason: instrument audit.
- [G] Nyx: paper-only cut changed 7 kinds, falsified nothing; one 9 s compile falsified a control (nyx/CHOP_SHOP_CALIBRATION) OBSERVED. Reason: a doctrine result (execute, don't read); not a search organism.
- [F] Proteus 4,000 organisms -> 306 transcript classes, 0 survivors (proteus/v0, v0_5) OBSERVED. Reason: diversity collapse; no oracle-headroom framing.
- [D] REQ-027 row-permutation invariance; block-shuffle cannot falsify it (techne/OPERATOR_PORTABILITY_RESULTS.md) OBSERVED. Reason: null-design lesson.
- [D] Harmonia S1 false discovery 0.517 counting observations not worlds (roles/Harmonia/science/ledgers/s1_known_null.json) OBSERVED. Reason: statistics lesson.
- [D] Koios ec_cm_mean 3.51 vs expected 1.5 yet ADMITTED (koios/results/mpa_area1_results.json) OBSERVED. Reason: unexplained residual with no consumer named; flagged, not admitted.
- [A] kissing number from theta residues 96.6% (whitepapers/cross_domain_discovery_instrument.md) OBSERVED. Reason: predictive; no search problem.
- [A] spectral tail: zeros 5-19 cluster rank better than the first zero (whitepapers/spectral_tail_rank_discrimination.md) OBSERVED; line later KILLED per retraction registry. Reason: killed.
- [B] OEIS: mean log-ratio heuristic ~70% vs PPO (prometheus_math/OEIS_SLEEPING_RESULTS.md) OBSERVED. Reason: feeds NUR-005; no follow-up world.
- [D] descriptor collapse: KSG MI ~1.4 nats after Pearson removed (whitepapers/descriptor_collapse_audit.md) OBSERVED. Reason: predictive-residual, no search consumer.
- [H] Lehmer 0-PROMOTE ceiling cluster; BSD policies saturate at class prior (prometheus_math/*_RESULTS.md) OBSERVED. Reason: ceilings without a named alternative representation; NUR-006's transfer probe names one to try.
- [C] REINFORCE collapses to 3 bins vs PPO uniform at equal ~random accuracy (prometheus_math/MODAL_COLLAPSE_*) OBSERVED. Reason: both at chance; no headroom.
- [J] REINFORCE seeded prior washed away (prometheus_math/CATALOG_SEEDED_RESULTS.md) OBSERVED. Reason: known negative.
- [K] trace poverty: 24,000 kill records first-fail-only-coded; Mathlib4 10 tactic classes cover 97.99% of 259,560 invocations (prometheus_math/TRIANGULATION_AUDIT; README.md) OBSERVED. Reason: the Mathlib figure is a real K-shaped tension but has no exact oracle in-repo; noted for a future world.
- [L] xenolexicon FIELD_BIOLOGIST recurs cross-scale (whitepapers/xenolexicon.md) OBSERVED. Reason: LLM-content.
- [D/G] synthetic-null retraction of +1.37x..18x lifts (prometheus_math/MODAL_COLLAPSE_SYNTHETIC) OBSERVED. Reason: retracted.
- remaining lines (D/H minor instances, Sigma-kernel, pulse.md fossil counts) OBSERVED. Reason: no oracle or no headroom; listed in the survey transcripts, not repeated here.
