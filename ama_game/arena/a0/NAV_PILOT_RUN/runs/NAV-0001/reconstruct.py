"""Reconstruct f mod 1009 from the fitted order-2 recurrence and scan for residue 17.

Fitted from metered samples f(1..4) = 41,257,730,954 ; held-out check f(5)=384.
Unique solution over GF(1009): f(n) = 9*f(n-1) - 14*f(n-2)  (b = 995 = -14).
Closed form (exact integers): f(n) = 3*2^n + 5*7^n  (char roots 2 and 7).
"""
P = 1009
f = {1: 41, 2: 257}
for n in range(3, 601):
    f[n] = (9 * f[n - 1] + 995 * f[n - 2]) % P

# independent cross-check via the closed form
for n in range(1, 601):
    assert f[n] == (3 * pow(2, n, P) + 5 * pow(7, n, P)) % P, n

hits = [n for n in range(1, 601) if f[n] == 17]
print("residue-17 hits in [1,600]:", hits[:20], "count:", len(hits))
if hits:
    for n in hits[:5]:
        print("n=%d f(n) mod 1009 = %d  (closed form 3*2^n+5*7^n)" % (n, f[n]))
period = None
for p in range(1, 2100):
    if f.get(1) is not None and all(f[n] == f[n + p] for n in range(1, 601 - p)) and p < 600:
        period = p
        break
print("apparent period within window:", period)
