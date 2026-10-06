# AETH-V2B-ER01 knowledge-transfer notes

Source: worktree C:/Prometheus-worktrees/aether-mwo, HEAD 05a46d2af (read-only).
All paths are relative to the worktree root. All commands run from the worktree root.
Line numbers are as of 05a46d2af.

Note added at commit time (BUCKKEEP Aether, 2026-10-05): Aether M2 reports that H1b continuity reproduces exactly on the
RTX 5060 Ti through the new ER01 runner: frozen_net64 = 0.9259185791015625. Consistent with Q4 below, the quoted
0.923 has no committed raw artifact; use the reproduced value (and the AETH-03 scout0 0.927 at 128^2) as references.

---------------------------------------------------------------------------

## Q1. Which kernel/module produced the "~92% frozen" finding

Short answer: the CPU NumPy reference kernel `aeth01.v1`, not a GPU kernel
and not AGE.

- Kernel: `Aether/test/reference/gpu_aeth01.py`, `gpu_step()` (line 111).
  The file is a "GPU-shaped" NumPy implementation. Its docstring (lines 1-26)
  says it was never run on GPU itself.
  - Its CuPy twin is `Aether/runpod/aeth01_canary/aeth01_gpu_kernel.py`,
    `gpu_step()` (line 99), with a cupy/numpy shim at lines 15-18.
    `Aether/test/test_aeth01_canary_parity.py` asserts the two files are
    AST-identical.
  - The CuPy twin produced the 2048^2 AETH-02 trajectories:
    `Aether/runpod/aeth02_circuitry/aeth02_runner.py:37`.
- "AGE" is not a kernel. `Aether/runpod/aeth01_canary/age_controller.py` is
  the stdlib RunPod launch/recovery controller (plan/run/recover/combine; see
  its docstring lines 1-40).
- Entry point for the 92% number (AETH-02 H1b):
  `Aether/observatory/aeth02_falsifiers.py`, `h1b_frozen_neighbourhoods(n=256,
  warmup=2500, window=64, ...)` at line 181. It is called from `main()`
  around line 627.
  - It uses `run()` (line 85) and `step()` (line 73), which call
    `K.gpu_step` with `K = gpu_aeth01` (line 37).
  - Command (from AETH-02_CLOSE section 0):

        python Aether/observatory/aeth02_falsifiers.py h1b --n 256 --warmup 2500 --out h1b.json

    (The report itself quotes `... all --n 256 --warmup 2500`.)
- Where the regime constants are defined (each module repeats them, with
  no shared config):
  - `Aether/observatory/aeth02_falsifiers.py:46-51`:
    - `B_BALANCED = dict(write_cost=1, maintenance_cost=1, replenish_numer=int(round(0.125*2**32)), replenish_amount=8)`
    - `B_SEED0 = 0x5C011701`, `B_RNG0 = 0xA37E01`
    - `MUT_NUMER = round(0.1*2**32)`
  - The same block appears in:
    - `Aether/observatory/aeth03_scouts.py:56-61` (as SEED0/RNG0/MUT_ON)
    - `Aether/runpod/aeth02_circuitry/aeth02_orchestrate.py:77-81`
    - the original definition: `Aether/observatory/aeth01_scout.py:93-94`
      (ROUND2_REGIMES "B_balanced", `prob()` at line 42)
- The aeth03_variants baseline is the same kernel.
  - `Aether/observatory/aeth03_variants.py:162-163`: variant "v1" calls
    `K.gpu_step` directly. SEMANTICS_ID "aeth01.v1" is at line 93.
  - It produced the re-measurement of 0.927 at 128^2 (warmup 1500) in
    AETH-03 scout0:

        python Aether/observatory/aeth03_scouts.py v1 --n 128 --seeds 2 --out-dir OUT

    - Evidence: `Aether/AETH-03/evidence/2026-09-26_scout0/scout_v1_n128_s{0,1}.json`
      (`S0.frozen_fraction_64` = 0.92676, 0.92706)
    - Reducer: `python Aether/observatory/aeth03_scouts_reduce.py Aether/AETH-03/evidence/2026-09-26_scout0`
