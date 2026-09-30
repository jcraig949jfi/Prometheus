# Nestor's independent re-check of Adversary 2 D3 (hijack) and D4 (phase arithmetic). Own code, not the adversary's scripts.
import sys, random
sys.path[:0]=['c9x-explore-2026-09-24/x_donor_swap','z80atlas-verify-2026-09-22','../../../lib']
import world, z8, p11, run_ds
g=run_ds.donor_genome(); a=run_ds.cells()["7ae3f9c1437c8000-s54765-tL-a0"]
r=world.Runner(dict(a['cell'],atlas_axis="NONE"),1,tier=a['tier'])
n=r.L; tl=world._pow2(2*n); kw=dict(n=n,tape_len=tl,budget=r.t['slice'],ops_mask=r._ops_mask(),cmr=0.0)
zero=(None,0,0)
def run(ga,gb,seed):
    tape,prov,lit,wo=p11.interact(z8,ga=ga,gb=gb,st_a=zero,st_b=zero,rng=random.Random(seed),**kw)
    return bytes(tape[0:n]), bytes(tape[n:2*n])
R=random.Random(7); N=400
ko=bytearray(g); 
for i in (23,24,52,53): ko[i]=0
cnt={'intact':0,'ko':0,'rand':0}; both=0
for t in range(N):
    pb=bytes(R.randrange(256) for _ in range(n)); rnd=bytes(R.randrange(256) for _ in range(n))
    for lab,ga in (('intact',g),('ko',bytes(ko)),('rand',rnd)):
        h0,h1=run(ga,pb,t)
        if p11.fidelity(h0,pb)>=0.9 and p11.fidelity(h0,ga)<0.9: cnt[lab]+=1
print('side0 half overwritten by partner-like content, of',N,':',cnt)
# who writes? restrict side-1 (partner) to its own half (OWN policy) via victim_side=0 + donor_disabled
c2=0; c_prov={'a':0,'b':0}
R=random.Random(7)
for t in range(N):
    pb=bytes(R.randrange(256) for _ in range(n)); rnd=bytes(R.randrange(256) for _ in range(n))
    tape,prov,lit,wo=p11.interact(z8,ga=g,gb=pb,st_a=zero,st_b=zero,rng=random.Random(t),victim_side=0,donor_disabled=True,**kw)
    h0=bytes(tape[0:n])
    if p11.fidelity(h0,pb)>=0.9 and p11.fidelity(h0,g)<0.9: c2+=1
    tape,prov,lit,wo=p11.interact(z8,ga=g,gb=pb,st_a=zero,st_b=zero,rng=random.Random(t),**kw)
    h0=bytes(tape[0:n])
    if p11.fidelity(h0,pb)>=0.9 and p11.fidelity(h0,g)<0.9:
        w=[prov[i] for i in range(n) if h0[i]!=g[i]]
        c_prov['a']+=sum(1 for x in w if x==1); c_prov['b']+=sum(1 for x in w if x==2)
print('overwrite with partner restricted to own half:',c2,'/',N,'; authorship of changed side-0 bytes in unrestricted overwrites (1=7ae3 ctx, 2=partner ctx):',c_prov)
