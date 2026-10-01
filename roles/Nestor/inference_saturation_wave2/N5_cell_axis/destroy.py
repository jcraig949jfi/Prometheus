"""N6: per-mutation destruction of zero-context copying under C7 (OPERAND) vs CF (SLOTTED) world mutation, panel donors."""
import sys, json, random, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from escape import G, runners, run_side, mutant, n
def zero_rate(g, R, trials=8):
    best = 0.0
    for side in (0, 1):
        ok = sum(run_side(g, bytes(R.randrange(256) for _ in range(n)), side, None)[0] for _ in range(trials))
        best = max(best, ok / trials)
    return best
out = []; tot = {'C7': [0, 0], 'CF': [0, 0]}
for k, g in enumerate(G):
    R = random.Random(5000 + k)
    b = zero_rate(g, R)
    row = {'donor': k, 'base_zero': b}
    if b >= 0.5:
        for c, r in runners.items():
            d = sum(zero_rate(mutant(r, g, R), R) < 0.5 for _ in range(80))
            row[c] = d; tot[c][0] += d; tot[c][1] += 80
    out.append(row); print(row, flush=True)
print('destroyed', tot)
json.dump({'rows': out, 'tot': tot}, open(HERE / 'destroy.json', 'w'), indent=1)
