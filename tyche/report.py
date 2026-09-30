"""Campaign report for Tyche v0: the charter's REQUIRED REPORT fields plus
the preregistered verdicts H1-H6 (roles/Tyche/prereg/2026-09-30_v0/PREREG.md),
computed in code from the run directory. Frozen with the preregistration.

Usage: python -m tyche.report <run_dir>
"""

from __future__ import annotations

import collections
import json
import os
import sys

NEG = ("tsd", "prf")


def jl(path):
    if not os.path.exists(path):
        return []
    return [json.loads(x) for x in open(path, encoding="ascii") if x.strip()]


def main(run):
    cfg = json.load(open(os.path.join(run, "CONFIG.json")))
    specs = json.load(open(os.path.join(run, "WORLDS.json")))
    by = {s["id"]: s for s in specs}
    A = json.load(open(os.path.join(run, "PASS_A_BASELINE.json")))
    D = json.load(open(os.path.join(run, "PASS_D_AUDITS.json")))
    gens = jl(os.path.join(run, "GENERATIONS.jsonl"))
    adm = jl(os.path.join(run, "ADMISSIONS.jsonl"))
    res = jl(os.path.join(run, "RESIDUALS.jsonl"))
    gene = [r for r in jl(os.path.join(run, "GENEALOGY.jsonl")) if r.get("event") == "birth"]
    fos = jl(os.path.join(run, "FOSSILS.jsonl"))
    rows = D["admitted"]
    train = [s["id"] for s in specs if s["role"] == "train"]
    held = [s["id"] for s in specs if s["role"] == "heldout"]

    def resid(tag, w, r="R0", split="val"):
        for x in res:
            if x["tag"] == tag and x["world"] == w:
                return x.get(f"{r}|{split}|resid_err_frac")
        return None

    epochs = sorted({x["tag"] for x in res if x["tag"].startswith("epoch")})

    # ---------------- H5 instrument
    cheat_ok = D["cheat_control"]["instrument_ok"]
    caus_all = all(r["causality"]["pass"] for r in rows)
    H5 = "PASS" if (cheat_ok and caus_all) else "FAIL"

    # ---------------- H1 planted positive controls
    planted = [w for w in train if by[w]["kind"] == "planted"]
    h1 = {}
    for w in planted:
        ib = A["initial_population_best"][w]
        if ib.get("test_gain", 0) >= 0.03:
            h1[w] = {"state": "VOID_INITIAL_ACCESS", "init_test_gain": ib.get("test_gain")}
            continue
        twin = [s["id"] for s in specs if s["kind"] == "tsd" and s["law_group"] == by[w]["law_group"]
                and s["role"] == "train"]
        solved = []
        for r in rows:
            if r["home"] != w:
                continue
            ok = (r["home_test"][0] >= 0.10 and r["replicated"] and r["beats_null"]
                  and r["causality"]["pass"])
            if twin:
                t = r["transfer"].get(twin[0], {})
                ok = ok and t.get("z", 0) < 3.0
            if ok:
                solved.append(r["id"])
        h1[w] = {"state": "SOLVED" if solved else "NOT_SOLVED", "lenses": solved,
                 "init_test_gain": ib.get("test_gain")}
    valid = [w for w in h1 if h1[w]["state"] != "VOID_INITIAL_ACCESS"]
    n_solved = sum(h1[w]["state"] == "SOLVED" for w in valid)
    if len(valid) >= 4 and n_solved >= 4:
        H1 = "PASS"
    elif n_solved <= 1:
        H1 = "FAIL"
    else:
        H1 = "INDETERMINATE"

    # ---------------- H2 false gradients
    fg = collections.defaultdict(list)
    for r in rows:
        for w in r["false_gradient_worlds"]:
            fg[w].append(r["id"])
        if by[r["home"]]["kind"] in NEG and r["replicated"] and r["beats_null"]:
            fg[r["home"]].append(r["id"])
    adm_neg = [x for x in adm if x["admitted"] and by[x["world"]]["kind"] in NEG]
    H2 = "PASS" if len(fg) == 0 else ("INDETERMINATE" if len(fg) == 1 else "FAIL")

    # ---------------- H3 residual shift
    first = epochs[0] if epochs else None
    h3 = {}
    for w in planted:
        if h1[w]["state"] != "SOLVED":
            continue
        r0 = [x for x in rows if x["id"] in h1[w]["lenses"]][0]["ruler"]
        a0, a1 = resid(first, w, r0), resid("final", w, r0)
        h3[w] = {"ruler": r0, "err_frac_start": a0, "err_frac_final": a1,
                 "rel_drop": (a0 - a1) / a0 if a0 else None}
    negw = [w for w in train if by[w]["kind"] in NEG]
    h3n = {w: {"err_frac_start": resid(first, w), "err_frac_final": resid("final", w)} for w in negw}
    ok_p = all(v["rel_drop"] is not None and v["rel_drop"] >= 0.5 for v in h3.values()) and h3
    within = [abs(v["err_frac_final"] - v["err_frac_start"]) <= 0.03 for v in h3n.values()
              if v["err_frac_start"] is not None]
    ok_n = within and sum(within) / len(within) >= 0.8
    H3 = "PASS" if (ok_p and ok_n) else ("INDETERMINATE" if not h3 else "FAIL")

    # ---------------- H4 redundancy on known worlds
    known = [w for w in train if by[w]["kind"] == "known"]
    b0 = A["baseline_eco0"]
    saturated = {(w, o) for w in known for o in ("lin", "tree", "tab")
                 if b0[w].get(f"R0|{o}|val", 0) >= 0.95}
    h4_viol = [x for x in adm if x["admitted"] and x["ruler"] == "R0" and (x["world"], x["org"]) in saturated]
    H4 = "PASS" if not h4_viol else "FAIL"

    # ---------------- H6 end to end
    good_later = []
    for r in rows:
        ep = r["admission"]["epoch"]
        if ep < 1 or not (r["replicated"] and r["beats_null"] and r["causality"]["pass"]):
            continue
        a0 = resid(first, r["home"], r["ruler"])
        ae = resid(f"epoch{ep}_start", r["home"], r["ruler"])
        if a0 is not None and ae is not None and a0 - ae >= 0.01:
            good_later.append(r["id"])
    H6 = "PASS" if (H1 == "PASS" and H2 == "PASS" and H5 == "PASS" and good_later) else (
        "FAIL" if H5 == "FAIL" or H1 == "FAIL" or H2 == "FAIL" else "INDETERMINATE")

    # ---------------- descriptive fields
    roots_final = set()
    last = gens[-1] if gens else {}
    born = {g["id"]: g for g in gene}
    dark_anc = [r["id"] for r in rows if r["dark_ancestors"]]
    fam_rows = collections.defaultdict(list)
    for r in rows:
        fam_rows[by[r["home"]]["family"]].append(r["id"])
    mut_counts = collections.Counter(op for g in gene for op in g["ops"])
    opaque = [r["id"] for r in rows if r["interpretation"] == "UNKNOWN" and r["replicated"] and r["beats_null"]]
    interp = [r["id"] for r in rows if r["interpretation"] != "UNKNOWN"]
    failed_roots = {f["root"] for f in fos} - {born[r["id"]]["root"] for r in rows if r["id"] in born}
    held_tr = {}
    for r in rows:
        for w in held:
            t = r["transfer"].get(w)
            if t and w in r.get("sig_transfer_worlds", []):
                held_tr.setdefault(w, []).append((r["id"], t["best_case"], round(t["gain"], 4)))
    near_chance = [w for w in train
                   if max(b0[w].get(f"R0|{o}|val", 0) for o in ("lin", "tree", "tab")) - b0[w]["majority|val"] < 0.02]
    open_anom = [r["id"] for r in rows if r["replicated"] and not r["beats_null"]]
    orgs = collections.Counter((by[r["home"]]["family"], r["org"]) for r in rows)

    out = {
        "run": run, "config": cfg["config"], "worlds_hash": cfg["worlds_hash"],
        "verdicts": {"H1_planted": H1, "H2_false_gradient": H2, "H3_residual_shift": H3,
                     "H4_redundancy": H4, "H5_instrument": H5, "H6_end_to_end": H6},
        "H1_detail": h1, "H2_false_gradient_worlds": dict(fg), "H2_admissions_on_negative_worlds":
            [(x["world"], x["id"], round(x["conf_gain"], 4), round(x["conf_z"], 2)) for x in adm_neg],
        "H3_planted": h3, "H3_negative": h3n, "H4_violations": h4_viol, "H6_later_generation_lenses": good_later,
        "WORLD_FAMILY": sorted({s["family"] for s in specs}),
        "INITIAL_PERFORMANCE": {w: {k: v for k, v in b0[w].items() if "|val" in k and "resid" not in k}
                                for w in train + held},
        "INITIAL_RESIDUAL": {w: {r: resid(first, w, r) for r in ("R0", "R2")} for w in train},
        "LENS_POPULATION_SIZE": cfg["config"]["N"], "LENSES_BORN": len(gene),
        "MUTATION_OPERATORS": dict(mut_counts),
        "SURVIVING_LINEAGES": last.get("roots_alive"),
        "DARK_ECOLOGY_LINEAGES": {"reserve_size": last.get("dark"), "lenses_ever_in_reserve":
                                  None},
        "MARGINAL_GAINS": [{"id": r["id"], "home": r["home"], "case": f"{r['ruler']}|{r['org']}",
                            "conf": round(r["admission"]["conf_gain"], 4), "test": round(r["home_test"][0], 4),
                            "reps": [round(x[0], 4) for x in r["home_reps"]], "null_p95": round(r["null"]["p95"], 4),
                            "replicated": r["replicated"], "beats_null": r["beats_null"],
                            "sensor": r["sensor_class"], "eff_len": r["eff_len"], "len": r["len"],
                            "epoch": r["admission"]["epoch"], "interpretation": r["interpretation"]}
                           for r in rows],
        "HELD_OUT_PERFORMANCE": held_tr,
        "TRANSFER_PERFORMANCE": {r["id"]: {"class": r["sensor_class"], "worlds": r.get("sig_transfer_worlds", [])}
                                 for r in rows},
        "SHORTCUT_AUDITS": {"cheat_control": D["cheat_control"], "causality_all_pass": caus_all,
                            "n_admission_tests": D["n_admission_tests"]},
        "FALSIFICATIONS": {"not_replicated": [r["id"] for r in rows if not r["replicated"]],
                           "replicated_but_within_null": open_anom,
                           "false_gradients": dict(fg)},
        "OPAQUE_SUCCESSFUL_LENSES": opaque,
        "INTERPRETABLE_SUCCESSFUL_LENSES": interp,
        "RESIDUAL_AFTER_EVOLUTION": {w: {r: resid("final", w, r) for r in ("R0", "R2")} for w in train},
        "REVIVED_LINEAGES": dark_anc,
        "FAILED_LINEAGES_COUNT": len(failed_roots),
        "OPEN_ANOMALIES": open_anom,
        "NEAR_CHANCE_WORLDS_AT_START": near_chance,
        "ADMITTED_BY_FAMILY": dict(fam_rows),
        "LENS_X_ORGANISM": {f"{k[0]}|{k[1]}": v for k, v in orgs.items()},
    }
    out["DARK_ECOLOGY_LINEAGES"]["lenses_ever_in_reserve"] = len({f["id"] for f in fos if f.get("dark_gens", 0) > 0})
    json.dump(out, open(os.path.join(run, "REPORT.json"), "w"), indent=1, sort_keys=True)
    print(json.dumps(out["verdicts"], indent=1))
    return out


if __name__ == "__main__":
    main(sys.argv[1])
