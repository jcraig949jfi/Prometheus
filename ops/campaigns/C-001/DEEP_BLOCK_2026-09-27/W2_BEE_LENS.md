# W2 -- BEE (z80atlas) as a scientific lens on reproduction and heredity

Worker: W2-bee-lens (disposable, no seat identity). Branch `worker/W2-bee-lens` from `origin/main`.
Scope: `prometheus/z80atlas/` at the frozen 72-hour-campaign commit `16fc6c2a2e65421d421f3b175809160813946208`
(hereafter **16fc6c2a**), the Bellerophon forensics/grounding/coupling record on
`origin/bellerophon/coupling-campaign-2026-09-24` (identical, file-for-file, to what is already merged onto
`origin/main` at `roles/Bellerophon/forensics_2026-09-23/` and `roles/Bellerophon/coupling_2026-09-24/` --
verified with `git diff origin/main origin/bellerophon/coupling-campaign-2026-09-24 -- roles/Bellerophon/forensics_2026-09-23/`,
empty output), and `roles/Bellerophon/` on `origin/main` generally.

Citation convention: `16fc6c2a:path:line` cites the frozen campaign harness by `git show 16fc6c2a:path`; a bare
`path:line` cites the current worktree (`origin/main`); doc citations are `path:line` against the committed
markdown/JSON. Every claim is labelled **NATIVE** (the engine's own code/records say it), **DERIVED** (computed by
me from preserved records), or **INFERRED** (my reading of documented material).

---

## WORLD

z80atlas is a population of Z80-like byte tapes living in a declared, versioned "physics." `Config` (a dataclass)
holds every axis an experiment can vary: `world` (SOUP/GRID/NICHES/GRAPH), `representation`, `layout`,
`reproduction`, `pressure`, `spatial`, `task`, `scoring`, `read_gate`, `env_dynamics`, `mutation`, `mutation_rate`,
`recombination`, `init`, plus `cells`/`ticks`/`budget`/`lifespan`/`init_tapes` (16fc6c2a:world.py:40-59). **NATIVE.**

The address space is one 256-byte block per interaction (`vm.SPACE = 256`, 16fc6c2a:vm.py:25): an organism's own
tape occupies `[0, L)`, a partner's tape is mapped into the "neighbour window" `[L, 2L)`, task input bytes live at
`IN_BASE = 0xE0` (16 bytes) and task outputs at `OUT_BASE = 0xF0` (16 bytes); everything is masked `& 0xFF`, so no
write can escape the 256-byte sandbox (16fc6c2a:vm.py:11-16,26-28,101). `L` (tape length) is 64 for `Z80_64`/`VM_COPY`
representations and 32 for `BYTECODE32` (16fc6c2a:world.py:61-63). **NATIVE.**

Spatial structure: `GRID`/`LOCAL` arranges cells on a `side x side` square with 4-neighbour wraparound adjacency
(`side = round(sqrt(cells))`, 16fc6c2a:world.py:74-75,205-213); `SOUP`/`WELL_MIXED` picks a uniformly random partner
every interaction (16fc6c2a:world.py:217-219); `GRAPH` draws a random 4-regular-ish adjacency once at init
(16fc6c2a:world.py:126-132); `NICHES` splits the grid into four 2x2-block niches (16fc6c2a:world.py:70-71,119-120)
with ten spatial policies governing migration between them (`NICHES_ISOLATED` through `RESERVOIR`,
16fc6c2a:grammar.py:25-26). **NATIVE.**

One tick (`World.step`, 16fc6c2a:world.py:302-391, docstring 16fc6c2a:world.py:4-22): (1) the `Environment` advances
(task shift/drift/co-evolution/environment-reproduction, see HEREDITY); (2)-(3) every living organism, in a
per-tick-shuffled order, picks a partner by the spatial policy, executes with its own tape + the partner's tape in
the window + task-input bytes, is scored, and any window writes are handed to the reproduction physics; (4) death
(`energy <= 0` or `age > lifespan`) and universal background mutation on every survivor; (5) `EXTERNAL`
population-manager reproduction, only if configured; (6) migration. **NATIVE.**

The frozen factor grammar (`grammar.py`) declares 14 axes (`FACTORS`, 16fc6c2a:grammar.py:19-35), structural
validity rules (`violations`, 16fc6c2a:grammar.py:72-102), 12 "collision" templates
(16fc6c2a:grammar.py:44-57), 8 critical matched controls (16fc6c2a:grammar.py:60-69), and a `grammar_hash()`
(16fc6c2a:grammar.py:238-241) that is asserted unchanged on every resume (16fc6c2a:scheduler.py:52-53). No level,
axis, constraint or threshold changes mid-campaign by design (16fc6c2a:grammar.py:1-7). **NATIVE.**

The 72-hour campaign that actually ran this code copied `prometheus/z80atlas` at exactly 16fc6c2a to a read-only
workdir before launch: `code/COMMIT_patched.txt = 16fc6c2a2e65421d421f3b175809160813946208`
(roles/Bellerophon/forensics_2026-09-23/EVIDENCE_MANIFEST.md:4). Wall time 2026-09-19T14:39:46Z to
2026-09-22T14:38:42Z, 63,247 completed runs, 49,412 distinct factor-vector families
(roles/Bellerophon/forensics_2026-09-23/POST_CAMPAIGN_FORENSICS.md:25,30,38). **DERIVED** (from the forensics team's
own recomputation of the preserved campaign records, which I did not re-run but whose defining code I did read).

---

## ENTITY

