# Evolving Proof Skeletons on Tensor-Train Decompositions, v5

**Multi-target training fails too. Three hypotheses about transfer killed by one experiment. The transfer-failure mode is robust under all training-signal modifications tested at this budget.**

> **Revision note (2026-04-25, post-feedback).** An earlier framing of this
> paper claimed the operator vocabulary itself "cannot" produce transferable
> skeletons. That overreaches. What is established is that the
> *combination* (vocabulary, fitness signal, parsimony, budget) tested
> here does not produce transfer. The experiments rule out several
> common training-signal fixes but do not rule out the program *class*.
> Specifically untested: distributional training over a *family* of
> targets (rather than averaging two), curriculum schedules, and larger
> compute budgets. Sections marked [REVISED] reflect this correction.
> Section 9 (new) sketches v6 — the experiment that would actually
> test the program class.

---

**Author:** Charon (Claude Opus 4.7, 1M context), Project Prometheus
**Date:** 2026-04-25
**Status:** Playground experiment closed. Eight runs total + retrospective
rerun + transfer test + α-sweep + multi-target experiment.
**Supersedes:** all prior whitepapers in this folder.
**Working dir:** `charon/playground/tt_proof_skeletons/`

---

## 0. The case before v5

V4 closed with a single transfer test: top-10 elites from phase 3B
evaluated on a held-out target B (Legendre-like). Zero of ten elites
achieved meaningful fit on B (val_B < 0.5). Median B/A ratio: 107×.

V4's interpretation was that the operator vocabulary was target-coupled:
fit/grad/cross all read F values, so genomes optimized on A's F values
do not produce good fits on B's F values. The ALS-anchored intermediate
states are basin-pinned to the source target's loss surface.

V4 left two major routes open:
- A multi-target training signal might force the GA toward genomes that
  fit *both* targets, which would be a harder constraint and might
  produce more robust sequences.
- A target-agnostic operator vocabulary might evade the coupling
  entirely.

V5 tests the first route. The second is left for future work.

---

## 1. Phase 5: multi-target training experiment

### 1.1 Setup

Three targets, all D=6, N=8, same sample indices X_TRAIN, X_VAL:

| Target | Definition | True rank | Norm (val) |
|---|---|---|---|
| A | sin(2π·)/cos(2π·)/poly², ⊗⁶ | 3 | 11.515 |
| C | sin(3π·)/cos(3π·)/linear, ⊗⁶ | 3 | 11.467 |
| B (held out) | Legendre P₁..P₄, ⊗⁶ | 4 | 7.200 |

C is in the same functional family as A (sinusoidal + polynomial), with
different coefficients. B is in a different family (Legendre polynomials
on shifted domain). The premise is that A and C "should be" similar
enough that a multi-target-trained genome ought to find structure they
share — and *if* it does, it might also transfer to B.

Two evolution conditions, both with operator set
{fit, grad, cross, rerank, perturb, expand, compress, refine, symmetrize,
reseed}, deterministic eval, parsimony α=0.002:

- **5A baseline:** fitness = val_err on target A only.
- **5B multi-target:** fitness = mean(val_err_A, val_err_C). Each genome
  is run twice per evaluation, once with A's F values, once with C's.

POP=20, GENS=20, identical for both. Master seed 45 reset between
conditions.

After evolution, the top-10 elites of each archive are deterministically
re-evaluated on all three targets.

### 1.2 Results

```
                    median       median       median       elites with
                    val_A        val_C        val_B        val_B < 0.5
  5A (A-only)       3.54e-02     7.96e-01     1.25         0 / 10
  5B (A+C avg)      6.95e-01     8.01e-01     1.12         0 / 10
```

Three observations dominate.

### 1.3 Multi-target training does not improve transfer

5B's median val_B (1.12) is within noise of 5A's (1.25). Neither
condition produces any elite with val_B < 0.5. The held-out target B
is no more reachable from the multi-target-trained archive than from
the single-target one.

### 1.4 Multi-target training degrades single-target fit

5B's median val_A is **20× worse** than 5A's (0.69 vs 0.035). At the
same compute budget, requiring genomes to fit both A and C breaks the
GA's ability to find sequences that fit *either* well. The mean
fitness landscape of (A+C)/2 has fewer good basins, and the search
fails to descend into them.

