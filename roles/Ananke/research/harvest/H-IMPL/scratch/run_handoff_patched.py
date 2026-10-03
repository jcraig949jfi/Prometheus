"""Run test_lens_swap's KA7 handoff tests with the ORIGINAL package but the PATCHED handoff()."""
import importlib.util, pathlib, sys
import pytest
P = pathlib.Path(__file__).resolve().parent / "patched/prometheus/ananke/lens_swap.py"
import prometheus.ananke.lens_swap as L
spec = importlib.util.spec_from_file_location("lens_swap_patched", P)
m = importlib.util.module_from_spec(spec); sys.modules["lens_swap_patched"] = m; spec.loader.exec_module(m)
L.handoff = m.handoff
print("handoff under test from", m.__file__)
sys.exit(pytest.main(["-q", "-p", "no:cacheprovider", "prometheus/ananke/tests/test_lens_swap.py", "-k", "handoff"]))
