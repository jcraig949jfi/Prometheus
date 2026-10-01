"""W2-45 a1: out-of-sample scoring of W2-2 EW-1/1b/2 (+EW-4 necessity) on W2-29 FULL, W2-22 and W2-37 BANK arms,
plus pre-registered EW-N on FULL E27. Read-only on other folders. python -B a1_score.py -> a1_score.json. See PREREG.md."""
import json, math, pathlib
HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parent
T = 163


def load(p):
    return [json.loads(l) for l in open(p)]


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(p, 4), round(max(0, c - h), 4), round(min(1, c + h), 4)]


# ---------- per-run alarm from a full trajectory ----------
def from_traj(tr):
    def B(e):  # cumulative causal births at end of epoch e (1-based); e<=0 -> 0; beyond end -> last
        if e <= 0:
            return 0
        return tr[min(e, len(tr)) - 1][2]
    n = len(tr)
    a = {}
    a["EW1"] = int(B(15) - B(10) >= 3)
    a["EW1b"] = int(max(B(e) - B(e - 1) for e in range(11, 21)) >= 2)
    a["EW2"] = int(B(5) >= 4)
    a["EW4"] = int(B(10) >= 1)
    a["_short"] = n < 20 and tr[-1][1] > 0   # run stopped before epoch 20 while alive (cap/runaway stop)
    return a


# ---------- bounds from genome first-appearance rows ----------
def from_genomes(rows, Bfinal):
    pts = sorted((f + 1, b) for _, f, b, _ in rows)  # (1-based epoch of birth, B after that birth)

    def lo(e):
        return max([b for ee, b in pts if ee <= e], default=0)

    def hi(e):
        if e <= 0:
            return 0
        return min([b - 1 for ee, b in pts if ee > e], default=Bfinal)

    def tri(lo_ok, hi_ok):
        return 1 if lo_ok else (0 if not hi_ok else None)
    a = {}
    a["EW1"] = tri(lo(15) - hi(10) >= 3, hi(15) - lo(10) >= 3)
    a["EW1b"] = tri(max(lo(e) - hi(e - 1) for e in range(11, 21)) >= 2, max(hi(e) - lo(e - 1) for e in range(11, 21)) >= 2)
    a["EW2"] = tri(lo(5) >= 4, hi(5) >= 4)
    a["EW4"] = tri(lo(10) >= 1, hi(10) >= 1)
    a["_bounds"] = dict(B5=[lo(5), hi(5)], B10=[lo(10), hi(10)], B15=[lo(15), hi(15)], B20=[lo(20), hi(20)])
    return a


# ---------- certain / frozen-inferred negatives when nothing else is known ----------
def from_summary(r, tier2=True):
    B, ep, stop = r["B"], r["epochs"], r["stop"]
    early_end = stop == "extinct" and ep <= 10
    frozen_early = tier2 and stop == "frozen" and (ep - 101) <= 9
    a = {}
    a["EW1"] = 0 if (B < 3 or early_end or frozen_early) else None
    a["EW1b"] = 0 if (B < 2 or early_end or frozen_early) else None
    a["EW2"] = 0 if B < 4 else None
    a["EW4"] = 0 if B == 0 else None
    return a


def score(units, obs, target):
    """units: list of (alarm dict, outcome dict). Returns counts under both imputations of ?."""
    out = {}
    for imp in (0, 1):
        tp = fn = fp = tn = 0
        for a, o in units:
            x = a[obs]; x = imp if x is None else x
            y = o[target]
            if y is None:
                continue
            if y and x: tp += 1
            elif y: fn += 1
            elif x: fp += 1
            else: tn += 1
        out["imp%d" % imp] = dict(tp=tp, fn=fn, fp=fp, tn=tn, hit=wilson(tp, tp + fn), fa=wilson(fp, fp + tn),
                                  ppv=wilson(tp, tp + fp))
    out["n_unknown"] = sum(1 for a, o in units if a[obs] is None)
    out["n_unknown_runaway"] = sum(1 for a, o in units if a[obs] is None and o[target])

    def verdict(c):
        if c["hit"] is None or c["fa"] is None:
            return None
        return c["hit"][0] >= 0.75 and c["fa"][0] <= 0.03
    v0, v1 = verdict(out["imp0"]), verdict(out["imp1"])
    out["verdict"] = "PASS" if (v0 and v1) else ("FAIL" if (v0 is False and v1 is False) else "UNRESOLVED")
    return out


def outcomes(r, free=False):
    o = {"xk": r["Bxk"] >= T, "B": r["B"] >= T}
    if free and r["stop"] == "free_cap256":
        o["xk_Cm"], o["xk_Cp"] = o["xk"], True
        o["B_Cm"], o["B_Cp"] = o["B"], True
    else:
        o["xk_Cm"] = o["xk_Cp"] = o["xk"]
        o["B_Cm"] = o["B_Cp"] = o["B"]
    return o


