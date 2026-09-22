# AETH-01 GPU Memory-Wall Optimization -- Round 01 (2026-09-22)

Instance: Aether[buckkeep-7a10ca4b], host BUCKKEEP.
Built from base_sha `251bc987e` in
`C:/Prometheus-worktrees/aether-memwall` on branch
`aether/aeth01-memwall-2026-09-22`.

Goal (unchanged from `GPU_MEMORY_OPTIMIZATION_HANDOFF_2026-09-22.md`):
push AGE past the A40 memory wall while preserving `aeth01.v1` behavior
exactly. Target was roughly 261 -> 120 bytes/site.

**Disposition: `MEMORY_WALL_MOVED`** (Phase 5 complete, section 9).

On a real A40 the optimized kernel ran **16384 x 16384 =
268,435,456 sites at 7.42 s/tick with 12.2 GiB still free**, where the
pre-optimization kernel died with OutOfMemoryError. The canary passed
300/300 bit-exact against the CPU oracle on the GPU, and all ten
lattice sizes the two runs have in common produced byte-identical final
states. Total cost $0.025 of the $3 authorization; pod terminated and
absence confirmed twice.

Off-GPU, peak per-tick allocation measured 240.00 -> 113.01 bytes/site
(2.12x); on the A40 the marginal pool cost measured 257 -> 128
bytes/site (2.01x).

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

## 7. What was NOT established BEFORE the A40 run

ANNOTATION 2026-09-22, after Phase 5: every risk in this section was
subsequently CLOSED on real hardware (section 9). The list is left
standing, unedited, because it is the pre-registered statement of what
the run had to settle -- rewriting it after the fact would erase the
record of what was actually uncertain beforehand.

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

## 9. Phase 5 -- the A40 run

Executed 2026-09-22, one pod, pinned to commit
`084c648274a30a11573b2fd97647a186f6b4ffdc` (NOT `faf567ab8`, which the
Phase 5 instruction quoted as the branch head; that commit predates this
round and pinning it would have benchmarked the OLD kernel and answered
the wrong question).

Raw evidence is committed beside this document under
`evidence/2026-09-22_optimized_scale_run/`: `bench.log`, `canary.log`,
`receipt.json`, `result.json`, `scale_report.txt`, `verdict.txt`.

### Run identity

- `run_id`: `aeth01-20260922T184536Z-71bd2e9d`
- pod `6q9raukca794ou`, NVIDIA A40, SECURE, $0.49/hr, 20 GB disk
- image `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`
- on-pod stack: Python 3.11.10, NumPy 2.2.0, CuPy 13.3.0
- reported device memory: 45,498 MiB usable
- kernel shipped: `aeth01_gpu_kernel.py`
  `f6323456b190f71e094fd1342fcbe5956c6c8b708f148c9597159dd9d8d78ed4`
  -- the optimized one, confirmed by the receipt's own `source_hashes`,
  and verified before launch to be byte-identical between the local
  worktree, the git blob and the GitHub raw bytes the pod downloads

### Preflight (before any pod existed)

Inventory checked read-only: `ACTIVE_POD_COUNT 0`, auth working. The four
pinned files' sha256 were compared local vs git-blob vs GitHub-raw, all
four MATCH, so the pod's own `sha256sum -c` gate could not fail for a
line-ending or push-lag reason. A standalone terminate-and-verify script
was written BEFORE launch so that an orchestrator killed mid-run could
not leave a pod billing.

### Canary -- PASS, on the GPU

300 frozen differential cases against the CPU oracle, run on the A40
before any benchmarking:

- status **PASS**, backend **cupy**, **300 / 300 matched**, 0 mismatches
- `gpu_kernel_seconds` 11.779 (baseline run: 14.747 on the same corpus)

This is the load-bearing semantic result: the narrowed dtypes, the
`np.roll` gathers and the in-place `mix64_vec` all behave identically
under CuPy, not merely under NumPy. The three risks section 7 listed as
unverified are now verified on hardware.

### Scaling curve

Same fixed parameters as the baseline run (`SEED=0x1234ABCD`,
`WRITE_COST=10`, `MAINT=1`, `REPL_NUMER=MUT_NUMER=2**31`, `REPL_AMT=5`,
2 warmup + 5 measured ticks). Digest = sha256[:16] of the 5 uint8 fields
after 7 ticks.

