# Bellerophon backlog (schema: roles/Archaeon/prompts/2026-09-10_backlog/00_BACKLOG_SCHEMA.md)

Currency: 2026-09-18 (rewritten to the schema on the day the role landed;
supersedes the 8-item provisional file of the morning pass). 24 items.
"builder" in the blocked_on column means the item is a build this seat
designs and another seat (or an operator-assigned amalgamation session)
executes; the seat's own artifact for such an item is the SPEC, and the
item stays open until the build lands.

BELL-01 | Commit directive 3 as the charter text (done 2026-09-18: prompts/2026-09-18_charter/ with MANIFEST) and keep RESPONSIBILITIES.md current against it | ENGINE | program | S | none | MANIFEST.md verifying; RESPONSIBILITIES.md s1 one-sentence contract
BELL-02 | Write the ABI diff table: primordial contract.World/Brain/Genome vs wforge vs campaign6 worlds/runtime vs proteus handover vs sfe.executors, per method, with adapter cost in lines | TOOLS | program | S | none | roles/Bellerophon/ABI_DIFF.md, every row cites a path and line
BELL-03 | Freeze contracts v0.1 as code: runtime_checkable Protocols + JSON schemas for World, Candidate, Pressure, Observer, Transform, Selector, Control, Experiment, Receipt | TOOLS | program | M | D-BELL-1 (package location) | contracts/*.py + schemas/*.json + a test that every reference impl named in design s2 satisfies its Protocol
BELL-04 | Specify the registry row schema and the admission predicate as a pure function over committed files (design s5 items 1-7) | TOOLS | program | S | BELL-03 | admission/SPEC.md + admission/predicate.py stub with the seven checks named and a fixture that fails each one
BELL-05 | Design the first home-written world, World.Cellular (integer CA, numba, trace hash, BIT), as a spec with oracle episodes and the three controls | TOOLS | program | S | BELL-03 | specs/world_cellular.md + oracle fixture (seed list, expected hashes computed by a 30-line pure-Python reference)
BELL-06 | Design Candidate.StateMachine (Mealy over integer alphabets) with descent operators and cost() | TOOLS | program | S | BELL-03 | specs/candidate_statemachine.md + reference hashes
BELL-07 | Design Pressure-as-World-transformer with probe() and cheat(); first three: Delay, Charge, RegimeSwitch as wrappers reproducing NPE B1 semantics bit-for-bit over wforge | TOOLS | program | M | BELL-03 | specs/pressure_wrappers.md + the F2 falsification fixture (probe must fail only for "does not bind")
BELL-08 | Design World.TapeSoup (BFF) with the emergence-rate positive control (paper: 40% of runs by 16k epochs) and the copy-op-removed cheat control | TOOLS | program | M | Techne bff-reference packet (held, D-BELL-4) | specs/world_tapesoup.md + control definitions; the body is Techne's
BELL-09 | Design World.Physics2D over Box2D v3: quantised readout, SEMANTIC repro, tolerance derivation, throughput protocol | TOOLS | program | M | D-BELL-3 + Techne box2d-v3 packet (held) | specs/world_physics2d.md with the tolerance derivation written BEFORE any binding runs
BELL-10 | Design the Receipt schema merging sfe.ExecutorResult and NPE validate_receipt (engineering/science disjoint, manifests of every slot, repro achieved, host, build hashes) | TOOLS | program | S | BELL-03 | schemas/receipt.json + a fixture receipt from each ecosystem that validates
BELL-11 | Design experiments.sweep/perturb/transfer/replay semantics, including the mandatory scratch+sham arms for transfer and the eligibility count before dispatch | TOOLS | program | M | BELL-03 | specs/experiment_grammar.md with one worked example per verb
BELL-12 | Design compile("sfe"): Experiment -> archaeon/frontier spec with declared capabilities and a Vivarium-evaluable outcome rule | TOOLS | program | M | BELL-11; Archaeon's specs.py as the target | specs/compile_sfe.md + one example spec that archaeon/frontier's validator accepts (validator run read-only)
BELL-13 | Design compile("npe"): Experiment -> NPE bus job(s) with the one-line hypothesis and lane routing | TOOLS | program | M | BELL-11; D-BELL-2 (NPE on main) | specs/compile_npe.md + one example job envelope validating under primordial/fabric/envelope.py
BELL-14 | The F1 test: one CA-world sweep compiled to both backends; specs must differ only in transport | TOOLS | program | S | BELL-12, BELL-13, builder | a committed pair of specs + a diff showing transport-only differences, or F1 recorded as HOLDS
BELL-15 | Design Observer.QD and Observer.Transcript wrappers; novelty-of-structure / -of-behaviour / -to-observer kept as separate manifest fields (operator, POET/ASAL directive) | TOOLS | program | S | BELL-03 | specs/observers.md
BELL-16 | The F2 test: one Pressure wrapped over wforge, Cellular and Graph worlds; probe() outcomes tabulated with reasons | TOOLS | program | S | BELL-07, builder | rows + verdict on F2
BELL-17 | Design Transform.* (relabel, permute channels, add irrelevant edges, corrupt, time-warp) with inverse() where it exists | TOOLS | program | S | BELL-03 | specs/transforms.md
BELL-18 | Design Selector wrappers: primordial/qd MAP-Elites as the reference; pyribs CMA-ME as the second implementation; archive-as-rows requirement | TOOLS | program | S | BELL-03; Techne pyribs packet (held) | specs/selectors.md
BELL-19 | Design Evaluator slot: numba_fused (NPE B6) reference, warp oracle-gated, llvm_genome as an EXPERIMENT with its crossover protocol | TOOLS | program | M | BELL-03 | specs/evaluators.md with the llvm-vs-fused preregistration text
BELL-20 | Milestone: Archaeon writes one experiment against the toolbox without reading any implementation, and its receipt validates | ENGINE | program | L | BELL-03..14 built | the receipt path, cited by Archaeon, and this seat's review packet
BELL-21 | Operator decision D-BELL-1: package location and name (proposal: prometheus/toolbox/) | ENGINE | program | XL | NEW: D-BELL-1 | a line in archaeon/docs/expansion/DECISIONS.md or the operator's word committed verbatim
BELL-22 | Operator decision D-BELL-2: NPE (primordial/) lands on main, or the NPE adapter is built on Nestor's branch | ENGINE | program | XL | NEW: D-BELL-2; Nestor | the decision recorded; if "on main", a prompt to Nestor drafted
BELL-23 | Operator decision D-BELL-3: gcc in WSL on M2 for native builds, or the Linux host | ENGINE | program | XL | NEW: D-BELL-3 | the decision recorded
BELL-24 | Operator decision D-BELL-4: release the drafted Techne/Nyx prompts now or after directive 4's ten-verdict bar | ENGINE | program | XL | NEW: D-BELL-4 | the decision recorded; prompts posted with receipts, or left held with the date
