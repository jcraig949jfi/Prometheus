from h import *
import statistics as S
t=json.load(open(D+'th015_out.json'))
rng=random.Random(2026); K=40
out=[]
for r in t['rows']:
    T=bytes.fromhex(r['tape']); M,X=P.machinery(T)
    assert M==r['M'] and X==r['X']
    ex=P.rate(lambda: P.graft(T,X,rng),K)['birth']
    rs=P.rate(lambda: P.graft(T,rng.sample(range(G),len(X)),rng),K)['birth']
    # contiguous block of |X| loci starting at 0 (prefix) -- position-only control
    pre=P.rate(lambda: P.graft(T,list(range(len(X))),rng),K)['birth']
    # M plus random loci to size |X|
    def mr():
        extra=rng.sample([p for p in range(G) if p not in M], len(X)-len(M)); return P.graft(T,M+extra,rng)
    mx=P.rate(mr,K)['birth']
    out.append((r['epoch'],len(M),len(X),ex,rs,pre,mx))
    print(r['epoch'],len(M),len(X),'X',ex,'rand|X|',rs,'prefix|X|',pre,'M+rand',mx, flush=True)
for i,n in enumerate(['X','rand|X|','prefix|X|','M+rand to |X|']):
    print(n, round(S.mean(o[3+i] for o in out),3))