| size | sites | tick_med (s) | sites/sec | mem used (MiB) | parity | digest | vs baseline |
|-----:|------:|-------------:|----------:|---------------:|:-------|:-------|:------------|
| 16 | 256 | 0.022952 | 11,153.9 | 270.2 | PASS | 1000219c591e1595 | same |
| 32 | 1,024 | 0.023848 | 42,939.2 | 270.2 | PASS | 9f65f15cb87b630f | same |
| 64 | 4,096 | 0.023230 | 176,326.0 | 270.2 | PASS | 3ce333436da923b0 | same |
| 128 | 16,384 | 0.023075 | 710,021.5 | 272.2 | PASS | 3ab66c98546a3a95 | same |
| 256 | 65,536 | 0.023026 | 2,846,231.4 | 278.2 | SKIPPED | 7383c7d828504a30 | same |
| 512 | 262,144 | 0.022989 | 11,402,985.0 | 302.2 | SKIPPED | a04b1321280b0b97 | same |
| 1024 | 1,048,576 | 0.032410 | 32,353,728.2 | 398.2 | SKIPPED | 87b8194c84a440d0 | same |
| 2048 | 4,194,304 | 0.119645 | 35,056,228.4 | 782.2 | SKIPPED | f2ad4a9ec9dbac4f | same |
| 4096 | 16,777,216 | 0.467566 | 35,882,025.5 | 2,318.2 | SKIPPED | 3741cde26ed38979 | same |
| 8192 | 67,108,864 | 1.859690 | 36,086,056.4 | 8,462.2 | SKIPPED | 2f787e64bf323091 | same |
| **16384** | **268,435,456** | **7.419936** | **36,177,599.4** | **33,038.2** | SKIPPED | **b3d06be54c1be93c** | **baseline OOM'd** |
| 32768 | 1,073,741,824 | -- | -- | -- | -- | -- | `AETH01_BENCH_STOP reason=OOM` |

"parity PASS" is bit-exact agreement with the pure-Python CPU oracle,
checked where the oracle is practical (<= 128).

**All ten digests the two runs share are byte-identical to the
pre-optimization A40 run** (`RUNPOD_SCALE_RECEIPT_2026-09-22.md`). That
is the semantic claim settled on hardware rather than by local proxy.
16384^2's digest `b3d06be54c1be93c` is new because the baseline could
not reach that size at all.

### The critical falsifier: PASSED

Section 6 predicted, before the run, that 8192^2 should fall from
16,718 MB to roughly 8.2-9.2 GB of used pool, and said that a materially
higher number would falsify the allocation model even if the digests
were right.

    8192^2 observed:  8,462.2 MiB = 8.87 GB   -- INSIDE the band
    baseline:        16,718.2 MiB
    reduction:        1.976x

### The pool model, now over-determined rather than guessed

Section 6's two overhead models rested on a single data point and were
flagged as the weakest numbers in this document. Two large sizes now
determine both parameters, and the fit is exact:

    used(MiB) = 270.2 + 128.000 bytes/site

Solved from 8192^2 and 16384^2 alone, the intercept comes out at
270.2 MiB -- which is exactly the floor the four smallest lattices
measured independently (270.2 MiB at 16, 32 and 64). A two-point fit
that reproduces a separately observed constant to the decimal is not a
coincidence.

The same form applied to the baseline run gives 257.000 bytes/site
marginal, so the measured on-GPU reduction is **2.008x**, against the
2.124x that tracemalloc measured off-GPU. The gap is CuPy's pool
rounding, and 128.000 bytes/site exactly is that rounding showing
itself: the measured 113.01 bytes/site of real allocation is being
served from power-of-two-shaped pool blocks.

Both section 6 predictions bracket the truth: 16384^2 was predicted at
32.99 GB (multiplicative) and 35.98 GB (additive) and came in at
34.64 GB, between them.

### Answering the primary question

> Can 16384^2 = 268,435,456 sites now execute on one A40 while
> remaining bit-exact aeth01.v1?

**Yes.** 7.42 s/tick, 36.18 M sites/sec, 33,038.2 MiB used with
**12,459.8 MiB (12.2 GiB) still free** -- comfortable, not marginal.

