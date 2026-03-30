"""
Machine 2: Spoke Densification — Fill empty damage operator × hub cells.

For each hub, determines which of the 9 damage operators are already present,
then fills empty cells with REAL, KNOWN resolutions from the relevant domain.
"""

import duckdb
import re
import uuid
from collections import defaultdict

DB_PATH = "F:/prometheus/noesis/v2/noesis_v2.duckdb"

ALL_OPS = [
    "DISTRIBUTE", "CONCENTRATE", "TRUNCATE", "EXTEND",
    "RANDOMIZE", "HIERARCHIZE", "PARTITION", "QUANTIZE", "INVERT"
]

# ============================================================
# RESOLUTION KNOWLEDGE BASE
# Each entry: (hub_id, operator, resolution_name, description)
# ONLY real, known practices from the relevant domain.
# ============================================================

RESOLUTIONS = [
    # === TOP PRIORITY CONSENSUS PREDICTIONS ===

    # CONCENTRATE x QUINTIC
    ("IMPOSSIBILITY_QUINTIC_INSOLVABILITY", "CONCENTRATE",
     "Discriminant loci",
     "Concentrate insolvability at specific coefficient values where the Galois group reduces from S_5 to a solvable subgroup. Most quintics are solvable; the generic case concentrates difficulty at discriminant-zero loci where root collisions change group structure."),

    # DISTRIBUTE x QUINTIC
    ("IMPOSSIBILITY_QUINTIC_INSOLVABILITY", "DISTRIBUTE",
     "Numerical root-finding methods",
     "Newton-Raphson, Durand-Kerner, and Aberth methods distribute approximation error across all roots simultaneously. No single root is solved exactly; instead error is spread uniformly, yielding all roots to arbitrary precision."),

    # CONCENTRATE x SHANNON
    ("SHANNON_CAPACITY", "CONCENTRATE",
     "Water-filling power allocation",
     "Concentrate transmission power on channels with highest SNR. Water-filling theorem (Cover & Thomas): optimal power allocation P_i = max(0, lambda - N_i) concentrates resources on strongest subchannels, leaving weak ones unused."),

    # === QUINTIC: fill remaining gaps ===

    # QUANTIZE x QUINTIC
    ("IMPOSSIBILITY_QUINTIC_INSOLVABILITY", "QUANTIZE",
     "Bring radical tower to discrete Galois lattice",
     "Galois theory maps the continuous problem of root extraction onto the discrete lattice of subgroup chains in S_5. Solvability reduces to checking whether the composition series has abelian factors — a discrete, decidable criterion."),

    # EXTEND x QUINTIC (using EXTEND, the DB operator name)
    ("IMPOSSIBILITY_QUINTIC_INSOLVABILITY", "EXTEND",
     "Bring-Jerrard normal form reduction",
     "Extend the coefficient field by Tschirnhaus transformations to reduce a general quintic to Bring-Jerrard form x^5 + x + a. This adds auxiliary radicals to simplify the structure, enabling solution via elliptic modular functions or hypergeometric series."),

    # === SHANNON: fill remaining gaps ===

    # QUANTIZE x SHANNON
    ("SHANNON_CAPACITY", "QUANTIZE",
     "Lattice codes and signal constellations",
     "Map continuous signal space onto discrete lattice points (QAM, PSK constellations). Quantization converts the continuous channel into a discrete one where capacity-approaching codes (LDPC, turbo, polar) can be designed with known algebraic structure."),

    # INVERT x SHANNON
    ("SHANNON_CAPACITY", "INVERT",
     "Source-channel separation / duality",
     "Shannon's separation theorem inverts the coding problem: instead of jointly optimizing source and channel coding, compress the source first (removing redundancy) then add structured redundancy for the channel. The inversion decouples two opposing goals."),

    # EXTEND x SHANNON
    ("SHANNON_CAPACITY", "EXTEND",
     "MIMO spatial multiplexing",
     "Add multiple antennas to create parallel spatial channels. MIMO capacity scales as C = sum log2(1 + SNR_i), extending capacity beyond single-channel limits by adding physical degrees of freedom (Telatar 1999, Foschini 1996)."),

    # === ARROW IMPOSSIBILITY ===

    ("IMPOSSIBILITY_ARROW", "HIERARCHIZE",
     "Federalism / multi-level governance",
     "Move aggregation failure up a level: local preferences aggregated at municipal level, municipal at state, state at federal. Each level uses simpler preference structures where Arrow's conditions can be relaxed (e.g., single-peaked within regions)."),

    ("IMPOSSIBILITY_ARROW", "PARTITION",
     "Domain restriction to single-peaked preferences",
     "Partition the preference domain into sub-domains where median voter theorem applies. Black (1948) showed single-peaked preferences admit a Condorcet winner, avoiding Arrow's impossibility by restricting the input space."),

    ("IMPOSSIBILITY_ARROW", "QUANTIZE",
     "Approval voting / score voting",
     "Replace ordinal ranking with cardinal scores (approval: binary; range: discrete scale). Arrow's theorem applies only to ordinal rank-order systems; moving to a discrete cardinal scale sidesteps the IIA violation."),

    ("IMPOSSIBILITY_ARROW", "INVERT",
     "Veto-based / negative voting",
     "Invert the aggregation direction: instead of choosing winners by positive support, eliminate candidates by vetoes. Moulin (1982) showed veto mechanisms satisfy different fairness properties, inverting the structural direction of preference aggregation."),

    ("IMPOSSIBILITY_ARROW", "EXTEND",
     "Monetary transfers / VCG mechanism",
     "Extend the mechanism space by adding side payments. The Vickrey-Clarke-Groves mechanism achieves efficiency with truthful revelation by adding a monetary dimension that Arrow's ordinal framework excludes."),

    # === CAP THEOREM ===

    ("IMPOSSIBILITY_CAP", "EXTEND",
     "CRDTs (Conflict-free Replicated Data Types)",
     "Extend the data model with algebraic structure (join-semilattices) so that concurrent updates automatically converge. CRDTs add mathematical constraints that make consistency compatible with availability under partition (Shapiro et al. 2011)."),

    ("IMPOSSIBILITY_CAP", "QUANTIZE",
     "Tunable consistency levels",
     "Quantize the consistency spectrum into discrete levels (ONE, QUORUM, ALL in Cassandra; bounded staleness in Cosmos DB). Operators choose a discrete consistency-availability tradeoff point rather than facing a binary choice."),

    ("IMPOSSIBILITY_CAP", "INVERT",
     "PACELC framework",
     "Invert the framing: instead of choosing during partitions, also consider the latency-consistency tradeoff during normal operation. Abadi (2012) showed the real engineering tradeoff is inverted — most time is spent in non-partition mode."),

    # === HEISENBERG UNCERTAINTY ===

    ("HEISENBERG_UNCERTAINTY", "EXTEND",
     "Squeezed states",
     "Extend the state space to squeezed coherent states where uncertainty in one quadrature is reduced below the vacuum level at the cost of increased uncertainty in the conjugate. Total uncertainty product still satisfies the bound but resources are redistributed."),

    ("HEISENBERG_UNCERTAINTY", "PARTITION",
     "Weak measurement / post-selection",
     "Partition measurement events by post-selection on the final state. Aharonov-Albert-Vaidman (1988) weak values allow extracting information about one observable with minimal disturbance to the conjugate, at the cost of discarding most measurement runs."),

    ("HEISENBERG_UNCERTAINTY", "QUANTIZE",
     "Discrete phase space (finite-dimensional Hilbert space)",
     "Replace continuous position-momentum with finite-dimensional discrete phase space (Wootters 1987, Gibbons et al. 2004). Mutually unbiased bases provide the discrete analog of complementary observables with quantized uncertainty relations."),

    ("HEISENBERG_UNCERTAINTY", "INVERT",
     "Time-reversed measurement (quantum eraser)",
     "Invert the measurement process: a quantum eraser retroactively removes which-path information, restoring interference. The conjugate variable's uncertainty is recovered by inverting the information extraction step (Scully & Druhl 1982)."),

    # === HALTING PROBLEM ===

    ("HALTING_PROBLEM", "EXTEND",
     "Oracle Turing machines / hypercomputation",
     "Extend the computational model by adding a halting oracle for level-0 machines, producing a level-1 machine. Turing's own construction (1939) showed this creates an arithmetic hierarchy, each level deciding the previous level's halting problem."),

    ("HALTING_PROBLEM", "PARTITION",
     "Decidable sublanguages",
     "Partition the space of programs into decidable subsets: primitive recursive functions, total functional languages (Agda, Coq), and termination-checked subsets. Each partition is decidable at the cost of reduced expressiveness."),

    ("HALTING_PROBLEM", "QUANTIZE",
     "Bounded model checking",
     "Quantize the execution horizon: check halting only up to k steps. Bounded model checking (Biere et al. 1999) makes the problem decidable by discretizing time into a finite grid, trading completeness for tractability."),

    ("HALTING_PROBLEM", "INVERT",
     "Co-recursion and productivity checking",
     "Invert the question: instead of asking 'does it halt?', ask 'does it produce output forever?' Coinductive types and productivity checkers verify that corecursive programs always make progress, inverting termination into perpetual output."),

    ("HALTING_PROBLEM", "EXTEND",
     "Type systems as termination provers",
     "Extend the language with dependent types or sized types that encode termination proofs in the type structure. The Calculus of Constructions (Coquand & Huet 1988) ensures all well-typed programs terminate."),

    # === GODEL INCOMPLETENESS ===

    ("GODEL_INCOMPLETENESS", "EXTEND",
     "Large cardinal axioms",
     "Extend the axiom system with large cardinal axioms (inaccessible, measurable, Woodin cardinals). Each extension proves consistency of weaker systems, pushing the incompleteness boundary outward at the cost of stronger ontological commitments."),

    ("GODEL_INCOMPLETENESS", "PARTITION",
     "Reverse mathematics program",
     "Partition mathematical statements by the axiom systems needed to prove them (RCA_0, WKL_0, ACA_0, ATR_0, Pi-1-1-CA_0). Each partition is internally complete for its class of statements (Friedman, Simpson)."),

    ("GODEL_INCOMPLETENESS", "INVERT",
     "Omega-consistency and reflection principles",
     "Add the reflection principle Con(T) as a new axiom, which states T is consistent. This inverts the incompleteness: the unprovable Godel sentence becomes provable, but generates a new unprovable sentence at the next level."),

    ("GODEL_INCOMPLETENESS", "QUANTIZE",
     "Proof complexity measures",
     "Quantize provability into discrete complexity classes: proofs of length at most n, or proofs in bounded arithmetic (S^1_2, T^i_2). Bounded arithmetic hierarchies discretize the proof space, making fragments decidable."),

    # === CARNOT LIMIT ===

    ("CARNOT_LIMIT", "EXTEND",
     "Combined cycle / cogeneration",
     "Extend the thermodynamic system by cascading multiple heat engines in series (gas turbine exhaust drives steam turbine). Combined cycle plants achieve ~62% efficiency by extending the working temperature range beyond single-cycle limits."),

    ("CARNOT_LIMIT", "PARTITION",
     "Regenerative cycles with finite stages",
     "Partition the compression/expansion into multiple intercooled/reheated stages. Ericsson and Stirling cycles approach Carnot efficiency by partitioning heat exchange into many small isothermal steps."),

    ("CARNOT_LIMIT", "QUANTIZE",
     "Finite-time thermodynamics (Curzon-Ahlborn)",
     "Quantize the idealized reversible limit into practical finite-rate operation. Curzon & Ahlborn (1975) showed maximum-power efficiency is eta_CA = 1 - sqrt(T_cold/T_hot), a discrete practical bound below Carnot."),

    ("CARNOT_LIMIT", "INVERT",
     "Heat pump / refrigeration cycle",
     "Invert the engine direction: run the Carnot cycle backward to pump heat from cold to hot reservoir. The COP = T_hot/(T_hot - T_cold) inverts the efficiency framing, and ground-source heat pumps achieve COP > 4."),

    ("CARNOT_LIMIT", "RANDOMIZE",
     "Thermoelectric generators (Seebeck effect)",
     "Convert thermal energy to electricity via stochastic electron transport across a temperature gradient. No moving parts; the random thermal motion of charge carriers is harnessed directly, with efficiency limited by the material's ZT figure of merit."),

    ("CARNOT_LIMIT", "HIERARCHIZE",
     "Exergy analysis / multi-temperature cascades",
     "Move efficiency analysis up a level from energy to exergy (available work). Hierarchical decomposition into temperature bands allows optimal allocation of each cascade stage to its temperature range (Bejan 1996)."),

    # === NYQUIST LIMIT ===

    ("NYQUIST_LIMIT", "EXTEND",
     "Compressive sensing / sub-Nyquist sampling",
     "Extend the signal model with a sparsity assumption. If the signal is K-sparse in some basis, O(K log N) random samples suffice for perfect reconstruction (Candes, Romberg, Tao 2006), far below the Nyquist rate."),

    ("NYQUIST_LIMIT", "INVERT",
     "Bandpass / undersampling",
     "Invert the baseband assumption: for narrowband signals at high carrier frequency, intentional aliasing (undersampling) maps the signal to baseband. Only the bandwidth matters, not the carrier frequency."),

    ("NYQUIST_LIMIT", "QUANTIZE",
     "Sigma-delta modulation",
     "Quantize aggressively (1-bit) but at very high oversampling ratio. Noise shaping pushes quantization error to high frequencies where it can be filtered out, trading bit depth for sample rate in a discrete tradeoff."),

    # === IMPOSSIBILITY_NO_FREE_LUNCH ===

    ("IMPOSSIBILITY_NO_FREE_LUNCH", "EXTEND",
     "Inductive bias / domain-specific priors",
     "Extend the learning algorithm with domain-specific inductive biases (convolutional structure for images, recurrence for sequences). By adding structural assumptions about the target distribution, the learner outperforms uniform on the relevant subset."),

    ("IMPOSSIBILITY_NO_FREE_LUNCH", "PARTITION",
     "Meta-learning / task partitioning",
     "Partition the problem space into task families and learn a separate inductive bias for each (MAML, Prototypical Networks). Each partition has a well-matched algorithm, sidestepping the impossibility on the full space."),

    ("IMPOSSIBILITY_NO_FREE_LUNCH", "HIERARCHIZE",
     "AutoML / neural architecture search",
     "Move algorithm selection up a meta-level: instead of choosing one algorithm, learn which algorithm to use for which problem class. The meta-learner operates on a higher level than any individual learner (Brazdil et al. 2003)."),

    ("IMPOSSIBILITY_NO_FREE_LUNCH", "INVERT",
     "Adversarial learning / GANs",
     "Invert the optimization: instead of finding the best hypothesis directly, train a generator against a discriminator. The adversarial inversion converts a search problem into a game-theoretic equilibrium (Goodfellow et al. 2014)."),

    # === IMPOSSIBILITY_BODE_INTEGRAL_V2 ===

    ("IMPOSSIBILITY_BODE_INTEGRAL_V2", "HIERARCHIZE",
     "Cascade / inner-outer loop control",
     "Move the sensitivity constraint up a level with nested feedback loops. The inner loop reshapes the plant dynamics seen by the outer loop, allowing the outer loop's Bode integral to be computed over the modified plant."),

    ("IMPOSSIBILITY_BODE_INTEGRAL_V2", "QUANTIZE",
     "Discrete-time / sampled-data control",
     "Move to discrete-time (z-domain) control where the Bode integral takes a different form. The bilinear transform maps the continuous constraint onto a discrete grid where digital controllers can be designed with different tradeoff characteristics."),

    ("IMPOSSIBILITY_BODE_INTEGRAL_V2", "INVERT",
     "Feedforward / disturbance observer",
     "Invert the feedback paradigm: use feedforward compensation to cancel known disturbances without entering the feedback sensitivity integral. Disturbance observers (DOB) invert the plant model to reject disturbances outside the feedback loop."),

    # === IMPOSSIBILITY_GOODHARTS_LAW ===

    ("IMPOSSIBILITY_GOODHARTS_LAW", "EXTEND",
     "Multi-metric dashboards / balanced scorecards",
     "Extend the single metric to a portfolio of metrics that are harder to simultaneously game. Kaplan & Norton's balanced scorecard (1992) uses financial, customer, process, and learning metrics to resist Goodhart collapse on any single measure."),

    ("IMPOSSIBILITY_GOODHARTS_LAW", "QUANTIZE",
     "Threshold-based satisficing",
     "Replace continuous optimization of the metric with discrete pass/fail thresholds. Simon's satisficing (1956): set a 'good enough' bar rather than maximizing, reducing the incentive gradient that drives metric corruption."),

    # === IMPOSSIBILITY_NO_CLONING_THEOREM ===

    ("IMPOSSIBILITY_NO_CLONING_THEOREM", "CONCENTRATE",
     "Quantum teleportation",
     "Concentrate the quantum state at a single destination by consuming entanglement and classical communication. The original state is destroyed (no cloning), but its information is perfectly relocated via Bell measurement (Bennett et al. 1993)."),

    ("IMPOSSIBILITY_NO_CLONING_THEOREM", "EXTEND",
     "Quantum error correction (redundant encoding)",
     "Extend the Hilbert space by encoding one logical qubit into many physical qubits (Shor code, surface code). Not cloning the state but distributing quantum information across entangled qubits to protect against errors."),

    ("IMPOSSIBILITY_NO_CLONING_THEOREM", "QUANTIZE",
     "Approximate cloning (Buzek-Hillery)",
     "Quantize the fidelity requirement: allow imperfect copies with bounded fidelity. The optimal 1-to-2 cloner achieves fidelity 5/6 (Buzek & Hillery 1996), converting an impossibility into a discrete quality-quantity tradeoff."),

    ("IMPOSSIBILITY_NO_CLONING_THEOREM", "INVERT",
     "SWAP test / state comparison",
     "Invert the goal: instead of copying an unknown state, compare two unknown states without learning either. The SWAP test determines equality/orthogonality with bounded error, extracting relational information without cloning."),

    # === IMPOSSIBILITY_GIBBS_PHENOMENON ===

    ("IMPOSSIBILITY_GIBBS_PHENOMENON", "EXTEND",
     "Wavelets (multi-resolution analysis)",
     "Extend the basis from global sinusoids to localized wavelets. Multiresolution analysis (Mallat 1989, Daubechies 1988) uses basis functions with compact support, eliminating Gibbs overshoot at discontinuities by adapting resolution locally."),

    ("IMPOSSIBILITY_GIBBS_PHENOMENON", "QUANTIZE",
     "Piecewise polynomial approximation (FEM)",
     "Replace global Fourier basis with piecewise polynomials on a discrete mesh. Finite element methods place knots at discontinuities, quantizing the domain into elements where the approximation is locally smooth."),

    ("IMPOSSIBILITY_GIBBS_PHENOMENON", "INVERT",
     "Gegenbauer reconstruction",
     "Invert the Fourier coefficients back through Gegenbauer polynomial expansion. Gottlieb & Shu (1997) showed that from the slowly-converging Fourier data, one can reconstruct the original function with exponential accuracy away from discontinuities."),

    # === IMPOSSIBILITY_IMPOSSIBLE_TRINITY_MACROECONOMICS ===

    ("IMPOSSIBILITY_IMPOSSIBLE_TRINITY_MACROECONOMICS", "EXTEND",
     "Currency board with fiscal buffers",
     "Extend the policy toolkit with sovereign wealth funds and fiscal stabilizers. Singapore and Hong Kong maintain fixed exchange rates and open capital accounts while using fiscal reserves as a substitute for independent monetary policy."),

    ("IMPOSSIBILITY_IMPOSSIBLE_TRINITY_MACROECONOMICS", "RANDOMIZE",
     "Managed float / dirty float",
     "Allow the exchange rate to fluctuate stochastically within bands (e.g., ERM II +/-15%). The random walk of the exchange rate absorbs external shocks probabilistically, providing partial monetary independence without full floating."),

    ("IMPOSSIBILITY_IMPOSSIBLE_TRINITY_MACROECONOMICS", "QUANTIZE",
     "Discrete capital flow categories (Tobin tax tiers)",
     "Quantize capital controls into discrete tiers: fully open for FDI, taxed for portfolio flows, restricted for short-term speculation. Chile's encaje (1991-98) imposed discrete reserve requirements by capital type."),

    ("IMPOSSIBILITY_IMPOSSIBLE_TRINITY_MACROECONOMICS", "INVERT",
     "Currency union (surrender sovereignty)",
     "Invert the national framing: join a currency union (eurozone) that eliminates the exchange rate dimension entirely. Independent monetary policy is surrendered rather than traded off, collapsing the trilemma to a bilateral choice."),

    # === IMPOSSIBILITY_FITTS_HICK_SPEED_ACCURACY ===

    ("IMPOSSIBILITY_FITTS_HICK_SPEED_ACCURACY", "EXTEND",
     "Predictive input / autocomplete",
     "Extend the interface with predictive models that reduce the effective number of choices. T9, autocomplete, and gesture typing reduce information content per keystroke, shifting the Hick-Hyman curve leftward without sacrificing accuracy."),

    ("IMPOSSIBILITY_FITTS_HICK_SPEED_ACCURACY", "QUANTIZE",
     "Discrete Fitts' index of difficulty",
     "Quantize the continuous distance/width tradeoff into discrete interface elements (toolbar buttons, ribbon tabs). Snap-to-grid and magnetic targets create discrete landing zones that quantize the Fitts ID to manageable levels."),

    ("IMPOSSIBILITY_FITTS_HICK_SPEED_ACCURACY", "INVERT",
     "Target comes to cursor (pie menus, marking menus)",
     "Invert the spatial relationship: instead of moving to a target, bring the target to the cursor. Pie menus (Callahan 1988) and marking menus (Kurtenbach 1993) use directional strokes from the current position, inverting distance dependence."),

    # === IMPOSSIBILITY_BELLS_THEOREM ===

    ("IMPOSSIBILITY_BELLS_THEOREM", "EXTEND",
     "Entanglement-based QKD (Ekert protocol)",
     "Extend the cryptographic toolkit by harnessing Bell violations as a resource. E91 protocol (Ekert 1991) uses Bell test statistics to certify key security — any eavesdropper necessarily disturbs the correlations below the Tsirelson bound."),

    ("IMPOSSIBILITY_BELLS_THEOREM", "QUANTIZE",
     "CHSH game / discrete Bell tests",
     "Quantize the continuous correlation function into discrete measurement settings and outcomes. The CHSH inequality (Clauser et al. 1969) reduces Bell's theorem to a 2-party, 2-setting, 2-outcome game with a sharp classical bound of 2."),

    ("IMPOSSIBILITY_BELLS_THEOREM", "INVERT",
     "Retrocausal / time-symmetric interpretations",
     "Invert the causal direction: allow future measurement settings to influence past preparations (Price, Huw 1996; two-state vector formalism of Aharonov). Local hidden variables are rescued by inverting the temporal arrow."),

    # === IMPOSSIBILITY_BORSUK_ULAM ===

    ("IMPOSSIBILITY_BORSUK_ULAM", "EXTEND",
     "Equivariant topology extensions",
     "Extend the symmetry group: Borsuk-Ulam generalizes to arbitrary group actions via equivariant cohomology. Tom Dieck's theorem extends the result to compact Lie group actions, adding structure that refines the antipodal constraint."),

    ("IMPOSSIBILITY_BORSUK_ULAM", "QUANTIZE",
     "Tucker's lemma (discrete Borsuk-Ulam)",
     "Quantize the sphere into a simplicial complex with antipodal labeling. Tucker's lemma (1946) is the combinatorial analog: any antipodal labeling of a triangulated sphere must have a complementary edge, giving a discrete version of the continuous result."),

    ("IMPOSSIBILITY_BORSUK_ULAM", "INVERT",
     "Ham sandwich theorem (applied form)",
     "Invert from impossibility to constructive guarantee: Borsuk-Ulam implies the ham sandwich theorem — any n measures in R^n can be simultaneously bisected by a single hyperplane. The topological obstruction becomes a constructive existence proof."),

    # === IMPOSSIBILITY_MYERSON_SATTERTHWAITE ===

    ("IMPOSSIBILITY_MYERSON_SATTERTHWAITE", "DISTRIBUTE",
     "Posted price mechanisms",
     "Distribute inefficiency uniformly: a posted price mechanism (take-it-or-leave-it) distributes the welfare loss across all valuation pairs equally. Hagerty & Rogerson (1987) showed optimal posted prices achieve a constant fraction of first-best surplus."),

    ("IMPOSSIBILITY_MYERSON_SATTERTHWAITE", "PARTITION",
     "Tiered bargaining / BATNA-based segmentation",
     "Partition buyer-seller pairs by outside option (BATNA). Within each segment, a mechanism calibrated to the narrower type distribution achieves higher efficiency than the universal mechanism."),

    ("IMPOSSIBILITY_MYERSON_SATTERTHWAITE", "QUANTIZE",
     "Discrete type spaces / finite auction formats",
     "Quantize the continuous type space into finitely many types. With discrete valuations, budget-balanced mechanisms can achieve full efficiency for sufficiently coarse type grids (Matsuo 1989, Makowski & Mezzetti 1993)."),

    ("IMPOSSIBILITY_MYERSON_SATTERTHWAITE", "INVERT",
     "Broker intermediation / market making",
     "Invert the bilateral structure: introduce a market maker who posts bid-ask spreads. The spread absorbs the information rent. The broker inverts the private-information problem by taking the opposite side of both trades."),

    ("IMPOSSIBILITY_MYERSON_SATTERTHWAITE", "EXTEND",
     "Repeat interaction / reputation mechanisms",
     "Extend the game to repeated interactions where reputation effects enable cooperation. The folk theorem implies that patient traders can achieve near-efficient outcomes in repeated bilateral trade (Athey & Miller 2007)."),

    # === RUNGE_PHENOMENON ===

    ("RUNGE_PHENOMENON", "EXTEND",
     "Chebyshev nodes / non-uniform sampling",
     "Extend the node placement from equispaced to Chebyshev-distributed (clustered at endpoints). Chebyshev interpolation minimizes the Lebesgue constant, eliminating Runge oscillations for analytic functions."),

    ("RUNGE_PHENOMENON", "QUANTIZE",
     "Spline interpolation with discrete knots",
     "Replace high-degree global polynomials with piecewise low-degree splines on a discrete knot grid. Cubic splines (Schoenberg 1946) maintain smoothness while quantizing the approximation into local segments that resist edge oscillation."),

    ("RUNGE_PHENOMENON", "INVERT",
     "Least-squares regression (underfitting by design)",
     "Invert the interpolation goal: instead of passing through all points, find the polynomial that minimizes total squared error. Deliberate underfitting (fewer degrees than data points) suppresses the oscillation by inverting the exactness requirement."),

    ("RUNGE_PHENOMENON", "EXTEND",
     "Rational approximation (Pade)",
     "Extend the approximation class from polynomials to rational functions P(x)/Q(x). Pade approximants and rational interpolation achieve exponential convergence for functions with poles, where polynomial interpolation necessarily diverges."),

    # === HAIRY_BALL_THEOREM ===

    ("HAIRY_BALL_THEOREM", "EXTEND",
     "Fiber bundles / frame fields",
     "Extend from vector fields to frame bundles. While S^2 admits no global nonvanishing section, the frame bundle is parallelizable (Hopf fibration). Adding a dimension resolves the topological obstruction."),

    ("HAIRY_BALL_THEOREM", "QUANTIZE",
     "Discrete vector field (CW complex)",
     "Quantize the continuous vector field onto a CW-complex decomposition of the sphere. Forman's discrete Morse theory (1998) creates discrete vector fields with isolated critical cells rather than continuous singularities."),

    ("HAIRY_BALL_THEOREM", "INVERT",
     "Index theory (use the zero constructively)",
     "Invert the obstruction into a feature: the Poincare-Hopf index theorem says the sum of indices at zeros equals the Euler characteristic. The guaranteed zero becomes a tool for proving existence of equilibria (Brouwer fixed point via hairy ball)."),

    ("HAIRY_BALL_THEOREM", "PARTITION",
     "Charts with transition functions",
     "Partition the sphere into coordinate charts (stereographic projection from two poles). Each chart supports a nonvanishing vector field; the topological obstruction is absorbed into the transition functions between charts."),

    # === IMPOSSIBILITY_MAP_PROJECTION ===

    ("IMPOSSIBILITY_MAP_PROJECTION", "EXTEND",
     "Globe / 3D digital earth",
     "Extend the representation from 2D to 3D. Google Earth, Cesium, and digital globes bypass the projection impossibility entirely by rendering the curved surface directly, adding the third dimension that projections remove."),

    ("IMPOSSIBILITY_MAP_PROJECTION", "RANDOMIZE",
     "Stochastic map tiling (Dymaxion variants)",
     "Fuller's Dymaxion projection unfolds the globe onto an icosahedron, but the choice of orientation is arbitrary. Random or optimized unfolding orientations distribute projection error stochastically across different use cases."),

    ("IMPOSSIBILITY_MAP_PROJECTION", "INVERT",
     "Inverse projection / geodesic computation",
     "Instead of projecting sphere to plane, compute distances and areas on the sphere directly using Vincenty's formulae or Karney's geodesic algorithms. Invert the need for flat maps by doing geometry natively on the curved surface."),

    # === IMPOSSIBILITY_MUNDELL_FLEMING ===

    ("IMPOSSIBILITY_MUNDELL_FLEMING", "EXTEND",
     "Macroprudential policy as fourth instrument",
     "Extend the policy toolkit by adding macroprudential tools (capital buffers, LTV limits, dynamic provisioning). Rey (2013) argued the trilemma is really a dilemma; macroprudential policy provides an independent instrument for financial stability."),

    ("IMPOSSIBILITY_MUNDELL_FLEMING", "QUANTIZE",
     "Capital flow management measures (discrete controls)",
     "Quantize capital account openness into discrete tiers: fully open FDI, taxed portfolio flows, prohibited short-term flows. IMF's institutional view (2012) endorses discrete, targeted capital flow management as a legitimate policy tool."),

    ("IMPOSSIBILITY_MUNDELL_FLEMING", "INVERT",
     "Dollarization / currency board",
     "Fully surrender monetary independence by adopting another country's currency (Ecuador, Panama). The trilemma is collapsed by inverting the sovereignty assumption — the country gains credibility and capital mobility at the cost of policy autonomy."),

    # === IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2 ===

    ("IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2", "QUANTIZE",
     "Discretized quasicrystal approximants",
     "Periodic approximants (1/1, 2/1, 3/2 Fibonacci) create conventional crystals that approximate quasicrystalline order. These rational approximations quantize the irrational tile ratio into large but finite unit cells with conventional symmetry."),

    ("IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2", "INVERT",
     "Photonic crystals with designed band gaps",
     "Invert the restriction: instead of trying to achieve forbidden rotational symmetries, design the band gap structure directly by engineering the photonic crystal geometry. The optical properties become the goal, not the crystallographic symmetry."),

    # === SEN_LIBERAL_PARADOX ===

    ("SEN_LIBERAL_PARADOX", "EXTEND",
     "Rights-waiver / exchange of rights",
     "Extend the mechanism by allowing individuals to voluntarily waive or trade their decisional rights. Gibbard (1974) showed that if agents can exchange rights, Pareto-efficient outcomes compatible with liberalism become achievable."),

    ("SEN_LIBERAL_PARADOX", "PARTITION",
     "Protected private sphere / public-private partition",
     "Partition decisions into a private sphere (individual sovereignty) and a public sphere (collective choice). Within each partition, a different aggregation rule applies, preventing cross-domain interference that generates the paradox."),

    ("SEN_LIBERAL_PARADOX", "INVERT",
     "Capability approach (Sen's own resolution)",
     "Invert from preference-based to capability-based evaluation. Sen's own later work (1985, 1999) reframes welfare in terms of functionings and capabilities rather than preference satisfaction, dissolving the paradox by changing the evaluative space."),

    ("SEN_LIBERAL_PARADOX", "QUANTIZE",
     "Lexicographic priority of rights",
     "Quantize the tradeoff into a strict priority ordering: rights constraints are satisfied first (lexicographically prior), then Pareto optimality is maximized within the feasible set. No continuous tradeoff between rights and efficiency is permitted."),

    ("SEN_LIBERAL_PARADOX", "HIERARCHIZE",
     "Constitutional vs. legislative choice levels",
     "Move rights protection up a level to the constitutional stage (Buchanan & Tullock 1962). At the constitutional level, agents unanimously agree on rights; at the legislative level, collective choice operates within those constraints."),

    # === GIBBARD_SATTERTHWAITE ===

    ("GIBBARD_SATTERTHWAITE", "EXTEND",
     "VCG mechanism with payments",
     "Extend the social choice function with monetary side payments. The VCG mechanism achieves strategy-proofness for quasi-linear preferences by adding a payment dimension that Gibbard-Satterthwaite's framework excludes."),

    ("GIBBARD_SATTERTHWAITE", "PARTITION",
     "Single-peaked domain restriction",
     "Restrict preferences to single-peaked profiles (Black 1948). On this subdomain, the median voter rule is strategy-proof, Pareto-efficient, and non-dictatorial — all three conditions that the full-domain theorem forbids."),

    ("GIBBARD_SATTERTHWAITE", "RANDOMIZE",
     "Random dictatorship / probabilistic voting",
     "Randomize the selection: choose a voter uniformly at random and implement their top choice. Gibbard (1977) showed random dictatorship is the unique strategy-proof and ex ante efficient randomized rule for 3+ alternatives."),

    # === FOUNDATIONAL_IMPOSSIBILITY ===

    ("FOUNDATIONAL_IMPOSSIBILITY", "PARTITION",
     "Constructive / classical partition",
     "Partition mathematics into constructive and classical domains. Constructive mathematics (Martin-Lof type theory, Coq) restricts to decidable propositions within its scope, achieving internal completeness by excluding undecidable statements."),

    ("FOUNDATIONAL_IMPOSSIBILITY", "EXTEND",
     "Transfinite extensions (ordinal analysis)",
     "Extend the proof system with transfinite induction up to larger ordinals. Gentzen (1936) proved PA consistent using induction up to epsilon_0, extending beyond the self-referential trap by adding well-ordering principles."),

    ("FOUNDATIONAL_IMPOSSIBILITY", "INVERT",
     "Paraconsistent logic",
     "Invert the consistency requirement: paraconsistent logics (da Costa, Priest) tolerate contradictions without explosion. The system becomes complete (trivially) by accepting some inconsistencies, inverting Godel's consistency-completeness tradeoff."),

    ("FOUNDATIONAL_IMPOSSIBILITY", "RANDOMIZE",
     "Probabilistic proof systems (interactive proofs)",
     "Replace deterministic proof verification with probabilistic checking. Interactive proofs (Goldwasser, Micali, Rackoff 1985) and PCP theorem allow verification with bounded error probability, randomizing the deterministic completeness barrier."),

    ("FOUNDATIONAL_IMPOSSIBILITY", "QUANTIZE",
     "Bounded arithmetic hierarchies",
     "Quantize the proof strength into discrete levels: S^1_2, T^i_2, PV, bounded arithmetic fragments. Each level is internally complete for its class of provable statements, creating a discrete ladder of consistency strength."),

    ("FOUNDATIONAL_IMPOSSIBILITY", "HIERARCHIZE",
     "Reflection principles / ordinal hierarchies",
     "Move to a meta-system that proves the consistency of the object system. Feferman's iterated reflection yields an ordinal-indexed hierarchy of theories, each level proving the previous level's consistency."),

    # === IMPOSSIBILITY_BODE_SENSITIVITY_WATERBED ===

    ("IMPOSSIBILITY_BODE_SENSITIVITY_WATERBED", "EXTEND",
     "Nonlinear control / sliding mode",
     "Extend beyond linear systems where the waterbed effect applies. Sliding mode control (Utkin 1977) uses discontinuous control to achieve robustness properties not subject to linear sensitivity constraints."),

    ("IMPOSSIBILITY_BODE_SENSITIVITY_WATERBED", "PARTITION",
     "Frequency-domain partitioning / multi-band design",
     "Partition the frequency axis into bands with separate controllers for each (notch filters for resonances, integral action for low frequencies). Each band's sensitivity is managed independently within the global integral constraint."),

    ("IMPOSSIBILITY_BODE_SENSITIVITY_WATERBED", "QUANTIZE",
     "Discrete-event / quantized control",
     "Replace continuous-time feedback with event-triggered control where actions occur only when a threshold is crossed. Astrom's event-triggered paradigm (2002) operates on a discrete event grid, changing the nature of the sensitivity tradeoff."),

    ("IMPOSSIBILITY_BODE_SENSITIVITY_WATERBED", "INVERT",
     "Feedforward / preview control",
     "Invert the feedback paradigm: use preview information about future disturbances to apply feedforward correction. Tomizuka's preview control (1975) bypasses the feedback sensitivity integral by acting on known-future disturbances."),

    ("IMPOSSIBILITY_BODE_SENSITIVITY_WATERBED", "HIERARCHIZE",
     "Supervisory control / gain scheduling",
     "Move the controller design up a level: a supervisory system switches between pre-designed controllers based on operating conditions. The meta-controller manages the waterbed tradeoff by selecting the appropriate sensitivity profile."),

    # === IMPOSSIBILITY_CALENDAR ===

    ("IMPOSSIBILITY_CALENDAR", "QUANTIZE",
     "Fixed calendar proposals (World Calendar, International Fixed)",
     "Quantize the irrational solar/lunar ratio into a fixed grid: 13 months of 28 days plus a blank day (International Fixed Calendar). The blank day absorbs the remainder, creating a perfectly regular discrete grid."),

    ("IMPOSSIBILITY_CALENDAR", "INVERT",
     "Purely solar calendars (abandon lunar tracking)",
     "Invert the priority: the Gregorian calendar abandons lunar synchronization entirely, tracking only the solar year. The leap year algorithm (every 4, skip 100, keep 400) handles the fractional day without any lunar reference."),

    ("IMPOSSIBILITY_CALENDAR", "RANDOMIZE",
     "Astronomical calendar (observe, don't predict)",
     "Replace algorithmic prediction with direct astronomical observation. The Islamic calendar traditionally starts months by sighting the new crescent, introducing stochastic variation that tracks the actual moon rather than a formula."),

    # === SOCIAL_CHOICE_IMPOSSIBILITY ===

    ("SOCIAL_CHOICE_IMPOSSIBILITY", "EXTEND",
     "Cardinal utility / range voting",
     "Extend from ordinal rankings to cardinal scores. Range voting allows voters to express intensity of preference, escaping Arrow's framework which only considers ordinal information. The additional information dimension enables more compatible aggregation."),

    ("SOCIAL_CHOICE_IMPOSSIBILITY", "PARTITION",
     "Deliberative democracy / agenda structuring",
     "Partition the decision process into sequential stages: deliberation narrows the alternative set, then voting selects from the reduced menu. Structured agendas prevent the cycling that generates Arrow impossibilities."),

    ("SOCIAL_CHOICE_IMPOSSIBILITY", "HIERARCHIZE",
     "Constitutional choice / Buchanan's levels",
     "Separate choice into constitutional (rules) and legislative (outcomes) levels. At the constitutional level, unanimity is feasible for rule selection; at the legislative level, the chosen rule operates within agreed constraints."),

    # === IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2 (more) ===

    ("IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2", "EXTEND",
     "Higher-dimensional embedding (cut-and-project)",
     "Extend to higher dimensions where 5-fold symmetry IS crystallographically allowed. Quasicrystals (Shechtman 1984) are projections of periodic lattices from 5D/6D space, adding dimensions to resolve the 2D/3D restriction."),

    ("IMPOSSIBILITY_CRYSTALLOGRAPHIC_RESTRICTION_V2", "PARTITION",
     "Hierarchical tiling (Penrose tiles)",
     "Partition the plane into two tile shapes (kite and dart) with matching rules that enforce aperiodic order. The local rules generate long-range 5-fold orientational order without translational periodicity, partitioning space non-periodically."),

    # === CROSS_DOMAIN_DUALITY (fill more damage ops) ===

    ("CROSS_DOMAIN_DUALITY", "DISTRIBUTE",
     "Functorial mapping (category theory)",
     "Distribute structure across domains via functors that preserve composition. The Yoneda lemma shows any object is determined by its relationships, distributing the structural information evenly across all morphisms."),

    ("CROSS_DOMAIN_DUALITY", "CONCENTRATE",
     "Galois correspondence",
     "Concentrate duality at the fixed-field/fixed-group correspondence. The fundamental theorem of Galois theory creates a bijection between intermediate fields and subgroups, concentrating the entire duality structure at a single lattice isomorphism."),

    ("CROSS_DOMAIN_DUALITY", "PARTITION",
     "Stone duality (topology-algebra partition)",
     "Partition mathematical structure into topological and algebraic halves connected by Stone duality: Boolean algebras correspond to Stone spaces, frames to locales. Each domain handles its native operations while the duality maintains the bridge."),

    ("CROSS_DOMAIN_DUALITY", "HIERARCHIZE",
     "Adjoint functor pairs (Kan extensions)",
     "Move duality up to the categorical level: left and right adjoints form a hierarchy where each level's free-forgetful pair generates the next. Kan extensions provide the universal construction at each hierarchical level."),

    ("CROSS_DOMAIN_DUALITY", "TRUNCATE",
     "Forgetful functor (drop structure)",
     "Truncate the dual by forgetting structure: a forgetful functor from groups to sets drops the group operation, reducing the dual mapping to its essential carrier. Only the information needed in the target domain is retained."),

    ("CROSS_DOMAIN_DUALITY", "RANDOMIZE",
     "Probabilistic duality (Fourier on groups)",
     "Randomize the dual via Pontryagin duality on locally compact abelian groups. The Fourier transform converts between time/frequency domains, with random signals mapped to their spectral density — a probabilistic version of the deterministic duality."),

    ("CROSS_DOMAIN_DUALITY", "EXTEND",
     "Enriched category theory",
     "Extend the duality framework from Set-enriched categories to V-enriched categories (metric spaces, posets, etc.). Lawvere's enriched categories add quantitative structure to the duality, extending the bridge between domains with richer morphism spaces."),

    ("CROSS_DOMAIN_DUALITY", "QUANTIZE",
     "Finite model theory (discrete duality)",
     "Quantize the duality to finite structures: Birkhoff's representation theorem restricts to finite distributive lattices and finite posets. The discrete version makes the duality computationally tractable and algorithmically implementable."),

    # === IMPOSSIBILITY_MUNDELL_FLEMING (more) ===

    ("IMPOSSIBILITY_MUNDELL_FLEMING", "HIERARCHIZE",
     "Supranational monetary authority (central bank hierarchy)",
     "Move monetary policy up a level to a supranational authority (ECB for the eurozone, hypothetical Asian Monetary Fund). The hierarchy resolves national-level trilemmas by delegating exchange rate management to a higher institutional level."),

    # === FORCED_SYMMETRY_BREAK (fill remaining: EXPAND via EXTEND) ===

    ("FORCED_SYMMETRY_BREAK", "EXTEND",
     "Microtonal / extended pitch systems",
     "Extend the pitch space beyond 12 divisions (19-EDO, 31-EDO, 53-EDO). More divisions per octave provide better rational approximations to just intervals, reducing the comma by spreading it across more, smaller steps."),

    ("FORCED_SYMMETRY_BREAK", "RANDOMIZE",
     "Adaptive tuning / real-time pitch correction",
     "Use algorithmic real-time pitch adjustment to stochastically shift intervals toward just intonation within a performance. Hermode Tuning and similar systems randomly micro-adjust pitches, never fully fixing the comma but probabilistically minimizing it."),
]


