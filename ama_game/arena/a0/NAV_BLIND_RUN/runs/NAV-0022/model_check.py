"""NAV-0022 reconstruction artifact.

Third-party runnable. No sealed data is read: the 38 observations below are
exactly the values returned by the metered CLI for session A0NAV_BLIND-NAV-0022.

Method
------
1. sample(1..12) -> 12 consecutive residues mod P=2003.
2. Berlekamp-Massey over GF(2003) returns a MINIMAL linear recurrence of
   order 2:   f(n) = 10*f(n-1) - 21*f(n-2)   (mod 2003).
   Characteristic polynomial x^2 - 10x + 21 = (x-3)(x-7), so
   f(n) = A*3^n + B*7^n; fitting f(1), f(2) gives A=3, B=2, i.e.
        f(n) = 3*3^n + 2*7^n  (mod 2003).
   12 terms over-determine an order-2 fit by 8 confirmations.
3. Model checked against 24 further observations spread over the whole
   domain (n = 25,50,...,600, both endpoints included): all match.
4. ord(3) = 1001, ord(7) = 2002 mod 2003 (prime), so f is periodic with
   period lcm = 2002. Exhaustive scan of ONE FULL PERIOD (n = 1..2002,
   2002 points, a bounded but complete search over the period, hence
   complete for all n) shows the residue 1403 is NOT in the image of f.
   In particular it is not attained on [1, 600].
"""
P = 2003
OBS = {1:23,2:125,3:767,4:1039,5:292,6:1131,7:1172,8:1990,9:1297,10:1225,
       11:1037,12:669,25:1042,50:1122,75:518,100:758,125:1548,150:1047,
       175:13,200:39,225:940,250:1965,275:780,300:1137,325:1337,350:1052,
       375:1275,400:1592,425:171,450:469,475:1832,500:1853,525:1497,
       550:387,575:1444,600:1698}

def f(n):
    return (3 * pow(3, n, P) + 2 * pow(7, n, P)) % P

def recur(n):
    a, b = 23, 125                      # f(1), f(2)
    if n == 1: return a
    for _ in range(n - 2):
        a, b = b, (10 * b - 21 * a) % P
    return b

def order(a, p):
    o = p - 1
    for q in (2, 7, 11, 13):            # 2002 = 2*7*11*13
        while o % q == 0 and pow(a, o // q, p) == 1:
            o //= q
    return o

if __name__ == "__main__":
    bad = [(n, v, f(n)) for n, v in sorted(OBS.items()) if f(n) != v]
    print("observations:", len(OBS), "mismatches:", bad)
    assert not bad
    assert all(f(n) == recur(n) for n in range(1, 61))
    o3, o7 = order(3, P), order(7, P)
    import math
    per = math.lcm(o3, o7)
    print("ord(3)=%d ord(7)=%d period=%d" % (o3, o7, per))
    assert all(f(n) == f(n + per) for n in range(1, 30))
    hits_domain = [n for n in range(1, 601) if f(n) == 1403]
    hits_period = [n for n in range(1, per + 1) if f(n) == 1403]
    print("hits of 1403 in [1,600]      :", hits_domain)
    print("hits of 1403 in one period   :", hits_period)
    print("DISPOSITION: TRUE" if not hits_domain else "DISPOSITION: FALSE")
