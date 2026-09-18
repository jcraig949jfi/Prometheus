"""C4-01 -- DAMAGE-BOUNDARY CENSUS (campaign 4, slot 1). Preregistration: C4-01/DESIGN.md,
decisions D4-001..D4-004 (DECISIONS.md). Sealed by the harness at run time with the same content.

    python -m archaeon.campaign4.c4_01 [--draws 8] [--E 16] [--procs 12] [--dry-run]
    python -m archaeon.campaign4.c4_01 --self-test        # machinery on synthetic draws; touches no parent

Where does the frozen substrate destroy variation? Every starting program variant (57,
manifest-backed, STARTING_POPULATION.json) x every grammar operator (12, frozen v0.4) x 8 draws,
each child evaluated on its parent's environment and three other preregistered environments
under common random numbers, classified D0..D7 by the rules of D4-003. No selection. The
label is not the evidence: every child row keeps the raw evaluate() dicts.

The interpreter is TOTAL (D4-002): D1 EXECUTION_FAULT cannot fire on this substrate and is
reported with eligible count 0, never as "0 observed".

REFUSES to run the census while the launch gate is RED (the gate receipt is read, not the
prose); --self-test and --dry-run never touch the 57 parents or the engine.
"""
from __future__ import annotations

import argparse
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

from proteus.foundry import grammar as GR                                   # noqa: E402
from proteus.foundry.affordances import CATEGORY, N_OPCODES                  # noqa: E402
from proteus.foundry.prng import SplitMix64, seed_from                       # noqa: E402
from proteus.foundry.vm import ManifestError                                 # noqa: E402
from proteus.eval.population_manifest import structural_descriptor           # noqa: E402
from archaeon.wse.evolve import evaluate                                     # noqa: E402
from archaeon.wse.worlds import WorldSpec, episodes_for, with_knobs          # noqa: E402
from archaeon.campaign4.c4base import C4, CAMPAIGN_SEED                      # noqa: E402

ID = "C4-01"
OPERATORS = tuple(GR.NAMES)                      # 12 operators of the frozen grammar (unreachable_removal removed)
DRAWS = 8
E = 16
# D4-003 constants (fixed before any row)
FLOOR = 3 / 16                                   # viability floor on reward_per_ask
BAND = 1 / 16                                    # equivalence band
D_LABELS = ("D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7")
D_NAMES = {"D0": "UNDECODABLE", "D1": "EXECUTION_FAULT", "D2": "DEGENERATE", "D3": "DISTINCT_NONVIABLE",
           "D4": "VIABLE_WORSE", "D5": "NEUTRAL", "D6": "EXAPTIVE", "D7": "IMPROVED_OR_NOVEL"}
# D4-004: environments
W0 = WorldSpec("W0", value_bits=4)
W0_HELDOUT = with_knobs(W0, name="W0_heldout", vocab="heldout")
W1_D1 = WorldSpec("W1_d1", delay=1, value_bits=4)
W1_D4 = WorldSpec("W1_d4", delay=4, value_bits=4)
W2_K2 = WorldSpec("W2_K2", K=2, value_bits=4)
ENVS = {"W0": W0, "W0_heldout": W0_HELDOUT, "W1_d1": W1_D1, "W1_d4": W1_D4, "W2_K2": W2_K2}
PARENT_ENV = {"gen0_random": "W0", "w0_solver": "W0", "shelf": "W2_K2", "delay_general": "W1_d4"}
OTHER_ENVS = ("W0_heldout", "W1_d1", "W1_d4", "W2_K2")


# ---------------------------------------------------------------- evaluation
def episodes(env: str, e: int = E) -> list:
    """CRN: one fixed episode set per environment for the whole census (family train, index 1)."""
    return episodes_for(ENVS[env], CAMPAIGN_SEED, "train", 1, e)


def answers(manifest: dict, eps: list) -> List[Optional[int]]:
    """The answer vector: the first output word at every ask position, None when silent.
    Re-runs the evaluator's loop so the vector and the reward come from the SAME execution."""
    from proteus.foundry.vm import Player, Meter                            # noqa: PLC0415
    player = Player(manifest)
    out: List[Optional[int]] = []
    for ei, ep in enumerate(eps):
        st = player.fresh_state()
        rng = SplitMix64(seed_from("wse.vmrng", 0, ei))
        for ti, words in enumerate(ep.ticks):
            player.begin_tick(st)
            outs, _ = player.run_tick(st, [words], 1, rng, meter=Meter())
            if ti in ep.expected:
                out.append(outs[0][0] if outs[0] else None)
    return out


