"""W2-39 a3: properties of the frozen rule. (i) hull bands per genotype for n = 64/128/256 (R3 at m = round(n*R1));
(ii) null false-kill per readout (world == M*, R3 law = C- and = C+ separately, worst reported) and the per-arm union bound;
(iii) power: P(R1 OUTSIDE) if the world morph arm follows H-NEAR (R1 = 0.08) or the founder's own M* rate (0.046);
(iv) the K4 founder case: world 4/4 at m = 4 vs M* founder R3 hull; (v) a dry run of k2_decide on synthetic counts."""
import json, pathlib
from scipy.stats import binom, betabinom
import band as BD
import k2_decide as KD
HERE = pathlib.Path(__file__).resolve().parent
A = json.load(open(HERE / "a1_results.json"))["genotypes"]
out = {}
for g, v in A.items():
    e, N = v["estimates"], v["counts"]["N"]
    row = {}
    for n in (64, 128, 256):
        r1 = KD.hull(e, None, None, "R1", "R1_Cplus", n)
        m = max(1, round(n * e["R1"]["p"]))
        r3 = KD.hull(e, None, None, "R3_Cminus", "R3_Cplus", m)
        fk = {}
        for key in ("R1", "R1_Cplus"):
            d = betabinom(n, e[key]["x"] + .5, e[key]["n"] - e[key]["x"] + .5)
            fk[key] = sum(d.pmf(k) for k in range(n + 1) if not (r1[0] <= k <= r1[1]))
        for key in ("R3_Cminus", "R3_Cplus"):
            d = betabinom(m, e[key]["x"] + .5, e[key]["n"] - e[key]["x"] + .5)
            fk[key] = sum(d.pmf(k) for k in range(m + 1) if not (r3[0] <= k <= r3[1]))
        pw = {}
        for label, p in (("H-NEAR_0.08", 0.08), ("founder_rate_0.046", 0.0462), ("H-SUPER_0.15", 0.15)):
            pw[label] = float(binom.cdf(r1[0] - 1, n, p) + binom.sf(r1[1], n, p))
        row[str(n)] = {"R1_hull_k": r1, "R1_hull_p": [round(r1[0] / n, 3), round(r1[1] / n, 3)], "m_exp": m,
                       "R3_hull_k": r3, "null_false_kill": {k: round(float(x), 4) for k, x in fk.items()},
                       "per_arm_union_bound": round(float(max(fk["R1"], fk["R1_Cplus"]) + max(fk["R3_Cminus"], fk["R3_Cplus"])), 4),
                       "P_R1_outside_if_world_p": {k: round(x, 4) for k, x in pw.items()}}
    out[g] = row
eF = A["F"]["estimates"]
out["K4_founder_world_4_of_4"] = {"R3_hull_at_m4": KD.hull(eF, None, None, "R3_Cminus", "R3_Cplus", 4),
                                  "inside_Cminus_band": BD.inside(4, eF["R3_Cminus"]["x"], eF["R3_Cminus"]["n"], 4),
                                  "inside_Cplus_band": BD.inside(4, eF["R3_Cplus"]["x"], eF["R3_Cplus"]["n"], 4)}
out["dry_run"] = KD.decide({"F": {"n": 128, "k27": 6, "k163": 2, "kB27": 6},
                            "AC": {"n": 128, "k27": 10, "k163": 5, "kB27": 10},
                            "81": {"n": 128, "k27": 38, "k163": 33, "kB27": 38}}, A)
print(json.dumps(out, indent=1))
json.dump(out, open(HERE / "a3_rule_props.json", "w"), indent=1)
