from h import *
t=json.load(open(D+'th015_out.json')); rng=random.Random(3)
for r in t['rows'][::4]:
    T=bytes.fromhex(r['tape']); M=r['M']; Mr=[]
    for p in range(G):
        kill=0
        for _ in range(16):
            t2=bytearray(T); t2[p]=rng.randrange(256); kill+= not P.run(bytes(t2))[0]
        if kill>=8: Mr.append(p)
    print(r['epoch'],'M(0x00)',M,'M(random, >=50% kill)',Mr,'zero-valued loci missed by 0x00 knockout',[p for p in Mr if p not in M and T[p]&31 in (0,30)], flush=True)
