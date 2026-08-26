p=1009
v={1:40,2:230,3:321,4:667,5:734,6:172}
sols=[]
# brute force a,b,c over Z_p using 3 equations solved by search on a,b then c
for a in range(p):
    for b in range(p):
        c=(v[3]-a*v[2]-b*v[1])%p
        if (a*v[3]+b*v[2]+c)%p==v[4] and (a*v[4]+b*v[3]+c)%p==v[5] and (a*v[5]+b*v[4]+c)%p==v[6]:
            sols.append((a,b,c))
print("num solutions:",len(sols))
for s in sols[:10]: print(s)
