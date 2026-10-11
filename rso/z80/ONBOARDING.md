# Z80 Atlas onboarding record (C-017-T030; directive s8)

Argus[harry1-6668fa07], claude-opus-5-5 (Q2), harry1, 2026-10-11. Engineering measurements for the third native runtime, set
beside C-010 (Ares) and C-016 (Ensorain, rso/ensorain/ONBOARDING.md s6) without normalising away the difference in difficulty.

## 1. Bespoke adapter lines

| File | Physical | Code (tokenizer; no comments, docstrings, blanks) | What it is |
|---|---|---|---|
| subjects.py | 93 | 54 | starters (H, NH, RECON; HOST / PARASITE for units), ten arms, seed partitions + conflict check |
| observe.py | 166 | 125 | engine.run's population loop re-implemented for the subset; per-byte writer tags; counterfactual; situ; founder source |
| assay.py | 245 | 178 | record -> replay -> refuse / label / class / origin; five forgeries; two baselines; rows; CLI |
| analysis.py | 107 | 75 | Q1-Q4, exact w_max, verdict, confusion |
| freeze.py | 56 | 39 | explicit-list LF-sha256 manifest + Python major.minor |
| **adapter total** | **667** | **471** | Ensorain 662 / 480; aspiration ~500; no control dropped |
| tests/test_attribution.py | 348 | | 42 unittest cases |
| dev/dev_check.py, red/run_red.py, red/make_edits.py | 150 | | development check and RED tooling |

About 125 of the 471 code lines (observe.py) exist only because `engine.run` keeps the population in locals and no birth is
observable from outside (rso/z80/CONTRACT.md s3). An engine that exposed a per-birth hook would need none of them.

## 2. Shared components (rso/registry)

| Entry | Use here | Reused / modified / too narrow |
|---|---|---|
| receipt-canonical (rso/slice001/receipt.py sha256_hex) | rows digest; every row field an int or a string | REUSED unmodified. No float needed: counts, classes and seeds only |
| ruler-binary-retention (rso/witness/ruler.py tail_le) | the exact binomial tail behind w_max | REUSED unmodified, OUTSIDE its named scope: the bound is an error rate (1/5), not a chance rate, and the unit is a run. Second engine to use it as a generic exact-binomial ruler on independent units (C-016 used 9/10); the entry's scope text should say so |
| registry file_sha (rso/registry/registry.py:27) | FROZEN.json | REUSED |
| mutation-runner | pattern only | run_red.py is the unittest variant C-016 introduced (in place, `-B`, caches purged, byte-restore checked) |
| exec-binding, custody-keeper, budget-ledger | not used | one run = one record = one row; no parent/child run tree; cost is minutes of CPU |
| stratified-holm-analysis | not used | one intersection-union test, no family to correct |
| witness-driver-ares | pattern only | recompute-from-bytes, controls as their own arms, refusal before launch on a hash mismatch |
| C-017-T020 demand gate (rso/z80/demand) | the carrier world and its F probe | REUSED as the negative-control detector b2 (its D reading, extended by "writes a functional copy") |

Modified shared components: **none**. No file outside rso/z80/ and roles/Argus/ was edited. Requests to Archaeon: **0**.

## 3. Native semantic mismatches (assumptions the Observatory carried that Z80 Atlas broke)

