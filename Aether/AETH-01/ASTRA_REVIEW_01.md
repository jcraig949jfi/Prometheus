# ASTRA INDEPENDENT REVIEW -- AETHER AETH-01

Author: Augment Agent / Astra, independent adversarial reviewer
Date: 2026-09-20
For: Aether's operator and external reviewers
Status: design review only; no implementation, repair, or campaign authorized

Reviewed design: `5e41c1d679fc52394cbb6efd2f56a41bd8483604`.
Inherited CPU baseline: `2959a7274994130cf86179e6bd2c05ab009e2fae`.
Frozen AETH-00 origin: `3ff4619de167847aa3e4a8f3dfa1775bddef53be`.

## Protocol, evidence, and claim ceiling

This review was performed in two passes. The complete Pass A section below was written to this file BEFORE opening `ADVERSARIAL_ANALYSIS.md` or `DECISIONS.md`. Pass B is appended afterward, without revising the independent record. Source locations refer to the reviewed design commit, not to future repairs. Bare document names below are relative to `Aether/AETH-01/`.

Important limitation on independence: the mandated starting document, `ASTRA_REVIEW_PACKET.md`, itself summarizes resident decisions, concerns, and proposed controls. Core documents also contain resident arguments and references to the withheld files. Pass A is independent derivation with those exposures, NOT a fully blinded experiment. Findings already advertised in the index must not be counted as newly discovered merely because they were derived again. This session also contains an earlier AETH-00 review; independence here is from the resident AETH-01 self-review, not from that prior engineering discussion.

Read in Pass A: all nine requested core documents; the frozen `Aether/AETHER_SPEC.md`; `Aether/production/aeth00.py`; AETH-00A/B receipts; production-conformance, production-differential, and statistical-diagnostic test material. No other Prometheus engine was inspected. Two read-only review subagents were restricted to the same permitted Aether documents and prohibited from opening the withheld files. Their arguments were checked against the specification before inclusion.

No simulator or test suite was run for this review. Numerical examples below are deductions from the written rules, not experimental results. The 85-test / 100,000-case history is a RECEIPT-REPORTED result, not an independently reproduced measurement. Only this review file is to be committed.

# PASS A -- independent record

## Reconstructed model: what Candidate 1 actually is

Candidate 1 is a synchronous, externally driven, typed lattice transducer. Four indefinitely retained bytes configure each site's outward write; a fifth byte gates execution and carries a saturating resource balance. There is no material vacancy, mortality operation, particle continuity, or state-maintenance requirement. Starvation disables emission, not storage. Local state changes can reconfigure later routing and emission.

The one-opcode description understates the host law. It contains an energy threshold comparison, field-dependent instruction dispatch, `min`-limited donation, maximum-priority selection, saturation, floor-limited decay, and two externally keyed stochastic-looking processes. These are substantial computational affordances even without an explicit branch instruction. Neither computational universality nor its impossibility follows from the opcode count.

Mutation is an error on a SUCCESSFUL incoming template operation. It is not background mutation of matter, nor a random walk on the recipient's previous byte. Resource inflow is assigned directly to every site by an external schedule; a recipient need not construct harvesting machinery to receive it. The global clock, absolute coordinates, and seed jointly specify part of the environment even though they are not ordinary lattice bytes.

Construction of byte values is built into WRITE. Construction of a new region's capacity to construct further regions is a DIFFERENT claim. AETH-01 currently conflates these levels in its proposed evidence ladder.

## STOP-SHIP

These prevent freezing the packet as written. They are not claims that a particular implementation is already defective: AETH-01 has no implementation.

### S01 -- The mandatory energy identity contradicts the transition law

**Class: semantic defect; proven by counterexample.**

`PHYSICS_SPEC_DRAFT.md:87-107,151-184` subtracts all transfer attempts and adds actual credited transfers, then subtracts the losses and overflow AGAIN. `REQUIREMENTS.md:48-49` mandates this identity on every generated case. `OBSERVATORY.md:60-70` incorrectly says a discrepancy necessarily means an implementation/instrumentation defect.

Take two neighboring donors, each with energy 2, WRITE_COST 1, payload 1, both targeting an empty receiver's energy. Disable maintenance and replenishment. Each donor pays 1 execution plus 1 transfer. One transfer wins. Final energies are 0, 0, 1: total **1**. The printed identity predicts `4 - 2 - 2 + 1 - 1 = 0`, whichever donor wins.

Let A be attempted transfers, C actual accepted transfer credits, L losing amounts, O transfer overflow, X execution expenditure, D actual maintenance, and R actual accepted replenishment. Then `A = C + L + O`. Either `E_next = E - X - A + C - D + R` OR `E_next = E - X - L - O - D + R` is the accounting identity. Combining the two double-counts sinks. This is a proposed correction for discussion, not an edited specification.

The exhaustive destruction list also omits execution expenditure. Replenishment saturation needs an explicit gross-versus-accepted convention; maintenance needs an identifiable trace amount/reason, not an implied event hidden among debits. A correct simulator must not be bent to pass the current equation.

### S02 -- The packet is not formally complete over its declared parameter domain

**Class: semantic defects; proven.**

- `PHYSICS_SPEC_DRAFT.md:27-34` declares two `uint32` numerators with allowed endpoint `2^32`. That endpoint is not representable. Widen the representation or explicitly encode probability one; wrapping it to zero is a different universe.
- `EXPERIMENTS.md:57-70` permits zones with DIFFERENT run parameters. The physics has five GLOBAL scalars, and its complete replay tuple has no parameter map (`PHYSICS_SPEC_DRAFT.md:12-38,219-227`). Initial-byte heterogeneity is legal; spatially varying laws are not this specification. Do not quietly implement the latter in the runner.
- The transition's local debit/credit arithmetic is otherwise reasonably determinate: source debits are computed from S[t], before incoming credits, and a self-transfer pays its execution cost. Preserve that ordering explicitly when repairing the accounting.

### S03 -- The central accessibility justification describes a different mutation process

**Class: substrate-design justification and scientific-identifiability defects; exact mechanism mismatch.**

`PHYSICS_SPEC_DRAFT.md:243-275` asserts an at-most-eight-event path between bytes, generally mild changes, approximately one-in-eight activation, and neutral drift of dormant machinery. The actual rule at lines 114-126 mutates the winning SOURCE PAYLOAD.

Counterexample: a fixed payload-0 writer repeatedly overwrites a starved neighbor's opcode. The possible stored values are only 0 and the eight powers of two. The recipient never reaches 3, however many such events occur. A completely WRITE-free world never mutates its four instruction/data fields at all, even at maximal MUT_NUMER and with continuing energy rain. The exception for a rare spontaneous activating mutation in `EXPERIMENTS.md:38-45` is therefore false.

Under uniform mutation-bit sampling, activation from donor payload p has probability `(1-mu)*1[p=1] + (mu/8)*1[HammingDistance(p,1)=1]`. It is not determined by the recipient's old opcode. Every mutation of an incoming 1 destroys that activation; many donor values cannot produce 1 in one event.

