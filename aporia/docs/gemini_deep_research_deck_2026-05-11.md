# Gemini Deep Research Deck — 2026-05-11

**Auto-generated** from `queue.jsonl` (20 entries, tier=1).

Fire via:
```
python aporia/scripts/gemini_deep_research_dispatch.py \
    --deck gemini_deep_research_deck_2026-05-11.md \
    --out aporia/docs/deep_research_batch_2026-05-11 \
    --batch-size 3 --resume
```

---

### Prompt 1: DR-001 — Verify AA-013 Strassen direct-sum R<=7 safe zone (Rupniewski 2024)

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

**Candidate:** Verify AA-013 Strassen direct-sum R<=7 safe zone (Rupniewski 2024)

**Why this verification matters:** Synthesis 2026-05-11 §3 flagged AA-013 needs primary-source pin on exact rank-7 bound + C^k tensor C^3 C^3 regime; current cite is secondary; substrate must reject 'additivity holds' outside safe zone

**Downstream consumer:** AA-013 register in techne/registry/anti_anchors.jsonl with verified_against_primary=true; T#6/T#23 catalog edit propagate

**Tags / context:** tensor, border-rank, additivity, AA-013, T#6, T#23

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 2: DR-002 — Verify AA-014 Border Comon's distinct from standard Comon's (Manziuk-Ventura 2024)

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

**Candidate:** Verify AA-014 Border Comon's distinct from standard Comon's (Manziuk-Ventura 2024)

**Why this verification matters:** AA-014 medium-high risk; Standard Comon's killed by Shitov 2018 but Border Comon's TRUE for n<=d+1, tame, sharp; substrate must NOT collapse the two

**Downstream consumer:** AA-014 register; RankZooSignature primitive cross-coord separation; MinimalBorderRankComonWitness Tier-B sub-type spec

**Tags / context:** tensor, border-rank, comon, AA-014, T#20

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 3: DR-003 — Verify AA-015 Bell-number det bound NOT applicable to permanent (HGJ 2024)

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

**Candidate:** Verify AA-015 Bell-number det bound NOT applicable to permanent (HGJ 2024)

**Why this verification matters:** Houston-Goucher-Johnston 2024 R(det_n)<=B_n is alternating-sign-specific; substrate must reject Bell-number permanent upper bound in char 0; cross-confirms det/perm tooling asymmetry HARD-3 finding

**Downstream consumer:** AA-015 register; PermanentNonExistenceCert outside-tier primitive; T#86 catalog edit

**Tags / context:** tensor, det-perm, bell-number, AA-015, T#86, HARD-3

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 4: DR-004 — Verify AA-016 BBvH free-probability matrix-only NOT tensor (Aden-Ali 2025)

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

**Candidate:** Verify AA-016 BBvH free-probability matrix-only NOT tensor (Aden-Ali 2025)

**Why this verification matters:** HIGH risk; BBvH 2024 Inventiones eliminates log-d for r=2 only; tensor r>=3 needs PAC-Bayesian or generic-chaining; cross-tier dimensional confusion failure mode

**Downstream consumer:** AA-016 register; RandomTensorConcentrationCert.PACBayesian Tier-D sub-type; T#71 catalog edit

**Tags / context:** tensor, operator-norm, free-probability, AA-016, T#71, T#72

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 5: DR-005 — Verify AA-017 Lackenby quasi-poly unknot pre-publication status

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

**Candidate:** Verify AA-017 Lackenby quasi-poly unknot pre-publication status

**Why this verification matters:** Medium-high risk forward false-anchor of AA-004 shape; Lackenby 2021 announcement may have entered LLM training as 'proved' but peer-review status unclear as of late 2025; check status as of today

**Downstream consumer:** AA-017 register with ANNOUNCED-NOT-PUBLISHED annotation; KnotInvariantBundle Tier-F primitive complexity field; Ergon knot calibration battery

**Tags / context:** knots, unknot, complexity, AA-017

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 6: DR-006 — Verify AA-018 Khovanov girth (not crossing count) governs tractability

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

**Candidate:** Verify AA-018 Khovanov girth (not crossing count) governs tractability

**Why this verification matters:** Medium risk HARD-5 / PATTERN_RANK_PARITY_LEAK at diagram-complexity layer; girth not crossing count controls Khovanov compute; substrate must store girth as first-class metadata

**Downstream consumer:** AA-018 register; KnotInvariantBundle.girth mandatory field; KnotJob/Regina ingestion pipeline schema

**Tags / context:** knots, khovanov, girth, AA-018, HARD-5

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 7: DR-007 — Verify AA-019 LMFDB GL(3) root number ML-predicted vs analytically proven

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

**Candidate:** Verify AA-019 LMFDB GL(3) root number ML-predicted vs analytically proven

**Why this verification matters:** MOST operationally-significant Wave-3 anti-anchor; Ergon's maass_gl3_gap_scan.py actively consumes LMFDB and risks inheriting ML hallucinations if no proven/predicted split

