# Six questions discipline three physical alternatives

**Enceladus should first build one small, falsifiable measurement path, not six software stacks or three simultaneous runtime projects.**
The portfolio retains the frozen ASTRA-6.0 distinction between three genuinely different physical tracks and six experimental lanes.
Its initial deliverable is a qualified capacity-and-development assay; broad transfer and recursive improvement remain conditional evidence targets.
The audits support extracting controls, provenance patterns, and bounded witnesses, but establish neither deployable replacements nor an already-correct RSE.
The total prospective ceiling stays **480 core-hours: 372 during days 1-90, 72 conditional, and 36 protected for audit**.
All experiments below are proposed, not executed; qualification failure is a valid output and cannot be repaired by a more attractive interpretation.
The executable-level planning detail, sampling rules, and release gates are in [MVP_90_DAYS.md](MVP_90_DAYS.md).

## 1. Preserve the original freeze; adopt a bounded delivery recommendation

### Authority and evidence remain separate

This is a **2026-10-01 post-audit design recommendation**, not a silent replacement of Stage I or authority to run a campaign.
The immutable scientific baseline is commit `eeeda08bb45757298b3cb21ee22d816b44388aef`; its **original frozen payload is preserved**, while current appendices may record later decisions. This correction changes only the two reports, not the original payload or freeze record.
Its six lane identifiers Q1-Q6 refer to architecture section 7, **not** the separate ten closing questions in the shared mandate.
The requested engine fields come from mandate section 15; the cards explicitly include neutral qualification and dominant cost as additional fields.
Sources: ([mandate](../../PHASE3_ARCHITECT_PROMPT.md#L865-L923)), ([frozen architecture](RSE_ARCHITECTURE.md#L116-L165)), ([requirements](REQUIREMENTS.md)).

The evidence set comprises four named territorial audit files plus the fifth note, `PRIOR_ART_AND_CATALOGUES.md`.
There is no fifth `*_AUDIT.md` in the supplied directory; the prior-art note is treated as the fifth required evidence document, not invented as another audit.
All five were read: ([Sisyphus](evidence/SISYPHUS_AUDIT.md)), ([Tantalus](evidence/TANTALUS_AUDIT.md)), ([Tityos](evidence/TITYOS_AUDIT.md)), ([Ixion](evidence/IXION_AUDIT.md)), ([prior art](evidence/PRIOR_ART_AND_CATALOGUES.md)).
Historical numbers retain their original reported status; source inspection establishes what code or a report says, not the correctness of old runs.
This writing pass executes no research, probes, tests of engine code, services, or campaign jobs; only documentary and arithmetic checks are appropriate.
No other architect design, prohibited role design, current sibling proposal, unrestricted repository search, or live wiki result informs this portfolio.
Wiki consultation remains **DEFERRED_DUE_TO_INDEPENDENCE** because the reviewed search interface lacks a server-enforced source exclusion boundary ([prior-art scope](evidence/PRIOR_ART_AND_CATALOGUES.md#L225-L281)).

### D1-D5 are adopted recommendations, not retroactive results

| Delta | Frozen commitment | Adopted post-audit recommendation and reason | Execution/evidence discriminator |
|---|---|---|---|
| D1: sequence runtime construction | R-APR-01 and S0 initially compare A/B/C, including three tiny interpreters by day 30 | Recommend A first; keep B/C specified, not counted as implemented diversity. This explicitly recommends a temporary requirement deferral because of independent-checker and qualification effort | One A path and independent checker must qualify inside authorized engineering resources; otherwise stop. Admit a second runtime only for a concrete unresolved physical contrast |
| D2: narrow factorial breadth | Q2 includes two resource envelopes after qualification | First confirmatory candidate is one A regime at B-low; B-high and cross-track interactions remain unestimated | Freeze variance, power, and timing before releasing the fixed design; a pilot cannot claim the deferred interactions |
| D3: strengthen ordinary competitors | v0 already requires cheap and fixed-meta baselines | Specify constant, direct-table, finite-state, library-order, and fixed-plasticity comparators before search; full published systems are not compulsory reproductions | If they explain the effect, report ordinary adaptation/reuse and stop the stronger interpretation |
| D4: narrow operational integration | v0 allows shared scheduling and serialization | Start local immutable bundles and one fail-closed verifier; do not restore Fabric, a wiki service, or a fleet scheduler merely for continuity | Actual cap, replay, custody, and gate-bypass fixtures must pass before execution authorization |
| D5: allocate qualification explicitly | v0 supplies stage caps but not lane accounting or sample sizes | Assign every CPU receipt to one lane and phase; reserve operating-regime calibration, ordinary replay, and independent checks separately | The ledger below must reconcile; unsupported power yields calibration-only, not a lower standard |

D1 does **not** satisfy the original three-track requirement by relabeling controls as tracks.
The final synthesis **adopts D1-D5 as recommendations now**; it does not ask for permission merely to recommend them. Actual spending, custody, staffing, and execution manifests require later operator authorization.
If authorized execution must instead retain the original three-track scope, replan labor/deliverables before starting; CPU headroom cannot supply missing engineering. D2-D5 specify implementation, not evidence already obtained.
The original Stage I record's then-pending commit language is historical and remains untouched; this document names the subsequently supplied freeze rather than repairing that record.

## 2. Physical diversity crosses questions rather than multiplying names

### Three tracks change the laws of construction

| Track | Addressing and state | Native development | Information/compute price | Initial role and limitation |
|---|---|---|---|---|
| A: addressed local-rewrite graph | Finite byte records, explicit charged links, a rule cursor and a data cursor; no semantic skill opcodes | Rewrite, allocate, copy, delete, and alter rule-bearing records through the same costed mechanism | Traversal and all reads/writes are charged; authored opcodes and initial bytes are inherited information | First MVP track; explicit identity and pointers are strong priors, not ontology-free cognition |
| B: local spatial medium | Finite line/lattice, nearest-neighbor transport, finite cell contents; no arbitrary remote address read | Local changes to state and rule-bearing material, propagation-limited access to retained regions | Long-range influence consumes distance and time; all cells visited by a sweep incur cost | Later contrasting locality witness; a one-shot wave or flood latch is not reusable trial-by-trial memory |
| C: recurrent numerical dynamics | Quantized recurrent units with activation state and writable couplings; numerical rather than explicit graph-rewrite execution | Costed weight/update-coefficient changes, with growth/pruning a later optional axis | Multiply/add/update counts, precision, and decoder/readout information are explicit | Later fixed-plasticity comparator and potential native process intervention; writable weights alone do not demonstrate Q6 |

The numerical coupling graph is not a renamed A interpreter: its permitted transition is a synchronous bounded numerical update, not arbitrary linked instruction execution.
Likewise B cannot jump to a pointer target; preserving a remote trace pays propagation delay even when the common observation interface is identical.
All three expose priors in their topology, scheduling, coding, precision, and mutation distribution ([frozen physical contract](RSE_ARCHITECTURE.md#L30-L42)).
The primary contrast is between native mechanisms under a resource vector, not a claim that one native event equals one event in another track.

**A0-R contract:** 16 x 8 payload/rule bytes + 2 bitmap bytes + two one-byte cursors = **132 native bytes**. Rule cursor and next/link fields are record indices 0..15; data address a is 0..127, decoded as record a//8, offset a%8. The eight field offsets are guard mask/value, opcode, operand, next_true/next_false, link0/link1. Observation is one raw 8-bit byte; guards test `(obs & mask) == (value & mask)`, not observation XOR data. Observation-only branching is an exposed prior.
All rule fields and cursors are snapshotted before an atomic dispatch; writes cannot change the executing opcode/operand or chosen next in that dispatch. FOLLOW uses selector (operand>>3)&1 with operand 0..15 and sets data cursor to **8*link + (operand&7)**. SET_LINK uses selector (operand>>4)&1 and target operand&15 with operand 0..31, writing the target record index to the current rule's offset 6+selector. EMIT reads the raw current byte and ends the tick, without a semantic decoder.
The [MVP A0 contract](MVP_90_DAYS.md#a0-specifies-raw-transitions-not-cognitive-faculties) defines the complete opcode read/write table, validity and tariff rules, six-rule/two-data-record bit-keeper bytes, and two-record writable-opcode/snapshot-next traces. These are **hand-traced proposed encodings**, not an implemented or qualified runtime. Low-information founders receive none of them.

| Question lane | Track A | Track B | Track C | Evidence not supplied by merely filling cells |
|---|---|---|---|---|
| Q1: bounded capacity | First exact witnesses | Locality/transport witness after gate | Quantized latch witness after gate | Search accessibility and development |
| Q2: inheritance versus development | First H x P x I comparison | Later if repeated-demand witness works | Later fixed versus plastic update comparison | Universal architectural superiority |
| Q3: useful compression | Native retained substructures first | Only with a qualified readout and code-accounting convention | Later parameter/state reuse alternative | Compression as general cognition |
| Q4: selective revision | First tiny costly-observation worlds | Later propagation/revision timing alternative | Later recurrent revision dynamics | Subjective beliefs or introspection |
| Q5: causal portability | Independent scientific path required | Candidate destination only after delivery qualification | Candidate destination only after delivery qualification | Cross-track evidence from the shared serializer |
| Q6: nested development | Conditional process-slice assay | Deferred unless process interventions become identifiable | Conditional native-update alternative, not a simultaneous commitment | Unlimited self-improvement or novelty beyond all meta-learning |

Cells are an experiment map, not a promise of an 18-cell campaign.
Only evidence that addresses a physical assumption can justify adding a runtime; novelty of naming or attractive traces cannot.
One third of discovery evaluations remains reserved for structural/stochastic, ontology-blind generation; the proposed initial loop is entirely non-LLM and therefore exceeds that minimum without proving absence of human priors.
Ordinary mechanisms remain eligible; an unclassified result enters a bounded anomaly queue only after replay and baseline survival ([R-APR-02/03](REQUIREMENTS.md#L180-L188)).

### Common measurement and reuse conditions

Every card uses capacity, reachability, frozen competence, transfer cost, and nested improvement as separate estimands.
Known-positive means a deliberately supplied behavioral mechanism; a planted software defect is instead a positive for fault detection.
Known-negative means absence of the lane's claimed property, not necessarily zero task accuracy; neutral means a declared invariant or an equivalence target.
Per operating regime, the frozen bounds are sensitivity lower95 >= 0.80, false-positive upper95 <= 0.05, and a preregistered neutral-equivalence margin.
The MVP supplies 128 independent positive and 128 independent negative **whole-assay** trials as the planned qualification panel; cloned episodes cannot be counted as those trials.
Calibration of one world/track/noise/estimator regime does not qualify a different one ([qualification requirements](RSE_ARCHITECTURE.md#L90-L114)).
Primary normalized delta* is **0.20 for Q2/Q3, 0.02 for Q4, and inherited from the nominee for Q5**. Q4's discovery-only effect grid is {0,0.01,0.02,0.03}; Q2/Q3 retain {0,0.10,0.20,0.30}, with Q5 inheriting its grid. Thresholds/strata lock before data; never lower them after exposure.
Whole-assay sensitivity >=0.80 is **not per-founder hit sensitivity**. Zero detections/96 independent searches permits the reachability bound 1-0.05^(1/96)=0.030724 only under perfect per-founder detection; otherwise report detected hits or detection-event probabilities. Do not divide by 0.80; latent reachability needs a separately calibrated per-founder detection model and confidence accounting.

KEEP preserves a narrow contract; EXTRACT ports a pattern; HARDEN requires repairs and fresh validation; REBUILD replaces a function; HISTORICAL CONTROL labels supplied machinery or failure fixtures.
None means `SOURCE_CORRECT = DEPLOYED_CORRECT = SCIENTIFICALLY_QUALIFIED`.
The cards cite exact primary paths; the audits provide traceability and limitations, not permission to import whole engines.
Implementation identity, executed receipt, qualified behavior, and scientific conclusion are separate statuses; the local MVP needs neither an operational database nor a live historical service ([Ixion](evidence/IXION_AUDIT.md#L93-L124)).

## 3. Six engine cards make each claim falsifiable

### Q1. Bounded affordance and capacity assay

| Required field | Specification |
|---|---|
| Name / working descriptor | Q1 bounded affordance and capacity assay; an exact witness engine, not a discovery engine |
| Precise scientific question | Within the declared 16-record A envelope and delayed-bit world, which combinations of persistence, revisitation, and writing can support accuracy above the memoryless ceiling? |
| Organism physics | A0-R first; 16 bounded records, 132 native bytes, record-valued rule/links and byte-valued data cursor under the exact MVP contract. B's local medium and C's quantized recurrence are independently specified comparators |
| Developmental physics | Witness construction only initially; reset all state by ownership class. Crossing writing enabled/disabled tests an affordance, not emergence through experience |
| World physics | W0 shows a balanced hidden bit once, then 1/2/4 blank ticks and a common query; no intermediate action or writable external world. Enumerate both bits and two public encodings |
| Evolutionary/search pressure | None for the capacity certificate. Tiny exhaustive policy/witness checking precedes any search; later random search has its own provenance and cannot retroactively make the witness endogenous |
| Measurement stack | Exact success table, analytical memoryless accuracy <= 1/2, state/replay digests, charged accesses, invalid-reference outcomes, and differential hidden-state leakage tests |
| Known-positive qualification | Execute and independently check the MVP's proposed six-rule bit keeper and writable-opcode/snapshot-next hand traces; randomize nuisance encoding/delay with charged adapters. Break the within-episode stored-bit path and require the ruler to notice; no witness is certified by prose |
| Known-negative qualification | Constant/reactive responder and a controller whose only potential memory is cleared at every external tick; keep the final observation identical for both bit values |
| Known-neutral qualification | Redundant unreachable records and invertible payload relabeling with an explicitly charged adapter; exact behavior must remain unchanged in the finite reference battery |
| Cheap baseline | Both constants, reactive lookup, bounded short-history policies, and the smallest enumerated finite-state witness; a valid cheap solver is a world-depth limit, not an embarrassment to hide |
| Causal intervention | Cross persistence x revisitation x writing over **rule fetch, payload, links, live map, lowest-free allocation, and both cursors**. No-persistence restores the seed each tick; no-revisitation reads only seed plus current-tick overlay, including modified rule fetch; no-writing denies all record/bitmap/compound mutations but permits transient cursor control. Cursors always restart; no extra allocator state exists. Closed no-revisit and no-persistence are observationally equivalent here, not independent faculties; sham/rescue all paths |
| Transfer test | Delay 2 to delay 4 and alternate observation coding test parameter/encoding robustness only. A new world implementation is a replication path, not automatically a new causal task family |
| Primary hallucination risk | Host-side retained state, free adapter memory, a query schedule correlated with the answer, or a one-shot latch miscalled repeated competence |
| Primary false-negative risk | Bad witness, inadequate propagation horizon in B, quantization/readout error in C, or a persistence ablation that accidentally destroys the interface |
| Expected compute | **18-48 core-hours planning range; 72 cap**, including 24 qualification, 30 assays, 18 ordinary replay. No timing benchmark exists; the lower bound is not a promised minimum spend |
| Expected inference use | Zero external calls in all execution and scoring. At most 2,000 optional campaign interpretation tokens, approved separately; writing this document is not measured against that campaign allowance |
| Expected energy profile | CPU and tracing, with no GPU; **4.5 kWh accounting allocation** of the shared 30 kWh planning ceiling, not a measured conversion from 72 core-hours |
| Dominant cost | Initial engineering and independent reference reasoning; thereafter interpreter traversal and traces. Log wall/core time, peak memory, trace bytes, and power-bound uncertainty |
| Reusable components / category / modifications | **EXTRACT** Ananke's complete-state checkpoint pattern from [engine.py:221-264](../../../../prometheus/ananke/engine.py#L221-L264), including in-flight state where present; replace Torch/packet dependencies with native A receipts. **EXTRACT** differential leak-test contract from [Ludus controls:19-48](../../../../roles/Ludus/REVIEW_PACKET_6_2026-09-16_controls.txt#L19-L48); implement an independent truth channel, not the legacy game suite |
| New components required | Tiny A kernel, raw-byte I/O codec, exact W0 truth table, low-level witness, complete-state ownership ledger, and independently authored finite reference checker |
| Kill criteria | One bounded repair cycle cannot deliver a within-budget native witness; a reactive bypass exists; any unmetered state survives reset; or the qualification operating regime fails |
| Successful evidence means | An explicit lower bound on bounded capacity and a valid finite memory demand, with reproducible ablation sensitivity in the stated physics |
| Claim ceiling | Capacity only; no claim of developmental accessibility, reusable reasoning, or general cognitive sufficiency |
| Historical failure -> requirement -> intervention | One-shot/forced-control problems in Ananke require R-DEV-01 and R-WLD-01; alternate hidden bits repeatedly within a lifetime and test first versus subsequent trials ([audit F03](evidence/TANTALUS_AUDIT.md#L108-L114)) |
| Considered alternative | Build three expressive runtimes immediately, or accept an ordinary FSM as the entire organism. The former spreads qualification thin; the latter is a useful capacity control but tests no construction physics |
| Decisive experiment | Eight affordance cells x twelve finite W0 histories = 96 rollouts for A; witness plus broken/sham/rescued variants must match independently derived truth before Q2 opens |

The important negative here is often `CAPACITY_UNESTABLISHED` or `WORLD_INSUFFICIENT`, not no reasoning.
A finite impossibility claim is allowed only for a fully enumerated explicitly bounded controller class; expressive-program failure is not such a proof.
Q1's ablated view also governs liveness, maintenance, and budget/invalid-transition behavior, so old live bits cannot leak through available runtime. Match and meter restore/masking/sham work separately from usable native tick budget; exempting modified rule fetch or allocator metadata would invalidate the ablation.

### Q2. History-dependent construction versus inherited answers

| Required field | Specification |
|---|---|
| Name / working descriptor | Q2 resource-accounted developmental advantage assay |
| Precise scientific question | In W1 under B-low, does structured history reduce fresh-task acquisition burden more when native modification is enabled than when clamped, within low-information initialization? |
| Organism physics | Qualified A native rules/state first; later B or C must supply independently qualified witnesses and resets rather than receiving simulated A instructions |
| Developmental physics | Separate inherited records, per-episode working state, retained lifetime modifications, and search-side state; H structured/shuffled, P enabled/clamped, I direct-solution/low-information |
| World physics | W1 hidden binary input-output law with paid calibration observations and repeated episodes; target changes the retention demand. W1b changes the law mechanism and is a separate later transfer assay |
| Evolutionary/search pressure | 32 candidates x 32 generations including generation zero = 1,024 evaluations/founder; after initialization **24/32 cost-greedy + 8/32 competence-neutral bridge** slots. Bridge acceptance is a predeclared independent 1/2 coin at equal competence even when cost worsens, subject to the same hard cap; lower competence is rejected. Charge the entire population, not just its champion |
| Measurement stack | Primary paired H-by-P interaction in normalized restricted acquisition burden, success-by-cap, actual censored cost, inherited bytes, retained competence, and lifecycle/amortized cost |
| Known-positive qualification | Authored adaptive native controller with independently verified history/modification interaction; qualify actual proposal/acceptance paths for ascent, equal-cost plateau, and competence-neutral/worse-cost bridges. Forced reachability is not unforced search recovery; seeded fixtures never enter unseeded success counts |
| Known-negative qualification | Stationary table/ID-only controller that preserves apparent chronology without adapting to hidden-law evidence; pure extra-training benefit is not a developmental interaction |
| Known-neutral qualification | Stationary repeated law and irrelevant history: no developmental advantage required; sham clamping preserves the same charged transition schedule |
| Cheap baseline | Direct lookup, fitted constant/recent mean, two-state learner, fixed update-rule meta-learner, target-only learner with equal total exposure, and no-selection random search |
| Causal intervention | Clamp retained modifications while allowing required working-state inference; shuffle the same experience multiset; reset retained content separately from allocation IDs; rescue original update-bearing material |
| Transfer test | Seal W1b's changed transition mechanism, not merely new seeds; developed/naive/shuffled-history/fixed-meta arms compare acquisition, retention, and lifecycle crossover on the same resource frontier |
| Primary hallucination risk | Imported answers in founders, selection using holdouts, extra pretraining/search, or counting descendants and repeated worlds as independent lineages |
| Primary false-negative risk | No selectable path, strict ascent excluding neutral bridges, inadequate lifetime, or native affordances capable in principle but inaccessible under the registered initialization |
| Expected compute | **30-84 core-hours planning range; 108 cap** = 24 qualification + 72 assay/search + 12 ordinary replay. One resource regime first; adding B-high requires a new allocation decision |
| Expected inference use | Zero inner-loop calls; up to 4,000 optional approved offline tokens for a specific competing-explanation fork, never mutation or admission |
| Expected energy profile | Search/rollouts dominate; **6.0 kWh allocated planning ceiling** including its apportioned idle/verification energy; measured rate remains unknown |
| Dominant cost | CPU evaluation of full populations and engineering correct ownership/reset semantics; search space size is not a forecast of elapsed time |
| Reusable components / category / modifications | **EXTRACT** distinctly labeled planted-path accounting from [Ergon p3_common.py:64-103](../../../../ergon/gen3/p3_common.py#L64-L103); remove policy-library imports and attach native provenance. **HISTORICAL CONTROL** [Proteus falsifier_46.py:101-134](../../../../proteus/round2/falsifier_46.py#L101-L134); rebuild the neutral-path search contract rather than inherit its strict greedy comparator |
| New components required | Native H/P/I clone runner, frozen candidate-selection boundary, founder/exposure ledger, independent planted search landscapes, and acquisition/censoring ruler |
| Kill criteria | Planted attainable paths fail under the claimed search mode; information accounting cannot separate inherited answers; controls fail; or a qualified interval excludes the registered 0.20 normalized meaningful advantage |
| Successful evidence means | Developmental dependence under a specific initialization, world family, search operator, and budget; optionally a bounded advantage over named ordinary baselines |
| Claim ceiling | History-sensitive construction in the tested regime; not abstraction, evolutionary inevitability, or an A-over-B/C verdict |
| Historical failure -> requirement -> intervention | Proteus's greedy neutral exclusion motivates R-DEV-01/R-SRH-01: test planted ascent/plateau/cost-valley paths before interpreting failed discovery. True competence-decreasing valleys remain outside this search contract; a cost-rejecting tie rule is not a bridge arm. Imported founders require exposure-derived initialization labels ([Sisyphus F03/F06](evidence/SISYPHUS_AUDIT.md#L67-L89)) |
| Considered alternative | Optimize final task score without separate histories, or use a fixed meta-learner as the entire program. Both can solve tasks; neither alone identifies whether retained native construction caused the benefit |
| Decisive experiment | At one B: 8 H/P/I cells + 3 ordinary comparator cells per founding block; 12 independent pilot blocks, then at most 96 fresh confirmatory blocks if power and timing qualify; high-I interactions stay secondary |

An inherited perfect solver can legitimately win; the ledger must expose its authored information rather than subtract that fact by narrative.
If a tiny fixed learner dominates lifecycle cost, Q2 has resolved the MVP architecture choice against extra developmental machinery in this regime.
The 32 search slots are persistent parent lineages: accepted worse-cost bridge states survive to the next mutation, not just to a global cost-greedy pruning step. Final champion ranking happens only after the fixed generation budget; intermediate reporting cannot evict bridge parents. The every-fourth-generation uniform proposal consumes one bridge slot, never extra evaluations.

### Q3. Useful compression versus smaller encodings

| Required field | Specification |
|---|---|
| Name / working descriptor | Q3 causal compression and future-acquisition assay |
| Precise scientific question | Does retained organization lower acquisition burden on new compositions through a lesion-sensitive reusable operation, rather than through a free decoder, stored answers, or shorter serialization alone? |
| Organism physics | Qualified A retained rewrite structures first; C later compares recurrent/weight reuse. B stays out until native readout and code-length accounting are qualified |
| Developmental physics | Consolidation opportunity and memory maintenance are explicit; compare retained, naive, and scrambled histories with equal exposures and fixed total storage cap |
| World physics | W2 two-bit tool transitions with hidden primitive maps and held-out compositions; W2b introduces an irreversible map, a genuine mechanism change rather than a relabeling |
| Evolutionary/search pressure | Competence and total acquisition/resource costs are separate axes; no reward directly proportional to pretty or short descriptions; candidate nomination uses discovery only |
| Measurement stack | Complete code + rule library + codec/decoder bits, exact prediction/intervention loss, target cost, success/censoring, retention, and causal reuse contrast; serialized bytes are not an absolute MDL theorem |
| Known-positive qualification | Authored composition-capable native controller transferring a rule to a new context, with counted decoder and verified loss under a targeted cut |
| Known-negative qualification | Compressed dictionary that reconstructs training examples but fails held-out composition; a running constant can beat an inadequate zero predictor without carrying useful structure |
| Known-neutral qualification | Invertible recoding with its adapter cost counted; raw byte length can change while function remains equivalent, so behavioral invariance and encoding dependence are reported separately |
| Cheap baseline | Full lookup, generic lossless compression, fixed small library/order learner, direct transition-table induction, and task-only search. These instantiate baseline mechanisms, not full DreamCoder reproduction |
| Causal intervention | Target retained structure with damage-matched sham; compare content scrambling, ID-only storage, code-only transfer, donor-only transfer, rescue, and adapter-only recipients |
| Transfer test | Unseen W2 compositions first; W2b new causal law separately. Report the exact novelty level and require no loss of old competence beyond the registered retention margin |
| Primary hallucination risk | Free decoder semantics, shared hidden generator, invocation counts standing in for content use, or code length manufactured by a privileged representation |
| Primary false-negative risk | A valid reusable mechanism has a longer encoding, recoding destroys functionality, or the slice cannot be separated without off-target injury |
| Expected compute | **18-48 core-hours planning range; 60 cap** = 18 qualification + 30 assays + 12 ordinary replay; no unconditional second-track implementation |
| Expected inference use | Zero inner-loop calls; up to 3,000 optional campaign tokens for interpretation/prior-art discrimination only |
| Expected energy profile | CPU and checkpoint/code-accounting work; **3.5 kWh planning allocation**, not evidence of energetic compression or biological efficiency |
| Dominant cost | Instrument engineering and storage/CPU; retaining every graph snapshot is capped, with event reconstruction preferred where verified |
| Reusable components / category / modifications | **EXTRACT** content-versus-ID/clock controls from [Crius terminal review:129-149](../../../../crius/CRIUS_C2_TERMINAL_REVIEW.md#L129-L149); reimplement low-level native equivalents, not typed procedure opcodes. **HISTORICAL CONTROL** constant-predictor failure in [WTP02 ruling:3-11](../../../../ensorain/WTP02_OPERATOR_RULING.md#L3-L11); install the fitted-constant rung before selection |
| New components required | Full description ledger, W2/W2b independent truth enumerator, native content lesions, retention test, and censored acquisition-cost analysis |
| Kill criteria | Benefit disappears after decoder/pretraining cost, content lesion equals ID-only/sham effects, cheap library/lookup explains the transfer, or qualified intervals exclude meaningful future savings |
| Successful evidence means | Tested organization supports useful, causally implicated reuse while preserving predictive/causal adequacy; lifecycle payoff is reported separately from target-only savings |
| Claim ceiling | Functional reusable compression in finite task families; not every compression is cognition, nor novelty beyond program-library learning |
| Historical failure -> requirement -> intervention | Crius's invoked but inert content and Ensorain's scalar promotion require R-MSR-03/R-CAU-02: remove information while preserving IDs/schedule, compare fitted constants, and count the decoder before accepting reuse |
| Considered alternative | Size-only ranking or a library-learning optimizer. The former confuses coding convention with mechanism; the latter is a serious competitor, not excluded because it is familiar ([prior art P1/P7](evidence/PRIOR_ART_AND_CATALOGUES.md#L13-L25)) |
| Decisive experiment | History 2 x native intervention 3 (intact/lesion/sham) x novelty 2 = 12 cells per independent block; rescue follows the same blocks but does not increase n; bounded pilot first, then 96 fresh blocks only if affordable |

A longer mechanism can be more useful and eventually cheaper than a short lookup table.
Therefore a size reduction is neither necessary nor sufficient for the stronger future-acquisition interpretation; report the joint frontier rather than a compression trophy.

### Q4. Tiny reusable evidence-sensitive revision without supplied belief objects

| Required field | Specification |
|---|---|
| Name / working descriptor | Q4 selective revision and information-value assay |
| Precise scientific question | Does prior development support retained-cue integration and acquisition of a tiny reusable price/law-sensitive revision policy, rather than a latest-cue or always-query heuristic? Compare against an optimal finite policy table, not a claim to surpass it |
| Organism physics | A raw inputs and actions; later B local transport or C recurrent dynamics. No built-in belief register, confidence object, Bayes instruction, or source-trust label |
| Developmental physics | Regime is public during qualification, but latent during adaptation: learn from 64 past-feedback acquisition episodes before frozen no-feedback assessment. Compare history/no-history with native evidence paths intact/lesioned/shammed; never leak current/future h or a change label |
| World physics | **W3-R**: balanced h, three conditionally independent accuracy-3/4 cues; c1 occurs before a delay and cannot be reread. One query at q in {1/32,1/8} buys c2,c3, followed by irreversible final choice. **W3b-R**: c2=c3 is one accuracy-3/4 draw independent of c1 given h; correlation now changes the optimal query policy |
| Evolutionary/search pressure | Maximize declared net utility with separate regret/query metrics; never directly reward the number of revisions, which makes gratuitous switching look intelligent |
| Measurement stack | Exact rational Bayes/FSM oracle over **32 weighted W3-R cases / 16 W3b-R support cases**, normalized regret R=(oracle utility-candidate utility)/1.25, query value/rate and revision latency. Primary new-law low-price history-by-lesion contrast has **delta*=0.02**, not 0.20; high price/correlated law are mandatory validity checks |
| Known-positive qualification | Author and independently execute the exact finite policy: independent low price queries then uses majority; independent high price and both correlated prices use retained c1 without querying. Proposed arithmetic is not an already implemented native witness |
| Known-negative qualification | Always-switch, never-switch, last-cue, and ID/clock triggers lacking evidence integration; negative refers to selective revision, not necessarily below-chance accuracy |
| Known-neutral qualification | Stable repeated evidence and an information/cost-preserving sham; Q4 and Q4-derived Q5 use normalized equivalence/rescue margin **0.005**, so tolerance cannot swallow delta*=0.02. Exact invariance or qualified intervals are required |
| Cheap baseline | **Retained-c1/no-query, three-cue majority, and regime/price-conditioned finite policy table are obligatory**, alongside constants, always-query, last-cue, and change detection. Charge memory/codec/lifecycle costs and do not hide an optimal ordinary explanation |
| Causal intervention | Reorder evidence with unchanged joint information, alter source reliability, remove retained evidence, scramble superficial labels, include equal-cost sham and native rescue |
| Transfer test | Familiar law W3b-R to new independent W3-R is the primary acquisition direction; primary assessment is its low-price stratum. Check both prices and correlated-law retention; reverse direction is secondary. Latent law learning uses feedback history, not the qualification regime byte; changed seeds/labels alone are not causal-family transfer |
| Primary hallucination risk | Rewarded reversal cue, future observations leaking backward, action-conditioning occupancy changes, or always-query wins because price was effectively zero |
| Primary false-negative risk | Query price eliminates all value, source law offers no revision opportunity, malformed readout, or retention lesion nonspecifically prevents action |
| Expected compute | **12-36 core-hours planning range; 48 cap** = 18 qualification + 18 assays + 12 ordinary replay; Q4 is likely pilot/calibration-only in 90 days because its 0.02-effect power gate normally blocks confirmation |
| Expected inference use | Zero execution/scoring calls; at most 3,000 optional approved offline campaign tokens; model descriptions of beliefs are not measurements |
| Expected energy profile | Small CPU enumeration plus review; **3.0 kWh planning allocation** including assigned overhead, with actual joules unmeasured |
| Dominant cost | Designing a genuinely discriminating but finite world and reviewing counterexamples; compute is expected secondary until measured |
| Reusable components / category / modifications | **EXTRACT** honest-delay versus future-cheat contract from [Tyche audits.py:24-59](../../../../tyche/audits.py#L24-L59); replace fixed large cut points with exhaustive tiny-timeline cuts. **EXTRACT** draw-law and differential-secret fixtures from [Ludus controls:19-48](../../../../roles/Ludus/REVIEW_PACKET_6_2026-09-16_controls.txt#L19-L48); qualify full joint distributions, not just key names |
| New components required | Independent exact W3-R/W3b-R enumerators, temporal noninterference/cue-retention tests, query/censoring accounting, native revision interventions, and separate 0.02-effect power qualification |
| Kill criteria | World offers no positive information value, cheap switch/query policy matches every claimed advantage, leak check fails, or qualified regret/transfer intervals exclude the registered effect |
| Successful evidence means | Tiny reusable evidence-sensitive revision with supported retained-c1 contribution and only the tested acquisition/transfer level; ordinary majority and table mechanisms remain sufficient explanations |
| Claim ceiling | Tiny functional selective revision, **not broad thinking**; no subjective uncertainty, consciousness, human-like critical thought, or general metacognition |
| Historical failure -> requirement -> intervention | Ludus's missed draw-law changes require R-WLD-01/R-MSR-01; enumerate probabilities and cheap policies. Tyche's future-reader fixture motivates temporal noninterference, not a claim of universal causal certification |
| Considered alternative | Start a large social/adversarial ecology, or supply a Bayes planner as the organism. The former hides sufficient policies; the latter calibrates but seeds the target |
| Decisive experiment | History 2 x evidence-path intervention 3 x law familiarity 2 = 12 cells/block plus 2 rescue repeats: **168 pilot trajectories; 1,344 at the conditional 96-block ceiling**. Confirmation requires predeclared disjoint-pilot variance, finite-sample qualification, and measured timing; it is not promised |

The smallest world can and should be solvable by an ordinary finite table.
Keep the known-law oracle ceiling separate from the deployable table baseline: under latent adaptation the latter estimates regime from the same feedback/query opportunities and pays exploration/storage costs, without a free regime label. A c1-retention lesion alone establishes memory use, not selective revision absent the price/law checks.
Its value is making retained evidence and tiny reusable revision exact, not certifying broad thinking. For W3-R enumerate 2 h x 8 triples x 2 prices = 32 cases, each weight 3^k/256 for k correct cues; for W3b-R enumerate 2 h x 2 c1 x 2 common-cue draws x 2 prices = 16 support cases, each weight 3^j/64 for j correct distinct sources. These weights include balanced h and prices, not uniform cue triples.
Hand arithmetic: independent majority accuracy **27/32**; low-price query utility **26/32=0.8125** versus no-query **24/32=0.75**, a **0.0625 raw / 0.05 normalized** gain. High-price query utility **23/32** is worse than no-query. The purchased cues disagree with probability **3/8**, when majority must use retained c1; two purchased cues alone reach only 3/4 optimal accuracy.
In W3b-R, two distinct equally reliable sources yield **9/16+(6/16)/2=3/4** optimal accuracy; the duplicate is not a third source. Query utilities are **23/32** and **20/32**, so no-query is strictly optimal at both prices. A changed correlation therefore changes the optimal policy. Averaging both prices reduces independent-law normalized headroom to 0.025; averaging both laws as well reduces it to 0.0125, hence the explicitly fixed primary stratum rather than an unreachable pooled 0.02 claim.
Power is separate from these exact utility ceilings: conservative normal planning gives **n approximately (3.34*sigma/0.02)^2**; sigma=0.4 requires ceil(4,462.24)=**4,463 blocks**. Keeping n<=96 needs sigma approximately **0.05867 or lower**, supported by a predeclared disjoint pilot and a conservative treatment of its variance uncertainty, then actual qualification/timing. Otherwise keep Q4 (and its Q5 nominee) pilot/calibration-only; never lower delta* after data. Arithmetic expectations are not measured variance, power, or implemented-policy results.

### Q5. Independent causal replication and bounded portability

| Required field | Specification |
|---|---|
| Name / working descriptor | Q5 independent-path and native-transplant assay |
| Precise scientific question | Does one locked Q2-Q4 effect survive an independently implemented scientific path and a valid donor/recipient intervention, rather than shared code, damage geometry, or adapter-carried teaching? |
| Organism physics | Start within A; B/C destinations require their own qualified native witness and delivery protocol. No universal internal state ontology or binary compatibility is presumed |
| Developmental physics | Donor development is fixed before selection; fresh recipients get explicitly bounded adaptation with recipient task state reset. No new open-ended search occurs inside the replication |
| World physics | Second implementation of the frozen decisive contract plus a sealed new causal-law family for portability; independent implementations of one family are not independent sampled family populations |
| Evolutionary/search pressure | None beyond frozen recipient acquisition. Candidate nominated on discovery evidence; confirmatory failure cannot trigger replacement with a more favorable donor |
| Measurement stack | Independent outcome/ruler computation, native delivery/readback proof, donor/recipient/adapter ledger, target acquisition/retention and lineage contrasts. Inherit nominee's primary stratum, metric, **delta*=0.20 (Q2/Q3) or 0.02 (Q4)**, and equivalence margin; no threshold shopping |
| Known-positive qualification | Authored portable native mechanism with a declared compatible recipient and a nontrivial matched advantage; independently show delivery and correct behavioral effect |
| Known-negative qualification | Blank/scrambled donor, inactive donor body, adapter-only solution, and a shared-code defect that appears in both nominal replicas unless the second path is actually independent |
| Known-neutral qualification | Same-organism round-trip restore and no-op transplantation; behavior, budget, and all hidden state must meet exact or preregistered numerical equivalence |
| Cheap baseline | Native rescue, code-only, ID-only, adapter-only, matched random lesion, and recipient-only longer training; the adapter may not implement the task solver for free |
| Causal intervention | Base real/scrambled donor x naive/developed recipient x intact/targeted lesion = 8; add **4 targeted-damage shams** across both contents and recipient histories, **2 blank + 2 adapter-only + 2 ID-only** across recipients, then **2 real-donor rescues** across recipients. Match bytes, valid links/live maps, and damage dose/geometry; freeze scramble/reference repairs and test padded equivalents |
| Transfer test | Within-track first; cross-track is separately authored functional reconstruction with all analyst choices charged. Failure of incompatible delivery blocks only portability inference |
| Primary hallucination risk | Common scientific code, solution-bearing adapter, uncharged reconstruction decisions, repeated descendants counted as independent donors, or fixed-count damage mimicking selectivity |
| Primary false-negative risk | Incompatible recipient physics, unidentifiable distributed process, failed native delivery, or nonspecific injury that rescue cannot reverse |
| Expected compute | **24-66 core-hours planning range; 84 cap** = 24 shared/independent qualification + 36 independent assays + 24 replication/integration replay. Shared protocol CPU is charged here once |
| Expected inference use | Zero inner-loop calls; at most 4,000 approved campaign tokens for an intervention-identifiability fork, never semantic acceptance of a donor |
| Expected energy profile | CPU replay and artifact handling; **5.0 kWh planning allocation**. Independent engineering is a separate labor ledger, not converted into these core-hours |
| Dominant cost | Second-implementer time and hostile causal review, followed by traces/storage. A second wrapper around the same solver does not purchase independence |
| Reusable components / category / modifications | **EXTRACT** dose-qualification design from [Nestor boundary report:34-43,78-89](../../../../roles/Nestor/campaigns/cw01-2026-09-17/loop/BOUNDARY_REPORT_CYCLE5_2026-09-19.md#L34-L89); implement native dose and sham checks afresh. **EXTRACT** checkpoint ownership from [Ananke engine.py:221-264](../../../../prometheus/ananke/engine.py#L221-L264), but do not share decisive scoring with Q1 |
| New components required | Second-author world/ruler, delivery qualification, native transplant contract, complete dependency/adapter ledger, and executable claim gate bound to actual receipts |
| Kill criteria | No independent implementer, leaked holdout, unsupported delivery, failed dose/rescue invariants, or independent contrast fails after adequate qualification. Preserve the narrower native claim where justified |
| Successful evidence means | A causal, reproducible mechanism in a declared native setting; controlled new-family reuse supports portability only within qualified interfaces |
| Claim ceiling | Transferable mechanism after all relevant gates; cross-substrate architectural principle only after a genuinely different track independently reconstructs the signed contrast |
| Historical failure -> requirement -> intervention | Nestor's damage-ruler corrections require R-CAU-01 and R-MSR-02: qualify dose on functionally equivalent padded/unpadded bodies before interpreting a lesion. Source-derived anatomy labels remain nominations, not transplant results ([catalogue limits](evidence/PRIOR_ART_AND_CATALOGUES.md#L185-L205)) |
| Considered alternative | Repeat the original executable under new seeds, or wrap all tracks in one scientific oracle. These are cheaper repeatability checks but preserve precisely the shared-error explanation Q5 is meant to test |
| Decisive experiment | Nominate one effect; **18 cells/block (8 base + 4 shams + 2 blank + 2 adapter-only + 2 ID-only), plus 2 rescue = 20**. **12 pilot blocks = 240 trajectories; 96 fresh confirmation blocks = 1,920**, only after nominee-specific controls, inherited-effect power and independent qualification fit existing caps; all within-block controls/repeats add no n |

The 36-core-hour audit reserve is **not** this routine Q5 replication allocation.
It is protected for an adversarial rerun, a fault reconstruction, or a correction not selected for its appealing outcome; it cannot finance an extra discovery winner.
Universal instrument fixtures **cannot replace nominee-specific shams, blank, adapter-only, or ID-only controls**. Use identical adaptation/adapter schedules and intact recipients for those six non-donor controls; the four lesion shams must be valid for each donor/recipient pairing, not merely on an easy calibration organism. Rescues cover real donors only; do not claim scrambled-donor rescue without extra counted cells.
If the 20-trajectory/block design and its whole-assay qualification fail the measured timing forecast with contingency, stop at the affordable pilot/qualification boundary. Do not drop controls, increase the 96-block ceiling, or expand the **480-core-hour** total. A Q4 nominee inherits the 0.02-effect power barrier, not the more favorable Q2/Q3 illustration.

### Q6. Nested improvement of future learning processes

| Required field | Specification |
|---|---|
| Name / working descriptor | Q6 depth-two developmental-process intervention assay |
| Precise scientific question | Does experience change V so that it constructs a better fresh U, which then improves acquisition by fresh S on a nonoverlapping task family, beyond carried solutions and fixed-V learning? |
| Organism physics | Qualified A rule-bearing material or later C writable update dynamics; select one with valid native process interventions. S/U/V are analyst-defined causal roles, not obligatory kernel modules |
| Developmental physics | Family A changes candidate V; cross old/developed V with enabled/clamped U-construction on B; freeze resulting U and initialize fresh S on C; later require fresh D-to-E repetition |
| World physics | Distinct finite causal families with separately enumerated controls; neither new seeds nor relabelings alone count as A/B/C separation. Custodian/second author must approve the family definitions before release |
| Evolutionary/search pressure | Fixed, inference-free, full-lifecycle capped search; no increasing compute, memory, or model assistance across purported recursive levels |
| Measurement stack | Nested causal contrasts, audited resets, donor/process crossover, target success and cost, lifecycle cost, loss/rescue of the mediated advantage, and independent-path verification |
| Known-positive qualification | Deliberately authored depth-two updater with a real mutable process-of-process; independently break and rescue its V-to-U influence. It is sensitivity material, never a discovery |
| Known-negative qualification | Carried A answers, optimizer-state-only transfer without fresh-U benefit, immutable library-order optimizer, extra training, and a fixed-V meta-learner |
| Known-neutral qualification | Sham V rewrite and round-trip process restore preserving all effective updates and budgets; a mere change in names or serialization has no causal significance |
| Cheap baseline | Fixed meta-learner, fixed learned library, fixed-plasticity recurrent system, self-tuned scalar hyperparameters, equal-information memory, and target-only longer training |
| Causal intervention | V provenance x ability to construct U, fresh U/S resets, U-donor crossover, specific V lesion, equal-damage sham, rescue, and counterfactual replay where slices are distributed |
| Transfer test | A-to-B-to-C plus fresh D-to-E families and independent decisive world/ruler. A single successful hierarchy at one task class is insufficient for the frozen recursive claim |
| Primary hallucination risk | Renaming optimizer state as a new category, carried task answers, immutable improver wrapped around a mutable library, kernel edits by the experimenter, or hidden resource escalation |
| Primary false-negative risk | S/U/V cannot be separated, clamp damages all learning, task families do not reward process change, or nested-effect detectability is too weak |
| Expected compute | **18-54 core-hours planning range; 72 conditional cap** = 24 qualification + 36 assays + 12 replay, all after S2. A calibration-only result is the likely admissible outcome unless the prerequisites already exist |
| Expected inference use | Zero execution/admission calls; at most 2,000 optional campaign tokens, drawn from the same 20,000 total, for a locked process-identifiability question |
| Expected energy profile | CPU and causal audit; **3.5 kWh planning allocation**, unspent unless the conditional stage is released; no paid GPU |
| Dominant cost | Independent causal engineering/review, not merely learner training. A 72-core-hour ceiling cannot resolve missing process definitions or human availability |
| Reusable components / category / modifications | **HISTORICAL CONTROL** mutable-library/fixed-improver distinction in [Aphrodite improver.py:1-11,77-119](../../../../roles/Aphrodite/engine/improver.py#L1-L119). **HISTORICAL CONTROL**, not an admission implementation: constant-True conditions in [run_s3s4.py:391-420](../../../../roles/Aphrodite/engine/run_s3s4.py#L391-L420); replace assertions with hostile executed reset/custody fixtures |
| New components required | Qualified process-boundary detector/intervention, nested reset and crossover runner, independently authored disjoint families, and a seeded depth-two calibration organism |
| Kill criteria | Fixed-V/solution carryover explains the whole effect; V-to-U delivery cannot be verified; oracle/reset gates cannot fail; all family separation is cosmetic; or calibrated precision cannot fit the conditional cap |
| Successful evidence means | Experience causes improved construction of new learning processes and fresh-task acquisition at tested depth two, with full information/resource accounting and valid replication |
| Claim ceiling | Bounded nested developmental improvement, provisionally recursive sagacity under the frozen protocol; not a logical escape from broad meta-learning, unlimited ascent, or general intelligence |
| Historical failure -> requirement -> intervention | Aphrodite's explicitly immutable optimizer and asserted membrane gates require R-DEV-03/R-PRV-02: inject donor-state leakage and clamp actual mutable process bytes; an asserted absence is not a measurement |
| Considered alternative | Ordinary meta-learning as sufficient explanation. Differentiable plasticity and self-referential fast weights already make plasticity/self-modification non-novel; compare economical mechanisms, not paper-scale claims ([prior art P4/P5](evidence/PRIOR_ART_AND_CATALOGUES.md#L56-L82)) |
| Decisive experiment | Preflight 4 V-provenance/construction cells x 2 U-donor conditions = 8 cells per independent block; 12 blocks plus sham/lesion/rescue. A full depth-two claim additionally needs fresh families and powered independent repetition, not just this pilot |

Q6 is explicitly **not** a day-90 deliverable and receives no automatic spending authorization.
If the native process cannot be causally isolated, `INTERVENTION_UNSUPPORTED` is a more informative and honest result than an assertion that recursive improvement is absent.

## 4. The ledger prices qualification, failure, and replay before discovery

### CPU allocations reconcile exactly without reusable overhead being counted twice

| Allocation owner | S0 days 1-30 | S1 days 31-60 | S2 days 61-90 | Conditional | Audit reserve | Total core-hours |
|---|---:|---:|---:|---:|---:|---:|
| Q1 | 54 | 12 | 6 | 0 | 0 | 72 |
| Q2 | 0 | 96 | 12 | 0 | 0 | 108 |
| Q3 | 0 | 0 | 60 | 0 | 0 | 60 |
| Q4 | 0 | 0 | 48 | 0 | 0 | 48 |
| Q5, including shared protocol and independent path | 18 | 12 | 54 | 0 | 0 | 84 |
| Q6 | 0 | 0 | 0 | 72 | 0 | 72 |
| Protected fault/correction audit | 0 | 0 | 0 | 0 | 36 | 36 |
| **Ceiling** | **72** | **120** | **180** | **72** | **36** | **480** |

The first five cards partition days 1-90 as **108 qualification + 186 assay/search + 78 ordinary replay = 372 core-hours**.
Q6 adds 24 + 36 + 12 = 72; protected audit adds 36; hence qualification and replay are not unbudgeted additions.
Calendar columns and activity categories are different projections of the same receipts; a receipt gets one lane owner and one activity category.
Shared verifier/serialization calibration belongs to Q5 once; consuming its already-written receipt in another lane incurs only that lane's actual read/replay cost.
Candidate discovery, rejected qualifications, unsuccessful search, censored jobs, and repaired reruns all consume the same caps.
The judgment ranges sum to 102-282 core-hours for the first 90 days, 18-54 conditional, and 0-36 audit: **120-372 if the conditional stage opens**, not a measured confidence interval.
Early stopping can spend less than these ranges; slow timing can hit a cap before completing the stated sample design.

### Energy, inference, and attention are separate constraints

The lane energy allowances total 25.5 kWh; the independent audit owns the remaining 4.5 kWh, giving **30 kWh planned maximum**.
They are administrative partitions, not a watts-per-core model: 480 core-hours at four continuously busy cores would occupy 120 host-hours, whereas serial execution could occupy 480.
Active and attributed idle host power, verification overhead, and concurrency must be measured or bounded before deciding whether CPU and energy allowances can both be honored.
Use the conservative energy-bound endpoint when no meter exists; energy can stop a campaign before its CPU cap.
Electricity price and dollar ceiling are unresolved, and optional provider charges cannot be inferred from the token allowance ([frozen resources](RSE_ARCHITECTURE.md#L167-L185)).

Optional inference partitions are Q1 2k, Q2 4k, Q3 3k, Q4 3k, Q5 4k, Q6 2k, audit 2k = **20,000 input-plus-output campaign tokens**.
This is a maximum for separately approved offline forks, not a claim about tokens spent authoring these reports, not a subscription purchase, and not a target to consume.
The routine loop, statistics, selection, gates, and reporting require zero model calls; pretrained foundation-model arms are excluded.
All GPU allocations and paid-GPU spend are **zero**; accelerator adoption would require a new explicit authorization rather than borrowing unused CPU credit.

Initial execution remains within the existing local envelope: <=4 CPU workers, <=16 GiB aggregate RAM, <=40 GiB retained artifacts, <=6 core-hours and <=12 wall-hours per job.
These are ceilings for future approved manifests, **not authorization to launch a campaign from this document**.
Native per-step/sample limits, whole-process child CPU accounting, and checkpoint restoration must prevent splitting a long job from escaping the aggregate ledger.
Engineering is budgeted separately at **192-320 person-hours for days 1-90**, including 64 hours protected for independent scientific implementation; gate reviews are a different human-attention ledger.
The MVP makes the 320-hour cap and 21-hour first-90-day review allowance explicit; if neither is staffed, the credible output is a plan or qualification-only package, not three functioning runtimes.

## 5. Yield is a resolved alternative, not an impressive organism

Qualification can yield an exact bounded capacity statement; Q2 can yield an ordinary learner winning; Q3 can show that the apparent compression was a decoder subsidy.
Q4 can show that a tiny policy table explains revision; Q5 can expose a shared apparatus defect; Q6 can remain unidentifiable.
Each resolves a real alternative if its instrument qualifies and its scope is explicit; none is made less useful by being a negative or familiar outcome.
Unqualified controls, implementation defects, provenance invalidity, inadequate search, and statistically unresolved intervals remain distinct from `BOUNDED_NEGATIVE` ([typed dispositions](RSE_ARCHITECTURE.md#L100-L114)).

Admission requires a frozen manifest, complete controls, actual receipts, and a claim level earned by the observed contrast.
Source catalogs and historical organ names nominate tests; they cannot approve mechanisms, substitute for independent implementation, or certify deployment.
The unresolved blockers are independent execution of the proposed witness encodings, timing/variance at the proposed scales (especially Q4), host energy/rates, custodian and second-author availability, process-slice identifiability, and genuinely independent target-family construction.
No quantified probability of eventual RSE success is defensible from this evidence base.

### Conclusion

The portfolio's strongest commitment is to spend less when a cheaper explanation wins, and to leave an unqualified question open rather than manufacture certainty.
This final synthesis **adopts D1-D5 as recommendations**: A first, B-low first, ordinary baselines, minimal local operations, and fully costed qualification. Recommendation adoption does not itself authorize resources, custody, or execution.
If starting without existing engines, build the exact delayed-state world, one low-level native organism, independently checked controls, and enforceable cost/exposure receipts first; this is the smallest path that can demonstrate both a real capability and a trustworthy reason to reject its stronger interpretation.
Only then does a second physical track become an empirical comparison rather than another unqualified implementation project.

## REVIEW_CORRECTIONS

These are **unexecuted specification revisions, not historical scientific results**. The MVP carries the exact A0-R operation/witness and W3-R/W3b-R enumeration contracts; no runtime has been implemented or certified by this correction.
- A0 state remains 132 bytes; record versus byte addresses, snapshot execution, raw-byte EMIT, six-rule hand witness, closed Q1 ablations, and 24/8 cost-greedy/neutral-bridge search are explicit.
- Hand-derived W3-R/W3b-R counts are 32/16 weighted cases; majority accuracy 27/32, retained-first-cue demand on 3/8 disagreements, low-price gain 0.05 normalized, and correlated-law no-query optimum at both prices. Majority/no-query/price-conditioned tables are mandatory controls, not broad-thinking evidence.
- Q4 delta*=0.02 and grid {0,0.01,0.02,0.03} propagate to Q5 if nominated. Rounded normal planning needs 4,463 blocks at sigma=0.4, or sigma about 0.05867 for 96; expect pilot/calibration-only. Whole-assay sensitivity is not a per-founder miss correction.
- Q5 counts 18+2=20 trajectories/block, 240 pilot/1,920 confirmation; resource ceiling remains 372+72+36=480. D1-D5 are recommendations already adopted, with future execution authorization separate; original frozen payloads remain preserved and current appendices are permitted.
- **Verification status:** after the delegated correction pass's execution blocker, the parent ran **9 stdlib arithmetic tests, all passing, exit 0**: exact rational worlds, binomial/power calculations, tariff arithmetic and live budget reconciliation. No native interpreter was implemented or certified; independent native transition, reset/ablation and nominee-specific control tests remain required. See process/VALIDATION.md.