"""W-R summary: tables + frozen checks from out/strat_*.json -> out/summary.txt, out/summary.json"""
import json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


ORDER = ["2dccdaa5", "c16d5231", "8c37f32e", "e06701a5", "78f3b0ec", "4781b0a1", "369f5a5b", "E1", "E2",
         "PLANT2", "PLANT1"]
ABST = ("78f3b0ec", "e06701a5")
L = []
P = lambda s="": L.append(s)


def fmt(c, key="f"):
    if not c or c.get("eligible", 0) == 0 or c.get("fS") is None:
        return f"{(c or {}).get('class', 'UNDEFINED')[:10]:10s} n{(c or {}).get('eligible', 0):4d}"
    ci = c.get("ci99", {})
    g = lambda k: f"{c[k]:.2f}[{ci[k][0]:.2f},{ci[k][1]:.2f}]" if ci.get(k) else f"{c[k]:.2f}"
    return f"{c['class'][:10]:10s} n{c['eligible']:4d} S{g('fS')} C{g('fC')} N{g('fN')} id{c['identity']:.2f}"


def diffs(d):
    if not d:
        return "-"
    return " ".join(f"d{x}{d[f'd{x}']:+.2f}[{d['ci99'][f'd{x}'][0]:+.2f},{d['ci99'][f'd{x}'][1]:+.2f}]"
                    for x in ("S", "C", "N") if f"d{x}" in d["ci99"])


def neg_control_rule(res):
    """PLAN s2: passes iff PHASE EFFECT at <= 1 offset and every class change is threshold jitter."""
    eff = [o for o, r in res.items() if r.get("phase_effect")]
    supported = [o for o, r in res.items() if r.get("phase_effect") and any(
        r[q]["class"] not in ("UNDEFINED", r["pooled"]["class"]) for q in ("q0", "q1"))]
    return {"effect_offsets": eff, "supported_class_changes": supported,
            "pass": len(eff) <= 1 and not supported}


summ = {}
for name in ORDER:
    f = HERE / f"out/strat_{name}.json"
    if not f.exists():
        P(f"== {name}: NOT RUN / missing")
        continue
    d = json.loads(f.read_text())
    res = d["offsets_res"]
    P(f"== {name} {d['update_mode']} period {d['update_period']} Pd {d['Pd']} strat {d['strat_kind']} "
      f"M {d['M']} ns {d['ns']} ro_off {d['ro_off']} normal acc by t0 phase {d['normal_acc_by_t0_phase']} "
      f"wall {d['wall_s']:.0f}s")
    cnt = {"RESOLVES": [], "PARTLY": [], "STAYS_MIXED": []}
    cntf = {"RESOLVES": [], "PARTLY": [], "STAYS_MIXED": []}
    changes, jitter, eff = [], [], []
    for o, r in res.items():
        tag = []
        if r.get("phase_effect"):
            eff.append(int(o)); tag.append("EFFECT")
        ch = [q for q in ("q0", "q1") if r[q]["class"] not in ("UNDEFINED", r["pooled"]["class"])]
        if ch:
            (changes if r.get("phase_effect") else jitter).append(int(o))
            tag.append("CHANGE" if r.get("phase_effect") else "jitter")
        if r.get("resolution"):
            cnt[r["resolution"]].append(int(o)); tag.append(r["resolution"])
        P(f" o{o:>2} pooled {fmt(r['pooled'])}")
        P(f"     q0     {fmt(r['q0'])}   trials {r['phase_trials'].get('0')}")
        P(f"     q1     {fmt(r['q1'])}   trials {r['phase_trials'].get('1')}")
        P(f"     diff q1-q0 {diffs(r.get('diff'))}  {' '.join(tag)}")
        if name in ABST:
            fo = [r[q].get("follow", {"class": "UNDEFINED", "eligible": 0}) for q in ("pooled", "q0", "q1")]
            P(f"     FOLLOW pooled {fmt(fo[0])}")
            P(f"     FOLLOW q0     {fmt(fo[1])}")
            P(f"     FOLLOW q1     {fmt(fo[2])}  {r.get('resolution_follow') or ''}")
            if r.get("resolution_follow"):
                cntf[r["resolution_follow"]].append(int(o))
    nc = neg_control_rule(res)
    s = {"effect_offsets": eff, "supported_changes": changes, "jitter_changes": jitter,
         "resolution": cnt, "resolution_follow": cntf if name in ABST else None, "negctrl_rule": nc,
         "classes": {o: [r["pooled"]["class"], r["q0"]["class"], r["q1"]["class"]] for o, r in res.items()},
         "classes_follow": {o: [r[q].get("follow", {}).get("class", "UNDEFINED") for q in ("pooled", "q0", "q1")]
                            for o, r in res.items()} if name in ABST else None}
    summ[name] = s
    P(f" SUMMARY {name}: phase-effect offsets {eff}; supported class changes {changes}; jitter {jitter}")
    P(f"   pooled-mixed resolution (frozen): " + ", ".join(f"{k} {v}" for k, v in cnt.items()))
    if name in ABST:
        P(f"   pooled-mixed resolution (follow): " + ", ".join(f"{k} {v}" for k, v in cntf.items()))
    P(f"   no-phase-effect rule (PLAN s2): {nc}")
    P()

