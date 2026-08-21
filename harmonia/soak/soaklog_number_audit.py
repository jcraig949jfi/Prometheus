"""Verify SOAK_LOG's numeric claims against the worklog (soak P47).

P46 certified the log on four STRUCTURAL checks and logged WITHHELD that its ~102
numeric claims were never verified. The log is the verdict's evidence artifact, so
those numbers are load-bearing.

METHOD, fixed before running:
  For each '## Pass N' section, extract every numeric token. A token is CORROBORATED
  if it appears verbatim in that pass's worklog record (any field). Tokens that do
  not appear are NOT errors -- they are candidates for hand adjudication, because a
  log may legitimately restate a number in a different form (percent vs fraction,
  rounded, or summed across records).

Deterministic: no sampling, every section checked. No writes.
"""
import json
import re
from pathlib import Path

LOG = Path("harmonia/soak/SOAK_LOG.md").read_text(encoding="utf-8")
recs = {}
for l in open("engine/shadow/WORKLOG.jsonl", encoding="utf-8"):
    r = json.loads(l)
    m = re.search(r"HARMA-P(\d+)", r.get("pass_id") or "")
    if m and r.get("agent") == "Harmonia-A":
        recs[int(m.group(1))] = json.dumps(r)

# split the log into '## Pass N' sections
parts = re.split(r"^## Pass (\d+)", LOG, flags=re.M)
sections = {}
for i in range(1, len(parts), 2):
    sections[int(parts[i])] = parts[i + 1]

NUM = re.compile(r"\b\d+(?:\.\d+)?\b")
STOP = {"0", "1", "2", "3", "4", "5"}          # bare small ints are too common to trace

print(f"{'pass':>5s} {'numbers':>8s} {'corroborated':>13s} {'unmatched':>10s}  unmatched tokens")
print("-" * 96)
tot = corr = 0
unmatched_all = []
for n in sorted(sections):
    blob = recs.get(n)
    if not blob:
        print(f"P{n:<4d} (no worklog record found)")
        continue
    toks = [t for t in NUM.findall(sections[n]) if t not in STOP]
    seen, uniq = set(), []
    for t in toks:
        if t not in seen:
            seen.add(t); uniq.append(t)
    hit = [t for t in uniq if t in blob]
    miss = [t for t in uniq if t not in blob]
    tot += len(uniq); corr += len(hit)
    unmatched_all += [(n, t) for t in miss]
    print(f"P{n:<4d} {len(uniq):>8d} {len(hit):>13d} {len(miss):>10d}  {', '.join(miss[:8])}")

print("-" * 96)
print(f"numeric tokens checked : {tot}")
print(f"corroborated verbatim  : {corr} ({100*corr/tot:.1f}%)" if tot else "none")
print(f"unmatched (to adjudicate): {len(unmatched_all)}")
print()
print("Unmatched tokens are CANDIDATES, not errors — a log may restate a number in a")
print("different form. Each is hand-adjudicated below in the pass record.")

# ---------------------------------------------------------------------------
# CALIBRATION OF THIS AUDIT, run because 100% is the shape that has misled this
# soak repeatedly. Two concerns:
#   (a) P30 reported 0 tokens -- the STOP filter removed every number in a section
#       whose figures are all small (2/4, 4/4, M1-M4).
#   (b) "token appears anywhere in the record JSON" may be unable to FAIL.
# Measure the audit's POWER: perturb each corroborated token and see if the
# matcher would flag the wrong value.
print("\nCALIBRATION — can this matcher detect a WRONG number?")
detected = missed = 0
examples = []
for n in sorted(sections):
    blob = recs.get(n)
    if not blob:
        continue
    toks = [t for t in NUM.findall(sections[n]) if t not in STOP]
    for t in dict.fromkeys(toks):
        if t not in blob:
            continue
        try:
            perturbed = str(int(t) + 1) if "." not in t else str(round(float(t) + 1.0, 1))
        except ValueError:
            continue
        if perturbed in blob:
            missed += 1
            if len(examples) < 6:
                examples.append((n, t, perturbed))
        else:
            detected += 1
tot_p = detected + missed
print(f"  perturbed values tested : {tot_p}")
print(f"  would be FLAGGED        : {detected} ({100*detected/tot_p:.1f}%)" if tot_p else "n/a")
print(f"  would slip through      : {missed} ({100*missed/tot_p:.1f}%)" if tot_p else "n/a")
if examples:
    print("  examples that would slip:", [f"P{n}: {a}->{b}" for n, a, b in examples])
print()
print(f"  STOP filter excluded the tokens 0-5 entirely, which is why P30 shows 0 checked;")
print(f"  its figures (2/4, 4/4) are all inside the excluded range.")
print("\n  The corroboration rate is only meaningful to the extent the matcher can fail.")
