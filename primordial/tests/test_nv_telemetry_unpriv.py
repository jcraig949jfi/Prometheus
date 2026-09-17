"""Q3: unprivileged telemetry features are exact on bytes and move under the planted cheats."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")
pytestmark = pytest.mark.skipif(not torch.cuda.is_available(), reason="needs a CUDA device")

from primordial.nv.telemetry.unpriv import BLOCKED, brain_forward, measure  # noqa: E402

# uploads per honest region: W (16*9*4) + b (16*4) + obs; download: 4096 int64 actions
W_B = 16 * 9 * 4 + 16 * 4


def test_bytes_are_exact():
    fn, obs_bytes = brain_forward()
    fn()
    r = measure(fn)
    assert r["h2d_bytes"] == obs_bytes + W_B
    assert r["d2h_bytes"] == 4096 * 8
    assert r["peak_mem_bytes"] > 0
    assert set(BLOCKED) <= set(r) and all(v.startswith("BLOCKED") for v in BLOCKED.values())


def test_extra_copy_cheat_moves_h2d_by_exactly_one_upload():
    honest, obs_bytes = brain_forward()
    cheat, _ = brain_forward(extra_copy=True)
    honest()
    h, c = measure(honest), measure(cheat)
    assert c["h2d_bytes"] - h["h2d_bytes"] == obs_bytes
    assert c["d2h_bytes"] == h["d2h_bytes"]


def test_sleep_cheat_moves_share_not_bytes():
    honest, _ = brain_forward()
    cheat, _ = brain_forward(sleep_s=0.2)
    honest()
    h, c = measure(honest), measure(cheat)
    assert c["wall_s"] >= h["wall_s"] + 0.19
    assert c["kernel_share"] < h["kernel_share"]
    assert (c["h2d_bytes"], c["d2h_bytes"]) == (h["h2d_bytes"], h["d2h_bytes"])


def test_forward_result_unchanged_by_meter():
    fn, _ = brain_forward(seed=3)
    ref = fn()
    out = {}
    measure(lambda: out.setdefault("a", fn()))
    assert torch.equal(ref, out["a"])
