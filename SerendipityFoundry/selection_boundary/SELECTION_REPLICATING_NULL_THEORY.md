# Selection-Replicating Null Theory

**The question.** Can an already-selected historical artifact have a
non-vacuous admission null *without* reproducing the process that made it
interesting?

**The answer.** Yes for one claim class, no for another, and for a third the
obstacle is factual and remediable rather than metaphysical. The boundary is
sharp and is drawn below.

This document was revised after independent adversarial review, which returned
**before** any verdict was stated (a deliberate process change; the previous
pass published a verdict while its review was still running). Three of my
initial formulations were wrong and are corrected in place, with the original
preserved in `FAILED_VERSIONS/`.

---

## 1. Definitions

* `D` — the selection sigma-field: **everything** knowable before a candidate
  became a candidate. All ledger records, all code, all prior analyses, every
  human decision, every adaptive mining query. `D` is deliberately maximal.
* `C` — the candidate, a `D`-measurable random element. Chosen by **any** rule,
  however hindsight-laden.
* `U` — post-commit public randomness (the beacon), independent of `D`.
* `theta` — **the entire realized test object**: statistic, threshold, the
  decoder from beacon bytes to an intervention, the support and law of `U`,
  the conditioning event, the tie rule, the censoring rule, the stopping rule.
* `phi_theta(c, u)` — the reject indicator.
* `S` — the selection functional (what the pipeline maximized).
* `nu_pipe` — the law of the artifact a complete pipeline nominates.

## 2. The Selection-Freedom Theorem

> **Theorem 1.** Let `C` be `D`-measurable and `U ⊥ D`. If
> `P_U(phi_theta(c,U)=1) <= alpha` **at the realized `c`**, then
> `P(reject) = E_D[ P_U(phi_theta(C,U)=1 | C) ] <= alpha` for **any**
> selection rule producing `C`.

The proof is one line of the tower property. Its entire content is *where the
bound is required to hold*.

**CORRECTION 1 (from review).** My draft required the bound *uniformly over
`c`* (`sup_c`). That is simultaneously **too strong** — `sup_c` equals 1 for
most tests worth running, so it would reject valid tests — and, as practised,
**too weak**, because registrants verify a bound *on average* and sincerely
believe they have it pointwise. The correct premise is the level **at the
realized candidate**, and it is *certifiable* (§4).

**CORRECTION 2 (from review). The source-of-randomness dichotomy is false.**
My draft claimed: selection is free when the null's randomness is created
after the candidate is fixed, and fatal when the null is a measure over the
space the candidate was selected from. Freshness of `U` is **necessary, never
sufficient**. Three counterexamples, all realizable on this substrate:

* **Selected support.** Draw a fresh beacon-uniform byte position and
  replacement; reject iff the trace is unchanged. Then, after mining `D`,
  narrow the intervention class to "positions in the executed region". `U` is
  still fresh and still independent of `D`, applied to a fixed `c` — and the
  rejection probability goes to 1. The randomness is fresh; its **support** was
  selected.
* **Selected statistic/threshold.** Fresh beacon-random inputs, but the
  threshold is set at a corpus quantile. No base measure appears anywhere, yet
  the threshold is `D`-measurable and calibrated to a corpus *average*.
* **Selected conditioning event.** Condition on the candidate's archive cell —
  when the archive (342 inserts / 12,490 rejects / 105 evictions) is itself a
  selection device on exactly that event, and eviction makes cell membership
  history-dependent.

In all three the registrant can truthfully say "my null uses randomness created
after the candidate was fixed" and be wrong.

> **Criterion (replacing the dichotomy).** Selection over `c` is free **iff**
> the entire test object `theta` is committed and hash-anchored **before** the
> beacon, and the level holds at the realized `c`.
>
> **SELECTION OVER `c` IS FREE. SELECTION OVER `theta` IS NOT.**

## 3. Genericity premises are banned

**CORRECTION 3 (from review).** Practical "pointwise" proofs on this substrate
almost always contain a hidden *"for a generic program"* step — an average-case
bound in disguise. Because **every byte sequence is a legal program**, the
corpus is a search engine for the exceptional set.

