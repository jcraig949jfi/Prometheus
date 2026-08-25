# Exhaustive check over the FULL stated domain [1, 2839]: no sampling, no bound short of the domain.
def steps(n):
    c = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        c += 1
    return c

worst_n, worst_s = 1, 0
viol = []
for n in range(1, 2840):
    s = steps(n)
    if s > worst_s:
        worst_n, worst_s = n, s
    if s >= 209:
        viol.append((n, s))

print("domain 1..2839 exhaustively checked, count =", 2839)
print("max stopping time:", worst_s, "at n =", worst_n)
print("violations (steps >= 209):", viol)
print("claim (all < 209) holds:", not viol)
# margin probe: first n above the domain that breaks 209
n = 2840
while True:
    if steps(n) >= 209:
        print("first n > 2839 with steps >= 209:", n, steps(n)); break
    n += 1
    if n > 4000: print("none up to 4000"); break

# argument step audit (all finite, exhaustive on their own stated ranges)
H = lambda n: n*n + (1 if n == 3 else 0)
print("s3:", all((n-3)*n*n == (n-3)*H(n) for n in range(1, 2001)))
print("s4:", all(n*n >= 2*n for n in range(2, 2001)))
print("s5:", 5**3 - 5 == 120)
print("s6:", all((n*(n+1)//2) % 2 == 0 for n in range(1, 2001) if n % 4 == 0))
print("s7:", any(n*n > 2000 for n in range(1, 2001)))
print("s8:", all((n**3 - n) % 6 == 0 for n in range(1, 2001)))
