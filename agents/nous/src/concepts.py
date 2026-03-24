"""
Concept dictionary for the Nous combinatorial hypothesis engine.

80-100 concepts from diverse fields, each with name, field, and short description.
"""

CONCEPTS = [
    # === Mathematics ===
    {"name": "Topology", "field": "Mathematics", "short_description": "Study of properties preserved under continuous deformations; connectedness, holes, and invariants."},
    {"name": "Category Theory", "field": "Mathematics", "short_description": "Abstract algebra of mappings between structures; functors, natural transformations, universal properties."},
    {"name": "Fourier Transforms", "field": "Mathematics", "short_description": "Decomposition of signals into constituent frequencies; bridges time/space and frequency domains."},
    {"name": "Prime Number Theory", "field": "Mathematics", "short_description": "Distribution and structure of primes; Riemann zeta function, prime gaps, multiplicative number theory."},
    {"name": "Fractal Geometry", "field": "Mathematics", "short_description": "Self-similar structures at every scale; Hausdorff dimension, iterated function systems, power-law scaling."},
    {"name": "Tensor Decomposition", "field": "Mathematics", "short_description": "Factoring multi-dimensional arrays into simpler components; CP, Tucker, and tensor train formats."},
    {"name": "Ergodic Theory", "field": "Mathematics", "short_description": "Long-term statistical behavior of dynamical systems; time averages converge to space averages."},
    {"name": "Information Theory", "field": "Mathematics", "short_description": "Quantification of information, entropy, and channel capacity; Shannon entropy, mutual information, KL divergence."},
    {"name": "Bayesian Inference", "field": "Mathematics", "short_description": "Updating beliefs with evidence via Bayes' theorem; prior/posterior distributions, conjugate priors, MCMC."},
    {"name": "Graph Theory", "field": "Mathematics", "short_description": "Study of networks as nodes and edges; connectivity, flows, spectral properties, random graphs."},
    {"name": "Measure Theory", "field": "Mathematics", "short_description": "Rigorous foundation for integration and probability; sigma-algebras, Lebesgue measure, convergence theorems."},
    {"name": "Dynamical Systems", "field": "Mathematics", "short_description": "Evolution of state over time via deterministic rules; attractors, bifurcations, Lyapunov exponents."},

    # === Physics ===
    {"name": "Chaos Theory", "field": "Physics", "short_description": "Sensitive dependence on initial conditions in deterministic systems; strange attractors, Lyapunov exponents."},
    {"name": "Thermodynamics", "field": "Physics", "short_description": "Energy, entropy, and equilibrium; laws governing heat transfer and the arrow of time."},
    {"name": "Quantum Mechanics", "field": "Physics", "short_description": "Superposition, entanglement, and measurement; wave functions, operators, decoherence."},
    {"name": "Phase Transitions", "field": "Physics", "short_description": "Abrupt qualitative changes in system behavior at critical parameters; universality classes, order parameters."},
    {"name": "Renormalization", "field": "Physics", "short_description": "Scale-dependent description of physical systems; coarse-graining, fixed points, universality."},
    {"name": "Statistical Mechanics", "field": "Physics", "short_description": "Macroscopic properties from microscopic constituents; partition functions, ensembles, fluctuation-dissipation."},
    {"name": "Gauge Theory", "field": "Physics", "short_description": "Symmetry-based framework for fundamental forces; local invariance, connections, fiber bundles."},
    {"name": "Holography Principle", "field": "Physics", "short_description": "Bulk information encoded on boundary; AdS/CFT correspondence, information density bounds."},

    # === Computer Science ===
    {"name": "Reservoir Computing", "field": "Computer Science", "short_description": "Fixed random recurrent network with trainable readout; echo state networks, liquid state machines."},
    {"name": "Genetic Algorithms", "field": "Computer Science", "short_description": "Optimization via selection, crossover, and mutation on candidate populations; fitness landscapes."},
    {"name": "Neural Architecture Search", "field": "Computer Science", "short_description": "Automated discovery of optimal network topologies; search spaces, performance predictors, weight sharing."},
    {"name": "Attention Mechanisms", "field": "Computer Science", "short_description": "Dynamic weighting of input elements by relevance; self-attention, cross-attention, multi-head attention."},
    {"name": "Sparse Autoencoders", "field": "Computer Science", "short_description": "Learning compressed representations with sparsity constraints; feature disentanglement, dictionary learning."},
    {"name": "Reinforcement Learning", "field": "Computer Science", "short_description": "Learning optimal actions via reward signals; policy gradients, Q-learning, exploration-exploitation tradeoff."},
    {"name": "Monte Carlo Tree Search", "field": "Computer Science", "short_description": "Tree search guided by random rollouts; UCB selection, expansion, backpropagation of value estimates."},
    {"name": "Compressed Sensing", "field": "Computer Science", "short_description": "Recovering sparse signals from far fewer measurements than Nyquist; RIP, basis pursuit, L1 minimization."},
    {"name": "Program Synthesis", "field": "Computer Science", "short_description": "Automatic generation of programs from specifications; constraint solving, neural-guided search, type-directed."},
    {"name": "Cellular Automata", "field": "Computer Science", "short_description": "Discrete computational systems with local rules generating complex global behavior; Rule 110, Game of Life."},
    {"name": "Constraint Satisfaction", "field": "Computer Science", "short_description": "Finding assignments that satisfy all constraints; backtracking, arc consistency, SAT solvers."},
    {"name": "Differentiable Programming", "field": "Computer Science", "short_description": "End-to-end gradient-based optimization of arbitrary programs; autodiff, neural ODEs, soft relaxations."},

    # === Biology ===
    {"name": "Evolution", "field": "Biology", "short_description": "Descent with modification via natural selection; fitness landscapes, speciation, genetic drift."},
    {"name": "Immune Systems", "field": "Biology", "short_description": "Adaptive defense via clonal selection and memory; antibody diversity, self/non-self discrimination."},
    {"name": "Neural Plasticity", "field": "Biology", "short_description": "Experience-dependent reorganization of neural circuits; Hebbian learning, synaptic pruning, critical periods."},
    {"name": "Gene Regulatory Networks", "field": "Biology", "short_description": "Interconnected gene expression controls; promoters, transcription factors, feedback loops, attractors."},
    {"name": "Symbiosis", "field": "Biology", "short_description": "Long-term interspecies interaction with mutual benefit; mutualism, endosymbiosis, holobiont theory."},
    {"name": "Ecosystem Dynamics", "field": "Biology", "short_description": "Energy flows, trophic cascades, and succession in ecological communities; resilience, keystone species."},
    {"name": "Morphogenesis", "field": "Biology", "short_description": "Self-organized pattern formation in development; Turing patterns, morphogen gradients, reaction-diffusion."},
    {"name": "Epigenetics", "field": "Biology", "short_description": "Heritable gene expression changes without DNA sequence alteration; methylation, histone modification, chromatin states."},
    {"name": "Swarm Intelligence", "field": "Biology", "short_description": "Collective behavior from simple agents without central control; ant colony optimization, flocking, stigmergy."},
    {"name": "Apoptosis", "field": "Biology", "short_description": "Programmed cell death for organism-level benefit; caspase cascades, quality control, developmental sculpting."},

    # === Cognitive Science ===
    {"name": "Dual Process Theory", "field": "Cognitive Science", "short_description": "Two systems of thought: fast intuitive (System 1) and slow deliberate (System 2); cognitive biases."},
    {"name": "Metacognition", "field": "Cognitive Science", "short_description": "Thinking about thinking; confidence calibration, error monitoring, strategy selection."},
    {"name": "Embodied Cognition", "field": "Cognitive Science", "short_description": "Cognition shaped by body-environment interaction; sensorimotor grounding, affordances, enactivism."},
    {"name": "Predictive Coding", "field": "Cognitive Science", "short_description": "Brain as prediction engine minimizing surprise; prediction errors, hierarchical generative models."},
    {"name": "Active Inference", "field": "Cognitive Science", "short_description": "Action and perception unified under free energy minimization; expected free energy, epistemic foraging."},
    {"name": "Global Workspace Theory", "field": "Cognitive Science", "short_description": "Consciousness as global broadcast of selected information; competition, ignition, widespread access."},
    {"name": "Analogical Reasoning", "field": "Cognitive Science", "short_description": "Transfer of relational structure between domains; structure mapping, far transfer, abstraction."},
    {"name": "Cognitive Load Theory", "field": "Cognitive Science", "short_description": "Limited working memory constrains learning; intrinsic, extraneous, and germane load; chunking."},
    {"name": "Theory of Mind", "field": "Cognitive Science", "short_description": "Modeling other agents' beliefs, desires, and intentions; false-belief tasks, recursive mentalizing."},

    # === Signal Processing ===
    {"name": "Wavelet Transforms", "field": "Signal Processing", "short_description": "Multi-resolution time-frequency analysis; localized basis functions, multiresolution analysis, denoising."},
    {"name": "Spectral Analysis", "field": "Signal Processing", "short_description": "Frequency-domain characterization of signals; power spectral density, periodograms, spectral leakage."},
    {"name": "Kalman Filtering", "field": "Signal Processing", "short_description": "Optimal recursive state estimation under noise; prediction-update cycle, Gaussian state space models."},
    {"name": "Matched Filtering", "field": "Signal Processing", "short_description": "Optimal detection of known signal in noise; cross-correlation, signal-to-noise ratio maximization."},

    # === Philosophy ===
    {"name": "Epistemology", "field": "Philosophy", "short_description": "Study of knowledge, justification, and belief; foundationalism, coherentism, reliabilism."},
    {"name": "Falsificationism", "field": "Philosophy", "short_description": "Science advances by attempting to disprove hypotheses; Popper's demarcation criterion, bold conjectures."},
    {"name": "Pragmatism", "field": "Philosophy", "short_description": "Truth as what works in practice; Peirce, James, Dewey; inquiry as self-correcting process."},
    {"name": "Phenomenology", "field": "Philosophy", "short_description": "First-person study of conscious experience and its structures; intentionality, bracketing, lifeworld."},
    {"name": "Dialectics", "field": "Philosophy", "short_description": "Progress through thesis-antithesis-synthesis; contradictions as engines of development; Hegel, Marx."},
    {"name": "Abductive Reasoning", "field": "Philosophy", "short_description": "Inference to best explanation from incomplete data; hypothesis generation, explanatory virtues."},

    # === Complex Systems ===
    {"name": "Self-Organized Criticality", "field": "Complex Systems", "short_description": "Systems naturally evolve to critical states with power-law avalanches; sandpile models, 1/f noise."},
    {"name": "Emergence", "field": "Complex Systems", "short_description": "Macro-level properties not reducible to micro-level components; weak vs strong emergence, downward causation."},
    {"name": "Network Science", "field": "Complex Systems", "short_description": "Structure and dynamics of complex networks; small-world, scale-free, community detection, cascades."},
    {"name": "Autopoiesis", "field": "Complex Systems", "short_description": "Self-producing systems that maintain their own organization; Maturana and Varela, organizational closure."},
    {"name": "Criticality", "field": "Complex Systems", "short_description": "Systems poised at boundary between order and disorder; maximal correlation length, susceptibility divergence."},

    # === Information Science ===
    {"name": "Kolmogorov Complexity", "field": "Information Science", "short_description": "Minimum description length of an object; algorithmic randomness, incompressibility, MDL principle."},
    {"name": "Error Correcting Codes", "field": "Information Science", "short_description": "Redundancy-based protection against noise; Hamming distance, Reed-Solomon, LDPC, turbo codes."},
    {"name": "Causal Inference", "field": "Information Science", "short_description": "Determining cause-effect from data; do-calculus, DAGs, interventions, counterfactuals, Pearl's framework."},

    # === Neuroscience ===
    {"name": "Hebbian Learning", "field": "Neuroscience", "short_description": "Neurons that fire together wire together; activity-dependent synaptic strengthening, LTP/LTD."},
    {"name": "Neural Oscillations", "field": "Neuroscience", "short_description": "Rhythmic brain activity at multiple frequencies; gamma binding, theta sequences, cross-frequency coupling."},
    {"name": "Neuromodulation", "field": "Neuroscience", "short_description": "Chemical signals that alter neural circuit dynamics; dopamine, serotonin, gain control, state-dependent processing."},
    {"name": "Sparse Coding", "field": "Neuroscience", "short_description": "Neural representations using few active neurons; energy efficiency, pattern separation, Olshausen-Field model."},

    # === Control Theory ===
    {"name": "Feedback Control", "field": "Control Theory", "short_description": "Using output error to adjust input; PID controllers, stability margins, Bode plots, Nyquist criterion."},
    {"name": "Optimal Control", "field": "Control Theory", "short_description": "Minimizing cost over trajectories; Pontryagin's principle, Hamilton-Jacobi-Bellman, LQR."},
    {"name": "Adaptive Control", "field": "Control Theory", "short_description": "Controllers that adjust parameters online to handle uncertainty; model reference, self-tuning regulators."},

    # === Linguistics ===
    {"name": "Compositionality", "field": "Linguistics", "short_description": "Meaning of whole determined by meaning of parts and combination rules; Frege's principle, syntax-semantics interface."},
    {"name": "Pragmatics", "field": "Linguistics", "short_description": "Context-dependent meaning beyond literal semantics; implicature, speech acts, Grice's maxims."},

    # === Economics / Game Theory ===
    {"name": "Mechanism Design", "field": "Economics", "short_description": "Engineering rules to achieve desired outcomes with self-interested agents; auctions, incentive compatibility."},
    {"name": "Nash Equilibrium", "field": "Game Theory", "short_description": "Stable strategy profiles where no agent benefits from unilateral deviation; mixed strategies, coordination games."},
    {"name": "Multi-Armed Bandits", "field": "Game Theory", "short_description": "Sequential decision-making under uncertainty; explore-exploit tradeoff, UCB, Thompson sampling."},

    # === Thermodynamics / Statistical Physics ===
    {"name": "Free Energy Principle", "field": "Theoretical Neuroscience", "short_description": "Biological systems minimize variational free energy; prediction error minimization, Markov blankets."},
    {"name": "Maximum Entropy", "field": "Statistical Physics", "short_description": "Least biased inference consistent with constraints; Jaynes' principle, exponential families, log-linear models."},

    # === Logic / Formal Methods ===
    {"name": "Type Theory", "field": "Logic", "short_description": "Formal system where types classify terms; dependent types, Curry-Howard correspondence, proof assistants."},
    {"name": "Model Checking", "field": "Formal Methods", "short_description": "Exhaustive verification of finite-state systems against specifications; temporal logic, state space exploration."},
]

# Validate
assert len(CONCEPTS) >= 80, f"Expected >=80 concepts, got {len(CONCEPTS)}"

# Field summary
def get_field_counts():
    from collections import Counter
    return Counter(c["field"] for c in CONCEPTS)

if __name__ == "__main__":
    print(f"Total concepts: {len(CONCEPTS)}")
    for field, count in sorted(get_field_counts().items()):
        print(f"  {field}: {count}")
