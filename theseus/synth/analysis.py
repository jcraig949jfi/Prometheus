"""v0 ANALYSIS: every number the preregistration names, computed mechanically.

Arms (viable candidates only unless stated):
  D  recursive ecology, DEEP + VERY_DEEP lanes (no raw-human parent)
  E  recursive ecology, DEEP_LENS lane (deep + an evolved lens parent)
  S  SHALLOW lane, G  G0 lane (ecology)
  P / B / C  one-shot G0 pairs / triplets / sextuplets (fixed-depth controls)
  A  LLM semantic synthesis (fresh agent, spec + tuples only)
  R  random programs complexity-matched to D
  W  deliberately weird random programs; X execution-neutral programs;
  HK known mechanisms hidden behind synthetic names.

Hard test (H1): does D occupy behavioural niches not reached by A, B, C, R?
Decision rule (PREREG s4): equal-n subsamples (n = min viable count over
D, A, B, C, R; n >= 30 or INDETERMINATE).
  EX_g(D)  = cells of grid g occupied by D and by none of A, B, C, R
  perm p   = share of 1000 label permutations of the pooled equal-n set
             whose "D" label gets EX >= observed
  O_m(X)   = median over x in X of the min distance (metric m) to the union
             of the other four arms of {D, A, B, C, R}
  PASS  if >= 2 of 3 grids have p < 0.05 AND EX(D) > EX(R), AND >= 2 of 3
        metrics have O(D) - O(R) > 0 with bootstrap 95% CI above 0
  FAIL  if >= 2 of 3 grids have EX(D) <= median permutation null, OR
        >= 2 of 3 metrics have O(D) - O(R) < 0 with CI below 0
  INDETERMINATE otherwise
"""

from __future__ import annotations

import numpy as np

from . import battery as bt
from . import entities as en
from . import rulers as ru

N_PERM = 1000
N_BOOT = 200
MIN_N = 30
CMP = ("A", "B", "C", "R")


def _viable(table, arm):
    return [r for r in table.get(arm, []) if r["viable"]]


def _F(rows):
    return np.array([r["fp"] for r in rows]) if rows else np.zeros((0, bt.FP_DIM))


def _cells(cal, F, grid):
    return cal.cells(F, grid) if len(F) else []


def _ex(cells_by_arm, target, others):
    own = set(cells_by_arm[target])
    rest = set()
    for o in others:
        rest |= set(cells_by_arm[o])
    return len(own - rest)


def _O(cal, F_target, F_rest, metric):
    if not len(F_target) or not len(F_rest):
        return None
    D = ru.dist_matrix(F_target, F_rest, metric, cal)
    return float(np.median(D.min(1)))


def _wilson(k, n):
    if n == 0:
        return [None, None]
    z = 1.96
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return [round(float(c - h), 4), round(float(c + h), 4)]


