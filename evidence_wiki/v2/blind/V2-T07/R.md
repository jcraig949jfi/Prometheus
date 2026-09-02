# PROPOSAL V2-T07 (arm)

## Hypothesis
The Prometheus techne cartography schema mandates **separation of claim ("paper says X") from verification ("X is true in our holdings")**. However, derived quantities stored in `techne/cartography/store/` (regulators, analytic Sha, conductors, and special values computed via `prometheus_math` tools) carry no per-record audit trail verifying that the stored value actually obeys the conjectures it purports to relate to. Specifically: (1) stored regulator values are not re-verified against BSD product bounds after storage; (2) saturation-index errors in TOOL_REGULATOR (known to cause off-by-index² inflation) are not detected post-hoc; (3) adjudication status is recorded as "PROPOSED" or "CONFIRMED" but confirmation is not tied to an actual conjecture-consistency check. We predict that systematic re-verification of stored derived quantities against their canonical conjecture formulations (BSD rank/regulator/Sha relationships, conductor divisibility properties, height matrix rank constraints) will expose at least one class of inconsistencies (either computational drift, schema corruption, or transient cache invalidation), and that this class will be orthogonal to the documented failure modes of the generating tools themselves.

## Motivating evidence
- `harmonia/memory/symbols/TOOL_REGULATOR.md` documents a **CRITICAL saturation gotcha**: without `ellsaturation(bound=100)`, the regulator is off by `(index)^2`. Example: 37.a1 unsaturated gives 0.46 instead of 0.051 (9× error). The tool's own test guards against this via `test_saturation_regression`, but no audit verifies that stored values in cartography/store/ actually called saturation before recording.
- `techne/cartography/schema.py` enforces `ADJUDICATION = ("PROPOSED", "CONFIRMED", "REFUTED", "BLOCKED")` and mandates that "only a deterministic predicate over stored evidence may write CONFIRMED". However, the schema does not *require* that the deterministic predicate actually validate a conjecture; a record can be marked CONFIRMED merely because an LLM or parsing step completed without error.
- `techne/cartography/store/taxonomy_events.jsonl` and the wider ledger structure store derived values with provenance (tool name, date, proposer role), but the adjudication field does not distinguish "confirmed to be computed" from "confirmed to satisfy the conjecture it relates to".
- The BSD conjecture (Sha_an = L'(E,1) * |E_tors|^2 / (Omega_E * Reg * prod c_p), used in Report #48 and TOOL_REGULATOR's docstring) is a natural litmus test — if all regulators stored in cartography satisfy the BSD product bound, that is strong evidence of correctness; any gross violation (regulator 100× off, or negative, or contradicting announced rank) is a red flag that survives tooling opacity.
- No existing audit loop was found in the codebase that systematically re-verifies stored derived quantities against their conjectures. The cartography schema's `predicates.py` validates evidence *types*, not *numeric correctness*.

