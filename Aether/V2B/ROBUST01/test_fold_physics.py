"""ROBUST01 fixtures for aeth01.op_xor_fold.

    python -m pytest Aether/V2B/ROBUST01/test_fold_physics.py -q

The reference here is a per-site Python loop restated from the law text, not the vectorized gather it checks.
"""

import hashlib
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fold_physics as FP  # noqa: E402

X = FP.X
EN = X.EXEC_ONLY
REACH01 = FP.REACH01

# The frozen REACH01 code ROBUST01 reuses, at the hashes its own preregistrations recorded (LADDER01 f372e412c,
# R4 082f2f27b, R4c), plus the kernel and the express01 wrapper as they stand at origin/main aef5dbd5b.
FROZEN = {
    "R3/r3_frontier.py": "b5d0ba8c340d93788b7f3bacbea9b3e37f28f8cae353cd4be6f934eb10a84d96",
    "R3/r3_certify.py": "851208e771ba2fc9e90dae7ded5bc2aeb77abf3a40a56525a5984e06f3ed86f7",
    "R3/r3_certify_run.py": "520257905ce0ee739ab2f03513f22c8f9452c9ad3881d305f31a7cb8092a26a9",
    "R3/r3_planted.py": "d0203f041378bfe302f13bddc3917bca7c4f91fa318e740a5b4f6305dd61b7b9",
    "R4/r4_accum.py": "a2cf73918215363b2e1a11199e94b528dcea7f5a8f09495063fa177b19192737",
    "R4/r4_reduce.py": "baf715919cf088ea1d18a31426059b2e8bfbf408671b7f58a290a56d868c4795",
    "R4/component_planted.json": "ca50a82890675001f7577d69a516d8fa153139bcb13f6a80a04099e06d2a7627",
    "R4/RULES.json": "f611cc7ef4bbc99214aa57cf0cc841b7227fef40d8fc1e6dd8110399fdde7fd2",
    "R2/express01.py": "b6c5a38a9bcdbaef87bb1d357cd3683713cc9b58050e78f4491447ca7f65dbb7",
    "reach_flight.py": "2b594c81418d1fa1f845dd09216dc12c805c209b834b711edbd46c82919e8b54",
    "../../test/reference/gpu_aeth01.py": "56c749afd409dba9e266e2b864eaac25ffc5953c57d8d7c64f6ad893e8a819e7",
    "../../runpod/aeth01_canary/aeth01_gpu_kernel.py": "1e89830d62e50266705ab95250890a80ab45479f336fd5b894e5b6af7f773f65",
}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def world(rng, n, energy_writes=True):
    s = [rng.integers(0, 256, (n, n)).astype(np.uint8) for _ in range(5)]
    s[0] = np.where(rng.random((n, n)) < 0.6, 1, s[0]).astype(np.uint8)
    s[4] = rng.integers(0, 32, (n, n)).astype(np.uint8)
    if not energy_writes:
        s[2] = np.where(s[2] % 5 == 4, s[2] - 1, s[2]).astype(np.uint8)
    return s


def loop_reference(s, write_cost=1):
    """Per site, per template field: (contender count, XOR of contender payloads). Torus, 4 neighbours."""
    n = s[0].shape[0]
    cnt = np.zeros((4, n, n), np.int64)
    fold = np.zeros((4, n, n), np.int64)
    e_cnt = np.zeros((n, n), np.int64)
    for y in range(n):
        for x in range(n):
            for dy, dx, need in ((-1, 0, X.S), (1, 0, X.N), (0, 1, X.W), (0, -1, X.E)):
                sy, sx = (y + dy) % n, (x + dx) % n
                if s[0][sy, sx] != 1 or int(s[4][sy, sx]) < write_cost or s[1][sy, sx] % 4 != need:
                    continue
                f = int(s[2][sy, sx]) % 5
                if f == 4:
                    e_cnt[y, x] += 1
                else:
                    cnt[f, y, x] += 1
                    fold[f, y, x] ^= int(s[3][sy, sx])
    return cnt, fold, e_cnt


def cpu():
    return X.load("cpu")


