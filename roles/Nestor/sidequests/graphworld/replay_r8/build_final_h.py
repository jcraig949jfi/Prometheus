"""H R8 FINAL.json builder. Accumulated during the round; re-run to regenerate. H files no experiment receipts:
H is the judge, so its products are replays (replay_r8/*.json), rule-consistency checks and disputes."""
import json
import subprocess
import time

from primordial.fabric import telemetry as TM

REPLAYS = [
    # (subject, predicate_event_id, rows/record, replay report, judge result, layer notes)
    ("G Route B (4 PENDING R16 train128 cells)", None, "primordial/ledger/qd/r8_route_b.json",
     "replay_r8/G-route-b.json", "AGREE: SURVIVAL_IMPOSSIBLE 4/4, robust to 24 family orders x 4 bootstrap seeds",
     "bus 1789593219810-0"),
    ("D-R8-1-byte-parity-rerank", "1789592362632-0", "primordial/ledger/rows/D/D-R8-1-byte-parity-rerank.jsonl",
     "replay_r8/D-R8-1.json", "AGREE: INDETERMINATE (binding cheat oracle < 14/16 on 4 rank-1 cells; honest oracles "
     "clean 21/21); values not re-scored (no elite bytes)", "bus 1789593625906-0; receipt 1789593602625-0"),
    ("C-R8-AP-01", "1789592531410-0", "primordial/ledger/rows/C/C-R8-AP-01-pairwise-d1-corruption-graphblas.jsonl",
     "replay_r8/C-R8-AP-01.json", "ARITHMETIC AGREE (PASS, 96 runs re-scored, 0 mismatches); READING DISPUTED: "
     "pressure claim VACUOUS (post hoc power analysis, disclosed)", "bus 1789594234509-0; R8_DISPUTES.json"),
    ("E-R8-H1-sham-response-curve", "1789593327107-0", "primordial/ledger/rows/E/E-R8-H1-sham-response-curve.jsonl",
     "replay_r8/E-R8-H1.json", "AGREE: FLAT_NO_SYSTEMATIC_RESPONSE + CHARGE_ALIGNMENT_NO_EFFECT (independent estimators, "
     "no fragile p); bounded null L0-L4 [-1.31, 0.87]; scale-only L4 beats scratch +2.10 [1.19, 2.98] (descriptive)",
     "bus 1789599171523-0"),
]

doc = {
    "schema_version": "FINAL_v1", "round_id": "r8", "lane": "H", "generated_ts": round(time.time(), 3),
    "code_sha": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
    "receipts": [],
    "row_files": [],
    "candidates": [],
    "why_not_run": [
        {"event_id": None, "item": "H3 historical tie-stability replay",
         "reason": "its tie-aware gate is D's PC 1789517018361-0, unbuilt; prompts_r8/H.md item 4 says skip",
         "projection": {"blocked_on": "PC 1789517018361-0", "cpu_s": None}},
    ],
    "unresolved_claims": [
        {"claim": "JUDGE REPLAY " + s + " -> " + res + " [record " + rec + "; report " + rep + "; " + refs + "]",
         "ref": pe} for s, pe, rec, rep, res, refs in REPLAYS
    ] + [
        {"claim": "DISPUTE vs C (not vs A): C-R8-AP-01 PASS reproduced; its pressure claim read VACUOUS by H. "
                  "Both positions preserved in R8_DISPUTES.json; A accepted the packet guards (1789595248255-0).",
         "ref": "1789594234509-0"},
        {"claim": "INSTRUMENT NOTE: C's AP planted nulls cannot PASS by construction (P2 FLOOR = best non-observing "
                  "output), so NULL_CHECK FAIL does not demonstrate discrimination. Filed before any null row.",
         "ref": "1789593220138-0"},
        {"claim": "JUDGE PREREGISTRATION for AP-02/AP-03: MDD80 reading rule, fixed before any cell row "
                  "(code 42dad4c7f).", "ref": "1789595069735-0"},
        {"claim": "CHECKER GAP (no action, execute order): BETA_SWEEP, SHAM_RESPONSE and DESCRIPTOR_ROBUSTNESS are not "
                  "in evidence_n.VERDICT_CLASSES; a VERDICT on BETA_SWEEP is not sample-checked. D-R8-2 declares a "
                  "conforming 32/4/8 anyway.", "ref": "1789595069735-0"},
        {"claim": "anti_prior.write_residue emits status=None rows refused by G1 lint (A 1789591818153-0); r8 rejected "
                  "set not committed to a file, recoverable from pm:prior:r8:candidates. H's for r9, not fixed now.",
         "ref": "1789591818153-0"},
    ],
    "self_disclosed_errors": [
        {"error": "Stated D-R8-1's cheat-oracle shortfall as oracle POWER as if verified; the rows cannot separate "
                  "power from defect. Downgraded to a hypothesis.", "ref": "1789593632354-0", "repaired": True},
        {"error": "Judge preregistration post cited 90458d47b for the MDD80 code; it is at 42dad4c7f.",
         "ref": "1789595101906-0", "repaired": True},
    ],
    "disputes_with_A": [],
    "interventions_received": [
        {"event_id": "1789592825696-0", "summary": "A relaunched H at 17:07 on prompts_r8 (build session had stopped)"},
        {"event_id": "1789591818153-0", "summary": "A: write_residue defect filed, H not to fix it now"},
        {"event_id": "1789595248255-0", "summary": "A accepted both C-R8-AP-01 packet guards; apply same lens to AP-02/03"},
        {"event_id": "1789595293221-0", "summary": "A: accumulate FINAL.json while running"},
    ],
    "job_status_counts": {},
    "notes": "H ran no worker and filed no receipts: every replay is a re-derivation from committed rows (seconds of "
             "CPU), producing no rows file. Layers kept separate: OBSERVATION = the rows; ELIGIBILITY = rule_consistency "
             "+ balance; VERDICT = the preregistered primary, reproduced or not; INTERPRETATION = what the verdict "
             "licenses (the only layer H disputed).",
}
TM.write_final("roles/Nestor/sidequests/graphworld/finals_r8/H.json", doc)
print("FINAL valid; unresolved", len(doc["unresolved_claims"]), "errors", len(doc["self_disclosed_errors"]))
