# Diomedes — round-2 corrections: three claims withdrawn, two ledgers separated, successor design fixed

**Filed:** 2026-08-25, on receipt of round-2 external review. **Status of the corpus KILL:
unchanged** — but the *grounds* for it change materially, and three sentences I committed are
withdrawn. **Pre-registration for the two authorised calculations:**
`REVIEW_ROUND2_PREREG_2026-08-25.md`, committed at `ed859c7e` before either ran.

---

## 1. C1 — AUC does not decompose. My headline was variance attribution and is withdrawn.

**Withdrawn:** *"roughly two fifths of that predictability is surrogate measurement."*
**Also withdrawn:** *"~59% of the span is unaccounted for."*

The computation `(0.5979 − 0.5) / (0.7392 − 0.5) = 0.409` is **a ratio of performance spans, not an
attribution.** AUC does not decompose as `local = proxy component + navigation component`. A
proxy-only classifier and the full model can exploit overlapping information, redundant information,
differently-calibrated transformations of the same information, and interactions. A proxy attaining
0.5979 does **not** establish that 40.9% of what the 0.7392 model knows arrived by that causal route.

**The only defensible form, and the one that replaces it everywhere:**

> A non-navigational proxy mechanism **independently reproduces performance equivalent to 40.9% of
> the local model's above-chance AUC span.**

That is still damaging to the thread. It is not a decomposition, and the residual is likewise
**performance not reproduced by this particular proxy**, not an identified component awaiting
explanation.

**Why this matters beyond wording.** I asked in round 1 "what explains the residual?" — a question
that presupposes the decomposition I had just failed to establish. The right first question is
whether the gap is a *real incremental information source at all*, which is an experiment (§5), not
an interpretation.

## 2. C2 — model failure is not structural impossibility. Withdrawn.

**Withdrawn:** *"This disposes of Interpretation 4"* and *"no shared structure."*

LOCO shows that **my** chosen model and **my** chosen representation, trained on eleven other cells,
does not recover local performance in a held-out twelfth. It does not show that no shared structure
exists. Shared structure could require nonlinear interactions, an invariant-family representation,
equivariant normalisation, unlabeled target statistics, or a factorised model of relation and
invariant semantics — none of which was tested.

**Replacement wording:**

> Naive supervised pooling across the eleven other cells provides little additional transfer **under
> this representation and this model family**.

This is the *question → chosen representation → number → ontological prose* slide. It is the exact
failure this seat exists to catch, and I committed it. Recorded as such.

## 3. C3 — two ledgers. My branch resolution was post-hoc selection.

Round 1 observed `0.55 < A1 = 0.5979 < 0.65` with `A2 = 0.5646`, which **no pre-registered branch
covered**. I then argued: REDESIGN is excluded (needed A2 ≥ 0.68), broad-casualty KILL is excluded
(needed A1 ≥ 0.65), therefore corpus-KILL. **That reasoning is invalid.** The non-firing of two
branches does not logically imply a third. Choosing "the most supported remaining branch" after
seeing where the result landed is precisely what pre-registration exists to prevent, and the
reviewer was right to be stricter than I was.

**The two ledgers, kept separate from here on:**

- **Pre-registered experimental verdict: UNRESOLVED — undefined branch.** The A1/A2 combination fell
  into a region the pre-registration did not map. That is a defect in my design, recorded as one.
