# E3 RUNNER: MINIMAL TFS-1, LIFETIME ORGANISM, 2x2 PROMOTION x ARCHIVE + CONTROLS

Author: the SUBSTRATE lead, C-015 W02. Implements `windows/E3_DESIGN_DRAFT.md`, which is **not frozen**. Code lives in
`roles/Aphrodite/beta04/tfs1/e3/`.

- **Data and labels.** Every number below comes from the **EXPOSED pilot_v2 worlds**. It is development data, not a
  screen. No statistic is claimed.
- **What was read and reused.**
  - Foundry OUTPUT files only: the manifests, the arm view, the evaluator files and WORLD_SEALED.json. No foundry code
    was read.
  - Atlas machinery is reused through `atlas.arms.Search`, `atlas.common`, and `atlas.sample.sample_uniform`.

## 1. Files and commands

All commands run from `roles/Aphrodite/beta04/` with `OMP_NUM_THREADS=1`, one process each.

| File | Role |
|---|---|
| `worlds.py` | Arm-view loader (`ArmWorld`: sha-verified, reads only `arm_view/`); coordinator-side `presentation_order`, `Evaluator`, `sealed`; `judge` (test + tribunal, value-or-FAIL); `AccessLog` (records every open during a lifetime) |
| `e3_known_positive.py` | s1 TFS1_INSTRUMENT_QUALIFIED procedure. Stage-cached in `runs/KP_<world>.json` |
| `organism.py` | s2 lifetime organism: arms P0A0 / P1A0 / P0A1 / P1A1 / RANDOM-LIBRARY / SHUFFLED-HISTORY / RANDOM-ARCHIVE |
| `resumable.py` | Checkpointed lifetimes. A production lifetime exceeds the 15 CPU-min single-run cap. Resuming is identical to an uninterrupted run (tested) |
| `final_eval.py` | s3 autonomous evaluation + cognitive ledger + endpoint |
| `dependency.py` | s4 removal + sham re-runs (with a REPLAY sanity re-run) |
| `smoke.py`, `summarize_smoke.py` | Development smoke runner + summary / cost model (`runs/SMOKE_SUMMARY.json`) |
| `tests/run_tests.py` | E3 tests (`E3_TEST_RESULTS.json`) |

```
python -m tfs1.e3.e3_known_positive --root foundry/<set> --world W --stage r1|chain|scratch|all [--mech m|--family F]
python -m tfs1.e3.e3_known_positive --root foundry/<set> --world W --verdict
python -m tfs1.e3.resumable --root foundry/<set> --world W --arm ARM --seed S --B 200000 --ckpt runs/L_<W>_<ARM>_s<S>.json --max-cpu 780
    (repeat until it prints DONE; then)  final_eval.evaluate_lifetime(rec, root, W);  dependency.dependency_tests(rec, fe, root, W)
python -m tfs1.e3.smoke --world W --arm ARM --seed 0 --B 20000      (non-resumable; small B only)
python -m tfs1.e3.tests.run_tests
```

## 2. What is implemented (deviations from the draft are flagged)

### s1 Known-positive chain (`e3_known_positive.py`)

**Admitted families.** These are the R3 / R4 families with status `ADMITTED` in the WORLD_MANIFEST id_map.

**Constituents.** Taken from WORLD_SEALED `mechanisms_used`.

**(i) R1 search per constituent mechanism.**
- Runs on the mechanism's R1 families: sealed R1 families with `mechanisms_used == [m]`, in index order.
- Search: TFS-1 base keyed enumeration, budget 1e6, seed 0, slot = family_id, max_size 12.
- The FIRST dev-consistent program is then judged on test + tribunal, with no hindsight.
- The next R1 family is tried only if this one gives no promotable mechanism.

**(ii) Promotion of the mechanism.** The promoted mechanism is the first closed lambda of the kind's type in the FOUND
program:
- f: Int->Int; p: Int->Bool; s: Int->Int->Int;
- the body must reference a parameter and must not reference xs (contract v0.1-1).

**FLAG KP1.** If the found program has no such lambda, a **readout fallback** abstracts a single (possibly repeated)
readout `(op xs)`, op in len/head/last/sum/max/min, into the parameter. I re-implemented this from the foundry QCONFIG
text ("f/p fallback: abstract a single repeated readout s(xs)"); the draft does not mention it.
- It mattered on W1d5301d0 f1: the first dev-consistent program was `(div (add 1 (last xs)) 3)`.
- The extracted lambda agrees with the sealed mechanism on probes: agreement 1.0 for every acquired mechanism.

