"""W-F T-CT-1 analysis: census table + frozen models/decision (PLAN.md)."""
import collections, csv, glob, json, pathlib

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out"
FAMS = ["HOLD", "RELAY", "MAJ"]
P8 = ["decay", "loss", "async", "lat_base", "capinv", "fanout", "pw", "wimm"]
P6 = ["decay", "loss", "async", "lat_base", "capinv", "wimm"]


def feats(ph):
    k = ph["decay_shift"]
    return {"decay": 0.0 if k == 0 else 2.0 ** -k, "loss": ph["loss"],
            "async": float(ph["update_mode"] == "async"), "lat_base": ph["lat_base"],
            "capinv": 0.0 if ph["cap"] == 0 else 1.0 / ph["cap"], "fanout": ph["fanout"],
            "pw": ph["payload_width"], "wimm": ph["wimm"]}


def load():
    rows = {}
    for f in sorted(glob.glob(str(OUT / "census_s*.jsonl"))):
        for line in open(f):
            if line.strip():
                r = json.loads(line)
                rows[r["cell_id"]] = r
    return list(rows.values())


def tags(r):
    t = []
    m = r["mid"]
    if r["class"] in ("SITE", "CHANNEL", "DUAL"):
        arm = {"SITE": ["site_all"], "CHANNEL": ["channel_all"],
               "DUAL": ["site_all", "channel_all"]}[r["class"]]
        if any(r["pre"][a]["verdict"] == "FLIP" for a in arm):
            t.append("HISTORY")
        other = {"SITE": "channel_all", "CHANNEL": "site_all"}.get(r["class"])
        if other and m[other]["verdict"] == "NO-EFFECT" and m[other]["arm_identical"]:
            t.append("TRIVIAL")
    if r["class"] == "JOINT":
        both = m["site_all"]["verdict"] == "CHANCE" and m["channel_all"]["verdict"] == "CHANCE"
        t.append("JOINT-SPLIT" if both else "JOINT-ASYM")
    if r["class"] != "UNREADABLE" and r["class_late"] != r["class"]:
        t.append("HANDOFF")
    if r["class"] == "CHANNEL":
        pf = [a for a in m if a.startswith("pay") and m[a]["verdict"] == "FLIP"]
        t.append("pay=" + ("+".join(pf) if pf else "none"))
        if m["channel_count"]["verdict"] == "FLIP":
            t.append("COUNT-FLIP")
    return t


def fam_baseline(ytr, ftr, fte):
    maj = collections.Counter(ytr).most_common(1)[0][0]
    per = {f: collections.Counter(ytr[ftr == f]).most_common(1)[0][0] for f in set(ftr)}
    return np.array([per.get(f, maj) for f in fte])


def cv(X8, X6, F1h, y, fam, reps=20):
    cnt = collections.Counter(y)
    strat = min(cnt.values()) >= 5
    res = collections.defaultdict(list)
    for s in range(reps):
        kf = (StratifiedKFold(5, shuffle=True, random_state=s) if strat
              else KFold(5, shuffle=True, random_state=s))
        acc = collections.defaultdict(list)
        for tr, te in kf.split(X8, y):
            t = DecisionTreeClassifier(max_depth=2, random_state=0).fit(X8[tr], y[tr])
            acc["tree_phys"].append(np.mean(t.predict(X8[te]) == y[te]))
            Xf = np.hstack([X8, F1h])
            t2 = DecisionTreeClassifier(max_depth=2, random_state=0).fit(Xf[tr], y[tr])
            acc["tree_phys_fam"].append(np.mean(t2.predict(Xf[te]) == y[te]))
            sc = StandardScaler().fit(X6[tr])
            lr = LogisticRegression(C=1.0, max_iter=5000).fit(sc.transform(X6[tr]), y[tr])
            acc["logit6"].append(np.mean(lr.predict(sc.transform(X6[te])) == y[te]))
            acc["family_only"].append(np.mean(fam_baseline(y[tr], fam[tr], fam[te]) == y[te]))
            maj = collections.Counter(y[tr]).most_common(1)[0][0]
            acc["majority"].append(np.mean(y[te] == maj))
        for k, v in acc.items():
            res[k].append(float(np.mean(v)))
    summ = {k: {"mean": float(np.mean(v)), "p2.5": float(np.percentile(v, 2.5)),
                "p97.5": float(np.percentile(v, 97.5))} for k, v in res.items()}
    gains = [a - b for a, b in zip(res["tree_phys"], res["family_only"])]
    return summ, gains, strat


