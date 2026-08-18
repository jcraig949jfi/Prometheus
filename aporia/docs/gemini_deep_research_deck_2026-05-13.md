# Gemini Deep Research Deck — 2026-05-13

**Combined: 3 substrate-shaped pilot prompts (DR-001 / DR-007 / DR-231) + 17 standard Tier-1/2 entries.**

Pilot prompts test the substrate-shaped pipeline against narrative-only baselines from 2026-05-11. Standard prompts continue Tier-1 anti-anchor verification + Tier-2 catalog continuation per the queue.

Fire:
```
python aporia/scripts/gemini_deep_research_dispatch.py \
    --deck aporia/docs/gemini_deep_research_deck_2026-05-13.md \
    --out aporia/docs/deep_research_batch_2026-05-13 \
    --batch-size 3 --resume
```

After return, post-process via:
```
python aporia/scripts/parse_substrate_blocks.py --batch-dir aporia/docs/deep_research_batch_2026-05-13  # for pilot 3
python aporia/scripts/validate_substrate_blocks.py --staged-dir aporia/docs/staged_substrate_blocks/2026-05-13  # for pilot 3
python aporia/scripts/burn_research_tokens.py --log-only --batch-dir aporia/docs/deep_research_batch_2026-05-13  # mark all 20 fired
```

---

### Prompt 1: DR-001 — Verify AA-013 Strassen direct-sum R<=7 safe zone (Rupniewski 2024) [SUBSTRATE-SHAPED]

```
Project Prometheus is a multi-agent mathematical research substrate. Doctrine constraints binding on your output:

1. NO paper-publishing framing. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, work-queue entries), not publishable claims.
2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist. When literature exhibits gravity wells, surface the alternatives explicitly and weight them equal-or-higher.
3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL from UNCONDITIONAL. Note WITHDRAWN preprints explicitly.
4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants. Tensor rank / border rank / cactus rank / border cactus rank / slice rank / partition rank / analytic rank / geometric rank are EIGHT distinct coordinates. Determinantal complexity dc / border determinantal dc-bar / formula size L / equivariant dc are FOUR distinct coordinates.
5. Date everything. 2024-2026 work especially - give the month and year of each cited result.
6. Behavior delta. Every finding must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

---

## TASK: anti-anchor verification

Verify the following anti-anchor candidate against primary literature:

**Candidate:** Verify AA-013 Strassen direct-sum R<=7 safe zone (Rupniewski 2024)

**Context:** Rupniewski's 2024 work proposes a "safe zone" R<=7 for the small-tensor case of Strassen's direct-sum additivity conjecture — meaning the conjecture is verified by exhaustive search for tensors of rank <= 7 in this regime. The exact bound and the regime in which it holds need primary-source pinning before promotion to the substrate's anti-anchor registry as a [VERIFY-LIVE] entry.

**Downstream consumer:** Techne v4.0 Wave 2 BorderRankWitness sub-cluster registration (SmallTensorAdditivitySafeZone Tier-B sub-type)

Produce a 4-section response:

(a) PRIMARY SOURCE CONFIRMATION. Quote the relevant theorem in the primary source. Give arXiv ID, journal reference, date of definitive publication.
(b) FOLLOW-ON WORK (2024-2026). Survey work that supersedes, refines, or cites this result.
(c) FALSE-FORM RECURRENCE. Search recent literature for the false form being asserted by other authors.
(d) RECOMMENDATION. Is the proposed anti-anchor true-form correct as stated, needs refinement, or needs inversion?

---

## SUBSTRATE BLOCK APPENDIX (REQUIRED)

At the END of your report, emit fenced YAML blocks tagged with their substrate type. The blocks will be parsed and validated automatically; conformance to schema is required. Schemas live at techne/contracts/substrate_block_schemas/.

For this anti-anchor verification, emit:

1. ONE anti_anchor block per AA candidate verified. Schema fields: _schema_version (const "1.0.0"), id (string like AA-013), name (UPPER_SNAKE_CASE identifier, no bare-noun coordinate words like "rank"/"complexity"/"dimension"/"degree"), false_form (string), true_form (string, min 60 chars - do not clip qualifiers), citation (arXiv:XXXX.XXXXX or DOI format), citation_status (peer_reviewed | preprint | withdrawn | conditional), risk_tier (high | medium | low), source_report (this report file name), verified_against_primary (boolean).

2. IF verification surfaces sub-anchors or related claims, emit additional anti_anchor blocks with id AA-013a, AA-013b, etc.

3. IF the recommendation includes a catalog correction, emit a catalog_edit block: _schema_version, entry_id (T#NN), field (refs / status / opens / etc), before (verbatim current text), after (verbatim proposed text), reason, citation, reviewer_action (replace | append | annotate).

Example block format:

```yaml
# substrate_block: anti_anchor
- _schema_version: "1.0.0"
  id: "AA-013"
  name: "STRASSEN_DIRECT_SUM_SAFE_ZONE_R7"
  false_form: "..."
  true_form: "..." # min 60 chars
  citation: "arXiv:XXXX.XXXXX"
  citation_status: "preprint"
  risk_tier: "medium"
  source_report: "01_dr_001_aa_013_strassen_substrate_shaped.md"
  verified_against_primary: true
