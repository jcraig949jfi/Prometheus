"""W2-52 r2: self-test gate, per-genome x arm table, paired bootstrap CIs, PREREG decision rule, mechanism tallies.
python -B r2_analyse.py -> r2_analyse.json"""
import json, pickle, random, pathlib, collections, statistics as st, sys
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W = HERE.parent
d = pickle.load(open(HERE / "r1_calls.pkl", "rb"))
calls, sides = d["calls"], d["sides"]
N = len(sides)
GEN = ["F", "AC", "5C", "C3", "C3+AC"]
ARMS = ["STOCK", "REVERSED"]
RUL = ["FID", "class", "exact"]


def m_vec(g, arm, rn):
    return [int(c["keep_" + rn]) + int(c["conv_" + rn]) for c in calls[(g, arm)]]


def summ(g, arm, rn):
    cs = calls[(g, arm)]
    n0 = sum(1 for s in sides if s == 0); n1 = N - n0
    k0 = sum(c["keep_" + rn] for c, s in zip(cs, sides) if s == 0); k1 = sum(c["keep_" + rn] for c, s in zip(cs, sides) if s == 1)
    c0 = sum(c["conv_" + rn] for c, s in zip(cs, sides) if s == 0); c1 = sum(c["conv_" + rn] for c, s in zip(cs, sides) if s == 1)
    return {"m": sum(m_vec(g, arm, rn)) / N, "keep": (k0 + k1) / N, "keep_s0": k0 / n0, "keep_s1": k1 / n1,
            "conv_s0": c0 / n0, "conv_s1": c1 / n1}


out = {"N": N, "n_side0": sides.count(0), "n_side1": sides.count(1)}
# ---------------- self-test ----------------
selftest = {}
selftest["traced_eq_plain_all"] = all(c["chk"]["traced_eq_plain"] for v in calls.values() for c in v)
selftest["stock_eq_common_pair_all"] = all(c["chk"]["eq_common_pair"] for (g, a), v in calls.items() if a == "STOCK" for c in v)
selftest["n_stock_calls_checked"] = sum(len(v) for (g, a), v in calls.items() if a == "STOCK")
ba = json.loads((W / "N17_setter_turnover" / "bank_assay.json").read_text())
BAMAP = {"F": "founder", "AC": "44-ac", "5C": "49-5c", "C3": "43-c3"}
mism = []
for g, k in BAMAP.items():
    s = summ(g, "STOCK", "FID"); ref = ba[k]["ZERO"]
    for a, b in (("m_base", "m"), ("keep", "keep"), ("conv_side0", "conv_s0"), ("conv_side1", "conv_s1")):
        if ref[a] != s[b]:
            mism.append(("bank_assay", g, a, ref[a], s[b]))
a2 = json.loads((W / "W2-41_carried_context" / "a2_assay.json").read_text())["res"]
nchk = 0
for g in GEN:
    for rn in RUL:
        s = summ(g, "STOCK", rn); ref = a2[g]["ZERO"][rn]
        for k in ("m", "keep", "keep_s0", "keep_s1", "conv_s0", "conv_s1"):
            nchk += 1
            if ref[k] != s[k]:
                mism.append(("a2_assay", g, rn, k, ref[k], s[k]))
selftest["bank_assay_and_a2_mismatches"] = mism
selftest["a2_fields_checked"] = nchk
nd = sum(1 for g in GEN for a, b in zip(calls[(g, "STOCK")], calls[(g, "REVERSED")])
         if (a["keep_exact"], a["conv_exact"]) != (b["keep_exact"], b["conv_exact"]))
selftest["negative_control_calls_differing_STOCK_vs_REVERSED"] = nd
selftest["PASS"] = selftest["traced_eq_plain_all"] and selftest["stock_eq_common_pair_all"] and not mism and nd > 0
out["selftest"] = selftest
assert selftest["PASS"], selftest

# ---------------- table ----------------
out["table"] = {g: {a: {rn: summ(g, a, rn) for rn in RUL} for a in ARMS} for g in GEN}


def boot(dv, B=10000, seed="W2-52"):
    rng = random.Random(seed)
    n = len(dv)
    ms = sorted(sum(dv[rng.randrange(n)] for _ in range(n)) / n for _ in range(B))
    mean = sum(dv) / n
    se = st.pstdev(dv) / n ** 0.5
    return {"mean": mean, "ci95_boot": [ms[int(0.025 * B)], ms[int(0.975 * B) - 1]],
            "ci95_normal": [mean - 1.96 * se, mean + 1.96 * se]}


def excl0(ci):
    return ci[0] > 0 or ci[1] < 0


