"""Inspect adversarial grid to understand failure patterns."""
import json, sys, os
sys.path.insert(0, 'agents/hephaestus/src')
from test_harness import load_tool_from_file

grid = json.loads(open('agents/nemesis/grid/grid.json').read())

# Show one example per category
seen = set()
for cell in grid.get('cells', []):
    t = cell.get('task', {})
    cat = t.get('category', '')
    if cat not in seen:
        seen.add(cat)
        print(f'[{cat}]')
        print(f'  prompt: {t.get("prompt","")[:120]}')
        print(f'  candidates: {t.get("candidates",[])}')
        print(f'  correct: {t.get("correct","")}')
        print()

# Now test our weakest tool against the grid and show failures
print("=" * 72)
print("Failure analysis for thermodynamics_x_morphogenesis_x_multi-armed_bandits")
tool = load_tool_from_file('agents/hephaestus/forge_v4/thermodynamics_x_morphogenesis_x_multi-armed_bandits.py')

fails_by_cat = {}
for cell in grid.get('cells', []):
    t = cell.get('task', {})
    if not t.get('prompt'): continue
    try:
        ranked = tool.evaluate(t['prompt'], t['candidates'])
        top = ranked[0]['candidate'] if ranked else '?'
        if top != t['correct']:
            cat = t.get('category', 'unknown')
            fails_by_cat.setdefault(cat, []).append({
                'prompt': t['prompt'][:100],
                'expected': t['correct'],
                'got': top,
                'reasoning': ranked[0]['reasoning'][:60] if ranked else '?'
            })
    except Exception as e:
        cat = t.get('category', 'unknown')
        fails_by_cat.setdefault(cat, []).append({'prompt': t['prompt'][:100], 'error': str(e)[:60]})

print(f'\nFailed {sum(len(v) for v in fails_by_cat.values())} adversarial tasks:')
for cat, fails in sorted(fails_by_cat.items(), key=lambda x: -len(x[1])):
    print(f'\n  [{cat}] ({len(fails)} failures):')
    for f in fails[:3]:
        if 'error' in f:
            print(f'    ERROR: {f["prompt"][:80]} -> {f["error"]}')
        else:
            print(f'    {f["prompt"][:80]}')
            print(f'      expected={f["expected"][:50]}, got={f["got"][:50]}')
            print(f'      reason={f["reasoning"]}')