def hard_test(table, cal, rng):
    arms = ("D",) + CMP
    V = {a: _viable(table, a) for a in arms}
    counts = {a: len(V[a]) for a in arms}
    n = min(counts.values())
    out = {"viable_counts": counts, "n_equal": n, "eligible": n >= MIN_N}
    if n < MIN_N:
        out["verdict"] = "INDETERMINATE"
        out["reason"] = f"n_equal {n} < {MIN_N}"
        return out
    sub = {a: [V[a][i] for i in rng.choice(len(V[a]), size=n, replace=False)] for a in arms}
    Fs = {a: _F(sub[a]) for a in arms}
    grids = {}
    for g in ru.GRIDS:
        cells = {a: _cells(cal, Fs[a], g) for a in arms}
        ex = {a: _ex(cells, a, [o for o in arms if o != a]) for a in arms}
        exD = _ex(cells, "D", CMP)
        pooled = [c for a in arms for c in cells[a]]
        null = []
        for _ in range(N_PERM):
            perm = rng.permutation(len(pooled))
            lab = {a: [pooled[i] for i in perm[j * n:(j + 1) * n]] for j, a in enumerate(arms)}
            null.append(_ex(lab, "D", CMP))
        null = np.array(null)
        grids[g] = {"EX_D_vs_ABCR": exD, "EX_each_vs_rest": ex, "perm_p": float((null >= exD).mean()),
                    "null_median": float(np.median(null)), "null_p95": float(np.percentile(null, 95)),
                    "occupied": {a: len(set(cells[a])) for a in arms}}
    metrics = {}
    for m in ru.METRICS:
        O = {a: _O(cal, Fs[a], np.vstack([Fs[o] for o in arms if o != a]), m) for a in arms}
        diffs = []
        for _ in range(N_BOOT):
            bs = {a: Fs[a][rng.choice(n, size=n, replace=True)] for a in arms}
            oD = _O(cal, bs["D"], np.vstack([bs[o] for o in arms if o != "D"]), m)
            oR = _O(cal, bs["R"], np.vstack([bs[o] for o in arms if o != "R"]), m)
            diffs.append(oD - oR)
        metrics[m] = {"O": O, "O_D_minus_O_R": O["D"] - O["R"],
                      "boot_ci95": [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))]}
    out["grids"] = grids
    out["metrics"] = metrics
    g_pass = sum(1 for g in grids.values() if g["perm_p"] < 0.05 and g["EX_D_vs_ABCR"] > g["EX_each_vs_rest"]["R"])
    m_pass = sum(1 for v in metrics.values() if v["boot_ci95"][0] > 0)
    g_fail = sum(1 for g in grids.values() if g["EX_D_vs_ABCR"] <= g["null_median"])
    m_fail = sum(1 for v in metrics.values() if v["boot_ci95"][1] < 0)
    if g_pass >= 2 and m_pass >= 2:
        verdict = "PASS"
    elif g_fail >= 2 or m_fail >= 2:
        verdict = "FAIL"
    else:
        verdict = "INDETERMINATE"
    out.update({"grids_pass": g_pass, "metrics_pass": m_pass, "grids_fail": g_fail, "metrics_fail": m_fail,
                "verdict": verdict})
    return out


def arity_oneshot(table, cal, rng):
    arms = ("P", "B", "C")
    rows = {}
    for a in arms:
        allr = table.get(a, [])
        v = _viable(table, a)
        rows[a] = {"n": len(allr), "viable": len(v), "viable_frac": (len(v) / len(allr)) if allr else None,
                   "viable_ci95": _wilson(len(v), len(allr))}
    n = min(r["viable"] for r in rows.values())
    if n >= 10:
        sub = {a: _F([_viable(table, a)[i] for i in rng.choice(rows[a]["viable"], size=n, replace=False)]) for a in arms}
        for g in ru.GRIDS:
            cells = {a: _cells(cal, sub[a], g) for a in arms}
            for a in arms:
                rows[a].setdefault("EX_vs_other_oneshot", {})[g] = _ex(cells, a, [o for o in arms if o != a])
                rows[a].setdefault("occupied", {})[g] = len(set(cells[a]))
        for m in ru.METRICS:
            for a in arms:
                rows[a].setdefault("O", {})[m] = _O(cal, sub[a], np.vstack([sub[o] for o in arms if o != a]), m)
    return {"n_equal": n, "arms": rows}