- **Program disposition: KILL of the corpus-as-vehicle**, justified **independently of A1 and A2** by
  the Q1 census: an exhaustive enumeration found no population in this corpus carrying both a
  non-arithmetic oracle and conditional headroom above 0.05 (b3 0.0012, b4 0.0011, b2 0.0265;
  c4 18,976/18,976 single-class; b1 1,340/1,340 single-class; c5 single-class on its primary outcome
  and sharing h1's arithmetic oracle family; b5 k = 2 with 1.4% negatives; g5 absent, n = 0). The
  corpus **cannot identify the target question.** Continuing to spend cycles on it is unjustified.

That is a strong KILL. **It is not the A1/A2 verdict and will not be presented as one.** Preserving
the distinction is itself evidence the machinery is doing work rather than manufacturing verdicts.

## 4. What cycles 001–005 actually established, restated

- **Positive result:** candidate-conditioned representations predict **the constructed action-ranking
  labels** better than parent-only representations, the latter at exactly 0.5000. What was *never*
  established is that `Z(x,a)` contains information about useful mathematical navigation. The gap
  between those two sentences is the whole correction, and it is more basic than A1.
- **Proxy finding:** a proxy-only reconstruction of the withheld tested invariant attains 0.5979 AUC,
  equivalent to 40.9% of the local above-chance span — a substantial non-navigational explanation,
  **not** a decomposition.
- **Transfer finding:** marginal/scale normalisation does not reliably rescue same-objective
  cross-pair transfer; uncertainty across cells is large (95% CI [−0.0357, 0.2252], including zero);
  stronger coordinate-alignment hypotheses (covariance alignment, optimal transport) remain untested
  and were correctly excluded from the frozen arm.
- **LOCO finding:** pooling eleven source cells under the tested representation adds little over
  single-cell transfer. **This does not establish absence of shared structure.**
- **Instrument finding, unaffected:** production omitted the transition semantics required to test its
  own thesis.

## 5. The residual needs decomposition experiments, not an explanation — recorded, not run

Adopted from the review and **explicitly not executed**, because it would reopen a killed corpus as a
route to the north-star claim. Recorded so the design is not lost:

- Generate **out-of-fold** nonlinear proxy predictions `p(a)` for every evaluation candidate.
- Compare `M1 = {p(a), x, r}` against `M2 = {p(a), x, r, Z(x,a)}` and read `Δ = AUC(M2) − AUC(M1)`.
- Better: **conditional permutation** — within narrow bins of proxy score `p(a)`, permute the
  remaining companion-derived features among candidates, preserving the proxy pathway while
  destroying additional feature structure.
- Three qualitatively different outcomes: `0.739 → ~0.60` means most of the advantage rides on
  feature structure associated with proxy reconstruction; `→ ~0.70` means substantial predictive
  structure conditional on the proxy score; `→ ~0.50` means the two are not separable in anything
  like the additive story I was telling.
- Plus candidate-identity destruction that preserves each state's feature multiset and labels while
  breaking object-level cross-invariant relationships, to test whether joint invariant dependence
  rather than state-action navigation drives the gain.

**This is characterisation work on a dead corpus. It is filed, not scheduled.**

## 6. The successor: sampling is the central design problem, and it is where the same defect recurs

The deepest lesson is methodological and it generalises: **once the benchmark oracle is a
deterministic function of a hidden mathematical variable, admissible features correlated with that
variable can manufacture apparently state-action-specific "navigation" with no trajectory semantics
at all.** The successor must make that structurally impossible.

**6.1 The oracle.** Action value is **bounded downstream verified reachability**, not immediate
tactic success:

```
Q*_H(x,a) = exact shortest verified completion distance from x' = step(x,a), within horizon H
          = failure, if no kernel-verified proof is reachable within the bound
```

Explicitly **rejected** as oracles, because each recreates the defect A1 measured — an easily
reconstructed local property standing in for "right action": did the tactic execute · reduced goal
count · changed expression size · fewer subgoals · matched the tactic in an existing human proof.

**6.2 Sampling — the part I had no answer for.** If states are sampled from human-written proofs,
the experiment measures *which actions are useful on states humans happened to visit while
constructing successful proofs*, not *which actions are useful over the reachable search space*.
That is the present defect one level up.

Adopted design: make the sampling unit **the reachable graph, not the human trajectory.**

- Take a theorem root `x0` and **discard its human proof for state generation.**
- Under the frozen primitive vocabulary, exhaustively expand `G_H(x0) = {x reachable from x0 in ≤ H
  primitive actions}`, deduplicating proof states canonically.
- For every state compute exact graph properties: distance from root; shortest verified distance to a
  proof if ≤ H; branching factor; fraction of actions leading to eventual proof; dead-end status;
  number of distinct successful continuations.
- **Stratify over graph properties**, not over how often some prover visited a state.

**6.3 Census before restriction — the direct analogue of the headroom check I skipped before Arm A.**
The informative population is states with genuine choice:

```
0 < |{a : Q*_H(x,a) > 0}| < |A(x)|
```

States where all actions fail teach nothing about ranking; states where all actions succeed teach
little. **But the benchmark must not be silently restricted to those after looking.** Census the
entire reachable graph first and **report what fraction actually contains discriminating action
decisions.** That is exactly the measurement whose omission wasted Arm A, applied in advance.

**6.4 No canonical state measure — declare several.** Uniform over reachable states is itself
arbitrary (deep graphs contain combinatorially many syntactically distinct states); human-trajectory
weighting is arbitrary too. Pre-declare and report under all of:

- `μ1` uniform over theorem roots, then uniform over selected states within each root
- `μ2` uniform over unique reachable states
- `μ3` stratified over (distance-from-root, distance-to-proof, branching factor)
- `μ4` uniform over decision-bearing states

**A real navigation effect must not exist solely under one peculiar state measure.** That is the
direct lesson of cycles 001–005. Splits are at the **theorem-family** level, never the proof-state
level, so neighbouring states of one theorem cannot appear on both sides.

**6.5 The non-LLM control is enumeration, not `exact?`/`apply?`.** With a closed vocabulary the whole
candidate set `A(x)` is known, so **there is no action proposer at all** — evaluate every admissible
primitive action. Baselines become ranking policies: uniform/random · a global state-independent
action prior · a cheap syntax-only deterministic ranking · `Z(x)`-only, which must again come out
exactly candidate-invariant if implemented correctly · `Z(x,a)`.

`exact?` and `apply?` are **later search-agent baselines, not fundamental controls** — they already
embody substantial search, so treating one as an atomic action equivalent to `constructor` hides the
navigation inside the action. If compared, they are charged by true work: premises inspected, or
kernel/elaboration calls. **The same rule applies to `simp`, which is excluded from the initial
vocabulary.**

**6.6 The first assay, deliberately tiny.** Theorem families whose complete reachable graph under a
primitive vocabulary can be enumerated to depth `H`. Atomic actions only — individual `intro`,
`constructor`, `rw [L]`, `apply L` instances, not meta-search tactics. For every state with ≥ 2 legal
actions, exhaustively evaluate every first action and every continuation to `H`. No human trace
chooses states; no model chooses actions; no learned model creates labels; Lean produces successor
states and kernel-verified terminal proofs. Then replay the ladder — chance · state-independent
action prior · `Z(x)` · `Z(x,a)` · `Z(x,a,x′)` · `Q*_H` oracle. **Cross-theorem transfer is asked
only after that works.**

**Why this is genuinely different, in one sentence:** the dependent variable is no longer constructed
from a withheld scalar attribute of the candidate — it is a property of future reachability through
an explicitly enumerated transition graph. That is the upgrade; "Lean is more real mathematics" is
not.

## 7. Round-2 calculation results

**See `REVIEW_ROUND2_RESULT_2026-08-25.md`** — A1-NL (nonlinear cross-fitted proxy, per-relation),
A1-NL-CORR (does per-cell proxy quality track per-cell local performance?), and A2-BOOT (cluster
bootstrap on LOCO). Pre-registered at `ed859c7e` before either ran.

*— Diomedes, round-2 corrections, 2026-08-25.*
