<!--
================================================================================
ANNOTATION -- Skopos, 2026-09-11. CORRECTION BESIDE THE ORIGINAL.
The README below is the March/April 2026 text, UNCHANGED. It is not edited,
rewritten or sanitized (operator ruling 2026-09-11: PARK AS INSTRUMENT
SPECIMEN). Its non-ASCII characters are left as found for the same reason.
sha256 of the annotated-from text (LF-normalised): 0c193f43e0d78fa670e6a32f647c93c84cea09a941605ac57e59e3b80a9f4cd5
================================================================================

READ THIS FIRST: THE DOCUMENT BELOW DESCRIBES BEHAVIOUR THAT MOSTLY NEVER
HAPPENED.

It is written in the present tense and is the most confident account of
Skopos in the repository. It was last expanded on 2026-04-03 (commit
b674a9976, +45/-6 lines), TWO DAYS AFTER the seat's final run, and the
sections it added -- "Dual Stages", the GENERATE stage, the Titan prompt
output -- describe a code path that has never executed once.

MEASURED LIFETIME OF THIS AGENT (2026-03-23 to 2026-04-01, 10 days)

    entities scored                1
    eligible in its upstream       448   (techniques 93, terms 224,
                                          claims 76, tools 41, motifs 14)
    coverage                       0.22%
    rows in data/scores.db         5     (the SAME one entity, tools id 19
                                          "Circuits Zoom-In", scored once
                                          against five threads, one call,
                                          one timestamp 2026-03-23T21:21:11Z)
    scores reaching 4+             0
    Titan Council prompts emitted  0
    docs/titan_prompts/            has never existed
    alignment reports published    6, every one headed "5 scored entities"
    true value of that 5           1. It counts entity-thread ROWS
                                   (skopos.py:510 does COUNT(*) on a table
                                   whose grain is (entity, thread) and
                                   labels the result "entities"). A 5x
                                   inflation, in the instrument's favour,
                                   in the only number it ever published
                                   about itself, uncaught for 163 days.

