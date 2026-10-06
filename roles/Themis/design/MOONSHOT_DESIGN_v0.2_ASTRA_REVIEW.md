# Project Moonshot v0.2 -- Astra review for Themis

+======================================================================+
| ASTRA REVIEW: PROJECT MOONSHOT v0.2                                    |
| Author: Enceladus / Astra, BUCKKEEP. Date: 2026-10-06.                  |
| For: Themis, operator, and RSO contract owners.                        |
| Status: REVISE BEFORE LAUNCHPAD; scientific status NOT_VERIFIED.       |
| Self-contained findings; repository anchors permit verification.      |
+======================================================================+

----- 0. Decision and scope -----

**Keep the Epic and its instrument-first direction. Revise the measurement
and integration contracts before treating Launchpad as a scientific test.**
This is not a request to replace survival-only evolution with an orthodox
learner, build a larger framework, or wait for the whole Observatory.

The strongest design decisions are worth preserving: independent H1/H2
claims, fixed Launchpad world distribution, independent consumer authority,
integer reference semantics, bounded shard epochs, explicit reachability
levels, and the distinction between fixing code and falsifying science.
The operator's approval and ownership boundary remain intact. Themis owns
disposition of this review; Palamedes/the RSO cell owns its contract.

Three contradictions need resolution before their respective gates freeze:

1. H1 demands rejection of a fabrication that the reused evidence contract
   explicitly cannot distinguish from authentic execution (F01).
2. R6 makes a destructive scramble an ablation and also requires it not to
   reproduce the ablation effect, rejecting a canonical memory user (F02).
3. Integer determinism is treated as sufficient fit to slice-001, but its
   claim, world, domain and verdicts are much narrower than Launchpad (F03).

Seven further findings make those gates operational rather than rhetorical.
One is a reproduced source defect, not merely an implementation wish list.
No scientific campaign, fleet job, paid job or change to the reviewed design
was made. The bounded local diagnostic probes are recorded in section 4.

**Snapshot.** Review base and fetched origin/main:
`0d62f04314101be2a5d8b1f7e19b651cff4ef01f`.
Target: [MOONSHOT_DESIGN_v0.2.md](MOONSHOT_DESIGN_v0.2.md), all 466 lines,
including the same-filename 2026-10-05b TDD revision. Target Git-blob SHA-256:
`4c3e8710a5f94f1625da76cbad0fd4820a36cb6487c0a9a25e54bbf799ff07fd`.
All target line references below refer to this snapshot, not a future v0.2.

Review branch: `enceladus/themis-moonshot-review-2026-10-06`.
Worktree: `C:/Prometheus-worktrees/enceladus-base-role`.
Tracked changes at review start: none. Delivery scope: this review only.
Canonical checkout, prior Foundry branch, runtime and main are not modified.

----- 1. Prioritized findings -----

BLOCKING means a contradictory or incompatible gate must be resolved before
that gate can judge evidence. HIGH means a missing contract or a confirmed
runtime defect must close before the relevant scientific execution. Neither
means "stop writing calibration fixtures"; that is how several gates close.

| ID | Priority | Decision needed | Close before |
|---|---|---|---|
| F01 | BLOCKING | H1 trust boundary and typed expected outcomes | H1 challenge freeze |
| F02 | BLOCKING | Destructive ablations versus preserving sham | R6 calibration freeze |
| F03 | BLOCKING | Native claim-to-RSO predicate mapping | Consumer admission |
| F04 | HIGH | Null information boundary and paired intervention semantics | Assay freeze |
| F05 | HIGH | Reachability, power and finite-budget claim | Science preregistration |
| F06 | HIGH | Separate HYB claim and neural-use contrast | Arm comparison freeze |
| F07 | HIGH | Scope of selection air-gap | Promotion/continuation policy |
| F08 | HIGH | Epoch completion and evidence sufficiency | Distributed scientific epochs |
| F09 | HIGH | Runtime readiness, including unpaid action writes | Survival-based search |
| F10 | HIGH | Fresh calibration challenge and leak controls | Instrument qualification |

