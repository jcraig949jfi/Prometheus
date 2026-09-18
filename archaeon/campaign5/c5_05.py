"""C5-05 -- DAMAGE GEOMETRY UNDER REPRESENTATION B (campaign 5, Phase B). Preregistration: C5-05/DESIGN.md.

    python -m archaeon.campaign5.c5_05 [--draws 8] [--procs 12] [--dry-run] [--self-test]

Arm R replicates C4-01 a02 (original parents, grammar v0.4, C4 seeds, OLD evaluator) label for
label. Arms G_v04 and G_B generate children once from the CANONICAL parents and evaluate each
child under OLD, B_FAIL and B_FIZZLE (matched perturbations, kept for C5-06). Bins DT / DF are
read before the unchanged C4-01 classifier.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from proteus.foundry import grammar as GR                                    # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from                       # noqa: E402
from proteus.foundry.vm import ManifestError                                 # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402
from archaeon.campaign5.c5base import C5, CAMPAIGN_SEED                      # noqa: E402
from archaeon.campaign5.repb import gen_b, grammar_b                         # noqa: E402
from archaeon.campaign5.repb.evaluate_b import evaluate_b                    # noqa: E402
from archaeon.campaign5.repb.vm_b import static_validity                     # noqa: E402

ID = "C5-05"
GRAMMARS = ("v04", "B")
INTERPS = ("OLD", "B_FAIL", "B_FIZZLE")
BINS = ("D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "DT", "DF")
DF_SUB = ("D2", "D3", "D4", "D5", "D6", "D7")
C401_CHILDREN = REPO / "archaeon" / "campaign4" / "C4-01" / "attempts" / "a02" / "children.json.gz"


def _digest(m: dict) -> str:
    return hashlib.sha256(json.dumps(m, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def eval_all_b(manifest: dict, eps: Dict[str, list], mode: str) -> Dict[str, dict]:
    out = {}
    for env, e in eps.items():
        r = evaluate_b(manifest, e, rng_seed=0, reward_mode="per_ask", mode=mode)
        r["meter"] = {k: v for k, v in r["meter"].items() if k not in ("wall_s", "cpu_s")}
        a = r["_answers"]; vals = [x for x in a if x is not None]
        r["_constant_answer"] = bool(vals) and len(set(vals)) == 1 and len(vals) == len(a)
        out[env] = r
    return out


def classify_b(cev: Dict[str, dict], pev: Dict[str, dict], disp: float, env: str, mode: str) -> dict:
    c = cev[env]
    if mode == "B_FAIL" and c.get("trapped"):
        return {"label": "DT", "why": "trapped on the parent environment (first fault ends the evaluation)", "trap_at": c["trap_at"], "reward": 0.0,
                "parent_reward": pev[env]["reward_per_ask"], "displacement": disp}
    base = C1.classify(cev, pev, disp, False, env)
    if mode == "B_FIZZLE" and c.get("faults", 0) > 0:
        return {"label": "DF", "sub": base["label"], "faults": c["faults"], "fault_sites": c["fault_sites"], "why": "faulted and continued; sub-bin = C4 label of the fizzled behaviour",
                **{k: v for k, v in base.items() if k not in ("label", "why")}}
    return base


def _interp_row(child: dict, cev: Dict[str, dict], pev: Dict[str, dict], env: str, mode: str) -> dict:
    disp = C1.displacement(cev[env]["_answers"], pev[env]["_answers"])
    cl = classify_b(cev, pev, disp, env, mode)
    return {"D": cl["label"], "sub": cl.get("sub"), "displacement": disp, "reward": cev[env]["reward_per_ask"], "answered_share": cev[env]["answered_share"],
            "evals": {k: v["reward_per_ask"] for k, v in cev.items()}, "faults": cev[env].get("faults", 0), "fault_sites": cev[env].get("fault_sites", 0),
            "trapped": bool(cev[env].get("trapped", False)), "ops_per_episode": cev[env]["ops_per_episode"], "classification": cl}


def census_parent_b(job: dict) -> List[dict]:
    """Rows for one canonical parent under one grammar: 12 operators x draws + 2 controls, each under the 3 interpreters."""
    pm, org, stratum, grammar = job["parent"], job["organism_id"], job["stratum"], job["grammar"]
    env = C1.PARENT_ENV[stratum]
    eps = {k: C1.episodes(k, job["E"]) for k in C1.ENVS}
    pev = {"OLD": C1.eval_all(pm, eps), "B_FAIL": eval_all_b(pm, eps, "FAIL"), "B_FIZZLE": eval_all_b(pm, eps, "FIZZLE")}
    rows = []
    edits = [(op, r) for op in C1.OPERATORS for r in range(1, job["draws"] + 1)] + [("control_identity", 0), ("control_randomize_all", 0)]
    for op, r in edits:
        rec = {"parent_id": org, "stratum": stratum, "parent_env": env, "grammar": grammar, "operator": op, "draw": r,
               "parent_reward": pev["OLD"][env]["reward_per_ask"], "parent_degenerate": pev["OLD"][env]["answered_share"] == 0.0 or bool(pev["OLD"][env].get("_constant_answer"))}
        undecodable = False; args: dict = {}; child = None
        if op == "control_identity":
            child = json.loads(json.dumps(pm)); args = {"control": "identity"}
        elif op == "control_randomize_all":
            rng = SplitMix64(seed_from("c5.05.control", CAMPAIGN_SEED, org, grammar))
            child = json.loads(json.dumps(pm))
            if grammar == "B":
                g = []
                for _ in range(len(child["genome"]) // 4):
                    g.extend(gen_b.valid_instr(rng, child["n_regs"]))
                child["genome"] = g
            else:
                child["genome"] = [rng.next_u32() for _ in child["genome"]]
            args = {"control": "randomize_all", "k": len(child["genome"]) // 4}
        else:
            rng = SplitMix64(seed_from("c5.05.edit", CAMPAIGN_SEED, org, grammar, op, r))
            try:
                if grammar == "B":
                    child, oprec = grammar_b.mutate_b(pm, rng, mate=None, name=op)
                else:
                    child, oprec = GR.mutate(pm, rng, mate=None, name=op)
                args = oprec["args"]; rec["len_before"], rec["len_after"] = oprec["len_before"], oprec["len_after"]
            except ManifestError as exc:
                undecodable = True; rec["validation_error"] = str(exc)[:200]
        rec["args"] = args
        rec["applied"] = not undecodable and not ("noop" in args)
        rec["could_not_apply"] = "noop" in args
        rec["region"] = C1.region_of(pm, op, args) if op in C1.OPERATORS else "CONTROL"
        if child is not None and not undecodable:
            sv = static_validity(child)
            rec["crossing"] = not sv["all_valid"]; rec["static_invalid"] = sv["invalid"]
            rec["child_digest"] = _digest(child)
            rec["by"] = {"OLD": _interp_row(child, C1.eval_all(child, eps), pev["OLD"], env, "OLD"),
                         "B_FAIL": _interp_row(child, eval_all_b(child, eps, "FAIL"), pev["B_FAIL"], env, "B_FAIL"),
                         "B_FIZZLE": _interp_row(child, eval_all_b(child, eps, "FIZZLE"), pev["B_FIZZLE"], env, "B_FIZZLE")}
        else:
            rec["crossing"] = None; rec["static_invalid"] = None
            rec["by"] = {m: {"D": "D0", "sub": None, "displacement": 0.0, "reward": 0.0, "classification": {"label": "D0", "why": "undecodable"}} for m in INTERPS}
        rec["parent_evals"] = {m: {k: v["reward_per_ask"] for k, v in pev[m].items()} for m in INTERPS}
        rows.append(rec)
    return rows


def replication_arm(parents: list, draws: int, E: int, procs: int, pool_map) -> dict:
    """Arm R: C4-01's census re-run byte for byte, compared to the committed children.json.gz."""
    with gzip.open(C401_CHILDREN, "rt", encoding="utf-8") as f:
        ref = json.load(f)
    key = lambda r: (r["parent_id"], r["operator"], r["draw"])                        # noqa: E731
    ref_by = {key(r): (r.get("child_digest"), r["D"]) for r in ref}
    jobs = [{"parent": p["parent"], "organism_id": p["organism_id"], "stratum": p["stratum"], "E": E, "draws": draws} for p in parents]
    got = [r for rows in pool_map(C1.census_parent, jobs, "R_arm_s") for r in rows]
    n = digest_ok = label_ok = missing = 0
    for r in got:
        k = key(r)
        if k not in ref_by:
            missing += 1; continue
        n += 1
        d, lab = ref_by[k]
        digest_ok += (r.get("child_digest") == d); label_ok += (r["D"] == lab)
    return {"rows_regenerated": len(got), "rows_matched": n, "missing_in_reference": missing, "digest_equal": digest_ok, "label_equal": label_ok,
            "pass": n > 0 and digest_ok == n and label_ok == n, "reference": str(C401_CHILDREN.relative_to(REPO)).replace("\\", "/")}


