M=1409
# closed form derived from recurrence f(n)=10f(n-1)-24f(n-2), f(1)=30,f(2)=156 -> f(n)=3(4^n+6^n)
seq={}
x,y=30%M,156%M
seq[1],seq[2]=x,y
for n in range(3,601):
    x,y=y,(10*y-24*x)%M
    seq[n]=y
# cross-check closed form
bad=[n for n in range(1,601) if seq[n]!=(3*(pow(4,n,M)+pow(6,n,M)))%M]
print("closed-form mismatches:",bad)
hits=[n for n in range(1,601) if seq[n]==569]
print("n with f(n) mod 1409 == 569:",hits[:20],"count",len(hits))
for n in hits[:5]:
    print(n, seq[n], (3*(pow(4,n,M)+pow(6,n,M)))%M)