def depth_vs_arity(reg, evals, collisions, table, cal):
    """Distance of each viable ecology child to the one-shot union (P+B+C): a
    time-independent reference, unlike birth-time archive novelty."""
    ref = _F(_viable(table, "P") + _viable(table, "B") + _viable(table, "C"))
    rows = []
    for c in collisions:
        i = c["child"]
        if not evals[i]["viable"]:
            continue
        rows.append({"id": i, "lane": c["lane"], "arity": c["arity"], "gen": c["gen"],
                     "min_depth": reg.min_depth_to_g0(i), "generation": reg[i]["generation"]})
    if not rows or not len(ref):
        return {"n": len(rows)}
    F = _F([{"fp": evals[r["id"]]["fp"]} for r in rows])
    d = {m: ru.dist_matrix(F, ref, m, cal).min(1) for m in ru.METRICS}
    for j, r in enumerate(rows):
        for m in ru.METRICS:
            r[f"d_oneshot_{m}"] = float(d[m][j])
    cellsum = {}
    for r in rows:
        key = f"{r['lane']}|k{r['arity']}"
        s = cellsum.setdefault(key, {"n": 0, **{m: [] for m in ru.METRICS}})
        s["n"] += 1
        for m in ru.METRICS:
            s[m].append(r[f"d_oneshot_{m}"])
    for key, s in cellsum.items():
        for m in ru.METRICS:
            s[m] = float(np.median(s[m])) if s[m] else None
    by_arity = {}
    for k in sorted({r["arity"] for r in rows}):
        rr = [r for r in rows if r["arity"] == k]
        by_arity[k] = {"n": len(rr), **{m: float(np.median([r[f"d_oneshot_{m}"] for r in rr])) for m in ru.METRICS}}
    gen_ok = [r for r in rows if r["generation"] is not None]
    rho = {}
    for m in ru.METRICS:
        x = np.array([r["generation"] for r in gen_ok], float)
        y = np.array([r[f"d_oneshot_{m}"] for r in gen_ok])
        rho[m] = _spearman(x, y)
    return {"n": len(rows), "by_lane_arity": cellsum, "by_arity": by_arity, "spearman_generation_vs_d_oneshot": rho,
            "rows": rows}


def _spearman(x, y):
    if len(x) < 3 or x.std() == 0 or y.std() == 0:
        return None
    rx = np.argsort(np.argsort(x))
    ry = np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def lineage_shuffle(dva, rng):
    rows = dva.get("rows") or []
    if len(rows) < 10:
        return {"n": len(rows)}
    x = np.array([r["generation"] for r in rows], float)
    y = np.array([r["d_oneshot_euclid_z"] for r in rows])
    obs = _spearman(x, y)
    null = [_spearman(rng.permutation(x), y) for _ in range(N_PERM)]
    null = np.array([v for v in null if v is not None])
    return {"n": len(rows), "rho_obs": obs, "null_p95_abs": float(np.percentile(np.abs(null), 95)),
            "perm_p_two_sided": float((np.abs(null) >= abs(obs)).mean()) if obs is not None else None}


def behaviour_shuffle(table, cal, rng):
    arms = ("D",) + CMP
    V = {a: _viable(table, a) for a in arms}
    n = min(len(v) for v in V.values())
    if n < 10:
        return {"n": n}
    sub = {a: _F([V[a][i] for i in rng.choice(len(V[a]), size=n, replace=False)]) for a in arms}
    pooled = np.vstack([sub[a] for a in arms])
    shuf = pooled.copy()
    for j in range(shuf.shape[1]):
        shuf[:, j] = shuf[rng.permutation(len(shuf)), j]
    out = {}
    for g in ru.GRIDS:
        real = {a: _cells(cal, sub[a], g) for a in arms}
        sh = {a: _cells(cal, shuf[i * n:(i + 1) * n], g) for i, a in enumerate(arms)}
        out[g] = {"EX_D_real": _ex(real, "D", CMP), "EX_D_shuffled_dims": _ex(sh, "D", CMP),
                  "occupied_real_total": len(set(c for a in arms for c in real[a])),
                  "occupied_shuffled_total": len(set(c for a in arms for c in sh[a]))}
    return out


def law_depth(g):
    return len({r["prov"].split("|")[0] for r in g["rules"] if str(r.get("prov", "")).startswith("law:")})


def lineage_integrity(reg, collisions):
    col_of = {c["child"]: c["cid"] for c in collisions}
    bad_anc, bad_law, checked = 0, 0, 0
    for e in reg.values():
        if e["origin"] != "synthetic" or e.get("kind") != "mechanism":
            continue
        checked += 1
        anc = set()
        stack = list(e.get("parentIds", []))
        while stack:
            p = stack.pop()
            if p in anc:
                continue
            anc.add(p)
            stack += reg[p].get("parentIds", [])
        if sorted(anc) != e["ancestry"]:
            bad_anc += 1
        own = {col_of.get(e["id"])} | {col_of.get(a) for a in anc}
        for r in e["executableRepresentation"]["rules"]:
            pv = str(r.get("prov", ""))
            for part in pv.split("|"):
                if part.startswith("law:") and part[4:] not in own:
                    bad_law += 1
                if part.startswith("x:") and part.split(":")[1] not in own:
                    bad_law += 1
    return {"checked": checked, "ancestry_mismatch": bad_anc, "foreign_provenance": bad_law}


