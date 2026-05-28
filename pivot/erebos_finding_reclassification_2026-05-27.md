# Erebos Finding Reclassification

**Date:** 2026-05-27
**Status:** v3 §4.10 mandatory deliverable. Per all four frontier reviewers' convergent critique that "none of the 7 findings is novel to primary literature" (whitepaper §10 admits this directly), the substrate's evidence base must be reclassified using ChatGPT's three-tier system before the next iteration can claim any inherited credit.

**Doctrine:** The substrate must not inflate its own results (`feedback_calibration` + `feedback_assume_wrong`). Stripping ambiguous evidence is more honest than retaining it.

---

## The three-tier classification (from v3 amendment §4.10)

1. **Substrate finding** — proves the substrate-side INSTRUMENT noticed structure. The structure may or may not be mathematical; the finding is about what the substrate's loaders successfully detected.
2. **Catalog finding** — reveals something about the dataset construction / enumerator bias. The structure exists in the catalog, not necessarily in the underlying mathematics.
3. **Mathematical finding** — plausible statement about the objects independent of the catalog. Would survive moving to a different (correctly-constructed) catalog of the same domain.
4. **Literature-grade finding** — survives external novelty and rigor audit. Published or publishable by a domain expert.

Strict ordering: every literature-grade is mathematical; every mathematical is catalog; every catalog is substrate. Not vice versa.

---

## Per-finding reclassification

