"""Build the per-row tables from out/*.json (no engine)."""
import json, glob, collections, gzip, pathlib
O = pathlib.Path(__file__).parent / "out"
def load(pat):
    rs = []
    for f in sorted(glob.glob(str(O / pat))): rs += json.load(open(f))["rows"]
    return {r["cell"]: r for r in rs}
base, ref, thin = load("t1_base_M64_*of4.json"), load("t1_refresh_M32_*of4.json"), load("t1_thin_M16_*.json")
full = {}; [full.update({(r["cell"], r["variant"]): r}) for r in load("t4_full_*.json").values()]
for f in glob.glob(str(O / "t4_full_*.json")):
    for r in json.load(open(f))["rows"]: full[(r["cell"], r["variant"])] = r
abl = {}
for f in glob.glob(str(O / "t4_abl_*.json")):
    for r in json.load(open(f))["rows"]: abl[(r["cell"], r["variant"])] = r
lines = []; cls = collections.Counter(); diag = collections.Counter()
for c in sorted(base, key=lambda c: (-base[c]["acc"], c)):
    b = base[c]; p = b["phys"]; e = b["env"]
    R = ref.get(c); T = thin.get(c)
    tags = []
    if p["decay_shift"] > 0: tags.append(f"decay{p['decay_shift']}")
    if p["cap"] > 0 and p["collision"] != "none": tags.append(f"cap{p['cap']}{p['collision'][:3]}")
    if p["loss"] >= 0.3: tags.append(f"loss{p['loss']}")
    if p["update_mode"] == "async": tags.append(f"async{p['update_p']}")
    if p["topology"] == "global": tags.append("global")
    if p["economy_on"] if "economy_on" in p else (p["c_emit"] or p["c_op"] or p["c_mem"]): tags.append("econ")
    ff = "-"
    if b["exact_space"] and b["lo99"] > 0.55:
        k = "PLANT-SOLVED"; reading = f"base exact {b['acc']:.3f} [{b['lo99']:.3f},{b['hi99']:.3f}] M64"
        a = abl.get((c, "base"))
        if c.startswith("6f82"): ff = "PASS (paired diff lo99 .359; teachers-removed .516)"
        elif a: ff = f"PASS (conservative diff >= {b['lo99'] - a['abl_hi99']:.2f}; teachers-removed {a['abl_acc']:.3f})"
    else:
        fr = full.get((c, "refresh")); ft = full.get((c, "thin"))
        if R and R["lo99"] > 0.70:
            k = "R-CANDIDATE"; reading = f"refresh OVR {R['acc']:.3f} [{R['lo99']:.3f},{R['hi99']:.3f}] M32"
            a = abl.get((c, "refresh")); ff = f"PASS (conservative diff >= {R['lo99'] - a['abl_hi99']:.2f}; teachers-removed {a['abl_acc']:.3f}, M32)" if a else "-"
        elif fr and fr["lo99"] > 0.55:
            k = "R-CANDIDATE"; reading = f"refresh OVR {fr['acc']:.3f} [{fr['lo99']:.3f},{fr['hi99']:.3f}] M64"
            ff = ("PASS" if fr["FLIP_FEEDBACK"] else "FAIL") + f" (paired diff lo99 {fr['ff_diff_lo99']:.3f})"
        elif ft and ft["lo99"] > 0.55:
            k = "R-CANDIDATE"; reading = f"thin OVR {ft['acc']:.3f} [{ft['lo99']:.3f},{ft['hi99']:.3f}] M64"
            ff = ("PASS" if ft["FLIP_FEEDBACK"] else "FAIL") + f" (paired diff lo99 {ft['ff_diff_lo99']:.3f})"
        else:
            k = "UNDECIDED"; best = max([("base", b["acc"]), ("refresh", R["acc"] if R else 0), ("thin", T["acc"] if T else 0)], key=lambda x: x[1])
            if ft: best = ("thin@64", ft["acc"])
            reading = f"best {best[0]} {best[1]:.3f}"
            for t in tags: diag[t] += 1
    cls[k] += 1
    sp = "exact" if b["exact_space"] else f"OVR L{p['prog_len']}->16" + (f" D{p['state_dim']}->2" if p["state_dim"] < 2 else "")
    lines.append(f"| {c} | {b['wave']} | {p['topology']} {p['update_mode']} | d{e['d']} dl{e['delta']} b{e['block']} | {b['lc_bound']:.2f} | {b['held_rec']:.3f} | {b['relay_rec']:.3f} | {sp} {b['acc']:.3f} [{b['lo99']:.3f},{b['hi99']:.3f}] | {R['acc'] if R else float('nan'):.3f} | {T['acc'] if T else float('nan'):.3f} | {' '.join(tags) or '-'} | **{k}** {reading} | {ff} |")
hdr = "| cell | wave | topo/update | env | lc bound | C1 held | C1 relay_pv32 | P-FLIP base (M64) | refresh M32 (OVR L22) | thin M16 (OVR L28) | physics tags | class (reading) | FLIP_FEEDBACK |\n|" + "---|" * 13
print(hdr); print("\n".join(lines)); print(); print(dict(cls)); print("UNDECIDED tag counts", dict(diag))
und = [l for l in lines if "UNDECIDED" in l]
print("n undecided", len(und))