An organism (`Org`) is: `id`, `tape` (a `bytearray` of `L` bytes -- the ENTIRE heritable state), `parent` (causal
parent id), `lineage` (causal lineage id), `birth` tick, `mechanism`, plus non-heritable bookkeeping (`energy`,
`age`, `score_ema`, `replications`, ...) and `glineage` ("GENETIC lineage: whose bytes this tape descends from"
(16fc6c2a:world.py:85-104, comment at line 104). `INIT_ENERGY = 12.0` for every fresh organism, seeded or not
(16fc6c2a:world.py:34,93). **NATIVE.**

There is no persistent internal machine state: every VM execution starts fresh with registers `A=B=C=D=S=T=0`,
`Z=CF=False`, `PC=entry` (16fc6c2a:vm.py:82-84) -- the tape's bytes are the only thing that carries information from
one execution to the next. A dedicated test asserts newborns "inherit nothing non-heritable": fresh energy
(`<= 12.0+3.0`), age `<= 2`, replications `<= 2` regardless of the parent's accumulated state
(16fc6c2a:tests/test_z80atlas.py:70-74). **NATIVE.**

Substrate ("Z80-LIKE, not the Z80 ISA"): byte-addressable, self-modifiable code/data; registers A/B/C/D + pointers
S/T; Z/C flags; jumps `JP/JZ/JNZ/JC/JR/DJNZ`; copy instructions `LDI/LDIR/COPYALL`; **no multiply** (shifts/adds
only); **any byte may be opcode or operand depending on where the PC lands**; **undefined opcodes execute as NOP**
so a mutated byte is reinterpreted, never an error (16fc6c2a:vm.py:1-9,31-54,199). Verified by a dedicated test that
flips a byte from `INC_A` to `OUT_A` mid-program and confirms the VM just runs the new instruction
(16fc6c2a:tests/test_z80atlas.py:21-30). **NATIVE.**

Representation controls `L` and whether the native `COPYALL` (whole-tape-in-one-instruction copy) primitive is legal:
`Z80_64` (L=64), `BYTECODE32` (L=32), `VM_COPY` (L=64, `allow_copyall=True`) (16fc6c2a:world.py:42,61-67,
16fc6c2a:vm.py:36,142-146). **NATIVE.**

Four `init` modes populate half the world's cells at t=0 (16fc6c2a:world.py:178-198): `RANDOM` (uniform random
bytes); `SEEDED_REPLICATOR` (a hand-written 8-byte `LDIR` self-copier, 16fc6c2a:vm.py:205-211); `SEEDED_WITNESS` (a
hand-written exact task solver, one program per task kind, 16fc6c2a:vm.py:214-237); `SEEDED_HYBRID` (replicator +
witness concatenated, dropping the replicator's HALT so execution falls into the task code,
16fc6c2a:vm.py:240-242). Seeded/transplanted organisms are always placed as a **minority** into a majority of
`RANDOM` organisms -- 1/8 of the filled half for seeds, 1/4 for transplants (16fc6c2a:world.py:190-198) -- and are
explicitly tagged (`seed_lineages`, 16fc6c2a:world.py:174-175) so later analysis can tell a planted lineage from a
candidate spontaneous one. **NATIVE.**

---

## REPRODUCTION (what event counted, in code, and every mode)

Six reproduction "physics" exist, `REPRO = (EXTERNAL, ENDOGENOUS_COPY, ENDOGENOUS_PARTIAL, OVERWRITE, CONSTRUCTIVE,
PAIR_EXECUTION)`; `ENDOGENOUS = frozenset(REPRO[1:])` -- the five non-EXTERNAL modes (16fc6c2a:world.py:35-36).
**NATIVE.**

**EXTERNAL.** Window writes made during normal execution mean *nothing*: `_apply_reproduction` returns immediately
under EXTERNAL, "the window is scratch" (16fc6c2a:world.py:396-397). Reproduction instead happens once per tick in
`_external_reproduce`, the "population manager" (16fc6c2a:world.py:444-480): it selects roughly `alive/8` parents
weighted by a pressure-dependent scheme (16fc6c2a:world.py:482-490), places a mutated copy of the parent's tape into
an empty (or, under WELL_MIXED/SOUP, any) neighbouring cell, optionally splices in `CROSSOVER` recombination from a
second randomly chosen parent (16fc6c2a:world.py:466-469), and mutates the offspring at **4x** the background rate
(16fc6c2a:world.py:470). The function opens with `assert cfg.reproduction == "EXTERNAL"` (16fc6c2a:world.py:447).
**NATIVE.**

**Endogenous physics -- the shared event.** Every non-EXTERNAL mode reads the same underlying event: bytes an
executing organism wrote into the neighbour window `[L, 2L)` during its own scored execution
(`tr.neighbour_writes`, checked at 16fc6c2a:world.py:342,344 and dispatched to `_apply_reproduction`,
16fc6c2a:world.py:394-415). What differs is the viability rule and what an occupied/empty target means:
- **ENDOGENOUS_COPY**: viable iff **all** `L` window bytes were written (16fc6c2a:world.py:406).
- **ENDOGENOUS_PARTIAL**: viable iff **>= 1** byte was written; the rest of the child inherits whatever the
  previously-occupying organism's tape held -- "chimeras" (16fc6c2a:world.py:406, docstring line 12).
- **OVERWRITE**: the target cell **must be occupied** (refused otherwise, 16fc6c2a:world.py:404-405); viable iff
  `>= L/2` bytes written; replaces the incumbent.
- **CONSTRUCTIVE**: the target cell **must be empty** (refused otherwise, 16fc6c2a:world.py:402-403); viable iff
  `>= L/2` bytes written; constructs into it.
- **PAIR_EXECUTION**: the two organisms' tapes are concatenated into one `2L`-byte program and run as a **single**
  VM execution (`_pair_execute`, 16fc6c2a:world.py:291-299); either half may rewrite the other; the halves are split
  back afterward (16fc6c2a:world.py:330-338, "the soup physics", docstring lines 15-16); viable iff `>= L/2` bytes
  of the partner's half changed (16fc6c2a:world.py:408).
All five conditions are collected in one dict at 16fc6c2a:world.py:406-408. A write that leaves the target
byte-for-byte identical to what it already contained is explicitly **not** a birth: `null_rewrites`, "the partner
was rewritten as EXACTLY itself: nothing was caused, no birth" (16fc6c2a:world.py:412-413). **NATIVE.**

**The endogenous guard.** `World._external_reproduce` asserts it is never invoked under a non-EXTERNAL config
(16fc6c2a:world.py:447), and `runner.run_spec` separately re-asserts after every completed run that
`not (vec["reproduction"] in ENDOGENOUS and summary["external_births"] > 0)` -- "external reproduction leaked into
an ENDOGENOUS treatment" (16fc6c2a:runner.py:36). Both are exercised by tests
(16fc6c2a:tests/test_z80atlas.py:49-55). **NATIVE.**

**A second, un-gated copy channel: migration.** Under spatial policies `NICHES_POLLINATION` and `RESERVOIR`,
`_migrate` spawns a **fresh** `Org` with the source's `lineage`/`glineage` while the source stays put -- "a copy
crosses, the source stays" (16fc6c2a:world.py:559-560). At 16fc6c2a this fires **regardless of the `reproduction`
axis**: nothing in `_migrate` (16fc6c2a:world.py:534-564) checks `cfg.reproduction`, and the copy is counted only in
`self.migrations`/`self.cross_niche_transport` (16fc6c2a:world.py:563), never in `external_births`. **The endogenous
guard above therefore cannot see it** -- it only inspects `external_births`. **DERIVED** (I read `_migrate` and the
guard side by side; neither the code nor its own docstring flags this interaction. It is exactly the defect the
forensics pass later named P1 -- see REINTERPRETATIONS).

