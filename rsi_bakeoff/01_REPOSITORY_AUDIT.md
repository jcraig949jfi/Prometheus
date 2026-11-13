# 01 — Repository audit

Author: Claude Opus 5.5 (Claude Code session), independent bake-off entrant.
Written 2026-11-13 (UTC clock at writing: 2026-11-13T02:16Z; operator date 2026-11-12 local).

## 0. Checkout provenance (read first)

| Item | Value |
|---|---|
| Reference commit requested | `5633cc02a92e5206528d5d67905b4b5d37137b46` |
| Checkout the session started in | `F:/Prometheus`, branch `vivarium/v0-2026-09-05`, HEAD `859a1bcf7`, dirty tree with ~55 untracked scratch files. **This is not the reference commit.** |
| What I did | `git fetch origin main` (objects arrived; the local `origin/main` ref update failed with "incorrect old value", a concurrent writer, so no ref was moved). The reference commit then existed locally and is an ancestor of remote `main` (`9884ac934`). I created a **new isolated worktree** `F:/Prometheus-worktrees/rsi-bakeoff-opus` on a new local branch `rsi-bakeoff/opus-5.5-2026-11-12`, at exactly `5633cc02a`. |
| Audited tree | `5633cc02a` (verified with `git rev-parse HEAD` inside the worktree before reading and again before writing). |
| Nothing pushed, merged or deployed. No production code, frozen test, ruling or evidence file was modified. The only new files are these eight under `rsi_bakeoff/`. |

No pre-existing "isolated bake-off worktree" was present (`git worktree list` searched for bakeoff/rsi names), so I made one rather than write into the operator's dirty canonical checkout. If the operator intended a different worktree, the documents can be moved unchanged; they cite paths relative to the reference tree.

## 1. Method and evidence tiers

Breadth from metadata (`git ls-files` counts, git log subjects since 2026-10-06, document headers), depth on the components my final architecture reuses. Tiers used throughout:

- **OBSERVED** — I read the code, or ran the tests, in this session.
- **REPORTED** — a committed repository document states it; I did not re-derive it.
- **DESIGNED** — proposed in a document; no executed evidence.

Tests I ran (CPU, seconds to a minute each; no engine campaigns were run):

| Suite | Command (from worktree root) | Result |
|---|---|---|
| Aphrodite engine | `cd roles/Aphrodite/engine && python -m pytest -q tests` | 49 passed (19 s) |
| Aphrodite W5P primitive promotion | `cd roles/Aphrodite/engine && python -m pytest -q w5p/tests` | 9 passed, 1 skipped (20 s) |
| RSO adversarial kit (attacks, mutants) | `python -m pytest -q rso/adversary/tests/test_attacks.py rso/adversary/tests/test_mutants.py` | 27 passed (5 s) |
| Crius sandbox | `python -m pytest -q crius/tests` | 41 passed (60 s) |

Python 3.12.10, Windows host. Worktree remained clean afterwards (`git status --porcelain` empty).

What I did not read: the bulk of `roles/Nestor/campaigns` (7k files), Aether GPU receipts, Ensorain/Cosmos run data, the 77k lines of Phase-3 design text beyond headers and decision sections. For engines I did not open, I rely on Hestia Audit 1 (`roles/Hestia/audit/2026-10-06/REPORT.md`, which cites file:line in 22 dossiers) and on later campaign closeouts, and say so.

## 2. The headline facts the architecture must respect

