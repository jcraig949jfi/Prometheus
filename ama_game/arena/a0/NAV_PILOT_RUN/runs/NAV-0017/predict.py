p=1009; a,b=11,979
f={1:40,2:230}
for n in range(3,701):
    f[n]=(a*f[n-1]+b*f[n-2])%p
hits=[n for n in range(1,601) if f[n]==24]
print("hits of 24 in [1,600]:",hits)
print("f(500)=",f[500],"f(600)=",f[600])
if hits: print("first hit",hits[0],"value",f[hits[0]])
# period check
per=None
for k in range(1,700):
    if f.get(1+k)==f[1] and f.get(2+k)==f[2]:
        per=k;break
print("period:",per)
