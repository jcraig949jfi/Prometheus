"""W2-42 a2: static assay of causal-lineage genotypes from the r1 replays, with W2-30 T2's scorer imported unchanged
(t2_neighbourhood.score: first 200 entries of the N17e/W2-24 W2-14-BASE bank panel, partner genome + carried regs,
donor ctx ZERO, both sides = 400 calls, copy errors off; m_exact / m_class (FID>=0.9 and bytes 43,44,45,49 equal) /
m_FID, per-side keep/conv). Genome set:
  controls  F, C3, AC, F+1=61, F+1=01, F+21=51, F+18=02 (W2-30 rows reproduced as a check)
  per run   top 12 donor genomes; ancestors of the first carrier of the top donor genome (founder -> it);
            dissection of the top donor genome: each diff site reverted to F (knock-out) and each diff site alone
            on F (knock-in); and for the top genome the 'core-only' (bytes 23..53 kept, rest = F) and 'edge-only'.
python -B a2_assay.py -> a2_assay.json"""
import json, sys, pathlib, time
import multiprocessing as mp
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W2 = HERE.parent
sys.path.insert(0, str(W2 / "W2-30_double_mutant"))
sys.path.insert(0, str(W2 / "W2-24_keep_variant"))
sys.path.insert(0, str(W2 / "W2-35_rotation_leak"))
RUNS = ("FULL_1438", "FULL_1469", "BANK_1505")


def work(items):
    import t2_neighbourhood as T
    T.setup()
    return [(h, T.score(bytes.fromhex(h))) for h in items]


def mk(g, muts):
    b = bytearray(g)
    for p, v in muts.items():
        b[p] = v
    return bytes(b)


def build():
    import frames
    F = frames.IMP
    jobs = {}

    def add(label, g):
        jobs.setdefault(g.hex(), []).append(label)
    for lab, m in (("F", {}), ("C3", {43: 0xC3}), ("AC", {44: 0xAC}), ("F+1=61", {1: 0x61}), ("F+1=01", {1: 0x01}),
                   ("F+21=51", {21: 0x51}), ("F+18=02", {18: 0x02})):
        add("ctrl|" + lab, mk(F, m))
    for name in RUNS:
        X = json.loads((HERE / ("r1_%s.json" % name)).read_text())
        gs = [bytes.fromhex(h) for h in X["gid"]]
        B = X["births"]
        cnt = {}
        for b in B:
            cnt[b[4]] = cnt.get(b[4], 0) + 1
        top = sorted(cnt, key=lambda k: -cnt[k])[:12]
        for rank, k in enumerate(top):
            add("%s|top%d|gid%d|donor_births%d" % (name, rank, k, cnt[k]), gs[k])
        # ancestry of first carrier of top genome
        bchild = {b[1]: b for b in B}
        oid = next(b[1] for b in B if b[5] == top[0])
        depth = 0
        while oid in bchild:
            b = bchild[oid]
            add("%s|anc|ep%d|depth-%d|gid%d" % (name, b[0], depth, b[5]), gs[b[5]])
            oid = b[2]
            depth += 1
        g = gs[top[0]]
        diffs = [i for i in range(64) if g[i] != F[i]]
        for i in diffs:
            add("%s|KO|%d:%02x>%02x" % (name, i, g[i], F[i]), mk(g, {i: F[i]}))
            add("%s|KI|%d:%02x>%02x" % (name, i, F[i], g[i]), mk(F, {i: g[i]}))
        add("%s|coreonly" % name, mk(F, {i: g[i] for i in diffs if 23 <= i <= 53}))
        add("%s|edgeonly" % name, mk(F, {i: g[i] for i in diffs if not 23 <= i <= 53}))
    return jobs


if __name__ == "__main__":
    t0 = time.time()
    jobs = build()
    items = sorted(jobs)
    chunks = [items[i::5] for i in range(5)]
    with mp.Pool(5) as pool:
        parts = pool.map(work, chunks)
    res = dict(x for p in parts for x in p)
    rows = []
    for h, labs in jobs.items():
        for lab in labs:
            rows.append({"label": lab, "hex": h, **res[h]})
    (HERE / "a2_assay.json").write_text(json.dumps({"n_unique": len(items), "rows": rows,
                                                    "wall_s": round(time.time() - t0, 1)}, indent=0))
    print("unique", len(items), "wall", round(time.time() - t0, 1))
