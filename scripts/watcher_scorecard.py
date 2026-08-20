#!/usr/bin/env python
"""Watcher scorecard — scores Aporia and Shadow-A against the execution ledger.

Preregistration (BINDING): pivot/PREREG_watcher_scorecard_2026-08-20.md
Run at the start of any session that touches watcher output:

    python scripts/watcher_scorecard.py            # harvest + score + report
    python scripts/watcher_scorecard.py --run-probes   # also execute probe commands

A script, not a service. Idempotent. Atomic writes only. If anything is
unreadable or inconsistent it prints STATUS: FAILED <why> and writes nothing —
it never re-prints yesterday's numbers with today's date (M4 reporter rule).

Ledgers (all append-only JSONL under watchers/):
  findings/<seat>.jsonl   typed findings emitted by watchers (schema: prereg SS2)
  adjudications.jsonl     {finding_id, verdict, by, ts_utc, detail}
                          verdict in CONFIRMED|REFUTED|PROBE-FAILED|UNRESOLVABLE-BY-EXECUTION
  decoys.jsonl            {decoy_id, artifact, defect_class, planted_by, ts_utc}
                          registered BEFORE planting (prereg SS4); Charon's authority
  metrics.jsonl           one row per scorecard round (written by this script only)

A "round" = one scorecard run that saw >=1 new finding. Overlap matches findings
across seats on (artifact, defect_class) — a proxy; disputes go to James, not to
a smarter matcher.
"""

import argparse
import io
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1252 guard

ROOT = Path(__file__).resolve().parent.parent
WDIR = ROOT / "watchers"
FINDINGS_DIR = WDIR / "findings"
ADJUDICATIONS = WDIR / "adjudications.jsonl"
DECOYS = WDIR / "decoys.jsonl"
METRICS = WDIR / "metrics.jsonl"

SEATS = ("aporia", "shadow_a")
VERDICTS = {"CONFIRMED", "REFUTED", "PROBE-FAILED", "UNRESOLVABLE-BY-EXECUTION"}
CAPTURE_OVERLAP = 0.7   # prereg SS1: alarm at >=0.7 for two consecutive rounds
CAPTURE_MONOTONE = 4    # ... or monotone increase across four rounds


def _fail(why: str) -> "NoReturn":
    print(f"STATUS: FAILED {why}")
    sys.exit(1)


def _read_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    rows = []
    # utf-8-sig: tolerate the BOM that PowerShell's Out-File -Encoding utf8 emits
    with io.open(path, "r", encoding="utf-8-sig") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                _fail(f"unparseable line {n} in {path.relative_to(ROOT)}: {e}")
    return rows


