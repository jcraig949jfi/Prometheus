"""W2-22 p2: the world itself (FIELD+FULL = bit-exact world pair epoch, W2-14 v0) under ATOMIC on C-ATOMIC seeds
12_000_000+s, s=0..29, horizon 300, ffield.run unchanged. Joined to C-ATOMIC's 2000-epoch world depth. -> runs_ATOMIC_world.jsonl"""
import json, time
import multiprocessing as mp
import w22
F = w22.F
CAT = F.CAMP / "c9x-explore-2026-09-24" / "c_atomic" / "results"
def job(s):
    t0 = time.process_time()
    res = F.run("ATOMIC", 12_000_000 + s, "FIELD", "FULL", T=300, traj=False)
    res["s"] = s
    res["cpu_s"] = round(time.process_time() - t0, 2)
    p = CAT / ("7ae3f9c1437c8000_%d_ATOMIC.json" % (12_000_000 + s))
    res["world2000_depth"] = json.loads(p.read_text())["depth"] if p.exists() else None
    return res
if __name__ == "__main__":
    with mp.Pool(6) as p, open(w22.HERE / "runs_ATOMIC_world.jsonl", "a") as fh:
        for res in p.imap_unordered(job, range(30)):
            fh.write(json.dumps(res) + "\n"); fh.flush()
            print(res["s"], res["stop"], res["epochs"], "B", res["B"], "maxA", res["maxA"], "dF", res["depth_f"], "dW", res["depth_world"], "w2000", res["world2000_depth"], res["cpu_s"], flush=True)
    print("DONE", flush=True)
