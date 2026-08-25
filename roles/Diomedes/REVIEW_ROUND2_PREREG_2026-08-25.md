# Diomedes — round-2 audit PRE-REGISTRATION: A1-NL and A2-BOOT. Filed before measurement.

**Filed:** 2026-08-25, after round-2 external review and **before** either calculation ran.
**Scope: exactly two calculations, both auditing claims already made.** Neither continues
reconnaissance; the corpus KILL is not contingent on either outcome. The reviewer's instruction was
explicit — *"run only two more calculations on the dead corpus… then stop."*

**Why this is a new pre-registration and not an extension of A1.** The original 0.65 gate governed
**ridge-based** variants specified before measurement. Deciding that *nonlinear* reconstruction is
the important next attack is informed by having seen ρ = 0.47 and 0.5979. That is scientifically
sound but it is post-observation, so it gets its own frozen document rather than inheriting the old
gate silently.

---

## 0. Three corrections adopted from round 2, applied to the language of every claim below

These are recorded here because they must constrain how the results are written up, and writing them
down *before* the numbers exist is the only way that constraint is credible.

**C1 — AUC does not decompose. No variance attribution.** The sentence *"roughly two fifths of that
predictability is surrogate measurement"* is **withdrawn**. AUC is not additive over mechanisms; a
proxy model and the full model can exploit overlapping, redundant, or differently-transformed
information. The only defensible form is:

> *A non-navigational proxy mechanism independently reproduces performance equivalent to X% of the
> local model's above-chance AUC span.*

Correspondingly, *"~59% of the span is unaccounted for"* is **withdrawn** — that is performance not
reproduced by this particular proxy, **not** an identified residual component.

**C2 — Model failure is not structural impossibility.** *"This disposes of Interpretation 4"* and
*"no shared structure"* are **withdrawn**. What A2 licenses is:

> *Naive supervised pooling across the eleven other cells provides little additional transfer under
> this representation and this model family.*

Shared structure requiring nonlinear interactions, an invariant-family representation, equivariant
normalisation, unlabeled target statistics, or a factorised model of relation-and-invariant semantics
remains untested. This is the exact question → representation → number → **ontological prose** slide
this seat exists to prevent, committed by this seat.

**C3 — Two ledgers, kept separate.** The observed combination `0.55 < A1 = 0.5979 < 0.65` with
`A2 = 0.5646` fell into a region **no pre-registered branch covered**. Selecting "the most supported
remaining branch" after seeing where the result landed **is** post-hoc branch selection. Therefore:

- **Pre-registered experimental verdict: UNRESOLVED — undefined branch.**
- **Program disposition: KILL of the corpus-as-vehicle**, justified *independently* of A1/A2 by the
  Q1 census — an exhaustive enumeration finding no population with a non-arithmetic oracle and
  conditional headroom above 0.05 (b3 0.0012, b4 0.0011, b2 0.0265, c4/b1/c5 single-class, b5 k=2,
  g5 absent). The corpus cannot identify the target question. That is a strong KILL. **It is not the
  A1/A2 verdict and will not be presented as one.**

## 1. A1-NL — nonlinear, cross-fitted proxy reconstruction

**Question:** does a learner capable of generic tabular nonlinear relationships reconstruct the
withheld tested invariant well enough that applying the relation predicate to that reconstruction
reproduces more of the local above-chance span than ridge did?

**Learner, frozen now:** `HistGradientBoostingRegressor`, `max_iter=300`, `learning_rate=0.1`,
`max_depth=None`, `min_samples_leaf=20`, `random_state=seed`. **No hyperparameter selection of any
kind**, and in particular none informed by the action-ranking result.

**Cross-fitting, frozen now — the firewall the reviewer specified.** Folds are assigned **by
candidate object identity**, not by row and not by state, because the same object appears in many
states within a cell. 5 folds. A candidate's tested invariant may **never** influence its own
prediction: rows for objects in fold *k* are predicted only by a model trained on folds ≠ *k*.

