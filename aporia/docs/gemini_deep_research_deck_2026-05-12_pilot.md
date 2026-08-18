# Gemini Deep Research Deck — 2026-05-12 (Substrate-Shaped Pilot)

**3 substrate-shaped variants for the pilot fire** + 17 standard tier-1 entries via `burn_research_tokens.py`. Pilot entries are DR-001 and DR-007 (both have narrative-only baselines from 2026-05-11 batch at `aporia/docs/deep_research_batch_2026-05-11/01_*.md` and `07_*.md` for A/B comparison) plus DR-231 (Tier-3 Jones polynomial — fresh fire, exercises both `training_anchor` and `paradigm_candidate` schemas).

**Pilot success criteria** (from `techne/PROMPT_2026-05-11_substrate_first.md`):
- ≥80% of substrate blocks emitted pass arXiv-verify + jsonschema validation → migrate all 4 templates
- 50-80% block validity → schemas need refinement before full migration; iterate
- <50% validity OR no reviewer-time savings → revert; keep arXiv-verify as standalone audit

**Fire mechanism:** manual append for these 3 pilot entries; defer `build_deck_from_queue.py` modification until pilot evidence justifies. Fire via standard dispatcher:
```
python aporia/scripts/gemini_deep_research_dispatch.py \
    --deck aporia/docs/gemini_deep_research_deck_2026-05-12_pilot.md \
    --out aporia/docs/deep_research_batch_2026-05-12_pilot \
    --batch-size 3 --resume
```

**Post-fire validation:**
```
python aporia/scripts/parse_substrate_blocks.py --batch-dir aporia/docs/deep_research_batch_2026-05-12_pilot
python aporia/scripts/validate_substrate_blocks.py --staged-dir aporia/docs/staged_substrate_blocks/2026-05-12
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

## Tracking after fire

After the 3 pilot prompts return:

1. Save reports to `aporia/docs/deep_research_batch_2026-05-12_pilot/`.
2. Run `parse_substrate_blocks.py` on the batch dir.
3. Run `validate_substrate_blocks.py` on the staged blocks.
4. Compare validation pass rate vs the design's 80% target.
5. Compare reviewer time-to-decision vs narrative-only baseline (DR-001 baseline at `01_verify_aa_013_*.md` and DR-007 baseline at `07_verify_aa_019_*.md` in `deep_research_batch_2026-05-11/`).
6. File T-2026-05-12-aporia-to-techne-pilot-result with the empirical metrics back to Techne for migration decision.

Pilot success → migrate all 4 tier templates; build ingest_substrate_blocks.py. Pilot failure → revert to narrative-only + arXiv-verify standalone audit.