### Finding 1: ITER-4 Salem-class moderation of Lehmer-bound survival
**Doc:** `pivot/erebos_substrate_finding_iter4_salem_class_moderation_2026-05-26.md`
**Original framing:** "First substrate-grade PROMOTED EREBOS verdict. Salem moderation observed_divergence = 0.997 vs null_p95 = 0.024 (41.7× null)."
**v3 reclassification:** **Catalog finding.**
**Rationale:** Salem-class is a Mossinghoff catalog annotation. The Mossinghoff catalog enumerates Salem polynomials densely in [1.18, 1.30] by design (per the catalog's own docstring). The moderation effect tracks the cataloguer's enumeration choices. It is consistent with what a Salem-theory practitioner would expect from a catalog that defines "Salem-class" by its membership in this cluster. The substrate did not discover Salem-cluster geometry; it instrumented a known feature of the data.
**What stays valid:** The substrate's INSTRUMENT (G02 contrast loader + permutation null) correctly detected the structure that exists in the catalog. The finding is a successful PROOF OF FALSIFICATION ROUTE, not a mathematical discovery.

### Finding 2: ITER-5 Salem moderation extends to band [1.30, 1.50]
**Doc:** `pivot/erebos_substrate_finding_iter5_salem_extends_to_band_2026-05-26.md`
**Original framing:** "Second substrate-grade PROMOTED claim. Salem moderation in higher band, 1.93× null."
**v3 reclassification:** **Catalog finding.**
**Rationale:** Same domain, narrower band, same catalog enumeration bias. The finding extends the ITER-4 observation but does not change its tier — both are statements about how the catalog populates [1.30, 1.50] with Salem vs non-Salem entries.
**What stays valid:** Independent verification that the ITER-4 loader infrastructure generalizes to band-restricted variants.

### Finding 3: ITER-10 G10 Salem cluster boundary detection
**Doc:** `pivot/erebos_substrate_finding_iter10_g10_salem_cluster_detection_2026-05-26.md`
**Original framing:** Instrument validation. "G10 correctly detected the documented Salem cluster boundary."
**v3 reclassification:** **Substrate finding.** (Already correctly framed in original doc.)
**Rationale:** G10's smoothness ratio metric is a substrate-side instrument. The detection of the Salem cluster boundary is evidence that the metric works as designed — a substrate-grade INSTRUMENT VALIDATION. Not mathematics, not catalog — substrate.
**No change.**

### Finding 4: ITER-13 G15 ledger MI self-audit
**Doc:** `pivot/erebos_substrate_finding_iter13_g15_ledger_mi_2026-05-26.md`
**Original framing:** Self-audit calibration. "73.8% of v1 signal was control-flow bookkeeping circularity."
**v3 reclassification:** **Substrate finding.** (Already correctly framed.)
**Rationale:** Pure substrate self-audit. The finding is about the substrate's own bookkeeping, not about mathematics or even about a catalog. Substrate-grade by definition.
**No change.**

### Finding 5: ITER-13 G11 v2 degree-minima concentration in non-Salem cells
**Doc:** `pivot/erebos_substrate_finding_iter13_g11_v2_degree_minima_concentration_2026-05-26.md`
**Original framing:** "Substrate-grade non-tautological observation. Degree-minima over-represented in non-Salem cells 59-77× expected rate. Chi² = 191."
**v3 reclassification:** **Catalog finding.**
**Rationale:** `degree_minimum` is a Mossinghoff catalog annotation. The concentration in non-Salem cells reflects which polynomials Mossinghoff chose to flag as `degree_minimum` (typically the smallest known at each degree, not necessarily the structural minimum). The ITER-15 G11 v3 verification confirmed catalog flag agrees with independent argmin at 87.5%, with 1 outlier — meaning the finding is statistically about the catalog's annotation, not the polynomial-class itself.
**What stays valid:** Substrate-grade observation that the catalog's degree-minimum annotations are anti-correlated with Salem-class membership. This is a CATALOG-CONSTRUCTION FACT, not a polynomial-class theorem.

### Finding 6: ITER-17 G23 1/log(N) decay law for minimum-Mahler-by-degree
**Doc:** (in-commit; G23 multi-law fit refinement)
**Original framing:** "1/log(N) is the actual best-fit law (R²=0.54), substantially better than 1/N (R²=0.25 log-log)."
**v3 reclassification:** **Catalog finding.**
**Rationale:** The 1/log(N) law was fit to the Mossinghoff catalog's per-degree minima curve. The catalog's enumeration completeness across degrees is uneven (some degrees have many entries, others have one or none). The 1/log(N) finding is partially a statement about the Lehmer-conjecture-related literature's expected asymptotic behavior, but the SPECIFIC FIT QUALITY (R²=0.54) depends on the catalog. A different (more uniformly enumerated) catalog could produce a different best-fit law.
**What stays valid:** The substrate's multi-law fit machinery correctly identified that O(1/N) is NOT the right framing for this data — that rejection is robust. The positive identification of 1/log(N) is conditional on Mossinghoff.

### Finding 7: ITER-18 G17 phase-transition at M=1.26
**Doc:** `pivot/erebos_substrate_finding_iter18_g17_salem_phase_transition_2026-05-26.md`
**Original framing:** "Salem-moderation phase transition at M=1.26 — sub-threshold boundary where intervention transitions from severable to surviving."
**v3 reclassification:** **Catalog finding.**
**Rationale:** The M=1.26 boundary sits exactly at the Salem cluster's upper density edge in the Mossinghoff catalog (per ITER-10 G10's KDE peak finding and the catalog's own docstring "Salem cluster runs through 1.18..1.30"). The phase transition is a sub-threshold artifact of where Mossinghoff put the cluster boundary, not a mathematical phenomenon.
**What stays valid:** The substrate's multi-threshold sweep machinery correctly localized the boundary to within 0.02 of the catalog-documented edge.

### Finding 8 (bonus, ITER-19): palindromicity ≡ Salem-class catalog equivalence
**Doc:** (in G11 v4 commit; P(salem | palindromic) = 0.9999)
**Original framing:** Catalog-equivalence observation.
**v3 reclassification:** **Catalog finding.** (Already correctly framed.)
**Rationale:** Pure statement about the Mossinghoff enumerator's choices — palindromic and Salem-class are coextensive in this catalog. Not a polynomial theorem.
**No change.**

---

## Tier counts post-reclassification

```
Substrate findings:        2  (G10 cluster detection + G15 self-audit)
Catalog findings:          6  (ITER-4, ITER-5, G11 v2 degree-minima,
                               G23 1/log(N), G17 phase transition,
                               G11 v4 palindromic-Salem equivalence)
Mathematical findings:     0
Literature-grade findings: 0
```

This is a substantial demotion from the v1 whitepaper's "7 triangulated phenomena." The v1 framing implied substrate-grade discovery; the v3 framing accurately states the substrate-grade INSTRUMENT BEHAVIOR.

## What this changes about the substrate's epistemic posture

The v1 whitepaper's strongest empirical claims relied on the 7 findings as evidence of substrate-as-discovery-engine. The v3 reclassification reframes them as evidence of substrate-as-instrument-validation. Both framings have value, but they are different claims:

- **v1 framing:** "Erebos surfaces substrate-grade mathematical structure in the Mahler spectrum."
- **v3 framing:** "Erebos correctly detects features of the Mossinghoff catalog and demonstrates that its loader infrastructure produces empirically-routed verdicts."

The second framing is what the evidence supports. The first framing is what the reviewers correctly identified as inflated.

## Implications for Phase 1 and Sprint-1

1. **Phase 1 BSD MVP loader** (v3 §4.6) becomes the architecture's earliest opportunity to produce a **catalog** finding in a non-Mahler domain. A finding there is still catalog-tier, but provides cross-domain triangulation that the current Mahler-only evidence cannot.
2. **Phase 1 plugin degeneracy audit** (v3 §4.2) may surface that some of the 7 catalog findings collapse to one or two underlying observations after operational deduplication of plugins. Tier counts could drop further.
3. **Sprint-1 ablation A8** (second-domain MVP) is precisely the experiment whose result would let any substrate finding upgrade from "catalog" to "mathematical" — by demonstrating that the finding generalizes across catalog choices.
4. **No substrate finding currently qualifies as "literature-grade."** The path from "mathematical" to "literature-grade" requires external evaluation (domain expert audit, primary literature submission). v3 explicitly does not commit to that path until Sprint-1 passes.

## What the whitepaper's Section 5 must say after this reclassification

The v1 whitepaper's Section 5 ("The Mahler-spectrum proof of concept — seven triangulated findings") needs replacement language. Draft replacement:

> The substrate's empirical evidence comes from the Mahler-spectrum domain, where the Mossinghoff catalog provides 8596 non-cyclotomic polynomials with computed Mahler measures. Eleven of the 22 composition loaders target this domain. The result: **two substrate findings** (G10 boundary detection + G15 ledger-MI self-audit) and **six catalog findings** (Salem moderation at threshold M_Lehmer + extended to band [1.30, 1.50]; degree-minima concentration in non-Salem cells; 1/log(N) decay law; phase transition at M=1.26; palindromic-Salem equivalence). **Zero mathematical findings and zero literature-grade findings** under v3 §4.10 classification. The substrate has demonstrated that its loader infrastructure produces empirically-routed verdicts; it has not yet demonstrated that those verdicts surface mathematics that primary-literature would call novel.

That paragraph replaces the existing Section 5 in ITER-29 commit.

## Decision

This reclassification is final and non-negotiable per v3 §4.10. The substrate's framing now matches its evidence. Any plugin retrofit, Sprint-1 result, or downstream consumer that wants to cite the substrate's findings does so against the v3 tier counts, not the v1 inflation.
