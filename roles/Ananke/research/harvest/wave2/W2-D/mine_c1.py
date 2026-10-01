"""Existing-data discriminators over C1 evolve/transfer rows (no engine). Writes out/mine_c1.json."""
import gzip, json, pathlib, collections
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[5]
R = [json.loads(l) for l in gzip.open(ROOT / "roles/Ananke/pte/c1_rows/cells.jsonl.gz", "rt")]
LC = json.load(open(ROOT / "roles/Ananke/research/harvest/H-PLANT/out/lc_census.json"))
lc = {}
for x in LC["rows"]:
    lc.setdefault(x["cell"], x["bound"])
ev = [r for r in R if r["kind"] == "evolve"]
FAMS = ("RELAY", "XOR", "MAJ", "FLIP", "HOLD")
# chance ceiling of the GA's selector: gen-0 max_acc (random genomes, M=8) per family
g0 = {f: np.array([r["result"]["curve"][0]["max_acc"] for r in ev if r["env"]["family"] == f]) for f in FAMS}
ceil = {f: float(np.quantile(g0[f], .95)) for f in FAMS}
def feats(r):
    c = r["result"]["curve"]; h = r["result"]["held"]
    mx = np.array([x["max_acc"] for x in c]); ba = np.array([x["best_acc"] for x in c])
    ma = np.array([x["mean_acc"] for x in c]); sa = np.array([x["mean_sens_any"] for x in c])
    mc = np.array([x["max_contrast"] for x in c])
    return dict(cell=r["cell_id"], wave=r["wave"], fam=r["env"]["family"], d=r["env"]["d"],
                held=h["acc"], lo=h["lo99"], hi=h["hi99"], sig=r["labels"]["SIGNAL"],
                train_final=r["result"]["champ_train_final"], pop_final_mean=r["result"]["pop_final_mean"],
                mx_first=float(mx[:6].mean()), mx_last=float(mx[-6:].mean()), mx_peak=float(mx.max()),
                peak_gen=int(mx.argmax()), ba_last=float(ba[-6:].mean()), ma_last=float(ma[-6:].mean()),
                ma_first=float(ma[:6].mean()),
                override_frac=float(np.mean(ba < mx - 1e-9)), sens_any_last=float(sa[-6:].mean()),
                contrast_last=float(mc[-6:].mean()), plant=r["result"]["plant"]["acc"],
                plant_name=r["result"]["plant"]["plant"], lc=lc.get(r["cell_id"]),
                twin_beyond=r["result"].get("twin", {}).get("beyond_hop"))
F = [feats(r) for r in ev]
def place(x):
    """Conservative link placement for a NULL evolve row from recorded data only. Returns a list of tags."""
    t = []
    if x["sig"]:
        return ["SIGNAL"]
    if x["lc"] is not None and x["lc"] < .60:
        t.append("P:lightcone<.60")
    if x["plant_name"] in ("relay_flood", "hold_latch") and x["fam"] in ("RELAY", "HOLD") and x["plant"] >= .75:
        t.append("notRP:family_plant>=.75")
    if x["lo"] > .5:
        t.append("V?:held_lo99>.5_but_not_SIGNAL")          # real, sub-threshold competence
    if x["sens_any_last"] < 1e-3:
        t.append("inert:population_state_insensitive")
    if x["ma_last"] - x["ma_first"] < .01 and x["mx_last"] <= ceil[x["fam"]]:
        t.append("flat:no_selectable_gradient")             # selector never saw anything above chance ceiling
    if x["mx_peak"] >= .75 and x["mx_last"] < x["mx_peak"] - .10:
        t.append("U?:peak_then_drop")
    if x["train_final"] - x["held"] > .06 and x["lo"] <= .5:
        t.append("winners_curse:train_final>>held")
    return t or ["unplaced"]
summary = {}
for f in FAMS:
    xs = [x for x in F if x["fam"] == f]
    nul = [x for x in xs if not x["sig"]]
    tags = collections.Counter(t.split(":")[0] for x in nul for t in place(x))
    s = {"evolve": len(xs), "null": len(nul), "gen0_maxacc_q95_ceiling": round(ceil[f], 3),
         "tags_on_nulls": dict(tags),
         "null_median_train_final_minus_held": round(float(np.median([x["train_final"] - x["held"] for x in nul])), 3) if nul else None,
         "null_median_mx_last": round(float(np.median([x["mx_last"] for x in nul])), 3) if nul else None,
         "null_median_ma_last_minus_first": round(float(np.median([x["ma_last"] - x["ma_first"] for x in nul])), 4) if nul else None,
         "null_frac_override": round(float(np.mean([x["override_frac"] for x in nul])), 3) if nul else None,
         "sig_median_mx_last": round(float(np.median([x["mx_last"] for x in xs if x["sig"]])), 3) if len(nul) < len(xs) else None,
         "null_held_lo_gt_.5": sum(1 for x in nul if x["lo"] > .5),
         "null_held_mean_gt_.55": sum(1 for x in nul if x["held"] > .55),
         "null_U_peak_drop": sum(1 for x in nul if "U?:peak_then_drop" in place(x)),
         }
    summary[f] = s
    print(f, json.dumps(s))
# SIGNAL attainability: held CI half-width at M_held=64 (32 pairs): what mean is needed for lo99>.55?
hw = collections.defaultdict(list)
for x in F:
    hw[x["fam"]].append(x["held"] - x["lo"])
att = {f: {"median_lower_halfwidth": round(float(np.median(v)), 3),
           "approx_mean_needed_for_SIGNAL": round(.55 + float(np.median([h for h, xx in zip(v, [y for y in F if y['fam']==f]) if xx['held'] > .55] or v)), 3)}
       for f, v in hw.items()}
print("attainability", att)
# transfers: champions evaluated off-family / off-scale
tr = [r for r in R if r["kind"] == "transfer"]
trs = collections.Counter((r["extra"].get("source_family"), r["env"]["family"], "variant" in r["extra"], r["labels"]["SIGNAL"]) for r in tr)
# evolve at FLIP d9cc etc: list all FLIP evolve rows with features
flip = sorted([x for x in F if x["fam"] == "FLIP"], key=lambda x: -x["held"])
json.dump({"summary": summary, "ceil": ceil, "attain": att, "rows": F, "place": {x["cell"]: place(x) for x in F},
           "transfer_counts": [list(k) + [v] for k, v in trs.items()]},
          open(HERE / "out/mine_c1.json", "w"), indent=1)
print("FLIP top held:", [(x["cell"][:8], round(x["held"], 3), round(x["lo"], 3), round(x["mx_last"], 3), x["lc"]) for x in flip[:8]])
