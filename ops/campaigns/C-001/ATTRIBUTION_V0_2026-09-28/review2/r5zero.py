from h import *
import statistics as S
t=json.load(open(D+'th015_out.json'))
rng=random.Random(5); K=40
res=[]
for r in t['rows']:
    T=bytes.fromhex(r['tape']); M=r['M']; X=r['X']
    z=bytearray(G)
    for p in M: z[p]=T[p]
    mz=P.run(bytes(z))[0]                                  # M on all-zero (NOP) background, deterministic
    nz=[p for p in X if T[p]!=0]                            # X without its 0x00 bytes
    xnz=P.rate(lambda: P.graft(T,nz,rng),K)['birth']
    # M on a background drawn from T's own byte composition shuffled
    def shuf():
        b=list(T); rng.shuffle(b); t2=bytearray(b)
        for p in M: t2[p]=T[p]
        return bytes(t2)
    ms=P.rate(shuf,K)['birth']
    res.append((mz,xnz,ms,len(M),len(nz),len(X)))
    print(r['epoch'],'|M|',len(M),'M on zeros',mz,'|X nonzero|',len(nz),'of',len(X),'graft Xnonzero',xnz,'M on shuffled-own',ms,flush=True)
print('M on zero bg: frac tapes', S.mean(x[0] for x in res), 'Xnonzero', S.mean(x[1] for x in res), 'M shuffled-own', S.mean(x[2] for x in res))
print('mean |X nonzero|', S.mean(x[4] for x in res))