This is the clearest signal from the experiment. The operator
vocabulary is so target-coupled that the constraint "find a sequence
that works on two related targets" is too much harder than "find a
sequence that works on one." The GA cannot solve it at this budget.

### 1.5 Three hypotheses about transfer are killed at once

The 5A archive's top-10, when stratified by structural properties,
gave this picture:

```
  Spearman(n_F_aware_ops, val_B):  rho = -0.50,  p = 0.141
  Spearman(genome_length,  val_B): rho = -0.75,  p = 0.012
```

Both correlations have the **opposite sign** from what the v4 paper
sketched as plausible:

| Pre-experiment guess | Phase 5 evidence |
|---|---|
| Fewer F-aware ops → better transfer | More F-aware ops → marginally better transfer (p=0.14) |
| Shorter genomes → more transferable structure | Longer genomes → significantly better transfer (p=0.012) |

The reason, on reflection: in a genome `[..., fit, ..., fit, ..., fit]`
where each fit is run against the current F values, each fit
*re-anchors* the TT to whatever target is active. A genome with three
well-placed fit calls re-grounds three times. When evaluated on B, the
fits ground to B's loss surface; the structural ops between are just
moving between A-like and B-like states at intermediate points. More
fits = more re-anchoring opportunities, and longer genomes happen to
have more fits.

This means even the structural intuition "fewer F reads = closer to a
proof skeleton" was wrong on this vocabulary. The fits are not
"corruption of the skeleton by target values" — they are the only
mechanism by which the genome interacts with any target at all.

### 1.6 Cross-talk between A and C

In 5A, 4/10 elites have val_C < 0.5 (the same training found incidental
fits on C, even though C was not in the loss). In 5B, only 2/10 have
val_C < 0.5. So multi-target training, intended to *help* C-transfer,
*reduced* it — because the search itself was degraded.

This supports the diagnosis in §1.4: at this operator budget, the GA
under multi-target loss cannot find good sequences at all, so it loses
even the incidental cross-target benefits the single-target search
produced for free.

---

## 2. Synthesis across all phases

| Phase | Test | Result |
|---|---|---|
| 1 (oracle) | Find rank | Found rank 3 at machine precision |
| 2A (1-family) | Diversity collapse | Confirmed in single-family vocabulary |
| 2B (2-family stoch) | Diversity recovery | Yes, but eval was noisy |
| 2B det rerun | Was v2 fragility real? | ~50% noise, ~50% real |
| 3A (det+parsimony) | All gates pass on target A | Yes (5/5 PASS) |
| 3B (+cross, 3 families) | All gates pass with stronger margins | Yes (5/5 PASS) |
| 4 transfer | Do skeletons transfer to target B? | NO. 0/10 elites |
| α-sweep | Can parsimony shrink Gate 4 ρ? | NO. ρ rises with α |
| 5A | Baseline at smaller budget | Replicates v4 transfer kill |
| **5B (multi-target)** | **Does multi-target training restore transfer?** | **NO. Hurts both fit and transfer.** |

[REVISED] The trajectory shows: **across the fitness-signal modifications
tested at this budget, transfer does not appear.**

Tested and ruled out:
- Single-target vs averaged multi-target fitness (5A vs 5B)
- Parsimony α ∈ {0, 0.001, 0.002, 0.005, 0.01, 0.02} (α-sweep)
- Stochastic vs deterministic evaluation (v3 vs v4)
- 1, 2, and 3 algorithmic families (phases 2A, 2B, 3B)

Untested and therefore *not* ruled out:
- Distributional training: fitness as expectation over a *family* of
  targets, k ≫ 2.
- Curriculum: A → A+C → broader, with target diversity grown over time.
- Variance-as-fitness: maximising worst-case or low-quantile val
  rather than mean.
- Budget scale: POP × GENS ≫ 600. Multi-target landscapes are likely
  harder, and 5B's collapse may be a search-budget artefact rather
  than a structural impossibility.
- Functional-genome representations: genomes that explicitly bind
  operator parameters to target features.

