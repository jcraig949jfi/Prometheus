# Z80 x Atlas combinatorial campaign - preregistration

Campaign id: z80atlas-2026-09-19
Seat: Nestor. Branch: nestor/sidequest-graphworld-2026-09-14. Host python: H:\Python312 (3.12).

GRAMMAR_SHA256: 570c8037ccf4f86d06bc7ef2a8263dab88fbd6d2bf430cbe52f346c8eb56c901

## Scope

This is computational artificial-life and algorithm-search research: integer programs on a
bounded virtual machine, search operators over byte strings, and population dynamics in
simulated worlds. There are no living organisms, no biological materials, no wet-lab
procedures, no pathogens, no genetic engineering, no biological sequence design and no
physical-world biological experimentation of any kind. Words like reproduction, lineage
and organism denote objects in the simulator and nothing else.

## The question

Which combinations of reproductive physics, representation topology, ecological structure
and environmental pressure create evolutionary paths to computations that are inaccessible
under ordinary externally managed reproduction?

The campaign inherits a specific, measured obstruction from cycle 8 of the CW01 loop: an
identity plateau whose organisms answer before reading the cue, four edits away from a
conditional program across a valley of zero fitness, with no beneficial one-edit or
two-edit mutant anywhere in an exhaustive census. That obstruction is rebuilt here in a
byte substrate and crossed with executable heredity, ecology and representation.

## What is frozen, and how

HASH ENFORCED. The factor grammar - factors, levels, declared constraints, control axes,
compute tiers - is hashed. run_campaign.py refuses to start unless grammar.grammar_hash()
equals the value above, and refuses to resume a campaign whose hash differs. The producer
can only assemble cells from this grammar, so no experiment semantics can be created while
the campaign runs.

PROSE DECLARED (not hash enforced, recorded here before launch):

- Stages by elapsed fraction of the 72 hours: EARLY 0.00, MIDDLE 0.35, LATE 0.78.
- Screening ends at 5000 completed runs or 0.55 priority-pair coverage, whichever is
  first; the rest of EARLY runs at the expansion tier.
- Promotion threshold 0.42 interest; verification candidate threshold 0.50; retirement
  below 0.10 interest after 3 runs in a family.
- Promotions may never exceed 45 per cent of submissions. The exploration floor is 30 per
  cent of every batch for the whole campaign, including LATE.
- Signal weights: replicated 0.30 (times 0.25 if the population was seeded with a
  hand-written replicator), crossed 0.30, entropy drop 0.10, reproductive compression
  0.10, novel genome 0.10, coexistence 0.05, transition 0.05, serendipity 0.10,
  persistence 0.05, invasion 0.10. Interest is their weighted sum, capped at 1.0, and is
  set to zero for any run carrying a critical anticheat flag.
- Wall clock: 72 hours from launch. Submission stops when the remaining time is less than
  1.15 times the running estimate for the current tier; work in flight is drained; state
  is frozen; the packet is emitted from the index on disk rather than from memory.

## Reproduction is the object, so it is defined structurally

In every ENDOGENOUS treatment the only path to a descendant is the organism executing
ALLOC (ask for a slot), writing bytes there itself, and executing BIRTH (declare it). The
world's entire bookkeeping is which slot it handed out; it never copies a byte on an
organism's behalf, so a child's contents are exactly what the organism wrote. An organism
that births without copying gets a child of zeros, which is a dead program, and that is
the correct outcome rather than an error.

`births_external` counts any descendant the runner caused. In an endogenous treatment a
single one raises a critical flag, voids the run for reproduction claims and excludes it
from the aggregated map. EXTERNAL reproduction exists as the matched exogenous control and
is never silently restored.

Task competence never copies an organism. It gates interaction opportunity, resource
acquisition or metabolism, depending on the pressure factor. Scoring runs in a scratch
arena with the world ops disabled, so an organism cannot reproduce or touch its soup while
being scored.

## The calibration gate

The campaign refuses to start unless all of these PASS (CALIBRATION.json):

1. VM semantics: 45 checks over instructions, flags, memory, sandbox policies, IO order,
   the answer-before-read probe, and frame-shift runnability.
2. Task witnesses solve their specs exactly, and the one-edit ancestor differs from the
   witness in exactly one operand byte.
3. Seeded replicators replicate, under block copy and bytewise copy, with a self-location
   primitive and with pc-relative self-location.
4. No general replicator exists without self-location: with a hardcoded base, faithful
   copying is confined to the organism that happens to sit at that address.
5. Endogenous reproduction invades from a seed in a random soup.
6. No runner births occur in any endogenous physics.
7. The exogenous control crosses a one-edit incremental constant.

