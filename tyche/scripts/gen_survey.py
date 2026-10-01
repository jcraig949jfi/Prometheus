"""Generator of tyche/residuals/drafted_survey.jsonl (written by the
survey-drafting agent, 2026-09-30; kept for provenance; output admitted
only through tyche.residuals.catalogue.validate)."""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "residuals", "drafted_survey.jsonl")
BY = "agent:survey-draft-2026-09-30"


def S(path, sha, quote):
    return {"path": path, "sha": sha, "quote": quote}


E = []


def add(seat, engine, phen, kind, sources, rows, note, tags, thread=None):
    E.append(dict(seat=seat, engine=engine, phenomenon=phen, residual_kind=kind,
                  sources=sources, raw_rows=rows, raw_rows_note=note,
                  links={"thread": thread, "artemis": None},
                  behaviour_tags=tags, drafted_by=BY))


ENV = "archaeon/envgate2/ENVGATE_CLOSURE_2026-09-26.md"
# 3
add("Archaeon", "archaeon", "Two ENVGATE-01 fossils are retained unresolved: in block 13 a near-copier's genome propagated with help from a foreign executor (host rescue), and in block 15 many parent-chain host labels collapse to ONE resident genetic lineage.",
    "parked", [S(ENV, "13cdec715", "**ENVGATE-01 block 13** (host rescue: a near-copier's genome propagated with help from a foreign executor) and **ENVGATE-01 block 15** (a takeover world whose many parent-chain host labels collapse to ONE resident genetic lineage).")],
    [], "off-repo: C:\\Prometheus-data\\evidence\\envgate01_2026-09-24\\", ["executor_material_decoupling", "label_collapse", "rescue_by_foreign_agent"])
# 6
add("Archaeon", "BEE", "In BEE run r038751, 27,083 births were location-foreign but own-material governed, which BEE's native pc < L self-replication criterion does not count.",
    "unexplained", [S("ops/threads/TH-002.md", "f525de9ef", "in r038751, 27,083 births were location-foreign but own-material governed.")],
    [], "off-repo: BEE's 845 traced runs are only on M2's disk", ["measure_disagreement", "location_vs_material"], "TH-002")
# 9
add("Archaeon", "BEE", "AN1: 233,499 BEE births where the writer spent most of its execution in partner or window code while its OWN material was inherited; 38,817 of them are native SR.",
    "unexplained", [S("archaeon/causal_lens/PORTABILITY01_REPORT.md", "37145999d", "AN1 (BEE) executor/material decoupling at scale: 233,499 births where the writer spent most of its execution in partner or window code while its OWN material was inherited. 38,817 of them are native SR.")],
    [], "prose only in repo; BEE traces off-repo on M2", ["decoupling", "executor_material_decoupling"])
# 10
add("Archaeon", "NPE", "NPE P-11-failing overwrite events show cross-execution in 46% of directed writes vs 11% otherwise (34 births, one specimen); the host-conditioned framing was withdrawn and whether the donor needs the victim's code is open.",
    "unexplained", [S("ops/threads/TH-003.md", "f525de9ef", "Surviving question (NPE-consistent): are P-11-failing overwrite events cross-execution-rich BECAUSE the donor cannot rebuild the victim without the victim's code? (46% vs 11%.)")],
    [], "prose only", ["association_without_cause", "reframed_after_audit"], "TH-003")
# 11
add("Archaeon", "archaeon", "The first Archaeon TH-013 measurement (founder material 0.0 at all positions in the block-13 lineage after 14,800 epochs) was retracted because the metric could not see displaced founder material; the Archaeon-vs-NPE conservation contrast is UNSUPPORTED, not refuted.",
    "instrument_ambiguity", [S("ops/threads/TH-013.md", "617c1217d", "founder material 0.0 at all positions in the block-13 dominant lineage after 14,800 epochs ... \"founder material 0.0\" is RETRACTED as unsupported ... are therefore UNSUPPORTED, not refuted.")],
    [], "corrected probe archaeon/attribution/probes/th013_block13.py; result pending in ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/", ["measure_blind_spot", "cross_engine_contrast_unresolved"], "TH-013")
