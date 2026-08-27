# Model fit + full-domain scan for NAV-0023
# Observed samples f(n) mod 4001 for n=1..10 via the metered interface:
obs = {1:21, 2:89, 3:381, 4:1649, 5:3220, 6:1, 7:3626, 8:606, 9:951, 10:440}
M = 4001

# Berlekamp-Massey style order-2 fit over Q using the first four terms:
# 381 = 89a + 21b ; 1649 = 381a + 89b  ->  a=9, b=-20
# char poly x^2 - 9x + 20 = (x-4)(x-5) -> f(n) = A*4^n + B*5^n
# 4A+5B=21, 16A+25B=89 -> A=4, B=1  =>  f(n) = 4^(n+1) + 5^n
def model(n):
    return (pow(4, n+1, M) + pow(5, n, M)) % M

ok = all(model(n) == v for n, v in obs.items())
print("model f(n) = 4^(n+1) + 5^n  mod 4001")
print("matches all 10 observed samples:", ok)
for n, v in sorted(obs.items()):
    print(f"  n={n:2d} observed={v:4d} model={model(n):4d} {'ok' if model(n)==v else 'MISMATCH'}")

hits = [n for n in range(1, 601) if model(n) == 1554]
print("n in [1,600] with model(n) == 1554:", hits)

# period of the model mod 4001 (4001 prime; multiplicative orders)
def order(a, m):
    k = 1; x = a % m
    while x != 1:
        x = x * a % m; k += 1
    return k
o4, o5 = order(4, M), order(5, M)
print("ord(4)=", o4, " ord(5)=", o5)
