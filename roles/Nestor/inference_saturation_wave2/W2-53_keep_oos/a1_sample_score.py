"""W2-53 a1: W2-42 a4 sampling + W2-30 t2 static assay (via W2-42 a2_assay.work, unchanged) of the r1 replays.
Pool = multiset of recorded causal-lineage child genomes (gid None skipped, as W2-29's record), genome first-birth order.
Window PRIM: births with epoch <= e163 (epoch in which Bxk first reaches 163; W2-29's xk163 stop), else all births.
Window ALL : all births to the W2-37 stop.
Sample: random.Random("W2-42a4|%s|%d" % (arm, s)).sample(pool, 50) (whole pool if <= 50).
Controls F and C3 scored as a scorer check (W2-42 T3: 0.550 / 0.985).
python -B a1_sample_score.py -> a1_samples.json, a1_scores.json"""
import json, sys, pathlib, time, random
import multiprocessing as mp
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W2 = HERE.parent
sys.path.insert(0, str(W2 / "W2-42_morphfree_persisters"))
sys.path.insert(0, str(W2 / "W2-35_rotation_leak"))
from a2_assay import work, mk  # noqa
NS = 50


def pool_of(gid, births):
    cnt, order = {}, []
    for b in births:
        k = b[1]
        if k is None:
            continue
        if k not in cnt:
            cnt[k] = 0
            order.append(k)
        cnt[k] += 1
    return [gid[k] for k in order for _ in range(cnt[k])]


if __name__ == "__main__":
    t0 = time.time()
    import frames
    F = frames.IMP
    samples, todo = {}, set()
    for arm in ("FREE", "FIELD"):
        for l in open(HERE / ("r1_%s.jsonl" % arm)):
            d = json.loads(l)
            if d["mismatch"]:
                continue
            B = d["births"]
            e163 = next((b[0] for b in B if b[3] >= 163), None)
            win = {"PRIM": [b for b in B if e163 is None or b[0] <= e163], "ALL": B}
            row = {"arm": arm, "s": d["s"], "B": d["out"]["B"], "Bxk": d["out"]["Bxk"], "stop": d["out"]["stop"],
                   "epochs": d["out"]["epochs"], "e163": e163, "n_none": sum(b[1] is None for b in B)}
            jp_first = None
            for w, bs in win.items():
                pool = pool_of(d["gid"], bs)
                rng = random.Random("W2-42a4|%s|%d" % (arm, d["s"]))
                smp = pool if len(pool) <= NS else rng.sample(pool, NS)
                row[w] = {"n_pool": len(pool), "sample": smp}
                todo.update(smp)
            samples["%s_%d" % (arm, d["s"])] = row
    ctrl = {"F": F.hex(), "C3": mk(F, {43: 0xC3}).hex()}
    todo.update(ctrl.values())
    items = sorted(todo)
    print("unique genomes", len(items), flush=True)
    t1 = time.process_time()
    chunks = [[(h, h) for h in items[i::5]] for i in range(5)]
    with mp.Pool(5) as p:
        parts = p.map(work, [[h for h, _ in c] for c in chunks])
    res = dict(x for pt in parts for x in pt)
    keep = ("keepF0", "keepF1", "convF1", "convF0", "m_class", "m_FID", "m_exact")
    scores = {h: {k: res[h][k] for k in keep} for h in items}
    (HERE / "a1_samples.json").write_text(json.dumps({"samples": samples, "controls": ctrl}))
    (HERE / "a1_scores.json").write_text(json.dumps({"scores": scores, "n_unique": len(items),
                                                     "wall_s": round(time.time() - t0, 1)}))
    print("F", scores[ctrl["F"]], "\nC3", scores[ctrl["C3"]], "\nwall", round(time.time() - t0, 1))
