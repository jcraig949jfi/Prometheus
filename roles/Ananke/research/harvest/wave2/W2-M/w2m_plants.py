"""W2-M MAJ INTEGRATION plant family (hand-written; never a search seed). Built with plants.assemble.

Shared mechanism (homogeneous, position-free): every site is sensor, relay and readout.
- Sensor: on a cue it emits its signed cue SENSE (+-256) as PAY0 (lane 1). 'gated' members emit only on the
  first awake cue tick of a trial (S2 = cue flag of the previous wake), so every sensor casts ONE vote.
- Relay (lanes L >= 2, payload lanes): a site forwards what it received on lane i as lane i+1
  (PAY{i+1} := IN0_i), i < L-1. Forwarding SUMS is linear, so no per-sensor identity is needed; each
  packet is forwarded once and lane L is never forwarded (hop-limited flood; dedup = hop limit).
- Readout tally S0 = signed SUM of every lane's arrivals over the current arrival run, i.e.
  S0 := (prev wake had arrivals ? S0 : 0) + sum_i w_i * IN0_i  on a wake with arrivals; held otherwise.
  The run resets at the first arrival wave of a trial (S1 = arrival flag of the previous wake): a
  cue-onset detector that needs no clock and no physics-decay-sensitive counter. The scored sign of S0
  is the majority of the votes that arrived in the run.
Members:
  INT_CO   6 lines, D>=1: S0 := sum of the LATEST arrival wave (co-arrival integration only; fits L=8).
  INT_1   11 lines, D>=2: run tally, lane 1, ungated.
  INT_1G  13 lines, D>=3: run tally, lane 1, gated single vote per sensor.
  INT_L   lanes 2..3 (needs P>=L), ungated; weights w (ring r1 non-backtracking correction w=(-2,1,1)
          for L=3: on a cycle lane-3 carries 3x every distance-1 vote).
Must-fail / controls:
  FIRST   S0 := sum of the FIRST arrival wave of a trial, later waves ignored (first-arrival readout).
  zero_comm (Controls) and DICT (schedule ablation: only sensor 0 of 5 receives cues).
"""
import numpy as np
from prometheus.ananke import plants

A = plants.assemble

def _bc(ph, body):
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()

def _tally(lanes_in):
    """lanes_in: list of (reg, weight in {1,-2}) -> run-tally lines (uses T0,T1, S0 tally, S1 flag)."""
    L = [("GT", "T0", "CNT0", "ZERO", 0),          # 256 iff any arrival this wake
         ("MOV", "T1", "S1", 0, 0),
         ("SEL", "T1", "S0", "ZERO", 0)]           # T1 = (prev wake had arrivals) ? S0 : 0
    for reg, w in lanes_in:
        if w == 1:
            L.append(("ADD", "T1", "T1", reg, 0))
        elif w == -2:
            L += [("SUB", "T1", "T1", reg, 0), ("SUB", "T1", "T1", reg, 0)]
        else:
            raise ValueError(w)
    L += [("SUB", "T1", "T1", "S0", 0),
          ("MULQ", "T1", "T1", "T0", 0),           # only on a wake with arrivals
          ("ADD", "S0", "S0", "T1", 0),
          ("MOV", "S1", "T0", 0, 0)]
    return L

def int_co(ph):
    return _bc(ph, A(ph, [("MOV", "PAY0", "SENSE", 0, 0),
                          ("MULQ", "EMIT", "SENSE", "SENSE", 0),
                          ("GT", "T0", "CNT0", "ZERO", 0),
                          ("SUB", "T1", "IN0_0", "S0", 0),
                          ("MULQ", "T1", "T1", "T0", 0),
                          ("ADD", "S0", "S0", "T1", 0)]))

def int_1(ph, gated=False):
    if gated:
        cue = [("MULQ", "T0", "SENSE", "SENSE", 0),
               ("GT", "T1", "S2", "ZERO", 0),
               ("MOV", "S2", "T0", 0, 0),
               ("SUB", "EMIT", "T0", "T1", 0),     # >0 only on the first awake cue tick
               ("MOV", "PAY0", "SENSE", 0, 0)]
    else:
        cue = [("MULQ", "EMIT", "SENSE", "SENSE", 0),
               ("MOV", "PAY0", "SENSE", 0, 0)]
    return _bc(ph, A(ph, cue + _tally([("IN0_0", 1)])))

