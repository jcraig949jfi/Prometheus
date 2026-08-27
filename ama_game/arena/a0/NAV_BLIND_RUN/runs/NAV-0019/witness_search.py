P=5003
obs={1:27,2:123,3:567,4:2643,5:2441,6:4130,7:3359,8:2664,9:1823,10:3151,11:1905,12:4155}
f=lambda n: 3*(pow(4,n,P)+pow(5,n,P))%P
print("match obs:", all(f(n)==v for n,v in obs.items()))
hits=[n for n in range(1,601) if f(n)==1140]
print("hits:",hits)
print("far vals:", [(n,f(n)) for n in (100,300,450,600)])