### F01. H1 asks the existing contract to detect an unobservable fabrication

**Anchors:** target S2 L86-L92 and S9 L294-L300. Frozen RSO
`rso/slice001/contract/CONTRACT.md` L106-L111; incorporated draft B
`rso/slice001/contract/drafts/B_evidence_receipt_authority.md` B5.4
L272-L277 and B9 L479-L483, L528-L540.

The target says H1 is confirmed only if the RSO rejects internally consistent
fabrications. The RSO contract explicitly says no predicate detects an
internally consistent lie made before registration. FAB_CONSISTENT can pass
binding, inventory and recomputation; FAB_REGISTERED can qualify custody.
The required limitation is "execution not authenticated," not a refusal
invented after seeing the planted label.

**Failure shape:** two submitted bundles have identical observable evidence
bytes; one was executed, one fabricated before registration. A consumer of
those bytes cannot distinguish their histories. Hashes, a keeper and opaque
IDs do not supply the missing observation. Requiring rejection can reward a
label leak or encourage changing a sound contract to satisfy an impossible
test. This is not evidence that the current RSO is defective.

**Repair:** give H1 a matrix of attack class, accessible evidence, expected
typed decision and claim ceiling. Reject detectable contract violations and
post-anchor alterations; report underpowered data as underpowered, not as a
dishonest producer. For pre-registration fabrications, either test that the
consumer preserves its execution-authenticity limitation, or first register
a new threat model and independent execution check. A consumer-controlled
rerun can check reproducibility of submitted code under fresh challenges; it
still does not prove that the alleged historical run occurred. State the
attacker powers and exactly what added evidence distinguishes the case.

**Acceptance:** honest negative and underpowered producers receive correct
typed outcomes; an altered anchored trace is refused; a fully consistent
registered fabrication never acquires an assertion of authenticated
execution. Do not score correct preservation of that limitation as H1 failure.
Any stronger detection claim requires a distinct, qualified instrument.

### F02. R6 confuses information destruction with an intervention sham

**Anchors:** target R6 L150-L158; floor world L373-L376.

R6 requires channel-cut and state-scramble/resample as ablations, then requires
an ablation drop "not reproduced by the scramble control." A destructive
scramble should reduce the performance of a genuine memory user.

**Counterexample:** a balanced binary cue is stored in one bit. Later the
observation is blank and choosing that bit determines survival. Intact and
information-preserving sham success are 1. Cutting cue acquisition, or
independently resampling the stored bit, gives success 1/2. The written rule
rejects this intended positive because the destructive resample also drops.
These exact probabilities were checked by finite enumeration for this review;
they are not measured Moonshot performance.

**Repair:** distinguish three operations: channel-cut; information-destroying
state resampling; and an information-preserving, valid-state sham that matches
the intervention procedure without removing the relevant information. State
what each operation changes and preserves. A second destructive ablation is
useful corroboration, not a control that must leave performance intact. If
"scramble" was intended as a preserving re-encoding, name the preserved
quantity and the corresponding decoder transformation explicitly.

**Acceptance:** the one-bit example passes the intended causal test; an invalid
state encoding that crashes a reflex controller does not. Freeze margins for
intact-versus-null, intact-versus-destructive intervention and intact-versus-
sham before the challenge, with failure of intervention validity reported
separately from absence of memory. Do not require every possible information
ablation to work: its target and causal interpretation must be specified.

### F03. A deterministic integer organism is not automatically a slice-001 case

**Anchors:** target S6.3 L234-L236, S8 L280-L283, S9 L287-L300.
RSO draft A `A_world_reset_observer.md` A1-A3 L28-L115;
`rso/slice001/adapter.py` L7-L16 and L56-L78.

Slice-001 certifies a useful bit across a named EPISODE CONTENT RESET through
one allowed component. It enumerates 4096 six-episode input histories, with
fixed output alphabets, bounded pending messages and explicit reset/restore
predicates. Its claim explicitly excludes origin, economy and native physics;
its finite exhaustive domain has no statistical INDETERMINATE slot.

