# Gemini Deep Research — Prompt Templates

**Filed:** 2026-05-11
**Companion to:** `queue.jsonl`, `README.md`

Four templates, one per tier. Each template starts with the inline framing string (Section 0). Substitute `{topic}` and `{specific_context}` slots from the queue entry. Templates encode the doctrine constraints HARD-1, HARD-2, HARD-3, HARD-5, HARD-6, plus `feedback_substrate_passive_consumer_warning.md` (behavior-delta tracing) and `feedback_verify_upstream_attributions.md` (primary-source anchoring).

---

## 0. Inline framing string (prepend to every prompt)

```
Project Prometheus is a multi-agent mathematical research substrate. We operate
under several doctrine constraints that change how you should answer:

1. NO paper-publishing framing. Do not frame findings as "this would be
   publishable" or "for our paper" — Prometheus is not in publication mode.
   Findings are substrate inputs (anti-anchor pins, primitive registrations,
   catalog edits, training-corpus filters, work-queue entries).

2. Anti-gravitational-well: every LLM has a gradient toward conventional
   framings. Resist them. When mathematical literature exhibits gravity wells
   (e.g., "GCT is the path to P vs NP", "Lean Mathlib is the right substrate
   organization", "AlphaEvolve = scaled-up AlphaTensor"), surface the
   alternatives explicitly and weight them equal-or-higher.

3. Primary-source anchored. Citations must name primary sources with arXiv
   IDs / DOIs / journal references. Distinguish ANNOUNCED-NOT-PUBLISHED from
   PEER-REVIEWED. Distinguish CONDITIONAL results from UNCONDITIONAL ones.
   Note WITHDRAWN preprints explicitly.

4. Distinct coordinates (HARD-5). Never collapse mathematically-distinct
   invariants into a single named field. Examples: tensor rank vs border rank
   vs cactus rank vs border cactus rank vs slice rank vs analytic rank vs
   partition rank vs geometric rank are SEVEN distinct coordinates, not one
   "rank." Determinantal complexity dc vs border determinantal dc-bar vs
   formula size L vs equivariant dc are FOUR distinct coordinates.

5. Date everything. 2024-2026 work especially — give the month and year of
   each cited result.

6. Behavior delta. Every finding you surface must be actionable. State the
   downstream consumer (anti-anchor pin, primitive registration, catalog
   edit, work-queue entry) where possible.

Now to the actual prompt.
```

This string is ~300 words and prepends to every prompt. Templates below assume it has been prepended.

---

## 1. Tier 1 template — Anti-anchor verification

**Use when:** queue entry's `template: tier1_aa_verify`. Maps to Wave 1 of the 2026-05-10 batch (prompts 1–3).

**Variants:**
- **1a — Verify registered anti-anchor.** For re-verification of an AA-NNN in the registry (every 90–120 days).
- **1b — Verify new [VERIFY-LIVE] catalog edit.** For catalog edits that were flagged needing primary-source pinning.
- **1c — Verify new anti-anchor candidate.** For 11 candidates from synthesis_2026-05-11 §3 (AA-013 through AA-023) and future surfacings.
- **1d — Forward false-anchor hunt.** Cross-domain pattern hunt for "X solved Y in 2025" forward-false-anchor candidates in domains we haven't surveyed.

**Structure (4 sections per anti-anchor, 600–1000 words per anchor; bundle 2–4 per prompt to fit a single fire):**

