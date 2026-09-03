# G. CAUSAL INTERVENTION MAP — Kouvaris et al. 2017

Directive §12: list every intervention; for each, say what was changed, what detector changed, what
acquisition changed, and what was held fixed. Then build only the causal graph the design actually
identifies. Directive §8: do not blur selection pressure and variation mechanism.

---

## 1. The interventions, exhaustively

There are **four arms plus two parameter sweeps**, and nothing else. Every one acts on the fitness
function or the environment.

| # | Arm | What is literally changed | Held fixed |
|---|---|---|---|
| 1 | **Control** — moderate switching | `K = 20000`, `λ = 0`, no noise | everything else |
| 2 | **Switching rate** | `K` swept, total generations pinned at 24×10⁶ | fitness form, operator, class |
| 3 | **Environmental noise** (jittering) | Gaussian `n_μ ~ N(0,1)` added to the **target vector `S`** every generation, scaled by `κ`; optimum `κ = 35×10⁻⁴` | operator, class, `K` |
| 4 | **L2 / weak connectivity** | cost term `λ·Σ b_ij²` added to fitness; optimum `λ = 38` | operator, class, `K`, noise |
| 5 | **L1 / sparse connectivity** | cost term `λ·Σ |b_ij|` added to fitness; optimum `λ = 0.22` | operator, class, `K`, noise |
| 6 | **Sensitivity sweeps** | `λ` and `κ` swept across ranges (Fig 4) | as above |

## 2. Directive §8, answered directly

> Does the intervention manipulate: developmental representation / mutation operator /
> genotype-phenotype mapping / selection history / environmental variability / connection cost /
> environmental noise / training distribution, or combinations?

| Candidate | Manipulated? | Note |
|---|---|---|
| developmental representation `B` | **NO — not manipulated. It is an OUTCOME.** | `B` changes in every arm, but always as an evolved response to a changed fitness function. It is never set, clamped, ablated or switched. |
| **mutation operator** | **NO** | `mutate_gene.m` and `mutate_weights_v2.m` are parameterless with hard-coded constants. No arm, sweep, appendix, preprint section or thesis Chapter 2 section varies a mutation rate or magnitude. |
| genotype–phenotype mapping | **NO, same as `B`** | The map *is* `B`; it is downstream of the intervention, not the intervention. |
| **selection history** | **YES** — arms 1, 2 | The order and duration of exposure to the three training targets. |
| **environmental variability** | **YES** — arms 2, 3 | Switching interval and target noise. |
| **connection cost** | **YES** — arms 4, 5 | Two functional forms, L1 and L2. |
| **environmental noise** | **YES** — arm 3 | |
| training distribution | **partly** — S1 only | The exhaustive 2^16 training-subset analysis varies which targets are in the training set, but **replaces evolution with Hebb's rule**, so it is not an evolutionary intervention. |

**The distinction the directive says not to blur, stated plainly.** Prometheus wants *evolution
changing the machine that generates future variation*. Kouvaris 2017 demonstrates *selection history
and cost pressures producing a machine that generates better-structured future variation*. The
machine changes; **what is manipulated is the pressure, never the machine.** Those are different
experiments and the second does not substitute for the first.

This is falsification question **F3 (`the manipulated variable changes selection rather than
variation machinery`) — TRUE**, and it is the load-bearing finding of this deliverable.

## 3. Per-intervention table (directive §12)

| Question | Arm 2 (`K`) | Arm 3 (`κ` noise) | Arm 4 (L2) | Arm 5 (L1) |
|---|---|---|---|---|
| What exactly was changed? | environmental switching interval | Gaussian noise on the target | `λ·Σb²` cost | `λ·Σ|b|` cost |
| What detector changed? | training/test χ² and the induced distribution; slow switching → memorisation of few targets, fast → under-fitting | test error reaches a minimum of 0.34 then over-fits more slowly | test error **flat** over evolutionary time — canalisation prevented | test error reaches **zero**; entropy converges to exactly 4 bits |
| What acquisition changed? | not separately reported for the `K` sweep | adapts faster than control; some targets still unreachable (outliers) | adapts faster than control; some targets still unreachable | **significantly** faster; reaches a phenotype otherwise inaccessible |
| Representation held fixed? | **NO** — it is the outcome | NO | NO | NO |
| Selection held fixed? | **NO** — this is what changed | NO | NO | NO |
| Environment held fixed? | NO (switching rate is the knob) | NO (target is jittered) | YES | YES |
| Mutation held fixed? | **YES** | **YES** | **YES** | **YES** |

