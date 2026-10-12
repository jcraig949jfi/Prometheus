"""Single-owner execution lease for long Cosmos campaigns (one active instance per seat).

The lease is a JSON file under COSMOS_HOME. A holder renews it; another instance may take it only
after it expires. Writes go through an flock'd lock file plus atomic rename, so two processes on one
host cannot both believe they hold it. Cross-host exclusion is by convention: the lease file lives
on the only host that runs Cosmos (BOOTSTRAP s0 names it), and comms `who` shows the live instance.

    python -m prometheus.cosmos.lease acquire <instance> [--ttl 7200]
    python -m prometheus.cosmos.lease renew   <instance>
    python -m prometheus.cosmos.lease release <instance>
    python -m prometheus.cosmos.lease show
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import socket
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Optional


def home() -> Path:
    return Path(os.environ.get("COSMOS_HOME") or (Path.home() / "cosmos_runs"))


def lease_path(root: Optional[Path] = None) -> Path:
    return (root or home()) / "LEASE.json"


class LeaseHeld(RuntimeError):
    pass


@contextmanager
def _locked(root: Path):
    root.mkdir(parents=True, exist_ok=True)
    with open(root / "LEASE.lock", "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def read(root: Optional[Path] = None) -> Optional[dict]:
    p = lease_path(root)
    if not p.exists():
        return None
    return json.loads(p.read_text())


def _write(root: Path, rec: dict) -> None:
    p = lease_path(root)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1, sort_keys=True))
    os.replace(tmp, p)


def acquire(instance: str, ttl: float = 7200.0, root: Optional[Path] = None,
            now: Optional[float] = None) -> dict:
    root = root or home()
    now = time.time() if now is None else now
    with _locked(root):
        cur = read(root)
        if cur and cur["instance"] != instance and cur["expires"] > now:
            raise LeaseHeld("lease held by %s until %s" % (cur["instance"], cur["expires_utc"]))
        rec = {"instance": instance, "host": socket.gethostname(), "pid": os.getpid(),
               "acquired": now if not cur or cur["instance"] != instance else cur["acquired"],
               "renewed": now, "ttl": ttl, "expires": now + ttl,
               "expires_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now + ttl))}
        _write(root, rec)
        return rec


def renew(instance: str, root: Optional[Path] = None, now: Optional[float] = None) -> dict:
    root = root or home()
    cur = read(root)
    if not cur or cur["instance"] != instance:
        raise LeaseHeld("not the holder (%s)" % (cur and cur["instance"]))
    return acquire(instance, cur["ttl"], root, now)


def release(instance: str, root: Optional[Path] = None) -> None:
    root = root or home()
    with _locked(root):
        cur = read(root)
        if cur and cur["instance"] == instance:
            lease_path(root).unlink()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="prometheus.cosmos.lease")
    ap.add_argument("cmd", choices=["acquire", "renew", "release", "show"])
    ap.add_argument("instance", nargs="?")
    ap.add_argument("--ttl", type=float, default=7200.0)
    a = ap.parse_args(argv)
    try:
        if a.cmd == "acquire":
            print(json.dumps(acquire(a.instance, a.ttl), indent=1))
        elif a.cmd == "renew":
            print(json.dumps(renew(a.instance), indent=1))
        elif a.cmd == "release":
            release(a.instance)
        else:
            print(json.dumps(read(), indent=1))
    except LeaseHeld as e:
        print("LEASE HELD: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
