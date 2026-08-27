"""NAV-0005: fit f from 20 metered samples, predict n in [1,600], locate f(n)==303 mod 4001."""
P = 4001
obs = {1:28,2:116,3:532,4:2564,5:625,6:2741,7:934,8:3134,9:595,10:832,
       11:3875,12:2801,13:862,14:2030,15:1589,16:2826,17:3892,18:2985,19:1980,20:14}

# Berlekamp-Massey on obs[1..20] gives connection poly [1, 3994, 10]  ->  f(n) = 7 f(n-1) - 10 f(n-2)
# char poly x^2 - 7x + 10 = (x-2)(x-5); solving 2A+5B=28, 4A+25B=116 -> A=B=4
def closed(n): return 4 * (pow(2, n, P) + pow(5, n, P)) % P
def rec(N):
    a, b = obs[1], obs[2]
    out = {1: a, 2: b}
    for n in range(3, N+1):
        a, b = b, (7*b - 10*a) % P
        out[n] = b
    return out

R = rec(600)
assert all(closed(n) == R[n] for n in range(1, 601)), "closed form != recurrence"
mism = [n for n in obs if obs[n] != closed(n)]
print("samples mismatching closed form 4*(2^n+5^n) mod 4001:", mism)

hits = [n for n in range(1, 601) if closed(n) == 303]
print("predicted n in [1,600] with f(n) mod 4001 == 303:", hits)
print("period of 4*(2^n+5^n) mod 4001 (mult order 2):", next(k for k in range(1,4001) if pow(2,k,P)==1), 
      "order 5:", next(k for k in range(1,4001) if pow(5,k,P)==1))
if hits:
    print("first witness:", hits[0], "value:", closed(hits[0]))
