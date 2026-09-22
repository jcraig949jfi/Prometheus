# AETH-01 GPU Memory-Wall Optimization -- Round 01 (2026-09-22)

Instance: Aether[buckkeep-7a10ca4b], host BUCKKEEP.
Built from base_sha `251bc987e` in
`C:/Prometheus-worktrees/aether-memwall` on branch
`aether/aeth01-memwall-2026-09-22`.

Goal (unchanged from `GPU_MEMORY_OPTIMIZATION_HANDOFF_2026-09-22.md`):
push AGE past the A40 memory wall while preserving `aeth01.v1` behavior
exactly. Target was roughly 261 -> 120 bytes/site.

**Local disposition: `MEMORY_WALL_MOVED_PENDING_HARDWARE`.**
Peak per-tick allocation measured 240.00 -> 113.01 bytes/site (2.12x)
with bit-exact output on every instrument available off-GPU. The claim
"the wall moved" is NOT yet made: it is a claim about an A40, and no A40
has run this kernel. Phase 5 is unstarted and costs money.

## 1. The previous round's accounting was never measured. This one is.

The handoff's Phase 2 was explicitly "analysis only, NOT yet validated"
-- a reasoned byte count, never executed. That number is not used here.

Peak allocation is measured with `tracemalloc`, which NumPy registers
its data allocations against. The harness first proves it can see NumPy
at all (it allocates a 4,000,000-byte array and requires the traced peak
to rise by at least that much -- observed 4,000,096) before reporting
anything. Without that check the whole table could read zero and look
like a triumph.

Baseline, unmodified kernel at `251bc987e`, NumPy backend:

| size | sites     | peak bytes  | bytes/site |
|-----:|----------:|------------:|-----------:|
| 64   | 4,096     | 987,833     | 241.17     |
| 128  | 16,384    | 3,936,857   | 240.29     |
| 256  | 65,536    | 15,733,386  | 240.07     |
| 512  | 262,144   | 62,919,306  | 240.02     |
| 1024 | 1,048,576 | 251,662,888 | 240.00     |

The asymptote is **240.00 bytes/site**. The A40 receipt's ~261 B/site is
CuPy *pool* occupancy at 8192^2, which includes pool rounding and the
benchmark's own retained state; the two numbers are consistent and are
not the same measurement. Every bytes/site figure below is the
tracemalloc peak, measured the same way.

## 2. What was changed, and what each change actually bought

Three changes, applied cumulatively, each measured on its own:

| variant | change | bytes/site | delta |
|:--------|:-------|-----------:|------:|
| baseline | -- | 240.00 | -- |
| v1 | one packed uint64 coordinate grid; toroidal gathers by `np.roll` | 216.00 | -24.00 |
| v2 | v1 + `mix64_vec` computed in place | 201.01 | -14.99 |
| v3 | v2 + narrowed field dtypes | 113.01 | -88.00 |

The handoff predicted the hash-chain temporaries were a marginal target
and the dtype work was the prize. Measurement agrees on the second half
and disagrees on the first: making `mix64_vec` in-place is worth 15
bytes/site for six lines, which is not marginal. It is safe because
`x = x.astype(np.uint64)` already returns a fresh array, so mutating it
cannot touch a caller's data.

### v1 -- coordinates and gathers

`np.meshgrid` materialized two full H x W int64 grids (16 B/site) whose
only purpose was to be packed into a uint64 key and to index neighbors.
Both uses are replaced:

- the packed key is built once per tick by broadcasting two thin 1-D
  ranges through the existing `pack_coords_vec` (8 B/site, one array);
- `arbitration_priority_vec`, `mu_vec` and `rho_vec` now take the packed
  array directly instead of a coordinate pair, so a coordinate pair is
  packed once per tick rather than once per (field, slot) -- 20 packings
  per tick removed;
- the neighbor gather `a[(row+dr) % H, (col+dc) % W]` is exactly the
  toroidal permutation `np.roll(a, (-dr, -dc), axis=(0, 1))`, so the two
  int64 index grids per slot are gone.

`pack_coords_vec` keeps its signature and stays in use; it is not dead
code.

### v3 -- narrowing, and why each narrowing is exact rather than lucky

Every narrowing below is justified from the VALIDATED parameter domain
in `oracle_aeth01.py` (`_require_int`), not from the values that happen
to appear in a test:

- `write_cost`, `maintenance_cost`, `replenish_amount` are validated
  into **[0, 255]**;
- all five lattice fields are uint8, so energy is in [0, 255].

Therefore:

