# C. HISTORICAL PHYSICS SPEC — Kouvaris et al. 2017

Every parameter carries a class: `VERIFIED_EXACT`, `VERIFIED_RANGE`, `VERIFIED_CONTRADICTORY`
(two primary sources disagree), `INFERRED`, `UNSPECIFIED`, `ASSUMED_FOR_RECONSTRUCTION`.
Sources: `PAPER` = article XML Methods/Results; `S1` = S1 Appendix; `CODE` = recovered MATLAB
(`code/KostasKouvaris_Evolvability`, README *"Implementation for Thesis Chapter 1"*).

**Directive §3 says do not paper over ambiguity. There is more of it than the paper suggests, and
the code is what exposed it.** Three parameters are contradictory across primary sources, and the
number of evolutionary replicates is never stated anywhere.

---

## 0. Their question, in their words, before translation (directive §2)

Frozen from the abstract, Table 1 and S1 before any Prometheus vocabulary is applied.

| Their term | Their operational meaning |
|---|---|
| **evolvability** | the *"predisposition to produce fit phenotypes in novel environments"* — Table 1(a), where they gloss it as *facilitated variation* and contrast it with *"just canalisation of past selected"* phenotypes. Operationalised two ways: the match of the induced phenotype distribution to the class, and generations-to-target on unseen environments. |
| **generalisation** | the learning-theory sense: producing an appropriate response to *novel* inputs by capturing regularities of the training set rather than memorising it. Operationalised as **test error**, the χ² lack of fit between the induced phenotype distribution and the distribution over *all 8* class members. |
| **developmental organisation** | the matrix **B** of gene-regulatory interactions, and only B. It is *"the free parameters of the developmental model that determine the functional organisation of development"* (S1). |
| **phenotypic variation** | the *distribution over adult phenotypes* induced by developing a **uniformly random** set of embryonic phenotypes through a fixed B. Their words: *"what phenotypes the evolved developmental constraints and biases B are predisposed to create starting from random initial gene expression levels, G"*. |
| **training environments** | the 3 target patterns actually selected for during evolution. Their χ² "training error" is measured against these. |
| **unseen / test environments** | the remaining members of the 8-pattern class, never selected for. The class is *defined by construction* as all combinations of 4 independent binary modules. |
| **over-fitting / canalisation** | training error keeps falling while test error rises. They label the moment test error first rises as where *"early stopping would be ideal"*. |

**Note on §21.** The learning language is the authors' analogy. Stated computationally and with no
cognition words, the claim is: *evolution under a finite set of structured environments produces a
G→P map whose induced phenotype distribution concentrates on the module-combinatorial family, and
that map subsequently reaches unselected members of that family faster.* That is a computational
phenomenon and is treated as one throughout.

---

## 1. Genotype

| Item | Value | Class | Source |
|---|---|---|---|
| Genotype | pair `[G, B]` | `VERIFIED_EXACT` | PAPER Methods |
| `G` | direct effects on the embryonic phenotype, `G = ⟨g_1 … g_N⟩` | `VERIFIED_EXACT` | PAPER, S1 |
| `G` domain | **CONTRADICTORY**: PAPER Methods enforces `g_i ∈ [−1,1]` continuous and the detector draws G in the continuous hypercube; **S1 declares `g_{t,i} ∈ {−1,1}` discrete** | `VERIFIED_CONTRADICTORY` | PAPER vs S1 |
| `B` | `N×N` real matrix of regulatory interactions | `VERIFIED_EXACT` | PAPER, S1 |
| Initialisation | *"Both G and B are initialised at zero"* | `VERIFIED_EXACT` | S1 |
| `N` | **16** phenotypic traits (4 modules × 4 traits) | `VERIFIED_EXACT` | S1 |

**Caption inconsistency, recorded not smoothed.** Fig 2's caption says the initial structure
*"represented all possible phenotypic patterns equally (here 2^12 possible phenotypes)"*, and S1
Fig B repeats `2^12`. But N = 16, and the entropy discussion says the distribution *"reduces from
16 bits (the original phenotype space) to four bits"*. 16 bits is 2^16. **`2^12` is unreconciled
with the rest of the paper** and is tagged `UNSPECIFIED`. It does not affect any conclusion here,
but a reconstruction must pick one and say which.

## 2. Development (the G→P map)

`VERIFIED_EXACT` from S1, except where noted.

```
P_0 = G
P_{t+1,i} = P_{t,i} + tau1 * sigma( sum_j b_ij * P_{t,j} ) - tau2 * P_{t,i}
sigma(x)  = tanh(alpha * x)
P_adult   = P_T
```

| Parameter | PAPER/S1 | CODE | Class |
|---|---|---|---|
| `tau1` (max expression rate) | 1 | 1 | `VERIFIED_EXACT` |
| `tau2` (degradation rate) | 0.2 | 0.2 | `VERIFIED_EXACT` |
| `alpha` (sigmoid gain) | **0.5** (S1) | **0.3** in `develop_v2.m`, with `%0.5` left commented beside it | `VERIFIED_CONTRADICTORY` |
| `T` (developmental steps) | **10** (S1) | **15** in `GRN.m` | `VERIFIED_CONTRADICTORY` |

