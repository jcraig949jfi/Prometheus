# O. RECONSTRUCTION VALUE AND SFE CALIBRATION PROPOSAL

Directive §18: is this specimen worth reproducing **independently of HC-T01**? Rank the candidate
reasons by expected information gain. Directive §19: record, without running, the composition that
the Toussaint/Kouvaris difference identifies.

**Nothing here is authorised and nothing here is run.** This is a costed proposal.

---

## 1. Why this specimen is a good reconstruction target

It has the property the EvCA and Toussaint specimens lack: **a known, non-trivial, positive result
with a predicted numerical value derived from problem structure before the run.** Under L1 the
entropy of the induced phenotype distribution should converge to exactly **4 bits** — the number of
independent modules — and over-fitting should read **below 4**, and the untrained map **16**. That is
a validation target with an attainable range computable in advance, which is what Prometheus's own
gate doctrine requires and what this literature almost never supplies.

It is also cheap. `N = 16`, `T = 10`, a single genotype, and a detector costing 5000 developmental
simulations. The whole paper is CPU-minutes on modern hardware.

## 2. The four candidate reasons, ranked by expected information gain

**Rank 1 — DETECTOR CALIBRATION: can Prometheus detect the known change without being told the
treatment?**
The strongest reason, because it tests our instrument against a case where the ground truth is known
and the answer is quantitative. Protocol: reconstruct the four arms, hand a Prometheus-side detector
the trajectories **blind** to which arm is which, and ask it to (a) rank arms by generalisation and
(b) locate the over-fitting change point in the control arm. The historical answer exists: L1 reaches
zero test error, L2 and noise plateau, control over-fits, and the change point is marked in Fig 3A.
*Information gain: high. Failure is informative — a detector that cannot recover a known, strong,
published effect is not ready to be pointed at an unknown one. This is an independent failure mode
for our instrument in the sense the programme requires, because the ground truth was set by someone
else.*

**Rank 2 — THE COMPOSITION TEST, on this specimen, at near-zero marginal cost.**
The reconstruction gets the A-local detector **for free** by keeping what the original discarded: log
the rejected mutant's phenotype at every SSWM step (`N_FAILURE_DATA_RECOVERY.md` §4.1). That yields a
one-step offspring sample taken with the real operator at the real current state, at every
generation, in all four arms, with **no change to the physics**. Then ask the question that remained
unanswered in April 2017: *does the local accessibility distribution move before, with, or after the
global expressibility distribution?* This is the cheapest possible instantiation of HC-T01's
scientific question, on a substrate where the global comparator already exists and is published.
*Information gain: high, and it is close to a free rider on rank 1.*

**Rank 3 — CONVERT PATTERN 2 INTO PATTERN 1 within a single arm.**
Freeze `B` at several points **along one run** — before the over-fitting change point, at it, and
after — and run the paper's own Fig 5 acquisition assay at each. No new instrument; the assay already
exists. This directly supplies the within-run detector-to-acquisition link the paper lacks, on the
paper's own design. *Information gain: high for the temporality question specifically
(`H_TEMPORALITY_ANALYSIS.md` §3). It is the experiment the authors were one sweep away from running.*

**Rank 4 — POSITIVE-CONTROL VALUE for the evolution of evolvability.**
Real but the weakest of the four, because it duplicates rank 1 without the blinding that makes rank 1
informative. Keep it only as a by-product.

**Rank 5 (not recommended) — TRANSFER TEST under held-out worlds.**
Attractive but premature: it needs an SFE world mapping that does not exist, and it would be testing
a Prometheus construct rather than recovering a historical one. Directive §22 forbids inventing
metrics on this pass, and this is where that temptation lives.

## 3. What must be settled before any code is written

Seven ambiguities, enumerated in `C_HISTORICAL_PHYSICS_SPEC.md` §10, three of them
code-versus-paper contradictions. In order of consequence:

1. **Is `G` mutated during the main runs at all?** Published Methods say a point mutation on `G`;
   the committed `GRN.m` sets `G = S'` at each environmental switch with `mG = mutate_gene(G)`
   commented out. These are different experiments. **This must be resolved first**, because rank 2
   depends entirely on there being a stream of rejected `G` mutants to log — and under the committed
   configuration there is none.
