# 01 -- Repository audit

Competitor: Claude Fable 5.2. Written 2026-11-13T02:18Z (UTC, from the clock). No subagents, no paid inference,
no GPU, no production engine run.

## 0. Checkout record (read this first)

| Item | Value |
|---|---|
| Reference commit required by the brief | `5633cc02a92e5206528d5d67905b4b5d37137b46` |
| Commit actually audited | `5633cc02a92e5206528d5d67905b4b5d37137b46` (verified with `git rev-parse HEAD` in the worktree) |
| Worktree | `F:/Prometheus-worktrees/rsi-bakeoff-fable-5.2`, branch `rsi-bakeoff/fable-5.2` (local only, not pushed) |

**Mismatch found and how it was resolved.** The session was started in `F:/Prometheus`, which is on branch
`vivarium/v0-2026-09-05` at `859a1bcf7` (a 2026-10-03 snapshot). That checkout did not contain the reference
commit at all, and no bake-off worktree existed. The reference commit exists on GitHub (`origin/main` is one commit
ahead of it). I ran `git fetch origin main` and created a new worktree pinned to the reference commit. Everything
below was read from that worktree. Nothing in `F:/Prometheus` was edited. The brief says "work only in the existing
isolated worktree"; none existed, so creating one is a deviation the operator should know about.

**Evidence grades used in this file.**

| Grade | Meaning |
|---|---|
| RAN | I executed the code or its tests at the reference commit in this session |
| READ | I read the code (and usually its tests) at the reference commit |
| DOC | I read a committed report; I did not read the code that produced the number |
| OFF-MAIN | The result is described on main but its rows or report live on another branch or another host |

Numbers quoted from reports are the reports' numbers. I re-derived none of them except where marked RAN.

## 1. The one-paragraph finding

Prometheus has measured the same four obstacles many times, and its own records say so plainly. No engine has
shown recursive improvement, and the seat chartered to find it (Aphrodite) withdrew the "RSI" name itself. The
strongest reusable asset for a self-improving engine is not an organism. It is **TFS-1**
(`roles/Aphrodite/beta04/tfs1/`): a typed functional program substrate with exact cost accounting, a promotion
operator that turns a learned sub-program into a callable primitive, an anti-unification compressor, a transplant
membrane and the control arms a recursion claim needs. Around it sit a world-demand foundry and a set of
evaluation kits (`rso/`) that already know how to refuse the program's historical false positives. What is missing
is any mechanism by which the engine's own search experience becomes durable search machinery.

## 2. What the historical record establishes

These are the facts a new architecture has to respect. Each is a repository result, with its source.

