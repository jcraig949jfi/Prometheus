import sys, random
sys.path.insert(0, r"D:\Prometheus-worktrees\bellerophon-post-campaign-forensics")
from prometheus.z80atlas import vm
from prometheus.z80atlas.tasks import Task, score
rng=random.Random(0)
def run(prog, x):
    mem=bytearray(256); mem[:len(prog)]=prog; mem[vm.IN_BASE]=x; tr=vm.execute(mem,64,0,256,[x]); return tr
for task in ("COND_ONE","COND_MULTI"):
  for name,prog in (("ECHO witness",vm.witness_echo()),("INC witness",vm.witness_inc())):
    T=Task(task); ema=0; above=0; N=200000; first=None
    for i in range(N):
        x=rng.randrange(256); tr=run(prog,x)
        s=score(T,tr.outputs,T.expected([x]),"ATOMIC","FORCED",tr.first_out_step,tr.first_in_step)
        ema=0.7*ema+0.3*s
        if ema>=0.85:
            above+=1; first = i if first is None else first
    print("%-10s %-12s ATOMIC+FORCED: exact-solve rate of the program = 0.5 region; P(score_ema>=0.85 per org-tick)=%.4f ; first 'crossing' at interaction %s"%(task,name,above/N,first))
# expected 'solvers' in a 256-cell population of such programs
print("=> with ~200 ECHO-like organisms, expected solvers per tick = %.1f  (solvers_tail>=1 -> 'solved', first_crossing -> moat_crossing trigger)"%(200*0.03))
# INCREMENTAL near-miss
T=Task("ECHO"); 
for off in (0,5,10,19,20):
    print(" INCREMENTAL: output x+%d on ECHO scores %.3f -> solver(ema>=0.85)=%s"%(off, score(T,[ (7+off)&255],[7],"INCREMENTAL","ABR",1,0), score(T,[(7+off)&255],[7],"INCREMENTAL","ABR",1,0)>=0.85))
T=Task("COND_MULTI")
tot=0
for x in range(256):
    tot+=score(T,[x],T.expected([x]),"INCREMENTAL","FORCED",2,1)
print(" INCREMENTAL COND_MULTI: the plain ECHO program's mean score = %.3f (ATOMIC would be 0.5)"%(tot/256))
