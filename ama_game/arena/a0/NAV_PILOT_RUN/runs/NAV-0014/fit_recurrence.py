"""NAV-0014 assessment artifact.

Claim: for every integer n with 1 <= n <= 600, f(n) mod 1409 is not 379.

Hypothesis given in the claim: f satisfies a linear recurrence of order at
most 2. Strategy: pay for a small number of metered samples, fit the
recurrence over GF(1409), validate the fit on points that were NOT used to
fit it (including three far-out points), then enumerate all 600 residues
locally at zero metered cost.

Metered observations actually purchased (10 calls total, per the harness
ledger; values reproduced verbatim below):

  sample  n=1   -> 39
  sample  n=2   -> 207
  sample  n=3   -> 1161
  sample  n=4   -> 1087
  sample  n=5   -> 157
  sample  n=6   -> 164
  sample  n=200 -> 1237
  sample  n=400 -> 1347
  sample  n=600 -> 228
  evaluate n=57 -> holds: true   (the closest approach to 379 in the model)

Only n=1..4 were used to fit; every other observation is an out-of-fit test.
This is an EXHAUSTIVE finite check over the full stated domain n in [1,600]
under the fitted model -- not a bounded search: the domain is finite and all
600 points are enumerated. Arithmetic is exact integer arithmetic mod 1409
(1409 is prime); no floating point is used anywhere.
"""

P = 1409
TARGET = 379

fit_obs = {1: 39, 2: 207, 3: 1161, 4: 1087}
holdout_obs = {5: 157, 6: 164, 200: 1237, 400: 1347, 600: 228}

# --- fit f(n) = a*f(n-1) + b*f(n-2) over GF(P) from n = 1..4 ---------------
m11, m12, r1 = fit_obs[2], fit_obs[1], fit_obs[3]
m21, m22, r2 = fit_obs[3], fit_obs[2], fit_obs[4]
det = (m11 * m22 - m12 * m21) % P
assert det != 0, "singular system: order-2 fit underdetermined, buy more samples"
inv = pow(det, P - 2, P)          # P prime => Fermat inverse
a = ((r1 * m22 - m12 * r2) * inv) % P
b = ((m11 * r2 - r1 * m21) * inv) % P
print("fitted recurrence: f(n) = %d*f(n-1) + %d*f(n-2)  (mod %d)" % (a, b, P))

# --- generate the whole domain locally ------------------------------------
seq = {1: fit_obs[1], 2: fit_obs[2]}
for n in range(3, 601):
    seq[n] = (a * seq[n - 1] + b * seq[n - 2]) % P

# --- out-of-fit validation -------------------------------------------------
ok = True
for n in sorted(fit_obs.keys() | holdout_obs.keys()):
    observed = fit_obs.get(n, holdout_obs.get(n))
    tag = "fit" if n in fit_obs else "HELD OUT"
    match = seq[n] == observed
    ok &= match
    print("  n=%-4d model=%-5d metered=%-5d %-9s %s"
          % (n, seq[n], observed, tag, "OK" if match else "MISMATCH"))
assert ok, "model disagrees with a metered observation; do not trust the scan"

# --- exhaustive enumeration of the stated domain --------------------------
hits = [n for n in range(1, 601) if seq[n] == TARGET]
near = [(n, seq[n]) for n in range(1, 601) if abs(seq[n] - TARGET) <= 3]
print("hits with f(n) mod %d == %d over n in [1,600]: %s" % (P, TARGET, hits))
print("closest approaches (|f(n)-%d| <= 3): %s" % (TARGET, near))
print("DISPOSITION:", "TRUE (no witness exists in domain)" if not hits
      else "FALSE, witness n=%d" % hits[0])
