"""RA-1 DATA AUDIT. Reads only frozen HC-T01 rows. Computes NO scientific
statistic about accessibility and acquisition. Its purpose is to establish
whether the committed rows can support the preregistered analysis at all.

Run from the RA directory:
    python ra_audit.py
"""
import csv
import glob
import hashlib
import json
import os
import subprocess
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.dirname(os.path.dirname(HERE))
GRID = os.path.join(SPEC, "derived", "grid")

COLS = ("tag gen best mean md_on md_off nd_on nd_off mit_on mit_off mia_on "
        "mia_off miu_on miu_off af_on af_off glen nops ousage al_on al_off "
        "minlen geno").split()


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load():
    runs = {}
    for f in sorted(glob.glob(os.path.join(GRID, "*.csv"))):
        base = os.path.basename(f)[:-4]              # a<alpha>_b<beta>_s<seed>
        parts = base.split("_")
        a, b, s = parts[0][1:], parts[1][1:], int(parts[2][1:])
        rows = []
        for line in open(f, encoding="utf-8", errors="replace"):
            p = line.rstrip("\n").split(",", 22)
            if len(p) >= 22:
                rows.append(dict(zip(COLS, p)))
        runs[(a, b, s)] = rows
    return runs


def main():
    audit = {}
    audit["git_commit"] = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=SPEC, capture_output=True,
        text=True).stdout.strip()
    audit["prompt_sha256"] = sha256(os.path.join(
        HERE, "PROMPT_RA_CONDITIONAL_ACCESSIBILITY_2026-09-03.txt"))

    runs = load()
    audit["n_run_files"] = len(runs)
    arms = sorted(set((a, b) for (a, b, s) in runs))
    audit["arms"] = ["alpha=%s beta=%s" % (a, b) for a, b in arms]
    audit["runs_per_arm"] = {"alpha=%s beta=%s" % (a, b):
                             sum(1 for k in runs if k[0] == a and k[1] == b)
                             for a, b in arms}

    # generations present
    gensets = set(tuple(sorted(int(r["gen"]) for r in v)) for v in runs.values())
    audit["distinct_generation_vectors"] = len(gensets)
    gens = sorted(next(iter(gensets)))
    audit["generations"] = gens
    audit["n_checkpoints"] = len(gens)

    # missing / duplicated
    missing, dup = [], []
    for k, v in runs.items():
        g = [int(r["gen"]) for r in v]
        if sorted(g) != gens:
            missing.append(str(k))
        c = Counter(g)
        if any(n > 1 for n in c.values()):
            dup.append(str(k))
    audit["runs_with_nonstandard_generations"] = missing
    audit["runs_with_duplicate_generations"] = dup

    # pairing across beta arms at equal alpha and seed
    paired = defaultdict(list)
    for (a, b, s) in runs:
        paired[(a, s)].append(b)
    audit["seed_pairing"] = {
        "alpha_seed_cells": len(paired),
        "cells_with_both_beta_arms": sum(1 for v in paired.values()
                                         if set(v) == {"0.1", "0.0"}),
        "paired_across_arms": all(set(v) == {"0.1", "0.0"}
                                  for v in paired.values())}

    # conventions
    allbest = [float(r["best"]) for v in runs.values() for r in v]
    allmd = [float(r["md_on"]) for v in runs.values() for r in v]
    allnops = [float(r["nops"]) for v in runs.values() for r in v]
    audit["fitness_convention"] = {
        "column": "best",
        "min": min(allbest), "max": max(allbest),
        "direction": "HIGHER IS BETTER; 0.0 is the optimum (ceiling); values "
                     "are the negative fraction of mismatched target symbols",
        "ceiling_value": 0.0}
    audit["detector_convention"] = {
        "column": "md_on",
        "meaning": "modular degree under the beta_probe=0.1 frozen probe",
        "min": min(allmd), "max": max(allmd),
        "direction": "higher = more period-5-aligned correlated variation"}

    # nops distribution, per arm
    nops_by_arm = defaultdict(list)
    for (a, b, s), v in runs.items():
        for r in v:
            nops_by_arm["alpha=%s beta=%s" % (a, b)].append(float(r["nops"]))
    audit["nops_distribution"] = {}
    for k, v in nops_by_arm.items():
        v = sorted(v)
        audit["nops_distribution"][k] = {
            "n": len(v), "min": v[0], "max": v[-1],
            "median": v[len(v)//2],
            "frac_zero": sum(1 for x in v if x == 0.0)/len(v)}

    # ceiling occupancy per generation per arm
    ceil = {}
    for a, b in arms:
        key = "alpha=%s beta=%s" % (a, b)
        seeds = [s for (aa, bb, s) in runs if aa == a and bb == b]
        ceil[key] = {}
        for g in gens:
            vals = []
            for s in seeds:
                row = next(r for r in runs[(a, b, s)] if int(r["gen"]) == g)
                vals.append(float(row["best"]))
            ceil[key][str(g)] = {
                "n": len(vals),
                "frac_at_ceiling": sum(1 for x in vals if x == 0.0)/len(vals),
                "mean_best": sum(vals)/len(vals)}
    audit["ceiling_occupancy"] = ceil

    # horizon feasibility: for each (t, h) how many runs can still improve
    audit["horizon_feasibility"] = {}
    for a, b in arms:
        key = "alpha=%s beta=%s" % (a, b)
        seeds = [s for (aa, bb, s) in runs if aa == a and bb == b]
        audit["horizon_feasibility"][key] = {}
        for i, t in enumerate(gens):
            entry = {}
            for j in range(i+1, len(gens)):
                h = gens[j]
                gains, headroom = [], 0
                for s in seeds:
                    b0 = float(next(r for r in runs[(a, b, s)]
                                    if int(r["gen"]) == t)["best"])
                    b1 = float(next(r for r in runs[(a, b, s)]
                                    if int(r["gen"]) == h)["best"])
                    gains.append(b1 - b0)
                    if b0 < 0.0:
                        headroom += 1
                nz = sum(1 for x in gains if x != 0.0)
                entry[str(h)] = {
                    "n": len(gains),
                    "n_with_headroom_at_t": headroom,
                    "n_nonzero_gain": nz,
                    "frac_structural_zero": 1.0 - nz/len(gains),
                    "n_distinct_gain_values": len(set(round(x, 9)
                                                     for x in gains))}
            audit["horizon_feasibility"][key][str(t)] = entry

    # prior filtering in HC-T01
    ap = os.path.join(SPEC, "derived", "analyze.py")
    src = open(ap, encoding="utf-8").read() if os.path.exists(ap) else ""
    audit["hct01_prior_filtering"] = {
        "analyze_py_present": bool(src),
        "analyze_py_sha256": sha256(ap) if os.path.exists(ap) else None,
        "notes": ("HC-T01's own K7 test excluded nothing, but its reported "
                  "Spearman used gain over fixed windows 100->500 and 50->200 "
                  "within the beta=0.1 arm only, n=30 runs.")}

    # input hashes
    audit["input_hashes"] = {
        "n_grid_files": len(glob.glob(os.path.join(GRID, "*.csv"))),
        "grid_manifest_sha256": hashlib.sha256(
            "".join(sorted(
                os.path.basename(f) + ":" + sha256(f)
                for f in glob.glob(os.path.join(GRID, "*.csv"))
            )).encode()).hexdigest(),
        "frozen_config_sha256": sha256(os.path.join(
            SPEC, "HC_T01_FROZEN_CONFIG.json")),
        "noise_floor_sha256": sha256(os.path.join(
            SPEC, "derived", "noise_floor.json")),
    }

    out = os.path.join(HERE, "RA1_DATA_AUDIT.json")
    json.dump(audit, open(out, "w", encoding="utf-8"), indent=1)
    print("wrote", out)

    # human summary
    print("\nruns=%d  arms=%s  checkpoints=%d"
          % (audit["n_run_files"], audit["arms"], audit["n_checkpoints"]))
    print("paired across arms:", audit["seed_pairing"]["paired_across_arms"])
    print("nonstandard generations:", audit["runs_with_nonstandard_generations"])
    print("duplicate generations:", audit["runs_with_duplicate_generations"])
    print("\nnops by arm:")
    for k, v in audit["nops_distribution"].items():
        print("  %-22s min=%.1f med=%.1f max=%.1f fracZero=%.3f"
              % (k, v["min"], v["median"], v["max"], v["frac_zero"]))
    print("\nfraction AT CEILING (best == 0.0) by generation:")
    hdr = "  %-22s" % "arm" + "".join("%7d" % g for g in gens[:14])
    print(hdr)
    for k, v in ceil.items():
        print("  %-22s" % k + "".join("%7.2f" % v[str(g)]["frac_at_ceiling"]
                                      for g in gens[:14]))
    print("  ... (later generations in the JSON)")


if __name__ == "__main__":
    main()
