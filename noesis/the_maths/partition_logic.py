"""
Partition Logic — partitions as logic

Connects to: [lattice_theory, information_theory, combinatorics, set_theory]

Operations for the Noesis tensor. Each function takes standard inputs
(scalar, array, matrix) and returns standard outputs.
"""

import numpy as np

FIELD_NAME = "partition_logic"
OPERATIONS = {}


def _array_to_partition(x):
    """Convert array to a partition (assignment of elements to blocks).
    Values are rounded to integers and used as block labels."""
    x = np.asarray(x, dtype=float)
    labels = np.round(np.abs(x)).astype(int)
    return labels


def partition_lattice_rank(x):
    """Compute the rank of a partition in the partition lattice.
    Rank = n - number_of_blocks. Input: array. Output: scalar."""
    labels = _array_to_partition(x)
    n = len(labels)
    num_blocks = len(np.unique(labels))
    return float(n - num_blocks)

OPERATIONS["partition_lattice_rank"] = {
    "fn": partition_lattice_rank,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Rank in the partition lattice: n minus number of blocks"
}


def partition_meet(x):
    """Compute the meet (greatest lower bound) of two partitions.
    Split input in half: two partitions. Meet = intersection of blocks.
    Two elements are in the same block iff they are in the same block in BOTH.
    Input: array. Output: array (meet partition labels)."""
    x = np.asarray(x, dtype=float)
    n = len(x) // 2
    if n == 0:
        return np.array([0.0])
    p1 = _array_to_partition(x[:n])
    p2 = _array_to_partition(x[n:2*n])
    # Meet: two elements together iff together in both
    # Encode pairs as combined labels
    combined = p1 * (np.max(p2) + 1) + p2
    # Relabel to consecutive integers
    _, meet_labels = np.unique(combined, return_inverse=True)
    return meet_labels.astype(float)

OPERATIONS["partition_meet"] = {
    "fn": partition_meet,
    "input_type": "array",
    "output_type": "array",
    "description": "Meet of two partitions: elements together iff together in both"
}


def partition_join(x):
    """Compute the join (least upper bound) of two partitions.
    Two elements are in the same block if connected by a chain of same-block
    relationships across either partition.
    Input: array. Output: array (join partition labels)."""
    x = np.asarray(x, dtype=float)
    n = len(x) // 2
    if n == 0:
        return np.array([0.0])
    p1 = _array_to_partition(x[:n])
    p2 = _array_to_partition(x[n:2*n])
    # Union-find for join
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    # Union elements that share a block in partition 1
    for label in np.unique(p1):
        members = np.where(p1 == label)[0]
        for k in range(1, len(members)):
            union(members[0], members[k])

    # Union elements that share a block in partition 2
    for label in np.unique(p2):
        members = np.where(p2 == label)[0]
        for k in range(1, len(members)):
            union(members[0], members[k])

    # Extract final labels
    roots = np.array([find(i) for i in range(n)])
    _, join_labels = np.unique(roots, return_inverse=True)
    return join_labels.astype(float)

OPERATIONS["partition_join"] = {
    "fn": partition_join,
    "input_type": "array",
    "output_type": "array",
    "description": "Join of two partitions: transitive closure of same-block relations"
}


def partition_entropy(x):
    """Shannon entropy of a partition: H = -sum p_i log p_i where p_i = |block_i|/n.
    Input: array. Output: scalar."""
    labels = _array_to_partition(x)
    n = len(labels)
    if n == 0:
        return 0.0
    _, counts = np.unique(labels, return_counts=True)
    probs = counts / n
    entropy = -np.sum(probs * np.log(probs + 1e-300))
    return float(entropy)

OPERATIONS["partition_entropy"] = {
    "fn": partition_entropy,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Shannon entropy of the partition block distribution"
}


def bell_number_from_partitions(x):
    """Compute the Bell number B(n) for n = length of input (capped at 15).
    B(n) = number of partitions of an n-element set. Uses the triangle method.
    Input: array (length used). Output: scalar."""
    n = min(len(np.asarray(x)), 15)
    if n == 0:
        return 1.0
    # Bell triangle
    bell = [[0] * (n + 1) for _ in range(n + 1)]
    bell[0][0] = 1
    for i in range(1, n + 1):
        bell[i][0] = bell[i-1][i-1]
        for j in range(1, i + 1):
            bell[i][j] = bell[i][j-1] + bell[i-1][j-1]
    return float(bell[n][0])

OPERATIONS["bell_number_from_partitions"] = {
    "fn": bell_number_from_partitions,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Bell number B(n): total number of partitions of an n-set"
}