Moonshot proposes within-life delayed-cue survival, reproductive lineages,
evolutionary discovery, hundreds of sampled seeds and statistical comparison.
None follows just because both systems use integers. The adapter says it is
not a universal runtime adapter. An RSO-shaped receipt alone does not convey
authority for a new predicate, world or sampling regime.

**Repair:** agree a versioned mapping with Palamedes before adapter work:
Moonshot proposition -> native state/boundary -> interventions -> trace fields
-> existing or new predicate -> calibration -> verdict/authority. Keep native
assay truth separate from a W-S1 transplant. A W-S1 pass supports the W-S1
claim, not automatically survival dependence or evolved origin in wforge.
Do not impose an artificial episode reset and quietly call it native physics.

First integration can remain a very small deterministic fixture plus honest
in-scope and out-of-scope receipts. A new native-world contract or explicit
amendment is an expected result, not permission to weaken the old contract.
Likewise, UNDERPOWERED, BLOCKED execution, UNQUALIFIED authority and a valid
negative must not collapse into a single KILL field.

**Acceptance:** an out-of-domain Moonshot receipt cannot acquire a W-S1 claim
by renaming its fields. The consumer states which claim is supported and by
which qualified predicates. Statistical and native-world extensions follow
the cell's versioned process. Float/GPU semantics are a later issue, not the
first or only integration gap.

### F04. Define the reactive null's information and the counterfactual's schedule

**Anchors:** target R1-R2 L135-L138, R6 L150-L158, Launchpad L373-L381.

An "optimal observation-only policy" needs a policy class and information
boundary. On two equally likely cue histories ending in the same blank
observation, one shared memoryless policy scores at most 1/2. Optimizing a
different constant policy for each seed scores 1, leaking the answer through
policy selection. Conversely, disabling an internal register does not remove
memory stored in location, charge, pending actions, other organisms or a
world mark subsequently visible in the current observation.

**Repair:** specify the policy's current observation, permitted clock/identity
inputs, policy-sharing distribution and allowed environmental memory. For
the tiny assay, enumerate an exact bound over that class. Label a best-found
reactive baseline as such when no bound is available. A reactive controller
with lawful environmental memory should either count under the declared
composite boundary or be blocked by world design; it is not automatically a
cheat. Keep phenotype state, inherited genome and search history distinct.

Paired intervention also needs a causal schedule. Hold the initial state and
exogenous opportunities/randomness fixed, not factual actions, births or
deaths that depend on the intervention. Otherwise a counterfactual death can
be followed by a forced factual reproduction. Named mutable RNG streams are
not sufficient if changed control flow consumes different draws: use an
explicit coupling rule, such as event-keyed exogenous draws, or document the
paired tape and consumption semantics. Fix intervention timing and target.

**Acceptance:** the two-history exact null remains 1/2 with one shared policy;
test-seed-conditioned policy selection is refused. A counterfactual death
removes its downstream reproduction while external resource arrivals remain
matched. Audit environmental carriers, adapter caches, observation buffers
and pending queues, not just the neural recurrent state.

### F05. Reachability is not statistical power, and a finite null is not global H2 KILL

**Anchors:** target R-RC/R10 L166-L176, S17 L414, S18.3 L444-L451.

The RC0/RC1/RC2 separation is valuable. The next step is to stop asking it to
do the job of a finite-sample rejection rule. RC0 proves expressibility, not
discovery. A fitness-improving path proves neither enough paths nor likely
mutation along them; therefore RC1 alone does not establish "not a needle."
RC2 estimates a rate under a particular search procedure and start
distribution; it is not an exact universal rate transferable to new settings.

**Counterexample:** even if the discovery probability is exactly 0.01 per
independent search replicate, zero discoveries in 100 replicates occurs with
probability 0.366032341. RC2 can be genuine while this null remains inconclusive.
For the one-sided claim p >= 0.01, zero discoveries first rejects at 5% with
299 independent replicates, without multiplicity/sequential adjustments.
The exact arithmetic was checked here; these are illustrative assumptions,
not proposed campaign counts or a Moonshot power calculation.

