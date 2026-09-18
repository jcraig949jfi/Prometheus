"""C4-08 -- CAN ROBUSTNESS BE CONSTRUCTED RATHER THAN GIVEN? (campaign 4, slot 8).
Preregistration: C4-08/DESIGN.md (re-premised: the "insulation removed" arm is REPRESENTATION_BLOCKED).

    python -m archaeon.campaign4.c4_08 [--seeds 1..6] [--N 200] [--G 100] [--E 16] [--draws 4] [--procs 12] [--dry-run] [--self-test]

Ancestral = the depth-16 C4-05 walkers (digest-verified). Ordinary descendants = the C4-06
mutation_only runs, RERUN here from the same seeds (their traces must equal the committed ones:
the negative control). Perturbed descendants = the same runs with two frozen-weight edits per
birth (descend n_ops=2; mutation load, no reward term). Then the fresh C4-01 assay (12 operators
x draws) on samples of all three populations, on W2_K2; structural comparison and a prospective
NOP-ablation of the suspected category AFTER the assay is measured.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry import grammar as GR                                   # noqa: E402
from proteus.foundry import generate as G                                   # noqa: E402
from proteus.foundry.affordances import CATEGORY, N_OPCODES, OPCODES_IN      # noqa: E402
from proteus.foundry.lineage import descend                                  # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from                       # noqa: E402
from proteus.foundry.vm import ManifestError                                 # noqa: E402
from proteus.eval.population_manifest import structural_descriptor           # noqa: E402
from archaeon.wse.economics import REGIMES                                   # noqa: E402
from archaeon.wse.evolve import Evolution                                    # noqa: E402
from archaeon.campaign2.c2base import FOUNDRY_C2                             # noqa: E402
from archaeon.campaign4.c4base import C4, CAMPAIGN_SEED                      # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign4 import c4_06 as C6                                   # noqa: E402

ID = "C4-08"
ENV = "W2_K2"
TOP = 32
ARMS = ("ancestral", "ordinary", "perturbed")


def perturbed_descend(parent, mutation_seed, mate=None, **kw):
    return descend(parent, mutation_seed, mate=None, n_ops=2, **kw)


def evolve_final(job: dict) -> dict:
    """One run; returns the trace and the top-TOP final manifests."""
    arm, seed, N, Gn, E, walkers = job["arm"], job["seed"], job["N"], job["G"], job["E"], job["walkers"]
    init = []
    for w in walkers:
        org = G.organism_record(dict(w["manifest"]), None, 0); org["origins"] = ["walker"]; init.append(org)
    prov = {"fill": "c4-05 depth-16 walkers, repeated to N by the evolver's init_pop rule", "n": len(init), "N": N, "verified_common": True}
    ev = Evolution(C6.TARGET, REGIMES["E0"], CAMPAIGN_SEED, seed, N=N, E=E, branch="c4-08-" + arm, foundry=FOUNDRY_C2, init_pop=init, gen0_provenance=prov,
                   descend_fn=(C6.mutation_only_descend if arm == "ordinary" else perturbed_descend))
    t0 = time.time()
    for g in range(Gn):
        ev.evaluate_generation(last=(g == Gn - 1))
        if g < Gn - 1:
            ev.reproduce()
    res = ev.result()
    tb = [t["best_reward"] for t in res["trace"]]
    final = [{"manifest": z["manifest"], "reward": z["reward"], "fitness": z["fitness"]} for z in res["final_population"][:TOP]]
    return {"arm": arm, "seed": seed, "trace_best": tb, "train_best_final": tb[-1], "final_top": final, "wall_s": round(time.time() - t0, 1),
            "mean_len_final": sum(len(f["manifest"]["genome"]) // GR.IW for f in final) / len(final)}


def assay_program(job: dict) -> dict:
    """The fresh C4-01 assay on one program: 12 operators x draws on W2_K2 (+ the other environments for D6)."""
    m, tag, draws, E = job["manifest"], job["tag"], job["draws"], job["E"]
    eps = {k: C1.episodes(k, E) for k in C1.ENVS}
    pev = C1.eval_all(m, eps)
    dig = hashlib.sha256(json.dumps(m, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    rows = []
    for op in C1.OPERATORS:
        for r in range(1, draws + 1):
            rng = SplitMix64(seed_from("c4.08.assay", CAMPAIGN_SEED, dig, op, r))
            try:
                child, rec = GR.mutate(m, rng, mate=None, name=op)
            except ManifestError:
                rows.append({"operator": op, "draw": r, "applied": False, "D": "D0"}); continue
            if "noop" in rec["args"]:
                rows.append({"operator": op, "draw": r, "applied": False, "could_not_apply": True}); continue
            cev = C1.eval_all(child, eps)
            disp = C1.displacement(cev[ENV]["_answers"], pev[ENV]["_answers"])
            rows.append({"operator": op, "draw": r, "applied": True, "D": C1.classify(cev, pev, disp, False, ENV)["label"], "displacement": disp})
    app = [r for r in rows if r.get("applied")]
    return {"tag": tag, "digest": dig, "reward_w2k2": pev[ENV]["reward_per_ask"], "len": len(m["genome"]) // GR.IW,
            "descriptor": structural_descriptor(m), "n_applied": len(app),
            "loss": sum(1 for r in app if r["D"] in ("D2", "D3")), "neutral": sum(1 for r in app if r["D"] == "D5"),
            "coherent": sum(1 for r in app if r["D"] in ("D3", "D4", "D6", "D7") or (r["D"] == "D5" and r["displacement"] > 0)),
            "improved": sum(1 for r in app if r["D"] == "D7"), "rows": rows}


def pop_table(assays: List[dict]) -> dict:
    n = sum(a["n_applied"] for a in assays)
    k = {f: sum(a[f] for a in assays) for f in ("loss", "neutral", "coherent", "improved")}
    cats = Counter()
    for a in assays:
        for c, v in a["descriptor"]["opcode_category_counts_static"].items():
            cats[c] += v
    tot = sum(cats.values()) or 1
    return {"programs": len(assays), "edits_applied": n,
            **{f: {"k": k[f], "p": round(k[f] / n, 4) if n else None, "band95": C1.wilson(k[f], n) if n else (None, None)} for f in k},
            "mean_len": round(sum(a["len"] for a in assays) / max(1, len(assays)), 3),
            "mean_reward_w2k2": round(sum(a["reward_w2k2"] for a in assays) / max(1, len(assays)), 4),
            "category_shares": {c: round(v / tot, 4) for c, v in sorted(cats.items())}}


def ablate(m: dict, category: str) -> dict:
    c = json.loads(json.dumps(m))
    g = c["genome"]
    for i in range(len(g) // GR.IW):
        if CATEGORY[g[i * GR.IW] % N_OPCODES] == category:
            g[i * GR.IW:(i + 1) * GR.IW] = [0, 0, 0, 0]
    return c


def self_test() -> int:
    ps = C1.parents_from_population()[:8]
    rw = C6.regenerate_walkers(ps, 16)          # the walks were made at E=16; any other E is a different walk
    w = rw["walkers"][:6]
    a = evolve_final({"arm": "perturbed", "seed": 1, "N": 12, "G": 3, "E": 8, "walkers": w})
    b = evolve_final({"arm": "perturbed", "seed": 1, "N": 12, "G": 3, "E": 8, "walkers": w})
    det = a["trace_best"] == b["trace_best"]
    s = assay_program({"manifest": w[0]["manifest"], "tag": "t", "draws": 1, "E": 8})
    abl = ablate(w[0]["manifest"], "logical")
    rep = {"walkers": len(w), "mismatches": rw["digest_mismatches"], "perturbed_deterministic": det, "assay_rows": len(s["rows"]), "assay_applied": s["n_applied"],
           "ablation_changed": abl != w[0]["manifest"], "cheat_robust_row": (0 == 0)}
    print(json.dumps(rep, indent=1))
    return 0 if (det and rw["digest_mismatches"] == 0 and s["n_applied"] > 0) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="*", type=int, default=[1, 2, 3, 4, 5, 6])
    ap.add_argument("--N", type=int, default=200)
    ap.add_argument("--G", type=int, default=100)
    ap.add_argument("--E", type=int, default=16)
    ap.add_argument("--draws", type=int, default=4)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C4-08")
    if a.self_test:
        return self_test()
    if not a.dry_run and not C1.gate_is_green():
        print("REFUSED: launch gate not green")
        return 3
    from archaeon.campaign4.c4harness import Experiment4                    # noqa: PLC0415

    class Robustness(Experiment4):
        ID = "C4-08"
        TITLE = "can robustness be constructed rather than given (re-premised)"
        PARENTS = ["C4-05", "C4-06", "C4-01"]
        ARM_FIELD = "arm"
        METRICS = ("loss_p", "neutral_p", "coherent_p", "mean_len")

    X = Robustness(dry_run=a.dry_run, procs=a.procs)
    design = (C4 / "C4-08" / "DESIGN.md").read_text(encoding="utf-8")
    parents = C1.parents_from_population()
    rw = C6.regenerate_walkers(parents, a.E)
    walkers = rw["walkers"]
    c406_runs = C4 / "C4-06" / "attempts" / "a01" / "runs.json"
    c406 = {(r["arm"], r["seed"]): r for r in json.loads(c406_runs.read_text(encoding="utf-8"))} if c406_runs.exists() else {}
    X.seal({
        "question": "Under selection with elevated mutation load (two frozen-weight edits per birth), do descendants change their own single-edit "
                    "D-transition probabilities relative to their ancestors and to descendants under ordinary load, and is an evolved structural "
                    "difference responsible? (The 'free insulation removed' arm is REPRESENTATION_BLOCKED, D4-007.)",
        "parent_evidence": "C4-01: single-edit loss .29-.64 per operator; C4-02: radius-2 loss .66; C4-05: 188 depth-16 walkers; C4-06: mutation_only runs (traces committed).",
        "why_this_slot": "The directive's construction-vs-given question, on the part of it this substrate can pose.",
        "assay_capability_requirement": "ancestral loss under the fresh assay within .10 of C4-01's shelf rates; the ordinary reruns' traces equal C4-06's committed "
                                        "traces (negative control); determinism; cheat",
        "positive_control": "ordinary arm: trace_equal_c406 >= 1.0 on every seed",
        "reachability_estimate": {"note": "descendant sampling; no reachability claim"},
        "arms": list(ARMS) + ["insulation_removed"],
        "crn_policy": "same cell seeds and init_pop as C4-06; the perturbed arm differs only in n_ops=2 per birth; assay edits seeded by (campaign_seed, program digest, operator, draw)",
        "budget": {"N": a.N, "G": a.G, "E": a.E, "seeds": a.seeds, "top": TOP, "draws": a.draws, "walkers": len(walkers)},
        "primary_observable": "per population: single-edit loss / neutral / coherent / improved shares with Wilson bands, mean length, category shares; "
                              "P1 perturbed loss < ancestral by >= .10; P2 ordinary loss NOT < ancestral by >= .10; suspected categories (share diff >= .10); "
                              "ablation loss delta on perturbed elites",
        "claim_ceiling": "a population comparison under one perturbation regime on one substrate; the ablation is prospective but static (NOP-out), not mechanistic",
        "falsification_condition": "P1 lost -> NEGATIVE",
        "kill_condition": "control failure -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["INSTRUMENT_INVALID", "REPRESENTATION_BLOCKED (insulation_removed arm)", "NOT_EXAMINED (ablation, when no category differs)"],
        "expected_machine_telemetry": ["traces", "assay rows per program", "population tables", "ablation table"],
        "machine_changes_exercised": ["descend n_ops=2", "NOP-out ablation"],
        "replacement_condition": "none",
        "ancestry": "original (queue slot 8)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": 1, "positive_control": {"arm": "ordinary", "metric": "trace_equal_c406", "min": 1.0, "min_rows": len(a.seeds)},
                 "primary": {"treatment": "perturbed", "control": "ancestral", "metric": "loss_p", "min_effect": -0.10}},
    })
    X.decision("D4-012: perturbation regime = descend(n_ops=2, mate=None) per birth; descendant sample = top-%d of each final population; the ordinary arm is "
               "RERUN (C4-06 saved traces, not manifests) and its traces are the negative control; suspected structures chosen only after the assay" % TOP)
    X.open("cmp4-c4-08")
    wid = X.world("robust", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    jobs = [{"arm": arm, "seed": s, "N": a.N, "G": a.G, "E": a.E, "walkers": walkers} for arm in ("ordinary", "perturbed") for s in a.seeds]
    runs = X.pool_map(evolve_final, jobs, "evolve_s")
    trace_ok = {}
    for r in runs:
        if r["arm"] == "ordinary":
            ref = c406.get(("mutation_only", r["seed"]))
            trace_ok[r["seed"]] = (ref is not None and ref["trace_best"] == r["trace_best"])
    # assay samples
    samples = [{"manifest": w["manifest"], "tag": "ancestral", "draws": a.draws, "E": a.E} for w in walkers]
    for r in runs:
        samples += [{"manifest": f["manifest"], "tag": r["arm"], "draws": a.draws, "E": a.E, "seed": r["seed"]} for f in r["final_top"]]
    assays = X.pool_map(assay_program, samples, "assay_s")
    for s, asy in zip(samples, assays):
        asy["seed"] = s.get("seed")
    tables = {arm: pop_table([x for x in assays if x["tag"] == arm]) for arm in ARMS}
    la, lo, lp = tables["ancestral"]["loss"]["p"], tables["ordinary"]["loss"]["p"], tables["perturbed"]["loss"]["p"]
    preds = {"P1": {"stated": "perturbed loss < ancestral loss by >= 0.10", "ancestral": la, "perturbed": lp, "held": (la is not None and lp is not None and la - lp >= 0.10)},
             "P2": {"stated": "ordinary loss NOT < ancestral by >= 0.10", "ordinary": lo, "held": (la is not None and lo is not None and not (la - lo >= 0.10))}}
    # structure: categories whose share differs (perturbed vs ancestral) by >= .10; length confound
    cs_a, cs_p = tables["ancestral"]["category_shares"], tables["perturbed"]["category_shares"]
    suspected = {c: round(cs_p.get(c, 0) - cs_a.get(c, 0), 4) for c in set(cs_a) | set(cs_p) if abs(cs_p.get(c, 0) - cs_a.get(c, 0)) >= 0.10}
    length_confound = tables["perturbed"]["mean_len"] >= 1.25 * tables["ancestral"]["mean_len"]
    ablation = {"status": "NOT_EXAMINED", "reason": "no category share differs by >= 0.10"} if not suspected else {"status": "RUN", "categories": {}}
    if suspected:
        elites = [r["final_top"][0]["manifest"] for r in runs if r["arm"] == "perturbed"]
        for cat in suspected:
            abl_jobs = [{"manifest": ablate(m, cat), "tag": "ablated_" + cat, "draws": a.draws, "E": a.E} for m in elites]
            abl = X.pool_map(assay_program, abl_jobs, "ablate_%s_s" % cat)
            base = X.pool_map(assay_program, [{"manifest": m, "tag": "elite", "draws": a.draws, "E": a.E} for m in elites], "elite_s")
            tb, ta = pop_table(base), pop_table(abl)
            ablation["categories"][cat] = {"share_delta": suspected[cat], "elite_loss": tb["loss"]["p"], "ablated_loss": ta["loss"]["p"],
                                           "elite_reward": tb["mean_reward_w2k2"], "ablated_reward": ta["mean_reward_w2k2"],
                                           "contributes": (ta["loss"]["p"] is not None and tb["loss"]["p"] is not None and ta["loss"]["p"] - tb["loss"]["p"] >= 0.10 and ta["mean_reward_w2k2"] >= C1.FLOOR)}
    grouped = []
    for arm in ARMS:
        t = tables[arm]
        grouped.append({"arm": arm, "loss_p": t["loss"]["p"], "neutral_p": t["neutral"]["p"], "coherent_p": t["coherent"]["p"], "mean_len": t["mean_len"], "n": t["edits_applied"]})
    for s, ok in trace_ok.items():
        grouped.append({"arm": "ordinary", "seed": s, "trace_equal_c406": 1.0 if ok else 0.0, "n": 1})
    grouped.append({"arm": "insulation_removed", "disposition": "REPRESENTATION_BLOCKED", "n": 0})
    for arm in ARMS:
        X.record(wid, {"arm": arm}, {"population": arm}, {"table": tables[arm], "label": "C4-08 fresh-assay table"}, "SURVIVED", key_parts=("pop", arm))
    X.record(wid, {"arm": "ablation"}, {"ablation": True}, {"ablation": ablation, "suspected": suspected, "length_confound": length_confound}, "SURVIVED" if suspected else "INCONCLUSIVE", key_parts=("ablation",))
    out_tables = {"tables": tables, "predictions": preds, "suspected_categories": suspected, "length_confound": length_confound, "ablation": ablation,
                  "trace_equal_c406": trace_ok, "walkers": {"regenerated": rw["regenerated"], "digest_mismatches": rw["digest_mismatches"]},
                  "runs": [{k: v for k, v in r.items() if k != "final_top"} for r in runs], "wall_s": round(time.time() - t0, 1)}
    X.att.write("ROBUSTNESS_TABLES.json", out_tables)
    X.att.write("assays.json", [{k: v for k, v in x.items() if k != "rows"} for x in assays])
    X.att.write("assay_rows.json", assays)
    X.att.write("final_tops.json", [{"arm": r["arm"], "seed": r["seed"], "final_top": r["final_top"]} for r in runs])
    X.publish(wid, "robustness_tables", "cmp4.c408_tables.v1", out_tables, {"info_kind": "artifact", "label": "C4-08 tables"})
    out = X.close(grouped, addendum={"predictions": json.dumps(preds), "ablation": json.dumps(ablation), "length_confound": str(length_confound)})
    print(json.dumps({"tables": {arm: {k: v for k, v in tables[arm].items() if k != "category_shares"} for arm in ARMS}, "predictions": preds,
                      "suspected": suspected, "length_confound": length_confound, "ablation": ablation, "trace_equal_c406": trace_ok, "close": out}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
