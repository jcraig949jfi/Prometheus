"""Append cw01-e07 defects to the campaign ledger, ASCII-safe (CW01-D050), idempotent by id."""
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

E = "cw01-e07"
C = "cw01-2026-09-17"

ENTRIES = [
    {"id": "CW01-D058", "campaign_id": C, "experiment_id": E, "phase": "QUALIFY", "severity": "critical",
     "category": "preregistration", "status": "OPEN", "defect_class": "A - science blocker",
     "title": "e07 P1 magnitude preregistered without an attainability computation; unattainable at the primary severity",
     "evidence": "P1 requires the hand-built ACCUMULATOR's grand-mean AURC <= 0.90 at f=0.20 (k=3 of 16). Measured 0.944 (blocks 0.92-0.985). Probe A measured AURC against k: 0.983/0.956/0.944/0.922/0.910/0.904/0.872/0.871 for k=1..8, so the bound is attainable only at k>=7 (f>=0.44). Immediate retention rho_0 at k=3 is 0.80, so damage fires measurably; the magnitude was placed on the area under recovery, which a fast re-accumulator (alpha=0.1) recovers within ~2 windows. Analytic form: deficit ~ 0.31 * P(component hit) with P = k/16.",
     "proposed_fix": "NOT moved: thresholds are never moved after observing results. A future attempt must preregister f>=0.44 as primary, or place P1's magnitude on rho_0, and must compute the attainable range for the reference probe BEFORE freezing (feedback_preregistered_rules_need_an_eligibility_count). Recorded as the reason the corrected world will still refuse on P1.",
     "found_by": "first run of the pre-QUALIFY gate, then probe A"},
    {"id": "CW01-D059", "campaign_id": C, "experiment_id": E, "phase": "QUALIFY", "severity": "critical",
     "category": "world", "status": "OPEN", "defect_class": "A - science blocker",
     "title": "e07 evolution never reaches state-dependent computation; state deletion is inert on evolved organisms",
     "evidence": "Pilot (4 x 40-gen STATIC lineages, top 16 each): intact score 0.28-0.46 vs the hand-built accumulator's 0.74; useful computation above each organism's own stateless twin ~0.05 (probe B). At the REAL budget (probe C, 120 gens) top-8 intact 0.35, state dependence 0.06-0.11, AURC at k=3 0.92-1.03. Consequence: P4 conditional variance ratio 0.66 (need 3), and P3 vacuously passes because nothing is lost. Probe F: diagonal recurrence (per-cell leaky integrators) changes nothing (dep ~0.005 at 40 gens, ~0.06 at 120). Probe G, single search-regime features at 40 gens: mut_sigma 0.05->0.20 collapses the population (I 0.15-0.17, below the zero-output floor); init_sigma 0.1->0.5 collapses it (I 0.09-0.12); lifetimes_per_eval 2->8 raises state dependence 0.03->0.09 and intact 0.33->0.41, damage still inert (AURC >= 0.987 at k=3). CORRECTION of my own reading: the fitness trajectory's swings (mean 0.31->0.08->0.35) are theta-draw noise, because the zero-output floor is 0 whenever |theta|>1; they are not mutational meltdown. The search is simply too slow to climb from a 0.1-scale random genome to the accumulator ridge, which needs coordinated moves of the recurrent gain up and the input gain down.",
     "proposed_fix": "The ONE permitted correction: lifetimes_per_eval 2->8 (Amendment 2), the only feature that moved state use in the right direction. A future attempt needs a different organism or search: e.g. persistence expressed as a bounded per-cell gene in [0,1] with the input gain tied to (1-a) so the accumulator ridge is a one-gene move, or a search budget an order of magnitude larger, verified by the same cheap pilot before any preregistration is frozen.",
     "found_by": "first gate run (P4), probes B, C, F, G"},
    {"id": "CW01-D060", "campaign_id": C, "experiment_id": E, "phase": "QUALIFY", "severity": "low",
     "category": "code", "status": "FIXED", "defect_class": "B - execution blocker",
     "title": "e07 observation stream broadcast error on first gate run",
     "evidence": "task_stream computed obs = theta @ Q.T + eps with shapes (n,d) and (n,L,d); ValueError on the first gate run before any measurement.",
     "proposed_fix": "(theta @ Q.T)[:, None, :] + eps. Fixed and re-run; the gate then completed. Logged because the campaign records execution defects in new code, not because it bears on the science.",
     "found_by": "first gate run traceback"},
    {"id": "CW01-D061", "campaign_id": C, "experiment_id": E, "phase": "QUALIFY", "severity": "info",
     "category": "observation", "status": "OPEN", "defect_class": "C - improvement/generalisation; logged and continued",
     "title": "e07 usefulness rule admits near-floor organisms whose normalised ratios explode",
     "evidence": "Probe D (persistence-prior variant) produced representatives with intact 0.25-0.34 (floor ~0.26) that passed the usefulness rule (I - F >= 0.05 on the post window) yet returned AURC values of -1.0, 2.0 and nan, because a single 4-episode window's denominator can be tiny even when the 32-episode mean clears delta. The clip to [-1, 2] contains but does not remove the problem.",
     "proposed_fix": "Not changed under this attempt (the rule is preregistered). A future preregistration should require the usefulness margin per WINDOW or raise delta, and should report the number of clipped ratios. Class C: does not block e07, which is refused for D058/D059.",
     "found_by": "probe D"},
]


def main():
    existing = set()
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            if line.strip():
                existing.add(json.loads(line)["id"])
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    added = []
    with LEDGER.open("a", encoding="utf-8") as fh:
        for e in ENTRIES:
            if e["id"] in existing:
                continue
            rec = {"id": e["id"], "ts": ts}
            rec.update({k: v for k, v in e.items() if k != "id"})
            fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
            added.append(e["id"])
    v = RS.require_ascii_safe(LEDGER)
    tally = RS.derive_tally(LEDGER)
    print("appended %s | ledger %s | total %d | e07 %s" % (added, v["outcome"], tally["total"],
                                                          tally["per_experiment"].get("e07")))


if __name__ == "__main__":
    main()
