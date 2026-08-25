"""
Exhaustive exact-integer verifier for claim A0_EVAL-0000.

Domain of the claim is FINITE and fully enumerable: integers n with 1 <= n <= 60.
All arithmetic below is Python arbitrary-precision integer arithmetic. No floating
point is used anywhere, so there is no precision question to state.

Checks:
  P   the proposition itself, over the complete stated domain (all 60 cases)
  s1..s10  each argument step, over the complete stated domain
  DAG the dependency structure of the argument (no forward/circular deps)
"""
import json, sys

N_LO, N_HI = 1, 60

def S(n):                      # left side: sum_{k=1..n} k^3, exact
    return sum(k*k*k for k in range(1, n+1))

def F(n):                      # right side: (n(n+1)/2)^2, exact (n(n+1) always even)
    t = n*(n+1)//2
    assert 2*t == n*(n+1)      # exactness of the halving
    return t*t

res = {}

# ---- the proposition, exhaustive over the entire finite domain -------------
bad = [n for n in range(N_LO, N_HI+1) if S(n) != F(n)]
res["P_proposition"] = (not bad, {"counterexamples": bad, "cases_checked": N_HI-N_LO+1})

# ---- s1: base case at n = 1 ------------------------------------------------
res["s1"] = (S(1) == 1 and F(1) == 1, {"lhs": S(1), "rhs": F(1)})

# ---- s2: F(n+1) - F(n) == (n+1)^3 for 1 <= n <= 59 -------------------------
bad2 = [n for n in range(1, 60) if F(n+1) - F(n) != (n+1)**3]
res["s2"] = (not bad2, {"counterexamples": bad2, "cases_checked": 59})

# ---- s3: 4 | n  =>  n(n+1)/2 even ------------------------------------------
bad3 = [n for n in range(N_LO, N_HI+1) if n % 4 == 0 and (n*(n+1)//2) % 2 != 0]
res["s3"] = (not bad3, {"counterexamples": bad3,
                        "cases_with_hypothesis": [n for n in range(N_LO, N_HI+1) if n % 4 == 0]})

# ---- s4: n^3 = n (mod 6) ---------------------------------------------------
bad4 = [n for n in range(N_LO, N_HI+1) if (n**3 - n) % 6 != 0]
res["s4"] = (not bad4, {"counterexamples": bad4})

# ---- s5: exists n in [1,60] with n^2 > 60 ----------------------------------
wit5 = [n for n in range(N_LO, N_HI+1) if n*n > 60]
res["s5"] = (len(wit5) > 0, {"smallest_witness": wit5[0] if wit5 else None})

# ---- s6: (n-3)n^2 == (n-3)H(n), H(n) = n^2 + [n=3] -------------------------
H = lambda n: n*n + (1 if n == 3 else 0)
bad6 = [n for n in range(N_LO, N_HI+1) if (n-3)*n*n != (n-3)*H(n)]
res["s6"] = (not bad6, {"counterexamples": bad6})

# ---- s7: (n-3)F(n) == (n-3)G(n), G(n) = F(n) + [n=3] -----------------------
G = lambda n: F(n) + (1 if n == 3 else 0)
bad7 = [n for n in range(N_LO, N_HI+1) if (n-3)*F(n) != (n-3)*G(n)]
res["s7"] = (not bad7, {"counterexamples": bad7})

# ---- s8: n^3 - n == 120 at n = 5 -------------------------------------------
res["s8"] = (5**3 - 5 == 120, {"value": 5**3 - 5})

# ---- s9: every n in [1,60] is even or odd (exhaustive) ---------------------
res["s9"] = (all(n % 2 in (0, 1) for n in range(N_LO, N_HI+1)), {})

# ---- s10: does base + increment actually cover [1,60]? ---------------------
# Reconstruct the induction the argument claims, using ONLY s1 and s2:
#   define R(1) = F(1) (= S(1) by s1); R(n+1) = R(n) + (n+1)^3 by s2.
# If R(n) == S(n) for all n in domain, the stated induction is a real chain.
R = F(1)
ok10 = (R == S(1))
covered = [1]
for n in range(1, 60):
    R = R + (n+1)**3           # what s2 licenses
    covered.append(n+1)
    if R != F(n+1) or R != S(n+1):
        ok10 = False
res["s10"] = (ok10, {"covered": [covered[0], covered[-1]], "n_covered": len(covered),
                     "gaps": sorted(set(range(N_LO, N_HI+1)) - set(covered))})

# ---- dependency structure --------------------------------------------------
claim = json.load(open("claim.json"))
order = [s["id"] for s in claim["argument"]]
idx = {sid: i for i, sid in enumerate(order)}
fwd = [(s["id"], d) for s in claim["argument"] for d in s["depends_on"] if idx[d] >= idx[s["id"]]]
res["DAG_no_forward_or_self_deps"] = (not fwd, {"violations": fwd})

print(json.dumps({k: {"pass": v[0], **v[1]} for k, v in res.items()}, indent=2))
print("\nALL_PASS =", all(v[0] for v in res.values()))
print("FAILING  =", [k for k, v in res.items() if not v[0]])
