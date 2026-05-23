"""
dr_followup_miner.py — Mine completed DR reports for explicit open-question
phrasings and emit a JSONL of candidate follow-up DR prompts for Aporia's
manual approval.

Design contract (per persona_seed_prompts_2026-05-21.md, Aporia tool #1):
  - Scan aporia/docs/deep_research_reports/**/*.md within a date window
  - Extract phrasings like "open question:", "remains open", "for n>3 open",
    "leave to future work", "we conjecture but do not prove"
  - Output candidates to aporia/docs/gemini_research_queue/dr_followup_candidates_<date>.jsonl
  - DO NOT auto-dispatch. Approval is a separate manual step (Aporia reads
    the candidates JSONL, picks ones to fire, calls Pythia's enqueue or
    seed-from-default with the chosen subset).

Usage:
  python -m aporia.scripts.dr_followup_miner            # default: today's date window
  python -m aporia.scripts.dr_followup_miner --days 7   # mine last 7 days of reports
  python -m aporia.scripts.dr_followup_miner --report   # print summary only, no write

Output schema (one JSON object per line):
  {
    "candidate_id":    "FU-2026-05-21-NNN",
    "source_report":   "aporia/docs/deep_research_reports/2026-05-21/00274_...md",
    "source_queue_ref":"ERG-01",
    "source_row_id":   274,
    "source_title":    "ERG-01: Proof reconstruction x falsification battery x ...",
    "question_text":   "<the open-question phrasing>",
    "context_excerpt": "<±200 chars surrounding the hit>",
    "trigger_pattern": "open_question | remains_open | future_work | ...",
    "discovered_at":   "2026-05-21T21:00:00Z",
    "approval_status": "pending"
  }
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORTS_BASE = REPO_ROOT / "aporia" / "docs" / "deep_research_reports"
OUT_DIR = REPO_ROOT / "aporia" / "docs" / "gemini_research_queue"

# Phrasing patterns. Each is (pattern_name, regex). Patterns are case-
# insensitive. Order matters only for `trigger_pattern` attribution when
# multiple match the same span (first hit wins).
PATTERNS = [
    ("open_question",   re.compile(r"\bopen\s+question[s]?\b\s*[:.\-—]", re.I)),
    ("open_problem",    re.compile(r"\bopen\s+problem[s]?\b\s*[:.\-—]", re.I)),
    ("remains_open",    re.compile(r"\b(?:remain[s]?|stay[s]?|still)\s+open\b", re.I)),
    ("n_case_open",     re.compile(r"\bfor\s+n\s*[=>≥]\s*\d+[^.\n]{0,80}\bopen\b", re.I)),
    ("future_work",     re.compile(r"\b(?:we\s+)?leave[s]?\s+[^.\n]{0,80}\b(?:to|as|for)\s+future\s+work\b", re.I)),
    ("further_needed",  re.compile(r"\bfurther\s+(?:research|work|study|investigation)\s+(?:is|are|will\s+be|would\s+be)\s+(?:needed|required|necessary)\b", re.I)),
    ("not_yet_known",   re.compile(r"\bit\s+(?:is|remains)\s+(?:not\s+yet\s+)?(?:unknown|unclear|open)\s+(?:whether|if|how)\b", re.I)),
    ("conjecture_only", re.compile(r"\bwe\s+conjecture\b[^.\n]{0,120}\bbut\s+do\s+not\s+prove\b", re.I)),
    ("no_proof_yet",    re.compile(r"\b(?:no|without|lacks?)\s+(?:complete\s+)?proof\b[^.\n]{0,80}\b(?:yet|to\s+date|so\s+far)\b", re.I)),
    ("question_mark",   re.compile(r"^\s*[*\-•]?\s*Q[uestion]*[:.]\s+.{15,300}\?$", re.M | re.I)),
]

# Heuristic header parser: Pythia's save_report writes a YAML-ish frontmatter:
#   **Pythia queue id:** 274
#   **Tier:** T4
#   **Priority:** 1
#   **Requested by:** Ergon
#   **Interaction ID:** v1_...
#   **Elapsed:** 306s
#   **Completed at:** 2026-05-21T11:30:56+00:00
#   ---
HEADER_FIELDS = {
    "queue_id":    re.compile(r"\*\*Pythia queue id:\*\*\s*(\d+)"),
    "tier":        re.compile(r"\*\*Tier:\*\*\s*([^\n]+)"),
    "queue_ref":   re.compile(r"\*\*(?:Queue ref|queue_ref):\*\*\s*([^\n]+)"),
    "requested_by":re.compile(r"\*\*Requested by:\*\*\s*([^\n]+)"),
}


def parse_report(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    title = ""
    m = re.match(r"^\s*#\s+(.+)", text)
    if m:
        title = m.group(1).strip()
    header = {}
    for key, rx in HEADER_FIELDS.items():
        m = rx.search(text)
        if m:
            header[key] = m.group(1).strip()
    # body starts after the first `---` separator (after Pythia's header block)
    parts = text.split("\n---\n", 1)
    body = parts[1] if len(parts) == 2 else text
    return {"title": title, "header": header, "body": body, "raw_len": len(text)}


def mine_report(report_path: Path, parsed: dict, candidate_seq: list[int]) -> list[dict]:
    body = parsed["body"]
    out: list[dict] = []
    seen_hashes: set[str] = set()
    for pat_name, rx in PATTERNS:
        for m in rx.finditer(body):
            start, end = m.span()
            ctx_start = max(0, start - 200)
            ctx_end = min(len(body), end + 200)
            excerpt = body[ctx_start:ctx_end].strip()
            # The "question" is the sentence containing the hit. Heuristic:
            # nearest sentence-end on each side.
            qstart = body.rfind(".", ctx_start, start) + 1
            qend = body.find(".", end)
            qend = qend if qend != -1 else min(len(body), end + 300)
            question_text = body[qstart:qend].strip()
            # normalize for dedup
            norm = re.sub(r"\s+", " ", question_text.lower())
            h = hashlib.sha1(norm.encode()).hexdigest()[:16]
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            candidate_seq[0] += 1
            out.append({
                "candidate_id":     f"FU-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-{candidate_seq[0]:03d}",
                "source_report":    str(report_path.relative_to(REPO_ROOT)).replace("\\", "/"),
                "source_queue_ref": parsed["header"].get("queue_ref", ""),
                "source_row_id":    int(parsed["header"].get("queue_id", "0") or 0),
                "source_title":     parsed["title"],
                "source_requested_by": parsed["header"].get("requested_by", ""),
                "question_text":    question_text[:600],
                "context_excerpt":  excerpt[:1000],
                "trigger_pattern":  pat_name,
                "discovered_at":    datetime.now(timezone.utc).isoformat(),
                "approval_status":  "pending",
                "dedup_hash":       h,
            })
    return out


def main():
    ap = argparse.ArgumentParser(description="Mine completed DR reports for follow-up question candidates.")
    ap.add_argument("--days", type=int, default=7,
                    help="number of trailing days of reports to scan (default 7)")
    ap.add_argument("--report-only", action="store_true",
                    help="print summary, do not write JSONL output")
    ap.add_argument("--out", type=Path, default=None,
                    help="output JSONL path (default: dr_followup_candidates_<UTC-date>.jsonl)")
    args = ap.parse_args()

    # Directories are named by local date when Pythia saved the report
    # (see scripts/pythia_daemon.py:report_path_for). Anchor the window on
    # local date but accept UTC date too in case of a midnight straddle.
    today_local = datetime.now().date()
    today_utc = datetime.now(timezone.utc).date()
    date_window = set()
    for i in range(args.days):
        date_window.add(today_local - timedelta(days=i))
        date_window.add(today_utc - timedelta(days=i))

    if not REPORTS_BASE.exists():
        print(f"reports base does not exist: {REPORTS_BASE}", file=sys.stderr)
        return 1

    scanned = 0
    candidates: list[dict] = []
    seq = [0]
    for date_dir in sorted(REPORTS_BASE.iterdir()):
        if not date_dir.is_dir():
            continue
        try:
            d = datetime.strptime(date_dir.name, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d not in date_window:
            continue
        for report in sorted(date_dir.glob("*.md")):
            scanned += 1
            parsed = parse_report(report)
            candidates.extend(mine_report(report, parsed, seq))

    print(f"scanned {scanned} reports across {len(date_window)} date(s)")
    print(f"extracted {len(candidates)} candidate follow-up questions")
    # Per-pattern breakdown
    if candidates:
        from collections import Counter
        by_pat = Counter(c["trigger_pattern"] for c in candidates)
        by_src = Counter(c["source_requested_by"] for c in candidates if c["source_requested_by"])
        print()
        print("by trigger pattern:")
        for pat, n in by_pat.most_common():
            print(f"  {n:4d}  {pat}")
        print()
        print("by source-report requester (top 10):")
        for src, n in by_src.most_common(10):
            print(f"  {n:4d}  {src}")

    if args.report_only:
        return 0

    out_path = args.out
    if out_path is None:
        out_path = OUT_DIR / f"dr_followup_candidates_{today_utc.isoformat()}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for c in candidates:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print()
    print(f"wrote {len(candidates)} candidates to {out_path.relative_to(REPO_ROOT)}")
    print("Manual approval step: read the JSONL, pick rows to fire, then dispatch via")
    print("  python scripts/pythia_daemon.py enqueue \"<title>\" \"<prompt>\" --priority 3")
    return 0


if __name__ == "__main__":
    sys.exit(main())