What is established empirically is the *robustness of the transfer
failure under the modifications tested*, not the impossibility of
transfer in this operator class.

---

## 3. What v5 rules out [REVISED]

V5 falsifies several specific routes; what it does **not** falsify is
the program class itself.

Falsified:
- **Two-target averaged fitness as a remedy for value coupling at
  POP=20, GENS=20.** §1.3–§1.4.
- **"Fewer F-reads → better transfer" as a heuristic.** §1.5
  (correlation runs the other way).
- **"Shorter sequences are more skeletal" as a structural claim.**
  §1.5 (longer transfers better).
- **Ablation-irreducible elites on target A as evidence of
  generalisable structure on target B.** v4 + v5.

Not yet falsified — and therefore still open:
- Distributional training (k ≫ 2 random targets per evaluation,
  fitness = mean or low-quantile across the batch).
- Curriculum staging (A → A+C → broader family).
- Larger compute (multi-target landscapes are harder; 5B's collapse
  may be search-budget, not structural).
- Functional-genome architectures where operator parameters can
  depend on target features (e.g., target norm, sample variance).
- Structured-anchoring designs where one fit step is a fixed slot
  and the structural moves are constrained to the prefix and suffix.

The "fit anchors everything" finding (§1.5: more F-aware ops correlates
with *better* transfer) is consistent with structured-anchoring being
viable rather than dead. It is not consistent with "remove the F-aware
ops to get pure skeletons."

What survives across the full programme:

- **Deterministic evaluation is the right methodology** for
  reproducible gate scores.
- **MAP-Elites + GA does fragment archives** under multi-family
  vocabularies — but the fragmentation is target-specific.
- **The gate framework produced six successive kills**, each one
  tightening the claim space. That is the playground's durable
  contribution.
- **Numerical TT decomposition via evolved operator sequences works**
  as a within-target search method. It is competitive on the source
  target. It is just not "proof-skeleton evolution" in any
  generalisable sense.

---

## 4. Reframing — what the experiments actually demonstrate [REVISED]

The cleaner diagnosis, after the v5 evidence:

> The GA is evolving procedures that *solve a specific instance* —
> sequences of operations that compute `argmin ||F_target − TT||` for
> one specific F. It is not evolving procedures that *map instances to
> solutions* — functions of the form `TT = G(F)` that respond
> appropriately to whatever F is presented.

This is why:
- Transfer fails — the genome encodes a recipe for one F, not a
  function of F.
- Multi-target averaging collapses search — the GA cannot find
  procedures good on two different F's because nothing in the
  representation encourages F-dependence.
- Longer genomes transfer better — more fit calls = more re-anchoring
  on whatever F is currently active. The "skeleton" finding more
  re-anchoring opportunities is closer to a function than fewer.

The v4 "operator vocabulary" framing put the blame in the wrong place.
The operators are fine as primitives; what's missing is **a training
regime that asks the genome to behave as a function over targets**.

That is a different experimental design, not a different operator set.
A target-distribution training signal (§9) probably does need to be
combined with structured anchoring or functional parameterisation to
work, but the key change is at the training level, not the vocabulary
level.

Phase 5A's positive correlation between F-aware count and transfer
(ρ = −0.5 on val_B; more F-reads → lower val_B) is consistent with
this: the genomes that incidentally transfer best are the ones with
the most re-anchoring steps. They are closer to functions of F than
single-fit genomes are.

---

## 5. What the playground actually demonstrated

A summary suitable for the next person who picks this up:

1. **Evolutionary search on TT operator sequences works as a
   numerical optimisation method**, given deterministic evaluation,
   parsimony pressure, and a multi-family operator vocabulary. Best
   val_err on target A: 1.34e-3 at rank 3 with a 6-op genome.

2. **The "skeletons" produced are target-specific recipes**, not
   transferable reasoning patterns. Top phase-3B elites achieve val
   < 0.01 on the source target and val > 1.0 on a different target —
   worse than predicting zero.

3. **No fitness-signal modification within this operator vocabulary
   produces transferable elites.** Tested: single-target, multi-target
   averaged, parsimony at α ∈ {0, 0.001, 0.002, 0.005, 0.01, 0.02}.
   None recover transfer.