def aggregate(rows: List[dict]) -> dict:
    W = C1.wilson
    out = {"by_grammar_interp_operator": {}, "by_grammar_interp": {}, "thresholds": {}, "crossing_share": {}, "displacement_by_bin": {}}
    for g in GRAMMARS:
        gr = [r for r in rows if r["grammar"] == g and r["operator"] in C1.OPERATORS and r["applied"]]
        out["crossing_share"][g] = {"n": len(gr), "crossing": sum(1 for r in gr if r["crossing"]), "share": round(sum(1 for r in gr if r["crossing"]) / max(1, len(gr)), 4)}
        for m in INTERPS:
            key = "%s x %s" % (g, m)
            cnt = Counter(r["by"][m]["D"] for r in gr)
            sub = Counter(r["by"][m]["sub"] for r in gr if r["by"][m]["D"] == "DF")
            n = len(gr)
            out["by_grammar_interp"][key] = {"n": n, **{b: {"k": cnt.get(b, 0), "rate": round(cnt.get(b, 0) / max(1, n), 4), "wilson": W(cnt.get(b, 0), n)} for b in BINS},
                                             "DF_sub": {s: sub.get(s, 0) for s in DF_SUB}}
            for op in C1.OPERATORS:
                orows = [r for r in gr if r["operator"] == op]
                c = Counter(r["by"][m]["D"] for r in orows)
                out["by_grammar_interp_operator"]["%s x %s x %s" % (g, m, op)] = {"n": len(orows), "crossing": sum(1 for r in orows if r["crossing"]),
                                                                                    **{b: c.get(b, 0) for b in BINS if c.get(b, 0)},
                                                                                    "DF_sub": dict(Counter(r["by"][m]["sub"] for r in orows if r["by"][m]["D"] == "DF"))}
            for b in BINS:
                ds = [r["by"][m]["displacement"] for r in gr if r["by"][m]["D"] == b]
                if ds:
                    out["displacement_by_bin"]["%s x %s x %s" % (g, m, b)] = {"n": len(ds), "mean": round(sum(ds) / len(ds), 4),
                                                                              "hist": {"0": sum(1 for d in ds if d == 0), "(0,.25]": sum(1 for d in ds if 0 < d <= .25),
                                                                                       "(.25,.5]": sum(1 for d in ds if .25 < d <= .5), "(.5,1]": sum(1 for d in ds if d > .5)}}
    # thresholds (per grammar arm)
    for g in GRAMMARS:
        gr = [r for r in rows if r["grammar"] == g and r["operator"] in C1.OPERATORS and r["applied"]]
        cross = [r for r in gr if r["crossing"]]; non = [r for r in gr if not r["crossing"]]
        t1_k = sum(1 for r in cross if r["by"]["B_FAIL"]["D"] == "DT")
        t1 = {"crossing_n": len(cross), "DT": t1_k, "share": round(t1_k / max(1, len(cross)), 4), "wilson": W(t1_k, max(1, len(cross))), "pass": len(cross) > 0 and t1_k / len(cross) >= 0.5}
        d5_fail = sum(1 for r in non if r["by"]["B_FAIL"]["D"] == "D5"); d5_old = sum(1 for r in non if r["by"]["OLD"]["D"] == "D5")
        t2 = {"non_crossing_n": len(non), "D5_B_FAIL": round(d5_fail / max(1, len(non)), 4), "D5_OLD": round(d5_old / max(1, len(non)), 4),
              "pass": abs(d5_fail - d5_old) / max(1, len(non)) <= C1.BAND}
        d6 = {m: sum(1 for r in gr if r["by"][m]["D"] == "D6") for m in INTERPS}
        t3 = {"D6": {m: {"k": d6[m], "rate": round(d6[m] / max(1, len(gr)), 4), "wilson": W(d6[m], max(1, len(gr)))} for m in INTERPS},
              "prediction_B_FAIL_lower_than_OLD_by_band": (d6["OLD"] - d6["B_FAIL"]) / max(1, len(gr)) > C1.BAND}
        f_cross = [r for r in cross if r["by"]["B_FIZZLE"]["D"] == "DF"]
        rec_k = sum(1 for r in f_cross if r["by"]["B_FIZZLE"]["sub"] in ("D5", "D6", "D7"))
        t4 = {"crossing_faulted_n": len(f_cross), "recovered_competent": rec_k, "share": round(rec_k / max(1, len(f_cross)), 4), "wilson": W(rec_k, max(1, len(f_cross))),
              "sub": dict(Counter(r["by"]["B_FIZZLE"]["sub"] for r in f_cross))}
        t5 = {m: sum(1 for r in gr if r["by"][m]["D"] == "D7") for m in INTERPS}
        out["thresholds"][g] = {"T1": t1, "T2": t2, "T3": t3, "T4": t4, "T5_D7": t5}
    out["thresholds"]["T6_crossing"] = out["crossing_share"]
    # controls
    ctl = {}
    for g in GRAMMARS:
        idr = [r for r in rows if r["grammar"] == g and r["operator"] == "control_identity"]
        ok = sum(1 for r in idr if all(r["by"][m]["displacement"] == 0.0 and all(abs(r["by"][m]["evals"][k] - r["parent_evals"][m][k]) < 1e-12 for k in r["by"][m]["evals"]) for m in INTERPS))
        rz = [r for r in rows if r["grammar"] == g and r["operator"] == "control_randomize_all"]
        old_destroy = sum(1 for r in rz if r["by"]["OLD"]["reward"] < C1.FLOOR); fail_dt_d2 = sum(1 for r in rz if r["by"]["B_FAIL"]["D"] in ("DT", "D2", "D3"))
        ctl[g] = {"identity_ok": ok, "identity_n": len(idr), "randomize_destroyed_OLD": old_destroy, "randomize_DT_or_D2_D3_B_FAIL": fail_dt_d2, "randomize_n": len(rz),
                  "pass": ok == len(idr) and old_destroy >= 0.95 * len(rz) and fail_dt_d2 == len(rz)}
    out["controls"] = ctl
    return out