Multi-bit variation can accumulate if mutated values become future source payloads along suitable paths. That requires pre-existing or constructed routing and copying opportunities; it is precisely the accessibility question, not something proved by an eight-bit alphabet. No claim of impossible constructor evolution follows, but the current affirmative rationale fails. Before freezing Candidate 1 as primordial physics, choose whether mutation is intentionally reproduction-coupled and replace the reachability argument with one about this actual transition graph. Do not silently add background mutation to rescue the prose.

### S04 -- The proposed claim ladder can certify a relay as recursive construction

**Class: scientific-identifiability defect, with ontology embedded in the observer.**

`HEREDITY_REQUIREMENTS.md:9-33` requires resemblance before causal construction, then promotes construction of bytes to recursive construction when the receiving region writes onward.

Consider three preconfigured, adequately powered WRITE cells A -> B -> C, all routing to the next cell's payload. A changes B's payload; next tick B changes C's payload. Source perturbations change downstream values, unrelated controls do not, and the trace has the required winning edges. A mutation at A -> B followed by faithful B -> C copying can also supply the stipulated new-then-propagated difference. Yet neither B's nor C's ability to construct was built: they were already forwarding machinery. This is ordinary signal transmission through an initial-condition scaffold, not evidence that a constructor recursively produced constructor capability.

Additional restrictions preselect the result:

- A strict resemblance prerequisite excludes dissimilar A -> B -> A construction, although byte resemblance is neither necessary nor sufficient for causal construction.
- Requiring a Mu-origin event for heritable variation excludes standing variation and variants of spatial, timing, or energy organization. Origin of a difference and transmission of a difference must be separate propositions.
- The resource-flow case at lines 49-52 disallows resource-mediated evidence from tiers 2-4 by field type, despite the requirements admitting that energy patterns might carry heredity.
- Parent-intact versus parent-consumed at line 46 is not a universal movement/reproduction discriminator: translation can leave residue, while fission or sacrificial construction consumes a parent. Every cell is always occupied, so unspecified "occupancy accounting" cannot supply missing individuality.

Require construction of the relevant downstream CAPACITY, not merely its current value. Keep resemblance, construction, recurrence, transmissible variation, and individuality as separable evidence axes. No detector implementation is required now, but this requirements error must not be frozen into the future observer.

### S05 -- The proposed GPU stopping rule changes the sampled science

**Class: scientific-identifiability defect and invalid engineering guarantee.**

`GPU_RUNPOD.md:36-43` calls finite low-activity/low-change windows proof that a world cannot change again. A starved writer can later receive replenishment. A same-value winner can later mutate. A currently losing writer can win under a later tick's priority field. Near-zero is weaker still. Even an all-inert world can have changing ENERGY under replenishment/decay.

These rules preferentially erase long quiescent intervals and rare reactivations, exactly the behavior the METASTABLE label is supposed to retain. A finite observation window is not an absorbing-state certificate. Stop only with a certificate for the stated observable/subspace, or label the run right-censored and audit stopped trajectories. Lattice-byte hash recurrence also is not recurrence of the full replay state: tick changes the next transition (`HABITABILITY.md:21-22,43-49`).

### S06 -- Resource overlays can launder seeded controls into spontaneous evidence

**Class: provenance/semantic defect; direct requirements contradiction.**

`EXPERIMENTS.md:47-55` lets resource-rich/poor regimes wrap "any of the above," including the seeded copier. Lines 66-71 then declare regimes 5-7 spontaneous and claim they contain no hand-authored functional pattern. A seeded copier with altered energy satisfies both recipes.

Origin class must compose from the COMPLETE initialization ancestry and survive all resource/environment overlays. A fingerprint match is a useful investigation trigger, not a provenance proof: perturbations evade exact fingerprints, while true reinvention can match one. Repair this before constructing campaign metadata or using any spontaneous-origin label.

## MAJOR

### M01 -- Modulo five removes an inherited neutral subspace

**Class: substrate-design change, not a harmless extra field.**

`arg1 mod 5` is explicit, but it is not an additive preservation of AETH-00's field semantics (`PHYSICS_SPEC_DRAFT.md:20-23,46-54`). For example, arg1=4 changes from opcode overwrite to energy transfer. More generally, flipping any one bit changes the residue modulo five because no power of two is divisible by five. The upper-six-bit neutrality of the old mod-four selector disappears. Uniform bytes also select opcode with 52 encodings and every other field with 51.

These are small encoding decisions with large mutational effects: a selector change can cross from state templating to resource donation. A payload high-bit flip can radically change a donation, not merely perturb a phenotype slightly. Audit encoding-to-behavior adjacency, conditional on actual incoming-write opportunities. The huge inert opcode class is a storage equivalence class, not automatically an accessible neutral network.

### M02 -- Memory is immortal; the economics charge activity and reserves, not persistence

**Class: substrate-design mismatch with the scientific economic narrative.**

`ECONOMICS.md:13-19,68-92` suggests maintenance makes persistent state worth paying for. It does not: the four template bytes persist at zero energy under every maintenance setting. No resource payment retains an opcode, operand, payload, or inert boundary. All sites already exist, and starvation does not remove any of them. Dormant unfinished structures can survive indefinitely, but without incoming writes they also do not search.

This is not automatically a reason to add decay. It is a reason not to describe energy bookkeeping as costly informational survival. A pattern can appear resurrected by rain without having maintained itself. The cheapest control is a matched configuration with emissions disabled: if its alleged persistent information survives equally well, persistence is not evidence of active maintenance.

Maintenance also taxes occupied ENERGY SITES rather than units: merging two positive reserves can reduce future total floor-limited maintenance, until the 255 cap or transfer losses dominate. Thus compact hoarding can be favored, contrary to treating hoarding as a generally losing default. This creates a specific condensation economy, not an unspecified metabolism.

### M03 -- What the economy actually rewards before sophisticated organization

**Class: substrate-design hypotheses, with several exact incentives.**

- **Broadcasting:** costs are paid on attempts, including same-value writes and losers. Useful computation earns no direct resource return; local overwriting, activation, routing, and donor control are the available ways to alter subsequent influence. A self-replenished broadcaster is the appropriate boring baseline, not evidence of metabolism.
- **Passive persistence/dead-matter advantage:** inert bytes never pay execution cost and never disappear from starvation. A zero-energy record is informationally as persistent as a rich record unless somebody overwrites it. Energy abundance is not itself reproductive success.
- **Hoarding/spatial monopolies:** compact reserves can save per-site maintenance; saturation limits them. Overwriting a neighbor's control fields may monopolize an externally replenished site or redirect its donations. Geographic resource capture need not imply autonomous organization.
- **Parasitism:** transfer is donor-controlled delivery, not a recipient's pull/steal operation. An incoming credit cannot directly drain its recipient. Taking an inert reservoir requires reconfiguring its owner into an appropriate donor. A passive recipient is not established as a parasite merely by receiving energy, nor does absence of structural-copy edges prove absence of beneficial contribution.
- **Arbitration/jamming:** at WRITE_COST=1 a donor with energy 1 can emit a zero-amount energy proposal. If it beats a donor offering 254, the receiver gets zero and the other donor loses 254 plus execution cost. With WRITE_COST=0 such zero-budget contestants can persist without energy. Exact outcome; frequency and evolutionary exploitability are unmeasured. Fair win COUNTS can coexist with extremely asymmetric useful delivery and destruction.
- **Sacrificial losers:** unconditional debit burns resources regardless of selection. For k equal positive transfers without saturation, only one amount reaches the target; the other k-1 are destroyed. This selects against convergent provision and may penalize cooperation most strongly precisely when several partners support one site.
- **Synchronization:** credit arrives after snapshot eligibility; maintenance precedes rain; new credit cannot finance same-tick execution. These phases impose latency, pulse thresholds, and shared timing even without an explicit timer opcode.

