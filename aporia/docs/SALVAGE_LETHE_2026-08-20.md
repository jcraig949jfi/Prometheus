# SALVAGE-LETHE: registry merge-check — zero anchor debt, one instrument artifact
Date: 2026-08-20 (Aporia P41) | Source artifact: charon/agents/lethe/artifacts/ (573 files,
May 21 era, verified loadable) | Consumer: anti_anchors registry hygiene + Lethe detector
post-mortem

## Pre-stated readings
ALL-MERGED (zero unmerged candidate topics) / PARTIAL-DEBT (1-3, file with primary
verification) / LARGE-DEBT (4+, dedicated lane).

## Inventory (by query)
573 files: 43 anti_anchor_candidate_* across 6 topics; 82 self_audit_null; ~440
null_probe_* across 12 topics (the cold-LLM control corpus, already partially consumed as
evidence-layer markers by the LAD width study).

## Merge-check result: ALL-MERGED (with one artifact reclassified)
- bounded_gaps_vs_twin_primes -> AA-058 BOUNDED_GAPS_246_VS_TWIN_PRIMES_OPEN
- mertens_conjecture          -> AA-045 MERTENS_CONJECTURE_REFUTED_1985
- schinzel_zassenhaus         -> AA-032 SCHINZEL_ZASSENHAUS_RESOLVED
- sensitivity_conjecture      -> AA-046 SENSITIVITY_CONJECTURE_RESOLVED_HUANG
- ternary_goldbach            -> AA-057 TERNARY_VS_BINARY_GOLDBACH_BOUNDARY
- fermat_last_theorem_calibration -> NO anchor, and NONE IS OWED (below)

Zero unmerged anti-anchor debt. The Lethe->registry pipeline did not leak candidates.

## The FLT files are a detector false positive, not a candidate
The two FLT "candidate" emissions (emit_rate 50%, n=4) contain samples that CORRECTLY
state FLT is proved (Wiles 1994, Taylor-Wiles 1995). The firing pattern —
`(?i)fermat.*last\s*theorem.*\b(open|unproven|conjecture(?:d)?|unresolved)\b` — matched
HISTORICAL NARRATION inside correct answers: "originally conjectured by Pierre de Fermat
in 1637", "no proof by Fermat has ever been found". The detector is stance-blind: it
pattern-matches words, not the claim's stance toward them.

This is what a calibration topic is FOR: FLT (settled, famous, history full of the word
"conjectured") measured the detector's false-positive behavior — ~50% emit rate on
correct answers. The artifact records the measurement; it must never be merged as an
anchor.

## Residue (narrative-resistance catalog candidate)
STANCE-BLIND PATTERN FIRE: a keyword detector over text about a resolved question will
fire on the question's own history ("conjectured in 1637" != "is a conjecture"). Any
anti-anchor miner keyed on status words needs stance parsing or a narration-exclusion
window, and its calibration battery needs at least one settled-theorem-with-conjecture-
history topic to measure exactly this.

## Trace-vector record
problem_id: SALVAGE-LETHE | tier_probe: artifact merge-check | answer_correct: n/a
domain_constraints_detected: [stance-blind-regex, calibration-topic-as-fp-meter, filename-pattern-covers-7.5%-of-artifact-mass]
operations_used: [artifact-existence-check, topic-enumeration-by-query, per-topic-registry-pinning, sample-level-reclassification]
kill_pattern: none (zero debt) | repair_available: stance parsing for any future Lethe revival (filed, not built — Lethe is DEAD/shelved)
residue: the 440-file null-probe corpus is a reusable cold-LLM control population for future prior-measurement work
