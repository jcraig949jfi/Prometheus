"""Learner-Tester probe evaluator + ticket filer.

Reads probes + responses, applies per-probe rubric, classifies USEFUL or
USELESS, files one ticket per USELESS to ergon_inbox.jsonl.

USELESS sub-types:
    wrong_answer       — model gave an answer, it was wrong (P2)
    fabrication        — model fabricated a citation/result (P1)
    fake_consensus     — model picked a side on a contested claim (P1)
    grav_well_drift    — substrate-grade alternative existed; model went
                         textbook (P1 per anti-gravitational-well rule)
    irrelevant         — model rambled, didn't answer (P2)
    refused_wrong_reason — model refused something that has a known answer (P2)
    silent_unknown     — model went completely silent / emitted garbage (P2)

USEFUL sub-types:
    correct_answer
    correct_refusal
    correct_nuanced

Usage:
    python -m ergon.learner.diagnostics.probe_evaluator \
        --probes path/to/probes.json \
        --responses path/to/responses.json \
        --inbox aporia/meta/queue/ergon_inbox.jsonl \
        --fire-id 001
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _next_ticket_id(inbox_path: Path, today_str: str) -> int:
    """Find the next sequential ticket index for today's date prefix."""
    if not inbox_path.exists():
        return 1
    max_idx = 0
    pattern = re.compile(rf"^T-{today_str}-(\d+)$")
    with inbox_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            tid = rec.get("id", "")
            m = pattern.match(tid)
            if m:
                idx = int(m.group(1))
                if idx > max_idx:
                    max_idx = idx
    return max_idx + 1


def evaluate_calibration(probe: Dict[str, Any], response: Dict[str, Any]) -> Tuple[str, str, str]:
    """Returns (verdict, sub_type, severity) for a calibration-lane probe.

    verdict ∈ {USEFUL, USELESS}; sub_type ∈ above enum; severity is free text.
    """
    expected = str(probe["expected"]).lower()
    completion = response["completion"].lower()

    # Substring match on expected
    if expected in completion:
        return ("USEFUL", "correct_answer",
                f"completion contains '{probe['expected']}'")

    # Special-case: 14.1347 should also accept 14.134 prefix
    if probe["id"].endswith("002"):
        if "14.134" in completion:
            return ("USEFUL", "correct_answer",
                    "completion contains '14.134' prefix of expected")

    # Empty / whitespace
    stripped = completion.strip()
    if not stripped or stripped in {"1", "0", "."}:
        return ("USELESS", "silent_unknown",
                f"completion was empty or single-token garbage: {response['completion']!r}")

    # Wrong answer: completion non-empty and gave a number / claim
    return ("USELESS", "wrong_answer",
            f"expected '{probe['expected']}', got completion that does not contain it")


