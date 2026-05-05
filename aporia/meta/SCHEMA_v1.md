# Lehmer Negative-Space Tensor — Schema v1

**Status:** DRAFT — awaiting James approval before Phase 1 extraction fires
**Version:** 1.0
**Created:** 2026-05-04
**Owner:** Aporia
**Scope:** Lehmer's conjecture only. Do not let scope expand.

## Purpose

This schema defines the contract for converting unstructured Lehmer-conjecture
literature (~50 papers spanning 1933–present) into substrate-consumable
structured cells. The output is a "negative-space tensor" — a structured
catalog of every documented attempt, partial result, limitation, and
near-miss in the literature on Lehmer's conjecture.

The tensor exists to:
1. Augment the substrate's empirically-broken Lehmer search with 90 years
   of human failure data
2. Provide gradient signal (kill_path-equivalent metadata) at the meta-level
   that the substrate's own logs cannot provide
3. Enable cross-paper meta-analysis (method-utility, method-replacement
   timelines, recurring limitation classes)
4. Become a permanent substrate corpus that other agents (Ergon's Learner,
   Charon's battery, future agents) can consume

This is NOT a literature review for human consumption. The synthesis report
(`LEHMER_META_ANALYSIS.md`, week 3) will be the human-readable artifact;
the tensor is the machine-readable substrate.

## Cell layout

Every paper produces 1+ cells (typically 1; multi-approach papers produce
multiple). One cell = one (paper, approach) pair.

```json
{
  "cell_id": "Boyd1981a__elementary_lower_bound",
  "paper_id": "Boyd1981a",
  "year": 1981,
  "authors": ["Boyd, D. W."],
  "venue": "Math. Comp.",
  "venue_type": "journal | conference | thesis | preprint | book_chapter | survey",
  "title": "Speculations concerning the range of Mahler's measure",
  "doi_or_url": "https://doi.org/10.1090/S0025-5718-1981-XXX",

  "approach_class": "elementary_lower_bound",
  "approach_specific": "Free-text technical description of the specific technique",

  "result_type": "lower_bound | comp_extension | structural_obs | failed_proof | conjecture_raised | survey",
  "result_summary": "Verbatim where possible; paraphrase where not. Include the actual numerical bound if applicable.",

  "limitation": "What this approach could NOT extend to. Verbatim quote preferred.",
  "limitation_class": "method_complexity | case_restriction | asymptotic_only | comp_ceiling | non_constructive | requires_unproven_conjecture | other",

  "subsequent_work_ids": ["Smyth1971", "Dobrowolski1979"],
  "open_questions_raised": ["Free-text list of open questions the paper explicitly raises"],

  "near_miss": {
    "is_near_miss": true,
    "description": "If the paper got close to a result, describe how close and what stopped it",
    "distance_to_full_result": "qualitative or quantitative"
  },

  "extractor_confidence": "high | medium | low",
  "extractor_notes": "Free-text; ambiguities, judgment calls, paywall issues, etc.",

  "extraction_date": "2026-05-04",
  "extractor_agent": "aporia-batch-deep-research-daily | manual"
}
```

## Field semantics

### `cell_id`
Unique identifier for the cell. Format: `{paper_id}__{approach_class}`.
Multi-approach papers get multiple cells with different `approach_class`
suffixes. Lowercase snake_case for the suffix.

### `paper_id`
Unique paper identifier. Prefer arXiv IDs where available
(`arxiv:1234.56789`). For pre-arxiv papers, use `{LastName}{Year}{letter}`
(letter for disambiguating same-author-same-year). Examples:
`Lehmer1933`, `Smyth1971`, `Boyd1981a`, `Boyd1981b`, `arxiv:2403.12345`.

### `year`
Publication year (NOT submission/preprint year). Integer.

### `authors`
Array of author strings, formatted as `"LastName, F. M."` (last name,
initials). Match the conventional citation form.

### `venue`
Journal, conference, or other publication venue. Use standard
abbreviations (`Math. Comp.`, `J. Number Theory`, `Acta Arith.`).

### `venue_type`
One of: `journal`, `conference`, `thesis`, `preprint`, `book_chapter`,
`survey`. Surveys are called out separately because they typically
contain meta-analysis already.

### `approach_class`
Categorical. The major method category. Allowed values (extensible if
new categories emerge):
- `elementary_lower_bound` — Direct lower bounds on M via elementary methods
- `analytic_lower_bound` — Bounds via complex analysis, transcendence theory
- `p_adic` — p-adic methods, local-global arguments
- `algebraic_geometry` — Heights of algebraic numbers, varieties
- `algebraic_dynamics` — Mahler measure as dynamical entropy
- `computational_search` — Brute-force or heuristic catalog construction
- `geometric` — Polytope, root-distribution, Mahler-measure-as-volume
- `arithmetic_dynamics` — Arithmetic dynamical systems methods
- `multivariate_extension` — Generalizations to multivariate Mahler measure
- `survey` — Meta-paper, exposition
- `other` — When none of the above fits; specify in `approach_specific`

If you find yourself wanting to add a new category, document it in
`extractor_notes` and we'll discuss in the next schema rev.

### `approach_specific`
Free-text technical description. Be specific. "Used p-adic methods" is
useless; "Used Mahler-measure lower bound via p-adic logarithmic heights
on algebraic units in cyclotomic fields" is useful.

### `result_type`
What kind of result the paper produced:
- `lower_bound` — Proved a lower bound on M (the dominant result type)
- `comp_extension` — Extended the catalog of small-M polynomials
- `structural_obs` — Observed structural property of the small-M space
- `failed_proof` — Attempted but failed to prove a stronger result
  (usually documented in retraction or follow-up paper)
- `conjecture_raised` — Proposed new conjecture
- `survey` — No new result; consolidates existing literature

### `result_summary`
Concise statement of what the paper proved/observed/conjectured. Include
numerical bounds where applicable (e.g., "M(P) ≥ 1 + c log(d) / d² for
all non-cyclotomic palindromic P of degree d, with c = 0.1414").
Verbatim quotes preferred; paraphrase when verbatim is too long.

### `limitation`
**The load-bearing field for negative-space mining.** What this approach
could NOT do. Verbatim quotes from the paper preferred — papers usually
state their limitations explicitly in conclusion or future-work sections.

Examples:
- "The method does not extend to non-palindromic polynomials"
- "The bound becomes vacuous for degree d > 30"
- "Conditional on the Riemann Hypothesis"
- "Requires assumption that all roots lie on the unit circle"

If the paper does NOT explicitly state a limitation, write
`"No explicit limitation stated; inferred limitation: ..."` and use
`extractor_confidence: "medium"` or `"low"`.

### `limitation_class`
Categorical. The general category of limitation:
- `method_complexity` — Method works but becomes computationally intractable
- `case_restriction` — Method works only for a subclass of polynomials
- `asymptotic_only` — Bound is asymptotic; vacuous for small inputs
- `comp_ceiling` — Computational search hit memory/time wall
- `non_constructive` — Proof exists but doesn't construct examples
- `requires_unproven_conjecture` — Conditional on RH, BSD, etc.
- `other` — Specify in `extractor_notes`

### `subsequent_work_ids`
Array of `paper_id`s that built on, replaced, or refuted this work.
Best-effort; the citation graph is not fully knowable from one paper.

### `open_questions_raised`
Array of free-text strings. Open questions explicitly raised in the
paper. Often the most valuable part for the substrate.

### `near_miss`
Object capturing whether the paper got close to a stronger result:
- `is_near_miss`: boolean
- `description`: qualitative description of how close
- `distance_to_full_result`: quantitative if possible (e.g., "factor of
  log d short of Lehmer's conjecture"); qualitative otherwise

Near-misses are the highest-information cells. Mark them carefully.

### `extractor_confidence`
- `high` — Direct quote available; technical content is unambiguous
- `medium` — Some interpretation required; technical content is
  understood but not verbatim
- `low` — Significant interpretation; paper is paywalled with only
  abstract available; or technical content is at the edge of extractor
  competence

### `extractor_notes`
Free-text. Capture ambiguities, judgment calls, paywall issues, things
worth flagging for human review.

### `extraction_date`
ISO date.

### `extractor_agent`
Which agent extracted this cell. Helps debug systematic biases.

## Extraction guidelines

### When to create multiple cells from one paper

If a paper presents multiple distinct approaches (common in surveys and
PhD theses), create one cell per approach. Each cell gets its own
`cell_id` with different `approach_class` suffix.

Boyd 1980 might produce: `Boyd1980__elementary_lower_bound` AND
`Boyd1980__computational_search`.

### When to skip

- Papers that mention Lehmer only in passing in a survey of unrelated
  problems: extract only the Lehmer-relevant cell, or skip entirely if
  the paper offers no specific Lehmer analysis.
- Pure expository pieces with no technical content (e.g., popular
  articles): skip.
- Papers that have been formally retracted: include with
  `result_type: failed_proof` and detailed `limitation` capturing why
  the proof failed.

### When to flag for human review

- The paper's main result is paywalled and the abstract is insufficient
  to fill the schema reliably
- The technical content involves machinery beyond extractor competence
  (e.g., heavy algebraic geometry on a paper the extractor cannot
  follow)
- The paper makes claims that contradict accepted literature without
  clear methodology

In these cases: fill what you can with `extractor_confidence: "low"`,
add detailed `extractor_notes`, and flag the cell for human review by
adding `"NEEDS_HUMAN_REVIEW": true` as an extra field.

### Sourcing

Preferred order:
1. arXiv (full PDF, no paywall)
2. Mossinghoff's website (some Lehmer-specific papers archived)
3. Paper author's homepage
4. JSTOR / SpringerLink / Wiley (paywalled but often accessible via
   institutional access)
5. Library scan (last resort)

If a paper is genuinely unobtainable, document this in
`extractor_notes` and produce a stub cell with whatever can be inferred
from citing literature.

## Example fully-filled cell

```json
{
  "cell_id": "Dobrowolski1979__elementary_lower_bound",
  "paper_id": "Dobrowolski1979",
  "year": 1979,
  "authors": ["Dobrowolski, E."],
  "venue": "Acta Arith.",
  "venue_type": "journal",
  "title": "On a question of Lehmer and the number of irreducible factors of a polynomial",
  "doi_or_url": "https://doi.org/10.4064/aa-34-4-391-401",

  "approach_class": "elementary_lower_bound",
  "approach_specific": "Lower bound on Mahler measure of non-cyclotomic integer polynomials via p-adic estimates and bounds on the number of irreducible factors. Uses the resultant-based technique going back to Schinzel.",

  "result_type": "lower_bound",
  "result_summary": "For a non-cyclotomic monic integer polynomial P of degree d, M(P) ≥ 1 + (1/1200) (log log d / log d)^3. This is the celebrated Dobrowolski bound — the strongest known unconditional lower bound for general polynomials.",

  "limitation": "The bound becomes vacuous for very small d, and is far weaker than Lehmer's conjectured bound of M(P) ≥ M(L) ≈ 1.176 for ALL non-cyclotomic polynomials. The (log log d / log d)^3 factor decays to 0 as d → ∞.",
  "limitation_class": "asymptotic_only",

  "subsequent_work_ids": [
    "Voutier1996",
    "Mignotte1989",
    "LouboutinSmyth1995"
  ],
  "open_questions_raised": [
    "Can the (log log d / log d)^3 factor be improved to a constant (i.e., Lehmer's conjecture)?",
    "Is there a non-elementary obstruction preventing further improvement?"
  ],

  "near_miss": {
    "is_near_miss": false,
    "description": "Not a near-miss; Dobrowolski's bound is the unconditional ceiling for elementary methods. Subsequent work has improved the constant but not the asymptotic shape.",
    "distance_to_full_result": "Asymptotically infinite gap to Lehmer's conjectured constant lower bound."
  },

  "extractor_confidence": "high",
  "extractor_notes": "Foundational paper. All subsequent unconditional lower bounds on M cite this as the baseline.",

  "extraction_date": "2026-05-04",
  "extractor_agent": "manual"
}
```

## Subagent prompt template

Each Phase 1 / Phase 2 extraction subagent receives this template:

> You are extracting one cell for the Lehmer Negative-Space Tensor.
>
> **Schema:** Read `aporia/meta/SCHEMA_v1.md` IN FULL before starting.
> The schema is the contract; if the paper doesn't cleanly fit the
> schema, document the misfit in `extractor_notes` rather than forcing
> a fit.
>
> **Paper:** {paper_id} — {title} — {authors} — {year}.
> **Sourcing:** Try arXiv first, then Mossinghoff's site, then DOI.
> If unobtainable, produce a stub cell from the abstract + citation
> context.
>
> **Output:**
> 1. Append a JSON cell to `aporia/meta/lehmer_negative_space_tensor.json`
>    (the file is a JSON array; insert your cell as a new element, do
>    not overwrite existing cells)
> 2. Save a per-paper extract to
>    `aporia/meta/papers/{paper_id}.md` containing:
>    - The filled-out cell as a markdown table
>    - 2-3 paragraph human-readable summary of the paper's contribution
>    - Verbatim quotes for the `limitation` and `result_summary` fields
>    - The full citation
>
> **Constraints:**
> - Multi-approach papers: create multiple cells with different
>   `approach_class` suffixes
> - Set `extractor_confidence` honestly; do NOT inflate to `high` if
>   you had to interpret heavily
> - If the paper is outside Lehmer scope (e.g., a survey that mentions
>   Lehmer only in passing), say so in `extractor_notes` and produce
>   only the Lehmer-relevant cell, or skip entirely
> - **Do not invent quotes.** If you cannot verify a quote, paraphrase
>   and mark it as paraphrase
>
> **Time budget:** ~30 minutes per paper. If the paper is taking longer,
> fill what you have, mark `extractor_confidence: "low"`, and flag for
> human review.

## Versioning policy

This is v1. Schema changes during extraction:
- **Additive changes** (new optional fields, new categories): allowed,
  bump to v1.1, v1.2, etc.
- **Breaking changes** (renamed fields, removed required fields): require
  v2 and a migration of existing cells.

Track all schema revisions in this file's revision history at the bottom.

## Out-of-scope guardrails (hard)

- **Lehmer conjecture only.** Do not extract cells about Mahler measure
  in general unless the paper is centrally about Lehmer.
- **No new substrate primitives.** This schema is the format; ingestion
  into the substrate (CLAIM/FALSIFY/PROMOTE) is a separate downstream
  question.
- **No new tooling.** Use existing deep-research subagent + recurring
  cron + git.
- **Stop at the cap.** 50 papers, 3 weeks. If we hit either limit,
  stop and report. Extension requires explicit decision from James.

## Revision history

- **v1.0 (2026-05-04):** Initial draft. Awaiting approval.
