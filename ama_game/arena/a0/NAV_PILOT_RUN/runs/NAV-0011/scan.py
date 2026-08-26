M=4001; a=10; b=3980; TARGET=1372
s=[None,47,281]
hits=[]
for n in range(3,601):
    s.append((a*s[n-1]+b*s[n-2])%M)
for n in range(1,601):
    if s[n]==TARGET: hits.append(n)
print("hits:",hits[:20],"count",len(hits))
# period detection
seen={}
for n in range(1,600):
    k=(s[n],s[n+1])
    if k in seen:
        print("period start",seen[k],"len",n-seen[k]); break
    seen[k]=n
open("predicted_seq.txt","w").write("\n".join(f"{n} {s[n]}" for n in range(1,601)))
