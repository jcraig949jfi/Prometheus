"""Iter 4 / Task #66: Investigate the surprise predicate from Trial 3.

Trial 3 smoke surfaced predicate `{neg_z: 3, pos_x: 4, neg_y: 1}` with
lift=12.42, NOT in OBSTRUCTION_SIGNATURE or SECONDARY_SIGNATURE. Two
hypotheses:
  H1 — Real second-order signal in OBSTRUCTION_CORPUS that Charon's
       planted signatures missed.
  H2 — Synthetic-generation artifact (small match-group overlapping a
       planted signature by coincidence; lift inflates via small N).

This script tests both:
  - Compute corpus summary (planted-signature counts, baseline rates)
  - Evaluate the surprise predicate; show the matched records
  - Check if any matched records are ALSO OBSTRUCTION/SECONDARY matches
  - Compute lift on the "non-overlap" subset (subtract planted matches
    from the match group; recompute lift)

Output: TRIAL_3_INVESTIGATION_REPORT.md with verdict.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

from prometheus_math._obstruction_corpus import (
    OBSTRUCTION_CORPUS,
    OBSTRUCTION_SIGNATURE,
    SECONDARY_SIGNATURE,
    corpus_summary,
)
from prometheus_math.obstruction_env import evaluate_predicate


SURPRISE = {"neg_z": 3, "pos_x": 4, "neg_y": 1}


def predicate_matches(features: Dict[str, Any], pred: Dict[str, Any]) -> bool:
    return all(features.get(k) == v for k, v in pred.items())


def investigate() -> Dict[str, Any]:
    summary = corpus_summary()

    # Evaluate the surprise predicate
    surp_eval = evaluate_predicate(SURPRISE, OBSTRUCTION_CORPUS)

    # Find all records matching the surprise predicate; show their features
    matched = []
    for entry in OBSTRUCTION_CORPUS:
        feats = entry.features()
        if predicate_matches(feats, SURPRISE):
            also_obstruction = predicate_matches(feats, OBSTRUCTION_SIGNATURE)
            also_secondary = predicate_matches(feats, SECONDARY_SIGNATURE)
            matched.append({
                "features": feats,
                "kill_verdict": entry.kill_verdict,
                "also_matches_obstruction": also_obstruction,
                "also_matches_secondary": also_secondary,
            })

    # Compute lift on the "non-overlap" subset: remove records that match
    # any planted signature, then recompute lift
    non_overlap_matched = [m for m in matched
                            if not m["also_matches_obstruction"]
                            and not m["also_matches_secondary"]]
    non_overlap_kills = sum(1 for m in non_overlap_matched if m["kill_verdict"])
    non_overlap_size = len(non_overlap_matched)

    # Baseline = non-match group; count its kills
    baseline_size = 0
    baseline_kills = 0
    for entry in OBSTRUCTION_CORPUS:
        feats = entry.features()
        if not predicate_matches(feats, SURPRISE):
            baseline_size += 1
            if entry.kill_verdict:
                baseline_kills += 1

    if non_overlap_size > 0 and baseline_size > 0:
        non_overlap_kill_rate = non_overlap_kills / non_overlap_size
        baseline_kill_rate = baseline_kills / baseline_size
        non_overlap_lift = (
            non_overlap_kill_rate / baseline_kill_rate
            if baseline_kill_rate > 0 else float("inf")
        )
    else:
        non_overlap_kill_rate = 0.0
        baseline_kill_rate = 0.0
        non_overlap_lift = 0.0

    # Verdict
    if surp_eval["match_group_size"] >= 5 and surp_eval["lift"] >= 5.0:
        verdict = "LIKELY_REAL_SIGNAL"
    elif surp_eval["match_group_size"] <= 2 and any(
        m["also_matches_obstruction"] or m["also_matches_secondary"]
        for m in matched
    ):
        verdict = "LIKELY_ARTIFACT_PLANTED_OVERLAP"
    elif non_overlap_size > 0 and non_overlap_lift >= 3.0:
        verdict = "PARTIAL_SIGNAL_BEYOND_PLANTED"
    elif non_overlap_size == 0 and any(
        m["also_matches_obstruction"] or m["also_matches_secondary"]
        for m in matched
    ):
        verdict = "PURE_PLANTED_OVERLAP"
    else:
        verdict = "AMBIGUOUS_LOW_POWER"

    return {
        "predicate": SURPRISE,
        "corpus_summary": summary,
        "surprise_eval": surp_eval,
        "matched_records": matched,
        "non_overlap_analysis": {
            "non_overlap_match_size": non_overlap_size,
            "non_overlap_kills": non_overlap_kills,
            "non_overlap_kill_rate": non_overlap_kill_rate,
            "baseline_kill_rate": baseline_kill_rate,
            "non_overlap_lift": non_overlap_lift,
        },
        "verdict": verdict,
    }


def format_report(results: Dict[str, Any]) -> str:
    surp = results["surprise_eval"]
    summary = results["corpus_summary"]
    non_ov = results["non_overlap_analysis"]
    matched = results["matched_records"]

    lines = [
        "# Trial 3 Surprise-Predicate Investigation",
        "",
        f"**Predicate:** `{results['predicate']}`",
        f"**Verdict:** **{results['verdict']}**",
        "",
        "## Corpus structure",
        f"- Total entries: {summary['n_total']}",
        f"- Total kills: {summary['n_kills']} (baseline rate {summary['baseline_kill_rate']:.4f})",
        f"- OBSTRUCTION_SIGNATURE matches: {summary['obstruction_matches']} (all killed: {summary['obstruction_killed']})",
        f"- SECONDARY_SIGNATURE matches: {summary['secondary_matches']} (all killed: {summary['secondary_killed']})",
        f"- Other (noise) kills: {summary['noise_kills']}",
        "",
        "## Surprise-predicate full lift evaluation",
        f"- Match-group size:    {surp['match_group_size']}",
        f"- Matched kill rate:   {surp['matched_kill_rate']:.4f}",
        f"- Baseline kill rate:  {surp['baseline_kill_rate']:.4f}",
        f"- Lift:                {surp['lift']:.4f}",
        "",
        "## Matched records",
    ]
    if matched:
        for i, m in enumerate(matched):
            flags = []
            if m["also_matches_obstruction"]:
                flags.append("ALSO_OBSTRUCTION")
            if m["also_matches_secondary"]:
                flags.append("ALSO_SECONDARY")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            lines.append(
                f"- Record {i}: kill={m['kill_verdict']}{flag_str}"
            )
            lines.append(f"  features: {m['features']}")
    else:
        lines.append("(no records matched the surprise predicate)")

    lines += [
        "",
        "## Non-overlap analysis",
        "(removing records that ALSO match planted signatures, recompute lift)",
        f"- Non-overlap match-group size: {non_ov['non_overlap_match_size']}",
        f"- Non-overlap kills:            {non_ov['non_overlap_kills']}",
        f"- Non-overlap kill rate:        {non_ov['non_overlap_kill_rate']:.4f}",
        f"- Baseline kill rate:           {non_ov['baseline_kill_rate']:.4f}",
        f"- Non-overlap lift:             {non_ov['non_overlap_lift']:.4f}",
        "",
        "## Verdict interpretation",
    ]

    verdict_text = {
        "LIKELY_REAL_SIGNAL": (
            "The predicate has a sufficiently large match-group and high lift that "
            "rules out the small-N coincidence explanation. This may be genuine "
            "signal in the corpus that Charon's planted signatures didn't cover. "
            "**Stoa note to Charon: substrate-grade discovery candidate.**"
        ),
        "LIKELY_ARTIFACT_PLANTED_OVERLAP": (
            "The predicate has a small match-group overlapping a planted "
            "signature. The high lift comes from the planted matches being "
            "kills by construction, NOT from independent signal. **Substrate-grade "
            "interpretation: this is the engine partially-rediscovering the "
            "planted signal via a coarser conjunctive predicate. Useful for "
            "validating selection pressure works; not a separate discovery.**"
        ),
        "PURE_PLANTED_OVERLAP": (
            "All matched records also match a planted signature. The lift is "
            "entirely due to planted-signal contamination. The engine "
            "rediscovered (a strict subset of) the planted signal under a "
            "weaker predicate. **Confirms selection pressure but no separate "
            "discovery.**"
        ),
        "PARTIAL_SIGNAL_BEYOND_PLANTED": (
            "After removing records that overlap planted signatures, the "
            "predicate still has lift >= 3.0 on the residual. This indicates "
            "real second-order signal in the corpus beyond what was planted. "
            "**Stoa note to Charon: the synthetic corpus has unintended "
            "structure; the engine surfaced it.**"
        ),
        "AMBIGUOUS_LOW_POWER": (
            "Match-group too small to disambiguate signal from artifact. "
            "Rerun with larger search budget or relaxed predicate complexity."
        ),
    }
    lines.append(verdict_text.get(results["verdict"], "(unknown verdict)"))

    return "\n".join(lines)


if __name__ == "__main__":
    results = investigate()
    out_dir = Path(__file__).parent
    (out_dir / "trial_3_investigation_results.json").write_text(
        json.dumps(results, indent=2, default=str), encoding="utf-8"
    )
    report = format_report(results)
    (out_dir / "TRIAL_3_INVESTIGATION_REPORT.md").write_text(report, encoding="utf-8")
    print(report)
