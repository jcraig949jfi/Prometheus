# Exhaustive exact-integer check over the full stated domain n in [1,40].
# All arithmetic is Python int (arbitrary precision). No floating point anywhere.
from fractions import Fraction

def F(n): return Fraction(n*(n+1), 2)          # exact rational; denominator 2
def ind(p): return 1 if p else 0

prop_fail = [n for n in range(1,41) if sum(k**1 for k in range(1,n+1)) != F(n)]

# s1: base case n=1
s1 = (sum(k for k in range(1,2)) == 1 and F(1) == 1)
# s2: F(n+1)-F(n) == (n+1)^1 for 1<=n<=39
s2 = [n for n in range(1,40) if F(n+1)-F(n) != (n+1)**1]
# s3: (n-3)n^2 == (n-3)H(n), H(n)=n^2+[n=3]
s3 = [n for n in range(1,41) if (n-3)*n**2 != (n-3)*(n**2 + ind(n==3))]
# s4: (n-3)F(n) == (n-3)G(n), G(n)=F(n)+[n=3]
s4 = [n for n in range(1,41) if (n-3)*F(n) != (n-3)*(F(n) + ind(n==3))]
# s5: every n in [1,40] is even or odd
s5 = [n for n in range(1,41) if not (n%2==0 or n%2==1)]
# s6: n^3 = n mod 6
s6 = [n for n in range(1,41) if (n**3 - n) % 6 != 0]
# s7: n^3 - n == 120 at n=5
s7 = (5**3 - 5 == 120)
# s8: does base+increment actually entail the proposition? replay the telescope.
tele_fail=[]
acc = 1
for n in range(1,40):
    acc = acc + (n+1)          # increment asserted by s2
    if acc != F(n+1): tele_fail.append(n+1)

print("proposition counterexamples:", prop_fail)
print("s1", s1)
print("s2 counterexamples:", s2)
print("s3 counterexamples:", s3)
print("s4 counterexamples:", s4)
print("s5 counterexamples:", s5)
print("s6 counterexamples:", s6)
print("s7", s7)
print("s8 telescope failures:", tele_fail)
print("search size (n values enumerated):", 40)
