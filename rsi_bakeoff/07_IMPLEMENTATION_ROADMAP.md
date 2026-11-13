# 07 -- Implementation roadmap

Three stages. Each ends in a go / no-go decision that can stop the line. Nothing below has been built; commands
for new code are proposed commands. Commands marked "exists" were run or read at the reference commit.

Estimates are mine. They are derived from committed throughput measurements where possible, and they are
estimates of a system that does not exist yet.

## 0. Ground rules for the build

| Rule | Reason |
|---|---|
| New code goes in a new top-level package `mathesis/` and a separate `mathesis_eval/`. No existing file is edited | TFS-1, the foundry and the RSO kits are frozen apparatus with receipts. Editing them would break their evidence |
| TFS-1 is a pinned dependency. At start-up, compare `tfs1.membrane.code_hashes()` against a recorded table and refuse to run on a mismatch | The engine's meaning depends on the interpreter's exact semantics |
| Import TFS-1 by adding `roles/Aphrodite/beta04` to `sys.path`. Never add `.../beta04/tfs1` itself, and never start Python inside it | `tfs1/enum.py` shadows the standard library's `enum` module from inside that directory. I hit this during the audit |
| Tests first, each increment its own commit | House practice (the RSO packets commit a failing test before the code) |
| `OMP_NUM_THREADS=1`, Python 3.12, standard library only | TFS-1's measurements were taken this way; no dependency to install on fleet nodes |
| One unified work meter from the first line of code | Retrofitting cost accounting is how Beta-04 ended with an uncharged ledger |
| Every experiment freezes its arms, thresholds and world seeds in a committed file before its first outcome | Standing rule of the program |

## 1. Exact source integrations

| Existing file (reference commit) | Used for | How |
|---|---|---|
| `roles/Aphrodite/beta04/tfs1/core.py` | Interpreter, type checker, term utilities, unit ledgers | import |
| `roles/Aphrodite/beta04/tfs1/enum.py` | `Enumerator` (subclassed), `oe_signature`, `oe_pruned_log`, `canon_comm`, `order_key`, `make_verifier` | import, subclass |
| `roles/Aphrodite/beta04/tfs1/library.py` | `Library.promote_body`, serialisation with re-derivation on load | import |
| `roles/Aphrodite/beta04/tfs1/compress.py` | `propose`, `refactor`, `antiunify`, `match`, `rewrite` | import |
| `roles/Aphrodite/beta04/tfs1/membrane.py` | Artifact hashing, transplant into a fresh process, receipts, `hitting_costs`, `paired_crn`, `flip_test` | import |
| `roles/Aphrodite/beta04/tfs1/e3/organism.py`, `e3/worlds.py` | Arm definitions and the redacted arm view; a model for the lifetime driver | read as specification; reuse `worlds` |
| `roles/Aphrodite/beta04/foundry/generator.py`, `qualify.py`, `nulls.py`, `interp_a.py` | Task worlds, admission gate, null ladder, the second interpreter | run as a separate tool to produce task files |
| `roles/Aphrodite/beta04/foundry/tenum.py` (`PRUNE_RULES`) | The hand-written rule list used as the miner's planted positive | read; transcribed into a test fixture |
| `rso/completeness/manifest.py`, `verify.py` | Sealed manifest of runs | import |
| `rso/qualify/falsifiable.py` | Control-falsifiability audit | import |
| `rso/adversary/attacks.py`, `core.py` | Attacks on the evaluator and reducer | import; register a new target |
| `crius/evaluate.py` (`causal_controls`) | Conditions E-J | read as specification; re-implemented over artifacts |
| `fabric/` at tag `fabric-v0.2` | Distribution across the fleet | submit script-executor tasks; from M1 |

## 2. M0 -- Proof of mechanism

**Question.** Can laws mined from the engine's own search experience become durable search machinery that pays
for itself, against the strongest no-learning search already in the repository?

**Why this first.** It is the cheapest test that can kill the whole proposal. It needs no library learning, no
schemas and no fleet.

### 2.1 Code

| Module | Contents | Size (estimate) |
|---|---|---|
| `mathesis/_paths.py` | Pinned import of TFS-1; code-hash check | 40 lines |
| `mathesis/meter.py` | Work meter over `tfs1.core.U` plus match units; per-phase accounting | 80 |
| `mathesis/theory.py` | `Law`, `Theory`: `is_normal`, `normalise`, ordered rewriting, retraction, hashing | 300 |
| `mathesis/mine.py` | Collision harvesting from `oe_pruned_log`; task-free enumeration; variable generalisation; bounded verification; orientation; removal of derivable laws | 350 |
| `mathesis/search.py` | `NFEnumerator(Enumerator)` overriding `terms()` | 120 |
| `mathesis/artifact.py` | Export and load of (library, theory) with hash | 80 |
| `mathesis/tests/` | Known-answer tests (below) | 400 |
| `mathesis/exp/m0_*.py` | The four experiment drivers | 400 |

