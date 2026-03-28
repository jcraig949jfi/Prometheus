"""Test only batch 2's 35 v4 tools."""
import sys, os
sys.path.insert(0, 'agents/hephaestus/src')
from test_harness import load_tool_from_file, run_trap_battery

BATCH2_TOOLS = [
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

forge_dir = 'agents/hephaestus/forge_v4'
results = []
for fn in BATCH2_TOOLS:
    fp = os.path.join(forge_dir, fn)
    try:
        tool = load_tool_from_file(fp)
        res = run_trap_battery(tool)
        name = fn.replace('.py','')
        adv = res.get('adversarial_accuracy', None)
        adv_str = f' adv={adv:.0%}' if adv is not None else ''
        print(f'{name[:55]:55s} acc={res["accuracy"]:.0%} cal={res["calibration"]:.0%}{adv_str} pass={res["passed"]}')
        results.append((name, res['accuracy'], res['calibration'], res['passed'], adv))
    except Exception as e:
        print(f'ERROR {fn}: {type(e).__name__}: {e}')

print(f'\n--- BATCH 2 SUMMARY ---')
n_pass = sum(1 for _,_,_,p,_ in results if p)
n_total = len(results)
avg_acc = sum(a for _,a,_,_,_ in results) / n_total if n_total else 0
avg_cal = sum(c for _,_,c,_,_ in results) / n_total if n_total else 0
avg_adv = sum(a for _,_,_,_,a in results if a is not None) / sum(1 for _,_,_,_,a in results if a is not None)
print(f'Tools: {n_total}, Passed: {n_pass}/{n_total}')
print(f'Avg accuracy: {avg_acc:.1%}, Avg calibration: {avg_cal:.1%}, Avg adversarial: {avg_adv:.1%}')
# Show which failed and why
print(f'\nFailed tools (pass=False):')
for name, acc, cal, passed, adv in results:
    if not passed:
        reason = ''
        if adv is not None and adv < 0.5:
            reason = f'adversarial={adv:.0%}<50%'
        elif acc <= 0.2:
            reason = f'acc={acc:.0%}<=NCD'
        else:
            reason = f'acc={acc:.0%} cal={cal:.0%}'
        print(f'  {name[:55]:55s} {reason}')
