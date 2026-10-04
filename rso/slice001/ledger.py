"""Attempted-run inventory and caps ledger (C-004-T019). Python >= 3.8, standard library only.

Every top-level validation launch (and every mutation child) is an attempt. An attempt is inventoried
whether it completes, fails, is refused by a cap, or dies without reporting. The ledger only COUNTS and
REFUSES: it decides nothing about what an attempt means scientifically (plan s3 Anchors, s6 caps).

Store: append-only JSONL, one record per line, flushed and fsynced before the call returns.
    START    {kind, run_id, node_id, launch_kind, start_utc, supplied_by}   written by begin()
    END      {kind, run_id, status, cpu_s, artifact_bytes, end_utc}         written by finish()
    REFUSED  {kind, run_id, node_id, launch_kind, cap, used, limit, at_utc, supplied_by}
inventory() derives the rows G-INV reads (evidence.inventory_terminal): one {kind: RUN, run_id, node_id,
status, launch_kind, cpu_us, artifact_bytes, ...} per run_id, then {kind: TERMINAL, row_count}. The rows are
canonical JSON (receipt.canonical_bytes refuses floats, draft B B2), so CPU is INTEGER MICROSECONDS cpu_us
(float seconds x 1e6, rounded; the JSONL store keeps the float seconds). A START with no END is INTERRUPTED
(cpu_us and artifact_bytes None: unmetered, never zero). It still counts as a launch if it was TOP_LEVEL.

Launch kinds: TOP_LEVEL (a validation launch: counts toward the launch cap), MUTATION_CHILD and RECEIPT
(charged CPU and bytes, never counted as launches). RECEIPT is for one row per receipt, with its node_id (V7),
under one charged TOP_LEVEL build row (C-004-T025).

Charging (contract.json `caps`, C-004-OP1, CPU cap per OP-4 / contract v1.0.3): top-level launches (REFUSED
rows, MUTATION_CHILD rows and RECEIPT rows do not count), CPU seconds and new artifact bytes of every finished
attempt including failures, retries and mutation children. begin() refuses once any cap is used up
(used >= limit), checking launches (TOP_LEVEL only), then CPU, then artifact bytes.

Field decisions (rso-builder-role s2.7):
  - "MB" in new_artifact_mb is 10**6 bytes (smaller, so the stricter reading; revisit if the keeper
    names MiB).
  - Single writer per store: begin() reads then appends without a lock. Concurrent top-level launches
    against one store could both pass the check; the slice launches serially. Revisit if T020 parallelises.
"""
import argparse
import datetime
import json
import os
import sys
import time

PKG_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONTRACT = os.path.join(PKG_DIR, "contract", "contract.json")

TOP_LEVEL = "TOP_LEVEL"
MUTATION_CHILD = "MUTATION_CHILD"
RECEIPT = "RECEIPT"        # one per receipt under a single charged build row: CPU and bytes, not a launch
LAUNCH_KINDS = (TOP_LEVEL, MUTATION_CHILD, RECEIPT)
END_STATUSES = ("COMPLETED", "FAILED")
MB = 1000 * 1000


class LedgerError(Exception):
    """Malformed caps, store or call. Fails closed."""


class CapExhausted(Exception):
    def __init__(self, cap, used, limit):
        Exception.__init__(self, "cap exhausted: %s used %s of %s" % (cap, used, limit))
        self.cap, self.used, self.limit = cap, used, limit


def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _number(v, name, integer=False):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0 or v != v:
        raise LedgerError("caps.%s must be a non-negative number, got %r" % (name, v))
    if integer and int(v) != v:
        raise LedgerError("caps.%s must be a whole number, got %r" % (name, v))
    return v


class Caps(object):
    def __init__(self, launches, cpu_s, artifact_bytes):
        self.launches, self.cpu_s, self.artifact_bytes = launches, cpu_s, artifact_bytes

    @classmethod
    def from_dict(cls, d):
        if not isinstance(d, dict):
            raise LedgerError("caps is not an object")
        for k in ("top_level_validation_launches", "cpu_minutes", "new_artifact_mb"):
            if k not in d:
                raise LedgerError("caps missing %s" % k)
        return cls(int(_number(d["top_level_validation_launches"], "top_level_validation_launches", True)),
                   _number(d["cpu_minutes"], "cpu_minutes") * 60,
                   _number(d["new_artifact_mb"], "new_artifact_mb") * MB)


