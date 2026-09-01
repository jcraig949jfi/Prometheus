"""Collision-proof cycle-number allocation. Repairs LIM-011.

THE DEFECT THIS REPLACES. Cycle numbers were computed as `last_cycle + 1` from an unlocked
local JSON state file. Two campaign instances forked and both allocated 038; the loser's fossil
was whatever git happened to overwrite. My own remediation then destroyed the rescued record
TWICE, because "max(existing files) + 1" is the SAME FORMULA as "last_cycle + 1" -- every cycle
writes a file, so max(existing) equals last_cycle by construction.

THE FIX IS EXCLUSIVE CREATION, NOT A BIGGER NUMBER. Allocation and reservation are made the
same act: the allocator creates the fossil file with O_CREAT|O_EXCL, which the filesystem
guarantees is atomic. If the file already exists -- because another worker took that number
between our scan and our write -- the create fails and we advance. No lock file to leak, no
state file to disagree with the directory, and correctness does not depend on the two workers
sharing memory or a clock.

WHAT IT DOES NOT FIX. Two workers can still do the same WORK under different numbers -- nothing
here coordinates which frontier a worker picks. That is a scheduling problem, not an allocation
one, and it is recorded rather than pretended away.
"""
from __future__ import annotations

import json
import os
import pathlib
import socket
import time
from typing import Optional

CYCLE_DIR = pathlib.Path(__file__).resolve().parent / "cycles"
#: Numbers at or above this are RESERVED for rescued/recovered records and are never allocated.
#: Recovered fossils actually live outside cycles/ now, but the reservation is kept so a future
#: hand-parked record cannot be overwritten by an allocator that has caught up.
RESERVED_FLOOR = 900
MAX_PROBE = 10000


def worker_id() -> str:
    """Identifies which instance wrote a cycle. Stamped on the fossil so a fork is visible in
    the record rather than inferred later from a merge conflict."""
    return socket.gethostname() + ":" + str(os.getpid())


def existing_numbers() -> set:
    if not CYCLE_DIR.exists():
        return set()
    out = set()
    for p in CYCLE_DIR.glob("cycle_*.json"):
        stem = p.stem.split("_", 1)[-1]
        if stem.isdigit():
            out.add(int(stem))
    return out


def allocate(start_hint: Optional[int] = None) -> tuple:
    """Reserve the next free cycle number by creating its file exclusively.

    Returns (cycle_number, path). The file exists and holds a placeholder; the caller
    overwrites it with the real fossil when the cycle finishes. Creating it up front is the
    point -- an unwritten reservation is not a reservation.
    """
    CYCLE_DIR.mkdir(parents=True, exist_ok=True)
    used = existing_numbers()
    n = max([x for x in used if x < RESERVED_FLOOR], default=-1) + 1
    if start_hint is not None:
        n = max(n, int(start_hint))

    while n < MAX_PROBE:
        if n >= RESERVED_FLOOR:
            raise RuntimeError("cycle numbering reached the reserved floor " + str(RESERVED_FLOOR))
        p = CYCLE_DIR / ("cycle_{:03d}.json".format(n))
        try:
            fd = os.open(str(p), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            n += 1
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump({"cycle": n, "status": "RESERVED",
                       "reserved_by": worker_id(),
                       "reserved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                      fh, indent=2)
        return n, p
    raise RuntimeError("no free cycle number below " + str(MAX_PROBE))


def verify_no_collisions() -> dict:
    """Audit: every cycle file's internal `cycle` field must match its filename, and no number
    may appear twice. A mismatch is the signature of a hand-edit or an overwrite."""
    mismatches, unreadable = [], []
    seen = {}
    for p in sorted(CYCLE_DIR.glob("cycle_*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:                                             # noqa: BLE001
            unreadable.append(p.name)
            continue
        stem = p.stem.split("_", 1)[-1]
        if stem.isdigit() and int(stem) != int(d.get("cycle", -1)):
            mismatches.append({"file": p.name, "internal_cycle": d.get("cycle")})
        seen.setdefault(int(d.get("cycle", -1)), []).append(p.name)
    dupes = {k: v for k, v in seen.items() if len(v) > 1}
    return {"files": len(seen), "filename_vs_field_mismatches": mismatches,
            "duplicate_cycle_numbers": dupes, "unreadable": unreadable,
            "CLEAN": not mismatches and not dupes and not unreadable}
