"""W2-54 shared: founder F, the world's two mutation kernels, and a structural jump-class screen.
Kernels (read from code, not fitted):
  birth copy error  (z8.py:413-417): each LDIR-copied byte flips ONE uniform bit w.p. cmr = 0.002
                     -> a specific (byte, bit) flip has prob 0.002/8 = 2.5e-4 per birth.
  in-place _mutate  (world.py:484-550, OPERAND, LOCAL, LOW): applied to BOTH halves after EVERY pair interaction
                     (world.py:826-827), incl. the child half at a birth; per non-opcode byte (z8.dis boundaries of
                     the CURRENT genome) w.p. 0.002: 45% +randint(-8,8), 45% one-bit flip, 10% uniform byte.
Screen jump_sites(g): linear-dis instructions at a <= 51 that are absolute JP-family (C3 C2 CA D2 DA) or relative
JR-family (18 20 28 30 38) whose landing (masked to the 128-byte tape) lies in 64..127 -- the W2-42 ejector shape."""
import sys, pathlib
sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
W2 = HERE.parent
sys.path.insert(0, str(W2 / "W2-35_rotation_leak"))
import frames  # noqa: E402
import world  # noqa: E402  (frames put C9 on the path)
import z8  # noqa: E402
F = frames.IMP
CMR = 0.002
MUT = 0.002
JPA = {0xC3: "JP", 0xC2: "JPNZ", 0xCA: "JPZ", 0xD2: "JPNC", 0xDA: "JPC"}
JPR = {0x18: "JR", 0x20: "JRNZ", 0x28: "JRZ", 0x30: "JRNC", 0x38: "JRC"}


def boundaries(g):
    return [a for a, _ in z8.dis(bytes(g))]


def operands(g):
    b = set(boundaries(g))
    return [i for i in range(len(g)) if i not in b]


def k_operand(old, new):
    """P(byte old -> new | this operand byte is hit by _mutate)."""
    if old == new:
        return 0.45 / 17 + 0.10 / 256
    d = (new - old) & 0xFF
    near = 1 if (d <= 8 or d >= 256 - 8) else 0
    bit = 1 if bin(old ^ new).count("1") == 1 else 0
    return 0.45 * near / 17 + 0.45 * bit / 8 + 0.10 / 256


def jump_sites(g):
    out = []
    for a, _s in z8.dis(bytes(g)):
        if a > 51:
            break
        op = g[a]
        if op in JPA and a + 2 < 64:
            land = g[a + 1] & 0x7F
            if land >= 64:
                out.append((a, JPA[op], land))
        elif op in JPR and a + 1 < 64:
            e = g[a + 1] - 256 if g[a + 1] > 127 else g[a + 1]
            land = (a + 2 + e) & 0x7F
            if land >= 64:
                out.append((a, JPR[op], land))
    return out


def mk(g, muts):
    b = bytearray(g)
    for p, v in muts.items():
        b[p] = v
    return bytes(b)


def band(s):
    """W2-42 bands on static side-0 FID keep; protected = STRONG (keep >= 0.85) and a copier."""
    if s["convF0"] >= 0.5:
        return "MORPH"
    if max(s["convF0"], s["convF1"]) < 0.5:
        return "NONCOPIER"
    k = s["keepF0"]
    return "STRONG" if k >= 0.85 else "PARTIAL" if k >= 0.62 else "F-LEVEL" if k >= 0.45 else "LOW"