class Attempt(object):
    def __init__(self, ledger, run_id):
        self._ledger, self.run_id, self._done = ledger, run_id, False

    def finish(self, status, cpu_s=0.0, artifact_bytes=0):
        if self._done:
            raise LedgerError("attempt %s already finished" % self.run_id)
        if status not in END_STATUSES:
            raise LedgerError("status must be one of %s, got %r" % (END_STATUSES, status))
        self._ledger._append({"kind": "END", "run_id": self.run_id, "status": status,
                              "cpu_s": float(cpu_s), "artifact_bytes": int(artifact_bytes),
                              "end_utc": _utc_now()})
        self._done = True


class _Run(object):
    """Context manager: measures this process's CPU, writes FAILED on an exception and re-raises."""

    def __init__(self, ledger, run_id, node_id, launch_kind, supplied_by):
        self._args = (run_id, node_id, launch_kind, supplied_by)
        self._ledger, self.attempt, self._c0 = ledger, None, None

    def __enter__(self):
        self.attempt = self._ledger.begin(*self._args[:3], supplied_by=self._args[3])
        self._c0 = time.process_time()
        return self.attempt

    def __exit__(self, exc_type, exc, tb):
        if not self.attempt._done:
            self.attempt.finish("FAILED" if exc_type else "COMPLETED", cpu_s=time.process_time() - self._c0)
        return False


def _canonical_row(row):
    out = dict(row)
    s = out.pop("cpu_s")
    out["cpu_us"] = None if s is None else int(round(s * 1000000))
    return out


