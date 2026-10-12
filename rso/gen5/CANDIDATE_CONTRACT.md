# Generation 5 candidate contract (C-018-T021) -- read-only survey

Author: Cadmus[harry1-1324c7b6], claude-sonnet-5-5 (Q2), headless on harry1. Written 2026-10-12. Read-only against every
engine lane; no campaign opened (directive s12: a fifth campaign needs a separate bounded authority); no large experiment. The
only execution is a 5.5 s executability smoke of Crius's own committed controls (section 6). Base `origin/main` `3f8cc0150`.
Sources: `roles/Hestia/audit/2026-10-06/REPORT.md` and dossiers, `roles/Aphrodite/beta04/SYNTHESIS.md`, `rso/reach/RESULT.md`,
`proteus/graph/GRAPH_ORGANISM_V1.md`, `roles/Crius/STATUS.md`, and the code named below.

## 1. Recommendation

**Primary: Crius (accessibility-frontier engine, RELAY world, executable-block reuse) -- native phenomenon: artifact-mediated
reuse, i.e. whether a stored, callable procedure causally accounts for later capability.**
**Runner-up: Ananke PTE (packet-tensor register programs) -- native phenomenon: two-part composition (FLIP/XOR).**
Not recommended now: graph rewriting (no dynamics engine exists), Aphrodite's foundry (own instrument still unvalidated; live seat),
another spatial medium (little contrast beyond Aether), a native ecology (Tyche/SFE/Primordial; contrast overlaps Z80 or a live M2 seat).

Chosen on scientific contrast, not convenience: Generations 1-4 asked about retention (Ares), within-life revision (Ensorain),
byte-writer attribution (Z80), and spatial ancestry vs content (Aether). None asks the Hestia question the directive names for
Generation 5 -- *does a preserved discovery CAUSALLY account for a later capability, against compute, storage and
memorisation* -- which is Hestia's promotion gap (W3) and cumulative learning, the top of its Composition Ladder (R4,
`REPORT.md` Part 5 STEP 1).

## 2. Survey (the five classes the directive lists)

| Class | Best in-repo instance | Native phenomenon | Known-answer reference | Verdict |
|---|---|---|---|---|
| Graph-rewriting system | `proteus/graph/` (graph-genome VM + connectivity grammar, 25 node kinds) | program structure as connectivity | keyed-memory witness graph (`witness.py`) | NOT READY: it is a genome format, not a rewriting medium; `GRAPH_ORGANISM_V1.md:12` "NO world has run it", its falsifier FAILED as formulated. Aether's "typed graph rewriting" is only a roadmap item (`REPORT.md` s3.1 step 4). Building one would be engine work. Revisit if an engine owner builds the medium |
| Developmental modular architecture | `roles/Aphrodite/engine` foundry + Beta-04 (stones, extraction, OE pruning) | stepping-stone acquisition, extraction invariance | foundry stones; E3-KP | DEFER: first demonstrated failure is stone ACQUISITION (7/15, bar 12); development/inheritance/second-order labels are INSTRUMENT_UNVALIDATED (`SYNTHESIS.md` s1). The seat has already built the instruments the Observatory would build; awaiting its Beta-05; high risk of duplicating a live owner |
| Compositional program substrate | `prometheus/ananke/` (PTE) | two-part composition (FLIP 0/290, XOR 0/83) | hand FLIP program, 16/16 lines (`REPORT.md` s3.4) | RUNNER-UP, section 7 |
| Another spatial/distributed medium | `herakles/evca` 1D CA; Odysseus spiking lockstep | local rule propagation | density-classification organisms | LOW CONTRAST: radius-3 CA rule evolution is "a field-documented dead end" (dossier); little beyond what Aether already tests |
| Native ecology with learning/exchange | `tyche/` lens ecology; `sfe_ecology`; Primordial NPE | lens interaction order (order-3 wall); echo/latch | subset-MI certificates; CT_UA genome | NOT NOW: Tyche is a live M2 seat (isolation); SFE/Primordial heredity contrast overlaps Z80 |
| **Reuse / accessibility** | **`crius/`** | **artifact-mediated reuse** | **`PROCEDURE_REUSE_C1` (constructed)** | **PRIMARY, sections 3-6** |

## 3. Primary candidate contract: Crius

- **Owner / state.** Engine lane `crius/` (6.0k lines) and seat `roles/Crius/`: seat CLOSED 2026-09-23, "not PARKED, no resume
  pointer ... any further work is a new charter" (`roles/Crius/STATUS.md`). No live seat to disturb, but also nobody to answer
  interface questions: Palamedes must name a steward (Aporia/Achilles) for the engine-owner role before an adapter packet, and
  the forbidden rescue moves in STATUS (lower E/H, more budget, parts in the population, C3) stay forbidden.
