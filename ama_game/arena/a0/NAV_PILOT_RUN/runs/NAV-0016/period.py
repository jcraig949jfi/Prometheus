p=1009;a=11;b=979
s=(23,133)
seen={}
x,y=s
n=1
occ=[]
period=None
for n in range(1,20000):
    if x==163: occ.append(n)
    if n>1 and (x,y)==s:
        period=n-1; break
    x,y=y,(a*y+b*x)%p
print("period",period,"first occurrences of 163 (n<=%d)"%n,occ[:10])
