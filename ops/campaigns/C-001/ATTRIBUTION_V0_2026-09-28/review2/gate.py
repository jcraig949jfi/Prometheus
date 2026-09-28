from h import *
from collections import Counter
EPS=(17300,17900,19400)
for s in d['snapshots']:
    if s["epoch"] not in EPS: continue
    row=[]
    for m in s['members']:
        T=bytes.fromhex(m['tape']); ne=nb=0
        for x in range(256):
            r=trace(T,x)
            if sum(r['nbr_mask'])/G>=0.9:
                nb+=1; ne+= r['nbr_window']==T
        row.append((ne,nb))
    print(s['epoch'], 'exact/birth inputs per member (of 256):', ' '.join('%d/%d'%x for x in row), flush=True)
