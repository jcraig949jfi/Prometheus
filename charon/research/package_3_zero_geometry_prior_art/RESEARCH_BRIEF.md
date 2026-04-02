# Research Package 3: Zero-Based Geometry — Prior Art Search
## For: Google AI Research Mode
## Priority: MEDIUM — novelty claim depends on this

---

## What We Built

A searchable coordinate system over arithmetic objects (elliptic curves,
modular forms, genus-2 curves) where each object is represented by a
vector of its L-function's low-lying zeros (Katz-Sarnak normalized).
Raw k-NN search in this space recovers known modularity theorem pairs and
clusters by analytic rank within conductor strata.

## What We Need to Know

Before claiming ANY novelty, we need to understand what already exists.

### Specific Questions

1. **Has anyone built a k-NN or nearest-neighbor search system using
   L-function zeros as coordinates?** Not PCA visualization, not statistical
   analysis — actual searchable retrieval where you input an object and
   get its nearest neighbors in zero space.

2. **Has anyone compared zero distributions ACROSS object types** (e.g.,
   elliptic curve zeros vs modular form zeros vs genus-2 curve zeros)
   as a geometric/metric comparison? Not within a single family — across families.

3. **The February 2025 paper arXiv:2502.10360** ("Machine learning the
   vanishing order of rational L-functions") — does it use zero vectors
   or Dirichlet coefficient vectors? Does it build a searchable system
   or just classify? How does their approach compare to ours?

4. **Oliver's ICMS 2024 work on unsupervised learning on LMFDB data** —
   does it use PCA on zeros or on coefficients? Is there a searchable
   component? How close is it to what we built?

5. **Edgar Costa's 2016 work on machine learning L-functions** — what
   representation did he use? PCA on what features?

6. **The murmuration follow-up literature (2022-2026):** Has anyone
   extended murmuration analysis to a multi-type search framework?
   Or is it all within-family statistical analysis?

7. **Specific to our ablation finding:** Has anyone reported that higher
   zeros (beyond the first few) carry more information about arithmetic
   invariants than the central zeros? This would be the key prior art
   claim to check.

### What Would Kill Our Novelty Claim

- If someone has already built k-NN on zero vectors across object types → we're replicating
- If the ablation result (removing first zero improves rank clustering) is known → the finding isn't new
- If PCA on zeros already produces the same ARI results → our contribution is engineering, not science

### What Would Strengthen Our Novelty Claim

- If existing work uses coefficients not zeros → our representation choice is novel
- If existing work stays within families not across → our cross-type comparison is novel
- If the ablation observation has no precedent → the spectral tail finding is new

## Key Papers to Check

- arXiv:2502.10360 — "Machine learning the vanishing order of rational L-functions" (Feb 2025)
- He, Lee, Oliver, Pozdnyakov — murmurations (2022) and all follow-ups
- Zubrilina — murmuration density formula (2023)
- Oliver — ICMS 2024 unsupervised learning on LMFDB
- Costa — ML on L-functions (2016)
- Sawin, Sutherland — EC murmuration density (arXiv:2504.12295, 2025)
- Bober, Booker, Lee, Lowry-Duda — BSD invariants and murmurations (2024)
- Any recent (2023-2026) work using zero statistics for computational number theory beyond murmurations

## Attach These Files

- `charon/reports/findings_2026-04-01.md` (what we built and found)
- `charon/reports/sprint_summary_2026-04-01_02.md` (the full sprint ledger)
- `charon/research/langlands_literature_survey.md` (our existing survey)