- Semantics text: `Aether/AETH-01/AETH01_REPAIRED_FREEZE_CANDIDATE.md` s3.

## Q2. The "free-compute / no-maintenance" regime

- Name: `C_free_compute`.
- Definition: `Aether/observatory/aeth01_scout.py`
  - line 54 (ROUND1_REGIMES, starting at line 49) and line 83
    (ROUND2_REGIMES, starting at line 80):
    `dict(write_cost=0, maintenance_cost=0, replenish_numer=0, replenish_amount=0)`
  - Physics seed `PHYSICS_SEED = 0x5C0117` (line 37). Init rng_seed 0xA37E
    (line 159). SIZE=128, TICKS=1500 (lines 33-34).
- Prose spec: `Aether/AETH-01/ECONOMICS.md:78` ("Regime C -- Free compute":
  WRITE_COST=0, MAINTENANCE_COST=0, REPLENISH_NUMER=0; a negative control).
- It is a parameter dict, not a flag. There is no CLI flag to select it in
  aeth02_falsifiers, aeth03_scouts or aeth_mobility; all three hard-code
  B_BALANCED.
- Run command: `python Aether/observatory/aeth01_scout.py X scout.jsonl 2`.
  `main()` at line 143 reads argv[2] as the output path and argv[3] as the
  round, and ignores argv[1].
- Evidence:
  - `Aether/AETH-01/evidence/2026-09-22_scout/scout_round{1,2}.jsonl`
  - Findings: `Aether/AETH-01/SCOUT_FINDINGS_2026-09-22.md:45-75`. Regime C
    "freezes at a fixed point" (aeth01_scout.py:73-77). Its only template
    churn is perturbation-driven (C_free 50%, mut 0.5: template sum 0.2981).
- First Light also ran C_free_compute at 4096^2 on GPU. Tick-1 replay digest
  for seed0: `85bf28673ad02641...` MATCH
  (`Aether/AETH-01/FIRST_LIGHT_01_2026-09-22.md:107-114`).

## Q3. GPU conformance: known-answer commands and digests

(a) Canary, 300/300 (CPU oracle vs GPU kernel, bit-exact)

- Runner: `Aether/runpod/aeth01_canary/run_canary.py`
  - corpus: RNG_SEED=0, 200 single-tick + 20 x 5-tick trials, MAX_DIM=4,
    EXPECTED_CASES=300 (lines 70-77)
  - random write_cost/maint/replenish/mut over the full byte domain,
    including 0 (lines ~159-167)
- Command on a GPU pod, from that directory: `python3 run_canary.py`, which
  writes `receipt.json`. The image CMD runs it via `pod_service.py`
  (Dockerfile:28; image pins numpy==2.2.0, cupy-cuda12x==13.3.0 at line 17).
- Local NumPy smoke only (not GPU evidence):
  `AETH01_CANARY_REQUIRE_GPU=0 python run_canary.py`
- The receipt holds no state digest. It holds pass counts plus the sha256 of
  each source file. Reproducible today: the current files hash to exactly the
  values in `Aether/AETH-01/evidence/2026-09-24_aeth02_trajectories/canary_receipt.json`
  (PASS, cupy, 300/300, run_id aeth02-20260924T070408Z-efe7be17, CuPy 13.3.0):
  - aeth01_cpu_oracle.py `1b28db2a10a9b9eb112af1a2addb162e63afa7cce214292dbff7401074df5f75`
  - aeth01_gpu_kernel.py `1e89830d62e50266705ab95250890a80ab45479f336fd5b894e5b6af7f773f65`
  - run_canary.py `751d5a20f324cc862e5b1fe29c3c40e11b41a50a040b418f6953ed14ea4b0399`
  - Check: `sha256sum Aether/runpod/aeth01_canary/{aeth01_cpu_oracle,aeth01_gpu_kernel,run_canary}.py`
- Earlier canary receipts (first_light, calibration, optimized_scale_run)
  carry older aeth01_gpu_kernel.py hashes, because the kernel was edited
  between runs.
- Receipt gate: `age_controller.py:501-510` and
  `aeth01_scale_orchestrate.py:187` require 300/300/300.

(b) A40 final-state digests (the strongest reproducible digests)

