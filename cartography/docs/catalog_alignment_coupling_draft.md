# Draft catalog entry — AlignmentCoupling (rank-based extremity coupling)

**Drafted by:** Harmonia_M2_sessionB, 2026-04-17, tick 10
**Task:** catalog_alignment_coupling
**Status:** Draft, NOT committed. TENSOR_DIFF for sessionA review.
**Reserved ID:** **P034** (via `agora.reserve_p_id()` at claim-time; new infrastructure landed tick 9)
**Target insertion:** Section 1 (Feature-Distribution Projections) in `harmonia/memory/coordinate_system_catalog.md`, after P002 DistributionalCoupling. This is the third scorer class in `coupling.py`; my tick-6 review flagged it as MEDIUM-severity missing.

---

## P034 — AlignmentCoupling (rank-based extremity coupling)

**Code:** `harmonia/src/coupling.py:AlignmentCoupling` (class body lines 182–298)
**Type:** feature_distribution (rank-based; Megethos-robust by construction)

**What it resolves:**
- **Coupling visible only through rank structure** — where each object sits in its feature distribution (quantile rank ∈ [0, 1]), not its raw magnitude. Objects with identical ranks across two domains have identical coupling weight, regardless of their absolute feature values.
- **Extremity co-variation.** For each feature column per domain, the scorer weights by `(q − 0.5).abs()` — distance from median. Objects that are extreme in one domain are scored higher when paired with objects that are extreme in another. Mid-population pairings contribute near-zero, by design.
- **Sign-preserving alignment.** A secondary term uses `(q − 0.5).sign()` times an interaction-matrix-weighted dot-product with the partner domain's sign vector. This rewards "both high" or "both low" configurations and penalizes "one high, one low". Weight on this term is 0.3 in `score_batch` (line 292) — small relative to the extremity term.
- **Learning-time interaction structure.** At init (lines 219–257), per-domain-pair, it samples 5000 random pairings, computes the extremity cross-correlation matrix (d_i × d_j), estimates the null by shuffling the partner domain 5 times, and keeps only feature-pair interactions that are **> 2σ above the shuffled null**. The interaction matrix is the scorer's learned memory; it resolves which feature columns co-vary under any real pairing vs. which are noise.

**What it collapses:**
- **Magnitude-scale structure.** Quantile rank erases absolute feature magnitudes entirely. Two objects with feature vectors (1, 2, 3) and (100, 200, 300) have identical rank signatures if they occupy the same percentile slots. This is Megethos-robust **by construction**, not by discipline — the scorer cannot be contaminated by P003 the way P001 and P002 can.
- **Sparse/binary feature structure.** Features with mostly-identical values (e.g. binary flags, sparse indicators) produce degenerate rankings where ties dominate, collapsing extremity differences. Use categorical projections (P010/P011/P012) instead.
- **Low-count populations** where rank quantiles are coarse. Below ~1000 objects, the rank granularity is too coarse for stable extremity measurement.

**Tautology profile:**
- **Not independent of P001/P002.** The underlying claim is still "these domains share a feature correspondence" — just measured through ranks instead of raw cosine. Using both P001 and P034 on the same hypothesis double-counts the distributional alignment signal. Pattern 1 (Distribution/Identity Trap) applies: if P001 gives ρ=0.9 and P034 gives a high score, check whether both are driven by the same formula-level overlap before celebrating.
- **Learning-time null ≠ inference-time null.** The built-in 2σ filter on the interaction matrix is a **learning discipline** — it rejects interaction cells that are noise given the observed pairings. It is NOT a post-hoc permutation null on the final score. To probe whether a batch-level coupling survives permutation, use P040 externally. Conflating the two is a protocol error.
- **Quantile-rank × degree-of-freedom coupling.** For tables where most objects have identical feature values (e.g. `rank` on ec_curvedata — 80% rank 0 or 1), the quantile map is nearly step-function. The rank-based transformation preserves less information than the raw numeric one. Check distribution shape before adopting P034 over P001.
- **Extreme-tail over-weighting in small samples.** `(q − 0.5).abs()` weights tails quadratically in a sense; with n < 1000 the top and bottom quantiles are dominated by 2-3 outlier objects, and their interactions drive the score disproportionately. Apply P043 bootstrap to confirm stability.

**Calibration anchors:**
- **Known rank-structure bridges.** Where rank signature across domains is a real invariance — e.g. F010 NF backbone's "small-disc NFs pair with low-conductor Artin reps" — P034 should resolve the signal. Untested on F010 as of this entry; candidate follow-up.
- **Modularity (F001) via P034 is weak.** Modularity is about L-function identity, not rank co-variation on arithmetic invariants. P034 has no principled reason to detect modularity; expect it to give no signal on pure EC↔MF modularity probes. If it does, either Pattern 5 applies (known bridge re-projected) or there is a leak.
- **Against P001 on the phoneme corpus (F021).** Phoneme framework gave ρ=0.95+ under P001 and was killed by P040. P034 on the same corpus should ALSO give a high score (ranks are aligned in the same trivial way the raw cosine is) — the 2σ learning-filter would not help here because the 5-shuffle null is too weak. This is the expected failure mode; confirms P034 is not a magic Megethos escape.

