"""BEL-RD-72 E1 (discovery): long-horizon accumulation inside a composite task, light census instrument.
    python3 plan_e1.py OUT.json
Seeded self-copiers (SEEDED_REPLICATOR: a minority of copiers in a random majority), v3 physics K40, persistence setting
from the pilot log (WELL_MIXED, lifespan 80, base income 40), 2,000 ticks, census every 100 ticks (light_halves).
Cells: C1_ON (COND_ONE, payment ON, 40 seeds), C1_OFF (COND_ONE, payment OFF, 20), CM_ON (COND_MULTI, payment ON, 20).
Distinct seeds everywhere (no pairing)."""
import hashlib, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from prometheus.z80atlas import coupling_campaign as CC
SEED = 72_100_000_000_000
CELLS = (("C1_ON", "COND_ONE", "ON", 40), ("C1_OFF", "COND_ONE", "OFF", 20), ("CM_ON", "COND_MULTI", "ON", 20))


def plan():
    P = []; n = 0
    for cell, task, arm, N in CELLS:
        for k in range(N):
            c = dict(CC.COMMON, **CC.V3, **CC.K["K40"])
            c.update(coupling=arm, task=task, init="SEEDED_REPLICATOR", ticks=2000, cells=256, spatial="WELL_MIXED", lifespan=80)
            P.append({"lane": "E1", "cell": cell, "arm": arm, "pair": None, "k": k, "kind": "light_halves", "census_every": 100,
                      "seed": SEED + n, "cfg": c}); n += 1
    for i, p in enumerate(P):
        p["id"] = "e1_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
