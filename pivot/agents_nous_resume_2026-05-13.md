# Nous — Resume Document

**Last activity:** 2026-03-27 20:35 (run `20260327_203534`)
**Status:** COLD (47 days idle as of 2026-05-13). Predates Agora; no telemetry wiring.
**Filed:** 2026-05-13 by Aletheia during orchestrator-design session (chip 3; Hephaestus chip 1, Apollo chip 2).
**Machine assignment:** M4 (per James, 2026-05-13 session).
**Doctrine cross-references:** `pivot/agent_portfolio_and_monitoring_2026-05-12.md` (orchestrator design), `apollo/RESUME.md` (chip 2 template), `roles/PipelineOrchestrator/RESPONSIBILITIES.md` (forge-pipeline role context).

## What Nous does

Combinatorial hypothesis engine. Samples concept triples from a curated 95-concept × 18-field dictionary, biased 80% toward cross-field combinations and weighted by Coeus forge-effect scores when available. Each triple is sent to the NVIDIA API (default model `nvidia/nemotron-3-super-120b-a12b`) with an implementation-focused prompt; the response is scored on Reasoning / Metacognition / Hypothesis-Generation / Implementability dimensions plus a separate novelty classification. High-composite, all-7+ ratings flag `HIGH_POTENTIAL` for downstream Hephaestus forging.

**Designed to run continuously and indefinitely** (`--unlimited`). Default batch size 500 combinations; 2.0s default inter-call delay. Checkpoints every 10 combinations; full resumability via `--resume`. Per-batch output to `agents/nous/runs/<timestamp>/responses.jsonl` (one JSON entry per evaluated triple) plus `rankings.md` (top 50 + full text for top 20).

## Current accumulated state on disk

- **`src/`**: `nous.py` (611 lines, well-structured), `concepts.py` (95-concept dictionary, 4-mechanism type taxonomy: constraint / structure / dynamics / measure), `scorer.py`, `rescore.py`.
- **`configs/`**, **`data/`**: configs + `priority_triples.json` (gap-targeted concept triples injected at front of queue).
- **`runs/`**: ~10 historical run directories, March 24-27. Most recent: `20260327_203534`. Each contains `responses.jsonl`, `rankings.md`, `checkpoint.json`, `meta.json`.
- **`README.md`**: comprehensive operational guide — prompt design, scoring, sampling, pipeline position.
- **`nous.log`**: top-level run log (single file across runs, appended).
- **Coeus integration**: Nous reads `agents/coeus/graphs/concept_scores.json` if present to bias sampling toward forge-productive concepts (3× weight for `forge_effect > 0.3`, 0.3× for `< -0.2`, with Goodhart-indicator demotion).

## Pipeline position

```
NOUS (M4)
  ↓ responses.jsonl  ← v1: file pickup. v2 (proposed): Agora stream.
COEUS (causal analysis)
  ↓ enrichments + concept_scores.json
HEPHAESTUS (M3 once revived)
  ↓ forged tools + ledger
NEMESIS (adversarial testing)
  ↓ adversarial_results.jsonl
COEUS (dual graph, Goodhart detection)
  ↓ updated concept_scores.json
NOUS (adjusted sampling weights) ← full cycle
```

**Hephaestus depends on Nous.** Per the chip-3 sequence note in `pivot/agent_portfolio_and_monitoring_2026-05-12.md` §2: Nous needs to be alive before Hephaestus has anything to forge.

## Dependencies for revival

| Requirement | Where | Risk |
|---|---|---|
| `NVIDIA_API_KEY` env var | `.env` or shell export | **Blocker if missing.** Script `sys.exit(1)` at line 465 if unset. |
| `openai` Python package | pip | Standard. |
| `concepts.py` dictionary | `agents/nous/src/concepts.py` | Present; 95 entries. |
| `agents/coeus/graphs/concept_scores.json` | Coeus output | **Optional.** Nous falls back to uniform weights if absent. Coeus is COLD; weights will be 1.0× until Coeus revives. |
| `agents/nous/data/priority_triples.json` | Manual curation | **Optional.** Empty list if absent. |
| Agora client lib (post-instrumentation) | `agora/` at repo root | **Optional after patch** — instrumentation is defensive; Nous runs without it. |
| Redis at `192.168.1.176:6379` | M1 | Confirmed reachable from M4 (2026-05-13). |

## Why it stopped — UNKNOWN, fits the broader April-25-pivot pattern but earlier

The March 27 last-run timestamp is *before* the April 25 attention pivot that paused most other agents. Nous probably stopped earlier because:

1. **Coeus dependency stalled** (most likely). Nous's Coeus-weighted sampling depends on Coeus's `concept_scores.json`. If Coeus stopped emitting fresh scores, Nous keeps running with stale weights, but the *value* of running drops — every batch produces the same gap-targeted suggestions. James probably stopped it when the feedback loop went silent.
2. **API key rotation / quota exhausted**. NVIDIA free-tier quota or expired key.
3. **Hephaestus backlog** (per `roles/PipelineOrchestrator/HEALTH_MONITORING_SCRIPTS.md` §2 "Backlog Interpretation"): Nous response queues over 1000 unprocessed → "Critical backlog; immediate intervention needed." If Hephaestus fell behind, James may have stopped Nous to let Hephaestus catch up.

