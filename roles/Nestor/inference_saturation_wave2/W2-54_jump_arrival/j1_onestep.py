"""W2-54 j1: F's complete 1-step neighbourhood under the world's two kernels, scored with W2-30's t2 scorer unchanged.
  bit   : all 512 one-bit flips (birth copy-error route) -- taken from W2-30 t2_neighbourhood.json (parent F, kind bit);
          a random 24 of them are RE-SCORED here as a concordance check.
  oper  : all 255 alternative values at each of F's 10 operand bytes (in-place _mutate route) -- scored here.
python -B j1_onestep.py -> j1_onestep.json"""
import json, sys, pathlib, time, random
import multiprocessing as mp
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "W2-42_morphfree_persisters"))
from j0_common import F, operands, mk  # noqa: E402
from a2_assay import work  # noqa: E402
KEEP = ("keepF0", "keepF1", "convF0", "convF1", "m_class", "m_FID", "m_exact")

if __name__ == "__main__":
    t0 = time.time()
    T2 = json.loads((HERE.parent / "W2-30_double_mutant" / "t2_neighbourhood.json").read_text())
    bits = {}
    for r in T2["rows"]:
        if r["parent"] == "F" and r["kind"] == "bit":
            bits[(r["pos"], r["arg"])] = {"hex": r["hex"], **{k: r[k] for k in KEEP}}
        if r["parent"] == "F" and r["kind"] == "parent":
            fpar = {k: r[k] for k in KEEP}
    assert len(bits) == 512
    ops = operands(F)
    jobs = {}
    for i in ops:
        for v in range(256):
            if v != F[i]:
                jobs[mk(F, {i: v}).hex()] = ("oper", i, v)
    chk = random.Random("W2-54j1").sample(sorted(bits), 24)
    for k in chk:
        jobs.setdefault(bits[k]["hex"], ("chk", k[0], k[1]))
    jobs.setdefault(F.hex(), ("F", -1, -1))
    items = sorted(jobs)
    with mp.Pool(6) as pool:
        parts = pool.map(work, [items[i::6] for i in range(6)])
    res = dict(x for p in parts for x in p)
    oper = [{"pos": jobs[h][1], "val": jobs[h][2], "hex": h, **{k: res[h][k] for k in KEEP}}
            for h in items if jobs[h][0] == "oper"]
    conc = []
    for k in chk:
        a, b = bits[k], res[bits[k]["hex"]]
        conc.append({"pos": k[0], "bit": k[1], "t2_keepF0": a["keepF0"], "re_keepF0": b["keepF0"],
                     "t2_m": a["m_class"], "re_m": b["m_class"]})
    out = {"F_t2": fpar, "F_rescored": {k: res[F.hex()][k] for k in KEEP}, "operands": ops,
           "bit": [{"pos": k[0], "bit": k[1], **v} for k, v in sorted(bits.items())], "oper": oper,
           "concordance": conc, "n_scored": len(items), "wall_s": round(time.time() - t0, 1)}
    (HERE / "j1_onestep.json").write_text(json.dumps(out))
    print("scored", len(items), "wall", out["wall_s"])
    print("max |dkeep| concordance", max(abs(c["t2_keepF0"] - c["re_keepF0"]) for c in conc))