**Known failure modes:**
- **High-Megethos data gives decent-looking scores in noisy ways.** Rank normalization kills magnitude scale, but rank order can still track magnitude within a stratum. If two domains have strongly-correlated magnitudes, their rank signatures are also correlated — P034 sees this as "aligned extremity" and fires. Pre-decontaminate with P052 where applicable.
- **The interaction-matrix is a memory.** AlignmentCoupling learns from the sample it sees at init. If you change the population (e.g. add new objects, change filters) without re-initializing, the interaction matrix is stale. Pattern 19 (Stale/Irreproducible) at scorer-state level.
- **Sigmoid normalization compresses the tail.** Final score is `sigmoid(total_score * 5)` (line 297). This compresses high-magnitude couplings toward 1.0 and mid-range toward 0.5. Two distinct "very strong" couplings are indistinguishable in output; use the pre-sigmoid `total_score` if relative ranking matters.
- **5-shuffle null at init is noisy.** The 2σ filter estimates null mean/std from only 5 permutations (line 245). This is a permissive filter — the effective rejection rate is ~5% under pure noise. Treat the learned interactions as coarse, not definitive.

**When to use:**
- **Coupling-across-projection probes where Megethos has been a chronic confound** and P052 decontamination is infeasible (categorical or non-numeric features). P034 gives a rank-based floor that P001 doesn't.
- **Extremity-driven phenomena.** When the hypothesis is literally "extremes align" (e.g. high-Sha curves paired with low-regulator curves), P034's extremity weighting is the right shape.
- **As a corroborating scorer alongside P001.** If P001 shows a signal, P034 showing the same signal at rank level is weak corroboration (Pattern 3 Weak Signal Walk invariance evidence). If P001 shows a signal but P034 doesn't, the coupling is magnitude-mediated and likely Megethos-contaminated — Pattern 3 kill axis.
- **Exploratory first-pass on new domain pairs** where rank-order is known but absolute scaling is arbitrary (mixed-unit datasets).

**When NOT to use:**
- **Categorical/object-level coupling claims.** Use P010/P011/P012. Quantile rank is defined only for continuous features.
- **Small-n populations (n < 1000).** Rank granularity is too coarse; bootstrap (P043) dominates the signal.
- **Publication-grade findings without post-hoc P040 permutation null.** The built-in 2σ learning-time filter is not a substitute for inference-time null.
- **In place of P001 when you want raw cosine similarity.** P034 and P001 measure different things; P034 is not a cleaner version of P001 — it is a distinct projection with a different invariance surface.

**Relationship to other projections:**
- **P001 CouplingScorer — parent class.** P034 inherits `__init__`'s feature-normalization machinery but overrides scoring entirely. Running both jointly and comparing is diagnostic: agreement = robust distributional signal; P001-only = magnitude-mediated (Megethos-suspicious); P034-only = pure rank extremity (may indicate sparse/binary features in the data).
- **P002 DistributionalCoupling — sibling.** P002 adds kurtosis ratio on top of cosine; P034 replaces cosine entirely with rank. Different axes on what "distributional" means.
- **P040 F1 permutation null — orthogonal/complementary.** P040 tests the inference-time coupling under label shuffle; P034's internal 2σ filter tests the learning-time interaction matrix under shuffle. They answer different questions and do not substitute for one another.
- **P052 Prime decontamination — can precede.** If the domains have prime-factorization-mediated coupling, decontaminate first; otherwise P034 will inherit the contamination (Pattern 1 at rank level).

**Tensor manifest updates needed (on acceptance):**
```json
{
  "PROJECTIONS_append": {
    "id": "P034",
    "label": "AlignmentCoupling (rank-based extremity coupling)",
    "type": "feature_distribution",
    "description": (
      "Rank-based (quantile) coupling scorer with extremity weighting and "
      "a sign-agreement term. Megethos-robust by construction. Learns an "
      "interaction matrix per domain pair at init via 5-shuffle 2σ filter. "
      "Sigmoid-normalized output. Complements P001 (raw cosine) and "
      "P002 (kurtosis-extended cosine); does NOT replace either."
    )
  },
  "INVARIANCE_suggestions": {
    "F020": {"P034": -1, "note": "Megethos axis should give noise under pure rank normalization — P034's purpose is to survive where P001 dies."},
    "F021": {"P034": -2, "note": "Phoneme corpus — rank signatures track the magnitude signatures, same kill expected. Confirms P034 is not a magic escape."},
    "F010": {"P034": 0, "note": "Untested. Natural P034 anchor — rank-structure coupling across NF/Artin labels. Candidate for a future wsw_F010_P034 task."}
  }
}
```

**Pattern notes:**
- **Pattern 15 (Machinery is the Product):** this scorer was built into `coupling.py` and shipped without a catalog entry for weeks. An undocumented scorer is an artifact, not an instrument; cataloging it now is a Pattern 15 recovery.
- **Pattern 11 (Language Discipline):** I avoided "cross-domain" and "bridge" throughout. "Coupling across projections" is the replacement where needed.
- **Pattern 1 (Distribution/Identity Trap):** explicitly called out in the tautology profile — P001 vs P034 joint use must pass a shared-formula check, not a simple both-agree check.

---

## Provenance and discipline notes

- Reserved ID **P034** via `agora.work_queue.reserve_p_id()` at claim time (tick 10). This is the first catalog_entry task to exercise the new reservation infrastructure (landed tick 9). SessionD's parallel `catalog_artin_is_even` appears to have taken **P033** (not confirmed; sessionA's review will confirm the registry).
- Drafted against source code at `harmonia/src/coupling.py` (12,655 bytes, last-modified Apr 12). I re-read the AlignmentCoupling class (lines 182–298) tick-6 and this tick.
- No edits to `coordinate_system_catalog.md`; waiting for sessionA review before merge.
- No git push per worker boundary.

## Review request

APPROVE at P034 and merge to catalog (Section 1 after P002), OR request revisions. INVARIANCE suggestions are advisory — F010 P034 candidate is a natural follow-up WSW task if you want to queue it.
