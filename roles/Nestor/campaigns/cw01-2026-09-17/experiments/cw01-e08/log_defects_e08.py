"""Append cw01-e08 defects to the campaign ledger, ASCII-safe, idempotent by id."""
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
E, C = "cw01-e08", "cw01-2026-09-17"

ENTRIES = [
    {"id": "CW01-D062", "experiment_id": E, "phase": "QUALIFY", "severity": "low", "category": "fixture",
     "status": "FIXED", "defect_class": "B - checker repair (demonstrated once, continued)",
     "title": "e08 Q6-2 'reduced participation' fixture did not reduce participation",
     "evidence": "The fixture organism was built with every codebook row set to action 7 (the costliest) but its tensor-train forward still chose the abstain row often enough to survive all 32 ticks on all 64 held seeds (live ticks 2048/2048, held64 91). A constant-action probe showed action 7 alone dies at ~tick 25 (25.6 live ticks, final charge 0), so early death IS reachable in w13; the fixture had simply not forced it. QUALIFY run 1 reported the fixture WRONG for that reason.",
     "proposed_fix": "Fixture rebuilt so the forward CANNOT abstain: all cores masked (the contraction becomes a fixed vector v) and the readout set so index 1 always wins for that v; verified always_acts_7 on 64 random observations. No predicate, threshold or accounting rule changed. Record preserved as QUALIFY_run1.json.",
     "found_by": "QUALIFY run 1"},
    {"id": "CW01-D063", "experiment_id": E, "phase": "QUALIFY", "severity": "low", "category": "fixture",
     "status": "FIXED", "defect_class": "B - checker repair (demonstrated once, continued)",
     "title": "e08 Q6-2 comparator measured static burden against the wrong organism",
     "evidence": "QUALIFY run 2: the repaired fixture died early as intended (1638/2048 live ticks, held64 0.0) but the checker compared its static burden with fixture 1's abstainer, a different genome with a different read mask, and reported WRONG. The accounting was correct; the comparator's reference was not the fixture's own abstaining twin.",
     "proposed_fix": "Comparator now builds the SAME genome with the codebook zeroed and requires equal static burden against it, plus lower live ticks and non-competence. QUALIFY run 3: CHARGED_LOWER_WORK_VISIBLE; all seven predicates pass. Record preserved as QUALIFY_run2.json.",
     "found_by": "QUALIFY run 2"},
    {"id": "CW01-D064", "experiment_id": E, "phase": "QUALIFY", "severity": "info", "category": "preregistration",
     "status": "OPEN", "defect_class": "C - observation; logged and continued",
     "title": "e08 Q3 selection rule picks the top of the sweep because criterion (d) cannot bind at the upper end",
     "evidence": "The preregistered rule freezes lambda as the LARGEST swept fraction satisfying (a) gradient, (b) competence attainable, (c) inactivity not optimal, (d) dynamic range >= 0.5 of the lambda=0 spread. Measured curve: every fraction from 0.125 to 2.0 qualifies; (d) grows with lambda (1.01 -> 1.82) rather than shrinking, so it never limits the upper end, and (b)/(c) hold up to 2.0 x lambda_max because the train-seed headroom (median competent fit 2052 vs abstain 1272, H = 780) is far larger than the ledger's held64 headroom (16 per seed). Frozen lambda = 390 = 2 x lambda_max: a max-burden organism pays 1560, about its whole fitness; a minimum-burden one pays ~120.",
     "proposed_fix": "NOT changed: the rule was preregistered and is followed as written; the full curve is published in QUALIFY.json. Consequence to watch at analysis: if the TAX arms lose competence (non-competent excess > 2 per level) the preregistered disposition is INCONCLUSIVE, which is the honest outcome of a tax this strong. A future preregistration should bound the sweep by a criterion that CAN bind above (e.g. the median competent organism must retain at least half its headroom under the tax at its own burden).",
     "found_by": "reading the Q3 curve after the run"},
    {"id": "CW01-D065", "experiment_id": E, "phase": "QUALIFY", "severity": "info", "category": "observation",
     "status": "OPEN", "defect_class": "C - observation; logged and continued",
     "title": "e08 pilot competence on held64 is a 2/4 lineage affair; Q4 passed via local accessibility",
     "evidence": "Four 400-generation no-tax pilots all reach train fitness ~2000 (abstain 1272) but only 2/4 have a representative above the held64 competence floor 166.47 (elite held64 107.8-186.1, 16/32 competent). Train seeds are overfit relative to held64. Q4 passed by branch A (single-bond truncation retains competence on 80% of eligible truncations), not branch B (needs 3/4).",
     "proposed_fix": "No change. Recorded so the analysis reader expects a substantial non-competent count in EVERY arm and reads the competence-excess rule (TAX minus no-TAX <= 2 per level) rather than absolute counts.",
     "found_by": "QUALIFY run 3"},
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
    print("appended %s | %s | total %d | e08 %s" % (added, v["outcome"], t["total"], t["per_experiment"].get("e08")))


if __name__ == "__main__":
    main()
