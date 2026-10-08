"""BEL-48H Window 1 plan (frozen by BEL_48H_PREREG.md s3 before any W1 run). Deterministic; prints count + sha256.

    python3 plan_w1.py OUT.json"""
import hashlib
import json
import sys

SEED_BASE = 48_100_000_000_000          # W1 v2 (amendment 1): fresh seeds; v1 base 48e12 superseded after 128 runs
BASE = dict(world="GRID", representation="Z80_64", layout="SHARED", reproduction="ENDOGENOUS_COPY", pressure="IMPLICIT",
            spatial="LOCAL", task="INC", scoring="ATOMIC", read_gate="ABR", env_dynamics="FIXED", mutation="BYTE",
            mutation_rate="MED", recombination="NONE", init="RANDOM", physics="v2", ticks=500, cells=256, budget=256)
REPROS = ("ENDOGENOUS_COPY", "ENDOGENOUS_PARTIAL", "OVERWRITE", "PAIR_EXECUTION", "CONSTRUCTIVE")


def plan():
    sys.path.insert(0, __import__("pathlib").Path(__file__).resolve().parents[4].as_posix())
    from prometheus.z80atlas import vm
    rep = vm.replicator(64).hex()
    P = []; lanes = {}

    def add(lane, cell, k, kind, cfg, arm=None, pair=None, cfg_b=None):
        ln = lanes.setdefault(lane, len(lanes))
        s = {"lane": lane, "cell": cell, "arm": arm, "pair": pair, "k": k, "kind": kind, "seed": SEED_BASE + ln * 10 ** 9 + k,
             "cfg": dict(BASE, **cfg)}
        if cfg_b is not None:
            s["cfg_b"] = dict(BASE, **cfg_b)
        P.append(s)

    # W1-A physics-invariance audit (plain, same seed, one switch flipped)
    for r in REPROS:
        for k in range(20):
            for arm in ("RESEMBLANCE", "PROVENANCE"):
                add("A1", "%s/WELL_MIXED" % r, k, "plain", {"reproduction": r, "spatial": "WELL_MIXED", "glineage_rule": arm}, arm, k)
    for pres in ("MINIMAL_CRITERION", "QD"):
        for k in range(20):
            for arm in ("RESEMBLANCE", "PROVENANCE"):
                add("A2", "%s/PARTIAL/WELL_MIXED" % pres, k, "plain",
                    {"reproduction": "ENDOGENOUS_PARTIAL", "spatial": "WELL_MIXED", "pressure": pres, "glineage_rule": arm}, arm, k)
    for r in REPROS:
        for k in range(20):
            for arm in ("HISTORICAL", "PAIRED"):
                add("A3", "%s/RANDOM" % r, k, "plain", {"reproduction": r, "init_draws": arm}, arm, k)
    for k in range(20):
        for arm in ("HISTORICAL", "PAIRED"):
            add("A4", "COPY/transplant", k, "plain", {"init_tapes": [rep], "init_draws": arm}, arm, k)
    # W1-B dual-ruler corrected baseline (historical physics; PROVENANCE + FUNC + TRB in shadow on the same trajectory)
    for r in REPROS:
        for k in range(300):
            add("B1", "%s/Z80_64/LOCAL" % r, k, "dual", {"reproduction": r})
    for rep_ in ("VM_COPY", "BYTECODE32"):
        for k in range(150):
            add("B1", "ENDOGENOUS_COPY/%s/LOCAL" % rep_, k, "dual", {"representation": rep_})
    for r in REPROS:
        for k in range(100):
            add("B2", "%s/Z80_64/WELL_MIXED" % r, k, "dual", {"reproduction": r, "spatial": "WELL_MIXED"})
    for k in range(30):
        add("B3", "pos_seeded_replicator", k, "dual", {"init": "SEEDED_REPLICATOR", "spatial": "WELL_MIXED"})
        add("B3", "cheat_bare_ldir", k, "dual", {"init_tapes": ["1500ff"]})
        add("B3", "cheat_smear", k, "dual", {"init_tapes": [bytes([0x07, 63, 0x08, 0, 0x03, 128, 0x15, 0xFF]).hex()]})
        add("B3", "cheat_capture_partial", k, "dual", {"reproduction": "ENDOGENOUS_PARTIAL", "init_tapes": [bytes([0x01, 0x77, 0x08, 70, 0x11, 0xFF]).hex()]})
    # W1-C DEF-BEL-009 pairing audit: transplant (replicator) vs no-transplant control on ONE seed, lockstep
    for arm in ("HISTORICAL", "PAIRED"):
        for k in range(150):
            add("C1", "COPY/LOCAL/transplant_vs_control", k, "lockstep", {"init_tapes": [rep], "init_draws": arm, "ticks": 300}, arm, k,
                cfg_b={"init_draws": arm, "ticks": 300})
    for i, p in enumerate(P):
        p["id"] = "w1_%05d" % i
    return P


if __name__ == "__main__":
    P = plan()
    b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b)
    print(len(P), hashlib.sha256(b).hexdigest())