The last row is identical across every column, and it is the reason this specimen cannot answer
HC-T01's question.

## 4. The causal graph the design actually supports

```
   intervention                     evolved                two readouts of ONE object
 (K, kappa, lambda)  ───────►    B_endpoint    ────┬────►  induced phenotype distribution  (Fig 3)
  selection / env                 (the G-P map)    │        = push-forward of uniform G through B
  side ONLY                                        │
                                                   └────►  generations-to-target under frozen B (Fig 5)
                                                            = hill-climb over the same G-space through the same B
```

**What is identified:** `intervention → B`, and `B → each readout`. The arms differ, and both
readouts differ with them.

**What is NOT identified, and must not be drawn:**

- `accessibility change → acquisition change`. There is no arm in which accessibility is perturbed
  while everything else is held fixed. Both readouts hang off the same `B`, so the design cannot
  distinguish mediation from common cause.
- Any temporal precedence claim. See `H_TEMPORALITY_ANALYSIS.md`.
- Any claim with an error term. The number of evolutionary replicates is unstated; only the
  acquisition assay (1000 runs) and the Hebbian enumeration carry replication.

**A sharper way to put the non-identification.** Given a frozen `B`, both readouts are deterministic
functionals of the same pair (`B`, `develop`). The detector is the push-forward of the uniform
measure on `G`-space; the acquisition assay is a hill-climb over that same space under that same map.
If `B` cannot express phenotype `s` from anywhere, hill-climbing under `B` will not find `s` either.
The paper observes exactly this agreement and reports it as a consistency check, correctly:
*"The outliers … indicate the inability of the developmental system to express the target phenotypic
pattern … This corresponds to the missing phenotype from the class we saw above in the evolved
phenotypic distributions."* That sentence is the two instruments agreeing about one object. It is
not evidence that one caused the other.

## 5. The one place in the whole recovered corpus where a variation operator *is* manipulated

Thesis **Chapter 3** (published as Rago, Kouvaris, Uller & Watson 2019, PLOS Comput Biol) sweeps the
mutation rate: `σ_μ ∈ {0.2, 0.01, 1×10⁻⁴, 1×10⁻⁵}`, with section 3.3.4 titled *"Low mutation rates
can enhance the evolution of adaptive plasticity in coarse-grained environments"*.

**It still does not give HC-T01 its cell, for three reasons:**

1. **Different system.** A population of 1000 individuals evolving continuous reaction norms against
   an environmental cue — not the modular GRN class, not SSWM, not the 8-pattern family.
2. **No sampled variation distribution.** The longitudinal quantity is *"goodness of fit of the
   evolving reaction norms to the current environment and all past selective environments over
   evolutionary time"*. A reaction norm is a deterministic curve read off the genotype across
   environments. It is a plasticity measure, not a distribution over offspring phenotypes. **Element
   A is absent.**
3. **The mutation rate is used as a learning-rate proxy, not as a mechanism ablation.** The thesis is
   explicit: *"the higher the mutation rate is, the higher the genetic change the population
   accumulates to a given environment (i.e., learning rate)"*. It is manipulated to change how fast
   the population tracks the environment — a *selection-dynamics* knob wearing an operator's
   clothing. Ablating a mechanism that shapes the structure of variation is a different act from
   scaling how much variation there is per generation, and the chapter does the second.

Recorded because it is the strongest thing in this corpus that could have been mistaken for
C-mechanism, and because a reviewer will ask.

## 6. What a reviewer should press on

- The claim that all four arms are selection-side rests on the absence of a mutation-rate parameter
  anywhere in the arms. That absence was checked three ways: a regex sweep of the article body for
  mutation-rate manipulation (zero hits outside a reference title), inspection of the two mutation
  functions in the recovered code (both parameterless), and the thesis figure list for Chapter 2
  (five figures, none a mutation sweep). If a reviewer finds a fifth arm, this deliverable is wrong.
- The `B`-mutation probability is stated as `1/15` in Methods, `1/2` in Results and `1` in code. The
  causal map does not depend on which is right, because none of them **varies across arms** — but a
  reconstruction does depend on it.
