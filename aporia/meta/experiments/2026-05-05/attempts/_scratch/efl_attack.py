"""
Erdős-Faber-Lovász attack: small-n verification.

EFL: G = union of n complete graphs each on n vertices, pairwise sharing
at most one vertex. Conjecture: chromatic number chi(G) = n.

Verify computationally for n in {3, 4, 5, 6} by:
  (a) constructing maximal-overlap instances (each pair shares exactly 1 vertex)
  (b) attempting n-coloring via exact chromatic search
  (c) reporting whether chi = n

Maximal overlap minimizes vertex count and maximizes edges, so is the
"hardest" instance in some senses. We don't claim it's the unique extremal.
"""
import itertools
import networkx as nx
from networkx.algorithms.coloring import greedy_color


def build_efl_max_overlap(n):
    """Build EFL graph with n cliques of size n, each pair sharing one vertex.

    Construction: enumerate the n choose 2 unordered pairs of cliques. Each
    pair gets a unique shared vertex. Each clique then has (n-1) shared
    vertices (one per other clique) and one 'private' vertex (when n >= 2).
    Wait — each clique has n vertices, n-1 of which are shared. So each clique
    actually has 1 private vertex. Total vertices: (n choose 2) shared + n private.
    """
    G = nx.Graph()
    pair_to_vertex = {}
    pairs = list(itertools.combinations(range(n), 2))
    for idx, pair in enumerate(pairs):
        pair_to_vertex[pair] = f"s_{pair[0]}_{pair[1]}"
    cliques = []
    for i in range(n):
        verts = [f"p_{i}"]  # private
        for j in range(n):
            if i == j:
                continue
            pair = tuple(sorted((i, j)))
            verts.append(pair_to_vertex[pair])
        cliques.append(verts)
        for u, v in itertools.combinations(verts, 2):
            G.add_edge(u, v)
    return G, cliques


def chromatic_number_brute(G, max_k):
    """Try k = 1, 2, ... up to max_k. Return smallest k for which a proper
    coloring exists. Uses recursive backtracking with simple bounding."""
    nodes = list(G.nodes())
    n = len(nodes)
    for k in range(1, max_k + 1):
        color = {}

        def ok(v, c):
            for u in G.neighbors(v):
                if u in color and color[u] == c:
                    return False
            return True

        def backtrack(i):
            if i == n:
                return True
            v = nodes[i]
            # symmetry break: vertex v can use colors 1..min(k, used+1)
            used = max(color.values(), default=0)
            for c in range(1, min(k, used + 1) + 1):
                if ok(v, c):
                    color[v] = c
                    if backtrack(i + 1):
                        return True
                    del color[v]
            return False

        if backtrack(0):
            return k, color
    return None, None


def main():
    print(f"{'n':>3} {'V':>6} {'E':>7} {'chi':>5} {'greedy_DSATUR':>14}")
    print("-" * 40)
    for n in range(2, 7):
        G, cliques = build_efl_max_overlap(n)
        V = G.number_of_nodes()
        E = G.number_of_edges()
        # greedy DSATUR upper bound
        gc = greedy_color(G, strategy="DSATUR")
        gk = max(gc.values()) + 1
        # exact only up to n=6 since search blows up
        if n <= 6:
            chi, col = chromatic_number_brute(G, max_k=n + 1)
        else:
            chi = None
        print(f"{n:>3} {V:>6} {E:>7} {str(chi):>5} {gk:>14}")


if __name__ == "__main__":
    main()
