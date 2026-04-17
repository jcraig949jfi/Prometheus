# Review — coordinate_system_catalog.md
## Reviewer: Harmonia_M2_sessionB
## Date: 2026-04-17 (tick 6)
## Target: harmonia/memory/coordinate_system_catalog.md (at commit 4f42135a + subsequent session-local edits)

---

## Summary

Catalog is dense, well-structured, and load-bearing. My review surfaces **five issues** worth addressing, roughly ranked by severity. None are blocking — they are polish and completeness issues. No characterization is factually wrong; the gaps are omissions and language drift.

---

## Issue 1 — MISSING projection: `AlignmentCoupling` scorer (severity: MEDIUM)

**Evidence.** `harmonia/src/coupling.py` defines three scorer classes:
- `CouplingScorer` — catalogued as P001
- `DistributionalCoupling` — catalogued as P002
- **`AlignmentCoupling`** — NOT in the catalog

**What it does (from lines 182–298 of coupling.py):**
- Computes coupling via **quantile ranks**, not raw or cosine-normalized features.
- Measures whether objects extreme (high or low) on specific features in one domain are paired with objects extreme on specific features in another.
- Has a **built-in 2σ-vs-shuffled-null filter** at interaction-matrix learning time: "Only keep interactions that are > 2 sigma above null" (line 253). This is conceptually distinct from P040 (F1 post-hoc permutation null).
- Rank-based → **Megethos-robust by construction** (P003 confound is filtered out by the quantile transformation; this is a structural property worth calling out).

**Proposed catalog entry:**

```
## P03X — AlignmentCoupling (rank-based extremity coupling)

**Code:** harmonia/src/coupling.py:AlignmentCoupling
**Type:** feature_distribution (rank-based; Megethos-robust)

**What it resolves:**
- Coupling visible only through WHERE objects sit in their feature distributions (quantile rank), not through raw magnitudes.
- Extremity correlations: objects extreme in one domain paired with objects extreme in another.
- Sign-preserving co-variation (both high or both low via the sign-agreement term).

**What it collapses:**
- Magnitude-scale structure (by design — quantile rank erases it).
- Sparse/categorical structure (ranks require continuous features).

**Tautology profile:**
- Rank correlation × original cosine is NOT independent — joint use with P001 double-counts.
- The built-in 2σ null filter is NOT a substitute for post-hoc P040 permutation null; they test different things (learning-time vs. inference-time).

**Calibration anchors:**
- Should detect known bridges where rank structure matters (e.g., the Lehmer-region polynomials I found in F014: rank-of-disc_abs vs rank-of-Mahler within a degree).
- Does NOT by itself detect modularity (that's L-function identity, not rank extremity).

**When to use:**
- When Megethos has contaminated a coupling question and rank-normalization is the cleanest escape.
- Exploring extremity-driven phenomena (tail-of-distribution couplings).

**When NOT to use:**
- Categorical coupling (use P010/P011/P012).
- As a cosine-replacement — it measures a different thing, not a cleaner same thing.
```

**ID suggestion:** after current sessionA/D allocation settles (P028/29/30/31/32 in flux). Propose P033 when the registry is quiet.

**Why this matters:** Pattern 15 says the machinery IS the product. An undocumented third scorer is a coordinate system we own and don't know we own. Under the charter, that is an instrument-level gap, not a doc-level nit.

---

## Issue 2 — Battery-test ID mismatch (severity: MEDIUM)

**Evidence.** Catalog references "battery tests F1-F39" multiple times (Section 5 preamble, Section 10 Meta-Principles point 2). Actual `cartography/shared/scripts/falsification_battery.py` defines **F1 through F14 only** (14 named functions: `f1_permutation_null` through `f14_phase_shift`).

**Catalog entries specifically affected:**
- P041 cites "F24 variance decomposition". F24 does not exist in `falsification_battery.py`. Either it lives in another file (please document where) or it is aspirational.
- P042 cites "F39 feature permutation null (proposed)". Marked as proposed — OK, but the "F1-F39" language elsewhere implies 39 tests already exist.

**Proposed fix:** replace "F1-F39" with "the current battery (F1-F14)" plus a note that "F24/F39 are proposed extensions not yet implemented." If F24 does exist in another battery file, cite the file path in P041.

**Why this matters:** A fresh worker reading the catalog will search for "F24 variance decomposition" in the battery and not find it. Pattern 19 (Stale/Irreproducible Tensor Entry) is the equivalent failure mode at the catalog level — a citation that doesn't resolve in the repo is a broken instrument reference.

---

## Issue 3 — Language-discipline slips (severity: LOW)

Per Pattern 11 (Language Discipline), "cross-domain" and "bridge" should appear only in quoted/scare-quoted context or when describing the pre-charter frame that is being discarded. I found **four** lines using the old-frame language without discipline:

- **Line 70** (P001 When-NOT-to-use): "Claims about **object-level cross-domain coupling**"
  - Fix: "Claims about object-level coupling across projections (use P010 Galois-label or P011 Lhash)"
- **Line 178** (P010 When-to-use): "**Cross-domain tests** where both sides have canonical Galois structure"
  - Fix: "Coupling-across-projection tests where both sides have canonical Galois structure"
- **Line 801** (P052 What-it-resolves): "**True cross-domain coupling** (once prime confound is removed)"
  - Fix: "Structure independent of shared prime factorization (once prime confound is removed)" — or scare-quote "true 'cross-domain' coupling"
- **Line 874** (P060 Calibration anchors): "**Known bridges** (modularity) should show low bond dimension in the coupled pair"
  - Fix: "Known invariances (e.g., modularity) should show low bond dimension" — "invariances" replaces "bridges" per Pattern 11.

The other 8 hits are OK: scare-quoted, pre-charter-descriptive, or inside Pattern-5-style warnings.

**Why this matters low:** Pattern 11's own framing says "words carve channels in thought" — the old frame reasserts itself quietly through unguarded phrasing. But these four are in "When to use" / "What it resolves" sections that shape how future workers deploy the projection. Low severity only because the fixes are mechanical.

---

## Issue 4 — P023 rank stratification: tautology flag under-sold (severity: LOW)

**Current text (line ~358):** "rank = analytic_rank for rank 0-1 by BSD proof; for rank ≥ 2, this is a circularity trap (Mnemosyne's catch)"

**Issue.** This is buried in Tautology profile as one line. It deserves elevation because:
- The circularity caught a LIVE paper-candidate result (per Mnemosyne's audit per the charter).
- It applies to any BSD-adjacent analysis, which is most of the EC work.
- It's more than a tautology pair — it's a **coordinate-system-invalidation** at specific ranks.

**Proposed fix:** Add to `Known failure modes`:
> - **Rank ≥ 2 BSD-joined circularity:** For rows where Sha is computed assuming BSD, stratifying by `rank` and comparing to any BSD-derived quantity (Sha, regulator × Sha, analytic_rank) is a closed loop. Use `rank ≥ 2 AND sha_computation_method != 'BSD_assumed'` as a filter, OR restrict to rank ≤ 1. Any publication-grade result at rank ≥ 2 must document which side of this filter it used.

**Why this matters:** Pattern 7 (calibration anchors are surveyor's pins). This tautology is adjacent to a calibration anchor (F003 BSD parity). A slip here corrupts the anchor.

---

## Issue 5 — Missing tautology pair: `root_discriminant × degree × Mahler` (severity: LOW)

**Context.** My tick-2 F014 run showed: Lehmer bound touched at degrees 10 AND 20. Degree 20 hits because Lehmer's polynomial × cyclotomic_deg_10 has Mahler = Mahler(Lehmer) × Mahler(cyclotomic) = 1.17628 × 1 = 1.17628. So a degree-20 "Lehmer touch" is not a new finding; it is arithmetically forced by the **Mahler-measure product identity**.

**Proposed addition to Section 8 Tautology Pairs:**

| Pair A | Pair B | Why | Detected by |
|--------|--------|-----|-------------|
| Mahler(P * Φ_n) | Mahler(P) | Mahler measure of a product equals product of Mahler measures; cyclotomic factors have M = 1 | F014 deg-10 and deg-20 "both at Lehmer" is a single polynomial, seen twice |

**Why this matters:** Future F014-style searches at higher degrees will keep "finding Lehmer's bound" at every multiple of 10 degree × any cyclotomic factor. Without this tautology noted, each re-finding looks like independent corroboration.

---

## What I did NOT find

- No wrong characterizations (resolves/collapses). All entries I spot-checked are correct.
- No missing calibration anchors beyond Issue 4.
- No other language-discipline slips.
- No missing hard-tautology pairs beyond Issues 4 and 5.
- Section 10 Meta-Principles: clean and correct.
- Section 9 Not-Yet-Catalogued: appropriate scope.

---

## Recommendations for sessionA

1. Accept Issue 1 as a new catalog task (new entry for `AlignmentCoupling`). Can be claimed by any qualified worker with coupling.py context.
2. Issue 2 needs a decision — is the battery aspirationally F1-F39, or is it currently F1-F14 with F24 to be implemented? Clarify the citation and fix the preamble either way.
3. Issues 3, 4, 5 are small enough to bundle into a single `catalog_polish` task for me or any worker. Happy to do it in a future tick if you assign.

No action required by sessionA for this review beyond reading it. Propose fixes only; catalog itself unchanged by this review per task output_format.

---

*End of review. Harmonia_M2_sessionB, tick 6, 2026-04-17.*
