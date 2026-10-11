"""BEL-48H Window 6 block 2: GENERALITY of two-fragment complementation (frozen by prereg s11 before any run).

    python3 plan_w6b2.py OUT.json

Confound-free fragment pairs built from evolved machine shapes (W3a/W6 origins: LD T,n + LDIR): writer A writes the two
LD T,n bytes into the partner's window with CONSTRUCTED writes (LD A,0x08; LD (T),A; INC T; LD A,n; LD (T),A) and holds
NO LDIR; carrier B holds only LDIR (+HALT) at p3. Each variant is asserted at build time: A, B non-FUNC; composite FUNC;
0 single-substitution FUNC mutants of A and of B, under both ENDOGENOUS_PARTIAL and ENDOGENOUS_COPY.
Arms per variant (40 seeds, shared by the 6 arms = paired; distinct across variants): PARTIAL x {AB, A, B, none},
PARTIAL target_fill zero x AB, ENDOGENOUS_COPY x AB. PAIRED init, WELL_MIXED, 300 ticks, HeredityWorld."""
import hashlib, json, sys, pathlib
sys.path.insert(0, pathlib.Path(__file__).resolve().parents[4].as_posix()); sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix())
from plan_w5 import BASE
SEED_BASE = 52_000_000_000_000
CANDIDATES = ((13, 0x40, 34), (4, 0xA0, 10), (30, 0x40, 45), (40, 0x41, 52), (8, 0x42, 20))


def build(p1, n, p3):
    from prometheus.z80atlas import vm
    A = bytearray(64); A[:10] = bytes([vm.LD_T_n, 64 + p1, vm.LD_A_n, 0x08, vm.LD_pT_A, vm.INC_T, vm.LD_A_n, n, vm.LD_pT_A, vm.HALT])
    B = bytearray(64); B[p3] = vm.LDIR; B[p3 + 1] = vm.HALT
    C = bytearray(B); C[p1] = 0x08; C[p1 + 1] = n
    return bytes(A), bytes(B), bytes(C)


def valid(v):
    from prometheus.z80atlas import vm
    from prometheus.z80atlas.world import Config
    from belinst import Func
    A, B, C = build(*v)
    if vm.LDIR in A:
        return False
    for repro in ("ENDOGENOUS_PARTIAL", "ENDOGENOUS_COPY"):
        f = Func(Config(reproduction=repro, physics="v2"))
        if f(A) or f(B) or not f(C):
            return False
        for t in (A, B):
            if any(f(t[:p] + bytes([b]) + t[p + 1:]) for p in range(64) for b in range(256) if b != t[p]):
                return False
    return True


def plan():
    variants = [v for v in CANDIDATES if valid(v)][:3]
    assert len(variants) == 3, variants
    P = []
    for vi, v in enumerate(variants):
        A, B, _ = build(*v)
        for k in range(40):
            for arm, repro, fill, tx in (("AB", "ENDOGENOUS_PARTIAL", "preserve", [A.hex(), B.hex()]), ("A", "ENDOGENOUS_PARTIAL", "preserve", [A.hex()]),
                                         ("B", "ENDOGENOUS_PARTIAL", "preserve", [B.hex()]), ("none", "ENDOGENOUS_PARTIAL", "preserve", []),
                                         ("AB_zero", "ENDOGENOUS_PARTIAL", "zero", [A.hex(), B.hex()]), ("AB_copy", "ENDOGENOUS_COPY", "preserve", [A.hex(), B.hex()])):
                cfg = dict(BASE, reproduction=repro, target_fill=fill, init_draws="PAIRED", ticks=300)
                if tx:
                    cfg["init_tapes"] = tx
                P.append({"lane": "G", "cell": "V%d_%s" % (vi, "_".join("%02x" % x for x in v)), "arm": arm, "pair": k, "k": k,
                          "kind": "heredity", "seed": SEED_BASE + vi * 10 ** 6 + k, "cfg": cfg, "variant": list(v)})
    for i, p in enumerate(P):
        p["id"] = "w6b2_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest(), sorted({p["cell"] for p in P}))
