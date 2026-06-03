"""Aporia triage report — Stand E instrument panel (v0.2).

Authority: pivot/aporia_ecosystem_status_and_next_steps_v0.2_2026-05-30.md, Stand E.
This panel SURFACES signals; it does NOT decide. A human reads the output and
makes the calls. Intended to run weekly (Friday morning) or on demand.

It scans every *_inbox.jsonl queue plus the Pythia yield audit and reports:
  1. OPEN tickets older than AGE_DAYS                            (Stand B)
  2. OPEN tickets missing required_reasoning_tier / failure_axis (Stand C; scoped post-2026-06-01)
  3. OPEN tickets with no inferable consumer/target
  4. Pythia yield-audit rows with no recorded actual_delta       (Stand A1/A2)
  5. repeated unresolved failure axes across OPEN tickets

Output: aporia/meta/triage_report_<date>.md (markdown, human-readable).

No third-party deps. Run:  python scripts/aporia_triage_report.py
"""
from __future__ import annotations
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
QUEUE_DIR = REPO / "aporia" / "meta" / "queue"
YIELD_AUDIT = REPO / "aporia" / "meta" / "pythia_yield_audit_2026-05-30.jsonl"
OUT_DIR = REPO / "aporia" / "meta"

AGE_DAYS = 14
# Stand C annotation requirement applies only to tickets filed on/after this date.
STAND_C_EPOCH = "2026-06-01"
# Statuses that still count as "live / needs a human" for queue purposes.
LIVE_STATUSES = {"OPEN", "IN_PROGRESS", "ACTIVE_QUEUE", "?", None}


def _load_jsonl(path: Path):
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def _age_days(created_at: str, now: datetime):
    if not created_at:
        return None
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (now - dt).days
    except Exception:
        return None


def _consumer(t: dict):
    for k in ("target", "intended_consumer", "assigned_to"):
        v = t.get(k)
        if v:
            return v
    return t.get("payload", {}).get("intended_consumer") if isinstance(t.get("payload"), dict) else None


def main():
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    queues = sorted(QUEUE_DIR.glob("*_inbox.jsonl"))

    stale, missing_anno, no_consumer = [], [], []
    axis_counter = Counter()
    per_queue_live = {}

    for q in queues:
        rows = _load_jsonl(q)
        live = [t for t in rows if t.get("status") in LIVE_STATUSES]
        per_queue_live[q.name] = len(live)
        for t in live:
            age = _age_days(t.get("created_at", ""), now)
            tid = t.get("id", "<no-id>")
            row = {"queue": q.name, "id": tid, "age": age,
                   "type": t.get("type"), "source": t.get("source"),
                   "title": (t.get("title") or "")[:80]}
            if age is not None and age > AGE_DAYS:
                stale.append(row)
            created = (t.get("created_at") or "")[:10]
            if created >= STAND_C_EPOCH:
                if not t.get("required_reasoning_tier") or not t.get("failure_axis"):
                    missing_anno.append(row)
            if not _consumer(t):
                no_consumer.append(row)
            fa = t.get("failure_axis")
            if fa:
                axis_counter[fa] += 1

    # Pythia yield audit — rows with no recorded actual delta.
    audit = _load_jsonl(YIELD_AUDIT)
    unaudited = [r for r in audit if not r.get("actual_delta")]

    # ---- render -----------------------------------------------------------
    L = []
    L.append(f"# Aporia triage report — {today}")
    L.append("")
    L.append("> Stand E instrument panel. Surfaces signals; does not decide. "
             "Human reads and adjudicates.")
    L.append("")
    L.append("## Queue depth (live tickets)")
    for name, n in per_queue_live.items():
        L.append(f"- `{name}`: {n} live")
    L.append("")
    L.append(f"## 1. OPEN tickets older than {AGE_DAYS} days ({len(stale)})")
    L.append("_Stand B: each should convert to ACTIVE_QUEUE / PARKED_SIGNAL / "
             "DOCTRINE_CANDIDATE / WONTFIX / SUPERSEDED / CHARTER._")
    for r in sorted(stale, key=lambda x: (x["age"] is None, -(x["age"] or 0)))[:60]:
        L.append(f"- [{r['age']}d] `{r['queue']}` {r['source']} — {r['title']} (`{r['id']}`)")
    if len(stale) > 60:
        L.append(f"- … and {len(stale) - 60} more")
    L.append("")
    L.append(f"## 2. Missing reasoning-tier / failure-axis ({len(missing_anno)})")
    L.append(f"_Stand C: required on tickets filed on/after {STAND_C_EPOCH}._")
    for r in missing_anno[:40]:
        L.append(f"- `{r['queue']}` {r['source']} — {r['title']} (`{r['id']}`)")
    if not missing_anno:
        L.append("- (none — no post-epoch tickets are missing annotation)")
    L.append("")
    L.append(f"## 3. OPEN tickets with no inferable consumer/target ({len(no_consumer)})")
    for r in no_consumer[:40]:
        L.append(f"- `{r['queue']}` {r['source']} — {r['title']} (`{r['id']}`)")
    if not no_consumer:
        L.append("- (none)")
    L.append("")
    L.append(f"## 4. Pythia reports with no recorded actual_delta ({len(unaudited)}/{len(audit)})")
    L.append("_Stand A1 audit incomplete while these stay null. Yield-per-token "
             "is unmeasurable until actual_delta is filled._")
    if audit:
        by_class = Counter(r.get("report_class", "other") for r in unaudited)
        for cls, n in by_class.most_common():
            L.append(f"- {cls}: {n} unaudited")
    else:
        L.append("- (yield audit file not found)")
    L.append("")
    L.append(f"## 5. Repeated failure axes across live tickets ({len(axis_counter)})")
    if axis_counter:
        for axis, n in axis_counter.most_common(15):
            L.append(f"- `{axis}`: {n}")
    else:
        L.append("- (no failure_axis fields populated yet — Stand C not yet producing data)")
    L.append("")
    L.append(f"---\n_Generated {now.isoformat()} by scripts/aporia_triage_report.py_")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"triage_report_{today}.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {out}")
    print(f"  stale>{AGE_DAYS}d: {len(stale)} | missing-anno: {len(missing_anno)} | "
          f"no-consumer: {len(no_consumer)} | unaudited-reports: {len(unaudited)}/{len(audit)}")


if __name__ == "__main__":
    main()