def genealogy_summary(reg, n_g0, lanes):
    out = {}
    for lane in lanes:
        es = [e for e in reg.values() if e.get("lane") == lane and e.get("kind") == "mechanism"]
        if not es:
            continue
        gs = [reg.genealogy(e["id"], n_g0) for e in es]
        md = [g["min_depth_to_g0"] for g in gs if g["min_depth_to_g0"] is not None]
        out[lane] = {
            "n": len(es),
            "generation_pct": np.percentile([g["generation"] for g in gs], [0, 25, 50, 75, 100]).tolist(),
            "min_depth_to_g0_pct": np.percentile(md, [0, 25, 50, 75, 100]).tolist() if md else None,
            "mean_ancestry_depth_mean": float(np.mean([g["mean_ancestry_depth"] for g in gs])),
            "raw_human_rule_frac_mean": float(np.mean([g["raw_human_rule_frac"] for g in gs])),
            "parent_synth_frac_mean": float(np.mean([g["parent_synth_frac"] for g in gs])),
            "direct_human_parent_frac": float(np.mean([g["has_direct_human_parent"] for g in gs])),
            "grandparents_all_synth_frac": float(np.mean([g["grandparents_synth"] for g in gs])),
            "ancestral_diversity_mean": float(np.mean([g["ancestral_diversity"] for g in gs])),
            "law_depth_pct": np.percentile([law_depth(e["executableRepresentation"]) for e in es], [0, 50, 100]).tolist(),
        }
    return out


def strongest(reg, evals, table, cal, repro_rows, cand_rows, marg_rows, n_g0):
    """Candidates meeting several independent properties, in precise language."""
    ref_arms = ("A", "B", "C", "P", "R", "G0")
    ref = _F([r for a in ref_arms for r in _viable(table, a)])
    rep = {x["id"]: x for x in repro_rows}
    cand = {x["id"]: x for x in cand_rows}
    marg = {x["id"]: x for x in marg_rows}
    out = []
    for arm in ("D", "E"):
        for r in _viable(table, arm):
            i = r["id"]
            if i not in rep:
                continue
            g = reg.genealogy(i, n_g0)
            cells = {gname: cal.cells(np.asarray(r["fp"]), gname)[0] for gname in ru.GRIDS}
            ref_cells = {gname: set(cal.cells(ref, gname)) for gname in ru.GRIDS}
            empty_in = [gname for gname in ru.GRIDS if cells[gname] not in ref_cells[gname]]
            dmin = {m: float(ru.dist_matrix(np.asarray(r["fp"])[None], ref, m, cal).min()) for m in ru.METRICS}
            out.append({
                "id": i, "arm": arm, "state": reg[i]["state"],
                "no_direct_raw_human_parent": not g["has_direct_human_parent"],
                "min_ancestry_depth_to_g0": g["min_depth_to_g0"], "generation": g["generation"],
                "raw_human_rule_frac": g["raw_human_rule_frac"],
                "niche_cells_absent_from_controls": empty_in,
                "niche_distance_to_controls": dmin, "tau_rep": cal.tau_rep,
                "mechanistic": rep[i]["verdict"], "best_known_dist": rep[i]["best_dist"],
                "best_known_family": rep[i]["best_family"],
                "replicates": cand.get(i, {}).get("replicates"), "transfer_score": cand.get(i, {}).get("transfer_score"),
                "twin_viable": cand.get(i, {}).get("twin_viable"),
                "lens_dependencies": reg[i].get("lensDependencies", []),
                "lens_best_drop": marg.get(i, {}).get("best_drop"),
                "interpretation": "not attempted (v0: interpretation comes after survival)",
            })
    out.sort(key=lambda x: (-len(x["niche_cells_absent_from_controls"]), -x["niche_distance_to_controls"]["euclid_z"]))
    return out