1. **"Who wrote it" is a property of the bytes.** It is not. A child the runner copied from a copier is byte-identical to one the
   copier wrote itself. The bytes-only reading (T020's D endpoint) calls runner-written copiers endogenous in 7/8 dev runs of
   H_EXT_SHORT. The writer is a fact of the execution path, so the trust root moved from the stored record to a replay of
   (spec, seed). An engine without byte-exact replay cannot be attributed this way.
2. **"The engine's provenance counters mean what they say."** `reads_nbr` / `exec_foreign` (the inputs of `donor_contributes`)
   also fire when a parent runs into its own freshly written copy. Read as "the environment contributed", they mislabelled
   4/21 ENDO dev runs. Environment contribution is now decided per byte by counterfactual re-execution.
3. **"A constructed arm keeps its mechanism."** Over evolutionary time it does not. Reconstructors convert to genuine endogenous
   transmission under task reward (3/12 runs by epoch 100); planted heritable lineages are partly replaced by reproducers that
   copy only by executing the target cell's code (2/16 at 200 epochs). Ground truth by construction is horizon-bounded; the
   horizons are part of the preregistration. This is the strongest reason the instrument is needed at all: the mechanism class
   of an evolved population cannot be read off its starting conditions.
4. **"Origin is in the founder bytes."** A random founder that already echoes is byte-identical to a planted one (1 dev run). Origin
   is the founder's SOURCE PATH (transplant / seeded vs random_tape), observed in the replay.
5. **"A few correct cases mean competence."** Three cases admit luck (a half-solver passes 1 in 8); the probe bar is 8 cases, the
   same with and without the neighbour.
6. **"The unit is the organism."** Organisms share ancestry; the unit is the run (T020, kept).
7. **"Environmental dependence can be grown as a population."** A parasite / host population does not persist (hosts are one
   mutation from self-function; parasites cannot reproduce under ENDOGENOUS_COPY). Only kept-byte reconstruction was grown;
   neighbour-dependent function is covered by unit known answers.
8. **"A frozen manifest can walk the directory."** It must not (C-016-T042 O2): freeze.py pins an explicit list, so a
   challenger's new files under rso/z80/ neither break nor join the freeze.

## 4. Time, CPU, memory, interventions

| Measurement | Value |
|---|---|
| Session start (boot, harry1) | 2026-10-11 15:12Z |
| Claim pushed | 15:14:12Z (12d0a04b4) |
| Time to first native execution | ~15:13Z, before the claim: the T021 smoke re-run, byte-identical to the committed result; first engine runs of the new constructions 15:2xZ |
| RED observed | 15:32:55Z (37bec7820) |
| First adapter-driven classification of native runs | ~15:36Z (one dev seed per arm) |
| Development check (final code) | 16:53-17:07Z; rows sha256 6e04917a; RED rows 17:15-17:21Z, 27/27 |
| Preregistration committed | 17:15:20Z (0c7afbeea) |
| Frozen | see FREEZE.md |
| Time to qualified result | not reached in this packet (Q3 challenge, then the confirmatory run) |
| CPU, whole packet | about 2.5 core-h, every run on dev seeds, <= 2 processes (three dev-check generations as the design changed, horizon probes, three RED runs) |
| Memory | ~6 MB traced Python allocation peak for one 200-epoch record + replay + both detectors (tracemalloc) |
| Operator interventions | 0 |
| Q3 reviewer time | to be recorded by the challenge packet |

## 5. Registry rows to add when the coordinator integrates (rso/registry is Palamedes's)

- `users` += "Z80 Atlas C-017 (rso/z80/)" on receipt-canonical, ruler-binary-retention (tail_le only) and registry file_sha.
- ruler-binary-retention `qualified_scope`: exact binomial tails on independent units against an ERROR-RATE bound (1/5), second
  non-retention use.
- Candidate entry `z80-replay-writer-attribution` (rso/z80/observe.py + assay.py), stage AUTHOR_TESTED. Scope: Z80 Atlas
  archaeon tree at 863d34a55, the PREREGISTRATION s2 subset, records replayable from (spec, seed). Not for: records without
  replay (s3.1); other topologies, physics, pressures or tasks (refused as UNSUPPORTED); horizons beyond those of PREREGISTRATION
  s3 (ground truth not checked there); neighbour-dependent function at population scale.
- Counterexample for any provenance-reading component: the engine's `reads_nbr` / `exec_foreign` are not environment contribution
  (s3.2).

## 6. The repair round (v1.1.0, C-017-T041; Argus[harry1-0d3b5331], claude-opus-5-5, headless on harry1)

| Measurement | Value |
|---|---|
| Boot / worktree from fe5d0d2d1 | ~19:20Z |
| Claim pushed | 19:22:29Z (7f017865d) |
| Repair + tests + RED + dev re-check committed | 19:55:29Z (16e249bdc) |
| PREREGISTRATION v1.1.0 committed | 19:58:33Z (7ad0131b7) |
| Re-frozen | see FREEZE.md v1.1.0 |
| Adapter lines after the repair (physical / code) | subjects 108 / 60, observe 170 / 125, assay 265 / 192, analysis 108 / 76, freeze 56 / 39: **707 / 492** (v1.0.0 667 / 471; +21 code lines: CDIST, b4, the reads rule, BASELINES, seeds for arm index >= 10) |
| Tests / RED mutants | 42 -> 51 / 27 -> 36 (E1 E2 E3 E5 verbatim from challenge/edits.json) |
| CPU | ~0.6 core-h (RED 2 x ~250 s, dev rows 2 x ~350 s, dev power 2 x ~500 s, unit and arm probes), <= 2 processes, dev seeds only |
| Operator interventions / requests to Archaeon | 0 / 0 |

Lessons (for the registry and the next engine):
1. **An invariance probe tests a GROUP, not a dependence.** Two alterations of the pre-window generate x -> +-x + c; anything
   invariant under that group passes, however target-dependent. A counterfactual-by-alteration needs either a direct witness of
   the access path (here: the VM's read counter) or a sample that is not a group element. ONBOARDING s3.2 still holds for
   exec_foreign (it fires on a parent's own fresh copy); for reads the counter is now used as a SUFFICIENT condition for K,
   accepting that a read of the parent's own fresh write is over-counted (dev: 91 of 98 reader births in one run).
2. **A baseline that cannot emit the answer is not a control.** b1 / b2 had no ENV output, so their Q4 failure on ENV was
   guaranteed. A registered baseline should be able to be right on every class; b4 is, and fails only where the recipe lies.
3. **A recipe TABLE built from the registered arms is the answer key.** The informative recipe reader is mechanistic; its failure
   needs an arm whose construction reads one way and works another (CDIST).
4. **Unpinned registered sentences survive** (E1 E2 E3 E5 each passed 42/42). A sentence in the preregistration that names a
   behaviour needs a test that a mutant of that behaviour turns RED; loading the challenger's mutants verbatim makes that cheap.
5. **Seed slots are a namespace, not a counter:** base + 1000 * arm index overflowed into the next partition at the eleventh arm.
