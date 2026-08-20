# KillVector -> Trace-Vector v2 crosswalk (SALVAGE-STYGIAN, P45)

Date: 2026-08-20 | Sources verified this pass: charon/agents/stygian/daemon.py (KillVector
stub, 8 fields) and aporia/doctrine/reasoning_ladder.md section 5 (trace vector, 17 fields,
canon: "the residue standard"). Consumer: any future Stygian revival emits trace-vector-
conformant records through this mapping; the v2.1 candidate fields go to the canon owner
for deliberate adjudication (canon is NOT edited by this document).

## Field mapping (verdict per field: DIRECT / MAPS-WITH-NOTE / STYGIAN-SPECIFIC / V2-GAP)

- problem_id -> problem_id. DIRECT.
- kill_pattern -> kill_pattern. DIRECT.
- falsifier_id -> tier_probe. MAPS-WITH-NOTE: KillVector names the specific battery test
  that fired; tier_probe names the probe/rung. The battery-test identity survives if
  tier_probe carries "v10-battery/<falsifier_id>" — a convention, not a schema change.
- hardness_signature -> (none). STYGIAN-SPECIFIC: hardness is a PROBLEM property, not an
  attempt property; it belongs in the problem catalog row (BL-C entries), joined by
  problem_id at analysis time. Putting it in the trace vector would denormalize.
- calibration_tier -> confidence_calibration. MAPS-WITH-LOSS, noted: KillVector's field
  states which anchor CLASS is required (KC-001-class); the trace field records the
  attempt's calibration BEHAVIOR. Both are needed; the requirement side joins from the
  battery spec by falsifier_id. No forced merge.
- competing_hypothesis_id -> (none). V2-GAP #1: the trace vector has NO slot linking an
  attempt to its PRE-REGISTERED competing hypothesis. Pre-registration linkage is standing
  doctrine (register-before-run); a residue record that cannot name the alternative it was
  racing loses exactly the exchangeability evidence the thesis wants. v2.1 CANDIDATE:
  `competing_hypothesis_id` (nullable).
- precision_floor -> (none). V2-GAP #2: verification depth is a first-class truth axis
  (resolution-dependent-truth doctrine: status/precision/method/stability), and the trace
  vector carries none of it. v2.1 CANDIDATE: `verification_precision` (the resolution at
  which answer_correct was adjudicated).
- repair_attempt_id -> repair_available. MAPS-WITH-REFINEMENT: v2's field is effectively a
  flag; Stygian's is an ID linking the concrete REWRITE artifact. An ID subsumes a flag.
  v2.1 CANDIDATE: widen repair_available to accept an artifact id (null / true / "<id>").

## Reading: ALIGNABLE (as pre-stated), with 2 genuine v2 gaps and 1 refinement
No field is incommensurable. Two KillVector fields protect doctrine (pre-registration
linkage, verification depth) that trace-vector v2 currently drops — the crosswalk's real
yield. The three v2.1 candidates are RECOMMENDATIONS to the canon layer, deliberately not
applied to reasoning_ladder.md by this pass: canon edits are their own act, reviewed as
such.

## Prior-reachability note
The gap findings flatter Stygian's schema (and the salvage lane). Checkable content: the
17 v2 fields and 8 KillVector fields are quoted from their sources above; the reader can
verify no v2 field names a competing hypothesis or a verification resolution.

## Trace-vector record (this document's own)
problem_id: SALVAGE-STYGIAN | tier_probe: schema-crosswalk | answer_correct: n/a
domain_constraints_detected: [problem-vs-attempt-property-split, preregistration-linkage-absent-in-v2, verification-depth-absent-in-v2]
operations_used: [both-schema-existence-check, per-field-typed-mapping, gap-extraction, canon-boundary-respect]
kill_pattern: none | repair_available: v2.1 candidates filed above
residue: a crosswalk that finds only DIRECT mappings has probably been done backwards — the gaps are the product
