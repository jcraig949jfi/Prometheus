"""Run one coupled world (off-plan seed) from whatever `prometheus` is first on sys.path; dump summary + timing.
Used to prove a measurement-only optimisation leaves every output byte-identical (compare two dumps)."""
import json, sys, time, pathlib
root, out, ticks, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
sys.path.insert(0, root)
from prometheus.z80atlas import coupling_campaign as CC, grammar as G
from prometheus.z80atlas.world import World
cfg = G.to_config(dict(CC.COMMON, task="ECHO", init="SEEDED_REPLICATOR"), ticks, CC.CELLS, CC.BUDGET, ())
for k, v in dict(CC.V3, **CC.K["K40"], coupling="ON").items(): setattr(cfg, k, v)
t0 = time.time(); w = World(cfg, seed); s = w.run(); dt = time.time() - t0
s.pop("wall_s", None)
pathlib.Path(out).write_text(json.dumps({"summary": s, "ticks_log": w.ticks_log, "snapshots": w.snapshots}, sort_keys=True, default=str), encoding="utf-8")
print(json.dumps({"root": root, "wall_s": round(dt, 1)}))
