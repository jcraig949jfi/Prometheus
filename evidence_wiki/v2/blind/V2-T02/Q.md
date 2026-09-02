# PROPOSAL V2-T02 (arm)

## Hypothesis

A record sanitizer configured with a maintained list of known-bad patterns can reject all defective records before corpus admission while maintaining ≥99% acceptance rate on clean records, measured across a stratified test corpus sampled from committed ledgers.

## Motivating evidence

Ergon Gen-1 validation (input_fingerprint.py, validate_persistence.py, FINDING_d5_reproducibility_2026-09-01) identified systematic defects in persisted records: oracle-field leakage, schema violations, line-ending artifacts, post-hoc exemptions that bypass scanning, and records computed over mutated source code. Unscreened corpus admission amplifies these defects through training; sanitizer filtering gates admission before metabolization. Known-bad patterns extracted from committed verdicts (validate_persistence checks A-E) form the reference baseline.

## Prospective predictions

1. Sanitizer rejects ≥95% of seeded-defect test records (oracle leakage, schema bloat, fingerprint mismatches)
2. Sanitizer accepts ≥99.5% of records from clean committed lineages (library_lineage_*.json, m1_rows.jsonl exact replays)
3. Pattern false-positive rate ≤0.5% on held-out clean shard (test/clean_100k_sample)
4. Pattern false-negative rate ≤1.0% on held-out defect shard (test/seeded_defects_1k)
5. No pattern triggers on both clean and defective records simultaneously (exclusivity constraint)

## Experiment

**Phase 1: Calibration and baseline**
- Extract known-bad patterns from:
  - Oracle field names (forbidden substrings from anti_cheat/static_checks.py)
  - Schema constraint violations (EVENT_FIELDS, ADMISSION_FIELDS, TOP_FIELDS, FINAL_FIELDS from validate_persistence.py)
  - Fingerprint mismatches (input_fingerprint.py PINNED_SOURCES sha mismatch sentinel)
  - Line-ending artifacts (LF vs CRLF encoding flags on bytes-level hash)
  - Exemption markers (hardcoded allowlist tokens, e.g., 'HARNESS_EXEMPT')
- Commit pattern list to patterns/known_bad_v1.jsonl with {pattern, category, severity, reason_ref}
- Encode patterns as (regex, field scope, record scope) tuples

**Phase 2: Test corpus construction**
- **Clean baseline:** 100k records randomly sampled without replacement from {library_lineage_1.json, library_lineage_2.json, library_lineage_3.json, m1_rows.jsonl exact_replay}; stratify by {lineage, position_in_library} bins
- **Seeded defects:** 1k synthetic records mutating clean baseline:
  - 250 inject oracle fields (e.g., 'oracle_score', '_authoritative_solves' in wrong field group)
  - 250 violate schema (missing declared fields, add undeclared fields, duplicate keys)
  - 250 corrupt fingerprint (mutate sha in input_fingerprint field, flag mismatch status)
  - 250 inject CRLF markers (record bytes include `'\r\n'` sentinel in field value)
- Hold out 20% of clean, 20% of seeded defects for validation; remaining 80% used for calibration

**Phase 3: Sanitizer run and measurement**
- Apply sanitizer to: calibration_clean (80k) + calibration_defect (800)
- For each record: capture (passes, pattern_id, field_scope, severity)
- Measure: accept_rate_clean, accept_rate_defect, per-pattern_specificity, coverage (% defects matched by ≥1 pattern)

**Phase 4: Held-out validation**
- Apply sanitizer to: validation_clean (20k) + validation_defect (200)
- Report false-accept (clean records rejected), false-reject (defects accepted)
- Compute per-category false rates: {oracle, schema, fingerprint, encoding, exemption}

## Controls

Records that MUST NOT be rejected by sanitizer (negative controls):
- Clean records with legitimate field names containing substrings of forbidden oracle tokens (e.g., field 'authoritative_method' should pass even though 'authoritative' matches oracle pattern; pattern must anchor to word boundaries)
- Clean records with all declared fields populated and no extra fields
- Clean records with lineage ancestry chain intact and fingerprinted inputs matching pinned sources
- Records with LF-only line endings (already normalized, not artifacts)
- Records from lineages with explicit exemption audit trail (e.g., D-5 Phase 1 with documented A1–A5 findings)

## Confound defenses

1. **Pattern leakage:** Run patterns on both clean and defect cohorts in parallel (independent streams); any pattern matching >0.1% of clean cohort is re-examined for false anchoring
2. **Stratification bias:** Sample by lineage, not sequentially; verify cohort composition (count by lineage, position_in_library) matches source distribution before filtering
3. **Fingerprint mutation reversibility:** Seeded defects corrupt fingerprints deterministically (e.g., flip 1 bit); verify that un-corrupted input matches pinned sources exactly, confirming mutation was the only change
4. **Pattern overfitting:** Patterns extracted from committed Gen-1 records only; do not optimize patterns against seeded defects (patterns → seeded defects is a burn test, not a tuning loop)
5. **Exemption scope creep:** Track all exemption tokens and their justifications in a separate audit log; rejects are forbidden to add new exemptions (read-only constraint, feedback_techne_may_patch_other_roles)

## Preregistered falsifiers (numeric thresholds)

Record sanitizer is REJECTED if any of the following hold on validation cohort (held-out 20%):