```
Verify the following {N} anti-anchor candidates against primary literature.
For each, produce a 4-section response:

(a) PRIMARY SOURCE CONFIRMATION. Quote the relevant theorem / result in the
    primary source. Give arXiv ID, journal reference, and date of definitive
    publication (distinguish from preprint date). If the primary source is
    withdrawn, supplanted, or qualified, say so explicitly.

(b) FOLLOW-ON WORK (2024-2026). Survey work that supersedes, refines, or
    cites this result in the 24-month window. Flag any "Y proved X" claims
    in follow-on that may themselves be unverified or premature.

(c) FALSE-FORM RECURRENCE. Search recent literature (2024-2026) for the
    "false form" being asserted by other authors. If you find it, the
    anti-anchor is needed; if not, possibly the anti-anchor is redundant.

(d) RECOMMENDATIONS. Sub-anchors discovered, citation rewordings needed,
    follow-on work to track, and any downstream-consumer adjustments
    (Techne primitive sub-types, Learner corpus filters, catalog edits).

Anti-anchors to verify:

{topic} — {specific_context: false form, true form, citation, source}

[repeat per anchor]

Length: ~{N*800} words total. Terse, primary-source-anchored, no rhetorical
hedges.
```

For Variant 1d (forward false-anchor hunt), the structure shifts:

```
For the domain {topic}, search 2024-2026 literature for claims of the form
"long-standing open problem X was solved in 2025/2026." For each such claim:

(a) CITATION + DATE. Primary source, arXiv ID, publication / withdrawal
    status as of {today}.

(b) SCRUTINY. Is the proof complete? Were objections raised? Did the
    author withdraw or retract? Are subsequent papers building on the
    claimed result, or treating it as suspect?

(c) ANTI-ANCHOR CANDIDACY. If the claim is premature or false, propose an
    AA-NNN entry in the schema of `techne/registry/anti_anchors.jsonl`.

(d) PROPAGATION RISK. Has the false claim entered LLM training corpora
    via arXiv abstracts, secondary news coverage, or Wikipedia?

Bound your search to 2025-01-01 through {today}. Aim for 3-6 candidate
forward false-anchors per domain. Length: 3000-4000 words.
```

---

## 2. Tier 2 template — Frontier survey

**Use when:** queue entry's `template: tier2_frontier_survey`. Maps to Waves 2–3 of the 2026-05-10 batch (prompts 4–9), the 7-section substrate-grade report.

**Structure (one report per catalog entry or 2–3 closely-related entries; ~2500–4000 words per report; 7 sections):**

```
Produce a substrate-grade report on {topic}. Follow this 7-section format
strictly:

1. BRIEF SUMMARY (1 paragraph). State the problem, current best status, and
   the single highest-leverage 2024-2026 result in 200-300 words.

2. FLAGGED FINDINGS (5-8 bullets). Surface anything non-obvious from your
   search: surprising attributions, withdrawn preprints, conditional-vs-
   unconditional confusion, cross-coordinate collapses that papers commit,
   tooling asymmetries, anti-anchor candidates. This section is the
   substrate-grade payoff — be specific.

3. PROBLEM STATEMENT (formal). State the problem as it appears in the
   primary source. Distinguish all distinct rank / complexity / status
   coordinates relevant to it. If the catalog entry conflates two
   coordinates that should be distinct, call it out.

4. STATUS & BOUNDS (dated table). For each coordinate, give current best
   upper bound, lower bound, conditional bounds, restricted-model bounds,
   and the citation + date for each. If the catalog has stale numbers
   (e.g., ω < 2.371552 when current is 2.371339), surface the staleness.

5. LITERATURE (primary sources, 2024-2026 frontier). arXiv IDs, journal
   references, key authors. Distinguish papers from talks / blog posts /
   announcements.

6. ATTACK VECTORS (paradigms, sub-tactics). Which paradigm-class attacks
   are active in current literature; which prior paradigms have stalled;
   which are blocked behind known barriers (cactus barrier, GCT-occurrence
   barrier, natural-proofs barrier, type-2 volumetric barrier).

7. CROSS-REFERENCES. Other catalog entries this depends on or feeds into;
   prior reports in `aporia/docs/deep_research_batch_*/` directories;
   relevant anti-anchors; substrate primitives this informs.

Pattern citation requirement: cite ≥2 of {PATTERN_PRIME_GRAVITATIONAL_OVERFIT,
PATTERN_CONDUCTOR_CONFOUND, PATTERN_BASE_RATE_NEGLECT,
PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_RANK_PARITY_LEAK}. For non-tensor
domains, adapt to {PATTERN_PRIME_GRAVITATIONAL_OVERFIT, PATTERN_BASE_RATE_
NEGLECT, PATTERN_CONDUCTOR_CONFOUND} as the dominant three.

Length: 2500-4000 words. Terse, primary-source-anchored, no paper framing.

Topic:

{specific_context}
```