Regime A's global bound on total WRITE attempts, `initial_total_energy / WRITE_COST` for positive cost and no inflow, has NO redistribution exception. Regime B has direct external endowments: recipients need not win transfers to obtain rain. Its long-run mean execution density is bounded above by mean accepted inflow per site divided by WRITE_COST, before other sinks. For the proposed nominal inflow 0.001 times 4-16 and cost 1, that upper bound is only 0.004-0.016 after initial reserves cease to matter. This is a bound, not a measured outcome.

The economy is a hidden ecological filter, even without a scalar fitness variable. Its filters favor particular occupation, routing, contention, and storage strategies. Claims of adaptive organization need evidence of transmissible, causally beneficial organization beyond those baselines.

### M04 -- Mean inflow is not a sufficient habitability axis

**Class: experimental-design defect; exact counterexample.**

`HABITABILITY.md:64-67` combines replenishment probability and amount into their product, despite the economics depending on burstiness. With initial energy zero, maintenance 2, WRITE_COST 3, and no incoming transfers, probability 1/2 with amount 2 never raises a site above energy 2: it cannot emit. Probability 1/16 with amount 16 permits emission after a replenishment. Both have mean nominal inflow 1 per tick.

Sweep probability and amount separately, or explicitly hold one fixed and limit the claim. Include thresholds and saturation, not just mean supply. Every proposed ordinary sweep size is even and a power of two; that preserves the square torus's bipartite structure and short wraparound paths. Odd and rectangular comparison worlds are needed before generalizing phase behavior. Tiny worlds can be semantically meaningful while scientifically dominated by topology.

Uniform random soup is not representation-neutral. At 1/256 opcode density, a 4x4 soup has probability `(255/256)^16`, about 94%, of containing no writer at initialization; its instruction fields are then permanently frozen under this mutation law. Separate initial absence of any mutational machinery from extinction of machinery that existed. Finite, fixed-size worlds also cannot establish literal open-endedness; expressibility and search accessibility must be stated at a specified scale and horizon.

### M05 -- Winner provenance is not the causal graph of construction

**Class: scientific-identifiability and data-preservation defects.**

`OBSERVATORY.md:141-153` follows winning value suppliers. A full causal account also needs the opcode/arguments enabling each event, energy suppliers and thresholds, losing proposals that blocked alternatives, destruction/saturation, mutation, external inflow, and untouched initial scaffolding. Same-value overwrites are not automatically necessary construction events. Redundant suppliers defeat single-source necessity tests. Resource-mediated effects cannot be dismissed simply because their edges are not structural copies.

An arbitrary source-bit perturbation causing Hamming divergence is not sufficient attribution: it may destroy routing or energy rather than alter transmitted information. An unrelated cell with similar surface statistics is often a weak control because it lacks comparable causal opportunity. Use content-versus-enabling perturbations, source/channel-specific blocking, rescue, and small joint interventions where redundancy is plausible. Hold exogenous forcing fixed for the first paired contrast, then test dependence on alternative forcing separately.

Preserve old/new values, source state dependencies, all contenders, winning pre-mutation payload, post-mutation value, clipped amounts, event identities with tick/field, and the intervention definition/result. These can be reconstructed in tiny deterministic replays; they need not become permanent per-cell ancestry tags. Preserve exact genesis/checkpoints, source revision, initialization ancestry, parameter provenance, and analysis-selection history. A promoted N-tick window alone cannot identify an ancestor before that window. Recorded genesis permits replay, but that is different from the promise of answering every later mechanism question without rerunning anything (`HEREDITY_REQUIREMENTS.md:55-65,92-104`).

### M06 -- The scout funnel can select artifacts and hide its own false negatives

**Class: scientific-identifiability and instrumentation-dependency defects.**

Scouts have tier-1 counters, but STRUCTURED requires tier-2 compression, MOBILE requires tier-2 component tracks, and CHAOTIC requires perturbations deferred to deepen/verify (`OBSERVATORY.md:155-177`; `HABITABILITY.md:33-53`; `GPU_RUNPOD.md:60-79`). These labels cannot all honestly drive promotion before their inputs exist. Unmeasured is not negative. PERIODIC and UNKNOWN need an explicit audit route too.

CPU/GPU verification only of promoted worlds cannot detect a GPU error that makes interesting worlds look dead. An adaptive majority-label grid also misses rare behaviors and islands between sampled points: with eight independent seeds, a 1%-frequency event is missed with probability `0.99^8`, about 92%. This is not a demand that nature produce an event; it is a limitation on what the sampling policy can exclude.

Before scientific use, audit a randomized share of rejected/stopped worlds and unrefined parameter regions, verify representative GPU negatives, record every denominator and censoring reason, and use fresh confirmatory seeds after selecting thresholds/regions. Preserve raw metrics and uncertainty; do not make label changes the only discovery channel. Labels are operational summaries, not physical phase proofs.

### M07 -- RNG marginal correctness is not independence of the environment

**Class: unsupported scientific/numerical assurance, not a demonstrated practical RNG failure.**

`PHYSICS_SPEC_DRAFT.md:144-149` says the three domains never share input material in a way that correlates outcomes. Distinct constants do not prove that. All outputs are deterministic functions of a single 64-bit seed, time, and coordinates. For example, let `g0=M(seed XOR MUT_DOMAIN_CONST)` and `r0=M(seed XOR REPLENISH_DOMAIN_CONST)`. At the same cell, choosing `t_r = t_mu XOR g0 XOR r0` makes the mutation and replenishment chains' next internal word equal; then `Mu_key = M(Rho_key XOR field)` at those respective ticks. This is an exact structural relation when the selected ticks are valid, not evidence of harmful short-run correlation. The matching tick may be far outside any campaign.

There is also a POSITIVE result: for a fixed opportunity and uniform 64-bit seed, the bijective chain gives a uniform Mu key. Its high-word trigger and low-three-bit index are then exactly independent, and the marginal trigger probability is exact after fixing the numerator representation. That does not establish independence along a realized trajectory, across neighboring cells, or conditional on state-selected successful writes.

Qualify claims accordingly. Test the actual fixed-seed/time/position exposure process, cross-domain associations, and value-weighted delivery. Preserve absolute position and forcing context for transplantation controls. Reusing the exact arbitration primitive preserves tie freedom, not scientific neutrality under newly attached economic stakes.

### M08 -- The heredity/novelty observatory has an ontology of its own

**Class: scientific-identifiability defect; not solved by keeping metadata out of physics.**

Grouping active/similar cells, matching spatial overlap, using centroids, and assigning stable component identities can manufacture individuality from an observer's scale/window. In a torus, naive centroids also jump at wrap boundaries. Neither component tracking nor an energy recipient's passivity establishes organism, lineage, parasite, or mutualist status.

