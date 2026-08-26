# Recovered model for the sealed sequence f.
# From 5 metered samples f(1..5) mod 4001 = 21, 89, 381, 1649, 3220
# the order-2 linear recurrence f(n) = 9 f(n-1) - 20 f(n-2) fits exactly,
# with closed form f(n) = 4^(n+1) + 5^n.
P = 4001
TARGET = 1554
seq = {}
a, b = 21, 89          # f(1), f(2)
seq[1], seq[2] = a, b
for n in range(3, 601):
    a, b = b, (9*b - 20*a) % P
    seq[n] = b
# cross-check closed form
for n in range(1, 601):
    assert seq[n] == (pow(4, n+1, P) + pow(5, n, P)) % P, n
hits = [n for n in range(1, 601) if seq[n] == TARGET]
print("samples check:", [seq[n] for n in range(1, 6)])
print("hits for f(n) mod 4001 == 1554 in [1,600]:", hits)
print("first few values:", [seq[n] for n in range(1, 12)])
