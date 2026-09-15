"""Clause B scoring (backlog S1): graft vs BOTH cheats, paired per run seed, Holm across worlds.

Contract clause B: a representation evolved in Domain A PASSES if, grafted into Domain B without
modification, it accelerates learning or inference. E-T1 showed graft - scratch false-alarms
through a distribution-equal cheat (w3, n=8), so E-T1b's protocol reads a graft against its cheats:

  acceleration   per run seed: d_cheat = held_auc(graft) - held_auc(cheat), cheat in
                 {rand_graft (same shape, fresh init), shuffle_graft (donor values permuted)}
  test           one-sided exact sign-flip p over 2^n flips (identical to E's transfer.signflip_p)
  per world      p_max = max over the two cheats; the graft must beat both
  family         Holm step-down across the (donor -> recipient) pairs at alpha
  gates          every run seed has all three conditions; the graft slot bytes are unmodified
                 and fused == numpy; the oracle rows are clean (world honest 0 failing, skip_lin
                 >= 14/16; brain honest 0 mismatched, cheat >= 14/16); the planted positive
                 (self_graft) beats both cheats at alpha. A failed gate is INDETERMINATE, never FAIL.

Verdict per pair: PASS (Holm rejects, gates clean), FAIL (gates clean, not rejected),
INDETERMINATE. The verdict reads rows only (per-run-seed rows; summary rows are used only to
cross-check that the re-derived p equals the harness's).

    python -m primordial.ops.qd_ledger check-b --rows primordial/ledger/rows/E/E-T1b-transfer-harness-vs-cheats.jsonl

v2 (E-R5-1, preregistered bus 1789467311525-0): rows stamped control_version clauseB_ctrl_v2_featperm are read
against CONTROLS_V2 = (scratch, sham) -- equal-budget scratch and the observation-feature-permuted donor. v1's
rand_graft lost to scratch at w13 train128 (E-R4-1), so beating it proved nothing. v2 gates: paired seeds, graft
integrity, sham integrity (sham_integrity.ok on every run seed), oracles clean. The planted positive/negative are
separate preregistered validation experiments, not an in-pair gate. v1 rows keep the v1 rule unchanged.
"""
from __future__ import annotations

import itertools
import json
import pathlib

import numpy as np

CHEATS = ("rand_graft", "shuffle_graft")
CONDITIONS = ("graft", "self_graft") + CHEATS
CONTROL_V2 = "clauseB_ctrl_v2_featperm"
CONTROLS_V2 = ("scratch", "sham")
CONDITIONS_V2 = ("graft",) + CONTROLS_V2
ALPHA = 0.05
CHEAT_BAR = 14
METRIC = "held_auc"


def signflip_p(d) -> float:
    """One-sided exact paired permutation p for mean(d) > 0 (same computation as E's harness)."""
    d = np.asarray(d, float)
    obs = d.mean()
    flips = np.array(list(itertools.product((1.0, -1.0), repeat=len(d))))
    return float(((flips * np.abs(d)).mean(1) >= obs - 1e-12).mean())


def holm(pvals: dict, alpha: float = ALPHA) -> dict:
    """-> {key: {"p_adj", "reject"}}; step-down, adjusted p monotone and capped at 1."""
    order = sorted(pvals, key=lambda k: (pvals[k], str(k)))
    m, run, out, stop = len(order), 0.0, {}, False
    for i, k in enumerate(order):
        run = max(run, min(1.0, (m - i) * pvals[k]))
        stop = stop or pvals[k] > alpha / (m - i)
        out[k] = {"p_adj": run, "reject": not stop}
    return out


def _oracle_problems(row: dict) -> list[str]:
    need = (("world_oracle_honest", "elites_failing", "==", 0), ("world_oracle_skip_lin", "elites_failing", ">=", CHEAT_BAR),
            ("brain_oracle_honest", "mismatched_rows", "==", 0), ("brain_oracle_cheat", "elites_mismatching", ">=", CHEAT_BAR))
    bad = []
    for block, key, op, bar in need:
        v = (row.get(block) or {}).get(key)
        ok = v is not None and (v == bar if op == "==" else v >= bar)
        if not ok:
            bad.append(f"{block}.{key}={v} (need {op} {bar})")
    return bad