The novelty assay sensibly refuses to equate non-recognition with novelty. Its remaining danger is description-induced unfamiliarity: removing opcode terminology can conceal an ordinary relay, threshold network, or template copier rather than reveal an alien mechanism. Preserve executable causal examples and intervention responses, not only human/model descriptions. Use multiple faithful descriptions, calibration mechanisms with matched obscurity and complexity, and familiar mechanistic models that make falsifiable predictions. Agreement among frontier models is not independent mechanistic evidence by itself. This assay stays deferred.

### M09 -- Engineering inheritance is being promoted into physics selection evidence

**Class: engineering/science boundary error.**

The frozen parent explicitly excludes suitable primordial physics, accessibility, open-endedness, and GPU correctness (`Aether/AETHER_SPEC.md:23-39`). Candidate selection nevertheless calls GPU viability "proven" and inherited trust nearly free (`PHYSICS_CANDIDATES.md:185-216`). The inspected production code is CPU gather only, as its receipt correctly says. Gather-shaped bounded locality is a strong feasibility argument, NOT measured GPU qualification.

What is legitimately inherited: exact integer mixing and tie freedom, snapshot discipline, physical-source identity, alias handling, byte comparison, and useful differential/mutant-testing methods. What is not: neutrality, energy/mutation semantics, field-selector topology, instrument completeness, GPU performance, or valid scientific claim definitions.

The old trace-on/off tests establish noninterference, not truth or causal completeness of the trace. Production computes `proposal_emitted` through a separate decoding path, and the inspected trace tests largely check event presence/flags and output equality. An independent event ledger comparison is needed for an AETH-01 instrument used as evidence. The 100,000-case test mostly compares one-step small-world transitions; it is not a bound on all campaign failures or an economic-scientific qualification.

## Ontology audit: working backward from the intended claims

| Intended phenomenon | Status under the proposed physics and observer | What would have to be demonstrated |
|---|---|---|
| Persistent organization | Byte retention is structurally privileged/free; maintained dynamic organization could emerge but is observationally ambiguous. | Causal resistance/recovery/maintenance beyond an emission-disabled or untouched-state baseline; distinguish memory from resource turnover. |
| Causal construction | Writing a neighbor's byte is a supplied primitive. Construction of an organized capacity is not. | Attribute the relevant capacity's enabling state and dependencies, not just the last value written. |
| Recursive construction | The present definition is easy for a preconfigured forwarding chain to satisfy. Stronger recursion is unestablished, not proved impossible. | A constructed instance acquires and transmits construction capability, with inherited environment and initial circuitry controlled. |
| Heritable variation | Copy errors structurally privilege one channel; standing, spatial, and energy variants are observer-restricted. | Separate origination, retention, transmission, functional consequence, and environmental re-creation. |
| Individuality | No organism ID is installed, but fixed site boundaries exist and tracking installs candidate individual boundaries. | Robust causal cohesion/independence or a clearly bounded operational alternative across segmentation choices; allow consortia and destructive reproduction. |
| Adaptive organization | No direct task score, but a strong ecological filter is installed. Energy possession or survival of bytes does not establish adaptation. | Transmissible differences that causally improve a declared physical performance under controlled environmental contrasts, not just residence in a lucky forcing field. |
| Novel mechanism | Neither guaranteed nor excluded by a single active opcode; familiar transducer operations are already supplied. | A mechanism-level result surviving causal tests and predictive familiar alternatives, not merely unfamiliar imagery or model vocabulary. |

Nothing here proves genuinely novel organization impossible. Several phenomena are made easy to describe while the stronger intended claims remain untested. The observer smuggles in a template-copy/Mu/parent-preserving heredity ontology more strongly than the bare absence of organism IDs removes one.

## Accessibility audit: expressible is not reachable

Useful paths need a source with a suitable payload, a route to the right field, sufficient energy, survival of overwrite competition, and a way for changed values to become future sources. Installing opcode 1 without appropriate arguments/payload can create a resource-burning or destructive broadcaster rather than an intermediate benefit. Coordinated byte changes are not made likely by being representable.

Partial machinery can survive as free stored information. Environmental circuitry can therefore hold unfinished computation, but it may also supply most of the claimed constructor. Cooperation can reconfigure donors and share values; lossy convergent transfer and activation-before-completion can create economic valleys. The actual rates, viable intermediates, and neutral paths require a dependency-conditioned graph or small controlled path census, not a genome-alphabet analogy.

Conversely, the absence of a branch opcode does not prove conditional strategies impossible: energy thresholds and reconfigurable enable/routing state already provide conditional dynamics. Do not add a familiar instruction set merely because no witness has yet been constructed. First ask which precise affordance is missing, and whether a bounded witness or obstruction supports that claim.

## Observatory audit: cheapest discriminating interventions

The safest observables are correctly defined byte transitions, proposal identities, attempted/accepted/lost energy amounts, and complete replay identities. They still need independent instrument validation. The most dangerous are labels that promote persistence, flux, component identity, or a winning-edge chain into organization, benefit, or heredity.

| False-positive channel | Cheapest discriminating intervention or negative fixture |
|---|---|
| Untouched bytes called self-maintenance | Matched configuration with emission disabled and identical forcing; compare information persistence, not just energy. |
| Forwarded payload called recursively constructed machinery | Preconfigured A -> B -> C relay negative; perturb/reset the recipient's inherited enabling configuration separately from its copied payload. |
| Environmental completion credited to a parent | Preserve energy/input statistics while independently varying source content, initial scaffold, and mutation; include rescue and common-forcing controls. |
| Renewed Mu or resource forcing called inherited variation | After a variant exists, test transmission with mutation disabled and controlled resource supply; compare different variants in the same background. |
| Translation, fission, or tracker overlap called birth | Compare torus-aware displacement and causal capacity counts; test a residue-leaving traveler and a parent-consuming multi-successor constructor. Neither parent survival nor a component ID decides the result. |
| Rainfall luck or jamming called adaptive cooperation | Exchange internal configurations across positions/forcing realizations, separate donation from control-field reprogramming, and measure delivered benefit versus energy destroyed. |
| Divergence called causal construction | Content-only versus enabling-state interventions, sham controls with comparable causal opportunity, and small joint-source ablations/rescue for redundancy. |
| Unfamiliar description called novel mechanism | Known relay/threshold/template controls rendered with matched obfuscation, multiple faithful descriptions, and interventions that discriminate predictive mechanistic accounts. |

These are proposed instruments/controls, not completed experiments and not assertions that emergence must occur.

## MINOR

### N01 -- Performance and scope arithmetic need correction

`GPU_RUNPOD.md:50-52` uses the reported roughly 300,000 cell-steps/s baseline to call a 32x32, few-thousand-tick replay a fraction of a second. At 3,000 ticks the baseline implies about **10.24 seconds**, before the new physics or forensic overhead. The 5-7-point five-axis grid at eight seeds already means 25,000-134,456 worlds before refinements and controls. These are arithmetic estimates, not fresh benchmarks. Counters involving histograms, compression, or distinct tuples are not automatically negligible GPU overhead. Profile before making budget commitments; no optimization is requested here.