def test_frozen_reach01_code_is_the_preregistered_code():
    for rel, want in FROZEN.items():
        assert sha(os.path.normpath(os.path.join(REACH01, rel))) == want, rel


@pytest.mark.parametrize("seed", range(6))
def test_fold_equals_law_text_and_contest_where_uncontested(seed):
    xp, K = cpu()
    rng = np.random.default_rng(100 + seed)
    s = world(rng, 11)
    tick = 1 + seed
    fold, _ = FP.step_fold(xp, K, 11, 0xF00D, tick, s, EN)
    con, _ = FP.contest_step(xp, K, "XOR", 11, 0xF00D, tick, s, EN)
    cnt, ref_fold, _ = loop_reference(s)
    multi = 0
    for f in range(4):
        want = np.where(cnt[f] > 0, s[f].astype(np.int64) ^ ref_fold[f], s[f].astype(np.int64))
        assert np.array_equal(fold[f].astype(np.int64), want), f
        single = cnt[f] <= 1
        assert np.array_equal(fold[f][single], con[f][single]), f
        multi += int((cnt[f] >= 2).sum())
    assert np.array_equal(fold[4], con[4])          # the energy field and its settlement are the frozen law
    assert multi > 0                                 # not vacuous: these worlds contain contested template writes


def test_fold_differs_from_contest_only_at_contested_sites():
    xp, K = cpu()
    s = world(np.random.default_rng(7), 16)
    fold, _ = FP.step_fold(xp, K, 16, 0xF00D, 3, s, EN)
    con, _ = FP.contest_step(xp, K, "XOR", 16, 0xF00D, 3, s, EN)
    cnt, _, _ = loop_reference(s)
    differ = sum(int((fold[f] != con[f]).sum()) for f in range(4))
    assert differ > 0
    for f in range(4):
        assert ((fold[f] != con[f]) <= (cnt[f] >= 2)).all()


def run_ticks(stepper, s, ticks, seed, n):
    xp, K = cpu()
    s = [a.copy() for a in s]
    for t in range(ticks):
        s, _ = stepper(xp, K, n, seed, t + 1, s, EN)
    return s


def fold_stepper(xp, K, n, seed, tick, s, en):
    return FP.step_fold(xp, K, n, seed, tick, s, en)


def contest_stepper(xp, K, n, seed, tick, s, en):
    return FP.contest_step(xp, K, "XOR", n, seed, tick, s, en)


def test_without_energy_writes_fold_is_translation_and_seed_invariant():
    n = 12
    s = world(np.random.default_rng(11), n, energy_writes=False)
    base = run_ticks(fold_stepper, s, 12, 0xF00D, n)
    for sh in ((1, 0), (0, 5), (7, 3)):
        moved = run_ticks(fold_stepper, [np.roll(a, sh, axis=(0, 1)) for a in s], 12, 0xF00D, n)
        assert all(np.array_equal(np.roll(b, sh, axis=(0, 1)), m) for b, m in zip(base, moved)), sh
    for sd in (0xBEEF, 0xCAFE):
        assert all(np.array_equal(b, o) for b, o in zip(base, run_ticks(fold_stepper, s, 12, sd, n)))
    # Non-vacuous: on the same world the contest law depends on coordinates.
    cbase = run_ticks(contest_stepper, s, 12, 0xF00D, n)
    cmoved = run_ticks(contest_stepper, [np.roll(a, (7, 3), axis=(0, 1)) for a in s], 12, 0xF00D, n)
    assert not all(np.array_equal(np.roll(b, (7, 3), axis=(0, 1)), m) for b, m in zip(cbase, cmoved))


def test_energy_contests_remain_the_only_coordinate_path():
    """With energy writes allowed, the fold law may depend on coordinates, and only through energy-field contests."""
    n = 12
    xp, K = cpu()
    s = world(np.random.default_rng(12), n, energy_writes=True)
    _, _, e_cnt = loop_reference(s)
    assert (e_cnt >= 2).any()
    _, counts = FP.gather(xp, s, 1)
    assert np.array_equal(counts[4].astype(np.int64), e_cnt)


