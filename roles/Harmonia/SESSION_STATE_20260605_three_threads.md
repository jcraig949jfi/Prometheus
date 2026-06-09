# Harmonia — Three-Thread State Snapshot (2026-06-05 cold restart)

**Purpose.** Cold-started Harmonia oriented on the three live multi-model
("swarm") threads and documented where each stands. No experiments launched
this session — all three are *stopped* and this doc is a faithful "where we
left off." Last substrate activity was 2026-05-30; today is 2026-06-05.

**Provenance check done this session:**
- `harmonia/experiments/reasoning_phase0.py` mtime = **May 30 06:12**. The two
  legality generators below were built that session (the writeup's §5 "owed"
  framing was superseded same-day per its §5.3 "RESOLVED 2026-05-30" note).
- `harmonia/experiments/test_legality_generators.py` mtime = **Jun 5** — written
  + run by the orientation Explore agent today (Bash-capable). 2494 passing.
  Untracked, low-risk ground-truth validation. Flagged, not buried.
- All of `harmonia/experiments/` is **untracked** (`?? harmonia/experiments/`).
- No Python processes running. Nothing is mid-flight.

---

## Thread 1 — Model Zoo (basis-vs-ladder) — **READY, never run live**

**Goal.** Decide whether reasoning is multi-axis (a *basis*) or a single
monotone rank-1 *ladder*, by running 15–18 stratified LLMs through the R0–R12
reasoning-ladder tier matrix and testing whether a multi-axis model predicts
**held-out-family** accuracy better than rank-1. This is the binding test all
four frontier reviewers named; the within-Anthropic trio is too saturated.

**Execution state.** Scaffolding complete, **no live matrix run yet.**
- Inventory DONE (2026-05-29): **18/24 models reachable** across Cerebras, Groq,
  NVIDIA, OpenAI → `zoo_inventory_result.json`.
- Adapter (`zoo_reasoner.make_zoo_reasoner`) DONE; smoke (`zoo_smoke.py`) PASS.
- Runner (`run_zoo_matrix.py`) DONE + **38 offline tests pass**
  (`test_zoo_matrix.py`): resumable JSONL checkpoint, per-provider pacing,
  parse-rate gate, bounded single re-ask, NVIDIA cold-start warmup.
- **No checkpoint/summary on disk** — zero accuracy cells scored. All scaffolding.

**Blockers (operational, not architectural).**
- DEAD: GitHub Models (429), Gemini (429). BLOCKED: DeepSeek (402 balance) —
  not load-bearing for the panel. Live: Groq, NVIDIA, Cerebras, OpenAI.
- Anthropic anchors are the ONLY schema-enforced path; zoo is free-text-JSON →
  parse-loss must ride into factor analysis as a covariate (like C-FORMAT).
- Catalog drift: re-list `/models` immediately before a full run.

**Exact next step.**
```
python harmonia/experiments/run_zoo_matrix.py --dry-run     # offline sanity
python harmonia/experiments/run_zoo_matrix.py --n 3         # LIVE, ~1.2k calls, no anchors
python harmonia/experiments/run_zoo_matrix.py --n 3 --with-anchors --drop-degraded
```
Anthropic-independent for the core panel → **this thread is NOT blocked by the
credit exhaustion that blocks Thread 2.** It can launch now.

**Open design Qs.** Examinee count for legit CDM/MIRT (need ≥8–40; have ~15–18);
NVIDIA cold-start timeouts (mitigation coded, unvalidated live); parse-failure
as covariate; the held-out-family prediction is the decisive metric, not raw acc.

