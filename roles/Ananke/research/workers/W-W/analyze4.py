"""PLAN s3/s4/s6 analysis: FC max tables (Wilson 99%), pass/robust, H0 vs W-U reproduction, T90/PCT must-fail,
power table, frozen s4 decision. Reads out/jobs/*.json (+ W-U out/fc_w*.json, reach_w*.json). -> out/analysis.json,
stdout tables."""
import glob
import json
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
WU = HERE.parent / "W-U" / "out"
CANDS = ("H0", "H1", "H2", "H3")
CTRL = ("T90", "PCT")
VS = ("FLIP_REL", "NO_EFFECT_REL", "CHANCE_REL")
PS, KS, MODELS = (32, 64, 128, 256), (3, 11, 12), ("worst", "realistic", "hetero")
Z = 2.5758293035489


def wilson(k, n, z=Z):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def load_jobs():
    J = {}
    for f in glob.glob(str(HERE / "out" / "jobs" / "*.json")):
        d = json.load(open(f))
        J[d["job"]] = d
    return J


def fc_tables(J):
    T = {}
    missing = []
    for c in CANDS + CTRL:
        T[c] = {}
        for P in PS:
            for K in KS:
                cell = {"pass": True, "robust": True, "fc_max": {}, "fails": []}
                for v in VS:
                    best = None
                    for m in MODELS:
                        j = J.get(f"FC_P{P}_K{K}_{m}")
                        if j is None:
                            missing.append((P, K, m))
                            cell["pass"] = None
                            continue
                        for p, r in j["res"].items():
                            k, n = r["k"][c][v], r["n"]
                            lo, hi = wilson(k, n)
                            if k / n > 0.01:
                                cell["pass"] = False if cell["pass"] is not None else None
                                cell["fails"].append([v, m, p, k / n, n])
                            if hi > 0.01:
                                cell["robust"] = False
                            if best is None or k / n > best[0]:
                                best = [k / n, lo, hi, n, m, p]
                    cell["fc_max"][v] = best
                T[c][f"P{P}_K{K}"] = cell
    return T, sorted(set(missing))


def wu_repro(J):
    """H0 counts vs W-U BOOTT counts: exact where n equal (same seeds, addendum D4), else two-proportion z."""
    W = {}
    for f in glob.glob(str(WU / "fc_w*.json")):
        W.update(json.load(open(f)))
    exact = mism = 0
    zs = []
    bad = []
    for P in PS:
        for K in KS:
            for m in MODELS:
                j = J.get(f"FC_P{P}_K{K}_{m}")
                w = W.get(f"P{P}_K{K}_{m}")
                if j is None or w is None:
                    continue
                for p, r in j["res"].items():
                    rw = w[p]
                    for v in VS:
                        a, b = r["k"]["H0"][v], rw["k"]["BOOTT"][v]
                        if r["n"] == rw["n"]:
                            if a == b:
                                exact += 1
                            else:
                                mism += 1
                                bad.append([P, K, m, p, v, a, b, r["n"]])
                        else:
                            p1, p2 = a / r["n"], b / rw["n"]
                            pp = (a + b) / (r["n"] + rw["n"])
                            se = math.sqrt(max(pp * (1 - pp), 1e-12) * (1 / r["n"] + 1 / rw["n"]))
                            zs.append([P, K, m, p, v, (p1 - p2) / se, r["n"], rw["n"]])
    return {"exact_equal": exact, "exact_mismatch": mism, "mismatch_list": bad[:20],
            "n_differs_points": len(zs), "max_abs_z": max([abs(z[5]) for z in zs], default=None),
            "z_gt_3": [z for z in zs if abs(z[5]) > 3]}


def power(J):
    Pw = {}
    for P in (32, 64):
        for K in (3, 11):
            for m in ("worst", "realistic"):
                j = J.get(f"POW_P{P}_K{K}_{m}")
                if j:
                    Pw[f"P{P}_K{K}_{m}"] = j["res"]
    return Pw


def decide(T, Pw):
    elig = [c for c in CANDS if all(T[c][d]["pass"] is True for d in T[c])]
    r = Pw.get("P64_K11_realistic")
    score = {}
    for c in CANDS:
        if r:
            score[c] = min(min(r[p]["FLIP_REL"][c], r[p]["NO_EFFECT_REL"][c]) for p in ("0.95", "0.99"))
    chosen = None
    if elig and r:
        best = max(score[c] for c in elig)
        order = ["H1", "H2", "H3", "H0"]   # s4.3 ties -> simplest among hybrids (H1<H2<H3)
        chosen = [c for c in order if c in elig and score[c] == best][0]
    prom = None
    if chosen and r:
        f99, n99 = r["0.99"]["FLIP_REL"][chosen], r["0.99"]["NO_EFFECT_REL"][chosen]
        prom = {"chosen": chosen, "FLIP_p99": f99, "NOEFF_p99": n99, "power_bar_ok": f99 >= 0.80 and n99 >= 0.80,
                "is_hybrid": chosen != "H0"}
    return {"eligible": elig, "score_min_FN_p95_p99_P64K11_realistic": score, "chosen": chosen, "promotion": prom}


if __name__ == "__main__":
    J = load_jobs()
    T, missing = fc_tables(J)
    R = {"missing": missing, "fc": T, "repro": wu_repro(J), "power": power(J)}
    R["decision"] = decide(T, R["power"])
    R["cpu_s_jobs"] = sum(j.get("cpu_s", 0) for j in J.values())
    json.dump(R, open(HERE / "out" / "analysis.json", "w"), indent=1)
    print("jobs", len(J), "missing FC designs", len(missing), "cpu core-h", round(R["cpu_s_jobs"] / 3600, 3))
    print("\nMAX FC % [Wilson 99%] (model p) per candidate x design; PASS/robust")
    for c in CANDS + CTRL:
        for d, cell in T[c].items():
            s = " ".join(f"{v[0]}{cell['fc_max'][v][0]*100:.2f}[{cell['fc_max'][v][1]*100:.2f},{cell['fc_max'][v][2]*100:.2f}]"
                         f"{cell['fc_max'][v][4][0]}{cell['fc_max'][v][5]}" if cell['fc_max'][v] else f"{v[0]}--" for v in VS)
            print(f"{c:4s} {d:8s} {s}  pass={cell['pass']} robust={cell['robust']} nfail={len(cell['fails'])}")
    print("\nREPRO", {k: v for k, v in R["repro"].items() if k != "z_gt_3"}, "z>3:", R["repro"]["z_gt_3"][:5])
    print("\nPOWER (F/N/C) per candidate")
    for d, r in R["power"].items():
        for p, rr in r.items():
            print(d, p, " ".join(f"{c}:{rr['FLIP_REL'][c]:.3f}/{rr['NO_EFFECT_REL'][c]:.3f}/{rr['CHANCE_REL'][c]:.3f}"
                                 for c in CANDS + CTRL), "fbF/N@FLIP", rr["FLIP_REL"]["_fb"])
    print("\nDECISION", json.dumps(R["decision"], indent=1))