def test_install_maps_xor_to_fold_and_refuses_other_ops():
    xp, K = cpu()
    s = world(np.random.default_rng(13), 10)
    want, _ = FP.step_fold(xp, K, 10, 5, 2, s, EN)
    con, _ = FP.contest_step(xp, K, "XOR", 10, 5, 2, s, EN)
    try:
        assert FP.install() == "aeth01.op_xor_fold"
        got, _ = X.step(xp, K, "XOR", 10, 5, 2, s, EN)
        assert all(np.array_equal(a, b) for a, b in zip(got, want))
        assert all(np.array_equal(a, b) for a, b in zip(FP.contest_step(xp, K, "XOR", 10, 5, 2, s, EN)[0], con))
        for op in ("REPLACE", "ADD", "ROTX"):
            with pytest.raises(ValueError):
                X.step(xp, K, op, 10, 5, 2, s, EN)
        with pytest.raises(NotImplementedError):
            FP.step_fold(xp, K, 10, 5, 2, s, EN, observer=[])
    finally:
        FP.uninstall()
    assert not FP.installed()
    again, _ = X.step(xp, K, "XOR", 10, 5, 2, s, EN)
    assert all(np.array_equal(a, b) for a, b in zip(again, con))


def test_frozen_search_and_reuse_evaluators_run_the_fold_law():
    """The patch must reach the frozen callers: r3_frontier.Evaluator and r4_accum.Eval3 look the step up as
    express01.step at call time. Every one of their ticks is a fold tick, and the outputs leave the contest law's."""
    import r3_frontier as F
    import r4_accum as A
    F.set_geom("G1")
    patches = F.random_patches(np.random.default_rng(5), 4)

    def final_states(ev):
        ev.run_batch(patches)
        return ev.last_fin

    contest = final_states(F.Evaluator("XOR", side=2, backend="cpu"))
    contest3 = final_states(A.Eval3("XOR", side=2, backend="cpu"))
    try:
        FP.install()
        n0 = FP.STEP_CALLS
        fold = final_states(F.Evaluator("XOR", side=2, backend="cpu"))
        assert FP.STEP_CALLS - n0 == 16 * F.T_EVAL
        n1 = FP.STEP_CALLS
        fold3 = final_states(A.Eval3("XOR", side=2, backend="cpu"))
        assert FP.STEP_CALLS - n1 == 8 * F.T_EVAL
    finally:
        FP.uninstall()
        F.set_geom("R3")
    # random patches leave the output at 0 under both laws, so compare the patches' final (opcode, arg1, payload)
    assert not np.array_equal(fold, contest) and not np.array_equal(fold3, contest3)


def test_runner_refuses_express01_as_a_script():
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(HERE, "r01_run.py"), "unused.json", "R2/express01.py"],
                       capture_output=True, text=True)
    assert r.returncode == 2 and "bypass" in r.stderr


def test_r2_planted_ladder_unchanged_by_fold():
    """R2's timed one-shot gadgets never have two writers on one (site, field) in one tick, so their tables must be
    the frozen XOR law's tables exactly."""
    gadgets = ("C0", "C1", "C2", "C3", "C4")
    want = {g: X.table(g, "XOR") for g in gadgets}
    try:
        FP.install()
        got = {g: X.table(g, "XOR") for g in gadgets}
    finally:
        FP.uninstall()
    assert got == want


def _gpu():
    try:
        import cupy
        cupy.cuda.runtime.getDeviceCount()
        return X.load("gpu")
    except Exception:
        return None


@pytest.mark.skipif(_gpu() is None, reason="no CUDA device")
def test_gpu_fold_is_bit_identical_to_cpu():
    gx, GK = _gpu()
    xp, K = cpu()
    n = 48
    for seed in range(3):
        s = world(np.random.default_rng(200 + seed), n)
        c = [a.copy() for a in s]
        g = [gx.asarray(a) for a in s]
        for t in range(16):
            c, _ = FP.step_fold(xp, K, n, 0xF00D, t + 1, c, EN)
            g, _ = FP.step_fold(gx, GK, n, 0xF00D, t + 1, g, EN)
        assert all(np.array_equal(a, b.get()) for a, b in zip(c, g)), seed