def analyse(reg, evals, table, collisions, pop_hist, cal, repro_rows, cand_rows, marg_rows, lens_rows,
            llm_rejected, n_g0, rng, archive):
    out = {}
    out["hard_test"] = hard_test(table, cal, rng)
    out["arity_oneshot"] = arity_oneshot(table, cal, rng)
    dva = depth_vs_arity(reg, evals, collisions, table, cal)
    out["depth_vs_arity"] = {k: v for k, v in dva.items() if k != "rows"}
    out["controls"] = {
        "lineage_shuffle": lineage_shuffle(dva, rng),
        "behaviour_shuffle": behaviour_shuffle(table, cal, rng),
        "execution_neutral": {"n": len(table.get("X", [])), "viable": len(_viable(table, "X")),
                              "fail_reasons": _reasons(table.get("X", []))},
        "weird_random": {"n": len(table.get("W", [])), "viable": len(_viable(table, "W")),
                         "fail_reasons": _reasons(table.get("W", []))},
        "random_matched": {"n": len(table.get("R", [])), "viable": len(_viable(table, "R")),
                           "fail_reasons": _reasons(table.get("R", []))},
        "hidden_known": _hk(repro_rows),
        "rule_destroyed_twins": {"n": len(cand_rows), "twin_viable": sum(1 for x in cand_rows if x["twin_viable"]),
                                 "twin_dist_over_tau_median": float(np.median([x["twin_dist"] / cal.tau_rep for x in cand_rows]))
                                 if cand_rows else None},
        "lineage_integrity": lineage_integrity(reg, collisions),
        "law_depth_oneshot_max": {a: max([law_depth(r["genome"]) for r in table.get(a, [])] or [0]) for a in ("P", "B", "C")},
        "llm_arm": {"n_valid": len(table.get("A", [])), "rejected": llm_rejected,
                    "viable": len(_viable(table, "A"))},
    }
    out["genealogy"] = genealogy_summary(reg, n_g0, ["G0", "SHALLOW", "DEEP", "VERY_DEEP", "DEEP_LENS"])
    out["mechanistic"] = {}
    for arm in sorted({x["arm"] for x in repro_rows}):
        rs = [x for x in repro_rows if x["arm"] == arm]
        out["mechanistic"][arm] = {v: sum(1 for x in rs if x["verdict"] == v) for v in
                                   ("REPRODUCED_BY_KNOWN", "PARTIALLY_REPRODUCED", "NOT_REPRODUCED_YET")}
        out["mechanistic"][arm]["median_best_dist_over_tau"] = float(np.median([x["best_dist"] / cal.tau_rep for x in rs]))
    lens_adm = [x for x in lens_rows if x.get("admitted")]
    lm = {}
    for arm in ("D", "E", "R", "B"):
        rs = [x for x in marg_rows if x["arm"] == arm and x.get("best_drop") is not None]
        from . import dark as dk
        lm[arm] = {"n": len(rs), "lens_dependent": sum(1 for x in rs if x["best_drop"] >= dk.ADMIT_DROP),
                   "median_best_drop": float(np.median([x["best_drop"] for x in rs])) if rs else None}
    out["lens"] = {"dark_objects": sum(1 for i in evals if (evals[i].get("dark") or {}).get("dark")),
                   "dark_objects_ecology": sum(1 for c in collisions if (evals[c["child"]].get("dark") or {}).get("dark")),
                   "lens_attempts": len(lens_rows), "lens_admitted": len(lens_adm), "lens_marginal": lm,
                   "resolved": [{"dark_object": x["dark_object"], "lens": x["lens_id"], "drop": x["drop"],
                                 "null_p95": x["null_p95_drop"]} for x in lens_adm]}
    states = {}
    for e in reg.values():
        states[e["state"]] = states.get(e["state"], 0) + 1
    out["states"] = states
    out["population_final"] = pop_hist[-1] if pop_hist else None
    out["niche_occupancy_final"] = archive.occupancy()
    out["new_niche_count_by_gen"] = [{"gen": p["gen"], **p["archive_occupancy"]} for p in pop_hist]
    out["strongest"] = strongest(reg, evals, table, cal, repro_rows, cand_rows, marg_rows, n_g0)[:15]
    out["predictions"] = score_predictions(out)
    out["verdicts"] = {"H1_hard_test": out["hard_test"]["verdict"],
                       "controls_valid": {"hidden_known_gate": out["controls"]["hidden_known"]["gate"],
                                          "execution_neutral_gate": out["controls"]["execution_neutral"]["viable"] <=
                                          0.05 * max(1, out["controls"]["execution_neutral"]["n"]),
                                          "lineage_integrity": out["controls"]["lineage_integrity"]["ancestry_mismatch"] == 0
                                          and out["controls"]["lineage_integrity"]["foreign_provenance"] == 0}}
    return out


