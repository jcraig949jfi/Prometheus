"""NAV-0018 reconstruction artifact.

Model fitted from metered samples: f(n) = 4*4^n + 5*7^n  (mod 3301),
equivalently the order-2 linear recurrence
    f(n+2) = 11*f(n+1) - 28*f(n)  (mod 3301),  f(1)=51, f(2)=309,
char. poly x^2 - 11x + 28 = (x-4)(x-7).

Run: python model_check.py
"""
P = 3301

def f(n):
    return (4 * pow(4, n, P) + 5 * pow(7, n, P)) % P

# every value observed through the metered interface (16 metered samples)
OBSERVED = {
    1: 51, 2: 309, 3: 1971, 4: 3126, 5: 2305, 6: 546, 7: 884, 8: 1038,
    50: 1913, 137: 1291, 213: 1087, 300: 2951, 377: 341, 451: 752,
    528: 2703, 600: 984,
}

def main():
    bad = [(n, v, f(n)) for n, v in OBSERVED.items() if f(n) != v]
    print("observed points:", len(OBSERVED), "mismatches:", bad)
    assert not bad

    # independent cross-check: iterate the recurrence rather than the closed form
    a, b = 51, 309
    seq = {1: a, 2: b}
    for n in range(3, 601):
        a, b = b, (11 * b - 28 * a) % P
        seq[n] = b
    assert all(seq[n] == f(n) for n in range(1, 601))

    hits_domain = [n for n in range(1, 601) if f(n) == 1436]
    print("n in [1,600] with f(n) == 1436:", hits_domain)

    # the sequence is purely periodic; period = lcm(ord(4), ord(7)) mod 3301
    def order(a):
        o, x = 1, a % P
        while x != 1:
            x = x * a % P
            o += 1
        return o
    import math
    per = math.lcm(order(4), order(7))
    hits_all = [n for n in range(1, per + 1) if f(n) == 1436]
    print("period:", per, "-- occurrences of 1436 over a full period:", hits_all)
    print("DISPOSITION: TRUE" if not hits_domain else "DISPOSITION: FALSE")

if __name__ == "__main__":
    main()