def _append_atomic(path: Path, row: dict) -> None:
    """Append one row via full-file rewrite to temp + os.replace (fleet convention)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with io.open(fd, "w", encoding="utf-8") as f:
            f.write(existing)
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        os.replace(tmp, str(path))
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def load_state():
    findings = {}
    for seat in SEATS:
        rows = _read_jsonl(FINDINGS_DIR / f"{seat}.jsonl")
        for r in rows:
            for key in ("id", "seat", "artifact", "claim", "defect_class"):
                if key not in r:
                    _fail(f"finding missing '{key}' in findings/{seat}.jsonl: {r.get('id', '?')}")
            if r["seat"] != seat:
                _fail(f"seat mismatch: {r['id']} says {r['seat']} but lives in {seat}.jsonl")
        findings[seat] = rows
    ids = [r["id"] for rows in findings.values() for r in rows]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        _fail(f"duplicate finding ids: {dupes}")

    adjudications = _read_jsonl(ADJUDICATIONS)
    for a in adjudications:
        if a.get("verdict") not in VERDICTS:
            _fail(f"unknown verdict {a.get('verdict')!r} on {a.get('finding_id')}")
    decoys = _read_jsonl(DECOYS)
    metrics = _read_jsonl(METRICS)
    return findings, adjudications, decoys, metrics


def run_probes(findings, adjudications, execute: bool):
    """Execute probe commands for unadjudicated findings (only with --run-probes)."""
    adjudicated = {a["finding_id"] for a in adjudications}
    queued, ran = [], []
    for seat, rows in findings.items():
        for r in rows:
            if r["id"] in adjudicated:
                continue
            probe = r.get("probe")
            if not probe:
                queued.append((r["id"], "no probe — needs a session to construct one"))
                continue
            if not execute:
                queued.append((r["id"], f"probe ready: {probe}"))
                continue
            try:
                p = subprocess.run(
                    probe, shell=True, cwd=str(ROOT), capture_output=True,
                    text=True, timeout=300,
                )
                verdict = "CONFIRMED" if p.returncode == 0 else "REFUTED"
                detail = (p.stdout or p.stderr or "").strip()[-500:]
            except Exception as e:  # timeout, spawn failure — loud, not a verdict
                verdict, detail = "PROBE-FAILED", str(e)[:500]
            _append_atomic(ADJUDICATIONS, {
                "finding_id": r["id"], "verdict": verdict,
                "by": "watcher_scorecard --run-probes",
                "ts_utc": datetime.now(timezone.utc).isoformat(),
                "detail": detail,
            })
            ran.append((r["id"], verdict))
    return queued, ran


def score(findings, adjudications, decoys, metrics):
    verdict_by_id = {a["finding_id"]: a["verdict"] for a in adjudications}
    decoy_artifacts = {d["artifact"] for d in decoys}
    prev_rounds = len(metrics)

    # Window = findings not covered by any previous round (id high-water set).
    covered = set()
    for m in metrics:
        covered.update(m.get("finding_ids", []))
    window = {s: [r for r in findings[s] if r["id"] not in covered] for s in SEATS}
    n_new = sum(len(v) for v in window.values())

    per_seat = {}
    for seat in SEATS:
        rows = findings[seat]
        real = [r for r in rows if r["artifact"] not in decoy_artifacts]
        on_decoys = [r for r in rows if r["artifact"] in decoy_artifacts]
        confirmed = [r for r in real if verdict_by_id.get(r["id"]) == "CONFIRMED"]
        refuted = [r for r in real if verdict_by_id.get(r["id"]) == "REFUTED"]
        with_probe = [r for r in rows if r.get("probe")]
        per_seat[seat] = {
            "findings_total": len(rows),
            "findings_new": len(window[seat]),
            "yield_confirmed": len(confirmed),
            "false_accusations": len(refuted),
            "false_accusation_rate": round(len(refuted) / len(real), 3) if real else None,
            "auto_adjudicable_fraction": round(len(with_probe) / len(rows), 3) if rows else None,
            "decoy_hits": len(on_decoys),
            "decoy_detection_rate": (round(len({r["artifact"] for r in on_decoys}) / len(decoy_artifacts), 3)
                                     if decoy_artifacts else None),
            "unadjudicated": len([r for r in real if r["id"] not in verdict_by_id]),
        }

    def keyset(seat):
        return {(r["artifact"], r["defect_class"]) for r in findings[seat]
                if r["artifact"] not in decoy_artifacts}
    a, b = keyset("aporia"), keyset("shadow_a")
    overlap = round(len(a & b) / len(a | b), 3) if (a | b) else None

    history = [m["overlap"] for m in metrics if m.get("overlap") is not None]
    if overlap is not None and n_new > 0:
        # only a round with new findings extends the trend; a re-run of the same
        # state must not double-count itself into the capture alarm
        history = history + [overlap]
    alarms = []
    if len(history) >= 2 and all(h >= CAPTURE_OVERLAP for h in history[-2:]):
        alarms.append(f"CAPTURE-ALARM: overlap >= {CAPTURE_OVERLAP} two consecutive rounds -> re-seed shadow (prereg SS1)")
    if len(history) >= CAPTURE_MONOTONE and all(
            history[-i] > history[-i - 1] for i in range(1, CAPTURE_MONOTONE)):
        alarms.append(f"CAPTURE-ALARM: overlap monotone-increasing across {CAPTURE_MONOTONE} rounds -> re-seed shadow (prereg SS1)")

    row = {
        "round": prev_rounds + 1 if n_new > 0 else prev_rounds,
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "per_seat": per_seat,
        "overlap": overlap,
        "overlap_history": history[-8:],
        "alarms": alarms,
        "finding_ids": sorted(covered | {r["id"] for v in window.values() for r in v}),
        "n_new_findings": n_new,
    }
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run-probes", action="store_true",
                    help="execute probe commands of unadjudicated findings (default: queue only)")
    args = ap.parse_args()

    findings, adjudications, decoys, metrics = load_state()
    queued, ran = run_probes(findings, adjudications, execute=args.run_probes)
    if ran:  # reload verdicts written this run
        adjudications = _read_jsonl(ADJUDICATIONS)

    row = score(findings, adjudications, decoys, metrics)
    if row["n_new_findings"] == 0 and not ran:
        print(f"STATUS: OK no new findings since round {len(metrics)}; metrics unchanged (not re-stamped)")
    else:
        _append_atomic(METRICS, row)
        print(f"STATUS: OK round {row['round']} written to watchers/metrics.jsonl")

    print(f"\n== Watcher scorecard — round {row['round']} ==")
    for seat in SEATS:
        s = row["per_seat"][seat]
        print(f"  {seat:9s} total={s['findings_total']} new={s['findings_new']} "
              f"confirmed={s['yield_confirmed']} refuted={s['false_accusations']} "
              f"probe-frac={s['auto_adjudicable_fraction']} "
              f"decoy-rate={s['decoy_detection_rate']} unadjudicated={s['unadjudicated']}")
    print(f"  overlap={row['overlap']} history={row['overlap_history']}")
    for alarm in row["alarms"]:
        print(f"  !! {alarm}")
    if ran:
        print(f"  probes executed: {ran}")
    if queued:
        print(f"  adjudication queue ({len(queued)}):")
        for fid, why in queued[:10]:
            print(f"    - {fid}: {why}")
        if len(queued) > 10:
            print(f"    ... and {len(queued) - 10} more")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # loud-fail convention: no silent zombie output
        _fail(f"{type(e).__name__}: {e}")
