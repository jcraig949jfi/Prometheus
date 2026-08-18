# Deep Research Report #131: Siegel Modular Forms Genus 3 — First-Pass Cataloging from BFvdG Tables

**Target Agent:** Harmonia
**Date:** 2026-04-23
**Status:** Scoping pass for first-pass cataloging

## 1. Problem Statement

Siegel modular forms (SMFs) of genus g are automorphic forms on Sp(2g, Z) acting on Siegel upper half-space H_g. g=1 reduces to classical elliptic modular; g=2 well-studied (LMFDB has smf_newforms for small levels and weights); **g=3 is frontier**. Dimensions of M_{k,j}(Sp(6,Z)) remain conjectural in many ranges; only small number of genus-3 Hecke eigenvalues computed.

**Q:** can we assemble first-pass catalog of ~1000 genus-3 Siegel forms (weights, vector-valued types, predicted dimensions, available Hecke traces) using Bergström-Faber-van der Geer (BFvdG) framework, cross-check against LMFDB smf_newforms?

Inventory + calibration, not discovery. Payoff: clean data layer so Harmonia tensor pipeline can include genus 3 alongside EC/g2/MF/NF/knots.

## 2. Literature

- **Bergström, Faber, van der Geer (2008)** *Siegel modular forms of degree three and cohomology of local systems*: core reference. Conjectural formula for trace of Hecke operators on S_{l,m,n}(Sp(6,Z)) via motives and point counts on A_3 over F_p.
- **Bergström-Faber-van der Geer (2012/2014):** extended tables; traces of T(p) for p up to 7, 11, 13 for specific (l,m,n).
- **van der Geer (2008)** *Siegel modular forms and their applications* (in "1-2-3 of Modular Forms"): dimensions and structure for g ≤ 3.
- **Chenevier-Renard (2015)** *Level one algebraic cusp forms of classical groups of small rank*: enumerates automorphic reps; genus-3 level-1 cusp form counts via Arthur.
- **Chenevier-Lannes (2019)** *Automorphic Forms and Even Unimodular Lattices*: level-1 table for low weights — cleanest ground truth.
- Secondary: Taïbi (2017) dimensions via Arthur; Ibukiyama theta series; Faber-van der Geer webpage tables.

## 3. LMFDB Data Reality

`smf_newforms` in LMFDB **sparse for g=3** (mostly g=2). BFvdG/Faber tables external (PDFs, webpage, Chenevier-Renard ancillary). Step 1: ingest into local `siegel_g3_catalog` with columns: (k, j_partition, level, char, dim_conjectural, T_p_traces{p=2..13}, source_ref, verified_flag).

Mnemosyne owns ingest; Harmonia consumes.

## 4. Test Design

Goal: ~1000 rows covering level-1 genus-3 forms across vector-valued weight range (l,m,n) with l ≥ m ≥ n ≥ 3.

1. Ingest BFvdG 2008/2012/2014 dim + trace tables (~200-400 rows).
2. Extend via Chenevier-Renard level-1 enumeration (~300-500 virtual entries with dim but no T_p).
3. Cross-check against LMFDB smf_newforms where overlap (g=2 corner, Saito-Kurokawa, Ikeda lifts as g=3 non-cusp).
4. For each row with ≥ 3 Hecke eigenvalues, compute Satake parameters and log(|a_p|)/p^{(k−3/2)} ratios — Ramanujan-analog on GSp(6).
5. Compare predicted lift structure (Miyawaki, Ikeda-Miyawaki) against BFvdG trace factorizations.

Schema: one JSON per form in `charon_data/siegel_g3/`.

## 5. Falsification

- BFvdG predicted T(p) disagrees with LMFDB-verified → flag row; escalate Kairos.
- BFvdG and Chenevier-Renard dimensions disagree in overlap → open question, not catalog error.
- **Hard kill:** scraped tables < ~400 usable rows → target becomes ~500; state plainly, don't pad synthetic.
- **Soft kill:** Harmonia tensor can't ingest vector-valued (l,m,n) → defer until schema supports partitions.

## 6. Budget

~1 day: 3h table scraping/parsing, 2h schema + ingest, 2h LMFDB cross-check, 1h Satake, 1h docs. Bookkeeping and calibration, no heavy compute.

## 7. Expected Outcome

**Most likely:** 400-800 genus-3 forms (below 1000 target), dominated by level-1 BFvdG + Chenevier-Renard, Hecke data for 50-150. Sufficient to add "siegel_g3" domain column in master tensor; test whether genus-3 exhibits same island-isolation as knots/NF or couples to genus-2 as expected.

**Positive surprise:** non-trivial correlation between genus-3 trace anomalies and genus-2 rank-jumps (Miyawaki/Ikeda lift bridge predicts; confirming would feed project_genus2_rosetta).

**Null (likeliest honest):** catalog built, data density too low for tensor coupling tests; flagged as "structural inventory complete, statistical tests deferred."

**No discovery claims from this pass.** Per feedback_assume_wrong + feedback_calibration: produces **data substrate**, not finding.

**Word count: ~770**
