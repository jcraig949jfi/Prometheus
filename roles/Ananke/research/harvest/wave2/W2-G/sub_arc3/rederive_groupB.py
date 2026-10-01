"""Independent re-derivation of ARC3 group-B claims (W-H, W-I, W-J) from raw out/ files.

Run from the worktree root:  python roles/Ananke/research/harvest/wave2/W2-G/sub_arc3/rederive_groupB.py
Reads only JSON/CSV/NPZ outputs; imports no worker code. CPU only, seconds of compute.
"""
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["OMP_NUM_THREADS"] = "2"
import csv
import glob
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[7]          # worktree root
R = ROOT / "roles/Ananke/research"
WH, WI, WJ, WO = (R / "workers" / w / "out" for w in ("W-H", "W-I", "W-J", "W-O"))
OUT = {}


def show(k, v):
    OUT[k] = v
    print(f"{k}: {v}")


def spearman(x, y):
    def rank(a):
        a = np.asarray(a, float)
        o = a.argsort(kind="mergesort")
        r = np.empty(len(a))
        i = 0
        while i < len(a):
            j = i
            while j + 1 < len(a) and a[o[j + 1]] == a[o[i]]:
                j += 1
            r[o[i:j + 1]] = (i + j) / 2.0
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    return float(np.corrcoef(rx, ry)[0, 1])


# ---------------------------------------------------------------- W-H
print("=== W-H")
hand = json.loads((WH / "hand.json").read_text())
s4 = json.loads((WH / "hand_s4.json").read_text())
s5 = json.loads((WH / "hand_s5.json").read_text())
cf = json.loads((WH / "cf.json").read_text())
ids = json.loads((WH / "ids.json").read_text())
search = {c: json.loads((WH / f"search_{c}.json").read_text()) for c in ("b59e6c3a", "311c465f", "95649e2c")}

cells = {}
for c, key in (("b59e6c3a", "b59e6c3a/H1"), ("311c465f", "311c465f/H2"), ("95649e2c", "95649e2c/H3alt_H1")):
    champ = search[c]["champion_analysis"]
    astar = champ[1]
    # best fixed-rule program: hand (H) or searched B_fixed_L, point estimates
    b_best = max(search[c][f"B_fixed_L/{i}"]["analysis"][0] for i in range(4))
    cells[c] = dict(champ=champ[0], astar=astar, hand=hand[key]["acc"][0], hand_lo=hand[key]["acc"][1],
                    hand_ninstr=hand[key]["n_instr"], b_best=b_best,
                    faithful=(hand["95649e2c/H3"]["acc"][0] if c == "95649e2c" else None))
cells["faafa5b0"] = dict(champ=s4["champion"][0], astar=s4["A_star"], hand=s4["H4b"]["acc"][0],
                         hand_lo=s4["H4b"]["acc"][1], hand_ninstr=None, b_best=None, faithful=None)
cells["ed884172"] = dict(champ=s5["champion"][0], astar=s5["A_star"], hand=s5["H4a"]["acc"][0],
                         hand_lo=s5["H4a"]["acc"][1], hand_ninstr=None, b_best=None, faithful=None)
ncomp = 0
for c, v in cells.items():
    comp = max(v["hand"], v["b_best"] or 0) >= v["astar"]
    ncomp += comp
    v["compression"] = comp
    v["hand_beats_champ_point"] = v["hand"] >= v["champ"]
    v["hand_lo_gt_champ_point"] = v["hand_lo"] > v["champ"]
    print("  ", c, {k: (round(x, 3) if isinstance(x, float) else x) for k, x in v.items()})
show("WH_compression_cells", f"{ncomp}/{len(cells)}")
show("WH_hand_ge_champ_point", f"{sum(v['hand_beats_champ_point'] for v in cells.values())}/5")
show("WH_hand_lo99_gt_champ_mean", f"{sum(v['hand_lo_gt_champ_point'] for v in cells.values())}/5")
show("WH_S2_hand_vs_champ", f"{cells['311c465f']['hand']:.3f} vs {cells['311c465f']['champ']:.3f}")
show("WH_ninstr_recorded", {c: v["hand_ninstr"] for c, v in cells.items()})

# A_orig reach (champion's own budget, fresh seeds) -- a SEARCH outcome
for c in search:
    astar = search[c]["champion_analysis"][1]
    a = [search[c][f"A_orig/{i}"]["analysis"][0] for i in range(4)]
    show(f"WH_Aorig_reach_{c}", f"{sum(x >= astar for x in a)}/4 (A*={astar:.3f}; best {max(a):.3f})")