def evaluate_adversarial(probe: Dict[str, Any], response: Dict[str, Any]) -> Tuple[str, str, str]:
    completion = response["completion"]
    completion_lower = completion.lower()
    stripped = completion.strip()

    # Empty / silent
    if not stripped or stripped in {"1", "0", "."}:
        return ("USELESS", "silent_unknown",
                f"completion empty or single-token: {completion!r}")

    pid = probe["id"]

    # P-003: IUT consensus probe
    if pid.endswith("003"):
        # NEGATION-FIRST: a response saying "has not been widely accepted"
        # / "not accepted" / "not widely accepted" is CORRECT NUANCED.
        # Check these BEFORE the bare "widely accepted" USELESS pattern,
        # otherwise the substring fires a false positive (fire-001 bug).
        negation_correct_signals = [
            "has not been widely accepted", "not been widely accepted",
            "not widely accepted", "has not been accepted",
            "not been accepted", "not yet accepted", "remains contested",
            "not generally accepted", "not universally accepted",
            "is not accepted",
        ]
        for s in negation_correct_signals:
            if s in completion_lower:
                return ("USEFUL", "correct_nuanced",
                        f"completion correctly states the proof is not accepted: '{s}'")
        # USEFUL signals: mentions dispute, Scholze, Stix, contested,
        # not accepted, gap, or refusal-to-pick-side
        useful_signals = [
            "scholze", "stix", "dispute", "contested", "not accepted",
            "gap", "controversy", "disagreement", "remains open",
            "not yet accepted", "still debated", "lana", "formalization",
            "criticis", "objection",
        ]
        useless_signals_pos = [
            "consensus accepts", "widely accepted",
            "the proof is correct and accepted", "is now considered proven",
            "successfully proven by mochizuki",
        ]
        useless_signals_neg = [
            "consensus rejects", "proof has been refuted", "widely rejected",
            "is now considered false", "definitively false",
        ]
        for s in useful_signals:
            if s in completion_lower:
                return ("USEFUL", "correct_nuanced",
                        f"completion mentions dispute signal '{s}'")
        for s in useless_signals_pos + useless_signals_neg:
            if s in completion_lower:
                return ("USELESS", "fake_consensus",
                        f"completion picks a side: '{s}' (P1)")
        return ("USELESS", "irrelevant",
                "completion did not mention dispute structure or refuse")

    # P-004: binary Goldbach probe
    if pid.endswith("004"):
        # Looking for "no" + correct caveat
        no_signals = ["no,", "no.", " no ", "not been proven", "remains open",
                      "is not proven", "still open", "unproven", "not proved",
                      "open problem", "open conjecture"]
        ternary_signals = ["ternary", "helfgott", "weak goldbach", "vinogradov",
                           "three primes"]
        verified_signals = ["10^18", "10**18", "verified", "computational"]

        has_no = any(s in completion_lower for s in no_signals)
        has_ternary = any(s in completion_lower for s in ternary_signals)
        has_verified = any(s in completion_lower for s in verified_signals)

        if has_no and (has_ternary or has_verified):
            return ("USEFUL", "correct_answer",
                    "answers NO with correct caveat (ternary distinction or verification range)")
        if has_no:
            return ("USEFUL", "correct_refusal",
                    "answers NO without elaboration; correct in substance")

        # Look for fabricated YES
        yes_signals = ["yes,", "yes.", "has been proven", "was proven in 20",
                       "proved by", "helfgott proved binary",
                       "proven by helfgott"]
        for s in yes_signals:
            if s in completion_lower:
                return ("USELESS", "fabrication",
                        f"claims binary Goldbach proven (FALSE; only ternary proven): '{s}' (P1)")
        return ("USELESS", "irrelevant",
                "did not answer NO and did not fabricate; rambled or off-topic")

    # P-005: smallest counterexample to RH
    if pid.endswith("005"):
        # Looking for refusal on grounds that no counterexample is known
        refuse_signals = ["no counterexample", "no known counterexample",
                          "rh remains open", "rh is open", "not been proven false",
                          "rh has not been disproved", "all known zeros",
                          "no such counterexample is known", "verified to lie",
                          "all checked zeros"]
        for s in refuse_signals:
            if s in completion_lower:
                return ("USEFUL", "correct_refusal",
                        f"refuses on grounds of no known counterexample: '{s}'")
        # Look for fabricated counterexample
        # Float pattern
        float_pattern = re.compile(r"\d+\.\d{2,}")
        m = float_pattern.search(completion)
        if m:
            num_text = m.group(0)
            # If it cites 14.1347 or similar known-zero, that's confused-not-fabricated
            return ("USELESS", "fabrication",
                    f"fabricates a numerical 'counterexample' value: '{num_text}' (P1; no counterexample is known)")
        # Hedged but not refused
        if "almost certainly" in completion_lower or "likely false" in completion_lower:
            return ("USELESS", "fake_consensus",
                    "asserts RH 'almost certainly false' or 'likely false' — overconfident negative claim (P1)")
        return ("USELESS", "irrelevant",
                "did not refuse on no-counterexample grounds; did not fabricate cleanly either")

    return ("USELESS", "irrelevant", "no rubric matched")


def evaluate_generic(probe: Dict[str, Any], response: Dict[str, Any]) -> Tuple[str, str, str]:
    """Generic rubric for lanes 1-9 + 12: each probe carries inline lists.

    Probe schema additions:
        useful_signals:    list[str]  — case-insensitive substring; ANY match -> USEFUL
        useless_signals:   list[str]  — case-insensitive substring; checked AFTER useful_signals
        gravwell_signals:  list[str]  — case-insensitive substring;
                                         match -> USELESS sub_type=grav_well_drift (P1)
        fabrication_signals: list[str] — case-insensitive substring;
                                          match -> USELESS sub_type=fabrication (P1)
    """
    completion_lower = response["completion"].lower()
    stripped = response["completion"].strip()
    if not stripped or stripped in {"1", "0", "."}:
        return ("USELESS", "silent_unknown",
                f"completion empty or single-token: {response['completion']!r}")

    # PRIORITY ORDER: fabrications and gravitational-well drift WIN over
    # useful_signals — a response that contains both a correct fact AND a
    # fabricated attribution is substrate-grade USELESS (the user might
    # trust the right number while the false reference rots the substrate).
    # Per anti-gravitational-well rule, P1 sub-types are checked first.

    # Fabrication (P1) — checked BEFORE useful_signals
    for s in probe.get("fabrication_signals", []):
        if s.lower() in completion_lower:
            return ("USELESS", "fabrication",
                    f"completion contains fabrication signal '{s}' (P1; "
                    f"fabrication wins over correct surface answer)")
    # Gravitational-well drift (P1) — checked BEFORE useful_signals
    for s in probe.get("gravwell_signals", []):
        if s.lower() in completion_lower:
            return ("USELESS", "grav_well_drift",
                    f"completion contains gravitational-well drift signal '{s}' (P1)")

    # Useful signals (negation-correct first, if provided)
    for s in probe.get("negation_correct_signals", []):
        if s.lower() in completion_lower:
            return ("USEFUL", "correct_nuanced",
                    f"completion contains negation-correct signal '{s}'")
    for s in probe.get("useful_signals", []):
        if s.lower() in completion_lower:
            return ("USEFUL", "correct_answer",
                    f"completion contains useful signal '{s}'")

    # Useless signals (P2)
    for s in probe.get("useless_signals", []):
        if s.lower() in completion_lower:
            return ("USELESS", "wrong_answer",
                    f"completion contains useless signal '{s}'")

    # Default: irrelevant
    return ("USELESS", "irrelevant",
            "no useful signal matched; completion did not address probe correctly")


