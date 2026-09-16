# LAUNCH_R8 -- REPRODUCIBLE LAUNCH SPECIFICATION

Purpose (operator prompt 27): document round 8 in enough detail that the launch can be REPRODUCED given the
same hardware, the same software versions, and the same start values and seeds. Everything below is either
MEASURED (captured from the machine on 2026-09-16 and labelled as such) or FROZEN (a value chosen before any
outcome exists). Nothing here is recalled from memory.

Companion documents:
- `SWARM_R8.md` -- the plan, rules, rulings R1-R14, gates G1-G7, adaptations ADAPT-1..15.
- `POST_ROUND_FINAL_STEPS.md` -- the close procedure and packet format.
- `prompts/2026-09-14_graphworld_swarm/24..27_*.md` -- operator directives, verbatim, sha256 in MANIFEST.

---

## 1. HARDWARE (MEASURED 2026-09-16)

| item | value |
|---|---|
| CPU | AMD Zen 4, Family 25 Model 97 Stepping 2, AuthenticAMD |
| cores | 8 physical / 16 logical |
| max clock | 4501 MHz |
| RAM | 31.6 GB |
| GPU | NVIDIA GeForce RTX 5060 Ti, 16311 MiB |
| GPU driver | 576.88 |
| compute capability | 12.0 (Blackwell) |
| OS | Windows-11-10.0.26200-SP0 |
| Redis host OS | Linux 6.6.87.2-microsoft-standard-WSL2 x86_64 |

The host is DEDICATED for the round: no other workload is scheduled. Round 7 demonstrated why this matters --
its first capacity probe was discarded because a conductor background job and a lane's pytest overlapped k=1.

## 2. SOFTWARE VERSIONS (MEASURED 2026-09-16)

| component | version |
|---|---|
| Python | 3.12.10 CPython |
| interpreter path | `C:\Users\jcrai\lab\gw-venv\Scripts\python.exe` |
| numpy | 2.5.3 |
| numba | 0.67.0 |
| llvmlite | 0.49.0 |
| redis-py | 8.1.0 |
| torch | 2.11.0+cu128 (CUDA 12.8, cuda.is_available() True) |
| scipy | 1.17.1 |
| pandas | 3.0.5 |
| psutil | 7.2.2 |
| Redis server | 8.6.3, standalone |
| Redis endpoint | `127.0.0.1:6390` db 0, `decode_responses=True` |
| wforge GRAMMAR_VERSION | `wforge-grammar-0.1` |

**NEVER `pip install` into `gw-venv`.** The environment is part of the experiment's identity; changing it
invalidates reproduction. If a package is missing, that is a finding, not a fix.

## 3. CODE STATE

| item | value |
|---|---|
| repo | `F:/Prometheus-worktrees/nestor-sidequest-graphworld` |
| branch | `nestor/sidequest-graphworld-2026-09-14` (NEVER main) |
| integration sha at launch prep | `72a417663c2a87fae20f5f844df3082bbac02890` |
| wforge location | `SerendipityFoundry/worldfoundry` -- **READ ONLY production seat, never edited** |

The gate records the exact tip sha used for the round; that sha, not this one, is the reproduction anchor if
build commits land after this document is written.

## 4. TIME AND CLOCK (FROZEN, operator prompt 25)

| allocation | duration |
|---|---|
| SCIENCE clock | 12 h, code-owned |
| setup + teardown | 2 h |
| iterative refinement | 1 h, interactive, closes before any result exists |
| END-TO-END CAP | 15 h, hard |

Clock is CAP-ANCHORED (ADAPT-2):

    SCIENCE_END_TS = min(science_start + 12 h, T0 + 15 h - teardown_reserve),  teardown_reserve = 60 min

Epochs: 12 x 3600 s. No conductor extension under any circumstance. A build or gate overrun consumes SCIENCE
time automatically; it never consumes the teardown window and never moves the cap.

## 5. SEEDS AND START VALUES (FROZEN BEFORE ANY OUTCOME)

### 5.1 Seed space already CONSUMED (measured)

    gen_seed 1..37   -- the R16 grid (37 worlds x 2 pressures {train8_held64, train128_held64})

Note on the grid's shape: the r7 packet's "74 cells" is 37 worlds x 2 pressures = 74 cells, of which 73 carry
committed r7 rows; the 74th is w13 `train128_held64`, the carried-over origin cell never re-screened in r7.
74 CELLS, not 74 worlds.

`20260916` is a PCG64 PERMUTATION seed in `R16_ORDER_R6.json`, NOT a gen_seed. Do not confuse the two.

### 5.2 Round 8 seeds (FROZEN)

