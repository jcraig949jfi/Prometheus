# W1 — NPE (z80atlas) as a Lens on Reproduction and Heredity

Worker: W1-npe-lens. Disposable research pass, read-only over Git history plus preserved
records under `roles/Nestor/`. Branch: `worker/W1-npe-lens` (worktree of `~/Prometheus`,
based on `origin/main` as of 2026-09-27). No scientific code, frozen evidence, or verdicts
were modified; this document is new.

Label convention throughout: **NATIVE** = the engine's own code/records say it directly;
**DERIVED** = computed/traced by this worker from preserved records (diffs, cross-file
tracing, aggregation); **INFERRED** = this worker's interpretive reading.

Primary sources (all under `roles/Nestor/`, paths relative to repo root unless a
`git show <branch>:<path>` is noted):
- `campaigns/z80atlas-2026-09-19/{world.py,z8.py,observatory.py,anticheat.py,DEFECTS.md}` — original campaign
- `campaigns/z80atlas-verify-2026-09-22/{world.py,z8.py,z8taint.py,p11.py,P11_SPEC.md,PREREGISTRATION.md,constants.py,controls.py,anticheat.py,hypotheses.py,grammar.py,adjudicate.py,adjudicate_c9.py,specimens.py,H3_RULER_TOURNAMENT.json,FREEZE.json,MANIFEST_FROZEN.json,GATES_PREFREEZE.json,CALIBRATION.json,D14_PROBE.json,d14_probe.py,S4_TIMING.json,s4_timing.py,S4_CANDIDATE.md}` — verification/freeze campaign
- `campaigns/z80atlas-forensics-2026-09-23/{H4_AUTOPSY.md,S1A_FUNNEL.md,S1C_P11_REASSAY.md,S1C_BREAKDOWN.json,FROZEN_FUNNEL.json,REPLAY_FUNNEL.json,P11_REASSAY.json}` — self-attack campaign
- `campaigns/c9x-explore-2026-09-24/{CAMPAIGN_REPORT.md, ~50 x_*/c_* sub-experiment dirs}` — exploratory campaign
- `FINDINGS.md`, `STATUS.md`, `BACKLOG_H0H5.md`
- `prompts/2026-09-26_npe_window_donor_discovery/DIRECTIVE_VERBATIM.md`
- Remote branch `origin/nestor/s1-forensics-2026-09-23` (11 commits ahead of `origin/main`, NOT merged — read via `git show`)
- `archaeon/causal_lens/{V02_REGRESSION_REPORT.md, fossils_npe.py, lens_npe_from_evidence.py, adapters_v02.py, adapters_v03.py, adapters/npe.py}`
- `ops/campaigns/C-001/E-001/T-004_RESULT.md`

---

## WORLD

**Substrate.** NATIVE. One shared byte arena (`bytearray`), sized to a power of two,
divided into fixed-size slots; organisms occupy byte spans, not CA cells and not one
tape each. Module docstring: "one arena, several physics, no hidden reproduction
operator" (`campaigns/z80atlas-2026-09-19/world.py:1-25`). Arena construction:
`self.mem = bytearray(self.arena_size)` (`world.py:96-108`).

The CPU is a purpose-built Z80-like byte-addressable VM, not a real Z80 emulator:
byte-addressable executable memory, variable-length instructions, register/flag ops,
conditional control flow, memory read/write through register pointers, a block-copy
primitive (LDIR), no multiplication, no privileged copy operator, and every undefined
byte decodes as a one-byte NOP so mutation always lands on a runnable program
(`z8.py:1-43`). Registers `B,C,D,E,H,L,(HL),A` plus flags `Z,C` (`z8.py:47-52`);
`Ctx.regs/fz/fc` persist across time slices per organism (`world.py:544-559`,
`z8.py:115-119`) — an organism is a continuously running process, not a function call
(`world.py:16-18`).

**Update rule / time model.** NATIVE. Each `Runner.step()` (`world.py:826-852`) runs one
epoch: environment update → validation → pressure/ecology → execution (time-sliced
per-organism, or one `_pair_epoch` round for `PAIR_EXECUTION`) → external births if
configured → migration → aging → population cap → telemetry. Execution is time-sliced
per `_execute()` (`world.py:538-569`) with a per-epoch instruction budget
(`_slice_len`, `world.py:530-536`); CPU state carries across slices.

**World ops (the only channel by which an organism, not the runner, can cause a
descendant).** NATIVE, `z8.py:18-30`: `ALLOC` (request child buffer), `BIRTH` (declare
child), `SELF`/`GETPC` (self-location), `SENSE`, `SPLIT` (partial birth), `LDIR`/`LDDR`
(block copy). Whether a given cell grants these is a grammar factor (`self_location`,
`copy_primitive`, `world_ops` — `campaigns/z80atlas-verify-2026-09-22/grammar.py:50-67`).

**Sandbox / write policy.** NATIVE, `z8.py:32-35`, enforced in `_writable()`
(`z8.py:134-145`): `OWN` (writes outside own span dropped, counted), `ARENA` (any arena
address writable — used by the pair tape), `FREE` (own span or the world's declared
free window). Out-of-policy writes are counted (`writes_blocked`), never silently
permitted.

**Physical constants.** NATIVE. `REP_LEN = {Z8_64:64, Z8_32:32, Z8_SHARED:96,
Z8_SEPARATED:96, Z8_SLOTTED:64}`; `MUT_RATE = {LOW:0.002, MID:0.01, HIGH:0.04}`
per-byte, opcode-categorical vs operand-numeric-gradient (`world.py:291-357,
37-40`; moved to `campaigns/z80atlas-verify-2026-09-22/constants.py:28-58` in the
verify campaign). `CROSS_THRESH=0.90` (held-out competence threshold). `MIN_LEN=8,
SLOT_FACTOR=2`. Copy-mutation on LDIR/LDDR (`z8.py:384-386`). Energy economics under
`RESOURCE_GATED`/`METABOLIC`/`COMPETITION` (`world.py:683-695`). Verify-campaign
thresholds are hash-pinned in one object (`PINNED_SHA256`, `constants.py:68`) so no
threshold can silently drift — a direct repair of an earlier defect (S3-2) where
`CROSS`/`MARGIN` had drifted as separate literals across files (`constants.py:1-20`).

**Determinism.** DERIVED. Stochastic but seeded and fully reproducible:
`self.rng = random.Random((seed*1000003) ^ zlib.crc32(...))` (`world.py:88`); every
downstream draw (mutation, allocation order, recombination, P-11 victim bytes/copy
mutation) derives from this RNG or from `event_seed()` hashes of
`(seed, epoch, pair index, side, draw k)` (`p11.py:63-65`, `P11_SPEC.md:75-76`). This
replayability is load-bearing for the entire forensic apparatus (P-11 re-execution,
replay-match checks — see STRONGEST FINDINGS).

