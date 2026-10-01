"""W2-42 a4: static keep/m (W2-30 t2 scorer, unchanged) of
 (a) every distinct DONOR genome of the three r1 replays (births-weighted time course);
 (b) a births-weighted sample of the stored lineage CHILD genomes of all 55 W2-29 conditioned runs (22 FULL + 33 BANK
     replay; genomes_*.jsonl), up to 50 births per run drawn with random.Random('W2-42a4|arm|s') from the
     multiset of recorded births (genome repeated by its count), so successes and failures can be compared.
python -B a4_panel.py -> a4_panel.json"""
import json, sys, pathlib, time, random
import multiprocessing as mp
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W2 = HERE.parent
W29 = W2 / "W2-29_residue"
sys.path.insert(0, str(HERE))
from a2_assay import work  # noqa
NS = 50

if __name__ == "__main__":
    t0 = time.time()
    todo = set()
    donors = {}
    for name in ("FULL_1438", "FULL_1469", "BANK_1505"):
        X = json.loads((HERE / ("r1_%s.json" % name)).read_text())
        rows = [[b[0], X["gid"][b[4]], b[6] != 0] for b in X["births"]]
        donors[name] = rows
        todo.update(x[1] for x in rows)
    A = json.loads((W29 / "a2_ring.json").read_text())
    succ = {(r["arm"], r["s"]): (r["succ"], r["succB"], r["B"], r["Bxk"]) for r in A["rows"]}
    samples = {}
    for tag, arm in (("FULL", "FULL"), ("BANKREP", "BANK")):
        for l in open(W29 / ("genomes_%s.jsonl" % tag)):
            d = json.loads(l)
            if (arm, d["s"]) not in succ:
                continue
            pool = [(h, e, b) for h, e, b, c in d["genomes"] for _ in range(c)]
            rng = random.Random("W2-42a4|%s|%d" % (arm, d["s"]))
            smp = pool if len(pool) <= NS else rng.sample(pool, NS)
            samples["%s_%d" % (arm, d["s"])] = {"succ": succ[(arm, d["s"])], "n_births_recorded": len(pool),
                                                "sample": smp}
            todo.update(x[0] for x in smp)
    items = sorted(todo)
    print("unique genomes", len(items), flush=True)
    chunks = [items[i::5] for i in range(5)]
    with mp.Pool(5) as pool:
        parts = pool.map(work, chunks)
    res = dict(x for p in parts for x in p)
    keep = ("keepF0", "keepF1", "convF1", "convF0", "m_class", "m_FID", "m_exact")
    scores = {h: {k: res[h][k] for k in keep} for h in items}
    (HERE / "a4_panel.json").write_text(json.dumps({"donors": donors, "samples": samples, "scores": scores,
                                                    "wall_s": round(time.time() - t0, 1)}))
    print("done wall", round(time.time() - t0, 1))