# 12
add("Archaeon", "archaeon", "In Archaeon block 13 (4,079 sampled births) the share of children that are copiers differs by mechanism: SELF_COPY 86.7%, HOST_EXECUTION 47.0%, NEIGHBOUR_COPY 35.3%, ORIGINATION 0%.",
    "unexplained", [S("ops/threads/TH-015.md", "f525de9ef", "children that are copiers: SELF_COPY 86.7%, HOST_EXECUTION 47.0%, NEIGHBOUR_COPY 35.3%, ORIGINATION 0%.")],
    [], "prose only; measured by the block-13 probe (see TH-013 retraction of a different metric from the same probe)", ["capability_transmission_varies_by_mechanism", "heterogeneous_blocks"], "TH-015")
C3 = "archaeon/campaign3/CAMPAIGN_REPORT.md"
# 13
add("Archaeon", "archaeon", "The Campaign 3 delay ladder yields a delay-invariant reader in 11 of 12 seeds (held-out 1.0, including untrained d8/d16) while matched direct search almost never does; the campaign's only reproducible positive capability is unexplained.",
    "unexplained", [S(C3, "cb9135104", "11 of 12 seeds become general on delays 0/1/2/4 (held-out 1.0) ... This is the campaign's only reproducible positive capability and it is unexplained.")],
    ["archaeon/campaign3/LEDGER.jsonl"], "", ["capability_without_mechanism", "generalises_beyond_training"])
# 14
add("Archaeon", "archaeon", "In 5 of 12 Campaign 3 seeds the first delay-1 battery promoted an organism the W0 population already contained, leaving open whether the ladder mostly selects or mostly builds.",
    "unexplained", [S(C3, "cb9135104", "In 5 of 12 seeds the first delay-1 battery promoted an organism the W0 population ALREADY contained.")],
    ["archaeon/campaign3/LEDGER.jsonl"], "", ["selection_vs_construction", "preexisting_variant_promoted"])
# 16
add("Aether", "AETH-02", "AETH-02: independent stationary statistics predict edge fraction to 0.2% but over-predict persistence 3.1x: 22.0% of edges should hold 64 ticks, only 7.2% do.",
    "contradictory", [S("Aether/AETH-01/AETH-02_CLOSE_2026-09-24.md", "0e63a3d52", "Only 7.2% do. Real edges are *less* persistent than independence predicts, so something correlated is shortening their lives relative to the naive model")],
    ["Aether/AETH-01/evidence/2026-09-24_aeth02_falsifiers/falsifiers_256.json"], "", ["shortfall_under_prediction", "persistence_anomaly"])
# 17
add("Aether", "runpod", "A 305 s RunPod dependency-install tail seen once in Iteration 1 has not reproduced in 13 later samples (4.4-14.7 s) and is kept as a real, unexplained event.",
    "not_replicated", [S("Aether/runpod/COST_MODEL.md", "070eed87b", "the 305 s tail seen once in Iteration 1 has not reproduced in 13 samples since and stays in the observed range as a real, unexplained event.")],
    [], "prose only", ["one_off_outlier", "fails_to_replicate"])
# 19
add("Aether", "aether", "In v1-family laws, removing perturbation stops ~95% of template change and freezes ~93% of template bytes; no endogenous turnover mechanism is known.",
    "parked", [S("ops/threads/TH-009.md", "7113eb2b5", "removing perturbation stops ~95% of template change (AETH-02 H4) and freezes ~93% of template bytes (rcv path probe, 2026-09-27).")],
    [], "prose only", ["freezes_without_noise", "noise_dependence"], "TH-009")
# 20
add("Aether", "aether", "E-009: rcv_str replicates on pooled origins (15/128 vs a 13/128 floor) but per-seed 3/2/5/5 of 32 puts two of the four fresh seeds individually below the 0.10 floor.",
    "weak", [S("ops/campaigns/C-002/E-009/RESULT.md", "cabc6314a", "rcv_str's effect is real but small and close to the floor. Per seed (of 32): 3 / 2 / 5 / 5, so two of the four fresh seeds are individually below the 0.10 floor")],
    ["ops/campaigns/C-002/E-009/REDUCTION.json"], "", ["near_floor_effect", "pooled_passes_per_seed_fails"])
