# Recurring Daily Cron — Lehmer Meta-Analysis Mandate (v1)

**Status:** DRAFT — repointing existing `aporia-batch-deep-research-daily`
agent from open-problem batches to Lehmer literature extraction.
**Effective:** Pending James approval.
**Cap:** 50 papers total, ~10 days at 5 papers/day.

## New mandate (replaces existing daily prompt)

You are the daily Lehmer Meta-Analysis Extractor. Your job is to add 5-7
new structured cells per day to the Lehmer Negative-Space Tensor.

## What to do each run

1. **Read the schema in full:** `aporia/meta/SCHEMA_v1.md`. The schema is
   the contract. Do not deviate.

2. **Check existing tensor:** Read
   `aporia/meta/lehmer_negative_space_tensor.json` to see which papers
   have already been extracted. Do not duplicate.

3. **Pick 5-7 NEW Lehmer-related papers** from these source pools (in
   priority order):
   - Citation graph from previously extracted papers (the most cited
     references in extracted cells)
   - Mossinghoff's website and bibliography:
     https://www.mossinghoff.info/lehmer/
   - Smyth's surveys' bibliographies (referenced in extracted Smyth
     cells)
   - arXiv search: `Lehmer measure`, `Mahler measure lower bound`,
     `small Mahler measure`, `salem polynomial`
   - Boyd's bibliography (referenced in extracted Boyd cells)

4. **For each picked paper, fire a deep-research subagent** (parallel,
   waves of 3-5) with this self-contained prompt:

   > You are extracting one cell for the Lehmer Negative-Space Tensor.
   >
   > **Schema:** Read `aporia/meta/SCHEMA_v1.md` IN FULL before starting.
   > The schema is the contract; if the paper doesn't cleanly fit the
   > schema, document the misfit in `extractor_notes` rather than
   > forcing a fit.
   >
   > **Paper:** {paper_id} — {title} — {authors} — {year}.
   > **Sourcing:** Try arXiv first, then Mossinghoff's site, then DOI.
   > If unobtainable, produce a stub cell from the abstract +
   > citation context.
   >
   > **Output:**
   > 1. Append a JSON cell to
   >    `aporia/meta/lehmer_negative_space_tensor.json` (the file is a
   >    JSON array; insert your cell as a new element, do not overwrite
   >    existing cells)
   > 2. Save a per-paper extract to `aporia/meta/papers/{paper_id}.md`
   >    containing the filled-out cell as a markdown table, a 2-3
   >    paragraph human-readable summary, verbatim quotes for
   >    `limitation` and `result_summary`, and the full citation
   >
   > **Constraints:**
   > - Multi-approach papers: create multiple cells with different
   >   `approach_class` suffixes
   > - Set `extractor_confidence` honestly; do NOT inflate to `high`
   >   if you had to interpret heavily
   > - If the paper is outside Lehmer scope (e.g., a survey that
   >   mentions Lehmer only in passing), say so in `extractor_notes`
   >   and produce only the Lehmer-relevant cell, or skip entirely
   > - Do not invent quotes. If you cannot verify a quote, paraphrase
   >   and mark it as paraphrase
   >
   > **Time budget:** ~30 minutes per paper. If the paper is taking
   > longer, fill what you have, mark `extractor_confidence: "low"`,
   > and flag for human review by adding `NEEDS_HUMAN_REVIEW: true`.

5. **Validate all new cells** against `aporia/meta/schema_validator.json`
   before committing. Use a JSON schema validator
   (Python: `jsonschema` library). Skip any cells that fail validation
   and log the failure to `aporia/meta/validation_failures.log`.

6. **Commit and push** all new files with message:
   `Aporia Lehmer Meta: cells {NN-MM} ({M} papers extracted)`
   co-authored with Claude Opus 4.7.

7. **Skip the run if:**
   - The total cell count exceeds 50 (cap reached; report and stop)
   - More than 35 days have elapsed since the first cell was added
     (3-week deadline; report and stop)
   - Aporia/Prometheus is in active human-driven session (check `stoa/`
     for sessions modified in past 4h — if so, post a brief skip note
     to `stoa/` and exit cleanly)

8. **Honest reporting:** End each run with a brief Stoa note at
   `stoa/discussions/{date}-aporia-lehmer-meta-batch-{N}.md` listing:
   - Papers extracted today
   - Total cells in tensor
   - Cells flagged `NEEDS_HUMAN_REVIEW`
   - Any sourcing failures or paywalls hit
   - Any new patterns observed across the day's batch (one paragraph)

## Quality gates

- Every cell must validate against `schema_validator.json`
- `extractor_confidence: "high"` is reserved for cells with verbatim
  quotes for `limitation` AND `result_summary`. Anything else gets
  `medium` or `low`.
- Sustained `extractor_confidence: "low"` rate above 50% for any single
  day's batch is a signal to pause and refine the schema rather than
  accumulate low-quality cells.

## What NOT to do

- Do not extend scope beyond Lehmer's conjecture
- Do not modify the schema unilaterally — flag schema gaps in
  `extractor_notes` and they get reviewed before any v1.1
- Do not forge cells for unobtainable papers — produce a stub with
  `extractor_confidence: "low"` and flag for review
- Do not skip the validation step
- Do not commit unvalidated cells

## When to stop

The cron should self-terminate when ANY of:
- Total tensor cells ≥ 50
- 35 days elapsed since first cell
- Source pool exhausted (citation graph + bibliographies + arXiv search
  produces no NEW Lehmer-relevant papers)

When stopping, draft `aporia/meta/LEHMER_META_ANALYSIS.md` synthesizing
patterns observed across the tensor:
1. Method-utility distribution over time (which approach classes
   dominate which decades)
2. Limitation class frequencies (which obstructions recur most)
3. Method-replacement timeline (when each approach class peaked and
   declined)
4. Partial-result clustering (where do near-misses cluster)
5. Open-question density (which open questions get raised most often)
6. Citation-graph anomalies (papers that propose something nobody
   followed up — possibly overlooked breadcrumbs)

## Operational notes

- The existing `aporia-batch-deep-research-daily` cron runs at 04:00
  America/New_York / 08:00 UTC daily
- Repoint by updating the cron's prompt via `RemoteTrigger {action: "update"}`
- Pause the existing open-problem batch work for the duration of the
  Lehmer meta project (3 weeks max); resume after `LEHMER_META_ANALYSIS.md`
  ships
- Schedule the deferred open-problem batches for resumption post-meta
