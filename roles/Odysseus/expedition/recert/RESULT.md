# Functional label recertification harness -- design, known answers, three labels

Currency: 2026-09-28. Odysseus expedition worker, ubu001, worktree odysseus-base-role @ 02800d2b5 (branch
odysseus/expedition-1-2026-09-28). Operator directive 2026-09-28 s6 (roles/Odysseus/prompts/
2026-09-28_expeditionary/01_OPERATOR_DIRECTIVE_verbatim.md:213-240). Stdlib only; no hosts, no installs.
Compute: known-answer tests ~20 s; L2 32 s; L1 346 s; L3 608 s; L2 oracle diagnostic ~60 s; smokes ~4 min.
About 20 min wall in total, on a laptop that other workers held at load average ~38, so the CPU time was lower.

Nothing outside this directory was modified. No historical record is rewritten. Every row keeps `then` (the
record's own label and fields, copied verbatim) beside `now` (the verdict and the measured columns).

## 0. Prior-work search (done first)

- `git grep` over all refs for "recertif": no hits. Nobody has built a general recertifier before.
- These are the closest instances. The harness generalises them and reuses their rules.
  - S1 (roles/Odysseus/frontier/poi/spikes/S1_copyless_sr/): the BEE isolation self-copy probe; 20/68 do not
    self-copy.
  - FR-011 (roles/Artemis/backlog/threads/FR-011.md): the P-11 BYTEWISE donors are near-homopolymers. It asks for
    "an information criterion".
  - NPE P-11 itself (roles/Nestor/campaigns/z80atlas-verify-2026-09-22/P11_SPEC.md, p11.py, tests/test_p11.py):
    a recertification of the 1,031 predecessor events that reported survivors beside the frozen count (the same
    then/now discipline).
  - BEE forensics:
    - `_is_self_copy` / repro_descriptor, the copy-op provenance rule (prometheus/z80atlas/world.py:576,
      adjudication.py:42);
    - the G8 cheat controls;
    - the HIST copy-op NOP ablation;
    - TRACER_DIVERGED, the replay-equality guard in roles/Bellerophon/forensics_2026-09-23/tools/traced_replay.py:4.
  - Archaeon causal lens archaeon/causal_lens/FALSE_FRIENDS.md, FF-1..34. The ones used here are FF-5 (any window
    write = replication), FF-11 (the NPE pair "birth" renames the host body in place), FF-15 (fidelity is
    resemblance), FF-24 (SUSTAINED is depth) and FF-28/30 (own code = location).
  - Rhadamanthus re-reviewed 19 death certificates: 3 UPHELD. Same shape: a verdict label re-tested later.
  - I6 s2.2 (roles/Odysseus/frontier/poi/raw/I6_failures_reversals.md): label-as-property, 21 rows.
- Reused unchanged: BEE's vm.execute and the frozen run plans (grounding.plan, coupling_campaign.plan). I rebuilt
  all 12,130 grounding configs; ids, seeds and cells match the result rows with 0 mismatches. Also reused: NPE's
  substrate z8.py (the forensic copy that ran the reassay) and p11.assay, unmodified.

## 1. Harness design (recert.py)

A `Label` is a plain spec. The engine parts are five callables:

    provenance(obj)       -> {"label_then": ..., <record fields verbatim>}      PROVENANCE: how the label was made
    structural(obj)       -> {"ok": bool, features...}                          STRUCTURAL: what it contains
    environments(obj)     -> [env, ...]                                         the environment set
    behavioural(obj, env) -> {"pass": bool, ...}                                BEHAVIOURAL: what it does, per env
    causal(obj, beh)      -> {"ok": True/False/None, effect...}                 CAUSAL: an intervention on the
                                                                                presumed mechanism, run in an env
                                                                                where the behaviour is present
plus claimed_property, expected_mechanism and min_rate. `recert.run(label, objs, workers)` forks over objects and
returns one row per object: then | structural | behavioural (pass rate over envs) | causal | now. The verdict is
the first rule that matches:

    LABEL_PROVENANCE_ONLY                 no behaviour in any env, presumed structure absent
    STRUCTURE_WITHOUT_BEHAVIOUR           no behaviour in any env, presumed structure present
    BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM  behaviour somewhere, but the intervention shows another mechanism
    LABEL_CONTEXT_DEPENDENT               behaviour and mechanism present, in < min_rate of envs
    LABEL_OK                              behaviour in >= min_rate of envs, mechanism as presumed (or n/a)
    UNLABELLED_<verdict>                  the same rules on control objects that do NOT carry the label
                                          (UNLABELLED_LABEL_OK = a false negative of the labelling process)

Files:
- recert.py: the library.
- bee_engine.py: the BEE adapter. It rebuilds run configs from the frozen plans and runs one execution exactly as
  World._execute does, in the run's own chemistry.
- l1_bee_sr.py, l2_npe_p11.py, l3_bee_solver.py: the label specs and runners.
- l2_oracle_regs.py: an L2 diagnostic.
- test_known_answers.py: the known-answer tests.
- analyse.py: builds TABLES.txt.
- Rows: L1_rows.json, L2_rows.json (plus L2_oracle.json), L3_rows.json, KNOWN_ANSWERS.json.
- Logs: run_L*.log.

The same causal idea is used for every "copy" label. It is template intervention: set do(template[p] := b) at
every position (2 random b each) and measure transmission T, the share of edits the child carries at p.

- Copying predicts T near 1.
- Painting (code that writes a fixed pattern that happens to resemble the parent) predicts T near 0.
- bits_transmitted = 8 x the number of positions carried in both draws. This is FR-011's information criterion,
  applied per object: a homopolymer painter carries 0 bits.
- The tape's own content (dominant-byte share, entropy) is reported beside it. Capacity and realised content are
  kept apart.

## 2. Known-answer results: 24/24 (KNOWN_ANSWERS.json)

    verdict table, 7 cases incl. an unlabelled capable control -> UNLABELLED_LABEL_OK        7/7
    L1 true: LDIR replicator + random tail                     LABEL_OK   rate 1.00 T 0.94 480 bits
    L1 true: LDI byte-loop replicator                          LABEL_OK   rate 1.00 T 0.91 464 bits
    L1 impostor: copy routine behind HALT                      STRUCTURE_WITHOUT_BEHAVIOUR
    L1 impostor: blank tape carrying the label                 LABEL_PROVENANCE_ONLY
    L1 impostor: zero painter (LD (T),A loop, tape = code+0s)  BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM  rate 1.00 T 0.00
    L1 painter: passes the functional test, fails BEE's copy-op rule (the rule is narrower than the label)
    L1 control: unlabelled replicator                          UNLABELLED_LABEL_OK
    L2 true: side-agnostic block copier (z8)                   LABEL_OK   rate 0.89 T 0.93
    L2 boundary: absolute-address copier (test_p11's own)      rate 0.50 (copies only from side 0), T 0.93
    L2 impostor: LDIR-smear zero painter                       BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM  T 0.01
    L2 impostor: bare LDIR, addresses from registers           STRUCTURE_WITHOUT_BEHAVIOUR
    L2 impostor: random genome carrying the label              LABEL_PROVENANCE_ONLY
    L2 painter: p11.assay ACCEPTS it directly (2/3 draws, fid 0.906) -- FR-011's claim, now a fixture
    L3 true: INC witness                                       LABEL_OK   IN knockout -> accuracy 0.02
    L3 impostor: right only with an empty window               LABEL_CONTEXT_DEPENDENT  rate 0.73
    L3 impostor: reads the input region by address, not IN     BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM
    L3 impostor: ECHO tape labelled an INC solver              LABEL_PROVENANCE_ONLY

One expectation moved and is recorded here. I first expected test_p11's absolute-address copier to come out
LABEL_CONTEXT_DEPENDENT. It works from one tape side only, so it passes in exactly half the environments. The
measured rate was 0.50 under one seed and 0.44 under another. The check asserts the bracket (rate in [0.3, 0.5],
mechanism OK) rather than a single verdict.

## 3. The third label, and why

L3 is BEE "competent" / "verified exact solver": tasks.verify_tape = the tape alone, an EMPTY window, 16 fixed panel
inputs. I chose it for three reasons:
- It is the other half of the coupling campaign's primary endpoint, "de novo competent self-replicating tape". S1
  and L1 test only the self-replicator half. With L3, the whole endpoint label is recertified on the same 68 tapes.
- It feeds G3's endogenous-advantage contrasts and every task_reached flag.
- It is a 16-point certificate standing in for a 256-point function.

## 4. L1 -- BEE "self-replicator" (sr_depth > 0, dominant_sr_tape)

What we called it then: "dominant self-replicating tape". The label is a BIRTH record: the organism's writer
self-copied when it was born (world.py:543). Nothing re-tests the organism itself.

The test, per object:
- Property: the tape writes a >= 0.9-fidelity copy of itself into the window. At least 0.9 L of the bytes must be
  written by execution and not moved there from the window itself; the in-place sweep, M2, is excluded.
- Environments: 8 inputs x 4 windows (zero, self, random x2) = 32, in the run's own chemistry.
- Mechanism: T >= 0.5.
- Structure: carries a copy-op byte.

Objects:
- All 1,425 distinct (dominant tape x chemistry) of the 12,130-run grounding round.
- S1's 68 coupling-ledger tapes, run again as a cross-check.

    L1a grounding, by origin              n    OK  CTX BWEM  SWB PROV  not-OK
      HIST (historical origin transplant) 389  384    0    1    3    1    1.3%
      random-start (de novo candidates)    67   62    0    1    4    0    7.5%
      seeded replicator populations       969  968    0    0    1    0    0.1%
      TOTAL                              1425 1414    0    2    8    1    0.8%
    L1d coupling origin ledger (S1 set)    68   47    3    0   13    5   30.9%
      ON arm                               42   39    0    0    1    2
      OFF / SHUFFLED / YOKED               26    8    3    0   12    3

Then vs now:
- In the grounding round, the descriptor's self_copy then (input 42, zero window) agrees with the verdict now for
  1,412 + 9 of 1,425 tapes.
- 2 then=False tapes are LABEL_OK now: they copy in other contexts.
- 2 then=True tapes are BWEM now: T 0.24 and 0.42, partial copy plus other writes.

Cross-check against S1: the harness reproduces S1 tape-for-tape (47 copiers = LABEL_OK; 20 non-copiers
not-OK). The one exception is c009689, which S1 counted as a copier on a single input with a random window. That
input is not in the harness's 32 environments, and the harness calls it SWB.

New here: 3 control-arm tapes (one tape, in the OFF, SHUFFLED and YOKED runs of one seed pair) are
LABEL_CONTEXT_DEPENDENT. They reproduce only when the neighbour window already holds a copy of them, and the LDIR
that does the copying executes at pc 71, i.e. from the NEIGHBOUR's copy of the code. This is FF-28/30 measured:
their "self-replication" is carried by a clone's code.

Information (FR-011's criterion) among the 1,461 LABEL_OK tapes:
- bits_transmitted: min 168, median 480, max 496. No homopolymer painter.
- Only 1 has a near-homopolymer tape (dominant byte >= 0.8).
- So BEE's certified heredity is informative: FR-011's painting worry does NOT apply to BEE.

Descriptor: knocking out the EXECUTED copy-op bytes removes behaviour in 1,115 of 1,461 LABEL_OK tapes and leaves
it at >= 0.5 in 112. That matches the HIST rescue (a copy op re-created or reached in another frame), and the
GROUNDING_REPORT already records it.

Reading: in the grounding round, the SR label holds for 99.2% of tapes. The label fails where S1 found it failing,
in the coupling campaign's non-ON arms (18 of 26 not-OK). That makes it a campaign-specific failure (sterile
label-carrying dominants), not a general defect of sr_depth.

## 5. L2 -- NPE "P-11 causal copy" (57 certified runs, first certified donor genome each)

What we called it then: "P-11 causal pair event". The event was re-executed from its EXACT recorded pair state:
both genomes AND both register files. Those 57 runs are what "A-1 narrowed to 57" and the P-11 depth counts rest
on.

The test, per object:
- Property: the certified donor GENOME passes the unmodified p11.assay (rebuilds a randomized partner) from
  register states it can reach. Those are fresh (newborn) and after 1, 2, 4 or 8 ordinary interactions with random
  partners on random sides (registers carried as the world carries them), on either side. That makes 18
  environments.
- Mechanism: template intervention, T >= 0.5.
- Structure: ED B0/B8 (BLOCK cells) or 7E+12 (BYTEWISE cells).

    L2a                                   n    OK  CTX BWEM  SWB PROV  not-OK
      BLOCK high-entropy                  33    2    1    3   27    0   93.9%
      BLOCK near-homopolymer (dom>=0.8)   14    0    0   10    1    3  100.0%
      BYTEWISE near-homopolymer           10    0    0    4    0    6  100.0%
      TOTAL                               57    2    1   17   28    9   96.5%

L2b, then (P-11 record) | now (this harness). Excerpt; all 57 rows are in TABLES.txt and L2_rows.json:

    run                            prim   depth draws dom  | now   rate fresh  T     bits oracle domb
    7ae3f9c1437c8000-s54765-tL-a0  BLOCK  2     3     0.08 | OK    0.50 0.50  0.812 392  Y      00
    e141105526c59efe-s92071-tL-a0  BLOCK  1     2     0.09 | OK    0.50 0.50  0.781 384  Y      00
    cb7f5ca16e697938-s60768-tL-a0  BLOCK  1     2     0.08 | CTX   0.11 0.00  0.812 392  n      00
    0e6c36f044262537-s23100-tL-a0  BLOCK  1     2     0.94 | BWEM  0.22 0.00  0.016 0    n      36
    164fced841ec95e0-s47993-tL-a0  BLOCK  1     3     0.91 | BWEM  0.17 0.00  0.000 0    Y      36
    03650e1ad792eefa-s9040-tL-a0   BLOCK  1     2     0.26 | SWB   0.00 0.00  -     -    Y      00
    c2a87e5970ad345d-s80949-tL-a0  BLOCK  2     2     0.19 | SWB   0.00 0.00  -     -    n      de
    2cb50bf028fcf0c5-s51326-tL-a0  BYTEW  1     3     0.91 | PROV  0.00 0.00  -     -    n      36

(fresh = pass rate from newborn registers; oracle = passes when handed HL = own start, DE = partner start,
BC = n by hand.)

- Only 3 of 57 certified donors are copiers of their own genome: 2 LABEL_OK and 1 CONTEXT_DEPENDENT, each
  carrying ~390 bits. One of them, 7ae3f9c1, is one of the two depth-2 P-11 lineages. The other depth-2 lineage,
  c2a87e59, is SWB.
- 17 are painters (BWEM; 14 of them near-homopolymers). They pass p11.assay in some reachable states while
  carrying 0-8 bits (T <= 0.05), except one partial copier with T 0.47 and 88 bits. The dominant byte is mostly
  0x36 (Z80 "LD (HL),n", whose operand equals its opcode).
- 28 carry a block-copy op but rebuild nothing from any reachable state (SWB). 16 of the 28 DO rebuild the partner
  when handed the ideal register file (oracle, L2_oracle.json). The certified genome contributes a bare LDIR/LDDR
  (e.g. 03650e1a: NOP x6, LDIR), and the source, destination and length came from register state. The world keeps
  that state per BODY: FF-11, the pair "birth" renames the host body in place and keeps its registers.
- 9 are PROV: near-homopolymers that do nothing from any state tried.
- Fresh-state pass: 7 of 57 pass in at least one fresh environment.
- 20 of 57 show the behaviour anywhere in the 18 environments.

## 6. L3 -- BEE "competent" / "verified exact solver"

What we called it then: "verified exact solver" (summary.verified.exact_tapes) or "competent" (coupling ledger),
which is verify_tape: empty window, the 16-point panel, and the DEFAULT chemistry.

The test, per object:
- Property: computes f on all 256 inputs (256 seeded pairs for SUM2) with an empty window, plus 32 inputs x 3
  other windows. That is 352 environments, in the run's OWN chemistry, with min_rate 0.9.
- Mechanism: knock out the executed IN instructions; accuracy must collapse. For CONST, the answer must instead be
  input-independent.
- Structure: passes the panel now and carries IN and OUT bytes.

    L3a                                   n    OK  CTX BWEM  SWB PROV
      coupling ledger (CONST 2, ECHO 61, INC 5)   68   68    0    0    0    0
      grounding G3 / G5 / G7 / G7P1 / G8 / HIST  831  831    0    0    0    0
      grounding P8 SEEDED/ON/undefined_halt INC    4    0    0    0    4    0
      TOTAL                                      903  899    0    0    4    0

- No certified solver is right only on the 16 panel points (0 of 903). Mean accuracy is 0.996 in every window
  type. The label is sound as a capability.
- The 4 SWB are a ruler defect, not an organism fact. These 4 tapes pass verify_tape because it executes with
  undefined = NOP (tasks.py:168-174 never passes cfg.ldir / cfg.undefined_op). In their own world (undefined ->
  HALT) they answer 0 of 352. They count as "verified exact solvers" of a chemistry they never ran in. Only the
  P8 undefined_halt and ldir_* cells are exposed.
- Then vs now, in the opposite direction: the coupling ledger says task_accuracy 0.0 for c010927 (ON) and c010929
  (SHUFFLED). Both are LABEL_OK CONST solvers now. repro_descriptor uses Task(cfg.task), whose k defaults to 42,
  instead of the configured CONST k = 126 (adjudication.py:57). The ledger's descriptor under-reports; the world's
  "competent" label was right.

## 7. What surprised me

1. P-11 certifies an EVENT, and the program reads it as a property of a GENOME. The P-11 spec is explicit that it
   re-executes the recorded register files. The heredity bookkeeping built on it (P-11 depth, "57 surviving
   replicators", the H2 arm B implant of the "donor genome") treats the genome as the replicator. Of those 57
   genomes:
   - 3 are real informative copiers;
   - 54 do not copy their genome from any state a genome can reach on its own (newborn, or up to 8 ordinary
     interactions). Of these, 17 paint and 37 do nothing. 16 of the 37 are "LDIR + borrowed registers": they
     copy only with the host body's leftover register state.
   FR-011's reading was "P-11 cannot tell painting from copying". It is broader than that: P-11 cannot tell the
   genome's contribution from the body's state.
2. BEE's label is much better than its campaign-level record suggested. In the grounding round it holds for
   99.2%, and every certified copy carries >= 168 bits. S1's 29% failure is specific to the coupling campaign's
   control arms.
3. The competence ruler is right about organisms and wrong about chemistry. The only L3 failures are 4 tapes
   certified in a chemistry they never ran in, which is a harness defect in verify_tape.
4. BEE's own copy-op self_copy rule is narrower than its label. It rejects a working painter and a clone-hosted
   copier alike, so a functional test plus a template intervention says more than either rule alone.

## 8. How Artemis's failure catalogue (FR-057) could use it

FR-057 wants typed reversal records and the ruler-defect vs substrate-fact share. Each harness row is a typed
record: label, then (verbatim provenance), now (verdict), and the column that failed. The column says which kind
of failure it is:

    PROVENANCE_ONLY / STRUCTURE_WITHOUT_BEHAVIOUR  label-as-property (I6 s2.2 shape)
    BEHAVIOUR_WITHOUT_EXPECTED_MECHANISM           ruler accepts a different mechanism (painting, IO bypass)
    CONTEXT_DEPENDENT                              ruler's environment too narrow (one window, one register state)
    a ruler that disagrees with its own world      ruler defect (the L3 chemistry case)

Suggested use:
- (a) A recert run per consequential label, before a campaign cites it. A Label spec is about 100 lines per
  engine, and runs take seconds to minutes.
- (b) The UNLABELLED_ prefix gives the false-negative rate when control objects are included.
- (c) KNOWN_ANSWERS.json-style fixtures per label are the "guard that can fire" evidence NPE lesson 1 asks for.
- (d) Candidate FR-057 rows from this run:
  - P-11-as-genome-property (L2);
  - verify_tape chemistry mismatch (L3);
  - repro_descriptor CONST k default (L3);
  - clone-hosted SR in coupling controls (L1).

## 9. Limits

- Isolation, not world replay. BEE: one execution per environment; the world's birth rules (target_fill, copy
  cost, lifespan) are not replayed. NPE: my warm-up is 1-8 interactions with RANDOM partners (clone partners and
  up to 32 interactions were probed on 8 donors: no change). The recorded register states that P-11 used are not
  stored in P11_REASSAY.jsonl, so I could not re-derive how each was reached. Reaching one of them through a real
  body history (FF-11) remains possible, and would itself be the finding: heredity carried by body state.
- The environment sets are my choice (L1: 8 inputs x 4 windows; L3: 352; L2: 18). The verdicts at the min_rate
  boundary (0.5 for L1/L2; 0.9 for L3) depend on them. Every row stores pass_rate so the threshold can be re-cut.
- T >= 0.5 is a presumed-mechanism threshold. Two L1 rows (T 0.24, 0.42) and one L2 row (T 0.47) sit near it.
- L1 objects are distinct (tape x chemistry), not runs. Seeded lanes dominate the count.
- PAIR_EXECUTION BEE cells are run as solo executions. For the first tape the memory effects are identical, but
  the partner's execution is not modelled.
- L2 covers the 57 surviving runs only. Donor genomes of the 974 non-surviving runs are not in the committed rows.
- No new campaign. This is a re-analysis of committed tapes with committed VMs.

Commands (from this directory, PYTHONDONTWRITEBYTECODE=1):

    python3 test_known_answers.py && python3 l2_npe_p11.py && python3 l1_bee_sr.py && python3 l3_bee_solver.py \
      && python3 l2_oracle_regs.py && python3 analyse.py > TABLES.txt