| # | Finding | Source | Grade |
|---|---|---|---|
| F1 | **Composition wall.** Seven substrates each failed to assemble the first mechanism made of two parts that are individually worthless: Ananke FLIP 0/290, z80atlas 0/960, SFE W2_K2 0/395, Crius 0/475,728 candidates, Tyche order-3 0 solves, Primordial 0, Aether <= 2/256 | `roles/Hestia/audit/2026-10-06/REPORT.md` Part 0 and Part 2 W1 | DOC |
| F2 | **Promotion works when supplied, and only then.** Aether: a planted component offered as a promoted primitive solves 8/8; the same component offered unmarked solves 0/8; no component 0/8 | `Aether/V2B/ROBUST01/S2A_RESULT.md` | DOC |
| F3 | **Reuse of a discovered component is not shown.** Aether S2b: `REUSE_NOT_SUPPORTED` (1/8) with the composition the search itself found | commit subject `ROBUST01 S2b RESULT`, `Aether/V2B/ROBUST01/S2B_RESULT.md` | DOC |
| F4 | **Stones are necessary, and acquiring them is the first failure.** TFS-1 with supplied stones crosses the composition step 13-15 of 15; without stones 0/120 and 0/15. Autonomous acquisition qualified only 7/15 (9/15, 8/15 at other seeds) | `roles/Aphrodite/beta04/SYNTHESIS.md` s2 | DOC |
| F5 | **Search coverage is the dominant repair.** Observational-equivalence pruning plus a refactoring-invariant extraction is the only cell at or above the bar at every seed (15/13/13) | same file, s3 | DOC |
| F6 | **Deciding what to learn is untested.** Every Beta-04 success had the decomposition supplied by the world | same file, s4 | DOC |
| F7 | **First-order inheritance transfers capability, not improvement.** An inherited library reaches 104 unseen families against 32, yet the next generation's own improvement falls from 56 to 10 | `roles/Aphrodite/beta02/R8_REPORT_AND_BETA02_CLOSE.md` | DOC |
| F8 | **Most of F7 is a headroom artifact.** 80-93% of the deficit disappears when all arms are scored on a common opportunity set; the inherited library ends at the highest competence | `roles/Aphrodite/beta03/BETA03_48H_CLOSE_SYNTHESIS.md` s3 Q1 | DOC |
| F9 | **The second-order chain breaks at representation.** A wrapped library entry has no extent at the next depth; promoting it to a one-node primitive restores extent | `roles/Aphrodite/science/arc3/ARC3_SYNTHESIS_2026-09-28.md` s1(f), s8 | DOC |
| F10 | **Improver parameters are inert.** Four variants of the improver's settings changed the selected schema in 4 of 12 cases, with held-out value differences of at most 4% | `roles/Aphrodite/science/compounding/rb6/RB6_LEVER_CHECK_RESULT.md` | DOC |
| F11 | **Worlds mostly do not pay for reasoning.** Cosmos: one register optimal everywhere. Ensorain: 0 world families need hidden state. Ludus: 2-step lookahead keeps >= 96% in 22/22 worlds | Hestia REPORT Part 2 W2 | DOC |
| F12 | **Supplied modules help; evolved modules are the wrong parts.** Ananke C4: search-acquired library present and live, never composed, 0/168; designed halves 2/32 | `rso/gen5/ananke/COORDINATION.md` | OFF-MAIN |
| F13 | **Reuse is real but undiscoverable in Crius.** Constructed reuse gives 49-50/50 against 24-36 fresh; native search 0/36; the first rewarded configuration is about 26 edits away with no gradient | `rso/gen5/SELECTION.md` s2 | DOC |
| F14 | **Controls that cannot fail have been shipped four times.** Each was caught by a challenge, not by its author | `rso/qualify/FALSIFIABILITY.md` | READ |

F12 needs care. `roles/Ananke/pte/c4/` at the reference commit holds the preregistration and code but no result
file. The result is on branch `ananke/p2b-2026-10-05`, and the C5T follow-up (4x budget) was never reported.

Two things the record does **not** establish, although summaries often read as if it did:

- It does not show that recursion is impossible. Beta-03's kill criterion was explicitly `NOT_MET` because the
  instrument failed its known-positive control.
- It does not show that a library hurts later learning. F8 retracts most of that reading.

## 3. Subsystem inventory

Each row answers the brief's seven questions. "Meaning preserved?" asks whether moving the component into a new
architecture keeps the scientific meaning its results were earned under.

### 3.1 Aphrodite -- RSI, abstraction compounding, improver evolution

| Question | Answer |
|---|---|
| Mechanism | Two engines. (a) Fold engine v1: enumeration inside one left-fold template; a least-general-generalisation step lifts a one-hole template into a proposal library that only reorders search. (b) TFS-1: typed lambda terms, bottom-up enumeration by size in a keyed order, promotion of learned sub-programs to primitives, anti-unification compression |
| Code and interfaces | `roles/Aphrodite/engine/` (`engine.py`, `improver.py`, `fair.py`, `a17.py`, `tribunal_t4.py`); `roles/Aphrodite/beta04/tfs1/` (`core.py`, `enum.py`, `library.py`, `compress.py`, `mutate.py`, `membrane.py`, `e3/organism.py`); `roles/Aphrodite/beta04/foundry/` |
| Demonstrated | First-order abstraction transplant on 5 unseen families (S4). Inheritance plus composition is a reliable stepping stone under constructed recurrence (A23, p = 0.0078). TFS-1 qualified as engineering: 15/15 known-answer tests |
| Negative results | F4-F10 above. `BOUNDED_RECURSIVE_SELF_IMPROVEMENT = NO` at Tiers 3A-3C. `TFS1_INSTRUMENT_QUALIFIED = NO` (7/15 against a bar of 12). Line renamed from "RSI" to "abstraction compounding" on 2026-09-27 |
| Could contribute | TFS-1 is the proposed base substrate. The foundry is the proposed task-world generator. R8 is the proposed second-order assay |
| Meaning preserved? | Yes for TFS-1 code, the membrane and the control arms: they are apparatus. No for any Aphrodite verdict: every one is scoped to its world and budget |
| Disposition | **REUSE** TFS-1, foundry, membrane, control arms. **REJECT** the fold engine as a substrate (`fair.py` states every library has "identical expressive power", so its libraries cannot change what is expressible) |
| Grade | TFS-1: RAN (6 tests) and READ. Fold engine: READ in part. Verdicts: DOC |

