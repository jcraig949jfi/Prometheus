#### Shared-module consumers (seat-owned code only: roles/<Seat>/ and seat-named top-level dirs)

| shared module | consuming seats | files | first use (file add date) | seats |
|---|---|---|---|---|
| pytest | 13 | 39 | 2026-05-01 | Aether, Ananke, Atalanta, Bellerophon, Charon, Crius, Harmonia, Hermes, Metis, Pronoia, Techne, Tyche, Vivarium |
| comms | 8 | 12 | 2026-09-05 | Aether, Arachne, Archaeon, Atlas, Ensorain, Pronoia, Techne, Vivarium |
| prometheus | 6 | 189 | 2026-09-23 | Aether, Ananke, Archaeon, Bellerophon, Cosmos, Odysseus |
| prometheus_math | 6 | 111 | 2026-04-25 | Aporia, Charon, Ergon, Harmonia, Techne, Theseus |
| evidence_wiki | 5 | 23 | 2026-09-05 | Archaeon, Atalanta, Atlas, Ludus, Vivarium |
| sigma_kernel | 4 | 47 | 2026-05-03 | Aporia, Charon, Ergon, Techne |
| fabric | 4 | 9 | 2026-09-27 | Ananke, Artemis, Nestor, Odysseus |
| agents | 3 | 5 | 2026-06-04 | Aporia, Arachne, Harmonia |
| pip | 2 | 2 | 2026-09-09 | Aether, Techne |
| thesauros | 2 | 19 | 2026-04-12 | Harmonia, Mnemosyne |
| prometheus_llm | 2 | 3 | 2026-09-01 | Hecate, Hephaestus |
| unittest | 2 | 4 | 2026-09-13 | Odysseus, Techne |
| prometheus_gpu | 1 | 4 | 2026-09-24 | Aether |
| blackboard_evolve | 1 | 1 | 2026-05-29 | Apollo |
| scripts | 1 | 1 | 2026-05-06 | Ergon |
| agora | 1 | 11 | 2026-04-22 | Harmonia |
| engine | 1 | 50 | 2026-09-21 | Aphrodite |
| roles | 1 | 1 | 2026-09-11 | Hypatia |
| primordial | 1 | 13 | 2026-09-16 | Nestor |
| sgp | 1 | 1 | 2026-09-12 | Techne |
| viv | 1 | 7 | 2026-09-05 | Vivarium |
| tests | 1 | 10 | 2026-09-16 | Vivarium |

#### Seat-to-seat instrument reuse (user seat code imports / path-references another seat's code)

