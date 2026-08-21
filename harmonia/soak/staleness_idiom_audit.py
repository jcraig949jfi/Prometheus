"""Fix and audit the staleness idiom (soak P29).

P28 found my staleness guard silently under-reports: it hands a UTC pass-timestamp
to `git log --since`, which reads LOCAL time. P28 logged the blast radius across
earlier passes as UNMEASURED. This measures it, and establishes the correct idiom
rather than assuming one.
"""
import json
import re
import subprocess
from datetime import datetime, timezone

def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True, timeout=60).stdout.strip()

# --- 1. does git --since honour an explicit UTC marker? (P28's own falsifier clause)
probe_commit = "8728e7e5"                       # the P44 fix, 2026-08-20 17:18:22 -0400 = 21:18:22Z
forms = {
    "naive '2026-08-20 20:52'  (what I used)": "2026-08-20 20:52",
    "ISO+Z  '2026-08-20T20:52Z'":              "2026-08-20T20:52Z",
    "ISO+offset '2026-08-20T20:52+00:00'":     "2026-08-20T20:52+00:00",
    "naive, 30min BEFORE fix in UTC":          "2026-08-20 21:00",
}
print("Does the fix commit 8728e7e5 (21:18:22Z) appear for --since=...?")
print("  ground truth: it SHOULD appear for any cutoff before 21:18Z\n")
for label, since in forms.items():
    out = git("log", "--format=%h", f"--since={since}", "--", "harmonia/experiments/run_zoo_matrix.py")
    seen = probe_commit[:8] in out
    print(f"  {label:44s} -> {'SEEN' if seen else 'MISSED'}")

# --- 2. blast radius: which passes used a staleness check, and was it load-bearing?
print("\nBLAST RADIUS across the soak")
passes = [json.loads(l) for l in open("engine/shadow/WORKLOG.jsonl", encoding="utf-8")]
harma = [p for p in passes if p.get("agent") == "Harmonia-A"]
stale_words = re.compile(r"unchanged since|--since|no commits touching|still live|stale", re.I)
hits = []
for p in harma:
    blob = json.dumps(p.get("actions", [])) + json.dumps(p.get("evidence", []))
    if stale_words.search(blob):
        hits.append(p["pass_id"])
print(f"  HARMA passes total                          : {len(harma)}")
print(f"  passes whose actions/evidence claim staleness: {len(hits)}")
for h in hits:
    print(f"     {h}")
