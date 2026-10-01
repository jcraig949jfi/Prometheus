"""W2-30 T3: analysis of t2_neighbourhood.json (no VM calls). Protection classes per the rule pre-specified in
t2's docstring; one-bit tables for 43/44/45; expected copy-error-child m; per-birth (copy error) and
per-interaction (in-place OPERAND _mutate, world.py:484-550 perturb law) protection-loss probabilities."""
import json, pathlib, collections
HERE = pathlib.Path(__file__).resolve().parent
D = json.load(open(HERE / "t2_neighbourhood.json"))
rows = D["rows"]
CM = 0.002
par = {x["parent"]: x for x in rows if x["kind"] == "parent"}
minK = lambda d: min(d["keepF0"], d["keepF1"])
maxC = lambda d: max(d["convF0"], d["convF1"])
REF = {"C3": "F", "C3+AC": "AC", "F": "F"}
thr = {p: (minK(par[p]) + minK(par[REF[p] if p != "F" else "F"])) / 2 for p in ("C3", "C3+AC")}
thr["F"] = thr["C3"]
NAMED = {}
F = bytes.fromhex(par["F"]["hex"])


def cls(d, p):
    if maxC(d) < 0.5:
        return "noncopier"
    return "protected" if minK(d) >= thr[p] else "unprotected"


def name_of(h):
    for nm in ("F", "C3", "C3+AC", "AC"):
        if par[nm]["hex"] == h:
            return nm
    return None


out = {"thr": thr, "parents": {p: {k: par[p][k] for k in ("m_exact", "m_class", "m_FID", "keepF0", "keepF1", "convF0", "convF1")} for p in par}}
for p in ("F", "C3", "C3+AC"):
    bits = [x for x in rows if x["parent"] == p and x["kind"] == "bit"]
    assert len(bits) == 512
    c = collections.Counter(cls(x, p) for x in bits)
    exp = {m: sum(x[m] for x in bits) / 512 for m in ("m_exact", "m_class", "m_FID")}
    # side-switch / conversion-side change
    tab = {}
    for pos in (43, 44, 45):
        tab[pos] = [{"bit": x["arg"], "val": "%02x" % bytes.fromhex(x["hex"])[pos], "class": cls(x, p),
                     "named": name_of(x["hex"]), "m_class": x["m_class"], "m_exact": x["m_exact"],
                     "keepF0": x["keepF0"], "keepF1": x["keepF1"], "convF0": x["convF0"], "convF1": x["convF1"]}
                    for x in bits if x["pos"] == pos]
    nonprot = [x for x in bits if cls(x, p) != "protected"]
    bypos = collections.Counter(x["pos"] for x in nonprot)
    better = sorted([x for x in bits if x["m_class"] > par[p]["m_class"] + 0.03], key=lambda x: -x["m_class"])
    out[p] = {"onebit_class_counts": dict(c), "onebit_frac_protected": c["protected"] / 512,
              "expected_m_copyerror_child": exp,
              "nonprotected_by_pos": dict(sorted(bypos.items())),
              "per_birth_loss_copyerror": CM / 8 * len(nonprot),
              "per_birth_any_copyerror": 1 - (1 - CM) ** 64,
              "unconditional_child_m_class": (1 - CM) ** 64 * par[p]["m_class"] + CM / 8 * sum(x["m_class"] for x in bits),
              "table_43_45": tab,
              "better_than_parent_m_class": [(x["pos"], x["arg"], round(x["m_class"], 3), cls(x, p)) for x in better[:10]],
              "n_protected_to_reach_from_F" if p == "F" else "_": [(x["pos"], "%02x" % bytes.fromhex(x["hex"])[x["pos"]], x["m_class"]) for x in bits if cls(x, p) == "protected"] if p == "F" else None}
# in-place OPERAND channel: per-interaction loss
for p in ("C3", "C3+AC"):
    P = bytes.fromhex(par[p]["hex"])
    vals = {}
    for x in rows:
        if x["parent"] == p and x["kind"] in ("val", "bit"):
            g = bytes.fromhex(x["hex"])
            vals[(x["pos"], g[x["pos"]])] = x
    ops = D["ops"][p]
    tot = 0.0
    per = {}
    exp_m = 0.0
    for i in ops:
        b0 = P[i]
        pr = collections.Counter()
        for dlt in range(-8, 9):
            pr[(b0 + dlt) & 0xFF] += 0.45 / 17
        for b in range(8):
            pr[b0 ^ (1 << b)] += 0.45 / 8
        for v in range(256):
            pr[v] += 0.10 / 256
        loss = sum(q for v, q in pr.items() if v != b0 and cls(vals[(i, v)], p) != "protected")
        per[i] = round(CM * loss, 7)
        tot += CM * loss
    out[p]["inplace_operand_positions"] = ops
    out[p]["per_interaction_loss_inplace"] = tot
    out[p]["per_interaction_loss_inplace_by_pos"] = per
    # full 256 tables at 43/44/45: count protected values
    out[p]["full256_protected_count"] = {i: sum(1 for v in range(256) if v != P[i] and cls(vals[(i, v)], p) == "protected") for i in (43, 44, 45)}
    out[p]["full256_44_45_protected_values"] = {i: ["%02x" % v for v in range(256) if v != P[i] and cls(vals[(i, v)], p) == "protected"] for i in (44, 45)}
# routes to C3+AC
C3 = bytes.fromhex(par["C3"]["hex"])
out["routes"] = {
    "F->C3 per birth (copy error, 43 bit1)": CM / 8,
    "F->AC per birth (copy error, 44 bit6)": CM / 8,
    "C3->C3+AC per birth (copy error 44 bit6)": CM / 8,
    "C3->C3+AC per interaction in-place (44 is an operand of JP in C3)": CM * (0.45 / 8 + 0.10 / 256),
    "AC->C3+AC per birth (copy error 43 bit1; 43 is an opcode in AC, so no in-place)": CM / 8,
    "C3+AC->C3 per interaction in-place (44 AC->EC)": CM * (0.45 / 8 + 0.10 / 256),
}
(HERE / "t3_analysis.json").write_text(json.dumps(out, indent=1))
print(json.dumps({"thr": thr, "parents": out["parents"]}, indent=1))
for p in ("F", "C3", "C3+AC"):
    o = out[p]
    print("\n==", p, o["onebit_class_counts"], "frac_prot %.3f" % o["onebit_frac_protected"], "exp_m", {k: round(v, 3) for k, v in o["expected_m_copyerror_child"].items()},
          "loss/birth %.2e" % o["per_birth_loss_copyerror"], "uncond child m_class %.3f" % o["unconditional_child_m_class"])
    print(" nonprot by pos", o["nonprotected_by_pos"])
    print(" better", o["better_than_parent_m_class"])
    if p == "F":
        print(" F->protected", o["n_protected_to_reach_from_F"])
    for pos, t in o["table_43_45"].items():
        for e in t:
            print("  ", pos, e["bit"], e["val"], e["class"], e["named"], "mc %.3f me %.3f k0 %.2f k1 %.2f c0 %.2f c1 %.2f" % (e["m_class"], e["m_exact"], e["keepF0"], e["keepF1"], e["convF0"], e["convF1"]))
    if p != "F":
        print(" inplace loss/interaction %.2e" % o["per_interaction_loss_inplace"], o["per_interaction_loss_inplace_by_pos"])
        print(" full256 protected", o["full256_protected_count"], o["full256_44_45_protected_values"])
print(out["routes"])