Details that matter for integration, all READ in `roles/Aphrodite/beta04/tfs1/`:

- `library.py` `Library.promote_body` makes a content-addressed entry with dependencies, lineage and depth. An
  entry whose expansion equals an existing one collapses to it (alias rule A1). Entries have at most two holes.
- `enum.py` `Enumerator.search` charges exactly 1 per candidate evaluated on dev examples. Hit charge equals
  static rank (tested).
- `enum.py` has optional observational-equivalence pruning (`oe=True`). It is **per task**: tables are rebuilt
  from each task's dev inputs. For lambda bodies it is a heuristic relative to a probe set, not exact. Its cost
  goes on a separate INFRA ledger that no economics comparison has yet charged.
- `enum.py` line 141 and 202-203: `oe_pruned_log` records every pruned term with its representative. This is a
  stream of candidate equations that nothing consumes today.
- `compress.py` `propose` ranks abstractions by corpus size reduction. It says in its own docstring that this is
  a simple count, not MDL.
- `e3/organism.py` already implements the arms `RANDOM-LIBRARY`, `SHUFFLED-HISTORY` and `RANDOM-ARCHIVE`.
- `membrane.py` exports a library, runs a recipient in a fresh process, and issues a no-donor-state receipt. It
  also has the exact sign-flip test (`flip_test`).
- Integration hazard, found by running it: the module is named `enum.py`. Starting Python with
  `roles/Aphrodite/beta04/tfs1/` as the working directory shadows the standard library's `enum` and breaks
  `import json`. Always run from `roles/Aphrodite/beta04/` as the design document says.

Measured throughput (`TFS1_THROUGHPUT.json`, DOC): about 38-94 thousand candidates per second pristine, falling to
about 10 thousand at size 8. Class sizes grow about 9.6x per size level pristine and about 11.4x with five library
entries. A five-entry library makes the size-8 class 3.4 times larger (18.2M against 5.4M).

### 3.2 Ananke -- compositional program search and reachability

| Question | Answer |
|---|---|
| Mechanism | 16-line register programs on a packet-tensor substrate, evolved by a plain GA across task cells. Counterfactual mirror-pair swaps locate where a bit is carried |
| Code | `prometheus/ananke/` (`engine.py`, `search.py`, `assays.py`, `lens_swap.py`, `oracle.py`); `roles/Ananke/pte/c4/` (`build_library.py`, `run_c4.py`, `reduce_c4.py`) |
| Demonstrated | Routed relay, causally supported and reproduced. An exact counterfactual tool. A protocol that separates "search cannot find" from "physics cannot do" (C2A) |
| Negative results | FLIP 0/290, XOR 0/83. One random edit kills a working program 62% of the time. C4 composition 0/168 (OFF-MAIN) |
| Could contribute | The C2A protocol and the swap assay as evaluation ideas |
| Meaning preserved? | The protocol yes. The substrate's results do not transfer to a typed functional language |
| Disposition | **REUSE the method, REJECT the substrate.** A 16-line flat genome with point mutation is the shape Hestia recommends stopping |
| Grade | DOC, with directory listings READ |

### 3.3 Aether -- deterministic artificial physics and causal propagation

| Question | Answer |
|---|---|
| Mechanism | A torus of 5-byte sites under a fixed physics law. One opcode writes a payload into a neighbour. Hash arbitration settles contests |
| Code | `Aether/` (197 Python files), `rso/aether/` |
| Demonstrated | Causal propagation without recoverable content (RX). Twin-world and counterfactual-parent instruments that caught three false positives. ROBUST01 S2a: promoted planted component 8/8 |
| Negative results | 98.7% of sites freeze. A winning write replaces its target, so inputs never combine: composition <= 2/256 under every law. S2b reuse not supported |
| Could contribute | Finding F2 is the cleanest evidence in the repository that **marking** a component as callable is what makes it usable. That is a design input, not code |
| Meaning preserved? | No. The physics is a copy-only medium; importing it would import its ceiling |
| Disposition | **REJECT as a substrate.** Keep F2 as evidence |
| Grade | DOC |

