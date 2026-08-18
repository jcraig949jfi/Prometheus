# Gemini Deep Research — Prioritized Default Queue

**Filed:** 2026-05-11
**Owner:** Aporia (queue maintenance), James (token spending decisions)
**Quota:** 20 Gemini Deep Research tokens / day; use-or-lose.
**Status:** 423-entry default queue across 4 tiers; see `queue.jsonl`.

---

## Daily burn procedure

Run `python aporia/scripts/burn_research_tokens.py`. See `BURN_PROCEDURE.md` for the full procedure (state survey, mix-tuning, urgent-injection protocol, failure modes, token economics). The orchestrator surveys substrate state, picks 20 topics across tiers (default mix 8/7/3/2), builds a deck, fires the dispatcher in background, then on a second `--log-only` pass appends to `fired_log.jsonl` and mutates `queue.jsonl` in place.

---

## Purpose

This queue exists for **no-urgent-work days** — days where there is no specific synthesis-pass-driven probe, no anti-anchor refire mandate, no Techne contract-change window dependency. On those days the daily 20-token quota is use-or-lose; rather than burn it on whatever happens to be top-of-mind, this queue supplies a pre-vetted prioritized backlog every entry of which already traces to a downstream substrate consumer.

The queue is **not** a replacement for fresh dispatch decks. When a synthesis pass surfaces an explicit next-batch list (as `gemini_research_synthesis_2026-05-11.md` did with its 11 anti-anchor candidates and 6 [VERIFY-LIVE] catalog edits), those decks take precedence. The queue is for the days in between.

---

## How to fire

Standard dispatch pattern (matches the 2026-05-10 batch protocol):

```bash
python aporia/scripts/gemini_deep_research_dispatch.py \
  --deck <picked-from-queue> \
  --out aporia/docs/deep_research_batch_<YYYY-MM-DD> \
  --batch-size 3 \
  --resume
```

For the queue: a "deck" is a small ad-hoc markdown file you assemble by lifting the next N entries' prompt text into a single file. Use the `prompt_templates.md` Section 7 helper script reference, or assemble by hand for a 3-entry deck.

### Selection rule

**Top-3-unfired by tier ascending, then id ascending.** I.e., fill Tier 1 entries first (lowest id first), then drop to Tier 2 once Tier 1 is exhausted, and so on. This ensures anti-anchor verification work — the highest-priority class per `feedback_verify_upstream_attributions.md` — gets done first, and the catalog continuation and calibration-anchor mining stay on a steady cadence beneath it.

In Python (rough):

```python
import json
with open("queue.jsonl") as f:
    entries = [json.loads(line) for line in f if line.strip() and not line.startswith("#")]
unfired = [e for e in entries if not e["fired"]]
unfired.sort(key=lambda e: (e["tier"], e["id"]))
next_three = unfired[:3]
```

### Tier structure

| Tier | Count target | Purpose | Cadence |
|---|---|---|---|
| **1** | ~50 | Anti-anchor verification, [VERIFY-LIVE] catalog edits, re-verification of registered anti-anchors, new primitive supporting literature | Fire ASAP; anti-anchors are highest-priority class per `feedback_verify_upstream_attributions.md` |
| **2** | ~150 | Catalog continuation — tensor open problems + adjacent open-question catalogs Aporia maintains | Steady-cadence; multi-month exhaustion timeline |
| **3** | ~150 | Calibration-anchor mining — domain × 2024–2026 frontier surveys identifying known-true-positive sets for Ergon's calibration battery | Parallel to Tier 2 once Tier 1 thins |
| **4** | ~50 | Methodology / corpus / vocabulary expansion / longer-tail forensics | Run when 1–3 thin out, or interleave when a methodology question becomes load-bearing |

---

## After-firing protocol

1. Run the dispatch script. Reports land under `aporia/docs/deep_research_batch_<YYYY-MM-DD>/<NN>_<slug>.md`.
2. If a report comes back as a JSON/structured-dispatch wrapper rather than markdown, post-process with `aporia/scripts/extract_dispatch_text.py` (this happens occasionally when the Gemini API returns a partial-tool response).
3. Append a log entry to `fired_log.jsonl` with `id, fired_date, output_path, batch_id, status`.
4. Update the corresponding queue entry: set `fired: true`, `fired_date: <YYYY-MM-DD>`, `output_path: <path>`. The `queue.jsonl` file is intended to be mutated in-place; a periodic git commit captures the running state.
5. If the report surfaces new findings — anti-anchor candidates, catalog edits, primitive proposals — write a per-fire synthesis note (1-2 paragraphs) into `aporia/docs/gemini_research_queue/notes/<id>_<date>.md` and link from the queue entry's `notes_path` field if you add one. After ~9–18 fires accumulate, run a full synthesis pass analogous to `gemini_research_synthesis_2026-05-11.md`.

