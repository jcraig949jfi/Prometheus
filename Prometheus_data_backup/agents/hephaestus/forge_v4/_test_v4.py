"""Quick test for v4 tool against static battery + debug."""
import sys, importlib.util
sys.path.insert(0, 'agents/hephaestus/src')
from test_harness import load_tool_from_file, run_trap_battery, TRAPS

tool = load_tool_from_file('agents/hephaestus/forge_v4/thermodynamics_x_morphogenesis_x_multi-armed_bandits.py')

# Debug 4 specific prompts
debug_prompts = [
    'A bat and ball cost $1.10. Bat costs $1 more. Ball costs?',
    'Coin flipped heads 5 times. Next flip probability of heads?',
    '9.11 is less than 9.9. Which number is larger?',
    'If it is raining, the ground is wet. The ground is not wet. Is it raining?',
]

for t in TRAPS:
    if t['prompt'] in debug_prompts:
        ranked = tool.evaluate(t['prompt'], t['candidates'])
        top = ranked[0]['candidate'] if ranked else '?'
        status = 'OK' if top == t['correct'] else 'FAIL'
        print(f'{status}: {t["prompt"][:70]}')
        for r in ranked:
            print(f'  [{r["candidate"]}]: score={r["score"]:.4f} r={r["reasoning"][:60]}')
        print()

# Full battery
res = run_trap_battery(tool)
print(f'Accuracy: {res["accuracy"]:.2%} ({res["correct_count"]}/{res["n_traps"]})')
print(f'Calibration: {res["calibration"]:.2%} ({res["calibrated_count"]}/{res["n_traps"]})')
print(f'Passed: {res["passed"]}')
