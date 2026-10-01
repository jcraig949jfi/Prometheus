"""W-O analysis (PLAN.md D1-D3): transition matrices with CIs, SINGLE vs EVERY,
and re-derived record readings (proposed corrections; records are not edited)."""
import collections, csv, glob, json, math, pathlib
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
RES = HERE.parents[1]
V = ("FLIP", "NO-EFFECT", "CHANCE")
VR = ("FLIP_REL", "NO_EFFECT_REL", "CHANCE_REL", "INDETERMINATE", "NOT_ELIGIBLE", "NO_PMIN")
PMIN = {k: v["p_min"] for k, v in json.load(open(RES / "workers/W-N/out/attain_table.json")).items()
        if isinstance(v, dict) and "p_min" in v}


def wilson(k, n, z=2.576):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 3), round(c + h, 3))


def cluster_ci(items, target, n_boot=2000, seed=0, alpha=0.01):
    """items: list of (specimen, verdict). Bootstrap over specimens."""
    by = collections.defaultdict(list)
    for s, v in items:
        by[s].append(v)
    sp = list(by)
    if not sp:
        return (None, None)
    rng = np.random.default_rng(seed)
    k = np.array([sum(v == target for v in by[s]) for s in sp])
    n = np.array([len(by[s]) for s in sp])
    bs = []
    for _ in range(n_boot):
        i = rng.integers(len(sp), size=len(sp))
        bs.append(k[i].sum() / n[i].sum())
    return (round(float(np.quantile(bs, alpha / 2)), 3), round(float(np.quantile(bs, 1 - alpha / 2)), 3))


def load():
    inv = list(csv.DictReader(open(OUT / "inventory.csv")))
    runs = {}
    errs = []
    for f in sorted(glob.glob(str(OUT / "rerun_s*.jsonl"))):
        for l in open(f):
            if l.strip():
                r = json.loads(l)
                if "error" in r:
                    errs.append(r)
                    continue
                runs[tuple(r["group"])] = r
    for f in sorted(glob.glob(str(OUT / "rerun_every_s*.jsonl"))):
        for l in open(f):
            if l.strip():
                r = json.loads(l)
                k = tuple(r["group"])
                if "error" in r or k not in runs:
                    continue
                runs[k]["every"] = r["every"]
    rows = []
    for x in inv:
        k = (x["source"], x["loader"], x["specimen"], x["offset"], x["trial_set"], x["family"])
        r = runs.get(k)
        y = dict(x)
        if r is None:
            y["single"] = "NOT_RUN"
            rows.append(y)
            continue
        a = r["arms"][x["arm"]]
        y.update(single=a["abs"], rel=a["rel_ungated"], z=a["z"], n512=a["normal"], s512=a["swap"], P=a["P"],
                 cells=a["cells"], census=r["census"]["class"], fS=r["census"]["fS"], fC=r["census"]["fC"],
                 fN=r["census"]["fN"], ident=r["census"]["identity"], follow=r["census_follow"]["class"])
        K = int(round(a["cells"] / max(1, 2 * a["P"])))
        pm = PMIN.get(f"P{a['P']}_K{K}")
        y["K"], y["p_min"] = K, pm
        y["rel_gated"] = ("NOT_ELIGIBLE" if a["normal"][1] < pm else a["rel_ungated"]) if pm else "NO_PMIN"
        ev = r.get("every", {}).get(x["arm"])
        y["every"] = ev["abs"] if ev else None
        y["every_swap"] = ev["swap"] if ev else None
        rows.append(y)
    return inv, rows, runs, errs


def matrix(rows, key="single", label="", cats=V):
    it = [r for r in rows if r.get(key) not in (None, "NOT_RUN")]
    n = len(it)
    res = {"n": n, "label": label}
    for v in cats:
        k = sum(r[key] == v for r in it)
        res[v] = {"k": k, "p": round(k / n, 3) if n else None, "wilson99": wilson(k, n),
                  "cluster99": cluster_ci([(r["specimen"], r[key]) for r in it], v)}
    return res