# 21
add("Ensorain", "WTP-01", "WTP-01 specimen S2 (b235013022100e1f) replicated a sudden single-checkpoint jump in 4/5 seeds while ending far worse than birth; the failure mode needs delayed credit, world structure, irreversibility and a moving world together and is UNEXPLAINED.",
    "unexplained", [S("ensorain/ENSORAIN_WTP01_REPORT.md", "092577f21", "UNEXPLAINED: a failure mode that needs delayed credit, world structure, irreversibility and a moving world together.")],
    ["ensorain/runs/wtp01/fossils/b235013022100e1f_101097.json"], "", ["jump_into_failure", "conjunctive_conditions", "control_shows_effect"])
# 22
add("Ensorain", "WTP-03", "WTP-03 substrate phase structure did not replicate: 358 Wave B crossovers, 0 REPLICATED of 12 tested.",
    "not_replicated", [S("ensorain/ENSORAIN_WTP03_REPORT.md", "a65d27ced", "358 Wave B crossovers; 0 REPLICATED of 12 tested.")],
    [], "prose only", ["fails_to_replicate_across_seeds", "phase_boundary_absent"])
# 23
add("Ensorain", "dials", "Dials retrospective: one nominal stability x consolidation coupling hit (p .022) fails a 6-test correction (.0083) and did NOT replicate in the E2 TT world (p .18).",
    "not_replicated", [S("ensorain/DIALS_RETRO.md", "0180ab244", "one nominal hit (p .022) that fails a 6-test correction (.0083) and did NOT replicate in the E2 TT world (p .18).")],
    ["ensorain/runs/e1p5_calibrate.jsonl", "ensorain/runs/e2_calibrate.jsonl"], "", ["fails_to_replicate", "multiple_comparison_fragile"])
# 25
add("Ananke", "PTE", "W-B HOLD champion 311c465f falls from 0.76 to 0.55 when distractors are removed: the champion depends on distractor input.",
    "unexplained", [S("roles/Ananke/research/workers/W-B/REPORT.md", "e3c233ed5", "Unexplained: 311c465f falls from 0.76 to 0.55 when distractors are removed. The champion depends on distractor input.")],
    [], "raw outputs under roles/Ananke/research/workers/W-B/out/ (file not pinned)", ["context_dependence", "needs_noise_to_work"])
# 26
add("Ananke", "PTE", "W-G: of the raw probe statistics only e79e72df BLANK (raw p 0.022, 0x5EB) was below 0.1, and it did not replicate.",
    "not_replicated", [S("roles/Ananke/research/workers/W-G/REPORT.md", "b0985cd10", "Of the raw probe statistics, only e79e72df BLANK (raw p 0.022, 0x5EB) was below 0.1, and it did not replicate.")],
    [], "raw outputs under roles/Ananke/research/workers/W-G/out/ (file not pinned)", ["fails_to_replicate_across_namespaces", "single_namespace_hit"])
# 27
add("Ananke", "PTE", "W-J: the C1 SAT / dense-code association did not replicate in fresh searches (0 of 4), and one ALOHA champion's code requires collisions to be erased.",
    "not_replicated", [S("roles/Ananke/research/workers/W-J/REPORT.md", "46dc8f25a", "dense-code association in C1 did not replicate in fresh searches (0 of 4). ... One ALOHA champion's code requires collisions to be erased.")],
    [], "prose only", ["fails_to_replicate", "needs_channel_loss"])
# 28
add("Ananke", "PTE", "W-R: 0x620 phase flags at offsets o1/o3 did not replicate at namespace 0x621 (PHASE EFFECT at 0 of 16 offsets), read as trial-level sampling.",
    "not_replicated", [S("roles/Ananke/research/workers/W-R/LOG.md", "f29aed544", "PHASE EFFECT at 0 of 16 offsets, no class change; per-phase = pooled everywhere. The 0x620 o1/o3 flags do not replicate")],
    [], "prose only (LOG.md)", ["fails_to_replicate_across_namespaces", "sampling_artifact_suspected"])
