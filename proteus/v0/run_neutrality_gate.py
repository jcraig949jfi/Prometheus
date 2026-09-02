"""Neutrality gate runner (A6). Reads the frozen prereg, refuses a grammar it was not written for,
runs the no-selection walk, writes rows and a verdict. Never edits the prereg.

    python proteus/v0/run_neutrality_gate.py
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
HERE = os.path.dirname(os.path.abspath(__file__))

from proteus.foundry import grammar, lineage, generate  # noqa: E402
from proteus.foundry.affordances import N_OPCODES  # noqa: E402
from proteus.foundry.identity import RUNTIME_HASH, hash_obj  # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from  # noqa: E402
from proteus.foundry.vm import SCHEMA  # noqa: E402

IW = 4


def ols_slope(ys):
    n = len(ys)
    xs = range(n)
    mx = (n - 1) / 2.0
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den else 0.0


def cohort_series(lengths, fn):
    """lengths: list over lineages of list over generations. Return per-generation fn over lineages."""
    G = len(lengths[0])
    return [fn([L[g] for L in lengths]) for g in range(G)]


def bootstrap_slope(lengths, fn, lo, hi, n_resample, rng):
    S = len(lengths)
    vals = []
    for _ in range(n_resample):
        idx = [rng.randbelow(S) for _ in range(S)]
        sub = [lengths[i] for i in idx]
        vals.append(ols_slope(cohort_series(sub, fn)[lo:hi]))
    vals.sort()
    return vals[int(0.025 * n_resample)], vals[int(0.975 * n_resample) - 1]


def main():
    with open(os.path.join(HERE, "NEUTRALITY_PREREG.json"), encoding="utf-8") as f:
        pre = json.load(f)
    if pre["grammar_hash"] != grammar.GRAMMAR_HASH:
        print("REFUSED: prereg grammar_hash", pre["grammar_hash"][:12], "!= current", grammar.GRAMMAR_HASH[:12])
        return 2
    if pre["runtime_hash"] != RUNTIME_HASH:
        print("REFUSED: prereg runtime_hash differs from current runtime")
        return 2
    d = pre["design"]
    S, G = d["lineages_per_cohort"], d["generations"]
    root = SplitMix64(seed_from("proteus.neutrality.v0", pre["seed"], grammar.GRAMMAR_HASH))
    t0 = time.time()
    cohorts = {}
    pooled_added = pooled_removed = 0
    op_counts = {}
    opcode_hist_start = [0] * N_OPCODES
    opcode_hist_end = [0] * N_OPCODES
    for start in d["start_sizes"]:
        crng = root.derive("cohort", start)
        orgs = []
        for s in range(S):
            r = crng.derive("lineage", s)
            m = {"schema_version": SCHEMA, "n_regs": d["n_regs"], "tape_words": d["tape_words"],
                 "genome": [r.next_u32() for _ in range(IW * start)], "code_writable": d["code_writable"],
                 "persist": d["persist"], "tick_budget": d["tick_budget"], "out_cap": d["out_cap"]}
            orgs.append(generate.organism_record(m, None, 0))
            for i in range(0, len(m["genome"]), IW):
                opcode_hist_start[m["genome"][i] % N_OPCODES] += 1
        lengths = [[start] for _ in range(S)]
        caps = [[d["tape_words"] // IW] for _ in range(S)]
        for g in range(1, G + 1):
            new = []
            for s in range(S):
                mate_idx = (s + 1 + crng.randbelow(S - 1)) % S
                child, rec = lineage.descend(orgs[s], seed_from(pre["seed"], start, s, g), mate=orgs[mate_idx])
                for op in rec["operators"]:
                    op_counts[op["operator"]] = op_counts.get(op["operator"], 0) + 1
                    delta = op["len_after"] - op["len_before"]
                    if delta > 0:
                        pooled_added += delta
                    elif delta < 0:
                        pooled_removed += -delta
                new.append(child)
                lengths[s].append(len(child["manifest"]["genome"]) // IW)
                caps[s].append(child["manifest"]["tape_words"] // IW)
            orgs = new
        for o in orgs:
            g_ = o["manifest"]["genome"]
            for i in range(0, len(g_), IW):
                opcode_hist_end[g_[i] % IW * 0 + g_[i] % N_OPCODES] += 1
        mean_s = cohort_series(lengths, statistics.fmean)
        med_s = cohort_series(lengths, statistics.median)
        brng = crng.derive("bootstrap")
        pairs = sum(len(L) for L in lengths)
        min_occ = sum(1 for L in lengths for x in L if x == grammar.GMIN) / pairs
        max_occ = sum(1 for L, C in zip(lengths, caps) for x, c in zip(L, C) if x == c) / pairs
        half = G // 2
        res = {
            "start": start,
            "slope_mean": ols_slope(mean_s),
            "slope_mean_ci95": bootstrap_slope(lengths, statistics.fmean, 0, G + 1, d["bootstrap_resamples"], brng),
            "slope_median": ols_slope(med_s),
            "slope_median_ci95": bootstrap_slope(lengths, statistics.median, 0, G + 1, d["bootstrap_resamples"], brng),
            "slope_mean_last_half": ols_slope(mean_s[half:]),
            "slope_mean_last_half_ci95": bootstrap_slope(lengths, statistics.fmean, half, G + 1, d["bootstrap_resamples"], brng),
            "final_variance": statistics.pvariance([L[-1] for L in lengths]),
            "final_mean": mean_s[-1],
            "min_occupancy": min_occ,
            "max_occupancy": max_occ,
            "burnin_mean_ratio": statistics.fmean(mean_s[half:]) / start,
            "mean_series": mean_s,
            "median_series": med_s,
            "final_lengths": [L[-1] for L in lengths],
        }
        cohorts[str(start)] = res
        print(f"cohort {start:>4}: slope_mean {res['slope_mean']:+.4f} CI {res['slope_mean_ci95'][0]:+.4f}..{res['slope_mean_ci95'][1]:+.4f}"
              f"  median {res['slope_median']:+.4f}  last-half {res['slope_mean_last_half']:+.4f}"
              f"  ratio {res['burnin_mean_ratio']:.3f}  min_occ {min_occ:.3f} max_occ {max_occ:.3f} final_mean {res['final_mean']:.1f}")
    balance = pooled_added / pooled_removed if pooled_removed else float("inf")
    tol = pre["tolerances"]
    gates = {}
    for start, r in cohorts.items():
        gates[f"G1_ratchet_{start}"] = abs(r["slope_mean"]) <= tol["slope"] and abs(r["slope_median"]) <= tol["slope"]
        gates[f"G4_stationarity_{start}"] = abs(r["slope_mean_last_half"]) <= tol["slope"]
        gates[f"G3_max_occupancy_{start}"] = r["max_occupancy"] <= tol["occupancy"]
        if int(start) in pre["design"]["envelope_gated_starts"]:
            gates[f"G3_envelope_{start}"] = tol["ratio"][0] <= r["burnin_mean_ratio"] <= tol["ratio"][1]
            gates[f"G3_min_occupancy_{start}"] = r["min_occupancy"] <= tol["occupancy"]
    gates["G2_balance"] = tol["balance"][0] <= balance <= tol["balance"][1]
    verdict = "PASS" if all(gates.values()) else "FAIL"
    # tolerance vs measurement error, reported not gated
    se_note = {}
    for start, r in cohorts.items():
        hw = (r["slope_mean_ci95"][1] - r["slope_mean_ci95"][0]) / 2
        se_note[start] = {"ci_half_width": hw, "tolerance": tol["slope"], "tolerance_exceeds_half_width": tol["slope"] > hw}
    out = {
        "schema_version": "proteus.neutrality_result.v0",
        "prereg_hash": hash_obj(pre),
        "grammar_hash": grammar.GRAMMAR_HASH,
        "runtime_hash": RUNTIME_HASH,
        "wall_s": time.time() - t0,
        "cohorts": cohorts,
        "pooled": {"added": pooled_added, "removed": pooled_removed, "ins_del_balance": balance,
                   "operator_counts": dict(sorted(op_counts.items()))},
        "opcode_hist_start": opcode_hist_start,
        "opcode_hist_end": opcode_hist_end,
        "gates": gates,
        "tolerance_vs_error": se_note,
        "verdict": verdict,
    }
    with open(os.path.join(HERE, "NEUTRALITY_RESULT.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    print("balance", f"{balance:.3f}", "gates", {k: v for k, v in gates.items() if not v} or "all pass")
    print("VERDICT", verdict, f"({out['wall_s']:.1f}s)")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