About 1,800 lines including tests.

### 2.2 Steps

| Step | Deliverable | Test that must pass first |
|---|---|---|
| 1 | Meter | Summing phases reproduces TFS-1's own unit counts on its cost-ledger test case |
| 2 | Theory: matching and normalisation | Hand-written laws normalise hand-written terms to known results; rewriting terminates on 10^4 random terms; refinement semantics respected on terms that FAIL |
| 3 | Search in normal form | With an empty theory the walk is byte-identical to TFS-1's (compare `walk_sha256` from `test_enumerator_determinism_and_crn`). With a sound theory, every task TFS-1 solves is still solved |
| 4 | Miner | Planted positive: the foundry's rule families are rediscovered. Planted negative: a law true on the probe set and false on the bounded domain is rejected |
| 5 | Soundness audit | Blamed-miss detector fires on a deliberately wrong law |
| 6 | Experiments M0-E0 to M0-E3 | -- |

### 2.3 Experiments

**M0-E0 -- miner calibration (prediction PRED-1 of file 05).** Mine from collisions over the 29 base primitives with all designer
pruning off. Compare against the foundry's `PRUNE_RULES` families P1-P4, P6 and P7 (the foundry's own labels).

**M0-E1 -- theory bootstrapping (the initial executable experiment).** No tasks involved, so every number is exact.

```
T_a = mine(empty, B)          T_b = mine(T_a, B)          T_c = mine(empty, 2B)
```

Report for each: the laws found; the number of normal-form terms per size and type; and, as the ceiling, the
number of distinct behaviours per size (the observational-equivalence count from the probe in file 01 s6). The
comparison of interest is `T_b` against `T_c`: same total work, with and without the miner using its own product.

**M0-E2 -- does the theory pay on tasks.** Arms BASE, BASE+, TREAT (a theory mined in one lifetime, no library),
MATCHED, SHAM-INERT, SHAM-SCRAMBLED, on the families already admitted by the Beta-04 foundry. This is a pilot: the
admitted set is 15 families in 7 worlds, too few for a confirmatory test. It gives a direction and a variance for
powering M1.

**M0-E3 -- does normalisation repair extraction (prediction PRED-3).** Take the Beta-04 E3-KP units whose stones were
mis-cut (`roles/Aphrodite/beta04/SYNTHESIS.md` s2). Normalise the solved programs under the mined theory, then
run the unmodified compressor. Count how many stones come out correctly cut, against the frozen extraction and
against the hand-written X-ABS patch.

### 2.4 Commands

```
# exists: confirm the pinned substrate (run from the worktree root)
cd roles/Aphrodite/beta04 && python -m tfs1.tests.run_tests --quick

# proposed
python -m unittest discover -s mathesis/tests -t .
python -m mathesis.exp.m0_e0_calibrate   --out runs/m0/e0.json
python -m mathesis.exp.m0_e1_bootstrap   --budget 2000000 --out runs/m0/e1.json
python -m mathesis.exp.m0_e2_tasks       --families roles/Aphrodite/beta04/foundry/production --freeze mathesis/exp/M0_FREEZE.json --out runs/m0/e2
python -m mathesis.exp.m0_e3_extraction  --out runs/m0/e3.json
python -m mathesis.exp.replay_check runs/m0          # every result reproduced bit-identically
```

### 2.5 Resources

| Item | Estimate | Basis |
|---|---|---|
| Engineering | 5-8 working days | 1,800 lines, tests first |
| E0, E1 | Under 2 core-hours | The probe covered size 6 in 0.4 s; size 8 is about 150 times more |
| E2 | 10-25 core-hours | 15 families x 6 arms x up to 1e6 candidates at 10-60 thousand per second (`TFS1_THROUGHPUT.json`) |
| E3 | Under 1 core-hour | A few dozen programs |
| Memory | Up to about 3 GB per process | TFS-1 peaked at 3.1 GB when walking size 8 with a library |
| GPU | None | -- |

One machine is enough.

### 2.6 Expected failure modes

| Failure | Sign | Response |
|---|---|---|
| Laws are sound on the probe set and wrong in general | Bounded verification rejects many; blamed misses in E2 | Enlarge the bounded domain; add edge-case inputs (empty list, ceiling values) |
| Matching costs more than it saves | TREAT loses to BASE+ on work although it evaluates fewer candidates | Index laws by head symbol; if still losing, this is the no-go |
| Laws inside lambda bodies are rare or useless | TREAT's advantage over BASE+ is nil exactly where BASE+ is heuristic | Report; lowers the value of the theory relative to per-task pruning |
| The Beta-04 admitted set is too easy or too hard to separate arms | All arms solve everything, or nothing | Report as underpowered; generate worlds for M1 before deciding |
| Normal-form search changes the keyed order in a way that helps or hurts by luck | Large seed variance | Evaluate at several order seeds, as E3-R did with seeds 0-2 |