**Repair:** freeze a claim tuple (world distribution, representation/palette,
search/mutation procedure, randomized-start distribution, budget, endpoint,
minimum effect/rate). Bind RC certificates to it and state their uncertainty.
Use distinct discovery, calibration and confirmation seeds. Reusing RC2
successes as confirmation after tuning the world/search is not independent
evidence. Count independent search populations, not descendants, ticks or
episodes from the same search run, as the discovery sampling unit.

Require both relevant reachability and a preregistered rejection/equivalence
rule for a scientific KILL. Failure to show superiority is not proof of no
advantage. No finite null kills the unbounded existential H2 across all future
worlds. A precise operational claim can be killed; untested scope stays open.
Execution failure is BLOCKED/INVALID, not an underpowered scientific outcome.

**Acceptance:** the 100-replicate example is not KILL; an uncertain RC2 estimate
does not become a certain null probability. Changing mutation kernels or start
distributions invalidates transfer of its certificate unless justified. A
campaign stops at its preregistered cap and reports the scoped verdict.

### F06. Launchpad adds a third claim, and palette access is not neural causation

**Anchors:** target H1/H2 L86-L102, R7 L159-L163, Launchpad L373-L383.

The Launchpad gate tests HYB superiority over SYM. That is distinct from both
observatory validity (H1) and evolved retained-information dependence (H2).
If both arms evolve genuine memory equally often, H2 can succeed while HYB
earns no promotion. If only planted controls pass, H1 calibration can succeed
while evolved H2 remains unestablished. Neither is a blanket Epic failure.

**Repair:** give HYB superiority its own named operational claim and verdict.
Choose rate-at-fixed-budget or time-to-first-qualified-crossing as the primary
endpoint, with non-crossers handled explicitly. To claim the preset advantage
delta, require the specified bound relative to delta, not just a point estimate
above delta plus a confidence interval excluding zero. Prespecify paired world
seeds, independent evolutionary replicates, multiplicity/stopping, second-world
holdout and how all candidates, null searches, retries and confirmation cost
enter the budget. "Hundreds of seeds" is not an analysis plan.

Match and report organism instruction/primitive work, mutable bytes, world
evaluations and host cost. A matrix call and a scalar operation are not equal
work because each is one VM instruction. State which resource defines the
primary fairness claim and report the other costs rather than asserting all
notions of fairness coincide.

A HYB win establishes an effect of offering the palette under the specified
search. It does not show the neural primitive carries the useful information:
search-space geometry or unused genome capacity can change discovery rates.
Add a post-search, valid-state primitive-disable/substitution contrast with a
cost-matched sham and a strong symbolic memory positive. Keep those diagnostics
out of reproductive fitness; a failed primitive-use contrast narrows the claim.

**Acceptance:** equal successful SYM/HYB arms report evolved retention but no
HYB advantage. A HYB winner that never uses its primitive cannot be labelled
neural-mechanism evidence. No GPU is necessary for these initial CPU contrasts.

### F07. Offline scoring alone does not establish a selection air-gap

**Anchors:** target S1 L74-L78, R4-R5 L142-L149, S6.4 L238-L240,
S9 L287-L292 and novelty claim L337-L343.

A metric need not appear in a fitness formula to affect reproductive ancestry.
If only high-scoring checkpoints receive further evolutionary epochs, their
descendants are selected using that metric. Likewise, world or search redesign
based on the S-meter is measurement-dependent selection across experiments.
That may be useful, but it is not a global selection air-gap.

**Repair:** choose and state the boundary. Either score-dependent promotion
only confirms frozen organisms, with no feedback into reproductive continuation,
or claim survival-only selection *within each frozen run* and disclose
metric-dependent allocation/curriculum between runs. Distinguish terminating
a complete preregistered campaign from selectively extending promising
lineages. Archive continuation and promotion decisions as part of ancestry.

