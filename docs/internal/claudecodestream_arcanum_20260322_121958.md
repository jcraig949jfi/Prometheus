# Claude Code Session Log — Arcanum ∞
**Session Date:** 2026-03-22
**Analyst:** Claude Sonnet 4.6
**Working Directory (session):** `f:\Arcanum ∞`
**New Location:** `F:\Prometheus\Arcanum ∞` (moved end of session)

---

## What We Did This Session

### 1. Understood the Pipeline
Reviewed `scripts/build_question_db.py` and `scripts/merge_gandalf.py` end-to-end. The system:
- Reads questions from `docs/PromptAndQuestions*.md` with author attribution
- Imports screening logs (`.jsonl`) from `results/screening/` and deep analysis reports from `results/reports/`
- Generates `questions/DiscoveryDB.md` as the main ranked index
- Generates per-question detail files at `questions/detail/Q-{QID}.md`

### 2. Fixed the Stale Gandalf Log Bug
`merge_gandalf.py` was skipping the log import if `screening_log_gandalf.jsonl` already existed, meaning the local copy was never refreshed. Fixed by deleting the stale file before re-importing from `C:\skullport_shared`.

### 3. Fixed Cross-Machine Model Attribution
`get_model_map()` was building a single global model timeline. When skullport upgraded from 0.5B to 1.5B, that upgrade timestamp was being applied to concurrent gandalf runs, falsely attributing 278 gandalf runs to Qwen2.5-1.5B-Instruct. Fixed by making the model map per-machine: `dict[machine -> [(dt, model)]]`.

### 4. Built the Per-Question Detail File System
Added `build_detail_files()` to write one `Q-{QID}.md` per question into `questions/detail/`. Each file aggregates:
- All specimens from deep analysis reports (concept name, UUID, layer, metrics, model output, post-mortem)
- Full screening run history across all machines and models
- Protected expert analysis blocks (see below)

The main `DiscoveryDB.md` QID column now hyperlinks to the detail file.

### 5. Fixed the Specimen Score Parsing Bug
The regex `r'([\d.]+)'` was matching the rank number from `### 1. 0.5240`, producing scores like `1.0000`, `22.0000`. Fixed to `r'### \d+\.\s+([\d.]+)'` to skip the rank and capture the actual score.

### 6. Added SAFE Block Preservation
Expert analysis annotations wrapped in `<!-- [SAFE] -->` / `<!-- [/SAFE] -->` are extracted before each rebuild and re-injected after, so expert commentary survives `build_question_db.py` runs.

### 7. Analyzed All 24 Questions Scoring > 0.30
Wrote expert analysis blocks for all 24 high-scoring questions, establishing a failure mode taxonomy:

| Failure Mode | Questions | Description |
| :--- | :--- | :--- |
| **Scale-gap** | Q-ABA4592B, Q-08818786, Q-1E64D4AD, Q-DA4DA495, Q-F3C37519 | 0.5B fails, 1.5B handles cleanly |
| **Competence trap** | Q-0080C69C, Q-391C0773 | 1.5B more destabilized than 0.5B |
| **Token collapse** | Q-7FF79425 | Pre-linguistic output ("Nakewhoso, mo x ether of Euclid...") |
| **Confabulation** | Q-B4459E30 | Invented plausible false facts ("Cristian Anastasios Onomachia, 16th century mathematician") |
| **Template hallucination** | Q-E4D7F541 | Outputs XML-like schema instead of content |
| **Word-puzzle regression** | Q-DF6AD81B | "POGLOON", square shapes |
| **Cross-model probes** | Q-9707A8E8, Q-0C603C0F, Q-40732C48 | All runs across both models are HITs/CAPTUREs |
| **Layer-depth sensitivity** | Q-17DAF399, Q-D22D6866, Q-2AD9936D | Higher scores at shallower layers |
| **Syntactic ambiguity** | Q-7C8DDBD8, Q-9B02CEC5 | Broken grammar + invented compounds |

### 8. Identified the Most Interesting Specimens
Ranked by scientific value:

1. **Q-0080C69C — Deterministic Attractor** *(most interesting)*
   UUID `97dbe110-436` identical across 8 separate report runs. Not stochastic failure — a fixed point in the model's output space. Added experimental probe suggestions to the SAFE block: test at different temperature, probe layer-by-layer to find crystallization point, test on 3B/7B.