Both disagreements are visible in the committed code as a changed value with the published value
left commented out. That is the signature of a parameter that moved late. A reconstruction must
run both and report both.

## 3. Variation operator — **identical in every arm, and this is the load-bearing fact**

| Item | Value | Class | Source |
|---|---|---|---|
| Mutation on `G` | add `μ1 ~ U[−0.1, 0.1]` to **one** gene `i` chosen uniformly at random; hard-bound `g_i` to `[−1,1]` | `VERIFIED_EXACT` | PAPER Methods; `mutate_gene.m` matches exactly (`mm = 0.1`, `randi(length(G))`, `min(max(.,-1),1)`) |
| Mutation magnitude on `B` | each `b_ij` independently `+ U[−0.1/(15N²), 0.1/(15N²)]` | `VERIFIED_EXACT` | PAPER Methods; `mutate_weights_v2.m` computes `mm = 1/150` then `B + m/(l^2)`, i.e. `0.1/15/N²` — an exact match |
| **Probability that `B` mutates per step** | **THREE-WAY CONTRADICTION**: PAPER Methods says **1/15**; PAPER Results says *"in half the reproduction events"* i.e. **1/2**; CODE `mutate_weights_v2.m` has `mr = 1`, i.e. **every step** | `VERIFIED_CONTRADICTORY` | PAPER Methods vs PAPER Results vs CODE |
| Selection regime | strong selection, weak mutation (SSWM); mutant replaces parent iff strictly fitter | `VERIFIED_EXACT` | PAPER Methods |
| Rationale given | so that results *"do not require lineage-level selection"* — a simple hill-climber suffices | `VERIFIED_EXACT` | PAPER Methods |

**The magnitude formula in the published Methods is a transcription of the code** (`0.1/15/N²` is
literally `mm/l^2` with `mm = 1/150`), which is strong evidence the code is the right implementation
family. That the *probability* is stated as three different numbers in three primary sources is
therefore a genuine defect in the record, not a version mismatch I can dissolve.

**No arm of any experiment changes any of the above.** `mutate_gene.m` and `mutate_weights_v2.m`
contain hard-coded constants with no parameter passed in, and no experiment in the paper, the
preprint, the S1 or thesis Chapter 2 varies a mutation rate or magnitude. This is the single most
important fact for `G_CAUSAL_INTERVENTION_MAP.md`.

## 4. Population

| Item | Value | Class |
|---|---|---|
| Population | **a single genotype** `[G,B]`, described as *"the average genotype of the population"* | `VERIFIED_EXACT` |
| Population size | n/a — there is no population in the algorithmic sense | `VERIFIED_EXACT` |

Consequence for the D-ladder: any ladder rung phrased as *"population-wide"* has to be reinterpreted
for this specimen, because there is no standing population and therefore no population-wide variance
to measure. This is handled explicitly in `E_D_LEVEL_ADJUDICATION.md` §2.

## 5. Fitness

`f = b − λ·c`, `VERIFIED_EXACT` in form.

- Benefit `b` from the inner product `P_a · S` with `P_a` normalised by `τ1/τ2`, so `b ∈ [0,1]`.
- Cost `c` is either `Σ|b_ij|` (**L1**, favours sparse connectivity) or `Σ b_ij²` (**L2**, favours
  weak connectivity). `VERIFIED_EXACT`.
- The exact functional form of `b` is given as a display formula in the XML and is not transcribed
  here; a reconstruction must read it from the XML rather than from this document.

## 6. Environments

| Item | Value | Class |
|---|---|---|
| Target | binary vector `S = ⟨s_1 … s_16⟩`, `s_i ∈ {−1,1}` | `VERIFIED_EXACT` |
| Class construction | 4 independent modules × 4 traits; each module has 2 complementary states → `2^4 = 16` patterns; the 8 bitwise complements are discarded as degenerate, leaving **8** | `VERIFIED_EXACT` (S1) |
| Base pattern | `(− + − + − − + + − + + − − − − −)` split into 4 modules | `VERIFIED_EXACT` (S1) |
| Training set | **3** patterns, given explicitly in S1 eq. (2) | `VERIFIED_EXACT` |
| Test set | all 8 class members (training set is a subset) | `VERIFIED_EXACT` |
| Switching | target changes every `K` generations, cycling the training set | `VERIFIED_EXACT` |
| `K` (control) | **20000** | `VERIFIED_EXACT` |
| Epoch | `N_T × K` generations, `N_T = 3` → 60000 generations per epoch | `VERIFIED_EXACT` |
| Run length (main arms) | **150 epochs** = 9×10⁶ generations | `VERIFIED_EXACT` |
| Run length (K-sweep) | total generations fixed at **24×10⁶** while `K` varies | `VERIFIED_EXACT` |
| CODE equivalents | `on_period = 4000` (=K), `epochs = 200`, `t_max = epochs*N*on_period = 2.4×10⁶` | `VERIFIED_CONTRADICTORY` with the paper's K and epoch count |

