"""W2-29 a1: pre-registered analysis. FULL prefix vs W2-22 FIELD BANK on the same seed prefix; morph strata from c1."""
import json, sys, pathlib
from scipy.stats import fisher_exact
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-22_second_regime"))
from a1_analyze import koopman_ci  # W2-22's Koopman

def L(p): return [json.loads(l) for l in open(p)]
full = L(HERE / "runs_FULL.jsonl")
smax = max(r["s"] for r in full)
assert sorted(r["s"] for r in full) == list(range(1000, smax + 1)), "prefix not contiguous"
bank = [r for r in L(HERE.parent / "W2-22_second_regime" / "runs_FIELD.jsonl") if r["s"] <= smax]
rep = {r["s"]: r for r in L(HERE / "runs_BANKREP.jsonl")}
cls = json.load(open(HERE / "c1_classes.json"))
gen = {}
for tag in ("FULL", "BANKREP"):
    for d in L(HERE / ("genomes_%s.jsonl" % tag)):
        gen[(tag, d["s"])] = d

def morph(tag, s):
    d = gen.get((tag, s))
    if d is None: return None
    hits = [(e, b, c, h) for h, e, b, c in d["genomes"] if cls[h]["confirmed"]]
    side0_unconf = sum(1 for h, *_ in d["genomes"] if cls[h]["side0"] and not cls[h]["confirmed"])
    if not hits: return {"present": False, "by27": False, "first_ep": None, "B_first": None, "n_types": 0,
                         "n_births": 0, "side0_unconfirmed": side0_unconf, "founder_is_side0": cls[d["founder"]]["side0"]}
    hits.sort()
    return {"present": True, "by27": min(b for _, b, _, _ in hits) <= 27, "first_ep": hits[0][0],
            "B_first": min(b for _, b, _, _ in hits), "n_types": len(hits), "n_births": sum(c for *_, c, _ in hits),
            "side0_unconfirmed": side0_unconf, "founder_is_side0": cls[d["founder"]]["side0"]}

rows = []
for arm, R, tag in (("FULL", full, "FULL"), ("BANK", bank, "BANKREP")):
    for r in R:
        if r["B"] < 27: continue
        m = morph(tag, r["s"])
        row = {"arm": arm, "s": r["s"], "stop": r["stop"], "epochs": r["epochs"], "B": r["B"], "Bxk": r["Bxk"],
               "kin": r["kin"], "maxA": r["maxA"], "succ": r["Bxk"] >= 163, "succB": r["B"] >= 163}
        if arm == "BANK":
            rr = rep[r["s"]]
            row["replay_ok"] = (rr["Bxk"] >= 163) == (r["Bxk"] >= 163) and (r["Bxk"] >= 163 or (rr["B"], rr["Bxk"]) == (r["B"], r["Bxk"]))
        row.update({"m_" + k: v for k, v in m.items()})
        rows.append(row)

def tab(sel):
    x = sum(r["succ"] for r in sel); return x, len(sel)
def fis(a, b):
    (x1, n1), (x2, n2) = a, b
    if n1 == 0 or n2 == 0: return None
    return fisher_exact([[x1, n1 - x1], [x2, n2 - x2]], alternative="greater")[1]

out = {"prefix_last_seed": smax, "n_full": len(full), "n_bank": len(bank),
       "E27": {"FULL": sum(r["B"] >= 27 for r in full), "BANK": sum(r["B"] >= 27 for r in bank)},
       "full_cpu_s": round(sum(r["cpu_s"] for r in full), 1), "rows": rows}
out["eligible"] = out["E27"]["FULL"] >= 10
F = [r for r in rows if r["arm"] == "FULL"]; B = [r for r in rows if r["arm"] == "BANK"]
out["primary"] = {"FULL": tab(F), "BANK": tab(B), "p_1s": fis(tab(F), tab(B))}
if tab(B)[0] > 0 and tab(F)[0] > 0:
    out["primary"]["koopman_ratio95"] = koopman_ci(tab(F)[0], tab(F)[1], tab(B)[0], tab(B)[1])
out["primary_B"] = {"FULL": (sum(r["succB"] for r in F), len(F)), "BANK": (sum(r["succB"] for r in B), len(B))}
for key in ("present", "by27"):
    k = "m_" + key
    st = {}
    for arm, S in (("FULL", F), ("BANK", B)):
        st[arm] = {"morph": tab([r for r in S if r[k]]), "none": tab([r for r in S if not r[k]])}
    res = {"strata": st,
           "RESIDUE_p (no-morph FULL>BANK)": fis(st["FULL"]["none"], st["BANK"]["none"]),
           "MORPH_p_FULL": fis(st["FULL"]["morph"], st["FULL"]["none"]),
           "MORPH_p_BANK": fis(st["BANK"]["morph"], st["BANK"]["none"]),
           "morph_stratum FULL>BANK p": fis(st["FULL"]["morph"], st["BANK"]["morph"])}
    rp, mf, mb = res["RESIDUE_p (no-morph FULL>BANK)"], res["MORPH_p_FULL"], res["MORPH_p_BANK"]
    resid = rp is not None and rp < 0.05
    mor = mf is not None and mb is not None and mf < 0.05 and mb < 0.05
    res["verdict"] = "BOTH" if resid and mor else "RESIDUE" if resid else "MORPH" if mor else "UNRESOLVED"
    out["rule_" + key] = res
json.dump(out, open(HERE / "a1_analysis.json", "w"), indent=1)
for k, v in out.items():
    if k != "rows": print(k, v)
print("%-5s %5s %-8s %4s %6s %5s %5s %4s %s" % ("arm", "s", "stop", "ep", "B", "Bxk", "kin", "succ", "morph(first_ep,B_first,n_types,n_births)"))
for r in rows:
    print("%-5s %5d %-8s %4d %6d %5d %5d %4s %s" % (r["arm"], r["s"], r["stop"], r["epochs"], r["B"], r["Bxk"], r["kin"], int(r["succ"]),
          (r["m_first_ep"], r["m_B_first"], r["m_n_types"], r["m_n_births"], "unconf", r["m_side0_unconfirmed"]) if r["m_present"] else ("-", "unconf", r["m_side0_unconfirmed"])) + (" replay_ok=%s" % r["replay_ok"] if "replay_ok" in r else ""))
