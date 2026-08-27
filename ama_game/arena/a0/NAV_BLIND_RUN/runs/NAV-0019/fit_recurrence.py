p=3301
vals={1:51,2:309,3:1971,4:3126,5:2305,6:546,7:884,8:1038}
seq=[vals[i] for i in range(1,9)]

def solve(M,y):
    n=len(M); m=len(M[0])
    A=[row[:]+[y[i]] for i,row in enumerate(M)]
    piv=[]; r=0
    for c in range(m):
        pr=None
        for i in range(r,n):
            if A[i][c]%p: pr=i;break
        if pr is None: continue
        A[r],A[pr]=A[pr],A[r]
        inv=pow(A[r][c],p-2,p)
        A[r]=[x*inv%p for x in A[r]]
        for i in range(n):
            if i!=r and A[i][c]%p:
                f=A[i][c]
                A[i]=[(A[i][j]-f*A[r][j])%p for j in range(m+1)]
        piv.append(c); r+=1
        if r==n: break
    # check consistency
    for i in range(r,n):
        if all(A[i][j]%p==0 for j in range(m)) and A[i][m]%p:
            return None
    sol=[0]*m
    for i,c in enumerate(piv): sol[c]=A[i][m]
    return sol

for order in range(1,5):
    # f(n+order) = sum c_j f(n+j)
    rows=[];ys=[]
    for start in range(0,len(seq)-order):
        rows.append(seq[start:start+order]); ys.append(seq[start+order])
    if len(rows)<order: continue
    s=solve(rows,ys)
    if s is None: print(order,"inconsistent"); continue
    # verify full
    ok=True
    for start in range(0,len(seq)-order):
        pred=sum(s[j]*seq[start+j] for j in range(order))%p
        if pred!=seq[start+order]: ok=False
    print(order,s,"verified" if ok else "FAIL")

# also try affine order1/2 (with constant)
for order in range(1,4):
    rows=[];ys=[]
    for start in range(0,len(seq)-order):
        rows.append(seq[start:start+order]+[1]); ys.append(seq[start+order])
    s=solve(rows,ys)
    if s is None: print("affine",order,"inconsistent"); continue
    ok=all(( sum(s[j]*seq[st+j] for j in range(order))+s[order])%p==seq[st+order] for st in range(0,len(seq)-order))
    print("affine",order,s,"verified" if ok else "FAIL")

# polynomial in n?
import itertools
def polyfit(deg):
    rows=[];ys=[]
    for n in range(1,deg+2):
        rows.append([pow(n,k,p) for k in range(deg+1)]); ys.append(vals[n])
    s=solve(rows,ys)
    if s is None: return None
    ok=all(sum(s[k]*pow(n,k,p) for k in range(deg+1))%p==vals[n] for n in range(1,9))
    return s if ok else None
for d in range(1,8):
    r=polyfit(d)
    if r: print("poly deg",d,r)
