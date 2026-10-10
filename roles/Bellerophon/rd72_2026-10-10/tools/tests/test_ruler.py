import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import ruler
from prometheus.z80atlas import vm


def test_ruler_profiles():
    R = vm.replicator(64)
    a = ruler.ruler(vm.hybrid_relocated(R, vm.witness_cond_one()), "COND_ONE")
    assert a["competent"] and a["func"] and a["halves"] == "BOTH" and a["n_ccrit"] >= 7 and all(g["competent"] for g in a["generations"])
    b = ruler.ruler(R, "ECHO")
    assert not b["competent"] and b["func"] and b["n_ccrit"] == 0 and b["n_rcrit"] >= 4