### 2.7 Go / no-go

| Outcome | Decision |
|---|---|
| PRED-1 fails | Fix the miner. Do not proceed |
| E1: `T_b` equals `T_c` in laws and in normal-form counts | Expected (prediction PRED-2). Not a stop: it says R-A saturates, which the design assumes |
| E2: TREAT beats BASE+ on total work in direction, zero blamed misses; **or** E3: normalisation repairs at least 2 of the mis-cut stones without a hand patch | **GO to M1** |
| E2: TREAT is no better than BASE+ on total work at every budget, **and** E3 repairs nothing | **NO-GO. Stop the line.** A learned theory is then a slower form of pruning the repository already has, and it does not help extraction. Write it up as a negative result |
| E2 underpowered and E3 positive | GO, with world generation as M1's first task |

## 3. M1 -- Recursive generation

**Question.** Does the first improved descendant, using machinery its parent built, build further machinery that
helps, under independent validation? This is the second-generation test of file 06 s6.

### 3.1 Code added

| Module | Contents | Size (estimate) |
|---|---|---|
| `mathesis/promote.py` | Normalise-then-compress; description-length score | 200 lines |
| `mathesis/schema.py` | Anti-unification over laws with operator variables; instantiation; hit records | 350 |
| `mathesis/search.py` (extended) | Inverse step; optional per-example join | 300 |
| `mathesis/accept.py` | Paired replay on the engine's validation set; logging of every trial | 150 |
| `mathesis/life.py` | Lifetime driver; arms TREAT, NO-INHERIT, CLAMP, SHUFFLED, PARAM-ONLY, shams | 400 |
| `mathesis_eval/` | Evaluator, reducer, manifest, adversary target, falsifiability table | 600 |
| `mathesis/ref/` | Hand-built reference artifacts for gates W2 and W3 | 150 |
| tests | -- | 800 |

About 3,000 further lines.

### 3.2 Steps

1. Generate and admit worlds with the existing foundry: two independent batches of at least 24 worlds each, plus
   a screening batch. Seal the test and tribunal examples.
2. Build the evaluator and pass gates R1-R4 on the reference and sham artifacts **before any treatment lifetime
   runs**.
3. Pass gates W1-W3. If W3 fails, C3 is untestable in this world: stop here and report.
4. Run the supply screen; fix the number of world pairs; freeze arms, thresholds, seeds and budgets in a committed
   file.
5. Run lifetimes for generations 0 to 1 and 1 to 2 in every arm; evaluate every artifact on the sealed families.
6. Reduce with the frozen reducer. Apply file 06 s7 mechanically.
7. Replay everything on a second host and compare hashes.

### 3.3 Harness and commands (proposed)

```
# worlds (existing tool, run from its own directory, as its design document specifies)
cd roles/Aphrodite/beta04/foundry && python qualify.py world ...        # see FOUNDRY_DESIGN.md for the exact flags

# evaluator qualification
python -m mathesis_eval.gates --reference mathesis/ref --out runs/m1/gates.json
python -m rso.adversary run mathesis_eval                                # after registering the target

# one unit of work: (arm, world batch, generation); submitted through Fabric, one task each
python -m fabric submit --as <seat> --executor script --base <pinned sha> \
       --cap python.3.12 --key m1/<arm>/<batch>/<gen> -- python -m mathesis.life --arm <arm> --gen <gen> --freeze M1_FREEZE.json

python -m mathesis_eval.evaluate --artifact <path> --sealed <batch> --out runs/m1/rows/
python -m mathesis_eval.reduce runs/m1 --freeze M1_FREEZE.json            # prints the label of file 06 s7
```

The Fabric flags are those documented in `fabric/README.md` s3. I have not submitted a task; check them against
the frozen CLI before use.

### 3.4 Resources

| Item | Estimate | Basis |
|---|---|---|
| Engineering | 3-5 weeks | 3,000 lines plus evaluator qualification |
| World generation and admission | 80-120 core-hours | Beta-04's whole campaign, foundry included, was 36.4 core-hours for 12 worlds |
| Lifetimes | 20-40 core-hours | About 13 arms x 2 generations x 2 batches, each well under an hour |
| Evaluation | 200-350 core-hours | About 20 artifacts x 2 batches x 24 worlds x roughly 10 families, capped at 1e6 candidates per task, times 2 for replay |
| Total | **300-500 core-hours** | A day or two of wall time on the fleet |
| GPU | None | -- |

### 3.5 Expected failure modes

