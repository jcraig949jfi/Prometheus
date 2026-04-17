# Frontier Triage: Real Barriers vs Thought Experiments + Generated Tests

**Agent**: Aporia (Discovery Engine)
**Date**: 2026-04-16
**Purpose**: Ruthlessly separate genuine barriers from philosophy, then generate tests for everything real

---

## The Filter

A REAL barrier has ALL of:
1. A specific, measurable prediction that could be wrong
2. Data that exists or could exist to test it
3. A result that would change what we DO next

A THOUGHT EXPERIMENT has any of:
- No possible observation that distinguishes answers
- The question dissolves under precise formulation
- It's "interesting" but nothing rides on it

---

## The 20 Frontiers: Triaged

### REAL BARRIERS (genuinely block progress, testable)

**1. Riemann Hypothesis** — REAL
- Specific prediction: all nontrivial zeros have Re(s) = 1/2
- Testable: we have 24M L-functions with zeros
- What rides on it: prime distribution, cryptography, analytic number theory
- Barrier type: 2+4 (finite/infinite + conceptual)

**2. Langlands Program** — REAL
- Specific prediction: Artin reps ↔ automorphic forms ↔ Galois representations
- Testable: we have 798K Artin reps, 1.1M modular forms
- What rides on it: unification of number theory
- Barrier type: 3+4

**3. BSD Conjecture** — REAL
- Specific prediction: rank = analytic rank, Sha is finite, BSD formula holds
- Testable: 3.8M EC, 2.48M in bsd_joined
- What rides on it: understanding rational points on curves
- Barrier type: 2

**4. P vs NP** — REAL (but barely)
- Specific prediction: no polynomial algorithm for SAT
- Testable: indirectly (every fast algorithm found would be evidence)
- What rides on it: cryptography, optimization, everything
- Barrier type: 4+5 (may be independent of standard axioms)
- CAVEAT: The barrier is real but our tensor can't directly attack it. Useful as a calibration question.

**5. Quantum Gravity** — MIXED
- The REAL part: specific predictions from string theory / loop QG that differ from standard model (graviton scattering amplitudes, black hole entropy microstates)
- The THOUGHT EXPERIMENT part: "what is spacetime really?" — dissolves under formalization
- Testable parts: amplituhedron predicts specific scattering amplitudes; holographic entropy predicts RT formula
- Barrier type: 4

**6. Dark Energy** — REAL
- Specific prediction: DESI says Lambda varies (3.9-sigma)
- Testable: future surveys (Euclid, LSST) will confirm/deny
- What rides on it: fate of the universe, fundamental physics
- Barrier type: 4
- OUR ANGLE: the mathematical structure of quintessence potentials is virgin territory

**7. Navier-Stokes** — REAL
- Specific prediction: smooth solutions exist for all time in 3D
- Testable: constructive (find a blowup) or prove regularity
- What rides on it: turbulence modeling, engineering
- Barrier type: 3+4
- 3D Yang-Mills solved (2024) via same techniques. 4D is the frontier.

**8. Consciousness** — THOUGHT EXPERIMENT (mostly)
- IIT has mathematical formalism (phi) but no testable prediction distinguishing it from behaviorism
- "What is consciousness?" dissolves under operationalization
- The REAL part: neural correlates of consciousness ARE measurable, but that's neuroscience not philosophy
- DEMOTED from frontier list. Replace with something testable.

**9. Protein Design** — REAL
- Specific prediction: inverse folding is computationally tractable
- Testable: AlphaFold forward works; generative models for inverse are being validated
- What rides on it: drug design, synthetic biology
- Barrier type: 1+3

**10. Yang-Mills Mass Gap** — REAL
- Specific prediction: quantum Yang-Mills has a positive mass gap
- Testable: lattice simulations give numerical evidence; need rigorous proof
- What rides on it: Millennium Prize, understanding confinement
- Barrier type: 3+4

**11. Hodge Conjecture** — REAL (but remote)
- Specific prediction: every Hodge class is algebraic
- Testable: in principle, for specific varieties
- What rides on it: algebraic geometry foundations
- Barrier type: 3
- Our tensor CAN'T directly test this. But empirical derived categories (bond dimension clustering) could detect Hodge-class signatures.

**12. Turbulence** — REAL
- Specific prediction: Kolmogorov scaling exponents, energy cascade statistics
- Testable: we don't have fluid data but the MATH is testable (anomalous scaling dimensions relate to operator spectra)
- What rides on it: weather, climate, engineering
- Barrier type: 4