- Expected digests file: `Aether/test/test_aeth01_memory_footprint.py:46-52`
  (`A40_DIGESTS`, sizes 16..256)
  - sizes up to 16384:
    `Aether/AETH-01/GPU_MEMORY_OPTIMIZATION_01_2026-09-22.md:148-151, 340-353`
  - raw: `Aether/AETH-01/evidence/2026-09-22_optimized_scale_run/{bench.log,scale_report.txt}`
- Digest definition: sha256[:16] over the 5 uint8 fields after 7 ticks.
- Parameters: SEED=0x1234ABCD, WRITE_COST=10, MAINT=1, REPL_NUMER=MUT_NUMER=2**31,
  REPL_AMT=5 (`aeth01_bench.py:27-31`).
  These are NOT the B-balanced parameters.
- Digests:
  - 16: `1000219c591e1595`
  - 32: `9f65f15cb87b630f`
  - 64: `3ce333436da923b0`
  - 128: `3ab66c98546a3a95`
  - 256: `7383c7d828504a30`
  - 512: `a04b1321280b0b97`
  - 1024: `87b8194c84a440d0`
  - 2048: `f2ad4a9ec9dbac4f`
  - 4096: `3741cde26ed38979`
  - 8192: `2f787e64bf323091`
  - 16384: `b3d06be54c1be93c`
- Reproduced on CPU in this session, 5 passed in 0.96 s:

      PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider -q Aether/test/test_aeth01_memory_footprint.py -k digest

- GPU re-run: `python3 Aether/runpod/aeth01_canary/aeth01_bench.py` on a pod.
  It prints a digest per size, with parity against the oracle up to 128.

(c) Known-answer lane, CPU units, cross-host

- Expected-hash file: `ops/campaigns/C-002/E-007/known_tasks.json`
  (`expected_legacy_sha256`). Built by
  `python Aether/observatory/aeth03_lane_reduce.py expected --evidence Aether/AETH-03/evidence/2026-09-26_propagation <law,seed,arm,start:stop ...>`.
- Example T-001 (v1, seed_index 0, off, slice 0:4, n128, warmup 1500, ticks 400):
  - expected_legacy_sha256 `1aa05bb79de90692da1813ed24e833ae569c7c47872b9d8a12acf6f989ec9499`
  - result_sha256 `d3cb0525dc7c292846410cc2aa2a6190c32451be129a07b7af25485ecd449d3b`
  - Bit-identical on BUCKKEEP (Win, NumPy 2.4.3) and 3 RunPod Linux hosts
    (NumPy 1.26.3); see `ops/campaigns/C-002/E-007/REDUCTION.json`.
- Commands:
  - run: `python Aether/observatory/aeth03_unit.py --law v1 --seed-index 0 --arm off --slice 0:4 --out T-001.json`
  - reduce: `python Aether/observatory/aeth03_lane_reduce.py reduce --tasks ops/campaigns/C-002/E-007/known_tasks.json --results <dir>`

## Q4. Observatory functions and the source of ~92%

- Frozen fraction:
  - (i) `aeth02_falsifiers.h1b_frozen_neighbourhoods` (line 181):
    - n=256, warmup 2500, window 64 ticks, perturbation ON (MUT_NUMER 0.1)
    - frozen = no net change in the 4 template fields (opcode, arg0, arg1,
      payload) between warm state and warm+64
    - output key `frozen_fraction_all_sites`
  - (ii) `aeth03_scouts.battery` S0 (lines 184-206):
    - same definition, n=128, warmup 1500, 64 ticks, MUT_ON
    - output key `S0.frozen_fraction_64`
  - Both compare endpoints only. A byte that changes and returns within the
    64 ticks counts as frozen.
- Template turnover: `Aether/observatory/aeth_mobility.py`
  - `MobilityMeter.update` (line 64; turnover appended at line 78) gives the
    per-tick share of 4*n^2 template bytes changed.
  - `metrics()` (line 92) gives turnover_early and turnover_late (first and
    last 100 ticks, EDGE=100), persistence, revisit, counter and
    active_site_share.
  - `classify()` (line 103) with `P1_RULE` (line 46; FROZEN if
    turnover_late < 0.002).
  - Driver: `mobility()` (line 124). Command:
    `python Aether/observatory/aeth_mobility.py --law v1 --seed-index 4 --arm off --out m.json`
  - S3 edge turnover (Jaccard) is in `aeth03_scouts.py` (docstring lines 26-28).