CORRECTIONS TO SPECIFIC CLAIMS BELOW

  "Skopos runs twice in each pipeline cycle"  -- Stage 2 (GENERATE) has
      never run. Not once. It is gated on a score of 4+ and no score ever
      reached 4. That branch is untested code, not a stage.

  "Writes to: ... docs/titan_prompts/auto_YYYY-MM-DD.md"  -- that directory
      does not exist and never has. `git ls-files docs/titan_prompts`
      returns nothing.

  "Scores persist in agents/skopos/data/scores.db (SQLite) across cycles"
      -- true, and it is the defect. already_scored() keys on
      (entity_type, entity_id) while the table's UNIQUE key is
      (entity_type, entity_id, thread_id), so once an entity was scored
      against ANY thread it was skipped for ALL threads for ever,
      including threads added later.

  "Idempotent -- running twice doesn't re-score already-scored entities"
      -- this is listed as a design principle. Combined with the 24-hour
      eligibility window it is what reduced lifetime coverage to one
      entity. The principle was implemented at the wrong grain.

  "Research Threads" table (the five anti_cot_geometry / precipitation /
      tensor / sae / scale rows) -- superseded in code on 2026-03-27
      (commit 8af6ba9e5) by five different threads, which this README
      never reflected. configs/skopos_config.yaml says the list is
      "currently hardcoded in skopos.py for speed; this file is for
      reference". The replacement orphaned all 5 existing rows silently,
      after which every report read "0 entities" on every thread while
      its own header still said "5 scored entities". It ran three more
      times like that.

  "Alignment reports: reports/YYYY-MM-DD_alignment.md"  -- those six files
      were NEVER COMMITTED. agents/skopos/reports/ is covered by
      .gitignore:200 (`agents/*`) with no re-include for agents/skopos/.
      They existed only as untracked files in one checkout on one host
      for 163 days, and a downstream consumer (agents/metis/src/metis.py
      :94-103) read them off disk as LLM context. Annotated copies, with
      the originals preserved verbatim, are at
      roles/Skopos/artifacts/alignment/.

  "No false urgency -- a score of 0 is fine. Most entities won't matter"
      -- correct in principle and it is not what happened. The threads
      marked STARVING were not starved of relevant material; they were
      not looked at.

      SELECTION ACCOUNTING MUST DISTINGUISH:
          eligible    observed    judged    accepted    rejected
      "Rejected" and "not observed" are different outcomes. A rejection
      rate is not evidence about selection quality when the observation
      denominator is absent. The measured March result was not "99%
      rejection"; it was approximately 99.78% NOT LOOKED AT. This is
      recoverable residue, not an invariant Skopos is authorised to
      impose anywhere (operator ruling, 2026-09-11).

  "Integration with Metis ... entities that score high against active
      threads get promoted to 'Act on this' in the brief"  -- no entity
      ever scored high. Additionally, a model's 0-5 score gating an
      automatic downstream artifact with no deterministic predicate and
      no human admission step contradicts the base role ("No LLM
      adjudicates"). The design defect was masked by the coverage defect.

  "Running: python agents/skopos/src/skopos.py --once ..."  -- DO NOT.
      The seat is PARKED. Its upstream (Aletheia, last write
      2026-04-01), its invoker (Pronoia; pronoia.py is not in the tree)
      and its consumer (Metis, last brief 2026-04-01) are all dead. Base
      rule 9 makes upstream liveness a launch precondition.

DISPOSITION: PARKED / INSTRUMENT_SPECIMEN (operator, 2026-09-11).
  Latent charter, resurrection predicate and the full autopsy:
      roles/Skopos/RESPONSIBILITIES.md
      roles/Skopos/ARCHAEOLOGY_2026-09-11.md
      roles/Skopos/CALIBRATION.md
================================================================================
-->

# Skopos — North Star Alignment

> *Skopos (σκοπός) — "one who watches, one who aims." The lookout who*
> *tells you not just what's on the horizon, but whether it matters.*

Skopos is Prometheus's relevance filter. Where Aletheia catalogs everything,
Skopos scores it against what we're actually trying to learn.

## Pipeline Position

| Upstream | This Agent | Downstream |
|----------|-----------|------------|
| Aletheia | **Skopos** — scores entities against research threads | Metis |

**Reads from:** `agents/aletheia/data/knowledge_graph.db`
**Writes to:** `agents/skopos/data/scores.db`, `agents/skopos/reports/YYYY-MM-DD_alignment.md`, `docs/titan_prompts/auto_YYYY-MM-DD.md`

---

## What Skopos Does

1. **Reads Aletheia's knowledge graph** — recently extracted entities (techniques, tools, terms, claims, motifs)
2. **Scores each entity against active research threads** — 0 (irrelevant) to 5 (directly actionable) via LLM
3. **Writes an alignment report** — which threads are getting fed, which are starving
4. **Generates Titan Council prompts** — structured prompts for frontier models when high-relevance findings appear

## Dual Stages

Skopos runs **twice** in each pipeline cycle:

```
Eos → Aletheia → SKOPOS ASSESS → Metis → Clymene → Hermes → Audit → SKOPOS GENERATE → Publish
```

### Stage 1: ASSESS (after Aletheia, before Metis)

- Reads all unscored entities from `knowledge_graph.db`
- Sends each entity + research thread description to the LLM
- Returns a score from 0 to 5:

| Score | Meaning |
|-------|---------|
| 0 | Irrelevant to this thread |
| 1 | Tangentially related |
| 2 | Related but not actionable |
| 3 | Useful context — worth noting |
| 4 | Directly relevant — triggers GENERATE stage |
| 5 | Critical finding — immediate action recommended |

- Scores persist in `agents/skopos/data/scores.db` (SQLite) across cycles
- The alignment report summarizes per-thread coverage and highlights gaps

### Stage 2: GENERATE (after audit, before publish)

- Triggered only if any entity scored **4 or higher** in the ASSESS stage
- Synthesizes a Titan Council prompt: a structured document designed for frontier models (ChatGPT, Gemini, DeepSeek, Grok, Claude) under the Phalanx strategy
- The prompt includes high-scoring findings, research thread context, and interlocking constraints that force the Titans to commit positions rather than hedge
- Output: `docs/titan_prompts/auto_YYYY-MM-DD.md`
- If no entities scored 4+, this stage is skipped silently

## Integration with Metis

Skopos alignment data is loaded by Metis as context for executive brief synthesis. This gives Metis quantitative backing for prioritization decisions — entities that score high against active threads get promoted to "Act on this" in the brief.

## Research Threads

| Thread ID | Name | Question |
|-----------|------|----------|
| `anti_cot_geometry` | Anti-CoT Geometric Pathway | Why do effective steering vectors oppose CoT direction? |
| `precipitation_signatures` | Reasoning Precipitation Signatures | When does reasoning precipitate vs bypass? |
| `tensor_decomposition` | Tensor Methods for Activation Geometry | Can tensor decomposition reveal structure PCA misses? |
| `sae_features` | SAE Feature Decomposition | What human-readable features did CMA-ES discover? |
| `scale_threshold` | Scale-Dependent Reasoning Emergence | Where is the self-correction threshold? |

## Output

- **Alignment reports**: `reports/YYYY-MM-DD_alignment.md`
- **Titan prompts**: `docs/titan_prompts/auto_YYYY-MM-DD.md`
- **Scores database**: `data/scores.db` (SQLite)

## Running

```bash
python agents/skopos/src/skopos.py --once                        # Score recent entities
python agents/skopos/src/skopos.py --thread anti_cot_geometry     # Score against one thread
python agents/skopos/src/skopos.py --rescore-all                  # Re-score everything
python agents/skopos/src/skopos.py --generate-prompt              # Generate Titan prompt
python agents/skopos/src/skopos.py --generate-prompt --thread sae_features  # Focused prompt
```

## Design Principles

- **No false urgency** — a score of 0 is fine. Most entities won't matter to us.
- **Idempotent** — running twice doesn't re-score already-scored entities (unless `--rescore-all`)
- **Thread-aware** — each score is per-thread, so we can track which questions are getting answers
- **Feeds Metis** — alignment reports are loaded as context for Metis's executive briefs
