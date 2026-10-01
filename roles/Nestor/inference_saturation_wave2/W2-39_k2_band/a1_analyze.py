"""W2-39 a1: R1/R2/R3 per genotype from runs_*.jsonl (fresh seeds 39_390_000+s), Jeffreys 95% CIs, and K2 prediction
bands for world arms n = 64/128/256 (R1, R2) and for R3 at the world denominator m implied by n (m = round(n*R1_M*)),
plus m = 3..40 tables. C- / C+ cap treatments as W2-22. Also: founder cross-check vs W2-22 FREE (seeds 9_999_000+)
and vs the world's 4/128 (R1 proxy = B>=27). Writes a1_results.json."""
import json, pathlib
from scipy.stats import fisher_exact
import band as BD
HERE = pathlib.Path(__file__).resolve().parent
GEN = ["F", "AC", "81", "C3", "C3+AC"]
CAP = "free_cap256"


def load(g):
    return [json.loads(l) for l in open(HERE / ("runs_%s.jsonl" % g.replace("+", "_")))]


def counts(R):
    N = len(R)
    e27 = [r for r in R if r["Bxk"] >= 27]
    c = {"N": N, "seeds": [min(r["s"] for r in R), max(r["s"] for r in R)], "n_unique_s": len({r["s"] for r in R}),
         "R1": len(e27),
         "R1_Cplus": sum(r["Bxk"] >= 27 or r["stop"] == CAP for r in R),
         "R2": sum(r["maxA"] >= 40 and r["B"] >= 27 for r in R),
         "R2_Cplus": sum((r["maxA"] >= 40 and r["B"] >= 27) or r["stop"] == CAP for r in R),
         "m27": len(e27),
         "R3_num_Cminus": sum(r["Bxk"] >= 163 for r in e27),
         "R3_num_Cplus": sum(r["Bxk"] >= 163 or r["stop"] == CAP for r in e27),
         "P_B163_uncond": sum(r["Bxk"] >= 163 for r in R),
         "cap_runs": sum(r["stop"] == CAP for r in R),
         "cap_runs_Bxk_lt27": sum(r["stop"] == CAP and r["Bxk"] < 27 for r in R),
         "cap_runs_in_m27_Bxk_lt163": sum(r["stop"] == CAP and 27 <= r["Bxk"] < 163 for r in R),
         "label_flood_maxA40_B_lt27": sum(r["maxA"] >= 40 and r["B"] < 27 for r in R),
         "kin_births_total": sum(r["kin"] for r in R), "B_eq_Bxk_all": all(r["B"] == r["Bxk"] for r in R),
         "stops": {s: sum(r["stop"] == s for r in R) for s in sorted({r["stop"] for r in R})},
         "median_epochs_cap": sorted([r["epochs"] for r in R if r["stop"] == CAP] or [0])[
             len([r for r in R if r["stop"] == CAP]) // 2],
         "cpu_s": round(sum(r["cpu_s"] for r in R), 1)}
    return c


out = {"genotypes": {}}
for g in GEN:
    c = counts(load(g))
    N, m = c["N"], c["m27"]
    est = {}
    for k, (x, n) in {"R1": (c["R1"], N), "R1_Cplus": (c["R1_Cplus"], N), "R2": (c["R2"], N),
                      "R2_Cplus": (c["R2_Cplus"], N), "R3_Cminus": (c["R3_num_Cminus"], m),
                      "R3_Cplus": (c["R3_num_Cplus"], m)}.items():
        est[k] = {"x": x, "n": n, "p": round(x / n, 4) if n else None,
                  "ci95": [round(v, 4) for v in BD.jeffreys_ci(x, n)]}
    bands = {}
    for nw in (64, 128, 256):
        b = {}
        for k in ("R1", "R1_Cplus", "R2"):
            bb = BD.band(est[k]["x"], N, nw)
            bb["false_kill"] = round(BD.false_kill(est[k]["x"], N, nw), 4)
            b[k] = bb
        mw = max(1, round(nw * c["R1"] / N))
        b["m_expected"] = mw
        for k in ("R3_Cminus", "R3_Cplus"):
            bb = BD.band(est[k]["x"], m, mw)
            bb["false_kill"] = round(BD.false_kill(est[k]["x"], m, mw), 4)
            b[k] = bb
        bands[str(nw)] = b
    r3tab = {}
    for mw in (3, 5, 8, 10, 15, 20, 30, 40, 60, 100):
        r3tab[str(mw)] = {k: [BD.band(est[k]["x"], m, mw)["k_lo"], BD.band(est[k]["x"], m, mw)["k_hi"]]
                          for k in ("R3_Cminus", "R3_Cplus")}
    out["genotypes"][g] = {"counts": c, "estimates": est, "bands": bands, "R3_band_by_m": r3tab}

# founder cross-checks
W22 = [json.loads(l) for l in open(HERE.parent / "W2-22_second_regime" / "runs_FREE.jsonl")]
cw = counts(W22)
cf = out["genotypes"]["F"]["counts"]
out["founder_vs_W2-22_FREE"] = {
    "W2-22": {k: cw[k] for k in ("N", "R1", "R2", "m27", "R3_num_Cminus", "R3_num_Cplus")},
    "W2-39": {k: cf[k] for k in ("N", "R1", "R2", "m27", "R3_num_Cminus", "R3_num_Cplus")},
    "fisher_R1_p": fisher_exact([[cf["R1"], cf["N"] - cf["R1"]], [cw["R1"], cw["N"] - cw["R1"]]])[1],
    "fisher_R2_p": fisher_exact([[cf["R2"], cf["N"] - cf["R2"]], [cw["R2"], cw["N"] - cw["R2"]]])[1]}
xF, NF = cf["R1"], cf["N"]
out["world_4_of_128_inside_Mstar_F_R1_band"] = BD.inside(4, xF, NF, 128)
out["world_4_of_128_inside_Mstar_F_R2_band"] = BD.inside(4, cf["R2"], NF, 128)
out["world_founder_control_band_from_4_of_128"] = {str(n): BD.band(4, 128, n) for n in (64, 128, 256)}
# null false-kill for the full K2 rule per morph genotype at n=128 (R1 outside OR R3 outside under BOTH treatments)
print(json.dumps({g: {"N": v["counts"]["N"], **{k: (v["estimates"][k]["x"], v["estimates"][k]["n"], v["estimates"][k]["p"],
                  v["estimates"][k]["ci95"]) for k in v["estimates"]}} for g, v in out["genotypes"].items()}, indent=0))
json.dump(out, open(HERE / "a1_results.json", "w"), indent=1)
