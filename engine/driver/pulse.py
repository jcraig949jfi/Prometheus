"""PULSE — the skimmable, query-traceable state page (Alethelia's first organ).

Regenerates engine/PULSE.md from git + queues + liveness. Every line is computed;
nothing is narrated. Anything not computable renders as UNKNOWN(n), never prose
(the anti-confabulation constitution, running on M1 until M4 hosts it).

    python engine/driver/pulse.py
"""
from __future__ import annotations
import json, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
Q = ROOT / "engine" / "queues"


def sh(*args: str) -> str:
    return subprocess.run(args, capture_output=True, text=True, cwd=str(ROOT)).stdout


def jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def main() -> int:
    now = datetime.now(timezone.utc)
    L = []
    L.append(f"# PULSE — generated {now.isoformat(timespec='seconds')}")
    L.append("")
    L.append("*Every line computed from state; nothing narrated. Steer via engine/STEERING.md —")
    L.append("read at every pass start, never blocking. Veto any AUTO-TAKEN row by adding a line there.*")
    L.append("")

    # liveness
    lv = subprocess.run(["python", "engine/driver/liveness.py", "--days", "3"],
                        capture_output=True, text=True, cwd=str(ROOT)).stdout.strip()
    L.append("## Liveness (3-day window)")
    L.append("```")
    L.append(lv if lv else "UNKNOWN(liveness script failed)")
    L.append("```")
    L.append("")

    # recent activity: last 72h non-cron commits
    log = sh("git", "log", "--since=72.hours.ago", "--pretty=%h %ad %s", "--date=format:%m-%d %H:%M")
    lines = [l for l in log.splitlines() if "auto: portfolio" not in l]
    L.append(f"## Commits, 72h (non-cron): {len(lines)}")
    L.extend(f"- {l}" for l in lines[:25])
    if len(lines) > 25:
        L.append(f"- … +{len(lines)-25} more")
    L.append("")

    # decision market
    bots = jsonl(Q / "BOTTLENECKS.jsonl")
    L.append("## Bottleneck hypotheses (confidence)")
    for b in bots:
        flags = " · ".join(k for k in ("probe_2026_08_18", "caution_2026_08_18", "note_2026_08_18") if k in b)
        L.append(f"- **{b['id']}** {b.get('confidence','?')} — {b.get('claim','')[:90]}"
                 + (f"  *[updated: {flags}]*" if flags else ""))
    L.append("")

    moves = jsonl(Q / "MOVES.jsonl")
    L.append("## Moves")
    for m in moves:
        L.append(f"- **{m['id']}** [{str(m.get('status','?'))[:60]}] {m.get('action','')[:80]}")
    L.append("")

    # decisions: pending for James, and auto-taken he may veto
    dec = jsonl(Q / "DECISIONS.jsonl")
    pend = [d for d in dec if d.get("status") == "PENDING-HITL"]
    auto = [d for d in dec if d.get("status") == "AUTO-TAKEN"]
    L.append(f"## Waiting on James (blocking THEMSELVES only): {len(pend)}")
    for d in pend:
        L.append(f"- {d.get('action', d.get('question','?'))}  *(filed {d.get('ts','?')[:10]})*")
    L.append("")
    L.append(f"## Auto-taken decisions (vetoable): {len(auto)}")
    for d in auto[-10:]:
        L.append(f"- {d.get('ts','?')[:10]} **chose:** {str(d.get('chose','?'))[:60]} — {d.get('question','')[:70]}")
    L.append("")

    # work queue
    work = jsonl(Q / "WORK.jsonl")
    by = {}
    for w in work:
        by.setdefault(w.get("status", "?"), []).append(w)
    L.append("## Work queue")
    for st, items in sorted(by.items()):
        L.append(f"- {st}: {len(items)}" + (f" — next: {items[0].get('desc','')[:70]}" if st == "QUEUED" else ""))
    L.append("")

    # findings in last 7d
    f7 = sh("git", "log", "--since=7.days.ago", "--diff-filter=A", "--name-only", "--pretty=format:")
    finds = sorted({l.strip() for l in f7.splitlines() if "FINDING_" in l})
    L.append(f"## Findings, 7d: {len(finds)}")
    L.extend(f"- {f}" for f in finds)
    L.append("")
    L.append("*North-star gauge is yours to make from the above; this page will not narrate it for you.*")

    (ROOT / "engine" / "PULSE.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    # INFRA-PULSE-M4 (P32): mirror to docs/ so GitHub Pages serves it — the
    # dashboard links to it and James can read loop status without a checkout.
    pages_copy = ["<!-- auto-synced from engine/PULSE.md by engine/driver/pulse.py; do not edit -->", ""] + L
    (ROOT / "docs" / "pulse.md").write_text("\n".join(pages_copy) + "\n", encoding="utf-8")
    print(f"PULSE.md written: {len(L)} lines (+ docs/pulse.md mirror)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
