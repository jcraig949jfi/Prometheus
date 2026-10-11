"""BEL-RD-72 F6 (prereg s15): transplantation of the error-threshold result (RM2) to a second composite and a second world
model, on FRESH seeds (base 72.6e12).   python3 plan_f6.py OUT.json
Setting = F1 (v3 K40, lifespan 40, 256 cells, PAIRED init, 32-copy founder transplant, payment ON, 2,000 ticks, census 100).
  CM   founder = copier + COND_MULTI witness (14 competence-critical bytes), task COND_MULTI, GRID LOCAL,
       mutation MED / LOW / VLOW on the same 20 seeds
  WM   founder = copier + COND_ONE witness (F1 W0), task COND_ONE, GRID WELL_MIXED, mutation MED / VLOW on the same 20 seeds"""
import hashlib, json, sys, pathlib
_H = pathlib.Path(__file__).resolve()
for _p in (_H.parent, _H.parents[1].parent / "bel48h_2026-10-08" / "tools", _H.parents[4]):
    sys.path.insert(0, str(_p))
from prometheus.z80atlas import vm, coupling_campaign as CC
SEED = 72_600_000_000_000
L = 64


def pad(b):
    return bytes(b[:L]) + bytes(max(0, L - len(b)))


def plan():
    CMW = pad(vm.hybrid_relocated(vm.replicator(L), vm.witness_cond_multi())).hex()
    W0 = pad(vm.hybrid_relocated(vm.replicator(L), vm.witness_cond_one())).hex()
    P = []
    for cell, task, spatial, founder, rates, base in (("CM", "COND_MULTI", "LOCAL", CMW, ("MED", "LOW", "VLOW"), 0),
                                                      ("WM", "COND_ONE", "WELL_MIXED", W0, ("MED", "VLOW"), 1000)):
        for k in range(20):
            for rate in rates:
                c = dict(CC.COMMON, **CC.V3, **CC.K["K40"])
                c.update(coupling="ON", task=task, init_draws="PAIRED", ticks=2000, cells=256, spatial=spatial, lifespan=40,
                         mutation_rate=rate, init_tapes=[founder])
                P.append({"lane": "F6", "cell": cell + "_" + rate, "arm": "ON", "pair": k, "k": k, "kind": "light_halves",
                          "census_every": 100, "seed": SEED + base + k, "founder": founder, "cfg": c})
    for i, p in enumerate(P):
        p["id"] = "f6_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
