"""Test all v4 batch 2 tools against static + adversarial batteries."""
import sys, os, glob
sys.path.insert(0, 'agents/hephaestus/src')
from test_harness import load_tool_from_file, run_trap_battery

forge_dir = 'agents/hephaestus/forge_v4'
files = sorted(glob.glob(os.path.join(forge_dir, '*.py')))
files = [f for f in files if not os.path.basename(f).startswith('_')]

results = []
for fp in files:
    try:
        tool = load_tool_from_file(fp)
        res = run_trap_battery(tool)
        name = os.path.basename(fp).replace('.py','')
        adv_acc = res.get('adversarial_accuracy', None)
        adv_str = f' adv={adv_acc:.0%}' if adv_acc is not None else ''
        print(f'{name[:55]:55s} acc={res["accuracy"]:.0%} cal={res["calibration"]:.0%}{adv_str} pass={res["passed"]}')
        results.append((name, res['accuracy'], res['calibration'], res['passed'], adv_acc))
    except Exception as e:
        print(f'ERROR {os.path.basename(fp)}: {type(e).__name__}: {e}')

print(f'\n--- SUMMARY ---')
n_pass = sum(1 for _,_,_,p,_ in results if p)
n_total = len(results)
avg_acc = sum(a for _,a,_,_,_ in results) / n_total if n_total else 0
avg_cal = sum(c for _,_,c,_,_ in results) / n_total if n_total else 0
print(f'Tools: {n_total}, Passed: {n_pass}/{n_total}')
print(f'Avg accuracy: {avg_acc:.1%}, Avg calibration: {avg_cal:.1%}')