class Ledger(object):
    def __init__(self, path, caps):
        self.path, self.caps, self.torn_tail = path, caps, False

    @classmethod
    def from_contract(cls, path, contract_path=DEFAULT_CONTRACT):
        try:
            with open(contract_path, "r", encoding="utf-8") as f:
                obj = json.load(f)
        except (OSError, ValueError) as e:
            raise LedgerError("cannot read contract %s: %s" % (contract_path, e))
        if not isinstance(obj, dict) or "caps" not in obj:
            raise LedgerError("contract %s has no caps" % contract_path)
        return cls(path, Caps.from_dict(obj["caps"]))

    # ---- store -------------------------------------------------------------------------------------
    def _append(self, rec):
        d = os.path.dirname(os.path.abspath(self.path))
        if not os.path.isdir(d):
            os.makedirs(d)
        with open(self.path, "a", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rec, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def _read(self):
        self.torn_tail = False
        if not os.path.isfile(self.path):
            return []
        with open(self.path, "r", encoding="utf-8", newline="") as f:
            text = f.read()
        lines = text.split("\n")
        recs = []
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
                if not isinstance(rec, dict) or "kind" not in rec or "run_id" not in rec:
                    raise ValueError("not a ledger record")
            except ValueError as e:
                if i == len(lines) - 1:               # no trailing newline: a torn final write
                    self.torn_tail = True
                    continue
                raise LedgerError("%s line %d is corrupt: %s" % (self.path, i + 1, e))
            recs.append(rec)
        return recs

    # ---- derived state -----------------------------------------------------------------------------
    def _runs(self, recs):
        """run_id -> merged row, in first-seen order (dicts preserve insertion order on >= 3.7)."""
        runs = {}
        for r in recs:
            k, rid = r["kind"], r["run_id"]
            if k in ("START", "REFUSED"):
                if rid in runs:
                    raise LedgerError("duplicate run_id in store: %s" % rid)
                row = {"kind": "RUN", "run_id": rid, "node_id": r.get("node_id"),
                       "launch_kind": r.get("launch_kind"), "supplied_by": r.get("supplied_by")}
                if k == "START":
                    row.update({"status": "INTERRUPTED", "cpu_s": None, "artifact_bytes": None,
                                "start_utc": r.get("start_utc"), "end_utc": None})
                else:
                    row.update({"status": "REFUSED", "cpu_s": 0.0, "artifact_bytes": 0,
                                "start_utc": r.get("at_utc"), "end_utc": r.get("at_utc"),
                                "refused_cap": r.get("cap")})
                runs[rid] = row
            elif k == "END":
                if rid not in runs or runs[rid]["status"] != "INTERRUPTED":
                    raise LedgerError("END without an open START: %s" % rid)
                runs[rid].update({"status": r["status"], "cpu_s": r["cpu_s"],
                                  "artifact_bytes": r["artifact_bytes"], "end_utc": r.get("end_utc")})
            else:
                raise LedgerError("unknown record kind %r" % k)
        return runs

    def usage(self):
        rows = list(self._runs(self._read()).values())
        return {"launches": sum(1 for r in rows if r["launch_kind"] == TOP_LEVEL and r["status"] != "REFUSED"),
                "cpu_s": sum(r["cpu_s"] or 0.0 for r in rows),
                "artifact_bytes": sum(r["artifact_bytes"] or 0 for r in rows)}

    def exhausted(self, launch_kind=TOP_LEVEL):
        """First exhausted cap as (name, used, limit), else None."""
        u = self.usage()
        if launch_kind == TOP_LEVEL and u["launches"] >= self.caps.launches:
            return ("top_level_validation_launches", u["launches"], self.caps.launches)
        if u["cpu_s"] >= self.caps.cpu_s:
            return ("cpu_minutes", u["cpu_s"] / 60.0, self.caps.cpu_s / 60.0)
        if u["artifact_bytes"] >= self.caps.artifact_bytes:
            return ("new_artifact_mb", u["artifact_bytes"] / float(MB), self.caps.artifact_bytes / float(MB))
        return None

    # ---- attempts ----------------------------------------------------------------------------------
    def begin(self, run_id, node_id, launch_kind=TOP_LEVEL, supplied_by=None):
        if launch_kind not in LAUNCH_KINDS:
            raise LedgerError("launch_kind must be one of %s" % (LAUNCH_KINDS,))
        if not isinstance(run_id, str) or not run_id or not isinstance(node_id, str) or not node_id:
            raise LedgerError("run_id and node_id are required non-empty strings")
        if run_id in self._runs(self._read()):
            raise LedgerError("run_id already inventoried: %s" % run_id)
        hit = self.exhausted(launch_kind)
        if hit:
            self._append({"kind": "REFUSED", "run_id": run_id, "node_id": node_id,
                          "launch_kind": launch_kind, "cap": hit[0], "used": hit[1], "limit": hit[2],
                          "at_utc": _utc_now(), "supplied_by": supplied_by})
            raise CapExhausted(*hit)
        self._append({"kind": "START", "run_id": run_id, "node_id": node_id, "launch_kind": launch_kind,
                      "start_utc": _utc_now(), "supplied_by": supplied_by})
        return Attempt(self, run_id)

    def run(self, run_id, node_id, launch_kind=TOP_LEVEL, supplied_by=None):
        return _Run(self, run_id, node_id, launch_kind, supplied_by)

    # ---- the inventory G-INV reads ------------------------------------------------------------------
    def inventory(self):
        """RUN rows then TERMINAL, as canonical JSON (receipt.canonical_bytes refuses floats, draft B B2):
        CPU is integer microseconds `cpu_us` (None when unmetered); the store keeps the float seconds."""
        rows = [_canonical_row(r) for r in self._runs(self._read()).values()]
        return rows + [{"kind": "TERMINAL", "row_count": len(rows)}]

    def write_inventory(self, path):
        d = os.path.dirname(os.path.abspath(path))
        if not os.path.isdir(d):
            os.makedirs(d)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            for r in self.inventory():
                f.write(json.dumps(r, sort_keys=True) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -B -m rso.slice001.ledger")
    ap.add_argument("command", choices=("summary", "export"))
    ap.add_argument("store")
    ap.add_argument("--contract", default=DEFAULT_CONTRACT)
    ap.add_argument("--out", help="export: destination file (default stdout)")
    args = ap.parse_args(argv)
    try:
        led = Ledger.from_contract(args.store, args.contract)
        if args.command == "summary":
            print(json.dumps({"usage": led.usage(), "caps": {"launches": led.caps.launches,
                                                              "cpu_s": led.caps.cpu_s,
                                                              "artifact_bytes": led.caps.artifact_bytes},
                              "exhausted": led.exhausted(), "torn_tail": led.torn_tail}, indent=2,
                             sort_keys=True))
        elif args.out:
            led.write_inventory(args.out)
        else:
            for r in led.inventory():
                print(json.dumps(r, sort_keys=True))
    except LedgerError as e:
        sys.stderr.write("ledger error: %s\n" % e)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
