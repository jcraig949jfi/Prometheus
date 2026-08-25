# Exact integer arithmetic throughout (Python ints). No floating point used.
res = {}
# Main proposition: for all n in [0,60], 3^n = 3^(n mod 6) (mod 7)
res['main'] = [n for n in range(0,61) if pow(3,n,7) != pow(3,n%6,7)]
# order of 3 mod 7
ordv = min(k for k in range(1,7) if pow(3,k,7)==1)
res['order_3_mod_7'] = ordv
res['powers_cycle'] = [pow(3,k,7) for k in range(0,7)]
# s1
res['s1'] = (pow(3,0,7)==1)
# s2: for all n in [0,54], 3^(n+6) = 3^n (mod 7)
res['s2_fail'] = [n for n in range(0,55) if pow(3,n+6,7)!=pow(3,n,7)]
# s3: n^3-n=120 at n=5
res['s3'] = (5**3-5==120)
# s3b: is n^3-n=120 an identity? check other n
res['s3_as_identity_fails_at'] = [n for n in range(0,10) if n**3-n!=120][:5]
# s4: n^3 = n mod 6 for 1<=n<=60
res['s4_fail'] = [n for n in range(1,61) if (n**3-n)%6!=0]
# s5: 4|n -> n(n+1)/2 even
res['s5_fail'] = [n for n in range(1,61) if n%4==0 and (n*(n+1)//2)%2!=0]
# s6
res['s6'] = any(n*n>60 for n in range(1,61))
# s7: each n in [0,60] in exactly one class mod 6
res['s7'] = all(len([r for r in range(6) if n%6==r])==1 for n in range(0,61))
# s8: (n-3)*n^2 == (n-3)*H(n), H(n)=n^2+[n==3]
res['s8_fail'] = [n for n in range(1,61) if (n-3)*n**2 != (n-3)*(n**2+(1 if n==3 else 0))]
# s9 reduction check: repeated subtraction of 6 lands on n mod 6 for all n in [0,60]
def reduce6(n):
    while n>=6: n-=6
    return n
res['reduction_ok'] = all(reduce6(n)==n%6 for n in range(0,61))
for k,v in res.items(): print(k,'=',v)