Measured, exactly, by enumerating the entire intervention support
(64 positions x 255 replacements = 16,320 mutants) on the real interpreter,
for the test "reject iff a single-byte perturbation leaves `(steps, output,
halt)` unchanged":

| candidate | exact `alpha(c)` |
|---|---|
| halts immediately (`JMP` self + padding) | **0.9694** |
| random 64B | 0.8398 |
| random 64B (other seed) | 0.8072 |
| loop-heavy | 0.1837 |
| all-NOP (every byte executed) | 0.1176 |
| dense arithmetic (ADD chain) | **0.0243** |

**Range: 0.024 to 0.969, a factor of 40.** No single pointwise claim covers
these. And note the direction that matters: a *generic* random program is
already ~84% inert, so a test premised on "few inert bytes" is mispriced for
essentially **every** program, not merely for adversarially selected ones.

> **Admissibility rule.** A level argument is admissible only if it is
> (i) an exact finite enumeration over `supp(U)`; (ii) an exchangeability/orbit
> argument carrying an **explicit stabilizer clause** and a conservative tie
> rule (`>=`, never a seeded tie-break); or (iii) a per-candidate certificate
> (§4). Any proof containing *generic*, *typical*, or *almost every* is an
> average-case bound and is rejected.

## 4. The Registered Conditional Level Certificate (RCLC)

The premise of Theorem 1 is **not** unverifiable. At registration time `c` is
known (it is `D`-measurable) and the law of `U` is declared. Therefore

```
alpha(c) = P_U( phi_theta(c, U) = 1 )
```

is a deterministic functional of two already-known objects. Evaluating it needs
**no fresh randomness** — the beacon is required only for the single real draw.
For single-byte interventions the support is 16,320 and `alpha(c)` is computed
*exactly*, in seconds (§3 is that computation).

> **RCLC.** Before the beacon, publish `hash(c)`, `hash(theta)`, and
> `alpha_hat(c)` — exact where the support is enumerable, otherwise a
> Clopper–Pearson upper bound — together with the hash of the certifying
> computation. **The Court debits `max(alpha_nominal, alpha_hat_upper)`.** If
> `alpha_hat_upper > alpha_nominal` the test is mispriced and must be
> re-specified before the beacon.

**Economic corollary.** Certifying a `1/K` tail costs `~K` evaluations, so
**certification cost lower-bounds the price**. That is the correct economics
for a conserved budget: a test you cannot afford to certify is a test you
cannot afford to buy.

## 5. Rarity claims: three constructions, not one

**CORRECTION 4 (from review).** My draft proposed a single "selection-
replicating null" whose unit is "the artifact the pipeline nominates". That
construction is **not an artifact test**.

Let the pipeline propose `X_1..X_N` and nominate `C* = argmax_i S(X_i)`. If the
null is `nu_pipe` (the law of a fresh pipeline's nominee), then `C*` and `C'*`
are i.i.d. draws from `nu_pipe`, so

```
p_rep = P(T(C'*) >= T(C*)) ~ Uniform(0,1)   EXACTLY, for every artifact, every T.
```

It never conditions on `C*`. Its only power is against *"the pipeline is not
the pipeline you modelled."* So:

| construction | tests | unit of inference | licenses an artifact claim? |
|---|---|---|---|
| **D1** replication null `nu_pipe` | pipeline-model misspecification | the pipeline | **no** |
| **D2** conditional/selective null `P(T \| S=s)` | the artifact | the artifact | yes, where `S` is a measurable event |
| **D3** rarity among outputs with `T` measurable wrt `S` | nothing | — | **provably vacuous** |

**D3 is doubly dead.** If `T` is the very quantity the pipeline maximized, then
conditional on nomination `T(C*) = max_i S(X_i)` by construction, `Var(T|S)=0`,
and the p-value is Uniform with power exactly `alpha` against *every*
alternative. Escaping it requires an **orthogonality certificate**: a
pre-registered argument that the claim statistic is not a function of the
selection functional.

## 6. The inflation law for incomplete replay

Matching operator chain, generation count and population size fixes only the
*proposal kernel* `Q`. The nominee's law is `Q` reweighted by survival. Omitting
a stage that retained a competition fraction `q` inflates the level by `~1/q`,
and **omissions compose multiplicatively**.

Measured in the toy harness (`toy_selection_bias.py`), true search depth
`N = 100`:

| replay assumes | realized rejection (target 0.05) |
|---|---|
| n = 100 (correct) | 0.052 |
| n = 50 | 0.100 |
| n = 20 | 0.220 |
| n = 10 | 0.338 |
| n = 1 | 0.830 |

**Undercounting the historical search is directly and monotonically
anti-conservative.** Two-stage selection shows the same law: replaying only the
inner stage gives 0.506 against 0.0495 for the full replay.

> **Requirement.** Every registered rarity claim publishes a **retention
> ledger**: per stage, cardinality in and out, hence the factor, hence
> `K_eff = K / prod(1/q_i)`.

## 7. Human attention, and what "unstateable" actually means

**CORRECTION 5 (from review), and the most important one.** My draft argued: the
five candidates were nominated by adaptive model-driven mining; that is not a
function of preserved inputs; therefore rarity claims about them are
retrospectively unstateable. **The middle step is a non sequitur.**

Selective inference does not replay the analyst. It conditions on the selection
**event**.

> **Theorem 2.** If the selection `S` is measurable with respect to *any*
> sigma-field `G`, then a null computed conditional on `G` has valid level for
> **every** selection rule in `G`. One never needs to know which rule was used,
> and conditioning on a *superset* is conservative, not invalid.

So the operative question is **not** "was the nomination rule a function?" but

> **is the sigma-field the miner consulted BOUNDED strictly inside `sigma(D)`?**

For the five frozen candidates the answer is factual, and it is no: the
archaeological mining **read the raw JSONL ledger files directly with ad-hoc
code**, bypassing any query interface, so no access log bounds `G`. The correct
status is therefore

    INADMISSIBLE FOR LACK OF A BOUNDED SELECTION SIGMA-FIELD

