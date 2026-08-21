"""Audit SOAK_LOG.md against WORKLOG.jsonl before the verdict rests on it (soak P46).

The final pass cites SOAK_LOG as the verdict's evidence artifact. This soak has twice
found a document drifted from the data it describes (ATTACK_PATTERNS, P41/P42). The
same check has never been run on my own document.

Population measured first, per SOAK-110: 110 SOAK ids in the worklog, 64 referenced
in the log, 102 numeric claims, 45 passes, 18 pass sections. Large enough to warrant
a mechanical check.
"""
import json
import re
from pathlib import Path

LOG = Path("harmonia/soak/SOAK_LOG.md").read_text(encoding="utf-8")
recs = [json.loads(l) for l in open("engine/shadow/WORKLOG.jsonl", encoding="utf-8")]
harma = [r for r in recs if r.get("agent") == "Harmonia-A"]

# --- 1. every SOAK id cited in the log must exist in the worklog
log_ids = set(re.findall(r"SOAK-\d+", LOG))
wl_ids = {f["id"] for r in harma for f in (r.get("soak_findings") or []) if f.get("id")}
phantom = sorted(log_ids - wl_ids, key=lambda s: int(s.split("-")[1]))
print(f"1. SOAK ids cited in the log      : {len(log_ids)}")
print(f"   ids recorded in the worklog    : {len(wl_ids)}")
print(f"   CITED BUT NOT IN WORKLOG       : {len(phantom)}  {phantom[:8] if phantom else ''}")
print(f"   in worklog but never cited     : {len(wl_ids - log_ids)}")

# --- 2. does the verdict line's pass count match reality?
m = re.search(r"Withheld — ([a-z\- ]+) passes in", LOG)
WORDS = {"thirty-nine": 39, "forty": 40, "forty-one": 41, "forty-two": 42,
         "forty-three": 43, "forty-four": 44, "forty-five": 45, "forty-six": 46}
claimed = WORDS.get((m.group(1).strip() if m else ""), None)
print(f"\n2. verdict line claims           : {m.group(1).strip() if m else '(not found)'} = {claimed}")
print(f"   HARMA passes in worklog        : {len(harma)}")
print(f"   MATCH                          : {claimed == len(harma)}")

# --- 3. pass sections vs passes run
secs = re.findall(r"^## Pass (\d+)", LOG, re.M)
sec_n = sorted(int(s) for s in secs)
pass_nums = sorted(int(re.search(r"HARMA-P(\d+)", r["pass_id"]).group(1))
                   for r in harma if re.search(r"HARMA-P(\d+)", r["pass_id"]))
print(f"\n3. '## Pass N' sections           : {len(sec_n)}  covering P{min(sec_n)}-P{max(sec_n)}")
print(f"   passes actually run            : {len(pass_nums)}  covering P{min(pass_nums)}-P{max(pass_nums)}")
missing = [p for p in pass_nums if p not in sec_n]
print(f"   passes with NO section         : {len(missing)}  {missing[:12]}{'...' if len(missing) > 12 else ''}")

# --- 4. is SOAK-08's stated status consistent with the reviews?
revs = [json.loads(l) for l in open("engine/shadow/REVIEWS.jsonl", encoding="utf-8")]
harma_revs = [r for r in revs if "HARMA" in json.dumps(r)]
triage = [r for r in harma_revs if "TRIAGE" in json.dumps(r).upper()]
print(f"\n4. reviews referencing HARMA      : {len(harma_revs)} (triage-scoped: {len(triage)})")
print(f"   log says SOAK-08 remains open  : {'SOAK-08 remains open' in LOG or 'SOAK-08 REMAINS OPEN' in LOG}")
print(f"   log still claims 'never engaged': {'has never engaged' in LOG}")

print("\nVERDICT-READINESS:")
issues = []
if phantom: issues.append(f"{len(phantom)} cited-but-absent SOAK ids")
if claimed != len(harma): issues.append("pass count mismatch")
if missing: issues.append(f"{len(missing)} passes undocumented by a section")
print("  " + ("; ".join(issues) if issues else "no discrepancies found"))
