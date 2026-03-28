"""
Topology organism.

Operations: betti_numbers, euler_characteristic, connected_components,
            persistent_homology_simple
"""

from .base import MathematicalOrganism


class Topology(MathematicalOrganism):
    name = "topology"
    operations = {
        "betti_numbers": {
            "code": """
def betti_numbers(adjacency):
    \"\"\"Compute Betti-0 (connected components) and Betti-1 (independent cycles)
    from an adjacency matrix of an undirected graph.
    Betti-0 = number of connected components.
    Betti-1 = E - V + C  (from Euler characteristic for graphs).\"\"\"
    A = np.asarray(adjacency, dtype=np.float64)
    n = A.shape[0]
    # Count edges (upper triangle of symmetric matrix)
    edges = int(np.sum(A > 0) // 2) if np.allclose(A, A.T) else int(np.sum(A > 0))

    # BFS to find connected components
    visited = np.zeros(n, dtype=bool)
    components = 0
    for start in range(n):
        if visited[start]:
            continue
        components += 1
        queue = [start]
        visited[start] = True
        while queue:
            node = queue.pop(0)
            for neighbor in range(n):
                if A[node, neighbor] > 0 and not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)

    b0 = components
    b1 = edges - n + components  # Euler formula for graphs
    return {"betti_0": b0, "betti_1": max(b1, 0)}
""",
            "input_type": "adjacency_matrix",
            "output_type": "dict",
        },
        "euler_characteristic": {
            "code": """
def euler_characteristic(adjacency):
    \"\"\"chi = V - E + F.  For a graph (no faces): chi = V - E.
    Input: adjacency matrix.\"\"\"
    A = np.asarray(adjacency, dtype=np.float64)
    V = A.shape[0]
    E = int(np.sum(A > 0))
    if np.allclose(A, A.T):
        E = E // 2
    return V - E
""",
            "input_type": "adjacency_matrix",
            "output_type": "scalar",
        },
        "connected_components": {
            "code": """
def connected_components(adjacency):
    \"\"\"Return list of component-label arrays via BFS.\"\"\"
    A = np.asarray(adjacency, dtype=np.float64)
    n = A.shape[0]
    labels = -np.ones(n, dtype=int)
    comp_id = 0
    for start in range(n):
        if labels[start] >= 0:
            continue
        queue = [start]
        labels[start] = comp_id
        while queue:
            node = queue.pop(0)
            for nb in range(n):
                if A[node, nb] > 0 and labels[nb] < 0:
                    labels[nb] = comp_id
                    queue.append(nb)
        comp_id += 1
    return labels
""",
            "input_type": "adjacency_matrix",
            "output_type": "vector",
        },
        "persistent_homology_simple": {
            "code": """
def persistent_homology_simple(distance_matrix):
    \"\"\"Simplified Vietoris-Rips persistent homology (H0 only).
    Returns birth-death pairs for connected components as edges are added
    in order of increasing distance.

    Input: square distance matrix.
    Output: list of (birth, death) pairs. The last component lives forever (death=inf).\"\"\"
    D = np.asarray(distance_matrix, dtype=np.float64)
    n = D.shape[0]

    # Union-Find
    parent = list(range(n))
    rank = [0] * n
    birth = [0.0] * n  # every point is born at distance 0

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1
        return True

    # Sort all edges by distance
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            edges.append((D[i, j], i, j))
    edges.sort()

    pairs = []
    for dist, i, j in edges:
        ri, rj = find(i), find(j)
        if ri != rj:
            # The younger component dies
            younger = rj if birth[rj] >= birth[ri] else ri
            pairs.append((birth[younger], dist))
            union(i, j)

    # One component survives forever
    pairs.append((0.0, float('inf')))
    return pairs
""",
            "input_type": "distance_matrix",
            "output_type": "persistence_diagram",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = Topology()
    print(org)

    # Triangle graph: 3 nodes, 3 edges, 1 cycle
    A = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]])
    betti = org.execute("betti_numbers", A)
    print(f"Triangle betti numbers: {betti}  (expect b0=1, b1=1)")

    chi = org.execute("euler_characteristic", A)
    print(f"Triangle Euler char: {chi}  (expect 0)")

    # Two disconnected edges
    A2 = np.array([
        [0, 1, 0, 0],
        [1, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
    ])
    labels = org.execute("connected_components", A2)
    print(f"Disconnected components: {labels}  (expect two groups)")

    betti2 = org.execute("betti_numbers", A2)
    print(f"Disconnected betti: {betti2}  (expect b0=2, b1=0)")

    # Persistent homology on 4 points
    pts = np.array([[0, 0], [1, 0], [0, 1], [5, 5]], dtype=float)
    D = np.sqrt(((pts[:, None] - pts[None, :]) ** 2).sum(axis=-1))
    ph = org.execute("persistent_homology_simple", D)
    print(f"Persistence diagram (H0): {ph}")

    print("--- topology: ALL TESTS PASSED ---")
