"""W2-J hand-written XOR plants (no search). Built from prometheus/ananke/plants.assemble + regmap.

Two families (every program reads only its own site's registers; positions are unknown to it):
  CLK  global tick clock + per-trial flag reset (sync update only). Generalises H-PLANT P-XOR to
       update_period 2 (clock advances by p per awake tick; onset test 'phase < p'), renormalises the
       flags every awake tick (GT S>onset: reset AND decay repair in one line), and, for decay_shift 1/6,
       keeps the clock as a mod-Pd counter whose stored value is pre-compensated for the decay
       (k=1: store u*2^p; k=6: u<64 is a decay fixed point).
  TTL  per-flag timers instead of a clock (any update mode): a flag is (re)learned only if its timer is
       older than W_s ticks, and counts as fresh for the readout while younger than W_f ticks.
       Timer = exogenous decay (decay_shift 3/6: value 256 decays deterministically every tick, awake or
       not) or a decrement per awake tick (decay 0: exact under sync, noisy under async).
Evidence modes: 'pay' (flags in PAY0/PAY1, threshold 0; noise-free rows), 'payN' (payloads scaled to
~32640 and threshold ~4080: robust to noise sums and saturate dilution), 'cnt' (flag type = channel,
evidence = packet COUNT CNT0/CNT1, which noise never touches; needs channels >= 2).
Readouts: 'xor' (- iff both flags) | 'nor' (the one-flag cheat: + iff no + flag; H-PLANT Disagreement 4).
"""
import numpy as np
from prometheus.ananke import plants
from prometheus.ananke.physics import Physics

A = plants.assemble


def _evidence(ev):
    if ev == "cnt":
        return [("MAX", "T0", "SENSE", "CNT0", 0), ("GT", "T0", "T0", "ZERO", 0),
                ("GT", "T1", "CNT1", "SENSE", 0)]
    if ev == "pay":
        return [("MAX", "T0", "SENSE", "IN0_0", 0), ("GT", "T0", "T0", "ZERO", 0),
                ("GT", "T1", "IN0_1", "SENSE", 0)]
    if ev == "payN":
        return [("CONST", "T3", 0, 7, 127), ("MULQ", "T0", "SENSE", "T3", 0), ("SUB", "T1", "ZERO", "T0", 0),
                ("MAX", "T0", "T0", "IN0_0", 0), ("MAX", "T1", "T1", "IN0_1", 0),
                ("SHR", "T2", "T3", 3, 0), ("GT", "T0", "T0", "T2", 0), ("GT", "T1", "T1", "T2", 0)]
    raise KeyError(ev)


def clk_lines(Pd, p, comp, ev, readout="xor"):
    L = []
    if comp == 0:                                   # S3 = absolute tick (decay 0 only)
        L += [("CONST", "T3", 0, 0, Pd - 1), ("MOD", "T2", "S3", "T3", 0), ("ADDI", "S3", "S3", 0, p),
              ("ADDI", "T2", "T2", 0, -p)]
    else:                                           # S3 = phase, stored pre-compensated for decay
        L += [("CONST", "T3", 0, 0, Pd - 1), ("ADDI", "T1", "S3", 0, p), ("MOD", "T1", "T1", "T3", 0)]
        if comp == 1:
            L += [("ADD", "T1", "T1", "T1", 0)] * p   # D^p(u * 2^p) = u for decay_shift 1
        L += [("ADDI", "T2", "S3", 0, -p), ("MOV", "S3", "T1", 0, 0)]
    L += [("GT", "T3", "ZERO", "T2", 0),            # 256 iff phase < p (trial onset at this awake tick)
          ("GT", "S1", "S1", "T3", 0), ("GT", "S2", "S2", "T3", 0)]   # reset at onset, else renormalise
    L += _evidence(ev)
    if ev == "cnt":
        L += [("GT", "T2", "T0", "S1", 0), ("GT", "T3", "T1", "S2", 0), ("ADD", "EMIT", "T2", "T3", 0),
              ("SHR", "CHAN", "T3", 8, 0)]
    else:
        L += [("GT", "PAY0", "T0", "S1", 0), ("GT", "PAY1", "T1", "S2", 0), ("ADD", "EMIT", "PAY0", "PAY1", 0)]
        if ev == "payN":
            L += [("MULQ", "PAY0", "PAY0", "T3", 0), ("MULQ", "PAY1", "PAY1", "T3", 0)]
    L += [("MAX", "S1", "S1", "T0", 0), ("MAX", "S2", "S2", "T1", 0)]
    if readout == "xor":
        L += [("XOR", "T0", "S1", "S2", 0), ("ADDI", "S0", "T0", 0, -128)]
    else:   # nor: + iff no + flag
        L += [("SUB", "S0", "ZERO", "S1", 0), ("ADDI", "S0", "S0", 0, 128)]
    return L



