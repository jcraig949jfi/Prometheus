# Generator #5 — Attention-Replay on Killed Findings

**Status:** ready to claim (Tier 0, no new infra required).
**Role:** producer (see `harmonia/memory/generator_pipeline.md`).
**Qualification:** any Harmonia session.
**Estimated effort:** one tick (~30–60 min for initial seed + audit trail).

---

## Why this exists

Every killed finding is terrain. A kill carves a "not-here" boundary along the projections tested at kill time. When a new projection later lands in the catalog, every killed F-ID becomes a re-test candidate against that projection. Possible outcomes:

- **Kill reinforced** — the new projection doesn't resolve either. Boundary sharpens.
- **Resurrection** — the new projection resolves where the old ones collapsed. The finding becomes live again, possibly with refined description.
- **Informative null** — the new projection collapses in a structured way (e.g., confirms Pattern 13 accumulated-kill axis class).

None of these outcomes require new primary measurement — they reuse existing data through new coordinate lenses. High ROI per compute unit.

This generator maintains a queue of such re-test tasks and a running audit trail.

---

## Inputs

- **Tensor:** `harmonia/memory/landscape_tensor.npz` or Redis mirror via `agora.tensor`. Target rows: every F-ID where `tier ∈ {killed, killed_tautology, data_artifact}`.
- **Projection catalog:** `harmonia/memory/coordinate_system_catalog.md` (42 projections as of 2026-04-19).
- **Tensor update stream:** `tensor:updates` in Redis — gives projection-addition timestamps so we can prioritize "new since last kill."
- **Kill provenance:** kill-commit timestamps embedded in each F-ID's tensor description.

---

## Process

For each killed F-ID `F`:

1. Resolve its current INVARIANCE row. Enumerate `P_tested` = { P : T[F, P] ≠ 0 }.
2. Compute `P_candidates` = catalog ∖ `P_tested`.
3. Score each `P ∈ P_candidates`:
   - **Adjacency:** if P has resolved structurally-similar live specimens (rows in the same topological cluster via `feature_edges`), +score.
   - **Recency:** if P was added to the catalog after F's kill commit, +score.
   - **Type novelty:** if P's type (`stratification` / `preprocessing` / `null_model` / `feature_extraction`) was not represented in `P_tested`, +score.
4. For the top 30% of candidates by score, emit an Agora task.

### Task payload

```python
{
    "task_id": f"replay_{F}_{P}_{yyyymmdd}",
    "type": "attention_replay",
    "feature_id": F,
    "projection_id": P,
    "score": <float>,
    "priority": -1.5 if top_decile else -0.5,
    "qualification": "harmonia_session",
    "dataset_hint": "<resolved from feature's tier + domain>",
    "null_spec_hint": "NULL_BSWCD@v2[stratifier=<class-appropriate>]",
    "notes": "Killed finding re-test. Apply null-protocol claim-class check before any promotion. Pattern 30 gate mandatory.",
}
```

---

## Outputs

- Initial batch of ≥ 30 attention-replay tasks seeded on `agora:work_queue`.
- For each killed F-ID touched, append to its tensor description a `replay_candidates` provenance block listing the (P, score, priority) tuples enqueued.
- New file: `harmonia/memory/kill_replay_log.md`. Sections:
  - Date / tick of seeding
  - F-IDs touched + candidate count per
  - Top-priority candidates with rationale
  - Audit trail: as tasks complete and verdicts arrive, append outcome (`KILL_REINFORCED` / `RESURRECTED` / `INFORMATIVE_NULL`).

---

## Epistemic discipline (hard rules)

1. **A resurrection is HIGH scrutiny.** Apply `symbols/protocols/null_protocol_v1.md` claim-class check before ANY +1 or +2 assignment.
2. **Pattern 30 gate mandatory.** Before reporting a newly-positive correlation on a previously-killed F-ID, run the algebraic-coupling diagnostic. Most "resurrections" on BSD-adjacent F-IDs will fail Pattern 30 and should be reported as such, not retracted later.
3. **Kill reinforced ≠ no news.** Log reinforced kills with the projection that confirmed them — this is terrain, not waste. The `kill_replay_log.md` audit trail is the evidence of Pattern 13 accumulated-kills.
4. **No silent promotion.** Any tier change on a killed F-ID goes through `decisions_for_james.md` before Redis update.

---

## Acceptance criteria

- [ ] ≥ 30 replay tasks seeded and visible via `queue_status()`.
- [ ] Each of the ~14 killed F-IDs (F010, F012, F020–F028, F043) has ≥ 1 candidate scored and either enqueued or explicitly recorded as "no valid candidate."
- [ ] `kill_replay_log.md` created with initial entries.
- [ ] Tensor descriptions updated with `replay_candidates` blocks.
- [ ] Commit message cites this prompt file and lists task count.

---

## Composes with

- **#2 null-family** (when live) — every replay runs the full null family instead of a single null. Upgrades this generator's resolution.
- **#6 pattern auto-sweeps** (when live) — gate for resurrection claims; currently manual Pattern 30 check.
- **#3 cross-domain transfer** — if a new projection originated in another domain, the replay simultaneously tests the transfer claim.
- **Existing `reaudit_10_stratifier_mismatch_cells`** — that task covers the +1-with-wrong-stratifier subset; this generator covers kills-with-new-projections. Different failure modes, same substrate.

---

## Claim instructions (paste-ready)

Paste into a fresh Harmonia session after cold-start restore:

> You are Harmonia_M2_session<X> resuming on Project Prometheus after restore protocol completion. Claim `gen_05_attention_replay_seed` from `agora:work_queue`, or seed it directly per `docs/prompts/gen_05_attention_replay.md` if not yet queued. Produce ≥ 30 Agora tasks following the spec. Commit `harmonia/memory/kill_replay_log.md` + tensor description updates. Post `WORK_COMPLETE` on `agora:harmonia_sync` with task count and top-5 priority re-tests.

---

## Version

- **v1.0** — 2026-04-20 — initial spec. Derived from generator pipeline v1.0.
