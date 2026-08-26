"""
NAV-0022 verification artifact.

Claim: for every integer n with 1 <= n <= 600, f(n) mod 2003 != 1403.

f is sealed, but the claim's own hypothesis states f satisfies a linear
recurrence of order at most 2. Ten metered observations of f were taken:
  n = 1..6 (fit + first check) and n = 200, 437, 600 (far-field check),
  plus one metered evaluate() at n = 600 (semantic cross-check).

Fitting a homogeneous order-2 recurrence over GF(2003) to n=1..4 gives
  f(n+2) = 10*f(n+1) + 1982*f(n)  (mod 2003),  1982 = -21 mod 2003
whose characteristic polynomial x^2 - 10x + 21 = (x-3)(x-7) yields the
closed form
  f(n) = 3^(n+1) + 2*7^n   (mod 2003).

Every one of the ten observations matches this closed form exactly, including
the three taken far from the fit window. This script re-derives the model,
checks it against all observations, and then exhaustively enumerates the
FULL stated domain n = 1..600 (600 points, complete -- not a bounded sample
of a larger domain) looking for the residue 1403.
"""
P = 2003
TARGET = 1403

# metered observations (point -> f(n) mod 2003), obtained via meter_cli sample
OBS = {1: 23, 2: 125, 3: 767, 4: 1039, 5: 292, 6: 1131,
       200: 39, 437: 348, 600: 1698}

def inv(x): return pow(x, P - 2, P)

# --- refit the order-2 recurrence from the first four observations ---
f1, f2, f3, f4 = OBS[1], OBS[2], OBS[3], OBS[4]
det = (f2 * f2 - f3 * f1) % P
assert det % P != 0, "fit matrix singular"
di = inv(det)
a = ((f3 * f2 - f4 * f1) * di) % P
b = ((f2 * f4 - f3 * f3) * di) % P
print(f"fitted recurrence: f(n+2) = {a}*f(n+1) + {b}*f(n)  (mod {P})")
assert (a, b) == (10, 1982), (a, b)

# --- closed form and agreement with every observation ---
def closed(n): return (pow(3, n + 1, P) + 2 * pow(7, n, P)) % P

# iterate the recurrence over the whole domain
seq = [None, OBS[1], OBS[2]]
for n in range(3, 601):
    seq.append((a * seq[n - 1] + b * seq[n - 2]) % P)

for n, v in sorted(OBS.items()):
    assert seq[n] == v, f"recurrence disagrees with observation at n={n}"
    assert closed(n) == v, f"closed form disagrees with observation at n={n}"
print(f"all {len(OBS)} metered observations reproduced exactly by both forms")
assert all(seq[n] == closed(n) for n in range(1, 601))
print("recurrence and closed form agree on all 600 points")

# --- exhaustive enumeration of the complete stated domain ---
hits = [n for n in range(1, 601) if seq[n] == TARGET]
print(f"points n in [1,600] with f(n) mod {P} == {TARGET}: {hits}  (count {len(hits)})")

dist = min((min((seq[n] - TARGET) % P, (TARGET - seq[n]) % P), n) for n in range(1, 601))
print(f"closest residue approach to {TARGET}: distance {dist[0]} at n={dist[1]} (value {seq[dist[1]]})")
print(f"distinct residues attained on [1,600]: {len(set(seq[1:601]))}")

with open("scan_rows.csv", "w") as fh:
    fh.write("n,f_n_mod_2003,equals_1403\n")
    for n in range(1, 601):
        fh.write(f"{n},{seq[n]},{int(seq[n] == TARGET)}\n")
print("wrote scan_rows.csv (600 rows)")

print("\nDISPOSITION: TRUE" if not hits else f"\nDISPOSITION: FALSE, witness n={hits[0]}")
