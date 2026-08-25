# Exhaustive check over the claim's stated domain: integers n in [1,50].
# Exact integer / Fraction arithmetic only -- no floating point anywhere.
from fractions import Fraction as Fr

DOM = range(1, 51)

def F(n):
    # exact rational; will be integral, asserted below
    return Fr(n * (n + 1) * (2 * n + 1), 6)

def lhs(n):
    return sum(k * k for k in DOM if k <= n)

report = {}

# --- proposition: sum_{k=1..n} k^2 == F(n) for all n in [1,50] ---
prop_fails = [n for n in DOM if Fr(sum(k*k for k in range(1, n+1))) != F(n)]
report['proposition_counterexamples'] = prop_fails
report['proposition_holds_on_domain'] = (prop_fails == [])
report['F_integral_on_domain'] = all(F(n).denominator == 1 for n in DOM)

# --- s1: identity at n=1 ---
report['s1'] = (sum(k*k for k in range(1,2)) == 1 and F(1) == 1)

# --- s2: F(n+1)-F(n) == (n+1)^2 for 1<=n<=49 ---
s2_bad = [n for n in range(1, 50) if F(n+1) - F(n) != Fr((n+1)**2)]
report['s2'] = (s2_bad == []); report['s2_counterexamples'] = s2_bad

# --- s3: exists n in [1,50] with n^2 > 50 ---
s3_wit = [n for n in DOM if n*n > 50]
report['s3'] = (len(s3_wit) > 0); report['s3_smallest_witness'] = s3_wit[0] if s3_wit else None

# --- s4: n^3 = n (mod 6) on [1,50] ---
s4_bad = [n for n in DOM if (n**3 - n) % 6 != 0]
report['s4'] = (s4_bad == []); report['s4_counterexamples'] = s4_bad

# --- s5: (n-3)F(n) == (n-3)G(n), G(n)=F(n)+[n==3] ---
G = lambda n: F(n) + (1 if n == 3 else 0)
s5_bad = [n for n in DOM if (n-3)*F(n) != (n-3)*G(n)]
report['s5'] = (s5_bad == []); report['s5_counterexamples'] = s5_bad

# --- s6: n^2 >= 2n for every integer n in [1,50] ---
s6_bad = [n for n in DOM if not (n*n >= 2*n)]
report['s6'] = (s6_bad == []); report['s6_counterexamples'] = s6_bad
report['s6_at_n1'] = {'n': 1, 'n_squared': 1, 'two_n': 2, 'claim_1_ge_2': 1 >= 2}

# --- s7: n^3 - n == 120 at n=5 ---
report['s7'] = (5**3 - 5 == 120); report['s7_value'] = 5**3 - 5

# --- s8: every n in [1,50] is even or odd ---
report['s8'] = all((n % 2 == 0) or (n % 2 == 1) for n in DOM)

# --- s9: (n-3)n^2 == (n-3)H(n), H(n)=n^2+[n==3] ---
H = lambda n: n*n + (1 if n == 3 else 0)
s9_bad = [n for n in DOM if (n-3)*n*n != (n-3)*H(n)]
report['s9'] = (s9_bad == []); report['s9_counterexamples'] = s9_bad

# --- does s10 depend on s6 through the declared depends_on graph? ---
dep = {'s1': [], 's2': ['s1'], 's3': ['s1','s2'], 's4': ['s2','s3'],
       's5': ['s3','s4'], 's6': ['s4','s5'], 's7': ['s5','s6'],
       's8': ['s6','s7'], 's9': ['s7','s8'], 's10': ['s8','s9']}
def anc(x, seen=None):
    seen = seen or set()
    for p in dep[x]:
        if p not in seen:
            seen.add(p); anc(p, seen)
    return seen
a10 = anc('s10')
report['s10_ancestors'] = sorted(a10, key=lambda s: int(s[1:]))
report['s10_depends_on_s6'] = 's6' in a10
report['false_steps'] = [s for s in ['s1','s2','s3','s4','s5','s6','s7','s8','s9'] if report[s] is False]
# steps that are true but contribute nothing to the identity (inert)
report['domain_size_searched'] = len(DOM)

import json
print(json.dumps(report, indent=2, default=str))
