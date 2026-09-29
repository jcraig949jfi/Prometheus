import sys, random
sys.path.insert(0, r"D:\Prometheus-worktrees\bellerophon-post-campaign-forensics")
from prometheus.z80atlas import vm
from prometheus.z80atlas.world import World, Config
L=64
def world(repro, **kw):
    cfg=Config(reproduction=repro, cells=4, ticks=1, world="SOUP", spatial="WELL_MIXED", **kw)
    w=World(cfg, 1); w.cells=[None]*4; w.seed_lineages=set(); return w
rnd=random.Random(5)
def rtape(): return bytearray(rnd.randrange(256) for _ in range(L))

print("--- R2 ENDOGENOUS_PARTIAL: writer writes ONE byte (LD T,70; LD (T),A) into an occupied random partner")
w=world("ENDOGENOUS_PARTIAL")
writer=rtape(); writer[:4]=bytes([vm.LD_T_n,70,vm.LD_pT_A,vm.HALT])
a=w._spawn(0,writer,None,"init"); b=w._spawn(1,rtape(),None,"init")
mem,tr=w._execute(a,b.tape,[0]); a.tape=bytearray(mem[:L]); w._apply_reproduction(a,1,mem,tr)
print(" births",w.endogenous_births,"captures",w.captures,"writer.replications",a.replications,"writer.fidelity_last %.3f"%a.fidelity_last,
      "(>= hifi 0.90) ; child glineage==partner's:",w.cells[1].glineage==b.glineage, "; first_replication.seeded",w.first_replication["seeded"])

print("--- R2b ENDOGENOUS_PARTIAL into an EMPTY cell: child = 63 zero bytes + 1; fidelity vs a mostly-zero writer")
w=world("ENDOGENOUS_PARTIAL")
z=bytearray(L); z[:4]=bytes([vm.LD_T_n,70,vm.LD_pT_A,vm.HALT])
a=w._spawn(0,z,None,"init")
mem,tr=w._execute(a,None,[0]); a.tape=bytearray(mem[:L]); w._apply_reproduction(a,1,mem,tr)
print(" child nonzero bytes",sum(1 for x in w.cells[1].tape if x),"fidelity %.3f"%a.fidelity_last,"-> counted hifi replication of a 4-byte program into a zero tape")

print("--- R3 PAIR_EXECUTION: any change to b (1 byte) is a birth; fidelity taken vs target (capture)")
cfg=Config(reproduction="PAIR_EXECUTION", cells=4, ticks=1, world="SOUP", spatial="WELL_MIXED")
w=World(cfg,1); w.cells=[None]*4
wa=rtape(); wa[:4]=bytes([vm.LD_T_n,100,vm.LD_pT_A,vm.HALT]); a=w._spawn(0,wa,None,"init"); b=w._spawn(1,rtape(),None,"init")
mem,tr=w._pair_execute(a,b,[0]); new_a=bytearray(mem[:L]); new_b=bytearray(mem[L:2*L]); a.tape=new_a
fid=1.0-sum(1 for x,y in zip(new_b,a.tape) if x!=y)/L
w._register_offspring(1,new_b,a,"PAIR_EXECUTION",fid,tr,replaced=b)
print(" bytes changed in b:",sum(1 for x,y in zip(new_b,b.tape) if x!=y),"; writer fidelity_last %.3f"%a.fidelity_last,"captures",w.captures)

print("--- R4 fill artifact under ENDOGENOUS_COPY: LD S,63 ; LD T,0 ; LD C,128 ; LDIR : smears byte mem[63] over [0,128)")
w=world("ENDOGENOUS_COPY")
t=rtape(); t[:7]=bytes([vm.LD_S_n,63,vm.LD_T_n,0,vm.LD_C_n,128,vm.LDIR])
t[63]=0x00
a=w._spawn(0,t,None,"init")
mem,tr=w._execute(a,None,[0]); a.tape=bytearray(mem[:L]); w._apply_reproduction(a,1,mem,tr)
print(" births",w.endogenous_births,"writer fidelity %.3f"%a.fidelity_last,"; writer post-exec tape unique bytes",len(set(a.tape)),"; fidelity compared against the writer's POST-execution (self-destroyed) tape")
# note the smear: S<T overlap -- actually S=63 > T=0 so it copies [63..191) to [0..128)
print("   (child == writer post-exec?)", bytes(w.cells[1].tape)==bytes(a.tape))

print("--- R5 GATED_INTERACTION: skipped organisms neither age nor pay cost")
cfg=Config(pressure="GATED_INTERACTION", cells=16, ticks=1, world="SOUP", spatial="WELL_MIXED")
w=World(cfg,3)
for _ in range(100): w.step()
ages=[o.age for o in w.cells if o]; print(" after 100 ticks: alive",len(ages),"max age",max(ages),"min age",min(ages),"(lifespan 40)")

print("--- R6 SEPARATED: pc_max (repro span) of the 2nd half is discarded")
cfg=Config(layout="SEPARATED", reproduction="ENDOGENOUS_COPY", cells=4, ticks=1, world="SOUP", spatial="WELL_MIXED")
w=World(cfg,1); w.cells=[None]*4
t=bytearray(L); t[0]=vm.HALT; t[32:32+8]=vm.replicator(L)
a=w._spawn(0,t,None,"init"); mem,tr=w._execute(a,None,[0]); print(" pc_max reported",tr.pc_max,"although execution reached pc>=39; neighbour_writes",tr.neighbour_writes)
