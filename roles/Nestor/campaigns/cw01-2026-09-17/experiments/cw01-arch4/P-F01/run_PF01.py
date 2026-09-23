"""P-F01 [T-X15, deformation A]: SINGLE-COORDINATE MANIPULATIONS of length, executable structure and
carried state, each under fixed-k and fraction-matched damage; plus the persistent-words census along
orig-rule walks. Predictions preregistered (see PREREG). Computational scope: integer programs on a
bounded VM.
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common as CM            # noqa: E402
import manip as MP             # noqa: E402
A, L = CM.A, CM.L
sys.path.insert(0, str(HERE.parent / "P-D01"))
sys.path.insert(0, str(HERE.parent / "P-E05"))
from run_PD01 import c408_tops   # noqa: E402
from run_PE05 import walk as walk64   # noqa: E402

PID, TID = "P-F01", "T-X15"
CELLS = [("delete", "k", 4, 1), ("delete", "f", 0.15, 1), ("operand", "k", 4, 1), ("operand", "f", 0.15, 1)]
VARIANTS = ("original", "pad", "duplicate", "persist_none")


def job(j):
    p = j["program"]
    env = p["env"]
    eps = A.episodes(env)
    pm = A.canonical(p["manifest"])
    out = {"pid": p["organism_id"], "set": p["stratum"], "variants": {}}
    for v in VARIANTS:
        m = {"original": pm, "pad": MP.pad(pm), "duplicate": MP.duplicate(pm), "persist_none": MP.persist_none(pm)}[v]
        if m is None:
            out["variants"][v] = {"feasible": False}
            continue
        try:
            ident = MP.identical(m, pm, eps)
        except A.ManifestError as e:
            out["variants"][v] = {"feasible": False, "why": str(e)[:80]}
            continue
        r = MP.assay(m, env, eps, CELLS, "%s|%s" % (p["organism_id"], v))
        r.update({"feasible": True, "identical": ident})
        out["variants"][v] = r
    return out


def census_job(j):
    p = j["parent"]
    env = p["env"]
    eps = {k: A.episodes(k) for k in A.ENVS}
    pm = A.canonical(p["manifest"])
    rows = []
    for w in (1, 2):
        wk = walk64(pm, p["organism_id"], w, eps[env], "orig", "frozen")
        for dd, m in sorted(wk["archived"].items()):
            r = MP.assay(m, env, eps[env], [("delete", "k", 4, 1), ("delete", "f", 0.15, 1)], "%s|census|%d|%d" % (p["organism_id"], w, dd))
            if r.get("degenerate"):
                continue
            rows.append({"pid": p["organism_id"], "walker": w, "depth": dd, "n_instr": r["n_instr"], "persistent_words": r["persistent_words"],
                         "loss_k4": r["cells"]["delete|k4|s1"]["loss"], "loss_f15": r["cells"]["delete|f0.15|s1"]["loss"]})
    return rows


def main():
    t0 = time.time()
    ph = L.prereg(HERE, {"perturbation_id": PID, "parent": TID, "deformation": "A", "scope": CM.SCOPE, "claim_type": "causal-separation",
                         "manipulations": {"pad": "append NOP instructions to double length (identity CHECKED on the base episodes)", "duplicate": "append a copy of the genome", "persist_none": "persist policy := none (measured against its own baseline)"},
                         "damage_cells": CELLS, "draws": 4, "programs": "viable parents, walker-16, C4-08 tops",
                         "predictions": {"DILUTION": "pad and duplicate lower fixed-k loss; neither changes fraction-matched loss",
                                         "REDUNDANCY": "duplicate lowers fraction-matched loss; pad does not",
                                         "CARRIED_STATE": "persist_none raises loss at fixed length; pad and duplicate move nothing",
                                         "BROKEN": "a pattern outside these three (e.g. pad changes fraction-matched loss; persist_none lowers loss)"},
                         "contrasts": "paired sign-flips per manipulation vs original, per cell, on programs where the manipulation is feasible (and, for pad, identity-preserving)",
                         "census": "orig-rule walks depth 64 (2 walkers x viable parents) archived 16/32/64: loss (k4, f.15) regressed on log length AND persistent words",
                         "material_rule": "any paired contrast outside its band, or the census regression assigns the depth effect to one covariate with the other inside its band",
                         "continuation": ["pad at random positions", "duplicate half", "persist regs/tape/all as a dose", "jump-topology census"],
                         "runtime": {"worktree": str(A.ARCH), "sha": A.ARCH_SHA}})
    parents = [p for p in CM.viable_parents() if not p["degenerate"]]
    programs = [dict(p, stratum="parent") for p in parents]
    for p in parents:
        wk = A.C5.walk(p["manifest"], p["organism_id"], 1, A.episodes(p["env"]), 16, 32)
        programs.append({"organism_id": p["organism_id"] + "/w1", "stratum": "walker16", "manifest": wk["archived"].get(wk["depth"]), "env": p["env"]})
    programs += c408_tops()
    with A.pool(8) as ex:
        rows = list(ex.map(job, [{"program": p} for p in programs]))
        census = [r for rs in ex.map(census_job, [{"parent": p} for p in parents]) for r in rs]
    # contrasts
    contrasts, feas = {}, {}
    for v in ("pad", "duplicate", "persist_none"):
        feas[v] = {"feasible": sum(1 for r in rows if r["variants"][v].get("feasible")), "identical": sum(1 for r in rows if r["variants"][v].get("identical")),
                   "degenerate": sum(1 for r in rows if r["variants"][v].get("feasible") and r["variants"][v].get("degenerate")), "n": len(rows)}
        for key in rows[0]["variants"]["original"]["cells"]:
            diffs, diffs_id = [], []
            for r in rows:
                o, x = r["variants"]["original"], r["variants"][v]
                if o.get("degenerate") or not x.get("feasible") or x.get("degenerate"):
                    continue
                lo, lx = o["cells"][key]["loss"], x["cells"].get(key, {}).get("loss")
                if lo is None or lx is None:
                    continue
                diffs.append(lx - lo)
                if x.get("identical"):
                    diffs_id.append(lx - lo)
            contrasts["%s|%s" % (v, key)] = {"all": CM.paired_signflip(diffs), "identity_preserving": CM.paired_signflip(diffs_id) if diffs_id else None}
    # census regression: loss ~ 1 + log n + persistent_words (standardised), per damage mode
    reg = {}
    if census:
        X = np.column_stack([np.ones(len(census)), np.log([c["n_instr"] for c in census]), [c["persistent_words"] for c in census]])
        X[:, 1] = (X[:, 1] - X[:, 1].mean()) / (X[:, 1].std() + 1e-9)
        X[:, 2] = (X[:, 2] - X[:, 2].mean()) / (X[:, 2].std() + 1e-9)
        for key in ("loss_k4", "loss_f15"):
            y = np.array([c[key] for c in census], float)
            ok = np.isfinite(y)
            b = np.linalg.lstsq(X[ok], y[ok], rcond=None)[0]
            # permutation band for each coefficient (2000 label shuffles)
            rng = np.random.Generator(np.random.PCG64(0))
            null = np.array([np.linalg.lstsq(X[ok], rng.permutation(y[ok]), rcond=None)[0] for _ in range(2000)])
            reg[key] = {"intercept": float(b[0]), "log_len_std": float(b[1]), "persistent_words_std": float(b[2]),
                        "log_len_band": [float(np.percentile(null[:, 1], 5)), float(np.percentile(null[:, 1], 95))],
                        "pw_band": [float(np.percentile(null[:, 2], 5)), float(np.percentile(null[:, 2], 95))], "n": int(ok.sum())}
        by_depth = {}
        for c in census:
            d = by_depth.setdefault(c["depth"], {"n": [], "pw": [], "k4": [], "f15": []})
            d["n"].append(c["n_instr"]); d["pw"].append(c["persistent_words"]); d["k4"].append(c["loss_k4"]); d["f15"].append(c["loss_f15"])
        by_depth = {str(k): {kk: float(np.nanmean(vv)) for kk, vv in v.items()} for k, v in sorted(by_depth.items())}
    else:
        by_depth = {}

    def sig(c):
        return bool(c and (c["above_p95"] or c["below_p05"]))
    # reading against the predictions (fixed-k delete and fraction delete)
    pad_k, pad_f = contrasts["pad|delete|k4|s1"]["identity_preserving"] or contrasts["pad|delete|k4|s1"]["all"], contrasts["pad|delete|f0.15|s1"]["identity_preserving"] or contrasts["pad|delete|f0.15|s1"]["all"]
    dup_k, dup_f = contrasts["duplicate|delete|k4|s1"]["all"], contrasts["duplicate|delete|f0.15|s1"]["all"]
    pn_k, pn_f = contrasts["persist_none|delete|k4|s1"]["all"], contrasts["persist_none|delete|f0.15|s1"]["all"]
    below = lambda c: bool(c and c["below_p05"])   # noqa: E731
    above = lambda c: bool(c and c["above_p95"])   # noqa: E731
    reading = []
    if below(pad_k) and below(dup_k) and not sig(pad_f) and not sig(dup_f):
        reading.append("DILUTION")
    if below(dup_f) and not sig(pad_f):
        reading.append("REDUNDANCY")
    if above(pn_k) or above(pn_f):
        reading.append("CARRIED_STATE")
    if sig(pad_f) or below(pn_k) or below(pn_f) or (above(pad_k) or above(dup_k)):
        reading.append("BROKEN")
    if not reading:
        reading.append("UNRESOLVED")
    material = bool(any(sig(c["all"]) for c in contrasts.values()) or any(not (r["log_len_band"][0] <= r["log_len_std"] <= r["log_len_band"][1]) or not (r["pw_band"][0] <= r["persistent_words_std"] <= r["pw_band"][1]) for r in reg.values()))
    out = {"perturbation_id": PID, "parent": TID, "reading": reading, "feasibility": feas, "contrasts": contrasts, "census_regression": reg, "census_by_depth": by_depth,
           "n_programs": len(rows), "n_census_rows": len(census), "material": material, "elapsed_s": round(time.time() - t0, 1)}
    L.result(HERE, out, ph)
    (HERE / "rows.json").write_text(json.dumps({"rows": rows, "census": census}, ensure_ascii=True, default=CM.js), encoding="utf-8")
    fmt = lambda c: (round(c["mean_diff"], 3), c["n"], c["above_p95"], c["below_p05"]) if c else None   # noqa: E731
    L.append_evidence(TID, PID, "single-coordinate manipulations: reading %s; pad(identity) k4 %s f15 %s; duplicate k4 %s f15 %s; persist_none k4 %s f15 %s; feasibility %s; census loss~log_len,pw: %s"
                      % (reading, fmt(pad_k), fmt(pad_f), fmt(dup_k), fmt(dup_f), fmt(pn_k), fmt(pn_f), feas,
                         {k: (round(v["log_len_std"], 3), v["log_len_band"], round(v["persistent_words_std"], 3), v["pw_band"]) for k, v in reg.items()}),
                      material, detail={"contrasts": {k: {kk: fmt(vv) for kk, vv in v.items()} for k, v in contrasts.items()}, "regression": reg, "by_depth": by_depth})
    print("DONE material=%s reading=%s (%.0f s) pad %s %s | dup %s %s | pn %s %s | feas %s | reg %s" % (material, reading, time.time() - t0, fmt(pad_k), fmt(pad_f), fmt(dup_k), fmt(dup_f), fmt(pn_k), fmt(pn_f), feas, {k: (round(v["log_len_std"], 3), round(v["persistent_words_std"], 3)) for k, v in reg.items()}))


if __name__ == "__main__":
    main()