| Failure | Sign | Response |
|---|---|---|
| W3 fails: the foundry has no second level a depth-2 artifact can exploit | Depth-2 reference does not beat depth-1 | Stop C3 here. This is Aphrodite's Beta-03 outcome C again, and it is a finding about worlds |
| Stones are still not acquired without a supplied decomposition | Few entries promoted; library stays under 10 | The recursion test is then run below the schema threshold (prediction PRED-4). Report as UNTESTED at scale, not as a negative |
| Schemas are inert | REC equals CLAMP | `recursion_test = NOT_DEMONSTRATED:IMPROVER_IDLE` |
| Acceptance test starves the lifetime | Most of the budget goes to replays | Batch changes; cap the fraction; report |
| Supply under power | Screen variance larger than expected | More worlds, or declare UNTESTABLE. Aphrodite lost 3 of 4 consecutive assays to supply; the screen exists because of that |

### 3.6 Go / no-go

| Outcome | Decision |
|---|---|
| `INVALID_OR_INCONCLUSIVE` | Repair the named gate once. A second failure stops the stage |
| `LEARNING_DEMONSTRATED` only | Stop. The design has collapsed to Candidate A |
| `SELF_MODIFICATION_DEMONSTRATED`, `recursion_test = NOT_DEMONSTRATED:SATURATED` or `IMPROVER_IDLE`, library above the threshold of prediction PRED-5 | **Stop the recursion claim.** Publish the L2 result and the negative |
| Same, but library below the threshold | One further run with a larger practice supply, preregistered. Then stop or go |
| `BOUNDED_RECURSIVE_IMPROVEMENT_SUPPORTED`, replicated | **GO to M2** |

## 4. M2 -- Transfer and expansion

**Question.** Do the gains hold on tasks and representations the engine's world did not shape?

### 4.1 Work items

| Item | Content | Why |
|---|---|---|
| F_far | A task generator written by a different author, over the same primitives, with a different family grammar. Candidates in the repository: Hestia's Composition Ladder rungs; Ensorain's hidden-state families | The foundry plants mechanisms. A gain there may be recovery of what was planted |
| F_ext | External tasks expressible in the contract language | Structure nobody at Prometheus chose |
| F_shift | Changed input distributions | Environment change |
| Second primitive basis | A new contract (for example Boolean and bit-vector operators) with its own interpreter | **The cleanest transfer test of the meta-level.** Library entries and laws do not carry over to new primitives. Schemas do. Compare theory mining in the new basis with inherited schemas against mining from nothing |
| Property laws | Use PROPERTY laws to prune sketches top-down (the surviving part of Candidate C) | A use of mined theory that per-task pruning cannot imitate |
| More generations | Run until the gain ratio is at or below one twice | Measure the depth of the bounded recursion |
| World co-evolution | Only if M1 was positive | Hestia's advice: coevolving worlds against an organism that cannot climb only generates harder deserts |

### 4.2 Known obstacle to settle first

The TFS-1 contract takes a list as input and has literals 0-3 only. Aphrodite's RB-5 found that its earlier fold
language could not express independent worlds without integer literals, a lag register and a position atom.
Whether the TFS-1 contract can express a useful set of external tasks is an open question. If it cannot, F_ext
needs a versioned contract extension, which re-bases every budget number and must be a separate, declared world.

### 4.3 Resources

| Item | Estimate |
|---|---|
| Engineering | 4-8 weeks, dominated by the independent generator and the second basis |
| Compute | 500-1,500 core-hours |
| GPU | None |

### 4.4 Go / no-go

| Outcome | Decision |
|---|---|
| C4 holds on F_far and F_ext | Qualifier `TRANSFER = YES`. Seek outside replication, as `PHASE3_CHALLENGES.md` 1e asks |
| Holds on F_near only | `TRANSFER = NO`. The result is "works under constructed recurrence", the same scope as Aphrodite's A23 |
| Inherited schemas do not speed mining in a second basis | The meta-level is basis-bound. Record it; it bounds what "learning to learn" means here |

## 5. Timeline and decision points

```
week 1          M0 built; E0, E1 run                      -> first numbers
week 2          M0 E2, E3                                  -> GO / NO-GO #1   (can stop the whole line)
weeks 3-6       M1 built; gates; worlds admitted           -> W3 decision     (can declare C3 untestable)
week 7          M1 confirmatory run and replay             -> GO / NO-GO #2
weeks 8-15      M2                                         -> transfer verdict
```

The first falsifiable result is due in week 1 and the first decision that can end the project in week 2.

## 6. What this roadmap does not include

- No change to any production engine, archive, ruling or frozen test.
- No language model anywhere in the runtime. Design-time help from models is governed by the charter's
  commitment 3 and is outside this plan.
- No seat assignment. Who owns the lane, and whether it merges with Aphrodite's Beta-05 question, is the
  operator's decision.
