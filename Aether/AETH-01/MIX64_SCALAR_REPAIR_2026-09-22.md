# AETH-01 Phase A -- removing the uint64 scalar-overflow warning

Instance: Aether[buckkeep-7a10ca4b], host BUCKKEEP, branch
`aether/aeth01-memwall-2026-09-22`.

Scope: the warning, and nothing else. No physics change, no
replay-identity change, no threshold change, no new capability.

## 1. First, a correction

The Phase 5 receipt called this warning a REGRESSION from the
memory-wall round's in-place `mix64_vec`. That was wrong, and the wrong
claim reached three committed documents before this repair started.

Direct experiment, both forms, scalar and array input, under
`warnings.catch_warnings` with `np.seterr(over="warn")`:

    OLD (expression)  scalar  1 warning   'overflow encountered in
                                           scalar multiply'
    NEW (in-place)    scalar  1 warning   same
    OLD (expression)  array   0 warnings
    NEW (in-place)    array   0 warnings

Both forms route through the same ufunc, so the baseline A40 run
emitted it too. It became visible this round only because this round
fixed the `.gitignore` rule that had been swallowing `*.log`, so the
pod's logs were committed for the first time. That is a change in
observability, not in behaviour. Recorded in
`roles/Aether/calibration/LEDGER.md` and annotated beside the original
claim in `GPU_MEMORY_OPTIMIZATION_01_2026-09-22.md` section 9.

## 2. Diagnosis

The table above is the whole diagnosis: **NumPy reports integer
overflow for SCALAR operations and says nothing for ARRAY ones.**

`mix64_vec` has twelve call sites. Six pass whole-lattice arrays; six
pass a scalar -- the seed/tick pre-mixes of the three hash domains:

    h0 = mix64_vec(np.uint64(seed) ^ ARBITRATION_SEED_XOR)   arbitration
    h1 = mix64_vec(h0 ^ np.uint64(tick))
    g0 = mix64_vec(np.uint64(seed) ^ MUT_DOMAIN_CONST)       perturbation
    g1 = mix64_vec(g0 ^ np.uint64(tick))
    r0 = mix64_vec(np.uint64(seed) ^ REPLENISH_DOMAIN_CONST) replenishment
    r1 = mix64_vec(r0 ^ np.uint64(tick))

So the warning is not about the lattice at all. It is six scalar mixes
per tick, of a value that depends only on `(seed, tick)`.

## 3. The repair

A scalar mixer in explicit modulo-2^64 Python-int arithmetic, which
cannot overflow rather than overflowing quietly:

    def mix64_scalar(x):
        mask = int(MASK64)
        x = int(x) & mask
        x ^= x >> 30
        x = (x * int(MIX_MUL_1)) & mask
        x ^= x >> 27
        x = (x * int(MIX_MUL_2)) & mask
        x ^= x >> 31
        return np.uint64(x)

The six scalar call sites call it; the six array call sites are
untouched. Applied character-identically to both kernel files.

Three properties make this a repair rather than a second hash:

- **The constants are shared, not restated.** `MASK64`, `MIX_MUL_1` and
  `MIX_MUL_2` are the same module constants `mix64_vec` uses. A test
  asserts the literals do NOT appear in `mix64_scalar`'s source, so the
  two mixers cannot drift apart one edit at a time.
- **The return type is unchanged.** `np.uint64` is exactly what
  `mix64_vec` returned for a scalar argument, so every downstream
  broadcast against a lattice array is byte-for-byte the same
  operation.
- **No warning filter anywhere.** Nothing is suppressed, caught or
  ignored; the arithmetic that overflowed no longer exists.

## 4. Falsification

1. **Old vs new hash over a large randomized 64-bit corpus.**
   2,000,014 values (2,000,000 drawn uniformly from the full 64-bit
   range, plus 14 domain edges: 0, 1, 2, 3, 2^31, 2^32-1, 2^32, 2^63-1,
   2^63, 2^64-2, 2^64-1, and the hash's own multipliers and domain
   constants, which are the classic way to land on a degenerate fixed
   point). **0 mismatches.**
2. **CPU/GPU differential, parity and properties.** 105 passed
   (`test_aeth01_gpu_differential.py`, `test_aeth01_canary_parity.py`,
   `test_aeth01_properties.py`, `test_aeth01_memory_footprint.py`).
   The AST parity test is what proves the two kernel files still match.
3. **Frozen A40 digests.** The reference kernel reproduces **8/8**
   including 2048^2; the bundled canary kernel 7/7 to 1024. These are
   digests produced on real A40 hardware under CuPy, so they are an
   external oracle, not a restatement of this code.
4. **Full suite.** `python -m pytest Aether/test -q`:
   **1002 passed, 5 skipped, 92 subtests, 0 failed** (583.7 s), up from
   994 passed -- the 8 new tests are this repair's own. The 5 skips are
   the usual Linux/POSIX pod-side gates, UNMEASURED on this host rather
   than passed.
5. **The warning is gone, not hidden.** Checked by turning
   RuntimeWarning into an error, on the BUNDLED kernel, with NumPy's
   own error policy additionally set to raise so the module's
   `np.seterr(over="ignore")` cannot mask anything:

       python -W error::RuntimeWarning, backend numpy_fallback,
       np.seterr(over="raise", under="raise", invalid="raise",
                 divide="raise")
       12 ticks at sizes 1, 3, 16, 64, seed and tick at 2^64-1,
       write_cost 255, maintenance 255, replenish and mutation
       certain -> NO RuntimeWarning raised.

   **Control for that check:** the same harness, given a deliberate
   `np.uint64(2**63) * np.uint64(4)`, DOES raise
   `RuntimeWarning: overflow encountered in scalar multiply`. Without
   this control, "no warning raised" would be indistinguishable from
   "the check cannot see warnings" -- which is the failure mode this
   program keeps finding in its own instruments.

A cross-check that is stronger than 1-5 because it does not involve
this code at all: `mix64_scalar` is asserted equal to
`oracle_aeth01.splitmix64_mix`, the CPU oracle's independent
restatement of the same finalizer, over the edges plus 20,000 random
values. Two implementations agreeing is weak; three, one of which was
written for a different purpose and does not import the others, is not.

## 5. Consequence for deployment

`image_manifest.json`'s kernel hash moved again:

    aeth01_gpu_kernel.py
      f6323456b190f71e094fd1342fcbe5956c6c8b708f148c9597159dd9d8d78ed4
   -> 138b32dccd1d69ede80bbe474fa028f6669fed525cb42e06afc6f6f594480f5f

Regenerated with `image_manifest.py`; exactly one hash changed;
`installed_dependencies` and `immutable_image_digest` remain null. Any
pod launched from the Phase 5 commit is running the pre-repair kernel
-- identical in behaviour, but a different artifact identity, and the
`AETH01_COMMIT` pin must be updated for any further run.

## 6. What this does not change

Nothing observable. `aeth01.v1` semantics, the replay identity, the
CPU oracle, `pod_service.py`, every threshold and every digest are
unchanged -- which is the entire claim, and the reason the evidence
above is all equality tests rather than measurements.