PASS, FAIL and NOT_VERIFIED are distinct. A check that could not run is never counted as a
check that passed.

## Accessibility, carried from cycle 8

- read_order ANSWER_BEFORE_READ reproduces the moat: echoing the first byte scores one
  half without ever reading the regime. FORCED_READ makes both regimes depend on a key
  byte in the input, so the first step toward reading is itself rewarded.
- Constants are ATOMIC (XOR 15, XOR 0x5A, ADD 0x25) or INCREMENTAL (XOR 1, ADD 1). This
  distinction only means something because operand mutation is numeric: a mutated operand
  takes a small signed delta or a single bit flip most of the time and is replaced
  outright only rarely, so from 0x00 the byte 0x01 is one step away and 0x5A is four bit
  flips away with no fitness signal in between. Opcode mutation is categorical.
- mutation_locality LOCAL preserves the reading frame; STRUCTURAL inserts and deletes, so
  downstream bytes decode as different instructions.
- Z8_SLOTTED is the fixed-frame control: slot-aligned point mutation, never insertion or
  deletion.

## Observatory

One row per run in INDEX.jsonl with the full factor vector, derived tags, the scheduler's
reason for allocating the run, its role (experiment, control, verify, intervention), the
matched-control pointer and axis, signals, anticheat flags and headline aggregates. Per
run: config, result, telemetry series, lineage with parent pointers and copy fidelity, and
preserved specimens with genome bytes and disassembly. A family is one cell of the
grammar; a run is that family at one seed, tier and attempt. Runs are append-only; a rerun
is a new run id with parent_run set.

Disk is budgeted. Over budget the observatory degrades in a declared order and writes the
degradation into the run's record rather than truncating silently.

## Anticheat

Detectors: runner births, validation writes, sandbox escape attempts, evaluator leakage
(high competence with zero input reads), held-out gap, nontermination wins, heredity
through stale residue, inheritance of declared non-heritable state, allocation denial, and
immortality past the reaper bound. Exploits are recorded, never silently patched. If an
exploit changes the scientific substrate, the specimen is frozen before any correction.

## Special results, flagged immediately

Reached only under endogenous reproduction; reached only in an incremental representation;
a reservoir niche crossing a moat; a spontaneous replicator from random bytes (only from a
population that was actually random - the grammar forbids seeded instruments in
spontaneity tests, and seeded runs score a quarter of the replication signal and can never
carry this flag); reproductive architecture changing under task demand.

## Success criterion

A well-provenanced map of which structural combinations generate replication, change
accessibility topology, produce transitions, create transferable machinery, maintain
stepping stones, alter evolvability, or reliably fail. Scientific promotion is
post-campaign adjudication. The packet reports matched-pair comparisons as the only
causal-shaped reading and labels the rest unpaired descriptive, because the scheduler chose
where to spend.

## Known limitations, declared before launch

1. Genome length is bounded by the slot (twice the representation length). Length evolves
   within that bound; it cannot grow without limit.
2. Z8_SLOTTED stands in for the existing Nestor fixed-width tape organism. Importing
   another worktree's runtime as a dependency of a 72-hour unattended run would trade the
   property under test for a fragility; the property under test is the reading frame.
3. Four of the directive's thirteen Atlas axes are other factors in this grammar and were
   not duplicated as axes: drift-versus-selection and implicit-versus-explicit are the
   pressure control axis, equal-compute-elite is explicit fitness under external
   reproduction, and coevolution-versus-curriculum-versus-randomisation is the environment
   factor. Alternative-substrate damage is the damage axis crossed with representation.
4. In PAIR_TAPE, heredity is detected by byte similarity between the halves before and
   after execution, with a 0.90 fidelity threshold. That is a heuristic for "this half was
   overwritten by a copy of the other", not a proof of causation.
5. Children inherit their parent's competence as a provisional estimate until the next
   validation pass. Without it a newborn is invisible to every selector for several
   epochs; with it, a selector may act briefly on a stale value.
6. Validation runs every 6, 10 or 12 epochs by tier, and is cached by genome. Competence
   trajectories are therefore sampled, not continuous.
7. Matched controls do not exist for every cell; where the grammar offers no valid
   partner the run is recorded with control_axis null, and a missing control is visible as
   a missing control rather than assumed benign.

## Autonomy

After launch there is no human in the loop and no model in the loop. The scheduler is
arithmetic: counts, thresholds and an upper-confidence bound. This model wrote the code,
ran the calibration gate, and stops. At 72 hours the campaign stops cleanly, freezes state
and emits the packet for subsequent review.
