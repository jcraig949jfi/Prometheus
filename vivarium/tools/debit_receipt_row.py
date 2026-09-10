"""ONE artifact-bearing row, end to end on the LIVE schema-7 engine.

The evidence Archaeon asked for before re-issuing the 48: a row that consumes a
real artifact through the loader on an engine with no reservation endpoint, and
whose load receipt says `allowance_mechanism` = debit. It reuses the phase-2
locators already published, so the bytes are the ones the campaign will
consume, not a fixture that resembles them.

It enqueues into the PRODUCTION register under a distinct candidate set, runs
exactly one tick, and prints the receipt. It does not touch Archaeon's rows.
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
REPO = HERE.parent
for extra in (str(HERE), str(REPO), str(HERE / "tests"),
              str(REPO / "SerendipityFoundry" / "SerendipityFoundryClient")):
    if extra not in sys.path:
        sys.path.insert(0, extra)

from viv import db as _db                                     # noqa: E402
from viv import identity as _identity                         # noqa: E402
from viv import queue as _q                                   # noqa: E402
from viv.loop import Vivarium                                 # noqa: E402
from viv.runner import SfeRunner                              # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--locators", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    loc_doc = json.loads(Path(args.locators).read_text(encoding="utf-8"))
    locators = loc_doc["locators"]
    published = {p["digest"]: p for p in loc_doc["published"]}

    # A failure_input_set, so the row exercises the loader the way the campaign
    # rows do. The component_library is the instrument control and is not what
    # the 48 failing rows tripped on.
    pack = None
    for digest, meta in sorted(published.items()):
        if meta["artifact_type"] == "failure_input_set":
            pack = (digest, meta)
            break
    if pack is None:
        print("no failure_input_set in the locator file", file=sys.stderr)
        return 2
    digest, meta = pack

    slot = {"digest": digest, "artifact_type": "failure_input_set",
            "schema_version": "1", "codec": "canonical-json-v1",
            "expected_bytes": meta["bytes"],
            "interface_id": "boolean-inputs-v1"}
    spec = {
        "spec_version": 3, "world": {"seed_root": 20260910},
        "hypothesis": "the loader pays for and consumes a real phase-2 pack on "
                      "an engine that has no reservation endpoint",
        "prediction": None,
        "work": {"kind": "artifact_probe_v1",
                 "payload": {"failure_inputs": slot,
                             "reduction": "xor_positional"}},
        "outcome_rule": {"field": "executor", "op": "==",
                         "value": "artifact_probe_v1", "if_true": "SURVIVED",
                         "if_false": "FALSIFIED",
                         "if_indeterminate": "INCONCLUSIVE",
                         "aggregate": "first"},
        "pew": None,
        "repeat": {"count": 1, "order": "sequential",
                   "seed_derivation": "constant", "state": "reset",
                   "budget": {"max_seconds": 600, "max_observations": 1}},
    }

    cfg = _db.load_config()
    schema = cfg["schema"]
    cacert = cfg.get("sfe_cacert")
    if cacert and not Path(cacert).is_absolute():
        cacert = str(REPO / cacert)
    role = cfg.get("identity_role", _identity.ROLE_PRODUCTION)

    conn = _db.connect()
    eid = _q.enqueue(
        conn, created_by="vivarium:debit-receipt",
        source_reason="F-1 evidence: one artifact row on the schema-7 engine "
                      "with the debit fallback live",
        source_evidence={"inbox": "INBOX_ARCHAEON_PHASE2_404_2026-09-10.md"},
        experiment_spec=spec, schema=schema,
        candidate_set_id="cs-viv-debit-receipt-%s" % uuid.uuid4().hex[:6],
        artifact_locators={digest: locators[digest]})
    conn.commit()
    print("enqueued %s consuming %s" % (eid, digest[:26] + "..."))

    runner = SfeRunner(base_url=cfg["sfe_base_url"],
                       token=_identity.token_for(role),
                       client_id=_identity.client_id_for(role),
                       cafile=cacert, worker_id="vivarium@debit-receipt",
                       lease_s=300.0, timeout=300.0, log=print)
    viv = Vivarium(worker_id="vivarium@debit-receipt", schema=schema,
                   runner=runner, pew_client=None, log=print)
    report = viv.tick(conn)
    conn.commit()

    row = _q.get(conn, eid, schema=schema)
    summary = row["result_summary"] or {}
    receipt = summary.get("load_receipt") or {}
    doc = {
        "outcome": report.outcome,
        "experiment_id": str(eid),
        "status": row["status"],
        "engine": runner.engine_identity,
        "allowance_mechanism": receipt.get("allowance_mechanism"),
        "cost_events": receipt.get("cost_events"),
        "cost_events_unavailable": receipt.get("cost_events_unavailable"),
        "digest_gate": receipt.get("digest_gate"),
        "bytes_loaded": receipt.get("bytes_loaded"),
        "closure_manifest": receipt.get("closure_manifest"),
        "consumed_digest": digest,
        "resolution": (receipt.get("closure") or [{}])[0].get("resolution"),
        "result": (summary.get("result") or {}).get("repeats", [{}])[0]
                  .get("result"),
        "resources": summary.get("resources"),
    }
    blob = json.dumps(doc, indent=2, default=str)
    print(blob)
    if args.out:
        Path(args.out).write_text(blob + "\n", encoding="utf-8")
    conn.close()
    ok = (report.outcome == "EXECUTED"
          and str(doc["allowance_mechanism"] or "").startswith("debit"))
    print("\nRESULT: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