def build(ph, lanes=1, reset="prev", k=0, gated=False, weights=None):
    """General member. lanes 1..3 (payload lanes); reset 'prev' (arrivals on the previous wake keep the run)
    or 'age' (S1 = age mark: 256 on a wake with arrivals, halved every wake; the run is kept while
    S1 >> k > 0, i.e. up to 8-k silent wakes without physics decay). Relays emit only when lane content
    is non-zero (squares), so zero packets never circulate."""
    w = weights or [1] * lanes
    L = []
    if gated:
        L += [("MULQ", "T0", "SENSE", "SENSE", 0), ("GT", "T1", "S2", "ZERO", 0),
              ("MOV", "S2", "T0", 0, 0), ("SUB", "T2", "T0", "T1", 0)]   # T2 > 0 only on a fresh cue
    else:
        L += [("MULQ", "T2", "SENSE", "SENSE", 0)]
    L += [("MOV", "PAY0", "SENSE", 0, 0)]
    for i in range(lanes - 1):
        L += [("MOV", f"PAY{i+1}", f"IN0_{i}", 0, 0),
              ("MULQ", "T3", f"IN0_{i}", f"IN0_{i}", 0),
              ("ADD", "T2", "T2", "T3", 0)]
    L[-1] = (L[-1][0], "EMIT", *L[-1][2:]) if lanes > 1 else L[-1]
    if lanes == 1:
        L += [("MOV", "EMIT", "T2", 0, 0)]
    L += [("GT", "T0", "CNT0", "ZERO", 0)]
    if reset == "prev":
        L += [("MOV", "T1", "S1", 0, 0)]
    else:
        L += [("SHR", "T1", "S1", k, 0)]
    L += [("SEL", "T1", "S0", "ZERO", 0)]
    for i in range(lanes):
        if w[i] == 1:
            L.append(("ADD", "T1", "T1", f"IN0_{i}", 0))
        else:
            assert w[i] == -2
            L += [("SUB", "T1", "T1", f"IN0_{i}", 0), ("SUB", "T1", "T1", f"IN0_{i}", 0)]
    L += [("SUB", "T1", "T1", "S0", 0), ("MULQ", "T1", "T1", "T0", 0), ("ADD", "S0", "S0", "T1", 0)]
    if reset == "prev":
        L += [("MOV", "S1", "T0", 0, 0)]
    else:
        L += [("SHR", "T2", "S1", 1, 0), ("MAX", "S1", "T0", "T2", 0)]
    return L

def nlines(Lst):
    return sum(1 for x in Lst if x[0] != "NOP")

def member(ph, **kw):
    Lst = build(ph, **kw)
    need = nlines(Lst)
    D = 3 if kw.get("gated") else 2
    P = kw.get("lanes", 1)
    ok = ph.prog_len >= need and ph.state_dim >= D and ph.payload_width >= P
    ph2 = ph if ok else ph.replace(prog_len=max(ph.prog_len, need), state_dim=max(ph.state_dim, D),
                                   payload_width=max(ph.payload_width, P))
    return ph2, _bc(ph2, A(ph2, Lst)), ok, need

def int_L(ph, L=2, weights=None):
    return member(ph, lanes=L, weights=weights)[1]

def first(ph):
    """First-arrival readout: S0 := wave sum only on the first arrival wave of a trial."""
    return _bc(ph, A(ph, [("MULQ", "EMIT", "SENSE", "SENSE", 0),
                          ("MOV", "PAY0", "SENSE", 0, 0),
                          ("GT", "T0", "CNT0", "ZERO", 0),
                          ("MOV", "T1", "S1", 0, 0),
                          ("SEL", "T1", "ZERO", "T0", 0),  # fresh = arrivals now AND none last wake
                          ("SUB", "T2", "IN0_0", "S0", 0),
                          ("MULQ", "T2", "T2", "T1", 0),
                          ("ADD", "S0", "S0", "T2", 0),
                          ("MOV", "S1", "T0", 0, 0)]))

def lines(g):
    return int((g[0, :, 0] % 16 != 0).sum())

def dict_sched(ep):
    """DICT control: only sensor 0 receives its cue; sensors 1..4 silent."""
    ep.schedule.sense_val[:, :, 1:] = 0

MEMBERS = {"INT_CO": (int_co, 6, 1, 1), "INT_1": (int_1, 10, 2, 1),
           "INT_1G": (lambda ph: int_1(ph, True), 13, 3, 1), "FIRST": (first, 9, 2, 1),
           "INT_2": (lambda ph: int_L(ph, 2), 13, 2, 2), "INT_3": (lambda ph: int_L(ph, 3), 16, 2, 3),
           "INT_3NB": (lambda ph: int_L(ph, 3, [-2, 1, 1]), 18, 2, 3)}
# name -> (builder, min prog_len, min state_dim, min payload_width)

def fits(name, ph):
    _, L, D, P = MEMBERS[name]
    return ph.prog_len >= L and ph.state_dim >= D and ph.payload_width >= P

def int_leak(ph):
    """3-line energy-cheap integrator: S0 += IN0_0 every wake; forgetting is left to the physics decay.
    For energy-economy cells (c_op per non-NOP line per wake, c_mem per non-zero S per tick)."""
    return _bc(ph, A(ph, [("MULQ", "EMIT", "SENSE", "SENSE", 0),
                          ("MOV", "PAY0", "SENSE", 0, 0),
                          ("ADD", "S0", "S0", "IN0_0", 0)]))
