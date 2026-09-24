"""The scalar hash path must be the same hash, and must not warn.

NumPy reports integer overflow for SCALAR operations and says nothing
for ARRAY ones. Six of `mix64_vec`'s call sites pass a scalar -- the
seed/tick pre-mixes of the three hash domains -- so every AETH-01 run
emitted `RuntimeWarning: overflow encountered in scalar multiply` on a
wraparound that is the intended semantic. (It predates the 2026-09-22
memory round: the earlier expression form warned identically. It only
became visible when the pod's logs were first committed, because
`*.log` had been gitignored.)

`mix64_scalar` removes it at the arithmetic source, in explicit
modulo-2^64 Python-int arithmetic that cannot overflow at all, rather
than by filtering a warning. This file is what stops that from silently
becoming a DIFFERENT hash:

- equality with `mix64_vec` over a randomized 64-bit corpus plus the
  domain edges;
- equality with `oracle_aeth01.splitmix64_mix`, which is an independent
  restatement of the same finalizer in the CPU oracle, so the two
  implementations being wrong together would have to be a coincidence;
- the warning is gone from a real `gpu_step`, checked by turning
  RuntimeWarning into an error rather than by counting log lines;
- the scalar path still returns `np.uint64`, which is what `mix64_vec`
  returned for a scalar and what everything downstream broadcasts
  against.
"""

import warnings

import numpy as np
import pytest

from reference.gpu_aeth01 import (MASK64, MIX_MUL_1, MIX_MUL_2, gpu_step,
                                  mix64_scalar, mix64_vec)
from reference.oracle_aeth01 import splitmix64_mix


# The whole legal domain's corners, plus the constants the hash itself
# is built from (a finalizer fed its own multipliers is a classic way to
# hit a degenerate fixed point).
EDGE_INPUTS = [
    0, 1, 2, 3,
    (1 << 31), (1 << 32) - 1, (1 << 32),
    (1 << 63) - 1, (1 << 63), (1 << 63) + 1,
    (1 << 64) - 2, (1 << 64) - 1,
    0x9E3779B97F4A7C15,          # ARBITRATION_SEED_XOR
    0xBF58476D1CE4E5B9,          # MIX_MUL_1
    0x94D049BB133111EB,          # MIX_MUL_2
    0xD1B54A32D192ED03,          # MUT_DOMAIN_CONST
    0x2545F4914F6CDD1D,          # REPLENISH_DOMAIN_CONST
    0x1234ABCD,                  # the benchmark seed
]

CORPUS_SIZE = 100_000


def _corpus():
    rng = np.random.default_rng(0xC0FFEE)
    drawn = rng.integers(0, 1 << 64, size=CORPUS_SIZE, dtype=np.uint64)
    return np.concatenate([np.array(EDGE_INPUTS, dtype=np.uint64), drawn])


def test_scalar_and_vector_mixers_agree_over_a_randomized_64bit_corpus():
    corpus = _corpus()
    expected = mix64_vec(corpus.copy())
    got = np.array([mix64_scalar(v) for v in corpus], dtype=np.uint64)
    disagreements = np.flatnonzero(got != expected)
    assert disagreements.size == 0, (
        "mix64_scalar diverged from mix64_vec on %d of %d inputs, first at "
        "%d: %d != %d -- the scalar path is no longer the same hash, which "
        "changes aeth01.v1 arbitration and perturbation"
        % (disagreements.size, corpus.size, int(corpus[disagreements[0]]),
           int(got[disagreements[0]]), int(expected[disagreements[0]])))


def test_scalar_mixer_agrees_with_the_independent_cpu_oracle():
    # oracle_aeth01.splitmix64_mix is a separate restatement of the same
    # finalizer; it does not import the kernel.
    for value in EDGE_INPUTS:
        assert int(mix64_scalar(value)) == splitmix64_mix(value), value
    rng = np.random.default_rng(0x5EED)
    for value in rng.integers(0, 1 << 64, size=20_000, dtype=np.uint64):
        assert int(mix64_scalar(value)) == splitmix64_mix(int(value)), int(value)


def test_scalar_mixer_returns_uint64_so_broadcasting_is_unchanged():
    for value in EDGE_INPUTS:
        result = mix64_scalar(value)
        assert isinstance(result, np.uint64), type(result)
        assert result.dtype == np.uint64


def test_scalar_mixer_cannot_overflow_by_construction():
    # Every intermediate is masked, so the result is in range for every
    # input in the domain -- including inputs above 2**64, which the
    # mask must fold rather than reject.
    for value in EDGE_INPUTS + [(1 << 64), (1 << 65) + 7]:
        assert 0 <= int(mix64_scalar(value)) <= int(MASK64)


def test_the_constants_are_shared_not_restated():
    # If mix64_scalar ever grows its own copies of the multipliers, the
    # two mixers can drift apart one edit at a time.
    import inspect

    source = inspect.getsource(mix64_scalar)
    assert "MIX_MUL_1" in source and "MIX_MUL_2" in source and "MASK64" in source
    assert "0xBF58476D1CE4E5B9" not in source
    assert "0x94D049BB133111EB" not in source
    assert int(MIX_MUL_1) == 0xBF58476D1CE4E5B9
    assert int(MIX_MUL_2) == 0x94D049BB133111EB


@pytest.mark.parametrize("size", [1, 2, 8])
def test_a_real_tick_emits_no_runtime_warning(size):
    # The point of the repair. Errors on RuntimeWarning instead of
    # grepping logs, so "the warning is hidden" and "the warning is
    # gone" cannot be confused. np.errstate is set to raise as well, so
    # a float-error route to the same message would also fail here.
    rng = np.random.default_rng(7)
    fields = [rng.integers(0, 256, size=(size, size), dtype=np.uint8)
              for _ in range(5)]
    fields[0] = np.where(rng.random((size, size)) < 0.7, np.uint8(1),
                         fields[0]).astype(np.uint8)
    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)
        with np.errstate(over="raise", under="raise", invalid="raise",
                         divide="raise"):
            gpu_step(size, size, (1 << 64) - 1, (1 << 64) - 1, 255, 255,
                     1 << 32, 255, 1 << 32, *fields)