def rep(lo, hi):
    """A C1-genome-representable constant v = imm << s (imm in [-128,127], s in 0..7) with lo < v <= hi,
    returned as (imm, s) with the smallest shift; None if none exists."""
    for s in range(8):
        for imm in range(-128, 128):
            v = imm << s
            if lo < v <= hi:
                return imm, s
    return None


def const(dst, lo, hi):
    r = rep(lo, hi)
    assert r is not None, ("no representable constant in", lo, hi)
    return ("CONST", dst, 0, r[1], r[0])


def decay_seq(start, k, n):
    v = [start]
    for _ in range(n):
        x = v[-1]
        v.append(x - (x >> k))
    return v


def ttl_thresholds(ph, Ws, Wf, timer, start=256):
    """-> (theta_s, theta_f). relearn iff S < theta_s; fresh iff S > theta_f."""
    if timer == "decay":
        k = ph.decay_shift
        v = decay_seq(start, k, Wf + Ws + 4)
        assert all(v[i] > v[i + 1] for i in range(max(Wf, Ws) + 1)), "timer saturates"
        return (v[Ws], v[Ws - 1]), (v[Wf + 1] - 1, v[Wf] - 1)   # intervals (lo, hi] for rep()
    # decrement per awake tick
    if ph.update_mode == "sync":
        p = ph.update_period
        js, jf = -(-Ws // p), Wf // p
    else:
        js, jf = max(1, round(ph.update_p * Ws)), round(ph.update_p * Wf)
    # decrement step 8 from 256: value after j awake ticks = 256 - 8j (multiples of 8 are representable)
    return (256 - 8 * js, 256 - 8 * js + 7), (256 - 8 * jf - 9, 256 - 8 * jf - 1)


def ttl_lines(ph, ev, Ws, Wf, timer, readout="xor", big=False):
    """big=True: timers start at 32640 instead of 256 (needed for decay_shift 1, where 256 saturates
    after 8 ticks); cnt evidence only."""
    ts, tf = ttl_thresholds(ph, Ws, Wf, timer, start=16256 if big else 256)
    L = list(_evidence(ev))
    if timer == "dec":
        L += [("ADDI", "S1", "S1", 0, -8), ("ADDI", "S2", "S2", 0, -8)]
    L += [const("T2", *ts)]
    if ev == "cnt":
        L += [("GT", "T3", "T2", "S1", 0), ("MULQ", "T3", "T3", "T0", 0),
              ("GT", "PAY0", "T2", "S2", 0), ("MULQ", "PAY0", "PAY0", "T1", 0),
              ("ADD", "EMIT", "T3", "PAY0", 0), ("SHR", "CHAN", "PAY0", 8, 0)]
        if big:
            L += [("CONST", "T0", 0, 7, 127), ("MULQ", "T3", "T3", "T0", 0), ("MULQ", "PAY0", "PAY0", "T0", 0)]
        L += [("MAX", "S1", "S1", "T3", 0), ("MAX", "S2", "S2", "PAY0", 0)]
    else:
        assert not big
        L += [("GT", "PAY0", "T2", "S1", 0), ("MULQ", "PAY0", "PAY0", "T0", 0),
              ("GT", "PAY1", "T2", "S2", 0), ("MULQ", "PAY1", "PAY1", "T1", 0),
              ("ADD", "EMIT", "PAY0", "PAY1", 0),
              ("MAX", "S1", "S1", "PAY0", 0), ("MAX", "S2", "S2", "PAY1", 0)]
        if ev == "payN":
            L += [("CONST", "T3", 0, 7, 127), ("MULQ", "PAY0", "PAY0", "T3", 0), ("MULQ", "PAY1", "PAY1", "T3", 0)]
    L += [const("T2", *tf)]
    if readout == "xor":
        L += [("SUB", "S0", "S1", "T2", 0), ("SUB", "T0", "T2", "S2", 0), ("SEL", "S0", "T0", "T2", 0)]
    else:   # nor: + iff P not fresh
        L += [("SUB", "S0", "T2", "S1", 0)]
    return L


def needs(ev, fam):
    return {"state_dim": {"clk": 4, "clk3": 5, "clk4": 5}.get(fam, 3),
            "payload_width": 2 if ev in ("pay", "payN") else 1,
            "channels": 2 if (ev == "cnt" or fam == "clk4") else 1}


def fit(ph: Physics, lines, ev, fam, strict: bool):
    """-> (physics, override dict) or (None, missing) if strict and the row's genome fields cannot hold it."""
    nd = needs(ev, fam)
    want = {"prog_len": len(lines), **nd}
    ov = {}
    for k, v in want.items():
        if getattr(ph, k) < v:
            ov[k] = v
    if strict:
        return (ph, {}) if not ov else (None, ov)
    return ph.replace(**ov).validate(), ov


def genome(ph: Physics, lines) -> np.ndarray:
    body = A(ph, lines)
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()


# ---------------------------------------------------------------- v2: payN evidence, persist/gossip
def _gossip(s):
    """EMIT := EMIT * [U > BIG - BIG>>s], U ~ RAND(-BIG..BIG): keeps ~2^-s/2 of emission ticks. T3=BIG."""
    return [("RAND", "T0", "T3", 0, 0), ("SHR", "T1", "T3", s, 0), ("SUB", "T1", "T3", "T1", 0),
            ("GT", "T0", "T0", "T1", 0), ("MULQ", "EMIT", "EMIT", "T0", 0)]


def clk2_lines(Pd, delta, p, comp, emit="persist", lat_min=1, gossip=None, readout="xor"):
    L = []
    if comp == 0:
        L += [("CONST", "T3", 0, 0, Pd - 1), ("MOD", "T2", "S3", "T3", 0), ("ADDI", "S3", "S3", 0, p),
              ("ADDI", "T2", "T2", 0, -p)]
    else:
        L += [("CONST", "T3", 0, 0, Pd - 1), ("ADDI", "T1", "S3", 0, p), ("MOD", "T1", "T1", "T3", 0)]
        if comp == 1:
            L += [("ADD", "T1", "T1", "T1", 0)] * p
        L += [("ADDI", "T2", "S3", 0, -p), ("MOV", "S3", "T1", 0, 0)]
    if emit == "persist":   # emission window: phase <= delta - lat_min (later packets are useless now
        L += [("CONST", "EMIT", 0, 0, delta - lat_min - p + 1),   # and would leak into the next trial)
              ("GT", "EMIT", "EMIT", "T2", 0)]
    L += [("GT", "T3", "ZERO", "T2", 0), ("GT", "S1", "S1", "T3", 0), ("GT", "S2", "S2", "T3", 0)]
    L += _evidence("payN")
    if emit == "once":
        L += [("GT", "PAY0", "T0", "S1", 0), ("GT", "PAY1", "T1", "S2", 0), ("ADD", "EMIT", "PAY0", "PAY1", 0),
              ("MAX", "S1", "S1", "T0", 0), ("MAX", "S2", "S2", "T1", 0)]
    else:
        L += [("MAX", "S1", "S1", "T0", 0), ("MAX", "S2", "S2", "T1", 0), ("MAX", "T2", "S1", "S2", 0),
              ("MULQ", "EMIT", "EMIT", "T2", 0), ("MOV", "PAY0", "S1", 0, 0), ("MOV", "PAY1", "S2", 0, 0)]
    L += [("MULQ", "PAY0", "PAY0", "T3", 0), ("MULQ", "PAY1", "PAY1", "T3", 0)]
    if gossip:
        L += _gossip(gossip)
    if readout == "xor":
        L += [("XOR", "T0", "S1", "S2", 0), ("ADDI", "S0", "T0", 0, -128)]
    else:
        L += [("SUB", "S0", "ZERO", "S1", 0), ("ADDI", "S0", "S0", 0, 128)]
    return L


BIGV = 16256   # = 127 << 7, the largest CONST in C1 genome space (imm in [-128,127], shift <= 7)


def ttl2_thresholds(ph, Ws, Wf, We):
    """timer value read at age n ticks; decay>0: exogenous D^n(BIG); decay 0: BIG - (#awake ticks)."""
    if ph.decay_shift > 0:
        v = decay_seq(BIGV, ph.decay_shift, max(Ws, Wf, We) + 4)
        assert all(v[i] > v[i + 1] for i in range(max(Wf, Ws, We) + 1)), "timer saturates"
        return (v[Ws], v[Ws - 1]), (v[Wf + 1] - 1, v[Wf] - 1), (v[We + 1] - 1, v[We] - 1)
    if ph.update_mode == "sync":
        p = ph.update_period
        aw = lambda n: n // p
    else:
        aw = lambda n: round(ph.update_p * n)
    # decay 0: decrement BIG>>6 = 254 per awake tick from BIG: value = 16256 - 254 j
    f = lambda j: BIGV - 254 * j
    js, jf, je = max(1, aw(Ws)), aw(Wf), aw(We)
    return (f(js), f(js) + 254), (f(jf) - 255, f(jf) - 1), (f(je) - 255, f(je) - 1)


def ttl2_lines(ph, Ws, Wf, We, emit="persist", gossip=None, readout="xor"):
    ts, tf, te = ttl2_thresholds(ph, Ws, Wf, We)
    L = list(_evidence("payN"))
    if ph.decay_shift == 0:
        L += [("SHR", "T2", "T3", 6, 0), ("SUB", "S1", "S1", "T2", 0), ("SUB", "S2", "S2", "T2", 0)]
    L += [const("T2", *ts),
          ("GT", "PAY0", "T2", "S1", 0), ("MULQ", "PAY0", "PAY0", "T0", 0),
          ("GT", "PAY1", "T2", "S2", 0), ("MULQ", "PAY1", "PAY1", "T1", 0)]
    if emit == "once":
        L += [("ADD", "EMIT", "PAY0", "PAY1", 0)]
    L += [("MULQ", "PAY0", "PAY0", "T3", 0), ("MULQ", "PAY1", "PAY1", "T3", 0),
          ("MAX", "S1", "S1", "PAY0", 0), ("MAX", "S2", "S2", "PAY1", 0)]
    if emit == "persist":
        L += [const("T2", *te), ("GT", "PAY0", "S1", "T2", 0), ("GT", "PAY1", "S2", "T2", 0),
              ("ADD", "EMIT", "PAY0", "PAY1", 0),
              ("MULQ", "PAY0", "PAY0", "T3", 0), ("MULQ", "PAY1", "PAY1", "T3", 0)]
    if gossip:
        L += _gossip(gossip)
    L += [const("T2", *tf)]
    if readout == "xor":
        L += [("SUB", "S0", "S1", "T2", 0), ("SUB", "T0", "T2", "S2", 0), ("SEL", "S0", "T0", "T2", 0)]
    else:
        L += [("SUB", "S0", "T2", "S1", 0)]
    return L


# ---------------------------------------------------------------- v3 clock: jitter-leak guards
def lat_range(ph):
    lo = max(1, ph.lat_base + ph.lat_hop * 1)
    hi = ph.lat_base + ph.lat_hop * ph.max_dist() + ph.lat_jitter
    if ph.dup > 0:
        hi += 1 + ph.lat_jitter
    return lo, min(hi, ph.lm() - 1 + (1 + ph.lat_jitter if ph.dup > 0 else 0))


def clk3_lines(ph, Pd, delta, emit="persist", gossip=None, readout="xor"):
    """clk2 + (a) emission window phase <= min(delta - lat_min, Pd - 1 + lat_min - lat_max) so no packet
    lands after the next onset + lat_min, and (b) the inbox is ignored at phases < lat_min (no legitimate
    packet of this trial can be there; a late one of the previous trial can). Needs state_dim >= 5."""
    p, k = ph.update_period, ph.decay_shift
    comp = 0 if k == 0 else k
    assert comp in (0, 1, 6)
    lmin, lmax = lat_range(ph)
    wend = max(0, min(delta - lmin, Pd - 1 + lmin - lmax))
    L = []
    if comp == 0:
        L += [("CONST", "T3", 0, 0, Pd - 1), ("MOD", "T2", "S3", "T3", 0), ("ADDI", "S3", "S3", 0, p),
              ("ADDI", "T2", "T2", 0, -p)]
    else:
        L += [("CONST", "T3", 0, 0, Pd - 1), ("ADDI", "T1", "S3", 0, p), ("MOD", "T1", "T1", "T3", 0)]
        if comp == 1:
            L += [("ADD", "T1", "T1", "T1", 0)] * p
        L += [("ADDI", "T2", "S3", 0, -p), ("MOV", "S3", "T1", 0, 0)]
    L += [("CONST", "EMIT", 0, 0, wend - p + 1), ("GT", "EMIT", "EMIT", "T2", 0),       # window
          ("CONST", "S4", 0, 0, lmin - p - 1), ("GT", "S4", "T2", "S4", 0),             # inbox mask
          ("GT", "T3", "ZERO", "T2", 0), ("GT", "S1", "S1", "T3", 0), ("GT", "S2", "S2", "T3", 0),
          ("CONST", "T3", 0, 7, 127), ("MULQ", "T0", "IN0_0", "S4", 0), ("MULQ", "T1", "IN0_1", "S4", 0),
          ("MULQ", "T2", "SENSE", "T3", 0), ("MAX", "T0", "T0", "T2", 0), ("SUB", "T2", "ZERO", "T2", 0),
          ("MAX", "T1", "T1", "T2", 0), ("SHR", "T2", "T3", 3, 0), ("GT", "T0", "T0", "T2", 0),
          ("GT", "T1", "T1", "T2", 0)]
    if emit == "once":
        L += [("GT", "PAY0", "T0", "S1", 0), ("GT", "PAY1", "T1", "S2", 0), ("ADD", "T2", "PAY0", "PAY1", 0),
              ("MULQ", "EMIT", "EMIT", "T2", 0), ("MAX", "S1", "S1", "T0", 0), ("MAX", "S2", "S2", "T1", 0)]
    else:
        L += [("MAX", "S1", "S1", "T0", 0), ("MAX", "S2", "S2", "T1", 0), ("MAX", "T2", "S1", "S2", 0),
              ("MULQ", "EMIT", "EMIT", "T2", 0), ("MOV", "PAY0", "S1", 0, 0), ("MOV", "PAY1", "S2", 0, 0)]
    L += [("MULQ", "PAY0", "PAY0", "T3", 0), ("MULQ", "PAY1", "PAY1", "T3", 0)]
    if gossip:
        L += _gossip(gossip)
    if readout == "xor":
        L += [("XOR", "T0", "S1", "S2", 0), ("ADDI", "S0", "T0", 0, -128)]
    else:
        L += [("SUB", "S0", "ZERO", "S1", 0), ("ADDI", "S0", "S0", 0, 128)]
    return L


# ---------------------------------------------------------------- v4 clock: trial-parity channels
def clk4_lines(ph, Pd, delta, emit="persist", gossip=None, readout="xor", wend=None):
    """Packets carry the trial parity as their CHANNEL (needs channels >= 2) and a site reads only the
    channel of the current trial's parity, so a late packet of the previous trial (jitter, dup, slow
    paths) can never set a flag. The clock counts mod 2*Pd (decay-compensated as in clk2).
    Emission window phase <= delta - lat_min (later packets cannot arrive by the readout)."""
    p, k = ph.update_period, ph.decay_shift
    comp = k
    assert comp in (0, 1, 3, 6)
    lmin, _ = lat_range(ph)
    if wend is None:
        wend = max(0, delta - lmin)
    L = []
    if comp == 0:   # S3 = t
        L += [("CONST", "T1", 0, 0, 2 * Pd - 1), ("MOD", "T1", "S3", "T1", 0),       # t mod 2Pd
              ("CONST", "T3", 0, 0, Pd - 1), ("MOD", "T2", "S3", "T3", 0),           # phase
              ("GT", "S4", "T1", "T3", 0),                                           # parity (256 = odd trial)
              ("ADDI", "S3", "S3", 0, p)]
    else:           # S3 = (t mod 2Pd) * scale
        L += [("CONST", "T3", 0, 0, 2 * Pd - 1), ("ADDI", "T1", "S3", 0, p), ("MOD", "T1", "T1", "T3", 0)]
        if comp == 1:
            L += [("ADD", "T1", "T1", "T1", 0)] * p
        if comp == 3:   # w = u + floor(u/7) (floor(37u/256) for u < 64) inverts one decay_shift-3 step
            L += [("CONST", "T3", 0, 0, 37)]
            L += [("MULQ", "T0", "T1", "T3", 0), ("ADD", "T1", "T1", "T0", 0)] * p
        L += [("CONST", "T3", 0, 0, Pd - 1), ("MOD", "T2", "S3", "T3", 0), ("GT", "S4", "S3", "T3", 0),
              ("MOV", "S3", "T1", 0, 0)]
    L += [("ADDI", "T2", "T2", 0, -p),
          ("CONST", "EMIT", 0, 0, wend - p + 1), ("GT", "EMIT", "EMIT", "T2", 0),       # window
          ("GT", "T3", "ZERO", "T2", 0), ("GT", "S1", "S1", "T3", 0), ("GT", "S2", "S2", "T3", 0),
          ("MOV", "T0", "S4", 0, 0), ("SEL", "T0", "IN1_0", "IN0_0", 0),
          ("MOV", "T1", "S4", 0, 0), ("SEL", "T1", "IN1_1", "IN0_1", 0),
          ("CONST", "T3", 0, 7, 127), ("MULQ", "T2", "SENSE", "T3", 0), ("MAX", "T0", "T0", "T2", 0),
          ("SUB", "T2", "ZERO", "T2", 0), ("MAX", "T1", "T1", "T2", 0), ("SHR", "T2", "T3", 3, 0),
          ("GT", "T0", "T0", "T2", 0), ("GT", "T1", "T1", "T2", 0), ("SHR", "CHAN", "S4", 8, 0)]
    if emit == "once":
        L += [("GT", "PAY0", "T0", "S1", 0), ("GT", "PAY1", "T1", "S2", 0), ("ADD", "T2", "PAY0", "PAY1", 0),
              ("MULQ", "EMIT", "EMIT", "T2", 0), ("MAX", "S1", "S1", "T0", 0), ("MAX", "S2", "S2", "T1", 0)]
    else:
        L += [("MAX", "S1", "S1", "T0", 0), ("MAX", "S2", "S2", "T1", 0), ("MAX", "T2", "S1", "S2", 0),
              ("MULQ", "EMIT", "EMIT", "T2", 0), ("MOV", "PAY0", "S1", 0, 0), ("MOV", "PAY1", "S2", 0, 0)]
    L += [("MULQ", "PAY0", "PAY0", "T3", 0), ("MULQ", "PAY1", "PAY1", "T3", 0)]
    if gossip:
        L += _gossip(gossip)
    if readout == "xor":
        L += [("XOR", "T0", "S1", "S2", 0), ("ADDI", "S0", "T0", 0, -128)]
    else:
        L += [("SUB", "S0", "ZERO", "S1", 0), ("ADDI", "S0", "S0", 0, 128)]
    return L
