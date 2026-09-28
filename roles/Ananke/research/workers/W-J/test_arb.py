"""Known-answer checks for ArbWorld (run before E2)."""
import sys, pathlib, numpy as np, torch
sys.path.insert(0, str(pathlib.Path(__file__).parent))
torch.set_num_threads(2)
from prometheus.ananke import plants
from prometheus.ananke.physics import Physics
from prometheus.ananke.engine import World
from arb import ArbWorld
ph = Physics(topology="ring", n_sites=16, radius=1, dest_mode="all", payload_width=1, channels=1,
             lat_base=2, state_dim=2, prog_len=4)
# program: EMIT := 256; PAY0 := SENSE... use constant payload by site via SENSE schedule
g = plants.assemble(ph, [("CONST", "EMIT", 0, 0, 1), ("MOV", "PAY0", "SENSE", 0, 0),
                         ("MOV", "S0", "IN0_0", 0, 0), ("MOV", "S1", "CNT0", 0, 0)])
from prometheus.ananke.engine import Schedule
T = 6
sidx = torch.tensor([[1, 3]]); sval = torch.zeros(T, 1, 2, dtype=torch.int32)
sval[:, 0, 0] = 100; sval[:, 0, 1] = 7         # site 1 says 100, site 3 says 7
sch = Schedule(sidx, sval, torch.tensor([[2]]))
out = {}
for name, cls in (("SUM", World), ("ARB", ArbWorld)):
    w = cls(ph, g[None, None].repeat(1, axis=0) if False else np.asarray(g)[None, None], [123], device="cpu", schedule=sch)
    for _ in range(T):
        w.step()
    out[name] = (int(w.S[0, 2, 0]), int(w.S[0, 2, 1]))
    print(name, "site2 S0,S1 =", out[name])
assert out["SUM"] == (107, 2), out
assert out["ARB"][0] in (100, 7) and out["ARB"][1] == 1, out
# determinism + graph equality on cuda if present
if torch.cuda.is_available():
    for cls in (ArbWorld,):
        a = cls(ph, np.asarray(g)[None, None], [5], device="cuda", schedule=sch); a.run(T, graph=False)
        b = cls(ph, np.asarray(g)[None, None], [5], device="cuda", schedule=sch); b.run(T, graph=True)
        assert a.digest() == b.digest(), "graph != eager"
        print("cuda graph==eager OK")
print("PASS")
# the lottery must change winner across ticks (state-free, tick-keyed)
w = ArbWorld(ph, np.asarray(g)[None, None], [123], device="cpu",
             schedule=Schedule(sidx, torch.cat([sval] * 10), torch.tensor([[2]])))
seen = []
for _ in range(60):
    w.step(); seen.append(int(w.S[0, 2, 0]))
print("winners seen:", sorted(set(seen[3:])), "share 100:", np.mean(np.array(seen[3:]) == 100))
assert set(seen[3:]) == {100, 7}
print("PASS2")
