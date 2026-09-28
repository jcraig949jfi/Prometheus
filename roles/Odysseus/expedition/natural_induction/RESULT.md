# Natural induction -- adversarial program -- RESULT

Status: EXPLORATORY. Toy model, small N (50 and 60), 5 training instances per
family, 20 (A,B) transfer pairs per family. Date: 2026-09-28. Author: an
Odysseus disposable research worker.

Directive: roles/Odysseus/prompts/2026-09-28_expeditionary/
01_OPERATOR_DIRECTIVE_verbatim.md section 9.

Base: frontier/poi/spikes/S6_natural_induction. Its dynamics, yield and
evaluation are copied verbatim into ni_adv.py. Nothing in S6 was modified.

## 0. Verdict

- Transfer does NOT occur.
  - MOD family (same module partition, new inter-module signs): zero-shot
    transfer is NEGATIVE, median z = -0.54 SD, positive in only 6/20 pairs.
  - A warm start from A is WORSE than learning on B from scratch, and the gap
    grows with B experience: -0.83 SD at 100 B-resets, -1.83 SD at 300 (the
    warm start is better in only 1/20 pairs at 300).
  - SK family: transfer is null (median z = +0.03, 10/20 positive).
  - The only positive transfer is to perturbed copies of A (P10: +0.73). Plain
    Hebbian storage of A's minima does the same there (+0.66 to +0.72).
- On A, the endpoint is matched exactly by storing one good minimum
  (BESTMEM or SAMEM, rho = 1.0).
- The only structure-level part of the learned couplings is inert. The
  intra-module block of WL has z = 0.00 on both A and B. All of the effect
  lives in the instance-specific inter-module part.
- Surviving interpretation: attractor reshaping / associative memory of
  visited minima, with a closed-loop, rich-get-richer selection among them
  (path-dependent in which minimum is captured). This is not a reusable
  inductive bias.
- KILL TEST (T4, preregistered): FAILED in both families.
  - MOD headline: K1 fails (z median -0.54, "negative"). K2 fails (median of
    NI minus best memory model = 0.00).
  - The thread "learning rule nobody installed" is RETIRED in favour of
    "attractor reshaping / memory of visited minima".
  - This applies to this toy under this protocol; section 7 lists what
    could reopen it.

## 1. Prior work

### 1a. Repository search

Search method:
- Pattern: git grep -i over *.md, *.py and *.txt for "natural induction",
  "hopfield", "hebbian", "hysteresis", "annealing", "stress-yield",
  "yielding" and "yield rate".
- Scope: all 88 refs, de-duplicated to 79 distinct trees; 3467 distinct
  paths matched.
- Most hits are unrelated. 2865 of them are agents/hephaestus, where
  "annealing" is used in the numerical sense.

Relevant hits:
- roles/Odysseus/frontier/poi/{raw/E5, NEWLENS, BACKLOG, REPORT, TERRITORIES,
  EXTERNAL} and spikes/S6_natural_induction. These are the origin of this
  thread.
- techne/research/evolution-as-learning/, on ref
  odysseus/th006-verification-pack and others, last touched 2026-09-04.
  - This is Techne's study of the Watson lineage (sources include
    watson2014_devmem and watson2016_howlearn).
  - MEMORY_VS_LOCKIN.md lists these as DERIVED, unmeasured failure modes of
    Hebbian outer-product memory:
    - "Orthogonal inaccessibility"
    - "Rigidity under environment switch -- a map tuned to regularity R1
      must unlearn R1 before it can acquire R2"
    - "Historical over-representation"
  - It also quotes that source's statement: "generalisation is
    (necessarily) equivalent to a 'failure' to restrict phenotypes to a
    set of training patterns".
  - Techne's E1 experiment ended as an "INSTRUMENT FAILURE, NOT A NULL"
    (commit 468a1f9ba).
  - This expedition MEASURES Techne's failure modes 4 and 5 in the NI toy:
    T1a negative transfer, and T1b warm start worse than scratch.