# ------------------------------------------------------------------ re-derivation
def wf_cls(nlo, v):
    if nlo < 0.60:
        return "UNREADABLE"
    s, c = v["site_all"] == "FLIP", v["channel_all"] == "FLIP"
    if s and c:
        return "DUAL"
    if s:
        return "SITE"
    if c:
        return "CHANNEL"
    if v.get("joint") == "FLIP":
        return "JOINT"
    return "ELSEWHERE"


def rederive_wf(rows, runs):
    """Re-derive W-F class / class_late for every W-F cell with >= 1 audited verdict.
    Two versions: (a) recorded normal lo99 (verdict-only change), (b) re-run normal lo99."""
    rec = {}
    for f in sorted(glob.glob(str(RES / "workers/W-F/out/census_s*.jsonl"))):
        for ln, l in enumerate(open(f), 1):
            r = json.loads(l)
            rec[r["cell_id"]] = (pathlib.Path(f).name, ln, r)
    ct = {}
    for i, r in enumerate(csv.DictReader(open(RES / "workers/W-F/out/census_table.csv")), 2):
        ct[r["cell"]] = i
    new = collections.defaultdict(dict)
    n512 = {}
    for r in rows:
        if r["source"] != "WF" or r["single"] == "NOT_RUN":
            continue
        new[r["specimen"]][(r["timing"], r["arm"])] = r["single"]
        if r["timing"] == "mid":
            n512[r["specimen"]] = r["n512"][1]
    out = []
    for cid, ch in new.items():
        fn, ln, r = rec[cid]
        mid = {a: r["mid"][a]["verdict"] for a in r["mid"] if a != "normal"}
        late = {a: r["late"][a]["verdict"] for a in r["late"] if a != "normal"}
        if r.get("joint"):
            mid["joint"] = r["joint"]["verdict"]
        for (t, a), v in ch.items():
            if t == "mid":
                mid[a] = v
            elif t == "late":
                late[a] = v
        nlo_rec = r["mid"]["normal"][1]
        nlo_new = n512.get(cid)
        for tag, nlo in (("rec_normal", nlo_rec), ("rerun_normal", nlo_new if nlo_new is not None else nlo_rec)):
            c = wf_cls(nlo, mid)
            cl = wf_cls(nlo, late) if c != "UNREADABLE" else "UNREADABLE"
            joint_missing = c == "ELSEWHERE" and "joint" not in mid
            out.append({"cell": cid[:8], "record": f"W-F/out/{fn}:{ln}", "table": f"W-F/out/census_table.csv:{ct.get(cid[:8])}",
                        "basis": tag, "class_rec": r["class"], "class_new": c, "class_late_rec": r["class_late"],
                        "class_late_new": cl, "changed": (c, cl) != (r["class"], r["class_late"]),
                        "nlo_rec": round(nlo_rec, 3), "nlo_512": None if nlo_new is None else round(nlo_new, 3),
                        "note": "joint arm never recorded" if joint_missing else ""})
    return out


def wi_reader(d, phi):
    vs, vc, vj = d["site_all"], d["channel_all"], d["joint"]
    if vs == "FLIP" and vc == "FLIP":
        return "D"
    if vs == "FLIP":
        return "S"
    if vc == "FLIP":
        return "C"
    if vj == "FLIP":
        return "M?" if phi is not None and phi <= -0.3 else "J"
    if vs == vc == vj == "NO-EFFECT":
        return "E"
    return "X"