## 7. Intervention arms (four, plus two sweeps)

| Arm | Knob | Value | Class |
|---|---|---|---|
| Control | moderate switching | `K = 20000`, `λ = 0`, no noise | `VERIFIED_EXACT` |
| Environmental switching rate | `K` | swept; total generations held at 24×10⁶ | `VERIFIED_RANGE` |
| Environmental noise ("jittering") | `κ` | Gaussian `n_μ ~ N(0,1)` added to the target `S` each generation, scaled by `κ`; optimum **`κ = 35×10⁻⁴`** | `VERIFIED_EXACT` at the optimum; sweep `VERIFIED_RANGE` |
| L2 / weak connectivity | `λ` on `Σb²` | optimum **`λ = 38`**; insensitive over `[10, 38]` | `VERIFIED_EXACT` |
| L1 / sparse connectivity | `λ` on `Σ|b|` | optimum **`λ = 0.22`**; generalisation error 0 over `ln(λ) ∈ [0.15, 0.35]`; fails at `λ = 0.4` | `VERIFIED_EXACT` |

**Every knob is on the fitness function or the environment. None is on the variation operator.**

## 8. Replication — the largest single gap

| Quantity | Value | Class |
|---|---|---|
| Evolutionary replicate runs behind Figs 2, 3, 4 and S1 Figs A–D | **never stated** | `UNSPECIFIED` |
| Seeds | never stated; the string "seed" occurs **0** times in the article body | `UNSPECIFIED` |
| Uncertainty on any longitudinal trajectory | **none reported** — no error bars, no bands, no interval | `VERIFIED_EXACT` (as an absence) |
| Replication in the recovered code | `GRN.m` has a single `for lambda = 0:0` loop and **no seed or replicate loop** | `VERIFIED_EXACT` |
| Adaptation-rate assay (Fig 5) | **1000 independent runs** per selective environment per arm | `VERIFIED_EXACT` |
| Training-set enumeration (S1 Fig, S5) | all `2^16 = 65536` subsets, **with error bars** | `VERIFIED_EXACT` |

The only error bars anywhere in the work are on the exhaustive training-set analysis, and that
analysis **replaces evolution with Hebb's rule** for tractability (S1: *"Hebbian learning was used
here for computational tractability (65536 possible combinations)"*). So the generality claim rests
on a Hebbian surrogate, and the evolutionary trajectories rest on an unstated and plausibly
single run per arm.

**Direction of this confound.** An unreplicated trajectory cannot be shown to exceed its own noise.
It pushes *against* the authors' claims being safely established, not in favour, so it does not
manufacture their positive result — but it does mean no interval on Fig 3 can be inherited, and any
Prometheus reconstruction must generate its own noise floor from scratch.

## 9. Acquisition evaluation (Fig 5)

| Item | Value | Class |
|---|---|---|
| Protocol | take the evolved `B`, **freeze it**, re-initialise `G` uniformly at random, evolve `G` only | `VERIFIED_EXACT` |
| Budget | 2500 generations, *"empirically found to be sufficient"* | `VERIFIED_EXACT` |
| Replication | 1000 independent runs per (environment × arm) | `VERIFIED_EXACT` |
| Statistic | generations to first attainment of maximum possible fitness | `VERIFIED_EXACT` |
| Censoring | failures assigned the ceiling value 2500 | `VERIFIED_EXACT` |
| Targets | all 8 class members, including the 5 never selected for | `VERIFIED_EXACT` |

## 10. What a faithful reconstruction must decide before running

1. `B`-mutation probability: 1, 1/2, or 1/15 (three primary sources, three answers).
2. `alpha`: 0.3 or 0.5.
3. `T`: 10 or 15.
4. `G` domain: continuous `[−1,1]` or discrete `{−1,1}`.
5. Phenotype category count: `2^12` or `2^16`.
6. Whether `G` is mutated at all during the main runs, or clamped to the current target. The
   published Methods describe a point mutation on `G`; **the committed `GRN.m` sets `G = S'`
   ("Equilibrated Gs") at each environmental switch and has `mG = mutate_gene(G)` commented out**,
   so in the committed configuration only `B` varies. Tagged `VERIFIED_CONTRADICTORY`. This is the
   most consequential of the six, because it changes what the evolutionary process even is.
7. Number of replicate runs, which no source supplies.

None of these ambiguities changes the adjudication in `E_D_LEVEL_ADJUDICATION.md`, because that
adjudication turns on *what was measured and against what*, not on parameter values. They matter
only if Prometheus reconstructs the specimen, which `O_SFE_CALIBRATION_PROPOSAL.md` costs out.