### 3.4 Nestor / Primordial -- evolutionary search and survival

| Question | Answer |
|---|---|
| Mechanism | Tensor-train "brains" tuned by random mutation and MAP-Elites; a byte soup where organisms must copy themselves |
| Code | `primordial/` (472 Python files), `roles/Nestor/` |
| Demonstrated | Heredity instruments (causal copy, byte provenance). Copy-direction coupling maintains function, 12/12 against 0/12 |
| Negative results | A do-nothing policy scores 107.75 against 98.76 for the best evolved brain. Replication claims fell from 1,031 runs to 2 real copiers on recheck |
| Could contribute | Cheat-control discipline; the lesson that a similarity test is not a copying test |
| Disposition | **REJECT as a substrate.** Maintenance of seeded code is not acquisition |
| Grade | DOC |

### 3.5 Bellerophon -- computational reproduction and capability retention

| Question | Answer |
|---|---|
| Mechanism | A Z80-like instruction soup of self-copying tape programs with tasks rewarded through a ledger |
| Code | `prometheus/z80atlas/`, `roles/Bellerophon/` |
| Demonstrated | A one-byte step (ECHO to INC) 58/320 against 0-1/320. Byte-exact replay, 114/114 |
| Negative results | The two-instruction step INC to COND_ONE: 0/960. From random starts 0/3,200 |
| Could contribute | The YOKED / SHUFFLED / RANDOM_REWARD control arms |
| Disposition | **REUSE the control design, REJECT the substrate** |
| Grade | DOC |

### 3.6 Cosmos -- evolving computational laws

| Question | Answer |
|---|---|
| Mechanism | Worlds with a delayed-match demand; an exhaustive symbolic-regression grammar mines "laws" over declared coordinates |
| Code | `prometheus/cosmos/` |
| Demonstrated | The C3 P1/P2 certificate (decode state and swap state to change behaviour), 5/5 planted controls |
| Negative results | 0/10 mined laws beat a zero-parameter rule written from the certificate's own economics. 721 worlds collapse to 8 behaviour classes |
| Could contribute | The rule "a mined law must beat the zero-parameter definition rung". My design mines equations; this rule applies directly |
| Disposition | **REUSE the acceptance rule.** REJECT the worlds |
| Grade | DOC |

### 3.7 Ensorain -- adaptive organisms and environmental interaction

| Question | Answer |
|---|---|
| Mechanism | A world-genome grammar generates tensor worlds; a fixed menu of 490 online regressors competes on one replayed experience stream against a null ladder |
| Code | `ensorain/` (201 Python files) |
| Demonstrated | The collider design: one stream replayed to every competitor, with a null ladder |
| Negative results | A tuned batch fit beats 9/9 promoted specimens. 179/181 admitted worlds have delay 0 |
| Could contribute | Common-stream replay to every arm, which is the same idea as TFS-1's keyed common-random-number order |
| Disposition | **REJECT as a substrate.** The principle is already in TFS-1 |
| Grade | DOC |

### 3.8 Crius -- learned procedures and inheritance

| Question | Answer |
|---|---|
| Mechanism | An evolving bytecode organism in a workspace sandbox. Measures whether stored machinery makes later tasks cheaper |
| Code | `crius/` (`evaluate.py`, `search.py`, `vm.py`, `qualify.py`), tests in `crius/tests/` |
| Demonstrated | A reuse assay that rejects known cheats. Constructed reuse is real (F13) |
| Negative results | Reuse is not accessible to mutation plus splice: 0/475,728. A quitting program once scored 3.00 against 2.97 for real reuse |
| Could contribute | `evaluate.py` `causal_controls` implements conditions E-J: ablate each artifact alone, ablate all, artifact-only transplant, full transplant, code only, compute matched, storage matched. `run_lifetime` implements FRESH / ACCUMULATED / RESET / SCRAMBLED |
| Meaning preserved? | The battery is substrate-independent in design. The code is tied to the Crius VM |
| Disposition | **REDESIGN:** port the A-J battery as a specification onto TFS-1 artifacts. Do not import the VM |
| Grade | READ (`evaluate.py` lines 129-262) |

### 3.9 Theseus -- generative search and adaptive generator selection

