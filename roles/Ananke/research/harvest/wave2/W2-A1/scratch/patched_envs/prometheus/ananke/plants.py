"""Hand-written genomes: POSITIVE CONTROLS and CHEATS only.

These exist to prove (a) each family is reachable in PTE-SUB-1 (a
necessity preflight; Ensorain R2) and (b) the detectors fire on real
signal. They are NEVER inserted into a search population: the search
must not be steered toward our designs (mission s17).

A tiny assembler names registers so the plants are readable.
"""
from __future__ import annotations

import numpy as np

from .physics import Physics

OPS = {"NOP": 0, "MOV": 1, "ADD": 2, "SUB": 3, "MULQ": 4, "ADDI": 5, "CONST": 6, "GT": 7,
       "SEL": 8, "MAX": 9, "SHR": 10, "XOR": 11, "MOD": 12, "RAND": 13, "SETRULE": 14, "WIMM": 15}


def regmap(ph: Physics) -> dict:
    D, P, C = ph.state_dim, ph.payload_width, ph.channels
    NW = ph.n_write()
    m = {f"S{i}": i for i in range(D)}
    m.update({f"T{i}": D + i for i in range(4)})
    m.update({"EMIT": D + 4, "CHAN": D + 5, "RPORT": D + 6, "RVAL": D + 7})
    m.update({f"PAY{p}": D + 8 + p for p in range(P)})
    for c in range(C):
        for p in range(P):
            m[f"IN{c}_{p}"] = NW + c * P + p
        m[f"CNT{c}"] = NW + C * P + c
    base = NW + C * P + C
    m.update({"SENSE": base, "ENERGY": base + 1, "ZERO": base + 2})
    return m


def assemble(ph: Physics, lines, L: int | None = None) -> np.ndarray:
    """lines: (op, dst, a, b, imm) with register names or ints. -> [L,5]."""
    rm = regmap(ph)
    L = L or ph.prog_len
    assert len(lines) <= L, (len(lines), L)
    out = np.zeros((L, 5), dtype=np.int64)
    for i, (op, d, a, b, imm) in enumerate(lines):
        r = lambda x: rm[x] if isinstance(x, str) else int(x)
        out[i] = (OPS[op], r(d), r(a), r(b), imm)
    return out


def relay_flood(ph: Physics) -> np.ndarray:
    """A site adopts sign(SENSE + IN0_0)*256 into S0 when non-zero and
    re-emits only when its value changes: one outward wave per change."""
    return assemble(ph, [
        ("ADD", "T0", "SENSE", "IN0_0", 0),
        ("GT", "T2", "T0", "ZERO", 0),
        ("GT", "T3", "ZERO", "T0", 0),
        ("SUB", "T1", "T2", "T3", 0),        # T1 = sign*256 or 0
        ("MULQ", "T2", "T1", "T1", 0),       # T2 = 256 if T1 != 0
        ("XOR", "T3", "T1", "S0", 0),
        ("MULQ", "T3", "T3", "T3", 0),       # >0 iff T1 != S0
        ("MULQ", "EMIT", "T2", "T3", 0),
        ("MOV", "PAY0", "T1", 0, 0),
        ("SUB", "T3", "T1", "S0", 0),
        ("MULQ", "T3", "T3", "T2", 0),
        ("ADD", "S0", "S0", "T3", 0),        # S0 := T1 where T1 != 0
    ])


def hold_latch(ph: Physics) -> np.ndarray:
    """S0 := sign(SENSE)*256 when |SENSE| > 128, else unchanged. Local
    memory only (no packets): solves HOLD without decay."""
    return assemble(ph, [
        ("CONST", "T0", 0, 0, 1),            # T0 = 1 << 7 = 128  (bf=b field=7 below)
        ("GT", "T2", "SENSE", "T0", 0),
        ("SUB", "T1", "ZERO", "T0", 0),      # -128
        ("GT", "T3", "T1", "SENSE", 0),
        ("SUB", "T1", "T2", "T3", 0),        # sign*256 or 0
        ("MULQ", "T2", "T1", "T1", 0),
        ("SUB", "T3", "T1", "S0", 0),
        ("MULQ", "T3", "T3", "T2", 0),
        ("ADD", "S0", "S0", "T3", 0),
    ])


def fix_const_shift(g: np.ndarray, i: int, shift: int) -> np.ndarray:
    g = g.copy()
    g[i, 3] = shift
    return g