---

## HEREDITY (what can pass, by which paths, glineage/material semantics)

Only tape bytes are heritable; nothing else survives a birth (`test_offspring_inherit_nothing_non_heritable`,
16fc6c2a:tests/test_z80atlas.py:70-74; inline comment "fresh energy, no registers: nothing non-heritable travels",
16fc6c2a:world.py:431). **NATIVE.**

Two distinct, simultaneously tracked lineage labels exist on every `Org` (16fc6c2a:world.py:90,104):

- **`lineage` (CAUSAL): who wrote it.** Set to the *writer's own* `lineage` at every endogenous birth
  (`lineage=parent.lineage`, 16fc6c2a:world.py:431) and at every external birth (16fc6c2a:world.py:474) -- it always
  tracks the organism that *executed* the write, independent of whose bytes ended up in the child.
- **`glineage` (GENETIC): whose bytes it resembles.** Computed in `_register_offspring`
  (16fc6c2a:world.py:417-431): "the WRITER is the causal parent; the GENETIC source is whichever tape the child's
  bytes resemble more -- the writer's, or the target's own previous contents." Fidelity is computed against both
  candidates; if the overwritten TARGET's fidelity is strictly higher, `material = "target"`,
  `glin = replaced.glineage`, and `self.captures += 1` fires (16fc6c2a:world.py:424-428) -- the **CAPTURE** event,
  explicitly named "code capture, the byte-soup ambiguity made explicit rather than hidden"
  (16fc6c2a:world.py:418-420). Otherwise `material = "writer"` is the default (16fc6c2a:world.py:421) -- ties
  (`fid_target == fidelity`, which for `L=64` occurs at an exact `L/2` Hamming split) resolve to **writer** because
  the comparison at line 425 is a strict `>`.

**Migration heredity** is different in kind: `_spawn(j, bytearray(o.tape), o.id, "pollination", lineage=o.lineage,
glineage=o.glineage)` (16fc6c2a:world.py:560) copies both labels unchanged because no VM execution or byte-mixing
occurs -- it is a pure structural duplication, not an *executed* reproduction event. **NATIVE.**

**Mutation** is the only stochastic post-birth alteration, applied to *every* living organism's own tape *every*
tick (`_mutate`, called for every survivor at 16fc6c2a:world.py:375). Four operators (16fc6c2a:world.py:234-261):
`OPERAND` (bytes outside decoded-opcode positions step by +-1), `OPCODE` (only decoded-opcode positions, full
re-roll), `BYTE` (any byte, full re-roll), `STRUCTURAL` (insert/delete/duplicate a random-length segment). Rate is
one of LOW/MED/HIGH (`0.002/0.008/0.03`, 16fc6c2a:world.py:78-79). `EXTERNAL` offspring additionally receive one
**extra** mutation pass at birth at **4x** the background rate (16fc6c2a:world.py:470); endogenous/migration
offspring receive no such birth-time bonus -- what a child inherits is exactly what the parent's tape looked like at
write time, then it is subject to the same universal per-tick background pass as any survivor from then on.
**NATIVE.**

**Environment heredity is separate machinery.** Under `ENV_REPRO` dynamics, a niche's task *parameters* (`kind`,
`k`) can be copied into a neighbouring niche once the source niche is "persistent" (occupancy above 30% of its
share) -- "environments REPRODUCE" (16fc6c2a:tasks.py:17-18,133-139); recorded in `Environment.lineage`
(16fc6c2a:tasks.py:102,138), entirely independent of organism `lineage`/`glineage`. **NATIVE.**

**Seeded lineages are natively self-marked.** `mechanism in ("seed", "transplant")` adds `o.glineage` to
`self.seed_lineages` at birth (16fc6c2a:world.py:174-175); every later replication record and the run summary carry
a `seeded` flag derived from this set (`first_replication["seeded"]`, 16fc6c2a:world.py:442;
`seed_lineage_share`/`seed_causal_share`, 16fc6c2a:world.py:693-694) -- the harness itself distinguishes "planted"
from "candidate spontaneous" at the raw-record level, before any forensics. **NATIVE.**

---

## OBSERVABILITY (directly measured vs. inferred)

**Directly measured, per instruction (`vm.Trace`, 16fc6c2a:vm.py:57-76):** step count, halted flag, `writes: Dict[addr,
last_value]`, self/neighbour/IO write and read counts, IO-region corruption count and first-corruption step, first
IN/OUT step, `copy_events` (LDI/LDIR/COPYALL moves into the window), executed-opcode histogram, `pc_max`. **NATIVE.**

**Directly measured, per birth** (`_register_offspring`, 16fc6c2a:world.py:436-438): tick, parent id, child id, cell,
`fidelity`, `mechanism`, `span` (`pc_max+1` of the triggering execution), `steps`, `replaced` id, `material`
(writer/target), `glineage`.

**Directly measured, per tick** (`_telemetry`, 16fc6c2a:world.py:607-624): alive count, interactions, mean/best
score, "solvers" (`score_ema >= 0.85`), copy attempts, replications and replication rate, mean fidelity, mean repro
span, deaths, external births, distinct `lineage` count, `arch_clusters` (distinct sorted first-6-opcode-position
sets -- a coarse structural-diversity proxy, 16fc6c2a:world.py:613), mean steps, niche occupancy, refused writes,
mean age.

**Directly measured, genealogy/archive:** `first_crossing` = first organism whose `score_ema` sustains `>= 0.85`
(16fc6c2a:world.py:357-359); `first_replication` = the **very first registered copy event, regardless of fidelity**
(16fc6c2a:world.py:439-442) -- this can be a near-zero-fidelity junk event (flagged later as defect D2, see
REINTERPRETATIONS); `_ancestry` walks the causal `parent_of` chain up to depth 40 (16fc6c2a:world.py:567-571);
serendipity specimens are archived whenever a tracked statistic moves `> 60%` relative to its running EMA
(`_serendipity`, 16fc6c2a:world.py:646-664); anti-cheat `exploits` record `corrupt_validation` (writing the input
region before reading it) and `evaluator_leakage` (a FORCED-gate task "solved" with zero reads)
(16fc6c2a:world.py:350-353,666-669).

**Directly measured, per top specimen (post-run):** mutational-neighbourhood scans (beneficial/neutral/deleterious/
lethal fractions, "moat density" toward the next-harder task in a matched family) and damage cliffs at
simultaneous-damage counts k=1,2,4,8,16 (`geometry.scan`/`damage_cliff`, 16fc6c2a:geometry.py:57-99), run by
`runner.run_spec` on the top 2 specimens, a random baseline, and the first replicator (16fc6c2a:runner.py:50-74).
All of the above: **NATIVE.**

