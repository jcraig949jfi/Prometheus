"""
Cap set attack: maximum size of subset of F_3^n with no 3-AP.

A 3-AP in F_3^n: three points x, y, z with x + y + z = 0 (mod 3) and not all equal.
Equivalently: any three points where one is the midpoint of the other two
(in F_3 the midpoint is well-defined: (a+c)/2 doesn't work since 2 is invertible
in F_3 actually — yes 2 is invertible since 2*2=1 mod 3, so midpoint = (a+c)*2).

But the standard formulation: a cap set = subset S of F_3^n with no three
distinct points x, y, z in S such that x + y + z = 0 in F_3^n.

Known maxima: n=1: 2, n=2: 4, n=3: 9, n=4: 20, n=5: 45, n=6: 112.
n=7 frontier: lower bound 236 (Edel 2004), upper bound improved by polymath.

Approach:
- Brute search for n in {1..4} (computable), confirm known maxima.
- n=5, 6 too large for naive brute search; use random sampling to find
  good caps, compare to known bounds.
- Polynomial-method bound: 2.756^n. For n=4 this gives <58, for n=5 <162.
"""
import itertools
import random
import time


def F3_vectors(n):
    """All vectors in F_3^n."""
    return list(itertools.product(range(3), repeat=n))


def add_F3(u, v):
    return tuple((a + b) % 3 for a, b in zip(u, v))


def is_cap(S):
    """A set S is a cap iff for any three distinct x, y, z in S, x+y+z != 0."""
    S_list = list(S)
    L = len(S_list)
    for i in range(L):
        for j in range(i + 1, L):
            # third point that would complete the AP
            x, y = S_list[i], S_list[j]
            # in F_3, the third point of an AP through x, y is
            # z such that x + y + z = 0, i.e. z = -(x+y) = 2(x+y)
            z = tuple((-a - b) % 3 for a, b in zip(x, y))
            if z != x and z != y and z in S:
                return False
    return True


def cap_extends(S_set, candidate, S_list):
    """Check if S + {candidate} is still a cap, given S is a cap."""
    for i, x in enumerate(S_list):
        for j in range(i + 1, len(S_list)):
            y = S_list[j]
            z = tuple((-a - b) % 3 for a, b in zip(x, y))
            if z == candidate:
                return False
    # also: candidate + x + y = 0 with x = y from S? requires x = y so no.
    # but for the new triples (cand, x, y) we need no zero-sum
    for i, x in enumerate(S_list):
        # third point of AP through cand and x
        z = tuple((-a - b) % 3 for a, b in zip(candidate, x))
        if z != candidate and z != x and z in S_set:
            return False
    return True


def largest_cap_brute(n, time_budget=30):
    """Branch-and-bound largest cap in F_3^n."""
    V = F3_vectors(n)
    best = [0, []]
    start = time.time()

    def backtrack(S_list, S_set, idx):
        if time.time() - start > time_budget:
            return
        if len(S_list) > best[0]:
            best[0] = len(S_list)
            best[1] = list(S_list)
        # naive bound: remaining + current
        if len(S_list) + (len(V) - idx) <= best[0]:
            return
        for j in range(idx, len(V)):
            cand = V[j]
            if cap_extends(S_set, cand, S_list):
                S_set.add(cand)
                S_list.append(cand)
                backtrack(S_list, S_set, j + 1)
                S_set.remove(cand)
                S_list.pop()

    backtrack([], set(), 0)
    return best[0], best[1]


def random_greedy_cap(n, trials=200, seed=0):
    """Random greedy: shuffle, add greedily."""
    rng = random.Random(seed)
    V = F3_vectors(n)
    best = 0
    best_cap = None
    for t in range(trials):
        order = list(V)
        rng.shuffle(order)
        S = []
        S_set = set()
        for v in order:
            if cap_extends(S_set, v, S):
                S.append(v)
                S_set.add(v)
        if len(S) > best:
            best = len(S)
            best_cap = list(S)
    return best, best_cap


def main():
    print("Cap set attack")
    print()
    print("Brute force max cap, n in {1..4}:")
    print(f"{'n':>3} {'|F_3^n|':>8} {'max_cap':>8} {'time':>8}")
    expected = {1: 2, 2: 4, 3: 9, 4: 20}
    for n in range(1, 5):
        t0 = time.time()
        size, cap = largest_cap_brute(n, time_budget=120 if n == 4 else 30)
        dt = time.time() - t0
        marker = " OK" if size == expected.get(n) else f" expected {expected.get(n)}"
        print(f"{n:>3} {3**n:>8} {size:>8} {dt:>7.2f}s{marker}")
    print()
    print("Random greedy best for n in {5, 6, 7}:")
    print(f"{'n':>3} {'|F_3^n|':>8} {'greedy_best':>11} {'known_max':>10}")
    known = {5: 45, 6: 112, 7: 236}
    for n in range(5, 8):
        t0 = time.time()
        size, cap = random_greedy_cap(n, trials=200, seed=42)
        dt = time.time() - t0
        print(f"{n:>3} {3**n:>8} {size:>11} {known.get(n, '?'):>10}  ({dt:.1f}s)")


if __name__ == "__main__":
    main()
