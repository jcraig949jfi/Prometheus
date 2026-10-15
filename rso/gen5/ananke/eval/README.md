# rso/gen5/ananke/eval -- independent evaluation for Ananke PTE-C4 (C-019-T040, read-only preparation)

Argus[harry1-666e5dbc], claude-opus-5-5 (Q2), harry1, 2026-10-15.
- Branch `argus/c019-t040`, from main `0546be826`.
- Owner records read-only at `origin/ananke/p2b-2026-10-05` @ `f58362c5e`.

This is the Observatory's half of a joint acquisition-to-composition experiment on Ananke's PTE: built and qualified on
known answers so that a joint run needs no Observatory build time.

It is NOT an experiment:
- no native search;
- no new worlds;
- nothing written under `prometheus/ananke/` or `roles/Ananke/`;
- the owner's champion populations (pops_C4T / pops_C4D) and any C5T output were never opened;
- the preregistration is a DRAFT that only the owner can sign off.

## 1. What is here

| file | what |
|---|---|
| `runner.py` | the CPU oracle's tick loop (`prometheus/ananke/oracle.py:277-511`, pinned by sha256) plus two marked additions: a between-tick hook (after the readout, as the engine's `lens.run`) and zero-communication. Every helper is imported from the oracle unchanged |
| `worlds.py` | sense streams for RELAY / HOLD / GATE / FLIP, mirror pairs, world seeds, env distance; the C4 task envs |
| `ruler.py` | the owner's competence rulers (RELAY-mh, FLIP B), studentized pair bootstrap, three-valued reading, 2.605-SE margin |
| `evaluate.py` | `eval_programs` on the oracle; the owner's known-answer seed keys; genome helpers; the register layout |
| `owner.py` | read-only, blob-pinned access to the owner's frozen C4 artifacts via `git show`. Refuses populations, C5T output and anything unpinned; re-hashes the bytes received |
| `ka_table.py` | the known-answer table (item 2): 108 checks, resumable rows carrying per-trial arrays, a reduce that recomputes rather than trusts |
| `mechanics.py` | Rung-4 interventions (item 3): line NOP, substitute, lesioned substitute, transplant (+ owner's renaming), **USE-DISABLED (bytes kept)**, register zero, zero communication, context / teacher off |
| `mechanics_run.py` | the interventions on gate_plant (2 cells) and P_FLIP (1 cell), each with a KNOWN outcome where one exists |
| `access.py` | accessibility statistics (item 4): exact CP, Fisher, Kaplan-Meier on right-censored hitting times, log-rank, exact McNemar on paired (cell, idx), paired first-to-B, exact power / detectable difference / n per arm, the search-table contract |
| `adversary_target.py` | the evaluator and the accessibility comparison as `rso.adversary` targets, run with the kit's runner (item 6) |
| `PREREG_DRAFT_PARTS_SUITABILITY.md` | the parts-suitability preregistration DRAFT (item 5), with `prereg_template.py`, which writes `qual/MANIFEST_TEMPLATE_parts_suitability.json` |
| `tests/` | unittest; `qual/RED_access_mechanics.txt` is the RED run |
| `runs/ka/`, `runs/mech/` | the committed rows (per-trial arrays included) and the worker logs |
| `qual/` | KA_TABLE.json, MECHANICS_KA.json, ADVERSARY_RUN.json, TEST_RUN.txt, RED log, manifest template |

Run:

    python -m unittest discover -s rso/gen5/ananke/eval/tests -t .
    python -m rso.gen5.ananke.eval.ka_table reduce rso/gen5/ananke/eval/runs/ka rso/gen5/ananke/eval/qual/KA_TABLE.json
    python -m rso.gen5.ananke.eval.mechanics_run reduce rso/gen5/ananke/eval/runs/mech rso/gen5/ananke/eval/qual/MECHANICS_KA.json
    python -m rso.gen5.ananke.eval.adversary_target --json rso/gen5/ananke/eval/qual/ADVERSARY_RUN.json

## 2. Independence: what is independent, what is a re-implementation from a reading

| part | source | independent of the owner's engine code? |
|---|---|---|
| dynamics | `prometheus/ananke/oracle.py`, written from DESIGN.md alone by its author; used unchanged (tick loop copied with two marked additions) | yes; it is the owner's own independent witness. No torch |
| sense streams | DESIGN.md s7 fixes semantics but not the ENV draw order. The order was read from `prometheus/ananke/envs.py:121-252`, whose bytes equal the hash the owner froze in FREEZE_C4_D.json (`56e0921b...`) | **no**: a re-implementation from a reading. Pinned by end-to-end conformance, not by independence |
| rulers | the text of PREREG_PTE_C4 s2 / run_c4.py:6-7 / c2a_common.competence docstring; the bootstrap's numerics from swap_rel.py:79-134 | rule from text; numerics from a reading |
| plants | the owner's committed `plant_genome` in admission_R4.json; RELAY_LATCH assembled from c2a_common.relay_latch's text through `plants.assemble` | the owner's genomes, by design (known answers) |

**Conformance.** Every admission reading the owner committed (40 rows: plant, null and adversaries at 4 cells x 4
tasks) is reproduced on the CPU oracle: mean and lo99 to 1e-9, and every status exactly (qual/KA_TABLE.json).
- Torch was not needed, so no private venv was created. The owner's numbers came from the torch engine, so this
  reproduction is itself the engine conformance at the verdict-number level.

## 3. Qualification evidence

| item | result | file |
|---|---|---|
| (1) evaluator conformance | 40/40 owner admission readings reproduced on the CPU oracle; max abs difference in mean and lo99 = **0.0**; statuses identical, including FLIP-0099 RELAY_LATCH INDETERMINATE (the owner's reason FLIP is not admitted there) | qual/KA_TABLE.json |
| (2) known answers | **108/108 PASS**, reduce problems [], 4 plan-fixed rows re-executed bit-identically. See the breakdown below | qual/KA_TABLE.json, runs/ka/ |
| (3) Rung-4 mechanics on the plants | **32/32 KNOWN PASS**, after one recorded correction (s7 item 7); 22 MEASURED / DESCRIPTIVE rows recorded. See the breakdown below | qual/MECHANICS_KA.json, qual/MECHANICS_KA_first_reduce_FAIL.json, runs/mech/ |
| (4) accessibility statistics | 17 tests on synthetic data with known answers. See the breakdown below | tests/test_access.py |
| (5) prereg DRAFT | PREREG_DRAFT_PARTS_SUITABILITY.md: the six claims separated, the falsifiability table (10 rows), the completeness manifest template (24 shards, rso.completeness format), the s11 resource block with measured throughput and an exact power table | |
| (6) adversarial kit | 2 targets, 14 variants: **12 REJECTED, 1 LIMITATION (argus-c019t040-ka-replay-sample), 1 NOT_APPLICABLE, 0 SURVIVED, 0 VACUOUS**; exit 0 | qual/ADVERSARY_RUN.json, qual/ADVERSARY_RUN_OUTPUT.txt |
| tests | **43 tests OK** (67 s): runner pin and equality, ruler semantics, custody, access, mechanics contracts and oracle fire tests, live conformance, committed-evidence reduces. RED before access / mechanics existed | qual/TEST_RUN.txt, qual/RED_access_mechanics.txt |

**(2) Known answers, by check.**
- ADM: 40 checks.
- hold_latch on GATE: FALSE at 4 cells.
- DLIB:
  - all 15 plant lines live at 4 cells;
  - plant / reassembled / CONTEXT-only / CUE-only read TRUE / TRUE / FALSE / FALSE, with per-trial output identical
    when reassembled, at 4 cells.
- All 56 module-alone checks read FALSE.

**(3) Mechanics on the plants, KNOWN outcomes.**
- **gate_plant at FLIP-0000 and FLIP-0004:**
  - context half NOP, cue half NOP: FALSE;
  - **USE-DISABLED** (bytes kept and executed, writes to the dead O.chan) on the context half, the cue half and both:
    FALSE;
  - self-substitution: IDENTICAL;
  - lesioned substitutes (same ops, input read from ZERO): FALSE;
  - consistent renaming S1<->S2: IDENTICAL;
  - renaming S0<->S1: FALSE;
  - register-zero S2 (the owner's known answer): FALSE;
  - zero communication: FALSE;
  - context removed: FALSE;
  - offset transplant: IDENTICAL at FLIP-0000.
- **P_FLIP at FLIP-0000:** baseline TRUE; zero communication FALSE; all lines use-disabled FALSE.
- **MEASURED rows, for example:**
  - the size-matched evolved HOLD module substituted for the context half: FALSE at both cells;
  - 8 of 8 transplants into random backgrounds: FALSE;
  - register-zero S0: FALSE at FLIP-0000 and TRUE at FLIP-0004;
  - P_FLIP register-zero S2 (an unused register): TRUE;
  - teacher off: FALSE.

**(4) Accessibility statistics, what the tests pin.**
- The owner's CP bounds: .109 / .142 / .038 / .050 / .008-.208.
- The coordination doc's Fisher numbers: 5/32 vs 0/32 gives p = .026.
- Kaplan-Meier:
  - textbook censoring;
  - an all-censored arm stays finite, with median NOT_REACHED and rmst equal to the budget;
  - a search that never ran is refused at time 0;
  - a synthetic geometric rate is recovered.
- Log-rank; exact McNemar; paired first-to-B.
- Exact power, by enumeration; min-detectable difference; n per arm.
- The search-table contract: unpaired, duplicate, forged hit, scrubbed checkpoints and past-budget tables are all
  refused; a search that never ran is excluded and counted.

**Measured throughput.** 15,000-19,700 site-ticks per second per process, with two processes running. In
world-episodes per second per process: 1.1-1.8 for GATE at N = 64; 0.46 at N = 100; 0.31 at N = 144. The KA run cost
6.5 CPU-h and the mechanics 0.73 CPU-h (PREREG draft s6.1).

## 4. The Rung-4 definition of "disable use without deleting the bytes"

PTE has no call instruction. Every line of the running rule executes every tick, so a module's "invocation" is its
effect on the rest of the program through the registers it writes.

**Definition.** USE-DISABLED keeps every module line's op, a, b and imm bytes and its position. The line stays non-NOP,
still reads its inputs and still draws its RAND stream. Only its destination is renamed, to O.chan.
- **Why O.chan.** O.chan is dead when channels == 1, since O.chan mod C = 0 for every value (DESIGN.md s6 step 7).
- **Raw byte.** The rename keeps the raw byte's high part, exactly as the owner's `rename_state` does. By the owner's
  own convention (library-tagged lines are renamed at instantiation and still counted as the module) the module is
  still present.
- **Refusals.** It is refused when channels != 1, or when a line outside the module reads O.chan.

**Fire tests, both ways.**
- A dead line use-disabled gives per-trial output identical to the plant (test_mechanics).
- On the plants (MECHANICS_KA.json), the GATE context half and cue half each use-disabled lose competence (FALSE).
  So does all of P_FLIP.

## 5. Limitations (recorded; the adversary kit prints them as LIMITATION, never as a pass)

- **argus-c019t040-ka-replay-sample.**
  - What the reduce does: `ka_table.reduce` recomputes every reading from the per-trial arrays stored in each row. It
    compares the row's own claims against the recomputation, and re-executes a plan-fixed sample of single-genome
    rows on the oracle.
  - The limitation: a consistent rewrite of the per-trial arrays of a row outside the replay sample, with pt_sha
    recomputed and the verdict unchanged, is not detected without replaying that row.
  - Partial mitigation: ADM rows are also bound by the owner's recorded mean and lo99 to 1e-9.
  - Closing it: replay every row, about 3 core-h.
- **Null genomes are excluded from the replay sample.** Their outputs (.5 everywhere) do not depend on the dynamics,
  so replaying one would check nothing. This was found while building the kit target.
- **Module-alone placement.** The owner's placement for the 56 module-alone checks is not recorded. Here a module is
  placed from line 0 with identity naming, and every check reads not-TRUE (the owner's reading). A different placement
  is not covered.
- **The sense-stream generator is not independent** (s2).
- **Scope of the evaluator.** It is qualified at the four C4 cells, R4 physics, tasks RELAY1H / HOLD / GATE / FLIP.
  - Not qualified: other physics, other families (XOR / MAJ raise ValueError), state_dim != 3 for USE-DISABLED's
    plant checks, or channels > 1 (USE-DISABLED refuses).
  - Throughput limits the evaluator to verification and sampling, not to evaluating whole populations per generation
    (s3).

## 6. Proposed registrations (owners: Eupalamus for rso/adversary, Palamedes for rso/registry)

- **rso/adversary.** Two lines make the targets permanent:
  - in `targets.py`, `from rso.gen5.ananke.eval.adversary_target import register; register()` after `TARGETS`;
  - the limitation `argus-c019t040-ka-replay-sample` moved into `limitations.py`.

  Until then, `adversary_target.py` registers them in memory and runs the kit's own `core.run_variants`.
- **rso/registry** (AUTHOR_TESTED): `ananke-c4-independent-evaluator`.
  - files: this directory;
  - scope: s5;
  - tests: `tests/`;
  - evidence: `qual/`;
  - dependencies: `prometheus/ananke/oracle.py` (pinned lines), the owner artifacts (blob pins), `rso.adversary`,
    `rso.completeness`.

## 7. Field decisions (rso-builder-role s2.7: uncertainty, choice, reversibility, revisit trigger)

1. **Hooks by copying the oracle's tick loop.**
   - Uncertainty: monkeypatching vs a copy.
   - Choice: a copy, with a sha256 pin on the source lines and an equality test.
   - Reversible: delete runner.py once the oracle grows hooks.
   - Revisit trigger: the oracle changes (the pin test fails).
2. **USE-DISABLED via the dead O.chan sink** (s4).
   - Revisit trigger: the owner defines module invocation natively (e.g. G > 1 with SETRULE).
3. **Per-trial arrays in KA rows; the KA run restarted at row 8.** The first attempt's 8 rows were all PASS; they are
   kept outside the repo at C:/tmp/argus40/ka_attempt0.
   - Why: a reducer that trusts row-carried status is the known C-013 "trusts-derived" defect.
4. **Mechanics on 64 worlds, not 128.** The KNOWN outcomes there are structural (exact chance, or identity).
   - Revisit trigger: a MEASURED row near a cut.
5. **The adversary target is registered in this package, in memory** (s6).
6. **owner.load hashes the bytes it receives** (git blob sha1), not just the blob id it asked for. The adversary kit's
   owner-corruption variant needed it.
7. **CORRECTION: transplant position-invariance.** The first mechanics reduce FAILED one KNOWN row. The offset
   transplant at FLIP-0004 was TRUE but not identical.
   - Cause: my `why` asserted "mut_site 0" without checking it. FLIP-0004 has mut_site .001 and wimm 1, and in-lifetime
     Kp mutation hits a hashed instruction index (DESIGN s6 step 8), so moving lines changes the dynamics.
   - The evaluator was right; the expectation was wrong.
   - Fix: the precondition is now computed from the physics. Where it fails the row is MEASURED.
   - The FAIL output is preserved (qual/MECHANICS_KA_first_reduce_FAIL.json). The finding is in the prereg
     falsifiability table: library insertion changes the dynamics of moved lines at that cell, independent of their
     function.
8. **A wrong test expectation, corrected.** In test_access I expected power(0 vs .25, n = 32) > .95. The exact value is
   .930; the enumeration test pins the exact value.

## 8. Line counts (ONBOARDING-style)

| | lines | what |
|---|---|---|
| **new, production** | ~1,810 | owner 64, worlds 242, ruler 135, evaluate 137, mechanics 159, access 243, ka_table 307, mechanics_run 207, adversary_target 242, prereg_template 48, runner header and additions ~27 |
| **new, tests** | 470 | 5 test modules, 43 tests |
| **reused unchanged, imported** | ~276 | oracle.py helpers (hash, topology, LM, execute_program) |
| **reused unchanged, imported** | ~200 | rso.adversary core / attacks / limitations / targets runner |
| **reused unchanged, imported** | 68 | rso.completeness.manifest.build |
| **reused unchanged, imported** | (assemble only) | plants.assemble + physics (for RELAY_LATCH) |
| **reused, copied with 4 marked lines added** | 235 | oracle.run tick loop (sha256-pinned source lines) |
| **reused as specification, not imported** | ~1,150 | the owner's C4 / C3 / C2A Python (c4_common, c4_admission, build_dlib, run_c4, c3r_common, c2a_common, assay_candidates, assay_c4), envs.py, swap_rel.interval, inference.reading3 |
| **reused as data** | 6 artifacts | the owner's frozen artifacts (blob-pinned): admission_R4, PLAN_C4_T, LIBRARY_C4, DLIB_C4 (+ ASSAY_C4D, REDUCE_C4D pinned, unread) |

**Not written, because it existed:**
- the dynamics;
- the plants;
- the library and the D-LIB halves;
- the kit's runner and attacks;
- the manifest format.

**Written because nothing existed for it:**
- a torch-free world generator;
- the ruler, without torch;
- the between-tick hooks on the oracle;
- USE-DISABLED;
- the censored-accessibility layer;
- evidence rows that carry their per-trial arrays.
