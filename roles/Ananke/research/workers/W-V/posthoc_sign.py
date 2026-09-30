"""W-V POST HOC (labelled, not in PLAN): 4781b0a1 single-sensor follow split by (i) the world's normal readout sign
(+ world vs - world) and (ii) the sensor's own vote (+/-) and the number of + votes in that world. champB offsets.
python posthoc_sign.py -> out/posthoc_sign.json"""
import json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np
import ana
d, m = ana.load_raw("champB")
ns0, y, sc, V = d["normal_s0"], d["y"], d["scored"], d["votes"]
Pd = int(d["Pd"]); trials = [int(k) for k in d["trials"]]
out = {}
for oi, o in enumerate(d["offsets"].tolist()):
    for q in (0, 1):
        trs = [k for k in trials if (k * Pd + o) % 2 == q]
        tr = np.zeros(ns0.shape[1], bool); tr[trs] = True
        corr = np.sign(ns0) == y
        el = corr[0::2] & corr[1::2] & sc[0::2] & tr[None]
        elw = np.repeat(el, 2, 0)
        part = np.sign(ns0.reshape(-1, 2, ns0.shape[1])[:, ::-1].reshape(ns0.shape))
        rows = {}
        for j in range(5):
            a = np.sign(d["arm_s0"][m["arms"].index(f"s{j}"), oi])
            fol = (a == part) & (a != 0)
            npos = (V == 1).sum(-1)
            for wsign in (1, -1):
                for vj in (1, -1):
                    for k_ in range(6):
                        sel = elw & (np.sign(ns0) == wsign) & (V[..., j] == vj) & (npos == k_)
                        if sel.sum():
                            key = f"world{'+' if wsign > 0 else '-'}_vote{'+' if vj > 0 else '-'}_npos{k_}"
                            r = rows.setdefault(key, [0, 0]); r[0] += int(fol[sel].sum()); r[1] += int(sel.sum())
        out[f"o{o}q{q}"] = {k: {"follow": round(v[0] / v[1], 3), "n": v[1]} for k, v in sorted(rows.items())}
        print(f"o{o}q{q}", {k: (v['follow'], v['n']) for k, v in out[f"o{o}q{q}"].items()})
(HERE / "out" / "posthoc_sign.json").write_text(json.dumps(out, indent=1))
