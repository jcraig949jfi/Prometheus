P=4001
def f(n): return (4*pow(3,n,P)+3*pow(7,n,P))%P
obs={25:844,87:2030,150:3627,233:1792,311:1348,400:2552,512:3472,600:481}
ok=all(f(n)==v for n,v in obs.items())
print("held-out points matched:",ok, {n:(v,f(n)) for n,v in obs.items() if f(n)!=v})
# closeness of the model image to 1422: how many n are within +-1 etc (sanity on planting)
vals=[f(n) for n in range(1,601)]
print("distinct values:",len(set(vals)))
import collections
print("1422 present:",1422 in vals)
# period of the pair
per=None
for k in range(1,4001):
    if pow(3,k,P)==1 and pow(7,k,P)==1: per=k; break
print("period of f:",per)
# does 1422 occur anywhere over a FULL period?
full=[n for n in range(1,per+1) if f(n)==1422]
print("hits over one full period", per, ":", full[:20], "count",len(full))
