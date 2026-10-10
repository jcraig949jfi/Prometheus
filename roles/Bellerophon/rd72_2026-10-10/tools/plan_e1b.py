"""BEL-RD-72 E1b (discovery; successor of E1, prereg s6-A): long-horizon accumulation inside a composite task.
    python3 plan_e1b.py OUT.json
Setting chosen by the FUNC-persistence pilots (pilot log): v3 K40 (base income 40), GRID LOCAL, lifespan 40, MED mutation,
founders = 32 copies of the bare copier (REP) transplanted (a quarter of the initial slots, PAIRED init), 3,000 ticks,
light census every 100 ticks. Cells: C1_ON (COND_ONE, payment ON, 80 worlds), C1_OFF (COND_ONE, OFF, 30), CM_ON
(COND_MULTI, ON, 40). Distinct seeds."""
import hashlib, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from prometheus.z80atlas import coupling_campaign as CC, vm
SEED = 72_300_000_000_000
CELLS = (("C1_ON", "COND_ONE", "ON", 80), ("C1_OFF", "COND_ONE", "OFF", 30), ("CM_ON", "COND_MULTI", "ON", 40))


def plan():
    REP = (vm.replicator(64) + bytes(56)).hex()
    P = []; n = 0
    for cell, task, arm, N in CELLS:
        for k in range(N):
            c = dict(CC.COMMON, **CC.V3, **CC.K["K40"])
            c.update(coupling=arm, task=task, init_tapes=[REP], init_draws="PAIRED", ticks=3000, cells=256, spatial="LOCAL", lifespan=40)
            P.append({"lane": "E1B", "cell": cell, "arm": arm, "pair": None, "k": k, "kind": "light_halves", "census_every": 100,
                      "seed": SEED + n, "cfg": c}); n += 1
    for i, p in enumerate(P):
        p["id"] = "e1b_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
