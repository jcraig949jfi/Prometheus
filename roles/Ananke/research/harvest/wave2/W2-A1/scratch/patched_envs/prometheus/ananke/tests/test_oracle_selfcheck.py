"""Self-checks of the PTE v1 CPU oracle ALONE (no GPU engine involved).

Expected values are derived by hand from roles/Ananke/pte/DESIGN.md.
Register layout used by most tests (D=2, P=1, C=1):
    S0=0 S1=1 T0..T3=2..5 emit=6 chan=7 rport=8 rval=9 pay0=10
    (NW=11) IN_sum0=11 IN_cnt0=12 SENSE=13 ENERGY=14 ZERO=15 (NR=16)
"""
import importlib.util
import pathlib

import numpy as np
import pytest

_P = pathlib.Path(__file__).resolve().parents[1] / "oracle.py"
_spec = importlib.util.spec_from_file_location("pte_oracle", _P)
O = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(O)

S0, S1, EMIT, CHAN, RPORT, RVAL, PAY0 = 0, 1, 6, 7, 8, 9, 10
IN_SUM, IN_CNT, SENSE, ENERGY, ZERO = 11, 12, 13, 14, 15
NOP = (0, 0, 0, 0, 0)


def base_phys(**kw):
    p = dict(topology="ring", n_sites=1, radius=1, k_random=2, rewire=0,
             state_dim=2, payload_width=1, channels=1, fanout=1,
             dest_mode="sample", loss=0.0, loss_per_hop=0, lat_base=1,
             lat_hop=0, lat_jitter=0, dup=0.0, noise=0, cap=0,
             collision="none", decay_shift=0, update_mode="sync",
             update_period=1, update_p=1.0, rules=1, prog_len=4,
             plastic_route=0, adapt_shift=0, wimm=0, setrule=0, mut_site=0.0,
             e_income=0, e_max=100, c_emit=0, c_op=0, c_mem=0, topo_seed=1)
    p.update(kw)
    return p


def pad(prog, L):
    return list(prog) + [NOP] * (L - len(prog))


def run1(prog, sense_val=0, T=1, ws=12345, **kw):
    """1-site world, every rule = prog. Returns oracle output dict."""
    phys = base_phys(**kw)
    L, G = phys["prog_len"], phys["rules"]
    genomes = [[pad(prog, L) for _ in range(G)]]
    sense = np.full((T, 1, 1), sense_val, dtype=np.int64)
    return O.run(phys, genomes, [ws], sense, T)


# ------------------------------------------------------------- hashing
def test_hash32_known_values():
    # hash32(0): every step keeps 0 (0 ^ 0 = 0, 0 * k = 0) -> 0
    assert O.hash32(0) == 0
    # hash32(1):
    #   x=1; x ^= 1>>16 (=0)                      -> 0x00000001
    #   x = 1 * 0x7FEB352D                         -> 0x7FEB352D
    #   x >> 15 = 0b0_1111_1111_1101_0110 = 0xFFD6
    #   x ^= 0xFFD6: 352D^FFD6 = CAFB              -> 0x7FEBCAFB
    #   x * 0x846CA68B = 0x422BDF5B_6889F849; &M32 -> 0x6889F849
    #   x >> 16 = 0x6889; F849 ^ 6889 = 90C0       -> 0x688990C0
    assert O.hash32(1) == 0x688990C0
    # hash32(0x10000):
    #   x ^= x>>16 (=1)                            -> 0x00010001
    #   0x10001 * 0x7FEB352D = 0x7FEB_B518352D     -> 0xB518352D
    #   x >> 15 = 0x16A30; x ^= it: 352D^6A30=5F1D, B518^0001=B519
    #                                              -> 0xB5195F1D
    #   * 0x846CA68B = 0x5DADF18F_DCAF72BF          -> 0xDCAF72BF
    #   x >> 16 = 0xDCAF; 72BF ^ DCAF = AE10       -> 0xDCAFAE10
    assert O.hash32(0x10000) == 0xDCAFAE10
    # masking: bits above 32 are dropped before hashing
    assert O.hash32(1 + (1 << 32)) == O.hash32(1)