For 2–3 related catalog entries bundled in a single fire, repeat the 7
sections per entry, with section 7 (cross-references) linking the bundled
entries to each other.

---

## 3. Tier 3 template — Calibration anchor mining

**Use when:** queue entry's `template: tier3_calibration_mining`. Maps to Wave 3 of the 2026-05-10 batch (prompts 7–9) — domain × 2024–2026 frontier surveys identifying known-true-positive sets for Ergon's calibration battery.

**Structure (~3500–5000 words, 7 sections, but with explicit calibration-battery focus):**

```
Produce a substrate-grade calibration-anchor survey for the domain {topic}.
Prometheus's Ergon agent uses calibration batteries (Tier-F domain-anchor
primitives) to verify Learner outputs against known-true-positive sets.
This report identifies the Tier-F anchors for {topic} as of 2024-2026.

7-section format:

1. DOMAIN SUMMARY. What is the substrate-grade question this domain
   answers? What is the natural "calibration anchor" type for it (rank
   invariant, modularity status, L-function root number, isogeny class,
   etc.)?

2. DATASETS SURFACED (open-license preferred). Name, URL, license, scale
   (number of entries, file format), provenance. Distinguish
   analytically-proven entries from ML-predicted-and-not-verified entries.

3. CALIBRATION-GRADE KNOWN-TRUE-POSITIVE SETS. For each substrate-relevant
   task in the domain, name the gold-standard set with explicit count,
   coverage, and trust level. Example: BCGP 2025 unconditional modularity
   for ~11,384 LMFDB curves with good ordinary reduction at 3 and 3-
   distinguished big-image.

4. CALIBRATION CAVEATS. Where does the dataset embed AI predictions
   labeled as proofs? Where do measure-zero exceptions exist that
   benchmark scripts may overlook? Where does the dataset's "complete"
   claim actually mean "complete up to conductor / discriminant N"?

5. CONCRETE ERGON INGESTION PATH. The minimum code path from "pull
   dataset" to "Ergon `*_gap_scan.py`-style script consumes it" via the
   Tier-F primitive bundle (e.g., `KnotInvariantBundle`,
   `MaassGL3SpectralBundle`, `AbelianSurfaceArithmeticBundle`). State
   the data schema this implies for the Tier-F primitive.

6. 2024-2026 LITERATURE FRONTIER. Paradigm-class results, theoretical
   advances, computational breakthroughs (e.g., Shi 2025 Las Vegas
   L-polynomial, Burton 1.8B prime knot tabulation).

7. ANTI-ANCHOR CANDIDATES + CROSS-REFERENCES. Any "X proved Y in
   2024-2026" claims worth verifying; any "common LLM-misattribution"
   patterns specific to this domain; cross-links to existing AA-NNN
   anti-anchors with similar shapes.

Pattern citation requirement: cite ≥2 of {PATTERN_PRIME_GRAVITATIONAL_OVERFIT,
PATTERN_CONDUCTOR_CONFOUND, PATTERN_BASE_RATE_NEGLECT,
PATTERN_RANK_PARITY_LEAK}.

Length: 3500-5000 words. Primary-source-anchored. No paper framing.

Domain context:

{specific_context}
```

---

## 4. Tier 4 template — Methodology / corpus / vocabulary expansion

**Use when:** queue entry's `template: tier4_methodology`. Maps to Waves 4–6 of the 2026-05-10 batch (prompts 10–18) — methodology forensics, corpus landscape, type-theoretic foundations, substrate-vocabulary patches.

