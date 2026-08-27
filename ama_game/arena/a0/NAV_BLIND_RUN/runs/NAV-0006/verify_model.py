"""NAV-0006 model check.

Hypothesis fitted from metered samples: f(n) = 3*4^n + 2^n  (mod 2711).
2711 is prime; ord_2711(2) = 1355.
Solving 3x^2 + x == 732 (mod 2711) with x = 2^n gives x in {1967, 2551};
2551 is not in <2>, and 1967 = 2^1167, so f(n) == 732 iff n == 1167 (mod 1355).
Least such n is 1167 > 600, hence the proposition holds on [1,600].
"""
p = 2711
f = lambda n: (3 * pow(4, n, p) + pow(2, n, p)) % p

OBS = {1:14, 2:52, 3:200, 4:784, 5:393, 6:1508, 7:482, 13:2369, 32:727,
       72:739, 100:2623, 126:733, 150:1835, 177:731, 201:742, 225:2224,
       275:1612, 288:738, 333:1115, 375:590, 426:733, 450:2183, 500:2008,
       527:729, 599:440, 600:1323}

bad = [(n, v, f(n)) for n, v in OBS.items() if f(n) != v]
print("metered points:", len(OBS), "mismatches:", bad)

hit = [n for n in range(1, 601) if f(n) == 732]
print("model n in [1,600] with f(n)==732:", hit)

nxt = [n for n in range(1, 3000) if f(n) == 732][:3]
print("first model solutions overall:", nxt)

near = sorted((min(abs(f(n)-732), p-abs(f(n)-732)), n, f(n)) for n in range(1, 601))[:8]
print("8 closest approaches to 732 in domain (all directly sampled):", near)
print("all 8 near points sampled?", all(n in OBS for _, n, _ in near))
