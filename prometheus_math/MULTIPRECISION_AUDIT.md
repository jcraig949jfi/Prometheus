# Multi-Precision Audit — KillVector v2 Numeric Components

**Date:** 2026-05-07 (contract-change window dispatch)
**Ticket:** T-2026-05-07-T029 (P2)
**Auditor:** Techne
**Verdict:** **PARTIAL gap — 2 of 6 margin units need multi-precision for under-explored regions; deferred to a future contract-change window per ticket scope (audit-only here).**

---

## TL;DR

KillVector v2's `KillComponent.margin: Optional[float]` is the central numeric quantity. All numeric-component encoding currently goes through Python's native `float` (IEEE 754 double; ~15-16 decimal digits). Per HARD-4 (calibration anchors in under-explored mathematical territory), three regions on the substrate's hunt list — Maass forms, p-adic L-functions, motivic periods — produce values whose precision exceeds double. Native float in those regions silently loses information.

This audit walks the 6 documented `MARGIN_UNITS` and classifies each for multi-precision need. Two of six need multi-precision support to be substrate-grade in the high-precision hunt regions:

- `absolute` (generic numeric distance) — needs `mpmath.mpf` or `gmpy2.mpz/mpq` to preserve >double precision
- `log_distance` (log10 distance) — same reason; log of a high-precision number under double loses precision

Four of six are precision-OK as-is:

- `p_value` (F1 permutation null) — bounded in [0,1], double is sufficient at typical N≤10⁹
- `z_score` (F6 base rate) — typically O(1) magnitudes, double is sufficient
- `hamming` (catalog distance) — integer-valued, double safely encodes ints up to 2⁵³
- `boolean` (0/1 flag) — trivially encodable

---

## Per-component precision audit

| Margin unit | Field type | Typical value range | Precision need | Substrate-grade? |
|---|---|---|---|---|
| `p_value` | float | [0, 1], smallest is ~1/N where N ≤ 1e9 | double sufficient (float can represent 1e-9 cleanly) | YES |
| `z_score` | float | typically [-10, +10]; substrate's $z=2$ characteristic | double sufficient | YES |
| `hamming` | float (int-valued) | [0, ∞); integer counts | double sufficient (ints to 2⁵³ are exact) | YES |
| `absolute` | float | unbounded | **NEEDS multi-precision in p-adic / motivic / Maass regions** | NO (gap) |
| `log_distance` | float | log10(distance); log of high-precision input loses precision under double | **NEEDS multi-precision in same regions as `absolute`** | NO (gap) |
| `boolean` | float (0/1) | {0, 1} | trivially encodable | YES |

---

## Substrate-side gap detail

Native `float` is fine for the discovery-pipeline domains the substrate currently exercises (Lehmer ±5 in M ≈ [1.0, 1.18]; BSD ranks 0-4; modular form weights small). Those regions live within double's precision envelope.

The **gap** appears when the substrate ingests:

1. **Maass form Hecke eigenvalues** (per T-2026-05-07-T023 capability gap): LMFDB stores these to 50+ digit precision because the corresponding Maass forms are characterized by precision-sensitive transcendental quantities. A KillComponent comparing a candidate's computed eigenvalue to LMFDB's high-precision value via `margin=abs(computed - lmfdb_value)` would compute the difference in double precision — losing all digits beyond ~16. The kill_vector then becomes useless for distinguishing "candidate matches to 30 digits" from "candidate matches to 16 digits."

2. **p-adic L-function values** (per T-2026-05-07-T025 capability gap): p-adic numbers have their own native precision concept (`O(p^N)` for some N). Encoding via float entirely discards the p-adic precision metadata; the substrate has no place to put it. The `margin` field would need to carry an `mpmath.mpf` or a typed `PadicValue` to preserve the p-adic structure.

3. **Motivic periods** (per T-2026-05-07-T028 capability gap): conjectural identity tests (e.g., `period_via_method_A == period_via_method_B`) need high-precision equality testing. Double is insufficient; mpmath at dps=50+ is the minimum.

---

## Proposed contract change (deferred to next window)

Per ticket scope (audit-only this dispatch), the implementation is deferred. The proposed contract change for the next contract-change window:

### Option A — Type-widen `KillComponent.margin`

```python
# Before:
margin: Optional[float] = None

# After:
margin: Optional[Union[float, "mpmath.mpf", "gmpy2.mpz", "gmpy2.mpq"]] = None
```

**Tradeoff:** widens the contract, but minimally. Most callers continue to pass `float` and see no change. Callers who need multi-precision pass `mpmath.mpf`. Downstream consumers (`_squash_margin`, MI estimators) need updating to handle non-float margin types.

### Option B — Explicit precision metadata on KillComponent

```python
# Before:
margin: Optional[float] = None
margin_unit: Optional[str] = None

# After:
margin: Optional[float] = None  # double-precision approximation, always
margin_high_precision: Optional[str] = None  # serialized mpmath.mpf for high-precision regions
margin_unit: Optional[str] = None
margin_precision_dps: Optional[int] = None  # decimal places of precision
```

**Tradeoff:** keeps `margin: float` contract intact (zero migration cost for existing callers); adds explicit precision-tagged sister fields. Downstream consumers use `margin_high_precision` if present, else `margin`. This is more conservative; preserves backwards compatibility at the cost of a slightly chunkier dataclass.

**Recommendation: Option B.** Preserves the existing `margin: Optional[float]` contract; multi-precision becomes opt-in via the sister field. Aligns with the substrate's pattern of additive-where-possible contract evolution (e.g., the `stability_pass` sister field on `KillComponent` for structured stability without removing the legacy scalar `stability` field).

---

## What this audit does NOT do (per ticket scope)

- No code changes (the contract change is queued for a future window via the ticket itself, NOT the in-place fix pattern that T018 used for sentinel cases — multi-precision is a substantively bigger contract change than getter-error semantics)
- No test additions (tests follow the implementation)
- No migration of existing kill_vector data (would happen as part of the implementation work)

A new ticket for the implementation should reference this audit doc and pick Option A vs. Option B.

---

## Cross-references

- `prometheus_math/kill_vector.py` lines 86-108 — `MARGIN_UNITS` tuple
- `prometheus_math/kill_vector.py` `KillComponent.margin` field definition
- `aporia/doctrine/critical_memories.md` HARD-4 (calibration anchors in high-precision territory)
- T-2026-05-07-T023, T-2026-05-07-T025, T-2026-05-07-T028 — capability-gap tickets that surface the precision need
- `pivot/contract_change_window_2026-05-07_summary.md` — closing summary of this dispatch
- `aporia/meta/queue/techne_inbox.jsonl#T-2026-05-07-T029` — original ticket

---

*Audit-only; no code change in this dispatch. Implementation deferred to next contract-change window per ticket. — Techne, 2026-05-07*