def test_H_known_values():
    assert O.H() == 0x811C9DC5                    # no keys: FNV offset
    # H(0) = hash32(0x811C9DC5 ^ 0):
    #   ^>>16: 0x811C9DC5 ^ 0x811C = 0x811C1CD9
    #   * 0x7FEB352D -> low32 0xA61CFF25
    #   ^>>15 (0x14C39) -> 0xA61DB31C
    #   * 0x846CA68B -> low32 0x74146834
    #   ^>>16 (0x7414): 6834 ^ 7414 = 1C20 -> 0x74141C20
    assert O.H(0) == 0x74141C20
    assert O.H(0, 1) == O.hash32(0x74141C20 ^ 1)
    assert O.H(-1) == O.hash32(0x811C9DC5 ^ 0xFFFFFFFF)
    assert O.p16(0.5) == 32768 and O.p16(1.0) == 65536


# ------------------------------------------------------------- 16 ops
def s0(out):
    return int(out["S"][0, 0, 0])


def test_op0_nop():
    assert s0(run1([(16, 0, SENSE, 0, 0)], sense_val=9)) == 0   # op 16 mod 16 = NOP


def test_op1_mov():
    assert s0(run1([(1, 0, SENSE, 0, 0)], sense_val=-7)) == -7
    # dst reduced mod NW=11: dst 11 -> S0
    assert s0(run1([(1, 11, SENSE, 0, 0)], sense_val=5)) == 5


def test_op2_add():
    assert s0(run1([(2, 0, SENSE, ENERGY, 0)], sense_val=300)) == 400
    assert s0(run1([(2, 0, SENSE, ENERGY, 0)], sense_val=32767)) == 32767  # sat


def test_op3_sub():
    assert s0(run1([(3, 0, SENSE, ENERGY, 0)], sense_val=300)) == 200
    assert s0(run1([(3, 0, SENSE, ENERGY, 0)], sense_val=-32767)) == -32767


def test_op4_mulq():
    # (-300*100) >> 8 = -30000 >> 8 = floor(-117.19) = -118
    assert s0(run1([(4, 0, SENSE, ENERGY, 0)], sense_val=-300)) == -118
    # 32767*32767 >> 8 = 4194048 -> sat 32767
    assert s0(run1([(4, 0, SENSE, SENSE, 0)], sense_val=32767)) == 32767


def test_op5_addi():
    assert s0(run1([(5, 0, SENSE, 0, -5)], sense_val=10)) == 5


def test_op6_const():
    # I=3, bf=10 -> 10&7=2 -> 3*4 = 12
    assert s0(run1([(6, 0, 0, 10, 3)])) == 12
    # I=-128, bf=7 -> -128*128 = -16384
    assert s0(run1([(6, 0, 0, 7, -128)])) == -16384


def test_op7_gt():
    assert s0(run1([(7, 0, SENSE, ENERGY, 0)], sense_val=101)) == 256
    assert s0(run1([(7, 0, SENSE, ENERGY, 0)], sense_val=100)) == 0


def test_op8_sel():
    # S0 == 0 (not > 0) -> B = ENERGY = 100
    assert s0(run1([(8, 0, SENSE, ENERGY, 0)], sense_val=7)) == 100
    # set S0 = 1 first -> A = SENSE = 7
    assert s0(run1([(6, 0, 0, 0, 1), (8, 0, SENSE, ENERGY, 0)], sense_val=7)) == 7


def test_op9_max():
    assert s0(run1([(9, 0, SENSE, ENERGY, 0)], sense_val=-5)) == 100
    assert s0(run1([(9, 0, SENSE, ENERGY, 0)], sense_val=150)) == 150


