# Model: f(n) = 7 f(n-1) - 10 f(n-2) mod 1409, fitted from samples f(1..8).
# Closed form solved below. Scan n in [1,600] for f(n) == 296 (mod 1409).
P = 1409
S = {1:31, 2:137, 3:649, 4:355, 5:222, 6:822, 7:716, 8:1019}

# closed form f(n) = A*2^n + B*5^n
# 2A + 5B = 31 ; 4A + 25B = 137  ->  B=5, A=3
A, B = 3, 5
for n in range(1, 9):
    assert (A*pow(2,n,P) + B*pow(5,n,P)) % P == S[n], n
print("closed form f(n) = 3*2^n + 5*5^n mod 1409 matches all 8 samples")

hits = [n for n in range(1, 601) if (A*pow(2,n,P) + B*pow(5,n,P)) % P == 296]
print("n in [1,600] with f(n) == 296 mod 1409:", hits)

# far-point predictions, to be checked against the metered oracle
for n in (100, 401, 600):
    print("predicted f(%d) = %d" % (n, (A*pow(2,n,P)+B*pow(5,n,P)) % P))
