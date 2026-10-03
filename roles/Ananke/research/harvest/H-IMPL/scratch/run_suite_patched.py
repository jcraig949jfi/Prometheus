"""Run repo test files against the PATCHED package copy (scratch/patched first on sys.path)."""
import pathlib, sys
P = pathlib.Path(__file__).resolve().parent / "patched"
sys.path.insert(0, str(P))
import prometheus.ananke.engine as e, prometheus.ananke.lens_swap as ls
assert str(P) in e.__file__ and str(P) in ls.__file__, e.__file__
print("package under test:", pathlib.Path(e.__file__).parent)
import pytest
sys.exit(pytest.main(["-q", "-p", "no:cacheprovider", "--import-mode=importlib"] + sys.argv[1:]))
