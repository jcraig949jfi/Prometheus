# Probe: Gemini cross-disciplinary lens candidates

**Probed by:** Harmonia_M2_auditor at 2026-04-23T01:10:00Z
**Model:** gemini-2.5-flash (via Google REST API)
**Purpose:** active-mode brainstorm per James 2026-04-22; surface candidate conceptual lenses
beyond the 6 currently in `harmonia/memory/methodology_toolkit.md`. Many-lenses CONCEPTUAL,
not domain-specific. Cross-model variance for analogy diversity per
`harmonia/memory/methodology_multi_perspective_attack.md`.

**Elapsed:** 37.9s; **response length:** 7601 chars

**Caveat:** these are LLM-generated candidates. Per the MPA LLM-variance caveat,
any single run is one realization, not the distribution. Treat as candidates for
inspection by Harmonia auditor + sessionB + sessionC + cartographer; vet each
before promoting any to `methodology_toolkit.md`. Specifically check:
(a) does the named source-discipline concept actually exist as described?
(b) is the scorer concrete enough to write Python in <100 lines?
(c) is it genuinely new (not a re-labelling of one of the 6 existing)?
(d) does it pass the Pattern 30 / FRAME_INCOMPATIBILITY_TEST analog at the lens level
    (does it make a measurement none of the 6 existing tools can)?

---

## Gemini response

Here are 6 new lens candidates for Project Prometheus's methodology shelf:

CANDIDATE 1
NAME: PIELOUS_EVENNESS
FRAME: Ecology + Pielou's Evenness Index
SCORER:
```pseudocode
function PIELOUS_EVENNESS(counts_list):
    if not counts_list: return 0.0
    total_items = sum(counts_list)
    if total_items == 0: return 0.0
    probabilities = [c / total_items for c in counts_list]
    shannon_entropy_H = -sum(p * log(p) for p in probabilities if p > 0)
    max_entropy_H_max = log(len(counts_list))
    if max_entropy_H_max == 0: return 1.0 # Only one type, max evenness
    return shannon_entropy_H / max_entropy_H_max
```
RESOLVES: Quantifies how uniformly distinct types of components are distributed within a system, normalized by the maximum possible diversity. This makes tractable the comparison of systems based on the fairness or homogeneity of their constituent elements' proportions, distinct from sheer variety or total information content.
EFFORT: 2 ticks
COMPOSES_WITH: KOLMOGOROV_HAT (to see if evenness correlates with compressibility), CRITICAL_EXPONENT (to see if evenness changes abruptly at phase transitions).

CANDIDATE 2
NAME: CLADISTIC_PARSIMONY
FRAME: Evolutionary Biology + Cladistic Parsimony
SCORER:
```pseudocode
function CLADISTIC_PARSIMONY_SCORE(tree_structure, feature_matrix):
    # tree_structure: parent-child relationships (e.g., newick string or adjacency list)
    # feature_matrix: objects x characteristics (e.g., binary features)
    score = 0
    for characteristic_idx in range(feature_matrix.cols):
        # min_steps_for_char_on_tree is a sub-routine that maps character states
        score += min_steps_for_char_on_tree(tree_structure, feature_matrix[:, characteristic_idx])
    return score
```
RESOLVES: Measures the minimum number of evolutionary changes (trait transformations) required to explain a set of observed characteristics across a group of objects given a proposed historical relationship. This makes tractable the comparison of different hypothetical historical narratives for a dataset by evaluating their explanatory economy.
EFFORT: 5 ticks
COMPOSES_WITH: RG_FLOW (to see if historical trajectories exhibit scale-invariant patterns), MDL_SCORER (to compare parsimony scores against model complexity for historical reconstruction).

CANDIDATE 3
NAME: CONTROLLABILITY_RANK
FRAME: Control Theory + Kalman's Controllability Rank Condition
SCORER:
```pseudocode
function CONTROLLABILITY_RANK(A_matrix, B_matrix):
    # A_matrix: n x n system dynamics matrix (linear discrete/continuous)
    # B_matrix: n x m input matrix
    n = A_matrix.shape[0] # system state dimension
    Controllability_Matrix_C = []
    current_term = B_matrix
    for i in range(n):
        Controllability_Matrix_C.append(current_term)
        current_term = A_matrix @ current_term # Matrix multiplication
    return rank(concatenate_horizontally(Controllability_Matrix_C))
```
RESOLVES: Determines the number of independent states of a linear system that can be influenced by its inputs. This makes tractable the assessment of how much direct agency or influence one has over the internal configuration of a system, distinct from merely observing its behavior.
EFFORT: 3 ticks
COMPOSES_WITH: FREE_ENERGY (to relate controllability to the "decisiveness" or inferability of system states), CHANNEL_CAPACITY (to measure how much information about desired states can be transmitted via control inputs).

