"""BEL-RD-72 F1 (prereg s10): COND_ONE desert stress test with a distance ladder.   python3 plan_f1.py OUT.json
Setting = E1b (v3 K40, GRID LOCAL, lifespan 40, 256 cells, PAIRED init, 32-copy founder transplant), task COND_ONE,
2,000 ticks, light census every 100. Founder cells (20 worlds each, payment ON and OFF):
  W0     the composite witness hybrid (copier + COND_ONE witness): positive control (does the setting KEEP a composite?)
  KO1 / KO2 / KO4   W0 with d of its 9 competence-critical, replication-neutral bytes (positions 4,5,7..13) set to NOP,
         positions drawn per world (rng 7210 + world index); every drawn founder must be FUNC and NOT BOTH (asserted)
  ECHOH  copier + ECHO witness (an evolved-like LO solver with no compare structure)
  REP    the bare copier (the E1b founder)
Distinct seeds (base 72.4e12). Founders are listed in the plan for the baseline geometry scan (tools/f1_geometry.py)."""
import hashlib, json, random, sys, pathlib
_H = pathlib.Path(__file__).resolve()
for _p in (_H.parent, _H.parents[1].parent / "bel48h_2026-10-08" / "tools", _H.parents[4]):
    sys.path.insert(0, str(_p))
from prometheus.z80atlas import vm, coupling_campaign as CC
from prometheus.z80atlas.world import Config
SEED = 72_400_000_000_000
L = 64
KO_POS = (4, 5, 7, 8, 9, 10, 11, 12, 13)
N = 20


def pad(b):
    return bytes(b[:L]) + bytes(max(0, L - len(b)))


def founders():
    W = pad(vm.hybrid_relocated(vm.replicator(L), vm.witness_cond_one()))
    return W, pad(vm.hybrid_relocated(vm.replicator(L), vm.witness_echo())), pad(vm.replicator(L))


def cfg(arm):
    c = dict(CC.COMMON, **CC.V3, **CC.K["K40"])
    c.update(coupling=arm, task="COND_ONE", init_draws="PAIRED", ticks=2000, cells=256, spatial="LOCAL", lifespan=40)
    return c


def plan():
    from light_halves import LightHalvesWorld
    W, E, R = founders()
    probe = LightHalvesWorld(Config(**dict(cfg("ON"), init_tapes=[R.hex()])), 0, census_every=10 ** 9)
    assert probe.halves(W) == "BOTH" and probe.func(W)
    P = []; n = 0
    for cell in ("W0", "KO1", "KO2", "KO4", "ECHOH", "REP"):
        for arm in ("ON", "OFF"):
            for k in range(N):
                if cell.startswith("KO"):
                    d = int(cell[2:]); rng = random.Random(7210 + n)
                    while True:
                        ps = sorted(rng.sample(KO_POS, d))
                        f = bytes(vm.NOP if i in ps else b for i, b in enumerate(W))
                        if probe.func(f) and probe.halves(f) != "BOTH":
                            break
                    meta = {"ko": ps, "founder_halves": probe.halves(f)}
                else:
                    f = {"W0": W, "ECHOH": E, "REP": R}[cell]; meta = {"founder_halves": probe.halves(f)}
                P.append({"lane": "F1", "cell": cell, "arm": arm, "pair": None, "k": k, "kind": "light_halves", "census_every": 100,
                          "seed": SEED + n, "founder": f.hex(), **meta, "cfg": dict(cfg(arm), init_tapes=[f.hex()])}); n += 1
    for i, p in enumerate(P):
        p["id"] = "f1_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b)
    from collections import Counter
    print(len(P), hashlib.sha256(b).hexdigest(), Counter((p["cell"], p.get("founder_halves")) for p in P))