def _reasons(rows):
    c = {}
    for r in rows:
        if r["viable"]:
            continue
        for k in ("deterministic", "stable", "nontrivial", "lifetime", "transforms", "responsive", "replicable"):
            if r["viability"].get(k) is False:
                c[k] = c.get(k, 0) + 1
    return c


def _hk(repro_rows):
    rs = [x for x in repro_rows if x["arm"] == "HK"]
    ok = sum(1 for x in rs if x["verdict"] in ("REPRODUCED_BY_KNOWN", "PARTIALLY_REPRODUCED"))
    return {"n": len(rs), "reproduced_or_partial": ok, "gate": (ok >= 0.8 * len(rs)) if rs else None,
            "by_verdict": {v: sum(1 for x in rs if x["verdict"] == v) for v in
                           ("REPRODUCED_BY_KNOWN", "PARTIALLY_REPRODUCED", "NOT_REPRODUCED_YET")}}


def score_predictions(out):
    """Preregistered predictions (PREREG s5), scored mechanically. RIGHT/WRONG/UNSCORABLE."""
    P = []

    def add(pid, text, val):
        P.append({"id": pid, "prediction": text, "outcome": val})

    h = out["hard_test"]
    add("P1", "H1 hard test is FAIL or INDETERMINATE (the thesis is not supported at v0 scale)",
        "UNSCORABLE" if h["verdict"] is None else ("RIGHT" if h["verdict"] in ("FAIL", "INDETERMINATE") else "WRONG"))
    ar = out["arity_oneshot"]["arms"]
    vf = [ar[a]["viable_frac"] for a in ("P", "B", "C")]
    add("P2", "one-shot viable fraction strictly decreases with arity: pairs > triplets > sextuplets",
        "UNSCORABLE" if None in vf else ("RIGHT" if vf[0] > vf[1] > vf[2] else "WRONG"))
    c = out["controls"]
    rv = c["random_matched"]["viable"] / max(1, c["random_matched"]["n"])
    add("P3", "complexity-matched random programs have a lower viable fraction than one-shot triplets",
        "UNSCORABLE" if vf[1] is None else ("RIGHT" if rv < vf[1] else "WRONG"))
    g = out["genealogy"].get("DEEP")
    add("P4", "DEEP-lane children carry on average < 0.2 of their rules unchanged from G0",
        "UNSCORABLE" if not g else ("RIGHT" if g["raw_human_rule_frac_mean"] < 0.2 else "WRONG"))
    add("P5", "at least one lens is admitted against an ecology dark object",
        "RIGHT" if out["lens"]["lens_admitted"] >= 1 else "WRONG")
    lm = out["lens"]["lens_marginal"]
    if lm["E"]["n"] and lm["D"]["n"]:
        e_, d_ = lm["E"]["lens_dependent"] / lm["E"]["n"], lm["D"]["lens_dependent"] / lm["D"]["n"]
        add("P6", "E-lane (deep + evolved lens parent) candidates are lens-dependent more often than D-lane",
            "RIGHT" if e_ > d_ else "WRONG")
    else:
        add("P6", "E-lane candidates are lens-dependent more often than D-lane", "UNSCORABLE")
    add("P7", "hidden-known control passes (>= 80% reproduced or partial)",
        "UNSCORABLE" if c["hidden_known"]["gate"] is None else ("RIGHT" if c["hidden_known"]["gate"] else "WRONG"))
    m = out["mechanistic"].get("D")
    add("P8", ">= 50% of the top D candidates are NOT_REPRODUCED_YET by the v0 known library",
        "UNSCORABLE" if not m else ("RIGHT" if m["NOT_REPRODUCED_YET"] >= 0.5 * sum(m[v] for v in
                                    ("REPRODUCED_BY_KNOWN", "PARTIALLY_REPRODUCED", "NOT_REPRODUCED_YET")) else "WRONG"))
    rho = out["depth_vs_arity"].get("spearman_generation_vs_d_oneshot", {}).get("euclid_z")
    add("P9", "among viable ecology children, generation correlates positively with distance to the one-shot union (Spearman > 0.1)",
        "UNSCORABLE" if rho is None else ("RIGHT" if rho > 0.1 else "WRONG"))
    return P