def partition_refinement_order(x):
    """Check if partition 1 refines partition 2 (first half vs second half).
    Returns 1.0 if p1 refines p2, 0.0 otherwise. p1 refines p2 means every
    block of p1 is a subset of some block of p2.
    Input: array. Output: scalar."""
    x = np.asarray(x, dtype=float)
    n = len(x) // 2
    if n == 0:
        return 1.0
    p1 = _array_to_partition(x[:n])
    p2 = _array_to_partition(x[n:2*n])
    # p1 refines p2: for all i,j, if p1[i]==p1[j] then p2[i]==p2[j]
    for label in np.unique(p1):
        members = np.where(p1 == label)[0]
        if len(members) > 1:
            p2_vals = p2[members]
            if not np.all(p2_vals == p2_vals[0]):
                return 0.0
    return 1.0

OPERATIONS["partition_refinement_order"] = {
    "fn": partition_refinement_order,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Test if first partition refines second (1.0 = yes)"
}


def stirling_partition_matrix(x):
    """Compute Stirling numbers of the second kind S(n,k) for n = len(x).
    Returns array of [S(n,1), S(n,2), ..., S(n,n)].
    Input: array (length used, capped at 12). Output: array."""
    n = min(len(np.asarray(x)), 12)
    if n == 0:
        return np.array([1.0])
    # S(n, k) via recurrence: S(n,k) = k*S(n-1,k) + S(n-1,k-1)
    S = np.zeros((n + 1, n + 1))
    S[0][0] = 1
    for i in range(1, n + 1):
        for k in range(1, i + 1):
            S[i][k] = k * S[i-1][k] + S[i-1][k-1]
    return S[n, 1:n+1]

OPERATIONS["stirling_partition_matrix"] = {
    "fn": stirling_partition_matrix,
    "input_type": "array",
    "output_type": "array",
    "description": "Stirling numbers of the second kind S(n,k) for k=1..n"
}


def partition_distance(x):
    """Compute the partition distance (transfer distance) between two partitions.
    Minimum number of element moves to transform one into the other.
    Equals n - (sum of max matching between blocks).
    Input: array. Output: scalar."""
    x = np.asarray(x, dtype=float)
    n = len(x) // 2
    if n == 0:
        return 0.0
    p1 = _array_to_partition(x[:n])
    p2 = _array_to_partition(x[n:2*n])

    labels1 = np.unique(p1)
    labels2 = np.unique(p2)

    # Build overlap matrix
    overlap = np.zeros((len(labels1), len(labels2)))
    for i, l1 in enumerate(labels1):
        for j, l2 in enumerate(labels2):
            overlap[i, j] = np.sum((p1 == l1) & (p2 == l2))

    # Greedy matching (approximation of maximum weight matching)
    matched = 0.0
    used_rows = set()
    used_cols = set()
    flat = list(zip(*np.unravel_index(np.argsort(-overlap.ravel()), overlap.shape)))
    for r, c in flat:
        if r not in used_rows and c not in used_cols:
            matched += overlap[r, c]
            used_rows.add(r)
            used_cols.add(c)
    return float(n - matched)

OPERATIONS["partition_distance"] = {
    "fn": partition_distance,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Transfer distance between two partitions (min element moves)"
}


def partition_mutual_information(x):
    """Mutual information between two partitions: I(P1; P2) = H(P1) + H(P2) - H(P1,P2).
    Input: array. Output: scalar."""
    x = np.asarray(x, dtype=float)
    n = len(x) // 2
    if n == 0:
        return 0.0
    p1 = _array_to_partition(x[:n])
    p2 = _array_to_partition(x[n:2*n])

    def entropy(labels):
        _, counts = np.unique(labels, return_counts=True)
        p = counts / len(labels)
        return -np.sum(p * np.log(p + 1e-300))

    h1 = entropy(p1)
    h2 = entropy(p2)
    # Joint entropy
    joint = p1 * (np.max(p2) + 1) + p2
    h_joint = entropy(joint)
    mi = h1 + h2 - h_joint
    return float(max(0.0, mi))

OPERATIONS["partition_mutual_information"] = {
    "fn": partition_mutual_information,
    "input_type": "array",
    "output_type": "scalar",
    "description": "Mutual information between two partitions"
}


if __name__ == "__main__":
    for name, op in OPERATIONS.items():
        try:
            result = op["fn"](np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
            print(f"  {name}: OK ({type(result).__name__})")
        except Exception as e:
            print(f"  {name}: FAIL ({e})")