```

Length: 2000-4000 words narrative + substrate blocks at end. No paper framing. Date every citation.
```

---

### Prompt 2: DR-007 — Verify AA-019 LMFDB GL(3) root number ML-predicted vs analytically proven [SUBSTRATE-SHAPED]

```
[Same doctrine framing as Prompt 1 - HARD-1 through HARD-6 binding constraints]

---

## TASK: anti-anchor verification with operational urgency

Verify the following anti-anchor candidate. This is operationally urgent — Ergon's maass_gl3_gap_scan.py is in active use against LMFDB GL(3) data that may be ML-predicted rather than analytically proven.

**Candidate:** Verify AA-019 LMFDB GL(3) root number ML-predicted vs analytically proven

**Context:** Recent work uses ML / murmuration-based methods to predict GL(3) automorphic L-function root numbers at scale. Some LMFDB entries may carry ML-predicted root numbers rather than analytically proven ones. The provenance distinction is load-bearing: an Ergon training corpus that treats ML-predicted root numbers as ground truth would be calibration-poisoned.

**Downstream consumer:**
- Ergon ergon/maass_gl3_gap_scan.py trust-tier annotation
- Techne v4.0+ MaassGL3SpectralBundle Tier-F primitive (when designed)
- Anti-anchor registry pin against ml_predicted treated as ground truth

Produce the standard 4-section response: PRIMARY SOURCE CONFIRMATION / FOLLOW-ON WORK / FALSE-FORM RECURRENCE / RECOMMENDATION.

---

## SUBSTRATE BLOCK APPENDIX (REQUIRED)

Emit at end of report:

1. ONE anti_anchor block for AA-019 itself.
2. IF verification surfaces specific LMFDB entry-level provenance distinctions (e.g. "rows X through Y are ml_predicted, rows Z onward are analytically proven"), emit ONE OR MORE training_anchor blocks. Schema fields: _schema_version (const "1.0.0"), id (anchor-maass_gl3-NNN), domain ("maass_gl3"), anchor_type (one of: invariant_value | classification | bound | predicate | spectrum | decomposition), dataset_source (URL / LMFDB table / paper ref), scale (object with instance_count and coverage_qualifier), prompt_template, expected_answer_shape, verification_method, trust_tier (analytically_proven | numerically_certified | ml_predicted | unverified), source (primary citation), source_date.
3. IF a paradigm candidate emerges (e.g. "murmuration-based prediction of root numbers" as methodology), emit a paradigm_candidate block: _schema_version, id (P-NEW-XXX), name (MurmurationRootNumberPrediction-style), category (methodology), consumes, produces, status (load-bearing | candidate | retracted), source.

Length: 2500-4500 words narrative + substrate blocks at end. The trust_tier field on training_anchor blocks is load-bearing - do not collapse ml_predicted into numerically_certified.
```