**Not observable at 16fc6c2a, only inferable after the fact:** *which code executed a copy* is absent from the
native schema. `Trace.writes` records only "addr -> last value written" (16fc6c2a:vm.py:61) -- never the executing
PC or opcode. `material` (16fc6c2a:world.py:421,426) answers a strictly weaker, **resemblance**-based question
(which prior tape does the child look more like) and says nothing about whose *code* produced the write. Recovering
"self-replication" in the stronger provenance sense (own bytes, moved by the writer's *own* code) required, after
the campaign, replaying history through a hand-instrumented copy of the VM that adds per-byte provenance
bookkeeping (source address, executing PC, and opcode of the last write to every window byte) --
`traced_replay.py` (roles/Bellerophon/forensics_2026-09-23/tools/traced_replay.py:1-3,79-94). **NATIVE limitation +
DERIVED reconstruction** (I read both the frozen `Trace` dataclass and the replay tool's provenance bookkeeping
directly).

"Solved the task" at 16fc6c2a is an EMA-smoothed threshold (`score_ema >= 0.85`, 16fc6c2a:world.py:357,619) or a
20-tick tail average (`solvers_tail`, 16fc6c2a:world.py:701) -- not a verified, exact, held-out check that the
tape *alone* answers every input of the task. **NATIVE limitation**, later named defect C2 (see RULER).

---

## RULER (triggers, SR predicates, adjudication statuses)

`observatory.py`'s frozen threshold table `T` (persistent_alive_fraction 0.30, replication_rate 0.05, hifi 0.90,
compression_ratio 0.70, solvers 1.0, coexistence_fraction 0.50, novelty_hamming 24;
16fc6c2a:observatory.py:16-24), hashed by `thresholds_hash()` (16fc6c2a:observatory.py:120-121) and re-checked on
resume together with the grammar hash (16fc6c2a:scheduler.py:52-53). **NATIVE.**

Fifteen mechanical, per-run `triggers` (16fc6c2a:observatory.py:27-62): `persistent`,
`persistence_above_control`, `replication`, `spontaneous_replication`, `novel_architecture`,
`reproductive_compression`, `task_reproduction_coupling`, `task_score`, `moat_crossing`, `escape`,
`cross_niche_transport`, `environment_lineage`, `coexistence`, `exploit_recorded`, `novelty_distance`; twelve are
declared `PROMOTING` (16fc6c2a:observatory.py:65-67). `trigger_score` counts fired PROMOTING triggers
(16fc6c2a:observatory.py:70-71); a family is **promoted** the first time any one run scores `>= 2`
(16fc6c2a:scheduler.py:159-161), **retired** once `>= 3` runs exist and the best score is `<= 1`
(16fc6c2a:scheduler.py:162-164, `RETIRE_AFTER_RUNS = 3`). **NATIVE.**

Five **high-value flags**, computed *across matched family pairs* rather than within one run
(`high_value_flags`, 16fc6c2a:observatory.py:74-117): `REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL`,
`REACHED_INCREMENTAL_NOT_ATOMIC`, `RESERVOIR_CROSSED_MOAT`, `REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK`,
`REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY`. **NATIVE.**

None of the above vocabulary includes an *adjudication* status -- that is a forensic-stage addition, applied to the
native triggers/flags after the campaign: **CONFIRMED_CAUSAL / REPRODUCED_ASSOCIATION / PROVISIONAL /
DETECTOR_ONLY / CONFOUNDED / INSTRUMENT_FAILURE / NOT_ADJUDICABLE / FALSIFIED**
(roles/Bellerophon/forensics_2026-09-23/POST_CAMPAIGN_FORENSICS.md:11-12). Applying that vocabulary: all five
high-value flag classes were **FALSIFIED** (`REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL`, `RESERVOIR_CROSSED_MOAT`),
**INSTRUMENT_FAILURE** (`REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY`), **CONFOUNDED**
(`REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK`), or **DETECTOR_ONLY**
(`REACHED_INCREMENTAL_NOT_ATOMIC`) (POST_CAMPAIGN_FORENSICS.md s3.1-3.6, table cross-referenced in
roles/Bellerophon/forensics_2026-09-23/GROUNDING_REPORT.md:139-156). **DERIVED** (the forensics team's own
recomputation from preserved records, read and reported here, not independently re-run by me).

