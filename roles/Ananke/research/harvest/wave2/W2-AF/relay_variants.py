"""W2-AF RELAY plant variants (hand-written; never a search seed), each designed against one dial.
All are homogeneous and position-free. Register use: S0 = held sign (+-256), S1 = timer.
PAY0/EMIT are written directly (they are writable registers and readable as temporaries).

R11  refresh-equivalent change relay (11 lines, D=1). V = (input sum != 0) ? input : S0; new = sign(V)*256
     (re-normalises S0 every awake tick, as P-2's relay_refresh); emit new iff it differs in sign from the old
     S0 (sign-product test, robust to decay of |S0|).
B(k) burst (redundancy against loss / sparse fanout): after a change keep re-emitting the held value for k-1
     more awake ticks (timer S1 = 256 on change, minus 256/k per awake tick). 14 lines, D=2.
S(k) sparse burst (against ALOHA/saturating caps): B(k) with each emission gated by RAND (p ~ 1/2), so
     neighbours' re-emissions de-synchronise. 15 lines, D=2.
E(h) refractory epoch lock (against async late learners, jitter and dup: stale packets of the previous trial
     arriving after the new wave): after adopting a value a site ignores packets for ~h awake ticks. 15 lines.
BE(h) E(h) that also re-emits during its refractory window (redundancy + lock). 16 lines, D=2.
L6   lean 6-line relay for energy-economy cells: S0 += 2*input sum (leaky through physics decay), emit the
     input sum when it opposes S0 or exceeds |S0| (so S0 = 0 relays forward). D=1. (A 5-line first draft that
     emitted only on strict opposition never left the sensor: S0 = 0 relays never emit; KA caught it.)
Controls: zero_comm (engine control) must give .5.
"""
import numpy as np
from prometheus.ananke import plants

A = plants.assemble

def _core(refractory=False):
    L = [("ADD", "T0", "SENSE", "IN0_0", 0),
         ("MULQ", "T1", "T0", "T0", 0),
         ("SEL", "T1", "T0", "S0", 0)]            # V = input nz ? input : S0
    if refractory:
        L += [("MOV", "T2", "S1", 0, 0),
              ("SEL", "T2", "S0", "T1", 0),        # refractory (S1 > 0) ? S0 : V
              ("GT", "T1", "T2", "ZERO", 0),
              ("GT", "T3", "ZERO", "T2", 0)]
        L += [("SUB", "PAY0", "T1", "T3", 0)]
    else:
        L += [("GT", "T2", "T1", "ZERO", 0),
              ("GT", "T3", "ZERO", "T1", 0),
              ("SUB", "PAY0", "T2", "T3", 0)]      # new = sign(V)*256
    L += [("MULQ", "T3", "PAY0", "S0", 0),         # >0 iff same sign as old S0
          ("GT", "T3", "T3", "ZERO", 0),
          ("MULQ", "T2", "PAY0", "PAY0", 0),       # 256 iff new != 0
          ("SUB", "EMIT", "T2", "T3", 0),          # 256 iff changed
          ("MOV", "S0", "PAY0", 0, 0)]
    return L

def R11():
    return _core()

def B(k=4):
    return _core() + [("ADDI", "S1", "S1", 0, -(256 // k)),
                      ("MAX", "S1", "S1", "EMIT", 0),
                      ("MAX", "EMIT", "EMIT", "S1", 0)]

def S(k=4):
    return B(k) + [("RAND", "EMIT", "EMIT", 0, 0)]

def E(h=4):
    return _core(True) + [("ADDI", "S1", "S1", 0, -(256 // h)),
                          ("MAX", "S1", "S1", "EMIT", 0)]

def BE(h=4):
    return E(h) + [("MAX", "EMIT", "EMIT", "S1", 0)]

def L6():
    return [("ADD", "PAY0", "SENSE", "IN0_0", 0),
            ("MULQ", "T1", "PAY0", "S0", 0),
            ("MULQ", "T2", "PAY0", "PAY0", 0),
            ("GT", "EMIT", "T2", "T1", 0),         # input nz and (opposes S0, or |S0| < |input|)
            ("ADD", "S0", "S0", "PAY0", 0),
            ("ADD", "S0", "S0", "PAY0", 0)]

def need_D(lines):
    return 2 if any("S1" in x[1:4] for x in lines) else 1

def genome(ph, lines):
    """-> (ph2, genome [G,L,5], in_space, nlines). Scored at prog_len max(L,16) and state_dim >= need so that
    every variant shares one World; NOP padding and extra zero registers are behaviour-neutral (c_op counts
    non-NOP lines; c_mem counts non-zero S registers; RAND streams are indexed by line, not by L)."""
    n = len(lines); D = need_D(lines)
    in_space = ph.prog_len >= n and ph.state_dim >= D
    ph2 = ph.replace(prog_len=max(ph.prog_len, 16), state_dim=max(ph.state_dim, 2))
    body = A(ph2, lines)
    return ph2, np.broadcast_to(body, (ph2.rules, *body.shape)).copy(), in_space, n

def menu(env):
    d = env.delta
    return {"R11": R11(), "B4": B(4), "B8": B(8), "S4": S(4), "E_h": E(max(2, d // 2)),
            "BE_h": BE(max(2, d // 2)), "L6": L6()}