def plant(name: str, ph: Physics) -> np.ndarray:
    """-> genome [1(G) ..., L, 5] broadcast to ph.rules variants."""
    if name == "relay_flood":
        body = relay_flood(ph)
    elif name == "hold_latch":
        body = fix_const_shift(hold_latch(ph), 0, 7)
    elif name == "null":
        body = np.zeros((ph.prog_len, 5), dtype=np.int64)
    elif name == "sense_copy":
        # CHEAT-class local policy: S0 := SENSE (scores only if the target
        # is present at the actuator itself; used with the leak env)
        body = assemble(ph, [("MOV", "S0", "SENSE", 0, 0)])
    else:
        raise KeyError(name)
    return np.broadcast_to(body, (ph.rules, *body.shape)).copy()


# ------------------------------------------------ C1b known-answer fixtures
# (PREREG_PTE_C1b s5). Each ships with the physics it is correct under;
# none is ever a search seed.

def c1b_echo_physics() -> Physics:
    """Ring r1, flood to both neighbours, delay 5 = half of HOLD's
    cue_len 2 + gap 8, lossless: a bit can ride out and back exactly once."""
    return Physics(topology="ring", n_sites=24, radius=1, dest_mode="all", lat_base=5,
                   lat_hop=0, lat_jitter=0, loss=0.0, payload_width=2, channels=1,
                   update_mode="sync", update_period=1, decay_shift=0, state_dim=2,
                   prog_len=28)


def echo_hold(ph: Physics) -> np.ndarray:
    """HOLD with the bit ONLY in flight. The sensor emits (cue, 3). A site
    whose marker sum is exactly 3 relays (payload, 1) once. Every site sets
    S0 := sign(payload) on arrival. The sensor's own S0 is written only by
    the returning echo, at the readout tick, so resetting site state mid-gap
    cannot hurt, and flushing the in-flight packets must."""
    return assemble(ph, [
        ("CONST", "T0", 0, 7, 1),            # 128
        ("GT", "T1", "SENSE", "T0", 0),
        ("SUB", "T2", "ZERO", "T0", 0),
        ("GT", "T2", "T2", "SENSE", 0),
        ("SUB", "T1", "T1", "T2", 0),        # cue sign*256 or 0
        ("CONST", "T3", 0, 0, 3),
        ("SUB", "T2", "IN0_1", "T3", 0),     # 0 iff marker sum == 3
        ("GT", "T0", "T2", "ZERO", 0),
        ("GT", "T3", "ZERO", "T2", 0),
        ("ADD", "T0", "T0", "T3", 0),        # 256 iff marker != 3
        ("CONST", "T3", 0, 7, 2),            # 256
        ("SUB", "T3", "T3", "T0", 0),        # 256 iff relay
        ("MULQ", "EMIT", "T1", "T1", 0),     # 256 iff cue
        ("MOV", "PAY0", "EMIT", 0, 0),
        ("SEL", "PAY0", "T1", "IN0_0", 0),   # cue ? cue : received payload
        ("MOV", "PAY1", "EMIT", 0, 0),
        ("CONST", "CHAN", 0, 0, 3),          # scratch (C=1: channel 0)
        ("CONST", "RPORT", 0, 0, 1),         # scratch (no plastic routing)
        ("SEL", "PAY1", "CHAN", "RPORT", 0),  # cue ? 3 : 1
        ("ADD", "EMIT", "EMIT", "T3", 0),
        ("GT", "T0", "IN0_0", "ZERO", 0),
        ("GT", "T2", "ZERO", "IN0_0", 0),
        ("SUB", "T0", "T0", "T2", 0),        # arrival sign*256 or 0
        ("MULQ", "T2", "T0", "T0", 0),
        ("SUB", "T1", "T0", "S0", 0),
        ("MULQ", "T1", "T1", "T2", 0),
        ("ADD", "S0", "S0", "T1", 0),        # S0 := arrival sign where one arrived
    ])


def c1b_rule_physics() -> Physics:
    return Physics(topology="ring", n_sites=16, radius=1, rules=2, setrule=1, prog_len=8,
                   update_mode="sync", update_period=1, decay_shift=0, state_dim=1)


