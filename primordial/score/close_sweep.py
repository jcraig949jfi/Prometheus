"""H-R6-2 (round 6, D10): no silent rows. The close sweep.

Round 5 left two committed row sets with no guarded receipt (E-R5-3 GPU results, the H replay of B-R5-1): the
measurements existed but bypassed the receipt layer. Rule: every rows file committed inside the round window is
cited by a GUARDED receipt (one carrying campaign_stage, i.e. filed through receipt_guard in bus.receipt), or the
sweep emits UNRECEIPTED_OBSERVATION naming it. No exemptions and no prose: paths are matched as identifiers.

  rows_committed_in_window(repo, start, end)   primordial/ledger/rows/** files added or modified by a commit whose
                                               committer time is in [start, end] -> {path: [commit shas]}
  guarded_receipts(ledger_dir, since)          receipt mirror lines (primordial/ledger/<lane>.jsonl) with
                                               campaign_stage and ts >= since
  sweep(...)                                   {rows_files, cited, unreceipted: [{path, commits}]}
  emit(r, result, round_id)                    one pm:events record per unreceipted path (event
                                               UNRECEIPTED_OBSERVATION), idempotent per (round, path)

    python -m primordial.score.close_sweep --round r6 [--emit]
    python -m primordial.score.close_sweep --start TS --end TS [--emit]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
ROWS_PREFIX = "primordial/ledger/rows/"
LEDGER_DIR = ROOT / "primordial" / "ledger"
EVENTS = "pm:events"
EVENT = "UNRECEIPTED_OBSERVATION"
SEEN = "pm:sweep:unreceipted:{}:{}"
ROWS_RE = re.compile(r"primordial/[\w./-]+\.jsonl?")


def rows_committed_in_window(repo=ROOT, start: float = 0.0, end: float = float("inf"),
                             prefix: str = ROWS_PREFIX) -> dict[str, list[str]]:
    q = subprocess.run(["git", "-C", str(repo), "log", "--all", "--format=@@%H %ct", "--name-only",
                        "--diff-filter=AM", "--", prefix], capture_output=True, text=True, timeout=300)
    out: dict[str, list[str]] = {}
    sha, ts = None, None
    for line in q.stdout.splitlines():
        if line.startswith("@@"):
            sha, t = line[2:].split()
            ts = float(t)
            continue
        path = line.strip()
        if path and sha and start <= ts <= end and path.startswith(prefix):
            out.setdefault(path, [])
            if sha not in out[path]:
                out[path].append(sha)
    return out


def guarded_receipts(ledger_dir=LEDGER_DIR, since: float = 0.0) -> list[dict]:
    recs = []
    for f in sorted(pathlib.Path(ledger_dir).glob("*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if isinstance(rec, dict) and rec.get("campaign_stage") is not None and float(rec.get("ts") or 0) >= since:
                recs.append(rec)
    return recs


def sweep(repo=ROOT, start: float = 0.0, end: float = float("inf"), receipts: list[dict] | None = None,
          ledger_dir=LEDGER_DIR) -> dict:
    files = rows_committed_in_window(repo, start, end)
    receipts = guarded_receipts(ledger_dir, start) if receipts is None else [
        r for r in receipts if r.get("campaign_stage") is not None]
    cited: dict[str, list[str]] = {}
    for rec in receipts:
        for p in set(ROWS_RE.findall(str(rec.get("rows") or ""))):
            cited.setdefault(p, []).append(rec.get("exp_id"))
    return {"window": [start, end], "rows_files": sorted(files),
            "cited": {p: cited[p] for p in sorted(files) if p in cited},
            "unreceipted": [{"path": p, "commits": files[p]} for p in sorted(files) if p not in cited]}


def emit(r, result: dict, round_id: str) -> list[str]:
    """One UNRECEIPTED_OBSERVATION event per unreceipted path, once per (round, path). -> paths emitted now."""
    emitted = []
    for u in result["unreceipted"]:
        if not r.set(SEEN.format(round_id, u["path"]), f"{time.time():.3f}", nx=True):
            continue
        r.xadd(EVENTS, {"event": EVENT, "json": json.dumps({"event": EVENT, "round": round_id, **u,
                                                            "window": result["window"], "ts": time.time()})})
        emitted.append(u["path"])
    return emitted


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--round")
    ap.add_argument("--start", type=float)
    ap.add_argument("--end", type=float)
    ap.add_argument("--emit", action="store_true")
    a = ap.parse_args(argv)
    from primordial.bus import bus
    r = bus.conn()
    rid = a.round or "adhoc"
    start, end = a.start, a.end
    if a.round:
        from primordial.ops import round_clock as RC
        clock = RC.read(r, a.round)
        if clock is None:
            print(f"no clock for round {a.round}")
            return 2
        start, end = clock["start_ts"], clock["end_ts"]
    out = sweep(ROOT, start or 0.0, end if end is not None else float("inf"))
    print(json.dumps({"round": rid, "rows_files": len(out["rows_files"]), "cited": len(out["cited"]),
                      "unreceipted": out["unreceipted"]}, indent=1))
    if a.emit:
        print("emitted", emit(r, out, rid))
    return 0 if not out["unreceipted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
