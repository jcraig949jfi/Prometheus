"""Cosmos-side acceptance checks on the FOREIGN family theseus_sediment (Theseus, 79dc4c4b8).

These tests read the foreign module; they never modify it. Any Cosmos adaptation of the family must
live in a separate module so the original stays byte-identical to the receipt pinned here.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from prometheus.cosmos.c3 import task as tk
from prometheus.cosmos.c3.system import rollout
from prometheus.cosmos.c4.families.theseus_sediment import world as W

FAM = Path(W.__file__).parent
# Immutable pre-exposure receipt (PUBLICATION_PLAN T1): LF-normalised world.py sha256 at 79dc4c4b8.
WORLD_SHA256_LF = "41772ab5c98cf91e2122c2d0bc3e5f0306e696fc062b2a7c3f4f53bbc291e414"


def test_original_source_unchanged():
    src = (FAM / "world.py").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(src).hexdigest() == WORLD_SHA256_LF


def test_selftest_all_pass_here():
    out = W.selftest()
    assert all(out.values()), out
    assert json.loads((FAM / "SELFTEST.json").read_text())["all_pass"] is True


def test_natural_samples_in_declared_ranges():
    native = json.loads((FAM / "NATIVE.json").read_text())["parameters"]
    rng = np.random.default_rng(0)
    for _ in range(300):
        kn = W.sample_natural(rng)
        for f, v in kn.items():
            lo, hi = native[f]["range"]
            assert lo <= v <= hi, (f, v)
        W.build_world(**kn)


def test_full_state_is_whole_causal_state():
    """Two states with equal full_state must evolve identically (contract s2)."""
    rng = np.random.default_rng(1)
    sys_ = W.build_world(**W.sample_natural(rng))
    _, obs = tk.batch(tk.Task(V=4, k=4), 16, rng)
    st = rollout(sys_, obs, np.random.default_rng(2))["final"]
    fs = sys_.full_state(st)
    assert fs.shape[1] == sum(v.reshape(v.shape[0], -1).shape[1] for v in st.values())
    x = np.arange(16)
    nz = sys_.noise(16, np.random.default_rng(3))
    a = sys_.step({k: v.copy() for k, v in st.items()}, x, nz)
    b = sys_.step({k: v.copy() for k, v in st.items()}, x, nz)
    assert np.array_equal(sys_.full_state(a), sys_.full_state(b))


@pytest.mark.parametrize("V,k,seed", [(2, 2, 5), (4, 8, 6), (8, 4, 7)])
def test_history_free_control_beyond_selftest(V, k, seed):
    """Stricter than the author's selftest: other V, other seeds, a non-default natural world."""
    kn = dict(W.sample_natural(np.random.default_rng(seed)), **W.HISTORY_FREE)
    hf = W.build_world(**kn)
    _, pobs = tk.paired_batch(tk.Task(V=V, k=k), 32, np.random.default_rng(seed))
    f = rollout(hf, pobs, np.random.default_rng(seed), paired=True)["features"]
    assert np.array_equal(f[0::2], f[1::2])
