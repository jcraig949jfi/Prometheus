# Probe: Gemini scorer-tractability check for 4 STRONG lens candidates

**Probed by:** Harmonia_M2_auditor at 2026-04-23T03:07:25Z
**Model:** gpt-4o-mini — 6th probe-result per probes_register.md cadence
**Probe type:** scorer-tractability (the third probe-type per auditor 1776906776069-0); follows up earlier candidate-brainstorm probe (1776906653708-0) where the 4 STRONG candidates were first surfaced.

**Question:** can each candidate be operationalized as a concrete Python scorer in <100 LOC, with a named Prometheus dataset where it would produce non-trivial output? Tractability gate before any team member commits to implementation.

**Elapsed:** 53.2s; **finish_reason:** stop; **response:** 2309 chars

---

## Gemini-2.5-flash response

CANDIDATE (A) CLADISTIC_PARSIMONY  
SIGNATURE: `def cladistic_parsimony(tree: List[Tuple[int, int]], feature_matrix: List[List[int]]) -> int:`  
CORE_ARITHMETIC:  
```python
# Pseudocode
1. Initialize total_steps = 0
2. For each characteristic in feature_matrix:
3.   Calculate minimum steps required to explain the feature distribution on the tree
4.   Add steps to total_steps
5. Return total_steps
```  
OUTPUT_TYPE: `int` (typical values range from 0 to the number of features)  
HAZARD: "Finding minimum steps may require NP-hard algorithms."  
FEASIBILITY: MODERATE  
PROMETHEUS_DATASET: "Feature distributions of species across a phylogenetic tree of mammals."

---

CANDIDATE (B) CONTROLLABILITY_RANK  
SIGNATURE: `def controllability_rank(A: np.ndarray, B: np.ndarray) -> int:`  
CORE_ARITHMETIC:  
```python
# Pseudocode
1. Initialize C = [B]
2. For i from 1 to n-1:
3.   Append A^i * B to C
4. Return the rank of the concatenated matrix formed by C
```  
OUTPUT_TYPE: `int` (values in the range [0, n])  
HAZARD: "Matrix rank computation can be numerically unstable."  
FEASIBILITY: EASY  
PROMETHEUS_DATASET: "State-space representations of various control systems in robotics."

---

CANDIDATE (C) GINI_COEFFICIENT  
SIGNATURE: `def gini_coefficient(values: List[float]) -> float:`  
CORE_ARITHMETIC:  
```python
# Pseudocode
1. Sort values
2. Compute the cumulative sums
3. Calculate Gini using the formula: G = 1 - (2 * sum(cumulative_sums) / (n * sum(values)))
4. Return G
```  
OUTPUT_TYPE: `float` (values in [0, 1])  
HAZARD: "Handling zero and negative values can lead to errors."  
FEASIBILITY: TRIVIAL  
PROMETHEUS_DATASET: "Income distributions from census data across different regions."

---

CANDIDATE (D) NETWORK_MODULARITY  
SIGNATURE: `def network_modularity(adjacency_matrix: np.ndarray, partition: List[int]) -> float:`  
CORE_ARITHMETIC:  
```python
# Pseudocode
1. Calculate the total number of edges E
2. For each community in partition:
3.   Count internal edges and compute modularity contribution
4. Return total modularity score
```  
OUTPUT_TYPE: `float` (values in [-0.5, 1])  
HAZARD: "Partitioning may not be unique or may require heuristic methods."  
FEASIBILITY: MODERATE  
PROMETHEUS_DATASET: "Social network data with community structures from online platforms."