**(iii) Chain search.** TFS-1 enumeration on the R3 / R4 family, with the library = {promoted mechanisms of its
constituents}, at 1e6. The first dev-consistent program is then judged on test + tribunal.
- **FLAG KP2.** The foundry's chain_d used ALL acquired primitives of the world. Here the library is the constituents
  only, as the draft says.

**(iv) Scratch control.** Base enumeration at 1e6 on the same family.

**Static diagnostic.** For each family, the sealed witness refactored with the promoted entries, its promoted-form size,
and the hitting-cost bracket of that size class.

**Verdict per world.** YES iff chain success is ≥ 80% AND scratch solves none.

### s2 Lifetime organism (`organism.py`)

**Information boundary.**
- A lifetime is given an `ArmWorld` (opaque id + dev only; the output type is inferred from the dev outputs) and a
  presentation order. The order is a list of opaque ids, extracted on the coordinator side BEFORE the lifetime.
- **No evaluator-side file is opened during a lifetime.** `AccessLog` proves this (tested).
- No certifier is consulted during a lifetime.

**Search per family.**
- `atlas` arm **A-FRESH** (restart hill-climbing), subclassed (`LifetimeSearch`) to:
  - stop at the FIRST dev-consistent program;
  - track restore origins and the top-k partial-credit programs.
- The start pool is evaluated once (1 charge each). Then come bursts of R mutation steps (neutral chain on exact dev
  credit), and each burst restores a parent drawn uniformly from the start pool.
- Budget B charges per family, matched across arms.
- **CRN:** the mutation stream is `rng_for(seed, "<arm_world>/<opaque>")`, identical in every arm.

**Start pool.** The generic starts of the type, plus (archive arms) the archive programs of that type in insertion
order. These are refactored modulo the current library when promotion is on, and limited to size ≤ 16.
- **FLAG D-ARCH1.** The draft says "restarts draw parents from the archive". Here the generic starts STAY in the pool,
  so archive-off is the pool restricted to generic starts.
- Archive programs are charged once per family when evaluated as starts. That is included in B.

**PROMOTION, after each solved family.**
- **Candidates** are of two kinds:
  - (a) closed lambda subterms of the solved program (expanded): no free variable, no xs (v0.1-1), body references a
    parameter, body size ≥ 2;
  - (b) the TFS-1 compressor's proposals over ALL solved programs so far, excluding any that reference xs.
- **Uses** = the number of solved programs containing the candidate.
- **Selection** = the top **K = 8** by (-uses, -body size, text).
- **Rebuild.**
  - The library is REBUILT deterministically after each solved family, in (size, text) order.
  - Each body is refactored modulo the entries already promoted, so a composition of earlier entries becomes depth 2.
    The known-answer test gets `(if (L_gt h0) (L_pow h0) h0)` at depth 2.
  - **FLAG D-PROM1.** Because the library is rebuilt each time, the top-K can change. Entries can leave, and that is
    why programs and archive entries are stored EXPANDED.

**ARCHIVE.** After each family it adds the solved program plus the top-**k = 3** partial-credit programs of that
family's search. These are ranked by exact dev credit, then partial credit; not all-FAIL; partial > 0; ties broken by
size, then text. The archive is target-blind.
- **FLAG D-ARCH2.** Descriptor-guided selection is not used, because no descriptor has qualified on these task classes.
  Selection is uniform (X1).

**Controls.**

| Control | Definition |
|---|---|
| RANDOM-LIBRARY | Each selected candidate is replaced by a uniform random closed body of the same Int-parameter count, result type and size (keyed per candidate, so stable). Non-Int-parameter candidates are matched on arity only, and the mismatch is recorded |
| SHUFFLED-HISTORY | Promotion on, order `SHUFFLED_ANTI_<1 + seed % 3>` |
| RANDOM-ARCHIVE | Every program the archive rule adds is replaced by a uniform random base program of the same type and size |

**Ledger**, per family and per lifetime:
- search charges; both unit ledgers; restores, and restores from the archive;
- start evaluations; rejected mutations;
- archive admissions;
- promotion: compressor calls, anti-unification pairs and CPU; rebuilds; promotion attempts; new entries.

### s3 Final evaluation (`final_eval.py`)

- Each dev-consistent lifetime program is judged ALONE on test + tribunal, with the library it was found with.
- **Endpoint:** admitted R3/R4 qualified, R2 qualified, total qualified, per-rung counts, and spurious dev-consistent
  programs.
