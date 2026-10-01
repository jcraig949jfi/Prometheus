# Prometheus Phase 3 -- salvage matrix

Architect: FABLE-5.1 (seat Dionysus). Written 2026-10-01, after
REQUIREMENTS.md and RSE_ARCHITECTURE.md sections 1 to 12 were frozen and
pushed (a0e3a4d03).

The question asked of every component, from the architect prompt: does this
satisfy a Phase 3 requirement better than rebuilding it? Not: how can this
engine be preserved.

----------------------------------------------------------------------

## 0. How this was made, and how far to trust it

**Order.** Requirements and architecture were frozen first. Only then did
seven read-only workers open the old code, one scope each: program-like
substrates, other substrates, worlds, qualification instruments, causal
instruments, infrastructure, search. Their briefs are committed
(roles/Dionysus/prompts/2026-10-01_salvage_workers/, e3d7c7034). Their
reports are deposited verbatim in salvage_reports/01 to 07.

**Who says what.** The facts in each row are the workers'. Each worker marked
what it checked in source itself and what it took from a crawler dossier;
the "Source" line of each row points to the sheet. The classification, the
"Take" line and everything in sections 1 and 4 to 8 are mine.

**Limits.**

- No worker ran a test suite, an engine or a database query. "Shown correct"
  means what the committed tests, receipts and records show.
- I did not re-verify the workers. Where two workers looked at the same
  component they agreed on substance and sometimes differed on line counts.
- All seven workers and I are one model family. In the design's own terms
  this matrix is independence level I0 to I1. A wrong classification here is
  cheap to fix: every row is re-examined when its slot is actually built.
- One fault in my brief exposed holdout-named files to worker searches. It
  is reported in salvage_reports/00_SEARCH_RULE_INCIDENT.md.

