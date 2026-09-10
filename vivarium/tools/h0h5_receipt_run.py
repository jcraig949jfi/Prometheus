"""One real artifact-consuming execution, in a DEVELOPMENT schema and engine.

This is the receipt run for H0-H5 iteration 1. It is a script rather than a
test because its output is evidence with identifiers in it: a world, an
artifact, an experiment, a work item, an observation, a ledger anchor and a
PEW encounter, all real, none of them from a fixture that tidies itself away.

    python SerendipityFoundry/SerendipityFoundryEngine/serve.py \\
        --db <tmp>/dev.sqlite --host 127.0.0.1 --port 8899 &
    VIV_SCHEMA=viv_dev_h0h5 VIV_PEW_NAMESPACE=test \\
        python tools/h0h5_receipt_run.py --sfe http://127.0.0.1:8899

It refuses to run against the production queue schema or the production PEW
namespace. Not because it would break anything -- because a receipt produced by
a run that quietly touched production would be worth nothing.
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "tests"))
sys.path.insert(0, str(HERE.parent / "SerendipityFoundry"
                       / "SerendipityFoundryClient"))

from artifact_fixtures import input_set, probe_spec     # noqa: E402
from viv import artifacts as _a                          # noqa: E402
from viv import db as _db                                # noqa: E402
from viv import pew as _pew                              # noqa: E402
from viv import queue as _q                              # noqa: E402
from viv.loop import Vivarium                            # noqa: E402
from viv.runner import SfeRunner                         # noqa: E402

ITEMS = [[0, 0, 1], [1, 1, 0], [1, 0, 1], [0, 1, 0]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sfe", required=True, help="DEVELOPMENT engine base url")
    ap.add_argument("--out", default=None, help="write the receipt JSON here")
    args = ap.parse_args()

    cfg = _db.load_config()
    schema = cfg["schema"]
    if schema in ("viv",):
        print("refusing: VIV_SCHEMA is the production register", file=sys.stderr)
        return 2
    if cfg.get("pew_namespace") == "prod":
        print("refusing: VIV_PEW_NAMESPACE is prod", file=sys.stderr)
        return 2
    if "192.168" in args.sfe:
        print("refusing: --sfe looks like the production engine",
              file=sys.stderr)
        return 2

    from sfclient import EngineClient
    client = EngineClient(args.sfe)
    client.register("vivarium-h0h5-receipt-%s" % uuid.uuid4().hex[:6])
    version = client.version()

    conn = _db.connect()
    _db.apply_migrations(conn, target_schema=schema)

    # -- the producer creates a real typed artifact ------------------------
    sid = client.create_session("h0h5-receipt-producer")
    pw = client.create_world(sid, "h0h5-producer-%s" % uuid.uuid4().hex[:8],
                             seed_root=20260909,
                             sharing_policy="EXPLICIT_IMPORT_ONLY")
    producer_world = pw["world_id"]
    client.start(producer_world)
    _obj, raw, slot = input_set(ITEMS)
    created = client.artifact(producer_world, "failure_input_set", raw)
    assert created["blob_hash"] == slot["digest"]

    # -- the sealed request ------------------------------------------------
    encounter = "h0h5-receipt-%s" % uuid.uuid4().hex[:12]
    spec = probe_spec(slot, reduction="xor_positional",
                      pew={"encounter_id": encounter, "players": [],
                           "world_binding_id": encounter})
    eid = _q.enqueue(
        conn, created_by="vivarium:h0h5-iteration-1",
        source_reason="the loader vertical slice: one real artifact consumed",
        source_evidence={"design": "H0-H5 v0.1", "contract": "C1/C3/C5"},
        experiment_spec=spec, schema=schema,
        artifact_locators={slot["digest"]: {
            "source_world": producer_world,
            "source_artifact": created["artifact_id"]}})
    conn.commit()

    pew_client = None
    if cfg.get("pew_token") and cfg.get("pew_base_url"):
        pew_client = _pew.PewClient(cfg["pew_base_url"], cfg["pew_token"],
                                    machine=cfg.get("machine", "M1"),
                                    agent="vivarium",
                                    namespace=cfg["pew_namespace"])

    runner = SfeRunner(base_url=args.sfe, token=client.token,
                       client_id=getattr(client, "client_id", None),
                       worker_id="vivarium@h0h5-receipt", log=print)
    viv = Vivarium(worker_id="vivarium@h0h5-receipt", schema=schema,
                   runner=runner, pew_client=pew_client, log=print)
    report = viv.tick(conn)
    conn.commit()

    row = _q.get(conn, eid, schema=schema)
    summary = row["result_summary"] or {}
    receipt = {
        "outcome": report.outcome,
        "queue": {"schema": schema, "experiment_id": str(eid),
                  "status": row["status"], "spec_hash": row["spec_hash"]},
        "engine": {"base_url": args.sfe, **version},
        "producer": {"world_id": producer_world,
                     "artifact_id": created["artifact_id"],
                     "blob_hash": created["blob_hash"],
                     "bytes": len(raw)},
        "execution": {k: summary.get(k) for k in
                      ("world_id", "world_name", "exp_id", "work_id", "obs_id",
                       "run_id", "outcome")},
        "anchor": summary.get("anchor"),
        "load_receipt": summary.get("load_receipt"),
        "resources": summary.get("resources"),
        "enforcement": summary.get("enforcement"),
        "result": (summary.get("result") or {}).get("repeats", [{}])[0]
                  .get("result"),
        "pew": {k: (summary.get("pew") or {}).get(k) for k in
                ("write_outcome", "recorded_in_sfe", "indexed_in_pew",
                 "pew_reference")},
        "pew_namespace": cfg.get("pew_namespace"),
    }
    blob = json.dumps(receipt, indent=2, default=str)
    print(blob)
    if args.out:
        Path(args.out).write_text(blob + "\n", encoding="utf-8")
    conn.close()
    return 0 if report.outcome == "EXECUTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
