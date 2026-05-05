"""
Sunflower attack: largest 3-sunflower-free family of k-sets.

A 3-sunflower in a k-uniform family is 3 sets A, B, C with
A ∩ B = A ∩ C = B ∩ C = A ∩ B ∩ C  (the common 'core').

Erdős-Ko: f_k(N) := max size of family of k-subsets of [N] with no 3-sunflower.
Conjecture: f_k(N) <= c(k)^k for some absolute constant c(k).

ALWZ 2019/2020: c(k) = O(log k). Open: explicit small constant.

Approach for k=3:
- For modest N, enumerate 3-subsets of [N], greedy / branch on inclusion,
  find largest family with no 3-sunflower.
- Compare with known bounds: f_3(N) >= ??? lower bound constructions
  (full design / Steiner triple systems sometimes feature here).

Brute force k=3, N=8: there are C(8,3) = 56 3-subsets, and we want the
largest 3-sunflower-free subfamily. We can enumerate via SAT-style backtracking.
"""
import itertools
import time


def is_sunflower(s1, s2, s3):
    """Three sets form a sunflower iff their pairwise intersections all
    equal their triple intersection."""
    core = s1 & s2 & s3
    return (s1 & s2) == core and (s1 & s3) == core and (s2 & s3) == core


def has_3_sunflower(family):
    """Check if family contains any 3-sunflower."""
    fam_list = list(family)
    for i, j, k in itertools.combinations(range(len(fam_list)), 3):
        if is_sunflower(fam_list[i], fam_list[j], fam_list[k]):
            return True
    return False


def largest_sunflower_free(N, k, time_budget_sec=30):
    """Branch-and-bound: enumerate k-subsets, try to extend family while
    maintaining sunflower-free. Returns (size, family) of best found."""
    universe = list(range(N))
    all_ksets = [frozenset(s) for s in itertools.combinations(universe, k)]
    best_size = 0
    best_family = []
    start = time.time()

    def adds_sunflower(family, candidate):
        for a, b in itertools.combinations(family, 2):
            if is_sunflower(a, b, candidate):
                return True
        return False

    def backtrack(family, idx):
        nonlocal best_size, best_family
        if time.time() - start > time_budget_sec:
            return
        if len(family) > best_size:
            best_size = len(family)
            best_family = list(family)
        # bound: remaining + current
        if len(family) + (len(all_ksets) - idx) <= best_size:
            return
        for j in range(idx, len(all_ksets)):
            cand = all_ksets[j]
            if not adds_sunflower(family, cand):
                family.append(cand)
                backtrack(family, j + 1)
                family.pop()

    backtrack([], 0)
    return best_size, best_family


def known_construction_kostochka(k):
    """Known lower-bound construction: Kostochka 1997 / Erdős-Szemerédi
    style gives f_k(N) >= (k!)^something for large N. Not implemented here.
    Just report what we know about lower bounds for k=3."""
    return None


def main():
    print("Sunflower attack: brute-force largest 3-sunflower-free family")
    print(f"{'k':>2} {'N':>3} {'size':>5} {'C(N,k)':>8} {'time':>8}")
    print("-" * 35)
    for k in [3]:
        for N in range(k, 9):
            t0 = time.time()
            size, fam = largest_sunflower_free(N, k, time_budget_sec=20)
            dt = time.time() - t0
            total = sum(1 for _ in itertools.combinations(range(N), k))
            print(f"{k:>2} {N:>3} {size:>5} {total:>8} {dt:>7.2f}s")
            if size <= 12:
                print(f"   family: {[sorted(s) for s in fam]}")


if __name__ == "__main__":
    main()