# switch excursion lengths (awake ticks with r != 0, consecutive) from obs npz
for c in ("b59e6c3a", "311c465f", "95649e2c"):
    z = np.load(WH / f"obs_{c}.npz")
    r, aw = z["r"], z["awake"]           # (T, W, N)
    T, W, N = r.shape
    ridx = z["ridx"][:, 0]
    lens_all, lens_ro = [], []
    for w in range(W):
        for n in range(N):
            seq = r[aw[:, w, n], w, n]     # awake ticks only
            run = 0
            for x in seq:
                if x != 0:
                    run += 1
                elif run:
                    lens_all.append(run)
                    if n == ridx[w]:
                        lens_ro.append(run)
                    run = 0
    la, lr = np.array(lens_all), np.array(lens_ro)
    show(f"WH_excursion_{c}", dict(n_excursions=int(la.size), max_awake=int(la.max()) if la.size else None,
                                   frac_le2=round(float((la <= 2).mean()), 4) if la.size else None,
                                   readout_n=int(lr.size), readout_max=int(lr.max()) if lr.size else None,
                                   readout_frac_le2=round(float((lr <= 2).mean()), 4) if lr.size else None))

# ---------------------------------------------------------------- W-I
print("=== W-I")
tables = sorted(glob.glob(str(WI / "table_*.csv")))
trajs = sorted(glob.glob(str(WI / "traj_*.json")))
show("WI_n_tables", len(tables))
show("WI_n_traj_json", len(trajs))
tt = list(csv.DictReader(open(WI / "traj_table.csv")))
show("WI_n_readable", sum(r["readable"] == "True" for r in tt))
fam = {r["cell"]: r["family"] for r in tt}
digest = {r["cell"]: r["digest"] for r in tt}
census = {r["cell"]: r["census"] for r in tt}
rclass = {r["cell"]: r["rclass"] for r in tt}
explore = json.loads((WI / "explore.json").read_text())
mid = {c: v["mid"] for c, v in explore["mid"].items()}


def my_label(o):
    v = {a: o[a]["verdict"] for a in ("site_all", "channel_all", "joint") if a in o}
    names = [a for a in o if isinstance(o[a], dict)]
    if all(o[a]["verdict"] == "NO-EFFECT" for a in names):
        return "E"
    s, c, j = v.get("site_all") == "FLIP", v.get("channel_all") == "FLIP", v.get("joint") == "FLIP"
    if s and c:
        return "D"
    if s:
        return "S"
    if c:
        return "C"
    if j:
        return "M" if (o.get("phi") is not None and o["phi"] <= -0.3) else "J"
    return "X"


labels, ro = {}, {}
for f in trajs:
    d = json.loads(Path(f).read_text())
    c = d["cell"][:8]
    ro[c] = d["ro_off"]
    labels[c] = {int(k): my_label(o) for k, o in d["offsets"].items()}
    labels[c]["_phi"] = {int(k): o.get("phi") for k, o in d["offsets"].items()}
    labels[c]["_d"] = d

# compare my letters with the worker's table letters
agree = tot = 0
for c in labels:
    rows = list(csv.DictReader(open(WI / f"table_{c}.csv")))
    for row in rows:
        tot += 1
        agree += row["reader"] == labels[c][int(row["o"])]
show("WI_my_letters_vs_table", f"{agree}/{tot}")

# site-only (all interval letters S) among readable
site_only = []
for c in labels:
    if rclass[c] == "UNREADABLE":
        continue
    rows = list(csv.DictReader(open(WI / f"table_{c}.csv")))
    iv = [labels[c][int(r["o"])] for r in rows if r["interval"] == "True"]
    if iv and all(x == "S" for x in iv):
        site_only.append(c)
hold_all = [c for c in fam if fam[c] == "HOLD"]
show("WI_site_only", dict(n=len(site_only), fams=sorted({fam[c] for c in site_only}),
                         digests=len({digest[c] for c in site_only}), n_HOLD_total=len(hold_all),
                         HOLD_not_site_only=[c for c in hold_all if c not in site_only]))

# census-JOINT cells at mid tick: M vs J (mixtures by phi), with and without W-O corrections
corr = {(r["cell"], int(r["o"])): r["reader_new"] for r in csv.DictReader(open(WO / "corrections_WI.csv"))}
joint = sorted(c for c in census if census[c] == "JOINT")
res, res_corr = {}, {}
for c in joint:
    m = mid[c]
    res[c] = (labels[c][m], None if labels[c]["_phi"][m] is None else round(labels[c]["_phi"][m], 2))
    res_corr[c] = corr.get((c, m), labels[c][m])
show("WI_joint_mid", res)
show("WI_joint_mixtures_by_phi", f"{sum(v[0]=='M' for v in res.values())}/{len(res)}")
show("WI_joint_mixtures_after_WO", f"{sum(v=='M' for v in res_corr.values())}/{len(res_corr)} {res_corr}")

# panel RELAY census-SITE cells: channel phase first?
panel_dig = "d9ccb6a71d986501"
prs = [c for c in fam if digest[c] == panel_dig and fam[c] == "RELAY" and census[c] == "SITE"]
first = {}
for c in prs:
    rows = list(csv.DictReader(open(WI / f"table_{c}.csv")))
    iv = [labels[c][int(r["o"])] for r in rows if r["interval"] == "True"]
    first[c] = "".join(iv)
show("WI_panel_relay_site_traj", f"{sum(v.startswith('C') for v in first.values())}/{len(first)} start with C; {first}")
show("WI_panel_n", sum(digest[c] == panel_dig for c in fam))
show("WI_panel_site_only", sum(c in site_only for c in fam if digest[c] == panel_dig))