### The new limiting boundary

Still memory, and still not time. 32768^2 stopped with
`AETH01_BENCH_STOP reason=OOM size=32768 err=OutOfMemoryError`, which
the model explains exactly: 1,073,741,824 sites would need
270.2 + 131,072 MiB = **128.3 GiB** against 45,498 MiB available.

The model puts the true ceiling at **370.5 M sites, about 19249^2** --
so 16384^2 is the largest power-of-two lattice that fits, and the next
doubling cannot fit on this device by a factor of ~2.9. Moving past
16384^2 is therefore a multi-GPU or sharding question, not another
constant-factor allocation question.

### Throughput

Peak **36,177,599 sites/sec**, up from 21,227,101 (**1.704x**). At the
one size both runs measured, 8192^2, tick time fell 3.161471 s ->
1.859690 s (1.700x). Section 4 guessed a bandwidth-bound GPU would also
get faster; it did, by 1.70x rather than the 2.3x seen on CPU.

Throughput is flat from 2048^2 upward (35.1, 35.9, 36.1, 36.2 M
sites/sec), so at 16384^2 the kernel is saturating the device rather
than degrading.

### Cost and containment

- pod wall time **186 s**, at $0.49/hr = **$0.0253**, against a $3
  authorization used to 0.84%
- exactly one pod, created on the first attempt (201), no
  pod-creating retries
- terminated `ACK_204`; absence confirmed by the orchestrator
  (`ACTIVE_POD_COUNT 0`) and then again by a separate script run
  afterwards from a clean process
- no credential printed, placed on argv, or written to any artifact; all
  six committed artifacts were scanned for credential patterns before
  committing
- BILLING RECONCILIATION IS INCOMPLETE and should not be read as done:
  $0.0253 is computed from measured pod wall time at the quoted SECURE
  rate. This client has no billing endpoint, so the charge itself was
  not read back from the provider. Confirming it in the console is a
  one-look operator action.

### One cosmetic regression, reported not hidden

Both `canary.log` and `bench.log` carry a new NumPy warning:

    /app/aeth01_gpu_kernel.py:42: RuntimeWarning: overflow encountered
    in scalar multiply  x *= MIX_MUL_1

It comes from the in-place `mix64_vec` when it is called on the numpy
SCALAR pre-mixes (`h0`, `h1`) rather than on an array. The uint64
wraparound is the intended semantic, and the bundled kernel cannot call
`np.seterr` because CuPy has no such function, so under the CuPy backend
the scalar path is not covered by the overflow policy the NumPy backend
sets. It is noise, not a defect: the canary matched 300/300 and all ten
shared digests are byte-identical. It was NOT fixed here because the
authorization said no kernel edits during the evidence run. Suggested
follow-up: compute the two scalar pre-mixes with explicit masking so the
warning cannot appear, which is a no-op on the values.

## 10. What is established now, and what still is not

Established on hardware: the optimized kernel is semantically identical
to the frozen one under CuPy; 268 M sites run on one A40; the memory
model is measured rather than projected; the boundary moved from
"16384^2 OOMs" to "32768^2 OOMs".

Still not established:

- **Nothing about the physics.** This round changed allocation and
  nothing else. `aeth01.v1` is still a CANDIDATE, not frozen, and no
  AETH-01 scientific claim is advanced by a faster kernel.
- Long runs. Every number here is 7 ticks. Nothing is known about
  stability, drift or determinism over the thousands of ticks a real
  campaign needs, and 7.42 s/tick means 16384^2 costs about 2.1 hours
  per 1,000 ticks on one A40 -- a campaign-planning fact, not a result.
- The ceiling of 19249^2 is a model extrapolation from two points, not a
  measurement. The only measured facts are that 16384^2 fits with
  12.2 GiB free and 32768^2 does not fit at all.
- Billing, as above.

## 11. Next executable action

None in this round; it is complete and its disposition is
`MEMORY_WALL_MOVED`. The seat's next decisions are AETH-01 science
questions (whether to freeze `aeth01.v1`, and which habitability
campaign the new 268 M-site capacity should be spent on), not further
kernel optimization -- the next doubling is a device-count problem, not
an allocation problem.
