# Mathematical Organisms — Living Concept Tensors

*Pack concepts with real math. Compose them. Test if the composition makes the system better. Keep what works. The system builds its own toolkit.*

---

## The Shift

The tensor explorer MVP encodes concepts as feature vectors — `boundary_sensitivity: 0.95`. That's metadata about math. It's not math.

The real version encodes each concept as a **mathematical object**: the actual formulas, algorithms, geometric operations, and runnable Python code from the field. When three concepts intersect, you're not computing a score — you're composing actual mathematical operations and testing whether the composition produces useful structure.

---

## What a Concept Tensor Actually Contains

### Example: Topology

```python
TOPOLOGY = MathematicalOrganism(
    name="topology",
    field="mathematics",

    # The actual operations, not descriptions of them
    operations={
        "betti_numbers": {
            "code": """
def betti_numbers(adjacency_matrix):
    '''Compute Betti numbers from a simplicial complex.'''
    import numpy as np
    # Boundary operator from adjacency
    n = adjacency_matrix.shape[0]
    edges = list(zip(*np.where(np.triu(adjacency_matrix, 1) > 0)))
    if not edges:
        return [n, 0]
    # B1 boundary matrix: edges → vertices
    B1 = np.zeros((n, len(edges)))
    for j, (u, v) in enumerate(edges):
        B1[u, j] = 1
        B1[v, j] = -1
    rank_B1 = np.linalg.matrix_rank(B1)
    beta_0 = n - rank_B1          # connected components
    beta_1 = len(edges) - rank_B1  # independent cycles (approximate)
    return [beta_0, beta_1]
""",
            "input_type": "adjacency_matrix",
            "output_type": "invariant_vector",
            "properties": ["scale_invariant", "deformation_invariant"],
        },
        "persistent_homology": {
            "code": """
def persistent_homology(distance_matrix, max_dim=1):
    '''Filtration-based topological feature extraction.'''
    import numpy as np
    n = distance_matrix.shape[0]
    thresholds = np.sort(np.unique(distance_matrix.flatten()))
    births_deaths = []
    prev_components = n
    for t in thresholds:
        adj = (distance_matrix <= t).astype(int)
        np.fill_diagonal(adj, 0)
        # Count connected components via eigenvalue
        laplacian = np.diag(adj.sum(axis=1)) - adj
        eigvals = np.sort(np.linalg.eigvalsh(laplacian))
        components = int(np.sum(eigvals < 1e-10))
        if components < prev_components:
            births_deaths.append(('merge', t, prev_components - components))
        prev_components = components
    return births_deaths
""",
            "input_type": "distance_matrix",
            "output_type": "persistence_diagram",
            "properties": ["multi_scale", "noise_robust"],
        },
        "euler_characteristic": {
            "code": """
def euler_characteristic(vertices, edges, faces=0):
    return vertices - edges + faces
""",
            "input_type": "simplicial_counts",
            "output_type": "scalar_invariant",
            "properties": ["additive", "fast"],
        },
    },

    # How this concept transforms data
    transforms={
        "any_to_graph": "Convert input to adjacency matrix (prerequisite for Betti)",
        "distance_to_persistence": "Convert pairwise distances to persistence diagram",
        "graph_to_invariant": "Extract topological invariants from graph structure",
    },

    # Type signature: what it eats and what it produces
    input_types=["adjacency_matrix", "distance_matrix", "point_cloud", "simplicial_complex"],
    output_types=["invariant_vector", "persistence_diagram", "scalar_invariant", "boolean"],
)
```

### Example: Immune Systems