1. **False accept rate (clean records rejected) > 0.5%:** sanitizer too strict; 1 in 200 clean records wrongly filtered
2. **False reject rate (defects accepted) > 1.0%:** sanitizer too weak; 1 in 100 defects pass undetected
3. **Exclusivity failure:** any single pattern matches ≥0.1% of clean AND ≥0.1% of defect cohort simultaneously (pattern underdetermined)
4. **Oracle pattern blind spot:** ≥5 oracle-field defects (seeded_defects category='oracle') accepted without match
5. **Schema coverage < 90%:** fewer than 90% of schema-violating defects matched by schema patterns
6. **Any per-category false-reject > 2%:** category-specific failure (e.g., fingerprint patterns miss >2% of fingerprint defects)
7. **Fingerprint false positives > 0.1%:** >0.1% of clean records flagged as fingerprint mismatches (indicates pattern drift from pinned sources)

Falsifier 1–7 are independent; **any single breach triggers REJECTION**. No thresholds are negotiable (feedback_gate_must_exceed_measurement_error).

## Stopping rule

- **Early stop if calibration false-reject > 2% on first 10k records:** indicates patterns are fundamentally misspecified; do not proceed to validation cohort
- **Early stop if Exclusivity fails during calibration:** indicates pattern overlap; pause and re-partition before validation
- **Complete validation phase regardless of interim results:** partial data from truncated validation is inadmissible; full validation cohort must be processed before any verdict
- **Verdict: PASS requires ALL seven falsifiers to hold on validation cohort (unanimity gate)**

## Expected failure modes

1. **Line-ending false positives:** CRLF patterns match on some systems (autocrlf=true) and should not; defense: normalize all records to LF before storing, flag only records with embedded CRLF in field values (not line terminators)
2. **Oracle field false negatives:** patterns use exact token match (e.g., 'oracle_score'); defects may use synonyms ('oracle_val', '_oracle'). Defense: burn test against seeded defects with token variants; update patterns if coverage < 90%
3. **Fingerprint pattern drift:** pinned sources change or are regenerated; old fingerprints become defective. Defense: patterns must reference commit sha of frozen sources (input_fingerprint.py model); invalidate patterns older than source age before running sanitizer
4. **Exemption scope ambiguity:** legacy records cite exemptions no longer justified; sanitizer cannot distinguish. Defense: exemptions require explicit audit trail entry with (exemption_reason, reference_commit, expiry_date); accept only records ≤expiry_date
5. **Seeded defect artificiality:** synthetic mutations do not reflect real defects; sanitizer optimizes for fakes. Defense: patterns extracted from committed records only; seeded defects are a burn test, not a tuning target; run secondary validation on real-world defects from prior campaigns if available

## Compute estimate

- Calibration phase: 1–2 CPU-hours (100k + 800 records, pattern matching + field scoping)
- Held-out validation phase: 0.5–1 CPU-hour (20k + 200 records)
- Pattern extraction and audit log assembly: 2–4 CPU-hours (manual review of Gen-1 verdicts, exemption justification)
- **Total estimate: 4–7 CPU-hours, negligible disk/memory (<1GB)**
- **Wall-clock time: <1 day on single worker**

## Prior evidence that materially changed this design (or 'none found')

**Prior evidence that shaped this design:**

- **Ergon Gen-1 validation architecture** (validate_persistence.py): the 5-check battery (SAME-SEED PARITY, ROUND-TRIP, NO ORACLE LEAKAGE, SCHEMA MINIMALITY, EXTERNAL FIDELITY) provided the schema constraint and oracle-field defect taxonomy; this proposal reuses those check categories as pattern categories
- **Input fingerprinting protocol** (input_fingerprint.py, FINDING_d5_reproducibility_2026-09-01): line-ending normalization trap identified (17 of 31 false hash violations on Windows autocrlf=true); this proposal explicitly adds LF/CRLF as a defect pattern and normalizes during corpus ingestion
- **Anti-cheat exemption audit** (FINDING_d5_reproducibility_2026-09-01 section 3): the defect class of "a check that removes a region before inspecting it" motivated the read-only exemption constraint; exemptions now require explicit audit trail (feedback_techne_may_patch_other_roles)
- **Certification module** (certified.py): the trichotomy {yes, no, indeterminate} for verdicts; this proposal applies the same gate structure (PASS requires ALL seven falsifiers)

## Unresolved uncertainty

1. **Real-world defect inventory:** unknown how many defect types exist in committed Gen-1 ledgers beyond the five check categories; seeded defects may miss emergent patterns (mitigation: secondary audit of actual rejects post-deployment, with loop back to pattern refresh)
2. **Pattern false-positive calibration:** the threshold 0.5% for clean-record false accept is conservative but arbitrary; no empirical baseline from prior filtering campaigns exists to justify it (mitigation: run on historical clean corpus first, report baseline before setting gate)
3. **Exemption scope boundary:** legacy records with undocumented exemptions will fail audit trail check; risk of over-rejection on back-end corpus if exemptions were widespread (mitigation: audit a sample of N=100 Gen-1 records pre-deployment to estimate exemption prevalence)
4. **Pattern language expressiveness:** regex + field scope may be insufficient for complex defects (e.g., cross-field inconsistencies, graph-structural violations); current design is pattern-bound, not rule-bound (mitigation: if burn test coverage < 90%, escalate to rule-based system post-validation)
5. **Fingerprint source drift:** PINNED_SOURCES may be edited post-commitment; no automated alarm if sources change (mitigation: include source sha in every record fingerprint field; sanitizer verifies it matches frozen sources at ingestion time)