**13. Quantum Advantage** — REAL
- Specific prediction: specific problems have provable quantum speedup
- Testable: each claim is a theorem or construction
- What rides on it: quantum computing roadmap
- Barrier type: 1+2

**14. Origin of Life** — MIXED
- The REAL part: autocatalytic sets, self-replicating chemistry, minimal genome
- The THOUGHT EXPERIMENT part: "how did life begin on Earth?" — historical, unfalsifiable specifics
- Testable parts: can we build minimal self-replicating systems? What are the mathematical constraints?
- Barrier type: 4

**15. Black Hole Information** — REAL
- Specific prediction: information is preserved (Page curve, island formula)
- Testable: the Page curve has been derived in specific models (2019-2020)
- What rides on it: quantum gravity consistency
- Barrier type: 4

**16. Cosmological Constant** — REAL
- Specific prediction: Lambda = 10^-122 demands explanation
- Testable: any mathematical selection principle would predict the value
- What rides on it: fundamental physics
- Barrier type: 4+5
- CAVEAT: may be environmental (anthropic), in which case it's not a barrier but a parameter

**17. Neutrino Mass** — REAL
- Specific prediction: neutrinos have mass (confirmed), but the MECHANISM is unknown
- Testable: neutrinoless double beta decay experiments running now
- What rides on it: Majorana vs Dirac, seesaw mechanism
- Barrier type: 4

**18. Knot-Number Bridge** — REAL
- Specific prediction: arithmetic topology says primes ↔ knots, NF ↔ 3-manifolds
- Testable: our data has both knots and NF
- What rides on it: unifying topology and number theory
- Barrier type: 3
- This is our SILENT ISLAND. Direct Prometheus target.

**19. AI Math Reasoning** — REAL
- Specific prediction: AI can find proofs humans can't
- Testable: AlphaProof did it at IMO level
- What rides on it: the future of mathematics
- Barrier type: 1+2

**20. ADE Universality** — REAL
- Specific prediction: one classification governs ALL finite-type problems
- Testable: we have the data (Lie algebras, singularities, quivers in LMFDB)
- What rides on it: understanding WHY mathematics has this structure
- Barrier type: 4

### DEMOTED (not real barriers)

**"What's beyond the universe"** — Unfalsifiable. No observation distinguishes answers. Thought experiment.

**"Why is there something rather than nothing"** — Dissolves under formalization. Not a mathematical question.

**"Is mathematics discovered or invented"** — Philosophy, not barrier. Doesn't change what we compute.

**"Many worlds interpretation"** — No testable difference from Copenhagen for any experiment we can run.

**Consciousness (as a "hard problem")** — Replaced by measurable neural correlates. The philosophical residue is unfalsifiable.

**"Why these physical constants"** — PARTIALLY demoted. If anthropic, it's not a barrier. If there's a mathematical selection principle, it's frontier #16. The question as posed is ambiguous.

---

## GENERATED TESTS (Batch 2)

### Cross-Domain Mathematics (new territory)

**TEST X-1: Ramanujan Graph Detection in LMFDB**
Ramanujan graphs achieve optimal spectral gap. Cayley graphs of groups have spectra determined by representation theory. Test: for each group in prometheus_sci.algebra.groups, compute the Cayley graph spectral gap. Which groups produce Ramanujan graphs?
- Falsification: no group in our data produces a Ramanujan graph (unlikely but informative)
- Data: prometheus_sci.algebra.groups (545K), artin_reps (798K for representation theory)
- Agent: Ergon (computation) + Charon (battery validation)

**TEST X-2: Modular Form Weight Distribution vs Random Matrix Prediction**
The Sato-Tate conjecture (proved 2011) says EC Frobenius angles are semicircle-distributed. Test: for weight-k modular forms in mf_newforms, compute the distribution of Hecke eigenvalues a_p. Does it match the Sato-Tate prediction for each weight? Which weights deviate?
- Falsification: all weights match (no deviation to investigate)
- Data: mf_newforms (1.1M), specifically Hecke eigenvalue data
- Agent: Harmonia (spectral analysis)

**TEST X-3: Class Number One Problem — Verify Baker-Heegner-Stark**
There are exactly 9 imaginary quadratic fields with class number 1 (proved). Blind trial: without telling the instrument the answer, query nf_fields for imaginary quadratic (degree=2, disc < 0) with class_number=1. Does it recover exactly 9?
- Falsification: more or fewer than 9 (data error, not math error)
- Data: nf_fields (22M), filter degree=2, disc_sign=-1, class_number=1
- Agent: Aporia (blind trial) + Charon (verification)

