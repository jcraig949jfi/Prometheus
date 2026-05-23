# Talos Corpus

Training corpus for the reasoning-code-specialist LoRA. Phase 0 builds it; Phase 1 (GPU training) consumes it.

## Layout

```
agents/talos/corpus/
  README.md                — this file
  manifest_latest.json     — atomic consumer-facing pointer (regenerated each productive tick)
  manifest_<UTC-date>.json — per-tick historical snapshots
  shards/                  — gitignored; the actual training data
    hephaestus_forge.jsonl
    apollo_organism.jsonl
    prometheus_substrate.jsonl
    external_reasoning_oss.jsonl
    synthetic.jsonl
  _staging/                — gitignored; sources before extraction
    external/<libname>/    — clone external libs here for Stream 4 to pick up
    synthetic/             — drop synthetic JSON files here for Stream 5
```

## Manifest schema

```json
{
  "schema_version": 1,
  "charter_version": "v1",
  "computed_at": "2026-05-23T12:00:00Z",
  "corpus_size": {"hephaestus_forge": 432, "apollo_organism": 0, ...},
  "total_examples": 1240,
  "stream_weights": {"hephaestus_forge": 0.30, ...},
  "stream_weights_alarm": null,
  "last_tick_summary": {...},
  "shards": {
    "hephaestus_forge": {
      "path": "agents/talos/corpus/shards/hephaestus_forge.jsonl",
      "examples": 432,
      "weight": 0.30
    },
    ...
  },
  "phase": "Phase 0 — corpus builder only; no training"
}
```

## Per-record schema (JSONL)

Each line in a shard:

```json
{
  "fingerprint": "<16-char content hash>",
  "stream": "hephaestus_forge",
  "weight": 0.30,
  "extracted_at": "2026-05-23T12:00:00Z",
  "function_name": "in_lehmer_band",
  "docstring": "Decide whether...",
  "snippet": "def in_lehmer_band(coeffs, threshold=1.18, dps=30):\n    ...",
  "lineno": 42,
  "body_lines": 18,
  "has_docstring": true,
  "source_path": "prometheus_math/lehmer/in_band.py"
}
```

## Phase 1 data loader expectations

The training-loop owner (likely Rhea) reads `manifest_latest.json`, opens each shard's `path`, and:
1. Applies per-stream sample weights from `stream_weights` (oversample low-weight streams to hit target ratios).
2. Wraps each `snippet` in the prompt template from `agents/talos/training/lora_config.yaml`.
3. Holds out 5% of each stream as eval-loss tracking (separate from the capability eval at `agents/talos/eval/`).
4. Shuffles within stream, then mixes per weight.
5. Trains the LoRA per the YAML spec.

## Why each shard is in its own JSONL file (not one combined file)

- Per-stream ablation: train without a stream by skipping its shard.
- Per-stream weight tuning: re-weight without re-extracting.
- Per-stream growth tracking: shard byte-size = corpus size per stream.
- Dedup: shard-local fingerprint set keeps within-stream duplicates out; cross-stream dedup happens at the loader level if desired.

— Aporia, 2026-05-23