— a *factual and remediable* status, not a metaphysical impossibility. **The
remedy is architectural**: route future mining through a logged query
interface, so that `G` is bounded by construction and `G`-conditional rarity
nulls become available.

Representability of human attention, per option:

| substitute | recovers | does not recover |
|---|---|---|
| contemporaneous logged rule | the rule, if one existed | nothing here: none was logged |
| reconstructed ranking function | a *modern* nomination rule | tests a **different claim** — it did not generate the artifact |
| blinded replay panel | a fresh nomination distribution | the original *unblinded* decision; blinding changes the functional |
| external frozen procedure | future admissibility | anything retrospective |

## 8. What survives: the candidate-conditional route

Measured (`toy_candidate_conditional_randomization.py`), with the specimen
chosen as the maximum of `n` draws **on the very statistic later reported** —
the most hindsight-laden selection possible — and a fresh randomized
intervention on clones with assignment drawn after the specimen is fixed:

| historical selection depth | rejection rate (null true) |
|---|---|
| n = 1 | 0.0533 |
| n = 100 | 0.0553 |
| n = 1,000 | 0.0567 |
| n = 200,000 | 0.0647 |

Level is flat in selection intensity (the endpoints differ by ~2 SE at 1,500
trials). Power against real effects: 0.215 / 0.585 / 0.979 at effect sizes
0.5 / 1.0 / 2.0 — the test is not vacuous.

**But class E is free with respect to SPECIMEN selection only.** Reporting the
best of 20 observables on the same specimen rejects at **0.648**; letting the
beacon select the observable restores **0.0525**. Class E therefore requires,
in addition to Theorem 1: `theta` committed pre-beacon (§2), an RCLC (§4), and
— where a menu is used — beacon selection from a committed menu whose members
are individually valid *and* across which the scientific claim is invariant.

## 9. Implications for stackvm-v1

The machine pipeline is unusually well instrumented. A single
`source_tree_hash` (`50b5c232`) covers all 261 experiments; seeds, budgets,
terrains and operator configs are recorded and hashed; `EXPERIMENT_FINISHED`
carries `best_artifact_id`, an explicit frozen max-of-N nomination.
Classification: **M1, M2, M5 = SR0; M3, M6 = SR1; M4, S1 = SR2; H1, H2, H3 =
SR3.**

Two bounding findings:

* **M3 is SR1, not SR0.** 85 of 87 selections were fully tied, so the winner is
  a seeded-uniform draw *over the realized pool*. Perturbing pool membership by
  one member re-randomizes the winner with probability `1/(m+1)`; across 85 tied
  selections a free-running replay diverges almost surely. Replay must be
  **pool-conditional**, re-deriving each selection from its recorded pool.
* **M4 is capped at SR2 by a hazard that is unfalsifiable from the record.**
  Verified in source: `adapter.py:215-239` returns `fitness=None,
  behavior=None` when `halt == "wall"`, and `simple_grid.py:69` then refuses
  insertion with `detail="no_fitness"` — so whether an evaluation is *eligible
  for nomination at all* depends on `time.perf_counter()` versus host CPU
  contention, not on `(code, inputs, max_steps)`. Empirically the corpus shows
  **zero** wall records and **zero** `no_fitness` rejections across 71,683
  executions. That is *not* reassurance: the era declared `adapter_version
  0.1.0`, and the current source states that **0.1.0 counted a walled case as
  simply "not passed"** — under the era's own semantics a wall leaves a record
  indistinguishable from ordinary step-exhaustion. Absence of evidence here is
  not evidence of absence, and the channel cannot be raised above SR2.

## 10. Implications for future substrates

1. **Log the query sigma-field.** The single highest-value architectural change:
   route all mining through an interface that records what was consulted. It
   converts rarity claims from inadmissible to admissible (§7).
2. **Make the selection functional recorded-measurable.** Run scored
   evaluations with `timeout_s = None` so the deterministic step meter is the
   only termination bound, and emit an explicit censoring indicator.
3. **Freeze the nomination function** and record it per run, as `M5` already
   does. `M5` is why anything here is replayable at all.
4. **Publish retention ledgers** from the start; `q_i` cannot be reconstructed
   later.
5. **Require RCLCs** rather than genericity arguments.

## 11. Relationship to conserved-risk pricing

The ledger debits `1/K` per registered test and bounds
`E[# false admissions] <= ALPHA_LIFE`. Three couplings established here:

* **RCLC changes what is debited**: `max(alpha_nominal, alpha_hat_upper)`, so a
  mispriced test is refused at registration rather than silently overspending.
  The dead-code family shows the exposure: a test priced at `2.4e-4` whose true
  level at a searchable candidate is `~0.97` would consume **nine times the
  entire lifetime budget** in one purchase.
* **The inflation law changes the effective threshold**: `K_eff = K / prod(1/q_i)`.
* **Certification cost lower-bounds the price** (§4), which makes very small
  `alpha` genuinely expensive rather than merely a number in a field.
