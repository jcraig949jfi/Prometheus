"""Minimal resource-lease ledger for Aphrodite ARC3 work on host M4.

Coordination only, NOT scientific authorisation. Every holder records host,
thread/experiment, resource envelope and expiry. Leases are released promptly.
    python lease.py acquire <holder> <thread> <cpu_cores> <hours> [note]
    python lease.py release <lease_id> [note]
    python lease.py list
acquire refuses if the active CPU total would exceed CAPACITY (8 cores on M4),
counting only unexpired leases, and prints the active holders so the caller
can QUEUE instead of competing.
"""
import json
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE / "ledger.jsonl"
ACTIVE = HERE / "active.json"
CAPACITY = 8
HOST = "M4"


def _now():
    return time.time()


def _load():
    try:
        return json.loads(ACTIVE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def _save(a):
    ACTIVE.write_text(json.dumps(a, indent=1, sort_keys=True), encoding="utf-8")


def _log(ev):
    ev["utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(LEDGER, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(ev, sort_keys=True) + "\n")


def active():
    a = _load()
    live = {k: v for k, v in a.items() if v["expires"] > _now()}
    for k in set(a) - set(live):
        _log({"event": "EXPIRED", "lease": k, **a[k]})
    if live != a:
        _save(live)
    return live


def acquire(holder, thread, cores, hours, note=""):
    live = active()
    used = sum(v["cpu_cores"] for v in live.values())
    if used + cores > CAPACITY:
        print("QUEUE: %d/%d cores leased: %s" % (used, CAPACITY,
              {k: (v["holder"], v["thread"], v["cpu_cores"]) for k, v in live.items()}))
        return None
    lid = uuid.uuid4().hex[:8]
    rec = {"holder": holder, "thread": thread, "host": HOST, "cpu_cores": cores,
           "expires": _now() + hours * 3600, "expires_utc": time.strftime(
               "%Y-%m-%dT%H:%MZ", time.gmtime(_now() + hours * 3600)), "note": note}
    live[lid] = rec
    _save(live)
    _log({"event": "ACQUIRE", "lease": lid, **rec})
    print(lid)
    return lid


def release(lid, note=""):
    live = active()
    rec = live.pop(lid, None)
    _save(live)
    _log({"event": "RELEASE", "lease": lid, "note": note, **(rec or {"missing": True})})
    print("released" if rec else "not active")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "acquire":
        acquire(sys.argv[2], sys.argv[3], int(sys.argv[4]), float(sys.argv[5]),
                " ".join(sys.argv[6:]))
    elif cmd == "release":
        release(sys.argv[2], " ".join(sys.argv[3:]))
    else:
        print(json.dumps(active(), indent=1))
