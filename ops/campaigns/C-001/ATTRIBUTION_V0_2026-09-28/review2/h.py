import json, sys, random
sys.path.insert(0, '/home/jcraig/Prometheus-worktrees/rev2')
from archaeon.z80atlas import vm
from archaeon.lineage import core as LC
from archaeon.attribution.probes.th013_block13 import ALLOWED, G
from archaeon.attribution.probes import th015_archaeon as P
D = '/home/jcraig/Prometheus-worktrees/rev2/ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/'
d = json.load(open(D+'th013_out.json'))
F = bytes.fromhex(d['founder']['tape'])
NAMES = "NOP LDi LDr ADD SUB INC DEC XOR AND OR SHL SHR CMP JP JR JZ JNZ JC LDm LDmi COPY IN OUT HALT SWAP NEG JPr DJNZ LEN SEAL NOP2 HALT2".split()
IMM = {1,13,14,15,16,17,19,27}
def dis(t, ex=None):
    out=[]
    for p,b in enumerate(t):
        op=b&31; r=(b>>5)&3; hi=b>>7
        out.append("%2d %02x %-5s r%d h%d %s"%(p,b,NAMES[op],r,hi,'*' if ex and ex[p] else ''))
    return "\n".join(out)
def trace(t, x, pc0=0, nbr=LC.ZERO):
    return vm.execute(t, nbr, (x,), LC.STEP_CAP, True, -1.0, pc0)
