# Verifier 1: full check of the proposition and of each argument step over the stated domain.
bad = [n for n in range(0, 81) if pow(3, n, 13) != pow(3, n % 3, 13)]
print("proposition counterexamples in [0,80]:", bad)
print("order of 3 mod 13:", next(k for k in range(1, 13) if pow(3, k, 13) == 1))
# s1: "At n = 1 both sides equal 1 modulo 13."
print("s1 at n=1: lhs 3^1 mod 13 =", pow(3,1,13), " rhs 3^(1 mod 3) mod 13 =", pow(3,1%3,13), " claimed value 1 ->", (pow(3,1,13)==1 and pow(3,1%3,13)==1))
# s2
print("s2:", all(pow(3,n+3,13)==pow(3,n,13) for n in range(0,78)))
# s3
print("s3:", all(n*n>=2*n for n in range(2,81)))
# s4
print("s4:", 5**3-5==120)
# s5
print("s5:", all(pow(3,n,13)==1 for n in range(0,81) if n%3==0))
# s6
print("s6:", any(n*n>80 for n in range(1,81)))
# s7
print("s7:", all((n*(n+1)//2)%2==0 for n in range(1,81) if n%4==0))
# s8
H = lambda n: n*n + (1 if n==3 else 0)
print("s8:", all((n-3)*n*n == (n-3)*H(n) for n in range(1,81)))
# s9 is a tautology; s10 is the conclusion step.
