P=2711
a,b=10,2690
seq={1:20,2:116}
for n in range(3,1201): seq[n]=(a*seq[n-1]+b*seq[n-2])%P
# closed form check: roots of x^2-10x+21 = (x-3)(x-7)
cf=[(2*(pow(3,n,P)+pow(7,n,P)))%P for n in range(0,1201)]
print("closed form f(n)=2*(3^n+7^n) matches recurrence on 1..1200:",
      all(seq[n]==cf[n] for n in range(1,1201)))
print("ord(3)=",next(k for k in range(1,P) if pow(3,k,P)==1),
      " ord(7)=",next(k for k in range(1,P) if pow(7,k,P)==1))
print("hits<=600:",[n for n in range(1,601) if seq[n]==1822])
print("hits<=1200:",[n for n in range(1,1201) if seq[n]==1822])
print("hits over full period n=1..2710:",[n for n in range(1,2711) if (2*(pow(3,n,P)+pow(7,n,P)))%P==1822])
d=min((min((seq[n]-1822)%P,(1822-seq[n])%P),n) for n in range(1,601))
print("closest approach to 1822 in [1,600]: cyclic distance",d[0],"at n =",d[1],"value",seq[d[1]])
print("predicted f(600) =",seq[600]," f(599) =",seq[599])