| Question | Answer |
|---|---|
| Mechanism | 40 claim generators in 10 families; a bandit reshuffles the active set by per-generator yield. Separately, `theseus/synth` collides rule programs |
| Code | `theseus/bandit/` (`epsilon_greedy.py`, `yield_proportional.py`), `theseus/generators/`, `theseus/synth/` |
| Demonstrated | Three gated control instruments. A composition detector that flags 40/40 planted cases |
| Negative results | The deep arm matches random. Compositions 0/1011 in every arm (`theseus/runs/composition_v2_2026-10-08/VERDICT.md`) |
| Could contribute | The bandit as a budget allocator between induction operators. This is parameter tuning, and my design reports it as such, never as self-modification |
| Disposition | **REUSE the bandit idea only.** It is about 100 lines; re-implementing it is cheaper than importing the package |
| Grade | DOC, directory READ |

### 3.10 Sigma Kernel -- provenance, knowledge representation, verification

| Question | Answer |
|---|---|
| Mechanism | A content-addressed, append-only symbol store with single-use capability tokens and three-valued gates |
| Code | `sigma_kernel/sigma_kernel.py` and 56 other Python files |
| Demonstrated | A record format that carries caveats inside the hash |
| Negative results | Computes nothing about a symbol's content. A capability double-spend under Postgres was found by reading and never fixed or race-tested (Hestia REPORT 3.6, D1) |
| Could contribute | The record shape (claim, status, caveat, provenance) for the engine's own theory ledger |
| Disposition | **REDESIGN:** copy the record shape into a single-process ledger. Do not depend on the kernel until the race is fixed |
| Grade | DOC, README READ |

### 3.11 Themis / Moonshot -- computational reasoning and hidden-state tasks

| Question | Answer |
|---|---|
| Mechanism | Designed: survival-only evolution of mechanisms that depend on retained hidden information; an "integer neural primitive" |
| Code | `moonshot/nf/`, `moonshot/epoch/`: a native execution fabric on Postgres with epoch replay. No organism, world-task or primitive code |
| Demonstrated | Infrastructure only (41 Postgres tests, mutation testing). Themis's own status says "no science run" |
| Negative results | None, because nothing scientific ran. Hestia graded it INSUFFICIENT_EVIDENCE |
| Disposition | **REJECT for this purpose.** Nothing to reuse that Fabric does not already provide |
| Grade | DOC, directory READ |

### 3.12 Hestia -- developmental cognition research and the 25-engine audit

| Question | Answer |
|---|---|
| Mechanism | An audit, not an engine: 22 dossiers with file-and-line citations, and a Composition Ladder proposal |
| Code | `roles/Hestia/audit/2026-10-06/` |
| Demonstrated | The cross-substrate diagnosis (F1, F11) and three named escapes from the wall: structured credit, modularity through promotion, lifetime learning |
| Limits it states itself | No engine was run. Same model family as the engine authors. The Valiant and Feldman citations are from memory |
| Could contribute | The decision rule in Part 5 Step 3, and the ladder rungs as a world-admission target |
| Disposition | **REUSE as the main map of dead ends** |
| Grade | DOC (read in full) |

### 3.13 RSO / Palamedes -- independent evaluation and causal attribution

| Question | Answer |
|---|---|
| Mechanism | An observatory that qualifies instruments on constructed positives and attacks them before use |
| Code | `rso/adversary/` (five attacks, runner), `rso/qualify/falsifiable.py`, `rso/completeness/` (sealed manifest, verifier), `rso/registry/` |
| Demonstrated | Four engines assessed. Every instrument qualified on constructed positives; no evolved subject passed. Gen-5 (cumulative discovery) closed with no substrate selected |
| Could contribute | `rso.adversary.attacks`: `drop`, `duplicate`, `rewrite_derived`, `constant_detector`, `scrub_answer`. `rso.qualify.falsifiable`: `cannot_emit`, `constant_passes`, `oracle_fails`, `reads_answer`, `trusts_derived`, `near_miss_rejected`. `rso.completeness.manifest.build` and `verify` |
| Meaning preserved? | Yes. These are generic functions over rows and detectors |
| Disposition | **REUSE directly** for the evaluator of the new engine |
| Grade | RAN (`rso/qualify/tests` 14 tests OK; `rso.adversary.tests.test_attacks` 24 tests OK) and READ |

### 3.14 Fabric -- distributed experiment infrastructure