- Active WRITE density: `Aether/observatory/aeth01_observatory.py`
  `cheap_counters()` (line 187):
  - `activity_density = (WRITE sites with energy >= write_cost)/n^2`
  - also `write_density`, `starved_density`, `energy_total`
  - Scouts variant: `aeth03_scouts.emitters()` (line 94).
- Energy state:
  - `cheap_counters()['energy_total']`
  - `gini_from_counts(histogram256(energy))` (line 75; used in
    `aeth02_falsifiers.measure`)
  - `S0.energy_mean` in `aeth03_scouts.battery`
  - per-field `change_rate()` (line 207; the energy field dominates in B,
    see SCOUT_FINDINGS:58-63)
- Where the 92% number lives:
  - `Aether/AETH-01/AETH-02_CLOSE_2026-09-24.md:80-98` (s1b table: **0.923**;
    "92% of the lattice shows no net template change over 64 ticks") and
    line 291
  - restated in `Aether/AETHER_ENGINE_CARD.md:96, 128`
  - 128^2 re-measurement 0.927: `Aether/AETH-03/PHYSICS_DESIGN_01_2026-09-26.md:408`
    and `Aether/pivot/AETHER_REVIEW_2026-09-27.md:267`
  - Size scan, warmup 900, frozen64 0.9219/0.9231/0.9240/0.9252 at
    128/192/256/384:
    `Aether/AETH-01/evidence/2026-09-24_aeth02_falsifiers/lattice_size_scan.log`
- NOT FOUND: a committed raw output for the H1b 0.923 value.
  - `evidence/2026-09-24_aeth02_falsifiers/falsifiers_256.json` has keys
    control/h1/h2/h3/h4 only, with no h1b.
  - `falsifiers_256_console.log` has no [h1b] line.
  - Also NOT FOUND: the script that generated `lattice_size_scan.log`
    (grepped Aether/, ops/, roles/Aether for "frozen64" and "lattice_size_scan").
  - The re-derivable evidence is the AETH-03 scout0 JSONs (0.927 at 128^2).

## Q5. Sparse-soup initial conditions and seed namespace

- Generator: `Aether/observatory/aeth01_run.py`
  - `build_initial("sparse_soup", h, w, rng_seed, write_density, energy_mode="uniform")`
    (line 47)
  - `numpy.random.default_rng(rng_seed)`. Call order: opcode background
    (non-WRITE bytes), is_write mask, arg0, arg1, payload, energy uniform
    0..255.
  - The recipe carries `initial_state_digest` (sha256[:32]).
    `verify_recipe()` rebuilds it.
  - Historical density is **write_density=0.50**, not sparse in the literal
    sense: `aeth02_falsifiers.py:91`, `aeth03_scouts.initial` lines 80-82,
    `aeth02_orchestrate.py:88`. The scout rounds also used 0.02, 0.10 and
    0.50 (`aeth01_scout.py` ROUND1/2_INITS).
- Seed namespace, offset by seed_index:
  - `seed = 0x5C011701 + seed_index` (physics, hash key)
  - `rng_seed = 0xA37E01 + seed_index` (init)
  - Sources: `aeth03_scouts.battery` line 185, `aeth_mobility.mobility`,
    `aeth02_closure.py:371-372`, `aeth03_longhorizon.py:60`.
  - AETH-02 2048^2 trajectories: `(0xA37E0{1,2,3}, 0x5C01170{1,2,3})`
    (`aeth02_orchestrate.py:114-116`).
- Seed_index usage history:
  - 0-1: AETH-02 / AETH-03 scouts
  - 0-3: Block D (propagation)
  - 4-7: fresh TEST seeds (E-009, E-012, V2B TEST-1/2/3)
  - 100: DEV-only calibration seed, never used for verdicts
  - Sources: `ops/campaigns/C-002/E-009/EXPERIMENT.md:14`,
    `Aether/V2B/TEST-2/PREREGISTRATION.md:20-21`,
    `Aether/V2B/TEST-3/PREREGISTRATION.md:28-30`
