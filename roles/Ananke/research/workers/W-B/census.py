"""W-B Part 2: SETRULE census over qualifying C1 cells (PLAN.md Part 2)."""
import gzip, hashlib, json, pathlib, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import numpy as np
from probe import REPO, run, acc, paired, freeze, set_r, census
from prometheus.ananke import envs, lens
from prometheus.ananke.physics import Physics

OUT = pathlib.Path(__file__).parent / "out"


def cells():
    rows = []
    with gzip.open(REPO / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt") as f:
        for line in f:
            r = json.loads(line)
            if r["kind"] != "evolve":
                continue
            ph, res = r["physics"], r["result"]
            if ph["rules"] > 1 and ph["setrule"] == 1 and r["labels"].get("SIGNAL") \
                    and res.get("held") and res["held"].get("lo99", 0) > 0.55:
                rows.append(r)
    return rows


def classify(o):
    if o["F"]["v"] != "HURTS":
        return "INERT" + ("/EQUIV" if o["F"]["v"] == "EQUIV" else "/weak")
    if o["FA"]["v"] == "HURTS":
        return "ONGOING" + ("/CUE_CARRYING" if o["census"]["partner_diff_site_ticks"] > 0 else "")
    m = o["census"]["modal_rule_after_trial1"]
    if o["census"]["modal_share_after_trial1"] >= 0.99 and o[f"U{m}"]["v"] == "EQUIV":
        return "UNIFORM_BOOT" + ("/ZERO" if m == 0 else f"/R{m}")
    if o["census"]["modal_share_after_trial1"] < 0.99 and o["TS"]["v"] == "EQUIV":
        return "PATTERN_BOOT/" + ("GENERIC" if o["TX"]["v"] == "EQUIV" else "WORLD_SPECIFIC")
    if o["FA"]["v"] == "EQUIV":
        return "TRANSIENT"
    return "UNRESOLVED"


def one(r):
    ph, env = Physics.from_dict(r["physics"]), envs.EnvSpec(**r["env"])
    g = np.asarray(r["result"]["champion"], dtype=np.int64)
    Pd, R = env.period(), ph.rules
    base = run(ph, g, env, record_r=True)
    nrm = acc(base)
    B = base.r.shape[1]
    o = {"family": env.family, "wave": r["wave"], "rules": R, "held": r["result"]["held"]["acc"],
         "genome_sha": hashlib.sha256(g.tobytes()).hexdigest()[:12],
         "physics": {k: r["physics"][k] for k in ("topology", "dest_mode", "update_mode", "update_p", "wimm", "n_sites")},
         "normal": lens.ci(nrm), "census": census(base.r, Pd)}
    o["F"] = paired(acc(run(ph, g, env, pre=freeze)), nrm)
    for k in range(R):
        tr = run(ph, g, env, pre=lambda w, k=k: (set_r(k)(w), freeze(w)))
        o[f"U{k}"] = paired(acc(tr), nrm)
        o[f"U{k}_emitters"] = float(tr.stats["emitters"].mean())
    o["normal_emitters"] = float(base.stats["emitters"].mean())
    rs = base.r[2 * Pd - 1].astype(np.int64)
    o["TS"] = paired(acc(run(ph, g, env, pre=lambda w: (set_r(rs)(w), freeze(w)))), nrm)
    src = ((np.arange(B) // 2 + 1) % (B // 2)) * 2
    rx = rs[src]
    o["TX"] = paired(acc(run(ph, g, env, pre=lambda w: (set_r(rx)(w), freeze(w)))), nrm)
    later = range(2, env.trials)
    tfa = run(ph, g, env, hooks={2 * Pd - 1: freeze})
    o["FA"] = paired(acc(tfa, later), acc(base, later))
    o["class"] = classify(o)
    return o


if __name__ == "__main__":
    t0 = time.time()
    res = {}
    for r in cells():
        cid = r["cell_id"]
        try:
            res[cid] = one(r)
            o = res[cid]
            print(f"{cid[:8]} {o['family']:5s} R={o['rules']} n={o['normal'][0]:.2f} F={o['F']['arm'][0]:.2f}{o['F']['v'][0]} "
                  f"modal={o['census']['modal_rule_after_trial1']}@{o['census']['modal_share_after_trial1']:.3f} "
                  f"pdiff={o['census']['partner_diff_site_ticks']} TS={o['TS']['v'][0]} FA={o['FA']['v'][0]} -> {o['class']}", flush=True)
        except Exception as e:  # record, keep going
            res[cid] = {"error": repr(e)}
            print(cid[:8], "ERROR", repr(e), flush=True)
        (OUT / "census.json").write_text(json.dumps(res, indent=1, default=float))
    print("wall", time.time() - t0)
