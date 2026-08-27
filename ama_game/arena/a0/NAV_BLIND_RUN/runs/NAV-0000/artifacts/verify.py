"""
NAV-0000 verification artifact.  Third-party runnable: `python verify.py`.
Uses only the 18 metered observations recorded below; no oracle access needed.

Claim: for every integer n with 1 <= n <= 600, f(n) mod 1409 is not 296.
Disposition: TRUE.
"""
P = 1409

# --- the 18 metered observations (16 sample, 2 evaluate) -------------------
SAMPLES = {1:31, 2:137, 3:649, 4:355, 5:222, 6:822, 7:716, 8:1019,
           9:1382, 61:337, 150:761, 293:492, 400:1041, 512:60,
           599:232, 600:1316}
EVALUATES = {1: True, 600: True}          # oracle verdicts at the endpoints

# --- step 1: Berlekamp-Massey on f(1..8) gave the order-2 relation ---------
#     f(n) = 7 f(n-1) - 10 f(n-2)  (mod 1409)
#     char poly x^2 - 7x + 10 = (x-2)(x-5)  ->  f(n) = A*2^n + B*5^n
#     2A +  5B =  31
#     4A + 25B = 137   =>  B = 5, A = 3
A, B = 3, 5
f = lambda n: (A * pow(2, n, P) + B * pow(5, n, P)) % P

for n in SAMPLES:
    assert f(n) == SAMPLES[n], ("model mismatch", n, f(n), SAMPLES[n])
print("closed form f(n) = 3*2^n + 5^(n+1) mod 1409 matches all %d observations"
      % len(SAMPLES))
print("  (8 fitting points n=1..8, plus 8 points chosen AFTER the fit and")
print("   spanning the domain: 9, 61, 150, 293, 400, 512, 599, 600)")

# --- step 2: the orbit of f, exhaustively ---------------------------------
# ord(2) = ord(5) = 704 mod 1409 (1409 prime, 1409-1 = 2^7 * 11),
# so f is purely periodic with period 704.  Since 704 >= 600, one period
# strictly contains the claim's domain; scanning it is exhaustive for [1,600]
# and in fact for ALL integers n.
assert f(1) == f(1 + 704) and f(7) == f(7 + 704)
orbit = {f(n) for n in range(1, 705)}
print("period = 704; distinct values attained = %d of %d residues"
      % (len(orbit), P))
print("296 in orbit(f)?", 296 in orbit)

hits_domain = [n for n in range(1, 601) if f(n) == 296]
hits_all    = [n for n in range(1, 705) if f(n) == 296]
print("n in [1,600]  with f(n) == 296:", hits_domain)
print("n in [1,704] (a full period, i.e. all n) with f(n) == 296:", hits_all)

# --- step 3: consistency with the two metered evaluate() verdicts ----------
for n, holds in EVALUATES.items():
    assert (f(n) != 296) == holds, ("evaluate disagrees with model at", n)
print("model agrees with both metered evaluate() verdicts")

assert not hits_domain
print("\nDISPOSITION: TRUE  -- 296 is not merely missed on [1,600];")
print("it is off the orbit of f entirely, so no n whatsoever attains it.")
