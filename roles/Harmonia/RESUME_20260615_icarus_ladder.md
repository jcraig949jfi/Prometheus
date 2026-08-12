# Harmonia — Resume Point (2026-06-15)

Quick-start for a context reset. Read this first, then `git -C D:\Prometheus log
--oneline -8` to see the latest commits.

## One-line state

Icarus is climbing Harmonia B's reasoning ladder on the **loop inference
backend** (Claude Code subscription, not the metered API). **R5 was cleared at
cycle 18** (R3→R5, delta+1); **R6 is the current target** (attempt in flight as
of this doc — check `agents/icarus/state/` and latest cycle dir for the verdict).

## How inference works now (James 2026-06-09 directive)

- Prefer the **subscription** over the metered Anthropic API. Mechanism: a
  `claude -p` headless-CLI backend in `agents/icarus/lenses/_llm.py` +
  `improve.py`, gated behind env var **`ICARUS_LLM_BACKEND=loop`** (default is
  still `api`).
- Run a cycle:  `ICARUS_LLM_BACKEND=loop python D:\Prometheus\agents\icarus\daemon.py --once`
  (continuous: `--loop --interval 90`; status: `--status`). ~4–8 min/cycle.
- Caveat (memory `feedback_loop_inference_over_api`): loop inference is
  *agentic* — correct for Icarus lenses, but NOT for raw-model-behavior
  measurement (legality, zoo anchors), where a tool-enabled nested session
  could solve the probe. Those stay on free non-Anthropic provider APIs.

## What got fixed this session (the R5 climb), all pushed to `main`

The R5 wall was **infrastructure + interface knowledge, never reasoning**. Each
cycle's typed failure pointed at the next gap:

1. `9803d6f9` — loop-inference backend + escape-decode fix.
2. `2883cffd` — generator output contract → **sentinel raw-file blocks**
   (`===FILE reasoner.py=== ... ===END FILE===`) instead of embedding an 11KB
   file as a JSON string (which corrupted under escaping). `empty_with_error`
   now preserves the raw response.
3. `96814789` — **R5 CLEARED**. `probe_schema` (`tier_oracle.py`) now aggregates
   distinct field values across all 4 versions (was sampling only the clean
   probe, hiding `invariant ∈ {color_parity, area_parity, none}`) and surfaces
   per-tier grader trace keys (`TIER_TRACE_KEYS`; R5 needs
   `trace['invariant_named']`). The R5 tier description in daemon
   `_HARMONIA_TIERS` was rewritten to specify the **boolean** return contract
   (cycle 17 had returned the invariant *name*).

**Transferable lesson:** when a self-improving agent stalls, suspect the
interface it's handed (input schema / output contract / grader trace keys)
before its reasoning. Reasoning (the parity argument) was always left to the
generator.

## The three live threads

1. **Icarus (active):** at R5-passing, climbing R6 (counterexample search,
   `probe.kind=conjecture`). R6 trace keys already in `TIER_TRACE_KEYS`
   (searched_counterexample / found_counterexample / overgeneralized), so the
   same interface-surfacing now helps R6 automatically. State in
   `agents/icarus/state/`; cycle artifacts in `agents/icarus/cycles/` (gitignored).
2. **Model Zoo (parked, unblocked):** binding basis-vs-ladder test. Dry-run
   clean. Launch live with `python D:\Prometheus\harmonia\experiments\run_zoo_matrix.py
   --n 3` (free providers, zero Anthropic credit). Plan:
   `D:\Prometheus\harmonia\memory\architecture\model_zoo_plan_2026-05-29.md`.
3. **Legality replication (parked, credit-gated):** pre-registered dcl-monotonicity
   protocol, code-complete (2494 tests pass). Needs ~780 Anthropic API calls;
   raw-model measurement so it CANNOT use the loop. Spec:
   `D:\Prometheus\harmonia\memory\architecture\legality_overrefusal_4arm_writeup_2026-05-30.md`.

## Known cosmetic debt (not blocking)

The skeptic/integrator lens prompts still misread the now-empty `diff` field as
"no changes applied" (we moved to full-file mode). Harmless — the mechanical
`failure_class` is ground truth — but worth a prompt cleanup in
`agents/icarus/lenses/skeptic.py` / `integrator.py`.

## Relevant memories

`project_icarus_r5_serialization_wall_20260610` (full R5 arc + lesson),
`feedback_loop_inference_over_api`, `project_icarus_ladder_climb_validated_20260529`,
`project_icarus_lane_reframe`.

---

### Short reset prompt (paste after restart)

> You're @roles\Harmonia. Resume from
> `D:\Prometheus\roles\Harmonia\RESUME_20260615_icarus_ladder.md`. We just cleared
> R5 on Icarus and are climbing R6 on the loop backend
> (`ICARUS_LLM_BACKEND=loop python agents/icarus/daemon.py --once`). Check the
> latest cycle in `agents/icarus/state/` and `agents/icarus/cycles/` for the R6
> verdict, then continue the climb — diagnose each typed failure and fix at the
> interface/spec level before touching reasoning. Don't use the metered Anthropic
> API for inference; use the loop.