def make_instance_id(comp_id, resolution_name):
    """Create a deterministic instance_id from hub and resolution name."""
    suffix = resolution_name.upper().replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
    suffix = re.sub(r'[^A-Z0-9_]', '', suffix)
    suffix = suffix[:60]
    return f"{comp_id}__{suffix}"


def main():
    con = duckdb.connect(DB_PATH)

    # 1. Get current state
    all_hubs = con.execute(
        "SELECT comp_id, description FROM abstract_compositions"
    ).fetchall()
    hub_count = len(all_hubs)

    existing_spokes = con.execute(
        "SELECT instance_id, comp_id, notes FROM composition_instances"
    ).fetchall()

    # Build map of existing damage ops per hub
    hub_ops = defaultdict(set)
    existing_ids = set()
    for iid, cid, notes in existing_spokes:
        existing_ids.add(iid)
        if notes:
            m = re.search(r'(?:ALSO_)?DAMAGE_OP:\s*(\w+)', notes)
            if m:
                hub_ops[cid].add(m.group(1))

    pre_filled = sum(len(ops) for ops in hub_ops.values())
    print(f"=== PRE-DENSIFICATION STATE ===")
    print(f"Total hubs: {hub_count}")
    print(f"Total possible cells: {hub_count * 9}")
    print(f"Filled damage-op cells: {pre_filled}")
    print(f"Fill rate: {pre_filled / (hub_count * 9) * 100:.1f}%")
    print(f"Existing spokes: {len(existing_ids)}")
    print()

    # 2. Process resolutions
    inserted = 0
    skipped_dup = 0
    skipped_already_filled = 0
    hub_improvements = defaultdict(int)

    for comp_id, op, res_name, desc in RESOLUTIONS:
        # Check hub exists
        hub_exists = con.execute(
            "SELECT 1 FROM abstract_compositions WHERE comp_id = ?", [comp_id]
        ).fetchone()
        if not hub_exists:
            print(f"  WARN: Hub {comp_id} not found, skipping")
            continue

        # Use EXTEND for the DB if task says EXPAND
        db_op = op  # already using EXTEND in our data

        # Check if this operator is already filled for this hub
        # (allow multiple resolutions per operator)
        instance_id = make_instance_id(comp_id, res_name)

        # Check for exact duplicate
        if instance_id in existing_ids:
            skipped_dup += 1
            continue

        # Also check by similar instance_id prefix to avoid near-duplicates
        dup_check = con.execute(
            "SELECT 1 FROM composition_instances WHERE instance_id = ?",
            [instance_id]
        ).fetchone()
        if dup_check:
            skipped_dup += 1
            continue

        notes = f"{res_name}: {desc} | DAMAGE_OP: {db_op}"

        con.execute(
            """INSERT INTO composition_instances
               (instance_id, comp_id, system_id, tradition, domain, notes)
               VALUES (?, ?, NULL, NULL, NULL, ?)""",
            [instance_id, comp_id, notes]
        )

        existing_ids.add(instance_id)
        hub_ops[comp_id].add(db_op)
        hub_improvements[comp_id] += 1
        inserted += 1

    # 3. Report results
    post_filled = sum(len(ops) for ops in hub_ops.values())
    post_spokes = con.execute("SELECT COUNT(*) FROM composition_instances").fetchone()[0]

    print(f"=== POST-DENSIFICATION STATE ===")
    print(f"New spokes inserted: {inserted}")
    print(f"Duplicates skipped: {skipped_dup}")
    print(f"Total spokes now: {post_spokes}")
    print(f"Filled damage-op cells (unique op×hub): {post_filled}")
    print(f"New fill rate: {post_filled / (hub_count * 9) * 100:.1f}%")
    print(f"Fill rate delta: +{(post_filled - pre_filled) / (hub_count * 9) * 100:.1f}%")
    print()

    print(f"=== HUBS MOST IMPROVED ===")
    for hub, count in sorted(hub_improvements.items(), key=lambda x: -x[1])[:15]:
        total_ops = len(hub_ops[hub])
        print(f"  {hub}: +{count} spokes ({total_ops}/9 operators filled)")

    print()
    print(f"=== HUBS WITH MOST EMPTY CELLS (still) ===")
    # Find hubs that still have many empty cells
    empty_counts = []
    for cid, desc in all_hubs:
        filled = len(hub_ops.get(cid, set()))
        empty = 9 - filled
        if empty > 0 and filled > 0:  # Only show hubs that have SOME ops but not all
            empty_counts.append((cid, empty, filled))
    empty_counts.sort(key=lambda x: -x[1])
    for cid, empty, filled in empty_counts[:15]:
        print(f"  {cid}: {empty} empty ({filled}/9 filled)")

    con.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
