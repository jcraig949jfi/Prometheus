"""NAV-0027 route artifact.

Hypothesis given in the claim: f satisfies a linear recurrence of order <= 2.
Therefore 4 consecutive observed values determine the coefficient pair (a, b)
in f(n+2) = a*f(n+1) + b*f(n) (mod 1009) whenever the 2x2 system is
non-singular; 2 further observed values are held out as a check.

Metered observations used (sample, mod 1009):
    f(1)=16 f(2)=80 f(3)=448 f(4)=606 f(5)=481 f(6)=612
Solved:      a=8, b=997 == -12  (unique solution mod 1009)
Held-out check at n=5,6: passes.
Closed form implied: f(n) = 2^(n+1) + 2*6^n   (char. roots 2 and 6)

The full sweep of n in [1,600] is then done LOCALLY at zero metered cost.
Exactly one n in [1,600] has f(n) mod 1009 == 75, namely n=501.
Confirmed on the metered interface: sample(501)=75, evaluate(501)->holds=false.
"""
P = 1009
f = [None, 16, 80]
for n in range(3, 601):
    f.append((8 * f[n - 1] - 12 * f[n - 2]) % P)

assert all(f[n] == (pow(2, n + 1, P) + 2 * pow(6, n, P)) % P for n in range(1, 601))
hits = [n for n in range(1, 601) if f[n] == 75]
if __name__ == "__main__":
    print("witnesses (f(n) mod 1009 == 75):", hits)
    print("f(501) mod 1009 =", f[501])
