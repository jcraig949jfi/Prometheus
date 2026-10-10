"""BEL-RD-72 K: composition of two computational blocks across a reachability desert (frozen by prereg s3).
    python3 plan_k.py OUT.json
physics v3 (coupling campaign COMMON + V3 + K40), task COND_MULTI, 1,000 ticks, PAIRED init, transplants = a quarter of the
initial slots (alternating when two fixtures). Fixture sets x operator regimes, 30 distinct seeds per cell:
  fixtures  XY_AL (X_al + Y_al), XY_SH (X_sh + Y_sh), XY_NS (X_sh + Y_ns), X_ONLY (X_al), Y_ONLY (Y_al), REP (pure copier)
  operators COPY_BYTE (ENDOGENOUS_COPY, BYTE mutation -- the historical LADDER regime), COPY_STRUCT (ENDOGENOUS_COPY,
            STRUCTURAL mutation: insert / delete / duplicate), PARTIAL_BYTE (ENDOGENOUS_PARTIAL, BYTE mutation)
plus payment control: XY_AL under coupling OFF in each operator regime (30 seeds)."""
import hashlib, json, sys, pathlib
sys.path.insert(0, pathlib.Path(__file__).resolve().parents[4].as_posix()); sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix())
from fixtures_k import fixtures
SEED = 71_000_000_000_000
FIX = {"XY_AL": ("X_al", "Y_al"), "XY_SH": ("X_sh", "Y_sh"), "XY_NS": ("X_sh", "Y_ns"), "X_ONLY": ("X_al",), "Y_ONLY": ("Y_al",), "REP": ("REP",)}
OPS = {"COPY_BYTE": {"reproduction": "ENDOGENOUS_COPY", "mutation": "BYTE"}, "COPY_STRUCT": {"reproduction": "ENDOGENOUS_COPY", "mutation": "STRUCTURAL"},
       "PARTIAL_BYTE": {"reproduction": "ENDOGENOUS_PARTIAL", "mutation": "BYTE"}}


def cfg(ops, tapes, coupling="ON", ticks=1000):
    from prometheus.z80atlas import coupling_campaign as CC
    c = dict(CC.COMMON, **CC.V3, **CC.K["K40"]); c.update(OPS[ops]); c.update(coupling=coupling, task="COND_MULTI", init_tapes=tapes,
                                                                             init_draws="PAIRED", ticks=ticks, cells=CC.CELLS, budget=CC.BUDGET)
    return c


def plan():
    F = {k: v.hex() for k, v in fixtures().items()}
    P = []; n = 0
    for ops in OPS:
        for fx, names in FIX.items():
            for k in range(30):
                P.append({"lane": "K", "cell": "%s/%s" % (fx, ops), "arm": "ON", "k": k, "pair": None, "kind": "comp", "seed": SEED + n,
                          "cfg": cfg(ops, [F[x] for x in names])}); n += 1
        for k in range(30):
            P.append({"lane": "K", "cell": "XY_AL/%s" % ops, "arm": "OFF", "k": k, "pair": None, "kind": "comp", "seed": SEED + n,
                      "cfg": cfg(ops, [F["X_al"], F["Y_al"]], coupling="OFF")}); n += 1
    for i, p in enumerate(P):
        p["id"] = "k_%05d" % i
    return P


if __name__ == "__main__":
    P = plan(); b = json.dumps(P, sort_keys=True, separators=(",", ":")).encode()
    open(sys.argv[1], "wb").write(b); print(len(P), hashlib.sha256(b).hexdigest())
