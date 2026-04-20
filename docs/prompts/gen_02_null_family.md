# Generator #2 — Null-Family Vector per Finding

**Status:** Tier 1 (low infra, days).
**Role:** Filter + Enricher.
**Qualification:** Harmonia session; familiarity with `symbols/protocols/null_protocol_v1.md`.
**Estimated effort:** 2–3 ticks for first implementation; ongoing as new nulls added.

---

## Why this exists

The current substrate records one z-score per cell, under one null. Pattern 21 established that the null is itself a projection: same data can produce z=+∞ under one null and z=0 under another. A finding's real shape is its **survival profile across a family of nulls**, not a single number against a single counterfactual.

Converting "the null" into "the null family" means:

- A +2 cell is labeled by *which* nulls it survived under — an invariance vector, not a boolean.
- Adding a new null retroactively re-audits every prior finding. History is never wasted.
- Discordance between nulls IS information (Pattern 21 diagnostic).
- Promotion thresholds become principled: "survives N of M family members at z ≥ 3."

---

## Infrastructure to build

### 1. Null operator symbols (add to registry)

Currently: `NULL_BSWCD@v2` (block-shuffle-within-stratum).

Add:

| Symbol | Type | Description | Purity class |
|---|---|---|---|
| `NULL_PLAIN@v1` | operator | Pure label permutation. Baseline coarse lens. | pure (seeded) |
| `NULL_BOOT@v1` | operator | Stratified bootstrap with replacement. Preserves marginal; tests sample-variance stability. | pure (seeded) |
| `NULL_FRAME@v1` | operator | Frame-based resample for Class 4 construction-biased samples. Requires sampling-frame spec as param. | pure (seeded) |
| `NULL_MODEL@v1` | operator | Parametric model null. Generates data from a fitted null model; requires model-spec as param. | pure (seeded) |

Each follows `symbols/VERSIONING.md` rules. Each has `purity_attestation` per `long_term_architecture.md §2.1`.

### 2. SIGNATURE@v2 schema extension

Current `SIGNATURE@v1` carries a single `null_spec` + single `z_score`. Extend to `SIGNATURE@v2` with:

```json
{
  ...existing fields...,
  "null_family_result": [
    {"null": "NULL_PLAIN@v1[seed=20260420]", "z_score": 7.63, "p": 1.8e-14},
    {"null": "NULL_BSWCD@v2[stratifier=conductor_decile,seed=20260417]", "z_score": 111.78, "p": 0},
    {"null": "NULL_BOOT@v1[stratifier=conductor_decile,n_boot=1000]", "z_score": 8.92, "p": 4e-19},
    {"null": "NULL_FRAME@v1[frame=lmfdb_r0_d5]", "z_score": "N/A", "reason": "not_class_4"},
    {"null": "NULL_MODEL@v1[model=GUE]", "z_score": -19.26, "reason": "baseline"}
  ],
  "family_verdict": "4/4 applicable nulls at z ≥ 3",
  "discordance_flag": false
}
```

`discordance_flag: true` when the family vector has a sign-flip or a > 10× magnitude spread — a Pattern 21 trigger.

### 3. Re-audit infra

For every cell at `+1` or `+2` today (~50 cells), enqueue a re-audit task under the full family. Results land as `SIGNATURE@v2` records; cells get their family-verdict label.

---

## Process

1. Implement the four new null operators as `computation` symbols. Promote to v1 per `VERSIONING.md`.
2. Extend `SIGNATURE` schema to v2. Old v1 SIGNATUREs remain immutable; new work writes v2.
3. Write a runner: `harmonia/runners/null_family.py` takes `(F, P, dataset, stratifier_override)` and returns the full `null_family_result`.
4. Seed ~50 re-audit tasks on Agora (one per existing non-calibration non-tautology cell) at priority `-0.8`.
5. Wire all future new-finding ingestion through the family runner.

---

## Outputs

- Four new promoted null operator symbols in `harmonia/memory/symbols/`.
- `SIGNATURE@v2` schema document + migration note.
- `harmonia/runners/null_family.py` implementation.
- `~50` Agora re-audit tasks seeded.
- `harmonia/memory/null_family_catalog.md` — the family's members, their claim-class applicability (per `null_protocol_v1.md`), and their roles.

---

## Epistemic discipline

1. **Not every null is applicable to every claim class.** `null_protocol_v1.md` Class 4 refuses `NULL_BSWCD`; Class 5 refuses all nulls. The family-runner records "N/A" with a reason, not a fake z-score.
2. **Discordance > 10× or sign-flip triggers manual Pattern 21 review** before any promotion.
3. **Each null's seed is pinned** per `VERSIONING.md` Rule 4 (precision declared). Re-runs on the same seed byte-identical.
4. **No cell promotes on partial family** without explicit conductor sign-off. "Survived 2 of 4 applicable" ≠ durable.

---

## Acceptance criteria

- [ ] Four new null symbols promoted at v1, visible via `all_symbols()`.
- [ ] `SIGNATURE@v2` MD exists with migration notes.
- [ ] Runner runs on a smoke test (e.g., F011:P020) and produces a populated `null_family_result`.
- [ ] ≥ 50 re-audit tasks visible on queue.
- [ ] Catalog doc shipped.
- [ ] One worked example end-to-end in `kill_replay_log.md` or equivalent (ideally resolving an existing cell from +2 to +2@family).

---

## Composes with

- **#5 attention-replay** — kill re-tests run the full family; resurrections must pass at least majority family.
- **#6 pattern auto-sweeps** — Pattern 21 discordance check is automatic from the family vector.
- **#1 Map-Elites** (when live) — family-verdict is the quality score for probe-cell occupancy.
- **#3 cross-domain transfer** — transferred projections inherit family discipline.

---

## Claim instructions (paste-ready)

> Claim `gen_02_null_family_seed` from Agora. Implement the four new null operators + SIGNATURE@v2 schema + runner + re-audit seeding per `docs/prompts/gen_02_null_family.md`. Commit `harmonia/memory/null_family_catalog.md` and the symbol MDs. Post `WORK_COMPLETE` with counts.

---

## Version

- **v1.0** — 2026-04-20 — initial spec from generator pipeline v1.0.