- Older AETH-01 scout namespace: physics `0x5C0117`, init `0xA37E`
  (`aeth01_scout.py:37, 159`).
- Auxiliary RNGs use their own per-module constants, e.g.:
  - 0xA3 + seed_index for origins (`aeth03_scouts.py:186`)
  - 0x11A2 lesion (`aeth02_falsifiers.py:253`)

## Q6. Known defects that would bite an energy-regime sweep

- `roles/Aether/DEFECTS.md` has a single entry: DEF-AETH-001, ubu001 disk
  full. It is infrastructure, RESOLVED, and has no physics defect.
- PHYSICS_DESIGN_03 amendments A1-A6 (`Aether/AETH-03/PHYSICS_DESIGN_03_2026-09-27.md:252-359`)
  are about verdicts (rcv_str, E-008..E-012). None is a dtype or backend
  defect.
- `Aether/runpod/FAILURE_PLAYBOOK.md` covers pod and bootstrap failures only
  (e.g. line 316, the cupy wheel install). No numeric divergence entries.
- Hazards found in code and docs:
  1. **Parameters are hard-coded to B_BALANCED** in every frozen/turnover
     instrument:
     - `aeth02_falsifiers.params()` (line 69)
     - `aeth03_scouts.params()` (line 65)
     - `aeth_mobility.mobility()` (via `S.params`)
     There is no CLI flag for write/maint/replenish
     (`aeth_mobility.py:182-189`; `aeth03_unit.py:199-208`). An ER sweep
     needs new plumbing; `Aether/AETH-03/FOLLOWUP_RANKING_2026-09-30.md:21`
     calls this "parameter plumbing". If a variant id is not passed through,
     results would silently stay B-balanced.
  2. **Energy dtype.** Energy is uint8, saturating at 255 (phases 5 and 7)
     and floored at 0 (phase 6), with arithmetic in int64
     (`gpu_aeth01.py:174-195`).
     - transfer_amt, value and best_value were narrowed to int16. That is
       valid only over the domain write_cost, maint, replenish_amount in
       [0, 255] (`GPU_MEMORY_OPTIMIZATION_01_2026-09-22.md:107-129`; 464/464
       adversarial cases, line 156).
     - Values >255 are outside the validated domain, and the int16 casts
       could wrap.
     - Inflow above 255 is destroyed as spillage
       (`AETH01_REPAIRED_FREEZE_CANDIDATE.md:49`). A rich-inflow regime will
       saturate, not accumulate.
  3. **write_cost=0.** `starved = energy < 0` is never true, so every WRITE
     site is active forever, and zero-amount energy proposals can still win
     and jam (`ASTRA_CLOSURE_REVIEW_02.md:200`). Under C_free, `emitters()`
     and `activity_density` therefore equal write_density, so the activity
     metric is uninformative.
  4. **CuPy vs NumPy.** No divergence was ever recorded (canary 300/300 x4;
     A40 digests reproduced on CPU). There is one known cosmetic issue: a
     uint64 scalar-overflow RuntimeWarning in `mix64` that CuPy cannot
     silence with `np.seterr`. It was fixed at the source
     (`Aether/AETH-01/MIX64_SCALAR_REPAIR_2026-09-22.md`, commit 66c55243f).
     Ledger correction: `roles/Aether/calibration/LEDGER.md:10-21`.
  5. **Cross-backend long-horizon agreement is unverified.** It is verified
     only at tick 1 (4096^2), at 7 ticks (16..16384) and for the canary
     cases. "Thousands of ticks" is explicitly open
     (`FIRST_LIGHT_01_2026-09-22.md:116-122`). Every ~92% number came from
     CPU NumPy, not GPU.
  6. **The B-regime change_rate is ~97% the energy field decrementing**
     (`SCOUT_FINDINGS_2026-09-22.md:58-66`). Use template-only metrics
     (frozen64, turnover) when comparing regimes with different maintenance.
- Prior statement of the gap: `Aether/AETHER_ENGINE_CARD.md:159-161`
  ("the frozen-medium result may be a property of B-balanced energy, not of
  the law").