**Downstream consumer:** AA-019 register; MaassGL3SpectralBundle.RootNumber mandatory enum (ANALYTICALLY_PROVEN | ML_PREDICTED_VIA_MURMURATION); maass_gl3_gap_scan.py partition

**Tags / context:** maass, gl3, lmfdb, murmuration, AA-019, ergon

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 8: DR-008 — Verify AA-020 BCGP 2025 modularity proportion NOT all abelian surfaces

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

**Candidate:** Verify AA-020 BCGP 2025 modularity proportion NOT all abelian surfaces

**Why this verification matters:** Medium-high risk forward false-anchor of AA-002 (Zauner conditional) shape; BCGP 2025 proves potential modularity in general + unconditional for ~11384 LMFDB curves with good ord red at 3 + 3-distinguished big image; substrate must NOT propagate 'all modular'

**Downstream consumer:** AA-020 register with conditional/unconditional split; AbelianSurfaceArithmeticBundle.modularity_conditional_or_unconditional enum; Ergon genus-2 calibration battery

**Tags / context:** genus-2, abelian-surface, modularity, AA-020, BCGP

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 9: DR-009 — Verify AA-021 AlphaTensor 4x4 over F_2 ONLY (not C); AlphaEvolve is the C result

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

**Candidate:** Verify AA-021 AlphaTensor 4x4 over F_2 ONLY (not C); AlphaEvolve is the C result

**Why this verification matters:** HIGH risk; mainstream press conflates AlphaTensor 2022 F_2 rank-47 with AlphaEvolve 2025 C rank-48; substrate must distinguish field of definition + system

**Downstream consumer:** AA-021 register; AlgorithmEvolutionaryLoop Tier-G primitive field-of-definition field; T#1 catalog edit cross-link

**Tags / context:** method, alphaevolve, alphatensor, matrix-mult, AA-021, T#1

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 10: DR-010 — Verify AA-022 AlphaEvolve meta-discovery (evolve search algo) NOT direct tensor search

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

**Candidate:** Verify AA-022 AlphaEvolve meta-discovery (evolve search algo) NOT direct tensor search

**Why this verification matters:** Medium risk HARD-2 anti-gravity-well; AlphaEvolve evolves PyTorch/JAX optimizer code via LLM mutator, not tensor space directly; substrate must register as MetaDiscoveryAlgorithmSynthesis

**Downstream consumer:** AA-022 register; P32_EvolutionaryLLMSynthesis paradigm sub-tactic MetaSearchAlgorithmSynthesis

**Tags / context:** method, alphaevolve, meta-discovery, AA-022, P32

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 11: DR-011 — Verify AA-023 SoS hierarchy not algorithmic upper bound for Tensor PCA

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

**Candidate:** Verify AA-023 SoS hierarchy not algorithmic upper bound for Tensor PCA

**Why this verification matters:** Medium risk HARD-2; Ding-Gu-Liu-Fang 2025 NSGA and Li 2025 Kikuchi both match SoS threshold without SDP overhead; substrate must NOT collapse 'SoS proves the limit' with 'SoS is the only algorithm at limit'

**Downstream consumer:** AA-023 register; SoSCertificate Tier-G theoretical_only vs executable annotation; T#73 catalog edit

**Tags / context:** method, sos, tensor-pca, AA-023, T#73, HARD-2

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 12: DR-012 — Re-verify AA-001 GCT_OCCURRENCE_DEAD against 2026 follow-on (BIP 2019)

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

**Candidate:** Re-verify AA-001 GCT_OCCURRENCE_DEAD against 2026 follow-on (BIP 2019)

**Why this verification matters:** 90-120 day re-verification cadence; AA-001 last verified 2026-05-11; check 2026 follow-on attempts to revive occurrence obstructions or extensions to non-padded perm

**Downstream consumer:** AA-001 last_verified update; GCTObstructionCertificate.OccurrenceObstruction KILLED status confirmed

**Tags / context:** tensor, gct, anti-anchor, AA-001, T#92, re-verify

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 13: DR-013 — Re-verify AA-002 ZAUNER_FALSE_ANCHOR against 2026 follow-on (AFK 2025)

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

**Candidate:** Re-verify AA-002 ZAUNER_FALSE_ANCHOR against 2026 follow-on (AFK 2025)

**Why this verification matters:** Re-verification; check whether AFK Stark+Shintani-Faddeev conditionality has been weakened or strengthened in 2026 follow-ons; status of Stark conjecture special cases

**Downstream consumer:** AA-002 last_verified update; RayClassFieldFiducial/StarkUnitWitness Tier-E primitive conditionality annotation refresh

**Tags / context:** tensor, zauner, sic-povm, stark, AA-002, T#85, re-verify

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 14: DR-014 — Re-verify AA-003 HILLAR_LIM_SYMRANK_Q_RESOLVED + AA-012 tensor-rank-over-Z undecidable

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

