"""NAV-0025 witness.

Metered observations (the ONLY facts taken from the arena's sealed sequence):
    sample(1)=32  sample(2)=176  sample(3)=992  sample(4)=1695   (values mod 4001)
    evaluate(8) -> holds = false

Hypothesis given in the claim: f obeys a linear recurrence of order <= 2.
Four samples determine it uniquely (mod the prime 4001), so the whole domain
[1,600] becomes computable locally at zero further metered cost.

Fitted:  f(n) = 10*f(n-1) - 24*f(n-2)   (mod 4001)
Char. poly x^2-10x+24 = (x-4)(x-6)  =>  f(n) = 2*4^n + 4*6^n  (exact, over Z)
Predicted f(8) = 2*4^8 + 4*6^8 = 6849536 ; 6849536 mod 4001 = 3825.

The forbidden residue 3825 is therefore hit at n = 8, inside [1,600].
Confirmed independently by the metered verifier: evaluate(8) -> holds=false.
"""
P = 4001
TARGET = 3825
OBS = {1: 32, 2: 176, 3: 992, 4: 1695}

# --- fit the order-2 recurrence from the four metered samples ---------------
det = (OBS[2] * OBS[2] - OBS[1] * OBS[3]) % P
assert det != 0, "degenerate; would need more samples"
dinv = pow(det, P - 2, P)
a = ((OBS[3] * OBS[2] - OBS[1] * OBS[4]) * dinv) % P
b = ((OBS[2] * OBS[4] - OBS[3] * OBS[3]) * dinv) % P
assert (a, b) == (10, 3977), (a, b)          # 3977 == -24 mod 4001

# --- closed form agrees with every metered sample ---------------------------
closed = lambda n: 2 * 4**n + 4 * 6**n
for n, v in OBS.items():
    assert closed(n) % P == v, n

# --- scan the claimed domain locally ---------------------------------------
hits = [n for n in range(1, 601) if closed(n) % P == TARGET]
print("recurrence: f(n) = %d*f(n-1) + %d*f(n-2) mod %d   (i.e. 10,-24)" % (a, b, P))
print("closed form: f(n) = 2*4^n + 4*6^n")
print("f(8) =", closed(8), "-> mod 4001 =", closed(8) % P)
print("n in [1,600] with f(n) mod 4001 == 3825:", hits[:12], "... count =", len(hits))
print("VERDICT: proposition is FALSE; smallest witness n =", hits[0])
