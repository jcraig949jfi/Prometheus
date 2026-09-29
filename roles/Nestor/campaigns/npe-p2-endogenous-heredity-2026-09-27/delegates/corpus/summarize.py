"""Aggregate q1_partial.jsonl, q2_regs.json, q2_donors.json, q3_reset.json, q4_provenance.json -> SUMMARY.json."""
import collections
import json
import re

import corpus_analysis as ca

H = ca.HERE
S = json.loads((H / "sample.json").read_text())
G = {(e["vm"], e["cell"], e["hex"]): e for e in S["genomes"]}
q1 = ca.load_q1()
out = {"sample_meta": {k: v for k, v in S["meta"].items() if k != "stratum_sizes"}}


def origin_class(e):
    if e.get("nocopy_donor"):
        return "first_donor_" + e["nocopy_donor"]
    return e["origin_exp"]


def pos_bin(p):
    return "00-15" if p < 16 else "16-31" if p < 32 else "32-47" if p < 48 else "48-63"


# ---------------- Q1
rows = collections.defaultdict(collections.Counter)
runs = collections.defaultdict(collections.Counter)
static = collections.defaultdict(collections.Counter)
pos = collections.defaultdict(list)
for d in q1:
    e = G[(d["vm"], d["cell"], d["hex"])]
    comp = d["rate_full"] >= 0.5
    ind = comp and d["rate_noself"] >= 0.5
    for key in [(d["cell"], d["vm"], origin_class(e)), (d["cell"], "ALL", "ALL"), ("ALL", "ALL", "ALL")]:
        c = rows["|".join(key)]
        c["n"] += 1
        c["competent_rerun"] += comp
        c["self_independent"] += ind
        c["has_ED32"] += e["has_self"]
        c["has_ED32_and_competent"] += e["has_self"] and comp
        c["has_ED32_and_self_independent"] += e["has_self"] and ind
        c["ED32_absent_but_self_dependent"] += (not e["has_self"]) and comp and not ind
    if comp:
        runs[(d["cell"], e["origin_run"])]["comp"] += 1
        runs[(d["cell"], e["origin_run"])]["ind"] += ind
        s = static[d["cell"]]
        s["n"] += 1
        s["first_" + str(e["first_blockcopy"])] += 1
        s["first_is_alias"] += e["first_is_alias"]
        s["only_alias"] += e["only_alias"]
        s["has_ED_form"] += any(k.startswith("ED") for k in e["blockcopy_encodings"])
        s["has_ED32"] += e["has_self"]
        s["pos_" + pos_bin(e["first_blockcopy_pos"])] += 1
        pos[d["cell"]].append(e["first_blockcopy_pos"])
out["q1_by_stratum"] = {k: dict(v) for k, v in sorted(rows.items())}
rl = collections.defaultdict(collections.Counter)
for (cell, run), c in runs.items():
    rl[cell]["runs_with_competent"] += 1
    rl[cell]["runs_all_self_independent"] += c["ind"] == c["comp"]
    rl[cell]["runs_any_self_dependent"] += c["ind"] < c["comp"]
out["q1_by_run"] = {k: dict(v) for k, v in rl.items()}
out["q1_self_dependent_runs"] = sorted("%s %s %d/%d" % (k[0], k[1], c["comp"] - c["ind"], c["comp"])
                                       for k, c in runs.items() if c["ind"] < c["comp"])
