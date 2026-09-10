#!/usr/bin/env python3
"""Bring up the CONTRACT SCRATCH ENGINE. One command, reproducible.

    python deploy/scratch_contract_engine.py            # start (foreground)
    python deploy/scratch_contract_engine.py --check     # is it up and correct?

WHY THIS EXISTS. Two jobs need an engine that is byte-identical to production
but whose ledger is disposable:

  1. `generate_sfe_contract.py --probe-base` derives session scoping by sending
     malformed session keys at every route. Pointed at production that writes
     client registrations and garbage into the live ledger. It must never be.
  2. `roles/Harmonia/contracts/verify_gate_states.sh` uses it as a REGRESSION
     FIXTURE: its test 5 proves the conformance gate returns state 1 (DRIFT) on
     a same-build/different-ledger engine. That test defaults to
     http://127.0.0.1:8901/v2 and fails as state 2 (UNREACHABLE) without it.

IT USED TO BE A BACKGROUND PROCESS OF ONE PERSON'S SESSION, which meant a
committed regression test depended on somebody's terminal staying open. This
script is the fix: anyone can bring the fixture back, and the check below says
whether the one that is running is the right one.

THE CHECK IS THE POINT. A scratch engine that does NOT match production's build
silently invalidates the contract generated against it. Worse, the first time I
started this I bound a port another seat's dev engine already held, and it
answered with the SAME build hash -- because we run the same code -- so the
mistake looked like success. The tell was a runtime flag that had not taken.
--check verifies build hash, schema, a DIFFERENT `engine_instance_id`, and that
registration is open.

WHAT --check DOES NOT VERIFY, stated because an earlier draft of this docstring
claimed it did: it does not confirm that the process on the port is serving
THIS database. It asks `/v2/version` and believes the answer. That is enough to
catch the failure it was written for -- production's own ledger answering, or a
build mismatch -- because `engine_instance_id` distinguishes ledgers even when
two engines share a build. It is NOT enough to tell one disposable scratch
engine from another seat's disposable scratch engine, and it does not try to.
The consequence is bounded: both are disposable, so probing the wrong one wastes
a run rather than writing to a ledger someone owns.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.dirname(HERE)

PORT = 8901                    # verify_gate_states.sh defaults to this
_VAR = os.path.join(ENG, "var", "scratch_contract")
LOG = os.path.join(_VAR, "scratch.log")
PROD = "https://192.168.1.202:8811/v2/version"


def base_for(port: int) -> str:
    return "http://127.0.0.1:%d" % port


def db_for(port: int) -> str:
    """One ledger PER PORT.

    The default port keeps the original path so nothing already running moves.
    Any other port gets its own database, because the only reason to ask for a
    second port is to have a second LEDGER -- that is exactly what the gate's
    state-1 test needs -- and two engines sharing one file would report the
    same engine_instance_id while looking like two engines. A caller who asked
    for two would get one identity and no error.
    """
    if port == PORT:
        return os.path.join(_VAR, "probe.db")
    return os.path.join(_VAR, "probe-%d.db" % port)


def live(url, cacert=None):
    import ssl
    try:
        ctx = ssl.create_default_context(cafile=cacert) if cacert else None
        with urllib.request.urlopen(url, timeout=10,
                                    **({"context": ctx} if ctx else {})) as r:
            return json.loads(r.read().decode()), None
    except Exception as e:                                     # noqa: BLE001
        return None, repr(e)[:160]


def check(cacert, port=PORT):
    base = base_for(port)
    scr, why = live(base + "/v2/version")
    if scr is None:
        print("  [FAIL] scratch engine is NOT running at %s" % base)
        print("         %s" % why)
        print("         start it: python deploy/scratch_contract_engine.py "
              "--port %d" % port)
        return 1
    prod, pwhy = live(PROD, cacert)
    ok = True

    def row(name, passed, detail):
        nonlocal ok
        if not passed:
            ok = False
        print("  [%s] %s" % ("PASS" if passed else "FAIL", name))
        print("         %s" % detail)

    print("CONTRACT SCRATCH ENGINE -- %s" % base)
    print("=" * 74)
    if prod is None:
        row("production reachable for comparison", False, pwhy)
    else:
        row("build hash IDENTICAL to production",
            scr.get("engine_source_hash") == prod.get("engine_source_hash"),
            "scratch %s\n         prod    %s"
            % (scr.get("engine_source_hash"), prod.get("engine_source_hash")))
        row("schema IDENTICAL to production",
            scr.get("schema_version") == prod.get("schema_version"),
            "scratch %s, prod %s" % (scr.get("schema_version"),
                                     prod.get("schema_version")))
        # THE ONE THAT MUST DIFFER. A scratch engine sharing production's
        # ledger would be production, and the probe writes.
        row("ledger is a DIFFERENT one",
            scr.get("engine_instance_id") != prod.get("engine_instance_id"),
            "scratch %s\n         prod    %s"
            % (scr.get("engine_instance_id"), prod.get("engine_instance_id")))
    row("registration is open (the probe registers a client)",
        bool(scr.get("registration_open")), str(scr.get("registration_open")))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--cacert", default=os.path.join(HERE, "m1.crt"))
    ap.add_argument("--port", type=int, default=PORT)
    a = ap.parse_args()
    if a.check:
        return check(a.cacert, a.port)

    db = db_for(a.port)
    os.makedirs(os.path.dirname(db), exist_ok=True)
    print("starting the contract scratch engine on %s" % base_for(a.port))
    print("  db  : %s   (disposable -- the probe writes garbage here)" % db)
    print("  log : %s" % LOG)
    print("  serves the CURRENT tree; verify with --check that it matches "
          "production's build before generating a contract against it.")
    with open(LOG, "ab") as log:
        return subprocess.call(
            [sys.executable, os.path.join(ENG, "serve.py"),
             "--db", db, "--host", "127.0.0.1", "--port", str(a.port),
             "--insecure", "--registration", "open",
             "--max-artifact-bytes", "33554432"],
            cwd=ENG, stdout=log, stderr=subprocess.STDOUT)


if __name__ == "__main__":
    sys.exit(main())
