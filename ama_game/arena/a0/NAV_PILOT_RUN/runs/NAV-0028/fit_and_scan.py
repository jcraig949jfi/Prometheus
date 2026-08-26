# Fit an order-<=2 linear recurrence over GF(1009) to observed f(1..5),
# then enumerate f(n) mod 1009 for n in [1,600] and search for the value 612.
P = 1009
obs = {1: 12, 2: 32, 3: 96, 4: 320, 5: 143}

def inv(x): return pow(x, P - 2, P)

# f(3) = a f(2) + b f(1)
# f(4) = a f(3) + b f(2)
m11, m12, r1 = obs[2], obs[1], obs[3]
m21, m22, r2 = obs[3], obs[2], obs[4]
det = (m11 * m22 - m12 * m21) % P
print("det =", det)
assert det != 0, "singular: need more samples / lower order"
a = ((r1 * m22 - m12 * r2) * inv(det)) % P
b = ((m11 * r2 - r1 * m21) * inv(det)) % P
print("recurrence: f(n) = %d*f(n-1) + %d*f(n-2)  (mod %d)" % (a, b, P))

# holdout check against f(5), which was NOT used in the fit
pred5 = (a * obs[4] + b * obs[3]) % P
print("predicted f(5) =", pred5, " observed f(5) =", obs[5], " match:", pred5 == obs[5])

seq = {1: obs[1], 2: obs[2]}
for n in range(3, 601):
    seq[n] = (a * seq[n - 1] + b * seq[n - 2]) % P
hits = [n for n in range(1, 601) if seq[n] == 612]
print("predicted hits of 612 in [1,600]:", hits[:20], "count:", len(hits))
print("first few terms:", [seq[n] for n in range(1, 11)])
# period detection
for n in range(3, 601):
    if seq[n] == seq[1] and seq[n + 1 if n < 600 else n] == seq[2] and n < 600:
        print("period candidate:", n - 1); break