res = {}
OBS = ["EW1", "EW1b", "EW2", "EW4"]

# ===================== FULL =====================
full = load(W / "W2-29_residue" / "runs_FULL.jsonl")
gen = {d["s"]: d for d in load(W / "W2-29_residue" / "genomes_FULL.jsonl")}
units, units_t1, per = [], [], []
for r in full:
    o = outcomes(r)
    if r["s"] in gen:
        a = from_genomes(gen[r["s"]]["genomes"], r["B"]); a1 = a
    else:
        a = from_summary(r, tier2=True); a1 = from_summary(r, tier2=False)
    units.append((a, o)); units_t1.append((a1, o))
    if r["s"] in gen or r["B"] >= 3:
        per.append(dict(s=r["s"], B=r["B"], Bxk=r["Bxk"], stop=r["stop"], epochs=r["epochs"],
                        **{k: a[k] for k in OBS}, bounds=a.get("_bounds")))
res["FULL"] = {"n": len(full), "runaways_xk": sum(r["Bxk"] >= T for r in full), "runaways_B": sum(r["B"] >= T for r in full),
               "E27": len(gen)}
for tgt in ("xk", "B"):
    for ob in OBS:
        res["FULL"]["%s|%s" % (ob, tgt)] = score(units, ob, tgt)
        res["FULL"]["%s|%s|tier1only" % (ob, tgt)] = score(units_t1, ob, tgt)
res["FULL"]["unknown_breakdown"] = {ob: {"B<27": sum(1 for (a, o), r in zip(units, full) if a[ob] is None and r["s"] not in gen),
                                         "E27": sum(1 for (a, o), r in zip(units, full) if a[ob] is None and r["s"] in gen)}
                                    for ob in OBS}
res["FULL"]["E27_rows"] = [p for p in per if p["s"] in gen]
# B<27 indeterminate profile
ind = [r for (a, o), r in zip(units, full) if r["s"] not in gen and a["EW1b"] is None]
res["FULL"]["EW1b_unknown_B_hist"] = sorted(r["B"] for r in ind)
res["FULL"]["EW1b_unknown_stop"] = {s: sum(r["stop"] == s for r in ind) for s in ("frozen", "extinct", "horizon")}

# frozen-assumption check on FULL E27 genome rows: no causal genome first born after epochs-101 for frozen runs
chk = []
for r in full:
    if r["s"] in gen and r["stop"] == "frozen":
        lastf = max(f for _, f, _, _ in gen[r["s"]]["genomes"])
        chk.append((r["s"], r["epochs"], lastf, lastf <= r["epochs"] - 101))
res["FULL"]["frozen_check_E27"] = chk

# EW-N within E27 (pre-registered)
cls = json.load(open(W / "W2-29_residue" / "c1_classes.json"))


def is_c3(h):
    return bytes.fromhex(h)[43] == 0xC3


def ewn(rows, last_ep, use_side0=True, use_c3=True, ring=False):
    for h, f, b, c in rows:
        if f > last_ep - 1:
            continue
        k = cls.get(h)
        s0 = bool(k and k["side0"] and (not ring or (k["de"] is not None and (k["de"] & 127) == 64)))
        if (use_side0 and s0) or (use_c3 and is_c3(h)):
            return 1
    return 0


E = []
for r in full:
    if r["s"] in gen:
        rows = gen[r["s"]]["genomes"]
        a1b = [a for (a, o), rr in zip(units, full) if rr["s"] == r["s"]][0]["EW1b"]
        firsts = {}
        for h, f, b, c in rows:
            k = cls.get(h)
            if k and k["side0"]:
                firsts["side0"] = min(firsts.get("side0", 999), f + 1)
            if is_c3(h):
                firsts["c3"] = min(firsts.get("c3", 999), f + 1)
        E.append(dict(s=r["s"], B=r["B"], Bxk=r["Bxk"], xk=r["Bxk"] >= T, Bt=r["B"] >= T,
                      EWN=ewn(rows, 20), EWN15=ewn(rows, 15), EWN30=ewn(rows, 30), side0_20=ewn(rows, 20, True, False),
                      c3_20=ewn(rows, 20, False, True), ring_20=ewn(rows, 20, True, True, True), EW1b=a1b,
                      first_side0_epoch=firsts.get("side0"), first_c3_epoch=firsts.get("c3"),
                      n_genomes_by20=sum(1 for _, f, _, _ in rows if f <= 19)))
res["EWN_rows"] = E