# 29
add("Aporia", "PTE", "PTE-C1 D-A: at M3 physics every packet has delay exactly 4 = delta, so C1's packet-ablation window can never contain the current trial's cue and the M3 \"packet ablation: no effect\" reading is vacuous.",
    "instrument_ambiguity", [S("programs/selective_irreversibility/ANOMALIES.md", "f6f58cf80", "In both M3 cells every packet has delay exactly 4 = delta (dup copies arrive at 5). So C1's window [t0, t0+delta) can NEVER contain an arrival carrying the current trial's cue")],
    [], "prose only", ["vacuous_control", "measure_blind_spot"])
# 30
add("Hecate", "hecate", "HT-e743909f97 W1: exhaustion LOWERED the onset delay (ratio 0.348 < 1), opposite sign to the hypothesis.",
    "contradictory", [S("hecate/programs/HT-e743909f97/DOSSIER.md", "ad693571a", "W1: exhaustion LOWERED the onset delay (ratio 0.348 < 1): opposite sign to the hypothesis")],
    ["hecate/programs/HT-e743909f97/worlds/W1/rows.jsonl", "hecate/programs/HT-e743909f97/worlds/W1/OUTCOME.json"], "", ["sign_reversal"])
# 31
add("Hecate", "hecate", "HT-5b0b3ebb8d W4: in TREATMENT, fail == touches_disabled for all 1747 beliefs, so the lucky-vs-grounded effect may be carried by endpoint location.",
    "instrument_ambiguity", [S("hecate/programs/HT-5b0b3ebb8d/DOSSIER.md", "23f4339f5", "in TREATMENT, fail == touches_disabled for all 1747 beliefs; a belief fails iff s or t is an interior state of the disabled mechanism.")],
    ["hecate/programs/HT-5b0b3ebb8d/worlds/W4/rows.jsonl"], "", ["outcome_determined_by_design", "confound_by_location"])
# 32
add("Hecate", "hecate", "HT-974471f045 W6: elite one-life fitness (best 0.7823) is far above instrument I_full 0.4576, and treatment elites decode better with recurrent W removed.",
    "unexplained", [S("hecate/programs/HT-974471f045/DOSSIER.md", "88bb37ada", "W6: elite one-life fitness (best 0.7823) far above instrument I_full 0.4576 ... W6: treatment elites decode better with recurrent W removed: recurrence is noise to the selected readout")],
    ["hecate/programs/HT-974471f045/worlds/W6/probe/rows.jsonl"], "", ["selection_on_luck", "ablation_improves"])
# 33a
add("Hecate", "hecate", "HT-55162c0ac0 W2: the null twin never shows the memory law, but a shuffled-fit controller stabilises whole cells (50/50 trials) in single seeds; pooled null fraction exceeded the 0.1 twin bound (0.2, then 0.4).",
    "instrument_ambiguity", [S("hecate/programs/HT-55162c0ac0/DOSSIER.md", "fefb095b2", "a shuffled-fit controller stabilises whole cells (50/50 trials) in single seeds")],
    ["hecate/programs/HT-55162c0ac0/worlds/W2/pilot_rows.jsonl"], "", ["control_shows_effect"])
# 33b
add("Hecate", "hecate", "HT-55162c0ac0 W3: opposite task orders end in different regimes (easy->hard mean 90.6 clusters, hard->easy mean 3.8) while the positive control fails.",
    "unexplained", [S("hecate/programs/HT-55162c0ac0/DOSSIER.md", "fefb095b2", "W3: TREATMENT orders end in different regimes: easy->hard (unforced at a=3.9) mean 90.6 clusters, hard->easy (unforced at a=3.7) mean 3.8 clusters")],
    ["hecate/programs/HT-55162c0ac0/worlds/W3/rows.jsonl"], "", ["order_dependence", "context_dependence"])
# 34
add("Hecate", "hecate", "HT-056d3ac561 W1: matched-run Lasso top-1 concentrates on entry 13 (49/50) while the oracle true-state-RMSE AUC is ~chance (0.476-0.558).",
    "instrument_ambiguity", [S("hecate/programs/HT-056d3ac561/DOSSIER.md", "88bb37ada", "W1: delta=0.1: oracle true-state-RMSE AUC 0.490 ~ chance ... W1: matched-run Lasso top-1 concentrated on entry 13 (49/50)")],
    ["hecate/programs/HT-056d3ac561/worlds/W1/rows.jsonl"], "", ["structured_output_without_signal", "silent_or_null_winner"])
