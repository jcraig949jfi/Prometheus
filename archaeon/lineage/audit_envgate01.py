"""ENVGATE-01 genetic-attribution AUDIT (directive A4) -- an adjudication artifact; ENVGATE-01's frozen endpoint is NOT recomputed.

Replays, on the attributed core, every ENVGATE-01 (block, arm) world that contains a historically established lineage whose founder the
frozen ruler calls a non-copier (the host-label candidates), plus the takeover worlds. A replay is ADMITTED only if its parent-chain
establishments equal the historical record for that world exactly. For each historical established lineage it records which GENETIC
lineages (glins) its members belonged to at its persistence check; then answers:
  distinct established genetic lineages; host labels attached to already-established genetic material; distinct reproductive genomes
  originated; genomes amplified through host-mediated execution; takeover worlds collapsing into few genetic sweeps.
Historical establishments in worlds not replayed (copier-founded only, no host-label candidate) are counted as distinct genetic lineages
under a stated assumption (each is a different arrival reproducing by self-copy), reported separately.
    python -m archaeon.lineage.audit_envgate01 --replay --workers 4 ; python -m archaeon.lineage.audit_envgate01 --report
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from archaeon.envgate import mechanism as M1
from archaeon.lineage import core as LC

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
E1 = REPO / "archaeon" / "envgate"
OUT = E1 / "genetic_audit"
SCHED = {"K_chambers": 2048, "dwell": 64, "refills": 1024}


class AuditWorld(LC.World):
    """Observation-only: at each parent-chain persistence check, record the glin composition of that lineage's living members."""
    def step(self, epoch, memo):
        due = list(self.lin_checks.get(epoch, []))
        super().step(epoch, memo)
        if due:
            if not hasattr(self, "lin_glins"): self.lin_glins = {}
            for f in due:
                c = Counter(self.glin[i] for i in range(LC.N) if self.genomes[i] is not None and self.lin[i] == f)
                self.lin_glins[f] = dict(c)


def worlds_to_replay():
    L = json.loads((E1 / "LINEAGES.json").read_text(encoding="utf-8"))["lineages"]
    s = {(r["block"], r["arm"]) for r in L if r.get("label")}
    return sorted(s)


def replay(block, arm):
    import archaeon.lineage.assay_block as AB
    orig = AB.World; AB.World = AuditWorld
    try:
        r = AB.run_block("envgate", block, SCHED, {arm: M1.ARMS[arm]}, keep_worlds=True)
    finally:
        AB.World = orig
    w = r["arms"][arm]["_world"]; hist = json.loads((E1 / "runs" / ("block_%02d.json" % block)).read_text(encoding="utf-8"))["arms"][arm]["established_arrivals"]
    pc = r["arms"][arm]["parent_chain_established_arrivals"]
    arr2f = {lr["arrival"]: f for f, lr in w.lin_rec.items()}
    comp = {a: getattr(w, "lin_glins", {}).get(arr2f.get(a), {}) for a in hist}
    gl = {g: {k: st[k] for k in ("root", "origin", "arrival", "births", "births_hosted", "births_self", "peak", "max_ggen")} | {"n_hosts": len(st["hosts"])}
          for g, st in w.gl.items() if st["births"] >= 3}
    res = {"block": block, "arm": arm, "admitted": pc == hist, "historical_established_arrivals": hist, "replay_parent_chain": pc,
           "genetic_established": w.genetic_establishments(), "lineage_glin_composition_at_check": {str(a): {str(k): v for k, v in c.items()} for a, c in comp.items()},
           "glins": {str(k): v for k, v in gl.items()}, "births_by_mechanism": dict(w.births_mech), "final_pop": r["arms"][arm]["final_ecology_pop"],
           "taint_calls": w.taint_calls, "fast_calls": w.fast_calls}
    OUT.mkdir(exist_ok=True); (OUT / ("replay_b%02d_%s.json" % (block, arm))).write_text(json.dumps(res, default=str) + "\n", encoding="utf-8", newline="\n")
    return {k: res[k] for k in ("block", "arm", "admitted")}


def report():
    L = json.loads((E1 / "LINEAGES.json").read_text(encoding="utf-8"))["lineages"]
    rep = {(r["block"], r["arm"]): json.loads((OUT / ("replay_b%02d_%s.json" % (r["block"], r["arm"]))).read_text(encoding="utf-8"))
           for r in L if (OUT / ("replay_b%02d_%s.json" % (r["block"], r["arm"]))).exists()}
    admitted = {k: v for k, v in rep.items() if v["admitted"]}
    rows = []; distinct = set(); host_labels = 0; unresolved = 0
    for r in L:
        k = (r["block"], r["arm"])
        if k in admitted:
            comp = admitted[k]["lineage_glin_composition_at_check"].get(str(r["arrival"]), {})
            if not comp: unresolved += 1; rows.append(dict(block=k[0], arm=k[1], arrival=r["arrival"], status="UNRESOLVED")); continue
            dom = max(comp, key=comp.get); g = admitted[k]["glins"].get(dom, {})
            own = g.get("arrival") == r["arrival"]
            if not own: host_labels += 1
            distinct.add((k, dom)); rows.append(dict(block=k[0], arm=k[1], arrival=r["arrival"], dominant_glin=dom, glin_root=g.get("root"), glin_arrival=g.get("arrival"),
                                                   status="OWN_GENOME" if own else "HOST_LABEL_ON_OTHER_GENOME", members=comp))
        else:
            distinct.add((k, "arrival:%d" % r["arrival"])); rows.append(dict(block=k[0], arm=k[1], arrival=r["arrival"], status="NOT_REPLAYED_ASSUMED_OWN_GENOME"))
    originated = sum(1 for v in admitted.values() for g in v["glins"].values() if g["root"] == "origination" and g["births"] >= 1)
    amplified = sum(1 for v in admitted.values() for g in v["glins"].values() if g["births_hosted"] > 0)
    tk = {"%d_%s" % k: {"historical_established": len(v["historical_established_arrivals"]), "distinct_genetic_lineages_behind_them": len({d for (kk, d) in distinct if kk == k}),
                        "genetic_establishments_in_replay": len(v["genetic_established"])} for k, v in admitted.items() if v["final_pop"] >= 0.9 * 128}
    out = {"schema": "archaeon.envgate01.genetic_audit.v1", "status": "ADJUDICATION ARTIFACT -- not a replacement for RESULTS.json", "historical_established": len(L),
           "replayed_worlds": len(rep), "admitted_worlds": len(admitted), "not_admitted": [f"{k[0]}_{k[1]}" for k, v in rep.items() if not v["admitted"]],
           "distinct_established_genetic_lineages": len(distinct), "host_labels_on_other_genetic_material": host_labels, "unresolved": unresolved,
           "distinct_reproductive_genomes_originated_in_replayed_worlds": originated, "genomes_amplified_by_host_execution_in_replayed_worlds": amplified,
           "hosted_births_in_replayed_worlds": sum(v["births_by_mechanism"].get("HOST_EXECUTION", 0) for v in admitted.values()),
           "takeover_worlds": tk, "rows": rows}
    (E1 / "GENETIC_AUDIT_2026-09-24.json").write_text(json.dumps(out, indent=1, default=str) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, default=str)); return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--replay", action="store_true"); ap.add_argument("--report", action="store_true"); ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    if a.replay:
        ws = worlds_to_replay(); print("replaying", ws, flush=True)
        with ProcessPoolExecutor(a.workers) as ex:
            for fu in as_completed([ex.submit(replay, b, arm) for b, arm in ws]): print(json.dumps(fu.result()), flush=True)
    if a.report: report()