- ergon/kouvaris2017/: Ergon's reproduction and causal map of Kouvaris et
  al. 2017. There, generalisation to unseen targets needs extra pressures
  (environmental noise, or an L1/L2 connection cost). Plain accumulation
  over-fits.
- No seat has run a transfer test, an endpoint-matched history test or a
  kill test on natural induction before this one.

### 1b. External sources (verified by web fetch/search 2026-09-28 unless noted)

- Watson, Buckley, Mills 2011, "Optimization in 'self-modeling' complex
  adaptive systems", Complexity 16(5):17-26 (doi 10.1002/cplx.20346).
  - Bibliographic record verified.
  - Protocol as restated in "Self-Optimization in Continuous-Time Recurrent
    Neural Networks", Frontiers in Robotics and AI 2018,
    doi 10.3389/frobt.2018.00096 (fetched; authors not recorded here):
    - Hopfield network, weights in {-1,+1};
    - Hebbian w_ij += delta*s_i*s_j;
    - repeated random resets;
    - small delta is required so "poor local optima are not reinforced";
    - the method works "much better on modular or structured problems".
  - That restatement mentions no transfer to other problem instances.
  - The full paper text was not accessible (paywall/403).
- Watson, Mills, Buckley 2011, "Global adaptation in networks of selfish
  components: emergent associative memory at the system scale", Artificial
  Life 17(3):147-166.
  - Bibliographic record verified.
  - Claim, from the search summary: the network "generalises over
    previously visited attractors to increase the basin of attraction of
    superior attractors before they are visited".
  - This is a WITHIN-INSTANCE generalisation claim. It is not transfer
    across instances.
- Levin, Millidge, Tschantz, Watson 2024, "Natural Induction: Spontaneous
  Adaptive Organisation without Natural Selection", Entropy 26(9):765
  (doi 10.3390/e26090765; bioRxiv 2024.02.28.582499).
  - Verified from the search abstract: learning "insomuch as it can store,
    recall, and generalise past configurations".
  - The MDPI, Soton and bioRxiv full texts returned 403 or 429, so it is NOT
    verified whether it contains a cross-instance transfer test.
- Weber, Guckelsberger, Froese 2025, "Untapped potential in
  self-optimization of Hopfield networks: the creativity of unsupervised
  learning", Artificial Life (arXiv 2501.04007; html fetched). Their setup is
  N=100 with 1000 resets.
  - They report four learning-rate regimes: too low, no convergence; too
    high, "no trace of the constraints"; intermediate "typical", within the
    no-learning distribution; intermediate "optimal", below it.
  - At the optimal alpha = 4e-7: "probability that the learned energy is
    lower than 99.9% of the non-learning energies is about 65.4%", against
    15.5% without learning.
  - No simulated-annealing comparison. No transfer test. No explicit
    critique of Watson.
  - Consistent with S6: a narrow rate window.
- Kouvaris, Clune, Kounios, Brede, Watson 2017, PLoS Comput Biol
  13(4):e1005358 (fetched). This is the Watson group's generalisation result
  (evolution of development, not NI).
  - Without noise or a connection cost, "organisms tended to accurately
    memorise the idiosyncrasies of their past environments, at the cost of
    losing their ability to retain appropriate flexibility for the future".
  - Noise and parsimony pressure were needed for generalisation to unseen
    targets from the same class.
  - This predicts exactly the failure measured here, because NI as run has
    no decay and no cost.
- Not found: any published cross-instance transfer test of
  self-optimising or NI Hopfield networks, or any published adversarial
  critique of NI. Absence is NOT verified; full texts were partly
  inaccessible.

## 2. What was run

- PREREG.md was frozen before the main run; its SHA-256 is in
  prereg_freeze.sha256, together with ni_adv.py.
- Code:
  - ni_adv.py: the model and all runs.
  - analyze.py: implements the PREREG rules. It was written after the freeze
    but before any main-run output was inspected; it was not changed after.
  - posthoc_scale.py: POST-HOC.