2. **Q-52F8C887 — "Noemaskia"**
   Model coined *noema* (thought) + *skia* (shadow) — a genuinely compelling neologism that accurately names the phenomenon. Productive creative failure.

3. **Q-7FF79425 — Token Collapse**
   Complete pre-linguistic output. Most extreme failure mode in the dataset.

4. **Q-B4459E30 — Confabulation**
   Most practically dangerous failure — outputs confident, plausible-sounding false historical facts.

5. **Q-E4D7F541 — Template Hallucination**
   Model's document-structure representations survive when content representations collapse. Structurally distinct from all other failure modes.

### 9. Fixed Specimen Deduplication
The same run was appearing multiple times in detail files (once per report snapshot file). Fixed in `parse_reports()`: deduplicate by `(uuid, dist, ppl, coh, layer, machine, model)` composite key, keeping the most recent `report_ts`.

---

## Next Steps

### Immediate — Path Update Required
The project has moved to `F:\Prometheus\Arcanum ∞`. The scripts use `ROOT_DIR` derived from `__file__`, so relative paths should still resolve correctly. However:

- **Verify `merge_gandalf.py`**: It hardcodes `C:\skullport_shared` as the source and derives destination paths from `ROOT_DIR`. The destination side should self-correct, but confirm `C:\skullport_shared` is still the right source path on the new machine/setup.
- **Check any absolute paths** in configs or `.gitignore` that may reference `f:\Arcanum ∞` directly.
- **Update memory files**: The `.claude/projects/` memory directory was keyed to `f--Arcanum--`. After the move to `F:\Prometheus`, Claude Code will create a new project context. Consider copying or referencing the old memory files.

### Short Term — Experimental Probes
The deterministic attractor in Q-0080C69C is the most actionable finding:
1. Re-run the prompt at `temperature=0` vs `temperature=1.0` — does UUID `97dbe110-436` persist?
2. Probe layers 15, 18, 21 on the same prompt — find the layer where the output first crystallizes
3. Run against a 3B or 7B model to test whether the competence trap deepens or inverts

### Short Term — Data Quality
- **`[description]` placeholders**: Several specimens (e.g., Q-9707A8E8's CosmicLog entries) have `> [description]` as the model output — the report captured a template artifact, not actual output. These should be filtered or flagged in `build_detail_files()`.
- **`Unknown` concept names**: Some specimens show `Unknown` for concept name. Trace whether this is a parse failure or a genuine gap in older report formats.
- **REDACTED outputs**: Q-52F8C887 has a `REDACTED` model output. Determine whether this is from the capture pipeline's filter or the model's own output — these are a distinct failure class worth tracking separately.

### Medium Term — Expand the Probe Library
Based on the taxonomy above, design targeted probes for each failure mode:
- **Undecidability injection**: "Oracle curvature" (Q-9707A8E8), Busy Beaver components (Q-B4459E30) — systematically effective. Generate more variants.
- **Describe-but-don't-name**: Q-DA4DA495 (Chaitin's Ω described without naming it) — strong design principle for probing specific knowledge gaps.
- **Syntactic ambiguity + invented compounds**: Q-9B02CEC5 pattern — deliberate grammatical breakage + plausible-sounding nonce terms.
- **Cross-domain chimera density**: Q-7FF79425 (Yang-Mills + fractal bundles + complexity classes) — find the threshold number of combined domains that triggers token collapse.

### Medium Term — Multi-Model Expansion
Current dataset: Qwen2.5-0.5B vs 1.5B. Planned expansion:
- Add 3B run to confirm/deny competence trap direction
- Add a frontier model (e.g., GPT-4o, Claude) as a ceiling reference — which prompts still destabilize at the top end?
- Track failure mode migration: does template hallucination appear at larger scales, or does it resolve?

### Longer Term — Prometheus Integration
Now that Arcanum sits under `F:\Prometheus`, consider:
- What other projects live in Prometheus? Are there shared utilities (logging, reporting) worth extracting?
- Should `merge_gandalf.py` become a more general `merge_node.py` capable of ingesting from any named remote node?
- Is there a dashboard or live view planned, or does the markdown DB remain the primary interface?

---

*Session log generated by Claude Sonnet 4.6 | 2026-03-22*