def render(out, tag):
    """Plain-text report (pure ASCII)."""
    L = [f"# Theseus {tag} -- report", "",
         "Generated by theseus.synth.analysis.render from REPORT.json; numbers only, no interpretation.", ""]
    h = out["hard_test"]
    L += ["## H1 hard test (D vs A, B, C, R; equal n)", "",
          f"verdict: {h['verdict']}   viable counts: {h['viable_counts']}   n_equal: {h['n_equal']}", ""]
    for g, v in (h.get("grids") or {}).items():
        L.append(f"  grid {g:5s} EX(D)={v['EX_D_vs_ABCR']:4d}  perm p={v['perm_p']:.3f}  null median={v['null_median']:.1f}"
                 f"  EX each={v['EX_each_vs_rest']}")
    for m, v in (h.get("metrics") or {}).items():
        L.append(f"  metric {m:11s} O={ {k: (round(x, 3) if x is not None else None) for k, x in v['O'].items()} }"
                 f"  O(D)-O(R)={v['O_D_minus_O_R']:.3f} CI95={[round(x, 3) for x in v['boot_ci95']]}")
    L += ["", "## Arity (one-shot G0 collisions)", ""]
    for a, v in out["arity_oneshot"]["arms"].items():
        L.append(f"  {a}: {v}")
    L += ["", "## Depth vs arity (ecology; median distance to one-shot union)", ""]
    for k, v in sorted((out["depth_vs_arity"].get("by_lane_arity") or {}).items()):
        L.append(f"  {k:16s} {v}")
    L.append(f"  by arity: {out['depth_vs_arity'].get('by_arity')}")
    L.append(f"  spearman(generation, d_oneshot): {out['depth_vs_arity'].get('spearman_generation_vs_d_oneshot')}")
    L += ["", "## Genealogy by lane", ""]
    for k, v in out["genealogy"].items():
        L.append(f"  {k}: {v}")
    L += ["", "## Mechanistic reproduction", ""]
    for k, v in out["mechanistic"].items():
        L.append(f"  {k}: {v}")
    L += ["", "## Lens loop", "", f"  {out['lens']}", "", "## Controls", ""]
    for k, v in out["controls"].items():
        L.append(f"  {k}: {v}")
    L += ["", "## States", "", f"  {out['states']}", "", "## Strongest candidates (precise language)", ""]
    for s in out["strongest"]:
        L.append(f"  {s}")
    L += ["", "## Predictions", ""]
    for p in out["predictions"]:
        L.append(f"  {p['id']} {p['outcome']:11s} {p['prediction']}")
    L += ["", "## Compute", "", f"  {out.get('compute')}", ""]
    txt = "\n".join(L) + "\n"
    return txt.encode("ascii", "replace").decode("ascii")
