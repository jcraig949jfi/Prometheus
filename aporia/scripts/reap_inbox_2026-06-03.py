"""One-off Aporia inbox triage — 2026-06-03.

Reaps the OPEN backlog in aporia/meta/queue/aporia_inbox.jsonl:

  1. Polyhymnia self-improvement-approval-request (SPAWN_SIBLING_SCOUR) x163
     -> RESOLVED_NOOP. The adaptation's apply() is _adapt_stub_log_only
        (daemon.py:257,291): a no-op placeholder. Approving accomplishes
        nothing. Root cause is a bounded-menu wall (feedback_gen_30_wall),
        not a missing approval. Disposition points to the verdict ticket.

  2. Polyhymnia self-improvement-menu-exhausted (if any) -> RESOLVED, same
     verdict pointer.

  3. saxl-source-pin (P1 verification-required) -> RESOLVED. Catalog
     tensor_open_problems_v1.md was corrected 2026-05-11 (entry 99 + line
     818): Saxl OPEN, Lee 2025 arXiv:2512.15035 WITHDRAWN, Sellke ->
     Luo-Sellke 2017 fourth-power. Acceptance criteria (1)-(3) met.

  4. Every other OPEN non-Polyhymnia ticket (2026-05-07..15, all >2wk
     stale, superseded by Erebos Phase 3 / Hephaestus / F2 / Pythia work)
     -> CLOSED_STALE with a re-file invitation.

Idempotent: only touches status=='OPEN'. Backs up first. Run with --apply
to write; default is dry-run.
"""
from __future__ import annotations
import json, sys, shutil
from datetime import datetime, timezone
from pathlib import Path

INBOX = Path(__file__).resolve().parents[2] / "aporia" / "meta" / "queue" / "aporia_inbox.jsonl"
NOW = datetime.now(timezone.utc).isoformat()
VERDICT_ID = "T-2026-06-03-aporia-polyhymnia-verdict"
APPLY = "--apply" in sys.argv


def disposition(t: dict):
    """Return (new_status, note) or None to leave untouched."""
    if t.get("status") != "OPEN":
        return None
    src = t.get("source")
    typ = t.get("type")
    tid = str(t.get("id", ""))
    if src == "Polyhymnia" and typ == "self-improvement-approval-request":
        return ("RESOLVED_NOOP",
                "SPAWN_SIBLING_SCOUR.apply is a no-op stub (daemon.py _adapt_stub_log_only); "
                f"approval would do nothing. Bounded-menu wall, not an approval gap. See {VERDICT_ID}.")
    if src == "Polyhymnia" and typ == "self-improvement-menu-exhausted":
        return ("RESOLVED",
                f"Menu-exhaustion acknowledged; real fix is menu growth, not approval. See {VERDICT_ID}.")
    if "saxl-source-pin" in tid:
        return ("RESOLVED",
                "Catalog corrected 2026-05-11 (tensor_open_problems_v1.md entry 99 + line 818): "
                "Saxl OPEN; Lee 2025 arXiv:2512.15035 WITHDRAWN; Sellke->Luo-Sellke 2017 fourth-power. "
                "Residual (audit other 2024-25 'resolved' claims) folded into next DR verification wave.")
    # everything else still OPEN and addressed to aporia: stale coordination/closures
    return ("CLOSED_STALE",
            "Reaped 2026-06-03 — >2wk stale (filed 2026-05-07..15), superseded by post-2026-05-20 "
            "Erebos/Hephaestus/F2/Pythia work. Re-file if still live.")


def main():
    lines = INBOX.read_text(encoding="utf-8", errors="replace").splitlines()
    out, counts = [], {}
    for line in lines:
        s = line.strip()
        if not s:
            continue
        try:
            t = json.loads(s)
        except Exception:
            out.append(s)  # preserve unparseable lines verbatim
            continue
        d = disposition(t)
        if d:
            new_status, note = d
            t["status"] = new_status
            t.setdefault("status_history", []).append(
                {"status": new_status, "at": NOW, "by": "aporia-triage-2026-06-03", "note": note})
            counts[new_status] = counts.get(new_status, 0) + 1
        out.append(json.dumps(t, ensure_ascii=False))

    print("=== disposition counts ===")
    for k, v in sorted(counts.items()):
        print(f"  {v:4d}  {k}")
    print(f"  total touched: {sum(counts.values())}")
    if not APPLY:
        print("\n(dry-run; pass --apply to write)")
        return
    bak = INBOX.with_suffix(".jsonl.bak-2026-06-03")
    shutil.copy2(INBOX, bak)
    INBOX.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"\nwrote {INBOX} ({len(out)} lines); backup {bak}")


if __name__ == "__main__":
    main()
