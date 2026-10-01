"""Known answer: batched evaluation reproduces W2-M's recorded score_null.json numbers exactly
(dev accs for every member, held acc, DICT acc) at 3 W2-M-scored rows, and hp_common.evaluate on one block.
Also times 1 vs 2 threads is done externally (AF_THREADS)."""
import af_common as c
import json, numpy as np, time
import w2m_plants as wp
from score_rows import genome, MENU
from prometheus.ananke import envs
from prometheus.ananke.physics import Physics
from prometheus.ananke.engine import Controls

W = {o["cell"][:8]: o for o in json.load(open(c.HERE.parent / "W2-M/out/score_null.json"))["rows"]}
R = {r["cell_id"][:8]: r for r in c.hc.rows()}
ck = c.Clock(); res = []
for cid in ["48dbe2a1", "8c5eba06", "c7ec8097"]:
    o = W[cid]; r = R[cid]
    ph = Physics.from_dict(r["physics"]).validate(); env = envs.EnvSpec(**r["env"])
    dev = c.dev_seeds(r); held = c.held_seeds(r)
    names = [k for k, v in o["dev"].items() if v["fits"]]
    jobs = [(genome(n, ph)[1], dev, False) for n in names]
    t0 = time.process_time()
    out = c.batch_eval(ph, env, jobs)
    tb = time.process_time() - t0
    ok_dev = all(abs(out[i]["acc"] - o["dev"][n]["acc"]) < 1e-12 for i, n in enumerate(names))
    g = genome(o["selected"], ph)[1]
    h, d = c.batch_eval(ph, env, [(g, held, False), (g, held, True)])
    t0 = time.process_time(); e1 = c.hc.evaluate(ph, g, env, held); ts = time.process_time() - t0
    z = c.batch_eval(ph, env, [(g, held, False)], ctrl=Controls(zero_comm=True))[0]
    rec = {"cell": cid, "dev_match": ok_dev, "held_match": abs(h["acc"] - o["held"]["acc"]) < 1e-12,
           "dict_match": abs(d["acc"] - o["DICT"]["acc"]) < 1e-12, "hp_eval_match": abs(e1["acc"] - h["acc"]) < 1e-12,
           "zero_comm": z["acc"], "cpu_batch_dev_s": round(tb, 2), "n_dev_jobs": len(names), "cpu_single64_s": round(ts, 2)}
    print(rec, flush=True); res.append(rec)
c.save(f"ka_batch_t{c.NT}.json", {"rows": res, "compute": ck.done()}); print(ck.done())