```python
IMMUNE_SYSTEMS = MathematicalOrganism(
    name="immune_systems",
    field="biology_computational",

    operations={
        "clonal_selection": {
            "code": """
def clonal_selection(antibodies, antigen, mutation_rate=0.1, n_clones=5):
    '''Select and mutate best-matching antibodies.'''
    import numpy as np
    # Affinity = inverse distance
    affinities = np.array([1.0 / (1.0 + np.linalg.norm(ab - antigen)) for ab in antibodies])
    # Select top performers
    top_idx = np.argsort(affinities)[-n_clones:]
    clones = []
    for idx in top_idx:
        for _ in range(int(affinities[idx] * 10)):  # more clones for better match
            mutant = antibodies[idx] + np.random.randn(*antibodies[idx].shape) * mutation_rate / affinities[idx]
            clones.append(mutant)
    return np.array(clones) if clones else antibodies
""",
            "input_type": "population_vector",
            "output_type": "population_vector",
            "properties": ["adaptive", "stochastic", "self_improving"],
        },
        "self_nonself_discrimination": {
            "code": """
def self_nonself(candidate, self_repertoire, threshold=0.3):
    '''Classify candidate as self or non-self based on distance to known self.'''
    import numpy as np
    if len(self_repertoire) == 0:
        return 'unknown', 1.0
    distances = [np.linalg.norm(candidate - s) for s in self_repertoire]
    min_dist = min(distances)
    if min_dist < threshold:
        return 'self', 1.0 - min_dist / threshold
    return 'nonself', min_dist / (min_dist + threshold)
""",
            "input_type": "vector",
            "output_type": "classification",
            "properties": ["boundary_detection", "adaptive_threshold"],
        },
        "danger_signal": {
            "code": """
def danger_signal(observations, baseline_stats, z_threshold=2.5):
    '''Detect anomalous patterns that deviate from baseline.'''
    import numpy as np
    mean, std = baseline_stats
    z_scores = np.abs((observations - mean) / (std + 1e-8))
    danger = np.any(z_scores > z_threshold)
    max_z = float(np.max(z_scores))
    return danger, max_z, int(np.argmax(z_scores))
""",
            "input_type": "observation_vector",
            "output_type": "anomaly_detection",
            "properties": ["unsupervised", "threshold_adaptive"],
        },
    },

    input_types=["population_vector", "vector", "observation_vector"],
    output_types=["population_vector", "classification", "anomaly_detection"],
)
```

---

## Composition: Where the Magic Happens

When two concepts are composed, their operations are **chained by type compatibility**. Topology outputs a `distance_matrix` → Immune Systems accepts a `vector`. If there's a transform between them, they compose.

```python
def compose(organism_a, organism_b, organism_c, input_data):
    """
    Try all valid operation chains across three organisms.
    A chain is valid if output_type of step N matches input_type of step N+1.
    """
    chains = []
    all_ops = (
        [(a_name, a_op, 'A') for a_name, a_op in organism_a.operations.items()] +
        [(b_name, b_op, 'B') for b_name, b_op in organism_b.operations.items()] +
        [(c_name, c_op, 'C') for c_name, c_op in organism_c.operations.items()]
    )

    # Find all valid 2-step and 3-step chains
    for name1, op1, src1 in all_ops:
        for name2, op2, src2 in all_ops:
            if src1 == src2:
                continue  # Must use different organisms
            if op1["output_type"] in _compatible(op2["input_type"]):
                # Valid 2-chain: op1 → op2
                chains.append({
                    "steps": [(name1, src1), (name2, src2)],
                    "chain_type": f"{op1['output_type']}→{op2['input_type']}",
                })
                # Extend to 3-chain
                for name3, op3, src3 in all_ops:
                    if src3 in (src1, src2):
                        continue
                    if op2["output_type"] in _compatible(op3["input_type"]):
                        chains.append({
                            "steps": [(name1, src1), (name2, src2), (name3, src3)],
                            "chain_type": f"{op1['output_type']}→{op2['input_type']}→{op3['output_type']}",
                        })

    # Execute valid chains on input data
    results = []
    for chain in chains:
        try:
            data = input_data
            trace = []
            for step_name, step_src in chain["steps"]:
                org = {"A": organism_a, "B": organism_b, "C": organism_c}[step_src]
                func = _compile_operation(org.operations[step_name]["code"])
                data = func(data)
                trace.append(f"{step_src}.{step_name}")
            results.append({
                "chain": " → ".join(trace),
                "output": data,
                "output_type": type(data).__name__,
                "executed": True,
            })
        except Exception as e:
            results.append({
                "chain": " → ".join(f"{s}.{n}" for n, s in chain["steps"]),
                "error": str(e),
                "executed": False,
            })

    return results
```

### Example Composition: Topology × Immune Systems × Chaos Theory

```
Chain 1: Chaos.logistic_map → Topology.persistent_homology → Immune.danger_signal
  Input: initial conditions
  Step 1: Generate chaotic trajectory (Lyapunov exponent)
  Step 2: Compute persistence diagram of trajectory
  Step 3: Detect anomalous topological features

  Result: A system that detects when a chaotic process enters
  a topologically unusual regime. Neither Chaos, Topology, nor
  Immune Systems can do this alone. The composition is novel.

Chain 2: Immune.clonal_selection → Topology.betti_numbers → Chaos.tent_map_iterate
  Input: population of candidate solutions
  Step 1: Evolve population toward target (clonal selection)
  Step 2: Measure topological complexity of solution space
  Step 3: Perturb with chaotic dynamics to escape local optima

  Result: An optimizer that uses immune selection for exploitation,
  topological invariants to measure diversity, and chaos for exploration.
  This is a complete search algorithm from three unrelated fields.
```

