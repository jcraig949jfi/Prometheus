# Mathematical Libraries Mapped to Prometheus Concepts

*What already exists in pip-installable Python packages that can be extracted into concept organisms*

---

## The Principle

Don't implement the math from scratch. The Python ecosystem already has mature, tested, numpy-compatible libraries for nearly every field in the 95-concept dictionary. Extract the functions, pack them into organisms, let the composition engine chain them.

**Total estimated coverage: ~80 of 95 concepts have existing library implementations.**

---

## Tier 1: Already Installed or One `pip install` Away

These are mature, lightweight, numpy-compatible. Most work on CPU. Each entry lists the concept, the library, and the specific functions to extract.

### Mathematics / Linear Algebra

| Concept | Library | Key Functions | Install |
|---------|---------|--------------|---------|
| **Tensor Decomposition** | `tensorly` | `tucker()`, `parafac()`, `tensor_train()`, `non_negative_tucker()` | `pip install tensorly` |
| **Category Theory** | `catgrad` or manual | Functors as function composition, morphism chaining | Manual (compose pattern) |
| **Measure Theory** | `scipy.integrate` | `quad()`, `dblquad()`, Lebesgue-like integration | Already installed |
| **Fourier Transforms** | `numpy.fft` | `fft()`, `rfft()`, `fftfreq()`, spectral analysis | Already installed |
| **Wavelet Transforms** | `pywt` | `wavedec()`, `cwt()`, multi-resolution analysis | `pip install PyWavelets` |
| **Compressed Sensing** | `scipy.optimize` | `linprog()` for L1 minimization, `lasso_path()` from sklearn | Already installed |
| **Sparse Autoencoders** | `saelens` or manual | Encode/decode with sparsity penalty | Manual (numpy only) |

### Dynamical Systems / Chaos / Complexity

| Concept | Library | Key Functions | Install |
|---------|---------|--------------|---------|
| **Chaos Theory** | `numpy` | Logistic map, Lorenz system, Lyapunov exponent computation | Already installed |
| **Ergodic Theory** | `numpy` | Time-average vs ensemble-average, mixing time estimation | Manual (straightforward) |
| **Dynamical Systems** | `scipy.integrate` | `solve_ivp()`, phase portraits, fixed point analysis | Already installed |
| **Phase Transitions** | `numpy` | Ising model, order parameter computation, susceptibility | Manual |
| **Criticality / SOC** | `numpy` | Sandpile model, avalanche size distribution, power law fit | Manual + `powerlaw` pip |
| **Fractal Geometry** | `numpy` | Box-counting dimension, Hausdorff dimension approximation | Manual |
| **Cellular Automata** | `numpy` | Rule tables, elementary CA, Game of Life | Manual (trivial in numpy) |

### Information Theory / Coding

| Concept | Library | Key Functions | Install |
|---------|---------|--------------|---------|
| **Information Theory** | `scipy.stats` | `entropy()`, mutual information via KL divergence | Already installed |
| **Kolmogorov Complexity** | `zlib` | `len(zlib.compress(x))` as approximation | Already installed |
| **Error Correcting Codes** | `galois` | Hamming codes, Reed-Solomon, syndrome decoding | `pip install galois` |
| **Compressed Sensing** | `sklearn.linear_model` | `Lasso()`, `OrthogonalMatchingPursuit()` | Already installed |

### Probability / Statistics / Bayesian

| Concept | Library | Key Functions | Install |
|---------|---------|--------------|---------|
| **Bayesian Inference** | `scipy.stats` | `bayes_mvs()`, prior/posterior computation, conjugate priors | Already installed |
| **Monte Carlo / MCMC** | `numpy.random` | Metropolis-Hastings, importance sampling | Manual (standard algorithms) |
| **Multi-Armed Bandits** | `numpy` | UCB1, Thompson sampling, epsilon-greedy | Manual (10-line implementations) |
| **Causal Inference** | `causal-learn` | PC algorithm, FCI, NOTEARS, LiNGAM | `pip install causal-learn` |
| **Statistical Mechanics** | `numpy` | Partition function, Boltzmann distribution, free energy | Manual |

### Optimization / Control / Game Theory

| Concept | Library | Key Functions | Install |
|---------|---------|--------------|---------|
| **Optimal Control** | `scipy.optimize` | `minimize()`, `differential_evolution()`, Pontryagin principle | Already installed |
| **Feedback Control** | `scipy.signal` | `lti()`, PID controller, Bode plots, transfer functions | Already installed |
| **Mechanism Design** | `numpy` | Auction theory (Vickrey), incentive compatibility checks | Manual |
| **Nash Equilibrium** | `scipy.optimize` | `linprog()` for zero-sum games, support enumeration | Manual + scipy |
| **Reinforcement Learning** | `numpy` | Q-learning, policy gradient, value iteration | Manual |
| **Genetic Algorithms** | `numpy` | Selection, crossover, mutation operators | Manual (or `deap`) |
| **Constraint Satisfaction** | `numpy` | Arc consistency, backtracking, constraint propagation | Manual |

### Signal Processing / Spectral