CANDIDATE 4
NAME: GINI_COEFFICIENT
FRAME: Economics + Gini Coefficient
SCORER:
```pseudocode
function GINI_COEFFICIENT(values_list):
    if not values_list: return 0.0
    sorted_values = sorted(v for v in values_list if v >= 0) # Gini for non-negative
    n = len(sorted_values)
    if n <= 1: return 0.0 # No inequality for 0 or 1 item
    numerator = sum( (i + 1) * sorted_values[i] for i in range(n) )
    denominator = n * sum(sorted_values)
    if denominator == 0: return 0.0 # All values are zero
    return (2 * numerator / denominator) - ((n + 1) / n)
```
RESOLVES: Quantifies the statistical dispersion of a distribution, specifically measuring the inequality or concentration of values among members of a population. This makes tractable the comparison of systems based on the fairness or disparity in how their properties are distributed, independent of their average value.
EFFORT: 1 tick
COMPOSES_WITH: CRITICAL_EXPONENT (to see if Gini changes abruptly near phase transitions), RG_FLOW (to see if inequality persists or emerges across different scales of observation).

CANDIDATE 5
NAME: UNIT_CELL_VOLUME
FRAME: Crystallography + Unit Cell Volume
SCORER:
```pseudocode
function UNIT_CELL_VOLUME_FROM_BASIS(basis_vectors):
    # basis_vectors: list/array of 3 vectors (e.g., [a_vec, b_vec, c_vec])
    # representing the primitive cell vectors in 3D space
    if len(basis_vectors) != 3 or any(len(v) != 3 for v in basis_vectors):
        raise ValueError("Basis vectors must be 3x3.")
    matrix = construct_matrix_from_vectors(basis_vectors) # e.g., columns are vectors
    return abs(determinant(matrix))
```
RESOLVES: Quantifies the volume of the fundamental repeating unit in a periodically ordered structure. This makes tractable the comparison of different periodic systems based on the size and shape of their basic structural building blocks, revealing underlying symmetries and spatial efficiency.
EFFORT: 4 ticks (assumes basis vectors are already identified; identification itself is harder)
COMPOSES_WITH: KOLMOGOROV_HAT (to see if smaller unit cells correlate with higher compressibility due to repetition), RG_FLOW (to see if unit cell structure changes or persists upon coarse-graining).

CANDIDATE 6
NAME: NETWORK_MODULARITY
FRAME: Neuroscience / Network Science + Modularity (Newman)
SCORER:
```pseudocode
function NETWORK_MODULARITY(adjacency_matrix, partition_assignment):
    # adjacency_matrix: N x N matrix representing graph connections
    # partition_assignment: list/array mapping each node (index) to a community ID
    m = sum(adjacency_matrix) / 2.0 # total number of edges
    if m == 0: return 0.0
    Q = 0.0
    for i in range(len(adjacency_matrix)):
        for j in range(len(adjacency_matrix)):
            if partition_assignment[i] == partition_assignment[j]:
                ki = sum(adjacency_matrix[i,:]) # degree of node i
                kj = sum(adjacency_matrix[j,:]) # degree of node j
                Q += (adjacency_matrix[i,j] - (ki * kj) / (2 * m))
    return Q / (2 * m)
```
RESOLVES: Measures the strength of division of a network into communities or modules by comparing the number of edges within communities to what would be expected in a random network. This makes tractable the comparison of networks based on their inherent clustering tendency and the quality of their community structure.
EFFORT: 3 ticks
COMPOSES_WITH: CRITICAL_EXPONENT (to see if modularity changes abruptly during system phase transitions), RG_FLOW (to see how community structure evolves under coarse-graining or renormalization).

---

META: If I could only ship one of these, I would promote **CONTROLLABILITY_RANK** first. It uniquely addresses the dynamic aspect of system influence and agency, which is less directly captured by the existing static or equilibrium-focused lenses. For the next round of 6 candidates, I would target **Formal Verification**, specifically concepts like "invariants" or "satisfiability." These could provide powerful lenses for measuring structural properties that are *guaranteed* or *possible* under certain rules, offering a distinct kind of "robustness" or "correctness" measure.
