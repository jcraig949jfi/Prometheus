import itertools
M=2711
s={1:22,2:124,3:712,4:1433,5:2664,6:381,7:2227,8:2282}
xs=[s[i] for i in range(1,9)]
def solve(A,b):
    # gaussian elim mod prime M
    n=len(A); m=len(A[0])
    A=[row[:]+[b[i]] for i,row in enumerate(A)]
    piv=[]
    r=0
    for c in range(m):
        p=None
        for i in range(r,n):
            if A[i][c]%M: p=i;break
        if p is None: continue
        A[r],A[p]=A[p],A[r]
        inv=pow(A[r][c],M-2,M)
        A[r]=[(v*inv)%M for v in A[r]]
        for i in range(n):
            if i!=r and A[i][c]%M:
                f=A[i][c]
                A[i]=[(A[i][j]-f*A[r][j])%M for j in range(m+1)]
        piv.append(c); r+=1
        if r==n: break
    # check consistency
    for i in range(r,n):
        if all(v%M==0 for v in A[i][:m]) and A[i][m]%M: return None
    x=[0]*m
    for i,c in enumerate(piv): x[c]=A[i][m]%M
    return x
for order in (1,2,3):
    for const in (0,1):
        m=order+const
        rows=[];bs=[]
        for n in range(1,9-order):
            row=[xs[n-1+k] for k in range(order)]
            if const: row=row+[1]
            rows.append(row); bs.append(xs[n-1+order])
        if len(rows)<m: continue
        sol=solve(rows,bs)
        if sol is None: continue
        # verify all
        ok=True
        for n in range(1,9-order):
            v=sum(sol[k]*xs[n-1+k] for k in range(order))+(sol[order] if const else 0)
            if v%M!=xs[n-1+order]%M: ok=False;break
        print(order,const,sol,"VERIFIED" if ok else "no")
