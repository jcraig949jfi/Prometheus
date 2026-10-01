"""Can each invariant test FAIL? Run its body under a deliberately wrong premise; each must raise."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tests"))
import test_w2a1_engine_invariants as T
from prometheus.ananke.engine import Controls, World
from prometheus.ananke.physics import Physics
import numpy as np, torch
def must_fail(name, fn):
    try:
        fn(); print("DID NOT FAIL (vacuous!):", name)
    except AssertionError:
        print("fails as it should:", name)
# 1 conservation with dup on: payload accounting must break
orig = T.rand_physics
T.rand_physics = lambda seed, **o: orig(seed, **{**o, "dup": 0.3})
must_fail("conservation under dup", lambda: [T.test_message_conservation_lossless(s) for s in range(8)])
T.rand_physics = orig
# 2 locality without zero_comm
oc = T.Controls
T.Controls = lambda **k: oc()
must_fail("locality without zero_comm", lambda: [T.test_zero_comm_locality(s) for s in range(10)])
T.Controls = oc
# 3 light cone with a too-fast speed limit (dmin+1)
og = T.topology.graph_distances
T.topology.graph_distances = lambda ph, s: og(ph, s) * 2
must_fail("light cone with doubled hop count", lambda: [T.test_light_cone(s) for s in range(10)])
T.topology.graph_distances = og
# 4 inert test with a NON-inert change
must_fail("inert: fanout under sample", lambda: T.test_inert_dials_leave_dynamics_identical(dict(topology="ring", n_sites=12, dest_mode="sample", fanout=2), dict(fanout=8)))