### N02 -- Some asserted examples are impossible or unmeasured

`HABITABILITY.md:44` offers "every proposal loses" as an active frozen example; every nonempty contest has a winner. Four neighbors can also update all four non-energy fields of a center simultaneously, contrary to the claim that any coherent tuple necessarily accumulates over multiple ticks (`PHYSICS_SPEC_DRAFT.md:277-286`). Multi-source construction is possible; sequential partial construction is not structurally forced.

`test_production_differential.py:81-87` calls its `(row+col) mod 4` 4x4 fixture dense four-way contention. Its direction pattern actually supplies at most two incoming competitors per target. A separate full four-way conformance fixture DOES exist, so this is coverage-description inflation, not evidence that four-way arbitration is untested.

### N03 -- Operational metric definitions are still drafts

Freeze measurement windows, field selections, zero-energy Gini conventions, normalization/nulls, and label thresholds before a campaign, not after seeing patterns. Specify whether change_rate counts energy settlement/replenishment or only winning template changes; the inherited `stored_bits_changed` event alone does not settle that question. Global entropy/compressibility/autocorrelation cannot by themselves establish resemblance between two particular regions. A diffusion null is not automatically appropriate to a non-diffusive copying system.

### N04 -- The three candidates are not equally specified

Candidates 2 and 3 are informative families, not complete rival universes: exact reaction catalog, rates/event scheduling, collision/binding law, and related numeric choices remain open. Do not call them fully specified or infer their scientific inferiority from this asymmetry. Candidate 1's typo-level issues and implementation costs should not be mixed with this larger selection uncertainty.

## CANDIDATE COMPARISON

### Strongest argument NOT to build Candidate 1 at all

The selected physics may be a sunk-cost extension of a specimen explicitly declared disposable. Its affirmative story assumes cheap neutral search of dormant matter, costly informational persistence, and constructor recursion, while the actual law supplies copy-dependent mutation, immortal inactive information, externally allocated execution budgets, and ready-made forwarding. A long campaign could rediscover communication/templating circuits in a free persistent medium and misread that as evidence for escaping representation-induced evolutionary barriers. It would be impeccably replayable and scientifically off-target.

This objection succeeds against building the CURRENT PACKET as a justified primordial substrate. It does not yet prove that the repaired law is scientifically useless. Minimum evidence that would reverse the stronger "do not build at all" judgment: (1) a corrected, honest mechanism-level contract; (2) a bounded analysis/witness of an accessible useful reconfiguration path under the ACTUAL copy-error and energy rules, with its initial/environmental assistance itemized; (3) a relay negative and a constructed-capacity positive that the intended evidence standard can distinguish. A seeded witness establishes expressibility/instrument operation only, never spontaneous origin. Failure of a prespecified bounded search is a bound on that search, not a universal impossibility theorem.

If the intended question really requires dormant matter to vary independently or memory to require active upkeep, Candidate 1 needs an explicit PRIMARY-PHYSICS redesign. Do not retrofit those mechanisms merely to make the current narrative true.

### Strongest argument FOR Candidate 1

Candidate 1 offers a small, exact, inspectable causal transducer with bounded-degree interactions, cheap counterfactual replay, and a plausible atomics-free GPU mapping. That makes it the lowest-cost way to discover whether claims and instruments survive adversarial tiny fixtures. Familiarity is an advantage for falsification when acknowledged. The explicit template primitive also gives unusually clear value-transport evidence, provided it is not mistaken for evidence of autonomous constructor production.

Those are arguments for a LIMITED, REPLACEABLE experiment after repair, not for primordial neutrality. The reused test method is stronger evidence than the reused ontology.

### Actual discriminators among the families

- **Candidate 2:** preferable if the scientific target is distributed catalytic/process heredity without a built-in template channel, and resource transformations should participate in the same state ontology. Its catalog may hard-code attractors; that risk is real but no more automatically disqualifying than Candidate 1's chosen templating/threshold/economic rules. The claim that exact asynchronous local dynamics necessarily require one global serial priority queue is too strong: independent or causally separated events can in principle be parallelized, though exact scheduling and conflict handling are harder. Approximate dynamics can be exactly replayable under their OWN specified law; reproducibility and fidelity to a continuous-time process are separate questions. This is not a proposal to smuggle an approximation in as exact chemistry.
- **Candidate 3:** preferable if continuity of material, topology of bonds, transport, and assembled boundaries are essential causal questions. It distinguishes physical transport from reconstruction more directly, but installs particle/bond ontology and may reward crystallization or jamming. It demands many more unspecified rules and more engineering before equally sharp falsification is possible.
- **Candidate 1:** preferable if the next question is whether cheaply replayable local reconfiguration plus explicit resource gating supports distinguishable constructed capacities through measured accessible paths. It is not preferable merely because its familiar implementation is already comfortable.

No evidence here establishes Candidate 2 or 3 as scientifically superior in general. The next decision should turn on these discriminators and small falsifiers, not on a vote for the strangest terminology or the smallest opcode count.

## MINIMUM REPAIR

1. **Repair the contract, not code:** choose one energy ledger, define saturation/maintenance events, fix probability-one representation, and restrict or separately specify heterogeneous parameters. Obtain independent hand-worked boundary cases before implementation.
2. **Replace the accessibility/economics narrative with the actual mechanism:** explicitly choose copy-coupled mutation and free informational retention, or reject those choices. Audit modulo-five behavioral adjacency and conditional mutation opportunities. Do not silently change the physics to obtain attractive results.
3. **Repair the claim contract:** distinguish byte transport from construction of capacity; separate resemblance from causation, origin from inheritance, resource organization from instruction-field copying, and individuality from tracking. Require the preconfigured-relay negative and scaffold-aware attribution.
4. **Repair selection/provenance rules before campaign tooling:** inherit seed/control origin through overlays; remove uncertified absorption claims; resolve metric-tier dependencies; reserve a negative/rejected-world audit path and independent confirmation samples.
5. **Preserve replay and intervention sufficiency:** typed event meanings and actual amounts, genesis/configuration ancestry, enabling/context state or its exact replay source, and selection history. Retain the honest CPU-only inheritance ceiling. Then adjudicate the small kill experiments below before deciding on a production AETH-01 implementation.

## DO NOT REPAIR YET

- Do not add branching, sensing, resource harvesting, literal movement, reproduction, protected genomes, or background mutation just because the present stories fail. Each would change the scientific question and accessibility landscape.
- Do not erase inert states, smooth mutation cliffs, refund losing transfers, prohibit zero-amount transfers, or charge informational storage merely to make life-like behavior easier. First expose their effects as explicit variables/controls. Some may later justify redesign; none should be silently optimized away.
- Do not redesign the hash solely because deterministic forcing is familiar or not perfectly neutral. First distinguish a measured short-run defect from a general non-independence caveat. Exactness remains valuable.
- Do not build a full heredity detector, novelty assay, GPU engine, or broad habitability sweep to resolve questions already falsifiable by a hand fixture or bounded path analysis.
- Do not treat synchronous clocks, toroidal geometry, or even-sized worlds as universal physics. Keep them as declared variants whose comparative effects remain empirical.

