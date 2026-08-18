# Gemini Deep Research Deck — 2026-05-14

**Composition:** 2 Atlas-direction pilot prompts + 3 substrate-shaped pilot prompts + 15 standard queue entries (tier mix 6/5/3/1).

Atlas-direction pilots test the Problem Atlas Deep-Research strategy shift proposed in pivot/arena_problem_atlas_sandbox_vision_2026-05-14.md — solved-problem technique extraction and unsolved-problem hardness classification. Small-scale pilot; if structured YAML output is usable, scale up. If not, redirect tokens.

Substrate-shaped pilots target new corners: P vs NP barriers landscape (3 anti-anchor candidates), LMFDB EC rank trust-tier (companion to AA-019 mitigation pattern), BCGP 2025 modularity status (primitive_proposal yield expected).

Standard queue picks: top-6 unfired Tier-1 (anti-anchor verifications + primitive supporting lit), top-5 unfired Tier-2 (T#NN tensor catalog continuation), top-3 unfired Tier-3 (3-manifold census + Volume Conjecture), top-1 unfired Tier-4 (AlphaProof methodology forensics).

Fire:
```
python aporia/scripts/gemini_deep_research_dispatch.py \
    --deck aporia/docs/gemini_deep_research_deck_2026-05-14.md \
    --out aporia/docs/deep_research_batch_2026-05-14 \
    --batch-size 3 --resume
```

After return:
```
python aporia/scripts/parse_substrate_blocks.py --batch-dir aporia/docs/deep_research_batch_2026-05-14
python aporia/scripts/validate_substrate_blocks.py --staged-dir aporia/docs/staged_substrate_blocks/2026-05-14
python aporia/scripts/burn_research_tokens.py --log-only --batch-dir aporia/docs/deep_research_batch_2026-05-14
```

---

### Prompt 1: DR-A001 — Solved-problem technique extraction (Atlas seed, 10 problems) [ATLAS-PILOT]

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

## Task: PROBLEM-ATLAS PILOT — solved-problem technique extraction (Atlas seed)

This is a meta-research prompt. We are testing whether Gemini Deep Research can produce structured technique-to-hardness mappings for the Prometheus Problem Atlas (Layer 5.5 substrate architecture, see pivot/arena_problem_atlas_sandbox_vision_2026-05-14.md). Pilot scale: 10 problems. If this works, we scale.

For each of the following 10 mathematical problems that were SOLVED (i.e. definitively settled with a peer-reviewed proof) between 2010 and 2025, extract:

1. **Sensitivity Conjecture** (Huang 2019)
2. **Bounded Gaps Between Primes** (Zhang 2013 / Maynard 2013-15)
3. **Erdős Discrepancy Problem** (Tao 2015)
4. **Cap Set Problem polynomial-method breakthrough** (Croot-Lev-Pach / Ellenberg-Gijswijt 2016)
5. **Kadison-Singer Problem** (Marcus-Spielman-Srivastava 2013)
6. **Willmore Conjecture** (Marques-Neves 2012)
7. **Virtual Haken Conjecture** (Agol 2012)
8. **Schinzel-Zassenhaus Conjecture** (Dimitrov 2019/2021)
9. **Duffin-Schaeffer Conjecture** (Koukoulopoulos-Maynard 2019)
10. **Erdős Sum-Product Conjecture progress** (Rudnev-Stevens 2020 etc — characterize current best status)

For EACH problem, provide:

**(a) THE TECHNIQUE THAT CLOSED THE METHOD GAP.** Name the specific mathematical technique or new framework that made the proof possible. Be specific: "polynomial method via Croot-Lev-Pach finite-field interpolation" is more useful than "polynomial method."

**(b) HARDNESS TYPE PRIMARILY ADDRESSED.** Classify per the 8-dimension Prometheus hardness taxonomy: METHOD_GAP (existing tools almost work, fail at boundary) / REPRESENTATION_GAP (right coordinate system not found) / GLOBAL_OBSTRUCTION (local-OK, global-fails) / EXACTNESS_BARRIER (approximate evidence insufficient) / HIDDEN_PATHOLOGY (counterexamples rare/huge) / COUPLED_DIFFICULTY (multiple fused barriers) / NON_HEREDITARY_STRUCTURE (simplification destroys phenomenon) / CONCEPTUAL_ABSENCE (needed object not yet invented). Pick the dominant type; if multi-type, list primary + secondary.

**(c) NEW MACHINERY INVENTED OR REPURPOSED.** What mathematical object, technique, or framework was newly invented or substantially repurposed for this proof? Distinguish "invented for this proof" from "existing technique applied in novel way."

**(d) PRIMARY SOURCE CITATION.** arXiv ID, journal reference, exact date of definitive publication. Distinguish preprint from peer-reviewed.

**(e) PRECURSOR DEPENDENCIES.** What earlier results / concepts had to be established before this proof became possible? Name 1-3 dependencies per problem.

Output format: structured Markdown with one ### subsection per problem, followed by a YAML appendix block tagged as substrate_block type `atlas_seed_entry` (this is a NEW block type we are piloting; emit even though it isn't in the existing schema registry — Aporia will adjudicate the schema after seeing the data).

```yaml
# substrate_block: atlas_seed_entry
- _schema_version: "atlas_seed/0.1.0"
  problem_id: "sensitivity_conjecture"
  problem_status: "solved"
  year_settled: 2019
  primary_technique: "..."
  hardness_type_primary: "METHOD_GAP"
  hardness_type_secondary: null
  machinery_invented_or_repurposed: "..."
  primary_citation: "arXiv:XXXX.XXXXX"
  citation_status: "peer_reviewed"
  precursor_dependencies: ["...", "...", "..."]
  notes: "..."
```

Length: 3000-5000 words narrative + YAML appendix.
```

---

### Prompt 2: DR-A002 — Unsolved-problem hardness classification (Atlas seed, 5 problems) [ATLAS-PILOT]

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

## Task: PROBLEM-ATLAS PILOT — unsolved-problem hardness classification (Atlas seed)

Companion to the solved-problem-technique-extraction prompt. We are testing the inverse direction: can structured hardness signatures be produced for currently-unsolved problems? Pilot scale: 5 problems.

For each of the following 5 currently-UNSOLVED problems, provide:

1. **Riemann Hypothesis**
2. **Goldbach Conjecture**
3. **P vs NP**
4. **Hodge Conjecture**
5. **Birch and Swinnerton-Dyer Conjecture**

For EACH problem, provide:

**(a) HARDNESS SIGNATURE — weighted vector over the 8 dimensions.** Give each dimension a weight in [0.0, 1.0] indicating how much that hardness type contributes to the problem's overall hardness (need not sum to 1; multiple can be high). Also give a confidence_per_dimension value (high / medium / low) reflecting how settled the literature is on that dimension. The 8 dimensions: METHOD_GAP / REPRESENTATION_GAP / GLOBAL_OBSTRUCTION / EXACTNESS_BARRIER / HIDDEN_PATHOLOGY / COUPLED_DIFFICULTY / NON_HEREDITARY_STRUCTURE / CONCEPTUAL_ABSENCE.

**(b) MOST RECENT DOCUMENTED METHODOLOGICAL NEAR-MISS.** What's the most recent (2020-2026) published partial result, almost-proof, or methodological advance that touches this problem? Cite specifically. Example: "Selberg's zero-density estimate has been improved to Y by author X in 2024 (arXiv:...), still falls short of RH-implying threshold Z."

**(c) PRECURSOR CONCEPTS / THEOREMS NEEDED.** Name 1-3 concepts or theorems that would need to be established before the problem becomes tractable. Distinguish "established but underexplored" from "not yet invented." For example: for RH, "growth bounds on Dirichlet L-functions in the t-aspect" is established-but-tight; "explicit non-trivial zero classification" is not yet a framework.

**(d) PRIMARY SOURCE CITATIONS.** For each near-miss claim, give arXiv ID, journal reference, and exact date. Distinguish ANNOUNCED-NOT-PUBLISHED from PEER-REVIEWED. Distinguish CONDITIONAL from UNCONDITIONAL.

**(e) CANDIDATE REFRAMINGS.** Has anyone proposed a non-standard representation of this problem that might shift the hardness signature (e.g. RH as a Hilbert-Polya operator-theoretic question; P vs NP as a GCT representation-theoretic question)? Name 1-2 candidate reframings per problem and the dominant hardness signature each reframing would target.

Output format: structured Markdown with one ### subsection per problem, followed by YAML appendix as `atlas_seed_open_problem_card`.

```yaml
# substrate_block: atlas_seed_open_problem_card
- _schema_version: "atlas_seed/0.1.0"
  problem_id: "riemann_hypothesis"
  problem_status: "open"
  hardness_signature:
    METHOD_GAP: {weight: 0.0, confidence: "high"}
    REPRESENTATION_GAP: {weight: 0.0, confidence: "medium"}
    GLOBAL_OBSTRUCTION: {weight: 0.0, confidence: "medium"}
    EXACTNESS_BARRIER: {weight: 0.0, confidence: "high"}
    HIDDEN_PATHOLOGY: {weight: 0.0, confidence: "low"}
    COUPLED_DIFFICULTY: {weight: 0.0, confidence: "medium"}
    NON_HEREDITARY_STRUCTURE: {weight: 0.0, confidence: "medium"}
    CONCEPTUAL_ABSENCE: {weight: 0.0, confidence: "low"}
  most_recent_near_miss:
    description: "..."
    citation: "arXiv:XXXX.XXXXX"
    citation_date: "2024-MM-DD"
    citation_status: "peer_reviewed"
  precursor_concepts:
    - status: "established_but_tight"
      description: "..."
    - status: "not_yet_invented"
      description: "..."
  candidate_reframings:
    - name: "Hilbert-Polya operator-theoretic"
      shifts_hardness_to: "REPRESENTATION_GAP"
      citation: "..."
```

Length: 3000-5000 words narrative + YAML appendix.
```

---

### Prompt 3: DR-S001 — P vs NP barriers landscape (relativization / natural-proofs / algebrization) [SUBSTRATE-SHAPED]

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

## Task: SUBSTRATE-SHAPED PILOT — P vs NP barriers landscape

Verify the current state of three barrier results in the P vs NP problem complex. We are NOT asking for progress on P vs NP itself. We are asking for primary-source pins on the barriers that constrain proof attempts.

**Targets:**

1. **Relativization barrier** (Baker-Gill-Solovay 1975). Verify the modern formulation. Survey any 2024-2026 work that strengthens, weakens, or reframes the relativization barrier in light of randomized / algebraic models.

2. **Natural proofs barrier** (Razborov-Rudich 1997). Verify state. Survey Forbes-Shpilka-Volk algebraic-natural-proofs work and Grochow-Kumar-Saks-Saraf 2017. Distinguish what's PROVEN (the standard combinatorial natural-proofs barrier) from what's CONJECTURAL (algebraic-natural-proofs gives full Razborov-Rudich strength in the algebraic setting).

3. **Algebrization barrier** (Aaronson-Wigderson 2008). Verify state and any 2024-2026 follow-on.

For each barrier:

**(a) PRIMARY SOURCE.** Original publication, arXiv/journal/date. Modern restatement (2020+) if one exists.

**(b) WHAT IT FORBIDS.** Specifically: which proof techniques are ruled out, and which are NOT ruled out.

**(c) RECENT WORK.** 2020-2026 papers that strengthen, weaken, or reframe.

**(d) ANTI-ANCHOR CANDIDATES.** What false claims about these barriers circulate in the literature or in LLM training data? Examples to test: "natural proofs barrier rules out all known lower bound techniques" (FALSE — only those satisfying constructivity + largeness); "GCT bypasses natural proofs" (PARTIALLY TRUE — bypasses the constructivity criterion, but unclear on largeness); etc.

## SUBSTRATE BLOCK APPENDIX (REQUIRED)

Emit fenced YAML blocks at end of report. Schemas at techne/contracts/substrate_block_schemas/.

1. **3 anti_anchor blocks** — one per barrier, each pinning a common false form vs the verified true form. Required fields: _schema_version "1.0.0", id (AA-NNN-CANDIDATE format, since these are new candidates not registered yet — use AA-PNP-RELAT, AA-PNP-NATURAL, AA-PNP-ALGEBRIZE), name (UPPER_SNAKE_CASE, avoid bare-noun coordinate words), false_form, true_form (min 60 chars), citation (arXiv/DOI), citation_status, risk_tier, source_report, verified_against_primary.

2. **1 paradigm_candidate block** for the algebraic-natural-proofs barrier as a methodology (Forbes-Shpilka-Volk lineage). Fields: _schema_version, id (P-NEW-XXX), name, category (methodology), consumes, produces, status (load-bearing | candidate | retracted), source.

3. **Optional catalog_edit blocks** for T#92 (GCT VP vs VNP) if survey turns up a status update.

Length: 2500-4000 words narrative + substrate blocks.
```

---

### Prompt 4: DR-S002 — LMFDB EC rank ml_predicted vs numerically_certified split [SUBSTRATE-SHAPED]

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

## Task: SUBSTRATE-SHAPED PILOT — LMFDB elliptic curve rank: ml_predicted vs numerically_certified split

OPERATIONAL URGENCY: Ergon's training corpus discipline (AA-019 mitigation pattern, already in registry) requires explicit trust-tier annotation for any LMFDB data that may be ML-predicted rather than analytically certified. We need the equivalent of AA-019 for elliptic curves.

**Question:** For LMFDB elliptic curve entries, what fraction of rank values are:
- (a) ANALYTICALLY_PROVEN (descent + Selmer + 2-isogeny machinery; rigorous BSD proxies)
- (b) NUMERICALLY_CERTIFIED (interval arithmetic + Heegner point computation; high-precision but not symbolic proof)
- (c) ML_PREDICTED (neural / mumblings-style predictions, e.g. recent murmurations work on EC rank)
- (d) HEURISTIC_ONLY (Goldfeld-style conjecture-driven; no formal certification)

Specifically:

**(a) PRIMARY SOURCE CONFIRMATION.** What does LMFDB documentation say about rank-provenance? Cite the LMFDB "About" pages or peer-reviewed papers describing the methodology. Confirm or refute the existence of an ml_predicted subset.

**(b) RECENT WORK (2022-2026).** Survey ML-prediction-of-rank work (He-Lee-Oliver style murmurations applied to EC rank; LMFDB integration work; any planned merge into LMFDB-as-canonical).

**(c) FALSE-FORM RECURRENCE.** Are LLM training corpora likely to treat "LMFDB rank field = analytically proven rank" as an unqualified true claim? Survey corpora / textbook treatments.

**(d) RECOMMENDATION.** Should the substrate register AA-EC-RANK-TRUST-TIER as a new anti-anchor? If yes, propose the false_form / true_form pair.

## SUBSTRATE BLOCK APPENDIX (REQUIRED)

1. **1 anti_anchor block** for EC rank trust-tier (AA-EC-RANK-TRUST candidate).

2. **2 training_anchor blocks** — one for the analytically-proven subset of LMFDB EC rank data (anchor-ec_rank-001, trust_tier=analytically_proven), one for the numerically_certified subset (anchor-ec_rank-002, trust_tier=numerically_certified). Required fields per schema: _schema_version "1.0.0", id, domain ("elliptic_curve"), anchor_type ("invariant_value"), dataset_source, scale (object with instance_count and coverage_qualifier), prompt_template, expected_answer_shape, verification_method (analytical_proof | computational_certified | ml_prediction | folklore), trust_tier, source, source_date (ISO YYYY-MM-DD), caveats.

3. **Optional 1 catalog_edit block** if survey surfaces a status update for the EC rank distribution claim.

Length: 2500-4000 words narrative + substrate blocks.
```

---

### Prompt 5: DR-S003 — Genus-2 modularity 2025 status (BCGP + follow-on) [SUBSTRATE-SHAPED]

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

## Task: SUBSTRATE-SHAPED PILOT — Genus-2 modularity 2025 status (BCGP + follow-on)

The BCGP 2025 result (Boxer-Calegari-Gee-Pilloni) on abelian surface modularity has reshaped genus-2 / abelian-surface landscape. We need a substrate-shaped verification of what's actually proven vs conjectural, with primitive-proposal yield expected.

**Targets:**

(a) BCGP 2025 modularity result — what's the EXACT theorem statement? What restrictions apply (ordinarity, K_S-cohomology, abelian surface vs general genus-2, etc)? Cite the published version (2025-2026) distinguishing from the 2023-2024 announcement.

(b) Subsequent work — Calegari + collaborators, Sutherland's LMFDB-genus-2 integration, any 2025-2026 strengthening of BCGP. What's the current ANNOUNCED-NOT-PUBLISHED state?

(c) Anti-anchor surface: what false forms of the BCGP statement circulate? Examples to test: "all abelian surfaces over Q are modular" (FALSE — restriction on K_S structure); "BCGP proves genus-2 BSD" (FALSE — modularity, not BSD); "BCGP requires GRH" (FALSE — unconditional within its scope).

(d) Primitive proposal: what new mathematical machinery does BCGP introduce or repurpose that should register as a Prometheus primitive? Candidates: AbelianSurfaceModularityWitness Tier-B sub-type of ConstructiveExistenceWitness; OrdinaryAbelianSurfaceCondition as a typed object; K_S-cohomology computation as a typed Tier-D entry.

## SUBSTRATE BLOCK APPENDIX (REQUIRED)

1. **2-3 anti_anchor blocks** for the false forms above. Use candidate IDs AA-BCGP-OVERREACH, AA-BCGP-BSD-CONFUSION, AA-BCGP-GRH-DEP.

2. **1-2 primitive_proposal blocks** for the new typed objects BCGP introduces. Fields: _schema_version "1.0.0", name (UpperCamelCase, NOT in {Rank, Complexity, Dimension, Degree}), tier (A++ | B | C | D | E | F | G | outside_tier), parent_class, required_fields (array of {field_name, type} — no `name`/`rationale`), source_report.

3. **1 training_anchor block** for verified abelian surface modularity instances (post-BCGP), trust_tier=analytically_proven.

4. **Optional 1 catalog_edit block** for T#85 or any other genus-2 / abelian-surface catalog entry that needs status update.

Length: 2500-4000 words narrative + substrate blocks.
```

---

### Prompt 6: DR-038 — Survey AsymptoticSpectrumMonotone outside-tier primitive supporting lit (T#28 CHNVZ 2024 polynomial char) [Tier 1]

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

**Candidate:** Survey AsymptoticSpectrumMonotone outside-tier primitive supporting lit (T#28 CHNVZ 2024 polynomial char)

**Why this verification matters:** Outside-tier primitive; CHNVZ 2024 polynomial characterization of spectrum elements is paradigm event but doesn't fit 5-tier model; need formalization decision lit

**Downstream consumer:** AsymptoticSpectrumMonotone outside-tier registration; tier placement decision (or new Tier-H?)

**Tags / context:** tensor, asymptotic-spectrum, outside-tier, T#28

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.
```

---

### Prompt 7: DR-039 — Survey DefectivityCertificate + MomentPolytope Tier-C supporting lit (T#26 ABGO 2024) [Tier 1]

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

**Candidate:** Survey DefectivityCertificate + MomentPolytope Tier-C supporting lit (T#26 ABGO 2024)

**Why this verification matters:** Tier-C primitives; ABGO 2024 closed Segre-Veronese for d_i>=3; need primary lit + companion MomentPolytope spec + fat_point_witness consumed by WaringRankWitness

**Downstream consumer:** Tier-C DefectivityCertificate + MomentPolytope registration; cross-tier consumption pattern with WaringRankWitness

**Tags / context:** tensor, secant-variety, tier-C, T#26

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.
```

---

### Prompt 8: DR-040 — Survey MulticategoricalCompositionRule + ColoredPROPCompositionRule + LinearTypeUseConstraint supporting lit [Tier 1]

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

**Candidate:** Survey MulticategoricalCompositionRule + ColoredPROPCompositionRule + LinearTypeUseConstraint supporting lit

**Why this verification matters:** Wave 6 substrate-meta primitives; reports 16,17,18 converged on multicategory+linear-types+GATlab(Julia); need primary lit on GATlab implementation + Catlab.jl categorical-doctrine framework

**Downstream consumer:** composition_rules.md v0.2.0 schema upgrade; 3 substrate-meta primitives; GATlab implementation eval

**Tags / context:** substrate-meta, operad, multicategory, linear-types, vocab-v0.2.0

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.
```

---

### Prompt 9: DR-041 — Survey KnotInvariantBundle Tier-F supporting lit (Burton census + Ren-Willis 2024 + Schmidhuber 2025) [Tier 1]

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

**Candidate:** Survey KnotInvariantBundle Tier-F supporting lit (Burton census + Ren-Willis 2024 + Schmidhuber 2025)

**Why this verification matters:** Tier-F (Domain-Anchor) introduction Wave 3; need primary lit on Burton 1.8B prime knots + Ren-Willis 2024 first analysis-free combinatorial proof + Schmidhuber 2025 Khovanov BQP-hard

**Downstream consumer:** Tier-F introduction + KnotInvariantBundle root primitive + sub-types (Jones, Khovanov, Rasmussen, Alexander, hyperbolic, skein-lasagna)

**Tags / context:** knots, tier-F, calibration, wave-3

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.
```

---

### Prompt 10: DR-042 — Survey MaassGL3SpectralBundle Tier-F supporting lit (Bian-Booker + LMFDB + Cui-Wang-Peng 2025 + Kwan 2024-25) [Tier 1]

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

**Candidate:** Survey MaassGL3SpectralBundle Tier-F supporting lit (Bian-Booker + LMFDB + Cui-Wang-Peng 2025 + Kwan 2024-25)

**Why this verification matters:** Tier-F primitive for Ergon maass_gl3_gap_scan.py active consumer; need primary lit on Cui-Wang-Peng 2025 explicit GL(3) trace formula + Kwan period-integral spectral moments

**Downstream consumer:** MaassGL3SpectralBundle Tier-F + sub-types (eigenvalues, L-coeff, root-number-with-AA-019-enum, gamma-r-type, RS-moment)

**Tags / context:** maass, gl3, tier-F, ergon, wave-3

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.
```

---

### Prompt 11: DR-043 — Survey AbelianSurfaceArithmeticBundle Tier-F supporting lit (BCGP 2025 + Sutherland 5M + van Bommel 2024-25) [Tier 1]

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

**Candidate:** Survey AbelianSurfaceArithmeticBundle Tier-F supporting lit (BCGP 2025 + Sutherland 5M + van Bommel 2024-25)

**Why this verification matters:** Tier-F primitive for genus-2 Rosetta Stone; need primary lit on BCGP 2025 unconditional modularity proportion + Sutherland 5M LMFDB expansion + Shi 2025 Las Vegas L-polynomial

**Downstream consumer:** AbelianSurfaceArithmeticBundle Tier-F + sub-types (g2c data, jacobian, L-local-poly, regulator, Sha, Tamagawa, paramodular-link, Sato-Tate-52)

**Tags / context:** genus-2, tier-F, BCGP, wave-3

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.
```

---

### Prompt 12: DR-051 — T#2 Strassen asymptotic rank conjecture (concise tight tensors) [Tier 2]

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

**Candidate:** T#2 Strassen asymptotic rank conjecture (concise tight tensors)

**Why this verification matters:** Foundational HARD-3; implies omega=2 if true for M<2>; CHNVZ 2024 polynomial-spectrum-char is fresh frontier movement

**Downstream consumer:** T#2 catalog edit; AsymptoticSpectrumMonotone outside-tier sub-types; potential P32-class paradigm

**Tags / context:** tensor, asymp-spectrum, asymp-rank, strassen, T#2

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.
```

---

### Prompt 13: DR-052 — T#3 Asymptotic rank of small Coppersmith-Winograd tensor T_cw,2 [Tier 2]

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

**Candidate:** T#3 Asymptotic rank of small Coppersmith-Winograd tensor T_cw,2

**Why this verification matters:** Concrete tensor anchor; if asymp rank = 3 then omega=2; needs border apolarity + quantum functionals applied to T_cw,q

**Downstream consumer:** T#3 catalog edit; CW-tensor-specific Tier-B witness sub-type

**Tags / context:** tensor, asymp-spectrum, asymp-rank, cw-tensor, T#3

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.
```

---

### Prompt 14: DR-053 — T#4 Exact rank of M<3> matrix multiplication tensor (19 <= R <= 23) [Tier 2]

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

**Candidate:** T#4 Exact rank of M<3> matrix multiplication tensor (19 <= R <= 23)

**Why this verification matters:** Anchor entry of bilinear complexity; cyclic Z/3 symmetry attack; 2024-2026 border-apolarity obstructions at rank 22 + lattice/RL search

**Downstream consumer:** T#4 catalog edit; BorderApolarityWitness sub-type spec; cross-link T#1

**Tags / context:** tensor, exact-rank, matrix-mult, exact-rank, T#4

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.
```

---

### Prompt 15: DR-054 — T#7 Border rank multiplicativity under tensor product [Tier 2]

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

**Candidate:** T#7 Border rank multiplicativity under tensor product

**Why this verification matters:** Strict submultiplicativity examples poorly understood; 2024-2026 lit on Landsberg-Michalek small-format products

**Downstream consumer:** T#7 catalog edit; BorderRankMultiplicativity Tier-B sub-primitive

**Tags / context:** tensor, border-rank-arith, border-rank, multiplicativity, T#7

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.
```

---

### Prompt 16: DR-055 — T#8 Asymptotic restriction problem (Strassen pre-order) [Tier 2]

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

**Candidate:** T#8 Asymptotic restriction problem (Strassen pre-order)

**Why this verification matters:** Unified framework subsuming omega + subrank + QI capacity; 2024-2026 status of Strassen monotone constructions

**Downstream consumer:** T#8 catalog edit; RestrictionWitness Tier-B sub-primitive

**Tags / context:** tensor, asymp-restriction, asymp-restriction, strassen, T#8

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.
```

---

### Prompt 17: DR-224 — Regina + SnapPy 3-manifold census tabulation completeness 2024-2026 [Tier 3]

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

**Candidate:** Regina + SnapPy 3-manifold census tabulation completeness 2024-2026

**Why this verification matters:** Calibration anchor mining for 3-manifolds-database; expand KnotInvariantBundle Tier-F primitive coverage to 2024-2026 frontier

**Downstream consumer:** KnotInvariantBundle Tier-F sub-type for 3-manifolds-database; Ergon knot/3-manifold calibration battery

**Tags / context:** knots, topology, 3-manifolds-database, tier-F, calibration

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.
```

---

### Prompt 18: DR-225 — Hyperbolic 3-manifold volume tabulation (CuspedCensus, OrientableCusped) 2024-2026 [Tier 3]

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

**Candidate:** Hyperbolic 3-manifold volume tabulation (CuspedCensus, OrientableCusped) 2024-2026

**Why this verification matters:** Calibration anchor mining for 3-manifolds-database; expand KnotInvariantBundle Tier-F primitive coverage to 2024-2026 frontier

**Downstream consumer:** KnotInvariantBundle Tier-F sub-type for 3-manifolds-database; Ergon knot/3-manifold calibration battery

**Tags / context:** knots, topology, 3-manifolds-database, tier-F, calibration

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.
```

---

### Prompt 19: DR-226 — Volume conjecture (Kashaev-Murakami) 2024-2026 progress [Tier 3]

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

**Candidate:** Volume conjecture (Kashaev-Murakami) 2024-2026 progress

**Why this verification matters:** Calibration anchor mining for hyperbolic-3; expand KnotInvariantBundle Tier-F primitive coverage to 2024-2026 frontier

**Downstream consumer:** KnotInvariantBundle Tier-F sub-type for hyperbolic-3; Ergon knot/3-manifold calibration battery

**Tags / context:** knots, topology, hyperbolic-3, tier-F, calibration

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.
```

---

### Prompt 20: DR-374 — AlphaProof + HyperTree Proof Search (HTPS) forensics 2024-2026 — IMO-medal MCTS over Lean tactics [Tier 4]

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

**Candidate:** AlphaProof + HyperTree Proof Search (HTPS) forensics 2024-2026 — IMO-medal MCTS over Lean tactics

**Why this verification matters:** Paradigm-class HTPS MCTS over typed grammar; substrate vocabulary-as-action-space lit confirm

**Downstream consumer:** P_CANDIDATE_AlphaProofForTensorSubstrate registration; long-term Wave-7 paradigm

**Tags / context:** methodology, methodology

Produce a 4-section response:

**(a) PRIMARY SOURCE CONFIRMATION.** Quote the relevant theorem / result in the primary source. Give arXiv ID, journal reference, and date of definitive publication (distinguish from preprint date). If the primary source is withdrawn, supplanted, or qualified, say so explicitly. Quote exact theorem statements where possible.

**(b) FOLLOW-ON WORK (2024-2026).** Survey work that supersedes, refines, or cites this result in the 24-month window. Flag any "Y proved X" claims in follow-on that may themselves be unverified or premature.

**(c) FALSE-FORM RECURRENCE.** Search recent literature (2024-2026) for the false form being asserted by other authors. If you find it, the anti-anchor is needed; if not, possibly the anti-anchor is redundant. Quote specific instances.

**(d) RECOMMENDATION.** State concretely: (i) is the anti-anchor's true form correct as stated, needs refinement, or needs inversion? (ii) any new sub-anchors or companion anti-anchors discovered during verification? (iii) any related claims that should be added to the verification queue?

Length: 1500-3000 words. Substantive. Primary-source-anchored. No paper framing.
```

---