**Environment/"physics" a cell selects.** NATIVE,
`campaigns/z80atlas-verify-2026-09-22/grammar.py:26-114`: `world` ∈ {PAIR_TAPE,
SOUP_MEM, GRID, GRAPH}; `environment` ∈ {STATIC, NONSTATIONARY_SHIFT, COEVO_ENV,
RESOURCE_LIMITED}; `representation` ∈ {Z8_64, Z8_32, Z8_SHARED, Z8_SEPARATED,
Z8_SLOTTED}; `reproduction` ∈ {EXTERNAL, ENDOGENOUS_COPY, ENDOGENOUS_PARTIAL,
OVERWRITE, CONSTRUCTIVE, PAIR_EXECUTION}; `self_location` ∈ {PRIMITIVE, PC_RELATIVE,
NONE}; `copy_primitive` ∈ {BLOCK, BYTEWISE}; `pressure` (11 levels); `structure`
(niche/migration topology including `RESERVOIR`). A "cell" is one full factor
combination, drawn from a validity-constrained grammar (e.g.
`seeded_replicator_needs_self_location`, `grammar.py:174-179`).

**09-19 → 09-22 diff.** DERIVED (`diff -u` of both `world.py`/`z8.py`). Additive
instrumentation, not a changed instruction set or physics:
- Material-provenance/taint tracking: `z8taint.py` (new, 361 lines), "a line-for-line
  copy of `z8.run` that additionally carries a TAG with every byte value"
  (`z8taint.py:1-18`); `Org.orig`/`Org.reg_taint`, `track_material` flag (active only
  for `structure=="RESERVOIR" and reproduction=="PAIR_EXECUTION"`).
- P-11 causal-copy assay wired into `_pair_interact`: on top of the old
  write-count-only criterion, a re-execution against a randomized victim tests causal
  authorship (calls to `p11.assay`/`p11.ordinary_diagnostics`).
- Lineage entries become dict events (`"birth"`/`"migration"`) carrying
  `causal`/`causal_pred`/`p11` fields, replacing a truncated tuple tail;
  `lineage_complete`/`retain_full_lineage` new (true only for RESERVOIR cells).
- New: `ancestry_certificate()`, `material_certificate()`, `_mutated_orig()` (none
  exist in 09-19); new summary fields `max_ancestry_depth`,
  `max_causal_replication_depth`, `max_causal_replication_depth_literal`,
  `propagating_replicators`.
- New experimental knobs: `implant`/`implant_bytes` (H2), `migration_disabled`/
  `easy_niche_disabled` (H3 arms), `init_niche_policy` (P-8 balanced seeding),
  `output_gate`/`cue_cost` (H1).
- `z8.py` gains `out_gate_reads`/`out_suppressed` (H1 answer-gating) and
  `prov`/`prov_lit`/`who` provenance fields on `Ctx`, populated in `wr()` — `prov[a]`
  = context that last *changed* the byte; `prov_lit[a]` = context that last *wrote* it
  at all (the causal-vs-literal authorship distinction central to P-11).
- The core VM decode loop, opcode table, ALU, jumps, LDIR mechanics are byte-for-byte
  identical between the two `z8.py` versions apart from the above.

INFERRED: all stochastic behavior lives in the world layer around the VM; the VM's
instruction semantics are deterministic except for the RNG-driven copy-mutation flip
inside LDIR itself.

---

## ENTITY

**Candidate reproductive entity.** NATIVE. An organism (`class Org`, `world.py:50-77`)
is a byte span ("slot") in the shared arena plus bookkeeping: `oid, slot, length, pc,
regs, fz, fc, energy, age, anc, pid, born, comp, held, probe, niche, alive, fidelity,
repro_span, births, ops, last_tel` (verify campaign adds `orig`, `reg_taint`). The
"genome" is literally `mem[slot:slot+length]`, read via `_genome(org)`
(`world.py:188-189`): `return bytes(self.mem[org.slot:org.slot+org.length])`.

**Boundary definition.** DERIVED, three overlapping mechanisms:
1. Address range — `org.slot` (byte offset, not slot index; the 09-19 docstring warns
   this distinction once caused all 256 organisms to collide on offset 0,
   `world.py:102-105`) and `org.length`.
2. Ownership map — `self.slot_owner: dict[slot -> oid]` (`world.py:108`), the
   authoritative record of current slot holder.
3. Genome content/checksum — blake2b hash used for dedup/novelty/specimen collection
   (`world.py:958-976`), but **not** the authoritative identity for
   reproduction/lineage purposes; `oid`+slot is authoritative, genome hash is not.

Representation length fixed per cell (`REP_LEN`, 32–96 bytes); `slot_size = L *
SLOT_FACTOR(2)` — each organism's slot is twice its genome length. Genome seeding
(`_seed_genome()`, `world.py:191-201`): fully `RANDOM` bytes, a hand-crafted
task-solving ancestor, or `_replicator_bytes()` — a hand-assembled seed replicator
matched to the cell's granted primitives (`world.py:214-241`); padding uses random
(not zero) bytes to avoid a NOP-sled confound (`world.py:203-212`).

`P11_SPEC.md` and `PREREGISTRATION.md` exist only in the verify-2026-09-22 campaign
directory, not the 09-19 original (DERIVED, directory listing comparison) — the
formal entity/reproduction definitions were tightened only in the second pass.

**Specimens.** NATIVE, `campaigns/z80atlas-verify-2026-09-22/specimens.py:1-99`: 16
pre-committed "specimens" (organism genomes) drawn from the 09-19 predecessor's 1,031
admissible spontaneous-replicator runs, coverage-balanced over
`(reproduction, structure, representation)` strata (`specimens.py:9-18`); a later
rule (`select_p11`/`manifest_p11`, `specimens.py:148-210`) rebuilds the panel
restricted to P-11 *causal* survivors only.

---

## REPRODUCTION

Two distinct code paths can register a "birth"; the bar for calling one a genuine
*replication* tightens substantially between 09-19 and 09-22.