def test_op10_shr():
    # -9 >> (17 & 15 = 1) = -5 (arithmetic, floor)
    assert s0(run1([(10, 0, SENSE, 17, 0)], sense_val=-9)) == -5
    assert s0(run1([(10, 0, SENSE, 3, 0)], sense_val=100)) == 12


def test_op11_xor():
    assert s0(run1([(11, 0, SENSE, 0, 0), ], sense_val=5)) == 5     # 5 ^ S0(0)
    # -1 ^ 32767 = -32768 -> sat -32767
    out = run1([(6, 1, 0, 0, -1), (11, 0, SENSE, 1, 0)], sense_val=32767)
    assert s0(out) == -32767


def test_op12_mod():
    # A=ENERGY=13, B=SENSE=-4 -> 13 mod 5 = 3
    assert s0(run1([(12, 0, ENERGY, SENSE, 0)], sense_val=-4, e_max=13)) == 3
    # A=SENSE=-7, B=ENERGY=3 -> -7 mod 4 = 1 (floor mod)
    assert s0(run1([(12, 0, SENSE, ENERGY, 0)], sense_val=-7, e_max=3)) == 1


def test_op13_rand():
    ws = 777
    # m = 5 -> (H(ws, RANDOP=7, t=0, n=0, i=0) mod 11) - 5
    exp = O.H(ws, 7, 0, 0, 0) % 11 - 5
    assert s0(run1([(13, 0, SENSE, 0, 0)], sense_val=-5, ws=ws)) == exp
    # at instruction index 1 the sub-index is i=1
    exp1 = O.H(ws, 7, 0, 0, 1) % 11 - 5
    assert s0(run1([NOP, (13, 0, SENSE, 0, 0)], sense_val=5, ws=ws)) == exp1
    assert s0(run1([(13, 0, ZERO, 0, 0)], ws=ws)) == 0            # m = 0


def test_op14_setrule():
    # G=3, every rule: SETRULE r_next = SENSE mod 3; SENSE=5 -> 2
    out = run1([(14, 0, SENSE, 0, 0)], sense_val=5, rules=3, setrule=1)
    assert int(out["r"][0, 0]) == 2
    # last one wins: 5 then 4 -> 4 mod 3 = 1
    out = run1([(14, 0, SENSE, 0, 0), (14, 0, ENERGY, 0, 0)], sense_val=5,
               rules=3, setrule=1, e_max=4)
    assert int(out["r"][0, 0]) == 1
    # setrule dial off: r stays at init H(ws, INIT=9, 0, n=0, 7) mod G
    ws = 4242
    out = run1([(14, 0, SENSE, 0, 0)], sense_val=5, rules=3, setrule=0, ws=ws)
    assert int(out["r"][0, 0]) == O.H(ws, 9, 0, 0, 7) % 3
    # the new rule executes NEXT tick: rule g writes CONST S1 = g
    phys = base_phys(rules=3, setrule=1)
    genomes = [[pad([(14, 0, SENSE, 0, 0), (6, 1, 0, 0, g)], 4) for g in range(3)]]
    out = O.run(phys, genomes, [ws], np.full((2, 1, 1), 5), 2)
    assert int(out["S"][0, 0, 1]) == 2


def test_op15_wimm():
    # WIMM Kp_next[SENSE mod L] = sat(ENERGY); L=3, SENSE=4 -> slot 1 = 50
    # instr 1: ADDI S0 = ZERO + imm 0 + Kp[1]; uses start-of-run Kp
    prog = [(15, 0, SENSE, ENERGY, 0), (5, 0, ZERO, 0, 0), NOP]
    out = run1(prog, sense_val=4, T=2, prog_len=3, wimm=1, e_max=50)
    assert out["Kp"][0, 0].tolist() == [0, 50, 0]
    assert out["S0_trace"][:, 0, 0].tolist() == [0, 50]
    # later write to the same slot wins
    prog = [(15, 0, SENSE, ENERGY, 0), (15, 0, SENSE, SENSE, 0), NOP]
    out = run1(prog, sense_val=4, prog_len=3, wimm=1, e_max=50)
    assert out["Kp"][0, 0].tolist() == [0, 4, 0]
    # dial off: no effect
    out = run1([(15, 0, SENSE, ENERGY, 0)], sense_val=4, prog_len=3, wimm=0)
    assert out["Kp"][0, 0].tolist() == [0, 0, 0]


