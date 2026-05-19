# Argos — PROBLEM_LENS_CATALOG@v1 Expander (Harmonia child)

**Machine:** M2
**Role:** the many-eyed Panoptes of the math corpus — extends per-problem lens
catalogs under `PROBLEM_LENS_CATALOG@v1`.
**Source of truth (code):** `D:\Prometheus\harmonia\agents\argos\daemon.py`
**Source of truth (base class):** `D:\Prometheus\harmonia\agents\_base.py`

---

## Why Argos exists

The Prometheus north star is *compressing coordinate systems of legibility,
not laws* (`C:\Users\James\.claude\projects\D--Prometheus\memory\user_prometheus_north_star.md`).
A problem becomes legible only when enough independent lenses have been
laid over it that their disagreement reveals its compression direction
(`D:\Prometheus\harmonia\memory\methodology_multi_perspective_attack.md`).
The anchor catalogs — Lehmer 28 lenses, Collatz ~18, P vs NP ~12 — exist
but the bulk of the open-problem corpus has no fingerprint yet.

Argos is the agent whose only job is to keep accreting that fingerprint.
For each problem he picks the next 3–5 unapplied lenses, seeds a
multi-perspective-attack scaffold, and after results land records the
`map_of_disagreement` vs `coordinate_invariant` vs `durable` verdict.

---

## Loop trigger

Rotation-driven. The orchestrator at
`D:\Prometheus\scripts\harmonia_loop.py` cycles Phylax → Sophia → Iris →
Argos → Telos, one tick per invocation, suitable for
`/loop 4m python scripts/harmonia_loop.py`. Argos does **not** self-cron.

---

## Per-tick contract (MVP)