**Acceptance:** counterfactually permuting offline scores cannot change
reproductive ancestry inside the claimed air-gap. If it changes only reporting
or frozen confirmation, the narrower separation holds. If it changes continued
breeding, report that intervention instead of hiding it behind "offline."

### F08. Specify epoch commit semantics and the limits of future re-scoring

**Anchors:** target R-EP/N4/N5 L185-L208, S6.0/S6.3 L215-L236,
S7.2 L247-L255 and S18.1 L426-L434.

The epoch abstraction is the correct direction. "Atomically published" still
needs a failure model. Worker retries, lease expiry and push failure can give
two valid attempts from one parent checkpoint. A single process completing
does not imply exactly one authoritative successor or one promotion decision.

**Repair:** identify semantic work by input-checkpoint hash, epoch-spec hash
and runtime version. Capture world, organisms, population/lineage state,
pending events, RNG state, mutation/search state and adapter state that affect
future behavior. Separate execution-attempt IDs and costs from semantic epoch
identity. Make output blobs durable before atomically exposing a verified
completion manifest binding input/spec/trace/output. Commit one accepted
successor through an explicit compare-and-swap rule; duplicate equal attempts
are idempotent, disagreeing outputs are quarantined, and stale workers cannot
advance the accepted chain. Charge retry costs even when their scientific
effects are discarded. Ordinary epoch retry must not masquerade as an RSO
content-reset intervention.

N5 also overpromises: no arbitrary future scorer can recover information that
was never logged or an intervention never run. A digest identifies data; it
does not contain the trace. Define a versioned evidence schema and a declared
class of supported re-scoring. Missing fields/arms mean NOT_EVALUABLE. New
counterfactual execution is a new, charged derived run with frozen inputs and
new provenance, not "re-scoring without re-running."

**Acceptance:** fault-inject before and after blob durability, completion
publication and lease expiry; observe one accepted successor, complete evidence
and no duplicate reproductive/promotion effect. Replaying two chained epochs
matches uninterrupted execution. A scorer requiring an absent intervention
reports the missing evidence rather than manufacturing a verdict.

### F09. Make substrate completion an explicit gate; wforge has an unpaid-write defect

**Anchors:** target S7.4 L262-L263 and S8 L273-L283;
`SerendipityFoundry/worldfoundry/wforge/world.py` L168-L188,
L207-L229, L250-L270.

The design correctly names wforge as dormant and unlaunched. The simultaneous
"two genuinely new builds" framing understates integration work with scientific
semantics: native checkpoint/restore, population/reproduction policy, assay
interventions, sufficient logs and consumer admission all need conformance
evidence. This review does not claim those capabilities are absent everywhere
in the repository; their completion for Moonshot is not demonstrated by reuse
names. `Encounter` itself offers stepping, observations and outcome hashing,
not a durable multi-epoch checkpoint/publication protocol.

**Reproduced defect:** when an action's cost exceeds the slot's charge,
`Encounter.step` sets `mag, cost = 0, 0` ("forced abstain") but then queues
writes from the original action vector. A controlled one-step local probe
gave available charge 1, requested cost 3, charged cost 0, `actions_used = 0`,
yet register change 251 relative to a zero-action twin. This is an action
affordability violation in the reviewed source, not a claim about evolved
exploit prevalence. It can corrupt survival-based selection and cost matching.

**Probe recipe:** construct `Mechanics` with one register and slot, horizon 2,
no linear operations/regime/stochasticity/delay, one action targeting register
0, action cost 3, step cost 0, start charge 1, yield register 0/window [0,1),
yield amount 0, observation registers [0], permutation [0,1], no observation
corruption/delay, horizon class MICRO. Make two `Encounter` instances with
world ID `review-underfunded` and episode seed 0. Step one with [[1]], the
other with [[0]]. Their charge is [1] and the first's action count is [0],
but the register difference modulo 65536 is 251. Zero background costs and
transitions isolate the action path; this is not a sampled campaign world.