**Candidate:** Re-verify AA-003 HILLAR_LIM_SYMRANK_Q_RESOLVED + AA-012 tensor-rank-over-Z undecidable

**Why this verification matters:** Re-verification; check whether Shitov 2016 arXiv:1611.01559 result has been extended or has new symmetric-Waring corollaries 2024-2026; AA-003 + AA-012 share citation, verify together

**Downstream consumer:** AA-003, AA-012 last_verified update; ComputationalComplexityCertificate.UndecidableClass refresh

**Tags / context:** tensor, complexity, shitov, AA-003, AA-012, T#56, re-verify

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 15: DR-015 — Re-verify AA-004 SAXL_T99_FALSELY_RESOLVED + AA-011 SAXL_CUBE_ANCHOR

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

**Candidate:** Re-verify AA-004 SAXL_T99_FALSELY_RESOLVED + AA-011 SAXL_CUBE_ANCHOR

**Why this verification matters:** Saxl was inverted 2026-05-11; high LLM-attribution-risk anchor; re-verify in 90 days whether Lee 2025 has been resubmitted, whether independent attempts have appeared, whether cube proof has been extended

**Downstream consumer:** AA-004, AA-011 last_verified update; RepresentationTheoreticInvariant/KroneckerInvariant primitive refresh; T#99 catalog edit refresh

**Tags / context:** tensor, saxl, kronecker, AA-004, AA-011, T#99, re-verify

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 16: DR-016 — Re-verify AA-005 CACTUS_BARRIER_6M_MINUS_4 (Buczynski Feb 2026)

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

**Candidate:** Re-verify AA-005 CACTUS_BARRIER_6M_MINUS_4 (Buczynski Feb 2026)

**Why this verification matters:** Re-verification; check whether the 6m-4 bound has been refined by 2026 follow-on work or extended to non-determinantal LBs

**Downstream consumer:** AA-005 last_verified update; CactusRankWitness primitive auto-flagging threshold refresh

**Tags / context:** tensor, cactus, border-rank, AA-005, T#19, re-verify

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 17: DR-017 — Re-verify AA-006 LUCCA_ATTRIBUTION + AA-007 TENSOR_TYPE2_NOT_SQRT_LOG_D + AA-010 type-2 five-region rarity

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

**Candidate:** Re-verify AA-006 LUCCA_ATTRIBUTION + AA-007 TENSOR_TYPE2_NOT_SQRT_LOG_D + AA-010 type-2 five-region rarity

**Why this verification matters:** Joint re-verification; all three pin same arXiv:2603.29571 + 2411.10633 result cluster; 90-day cadence; check whether Lucca has new papers, type-2 frontier movement

**Downstream consumer:** AA-006, AA-007, AA-010 last_verified update; RandomTensorConcentrationCert refresh

**Tags / context:** tensor, type-2, operator-norm, AA-006, AA-007, AA-010, T#72, re-verify

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 18: DR-018 — Re-verify AA-008 EQUIVARIANT_EXPONENTIAL_RESTRICTED (Landsberg-Ressayre 2017)

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

**Candidate:** Re-verify AA-008 EQUIVARIANT_EXPONENTIAL_RESTRICTED (Landsberg-Ressayre 2017)

**Why this verification matters:** Re-verification; check whether the restricted-model dc(perm) exponential bound has been extended beyond equivariant model 2018-2026

**Downstream consumer:** AA-008 last_verified update; EquivariantComplexityCertificate restricted_to annotation refresh

**Tags / context:** tensor, gct, permanent, equivariant, AA-008, T#92, re-verify

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 19: DR-019 — Re-verify AA-009 BORDER_CACTUS_DISTINCT_FIFTH_RANK (Buczynska-Buczynski Jan 2026)

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

**Candidate:** Re-verify AA-009 BORDER_CACTUS_DISTINCT_FIFTH_RANK (Buczynska-Buczynski Jan 2026)

**Why this verification matters:** Re-verification; check whether border-cactus literature has expanded the fifth-rank invariant class or introduced a sixth

**Downstream consumer:** AA-009 last_verified update; RankZooSignature primitive Tier-A++ field-set refresh

**Tags / context:** tensor, rank-zoo, cactus, AA-009, T#19, re-verify

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```

### Prompt 20: DR-020 — VERIFY-LIVE T#6 Rupniewski 2024 small-tensor additivity safe zone exact bound

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

**Candidate:** VERIFY-LIVE T#6 Rupniewski 2024 small-tensor additivity safe zone exact bound

**Why this verification matters:** Synthesis 2026-05-11 §2 catalog table flagged T#6 as [VERIFY-LIVE]; exact R<=7 bound cited in two reports but needs primary-source pin before substrate-canonical safe-zone registration

**Downstream consumer:** T#6 catalog edit propagate; SmallTensorAdditivitySafeZone Tier-B sub-type registration unblocked

**Tags / context:** tensor, additivity, catalog, T#6, T#23, VERIFY-LIVE

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.

```
