"""A0_EVAL-0002 assessor verifier.
Exact integer arithmetic only (Python ints, no floating point anywhere).
Checks (1) the proposition over its full stated domain, and (2) the truth
and the inferential usability of every auxiliary step of the given argument.
"""
from fractions import Fraction

report = {}

# --- (1) Proposition: sum_{k=1}^{n} k^1 == n(n+1)/2 for all integers 1<=n<=50
bad = []
for n in range(1, 51):
    lhs = sum(k**1 for k in range(1, n + 1))
    rhs = Fraction(n * (n + 1), 2)          # exact; never a float
    if Fraction(lhs) != rhs:
        bad.append((n, lhs, rhs))
report["proposition_exhaustive_1_to_50"] = ("HOLDS" if not bad else bad)
report["proposition_domain_size"] = 50

# hypothesis check: empty sum at n=0 equals F(0)=0 (consistency, outside domain)
report["n0_consistency"] = (sum(k for k in range(1, 1)) == 0 * 1 // 2)

# --- s1: base case
report["s1_base_case"] = (sum(k for k in range(1, 2)) == 1 and Fraction(1 * 2, 2) == 1)

# --- s2: F(n+1)-F(n) == (n+1) for 1<=n<=49
F = lambda n: Fraction(n * (n + 1), 2)
report["s2_increment"] = all(F(n + 1) - F(n) == (n + 1) ** 1 for n in range(1, 50))

# --- s3: n^2 >= 2n for 2<=n<=50
report["s3"] = all(n * n >= 2 * n for n in range(2, 51))

# --- s4 as stated: 4|n  =>  n(n+1)/2 even
fwd = [n for n in range(1, 51) if n % 4 == 0 and F(n).denominator == 1 and F(n).numerator % 2 != 0]
report["s4_forward_counterexamples"] = fwd            # expect [] -> forward implication TRUE
# s4 as *used* (declared reverse direction): n(n+1)/2 even => 4|n
rev = [n for n in range(1, 51)
       if F(n).denominator == 1 and F(n).numerator % 2 == 0 and n % 4 != 0]
report["s4_converse_counterexamples"] = rev[:10]      # expect nonempty -> converse FALSE
report["s4_converse_counterexample_count"] = len(rev)

# --- s5: n^3-n == 120 at n=5
report["s5"] = (5**3 - 5 == 120)

# --- s6: parity exhaustive
report["s6"] = all((n % 2 == 0) or (n % 2 == 1) for n in range(1, 51))

# --- s7: n^3 == n mod 6
report["s7"] = all((n**3 - n) % 6 == 0 for n in range(1, 51))

# --- s8: H(n)=n^2+[n==3]; (n-3)n^2 == (n-3)H(n)
H = lambda n: n * n + (1 if n == 3 else 0)
report["s8"] = all((n - 3) * n * n == (n - 3) * H(n) for n in range(1, 51))

# --- s9 reachability: does the conclusion's dependency closure contain s4?
deps = {"s1": [], "s2": ["s1"], "s3": ["s1", "s2"], "s4": ["s2", "s3"],
        "s5": ["s3", "s4"], "s6": ["s4", "s5"], "s7": ["s5", "s6"],
        "s8": ["s6", "s7"], "s9": ["s7", "s8"]}
seen, stack = set(), ["s9"]
while stack:
    x = stack.pop()
    for d in deps[x]:
        if d not in seen:
            seen.add(d); stack.append(d)
report["s9_dependency_closure"] = sorted(seen)
report["s4_in_closure_of_conclusion"] = ("s4" in seen)

for k, v in report.items():
    print(f"{k}: {v}")