out["q1_static_competent"] = {k: dict(v) for k, v in static.items()}
out["q1_first_blockcopy_pos_median"] = {k: sorted(v)[len(v) // 2] for k, v in pos.items()}

# ---------------- Q2
C = ["B", "C", "D", "E", "H", "L", "A", "BC", "DE", "HL", "fz", "fc"]


def q2tab(rs):
    return {"n": len(rs), "base_mean": round(sum(r["base"] for r in rs) / len(rs), 3),
            "mean_rate": {c: round(sum(r[c] for r in rs) / len(rs), 3) for c in C},
            "n_drop_ge_half": {c: sum(r[c] < 0.5 * r["base"] for r in rs) for c in C}}


q2 = json.loads((H / "q2_regs.json").read_text())
t = {}
for cell in ("7ae3", "ffa6"):
    for sd in (True, False):
        v = [r for r in q2 if r["cell"] == cell and r["self_dep"] == sd]
        if v:
            t["%s|%s" % (cell, "SELF_dependent" if sd else "SELF_free")] = q2tab(v)
    t["%s|ALL" % cell] = q2tab([r for r in q2 if r["cell"] == cell])
out["q2_competent_sample"] = t
q2d = json.loads((H / "q2_donors.json").read_text())
out["q2_first_donors_base_ge_0.25"] = {st: q2tab([r for r in q2d if r["nocopy_donor"] == st and r["base"] >= 0.25])
                                       for st in ("NO_COPY", "ESTABLISHED")}

# ---------------- Q3
q3 = json.loads((H / "q3_reset.json").read_text())
R = ["NONE", "B", "C", "D", "E", "H", "L", "A", "BC", "DE", "HL", "fz", "fc", "FLAGS", "ALL_REGS", "ALL"]
SINGLE = ["B", "C", "D", "E", "H", "L", "A", "BC", "DE", "HL", "fz", "fc", "FLAGS"]


def rest(r, k):
    return r["rates"]["ALL"] > 0 and r["rates"][k] >= 0.5 * r["rates"]["ALL"]


q3o = {}
for st in ("NO_COPY", "ESTABLISHED"):
    allr = [r for r in q3 if r["status"] == st]
    ok = [r for r in allr if r["rates"]["ALL"] >= 0.1]
    po = [r for r in ok if r["rates"]["NONE"] < 0.25 * r["rates"]["ALL"]]
    cs = [s["side_regs_BCDEHLA_fz_fc"] for r in allr for s in r["carried_states"]]
    q3o[st] = {"n": len(allr), "n_fresh_rate_ge_0.1": len(ok), "n_poisoned": len(po),
               "mean_rate": {k: round(sum(r["rates"][k] for r in allr) / len(allr), 3) for k in R},
               "poisoned_restored_by": {k: sum(rest(r, k) for r in po) for k in R},
               "poisoned_restored_by_any_single_or_pair": sum(any(rest(r, k) for k in SINGLE) for r in po),
               "poisoned_restored_by_L_or_HL": sum(rest(r, "L") or rest(r, "HL") for r in po),
               "poisoned_restored_by_E_or_DE": sum(rest(r, "E") or rest(r, "DE") for r in po),
               "poisoned_restored_by_B_C_BC_A_flags": sum(any(rest(r, k) for k in ("B", "C", "BC", "A", "fz", "fc", "FLAGS")) for r in po),
               "carried_states_distinct": len(cs),
               "carried_BC_zero_share": round(sum(x[1][0] == 0 and x[1][1] == 0 for x in cs) / len(cs), 3),
               "carried_fz1_share": round(sum(x[2] == 1 for x in cs) / len(cs), 3)}
out["q3"] = q3o

# ---------------- Q4
q4 = json.loads((H / "q4_provenance.json").read_text())
out["q4_n_self_free_competent"] = len(q4)
sides = collections.Counter()
for d in q4:
    a, b = d["side_pass_10"]
    sides[(("side0" if a >= 5 else "") + ("side1" if b >= 5 else "")) or "neither_ge_5of10"] += 1
out["q4_working_side"] = dict(sides)


def kind_src(s):
    s = re.sub(r" @[+-]?\d+", "", s)
    if s == "fresh(0)":
        return "fresh_zero"
    if re.search(r",[0-9A-F]{2,4}$", s):
        return "immediate"
    if "INC" in s or "DEC" in s:
        return "inc_dec"
    if "(HL)" in s or "(BC)" in s or "(DE)" in s:
        return "memory_read"
    return "register_copy"


w0 = [d for d in q4 if d["side"]["0"] and d["side_pass_10"][0] >= 5]
mot = collections.Counter()
for d in w0:
    e = d["side"]["0"]
    hl = e["HL"] & 127
    err = hl if e["kind"] == "LDIR" else (hl - 63) % 128
    mot["DE_minus_HL_eq_64_mod128"] += (e["DE"] - e["HL"]) % 128 == 64
    mot["BC_0_or_ge64"] += e["BC"] == 0 or e["BC"] >= 64
    mot["BC_0"] += e["BC"] == 0
    mot["HL_anchor_exact"] += err == 0
    mot["HL_anchor_within_2"] += err <= 2 or err >= 126
    mot[e["kind"]] += 1
out["q4_side0_motif"] = {"n": len(w0), **dict(mot)}
for reg in ("L", "H", "E", "D", "C", "B"):
    out["q4_side0_%s_source" % reg] = dict(collections.Counter(kind_src(d["side"]["0"]["last_setter"][reg]) for d in w0))
out["q4_side0_any_of_BCDEHL_fresh"] = sum(any(v == "fresh(0)" for v in d["side"]["0"]["last_setter"].values()) for d in w0)
(H / "SUMMARY.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