- **Cognitive ledger:** ORGANISM / DEVELOPMENTAL (calls a primitive) / SEARCH_INFRA (burst restored from an archive
  program, or archive-delivered) / CERTIFIER (verdict only; 0 consultations during the lifetime), plus a primary-source
  label.

### s4 Dependency (`dependency.py`)

For each qualified admitted R3/R4 solution that calls an entry e, three re-runs:
- **REPLAY:** must reproduce the recorded hit;
- **REMOVED:** e and its dependents removed; archive starts are expanded and re-refactored;
- **SHAM:** a matched random entry replaces e.

SUPPORTED iff REPLAY qualifies and both REMOVED and SHAM fail. Supported depth = the max depth over the supported
entries.

## 3. Tests (`E3_TEST_RESULTS.json`): 10 PASS / 0 FAIL

The base TFS-1 suite still gives 15/15 after the v0.1-1 library flag was added.

| Test | Result |
|---|---|
| determinism_in_process_and_fresh_process | P1A1, 14 families, B 1,500: identical record in process; identical decision hash in a fresh `python -I` process; seed 1 differs |
| **arm_view_only_access_log** | 13 paths opened during a P1A1 lifetime, **all under `arm_view/`**, 0 evaluator / WORLD_* files. Positive control: an evaluator read is caught |
| **budget_matching_and_crn** | 7 arms x 8 families at B 1,000: every family charges ≤ B; every unsolved family charges exactly B; the first family (no history) is identical across all CURRICULUM arms |
| **no_target_leakage_perturbed_evaluator** | Test outputs, tribunal outputs and witnesses perturbed for every family: lifetime decisions, library and archive are **identical**. Final evaluation changes (2 qualified to 0), so the perturbation was effective |
| lifetime_library_semantics_and_v01_1 | On a PLANTED synthetic arm-view world (instrument test): 2 library snapshots, every one reloads byte-identically, no entry references xs, promoted programs evaluate == their expansion (20 checks) |
| checkpoint_resume_identical | P1A1, RANDOM-LIBRARY, RANDOM-ARCHIVE resumed after every family (7 processes' worth of checkpoints): decisions, library and archive identical to an uninterrupted lifetime |
| developmental_known_answer_depth2 | A planted corpus gives `(pow h0 3)` and `(gt h0 4)` at depth 1, and `(if (L_gt h0) (L_pow h0) h0)` at **depth 2**. The random library matches count and result types and never composes |
| random_archive_matched | Archive rule counts hold; every random-archive entry is random; counts are matched per family on its own run |
| dependency_machinery | Removing an entry removes its dependents; the sham has the same params / ret and depth 1 |
| known_positive_extraction_and_judge | Readout fallback, closed-lambda extraction, fold-step extraction; an expected `"FAIL"` requires a FAIL |

## 4. Known-positive results (EXPOSED pilot_v2; `runs/KP_<world>.json`)

**R1 acquisition, base enumeration at 1e6, first dev-consistent program:**

| World | Mechanism | R1 family : charge, CPU | Found | Extracted (agreement with sealed) |
|---|---|---|---|---|
| W1d5301d0 | f1 | F006 : 49,862, 1.0 s | `(div (add 1 (last xs)) 3)` | readout fallback `(lam x (div (add 1 x) 3))` (1.0) |
| W1d5301d0 | p0 | F008 : 27,841, 1.4 s | `(filter (lam x (lt x (add 2 3))) xs)` | closed lambda (1.0) |
| W1d5301d0 | s0 | F010 : not found at 1e6 (62 s); F012 : 286,293, 17 s | `(scanl (lam a (lam b (sub b (div a 3)))) 1 xs)` | closed lambda (1.0) |
| W0467897d | f1 | F006 : not found (68 s); F007 : 763,421, 56 s | `(max (map (lam x (pow (gcd x x) 3)) xs))` | closed lambda (1.0) |
| W0467897d | **p0** | F008 : **not found at 1e6** (58 s); F010 : 346 | `(filter (lam x (lt 3 x)) xs)`: **dev-consistent, fails test** (x > 3 vs the sealed x > 4) | **NOT ACQUIRED** |

**Chain (iii) and scratch (iv) at 1e6:**

| Family | Chain | Charge | Program | Scratch |
|---|---|---|---|---|
| W1d5301d0-F027-R3 | SOLVED | 650,459 | `(foldl (lam a (lam b (L_s0 a (L_f1 b)))) 0 xs)` | not found |
| W1d5301d0-F035-R3 | SOLVED | 410,735 | `(L_f1 (foldl (lam a (lam b (L_s0 a b))) 0 xs))` | not found |
| W1d5301d0-F071-R4 | SOLVED | 64,561 | `(filter (lam x (L_p0 x)) (map (lam x (L_f1 x)) xs))` | not found |
| W1d5301d0-F077-R4 | **NOT FOUND at 1e6** | | witness refactored is promoted size **8**, bracket [124,979, 1,365,260] | not found |
| W0467897d-F061 / F081 / F085-R3 | **CHAIN_C_FAIL** (p0 not acquired) | | | not found (all three) |

**Verdicts:**
- **W1d5301d0:** 3/4 = 75%, so **NO**: just under the 80% rule, and scratch fails every family.
- **W0467897d:** 0/3, so **NO**.
- **Pooled pilot:** 3/7.

On this exposed data, TFS-1 does **not** reproduce the foundry's chain at 1e6. There are two causes:
- **A spurious first dev-consistent program in R1 (W0467897d p0).** That world's R1 dev set does not separate x > 3
  from x > 4. The foundry's own R1 search found `F008` instead.
- **The TFS-1 horizon.** There is no observational-equivalence pruning, so the size-8 classes with a 2-entry library
  are about 1.2M.

This is a **pilot instrument reading, not the E3 verdict**: the verdict is taken on the production set. If production
looks the same, the directive's label applies: `TFS1_REACHABILITY_INSTRUMENT = FAIL`.

## 5. Development smoke (EXPOSED pilot_v2; `runs/SMOKE_*.json`, `runs/SMOKE_SUMMARY.json`)

**Setup.** All 7 arms on W1d5301d0 (50 families) and W0467897d (49 families), seed 0, **B = 20,000**, R = 100,
K = 8, k = 3, CURRICULUM order (SHUFFLED_ANTI_1 for SHUFFLED-HISTORY). One process per lifetime; each lifetime took
145-232 CPU-s.

| World | Arm | Solved in lifetime | Qualified | Admitted R3R4 | Admitted R2 | Library | Archive | Hits from archive origin |
|---|---|---|---|---|---|---|---|---|
| W1d5301d0 | P0A0 / P1A0 / RANDOM-LIBRARY / SHUFFLED-HISTORY | 5 | 4 | 0/4 | 0/3 | 0 | 0 | 0 |
| W1d5301d0 | P0A1 / P1A1 | 5 | 5 | 0/4 | 0/3 | 0 | 150 | 2 |
| W1d5301d0 | RANDOM-ARCHIVE | 4 | 4 | 0/4 | 0/3 | 0 | 146 | 1 |
| W0467897d | P0A0 / P1A0 / RANDOM-LIBRARY / SHUFFLED-HISTORY | 6 | 6 | 0/3 | 0/3 | 0 | 0 | 0 |
| W0467897d | P0A1 / P1A1 | 6 | 6 | 0/3 | 0/3 | 0 | 143 | 2 |
| W0467897d | RANDOM-ARCHIVE | 7 | 6 | 0/3 | 0/3 | 0 | 143 | 7 |

Solve rates pooled over all 14 lifetimes, by rung:

| Rung | Solved |
|---|---|
| R0 | 0.75 |
| R1 | 0.06 |
| R2 | 0 |
| R3 | 0 |
| R4 | 0.09 (dev-consistent only) |
| R5 | 0 |

**Reading (development only).**
- At B = 2e4 **no library ever forms**: the few solved programs are lambda-free readouts such as `(sum (drop 3 xs))`,
  and the compressor needs at least 2 uses.
- So the promotion arms equal their no-promotion twins, and the 2x2 is uninformative at this budget.
- No dependency test was triggered (no qualified R3/R4).

**B = 2e5 PROBE (P1A1, W1d5301d0).** Resumable, 2 x 700 CPU-s chunks; stopped at 42/50 families to stay within the
compute cap. File: `runs/PROBE_W1d5301d0_P1A1_s0_B200000.json`.
- 9/42 solved; 7 qualified (R0 x 4, R1 x 3).
- A library formed: 5 entries, one at **depth 2**: `(L_div3 (neg h0) (add h1 1))` over `(div (add h0 h1) 3)`.
- **Drift junk is promoted.** Two entries are the constant-1 bloat `(pow 1 (add h0 ...))`, picked up from
  neutral-drift genotypes.
- One admitted R3 (F035) ended with a dev-consistent program found via the archive. It **fails test + tribunal**
  (spurious).
- One R1 solution called a (junk) library entry and qualified.
- Unsolved families cost a mean of **42.8 CPU-s at 2e5** (rate ≈ 4,670 charges/CPU-s).

## 6. Cost model (for budgeting the production screen)

**Rate.**
- Lifetime search: **about 5,000 charges per CPU-s** (median over the 14 smoke lifetimes, 3,900-6,000); 4,670 at
  B = 2e5. A charge = one candidate evaluated on 12 dev examples, plus mutation, compile and credit.
- Final evaluation: negligible.
- Promotion (compressor + rebuild): < 1% of CPU in the probe.

**Per family:** an unsolved family costs B / 5,000 CPU-s (40 s at 2e5); solved families cost less. Most R2-R5 families
are unsolved at 2e5 (probe), so a lifetime is close to the upper bound.

| B per family | One lifetime (about 50 families), upper bound | Screen 8 worlds x 7 arms x 1 seed |
|---|---|---|
| 2e4 | 0.055 core-h (measured 0.04-0.06) | 3.1 core-h |
| 5e4 | 0.14 | 7.7 |
| 1e5 | 0.27 | 15.4 |
| **2e5** | **0.55 (probe: 0.40 for 42 families)** | **30.8 core-h** |

**Further costs:**
- **Dependency re-runs:** 3 x B per (qualified R3/R4 solution, called entry), about 2 CPU-min each at 2e5.
- **E3 s1 known-positive:** about 15-30 CPU-min per world (r1 + chain + scratch at 1e6; a single 1e6 base enumeration
  is 50-75 s; a library enumeration is 25-50 s).
- **Process cap:** a 2e5 lifetime is about 33 CPU-min, so it MUST use `resumable.py` (780 s chunks; 3 invocations).
- **"8 seeds per cell"** in the draft means 8 worlds; a second seed per world doubles the cost.

## 7. Open decisions

| # | Decision | Current choice | Why it matters |
|---|---|---|---|
| **B** | Search budget per family | Draft 2e5; smoke 2e4 | At 2e4 nothing promotable is ever solved (no library forms; the 2x2 collapses). At 2e5 a library forms on R0/R1. Screen ≈ 31 core-h at 2e5 vs 15 at 1e5 |
| **K** | Library cap | 8, top-K rebuilt every solved family | With rebuild, entries can be displaced. A fixed "no eviction" cap would freeze early (R0) junk in |
| **R** | Restart interval (burst length) | 100 steps | Untuned. A-FRESH with R = 100 solves R0 well and R2+ almost never; longer chains or a different R changes reachability for all arms equally |
| **k** | Archive partial-credit programs per family | 3 (+ the solved program) | The archive grows by about 150 entries per lifetime; these are charged as starts each family (≤ about 50 per family per type) |
| E3-1 | Drift bloat in promotion | Not filtered | The probe promoted constant-1 junk (`pow 1 ...`). Options: (a) simplify solved programs before consolidation (shortest dev-equivalent sub-program); (b) reject candidates that are constant on probe inputs; (c) leave as is (honest machinery). Must be frozen before the screen |
| E3-2 | Readout fallback in s1 (KP1) | ON (mirrors the foundry QCONFIG text) | Without it, W1d5301d0 f1 is not acquired (its first dev-consistent program has no lambda) |
| E3-3 | s1 chain library | Constituents only (KP2) | The foundry used all acquired primitives; constituents-only is easier to enumerate |
| E3-4 | s1 first-dev-consistent rule on R1 | No hindsight (rule 2) | It produced the spurious `x > 3` on W0467897d p0, which kills that whole world's chain |
| E3-5 | Generic starts kept in the archive arms' pool (D-ARCH1) | Kept | A pure-archive pool changes the A1 factor to a different operator |
| E3-6 | Arity-2 lambda candidates with an unused parameter | Allowed (e.g. `(neg h1)`) | They are never recognised by refactoring (fixed: compress.rewrite no longer crashes on them); consider requiring all params referenced |
| E3-7 | `(map (lam x (L x)) h0)`-style compressor entries count as depth 2 | Counted by the DAG | They are lifted re-expressions; only the s4 ablation can support a depth claim |
| E3-8 | Seeds | 1 per world-cell in the cost model | 8 worlds x 1 seed is what "8 per cell" buys at about 31 core-h |