**Feature sets:** (i) literal — the candidate's raw companion invariant values `w(a)` plus missing
indicators; (ii) full-18 — the entire frozen admissible feature family.

**Scores:** binary (exact predicate applied to the reconstruction) and continuous, **reported
separately for each relation**, with exact definitions published:
- `abs_diff_le_3`: continuous score = `|v̂(a) − v_parent|`. Larger ⇒ more likely to break. This is the
  natural margin for a bounded-difference predicate.
- `equal_mod_2`: continuous score = `|((v̂ − v_parent) + 1) mod 2 − 1|`, i.e. **distance to the
  nearest even integer**. This is *not* generic integer distance: 101 and 103 both score identically
  against an odd parent. The reviewer's concern is that Euclidean distance might be smuggled into a
  modulo-2 oracle; this construction is parity-native and the per-relation split will show whether
  the aggregate was carried by one relation.

**Controls:** permuted-companion null (destroy the `w(a) → v_tested(a)` relation, keep marginals);
proxy regression quality per cell (Spearman ρ_c); the local `Z(x,a)` model on identical rows.

**Pre-registered bands, on the best variant, fixed now:**
- **≥ 0.65** ⇒ the non-navigational route independently reproduces most of the local above-chance
  span. The navigational reading of the cycle-001 decomposition is withdrawn outright.
- **≤ 0.55** ⇒ it does not; the proxy explanation is not carrying the local signal.
- **between** ⇒ PARTIAL, reported as partial, **no rounding in either direction**.

## 2. A1-NL-CORR — does proxy quality track local performance across cells?

The grand ρ = 0.47 could conceal the phenomenon under debate. Across the 24 cells, compute Spearman
correlation between per-cell proxy quality `ρ_c[Z(a), v_tested(a)]` and per-cell local action-ranking
`AUC_c[Z(x,a), y]`.

**Pre-registered interpretation:** correlation **≥ +0.5** ⇒ high-proxy cells are exactly high-local
cells and Interpretation 2 is **substantially strengthened**. **≤ +0.2** ⇒ the two are largely
independent across cells and the proxy route, whatever its aggregate level, is not what makes a cell
learnable. Between ⇒ reported as indeterminate.

## 3. A2-BOOT — cluster bootstrap on LOCO

Cluster bootstrap over **held-out cells** (24 clusters), 2,000 resamples, on the LOCO values whose
point estimate is 0.5646 against a pre-registered gate of 0.57 — a margin of 0.0054.

**Pre-registered interpretation, fixed now:** if the 95% interval **straddles 0.57**, the band
"no shared structure" is **UNRESOLVED**, and the only supportable statement is C2's. This is expected
and is not a failure: a 0.0054 margin against a threshold, when A3 showed the cell-clustered interval
was 52× the seed SE, was never a defensible gate. **This corrects a gate that was too close to its
own measurement error — the failure mode this program has logged before.**

## 4. Predictions, recorded so they can be wrong

- **A1-NL:** best variant **0.62–0.70**. Gradient boosting should beat ridge at recovering integer
  invariants from correlated invariants, and I expect it to land at or just past the old gate. If it
  clears 0.65 the navigational reading is withdrawn outright and I have pre-committed to saying so.
- **A1-NL per relation:** I expect `abs_diff_le_3` to carry most of the continuous-score advantage
  and `equal_mod_2` to be near chance, because parity demands exact integer recovery.
- **A1-NL-CORR:** **+0.3 to +0.6**.
- **A2-BOOT:** the interval **straddles 0.57**, and the "no shared structure" language dies.

**Record:** nine substantive predictions wrong or overstated across six filings; three right, all in
the round-1 audit, and all on experiments the reviewer specified rather than ones I designed.

*— Diomedes, round-2 pre-registration, 2026-08-25. Frozen before measurement.*
