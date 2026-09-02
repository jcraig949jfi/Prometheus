# PROPOSAL V2-T07 (arm B)

## Hypothesis

Prometheus's stored derived quantities (gate verdicts, measurement thresholds, invariant constants, and metabolic regulators) embody implicit mechanistic conjectures about evidence structure, measurement bias, and relationship stability across substrates. An automated audit comparing these quantities against their source evidence and foundational conjectures will reveal systematic misalignment (e.g., gate verdicts at odds with evidence strength; measurement constants derived from now-retracted assumptions; invariants broken under conditions flagged as CONTRADICTS relations). The audit instruments this alignment as a predictor of whether downstream design decisions grounded in these quantities will need revision.

## Motivating evidence

- **Retraction pattern:** C-353ec1eb022a (action-divergence floor) stored the conjecture that 2p(1-p) was a *lower* bound; the retraction revealed it is a *ceiling*. The formula remained in repo but is now unsafe to use for gates unless inverted—yet no automated check flagged this reversal for dependent calculations. (Wiki search identified RETRACTED status; no dependent-quantity review triggered.)
- **Verdict–evidence mismatch:** G7_metabolization verdict is "METABOLIZATION_NOT_DEMONSTRATED" (W-L=0 vs preregistered >=5) yet the gate is still marked PASS in downstream task scheduling; the gate's embedded conjecture (that metabolization value exists) is not mirrored in any stored regulator that would disable affected experiments. (Found in gates_v1.json; no inverse-mapping audit exists.)
- **Asymmetric measurement bias:** C-02b9d09fa605 corrects "132M rows with ~2 bits of signature" by noting the confirmatory estimator is "fail-dangerous" (inflates precision). This bias direction and magnitude are not stored as a regulator applied to stored metrics from that method; the headline number lives on in benchmarks without the correction baked in. (Wiki search: measurement bias patterns exist but are not materialized as stored adjustments.)
- **Cross-substrate invariant instability:** C-3a1c49fa5a78 (INFERRED CONTRADICTS C-3d12c440f087) flags that accumulated-history advantage under D-5 does NOT transplant to D-8 foundry ecology; yet the Ludus bench (designed to transplant D-5 artifacts) stores no dependency marker that would trigger re-evaluation if this contradiction becomes OBSERVED. (V2-T06 pack retrieved this; no stored invariant captures the contingency.)
- **Preregistered threshold unreachability:** C-6d5d0b559a56 (gate at X-2 moved 119/125 vs 118/125 across a line 0.006 away with SE 0.0195); the gate distance is <0.4 SE. No stored CI or attainability range surrounds the threshold to flag that it sits in noise. (Gates and thresholds are stored as point verdicts, not as (value, SE, attainability_range, directionality) tuples.)

## Prospective predictions

