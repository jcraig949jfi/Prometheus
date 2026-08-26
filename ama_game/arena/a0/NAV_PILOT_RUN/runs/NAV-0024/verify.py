M=3301
a,b = 9, 3287   # f(n) = 9 f(n-1) - 14 f(n-2)
seq={1:30,2:200}
for n in range(3,701): seq[n]=(a*seq[n-1]+b*seq[n-2])%M
checks={99:2874,317:248,600:1093,1:30,2:200,3:1380,4:3018,5:1240}
for n,v in sorted(checks.items()):
    print(n, seq[n], v, "OK" if seq[n]==v else "FAIL")
# closed form
cf = {n:(pow(2,n,M)+4*pow(7,n,M))%M for n in range(1,701)}
print("closed form agrees:", all(cf[n]==seq[n] for n in range(1,701)))
hits=[n for n in range(1,601) if seq[n]==981]
print("hits in [1,600]:", hits)
print("first hit anywhere n<=100000:", next((n for n in range(1,100001) if (pow(2,n,M)+4*pow(7,n,M))%M==981), None))
import math
print("distinct values in [1,600]:", len(set(seq[n] for n in range(1,601))))