1. **The composition wall is the program's most replicated result** (REPORTED, Hestia Audit 1 Part 0/W1): eight substrates find one-step mechanisms and none assembles a two-part mechanism whose parts are individually worthless — Ananke FLIP 0/290, z80atlas COND_ONE 0/960, SFE W2_K2 0/395, Crius 0/475,728 candidates, Tyche order-3 0, Primordial no cue reader, Aether ≤2/256, Theseus 30b 0/120 per arm (`theseus/runs/composition_v2_2026-10-08/VERDICT.md`, OBSERVED). Hestia's named escapes: (a) structured / non-scalar credit, (b) modularity — promote a solved unit to a callable primitive, (c) within-lifetime learning.
2. **Later work narrowed it, and did not overturn it.**
   - Ananke PTE-C4: 0/168 two-stage solutions with no library, with duplication, and with a search-acquired RELAY/HOLD library; designed halves 2/32 (REPORTED, `ops/campaigns/C-019/CLOSEOUT.md`). The parts that search acquired were the wrong parts.
   - Aphrodite Beta-04 (`roles/Aphrodite/beta04/SYNTHESIS.md`, OBSERVED): when stones are supplied, composition is reachable (13–15/15). The **first demonstrated failure is stone acquisition**. Its causes are search coverage of the stone's size class (1e6 covers ~7%) and an extraction rule that is not invariant to refactorings. The decomposition was supplied, and autonomy is "low".
   - Aether ROBUST01 (`Aether/pivot/AETH_ROBUST01_REVIEW_2026-10-18.md`, OBSERVED): a law change made planted composition position-robust. Discovered compositions were *not* reusable (S2b P 1/8).
   - Crius (C-019): the reuse advantage of a *hand-built* stored procedure is real (49–50/50 vs 24–36). Native discovery is inaccessible (a ~26-edit valley, 0/36).
3. **Engine-scale RSI has been attempted, carefully, and has not been established** (Aphrodite `STATUS.md`, OBSERVED):
   - BOUNDED_RECURSIVE_SELF_IMPROVEMENT = NO (Tiers 3A–3C).
   - BOUNDED_RSI not established (A15–A17; NO / UNTESTABLE on catalog supply).
   - The improver-parameter levers that were tested are **practically inert**: hole count, selection statistic and 2-step lookahead change held-out value by ≤4%, inside noise, because candidate menus are 4–9 items, all inside G1's span (`science/compounding/rb6/RB6_LEVER_CHECK_RESULT.md`).
   - The RSI toys (`science/rsi/RESULTS_2026-09-17.md`): a parametric self-improver did about what random local search does (42.5% of random perturbations matched its generation-1 median). **A leaky accounting channel was exploited within one generation**; an independent counter caught it.
4. **What did work in abstraction compounding is narrow and informative** (Aphrodite ARC3 synthesis, OBSERVED):
   - Inheritance + composition + *recurrence that validation can see* is a reliable, generic, structure-specific stepping stone (A23: G1 YES, GENERIC 3/3, G1_NC 0/10).
   - The composition move was a **designer edit to the improver**.
   - Second order breaks at **representation depth**; promoting a solved schema to a one-node primitive (W5P) restores extent.
   - Capability numbers are budget-relative: there is a walk "coverage cliff".
   - Hestia R8: inheriting the learned library cut the next generation's own learning from 56 families to 10. **Inheritance substituted for improvement.**
5. **The instruments are the strongest asset; the organisms are the weakest** (Hestia Part 0 item 1; Part 4 ranking). Every positive claim in the record survived only because of planted positives, shams, transplants, paired common-random-number designs and adversarial review.
6. **Power is the hidden gate** (C-019 closeout): a constructed positive at 2/32 needs ~107 searches per arm for 80% power. Any design whose success events are rare per run is unaffordable to *test*, even if it works.

## 3. Subsystem inventory

Legend for the last column: **REUSE** (take as is), **REDESIGN** (take the idea, rebuild), **REJECT** (not for this architecture; it may keep value elsewhere).

### 3.1 Aphrodite — engine-scale RSI, abstraction compounding, improver evolution
- **Mechanism:** enumerative search over a one-accumulator left-fold DSL (`engine/basis_v4.py`, 345 lines). The library (`engine/fair.py` `KLib`) is an ordered proposal list *walked first*, with a complete fallback: "every library has identical expressive power" (fair.py docstring, OBSERVED). The improver `a17.donor` (`engine/a17.py:453`) runs observe-search, then behaviour-classing with certificates (`certified_classes`, `cert.py`), then single-hole LGG schema derivation (`tier3d.derive_schemas`), then paired-cost selection with a one-sided 95% lower bound (`select`).
- **Interfaces:**
  - `Escrow` (charge-metered budget, `engine.py:82`);
  - disjoint entropy domains for dev / search / tribunal (`engine.py:52-66`);
  - common-random-number keyed walk order (`fair.py:key/keyed`);
  - `Cell` (paired unit) and `paired_summary`;
  - the content-addressed `Artifact` membrane (`engine.py:127`);
  - W5P `promote.py`: a content-addressed promoted primitive whose evaluation is *exactly* its expansion, plus an independent evaluator that tests the contract.
