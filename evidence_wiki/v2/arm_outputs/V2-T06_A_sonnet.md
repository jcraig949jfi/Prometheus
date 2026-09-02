# PROPOSAL V2-T06 (arm A)

## Hypothesis
Transplanting the accumulated executable artifact library from Agent D-5's
findability generation into the Ludus games-as-worlds bench will raise the
solitaire solve/circuit-discovery rate on Ludus worlds relative to a
history-free baseline, but the size of that gain will be governed by the same
decomposition D-5 already measured in its own substrate: a library-CONTENT
effect (specific ecology-adapted artifacts) versus a generic diversity-
injection effect (having accumulated ANY sizeable library, regardless of
content). We hypothesize the content-specific component will NOT transplant
across the D-5 register-machine substrate boundary into Ludus's dice/card
substrates without an explicit verb-translation interface, because D-5's own
artifacts are whole programs over a frozen, non-extensible 14-opcode
instruction set native to its mutation-physics register machine — a
representation with no shared primitives with Martian Dice, Flip 7, Incan
Gold, or Can't Stop.

## Motivating evidence
`agent_d5_blind/VERDICT.md` (verdict HISTORY_FINDABILITY_ADVANTAGE, dated
2026-08-27) is the primary source. Its central result: M1 (library-carrying)
beats M0 (history-free) by +10.95pp CFR (p=0.0007, one-sided paired
permutation, task-level n=42), and the causal decomposition (gate G9) shows
this is a library-CONTENT effect, not a developmental-correspondence effect —
M1-shuffled-history retains 100% of the advantage, M1-random-library (size-
matched random-walk genotypes) retains only 39%. Critically for a transplant
design, gate G7 (frozen alien zero-shot transfer, still WITHIN the D-5
register-machine substrate) was NOT ESTABLISHED: +5pp, p=0.26. If transfer to
an alien task family inside the SAME substrate is already non-significant,
transfer across substrate families (register-machine genotypes to card/dice
game states) is the harder case, not the easier one. `ludus/bench/
RULES_AUDIT.md` establishes that all four currently-implemented Ludus worlds
(Martian Dice, Flip 7, Incan Gold, Can't Stop) are solitaire-only and that
every rule constant is HYPOTHESIZED (reconstructed from memory, no rulebook
consulted) — a failed audit blocks promotion of any claim about the named
commercial game but not the machinery, per that document's own framing.
User memory (already in context, not separately retrieved) supplies two
load-bearing facts I treat as established prior findings rather than
re-deriving them: `feedback_verbs_must_be_native.md` (seven generic operators
found zero relations on a 295M-triple corpus; one native verb found 4,476 on
the same data — verbs must be native to the objects they act on) and
`project_ludus_bench.md` (Ludus's own charter already expects "transfer
mediated by INTERFACES," not raw artifact reuse).

## Prospective predictions
1. Naive/raw transplant (D-5 opcodes replayed unmodified against a Ludus
   adapter, no native-verb translation): predict solve-rate gain over
   history-free baseline in the range -2pp to +5pp, NOT distinguishable from
   zero at n=40 task instances (point estimate closest to G7's own +5pp,
   p=0.26 in-substrate ceiling; cross-substrate should not exceed it).
2. Size-matched random-artifact-library control (Ludus-native programs of
   matched length/complexity, no D-5 provenance): predict this control
   captures most of whatever gain arm 1 shows — i.e., transplant arm minus
   random-library-control gain <= 3pp, replicating D-5's own G9 finding
   (39% content retention in-substrate implies <39% is optimistic for
   cross-substrate; we predict closer to 0-15%).
3. Interface-translated transplant (D-5 opcodes mapped to native Ludus verbs
   — e.g. claim-symbol, reroll, bank, push — via an explicit hand-built
   interface per world): predict this is the only arm with a chance of
   recovering a positive, content-attributable, statistically significant
   gain, plausibly +5 to +12pp on the worlds whose action grammar is
   opcode-decomposable (Can't Stop, Martian Dice), and near-zero on worlds
   whose core mechanic is set-collection-without-replacement (Flip 7, Incan
   Gold) where D-5's register-machine primitives have no natural counterpart.
4. Executability floor: fewer than 90% of raw D-5 artifacts will parse/run
   without error against a Ludus adapter without translation (structural
   incompatibility precedes any content-effect question).

## Experiment
Four arms, four worlds (Martian Dice, Flip 7, Incan Gold, Can't Stop; all
solitaire per current bench scope), 5 seeds/arm/world (per
`feedback_replicate_seeds.md`), metered evaluation budget matched to the
D-5 M0/M1 comparison (fixed evals per task, not fixed wall-clock):
- Arm H0 (history-free baseline): world-native search/policy with no library.
- Arm RAW (naive transplant): D-5's frozen artifact library replayed through
  a syntax-only adapter into each Ludus world's action space, no semantic
  translation.
- Arm RAND (diversity-injection control): a size-matched library of random
  Ludus-native programs, generated the same way D-5's G9 random-library arm
  was built (random-walk genotypes matched for count and complexity).
- Arm IFACE (interface-translated transplant): D-5 artifacts passed through a
  hand-authored opcode-to-native-verb mapping per world before replay.
Primary outcome: per-world, per-arm solve/circuit-discovery rate (CFR
analog) against the world's oracle-reachable target set, paired against H0
by task instance, one-sided permutation test (mirrors D-5's own G4
methodology in `results/compute_gates.py`).

## Controls
- H0 (history-free) isolates the library's total effect.
- RAND (size-matched random library) isolates content from mere
  diversity-injection, replicating D-5's G9 design directly — this is the
  single most important control given G9 already showed random libraries
  capture 39% of the in-substrate effect.
- Shuffled-acquisition-order variant of arm IFACE (optional, budget-
  permitting): tests whether D-5's own G6/G9 "order does not matter" finding
  also holds when the library has been re-encoded into a new substrate; not
  required for the primary falsifiers below.
- Executability pre-gate (P0/P1-style, per VERDICT.md's claim ladder):
  measure the fraction of RAW-arm artifacts that execute without crashing
  BEFORE comparing solve rates, so a null result cannot silently conflate
  "didn't run" with "ran but didn't help."

## Confound defenses
- Solitaire-only scope: all four worlds are currently solitaire
  (`RULES_AUDIT.md`); no claim from this experiment generalizes to
  multiplayer Ludus worlds (Incan Gold's real character is explicitly
  opponent-driven and is out of scope here).
- HYPOTHESIZED rule constants: per `RULES_AUDIT.md` Priority-1 list (Martian
  Dice's doubled ray face, Flip 7's rank-multiplicity deck, Incan Gold's
  hazard/treasure distribution, Can't Stop's column heights), any
  game-specific promoted claim is gated on the HITL rules audit passing for
  that world; a machinery-only claim (the transplant mechanism works/doesn't,
  independent of whether Martian Dice's dice are faithfully modeled) is NOT
  gated by the audit and is the claim this proposal actually stakes.
- Substrate heterogeneity within D-5 itself (SHRC 8/8 vs MULC3 0/8 at the
  same evaluation budget) means results must be reported per-world, never
  pooled into one cross-world number, mirroring
  `feedback_sampling_strategy_is_analysis.md` / stratification doctrine.
- Underpowered-speed trap: D-5's own HACR (accumulation speed metric) was
  NOT ESTABLISHED at n=13 (90% CI [0.93, 3.70] touching 1.0). This proposal
  does not preregister a speed/efficiency claim for the transplant, only a
  solve-rate claim, to avoid repeating that underpowered comparison.
- Rows-with-verdict discipline: raw per-task/per-arm rows ship in the same
  commit as any verdict (`feedback_verdict_without_rows_is_an_assertion.md`).

## Preregistered falsifiers (numeric thresholds)
1. PRIMARY — transplant confers an advantage: FALSIFIED if the best-
   performing transplant arm's (RAW or IFACE) solve-rate advantage over H0
   is < +5pp OR p >= 0.05 one-sided permutation, pooled across >=40 task
   instances spanning all 4 worlds with >=8 instances/world.
2. EXECUTABILITY GATE: FALSIFIED (RAW arm voided, do not proceed to compare
   its solve rate) if < 90% of RAW-arm artifacts execute without error
   against the Ludus adapter.
3. CONTENT-VS-DIVERSITY GATE (G9 analog): "library CONTENT transplanted" is
   FALSIFIED if RAND (random-library control) retains >= 70% of whatever
   advantage the best transplant arm shows over H0 — i.e., the effect is
   attributable to generic diversity injection, not to D-5-specific content.
4. INTERFACE-MEDIATION GATE: the claim "interfaces mediate transfer"
   (per `project_ludus_bench.md`) is FALSIFIED if IFACE's advantage over H0
   does not exceed RAW's advantage over H0 by >= 5pp.
5. FLOOR-REPLICATION GATE: if the best transplant arm's point estimate is
   <= 0pp, this is not a weaker version of D-5's G7 null — it is a full
   replication of it under harder (cross-substrate) conditions, and the
   transplant is called an outright FAILURE, not "underpowered."

## Stopping rule
Pilot on ONE world (Can't Stop — the world whose action grammar is most
opcode-decomposable, per prediction 3) at reduced n (per
`feedback_preflight.md` preflight doctrine) before committing to the full
4-world x 4-arm x 5-seed battery. STOP and report NOT ESTABLISHED without
running the remaining worlds if the executability gate (falsifier 2) fails
on the pilot — a substrate-incompatibility failure at the pilot stage will
not be fixed by more worlds. If the pilot clears the executability gate,
proceed to the full battery; STOP at the full battery's completion
regardless of outcome (no post hoc extension of n or seeds beyond the
preregistered 5/arm/world).

## Expected failure modes
1. Artifacts fail to execute at all against Ludus's action/state
   representations (most likely single failure mode, per
   `feedback_verbs_must_be_native.md` — D-5's opcodes are native to a
   register-machine genotype substrate, not to card/dice game trees).
2. Artifacts execute but the RAND control captures most of the gain (content
   effect does not survive the substrate boundary; only "having a library at
   all" transplants).
3. Rules audit (RULES_AUDIT.md) later finds a Priority-1 constant wrong in
   one of the four worlds, which does not undermine the machinery claim but
   voids any statement that named a specific commercial game correctly.
4. The 4-world solitaire battery is simply too small (echoes D-5's own G5
   underpowered problem at n=13); any positive point estimate with a CI
   touching zero should be reported as NOT ESTABLISHED, not as a pass.
5. Interface translation (arm IFACE) is itself under-specified or leaky —
   the hand-authored opcode-to-verb mapping could smuggle in solution
   knowledge not present in D-5's original artifacts, inflating IFACE's
   apparent advantage; this must be checked by comparing IFACE against an
   H0 arm that has ALSO been given the interface's native-verb vocabulary
   (but not the D-5 artifacts) — a "vocabulary-only" control not yet built
   into the arm list above and flagged here as a design gap.

## Compute estimate
Four worlds x four arms x five seeds = 80 runs. Ludus worlds are currently
single-turn/short-horizon solitaire (per RULES_AUDIT.md scope cuts: Can't
Stop is "a single turn from an empty board," not a full game), so each run
is expected to be on the order of 10^3-10^4 evaluations, consistent with
D-5's own M2/M1 metering (30k evaluations per non-control task in its P2
gate). Total estimated evaluations: ~10^5-10^6, single-machine, expected
wall-clock on the order of hours, not days — no GPU required (Ludus's
solvers and D-5's register-machine substrate are both CPU-bound per the
existing `ludus/bench/` and `agent_d5_blind/substrate/` code). The pilot
(one world, reduced n) should be budgeted at well under 10% of this total
before the stopping-rule decision point.

## Prior evidence that materially changed this design
`agent_d5_blind/VERDICT.md` gates G7 (frozen alien zero-shot transfer,
+5pp, p=0.26, NOT ESTABLISHED — measured WITHIN the D-5 substrate) and G9
(causal content-vs-order decomposition: shuffled retains 100%, random-
library retains 39%) together moved this design from "expect the D-5
library to transplant a double-digit-point gain" to "expect near-null
unless an explicit interface layer supplies the missing native-verb
correspondence, and even then expect the random-library control to eat most
of any apparent gain." Without G7/G9, this proposal would have proposed a
single naive-transplant arm and treated any positive delta as evidence of
content transfer; with them, the RAND control (falsifier 3) is the
load-bearing test, not the H0 comparison. `ludus/bench/RULES_AUDIT.md`
changed the scope claim: without it this proposal would have risked framing
results as claims about the named commercial games; with it, the claim is
explicitly restricted to the machinery, pending audit.

## Unresolved uncertainty
- No file search under the 15-op budget located D-5's original opcode
  list or the Ludus adapter/interface code (if any already exists) in
  enough depth to confirm whether a `Ludus <-> D-5` interface layer is a
  greenfield build or partially built; `ludus/bench/circuits.py` and
  `ludus/bench/worlds2.py` were listed but not opened, and could resolve
  this.
- Whether the RAND control's random-walk genotype generator can be
  faithfully reproduced against Ludus's action space, or needs to be
  rebuilt from scratch, is unresolved (D-5's generator lives in
  `agent_d5_blind/mutation/physics.py`, not opened in this pass).
- The vocabulary-only control flagged under Expected failure mode 5 is a
  known design gap, not yet resolved into a fifth arm; doing so would
  change the compute estimate and falsifier set.
- Whether Ludus's transfer_matrix.json (`ludus/atlas/transfer_matrix.json`,
  listed but not opened) already encodes a cross-world/cross-substrate
  transfer estimate that would sharpen or contradict prediction 3 is
  unresolved.

## Operation log (numbered; ops used / 15, documents opened / 12)
1. Bash `find F:/Prometheus -maxdepth 2 -iname "*ludus*"` — locate Ludus
   top-level paths.
2. Glob `**/*d5*findability*` (no path set) — no results (cwd scoping
   issue, informative failure).
3. Glob `**/*D5*.md` (no path set) — no results (same issue).
4. Glob `ludus/**/*.md` (no path set) — no results (same issue).
5. Glob `**/*.md` under `F:\Prometheus\ludus` — enumerated Ludus docs
   (RULES_AUDIT.md, BACKLOG.md, CIRCUIT_LEDGER.md, CIRCUIT_MATURITY.md,
   worlds atlas README + many world pages).
6. Glob `**/*d5*` under `F:\Prometheus\roles` — no results.
7. Glob `**/*findability*` under `F:\Prometheus` — timed out (ripgrep
   20s limit; informative failure, not retried against budget).
8. Grep `D-5|D_5|findability` under `F:\Prometheus\roles` — 3 files
   (Mnemosyne charter, Ergon charter, Techne fire log; not opened, low
   relevance signal from filenames/context alone).
9. Grep `frozen opcodes|primitive-extension|whole-program seed` under
   `F:\Prometheus` — 10 files, including two files under evidence_wiki
   (out of scope, not opened) and several under `ergon/gen1`/`ergon/gen0`
   (not opened — off-topic per filenames, unrelated Ergon generations).
10. Grep `D-5|D5 search agent|Family A has no slot` under
    `F:\Prometheus\incubation` — no results.
11. Bash `find F:/Prometheus -maxdepth 1 -type d` — top-level directory
    map; located `agent_d5_blind/`.
12. Bash `find F:/Prometheus/agent_d5_blind -maxdepth 2` — full D-5
    artifact-library directory structure (VERDICT.md, MANIFEST.md,
    task_generators/hidden_library.py, substrate/rm_fast.py + rm_vm.py,
    mutation/physics.py, results/*.json).
13. Bash `find F:/Prometheus/ludus -maxdepth 3 -not -path "*atlas_of_worlds*"`
    — full Ludus bench directory structure excluding the (724-file)
    worlds atlas.
14. Read `F:\Prometheus\agent_d5_blind\VERDICT.md` — DOCUMENT 1/12;
    primary source for the hypothesis, predictions, and falsifiers above.
15. Read `F:\Prometheus\ludus\bench\RULES_AUDIT.md` — DOCUMENT 2/12;
    source for the solitaire-scope and HYPOTHESIZED-rules confound
    defenses above.

Ops used: 15/15. Documents opened: 2/12. Unused document budget (10 more
opens available) was not spent because the 15-op ceiling was reached first;
the highest-value unopened candidates are listed under Unresolved
uncertainty above (`agent_d5_blind/MANIFEST.md`,
`agent_d5_blind/task_generators/hidden_library.py`,
`agent_d5_blind/mutation/physics.py`, `ludus/bench/circuits.py`,
`ludus/bench/worlds2.py`, `ludus/atlas/transfer_matrix.json`,
`ludus/docs/Worlds as Part of the Prometheus Strategic Roadmap.md`).