## KILL EXPERIMENTS

These are proposed next-step falsifiers, not executed work. Predeclare resources/horizons and preserve negative outcomes. None tests whether spontaneous emergence "passes."

| ID | Smallest useful experiment/check | Assumption falsified / decision on failure |
|---|---|---|
| K1 | Hand ledger for execution alone, two competing donors, overflow, self-transfer, maintenance floor, and saturated replenishment. | Already falsifies the printed accounting identity. Any repaired discrepancy blocks implementation. |
| K2 | Exact conditional mutation graph: fixed donor payload, repeated overwrite, all-inert world, and the 256 selector bytes with one-bit edges. | Falsifies autonomous dormant drift and unconditional eight-event reachability. Record opportunity constraints; choose copy-coupled search intentionally or redesign. |
| K3 | Preconfigured A -> B -> C relay versus a fixture where the recipient's ability to produce a further capable recipient actually had to be constructed. Separate payload, enable/routing, energy, and scaffold interventions. | If both receive the same recursive-construction verdict, the claim standard is unusable. If a bounded capability witness is unavailable, report that limitation rather than coding a detector around the relay. |
| K4 | Isolated pulse-budget cell; equal-mean rain pair from M04; two-site reserve pooling; zero-amount versus large-amount transfer contest. | Tests whether proposed economics are predominantly externally driven firing, reserve condensation, and jamming. Separate useful credit, destruction, activity, and informational retention. Do not call a trivial baseline metabolic organization. |
| K5 | Continue a randomized subset of would-be DEAD/FROZEN stops to a fixed horizon; include delayed-rain and same-value-then-mutation fixtures. | Any reactivation refutes the absorption rule. Without certificates, budget-limited stopping becomes censoring, with measured missed-reactivation rates for a declared distribution. |
| K6 | Apply every resource overlay to both seeded control recipes and random recipes; round-trip provenance and genesis. | Any seeded descendant labeled spontaneous blocks campaign reporting. Structural fingerprints do not substitute for this check. |
| K7 | Tiny audit of oracle/trace agreement and scout selection, including intentionally suppressed activity or missing event records; verify randomly selected negatives as well as positives. | Tests whether the instrumentation and funnel can hide their own defects. Declare coverage and acceptance before use. |
| K8 | Bounded path/assembly witness with viable or dormant intermediates, matched isolated versus scaffolded conditions, plus position/time/odd-size transplants. | Tests accessibility and dependence on inherited circuitry/forcing/topology, not merely final expressibility. A null is scoped to the prespecified path class and budget; it does not license adding convenient operations. |

### Pass A provisional verdict

**PROCEED_TO_REPAIR**, meaning repair and adjudicate the DESIGN PACKET first, not proceed to implementation. There are decisive semantic and inference failures, but no demonstrated impossibility that warrants an immediate candidate switch. Candidate 1 remains only a provisional cheapest falsification platform. If the intended scientific question rejects copy-coupled search or free information storage, escalate to REDESIGN_PRIMARY_PHYSICS explicitly rather than cosmetically repairing the narrative.

### Pass A answer: the single most dangerous misunderstanding

The designers appear to be reasoning about autonomous mutation-and-selection of dormant organization when the specified universe mutates only the writable footprint of already functioning template traffic and stores untouched information for free. That makes inherited/environmental circuitry both the prerequisite for search and a ready-made supplier of apparent construction. A value-lineage graph can then credit "recursive constructors" for capabilities the world already supplied. Perfect implementation would make this misidentification more persuasive, not less wrong.

END OF PASS A -- recorded before the two withheld resident documents were opened.

# PASS B -- comparison with the resident model

## Pass separation and integrity

Only after recording Pass A were `ADVERSARIAL_ANALYSIS.md` (22 items) and `DECISIONS.md` (14 provisional decisions) opened. The pre-Pass-B artifact was 47,351 bytes; its SHA-256 was `70439D5122E6B1064818573692059E90C524C01CC636524699F4DE61790159A1`. That entire byte prefix is retained. This establishes which written claims preceded the withheld documents; it does not remove the index/core-document exposure disclosed above.

The resident review names many relevant risk categories and is often appropriately cautious. Its central weakness is that its controls frequently assume the semantic model is already correct. Consequently, it misses contradictions between that model and the actual law, and sometimes proposes a control that cannot produce the purported null process.

## WHAT SONNET MISSED

The clearest distinct contributions are not additional warnings that "a detector could be wrong." They are short counterexamples to specific load-bearing assurances:

1. **A correct transition fails the mandatory energy invariant (S01).** Neither withheld document detects double subtraction of dissipated transfers. The ledger treats the economics as fully specified and the observer treats equation failure as an implementation fault. This is an immediate pre-code stop.
2. **Dormant neutral drift is absent from the specified search process (S03).** The all-inert mutation null in self-analysis #18 reinforces, rather than repairs, the mistaken model. Copy errors can generate new values, but do not grant every stored byte an autonomous Hamming-cube walk.
3. **The field extension destroys selector-level one-bit neutrality (M01).** D-AETH01-02/-08 discuss width, location, arbitration, and economic stakes, but not the modulo-five adjacency change. This is a representation/accessibility change hidden inside an "additive" extension.
4. **The evidence ladder admits pre-existing communication circuitry as constructor recursion (S04).** Generic warnings about environmental parents do not cover a relay where the alleged source genuinely DOES causally change the receiver. The missing question is who constructed the receiver's ability to continue the process.
5. **Apparent absorbing-state optimization deletes possible futures (S05).** The withheld review does not challenge the promised proof of terminal behavior. The error is especially consequential because later CPU verification sees only selected survivors.
6. **Seeded resource overlays have contradictory origin labels (S06).** Contamination is already known, but the concrete classification bug is present in the design recipe itself, not merely a hypothetical script failure or imperfect fingerprint.
7. **One nominal inflow coordinate contains behaviorally different worlds (M04).** The equal-mean pulse counterexample does not require a campaign to invalidate the collapsed axis. D-AETH01-10 calls axis choice provisional but does not identify this non-equivalence.
8. **Energy taxes reserves, not information; fixed per-site maintenance can favor concentration (M02-M03).** The resident recognizes persistence by neglect and initial-energy luck, but does not derive these incentive consequences or notice that Regime B still leaves informational storage free.
9. **Zero-amount transfers have destructive economic effects (M03).** Self-analysis #14 calls them physically inert. Their potential to win while burning another donor's entire offered amount is a different, causally consequential behavior.
10. **The instrumentation funnel has circular prerequisites (M06).** The resident recognizes hidden local activity, but puts the local/compression/intervention instruments after gates that need their outputs. Verification of selected positives alone also leaves false-negative simulator failures unaudited.

Other concrete omissions include the unrepresentable probability-one endpoint, spatial-parameter/replay incompatibility, CPU time arithmetic, and the distinction between trace noninterference and trace accuracy. These are valuable engineering findings but should not be inflated into separate scientific discoveries.

## WHAT SONNET GOT RIGHT

