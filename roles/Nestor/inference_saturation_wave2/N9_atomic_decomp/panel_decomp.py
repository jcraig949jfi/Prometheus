"""N10: N9's write-back decomposition across the 16 C-ZERO-SPECIFIC donors (dense VM, CF cell, ZERO context, copy errors
at cell rate) and its correlation with observed per-donor ZERO successes (S5 count of 3 runs)."""
import sys, json, random, pathlib, glob
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'inference_harvest_2026-09-30' / 'forensics'))
import map_common as mc
import world, p11
z8 = mc.DENSE; world.z8 = z8
r = world.Runner(mc.celld('CF'), 1, tier=mc.BASE['tier'])
n = r.L; tl = world._pow2(2 * n)
kw = dict(n=n, tape_len=tl, budget=r.t['slice'], ops_mask=r._ops_mask(), cmr=r.copy_mut)
CZ = mc.P2 / 'c_zero_specific'
G = [bytes.fromhex(d['hex']) for d in json.load(open(CZ / 'DONORS.json'))]
obs = {}
for p in glob.glob(str(CZ / 'results' / '*.json')):
    x = json.load(open(p))
    if x['policy'] == 'ZERO':
        obs.setdefault(x['donor'], []).append(bool(x['S5']))
def gw(p0, p1, p2):
    s = 0.5
    for _ in range(3000):
        s = 1 - (p0 + p1 * (1 - s) + p2 * (1 - s) ** 2)
    return max(0.0, s)
N = 600; rows = []
for k, g in enumerate(G):
    R = random.Random(9000 + k); cnt = {w: [0, 0, 0] for w in ('BASE', 'ATOMIC', 'WRITEGATE')}
    for t in range(N):
        pb = bytes(R.randrange(256) for _ in range(n)); side = t % 2
        z = (None, 0, 0)
        ga, gb = (g, pb) if side == 0 else (pb, g)
        tape, prov, lit, wo = p11.interact(z8, ga=ga, gb=gb, st_a=z, st_b=z, rng=random.Random(t), **kw)
        pre = [ga, gb]; fin = [bytes(tape[0:n]), bytes(tape[n:2 * n])]
        prom = [p11.predecessor_accepts(p11.fidelity(fin[h], pre[1 - h]), p11.fidelity(fin[h], pre[h]), wo[1 - h], n) for h in (0, 1)]
        halves = {'BASE': fin, 'ATOMIC': [fin[h] if prom[h] else pre[h] for h in (0, 1)],
                  'WRITEGATE': [fin[h] if wo[1 - h] >= n // 4 else pre[h] for h in (0, 1)]}
        for w, hs in halves.items():
            cnt[w][sum(p11.fidelity(hh, g) >= 0.9 for hh in hs)] += 1
    row = {'donor': k, 'obs_zero_S5': sum(obs.get(k, [])), 'obs_n': len(obs.get(k, []))}
    for w, c in cnt.items():
        p0, p1, p2 = (v / N for v in c); row[w] = {'m': round(p1 + 2 * p2, 3), 'P': round(gw(p0, p1, p2), 3)}
    rows.append(row); print(row, flush=True)
from scipy.stats import spearmanr
for w in ('BASE', 'ATOMIC', 'WRITEGATE'):
    print(w, spearmanr([x[w]['P'] for x in rows], [x['obs_zero_S5'] for x in rows]))
json.dump(rows, open(HERE / 'panel_decomp.json', 'w'), indent=1)
