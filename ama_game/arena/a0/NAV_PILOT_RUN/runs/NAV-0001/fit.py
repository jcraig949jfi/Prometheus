P=1009
v={1:41,2:257,3:730,4:954,5:384}
# solve a*v[k+1] + b*v[k] = v[k+2] for k=1,2
import itertools
sols=[]
for a in range(P):
    for b in range(P):
        if (a*v[2]+b*v[1])%P==v[3] and (a*v[3]+b*v[2])%P==v[4]:
            sols.append((a,b))
print("homogeneous order-2 solutions:",sols)
for a,b in sols:
    print("predict f(5)=",(a*v[4]+b*v[3])%P,"actual",v[5])