- **Pinned SHA.** Lane last changed at `8ad374ed5` (2026-09-25). Pin the adapter to the Palamedes-chosen `origin/main` SHA and
  hash `crius/{vm,evaluate,baselines_c1,world_c1,env,streams,tasks_c1,workspace,artifacts}.py` + `configs/c1.json`
  (c1.json frozen fingerprint `32dfb243be9fdec9` per STATUS).
- **Native phenomenon.** A lifetime of 50 tasks in stages A-E; the organism may persist a Workspace and a 32-block executable
  BlockStore across tasks. Question: does the stored artifact (a typed procedure block invoked by `BLK_INVOKE`) causally account
  for later success, as opposed to compute, storage, a memorised answer table, or the world's own leak.
- **Native interventions (already implemented, `crius/evaluate.py`).** Conditions ACCUMULATED / FRESH / WORKSPACE_RESET /
  WORKSPACE_SCRAMBLED (`run_lifetime` :129, `full_battery` :252) and, from a stage snapshot, ARTIFACT_ABLATION (each block, and
  all), ARTIFACT_TRANSPLANT, FULL_WORKSPACE_TRANSPLANT, CODE_ONLY, COMPUTE_MATCHED, STORAGE_MATCHED (`causal_controls` :207).
  `reuse_gain` is an exact deterministic re-run difference, not an estimate.
- **Known-answer reference (constructed).** `ProcedureReuseC1` (`baselines_c1.py:98`): calibration + template blocks, execution
  by `BLK_INVOKE`. A constructed positive qualifies the INSTRUMENT, not discovery (directive s8).
- **Simpler competitors already built.** `QuitC1` (:61, abstention), `TableMemoC1` (:72, answer table), `ProcedureNoCalC1` (:319,
  same blocks with the hidden identifier permutation ignored = counterfeit/near-miss), enumeration, compute-matched, storage-matched.
- **Unit.** The LIFETIME (50 tasks share the workspace; the C-016 lesson, `rso/registry`: dependent episodes are not independent).
- **Independent recompute.** The engine is deterministic and pure-Python; success counts, `reuse_gain` and the condition table
  recompute from stored task results. Ablation/transplant require native re-execution (explicit trust boundary).

## 4. Hestia concerns this reaches

| Concern | Reached by |
|---|---|
| preservation of discoveries | persisted Workspace/BlockStore; ARTIFACT_TRANSPLANT vs CODE_ONLY |
| cumulative learning | ACCUMULATED vs FRESH over a lifetime; `reuse_gain` per task |
| compositional capability | typed templates with argument ports; per-block ablation (a single block can carry the whole gain) |
| reachability deserts | the engine's measured result: reuse EXISTS and executes at three constructed levels (block control 46.1 vs 20.7; typed transplant 6/6/6 vs 1/1/0; PARTS +15.97 at 47 edits) but is not accessible to (8+24) mutation+splice at any rung in 300 iterations (0/36 runs; `roles/Crius/STATUS.md`) |
| developmental organization | not reached (Aphrodite lane); declared out of scope rather than stretched |

No recursive-sagacity claim is implied. The expected result class is "constructed reuse is attributable; native discovery of
reuse is DETECTION_UNQUALIFIED / not found", the same honest shape as Generation 3.

## 5. Demand-gate sketch (what the Generation-5 selection step must show before any adapter)

Run read-only on new lifetime seeds (not 1, 201-203, 301-303), one process, minutes. Freeze rules first.
1. **World demand.** Does the task stream REWARD reuse? Required: compute-matched / storage-matched / table / abstention
   competitors all < the reuse positive by a pre-stated margin; MDL check that no short formula solves the stream (Hestia gate).
2. **Known-answer positive** (`ProcedureReuseC1`) attributable in >= 3/3 seeds: ACCUMULATED >> FRESH, CODE_ONLY, COMPUTE_MATCHED,
   STORAGE_MATCHED; per-block ablation kills it.
3. **Near-misses that must FAIL:** `ProcedureNoCalC1` (permutation-blind), `TableMemoC1`, a block present but never invoked,
   a block copied from a different stream, a scrambled workspace.
4. **Falsifiability checklist** (Aether SELECTION s4 format, six questions) for every control, including the world leak below.
5. **Completeness contract** (Gen-4 shared component, if landed): frozen manifest of seeds x conditions x blocks; a dropped
   condition must refuse, not shrink the experiment.
6. **Kill / narrow rule.** If competitors reach the positive (the world does not demand reuse) or the world's leak explains the
   gain, narrow to "reuse needs a leak-free stream" and say so, as Z80 narrowed retention.

## 6. Executability smoke (done; not a result)

`rso/gen5/smoke_crius.py`, output `rso/gen5/smoke_crius_result.json` (sha256 prefix `4fce11604b6f39f9`), 5.5 s:

    python -m rso.gen5.smoke_crius rso/gen5/smoke_crius_result.json

Seeds 18_021_001..003 (disjoint from every Crius-registered seed), frozen `crius/configs/c1.json`, 50 tasks/lifetime:

| seed | REUSE ACC / FRESH / SCRAMBLED | NOCAL ACC / FRESH | TABLE_MEMO ACC | QUIT | snapshot remainder: ACC / ablate-all / code-only / compute-matched / storage-matched |
|---|---|---|---|---|---|
| 18021001 | 49 / 26 / 26 | 26 / 26 | 26 | 19 | 18 / 6 / 6 / 6 / 6 |
| 18021002 | 50 / 32 / 32 | 32 / 32 | 32 | 20 | 18 / 5 / 5 / 5 / 5 |
| 18021003 | 50 / 28 / 29 | 28 / 28 | 28 | 19 | 18 / 5 / 5 / 5 / 5 |

The constructed positive separates from every competitor, the permutation-blind near-miss and answer table show NO gain, and
single-block ablation is as damaging as removing all blocks in all three seeds (block 0). It runs in seconds on one core. This
shows the controls EXECUTE, nothing more: the positive was hand-built, and the leaks below mean it is not yet a demand-gate pass.

## 7. Likely qualification difficulties (honest list)

1. **The world leaks and the substrate helps.** `world_c1.primitive_of_action` (:81) exposes the primitive an action performed
   (`env.py:97`); in rung B the substrate silently calibrates action ids (`vm.py:461`). The positive's gain may be largely
   the leak plus calibration, not "reuse". The leak-ablated stream is the first thing the demand gate must test.
2. **Native discovery is absent.** 0 reproducible ACC > FRESH in 36 search runs; any native claim is DETECTION_UNQUALIFIED.
   The Observatory can only qualify attribution on constructed lifetimes (Generation-3 shape).
3. **Recipe-predictable controls.** Ablation of a hand-built block is predictable from the recipe; each control needs the
   privileged-access question answered (the "recipe reader given the answer table" trap).
4. **Dependent tasks.** 50 tasks share a workspace: analyse per lifetime (registry `ruler-binary-retention` NOT-FOR note).
5. **Evidence custody.** Large Crius run rows exist on M2 only, by hash (Hestia D7); the adapter must use fresh local runs.
6. **No steward.** Closed seat; a named owner is required before any interface request is possible.
7. **Reusable components apply at narrow scope:** `custody-keeper` (bytes), `receipt-canonical` (ints/strings only; floats such
   as `fitness` must be encoded as fixed-point), `stratified-holm-analysis` (binary per-lifetime success, NOT its `analyze.py`
   as a general analyzer), `integration-notify`. Reusing the CODE does not carry the scientific inference (directive s11).

## 8. Runner-up contract: Ananke PTE (kept ready, not opened)

- **Owner / state.** `prometheus/ananke/` (6.1k lines, 20 modules), seat Ananke (`roles/Ananke`, STATUS: no new large PTE
  campaign under MWO-0001; Wave-2 closed). Pin at the chosen SHA; `engine.py`, `oracle.py`, `assays.py`, `plants.py`, `envs.py`.
- **Native phenomenon.** FLIP/XOR: a two-part mechanism whose parts are individually worthless (Hestia W1, "the composition
  wall"; FLIP 0/290, XOR 0/83).
- **Known answer.** Hand FLIP program using 16/16 lines (`p_flip`, in the seat lane `roles/Ananke/pte/c2a/c2a_common.py`, NOT in
  the engine package); RELAY/HOLD plants are in the engine (`plants.py:48,67`; `plant()` :89 also holds a `sense_copy` cheat). **Independent oracle:** `oracle.py` is an integer re-implementation with a conformance test, the best
  independent-recompute story of any candidate. **Native intervention:** exact mirror-pair carrier swaps (`assays.py:306`
  `transplant_state`, `twin_assay` :233); worlds come in mirror pairs so every constant policy scores exactly 0.5.
- **Simpler competitors:** constant, echo, hold-latch, one-value control (exactly 3/6), zero-communication control.
- **Difficulties:** reachability (only 4/200 FLIP cells admissible), needle landscape (62% single-edit kill), plants are
  hand-built, the seat is live and its next experiment is the Hestia "single most informative next run" (block-duplication FLIP
  test), so an Observatory campaign would duplicate or race it. Choose it if the operator wants composition specifically.

## 9. Decisions requested of Palamedes / the operator

1. Confirm Crius as the Generation-5 candidate (or take Ananke) and name an engine steward for the closed Crius lane.
2. Authorise a read-only Generation-5 selection step with the section-5 gate; nothing here opens the campaign.
3. The graph-rewriting and developmental options stay on the shelf with the conditions in section 2.

## 10. Limitations

Q2 author; Hestia's dossiers are a model's assessment and some numbers are CLAIMED, not OBSERVED (Hestia D7); only Crius's
controls were executed (5.5 s); Ananke, Aphrodite, Proteus-graph and Tyche were read, not run.