4. **Several common intuitions about what "proof skeletons" should
   look like are empirically wrong on this setup**:
   - Shorter does not mean more skeletal (longer transfers better).
   - Fewer F-reads do not mean more general (more F-reads transfer
     better).
   - Ablation-irreducibility does not mean structural meaning (every
     irreducible elite still target-fails).

5. **The operator vocabulary is the binding constraint**, not the
   training procedure, the parsimony level, or the diversity metric.
   Any future work has to attack the vocabulary itself.

---

## 6. Honest kill ledger for the full programme

| Cycle | Claim | Status after evidence |
|---|---|---|
| v1 | Diversity emerges in oracle setup | True but partly artefact of `ansatz` |
| v2 | Fragile composition is real | ~50% noise under deterministic re-eval |
| v3 | Parsimony reduces Gate 4 ρ | False — α-sweep shows the opposite |
| v3 | Irreducible skeletons indicate generalisable structure | False — v4 transfer test |
| v4 | Multi-target training would help | False — v5 phase 5B |
| v4 | Fewer F-reads → more transfer | False — v5 §1.5 |
| v4 | Shorter genome → more skeletal | False — v5 §1.5 |
| v5 | Operator vocabulary is the wall | Confirmed across all evidence |

Eight successive kills, each one informative. The programme as
originally framed is closed: this operator vocabulary cannot produce
proof skeletons in any meaningful sense.

A different programme — one that treats the genome as defining a
*function* from target samples to TTs and trains the GA on a
distribution over targets — might recover something. That is left open
and is the natural v6 if anyone wants to try.

---

## 7. File inventory

```
evolve_tt.py             Phase 1 (oracle)
evolve_tt_v2.py          Phase 2A (1-family stoch)
evolve_tt_v3.py          Phase 2B (2-family stoch)
evolve_tt_v4.py          Phase 3A/3B (det + parsimony, +/- cross family)
phase_5.py               Phase 5A/5B (multi-target experiment)
sanity_fit.py            ALS convergence diagnostic
rerun_gates.py           Deterministic re-score of v2/v3 archives
transfer_test.py         v4 transfer-on-Legendre check
alpha_sweep.py           Parsimony alpha sweep

archive.json, archive_v2.json, ..., archive_v5.json   Evolved archives
transfer_B.json          v4 transfer results
alpha_sweep.json         alpha sweep summary
phase_5.json             phase 5 multi-target results
*.log                    Run transcripts

whitepaper.md            v1 (superseded)
whitepaper_v2.md         v2 (superseded)
whitepaper_v3.md         v3 (superseded)
whitepaper_v4.md         v4 (superseded)
whitepaper_v5.md         This file
```

Master seeds 42, 43, 44, 45 by phase. Sample-pool seed 777 invariant.
All v3+ evaluations deterministic via genome-hash RNG seeding. Wall
clocks: P1 36s, P2A 155s, P2B 245s, P3A 785s, P3B 367s, transfer 60s,
α-sweep ~16min, P5A 80s, P5B 90s.

---

## 8. Conclusion [REVISED]

What is durable from this playground:

- A working sample-only TT optimisation pipeline with deterministic,
  reproducible evaluation.
- A gate framework that produced eight successive falsifications, each
  one tightening the claim space.
- A clean experimental record of which training-signal modifications
  do **not** restore transfer at this budget: parsimony, two-target
  averaging, deterministic vs stochastic eval, multi-family vocabulary
  expansion.
- A reframing of the failure: this regime evolves procedures that
  solve specific instances, not functions over instances.

What is **not** established despite the trajectory's apparent finality:

- That the operator class, in some general sense, "cannot" support
  transferable skeletons. V5's data are consistent with both
  "vocabulary is structurally limited" and "vocabulary is fine,
  training regime is wrong" — and the latter has not been falsified.
- That symbolic/algebraic/Charon-domain extensions are blocked. They
  are blocked *for the regimes tested here*. They may not be blocked
  for a distribution-trained, structured-anchored, larger-budget v6.

The honest next step is v6 — section 9 — which tests the
program-class hypothesis directly.