- **Demonstrated:** S4 ABSTRACTION_TRANSPLANT YES; TRANSFERABLE_SEARCH_LEVERAGE YES_LOCAL; A23 recurrent stepping stone YES under constructed recurrence.
- **Negative:** BOUNDED_RSI NO / UNTESTABLE; G1_STEPPING_STONE NO under natural supply; R8 substitution; improver levers inert; RB-5 says the fold DSL cannot express independent worlds (EC/OEIS); Beta-04 acquisition failure.
- **Contribution:** the *experimental protocol* — membrane, escrow, entropy separation, CRN pairing, sham donors, R8 "enable vs substitute" test, promotion semantics, and the rule that an improver must be a typed data object edited through a validated interface (RB-6 §2.6).
- **Meaning preserved if integrated?** Yes for the protocol pieces, which are substrate-agnostic. No for the fold DSL as a substrate: its library is a reordering of a fixed space, so "learning" there can only ever be efficiency.
- **Disposition:** **REUSE** the protocol code patterns (escrow, entropy domains, keyed CRN, membrane, promotion contract). **REJECT** the fold DSL as the M0 substrate (representational ceiling RB-5). **REDESIGN** the improver as a program rather than a parameter genome (§5 of 03/04).

### 3.2 Ananke — compositional program search and reachability (PTE)
- **Mechanism:** 16-line register programs, plain GA, across task cells; counterfactual mirror-pair swaps (REPORTED via Hestia 3.4).
- **Demonstrated:** routed RELAY, size-free, causally supported.
- **Negative:** FLIP 0/290, XOR 0/83; C4 0/168; "one random edit kills a working program 62%".
- **Contribution:** the "search cannot find vs physics cannot do" protocol (C2A), and the counterfactual swap tool.
- **Disposition:** **REJECT** as substrate (needle landscape, owner unavailable since 2026-10-09). **REUSE** the C2A *idea* as the representational-ceiling vs search-bottleneck discriminator, implemented natively (hand-built positive in the same DSL, then searched-for).

### 3.3 Aether — deterministic artificial physics, causal propagation
- **Mechanism:** GPU field physics with contest/fold write laws; twin-world / counterfactual-parent / value-provenance stack.
- **Demonstrated:** C-018 CAUSAL_PROPAGATION; ROBUST01 S2a CUMULATIVE_ACQUISITION_ADVANTAGE with a *planted* component.
- **Negative:** discovered compositions not reusable (S2b 1/8); held-out generality 1/40.
- **Disposition:** **REJECT** for this engine: GPU-bound, a physics substrate whose "computation" is not program-like, and no improver concept. Its replay-audit discipline (57/57 MATCH) is the model for M1 replay.

### 3.4 Nestor / Primordial — evolutionary search and survival
- **Negative** (REPORTED): do-nothing policy 107.75 beats best evolved 98.76; spontaneous replication withdrawn; Z80 CW01 cycles closed INCONCLUSIVE / DESIGN UNREACHABLE.
- **Disposition:** **REJECT** as substrate. **REUSE** the lessons: "similarity is not copying"; count-fixing damage rulers manufacture coordinates.

### 3.5 Bellerophon — reproduction and capability retention
- **Negative:** E-BEL-REPL-01 K3 had no route to SURVIVES (errata c776cea6a), a design whose PASS was unreachable.
- **Disposition:** **REJECT** substrate. **REUSE** the lesson as a requirement: every verdict needs a demonstrated attainable PASS (a planted positive).

### 3.6 Cosmos — evolving laws
- **Negative:** 721 worlds collapse to 8 behavioural classes; one register optimal; location bias explained an apparent law.
- **Disposition:** **REJECT**. The lesson is world demand: a world that a reflex solves teaches nothing.

### 3.7 Ensorain — adaptive organisms
- **Negative:** a constant predictor beat the organisms, which gave the constant-twin rule; 0 grammar families need hidden state.
- **Disposition:** **REJECT** substrate. **REUSE** the constant-twin baseline in every comparison.

