"""
NAV-0016 assessment artifact. Third-party runnable, no metered access needed.

Route:
 1. 8 metered samples at n=1..8 -> fit a constant-coefficient linear recurrence
    over GF(1009). Order 1 and all polynomial models (deg 1..6) are INCONSISTENT.
    Order 2 is consistent and OVERDETERMINED (6 equations, 2 unknowns):
        f(n) = 11*f(n-1) + 979*f(n-2)  (mod 1009),  979 = -30
    Characteristic x^2 - 11x + 30 = (x-5)(x-6)  =>  f(n) = A*5^n + B*6^n.
    Initial conditions give A = 1, B = 3.
 2. ord(5) mod 1009 = 504, ord(6) mod 1009 = 252  =>  f is purely periodic with
    period 504. The domain [1,600] therefore CONTAINS a full period, so the
    proposition over [1,600] is equivalent to "163 is not in the image of f".
 3. 163 is not attained by f at any n. (The image has 378 of the 1009 residues.)
 4. 16 further metered samples spread over [1,600], including both endpoints,
    agree with the closed form exactly: 24/24.
"""
P = 1009

def f(n):
    return (pow(5, n, P) + 3 * pow(6, n, P)) % P

# every metered observation taken during this run (n -> observed f(n) mod 1009)
OBSERVED = {
    1: 23, 2: 133, 3: 773, 4: 477, 5: 219, 6: 207, 7: 752, 8: 44,
    12: 84, 25: 212, 50: 92, 75: 445, 100: 891, 150: 826, 200: 623,
    250: 481, 300: 889, 350: 136, 400: 698, 450: 498, 500: 715,
    550: 598, 599: 502, 600: 274,
}

def order(a):
    k, x = 1, a % P
    while x != 1:
        x = x * a % P
        k += 1
    return k

if __name__ == "__main__":
    mism = [(n, v, f(n)) for n, v in sorted(OBSERVED.items()) if f(n) != v]
    print("observations:", len(OBSERVED), "mismatches:", mism)
    print("recurrence check f(n)=11f(n-1)-30f(n-2):",
          all(f(n) == (11 * f(n - 1) - 30 * f(n - 2)) % P for n in range(3, 2000)))
    print("ord(5)=", order(5), " ord(6)=", order(6), " period=", 504)
    print("f(n+504)==f(n) for n=1..600:",
          all(f(n) == f(n + 504) for n in range(1, 601)))
    hits = [n for n in range(1, 601) if f(n) == 163]
    print("n in [1,600] with f(n)==163:", hits)
    print("163 in image over a full period [1,504]:",
          163 in {f(n) for n in range(1, 505)})
    print("distinct residues attained:", len({f(n) for n in range(1, 505)}))
