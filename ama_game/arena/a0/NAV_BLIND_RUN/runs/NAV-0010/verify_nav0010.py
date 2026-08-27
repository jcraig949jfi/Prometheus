"""NAV-0010 verification artifact.

Model recovered from 4 metered samples and confirmed against 14 further
metered observations (10 of them out-of-sample, spanning the full domain):

    p = 5003
    f(1) = 43, f(2) = 271
    f(n) = 12*f(n-1) + 4968*f(n-2)   (mod 5003)          [4968 = -35 mod 5003]

Claim: for all n in [1,600], f(n) mod 5003 != 4038.

This script is self-contained and reproduces the disposition without further
metered calls. All metered observations used are listed in OBSERVED and are
re-checked against the model below.
"""
P = 5003
A, B = 12, 4968

# every metered observation made during this run (point -> f(n) mod 5003)
OBSERVED = {
    1: 43, 2: 271, 3: 1747, 4: 1473, 5: 1558, 6: 2162, 7: 1432, 8: 1550,
    37: 4354, 99: 4669, 150: 3892, 233: 2765, 301: 4632, 388: 684,
    450: 3294, 512: 4066, 577: 4112, 600: 3078,
}
# points 1,2 are the seed; 3,4 fixed the two coefficients.
FIT_POINTS = {1, 2, 3, 4}


def model(nmax):
    f = {1: 43, 2: 271}
    for n in range(3, nmax + 1):
        f[n] = (A * f[n - 1] + B * f[n - 2]) % P
    return f


def main():
    f = model(6000)

    # 1. model agrees with every metered observation
    mism = [n for n, v in OBSERVED.items() if f[n] != v]
    print("metered observations:", len(OBSERVED),
          "| out-of-sample:", len(OBSERVED) - len(FIT_POINTS),
          "| mismatches:", mism)
    assert not mism

    # 2. exhaustive check over the stated domain [1,600] under the model
    hits = [n for n in range(1, 601) if f[n] == 4038]
    print("n in [1,600] with f(n) == 4038:", hits)

    # 3. stronger structural fact: the state (f(n),f(n+1)) is purely periodic
    #    with period 5002, and 4038 is not in the value set of the orbit at all.
    s = (43, 271)
    cur, k = s, 0
    while True:
        k += 1
        cur = (cur[1], (A * cur[1] + B * cur[0]) % P)
        if cur == s:
            break
    vals = {f[n] for n in range(1, k + 1)}
    print("state period:", k, "| distinct values in orbit:", len(vals),
          "| 4038 in orbit:", 4038 in vals)

    print()
    print("DISPOSITION: TRUE" if not hits else "DISPOSITION: FALSE")


if __name__ == "__main__":
    main()