Positive/negative/cheat controls as a *category* were formalized only in the grounding round's preregistration
(GROUNDING_PREREG.md s.G8, roles/Bellerophon/forensics_2026-09-23/GROUNDING_PREREG.md:116-127): every detector must
ship with a cell that must fire (seeded replicator, seeded witness), a cell that must not (EXTERNAL+NEUTRAL, LDIR
disabled), and a cell engineered to *look* like the phenomenon without being it (bare-LDIR/self-smear/1-byte-capture
transplants) -- a failing control would declare the dependent results `NOT_ADJUDICABLE`. At 16fc6c2a the harness
already HAD five analogous "positive controls" (`controls.py:CONTROL_VECS`, 16fc6c2a:controls.py:36-45) gating the
*campaign's own start* (a failing one halts the campaign, 16fc6c2a:scheduler.py:327-331), but it had no *negative*
or *cheat* control category at all. **NATIVE** (16fc6c2a controls) + **DERIVED** (the grounding round's extension).

---

## STRONGEST FINDINGS (what survived BEE's own forensic attacks)

1. **Spontaneous, own-code self-replication from RANDOM populations.** The only phenomenon to survive both the
   forensic re-reading of the 72h campaign and the independent 12,130-run grounding round (fresh seeds, repaired
   detectors, preregistered predictions, no promotion). Grounding: reproduces at 0.75-4.8% of fresh runs depending
   on physics/representation, pooled 2.3% (GROUNDING_REPORT.md:17,45-50); **causally** dependent on the LDIR-class
   copy opcode *and* the "undefined-byte = NOP" slide that lets the PC wander into copy code -- removing either
   abolishes it (P8a/P8b, GROUNDING_REPORT.md:27-28,78-82); forms deep, transmitting lineages in a real minority of
   origins (39.4% SUSTAINED depth>=3, 44% EVOLUTIONARILY_ACTIVE, GROUNDING_REPORT.md:56-58, below the 90%
   trigger-selected historical estimate -- selection bias exposed); 86.1% of 345 banked historical origin tapes
   re-replicate when transplanted into fresh random populations (GROUNDING_REPORT.md:101-103). Final verdict:
   **CONFIRMED_CAUSAL** (GROUNDING_REPORT.md:143). **DERIVED.**

2. **All five automated "high-value flags" the campaign's own scheduler promoted on collapsed under adjudication**
   (POST_CAMPAIGN_FORENSICS.md s3, GROUNDING_REPORT.md s8): `REACHED_UNDER_ENDOGENOUS_NOT_EXTERNAL` **reversed**
   (matched, causal design: EXTERNAL reaches verified solutions 178 vs 2 discordant pairs,
   GROUNDING_REPORT.md:20,113-121); `REPRODUCTIVE_MACHINERY_RAISED_BENEFICIAL_DENSITY` was an unpaired-measurement
   artefact whose real (tiny) residual is **antagonism**, not synergy, between copying and computing
   (GROUNDING_REPORT.md:21,86-97); `REPRODUCTIVE_ARCHITECTURE_RESPONDED_TO_TASK` was a seeded-hybrid-takeover
   confound, null under a frozen structural descriptor (GROUNDING_REPORT.md:22,122-126); `REACHED_INCREMENTAL_NOT_ATOMIC`
   was a partial-credit-vs-exact-match ruler artefact with no detectable directional effect
   (POST_CAMPAIGN_FORENSICS.md s3.5); `RESERVOIR_CROSSED_MOAT` was an easy-niche + mis-seeded-witness confound
   (POST_CAMPAIGN_FORENSICS.md s3.6). **DERIVED.**

3. **The single strongest causal result of the whole program is a harness defect, not a biology finding.** Under
   `NICHES_POLLINATION`/`RESERVOIR`, migration silently manufactures an un-gated copy
   (16fc6c2a:world.py:559-560, see REPRODUCTION above) that the endogenous guard never sees; this one channel
   explains nearly all of the historical POLLINATION "topology effect" -- on identical seeds, switching the
   migration channel from COPY to MOVE takes extinction from 0/150 to 148/150 and spontaneous rate from 20.0% to
   1.3% (GROUNDING_REPORT.md:74-77; defect ledgered as P1,
   roles/Bellerophon/forensics_2026-09-23/ISSUE_AND_REPAIR_LEDGER.md row P1). **DERIVED.**

4. **Under the grammar's default (IMPLICIT) pressure, the task is causally inert.** A RANDOM population's energy
   inflow (`1.0 + 0.5*score`, 16fc6c2a:world.py:512) never falls below its cost (`0.9 + 0.001*steps`,
   16fc6c2a:world.py:516) regardless of score, so task performance can never decide who lives, dies, or reproduces;
   five of six task families were run-for-run IDENTICAL in the grounding round because of this
   (GROUNDING_REPORT.md:51-55). More broadly, under ENDOGENOUS reproduction, seeded task code actively **decays**
   because selection sees only the copy routine: matched seed-pair design, EXTERNAL reaches verified task solutions
   in 178/180 discordant pairs vs 2/180 for ENDOGENOUS (GROUNDING_REPORT.md:20,113-121). Bellerophon's own summary:
   "the physics is not yet a place where computation can affect reproduction"
   (POST_CAMPAIGN_FORENSICS.md:264). **DERIVED.**

5. **A later, hand-designed physics extension (v3, `coupling.py`) closed that gap for the first time, with real
   limits.** A VM-invisible "copy resource" ledger charges construction and pays a bonus only for verified-correct
   output (roles/Bellerophon/coupling_2026-09-24/COUPLING_CAMPAIGN_PREREG.md:15-24). Correct computation causally
   raised reproductive output (P1: 40/40 seed pairs, roles/Bellerophon/coupling_2026-09-24/COUPLING_CAMPAIGN_REPORT.md:29)
   and contingent (not merely equal-supply) earning maintained seeded competence against mutational decay (P2:
   149/150 pairs, COUPLING_CAMPAIGN_REPORT.md:30). But genuine *acquisition* of competence in a population that
   started with none occurred only for the single simplest task (ECHO), and mainly at one of two
   parameterizations (COUPLING_CAMPAIGN_REPORT.md:50-53,79); the campaign's own scope section states plainly that
   the confirmed core is "generality of MAINTENANCE of seeded code," not evolution creating computation
   (COUPLING_CAMPAIGN_REPORT.md:135-146). **DERIVED.**

---

## REINTERPRETATIONS (what later instrumentation changed)

- **Self-replication: resemblance -> provenance.** At 16fc6c2a, "material" is a resemblance vote between two
  candidate parent tapes (16fc6c2a:world.py:417-431); it is silent about which *code* executed the writes. A
  provenance-based classifier (own bytes, moved by the writer's *own* code, fidelity `>=0.9` before **and** after
  execution) first existed only as `traced_replay.py`'s bolted-on instrumented VM
  (roles/Bellerophon/forensics_2026-09-23/tools/traced_replay.py:1-22) and was later ported into the shipped engine
  itself as `World._is_self_copy`, riding on a **new** `Trace.win_prov` per-byte-provenance field that did not exist
  at 16fc6c2a (current `vm.py:78,127`; current `world.py:576-588`). **DERIVED + NATIVE** (I diffed the frozen
  `Trace` dataclass, which has no provenance field, against the current one, which does).
- **"First replication"/"first crossing" -> `first_self_replication`.** At 16fc6c2a these fields fire on the first
  *registered* copy event or score crossing, with no fidelity or self-direction check
  (16fc6c2a:world.py:357-359,439-442) -- ledgered as defect D2, "every descriptor anchored on it ... inherits
  junk" (ISSUE_AND_REPAIR_LEDGER.md row D2). The repair adds `first_self_replication` as a **separate**,
  provenance-gated field (GROUNDING_PREREG.md:41; current `world.py:563-567`), leaving the historical field's
  meaning intact but "INTERPRETATION_INVALID as 'first replicator'" (ISSUE_AND_REPAIR_LEDGER.md row D2). **DERIVED.**
- **"Solved" -> verified exact panel match.** `score_ema >= 0.85` (16fc6c2a:world.py:357,619) became a verified
  exact match on a fixed 16-input panel (`task_reached`, GROUNDING_PREREG.md:35-36) after defect C2 -- "only
  126/492 sampled crossing tapes are exact" (ISSUE_AND_REPAIR_LEDGER.md row C2). **DERIVED.**
- **Migration copying under POLLINATION/RESERVOIR: unremarked -> gated by a physics version.** 16fc6c2a's
  `_migrate` copy (16fc6c2a:world.py:559-560) is unconditioned on `reproduction`; the repair adds a
  `Config.physics` flag ("v1" replays the historical harness byte-for-byte; "v2" moves rather than copies under
  ENDOGENOUS reproduction) (current `world.py:62-71,718-719`; ISSUE_AND_REPAIR_LEDGER.md row P1). **DERIVED + NATIVE.**
- **The reproduction-computation resource channel itself was redesigned, not merely repaired.** 16fc6c2a already
  coupled score to energy under some pressures (`_inflow`/`_cost`, 16fc6c2a:world.py:493-519), but grounding showed
  this binds only weakly and never under the *default* pressure (finding 4 above). Physics v3's `coupling.py`
  layers an entirely separate, explicit copy-resource ledger `R` on top of the same tape/VM/window substrate as
  the *only* path by which task correctness can affect reproduction when `scoring=NEUTRAL`
  (COUPLING_CAMPAIGN_PREREG.md:15-24) -- a different reproductive economy, not a bugfix to the old one. **NATIVE + DERIVED.**
- **"Reproductive architecture" -> a frozen structural descriptor.** `repro_span = tr.pc_max + 1` of a
  copy-triggering execution (16fc6c2a:world.py:434,441) was shown to be dominated by IO-region PC excursions and
  tick-0 junk events (ISSUE_AND_REPAIR_LEDGER.md row C7) and replaced by `repro_descriptor`/`arch_descriptor`
  (copy_op, copy_pc, exec_own_bytes, exec_before_copy, task_before_copy, copy_covers_task; current
  `adjudication.py:42-103`) for the G5 re-grounding and the coupling campaign's architecture lanes
  (COUPLING_CAMPAIGN_PREREG.md:80-81). **DERIVED + NATIVE.**

---

## ATTENTION

**Host dependence.** `CAPTURE`-style births (native `material = "target"`) are majority-authored by the organism a
writer *overwrote*, not by the writer (16fc6c2a:world.py:417-431); `OVERWRITE` physics requires an *occupied*
target by construction (16fc6c2a:world.py:404-405) -- every such birth is host-dependent as a matter of physics,
not measurement noise. This is exactly the class of sighting the cross-engine causal-lens work treats as one of
three independent "host-conditioned reproduction" observations across engines
(archaeon/causal_lens/PORTABILITY01_REPORT.md:174). **NATIVE.**

**Self vs. foreign material.** At 16fc6c2a `material` is resemblance-only (see HEREDITY); it never asks which
*code* (own tape vs. the window `[L,2L)`, which may hold the partner's bytes *or* the writer's own just-copied
bytes) executed the write. Nothing in `vm.execute` (16fc6c2a:vm.py:78-201) prevents the PC from running from the
window under `SHARED` layout (the default, 16fc6c2a:world.py:43) -- so "self-copied code executed from a
foreign-looking location" is representable by the substrate but was, at 16fc6c2a, unrecorded and unrecoverable
except by full replay. **NATIVE.**

**Acquisition vs. maintenance.** The coupling campaign explicitly separates them and finds strong evidence only for
*maintenance* (contingent earning preserves already-present competence against mutational decay: P2 holds
149/150 pairs, COUPLING_CAMPAIGN_REPORT.md:30,48-49), with genuine *acquisition* (competence appearing where there
was none) limited to the single easiest task and mostly one parameterization (ECHO K40 29/150 vs. controls 6/150;
CONST 0-1/150; fully random populations 0/3,200, COUPLING_CAMPAIGN_REPORT.md:50-53,79). This mirrors a base-level
finding at the copier stage itself: every one of 160 grounding-round self-replication origins was *built by another
organism's prior copy activity* -- none was present, unmodified, from initialization
(GROUNDING_REPORT.md:60-64,146). Even "spontaneous" self-replication is itself acquired across a construction
chain, never simply maintained from t=0. **DERIVED.**

**Code execution vs. material inheritance.** This is precisely the WHO/WHERE/WHAT distinction Archaeon's
causal-lens work names "B6" for z80atlas specifically: WHO executed (the writer, always unambiguous in BEE's
`parent` field for single-execution physics, 16fc6c2a:world.py:394-431), WHERE it executed from (`pc < L` vs.
`[L,2L)`, formalized natively as `by_own_code` only in the *repaired* engine, current `adjudication.py:64`), and
WHAT material the executing code *is* (self-copied code sitting in the window reads as "foreign" by location but is
"own" by material -- never natively distinguished at 16fc6c2a or since; see SECOND PART item 2 below for where the
reports' own labelling of this blurs). **NATIVE + DERIVED.**

**Reproductive architecture.** Measured historically via `repro_span` (16fc6c2a:world.py:434) and compared almost
exclusively on `SEEDED_HYBRID` families where a hand-written replicator+witness dominates by construction (579/600
of the flagged instances, ISSUE_AND_REPAIR_LEDGER.md row C7); the frozen structural descriptor found **no**
task-driven architecture change (0/300 triples, GROUNDING_REPORT.md:122-126,150), and the coupling campaign
likewise found architecture change "only weakly observed" beyond the seeded shape
(COUPLING_CAMPAIGN_REPORT.md:64-66). **DERIVED.**

**Endogenous vs. externally supplied mechanisms.** The grammar draws a hard, code-enforced line between
reproduction an organism must *execute* (the five ENDOGENOUS physics, gated by the runner-level assertion,
16fc6c2a:runner.py:36, and the population-manager assertion, 16fc6c2a:world.py:447) and reproduction *supplied* by
an external population manager irrespective of what any organism executed (16fc6c2a:world.py:444-480). The
grounding round's most robust causal result runs opposite to the campaign's own flag detector: EXTERNAL population
management reaches verified task solutions far more reliably than letting organisms reproduce themselves (178 vs 2
discordant pairs, GROUNDING_REPORT.md:20,113-121) -- in this substrate, externally-imposed selection outperforms
self-directed reproduction at preserving/reaching useful computation. Physics v3 was built specifically to ask
whether an *endogenous* alternative could still be engineered (a resource ledger tying construction cost to
verified output) rather than abandoning endogenous reproduction as a research target
(COUPLING_CAMPAIGN_PREREG.md:9-27). **DERIVED.**

---

## SECOND PART -- where `V02_REGRESSION_REPORT.md` and `T-004_RESULT.md` disagree with, go beyond, or are
unsupported by BEE's own code/records

Both target documents are Archaeon's cross-engine "causal lineage lens" work, reading BEE (z80atlas at 16fc6c2a plus
its forensic-era `traced_replay.py`) as one of four independently-implemented substrates. I checked every
BEE-specific claim I could against `prometheus/z80atlas/*.py` (both the frozen 16fc6c2a copy and the current,
repaired tree) and the forensics documents. Findings:

1. **Nearly every specific BEE number in both reports is unsupported by anything committed to Git.** The evidence
   both reports cite is "845 preserved traced-birth logs" at a *local* Windows path
   (`C:\Users\James\z80atlas_forensics_2026-09-23_local\births`, archaeon/causal_lens/PORTABILITY01_REPORT.md:13,
   which V02_REGRESSION_REPORT.md builds directly on at line 29). `traced_replay.py`'s own docstring says per-birth
   detail "stays in LOCAL" (roles/Bellerophon/forensics_2026-09-23/tools/traced_replay.py:22). None of the raw
   traced-birth logs, the "845 runs, 28,964,089 births" aggregate, the specific per-run numbers in
   V02_REGRESSION_REPORT.md (e.g. lines 36-38's 44,773/170,767/17,959 split; lines 44-49's 817,352/847,000 split;
   line 102-103's r038751/r016299 breakdowns) or in T-004_RESULT.md (lines 24-25's r038751/r016299 rows) exist
   anywhere in the git-tracked repository. Internally the arithmetic is self-consistent (e.g.
   T-004_RESULT.md:24 27,083+21+1,059 = 28,163; 17,501+8,166+13,158 = 38,825), so I have no basis to say the
   *numbers* are wrong -- only that they are **not verifiable from Git**: BEE's own committed code/records cannot
   confirm or deny them. This is the single largest gap in both reports' BEE sections. **DERIVED** (checked by
   grepping the whole repository for the cited local paths and any equivalent committed receipt; none exists under
   `roles/Bellerophon/` or `archaeon/causal_lens/`).