- Families:
  - MOD: N=60, 12x5 modules, delta = 3e-4.
  - SK: N=50, delta = 1e-4.
- Seeds and pairs: training instances A = 11..15 per family; 4 same-family
  B per A.
- Other targets:
  - MOD: Xperm (a different partition) and Xsk60.
  - SK: P10 and P30 (A with 10% or 30% of coupling signs flipped).
- Systems:
  - NI;
  - NI2 (a different reset history);
  - NIslow (delta/3, 3x resets);
  - H (sign-blind fatigue: bonds between co-flipping units soften);
  - MEM (open-loop Hebbian storage of 1000 plain-relaxation minima);
  - SAMEM (storage of the simulated-annealing endpoint);
  - BESTMEM (storage of the best-known minimum);
  - NIblock and NIinter (the intra-module and inter-module parts of NI's WL).
  - Memory-model scales come from a 5-point grid, chosen on A only.
- Metric: z = (M_noyield - M_X) / SD_noyield on the target. M is the mean E0
  over 100 paired starts after polishing on the target's own W0.
- Wall time: main 2076 s (4 workers, shared machine at load ~27-35), plus
  post-hoc 102 s.
- Determinism: posthoc_scale.py re-trained the NI couplings. ||WL||_F was
  identical to the main run to 3 decimals on all 5 A.

## 3. Results

Per-A lists are for A = 11, 12, 13, 14, 15.

### T1 TRANSFER

T1a zero-shot on same-family B. Values are median z over 20 pairs, with the
min..max range and the number of positive pairs.

| System | MOD | MOD label | SK | SK label |
|---|---|---|---|---|
| NI | -0.54 [-3.18..+1.81], 6/20 | NEGATIVE | +0.03 [-0.54..+0.57], 10/20 | none |
| NI2 | -1.06, 7/20 | none | +0.08, 13/20 | - |
| NIslow | -1.00, 3/20 | negative | +0.10, 12/20 | - |
| MEM (scale chosen on A) | -1.11, 1/20 | negative | +0.10 | - |
| SAMEM | -1.20, 4/20 | negative | +0.07 | - |
| BESTMEM | -1.14, 3/20 | negative | +0.06 | - |
| H | 0.00 | - | +0.02 | - |
| NIblock (intra-module part only) | 0.00 [-0.03..0.00] | - | - | - |
| NIinter (inter part only) | -0.54 (identical to NI) | - | - | - |

- MOD fraction of B starts reaching B's exact ground state: noyield 0.015,
  NI 0.000, BESTMEM 0.000.
- Reading: every system that stores A's minima pushes B toward A's
  module-sign pattern, which is a random configuration for B.

T1b: limited B experience. The statistic is (M_scratch - M_warm) / SD0,
with the same B stream and the same eval starts. Negative means the warm
start is worse.

MOD:

| B resets | Warm minus scratch | Warm better in | Scratch z | Warm z |
|---|---|---|---|---|
| 100 | -0.83 [-3.24..+1.43] | 6/20 | +0.21 | -0.54 |
| 300 | -1.83 [-4.22..+0.11] | 1/20 | +1.17 | -0.54 |

- The warm z does not move from 0 to 300 B-resets: it is frozen at A's
  imprint, because WL_A (about 3 per pair) dwarfs B's inter couplings of
  0.05.
- Scratch at 1000 B-resets: z = +1.62.

SK:

| B resets | Warm minus scratch | Warm better in | Scratch z | Warm z |
|---|---|---|---|---|
| 100 | +0.05 | 10/20 | - | - |
| 300 | -0.69 | 1/20 | +0.74 | 0.00 |

- Scratch at 1000 B-resets: z = +1.49.

In both families, prior experience on A retards learning on B. This is
Techne's derived "rigidity under environment switch", now measured.

T1c: other targets (5 pairs each; median z).

| Target | NI | Memory models | Other |
|---|---|---|---|
| MOD Xperm | -0.10 (none) | MEM -0.43, SAMEM +0.24, BESTMEM -0.28 | NI2 +0.68 (4/5, "positive" by rule; judged noise, since its range is -3.21..+0.85) |
| MOD Xsk60 | -0.16 (none) | all within +/-0.2 | - |
| SK P10 | +0.73, 5/5 (positive) | MEM +0.66 (5/5), SAMEM +0.72, BESTMEM +0.72 | - |
| SK P30 | +0.40, 4/5 (none) | MEM +0.31, SAMEM +0.48, BESTMEM +0.48 | - |

Transfer appears only where B shares A's minima, and plain storage of A's
minima matches it.

POST-HOC (not preregistered; posthoc_scale.py). Is the MOD failure only a
magnitude artefact? c*WL_A was applied to B for c from 0.003 to 1:

| c | Median z on B | Median z on A |
|---|---|---|
| 0.003 | -0.03 | +0.02 |
| 0.01 | -0.18 (0/20 positive) | +0.08 |
| 0.03 | -0.35 | +1.01 |
| 0.1 | -0.52 | +2.17 |
| 0.3 | -0.54 | +2.20 |
| 1 | -0.54 | +2.20 |

No scale gives positive transfer. At every scale where WL helps A, it
hurts B.

### T2 IDENTICAL ENDPOINT, DIFFERENT HISTORY

Pairs were endpoint-matched on A at |dM_A| <= 0.25 SD. The history effect on
B is h = (M_NI(B) - M_X(B)) / SD0.

MOD:

| Pair | Matched A | Median abs(h) | Median signed h | History matters? |
|---|---|---|---|---|
| NI vs BESTMEM | 5/5 | 0.28 | 0.00 | no |
| NI vs NIslow | 3/5 | 0.28 | 0.00 | no |
| NI vs SAMEM | 3/5 | 0.53 | 0.00 | "yes" |
| NI vs NI2 | 1/5 | 0.00 | - | no |
| NI vs MEM | 0/5 | - | - | not matchable |

- NI vs BESTMEM is the key pair. One-shot storage of the single best minimum
  equals 1000 resets of accumulated experience, both on A and on B.
- NI vs SAMEM: the size of the effect is real, but its sign is 0. Which
  specific A-minimum was stored decides how badly B is hurt; the way it
  was acquired does not.
- NI vs NI2: NI2 ended in worse minima on 4/5 A (for example -147.5 against
  -152.5), so the endpoint was not matched.
- NI vs MEM: open-loop frequency memory never reaches NI's A endpoint.

SK:
- NI vs NI2: 4/5 matched, abs(h) 0.07.
- NI vs NIslow: 4/5 matched, abs(h) 0.08.
- NI vs SAMEM: 5/5 matched, abs(h) 0.09.
- NI vs BESTMEM: 4/5 matched, abs(h) 0.05.
- NI vs MEM: 3/5 matched, abs(h) 0.27.
- No history effect anywhere.

Path dependence of WHICH minimum is captured (modal-attractor overlap abs(q)
with NI):

| Family | NI2 | NIslow |
|---|---|---|
| MOD | 0.33, 0.50, 0.83, 0.50, 1.00 | 0.83, 0.83, 0.67, 0.50, 1.00 |
| SK | 1, 1, 0.72, 1, 0.12 | same as NI2 |

In MOD, different histories capture different minima, of different
quality.

Conclusion for T2: once the endpoint is matched, history has no
systematic effect on new instances. What carries over is the identity of
the stored minimum, not the process that found it.

### T3 ALTERNATIVES

Each alternative is named with its discriminating statistic and the
observed value (median over A).

- Annealing (on states, original energy).
  - Statistic: fresh-start gain after the process. It is 0 for SA by
    construction; NI's frozen-WL gain is z_NI(A) = +2.20 in MOD and +1.23
    in SK.
  - So NI is NOT merely annealing: it changes the future dynamics.
  - But an SA endpoint stored once (SAMEM) gives rho = 1.00 (MOD) and 1.20
    (SK).
  - SA's single-run endpoint equals or beats NI's eval minimum on 2/5
    (MOD) and 5/5 (SK) A.
- Hysteresis / material memory without Hebbian direction (H).
  - Best eps: 1e-3 in MOD, 1e-1 in SK.
  - z_H(A) = 0.00 in MOD and +0.19 in SK; rho = 0.00 and 0.15.
  - At other rates in MOD it is harmful: z = -0.24 at eps=1e-2 and -1.2 at
    eps=1e-1.
  - H is history-dependent (relative ||W_h1 - W_h2||):
    - MOD: 0.011-0.013 (all above 0.01);
    - SK: 0.004-0.013 (above 0.01 on only 1/5).
  - Generic history-dependence without the sign-aligned (Hebbian) direction
    does not produce the effect. This is consistent with S6's anti control.
- Plain parameter adaptation toward visited minima, open loop (MEM).
  - MOD: rho = 0.58, so the closed loop matters. Frequency-weighted storage
    of 1000 random minima is not enough in MOD, because the modal-frac is
    only 0.11-0.28.
  - SK: rho = 0.97, so open-loop memory suffices.
- Attractor reshaping toward one good minimum (BESTMEM).
  - rho = 1.00 (MOD) and 1.20 (SK).
  - Endpoint-identical to NI on A, and never worse than NI on A.
  - Within 0.05 SD of NI on the one target where NI transfers (SK P10).
- Path dependence.
  - Present in which minimum is captured (MOD overlaps 0.33-1.0).
  - Not in the transferable content (T2).

Which alternative predicts all the observed signatures:
- The signatures are:
  - the gain on A;
  - the sign-dependence;
  - equivalence with one-shot storage of a good minimum;
  - no gain from the structural block;
  - negative transfer where minima differ;
  - memory-level transfer where minima are shared;
  - warm start worse than scratch.
- "Closed-loop attractor reshaping" predicts all of them: an associative
  memory of visited minima, whose feedback concentrates on one
  (large-basin, low-energy) minimum.
- Pure annealing fails the fresh-start statistic.
- Sign-blind hysteresis fails the gain statistic.
- Open-loop memory is partial in MOD (rho 0.58).
- "Learning a reusable inductive bias" fails T1.

### T4 KILL TEST (preregistered)

MOD (headline):
- K1 (zero-shot NI transfer positive): FAIL. Median -0.54, 6/20 positive,
  labelled NEGATIVE.
- K2 (NI beats the best memory model by >= 0.25 SD): FAIL. The median
  difference is 0.00, and NI is better on only 4/20 pairs.

SK:
- K1: FAIL (+0.03, 10/20).
- K2: FAIL (-0.07, 6/20).

VERDICT: RETIRED. "Learning rule nobody installed" gives way to "attractor
reshaping / memory of visited minima".

## 4. Which interpretation survives

A closed-loop associative memory of the system's own visited minima: slow
Hebbian yield plus resets make a rich-get-richer selection among minima.
Because low-energy minima tend to have large basins (Watson's stated
premise), this concentrates the system onto one good minimum of THIS
instance. It is:
- optimisation by self-imprinting;
- genuinely history-dependent in which minimum wins;
- not annealing, because the future dynamics change;
- not sign-blind material memory, because the direction matters.

It does not extract anything reusable. The only structure-level component
it accumulates, the intra-module block, has zero functional effect, and
the instance-specific imprint actively harms new instances and slows
re-learning. By the operator's criterion (transfer, rather than falling
into the same attractor), the evidence is for "memory", not "induction".

