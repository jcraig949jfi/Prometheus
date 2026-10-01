"""N11: C-ZERO-SPECIFIC donors screened from zero vs 0x5A vs random register entry states (both sides, 20 random partners)."""
import sys, json, random, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from escape import G, run_side, n
rows = []
for k, g in enumerate(G):
    R = random.Random(321 + k); row = {'donor': k}
    for name, regs in (('ZERO', None), ('CONST5A', [0x5A] * 8)):
        best = 0
        for side in (0, 1):
            ok = sum(run_side(g, bytes(R.randrange(256) for _ in range(n)), side, regs)[0] for _ in range(20))
            best = max(best, ok / 20)
        row[name] = best
    best = 0
    for side in (0, 1):
        ok = sum(run_side(g, bytes(R.randrange(256) for _ in range(n)), side, [R.randrange(256) for _ in range(8)])[0] for _ in range(20))
        best = max(best, ok / 20)
    row['RANDOM'] = best
    rows.append(row); print(row)
print('competent (>=0.5): ZERO', sum(r['ZERO'] >= .5 for r in rows), 'CONST5A', sum(r['CONST5A'] >= .5 for r in rows), 'RANDOM', sum(r['RANDOM'] >= .5 for r in rows))
json.dump(rows, open(HERE / 'const_screen.json', 'w'), indent=1)