The same file updates a digest of (tick, registers, charge, alive) and returns
that digest and summary counters. That interface alone does not expose
action/observation/intervention evidence or reconstructible checkpoint state.
Other code may add logging; a digest alone is not R9 compliance.

**Repair:** ask the substrate owner to add the red affordability regression,
fix the intake/queue path, and exercise over-budget, exactly affordable, delayed
and multi-channel actions against charged work. Do not quietly patch this
dependency as part of a documentary review. Name completion owners, acceptance
fixtures and bounded engineering effort instead of counting only two builds.

**Acceptance:** an unaffordable action has the defined abstention effect and
cannot queue unpaid writes. Then demonstrate a native frozen-input -> epoch
-> evidence -> independent decision vertical slice before launching search.
The local reproduction exited 0 because the defect was successfully reproduced;
the forced-abstain invariant FAILED. No fix or full runtime suite is claimed.

### F10. Opaque IDs do not make repeated calibration independent

**Anchors:** target R11 L177-L181, S18.2 L436-L442 and S18.3 L444-L460.

Opaque IDs and delayed label reveal are necessary improvements, not sufficient
blindness. A planted memory program, code hash, filename, trace shape, artifact
size or metadata pattern can identify a case family. Repeatedly fixing the
instrument against the same disguised controls can overfit their generators.

**Repair:** separate public development fixtures from a fresh qualification
challenge and from scientific confirmation. Commit the ruler and acceptance
rules before challenge generation/reveal. An independent case generator/keeper
holds assignments; the consumer receives the fields it needs to verify evidence
but no unnecessary label-bearing metadata. Record unavoidable code exposure,
who has seen which controls, and limits to independence. Include varied lawful
positives and memoryless look-alikes, environmental-carrier cases, invalid-state
ablation damage, and truth-model limitations from F01. Blindness must not mean
discarding provenance needed for binding checks.

Layer-1/2 defects can be repaired, but a revealed failed qualification attempt
stays in the record. A revised instrument version needs a fresh challenge and
new exposure receipt; repeatedly greening the same hidden set is regression,
not independent qualification. Bound attempts, false-positive/false-negative
criteria, and resource spend in advance.

**Acceptance:** renaming/permuting opaque IDs and irrelevant metadata leaves
verdicts unchanged. Freeze the scorer before reveal; demonstrate challenge
classification on unseen case variants, reporting the full confusion table and
scope rather than declaring the instrument generally unfooled.

----- 2. Smaller but worthwhile corrections -----

- **S scale (L115-L121):** label the numerical animal analogies illustrative,
  not calibrated measurements. Delayed retained-information use does not by
  itself demonstrate a world model, counterfactual reasoning, abstraction,
  general intelligence or recursion. Keep the floor claim precise.
- **S3/S14 (L107-L109, L387-L388):** "LLMs cannot discover" and "built so it
  cannot [fool its author]" exceed the evidence. State a design preference
  and an adversarial testing obligation, not impossibility guarantees.
- **Scheduling (L257-L260 versus L373-L375):** explicitly scope GPU routing to
  later admitted acceleration. Integer HYB Launchpad is CPU-only as S13 says.
  Integer/quantized does not itself ensure equality: accumulation order,
  overflow, saturation, rounding and activation semantics need specification.
- **Portability/SPOF (N3/N7; S7.2/S11):** DB-free does not imply availability
  without the git remote. State remote-outage behavior and read/write trust;
  a worker should not gain consumer/promotion authority merely because it can
  push a completion ref. Auto-join must not auto-authorize arbitrary code.
- **Scale assertions (L347-L349):** local time, energy and coordination are
  costs; linear scaling is an M4 hypothesis, not an established property.
  Measure useful work, retries, artifact/ref growth and maintenance load; keep
  large trace bodies out of an unbounded git history if measurements require it.