2. `B`-mutation probability: 1, 1/2 or 1/15 (three sources, three answers).
3. `alpha`: 0.3 (code) or 0.5 (S1). `T`: 15 (code) or 10 (S1).
4. `G` domain: continuous or `{−1,1}`.
5. Phenotype category count: `2^12` (Fig 2 caption) or `2^16` (entropy discussion, and N=16).
6. Replicate count: unstated everywhere; **must be chosen by us and reported**, since no historical
   value can be inherited.

**Validation targets, fixed in advance**, all from the published record:
- **V1** entropy under L1 converges to **4 bits** (S1 Fig D) — primary, quantitative, with a
  structurally derived expected value.
- **V2** entropy of the untrained map is **16 bits** — primary, trivially checkable, catches
  category-count errors.
- **V3** L1 generalisation error reaches **zero**, over `ln(λ) ∈ [0.15, 0.35]`, and fails at
  `λ = 0.4` — primary.
- **V4** control arm shows test error falling then rising, with an identifiable change point — structural.
- **V5** noise arm test-error minimum ≈ **0.34** — corroborating.
- **V6** L2 optimum at `λ = 38`, insensitive over `[10, 38]`; noise optimum at `κ = 35×10⁻⁴` — corroborating.
- **V7** Fig 5 outliers: at least one class member censored under control, noise and L2, and reachable
  under L1 — structural, and the one that ties the detector to acquisition.

**Scoring rule, fixed now:** V1, V2 and V3 are primary. Each must be matched within a tolerance set
from the reconstruction's own run-to-run spread, and that spread must be computed and reported
**before** the tolerance is chosen. Missing a primary target materially yields
`RECONSTRUCTION_FAILS` and nothing about the historical record follows from our runs.

## 4. Estimated cost

| Stage | Work | Order of magnitude |
|---|---|---|
| Physics rebuild | GRN, fitness, SSWM loop, class construction | a day of implementation |
| Detector rebuild | Sobol + scramble, develop, bin, χ², entropy | hours |
| Four arms × 30 replicates × 150 epochs | 9×10⁶ generations per run | CPU-hours, trivially parallel |
| Detector at every epoch | 5000 developments × 150 epochs × 4 arms × 30 runs | CPU-hours |
| Rank 2 rejection logging | one write per generation | storage, not compute |
| Rank 3 checkpoint acquisition assay | 1000 runs × 2500 gens × k checkpoints × 4 arms | the dominant cost, still CPU-days at most |

**No GPU, no model in the loop, no external service.** This is squarely inside the compute envelope
that has repeatedly been the programme's binding constraint elsewhere.

## 5. Directive §19 — the composition candidate, recorded and NOT run

The Toussaint/Kouvaris difference identifies an untested composition, and stating it is the point of
§19.

> **Toussaint supplies:** a variation operator that can be switched on and off, and a detector that
> samples what that operator actually produces from the current state.
> **Kouvaris supplies:** a selection regime that provably shapes the machinery producing future
> variation, plus a constructed class with held-out environments that makes "generalisation"
> measurable rather than asserted.
>
> **The composition:** *variation machinery that changes itself under selection pressures that favour
> generalisable future variation* — i.e. put an operator whose own parameters are heritable inside a
> modularly-varying environment with a parsimony pressure, and measure the one-step offspring
> distribution longitudinally in every arm while it happens.

Two warnings recorded with it, both from this pass:

- **The tautology hazard compounds.** If the operator's parameters are heritable *and* the detector is
  the distribution that operator induces, then the detector moves with the genotype by construction.
  The mechanical-effect null that Herakles preregistered for a fixed `β` becomes harder, not easier,
  when `β` itself evolves. This composition needs that null designed *first*.
- **The coupling hazard persists.** Both readouts would still be functionals of the same evolved
  object unless the acquisition assay is run on a genuinely held-out environment set — which is the
  Kouvaris half of the composition, and is the reason the two halves need each other.

**Not authorised, not costed beyond this, not to be started.** It is recorded as a part in
`M_CANDIDATE_COMPUTATIONAL_PARTS.jsonl` and nothing more.

## 6. Recommendation

**Do rank 1 and rank 2 together or not at all.** They share a reconstruction, the second is nearly
free given the first, and separately neither is worth the CPU: rank 1 alone only confirms someone
else's published result, and rank 2 alone has no calibrated instrument behind it.

**Do not start until ambiguity 1 is resolved** — whether `G` is mutated during the main runs — because
rank 2 does not exist if it is not. That resolution requires reading `GRN.m` against the published
Methods and choosing, with the choice recorded before any run.
