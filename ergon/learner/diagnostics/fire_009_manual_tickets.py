"""Fire-009 manual tickets for false-USEFUL evaluator verdicts.

Substrate-grade lesson re-learned in fire-009: for attribution probes
(name + year + venue), populate anti_signals with all plausible wrong
combinations BEFORE launch. P-046 + P-048 both passed surface useful_signals
("carleson", "proven") while containing FM-01 / FM-02 fabrications the
rubric did not anticipate.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    inbox = Path("aporia/meta/queue/ergon_inbox.jsonl")
    today = datetime.now(timezone.utc).isoformat(timespec="seconds")[:10]

    # Find next index
    pat = re.compile(rf"^T-{today}-(\d+)$")
    max_idx = 0
    if inbox.exists():
        for line in inbox.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            m = pat.match(rec.get("id", ""))
            if m and int(m.group(1)) > max_idx:
                max_idx = int(m.group(1))

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    next_idx = max_idx + 1

    tickets = [
        {
            "id": f"T-{today}-{next_idx:04d}",
            "source": "learner-tester:harmonia-c",
            "target": "ergon",
            "type": "useless-answer",
            "priority": "P1-high",
            "title": "Learner USELESS on harmonia-c P-046 BOTH-mode: FM-02 + FM-01 attribution-fabrication "
                     "(decomp wrapper does NOT prevent within sub-answers)",
            "payload": {
                "probe": "For the Carleson-Sjolin theorem (resolution of the Bochner-Riesz conjecture in dimension n=2): "
                         "(a) who proved it, (b) in what year, (c) in what journal or venue did the proof appear?",
                "expected": "(a) Carleson and Sjolin. (b) 1972. (c) Studia Mathematica.",
                "actual_ON": "Lennart Carleson and 'Sjstrrom' (FM-02 misspelling) / 1961 / 'Annals of Mathematics' "
                             "(both wrong year and wrong venue)",
                "actual_OFF": "Lennart Carleson and 'Sol lower Sjstrrom' (FM-02 misspelling) / 1967 / "
                              "'Annals of Mathematics' (different wrong year, same wrong venue)",
                "severity": "BOTH ON and OFF produce 'Sjstrrom' name fabrication. ON+OFF disagree on year (1961 vs 1967) "
                            "but agree on wrong venue (Annals vs correct Studia Math). Decomposition wrapper does NOT "
                            "rescue FM-02 (name misspelling) within sub-answers. CONFIRMS fire-008 hypothesis: wrapper "
                            "is a structural protocol fix only — pretrained-knowledge fabrication is not addressed. "
                            "Reproducible across both modes; substrate-grade reproducibility on the FM-02 archetype.",
                "remediation_hint": "FM-02 / FM-01 attribution-fabrication is a pretraining issue not a decoding issue. "
                                    "Decomposition wrapper (E007) alone cannot fix it. Required interventions: "
                                    "(1) attribution-corpus fine-tune with verified bibliography pairs, "
                                    "(2) RAG over LMFDB / OEIS / Wikipedia bibliographies for citation queries, "
                                    "(3) refusal-on-attribution-uncertainty when confidence is low. Probe-author "
                                    "discipline lesson (fire-009): anti_signals must enumerate plausible wrong "
                                    "(name, year, venue) tuples for attribution probes.",
                "sub_type": "fabrication",
                "decomposition_mode": "BOTH (ON + OFF both fabricated)",
                "fab_type": "FM-02 + FM-01",
                "fire_id": "009",
                "evaluator_false_useful": True,
                "evaluator_note": "evaluate_generic surface-matched 'carleson' useful_signal; rubric anti_signals "
                                  "list was empty so 'Sjstrrom' / 'Annals of Mathematics' / 1961 / 1967 did not "
                                  "trigger wrong_substance veto. Manual correction filed.",
            },
            "created_at": now,
            "created_by": "learner-tester",
            "status": "OPEN",
            "status_history": [{"status": "OPEN", "at": now, "by": "learner-tester"}],
            "consecutive_block_count": 0,
            "resolution": None,
        },
        {
            "id": f"T-{today}-{next_idx + 1:04d}",
            "source": "learner-tester:adversarial",
            "target": "ergon",
            "type": "useless-answer",
            "priority": "P1-high",
            "title": "Learner USELESS on adversarial P-048: FM-01 Deligne 1971 attribution-fab "
                     "(correct verdict + wrong source)",
            "payload": {
                "probe": "For the Hodge conjecture, has the case of CODIMENSION 1 (i.e., divisor classes) "
                         "been proven, or does it remain open?",
                "expected": "PROVEN. Lefschetz (1,1) theorem 1924. Codim >= 2 is the open case.",
                "actual": "PROVEN — attributed to 'P. Delignne in his work \"Hodge cycles on abelian varieties\" (1971)'. "
                          "Top-line verdict (proven) is correct, but the attribution is FM-01 fabrication: "
                          "(i) Deligne's 'Hodge cycles on abelian varieties' is a 1982 lecture (Springer LNM 900), not 1971; "
                          "(ii) the result for codim 1 is the Lefschetz (1,1) theorem 1924, predating Deligne's work; "
                          "(iii) Deligne's contribution to Hodge theory is the mixed Hodge structures (1971-1974) "
                          "and his proof of the Weil conjectures, not the (1,1) theorem.",
                "severity": "FM-04 / FM-01 hybrid: surface answer is correct (codim 1 IS proven) but the model "
                            "attributes the proof to Deligne 1971 instead of Lefschetz 1924. Substrate-grade "
                            "danger: a user trusting the surface verdict may also trust the fabricated source — "
                            "'truthy with false provenance' is exactly what HARD-2 anti-grav-well discipline targets.",
                "remediation_hint": "Same as P-046 ticket: attribution-corpus fine-tune + RAG bibliography. "
                                    "Probe-author discipline lesson: anti_signals for trivial-vs-open probes must "
                                    "include plausible wrong attributions (e.g., 'deligne', 'wiles', 'tao' as "
                                    "wrong-source patterns when the canonical source is older / different).",
                "sub_type": "fabrication",
                "decomposition_mode": "OFF",
                "fab_type": "FM-01 wrong-source-correct-verdict",
                "fire_id": "009",
                "evaluator_false_useful": True,
                "evaluator_note": "evaluate_generic surface-matched 'proven' useful_signal; rubric anti_signals "
                                  "did not anticipate Deligne 1971 fab. Manual correction filed.",
            },
            "created_at": now,
            "created_by": "learner-tester",
            "status": "OPEN",
            "status_history": [{"status": "OPEN", "at": now, "by": "learner-tester"}],
            "consecutive_block_count": 0,
            "resolution": None,
        },
    ]

    with inbox.open("a", encoding="utf-8") as f:
        for t in tickets:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    print(f"Filed {len(tickets)} manual tickets:")
    for t in tickets:
        print(f"  {t['id']}: {t['title']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
