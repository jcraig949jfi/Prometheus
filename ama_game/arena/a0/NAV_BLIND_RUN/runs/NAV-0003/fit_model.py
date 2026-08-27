"""NAV-0003 witness reconstruction.

Six metered samples of f (mod 2003) were taken at n = 1..6:
    15, 39, 105, 291, 825, 376
A two-term exponential ansatz f(n) = a*3^n + b*2^n was fitted from n=1,2
(3a+2b=15, 9a+4b=39  =>  a=3, b=3), i.e.

    f(n) = 3^(n+1) + 3*2^n

and it reproduced all six observed samples exactly, including the wrap at n=6
(2379 mod 2003 = 376). Under that model the congruence f(n) = 364 (mod 2003)
has exactly one solution in [1, 600]: n = 243.

Two further metered calls confirmed the model's prediction on the real object:
    sample(243)   -> 364
    evaluate(243) -> holds: false

Total metered cost: 8 of 120 credits.
"""
M = 2003
f = lambda n: (pow(3, n + 1, M) + 3 * pow(2, n, M)) % M

OBSERVED = {1: 15, 2: 39, 3: 105, 4: 291, 5: 825, 6: 376, 243: 364}

if __name__ == "__main__":
    for n, v in OBSERVED.items():
        assert f(n) == v, (n, f(n), v)
    print("model matches all 7 metered observations")
    hits = [n for n in range(1, 601) if f(n) == 364]
    print("n in [1,600] with f(n) %% 2003 == 364:" % (), hits)
    assert hits == [243]