**Path 1 — private-slot endogenous birth (`_on_birth`, `world.py:467-527`).** NATIVE.
```
world.py:483-484  wrote_bytes = sum(child_bytes[i] != pre[i] ...); wrote = wrote_bytes > 0
world.py:507-517  fid = _fidelity(parent, g); is_repl = fid >= 0.90 and wrote_bytes >= 0.5*len(g)
```
A birth counts as replication iff (a) child genome ≥90% byte-identical to parent
(`_fidelity`, `world.py:980-985`) AND (b) the parent itself wrote ≥50% of the child's
bytes, measured against the slot's pre-ALLOC snapshot (`world.py:460-463`) — not a
zero-counter. Docstring: "REPLICATION REQUIRES EVIDENCE OF CAUSATION, NOT RESEMBLANCE"
(`world.py:513-517`) — guarding against a child merely resembling a parent because a
converged population left a dead relative's bytes in the slot. Verify campaign renames
the bare literals to `C["REPL_FIDELITY"]=0.90`, `C["REPL_WROTE_SHARE"]=0.50`
(`constants.py:34-35`); function unchanged in substance.

**Path 2 — pair-tape interaction (`_pair_epoch`/`_pair_interact`).** NATIVE.
09-19 predecessor criterion (`world.py:601-638`, `_pair_interact`):
```
fid_other >= 0.90 and fid_self < 0.90 and donor_wrote >= 0.25 * n
```
09-22 reimplements this verbatim as the gate (`p11.py:153-156`,
`predecessor_accepts`), then runs the load-bearing **P-11 causal assay**
(`p11.py:105-150`): three randomized-victim re-execution draws test C2 (rebuild:
victim reaches fidelity ≥0.90 to donor after re-running from a randomized state), C4
(authorship: ≥90% of donor-directed byte changes were last *changed* by donor's
context, via `prov`), C5 (matched control: with donor's off-span writes blocked, the
same randomized victim does *not* converge). A candidate is **P-11 causal** iff it
passes `predecessor_accepts` AND ≥2 of 3 draws pass all of C2∧C4∧C5
(`p11.py:135-147`). Preregistered prospectively in `P11_SPEC.md:16-47`, "written and
tested BEFORE any of the 1,031 predecessor cases were inspected" (`P11_SPEC.md:3`).
One documented ambiguity flagged by NPE itself for operator review: authorship can be
read as "last value change" (`prov`, primary) or "last write at all" (`prov_lit`,
mandatory sensitivity check, amendment A-16) — yielding 57 vs 48 causal survivors out
of 1,031 (`PREREGISTRATION.md:39-40`).

**Does the preregistered definition match the implementation?** DERIVED — yes,
closely: `world.py`'s `_pair_interact` calls `p11.predecessor_accepts` then `p11.assay`
exactly per spec, storing both `causal` (P-11) and `causal_pred` (predecessor) flags
per lineage edge.

**Path 3 — external births.** NATIVE, `world.py:640-668`, explicitly *not*
replication — "the population manager copies, as ordinary evolutionary runs do,"
never marked causal.

**Causal replication depth (does it propagate).** NATIVE/DERIVED.
`max_causal_replication_depth` = longest parent-child chain using only P-11-causal
edges, gated at `C["CAUSAL_DEPTH"]=5` (`constants.py:32`) for the H2 hypothesis.
Empirically: "Reconstruction shows depth 1 in 911 of 1,031 admissible runs"
(`campaigns/c9x-explore-2026-09-24/CAMPAIGN_REPORT.md:17`) — the overwhelming
majority of predecessor "replicators" were one-shot, non-propagating.

---

## HEREDITY

At least four distinct channels exist (INFERRED synthesis); only genome-byte
inheritance is under experimental contention across the whole 09-22/09-24 body of
work.

1. **Genome bytes, private-slot path.** NATIVE. Only channel is the organism's own
   writes into its ALLOC-granted slot (`FREE` policy sandbox); mutation
   (`_mutate`, `world.py:291-357`) applied as bytes are written at `BIRTH`. CPU
   register/flag state is **not** copied to children — a child gets a fresh `Org()`;
   only task-competence estimates (`comp/held/probe`) are explicitly carried over as
   a provisional measurement-schedule accommodation (`world.py:497-502`).

2. **Genome bytes, pair-tape path.** NATIVE. Both organisms co-execute on one shared
   ARENA-policy tape; whichever organism's writes end up in a half determines what is
   inherited — the P-11 assay exists specifically to test causal authorship of that
   inheritance.

3. **Energy.** NATIVE for `EXTERNAL` births only: `child.energy = parent.energy * 0.5`
   (`world.py:665`). Ordinary endogenous births in the frozen 09-22 engine do **not**
   inherit energy — `world._on_birth` never sets it, so newborns start at 0
   (`campaigns/c9x-explore-2026-09-24/x_energy_inherit/run_n.py:9-11`, an exploratory
   patch external to the frozen engine, not part of it). That patch
   (`x_energy_inherit/run_n.py:64-66`: `half = o.energy*0.5; o.energy -= half;
   child.energy += half`) produced a signal (BASE 1/19 cells reach depth≥2, INHERIT
   7/19; `x_energy_inherit/SUMMARY.json:1-13`) later confirmed as **C-ENERGY**: "child
   replication 20/40 vs 4/40, p=7e-5" (`CAMPAIGN_REPORT.md:24`) — newborn starvation
   (zero inherited energy, ~70-instruction copy cost) is a real barrier to sustained
   heredity under energy-scarce pressures, relieved by inheritance.

4. **Material provenance/taint (`z8taint.py`).** NATIVE, active only for
   `structure=="RESERVOIR" and reproduction=="PAIR_EXECUTION"` cells. Each byte
   *value* carries a tag naming the niche in which it was *made* (not who currently
   holds it); loads/moves/stores propagate the source's tag; LDIR/LDDR copy the tag
   with the byte (a copy-mutation flip makes new material, tagged to the executing
   organism's niche); computed values (ALU, INC/DEC, SENSE, SELF/GETPC return, task
   input) are tagged new material. Basis of the H3 ruler R3 "material certificate"
   (`material_certificate()`, `world.py`) — see RULER — replacing an earlier
   id-based ancestry certificate NPE itself showed was defeatable: "an organism keeps
   its id while its bytes are replaced (0.97→0.00 identity over 600 epochs with no
   lineage event)" (`PREREGISTRATION.md:48`, amendment A-24).

**Ancestry bookkeeping vs. actual material diverge — a central c9x-explore-2026-09-24
finding.** DERIVED. `anc` (ancestor id) tracks slot-lineage succession, not byte
content:
- `x_content/run_xc.py:5-8`: "the most frequent genomes of two founder-descended
  (`anc==0`) runaway populations differ from the founder at 58–62 of 64 bytes."
- `x_content/SUMMARY.json:2-11`: WEAK_SIGNAL; median founder-byte-share = 0.1343
  (own cell) / 0.2531 (foreign cell), both far below the 0.5 threshold.