2. **T-004_RESULT.md mislabels `own_steps`/`win_steps` as "native."** Its WHERE-row for BEE reads: "pc < L own /
   [L, 2L) window / elsewhere (native `by_own_code`, own/win steps)" (T-004_RESULT.md:16). Checked: `by_own_code`
   genuinely exists in the shipped engine's own `adjudication.py` (current `adjudication.py:64`,
   `own_code = sum(1 for _, pc in own if pc < L)`) -- that half of the claim is accurate. But `own_steps`/`win_steps`
   (the per-execution step-share accounting used for the WHERE reading of *execution time*, as opposed to *write
   location*) exist **only** inside `traced_replay.py`'s separate, hand-copied instrumented VM
   (`_ACC` dict, roles/Bellerophon/forensics_2026-09-23/tools/traced_replay.py:40,71-73). I grepped the actual
   shipped package (`prometheus/z80atlas/*.py`, both 16fc6c2a and current) for `own_steps`/`win_steps`: the only hit
   is an unrelated, coincidentally-named dict key `"win_steps": None` inside a physics-v3 exploit-probe structure
   (current `world.py:430`) that has nothing to do with step-share accounting -- `vm.Trace` (16fc6c2a:vm.py:57-76
   and the current version) has no such fields, and neither does `adjudication.py`. Calling step-share accounting
   "native" therefore overstates: it is bookkeeping in a bespoke, unshipped, forensics-only duplicate of the VM, not
   something the BEE engine itself records or computes. **CONFIRMED disagreement** (a provenance mislabelling, not a
   numeric one).

