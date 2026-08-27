"""NAV-0002 -- reconstruction of the sealed sequence f and decision of the claim.

Claim: for every integer n with 1 <= n <= 600, f(n) mod 1009 is not 848.

All observations of f came through the metered CLI (session A0NAV_BLIND-NAV-0002).
This file contains ONLY observed values and locally-derived arithmetic; it does
not re-implement the sealed generator from any privileged source.

Step 1  (8 metered `sample` calls, n = 1..8) -- observed residues.
Step 2  Fit a linear recurrence mod the prime 1009 by Gaussian elimination.
        Order 2 fits with 6 equations in 2 unknowns (4-fold overdetermined):
            f(n) = 8*f(n-1) - 12*f(n-2)   (mod 1009)
        Characteristic poly x^2 - 8x + 12 = (x-2)(x-6), giving the closed form
            f(n) = 2^(n+1) + 6^n          (mod 1009)
Step 3  ord(2) mod 1009 = 504, ord(6) mod 1009 = 252, so the residue sequence is
        purely periodic with period lcm = 504 <= 600.  The window [1,600]
        therefore contains a COMPLETE period; an exhaustive scan of n = 1..504
        settles the claim for all n, not merely within a bounded window.
Step 4  Exhaustive scan over the full period: 848 never occurs.  393 distinct
        residues are attained; 849 IS attained (n=130) and 846 IS attained
        (n=112), so 848 is a genuine near-miss, not a vacuous target.
Step 5  Model validated against 12 further metered `sample` calls spread across
        [1,600] (incl. n=505 confirming f(505)=f(1)=10, and n=600), plus 2
        metered `evaluate` calls at the two near-miss points n=112 and n=130.
        20/20 sampled residues match the model; 2/2 evaluations hold.

Total metered cost: 22 credits of 120.
All integer arithmetic; no floating point is used anywhere.
"""

P = 1009
TARGET = 848

# --- metered observations (sample: value of f(n) mod 1009) -------------------
OBSERVED = {
    1: 10, 2: 44, 3: 232, 4: 319, 5: 777, 6: 370, 7: 699, 8: 143,   # fitting set
    23: 867, 71: 953, 124: 298, 187: 366, 233: 164, 289: 272,        # validation set
    344: 5, 401: 49, 457: 918, 505: 10, 552: 748, 600: 89,
}
# metered observations (evaluate: does the proposition hold at n)
OBSERVED_EVAL = {112: True, 130: True}


def model(n):
    """Reconstructed closed form: f(n) = 2^(n+1) + 6^n (mod 1009)."""
    return (2 * pow(2, n, P) + pow(6, n, P)) % P


def by_recurrence(limit):
    """Independent path: iterate f(n) = 8 f(n-1) - 12 f(n-2) from f(1), f(2)."""
    f = [None, 10, 44]
    for n in range(3, limit + 1):
        f.append((8 * f[n - 1] - 12 * f[n - 2]) % P)
    return f


def mult_order(a):
    k, x = 1, a % P
    while x != 1:
        x = x * a % P
        k += 1
    return k


def main():
    # (a) the two derivations of the model agree
    f = by_recurrence(600)
    assert all(f[n] == model(n) for n in range(1, 601)), "recurrence != closed form"

    # (b) the model reproduces every metered observation
    mismatch = [(n, model(n), v) for n, v in OBSERVED.items() if model(n) != v]
    assert not mismatch, f"model contradicted by metered samples: {mismatch}"
    ev = [(n, model(n)) for n, h in OBSERVED_EVAL.items()
          if (model(n) != TARGET) != h]
    assert not ev, f"model contradicted by metered evaluations: {ev}"

    # (c) periodicity: the window contains a whole period
    o2, o6 = mult_order(2), mult_order(6)
    from math import gcd
    period = o2 * o6 // gcd(o2, o6)
    assert period == 504 and period <= 600
    assert all(model(n) == model(n + period) for n in range(1, 601 - period + 1))

    # (d) exhaustive scan over the full period -> settles all n >= 1
    hits_period = [n for n in range(1, period + 1) if model(n) == TARGET]
    hits_window = [n for n in range(1, 601) if model(n) == TARGET]

    print(f"ord(2)={o2} ord(6)={o6} period={period}")
    print(f"metered observations reproduced: {len(OBSERVED)} samples, "
          f"{len(OBSERVED_EVAL)} evaluations, 0 mismatches")
    print(f"hits of {TARGET} over full period [1,{period}]: {hits_period}")
    print(f"hits of {TARGET} over claim window [1,600]:    {hits_window}")
    print(f"distinct residues attained in [1,600]: "
          f"{len(set(model(n) for n in range(1,601)))}")
    print(f"near misses: 846 at n=112, 849 at n=130")
    print("DISPOSITION: TRUE" if not hits_window else "DISPOSITION: FALSE")


if __name__ == "__main__":
    main()
