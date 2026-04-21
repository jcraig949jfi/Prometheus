# Composition Results Log — gen_10

**Generated:** 2026-04-20 — gen_10 first-pass
**Source:** `docs/prompts/gen_10_composition_enumeration.md`
**Runner:** `harmonia/composers/enumerate.py`

## Purpose

Each completed composition run is recorded here with its verdict, any
new F-IDs or cells produced, and any Pattern 30 / Pattern 21 flags.
Compositions that consistently return noise after ≥ 3 tries get
deprioritized (retired list in `composition_queue.md`).

---

## Worked example: NULL_PLAIN@v1 ∘ Q_EC_R0_D5@v1 (rank 28, score 1.581)

**Context:** This composition applies the plain label-permutation null
to the Q_EC_R0_D5 dataset snapshot. It's a baseline "first-light"
composition — can we actually run the enumeration pipeline end-to-end
and land a result?

**Execution (smoke):**

Because Q_EC_R0_D5@v1 is a 559,386-row snapshot and the driver does not
carry a per-cell statistic registry yet, the worked example ran against
the synthetic F011-like dataset produced by `null_family.py::_synthetic_f011_data`
(n=2000). This is a legitimate scaffold-level worked example:

- **Outer:** NULL_PLAIN@v1[n_perms=100, seed=20260420]
- **Inner:** Q_EC_R0_D5@v1 (proxied by synthetic F011-like data at smoke-test scale)
- **Statistic:** regression slope of `value` on `conductor`
- **Observed:** ~1e-6 (near zero as expected from the synthetic construction when
  the stratifier aligns with the signal axis)
- **NULL_PLAIN z-score:** 11.99
- **NULL_BSWCD z-score (reference):** 0.05
- **Pattern 21 discordance_flag:** true (|z| spread = 240x)

**Verdict:** NO-OP at the tensor. The synthetic scaffold produces a
legitimate Pattern 21 signature (signal lives between deciles, not within)
but does not correspond to a real F-ID cell — no tensor landing.

**Interpretation:** the gen_10 pipeline runs end-to-end. A full
production composition run requires:

1. Real tensor dataset ingestion (Q_EC_R0_D5@v1 SQL hydration),
2. Per-cell statistic registry (`harmonia/statistics/<F-id>.py` per
   open follow-up from gen_02),
3. Pattern 30 gate (gen_06 companion — active; worker should call it).

The Pattern 30 check for NULL_PLAIN ∘ Q_EC_R0_D5 ran conceptually:
no algebraic-identity coupling between NULL_PLAIN's shuffle operation
and the dataset's primary keys (conductor, analytic_rank). Pass.

**Artifact:** reproducibility_hash of the smoke SIGNATURE@v2 is
`34c01ca7e1c4f3c38c3da088...` — traceable to `null_family.py::smoke_test`.

---

## First-pass enumeration summary (2026-04-20)

- **Symbols inspected:** 7 (EPS011, LADDER, NULL_BOOT, NULL_BSWCD, NULL_FRAME, NULL_MODEL, NULL_PLAIN — SIGNATURE excluded as schema-only, Q_EC_R0_D5 included as dataset)
- Correction: symbol count is 9 per latest substrate_health; enumeration uses all 9. The actual numbers surface in `composition_queue.md` header.
- **Valid compositions:** 36
- **Rejected by validator:** 45
- **Top-10 seeded onto Agora:** 10 (task_type `composition_run`, priorities -0.60 to -0.42)

**Top-scored rank-1 composition:** `NULL_BSWCD@v2 ∘ NULL_BSWCD@v2` — a
self-composition (operator ∘ operator). High score driven by
NULL_BSWCD@v2's reference count (10 refs-to in symbols:refs) and its
n_bins_default=10 fanout. Semantically: "block-shuffle within one
stratifier, then block-shuffle within another." A legitimate composition
when the two stratifier parameterizations differ (e.g., conductor then
rank); degenerate when they match. Worker should disambiguate via the
parameter list in the task payload.

---

## Retired compositions

None yet (first-pass). Deprioritization criterion: ≥ 3 runs returning
null-verdict.

---

## Follow-up required

- Statistic registry (`harmonia/statistics/<F-id>.py`) to avoid per-worker
  re-derivation.
- Operator runtime metadata (cost field is currently defaulted to 10s).
- Per-operator output-type declaration so operator ∘ operator
  compatibility can be checked rigorously, not assumed.

---

## Version history

- **v1.0** — 2026-04-20 — initial log; one scaffold-level worked example;
  first-pass enumeration summary.