def cheat_control() -> dict:
    prog = {"schema_version": "proteus.player_manifest.v0", "n_regs": 4, "tape_words": 32, "code_writable": False, "persist": "none", "tick_budget": 64, "out_cap": 4,
            "genome": [3, 0, 7, 0, 99, 0, 0, 0, 23, 0, 1, 0, 1, 0, 0, 0]}
    eps = {k: C1.episodes(k, 4) for k in C1.ENVS}
    pev_f = eval_all_b(gen_b.canonicalize(prog), eps, "FAIL"); pev_z = eval_all_b(gen_b.canonicalize(prog), eps, "FIZZLE")
    rf = _interp_row(prog, eval_all_b(prog, eps, "FAIL"), pev_f, "W0", "B_FAIL"); rz = _interp_row(prog, eval_all_b(prog, eps, "FIZZLE"), pev_z, "W0", "B_FIZZLE")
    return {"B_FAIL": rf["D"], "B_FIZZLE": rz["D"], "sub": rz["sub"], "pass": rf["D"] == "DT" and rz["D"] == "DF"}


def canonical_parents(parents: list) -> list:
    return [{**p, "parent": gen_b.canonicalize(p["parent"]), "canonical_digest": _digest(gen_b.canonicalize(p["parent"]))} for p in parents]


