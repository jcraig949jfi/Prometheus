# watchers/ — the scored-shadow ledgers

Binding instrument: `pivot/PREREG_watcher_scorecard_2026-08-20.md`
Scorer: `python scripts/watcher_scorecard.py` (add `--run-probes` to execute queued probes).
Run at the start of any session that touches watcher output. Any seat may run it.

Layout (all append-only JSONL):
- `findings/aporia.jsonl`, `findings/shadow_a.jsonl` — typed findings (schema in prereg §2).
  **A watcher session that appended no typed rows produced, for scoring purposes, nothing.**
- `adjudications.jsonl` — execution verdicts only: CONFIRMED / REFUTED / PROBE-FAILED /
  UNRESOLVABLE-BY-EXECUTION. Nobody adjudicates by reading.
- `decoys.jsonl` — Charon registers decoys here BEFORE planting (synthetic-record firewall).
- `metrics.jsonl` — written by the scorecard only. Hand-editing this file is an ATK-007 offense.

`defect_class` values come from `attacks/REGISTRY.md`. Watchers are scored against the
execution ledger, never against each other.
