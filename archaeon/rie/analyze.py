"""RIE-01 analysis (frozen with the preregistration). Evidence tiers are kept apart (directive C14):
  1 UNBIASED EVENT RATES   from unbiased-lane worlds only (wave 0 + the reserved 40% of later waves): per factor level, per million
                           arrivals / per world, with exact Poisson (Garwood) 95% intervals, for every transition of the map
                           arrivals -> latent copier (1-in-8 ruler sample x 8) -> first reproduction -> genetic establishment
                           -> amplification / dependency -> long-run architecture (takeover, coexistence)
  2 ADAPTIVE DISCOVERY     events found in adaptive-lane worlds: listed as SPECIMENS, never pooled into rates
  3 CAUSAL COMPARISONS     wave 0 only: every cell has seeds 0..3 on identical inflow tape streams; per factor, paired differences of
                           genetic establishments per world against the reference level (IID / REPLACE / WELL_MIXED / vmcopy) matched on
                           all other factors and seed; exact two-sided sign test; Holm over each factor's contrasts
  4 FORENSIC MECHANISMS    top specimens (originated, unclassified, liberation, acquisition, host-amplified takeovers) with evidence pointers;
                           post-campaign replays: identity replay (same spec+seed must reproduce) and counterfactual regime -> IID replay
                           (does the same founding arrival still establish?). Once = SPECIMEN; reproduced under intervention = EVIDENCE
  5 SPECULATIVE            anything else is labelled hypothesis
    python -m archaeon.rie.analyze [--counterfactuals 8]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
FACTORS = {"regime": "IID", "inflow": "REPLACE", "topology": "WELL_MIXED", "substrate": "vmcopy"}


def garwood(k, alpha=0.05):
    from scipy.stats import chi2
    lo = 0.0 if k == 0 else chi2.ppf(alpha / 2, 2 * k) / 2; hi = chi2.ppf(1 - alpha / 2, 2 * k + 2) / 2
    return [lo, hi]


def tail2(pos, neg):
    n = pos + neg
    if n == 0: return 1.0
    k = max(pos, neg); return min(1.0, 2 * sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n)


def holm(ps):
    order = sorted(ps, key=lambda k: ps[k]); out = {}; stop = False
    for i, k in enumerate(order):
        if not stop and ps[k] <= 0.05 / (len(order) - i): out[k] = True
        else: stop = True; out[k] = False
    return out


def world_metrics(r):
    gl = list(r["glins"].values()); est = [g for g in gl if g["established"] and not g["inserted"]]
    return {"arrivals": r["arrivals"], "latent_copier_est": r["latent_copier_arrivals_sample"] * r["ruler_sample_every"],
            "latent_exact_est": r["latent_exact_arrivals_sample"] * r["ruler_sample_every"],
            "first_reproduction": sum(1 for g in gl if g["root"] == "arrival" and g["births"] >= 1 and not g["inserted"]),
            "originations_reproducing": sum(1 for g in gl if g["root"] == "origination" and g["births"] >= 1 and not g["inserted"]),
            "established": len(est), "established_originated": sum(1 for g in est if g["mechanism"] == "ORIGINATED_GENOME"),
            "amplified_glins": sum(1 for g in gl if g["births_hosted"] > 0), "hosted_births": sum(g["births_hosted"] for g in gl),
            "host_execution_births": r["births_by_mechanism"].get("HOST_EXECUTION", 0), "births": r["births"],
            "env_gated": sum(1 for g in est if "ENV_GATED" in g["dependency"]), "env_free": sum(1 for g in est if "ENV_FREE" in g["dependency"]),
            "host_dependent": sum(1 for g in est if "HOST_DEPENDENT" in g["dependency"]), "liberation": sum(1 for g in est if g["liberation"]),
            "acquisition": sum(1 for g in est if g["acquisition"]), "unclassified": sum(1 for g in est if g["mechanism"] == "UNCLASSIFIED_REPRODUCTIVE_MECHANISM"),
            "takeover": int(r["takeover_observations"] > 0), "coexistence": r["coexistence_episodes"],
            "mechanisms": Counter(g["mechanism"] for g in est), "foreign_executor_roles": sum(1 for g in gl if g["foreign_executor_role"])}


RATE_KEYS = ["latent_copier_est", "latent_exact_est", "first_reproduction", "originations_reproducing", "established", "established_originated", "amplified_glins",
             "hosted_births", "env_gated", "env_free", "host_dependent", "liberation", "acquisition", "unclassified", "takeover", "coexistence"]


def load():
    worlds = []
    for p in sorted(RUNS.glob("*.json")):
        r = json.loads(p.read_text(encoding="utf-8")); r["_file"] = p.name; worlds.append(r)
    return worlds


def rates(ws):
    out = {}
    for f in FACTORS:
        lv = defaultdict(list)
        for r in ws: lv[r["spec"][f]].append(r)
        out[f] = {}
        for level, rs in sorted(lv.items()):
            arr = sum(r["arrivals"] for r in rs); m = [world_metrics(r) for r in rs]; row = {"worlds": len(rs), "arrivals": arr}
            for k in RATE_KEYS:
                tot = sum(x[k] for x in m); ci = garwood(int(round(tot)))
                row[k] = {"total": tot, "per_world": round(tot / len(rs), 4), "per_million_arrivals": round(1e6 * tot / max(1, arr), 4),
                          "per_million_ci95": [round(1e6 * c / max(1, arr), 4) for c in ci]}
            row["mechanisms"] = dict(sum((x["mechanisms"] for x in m), Counter()))
            out[f][level] = row
    return out


def causal(w0):
    key = lambda r, f: tuple((k, r["spec"][k]) for k in FACTORS if k != f) + (("seed", r["seed"]),)
    out = {}
    for f, ref in FACTORS.items():
        idx = {}
        for r in w0: idx[(key(r, f), r["spec"][f])] = world_metrics(r)["established"]
        levels = sorted({r["spec"][f] for r in w0} - {ref}); ps = {}; res = {}
        for lv in levels:
            pos = neg = 0; d = []
            for (k, l), y in idx.items():
                if l != ref: continue
                y2 = idx.get((k, lv))
                if y2 is None: continue
                d.append(y2 - y); pos += y2 > y; neg += y2 < y
            ps[lv] = tail2(pos, neg); res[lv] = {"pairs": len(d), "mean_diff_established_per_world": round(sum(d) / max(1, len(d)), 4), "pos": pos, "neg": neg, "p_two_sided": ps[lv]}
        h = holm(ps) if ps else {}
        for lv in res: res[lv]["holm_significant"] = h[lv]
        out[f] = {"reference": ref, "contrasts": res}
    return out


def specimens(ws, lane):
    sp = []
    for r in ws:
        for gid, g in r["glins"].items():
            if not g["established"] or g["inserted"]: continue
            tags = [t for t, c in (("ORIGINATED", g["mechanism"] == "ORIGINATED_GENOME"), ("UNCLASSIFIED", g["mechanism"] == "UNCLASSIFIED_REPRODUCTIVE_MECHANISM"),
                                   ("LIBERATION", g["liberation"]), ("ACQUISITION", g["acquisition"]), ("HOST_AMPLIFIED", g["mechanism"] == "HOST_AMPLIFIED"),
                                   ("FOREIGN_EXECUTOR", g["foreign_executor_role"])) if c]
            if tags: sp.append({"lane": lane, "file": r["_file"], "spec": r["spec"], "seed": r["seed"], "glin": gid, "tags": tags, "arrival": g["arrival"],
                                "mechanism": g["mechanism"], "founder_class": g["founder_class"], "dominant_class": g["dominant_class"], "dependency": g["dependency"],
                                "births": g["births"], "hosted": g["births_hosted"], "peak": g["peak"], "max_ggen": g["max_ggen"],
                                "founder_tape": g["founder_tape"], "dominant_genome": g["dominant_genome"], "dominant_exact_inputs": g["dominant_exact_inputs"]})
    return sp


def counterfactuals(sp, n):
    from archaeon.rie.world import run_world
    out = []
    pick = sorted([s for s in sp if s["arrival"] is not None], key=lambda s: (-len(s["tags"]), -s["peak"]))[:n]
    for s in pick:
        same = run_world(s["spec"], s["seed"]); ident = str(s["glin"]) in {str(k) for k in same["genetic_established"]}
        cf_spec = dict(s["spec"], regime="IID") if s["spec"]["regime"] != "IID" else dict(s["spec"], regime="PERIODIC")
        cf = run_world(cf_spec, s["seed"])
        cf_est = any(g["arrival"] == s["arrival"] and g["established"] for g in cf["glins"].values())
        out.append({"specimen": {k: s[k] for k in ("file", "glin", "tags", "arrival", "mechanism")}, "identity_replay_reproduces": ident,
                    "counterfactual_regime": cf_spec["regime"], "same_arrival_establishes_under_counterfactual": cf_est,
                    "status": "EVIDENCE (environment-dependent)" if ident and not cf_est else ("EVIDENCE (environment-robust)" if ident and cf_est else "SPECIMEN (replay failed)")})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--counterfactuals", type=int, default=8); a = ap.parse_args(argv)
    ws = load(); unb = [r for r in ws if r.get("lane", "").startswith("unbiased")]; ada = [r for r in ws if r.get("lane") == "adaptive"]
    w0 = [r for r in ws if r.get("lane") == "unbiased_wave0"]
    sp_u = specimens(unb, "unbiased"); sp_a = specimens(ada, "adaptive")
    res = {"schema": "archaeon.rie.results.v1", "worlds": len(ws), "unbiased_worlds": len(unb), "adaptive_worlds": len(ada), "wave0_worlds": len(w0),
           "exposure_ok_all": all(r["exposure_ok"] for r in ws), "arrivals_total": sum(r["arrivals"] for r in ws),
           "tier1_unbiased_rates": rates(unb), "tier3_causal_wave0": causal(w0),
           "tier2_adaptive_specimen_count": Counter(t for s in sp_a for t in s["tags"]), "tier1_unbiased_specimen_count": Counter(t for s in sp_u for t in s["tags"]),
           "specimens_unbiased": sp_u[:300], "specimens_adaptive": sp_a[:300]}
    res["tier4_counterfactuals"] = counterfactuals(sp_u + sp_a, a.counterfactuals) if a.counterfactuals else []
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: res[k] for k in ("worlds", "unbiased_worlds", "adaptive_worlds", "exposure_ok_all")}, default=str)); return 0


if __name__ == "__main__":
    sys.exit(main())