---

### Prompt 3: DR-231 — Jones polynomial value range + extremal coefficients 2024-2026 [TIER-3 SUBSTRATE-SHAPED]

```
[Same doctrine framing - HARD-1 through HARD-6 binding constraints]

---

## TASK: Tier-3 calibration anchor mining for knot theory

This is a calibration-anchor mining survey for the knot theory domain. Knot theory is HARD-3 priority adjacent (tensor mathematics is the primary HARD-3 weight; knots are second-tier calibration territory).

**Topic:** Jones polynomial value range + extremal coefficients 2024-2026

Produce a 7-section substrate-grade report:

1. Brief summary (1 paragraph): the state of the Jones polynomial value range question and extremal coefficient bounds as of 2024-2026.
2. Flagged findings (5-8 bullets): non-obvious recent results, withdrawn-paper risks, attribution corrections worth pinning.
3. Problem statement (formal).
4. Status & bounds (table form, dated). What's the current best lower/upper bound on extremal coefficient magnitudes? What knots saturate the bound? Where are the open frontiers?
5. Literature (primary sources, arXiv IDs, 2024-2026 frontier).
6. Attack vectors active in the literature (paradigms, sub-tactics).
7. Cross-references (other catalog entries, related Tier-3 surveys).

Cite >=2 of these patterns where relevant: PATTERN_PRIME_GRAVITATIONAL_OVERFIT, PATTERN_CONDUCTOR_CONFOUND, PATTERN_BASE_RATE_NEGLECT, PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_RANK_PARITY_LEAK.

---

## SUBSTRATE BLOCK APPENDIX (REQUIRED)

Emit at end of report:

1. MULTIPLE training_anchor blocks (target 5-15) for specific knot/Jones-polynomial labeled instances that the calibration battery can verify. Each anchor: domain="knot_theory" or "knots", anchor_type appropriate (invariant_value for specific Jones polys; bound for extremal coefficient bounds; etc), dataset_source (KnotInfo URL / paper ref), trust_tier (analytically_proven for theorems; numerically_certified for SnapPy-verified; ml_predicted if any ML methods used). The full set should exercise the trust_tier enum.

2. ZERO OR MORE paradigm_candidate blocks if methodological novelty emerges (e.g. "Khovanov-categorification-driven extremal coefficient bounds" if that turns out to be a paradigm).

3. ZERO OR MORE composition_rule blocks if cross-tier composition surfaces (e.g. "Jones polynomial bound + Khovanov homology bound = sharper bound" would be a Tier-something composition).

4. ZERO OR MORE primitive_proposal blocks if the survey surfaces a new primitive candidate the substrate vocabulary should register.

5. ZERO OR MORE catalog_edit blocks if the survey corrects an existing entry in aporia/mathematics/tensor_open_problems_v1.md or surfaces a new catalog entry candidate.

This Tier-3 prompt exercises the FULL substrate_block schema set deliberately. The pilot's job is to discover which schemas Gemini emits cleanly and which need refinement.

Length: 3000-5000 words narrative + substrate blocks at end. The substrate blocks ARE the deliverable; the narrative supports them.
```

---

---

### Prompt 4: DR-021 — VERIFY-LIVE T#20 Manziuk-Ventura 2024 minimal border Comon n<=d+1 regime

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** VERIFY-LIVE T#20 Manziuk-Ventura 2024 minimal border Comon n<=d+1 regime

**Why this verification matters:** Synthesis 2026-05-11 §2 [VERIFY-LIVE]; n<=d+1 regime + tame + sharp classifications need primary-source pin from arXiv:2411.05721

**Downstream consumer:** T#20 catalog edit propagate; MinimalBorderRankComonWitness sub-type classifications confirm

