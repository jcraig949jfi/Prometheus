"""Nestor compute lease -- now a thin frontend onto the fabric lease.

MIGRATED 2026-09-28 (operator ruling: the fabric lease is the one authority; the ARC3 "host lease file + comms
record" convention is retired). The command line, exit codes and log are unchanged. Underneath, the lease is the
fabric's atomic Postgres row for "<this host>:<resource>" (for example skullport:cpu8), the same row fabric
Attempts take. No host lease file is written and no comms LEASE broadcast is posted.
`python -m fabric lease status` shows every holder.

    python roles/Nestor/tools/nestor_lease.py status
    python roles/Nestor/tools/nestor_lease.py acquire cpu8 --ttl-min 120 --envelope "..." --work "X-A3-FAIR"      (exit 3 if held)
    python roles/Nestor/tools/nestor_lease.py wait-acquire cpu8 --ttl-min 120 --envelope "..." --work "..."       (queues)
    python roles/Nestor/tools/nestor_lease.py release cpu8
    python roles/Nestor/tools/nestor_lease.py extend cpu8 --ttl-min 60

- Every acquire, extend and release is appended to --log (default: roles/Nestor/LEASES.jsonl).
- Tokens for leases this Nestor holds are kept in ~/.prometheus/nestor_lease_tokens.json. That file is a token
  cache, not a lease.
- If the lease store is unreachable, `acquire` prints UNAVAILABLE and exits 4 (nothing granted), and
  `wait-acquire` keeps waiting. Never assume the resource is free.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from fabric import lease_compat as L  # noqa: E402

TOKENS = pathlib.Path(os.path.expanduser("~/.prometheus/nestor_lease_tokens.json"))


def _log(path: pathlib.Path, rec: dict) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")


def _toks() -> dict:
    return json.loads(TOKENS.read_text()) if TOKENS.exists() else {}


def _save(toks: dict) -> None:
    TOKENS.parent.mkdir(parents=True, exist_ok=True)
    TOKENS.write_text(json.dumps(toks, default=str))


def acquire(res, ttl_min, envelope, work, log) -> dict | None:
    """The lease record, or None if BUSY. Raises L.StoreUnavailable if the store cannot be reached."""
    r = L.acquire(res, "Nestor " + work, purpose=envelope, ttl_s=int(60 * ttl_min))
    if r["result"] != "ACQUIRED":
        return None
    rec = {"resource": res, "fabric_resource": r["resource"], "host": L.host(), "owner": "Nestor " + work,
           "envelope": envelope, "since": time.time(), "until": str(r["expires_at"]), "token": r["token"],
           "lease_id": r["lease_id"], "mechanism": "fabric lease (canonical authority)"}
    toks = _toks(); toks[res] = rec; _save(toks)
    _log(log, {"event": "ACQUIRED", **rec, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
    return rec


def release(res, log) -> str:
    mine = _toks().get(res)
    if not mine:
        return "NOT HELD"
    out = L.release(res, mine["token"], "Nestor")
    toks = _toks(); toks.pop(res, None); _save(toks)
    if out == "RELEASED":
        _log(log, {"event": "RELEASED", "resource": res, "token": mine["token"], "owner": mine["owner"],
                   "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
    return out


def extend(res, ttl_min, log) -> str:
    mine = _toks().get(res)
    if not mine:
        return "NOT HELD"
    out = L.renew(res, mine["token"], int(60 * ttl_min))
    if out == "EXTENDED":
        _log(log, {"event": "EXTENDED", "resource": res, "token": mine["token"], "owner": mine["owner"],
                   "ttl_min": ttl_min, "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("status", "acquire", "wait-acquire", "release", "extend"))
    ap.add_argument("resource", nargs="?")
    ap.add_argument("--ttl-min", type=float, default=60)
    ap.add_argument("--envelope", default="")
    ap.add_argument("--work", default="")
    ap.add_argument("--log", default=str(REPO / "roles" / "Nestor" / "LEASES.jsonl"))
    a = ap.parse_args()
    log = pathlib.Path(a.log)
    try:
        if a.cmd == "status":
            for l in L.status():
                print(l["resource"], l["holder"], "until", l["expires_at"], "STALE" if l["stale"] else "ACTIVE")
        elif a.cmd == "acquire":
            r = acquire(a.resource, a.ttl_min, a.envelope, a.work, log)
            print("ACQUIRED %s" % r["token"] if r else "BUSY")
            sys.exit(0 if r else 3)
        elif a.cmd == "extend":
            r = extend(a.resource, a.ttl_min, log)
            print(r)
            sys.exit(0 if r == "EXTENDED" else 3)
        elif a.cmd == "wait-acquire":
            while True:
                try:
                    r = acquire(a.resource, a.ttl_min, a.envelope, a.work, log)
                except L.StoreUnavailable as e:                   # cannot see the lease state: WAIT, never assume free
                    print("UNAVAILABLE (waiting): %s" % e, flush=True)
                    r = None
                if r:
                    print("ACQUIRED %s" % r["token"])
                    return
                time.sleep(30)
        else:
            print(release(a.resource, log))
    except L.StoreUnavailable as e:
        print("UNAVAILABLE: lease store unreachable, nothing granted or released: %s" % e)
        sys.exit(4)


if __name__ == "__main__":
    main()