def sc_simple(rows, key, tgt):
    tp = sum(1 for e in rows if e[key] and e[tgt]); fn = sum(1 for e in rows if not e[key] and e[tgt])
    fp = sum(1 for e in rows if e[key] and not e[tgt]); tn = sum(1 for e in rows if not e[key] and not e[tgt])
    hit, fa = wilson(tp, tp + fn), wilson(fp, fp + tn)
    return dict(tp=tp, fn=fn, fp=fp, tn=tn, hit=hit, fa=fa, ppv=wilson(tp, tp + fp),
                verdict=("PASS" if hit and fa and hit[0] >= .75 and fa[0] <= .03 else "FAIL"))


Ek = [dict(e, both=int(e["EWN"] and e["EW1b"] == 1)) for e in E]
res["EWN"] = {}
for tgt in ("xk", "Bt"):
    for key in ("EWN", "EWN15", "EWN30", "side0_20", "c3_20", "ring_20", "both"):
        res["EWN"]["%s|%s" % (key, tgt)] = sc_simple(Ek, key, tgt)
    Ekn = [e for e in Ek if e["EW1b"] is not None]
    res["EWN"]["EW1b|%s|E27_known" % tgt] = sc_simple(Ekn, "EW1b", tgt)

# ===================== BANK model arms =====================
arms = {
    "W2-22 FIELD BANK": (W / "W2-22_second_regime" / "runs_FIELD.jsonl", False),
    "W2-22 FREE BANK": (W / "W2-22_second_regime" / "runs_FREE.jsonl", True),
    "W2-37 FIELD BANK": (W / "W2-37_fstar_k1" / "runs_FIELD.jsonl", False),
    "W2-37 FREE BANK": (W / "W2-37_fstar_k1" / "runs_FREE.jsonl", True),
}
frozen_traj_check = {}
for name, (p, free) in arms.items():
    rs = load(p)
    U = []
    bad = 0; tot = 0; short = []
    for r in rs:
        o = outcomes(r, free)
        if "traj" in r:
            a = from_traj(r["traj"])
            if a["_short"]:
                short.append((r["s"], r["epochs"], r["stop"], r["B"], r["Bxk"]))
                if len(r["traj"]) < 20:  # window not fully observed -> unknown unless already decided
                    for ob in ("EW1", "EW1b"):
                        if a[ob] == 0:
                            a[ob] = None
            if r["stop"] == "frozen":  # tier-2 assumption check: no causal birth after epoch epochs-100 (1-based)
                tot += 1
                lb = r["epochs"] - 100
                if r["traj"][-1][2] != r["traj"][max(lb, 1) - 1][2]:
                    bad += 1
        else:
            a = from_summary(r, tier2=True)
        U.append((a, o))
    frozen_traj_check[name] = dict(frozen_with_traj=tot, causal_birth_after_last_anc0_birth=bad)
    d = {"n": len(rs), "with_traj": sum("traj" in r for r in rs),
         "runaways_xk": sum(o["xk"] for a, o in U), "runaways_B": sum(o["B"] for a, o in U),
         "cap256": sum(r["stop"] == "free_cap256" for r in rs), "short_alive_traj": short[:40], "n_short": len(short)}
    for tgt in (("xk_Cm", "xk_Cp", "B_Cm", "B_Cp") if free else ("xk", "B")):
        for ob in OBS:
            d["%s|%s" % (ob, tgt)] = score(U, ob, tgt)
    d["unknown"] = {ob: sum(1 for a, o in U if a[ob] is None) for ob in OBS}
    res[name] = d
res["frozen_traj_check"] = frozen_traj_check
json.dump(res, open(HERE / "a1_score.json", "w"), indent=1, default=str)


def line(tag, s):
    c0, c1 = s["imp0"], s["imp1"]
    return "%-34s hit %s/%s..%s/%s FA %s..%s  unk %d (run %d)  %s" % (
        tag, c0["tp"], c0["tp"] + c0["fn"], c1["tp"], c1["tp"] + c1["fn"], c0["fa"], c1["fa"], s["n_unknown"],
        s["n_unknown_runaway"], s["verdict"])


for name in ["FULL"] + list(arms):
    d = res[name]
    print("=====", name, {k: d[k] for k in d if k in ("n", "with_traj", "runaways_xk", "runaways_B", "E27", "cap256", "n_short", "unknown")})
    for k, v in d.items():
        if isinstance(v, dict) and "imp0" in v and "tier1" not in k:
            print(line(k, v))
print("frozen check", frozen_traj_check, res["FULL"]["frozen_check_E27"])
print("FULL unknown breakdown", res["FULL"]["unknown_breakdown"], res["FULL"]["EW1b_unknown_stop"])
for k, v in res["EWN"].items():
    print("EWN", k, v)
for e in E:
    print(e)
for p in res["FULL"]["E27_rows"]:
    print(p)