- **Coordinate-dependent arbitration has scientific consequences beyond tie freedom.** Self-analysis #6/#16 and D-AETH01-08 explicitly say so, including the new economic stakes. This concern was already exposed in the initial packet; it is not an Astra-only insight.
- **Persistence, resemblance, and activity are insufficient evidence.** Self-analysis #1/#2/#8/#14 correctly names environmental sources, persistence by neglect, frozen compressibility, and same-value activity. The controls need strengthening, but the distinctions are important.
- **Initial energy, saturation, and dry spells can manufacture apparent robustness or coordination.** Self-analysis #7/#12/#15/#17 correctly motivates matched resource conditions and explicit accounting. The proposed interpretations occasionally overreach, as noted below.
- **Instrumentation and replay require explicit qualification.** Self-analysis #9/#20/#21 and D-AETH01-09 rightly demand full replay parameters, checkpoint round trips, CPU/GPU differential comparison, and trace noninterference. They do not substitute for event truth or representative sampling.
- **Seeded instruments are not spontaneous-origin evidence.** Self-analysis #5 and D-AETH01-12 adopt the correct high-level separation and even acknowledge fingerprint evasion. The overlay contradiction is a failure to carry that rule through composition, not an absence of the principle.
- **Aggregate observables can hide real localized behavior; majority labels hide mixtures.** Self-analysis #19/#22 identifies both risks. Preserve distributions and an independent negative-audit route rather than treating the issue as solved by mentioning a component tracker.
- **The selected ontology, energy width, and maximum transfer loss are deliberate priors.** D-AETH01-01/-02/-05 is candid about them. Keeping alternatives and reversals visible is good practice; an acknowledged prior is nevertheless still a scientific commitment needing a relevant discriminator.
- **No obligation to prefer exotic machinery.** Candidate 3 is rejected mainly for engineering cost, not declared scientifically inferior. Deferral of GPU-side forensics and the refusal to install organisms, tasks, or LLMs inside physics are appropriate for this stage.

## Issue-by-issue comparison

Classification applies to the specific proposition in each row. A broad category being mentioned does not mean its concrete counterexample was found. Conversely, discovering a stronger failure inside a known risk is not a wholly independent discovery. No aggregate "reviewer accuracy" score is inferred from this table.

| Independent issue | Classification | Comparison against resident self-review/ledger |
|---|---|---|
| S01: mandatory balance double-counts losses; sink list omits execution | ASTRA_ONLY | No corresponding finding in the 22 attacks or D-AETH01-05/-06. |
| S02: uint32 cannot represent the permitted probability-one numerator | ASTRA_ONLY | Numerical reproducibility is asserted; this representation conflict is absent. |
| S02: spatial parameter zones are outside the scalar law/replay tuple | ASTRA_ONLY | D-AETH01-06 positively relies on parameter zones; D-AETH01-09 never adds their map. |
| S03: incoming-copy mutation is not resident-byte drift or an unconditional eight-event path | ASTRA_ONLY | D-AETH01-04 discusses byte synthesis and energy exclusion, not the actual opportunity graph. Self-analysis #18 assumes the missing process. |
| Self-analysis #18: an all-inert world supplies a same-mutation-process neutral null | DISAGREEMENT | It supplies zero template mutations. A valid null must match copying/mutation opportunities while removing the selective contrast being tested. |
| S04: preconfigured relay can satisfy recursive-construction criteria | ASTRA_ONLY | #1 tests a spurious parent, but the relay has a genuine causal parent for its DATA. It lacks construction of the onward CAPACITY. |
| S04: resemblance/Mu/parent-preservation restrictions preselect heredity | DISAGREEMENT | D-AETH01-11 acknowledges taxonomy as a prior but defers reconsideration until a detector sees awkward specimens. Logical counterexamples already exist. |
| S05: finite quiet windows are not absorption proofs | ASTRA_ONLY | Not identified; the funnel's early termination is treated as pure savings. |
| S05: lattice recurrence versus full replay-state recurrence | SAME_ISSUE_DEEPER | #3/#4 recognize synchronization/topology; the omitted clock prevents the claimed inference from a repeating lattice alone. |
| S06: seeded controls relabeled through resource overlays | SAME_ISSUE_DEEPER | #5 and D-AETH01-12 know contamination risk, not this exact contradictory recipe. |
| M01: mod-five encoding removes all one-bit-neutral arg1 edges | ASTRA_ONLY | D-AETH01-02/-08 describes a small additive extension; mutation topology is not analyzed. |
| M02: maintenance never charges retention of four template bytes | SAME_ISSUE_DEEPER | #2 knows untouched bytes persist, but the economics still treats Regime B as making informational persistence costly. |
| M02-M03: reserve concentration can reduce maintenance | ASTRA_ONLY | No concentration incentive is derived; hoarding is framed principally as a loss. |
| M03: 100% losing-transfer loss is an arbitrary severity choice | SONNET_ALREADY_FOUND | Explicit in D-AETH01-05 and the index. |
| M03: zero-amount contestants destroy competitors' energy | SAME_ISSUE_DEEPER | #14 notices zero-amount transfers only as activity inflation, and incorrectly calls them physically inert. |
| M03: donation is not recipient extraction; direct rain does not require transfer capture | ASTRA_ONLY | The economic narrative conflates these processes; the self-review does not correct it. |
| M04: equal mean inflow does not identify equivalent regimes | ASTRA_ONLY | D-AETH01-10 questions whether axes are informative, not whether one coordinate collapses distinct threshold behavior. |
| M04: even-torus/initial-writer distribution constrains sampled accessibility | SAME_ISSUE_DEEPER | #4/#13/#19 know topology/inert-majority risks; parity and the absorbing initialization probability sharpen them. |
| M05: winners-only provenance and single perturbations miss enabling, redundant, and initial causes | SAME_ISSUE_DEEPER | #1 and the heredity cases require intervention and environmental attribution; they do not establish sufficiency of the proposed graph/controls. |
| M06: promotion needs measurements unavailable to scouts; positive-only verification misses suppressed worlds | SAME_ISSUE_DEEPER | #19/#22 know false negatives and mixtures; the actual information-flow failure in the funnel is new. |
| M07: positional/economic neutrality requires actual-contest qualification | SONNET_ALREADY_FOUND | #6/#16 and D-AETH01-08 state this clearly. Astra adds delivery/destruction weighting, not the basic warning. |
| M07: separated constants do not prove independent environmental processes | DISAGREEMENT | The formal draft makes an unconditional independence assurance; the ledger does not provide its proof or appropriately scoped evidence. |
| #11: top/bottom bits of Mu are intrinsically suspect under independent uniform-seed sampling | SONNET_CONCERN_OVERRATED | Bijection proves the marginal independence for a fixed opportunity. Dynamic conditioning and within-run/cross-domain behavior remain legitimate open questions. |
| M08: component boundaries/novelty descriptions can impose ontology | SAME_ISSUE_DEEPER | #10 and the novelty requirements correctly warn about invented boundaries and non-recognition. Unsupervised detection and disguised words do not remove the prior. |
| M09: GPU mapping/fitness of the ontology are inherited as proven | DISAGREEMENT | D-AETH01-01 invokes proven GPU mapping; the baseline is CPU-only and explicitly denies scientific substrate qualification. |
| No branch opcode proves a strong conditional-expressivity ceiling | SONNET_CONCERN_OVERRATED | R14's tension is a valid question, not a proved impossibility: thresholded energy and writable control state already supply conditional dynamics. |
| Candidate 2 is necessarily globally serial and replay-hostile | DISAGREEMENT | D-AETH01-01 inherits an overly categorical dismissal. Exact causal scheduling difficulty, parallelism, and replay of an approximate law are separate questions. |
| N01: CPU replay arithmetic and campaign scale | ASTRA_ONLY | D-AETH01-13 names a possible backlog but does not catch the existing order-of-magnitude time error. |
| N02: mandatory multi-tick assembly / all proposals losing / mislabeled dense fixture | ASTRA_ONLY | Concrete narrative/coverage corrections, not new physics results. |
| Full replay tuple, trace noninterference, seeded separation, mixture reporting | SONNET_ALREADY_FOUND | #5/#9/#20/#21/#22 and D-AETH01-09/-12 deserve credit; repair implementation of these principles rather than claiming to invent them. |