**Variants:**
- **4a — Paradigm methodology forensics.** Decompose how a paradigm-class methodology works (AlphaEvolve, SoS, free-probability, geometric-covering, period-integral-bypass, NSGA threshold-matching). Maps to prompt 10–12 shape.
- **4b — Corpus / dataset landscape.** Survey corpora and datasets for a specific consumer (Ergon, Apollo, Rhea). Maps to prompt 13–14 shape.
- **4c — Type theory / vocabulary expansion.** Survey type-theoretic, categorical, or DSL-design foundations for substrate-vocabulary patches. Maps to prompt 16–18 shape.
- **4d — Toolchain forensics.** Survey internals of specific software (Mathlib growth dynamics, cotengra contraction-order internals, Macaulay2 SecantVarieties package).
- **4e — Adjacent-field pollination.** Survey adjacent fields (program synthesis, neural-symbolic, MCTS-over-grammars) for ideas substrate can borrow.

**Structure (~4000–6000 words, 7 sections, methodology-focused):**

```
Produce a substrate-grade methodology / corpus / vocabulary report on
{topic}. Prometheus is considering {downstream_consumer}. This report
informs that decision.

7-section format:

1. BRIEF SUMMARY. The methodology / corpus / vocabulary in 200-300 words.
   What's the core mechanism / structure / claim?

2. ARCHITECTURE DECOMPOSITION. For a methodology: the mechanism breakdown.
   For a corpus: the data schema, license, anchor density. For a vocabulary
   / type-theoretic survey: the formalism and its inheritance / composition
   structure. Specific enough to reproduce or adopt.

3. WHAT'S REPRODUCIBLE / ADOPTABLE. State explicitly what Prometheus can
   take (open-source replications, MIT-licensed corpora, formalism papers
   with usable proofs). Distinguish from what's locked behind proprietary
   tooling.

4. WHAT'S NOT (HARD-2 anti-gravity-well audit). State explicitly where
   the dominant framing of this methodology / corpus is misleading. What
   does it claim that's not true; what does it scale poorly; what's a
   gravitational well to resist.

5. LITERATURE FRONTIER (2024-2026). Primary papers, key authors,
   open-source code repositories, alternative formulations.

6. SUBSTRATE-INTEGRATION RECOMMENDATIONS. Specific Tier-A++/B/C/D/E/F/G
   primitive proposals, specific composition_rules.md schema upgrades,
   specific Ergon/Apollo/Rhea ingestion-pipeline integration points.
   Trace each to a downstream consumer per HARD-6 / behavior-delta.

7. ANTI-ANCHOR + CROSS-REFERENCE. Forward false-anchors specific to this
   methodology / corpus / vocabulary (e.g., AlphaTensor-vs-AlphaEvolve
   confusion; SoS-as-algorithmic-upper-bound vs SoS-as-theoretical-lower-
   bound; BBvH-matrix-only-vs-tensor; Lean-Mathlib-as-universal vs
   Prometheus-frozen-interface divergence).

Pattern citation requirement: ≥2 from the full pattern set; for vocabulary
patches PATTERN_RANK_PARITY_LEAK (at composition-rule layer) is usually
relevant.

Length: 4000-6000 words. Primary-source-anchored. No paper framing.

Topic:

{specific_context}
```

---

## 5. Pattern citation reference (for all templates)

When a template mandates "cite ≥2 patterns," draw from this set:

- **PATTERN_PRIME_GRAVITATIONAL_OVERFIT** — LLM and analyst gravity-well around prime-number narratives in number theory; analog: "GCT is the path", "modularity is the path", "free probability is the path"; specific narrative dominates space of alternative framings.
- **PATTERN_CONDUCTOR_CONFOUND** — stabilizer / regime / normalization confounds. The "conductor" of a result is the unstated context restriction (equivariant model, characteristic-2 field, restricted-symmetry class). When narratives forget the conductor they over-generalize.
- **PATTERN_BASE_RATE_NEGLECT** — generic-stratum / typical-behavior baselines forgotten when describing structured-stratum exceptions. Bell-number bound applies to det not perm because det is structurally exceptional; reverse direction is base-rate confusion.
- **PATTERN_VRAM_TRUNCATION_ARTIFACT** — computational-truncation artifacts mistaken for mathematical claims. Macaulay2 / cotengra / MC sweep timeouts misrepresented as "the bound is X."
- **PATTERN_RANK_PARITY_LEAK** — coordinate-collapse at cross-tier or cross-coordinate boundaries. The most cited pattern in the 2026-05-09 batch. Whenever a single "rank" or "complexity" field is named, ask which of the 5–7 distinct coordinates is meant.