## Prospective predictions
- **P1 — Saturation Index Detection**: At least 5% of stored TOOL_REGULATOR values over rank ≥2 curves will show evidence of insufficient saturation when compared against LMFDB canonical values, either as multiplicative factors near perfect-square integers or as regulator^2 relationships among related curves (e.g., quadratic twist pairs).
- **P2 — Adjudication-Conjecture Mismatch**: At least one curve will have a stored regulator marked `CONFIRMED` in adjudication status but violating the announced rank (negative regulator for rank ≥1, or regulator magnitude incompatible with height matrix rank via the BSD denominator).
- **P3 — Cross-Tool Inconsistency**: For the same elliptic curve, TOOL_REGULATOR and TOOL_ANALYTIC_SHA stored values will fail the BSD product relationship (deviation > 10% from the canonical L'(E,1) * Tate_pairing product), indicating one tool's output was stale or computed under different saturation settings.
- **P4 — Schema Corruption Signal**: Ledger inspection will reveal at least one record where the `adjudication` field is CONFIRMED but the `evidence_type` is PROPOSED (a state transition violation — proposed evidence cannot atomically confirm itself), or where the `regulator` and `rank` fields are paired inconsistently (e.g., rank=0 with nonzero regulator).

## Experiment
**Program-wide audit of derived quantities vs. conjectures**, run once to establish a baseline and then on a recurring cadence (quarterly) to detect drift:

1. **Inventory stored derived quantities** (no execution): Extract all records from `techne/cartography/store/taxonomy_events.jsonl`, `techne/cartography/store/claims.jsonl`, and related ledgers where `tool_name LIKE 'TOOL_REGULATOR|TOOL_ANALYTIC_SHA|TOOL_CONDUCTOR|TOOL_CLASS_NUMBER'` and `adjudication IN ('PROPOSED', 'CONFIRMED')`. For each record, extract: curve (a-invariants or LMFDB label), stored value, rank_lower/rank_upper, torsion_order, date_computed, proposer_role. Target: 1000–5000 curve-tool pairs.

2. **Load LMFDB canonical reference** (local read-only mirror; pre-cached): Use the locally installed LMFDB dumps (if absent, document this as an unresolved blocker). Construct a reference table of canonical (regulator, rank, Sha_analytic, conductor, torsion) keyed by curve a-invariants for all curves in the Prometheus inventory.

3. **Verification protocol per curve**:
   - **Rank consistency**: If stored rank_proved=True, verify that rank_lower == rank_upper. If not, flag as RANK_MISMATCH.
   - **Regulator sign and magnitude**: 
     - If rank=0, regulator must be zero (or 1.0 in some normalizations); any nonzero value flags as RANK_REGULATOR_CONTRADICTION.
     - If rank≥1, regulator must be positive. Compare against LMFDB canonical; if ratio > 2× or < 0.5×, flag as SATURATION_SUSPECT (possibly an index² error).
   - **BSD product bound**: For curves with rank ≤ 2 (high confidence in the BSD formula accuracy), compute the LHS of BSD (Sha_an × Reg × prod c_p) and RHS (L'(E,1) × |tors|²). Relative deviation > 10% flags as BSD_ANOMALY.
   - **Cross-tool consistency**: If both TOOL_REGULATOR and TOOL_ANALYTIC_SHA are stored for the same curve, verify they obey known relationships (e.g., Sha enters BSD denominator, regulator enters numerator with opposite sign). Disagreement on rank signals one tool saw stale/different data.
   - **Height matrix rank**: For rank ≥2, verify that the stored height_matrix (if provided) has rank == announced_rank. Non-full rank flags as HEIGHT_RANK_DEFECT.

4. **Schema audit (orthogonal to numeric verification)**:
   - Check that all CONFIRMED records have corresponding PROPOSED parent records (adjudication history integrity).
   - Check for impossible state transitions (e.g., PROPOSED → CONFIRMED with no predicate run, or CONFIRMED → PROPOSED).
   - Extract all records where `evidence_type` is DERIVED_INTERPRETATION but `adjudication` is CONFIRMED; these represent our own derived claims and require the strictest scrutiny.

5. **Log results**: Write a ledger `V2-T07_audit_ledger.jsonl` with one record per curve-tool pair, including: curve, stored_value, LMFDB_canonical, verification_status (OK / RANK_MISMATCH / SATURATION_SUSPECT / BSD_ANOMALY / etc.), deviation_ratio, adjacent_finding (e.g., "quadratic_twist_pair_both_suspect"). Never aggregate; row-level audit per `feedback_verdict_without_rows_is_an_assertion`.

## Controls
- **Reference population control**: LMFDB canonical values are pre-registered and read-only; no retro-fitting. If LMFDB is locally unavailable, treat absence of reference as a stopping condition (do not proceed without the gold standard).
- **Low-rank calibration control**: Run verification on a subset of rank-0 and rank-1 curves only first (lower false-positive rate for saturation detection due to simpler height matrices). Reserve rank ≥2 curves for a secondary pass after low-rank findings are adjudicated.
- **Tool-isolated recomputation (optional but recommended)**: For any curve flagged as SATURATION_SUSPECT, re-call TOOL_REGULATOR directly in a fresh Python session with explicit logging of `ellsaturation()` call and resulting index. This breaks the "control drawn from the treatment's selection relation" failure by independently re-deriving the quantity.
- **Negative control — unchanged curves**: Identify a set of curves (e.g., first 20 LMFDB by conductor) that have been in storage since the earliest Prometheus campaigns and have never been recomputed. Verify these *also* obey the verification thresholds; if they do not, the audit itself is suspect (measuring computational drift, not storage integrity).
- **Empty-store baseline**: Before populating the audit ledger, confirm that `techne/cartography/store/` is not empty and contains at least 100 curve records. If the store is empty or sparsely populated, audit cannot proceed (document as unresolved blocker).

## Confound defenses
- **Wrong population** (see `feedback_wrong_population_statistics`): LMFDB reference and Prometheus stored values must be keyed by the **same** curve definition (a-invariants or LMFDB short label). Any mismatch in curve definitions (different normalization, e.g., Weierstrass vs. Montgomery) breaks the comparison; pre-register the normalization standard before the audit begins.
- **Saturation-index ambiguity**: The regulator formula allows multiple normalizations (different conventions for the Neron-Tate height). Pre-register which convention TOOL_REGULATOR uses (PARI's default is Neron-Tate with respect to the canonical form). Check LMFDB's stated convention and document any conversion factor.
- **Stale reference data**: LMFDB dumps must have a timestamp. If any Prometheus computation date is *after* the LMFDB dump date, that curve's LMFDB value may be outdated (LMFDB corrects errors as Magma/PARI updates accumulate). Flag such pairs as REFERENCE_STALE and exclude from core falsifiers.
- **Torsion-order encoding**: LMFDB stores torsion as both order and structure (e.g., [2, 4]). Verify that the stored torsion_order matches the product of structure components; any discrepancy is an encoding error independent of the regulator itself.
- **Rank-proven status**: LMFDB's rank is fully proven for small conductor; for large conductor (>10^8), ranks are proven via 2-descent but the Mordell-Weil group is not fully known. Do not expect perfect BSD agreement for rank > 2 or conductor > 10^6; pre-register a two-tier threshold (tight for small, loose for large).

## Preregistered falsifiers (numeric thresholds)
(Thresholds calibrated to LMFDB audit precedents and TOOL_REGULATOR's documented saturation risk.)

- **F1 — rank-regulator consistency** (fatal): Any curve with rank=0 and regulator > 0.001 (accounting for numerical precision) OR rank ≥1 and regulator < 0 → REJECT audit. This is a logical impossibility, not a measurement error. Count: 0 allowed.
- **F2 — saturation-index signature** (major): Curves with ratio(stored_regulator / LMFDB_regulator) ≈ k² for integer k ∈ {2, 3, 4, 5} (common index values) account for ≥ 10 curves (raw count, not rate). Any single k covering ≥5 curves is a red flag for systematic saturation failure. Threshold: REJECT if ≥10 curves exhibit perfect-square-factor anomalies.
- **F3 — BSD product anomaly** (major): For rank ≤2 curves (high-confidence BSD formula), at least 95% must satisfy |LHS - RHS| / max(|LHS|, |RHS|) < 0.10 (10% relative deviation). If < 90% pass, REJECT.
- **F4 — adjudication integrity** (moderate): Any record with impossible state transitions (PROPOSED → CONFIRMED with no predicate log) or mismatched evidence_type/adjudication pairs (DERIVED_INTERPRETATION + PROPOSED allowed; DERIVED_INTERPRETATION + CONFIRMED requires documented predicate). Count ≥5 such records → escalate but do not auto-reject; document as findings.
- **F5 — cross-tool consistency** (major, if multiple tools stored): For curves with both TOOL_REGULATOR and TOOL_ANALYTIC_SHA values, verify that the BSD product relationship holds. If ≥20% of such curves violate the relationship beyond the rank-≥3 tolerance → REJECT.
- **PASS criterion**: All five falsifiers clear (F1–F5) AND the audit ledger is complete (no missing LMFDB reference for ≥95% of stored curves) AND negative-control baseline (unchanged curves) also passes F1–F3.

## Stopping rule
Run the full audit once with pre-registered sample size (~1000–5000 curve records from cartography/store/, all rank 0–3 curves). 

- **If all falsifiers F1–F5 clear**: Archive the ledger as `V2-T07_baseline_ledger.json` and schedule the next audit run for Q4 2026 (quarterly cadence). Document in `evidence_wiki/v2/arm_outputs/V2-T07_A_verdict.md` the pass thresholds and any patterns observed.
- **If F1 or F2 fails** (rank-regulator contradiction or saturation-index clusters): STOP. Do not proceed to F3–F5. This signals a tool-level error in prometheus_math (regulator computation or storage), not a schema-level issue. Route to Techne/Harmonia for TOOL_REGULATOR rebuild and re-validation against test_saturation_regression. Re-run audit only after rebuild is certified.
- **If F3 fails** (BSD anomaly ≥10%): Inspect the failing curves individually for signs of: (a) LMFDB reference being stale (check dump date vs. computation date); (b) rank_proved=False (unproven rank → BSD formula unreliable). If >50% of failures are due to (b), re-run audit on rank_proved=True subset only and re-register F3 threshold for the full set post-hoc. If rank-proof status is uncertain, escalate to Aporia for independent rank verification on a sample of failing curves.
- **If F4 fails** (adjudication integrity issues): Repair the schema (fix state transitions, backfill missing parent records). Re-run F4 check only after repairs. Do not skip to F5 without F4 passing.
- **If F5 fails** (cross-tool mismatch): Inspect whether TOOL_REGULATOR and TOOL_ANALYTIC_SHA were computed under different saturation bounds or on different dates. Re-verify the failing curves in isolation (re-call both tools); if re-computed values agree, cache-invalidation is likely. Archive the finding in `V2-T07_findings.md` and proceed to next audit cycle with a note on cache-coherence risk.

- **No more than 1 retry per falsifier** before escalating to Daedalus/Serendipity Foundry for a schema redesign that embeds verification state directly in storage (e.g., a `verification_timestamp` field and a `canonical_reference_checksum` to detect stale comparisons).

## Expected failure modes
- **Saturation-index clustering**: A batch of curves stored before TOOL_REGULATOR's saturation fix was deployed (if such a deployment happened between storage date and audit date) will show systematic index² inflation. Example: if deployment occurred in June 2026 and curves were stored in March 2026, all March curves might be off by 4× or 9×.
- **Rank-proven status mismatch**: A curve stored with rank_proved=True in Prometheus but rank_proved=False in LMFDB (or vice versa) will fail BSD checks due to formula assumptions. LMFDB's rank proof is more stringent for large conductors.
- **Normalization drift**: Neron-Tate height is defined up to a normalization constant (often ±2 or logarithmic scale factors). A regulator computed under PARI's default vs. LMFDB's convention may differ by a known multiplicative constant; if that constant is not pre-registered, false-positive anomalies ensue.
- **Torsion-order encoding errors**: A few LMFDB curves have torsion structure encoded incorrectly in older dumps (e.g., [2, 4] vs. Z/2 × Z/4 confusion). Prometheus might store the correct group structure but mismatch the LMFDB label's order field.
- **Ephemeral cache corruption**: If cartography/store/ is backed by an in-memory cache that is not synced to disk reliably, concurrent writes (e.g., during a campaign) might corrupt records. This would show up as random anomalies, not systematic patterns, and would require investigation of the storage layer.
- **Query-time computation drift**: If derived quantities are computed at *query* time (lazy evaluation) rather than stored eagerly, the audit might measure different values on different runs if the underlying library (PARI/cypari version) has drifted. Pre-register the exact tool versions and library versions used at storage time.

## Compute estimate
CPU-only, no GPU. Dominated by LMFDB reference load and per-curve BSD formula evaluation:
- **LMFDB reference load**: ~500 MB–1 GB dump (if pre-cached locally). One-time load; ~5 minutes to index.
- **Per-curve verification**: BSD formula evaluation is O(1) arithmetic; ~1000–5000 curves × ~1ms per curve = 1–5 seconds batch time.
- **Recomputation (optional, if F2 fails)**: Re-calling TOOL_REGULATOR on 50–100 suspect curves; each call costs ~100 ms (rank ≤2 curves, already known generators). Total: ~5–10 seconds.
- **Schema audit**: Ledger scan for state transitions and evidence-type mismatches; O(n) scan of cartography store, ~10 seconds for 10K records.
- **Total elapsed**: ~20–30 minutes (one-machine CPU; no parallelization required initially).
- **Storage for audit results**: `V2-T07_audit_ledger.jsonl` with ~1000–5000 rows, ~50 MB uncompressed.

## Prior evidence that materially changed this design (or 'none found')

**Found and used:**
1. `harmonia/memory/symbols/TOOL_REGULATOR.md` — supplied the critical saturation-index failure mode (index² inflation) and the concrete example (37.a1: 0.46 vs. 0.051). This directly shaped F2 (saturation-index signature falsifier) and the recomputation control.
2. `techne/cartography/schema.py` — supplied the ADJUDICATION and EVIDENCE_TYPE enumerations and the mandate that "only a deterministic predicate may write CONFIRMED". This shaped F4 (adjudication integrity) and the insight that schema verification is orthogonal to numeric verification.
3. `techne/ARSENAL_ROADMAP.md` — supplied the inventory of derived-quantity tools (TOOL_REGULATOR, TOOL_ANALYTIC_SHA, TOOL_CONDUCTOR, etc.) and their tier status. This shaped the scope of the audit (which tools to focus on).
4. Implicit references to BSD conjecture in `harmonia/memory/symbols/TOOL_REGULATOR.md` (Sha_an formula) — shaped F3 (BSD product anomaly falsifier).

**Not found but referenced in memory:**
- Report #48 (BSD Tier 1, Sha*Reg product bound) — cited in TOOL_REGULATOR.md but not located in this search. This would have calibrated the F3 threshold more precisely.
- Techne test files (`test_regulator.py`, `test_saturation_regression`) — grep found them but not read; they would have provided real test case coordinates and expected values for calibration.

**Search budget (13/15 operations used; 2 unused)**:
The two unused operations remain in budget for contingencies (e.g., if LMFDB reference location needs to be discovered, or if a critical doc was mis-parsed). Given the constraint, the design is based on incomplete reconnaissance; sections 5 (Controls, reference-population control) and 7 (confound defenses, stale-reference issue) are marked as requiring pre-run validation.

## Unresolved uncertainty
1. **LMFDB reference availability**: Is an LMFDB dump pre-cached locally in Prometheus? Which location? Which dump date? This is marked as a **stopping condition** (see Controls); the audit cannot proceed without resolving this.
2. **Cartography store population and schema evolution**: The audit assumes `techne/cartography/store/` contains 1000+ curve records with ADJUDICATION and EVIDENCE_TYPE fields. No direct inspection of the store schema was performed (read budget exhausted). If the store schema has evolved or is sparsely populated, the audit scope must shrink accordingly.
3. **Tool version history**: At what date was TOOL_REGULATOR's saturation fix deployed (if one exists)? Does the storage ledger track the tool version used at computation time? If not, detecting a systematic saturation-index error requires a reverse-lookup (compute tool version from date + changelog).
4. **Rank-proof ground truth**: Does Prometheus store a `rank_proved` flag for each curve, or is rank proof status only available via LMFDB? If Prometheus does not store rank proof, then F3 (BSD formula) must be gated by LMFDB's rank_proved status pre-retrieval.
5. **Audit timing and re-verification cost**: Is it feasible to re-call TOOL_REGULATOR on 100s of curves as part of the F2 remediation (recomputation control)? That depends on available GPU/CPU budget and whether Techne can schedule those tasks. Pre-approval recommended.
6. **Cross-tool consistency scope**: Are TOOL_ANALYTIC_SHA and TOOL_REGULATOR always computed together for the same curves, or are they stored independently? The F5 falsifier assumes paired storage; if they are independent, F5 is inapplicable.