3. **"BEE's own traced VM, unmodified" (V02_REGRESSION_REPORT.md:11, echoing
   archaeon/causal_lens/PORTABILITY01_REPORT.md:13) is imprecise about what "unmodified" means.**
   `traced_replay.py._install()` explicitly **monkey-patches** `vm.execute` with "a line-for-line copy of
   vm.execute (frozen), with bookkeeping added" (roles/Bellerophon/forensics_2026-09-23/tools/traced_replay.py:54-56)
   -- it substitutes a hand-maintained duplicate function object, not the actual `prometheus/z80atlas/vm.execute`.
   The tool mitigates this by checking every replay's regenerated summary against the historically stored one and
   marking any divergence `TRACER_DIVERGED` (traced_replay.py:2-4), and the reports do cite that check (0/544, 0/300
   diverged, roles/Bellerophon/forensics_2026-09-23/POST_CAMPAIGN_FORENSICS.md:159). So "unmodified" is defensible
   as a claim about *verified behavioural equivalence*, and Bellerophon does own and author the tool -- but it is
   not literally the same code object as the shipped `vm.py`, and neither target report states that distinction.
   **Flag as an imprecision**, not a hard error, since the equivalence is independently checked and documented.

4. **The "lens class" taxonomy (AUTONOMOUS/DECOUPLED/CAPTURE/ORIGINATION/WRITER_MIXED_EXEC/UNRESOLVED) that both
   reports treat as an unquestioned baseline is Archaeon's invented category set, not BEE's native vocabulary --
   with one partial exception.** `archaeon/causal_lens/PORTABILITY01_REPORT.md:35-49` explicitly labels its own
   column "lens class"; grepping `prometheus/z80atlas/*.py` for these exact names finds none of them as native BEE
   fields or class names. BEE's genuinely native run/birth vocabulary is `mechanism` (one of the REPRO physics names
   plus `seed`/`transplant`/`pollination`/`init`, 16fc6c2a:world.py:92,167-198) and `material`
   (writer/target, 16fc6c2a:world.py:421-428). The one partial correspondence: the lens's `CAPTURE` category does
   map onto a genuinely native counter, `self.captures` (16fc6c2a:world.py:153,427), incremented for exactly the
   `material == "target"` events the lens calls CAPTURE -- so that one lens category is a formalized re-labelling of
   a real native concept, not an invention from nothing. The others (AUTONOMOUS, DECOUPLED, ORIGINATION,
   WRITER_MIXED_EXEC, UNRESOLVED) have no native counterpart at all. When V02_REGRESSION_REPORT.md and
   T-004_RESULT.md speak of "BEE AN1," "BEE CAPTURE," or (PORTABILITY01_REPORT.md:35) "native `is_sr`," part of what
   is being called BEE's own reading is in fact a third-party schema Archaeon built on top of BEE's genuinely native
   fields. (`is_sr` itself is not a field name anywhere in BEE's code either at 16fc6c2a or currently; it is a local
   Python variable inside `traced_replay.py`'s per-birth loop, `is_sr = is_sr_post and fid_pre >= 0.9`,
   roles/Bellerophon/forensics_2026-09-23/tools/traced_replay.py:228 -- a paraphrase, not a literal native field
   name.) **Flag as going beyond BEE's own records**, though the underlying computation is a defensible, checkable
   derivation from native fields, not a fabrication.