def self_test(draws: int = 2, E: int = 8) -> int:
    ps = canonical_parents(C1.parents_from_population()[:4])
    rows = []
    for p in ps:
        for g in GRAMMARS:
            rows += census_parent_b({"parent": p["parent"], "organism_id": p["organism_id"], "stratum": p["stratum"], "grammar": g, "draws": draws, "E": E})
    agg = aggregate(rows)
    again = census_parent_b({"parent": ps[0]["parent"], "organism_id": ps[0]["organism_id"], "stratum": ps[0]["stratum"], "grammar": "B", "draws": draws, "E": E})
    det = json.dumps(again, sort_keys=True) == json.dumps([r for r in rows if r["parent_id"] == ps[0]["organism_id"] and r["grammar"] == "B"], sort_keys=True)
    ch = cheat_control()
    print(json.dumps({"rows": len(rows), "controls": agg["controls"], "cheat": ch, "deterministic": det, "crossing": agg["crossing_share"],
                      "bins_B_x_B_FAIL": {b: agg["by_grammar_interp"]["B x B_FAIL"][b]["k"] for b in BINS}, "bins_v04_x_B_FAIL": {b: agg["by_grammar_interp"]["v04 x B_FAIL"][b]["k"] for b in BINS}}, indent=1))
    return 0 if (all(c["pass"] for c in agg["controls"].values()) and ch["pass"] and det) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=C1.DRAWS)
    ap.add_argument("--E", type=int, default=C1.E)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C5-05")
    if a.self_test:
        return self_test()
    from archaeon.campaign5.c5base import harness                            # noqa: PLC0415

    class Geometry(harness()):
        ID = "C5-05"
        TITLE = "damage geometry under representation B (matched perturbations, DT/DF bins)"
        PARENTS = ["C4-01", "C5-03", "C5-04"]
        ARM_FIELD = "arm"
        METRICS = ("d5_rate", "d6_rate", "dt_rate", "df_rate", "crossing")

    X = Geometry(dry_run=a.dry_run, procs=a.procs)
    design = (C5 / "C5-05" / "DESIGN.md").read_text(encoding="utf-8")
    parents = C1.parents_from_population(); cps = canonical_parents(parents)
    X.seal({
        "question": "Under representation B, does a real local failure boundary change how programs die (a TRAP bin absorbing D2/D3 death) while leaving the "
                    "neutral and exaptive bins of non-crossing children where they were?",
        "parent_evidence": "C4-01 (D-taxonomy on the total interpreter; D7 = 0; cliff); C5-03 F8 (grammar B crosses in 9.3% of children); C5-04 (P1-P4 hold).",
        "why_this_slot": "The directive's damage geometry replication with predefined bins; matched perturbations feed C5-06.",
        "assay_capability_requirement": "arm R equals C4-01 a02 label for label and digest for digest; identity/randomize/cheat controls as in DESIGN.md",
        "positive_control": "controls arm: pass >= 1.0",
        "reachability_estimate": {"note": "not a reach experiment"},
        "arms": ["controls", "R"] + ["%s x %s" % (g, m) for g in GRAMMARS for m in INTERPS],
        "crn_policy": "one child per (parent, grammar, operator, draw) from seed_from('c5.05.edit', 20260922, ...); the same child under all three interpreters; episodes as C4-01",
        "budget": {"parents": len(parents), "grammars": list(GRAMMARS), "operators": len(C1.OPERATORS), "draws": a.draws, "E": a.E, "interpreters": list(INTERPS)},
        "primary_observable": "bin distributions per grammar x interpreter (x operator); T1-T6; controls; R replication receipt",
        "claim_ceiling": "single-edit geometry on 57 parents; no evolution; no claim about discovery",
        "falsification_condition": "T1 < .50 (boundary mostly unexecuted) or T2 fails (boundary disturbs non-crossing children) -> the boundary is not what it was designed to be",
        "kill_condition": "R arm mismatch or control failure -> INSTRUMENT_INVALID",
        "typed_failure_conditions": ["INSTRUMENT_INVALID"],
        "expected_machine_telemetry": ["per-child rows with three interpreter readings", "crossing flag", "faults and sites"],
        "machine_changes_exercised": ["classify_b (DT/DF before the C4 classifier)", "grammar B census", "matched-perturbation rows"],
        "replacement_condition": "none",
        "ancestry": "original (Phase B, slot 3; C4-01 replayed)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": len(parents), "positive_control": {"arm": "controls", "metric": "pass", "min": 1.0, "min_rows": 1},
                 "primary": {"treatment": "B x B_FAIL", "control": "B x OLD", "metric": "d6_rate", "min_effect": -0.0625}},
    })
    X.decision("D5-010: C5-05 bins DT/DF read before the unchanged C4-01 classifier; crossing = static invalidity of the child's genome; thresholds T1-T6 fixed in DESIGN.md")
    X.open("cmp5-c5-05")
    wid = X.world("damage-geometry-b", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    rep = replication_arm(parents, a.draws, a.E, a.procs, X.pool_map)
    jobs = [{"parent": p["parent"], "organism_id": p["organism_id"], "stratum": p["stratum"], "grammar": g, "draws": a.draws, "E": a.E} for p in cps for g in GRAMMARS]
    rows = [r for rs in X.pool_map(census_parent_b, jobs, "census_s") for r in rs]
    agg = aggregate(rows); agg["replication"] = rep; agg["cheat"] = cheat_control()
    agg["controls_pass"] = all(c["pass"] for c in agg["controls"].values()) and agg["cheat"]["pass"] and rep["pass"]
    grouped = [{"arm": "controls", "pass": float(agg["controls_pass"]), "n": 1}, {"arm": "R", "pass": float(rep["pass"]), "digest_equal": rep["digest_equal"], "label_equal": rep["label_equal"], "n": rep["rows_matched"]}]
    for p in cps:
        for g in GRAMMARS:
            prow = [r for r in rows if r["parent_id"] == p["organism_id"] and r["grammar"] == g and r["operator"] in C1.OPERATORS and r["applied"]]
            for m in INTERPS:
                c = Counter(r["by"][m]["D"] for r in prow); n = max(1, len(prow))
                grouped.append({"arm": "%s x %s" % (g, m), "parent_id": p["organism_id"], "stratum": p["stratum"], "n": len(prow),
                                "d5_rate": c.get("D5", 0) / n, "d6_rate": c.get("D6", 0) / n, "dt_rate": c.get("DT", 0) / n, "df_rate": c.get("DF", 0) / n,
                                "crossing": sum(1 for r in prow if r["crossing"]) / n})
            content = {"grammar": g, "parent": p["organism_id"], "stratum": p["stratum"], "canonical_digest": p["canonical_digest"],
                       "children": [{"operator": r["operator"], "draw": r["draw"], "crossing": r["crossing"], "digest": r.get("child_digest"),
                                     "D": {m: r["by"][m]["D"] for m in INTERPS}, "sub": r["by"]["B_FIZZLE"].get("sub"), "disp": {m: r["by"][m]["displacement"] for m in INTERPS}} for r in prow]}
            X.record(wid, {"arm": "census", "parent_id": p["organism_id"], "grammar": g}, {"arm": "census", "parent": p["organism_id"], "grammar": g}, content, "SURVIVED", key_parts=(g, p["organism_id"]))
    agg["wall_s"] = round(time.time() - t0, 1)
    X.att.write("GEOMETRY_B.json", agg)
    with gzip.open(X.att.path / "children.json.gz", "wt", encoding="utf-8") as f:
        json.dump(rows, f)
    (X.att.path / "CHILDREN_DIGEST.json").write_text(json.dumps({"children.json.gz_rows": len(rows), "sha256_of_rows_json": hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()}, indent=1) + "\n", encoding="utf-8", newline="\n")
    X.publish(wid, "geometry_b", "cmp5.c505_geometry_b.v1", {k: v for k, v in agg.items() if k != "by_grammar_interp_operator"}, {"info_kind": "artifact", "label": "C5-05 damage geometry under B"})
    out = X.close(grouped, addendum={"thresholds": json.dumps({g: {k: (v.get("pass") if isinstance(v, dict) else v) for k, v in agg["thresholds"][g].items()} for g in GRAMMARS}),
                                     "replication": json.dumps(rep), "crossing": json.dumps(agg["crossing_share"])})
    print(json.dumps({"replication": rep, "controls": agg["controls"], "cheat": agg["cheat"], "crossing": agg["crossing_share"], "thresholds": agg["thresholds"],
                      "bins": {k: {b: v[b]["rate"] for b in BINS} for k, v in agg["by_grammar_interp"].items()}, "close": out["disposition"], "wall_s": agg["wall_s"]}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