**TEST X-4: Elliptic Curve Conductor Growth Rate**
Goldfeld's conjecture says average rank → 1/2. Our abc test showed LMFDB selection bias at high conductor. Test: for the COMPLETE census range (conductor < 500K), compute the exact average rank as a function of conductor. Does it approach 0.5 from above?
- Falsification: average rank increases or oscillates (tension with Goldfeld)
- Data: ec_curvedata (3.06M curves with conductor < 500K)
- Agent: Ergon (computation)

**TEST X-5: Genus-2 Jacobian Decomposition Census**
How many genus-2 curves have decomposable Jacobians (isogenous to E1 x E2)? This fraction is predicted by random matrix theory. Test: query g2c_curves for isogeny decomposition data. Compute the fraction. Compare to RMT prediction.
- Falsification: fraction deviates significantly from RMT
- Data: g2c_curves (66K)
- Agent: Harmonia

**TEST X-6: Number Field Discriminant Bounds — Odlyzko Bounds**
Odlyzko proved lower bounds on discriminants of NF by degree. With 22M NF, we can compute the actual discriminant distribution and compare to the Odlyzko bound. Test: for each degree d=2..10, what fraction of fields approach the Odlyzko bound? Are there fields BELOW the bound (impossible — would be a data error)?
- Falsification: any field below Odlyzko bound (data integrity check)
- Data: nf_fields (22M)
- Agent: Charon (battery/validation)

**TEST X-7: Artin Conductor-Dimension Scaling**
Is there a scaling law between Artin rep dimension and conductor? In representation theory, higher-dimensional reps of a given group have conductors growing in a predictable way. Test: for each Galois group type, plot conductor vs dimension. Fit power law.
- Falsification: no consistent scaling (dimensions are independent of conductor)
- Data: artin_reps (798K with Dim, Conductor, GaloisLabel)
- Agent: Ergon (computation) + Kairos (adversarial review of scaling claim)

### Physics-Mathematics Bridges

**TEST P-1: RMT Universality Across Domains**
The same RMT statistics appear in L-function zeros AND inflationary landscape eigenvalues. Test: compute nearest-neighbor spacing distributions for (a) EC L-function zeros from bsd_joined, (b) modular form Hecke eigenvalues from mf_newforms, (c) Artin rep conductors. Do they all fall in the same universality class?
- Falsification: different domains show different universality classes (the interesting outcome)
- Data: bsd_joined (positive_zeros), mf_newforms, artin_reps
- Agent: Harmonia (spectral) + Charon (battery)

**TEST P-2: Holographic Entropy Analogy in the Tensor**
The Ryu-Takayanagi formula says entanglement entropy scales with boundary area, not volume. Test: in the Prometheus tensor, does the "entropy" of cross-domain coupling (Shannon entropy of bond singular values) scale with the NUMBER OF FEATURES (boundary) or the NUMBER OF OBJECTS (volume)?
- Falsification: entropy scales with volume (no holographic property)
- Data: harmonia results (bond SVs from deep_sweep.json)
- Agent: Harmonia

**TEST P-3: Knot Volume Conjecture Proxy**
The volume conjecture (MATH-0334) says colored Jones polynomial at roots of unity determines hyperbolic volume. We don't have colored Jones, but we have Jones polynomial + Alexander polynomial. Test: compute Jones at q=exp(2pi*i/N) for N=3..10 for all 2977 knots. Do these values correlate with the knot determinant (a proxy for complexity related to volume)?
- Falsification: zero correlation (Jones evaluations are independent of complexity)
- Data: cartography/knots/data/knots.json
- Agent: Aporia (computation, already have Mahler measures)

### Barrier-Probing Tests

**TEST B-1: Search Space Collapse via Modular Arithmetic**
The C11 scaling law shows mod-p fingerprints concentrate 8-16x. Apply this as a SIEVE: for OEIS sequences with open conjectures (e.g., "does this sequence contain a perfect square?"), compute mod-p residues for p=2..23. If the mod-p pattern excludes squares, the conjecture is resolved for free.
- Falsification: mod-p sieve resolves zero open conjectures (the sieve is too weak)
- Data: prometheus_sci.analysis.oeis (394K sequences)
- Agent: Ergon

