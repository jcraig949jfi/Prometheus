M=2711
def f(n): return (pow(4,n,M)+3*pow(6,n,M))%M
s={1:22,2:124,3:712,4:1433,5:2664,6:381,7:2227,8:2282}
print("check samples:", all(f(n)==v for n,v in s.items()))
hits=[n for n in range(1,601) if f(n)==887]
print("hits:",hits)
print("spot:", [(n,f(n)) for n in (50,100,300,600)])
# period
seq=[f(n) for n in range(1,1201)]