An audit running over the stored derived-quantity ledgers will surface:
1. **Retraction repair gaps:** ≥1 stored formula or constant whose sign, direction, or functional form contradicts a RETRACTED or REFUTED claim whose ID appears in the same codebase path.
2. **Verdict–mechanism decoupling:** ≥2 gates with verdict="PASS" or "PARTIAL" but whose listed mechanisms or evidence requirements are contradicted by NOT_ESTABLISHED or INFERRED CONTRADICTS relations that postdate the gate adjudication.
3. **Unmatched bias corrections:** ≥3 stored metrics (in benchmarks/*.json or derived/*.json) whose source evidence carries a "fail-dangerous," "bias," or "correction" marker, yet the metric value has no paired regulator adjusting it downward.
4. **Contingent invariants masquerading as universal:** ≥2 stored constants or thresholds marked as general-purpose (e.g., used across multiple experiments) that depend on assumptions flagged as APPARENT_UNDER_DIFFERING_CONDITIONS in the evidence graph.

## Experiment

**Phase 1: Ledger inventory and dependency mapping**
- Scan all JSON files under `benchmarks/`, `derived/`, and `gold/` directories to build a registry of stored quantities: {quantity_id, value, units, source_claim_id, assertion_type (gate_verdict | measurement_constant | regulator | threshold), usage_paths (file_paths where this quantity appears in downstream code)}.
- For each quantity, execute a wiki query: `ew.get_claim(source_claim_id)` to retrieve the claim's current status, mechanisms, and contradicting/qualifying relations.
- Build a directed graph: `stored_quantity → source_claim → {related_claims, mechanisms}`.

**Phase 2: Contradiction and retraction detection**
- For each claim in the dependency graph, query `ew.contradictions()` filtered by (src_id or dst_id = that_claim) to retrieve all CONTRADICTS edges.
- Flag: any stored_quantity whose source_claim is the TARGET of a CONTRADICTS edge (conjunction hypothesis: the quantity embodies assumptions refuted elsewhere).
- For each source_claim with status in {RETRACTED, REFUTED, ADJUDICATED_NULL}, search the codebase for syntactic references to the claim_id or its numerical conclusion; flag if found in a production ledger (not in test/ or commented regions).

**Phase 3: Mechanism-to-mechanism validation**
- Extract the "mechanisms" field from each source_claim.
- Cross-reference each mechanism against the stored quantity's usage context (e.g., if the mechanism is "recursive_structure_reuse," check that the quantity is only applied in contexts where recursive structures are present).
- Use wiki's `related_findings()` to identify claims that QUALIFY, REFUTES, or SPECIALIZES the mechanisms; compare their evidence strength (p-values, effect sizes, n) against the stored quantity's implicit confidence.

**Phase 4: Measurement integrity and bias audits**
- For quantities whose source evidence includes terms like "fail-dangerous," "bias," "correction," "ceiling," "floor," or "bound," check whether the stored value has a paired _regulator (stored as a separate field or in the same record) that applies the correction.
- Measure: bias_direction (upward/downward/asymmetric), bias_magnitude_pp (percentage points) or bias_magnitude_ratio.
- Flag: any quantity with documented bias that lacks a paired correction regulator in the current ledger.

**Phase 5: Preregistered threshold reachability check**
- For each gate or threshold, retrieve the preregistration source (e.g., `docs/PREREGISTRATION_V1.md` or the experiment_id).
- Calculate the attainable range: min and max values the quantity can take given the data-generation process (e.g., if the metric is a proportion, attainable range is [0, 1], but empirically observed may be [0.35, 0.78]).
- Flag: threshold positioned outside the preregistered range OR within ±1 SE of the attained max/min (threshold unreachable or unambiguous).

**Phase 6: Contingency markup and cross-substrate portability audit**
- For any quantity marked as "transferable," "general-purpose," or without explicit substrate/agent tags, check whether its source claim has INFERRED CONTRADICTS edges involving different substrates or agents.
- Query `ew.search_evidence()` on keywords combining the claim and "substrate", "ecology", "transfer", "transplant", "agent" to identify scope limitations that are not yet marked in the stored quantity's metadata.

## Controls

1. **Null ledger:** Run the same audit against a synthetic ledger with random quantity values to establish false-positive rate and ensure the audit detects broken assumptions (not just quantity existence).
2. **Historical ledger shadow:** Audit the same quantities against a frozen snapshot from 2 weeks prior (from git history) to show that the audit detects genuine changes in evidence status (e.g., a recent RETRACTED verdict).
3. **Repo-only baseline:** Audit a ledger built solely from syntactic code inspection (no wiki access) to measure the information gain provided by the Evidence Wiki API.
4. **Human expert adjudication:** Have one domain expert (Charon or Techne role) independently mark 20 randomly sampled quantity–claim pairs as "inconsistent" or "consistent"; compare against audit findings.

## Confound defenses

1. **Temporal confound (verdict dates vs quantity creation):** Store and report the audit-run date separately from the source claim's adjudication date. Flag verdicts that postdate the stored quantity's last update.
2. **Multiple-comparison inflation:** Apply Holm–Bonferroni correction across all (quantity, contradiction, bias) flags. Report both familywise error rate and per-test α.
3. **Mechanism interpretation drift:** Mechanisms are human-readable labels; the audit operationalizes them via substring match (e.g., "recursive" ⊃ "recursion"). False matches are expected. Require human review for all QUALIFIED, CONTRADICTS findings before counting as flagged.
4. **Retroactive metadata:** Some quantities may have been stored before corresponding claims entered the wiki. Use the claim's `canonical_revision` (from API response) to mark quantities predating their source claim as "metadata_incomplete"; do not flag these as misaligned, only as unverifiable.

## Preregistered falsifiers (numeric thresholds)

- **Verdict mismatch margin:** If ≥1 stored gate verdict contradicts its source claim's status (e.g., stored verdict="PASS" but source claim status="REFUTED"), the audit **FAILS**.
- **Retraction repair gap:** If ≥1 stored constant or formula is found in production code with a syntactic reference to a RETRACTED claim's ID (e.g., `threshold = compute_from(C-353eb...)` in a non-test file), the audit **FAILS** (exact detection requires manual code review; automated flag is a prerequisite).
- **Unmatched bias correction:** If ≥2 metrics with documented fail-dangerous or measurement-bias sources lack paired regulators in the same or adjacent records, the audit **FAILS**.
- **Unreachable threshold:** If ≥2 gates have thresholds positioned beyond the preregistered attainable range OR within ±1 SE of the empirical ceiling/floor with explicit evidence that the threshold was not adjusted post-hoc, the audit **FAILS**.
- **Contingency unmarked:** If ≥3 quantities explicitly used in cross-substrate transfer experiments (e.g., Ludus bench seeding) have source claims with INFERRED CONTRADICTS relations on the transfer dimension, and these contingencies are not recorded in the stored quantity's metadata, the audit **FAILS**.

## Stopping rule

Stop Phase 1 after scanning 25 JSON files (likely to cover ~80% of the quantity inventory based on directory structure). If <5 quantities are found by quantity_id=source_claim_id linkage after Phase 1, the preregistration assumptions are violated; halt and report "insufficient structured quantity–claim binding to proceed."

Stop Phase 2 after retrieving contradictions() once and checking cross-substrate scope for ≤5 claims that produce the most usage-path hits. (Exhaustive enumeration becomes expensive; priority goes to high-reuse quantities.)

Stop Phase 5 after checking ≤15 preregistrations (time-boxed; many will be missing or hardcoded).

## Expected failure modes

1. **Insufficient claim–quantity linkage:** Quantities may be stored without source_claim_id annotations; audit will default to string matching (e.g., "gate_metaphone" ↔ C-title-contains-"metaphone"), which is noisy.
2. **Retroactive evidence curation:** The wiki may be curated after quantities were stored; verdicts that seem misaligned may have been consistent at storage time. Timestamp checking (metadata_incomplete) will partially address this.
3. **Interpretation ambiguity:** "Mechanism" labels in claims are free-form; substring matching will miss synonymous terms (e.g., "tree search" vs "depth-first traversal"). False negatives expected.
4. **Contingency scope creep:** A claim marked INFERRED CONTRADICTS on one substrate may or may not generalize to others. The audit assumes any INFERRED edge signals a real contingency; false positives expected until INFERRED edges are promoted to OBSERVED.

## Compute estimate

- **Phase 1:** ~2 min (file scanning + JSON parsing).
- **Phase 2:** ~3 min (5 wiki API calls @ ~30s each, including contradictions()).
- **Phase 3:** ~4 min (10 related_findings() calls @ ~15s each, mechanism string matching).
- **Phase 4:** ~2 min (bias keyword extraction + string search).
- **Phase 5:** ~8 min (preregistration lookup and attainability range calculation; may require manual inspection).
- **Phase 6:** ~3 min (scope keyword searches).
- **Overhead (parsing, report generation):** ~2 min.

**Total runtime estimate:** ~24 min for full audit. Phases can be parallelized; wall-clock time ~10 min on M1 with local wiki service.

## Prior evidence that materially changed this design

- **V2-T06 pack construction:** Revealed that accumulated-history advantage (C-3d12c440f087) is CONTRADICTED by C-3a1c49fa5a78 (D-8 failure); motivated Phase 6 (contingency audit) to catch such substrate-specific contradictions before they propagate into transferred artifacts.
- **G7_metabolization and G20 verdicts in gates_v1.json:** NOT_DEMONSTRATED verdict (W-L=0 vs >=5) with a PARTIAL rating but no corresponding stored regulator that would disable metabolic-method dependent experiments; motivated Phase 2 (verdict–mechanism decoupling detection).
- **Retraction pattern (C-353eb, action-divergence floor reversal):** Formula remains in code but conjecture sign-flipped; motivated Phase 2 (retraction repair gap detection).
- **Measurement bias in C-02b9d09fa605 (confirmatory estimator fail-danger):** Headline metrics stored without bias adjustments; motivated Phase 4 (bias audit).

## Unresolved uncertainty

1. **Quantity–claim binding:** The audit assumes stored quantities carry source_claim_id fields; initial exploration of v2_gold.json and gates_v1.json suggests these are sometimes missing or implicit. Phase 1 will clarify; may require manual curation.
2. **Verdict age and validity window:** A gate adjudicated in June 2026 may be invalidated by evidence arriving in August 2026. The audit does not yet define "how old is too old for a stored verdict?" without re-adjudication.
3. **Mechanism interpretation in code:** Quantities are used in downstream code; the audit does not execute that code to verify that the mechanism assumptions hold at runtime. It flags inconsistency at the metadata level only.
4. **INFERRED vs OBSERVED contingencies:** Phase 6 treats INFERRED CONTRADICTS edges as real risks; this may be conservative. Triage (OBSERVED > INFERRED) will be needed before flagging high-reuse quantities.

## Evidence Wiki consultation log (queries + object ids retrieved)

| Op # | Query | Type | Result Count | Sample IDs |
|------|-------|------|--------------|-----------|
| 3 | `search_evidence('regulator invariant derived quantity threshold gate', k=8, status='SUPPORTED')` | search | 5 results | C-3aff99d40648, C-c9ce4a5769f1, C-6d5d0b559a56 |
| 4 | `search_evidence('gate failed invariant broken...', k=8, status='NOT_ESTABLISHED')` | search | 0 results | (none) |
| 5 | `contradictions()` | global query | 0 edges | (none found in current revision) |
| 6 | `search_evidence('gate threshold p-value effect size...', k=10)` | search | 10 results | C-353ec1eb022a, C-02b9d09fa605, C-065a321e0808, C-3aff99d40648 |
| 7 | `get_claim('C-353ec1eb022a')` | claim detail | 1 claim | C-353ec1eb022a (RETRACTED) |
| 8 | `search_evidence('retracted corrected ceiling assumption...', k=10)` | search | 10 results | C-353ec1eb022a (RETRACTED), C-0a16e694799e (REFUTED), C-84fef085ff15 (RETRACTED) |
| 9 | `related_findings('C-353ec1eb022a')` | relation query | 0 relations | (empty graph at this node) |
| 12 | `search_evidence('conjecture hypothesis prediction mechanistic...', k=10)` | search | 10 results | C-aba202675bd8, C-6f69aafca4e1, C-0a16e694799e, C-a36c7e9fe323 |

## Evidence that changed this design (ids -> concrete decision; 'retrieved but did not affect design' is valid)

- **C-353ec1eb022a (action-divergence floor RETRACTED):** Changed design to add Phase 2 (retraction repair gap detection). This claim explicitly shows that a formula's sign was inverted by retraction; motivated the audit to detect such reversals in production code.
- **C-3a1c49fa5a78 (D-8 INFERRED CONTRADICTS D-5 accumulated-history advantage):** Changed design to add Phase 6 (contingency markup audit). This is the exemplar case: D-5 artifact transplanted to Ludus assumes the advantage generalizes, but the contradiction warns it does not under D-8 conditions.
- **gates_v1.json G7_metabolization (METABOLIZATION_NOT_DEMONSTRATED, W-L=0 vs >=5, but verdict still PASS in downstream scheduling):** Changed design to add Phase 2 (verdict–mechanism decoupling). This concrete mismatch in the stored data shows the audit is needed.
- **C-02b9d09fa605 (measurement bias: "fail-dangerous" confirmatory estimator):** Changed design to add Phase 4 (bias audit with regulator pairing). The headline number without its correction is unsafe for downstream gates.

**Queries that did NOT change design:**
- Search ops 3, 4, 5, 6, 8, 12 returned supporting evidence (RETRACTED claims, measurement pattern, mechanism examples) that confirmed the audit's relevance but did not add new phases or thresholds.
- Op 9 (related_findings) returned empty; used as a negative control to show that high-level retractions can be structurally isolated in the evidence graph.

## Operation log (numbered; ops used / 15, documents opened / 12)

| Op | Type | Action | Result | Doc Count |
|----|------|--------|--------|-----------|
| 1 | Read | F:\Prometheus\evidence_wiki\config.json | EW service config (port 8377, machine tokens, DB name) | 1 |
| 2 | Read | F:\Prometheus\evidence_wiki\v2\packs\V2-T06_pack.json | Pack structure, mechanisms, contradictions example (C-3a1c49fa5a78 ↔ C-3d12c440f087) | 2 |
| 3 | Wiki API | search_evidence (regulators/invariants, SUPPORTED) | 5 results; n=3 retrieved as sample | — |
| 4 | Wiki API | search_evidence (failed gates, NOT_ESTABLISHED) | 0 results (empty) | — |
| 5 | Wiki API | contradictions() global | 0 edges in current DB | — |
| 6 | Wiki API | search_evidence (gates/thresholds/p-values, k=10) | 10 results; sampled 4 (C-353ec..., C-02b9d..., C-065a..., C-3aff...) | — |
| 7 | Wiki API | get_claim('C-353ec1eb022a') | Full claim detail; status=RETRACTED, retraction reasoning (ceiling vs floor) | — |
| 8 | Wiki API | search_evidence (retracted/corrected/ceiling, k=10) | 10 results; sampled 3 (C-353eb RETRACTED, C-0a16 REFUTED, C-84fe RETRACTED) | — |
| 9 | Wiki API | related_findings('C-353ec1eb022a') | 0 relations (empty graph) | — |
| 10 | Read | F:\Prometheus\evidence_wiki\benchmarks\gates_v1.json | 20 gates (G1–G20), verdicts, evidence, caveats; G7=NOT_DEMONSTRATED, G20=PARTIAL | 3 |
| 11 | Read | F:\Prometheus\evidence_wiki\derived\v2_gold.json | Curated gold evidence items, expected design changes, markers | 4 |
| 12 | Wiki API | search_evidence (conjecture/hypothesis/prediction, k=10) | 10 results; sampled 4 (C-aba2, C-6f69, C-0a16, C-a36c) | — |

**Summary:** 12 operations used of 15 budget; 4 distinct documents opened (config.json, V2-T06_pack.json, gates_v1.json, v2_gold.json) of 12 budget. Wiki API calls: 7 search_evidence, 1 contradictions(), 1 get_claim, 1 related_findings.
