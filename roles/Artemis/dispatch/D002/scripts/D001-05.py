"""Re-check of D001-05 counts. Not executed by the worker.

Inputs (repo @ 0424c372a6bba88f50d31f3abbd8b1204871bba6):
  aporia/docs/gemini_research_queue/queue.jsonl
  aporia/docs/gemini_research_queue/fired_log.jsonl
  aporia/docs/deep_research_reports/  (Moros report count)

Decision: REPORT.md claims fired=53, unfired=370, and that the fired set equals the
fired_log DR-id set, with all fired dates in 2026-05-13..14; plus 32 Moros reports.
Any other output falsifies the corresponding claim (C1/C2/C4/C8).
Run from repo root: python analysis.py
"""
import json
import pathlib
from collections import Counter

Q = pathlib.Path("aporia/docs/gemini_research_queue")

queue = [json.loads(l) for l in (Q / "queue.jsonl").read_text().splitlines()
         if l.strip() and not l.startswith("#")]
fired = {e["id"] for e in queue if e.get("fired")}
print("1. queue entries:", len(queue), "fired:", len(fired), "unfired:", len(queue) - len(fired))
print("   tier x fired:", sorted(Counter((e["tier"], bool(e.get("fired"))) for e in queue).items()))

log = [json.loads(l) for l in (Q / "fired_log.jsonl").read_text().splitlines()
       if l.strip() and not l.startswith("#")]
log_dr = {r["id"] for r in log if r["id"].startswith("DR-")}
print("2. fired_log rows:", len(log), "DR ids:", len(log_dr),
      "dates:", sorted(Counter(r["fired_date"] for r in log).items()))
print("   queue-fired == log DR ids:", fired == log_dr,
      "only-in-queue:", sorted(fired - log_dr), "only-in-log:", sorted(log_dr - fired))

moros = sorted(pathlib.Path("aporia/docs/deep_research_reports").rglob("*moros_cross_pollination*"))
print("3. Moros reports:", len(moros))