1. **Parse the open-problem corpus.** Read
   `D:\Prometheus\aporia\docs\gemini_research_queue\queue.jsonl` if present
   (line-delimited JSON with id/title/prompt/tier). Otherwise scan
   `D:\Prometheus\aporia\` for open-problem markdown files at depth ≤ 3
   and the per-domain `questions.jsonl` files plus the anchor catalogs
   under `D:\Prometheus\harmonia\memory\catalogs\`.
2. **Parse the lens shelf.** Extract operator names from
   `D:\Prometheus\harmonia\memory\methodology_toolkit.md` via the regex
   `### \d+\. \`([A-Z_]+@v\d+)\``. Also include the disciplinary stances
   from `D:\Prometheus\harmonia\memory\methodology_multi_perspective_attack.md`
   and any catalogs under `D:\Prometheus\harmonia\memory\catalogs\`.
3. **Score problems by lens-deficit + verdict-mode.** Per-problem state at
   `D:\Prometheus\harmonia\agents\argos\state\lens_history.json`:
   `{problem_id: {applied_lenses: [...], last_verdict: <str|null>}}`.
   Score = `(total_lenses_known - applied_count)` plus a verdict bonus
   (`+3` for `map_of_disagreement`, `+1` for `null`/unknown,
   `0` for `coordinate_invariant` or `durable`). Pick highest.
4. **Propose the next 3 lenses.** From the shelf, pick the 3 unapplied
   lenses heuristically matched to the problem's tier/domain:
   - Tier 1 (cheap): `KOLMOGOROV_HAT@v1` first, then `CRITICAL_EXPONENT@v1`,
     then `MDL_SCORER@v1`.
   - Tier 2+ (deep): disciplinary stances from the multi-perspective
     methodology — dynamical-systems, information-theory,
     renormalization-group, adversarial-empirical, mathematical-physics —
     in that lexical order.
   Deterministic: ties broken alphabetically.
5. **Emit the catalog draft.** Write
   `D:\Prometheus\harmonia\agents\argos\artifacts\lens_catalog_<slug>_<utc>.md`
   containing problem id/title/tier, applied-lenses list with verdict per
   (from state), proposed next-3 lenses with one-paragraph specs each
   citing the toolkit file:line, multi-perspective-attack scaffold (5
   disciplinary stances + forbidden-move constraints stubs), and a
   "next step" line — a Pythia DR prompt sketch for primary-literature
   lens fingerprint.
6. **Optional Pythia DR seed (if available and not dry_run).** Enqueue
   ONE DR request per tick max via `self.pythia_enqueue_dr(...)` —
   title `"Argos lens fingerprint: <problem title>"`, prompt = the
   multi-perspective spec from the artifact, `priority=5`, `tier='T5'`.
   Track in state key `dr_seeded`.
7. **Update state.** Append the proposed lenses to
   `lens_history[<problem_id>].applied_lenses` so they're not re-proposed
   next tick. `last_verdict` stays unchanged until a human / conductor
   updates it.
8. **Backlog self-gen** when every queue problem already has every shelf
   lens applied. Argos uses DeepSeek to propose 5 fresh open problems
   from an undercovered subfield with primary-source pointers and writes
   them to `pending_problem_seeds_<utc>.md`. Argos **never** modifies
   `D:\Prometheus\aporia\docs\gemini_research_queue\queue.jsonl` or any
   catalog file directly.
9. **Anti-reward-capture selection.** Two-problem ties resolved by:
   `map_of_disagreement` > `null` > `coordinate_invariant`. The tiebreaker
   decision is logged.
10. **Telemetry.** `self.log_work("argos_tick_complete", ...)` and the
    base-class heartbeat.

Return: `{problem_id_processed, lenses_proposed, dr_seeded,
artifacts_written, errors, backlog_remaining, ...}`.

---

## Backlog sources

Argos is **queue-driven** (Aporia's open-problem queue is the inbox). The
self-generated backlog only fires when every known problem has every
known lens applied — a state we don't expect to reach often, so the
DeepSeek-driven proposal artifact stays a propose-only artifact for the
conductor to triage into Aporia.

---

## Anti-reward-capture safeguard

Argos's selection policy is explicitly **anti-greedy**: a problem whose
last verdict was `map_of_disagreement` (the highest-information case)
gets a `+3` bonus over a problem whose lenses all agreed
(`coordinate_invariant`, `durable`). This biases lens accretion toward
the genuinely contested problems. Without the bonus, Argos would prefer
"clean" problems with thin fingerprints — the reward-signal-capture
failure mode (`feedback_autonomous_when_idle.md`,
`feedback_self_dissent.md`).

---

## Constraints

- **No `.env` / key-file reads** — use `keys.get_key()` via the base class.
- **Absolute paths only** (`D:\Prometheus\...`) in all artifacts and prose.
- **Graceful degradation** — DeepSeek, Redis, Postgres, missing toolkit /
  queue / catalog files must not crash the tick.
- **No catalog or queue edits.** Argos only proposes via artifacts under
  `D:\Prometheus\harmonia\agents\argos\artifacts\`. The conductor (or a
  human) promotes proposals into
  `D:\Prometheus\harmonia\memory\catalogs\<problem>.md`.
- **One DR per tick maximum** — Pythia's 20/day external budget is the
  rate limit; Argos defers to it.

---

## File map

- Code: `D:\Prometheus\harmonia\agents\argos\daemon.py`
- Charter: `D:\Prometheus\harmonia\agents\argos\CHARTER.md` (this file)
- State: `D:\Prometheus\harmonia\agents\argos\state\*.json`
  - `lens_history.json` — per-problem applied-lens list + last verdict
  - `dr_seeded.json` — list of `{problem_id, queue_row_id, ts}`
- Artifacts: `D:\Prometheus\harmonia\agents\argos\artifacts\*.md`
  - `lens_catalog_<slug>_<utc>.md` — per-tick catalog drafts
  - `pending_problem_seeds_<utc>.md` — self-gen backlog (rare)
- Base class: `D:\Prometheus\harmonia\agents\_base.py`
- Rotation orchestrator: `D:\Prometheus\scripts\harmonia_loop.py`

---

**v0.1** — 2026-05-17 — initial MVP charter. One real catalog draft per
tick, optional Pythia DR seed, propose-only on catalogs/queue.
Anti-reward-capture: `+3` bonus for `map_of_disagreement` problems.
