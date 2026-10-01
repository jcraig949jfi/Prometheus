"""W2-17 a7: summarize r7 persistence accounting. Per (type, q_act bin): per-interaction rates of conversion,
kin re-conversion, repair of eroded kin, cost-free kin overwrite, true loss (foreign overwrite + erosion).
'net' = conv - (ow_for + erode) per member-interaction counts a kin overwrite as cost-free (W2-14 mechanism i);
'net_strict' also charges ow_kin as a loss. Pooled over runs and per run."""
import json, pathlib, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
res = {"per_run": {}, "pooled": {}}
pool = {}
for f in sorted((HERE / "r7_out").glob("*.json")):
    d = json.loads(f.read_text())
    per = {}
    for key, v in d["acc"].items():
        t, qb = key.split("|")
        qb = int(qb)
        band = "q<0.1" if qb == 0 else ("0.1-0.3" if qb <= 2 else "q>=0.3")
        for tgt in (per, pool):
            w = tgt.setdefault("%s|%s" % (t, band), {k: 0 for k in v})
            for k in v:
                w[k] += v[k]
    res["per_run"][d["label"]] = per
    H = d["hist_epoch_activeS0_activeS1_tagged"]
    res["per_run"][d["label"]]["_maxq_act"] = max((h[1] + h[2]) / 256 for h in H)
    res["per_run"][d["label"]]["_active_S0_S1_at_50_100_149"] = [(H[e][1], H[e][2]) for e in (50, 100, 149) if e < len(H)]


def rates(w):
    n = max(1, w["n"])
    return {"n": w["n"], "conv": round(w["conv"] / n, 3), "conv_kin_share": round(w["conv_kin"] / max(1, w["conv"]), 3),
            "repair_share_of_conv": round(w["conv_repair"] / max(1, w["conv"]), 3),
            "ow_kin": round(w["ow_kin"] / n, 3), "ow_for": round(w["ow_for"] / n, 3), "erode": round(w["erode"] / n, 3),
            "net": round((w["conv"] - w["ow_for"] - w["erode"]) / n, 3),
            "net_strict": round((w["conv"] - w["ow_for"] - w["erode"] - w["ow_kin"]) / n, 3)}


for k in sorted(pool):
    res["pooled"][k] = rates(pool[k])
    print("POOLED", k, res["pooled"][k])
for lab, per in res["per_run"].items():
    print(lab, "max q_act %.2f" % per["_maxq_act"], "active (S0,S1) at e50/100/149", per["_active_S0_S1_at_50_100_149"])
    for k in sorted(x for x in per if not x.startswith("_")):
        r = rates(per[k]); per[k] = r
        print("   ", k, r)
(HERE / "a7_persist.json").write_text(json.dumps(res, indent=1))
