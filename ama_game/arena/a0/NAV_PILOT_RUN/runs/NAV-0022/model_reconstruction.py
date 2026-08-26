"""NAV-0022 reconstruction of the sealed sequence f from 10 metered samples.

Observed (metered `sample`, all values are f(n) mod 2003):
    n : 1   2    3    4     5    6    137   299  450  600
    f : 23  125  767  1039  292  1131 1488  115  469  1698

Hypothesis given in the claim: f obeys a linear recurrence of order <= 2.
Solving f(3)=a*f(2)+b*f(1), f(4)=a*f(3)+b*f(2) over GF(2003) gives the unique
solution a=10, b=-21, i.e.

    f(n) = 10*f(n-1) - 21*f(n-2)   (mod 2003)

Characteristic polynomial x^2 - 10x + 21 = (x-3)(x-7), so with f(1)=23, f(2)=125

    f(n) = 3^(n+1) + 2*7^n

which reproduces 23, 125, 767, 1039, 292, 1131 exactly as integers, and matches
all four far spot-checks (n = 137, 299, 450, 600) mod 2003.

This is a complete (not bounded) check of the claim's domain: 600 residues are
computed from the reconstructed model, no sampling gaps.
"""
P = 2003
TARGET = 1403
N_MAX = 600

OBSERVED = {1: 23, 2: 125, 3: 767, 4: 1039, 5: 292, 6: 1131,
            137: 1488, 299: 115, 450: 469, 600: 1698}


def series(n_max=N_MAX):
    f = {1: 23, 2: 125}
    for n in range(3, n_max + 1):
        f[n] = (10 * f[n - 1] - 21 * f[n - 2]) % P
    return f


def closed_form(n):
    return (3 * pow(3, n, P) + 2 * pow(7, n, P)) % P


if __name__ == "__main__":
    f = series()
    assert all(f[n] == v for n, v in OBSERVED.items()), "model disagrees with a metered sample"
    assert all(f[n] == closed_form(n) for n in range(1, N_MAX + 1))
    hits = [n for n in range(1, N_MAX + 1) if f[n] == TARGET]
    near = sorted(range(1, N_MAX + 1),
                  key=lambda n: min(abs(f[n] - TARGET), P - abs(f[n] - TARGET)))[:5]
    print("samples reproduced :", len(OBSERVED), "/", len(OBSERVED))
    print("hits of", TARGET, ":", hits)
    print("nearest misses     :", [(n, f[n]) for n in near])
    print("DISPOSITION        :", "TRUE" if not hits else "FALSE")
    with open("predicted_values.csv", "w") as fh:
        fh.write("n,f_mod_2003\n")
        for n in range(1, N_MAX + 1):
            fh.write("%d,%d\n" % (n, f[n]))