| array | was | now | why it is exact |
|:------|:----|:----|:----------------|
| `direction` | int64 | uint8 | `arg0 % 4` is in {0,1,2,3} for every uint8 |
| `target_field` | int64 | uint8 | `arg1 % 5` is in {0,...,4} for every uint8 |
| `transfer_amt` | int64 | int16 | `energy - write_cost` is in [-255, 255] over the whole legal domain, and `payload` is in [0, 255] |
| `value` | int64 | int16 | selects between the two above |
| `best_value` | int64 | int16 | starts at 0, otherwise takes `value` at a valid slot, so it is in [0, 255] |
| `bit_index` | int64 | int16 | `key & 0b111` is in [0, 7] |
| `template[0..3]` | int64 | int16 | uint8 inputs, and `stored` is a XOR of a [0,255] value with `1 << b`, b in [0,7] |

Note what is NOT narrowed: `energy_i` and the running `e` stay int64,
and `best_priority`/`prio` stay uint64. The arbitration priority is a
64-bit hash and truncating it silently changes which neighbor wins a
contested write; section 5 shows that exact mistake being caught.

Also removed: `.astype(np.int64).copy()` on the four template arrays.
`astype` already returns a fresh array, so the `.copy()` allocated each
template field twice.

### A narrowing deliberately NOT taken

uint8 (rather than int16) for `value`/`transfer_amt`/`best_value` also
produces bit-identical output and saves a further ~8 bytes/site. It was
measured and rejected. It is only correct via an unobservability
argument -- at inactive sites `energy - write_cost` is negative, uint8
wraps it, and the wrapped value is never read because every consumer is
masked by `active`. int16 is correct by range over the entire legal
domain with no such argument. 113 bytes/site already clears the target;
buying 8 more with a weaker correctness story is a bad trade.

## 3. Falsification evidence

The optimized kernel is required to be BIT-EXACT, not close. Four
independent instruments, all run against both patched files:

1. **A40 digest oracle (the strongest evidence).** The eight final-state
   digests in `RUNPOD_SCALE_RECEIPT_2026-09-22.md` were produced on real
   A40 hardware under CuPy. The harness replicates `aeth01_bench.py`'s
   procedure exactly (same `RandomState` seeding, 2 warmup + 5 measured
   ticks, sha256[:16] over the five final uint8 fields). The unmodified
   kernel was checked FIRST, to prove the oracle reproduces on this host
   at all -- 7/7 match up to 1024. The optimized kernel then reproduced
   **8/8 including 2048^2**, and the bundled canary kernel 7/7 up to
   1024:

   | size | digest | | size | digest |
   |-----:|:-------|-|-----:|:-------|
   | 16 | 1000219c591e1595 | | 256 | 7383c7d828504a30 |
   | 32 | 9f65f15cb87b630f | | 512 | a04b1321280b0b97 |
   | 64 | 3ce333436da923b0 | | 1024 | 87b8194c84a440d0 |
   | 128 | 3ab66c98546a3a95 | | 2048 | f2ad4a9ec9dbac4f |

2. **Randomized differential**, 400 trials, dims 1..16 x 1..16, random
   seed/tick/write_cost/maintenance/replenish/mut, opcode biased 60% to
   WRITE so arbitration actually contends: **400/400 bit-exact** on all
   five fields and both counters.

3. **Adversarial differential**, 464 cases aimed AT the narrowing rather
   than around it: every extreme of the validated parameter domain,
   saturating and starving energy, perturbation and replenishment both
   fully on and fully off, all 20 direction x target-field combinations,
   degenerate lattices (1x1, 1x2, 2x1, 1x8, 8x1), non-square lattices,
   and seed/tick at the top of their range. The case that would break a
   careless narrowing -- `write_cost=255`, `energy=0`,
   `target_field==ENERGY`, driving `transfer_amt` to -255 -- is included
   explicitly. **464/464 bit-exact.**

4. **The existing suite**: `test_aeth01_canary_parity.py` (AST identity
   of the two files), `test_aeth01_gpu_differential.py`,
   `test_aeth01_properties.py` -- **95 passed**. Full `Aether/test`:
   **994 passed, 5 skipped, 92 subtests, 0 failed** (542 s), against
   984 passed / 5 skipped before the round. The 5 skips are Linux and
   POSIX pod-side gates, so on this Windows host they are UNMEASURED
   rather than passed, and nothing here claims pod-side behaviour.

5. **A regression guard that can fail.**
   `Aether/test/test_aeth01_memory_footprint.py` (10 tests) asserts the
   bytes/site ceiling, a "materially below the old baseline" check, the
   A40 digests for 16..256, and -- first -- that tracemalloc can see
   NumPy allocations at all, so the ceiling cannot pass vacuously. It
   was verified to bite: with the kernel reverted to `251bc987e`, four
   of its assertions fail, while the digest assertions correctly stay
   green because semantics never changed.

## 4. Speed, as a side effect

Not the objective, and measured only on NumPy/CPU, where it does not
predict GPU behavior:

| size | before (s/tick) | after (s/tick) | ratio |
|-----:|----------------:|---------------:|------:|
| 256 | 0.2679 | 0.0948 | 2.83x |
| 512 | 1.6726 | 0.6193 | 2.70x |
| 1024 | 6.2093 | 2.7172 | 2.29x |

Plausible on a bandwidth-bound GPU too, since less memory is moved, but
that is a hypothesis for Phase 5, not a result.

## 5. Controls (base role s2: positive, negative, cheat)

Three defects were injected deliberately to test whether the
instruments can see a broken kernel at all.

| injected defect | detected? |
|:----------------|:----------|
| A: uint8 instead of int16 for `value`/`transfer_amt` | **NO** |
| B: roll shift sign flipped, `(dr, dc)` for `(-dr, -dc)` | YES -- 8/464 adversarial, all digests differ |
| C: arbitration priority truncated to uint32 | YES -- 4/464 adversarial, 75/400 randomized, digests differ |

**Control A failed to be a control, and that is the finding**, not a
gap: uint8 there is genuinely semantics-preserving (section 2), so no
instrument should have flagged it. It is recorded as an inverted result
rather than quietly dropped. B is the gross transcription error and C is
the subtle one -- C changes only contested arbitration and is still
caught by all three instruments, which is the evidence that the channel
can observe the property being claimed.

## 6. Projection to 16384^2, stated as a falsifiable prediction

At 113.01 bytes/site, 16384^2 = 268,435,456 sites needs **30.3 GB** of
peak allocation. The A40 carries 48 GB. Two models of CuPy pool
overhead, both anchored on the single baseline data point (261 B/site of
pool against 240 B/site of measured peak at 8192^2):

- multiplicative (x1.0875): 123 B/site -> **33.0 GB**
- additive (+21 B/site): 134 B/site -> **36.0 GB**

Both fit. Both rest on ONE data point and are the weakest numbers in
this document; they are the prediction, not the result.

Sharper falsifier, at a size already measured on real hardware:
**8192^2 should drop from 16,718 MB to roughly 8.2-9.2 GB of used
pool.** If the A40 run reports 8192^2 materially above that band, the
allocation model in section 1 is wrong about CuPy even though the
digests are right, and the 16384^2 projection should not be trusted.

## 7. What is NOT established

- **No GPU has run this.** Every number here is NumPy on CPU. CuPy pool
  behavior, and its dtype-promotion and `roll` implementations, are
  unverified.
- **`np.roll` is a new API dependency** this kernel did not previously
  have. `cupy.roll` exists and accepts tuple shift/axis, but that is
  read from documentation, not observed on hardware.
- Narrowed-dtype arithmetic (`np.int16(1) << bit_idx`, int16/int64
  mixing under NEP 50) is verified on NumPy 2.4.3 locally; the pod ran
  NumPy 2.2.0 with CuPy 13.3.0.
- These three risks are bounded rather than open-ended: the on-pod
  300-case canary runs against the CPU oracle BEFORE any benchmarking,
  so a CuPy divergence stops the run at roughly $0.02 rather than
  corrupting a result.
- No physics changed. `aeth01.v1` semantics, the freeze candidate, the
  CPU oracle and `pod_service.py` are all untouched.

## 8. The deployment pin moved, on purpose

`Aether/runpod/aeth01_canary/image_manifest.json` pinned the kernel's
sha256 and the full suite failed on it, which is the pin working rather
than a nuisance:

    aeth01_gpu_kernel.py
      was 0b7c89bd35912c82cae9c3baca10d0e56eef3cf72222c9da045026f58c3195e3
      now f6323456b190f71e094fd1342fcbe5956c6c8b708f148c9597159dd9d8d78ed4

The manifest was regenerated with its own generator
(`image_manifest.py`); exactly one hash changed and nothing else, and
`installed_dependencies` / `immutable_image_digest` remain null, so no
build-verified identity is being claimed that was not checked.

Consequence for Phase 5: **any previously built or approved canary image
is now stale.** The source hashes recorded in
`RUNPOD_SCALE_RECEIPT_2026-09-22.md` describe the pre-optimization
kernel and must not be reused as the identity of this one.
`aeth01_scale_orchestrate.py` computes its per-file checksums at import
time rather than storing them, so it needs no edit -- it will pin
whatever it ships.

## 9. Next executable action

Phase 5: one A40 pod, sizes 256..16384, one pod at a time, $3 ceiling,
no pod-creating retries, terminate and re-confirm `ACTIVE_POD_COUNT 0`.
It spends real money and is therefore held for the operator's explicit
go. Phase 6's final disposition (`MEMORY_WALL_MOVED` /
`NO_MATERIAL_GAIN` / `SEMANTIC_PARITY_FAILURE`) is written from that
run's receipt, against the section 6 predictions.
