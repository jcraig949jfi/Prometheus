"""W2-30 T2: mutational neighbourhoods. Parents: F, C3, C3+AC (F as baseline), reference AC.
(a) full one-bit neighbourhood (64 x 8 = 512) of each parent;
(b) all 255 alternative values at every OPERAND position of C3 / C3+AC (r._boundaries; the world's in-place
    _mutate with mutation_operator=OPERAND touches only these) plus position 43.
Each variant v: panel = first 200 entries of the N17e/W2-24 bank panel (W2-14 BASE, epochs 10-299), partner genome
+ carried registers, donor ctx ZERO, each partner run at BOTH sides (400 calls), copy errors off.
Recorded per v (all relative to v itself): m_exact (byte-identical halves), m_class (FID>=0.9 AND same bytes at
43,44,45,49), m_FID (FID>=0.9), per-side keep/conv (FID and exact).
PRE-SPECIFIED protection rule (written before any neighbour was scored): v is a PROTECTED COPIER iff
  min-side keep_FID >= thr AND max-side conv_FID >= 0.5, with thr = midpoint of parent's min-side keep_FID and
  the unprotected reference's (F for C3, AC for C3+AC), both measured on this same 400-call panel.
'unprotected copier' = max-side conv_FID >= 0.5 but keep below thr; 'non-copier' = max-side conv_FID < 0.5."""
import json, sys, pathlib, time
import multiprocessing as mp
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-24_keep_variant"))
sys.path.insert(0, str(HERE))
NP = 200
CLS = (43, 44, 45, 49)


def setup():
    global C, r, n, PAN
    from q1_trace import panel
    from tvm import C as _C
    C = _C
    r = C.runner_for_spec(C.run_ds.DONOR)
    n = r.L
    PAN = panel()[:NP]


def score(v):
    k = {"ke0": 0, "ke1": 0, "kf0": 0, "kf1": 0, "ce0": 0, "ce1": 0, "cf0": 0, "cf1": 0, "kc": 0, "cc": 0}
    for y, cy, _cx, _s in PAN:
        for s in (0, 1):
            ga, gb, sa, sb = (v, y, C.ZERO, cy) if s == 0 else (y, v, cy, C.ZERO)
            o = C.pair(r, ga, gb, sa, sb, 0.0)
            nx, ny = (o["na"], o["nb"]) if s == 0 else (o["nb"], o["na"])
            fk, fc = C.FID(v, nx) >= 0.9, C.FID(v, ny) >= 0.9
            k["ke%d" % s] += nx == v; k["ce%d" % s] += ny == v
            k["kf%d" % s] += fk; k["cf%d" % s] += fc
            k["kc"] += fk and all(nx[i] == v[i] for i in CLS)
            k["cc"] += fc and all(ny[i] == v[i] for i in CLS)
    N = NP
    d = {"m_exact": (k["ke0"] + k["ke1"] + k["ce0"] + k["ce1"]) / (2 * N),
         "m_class": (k["kc"] + k["cc"]) / (2 * N),
         "m_FID": (k["kf0"] + k["kf1"] + k["cf0"] + k["cf1"]) / (2 * N)}
    for s in (0, 1):
        d["keepF%d" % s] = k["kf%d" % s] / N; d["convF%d" % s] = k["cf%d" % s] / N
        d["keepE%d" % s] = k["ke%d" % s] / N; d["convE%d" % s] = k["ce%d" % s] / N
    return d


def work(items):
    setup()
    return [(key, score(bytes.fromhex(h))) for key, h in items]


if __name__ == "__main__":
    t0 = time.time()
    setup()
    from q1_trace import mk
    F = C.run_ds.donor_genome()
    P = {"F": F, "C3": mk(F, {43: 0xC3}), "C3+AC": mk(F, {43: 0xC3, 44: 0xAC}), "AC": mk(F, {44: 0xAC})}
    ops = {nm: [i for i in range(n) if i not in r._boundaries(P[nm])] for nm in P}
    jobs = {}
    for nm in P:
        jobs[(nm, "parent", -1, -1)] = P[nm]
    for nm in ("F", "C3", "C3+AC"):
        for i in range(n):
            for b in range(8):
                jobs[(nm, "bit", i, b)] = mk(P[nm], {i: P[nm][i] ^ (1 << b)})
    for nm in ("C3", "C3+AC"):
        for i in sorted(set(ops[nm]) | {43}):
            for val in range(256):
                if val != P[nm][i]:
                    jobs[(nm, "val", i, val)] = mk(P[nm], {i: val})
    uniq = {}
    for key, g in jobs.items():
        uniq.setdefault(g.hex(), key)
    items = [("|".join(map(str, key)), h) for h, key in uniq.items()]
    chunks = [items[i::6] for i in range(6)]
    with mp.Pool(6) as pool:
        res = dict(x for part in pool.map(work, chunks) for x in part)
    byhex = {h: res["|".join(map(str, key))] for h, key in uniq.items()}
    rows = [{"parent": k[0], "kind": k[1], "pos": k[2], "arg": k[3], "hex": g.hex(), **byhex[g.hex()]} for k, g in jobs.items()]
    out = {"NP": NP, "ops": ops, "n_unique": len(uniq), "rows": rows, "wall_s": round(time.time() - t0, 1)}
    (HERE / "t2_neighbourhood.json").write_text(json.dumps(out))
    print("unique", len(uniq), "wall", out["wall_s"])
    for nm in P:
        print(nm, byhex[P[nm].hex()])