# 35
add("Hecate", "hecate", "HT-ae38c641b1 W3: the NULL_TWIN takes exactly 2 distinct finite W values in every seed, with Kleene-cap unconverged theta in each.",
    "instrument_ambiguity", [S("hecate/programs/HT-ae38c641b1/DOSSIER.md", "88bb37ada", "W3: NULL_TWIN distinct finite W values per seed: [2, 2, 2, 2, 2]")],
    ["hecate/programs/HT-ae38c641b1/worlds/W3/rows.jsonl"], "", ["degenerate_null", "measure_collapse"])
# 39
add("Bellerophon", "Proteus", "In the playtest harness 49/60 random Proteus players are silent on the probe, and a Proteus player that never acted (actions 0) \"won\" survival with the constant-zero player's fingerprint.",
    "instrument_ambiguity", [S("roles/Bellerophon/OVERNIGHT_LEDGER_2026-09-19.md", "cfc4542f3", "the Proteus player never acted (actions 0) and \"won\" survival ... 49/60 random Proteus players are silent on the probe.")],
    [], "prose only", ["silent_or_null_winner"])
# 40
add("Nestor", "cw01", "cw01-e05 r11 records n_load_bearing = 0 of 3 carried, yet its targeted ablation cost is 57.94 against a random-removal sham of 36.53.",
    "unexplained", [S("roles/Nestor/campaigns/cw01-2026-09-17/experiments/cw01-e05/MECHANISM_OF_NULL.md", "f3fb591df", "r11 records `n_load_bearing = 0` of 3 carried, while its targeted ablation cost is 57.94 against a random-removal sham of 36.53")],
    ["roles/Nestor/campaigns/cw01-2026-09-17/experiments/cw01-e05/RESULT.json"], "", ["measure_disagreement", "effect_without_component"])
# 41a
add("Nestor", "cw01", "T-X05: amputation alone lowers burden (scalar .81-1.52 vs 1.87) without raising held64, so the e08 association of low burden with high held64 is still unexplained.",
    "unexplained", [S("roles/Nestor/campaigns/cw01-2026-09-17/loop/CYCLE_REPORT_CYCLE8_2026-09-19.md", "3af735d67", "P-D12 excluded structural pressure alone; the association (low burden, high held64) is still unexplained.")],
    ["roles/Nestor/campaigns/cw01-2026-09-17/experiments/cw01-loop2/P-D12/RESULT.json"], "", ["association_without_cause", "decoupling"])
# 41b
add("Nestor", "cw01", "T-X18: blind deletion IMPROVES raw score on average in evolved e06 bodies (TAPE -.14 relative, TREE -.04): evolved bodies carry score-harmful units.",
    "unexplained", [S("roles/Nestor/campaigns/cw01-2026-09-17/loop/BOUNDARY_REPORT_CYCLE4_2026-09-19.md", "ce97fbcc4", "Blind deletion IMPROVES raw score on average (TAPE -.14 relative, TREE -.04): evolved bodies carry score-harmful units.")],
    ["roles/Nestor/campaigns/cw01-2026-09-17/experiments/cw01-loop4/P-F09/rows.json"], "", ["ablation_improves", "deleterious_load"])
# 43
add("Ares", "ares", "Cycle 1's W4 \"plasticity 0/10\" does not replicate: on ten fresh lineages plasticity is load-bearing in about 4 of 10, and the gap is not fully explained.",
    "not_replicated", [S("ares/ARES_CYCLE2_REPORT.md", "3f68be2b9", "does not replicate; plasticity is load-bearing in about 4 of 10 fresh W4 lineages.")],
    [], "prose only", ["fails_to_replicate_across_lineages", "instrument_change"])
# 45
add("AC-01", "alien_circuitry", "AC-01: kernel-aware search is still 2.0-2.4x the oracle and count features leave 42-49% of D's variance; the distance layer is real and unexplained.",
    "unexplained", [S("alien_circuitry/SURVIVOR_GATE_RECEIPT.md", "014aa4f75", "The distance layer is real and unexplained: kernel-aware search is still 2.0-2.4x the oracle, count features leave 42-49% of D's variance")],
    [], "prose only", ["excess_over_prediction", "unexplained_variance"])