def verdict(ds, dr):
    if dr["mean"] > 0 and excl0(dr["ci95_boot"]):
        return "REFUTED"
    if ds["mean"] > 0 and excl0(ds["ci95_boot"]) and (dr["mean"] <= 0 or not excl0(dr["ci95_boot"])):
        return "CONFIRMED"
    return "UNRESOLVED"


diffs = {}
for rn in RUL:
    for g in GEN[1:]:
        for a in ARMS:
            dv = [p - q for p, q in zip(m_vec(g, a, rn), m_vec("F", a, rn))]
            diffs["%s-F|%s|%s" % (g, a, rn)] = boot(dv)
    # arm effect per genome (REVERSED - STOCK), paired
    for g in GEN:
        dv = [p - q for p, q in zip(m_vec(g, "REVERSED", rn), m_vec(g, "STOCK", rn))]
        diffs["%s:REV-STOCK|%s" % (g, rn)] = boot(dv)
out["paired_diffs"] = diffs
v = {rn: verdict(diffs["AC-F|STOCK|%s" % rn], diffs["AC-F|REVERSED|%s" % rn]) for rn in ("class", "FID")}
v["exact(secondary)"] = verdict(diffs["AC-F|STOCK|exact"], diffs["AC-F|REVERSED|exact"])
v["5C(secondary,class)"] = verdict(diffs["5C-F|STOCK|class"], diffs["5C-F|REVERSED|class"])
v["5C(secondary,FID)"] = verdict(diffs["5C-F|STOCK|FID"], diffs["5C-F|REVERSED|FID"])
v["OVERALL"] = v["class"] if v["class"] == v["FID"] else "UNRESOLVED (ruler-dependent)"
out["verdict"] = v

# ---------------- mechanism tallies ----------------
mech = {}
for g in GEN:
    for a in ARMS:
        for s in (0, 1):
            cs = [c for c, ss in zip(calls[(g, a)], sides) if ss == s]
            c = collections.Counter()
            dom = collections.Counter()
            for q in cs:
                c["N"] += 1
                for k in ("donor_runs_first", "intact_at_donor_start", "partner_enters_donor_half",
                          "partner_runs_donor_LDIR52", "partner_jumps_43_to_108"):
                    c[k] += q[k]
                c["keep_FID"] += q["keep_FID"]; c["conv_FID"] += q["conv_FID"]
                c["keep_class"] += q["keep_class"]; c["conv_class"] += q["conv_class"]
                pre = "intact" if q["intact_at_donor_start"] else "predamaged"
                c["n|" + pre] += 1
                c["conv_class_fail|" + pre] += not q["conv_class"]
                c["keep_class_fail|" + pre] += not q["keep_class"]
                if not q["keep_FID"] and q["auth"]:
                    dom[max(q["auth"], key=q["auth"].get)] += 1
                c["keep_FID_fail_with_partner_LDIR52"] += (not q["keep_FID"]) and q["partner_runs_donor_LDIR52"]
            mech["%s|%s|side%d" % (g, a, s)] = {"counts": dict(sorted(c.items())), "keep_FID_loss_dominant_author": dict(dom)}
out["mechanism"] = mech
(HERE / "r2_analyse.json").write_text(json.dumps(out, indent=1))

# ---------------- print ----------------
print("SELFTEST", json.dumps(selftest))
print("%-6s %-8s | %6s %6s %6s | %s" % ("genome", "arm", "FID", "class", "exact", "class keep s0/s1  conv s0/s1"))
for g in GEN:
    for a in ARMS:
        t = out["table"][g][a]; c = t["class"]
        print("%-6s %-8s | %.3f  %.3f  %.3f | %.3f/%.3f  %.3f/%.3f" % (g, a, t["FID"]["m"], c["m"], t["exact"]["m"],
              c["keep_s0"], c["keep_s1"], c["conv_s0"], c["conv_s1"]))
for k, val in diffs.items():
    print("%-28s %+.3f boot[%+.3f,%+.3f] norm[%+.3f,%+.3f]" % (k, val["mean"], *val["ci95_boot"], *val["ci95_normal"]))
print("VERDICT", v)
for k, val in mech.items():
    cc = val["counts"]
    print(k, {x: cc.get(x, 0) for x in ("N", "intact_at_donor_start", "partner_runs_donor_LDIR52", "partner_jumps_43_to_108",
                                         "keep_FID", "conv_FID", "conv_class_fail|intact", "conv_class_fail|predamaged",
                                         "keep_FID_fail_with_partner_LDIR52")}, val["keep_FID_loss_dominant_author"])