| purpose | seed | notes |
|---|---|---|
| anti-prior candidate list | `20260921` | code-published before any prediction seals |
| anti-prior arm assignment | `20260922` | PCG64; arm never disclosed to experimenter lanes while live |
| screen order permutation | `20260923` | PCG64 over the frozen world manifest |
| L-band mutation op seeds | `20260924` | PCG64 stream; draws `op_seed` per descendant |
| stratum B background worlds | `gen_seed 900000 + i` | verified collision-free: no consumed gen_seed >= 1000 |

Prior-round seeds, recorded so a reproduction can distinguish rounds: r7 used 20260919 (candidates),
20260920 (arm), 20260916 (screen order); r6 used 20260916/17/18.

### 5.3 Capacity / broker start values (MEASURED r7, carried unless re-probed)

| value | setting | source |
|---|---|---|
| k* (concurrent tokens) | 2 | `NODE_CAPACITY_PROFILE_R7` |
| threads per worker | 8 | `threads_for(k) = min(THREAD_CAP=8, HOST_THREADS=16 // k)` |
| probe grid | (1, 2, 3, 4, 6, 8) | `capacity.py` GRID; 4/6/8 UNTESTED in r7 |
| gain bar | 1.15 | `capacity.py` GAIN |
| p95 latency bar | 1.5x k=1 | `capacity.py` P95_LIMIT |
| probe target / budget | 20.0 s / 840 s | TARGET_S / BUDGET_S |

Measured r7 profile: k=1 throughput 10,084.63 (p95 20.194 s); k=2 17,512.92 (p95 23.257 s) = **1.737x**;
k=3 19,218.13 (p95 31.790 s) FAILED BOTH bars (gain 1.097 < 1.15; p95 31.790 > 30.291).

**The concurrency latency rule is NOT relaxed inside the round** (operator s19). Any re-probe is a bounded
BUILD experiment with a frozen criterion.

## 6. THE L-BAND RULE (FROZEN, ruling R13)

A world is `expand(de_novo(GRAMMAR_VERSION, gen_seed))`. It is NOT a parameter vector, so perturbation happens
in GENOME space via `wforge.genome.mutate(parent, op, op_seed)`, which returns a frozen DESCENDANT. The op is
interpreted at EXPANSION time, so the descendant genome alone reproduces the world bit-for-bit. wforge is
never edited; `mutate` is a public API call.

Base: **w13** = `de_novo("wforge-grammar-0.1", 13)` -> `world_id Wf250db380cb2afd3`,
mechanism `T=32, S=1, W=1, n=32, n_regs=7, lin_ops=4, corrupt_rate=16, obs_delay=0, horizon_class=SHORT,
act_targets=[5], yield_reg=5, yield_amt=10, start_charge=191`.

| band | rule |
|---|---|
| **L1** | EXACTLY ONE op from {`PARAM_PERTURB`, `REWIRE`, `PRIMITIVE_INSERT`, `PRIMITIVE_DELETE`} -- size-preserving, single-axis |
| **L2** | exactly two such ops, OR one labelled structural op (`BUDGET_MUTATE` / `INTERFACE_MUTATE`) |
| **L3** | three such ops, or two including a labelled structural op |

`BUDGET_MUTATE` and `INTERFACE_MUTATE` are held out of L1 and always carry an explicit structural label,
because they are not equal in magnitude to the single-axis ops (measured below).

**MECHANISM-LEVEL DEDUPLICATION IS MANDATORY.** Silent mutations are real and measured: `PARAM_PERTURB`
op_seed 4 and `BUDGET_MUTATE` op_seeds 2,3,4 each produce a DIFFERENT `world_id` that expands to an IDENTICAL
mechanism. A band that trusts genome ids would screen the same world twice and count it as two data points.
Dedup on the expanded mechanism, keep the lowest op_seed representative, and record every discarded duplicate.

Measured distance-1 effects on w13 (op_seeds 1-4):

| op | effect | size |
|---|---|---|
| PARAM_PERTURB | `yield_amt` 10->9/8/13; op_seed 4 = NO CHANGE | n=32 |
| PRIMITIVE_INSERT | `lin_ops` 4->5 | n=32 |
| PRIMITIVE_DELETE | `lin_ops` 4->3 | n=32 |
| REWIRE | `act_targets` [5]->[1]/[2]/[6]/[3] | n=32 |
| BUDGET_MUTATE | `horizon` 32->64 on op_seed 1 only; 2,3,4 NO CHANGE | n=32 or 64 |
| INTERFACE_MUTATE | `corrupt_rate` 16->0 AND `obs_delay` 0->2 AND `horizon_class` SHORT->MEDIUM, identical on every op_seed | n=32 |

w13 has `corrupt_rate=16`, so `INTERFACE_MUTATE` switches corruption OFF while switching delay ON -- a trade of
one observational difficulty for another, not a clean-to-noisy step. `horizon_class` is DERIVED
(`slow = delay*8 + obs_delay*4 + regime_period`), never authored, and is not an independent axis.

## 7. STRATUM B (FROZEN)