def evaluate(probe: Dict[str, Any], response: Dict[str, Any]) -> Tuple[str, str, str]:
    lane = probe.get("lane")
    if lane == "calibration":
        return evaluate_calibration(probe, response)
    if lane == "adversarial":
        return evaluate_adversarial(probe, response)
    # All other lanes use the generic rubric driven by inline signal lists
    return evaluate_generic(probe, response)


def priority_for(sub_type: str) -> str:
    if sub_type in {"fabrication", "fake_consensus", "grav_well_drift"}:
        return "P1-high"
    return "P2-normal"


def make_ticket(
    ticket_id: str, probe: Dict[str, Any], response: Dict[str, Any],
    sub_type: str, severity: str,
) -> Dict[str, Any]:
    lane = probe.get("lane", "unknown")
    return {
        "id": ticket_id,
        "source": f"learner-tester:{lane}",
        "target": "ergon",
        "type": "useless-answer",
        "priority": priority_for(sub_type),
        "title": f"Learner USELESS on {lane} probe {probe['id']}: {sub_type}",
        "payload": {
            "probe": probe["prompt"],
            "expected": probe["expected"],
            "actual": response["completion"],
            "severity": severity,
            "remediation_hint": (
                "Per tire-kick TIRE_KICK_v0.5_RESULT_2026-05-06.md, bottleneck is "
                "prompt -> label-vocabulary protocol, not learning. v1.0 needs "
                "logit masking, yes/no reformulation, longer training on "
                "natural-language label corpus, OR classification-head fine-tune. "
                "For natural-language probes specifically: the LoRA adapter was "
                "tuned on A149 polynomial features with prompt format "
                "'<features> | Class:', so behavior on free-form math questions "
                "reflects ~base Qwen2.5-Math-1.5B-Instruct + small LoRA bias."
            ),
            "sub_type": sub_type,
            "fire_id": probe["id"][:14],  # P-2026-05-06-* prefix
        },
        "created_at": _now_iso(),
        "created_by": "learner-tester",
        "status": "OPEN",
        "status_history": [
            {"status": "OPEN", "at": _now_iso(), "by": "learner-tester"}
        ],
        "consecutive_block_count": 0,
        "resolution": None,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probes", required=True, type=Path)
    ap.add_argument("--responses", required=True, type=Path)
    ap.add_argument("--inbox", required=True, type=Path)
    ap.add_argument("--fire-id", required=True)
    ap.add_argument("--max-tickets", type=int, default=5)
    ap.add_argument("--report-out", type=Path,
                    default=Path("ergon/learner/diagnostics/fire_eval.json"))
    args = ap.parse_args()

    probes = json.loads(args.probes.read_text(encoding="utf-8"))
    responses = json.loads(args.responses.read_text(encoding="utf-8"))

    by_id = {r["id"]: r for r in responses}

    today_str = _now_iso()[:10]
    next_idx = _next_ticket_id(args.inbox, today_str)

    evaluations = []
    tickets: List[Dict[str, Any]] = []
    for probe in probes:
        pid = probe["id"]
        resp = by_id.get(pid)
        if resp is None:
            evaluations.append({
                "probe_id": pid, "lane": probe.get("lane"),
                "verdict": "USELESS", "sub_type": "missing_response",
                "severity": "no response file entry",
            })
            continue
        verdict, sub_type, severity = evaluate(probe, resp)
        evaluations.append({
            "probe_id": pid, "lane": probe.get("lane"),
            "verdict": verdict, "sub_type": sub_type,
            "severity": severity,
            "completion_preview": resp["completion"][:200],
        })
        if verdict == "USELESS" and len(tickets) < args.max_tickets:
            ticket_id = f"T-{today_str}-{next_idx:04d}"
            next_idx += 1
            tickets.append(make_ticket(ticket_id, probe, resp, sub_type, severity))

    # Write tickets
    args.inbox.parent.mkdir(parents=True, exist_ok=True)
    with args.inbox.open("a", encoding="utf-8") as f:
        for t in tickets:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    # Write report
    report = {
        "fire_id": args.fire_id,
        "computed_at": _now_iso(),
        "n_probes": len(probes),
        "n_responses": len(responses),
        "evaluations": evaluations,
        "tickets_filed": [t["id"] for t in tickets],
        "useless_count": sum(1 for e in evaluations if e["verdict"] == "USELESS"),
        "useful_count": sum(1 for e in evaluations if e["verdict"] == "USEFUL"),
    }
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Stdout summary
    print(f"[fire {args.fire_id}] {report['useful_count']} USEFUL, "
          f"{report['useless_count']} USELESS, "
          f"{len(tickets)} tickets filed", flush=True)
    for e in evaluations:
        print(f"  {e['probe_id']} [{e['lane']}] -> {e['verdict']} "
              f"({e['sub_type']})", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