def displacement(a: List[Optional[int]], b: List[Optional[int]]) -> float:
    n = max(1, len(a))
    return sum(1 for x, y in zip(a, b) if x != y) / n


def region_of(parent: dict, op: str, args: dict) -> str:
    """Affordance category of the instruction the operator touched, read from the PARENT."""
    if op == "config_perturbation":
        return "MANIFEST"
    pos = None
    if "pos" in args:
        pos = args["pos"]
    elif "word" in args:
        pos = args["word"] // GR.IW
    elif "a" in args:
        pos = args["a"]
    elif "src" in args:
        pos = args["src"]
    if pos is None:
        return "UNKNOWN"
    g = parent["genome"]
    i = int(pos) * GR.IW
    if i < 0 or i >= len(g):
        return "UNKNOWN"
    return CATEGORY[g[i] % N_OPCODES]


def classify(child_ev: Dict[str, dict], parent_ev: Dict[str, dict], disp: float, undecodable: bool, env: str) -> dict:
    """D4-003 rules; precedence D0 > D2 > D7 > D6 > D5 > D4 > D3. Returns the label and the
    numbers the label was read from."""
    if undecodable:
        return {"label": "D0", "why": "manifest validation failed after the edit"}
    c, p = child_ev[env], parent_ev[env]
    r, rp = c["reward_per_ask"], p["reward_per_ask"]
    ev = {"reward": r, "parent_reward": rp, "answered_share": c["answered_share"], "displacement": disp}
    if c["answered_share"] == 0.0 or c.get("_constant_answer"):
        return {"label": "D2", "why": "no answer or one constant answer on every ask", **ev}
    if r > rp + BAND:
        return {"label": "D7", "why": "reward above parent + band on the parent environment", **ev}
    exapt = [o for o in OTHER_ENVS if o != env and child_ev[o]["reward_per_ask"] >= parent_ev[o]["reward_per_ask"] + BAND
             and child_ev[o]["reward_per_ask"] >= FLOOR]
    if exapt:
        return {"label": "D6", "why": "beats the parent by >= band and clears the floor on another environment", "exaptive_on": exapt, **ev}
    if abs(r - rp) <= BAND:
        return {"label": "D5", "why": "within the equivalence band", **ev}
    if r >= FLOOR:
        return {"label": "D4", "why": "viable, below parent - band", **ev}
    return {"label": "D3", "why": "below the viability floor" + ("" if disp > 0 else " (displacement 0)"), **ev}


def identity_ok(r: dict) -> bool:
    """The negative control: an identity edit must show displacement 0 and the parent's own
    reward on every environment. Its LABEL is whatever the parent's own would be (a degenerate
    parent yields D2 by construction), so the label is not the test."""
    return (r.get("displacement") == 0.0 and r.get("evals") is not None
            and all(abs(v["reward_per_ask"] - r["parent_evals"][k]) < 1e-12 for k, v in r["evals"].items()))


def eval_all(manifest: dict, eps: Dict[str, list]) -> Dict[str, dict]:
    out = {}
    for env, e in eps.items():
        r = evaluate(manifest, e, rng_seed=0, reward_mode="per_ask")
        # timing keys are the only non-deterministic content of evaluate(); the harness records
        # wall time at the attempt level, so rows stay a pure function of (manifest, episodes)
        r["meter"] = {k: v for k, v in r["meter"].items() if k not in ("wall_s", "cpu_s")}
        a = answers(manifest, e)
        vals = [x for x in a if x is not None]
        r["_answers"] = a
        r["_constant_answer"] = bool(vals) and len(set(vals)) == 1 and len(vals) == len(a)
        out[env] = r
    return out