Fresh worlds from the untouched range `gen_seed 900000 + i`, drawn by code, frozen with their world_ids before
any screening. Purpose: estimate background survivorship rarity against which local enrichment near w13 is
judged. No outcome-dependent expansion this round. No hand-designed worlds this round.

## 8. SIZING (ruling R11 -- MEASURE-THEN-SIZE, not a fixed N)

Screening cost is NOT predictable from world parameters. Measured across 30 worlds with committed cost and
gate features: `n_gates` r = **-0.168** (negatively correlated), T 0.255, cells -0.305, qd_wall_s 0.095,
screen_k constant. Per-unit cost spans ~500x INVERSELY to search size (w16: 9,766 CPU-s per 1k gates over
1,092 gates; w31: 63 over 86,870). Median 612 CPU-s per 1k gates, mean 2,672, range 19-9,766.

Therefore: freeze L1, screen it, MEASURE actual cost, then let CODE size the remainder against remaining
clock. A fixed N quoted in advance would be a guess wearing arithmetic.

Round capacity for reference: 12 h x 7.25 sustained threads (r7 realized) = **313,200 CPU-s**;
at a perfect 16 threads, 691,200.

## 9. LAUNCH SEQUENCE

Preconditions, each verified not assumed:

1. Round 7 is closed: `pm:epoch:state` phase `closed`, `pm:round:current` unset, 0 registrations, 0 stop flags.
2. Prior-round residue cleared: `residue clear --prior-round r7` (expected: 6 DEAD_CONSUMER, pending 0).
3. Conductor worktree fast-forwarded; `git status --porcelain` empty.
4. No worker processes alive (verified by pid scan, excluding the scanner's own ancestor chain).

Then, in order:

5. **BUILD** (<= 60 min) in gate order **G1, G6, G5, G7, G2, G3, G4**, then conditionals C1/C2/C3.
6. **GATE** (<= 20 min): full suite; discovered build tests; planted EVIDENCE_N_v1 refusals
   (16/1/16, 32/4/(16,8,4,4), 32/4/(29,1,1,1)) must be refused at admission with ZERO rows; vocabulary lint;
   protocol lint; live residue scan clean; capacity profile present; the gate records the tip sha.
7. **REFINE** (<= 60 min, interactive) -- instruments, logistics and sizing only. CLOSES before any result.
8. **CLOCK START**: round clock `r8`, 12 x 3600 s epochs, cap-anchored end_ts, stage PRODUCTION, lanes
   B,C,D,E,G (+H,R as non-job lanes). Controller owns every boundary; the conductor pushes nothing.
9. **CLOSE**: code-owned. Then `POST_ROUND_FINAL_STEPS.md`.

Gate -> blocked-work map is enforced at ADMISSION with refusal reason `GATE_NOT_LANDED:<id>`, so an
over-subscribed build degrades by machine refusal at zero CPU rather than by conductor judgement.

## 10. WHAT REPRODUCTION REQUIRES (the archival contract, prompt 26)

A future analyst reproducing this launch needs, all of which the round must commit:

- this file, `SWARM_R8.md`, and the four operator prompts with their sha256 in MANIFEST;
- the gate's tip sha and the transitive import-closure fingerprint of every job fn;
- the frozen world manifest: every `world_id`, its genome (grammar_version, generation_seed,
  mutation_history), and its expanded mechanism;
- seed manifests and RNG family assignments per run;
- genome bytes for every candidate and control arm;
- per-generation trajectories, not only endpoints;
- raw oracle outputs;
- the env fingerprint in sections 1-3;
- predicate refs (`refs/pm/pred/<id>`) pinned BEFORE each run;
- captured payloads of ABORTED runs;
- the job done stream and all telemetry streams, exported per epoch to committed rows (gate G7).

Retention is APPEND-ONLY. Nothing is rotated, trimmed or deleted. The bus is NOT an archive: it is capped at
`maxlen=100_000, approximate=True` and ages out.

## 11. KNOWN LIMITS OF THIS REPRODUCTION

Stated so a future analyst is not misled about what "same" means:

- **Single host.** There is no second machine, so instrumentation displacement (ruling R8) cannot include host
  displacement. A replication reproduced here shares this host's failure modes.
- **k=4, 6, 8 never tested.** `k*=2` is optimal only among {1,2,3}; the r7 probe budget expired.
- **Whether the numba kernel scales past 8 threads is unknown** -- `THREAD_CAP=8` prevents a 1x16 worker.
- **GPU evolution was measured and rejected** (inexact: 6 fitness + 3 cells mismatched in 819,200 evaluations;
  ~7x slower). The exactness failure is UNEXPLAINED and is not reproduced-away by re-running.
- **w13 itself was never screened in r7**, so there is no measured screening cost for the world stratum L
  perturbs around.
- Timing figures (throughput, p95, CPU-s) are machine- and thermal-dependent and will not reproduce exactly;
  VERDICTS and world identities will, because they are seeded and code-derived.