| Concept | Library | Key Functions | Install |
|---------|---------|--------------|---------|
| **Spectral Analysis** | `scipy.signal` | `welch()`, `periodogram()`, eigenvalue decomposition | Already installed |
| **Kalman Filtering** | `filterpy` | `KalmanFilter()`, predict/update cycle, smoother | `pip install filterpy` |
| **Matched Filtering** | `scipy.signal` | `correlate()`, template matching, SNR computation | Already installed |

### Network Science / Graph Theory

| Concept | Library | Key Functions | Install |
|---------|---------|--------------|---------|
| **Network Science** | `networkx` | Centrality, clustering, community detection, shortest path | `pip install networkx` |
| **Graph Theory** | `networkx` + `numpy` | Adjacency spectrum, Laplacian, graph kernels | Already available |

### Biology / Neuroscience / Cognitive Science

| Concept | Library | Key Functions | Install |
|---------|---------|--------------|---------|
| **Neural Oscillations** | `scipy.signal` | `hilbert()` (analytic signal), bandpass, phase-amplitude coupling | Already installed |
| **Neural Plasticity / Hebbian** | `numpy` | Oja's rule, STDP, weight update rules | Manual (5-line implementations) |
| **Neuromodulation** | `numpy` | Dopamine-like gain modulation, reward prediction error | Manual |
| **Reservoir Computing** | `numpy` | Echo state network, spectral radius tuning, readout training | Manual (~50 lines) |
| **Predictive Coding** | `numpy` | Prediction error minimization, hierarchical message passing | Manual |
| **Active Inference** | `numpy` | Free energy minimization, expected free energy, belief updating | Manual (~100 lines) |
| **Gene Regulatory Networks** | `numpy` | Boolean networks, ODE models, Hill functions | Manual |
| **Immune Systems** | `numpy` | Clonal selection, negative selection, danger model | Manual |
| **Ecosystem Dynamics** | `scipy.integrate` | Lotka-Volterra, replicator dynamics, competition models | Already installed |
| **Morphogenesis** | `numpy` | Turing patterns, reaction-diffusion (Gray-Scott) | Manual |
| **Apoptosis** | `numpy` | Threshold-based pruning, fitness-gated elimination | Manual (trivial) |

### Physics

| Concept | Library | Key Functions | Install |
|---------|---------|--------------|---------|
| **Thermodynamics** | `numpy` | Partition function, Boltzmann, entropy, free energy | Manual |
| **Renormalization** | `numpy` | Block spin, coarse-graining, RG flow | Manual |
| **Holography Principle** | `numpy` | Area-entropy bounds, bulk-boundary correspondence | Manual (conceptual) |
| **Gauge Theory** | `numpy` | Lattice gauge theory basics, Wilson loops | Manual (advanced) |

### Philosophy / Logic / Linguistics

| Concept | Library | Key Functions | Install |
|---------|---------|--------------|---------|
| **Falsificationism** | Manual | Counterexample search, modus tollens application | Pattern-based |
| **Dialectics** | Manual | Thesis-antithesis-synthesis scoring | Pattern-based |
| **Epistemology** | Manual | Evidence accumulation, belief revision (Jeffrey conditioning) | Bayesian framework |
| **Pragmatics** | Manual | Gricean maxims (quantity, quality, relevance, manner) | Regex + rules |
| **Phenomenology** | Manual | Bracketing, intentionality detection | Pattern-based |
| **Theory of Mind** | Manual | Belief attribution, false belief detection | State machine |
| **Metacognition** | Manual | Confidence calibration, uncertainty detection | Already in forge tools |
| **Analogical Reasoning** | Manual | Structure mapping, relational similarity | Pattern + graph |
| **Abductive Reasoning** | Manual | Inference to best explanation, hypothesis ranking | Bayesian model selection |
| **Type Theory** | Manual | Type checking, type inference, dependent types | Pattern-based |
| **Model Checking** | Manual | State space exploration, CTL/LTL properties | Graph traversal |
| **Program Synthesis** | Manual | Enumerative search, constraint-guided generation | Search algorithms |

---

## Tier 2: Heavier Libraries (Worth Installing for Depth)

| Library | Concepts Covered | Size | Install |
|---------|-----------------|------|---------|
| `networkx` | Network Science, Graph Theory, Community Detection | 5MB | `pip install networkx` |
| `PyWavelets` | Wavelet Transforms, Multi-Resolution Analysis | 3MB | `pip install PyWavelets` |
| `filterpy` | Kalman Filtering, Bayesian Estimation | 1MB | `pip install filterpy` |
| `galois` | Error Correcting Codes, Finite Fields | 2MB | `pip install galois` |
| `powerlaw` | Criticality, Scale-Free Detection | 1MB | `pip install powerlaw` |
| `causal-learn` | Causal Inference (PC, FCI, NOTEARS, LiNGAM) | 10MB | Already installed |
| `deap` | Genetic Algorithms, GP, Multi-Objective | 3MB | `pip install deap` |
| `sympy` | Symbolic Math, Algebra, Calculus, Logic | 15MB | `pip install sympy` |