| Question | Answer |
|---|---|
| Mechanism | A durable work queue on Postgres. Workers pull tasks, run them at a pinned commit, and the runtime uploads artifacts |
| Code | `fabric/` (`store.py`, `worker.py`, `executors.py`, `gateway.py`, `schema.sql`), frozen at tag `fabric-v0.2` |
| Demonstrated | A script executor that runs a repository module at a pinned SHA with no shell and an environment allow-list |
| Limits | Frozen: no new features. Themis records that every program login is the Postgres superuser and the executor is not sandboxed |
| Could contribute | Distribution of experiment arms across the fleet. One task per (arm, seed) |
| Disposition | **REUSE as is,** for M1 and later. M0 fits on one machine and should not depend on it |
| Grade | DOC (README and FREEZE READ) |

### 3.15 Serendipity Foundry and the SFE ecology

| Question | Answer |
|---|---|
| Mechanism | A provenance-heavy experiment ledger hosting worlds, with flat bytecode players evolved by a tournament GA |
| Code | `SerendipityFoundry/` (197 Python files), `vivarium/`, `proteus/` |
| Negative results | Two-value memory unreachable: 0/18,266 useful single edits; W2_K2 0/395 though a 12-instruction hand solution exists. Each row costs 95-193 s of round-trips for 0.1 s of science |
| Could contribute | Sealed predictions and loser-preserving selection as record-keeping rules |
| Disposition | **REJECT the organism side.** Adopt sealed predictions as a rule |
| Grade | DOC |

### 3.16 Other engines found by inspection

| Engine | Path | One-line disposition |
|---|---|---|
| Tyche | `tyche/` | Marginal-gain ruler and interaction-order certificate are worth keeping as ideas. Organism: order-3 needle, 0 solves |
| Ares | `ares/` | One-bit latch ceiling. Transplant recovers a median 0.019 of function because edges are rewired at random |
| Ludus | `ludus/` | Exact value-retention bench. Worlds are shallow |
| incubation / D-VM | `incubation/`, `incubation_d/` | The right idea (a learned transform is data a later transform can edit) and no working instance: 0.037% of length-5 meta-programs are distinct |
| forge lineage | `forge/`, `agents/hephaestus/` | The measured example of cosplay: a constant beats the best tool, 0/10 tiers compose |
| alien_circuitry | `alien_circuitry/` | Needs the full answer table first |
| agent_d2..d5 | `agent_d*_blind/` | D-5's "learning" was a warm-start cache: shuffled history keeps all of it. Source of the shuffled-history control |
| Pan, Atlas, Mnemosyne | `pan/`, `atlas/`, `evidence_wiki/` | Discovery and memory layers for the fleet. Not engine components |

All DOC, from the Hestia report.

## 4. Prior Phase 3 architecture proposals, read as competing hypotheses

| Proposal | Path | Its hypothesis | What I take | Where I disagree |
|---|---|---|---|---|
| FABLE-5.1 | `docs/phase3/design/FABLE-5.1/RSE_ARCHITECTURE.md` | Study within-lifetime construction; establish demand, expressibility, reach and detectability before any open question; descend from existence proofs | Descent from existence proofs. "Recursive sagacity is a property with a test, not a machine" | Its workspace machine is a stored-program register organism. That is the flat-genome shape with the reach problem it names itself |
| OPUS-5.5 | `docs/phase3/design/OPUS-5.5/RSE_ARCHITECTURE.md` | One deeply instrumented developmental graph machine in which development instructions are ordinary instructions | The ablation lattice: every affordance is a switch on one code path | Rewrite-of-rewriters by mutation is what Eurisko tried. Throughput under full instrumentation was unmeasured |
| ASTRA-6.0 | `docs/phase3/design/ASTRA-6.0/RSE_ARCHITECTURE.md` | Three substrate tracks, six questions; a nested S / U / V causal criterion | The S / U / V criterion and its clamp-and-rescue test. I adopt it in file 06 | It deliberately selects no engine |
| Synthesis v0.4 | `docs/phase3/synthesis/ENCELADUS-DIONYSUS-v0.4/` | Thin federation, strong R0, claim-specific controls | "Register answers per claim, never veto by pedigree" | It is an evaluation contract, not an engine |

All three designs are observatories. None proposes a mechanism by which an improver changes itself. That gap is
what this bake-off asks for.

## 5. The obstacles, mapped to what would have to be true

