# Kill-Replay Log — Generator #5

**Generated:** 2026-04-20T23:05:33.093068+00:00
**Source:** `docs/prompts/gen_05_attention_replay.md` @ commit `ac354b26`
**Runner:** Harmonia_M2_sessionA_20260420

## Purpose

Every killed F-ID is terrain. When a new projection lands in the catalog, every killed F-ID becomes a re-test candidate against that projection. This log records the initial seeding and the ongoing audit trail.

## Summary

- **Killed / artifact F-IDs inspected:** 13
- **Candidate (F, P) pairs enumerated:** 443
- **Tasks seeded this tick:** 30
- **Per-F-ID guarantee:** ≥ 1 candidate per killed F-ID

## Scoring function (v1)

```
score = adjacency + 2 * type_novelty + 1.5 * recency
```

- **adjacency** — count of live specimens for which this projection resolves at +1 or +2 (higher = more validated lens).
- **type_novelty** — 1 if this projection's type does not appear in the F-ID's already-tested set.
- **recency** — 1.0 if P-ID ≥ 100 (added post-sessionA 2026-04-17), 0.5 if P-ID ≥ 28, else 0.

**Known concentration:** P023 (Rank stratification) dominates top-of-queue because it resolves 9 live specimens. The per-F-ID guarantee ensures every killed F-ID still gets a replay slot even when P023 saturates; the Map-Elites meta-allocator (#1) will eventually diversify by enforcing behavior-cell uniqueness in quality-diversity mode.

## Seeded replay tasks (30)

| # | F-ID | P-ID | P type | Score | Task ID |
|---|---|---|---|---|---|
| 1 | F020 | P023 | stratification | 10.00 | `replay_F020_P023_20260420` |
| 2 | F021 | P023 | stratification | 10.00 | `replay_F021_P023_20260420` |
| 3 | F022 | P023 | stratification | 10.00 | `replay_F022_P023_20260420` |
| 4 | F026 | P023 | stratification | 10.00 | `replay_F026_P023_20260420` |
| 5 | F027 | P023 | stratification | 10.00 | `replay_F027_P023_20260420` |
| 6 | F010 | P023 | stratification | 8.00 | `replay_F010_P023_20260420` |
| 7 | F012 | P023 | stratification | 8.00 | `replay_F012_P023_20260420` |
| 8 | F023 | P023 | stratification | 8.00 | `replay_F023_P023_20260420` |
| 9 | F024 | P023 | stratification | 8.00 | `replay_F024_P023_20260420` |
| 10 | F025 | P023 | stratification | 8.00 | `replay_F025_P023_20260420` |
| 11 | F028 | P023 | stratification | 8.00 | `replay_F028_P023_20260420` |
| 12 | F031 | P023 | stratification | 8.00 | `replay_F031_P023_20260420` |
| 13 | F043 | P104 | null_model | 7.50 | `replay_F043_P104_20260420` |
| 14 | F020 | P020 | stratification | 8.00 | `replay_F020_P020_20260420` |
| 15 | F021 | P020 | stratification | 8.00 | `replay_F021_P020_20260420` |
| 16 | F022 | P020 | stratification | 8.00 | `replay_F022_P020_20260420` |
| 17 | F026 | P020 | stratification | 8.00 | `replay_F026_P020_20260420` |
| 18 | F027 | P020 | stratification | 8.00 | `replay_F027_P020_20260420` |
| 19 | F024 | P104 | null_model | 7.50 | `replay_F024_P104_20260420` |
| 20 | F025 | P104 | null_model | 7.50 | `replay_F025_P104_20260420` |
| 21 | F031 | P104 | null_model | 7.50 | `replay_F031_P104_20260420` |
| 22 | F012 | P020 | stratification | 6.00 | `replay_F012_P020_20260420` |
| 23 | F020 | P021 | stratification | 6.00 | `replay_F020_P021_20260420` |
| 24 | F020 | P024 | stratification | 6.00 | `replay_F020_P024_20260420` |
| 25 | F021 | P021 | stratification | 6.00 | `replay_F021_P021_20260420` |
| 26 | F021 | P024 | stratification | 6.00 | `replay_F021_P024_20260420` |
| 27 | F022 | P021 | stratification | 6.00 | `replay_F022_P021_20260420` |
| 28 | F022 | P024 | stratification | 6.00 | `replay_F022_P024_20260420` |
| 29 | F025 | P020 | stratification | 6.00 | `replay_F025_P020_20260420` |
| 30 | F026 | P021 | stratification | 6.00 | `replay_F026_P021_20260420` |

## Per-killed-F-ID candidate summary

- **F010** — 1 replay task(s) seeded: `P023`
- **F012** — 2 replay task(s) seeded: `P023`, `P020`
- **F020** — 4 replay task(s) seeded: `P023`, `P020`, `P021`, `P024`
- **F021** — 4 replay task(s) seeded: `P023`, `P020`, `P021`, `P024`
- **F022** — 4 replay task(s) seeded: `P023`, `P020`, `P021`, `P024`
- **F023** — 1 replay task(s) seeded: `P023`
- **F024** — 2 replay task(s) seeded: `P023`, `P104`
- **F025** — 3 replay task(s) seeded: `P023`, `P104`, `P020`
- **F026** — 3 replay task(s) seeded: `P023`, `P020`, `P021`
- **F027** — 2 replay task(s) seeded: `P023`, `P020`
- **F028** — 1 replay task(s) seeded: `P023`
- **F031** — 2 replay task(s) seeded: `P023`, `P104`
- **F043** — 1 replay task(s) seeded: `P104`

## Epistemic discipline applied

1. **Resurrections are high scrutiny.** Any (killed F, P) that returns +1 or +2 must pass `symbols/protocols/null_protocol_v1.md` claim-class check before promotion, AND manual Pattern 30 gate (gen_06 not yet live).
2. **Kill reinforcement is not waste.** Reinforced kills get logged here as Pattern 13 anchor-growth.
3. **No silent promotion.** Any tier change on a killed F-ID routes through `decisions_for_james.md`.
4. **Pattern 19 applies.** Reopening a kill changes the instrument reading of a prior measurement; provenance block required on any updated F-ID description.

## Audit trail

As replay tasks complete and verdicts arrive, append entries here:

```
### YYYY-MM-DD [task_id]
- Verdict: KILL_REINFORCED | RESURRECTED | INFORMATIVE_NULL
- z-score / effect: ...
- Null used: NULL_*@v* with stratifier
- Pattern 30 gate: CLEAR / WARN / BLOCK
- Action: tensor cell updated / no change / escalated
```

## Composition notes

- **Waiting on #2 null-family** to upgrade each replay from single-null to family-vector.
- **Waiting on #6 pattern auto-sweeps** to replace manual Pattern 30 gate.
- **Waiting on #3 cross-domain transfer** to supply new P-IDs (every new P-ID triggers a fresh replay sweep).

## Version

- **v1.0** — 2026-04-20 — initial seeding under generator pipeline v1.0.

### 2026-04-22 `replay_F010_P023_20260420` (Harmonia_M2_sessionB)
- **Verdict:** INFORMATIVE_NULL
- **z-score / effect:** N/A (projection not category-applicable)
- **Null used:** None (see rationale)
- **Pattern 30 gate:** N/A_KILLED (F010 registered as `killed_no_correlation`; gen_06 retrospective verdict silent-CLEAR-equivalent)
- **Action:** no tensor mutation; task outcome logged as informative-null for gen_05 scoring-function feedback
- **Rationale:** F010 claims a coupling between number-field objects (NF) and Artin representations (Artin). Neither domain carries the EC-specific "analytic rank" concept P023 stratifies on. Re-testing F010 via P023 is a category mismatch — the stratification axis doesn't apply to the specimen's data. The kill is neither reinforced nor overturned by this re-test; the test is simply null-applicable.
- **Compression candidate:** gen_05's scoring function (`adjacency + 2·type_novelty + 1.5·recency`) scored this pair at 8.0 because P023 has high adjacency across EC-side live specimens (9 resolves), but the function does NOT check F-ID-domain ↔ P-ID-applicability compatibility. This is a `LENS_MISMATCH` / `lens_wrong_category` failure at the generator-seeding level (per `harmonia/memory/catalogs/*.md` LENS_MISMATCH candidate discussion). Recommendation: gen_05 scoring v2 should gate on domain-compatibility — e.g., EC-specific stratifications (P023 rank, P024 torsion, P025 CM, P026 semistable) should NOT be seeded against NF/Artin/MF/knot F-IDs unless those F-IDs explicitly declare an EC sub-projection. Similar adjacency-driven mismatches likely affect other seeded replay_F0XX_P023 tasks for killed NF/MF-domain F-IDs (e.g., F022 NF backbone, F026 Artin proof-frontier).

### 2026-04-22 `replay_F012_P023_20260420` (Harmonia_M2_sessionB)
- **Verdict:** KILL_REINFORCED
- **z-score / effect:** N/A (no new computation performed)
- **Null used:** None (see rationale)
- **Pattern 30 gate:** N/A_KILLED (F012 registered as `killed_no_correlation`)
- **Action:** no tensor mutation
- **Rationale:** F012 is a Pattern-19 kill — the original |z|=6.15 Möbius bias at g2c aut groups did NOT reproduce under clean n=66158 measurement (max|z|=0.39 under μ, 0.52 under λ, p ≈ 0.6-0.7). The kill isn't "a specific stratification ruled out a real effect"; it's "the original observation was never reproducible." Re-testing under P023 rank stratification cannot resurrect a claim whose raw aggregate measurement already falsified the original z-score. Category-applicability note: genus-2 curves do have Jacobian Mordell-Weil rank, so P023 is partially applicable (unlike the F010 / NF-Artin case); but partial applicability doesn't matter when the underlying claim is a Pattern-19 stale-measurement kill.
- **Pattern distinguishing this from F010 / category-mismatch INFORMATIVE_NULLs:** F010 was INFORMATIVE_NULL because P023 doesn't apply to the NF-Artin domain at all (true category mismatch). F012 is KILL_REINFORCED because P023 DOES partially apply (via Jacobian rank) but the underlying Pattern-19 kill is orthogonal to projection-choice. These are two distinct failure modes for replay tasks; gen_05 v2 should distinguish them:
  - `INFORMATIVE_NULL(category_mismatch)` — projection not applicable to specimen domain; test null by construction.
  - `KILL_REINFORCED(pattern_19_orthogonal)` — kill is measurement-level (claim didn't reproduce); projection choice doesn't matter.
