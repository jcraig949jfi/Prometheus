"""
Frankl Union-Closed Sets attack: small-n empirical worst case.

For each ground-set size n, enumerate union-closed families F over [n]
(non-empty, contains the union — i.e. closed under pairwise union).
For each family, find the maximum element-frequency = max_x |{S in F : x in S}|.
Conjecture: max element-frequency >= |F| / 2.

Track the empirical minimum of max_freq / |F| over all enumerated families.

Direct enumeration is super-exponential. Instead, we sample / enumerate
union-closed families generated from small base families.

We use a simple technique: every union-closed family on [n] is determined
by its set of meet-irreducibles. But for a quick empirical attack,
generate union-closures from random subsets and tabulate.
"""
import itertools
import random


def union_closure(base_sets, ground=None):
    """Compute the union-closure of a list of frozensets."""
    F = set(frozenset(s) for s in base_sets)
    changed = True
    while changed:
        changed = False
        new = set()
        for a, b in itertools.combinations(F, 2):
            u = a | b
            if u not in F:
                new.add(u)
        if new:
            F |= new
            changed = True
    return F


def max_freq_ratio(F, ground):
    """Return (max_freq, len(F), ratio max_freq/len(F)) and the witness elements."""
    if not F:
        return 0, 0, 0.0, set()
    counts = {x: 0 for x in ground}
    for S in F:
        for x in S:
            counts[x] += 1
    if not counts:
        return 0, len(F), 0.0, set()
    m = max(counts.values())
    witnesses = {x for x, c in counts.items() if c == m}
    return m, len(F), m / len(F), witnesses


def enumerate_small_uc_families(n, samples=2000, seed=0):
    """Sample-based: generate random base families, compute union-closure,
    record min ratio. Also ensures we hit the obvious extremal families."""
    rng = random.Random(seed)
    ground = frozenset(range(n))
    all_subsets = [frozenset(s) for k in range(0, n + 1)
                   for s in itertools.combinations(ground, k)]
    # exclude empty for some experiments
    nonempty = [s for s in all_subsets if s]
    worst_ratio = 1.0
    worst_family = None
    seen_signatures = set()

    # Always include the family of all singletons-extended
    bases = []
    # 1) all singletons
    bases.append([frozenset({i}) for i in range(n)])
    # 2) all singletons + ground
    bases.append([frozenset({i}) for i in range(n)] + [ground])
    # 3) chain
    bases.append([frozenset(range(i + 1)) for i in range(n)])

    for _ in range(samples):
        size = rng.randint(2, min(2 ** n, 10))
        base = rng.sample(nonempty, min(size, len(nonempty)))
        bases.append(base)

    for base in bases:
        F = union_closure(base)
        if not F:
            continue
        sig = tuple(sorted(tuple(sorted(s)) for s in F))
        if sig in seen_signatures:
            continue
        seen_signatures.add(sig)
        m, L, r, w = max_freq_ratio(F, ground)
        if r < worst_ratio:
            worst_ratio = r
            worst_family = F
    return worst_ratio, worst_family


def main():
    print("Frankl empirical worst-case (sampled union-closed families)")
    print(f"{'n':>3} {'min_ratio':>10} {'#families_sampled':>18}")
    for n in range(2, 7):
        r, F = enumerate_small_uc_families(n, samples=3000, seed=n)
        print(f"{n:>3} {r:>10.4f}")
        if r < 0.5:
            print(f"   COUNTEREXAMPLE? family of size {len(F)}: {sorted(map(sorted, F))}")
    # Also: report Gilmer/Sawin-style theoretical bounds for context
    print()
    print("Reference: 0.5 = Frankl conjecture; 0.38234 ~ Sawin/Cambie 2023 best lower bound")


if __name__ == "__main__":
    main()
