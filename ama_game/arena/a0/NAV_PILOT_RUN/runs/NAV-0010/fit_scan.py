"""NAV-0010 assessment artifact.

Route: the claim's own hypotheses state f satisfies a linear recurrence of order
at most 2.  Such a recurrence is uniquely determined mod p by four consecutive
terms whenever the 2x2 Hankel matrix is invertible.  So 4 metered samples pin
the whole of [1,600]; the remaining 5 samples are held-out validation, two
adjacent (n=5,6) and three far (n=100,350,600).  Total metered cost: 9.

The naive route (range 1 600) costs 600 and is unaffordable under a 120 cap.

All arithmetic is exact integer arithmetic mod 5003.  No floating point is used.
The scan over [1,600] below is exhaustive over the full stated domain -- it is
not a bounded search inside a larger domain.
"""

p = 5003
TARGET = 4038

# --- metered observations (the only facts about f used here) -----------------
obs = {1: 43, 2: 271, 3: 1747, 4: 1473, 5: 1558, 6: 2162,
       100: 3115, 350: 2085, 600: 3078}

# --- fit f(n) = a*f(n-1) + b*f(n-2)  (mod p) from n = 1..4 only --------------
M = [[obs[2], obs[1]], [obs[3], obs[2]]]
r = [obs[3], obs[4]]
det = (M[0][0] * M[1][1] - M[0][1] * M[1][0]) % p
assert det != 0, "Hankel matrix singular; recurrence not pinned by these terms"
inv = pow(det, p - 2, p)
a = ((r[0] * M[1][1] - M[0][1] * r[1]) * inv) % p
b = ((M[0][0] * r[1] - r[0] * M[1][0]) * inv) % p

# --- generate the whole domain ----------------------------------------------
f = {1: obs[1], 2: obs[2]}
for n in range(3, 601):
    f[n] = (a * f[n - 1] + b * f[n - 2]) % p

# --- validation against every held-out metered observation ------------------
held_out = {n: v for n, v in obs.items() if n > 4}
mismatches = {n: (f[n], v) for n, v in held_out.items() if f[n] != v}

# --- closed form: x^2 - 12x + 35 = (x-5)(x-7)  =>  f(n) = 3*5^n + 4*7^n ------
closed_ok = all((3 * pow(5, n, p) + 4 * pow(7, n, p)) % p == v
                for n, v in obs.items())

# --- exhaustive scan of the full domain -------------------------------------
hits = [n for n in range(1, 601) if f[n] == TARGET]
nearest = min(range(1, 601), key=lambda n: min((f[n] - TARGET) % p,
                                               (TARGET - f[n]) % p))

if __name__ == "__main__":
    print("recurrence: f(n) = %d*f(n-1) + %d*f(n-2) mod %d   (b == -%d)"
          % (a, b, p, p - b))
    print("char poly x^2 - 12x + 35 = (x-5)(x-7);  closed form 3*5^n + 4*7^n")
    print("closed form reproduces all 9 metered samples exactly:", closed_ok)
    print("held-out metered points:", sorted(held_out))
    print("held-out mismatches:", mismatches if mismatches else "none")
    print("n in [1,600] with f(n) mod %d == %d: %s (count %d)"
          % (p, TARGET, hits, len(hits)))
    print("nearest approach: n=%d f(n)=%d" % (nearest, f[nearest]))