def row_table(r):
    m = r["mid"]
    f = feats(r["physics"])
    pay = {a: m[a]["verdict"] for a in m if a.startswith("pay")}
    j = r["joint"]
    return {"cell": r["cell_id"][:8], "wave": r["wave"], "family": r["family"],
            "class": r["class"], "class_late": r["class_late"], "tags": ";".join(tags(r)),
            "normal": round(m["normal"][0], 3), "normal_lo99": round(m["normal"][1], 3),
            "held_acc": round(r["held"]["acc"], 3),
            "site_all": m["site_all"]["verdict"], "site_acc": round(m["site_all"]["acc"][0], 3),
            "site_ident": m["site_all"]["arm_identical"],
            "channel_all": m["channel_all"]["verdict"], "chan_acc": round(m["channel_all"]["acc"][0], 3),
            "chan_ident": m["channel_all"]["arm_identical"],
            "channel_content": m["channel_content"]["verdict"],
            "channel_count": m["channel_count"]["verdict"], "w": m["w"]["verdict"],
            "pay": " ".join(f"{k}:{v[:4]}" for k, v in pay.items()),
            "joint": j["verdict"] if j else "", "joint_acc": round(j["acc"][0], 3) if j else "",
            "late_site": r["late"]["site_all"]["verdict"], "late_chan": r["late"]["channel_all"]["verdict"],
            "pre_site": r["pre"]["site_all"]["verdict"], "pre_chan": r["pre"]["channel_all"]["verdict"],
            "dest_mode": r["physics"]["dest_mode"], "topology": r["physics"]["topology"],
            "decay_shift": r["physics"]["decay_shift"], "cap": r["physics"]["cap"],
            "update_mode": r["physics"]["update_mode"],
            **{k: f[k] for k in ("loss", "lat_base", "fanout", "pw", "wimm")},
            "delta": r["env"]["delta"], "gap": r["env"]["gap"]}


if __name__ == "__main__":
    rows = load()
    errs = [r for r in rows if "error" in r]
    rows = [r for r in rows if "error" not in r]
    table = sorted((row_table(r) for r in rows), key=lambda t: (t["family"], t["class"], t["cell"]))
    with open(OUT / "census_table.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(table[0]))
        w.writeheader()
        w.writerows(table)
    ct = collections.Counter((t["family"], t["class"]) for t in table)
    classes = sorted(set(t["class"] for t in table))
    print("n cells", len(table), "errors", len(errs), [e["error"][:120] for e in errs[:3]])
    print("      " + " ".join(f"{c[:10]:>11s}" for c in classes))
    for fm in FAMS:
        print(f"{fm:6s}" + " ".join(f"{ct[(fm, c)]:11d}" for c in classes))
    tagc = collections.Counter(x for t in table for x in t["tags"].split(";") if x)
    print("tags", dict(tagc))
    rd = [r for r in rows if r["class"] != "UNREADABLE"]
    y = np.array([r["class"] for r in rd])
    cnt = collections.Counter(y)
    y = np.array([c if cnt[c] >= 5 else "OTHER" for c in y])
    fam = np.array([r["family"] for r in rd])
    X8 = np.array([[feats(r["physics"])[k] for k in P8] for r in rd])
    X6 = np.array([[feats(r["physics"])[k] for k in P6] for r in rd])
    F1h = np.array([[float(f == g) for g in FAMS] for f in fam])
    out = {"n_rows": len(rows), "n_errors": len(errs), "n_readable": len(rd),
           "class_counts_raw": dict(cnt), "class_counts_model": dict(collections.Counter(y)),
           "family_x_class": {f"{a}|{b}": v for (a, b), v in ct.items()}, "tags": dict(tagc)}
    top = collections.Counter(y).most_common(1)[0][1] / len(y) if len(y) else 0
    out["top_class_share"] = top
    if len(rd) < 30:
        out["decision"] = "INCONCLUSIVE (< 30 readable)"
    else:
        cvr, gains, strat = cv(X8, X6, F1h, y, fam)
        out["cv"] = cvr
        out["stratified"] = strat
        g = float(np.mean(gains))
        out["gain_tree_minus_family"] = {"mean": g, "p2.5": float(np.percentile(gains, 2.5)),
                                         "p97.5": float(np.percentile(gains, 97.5))}
        out["decision"] = "physics selects the carrier" if g >= 0.10 else "family selects"
        if top >= 0.90:
            out["decision"] += " (carrier near-uniform; decision not informative)"
        full = DecisionTreeClassifier(max_depth=2, random_state=0).fit(X8, y)
        out["tree_full"] = export_text(full, feature_names=P8)
        fullf = DecisionTreeClassifier(max_depth=2, random_state=0).fit(np.hstack([X8, F1h]), y)
        out["tree_phys_fam_full"] = export_text(fullf, feature_names=P8 + ["is_" + f for f in FAMS])
        desc = {}
        for k in P8:
            lv = collections.defaultdict(collections.Counter)
            for r, c in zip(rd, y):
                lv[feats(r["physics"])[k]][c] += 1
            desc[k] = {str(a): dict(b) for a, b in sorted(lv.items())}
        out["class_by_dial"] = desc
        wf = collections.defaultdict(collections.Counter)
        for r, c in zip(rd, y):
            wf[(r["family"], r["physics"]["dest_mode"])][c] += 1
        out["class_by_family_destmode"] = {f"{a}|{b}": dict(v) for (a, b), v in wf.items()}
    (OUT / "model.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in out if k not in ("class_by_dial", "family_x_class")}, indent=1))
