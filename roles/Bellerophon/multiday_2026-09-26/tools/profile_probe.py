"""Profile one coupled run (OFF-PLAN pilot seed; engineering only). Writes cProfile stats text to --out."""
import cProfile, io, pathlib, pstats, sys, argparse
ROOT = pathlib.Path(__file__).resolve().parents[4]; sys.path.insert(0, str(ROOT))
from prometheus.z80atlas import coupling_campaign as CC, grammar as G
from prometheus.z80atlas.world import World
ap = argparse.ArgumentParser(); ap.add_argument("--ticks", type=int, default=1000); ap.add_argument("--out", required=True); a = ap.parse_args()
vec = dict(CC.COMMON, task="ECHO", init="SEEDED_REPLICATOR")
cfg = G.to_config(vec, a.ticks, CC.CELLS, CC.BUDGET, ())
for k, v in dict(CC.V3, **CC.K["K40"], coupling="ON").items(): setattr(cfg, k, v)
w = World(cfg, 7_600_000_000_000 + a.ticks)
pr = cProfile.Profile(); pr.enable()
import time; marks = []; t0 = time.time()
for i in range(a.ticks):
    w.step()
    if i % 100 == 99: marks.append((i + 1, round(time.time() - t0, 1), sum(1 for o in w.cells if o is not None), len(w.sr_depth), w.endogenous_births))
pr.disable()
s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats("cumulative").print_stats(35)
s2 = io.StringIO(); pstats.Stats(pr, stream=s2).sort_stats("tottime").print_stats(25)
pathlib.Path(a.out).write_text("marks (tick, wall_s, alive, ids, births):\n" + "\n".join(map(str, marks)) + "\n\n" + s.getvalue() + "\n\nTOTTIME\n" + s2.getvalue(), encoding="utf-8")
