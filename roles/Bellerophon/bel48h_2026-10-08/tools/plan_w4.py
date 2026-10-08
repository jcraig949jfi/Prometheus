"""BEL-48H Window 4 plan: computation x reproduction under physics v3 (frozen by BEL_48H_PREREG.md s5 before any W4 run).

    python3 plan_w4.py OUT.json

M1  conflict repair, powered re-test of coupling P6 (historical 4/60 ON vs 0/60 OFF, p 0.125): fixtures REP + BAD
    (BAD = LD T,L; LDIR with C = 0 -- a 256-byte sweep that wrecks the inputs -- followed by the INC witness), INC,
    K16, coupling ON vs OFF, 300 seed-pairs, the historical COMMON/V3 configuration (coupling_campaign.py).
M2  de novo acquisition from pure copiers (historical B-cop ECHO K40: 29/150 ON vs 6/150 OFF): SEEDED_REPLICATOR,
    task ECHO, K40, coupling ON / OFF / SHUFFLED, 150 seeds each."""
import hashlib
import json
import pathlib
import sys

SEED_BASE = 48_900_000_000_000


def plan():
    sys.path.insert(0, pathlib.Path(__file__).resolve().parents[4].as_posix())
    from prometheus.z80atlas import coupling_campaign as CC
    P = []; lanes = {}

    def add(lane, cell, arm, k, vec, over, tapes=(), kn="K16"):
        ln = lanes.setdefault(lane, len(lanes))
        cfg = dict(CC.COMMON, **vec); cfg.update(CC.V3); cfg.update(CC.K[kn]); cfg.update(over)
        cfg.update(ticks=CC.TICKS, cells=CC.CELLS, budget=CC.BUDGET)
        if tapes:
            cfg["init_tapes"] = list(tapes)
        P.append({"lane": lane, "cell": cell, "arm": arm, "pair": k, "k": k, "kind": "comp",
                  "seed": SEED_BASE + ln * 10 ** 9 + k, "cfg": cfg})

    for k in range(300):
        F = CC.fixtures("INC", SEED_BASE + k)
        for arm in ("ON", "OFF"):
            add("M1", "E2_REP_BAD_K16", arm, k, {}, {"coupling": arm}, tapes=[F["REP"], F["BAD"]])
    for k in range(150):
        for arm in ("ON", "OFF", "SHUFFLED"):
            add("M2", "Bcop_ECHO_K40", arm, k, {"task": "ECHO", "init": "SEEDED_REPLICATOR"}, {"coupling": arm}, kn="K40")
    for i, p in enumerate(P):
        p["id"] = "w4_%05d" % i
    return P


if __name__ == "__main__":
    P = plan()
    b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b)
    print(len(P), hashlib.sha256(b).hexdigest())
