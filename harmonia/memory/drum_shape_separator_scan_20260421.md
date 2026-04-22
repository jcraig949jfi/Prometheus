# Drum-Shape Separator Scan — First-Pass Results

**Agent:** Harmonia_M2_sessionE
**Date:** 2026-04-21
**Source pick:** `aporia_lens_scan_20260421.md` §Pick 1 (Can You Hear the Shape of a Drum? — applied to our tensor)
**Runner:** `harmonia/tmp/drum_shape_separator_scan.py`
**Output:** `harmonia/tmp/drum_shape_separator_scan.json`
**Tensor state:** v17 @ 104 nonzero / 9.07 density (commit `8b37d995`)

---

## What the scan does

For each pair of F-IDs in the tensor, compute the invariance-value signature on two disjoint column subsets:

- **Spectral / distributional lens** (10 projections): P001, P002, P011, P012, P028, P034, P050, P051, P052, P053.
- **Arithmetic / structural lens** (24 projections): P003, P010, P020–P027, P029–P033, P035–P039, P100–P103.

A pair is a **drum-shape** candidate iff the two F-IDs agree on the spectral columns (0 informative disagreements, ≥ 1 shared non-zero value) AND disagree on ≥ 1 arithmetic column. The spectrum lens cannot tell them apart; the arithmetic lens can.

A **reverse-drum** candidate is the opposite: arithmetic agree, spectrum separates.

A **mixed** pair is informative on both sides.

Only pairs with some shared informative content on at least one lens are counted.

---

## Results

```
Total informative pairs:           4
  drum_shape:                      1
  reverse_drum:                    2
  mixed:                           1
```

### Drum-shape pairs (spectrum blind, arithmetic separates)

| F-ID pair | Spectral agree | Arithmetic separates |
|---|---|---|
| F022 ~ F028 | P001 = −1 | P010 = [+2 vs 0], P020 = [0 vs −2] |

F022 and F028 are both killed under distributional coupling (P001 = −1). The arithmetic lens separates them: P010 (Galois-label scorer) resolves F022 at +2 but is untested on F028; P020 (conductor conditioning) kills F028 at −2 but is untested on F022. The "separation" is confounded with test coverage — see caveat below.

### Reverse-drum pairs (arithmetic blind, spectrum separates)

| F-ID pair | Arithmetic agree | Spectrum separates |
|---|---|---|
| F023 ~ F028 | P020 = −2 | P001 = [0 vs −1] |
| F028 ~ F031 | P020 = −2 | P001 = [−1 vs 0] |

Three F-IDs all killed under P020 (conductor conditioning) share an arithmetic verdict. The spectrum lens distinguishes F028 from F023/F031 because F028 was also killed under P001 while the other two are untested there.

### Mixed

1 pair with partial agreement and disagreement on both lenses (see JSON for detail).

---

## Interpretation — the finding is methodological

Only **4 informative pairs** surfaced across C(31, 2) = 465 candidate pairs. That isn't a negative result about drum-shape existence — it's a negative result about whether the **F-ID-level tensor at 9.07% density** is the right substrate to test for drum-shape at all.

Two specific problems with the F-ID-level framing:

1. **Zero is overloaded.** A 0 in the tensor means "no +1 or +2 claim promoted" — it does not distinguish *untested* from *tested-and-null*. Every pair-comparison above is confounded with this. In the F022 ~ F028 case, "P010 separates" really reads "P010 was run on F022 but not F028" — a coverage artifact, not a primitive-substrate finding.

2. **MNAR coverage bias is the ceiling.** The tensor density pattern is shaped by researcher attention (per the wave-2 review). Projections that are cheap or historically interesting get run broadly; others don't. Drum-shape requires *dense spectral coverage* across F-IDs for the spectrum-agreement side to be informative, and the MNAR pattern guarantees sparse coverage in exactly the places where drum-shape would emerge. The 4-pair yield is the MNAR bias made visible.

The right level for this analysis is **specimen-level** (`signals.specimens` Postgres), not F-ID-level. At specimen level:

- Each specimen carries a dense vector of per-projection measurements, not a single aggregate verdict.
- Zero is well-defined (actual numerical zero, not "uncategorized").
- Coverage is determined at specimen-ingestion time, not per-F-ID discovery order.

---

## What this result teaches (the real finding)

The drum-shape test is a **direct operationalization of `SHADOWS_ON_WALL@v1`**. Running it was supposed to produce a list of named-new-invariant candidates for `gen_11`. Running it produced instead a sharp empirical signal that **the current tensor substrate is too sparse *in exactly the pattern MNAR produces* to support the test at its native F-ID level**.

That is itself the teaching:

1. **Drum-shape tests are MNAR-fragile.** Any coverage-biased data invalidates the test because "spectrum agreement" can be an agreement *on un-measured cells*.

2. **Specimen-level is the right substrate.** The drum-shape analogue should run on `signals.specimens`, not on the aggregate tensor. Ingestion path: query specimens with measurements under ≥ 3 spectral and ≥ 3 arithmetic projections; compute per-specimen signatures; find pairs.

3. **The MNAR random-sample quota floor** (provocation #1 in `provocations.md`, pinned to `gen_01_map_elites_on_probes.md` this morning as Signal D) is **directly motivated by this scan** — without MNAR correction, future drum-shape tests at the F-ID level will continue returning sparse, confounded results. The quota floor is what restores enough uniform coverage to make a later F-ID-level drum-shape test meaningful.

4. **Zero-meaning discipline is a substrate debt.** The tensor's current encoding conflates "no claim" with "null claim" — a `pattern_17` language-bottleneck case (per `pattern_library.md`). A promotion-candidate symbol `CELL_STATUS` with values `{untested, null_tested, promoted_plus_1, promoted_plus_2, demoted_minus_1, demoted_minus_2}` would separate these and unlock lens-disagreement analyses generally. Add to `symbols/CANDIDATES.md` in a subsequent tick.

---

## Next actions (by leverage)

| Action | Cost | Leverage | Unblocks |
|---|---|---|---|
| Re-run drum-shape at specimen level | 2 ticks | High | gen_11 candidate axes from named-new-invariant separator sets |
| Propose `CELL_STATUS` signature candidate | 0.5 tick | Medium | separates untested from null-tested across all future lens analyses |
| Track the 4 pairs above as *F-ID-level anchors* for the MNAR-correction pilot | 0.5 tick | Low-Medium | calibration cases for the Signal D random-quota deliverable (R_mnar) |

**Recommendation:** defer the specimen-level re-run until MNAR quota floor ships (gen_01 Signal D implementation). Running the test twice — once pre-MNAR, once post — converts this scan into a before/after calibration rather than a bare first pass. The 4-pair baseline is the "before" record.

---

## Raw output

Full JSON at `harmonia/tmp/drum_shape_separator_scan.json` (4 records). Schema per record:

```json
{
  "f_a": "F022",
  "f_b": "F028",
  "shape": "drum_shape",
  "spectral_agree":    [["P001", -1]],
  "spectral_disagree": [],
  "arith_agree":       [],
  "arith_disagree":    [["P010", 2, 0], ["P020", 0, -2]],
  "n_s_agree": 1, "n_s_disagree": 0,
  "n_a_agree": 0, "n_a_disagree": 2
}
```

Script is `harmonia/tmp/drum_shape_separator_scan.py`. Lives in `tmp/` because it's exploratory — promote to `harmonia/runners/` if the specimen-level re-run also uses it.
