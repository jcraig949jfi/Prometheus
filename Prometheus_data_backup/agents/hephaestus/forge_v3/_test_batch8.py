"""Test all 15 category parsers against representative examples."""
import importlib.util, sys, os

def load_tool(path):
    spec = importlib.util.spec_from_file_location('t', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ReasoningTool()

tests = [
    # (prompt, [candidates], expected_substring_in_winner)
    # 1. numeric_float_comparison
    ('Is 9.11 larger than 9.9?', ['Yes, 9.11 is larger', 'No, 9.9 is larger'], 'No'),
    # 2. trick_question_equal_weight
    ('Which is heavier, a pound of feathers or a pound of steel?', ['Steel is heavier', 'They are the same weight'], 'same'),
    # 3. positional_logic
    ('You overtake the person in second place. What place are you in?', ['First place', 'Second place'], 'Second'),
    # 4. algebraic_word_problem
    ('A bat and a ball cost $1.10 total. The bat costs $1.00 more than the ball. How much does the ball cost?', ['$0.05', '$0.10'], '0.05'),
    # 5. universal_quantifier_converse_error
    ('All cats are animals. Are all animals cats?', ['Yes, all animals are cats', 'No, not all animals are cats'], 'No'),
    # 6. mathematical_identity
    ('Does 0.9999 repeating equal 1?', ['Yes, it equals 1', 'No, it does not equal 1'], 'Yes'),
    # 7. pigeonhole_principle
    ('There are 13 people and 12 months. Must at least two share a birthday month?', ['Yes, by pigeonhole', 'No, not necessarily'], 'Yes'),
    # 8. statistical_independence
    ('A fair coin has landed heads 10 times in a row. What is the probability the next flip is heads?', ['Higher than 50%', '50%'], '50'),
    # 9. number_parity
    ('Is the sum of two odd numbers always odd?', ['True, always odd', 'False, the sum is even'], 'False'),
    # 10. all_but_N_survivor
    ('You have 10 sheep. All but 3 die. How many are left?', ['3', '7'], '3'),
    # 11. negation_scope_insufficiency
    ('Not all students passed the exam. Did every student pass?', ['Yes', 'Cannot be determined from the given info'], 'Cannot'),
    # 12. stated_premise_usage
    ('5 is less than 8. Which is larger?', ['5', '8'], '8'),
    # 13. subject_object_verb_parsing
    ('The cat chased the dog. Who was chased?', ['The cat', 'The dog'], 'dog'),
    # 14. modus_tollens_contrapositive
    ('If it rains, the ground is wet. The ground is not wet. Is it raining?', ['Yes', 'No, it is not raining'], 'No'),
    # 15. transitivity
    ('Alice is taller than Bob. Bob is taller than Charlie. Who is tallest?', ['Alice', 'Charlie'], 'Alice'),
]

def run_tests(tool_path):
    tool = load_tool(tool_path)
    correct = 0
    for prompt, cands, expected in tests:
        r = tool.evaluate(prompt, cands)
        winner = r[0]['candidate']
        ok = expected.lower() in winner.lower()
        correct += int(ok)
        status = 'PASS' if ok else 'FAIL'
        print(f'  {status}: {prompt[:55]}... -> {winner[:40]}')
    pct = 100 * correct / len(tests)
    print(f'  Result: {correct}/{len(tests)} ({pct:.0f}%)')
    return correct, len(tests)

def count_lines(path):
    with open(path) as f:
        return sum(1 for _ in f)

def check_ncd_weight(path):
    """Check NCD weight is <= 15% by reading the evaluate method."""
    with open(path) as f:
        src = f.read()
    # Look for NCD contribution in score formula
    if 'ncd_s * 0.12' in src or 'ncd_s * 0.15' in src or 'ncd_s * 0.10' in src:
        return True
    return False

if __name__ == '__main__':
    d = os.path.dirname(os.path.abspath(__file__))
    # Test one representative tool
    sample = os.path.join(d, 'ibai_v2.py')
    print(f'Testing: {os.path.basename(sample)}')
    run_tests(sample)

    # Line count check
    lines = count_lines(sample)
    print(f'\n  Line count: {lines} (limit: 200) {"PASS" if lines <= 200 else "FAIL"}')

    # NCD weight check
    ncd_ok = check_ncd_weight(sample)
    print(f'  NCD <= 15%: {"PASS" if ncd_ok else "CHECK MANUALLY"}')

    # Check all 27 tools load without error
    print('\nImport check for all 27 tools:')
    batch_files = [
        "category_theory_x_phase_transitions_x_neural_architecture_search",
        "dynamical_systems_x_kalman_filtering_x_mechanism_design",
        "fractal_geometry_x_differentiable_programming_x_free_energy_principle",
        "kolmogorov_complexity_x_free_energy_principle_x_model_checking",
        "phase_transitions_x_network_science_x_maximum_entropy",
        "statistical_mechanics_x_wavelet_transforms_x_mechanism_design",
        "wavelet_transforms_x_network_science_x_compositionality",
        "bayesian_inference_x_mechanism_design_x_free_energy_principle",
        "chaos_theory_x_adaptive_control_x_compositionality",
        "epistemology_x_criticality_x_nash_equilibrium",
        "feedback_control_x_pragmatics_x_free_energy_principle",
        "gene_regulatory_networks_x_kalman_filtering_x_mechanism_design",
        "mechanism_design_x_nash_equilibrium_x_free_energy_principle",
        "prime_number_theory_x_criticality_x_model_checking",
        "sparse_autoencoders_x_global_workspace_theory_x_free_energy_principle",
        "tensor_decomposition_x_swarm_intelligence_x_analogical_reasoning",
        "wavelet_transforms_x_abductive_reasoning_x_mechanism_design",
        "chaos_theory_x_neural_plasticity_x_autopoiesis",
        "falsificationism_x_network_science_x_compositionality",
        "measure_theory_x_spectral_analysis_x_nash_equilibrium",
        "quantum_mechanics_x_metacognition_x_free_energy_principle",
        "statistical_mechanics_x_evolution_x_free_energy_principle",
        "category_theory_x_ergodic_theory_x_metacognition",
        "ergodic_theory_x_predictive_coding_x_global_workspace_theory",
        "renormalization_x_global_workspace_theory_x_criticality",
        "phase_transitions_x_network_science_x_mechanism_design",
        "ibai_v2",
    ]
    ok_count = 0
    for name in batch_files:
        path = os.path.join(d, name + '.py')
        try:
            t = load_tool(path)
            # Quick smoke test
            r = t.evaluate('Is 2 larger than 1?', ['Yes', 'No'])
            assert len(r) == 2
            ok_count += 1
        except Exception as e:
            print(f'  FAIL: {name}: {e}')
    print(f'  {ok_count}/{len(batch_files)} tools loaded and passed smoke test.')
