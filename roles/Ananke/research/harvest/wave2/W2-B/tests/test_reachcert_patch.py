"""Regression tests for patch/reach_certificate_window_decision.diff (W2-B).
FAIL on the current H-INST pte_trace.reach_certificate, PASS on patch/patched/pte_trace.py.
Run against either module with W2B_PTE=orig|patched (default patched):
  CUDA_VISIBLE_DEVICES=-1 W2B_PTE=orig python -m pytest tests/test_reachcert_patch.py -q -p no:cacheprovider
"""
import importlib.util
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import w2b_common as c  # noqa: E402  (CPU guard, 2 threads, repo on sys.path)
from w2b_common import np, envs, assays, plants, torch  # noqa: E402
from prometheus.ananke import c1b  # noqa: E402

which = os.environ.get("W2B_PTE", "patched")
src = (c.ROOT / "roles/Ananke/research/harvest/H-INST/pte_trace.py") if which == "orig" else (HERE / "patch/patched/pte_trace.py")
spec = importlib.util.spec_from_file_location("pte_trace_under_test", src)
P = importlib.util.module_from_spec(spec)
sys.modules["pte_trace_under_test"] = P
spec.loader.exec_module(P)

SEEDS = assays.world_seeds(0x7E57, 16)
M = len(SEEDS)
HOLD = envs.EnvSpec(family="HOLD", gap=8, cue_len=2, trials=12)
TK = c1b.ticks(HOLD)
K = 5


def latch():
    ph = plants.c1b_echo_physics().replace(prog_len=12, payload_width=1)
    return ph, plants.plant("hold_latch", ph)


def test_hook_in_earlier_trial_does_not_make_trial_absorbed():
    """A trial-0 hook zeroes the readout site's S0; trial 1's cue re-latches it, so nothing reaches trial K.
    Current code: ABSORBED (touch at lag -68 counted). Patched: NOT_REACHED."""
    ph, g = latch()
    ep = envs.build(ph, HOLD, SEEDS)
    a = torch.as_tensor(ep.schedule.read_idx[:, 0])

    def zero(w):
        w.S[torch.arange(M), a, 0] = 0
    r = P.reach_certificate(ph, g, HOLD, SEEDS, {TK["mid"][0]: zero}, K)
    assert r["applied"] == 1.0
    assert r["verdict"] == "NOT_REACHED", r["verdict"]
    # MUST-STAY: the same hook inside trial K's window is still a touch (and an output change)
    r2 = P.reach_certificate(ph, g, HOLD, SEEDS, {TK["mid"][K]: zero}, K)
    assert r2["verdict"] == "REACHED_OUTPUT"


def test_value_only_change_is_not_a_decision_change():
    """A +1 nudge to S0 at ONE world's readout site: value changed in 1/16 worlds, no decision changed.
    Current code has no decision-level key; patched reports decision == 0 and the per-world class."""
    ph, g = latch()
    ep = envs.build(ph, HOLD, SEEDS)
    a = int(ep.schedule.read_idx[0, 0])

    def nudge(w):
        w.S[0, a, 0] += 1
    r = P.reach_certificate(ph, g, HOLD, SEEDS, {TK["ro"][K] - 1: nudge}, K)
    assert r["verdict"] == "REACHED_OUTPUT" and abs(r["output"] - 1 / M) < 1e-9
    assert r.get("decision") == 0.0
    assert r["per_world"][0] == "REACHED_VALUE_ONLY" and r["per_world"][1] == "UNAPPLIED"