5. **V02_REGRESSION_REPORT.md's B6 claim about BEE's *current* native SR criterion is accurate, and I confirm it
   independently.** Lines 94-115 state BEE's native self-replication criterion is location-based (`pc < L`) and
   therefore cannot distinguish self-copied code executed from the window from genuinely foreign code. Checked
   against the current shipped `World._is_self_copy` (current `world.py:576-588`): it computes
   `own_code = sum(1 for pc in own if pc < L)` (line 586) -- exactly the location-based test the report describes,
   still true of the engine as it stands today, not merely of the historical forensics tool. **No disagreement;
   confirmed as described.**

6. **T-004_RESULT.md's treatment of `material` as "writer = WHO throughout" is consistent with the native code.**
   For every physics except `PAIR_EXECUTION`, the interacting/executing organism is unambiguous (`o`/`parent` in
   `_apply_reproduction`/`_register_offspring`, 16fc6c2a:world.py:394-431); `material` is a separate,
   fidelity-comparison-based label about *whose bytes* ended up in the child (16fc6c2a:world.py:421-428), never a
   record of who executed. The report's characterization is accurate here. **No disagreement.**

7. **"BEE quarantines the whole run" (echoing PORTABILITY01_REPORT.md:50-53, which V02_REGRESSION_REPORT.md's B6/D2
   rows build on) describes a *post-hoc adjudication rule*, not something the campaign that produced the 42
   transplant runs itself enforced.** At 16fc6c2a, `observatory.py`'s triggers/flags contain no "quarantine"
   concept at all (16fc6c2a:observatory.py:1-130, no such term). The rule that spontaneity adjudication requires
   `init_tapes` to be empty was added during forensics as defect-repair C9
   (roles/Bellerophon/forensics_2026-09-23/ISSUE_AND_REPAIR_LEDGER.md row C9) and lives in the *current*
   `adjudication.spontaneous(s, vec, has_init_tapes)` (current `adjudication.py:31-40`), which did not exist when
   the 42 runs were generated. Neither target report states that "BEE quarantines" refers to the repaired
   adjudication layer built after the fact, not to anything the running 72h campaign itself did. **Flag as an
   imprecision about which version of "BEE" is native.**

8. **Micro-benchmark numbers are unverifiable from Git.** V02_REGRESSION_REPORT.md:158 ("BEE: 3.54 us/birth (v0.1)
   vs 3.77 us/birth (v0.2)... with I/O the v0.1 figure was 13.78 us") cites no committed script or receipt under any
   path I was given; I cannot confirm or refute it. **Unverifiable, not necessarily wrong.**

9. **T-004_RESULT.md's "Still NOT_IDENTIFIABLE" claim about writes from `pc >= 2L` ("elsewhere") is structurally
   consistent with BEE's own address-space layout**, even though its specific counts (528,897 / 66,669) fall under
   item 1's unverifiability: the native layout genuinely reserves `[0,L)` own tape, `[L,2L)` neighbour window, and a
   distinct IO/scratch region starting at `IN_BASE = 0xE0` (16fc6c2a:vm.py:11-16,26-28) -- "elsewhere" names a real,
   structurally distinct region the harness itself defines. **No disagreement on structure; numbers unverifiable
   per item 1.**

10. **The `material` tie-break BEE itself uses is a different policy from the one the lens's "strict majority"
    language implies, but this is a legitimate difference in purpose, not an error.** V02_REGRESSION_REPORT.md:44
    ("the rest sit at exactly L/2, and v0.2 requires a strict majority") treats an exact 50/50 fidelity split as
    ambiguous for *continuity* purposes. BEE's own code already resolves that exact case, for a *different*
    purpose (who gets replication credit): `material` defaults to `"writer"` and is only overwritten by a **strict**
    `>` comparison (`if fid_target > fidelity`, 16fc6c2a:world.py:425) -- so BEE itself never treats an exact tie as
    ambiguous; it silently credits the writer. The two reports do not claim otherwise, so this is not a
    disagreement, but it is worth recording as a place where "BEE's own answer" and "the lens's answer" differ by
    design, for different questions, and a careless reading could conflate them.

---

## What could NOT be determined from Git, and why

- **Every specific BEE birth-level and run-level number in `V02_REGRESSION_REPORT.md` and `T-004_RESULT.md`**
  (the 233,499/44,773/170,767/17,959 split; 817,352 of 847,000; the r038751/r016299 tables; "845 runs,
  28,964,089 births"; the 606/341-run replay-identical counts) -- because the underlying evidence
  (traced-birth logs, per-run directories) was explicitly kept local to Windows machines
  (`C:\Users\James\z80atlas_forensics_2026-09-23_local\births`, `C:\Users\James\z80atlas_campaign_2026-09-19`,
  `C:\Users\James\z80atlas_grounding_2026-09-23`, `C:\Users\James\z80atlas_coupling_2026-09-24`) and never
  committed; only receipts, hashes, and the tools that produced them are in Git.
- **Whether the 63,247-run campaign's own `runs.jsonl`/`state.json` actually contain the exact figures the forensics
  reports quote** (e.g. "1,629 flag events", "49,412 families") -- I read and trust the tools that compute them
  (`tools/census.py`, `tools/rates.py`, etc. exist and match their stated logic on inspection) but did not re-run
  them against the (absent) raw campaign directory myself; this worker treats those figures as **DERIVED** by the
  forensics team, not independently re-verified by me.
- **Micro-benchmark timings** (V02_REGRESSION_REPORT.md s8) -- no committed script or receipt path was given for
  these under the paths in scope.
- **Whether `traced_replay.py`'s hand-copied VM is byte-for-byte identical to `vm.execute`** beyond the specific
  divergence checks the tool itself performs and reports (0/544, 0/300 diverged) -- I compared the two functions by
  eye (traced_replay.py:54-180 vs. 16fc6c2a:vm.py:78-201) and found them structurally parallel with provenance hooks
  added, but a byte-level diff of the two Python source files was not performed as part of this task.
- **The coupling-campaign's raw per-run evidence** (`C:/Users/James/z80atlas_coupling_2026-09-24`, `results.jsonl`,
  `PHASE2_PLAN.json`, etc., COUPLING_CAMPAIGN_REPORT.md:164-169) -- hashes only are committed; I did not and could
  not recompute the P1-P6 statistics myself.
- **Whether the operational/timing claims in `V02_REGRESSION_REPORT.md` line 12** ("BEE used at most 3 workers
  while Bellerophon's campaign held M2") match any process log -- no such log is in the paths I was given.

---

*Packages/tools installed by this worker: none. All analysis was read-only (`git show`, `Read`, `grep`).*
