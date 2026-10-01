"""W2-22 a2 (arithmetic on saved runs, no VM): adversarial checks on the primary. -> a2_adversarial.json"""
import json, math, random
from scipy.stats import fisher_exact, norm
import w22, a1_analyze as A
F_ = A.load("FIELD"); R_ = A.load("FREE")
out = {}
fc = sorted([r for r in F_ if r["B"] >= 27], key=lambda r: r["B"])
out["FIELD_conditioned"] = [{k: r[k] for k in ("s", "B", "Bxk", "kin", "maxA", "A_end", "stop", "epochs", "depth_f")} |
                            {"B_last50": (r["traj"][-1][2] - r["traj"][-51][2]) if len(r["traj"]) > 50 else None} for r in fc]
fr = sorted([r for r in R_ if r["B"] >= 27], key=lambda r: r["B"])
out["FREE_conditioned"] = [{k: r[k] for k in ("s", "B", "maxA", "stop", "epochs", "depth_f")} for r in fr]
# world X-TICKET (W2-14 table): E27 4/128, all 4 reach >= 163
x1, n1 = sum(r["B"] >= 163 for r in fc), len(fc)
out["world_vs_FIELDBANK_conditional"] = {"world": "4/4", "FIELD_BANK": "%d/%d" % (x1, n1),
    "fisher_1s_world_greater": fisher_exact([[4, 0], [x1, n1 - x1]], alternative="greater")[1]}
# alternative CI methods for the C- ratio (9/33 vs 10/48)
def katz(x1, n1, x2, n2):
    lr = math.log((x1 / n1) / (x2 / n2)); se = math.sqrt(1 / x1 - 1 / n1 + 1 / x2 - 1 / n2)
    return math.exp(lr - 1.96 * se), math.exp(lr + 1.96 * se)
def boot(f, g, B=20000, seed=1):
    rng = random.Random(seed); rs = []
    for _ in range(B):
        a = sum(rng.choice(f) for _ in f) / len(f); b = sum(rng.choice(g) for _ in g) / len(g)
        if b > 0: rs.append(a / b)
    rs.sort(); return rs[int(.025 * len(rs))], rs[int(.975 * len(rs))]
fs = [int(r["B"] >= 163) for r in fc]
gm = [int(r["B"] >= 163) for r in fr]
gp = [int(r["B"] >= 163 or r["stop"] == "free_cap256") for r in fr]
out["C-_ratio_CIs"] = {"koopman": A.koopman_ci(sum(fs), len(fs), sum(gm), len(gm)), "katz": katz(sum(fs), len(fs), sum(gm), len(gm)),
                       "bootstrap_pct": boot(fs, gm)}
out["C+_ratio_CIs"] = {"koopman": A.koopman_ci(sum(fs), len(fs), sum(gp), len(gp)), "katz": katz(sum(fs), len(fs), sum(gp), len(gp))}
# FREE cap256 runs below 163: epoch of capping and B at cap
out["FREE_cap_below163"] = sorted((r["epochs"], r["B"]) for r in fr if r["stop"] == "free_cap256" and r["B"] < 163)
# a mid-point censoring treatment: cap256 counts as success only if B >= 100 at cap
gmid = [int(r["B"] >= 163 or (r["stop"] == "free_cap256" and r["B"] >= 100)) for r in fr]
out["C_mid_B100"] = {"FREE": "%d/%d" % (sum(gmid), len(gmid)), "koopman": A.koopman_ci(sum(fs), len(fs), sum(gmid), len(gmid))}
# pooled with W2-14's 40-seed FIELD BANK / FREE BANK (s 0-39)
L = [json.loads(l) for l in open(w22.HERE.parent / "W2-14_F_calibration" / "ladder.jsonl")]
def pick(st): return [r for r in L if r["rule"] == "BASE" and r["struct"] == st and r["partner"] == "BANK" and r["ctx"] == "CARRY" and r["mut"]]
w14f, w14r = pick("FIELD"), pick("FREE")
out["W2-14_seeds"] = {"FIELD": [(r["s"], r["B"], r["stop"]) for r in w14f if r["B"] >= 27], "FREE": [(r["s"], r["B"], r["stop"]) for r in w14r if r["B"] >= 27]}
json.dump(out, open(w22.HERE / "a2_adversarial.json", "w"), indent=1, default=str)
for k, v in out.items():
    print("==", k)
    if isinstance(v, list):
        for x in v: print("  ", x)
    else: print("  ", v)