def census_parent(job: dict) -> List[dict]:
    """All rows for one parent: 12 operators x draws, plus the two control edits."""
    p = job["parent"]
    org = job["organism_id"]
    stratum = job["stratum"]
    env = PARENT_ENV[stratum]
    eps = {k: episodes(k, job["E"]) for k in ENVS}
    pev = eval_all(p["manifest"] if "manifest" in p else p, eps)
    pm = p["manifest"] if "manifest" in p else p
    pdesc = structural_descriptor(pm)
    rows = []
    edits = [(op, r) for op in OPERATORS for r in range(1, job["draws"] + 1)]
    edits += [("control_identity", 0), ("control_randomize_all", 0)]
    for op, r in edits:
        rec = {"parent_id": org, "stratum": stratum, "parent_env": env, "operator": op, "draw": r,
               "parent_reward": pev[env]["reward_per_ask"], "parent_descriptor": pdesc,
               "parent_evals": {k: v["reward_per_ask"] for k, v in pev.items()},
               "parent_degenerate": pev[env]["answered_share"] == 0.0 or bool(pev[env].get("_constant_answer"))}
        undecodable = False
        args: dict = {}
        child = None
        if op == "control_identity":
            child = json.loads(json.dumps(pm))
            args = {"control": "identity"}
        elif op == "control_randomize_all":
            rng = SplitMix64(seed_from("c4.01.control", CAMPAIGN_SEED, org))
            child = json.loads(json.dumps(pm))
            child["genome"] = [rng.next_u32() if hasattr(rng, "next_u32") else rng.randint(0, (1 << 32) - 1) for _ in child["genome"]]
            args = {"control": "randomize_all", "k": len(child["genome"]) // GR.IW}
        else:
            rng = SplitMix64(seed_from("c4.01.edit", CAMPAIGN_SEED, org, op, r))
            try:
                child, oprec = GR.mutate(pm, rng, mate=None, name=op)
                args = oprec["args"]
                rec["len_before"], rec["len_after"] = oprec["len_before"], oprec["len_after"]
            except ManifestError as exc:
                undecodable = True
                rec["validation_error"] = str(exc)[:200]
        rec["args"] = args
        rec["applied"] = not undecodable and not ("noop" in args)
        rec["could_not_apply"] = "noop" in args
        rec["region"] = region_of(pm, op, args) if op in OPERATORS else "CONTROL"
        if child is not None and not undecodable:
            cev = eval_all(child, eps)
            disp = displacement(cev[env]["_answers"], pev[env]["_answers"])
            rec["evals"] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")} for k, v in cev.items()}
            rec["displacement"] = disp
            rec["statuses"] = cev[env]["statuses"]
            rec["ops_per_episode"] = cev[env]["ops_per_episode"]
            rec["child_descriptor"] = structural_descriptor(child)
            rec["child_digest"] = hashlib.sha256(json.dumps(child, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            rec["classification"] = classify(cev, pev, disp, False, env)
        else:
            rec["classification"] = classify({}, pev, 0.0, True, env)
        rec["D"] = rec["classification"]["label"]
        rows.append(rec)
    return rows


# ---------------------------------------------------------------- aggregation
def wilson(k: int, n: int, z: float = 1.96) -> tuple:
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (round(max(0.0, c - h), 4), round(min(1.0, c + h), 4))


def flow_table(rows: List[dict], key) -> dict:
    """P(Dk | key) with counts, applied counts and could-not-apply counts; D1 carries eligible 0."""
    out: Dict[str, dict] = {}
    for r in rows:
        k = key(r)
        g = out.setdefault(k, {"n": 0, "applied": 0, "could_not_apply": 0, "counts": Counter(), "disp": []})
        g["n"] += 1
        if r["could_not_apply"]:
            g["could_not_apply"] += 1
            continue
        g["applied"] += 1
        g["counts"][r["D"]] += 1
        if "displacement" in r:
            g["disp"].append(r["displacement"])
    for k, g in out.items():
        n = g["applied"]
        g["rates"] = {d: {"k": g["counts"].get(d, 0), "p": round(g["counts"].get(d, 0) / n, 4) if n else None, "band95": wilson(g["counts"].get(d, 0), n)}
                      for d in D_LABELS}
        g["rates"]["D1"]["eligible"] = 0
        g["rates"]["D1"]["reason"] = "total interpreter: no fatal operation exists (D4-002)"
        g["displacement_hist"] = _hist(g["disp"])
        g["displacement_mean"] = round(sum(g["disp"]) / len(g["disp"]), 4) if g["disp"] else None
        g["counts"] = dict(g["counts"])
        del g["disp"]
    return out


def _hist(xs: list) -> dict:
    bins = {"0": 0, "(0,0.25]": 0, "(0.25,0.5]": 0, "(0.5,0.75]": 0, "(0.75,1]": 0}
    for x in xs:
        if x == 0:
            bins["0"] += 1
        elif x <= 0.25:
            bins["(0,0.25]"] += 1
        elif x <= 0.5:
            bins["(0.25,0.5]"] += 1
        elif x <= 0.75:
            bins["(0.5,0.75]"] += 1
        else:
            bins["(0.75,1]"] += 1
    return bins


def tvd(a: dict, b: dict) -> float:
    return round(0.5 * sum(abs((a.get(d, {}).get("p") or 0) - (b.get(d, {}).get("p") or 0)) for d in D_LABELS), 4)


def pairwise_tvd(table: dict) -> dict:
    ops = [k for k in table if k in OPERATORS]
    out = {}
    for i, a in enumerate(ops):
        for b in ops[i + 1:]:
            out["%s|%s" % (a, b)] = tvd(table[a]["rates"], table[b]["rates"])
    return out


def group_rows(rows: List[dict]) -> List[dict]:
    """One harness row per (parent, operator) for the accounting machinery (arm = operator)."""
    by: Dict[tuple, list] = {}
    for r in rows:
        by.setdefault((r["parent_id"], r["operator"]), []).append(r)
    out = []
    for (pid, op), rs in sorted(by.items()):
        applied = [r for r in rs if r["applied"]]
        c = Counter(r["D"] for r in applied)
        n = len(applied)
        out.append({"parent_id": pid, "operator": op, "stratum": rs[0]["stratum"], "parent_env": rs[0]["parent_env"],
                    "draws": len(rs), "applied": n, "could_not_apply": sum(1 for r in rs if r["could_not_apply"]),
                    "loss_rate": (c["D0"] + c["D2"] + c["D3"]) / n if n else None,
                    "destroyed": (c["D2"] + c["D3"]) / n if n else None,
                    "neutral_rate": c["D5"] / n if n else None, "improved_rate": c["D7"] / n if n else None,
                    "exaptive_rate": c["D6"] / n if n else None, "viable_worse_rate": c["D4"] / n if n else None,
                    "identity_ok": (sum(1 for r in applied if identity_ok(r)) / n if n else None) if op == "control_identity" else None,
                    "parent_degenerate": rs[0].get("parent_degenerate"),
                    "displacement_mean": (sum(r.get("displacement", 0.0) for r in applied) / n) if n else None,
                    "D_counts": dict(c)})
    return out


# ---------------------------------------------------------------- main
def parents_from_population() -> List[dict]:
    d = json.loads((C4 / "STARTING_POPULATION.json").read_text(encoding="utf-8"))
    return [{"organism_id": o["organism_id"], "stratum": o["class"], "parent": o["manifest"]} for o in d["organisms"]]


def gate_is_green() -> bool:
    p = C4 / "LAUNCH_GATE_RECEIPT.json"
    if not p.exists():
        return False
    return bool(json.loads(p.read_text(encoding="utf-8")).get("campaign_may_start"))


def self_test(draws: int, e: int) -> int:
    """Machinery only: two synthetic foundry draws (seed 77, not the population), every
    operator, the two controls, the classifier's cheat control. Writes nothing under C4-01/."""
    from proteus.foundry import generate as G                                # noqa: PLC0415
    from archaeon.campaign2.c2base import FOUNDRY_C2                         # noqa: PLC0415
    ms = [o["manifest"] for o in G.generate(dict(FOUNDRY_C2, seed=77, n=2))]
    rows = []
    for i, m in enumerate(ms):
        rows += census_parent({"parent": m, "organism_id": "selftest-%d" % i, "stratum": "gen0_random", "draws": draws, "E": e})
    ident = [r for r in rows if r["operator"] == "control_identity"]
    rnd = [r for r in rows if r["operator"] == "control_randomize_all"]
    ok_ident = all(identity_ok(r) for r in ident)
    # cheat control: a copy of one row with reward forced to 1.0 must read D7
    r0 = next(r for r in rows if r["applied"] and r["operator"] in OPERATORS)
    cev = {k: dict(v, reward_per_ask=1.0 if k == r0["parent_env"] else v["reward_per_ask"], _constant_answer=False, answered_share=1.0) for k, v in r0["evals"].items()}
    pev = {k: dict(v) for k, v in r0["evals"].items()}
    pev[r0["parent_env"]]["reward_per_ask"] = r0["parent_reward"]
    cheat = classify(cev, pev, 0.5, False, r0["parent_env"])["label"]
    det = census_parent({"parent": ms[0], "organism_id": "selftest-0", "stratum": "gen0_random", "draws": draws, "E": e})
    same = json.dumps(det, sort_keys=True, default=str) == json.dumps([r for r in rows if r["parent_id"] == "selftest-0"], sort_keys=True, default=str)
    tbl = flow_table(rows, lambda r: r["operator"])
    rep = {"rows": len(rows), "identity_ok_all": ok_ident, "randomize_all_D": Counter(r["D"] for r in rnd),
           "cheat_reads_D7": cheat == "D7", "deterministic_rerun_identical": same,
           "D_by_operator": {k: v["counts"] for k, v in tbl.items()}, "could_not_apply": {k: v["could_not_apply"] for k, v in tbl.items()},
           "regions": Counter(r["region"] for r in rows)}
    print(json.dumps(rep, indent=1, default=str))
    return 0 if (ok_ident and cheat == "D7" and same) else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=DRAWS)
    ap.add_argument("--E", type=int, default=E)
    ap.add_argument("--procs", type=int, default=12)
    ap.add_argument("--dry-run", action="store_true", help="synthetic parents (never the 57), no engine")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    from archaeon import workspace                                          # noqa: PLC0415
    workspace.assert_not_canonical("C4-01 census")
    if a.self_test:
        return self_test(2, 8)
    if not a.dry_run and not gate_is_green():
        print("REFUSED: the Campaign 4 launch gate is not green (archaeon/campaign4/LAUNCH_GATE_RECEIPT.json). "
              "Run python -m archaeon.campaign4.launch_gate; nothing here runs while it is RED.")
        return 3
    from archaeon.campaign4.c4harness import Experiment4                    # noqa: PLC0415

    class Census(Experiment4):
        ID = "C4-01"
        TITLE = "damage-boundary census"
        PARENTS = ["C3-SFE-01", "C3-SFE-03", "C3-SFE-04"]
        ARM_FIELD = "operator"
        METRICS = ("loss_rate", "neutral_rate", "improved_rate", "exaptive_rate", "displacement_mean")

    X = Census(dry_run=a.dry_run, procs=a.procs)
    design = (C4 / "C4-01" / "DESIGN.md").read_text(encoding="utf-8")
    X.seal({
        "question": "Where does the frozen substrate destroy variation? For each of the 12 grammar operators applied once to each of the 57 "
                    "starting program variants (8 draws), the distribution over D0..D7 and the behavioral displacement conditional on executing.",
        "parent_evidence": "Campaigns 1-3: repeated boundaries where edits stop producing informative phenotypes (unreachable summits, inert shelves). "
                           "The interpreter is TOTAL (D4-002): D1 cannot fire; D0 is post-edit validation only.",
        "why_this_slot": "Establishes the actual damage boundary before any attempt to move it (C4-03, C4-07, C4-08); fills the first column of the damage geometry map.",
        "assay_capability_requirement": "controls: identity edit 57/57 D5 with displacement 0; whole-genome randomization >= 45/57 destroyed (D2 or D3); "
                                        "the D7 detector reads D7 on a hand-set reward (cheat); one parent's rows reproduce byte-for-byte on rerun",
        "positive_control": "control_randomize_all arm: destroyed (D2+D3 share) >= 1.0 on >= 45 of 57 parents",
        "reachability_estimate": {"note": "not a search; no reachability lookup applies (evaluation census)"},
        "arms": list(OPERATORS) + ["control_identity", "control_randomize_all"],
        "crn_policy": "one fixed episode set per environment (family train, index 1, E=%d) shared by every parent and child; edits seeded from "
                      "(campaign_seed, organism_id, operator, draw)" % a.E,
        "budget": {"parents": 57, "operators": len(OPERATORS), "draws": a.draws, "environments": list(ENVS), "E": a.E,
                   "floor": FLOOR, "band": BAND, "parent_env": PARENT_ENV, "other_envs": list(OTHER_ENVS)},
        "primary_observable": "P(Dk | operator), P(Dk | operator, stratum), P(Dk | region) with Wilson bands and eligible counts; displacement histogram "
                              "by operator; pairwise total-variation distance between operators' D-distributions",
        "claim_ceiling": "a measured map at 8 draws per (parent, operator) on one frozen substrate; no mechanism; no evolvability claim",
        "falsification_condition": "every operator pair has TVD < 0.05 (all classes look alike), or region UNKNOWN for > 20% of applied edits, "
                                   "or D0 > 50% of edits (the instrument cannot say where loss occurs) -> NEGATIVE, recorded, nothing fixed in C4-01",
        "kill_condition": "a control fails -> INSTRUMENT_INVALID; the slot stops and the defect is recorded",
        "typed_failure_conditions": ["INSTRUMENT_INVALID", "UNDERPOWERED", "ENGINE_FAILURE / INSTRUMENT_FAILURE"],
        "expected_machine_telemetry": ["flow table D0..D7 by operator / stratum / region", "displacement histograms", "per-child raw evaluate() dicts on 4 environments",
                                       "structural descriptors before/after", "operator args with touched positions"],
        "machine_changes_exercised": ["campaign-4 harness (D4-001)", "classifier D4-003", "total-interpreter accounting (D1 eligible 0)"],
        "replacement_condition": "none: first slot",
        "ancestry": "original (queue slot 1)",
        "design_digest": "sha256:" + hashlib.sha256(design.replace("\r\n", "\n").encode("utf-8")).hexdigest(),
        "decl": {"n_min": 57, "positive_control": {"arm": "control_randomize_all", "metric": "destroyed", "min": 1.0, "min_rows": 45},
                 "readout_control": {"arm": "control_identity", "metric": "identity_ok", "chance": 0.0, "min_above": 0.99},
                 "primary": {"treatment": "randomization", "control": "operand_perturbation", "metric": "loss_rate", "min_effect": 0.05}},
    })
    X.decision("D4-001..D4-004 applied; the census refuses while the gate is RED; controls are rows in the same table")
    parents = parents_from_population() if not a.dry_run else [
        {"organism_id": "dry-%d" % i, "stratum": "gen0_random", "parent": m}
        for i, m in enumerate(o["manifest"] for o in __import__("proteus.foundry.generate", fromlist=["generate"]).generate(
            dict(__import__("archaeon.campaign2.c2base", fromlist=["FOUNDRY_C2"]).FOUNDRY_C2, seed=77, n=3)))]
    X.open("cmp4-c4-01")
    wid = X.world("census", "ISOLATED", use_group=False)
    X.publish_prereg(wid)
    t0 = time.time()
    jobs = [dict(p, draws=a.draws, E=a.E) for p in parents]
    per_parent = X.pool_map(census_parent, jobs, "census_s")
    rows = [r for rs in per_parent for r in rs]
    grouped = group_rows(rows)
    # engine records: one observation per (parent, operator) group with its draws inside
    for g in grouped:
        rs = [r for r in rows if r["parent_id"] == g["parent_id"] and r["operator"] == g["operator"]]
        content = {"group": g, "children": [{k: r.get(k) for k in ("draw", "D", "applied", "could_not_apply", "region", "displacement", "args",
                                                                     "len_before", "len_after", "child_digest", "classification")} for r in rs],
                   "label": "C4-01 census row; the raw evaluate() dicts are in rows.json"}
        X.record(wid, g, {"parent": g["parent_id"], "operator": g["operator"]}, content,
                 "SURVIVED" if g["applied"] else "INCONCLUSIVE", key_parts=(g["parent_id"][:16], g["operator"]))
    tables = {"by_operator": flow_table(rows, lambda r: r["operator"]),
              "by_operator_stratum": flow_table(rows, lambda r: "%s|%s" % (r["operator"], r["stratum"])),
              "by_region": flow_table(rows, lambda r: r["region"]),
              "by_stratum": flow_table(rows, lambda r: r["stratum"])}
    tables["pairwise_tvd"] = pairwise_tvd(tables["by_operator"])
    tables["min_pairwise_tvd"] = min(tables["pairwise_tvd"].values()) if tables["pairwise_tvd"] else None
    tables["max_pairwise_tvd"] = max(tables["pairwise_tvd"].values()) if tables["pairwise_tvd"] else None
    tables["region_unknown_share"] = round(sum(1 for r in rows if r["applied"] and r["region"] == "UNKNOWN") / max(1, sum(1 for r in rows if r["applied"])), 4)
    tables["d0_share"] = round(sum(1 for r in rows if r["D"] == "D0") / max(1, len(rows)), 4)
    tables["d1_eligible"] = 0
    tables["wall_s"] = round(time.time() - t0, 1)
    X.att.write("FLOW_TABLES.json", tables)
    X.att.write("children.json", rows)
    # info_kind must be one of the engine's five (artifact/failure/hypothesis/observation/success);
    # attempt a01 failed here on "measurement" (HTTP 422) and is preserved beside this rerun
    X.publish(wid, "flow_tables", "cmp4.flow_tables.v1", tables, {"info_kind": "artifact", "label": "C4-01 census"})
    out = X.close(grouped, meas_extra={"tables_digest": hashlib.sha256(json.dumps(tables, sort_keys=True, default=str).encode()).hexdigest()},
                  addendum={"falsifying_outcome_check": json.dumps({"max_pairwise_tvd": tables["max_pairwise_tvd"], "region_unknown_share": tables["region_unknown_share"],
                                                                     "d0_share": tables["d0_share"]})})
    print(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