Each hypothesis is under 10 min to test:
- (1) `ls -lat agents/coeus/graphs/concept_scores.json` — check mtime
- (2) Try a single API call with current key
- (3) Count entries in latest `responses.jsonl` vs Hephaestus's ledger.jsonl entries

## What 10 minutes of attention would unblock

1. Check `NVIDIA_API_KEY` is set; verify with a probe call.
2. `cd C:\Prometheus && python agents/nous/src/nous.py --n-combos 5 --delay 2.0` — small smoke test.
3. If 5/5 combinations score successfully, the loop works. Launch `--unlimited` and detach.

## What 30 minutes would unblock

Above plus:
- Apply the Agora instrumentation patch (see `pivot/nous_instrumentation_patch_2026-05-13.md` or the inline edit landed in this session). Confirms heartbeats appear in Redis `agent:Nous`.
- Verify HIGH_POTENTIAL events arrive on `agora:discoveries` stream (read via `python -m agora.helpers tail_sync agora:discoveries`).
- Check Coeus weights file age; if stale (> 7 days), launch Nous with `--no-coeus-weights` to fall back to uniform sampling.

## Revival paths

**Path A — minimal restart on M4.** Validate API key, smoke test 5 combos, launch `--unlimited --delay 2.0` in a Windows Terminal tab. Effort: 10 min.

**Path B — Path A + Agora instrumentation.** Apply nous.py patch (heartbeat + STATUS.json + HIGH_POTENTIAL stream emit + warn on API failure), confirm telemetry visible in `pivot/portfolio_STATUS.md`. Effort: +20 min after Path A.

**Path C — Path B + cross-machine handoff to Hephaestus.** Push HIGH_POTENTIAL combos to a new `agora:forge_candidates` stream instead of (or in addition to) `responses.jsonl`. Hephaestus on M3 consumes via consumer group. This is the architectural payoff that makes Redis-as-fabric earn its keep. Effort: ~1 session, requires Hephaestus consumer-side code.

**Recommended:** Path B for v0 (this session's deliverable). Path C after Hephaestus revives on M3.

## How this fits the orchestrator framework

Per `pivot/agent_portfolio_and_monitoring_2026-05-12.md` §4:

```yaml
# In M4's schedule.yaml (to be created)
continuous_daemons:
  - id: nous_combinatorial
    machine: M4
    service_unit: nous.service (Windows scheduled task initially)
    entry_point: python agents/nous/src/nous.py --unlimited --delay 2.0
    restart_policy: on-failure
    health_check: agent:Nous Redis hash, last_heartbeat age < 5min
    journal: agents/nous/runs/
    checkpoint_cadence: every 10 combinations (~30-60s)
```

**Nous's quickness is the opposite property from Apollo's slowness.** Nous emits one event per ~2-5 seconds (per API call + 2s delay). The monitor's 60s heartbeat cadence is plenty; per-combination events go to streams, not the dashboard digest. Backlog tracking remains crucial: a 1000-deep Nous queue with no Hephaestus consumer is wasted API credits.

## What to monitor (for the portfolio dashboard)

Real-time signal the portfolio monitor needs from Nous:
- Run name + start time
- Combinations completed this run
- Last `HIGH_POTENTIAL` event (concepts + score)
- API failure rate (last 10 calls)
- Current model + delay setting
- Unique triples processed (vs total in run dir's responses.jsonl)
- ETA: roughly `(remaining_in_batch * (delay + api_latency))` seconds

Nous writes `agents/nous/STATUS.json` every 10 combinations and mirrors the same dict to Redis hash `agent:Nous`. Cross-machine readers (M1 monitor daemon) read Redis only — no filesystem mount needed.

## Open questions

- **Should Nous gate on Hephaestus backlog?** If Hephaestus has >500 unforged responses, Nous keeps spending API tokens generating things that won't get forged. Worth adding a "pause when backlog > threshold" check, but that requires Hephaestus to be emitting backlog state to Agora.
- **API key sharing across machines.** Once Hephaestus revives on M3 with its own NVIDIA calls, both M3 and M4 use the same key. Quota interaction needs thought — share a quota-tracker via Agora, or accept that M4-Nous and M3-Hephaestus may both hit rate-limits independently?
- **Coeus revival precedes Nous's full value.** Nous runs without Coeus but loses the forge-feedback loop. Coeus is chip 4 candidate; if Aporia gets to it before Nous launches, Nous launches with weighted sampling intact.

## NOTES FROM JAMES

(Pre-stubbed. Add commentary here when reviving.)

## Next chip after Nous

**Coeus** (`agents/coeus/`). Reason: Nous's full value depends on Coeus's forge-effect scores; without Coeus, Nous samples uniformly and the feedback loop is open. Coeus is also dormant (~April 25 pivot pattern expected). Chip pattern same: locate, survey state, write RESUME, update portfolio index.

After Coeus: Cartography (largest dormant corpus), Ignis, Rhea, then the remaining `agents/` directories whose state is currently unknown.
