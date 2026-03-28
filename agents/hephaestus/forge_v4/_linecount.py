"""Count lines in batch 2 tools."""
import os, glob

BATCH2 = [
    "thermodynamics_x_morphogenesis_x_multi-armed_bandits.py",
    "mechanism_design_x_nash_equilibrium_x_free_energy_principle.py",
    "thermodynamics_x_monte_carlo_tree_search_x_free_energy_principle.py",
    "active_inference_x_mechanism_design_x_type_theory.py",
    "thermodynamics_x_neuromodulation_x_multi-armed_bandits.py",
    "ergodic_theory_x_ecosystem_dynamics_x_theory_of_mind.py",
    "chaos_theory_x_neural_architecture_search_x_falsificationism.py",
    "bayesian_inference_x_free_energy_principle_x_model_checking.py",
    "neural_plasticity_x_pragmatics_x_free_energy_principle.py",
    "cellular_automata_x_mechanism_design_x_free_energy_principle.py",
    "ergodic_theory_x_sparse_autoencoders_x_pragmatics.py",
    "chaos_theory_x_wavelet_transforms_x_compositionality.py",
    "ergodic_theory_x_measure_theory_x_dual_process_theory.py",
    "bayesian_inference_x_free_energy_principle_x_sensitivity_analysis.py",
    "chaos_theory_x_network_science_x_free_energy_principle.py",
    "wavelet_transforms_x_pragmatics_x_free_energy_principle.py",
    "reservoir_computing_x_falsificationism_x_maximum_entropy.py",
    "chaos_theory_x_emergence_x_error_correcting_codes.py",
    "topology_x_renormalization_x_pragmatics.py",
    "statistical_mechanics_x_compressed_sensing_x_falsificationism.py",
    "evolution_x_pragmatics_x_free_energy_principle.py",
    "neuromodulation_x_multi-armed_bandits_x_model_checking.py",
    "causal_inference_x_mechanism_design_x_type_theory.py",
    "phase_transitions_x_morphogenesis_x_sparse_coding.py",
    "ecosystem_dynamics_x_multi-armed_bandits_x_free_energy_principle.py",
    "ergodic_theory_x_embodied_cognition_x_causal_inference.py",
    "neuromodulation_x_mechanism_design_x_maximum_entropy.py",
    "bayesian_inference_x_neural_oscillations_x_free_energy_principle.py",
    "tensor_decomposition_x_falsificationism_x_free_energy_principle.py",
    "thermodynamics_x_embodied_cognition_x_network_science.py",
    "predictive_coding_x_falsificationism_x_free_energy_principle.py",
    "reservoir_computing_x_active_inference_x_abductive_reasoning.py",
    "neuromodulation_x_nash_equilibrium_x_maximum_entropy.py",
    "spectral_analysis_x_falsificationism_x_criticality.py",
    "network_science_x_pragmatics_x_hoare_logic.py",
]

d = "agents/hephaestus/forge_v4"
over = []
for fn in BATCH2:
    fp = os.path.join(d, fn)
    with open(fp) as f:
        n = len(f.readlines())
    if n > 200:
        over.append((fn, n))
    print(f"  {n:4d} lines: {fn}")

if over:
    print(f"\n*** {len(over)} tools OVER 200 lines:")
    for fn, n in over:
        print(f"  {fn}: {n}")
else:
    print("\nAll tools under 200 lines.")
