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
    {"id": "CW01-D066", "experiment_id": E, "phase": "CLOSE_SCIENCE", "severity": "critical", "category": "preregistration",
     "status": "OPEN", "defect_class": "A - science blocker (the question could not be verified)",
     "title": "e08 minimum-count rule frozen against a pilot that predicted marginal attainability; contrast NOT_VERIFIED",
     "evidence": "PREREGISTRATION section 5 requires at least 6 competent lineages per TAX level (of 16) and 4-each-way common support. The disjoint pilot had ALREADY shown (D065) that only 2/4 no-tax lineages reach a held64-competent representative, i.e. an expected ~8 of 16 per level with wide variance - marginal against 6 - and I froze the rule anyway. EXECUTE: competent lineages CONTROL 2/8, TAX 1/8, AMP 2/8, TAX+AMP 3/8 -> 4 per TAX level; common support fails. Disposition INCONCLUSIVE by the frozen rules. The descriptive table is unambiguous and is NOT promoted: scalar burden (all representatives) CONTROL 1.725, TAX 0.834, AMP 0.926, TAX+AMP 0.512, at mean held64 155.7 / 155.4 / 156.0 / 171.2; params 2943 / 1199 / 768 / 377; bits 27.6 / 10.6 / 33.5 / 15.4. The non-competent excess rule (TAX minus no-TAX <= 2 per level) PASSED (+1, -1): the tax did not remove competence relative to control.",
     "proposed_fix": "NOT relaxed post hoc. This is the fourth instance of the eligibility-count lesson in the campaign and the first where the count WAS available and was misread as sufficient. A future attempt must (a) make competence attainable on held64 in most lineages before freezing (more generations, or representatives selected by held-out score on a disjoint selection seed set, or a competence floor defined on the assay distribution), and (b) set the minimum count from the pilot's competent-lineage RATE with a margin, or choose the lineage count to guarantee it. Everything else in the design held: accounting, sham, fixtures, contract, blinded assay.",
     "found_by": "analyze_e08.py under the frozen contract"},
    {"id": "CW01-D067", "experiment_id": E, "phase": "PACKAGE", "severity": "medium", "category": "durability",
     "status": "FIXED", "defect_class": "B - execution/recoverability",
     "title": "e08 fossil of representative genomes was written as .npz, which the repo .gitignore silently excludes",
     "evidence": ".gitignore line 492 'roles/**/*.npz' matched fossils/representatives.npz; git status showed the directory as ignored, so the preserved lineages would never have been committed and a recovering executor would have found no fossil.",
     "proposed_fix": "A .bin form was ignored as well (line 494 'roles/**/*.bin'); only JSON survives under roles. Converted to fossils/representatives.json: base64 of the raw uint8 records with sha256, shape, record_nbytes, contract hash and per-record arm/lineage/rep/sha; npz and bin removed; verified not ignored and round-trips. Standing rule: run git check-ignore on any new artefact type before relying on it as durable.",
     "found_by": "git status after EXECUTE"},
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
