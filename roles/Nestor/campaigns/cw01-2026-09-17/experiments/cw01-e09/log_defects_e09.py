"""Append cw01-e09 defects to the campaign ledger, ASCII-safe, idempotent by id."""
from __future__ import annotations

import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent


def _bootstrap_lib():
    for cand in [HERE] + list(HERE.parents):
        if (cand / "lib" / "repopath.py").exists():
            sys.path.insert(0, str(cand / "lib"))
            return cand / "lib"
    raise RuntimeError("cannot locate lib/repopath.py walking up from %s" % HERE)


_bootstrap_lib()
import repopath as RP          # noqa: E402
import recordsafety as RS      # noqa: E402

CAMPAIGN = RP.find_campaign_root(HERE)
LEDGER = CAMPAIGN / "DEFECTS.jsonl"
E, C = "cw01-e09", "cw01-2026-09-17"

ENTRIES = [
    {"id": "CW01-D068", "experiment_id": E, "phase": "RECONCILE", "severity": "critical", "category": "world",
     "status": "OPEN", "defect_class": "A - science blocker (the question cannot be posed)",
     "title": "e09 substrate has no organism-side composition: the organism's only act is one 3-bit nudge per tick",
     "evidence": "np_world.py:92-102 / wforge world.py:212-229: x = action % 8; pend[target] += x * 251; the world's own affine maps then transform every register (np_world.py:112-114). The TT organism (genomes.py:213-263) selects a codebook row that is a constant. No operation selection, no invocation, no argument, no organism-owned workspace, no reuse. The only native chain form, c3_ecology.py's straight-line 'program' (ops add/sub/mul/xor/and/or on hex digits), was never a world policy and has no reuse (one consumer per intermediate).",
     "proposed_fix": "Closed INCONCLUSIVE / DESIGN UNREACHABLE at reconcile per the brief. A future attempt needs a new organism family with selectable, chainable operations over an owned workspace, and a world screen on which capability generalises to held-out seeds. Substrate build work, not an interface.",
     "found_by": "e09 reconcile from code"},
    {"id": "CW01-D069", "experiment_id": E, "phase": "RECONCILE", "severity": "high", "category": "observation",
     "status": "OPEN", "defect_class": "C - observation; logged and continued",
     "title": "e09 probe: digit-program policies in w13 overfit the 8 train seeds and sit at or below the abstain floor on held64",
     "evidence": "PROBE_E09.json. Single-op exhaustive (2400): train max 1386 vs abstain 1272; held64 of the best-by-train 142.5, max over the top 64 = 159.0 (the abstain floor), 0/64 competent. 3-op arithmetic chains (4 lineages x 150 gens): train 1661-1828, held64 145.6-148.7. Scrambled random op tables: train 1729-1868, held64 148.6-166.2. Depth raises train fitness and nothing survives held64; scrambled equals arithmetic. Same pattern as e08 D065 (TT lineages competent on held64 only 2/4 pilots): train8 selection on w13 rewards seed-specific register trajectories.",
     "proposed_fix": "Not acted on here. For the substrate: any future world screen should select on more train seeds or score generalisation directly, because w13's train8 fitness is only loosely coupled to held64 capability across three organism families now (TT, single-op, chain).",
     "found_by": "e09 reconcile probe"},
]


def main():
    existing = set()
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if line.strip():
            existing.add(json.loads(line)["id"])
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    added = []
    with LEDGER.open("a", encoding="utf-8") as fh:
        for e in ENTRIES:
            if e["id"] in existing:
                continue
            rec = {"id": e["id"], "ts": ts, "campaign_id": C}
            rec.update({k: v for k, v in e.items() if k != "id"})
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
            added.append(e["id"])
    v = RS.require_ascii_safe(LEDGER)
    t = RS.derive_tally(LEDGER)
    print("appended %s | %s | total %d | e09 %s" % (added, v["outcome"], t["total"], t["per_experiment"].get("e09")))


if __name__ == "__main__":
    main()