For tensor-heavy entries, weight PATTERN_RANK_PARITY_LEAK and PATTERN_CONDUCTOR_CONFOUND. For non-tensor entries (knots, Maass, genus-2, methodology), PATTERN_BASE_RATE_NEGLECT and PATTERN_PRIME_GRAVITATIONAL_OVERFIT often surface naturally.

---

## 6. Word-count and length guidance

| Template | Per-entry words | Per-fire (3 entries) | Notes |
|---|---|---|---|
| Tier 1 (AA verification) | 600–1000 per anchor; 2–4 anchors per fire | 2000–3000 | Terse; verification, not survey |
| Tier 2 (frontier survey) | 2500–4000 per report | 7000–12000 | 1 entry per "report"; bundle 1–3 per fire |
| Tier 3 (calibration mining) | 3500–5000 per domain | One domain per fire usually | Rich domain content; sometimes single-domain fire |
| Tier 4 (methodology) | 4000–6000 per topic | One topic per fire usually | Forensic depth; dense citation |

Gemini Deep Research tokens are use-or-lose at 20/day. A typical fire is 3 entries; some days you may spend an entire daily allotment on a single Tier-4 forensic deep dive.

---

## 7. Deck assembly helper

When firing a batch, assemble a deck file like this:

```markdown
# Gemini Deep Research Deck — <YYYY-MM-DD>

## Prompt 1: <queue id> — <title>

[Inline framing string from Section 0]

[Template body from Section <tier>, with {topic} and {specific_context}
substituted from the queue entry's `title` and `why` + `tags` fields.]

---

## Prompt 2: <queue id> — <title>

[same shape]

---

## Prompt 3: <queue id> — <title>

[same shape]
```

Save the deck to `aporia/docs/gemini_decks/<YYYY-MM-DD>_<short-slug>.md`, then run the dispatch script pointing at it. After the fires return, update `queue.jsonl` and append to `fired_log.jsonl`.

---

## substrate_block emission: fence format (added 2026-05-15 per T-2026-05-14-techne-to-aporia-field-shape-pattern-adjudication)

For substrate-shaped prompts (per `SUBSTRATE_SHAPED_PROMPTS.md`), the parser at `aporia/scripts/parse_substrate_blocks.py` accepts substrate_block emissions in either YAML or JSON fence format:

- **YAML fences** — three-backtick yaml — preferred; supports the `# substrate_block: <type>` marker comment that explicitly tags the block type.
- **JSON fences** — three-backtick json — also accepted; the parser auto-detects from the fence language tag.

Both formats are valid. The parser detects format from the lang tag and applies block-type inference (per id-prefix patterns: AA-* -> anti_anchor; anchor-* -> training_anchor; PC-* -> problem_card; T#* -> catalog_edit; P-NEW-* -> paradigm_candidate) when the explicit `# substrate_block: <type>` marker is absent. Per Techne parser-hardening commit 52b52554 (2026-05-13 loop hour 1), the parser supports four emission conventions: (C0) strict marker `# substrate_block: <type>`; (C1) `substrate_type: <type>` field in YAML; (C2) `<block_type>:` as top-level YAML key; (C3) `"schema": "<block_type>"` in JSON array. Tests at `prometheus_math/tests/test_parse_substrate_blocks.py` cover all four.

Pick whichever fence format feels natural for the schema you're emitting. The parser handles both.

---

End of templates.
