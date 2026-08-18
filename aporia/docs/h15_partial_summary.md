# H15 NF Tower Termination — Partial Summary

**Date:** 2026-04-22
**Status:** PARTIAL — 5 results captured before script hung/died on sample 6

## Background

H15 hypothesis (from consolidated frontier hypotheses 20260417):
> "ADE Galois groups have class number towers terminating in ≤ 2 steps; non-ADE > 2. Tables: nf_fields. Kill: Wilcoxon p > 0.01. Connection: Golod-Shafarevich."

## Toolchain

- `techne.lib.hilbert_class_field.class_field_tower(poly, max_depth=3, max_class_number=50)`
- `techne.lib.galois_group.galois_group(poly)` (not used in this run; LMFDB galois_label used instead)
- LMFDB `nf_fields` via postgres

Blocker: at class_number > 50, PARI stack overflows. Techne guard added `max_class_number` kwarg.

## Partial Results (5 complete)

| Label | Galois | cn | Tower cn_seq | Depth | Note |
|-------|--------|-----|--------------|-------|------|
| 2.2.44033.1 | 2T1 (C_2, abelian) | 3 | [3, 1] | 1 | trivial |
| 2.2.6105.1 | 2T1 (C_2, abelian) | 4 | [4, 2, 1] | 2 | 2-step tower |
| 2.2.25736.1 | 2T1 (C_2, abelian) | 4 | [4, 1] | 1 | trivial |
| 2.2.64933.1 | 2T1 (C_2, abelian) | 5 | [5, 1] | 1 | trivial |
| 2.0.2296.1 | 2T1 (C_2, abelian) | 16 | [16, 112] | 1 (aborted) | HCF cn=112 beyond guard; tower is genuinely deeper |

## Reading

At **low class number** (cn ≤ 5), HCF tower terminates at depth 1 in most cases — a trivial closure. The ADE vs non-ADE discrimination H15 predicts cannot be tested here; all samples happen to be ADE-A (cyclic C_2).

**Interesting specimen:** `2.0.2296.1` (disc = -2296, cn = 16) has HCF class number 112. This is a candidate for a Golod-Shafarevich-style long tower — the 2-rank of Cl(K) may be large enough to force infinite tower extension. Such fields are known for imaginary quadratic K with 2-rank ≥ 5 (Brumer's sufficient condition for infinite tower).

## Why the script hung

Sample 6 (a deg-3 or 4 solvable-nonabelian case, by random selection) triggered a slow PARI HCF computation that did not complete in 180s budget. Python process remained alive but stalled; eventually killed externally.

## Next Steps

1. Per-sample subprocess isolation with hard timeout (multiprocessing.Pool with per-task SIGKILL at 20s wall).
2. Target cn ∈ {6, 8, 10, 12, 15, 20} across the three Galois buckets (avoid cn ≤ 5 trivial regime).
3. The 2.0.2296.1 specimen alone may be the most valuable finding — a concrete candidate for Golod-Shafarevich infinite tower in LMFDB.

## Open Question

Is `2.0.2296.1` (disc = -2296 = -8 * 287, so K = Q(sqrt(-574)?) already known in the class-field-tower literature? A targeted check via Koch-Venkov / Brumer tables would confirm whether this is a textbook example or a fresh specimen.