def pairs_from_rows(rows: list[dict]) -> dict:
    """(exp_id, family, donor, recipient) -> {condition: {run_seed: row}} plus the summary row, if any.
    Keyed by exp_id so two experiments over the same world pair never merge."""
    out: dict = {}
    for r in rows:
        key = (r.get("exp_id") or "", r.get("family"), r.get("donor_world"), r.get("recipient_world"))
        if None in key[1:]:
            continue
        g = out.setdefault(key, {"by_cond": {}, "summary": None, "control_version": None})
        if r.get("control_version"):
            g["control_version"] = g["control_version"] or r["control_version"]
            if g["control_version"] != r["control_version"]:
                g["mixed_control_versions"] = True
        if r.get("condition") == "summary":
            g["summary"] = r
        elif r.get("condition") in CONDITIONS + ("scratch", "sham") and r.get("run_seed") is not None:
            g["by_cond"].setdefault(r["condition"], {})[r["run_seed"]] = r
    return out


def evaluate_pair_v2(g: dict, alpha: float = ALPHA, metric: str = METRIC) -> dict:
    """clauseB_ctrl_v2_featperm: the graft must beat BOTH equal-budget scratch and the feature-permuted sham."""
    bc = g["by_cond"]
    problems = []
    if g.get("mixed_control_versions"):
        problems.append("rows of this pair carry more than one control_version")
    seeds = sorted(set.intersection(*(set(bc.get(c, {})) for c in CONDITIONS_V2))) if all(c in bc for c in CONDITIONS_V2) else []
    for c in CONDITIONS_V2:
        extra = set(bc.get(c, {})) - set(seeds)
        if c not in bc:
            problems.append(f"no {c} rows")
        elif extra:
            problems.append(f"{c} has unpaired run seeds {sorted(extra)}")
    res: dict = {"run_seeds": seeds, "n": len(seeds), "control_version": CONTROL_V2}
    if len(seeds) < 2:
        return dict(res, verdict="INDETERMINATE", problems=problems or ["fewer than 2 paired run seeds"])
    col = lambda c: np.array([bc[c][s][metric] for s in seeds], float)
    for other in CONTROLS_V2:
        d = col("graft") - col(other)
        res[f"graft_vs_{other}_diff_mean"] = float(d.mean())
        res[f"graft_vs_{other}_p"] = signflip_p(d)
    res["graft_p_max"] = max(res[f"graft_vs_{c}_p"] for c in CONTROLS_V2)
    d = col("sham") - col("scratch")
    res["sham_vs_scratch_diff_mean"], res["sham_below_scratch_p"] = float(d.mean()), signflip_p(-d)
    grafts = [bc["graft"][s] for s in seeds]
    if not all(r.get("graft_bytes_unmodified") is True and r.get("graft_fused_eq_numpy") is True for r in grafts):
        problems.append("graft integrity (bytes unmodified and fused == numpy) not true on every run seed")
    bad_sham = [s for s in seeds if (bc["sham"][s].get("sham_integrity") or {}).get("ok") is not True]
    if bad_sham:
        problems.append(f"sham integrity not ok on run seeds {bad_sham}")
    oracle_rows = [r for r in grafts if "world_oracle_honest" in r]
    if not oracle_rows:
        problems.append("no oracle row on the graft condition")
    for r in oracle_rows:
        problems += [f"run seed {r['run_seed']}: {p}" for p in _oracle_problems(r)]
    logged = (g.get("summary") or {}).get("graft_vs_controls_held_auc_p_max")
    if metric == "held_auc" and logged is not None:
        res["harness_graft_p_max"] = logged
        res["rederived_equals_harness"] = abs(logged - res["graft_p_max"]) < 1e-12
    res["problems"] = problems
    return res


