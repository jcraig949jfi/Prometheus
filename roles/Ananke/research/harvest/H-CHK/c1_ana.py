"""C1 analysis: W-P truth tables (pooled + clock parity) on the plant, W-V summary, frozen reading (X2)."""
import json, time
import numpy as np
import hchk as H
t0 = time.time()
tt = H.mod("wp_tt")
d = dict(np.load(H.OUT / "c1_tt_raw.npz"))
names = [str(x) for x in d["names"]]
half = [tuple(int(v) for v in z) for z in d["subs"]]
offs = [int(o) for o in d["offsets"]]
trials = [int(k) for k in d["trials"]]
ph0, env, _ = H.champ()
ph = H.c1_physics(ph0)
comps = tt.coarse_components(ph)
site_mask = [tt.is_site(comps[k]) for k in names]
res = {k: {o: d[f"k{k}_o{o}"].astype(np.int64) for o in offs} for k in trials}
ys = {k: d[f"y_k{k}"] for k in trials}
tabs = H.wp_tables(res, ys, half, len(names), trials, offs)
wp = H.wp_summary(tabs, names, site_mask, trials, env.period(), P=128)
lines = []
for o in offs:
    for lab in ("pooled", "parity0", "parity1"):
        lines.append(H.wp_line(o, lab, wp[o][lab]))
print("\n".join(lines), flush=True)
wvout = json.load(open(H.OUT / "c1_wv_summary.json"))
rd = H.reading_c1(wp, wvout)
print("READING", json.dumps(rd, default=str), flush=True)
slim = {o: {lab: {k: s.get(k) for k in ("eligible", "fS", "fC", "fN", "fN_ci99", "base_N", "class", "polarity",
                                           "pt", "ci99", "top2", "cls", "md_top", "comp_in_R", "d_plus")}
            for lab, s in dd.items()} for o, dd in wp.items()}
H.dump({"reading": rd, "wp": slim, "names": names, "wall_s": time.time() - t0}, "c1.json")
(H.OUT / "c1_wp_table.txt").write_text("\n".join(lines) + "\n")
