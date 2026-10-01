"""W2-B check C: the C1b A1.2 CARRYOVER census reads sign(signed in-flight sum). For codes whose in-flight
payload sum has the same sign in both mirror twins (rectified / presence / count codes) the predictor is
identical in the twins while the targets are negated, so the statistic is exactly .5 per pair: the
confound check cannot fire. Exploratory twin-antisymmetric variants (not prereg'd): sign of the twin
difference of the in-flight count and of the signed sum, scored against the previous target.
usage: python check_carryover.py"""
import gzip
import json

import w2b_common as c
from w2b_common import np, envs, assays, Physics
from prometheus.ananke import c1b

SPEC = ("0a23398f20cc41a2", "f6b623cdb23afd2c", "4ab2ba014aac967e")


def main():
    ck = c.Clock()
    rows = {}
    for l in gzip.open(c.ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt"):
        r = json.loads(l)
        if r["cell_id"] in SPEC and r["kind"] == "evolve":
            rows[r["cell_id"]] = r
    seeds = assays.world_seeds(c.NS + 5, 64)
    out = {}
    for cid in SPEC:
        r = rows[cid]
        ph = Physics.from_dict(r["physics"]).validate()
        env = envs.EnvSpec(**r["env"])
        g = np.asarray(r["result"]["champion"])
        run = c1b.evaluate(ph, g, env, seeds, device="cpu")
        frozen = c1b.carryover(run, env)
        tk = c1b.ticks(env)
        t_on = [t0 - 1 for t0 in tk["t0"][1:]]
        cnt = np.stack([run.tel["c_inflight_cnt"][t] for t in t_on], 1).astype(float)
        s = np.stack([run.tel["c_inflight_sum"][t] for t in t_on], 1).astype(float)
        y_prev = run.ep.y[:, :-1]
        res = {"normal": c.ci(run.pairs), "frozen_carryover": frozen,
               "twins_identical_sign_of_sum": float((np.sign(s[0::2]) == np.sign(s[1::2])).mean()),
               "twins_identical_count": float((cnt[0::2] == cnt[1::2]).mean()),
               "twins_identical_sum": float((s[0::2] == s[1::2]).mean())}
        for nm, x in (("count", cnt), ("sum", s)):
            d = np.zeros_like(x)
            d[0::2] = x[0::2] - x[1::2]
            d[1::2] = -d[0::2]                                  # antisymmetric by construction
            cc = np.where(d == 0, 0.5, (np.sign(d) == y_prev).astype(float))
            # orientation is free (a code may be + or - coded): report |acc - .5|
            pw = cc.mean(1).reshape(-1, 2).mean(-1)
            res[f"twin_diff_{nm}_prev_target"] = {**c.ci(pw), "nonzero_frac": float((d != 0).mean())}
        out[cid] = res
        print(cid, json.dumps(res, default=float), flush=True)
    out["compute"] = ck.done()
    print(out["compute"])
    c.save("check_carryover.json", out)


if __name__ == "__main__":
    main()
