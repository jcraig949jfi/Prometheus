# Hephaestus — Resume Document

**Last revived attempt:** 2026-04-02 (last log entry, runs/, hephaestus.log)
**Status:** LUKEWARM (40 days idle as of 2026-05-12). Substantial accumulated state. Revival is structural not from-scratch.
**Filed:** 2026-05-12 by Aporia during chip-away portfolio revival (first chip; Apollo next, then news research).
**Doctrine cross-references:** `project_nous_hephaestus.md`, `feedback_forge_division.md`, `project_forge_bypass_finding.md`, `project_tiered_forge.md` (all in `C:\Users\jcrai\.claude\projects\F--Prometheus\memory\`).

## What Hephaestus does

Hephaestus is the **automated forge for reasoning tool primitives**. It takes scored concept combinations from Nous (e.g. `Category Theory × Sparse Coding × Mechanism Design`), runs them through Coeus's causal-intelligence directive layer, and uses a frontier API (Augment / NVIDIA 397B / configurable) to generate a Python `ReasoningTool` class implementing the combination as deterministic, fast, interpretable code. Five gates filter the output: syntax → imports (numpy+stdlib only) → interface (`evaluate` + `confidence` methods required) → runtime (instantiate + verify output shape) → trap battery (15 traps; must strictly beat NCD compression baseline).

Forge rate ~40%. Default cadence: poll Nous every 5 minutes, process Coeus-priority order, auto-trigger Coeus rebuild + report regeneration every 50 forges. **Designed to run continuously**, not on a cron schedule. Per the user's machine architecture: candidate for continuous daemon on M2 once revived.

## Current accumulated state on disk

- **9 forge versions** at `agents/hephaestus/forge` through `forge_v9`. File counts: 733 / 50 / 333 / 375 / 367 / 2 / 65 / 5 / 15 = **~1,945 forged tools total**.
- **Ledger** at `agents/hephaestus/ledger.jsonl` — **4,905 entries** of attempted forges (both passed → `forge/` and `scrap/`). `ledger.jsonl.bak` backup also present.
- **Novelty scores** at `novelty_scores.json` — cross-forge novelty tracking.
- **Runs directory** with timestamped run logs through 2026-04-02 (forge fired 5+ runs per day on Apr 2 before stopping).
- **Three docs**: `README.md` (architecture overview), `MODEL_COMPARISON_REPORT.md`, `REPAIR_SCORECARD.md`.
- **Source modules** at `agents/hephaestus/src/` — `prompts.py`, `validator.py`, and the orchestrator (entry point TBD-locate; likely `src/hephaestus.py` or similar).

## Direct dependencies — Nous + Coeus

- **Nous** at `F:/Prometheus/agents/nous/` (also missing from earlier orchestrator survey for same `agents/` parent reason). Produces scored concept combinations. Hephaestus polls Nous's JSONL output every 5 min.
- **Coeus** at `F:/Prometheus/agents/coeus/`. Provides causal-intelligence directives + Coeus-priority ranking that biases Hephaestus's queue order.
- **Two separate `forge/` artifacts** also exist at `F:/Prometheus/forge/v2/nous_t2/` and `F:/Prometheus/forge/v3/nous_t3/` — different output stream from a Nous variant; unclear if currently active.

## Why it stopped — UNKNOWN, needs probing

The log just stops on 2026-04-02 at `Calling Augment API (auggie-sdk)...` (one of multiple calls). No error message. Three hypotheses:

1. **Augment API key revoked or quota exhausted.** Augment was the configured model provider per the log (`Using Augment API (force-aggie mode)`). If the API key is no longer valid, the forge stalls on first call.
2. **Nous stopped producing fresh combinations.** If Nous's JSONL hasn't been updated since early April, Hephaestus has nothing to forge and idles silently.
3. **Manual halt during the April 25 attention pivot.** The user pivoted to substrate-vocabulary / Learner work around April 25; possible Hephaestus was deliberately stopped to free compute.

Each hypothesis is testable in <5 min. The actual blocker is one of the three.

## What 10 minutes of attention would unblock

1. Open `agents/hephaestus/src/` and identify the orchestrator entry point (likely a `main()` or `if __name__ == "__main__"` in a file named `hephaestus.py` / `runner.py` / `loop.py`).
2. Check `keys.get_key("AUGMENT")` (or equivalent) returns a valid key. If not, the blocker is hypothesis 1; rotate the key or switch to NVIDIA provider.
3. Check `agents/nous/` last-modified timestamp. If Nous's JSONL hasn't been updated since April, hypothesis 2 applies — need to revive Nous first (separate chip).
4. If both check out, restart the orchestrator process. It will pick up from the ledger and skip already-attempted combinations.

## What 30 minutes of attention would unblock

Above plus:
- Read the `MODEL_COMPARISON_REPORT.md` to confirm the model choice is still optimal in 2026 model landscape (Augment was 2026-spring vintage; may want to switch to a newer 2026 frontier or to a local model on M2).
- Run a single forge-cycle dry-run against a known Nous combination to verify the 5 gates still execute correctly (in case Python deps drifted).
- Confirm the trap-battery NCD baseline file is still where it expects.

## Revival paths (when ready)

**Path A — minimal restart on current machine.** Validate keys + Nous freshness + restart. If everything passes, Hephaestus resumes forging at the same forge_v9 rate. Effort: 10 min.

**Path B — port to M2 continuous daemon** (per machine-architecture plan). Move the orchestrator to M2 as a Windows service or systemd unit. M2's GPU isn't actively used by Hephaestus (the model call is API-side; trap battery is CPU), so VRAM headroom stays for Apollo. Effort: ~1 hour one-time setup, then continuous.

**Path C — bigger refactor before revival.** If the user wants to overhaul the model provider (Augment → NVIDIA → local 4B), refactor `src/prompts.py` and `src/validator.py` for the new provider's call shape. Effort: ~1 day. NOT recommended for chip-away revival; do Path A or B first, refactor later if needed.

## How this fits the orchestrator framework

Once the `agentic_loop.py` per-machine framework is built, Hephaestus is a **continuous daemon registered separately**, NOT a scheduled cron entry. Its schedule.yaml entry would look like:

```yaml
continuous_daemons:
  - id: hephaestus_forge
    machine: M2
    service_unit: hephaestus-forge.service (systemd) OR HephaestusForge (Windows service)
    entry_point: python -m agents.hephaestus.src.hephaestus
    restart_policy: on-failure
    health_check: agora STREAM_MAIN heartbeat every 5 min
    log_path: agents/hephaestus/logs/hephaestus_<date>.jsonl
```

Health check via Agora `STREAM_MAIN` heartbeat: if Hephaestus stops heartbeating for >15 min, M1's portfolio digest flags it the next morning.

## NOTES FROM JAMES

(Pre-stubbed for paste-edit workflow per `feedback_no_hard_tables.md` companion principle. Add commentary here when reviving; this block is the natural entry point for "actually do this" direction.)

## Next chip after Hephaestus

Apollo. The pattern repeats: locate (probably also under `agents/`), survey state on disk, identify blocker, write `agents/apollo/RESUME.md` analogous to this one. Then news research / Cartography. Substrate + Learner stays the 90% focus throughout.
