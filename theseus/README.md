# Theseus — Substrate Generation Engine

A continuously-running Python engine that generates mathematical claims
for sigma to verify, producing typed substrate records at volume.

## What this is

Sigma verifies claims. Theseus generates them. Together they close a loop
sigma cannot close alone: substrate cannot grow without a claim source.

Theseus is structurally generative (combinatorial + bandit + parallel
generators), so it cannot run out of work the way Harmonia and Charon
fan-outs did. The full menu is 40 generator types across 10 families;
five run in parallel per batch; a scoreboard tracks per-generator yield;
a bandit reshuffles the active set every batch.

## Why a separate engine

Sigma is doctrine — load-bearing for every agent that emits typed
records. Mixing claim-generation logic into sigma would couple the
verifier to the generator, breaking the layer separation. Theseus
imports from sigma_kernel and prometheus_math but never writes there.

## Quick start

```
python -m theseus.daemon --batch-hours 1 --generators a1,b5,c1,d1,e1
```

Runs the five v0.1 generators for one hour, journals the batch to
`theseus/journals/BATCH_LOG.md`, and emits records to
`theseus/corpus/<batch_id>.jsonl`.

## Layout

- `CHARTER.md` — design doctrine (read first)
- `inventory.md` — the 40 generator types, build status
- `ROADMAP.md` — current state, next tiers
- `daemon.py` — batch loop
- `config.py` — paths, durations, defaults
- `generators/` — generator implementations + stubs
- `scoring/` — per-generator scoreboard, 7-axis metrics
- `bandit/` — generator selection policy
- `emit/` — record schema, corpus writer
- `journals/` — human-readable batch log + structured batch records
- `tests/` — unit tests for daemon, scoring, generators

## Consumer

The future Ergon Learner (currently paused) is the mediate consumer of
the emitted corpus. Records land in `theseus/corpus/` until Ergon's
ingester is ready.

See `CHARTER.md` for the full design philosophy and Standing Orders.
