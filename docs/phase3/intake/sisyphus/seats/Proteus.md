# Proteus -- forensic dossier

Seat: Proteus (Player Foundry maintainer)
Crawl date: 2026-10-01
Base SHA of worktree: 19299e06b (origin/main at crawl)
Crawler: Sisyphus worker (Opus 5.5), read-only

Coverage statement.
READ: roles/Proteus/RESPONSIBILITIES.md (sections 0-6), TODO.md (A-C), STATUS_2026-09-04_closure.md,
PROTEUS_PROGRAM_REVIEW_PACKET_V0_TO_V0_5.txt (sections 1-5), journal/2026-09-18 (tail), BACKLOG_H0H5.md
(grep); code proteus/foundry/{vm,affordances,grammar (head),generate,probes,signatures}.py,
proteus/graph/{vm,affordances}.py (heads), proteus/round2/falsifier_46.py (walk section),
proteus/round2/PROTEUS-46_FALSIFIER.md, ANATOMY_L0.md (head), proteus/docs/campaign6/
PROTEUS_CAMPAIGN6_AXIS_O_SCOPE.md (sections 0-3), ROUND_2 design (section 0); full git log of
proteus/ and roles/Proteus (86 commits, 2026-09-02 .. 2026-09-18) plus --all since 09-18 (none);
consumer imports of proteus outside proteus/ (git grep); archaeon/campaign6/DECISIONS.md (D6-001..006)
and campaign6 commit log; Harmonia ruling RULING_PROTEUS_CURRENT_INSTRUMENT_AND_R4_2026-09-18.md
(sections 0-1) and M2_QUALIFICATION_TWO_ROUND_CLOSURE_2026-09-04.txt (section 1); comms bodies #735,
#1116, #1129 and the Proteus comms listing; Atlas inference-harvest docs (grep for Proteus) and the
Achilles census registry rows; Artemis D002 RESULT row D002-03q and ENGINE_LENS_CARDS.
NOT READ: the full text of the per-pass review packets V0.3-V0.6 (headline/verdict lines only via the
consolidated program packet and commit messages); proteus/v0_3..v0_6 analysis code beyond file
listing; proteus/integration and proteus/compose code bodies; proteus/eval/* bodies other than
names; journals 2026-09-16/17 in full; the prompt directories (verbatim operator texts). Reason:
budget; these are verdict/support material whose headlines are captured via commit messages and the
consolidated packet. Archaeon campaign code that consumes the VM is described only at the interface
level (it belongs to the Archaeon dossier).

-------------------------------------------------------------------------------------------------
## 1. Identity and purpose

Canonical name: Proteus. Aliases in the record: instance tags Proteus[m2-67f3bd16] (2026-09-16),
Proteus[m2-7d051790] (2026-09-17/18) [HIST]; census alias none (roles/Achilles/census/registry/
seats_part*.json) [HIST].

Origin. Established 2026-09-02 "by James, in the session that parked Diomedes"
(roles/Proteus/RESPONSIBILITIES.md header) [HIST]. The operator of that session had been Diomedes;
RESPONSIBILITIES s5 records what carried over (K0 alphabet-and-entropy rule, headroom-first rule, the
unflattering calibration ledger) and states "Nothing of Diomedes's mandate carries over" [INTENT].
Founding commit 2c121dc0e (2026-09-02, "new seat -- Player Foundry maintainer; V0 brief committed
verbatim and hashed") [HIST]. Authoritative brief: roles/Proteus/PROMPT_PROTEUS_PLAYER_FOUNDRY_V0_
2026-09-02.txt (sha256 cacf303f..., hashed over LF blob) [INTENT].

Original charter (one-sentence contract, RESPONSIBILITIES s1) [INTENT]: "Manufacture enormous numbers
of small, diverse, semantically sterile computational organisms from compact seeded manifests; make
every one of them replayable, lineage-traceable, and resource-metered; never look inside a
qualification world, never tune to one, and never adjudicate whether a survivor is interesting."
Hard rules R1-R9: semantic quarantine (string layer mechanical, ontology layer review-gated);
player/world firewall with a READ_LEDGER; genomes are data; mutation includes subtraction and growth
is not the default (neutrality check); immutable experience; resources a vector not a scalar; the
P=(M,T,C,Pi) lens is not the architecture; anti-wow / no adjudication; "materially different" must be
measured.

Role pivots (reconstructed from git log):
- 2026-09-02 .. 09-03: Foundry build + six preregistered neutrality/equilibrium passes V0..V0.6 on the
  MUTATION KERNEL itself, no world ever touched [HIST].
- 2026-09-03 .. 09-04: "HARMONIA INTEGRATION READINESS" directive (7e17e1e18): "ready the adventurers,
  do not study them further" -- specimen registry, 64-organism frozen menagerie, consumer contract;
  closure packet for A/B/A+B composition identity (6ca171129) [HIST].
- 2026-09-04: seat moves to M2 (SPECTREX5); 2026-09-16 operator rules machine M2 (a1346932e) [HIST].
- 2026-09-05 .. 09-11: supplier to Archaeon H0-H5 (WP-B1 VM as pure library, PR-ID identity fd5927cdd;
  H1 Boolean channel 790fb4803; seed-probe witness-collapse note 5dc8b3e40; TECHNE-12 shrink target)
  [HIST].
- 2026-09-11: base-role adoption (8fb6864cd); D-23 guards on 34 entry points [HIST].
- 2026-09-16 .. 09-17: H1 beta sizing, rule-table MINT (ruling #268), point-release review,
  "Round 2 Representation & Search Geometry" design (901e36d88), repair order s3 (foundry_profile.v1,
  population_manifest.v1), G5 mint of Archaeon's exact C4 starting population (e11e22370, reminted
  0e9fd9cb1) [HIST].
- 2026-09-18: Campaign 6 Axis O -- the seat declares the flat genome + syntactic grammar "retired as a
  SEARCH structure by C4/C5", builds proteus.graph_organism.v1 (348d12816), behavior_fingerprint.v1
  (b3d27cbda), graph handover for executors (3ba52bc20), then its own preregistered falsifier
  PROTEUS-46 kills the motivating claim (eb58691fc prereg, 6a98ef0bb run) [HIST].

Terminal state. Last commit on proteus/ or roles/Proteus: 6a98ef0bb, 2026-09-18 [IMPL: git log --all
since 09-18 returns nothing]. Artemis #1116 / #1129 (2026-09-30) state "Proteus has been inactive since
09-18" [HIST]. Census state marker for the engine: DORMANT (derived from last commit) [HIST]. No
RETIRED/PARKED marker exists in the seat's own files; RESPONSIBILITIES currency 2026-09-16 [IMPL].
Effective status: DORMANT, undeclared.

Relationships [HIST unless marked]:
- Daedalus (SFE engine): Proteus supplies the player side; Daedalus the arena/ledger
  (RESPONSIBILITIES s2). Daedalus's C6 envelope shaped behavior_fingerprint.v1.
- Archaeon: principal CONSUMER. Archaeon campaigns 1-6, WSE, frontier, envgate, rie, lineage,
  z80atlas all import proteus.foundry (git grep: ~60 files under archaeon/) [IMPL]. Proteus minted C4's
  starting population and handed the graph substrate to Archaeon's Deep Frontier (archaeon/campaign6/
  substrate.py imports proteus.graph.handover) [IMPL].
- Vivarium: vivarium/viv/artifacts.py consults proteus.eval.boolean.check for the boolean-components-v1
  artifact and refuses if Proteus is not importable [IMPL]; vivarium/viv/bundle.py follows Proteus #338
  on population manifest shape [IMPL].
- Harmonia: first integration (genesis/harmonia_a/first_integration imports proteus) [IMPL]; Harmonia
  ruled on the V0.5 current instrument 2026-09-18 [HIST].
- Nestor CW01 T-ARCH4 ran on the same VM (roles/Nestor/campaigns/cw01-2026-09-17/experiments/cw01-arch4
  imports proteus) [IMPL]; Techne, Nyx, Odysseus, Artemis dispatch scripts and engine/necropolis also
  import it [IMPL].
- Ludus: CHARTER_v3 s7 names Proteus as organism supplier and Ludus as writer of the world-side binding
  to the Proteus channel ABI; that binding (LUDUS-06) was never written [IMPL: no ludus import anywhere].
- Census disagreement: the Achilles engine registry lists Proteus as a CONSUMER of ludus with evidence
  "roles/Proteus/RESPONSIBILITIES.md:73 (ludus/bench/worlds.py)". That line is a DO-NOT-READ clause
  ("I do not maintain, read for advantage, or modify ... ludus/bench/worlds.py"). The census relation is
  wrong [CORRECTION, verified against source].

Hosts: founded with Machine unassigned; ran on M2 / SPECTREX5 from 2026-09-04 (STATUS_2026-09-04);
operator ruled M2 2026-09-16 [HIST]. Comms/PEW resolved to M1 store [HIST].

-------------------------------------------------------------------------------------------------
## 2. Engine / system inventory

E1. proteus.foundry v0 -- the player VM, generator, mutation grammar [IMPL]
- Paths: proteus/foundry/{vm.py 300 lines, affordances.py 110, grammar.py 400, generate.py 105,
  lineage.py 78, prng.py 83, probes.py 70, signatures.py 58, qualify.py 55, identity.py 56, export.py 80}.
- Purpose: deterministic manufacture of bytecode organisms from a seeded Foundry manifest; replay;
  mutation with lineage records; resource metering.
- Versions: runtime hash 73f110e2 (frozen; Campaign 6 scope header); affordance table
  proteus.affordances.v0 (25 opcodes); grammar versions v0, v0.1, v0.2 (retained executable as FROZEN
  EVIDENCE), v0.3 (zeroing removed, weights renormalised mechanically), v0.4 (half-tape rule removed;
  the active grammar at Campaign 6); profile pfp1:625bc70456ebfa20 [IMPL/HIST].
- Entrypoints: Player(manifest).run_tick(state, inputs, n_out, rng, meter, budget);
  generate.sample_manifest / population; grammar mutate operators; lineage.descend/checkpoint/restore.
- State: manifest (immutable, content-addressed) + state {tape, regs, ip, ticks} [IMPL vm.py].
- Persistence: persist policy in {none, regs, tape, all} controls what survives tick boundaries [IMPL].
- Execution: pure-Python interpreter, single core [IMPL].

E2. Instrument stack of the Foundry (A4/A5 signatures, neutrality and kernel crucibles) [IMPL]
- probes.py: probe ensemble of uniform noise inputs seeded from the review addendum's sha256;
  probe_transcript_equivalence = hash of outputs+status over 4 probes x 3-6 ticks.
- signatures.py: per-class knockout vector (rewrite class to NOP, rerun ensemble).
- proteus/v0 (diversity demo + neutrality gate), v0_3 (13-coordinate neutrality battery, four null
  controls), v0_4 (NC5 joint reversible walk, dual Holm), v0_5 (kernel.py: stationary distribution,
  probability current J, entropy production, Monte-Carlo noise floor; multiplicity.py global family),
  v0_6 (full 2,044-state live kernel, dual kernels K_A/K_B, attribution, cross-runtime replay).

E3. Integration / specimen layer (Harmonia-facing) [IMPL]
- proteus/integration/ (registry.py, menagerie.py, specimen_gate.py, PLAYER_REGISTRY.json, smoke,
  determinism, mint roundtrip), proteus/contracts/ (WORLD_INTERFACE.md, SFE_INTEGRATION.md,
  PEW_EXPORT.md, SPECIMEN_AND_COMPOSITION_IDENTITY.md, RETENTION_AND_MEASUREMENT_V0.md,
  TEMPORAL_PROGRAM_INTERFACE_PROPOSAL.md, schemas). 64-organism frozen menagerie.
- proteus/compose/ (segment/composition identity, exact ablation by NOP substitution, golden vectors,
  meter floor). Deliberately outside foundry/ so runtime_hash is unchanged.
- RETENTION_AND_MEASUREMENT_V0.md is a contract with NO implementation (TODO T3) [IMPL: stated by seat;
  CODE-INFERRED: no reservoir module present in git ls-files].

E4. proteus.eval -- identity, Boolean channel, anatomy, fingerprints, mints [IMPL]
- proteus/eval/: identity.py (PR-ID), boolean.py / boolean_universe.py (H1 Boolean substrate; 4-input
  universe enumerated: 893 of 65,536 tables solvable at size 7, per a1346932e-era commit ae019fb79
  [RESULT-UNVERIFIED]), genome_read.py (D-16), shrink.py + hypothesis_strategy.py (TECHNE-12),
  foundry_profile.py (PROTEUS-29), population_manifest.py (PROTEUS-30), rule_table_identity.py /
  rule_table_mint.py (ruling #268 MINT: hash-chained append-only ledger, four refusals),
  keyed_memory_witness.py (12-instruction keyed memory under the frozen ISA), anatomy.py, fingerprint.py
  (behavior_fingerprint.v1, <= 1 KiB, reward-leak keys refused by schema).
- proteus/round2/: ANATOMY_L0 (structure of Archaeon's C4 specimens), falsifier_46.py.

E5. proteus.graph -- graph_organism.v1 (PROTEUS-43) [IMPL]
- Paths: proteus/graph/{vm.py 342, affordances.py 90, grammar.py 327, generate.py 101, lineage.py 63,
  profile.py 95, handover.py 96, witness.py 148, identity.py 41}; GRAPH_ORGANISM_V1.md;
  GRAPH_PROFILE_CATALOG.json; KEYED_MEMORY_WITNESS_GRAPH.json.
- Genome = nodes (kind, params, persist) + data_edges + control_edges + entry + limits; 25 node kinds
  (v0 semantics minus positional jumps, plus ROUTE, CALL, RETURN); dormant (unreachable) nodes never run
  and cost nothing. Grammar graph_grammar.v1: NODE_ADD/REMOVE/KIND/PARAM, EDGE_ADD/CUT/RETARGET,
  SUBGRAPH_COPY/COPY_ATTACH/MOVE/REMOVE, CROSSOVER_SUBGRAPH, CONFIG_PERTURB; lineage_record.v1 with an
  explicit edit list, "child == parent + edits" asserted by test.
- Runtime hash f850a6ed after handover change, profile pfp1:2595e1aefd59975f (earlier pfp1:3081a8ef...)
  [HIST, 3ba52bc20 message].
- Same world ABI as v0 (run_tick with opaque integer channels) [IMPL vm.py docstring].
- "no world has run it" at build (348d12816) [HIST]; Archaeon then registered it (b334d0949) and its
  frontier digest records "graph fires 100x less" (b5280148c) [HIST].

E6. Scaffolding with no code: retention reservoir (T3), PEW export never exercised against the live
service (T5), temporal-program DELAY interface (PROPOSAL only, a648b99a7) [IMPL: contracts exist,
implementation absent per TODO].

Approximate scale: proteus/ 294 tracked files; foundry+graph core ~2,700 lines Python; test suite
"386 passed / 2 skipped" at 348d12816 [HIST].

-------------------------------------------------------------------------------------------------
## 3. Architecture

World. Proteus has no world. By charter it never reads one (R2 firewall; READ_LEDGER.md). The only
world-like thing it owns is the probe ensemble: 4 probes, 1-3 input channels, 1-3 output channels,
3-6 ticks, 0-3 uniform 32-bit values per channel per tick, budget cap 256 ops/tick (DEFAULT_ENSEMBLE in
proteus/foundry/probes.py) [IMPL]. It is explicitly "noise with a declared shape" with "no task"
[IMPL docstring]. Worlds that ran Proteus organisms (W0..W7, envgate, C6 composed worlds) are Archaeon's.

Organism (v0) [IMPL vm.py, affordances.py]:
- Genotype: list of 32-bit words; instruction = 4 words (op, a, b, c); op = word mod 25, so EVERY word
  sequence is a legal program ("the interpreter is total"). a, b register indices mod n_regs; c either a
  register index or a signed immediate/offset.
- Manifest: {schema_version, n_regs 2..16, tape_words 16..4096 (mult. of 4), genome 4..4096 words,
  code_writable bool, persist in {none,regs,tape,all}, tick_budget 8..65536, out_cap 1..256}.
- Phenotype: execution of the genome copied to the FRONT OF THE TAPE (single address space). If
  code_writable, ST can overwrite the genome region: self-modification is possible.
- Memory: registers (<= 16) + tape (<= 4096 words), LD/ST register-indirect; persistence policy.
- Control flow: JMP/JZ/JNZ with immediate offsets in units of instructions (positional); HALT (ip -> 0),
  YIELD (resume next tick). No indirect jump, no call/return in v0.
- I/O: IN/INQ read opaque integer input channels (cursor per tick); OUT appends to an output channel
  (dropped beyond out_cap); RND reads an externally supplied SplitMix64 stream.
- Compute model: op budget per tick; status in {halt, yield, budget}.
- Meter: ops, ops_by_category, code_region_writes, branches_taken, in_reads, out_writes, out_dropped,
  rnd_draws, wall_s, cpu_s, ticks, budget_exhausted_ticks; declared proxies for "search expenditure"
  (= branches) and "adaptation expenditure" (= code-region writes). No fitness field.

Design-vs-implementation disagreements:
- affordances.py docstring says the LDC immediate is operand c; vm.py reads it from slot b (op 3:
  regs[a] = bw). TABLE row is right, prose wrong; not fixable without changing runtime_hash because the
  hash covers the file (STATUS_2026-09-04, TODO T9) [CORRECTION, verified: vm.py line "regs[a] = bw &
  MASK32"].
- organism_id hashes the manifest only and pins BYTES not EXECUTION: a 25 -> 26 opcode amendment
  re-decodes 94.87% of instructions with organism_id unchanged; the replayable identity is the triple
  (organism_id, runtime_hash, affordance_hash) (STATUS_2026-09-04) [RESULT-UNVERIFIED, mechanism
  CODE-INFERRED from op = word mod N_OPCODES].
- RESPONSIBILITIES R1 asks for a "costed random draw, a cost query"; amendment A2 removed the cost
  opcode ("randomness does not intrinsically know its cost") [IMPL affordances docstring].

Mutation/search operators (v0.4) [IMPL grammar.py]: 12 syntactic operators with frozen weights:
insertion, deletion, duplication, movement, replacement, operand_perturbation, reference_redirection,
region_swap, splice (needs a mate; self if none), randomization, unreachable_removal (approximate),
config_perturbation. Zeroing was removed in v0.3 (weights divided by 0.96 mechanically, code asserts).
Operators act on aligned instruction BLOCKS of k in [1,4] -- positions, not parts (C6 scope s0).

Selection/admission. None inside Proteus by charter (R8). Selection was done by consumers (Archaeon
campaigns, CW01, Deep Frontier). Proteus's own "admission" machinery is quarantine audit (string
scan, allowlisted imports), qualification of the diversity instrument (qualify.py), specimen_gate.py
(registry identity), and the MINT refusals for derived rule tables [IMPL].

Reproduction/lineage. lineage.descend applies a grammar operator and writes lineage_record.v0
(operators + seeds + pre/post hashes; replayable, not diffable); graph lineage_record.v1 adds an edit
list [IMPL]. Recombination: splice (v0), CROSSOVER_SUBGRAPH (graph; attaches DORMANT, so 100% neutral
by construction per PROTEUS-46 table) [IMPL + RESULT].

Learning/adaptation: none within a lifetime beyond self-modifying code and persistent tape/regs. No
communication primitive between organisms other than whatever a world routes through channels.

Provenance/identity: runtime_hash, affordance_hash, grammar hash, foundry_profile (pfp1:...),
population_manifest.v1 (declaration_canonical_digest bound beside raw-byte digest after G5 remint),
PR-ID across families, audit identity (AUDIT_IDENTITY.json, tree digest 3ae4ee8b773e0fcf "FRESH")
[IMPL/HIST]. eol=lf pinned so hashes reproduce across CRLF checkouts (b2ec2d1aa) [HIST].

Experimental control structure: every pass froze a preregistration in its own commit before any run
(e.g. d22df6480 "FROZEN BEFORE THE PRODUCTION RUN"; eb58691fc "committed BEFORE any child is
generated") [HIST, verifiable by commit order]. Failed runs preserved under their own identity
(NEUTRALITY_RESULT_grammar_v0_FAIL.json, _v0_1_FAIL, _v0_2_FAIL, RESULT_FULL_n12000_GATE_FAIL.json)
[IMPL: files exist].

-------------------------------------------------------------------------------------------------
## 4. World capability audit

Proteus owns no world (by design). What it owns:
- Probe ensemble: 4 noise probes, <= 3 channels, <= 6 ticks, <= 3 values/channel/tick, 256 ops/tick.
  Nonspatial, stochastic only via the supplied RND stream, no reward, no adversary, no ecology, no
  environmental change, no delayed consequence beyond tick persistence. Effectively a fixed, tiny,
  memorisable fingerprinting harness [IMPL]. It is not a toy world in the pejorative sense; it was never
  meant to be a world. Its LIMITATION as an observable is measured: on 2-instruction segment players
  it resolves 3 classes / 87.5% in one class; 52/56 players emit nothing (TODO T1) [RESULT-UNVERIFIED];
  in Harmonia's M2 qualification the transcript was CONSTANT across five structurally distinct
  conditions including a full ablation (M2_QUALIFICATION_TWO_ROUND_CLOSURE s1) [HIST].
- The mutation kernel as a "world": V0.5/V0.6 treat the structural state space of the grammar (124
  enumerated states; then the full 2,044 valid structural states) as a Markov chain. This is a closed,
  exhaustively enumerable space over (genome_length, tape_words, ...) coordinates [IMPL/HIST].
- The keyed-memory witness and Boolean universe are hand-written tasks used as expressiveness
  witnesses, not worlds.
Worlds consuming Proteus organisms are Archaeon's W0..W7 and C6 composed worlds (bins 0-10, resources,
locality, hidden state, hazards, coupling per 1fd96a5cd) [HIST, belongs to Archaeon dossier].

-------------------------------------------------------------------------------------------------
## 5. Organism capability audit

v0 organism [IMPL, grounded in vm.py/affordances.py]:
- Instruction set: 25 ops in 9 classes (halt/yield+NOP, read/write, indirection, arithmetic, logical,
  comparison, control, opaque I/O, randomness). Turing-complete in the bounded sense (conditional
  branch + indirect memory + arithmetic) within tape <= 4096 words and <= 65,536 ops/tick.
- Writable memory: tape (<= 4096 words), registers (<= 16); code region writable when code_writable.
- Recurrent state: persist in {regs, tape, all} carries state across ticks; a tick can YIELD and resume.
- Sensors/actuators: integer input channels (IN, INQ) and output channels (OUT); semantics entirely
  supplied by the world.
- Self-modification: yes (code_writable). Reproduction: not an organism capability -- reproduction is
  external (grammar applied by a consumer). No self-copy instruction; an organism cannot emit a child.
- Learning/adaptation: only via self-modifying code or stored tape; no gradient, no plasticity rule.
- Planning/internal simulation/abstraction: nothing prevents a program from implementing them, but no
  primitive supports them and the search operators do not compose parts.
- Cross-task reuse: v0 has no callable unit (no indirect jump, no return). Reuse is copy-by-position.
- Expressiveness witness: a keyed two-value memory is a 12-instruction program at 9 ops/tick in the
  frozen ISA, with negative and cheat controls (point-release review, 20bd3cfdc) [RESULT-UNVERIFIED].
  H1: the existing channel expresses all 3-input Boolean tasks, verified exhaustively against an
  independent oracle (790fb4803) [RESULT-UNVERIFIED].

Graph organism (v1) adds: ROUTE (predicate-selected control port), CALL/RETURN with bounded stack
(call_depth_max), per-node persist, dormant structure as first-class, connectivity-level mutation.

Fighting chance? Architecturally the v0 VM CAN express nontrivial programs (memory, branching,
indirection, persistence, self-modification). The binding constraint documented across Archaeon C4/C5
and Proteus's own PROTEUS-46 is REACHABILITY under the syntactic grammar, not expressiveness:
"0/5,472 single edits improved a parent"; "in most cells the elite IS the starting parent after 36,000
evaluations" (C6 scope s0 summarising C4/C5) [HIST, belongs to Archaeon; quoted by Proteus]. On the
one task where Proteus tested the graph substrate (one_value 3/6 -> two_key 6/6), neither grammar
produced a USEFUL single edit (0/4,267 v0.4; 0/4,881 graph) [RESULT-UNVERIFIED]. So: a realistic
chance of EXPRESSING small reasoning-like programs exists; a realistic chance of REACHING them by the
frozen search operators, in the worlds tried, was measured as very low. Whether the reachability
failure is a property of the landscape or of the search rule is contested (section 9, T3).

-------------------------------------------------------------------------------------------------
## 6. Search and pressure mechanism

Novelty production inside Proteus: (a) uniform-random genome words from a seeded generator (the
generator "holds NO opinion about which opcodes or operands are common"; the only bias is
op = word mod 25 over uniform words) [IMPL generate.py]; (b) the 12-operator syntactic grammar; (c) the
graph grammar. No selection, no fitness, no curriculum, no ecological pressure inside Proteus (R8).

Pressure is applied by consumers. Proteus's distinctive contribution is to characterise the
UNSELECTED mutation kernel as a dynamical object:
- Neutrality gate (R4): expected genome size must not drift up under no selection. Runs 1-3 failed
  (v0, v0.1, v0.2); V0.4's NC5 joint symmetric walk reproduced the same drift numbers with no prior
  ("instructions per generation cohort 8: v0 +0.0707 ... NC5 +0.0408") -> the historic failures were
  boundary geometry, not a grammar prior [RESULT-UNVERIFIED, program packet s3.1].
- Equilibrium analysis: the kernel is non-reversible; 166 of 506 connected pairs carry current above
  the MC noise floor; 165 attributed to OPERATOR_WEIGHTING [RESULT-UNVERIFIED]. V0.6 final: full-space
  kernel reproducibly irreversible; authored weighting sets the MAGNITUDE not the EXISTENCE of the
  current; operational significance NOT YET ADJUDICATED (b819df415) [RESULT-UNVERIFIED].

Bottlenecks and collapse modes named in the record:
- Positional addressing: jump targets are positions, so insertion/movement break routing (C4-04:
  insertion +.215, movement +.193 above pooled effect) [HIST].
- Contiguous-block operators are destructive: in PROTEUS-46, deletion .97, movement .97, region_swap
  .995, splice .91 DESTROYED vs operand_perturbation .354 (v0.4, one_value parent) [IMPL: committed
  result file].
- Dormant-attach graph operators are neutral BY CONSTRUCTION (NODE_ADD, EDGE_ADD, SUBGRAPH_COPY(_ATTACH),
  CROSSOVER_SUBGRAPH: NEUTRAL 1.0000) -- they cannot by themselves change behaviour [IMPL result].
- Selection builds robustness as LENGTH and behavioural neutrality (C4-08: 19 -> 62 instructions)
  [HIST, Archaeon] -- but Atlas F8 / CW01 ruler audit argue count-fixed damage rulers manufacture
  "length protects" (section 9, T4).

-------------------------------------------------------------------------------------------------
## 7. Measurement / ruler stack

Proteus-owned rulers [IMPL unless marked]:
- probe_transcript_equivalence (hash of transcript on 4 noise probes). Known blind spot: degenerate to
  constant on small organisms (T1; Harmonia M2 closure).
- knockout vector over 9 classes (A5). Lower-bound caveat: NOP aliasing (w mod 25 == 0 gives 0/25/50
  as instruction-identical, data-distinct nulls); 342/343 class knockouts clean, 1 confounded
  (STATUS_2026-09-04) [RESULT-UNVERIFIED]; T6 says the bound's width is unmeasured.
- Meter projection: Meter.as_dict() minus wall_s, cpu_s, gpu. Raw meter reproduced on 0/40 identical
  re-runs because of timings; projection 40/40 (TODO T1 amendment, test_meter_observable.py).
  T2 chance floor: 37 ops_by_category classes on 56 players sits EXACTLY on the random-population null
  (median 36, range 27-43); "37 classes ... must never be cited" as population evidence. Discrimination
  over 200 matched pairs: identity 0, inert padding 0, treatment .775, order .49, partner .755,
  independent .99 (TODO T2, RESULT_METER_FLOOR.json) [RESULT-UNVERIFIED].
- Neutrality battery (13 coordinates, V0.3), null controls NC1-NC5 (NC5 = joint reversible manifest
  walk), dual Holm and then a GLOBAL multiplicity family (V0.5: 350 coordinate x cohort cells).
- Kernel current instrument (v0_5/kernel.py): J = pi_i P_ij - pi_j P_ji, two independent samples A/B,
  noise floor = max |J_A - J_B|, entropy production, cycle affinity; reversible reference.
  Harmonia ruling 2026-09-18: ADMITTED AS A DETECTOR, NOT ADMITTED AS AN ABSENCE INSTRUMENT; the
  reversible-reference check "CANNOT FAIL" (detailed balance by algebra; 0.0 on a synthetic kernel
  too); the "occupancy TV 0.019747 vs sampling floor about 0.019" is "NOT A MEASUREMENT: the floor is
  quoted, not computed" [CORRECTION]. Artemis D004-04 (worker, 2026-09-30): MDC 1e-4 flux units below
  the 1.44e-3 residual scale, selection bias INDETERMINATE (<= .004 instructions) [RESULT-UNVERIFIED].
- PROTEUS-46 classes on the two-key probe: USEFUL / GRADED_DOWN / DESTROYED / NEUTRAL / NEUTRAL_DIFF;
  floor from two seed batches; K=400 children per operator; secondary random and greedy 3-step walks
  (proteus/round2/PROTEUS-46_PREREGISTRATION.md) [IMPL].
- behavior_fingerprint.v1 (T0 row; deterministic, no timings, reward-leak keys refused). Recorded blind
  spot: v0 written-address set (b3d27cbda message) [HIST].
- ANATOMY_L0: 24 structural statistics x 20,000-permutation floor, uncorrected; "readers vs W0:
  tick_budget / conditional branch lead, none past 24-way correction" (e11e22370) [RESULT-UNVERIFIED].
Positive/negative controls: present and preregistered in most passes; Harmonia identified one control
(reversible reference) that could not fail. Five regression gates "proven able to fail" in the
pre-T1 hardening pass (a2e69f7bc) [HIST].

-------------------------------------------------------------------------------------------------
## 8. Experiment inventory (campaigns)

C1. V0 Foundry build + neutrality gate runs 1-3 + diversity demonstration
- Date 2026-09-02 (20a523289, b642b9be5, b9c0316fa, fcd471422, 86c7ee1f7, d07bbc52e, 8dff32f4d).
- Question: does the unselected grammar drift genome size (R4)? Is the diversity instrument qualified?
- Organism: v0 foundry populations; world: none (probe ensemble). Pressure: none.
- Arms: grammar v0, v0.1, v0.2; cohorts at start lengths 8/32/128, 60 lineages per cohort.
- Reported: all three neutrality runs FAILED (e.g. run 3: 32 PASS, 8 reflects off minimum, 128 negative
  with CI spanning zero); diversity instrument QUALIFIED (v0.1 rows: 313 classes / 961 vectors).
- Later: V0.4 reclassified the length failures as joint geometry (NC5); v0.2's half-tape rule had
  introduced a REAL tape ratchet removed in V0.4.
- Paths: proteus/v0/NEUTRALITY_RESULT_grammar_v0*_FAIL.json, DIVERSITY_RESULT.json,
  CAMPAIGN_1_PROPOSAL.md (Campaign 1 proposed, NOT launched).
- Label: REPORTED NEGATIVE/NULL (gate) / LATER OVERTURNED (interpretation of the failure).

C2. V0.3 Neutrality crucible -- 2026-09-03 (bf9aeaecd .. c74ed8c1a)
- Change: zeroing operator removed. 13-coordinate battery, NC1-NC4, six probe ensembles, cross-host
  replay on three runtimes.
- Reported: NOT_QUALIFIED_DIRECTIONAL_MUTATION_PRIOR_REMAINS -- "the grammar grows the tape, and the
  prior is the residue of my own previous fix" (the v0.2 half-tape rule).
- Label: REPORTED NEGATIVE/NULL (qualification not achieved), with self-identified defect.

C3. V0.4 Reversibility crucible -- 2026-09-03 (d40e1b279 .. ccc5c8287)
- Change: half-tape rule removed; NC5 joint reversible walk; exhaustive symmetry proof over 2,044 states
  (fitting-shrink blocks 510 -> 0).
- Reported: tape ratchet GONE by proof; historical length failure = JOINT GEOMETRY; one content
  coordinate (halt/yield share at cohort 128, delta -0.0191, z 3.53) fired the preregistered rule ->
  NOT_QUALIFIED.
- Later: V0.5 confirmatory test reversed the sign (delta +0.0118, z 1.90, one-sided p .9716) ->
  V0_4_CONTENT_DISCOVERY_NOT_REPLICATED.
- Label: LATER OVERTURNED (the content discovery); REPORTED POSITIVE (ratchet removal, by proof).

C4. V0.5 Equilibrium and confirmation crucible -- 2026-09-03 (afa792908 .. fe27309f4)
- Zero grammar changes. 124 enumerated structural states x 50,000 mutations/state.
- Reported: 0 of 350 cells survive the global family; structural kernel NONEQUILIBRIUM with authored
  current (166/506 pairs above floor, 165 attributed to operator weighting; sigma 9.97e-3 nats/step);
  "does not move the marginals" (occupancy TV 0.0198 vs ~0.019 floor). Preregistered full-space
  sensitivity arm FAILED its own frozen gate (program packet 6.8).
- Standing candidate deliberately NOT declared: genome_length at cohort 256 vs NC5 negative on both
  seeds (V0.5 -12.80, z 3.55), survives within-cohort, not the global family.
- Later: Harmonia 2026-09-18 -- detector admitted, absence use not admitted; reversible reference
  cannot fail; marginal-TV claim not a measurement [CORRECTION].
- Label: MIXED.

C5. V0.6 Full-space nonequilibrium crucible -- 2026-09-03 (b02d97e4b .. b9128d8f3)
- 2,044-state live kernel; n=12,000 precision gate FAILED by 0.0003 -> target held, n raised to 20,000
  (aafce2bd2); dual kernels K_A/K_B; cross-runtime replay CPython 3.11/3.12 with a negative control.
- Reported: NOT_QUALIFIED_AUTHORED_NONEQUILIBRIUM_CURRENT -- current real, reproducible across kernels
  (<1%), material-edge sign agreement 1.0000; authored weighting controls MAGNITUDE not EXISTENCE; the
  cycle-affinity MAXIMUM declared a winner's curse, not a finding; operational significance NOT YET
  ADJUDICATED.
- Defect carried: `random` in v0_6/equilibrium.py (T8), blast radius pinned to non-adjudicated calls.
- Label: REPORTED POSITIVE (for nonequilibrium current) / INCONCLUSIVE (for consequence).

C6. Harmonia integration readiness + A/B/A+B closure -- 2026-09-03/04 (d5e3d3dbb, 6be6103f1, 6ca171129)
- Specimen registry, 64-organism menagerie, segment players, exact ablation.
- Reported: A+B differed from both parents in 0/200 pairs; attributed to observable degeneracy, NOT to
  composition; "composition adds nothing" named as the most promotable-looking and most wrong
  constraint candidate (X1). Harmonia's M2 run: 1 transcript class among 5 conditions.
- Label: INSTRUMENT FAILURE (by the seat's own reading).

C7. T2 meter chance floor -- 2026-09-05 (c8f848c65)
- Reported: METER_DISCRIMINATES_BEYOND_SIZE; 37 classes = exactly chance; size confound absent
  (padding 0/200); "just use Meter.as_dict()" was a trap (timings).
- Label: REPORTED POSITIVE (for the projection as an instrument).

C8. H0-H5 supplier work -- 2026-09-08 .. 09-17 (fd5927cdd, 790fb4803, 5dc8b3e40, 5eae54618, ae019fb79)
- WP-B1 VM as pure library; H1 Boolean expressiveness exhaustive; witness collapse attributed to the
  SEED PROBES not candidate order (seeded_permutation_v1); shrink target with "a measured disagreement
  with Hypothesis"; 4-input universe enumeration (893/65,536 at size 7).
- Label: UNKNOWN as science (these are instrument/supply deliverables; results unverified here).

C9. Rule-table MINT, foundry_profile/population_manifest, C4 G5 mint -- 2026-09-16 .. 09-18
- Population manifest over Archaeon's exact C4 starting population (57 organisms, digest a3f9816f...);
  G5 remint for checkout-invariance; launch_gate key defect reported (e11e22370, 0e9fd9cb1).
- Label: REPORTED POSITIVE (supply delivered; C4 gate went GREEN after remint, comms #425).

C10. Round 2 / L0 anatomy -- 2026-09-17 (901e36d88, e11e22370)
- Design-only round under operator rule "Do not design organisms to solve W2_K2 or delay tasks";
  amendment A re-sequenced "minimal neutral expressiveness" behind anatomy; L0 anatomy of C4 specimens:
  no statistic past 24-way correction.
- Label: REPORTED NEGATIVE/NULL (anatomy) / design only.

C11. Campaign 6 Axis O -- graph_organism.v1 + PROTEUS-46 -- 2026-09-18
- Question: does a connectivity-level genome remove the C4 "cliff" (no graded intermediate) on the
  one_value (3/6) -> two_key (6/6) step?
- Arms: v0.4 vs graph_grammar.v1; parents one_value and keyed; K=400 children per operator; floor from
  two seed batches; random 3-step walks (200) and greedy 3-step width 50 (100).
- Reported: CLIFF_SURVIVES / FALSIFIER_FAILED, neighbourhood_exhausted False. USEFUL 0/4,267 (v0.4) vs
  0/4,881 (graph); graph DESTROYED .357 vs .705; best two_key seen 3 on both; departures none.
- Consequence: operator ruling -- graph profile stays as a substrate; Deep Frontier's graph
  transformations BLOCKED as formulated with four reopen conditions; frontier suppression PROTEUS-46
  scoped "only the per-operator single-edit neighbourhood of one hand-written witness" (#735).
- Later: Artemis D002-03q (worker quick mode, 2026-09-30): a 5-edit duplicate-and-diverge neutral path
  exists on graph_grammar.v1 (4 NEUTRAL steps at 3/6, then 6/6); the greedy walk never accepts a
  neutral child; population search (pop 50 x 100 gens) never reached 6/6; full drift run timed out.
- Label: MIXED / contested (REPORTED NEGATIVE for the claim as formulated; a later unverified worker
  result shows the search rule could not see a neutral path).

-------------------------------------------------------------------------------------------------
## 9. False-positive / false-negative archaeology

T1. Neutrality failures (V0..V0.2) -> geometry, not prior.
claim: grammar has an upward length prior (runs 1-3 FAIL) -> evidence: marginal drift per cohort ->
challenge: no geometry control existed -> correction: V0.4 NC5 symmetric walk reproduces the drift
(+0.0408 / -0.0159) -> status: HISTORICAL_V0_LENGTH_FAILURE_RECLASSIFIED_AS_JOINT_GEOMETRY. Cost: two
grammar revisions, one of which (v0.2 half-tape) introduced a real tape ratchet [HIST/CORRECTION].
Lesson class: boundary geometry mistaken for a directional prior.

T2. V0.4 halt/yield discovery -> sign reversal.
claim: halt/yield share at cohort 128 differs from length-matched null (z 3.53) -> challenge: did not
replicate across cohorts, absent against second null, no mechanism -> correction: V0.5 frozen
confirmatory test, delta +0.0118, one-sided p .9716 -> status: NOT_REPLICATED, retained in record.
A standing analogous candidate (genome_length @256, z 3.55, two seeds) was deliberately not chased.

T3. "Composition adds nothing" (0/200) -> observable degeneracy.
claim (latent): A+B indistinguishable from parents -> evidence: transcript classes 3 / 87.5% share ->
challenge (self): meter resolves far more -> correction: T2 meter projection discriminates treatment
.775 at size floor 0 -> status: composition question OPEN; Artemis D003-03 (2026-09-30) says "Crucibles
A, D and E never ran" [HIST]. This is a false-NEGATIVE trap the seat caught.

T4. "Use Meter.as_dict()" -> timing noise.
Raw meter reproduced 0/40; projection 40/40. An operator instruction would have made every composition
result noise (TODO T1 amendment) [HIST].

T5. Kernel "control behaves" and "does not move the marginals".
claim (V0.5): reversible reference max |J| 2.17e-19 shows the control works; TV 0.0198 vs floor ~0.019
means marginals unmoved -> challenge: Harmonia 2026-09-18 -- reference cannot fail by algebra; floor
quoted not computed -> status: detector admitted, absence claims not admitted [CORRECTION].

T6. Graph connectivity removes the cliff (PROTEUS-43 motivation) -> PROTEUS-46 FALSIFIER_FAILED ->
contested by search-rule analysis.
claim: connectivity editing makes the one_value -> two_key step graded -> evidence: 0 USEFUL on both
substrates; greedy never above 3/6 -> challenge: (a) operator ruling reframed CLIFF_SURVIVES as
"falsifier failed as formulated", retirement only on exhaustion (eb58691fc) [HIST]; (b) verified in code
here: falsifier_46.py greedy walk initialises best_key = (cur, 0) and scores children key =
(two_key, -ops); a NEUTRAL child (same two_key, ops > 0) has key (cur, -ops) < (cur, 0) and is never
accepted, so the greedy walk cannot traverse a neutral plateau [IMPL, verified]; (c) Artemis D002-03q
finds a 5-edit neutral path [RESULT-UNVERIFIED] -> status: the suppression is still in force (frontier
logged 299,991 BLOCKED rows of ONE decision, #735) [HIST]. Classification: the greedy walk could not
detect a path that requires >= 1 neutral step; the walk length (3) was shorter than the reported path
(5). The USEFUL-share primary statistic is unaffected by this (single-edit). This is a candidate
false-negative regime, not an overturn: population search also failed to reach 6/6.

T7. C4 "cliff" and "length protects" (VM-level, Archaeon-owned but on the Proteus VM).
Atlas F8 (ATLAS_CROSS_ENGINE_SYNTHESIS s1): CW01's Bernoulli(f) ruler audit made 4/7 fixed-count damage
claims disappear and 2 shrink; "the Campaign-4 'cliff', which PROTEUS-46, HEPH-32, FP-003 and the
299,991-echo suppression all build on, was measured with a count ruler and a greedy tie-rejecting walk"
-- "The cliff has never been re-read" [HIST, Atlas; partially verified: the greedy tie-rejection is
verified for PROTEUS-46 (T6); the C4 ruler was not inspected here].

T8. organism_id pins bytes not execution.
A silent identity hazard found and recorded; replayable identity redefined as a triple (STATUS 09-04)
[HIST].

Recurrent confound classes on this seat: boundary geometry vs prior; observable degeneracy read as
absence; timing in identity observables; controls that cannot fail; search rules that reject neutral
moves; single-witness scope extrapolated into a frontier-wide suppression.

-------------------------------------------------------------------------------------------------
## 10. Research outputs

- roles/Proteus/PROTEUS_PROGRAM_REVIEW_PACKET_V0_TO_V0_5.txt -- consolidated arc, instrument failure
  ledger (s6), four decisions owed to external review.
- roles/Proteus/PROTEUS_V0_3/V0_4/V0_5 *_REVIEW_PACKET.txt, PROTEUS_V0_6_INTERIM_PREREGISTRATION,
  INTERIM_2_GATES_CLEARED, FINAL_EXTERNAL_REVIEW_PACKET.txt -- per-pass packets.
- roles/Proteus/REVIEW_PACKET_PROTEUS_V0_BRIEF_2026-09-02.txt, ..._POSTBUILD_... -- V0 build.
- roles/Proteus/ADDENDUM_EXTERNAL_REVIEW_V0_2026-09-02.txt -- nine amendments A1-A9 (verbatim, hashed).
- roles/Proteus/PROTEUS_CLOSURE_PACKET_2026-09-04.txt (828 lines, 16 sections) + STATUS_2026-09-04.
- roles/Proteus/PROTEUS_HARMONIA_INTEGRATION_READINESS_REVIEW_PACKET.txt, PROTEUS_PRE_T1_HARDENING_
  REVIEW_PACKET.txt, HARMONIA_HANDOFF.md, CONSUMER_SURFACE_V0_6.md.
- roles/Proteus/NOTE_WITNESS_CASE_COLLAPSE_2026-09-10.md.
- proteus/ARCHITECTURE.md, proteus/MUTATION_GRAMMAR.md, proteus/contracts/*.md.
- proteus/docs/point_release_2026-09/PROTEUS_POINT_RELEASE_REVIEW.md (expressiveness not frontier).
- proteus/docs/round2/ROUND_2_REPRESENTATION_AND_SEARCH_GEOMETRY.md (design + three amendments).
- proteus/docs/campaign6/PROTEUS_CAMPAIGN6_AXIS_O_SCOPE.md (requirement table v0 vs graph).
- proteus/graph/GRAPH_ORGANISM_V1.md; proteus/round2/PROTEUS-46_PREREGISTRATION.md, _FALSIFIER.md,
  ANATOMY_L0.md; proteus/eval/BOOLEAN_UNIVERSE_TABLE.md.
- External/cross-seat: roles/Harmonia/rulings/RULING_PROTEUS_CURRENT_INSTRUMENT_AND_R4_2026-09-18.md;
  archaeon/frontier/suppressions/PROTEUS-46.json; roles/Artemis/dispatch/D002/RESULT.md (D002-03q),
  D004/RESULT.md (MDC); Atlas ATLAS_CONTRADICTIONS_AND_NATURAL_EXPERIMENTS.md A7, A12, A15.

-------------------------------------------------------------------------------------------------
## 11. Journals, TODOs, pivots, abandoned branches

- journal/ covers only 2026-09-16, 09-17, 09-18 (earlier passes recorded as STATUS_*.md files).
- TODO.md (last full update 09-04; mapped to BACKLOG_H0H5 rows 09-16): A (T1 degenerate surface, T2
  CLOSED), B (T3 retention unimplemented, T4 not in portfolio monitor EXPECTED_AGENTS, T5 PEW export
  never exercised, T6 alias bound width, T7 neutrality hard gate NOT passed since 09-02, T8 `random`),
  C (two changes bundled that force a runtime transition: e.g. T9 LDC docstring), E (not to start
  without a directive).
- BACKLOG_H0H5.md: PROTEUS-01..48 (42-48 added for Campaign 6); PROTEUS-46 ran; others in 42-48 not
  run by 09-18 [HIST from journal tail].
- Pivots and why: (1) neutrality qualification -> integration readiness (operator: "ready the
  adventurers, do not study them further", 09-03); (2) substrate-science -> supplier for Archaeon H0-H5
  and campaigns (09-05 onward); (3) "organism expressiveness is not the frontier constraint" (09-17
  point release) -> Round 2 representation/search geometry (operator 09-17) -> Campaign 6 graph
  organism (operator directive 09-18, following C5 closure "the failure has moved upstream").
- Abandoned/superseded: grammar v0/v0.1/v0.2 (retained executable as frozen evidence), zeroing
  operator, half-tape rule, Campaign 1 proposal (proteus/v0/CAMPAIGN_1_PROPOSAL.md; never launched),
  Archaeon's "Representation G" withdrawn in favour of Proteus graph (D6-004), Representation B
  adopted "as an instrument, not a VM".
- No unmerged proteus/* branch on origin (git branch -r) [IMPL].
- Unflattering self-calibration: journal 09-18: "The seat proposed this profile eleven hours ago and
  its own preregistered test killed the motivating claim" [HIST].

-------------------------------------------------------------------------------------------------
## 12. Lens inventory

L-P1. Mutation-kernel thermodynamics lens (v0_5/v0_6 kernel instrument)
- Substrate: the grammar's Markov kernel over enumerated structural states (124; 2,044 full space).
- Organisms: unselected genomes; world: none; pressure: none (the point is the null).
- Phenomenon family: authored directionality in variation operators; nonequilibrium current;
  whether the search operator itself carries a "ladder".
- Resolving mechanism: exhaustive state enumeration, sampled transition probabilities, J, sigma,
  cycle affinities, dual kernels, attribution by operator.
- Resolution ceiling: MDC ~1e-4 flux units (Artemis worker); Harmonia: no absence threshold X yet.
- Noise: MC sampling (floor = max |J_A - J_B|), winner's curse on maxima, `random` in equilibrium.py.
- Limitation: state space is structural coordinates only (length, tape, config), not content; the
  consequence for selection is unadjudicated (bias <= .004 instructions per Artemis).
- Reusable: the method (enumerate kernel, measure current, attribute to operators) is substrate-agnostic.
- Toy-grade: the coordinate space; Unknown: whether current matters under any selection regime.

L-P2. Single-edit landscape / mutational neighbourhood lens (PROTEUS-46 harness, anatomy, knockouts)
- Substrate: v0.4 and graph genomes around hand-written witnesses; ruler: two-key probe classes.
- Phenomenon: gradedness vs cliffs in genotype-phenotype maps; neutrality; operator-specific damage.
- Mechanism: K children per operator classified against a seed-batch floor; walks.
- Ceiling: single-edit scope; 3-step walks; greedy rule cannot cross neutral plateaus (verified).
- Noise: count-based damage rulers (Atlas F8), witness choice (one hand-written parent per arm).
- Reusable: per-operator class tables, edit-list lineage, dual-substrate comparison design.
- Toy-grade: the task (one_value 3/6 vs two_key 6/6) and n=1 witness per substrate.

L-P3. Observable-adequacy lens (transcript vs meter vs fingerprint)
- Phenomenon: whether an observable can distinguish organisms at all; chance floors for class counts.
- Mechanism: matched-pair discrimination rates with identity, padding and independent ceilings.
- Reusable: the T2 design (identity / size floor / treatment / order / partner / independent) is a
  general recipe for qualifying any behavioural observable.
- Limitation: the probe ensemble is noise of tiny size; behavioural signal depends on worlds Proteus
  never owns.

L-P4. Substrate-supply lens (v0 VM and graph VM as shared organism substrates)
- What exists: a total, deterministic, replayable, hashed bytecode VM used by Archaeon C1-C6, CW01,
  Deep Frontier, Vivarium artifacts; a graph VM with dormant structure and edit-list lineage.
- Ceiling: pure-Python single core (C6 measured science 0.1 s vs SFE row 95-193 s, i.e. the VM was not
  the bottleneck -- Artemis ENGINE_LENS_CARDS [HIST]); tape <= 4096 words.
- Limitation: v0 positional addressing; no callable units; graph runtime has never been the substrate of
  a completed campaign result beyond Deep Frontier's early readouts ("graph fires 100x less").
- Unknown: whether graph organisms change reachability under population search with neutral drift.

-------------------------------------------------------------------------------------------------
## Open questions / unknowns

- Did any consumer ever measure behaviour of graph organisms under a full selection run after 09-18?
  Deep Frontier digests mention graph firings; not inspected here [UNKNOWN].
- The full D002-03 neutral-drift run (500 walks x 3000 steps) timed out; whether long neutral drift
  reaches 6/6 at a rate beating the control is UNKNOWN.
- The 893/65,536 Boolean table count and the keyed-memory witness were not re-derived here.
- Whether the C4 "cliff" survives a Bernoulli(f) damage ruler (Atlas frontier item 1) is UNKNOWN; the
  dependency chain (C4 cliff -> PROTEUS-46 premise -> frontier suppression) has not been re-read.
- Retention reservoir (T3) and PEW export (T5) have no implementation; any citation of them as running
  mechanisms is unsupported.
- Seat status is undeclared: DORMANT by activity, with no RETIRED/PARKED marker in roles/Proteus.
- T7 (neutrality hard gate) has never passed; the program nevertheless built campaigns on grammar
  v0.4. Whether that matters quantitatively is the unadjudicated "operational significance" of V0.6.
