"""COPIER-CENSUS-01 stage 2 + report + world-level prediction. Definitions are frozen in PREREG.json before the census runs.

    python -m archaeon.z80atlas.census.report --characterize --workers 22
    python -m archaeon.z80atlas.census.report --report
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.z80atlas.census import copier_census as C
from archaeon.z80atlas.denovo.run_denovo import clopper_pearson

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"                                                       # gitignored chunk outputs
STRATA = {"vmcopy32": ("vmcopy", 32), "z80_32": ("z80", 32), "vmcopy64": ("vmcopy", 64), "z80_64": ("z80", 64)}
STAGE2_CAP = 3000
FOUNDERS_PER_WORLD = C.FROZEN["N"] * C.FROZEN["init_fill_pct"] / 100.0      # expected random founders in a random-init world
READINGS = {"LOTTERY_CONSISTENT": "0.05 <= lambda <= 20: one surviving world is what an initial-founder lottery predicts",
            "LOTTERY_INSUFFICIENT": "lambda < 0.05: the initial-tape prior cannot account for the survivor (look at mutation-born or neighbour-dependent copying)",
            "SURVIVAL_LIMITED": "lambda > 20: copier founders were common; survival, not supply, is the bottleneck"}


def load_hits(stratum: str):
    counts = Counter(); n = 0; hits = []; in_read = 0
    for p in sorted((RUNS / stratum).glob("chunk_*.json")):
        c = json.loads(p.read_text(encoding="utf-8")); n += c["n"]; counts.update(c["counts"]); hits += c["hits"]; in_read += c["in_read"]
    return n, counts, hits, in_read


def _char(args):
    h, substrate = args
    return h["tape"], C.characterize(h, substrate)


def characterize(workers: int) -> int:
    for s, (sub, G) in STRATA.items():
        n, counts, hits, _ = load_hits(s)
        if not n: continue
        pick = hits if len(hits) <= STAGE2_CAP else random.Random("stage2:" + s).sample(hits, STAGE2_CAP)
        out = {}
        with ProcessPoolExecutor(workers) as ex:
            for fu in as_completed([ex.submit(_char, (h, sub)) for h in pick]):
                t, r = fu.result(); out[t] = r
        (RUNS / s / "STAGE2.json").write_text(json.dumps({"n_hits": len(hits), "characterized": len(out), "results": out}) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps({"stratum": s, "hits": len(hits), "characterized": len(out)}), flush=True)
    return 0


def campaign_worlds():
    """Random-init endogenous campaign worlds without inserted material, by (substrate, genome, input regime)."""
    from archaeon.z80atlas.postcampaign import adjudicate as A
    runs, _, _ = A.load_runs(Path(A.DEFAULT_HIST)); endo = ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "CONSTRUCTIVE", "PAIR_EXECUTION")
    w = Counter(); surv = Counter()
    for r in runs.values():
        fv = r["factor_vector"]
        if r["status"] == "DONE" and fv["init"] == "random" and fv["reproduction"] in endo and ":transplant:" not in r["scheduler_reason"]:
            k = "%s%d|%s" % (fv["representation.substrate"], fv["representation.genome"], "input0_only" if fv["task"] == "none" else "uniform_input")
            w[k] += 1; surv[k] += r["signals"]["extinct_epoch"] is None
    return w, surv


def report() -> int:
    pre = json.loads((HERE / "PREREG.json").read_text(encoding="utf-8"))
    strata = {}
    for s, (sub, G) in STRATA.items():
        n, counts, hits, in_read = load_hits(s)
        if not n: continue
        st2p = RUNS / s / "STAGE2.json"; st2 = json.loads(st2p.read_text(encoding="utf-8"))["results"] if st2p.exists() else {}
        exact_any = sum(counts.get(c, 0) for c in ("EXACT_UNGATED", "EXACT_GATED")); exact_x0 = sum(1 for h in hits if 0 in h["exact_inputs"])
        gate_hist = Counter(h["n_exact_inputs"] for h in hits if h["n_exact_inputs"])
        arch = Counter(C.architecture(h) for h in hits); arch_exact = Counter(C.architecture(h) for h in hits if h["n_exact_inputs"])
        sp = next((h for h in hits if h["tape"] == C.SPECIMEN), None)
        s2 = [st2[h["tape"]] for h in hits if h["tape"] in st2]
        def s2m(key, cls=None):
            v = [st2[h["tape"]][key] for h in hits if h["tape"] in st2 and (cls is None or h["class"] == cls)]
            return round(sum(v) / len(v), 4) if v else None
        strata[s] = {"substrate": sub, "G": G, "tapes": n, "counts": {c: counts.get(c, 0) for c in C.CLASSES},
                     "density": {c: {"k": counts.get(c, 0), "p": counts.get(c, 0) / n, "ci95": clopper_pearson(counts.get(c, 0), n)} for c in C.CLASSES},
                     "exact_capable": {"k": exact_any, "p": exact_any / n, "ci95": clopper_pearson(exact_any, n)},
                     "exact_at_input0": {"k": exact_x0, "p": exact_x0 / n, "ci95": clopper_pearson(exact_x0, n)},
                     "frac_tapes_reading_input": round(in_read / n, 4),
                     "gating_hist_n_exact_inputs": dict(sorted(gate_hist.items())), "gated_share_of_exact": round(sum(v for k, v in gate_hist.items() if k < 256) / exact_any, 4) if exact_any else None,
                     "architectures_all_hits": dict(arch.most_common()), "architectures_exact": dict(arch_exact.most_common()),
                     "stage2": {"characterized": len(s2), "offspring_heritable": sum(x["offspring_heritable"] for x in s2),
                                "mean_frac_keep_any_exact_EXACT_GATED": s2m("frac_keep_any_exact", "EXACT_GATED"), "mean_frac_keep_any_exact_EXACT_UNGATED": s2m("frac_keep_any_exact", "EXACT_UNGATED"),
                                "mean_frac_keep_any_birth": s2m("frac_keep_any_birth"), "occupied_nbr_any_exact": sum(x["occupied_nbr_exact"] > 0 for x in s2),
                                "mean_essential_positions_exact": round(sum(len(x["essential_positions"]) for x in s2 if x["essential_positions"] is not None) / max(1, sum(1 for h in hits if h["n_exact_inputs"] and h["tape"] in st2)), 2)},
                     "specimen_found_in_census": sp is not None,
                     "steps_exact_median": sorted(h["steps"] for h in hits if h["n_exact_inputs"])[len([h for h in hits if h["n_exact_inputs"]]) // 2] if exact_any else None}
    worlds, surv = campaign_worlds(); lam = 0.0; lam_lo = 0.0; lam_hi = 0.0; per = {}
    for k, nw in worlds.items():
        s, regime = k.split("|")
        if s not in strata: per[k] = {"worlds": nw, "survived": surv[k], "note": "stratum not censused"}; continue
        d = strata[s]["exact_at_input0" if regime == "input0_only" else "exact_capable"]
        f = lambda p: nw * (1 - (1 - p) ** FOUNDERS_PER_WORLD)
        per[k] = {"worlds": nw, "survived": surv[k], "p": d["p"], "lambda": f(d["p"]), "lambda_ci": [f(d["ci95"][0]), f(d["ci95"][1])]}
        lam += f(d["p"]); lam_lo += f(d["ci95"][0]); lam_hi += f(d["ci95"][1])
    reading = "LOTTERY_INSUFFICIENT" if lam < 0.05 else ("SURVIVAL_LIMITED" if lam > 20 else "LOTTERY_CONSISTENT")
    res = {"schema": "archaeon.z80atlas.copier_census.results.v1", "prereg_sha256": C.hashlib.sha256((HERE / "PREREG.json").read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
           "strata": strata, "prediction": {"founders_per_world": FOUNDERS_PER_WORLD, "by_world_class": per, "lambda_worlds_with_exact_copier_founder": lam,
                                            "lambda_ci_from_density_ci": [lam_lo, lam_hi], "observed_surviving_worlds": sum(surv.values()),
                                            "reading": reading, "readings": READINGS}}
    (HERE / "RESULTS.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({s: {"tapes": v["tapes"], "exact": v["exact_capable"]["k"], "near": v["counts"]["NEAR_COPIER"], "span": v["counts"]["SPAN_COPIER"]} for s, v in strata.items()}))
    print(json.dumps({"lambda": lam, "ci": [lam_lo, lam_hi], "reading": reading}))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--characterize", action="store_true"); ap.add_argument("--report", action="store_true"); ap.add_argument("--workers", type=int, default=22)
    a = ap.parse_args(argv)
    if a.characterize: return characterize(a.workers)
    if a.report: return report()
    ap.print_help(); return 1


if __name__ == "__main__":
    sys.exit(main())