### 3.8 Crius — learned procedures and inheritance
- **Mechanism:** register bytecode VM with a persistent Workspace and BlockStore; recorded executable blocks (`crius/vm.py`, 705 lines, OBSERVED). Search by mutation + splice (`crius/search.py`).
- **Demonstrated:** hand-built stored procedure carries a reuse advantage; ablation removes it, transplant carries it.
- **Negative:** discovery 0/36; WORLD_DEMAND_NOT_QUALIFIED; auto-calibration and the free simulator did hard parts (`vm.py:461`, `:490`); "every metric was gamed".
- **Contribution:** the reuse assay (RELAY, A–J controls, neutral-edit rescoring) — "did a stored mechanism make later learning cheaper?"
- **Disposition:** **REUSE** the assay design (savings, ablation, transplant, neutral-edit rescoring) as the template for my "inherited improvements disabled" and knockout arms. **REJECT** the VM.

### 3.9 Theseus — generative search, adaptive generator selection
- **Negative:** deep arm indistinguishable from random; 14/95 concepts compile to one 2-rule program; composition 0/120 per arm with a gate-passing detector.
- **Disposition:** **REJECT** substrate. **REUSE** the detector-gate pattern: a planted positive flagged 40/40 and negatives 0/40 before arms are read.

### 3.10 Sigma kernel — provenance, verification
- **Mechanism:** content-addressed append-only symbol store, single-use capability tokens, three-valued gates.
- **Defect** (REPORTED, Hestia D1): capability double-spend race under Postgres (`sigma_kernel.py:833/837` then `:899`).
- **Disposition:** **REJECT for M0** (a hashed JSONL ledger suffices; the race defect is unresolved). Possible M2 evidence sink after the compare-and-set fix.

### 3.11 Themis / Moonshot — hidden-state reasoning
- **REPORTED:** 0 lines of organism/primitive code; the floor task is a 1-bit latch.
- **Disposition:** **REJECT** (nothing to integrate). The hidden-state task *idea* is a candidate M2 domain.

### 3.12 Hestia — audit and developmental cognition
- **Contribution:** the composition-wall diagnosis, the Composition Ladder (R0–R4), and the decision rule "if only E-a (curriculum) works, say it is designed reasoning with extra steps".
- **Disposition:** **REUSE** the ladder logic as the M2 transfer domain and the three-escape framing as the design target. My architecture is an E-b (promotion) + reflexive-improver bet.

### 3.13 RSO / Palamedes / Argus / Pallas — independent evaluation
- **Mechanism:** an Observatory that owns evaluation, attribution and provenance, and never supplies solutions.
  - `rso/adversary`: deterministic kit, OBSERVED tests pass. Attacks DROP / DUPLICATE / REWRITE_DERIVED / CONSTANT / SCRUB_ANSWER, with verdicts REJECTED / LIMITATION / SURVIVED / VACUOUS / ERROR / NOT_APPLICABLE.
  - A registry of qualified instruments.
  - The integrator reproduces and mutates every packet.
- **Demonstrated:** caught 13/18 historical defects automatically; Aether audit 57/57 MATCH.
- **Disposition:** **REUSE as the independent evaluator owner.** The kernel's acceptance and the final held-out verdicts are run by an RSO seat, not by the engine author. The adversarial kit gets new targets for the engine's evaluator.

### 3.14 Fabric — distributed experiment infrastructure
- **Mechanism:** Postgres-backed durable task queue. One live attempt per task; leases in the DB; pinned detached worktree per base SHA; the runtime (not the model) uploads artifacts (`fabric/README.md`, `store.py` 586 lines).
- **Disposition:** **REUSE for M1/M2** fan-out of independent meta-search replicates and evaluation cells (embarrassingly parallel, pinned SHA). **Not needed for M0**, which runs on one host.

### 3.15 Serendipity Foundry, Nyx, forge lineage, incubation, alien_circuitry, D-series, Tyche, Herakles, Ares, Odysseus, Ludus, z80atlas
- All REPORTED via Hestia Audit 1 as SALVAGE_COMPONENT.
- Every one except Tyche and Ares is a dead end as a substrate.
- Reusable instrument ideas:
  - Tyche's interaction-order certificate;
  - D-series shuffled-history and random-library ablations (D-5: "shuffled history keeps 100% of gain", the canonical warning that apparent learning can be a non-learning artifact);
  - forge's constant decoy (75/186 ≥ best tool 74);
  - Ludus's exact value-retention ruler.
- **REJECT** all as substrates for this engine.

## 4. Implemented vs proposed (selected components only)

