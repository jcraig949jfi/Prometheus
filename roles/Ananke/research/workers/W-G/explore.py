"""POST-HOC EXPLORATORY (not part of the decision): scar anatomy and
regeneration tests on the DISCOVERY namespace 0x5EB only.
E-A anatomy: at end of trial k+6, per differing element: carrier, is the
    site the sensor / the actuator, twin difference; sign vs cue.
E-B heal-all-but-X at end of trial k+2: do the other carriers re-diverge
    from X alone (X regenerates the difference) and do answers differ?
"""
import json
import sys
import pathlib
import numpy as np
import torch

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wg  # noqa: E402
from prometheus.ananke import assays  # noqa: E402

NS = 0x5EB
SEEDS = assays.world_seeds(NS, wg.M)
WANT = {"D_f7e62fe3": ["w"], "D_0ad7dc00": ["Kp", "S"], "D_6a47bd68": ["S"], "D_e79e72df": ["Kp"],
        "M2_fresh2": ["w"], "M2_fresh3": ["w", "Kp"]}


def anatomy(w, c, tw):
    out = {}
    sen = w.sch_idx[:, 0].cpu().numpy()
    act = w.read_idx[:, 0].cpu().numpy()
    for n, a in w.state_arrays().items():
        a = a.to(torch.int64).cpu().numpy()
        if n in wg.FLIGHT:
            continue
        d = a[0::2] - a[1::2]                        # [32, N, ...]
        rows = []
        for p in range(wg.NP):
            idx = np.argwhere(d[p] != 0)
            for ix in idx[:6]:
                site = int(ix[0])
                rows.append({"pair": p, "site_role": "sen" if site == sen[2 * p] else ("act" if site == act[2 * p] else "other"),
                             "idx": [int(x) for x in ix[1:]], "diff_times_c": int(d[p][tuple(ix)] * c[p])})
        if rows:
            roles = {}
            for r in rows:
                roles[r["site_role"]] = roles.get(r["site_role"], 0) + 1
            vals = [r["diff_times_c"] for r in rows]
            out[n] = {"n_elems_listed": len(rows), "roles": roles,
                      "diff_times_c_values": sorted(set(vals))[:12],
                      "frac_pos": float(np.mean(np.array(vals) > 0))}
    return out


def main():
    res = {}
    for sp in wg.specimens():
        if sp["name"] not in WANT:
            continue
        tw = wg.twin_setup(sp["ph"], sp["env"], SEEDS)
        c = tw["ylead"][:, wg.K].astype(np.int64)
        Pd = tw["Pd"]
        snap = {}
        t_end6 = (wg.K + 7) * Pd - 1
        rec = wg.run(sp, tw, hooks={t_end6: lambda w: snap.setdefault("a", anatomy(w, c, tw))})
        base_ans = np.sign(rec["trace"][tw["ro"]])
        r = {"anatomy_end_k+6": snap["a"], "heal_all_but": {}}
        for X in WANT[sp["name"]]:
            keep = set(wg.GROUPS[X])

            def hk(w, keep=keep):
                for n, a in w.state_arrays().items():
                    if n in keep:
                        continue
                    if n in wg.FLIGHT:
                        a[:, 1::2] = a[:, 0::2]
                    else:
                        a[1::2] = a[0::2]
            ne = {}

            def rec_nd(w, key):
                ne[key] = int((~wg.all_equal(w)).sum())
                ne[key + "_only_X"] = int(sum(1 for p in range(wg.NP) if all(
                    (getattr(w, n)[2 * p] == getattr(w, n)[2 * p + 1]).all() if n not in wg.FLIGHT else
                    (getattr(w, n)[:, 2 * p] == getattr(w, n)[:, 2 * p + 1]).all()
                    for n in w.state_arrays() if n not in keep)))
            th = (wg.K + 3) * Pd - 1
            hooks = {th: [hk, lambda w: rec_nd(w, "after_heal")],
                     (wg.K + 5) * Pd - 1: lambda w: rec_nd(w, "end_k+4"),
                     (wg.K + 7) * Pd - 1: lambda w: rec_nd(w, "end_k+6")}

            def multi(t):
                h = hooks[t]
                return (lambda w: [f(w) for f in h]) if isinstance(h, list) else h
            rr = wg.run(sp, tw, hooks={t: multi(t) for t in hooks})
            a = np.sign(rr["trace"][tw["ro"]])
            gd = {j: {"n_ans_diff": int((a[wg.K + j, 0::2] != a[wg.K + j, 1::2]).sum()),
                      "sum_g": float(wg.g_of(a[wg.K + j], c).sum())} for j in range(3, 9) if wg.K + j < a.shape[0]}
            r["heal_all_but"][X] = {"pairs_differing": ne, "answers": gd}
        res[sp["name"]] = r
        print(sp["name"], json.dumps(r)[:1500], flush=True)
    (HERE / "out" / "explore_0x5eb.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
