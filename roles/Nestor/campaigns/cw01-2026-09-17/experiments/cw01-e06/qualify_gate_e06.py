"""Q16 HARD GATE for cw01-e06: a world must EARN admission before compute is spent.

Three preconditions, all measured before any evolutionary run of the experiment proper:

  P1  NON-DEGENERATE   every reuse band produces a target that actually varies over its
                       own input domain. The pre-fix generator emitted a CONSTANT target
                       at reuse=0.50 (1 distinct output over 400 draws), which makes
                       solve-rates meaningless.
  P2  TWO-SIDED        Delta(r) = F_TREE(r) - F_TAPE(r) must CHANGE SIGN across the
                       reuse bands of ONE substrate-neutral generator. It is not enough
                       that some TREE-friendly world and some TAPE-friendly world exist
                       somewhere; comparative advantage must be a property of the
                       environment axis.
  P3  MUTUALLY         each substrate must invade the other when rare, against an
      INVASIBLE        EVOLVED RESIDENT at equilibrium. Coexistence is unreachable
                       otherwise, and design requirement 4 is violated.

THE GATE MUST BE SHOWN REFUSING.

The pre-fix world - targets generated as depth-3 expression trees, one substrate's
native form - is retained as an adversarial FIXTURE and run through the same gate. It
must be REFUSED. A gate that has only ever admitted the world it was written alongside
is not evidence; that is the guardproof doctrine applied to a world rather than to a
guard.

AND THE GATE IS NOT TUNED UNTIL IT ADMITS. If the redesigned world is also refused,
that is the finding and it is recorded as a refusal, not as a reason to relax P1-P3.

CW01-D046: roots discovered by marker, never by counting parents.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


_bootstrap_lib()
sys.path.insert(0, str(HERE))
import repopath as RP          # noqa: E402
import seeds as S              # noqa: E402
import world_e06 as W          # noqa: E402

CAMPAIGN = RP.find_campaign_root(HERE)


def delta_r(cfg, aid, targets, n_probe=40, n_items=96):
    """Delta(r) = TREE solve rate - TAPE solve rate, per reuse band.

    Measured on RANDOM genomes so this reflects the environment's comparative
    advantage, not a search outcome. Both substrates see items drawn from the SAME
    band, so the only thing varying is the environment axis.
    """
    tol = cfg["sharing"]["tolerance"]
    r = np.random.Generator(np.random.PCG64(S.seed(aid, "dr_pop", 0)))
    pop = {s: [W.seed_genome(cfg, r, s, s) for _ in range(n_probe)] for s in ("TREE", "TAPE")}
    rows = []
    for t in targets:
        rng = np.random.Generator(np.random.PCG64(S.seed(aid, "dr_items|%s" % t.get("reuse_target"), 0)))
        items = W.items_for_band(cfg, rng, t, n_items)
        rate = {s: float(np.mean([sum(W.solved_mask(g, cfg, items, tol)[0]) / len(items)
                                  for g in pop[s]])) for s in ("TREE", "TAPE")}
        rows.append({"reuse_target": t.get("reuse_target"),
                     "reuse_measured": t.get("reuse_measured"),
                     "tree_cost": t.get("tree_cost"), "tape_cost": t.get("tape_cost"),
                     "distinct_outputs": t.get("distinct_outputs"),
                     "F_TREE": rate["TREE"], "F_TAPE": rate["TAPE"],
                     "delta": rate["TREE"] - rate["TAPE"]})
    return rows


def run_gate(cfg, aid, targets, label, gens_resident=40, gens_invade=20, n_org=96):
    degenerate = [t.get("reuse_target") for t in targets if t.get("degenerate")]
    p1 = not degenerate

    rows = delta_r(cfg, aid, targets)
    deltas = [x["delta"] for x in rows]
    p2 = (max(deltas) > 0) and (min(deltas) < 0)

    inv = W.invasion_analysis(cfg, S.seed, aid, gens_resident=gens_resident,
                              gens_invade=gens_invade, n_org=n_org, target=targets)
    p3 = inv["mutually_invasible"]

    reasons = []
    if not p1:
        reasons.append("degenerate bands %s" % degenerate)
    if not p2:
        reasons.append("Delta(r) never changes sign (range %+.4f..%+.4f)" % (min(deltas), max(deltas)))
    if not p3:
        reasons.append(inv["verdict"])
    return {"world": label, "P1_non_degenerate": p1, "P2_two_sided": p2,
            "P3_mutually_invasible": p3, "admitted": bool(p1 and p2 and p3),
            "delta_table": rows, "invasion": inv["directions"],
            "reasons": reasons or ["all three preconditions met"]}


def main():
    print("########## cw01-e06 Q16 HARD GATE ##########")
    cfg = json.loads((HERE / "WORLD.json").read_text(encoding="utf-8"))
    aid = cfg["attempt_id"]

    print("\n-- building targets --")
    new_targets = W.attempt_target(cfg, S.seed)
    for t in new_targets:
        print("   band %.2f | measured reuse %.2f | tree_cost %3d vs tape_cost %2d | distinct %d%s"
              % (t["reuse_target"], t["reuse_measured"], t["tree_cost"], t["tape_cost"],
                 t["distinct_outputs"], "  DEGENERATE" if t["degenerate"] else ""))
    legacy = [{"reuse_target": None, "reuse_measured": None, "tree_cost": None,
               "tape_cost": None, "distinct_outputs": None, "degenerate": False,
               "graph": W.legacy_tree_target(cfg, S.seed)}]

    results = {}
    for label, tg in (("LEGACY_tree_target (adversarial fixture)", legacy),
                      ("REDESIGNED_operation_graph", new_targets)):
        print("\n-- gate on %s --" % label)
        res = run_gate(cfg, aid, tg, label)
        results[label] = res
        for x in res["delta_table"]:
            print("   r=%s  F_TREE %.4f  F_TAPE %.4f  delta %+.4f"
                  % (x["reuse_target"], x["F_TREE"], x["F_TAPE"], x["delta"]))
        for d, v in res["invasion"].items():
            print("   %-18s seeded %.3f -> %.3f  invaded=%s" % (d, v["seeded"], v["final"], v["invaded"]))
        print("   P1 %s | P2 %s | P3 %s  =>  %s"
              % (res["P1_non_degenerate"], res["P2_two_sided"], res["P3_mutually_invasible"],
                 "ADMIT" if res["admitted"] else "REFUSE"))
        for why in res["reasons"]:
            print("     - %s" % why)

    legacy_res = results["LEGACY_tree_target (adversarial fixture)"]
    new_res = results["REDESIGNED_operation_graph"]
    gate_proven = not legacy_res["admitted"]

    print("\n== gate credibility ==")
    print("   legacy world REFUSED (gate can fire): %s" % gate_proven)
    print("   redesigned world admitted           : %s" % new_res["admitted"])
    verdict = ("GATE PROVEN AND WORLD ADMITTED" if (gate_proven and new_res["admitted"]) else
               "GATE PROVEN, WORLD STILL REFUSED" if gate_proven else
               "GATE NOT CREDIBLE - it admitted the known-broken world")
    print("   %s" % verdict)
    if gate_proven and not new_res["admitted"]:
        print("   -> recorded as a refusal. The gate is NOT relaxed to admit.")

    (HERE / "QUALIFY_GATE.json").write_text(json.dumps(
        {"campaign_id": "cw01-2026-09-17", "experiment_id": "cw01-e06", "attempt_id": aid,
         "preconditions": {"P1": "every reuse band non-degenerate",
                           "P2": "Delta(r) changes sign across bands of ONE generator",
                           "P3": "mutual invasibility against evolved residents"},
         "results": results, "gate_can_refuse": gate_proven,
         "world_admitted": new_res["admitted"], "verdict": verdict,
         "_rule": "the gate is never tuned until it admits; a refusal is a finding"},
        indent=1, default=str), encoding="utf-8")
    return 0 if (gate_proven and new_res["admitted"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
