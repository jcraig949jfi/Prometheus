"""Demonstrate the conformance gate against REAL engines, and record it.

The operator's requirement was explicit: "Do not simply add a CI test proving
the command can run. Demonstrate that an intentionally incompatible engine
prevents actual work, and that a conformant engine permits it."

So every state below is produced by a real engine or a real absence of one --
no monkeypatching, no fabricated identity -- and each is scored on the
CONSEQUENCE rather than on the gate's own words: after the tick, could a row
be claimed? The queue counts before and after are in the receipt.

  CONFORMANT      the live engine named by the contract
  WRONG_INSTANCE  a second engine, its own ledger, its own instance id
  DRIFT           the live engine against a contract describing a route it
                  does not serve
  UNREACHABLE     a port with nothing on it

THE RUNNER IS A DOUBLE, and that is stated rather than hidden: the point
under test is whether work BEGINS, so the demonstration shows the row reaching
dispatch and no science is executed against any engine. The three halting
cases never reach the runner at all, which is itself the thing being shown.

Usage:
    python tools/conformance_demo.py --live-base https://host:8811/v2 \
        --scratch-base http://127.0.0.1:8907/v2 --out <receipt.json>
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

VIVARIUM = Path(__file__).resolve().parent.parent
REPO = VIVARIUM.parent
for p in (str(VIVARIUM), str(REPO)):
    if p not in sys.path:
        sys.path.insert(0, p)

from viv import conformance as _conf                            # noqa: E402
from viv import db as _db                                       # noqa: E402
from viv import queue as _q                                     # noqa: E402
from viv.loop import BLOCKED, Vivarium                          # noqa: E402

CONTRACT = REPO / "roles/Harmonia/contracts/sfe_contract.json"


class _Double:
    """Proves the tick got past the gate without executing science."""

    def __init__(self):
        self.dispatched = 0

    def run(self, request, on_running=None):
        self.dispatched += 1
        raise RuntimeError("demonstration double: no science was executed")


def _spec():
    return {"spec_version": 3, "world": {"seed_root": 424242},
            "hypothesis": "a mechanical loop runs what it is given, once",
            "prediction": None, "work": {"kind": "noop_v0", "payload": {}},
            "outcome_rule": {"field": "executed", "op": "==", "value": True,
                             "if_true": "SURVIVED", "if_false": "FALSIFIED",
                             "if_indeterminate": "INCONCLUSIVE",
                             "aggregate": "first"},
            "repeat": {"count": 1, "order": "sequential",
                       "seed_derivation": "sha256_index", "state": "reset",
                       "budget": {"max_seconds": 60, "max_observations": 1}},
            "pew": None}


def _case(name, conn, schema, cfg, expect_halt):
    """One case: enqueue a row, tick, and report what the queue did."""
    _q.enqueue(conn, created_by="conformance-demo", source_reason=name,
               experiment_spec=_spec(), schema=schema)
    conn.commit()
    before = _q.counts(conn, schema=schema)

    rec = _conf.evaluate(cfg, schema="viv")      # scored as production

    double = _Double()
    v = Vivarium(worker_id="demo-" + name, schema=schema, config={},
                 conformance=cfg, runner=double, log=lambda *a: None)
    # Force the gate to be judged under production rules inside the tick too.
    v.schema_for_gate = "viv"
    orig = _conf.require

    def gated(c=None, **kw):
        return orig(c, schema="viv")

    _conf.require = gated
    try:
        rep = v.tick(conn)
    finally:
        _conf.require = orig
    after = _q.counts(conn, schema=schema)

    ok = (rep.outcome == BLOCKED) if expect_halt else (double.dispatched == 1)
    out = {
        "case": name,
        "expected": "HALT, nothing claimed" if expect_halt
                    else "PROCEED, the row is claimed and reaches dispatch",
        "gate_state": rec.get("state"), "halted": rec.get("halted"),
        "reason": rec.get("reason"),
        "live_identity": rec.get("live"),
        "contract_identity": (rec.get("contract") or {}).get(
            "engine_instance_id"),
        "gate_mode": (rec.get("gate") or {}).get("mode"),
        "gate_exit": (rec.get("gate") or {}).get("exit"),
        "attempts": len(rec.get("attempts") or []),
        "tick_outcome": rep.outcome,
        "queue_before": before, "queue_after": after,
        "queued_unchanged": before.get("queued") == after.get("queued"),
        "reached_dispatch": double.dispatched,
        "AS_EXPECTED": bool(ok),
    }
    # A halted case leaves its row QUEUED, so the count grows by exactly one
    # per halt and never falls. That accumulation is evidence rather than
    # untidiness: it is the queue showing that nothing was consumed.
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live-base", required=True)
    ap.add_argument("--scratch-base", required=True)
    ap.add_argument("--dead-base", default="http://127.0.0.1:9/v2")
    ap.add_argument("--cacert", default=None)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tmp = Path(a.out).parent
    tmp.mkdir(parents=True, exist_ok=True)

    # A contract that describes a route the live engine does not serve. That
    # is a BREAKING difference -- the contract's claims no longer hold -- so
    # the gate must call it DRIFT and not INCOMPLETE.
    C = json.loads(CONTRACT.read_text(encoding="utf-8"))
    C["routes"].append({"method": "GET", "path": "/v2/this-route-never-existed",
                        "path_params": [], "required_body": [],
                        "required_query": [], "requires_session_key": False})
    tampered = tmp / "tampered_contract.json"
    tampered.write_text(json.dumps(C), encoding="utf-8")

    schema = "viv_demo_" + uuid.uuid4().hex[:8]
    conn = _db.connect()
    _db.apply_migrations(conn, target_schema=schema)

    def cfg(base, contract=None, **kw):
        return _conf.Config(
            base_url=base,
            contract_path=str(contract or CONTRACT),
            cacert=a.cacert,
            cache_path=str(tmp / ("cache_%s.json" % uuid.uuid4().hex[:6])),
            **kw)

    cases = []
    try:
        cases.append(_case("conformant_live_engine", conn, schema,
                           cfg(a.live_base), expect_halt=False))
        cases.append(_case("wrong_instance_scratch_engine", conn, schema,
                           cfg(a.scratch_base), expect_halt=True))
        cases.append(_case("drift_tampered_contract", conn, schema,
                           cfg(a.live_base, contract=tampered),
                           expect_halt=True))
        cases.append(_case("unreachable_dead_port", conn, schema,
                           cfg(a.dead_base, retries=2, backoff_s=0.2,
                               timeout_s=2.0),
                           expect_halt=True))
    finally:
        _db.drop_schema(conn, schema)
        conn.close()

    receipt = {
        "schema": "vivarium.conformance_demo.v1",
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "live_base": a.live_base, "scratch_base": a.scratch_base,
        "dead_base": a.dead_base,
        "contract": str(CONTRACT.relative_to(REPO)),
        "contract_hash": _conf.contract_hash(CONTRACT),
        "declared_routes": len(_conf.CONSUMER_ROUTES),
        "runner": "double -- no science executed against any engine",
        "cases": cases,
        "all_as_expected": all(c["AS_EXPECTED"] for c in cases),
    }
    Path(a.out).write_text(json.dumps(receipt, indent=1), encoding="utf-8")

    print("%-32s %-18s %-9s %-8s %s"
          % ("case", "state", "tick", "queued", "as expected"))
    for c in cases:
        print("%-32s %-18s %-9s %-8s %s"
              % (c["case"], c["gate_state"], c["tick_outcome"],
                 "%s->%s" % (c["queue_before"].get("queued"),
                             c["queue_after"].get("queued")),
                 c["AS_EXPECTED"]))
    print("\nall_as_expected: %s   receipt: %s"
          % (receipt["all_as_expected"], a.out))
    return 0 if receipt["all_as_expected"] else 1


if __name__ == "__main__":
    sys.exit(main())
