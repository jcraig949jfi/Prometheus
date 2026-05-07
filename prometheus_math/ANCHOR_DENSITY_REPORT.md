# Calibration Anchor Density Report

_Generated: 2026-05-07 10:56:39 UTC_
_Per inbox ticket T-2026-05-07-T036 (prometheus_math/anchor_density.py)_

## Summary

- **Charts audited:** 1
- **Anchors loaded:** 2
- **Under-anchored threshold (per-axis):** 0.100
- **Under-anchored charts:** 1
- **Unmatched anchors (in store but not mapped to any chart):** 2

## Per-Chart Metrics

| chart_id | domain | region_key | axes | anchors | density (per-axis) | flag |
|---|---|---|---:|---:|---:|---|
| `lehmer:deg14:pm5:palindromic` | `lehmer` | `deg14:pm5:palindromic` | 8 | 0 | 0.000 | UNDER |

## Under-Anchored Charts (Substrate Finding)

**1 chart(s) are under-anchored** (count == 0 OR per-axis density < 0.100). Per HARD-4, calibration anchors are load-bearing infrastructure; under-anchored regions are epistemically blind. Recommend Aporia + Mnemosyne sourcing calibration anchors for these regions:

- `lehmer:deg14:pm5:palindromic`

## Unmatched Anchors (Substrate Finding)

**2 anchor(s) in the store do not match any registered chart** under the conservative-permissive heuristic (chart's domain or region_key first segment appears in the anchor's structural_signature or tag_set). Either: (a) the anchor schema needs an explicit `chart_id` field; or (b) the relevant chart isn't yet registered. Sample unmatched anchor ids:

- `CAL-2026-04-26-001`
- `CAL-2026-04-26-002`

## Caveats

1. **Conservative-permissive matching.** This audit uses substring matching on free-text fields because the anchor schema lacks an explicit `chart_id` field. False positives (anchor mapped to a chart it shouldn't be) and false negatives (anchor missed by matching) are both possible. Recommend Aporia file a follow-up ticket to add `chart_id` to the calibration anchor schema.
2. **Per-axis density is a proxy.** True volume normalization (volume of admissible region) is chart-specific and not generally computable. The per-axis-density metric is a comparable proxy across charts; a future Aporia ticket can extend with chart-specific volume estimators where they exist.
