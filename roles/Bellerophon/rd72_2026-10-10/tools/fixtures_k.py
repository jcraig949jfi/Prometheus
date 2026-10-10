"""BEL-RD-72 K fixtures: two-source COMPUTATIONAL composition across a desert (COND_MULTI).

X  copier + transform block (LD B,85; XOR A,B; ADD A,3) -> correct on x >= 128 only (pays half of COND_MULTI)
Y  copier + branch block (CP A,128; JC) echoing x       -> correct on x < 128 only (pays the other half)
Neither has ANY single-step route (substitution, self segment move, insertion) to a FUNC + COND_MULTI-competent tape
(enumerated). Layouts:
  ALIGNED  X's block at 12..16 after a NOP pad; Y's empty slot at 12..16: composite = Y[0:12] + X[12:] (one prefix
           transfer; a Y whose copy length mutates to 12 writes it -- but then carries the truncated copier)
  SHIFTED  X's block at 8..12, Y's slot at 12..16: one segment transfer from X into Y (12 routes), not a prefix
  NOSLOT   Y's branch jumps straight to OUT: no single segment transfer suffices (0 routes): needs rearrangement"""
from prometheus.z80atlas import vm

L = 64


def _pad(b):
    return bytes(b[:L]) + bytes(max(0, L - len(b)))


def fixtures():
    R = bytes(vm.replicator(L)[:7])
    X_al = _pad(R + bytes([vm.IN_A, 0, 0, 0, 0, vm.LD_B_n, 85, vm.XOR_A_B, vm.ADD_A_n, 3, vm.OUT_A, vm.HALT]))
    Y_al = _pad(R + bytes([vm.IN_A, vm.CP_A_n, 128, vm.JC_n, 17, 0, 0, 0, 0, 0, vm.OUT_A, vm.HALT]))
    X_sh = _pad(R + bytes([vm.IN_A, vm.LD_B_n, 85, vm.XOR_A_B, vm.ADD_A_n, 3, vm.OUT_A, vm.HALT]))
    Y_ns = _pad(R + bytes([vm.IN_A, vm.CP_A_n, 128, vm.JC_n, 12, vm.OUT_A, vm.HALT]))
    return {"X_al": X_al, "Y_al": Y_al, "X_sh": X_sh, "Y_sh": Y_al, "Y_ns": Y_ns, "REP": _pad(vm.replicator(L))}
