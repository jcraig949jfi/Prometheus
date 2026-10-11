"""BEL-48H Window 6 confirmation plan, block 1 (frozen by BEL_48H_PREREG.md s9 before any run).

    python3 plan_w6.py OUT.json

C1   ORIGIN PATHWAY CONFIRMATION on unseen, fully independent populations (one distinct seed per run, amendment 2):
     RANDOM init, GRID WELL_MIXED, 500 ticks, historical physics; ENDOGENOUS_PARTIAL / PAIR_EXECUTION / ENDOGENOUS_COPY,
     400 runs each; OriginWorld (eager change tags, first-FUNC event dissection, reversion).
C2   DISTRIBUTED PERSISTENCE CONFIRMATION (W2 s2.D, post-hoc there): the H2 'A' world (prefix-writer fragment, PAIRED
     init, ENDOGENOUS_PARTIAL, 300 ticks), 100 fresh distinct seeds, HeredityWorld."""
import hashlib, json, sys
from plan_w5 import BASE
from plan_w2 import fragments
SEED_BASE = 50_000_000_000_000


def plan():
    A, _ = fragments(); P = []; n = 0
    for r in ("ENDOGENOUS_PARTIAL", "PAIR_EXECUTION", "ENDOGENOUS_COPY"):
        for k in range(400):
            P.append({"lane": "C1", "cell": "%s/Z80_64/WELL_MIXED" % r, "arm": None, "pair": None, "k": k, "kind": "origin",
                      "seed": SEED_BASE + n, "cfg": dict(BASE, reproduction=r)}); n += 1
    for k in range(100):
        P.append({"lane": "C2", "cell": "A/PARTIAL", "arm": None, "pair": None, "k": k, "kind": "heredity",
                  "seed": SEED_BASE + 10 ** 6 + k, "cfg": dict(BASE, init_tapes=[A], init_draws="PAIRED", ticks=300)})
    for i, p in enumerate(P):
        p["id"] = "w6_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