def rederive_wi(rows):
    out = []
    by = collections.defaultdict(dict)
    for r in rows:
        if r["source"] == "WI" and r["single"] != "NOT_RUN":
            by[(r["specimen"], int(r["offset"]))][r["arm"]] = r["single"]
    trajs = {}
    for (sp, o), ch in sorted(by.items()):
        if sp not in trajs:
            trajs[sp] = json.loads((RES / f"workers/W-I/out/traj_{sp[:8]}.json").read_text())
        t = trajs[sp]
        d = t["offsets"][str(o)]
        rv = {a: d[a]["verdict"] for a in t["arms"]}
        nv = dict(rv)
        nv.update(ch)
        readable = t["normal"][1] >= 0.60
        # recorded label via the record's own rule (M needs accs; reuse record's reader string for comparison)
        r_old = wi_reader(rv, d["phi"]) if readable else "?"
        r_new = wi_reader(nv, d["phi"]) if readable else "?"
        # 'M' vs 'J': record rule also checks |a_s + a_c - 1| <= .15 on recorded accs
        if r_old == "M?" or r_new == "M?":
            a_s, a_c = d["site_all"]["acc"][0], d["channel_all"]["acc"][0]
            m = abs(a_s + a_c - 1) <= 0.15
            r_old = ("M" if m else "J") if r_old == "M?" else r_old
            r_new = ("M" if m else "J") if r_new == "M?" else r_new
        skip = ("site_all", "channel_all", "joint")
        sc_old = [a for a in t["arms"] if a not in skip and rv[a] == "CHANCE"]
        sc_new = [a for a in t["arms"] if a not in skip and nv[a] == "CHANCE"]
        sf_old = [a for a in t["arms"] if a not in skip and rv[a] == "FLIP"]
        sf_new = [a for a in t["arms"] if a not in skip and nv[a] == "FLIP"]
        out.append({"cell": sp[:8], "o": o, "table": f"W-I/out/table_{sp[:8]}.csv:{o + 3}",
                    "reader_rec": r_old, "reader_new": r_new, "sub_chance_rec": "+".join(sc_old),
                    "sub_chance_new": "+".join(sc_new), "sub_flip_rec": "+".join(sf_old), "sub_flip_new": "+".join(sf_new),
                    "reader_changed": r_old != r_new, "subs_changed": (sc_old, sf_old) != (sc_new, sf_new)})
    return out


def rederive_sct(rows):
    s = json.loads((RES / "spikes/out/s_ct.json").read_text())
    out = []
    by = collections.defaultdict(dict)
    for r in rows:
        if r["source"] == "SCT" and r["single"] != "NOT_RUN":
            by[r["specimen"]][r["arm"]] = r["single"]
    for sp, ch in by.items():
        v = {a: s[sp][a]["verdict"] for a in ("sitestate", "inflight")}
        n = dict(v)
        n.update({a: x for a, x in ch.items() if a in n})
        cls = lambda q: "site-state" if q["sitestate"] == "FLIP" else ("in-flight" if q["inflight"] == "FLIP" else "joint")
        out.append({"parent": sp, "changes": ch, "we_class_rec": cls(v), "we_class_new": cls(n),
                    "changed": cls(v) != cls(n),
                    "affected": "W-E ret_census.specimens() class for D-wave cells with parent " + sp})
    return out