def evaluate_pair(g: dict, alpha: float = ALPHA, metric: str = METRIC) -> dict:
    if g.get("control_version") == CONTROL_V2:
        return evaluate_pair_v2(g, alpha, metric)
    if g.get("control_version"):
        return {"run_seeds": [], "n": 0, "verdict": "INDETERMINATE",
                "problems": [f"unknown control_version {g['control_version']!r}"]}
    bc = g["by_cond"]
    problems = []
    seeds = sorted(set.intersection(*(set(bc.get(c, {})) for c in CONDITIONS))) if all(c in bc for c in CONDITIONS) else []
    for c in CONDITIONS:
        extra = set(bc.get(c, {})) - set(seeds)
        if c not in bc:
            problems.append(f"no {c} rows")
        elif extra:
            problems.append(f"{c} has unpaired run seeds {sorted(extra)}")
    res: dict = {"run_seeds": seeds, "n": len(seeds)}
    if len(seeds) < 2:
        return dict(res, verdict="INDETERMINATE", problems=problems or ["fewer than 2 paired run seeds"])
    col = lambda c: np.array([bc[c][s][metric] for s in seeds], float)
    for c in ("graft", "self_graft"):
        for cheat in CHEATS:
            d = col(c) - col(cheat)
            res[f"{c}_vs_{cheat}_diff_mean"] = float(d.mean())
            res[f"{c}_vs_{cheat}_p"] = signflip_p(d)
        res[f"{c}_p_max"] = max(res[f"{c}_vs_{cheat}_p"] for cheat in CHEATS)
    grafts = list(bc["graft"].values())
    if not all(r.get("graft_bytes_unmodified") is True and r.get("graft_fused_eq_numpy") is True for r in grafts):
        problems.append("graft integrity (bytes unmodified and fused == numpy) not true on every run seed")
    oracle_rows = [r for r in grafts if "world_oracle_honest" in r]
    if not oracle_rows:
        problems.append("no oracle row on the graft condition")
    for r in oracle_rows:
        problems += [f"run seed {r['run_seed']}: {p}" for p in _oracle_problems(r)]
    if res["self_graft_p_max"] >= alpha:
        problems.append(f"planted positive not detected: self_graft p_max {res['self_graft_p_max']:.4g} >= {alpha}")
    s = g.get("summary") or {}
    logged = (s.get("graft") or {}).get("vs_cheats_held_auc_p_max")
    if metric == "held_auc" and logged is not None:
        res["harness_graft_p_max"] = logged
        res["rederived_equals_harness"] = abs(logged - res["graft_p_max"]) < 1e-12
    res["problems"] = problems
    return res


def check_b(rows: list[dict], alpha: float = ALPHA, metric: str = METRIC) -> dict:
    per = {k: evaluate_pair(g, alpha, metric) for k, g in pairs_from_rows(rows).items()}
    adj, families = {}, {}
    for exp in sorted({k[0] for k in per}):                       # Holm across worlds WITHIN one experiment
        eligible = {k: v["graft_p_max"] for k, v in per.items()
                    if k[0] == exp and not v["problems"] and "graft_p_max" in v}
        families[exp] = len(eligible)
        if eligible:
            adj.update(holm(eligible, alpha))
    table = []
    for k, v in sorted(per.items(), key=lambda kv: (kv[0][0], str(kv[0][1]), kv[0][3], kv[0][2])):
        exp, fam, donor, rec = k
        if k in adj:
            v["holm_p_adj"], v["verdict"] = adj[k]["p_adj"], "PASS" if adj[k]["reject"] else "FAIL"
        else:
            v.setdefault("verdict", "INDETERMINATE")
        table.append({"exp_id": exp, "pair": f"w{donor}->w{rec}", "family": fam, "control_version": v.get("control_version"), **v})
    return {"clause": "B", "metric": metric, "alpha": alpha, "holm_families": families, "pairs": table}


def load_rows(paths) -> list[dict]:
    out = []
    for p in paths:
        for line in pathlib.Path(p).read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if isinstance(r, dict):
                out.append(r)
    return out