# ------------------------------------------------------------- topology
def test_torus_3x3_r1():
    nbr, dist = O.build_topology(base_phys(topology="torus", n_sites=9, radius=1))
    # order: dy=-1 (dx=0); dy=0 (dx=-1, dx=+1); dy=+1 (dx=0)
    assert nbr[4] == [1, 3, 5, 7]
    assert nbr[0] == [6, 2, 1, 3]       # (y,x)=(0,0): up wraps to y=2
    assert nbr[8] == [5, 7, 6, 2]       # (2,2)
    assert all(d == [1, 1, 1, 1] for d in dist)


def test_ring_r2():
    nbr, dist = O.build_topology(base_phys(topology="ring", n_sites=6, radius=2))
    assert nbr[0] == [4, 5, 1, 2]
    assert nbr[3] == [1, 2, 4, 5]
    assert dist[0] == [2, 1, 1, 2]


def test_global_topology():
    assert O.build_topology(base_phys(topology="global", n_sites=5)) == (None, None)


def test_LM():
    # 1 + (lat_base + lat_hop*maxdist + 2*jitter + 1)
    p = base_phys(topology="ring", n_sites=6, radius=2, lat_base=2, lat_hop=3,
                  lat_jitter=1)
    assert O.compute_LM(p, O.build_topology(p)[1]) == 1 + (2 + 6 + 2 + 1)


# ------------------------------------------------------------- transport
RELAY = [(1, EMIT, SENSE, 0, 0), (6, PAY0, 0, 0, 77), (1, S0, IN_SUM, 0, 0),
         (1, S1, IN_CNT, 0, 0)]


def relay_run(T=5, **kw):
    phys = base_phys(n_sites=2, lat_base=2, **kw)
    sense = np.zeros((T, 1, 2), dtype=np.int64)
    sense[0, 0, 0] = 1                  # only site 0 at t=0 emits
    return O.run(phys, [[RELAY]], [99], sense, T)


def test_relay_arrival_tick():
    out = relay_run()
    # emitted at t=0, delay = lat_base = 2 -> slot 2, delivered at t=2
    assert out["S0_trace"][:, 0, 1].tolist() == [0, 0, 77, 0, 0]
    assert out["S0_trace"][:, 0, 0].tolist() == [0] * 5
    assert out["stats"]["emitted"] == [1, 0, 0, 0, 0]
    assert out["stats"]["delivered"] == [1, 0, 0, 0, 0]
    assert out["LM"] == 4


def test_loss_one_delivers_nothing():
    out = relay_run(loss=1.0)
    assert out["S0_trace"].tolist() == np.zeros((5, 1, 2)).tolist()
    assert out["stats"]["delivered"] == [0] * 5
    assert out["stats"]["lost"] == [1, 0, 0, 0, 0]


def _collide(collision, cap):
    # ring N=3 r=1, dest_mode=all: sites 0 and 2 emit to both neighbours.
    # site 1 gets 2 packets (tot=2), sites 0 and 2 get 1 each. delay 1.
    phys = base_phys(n_sites=3, dest_mode="all", lat_base=1, collision=collision,
                     cap=cap)
    T = 3
    sense = np.zeros((T, 1, 3), dtype=np.int64)
    sense[0, 0, 0] = sense[0, 0, 2] = 1
    return O.run(phys, [[RELAY]], [5], sense, T)


