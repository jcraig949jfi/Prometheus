"""Check: explib and its core tests run with prometheus and torch made unimportable. Exit code = pytest's."""
import importlib.abc
import pathlib
import sys


class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        if name.split(".")[0] in ("prometheus", "torch"):
            raise ImportError(f"BLOCKED import of {name} (core must be engine-free)")
        return None


sys.meta_path.insert(0, Block())
import pytest  # noqa: E402

here = pathlib.Path(__file__).resolve().parents[1]
core = [str(p) for p in sorted((here / "tests").glob("test_*.py")) if p.name != "test_pte_adapter.py"]
sys.exit(pytest.main(["-q", "-p", "no:cacheprovider", *core]))
