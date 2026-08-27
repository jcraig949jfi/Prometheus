"""NAV-0004 reproduction artifact.

Fitted model for the sealed sequence, recovered from 6 metered samples:
    f(n) = 4*5^n + 3*6^n   (mod 2711)
equivalently the order-2 recurrence  f(n+2) = 11*f(n+1) - 30*f(n)  (mod 2711),
characteristic polynomial x^2 - 11x + 30 = (x-5)(x-6).

2711 is prime; ord(5) = ord(6) = 1355, so the sequence is purely periodic with
period 1355. The residue 1673 does not occur ANYWHERE in that full period, hence
in particular not on 1 <= n <= 600.

Run: python model_check.py
"""
M = 2711
TARGET = 1673

def f(n):
    return (4 * pow(5, n, M) + 3 * pow(6, n, M)) % M

# 16 metered observations (sample(n) -> f(n) mod 2711), 6 used to fit, 10 held out.
OBS = {1: 38, 2: 208, 3: 1148, 4: 966, 5: 585, 6: 1854, 7: 133, 40: 2553,
       111: 2047, 157: 1661, 243: 1682, 337: 1274, 423: 1687, 463: 1665,
       545: 1677, 600: 1890}

if __name__ == "__main__":
    assert all(M % p for p in range(2, 53)), "2711 prime"
    mism = [(n, v, f(n)) for n, v in OBS.items() if f(n) != v]
    print("observations:", len(OBS), "mismatches:", mism)
    print("recurrence holds on fitted model:",
          all((11 * f(n + 1) - 30 * f(n)) % M == f(n + 2) for n in range(1, 3000)))
    hits_domain = [n for n in range(1, 601) if f(n) == TARGET]
    hits_period = [n for n in range(1, 1356) if f(n) == TARGET]
    print("hits of 1673 in [1,600]:", hits_domain)
    print("hits of 1673 over the full period [1,1355]:", hits_period)
    near = sorted(range(1, 601), key=lambda n: abs(f(n) - TARGET))[:5]
    print("closest approaches in [1,600]:", [(n, f(n)) for n in near])
