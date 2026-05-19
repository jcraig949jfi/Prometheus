# Sophia — Coordinate-System Scout (Harmonia child)

**Machine:** M2
**Role:** closed-loop incarnation of `gen_11` / axis-space invention.
**Source of truth (code):** `D:\Prometheus\harmonia\agents\sophia\daemon.py`
**Source of truth (base class):** `D:\Prometheus\harmonia\agents\_base.py`

---

## Why Sophia exists

The Prometheus north star is *compressing coordinate systems of legibility,
not laws* (`C:\Users\James\.claude\projects\D--Prometheus\memory\user_prometheus_north_star.md`).
The unit of discovery is "invariant under a specific projection" (Pattern 6),
not "universal law." Sophia is the agent that continuously composes new
projections by cross-multiplying:

- the methodology toolkit
  (`D:\Prometheus\harmonia\memory\methodology_toolkit.md` — `K̂`,
  `CRITICAL_EXPONENT`, `CHANNEL_CAPACITY`, `MDL_SCORER`, `RG_FLOW`,
  `FREE_ENERGY`, `GINI_COEFFICIENT`, `CONTROLLABILITY_RANK`, `TT_APPROX_MAP`,
  `CONJECTURE_GENERATOR`, …), with
- promoted `AXIS_CLASS` operators and live frontier specimens
  (`D:\Prometheus\harmonia\memory\frontier_specimen_state.md`).

Survivors become draft symbol candidates with the 5-gate tensor-admission
test pre-filled and a seedable Agora queue task spec.

---

## Loop trigger

Rotation-driven. The orchestrator at
`D:\Prometheus\scripts\harmonia_loop.py` cycles Phylax → Sophia → Iris →
Argos → Telos, one tick per invocation, suitable for
`/loop 4m python scripts/harmonia_loop.py`. Sophia does **not** self-cron.

---

## Per-tick contract (MVP)

1. Parse the operator shelf (`methodology_toolkit.md`) — extract entries
   matching `### N. NAME@vN — …`.
2. Parse the specimen shelf (`frontier_specimen_state.md`) — pick out
   `live_specimen` F-IDs and the calibration anchors F001-F005, F008, F009.
3. Pick one untried `(operator, specimen)` pair, lexicographically smallest.
   Tried pairs persisted at
   `D:\Prometheus\harmonia\agents\sophia\state\tried_pairs.json`.
4. Compose a projection proposal artifact under
   `D:\Prometheus\harmonia\agents\sophia\artifacts\proposal_<OP>_x_<FID>_<utc>.md`.
   Each artifact contains:
   - operator name + frame
   - specimen + current tier
   - proposed scoring procedure
   - **calibration-anchor sanity gate** (mandatory — Sophia's anti-reward-
     capture brake; see below)
   - 5-gate tensor-admission stub (null-calibrated / representation-stable /
     not-marginals / non-tautological / domain-agnostic — all UNFILLED with
     one-line how-tos)
   - "next step" — a seedable Agora queue task spec (described, not seeded
     in MVP; that's Theseus/Charon's wave)
5. Optional DeepSeek enrichment — one short call asking for a concrete
   scorer + sanity check; appended under `## DeepSeek scoring sketch` when
   available. Skipped silently otherwise.
6. Mark the pair tried in state.
7. Telemetry — `log_work("sophia_tick_complete", …)` + heartbeat via the
   base class wrapper.

Return: `{items_processed, artifacts_written, errors, backlog_remaining,
pair_proposed, …}`.

---

## Backlog sources

Sophia is **not** queue-driven. Backlog is the Cartesian product of the
operator shelf and the live-specimen + anchor lists, minus tried pairs.

When the product is exhausted, `self_generate_backlog()` emits a meta-task
artifact suggesting an expansion of `methodology_toolkit.md` — proposal
only, never a direct edit to the toolkit file. DeepSeek may be asked to
draft a candidate new operator entry.

`tried_pairs` is **only** reset when a human sets state-key
`reset_requested = true` at
`D:\Prometheus\harmonia\agents\sophia\state\reset_requested.json`.

---

## Anti-reward-capture safeguard

Sophia is by construction attracted to novel-looking lenses. The explicit
brake: **every proposal MUST include one calibration anchor**
(F001-F005, F008, or F009) with an expected verdict. The selection rule
forces this — the chosen pair is `(operator, specimen)` where specimen is
the lexicographically smallest untried specimen, AND the proposal
artifact pairs the live specimen with an additional anchor for the
sanity-gate column. A proposal whose tool can't agree with known truth
under its own lens is miscalibrated, not insightful — the F043 lesson
codified.

---

## Constraints

- **No `.env` / key-file reads** — use `keys.get_key()` via the base class.
- **Absolute paths only** (`D:\Prometheus\...`) in all artifacts and prose.
- **Graceful degradation** — DeepSeek, Redis, Postgres failures must not
  crash the tick.
- **No scorer execution in MVP.** Sophia only proposes. Execution lands
  in a later wave (Theseus / Charon consume the proposals).
- **Propose-only on `methodology_toolkit.md`.** Sophia never edits it.

---

## File map

- Code: `D:\Prometheus\harmonia\agents\sophia\daemon.py`
- Charter: `D:\Prometheus\harmonia\agents\sophia\CHARTER.md` (this file)
- State: `D:\Prometheus\harmonia\agents\sophia\state\*.json`
- Artifacts: `D:\Prometheus\harmonia\agents\sophia\artifacts\*.md`
- Base class: `D:\Prometheus\harmonia\agents\_base.py`
- Rotation orchestrator: `D:\Prometheus\scripts\harmonia_loop.py`

---

**v0.1** — 2026-05-17 — initial MVP charter. One real proposal per tick,
no scorer execution. Anti-reward-capture: anchor in every proposal.
