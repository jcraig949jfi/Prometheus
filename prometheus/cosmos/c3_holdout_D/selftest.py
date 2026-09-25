"""Controls-only selftest for holdout D (contract s6). Booleans only; NEVER touches the hidden worlds.

  COSMOS_BROKER=1 python -m prometheus.cosmos.c3_holdout_D.selftest [out.json]

Checks (each run on the family AND on a deliberately defective system, which must FAIL the check):
  replay_identical            same (world, seed) twice -> bit-identical states and readout features
  interchange_round_trip      exchanging paired rows twice at t = k is the identity, the state is row-aligned
                              (every array has axis 0 = episode), and continuing from it reproduces the
                              intact rollout bit-for-bit
  interchange_transplant      exchanging the full state at t = k makes row 2i continue EXACTLY as row 2i+1
                              did intact (the dict holds the whole causal state; nothing hides elsewhere)
  history_free_certifies_NONE the lattice's history-free control world (p_decay = 1) certifies NONE with the
                              reference certificate prometheus/cosmos/c3/certify.py
Demo worlds used for replay / interchange are fixed lattice points chosen by the author, not hidden worlds;
no certify outcome of any family world other than the history-free control is computed or reported.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from prometheus.cosmos.c3.certify import certify
from prometheus.cosmos.c3.system import System, rollout, swap_rows
from prometheus.cosmos.c3.task import Task, batch, onehot, paired_batch
from prometheus.cosmos.c3_holdout_D import medium

HERE = Path(__file__).resolve().parent
DEMO = medium.World(V=3, k=4, L=16, D=0.2, v=0.5, p_decay=0.03, kappa=0.1, q=1.0, sigma=0.2,
                    x_in=0, d_patch=4, w_patch=2)
CERT_SEED = 20260925


# ---------------------------------------------------------------- injected defects (negative controls)
class DefectUnseededNoise(medium.ReactiveChannel):
    """Draws its noise from a fresh OS-entropy generator instead of the harness rng."""
    def noise(self, n, rng):
        return {"xi": np.random.default_rng().standard_normal((n, self.w.L, self.S))}


class DefectPairPooled(medium.ReactiveChannel):
    """Keeps an extra array pooled over PAIRS of episodes (axis 0 = E/2): not row-aligned."""
    def init(self, E):
        st = super().init(E)
        st["pool"] = np.zeros((E // 2, self.w.L))
        return st

    def step(self, state, obs_t, noise):
        new = super().step({"c": state["c"]}, obs_t, noise)
        E = new["c"].shape[0]
        new["pool"] = new["c"].sum(2)[: E // 2 * 2].reshape(E // 2, 2, -1).mean(1)
        return new


class DefectHiddenState(medium.ReactiveChannel):
    """Keeps part of the causal state (a per-episode cue tag) on the object, outside the state dict."""
    def init(self, E):
        self._tag = np.zeros(E)
        self._t = 0
        return super().init(E)

    def step(self, state, obs_t, noise):
        if self._t == 0:
            self._tag = np.asarray(obs_t, float).copy()
        self._t += 1
        new = super().step(state, obs_t, noise)
        new["c"][:, 0, 0] += 1e-3 * self._tag
        return new


class DefectShadowRegister(medium.ReactiveChannel):
    """A 'history-free' control that secretly copies the cue into a shadow register it reads."""
    def init(self, E):
        st = super().init(E)
        st["shadow"] = np.full(E, -1, dtype=np.int64)
        st["t"] = np.zeros(E, dtype=np.int64)
        return st

    def step(self, state, obs_t, noise):
        new = super().step({"c": state["c"]}, obs_t, noise)
        sh = state["shadow"].copy()
        first = state["t"] == 0
        sh[first] = obs_t[first]
        new["shadow"], new["t"] = sh, state["t"] + 1
        return new

    def _sh(self, st):
        return onehot(np.where(st["shadow"] < 0, self.w.V, st["shadow"]), self.w.V + 1)

    def readout_features(self, st):
        return np.hstack([super().readout_features(st), self._sh(st)])

    def full_state(self, st):
        return np.hstack([super().full_state(st), self._sh(st)])


# ---------------------------------------------------------------- checks
def _run(sys_: System, task: Task, seed: int):
    rng = np.random.default_rng(seed)
    _c, obs = batch(task, 64, rng)
    r = rollout(sys_, obs, rng, record=tuple(range(task.T)))
    return r


def replay_identical(sys_: System, task: Task, seed: int = 11) -> bool:
    a, b = _run(sys_, task, seed), _run(sys_, task, seed)
    same = all(np.array_equal(a["states"][t], b["states"][t]) for t in a["states"])
    return bool(same and np.array_equal(a["features"], b["features"]))


def _paired_rollout_split(sys_: System, task: Task, seed: int, t_swap: int, n_swaps: int):
    """Paired rollout with n_swaps exchanges applied right after step t_swap (0 = intact)."""
    rng = np.random.default_rng(seed)
    _c, obs = paired_batch(task, 32, rng)
    nrng = np.random.default_rng(seed + 1)
    E = obs.shape[0]
    perm = np.arange(E).reshape(-1, 2)[:, ::-1].reshape(-1)
    st = sys_.init(E)
    for t in range(task.T):
        nz = {k: np.repeat(v, 2, axis=0) for k, v in sys_.noise(E // 2, nrng).items()}
        st = sys_.step(st, obs[:, t], nz)
        if t == t_swap:
            for _ in range(n_swaps):
                st = swap_rows(st, perm)
    return st, sys_.full_state(st), sys_.readout_features(st), perm


def interchange_round_trip(sys_: System, task: Task, seed: int = 12) -> bool:
    try:
        st0 = sys_.init(8)
        if not all(np.asarray(v).shape[0] == 8 for v in st0.values()):
            return False
        _s, f0, r0, _p = _paired_rollout_split(sys_, task, seed, task.k, 0)
        _s, f2, r2, _p = _paired_rollout_split(sys_, task, seed, task.k, 2)
        return bool(np.array_equal(f0, f2) and np.array_equal(r0, r2))
    except (IndexError, ValueError):
        return False


def interchange_transplant(sys_: System, task: Task, seed: int = 13) -> bool:
    """After one exchange at t = k, row i must end exactly where its partner ended intact (the pair
    shares distractors, query and noise after t = k)."""
    try:
        _s, f0, _r0, perm = _paired_rollout_split(sys_, task, seed, task.k, 0)
        _s, f1, _r1, _p = _paired_rollout_split(sys_, task, seed, task.k, 1)
        return bool(np.array_equal(f1, f0[perm]))
    except (IndexError, ValueError):
        return False


def history_free_none(sys_: System, task: Task, seed: int = CERT_SEED) -> dict:
    r = certify(sys_, task, seed=seed)
    return {"pass": r["class"] == "NONE", "class": r["class"], "P1_p": r["P1"]["p"],
            "P2_effect": r["P2"]["effect"], "P2_se": r["P2"]["se"]}


def src_sha(name: str) -> str:
    return hashlib.sha256((HERE / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def run(with_certify: bool = True) -> dict:
    demo, dt = medium.ReactiveChannel(DEMO), DEMO.task()
    ctrl_w = medium.CONTROL_HISTORY_FREE
    ctrl, ct = medium.ReactiveChannel(ctrl_w), ctrl_w.task()
    res = {
        "family": medium.FAMILY_NAME, "family_version": medium.FAMILY_VERSION,
        "machine": "M1 SKULLPORT", "python": sys.version.split()[0], "numpy": np.__version__,
        "demo_world": DEMO.as_dict(), "control_world": ctrl_w.as_dict(),
        "control_world_in_lattice": medium.in_lattice(ctrl_w),
        "medium_src_sha256": src_sha("medium.py"),
        "checks": {
            "replay_identical": replay_identical(demo, dt),
            "replay_identical_control_world": replay_identical(ctrl, ct),
            "interchange_round_trip": interchange_round_trip(demo, dt),
            "interchange_transplant": interchange_transplant(demo, dt),
        },
        "negative_controls_must_be_false": {
            "replay_identical[DefectUnseededNoise]": replay_identical(DefectUnseededNoise(DEMO), dt),
            "interchange_round_trip[DefectPairPooled]": interchange_round_trip(DefectPairPooled(DEMO), dt),
            "interchange_transplant[DefectHiddenState]": interchange_transplant(DefectHiddenState(DEMO), dt),
        },
    }
    if with_certify:
        hf = history_free_none(ctrl, ct)
        res["checks"]["history_free_certifies_NONE"] = hf.pop("pass")
        res["history_free_control_detail"] = hf
        bad = history_free_none(DefectShadowRegister(ctrl_w), ct)
        res["negative_controls_must_be_false"]["history_free_certifies_NONE[DefectShadowRegister]"] = bad.pop("pass")
        res["defect_shadow_detail"] = bad
    res["all_checks_true"] = all(res["checks"].values())
    res["all_negative_controls_false"] = not any(res["negative_controls_must_be_false"].values())
    res["selftest_pass"] = bool(res["all_checks_true"] and res["all_negative_controls_false"]
                                and res["control_world_in_lattice"])
    return res


if __name__ == "__main__":
    out = run()
    txt = json.dumps(out, indent=1, sort_keys=True)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(txt + "\n", encoding="utf-8", newline="\n")
    print(txt)