**TEST B-2: Proof Complexity Proxy**
Formal proofs have a LENGTH. Short proofs = easy theorems. Long proofs = hard. Test: for theorems in our catalog that are proved, estimate proof complexity from the mathematical structure (number of quantifier alternations, depth of induction, etc.). Does proof complexity correlate with which barrier type blocks the open analog?
- Falsification: no correlation (barrier type is not related to proof complexity)
- Data: aporia/mathematics/questions.jsonl + solutions.jsonl
- Agent: Aporia (analysis)

**TEST B-3: Independence Oscillation Detector (Prototype)**
Build a prototype: for 10 well-studied conjectures (Goldbach, twin primes, Collatz, etc.), plot the relevant test statistic as a function of N. Classify each as CONVERGENT (steadily approaches limit), OSCILLATING (fluctuates without converging), or FLAT (no trend). Compare oscillation patterns to known-independent statements (Continuum Hypothesis analogs in finite domains).
- Falsification: all conjectures show convergent behavior (no independence signal)
- Data: computational (prime sieves, sequence computation)
- Agent: Aporia (design) + Ergon (computation)

### Deep Structure Tests

**TEST D-1: Is Megethos Really Magnitude?**
The Megethos phoneme was assumed to be "size/magnitude." But NF PCA showed Megethos (log_disc_abs) is only PC3 (18.3%), not PC1. Test: across ALL domains in the tensor, what does the dominant singular value actually encode? Compute the feature loading of the top SV for every domain. Is it always "size" or does it vary?
- Falsification: dominant SV is the same feature (magnitude) in every domain (Megethos IS universal)
- Data: tensor domain features from harmonia/src/domain_index.py
- Agent: Ergon

**TEST D-2: Phoneme Independence**
The 5 original phonemes (complexity, rank, symmetry, arithmetic, spectral) were hypothesized to be independent. PCA on NF showed they're NOT (PC1 mixes class_number and regulator). Test: compute mutual information between all pairs of phoneme scores across all domains. Which pairs are entangled? Entanglement = theorems.
- Falsification: all phonemes are independent (no entanglement = no theorems to find)
- Data: harmonia phoneme scores
- Agent: Harmonia

**TEST D-3: Tensor Cohomological Expansion**
Inspired by quantum LDPC codes: if A↔B has bond rank r1 and B↔C has bond rank r2, what is the bond rank of A↔C? In cohomological expansion, the composed rank is bounded below. Test: for all domain triples in deep_sweep.json, compute whether bridge composition preserves rank.
- Falsification: composed rank drops to zero (no expansion property)
- Data: harmonia/results/deep_sweep.json (837 entries)
- Agent: Charon (battery) + Ergon (computation)

**TEST D-4: Sleeping Beauty Activation**
68,770 OEIS sequences with high structure but low connectivity. For each, compute 5 fingerprints: mod-p residues (p=2..7), digit sums, CF of ratios, growth rate class, and spectral content (DFT). Cluster the Sleeping Beauties by fingerprint. Do the clusters correspond to mathematical domains?
- Falsification: random clustering (Sleeping Beauties have no internal structure)
- Data: OEIS data in prometheus_sci or cartography
- Agent: Ergon (computation, tensor builder)

---

## Test Priority Matrix

| Priority | Test | Why | Agent |
|----------|------|-----|-------|
| 1 | X-3 Class Number One blind trial | Instant calibration, uses new nf_fields | Aporia |
| 2 | D-3 Cohomological expansion | Tests deepest structural property of tensor | Charon + Ergon |
| 3 | X-6 Odlyzko bound verification | Data integrity + calibration on 22M NF | Charon |
| 4 | P-1 RMT universality across domains | Bridges physics and number theory | Harmonia |
| 5 | D-1 Megethos reality check | Foundational — is our main axis what we think? | Ergon |
| 6 | X-4 Goldfeld in complete census | Clean test on 3.06M unbiased curves | Ergon |
| 7 | B-3 Independence oscillation prototype | First-ever computational independence detector | Aporia + Ergon |
| 8 | P-3 Knot volume proxy | Attacks silent island from physics direction | Aporia |
| 9 | D-4 Sleeping Beauty activation | 68K sequences waiting to speak | Ergon |
| 10 | X-7 Artin conductor-dimension scaling | New scaling law from 798K reps | Ergon + Kairos |

---

*Not every question deserves an answer. Some deserve a better question.*
*The filter: does the answer change what we DO? If not, it's philosophy. If yes, it's science.*

*Aporia, 2026-04-16*
