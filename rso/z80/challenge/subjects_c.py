"""C-017-T040 challenge subjects (Pallas, Q3). Adversarial constructed tapes and one adversarial arm against the FROZEN
Z80 attribution assay (FREEZE_Z80_ATTRIBUTION v1.0.0). Read-only against archaeon/; nothing here edits a frozen file.

Seeds: the challenge partition 17_040_000..17_049_999 (PREREGISTRATION s6: "challenge 17_040_000 (Pallas, free use)").
Every seed used by this set is listed by seeds_used() and checked disjoint from 17_050_xxx (confirmatory) and from every
range in subjects.REGISTERED before any case runs (conflicts() == []).
"""
from archaeon.z80atlas import tasks as T, vm
from rso.z80 import subjects as S

I = vm.I
G = S.G

# ---------------------------------------------------------------- adversarial parents (unit known answers)


def CDIST():
    """Counterfactual-invariant reconstructor (PREREGISTRATION s11.5 made concrete). IN A / OUT A / NOP at 0..2 like RECON,
    then: child[0] = circdist(t0, t2) and child[1] = child[0] + 1, where t0, t2 are the TARGET cell's bytes 0 and 2 read
    from the window; then COPY own bytes 2..28 to the window; bytes 29..31 kept. 29/32 written (>= copy_min_frac .9).
    circdist(a, b) = min((a-b) mod 256, (b-a) mod 256) is invariant under BOTH frozen counterfactuals (complement negates
    a-b; +0x55 preserves it), so bytes 0..1 are tagged P although their value is a function of the target's content: over
    a kin target (t0, t2) = (21, 0) they are IN A / OUT A; over an empty target (0, 0) they are NOP / LD A,imm (dead).
    By observe.py's own definition (lines 12-14: K = 'a written byte whose value ... changes with the target cell's prior
    content') these are K bytes. The unit-level fact needs no population; the arm CDIST_ENDO_IMPL below shows the class."""
    return T.pad([I(21, 0), I(22, 0), 0,
                  I(19, 0, 0), 130,          # LD A,(130)  A = t2
                  I(2, 1, 1),                # LD B,A
                  I(19, 0, 0), 128,          # LD A,(128)  A = t0
                  I(4, 1),                   # SUB A,B     A = t0 - t2 (mod 256)
                  I(1, 2), 128,              # LD C,128
                  I(12, 2),                  # CMP A,C     cf = A < 128
                  I(17), 1,                  # JC +1       skip NEG when A < 128
                  I(25),                     # NEG A
                  I(19, 0, 1), 128,          # LD (128),A  child[0] = circdist(t0, t2)
                  I(5, 0),                   # INC A
                  I(19, 0, 1), 129,          # LD (129),A  child[1] = child[0] + 1
                  I(1, 1), 2,                # LD B,2
                  I(1, 2), 130,              # LD C,130
                  I(1, 3), 27,               # LD D,27
                  I(20),                     # COPY        mem[C] = mem[B]; B++; C++
                  I(6, 3),                   # DEC D
                  I(16), 0xFC,               # JNZ -4
                  I(23)], G)                 # HALT


def XORW():
    """XOR writer: child[0] = t0 XOR t2 of the target (21 over kin), then COPY own 1..29; bytes 30..31 kept (30/32 written).
    Invariant under the complement (both operands flip) but NOT under +0x55: the frozen two-sample counterfactual tags byte
    0 K. Witness W1 for edit E1 (drop the +0x55 sample): under E1 byte 0 becomes P."""
    return T.pad([I(21, 0), I(22, 0), 0,
                  I(19, 0, 0), 130, I(2, 1, 1), I(19, 0, 0), 128, I(7, 1),      # A = t0 ^ t2
                  I(19, 0, 1), 128,                                            # LD (128),A
                  I(1, 1), 1, I(1, 2), 129, I(1, 3), 29, I(20), I(6, 3), I(16), 0xFC, I(23)], G)


def INPW():
    """Input writer: IN A / OUT A, then child[0] = the INPUT byte of the parent's case 0; COPY own 1..31 (32/32 written).
    The child's byte 0 depends on the world's input stream, not on the target cell: the frozen counterfactual (same input,
    altered pre-window) tags it P. With input 21 the child is IN A / OUT A ... (functional); with any other input it is not.
    Probe P-INPUT (ENV means the target cell, not 'the environment') and witness W5 for edit E5 (counterfactual run with an
    empty input: byte 0 becomes K)."""
    return T.pad([I(21, 0), I(22, 0), I(19, 0, 1), 128,
                  I(1, 1), 1, I(1, 2), 129, I(1, 3), 31, I(20), I(6, 3), I(16), 0xFC, I(23)], G)