| user seat | provider seat | files | first use | mechanism | example file |
|---|---|---|---|---|---|
| Archaeon | Proteus | 83 | 2026-09-05 | import | archaeon/campaign1/sfe01.py |
| Charon | Harmonia | 16 | 2026-05-19 | import | charon/agents/_base.py |
| Harmonia | Theseus | 16 | 2026-06-10 | import | harmonia/diagnostics/coverage_diagnostic.py |
| Archaeon | Herakles | 8 | 2026-09-10 | import | archaeon/campaign1/sfe04.py |
| Odysseus | Archaeon | 8 | 2026-09-27 | import | roles/Odysseus/expedition/census/S7_h8_matched/full_run.py |
| Charon | Techne | 6 | 2026-04-25 | import | charon/agents/stygian/loaders/composition_g24_lehmer_x_flip.py |
| Charon | Ergon | 6 | 2026-08-16 | import | charon/probe/c1c2_gate_fire_2026-09-11.py |
| Nestor | Archaeon | 6 | 2026-09-18 | import | roles/Nestor/campaigns/cw01-2026-09-17/experiments/cw01-arch4/P-H10/run_PH10.py |
| Techne | Proteus | 6 | 2026-09-10 | cli/path/import | techne/acquisition/checks/hypothesis_h1_minimiser.py |
| Techne | Ergon | 6 | 2026-08-16 | import | techne/attacks/probe_ergon_leakage_gate_2026-08-25.py |
| Nyx | Techne | 5 | 2026-09-14 | import | nyx/atlas/author.py |
| Nemesis | Archaeon | 5 | 2026-09-11 | import | roles/Nemesis/attacks/2026-09-11_eos_gate_repaired/reattack.py |
| Nestor | Proteus | 5 | 2026-09-18 | import | roles/Nestor/campaigns/cw01-2026-09-17/experiments/cw01-arch4/P-G03/run_PG03.py |
| Techne | Harmonia | 5 | 2026-08-21 | import/path | techne/fossils/capsule.py |
| Harmonia | Archaeon | 4 | 2026-09-14 | import | roles/Harmonia/qualification/h0h5/h1h0_phase2_analysis.py |
| Theophrastus | Herakles | 4 | 2026-09-13 | import | theophrastus/cross_consumer.py |
| Vivarium | Archaeon | 4 | 2026-09-06 | import | vivarium/demo_family.py |
| Vivarium | Proteus | 4 | 2026-09-09 | import | vivarium/tests/test_cegis_boolean.py |
| Archaeon | Harmonia | 3 | 2026-09-05 | path | archaeon/conformance.py |
| Ergon | Harmonia | 3 | 2026-04-14 | import | ergon/harmonia_bridge.py |
| Harmonia | Ergon | 3 | 2026-08-16 | import | harmonia/probe/c_static_leakage_probe.py |
| Polyhymnia | Archaeon | 3 | 2026-09-11 | import | roles/Polyhymnia/science/lincode_decoders.py |
| Techne | Archaeon | 3 | 2026-09-10 | cli/path/import | techne/h3_retention/c3_stream.py |
| Theseus | Tyche | 3 | 2026-09-30 | import | theseus/synth/dark.py |
| Vivarium | Herakles | 3 | 2026-09-08 | import | vivarium/tests/test_theo_req_005_derived_rule_passthrough.py |
| Ergon | Techne | 2 | 2026-05-05 | import | ergon/scripts/compute_knot_shape_fields.py |
| Harmonia | Techne | 2 | 2026-06-09 | import | harmonia/diagnostics/calibration_library_smoke.py |
| Nyx | Diomedes | 2 | 2026-09-11 | path | nyx/specimens/diomedes_k0_census/ablations/n2_controls.py |
| Nyx | Proteus | 2 | 2026-09-11 | import | nyx/specimens/hypothesis_shrinker/ablations/n1_controls.py |
| Proteus | Herakles | 2 | 2026-09-16 | import | proteus/eval/rule_table_identity.py |
| Artemis | Proteus | 2 | 2026-09-30 | import | roles/Artemis/dispatch/D002/scripts/D001-03.py |
| Odysseus | Nestor | 2 | 2026-09-28 | path | roles/Odysseus/expedition/recert/coldstart_A-001/l2_npe_p11.py |
| Theophrastus | Archaeon | 2 | 2026-09-13 | import | theophrastus/crucible.py |
| Apollo | Archaeon | 1 | 2026-09-11 | import | apollo/serendipity/workspace_guard.py |
| Aporia | Archaeon | 1 | 2026-09-11 | import | aporia/lot/run_a3.py |
| Aporia | Techne | 1 | 2026-05-05 | import | aporia/scripts/h15_run.py |
| Atlas | Archaeon | 1 | 2026-09-19 | import | atlas/__main__.py |
| Charon | Archaeon | 1 | 2026-09-11 | import | charon/probe/c1c2_gate_fire_2026-09-11.py |
| Charon | Theseus | 1 | 2026-06-22 | import | charon/probe_seam_leak.py |
| Ergon | Archaeon | 1 | 2026-09-11 | import | ergon/workspace_guard.py |
| Harmonia | Apollo | 1 | 2026-06-27 | import | harmonia/diagnostics/run_coverage_sweep.py |
| Harmonia | Charon | 1 | 2026-06-10 | import | harmonia/primitives/test_baseline_costume_parity.py |
| Hephaestus | Archaeon | 1 | 2026-09-11 | import | hephaestus/workspace_guard.py |
| Ludus | Ergon | 1 | 2026-09-01 | import | ludus/ceiling1.py |
| Nyx | Ares | 1 | 2026-09-25 | import | nyx/readings/ares_w4_reading.py |
| Nyx | Herakles | 1 | 2026-09-30 | import | nyx/readings/theo_req_003_composition.py |
| Arachne | Archaeon | 1 | 2026-09-11 | import | roles/Arachne/science/census.py |
| Artemis | Herakles | 1 | 2026-09-28 | import | roles/Artemis/challenge/experiments/FR-101/run_fr101.py |
| Artemis | Nestor | 1 | ? | path | roles/Artemis/challenge/p11/fetch_foreign.sh |
| Artemis | Ensorain | 1 | 2026-09-30 | import | roles/Artemis/dispatch/D002/scripts/D001-02.py |
| Artemis | Lexis | 1 | 2026-09-30 | path | roles/Artemis/dispatch/D002/scripts/D001-07.py |
| Artemis | Ares | 1 | 2026-09-30 | import | roles/Artemis/dispatch/D002/scripts/D001-08.py |
| Artemis | Archaeon | 1 | 2026-09-30 | import | roles/Artemis/dispatch/D004/scripts/D003-05.py |
| Elenchus | Herakles | 1 | 2026-09-11 | import | roles/Elenchus/investigations/2026-09-11_epistemic_debt/verify_d18_inertness.py |
| Harmonia | Proteus | 1 | 2026-09-17 | import | roles/Harmonia/science/proteus_current_instrument_audit.py |
| Herakles | Archaeon | 1 | 2026-09-06 | import | roles/Herakles/deep_research/2026-09-06_archaeon_template_mining/expansion_pass/ |
| Hypatia | Nemesis | 1 | 2026-09-11 | path | roles/Hypatia/science/season1/verify_ladder.py |
| Kairos | Archaeon | 1 | 2026-09-11 | import | roles/Kairos/science/claim_lint.py |
| Lexis | Archaeon | 1 | 2026-09-11 | import | roles/Lexis/workspace_guard.py |
| Nemesis | Kairos | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Hypatia | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Coeus | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Hermes | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Talos | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Clymene | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Arachne | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Harmonia | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Nemesis | Polyhymnia | 1 | 2026-09-11 | path | roles/Nemesis/science/census/classify.py |
| Odysseus | Proteus | 1 | 2026-09-27 | import | roles/Odysseus/frontier/poi/runs/R4_A-001/r4lib.py |
| Odysseus | Bellerophon | 1 | ? | path | roles/Odysseus/th006/tools/node_check.sh |
| Techne | Theseus | 1 | 2026-09-11 | cli/path | techne/scripts/forensic_inventory.py |
| Theseus | Ergon | 1 | 2026-06-15 | import | theseus/tests/test_seam_outcome_fidelity.py |
| Tyche | Hecate | 1 | 2026-09-30 | import | tyche/worlds.py |
| Vivarium | Harmonia | 1 | 2026-09-11 | path | vivarium/viv/conformance.py |