The word "learning" is defensible only in the weak associative-memory
sense, which is the sense Levin et al. 2024 define: "store, recall, and
generalise past configurations". The "generalise" part is not supported
across instances here.

## 5. What a Prometheus substrate would need (to test further or host this)

1. Everything S6 listed:
   - a fast dissipative state;
   - a slow plastic layer separate from frozen constraints;
   - a local yield hook with a sweepable rate;
   - a reset scheduler;
   - freeze/eval/polish hooks;
   - control switches.
2. An INSTANCE FAMILY GENERATOR with controllable shared structure (fixed
   decomposition, fresh particulars), plus graded relatedness
   (sign-flip fraction p). Transfer is only meaningful against such a
   family.
3. Plastic-layer TRANSPLANT and warm-start: apply WL_A to B, continue
   learning on B, and have matched-scratch baselines on the same B stream.
4. MEMORY BASELINES as configuration: store the best or annealed minimum,
   and store the open-loop visited minima, both norm-matched with a scale
   grid chosen on A. Without these, any "learning" claim is untestable.
5. Weight decay or a connection-cost term, and injected noise, as knobs.
   Kouvaris 2017 and Techne's MEMORY_VS_LOCKIN both say that generalisation,
   if it exists at all, lives there. NI as run has neither.
6. Decomposition of the learned couplings (for example block vs off-block)
   with per-component ablation.