def JROP():
    """IN A; JR +<byte 2>; OUT A; HALT. With byte 2 = 0 the jump is a NOP and the tape echoes. Witness W2 for edit E2 (the
    sufficiency filler): with tags P P K P P ..., restrict(.., 'P') zeroes byte 2 -> JR +0 -> F0 -> ENDO under the frozen
    zero filler; under a NOP-opcode filler 0x1E the operand becomes +30 -> no output -> not F0 -> ENV."""
    return T.pad([I(21, 0), I(14), 0, I(22, 0), I(23)], G)


def DORMANT():
    """Sufficiency vs expression (probe P-DORMANT): [IN A, OUT A, NOP] then a second [IN A, OUT A] then HALT. With tags
    K K K P P P ... the FIRST output (the scored one) comes from the K bytes; the P bytes alone also echo (after three NOPs),
    so assay.label says ENDO. The registered rule (PREREGISTRATION s4.4) chooses this; recorded for the interpretation."""
    return T.pad([I(21, 0), I(22, 0), 0, I(21, 0), I(22, 0), I(23)], G)


HALF = T.pad([I(21, 0), I(1, 1), 0x80, I(12, 1), I(17), 0x01, I(23), I(22, 0), I(23)], G)   # tests/test_attribution.py:25

# ---------------------------------------------------------------- the adversarial arm (same world / physics / pressure / horizon as the ENV arm)
CDIST_ARM = dict(name="CDIST_ENDO_IMPL", gt="ENV", origin="INSERTED", starter="CDIST", n=128, phys="ENDOGENOUS_COPY",
                 press="implicit_survival", epochs=100)
STARTERS = dict(S.STARTERS, CDIST=CDIST)


def spec(arm, epochs=None):
    """subjects.spec for an arm whose starter may be one of this file's (the frozen function is not modified; copied logic)."""
    from archaeon.z80atlas import grammar as GR
    init = arm.get("init", "random")
    s = GR.make(S.WORLD, S.REP, arm["phys"], [arm["press"]], S.TASK, "local_byte", init, stage="early", reason="z80attr-challenge:" + arm["name"])
    s["budget"] = dict(s["budget"], max_epochs=epochs or arm["epochs"])
    if arm["starter"]:
        s["transplant"] = {"from_run": None, "tapes": [STARTERS[arm["starter"]]().hex()] * arm["n"]}
        s["init"] = "transplanted_lineage"
        s["spec_id"] = GR.spec_id(s) + "-t"
    return s


# ---------------------------------------------------------------- seeds (all inside 17_040_000..17_049_999)
N_ARM = 6                                     # records per registered arm (S3 / S4 / B6)
PART = "challenge"


def arm_seeds(name):
    return S.seeds(name, PART, N_ARM)


CDIST_SEEDS = [17_040_501 + k for k in range(8)]
HZ_RECON_SEEDS = [17_047_601 + k for k in range(6)]          # RECON_ENDO_IMPL at 20 / 40 / 60 epochs (same seeds)
HZ_HENDO_SEEDS = [17_040_601 + k for k in range(12)]         # H_ENDO_GATED at 200 epochs
HZ_HEXT_SEEDS = [17_044_601 + k for k in range(6)]           # H_EXT_SHORT at 30 epochs
PL_SCAN = (17_049_001, 17_049_999)                            # probe-case lottery scan (probe cases only; two engine runs)


def seeds_used():
    out = []
    for a in S.NAMES:
        out += arm_seeds(a)
    out += CDIST_SEEDS + HZ_RECON_SEEDS + HZ_HENDO_SEEDS + HZ_HEXT_SEEDS + list(range(PL_SCAN[0], PL_SCAN[1] + 1))
    return out


def conflicts():
    bad = [s for s in seeds_used() if not (17_040_000 <= s <= 17_049_999)]
    bad += [s for s in seeds_used() if any(lo <= s <= hi for lo, hi in S.REGISTERED)]
    bad += [s for s in seeds_used() if 17_050_000 <= s <= 17_059_999]
    return sorted(set(bad))
