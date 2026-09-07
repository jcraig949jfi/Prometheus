# Work packages — amended 2026-09-07 (later) per the operator's amendment order

Annex to `archaeon/docs/ROADMAP.md` §D. Graph in `GRAPH.md`. **28 packages**
(the first delivery summary said 29; the table then and now enumerates 28 —
0a–0f, X1 X2 X5 X6 X7 X8, A1–A4, B1–B4, C1–C4, P0–P3. The count was a
miscount, not an omitted package.)

For every ID: primary owner and handoffs; **true dependency** (executable /
comparison / qualification — never a universal gate); suggested tests
(failure modes to cover, not a quota); acceptance artifact; **claim
boundary** (what completion does and does not license); reopening condition.
Cost: S under a day, M a few days, L longer. Compute is host CPU.

Status legend: DONE (commit) · IN LANE (Archaeon, not started) · OWNER (filed
to its owner) · CONDITIONAL (waits on a named result).

---

## Integrity (local gates; each gates only what depends on it)

### WP-0a · Refuse invalid bitstring lengths · **Daedalus**
- Dependency: none. Gates execution of affected candidates, not library work.
- Tests: 0a-a shorter/longer refused, exact length scores as before; 0a-b invalid length/type/alphabet fail clearly, no ordinary observation emitted; 0a-c Herakles's F-1 table now exercises refusal; sealed fixtures keep result and identity. Docstring: root vs derived per-repeat seed.
- Acceptance: regression test + owner-run example closing the silent lowered-ceiling path.
- Claim boundary: an integrity repair; licenses nothing scientific.
- Status: OWNER (`roles/Daedalus/INBOX_…EXPANSION_ROADMAP…` amended).

### WP-0b · Degeneracy reporting under reset · **Vivarium**
- Dependency: none. Gates degeneracy *reporting* for stateful kinds.
- Tests: 0b-a deterministic stateful walk, reset + constant seed → degenerate-by-construction, identical replay; 0b-b persist / changing seeds follow declared behaviour, never auto-marked constant; 0b-c a constant score across different trajectories is not by itself structural degeneracy.
- Acceptance: the reported defect reproduced and fixed without flattening internal dynamics or confusing empirical variance with construction guarantees.
- Claim boundary: a kind's cross-execution `stateful` flag says nothing about state inside one execution (CA lattice, VM tape).
- Status: OWNER.

### WP-0c · One arm value through both seals · **Vivarium** (Daedalus: `sfclient.family_member(arm=)`, read contracts)
- Dependency: engine revision with `family_members.arm` (live, `642736763`). Gates M-ELIGIBLE's arm legibility only.
- Tests: 0c-a identical execution inputs under labels A/B keep one execution hash while member bindings record different arms; 0c-b queue arm = sealed member arm = audit envelope = PEW design arm; omitted/conflicting arms fail at the boundary; 0c-c reassignment after commitment refused, identical re-add idempotent; 0c-d design commitment precedes execution/outcome events and is traversable through typed references, not manifest prose.
- Acceptance: one complete arm-bound round trip with readback and ordering evidence.
- Claim boundary: same-hash applies only when execution inputs are identical; changing execution parameters still changes identity.
- Status: OWNER.

### WP-0d · D3 reconciled; campaign statistics corrected · **Archaeon** (Harmonia: scoped ruling)
- Dependency: none. Gates claims using D3 (M-SIGNAL false-discovery figures), not family development.
- Tests: 0d-a exact F-tail + seeded simulation reproduce 0.106; 0d-b denominators, zero-variance neighbourhoods, overlap reported; 0d-c exact enumeration mean ½ var 1/(4L), 1/96 vs 1/112; 0d-d plan assignments = metadata; sealed hashes unchanged.
- Acceptance: `archaeon/docs/D3_NULL_RECONCILIATION.md` + `d3_null_reconciliation.json`; `campaign.check()["levels"]` v2 (deterministic enumeration at WORLD; mean-null with unequal variances).
- Claim boundary: explains the number; D3 stays admitted for region discrimination on a frozen corpus; a Gaussian null approximates a Binomial one at n = 8.
- Status: **DONE** (this commit). Reopen: Harmonia's ruling; binomial-null calibration at the family's L under a frozen design.