| Obstacle named in the brief | What the record shows | Requirement on a new architecture |
|---|---|---|
| Parts work alone but cannot be discovered or composed | F1, F4, F12 | Parts must be found by something other than end-to-end fitness |
| No gradient toward intermediates | F1, F13 | Credit per example or per sub-goal, not one scalar per lifetime |
| Representational ceiling blocks second-order abstraction | F9 | A learned unit must become a true primitive of size one |
| Inherited parts do not change future discoverability | F7, F8 | Score on a common opportunity set; measure discovery rate, not end state |
| No cumulative lifetime learning | Hestia W1 escape (c) is untested anywhere | Experience inside a lifetime must leave durable machinery |
| Gains from compute, not mechanism | TFS-1 charges exactly; OE cost is on an uncharged ledger | One ledger for everything, including the cost of learning |
| Worlds reward memorisation or supplied answers | F6, F11 | World admission gate with null ladder; decomposition never supplied |
| Stored knowledge versus changed machinery | Not separated anywhere in the repository | Define the two operationally and ablate each alone |
| Evolving algorithms versus evolving discovery | F7 | Endpoint is discovery cost on unseen families |

## 6. What I verified by execution

| Check | Command (from the worktree) | Result |
|---|---|---|
| TFS-1 promotion, alias, cost ledger, compressor, determinism | `cd roles/Aphrodite/beta04 && python -m tfs1.tests.run_tests test_promotion_semantics_random test_alias_collapse_and_depth test_cost_ledger_exact test_compressor_planted_kat test_compressor_function_hole test_enumerator_determinism_and_crn` | 6 PASS, 0 FAIL |
| RSO falsifiability checks | `python -m unittest discover -s rso/qualify/tests -t .` | 14 tests OK |
| RSO attack functions | `python -m unittest rso.adversary.tests.test_attacks` | 24 tests OK |
| Redundancy in TFS-1's search space | `rsi_bakeoff/evidence/probe_oe.py` (my script; imports TFS-1 unmodified) | see below |

The test runner writes a `_PARTIAL.json` results file; I deleted it afterwards, and `git status` was clean before
I added `rsi_bakeoff/`.

**Probe result** (`rsi_bakeoff/evidence/probe_oe_n6.json`; 0.4 CPU-seconds; 8 random input lists):

| Root type | Size | Syntactic terms | After commutative canonicalisation | Distinct behaviours on the probe inputs |
|---|---|---|---|---|
| Int | 4 | 796 | 658 | 184 |
| Int | 5 | 9,324 | 6,723 | 507 |
| Int | 6 | 80,880 | 55,995 | 3,927 |
| List | 6 | 9,057 | 8,036 | 1,452 |
| Bool | 6 | 30,444 | 21,357 | 107 |

Three readings, with their limits:

1. At size 6, about 14 of every 15 Int-valued candidates repeat a behaviour already seen. The figure is an upper
   bound on redundancy: 8 inputs can merge terms that differ elsewhere.
2. The redundancy factor is large but roughly constant. Growth per size level falls only from about 8.3x to about
   7.7x. Removing redundancy therefore buys roughly one extra size level, not an unbounded gain. File 08 uses this
   number against my own proposal.
3. The prune log already contains general laws nobody wrote down, for example `(head (rev xs)) => (last xs)` and
   `(len (rev xs)) => (len xs)`, among 17,646 pruned pairs. The foundry hand-codes seven such rule families
   (`roles/Aphrodite/beta04/foundry/tenum.py`, `PRUNE_RULES` P1-P7). The engine could learn them instead.

The 55,995 figure matches `TFS1_THROUGHPUT.json` exactly, which confirms the probe counted the same space.

## 7. Unresolved questions from the audit

1. Ananke C5T (composition at 4x budget) has no committed result. If it found composition, F12 weakens.
2. `roles/Hestia/audit/2026-10-06/RESPONSE_TO_EXTERNAL_REVIEWS_2026-10-08.md` amends the audit (M1-M7). I read the
   summary of the amendments in the report, not the 517-line response.
3. Aphrodite's Beta-05 (autonomous stone discovery) is named as the next question and has no record at this
   commit. My proposal overlaps it. The operator should decide whether they are one line of work.
4. The foundry's and TFS-1's interpreters were written independently, and the A/B conformance test between them
   is described as joined by a coordinator. I did not find and run that joined test.
5. I did not read the four forensic intake packages under `docs/phase3/intake/`. The Hestia report and the
   Phase 3 challenges document summarise them.