- **Anti-degeneracy (R-AD):** define finite lineage-continuation horizons,
  reproduction costs and resource turnover. Naming reproduction alone does
  not exclude inert self-copying or parasitic survival; do not remove a lawful
  discovered strategy after observing it without a new world version.
- **Prior-art/economics:** this was not an external literature or price audit.
  Entries marked "verify" remain unverified, and no novelty claim is certified.
  Do not delay the small contract repairs for a broad survey or cloud planning.

----- 3. Minimal incorporation plan and decision gates -----

1. **Themis + Palamedes: freeze claims and boundaries.** Resolve F01-F03 and
   assign separate H1, operational H2 and HYB verdicts. Record accept/reject/
   defer for every finding, with rationale and a closure artifact. A rejection
   should answer the counterexample, not just restate the intended design.
2. **Themis + substrate owner: one CPU vertical slice.** Repair F09 under the
   owner's tests; specify native state and events; execute planted memory,
   reflex, sham and two destructive interventions through native evidence and
   the agreed independent consumer. No evolutionary campaign needed yet.
3. **Consumer/keeper: instrument qualification.** Fresh, frozen H1/R6 challenge
   with typed outcomes, known limits and independent exposure accounting. This
   is M1 work, not something M1 must already have completed before starting.
4. **Themis: bounded reachability and science preregistration.** Freeze the
   claim tuple, RC transfer conditions, power, primitive-use contrast, budgets,
   continuation policy and confirmation split. Do not count tuning as held-out
   evidence. Seek operator decisions where existing authority requires them.
5. **M4 in parallel, isolated from scientific selection:** use synthetic epochs
   for retry/publication/remote-outage tests and transport measurements. Prove
   native epoch conformance before distributing reproductive populations.
6. **Then Launchpad; GPU/cloud only if earned.** Valid outcomes include H1
   qualification with no evolved positive, scoped H2 success with no HYB edge,
   and a decisive bounded null. Keep M5 and extended cloud deferred. A runtime
   or ruler failure halts affected inference; it is not an H2 KILL.

No new numeric resource cap is authorized by this review. Declare engineering,
qualification, RC and scientific caps separately, count failed attempts, and
stop at the first exhausted applicable cap. More compute does not resolve F01
or F02. A smaller claim or retirement remains a valid disposition.

----- 4. Evidence, checks and limitations -----

Read the full target and the operator's v0.2 approval/rulings. The earlier
charter was inspected in part, not audited as executable code. The approval's
instrument-first and constitutional ownership decisions govern this review;
no alternative Epic direction is implied. Related implementation inspection
was targeted, not a repository-wide completeness audit.

Source-checked findings use the base commit above. SHA-256 values below are
over Git-blob bytes; checked-out text was compared after CRLF normalization:

| Source | Git-blob SHA-256 |
|---|---|
| `rso/slice001/contract/CONTRACT.md` | `48fc6ba15caabc42ab7bf2beb4847682658d91de75318d408fd10d3aa0305025` |
| `rso/slice001/contract/drafts/A_world_reset_observer.md` | `254cd8c9bf7ef5a637623b9571a11eca2a903baaaa60243d85bbd8b8a897a9c8` |
| `rso/slice001/contract/drafts/B_evidence_receipt_authority.md` | `e1316d742e70b54501b672b8e15f913520799fc1ffb1af88490fee8ffec40174` |
| `rso/slice001/adapter.py` | `d3ffb4b30d09e6048ce165141052b96603a951c6864454a126b8d89745f9aea6` |
| `SerendipityFoundry/worldfoundry/wforge/world.py` | `31d40f0030d79d2981b28f2a05252914ebbbecf4cd764aef14e343f3a32524fe` |

The incorporated A/B drafts are normative through CONTRACT.md; their DRAFT
headers are superseded by its freeze. Amendment v1.0.4 was also inspected; it
changes validation-launch accounting, not the trust-model distinction cited
here. This is not a rerun or requalification of the RSO methods slice.

Executed locally with Python standard-library probes, no new dependencies:
- Six source hashes and normalized working-copy equality: PASS, exit 0.
- Finite one-bit success/null/resample arithmetic and binomial tail example:
  PASS, exit 0. These validate review counterexamples, not Moonshot science.