| Component I reuse | Implemented and tested? | Evidence |
|---|---|---|
| Escrow / charge metering | Yes | `engine.py:82`, exercised by 49 engine tests (OBSERVED) |
| Disjoint entropy domains | Yes | `engine.py:52-66` (OBSERVED) |
| Keyed CRN order + paired cells | Yes | `fair.py` (OBSERVED); frozen by AMENDMENT 13 |
| Content-addressed artifact membrane | Yes | `engine.py:127`, `tests/test_membrane.py` (OBSERVED) |
| Primitive promotion with exact-expansion contract | Yes | `w5p/promote.py`, 9 tests pass (OBSERVED) |
| Improver-as-typed-data + frozen interpreter (RB-6 §4.1) | **No** — DESIGNED only | `science/compounding/rb6/IMPROVER_EVOLUTION_PROGRAM.md` |
| Adversarial evaluator kit | Yes | `rso/adversary`, 27 tests pass (OBSERVED) |
| Crius reuse-assay control battery | Yes, Crius-specific | `crius/evaluate.py`, 41 tests (OBSERVED); must be re-implemented for a new DSL |
| Fabric queue | Yes | `fabric/` (REPORTED; tests not run here, needs Postgres on M1) |

## 5. Known obstacles: where each lives in the record

| Obstacle named in the brief | Strongest record instance |
|---|---|
| Works individually, cannot be discovered/composed | Crius (hand-built yes, discovered 0/36); Beta-04 (composition with supplied stones 13/15; acquisition fails) |
| No gradient to intermediates | Crius part values −0.001/−0.002/−0.057 → +1.14 together; Ananke 62% lethal single edits |
| Representational ceiling to 2nd-order abstraction | Aphrodite G3 has no extent in W5 (depth wall); W5P promotion restores extent |
| Inheritance that does not change discoverability | R8 (56 → 10); A19 G1_STEPPING_STONE NO under natural supply; Ananke C4 "wrong parts" |
| No cumulative lifetime learning | Moonshot (no code); Odysseus (no plasticity) |
| Gains from compute, not mechanism | A23 capability ≥330–447x is "budget-relative, a walk-cliff quantity"; RSI toy random-perturbation floor |
| Worlds rewarding memorisation / supplied solutions | Theseus 14/95 concepts → same program; R6 oracle shipped `truth` in the probe; Beta-04 decomposition supplied |
| Stored knowledge vs machinery change | Aphrodite: the improver is code, only the library changes (RB-6 §1: "Aphrodite today is L1") |
| Evolving algorithms vs evolving the ability to discover them | No instance in the record of the latter. RB-6 V5-b "not demonstrated anywhere in the surveyed literature" |

## 6. Prior Phase-3 architecture proposals (treated as competing hypotheses)

- **OPUS-5.5 (Epimetheus)** `docs/phase3/design/OPUS-5.5/RSE_ARCHITECTURE.md`: an instrumented developmental observatory around ONE primary substrate, with qualified rulers first. Ruler validity is ranked the dominant binding constraint (54% of 210 coded failures).
- **FABLE-5.1 and ASTRA-6.0:** gate/harness specifications.
- **Synthesis v0.4** (`docs/phase3/synthesis/ENCELADUS-DIONYSUS-v0.4/SYNTHESIS_AND_DECISIONS_v0.4.md`): "strong recursion unqualified".
- **My reading:** all three are *methodology-first* designs. They are right that unqualified rulers produced most past false positives, and I adopt their discipline. Their weakness for this brief: none specifies an improver whose own machinery is the object of search, so none can produce an L2/L3 observation. An observatory with nothing recursive inside it measures nothing recursive. The OPUS-5.5 document shares my model family; I treated it as a hypothesis to beat, not as authority.

## 7. Integration-suitability summary

Reuse discipline, not organisms. No existing Prometheus substrate is a good host for recursive improvement:
- Aphrodite's fold DSL has identical-expressivity libraries and a ceiling on independent worlds.
- Ananke, Crius and Theseus have needle landscapes.
- Aether is a GPU physics with no improver concept.

The strongest reusable assets are:
1. Aphrodite's experimental membrane: escrow, entropy domains, CRN pairing, promotion contract, sham donors, R8;
2. the RSO evaluator ownership and adversarial kit;
3. the Crius / D-series control batteries;
4. Fabric for fan-out;
5. the negative results themselves, which set the design's priors (§2).
