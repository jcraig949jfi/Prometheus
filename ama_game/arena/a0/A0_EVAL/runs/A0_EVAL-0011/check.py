# Verifier: recompute the recurrence and compare against the claimed closed form.
# Exact integer arithmetic (Python int), no floating point.
a = {0: 4, 1: 10}
for n in range(2, 31):
    a[n] = 6*a[n-1] + (-8)*a[n-2]
f = lambda n: 4*(2**n) + 1*(4**n)
bad = [(n, a[n], f(n)) for n in range(0, 31) if a[n] != f(n)]
print("n_checked = 0..30 (31 values), exact integer arithmetic")
print("mismatches:", len(bad))
for n, an, fn in bad[:5]:
    print("  n=%d  a_n=%d  closed_form=%d" % (n, an, fn))
# also test step s3: does the closed form satisfy the recurrence?
s3 = all(f(n+2) == 6*f(n+1) + (-8)*f(n) for n in range(0, 29))
print("s3 (closed form satisfies recurrence on [0,28]):", s3)
# correct closed form A*2^n + B*4^n from the two base cases
# A+B=4, 2A+4B=10 -> B=1? no: A=3,B=1
print("fit check 3*2^n+1*4^n:", all(a[n] == 3*2**n + 4**n for n in range(0, 31)))