### WP-0e · Kind-generic builder · **Archaeon** (Vivarium: WP-0f result schema supersedes the local copy)
- Dependency: none for bitstring/walk (local declared result fields); WP-0f for new kinds' field validation.
- Tests: 0e-a bitstring and fixed-scale walk build through real contracts; a third fixture kind exercises the generic path; 0e-b missing kind, destroyed value, unsupported sampler, wrong scalar type, vector-valued outcome field → specific failures before queueing; 0e-c incoherent bits/length rejected, unrelated axes independent; 0e-d fixed-seed replay, nothing defaulted, legacy sealed spec keeps its hash.
- Acceptance: `archaeon/producer/kindspec.py`; `falsification_walk.v1` (Archaeon's separately proposed design, `step_scale` fixed; **not** a repair of v0, whose nulls stay null) is runnable+drawable+buildable; `check()` reports all three; the tick builds through the drawn template.
- Claim boundary: buildable ≠ admitted ≠ eligible; no scientific conclusion.
- Status: **DONE** (this commit).

### WP-0f · Result schemas and thin wrappers · **Vivarium** (Daedalus A1, Herakles C1, Proteus B1; Archaeon 0e consumes)
- Dependency: none. Gates template field validation for new kinds.
- Tests: 0f-a unknown fields, wrong types, missing required outputs, non-finite scores, unsupported vector reductions → specific diagnostics; 0f-b library and wrapper results match on shared fixtures (errors, seeds, witness ordering, state init); 0f-c declared witness/trace bounds respected with explicit truncation metadata; `cli kinds` exposes the same contract validation uses.
- Acceptance: `Kind.result_schema`; malformed executor output cannot masquerade as a valid observation.
- Claim boundary: A/B/C kinds are stateless *across* executions while modelling state *within* one.
- Status: OWNER.

## Cross-cutting

### WP-X1 · Analysis-family convention · **Harmonia** (Archaeon: first analysis; Daedalus: nothing)
- Dependency: none for the convention; a read scope for a production analysis (fixtures until then).
- Tests: X1-a worked analysis resolves exact sources and reproduces; X1-b duplicates, missing sources, mixed measurements, wrong unit detected, never pooled; X1-c replacing a source or version changes the derived identity; originals unchanged; X1-d repeats from one world do not inflate n; exploratory output cannot become preregistered retroactively.
- Acceptance: written convention (immutable source refs, source-set digest, analysis version, independent unit, measurement identity, declared null, frozen-vs-exploratory flag) + one inspectable analysis.
- Claim boundary: adjudication outside executors; within-run aggregate keeps its meaning.
- Status: OWNER. Read-scope grant is a readback dependency only; unrelated worlds must stay outside scope.

### WP-X2 · Backend repeatability within declared scope · **Vivarium** (Harmonia: what grades license; operator: tool admission)
- Dependency: WP-P0's tool, or any admitted tool. Gates backend observations' licensed grade only.
- Tests: X2-a deterministic backend repeats; a nondeterministic one records a mismatch rather than a silent downgrade; X2-b matches twice, diverges on the third → no universal guarantee from the admission pair; X2-c build/config/environment change invalidates prior qualification; untested vs sampled-replay observations distinguishable; X2-d canonicalisation removes only declared non-scientific metadata; timeout/crash/partial output keep honest records.
- Acceptance: versioned contract; bounded seed/config replay matrix; scoped Harmonia ruling. Existing grade enums preserved.
- Claim boundary: matching re-executions are repeatability evidence in tested conditions, never proof of determinism.
- Status: OWNER (wording corrected from "double-run proves determinism").

### WP-X5 · Witness presence and typed lineage, reference-only · **Mnemosyne** (Daedalus: observation/artifact identity; Proteus: organism identity; Vivarium: emits)
- Dependency: none. Gates queryable witnesses and lineage, not execution.
- Tests: X5-a program and CA witnesses findable and resolvable to authoritative content; absent/empty/truncated/unavailable distinguishable; X5-b digest/reference mismatch, wrong identity, unauthorized readback fail via existing access control; X5-c idempotent identical edge writes, conflicting same-identity writes fail, chains traversable; X5-d eviction/index changes never delete or reinterpret SFE history.
- Acceptance: one program-witness and one CA-witness round trip + a small typed lineage/transfer chain; reference-only doctrine satisfied or an approved exception recorded (the earlier "witness jsonb copy" is withdrawn in favour of a typed reference/presence index unless a doctrine ruling says otherwise).
- Status: OWNER.

### WP-X6 · Exploration reserve across families first · **Archaeon** (operator: values)
- Dependency: none to implement; operator values to *activate*.
- Tests: X6-a 100-template vs 1-template families equal entitlement; X6-b more families than slots → all served within the horizon, or the shortfall stated; X6-c baseline cannot enter the reserve via alias/ambiguity; no eligible family → unspent, reported; X6-d counters once per event; frozen order immune to later counters/timestamps.
- Acceptance: `archaeon/producer/allocation.py` (family-first deficit round-robin, deterministic replay, snapshot hash); tick records `family` and `allocation` in `source_evidence`; INACTIVE until `archaeon/policies/allocation.reserve.v0.json` carries `chosen_by`/`chosen_on`.
- Claim boundary: 1/6, 90 days, 24 rows, cap 4 are proposals; "24 rows" is not a power or eligibility guarantee; equal reserve fractions alone do not make arms comparable.
- Status: **DONE** as code (this commit); policy INACTIVE pending D-6.

### WP-X7 · Per-family directed template + matched frozen control · **Archaeon** (operator admits; Harmonia qualifies the detector)
- Dependency (split, per the order): **collection** needs only the admitted random route; **comparison** needs a frozen corpus/universe, both orders committed, applicable controls, and the qualified detector.
- Tests: X7-a every directed draw satisfies its region constraints; empty/malformed/wrong-family regions → explicit blocked result; X7-b frozen source refs, detector version, policy version, universe, budget, orders reproduce exactly; X7-c widening the universe invalidates the old pairing and creates a separately versioned matched control; X7-d a non-firing or ineligible detector → scoped status under the allocation policy; never deletes or rejects the family.
- Acceptance: for each implemented family, one corpus → signal → proposed next experiment → preserved provenance path; frozen comparison available for qualification.
- Status: IN LANE per family (bitstring: `resample_region.v0` PROPOSED; NK/CA/program after their kinds).

### WP-X8 · Retain observable behavioural diversity without score lift · **Archaeon** (Harmonia: claim boundaries; Proteus: identity; Mnemosyne: references)
- Dependency: WP-0f (result schema) for descriptor fields; PR-ID for cross-family identity.
- Tests: X8-a equal-score programs/rules with different trajectories occupy the archive with no positive-effect verdict; X8-b a label change or jointly transformed exact symmetry is not new behaviour under a descriptor convention that treats it as equivalent; X8-c failure-first retention bounded when every candidate is informative (deterministic tie-break); eviction touches pointers only; X8-d descriptor versions explicit; missing trace = unknown, not identical; no undeclared model-generated promise score can be consumed.
- Acceptance: coverage reports distinguish family execution, descriptor occupancy, observed behaviour, qualification; no cross-family scalar; passive retention usable before any active archive policy.
- Claim boundary: artifact identity ≠ observable behaviour ≠ performance ≠ causal evidence; execution errors ≠ completed negative outcomes.
- Status: IN LANE (after 0f).

## Branch A — interacting landscapes

### WP-A1 · NK landscapes with a verifiable witness · **Daedalus** (Vivarium registers kind/schema; Archaeon builds A2)
- Dependency: none.
- Tests: A1-a hand-computed small tables → exact scores and per-locus contributions summing to the score; A1-b k=0 has no cross-locus interaction; a constructed k>0 fixture exhibits one (not left to a random seed); A1-c joint locus/table/candidate permutation satisfies A2's invariant; seed replay regenerates tables; A1-d illegal k, duplicate/self-neighbour violations, length mismatch, malformed table sizes refused; A1-e a tiny exhaustively solved interacting fixture verifies solved/optimum semantics including incompatible local maxima.
- Acceptance: documented deterministic executor; contribution witness; registered measurements through the authorized path; wrapper parity.
- Claim boundary: k=0 equals the old onemax only if that construction is explicitly implemented; for k>0 score = 1 is not assumed attainable and a below-maximum locus is not an independent actionable correction.
- Status: OWNER.

### WP-A2 · NK null, control and uniform templates · **Archaeon** (Daedalus specifies the symmetry; operator admits)
- Dependency: A1, 0e.
- Tests: A2-a jointly permuted landscape and candidate preserve score; contribution matches after inverse permutation; A2-b a small asymmetric fixture catches candidate-only permutation; A2-c k=0 and interacting treatments declare construction, seed coupling and what differs; all three templates draw coherent parameters through 0e.
- Acceptance: three checkable templates with a documented null and control. Admission and qualification stay separate.
- Status: CONDITIONAL on A1.

### WP-A3 · First NK corpus, then a frozen comparison · **Archaeon** issues (Vivarium executes; Harmonia adjudicates)
- Dependency, **split**: A3-acq (corpus acquisition through the admitted random route) needs A2 + local integrity; A3-cmp (frozen comparison) needs a frozen corpus/universe, approved protocol, correct provenance/units, and the detector's qualification.
- Tests: A3-a each series holds its landscape fixed while candidates change; queries share declared lineage, never counted as independent landscapes; A3-b corpus and universe hashes precede both orders and execution; source-witness refs round-trip; A3-c permutation control satisfies its exact invariant while detector calibration uses the separately declared stochastic null; A3-d no separation → a report scoped to these coordinates/policy/budget, never "NK is flat".
- Acceptance: a preserved, inspectable NK corpus and a correctly staged comparison plan. The proposed k∈{0,2,4} × 3 seeds × 20 queries is a **bounded pilot** until Harmonia sizes the intended claim; the measurement (interaction / region discrimination / selection improvement) is named before the run.
- Status: CONDITIONAL on A2.

### WP-A4 · Related landscapes without waiting for runtime memory · **Daedalus** (Harmonia: relation/mapping and transfer comparison; Proteus: identity where needed)
- Dependency: A1. **Not** B4. Transfer of a source-derived candidate, program or parameter vector needs a declared mapping and baselines, not persistent runtime memory (HA-1).
- Tests: A4-a identity relation reproduces the source landscape; controlled partial sharing gives the declared overlap, boundaries checked; A4-b execution-affecting table configurations cannot hide behind an unchanged execution identity; mapping refs round-trip separately; A4-c a source-derived static candidate is mapped and evaluated without a persistent-state interface; A4-d baseline arms share target worlds/budgets and differ only in source information; leakage detected.
- Acceptance: executable related worlds and a valid transfer-comparison design (matched fresh / shuffled / unrelated-source baselines). Design labels never alter a landscape; a changed parameter contract is a new kind/version.
- Claim boundary: a null transfer result prices that source artifact and policy; it does not undo relatedness. A known construction curve is distinct from a policy's empirical ability to exploit related worlds.
- Status: OWNER (wording "deferred behind a stateful organism" withdrawn).

## Branch B — symbolic execution

### WP-B1 · VM as a pure semantic library · **Proteus** (Vivarium: thin wrapper)
- Dependency: none.
- Tests: B1-a tiny hand-authored programs verify arithmetic/control flow, input consumption, output semantics, exact first counterexample under a declared ordering; B1-b all 64 specimens agree with the arena path; world-blindness reported without counting every specimen as a responsive agent; B1-c zero/min/exhausted budgets, invalid opcodes, absent outputs, missing specification lookups have defined results (budget exhaustion is a declared status, counterexample or not, by contract); B1-d replay and semantic opcode relabelling hold; trace truncation explicit, cannot change execution or select a different witness.
- Acceptance: side-effect-free library; independent semantic fixtures; wrapper/arena parity. Existing specimens need not solve the new task.
- Status: OWNER.

### WP-B2 · Program templates and information controls · **Archaeon** (Proteus specifies VM and opcode transformation)
- Dependency: B1, 0e.
- Tests: B2-a renaming opcode encoding and decoder together preserves outputs/halting/steps; traces compared after decoding; B2-b the two arm views differ only in the declared witness treatment; an adversarial fixture detects a witness copied into another producer-visible field (outputs vector, expected outputs, trace, log, ordering); B2-c restrictions do not remove the authoritative observation from audit storage; the wrong arm cannot retrieve it through the permitted proposal interface.
- Acceptance: replayable templates and a precise information-access contract. Where the specification is already public, the claim is an interface/computational saving, not access to unavailable information.
- Status: CONDITIONAL on B1.

### WP-B3 · Frozen selection vs online witness refinement — two named experiments · **Archaeon** (Harmonia: protocol qualification)
- Dependency: B2, X1, X7. Named **before** implementation: (i) **frozen M-SIGNAL route** — directed orders from already frozen evidence, both orders and the universe frozen, canonical endpoint; no claim that returned witnesses changed the order; (ii) **adaptive witness route** — precommitted policy code/version, allowed evidence, initial state, seeds, budgets, tie-breaks, stopping/censoring; later programs may depend on returned witnesses; rounds-to-match under its own approved protocol, never called M-SIGNAL.
- Tests: B3-a a frozen order does not change after new observations; a claimed online dependency is rejected under that protocol; B3-b the adaptive policy reproduces the same next candidate from the same permitted history and seed, and follows a different valid branch when the witness changes; B3-c both arms obey one budget and stopping rule; unsolved runs censored/counted by the preregistered convention, never dropped; B3-d B2's leakage checks hold end to end; an intentionally witness-using toy policy shows the treatment reaches the producer.
- Acceptance: one internally consistent protocol per route and an executable example.
- Claim boundary: no advantage = no demonstrated advantage for the tested policy/design; it does not prove the policy ignored the witness or that counterexamples are useless. Producer-side use of prior observations is distinct from a running organism reading fossils.
- Status: CONDITIONAL on B2; route (ii) needs Harmonia's protocol before any online campaign.

### WP-B4 · Widen the input channel, bounded applicability · **Proteus** (Harmonia: PATH B qualification)
- Dependency: none. **Gates only claims relying on that channel/population** — not organism diversity or source-artifact transfer generally.
- Tests: B4-a an input-sensitive program changes behaviour with world input; a world-blind program is the negative control; B4-b alphabet boundaries, sequencing, initialization, entropy agree with the declared channel; no hidden fossil access; B4-c legacy fixtures keep old behaviour under the old version; new channel distinguishable in execution identity; B4-d usable population and pair counts from the stated criterion with floor/ceiling and uncertainty.
- Acceptance: versioned, tested channel and a scoped PATH B result on the appropriate frozen population, not generalized to every program, genome, rule or transfer experiment.
- Status: OWNER (wording "prerequisite of any organism claim in B" withdrawn; scoped).

## Branch C — spatial, stateful

### WP-C1 · CA verifier as a pure library · **Herakles** (Vivarium wraps; Archaeon uses the contract in C2/C3)
- Dependency: none.
- Tests: C1-a hand-computed tiny states verify wraparound, simultaneous update, neighbourhood indexing, update count; a second simple implementation is the independent oracle; C1-b six recovered genomes have golden results on small fixed IC fixtures; malformed tables, unsupported radius, invalid density/grid fail explicitly; C1-c joint reflection and complement satisfy whole-trajectory equivariance, compared on normalized trajectories not raw hashes; C1-d sampling seed and configuration replay; no filesystem or global-RNG side effects; C1-e a **separate** historical-reproduction run uses the source's conventions, an adequate declared IC sample, and a prespecified uncertainty/multiplicity procedure; discrepancies diagnosed, tolerance never changed after inspection.
- Acceptance: pure library with semantic and symmetry tests; thin-wrapper parity fixture; honest historical-validation report. Pinned: ring boundary, neighbourhood bit order, rule encoding, supported radius (no silent generalization of an r=3 decoder), update count, majority/tie convention, accuracy definition; bounded witnesses and a declared selected trajectory/digest.
- Claim boundary: faithful deterministic behaviour is an implementation result; statistical reproduction is a separately reported qualification result.
- Status: OWNER.

### WP-C2 · CA templates with correct symmetries and scoped ablations · **Archaeon** (Herakles: C1 fixtures; operator admits)
- Dependency: C1, 0e.
- Tests: C2-a joint rule/input reflection (and, for complement, also the majority target and witnesses) yields exactly transformed trajectories and identical correctness masks after normalization; odd-size majority tested; if even grids are supported the declared tie rule must transform consistently before complement invariance is claimed; C2-b a fixture detects rule-only same-IC transformation; C2-c radius/table-size mismatch rejected; r=0 really reads only the centre cell (explicit centre-only family or declared projection, correct table size); C2-d T=1 performs the declared single update; report names horizon change separately from memory claims.
- Acceptance: reflection, radius-zero, one-step and uniform templates with executable semantic checks and accurately described controls.
- Claim boundary: "same seed" alone is not the symmetry; T=1 is a shortened horizon, not removal of all state; exact symmetry tests do not certify any detector's false-alarm rate.
- Status: CONDITIONAL on C1.

### WP-C3 · First CA corpus and family-specific qualification · **Archaeon** issues (Herakles: conventions; Vivarium executes; Harmonia adjudicates)
- Dependency, **split**: historical reproduction (C1-e) · random-rule corpus acquisition (admitted random route) · frozen selection evaluation (frozen corpus, protocol, provenance/units, detector qualification).
- Tests: C3-a historical and random arms receive the declared paired ICs; rule identities and source revisions retained; C3-b accuracy, failing ICs and the selected trajectory identify the same run and replay from inputs; C3-c shared ICs, repeats, rule reuse do not inflate independent-unit count; Harmonia's clustered/paired analysis followed; C3-d a null or weak result retains observations and a bounded conclusion; never "needle-like" for the family without evidence for that claim.
- Acceptance: a usable spatial corpus; an explained historical-validation result (a mismatch is diagnosed across conventions, horizon, sampling, transcription, implementation — not presumed a verifier defect); a correctly frozen next comparison. Rediscovery of known strategies labelled as such.
- Status: CONDITIONAL on C2. Historical qualification may stay unresolved while labelled development data and library work proceed.

### WP-C4 · Environment–organism co-development as a later bridge · **Harmonia** designs (Archaeon implements the declared producer policy)
- Dependency: validated CA semantics (C1) for executable trials; a bounded design/spike may precede full C3 qualification.
- Tests: C4-a frozen policy + identical history/seeds reproduce the next environment–artifact pair; C4-b holding environments fixed / organisms fixed each disables the intended update; invalid generated environments rejected; C4-c training observations cannot alter the frozen evaluation set; lineage records identify which observations informed each update.
- Acceptance: a faithful bounded protocol with explicit alternatives and controls; adaptive if decisions use newly returned results; persistent controller runtime memory only if the chosen question needs it.
- Claim boundary: co-development can be implemented and tested while its advantage over a fixed curriculum stays unknown.
- Status: OWNER.

## Branch D — population ecology

### WP-P0 · Bounded population-route spike · **Vivarium** (operator authorizes scope; Ergon consulted on the freeze)
- Dependency: operator authorization consistent with Ergon's freeze record. Routes compared: available Avida version/build path; minimal in-process soup; recovered `hct01.c` where applicable.
- Checks: P0-a clean documented build/run succeeds or records the exact blocker per route; P0-b bounded repeated runs preserve inputs, environment, digests, failures, costs; P0-c report distinguishes not attempted / blocked / failed / runnable / repeatable-under-tested-conditions, never upgraded to proved determinism. Avida 2.2 runnability kept separate from fidelity to the 1.6 experiment; the spike is not permission for frozen population generation.
- Acceptance: evidence-based route comparison within the approved cap (proposed two days); route selected or deferred on explicit cost/fidelity/reproducibility grounds; no ecological claim.
- Status: OWNER, awaiting authorization.

### WP-P1 · Implement the selected population route · **Vivarium** (P0 selects; P2 units; P3 neutral baseline; X5 lineage refs; X2 only if the route crosses a process boundary)
- Dependency: P0. Descriptive execution permitted before P3; **claims depending on neutrality** need P3.
- Tests: P1-a a tiny manually computable population follows the declared reproduction/resource update; P1-b zero mutation → no mutation-generated novelty; disabling a declared interaction removes that dependency with other parameters explicit; P1-c parentage/mutation edges reconstruct the sampled lineage; extinct and surviving lineages traceable; P1-d identical inputs replay within contract; scheduler/initialization changes reflected in provenance/identity; P1-e a separate neutral-baseline comparison matches P3's demography and assumptions; unlimited resources not accepted as neutrality by label.
- Acceptance: one faithful population world with preserved trajectories, lineage and scoped reproducibility evidence.
- Claim boundary: neutrality, persistent diversity and adaptive advantage are separately qualified claims.
- Status: CONDITIONAL on P0.

### WP-P2 · Generations, episodes, statistical independence · **Harmonia** (Daedalus implements vocabulary/validation)
- Dependency: none. Gates analyses using those units, not library development or the P0 spike.
- Tests: P2-a a 100-generation trajectory from one seeded population reports 100 time points and the declared number of independent populations, not n=100; P2-b episodes with shared controller state or world history preserve dependencies; independent resets carry explicit initialization; P2-c unsupported unit declarations fail clearly; existing units keep their meaning through schema/client round trips.
- Acceptance: vocabulary ruling; worked CA/population examples; additive schema conformance; decision on how ORIGINAL/REPLICATION represent a continuous trajectory.
- Claim boundary: a vocabulary addition cannot make successive generations independent replicates.
- Status: OWNER.

### WP-P3 · A specified neutral baseline; reversibility separate · **Harmonia** (Proteus/Vivarium implement kernel and dynamics)
- Dependency: none. Gates **claims needing the neutral baseline**, not execution or descriptive study.
- Tests: P3-a on a small finite kernel: nonnegative transitions, rows sum to one, declared stationary π satisfies πP = π; P3-b a reversible fixture satisfies πᵢPᵢⱼ = πⱼPⱼᵢ; the three-state lazy clockwise cycle P = 0.5I + 0.5S keeps uniform stationarity while failing detailed balance — classification must distinguish the two; P3-c a deliberately biased mutation fixture is detected against the declared reference measure without being mistaken for a failed implementation of a declared biased treatment; P3-d neutral-drift comparisons match specified demography and fitness assumptions; resource removal that changes them is not silently the same null.
- Acceptance: a tested neutral baseline with explicit scope (reference measure, mutation process, fitness, reproduction/replacement, resource regime, meaning of "neutral") and a separate reversibility statement. Nonreversible kernels can have stationary distributions; declared mutation bias can itself be a treatment.
- Status: OWNER (earlier "detailed balance before any diversity claim" withdrawn; scoped).

---

## What each first experiment lets the next action depend on

- **A3 → X7(A):** a fired, qualified D3 region on an NK world becomes the argument of `nk.resample_region.v0`, compared against `nk.uniform.v0` on the NK family's own frozen corpus.
- **B3 (frozen route) → `program.refine_on_witness.v0`:** a witness already in the frozen corpus becomes a parameter of the next program's specification emphasis; **B3 (adaptive route)** uses returned witnesses under its own protocol.
- **C3 → `ca.resample_region.v0` and a directed IC distribution:** a fired region on a declared rule-table descriptor, or a witness IC set, constrains the next draw.

Broad collection through the admitted random route never waits for a signal; the comparison always waits for a frozen corpus.