# ---- plant known-answer check (PLAN s4)
A = {**{o: "CHANNEL" for o in range(0, 5)}, 5: "SITE", **{o: "CHANNEL" for o in range(6, 11)}, 11: "SITE", 12: "SITE"}
B = {0: "IDENTITY-BROKEN", **{o: "CHANNEL" for o in range(1, 6)}, 6: "SITE", **{o: "CHANNEL" for o in range(7, 12)},
     12: "SITE"}


def plant_check(name, use_perm=False):
    d = json.loads((HERE / f"out/strat_{name}.json").read_text())
    res = d["permuted_mustfail"] if use_perm else d["offsets_res"]
    disc = sorted(int(o) for o, r in res.items() if r["q0"]["class"] != r["q1"]["class"])
    i = disc == [0, 5, 6, 11]
    ii_bad = []
    for o, r in res.items():
        o = int(o)
        exp = {o % 2: A[o], (o + 1) % 2: B[o]}           # A: q = o mod 2; B: q = (o+1) mod 2
        for q in (0, 1):
            if r[f"q{q}"]["class"] != exp[q]:
                ii_bad.append((o, q, r[f"q{q}"]["class"], exp[q]))
    iii = all(res[str(o)]["pooled"]["class"] == "MIXTURE" and res[str(o)]["resolution"] == "RESOLVES"
              for o in (5, 6, 11))
    nacc = d["normal_acc_by_t0_phase"]
    nok = all(v is not None and v >= 0.95 for v in nacc.values())
    return {"spec": name, "permuted": use_perm, "discordant": disc, "i": i, "ii": not ii_bad,
            "ii_mismatch": ii_bad[:8], "iii": iii, "normal_ok": nok, "normal": nacc,
            "PASS": bool(i and not ii_bad and iii and nok)}


ka = []
for name, perm in (("PLANT2", False), ("PLANT1", False), ("PLANT2", True)):
    if (HERE / f"out/strat_{name}.json").exists():
        ka.append(plant_check(name, perm))
P("== KA-P plant known-answer (PASS required for PLANT2; must FAIL for PLANT1 and PLANT2-permuted)")
for k in ka:
    P(" " + json.dumps(k))
P("== KA-N: no-phase-effect rule must FAIL on positives (4781b0a1, PLANT2) and PASS on 369f5a5b")
for n in ("369f5a5b", "4781b0a1", "PLANT2", "PLANT1"):
    if n in summ:
        P(f" {n}: pass={summ[n]['negctrl_rule']['pass']} effect offsets {summ[n]['negctrl_rule']['effect_offsets']}")

tot = {"RESOLVES": 0, "PARTLY": 0, "STAYS_MIXED": 0}
totf = {"RESOLVES": 0, "PARTLY": 0, "STAYS_MIXED": 0}
for n in ORDER[:9]:
    if n in summ:
        for k in tot:
            tot[k] += len(summ[n]["resolution"][k])
            if summ[n]["resolution_follow"]:
                totf[k] += len(summ[n]["resolution_follow"][k])
P(f"== TOTAL pooled-mixed readings over the 9 specs (frozen census): {tot}")
P(f"== TOTAL pooled-mixed readings, abstainers' follow census: {totf}")
(HERE / "out/summary.txt").write_text("\n".join(L))
(HERE / "out/summary.json").write_text(json.dumps({"specs": summ, "ka_plant": ka, "total": tot, "total_follow": totf},
                                                   indent=1))
print("\n".join(L))
