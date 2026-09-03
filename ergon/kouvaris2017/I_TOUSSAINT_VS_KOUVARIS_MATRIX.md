# I. TOUSSAINT vs KOUVARIS — direct comparison

Toussaint column from Herakles's recovered specimen (`herakles/specimens/spec-toussaint-exploration/`,
principally `SRC-PHD-2003` §§1.5.3–1.5.4, `HC_T01_FROZEN_CONFIG.json`,
`HISTORICAL_VALIDATION_TARGETS.md`). Kouvaris column from this pass's primary sources.

---

## 1. The matrix (directive §15 rows)

| Row | Toussaint 2003 | Kouvaris 2017 |
|---|---|---|
| **Year** | 2003 (PhD thesis, Bochum) | 2017 (PLOS Comput Biol; preprint 2015) |
| **Genotype representation** | variable-length symbol string over an 8-letter alphabet, with promoters; genome length evolves (25 → 11) | fixed pair `[G, B]`: 16 real embryonic values + a 16×16 real regulatory matrix |
| **Phenotype** | 25-symbol sequence; target `abcdeabcdeabcdeabcdeabcde`, period 5 | 16 real gene-expression levels, signed to a 16-bit pattern; targets are 8 modular patterns from a 4-module class |
| **Developmental map** | rule-rewriting, `T = 1` development step | recurrent non-linear GRN, `T = 10` steps (code says 15) |
| **Population** | μ = 30 parents, λ = 100 offspring, no crossover | **none** — a single genotype under strong-selection-weak-mutation |
| **Exploration distribution** | `Ξ_σ`, the **offspring** distribution induced by the actual variation operator on a parent | the distribution of adult phenotypes obtained by developing **uniformly random** embryonic phenotypes through a fixed `B` |
| **Local vs global detector** | **LOCAL** — one variation step from a real parent | **GLOBAL** — uniform Sobol draw over the whole `[−1,1]^16` cube; the authors call it an estimate of drift |
| **Per-individual sampling** | **YES** — 2000 sampled offspring per individual per generation | no; the probe set is independent of any individual |
| **Population-wide sampling** | **YES** — averaged over the 100-offspring population | n/a (no population); the sample is over genotype *space*, which over-covers rather than under-covers |
| **Longitudinal sampling** | **YES**, per generation, in Experiment 1 | **YES**, per epoch, in all four arms |
| **Intervention** | `β`, the rate of second-type mutations, switched **on (0.1) / off (0.0)** | four selection-side arms: switching interval `K`, target noise `κ`, L2 cost `λ = 38`, L1 cost `λ = 0.22` |
| **Intervention targets the variation operator?** | **YES** — `β` *is* an operator parameter | **NO** — never; both mutation functions are parameterless and identical in every arm |
| **Intervention targets selection?** | no | **YES** — all four arms |
| **Within-run acquisition** | fitness per generation, within runs, in both arms | **NO** — acquisition measured once, post-evolution, on frozen `B` |
| **Unseen-environment test** | **NO** — a single fixed target sequence | **YES** — 3 training targets, 8-member class, 5 never selected |
| **Ablation** | **YES**, clean on/off | arms, but no mechanism is ablated |
| **Same-probe counterfactual** | not in the historical design (HC-T01 adds `beta_probe = 0.1` as a fixed probe) | **YES by construction** — one fixed 5000-point Sobol set reused at every epoch and in every arm |
| **Run-level causal inference** | historical: no; HC-T01 preregisters paired permutation over 30 run pairs, Holm-corrected | **no** — number of evolutionary runs never stated, no uncertainty on any longitudinal figure |
| **Detector used for selection?** | **NO** — scientist-side | **NO** — scientist-side, and stated explicitly in S1 as *"a post hoc analysis, and hence not part of the actual evolutionary dynamics"* |
| **D-level** | detector experiment reaches D3; the ablation reaches D1–D2 with an acquisition outcome but **no detector inside it** | **D3 outright; D4 at arm level; not D5** |
| **Unresolved confound** | TRAP 1 — `β` parameterises the operator that *induces* `Ξ_σ`, so "arms differ on the detector" is partly true by construction; a generation-zero mechanical-effect null is mandatory | detector and acquisition are two deterministic functionals of the same frozen `B`, so their agreement is close to definitional; and no replication |

## 2. The single sentence answer to directive §15

> **What does HC-T01 measure that Kouvaris 2017 does not?**

**The distribution of phenotypes reachable in one application of the actual variation operator from
the state the lineage currently occupies, measured inside every arm of an on/off ablation of that
operator, and related to what the lineage subsequently acquires in the same run.**

Kouvaris measures a different distribution (global, operator-free), under a different kind of
intervention (selection-side), joined to acquisition at a different level (arm, endpoint). The answer
to §15 is therefore **not** "nothing material". Three material things differ, and each is the
difference between two objects that can move independently.

## 3. Where each is the better experiment

Stated symmetrically, because the directive forbids defending either.

**Toussaint / HC-T01 is better at:**
- measuring what is reachable *from here* — the detector uses the real operator on real parents;
- having a mechanism that can be switched off, which is the only way to ask what the mechanism does;
- within-run temporality, since fitness is recorded per generation in both arms.

**Kouvaris is better at:**
- **non-tautology.** No Kouvaris arm touches the operator, so the detector's movement is entirely an
  evolved response. Toussaint's `β` is the operator, so part of any arm difference is arithmetic;
- **defining what generalisation means.** A constructed class with a held-out subset beats a single
  fixed target;
- **distinguishing kinds of acquisition.** Censored outliers separate "cannot express" from "slow to
  find"; Toussaint's fitness curve does not;
- **probe discipline.** One fixed sample reused everywhere.

**Neither is good at:** run-level uncertainty on the detector. Toussaint reports none — the record
contains no uncertainty of any kind for his detector, which is why HC-T01 must measure its own noise
floor before choosing any threshold. Kouvaris reports none either. **This is a property of the
literature, not of one author**, and it is the strongest argument in this pass for reconstructing
rather than merely reading.

## 4. What HC-T01 should change as a result

Concrete, and each traceable to a row above.

1. **Adopt the fixed-probe design.** Draw the offspring-sampling randomness once and reuse it across
   arms, checkpoints and run pairs, as `findErrors.m` does for `H` and as `computeM.m` does via
   `rand_nums.mat`. HC-T01's frozen config sets `beta_probe = 0.1` and `detector_samples_S = 2000`
   but does not say the draws are shared. Sharing them removes probe noise from every contrast for
   free.
2. **Add a held-out target set.** Toussaint's single periodic target gives no way to separate
   "acquired the target" from "acquired the structure". A second target of the same period-5 family,
   never selected for, would let HC-T01 report `REACHES_PREVIOUSLY_UNREACHABLE` rather than only
   `ACQUIRES_FASTER`. This is the cheapest upgrade available and it is borrowed wholesale.
3. **Separate the two clocks in the preregistration.** Say explicitly that the detector is read on the
   generation clock and that the acquisition it should predict is read on the same clock, and fix the
   lead window `n` before the run. `H_TEMPORALITY_ANALYSIS.md` §5 explains why this matters.
4. **Report unreachability, not only fitness.** Censor and count the runs that never attain the
   target, as Kouvaris does at 2500 generations. HC-T01's `primary_acquisition_metric` is currently
   `best_fitness`, which cannot distinguish the two failure modes.
5. **Re-justify against Kounios 2016, Petak 2025 and Tiso 2024, not against Toussaint's corpus
   alone.** The missing-cell argument was built before those were screened. See
   `K_DESCENDANT_SEARCH.md`.