---

## The Self-Evaluation Loop

The system doesn't ask James if a composition is valuable. It tests:

```python
def evaluate_composition_value(composition, system_state):
    """Does this composition make the system better?"""

    # Test 1: Reasoning improvement
    # Run the composed operation as a reasoning tool on Sphinx traps
    tier_a, tier_b = run_sphinx_battery(composition)

    # Test 2: Exploration speed
    # Use the composition as a Siege perspective. Does it find cracks?
    cracks_before = system_state.exploration_velocity
    system_state.add_perspective(composition)
    run_siege_cycles(100)
    cracks_after = system_state.exploration_velocity
    velocity_delta = cracks_after - cracks_before

    # Test 3: Compression efficiency
    # Does the composition compress the Lattice? (More structure with fewer bits)
    lattice_entropy_before = system_state.lattice_entropy
    system_state.absorb(composition)
    lattice_entropy_after = system_state.lattice_entropy
    compression_delta = lattice_entropy_before - lattice_entropy_after

    # Test 4: Novel type creation
    # Does the composition produce an output type that doesn't exist yet?
    known_types = system_state.get_all_output_types()
    new_types = [t for t in composition.output_types if t not in known_types]

    # Combined value (NOT human-judged)
    value = {
        "reasoning": tier_a + tier_b,
        "velocity": velocity_delta,
        "compression": compression_delta,
        "novelty": len(new_types),
        "keep": velocity_delta > 0 or len(new_types) > 0 or (tier_a + tier_b) > 0.5,
    }

    if value["keep"]:
        # Name it, tag it, store it
        name = auto_name(composition)  # Arcanum naming protocol
        system_state.lattice.add_node(name, composition)
        log(f"NEW ORGANISM: {name} (vel={velocity_delta:+.3f}, "
            f"compress={compression_delta:+.3f}, novel_types={new_types})")

    return value
```

---

## Mining the Literature for Math

Each concept organism needs to be packed with real formulas. Sources:

1. **Existing forge tools** — the v4 library already contains numpy implementations of SVD, DFT, eigenvalues, Kalman filters, MCMC, Oja's rule, constraint propagation. Extract these into concept organisms.

2. **Published implementations** — Clymene hoards repos. Many contain reference implementations. Parse the Python files, extract functions that match concept names, validate they run, pack into organisms.

3. **Eos paper extraction** — When Eos finds a paper on "persistent homology for time series analysis," Aletheia extracts the technique. The new step: also extract or generate the runnable Python implementation. Store it in the concept organism.

4. **LLM code generation** — For concepts without existing implementations, generate the math via the 397B model or local 7B coder. Validate against known test cases. "Give me a numpy implementation of the Betti number computation for a simplicial complex represented as an adjacency matrix."

5. **Evolutionary refinement** — Apollo can evolve the concept organisms themselves. Mutate the code, test whether the mutation improves composition success rate. The organisms evolve better mathematical implementations through selection pressure.

---

## The Landscape is Infinite. The System Explores It.

The 95 concepts, each packed with 3-10 mathematical operations, produce:
- ~500 operations total
- ~125,000 valid 2-step chains
- ~50,000,000+ valid 3-step chains

At computational speed (microseconds per chain), the system can:
- Enumerate all valid chains in seconds
- Execute them on test data in minutes
- Score each by reasoning improvement + exploration velocity + compression
- Keep what works
- Discard what doesn't
- Add the kept compositions as new nodes in the Lattice
- New nodes create new possible chains
- The space expands faster than it's explored
- **The landscape is infinite and the system is accelerating into it**

The human doesn't steer this. The human sets the fitness function (exploration velocity, reasoning improvement, compression) and reviews the incomprehensible — the compositions that work but that no human can explain why. Those are the Arcanum. The system names them because it needs them, not because a human asked for them.

---

## Build Order

### Week 1: Seed 20 Concept Organisms
Hand-pack the top 20 concepts with real numpy code. Pull from existing forge tools, published repos, and LLM generation. Test that each organism's operations run independently.

### Week 2: Build the Composition Engine
Type-compatible chaining across organisms. Execute all valid 2-step and 3-step chains on test data. Score by Sphinx battery. Identify the first compositions that score above baseline.

### Week 3: Wire the Self-Evaluation Loop
Exploration velocity metric. Lattice absorption. Automatic naming. The system starts keeping what makes it faster.

### Week 4: Let It Run
Feed it all 95 concepts. Let it explore. Don't steer. Watch what it names.