def test_aloha_collision_discards():
    out = _collide("aloha", 1)
    assert out["S"][0, :, 1].tolist() == [0, 0, 0]       # final tick sees nothing
    assert out["S0_trace"][1, 0].tolist() == [77, 0, 77]  # site 1 discarded
    assert out["stats"]["collided"] == [0, 2, 0]
    ref = _collide("none", 1)
    assert ref["S0_trace"][1, 0].tolist() == [77, 154, 77]
    assert ref["stats"]["collided"] == [0, 0, 0]


def test_saturate_scales():
    out = _collide("saturate", 1)
    # sum 154*1//2 = 77, cnt 2*1//2 = 1
    assert out["S0_trace"][1, 0].tolist() == [77, 77, 77]


def test_saturate_floor_negative():
    # payload = ZERO - SENSE; sites 0 and 2 sense 1 and 2 -> payloads -1, -2.
    # site 1: sum -3, tot 2, cap 1 -> (-3*1)//2 = -2 (floor; truncation = -1)
    prog = [(1, EMIT, SENSE, 0, 0), (3, PAY0, ZERO, SENSE, 0),
            (1, S0, IN_SUM, 0, 0), (1, S1, IN_CNT, 0, 0)]
    phys = base_phys(n_sites=3, dest_mode="all", lat_base=1, collision="saturate",
                     cap=1)
    sense = np.zeros((2, 1, 3), dtype=np.int64)
    sense[0, 0, 0], sense[0, 0, 2] = 1, 2
    out = O.run(phys, [[prog]], [5], sense, 2)
    assert out["S0_trace"][1, 0].tolist() == [-2, -2, -1]
    assert int(out["S"][0, 1, 1]) == 1          # cnt 2*1//2
    assert out["stats"]["saturated"] == [0, 1]      # T=2 ticks


# ------------------------------------------------------------- determinism
def _rich():
    phys = base_phys(topology="smallworld", n_sites=16, rewire=300, state_dim=3,
                     payload_width=2, channels=2, fanout=2, loss=0.2,
                     loss_per_hop=1, lat_base=1, lat_hop=1, lat_jitter=2,
                     dup=0.3, noise=3, cap=3, collision="saturate",
                     decay_shift=3, update_mode="async", update_p=0.6, rules=2,
                     prog_len=8, plastic_route=1, adapt_shift=1, wimm=1,
                     setrule=1, mut_site=0.1, e_income=2, e_max=50, c_emit=1,
                     c_op=1, c_mem=1, topo_seed=17)
    rng = np.random.default_rng(0)
    B, G, L = 3, 2, 8
    g = np.stack([rng.integers(0, 256, (B, G, L)), rng.integers(0, 256, (B, G, L)),
                  rng.integers(0, 256, (B, G, L)), rng.integers(0, 256, (B, G, L)),
                  rng.integers(-128, 128, (B, G, L))], axis=-1)
    sense = rng.integers(-256, 257, (20, B, 16))
    return phys, g, [1, 2, 0xFFFFFFFF], sense


def test_determinism():
    phys, g, ws, sense = _rich()
    a = O.run(phys, g, ws, sense, 20)
    b = O.run(phys, g, ws, sense, 20)
    for k in a:
        if k == "stats":
            assert a[k] == b[k]
        elif isinstance(a[k], np.ndarray):
            assert np.array_equal(a[k], b[k]), k
        else:
            assert a[k] == b[k]
    st = a["stats"]
    for t in range(20):
        assert st["emitted"][t] + st["dup"][t] == st["delivered"][t] + st["lost"][t]
    assert sum(st["emitted"]) > 0            # the config actually exercises emission
    assert a["S"].shape == (3, 16, 3) and a["w"].shape == (3, 16, 4)
    assert a["Msum"].shape == (a["LM"], 3, 16, 2, 2)
