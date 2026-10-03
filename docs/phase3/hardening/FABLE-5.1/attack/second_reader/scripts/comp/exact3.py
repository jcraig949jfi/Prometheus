"""Exact check, N = 3 symbols (6 permutations, 6^6 = 46656 lives): for which sets of shown pairs is the
ninth map (2,2) uniformly distributed given every shown table? Enumerates all keys."""
from itertools import permutations, product
from collections import defaultdict
N = 3
PERMS = list(permutations(range(N)))
ALL = [(j, k) for j in range(3) for k in range(3)]

def comp(p, l):               # x -> p[l[x]]
    return tuple(p[l[x]] for x in range(N))

def dist(shown):
    table = defaultdict(lambda: defaultdict(int))
    for L in product(PERMS, repeat=3):
        for P in product(PERMS, repeat=3):
            key = tuple(comp(P[k], L[j]) for j, k in shown)
            table[key][comp(P[2], L[2])] += 1
    kinds = set()
    for key, d in table.items():
        vals = sorted(d.values())
        kinds.add("determined" if len(d) == 1 else ("uniform" if len(d) == len(PERMS) and len(set(vals)) == 1 else "other"))
    return kinds

cases = {
 "all eight shown": [p for p in ALL if p != (2, 2)],
 "control: move 2 never shown (six pairs)": [(j, k) for j in range(3) for k in range(2)],
 "control: table 2 never shown (six pairs)": [(j, k) for j in range(2) for k in range(3)],
 "one triangle (2,1),(1,1),(1,2)": [(2, 1), (1, 1), (1, 2)],
 "two of that triangle (2,1),(1,2)": [(2, 1), (1, 2)],
 "two of that triangle (1,1),(1,2)": [(1, 1), (1, 2)],
 "row 2 and column 2 only: (2,0),(2,1),(0,2),(1,2)": [(2, 0), (2, 1), (0, 2), (1, 2)],
 "five-edge path, no triangle: (0,2),(0,1),(1,1),(1,0),(2,0)": [(0, 2), (0, 1), (1, 1), (1, 0), (2, 0)],
 "that path minus (1,1)": [(0, 2), (0, 1), (1, 0), (2, 0)],
}
for name, shown in cases.items():
    print("%-62s -> ninth map given the shown tables: %s" % (name, ", ".join(sorted(dist(shown)))))