**Tags / context:** tensor, comon, border-rank, T#20, VERIFY-LIVE

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 5: DR-022 — VERIFY-LIVE T#23 Strassen tensor-rank additivity safe-zone (same as T#6)

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** VERIFY-LIVE T#23 Strassen tensor-rank additivity safe-zone (same as T#6)

**Why this verification matters:** Synthesis 2026-05-11 §2 [VERIFY-LIVE]; T#23 shares Rupniewski 2024 source with T#6; verify rank-7 ceiling annotation explicit in primary

**Downstream consumer:** T#23 catalog edit propagate; cross-link with T#6 sub-type registration

**Tags / context:** tensor, additivity, catalog, T#23, VERIFY-LIVE

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 6: DR-023 — VERIFY-LIVE T#86 Houston-Goucher-Johnston 2024 Bell-number det bound + Han-Ju-Kim 2025 det_4=12 perm_4=8

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** VERIFY-LIVE T#86 Houston-Goucher-Johnston 2024 Bell-number det bound + Han-Ju-Kim 2025 det_4=12 perm_4=8

**Why this verification matters:** Synthesis 2026-05-11 §2 [VERIFY-LIVE]; Han-Ju-Kim 2025 over arbitrary char != 2 is the new claim; needs primary-source pin

**Downstream consumer:** T#86 catalog edit propagate; BellNumberDeterminantBound Tier-B sub-type registration

**Tags / context:** tensor, det-perm, bell-number, T#86, VERIFY-LIVE

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 7: DR-024 — VERIFY-LIVE T#93 Burgisser-Dogan-Makam-Wigderson 2026 torus-action orbit closure P-time

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** VERIFY-LIVE T#93 Burgisser-Dogan-Makam-Wigderson 2026 torus-action orbit closure P-time

**Why this verification matters:** Synthesis 2026-05-11 §2 [VERIFY-LIVE]; BDMW 2026 P-time torus-action OCI is the new claim; TOCI complexity class emerged 2024-2026

**Downstream consumer:** T#93 catalog edit propagate; OrbitClosureNonMembershipWitness sub-type TOCI primitive proposal

**Tags / context:** tensor, orbit-closure, complexity, T#93, VERIFY-LIVE

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 8: DR-025 — VERIFY-LIVE AA-021 AlphaTensor field-of-definition (Nature 2022 paper primary pin)

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** VERIFY-LIVE AA-021 AlphaTensor field-of-definition (Nature 2022 paper primary pin)

**Why this verification matters:** Synthesis 2026-05-11 §12; AA-021's specific claim that AlphaTensor failed over C should be primary-pinned via the Nature paper

**Downstream consumer:** AA-021 primary-source field-of-definition pin; AlgorithmEvolutionaryLoop primitive field schema