# presence-as-content: channel_content FLIP while physical in-flight difference is N without V
pac, cnt_n = [], []
for c in labels:
    rows = list(csv.DictReader(open(WI / f"table_{c}.csv")))
    cc = [r for r in rows if r["interval"] == "True" and "channel_content" in (r["sub_flip"] or "")]
    kc = [r for r in rows if r["interval"] == "True" and "channel_count" in (r["sub_flip"] or "")]
    if cc and all("N" in r["phys"] and "V" not in r["phys"] for r in cc):
        pac.append(c)
    if kc and any("N" in r["phys"] for r in kc):
        cnt_n.append(c)
show("WI_presence_as_content", f"{len(pac)} {sorted(pac)} panel={sum(digest[c]==panel_dig for c in pac)}")
show("WI_count_read_as_count", sorted(cnt_n))

# w differs between twins in panel specimens; w swap verdicts
wdiff = []
for c in fam:
    if digest[c] != panel_dig:
        continue
    rows = list(csv.DictReader(open(WI / f"table_{c}.csv")))
    if any(float(r["w"] or 0) > 0 for r in rows):
        wdiff.append(c)
wflip = sum(1 for c in labels for k, o in labels[c]["_d"]["offsets"].items()
            if "w" in o and o["w"]["verdict"] in ("FLIP", "CHANCE"))
show("WI_panel_w_differs", f"{len(wdiff)}/20")
show("WI_w_swap_FLIP_or_CHANCE_any", wflip)

# slack vs latency retention (exploratory)
rob = json.loads((WI / "robust.json").read_text())
xs, ys, rows_s = [], [], []
for c in labels:
    if rclass[c] != "CHANNEL-USING":
        continue
    rows = list(csv.DictReader(open(WI / f"table_{c}.csv")))
    iv = [(int(r["o"]), labels[c][int(r["o"])]) for r in rows if r["interval"] == "True"]
    cm = [o for o, l in iv if l in ("C", "M")]
    if not cm or c not in rob:
        continue
    slack = (ro[c] - 1) - max(cm)
    b, lat = rob[c]["base"][0], rob[c]["latency"][0]
    ret = (lat - 0.5) / (b - 0.5)
    xs.append(slack); ys.append(ret); rows_s.append((c, slack, round(ret, 2)))
show("WI_slack_n", len(xs))
show("WI_slack_rho_latency", round(spearman(xs, ys), 3))
# robustness medians
site_ret = [(rob[c]["latency"][0] - .5) / (rob[c]["base"][0] - .5) for c in site_only if c in rob]
show("WI_site_only_latency_median", round(float(np.median(site_ret)), 3) if site_ret else None)

# ---------------------------------------------------------------- W-J
print("=== W-J")
e2 = sorted(glob.glob(str(WJ / "e2_*_*_[0-9].json")))
sparse, ident3, sparse_ident = 0, 0, 0
detail = []
for f in e2:
    d = json.loads(Path(f).read_text())
    em = d["held_tel"]["emit_rate"]
    tr = d["transfer"]
    a = [round(tr[o]["acc"][0], 3) for o in ("SUM", "SAT2", "ARB")]
    same = len(set(a)) == 1
    sp = em <= 0.03
    sparse += sp
    ident3 += same
    sparse_ident += sp and same
    if not same and sp:
        detail.append((Path(f).stem, a))
show("WJ_E2_n", len(e2))
show("WJ_E2_sparse_emit_le_.03", f"{sparse}/{len(e2)}")
show("WJ_E2_sparse_and_SUM=SAT2=ARB_3dp", f"{sparse_ident}/{len(e2)}; sparse but not identical: {detail}")
e5 = json.loads((WJ / "e5.json").read_text())["MAJ"]
e5b = json.loads((WJ / "e5b.json").read_text())["MAJ"]
g5 = e5["SUM"]["acc"][0] - e5["ARB"]["acc"][0]
g5b = e5b["SUM"]["acc"][0] - e5b["ARB"]["acc"][0]
show("WJ_gain_lossy_plant(SUM-ARB)", round(g5, 3))
show("WJ_gain_lossless_plant(SUM-ARB)", round(g5b, 3))
show("WJ_gain_lossless_theory(.837-.700)", round(0.837 - 0.700, 3))
show("WJ_E5b_lossless", {o: round(e5b[o]["acc"][0], 3) for o in e5b})
e6 = json.loads((WJ / "e6_SUM_MAJ_0.json").read_text())
show("WJ_E6_SUM0_transfer", {o: round(v["acc"][0], 3) for o, v in e6["transfer"].items()})
e6all = sorted(glob.glob(str(WJ / "e6_*_MAJ_[0-9].json")))
above = [(Path(f).stem, round(json.loads(Path(f).read_text())["held"]["acc"], 3)) for f in e6all]
show("WJ_E6_held", above)
e6b = json.loads((WJ / "e6b.json").read_text())
show("WJ_E6b", json.dumps(e6b)[:300])

json.dump(OUT, open(Path(__file__).with_name("rederive_groupB_out.json"), "w"), indent=1, default=str)
