"""BEL-48H Window 2 plan: heredity and genetic provenance (frozen by BEL_48H_PREREG.md s4 before any W2 run).

    python3 plan_w2.py OUT.json

H1  founder-tagged heredity in fresh random worlds where FUNC arises (WELL_MIXED; historical physics, measurement only)
H2  fragment complementation: carriers of two NON-functional fragments of the minimal copier, injected as a quarter of
    the initial population under PAIRED init (identical random majority across arms):
      A  'prefix copier': copies its own 2 bytes LD T,64 (stored at 20-21) into partner window 0-1, then HALT
      B  'LDIR carrier':  LD A,1 ; LDIR at 0-2 (T = 0: smears itself; never writes a window)
    arms AB, A, B, none under ENDOGENOUS_PARTIAL (unwritten target bytes survive into the child); AB also under
    ENDOGENOUS_COPY (a 2-byte write is not viable: the physics forbids the complementation) as the physics control."""
import hashlib
import json
import pathlib
import sys

SEED_BASE = 48_500_000_000_000
BASE = dict(world="GRID", representation="Z80_64", layout="SHARED", reproduction="ENDOGENOUS_PARTIAL", pressure="IMPLICIT",
            spatial="WELL_MIXED", task="INC", scoring="ATOMIC", read_gate="ABR", env_dynamics="FIXED", mutation="BYTE",
            mutation_rate="MED", recombination="NONE", init="RANDOM", physics="v2", ticks=500, cells=256, budget=256)


def fragments():
    sys.path.insert(0, pathlib.Path(__file__).resolve().parents[4].as_posix())
    from prometheus.z80atlas import vm
    A = bytearray(64); A[:8] = bytes([vm.LD_S_n, 20, vm.LD_T_n, 64, vm.LD_C_n, 2, vm.LDIR, vm.HALT]); A[20:22] = bytes([vm.LD_T_n, 64])
    B = bytearray(64); B[:3] = bytes([vm.LD_A_n, 1, vm.LDIR])
    return bytes(A).hex(), bytes(B).hex()


def plan():
    A, B = fragments()
    P = []; lanes = {}

    def add(lane, cell, k, cfg, arm=None, pair=None):
        ln = lanes.setdefault(lane, len(lanes))
        P.append({"lane": lane, "cell": cell, "arm": arm, "pair": pair, "k": k, "kind": "reach" if lane == "H1" else "heredity",
                  "seed": SEED_BASE + ln * 10 ** 9 + k, "cfg": dict(BASE, **cfg)})

    for r, n in (("ENDOGENOUS_PARTIAL", 150), ("PAIR_EXECUTION", 150), ("ENDOGENOUS_COPY", 150)):
        for k in range(n):
            add("H1", "%s/Z80_64/WELL_MIXED" % r, k, {"reproduction": r})
    for k in range(100):
        add("H1", "ENDOGENOUS_COPY/VM_COPY/WELL_MIXED", k, {"reproduction": "ENDOGENOUS_COPY", "representation": "VM_COPY"})
    for k in range(100):
        for arm, tx in (("AB", [A, B]), ("A", [A]), ("B", [B]), ("none", [])):
            c = {"init_draws": "PAIRED", "ticks": 300}
            if tx:
                c["init_tapes"] = tx
            add("H2", "PARTIAL/" + arm, k, c, arm, k)
        add("H2", "COPY/AB", k, {"init_draws": "PAIRED", "ticks": 300, "reproduction": "ENDOGENOUS_COPY", "init_tapes": [A, B]}, "COPY_AB", k)
    for i, p in enumerate(P):
        p["id"] = "w2_%05d" % i
    return P


if __name__ == "__main__":
    P = plan()
    b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b)
    print(len(P), hashlib.sha256(b).hexdigest())