**Tags / context:** method, alphatensor, alphaevolve, AA-021, VERIFY-LIVE

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 9: DR-026 — Survey literature supporting TensorNetwork + ContractionOrderWitness Tier-A++ primitive (T#84)

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** Survey literature supporting TensorNetwork + ContractionOrderWitness Tier-A++ primitive (T#84)

**Why this verification matters:** Highest-priority Tier-A++ primitive per synthesis 2026-05-09 §8 Wave 1; need cotengra/opt_einsum production-stack literature + line-graph treewidth complexity bounds + heuristic-with-bounds vs exact distinction; pre-requisite for substrate-tester probes

**Downstream consumer:** TensorNetwork + ContractionOrderWitness Tier-A++ registration unblocked; cotengra/opt_einsum substrate-canonical handle spec

**Tags / context:** tensor, tensor-network, contraction, tier-A++, T#84

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 10: DR-027 — Survey literature supporting CactusRankWitness pilot (T#19) for Tier-B contract change

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** Survey literature supporting CactusRankWitness pilot (T#19) for Tier-B contract change

**Why this verification matters:** Synthesis 2026-05-09 §8 Wave 1 pilot for Tier-B contract change; need apolar 0-dim Gorenstein scheme construction lit + Macaulay2 Apolarity package state + extreme-rank examples; pre-req for pilot

**Downstream consumer:** CactusRankWitness Tier-B sub-type pilot registration; T-ST-T19-001 substrate-tester probe spec

**Tags / context:** tensor, cactus, tier-B, T#19

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 11: DR-028 — Survey RankZooSignature Tier-A++ tracking primitive supporting lit (T#13, T#19, T#22)

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** Survey RankZooSignature Tier-A++ tracking primitive supporting lit (T#13, T#19, T#22)

**Why this verification matters:** Tier-A++ retrofittable on existing tensor nodes; need separator constructions Lampert-Moshkovitz 2509.06294 + Buczynska-Buczynski 2601.19558 + Shitov 2021 perm_3=16 in single unified spec

**Downstream consumer:** RankZooSignature Tier-A++ field-set finalization; HARD-5 enforcement spec

**Tags / context:** tensor, rank-zoo, tier-A++, T#13, T#19, T#22

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 12: DR-029 — Survey BorderRankWitness Tier-B parent + cross-cutting sub-primitives (T#34) supporting lit

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** Survey BorderRankWitness Tier-B parent + cross-cutting sub-primitives (T#34) supporting lit

**Why this verification matters:** Parent class for Tier-B cluster; need ∃R-hardness lit + DualityCheck + PrecisionFloorCertificate constructions; pre-req for Wave 2 Tier-B sub-type cluster registration

**Downstream consumer:** BorderRankWitness Tier-B parent + DualityCheck + PrecisionFloorCertificate cross-cutting sub-types registration

**Tags / context:** tensor, border-rank, tier-B, T#34

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 13: DR-030 — Survey LimitWitness Tier-B sub-type supporting lit (T#43 de Silva-Lim 2008 + 2024-2026 follow-on)

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** Survey LimitWitness Tier-B sub-type supporting lit (T#43 de Silva-Lim 2008 + 2024-2026 follow-on)

**Why this verification matters:** Tier-B sub-type for ill-posedness; need de Silva-Lim 2008 + 2024-2026 follow-on on stable substitutes (Tucker/HT/symmetric/orthogonal where existence holds)

**Downstream consumer:** LimitWitness Tier-B sub-type registration; cross-link to GenericityAlmostEverywhereCert composition

**Tags / context:** tensor, limit-witness, ill-posed, tier-B, T#43

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 14: DR-031 — Survey WaringRankWitness Tier-B sub-type supporting lit (T#22 Shitov 2021 perm_3=16)

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** Survey WaringRankWitness Tier-B sub-type supporting lit (T#22 Shitov 2021 perm_3=16)

**Why this verification matters:** Det/perm tooling asymmetry HARD-3 surface; need primary lit on R_W(perm_3)=16 + R_W(perm_n) status n>=4 + symmetric-flattening lower bound constructions

**Downstream consumer:** WaringRankWitness Tier-B sub-type registration; det/perm asymmetry HARD-3 documentation

**Tags / context:** tensor, waring, permanent, tier-B, T#22, HARD-3

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 15: DR-032 — Survey ReshapingCertificate + MeasureZeroExceptionAnnotation supporting lit (T#40 AOP/CO-V)

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** Survey ReshapingCertificate + MeasureZeroExceptionAnnotation supporting lit (T#40 AOP/CO-V)

**Why this verification matters:** Tier-B cross-cutting sub-primitives required for substrate-tester fire #45 cross-tier composition pattern; need primary lit on AOP/CO-V exception list (6,2,9), (4,3,8), (3,5,9)

**Downstream consumer:** ReshapingCertificate + MeasureZeroExceptionAnnotation Tier-B sub-types registration; T-ST-fire45-001 probe spec

**Tags / context:** tensor, cp-identifiability, tier-B, tier-D, T#40

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 16: DR-033 — Survey PhaseTransitionThreshold + AlgorithmThresholdCert + GenericityAlmostEverywhereCert (T#73) supporting lit

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** Survey PhaseTransitionThreshold + AlgorithmThresholdCert + GenericityAlmostEverywhereCert (T#73) supporting lit

**Why this verification matters:** Tier-D triple composition (substrate-tester fire #43); need explicit lit on Tensor PCA threshold (Hopkins 2018, Wein-El Alaoui-Moore, 2024-2026) + NSGA + Kikuchi algorithmic matchers

**Downstream consumer:** Tier-D triple primitive registration; T-ST-fire43-001 probe spec; AA-023 cross-link

**Tags / context:** tensor, tensor-pca, tier-D, T#73

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 17: DR-034 — Survey OrbitClosureNonMembershipWitness + AlgebraicNaturalProofsBarrier supporting lit (T#92)

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** Survey OrbitClosureNonMembershipWitness + AlgebraicNaturalProofsBarrier supporting lit (T#92)

**Why this verification matters:** Tier-B parent + Tier-D meta-warning for GCT-style obstructions; need Forbes-Shpilka-Volk barrier check primary lit + post-BIP non-occurrence sub-type lit

**Downstream consumer:** OrbitClosureNonMembershipWitness Tier-B + AlgebraicNaturalProofsBarrier Tier-D registration; T-ST-T92 probe spec cluster

**Tags / context:** tensor, gct, orbit-closure, natural-proofs, tier-B, tier-D, T#92

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 18: DR-035 — Survey Structured-Equivalence-Class meta-primitive supporting lit (T#79 SLOCC 2025 AME-at-n=5)

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** Survey Structured-Equivalence-Class meta-primitive supporting lit (T#79 SLOCC 2025 AME-at-n=5)

**Why this verification matters:** Meta-primitive unifying OrbitWitness + HomotopyWitness + ArityGradedOperationFamily; need primary lit on AME-at-n=5 result + 2024-2026 SLOCC classification status

**Downstream consumer:** Structured-Equivalence-Class Tier-E meta-primitive registration; P03 R-GIT-product sub-tactic

**Tags / context:** tensor, slocc, meta-primitive, tier-E, T#79

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 19: DR-036 — Survey RayClassFieldFiducial + StarkUnitWitness supporting lit (T#85 AFK 2025)

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** Survey RayClassFieldFiducial + StarkUnitWitness supporting lit (T#85 AFK 2025)

**Why this verification matters:** Conditional anchors required by AFK 2025 Zauner construction; need primary lit on Stark conjectures + Shintani-Faddeev modularity status + conditional-vs-unconditional flag schema

**Downstream consumer:** RayClassFieldFiducial + StarkUnitWitness Tier-E registration; conditional flag schema for any future Stark-dependent primitive

**Tags / context:** tensor, zauner, stark, tier-E, T#85

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 20: DR-037 — Survey RepresentationTheoreticInvariant + KroneckerInvariant + PartitionObject Tier-E parents (T#95)

```
Project Prometheus is a multi-agent mathematical research substrate. We operate under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be publishable" or "for our paper" — Prometheus is not in publication mode. Findings are substrate inputs (anti-anchor pins, primitive registrations, catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional framings. Resist them. When mathematical literature exhibits gravity wells (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones. Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct invariants into a single named field. Examples: tensor rank vs border rank vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs partition rank vs geometric rank are SEVEN distinct coordinates, not one "rank." Determinantal complexity dc vs border determinantal dc-bar vs formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the downstream consumer (anti-anchor pin, primitive registration, catalog edit, work-queue entry) where possible.

Now to the actual prompt.

---

## Task: anti-anchor verification

Verify the following anti-anchor candidate against primary literature.

**Candidate:** Survey RepresentationTheoreticInvariant + KroneckerInvariant + PartitionObject Tier-E parents (T#95)

**Why this verification matters:** Tier-E parent class shared with T#92; need primary lit on Kronecker positivity NP-hardness (Ikenmeyer-Mulmuley-Walter) + Saxl cube anchor + partition-object schema

**Downstream consumer:** Tier-E parent class registration; prerequisite for GCTObstructionCertificate composite

**Tags / context:** tensor, kronecker, saxl, tier-E, T#95

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

