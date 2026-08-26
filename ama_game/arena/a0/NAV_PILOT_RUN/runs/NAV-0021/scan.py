M=2711
a,b=7,-12
f={1:18,2:66}
for n in range(3,601):
    f[n]=(a*f[n-1]+b*f[n-2])%M
hits=[n for n in range(1,601) if f[n]==506]
print("closed-form check:", all(f[n]==(2*pow(3,n,M)+3*pow(4,n,M))%M for n in range(1,601)))
print("hits for 506:",hits)
print("first few:",[f[n] for n in range(1,8)])
if hits:
    n=hits[0]
    print("witness n=",n,"f(n) mod 2711 =",f[n])
    print("neighbours",{k:f[k] for k in range(max(1,n-2),min(600,n+2)+1)})
print("distinct residues hit:",len(set(f[n] for n in range(1,601))))
