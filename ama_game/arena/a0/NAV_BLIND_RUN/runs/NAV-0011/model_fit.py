"""NAV-0011 reconstruction artifact.
20 metered sample() calls at n=1..20 gave f(n) mod 4001. Gaussian elimination
over GF(4001) for a homogeneous linear recurrence found an order-2 fit at the
minimal order tried that admits one:  f(n) = 10*f(n-1) - 21*f(n-2)  (mod 4001),
characteristic roots 3 and 7, closed form f(n) = 4*3^n + 5*7^n (mod 4001).
Extrapolating over the full stated domain 1..600 gives exactly one n with
f(n) mod 4001 == 1372, namely n = 243. Confirmed by metered sample(243)=1372
and evaluate(243) -> holds=false.
"""
P = 4001
OBS = [47,281,1823,326,986,3014,1432,3039,318,3377,
       3086,3954,2741,390,2353,3337,3962,1551,325,2687]  # n = 1..20, metered

f = [0, 47, 281]
for n in range(3, 601):
    f.append((10*f[n-1] - 21*f[n-2]) % P)

assert f[1:21] == OBS, "recurrence disagrees with metered observations"
assert all(f[n] == (4*pow(3, n, P) + 5*pow(7, n, P)) % P for n in range(1, 601))

hits = [n for n in range(1, 601) if f[n] == 1372]
if __name__ == "__main__":
    print("witnesses in [1,600]:", hits)          # -> [243]
    print("f(243) mod 4001 =", f[243])            # -> 1372
