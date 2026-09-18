"""C4-02 -- MUTATION-RADIUS RESPONSE CURVE (campaign 4, slot 2). Preregistration: C4-02/DESIGN.md.

    python -m archaeon.campaign4.c4_02 [--draws 8] [--E 16] [--procs 12] [--dry-run] [--self-test]

Does genotypic distance have any usable relationship to behavioral distance? For each of the 57
starting program variants and each radius delta in {1, 2, 4, 8, 16}, 8 children made by delta
successive grammar.mutate() calls with operators drawn by the FROZEN WEIGHTS; every child
evaluated on the parent's environment and the three others under the same CRN episodes as C4-01,
classified by C4-01's classifier (D4-003). Radius 0 (identity) is the negative control; the
radius-1 D-distribution against C4-01's weighted mixture of per-operator distributions is the
consistency control (TVD <= 0.10). Nothing is tuned after a result.
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
from proteus.foundry.prng import SplitMix64, seed_from                       # noqa: E402
from proteus.foundry.vm import ManifestError                                 # noqa: E402
from proteus.eval.population_manifest import structural_descriptor           # noqa: E402
from archaeon.campaign4.c4base import C4, CAMPAIGN_SEED                      # noqa: E402
from archaeon.campaign4 import c4_01 as C1                                   # noqa: E402

ID = "C4-02"
RADII = (0, 1, 2, 4, 8, 16)
DRAWS = 8
E = 16
D_LABELS = C1.D_LABELS


def child_at_radius(parent: dict, org: str, delta: int, r: int):
    """delta successive frozen-weight mutate() calls from one rng; returns (child, op_records, undecodable)."""
    rng = SplitMix64(seed_from("c4.02.radius", CAMPAIGN_SEED, org, delta, r))
    m = json.loads(json.dumps(parent))
    recs = []
    for _ in range(delta):
        try:
            m, rec = GR.mutate(m, rng, mate=None, name=None)
        except ManifestError as exc:
            return None, recs, str(exc)[:200]
        recs.append(rec)
    return m, recs, None


def census_parent(job: dict) -> List[dict]:
    pm = job["parent"]
    org = job["organism_id"]
    stratum = job["stratum"]
    env = C1.PARENT_ENV[stratum]
    eps = {k: C1.episodes(k, job["E"]) for k in C1.ENVS}
    pev = C1.eval_all(pm, eps)
    pdesc = structural_descriptor(pm)
    rows = []
    for delta in RADII:
        for r in range(1, job["draws"] + 1):
            if delta == 0 and r > 1:
                break                                   # one identity row per parent
            rec = {"parent_id": org, "stratum": stratum, "parent_env": env, "radius": delta, "arm": "r%d" % delta, "draw": r,
                   "parent_reward": pev[env]["reward_per_ask"], "parent_descriptor": pdesc,
                   "parent_evals": {k: v["reward_per_ask"] for k, v in pev.items()},
                   "parent_degenerate": pev[env]["answered_share"] == 0.0 or bool(pev[env].get("_constant_answer"))}
            if delta == 0:
                child, recs, err = json.loads(json.dumps(pm)), [], None
            else:
                child, recs, err = child_at_radius(pm, org, delta, r)
            rec["op_records"] = recs
            rec["operators"] = [x["operator"] for x in recs]
            rec["first_operator"] = recs[0]["operator"] if recs else "identity"
            rec["noop_steps"] = sum(1 for x in recs if "noop" in (x.get("args") or {}))
            rec["applied"] = err is None
            rec["could_not_apply"] = False                    # a radius step that noops still counts as a step
            if err is not None:
                rec["validation_error"] = err
                rec["classification"] = C1.classify({}, pev, 0.0, True, env)
            else:
                cev = C1.eval_all(child, eps)
                disp = C1.displacement(cev[env]["_answers"], pev[env]["_answers"])
                rec["evals"] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")} for k, v in cev.items()}
                rec["displacement"] = disp
                rec["statuses"] = cev[env]["statuses"]
                rec["ops_per_episode"] = cev[env]["ops_per_episode"]
                rec["len_after"] = len(child["genome"]) // GR.IW
                rec["len_before"] = len(pm["genome"]) // GR.IW
                rec["child_descriptor"] = structural_descriptor(child)
                rec["child_digest"] = hashlib.sha256(json.dumps(child, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                rec["classification"] = C1.classify(cev, pev, disp, False, env)
            rec["D"] = rec["classification"]["label"]
            rows.append(rec)
    return rows


# ---------------------------------------------------------------- curves and shapes
def curve(rows: List[dict], key) -> dict:
    out = {}
    for k, g in C1.flow_table(rows, key).items():
        out[k] = g
    return out


def _p(g: dict, d: str) -> float:
    return (g["rates"][d]["p"] or 0.0) if g["applied"] else 0.0


def shapes(by_radius: dict, by_radius_stratum: dict, by_first_op: dict) -> dict:
    """The preregistered failure shapes (C4-02/DESIGN.md), each a measured predicate."""
    rad = [r for r in RADII if r > 0 and ("r%d" % r) in by_radius]
    loss = {r: _p(by_radius["r%d" % r], "D2") + _p(by_radius["r%d" % r], "D3") for r in rad}
    neut = {r: _p(by_radius["r%d" % r], "D5") for r in rad}
    disp = {r: by_radius["r%d" % r]["displacement_mean"] for r in rad}
    var = {}
    for r in rad:
        g = by_radius["r%d" % r]
        # variance from the histogram is coarse; use the rows' displacement list kept in _disp
        var[r] = g.get("displacement_var")
    sh = {"flat_neutral": all(neut[r] >= 0.8 for r in rad),
          "cliff": any(loss[rad[i + 1]] - loss[rad[i]] >= 0.5 for i in range(len(rad) - 1)),
          "complete_catastrophe": bool(rad) and loss[rad[0]] >= 0.95,
          "loss_by_radius": loss, "neutral_by_radius": neut, "displacement_by_radius": disp}
    # region between "nothing changes" and "everything dies", per stratum
    region = {}
    for k, g in by_radius_stratum.items():
        r, s = k.split("|")
        if not g["applied"]:
            continue
        ok = _p(g, "D5") <= 0.5 and (_p(g, "D2") + _p(g, "D3")) <= 0.5 and g["displacement_mean"] is not None and 0 < g["displacement_mean"] < 1
        region.setdefault(s, {})[r] = ok
    sh["traversable_region_by_stratum"] = {s: any(v.values()) for s, v in region.items()}
    sh["traversable_region_cells"] = region
    # islands: stratum curves vs pooled at some delta (TVD >= 0.3); first-operator curves at delta 1
    def tvd(a, b):
        return round(0.5 * sum(abs(_p(a, d) - _p(b, d)) for d in D_LABELS), 4)
    sh["parent_specific_islands"] = {k: tvd(g, by_radius[k.split("|")[0]]) for k, g in by_radius_stratum.items() if g["applied"]}
    sh["parent_specific_islands_present"] = any(v >= 0.3 for v in sh["parent_specific_islands"].values())
    sh["operator_specific_islands"] = {k: tvd(g, by_radius["r1"]) for k, g in by_first_op.items() if g["applied"] and "r1" in by_radius}
    sh["operator_specific_islands_present"] = any(v >= 0.3 for v in sh["operator_specific_islands"].values())
    return sh


def c401_mixture(applicable_ops: Dict[str, int]) -> dict:
    """C4-01's per-operator D-distributions weighted by the grammar's frozen weights,
    renormalized over the operators that applied: the expected radius-1 distribution."""
    p = C4 / "C4-01" / "attempts" / "a02" / "FLOW_TABLES.json"
    if not p.exists():
        return {"available": False}
    t = json.loads(p.read_text(encoding="utf-8"))["by_operator"]
    w = dict(zip(GR.NAMES, GR.WEIGHTS))
    tot = sum(w[o] for o in GR.NAMES if o in t and t[o]["applied"])
    mix = {d: 0.0 for d in D_LABELS}
    for o in GR.NAMES:
        if o in t and t[o]["applied"]:
            for d in D_LABELS:
                mix[d] += (w[o] / tot) * ((t[o]["rates"][d]["p"] or 0.0))
    return {"available": True, "mixture": {d: round(v, 4) for d, v in mix.items()}, "source": str(p.relative_to(REPO)).replace("\\", "/")}


def group_rows(rows: List[dict]) -> List[dict]:
    by: Dict[tuple, list] = {}
    for r in rows:
        by.setdefault((r["parent_id"], r["arm"]), []).append(r)
    out = []
    for (pid, arm), rs in sorted(by.items()):
        applied = [r for r in rs if r["applied"]]
        c = Counter(r["D"] for r in applied)
        n = len(applied)
        out.append({"parent_id": pid, "arm": arm, "radius": rs[0]["radius"], "stratum": rs[0]["stratum"], "draws": len(rs), "applied": n,
                    "loss_rate": (c["D0"] + c["D2"] + c["D3"]) / n if n else None, "neutral_rate": c["D5"] / n if n else None,
                    "improved_rate": c["D7"] / n if n else None, "exaptive_rate": c["D6"] / n if n else None,
                    "displacement_mean": (sum(r.get("displacement", 0.0) for r in applied) / n) if n else None,
                    "identity_ok": (sum(1 for r in applied if C1.identity_ok(r)) / n if n else None) if arm == "r0" else None,
                    "noop_steps_mean": (sum(r["noop_steps"] for r in rs) / len(rs)) if rs else None, "D_counts": dict(c)})
    return out


def self_test() -> int:
    from proteus.foundry import generate as G                                # noqa: PLC0415
    from archaeon.campaign2.c2base import FOUNDRY_C2                         # noqa: PLC0415
    m = [o["manifest"] for o in G.generate(dict(FOUNDRY_C2, seed=78, n=1))][0]
    job = {"parent": m, "organism_id": "selftest-0", "stratum": "gen0_random", "draws": 2, "E": 8}
    a = census_parent(job); b = census_parent(job)
    same = json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)
    r0 = [r for r in a if r["radius"] == 0]
    rad = Counter(r["radius"] for r in a)
    lens = {r["radius"]: len(r["operators"]) for r in a}
    ok = same and all(C1.identity_ok(r) for r in r0) and all(lens[k] == k for k in lens)
    print(json.dumps({"rows": len(a), "deterministic": same, "identity_ok": all(C1.identity_ok(r) for r in r0), "rows_per_radius": rad,
                      "operators_per_child_equals_radius": all(lens[k] == k for k in lens), "mixture": c401_mixture({})}, indent=1, default=str))
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=DRAWS)
    ap.add_argument("--E", type=int, default=E)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C4-02 radius curve")
    if a.self_test:
        return self_test()
    if not a.dry_run and not C1.gate_is_green():
        print("REFUSED: launch gate not green")
        return 3
    from archaeon.campaign4.c4harness import Experiment4                    # noqa: PLC0415

    class Radius(Experiment4):
        ID = "C4-02"
        TITLE = "mutation-radius response curve"
        PARENTS = ["C4-01"]
        ARM_FIELD = "arm"
        METRICS = ("loss_rate", "neutral_rate", "displacement_mean", "exaptive_rate")

    X = Radius(dry_run=a.dry_run, procs=a.procs)
    design = (C4 / "C4-02" / "DESIGN.md").read_text(encoding="utf-8")
    X.seal({
        "question": "Does genotypic distance have any usable relationship to behavioral distance? For radii 1, 2, 4, 8, 16 successive frozen-weight "
                    "grammar edits from each of the 57 starting program variants: D(delta) = displacement conditional on executing, and P(D2 or D3 | delta).",
        "parent_evidence": "C4-01 (54ce467f2): at radius 1, D7 = 0 in 5,472 edits; displacement bimodal (0 or > 0.75); loss by operator .15-.76; "
                           "gen0_random parents degenerate themselves.",
        "why_this_slot": "Whether a region exists between 'nothing changes' and 'everything dies' decides what C4-05 (neutral walks) and C4-06 (recombination) "
                         "can even attempt; it replaces further blind attacks on the old hard summit (directive section 4).",
        "assay_capability_requirement": "radius 0 identity 57/57 (displacement 0, parent's rewards); radius-1 D-distribution within TVD 0.10 of C4-01's "
                                        "frozen-weight mixture of per-operator distributions",
        "positive_control": "r0 arm: identity_ok >= 1.0 on 57/57 parents; consistency: TVD(r1, C4-01 mixture) <= 0.10",
        "reachability_estimate": {"note": "evaluation census; no reachability lookup applies"},
        "arms": ["r%d" % r for r in RADII],
        "crn_policy": "the SAME episode sets as C4-01 (family train, index 1, E=%d); children seeded from (campaign_seed, organism_id, radius, draw); "
                      "operators drawn by frozen weights (name=None)" % a.E,
        "budget": {"parents": 57, "radii": list(RADII), "draws": a.draws, "E": a.E, "environments": list(C1.ENVS), "floor": C1.FLOOR, "band": C1.BAND},
        "primary_observable": "per radius and per (radius, stratum): mean displacement, displacement histogram, P(D2 or D3), P(D5), P(D6 or D7) with Wilson bands; "
                              "the same by first operator at radius 1; the six named shapes as measured predicates; traversable-region cells per stratum",
        "claim_ceiling": "a measured curve at 8 draws per (parent, radius) on one frozen substrate; no mechanism",
        "falsification_condition": "NEGATIVE if flat-neutral (P(D5) >= 0.8 at every radius) or complete catastrophe (P(D2 or D3) >= 0.95 at radius 1) "
                                   "holds for every stratum (no traversable region anywhere); SUPPORTED if a traversable region exists in >= 1 stratum",
        "kill_condition": "a control fails -> INSTRUMENT_INVALID (if the consistency control fails, C4-02 and C4-01 disagree about the same substrate; "
                          "investigated before C4-03)",
        "typed_failure_conditions": ["INSTRUMENT_INVALID", "UNDERPOWERED", "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["curves by radius / stratum / first operator", "op_records per child", "noop steps per child", "descriptors before/after"],
        "machine_changes_exercised": ["C4-01 classifier reused unchanged", "radius composition of frozen-weight edits"],
        "replacement_condition": "none",
        "ancestry": "original (queue slot 2)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": 57, "positive_control": {"arm": "r0", "metric": "identity_ok", "min": 1.0, "min_rows": 57},
                 "primary": {"treatment": "r8", "control": "r1", "metric": "loss_rate", "min_effect": 0.05}},
    })
    X.decision("D4-006: radius = number of mutate() applications including steps whose operator noops (noop_steps recorded per child); "
               "prediction written to be lost: loss_rate(r8) - loss_rate(r1) >= 0.05")
    parents = C1.parents_from_population() if not a.dry_run else [
        {"organism_id": "dry-%d" % i, "stratum": "gen0_random", "parent": m}
        for i, m in enumerate(o["manifest"] for o in __import__("proteus.foundry.generate", fromlist=["generate"]).generate(
            dict(__import__("archaeon.campaign2.c2base", fromlist=["FOUNDRY_C2"]).FOUNDRY_C2, seed=78, n=3)))]
    X.open("cmp4-c4-02")
    wid = X.world("radius", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    per_parent = X.pool_map(census_parent, [dict(p, draws=a.draws, E=a.E) for p in parents], "census_s")
    rows = [r for rs in per_parent for r in rs]
    # displacement variance per radius (for the exploding-variance shape)
    by_radius = curve(rows, lambda r: r["arm"])
    for arm, g in by_radius.items():
        ds = [r["displacement"] for r in rows if r["arm"] == arm and "displacement" in r]
        mu = sum(ds) / len(ds) if ds else None
        g["displacement_var"] = round(sum((d - mu) ** 2 for d in ds) / len(ds), 5) if ds else None
    by_rs = curve(rows, lambda r: "%s|%s" % (r["arm"], r["stratum"]))
    by_first = curve([r for r in rows if r["radius"] == 1], lambda r: r["first_operator"])
    sh = shapes(by_radius, by_rs, by_first)
    vs = [by_radius["r%d" % r]["displacement_var"] for r in RADII if r > 0 and "r%d" % r in by_radius]
    sh["exploding_variance"] = any(vs[i + 1] is not None and vs[i] and vs[i + 1] >= 4 * vs[i] for i in range(len(vs) - 1))
    mix = c401_mixture({})
    if mix.get("available") and "r1" in by_radius:
        sh["consistency_tvd_r1_vs_c401_mixture"] = round(0.5 * sum(abs(_p(by_radius["r1"], d) - mix["mixture"][d]) for d in D_LABELS), 4)
        sh["consistency_ok"] = sh["consistency_tvd_r1_vs_c401_mixture"] <= 0.10
    grouped = group_rows(rows)
    for g in grouped:
        rs = [r for r in rows if r["parent_id"] == g["parent_id"] and r["arm"] == g["arm"]]
        content = {"group": g, "children": [{k: r.get(k) for k in ("draw", "D", "operators", "noop_steps", "displacement", "len_before", "len_after", "child_digest", "classification")} for r in rs],
                   "label": "C4-02 radius row; raw evaluate() dicts in children.json"}
        X.record(wid, g, {"parent": g["parent_id"], "radius": g["radius"]}, content, "SURVIVED" if g["applied"] else "INCONCLUSIVE",
                 key_parts=(g["parent_id"][:16], g["arm"]))
    tables = {"by_radius": by_radius, "by_radius_stratum": by_rs, "by_first_operator_r1": by_first, "shapes": sh, "c401_mixture": mix,
              "d1_eligible": 0, "wall_s": round(time.time() - t0, 1)}
    X.att.write("CURVES.json", tables)
    X.att.write("children.json", rows)
    X.publish(wid, "curves", "cmp4.radius_curves.v1", tables, {"info_kind": "artifact", "label": "C4-02 radius curves"})
    out = X.close(grouped, meas_extra={"tables_digest": hashlib.sha256(json.dumps(tables, sort_keys=True, default=str).encode()).hexdigest()},
                  addendum={"shapes": json.dumps({k: v for k, v in sh.items() if not isinstance(v, dict)})})
    print(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