def rule_switch_hold(ph: Physics) -> np.ndarray:
    """HOLD solved ONLY through SETRULE: the cue sign selects the rule, and
    each rule writes a fixed sign into S0 every tick. freeze_rule must kill
    it (the positive control for C1b's R clause). -> genome [2, L, 5]."""
    assert ph.rules == 2 and ph.setrule
    r0 = assemble(ph, [
        ("CONST", "T0", 0, 7, 1),            # 128
        ("GT", "T1", "SENSE", "T0", 0),      # 256 on a + cue
        ("SHR", "T1", "T1", 8, 0),           # 1 / 0
        ("SETRULE", "T3", "T1", 0, 0),       # -> rule 1 on a + cue, else stay 0
        ("CONST", "S0", 0, 7, -2),           # -256
    ])
    r1 = assemble(ph, [
        ("CONST", "T0", 0, 7, -1),           # -128
        ("GT", "T1", "T0", "SENSE", 0),      # 256 on a - cue
        ("SHR", "T1", "T1", 8, 0),
        ("CONST", "T2", 0, 0, 1),
        ("SUB", "T1", "T2", "T1", 0),        # 0 on a - cue, else 1
        ("SETRULE", "T3", "T1", 0, 0),
        ("CONST", "S0", 0, 7, 2),            # +256
    ])
    return np.stack([r0, r1])


def c1b_route_physics() -> Physics:
    """Ring r2: ports 0 and 3 are at distance 2, ports 1 and 2 at distance 1
    (topology.build offsets -2,-1,1,2). RELAY at d=2 puts the actuator on a
    distance-2 port of the sensor, whichever side it is on."""
    return Physics(topology="ring", n_sites=64, radius=2, dest_mode="sample", fanout=8,
                   plastic_route=1, adapt_shift=0, lat_base=1, lat_hop=0, lat_jitter=0,
                   loss=0.0, payload_width=1, channels=1, update_mode="sync",
                   update_period=1, decay_shift=0, state_dim=3, prog_len=24)


def route_relay(ph: Physics) -> np.ndarray:
    """RELAY solved ONLY through plastic routing. During the 4 cue ticks the
    sensor walks its 4 ports (counter S2) and writes w: a + cue opens the
    distance-2 ports and closes the distance-1 ports; a - cue does the
    opposite. From then on the sensor (role latch S1) pings every tick
    through w. The actuator's S0 := +256 if a ping arrived this tick, else
    -256. freeze_routing must kill it (the positive control for
    freeze_routing's absence reading)."""
    return assemble(ph, [
        ("CONST", "T0", 0, 7, 1),            # 128
        ("GT", "T1", "SENSE", "T0", 0),
        ("SUB", "T2", "ZERO", "T0", 0),
        ("GT", "T2", "T2", "SENSE", 0),
        ("ADD", "T3", "T1", "T2", 0),        # 256 iff cue
        ("SUB", "T1", "T1", "T2", 0),        # cue sign*256 or 0
        ("MAX", "S1", "S1", "T3", 0),        # role latch: I am the sensor
        ("MOV", "RPORT", "S2", 0, 0),        # port j = counter (mod R in the engine)
        ("SHR", "T2", "S2", 1, 0),
        ("XOR", "T2", "S2", "T2", 0),
        ("CONST", "T0", 0, 0, 1),
        ("MOD", "T2", "T2", "T0", 0),        # near = bit0 ^ bit1 of j (1 on ports 1, 2)
        ("CONST", "T0", 0, 7, 255),          # BIG = 32640
        ("SUB", "CHAN", "ZERO", "T0", 0),    # -BIG (scratch; C=1: channel 0)
        ("MOV", "RVAL", "T2", 0, 0),
        ("SEL", "RVAL", "CHAN", "T0", 0),    # near ? -BIG : +BIG
        ("MULQ", "RVAL", "RVAL", "T1", 0),   # x cue sign; 0 outside the cue
        ("SHR", "T2", "T3", 8, 0),
        ("ADD", "S2", "S2", "T2", 0),        # counter++ on cue ticks
        ("MOV", "EMIT", "S1", 0, 0),         # ping every tick once I am the sensor
        ("CONST", "PAY0", 0, 7, 2),
        ("GT", "T0", "CNT0", "ZERO", 0),
        ("ADD", "S0", "T0", "T0", 0),
        ("ADDI", "S0", "S0", 0, -256),       # +256 if a ping arrived, else -256
    ])


def c1b_da_physics() -> Physics:
    """The D-A fixture: delay == delta (RELAY d=1, delta 4, latency 4)."""
    return Physics(topology="ring", n_sites=24, radius=1, dest_mode="all", lat_base=4,
                   lat_hop=0, lat_jitter=0, loss=0.0, update_mode="sync",
                   update_period=1, decay_shift=0, prog_len=12)


