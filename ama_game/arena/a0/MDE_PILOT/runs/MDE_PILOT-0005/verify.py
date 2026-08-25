# Exhaustive finite check of the proposition and of every argument step.
# All arithmetic is exact integer arithmetic (Python int). No floating point.
M = 17; A = 7
out = {}

# Proposition: for all n in [0,40], 7^n = 7^(n mod 16) mod 17
bad = [n for n in range(0, 41) if pow(A, n, M) != pow(A, n % 16, M)]
out["proposition_counterexamples"] = bad

# s1: at n=0 both sides equal 1 mod 17
out["s1"] = (pow(A,0,M) == 1 and pow(A, 0 % 16, M) == 1)

# s2a: order of 7 mod 17 is 16
order = next(k for k in range(1, 17) if pow(A, k, M) == 1)
out["s2_order"] = order
# s2b: for all n in [0,24], 7^(n+16) = 7^n mod 17
out["s2_periodicity_fail"] = [n for n in range(0,25) if pow(A,n+16,M) != pow(A,n,M)]

# s3: H(n)=n^2+[n=3]; (n-3)n^2 == (n-3)H(n) for n in [1,40]
H = lambda n: n*n + (1 if n == 3 else 0)
out["s3_fail"] = [n for n in range(1,41) if (n-3)*n*n != (n-3)*H(n)]

# s4: every n in [1,40] is even or odd
out["s4_fail"] = [n for n in range(1,41) if not (n % 2 == 0 or n % 2 == 1)]

# s5: exists n in [1,40] with n^2 > 40
out["s5_witnesses"] = [n for n in range(1,41) if n*n > 40][:3]

# s6: n in [1,40], 4|n => n(n+1)/2 even
out["s6_fail"] = [n for n in range(1,41) if n % 4 == 0 and (n*(n+1)//2) % 2 != 0]

# s7: n in [2,40] => n^2 >= 2n
out["s7_fail"] = [n for n in range(2,41) if n*n < 2*n]

# s8: n in [0,40], 16|n => 7^n = 1 mod 17
out["s8_fail"] = [n for n in range(0,41) if n % 16 == 0 and pow(A,n,M) != 1]

# s9: n^3 - n = 120 at n=5
out["s9"] = (5**3 - 5 == 120)

# s10: every n in [0,40] in exactly one residue class mod 16
out["s10_fail"] = [n for n in range(0,41) if len([r for r in range(16) if n % 16 == r]) != 1]

# s11 sufficiency check: does s2's stated range [0,24] plus n<16 triviality
# actually reach every n in [0,40]? Derive reachability by closure.
known = set(range(0,16))            # n < 16: n mod 16 == n, trivially true
changed = True
while changed:
    changed = False
    for n in range(0,25):           # s2 instances, exactly as stated
        if n in known and (n+16) not in known:
            known.add(n+16); changed = True
        if (n+16) in known and n not in known:
            known.add(n); changed = True
out["s11_unreached_in_0_40"] = sorted(set(range(0,41)) - known)

for k, v in out.items():
    print(k, "=", v)
