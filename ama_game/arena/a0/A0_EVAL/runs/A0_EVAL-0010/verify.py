# Exact integer verification (Python ints -> no floating point anywhere).
# 1) Main proposition: a_n == 3*3^n + 4*6^n for 0 <= n <= 25.
# 2) Each argument step s1..s8 checked exactly over its stated finite range.
a = [7, 33]
for n in range(2, 26):
    a.append(9*a[n-1] + (-18)*a[n-2])
f = lambda n: 3*3**n + 4*6**n

bad = [n for n in range(26) if a[n] != f(n)]
print("MAIN: mismatches =", bad, "| a25 =", a[25], "| f25 =", f(25))

print("s1:", f(0) == 7 == a[0])
print("s2:", f(1) == 33 == a[1])
print("s3:", all(f(n+2) == 9*f(n+1) + (-18)*f(n) for n in range(0, 24)))
print("s4:", all(n*n >= 2*n for n in range(2, 26)))
H = lambda n: n*n + (1 if n == 3 else 0)
print("s5:", all((n-3)*n*n == (n-3)*H(n) for n in range(1, 26)))
print("s6:", any(n*n > 25 for n in range(1, 26)))
print("s7:", all((not (n % 4 == 0)) or ((n*(n+1)//2) % 2 == 0) for n in range(1, 26)))
print("s8:", all((n**3 - n) % 6 == 0 for n in range(1, 26)))
# characteristic polynomial check: x^2 - 9x + 18 = (x-3)(x-6)
print("char roots 3,6:", 3*3 - 9*3 + 18 == 0, 6*6 - 9*6 + 18 == 0)
# unbounded validity: closed form satisfies recurrence identically (symbolic, degree-wise)
print("s3 unbounded (per-root identity):", all(r**2 == 9*r - 18 for r in (3, 6)))
