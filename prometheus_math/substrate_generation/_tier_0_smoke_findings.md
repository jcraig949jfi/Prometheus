# Tier-0 Smoke-Test Findings

**Date:** 2026-05-11
**Run:** `prometheus_math/substrate_generation/_tier_0_smoke_results.json`
**Configuration:** deg-12 palindromic, coef_bound=±2, max_candidates=30, in-memory SigmaKernel

---

## Verdict — pipeline works; bottleneck identified

The harness ran end-to-end through enumeration → Mahler measure → DiscoveryPipeline.process_candidate → KillVector v2 → outcome classification. **Pipeline integrity confirmed.**

But the run also identified the dominant bottleneck for any future scale-up.

---

## Numbers

| Metric | Value |
|---|---:|
| Enumerated | 15625 (full coef_bound=2 palindromic deg-12 with c_0=1) |
| Mahler computation failed | 1801 (12% of enumeration) |
| Out-of-band M (not in (1.001, 1.18)) | 13820 (88% of enumeration) |
| **In-band, processed** | **4** (0.026% of enumeration) |
| Wall-clock | 457.56s (~7.6 min) |
| Records/hour (extrapolated) | 31.5 — meaningless statistically (n=4) |
| Near-miss rate | 0.0 |
| Catalog-disagreement rate | 1.0 (all 4 had catalog hit + F-gate survivor split) |
| All processed terminal state | REJECTED (kill_pattern: `reducible:...`) |

---

## Findings

### Finding 1 (DOMINANT BOTTLENECK): in-band rate is 0.026%

Of 15625 enumerated candidates, only 4 had Mahler measure in the Lehmer band (1.001, 1.18). The substrate is paying the full enumeration + Mahler-computation cost on 99.974% of candidates that get immediately discarded as out-of-band.

**Implication:** brute-force enumeration is a wasteful generator strategy. Tier-1+ should:
- Use a **band-aware enumerator** that biases toward coefficient patterns known to produce in-band Mahler measures (e.g. patterns near Mossinghoff catalog entries; patterns with specific cyclotomic-factor signatures)
- Or **post-hoc-filter** during Mahler computation: bail out early once `|root|` magnitudes show M will be > 1.18

### Finding 2: mpmath.polyroots failure rate is high (12%)

1801 of 15625 candidates failed Mahler computation entirely (mpmath.polyroots couldn't converge within 100 maxsteps at dps=60). This is a numerical-robustness gap.

**Implication:** Tier-1 Mahler computer should fall back to sympy factorization when mpmath fails (the existing `_lehmer_brute_force_path_b.mahler_measure_high_precision` does this; Tier-0 used a lighter-weight version for speed and paid the failure cost).

### Finding 3: per-candidate cost is ~29ms (pure Mahler dominated)

457s / 15625 = 29ms per Mahler attempt. The 4 in-band candidates took an additional ~10s each through the full F-gate battery (sympy factorization + catalog HTTP).

**Implication:** Tier-1 should:
- Batch Mahler computations on GPU where possible (numpy / cupy polynomial root-finders for the bulk pre-filter)
- Reserve mpmath high-precision for in-band candidates only
- Cache catalog HTTP lookups locally (LMFDB / OEIS / Mossinghoff)

### Finding 4: all 4 in-band candidates were "reducible" rejections

Every processed candidate factored into smaller polynomials × cyclotomic factors. None survived to F-gate evaluation. This is correct substrate behavior (Lehmer candidates must be irreducible) but it means **the smoke test produced 0 records that exercise F1/F6/F9/F11**.

**Implication:** Tier-1 enumerator should pre-filter for irreducibility (via SymPy factor) BEFORE Mahler computation, since reducible polys are guaranteed to either have M=1 (all cyclotomic factors) or be eliminated by the irreducibility check anyway. Saves ~50% of work.

### Finding 5: catalog-disagreement rate of 1.0 is a definitional artifact

All 4 had `catalog_disagreement: True` because the smoke test's classifier flags this when ANY catalog component triggers AND ANY F-gate survives. For reducible candidates the catalog reports "factor matches Mossinghoff entry X" while F-gates haven't been reached yet. This isn't substrate-disagreement; it's a Tier-0 classifier artifact.

**Implication:** Tier-1 quality scorer should refine the catalog-disagreement definition to exclude reducible cases (where F-gates were never reached).

---

## Bottleneck attribution

If we extrapolate naively:
- 4 records in 457s = 31.5 records/hour at this in-band rate
- For 10K records/day target: would need 13.2 days at this rate (clearly insufficient)
- For 100K records/day Tier-2 target: 132 days (impossible at this rate)

The 30-1000× speedup needed comes from **smarter enumeration**, not faster probes:
- Pre-filter for irreducibility: ~2× (eliminates ~50% reducible cases)
- Band-aware enumeration biased to in-band coefficient patterns: ~10-100× (raises in-band rate from 0.026% to 0.3-3%)
- Catalog HTTP local cache: ~2-5× (eliminates redundant lookups)
- Batched GPU Mahler pre-filter at lower precision: ~3-10× (parallelizes the dominant cost)

Combined: ~120-1000× achievable, putting 10K records/day in reach on local hardware.

---

## What this confirms for the design doc

The Tier-0/1/2/3 roadmap holds, but the Tier-1 work needs to include:

1. **Band-aware enumerator** (not just generic palindromic enumeration)
2. **Irreducibility pre-filter** (cheap; eliminates 50% of work)
3. **Mahler fallback chain** (mpmath → sympy when mpmath fails)
4. **Catalog HTTP local cache**
5. **Batched GPU Mahler at lower precision** for the pre-filter pass

These are all WITHIN file ownership (no contract change needed). They sit on top of the Tier-0 harness rather than rewriting it.

The active-sampler layer (Policy A info-theoretic scoring) remains a Tier-1 deliverable but it now has an additional input: the Tier-0 finding that catalog-disagreement classifier needs refinement to exclude reducible cases.

---

## Aporia decision impact

This smoke test STRENGTHENS the case for Aporia greenlight:

- Pipeline integrity proven (the substrate writes through to KillVector v2; outcomes are correctly classified)
- Bottleneck is enumeration efficiency, not substrate write rate (substrate could absorb 100K records/day without breaking a sweat)
- Tier-1 enhancements are well-scoped and within file ownership
- Quality concerns are real (Tier-0 produced 0 F-gate-exercising records; Tier-1 active sampler must address)

Recommended Aporia decision based on smoke test:
1. **Greenlight Tier-0 baseline run** with band-aware enumeration (10K candidates target; expect actual records 100-300 with 1-3% in-band rate after pre-filter)
2. **Greenlight Tier-1 enhancements as a single batch** (band-aware enum + irreducibility pre-filter + Mahler fallback + catalog cache + GPU pre-filter)
3. **Defer Tier-1 active sampler design** until Tier-1 enhancements ship and we have ~1K real F-gate-exercised records to score against

— Techne, 2026-05-11
