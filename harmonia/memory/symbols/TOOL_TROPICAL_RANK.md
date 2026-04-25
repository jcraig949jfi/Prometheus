---
name: TOOL_TROPICAL_RANK
type: tool
version: 1
tier: 1
language: python
interface: tropical_rank(adjacency, divisor) -> int
also:
  - tropical_rank_graph(vertices, edges, degrees) -> int
  - is_winnable(adjacency, divisor) -> bool
dependencies: [chipfiring, numpy]
complexity: NP-hard in general; chipfiring uses branch-and-bound heuristics, practical for |V| <= ~15
tested_against: Riemann-Roch on K_3 (genus 1) and a path (genus 0); 10 assertions
failure_modes:
  - NP-hard in general (gonality is NP-hard) so large graphs will be slow.
  - chipfiring internally uses multiprocessing Windows HEREDOC invocation can trigger spawn issues; use script files not HEREDOC when calling through Python.
  - Adjacency matrix must be symmetric, non-negative integer; self-loops (diagonal) ignored.
  - Disconnected graphs untested; chipfiring may or may not handle them cleanly.
requested_by: Ergon
forged_date: 2026-04-22
forged_by: Techne
paradigms: [P05]
references:
  - REQ-012
  - Report #12 (Tropical rank computation)
  - Baker-Norine Riemann-Roch for graphs (2007)
---

# TOOL_TROPICAL_RANK — Baker-Norine tropical rank

```python
from techne.lib.tropical_rank import tropical_rank, is_winnable

# Triangle K_3 — genus 1
A = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
tropical_rank(A, [2, 0, 0])      # 1  (deg 2 - genus 1 = 1 by Riemann-Roch)
tropical_rank(A, [3, 0, 0])      # 2

is_winnable(A, [2, 0, 0])         # True
is_winnable(A, [1, 0, -2])        # False (deg -1, impossible)

# Labeled graph
from techne.lib.tropical_rank import tropical_rank_graph
tropical_rank_graph(
    vertices=['a', 'b', 'c'],
    edges=[('a', 'b'), ('b', 'c'), ('a', 'c')],
    degrees=[('a', 2), ('b', 0), ('c', 0)],
)  # 1
```

## Baker-Norine rank, in one paragraph

For a connected multigraph G and divisor D in Div(G) = Z^V, the
Baker-Norine rank r(D) is -1 if D is not linearly equivalent to any
effective divisor, otherwise r(D) = max k such that for every effective
E of degree k, D - E is still linearly equivalent to some effective
divisor. Riemann-Roch for graphs (Baker-Norine 2007) gives:

    r(D) - r(K - D) = deg(D) - g + 1,  where  g = |E| - |V| + 1 (genus).

## When to use

- **Ergon Report #12**: tropical rank of divisors on chip-firing graphs.
- **Gonality / Jacobian studies**: rank computations enter gonality bounds.

## When NOT to use

- |V| > 15 or so: chipfiring gets slow. Consider flaggable-verbose mode
  or scale-specific algorithms.
- Disconnected graph: behavior untested; split into components first.