## 6. Deviations and limits

- MOD delta = 3e-4 is S6's post-hoc rate, confirmed in S6 on fresh seeds.
  It was not re-tuned here.
- The T4 verdict could depend on the rate window. Weber et al. find an
  "optimal" regime that is much slower relative to N.
- Transfer family design: MOD-B keeps the partition but redraws all
  inter-module signs, so A's minima carry no information about B's minima.
  - That is deliberate (it isolates structure from memory).
  - A family with partially shared inter-module signs would test graded
    relatedness in MOD; only SK P10/P30 did that here.
- In MOD the intra-module structure is already fully satisfied by
  single-flip relaxation, so NIblock could not help even in principle.
  - A family whose shared structure is NOT already enforced by W0 (for
    example weak intra-module couplings that the learner must discover)
    would be a fairer test of "learning the decomposition".
  - This is the main open door; see section 7.
- The T2 match criterion was met by few pairs in MOD for NI2 (1/5) and MEM
  (0/5). The T2 MOD conclusions rest mainly on BESTMEM (5/5) and on
  NIslow/SAMEM (3/5 each).
- Sample sizes are small. The z values on MOD are lumpy because evaluations
  collapse onto one attractor.
- No weight decay; zero temperature only.
- The H model is one choice of sign-blind material memory (co-flip
  softening); other hysteretic laws were not tried.