---

## Re-fill cadence

Rebuild the queue when **unfired entries drop below 100**. At 20 tokens/day and average 3 entries per fire (some batches go 1, some 6), the queue should last 2–6 months. Re-fill is a substrate-level act: it requires re-reading the latest synthesis, the tensor catalog's current state, the anti-anchor registry, and the Techne work queue, and re-ranking by tier+leverage. Do not auto-extend the queue from templates alone — entries without a current downstream consumer violate `feedback_substrate_passive_consumer_warning.md`.

---

## Quality bar

Every entry must trace to a downstream consumer. The `downstream_consumer` field is mandatory and must name one of:

- A specific Techne registration target (primitive name, anti-anchor ID, tier slot)
- A specific Ergon training-pipeline input or script (e.g., `maass_gl3_gap_scan.py`)
- A specific anti-anchor in `techne/registry/anti_anchors.jsonl` (e.g., AA-013)
- A specific substrate vocabulary patch (e.g., `composition_rules.md` v0.2.0 schema field)
- A specific catalog edit (e.g., T#NN row in `tensor_open_problems_v1.md`)

Entries with `downstream_consumer: "general interest"` are not allowed. If a topic feels worth surveying but you cannot name a consumer, the entry stays out of the queue until a consumer materializes elsewhere in the substrate.

This is enforced by convention, not by tooling. Periodic audit: search the queue for vague consumer strings and either upgrade them or drop them.

---

## Reference: prompt templates

`prompt_templates.md` contains the four template families (one per tier) plus the inline framing string each prompt should begin with. Templates encode:

- Project Prometheus context (no paper-publishing framing per HARD-1)
- Doctrine constraints (HARD-1 / HARD-2 / HARD-3 / HARD-5 / HARD-6)
- Mandated pattern citations (≥2 of {PATTERN_PRIME_GRAVITATIONAL_OVERFIT, PATTERN_CONDUCTOR_CONFOUND, PATTERN_BASE_RATE_NEGLECT, PATTERN_VRAM_TRUNCATION_ARTIFACT, PATTERN_RANK_PARITY_LEAK}) for tensor-domain entries
- Format requirements (7-section structure for frontier surveys; 4-section structure for anti-anchor verifications)
- Word-count targets

Each entry in `queue.jsonl` carries a `template` field (`tier1_aa_verify`, `tier2_frontier_survey`, `tier3_calibration_mining`, `tier4_methodology`). When assembling a deck, look up the template, substitute the entry's `title` and `why` into the template's `{topic}` and `{specific_context}` slots, and you have a fire-ready prompt.

---

## Hard-rule compliance

- **HARD-1 (no paper-publishing framing):** every prompt template begins with the substrate-grade framing string; no "for our paper" framings.
- **HARD-2 (anti-gravitational-well):** queue intentionally biases toward unfashionable directions (det/perm asymmetry, knot calibration, methodology forensics that surface failure modes); explicitly avoids "X is the future" framings.
- **HARD-3 (tensor-priority weighting):** Tier 1 entries skew tensor-heavy; tensor catalog continuation dominates Tier 2.
- **HARD-5 (distinct coordinates):** anti-anchor entries enforce coordinate-non-collapse (rank-zoo, complexity-coordinate-zoo, modularity-conditional-zoo).
- **HARD-6 / behavior delta:** every entry has a named downstream consumer. Queue maintainer audits the consumer field periodically.

No orphan entries. No "interesting but no consumer." If quality drops below the bar, the queue ends short rather than padding.

---

## File manifest

| File | Purpose |
|---|---|
| `README.md` | This file — purpose, fire protocol, tier structure, quality bar |
| `BURN_PROCEDURE.md` | Daily burn procedure, mix-tuning rules, urgent-injection protocol, failure modes |
| `prompt_templates.md` | Substrate-grade 7-section template plus variants per tier; inline framing string |
| `queue.jsonl` | The 423 entries; one JSON object per line; schema below |
| `fired_log.jsonl` | Append-only fire log; empty at queue-creation time |

Queue entry schema:

```json
{
  "id": "DR-001",
  "tier": 1,
  "domain": "tensor",
  "subdomain": "border-rank",
  "title": "Short description",
  "why": "Concrete justification with downstream-consumer trace",
  "downstream_consumer": "Named consumer (Techne registration, Ergon script, AA-NNN, etc.)",
  "template": "tier1_aa_verify | tier2_frontier_survey | tier3_calibration_mining | tier4_methodology",
  "tags": ["domain-tag", "subdomain-tag", "T#NN", "AA-NNN"],
  "estimated_yield": "1 substrate-grade report + N anti-anchor candidates",
  "fired": false,
  "fired_date": null,
  "output_path": null,
  "source": "synthesis_2026-05-11 §N | catalog_v1 §N | inferred"
}
```
