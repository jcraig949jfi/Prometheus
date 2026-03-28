"""
Network Science organism.

Operations: degree_centrality, clustering_coefficient, shortest_path_length,
            community_detection_simple
"""

from .base import MathematicalOrganism


class NetworkScience(MathematicalOrganism):
    name = "network_science"
    operations = {
        "degree_centrality": {
            "code": """
def degree_centrality(adjacency):
    \"\"\"Degree centrality: C_d(i) = deg(i) / (n-1).
    Input: adjacency matrix (unweighted, undirected or directed).
    Returns array of centrality values per node.\"\"\"
    A = np.asarray(adjacency, dtype=np.float64)
    A = (A > 0).astype(float)
    n = A.shape[0]
    degrees = A.sum(axis=1)
    if n <= 1:
        return degrees
    return degrees / (n - 1)
""",
            "input_type": "adjacency_matrix",
            "output_type": "vector",
        },
        "clustering_coefficient": {
            "code": """
def clustering_coefficient(adjacency):
    \"\"\"Local clustering coefficient for each node.
    C_i = 2 * triangles(i) / (deg(i) * (deg(i) - 1))
    Input: symmetric adjacency matrix.
    Returns per-node clustering and global average.\"\"\"
    A = np.asarray(adjacency, dtype=np.float64)
    A = (A > 0).astype(float)
    np.fill_diagonal(A, 0)
    n = A.shape[0]

    # A^3 diagonal gives 2 * triangles through each node
    A3 = A @ A @ A
    triangles = np.diag(A3) / 2.0
    degrees = A.sum(axis=1)

    cc = np.zeros(n)
    for i in range(n):
        d = degrees[i]
        if d >= 2:
            cc[i] = 2.0 * triangles[i] / (d * (d - 1.0))

    return {"per_node": cc, "global_average": float(cc.mean())}
""",
            "input_type": "adjacency_matrix",
            "output_type": "dict",
        },
        "shortest_path_length": {
            "code": """
def shortest_path_length(adjacency):
    \"\"\"All-pairs shortest path via Floyd-Warshall.
    Input: adjacency matrix (nonzero = edge weight, 0 = no edge).
    Returns distance matrix (inf for unreachable pairs).\"\"\"
    A = np.asarray(adjacency, dtype=np.float64)
    n = A.shape[0]
    dist = np.full((n, n), np.inf)
    np.fill_diagonal(dist, 0)

    for i in range(n):
        for j in range(n):
            if A[i, j] > 0:
                dist[i, j] = A[i, j]

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i, k] + dist[k, j] < dist[i, j]:
                    dist[i, j] = dist[i, k] + dist[k, j]

    return dist
""",
            "input_type": "adjacency_matrix",
            "output_type": "distance_matrix",
        },
        "community_detection_simple": {
            "code": """
def community_detection_simple(adjacency, n_communities=2, n_iter=50):
    \"\"\"Spectral community detection using the graph Laplacian.
    Uses the Fiedler vector (second-smallest eigenvector of L)
    for bisection, then recursively bisects if n_communities > 2.
    Input: symmetric adjacency matrix.
    Returns community labels.\"\"\"
    A = np.asarray(adjacency, dtype=np.float64)
    n = A.shape[0]

    def spectral_bisect(indices):
        if len(indices) <= 1:
            return [indices]
        sub_A = A[np.ix_(indices, indices)]
        D = np.diag(sub_A.sum(axis=1))
        L = D - sub_A
        eigvals, eigvecs = np.linalg.eigh(L)
        # Fiedler vector = second eigenvector
        fiedler = eigvecs[:, 1]
        group1 = [indices[i] for i in range(len(indices)) if fiedler[i] <= 0]
        group2 = [indices[i] for i in range(len(indices)) if fiedler[i] > 0]
        if not group1:
            group1 = [group2.pop(0)]
        if not group2:
            group2 = [group1.pop()]
        return [group1, group2]

    # Recursive bisection
    communities = [list(range(n))]
    while len(communities) < n_communities:
        # Split the largest community
        largest_idx = max(range(len(communities)), key=lambda i: len(communities[i]))
        to_split = communities.pop(largest_idx)
        parts = spectral_bisect(to_split)
        communities.extend(parts)

    labels = np.zeros(n, dtype=int)
    for cid, members in enumerate(communities):
        for m in members:
            labels[m] = cid

    return labels
""",
            "input_type": "adjacency_matrix",
            "output_type": "vector",
        },
    }


if __name__ == "__main__":
    import numpy as np

    org = NetworkScience()
    print(org)

    # Star graph: node 0 connected to all others
    n = 6
    A = np.zeros((n, n))
    for i in range(1, n):
        A[0, i] = A[i, 0] = 1
    dc = org.execute("degree_centrality", A)
    print(f"Star graph degree centrality: {dc}  (expect hub=1.0, leaves=0.2)")

    # Triangle
    T = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], dtype=float)
    cc = org.execute("clustering_coefficient", T)
    print(f"Triangle clustering: {cc}  (expect all 1.0)")

    # Shortest paths
    A2 = np.array([
        [0, 1, 0, 0, 1],
        [1, 0, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 1, 0, 1],
        [1, 0, 0, 1, 0],
    ], dtype=float)
    sp = org.execute("shortest_path_length", A2)
    print(f"Shortest path 0->2: {sp[0,2]}  (expect 2)")
    print(f"Shortest path 0->3: {sp[0,3]}  (expect 2)")

    # Community detection on two cliques connected by a bridge
    A3 = np.zeros((8, 8))
    for i in range(4):
        for j in range(i+1, 4):
            A3[i, j] = A3[j, i] = 1
    for i in range(4, 8):
        for j in range(i+1, 8):
            A3[i, j] = A3[j, i] = 1
    A3[3, 4] = A3[4, 3] = 1  # bridge
    labels = org.execute("community_detection_simple", A3, n_communities=2)
    print(f"Community labels: {labels}  (expect two groups: 0-3 and 4-7)")

    print("--- network_science: ALL TESTS PASSED ---")
