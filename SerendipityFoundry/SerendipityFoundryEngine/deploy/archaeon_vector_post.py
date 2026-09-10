#!/usr/bin/env python3
"""TRACKA-VECTOR-1, closed end to end: post a real Archaeon vector.

    python deploy/archaeon_vector_post.py [--port 8878]

A DEVELOPMENT engine, over real HTTP, with the shipped sfclient. Production is
not touched and not restarted.

WHAT IS POSTED. Not a vector written here to pass: the `engine_entries` field
of a committed producer receipt under archaeon/docs/h0h5/, which is what
costs.to_engine_entries() produced for a real CostEvent. It is posted verbatim.

WHAT IS PROVED. That the projection now round-trips: the engine accepts it,
seals it, stamps the enforcement class ITSELF from the world's limit, and hands
the classes back -- so costs.from_engine_response() has something true to read.
The producer's own enforcement_class never crosses the wire, which is the whole
point: a caller that could declare its own class could opt out of a cap it was
given.

The 200 response is written to deploy/ARCHAEON_VECTOR_200_2026-09-10.json.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.dirname(HERE)
SF = os.path.dirname(ENG)
REPO = os.path.dirname(SF)

for p in (ENG, os.path.join(SF, "SerendipityFoundryClient"), REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

from sfe.release import ENGINE_SOURCE_HASH                          # noqa: E402
from sfe.store import SCHEMA_VERSION                                # noqa: E402
from sfclient import EngineClient, EngineError                      # noqa: E402

#: The world's budget. It is declared HERE, before the post, because the
#: enforcement class comes from the LIMIT -- so which classes come back is a
#: fact about this declaration and not about anything the producer said.
BUDGET = {
    "wall_seconds": {"limit": None, "enforcement": "measured"},
    "cpu_seconds": {"limit": 600, "enforcement": "enforceable"},
    "items": {"limit": None, "enforcement": "measured"},
    # gpu_seconds is deliberately NOT declared: an undeclared resource resolves
    # to `unavailable`, and the producer's own entry for it is already
    # quantity=null. Unavailable is not zero in either direction.
}


def free_port(preferred):
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", preferred))
        return preferred
    except OSError:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]
    finally:
        s.close()


def start_engine(db, port, log_path):
    log = open(log_path, "wb")
    proc = subprocess.Popen(
        [sys.executable, os.path.join(ENG, "serve.py"), "--db", db,
         "--host", "127.0.0.1", "--port", str(port), "--insecure",
         "--registration", "open"],
        cwd=ENG, stdout=log, stderr=subprocess.STDOUT)
    base = "http://127.0.0.1:%d" % port
    for _ in range(200):
        if proc.poll() is not None:
            raise SystemExit("development engine exited; see %s" % log_path)
        try:
            with urllib.request.urlopen(base + "/v2/version", timeout=2) as r:
                return proc, base, json.loads(r.read().decode())
        except Exception:                                    # noqa: BLE001
            time.sleep(0.25)
    proc.kill()
    raise SystemExit("development engine never bound %s" % base)


def pick_receipt():
    pat = os.path.join(REPO, "archaeon", "docs", "h0h5",
                       "ISSUE_RECEIPTS_*.json")
    for p in sorted(glob.glob(pat)):
        with open(p, encoding="utf-8") as fh:
            doc = json.load(fh)
        if doc.get("engine_entries"):
            return p, doc
    raise SystemExit("no Archaeon receipt with engine_entries under %s" % pat)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8878)
    ap.add_argument("--workdir", default=os.path.join(
        os.environ.get("TEMP", "."), "archaeon_vector_dev"))
    ap.add_argument("--out", default=os.path.join(
        HERE, "ARCHAEON_VECTOR_200_2026-09-10.json"))
    a = ap.parse_args()

    path, doc = pick_receipt()
    entries = doc["engine_entries"]
    rel = os.path.relpath(path, REPO).replace(os.sep, "/")

    os.makedirs(a.workdir, exist_ok=True)
    db = os.path.join(a.workdir, "vector.db")
    for stale in (db, db + "-wal", db + "-shm"):
        if os.path.exists(stale):
            os.remove(stale)

    proc, base, version = start_engine(db, free_port(a.port),
                                       os.path.join(a.workdir, "engine.log"))
    ok = True
    try:
        c = EngineClient(base)
        c.register("archaeon-vector-post")
        sid = c.create_session("archaeon-vector")
        wid = c.create_world(sid, "archaeon-vector", budget=BUDGET)["world_id"]
        c.start(wid)

        print("TRACKA-VECTOR-1 -- POSTING A REAL ARCHAEON VECTOR")
        print("=" * 74)
        print("  source receipt      %s" % rel)
        print("  producer event      %s"
              % doc.get("cost_event", {}).get("cost_event_id"))
        print("  entries             %d" % len(entries))
        print("  engine_source_hash  %s" % ENGINE_SOURCE_HASH)
        print("  schema_version      %s" % SCHEMA_VERSION)
        print("  engine_instance_id  %s" % version.get("engine_instance_id"))
        print("  world budget        %s" % json.dumps(BUDGET))
        print()

        http, resp, err = 200, None, None
        try:
            resp = c.cost_event(
                wid, stage=doc["cost_event"]["stage"],
                attempt_id=doc["cost_event"]["attempt_id"],
                resources=entries,
                output_artifacts=doc["cost_event"].get("output_refs") or [],
                source_artifacts=doc["cost_event"].get("source_refs") or [],
                environment=doc["cost_event"].get("environment") or {},
                refs={"producer_cost_event_id":
                      doc["cost_event"]["cost_event_id"],
                      "producer_billing_owner":
                      doc["cost_event"].get("billing_owner"),
                      "source_receipt": rel})
        except EngineError as exc:
            http, err = exc.status, exc.detail
            ok = False

        stamped = {}
        if resp is not None:
            for e in resp["resources"]:
                stamped[e["resource"]] = e.get("enforcement")
                print("  %-14s q=%-22s method=%-9s -> enforcement=%s"
                      % (e["resource"], e["quantity"], e["method"],
                         e.get("enforcement")))
            print()
            print("  cost_event_id       %s" % resp["cost_event_id"])
            print("  entry_hash          %s" % resp["entry_hash"])

            # from_engine_response reads the class BACK; the producer never
            # asserted one. Run THEIR function on THIS response.
            from archaeon.producer import costs as _costs   # noqa: PLC0415
            read_back = _costs.from_engine_response(
                [{**e, "enforcement_class": e.get("enforcement")}
                 for e in resp["resources"]])
            print("  from_engine_response %s" % json.dumps(read_back))

            sealed = c.get_cost_event(resp["cost_event_id"])
            prov_ok = all(
                e["refs"].get("producer_method")
                for e in sealed["sealed"]["resources"])
            report = c.cost_report(wid)
            out = {
                "_what_this_is":
                    "TRACKA-VECTOR-1 closed end to end. The engine_entries of "
                    "a committed Archaeon producer receipt, posted verbatim "
                    "to a DEVELOPMENT engine over HTTP and accepted. The "
                    "enforcement classes below were stamped BY THE ENGINE from "
                    "the world's declared limits; the producer's own "
                    "enforcement_class never crossed the wire.",
                "source_receipt": rel,
                "producer_cost_event_id":
                    doc["cost_event"]["cost_event_id"],
                "engine": {
                    "engine_source_hash": ENGINE_SOURCE_HASH,
                    "schema_version": SCHEMA_VERSION,
                    "engine_instance_id": version.get("engine_instance_id"),
                    "note": "a DEVELOPMENT ledger. Production was not touched.",
                },
                "world_budget_declared": BUDGET,
                "request": {"http_method": "POST",
                            "path": "/v2/worlds/{world_id}/cost-events",
                            "resources": entries},
                "response": {"http": 200, "body": resp},
                "enforcement_stamped_by_the_engine": stamped,
                "from_engine_response": read_back,
                "provenance_survived": prov_ok,
                "sealed_resources": sealed["sealed"]["resources"],
                "entry_hash": resp["entry_hash"],
                "cost_report": {
                    "additive_totals": report["additive_totals"],
                    "unavailable_counts": report["unavailable_counts"],
                    "by_artifact_keys": sorted(report["by_artifact"])[:5],
                },
            }
            for name, want in (("wall_seconds", "measured"),
                               ("cpu_seconds", "enforceable"),
                               ("items", "measured"),
                               ("gpu_seconds", "unavailable")):
                if stamped.get(name) != want:
                    print("  [FAIL] %s stamped %s, expected %s"
                          % (name, stamped.get(name), want))
                    ok = False
            if not prov_ok:
                print("  [FAIL] provenance did not survive into the seal")
                ok = False
            if "gpu_seconds" in report["additive_totals"]:
                print("  [FAIL] an unavailable quantity was summed")
                ok = False
        else:
            out = {"_what_this_is": "TRACKA-VECTOR-1 post FAILED",
                   "source_receipt": rel,
                   "request": {"resources": entries},
                   "response": {"http": http, "error": err}}
            print("  REFUSED http=%s %s" % (http, json.dumps(err)[:400]))

        with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(out, indent=2, default=str) + "\n")
        print()
        print("  written: %s" % a.out)
        print("  RESULT: %s" % ("PASS" if ok else "FAIL"))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
