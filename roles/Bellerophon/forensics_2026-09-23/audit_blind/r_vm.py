import sys, random
sys.path.insert(0, r"D:\Prometheus-worktrees\bellerophon-post-campaign-forensics")
from prometheus.z80atlas import vm
from prometheus.z80atlas.world import World, Config, Org
L=64
print("--- R1 bare LDIR at reset registers (S=T=C=0): C=0 wraps -> 256-byte self-copy, nothing changes")
partner=bytes(random.Random(1).randrange(256) for _ in range(L))
mem=bytearray(256); mem[0]=vm.LDIR; mem[1]=vm.HALT; mem[L:2*L]=partner; before=bytes(mem)
tr=vm.execute(mem,L,0,256,[])
print(" steps",tr.steps,"budget 256; window addrs 'written':",sum(1 for a in tr.writes if L<=a<2*L),"of",L,"; bytes actually changed:",sum(1 for a,b in zip(before,mem) if a!=b),"; neighbour_writes",tr.neighbour_writes,"copy_events",tr.copy_events)
print("--- R1b COPYALL budget overrun")
mem=bytearray(256); mem[:6]=vm.replicator_copyall(L)
tr=vm.execute(mem,L,0,3,[],allow_copyall=True); print(" budget 3 -> steps",tr.steps)
print("--- R1c PC runs off own tape into partner window (NOP-sled executes partner's ECHO witness)")
mem=bytearray(256); mem[L:L+3]=vm.witness_echo(); mem[vm.IN_BASE]=77
tr=vm.execute(mem,L,0,256,[77]); print(" zero-tape outputs",tr.outputs,"pc_max",tr.pc_max,"halted",tr.halted)
print("--- R1d empty partner cell: zero window + NOP tape runs into IN region, executing input bytes as opcodes")
mem=bytearray(256); mem[vm.IN_BASE]=0x41   # input byte 0x41 == OUT_A opcode
tr=vm.execute(mem,L,0,256,[0x41]); print(" outputs",tr.outputs,"pc_max",hex(tr.pc_max),"reads_in",tr.reads_in)