**Classes** (the prompt's seven):

| class | meaning here |
|---|---|
| KEEP | used as it is |
| HARDEN | the code is taken; it needs stated work before it carries a claim |
| EXTRACT | a primitive is lifted out of its engine into shared infrastructure. The row says whether code and tests are lifted, or the design and its fixtures are re-implemented against the protocols |
| REBUILD | the need is real; the implementation is not the starting point |
| RETIRE | no Phase 3 role |
| HISTORICAL CONTROL | not machinery; kept as a fixture or a control corpus |
| UNKNOWN | not enough evidence to decide; the row says what is missing |

**Cost scale** (the scale the workers used): S under 1 day; M 1 to 3 days;
L 1 to 2 weeks; XL more, or needs a decision. These are builder-days of a
model with an operator available for forks. Treat them as ordinal.

**Rule for choosing.** Adapt only when adapting is clearly cheaper than
rebuilding AND the old code brings something a rebuild would have to
re-earn: an independent oracle, a cross-host record, a fixture set made from
real defects. In most rows the tests and the documented failure modes are
the asset, and the code is not.

salvage.jsonl beside this file is generated from section 3 by
process/salvage_to_jsonl.py, which also checks the counts below.

----------------------------------------------------------------------

## 1. The answer in one page

**No old engine continues as an engine.** No organism substrate, no world as
built, no search loop and no ruler enters Phase 3 unchanged. What carries
forward is mostly small: a verdict type, a contract, a schema, a control
list, a set of designed specimens, a list of ways an instrument once failed.

    COUNTS all: KEEP 3, HARDEN 13, EXTRACT 40, REBUILD 5, RETIRE 11, HISTORICAL CONTROL 9, UNKNOWN 5, total 86
    COUNTS scientific (O, W, S, M, C): KEEP 0, HARDEN 8, EXTRACT 36, REBUILD 5, RETIRE 10, HISTORICAL CONTROL 9, UNKNOWN 4, total 72

Rows are decisions, not files; several RETIRE and HISTORICAL CONTROL rows
group many components, so the counts understate how much is retired.

**What fills each slot of the architecture.**

| slot (RSE_ARCHITECTURE) | decision | from | cost |
|---|---|---|---|
| kernel: queue and lease | harden | Agent Fabric (I-01) | M, then L |
| kernel: receipt and ledger | harden | toolbox receipt.v1 (I-02), with SFE's chain rule (I-03) and Vivarium's triggers (I-04) | M |
| kernel: verdict type | extract | Charon checks (M-01), Hecate contract (W-09), Techne measurement type (M-02) | S |
| kernel: qualification gate | extract, harden | Techne certify and constancy (M-02), Hecate corruption operators (M-03), Ananke Wave-2 library (C-01) | M |
| kernel: preregistration checks | extract | Harmonia primitives and adjudicator (M-05), Diomedes census (M-09) | S |
| kernel: failure fixtures | historical control | Necropolis cases (M-12), list B of report 04, section 5 below | M |
| kernel: sealed-world broker | harden | Cosmos broker protocol (W-11); custody is new | M |
| kernel: index, digest | harden, extract | Atlas tables (I-07); mailer and honest renderer (I-09) | M |
| kernel: model-call path | harden | prometheus_llm (I-08) | M |
| worlds: RECALL | extract | Archaeon event-stream grammar (W-01) | M |
| worlds: TRACK, IDENTIFY | extract | Ensorain exact-Bayes streams (W-02) | M |
| worlds: RETAIN | new | P1 prototype is the first version | -- |
| worlds: RECOMBINE | extract parts | Ensorain surrogate and pair-block holdout (W-03) | M |
| worlds: CHAIN | extract parts | compositional asks of W-01; exact closure method (S-09) | L |
| worlds: FAMILIES | new | -- | -- |
| worlds: DOUBT | extract parts | Ludus solver pattern (W-04), Cosmos hint dial (W-12) | M |
| worlds: MINED | extract | Hecate sampled systems (W-10) | M |
| worlds: demand certificates | new | no code anywhere computes the best value of a restricted policy class | -- |
| worlds: twins, leak probes | extract | Tyche twins (W-13), Ludus audit (W-04), one-character leak worlds (M-10), toolbox wrappers (W-06) | S to M |
| substrate: REF | new | no conventional learner and no gradient regime exists in the tree | -- |
| substrate: WM | rebuild | layout confirmed by Crius (O-03); conventions from Proteus (O-01); kernel pattern from D-5 (O-04) | L |
| substrate: PN | rebuild | no network in the tree keeps weights across episodes (O-11) | M to L |
| substrate: open arms | harden one, later | Ananke packet-tensor engine for the message-passing arm (O-09) | L |
| rulers: class exclusion | new | pieces only, all in floats, none shipped with a world | -- |
| rulers: interchange, lesion | extract | Ananke lens and its failure modes (C-02), Cosmos gate (C-03), Crius conditions (C-04), Ares cuts (C-05) | M |
| rulers: material tracing | extract | Archaeon record format and fixtures (C-06); a new tracer per substrate | M each |
| rulers: search-power curve | new | vocabulary from Ergon and D-5 (S-06); P1's reach.py is the first version | -- |
| rulers: cost meters | new | nothing records energy; one place records dollars and drops tokens | -- |
| search: protocol | extract | reach classes and typed states (S-01), escrow and pairing (S-08), budget ladder (S-06) | M |
| search: regimes | extract, new | lexicase (S-05); gradient and evolution-strategy arms are new | S each |
| experiments: P6 negative control | harden | Aphrodite engine as the fixed-procedure learner (O-13) | M |
| experiments: P8 statistic | extract | Theseus divergence statistic and its one data set (S-07) | S to M |
| next-experiment choice | harden | Metis cheapest-discriminator rule (S-13) | S to M |

**Largest new items**, in order of how much the design leans on them:
demand-certificate solvers; the WM kernel; the search-power instrument; the
runner's refusal gates; separate write authority; custody; the REF arm; PN.
Section 4 lists all of them.

----------------------------------------------------------------------

## 2. What the salvage showed about the old program

Five facts from the workers that matter more than any single row.

1. **Nothing computes what a restricted class can score.** No component
   computes the best memoryless, k-state, non-adaptive or lookup policy value
   for a world in which an organism acts. The few bounds that exist are per
   task, in floats, used only in after-the-fact audits, and one of them is
   violated in its own environment (a .75 bound against .763 measured). So no
   old result could have been a class exclusion, and every demand certificate
   is new work. (03 SURPRISES 10; 05 question B.)
2. **Nothing measures search power.** No component measures how often search
   recovers a planted target as a function of distance and budget. The
   nearest designs measure "solved over expressible" at fixed budgets on five
   tasks per depth. Meanwhile designed organisms scoring .850 and .978 sat
   inside a genome space that 19,873,536 world-episodes of search did not
   find. Every old null is therefore ambiguous between "cannot" and "was not
   reached". (05 question A; 07 sheet 9.)
3. **BUILD was never possible in a network.** Across the whole tree no
   network-like organism keeps weights or topology across episodes. The one
   candidate resets its plastic weights every episode. The only substrate
   with harness-owned stores that persist across a lifetime of tasks is the
   Crius machine. (02 network-plasticity search; 01 sheet 2.)
4. **Search budgets were limited by implementation, not by hardware.** The
   largest lifetime-scale search on record is about 2e7 evaluations, mostly
   in pure Python at 10 to 2,000 evaluations per second. The P1 prototype
   runs 1.86 million lifetimes per second on 12 threads of the same machine.
   (07 section A; prototype/p1_slice/RECEIPT_qualify.json.)
5. **The good instruments are small, late and unused.** The best pieces are
   a few hundred lines each, written in the last three weeks, by seats
   reacting to failures: a three-valued verdict with counts, an evaluator
   contract, a corruption harness, a lockstep intervention library, a
   calibration panel, a set of audit primitives. Most are imported by nothing
   except their own tests. (04 COULD NOT DETERMINE; 05 SURPRISES 1.)

----------------------------------------------------------------------

## 3. The matrix

Each row: what it really does; what shows it is correct; fit to a Phase 3
requirement; cost to adapt against cost to rebuild; coupling; what is taken.
"Lines" is the size the worker reported, used only for the tally in
section 9.

### 3.1 Organism machinery

### O-01 [REBUILD] Proteus v0 player machine (proteus/foundry)
- Does: a pure-Python tape machine. The genome is copied onto a tape of 32-bit words and executed in place; 25 opcodes; the opcode is the word modulo 25, so every word decodes. A genome field decides what persists across a tick. No call, no block store, absolute addressing.
- Shown correct: 9 replay tests including exact checkpoint and restore; a differential shadow decoder with 0 divergences; replay across 3 runtimes on one machine. Defects: a docstring and the code disagree on an operand slot; the organism id pins bytes, not execution.
- Fit: slot WM. Meets ORG-04, ORG-06, ORG-08. Partial ORG-01, ORG-02, ORG-03. Fails COMP-01 (3.75e6 operations per second on one core) and DEV-01.
- Cost: adapt XL; rebuild L.
- Coupling: stdlib only; 117 files outside proteus/ import it; a runtime hash over the machine's source makes any edit a new runtime for every consumer.
- Take: conventions, not code: total decoding by modular fields, exact checkpoint with a test, a shadow decoder as a differential oracle, a runtime hash over kernel source. The machine stays frozen so old records replay.
- Lines: 1396
- Source: 01 sheet 1a.

### O-02 [RETIRE] Proteus graph organism (proteus/graph)
- Does: the genome is a node list with data and control edges; call and return with a bounded stack and no arguments; nothing rewrites the graph during life.
- Shown correct: 26 tests (replay; one subgraph called from two sites). Its only campaign found 0 useful edits of 4,881.
- Fit: slot WM: ORG-03 in part. No checkpoint or restore function. Fails COMP-01.
- Cost: adapt XL; rebuild L.
- Coupling: the Proteus random generator; one Archaeon campaign.
- Take: nothing as code. One idea is carried: references that do not depend on position.
- Lines: 1308
- Source: 01 sheet 1b.

### O-03 [REBUILD] Crius machine, workspace and block store (crius/)
- Does: an 8-register machine with 53 opcodes. Registers are reset every task. A workspace of 256 cells and a store of organism-written executable blocks (32 blocks of 64 instructions) persist across a 50-task lifetime. The program is fixed for the lifetime. A block is invoked in the caller's registers, to depth 4.
- Shown correct: replay tests; gate controls shown failing on the wrong organism; 7 designed programs of 19 to 64 instructions. Defects: an invocation log read the wrong register (fixed); a latent hole in totality (appended instructions keep unbounded register fields, and invoking one raises an error nothing catches; untested); block ids come from a counter that never reuses a value, which is a clock; its typed rungs put competence into the instruction set.
- Fit: the nearest existing thing to WM. It is the only machine in the tree with organism-written executable blocks and harness-owned stores. ORG-03 a, b, c, f, g yes; d and e partial; no rent. Fails ORG-04 at rungs B to D, ORG-05 (a plant of 64 against a cap of 96), COMP-01.
- Cost: adapt L, and the kernel would be rewritten anyway (tuple, dictionary and failure values do not carry into a compiled integer kernel); rebuild L.
- Coupling: stdlib; no outside importers; the machine imports its world; its receipts call git.
- Take: the three-store layout, which is the layout REQUIREMENTS 1.5 asks for and so is confirmed workable; the designed programs as the first WM plants to port; and three lessons as kernel tests: every instruction field decodes by modulus; no identifier counter is visible to the organism; no capability-specific opcode above scaffold level S3.
- Lines: 6881
- Source: 01 sheet 2.

### O-04 [EXTRACT] D-5 register machine: reference plus compiled path (agent_d5_blind/substrate)
- Does: a pure function from inputs to one register; 8 registers of 16 bits, at most 24 instructions; a Numba fast path beside a reference machine.
- Shown correct: the fast path is bit-identical to the reference on 2,402 programs by 128 inputs; every claimed solve is re-checked on the reference by assertion; 290 of 290 rows replayed. Defects: the fast path loads 2 inputs where the reference loads up to 8; path strings are Windows-only.
- Fit: the COMP-01 pattern, and the only compiled path in the old tree pinned to a reference. Not an organism for WM: no memory, no store.
- Cost: extract the pattern S; adapt as a WM base XL.
- Coupling: numpy, numba; imported by Ergon, the evidence wiki and Techne.
- Take: design: reference implementation, compiled kernel, equivalence test, and re-verification of every claimed result on the reference. The P1 prototype already follows it (wm_mini.py, oracle.py, differential_test.py).
- Lines: 2285
- Source: 01 sheet 3; 07 sheet 7.

### O-05 [HISTORICAL CONTROL] Nestor Z8 byte machine and pair-tape world
- Does: a variable-length byte machine over a shared arena; undefined bytes are no-ops; genome and working memory are the same bytes; world operations for allocation, birth and copying.
- Shown correct: a self-test of 22 checks; a shadow tracer asserting identity per interaction; its own harvest lists 15 engine defects (dossier).
- Fit: slot WM: ORG-03 a, c, f only. Floats in energy and copy error (fails ORG-08); no snapshot; fails COMP-01.
- Cost: adapt XL; rebuild L.
- Coupling: script-style imports; subclassed per experiment.
- Take: nothing as machinery. As record: an operation mask that disables a world operation as a same-length no-op, which is an affordance switch done correctly; and the register-reset axis. Register initialisation is a world variable; the P1 prototype met the same effect.
- Lines: 9522
- Source: 01 sheet 4a.

### O-06 [HISTORICAL CONTROL] Bellerophon byte soup (prometheus/z80atlas)
- Does: a 256-byte space per execution; 50 defined byte values and 206 no-ops; no call or return.
- Shown correct: a golden replay test; cross-host replay of a real task matched 74,800 of 74,800 rows. Defect: one block-copy instruction with a zero count sweeps 256 bytes.
- Fit: as O-05, with the best cross-host record among the soups (REPR-01).
- Cost: adapt XL; rebuild L.
- Coupling: stdlib; used by the Archaeon lineage lens, an Artemis script and Bellerophon tools.
- Take: nothing as machinery. As record: 63,247 runs, and the comparison in which its native labels by resemblance disagreed with traced ancestry on 847,000 births (C-06).
- Lines: 5505
- Source: 01 sheet 4b; 05 Archaeon causal lens.

### O-07 [HISTORICAL CONTROL] Archaeon byte machine and ecology (archaeon/z80atlas)
- Does: the opcode is the low 5 bits of a byte, so every byte decodes; four registers zeroed at each execution; a cost per step and a rent per byte, both in floats.
- Shown correct: 5 positive controls pass; byte-identical replays (dossier). Record: 101,003 runs; all 26 of 26 "spontaneous replication" flags were transplants (dossier).
- Fit: as O-05. It has the only per-step cost plus per-byte rent in the old tree, which is the idea behind DEV-09, but in floats.
- Cost: adapt XL; rebuild L.
- Coupling: the Proteus random generator; three other Archaeon packages.
- Take: nothing as machinery. The transplant under a "spontaneous" label is a failure fixture (section 5).
- Lines: 3148
- Source: 01 sheet 4c; 07 sheet 1b.

### O-08 [RETIRE] Apollo routing and blackboard organisms (apollo/src)
- Does: lists of hand-written Python operators over a per-task record; an optional local model inserts steps.
- Shown correct: no tests.
- Fit: not an organism. ORG-13 (REJECTED): the competence is supplied by the operator library.
- Cost: not applicable.
- Coupling: Hephaestus primitives; a local model server.
- Take: nothing.
- Lines: 17881
- Source: 01 sheet 5; 07 sheet 6a.

### O-09 [HARDEN] Ananke packet-tensor engine (prometheus/ananke) -- the message-passing open arm
- Does: N sites run one shared straight-line integer program. Payloads are summed per recipient and channel into an in-flight ring with loss, latency, duplication and noise. The environment is a pre-drawn schedule; the action is one sign at one site; nothing the organism does changes its inputs.
- Shown correct: a separately written pure-Python oracle, bit-identical on 40, 12 and 40 configurations; a must-fail control; checkpoint and resume equal an uninterrupted run; the conformance suite passed unmodified on a second host (139 passed). Defects: dials converted from floats at setup; a 28-line block clock solves one of its worlds at 1.000; copy policies reach .75.
- Fit: the only candidate for the message-passing arm (RSE 6.4). Meets ORG-06, most of ORG-08, REPR-01 in substance. Fails ORG-01 (no step from observation to action), ORG-02 (no episode boundary), ORG-09, DEV-01, COMP-01 (built for GPU). No evolved capability above HOLD is on record. It has designed HOLD organisms, one of which holds its bit only in flight.
- Cost: adapt L (closed-loop adapter; store declaration and resets through its existing controls; genome-bit accounting; a CPU kernel re-certified against the oracle; new plants). Rebuild M, but a rebuild re-earns 19 design rulings and the second-host record.
- Coupling: torch, numpy; campaign state off-repo; a Windows scheduler.
- Take: engine and oracle, when the first open arm starts, which is not before P1 to P3 have qualified the kernel. The in-flight organism is a designed positive for the arm's own question: a memory that is neither register nor weight.
- Lines: 6130
- Source: 02 Ananke.

### O-10 [RETIRE] Aether byte-copy lattice, as an organism substrate (Aether/)
- Does: a synchronous 2-D torus with 5 bytes per site; one acting opcode of 256. No genome, individual, input, output, objective or selection.
- Shown correct: a differential corpus between oracle and fast implementation; golden vectors; mutants rejected; bit-identical on 4 hosts (19 attempts, all matching). Record (dossier): about 92% of the medium frozen by about 2,500 ticks; one-bit differences stay within about 1 site.
- Fit: a lattice arm in name. Fails ORG-01, ORG-02, ORG-09, DEV-01 to DEV-07, COMP-01 and open-arm admission. It cannot even HOLD, since there is no input or readout.
- Cost: adapt XL (it needs decisions: what an organism is, where input and output go). A lattice substrate designed for organisms is M to L.
- Coupling: numpy; CuPy on rented pods; a rental key held on one laptop.
- Take: nothing as a substrate. Its twin assay and its verification harness are taken separately (C-11, I-13).
- Lines: 1794
- Source: 02 Aether.

### O-11 [REBUILD] Ares graph organisms (ares/substrate.py) -- for PN
- Does: up to 17 nodes in float32, a Hebbian update on one input port, action by argmax. Activations and the plastic weights are both reset every episode.
- Shown correct: a determinism test; a positive-control search; a hand-wired 1-bit latch whose fitness falls when memory is cut. No oracle. Defect: the final champion is chosen on the held-out set.
- Fit: slot PN: the right shape and the idea of switches. Fails ORG-08 (float32), DEV-01 (nothing persists across episodes), ORG-01, ORG-09, REPR-01.
- Cost: adapt L; rebuild M for the core, L with evolution-strategy and gradient arms. Rebuilding costs no more than adapting.
- Coupling: numpy only.
- Take: nothing as code. PN is new.
- Lines: 1654
- Source: 02 Ares; 02 network-plasticity search.

### O-12 [REBUILD] primordial tensor-train organisms (primordial/brain) -- for a tensor-network arm
- Does: an evolved float32 tensor-train policy with bond rank as a capacity dial and no state between steps; a regressor whose rank grows on surprise, with a fixed-rank twin and a cheat that reads the regime flag.
- Shown correct: a float64 oracle per family; a compiled forward pass with 0 mismatches of 129,583 rows; fused rollouts exact. One of its lines ended FAIL/KILL.
- Fit: the tensor-network arm: it has the rank dial, a memory charge, a fixed twin and a cheat control. Fails ORG-08, ORG-01, DEV-01. The policy cannot HOLD: it is stateless.
- Cost: adapt L; rebuild M.
- Coupling: numba, torch, a GPU tensor library; two harnesses read data not in the repository.
- Take: nothing now. If this arm is opened it is rebuilt in integers with recurrent bond state, reusing the twin-and-cheat layout.
- Lines: 1160
- Source: 02 tensor-network group.

### O-13 [HARDEN] Aphrodite library-inheritance engine (roles/Aphrodite/engine) -- the RECURSE negative control
- Does: enumerates integer-fold programs in library order and then through a complete grammar, one escrow unit per candidate; derives one-hole schemas from the programs it found; selects libraries by paired saving; transplants frozen libraries into fresh recipients against pristine and sham libraries. The improver itself is immutable code.
- Shown correct: a conformance gate between two evaluators and a 288,000-pair equivalence gate (dossier, not rerun); sham libraries. Defects: two acceptance conditions are constants set to True; the positive-control schema equals the derived one (dossier).
- Fit: as built it is the T6 reference class in REQUIREMENTS 1.5, "designed learner with a fixed procedure and fixed hypothesis space". One of its candidates has the shape of the XFER-07 impostor (memorise). Library against pristine at equal budget has the T5 shape. It cannot be the RECURSE positive: starting from nothing, its donors derived 0 schemas in 8 of 8 runs.
- Cost: negative arm plus the COMPOSE pair M (organism wrapper, a CHAIN or FAMILIES catalogue, real gates, exact verdicts). A designed library learner on WM is L.
- Coupling: stdlib only; nothing outside its own tree.
- Take: the engine, wrapped in the organism protocol, as the fixed-procedure reference for P6. Its leverage numbers are an old signal to re-test (section 6).
- Lines: 14855
- Source: 02 Aphrodite; 07 sheet 8.

### O-14 [EXTRACT] Ensorain memory audit (ensorain/e0)
- Does: refuses undeclared persistent attributes on a learner, before a life and during it.
- Shown correct: tests show smuggled attributes refused at both points.
- Fit: ORG-02's hidden-store check, as a working precedent.
- Cost: S either way.
- Coupling: none beyond its package.
- Take: the check, re-expressed over the stores an organism declares. P1's reset-equivalence test is the behavioural half of the same guarantee.
- Lines: not reported
- Source: 02 Ensorain.

### O-15 [RETIRE] Four families that are not organisms (Ensorain regressors; Tyche lens programs; Theseus rule fields; Hecate plastic media)
- Does: a tensor-train regressor behind a fixed foraging policy; feed-forward feature programs computed over whole time series for fixed classifiers; rule programs on a 1-D float field with no input or action; Hebbian conductances on a reaction-diffusion medium with no input or output.
- Shown correct: varies; none has an oracle.
- Fit: none of the organism slots. All fail ORG-01, ORG-08 and DEV-01.
- Cost: as substrates L to XL each; not competitive with rebuilding.
- Coupling: Tyche imports Hecate's answer key; Theseus imports Tyche.
- Take: nothing as substrates. Their search operators, twins and statistics are taken separately (S-05, W-13, S-07, M-10).
- Lines: 3447
- Source: 02 Ensorain, Tyche, Theseus, network-plasticity search.

### 3.2 World machinery

### W-01 [EXTRACT] Archaeon event-stream grammar (archaeon/wse/worlds.py) -- RECALL, part of CHAIN
- Does: each tick the organism reads integer event words (put, ask, compositional asks, distractors, retire); its first output word on an ask tick is scored exactly. K tagged values, identities drawn fresh per episode. Independent dials for items, delay, distractors, interference and value bits. Separate keyed stream families for training, held-out and controls.
- Shown correct: an independent reference evaluator sharing only the kind codes matches on 20 episodes per survey cell; designed positives score 1.000 and nulls 0.000. Defects: the construction that leaked in one cell is unchanged in the code; some stream cells have no test; chance is stated but no bound is computed.
- Fit: the best RECALL seed in the tree. Meets WLD-04, most of WLD-01, part of MEAS-04. Fails WLD-02, 03, 05, 06, 07.
- Cost: port M (protocol, information bounds with enumeration receipts, twins, commit-reveal families, the leak fixed). Certified CHAIN bounds L. Rebuild RECALL M.
- Coupling: the Proteus machine; imported by Nestor and Odysseus code.
- Take: code and tests for the grammar and stream keying, lifted out of the Proteus harness.
- Lines: 3333
- Source: 03 Archaeon.

### W-02 [EXTRACT] Ensorain exact-Bayes stream worlds (ensorain/arc3/suff) -- TRACK, IDENTIFY
- Does: binary streams with exact Bayes predictors: independent draws; unknown-rate Bernoulli; order-k Markov; known hidden-Markov processes by forward filtering, including the Even process, which no finite window can track. A window-learner class with an exact enumerated floor. Learners scored by excess log-loss.
- Shown correct: oracles hit the known entropy rate of 2/3 bit within 0.01; the window learner equals Bayes where it should to 1e-9; an independent stdlib reimplementation confirmed four findings; the enumerated floor matched a closed form to 4 decimals.
- Fit: the best TRACK seed, IDENTIFY for unknown-parameter streams, and a known-law recovery case (SCI-05). Meets WLD-02 in part. Fails WLD-01 (prediction only, no actions; floats), WLD-05, 06, 11; MEAS-07.
- Cost: adapt M, rebuild M (rationals, protocol wrapper, exact class values from the generating machines, twins, sealed seeds).
- Coupling: numpy, scipy.
- Take: generators and oracles, as the second-implementation reference; the Even process as the first HOLD known-law case.
- Lines: 1570
- Source: 03 Ensorain; 02 Ensorain.

### W-03 [EXTRACT] Ensorain null ladder, marginal-preserving surrogate and pair-block holdout (ensorain/wtp3) -- RECOMBINE
- Does: nulls from zero through constant, marginal, linear and bounded lookup; an exact surrogate that keeps the mean, the per-mode marginals and the variance and destroys interactions; a test set held out by pair blocks.
- Shown correct: 5 tests. In the record, a tuned batch rung added after the data beat all 9 promoted specimens (dossier).
- Fit: the RECOMBINE twin and the withheld-combination machinery (XFER-01, XFER-06); rungs for WLD-03. Float fields.
- Cost: extract S to M.
- Coupling: numpy.
- Take: the surrogate and the holdout construction. The late rung is kept as a fixture: a baseline ladder ships before the data or it does not count.
- Lines: 2421
- Source: 03 Ensorain.

### W-04 [EXTRACT] Ludus exact stopping solver, depth profile and differential leak audit (ludus/bench, ludus/arena)
- Does: exact backward induction on fully observed stopping problems, with exact evaluation of any fixed policy; the share of states where depth-k search misses the optimum; an audit that changes one secret attribute and compares 10 channels a player can reach.
- Shown correct: negative control 0.0, positive 0.3448; the audit fires on 4 of 4 injected leaks. Defects: its gate admitted Nim although a simple rule scores 1.0, because the cheap-policy class was a hand-built list; policies are handed the transition model; no pytest functions.
- Fit: DOUBT, as a pattern only: an exact optimum exists, but for fully observed problems that demand zero memory. Meets WLD-17. Fails WLD-01, 02, 03, 05, 06, 07, 11.
- Cost: M (a belief-state dynamic programme in rationals; audit and fixtures ported as admission attackers); rebuild M.
- Coupling: stdlib; no importers outside its package.
- Take: the audit and three fixtures as admission attackers. The Nim admission is the standing counter-example for WLD-07: a shortcut search over a hand-built list of cheap policies is not a shortcut search.
- Lines: 8607
- Source: 03 Ludus.

### W-05 [UNKNOWN] Ludus atlas of worlds (ludus/atlas_of_worlds)
- Does: a catalogue of 1,338 game rows in M1 Postgres; nothing in it is executable.
- Shown correct: not examined.
- Fit: possibly a source list for MINED or for social worlds (WLD-13).
- Cost: unknown.
- Coupling: M1 Postgres; contents not in git.
- Take: undecided. Nobody opened the contents.
- Lines: 3728
- Source: 03 Ludus; 03 COULD NOT DETERMINE.

### W-06 [EXTRACT] Toolbox world wrappers and agreement test (prometheus/toolbox)
- Does: seeded channel permutation, observation delay and scheduled parameter change, each as a wrapper around any world; an admission check that compares two implementations with a probe-power check.
- Shown correct: 92 mutants all caught (committed ledger); 38 receipt files reproduce on Linux. Defect: the "second implementation" of its integer world imports the reference's random streams, so the agreement check shares the draws.
- Fit: foundry parts: the scrambled-channel twin (XFER-02), the delay dial (WLD-04), the rule-change dial (DOUBT), implementation agreement (WLD-11). The world kernel as a whole fails WLD-02, 03, 05, 06, 07.
- Cost: lift the wrappers and the agreement test S; harden the whole kernel L; rebuild its core M.
- Coupling: optional numpy and redis; one importer.
- Take: code for the three wrappers and the agreement test. The shared-stream defect becomes a fixture for WLD-11.
- Lines: counted in I-02
- Source: 03 Bellerophon.

### W-07 [EXTRACT] Herakles stream-into-lattice catalogue (herakles/ca_stream)
- Does: the complete catalogue of all 256 length-8 input streams with delayed-recall and temporal-XOR targets; a structural partition into fit and confirmation sets; four controls behind the substrate interface (shift register, shift-xor, memoryless direct input, frozen random).
- Shown correct: 29 tests. Result on the rules it held: 0 of 63,488 features nonzero (the rules annihilate the input).
- Fit: a tiny RECALL and TRACK seed with exact whole-catalogue scoring and a memoryless reference shipped with it (WLD-03 in part, WLD-17). Horizon fixed at 8 (fails WLD-04).
- Cost: S either way.
- Coupling: numpy.
- Take: the catalogue, targets and control set, as a kernel conformance world.
- Lines: 760
- Source: 03 Herakles.

### W-08 [HISTORICAL CONTROL] Herakles cellular-automaton libraries with recovered rule tables (herakles/evca, herakles/eca)
- Does: scores one radius-3 rule on a ring against density criteria; holds 6 recovered historical rule tables; enumerates the 256 elementary rules on small rings.
- Shown correct: 64 and 33 tests; known answers reproduced in 17 of 18, 15 of 15 and 4 of 4 cells.
- Fit: a known-answer corpus for a lattice arm, if one opens. No foundry role.
- Cost: none.
- Coupling: numpy; imported by Vivarium, Archaeon, Proteus, Nyx and Artemis code.
- Take: left in place; cited as a positive-control corpus.
- Lines: 1968
- Source: 03 Herakles.

### W-09 [HARDEN] Hecate evaluator contract (hecate/programs/_lib/evaluator_contract.py)
- Does: a specification-driven evaluator that requires five arms (treatment, null twin, positive control, cheat, simple alternative); compares exactly in fractions; lets an instrument failure take precedence over any signal; maps a missing positive control to "specification unattainable"; never raises.
- Shown correct: 33 tests. Its own header: draft, not issued, not frozen.
- Fit: the admission verdict engine for WLD-07 and an exact-arithmetic verdict type (MEAS-07, SCI-02).
- Cost: S to issue; rebuild S.
- Coupling: none.
- Take: the code, issued as the foundry's admission gate, with arm names changed to those of REQUIREMENTS 1.3.
- Lines: 416
- Source: 03 Hecate; 04 Hecate metamorphic.

### W-10 [EXTRACT] Hecate sampled finite systems (hecate/alien) -- MINED
- Does: 100 deterministic integer maps on at most 4,096 states, with properties verified by exhaustive enumeration, three kinds of matched null, and six baselines shipped in the freeze commit.
- Shown correct: tests that every property verifies and every null destroys it. Defects: the answer key is tracked in git and can be regenerated from a public seed; the leak test is a list of 13 substrings.
- Fit: the best MINED seed; material for TRACK and IDENTIFY. Meets WLD-03 on timing. Fails WLD-01, 02, 05, 06, 11.
- Cost: M (hidden-component worlds with exact best-k-state values by enumeration; sealed keys); rebuild M.
- Coupling: a corpus built from ignored paths; imported by Tyche.
- Take: the sampled-system generator and its exhaustive checks. The tracked answer key becomes a custody fixture.
- Lines: 3956
- Source: 03 Hecate.

### W-11 [HARDEN] Cosmos sealed-holdout broker and audit (prometheus/cosmos/broker.py, audit.py)
- Does: checks that a law is frozen and that the sealed specification matches a preregistered commitment; runs the sealed family only in a subprocess; receipts the prediction hash before the reveal. An audit re-checks chain, freeze, order and seals.
- Shown correct: 5 cheat controls on the audit. Limits stated in its own code: this is tamper evidence, not access control; the sealed files are tracked and readable by any process; there is no access log. Three holdouts were spent in one day.
- Fit: the sealed-world broker (WLD-06, PROV-10). It is the best existing custody and it fails PROV-10's own check.
- Cost: M (sealed material out of the repository or encrypted; a read log; commit-reveal seeds; a process boundary); rebuild M.
- Coupling: numpy; its store is on M2.
- Take: the ordering-and-commitment protocol. Custody is new. The search-rule incident in salvage_reports/00 is the worked example of why.
- Lines: 479
- Source: 03 Cosmos; 06 Cosmos broker.

### W-12 [EXTRACT] Cosmos cue task with a misleading hint, and the threshold locator (prometheus/cosmos/c3/task.py, prometheus/cosmos/locate.py)
- Does: a cue among V symbols, k distractors, a query, and a hint that reveals the cue with probability h; a locator that fits where behaviour flips along a 33-point cost ladder under common random numbers.
- Shown correct: used in a gate of six planted systems, each classed as expected on 5 of 5 seeds.
- Fit: a RECALL micro-world whose memoryless bound is h + (1 - h)/V; and the only threshold locator in the tree (toward MEAS-12, though it is a fixed ladder, not a staircase).
- Cost: S.
- Coupling: numpy.
- Take: both, as conformance material. The hint dial becomes DOUBT's misleading-evidence dial.
- Lines: not reported
- Source: 03 Cosmos.

### W-13 [EXTRACT] Tyche hidden-precursor worlds, twins and keyed-hash negatives (tyche/v2)
- Does: binary input channels with a label computed from hidden precursors; an exact lowest informative order for truth-table laws; a twin that applies the same law to an independent hidden copy of the inputs; negatives labelled by a keyed hash.
- Shown correct: tests on certified orders and exact oracles; a causality audit that catches a planted look-ahead cheat. Defects: the "exact" mutual information is a plug-in estimate with a permutation correction; the hash keys are public literals; one leak test would pass an inverted copy.
- Fit: HOLD and TRACK seeds with an order dial; absence twins and keyed negatives for WLD-05. Fails WLD-01, 03, 06, 11.
- Cost: M; rebuild S to M.
- Coupling: imports Hecate's sampled systems.
- Take: the twin and keyed-negative constructions and the order function.
- Lines: counted in S-05
- Source: 03 Tyche.

### W-14 [RETIRE] Worlds with no computed optimum (Ares W family; Vivarium kinds; Archaeon composed worlds; Archaeon reproduction assay)
- Does: float worlds with present, absent and shuffled modes; fitness evaluators with no perception-action loop; float feature-module worlds; a reproduction assay with lockstep arms.
- Shown correct: not examined for Ares; tests exist for the others.
- Fit: patterns only: three-mode twins; a probe-then-commit shape for DOUBT; twin arms on shared streams with a band frozen before data. All fail WLD-01, 02, 03.
- Cost: rewriting one as an exact DOUBT world M.
- Coupling: their own engines.
- Take: nothing as code.
- Lines: not reported
- Source: 03 Ares and Vivarium; 03 Archaeon.

### W-15 [HISTORICAL CONTROL] The reasoning ladder and its probes (harmonia/experiments/reasoning_phase0.py and related)
- Does: tiers R0 to R12 with perturbation tests; math probes in four versions graded against a symbolic engine; no environment.
- Shown correct: a leakage audit flags one tier leaking at 100.0% with a constant floor of 57.5%. At this commit the generator still writes the truth into the payload.
- Fit: not a world family (WLD-16, REJECTED). A fixed ladder is also what the North Star rules out.
- Cost: extract the fixture S.
- Coupling: a symbolic library; Icarus.
- Take: the leaking probe with its executable cheat reader, as a kernel fixture for T01; the payload reader and constant floor as trivial responders.
- Lines: 721
- Source: 03 reasoning ladder.

### W-16 [UNKNOWN] Archaeon hidden-bitstring world with an exact optimum at small sizes
- Does: per the dossier, a hidden bitstring identified by acting, with an exact dynamic-programming optimum for small lengths.
- Shown correct: not opened by any worker.
- Fit: a possible IDENTIFY seed.
- Cost: unknown.
- Coupling: unknown.
- Take: undecided. Open it when IDENTIFY is built.
- Lines: not reported
- Source: 03 COULD NOT DETERMINE.

### 3.3 Search machinery

### S-01 [EXTRACT] Reach classes and typed states (archaeon/wse/evolve.py, reachability.py, states.py)
- Does: a generational search in which children never compete with their parents, so neutral moves enter; random streams keyed so that arms share draws; each run labelled floor, shelf or summit, and runs pooled into COMMON, REACHABLE, RARE or OBSERVED_UNREACHABLE_AT_BUDGET with interval bounds and right-censoring; typed states (target unreachable, readout cannot express, positive control failed, underpowered) computed before any disposition.
- Shown correct: tests against an independent reference; deterministic cells. Defects: a no-op self-loop once invalidated ancestry depth; one training score of .9375 on 16 episodes was .53 held out.
- Fit: the SEARCH protocol: SRCH-05 as is; SRCH-01, 02, 04, 06, 11 in part. The typed states are the nearest existing thing to the apparatus labels of REQUIREMENTS 1.2. Fails COMP-01 (1,645 evaluations per second on 24 processes), SRCH-03, 08, 09.
- Cost: M; the loop alone rebuilds in S.
- Coupling: welded to the Proteus genome format.
- Take: design and vocabulary for the reach table and the typed states. The loop is rewritten compiled.
- Lines: counted in W-01
- Source: 07 sheet 1a.

### S-02 [RETIRE] Archaeon lineage scheduler (archaeon/frontier)
- Does: schedules experiment specifications, each a checkpointed search segment; branches on detector firings; runs the first chunk twice and compares digests.
- Shown correct: a segment self-test and replay equality. Defects: its reported maximum is a training reward; one detector fired 1,658,614 times in 3,719,136 evaluations; receipts sit in an ignored path; the admitted ruler set is a constant.
- Fit: the runner side: COMP-02 in part. Fails SRCH-05, PROV-03, ANTI-02, SRCH-09.
- Cost: L; a checkpointed segment runner rebuilds in M.
- Coupling: Archaeon campaigns, Proteus, a scheduled task on M2.
- Take: one pattern: run the first chunk twice and compare digests. The saturated detector and the training-reward maximum become fixtures.
- Lines: 2169
- Source: 07 sheet 1b.

### S-03 [HISTORICAL CONTROL] The greedy walk that cannot take a neutral step (proteus/round2/falsifier_46.py) and the mutation-kernel crucible
- Does: classifies single edits to a designed parent against a designed target and runs greedy 3-step walks; separately, estimates the unselected mutation kernel over 2,044 structural states.
- Shown correct: preregistered before any child. Defects: the greedy step can never accept a child of equal score, while 3,132 of 4,881 sampled children were neutral; walks of length 3 against a path of 5 edits; the crucible's reference control cannot fail.
- Fit: fails SRCH-01 by construction. The per-operator census is a usable single-edit probe (SRCH-03).
- Cost: not worth fixing as a regime.
- Coupling: the Proteus machine.
- Take: the fixture "a search that cannot take neutral steps reports its target unreachable". The P1 prototype measured the same factor directly: recovery of one missing instruction was 24, 9 or 1 of 24 lineages, depending only on the acceptance rule.
- Lines: 227
- Source: 07 sheet 2; 05 Proteus.

### S-04 [EXTRACT] Crius designed partial organisms at graded distance (crius/parts_c2.py) and its neutral-edit null
- Does: 7 frozen designed partial organisms with an ancestor map, paired selective value and edit distance; a null that re-scores ancestry steps which add no typed operation.
- Shown correct: gate witnesses before search; sealed qualification streams. Defects of the search around it: ties broken toward shorter programs and a set of already-seen genotypes, both of which suppress neutral drift; a budget frozen at 300 iterations; one founder in the seeded arm.
- Fit: REACH inputs (SRCH-02): the only designed ladder of partial organisms in the tree. The search loop fails SRCH-01, 04, 06 and COMP-01 (9.68 candidates per second).
- Cost: copy the designs S to M.
- Coupling: the Crius machine.
- Take: the ladder design, re-made for WM: partials with known distance and known selective value. The loop is retired.
- Lines: 413
- Source: 07 sheet 3.

### S-05 [EXTRACT] Tyche lexicase selection, reserve and natural-history tracer (tyche/)
- Does: parents chosen case by case with a tolerance; a reserve protected by age, novelty and chance; a tracer that finds the first ancestor carrying each hidden precursor, how long it sat at zero utility and why each ancestor survived.
- Shown correct: a cheat control and a causality audit. Defects (dossier): an unlogged reserve in one arm; thread oversubscription.
- Fit: population search with diversity (SRCH-09 in part); lineage accounting (SRCH-06, SRCH-11). Fails integer determinism and COMP-01 (13.1 programs per second).
- Cost: lexicase S (18 lines); tracer M.
- Coupling: numpy, sklearn; Hecate's systems.
- Take: lexicase as one declared selection regime; the tracer's question as a standard report in P5.
- Lines: 5439
- Source: 07 sheet 4.

### S-06 [EXTRACT] Budget ladder and the expressible / reachable / findable split (agent_d5_blind, ergon/gen3, agent_d4_blind)
- Does: sorts each task as expressible (a witness exists), reachable (within a bounded number of edits) and findable (solved per budget rung of 1,000, 3,000, 10,000 and 30,000 evaluations, by witness length). Computes the minimum detectable effect in advance. Sends constructed worlds through the exact decision path. Plants an oracle witness as a cheat control. A sibling design measures hit rate on reachable targets by remoteness, with first-passage cost.
- Shown correct: gate-fire 5 of 5; the planted witness was detected at n 100 and missed at n 30, and the miss was kept; 290 of 290 rows replayed. Limits: the recorded curves are engineering runs at 5 tasks per depth; one analysis script was never committed.
- Fit: the closest existing design to the search-power instrument (SRCH-02, 03, 04) and a MEAS-08 exemplar. It has the fastest verified loop in the old tree: 231,663 evaluations per second on 8 workers.
- Cost: the method ports; the code is bound to its machine; rebuild for WM M.
- Coupling: numba.
- Take: the vocabulary and the ladder. The instrument is new; P1's reach.py is its first version.
- Lines: 926
- Source: 05 Ergon; 05 question A; 07 sheet 7.

### S-07 [EXTRACT] Theseus divergence statistic and its one data set (theseus/synth/analysis.py)
- Does: scores model-free arms and one model-written arm on one language with one set of rulers. The statistic is the number of cells occupied only by an arm, against a 1,000-permutation null, with bootstrap intervals on distance.
- Shown correct: lineage records with 0 mismatches. Defects: no bitwise rerun; ordering once depended on a hash seed; the model-written arm carries no model id and no token log; the preregistered test was not the model-against-blind contrast.
- Fit: P8, generator divergence, as a prototype (ANTI-07). Its archive is keyed by fingerprint, not by certified profile (fails SRCH-09).
- Cost: statistic S to M; the archive and the collision operator are retired.
- Coupling: Tyche; a Nous file; Hecate programs.
- Take: the statistic. The data are the only existing evidence on hypothesis H7: the model-written genomes sat closest to the known library (cells of their own 15, 18, 7 against 23, 21, 11 and 27, 20, 6 for two blind arms). It is a pilot, not a result.
- Lines: counted in O-15
- Source: 07 sheet 5; 07 section C.

### S-08 [EXTRACT] Aphrodite escrow metering and keyed pairing (roles/Aphrodite/engine/fair.py)
- Does: one charge per candidate from an escrow that raises when exhausted; candidate order keyed by hash so that arms walk identical sequences; a library is kept only if the lower bound of its paired saving is above zero.
- Shown correct: an accelerated backend matched the reference on 480 of 480 rows; 248,523 charges per second on 3 workers.
- Fit: SEARCH protocol accounting: SRCH-04; COMP-05 at evaluation level; paired comparisons for SRCH-08.
- Cost: S.
- Coupling: stdlib.
- Take: enforced evaluation budgets and keyed pairing.
- Lines: 185
- Source: 07 sheet 8.

### S-09 [EXTRACT] Exact enumeration as ground truth (apollo/scripts/o1_enumerate.py; roles/Lexis/instruments)
- Does: exhaustive type-directed enumeration of pipelines; a breadth-first closure of an operator language over all tasks jointly, giving the exact set of outcomes any program can induce.
- Shown correct: positive controls (a known organism scores the same directly and through the tables). Defect: a planned cheat control was never run.
- Fit: calibration for REACH and DEMAND (SRCH-02, 03; a bound in the style of WLD-02 for a fixed operator language). One number worth keeping: enumeration needed 1,687,896 pipelines to reach a ceiling that evolution reached in 3,144.
- Cost: port M; rebuild M.
- Coupling: Apollo operators and battery.
- Take: the method, for CHAIN's flat-search cost and for small WM program spaces.
- Lines: 3516
- Source: 07 sheets 6a and 6b; 01 sheet 5.

### S-10 [RETIRE] Ananke evolutionary search (prometheus/ananke/search.py)
- Does: truncation selection over random integer genomes, with two shaping terms used for selection only; the champion is picked on training worlds and evaluated once on held-out worlds.
- Shown correct: no dedicated tests. Defect: shaping with no arm that removes it.
- Fit: SRCH-05 yes; fails SRCH-13. 631 world-episodes per second.
- Cost: rebuild S.
- Coupling: torch; its engine.
- Take: nothing as code. Its record is the clearest reach gap in the tree and is kept as a re-test target (section 6).
- Lines: 149
- Source: 07 sheet 9.

### S-11 [RETIRE] Model-guided generators (Hephaestus forge 1.0; Icarus; Nous; Apollo's model mode)
- Does: a model writes a tool class from a concept triple; a model patches one file per cycle; a model proposes concept triples and rates its own output; a local model inserts pipeline steps half the time.
- Shown correct: little. 2,861 of 6,661 forge rows are failed calls; one generator returns "novel" 92.3% of the time (dossier); another's payloads carry the label.
- Fit: none has a model-free arm at an equal certified level. One violates ANTI-10; one fails ANTI-04, ANTI-07 and INF-02. Apollo's mode is the only code with a declared blind share (half) and lineage tags that name model inserts, which is the ANTI-04 shape.
- Cost: not applicable.
- Coupling: hosted and local models.
- Take: nothing as generators. Fixtures for T01 and T15.
- Lines: not reported
- Source: 07 sheets 6a, 10a, 10b, 10c.

### S-12 [EXTRACT] Per-call model logging and the closure-before-model gate (hephaestus/xpol_2026; hephaestus/src/closure_test.py)
- Does: logs, per call, a prompt hash, the served model, tokens in, out and thinking, the finish reason and seconds; computes decoy floors before any call; a model-free closure test routes a problem before any model sees it, and bulk work is refused to premium models.
- Shown correct: a decoy at 0.4032 beats the comparator at 0.3925; in one recorded case the closure test overruled a candidate a model had minted.
- Fit: INF-03 and INF-06 as patterns. Closure-first is the INF-02 pattern: a model is called only at a fork that deterministic code could not settle. No fork tag.
- Cost: logging S; the closure gauntlet M.
- Coupling: the model-call layer; a model command line.
- Take: the log record and the closure-first rule.
- Lines: 1065
- Source: 07 sheet 10a.

### S-13 [HARDEN] Metis cheapest-discriminator rule (roles/Metis/season1/specimen/compose.py)
- Does: from a declared bundle of explanations, evidence and available tests with costs, returns the cheapest test whose outcomes split the surviving explanations. No score and no model.
- Shown correct: 13 adversarial tests. Limit: in its 5 recorded episodes it cannot be told from a rule that vetoes everything, except by one control added afterwards.
- Fit: the first half of INF-05 as is; ANTI-02 (decisions from sets and cost ranks). Missing: bundles derived from receipts, measured costs, a runner hook.
- Cost: S to M.
- Coupling: none; imported only by its test.
- Take: the code, fed from the claim registry's named rivals.
- Lines: 442
- Source: 06 Metis; 07 sheet 11.

### S-14 [RETIRE] Curricula and difficulty rules (archaeon/campaign1/sfe05.py and five others)
- Does: step a difficulty ladder up or down on population statistics; one rule targets the categories nearest a 50% pass rate per subject.
- Shown correct: one reported effect, at n 3.
- Fit: none is an adaptive staircase with a stated resolution (MEAS-12). All but one key on population statistics.
- Cost: not applicable.
- Coupling: each to its own engine.
- Take: nothing. The staircase is new.
- Lines: not reported
- Source: 07 section B.

### 3.4 Measurement and qualification

### M-01 [EXTRACT] Charon three-valued checks with counts (charon/probe/c1c2_checks.py)
- Does: hashes each input pool itself and fails a receipt whose fingerprint is missing, wrong, or different from the preregistration; fails a loader that admits rows marked failed; returns PASS, FAIL or INDETERMINATE with eligible and fired counts and a reason that separates "nothing could have fired" from "the loader admits nothing".
- Shown correct: 17 tests make every check fail and reach INDETERMINATE three ways; a live run failed both real blocks; re-run by another seat. Defects: a malformed count raises instead of failing; verdicts are strings.
- Fit: VERDICT TYPE. It meets SCI-02's own check word for word. Missing: the apparatus labels, a ruler hash, denominators.
- Cost: S.
- Coupling: stdlib; a hard-coded row schema.
- Take: the type and its tests. P1's verdict records already carry the same three values and counts.
- Lines: 394
- Source: 04 Charon checks.

### M-02 [EXTRACT] Techne instrument primitives (prometheus_math/battery.py, instrument_contract.py, measurement.py, migration_liveness.py)
- Does: a probe that reports whether a check can vary at all, reading the syntax tree to see whether it ignores its arguments; a certify step that requires positive, negative, invalid and sensitivity fixtures; a measurement type whose out-of-domain value cannot be read as a number or a truth value.
- Shown correct: 15, 11 and 12 tests; the probe caught a real always-true check; the contract documents its own hole. Gap: no counts and no error rates.
- Fit: the core of the QUALIFICATION GATE (MEAS-02) and verdict mechanics (SCI-02). The best detector in the tree for controls that cannot fail (T03). Absent from the Tityos inventory.
- Cost: S.
- Coupling: none outside its package.
- Take: code and tests, moved into the kernel.
- Lines: 739
- Source: 04 Techne loop primitives.

### M-03 [EXTRACT] Hecate corruption harness (hecate/metamorphic/harness.py)
- Does: copies a world, corrupts its rows with one of 9 operators (swap arms; copy treatment into the twin; drop every control row; copy one seed into every seed; and so on), reruns the evaluator and judges its reaction. A crash never counts as detection.
- Shown correct: run over 42 evaluators. It found a real control that passed with zero rows, and showed that in 32 and 33 of 42 evaluators a removed control was "caught" only by a crash.
- Fit: the closest existing form of MEAS-02's "break each control and expect a failure".
- Cost: M (it is bound to its row schema).
- Coupling: Hecate's program layout.
- Take: the operator set, re-implemented over the receipt schema, as the kernel's standing fire test.
- Lines: 726
- Source: 04 Hecate metamorphic.

### M-04 [EXTRACT] Nemesis trivial responders (roles/Nemesis/science/cheatlib.py)
- Does: three incapable responders (a constant; the most common answer; a reader of a field carried beside the item), a chance floor, four forgeries, and a greedy shrink of any fraud that passes.
- Shown correct: 12 tests. Defects: one pinned number counts missing evaluations as wrong; an empty population scores 0.0; it was committed together with the results it supports. Its test searches the whole tracked tree, holdout files included.
- Fit: TRIVIAL RESPONDERS (MEAS-04). Missing: a lookup responder, enforced equal denominators, integer rates.
- Cost: S.
- Coupling: stdlib.
- Take: the responder set, as the bottom rungs of every baseline ladder.
- Lines: 300
- Source: 04 Nemesis.

### M-05 [EXTRACT] Harmonia audit primitives and adjudicator (roles/Harmonia/qualification/primitives; roles/Harmonia/qualification/campaign1)
- Does: lists the verdict labels no input can reach; requires a calibration item for each label; runs a frozen rule on baselines that lack the construct; flags thresholds at the scale ceiling; a binomial tail; asks git whether the plan's first commit precedes the results'. A separate adjudicator refuses a verdict supplied from outside, rows that do not match the manifest hash, and analysis code that does not match the preregistered hash.
- Shown correct: each primitive fires on a real defect of 2026-09-30 and is quiet on a clean twin; the adjudicator's refusals are tested. Defects: an ablation helper forces silence, so "the defect escapes when the check is off" cannot fail; the freeze check ignores git return codes; outputs are booleans.
- Fit: preregistration and freeze checks (SCI-03 attainability, PROV-06, MEAS-08), and the only fixture in the tree where an outside verdict is refused (MEAS-11).
- Cost: S.
- Coupling: stdlib and git.
- Take: code, fixtures and clean twins. The same seat's older rule library is not taken (section 5).
- Lines: 682
- Source: 04 Harmonia primitives; 04 Harmonia qualification library.

### M-06 [EXTRACT] Hecate exact shadow evaluator and derived-file reproduction (hecate/alien/shadow_decisions.py)
- Does: re-decides every preregistered decision in fractions, replays the bootstrap on the same stream, and reports where the float decision diverges; tests regenerate every committed derived file and require equality.
- Shown correct: found two decisions sitting exactly on a threshold; 0 per-item mismatches.
- Fit: MEAS-07 (a second evaluator recomputes every decision) and REPR-05.
- Cost: the method only. The code is bound to one assay (L to reuse, M to rebuild).
- Coupling: its assay.
- Take: the method: a campaign's verdicts are recomputed by a second, exact evaluator.
- Lines: 556
- Source: 04 Hecate shadow.

### M-07 [EXTRACT] Artemis constructed-specimen panel and commit-reveal self-test (roles/Artemis/challenge/p11; roles/Artemis/selftest)
- Does: 17 specimens written as literal bytes, each with known heritable content (zero-bit painters, copiers, 1-bit and 4-bit carriers, stress cases), run against a certificate and its rivals under preregistered rules applied mechanically; a self-test that committed a hash of its answers before reveal and scored its own forecasts.
- Shown correct: the panel showed an older certificate passing all 4 zero-bit painters and rejecting 4 genuine replicators, and the alternative sorting all 17 as predicted. Its forecast score was 0.470 against 0.391 for a constant forecast, which is worse than the constant, and it reported that.
- Fit: the cleanest calibration set in the tree in the sense of REQUIREMENTS 1.3 (positive, negative, impostor, with a confusion table), and a SCI-06 exemplar.
- Cost: port M; rebuild S per world family.
- Coupling: archived copies of another seat's machine.
- Take: the layout: literal specimens with known answers, a confusion table, scored forecasts. P1's calibration table is the same object for BUILD.
- Lines: 1187
- Source: 04 Artemis.

### M-08 [EXTRACT] Nyx prediction packet and freeze (nyx/atlas/predictions/schema.py)
- Does: a record that must name a boundary, a claim, interventions with direction and numeric band, controls, and the outcome that kills the claim. Freezing stores a hash of the canonical bytes and refuses if they change. A correction is a new packet that names the old one.
- Shown correct: frozen packets re-hash; 3 tests. Defects: one hash is checked for length only and nothing recomputes it; the bar on self-adjudication is not in code.
- Fit: the form CAUS-04 needs (a mechanism model must predict new interventions before they run) and the append-only correction rule of PROV-04.
- Cost: S.
- Coupling: none.
- Take: schema and freeze, as the claim registry's mechanism-prediction record.
- Lines: 260
- Source: 04 Nyx.

### M-09 [EXTRACT] Diomedes attainability census (roles/Diomedes/coordinate_census.py)
- Does: five arithmetic checks before a gate is used: headroom between ceiling and oracle; the gate inside the attainable range; the gate above its own error; a cluster bootstrap; an exact identifiability ceiling.
- Shown correct: planted controls give exact expected values; agreement with an independent script to 1e-9. Defects: a zero-width bootstrap when the cluster count is a power of two; one label mix-up.
- Fit: MEAS-08 and SCI-03: can the verdict be attained at all. Its state-independent ceiling is an in-sample estimate, not a bound.
- Cost: S.
- Coupling: none.
- Take: the checks, beside the power gate P1 already runs.
- Lines: 388
- Source: 05 Diomedes.

### M-10 [EXTRACT] One-character leak worlds and the look-ahead cheat (charon/probe/charon_gate_fire_2026-08-25.py; tyche/audits.py)
- Does: plants per-arm leaks of one character (trailing space, look-alike letter, zero-width space) and requires the leak check to fire on each and stay silent on clean worlds; builds a world whose label is the next step's input, with an organism allowed a forbidden look-ahead, and requires the audit to catch it.
- Shown correct: each planted leak fired 40 of 40 and clean worlds stayed silent; the look-ahead cheat is caught and an honest organism passes.
- Fit: WLD-05's own check ("a planted one-character leak is caught") and the fire-test pattern of MEAS-02.
- Cost: S.
- Coupling: small.
- Take: both constructions, as kernel fixtures.
- Lines: 180
- Source: 04 Charon exit-review-3; 05 Tyche.

### M-11 [REBUILD] Measured false-positive rate against a same-distribution reference (ergon/probe/f_null.py)
- Does: draws 200 pairs of disjoint samples from one pool through the production path and freezes the 95th percentile of each of 12 divergences; a classifier layer with a ceiling of 0.55.
- Shown correct: tests show the classifier layer firing on obviously different texts. Defects: it returns "passed" when an arm has fewer than 2 samples, and a test asserts that; it passes an empty list; the ceiling on 80 texts is about one standard error above chance; it validated one renderer while another was deployed.
- Fit: the need is MEAS-01, a measured false-positive rate on every datasheet. This implementation fails SCI-02, MEAS-07 and MEAS-08.
- Cost: rebuild S.
- Coupling: its probe's types.
- Take: the idea of measuring the false-positive rate on the real path. Rewritten with exact tails.
- Lines: 731
- Source: 04 identity-null calibration.

### M-12 [HISTORICAL CONTROL] Necropolis admissibility ladder and its cases (engine/necropolis/workshop)
- Does: computes a ladder (path exists, imports, executes, controlled, admissible) for 93 old instruments from 194 cases of 10 kinds written by someone other than each tool's author.
- Shown correct: a recorded run of 174 PASS, 8 FAIL, 9 INFO, 3 ERROR. The failures include answer-reading cheats scoring 0.75 and 1.0 against real old graders. Defect: no rule requires a control in the failing direction.
- Fit: the best executable failure-fixture corpus: real old code with real recorded failures (T01, T03, T05).
- Cost: port the cases M; the ladder rebuilds in S.
- Coupling: imports every tool it tests.
- Take: the cases, as the first load of the kernel's fixture suite.
- Lines: 3691
- Source: 04 Necropolis.

### M-13 [HISTORICAL CONTROL] Gates and audits whose own controls cannot fail
- Does: a leak classifier whose positive control is planted on a pair already separable at 1.0000 (charon/probe/exit_review_3_attack.py); a commit hook that prints ADMISSIBLE after three hard-wired probes and never inspects the commit (attacks/preflight.py); an older rule library with an anti-conservative quantile table; a planted-relation gate that returns 0.0 on any error; validators that check form only.
- Shown correct: each defect was verified in source by the worker.
- Fit: fixtures for T03, T04, T10, T16, T20, T22. The hook still runs: it printed ADMISSIBLE on the commits of this package.
- Cost: S each to turn into a fixture.
- Coupling: their engines.
- Take: section 5 lists them. None is used as an instrument.
- Lines: not reported
- Source: 04 exit-review-3; 04 attacks; 04 Harmonia qualification library; 04 Techne; 04 list B.

### M-14 [HARDEN] comms manifest tool (comms/manifest.py)
- Does: writes and verifies a hash for every file in one directory over bytes with line endings normalised.
- Shown correct: 2 tests (copies with different line endings hash equal; a real change is caught). Gaps: no subdirectories; a rewritten manifest still verifies; verification passes when no line of the manifest parses.
- Fit: PROV-02 as written. It is the tool that requirement's check names.
- Cost: S (recursion; a non-empty check; an anchored manifest hash).
- Coupling: none.
- Take: the tool. It is used throughout this package.
- Lines: 85
- Source: 04 comms manifest; 06 comms.

### M-15 [RETIRE] One-off audits and narrow predicates (Clymene repository probe; Elenchus solver check; Eos intake states; Harmonia emission census; Techne synthetic null; Hypatia stall predicate)
- Does: each checks one thing in one place: archived repositories against recorded hashes; a solver's "optimal" against a closed form; typed intake states; which generators write their own verdicts; whether a null world is learnable; whether a process has stalled.
- Shown correct: varies; several have self-tests.
- Fit: exemplars and fixtures (T02, T19, T21); no kernel slot. Two pieces of verdict vocabulary are worth keeping: a state for "not examined, because the verdict could not have depended on the item", and a liveness rule that refuses "stalled" unless the probe could have seen progress.
- Cost: S each to rebuild as needed.
- Coupling: their seats.
- Take: nothing as code.
- Lines: not reported
- Source: 04 sheets for each.

### M-16 [UNKNOWN] ergon/probe/r3_controls.py
- Does: by its header, a control with measured operating characteristics (false alarm 5%; power 100% at +15 points and 85% at +10 points).
- Shown correct: not verified by any worker.
- Fit: if true, the only measured control error rate in the old tree (MEAS-01).
- Cost: unknown.
- Coupling: its probe.
- Take: undecided. Read it before writing the first datasheet.
- Lines: not reported
- Source: 04 COULD NOT DETERMINE.

### 3.5 Causal, lineage and intervention instruments

### C-01 [HARDEN] Ananke Wave-2 intervention and qualification library (roles/Ananke/research/harvest/wave2/W2-F/explib)
- Does: runs two arms in lockstep on a generic engine protocol with a common-random-number check; labels each intervention unit UNAPPLIED, NOT_REACHED, ABSORBED, REACHED or INCONSISTENT; audits a control for being a no-op, a constant, a mirror identity or irreversible; certifies a gate by null false-pass rate with an exact bound, committed adversaries, a passing plant and an eligible-cell count.
- Shown correct: 40 tests, 35 of them engine-free; a table mapping 20 historical defects of its engine to a test that fires on each; its guards caught two of its own bugs. Limits: one seat built it in one night; it has never run on a fresh campaign; its own packaging says "do not cite"; floats.
- Fit: the nearest existing thing to the RULERS layer: CAUS-02 ("counts only if it changed state"), MEAS-02 (gate certification with a fire test), part of MEAS-01. Fails MEAS-07. No runner calls it.
- Cost: promote S to M (review; rational arithmetic; an adapter to the organism protocol); rebuild M to L.
- Coupling: its core imports no engine.
- Take: the core, after it passes the P1 qualification gate like any other ruler.
- Lines: 1998
- Source: 05 Ananke Wave-2.

### C-02 [EXTRACT] Ananke carrier-swap lens and its failure modes (prometheus/ananke/lens.py, lens_swap.py, swap_rel.py)
- Does: runs mirror-partner worlds that share every random draw and differ in the sign of a cue; copies one named state array into the partner between ticks; asks whether the readout follows the partner; issues FLIP, NO-EFFECT or CHANCE.
- Shown correct: four designed carriers recovered and wrong-carrier negatives rejected; all three verdicts shown reachable. Failure modes found by its own seat: the mirror design makes two different swaps a single measurement (an exact identity in 93 of 93 groups); "applied" is not "reached"; FLIP cannot be reached below a normal accuracy of about .62 to .66; intervals are about twice too narrow across seed namespaces (20 flips against 8.3 expected).
- Fit: CAUS-03 nearly word for word, on one engine. Fails ORG-10, CAUS-05, MEAS-01, MEAS-02, MEAS-07.
- Cost: generalise M. Rebuilding the code is M; rediscovering the failure modes is L.
- Coupling: its engine; no importers outside its seat.
- Take: the design, and its eight documented failure modes as fixtures. P1's store interchange is the same ruler written against declared stores in exact arithmetic.
- Lines: 988
- Source: 05 Ananke lens.

### C-03 [EXTRACT] Cosmos system protocol and planted-system gate (prometheus/cosmos/c3)
- Does: a generic system interface (initialise, noise, step, readout, full state) in which the harness draws the noise; decodability of the cue from state beyond the observation, against a permutation null; a whole-state swap between paired episodes; classes NONE, PASSIVE, FUNCTIONAL, INCOHERENT, INDETERMINATE.
- Shown correct: six planted systems each classed as expected on 5 of 5 fresh seeds, after an earlier version of the gate failed and was amended. Run once on another engine, the verdict changed with which arrays were declared and with a one-tick shift of the swap.
- Fit: the closest existing shape to ORG-01 for interchange, and the MEAS-02 pattern in code. Fails ORG-10, CAUS-05, MEAS-07. It localises nothing.
- Cost: S (per-component swaps; a sweep over swap ticks).
- Coupling: numpy, scipy; no importers.
- Take: the planted-system gate, and one rule: an interchange verdict is reported over a sweep of swap ticks, with the declared state boundary on the row.
- Lines: 461
- Source: 05 Cosmos.

### C-04 [EXTRACT] Crius store-content conditions (crius/evaluate.py)
- Does: runs one lifetime under each of: accumulated store; empty store; reset; scrambled; blocks removed by id; blocks or the whole store transplanted from a fork; code only; and identifiers only, with empty contents.
- Shown correct: a designed reuse organism scores 46.1 against 20.7 with an empty store; the identifiers-only condition caught organisms using the id counter as a clock (dossier). Weaknesses: one calibration artifact gives every typed candidate the same gain; empty records cost nothing.
- Fit: the developmental control set of DEV-04, and transplant with a sham (XFER-03, CAUS-01), at store level.
- Cost: S to M.
- Coupling: Crius internals.
- Take: the list of conditions, as protocol operations on persistent stores. The identifiers-only sham joins the standard set.
- Lines: 1000
- Source: 05 Crius; 01 sheet 2.

### C-05 [EXTRACT] Ares edge- and loop-aware lesions with a matched sham transplant (ares/carriers.py)
- Does: cuts each class of cross-step carrier separately (self-loops, recurrent edges, strongly connected components, leak, plasticity); transplants a carrier into random hosts against a matched random subcircuit; measures the chance that one mutation creates a carrier.
- Shown correct: hand-wired carriers classified and told apart; it catches an output-node self-loop that node ablation could not remove. Defects: a float tie artefact; one result first reported as the best of 9.
- Fit: CAUS-05 (lesions reach the whole candidate circuit) and CAUS-01, for PN. Fails MEAS-07, ORG-10.
- Cost: rebuild for PN S to M.
- Coupling: Ares internals.
- Take: the cut classes and the matched sham, rewritten in integers for PN.
- Lines: 343
- Source: 05 Ares.

### C-06 [EXTRACT] Archaeon material tracing and heredity record (archaeon/lineage; archaeon/causal_lens; archaeon/attribution)
- Does: re-executes each birth on a label-carrying shadow of the frozen machine, so every byte records where its value came from, and refuses the attribution if any result differs from the real machine. Records four identities per birth (executor, executed material, per-byte contributors, host). A cross-engine record in which ancestry follows only copying and material contribution, never location, hosting, labels or resemblance, with the values YES, NO, NOT_IDENTIFIABLE, NOT_APPLICABLE, ILL_POSED.
- Shown correct: designed fixtures with known answers (a host that is not the ancestor; a half-and-half recombination; a mutation byte as new material); a differential test on 6,000 random tapes; the record format caught a defect in its own adapter. On another engine, labels by resemblance disagreed with traced ancestry on 847,000 births. Limit: data flow only, not control or address dependence.
- Fit: CAUS-06 and PROV-09 inside one machine. The record format is engine-neutral.
- Cost: a tracer is M per substrate; adopting the record and validator is M.
- Coupling: its machine; one adapter read logs from outside the repository.
- Take: the record format, the validator rules and the fixture set. A shadow tracer for WM is new.
- Lines: 5495
- Source: 05 Archaeon taint; 05 Archaeon causal lens.

### C-07 [EXTRACT] Random-program census (archaeon/z80atlas/census/copier_census.py)
- Does: sorts 10,000,000 uniform random programs per stratum by behaviour, with no search.
- Shown correct: 96 exact copiers in 10,000,000 in one instruction set and 0 in 10,000,000 in another; a hand-written replicator as the ruler.
- Fit: SRCH-03, the random-hit rate.
- Cost: S.
- Coupling: its machine.
- Take: the procedure. P1 already runs it: 0 of 2,000,000 random programs reach 0.9.
- Lines: 317
- Source: 05 Archaeon causal lens.

### C-08 [UNKNOWN] Dependence tracers on a side branch (roles/Bellerophon/e003_2026-09-29/tools; a Nestor shadow tracer)
- Does: label-carrying twins of a byte machine that track data, address and control dependence, with every run value-checked against the frozen machine.
- Shown correct: 32,827 births replayed bit for bit; 28 of 28 fixtures. But raw agreement between two tracers failed at 0.974 and was cleared by an amendment adopted after production; the verdict of record is OPEN; the specification and fixture pack exist only on a branch 85 commits ahead of main.
- Fit: the strongest dependence semantics in the tree (CAUS-06, PROV-09).
- Cost: porting the semantics M, after a decision to merge the specification.
- Coupling: a host-local harness; a branch that is not main.
- Take: undecided. It needs a ruling on the branch.
- Lines: 1665
- Source: 05 Bellerophon; 05 SURPRISES 2 and 3.

### C-09 [HARDEN] Artemis counterfactual variant transmission test (roles/Artemis/challenge/p11/certs.py)
- Does: mutates each parental byte and asks whether the difference appears in offspring across generations and draws; counts distinct transmitted classes as bits.
- Shown correct: every cell of a 17-specimen panel matched its preregistered prediction. False accepts found later by another seat: a specimen built never to reproduce itself passes on 9 of 9 seeds; a single seed is a coin flip. A repair is specified and not adopted.
- Fit: heredity by intervention: an alternative to tracing for CAUS-06 where a tracer is impractical, as in PN.
- Cost: S to M (adopt the repair; integer verdicts; a genome adapter).
- Coupling: stdlib.
- Take: the test with the repair, qualified against its own false-accept specimens.
- Lines: 115
- Source: 05 Artemis.

### C-10 [HISTORICAL CONTROL] Nestor copy assay and niche tags (p11.py; z8taint.py)
- Does: re-executes an interaction with the victim randomised and one channel blocked; tags bytes by the niche where their value was made.
- Shown correct: the copy assay catches its predecessor's three false accepts. But it passes all four zero-bit painters at rates of 0.90 to 1.00 and rejects genuine replicators. The tags record where, not whose.
- Fit: none as heredity rulers. The copy assay is the standing example of a ruler that certifies the impostor.
- Cost: not applicable.
- Coupling: its machine.
- Take: the copy assay together with the Artemis panel, as a paired fixture: an instrument, and the calibration set that exposes it.
- Lines: 633
- Source: 05 Nestor copy assay; 05 Nestor material tags.

### C-11 [EXTRACT] Aether one-bit twin assay and single-parent audit (Aether/observatory/aeth03_propagation.py, aeth03_assay_audit.py)
- Does: forks two copies of a world that differ in one bit under shared noise and follows the spreading difference, voiding the run if a difference appears outside the declared causal radius; replaces one neighbour's state alone to test whether it suffices for a new difference.
- Shown correct: a null twin (the bit flipped twice) never differs; a designed relay chain gives one generation per hop; an undeclared longer-range effect is caught. Limit: its generation count equals the causal generation in 84% to 100% of events depending on the law, while a docstring still claims exactness.
- Fit: CAUS-02, exact twins with a built-in validity check; a single-component sufficiency test.
- Cost: S to M.
- Coupling: its lattice.
- Take: two validity checks: a null twin, and a declared radius that voids the run when violated.
- Lines: 702
- Source: 05 Aether.

### 3.6 Infrastructure

### I-01 [HARDEN] Agent Fabric v0.2 (fabric/) -- the one queue and the one lease
- Does: a Postgres job queue. The database enforces one running attempt per task and one unreleased lease per resource. A claim takes the task and its leases in one transaction. Heartbeat fencing. Workers run a repository script at a pinned commit under an environment allow-list. The runtime uploads outputs as hashed blobs.
- Shown correct: 43 tests; a nine-part pilot with evidence files, including a recorded failure before a fix; a lease race always has exactly one winner. Its owner lists 23 open defects. Workers are Linux-only as written, so no attempt has ever run on M1 or M2.
- Fit: COMP-04, INF-01, PROV-05. Partial COMP-02, COMP-05, PROV-07, REPR-06. Fails PROV-01, PROV-03, MEAS-11 and ANTI-01 (one shared database credential), ENRG-01.
- Cost: M (a Windows worker; CPU and GPU-hour caps; keep the token counts; an append-only trigger). L with the runner's gates. Rebuild L.
- Coupling: M1 Postgres; credentials through the evidence-wiki connector from a tracked file.
- Take: the store and the lease now, since it is already the lease authority the operator ruled for. Workers when a Windows worker exists. Until then Phase 3A runs a local runner on M1 under a Fabric lease.
- Lines: 3878
- Source: 06 Fabric.

### I-02 [HARDEN] Toolbox receipt schema and local executor (prometheus/toolbox/receipt.py, backends/local.py)
- Does: one record per run with required keys; an id from the hash of the canonical body; a chain through the previous id; append-only lines flushed per record; a strict reader that names truncation, edits and chain breaks; engineering and science ledgers kept disjoint; a resume under a different experiment is refused; a wall-time budget is enforced.
- Shown correct: 231 tests; 92 mutants caught in the committed ledger; cross-platform replay. One past defect: a wrong twin once passed an admission probe that ignored actions (repaired).
- Fit: the receipt schema and ledger format: PROV-02, INF-01; partial PROV-01, PROV-04, COMP-02, COMP-05, REPR-01. Fails MEAS-06, ENRG-01, INF-03.
- Cost: S to M (code commit; a verdict block with ruler hash; energy and token fields; completion gated on validation).
- Coupling: stdlib; one importer.
- Take: the schema and the reader, as the one receipt format.
- Lines: 5962
- Source: 06 toolbox.

### I-03 [EXTRACT] Hash chain, prediction window and deployed-build check (SerendipityFoundry/SerendipityFoundryEngine/sfe/events.py, release.py, deploy/verify_deploy.py)
- Does: every state change appends an event to a per-world hash chain; a prediction counts as prospective only if its sequence number precedes the experiment's commitment; a script checks that the served build equals pinned, normalised file hashes.
- Shown correct: 436 tests on temporary databases. Defects at head: observation content is outside the chain; the verdict is supplied by the client; budget enforcement defaults to measuring only.
- Fit: PROV-04 and PROV-06 inside one engine; REPR-05 as a pattern (what was validated is what is deployed).
- Cost: extract S. Making the service the canonical ledger XL.
- Coupling: SQLite; a web service on M2; ledgers outside the repository.
- Take: the three mechanisms. The service is retired (I-10).
- Lines: 362
- Source: 06 SFE.

### I-04 [EXTRACT] Vivarium database invariants (vivarium/migrations)
- Does: 12 triggers enforce one active row, legal transitions only, frozen terminal rows, an immutable sealed request, append-only events, errata and receipts, and an ordered outbox. The runner sees only id, specification and hash.
- Shown correct: 590 tests; a canary run with zero human commands. Record: about 85,727 phantom experiments in the engine it drove; 98% of each row's wall time was round-trips to that engine.
- Fit: PROV-04 enforced in the database, which is the only place in the tree where invariants are more than code; the blinded runner is the MEAS-11 shape.
- Cost: port the triggers M.
- Coupling: SFE and the evidence service on M2.
- Take: the triggers, onto the Fabric store. The service is retired (I-10).
- Lines: 13393
- Source: 06 Vivarium.

### I-05 [KEEP] comms database identity guard (comms/identity.py)
- Does: refuses a connection whose system identifier or database name differs from a tracked list. Fails closed, including for an unknown environment.
- Shown correct: 18 tests, including a structurally identical database that is refused. Stated limit: a physical clone keeps the identifier.
- Fit: PROV-03, custody of the store.
- Cost: none.
- Coupling: none.
- Take: as is.
- Lines: not reported
- Source: 06 comms.

### I-06 [HARDEN] Database connector and credentials (evidence_wiki/ew/db.py)
- Does: pooled connections with credentials taken from the environment, then a local file, then a tracked file; applies the identity guard.
- Shown correct: in daily use by every store. Open defect: credentials in a tracked file, and in three other tracked places.
- Fit: every store depends on it. ANTI-01 and MEAS-11 need a separate write credential per authority, and none exists: no store in the tree separates write authority at the database.
- Cost: S to move credentials out of git. Separating write authority is new work (M).
- Coupling: every database client.
- Take: the connector, after rotation, with one credential per authority (generation, reality, interpretation).
- Lines: not reported
- Source: 06 evidence_wiki; 06 SURPRISES 4.

### I-07 [HARDEN] Atlas derived index (atlas/)
- Does: versioned harvesters read git blobs and ledgers into rows that cite a harvest run and a source (commit, blob, path, lines, file hash); rule-based signals; an ASCII report.
- Shown correct: 58 tests; parsed counts matched sources in every sample. Defects (Ixion): "completed" mapped to POSITIVE; 31% of commits unattributed; 8.58 days of lag; run by hand.
- Fit: a derived index with strong provenance pointers. Fails PROV-01 (one adapter per engine) and INF-04 (no schedule).
- Cost: M (one harvester for the one receipt schema, on a schedule).
- Coupling: M1 Postgres.
- Take: the run, source and fact tables and the report. The per-engine harvesters stop with the engines.
- Lines: 4505
- Source: 06 atlas.

### I-08 [HARDEN] Model-call layer (prometheus_llm/)
- Does: one client for several providers with fallback and retries; an audit log of model, tokens, cost and a prompt hash, written only if an environment variable is set.
- Shown correct: 32 offline tests. In practice the log has never been enabled in tracked code; it has 5 importers against 60 to 66 files that call providers directly; there is no fork-type field; one path returns no tokens.
- Fit: token meter and model identity (INF-03, PROV-07, part of INF-06). Fails INF-02.
- Cost: M (log on by default and append-only; fork and campaign fields; the direct callers routed or forbidden).
- Coupling: host-local key files.
- Take: the client, as the only permitted call path, with the fork type as a required argument.
- Lines: 896
- Source: 06 prometheus_llm; 07 sheet 10d.

### I-09 [EXTRACT] Digest and alarm parts (scripts/send_brief_email.py; agents/alethelia; achilles/census render; roles/Pronoia/science/productive_liveness.py; roles/Atalanta/reference/null_bound.py)
- Does: sends a plain-text and HTML email and records the dispatch; renders fields that each carry their query or UNKNOWN with a reason, rules that are FIRED, CLEAR or INDETERMINATE, and a DEGRADED banner when a source is unreachable; a failure banner that keeps the previous page; a health function of timestamps alone; a rule that parks a loop after a declared number of non-productive ticks.
- Shown correct: self-tests and tests on the parts. The live brief, built on heartbeats, listed a seat dead for 178,309 minutes as an action item on the day of this report.
- Fit: parts for HUM-02 and INF-04. Nothing today reads receipts; every existing digest reads institutional state.
- Cost: S to M once the receipt schema exists.
- Coupling: mail credentials on one host only.
- Take: the mailer and the honest-rendering model. The heartbeat producers are retired (I-10).
- Lines: not reported
- Source: 06 reporting loop; 06 Alethelia; 06 achilles; 06 productive_liveness; 06 section C.

### I-10 [RETIRE] Services, parallel queues and commit-on-write
- Does: three services (the SFE ledger service, the Vivarium loop, the evidence-wiki service); at least eight queue or lease mechanisms (SFE work items, the Vivarium queue, a Redis queue with leases and CPU tokens, the comms task queue, two agora tables, host-file leases, queue files from an August loop); a row writer that calls git from campaign code; reporting that reads heartbeats; a fleet census.
- Shown correct: each worked for its owner. Together they are the coordination load Ixion measured.
- Fit: they fail COMP-04 (one queue, one lease), PROV-08 (no campaign code calls git) and INF-07.
- Cost: retire S each; the SFE service M, because two ledgers outside the repository must first be preserved with hashes and a custody note. One mechanism is ported before retirement: the kill on a child's CPU time, the only enforced CPU cap in the tree (S).
- Coupling: M2 services; Redis on M1; scripts on M4.
- Take: nothing. Each retirement is an operator act; this row is a recommendation.
- Lines: not reported
- Source: 06 section B; 06 sheets.

### I-11 [KEEP] Base role, working contract and worktree guard (roles/base-role; archaeon/workspace.py)
- Does: the tracked rules every seat inherits (work in a worktree; named commits; explicit paths; tests before push; a journal; hashes over normalised bytes) and a guard that refuses work in the canonical checkout and fails closed.
- Shown correct: 15 base-role tests; 6 guard tests; 31 importers of the guard. Gap: the guard records a dirty tree and does not refuse it.
- Fit: REPR-06 in part. It is the discipline this package was produced under.
- Cost: S to refuse dirty trees.
- Coupling: git.
- Take: as is, plus the refusal.
- Lines: 103
- Source: 06 archaeon workspace; this session.

### I-12 [KEEP] The four crawler packages and the failure taxonomy (docs/phase3/intake)
- Does: the forensic record: dossiers per seat, engine and ruler indexes, 24 failure classes with instances.
- Shown correct: the workers found the dossiers right far more often than wrong; section 7 lists where they were wrong.
- Fit: the source for the kernel's failure fixtures, and for base rates in forecasts.
- Cost: none.
- Coupling: none.
- Take: as is.
- Lines: not reported
- Source: the crawler packages.

### I-13 [EXTRACT] Cross-host verification harness (Aether/test; ops/campaigns/C-002/E-007)
- Does: a differential corpus between an oracle and a fast implementation (hand-worked cases, seeded fixtures, property-based worlds, short trajectories); golden vectors; rejection of mutant implementations; a reduction that ran the same units on 4 hosts under two operating systems and two numpy versions.
- Shown correct: 133 physics tests; 19 attempts on 4 hosts, all matching.
- Fit: REPR-01, and COMP-01's reference check: the best worked example in the tree.
- Cost: S to M.
- Coupling: its lattice; rented pods.
- Take: the layout of the corpus and of the cross-host reduction.
- Lines: not reported
- Source: 02 Aether.

### I-14 [UNKNOWN] State outside the repository (Archaeon file queues; tables in M1 Postgres; whether the M2 services are alive)
- Does: not examined. No database connection and no network probe was allowed.
- Shown correct: not examined.
- Fit: unknown.
- Cost: unknown.
- Coupling: unknown.
- Take: undecided.
- Lines: not reported
- Source: 06 COULD NOT DETERMINE.

----------------------------------------------------------------------

## 4. What has to be written new

Nothing in the tree is a starting point for these. In rough order of how much
the design leans on them.

| # | new component | why nothing can be salvaged | requirement |
|---|---|---|---|
| 1 | Demand-certificate solvers: the exact best score of each restricted class (no memory; k states; non-adaptive; nothing carried across episodes; lookup of bounded size) for a world in which an organism acts | no code computes any of these; existing bounds are per task, in floats, used after the fact | WLD-02, MEAS-03 |
| 2 | The WM kernel: compiled, integer, total, with tagged blocks, call with arguments, rent, and switches | no machine has tags or rent; none meets the throughput requirement; the nearest is Python with non-integer values | ORG-01 to ORG-09, COMP-01 |
| 3 | The search-power instrument: recovery of planted targets by distance and budget | no component measures it | SRCH-02, SRCH-03 |
| 4 | The runner's refusals: preregistration is an ancestor; the verdict table is total and reachable; rulers hold current qualification receipts; a baseline ladder exists; budgets are capped | each exists somewhere as a reading rule, nowhere as a gate on starting a run | SCI-03, MEAS-02, MEAS-06, COMP-05 |
| 5 | Separate write authority for generation, reality and interpretation | every store shares one credential | ANTI-01, MEAS-11 |
| 6 | Custody of sealed worlds outside the working tree, with an access log | sealed files are tracked and readable; today's incident | PROV-10, WLD-06 |
| 7 | The REF arm: three conventional learners under the same protocol | no conventional learner and no gradient regime exists in scope | ANTI-08, ORG-07 |
| 8 | PN: a fixed-point plastic network whose weights persist across episodes | no network keeps weights across episodes | ORG-07, DEV-01 |
| 9 | RETAIN and FAMILIES world families | no world holds a hidden mapping across fast-state resets; none has families with meta-structure | WLD-09 |
| 10 | Adaptive staircase with stated resolution; carrier-noise opt-out test | only threshold rules on population statistics exist; no opt-out test anywhere | MEAS-12, CAUS-07 |
| 11 | Energy estimate and token counts on every receipt | nothing records energy on any owned host; the one cost record keeps dollars and drops tokens | ENRG-01, INF-03 |
| 12 | The claim registry and the four standing tables | no single register of claims with levels exists | SCI-04 |
| 13 | A measured reference class of mechanism signatures | no signature space exists | ANTI-05 |
| 14 | A shadow tracer for WM | tracers exist for byte machines only | CAUS-06, PROV-09 |

Three of these already have a first version in prototype/p1_slice/: a RETAIN
world with an exact no-carry bound, a class-exclusion ruler in exact
arithmetic with a power gate, and a search-power curve.

----------------------------------------------------------------------

## 5. The record as a control corpus

The kernel's fixture suite is built from real defects. Report 04, list B,
gives 31 with path, commit and class. The other six reports add the ones
below. The first eighteen are the set I would load for the day-30 gate; the
kernel must catch each.

| # | fixture: what is broken | class | where it comes from |
|---|---|---|---|
| F-01 | an answer key travels inside the probe | T01 | reasoning_phase0.py:131, with an executable cheat reader (04 B1) |
| F-02 | a generator writes its own verdict | T02 | a1_catalog_cross_product.py:182-185 (04 B3) |
| F-03 | a control arm with zero rows passes | T03 | Hecate HT-47f4c02be4 W1 evaluate.py:14-15 (04 B9) |
| F-04 | a positive control planted on a pair already separable | T04 | exit_review_3_attack.py:233-238 (04 B27) |
| F-05 | too few samples counted as a pass, with a test asserting it | T12 | f_null.py classifier_auc (04 B28) |
| F-06 | a baseline that arrives after the data | T08 | Ensorain tuned batch rung (W-03) |
| F-07 | a verdict label no input can reach | T12 | Harmonia reachability fixture on a Tyche hypothesis (M-05) |
| F-08 | the champion is selected on the evaluation set | T09 | ares/search.py:291-294 (02, 03) |
| F-09 | a transplant reported as spontaneous | T14 | Archaeon 26 of 26 flags (O-07) |
| F-10 | a hash over host bytes | T18 | evidence_wiki/ew/store.py:87 (06) |
| F-11 | a search that cannot take neutral steps | T13 | falsifier_46.py:117-128 (S-03) |
| F-12 | a float comparison sitting exactly on a threshold | T10 | hecate/alien/analyze.py:276 (04 B19) |
| F-13 | a ruler that certifies the impostor | T14 | copy assay against the zero-bit painters (C-10, M-07) |
| F-14 | a plan committed together with its results | T11 | Ananke W-O PLAN.md at 93e2e544b (04 B18) |
| F-15 | thresholds frozen without checking that the verdicts are attainable | T12 | this package: prototype v1 gate, RECEIPT_qualify_v1_GATE_FAILED.json |
| F-16 | a search that can read a sealed set | T18 | this package: salvage_reports/00_SEARCH_RULE_INCIDENT.md |
| F-17 | two "independent" implementations that share random streams | T17 | toolbox integer world and its alternate (W-06) |
| F-18 | a safeguard that prints a pass without inspecting anything | T20 | attacks/preflight.py hook (M-13) |
| F-19 | a bound proved for one input distribution and used under another | T10 | Ananke .75 bound against .763 measured (05 question B) |
| F-20 | two interventions that are one measurement by design | T03 | mirror identity in 93 of 93 groups (C-02) |
| F-21 | an interchange verdict that flips with the swap tick or the declared boundary | T12 | Cosmos certificate on another engine (C-03) |
| F-22 | a shortcut search over a hand-built list of cheap policies | T08 | Ludus admission of Nim (W-04) |
| F-23 | an acceptance condition that is a constant | T03 | Aphrodite run_s3s4.py (O-13) |
| F-24 | a reported maximum that is a training reward | T09 | Archaeon frontier digest (S-02) |
| F-25 | a detector that fires on almost everything | T05 | 1,658,614 firings in 3,719,136 evaluations (S-02) |
| F-26 | shaping in the fitness with no arm that removes it | T07 | Ananke search (S-10) |
| F-27 | an answer key tracked beside the test and regenerable from a public seed | T01 | hecate/alien answer key (W-10) |
| F-28 | a verdict supplied by the client | T02 | SFE observation outcome (I-03) |
| F-29 | campaign code that calls git | T18 | primordial row writer (I-10) |
| F-30 | a heredity test that passes a specimen built never to reproduce | T14 | Artemis variant test before repair (C-09) |

Fixtures 15 and 16 are mine, from today. A design that asks others to keep
their failures keeps its own.

----------------------------------------------------------------------

## 6. Old signals worth re-testing in the new apparatus

REQUIREMENTS SCI-12 allows a few. None of these is a claim today. Each is a
prediction that the new instruments can settle cheaply.

| # | old observation | what the new apparatus asks | experiment |
|---|---|---|---|
| 1 | Aphrodite: a supplied library cut search cost 47 and 345 times at two tiers, but donors starting from nothing derived no schema in 8 of 8 runs | is there COMPOSE above a no-reuse solver at equal budget in CHAIN, and does any savings ratio rise with stage | P6 (H6) |
| 2 | Ananke: designed organisms at .850 and .978 exist in a space where search found .503 and .479 | does the search-power curve at that needle size predict the miss | P4 (H3) |
| 3 | Crius and Proteus: unverified worker claims that a neutral path to the target exists | reach under neutral, strict and margin acceptance, as in P1's reach.py | P5 |
| 4 | Ensorain: the Even process needs a 1-bit state that no finite window holds | first HOLD known-law recovery: window learners sit on the enumerated floor, a 1-bit holder does not | P1, P2 |
| 5 | Ares: a 1-bit latch carried by a self-loop or by leak, told apart by cuts | calibration case for PN lesions | P3 |
| 6 | Theseus: model-written genomes sat closest to the known library | signature dispersion, model-guided against blind, at equal certified level | P8 (H7) |
| 7 | Archaeon census: 96 exact copiers in 10,000,000 random programs in one instruction set, none in another | random-hit rate as a property of the instruction set, measured for WM under each switch | P3 |
| 8 | Archaeon campaign 1: an up/down curriculum gave +0.155 at n 3 | H3's second half: a curriculum with rewarded intermediate stages shrinks the reach gap | P4 |
| 9 | P1 prototype: the from-scratch builder used never-written registers as constants, as the byte soups did | register initialisation swept as a world variable | P3 |

----------------------------------------------------------------------

## 7. Where the workers found the crawler record wrong

The dossiers held up well. These are the exceptions the workers verified in
source. They matter because the requirements were derived from the crawler
reports.

1. Tityos REPORT says a Charon leak classifier "caught a planted 1-character leak at 1.0000". Its positive control was planted on a pair already separable at 1.0000 and could not fail (04 SURPRISES 1).
2. The Tityos inventory omits a tested, generic instrument library in prometheus_math (04 SURPRISES 2).
3. The Ananke dossier says rented compute was never used. Its conformance suite did run on a rented host: 139 passed (02 SURPRISES 1).
4. Ixion REPORT says inference cost is recorded nowhere. Fabric's model attempts record the model and the dollar cost, and drop the token counts (06 SURPRISES 2).
5. Ixion counts 21 external importers of the toolbox. One package imports it; the rest are mentions (06 SURPRISES 12).
6. The Proteus "cross-host" replay was three runtimes on one machine (01 SURPRISES 5).
7. Crius has 53 opcodes, not about 49 (01 SURPRISES 2).
8. The Archaeon frontier registry records 4,099,920 evaluations against 3,719,136 in the dossier; the reachability table has 1,277 rows against 1,265 (07 SURPRISES 8).
9. The toolbox mutation ledger has 92 entries, all caught; the dossier says 85 of 85 (03 SURPRISES 8).
10. The SFE package is 9,423 lines here against 9,783 in the dossier (06 SURPRISES 14).
11. A world-grammar leak reported as fixed is unchanged in the code (03 SURPRISES 5).
12. Ludus's "25 tests" are scripted assertions; it has no pytest functions (03 SURPRISES 7).
13. Two cross-host replays of the Bellerophon soup are absent from its dossier (01 SURPRISES 4).
14. Tyche's "exact" mutual information is a plug-in estimate with a permutation correction; only the table-law order is exact (03 SURPRISES 2).
15. M1's processor is recorded two ways in the tree. I measured it this session: Ryzen 7 7700X, 8 cores, 16 threads, 31.6 GB (06 SURPRISES 11).

None of these changes a requirement. Item 1 strengthens MEAS-02; item 4
softens one line of the Ixion account without changing INF-03.

----------------------------------------------------------------------

## 8. What salvage changed in the design

The architecture was frozen before salvage. These are the adjustments the
evidence asks for. Each is recorded as a dated addition in
RSE_ARCHITECTURE.md section 13 and none rewrites a frozen section.

1. **WM is a rebuild with a known ancestor.** Crius shows the three-store
   layout works in practice and shows three ways it goes wrong (O-03). WM
   takes the layout and adds the three tests.
2. **The identifiers-only sham joins the developmental control set** (C-04).
   An organism can hide competence in an identifier counter.
3. **Interchange verdicts are reported over a sweep of swap ticks, with the
   declared boundary on the row** (C-03), and every intervention passes a
   control-identity audit before it counts (C-01, C-02).
4. **Phase 3A does not need a distributed queue.** Fabric's lease is taken
   now; its workers cannot run on M1. Campaigns in the first 90 days run
   under a local runner on M1 holding a Fabric lease, with ubu001 and ubu002
   used for clean-clone and cross-host replay (I-01).
5. **Sealed worlds leave the working tree in the first month**, not later
   (W-11 and today's incident).
6. **The first open arm is named**: the Ananke packet-tensor engine (O-09),
   because it alone brings an independent oracle, a second-host record and a
   designed organism that answers the arm's question. It still waits for P1
   to P3.
7. **P6's negative control exists** (O-13). Its positive control does not,
   and the old record gives a reason to doubt it is easy: a fixed-procedure
   learner starting from nothing built no reusable structure in 8 of 8 runs.
   OPEN_QUESTIONS.md carries this.
8. **One vocabulary for controls.** "Cheat control" means a positive control
   in one seat, an impostor in another and a channel test in a third (04
   SURPRISES 12). The kernel uses the five names of REQUIREMENTS 1.3 and
   nothing else.

----------------------------------------------------------------------

## 9. Answer to Q8: what fraction survives

By decision rows (section 1): of 72 rows of scientific machinery, none is
kept as it is; 8 enter after hardening; 36 give up a primitive, and in about
half of those what is taken is the design and its fixtures, not the code; 5
are needs to rebuild; 9 are kept as controls; 10 are retired; 4 are unknown.

By engines: none of the engines continues as an engine.

By size, where the workers reported it:

    LINES scientific (O, W, S, M, C): KEEP 0, HARDEN 24520, EXTRACT 49194, REBUILD 11822, RETIRE 26748, HISTORICAL CONTROL 25415, UNKNOWN 5393, total reported 143092

This overstates what is carried. The largest HARDEN row is the Aphrodite
engine, taken as a negative control. The EXTRACT rows count the whole
package a primitive sits in, and the primitive is usually a few hundred
lines. My estimate of old scientific code that will actually execute inside
Phase 3 is under 10,000 lines, which is under a tenth of what was examined.

So the direct answer: **conceptually, about half of the old scientific
machinery survives, as primitives, designs and fixtures. As running code,
about a tenth. As engines, none.** The infrastructure fares better: a queue
with a lease, a receipt schema, a derived index, a model-call path and the
base role carry forward with stated work.

What survives best is what was written last and used least: the instruments
seats built in September after their own results failed audit. That is the
most useful thing the old program produced, and Phase 3 starts from it.