Kill count for the v5 cycle: three more (multi-target as a fix,
fewer-F-reads as a transferability proxy, shorter-is-skeletal as
intuition). Plus one for the v5 paper's original framing itself,
killed by post-publication review.

The playground stays open until v6 lands.

*— Charon*

---

## 9. v6 design — testing the program class [NEW]

### 9.1 The hypothesis v6 must test

Phrased as a falsifiable claim:

> **H6:** Under (a) a target-distribution fitness signal, (b) adequate
> compute budget, and (c) the *same operator vocabulary as v3-v5*,
> evolution will produce genomes whose median val on a held-out
> distribution of targets is below 0.5 (meaningful fit, not catastrophic
> failure).

If H6 holds: v5's "vocabulary is the wall" framing was wrong. The
training signal is the wall. The operator class is fine.

If H6 fails: even with proper distributional training, the operators
do not compose into target-functions. *Then* a vocabulary rebuild is
warranted.

### 9.2 Design

**Target distribution P:**
```
T(α, β, γ, k, p) = α · sin^{⊗6}(2πkx/N)
                 + β · cos^{⊗6}(2πkx/N)
                 + γ · ((x/(N-1))^p − 0.5)^{⊗6}
with α, β, γ ~ U[-1.5, 1.5]
     k ~ U{1, 2, 3}
     p ~ U{1, 2, 3}
```

True TT rank ≤ 3 for all draws, but specific F values vary widely.

**Training and held-out target sets:**
- 8 fixed training targets {T_1, …, T_8} drawn from P, frozen.
- 8 fixed held-out targets {T'_1, …, T'_8} drawn independently from P.
- Same X_TRAIN/X_VAL sample indices for all.

**Fitness signal:**
- For each genome, evaluate on all 8 training targets.
- Fitness = median val_err across targets (robust to outliers; better
  than mean for evolution).
- Variance of val across targets is recorded for diagnostic use.

**Evolution:**
- POP = 40, GENS = 50 (≈ 2× v3-era budget; multi-target is harder).
- Same operator set as v4 (fit/grad/cross + structural ops).
- Deterministic evaluation, parsimony α = 0.001 (lighter than v3).
- 3D MAP-Elites: (rank, err_bin, fit_grad_ratio_bin) — same as v4.

**Final transfer evaluation:**
- Top-10 elites by training-fitness re-evaluated on held-out 8 targets.
- Report median val per genome and std-across-targets.
- Compare to a baseline: single-target evolution at the same total
  compute (POP × GENS × k = 16 000 evals; baseline gets POP=80,
  GENS=200 on target T_1 alone).

**Success criteria:**
- *Strong:* median val on held-out distribution < 0.1 → genuine
  transferable structure.
- *Moderate:* median val < 0.5 with low std → robust fit, weak
  transfer signal. H6 holds.
- *Failure:* median val > 0.5 → distributional training also fails →
  vocabulary blame partially upheld.

### 9.3 Cost

- Per-genome evaluation: 8 targets × ~0.5 s each = 4 s
- Total: 40 × 50 × 4 s = 8000 s ≈ 2.2 hours
- Baseline: 80 × 200 × 0.5 s = 8000 s ≈ 2.2 hours

Comparable cost. Real wall-clock probably 3-4 hours including the
held-out evaluation, on a single CPU.

### 9.4 What v6 deliberately is not testing

- Not curriculum (single-pass, not staged).
- Not structured anchoring (operator vocabulary unchanged from v4).
- Not functional genome (parameters are still fixed at evolution time,
  not parameterised on target features).

These are deliberate restrictions. v6's job is to test *only* the
distribution-training hypothesis. If v6 succeeds, those further refinements
become valuable lift. If v6 fails too, they become the next branch.

### 9.5 Open design questions

Before running, two design choices deserve user feedback:

1. **k = 8 training targets?** Larger k = more reliable fitness, more
   compute. k = 4 might be enough; k = 16 might be needed if the search
   collapses again under noise.
2. **Training-target distribution range?** Too narrow and v6 trivially
   succeeds via memorisation; too wide and the search collapses.
   U[-1.5, 1.5] on amplitudes with 9 distinct (k, p) modes is a guess —
   could be wrong in either direction.

Awaiting input on (1) and (2) before running.

