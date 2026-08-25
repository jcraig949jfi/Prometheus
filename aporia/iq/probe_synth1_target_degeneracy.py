"""probe_synth1_target_degeneracy.py — is the SYNTH-1 target measurable at all?

IQ-PORT-1's inventory showed canary:vacuous_truth has only two distinct prompt strings and
the correct answer begins "Yes" in 5/5. That is an INSPECTION. This converts it into a
measurement: build the cheapest possible answer-counterfeit -- a scorer that ignores the
problem entirely and picks the candidate with a fixed prefix -- and see what it scores.

A counterfeit that scores 5/5 means the category cannot discriminate synthesis from a
constant, and SYNTH-1 cannot be measured on those 5 tasks.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
for p in (ROOT/"apollo"/"src", ROOT/"apollo"/"scripts", ROOT/"agents"/"hephaestus"/"src"):
    sys.path.insert(0, str(p))

canary = json.loads((ROOT/"apollo"/"data"/"clean_canary_v01.json").read_text(encoding="utf-8"))["tasks"]

for cat in ("vacuous_truth", "consistency_check", "temporal_ordering", "all_but_n"):
    ts = [t for t in canary if t.get("category") == cat]
    prompts = Counter(t["prompt"] for t in ts)
    print(f"\n{cat}: n={len(ts)} distinct_prompts={len(prompts)}")
    # cheapest counterfeit family: pick the candidate starting with a fixed token
    best = None
    tokens = set()
    for t in ts:
        for c in t["candidates"]:
            tokens.add(c.split()[0])
    for tok in sorted(tokens):
        hits = 0
        for t in ts:
            pick = next((c for c in t["candidates"] if c.split()[0] == tok), None)
            hits += (pick == t["correct"])
        if best is None or hits > best[1]:
            best = (tok, hits)
    print(f"  best fixed-prefix counterfeit: pick '{best[0]}...' -> {best[1]}/{len(ts)}")
    # position counterfeit: always pick candidate index i
    pos = [sum(1 for t in ts if len(t['candidates'])>i and t["candidates"][i]==t["correct"])
           for i in range(4)]
    print(f"  fixed-position counterfeit by index: {pos} (max {max(pos)}/{len(ts)})")
    # distinct correct-answer prefixes
    print(f"  correct-answer first tokens: {Counter(t['correct'].split()[0] for t in ts)}")
