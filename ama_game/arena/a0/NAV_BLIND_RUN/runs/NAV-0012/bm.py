P=4001
S=[33,183,1137,3526,3381,3775,2758,318,1276,2081,2016,465,2324,1472,1925,341,2995,2784,954,3089,2854,3681,882,3537]
def bm(s,p):
    C=[1]; B=[1]; L=0; m=1; b=1
    for n in range(len(s)):
        d=s[n]
        for i in range(1,L+1): d=(d+C[i]*s[n-i])%p
        if d==0:
            m+=1
        elif 2*L<=n:
            T=C[:]
            coef=d*pow(b,p-2,p)%p
            while len(C)<len(B)+m: C.append(0)
            for i in range(len(B)): C[i+m]=(C[i+m]-coef*B[i])%p
            L=n+1-L; B=T; b=d; m=1
        else:
            coef=d*pow(b,p-2,p)%p
            while len(C)<len(B)+m: C.append(0)
            for i in range(len(B)): C[i+m]=(C[i+m]-coef*B[i])%p
            m+=1
    return L,C
for k in range(4,len(S)+1):
    L,C=bm(S[:k],P)
    print(k,L)
L,C=bm(S,P)
print("order",L,"C",C[:L+1])