**Key files (all `D:\Prometheus\harmonia\experiments\` unless noted):**
`run_zoo_matrix.py`, `zoo_reasoner.py`, `zoo_inventory.py`, `zoo_smoke.py`,
`test_zoo_matrix.py`, `zoo_inventory_result.json`;
plan = `D:\Prometheus\harmonia\memory\architecture\model_zoo_plan_2026-05-29.md`;
synthesis = `...\reasoning_ladder_frontier_synthesis_2026-05-29.md`.

---

## Thread 2 — Legality over-refusal replication — **CODE-COMPLETE, credit-blocked**

**Goal.** Replicate the log over-refusal gap and run the pre-registered
*dcl-monotonicity* prediction: does Opus 4.8's over-refusal rate scale with the
number of independent domain conditions on the candidate root (abs-clean dcl=1
< log-2arg dcl=2 < log-3arg dcl=3)?

**Code readiness — DONE.**
- Generators all present in `reasoning_phase0.py`: `gen_abs_extra_clean` (dcl=1,
  a≤b only), `gen_log_extra` (dcl=2), `gen_log_extra_3arg` (dcl=3 cubic, unique
  in-domain root). Built May 30.
- `test_legality_generators.py`: **2494 passed** across binding seeds
  20260530/01/02/03 — ground truth validated by direct substitution + a
  3000-seed uniqueness scan (no multi-root "poisoned" probes). Written/run today.
- `run_legality_replication.py` wired: 3 arms in dcl order, seeds
  **20260601/02/03** hardcoded (no redraw-on-failure), n=40, effort=high pinned,
  Opus 4.8 + Sonnet 4.6, incremental file-write-flush output (kill-safe).
- `morphology.py` emits canonical `over_refused` everywhere (unified 2026-05-30).
- **No code work remains.**

**Blocker.** Anthropic credits exhausted (`bmf822eb9` = 480/480 api-failures).
Need ~**780 calls** (720 arms + 60 R8 confirm); top up to comfortably absorb 800+.

**Attempt ledger.** `bad3ay4wk` = the suggestive 4-arm result (1→2→7→15 climb,
0 api-fail). `b11qt11yt` = output lost to redirect collision. `bmf822eb9` =
credit exhaustion.

**Binding decision rules (pre-registered — do not relax):**
- log REPLICATES ⟺ pooled Opus ≤0.75 AND Sonnet ≥0.95 AND Fisher p<0.01 AND
  ≥80% Opus errors `over_refused`. DIES ⟺ Opus >0.85 OR p>0.05 OR per-seed Opus
  range >0.20. Else AMBIGUOUS.
- dcl-monotonicity CONFIRMS ⟺ Opus(log-3arg) < Opus(log-2arg) < Opus(abs-clean)
  with non-overlapping 95% CIs at each step. FALSIFIES ⟺ log-3arg ≥ log-2arg
  (CI overlap). Else PARTIAL.
- Double dissociation STANDS ⟺ log REPLICATES AND R8 reconfirms Opus>Sonnet at
  p<0.10.

**Exact next step.** Top up Anthropic balance, then from `harmonia/experiments/`:
```
python run_legality_replication.py 40 20260601,20260602,20260603
```
~2–3 h at effort=high; reports per-seed + pooled verdicts to
`legality_replication_result.txt`.

---

## Thread 3 — Icarus ladder climber — **STOPPED at cycle 013 (R5), transient crash**

**Goal.** Self-improving harness that climbs Harmonia B's reasoning ladder by
proposing/applying/testing code diffs to a sympy reasoner; **every cycle emits a
typed training object** (failure class, improvement kind, load-bearing lens). It
is failure-to-representation instrumentation, NOT a synthetic reasoner.

**Tier state (from state JSONs).** Currently passing **R3**; target **R5**;
iteration **n=13**; last stable cycle **012** (2026-05-29T12:07, sp.cancel() +
explicit singularity tracking, 100% train+holdout on R3). 3 open debts (float
PolynomialError crash; symbolic-parametric domain guard; reasoner echoes
excluded_value instead of independently verifying).

**Daemon status.** STOPPED — no pid file, no running process. Last activity
2026-05-29T19:11.

**Why cycle 013 parked.** `diff_apply_failed`, but NOT the edit interface —
Generator + Diagnostician + Integrator all returned non-JSON with
tokens_used=0/cost=0 → an **API/connector timeout**, pre-panel. The patcher
never received a diff.

**R5 wall fixes — landed, barely tested.** Last two commits (f82cfabe, 38df7944)
fixed the three real R5 blockers: blind Generator (source truncated 6k→30k),
read-only clone (lineage chmod), edit-interface mismatch (full-file write mode
bypassing unified-diff). Cycle 012 stable came AFTER the fixes; cycle 013 was the
first R5 re-attempt under full-file mode but crashed on the connector event
before exercising it. **So the fixes are effectively unvalidated against a real
R5 attempt.**

**Exact next step.**
```
python D:\Prometheus\agents\icarus\daemon.py --once     # diagnose the connector crash, retry R5
# then, if clean:
python D:\Prometheus\agents\icarus\daemon.py --loop --interval 90
```
First clean R5 cycle either advances target→R6 or captures a real
last_failure_direction (the typed object) for cycle 015's Generator.

**State files.** `agents/icarus/state/` (iteration_n, tier_target,
tier_currently_passing, last_stable_cycle, last_failure_direction,
debt_ledger, kill_clusters, training_stream.jsonl). State + cycles untracked.

---

## Cross-thread read

- **Two are launchable now; one is hard-blocked.** Zoo (Thread 1, Anthropic-
  independent) and Icarus (Thread 3, daemon-only, has its own daily cap file)
  can run immediately. Legality (Thread 2) waits on an Anthropic top-up.
- **All experiment + Icarus state is untracked.** A commit of the May 30 zoo +
  legality scaffolding (and a decision on whether Icarus cycle dirs belong in
  git) is owed independent of any launch.
- **Discipline anchors that bind here:** background output capture (never
  shell-redirect a bg run — write the result file from Python with per-cell
  flush); the legality decision rules are pre-registered and must not be
  relaxed post-hoc; the zoo's held-out-family prediction (not raw accuracy) is
  the decisive basis-vs-ladder metric.
