# Null-Family Catalog

**Status:** v1.0 — shipped with generator gen_02 (2026-04-20) under
`docs/prompts/gen_02_null_family.md`.

**Companion runner:** `harmonia/runners/null_family.py`
**Companion schema:** `SIGNATURE@v2` — `harmonia/memory/symbols/SIGNATURE_v2.md`
**Companion discipline:** `symbols/protocols/null_protocol_v1.md`

---

## Purpose

Converts "the null" into "the null family." Every +1 or +2 cell is now
labelled by an *invariance vector* across a family of null operators,
not a single z-score against a single counterfactual. Discordance
between family members IS information (Pattern 21 diagnostic).

---

## Family members (promoted 2026-04-20)

| Symbol | Type | Class 1 | Class 2 | Class 3 | Class 4 | Class 5 | Purity |
|---|---|---|---|---|---|---|---|
| `NULL_PLAIN@v1`    | operator | applies | applies | applies | N/A | N/A | pure, seeded |
| `NULL_BSWCD@v2`    | operator | applies | applies | applies | N/A | N/A | pure, seeded |
| `NULL_BOOT@v1`     | operator | applies | applies | applies | N/A | N/A | pure, seeded |
| `NULL_FRAME@v1`    | operator | N/A | N/A | N/A | **required** | N/A | pure, seeded |
| `NULL_MODEL@v1`    | operator | sometimes | rarely | rarely | sometimes | N/A | pure, seeded |

Class definitions live in `null_protocol_v1.md §Claim classes`.

---

## Roles within the family

| Symbol | Question the symbol answers |
|---|---|
| `NULL_PLAIN@v1` | Is the observed statistic distinguishable from a completely shuffled universe? (Baseline coarse; most likely to report "signal.") |
| `NULL_BSWCD@v2` | Is there within-stratum structure after preserving the stratifier's marginal? (Tests whether the claim is a within-stratum pairing.) |
| `NULL_BOOT@v1` | Is the statistic stable under sample-variance perturbation of the same frame? (Tests estimate reliability, NOT pairing.) |
| `NULL_FRAME@v1` | Is the claim still present after correcting for the construction bias of the sample? (Only Class-4-appropriate null.) |
| `NULL_MODEL@v1` | Does the observed statistic match a specific theoretical distribution, or deviate from it? (DURABLE = rejects model.) |

---

## Pattern 21 discordance triggers

The runner computes `discordance_flag: true` iff:

1. **Sign flip** across applicable nulls (one positive z, one negative z
   of comparable magnitude). NULL_MODEL sign is exempted because "reject
   model" is legitimate negative-z semantics.
2. **Spread > 10×** in |z| across applicable nulls.

Either condition requires manual Pattern 21 review BEFORE any promotion
to +2@family. See `pattern_library.md` Pattern 21.

**Example** (smoke test, 2026-04-20): synthetic F011-like data yields
PLAIN z=11.99, BSWCD z=0.05. Classic "signal is between-stratum drift,
not within-stratum structure." discordance_flag: true.

---

## Promotion thresholds

Per gen_02 spec §Epistemic discipline:

| Family verdict | Promotion path |
|---|---|
| `M/M applicable at z >= 3, discordance_flag=false` | eligible for +2@family after conductor check |
| `N/M at z >= 3 (N < M)` | flag; conductor sign-off required |
| `M/M at z >= 3, discordance_flag=true` | Pattern 21 review required; not promotable until resolved |
| `no_applicable_nulls` | Class 5 (theorem/identity); verdict semantics differ — not null-tested |
| `rejected` (any applicable null reports |z| < 3) | not promotable |

"+2" continues to mean "resolves under this projection"; "+2@family"
adds "resolves under every applicable member of the 2026-04-20 family."
Mixed cells can exist — e.g., a cell that is +2 under BSWCD at v1 but
not re-run under the family. The re-audit queue clears this over time.

---

## Seed discipline

Per `VERSIONING.md` Rule 4, each null's default seed is pinned:

| Symbol | Default seed | Rationale |
|---|---|---|
| `NULL_PLAIN@v1` | 20260420 | gen_02 promotion date |
| `NULL_BSWCD@v2` | 20260417 | v1 promotion date (carried through v2) |
| `NULL_BOOT@v1`  | 20260420 | gen_02 promotion date |
| `NULL_FRAME@v1` | 20260420 | gen_02 promotion date |
| `NULL_MODEL@v1` | 20260420 | gen_02 promotion date |

Re-runs with the same seed are byte-identical. Per-call overrides (e.g.
`[seed=42]`) appear in the null_spec string inside SIGNATURE@v2.

---

## Re-audit queue (2026-04-20 seeding)

33 eligible non-calibration +1/+2 cells enumerated from tensor v17 at
source_commit 8b37d995. One re-audit task per cell, seeded at priority
`-0.8` (per gen_02 spec §Process step 4) on the Agora queue with
task_type `reaudit_null_family`.

Task payload per cell:
- `spec`: `docs/prompts/gen_02_null_family.md`
- `goal`: `Rerun F<id>:P<id> under null family; produce SIGNATURE@v2`
- `acceptance`: family_result for all applicable nulls; SIGNATURE@v2 record
- `composes_with`: gen_05 (if cell is in attention-replay queue)
- `epistemic_caveats`: claim class must be declared; NULL_FRAME requires
  frame spec

---

## Composes with

- **gen_05 attention-replay on kills** — kill re-tests run the full family;
  resurrections must pass at least majority family.
- **gen_06 pattern auto-sweeps** — Pattern 21 discordance check is
  automated from the family vector (MANDATORY companion).
- **gen_01 Map-Elites (when live)** — `family_verdict` is the quality
  score for probe-cell occupancy.
- **gen_03 cross-domain transfer** — transferred projections inherit
  family discipline.
- **gen_10 composition enumeration** — every null added to the family
  spawns N new compositions to enumerate.

---

## Open items

- Per-frame resamplers for NULL_FRAME@v1 are NOT shipped. `frame_null`
  is a scaffold requiring a per-case `resampler` callable. First
  frames to implement: `lmfdb_r0_d5` (F011 frame), `lmfdb_r4` (F044
  frame). Priority: F044's three +2 cells are PROVISIONAL pending this.
- Per-model samplers for NULL_MODEL@v1 are similarly not shipped. First
  model to implement: GUE first-gap for F011. Target file:
  `harmonia/nulls/models/gue.py`.
- The runner's per-cell statistic is currently caller-supplied. A
  registry of per-F-ID statistic functions (`harmonia/statistics/<F-id>.py`)
  is proposed as follow-up.

---

## Version history

- **v1.0** — 2026-04-20 — initial catalog shipped with gen_02 Tier 1
  first-pass. Four new null operator symbols promoted; SIGNATURE
  schema bumped to v2; runner scaffold + smoke test live; re-audit
  tasks queued on Agora. Per-frame resamplers and per-model samplers
  deferred to follow-up tasks.
