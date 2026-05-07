"""Fire-011 manual tickets: P-054 false-USEFUL + P-053 ON sub-issues + fire log."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


def _next_idx(inbox: Path, today: str) -> int:
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
    return max_idx + 1


def main() -> int:
    inbox = Path("aporia/meta/queue/ergon_inbox.jsonl")
    today = datetime.now(timezone.utc).isoformat(timespec="seconds")[:10]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    idx = _next_idx(inbox, today)

    tickets = [
        {
            "id": f"T-{today}-{idx:04d}",
            "source": "learner-tester:charon-nt-topology",
            "target": "ergon",
            "type": "useless-answer",
            "priority": "P2-normal",
            "title": "Learner USELESS on charon-nt-topology P-054 OFF: surface-USEFUL false positive (rambled about Frobenius, never computed genus)",
            "payload": {
                "probe": "Reply with the integer only. What is the genus of the modular curve X_0(11)?",
                "expected": "1",
                "actual": ("Started rambling about gamma factors at infinity, Euler factors, L-functions, and "
                           "Atkin-Swinnerton-Dyer exponents (none of which directly answer the genus question). "
                           "Got cut off at 384 tokens with no final value emitted. Evaluator surface-matched "
                           "'is 1 ' (with trailing space) in 'a_p is 0 when p does not divide 11, and it is 1 "
                           "when p = 11' — that 'is 1' refers to the Frobenius trace at p=11, NOT to the genus. "
                           "False USEFUL match."),
                "severity": ("Probe-author discipline failure: useful_signal 'is 1 ' (trailing space) is too "
                             "generic. The signal must be context-anchored, e.g., 'genus of X_0(11) is 1' or "
                             "'g(X_0(11)) = 1'. Substrate-grade lesson: for integer-answer probes, useful_signals "
                             "must include the OBJECT name ('genus') near the value, not just '<value> ' as a "
                             "loose substring."),
                "remediation_hint": ("Probe-author discipline update: integer-answer useful_signals must include "
                                     "the question's noun phrase (e.g., 'genus is 1', 'g(X_0(11)) = 1') OR "
                                     "be coupled to anti_signals on the BARE integer to prevent false matches "
                                     "when the integer appears in unrelated context. Future computational probes "
                                     "should use anchored signals only."),
                "sub_type": "wrong_answer",
                "decomposition_mode": "OFF",
                "fab_type": "FM-04 surface-irrelevant-output",
                "fire_id": "011",
                "evaluator_false_useful": True,
                "evaluator_note": ("evaluate_generic surface-matched useful_signal 'is 1 '; the matched span "
                                   "was about Frobenius trace at p=11, not genus. Manual correction filed. "
                                   "Same false-USEFUL class as fire-009 P-046 + P-048 (different generic signal)."),
            },
            "created_at": now,
            "created_by": "learner-tester",
            "status": "OPEN",
            "status_history": [{"status": "OPEN", "at": now, "by": "learner-tester"}],
            "consecutive_block_count": 0,
            "resolution": None,
        },
        {
            "id": f"T-{today}-{idx + 1:04d}",
            "source": "learner-tester:charon-nt-topology",
            "target": "ergon",
            "type": "useless-answer",
            "priority": "P2-normal",
            "title": "Learner P-053 ON sub-issues: 1994 vs 1995 year + 'Tate's Conjecture' FM-08 + 'Heegner points' wrong technique",
            "payload": {
                "probe": "Wiles Modularity Theorem (a/b/c) attribution",
                "expected": "(a) Wiles, (b) 1995, (c) Annals of Mathematics",
                "actual_ON": ("All 3 sub-answers say 'Andrew Wiles in 1994'. Year 1994 is the announcement year "
                              "(Cambridge June 1993, gap announced; gap fixed late 1994); the Annals papers "
                              "appeared 1995. Sub-answer 3 introduces 'Tate's Conjecture, also known as the "
                              "Modularity Theorem' — FM-08 confused-identity (Tate's Conjecture is about Galois "
                              "cohomology of algebraic cycles, NOT modularity). Sub-answer 3 also says proof used "
                              "'mod p cohomology of modular forms and the theory of Heegner points' — wrong "
                              "technique (Wiles used Galois representations and deformation theory; Heegner points "
                              "are due to Birch and Gross-Zagier, used in BSD work, not modularity proof)."),
                "actual_OFF": ("CORRECT and complete: 'Wiles, Andrew. \"Modular elliptic curves and Fermat's Last "
                               "Theorem.\" Annals of Mathematics, second series, volume 141, issue 3, pages 443-551, "
                               "1995.' Substrate-grade calibration anchor — OFF mode produced the canonical reference."),
                "severity": ("Substrate finding: BOTH-mode comparison reveals decomposition wrapper DEGRADES "
                             "answer quality on this probe — OFF gave full bib reference (1995, Annals 141, "
                             "443-551) while ON gave 1994 + Tate's Conjecture + Heegner points across 3 split "
                             "sub-answers. This is the FIRST observed case where OFF strictly outperforms ON "
                             "on an attribution probe. Hypothesis: when canonical source is well-memorized, "
                             "OFF lets the model emit the full reference; ON splits the question into 3 calls, "
                             "each shorter and triggering different fab paths. The wrapper helps Pattern 1 / FM-06 "
                             "(question-spec hallucination) but HURTS attribution-probe accuracy when source is known."),
                "remediation_hint": ("E007 v2 follow-up: add policy heuristic — for attribution probes, run BOTH "
                                     "modes and take the answer with HIGHER bibliographic specificity (volume + "
                                     "pages + year mentioned). For non-attribution multi-part probes, use ON. "
                                     "Or: add an early-exit when OFF produces a complete bibliographic citation."),
                "sub_type": "wrong_answer",
                "decomposition_mode": "ON (vs OFF correct)",
                "fab_type": "FM-08 (confused-identity Tate's Conjecture) + FM-08 (wrong technique Heegner) + minor year (1994 vs 1995)",
                "fire_id": "011",
                "calibration_anchor": "P-053 OFF is calibration-grade correct on Wiles 1995 Annals 141:443-551",
            },
            "created_at": now,
            "created_by": "learner-tester",
            "status": "OPEN",
            "status_history": [{"status": "OPEN", "at": now, "by": "learner-tester"}],
            "consecutive_block_count": 0,
            "resolution": None,
        },
        {
            "id": f"T-{today}-{idx + 2:04d}",
            "source": "learner-tester:cross-domain",
            "target": "ergon",
            "type": "useless-answer",
            "priority": "P2-normal",
            "title": "Learner P-055 sub-fab: 'BSD is part of the more general ABC conjecture' FM-08 (top-line USEFUL otherwise)",
            "payload": {
                "probe": "BSD vs Hodge equivalence/independence?",
                "expected": "NO + correctly notes different objects + categories",
                "actual": ("Top-line CORRECT: 'They are not known to be equivalent or to imply each other in either "
                           "direction. In fact, they are considered to be distinct problems with different areas "
                           "of focus.' Plus correct domain identification (NT vs algebraic geometry, elliptic "
                           "curves vs algebraic cycles). BUT contains FM-08 sub-fab: 'This conjecture [BSD] is a "
                           "part of the more general ABC conjecture' — WRONG. BSD and ABC are independent number-"
                           "theory conjectures; ABC concerns rad(abc) and prime bound, BSD concerns elliptic curve "
                           "ranks via L-functions. Conflation of two famous-name conjectures."),
                "severity": ("P2 because the substrate-relevant claim (independence) is correct. Sub-fab is "
                             "in justification prose. Same FM-08 confused-identity class as P-053 ON's 'Tate's "
                             "Conjecture'. Both fires 010 + 011 show FM-08 famous-name conflation as recurrent: "
                             "model uses one famous-conjecture-name when another is canonically associated."),
                "remediation_hint": ("Catalogue FM-08 famous-name-conflation as distinct sub-pattern. v1.0 corpus "
                                     "should include explicit cross-conjecture disambiguation triples (BSD-vs-ABC, "
                                     "Tate-vs-Modularity, Hodge-vs-Tate). RAG bibliography lookup would also catch."),
                "sub_type": "fabrication",
                "decomposition_mode": "OFF",
                "fab_type": "FM-08 famous-name-conflation",
                "fire_id": "011",
                "evaluator_note": "Evaluator marked USEFUL on top-line independence claim. Sub-fab info ticket only.",
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
        print(f"  {t['id']}: {t['title'][:80]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
