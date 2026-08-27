"""NAV-0031 reconstruction artifact.

Observed via the metered interface (sample), 8 points, cost 8:
  f(1..8) mod 4001 = 23, 151, 1037, 3218, 2441, 923, 2140, 2337

Berlekamp-Massey-style fit over GF(4001): the minimal order-2 linear
recurrence through those 8 terms is
      f(n+2) = 9*f(n+1) - 14*f(n)   (mod 4001)
char. poly x^2 - 9x + 14 = (x-2)(x-7), so with f(1)=23, f(2)=151:
      f(n) = 2^n + 3*7^n            (mod 4001)

Scanning that closed form over the full stated domain 1 <= n <= 600
(no metered cost -- pure local arithmetic) gives exactly one n with
f(n) == 1243, namely n = 514.

The witness was then confirmed against the sealed sequence with two
metered calls: sample(514) -> 1243 and evaluate(514) -> holds=false.
Total metered cost: 10.
"""
P = 4001
OBS = {1: 23, 2: 151, 3: 1037, 4: 3218, 5: 2441, 6: 923, 7: 2140, 8: 2337}


def f(n):
    return (pow(2, n, P) + 3 * pow(7, n, P)) % P


def main():
    for n, v in OBS.items():
        assert f(n) == v, (n, f(n), v)
    for n in range(1, 599):
        assert f(n + 2) == (9 * f(n + 1) - 14 * f(n)) % P
    hits = [n for n in range(1, 601) if f(n) == 1243]
    print("model agrees with all 8 metered observations")
    print("n in [1,600] with f(n) mod 4001 == 1243:", hits)
    print("f(514) mod 4001 =", f(514))
    assert hits == [514]
    print("PROPOSITION IS FALSE; witness n=514")


if __name__ == "__main__":
    main()