**Total install footprint: ~40MB for full coverage.**

---

## The Extraction Pattern

For each library, the extraction is mechanical:

```python
# Step 1: Import the library function
from scipy.stats import entropy as scipy_entropy

# Step 2: Wrap it in the organism interface
INFORMATION_THEORY = MathematicalOrganism(
    name="information_theory",
    operations={
        "shannon_entropy": {
            "code": """
def shannon_entropy(distribution):
    import numpy as np
    p = np.array(distribution, dtype=float)
    p = p[p > 0]  # Remove zeros
    p = p / p.sum()  # Normalize
    return -np.sum(p * np.log2(p))
""",
            "input_type": "probability_distribution",
            "output_type": "scalar",
        },
        "mutual_information": {
            "code": """
def mutual_information(joint_distribution):
    import numpy as np
    pxy = np.array(joint_distribution, dtype=float)
    pxy = pxy / pxy.sum()
    px = pxy.sum(axis=1)
    py = pxy.sum(axis=0)
    mi = 0.0
    for i in range(pxy.shape[0]):
        for j in range(pxy.shape[1]):
            if pxy[i,j] > 0:
                mi += pxy[i,j] * np.log2(pxy[i,j] / (px[i] * py[j]))
    return mi
""",
            "input_type": "joint_distribution",
            "output_type": "scalar",
        },
        "kl_divergence": {
            "code": """
def kl_divergence(p, q):
    import numpy as np
    p, q = np.array(p, dtype=float), np.array(q, dtype=float)
    mask = (p > 0) & (q > 0)
    return np.sum(p[mask] * np.log2(p[mask] / q[mask]))
""",
            "input_type": "distribution_pair",
            "output_type": "scalar",
        },
    }
)
```

**Time per concept: 15-30 minutes** (find the library, identify 3-5 key functions, wrap in organism interface, test).

**Time for all 95 concepts: ~40-50 hours** spread across sessions. Or parallelize with Claude Code instances — 5 instances × 19 concepts each = done in a day.

---

## What's NOT in Libraries (The Manual 15%)

These concepts need custom implementations because they're either too abstract or too cross-disciplinary for any single library:

1. **Autopoiesis** — self-reproducing systems (implement as a cellular automaton that maintains its own boundary)
2. **Global Workspace Theory** — consciousness model (implement as a broadcast/compete architecture)
3. **Dual Process Theory** — System 1/System 2 (implement as fast heuristic + slow deliberative scoring)
4. **Embodied Cognition** — grounded reasoning (implement as sensorimotor state tracking)
5. **Compositionality** — semantic composition (implement as recursive tree evaluation)
6. **Emergence** — macro from micro (implement as coarse-graining + measure of novel properties)
7. **Swarm Intelligence** — collective computation (implement as particle swarm optimization)
8. **Cognitive Load Theory** — working memory limits (implement as buffer with overflow)
9. **Attention Mechanisms** — selective processing (implement as softmax-weighted aggregation)

But even these are 20-50 lines of numpy each. They're not hard — they're just not in a pip package.

---

## The Bootstrap Plan

### Day 1: Install + Extract Tier 1 (what's already there)

```bash
pip install tensorly PyWavelets filterpy galois powerlaw networkx deap sympy
```

Then extract organisms from:
- `numpy` / `scipy`: ~30 concepts (already installed, just wrap functions)
- `networkx`: ~5 concepts
- `tensorly`: ~3 concepts
- Existing forge tools: ~20 concepts (the v4 library has numpy implementations of SVD, DFT, eigenvalues, Kalman, MCMC, etc.)

**Result: ~58 concept organisms populated with real math in one day.**

### Day 2: Manual Implementations for Tier 2

- The 15 manual concepts: 20-50 lines each, ~4 hours total
- The biology/neuroscience concepts: mostly numpy implementations of standard algorithms
- The philosophy/logic concepts: pattern-based, similar to existing forge tools

**Result: ~80 concept organisms. 85% coverage.**

### Day 3: Composition Engine + First Test

- Build the type-compatible chaining engine
- Run all valid chains on test data
- Score by: does it execute? Does it produce non-trivial output? Does it produce output different from either input alone?
- First results: how many of the ~50M possible 3-chains actually run?

### Day 4+: Self-Evaluation Loop

- Wire exploration velocity metric
- Let it keep what makes it faster
- Let it name what it can't explain
- Watch

---

## Storage: Every Result Has Value

Even a 0.00007 score gets stored. The intersectional vector database:

```python
# Every composition result, regardless of score
results_db.insert({
    "chain": "topology.betti → immune.danger_signal → chaos.lyapunov",
    "score": 0.00007,
    "output_type": "scalar",
    "output_hash": hash(output),
    "execution_time_us": 340,
    "novel_properties": [],
    "timestamp": now(),
})

# Later, when a NEW concept is added, re-score stored low-scorers
# A 0.00007 might become 0.45 in the context of a new concept
# that creates the right bridge
```

Nothing is truly zero. The Lattice remembers everything. Some nodes are dormant until the right neighbor activates them.
