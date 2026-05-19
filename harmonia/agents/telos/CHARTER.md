# Telos — Stalled-Specimen Reviver (Harmonia child)

**Machine:** M2
**Role:** negative-space patroller; counter to the human-bottleneck on the live-specimen pile.
**Source of truth (code):** `D:\Prometheus\harmonia\agents\telos\daemon.py`
**Source of truth (base class):** `D:\Prometheus\harmonia\agents\_base.py`

---

## Why Telos exists

The frontier-specimen pile grows. The operator has limited daily attention.
F-IDs at `live_specimen` tier accumulate `last_audit_outcome` dates that
silently slide further into the past, and the implicit signal "nobody is
asking new questions about this specimen" gets misread as "the specimen
is settled." It isn't. It's just stalled.

Telos is the agent that asks the questions the operator stopped having
time to ask. He watches the specimen ledger and the landscape tensor for
cells at `live_specimen` tier with no audit-outcome delta in N days. For
each stalled F-ID he enumerates what HAS NOT been tried — lenses absent
from its `cross_refs`, null families not in its last replay, symbols and
`AXIS_CLASS` operators promoted since its last audit, retractions in
adjacent F-IDs that may reframe its evidence.

Telos files a **revive-task artifact** + (optionally) describes a
seedable Agora queue task. He does not seed himself — proposal only.

When the live-specimen pile is exhausted of stalled rows, Telos patrols
**killed F-IDs** ("would current tooling un-kill F010 NF backbone? F012
Möbius H85?"), because retractions are not always permanent.

When the killed list is exhausted too, Telos files a
`NEGATIVE_SPACE_MAPPED@v1` candidate artifact naming what's been
exhaustively patrolled and proposing the gap as a substrate-primitive
candidate. **Silence is forbidden** — silence is reward-capture
(validating "the specimen is dead" by not asking).

---

## Loop trigger

Rotation-driven. The orchestrator at
`D:\Prometheus\scripts\harmonia_loop.py` cycles Phylax → Sophia → Iris →
Argos → Telos, one tick per invocation, suitable for
`/loop 4m python scripts/harmonia_loop.py`. Telos does **not** self-cron.

---

## Per-tick contract (MVP)

1. **Parse the specimen ledger** — `D:\Prometheus\harmonia\memory\frontier_specimen_state.md`.
   Extract the "Active F-IDs" tables (tier, last_audit_outcome,
   open_questions, cross_refs). Parse the "Killed + data-frontier (stub)"
   sentence for the killed-F-ID list.
2. **Compute stall age** — extract the latest `\d{4}-\d{2}-\d{2}` from
   each `last_audit_outcome`, compute days since. State key
   `stall_threshold_days` (default 14) governs candidacy.
3. **Parse the available-lenses delta** — read
   `D:\Prometheus\harmonia\memory\methodology_toolkit.md` for the
   operator shelf. Read promoted symbols via
   `agora.helpers.substrate_health()` if available, else fall back to
   `D:\Prometheus\harmonia\memory\symbols\INDEX.md`. The "lenses that
   landed since this F-ID's last audit" set is the diff of current
   promoted-symbols vs symbols referenced in its `cross_refs`.
4. **Pick the most-stalled F-ID** (longest stall age). Tiebreak: prefer
   F-IDs whose `open_questions` field is non-empty. Anti-greedy: skip
   `last_picked` (state) — rotate.
5. **Emit a revive-task artifact** at
   `D:\Prometheus\harmonia\agents\telos\artifacts\revive_<FID>_<utc-iso>.md`
   with F-ID + tier + stall-age-days, quoted `last_audit_outcome`,
   list of lenses-not-yet-applied, list of new symbols since last audit,
   list of retractions in adjacent F-IDs (cross-reference
   `D:\Prometheus\harmonia\memory\retraction_registry.md`), proposed
   top-3 next audit actions with priority scores, and a seedable Agora
   queue task spec (description only — do not seed).
6. **Optional DeepSeek probe** (one short call max) for highest-leverage
   next audit; appended as `## DeepSeek next-action sketch`.
7. **If no live_specimen is stalled past threshold**, patrol the killed
   list: pick the lex-smallest killed F-ID not in state key
   `killed_revisited`; emit `killed_revisit_<FID>_<utc-iso>.md`
   (what-was-tried-then / what's-available-now / verdict-sketch).
   Append the F-ID to `killed_revisited`.
8. **If no live AND no killed left**, file a `NEGATIVE_SPACE_MAPPED@v1`
   candidate artifact naming what's been exhaustively patrolled and
   proposing the gap as a substrate-primitive candidate. Never silent.

## Backlog generation

Telos's backlog **is the specimen pile**. `self_generate_backlog()`
returns a sorted list of `(F-ID, stall_days)` candidates (live-specimens
past threshold first; killed-F-IDs after; finally a sentinel item
indicating the `NEGATIVE_SPACE_MAPPED` fallback). Returned to the loop
orchestrator as the work-item view.

## Constraints (hard)

- NEVER read `.env`, `*Key*`, `*secret*`, `*credential*`, `*.env`.
  Use `keys.get_key()` only.
- All file paths in artifacts use absolute paths with drive letter.
- Graceful degradation across Redis / PG / DeepSeek / missing files.
- One revive-task or killed-revisit or `NEGATIVE_SPACE_MAPPED` artifact
  per tick — never a silent tick.
- Do NOT modify `frontier_specimen_state.md` or any tier values.
  Telos only proposes.

## Telemetry

`self.log_work("telos_tick_complete", summary=...)`. Return dict:
`{fid_picked, mode, stall_days, lenses_proposed, artifacts_written,
errors, backlog_remaining}`.