# 46
add("Koios", "koios", "Koios ec_cm_mean is 3.51 vs expected 1.5, an unexplained residual with no consumer named (flagged in the AC-01 tension inventory).",
    "unexplained", [S("alien_circuitry/nursery/TENSION_INVENTORY.md", "86a429efe", "Koios ec_cm_mean 3.51 vs expected 1.5 yet ADMITTED (koios/results/mpa_area1_results.json) OBSERVED. Reason: unexplained residual with no consumer named")],
    ["koios/results/mpa_area1_results.json"], "", ["excess_over_prediction"])
# 47
add("Ergon", "ergon", "Ergon P3: a good planted resident's descendants helped other tasks by about +0.95 pp net, a weak signal logged as residue.",
    "weak", [S("ergon/gen3/REVIEW_PACKET_P3_2026-09-11.txt", "7c1ad3729", "The planted-witness footprint (section 4) is a weak signal, not a result: a good resident's descendants helped other tasks by about +0.95 pp net. No claim; logged as residue.")],
    [], "prose only", ["spillover", "near_floor_effect"])
# 48
add("Nyx", "atlas", "Nyx atlas: CK's epoch reclamation and LMDB's freelist fail the same way (one stuck reader stops everyone) with no shared code or domain; radamsa's mutator scheduler has no signal from the target.",
    "unexplained", [S("nyx/atlas/FIRST_PASS_RETURN_2026-09-16.md", "aca5cf4c6", "radamsa's mutator scheduler has NO signal from the target ... CK's epoch reclamation and LMDB's freelist fail the same way (one stuck reader stops everyone) though no line of code is shared")],
    [], "prose only (reading claims, unmeasured)", ["convergent_failure_shape", "looks_adaptive_is_not"])
# 50
add("Aphrodite", "aphrodite", "Aphrodite engine: lineages are clones, not replicates: 1 distinct artifact across 10 seeds (dev instances seeded independently of lineage seed).",
    "instrument_ambiguity", [S("roles/Aphrodite/engine/README.md", "10ace795b", "lineages are clones, not replicates ... distinct artifacts across 10 seeds   1")],
    [], "prose only", ["pseudoreplication", "diversity_collapse"])
# 51
add("Tyche", "tyche", "Tyche v0 P5/R2/tree lenses gain on the selection seed but not reliably on fresh seeds: +0.134 vs exactly 0.000/0.000, +0.159 vs -0.006/-0.004, 0.236 vs 0.033/0.218.",
    "not_replicated", [S("tyche/runs/v0_2026-09-30/REPORT.md", "bdeba9865", "P5/R2/tree: L-3c1c67ab5c test +0.134 (z 12.3) on the selection seed, EXACTLY 0.000 on both fresh seeds; L-31c5492eec +0.159 vs -0.006/-0.004; L-cd407208ed 0.236 vs 0.033/0.218.")],
    ["tyche/runs/v0_2026-09-30/PASS_D_AUDITS.json"], "", ["fails_to_replicate_across_seeds", "selection_seed_overfit"])
# 52
add("Tyche", "tyche", "Tyche v0 P1 (delayed XOR, delays 4 and 11) stayed at the noise floor (best val gain 0.029-0.037) for all 40 generations.",
    "unexplained", [S("tyche/runs/v0_2026-09-30/REPORT.md", "bdeba9865", "P1 (delayed XOR, delays 4 and 11: each half carries zero marginal information) stayed at the noise floor (best val gain 0.029- 0.037) for all 40 generations")],
    ["tyche/runs/v0_2026-09-30/GENERATIONS.jsonl"], "", ["needle_not_reached", "no_partial_gradient"])

with open(OUT, "w", encoding="ascii", newline="\n") as f:
    for i, e in enumerate(E, 1):
        e = {"rid": "R-S%03d" % i, **e}
        f.write(json.dumps(e, ensure_ascii=True, sort_keys=True) + "\n")
print(len(E))
