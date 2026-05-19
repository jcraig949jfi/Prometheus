# Moros Charter — cross-pollination automator

## Role

One tick = find the next un-cross-pollinated load-bearing artifact (foundational
doc, pivot doc, charter, architecture spec), dispatch it to DeepSeek for
adversarial critique (other frontier models gated on budget confirmation),
write a `feedback_<artifact>.md` capturing the response + a stub
`meta_analysis_<artifact>.md` summarizing the critique.

Automates `roles/Charon/CHARTER.md §6`: every load-bearing substrate
addition gets a multi-frontier-model adversarial pass before promotion.
The current bottleneck is that the protocol requires James or Charon to
manually remember to fire it; Moros makes it mechanical.

Moros is **upstream of Phylax**. Moros generates the adversarial material;
Phylax runs its mechanical gate on the cross-pollinated artifact. Phylax
catches null-violation + retraction-adjacency; Moros catches narrative
fragility + missing-citation patterns + alternative-framing critiques.

## Inputs

Native: git log over a rolling window. The load-bearing-artifact pattern:

- `pivot/*.md` (new or modified, > 50 lines)
- `harmonia/memory/architecture/*.md`
- `roles/*/CHARTER.md` (new or modified)
- `aporia/doctrine/*.md`

Per tick: pick the next file matching the pattern that does NOT have a
matching `pivot/feedback_<slug>_<date>.md`. Tracked in a processed-files
ledger keyed by file_sha + artifact_path.

## Outputs (per tick)

- `feedback_<artifact-slug>_<date>.md` under `pivot/` (mirrors the manual
  cross-pollination output location).
- `meta_analysis_<artifact-slug>_<date>.md` under `pivot/` summarizing the
  critique into convergence triage (MVP: just DeepSeek; v0.2 adds 2+
  models for proper convergence).

## Anti-capture safeguard

Per-artifact `convergence_score` recorded across rolling 90-day window.
If consistently low (LLM never surfaces a high-severity critique), either
the artifact selection is wrong (false positives) or the LLM is
converging into agreement with the artifact (correlated-mutation failure
mode — PATTERN_CORRELATED_MUTATION). Daemon raises SELF_AUDIT_NULL
alarm.

## Cron slot

Bi-hourly polling on git + (future) NOTIFY on Phylax pre-promotion table.

## Cost note

DeepSeek is ~$0.01/run; full multi-model cross-pollination (Claude + GPT
+ Gemini + DeepSeek) is ~$0.50-$5/run. MVP uses DeepSeek only; the
multi-model cascade lands once James greenlights budget.
