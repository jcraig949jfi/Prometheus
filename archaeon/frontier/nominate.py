"""Archaeon's hand on the queue (DF-013): push a spec, a family module's specs, or a pursuit multiplier -- as data the scheduler
honours without asking.

    python -m archaeon.frontier.nominate spec <path.json> --pool EXPLOITATION --priority 3.0 --lineage LIN-xxx [--note ...]
    python -m archaeon.frontier.nominate design <module>            # runs archaeon.frontier.design.<module>.emit() and queues what it returns
    python -m archaeon.frontier.nominate pursue --lineage LIN-xxx --multiplier 4.0 [--family C5-flat --multiplier 2.0]
    python -m archaeon.frontier.nominate status
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
for p in (REPO, REPO / "SerendipityFoundry" / "SerendipityFoundryClient"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from archaeon.frontier import specs as SP                                    # noqa: E402
from archaeon.frontier.registry import Registry                              # noqa: E402
from archaeon.frontier.queues import Queues                                  # noqa: E402

HERE = Path(__file__).resolve().parent
PURSUE = HERE / "pursue.json"


def queue_specs(reg: Registry, q: Queues, lineage_id: str, items: list, pool: str, priority: float, note: str) -> list:
    """items: list of (spec, trigger). Adds transformations to the lineage and queue items; returns ids."""
    seen = {t["id"] for t in reg.get(lineage_id)["transformations"]}
    trs = []
    for spec, trigger in items:
        spec = SP.validate_spec(spec)
        if spec["experiment_id"] in seen:
            continue
        seen.add(spec["experiment_id"])
        trs.append({"id": spec["experiment_id"], "dims": spec.get("dims", ["designed"]), "from": spec.get("from_", "-"), "to": spec.get("to_", trigger), "budget_evaluations": spec["budget"]["evaluations"],
                    "status": "PENDING", "trigger": trigger, "spec": spec, "pool": pool})
    if trs:
        reg.add_transformations(lineage_id, trs)
        for i, t in enumerate(trs):
            q.push(pool, lineage_id=lineage_id, transformation_id=t["id"], priority=priority - 0.001 * i, lane=t["spec"]["provenance"]["lane"], budget_evaluations=t["budget_evaluations"], note=note)
        reg.event(lineage_id, "DESIGNED", {"n": len(trs), "pool": pool, "priority": priority, "note": note, "ids": [t["id"] for t in trs][:20]})
    return [t["id"] for t in trs]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd")
    a1 = sub.add_parser("spec"); a1.add_argument("path"); a1.add_argument("--pool", default="EXPLOITATION"); a1.add_argument("--priority", type=float, default=2.0); a1.add_argument("--lineage", required=True); a1.add_argument("--note", default="")
    a2 = sub.add_parser("design"); a2.add_argument("module"); a2.add_argument("--priority", type=float, default=None)
    a3 = sub.add_parser("pursue"); a3.add_argument("--lineage", default=None); a3.add_argument("--family", default=None); a3.add_argument("--multiplier", type=float, default=2.0); a3.add_argument("--note", default="")
    sub.add_parser("status")
    a = ap.parse_args(argv)
    reg = Registry(); q = Queues()
    if a.cmd == "spec":
        spec = json.loads(Path(a.path).read_text(encoding="utf-8"))
        ids = queue_specs(reg, q, a.lineage, [(spec, "nominated")], a.pool, a.priority, a.note); print(json.dumps({"queued": ids}))
    elif a.cmd == "design":
        mod = importlib.import_module("archaeon.frontier.design." + a.module)
        out = mod.emit(reg, q, priority=a.priority)
        print(json.dumps(out, indent=1, default=str))
    elif a.cmd == "pursue":
        pt = json.loads(PURSUE.read_text(encoding="utf-8")) if PURSUE.exists() else {"lineages": {}, "families": {}, "history": []}
        if a.lineage:
            pt["lineages"][a.lineage] = a.multiplier
        if a.family:
            pt["families"][a.family] = a.multiplier
        pt["history"].append({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "lineage": a.lineage, "family": a.family, "multiplier": a.multiplier, "note": a.note})
        PURSUE.write_text(json.dumps(pt, indent=1) + "\n", encoding="utf-8", newline="\n"); print(json.dumps(pt["lineages"]), json.dumps(pt["families"]))
    else:
        print(json.dumps({"registry": reg.summary(), "queues": q.status(), "pursue": json.loads(PURSUE.read_text(encoding="utf-8")) if PURSUE.exists() else {}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