- Yet `c_core` (CONFIRMED, `c_core/VERDICT.json`): two specific genome positions are
  almost universally conserved across 27 runaway populations — position 23–24
  (`ED 32` = `OP_SELF`) in 27/27, position 52–53 (`ED B0` = `LDIR`) in 25/27 (later
  files report 19/27 under a stricter count). `CAMPAIGN_REPORT.md:88-91`: "runaway
  populations are founder-descended in lineage but carry only 13-25% founder bytes;
  the founder material that almost every member keeps is the two world-op
  instructions, OP_SELF and LDIR... Heredity here conserves the replication
  machinery's key instructions and replaces the rest." Flagged by the operator
  (Aporia #621, `FINDINGS.md:376-379`) as exactly what purifying selection on a
  functional core plus drift predicts, not evidence for anything stronger; an earlier
  self-framing as "Selective-Irreversibility" evidence was explicitly **withdrawn**
  by operator directive 2026-09-26 (`FINDINGS.md:389-393`).

**Donor competence is a genome×cell joint property, not a genome-alone property.**
DERIVED, from paired sub-experiments:
- `x_donor_rate/SUMMARY.json:1-4` (SIGNAL): of 16 H2-panel donor genomes, one
  specimen (`7ae3...`) passes 96% of fresh-implant P-11 assays; two ~29%; twelve ~0%;
  Spearman(pass-rate, ATOMIC-arm any-copy share)=0.741.
- `x_donor_swap/SUMMARY.json` (WEAK_SIGNAL): transplanting the `7ae3` genome into 11
  other panel specimens' cells (erosion removed) gets runaways in only 3/11 foreign
  cells (`ffa6` 4/8, `9cba` 1/8, `e160` 1/8) vs control 3/8 — competence is joint,
  not portable alone.
- `x_swap_origin` vs `x_swap_ancestry` (reconciled `CAMPAIGN_REPORT.md:83-87`):
  foreign-cell runaways lie outside the transplanted founder's P-11-*certified*
  causal lineage, yet ARE `anc==0`-descended (0.99–1.0 share) — "certification breaks
  inside the lineage, it does not mark native lineages." Corroborated by `x_cert_break`
  (`FINDINGS.md:383-388`): ~5–16% of replication events inside runaway lineages are
  not P-11-certified; a per-edge break rate caps any "founder-rooted causal depth"
  reading at roughly `1/p` generations.

**Summary judgment (INFERRED):** the substrate supports genome-byte, energy, and
task-competence-estimate inheritance, but not CPU-register-state inheritance across
generations; and the central empirical result across the whole body of work is that
even confirmed "runaway heredity" populations conserve not the whole genome but
specifically the two instructions implementing the replication machinery itself
(`OP_SELF`, `LDIR`) — a minimal-replicase-like inheritance pattern — while the
lineage-bookkeeping field (`anc`) is only a slot-succession record, not a
content-fidelity guarantee.

---

## OBSERVABILITY

**Per-run record shape.** NATIVE, `observatory.py:9-15` (identical header in both
campaigns): `CONFIG.json` (frozen cell/seed/tier/grammar hash/parent run/control
role), `RESULT.json` (aggregated summary, anticheat flags, signals, timings),
`series.jsonl.gz` (per-epoch telemetry), `lineage.jsonl.gz` (parent pointers, birth
epochs, copy fidelity, reproductive span), `specimens.json.gz` (preserved genome bytes
+ disassembly). Disk-budget degradation thins these under pressure and records
`observatory_degraded` in `RESULT.json` rather than silently truncating; the verify
campaign exempts RESERVOIR runs from this via `lineage_complete`
(`observatory.py:91-99`).

**NATIVE (directly instrumented during simulation).** Live counters incremented in the
run loop (`self.ct[...]`: `births_endogenous`, `births_external`, `deaths`,
`alloc_calls`, `writes_blocked`, `validation_writes`, `copy_bytes`, `migrations`,
`p11_events`). Per-epoch telemetry snapshot (`_telemetry`, `world.py:1157-1183`,
sampled every `snap_every//4` epochs): `pop`, `births_endo`, `births_ext`, `deaths`
(direct counter reads); `comp_mean`/`comp_max`, `held_best`, `probe_best`, `len_mean`,
`age_mean`, `uniq` (blake2b-distinct genome count), `dom_share`, `fid_mean`,
`span_mean`, `entropy`, `energy_mean`. `_fidelity(a,b)` (`world.py:1373-1378`) is a
direct byte-level per-comparison measurement. `D14_PROBE.json`/`d14_probe.py`:
purpose-built instrumentation that monkeypatches `Runner._place` to record each
organism's birth-genome bytes, then at run end computes fidelity-to-own-birth-genome
for organisms alive but never a lineage child ("zero-edge" case). Result (verified):
`zero_edge_alive=128`, `fidelity_to_own_birth_genome_median=0.0`,
`share_below_0.10=1.0` over 600 epochs on both H3 pinned cells — organism identity
(oid) does **not** track genome bytes on the pair tape. This NATIVE finding directly
motivated choosing ruler R3 (material tracking) over R0 (id tracking) — see RULER.
`S4_TIMING.json`/`s4_timing.py`: wall-clock-only instrumentation, deliberately
stripped of any outcome field ("timing cannot become a pilot of the result",
`s4_timing.py:8-9`), run on off-manifest seeds (`TIMING_SEED=9_900_001`) so timing runs
can't leak into the frozen result set.

**DERIVED (computed in `summary()` from native counters/series, same run, pre-
adjudication).** `world.py:1214-1327`: `replication_rate = births_endogenous /
max(1,slices)`; `entropy_drop`; `max_ancestry_depth`/`max_causal_replication_depth`/
`n_lineages_depth_ge_2/5`/`propagating_replicators` (from `_lineage_graph()` +
`_depths()`); `ancestry_certificate`/`material_certificate`; `crossed_ever` vs
`crossed_at_final` kept explicitly separate (repair "P-3"); `flags`/`voided` via
`anticheat.scan()` — a pure function of the already-derived summary, not of raw
telemetry.

**Explicitly non-scoring / archival-only.** `serendipity()` (`observatory.py:142-190`,
both campaigns): "Pure function of the record... They archive; they never score" —
compares first-quarter vs last-quarter series means to flag qualitative shifts for
specimen preservation only, never used to adjudicate a run.

---

## RULER

**Chain of custody.** DERIVED. `world.py` writes NATIVE counters + DERIVED summary
(incl. certificates/flags) → `anticheat.py` (pure function of the summary, artifact
filter) → `hypotheses.py` (threshold decision rules, operator-ruled 2026-09-24,
converting bundle results to verdicts) → `adjudicate_c9.py` (glues bundle
store+manifest to `hypotheses.py` → `ADJUDICATION_C9.json`) / `adjudicate.py`
(parallel, older flag-level adjudicator off `INDEX.jsonl`).

**`anticheat.py` — artifact/exploit guards.** NATIVE, byte-identical across both
campaigns. Ten flags with severity (`anticheat.py:33-36`): `RUNNER_BIRTH` (critical —
the scheduler itself created a descendant; "the one failure that would void the whole
campaign"), `VALIDATION_WRITE` (critical), `SANDBOX_ESCAPE` (high — blocked writes
outside policy window, "attempts are evidence"), `EVALUATOR_LEAKAGE` (high — comp≥0.80
with 0 reads), `STALE_RESIDUE_BIRTH` (high — birth with no copy but viable, heredity
via leftover bytes not copying), `NONHERITABLE_STATE` (high), `HELDOUT_GAP` (medium —
memorization not generalization), `NONTERMINATION_WIN` (medium), `ALLOC_DENIAL` (low),
`IMMORTAL` (low). `voids_run()` (`anticheat.py:114-117`): any critical flag means the
run "cannot support any claim about reproduction" — kept and labelled, not deleted.

**`controls.py` — the calibration gate.** NATIVE, `controls.py:1-18`: 5 positive/
negative controls against the real engine, gating campaign launch. Includes a
hand-written seeded replicator that must replicate at fidelity ≥`REPL_FIDELITY`(0.90)
(`control_replication`) AND must *not* replicate when placed outside its hardcoded
address (negative case, `controls.py:92-118`); a task-solving witness that must reach
comp=held=1.0 (`control_witness`); an EXTERNAL-reproduction control that must be able
to cross a one-edit constant else "the mutation model is too weak to resolve any
accessibility difference and every later negative would be vacuous"
(`control_external_evolves`); a seeded replicator among random bytes that must invade
(`control_invasion`); and the campaign-voiding negative control — across four
endogenous physics with RANDOM seeding, the runner itself must create **zero**
external births (`control_no_runner_births`). Verified: `CALIBRATION.json` — 10/10
PASS, `gate: PASS`.

**`hypotheses.py` — the decision rules (operator-ruled 2026-09-24).** NATIVE.
- H1 (`:76-102`): gate main effect / cost×gate interaction on `held_max_final`,
  threshold `C["H1_THRESHOLD"]=0.15`.
- H2 (`:21-69`): per-seed "reaches" iff `max_causal_replication_depth >=
  C["CAUSAL_DEPTH"]`(5); specimen SUPPORTS iff arm B reaches ≥8/16 seeds AND arm C
  reaches ≤2/16; panel PANEL_POSITIVE iff ≥2 supporting specimens from different
  strata.
- H3 (`:113-138`): RESERVOIR_SUPPORTED iff arm A has ≥5 material certificates AND A's
  rate exceeds B and C by ≥0.20.
All thresholds live in one hash-pinned object (`constants.py`), built specifically to
stop a prior defect (S3-2) where thresholds had drifted as separate literals.

**`H3_RULER_TOURNAMENT.json` — the literal tournament that decided the causal-event
ruler.** NATIVE, read in full. Four candidate certificate definitions scored against 9
adversarial fixtures driven through the real pair-interaction code
(`tests/test_h3_material.py:1-24`): `R0_id` (id-chain certificate, pre-C9-D14),
`R1_founder_fidelity` (founder-birth-genome resemblance ≥0.50), `R2_causal_edge_window`
(≥1 P-11-causal edge within 50 epochs), `R3_material` (crossing genome ≥0.50
easy-niche MATERIAL by VM dataflow tracking, independent of lineage identity). Final
scores out of 9 correct fixture calls: R0=4, R1=7, R2=4, **R3=9 (perfect)**. Selected:
`R3_material`, at `share_threshold=0.5` (`C["H3_MATERIAL_SHARE"]`). This is the direct
answer to "what decided an event was causal": the crossing genome must be ≥50%
easy-niche-made material as tracked through actual VM dataflow that survives
mutation/recombination — not organism identity (R0), not lineage-edge proximity (R2).
Motivated by the NATIVE D14_PROBE finding that identity tracks nothing on the pair
tape.

**Preregistration (decision rule fixed before data collection).** NATIVE,
`PREREGISTRATION.md:1-403`: repairs P-1 through P-11 with tests required to fail
unrepaired / pass repaired (`:69-226`); H1/H2/H3 rules matching `hypotheses.py`
exactly (`:229-333`); a "what failure looks like" section defining null outcomes as
publishable in advance, precluding post-hoc reframing (`:356-368`); a 6-row
gate-before-launch checklist (`:372-402`).

**Freeze gate chain.** NATIVE. `GATES_PREFREEZE.json`: 14/14 PASS, including VM
selftest, P1-P11 repairs, T-H3-MAT material ruler tournament, T-MAN/T-HASH manifest+
hash reproducibility. `CALIBRATION.json`: 10/10 PASS. `FREEZE.json`: `status: FROZEN`,
`frozen_at: 2026-09-24T07:05:54`, protocol `cycle9-verify-3`, `n_runs: 1200`,
`n_bundles: 380`, `by_hypothesis: {H1:60, H2:256, H3:64, H4:0}`. `MANIFEST_FROZEN.json`:
380 bundles matching that protocol version.

**Derived tags gating eligibility.** NATIVE, `grammar.py:269-280` (`derived(cell)`):
`endogenous`, `spontaneity_test` (endogenous AND RANDOM seeding), `constant_kind`,
`has_task`, `moat`, `seeded_instrument` — gate which flags/certificates are even
eligible (e.g. RUNNER_BIRTH only checked for endogenous cells; a reservoir claim is
INADMISSIBLE if `seeded_instrument` or not `endogenous`).

---

## STRONGEST FINDINGS

The forensic pass (`z80atlas-forensics-2026-09-23`, "S1-A/B/C") first re-ran the
frozen campaign as byte-for-byte replays (NATIVE: `S1A_FUNNEL.md:9` — "256 of 256
REPLAY_MATCH"; `S1C_P11_REASSAY.md:17` — "REPLAY_MATCH 1,031/1,031") before applying
stricter adversarial criteria — i.e., reproducibility itself was verified before any
re-adjudication.

**Killed / withdrawn:**
- **A-4 "endogenous-only accessibility" — WITHDRAWN.** The single admissible instance
  was autopsied (`H4_AUTOPSY.md:9-21`): the endogenous arm had zero ALLOC calls, zero
  births, zero deaths, zero mutations in 4,000 epochs — the population never changed;
  its "held" score moved only because the coevolving task environment shifted under
  it. The "matched" control was inherited from a sibling run at a different tier/seed
  (defect Z80A-D04, `:52-62`); the true matched control crossed *earlier* (epoch 48)
  than the endogenous arm (epoch 636). Of 65 flagged instances, 64 were adjudicated
  against an unmatched control; the one ADMISSIBLE case is the one just withdrawn
  (`FINDINGS.md:197-201`).
- **A-1 "spontaneous replication from random bytes" — narrowed from 1,031 to 57 (48
  literal).** No lineage reaches depth 3 (`S1C_P11_REASSAY.md:36-44`). Root cause
  (Z80A-D05, `:66-74`): under `RECOMBINATION`, the world's own recombination operator
  spliced the victim with a random living organism *after* the donor-victim
  comparison, crediting 6,287 of 6,547 events to the mutation operator, not the
  donor. Final honest statement (`:82-85`): "57 of 1,031 random-start pair-tape runs
  contain at least one interaction in which one organism can rebuild a randomized
  partner to ≥0.90 fidelity by its own writes; none of those lineages reaches depth
  3."
- **A-5, A-6, A-3 — WITHDRAWN** as unanswerable/misattributed (`FINDINGS.md:65-99`).

**What held up:**
- **A-2 matched-pair effects — HOLDS.** 10,741 Hamming-distance-1 pairs; recomputation
  from the index reproduces the packet exactly across all 28 axes (`FINDINGS.md:43-48`).
- **E-1 "non-pair physics never searched" — HOLDS.** 907 FREE-policy random-start runs
  + 192 forensic replays: zero births of any kind in
  ENDOGENOUS_COPY/PARTIAL/CONSTRUCTIVE physics (362k successful ALLOCs, 0 births);
  in OVERWRITE physics, 656 replayed births, none at fidelity ≥0.90
  (`S1A_FUNNEL.md:28-31`, `FINDINGS.md:181-186`).
- **E-2 P-11 causal-copy criterion — HOLDS as an instrument.** Committed and tested
  before use; 14/14 on a targeted assay (`FINDINGS.md:188-190`).
- The **methodological lessons** (`FINDINGS.md:398-433`) are a durable output in their
  own right: 12 named defect classes (e.g. "a guard that cannot fire proves nothing,"
  "a control inherited from a sibling is not a control," "measure a copy where it
  happens").

**Net verdict (DERIVED):** neither of the original campaign's two headline claims
survived at its original strength — A-1 fell from "1,031 replicators" to "57 causal,
depth ≤2"; A-4 fell to fully withdrawn. What survived was the narrower re-adjudicated
residue plus the instrumentation built to find it (P-11, the replay-match protocol,
the taint/material tracking).

---

## REINTERPRETATIONS

The forensic pass reframed the guiding question as (DERIVED,
`CAMPAIGN_REPORT.md:37-39`): *"why is sustained heredity so much harder than making
one convincing copy, and where does the transition fail?"* `c9x-explore-2026-09-24`
ran ~43 experiment-graph nodes chasing this, with 8 promoted CONFIRM claims (frozen,
fresh-seed, pre-declared-rule tests, `CAMPAIGN_REPORT.md:19-31`).

- **Non-pair heredity is achievable — but only in an artificially permissive world,
  reversing the "dead end" reading of E-1.** Chain: **C-SELFLOC** (self-location
  gates heredity: depth≥3 in 13/36 vs 0/36, p=1.6e-10) → **C-ENERGY** (depth-1 wall =
  newborn starvation; conserved half-energy transfer: 20/40 vs 4/40, p=7e-5) →
  **C-DENSE** (denser ALLOC/LDIR/BIRTH encoding makes spontaneous replication from
  random bytes appear: 13/40 vs 0/40, p=3.8e-5) → **C-ABLATE** (self-location and
  in-place search each necessary; energy-for-depth not confirmed) (`:42-51`).
- **The pair-tape "replicators" reinterpreted from "mostly artifact" to
  "artifact-suppressed real phenomenon."** With recombination splicing turned off,
  **C-RUNAWAY** shows genuine runaway causal heredity in one specimen's cell (7/150
  vs 0/150, p=0.0073, max depth 549 vs 13) — the same operator that manufactured 94%
  of the fake replicators (Z80A-D05) also suppresses real ones from running away
  (`FINDINGS.md:280-289`, `CAMPAIGN_REPORT.md:52-57`).
- **Establishment, not encoding, becomes the new bottleneck once acquisition is
  solved.** C-CRITICAL-MASS → X-DOSE-CURVE (clean null: founders are independent
  ~13% lottery tickets, not cooperative) → X-TICKET/X-STALL/X-STALL-F0 identify
  tape-write erosion (~5%/byte/epoch, ~25x nominal mutation) as the actual killer of
  stalled lineages → C-ATOMIC C1 (fixing it: runaways 46/80 vs 1/80, p=4e-17) but C2
  generality fails (1/120 vs 0/120 across the other 15 panel specimens) — donor
  competence is a property of genome×cell, not genome alone (see HEREDITY;
  `FINDINGS.md:328-334`).
- **Certification is reinterpreted as bounded, not absolute.** X-CERT-BREAK: ~5–16%
  of replication events inside runaway lineages are not P-11-certified, capping any
  "founder-rooted causal-depth" reading at ~1/p generations — meaning earlier
  NATIVE-vs-certified-lineage-only distinctions measured luck of an unbroken run, not
  a different kind of heredity (`FINDINGS.md:383-388`).
- **Not yet merged to main:** remote branch `origin/nestor/s1-forensics-2026-09-23`
  (11 commits ahead of `origin/main`, DERIVED from `git log
  origin/main..origin/nestor/s1-forensics-2026-09-23`) answers the 2026-09-26
  donor-discovery directive
  (`prompts/2026-09-26_npe_window_donor_discovery/DIRECTIVE_VERBATIM.md:43`): "How do
  competent hereditary donors arise from non-competent starting material, and what
  barrier currently controls that transition?" Per the branch's `W1_REPORT.md`/
  `FINDINGS.md` (accessed via `git show`, not present in this worktree):
  **C-DENSE-COPY CONFIRMED** (1/64→39/64, p=1e-14: donor *acquisition* gated by
  encoding accessibility of block-copy, not presence); **C-STATELESS-FFA6 CONFIRMED**
  (0.33→0.81, p=3e-5, one cell only): *establishment* gated by carried
  execution-register-state persistence — a genome competent from a fresh start
  "self-poisons" after its own first execution. A new failure mode is named: a
  SELF-free copier (LDIR/LDDR + incidental register state, no OP_SELF) arose in the
  one n=1 acquisition event, showing the earlier "requires SELF+LDIR" ruler was too
  narrow. **Not yet frozen/merged as of this snapshot — flag as provisional.**

---

## ATTENTION

**Host dependence.** Reproduction competence is not a portable property of a genome —
it is joint with the host cell's physics. `x_donor_swap` (WEAK_SIGNAL): the single
most-competent donor genome (`7ae3`, 96% fresh-implant P-11 pass rate) produces
runaways in only 3 of 11 foreign cells when transplanted, at rates far below its home
cell's. The not-yet-merged W1 window sharpens this further: `C-STATELESS-FFA6`
(establishment gated by register-state persistence) confirmed in exactly one cell
(`ffa6`) and explicitly not confirmed in the other tested cell (`7ae3`) — the same
genome that is the best *donor* is not where the *establishment* mechanism was
confirmed. Host (cell/niche/physics) dependence is therefore load-bearing at both the
acquisition and establishment stages, not an incidental variable.

**Self vs foreign material.** The taint system (`z8taint.py`) tags material by where
it was *made* (niche of origin), not by which organism currently carries it — this is
the only mechanism in NPE that distinguishes "self" from "foreign" byte-for-byte
rather than by lineage bookkeeping. The R3 material certificate (H3 ruler,
`share_threshold=0.5`) formalizes "foreign" as ≥50% material made outside the
organism's home (easy) niche. Separately, `x_content`/`c_core` show that even within a
single founder-descended lineage, "self" (founder-original) material erodes to
13–25% while two specific instructions (OP_SELF, LDIR) persist — i.e. at the
byte level, almost everything in a "self" lineage is actually foreign-origin material
by the time it's observed, except the replication machinery itself.

**Acquisition vs maintenance of replication.** These are explicitly separated as
distinct barriers in the still-unmerged W1 window's barrier map (DERIVED from branch
`origin/nestor/s1-forensics-2026-09-23`): variation → donor **acquisition** (relieved
by encoding accessibility, C-DENSE-COPY) → causal copy/**establishment** (~0.4 base
rate, gated by register-state persistence, C-STATELESS-FFA6) → **sustained** heredity
(gated separately again — X-CERT-BREAK shows ~5–16% per-edge certification failure
even once a lineage is running, and X-TICKET/X-STALL show tape-write erosion kills
established lineages independent of whether they ever acquired competence). NPE's own
data therefore treats "can copy once" (acquisition), "copy is causally certified"
(establishment), and "keeps copying across generations" (maintenance) as three
separately-measured, separately-failing stages — not one on/off property.

**Code execution vs material inheritance.** NPE's central late-stage finding (HEREDITY
above) is that these come apart: `anc` (lineage/execution-slot succession) says a
population is "founder-descended," while byte-content analysis (`x_content`) shows
only 13–25% of the founder's actual material survives. What is conserved is not the
genome-as-executed-history but two specific instructions (OP_SELF, LDIR) — i.e. code
*identity* (which slot-lineage a population's execution history traces to) and
material inheritance (which bytes it is actually made of) are empirically
dissociable, and NPE's tooling (taint tracking, R3 material certificate) was built
specifically because the id/lineage-based certificate (R0) was shown to be gameable
(D14_PROBE: fidelity-to-own-birth-genome median 0.0 while identity/oid is preserved).

**Reproductive architecture.** Two structurally different architectures exist in one
substrate: (a) private-slot endogenous copying (ALLOC→write→BIRTH, sandboxed to own
span, OWN/FREE write policy) and (b) pair-tape co-execution/overwrite (two organisms
sharing one ARENA-writable tape, "reproduction" arising as one organism overwriting
another with materially traceable bytes). These are not variants of one mechanism —
architecture (a) never produced a single confirmed replication event across the
entire body of work under ENDOGENOUS_COPY/PARTIAL/CONSTRUCTIVE physics (E-1: 362k
ALLOCs, 0 births) until the artificially permissive c9x-explore conditions
(self-location + energy inheritance + denser encoding) were added; architecture (b)
is where essentially all of NPE's confirmed causal-copy evidence (P-11 survivors,
C-RUNAWAY) originates. The "reproductive entity" is thus better described, on this
evidence, as an emergent property of the pair-tape interaction architecture
specifically, not of the VM/genome model in general.

**Endogenous vs externally supplied mechanisms.** The base substrate as frozen at
verify-2026-09-22 does not supply energy inheritance, dense-enough world-op encoding,
or self-location by default for most cells — each was later shown (c9x-explore) to be
a necessary, and in combination sufficient, external addition for non-pair heredity to
occur at all. This means NPE's most permissive confirmed replication regime
(C-DENSE/C-SELFLOC/C-ENERGY combined) depends on experimenter-supplied physics
choices, not on properties that emerge unaided from a "neutral" random-byte start;
the anticheat system's `RUNNER_BIRTH`/`SANDBOX_ESCAPE` critical flags exist precisely
to catch the case where such supplied mechanisms cross the line into the runner
itself performing the reproduction rather than the organism. Every confirmed causal
result in this document passed `control_no_runner_births` and had zero critical
anticheat flags in its bundle (frozen record; `CALIBRATION.json` gate PASS,
`FREEZE.json` status FROZEN) — the endogenous/external distinction is thus enforced
structurally, not just interpretively, by the ruler chain.

---

## SECOND PART — Cross-check against archaeon/causal_lens and ops/campaigns reports

Sources read in full: `archaeon/causal_lens/V02_REGRESSION_REPORT.md` (NPE sections)
and `ops/campaigns/C-001/E-001/T-004_RESULT.md` (NPE rows), plus spot checks of
`fossils_npe.py`, `lens_npe_from_evidence.py`, `adapters_v02.py`, `adapters_v03.py`,
`adapters/npe.py`.

### Points of disagreement, overreach, or unsupported extension

1. **The single most consequential disagreement.** DERIVED, category: conflicts with
   NPE's own framing. Both `V02_REGRESSION_REPORT.md` (§3 "AN3 host-conditioned
   reproduction", `V02...md:55-66`) and `T-004_RESULT.md` (§"Host-conditioning and
   cross-execution", `:28-34`, `:46`) build their "host-conditioned reproduction...
   survives; mechanistic lead" claim over a population of **34 "pair-tape births"**
   gated only by NPE's *weak legacy predecessor criterion*
   (`predecessor_accepts`/`world.py` pair-interact gate), not by NPE's own stricter
   P-11 causal pass. The AN3/AN8 "NECESSITY" leg is built from
   `fid_donor_disabled_ordinary` — a field NPE's own `p11.py` function
   `ordinary_diagnostics` is explicitly docstringed as producing **"Diagnostics on the
   OBSERVED event (not criteria)"**. The adapter code admits this outright: `adapters/
   npe.py:11-15` — "native verdict fields (`causal`, `causal_pred`, p11 `pass`,
   `pass_literal`, `C2`, `C4`, `C5`, `draws_passed`) are never read by the lens rules
   below." Meanwhile NPE's own comparable measurement over the full corpus (not just
   one specimen) found only **57 of 1,031** (~5.5%) predecessor-admissible pair
   events survive as P-11-causal (`FINDINGS.md:192-195`, "STRONGEST FINDINGS" above).
   Neither target document surfaces to the reader that "births" here means
   "predecessor-admissible," not "P-11-causal," nor that one whole leg of the
   host-conditioning test rests on a field NPE's authors declined to certify as
   decisive. This is unsupported extension bordering on disagreement: NPE's own
   records would predict such a claim, if built on the same denominator NPE itself
   uses (P-11 causal survivors), should apply to a tiny handful of events at most, not
   16 of 34.

2. **"REPAIRED... RESOLVES BY DISTINCTION" for body/identity (FF-11, `V02...md:79-81,
   88`).** DERIVED, category: goes beyond NPE's own status. NPE's own tracked defect
   ledger (`FINDINGS.md` C9-D14) explicitly leaves the underlying validity concern
   ("the H3 certificate follows id, so it certifies identity, not heredity") **open,
   freeze stopped** — NPE never declared this "repaired" via a body/identity
   distinction; NPE's actual fix for the same underlying problem was a *different*
   repair, the R3 material certificate (see RULER, HEREDITY), which the target
   documents' body/identity framing does not mention or reconcile with. Calling this
   "REPAIRED" overstates closure relative to NPE's own open-defect status.

3. **"4 distinct P-11 tests" (`V02...md:91`, portability row `:150`).** DERIVED,
   category: overstates NPE's own criterion count. NPE's `P11_SPEC.md` defines
   **three** pass criteria (C2, C4, C5); the "4th" folds in the same
   `fid_donor_disabled_ordinary`-based NECESSITY leg flagged in point 1 as a
   diagnostic, not a criterion, in NPE's own code. The count silently mixes 3
   NPE-certified tests with 1 Archaeon-manufactured one.

4. **AN4 "transplant minority 5/24... v0.1 over-claimed" (`V02...md:132`).**
   INFERRED/unverified — could not trace the specific counts (5/24, 7/24) to a
   specific Nestor source file in the time available; the general vocabulary
   (TRANSPLANT = ACTUAL_GENOME implant) matches `PREREGISTRATION.md` A-17/A-20
   (arm B/C implant design), so the framing is NATIVE-grounded but the numbers
   themselves are unconfirmed against NPE's own output — flagged as a gap, not a
   confirmed disagreement.

5. **T-003 cross-execution figures — "WHO != WHAT in 127 of 481 directed writes
   (26.4%)", "46% vs 11%" (`T-004_RESULT.md:17-18,25,28-34`).** INFERRED/unverified.
   These derive from a T-003 probe not covered by the files this pass could read in
   depth (T-003 script itself was not located/verified). The anchoring claim ("34/34
   lineage identical to preserved replays," `T-004_RESULT.md:5-6`) is consistent with
   NPE's own replay-match guarantees (STRONGEST FINDINGS: "256 of 256 REPLAY_MATCH"),
   so the underlying replay methodology is credible, but the specific percentages
   could not be independently reproduced from NPE's own records in this pass.

6. **Performance figures ("NPE: 36 runs in 0.4 s," "NPE arm replay 175-212 s",
   `V02...md:161,166`).** Not evaluated as a substantive NPE claim — these describe
   Archaeon's own replay-harness runtime, not NPE's reproduction/heredity model; no
   disagreement assessed.

7. **Points that DO hold up against NPE's own records (for contrast, not overreach):**
   the WHO-vs-WHAT correction itself (`prov`/`prov_lit` = authorship/WHO, not
   material/WHAT) matches `P11_SPEC.md:54-63` exactly and is a genuine, NPE-consistent
   self-correction by Archaeon of its own earlier v0.1 misreading; "NPE donor body:
   the slot is not recorded" (`T-004_RESULT.md:54`) matches the adapter's own honest
   NOT_IDENTIFIABLE accounting and NPE's observer-only integration; and the
   single-specimen scope caveat ("34 events and one specimen," `V02...md:186`) is
   self-disclosed and consistent with NPE's own repeated practice of not
   generalizing past one panel specimen (e.g. `FINDINGS.md` E-9 H2).

---

## WHAT COULD NOT BE DETERMINED FROM GIT, AND WHY

- **The exact T-003 probe script and its numeric outputs** (26.4% WHO≠WHAT, 46% vs
  11% cross-execution split cited in `ops/campaigns/C-001/E-001/T-004_RESULT.md`)
  were not located/verified in this pass; the file wasn't in the set explicitly
  scoped for deep reading and time did not permit a fuller side search. Flagged
  INFERRED/unverified above rather than asserted either way.
- **AN4's specific transplant counts (5/24, 7/24)** in `V02_REGRESSION_REPORT.md:132`
  could not be traced to a specific Nestor source file; only the general vocabulary
  (arm B/C implant design) was confirmed against `PREREGISTRATION.md`.
- **The not-yet-merged `origin/nestor/s1-forensics-2026-09-23` branch's W1 donor-
  discovery findings** (C-DENSE-COPY, C-STATELESS-FFA6) were read via `git show` but
  are, by the branch's own status, not yet frozen/merged/adjudicated by the same gate
  chain (FREEZE/CALIBRATION) applied to the rest of this document — treated as
  provisional throughout and explicitly flagged as such rather than folded into
  STRONGEST FINDINGS.
- **`origin/nestor/c3-holdout-d-2026-09-25`** was identified but not pursued — its own
  `STATUS.md` states it is an unrelated Cosmos-delegation holdout-prediction seal
  awaiting external predictions, out of scope for this lens.
- **The 09-19 campaign's own `DEFECTS.md` and `REPORT.html`** were not read in depth
  (only referenced by directory listing); some 09-19-specific defect history may be
  missing from the WORLD/ENTITY diff account, which relied primarily on `diff -u`
  between the two campaigns' `world.py`/`z8.py`.
- **Full read of all ~50 `x_*`/`c_*` sub-experiment directories in `c9x-explore-
  2026-09-24`** was not performed exhaustively; research prioritized breadth via each
  directory's summary/report file rather than its full code, per the scale of the
  task. A handful of directories not named in REINTERPRETATIONS/HEREDITY above were
  not individually characterized.
- **Independent re-execution of any NPE run or the archaeon adapters** was not
  attempted (out of scope: read-only analysis per task instructions, and compute
  budget is a 4-core/7GB laptop) — all claims rest on reading preserved records and
  code, not on reproducing runs.

No packages were installed during this research pass.
