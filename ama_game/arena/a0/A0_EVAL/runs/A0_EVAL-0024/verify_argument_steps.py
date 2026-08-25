# Exhaustively check argument steps s2,s3,s5,s6,s7 as literally stated. Exact integers.
def st(n):
    c = 0
    while n != 1:
        n = n//2 if n % 2 == 0 else 3*n+1
        c += 1
    return c

s2 = all(st(n) < 443 for n in range(1, 2355))
s3 = all(n*n >= 2*n for n in range(2, 2001))
s5 = all((n**3 - n) % 6 == 0 for n in range(1, 2001))
H  = lambda n: n*n + (1 if n == 3 else 0)
s6 = all((n-3)*n*n == (n-3)*H(n) for n in range(1, 2001))
s7 = (5**3 - 5 == 120)
print("s2 sweep [1,2354] all < 443 :", s2)
print("s3 n^2>=2n on [2,2000]      :", s3)
print("s5 n^3 = n mod 6 on [1,2000]:", s5)
print("s6 (n-3)n^2=(n-3)H(n)       :", s6)
print("s7 5^3-5 == 120             :", s7)
# Does anything in s1..s7 constrain n > 2354? Largest n any step speaks about:
print("largest n mentioned by s1-s7: 2354 ; domain upper end: 372001")
print("uncovered portion of domain :", 372001 - 2354, "integers")