## Additional Pass B findings and qualifications

### B01 -- Several proposed discriminating controls do not discriminate as stated

These are **SAME_ISSUE_DEEPER**, except where specifically classified above:

- **Self-analysis #1:** an unaffected child after a parent perturbation does not prove "environment did it." The perturbation may be too late, miss the causal field, or leave a redundant pathway. This is the M05 timing/redundancy problem, not a reason to abandon intervention.
- **#2:** zero winning-write rows inside a short window cannot falsify ANY causal claim; construction may precede the window, and resource/enabling causes need not appear as structural-copy winners there.
- **#3/#6:** phase randomization and coordinate transplants are useful, but a genuinely functioning mechanism can depend on its forcing environment. Survival of the manipulation is not a definition of genuine organization, and failure is not a clean proof of an artifact. Use crossed content/location/forcing controls and limit conclusions to that dependence.
- **#8/#10:** sustained change and an unsupervised boundary detector are not neutral admissions criteria for organization. They can exclude quiet functional memory and reproduce a clustering prior. They are observables to calibrate, not organism definitions.
- **#19:** "always" using component-scale metrics conflicts with keeping those metrics off scouts. The negative-audit path is a concrete repair to that mismatch, not merely another warning about aggregates.

### B02 -- Some small-physics concerns are overstated or incorrectly interpreted

**SONNET_CONCERN_OVERRATED / precise corrections:**

- In #13, dimension 2 aliases opposite neighbors to the SAME OTHER cell; self-targeting requires a dimension of 1. More importantly, a self-transfer does not create energy. An uncontested winning self-transfer's debit and credit cancel except for execution cost, then maintenance is charged; losing a contested self-transfer can only add dissipation. With positive cost and no inflow, self-transfer cannot establish self-sustaining metabolism even in a degenerate torus. The corrected ledger, not a blanket dimension exclusion, is the decisive control. Ordinary-size validation remains appropriate.
- In #17, a cell at capacity really is storing 255 units. Saturation/spillage is a confound for adaptive-storage claims, not proof that the cell is "not storing anything." Compare causal acquisition, retention, and usable reserve against matched baselines.
- Excluding energy from direct bit-flip mutation is not by itself a fixed genome boundary or proof that resource-handling traits cannot be inherited. Routing, capacity-use patterns, and instruction-mediated resource control can vary. The MORE restrictive decision is the observer's categorical exclusion of resource-only construction evidence. Do not add energy mutation just to satisfy a misleading symmetry argument.

### B03 -- The decision falsifiers need observable endpoints, not interestingness

**SAME_ISSUE_DEEPER** relative to D-AETH01-01/-02/-03/-05/-06/-10. Their reversal conditions commendably make choices provisional, but phrases such as "reasonably thorough," "interesting economic dynamics," or transfer "never favored anywhere" do not specify a finite adjudication. Repeatedly changing physics until a preferred habitability label appears would itself select familiar-looking machinery.

Define the missing affordance or identifiability criterion, the bounded probe, and its claim ceiling BEFORE using a null to switch candidates. A failure can justify stopping expenditure without proving universal impossibility. This review's K1-K8 are a cheaper initial sequence than the broad sweep; executing them is future work, not part of this review.

### Reviewer's own qualifications to the preserved Pass A

- M04's request for rectangular comparisons should not be read as saying rectangles are forbidden: `H,W in {4,8,16,32}` permits unequal dimensions. What is missing is assured comparison coverage, especially odd/non-power-of-two dimensions. The even-torus parity concern remains.
- S03 uses "reproduction-coupled" once as shorthand. The precise term is **copy-coupled**: the mutation opportunity is a byte write, not an established organism reproduction event. That distinction is central to this review.
- S04 proposes construction-capacity controls, NOT an axiom that a constructor must be isolated, parent-preserving, or sufficient without an environment. A distributed consortium may be the appropriate unit. Attribute and test assistance rather than demanding its absence.
- M07's exact time-shift relation is not evidence of a practical exploitable correlation, and no such exploit was measured. It limits the absolute independence wording, not the acceptability of deterministic pseudorandom forcing per se.
- Any effect of background resources, clock, or geometry is a real effect of THIS specified universe. Calling it a confound refers to a stronger generalization or ancestry claim, not to something unreal in the simulation.

## VERDICT

**PROCEED_TO_REPAIR**

This means repair the DESIGN and its scientific inference contract before freezing or implementing it. It is not approval to build Candidate 1 now, run a habitability campaign, spend Runpod credit, or claim that Aether's scientific hypothesis is supported.

The Pass A verdict is unchanged by the resident comparison. The minimum next step is the five-item MINIMUM REPAIR list, with the hand-checkable K1/K2/K6 contradictions resolved first and the K3 relay/capability discrimination specified before a production implementation. Keep Candidates 2 and 3 available. Escalate to REDESIGN_PRIMARY_PHYSICS if the actual copy-coupled search/free-storage law is incompatible with the scientific requirement after it is stated honestly; switch candidates only on a relevant discriminator, not because more elaborate machinery sounds alien.

The most distinct value supplied by this review is the conversion of reassuring categories into counterexamples: a correct step that fails the mandatory ledger, a dormant world in which the proposed mutation null cannot run, and a preconfigured relay that can satisfy the claimed recursive-construction ladder. These are actionable pre-code failures, not new empirical results.

### Single most dangerous thing the designers appear not to understand yet

**AETH-01 does not autonomously explore dormant matter in the way its accessibility story assumes. It mutates only successful copying by already functioning machinery, while retaining untouched information for free. The inherited and environmental machinery enabling that copying can then be misattributed as a recursively constructed organism by the proposed observer.**

This is more dangerous than a weak hash or slow GPU kernel: exact replay and excellent TDD could make the wrong scientific interpretation exceptionally convincing.

Document-only validation checked the preserved Pass A byte-prefix hash, ASCII encoding, required sections, and all five comparison categories. No simulator qualification or experimental result is claimed from those checks.

END OF REVIEW -- only this document is authorized for the separate review commit. No implementation or repair performed. "Do not build this candidate" remains a legitimate outcome of the bounded follow-up decisions, not an outcome the review process should be designed to avoid.