- One-step wforge affordability probe: defect REPRODUCED, exit 0, as F09
  records. This is a failing runtime invariant, not a passing runtime test.

Documentary checks: PASS, exit 0, for ASCII, LF, final newline, absence of
trailing whitespace, local link/cited-path existence, ten unique finding IDs,
three BLOCKING/seven HIGH rows, anchors/repair/acceptance in every finding,
six source hashes, unchanged reviewed sources, and branch/base isolation.
These are document checks, not empirical qualification. Staged scope and
remote commit identity are separate delivery checks.

Proposed acceptance tests elsewhere in this review have NOT been implemented or run.
No full runtime regression, end-to-end native adapter, search campaign,
cross-host oracle parity or adversarial qualification is claimed.

Evidence Wiki import was unavailable (`ModuleNotFoundError`); no search result
or submission is claimed. Indexed code retrieval could not address the linked
worktree; direct file reads at the pinned revision supplied the evidence.
Internal analytical/source review assistance is not independent qualification,
Themis agreement or Fable approval. A final auxiliary draft-check request
returned no response; no approval or validation evidence is attributed to it.
Scientific status remains NOT_VERIFIED.

----- 5. Copyable handoff packet -----

+======================================================================+
| MOONSHOT v0.2 -- ASTRA HANDOFF                                        |
| Enceladus / Astra, BUCKKEEP, 2026-10-06. For: Themis and operator.      |
| Status: REVISE BEFORE LAUNCHPAD. Science: NOT_VERIFIED.                |
| Self-contained summary; full finding/repair/test detail is in file.   |
+======================================================================+

0. Decision: keep the Epic, fixed-world CPU Launchpad and independent RSO
authority. Do not freeze the scientific gates until the contradictions close.

1. Three blockers: H1 demands detection of pre-registration fabrications
outside the RSO trust model; R6 rejects genuine memory when a destructive
scramble also causes a drop; integer determinism alone does not admit a
native survival assay to the finite reset-retention slice-001 contract.

2. Seven high-priority closures: specify the null's information boundary and
exogenous counterfactual schedule; separate reachability from statistical
power; separate H1/H2/HYB claims and test actual primitive use; bound the
selection air-gap; define idempotent epoch commits and re-scoring limits;
qualify the runtime; and use fresh blinded instrument challenges after repair.

3. Exact counterexamples: one-bit intact/sham success 1 versus destructive
resample/null 1/2. At discovery probability 0.01, zero hits in 100 independent
replicates has probability 0.366032341; at least 299 are needed for the stated
one-sided 5% zero-hit rejection, without other adjustments. Not campaign data.

4. Reproduced source defect: wforge queues an unaffordable action despite
recording forced abstention. Available charge 1, requested cost 3, charged 0,
actions_used 0, yet the register changes by 251 versus a zero-action twin.
The diagnostic exits 0 because reproduction succeeds; the invariant fails.
No runtime fix or evolved-exploit claim was made.

5. Next: Themis dispositions, Palamedes claim mapping, substrate regression
repair, one planted CPU native-evidence slice, fresh instrument challenge,
then bounded reachability/science. M4 can test synthetic epochs in parallel.
No paid job, extended campaign, design edit or main merge is part of this work.

6. Evidence: base 0d62f04314101be2a5d8b1f7e19b651cff4ef01f; six source
hashes checked; analytical examples and source probe executed. Wiki import
unavailable. Proposed acceptance tests remain unrun. No scientific result,
external approval or general instrument qualification is claimed.

7. Artifact: roles/Themis/design/MOONSHOT_DESIGN_v0.2_ASTRA_REVIEW.md
Branch: enceladus/themis-moonshot-review-2026-10-06.
The reviewed source remains unchanged. Themis owns incorporation.

+======================================================================+
| END. Narrow the claim, reject a finding with evidence, or STOP.       |
+======================================================================+
