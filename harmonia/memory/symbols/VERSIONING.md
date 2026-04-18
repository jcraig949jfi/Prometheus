# Symbol Versioning Discipline

**Status:** MANDATORY. Non-compliance is a hard failure, not a warning.
**Scope:** every symbol, every reference, every communication that
mentions a symbol.

---

## The five rules

### Rule 1 — Every symbol has a version
Every promoted symbol carries an integer `version` (1, 2, 3, …) and an
ISO-8601 `version_timestamp`. A symbol without both fields fails
promotion. Redis reject.

### Rule 2 — Every reference is versioned
Any reference to a symbol must carry its version: `NULL_BSWCD@v1`, not
`NULL_BSWCD`. Inter-agent messages that cite a symbol without `@v<N>`
are malformed and should be rejected by the receiver. The bare name
`NULL_BSWCD` is allowed ONLY as a discovery-layer query ("which
versions exist?") — never as a call target.

### Rule 3 — Promoted versions are immutable
Once `version: N` ships to Redis, its content is frozen forever. Not
editable. Not amendable. Corrections are always **new versions**, never
rewrites of old ones.

The authoritative bytes of `NULL_BSWCD@v1` on 2026-04-18 must be
byte-identical to `NULL_BSWCD@v1` on 2030-04-18. Anyone computing with
`NULL_BSWCD@v1` gets the same result forever, even if later versions
correct it.

### Rule 4 — Precision is declared
Every symbol's frontmatter includes a `precision:` block that states
numerical precision for all values it emits or references:

- **Constants:** significant figures, error bar form, units
- **Operators:** output dtype, internal representation, deterministic-vs-MC
  with seed
- **Datasets:** row-count exactness, column dtypes, timestamp resolution
- **Shapes:** field dtypes, threshold constants
- **Signatures:** precision per tuple field

A change in precision — *improvement OR reduction* — triggers a version
increment. If v1 reports z to 2 decimals and v2 reports to 4, that is a
new version. If v1 reports to 4 decimals and v2 backs off to 2 because
we discovered the trailing digits were noise, that is still a new
version.

### Rule 5 — Agents detect mismatch and upgrade
When an agent encounters a cached reference to `SYMBOL@v1` and Redis
reports `symbols:SYMBOL:latest = 2`, the agent:

1. Logs the mismatch explicitly (not silently).
2. Inspects the v2 change log in the MD's Version history.
3. If v2 is a compatible extension (additive): upgrades its cached
   reference, reruns the affected calculation.
4. If v2 breaks compatibility with the agent's call signature: the
   agent refuses to upgrade silently and flags a HITL review.

An agent that ignores version mismatches and keeps using a stale
version is producing stale results. Detection is the agent's
responsibility, not the system's.

---

## What the rules guarantee

**Idempotence across time.** `NULL_BSWCD@v1[stratifier=X, seed=20260417]`
on data `D` produces the same output today, next week, next year, and
in 2035. If it was wrong, it stays wrong at v1 — and the correct answer
lives at v2. The history is recoverable because v1 is immutable.

**Idempotence across agents.** Two agents at the same version with the
same input produce the same output. Differences trace to different
inputs or different versions, not to different interpretations of the
same symbol.

**Auditability across sessions.** A finding from six months ago citing
`NULL_BSWCD@v1` can be reproduced exactly by pulling v1 from Redis
(or git blame on that version's MD). No "what did we mean by
block-shuffle back then" ambiguity.

**Compatibility contract.** Semantic versioning is implicit: a
parameter addition that preserves default behavior is a minor bump
(v1 → v2, backward-compat). A default-behavior change or a precision
reduction is a breaking bump (v1 → v2, incompatible — agents must
decide explicitly). We don't expose SemVer fields separately; we
document the break type in the version history and let agents check
it.

---

## File + Redis layout under versioning

### MD frontmatter (mandatory fields)

```yaml
---
name: <NAME>
type: operator | shape | constant | dataset | signature
version: <int ≥ 1>
version_timestamp: <ISO-8601 UTC>
immutable: true                # always true on promoted versions
previous_version: <int | null> # null for v1; integer for v2+
precision:
  # type-specific precision declarations
  # operators: output_dtype, mc_seed, determinism
  # constants: sig_figs, error_bar_form, units
  # datasets: row_exactness, column_dtypes
  # shapes: field_dtypes, thresholds
  # signatures: per-field precision
proposed_by: <agent>@<commit>
promoted_commit: <hash>          # the commit that promoted THIS version
references:
  - <OTHER_SYMBOL>@v<N>          # version-pinned. NO bare names.
  - F<id>@c<short_commit>        # for non-symbol refs, pin by commit
  - P<id>@c<short_commit>
  - Pattern_<n>@c<short_commit>
redis_key: symbols:<NAME>:v<N>:def
implementation: <path::func>@<commit_or_tag>
---
```

Every field except `previous_version` is mandatory. `implementation`
may be `null` (shape/signature symbols have no executable
implementation) but the field must appear.

### Redis key layout

| Key | Type | Mutability | Contents |
|---|---|---|---|
| `symbols:<NAME>:v<N>:def` | STRING | **immutable once written** | Full JSON blob for version N |
| `symbols:<NAME>:v<N>:meta` | HASH | **immutable once written** | Frontmatter for version N |
| `symbols:<NAME>:latest` | STRING | mutable | Current version integer |
| `symbols:<NAME>:versions` | SORTED SET | append-only | All promoted version integers with ISO timestamps as scores |
| `symbols:all` | SET | append-only | All symbol names |
| `symbols:by_type:<type>` | SET | append-only | Names by type (membership only, not version-specific) |
| `symbols:refs:<NAME>@v<N>` | SET | append-only | Symbols that reference this specific version |

Immutability is enforced by `agora.symbols.push`: if the Redis `:def`
for version N already exists with different content, the push fails.
Correction workflow is:

1. Read the current v1 MD.
2. Create a new file capturing v2 (either same filename with v2
   frontmatter, or append-only inside a `<NAME>/` directory — see
   Migration section).
3. Run `push_symbol` with the v2 MD. The v1 keys stay; new `:v2:*`
   keys are written; `:latest` updates.
4. Old references to `@v1` still resolve. New work references `@v2`.

### Discovery layer

An agent that knows only the bare name (e.g. a new instance bootstrapping)
queries:

```python
from agora.symbols import all_versions, check_version, resolve
# List versions
all_versions('NULL_BSWCD')    # [1, 2]

# Resolve specific version
resolve('NULL_BSWCD', version=2)

# Upgrade check (cached version vs latest)
needs_upgrade, latest = check_version('NULL_BSWCD', cached=1)
# needs_upgrade = True; latest = 2
```

`resolve(name)` without a version emits a warning and returns the
latest. Agents that care about reproducibility must always pass
`version=N`.

---

## Communication protocol

### Inter-agent messages

Every mention of a symbol in a WORK_COMPLETE, TENSOR_DIFF, or any
sync-channel message must include `@v<N>`:

✅ `F041a@cf1843656: LADDER@v1[axis=P021@c348113f3, rank=2, corr=0.97]`
❌ `F041a: LADDER[axis=P021, rank=2, corr=0.97]`  ← FAIL: unversioned

Where non-symbol references (F-ids, P-ids, Patterns) carry a commit
short-hash instead of a version number until we retrofit full
versioning on the tensor and catalog (tier 2).

### Human-readable messages

When communicating with a human (project lead), agents relax the
discipline and write English with inline versions only for precision:
"F041a's LADDER shape (v1) shows correlation 0.97." The symbol +
version still appears, just embedded in prose rather than as a call
signature.

### SIGNATURE tuples

The SIGNATURE@v2 schema (supersedes SIGNATURE@v1 which did not include
versions) mandates:

```json
{
  "signature": {
    "feature_id": "F041a@c348113f3",
    "projection_ids": ["P023@c348113f3", "P020@c348113f3"],
    "null_spec": "NULL_BSWCD@v1[stratifier=conductor_decile,n_perms=300,seed=20260417]",
    "dataset_spec": "Q_EC_R0_D5@v1 ∩ rank=2",
    "n_samples": 222288,
    "effect_size": 1.31,
    "z_score": 3.37,
    "precision": {
      "effect_size": "4 sig figs",
      "z_score": "2 decimal places",
      "n_samples": "exact"
    },
    "commit": "4a046a81",
    "worker": "Harmonia_M2_sessionC_U_A",
    "timestamp": "2026-04-18T12:47:00Z",
    "reproducibility_hash": "<sha256 of above>"
  }
}
```

Two SIGNATUREs with identical `{feature_id, null_spec, dataset_spec,
n_samples}` MUST produce byte-identical `(effect_size, z_score)` —
that's idempotence. Drift on that tuple is a bug, not a judgment call.

---

## Migration: retrofit the current seed symbols

The 5 symbols promoted pre-versioning (commit `c98b7ec6`) are now all
rewritten to v1 under the strict schema:
- Added `version_timestamp`, `immutable: true`, `previous_version: null`
- Added `precision:` block
- Retrofitted `references:` to versioned form
- Old Redis keys `symbols:<NAME>:def` are superseded by
  `symbols:<NAME>:v1:def`. During migration, both exist; the unversioned
  keys will be deleted once no reader depends on them.

---

## Failure modes the discipline prevents

**Drift on the same version.** Before: "F011 z_block=10.46" in one
message, "z_block=4.19" in another, both claiming the same audit — but
actually different stratifiers. After: `NULL_BSWCD@v1[stratifier=class_size]`
vs `NULL_BSWCD@v1[stratifier=torsion_bin]` — immediately distinct at
the call site, no ambiguity.

**Silent retroactive changes.** Before: we corrected NULL_BSWCD's
recommended stratifier in-place; all prior citations now silently point
at the corrected version. After: the correction is v2; all prior
citations still resolve to v1 exactly as they were.

**Precision creep.** Before: one report quotes ε₀₁₁ = 31.08; another
quotes 22.90; readers unsure if same estimate or different ansatz.
After: `EPS011@v1 = 22.90 ± 0.78 %` and `EPS011@v1[ansatz=power_law]
= 31.08 ± 6.19 %` are distinct parametrized queries against the same
versioned symbol; results are labeled.

**Bit-rot of dependencies.** Before: an agent's code calls
`block_shuffle()` in `harmonia/nulls/block_shuffle.py`; if that module
changes, old results are no longer reproducible. After: the symbol
pins `implementation: harmonia/nulls/block_shuffle.py::bswcd_null@<commit>`.
The implementation at that commit is what produces `@v1` results.

---

## What versioning does NOT do

- Does not guarantee correctness. `@v1` may be wrong; it is just
  *consistently* wrong everywhere until `@v2` corrects it.
- Does not eliminate disagreement. Two agents running `@v1` on
  different data still produce different outputs — that's the intent.
- Does not replace provenance. The Version history section of the MD
  is still the authoritative narrative of why each version changed.

---

## Enforcement

- `agora.symbols.push` refuses to overwrite an existing
  `symbols:<NAME>:v<N>:def` with different content.
- `agora.symbols.push` rejects symbols missing `version_timestamp`,
  `precision`, or with unversioned references.
- `agora.symbols.resolve(name)` without a version emits a warning.
- Agents reading bare-name references in inter-agent messages should
  log a WARNING (not a silent fallback).

Discipline is enforced at the tooling layer because it cannot be
enforced at the prose layer. An agent composing a message can still
write `NULL_BSWCD` without `@v1` in English; the parser flags it on
ingest.

---

## Version history (of this document)

- **v1** 2026-04-18 — initial discipline established per project lead
  directive "versioning needs to be baked in from day one." Retrofits
  the 5 seed symbols to v1 under strict schema. Tier 1 scope: symbol
  MDs + Redis. F-ID / P-ID / Pattern full versioning deferred to tier 2.