if __name__ == "__main__":
    inv, rows, runs, errs = load()
    ran = [r for r in rows if r["single"] != "NOT_RUN"]
    S = {"inventory": len(inv), "groups_run": len(runs), "verdicts_run": len(ran), "errors": len(errs),
         "err_groups": [e["group"] for e in errs]}
    M = {"all": matrix(rows, "single", "SINGLE abs, all")}
    rd = lambda r: r["readable_lo99_ge_60"] == "True"
    M["readable"] = matrix([r for r in rows if rd(r)], "single", "SINGLE abs, recorded lo99 >= .60")
    M["unreadable"] = matrix([r for r in rows if not rd(r)], "single", "SINGLE abs, recorded lo99 < .60")
    for src in ("WF", "WI", "SCT"):
        M[f"src_{src}"] = matrix([r for r in rows if r["source"] == src], "single", src)
        M[f"src_{src}_readable"] = matrix([r for r in rows if r["source"] == src and rd(r)], "single", src + " readable")
    for fam in ("HOLD", "RELAY", "MAJ"):
        M[f"fam_{fam}"] = matrix([r for r in rows if r["family"] == fam], "single", fam)
    for a in sorted({r["arm"] for r in rows}):
        M[f"arm_{a}"] = matrix([r for r in rows if r["arm"] == a], "single", a)
    M["rel_ungated_all"] = matrix(rows, "rel", "W-N REL ungated, all", VR)
    M["rel_gated_all"] = matrix(rows, "rel_gated", "W-N REL gated (attain_table p_min), all", VR)
    M["rel_ungated_readable"] = matrix([r for r in rows if rd(r)], "rel", "REL ungated, readable", VR)
    M["rel_gated_readable"] = matrix([r for r in rows if rd(r)], "rel_gated", "REL gated, readable", VR)
    M["rel_gated_unreadable"] = matrix([r for r in rows if not rd(r)], "rel_gated", "REL gated, unreadable", VR)
    ev = [r for r in rows if r.get("every")]
    M["every_subset_EVERY"] = matrix(ev, "every", "EVERY abs, subset")
    M["every_subset_SINGLE"] = matrix(ev, "single", "SINGLE abs, same subset")
    agree = collections.Counter((r["single"], r["every"]) for r in ev)
    S["single_vs_every"] = {f"{a}|{b}": n for (a, b), n in sorted(agree.items())}
    S["single_every_agree"] = (sum(n for (a, b), n in agree.items() if a == b), len(ev))
    rel = collections.Counter((r["single"], r.get("rel")) for r in ran)
    S["single_vs_rel_ungated"] = {f"{a}|{b}": n for (a, b), n in sorted(rel.items())}
    # readability shift at M=512
    S["readability"] = collections.Counter(
        f"rec{'R' if rd(r) else 'U'}->512{'R' if r['n512'][1] >= 0.60 else 'U'}" for r in ran)
    # D1
    rr = [r for r in ran if rd(r)]
    k = sum(r["single"] == "FLIP" for r in rr)
    lo, hi = cluster_ci([(r["specimen"], r["single"]) for r in rr], "FLIP")
    S["D1"] = {"readable_n": len(rr), "flip_k": k, "cluster99": (lo, hi),
               "call": "WIDESPREAD" if lo is not None and lo > 0.20 else ("ISOLATED" if hi is not None and hi < 0.10 else "PARTIAL")}
    # census classes on groups
    S["census_class_groups"] = collections.Counter(r["census"]["class"] for r in runs.values())
    S["census_follow_groups"] = collections.Counter(r["census_follow"]["class"] for r in runs.values())
    wf = rederive_wf(rows, runs)
    wi = rederive_wi(rows)
    sct = rederive_sct(rows)
    S["WF_class_changes"] = {b: sum(x["changed"] for x in wf if x["basis"] == b) for b in ("rec_normal", "rerun_normal")}
    S["WF_cells"] = len({x["cell"] for x in wf})
    S["WI_reader_changes"] = sum(x["reader_changed"] for x in wi)
    S["WI_sub_changes"] = sum(x["subs_changed"] for x in wi)
    S["WI_offsets"] = len(wi)
    S["SCT"] = sct
    json.dump({"summary": S, "matrices": M}, open(OUT / "summary.json", "w"), indent=1, default=str)
    with open(OUT / "rerun_table.csv", "w", newline="") as f:
        keys = ["vid", "source", "specimen", "family", "arm", "timing", "offset", "normal_m", "normal_lo", "swap_m",
                "swap_lo", "swap_hi", "single", "every", "rel", "rel_gated", "p_min", "K", "z", "n512", "s512", "every_swap", "census", "fS", "fC",
                "fN", "ident", "follow", "record", "record_line", "derived_line", "derived_reading"]
        w = csv.DictWriter(f, keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps([round(x, 3) for x in r[k]]) if isinstance(r.get(k), (list, tuple)) else r.get(k)) for k in keys})
    with open(OUT / "corrections_WF.csv", "w", newline="") as f:
        w = csv.DictWriter(f, list(wf[0]) if wf else ["cell"])
        w.writeheader()
        w.writerows(wf)
    with open(OUT / "corrections_WI.csv", "w", newline="") as f:
        w = csv.DictWriter(f, list(wi[0]) if wi else ["cell"])
        w.writeheader()
        w.writerows(wi)
    print(json.dumps(S, indent=1, default=str))
    for k2, m in M.items():
        print(k2, m["n"], {v: (m[v]["k"], m[v]["p"], m[v]["wilson99"], m[v]["cluster99"]) for v in m if v not in ("n", "label")})
