"""N7: does the background partner field differ by cell operator in a way that changes founder fate?
Static: partner pools = random genomes after A world-mutation events under C7 vs CF operator; founder (panel donor)
retention (own half not overwritten by a predecessor-accepted partner copy) and conversion, zero context, both sides."""
import sys, json, random, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from escape import G, runners, n, z8, tl, budget, mask
import p11
def interact(g, pb, side):
    ga, gb = (g, pb) if side == 0 else (pb, g)
    tape, prov, lit, wo = p11.interact(z8, n=n, tape_len=tl, ga=ga, gb=gb, st_a=(None, 0, 0), st_b=(None, 0, 0), budget=budget,
                                       ops_mask=mask, cmr=0.0, rng=random.Random(0))
    h = 0 if side == 0 else n; o = n - h
    fh, ph = bytes(tape[h:h + n]), bytes(tape[o:o + n])
    lost = p11.predecessor_accepts(p11.fidelity(fh, pb), p11.fidelity(fh, g), wo[1 - side], n)
    conv = p11.predecessor_accepts(p11.fidelity(ph, g), p11.fidelity(ph, pb), wo[side], n)
    return lost, conv
def pool(op, age, k, seed):
    R = random.Random(seed); r = runners[op]; r.rng = R; out = []
    for _ in range(k):
        g = bytes(R.randrange(256) for _ in range(n))
        for _ in range(age):
            g = r._mutate(g)
        out.append(g)
    return out
res = {}
for age in (0, 60, 240):
    for op in ('C7', 'CF'):
        P = pool(op, age if age else 0, 300, 77 + age)
        L = C = T = 0
        for g in G:
            for i, pb in enumerate(P[:120]):
                l, c = interact(g, pb, i % 2)
                L += l; C += c; T += 1
        res['%s/age%d' % (op, age)] = {'founder_lost': round(L / T, 4), 'converted': round(C / T, 4), 'n': T}
        print(op, age, res['%s/age%d' % (op, age)], flush=True)
json.dump(res, open(HERE / 'field.json', 'w'), indent=1)