def _eq(k: int, src: str, dst: str) -> list:
    """dst := 256 iff src == k, else 0 (uses T0, T3 as scratch)."""
    return [
        ("CONST", "T3", 0, 0, k),
        ("SUB", dst, src, "T3", 0),
        ("GT", "T0", dst, "ZERO", 0),
        ("GT", "T3", "ZERO", dst, 0),
        ("ADD", "T0", "T0", "T3", 0),
        ("CONST", dst, 0, 7, 2),
        ("SUB", dst, dst, "T0", 0),
    ]


def sham_positive_hold(ph: Physics) -> np.ndarray:
    """F_sham_positive (PREREG_PTE_C1b A1.1): echo_hold whose relays must be
    RE-ARMED by a packet that is in flight across the inter-trial interval.
    The sensor, on receiving its echo (marker sum 2) at the readout tick,
    emits an arming packet (0, 7). A neighbour relays a cue (marker 3) only
    if armed, then disarms itself (S1 := 256); an arming packet clears S1.
    Relays start armed, so trial 0 works. Flushing in-flight traffic at the
    first ITI tick kills the arming packets, so every later trial fails.
    Physics: c1b_echo_physics (delay 5; HOLD cue_len 2, gap 8, iti 2)."""
    return assemble(ph, [
        ("CONST", "T0", 0, 7, 1),            # 128
        ("GT", "T1", "SENSE", "T0", 0),
        ("SUB", "T2", "ZERO", "T0", 0),
        ("GT", "T2", "T2", "SENSE", 0),
        ("SUB", "T1", "T1", "T2", 0),        # cue sign*256 or 0
        ("MOV", "RVAL", "T1", 0, 0),         # hold the cue (scratch: no plastic routing)
        *_eq(3, "IN0_1", "T1"),              # T1 = 256 iff a cue packet arrived
        ("GT", "T2", "S1", "ZERO", 0),       # 256 iff disarmed
        ("CONST", "T0", 0, 7, 2),
        ("SUB", "T2", "T0", "T2", 0),        # 256 iff armed
        ("MULQ", "T1", "T1", "T2", 0),       # relay = cue packet AND armed
        ("MAX", "S1", "S1", "T1", 0),        # disarm after relaying
        *_eq(7, "IN0_1", "T2"),              # T2 = 256 iff an arming packet arrived
        ("CONST", "T0", 0, 7, 2),
        ("SUB", "T0", "T0", "T2", 0),
        ("MULQ", "S1", "S1", "T0", 0),       # re-arm: S1 := 0
        *_eq(2, "IN0_1", "T2"),              # T2 = 256 iff my echo arrived
        ("MULQ", "EMIT", "RVAL", "RVAL", 0),
        ("ADD", "EMIT", "EMIT", "T1", 0),
        ("ADD", "EMIT", "EMIT", "T2", 0),    # emit on cue, relay or echo
        ("MULQ", "PAY0", "RVAL", "RVAL", 0),
        ("MULQ", "T0", "IN0_0", "T1", 0),    # relayed payload (0 unless relaying)
        ("SEL", "PAY0", "RVAL", "T0", 0),    # cue ? cue : relayed payload
        ("CONST", "T3", 0, 0, 1),
        ("CONST", "T0", 0, 0, 7),
        ("MOV", "PAY1", "T1", 0, 0),
        ("SEL", "PAY1", "T3", "T0", 0),      # relay ? 1 : 7
        ("MOV", "T0", "PAY1", 0, 0),
        ("MULQ", "CHAN", "RVAL", "RVAL", 0),  # scratch (C=1: channel 0)
        ("CONST", "T3", 0, 0, 3),
        ("MOV", "PAY1", "CHAN", 0, 0),
        ("SEL", "PAY1", "T3", "T0", 0),      # cue ? 3 : previous
        ("GT", "T0", "IN0_0", "ZERO", 0),
        ("GT", "T2", "ZERO", "IN0_0", 0),
        ("SUB", "T0", "T0", "T2", 0),        # arrival sign*256 or 0
        ("MULQ", "T2", "T0", "T0", 0),
        ("SUB", "T1", "T0", "S0", 0),
        ("MULQ", "T1", "T1", "T2", 0),
        ("ADD", "S0", "S0", "T1", 0),        # S0 := arrival sign where one arrived
    ])