- Full texts of Watson 2011 (Complexity) and Levin et al. 2024 (Entropy)
  were not accessible. The protocol claims about them rest on the
  secondary restatement cited above.
- Side effect outside the output directory: one WebFetch of an arXiv PDF
  was cached by the tool harness under ~/.claude/projects/.../tool-results/.
  This was not a deliberate write, and it contains no memory or config.
- analyze.py prints only; a display truncation in the ad-hoc console
  summary did not affect results.json.

## 7. What would reopen the thread

The thread would reopen only if a preregistered test on a family of this
kind passes K1 and K2. The family needs a shared decomposition that W0
under-specifies (for example intra-module couplings of 0.1-0.3, so
modules are NOT automatically coherent), run with decay or noise:
- K1: NI trained on A gives a positive zero-shot or warm-start gain on B,
  where B has a fresh inter-module pattern.
- K2: NI beats BESTMEM, SAMEM and MEM on that transfer.

## 8. Files (roles/Odysseus/expedition/natural_induction/)

- PREREG.md and prereg_freeze.sha256: the frozen protocol and code hash.
- ni_adv.py: the model and runs (main); smoke = the timing run on seed 999.
- analyze.py: the preregistered decision rules; writes results.json.
- results_raw.json: per-start energies for every system x target,
  B-experience runs and training metadata.
- results.json: all T1-T4 statistics per family.
- posthoc_scale.py and posthoc_scale.json: the POST-HOC WL-scale transfer
  sweep.
- main.log: stage timings.
