# Qualify one engine before expanding claims

**The first 90 days should deliver one tiny native engine, an independently checked measurement path, and at most a few sharply bounded decisions about development.**
Do not promise three complete runtimes, six successful studies, or recursive sagacity by day 90.
Keep the three physics tracks and six question lanes as the scientific portfolio, adopting A-first sequencing as the design recommendation after the audits exposed qualification and independence costs.
This plan is part of the independent design package. Its later engine builds, native calibration, experiments and benchmarks remain proposed; offline document and arithmetic validation is recorded separately.
The prospective resource envelope is **372 core-hours through day 90 + 72 conditional + 36 protected audit = 480**, with zero paid GPU and no external inference in experimental loops.
The optional 20,000 campaign-token allowance and 30 kWh energy ceiling are planning limits, not measured consumption, purchases, or evidence that this schedule is feasible.
An honest qualification-only package or a strong ordinary baseline winning is a successful MVP outcome if it resolves the planned choice.

## 1. One staffed, bounded instrument replaces simultaneous runtime construction

### This proposal does not rewrite Stage I

The scientific baseline remains `eeeda08bb45757298b3cb21ee22d816b44388aef`, including [REQUIREMENTS.md](REQUIREMENTS.md), [RSE_ARCHITECTURE.md](RSE_ARCHITECTURE.md), and [the freeze record](process/STAGE_I_FREEZE.md).
The original frozen payload is preserved; current appendices record later decisions without rewriting it. The Stage I freeze record and its historical pending-commit text remain unchanged.
Q1-Q6 here retain the six experimental lanes of architecture section 7, not the mandate's differently numbered Q1-Q10 questions.
The complete six cards and their exact primary-source salvage citations are in [ENGINE_PORTFOLIO.md](ENGINE_PORTFOLIO.md).
The final synthesis adopts D1-D5 as recommendations: A-first staging, one initial resource regime, explicit ordinary baselines, minimal local operations, and fully costed qualification. No further permission is needed merely to recommend them.
D1 recommends temporarily deferring R-APR-01's initial three-track implementation requirement; it does not claim compliance with that original requirement or authorize execution.
Actual resources, custody, staffing, and run manifests still require operator authorization. If execution must instead meet the original three-track scope, replan labor before starting rather than silently dropping the independent checker.

All five supplied evidence notes were read: [Sisyphus](evidence/SISYPHUS_AUDIT.md), [Tantalus](evidence/TANTALUS_AUDIT.md), [Tityos](evidence/TITYOS_AUDIT.md), [Ixion](evidence/IXION_AUDIT.md), and [prior art/catalogues](evidence/PRIOR_ART_AND_CATALOGUES.md).
They motivate controls and scope choices, not claims of present deployment correctness; there are four `*_AUDIT.md` files plus the prior-art note in this evidence directory.
Historical failure reports remain reported observations unless independently tested later; this writing pass does not rerun them.
No other architect design, prohibited role design/current proposal, unfiltered retrieval, live wiki, database, sealed historical holdout, or credential file is needed.
The wiki remains deferred because the reviewed API does not guarantee source exclusion before results return ([scope reason](evidence/PRIOR_ART_AND_CATALOGUES.md#L225-L281)).

### Build scope and ownership are small enough to fail visibly

The first engine is **A0**, a finite local-rewrite interpreter with a tiny exact world and a deliberately authored memory witness.
It shares only manifest, receipt, and serialization conventions with the independent reference path; decisive truth generation and score computation must be separately implemented.
The implementer builds A0 and discovery tools; a second implementer receives the behavioral/intervention contract, not the first solver/scorer source or outcome-dependent patches.
A custodian controls confirmation seeds/configurations and the candidate-selection lock; this is a role with tested access boundaries, not a self-declared flag in an unrestricted process.
If distinct custody or independent authorship cannot be staffed, retain repeatability/qualification outputs and withhold mechanism-level independence claims.

| Work package | Concrete artifact to build later | Existing material to reuse narrowly | Explicit exclusion |
|---|---|---|---|
| A0 physics | Finite records, low-level transition interpreter, complete checkpoints, native resource meter | Ananke complete-state checklist as EXTRACT, not its runtime | No Torch dependency, networked optimizer, typed belief/planner library, or external code execution |
| Exact worlds | W0 truth table, W1 transition table, optional W2/W3-R/W3b-R exact references | Ludus differential leak/draw-law fixture contracts as EXTRACT | No large game collection, adaptive ecology, or imported answer-key access |
| Qualification | Seeded positive/negative/neutral organisms, independent oracle, real admission-route tests | Tityos failure shapes and Ergon planted-label pattern as EXTRACT | No inheritance of old PASS labels or historical calibrated error rates |
| Local evidence | Create-only run directory, byte/config hashes, counter ledger, correction links | Ixion's transport/provenance distinctions as EXTRACT | No fleet migration, automatic wiki write, model heartbeat, or deployment claim |
| Causal analysis | Native lesion/sham/rescue and donor/recipient controls | Nestor dose checks and Crius ID/content separation as EXTRACT | No anatomy label accepted as causal proof |
| Statistical decision | Small independently checked calculation path; exact finite/binomial cases first | Frozen estimands retained; known-defective legacy quantile code REBUILD | No custom unqualified bootstrap RNG or hard-coded two-primary correction |

Exact primary seams are [Ananke state/checkpoint](../../../../prometheus/ananke/engine.py#L221-L264), [Ludus control contract](../../../../roles/Ludus/REVIEW_PACKET_6_2026-09-16_controls.txt#L19-L48), and [Ergon planted rows](../../../../ergon/gen3/p3_common.py#L64-L103).
The statistical replacement is motivated by the directly scoped arithmetic defects in [Tityos E2](evidence/TITYOS_AUDIT.md#L238-L254); no replacement package or dependency is selected or installed here.
Legacy code remains a source of fixtures and contracts; **reuse never implies deployment correctness**.

## 2. Exact worlds and native rules expose what the experiment actually asks

### A0 specifies raw transitions, not cognitive faculties

A0-R has 16 records of eight unsigned bytes, a two-byte live-record bitmap, and two one-byte cursors: **16 x 8 + 2 + 1 + 1 = 132 bytes of native state** before immutable configuration and meter metadata. Record r is live iff bit (r%8) of bitmap byte r//8 is set (least-significant bit first).
The rule cursor is a **record index 0..15**; the data cursor is a **byte address a in 0..127**, with record `a//8` and offset `a%8`. There is no implicit truncation or address wrapping.
Rule offsets 0..7 are exactly **guard mask, guard value, opcode, operand, next_true, next_false, link0, link1**. Both next fields and both link fields encode record indices, not byte addresses; only dereferenced fields require live targets.
All authored interpreter semantics, initial bytes, and codecs are counted in the information ledger; 132 bytes is not the complete description length.
Records 0-7 are the retained region and 8-15 are episode-working material; this reset partition, byte addressing, and the input/branch convention are exposed priors, not discovered cognitive decompositions.
The low-information birth has records 0..3 and 8..9 live, legal sampled rule bytes, and zero data; the separate seeded witness below has six authored rule records instead. Dead bytes are canonical zero and cannot be an uncharged archive.
The external observation is exactly one unsigned **8-bit byte**, immutable throughout its tick. A guard is `(obs & mask) == (value & mask)`; **it tests observation only**, replacing the old observation-XOR-data guard. Data-dependent control must be constructed through native writable material, not a hidden comparison primitive.
Each dispatch snapshots the two cursors, both bitmap bytes, observation, and all eight bytes of the live rule record before testing the guard. On true, execute the snapshotted opcode/operand/links; on false, perform no opcode effect. Choose next_true/next_false from that same snapshot, even if this dispatch rewrites its own rule or next field.
For non-EMIT transitions the selected next must be in 0..15; fetch checks its liveness on the following dispatch. EMIT on a true guard instead ends the tick without reading/validating a next target. No instruction field is reread during the current dispatch; modified instructions take effect only on a later fetch.

| Opcode byte | Exact reads/writes beyond the dispatch snapshot (all arithmetic is on unsigned bytes) |
|---|---|
| 0 NOP | No payload read or write; operand ignored |
| 1 WRITE_OBS | Write snapshotted obs to byte a; operand ignored; no old payload read |
| 2 XOR_IMM | Read byte a once; write `old XOR operand` to a |
| 3 AND_IMM | Read byte a once; write `old AND operand` to a |
| 4 FOLLOW | Require operand 0..15; selector s=(operand>>3)&1, offset=operand&7. Read target record index from snapshot link[s], validate live target, then write data cursor **8*link[s] + (operand & 7)**; no payload read |
| 5 SET_LINK | Require operand 0..31; selector s=(operand>>4)&1, target=operand&15. Validate target live and write that record index to **current rule record offset 6+s**; no implicit data-cursor link and no traversal |
| 6 ALLOC | Require operand 0..1 (selector s); scan snapshotted bitmap for lowest free record t, zero its eight bytes, set its live bit, and write t to current rule offset 6+s. No extra allocator cursor exists. If full, charged no-op plus trace event |
| 7 COPY | Require operand 0..1; snapshot all eight source bytes from record a//8, then copy them to the live record named by snapshot link[operand]. Source offset a%8 is ignored; snapshot copying defines overlap/self-copy. Bitmap and cursors unchanged |
| 8 DELETE | Require operand 0..1; zero all eight bytes of the live record named by snapshot link[operand], then clear its live bit. Self-deletion is allowed; subsequent dead fetch/read is invalid |
| 9 EMIT | Read and emit **the raw current byte at a**, without masking or decoding, and end the tick; operand ignored. Invalid world actions remain scored failures |

Payload accesses require their record live; FOLLOW may repair a dangling data cursor without reading it. Noncanonical selector operands, invalid executed opcodes, or invalid dereferenced addresses end the tick as an explicit invalid transition, with no fallback pointer or partial writes.
Reserve and charge the 14-unit snapshot/dispatch cost before fetch (or stop without starting if fewer than 14 units remain); a failed live-rule fetch consumes that reservation without reading dead payload. Validate targets/selected next and reserve the remaining opcode reads/writes/traversal plus next-cursor write before executing any effect. Invalid or budget-rejected attempts retain the snapshot charge but perform no partial writes; attempted dispatches count toward the 64 limit. A no-output cap stop is allowed for cue/blank ticks; no output at a required decision is a scored failure. EMIT produces at most one action per tick; worlds accept actions only on declared decision ticks.
Tariff is dispatch 1, byte read 1, byte write 2, link traversal 2 for FOLLOW/COPY/DELETE, allocation attempt 8 plus successful initialization writes, and maintenance 1 per live record at tick entry; host CPU is also measured.
Thus every dispatch snapshot costs 13 byte reads (2 cursors + 2 bitmap + 1 observation + 8 rule); every non-EMIT transition also charges its one-byte rule-cursor write, even for a self-loop. Snapshot operand/link use is not charged twice. ALLOC/DELETE each write one bitmap byte; no hidden bitmap reread is needed. Cursor restarts cost two byte writes per tick, in addition to maintenance.
Rule-bearing bytes are writable by the same operations as payload. Dispatch scratch is inaccessible interpreter state, discarded at atomic boundaries; checkpoints occur only there. It supplies no extra persistent organism byte. Kernel, safety checks, counters, and scoring code are immutable and inaccessible.
At every external tick the cursors restart at fixed entry/data addresses, never outcome-selected addresses. Only the 128 record bytes and bitmap may carry cross-tick information; clocks, IDs, filenames, seeds, and host objects are forbidden channels.
B-low permits 64 dispatches and 1,024 tariff units per external tick, 16 records, and at most 64 target acquisition trials; either cap stops the step.
B-high would permit 128 dispatches, 2,048 tariff units and 32 records, but **is deferred**, not pooled with B-low or required for the first decision. It requires a separately versioned bitmap/address/operand contract; the 132-byte A0-R encoding is only for 16 records.
Within a lifetime, the working region resets between episodes; retained-region edits survive only where native plasticity is enabled; all retained allocation/live-map effects follow the same ownership rule.
Clamping restores retained bytes and retained live bits at episode boundaries with matched charged sham work, while preserving legitimate within-episode working-state inference.
During target acquisition all arms receive the same enabled learning rules; P in Q2 identifies whether history could construct retained material, not whether the target learner was denied all memory.
Frozen competence disables retained learning while allowing working-state transitions; if this boundary cannot be implemented without destroying inference, report prequential competence instead.

The **proposed seeded** six-rule/two-data-record bit keeper has entry rule 0, data address 64, and live records {0,1,2,3,4,5,8,9}. Its bitmap bytes are (63,3); all other records are dead zero. At episode reset r8=(4,0,0,0,0,0,0,0) marks no valid cue and r9 is eight zero bytes. The six retained rule tuples are decimal bytes in the layout above:

| Record | Exact eight bytes | Role in the hand trace |
|---|---|---|
| 0 | (254,2,1,0,1,2,0,0) | Cue 2/3: WRITE_OBS at address 64; otherwise go to 2 |
| 1 | (0,0,3,1,2,2,0,0) | AND_IMM 1 leaves bit b at address 64 |
| 2 | (255,4,7,0,3,2,9,0) | Query 4: COPY r8 to r9; otherwise false-branch self-loop until cap |
| 3 | (0,0,1,0,4,4,0,0) | Query obs=4 overwrites r8[0], invalidating the consumed cue |
| 4 | (0,0,4,0,5,5,9,0) | FOLLOW link0=r9, offset 0: data address becomes 72 |
| 5 | (0,0,9,0,5,5,0,0) | EMIT raw r9[0], ending tick |

Hand trace, not runtime certification: cue 2/3 follows 0->1->2 and stores 0/1; blank 0 follows 0->2 and leaves it unchanged. Each tick restarts cursors at (0,64). Query 4 follows 0->2->3->4->5, copies b before invalidation, and emits b. A query without a new cue copies/emits raw 4, a scored invalid action, including a query before any cue. A new cue restores either bit; four alternating demands therefore do not reduce to a one-shot latch. The alternate W0 codec needs its counted adapter, not a claim that these bytes already solve inverted cues.
The tariff hand calculation gives **cue: 62 completed dispatches plus one budget-rejected attempt, 1,023 units** (12 tick-entry + 62*16 base + 2 WRITE + 3 AND = 1,009, then 14 for attempt 63; its next-cursor write would exceed 1,024). Blank completes **63 dispatches/1,020 units**, leaving too little to start another snapshot. Query is **five dispatches/123 units** (12 tick-entry + 5*14 snapshots/dispatch + 4*2 rule-cursor writes + 26 COPY + 2 WRITE + 4 FOLLOW + 1 EMIT). These are prospective arithmetic expectations, not measurements.
Two separate two-record synthetic hand traces expose writable instruction semantics (only r0/r1 live, all unspecified bytes zero): with r0=(0,0,2,9,1,1,0,0), r1=(0,0,0,0,0,0,0,0), and data address 10, r0 XORs r1's opcode 0->9; the next fetch executes EMIT and returns raw 9. This is an opcode-execution witness, not W0 success.
For snapshot-next behavior use r0=(0,0,2,1,1,1,0,0), r1=(0,0,9,0,1,1,0,0), and data address 4: r0 changes its stored next_true 1->0 but still advances to snapshotted next=1; r1 emits raw 0. Neither trace certifies an implementation, endogenous development, or a search result; both must be independently executed before qualification.
Low-information discovery organisms receive none of these witness bytes or their subroutines. Founding populations have 32 candidates; at most 32 generations including generation zero gives **1,024 candidate evaluations per founder block**.
After generation zero, each 32-evaluation generation reserves **24 cost-greedy slots and 8 competence-neutral bridge slots**; all use development data only. Under the same hard resource caps, better competence is accepted and lower competence rejected. At equal competence, the greedy arm rejects higher cost and accepts lower cost (exact ties use a fixed 1/2 coin); the bridge arm accepts with an independent **predeclared probability 1/2 regardless of cost**, including worse cost. This probability is not tuned from outcomes.
Each slot is a persistent parent lineage with one proposal per generation (normally a mutation, except the registered uniform proposal below); an accepted bridge becomes that slot's next parent even when a cheaper equal-competence organism exists elsewhere. No global cost ranking may evict bridge parents before their next mutation. Only the final champion is chosen by competence then cost after the registered generation budget; intermediate cost-best reporting cannot alter bridge survival.
Each mutation performs one legal opcode/operand/link edit, insertion, or deletion with fixed equal operator probabilities; invalid draws consume budget and cannot trigger unmetered retries.
Every fourth generation evaluates a fresh uniformly sampled candidate in one of the eight bridge slots, not as bonus compute; at least one third of discovery remains structural/stochastic, and all initial generation is non-LLM.
Before interpreting search failure, independently qualify planted ascent, equal-cost plateau, and **competence-neutral/worse-cost bridge** paths using the actual proposal/acceptance kernel and fixed finite-budget crossing criteria. Seeded forced-path reachability and unforced search recovery are distinct gates; a competence-decreasing valley is expected to fail both arms and is outside the claimed accessibility boundary.
Recombination, novelty archives, topology-wide optimization, and ecology remain deferred; neither a 1/2 tie coin after cost rejection nor a rare uniform restart substitutes for the eight bridge slots.

### B0 and C0 are specified competitors, not simultaneous deliverables

B0's capacity micro-spec is a nine-site line with reflecting boundaries, two four-bit state channels per site, and one four-bit rule selector per site.
Each synchronous sweep reads only the site's previous state and immediate neighbors; one of a declared finite set of local Boolean/rewrite tables updates its channels and selector.
Rule-bearing selector material may change locally; no instantaneous remote read or global reduction is legal, and each of nine cell updates is charged.
A cue enters at site 0 and a readout is taken at site 8; any influence requires at least eight sweeps, so a shorter horizon is a certified world/physics mismatch, not failed emergence.
Its witness is an authored local relay plus retained local bit; the trial-position assay distinguishes reusable transport from a one-shot flood latch.
C0's micro-spec uses eight recurrent units, signed fixed-point Q4.4 activations/weights, saturation after each update, and a fixed round-to-nearest/ties-to-even rule.
Its synchronous update is a clipped weighted sum of previous activations and raw input; a declared finite local rule updates weights using pre/post values and writable per-edge coefficients.
All products, sums, updates, and coefficient writes are charged; coefficients may be writable but the numerical update kernel remains fixed, and growth/pruning is initially off.
The controls are a manually configured latch, fixed weights, and fixed-plasticity coefficients; none supplies evidence that update machinery developed endogenously.
A future comparison must ledger native precision, host arithmetic, codec information, and unequal achievable transitions; neither same byte count nor same wall time makes A/B/C perfectly resource-equivalent.
At most one 24-engineering-hour B0-or-C0 capacity spike can replace unstarted optional scope after day 60; it cannot be added on top of the 320-hour plan, and its CPU must remain inside Q1's unused allocation.
If a qualified second track needs more work, defer it beyond day 90 with a new plan; a stub, schema, or A wrapper does not count as physical diversity.

### W0 gives an exact memory demand without pretending it is reasoning

Draw b uniformly from {0,1}; emit cue byte 2+b, then d blank bytes 0, then common query byte 4; require one final raw action in {0,1}.
Use d in {1,2,4}; swap the two cue encodings in a second public-codec condition, with the adapter's description and computation charged.
The evaluator enumerates **2 bits x 3 delays x 2 encodings = 12 histories**, never passing hidden b or generator state to the candidate.
The answer is not writable through intermediate actions because no actions are accepted until the final query; event count and final observation are identical for both b values at each d.
A stateless policy therefore has expected success at most 1/2, whereas a native two-state witness can reach 1; this is an analytical claim about this finite world only.
Its depth vector is one retained bit, d-tick delay, two terminal actions, zero information-query price, irreversible final report, no composition, and no law change.
For repeated demand, concatenate four independently chosen bits with fresh cue/query pairs; score trial positions separately and reset only the declared episode state.
The primary capacity factorial is persistence x revisitation x writing, 2^3 = 8 cells; evaluate all 12 histories in each: **96 base rollouts per track**, not 96 independent statistical replicates.
Close each ablation over **rule fetch, payload, both link fields, live map, allocator decisions, and both cursors**, not just data loads. Immutable kernel code and baseline instruction fetch remain available, but modified rule fetch is not an exempt memory channel.

| Channel | No persistence | No revisitation | No writing |
|---|---|---|---|
| Payload, rule/opcode/next bytes, and link fields | Restore birth/seed image before every tick | Every read/fetch sees the birth/seed image plus this tick's write overlay; mask all earlier-tick writes, including modified instructions | Deny all record-byte mutations, including COPY/DELETE/initialization and link edits |
| Live bitmap and allocation | Restore birth live map before every tick | Liveness tests and lowest-free allocation use the same birth map plus current-tick overlay, never the actual older map | Deny bitmap mutation and the entire associated compound operation |
| Rule/data cursors and allocator metadata | Restart both cursors at fixed addresses every tick; no hidden allocator state | Same restart; no previous cursor, allocation order, cached link, or free-list channel | Within-tick cursor control is allowed; tick restart prevents persistent cursor storage; allocator has only the denied bitmap writes |

No-writing charges attempted legal mutations but suppresses **all** their compound state changes; it does not prevent within-tick interpretation. No-revisitation may retain physical old storage, but no organism-visible read path may consult it. With these closed interfaces it is observationally equivalent to no-persistence; no-writing also removes writable cross-tick storage here. Mark these physically/observationally degenerate cells explicitly, not as three independently necessary faculties. Test self-modified opcode/next fetch, live-bit tests, lowest-free allocation, and cursor restart as adversarial cases in all eight cells.
Liveness/legality checks, maintenance charges, budget availability, and invalid/cap-stop behavior must use the same ablated view: older hidden live bits must not change how long a tick can run. Physical restore/masking/sham work is separately metered and matched without changing the organism's usable tick budget; no off-ledger host work or timing/output side channel is permitted.
Broken, sham, and rescued witnesses add 3 x 96 = 288 rollouts; base plus these variants totals **384 deterministic rollouts for A0**, before repeated-demand and qualification panels.
Only d=2/canonical codec is initially proposed as the statistical operating regime; d=1/4 and the alternate codec remain exact finite checks unless separately qualified.

### W1 makes history, inheritance, and lifetime adaptation separable

Each four-trial episode samples a hidden bit theta and uses the law y = x XOR theta, with x in {0,1}; the first two trials reveal feedback and the last two score without feedback.
Counterbalance the calibration inputs so both x values occur; feedback is delivered only after the candidate's prediction, with no future-label field exposed.
Present the calibration cue, a W0-style blank delay, then the query; delayed retention is a controlled axis, not a larger world with unknown minimum policy.
Development history contains 16 episodes: eight at delay 1 and eight at delay 2, each delay stratum balanced across theta and input order; record the complete world draw as the paired block.
H-structured orders shorter delays before longer ones; H-shuffled uniformly permutes the **same episode multiset**, never granting extra observations or repetitions.
The episode ordering can itself be a cue, so target theta/order is independently counterbalanced and the ID/clock-only baseline is mandatory.
P enabled/clamped acts on cross-episode retained edits during history; I low-information/direct-solution is a founder treatment with exact inherited bytes and source exposure charged.
The direct-solution arm contains a stationary lookup fitted on a development law; it is not falsely advertised as an adaptive oracle, and it competes alongside a genuine two-state adaptive baseline.
Targets initially use delay 4 under the same XOR mechanism: this is **within-family parameter transfer**, not new-causal-family evidence.
W1b changes theta after an observed flip event with theta_next = theta XOR event; repeated delayed reports now require state updating rather than stationary calibration alone.
A finite-state oracle for W1b must be constructed and qualified before any cross-family claim; the target event stream is not disclosed through a privileged state bit.
The depth vector records one hidden law bit, delayed recall, repeated-demand updating in W1b, two output actions, and a new causal transition rather than only new seeds.
Every candidate evaluation during search uses 16 development episodes; all 1,024 population evaluations are charged even though only one champion's descendants enter the factorial.
Lock the champion on development performance before confirmation; no Ares-style maximum over held-out candidates is permitted ([selection failure](evidence/SISYPHUS_AUDIT.md#L97-L101)).

### W2 tests reuse against a tiny table; W3-R tests tiny reusable revision

W2 state is two bits x; tool a flips the low bit, and tool b swaps the bits; a public raw command names a sequence of tool labels, and the candidate predicts the final two-bit state.
The association between the two labels and primitive maps is hidden per law block; examples reveal observed transitions, not map names or a composition routine.
Training uses all length-one and length-two command forms with balanced starts; the sealed composition panel uses length three.
Enumerating two label assignments and four starts gives **48 length-one/two cases** and **64 length-three cases**; the independent evaluator can enumerate the entire finite support.
A direct two-tool transition table has eight state-action entries and solves any composition once acquired; it is an obligatory cheap baseline and a strict ceiling on exotic interpretations.
W2b replaces the low-bit flip with setting the low bit to zero, making that tool irreversible; this is a changed causal map, while label permutations alone remain nuisance recoding.
No native COMPOSE opcode is supplied; the seeded positive explicitly programs primitive reuse and is ledgered as authored.
Code accounting includes the interpreter, primitive tables, decoder/adapter, retained structure, and any compression dictionary; length changes caused solely by invertible recoding are reported as coding dependence.

**W3-R replaces W3, and W3b-R replaces W3b; the old two-cue world is not retained as a qualified revision task.** Draw balanced h and three cues c1,c2,c3, each independently correct with probability 3/4 conditional on h. Show c1 once, then a two-blank delay; c1 cannot be reread. After observing price q in **{1/32,1/8}**, choose final 0/1 or query once to buy both c2 and c3, then make one irreversible final decision. Correctness pays 1, incorrectness 0, less q if queried.
The raw-byte codec is c1=2+bit, blank=0, price low/high=8/9, c2=16+bit, c3=18+bit, final prompt=20; at the price prompt output 0/1 ends the episode or action 2 requests the pair. Only 0/1 are legal at the final prompt. Intermediate cues accept no action and provide no writable external memory. Price and label encodings are public, counted priors; balanced prices are independent of h/cues.
For qualification the regime is known via a public initial byte 24 (independent) or 25 (correlated); the exact policy oracle uses that information. During adaptation **the regime is latent**, with no regime/change byte; only past feedback (32+h after a completed decision) permits learning its law. Use 64 feedback acquisition episodes, followed by frozen no-feedback assessment; never expose current/future h before a decision. Oracle regret references the known-law optimum, not a claim that a latent-law learner starts with it.
Enumerate **2 h x 8 cue triples x 2 prices = 32 weighted independent cases**, with row weight `3^k/256`, k=number of correct cues. For each fixed h/price, correctness patterns 111,110,101,011,100,010,001,000 have numerator weights **27,9,9,9,3,3,3,1**; their sum is 64, hence total probability 1 across four h/price strata.
Majority accuracy is **(27+9+9+9)/64 = 27/32**. At low price query utility is **26/32 = 0.8125**, versus no-query **3/4 = 24/32**; maximum gain over no-query is **2/32 = 0.0625 raw = 0.05 normalized by 1.25**. At high price query utility is **23/32**, strictly worse than no-query. The optimum queries only at low price and uses majority after purchase.
The first cue is operationally necessary for that majority rule: c2 and c3 disagree with probability **2*(3/4)*(1/4)=3/8**, and then majority must use retained c1. Without c1, two equally reliable purchased sources yield only 3/4 optimal accuracy, before their positive cost. Always following the latest cue cannot reproduce the gain.
In **W3b-R**, c2=c3=z is one accuracy-3/4 draw independent of c1 given h. Enumerate **2 h x 2 c1 x 2 z x 2 prices = 16 support cases** (off-support triples have zero weight); each row has weight `3^j/64`, j=number correct among c1,z. Per h/price the four weights have numerators 9,3,3,1 and sum 16.
Two distinct equally reliable sources give optimal accuracy **9/16 + (6/16)/2 = 3/4**: on disagreement the posterior is tied. Duplicating z does not supply a third independent source. Query utility is 23/32 at low price or 20/32 at high price, so **no-query is strictly optimal at both prices**. Correlation now changes the optimal policy rather than merely its description.
Obligatory baselines are retained-c1/no-query, three-cue majority, always-query, and the **regime- and price-conditioned finite policy table** (alongside constants/last-cue/change detectors). Do not claim improvement over an optimal table; compare acquisition, retained contribution, and full lifecycle cost. These are tiny reusable revision demands, not broad thinking or supplied belief objects.
Distinguish the known-law table's oracle ceiling from a deployable table baseline: the latter must estimate the latent regime from the **same feedback/query opportunities**, paying for exploration and stored parameters, with no privileged regime input. Removing retained c1 alone demonstrates a memory contribution, not selective revision without the price/law policy checks.
For the 12-cell Q4 design, familiar law is W3b-R and new law is W3-R; fix the primary history-by-lesion contrast on the **new independent law's low-price stratum** after acquisition. High-price and correlated-law outcomes are mandatory policy-validity/retention checks, not outcome-selected alternatives. Reverse-direction adaptation is secondary. Do not dilute the 0.05 headroom by silently pooling prices or laws: equal prices alone reduce independent-law average headroom to 0.025, and adding equally weighted correlated trials reduces it to 0.0125.
Use matched stable/changed-law blocks to separate warranted revision from false switching; report exact-weight utility, common-reference regret, query rate, and acquisition-time revision latency. Stdlib rational enumeration now checks these finite-law expectations (process/VALIDATION.md); independent native execution remains required and no developmental experiment is completed.
There is no confidence score until an output scoring interface itself qualifies; raw internal activations do not become beliefs by analyst naming.

### Transfer partitions specify what was actually unseen

| Partition | Purpose and custody | Reuse rule |
|---|---|---|
| Control development | Hand-built witnesses, defects, clean twins, exact truth checking | Open to implementers; cannot estimate held-out qualification error |
| Qualification | Independent fixture draws from one frozen track/world/noise/cost/estimator regime | Control identities blinded; repair retires the affected panel and triggers fresh qualification |
| Discovery | Search, curriculum selection, mechanism nomination, 12-block timing/variance pilot | Any observed outcomes stay discovery; do not relabel its best case as confirmation |
| Confirmation | Fresh founder streams and sealed target configurations after all choices lock | No per-case feedback until completion; tuning consumes the partition permanently |
| Independent replication | Second scientific implementation, new founder draws and permitted target-law contract | Same-family repeatability and new-family transfer are recorded separately |

Changing generator author helps expose implementation bias but does not magically create a sampled population of causal families.
With two named world families, report conditional contrasts in each and an explicitly weighted average; do not claim a universal across-family standard error from two families.
Custody preflight must show that candidate/search cannot read hidden fields, seeds, assessment truth, or evaluator files; swapping secret state must change only permitted observations.
The plan publishes mechanism families intentionally; only seeds/configurations and evaluative outcomes are sealed, so no claim of conceptual surprise is made.

## 3. Qualification and power determine whether a run is a decision or a pilot

### Qualify the actual measurement route, not a convenient surrogate

The instrument contract is a versioned chain: candidate bytes -> native trajectory -> read-only ruler -> explicit admission result -> immutable receipt.
Delete a guard, corrupt a hash, skip a control, exceed a budget, leak a future cue, or replace a verdict with constant PASS; the real promotion route must reject each violation and accept its clean twin.
No candidate-supplied `passed=true`, schema-only digest, or source-read assertion can satisfy an execution or scientific gate.
This follows the observed asserted-gate and disconnected-control failures, not a claim that these proposed fixtures already cover all failures ([Tityos gates](evidence/TITYOS_AUDIT.md#L31-L75)).

For **each released primary operating regime**, plan 128 independently generated planted-effect assay trials and 128 independent null assay trials, with 64 independently generated paired neutral/sham assays.
A trial is a complete invocation of the production measurement/decision chain on a fresh independently seeded batch of native control trajectories; its recovery/false-alarm endpoint is the signed statistical-detection flag, not proof that the effect exceeds delta*.
Practical-threshold and causal-admission fields still traverse that same route and receive hostile gate tests; their success probabilities must not be confused with detection sensitivity.
If the production contrast uses 96 founder blocks, one sensitivity trial contains those 96 planted founder blocks; 128 positive plus 128 negative trials therefore contain **24,576 planted founder blocks**, not 256 episodes.
Those controls use cheap authored organisms without evolutionary search; all simulator, loader, and scoring work is still metered inside the lane's qualification allocation.
Q1's deterministic truth-table checker has a different smaller whole-assay unit; its success cannot be substituted for Q2-Q5 sensitivity of a 96-block estimator.
The neutral panel traverses the same path; 64 is its number of independent batch differences, not the count of cloned sham episodes.
The qualification distribution is an explicit mixture of native witness instances, nuisance encodings, and registered noise realizations; duplicate draws do not create new source families or implementation independence.
Historical failures used to design these panels are training fixtures; an independently constructed withheld defect/clean-twin subset is required before extrapolating beyond them.

Exact one-sided 95% binomial bounds at n=128 require **at least 111/128 planted recoveries** to establish sensitivity >=0.80, and **at most 2/128 false alarms** to establish FPR <=0.05.
At the boundary p=0.80, P(X>=111)=0.0322244; at p=0.05, P(X<=2)=0.0425968; these are arithmetic calculations, not observed outcomes.
If true sensitivity were 0.90, the sensitivity gate would pass with probability about 0.91250; if FPR were 0.005, the FPR gate would pass with probability about 0.97312.
The gates are separate regime-specific confidence statements, not a simultaneous guarantee across every lane; label them accordingly or preregister stronger multiplicity-adjusted qualification counts.
The mathematical best-case 14/14 positives and 0/59 negatives give bounds 0.807364 and 0.049508, but are fragile all-correct designs and exclude neutral/power costs ([Tityos calculation](evidence/TITYOS_AUDIT.md#L268-L279)).
Do not subdivide one correlated control lineage into 128 pseudo-trials or silently pool incompatible noise/track regimes to reach these counts.

For A0 exact neutral fixtures, enumerate the full declared finite relabeling/round-trip support and require behavioral equality; this proves neutrality only on that support.
For stochastic batch neutrality, require the 90% confidence interval on the paired normalized mean effect entirely within **[-0.05,+0.05]** for Q2/Q3; use **[-0.005,+0.005]** for Q4 and Q4-nominated Q5 so sham tolerance cannot swallow the smaller target effect. Q5 otherwise inherits its nominee's margin.
A planning SD of 0.10 and n=64 gives SE=0.0125 and normal 90% half-width about 0.0206; that illustration cannot establish Q4's tighter equivalence even at zero mean. Actual qualification must meet its lane-specific margin inside existing caps, or remain unresolved.
Run preregistered discovery-only dose/noise sweeps at planted effects {0,0.10,0.20,0.30} for Q2/Q3 and **{0,0.01,0.02,0.03} for Q4**; Q5 inherits the nominated lane's grid. Two noise settings and eight independent batches per cell give **64 characterization batches per lane**.
The 128/128 qualification gate applies to the single chosen regime at **delta*=0.20 for Q2/Q3 or 0.02 for Q4**, and its null; Q5 inherits the nominee's threshold. Select before qualification outcomes; failure does not authorize switching to whichever regime passed.
Use native effect mechanisms and an independent exact oracle to establish the planted magnitude; changing a stored summary number without changing native trajectories is not sensitivity qualification.
If the lane's exact native effect injection cannot be delivered, document the achieved grid and revise a future preregistration before exposure, not after a desired verdict; never lower the current threshold after data.

### Freeze independent units, contrasts, and practical effect sizes

The primary independent unit is an independently initialized **founder block**, including its own search RNG and world draw; treatment clones within it produce one paired contrast.
Episodes, offspring, checkpoints, mutation attempts, repeated target cases, and rescue copies are repeated measurements, not added n.
For follow-up Q3/Q4 on existing Q2 material, keep every eligible founder selected by the predeclared rule, not just successful ones; inherited compute was already charged to Q2.
Follow-up target draws and interventions are fresh, but sharing founders makes cross-lane results dependent; the dependency ledger and Holm family retain that fact.
Missing founders, failed jobs, budget censoring, and invalid interventions remain in the ledger; do not silently replace them until n looks favorable.

For the deterministic Q2/Q3 worlds and their Q5 replicas, measure K as target acquisition trials to a frozen competence threshold: at least 90% exact-panel accuracy and old-family retention at least 90%, assessed on frozen clones every eight trials through trial 64.
Assessment outcomes stay evaluator-only until the experiment completes, so candidate learning cannot optimize the threshold panel from feedback.
Report success-by-64 and K censoring separately; use C=min(K,64)/64 as a **restricted acquisition burden**, explicitly assigning 1 to unresolved cases, not pretending they reached criterion at trial 64.
Primary savings are differences in C; full lifecycle costs include development, whole-population search, initial bytes, and assessment/replay rather than just target trials.
For W3-R/W3b-R use normalized regret R=(exact-oracle utility minus candidate utility)/1.25; this fixed conservative denominator covers the declared reward range and is not re-estimated from observations.
Q4 and a Q4-derived Q5 replica use regret rather than the 90% accuracy criterion: the independent-source oracle accuracy is at most **27/32**, and the correlated-source oracle is 3/4. Define old-law retention as normalized regret worsening by no more than 0.005 for these lanes.
Set **delta*=0.20 for Q2/Q3, delta*=0.02 for Q4**, and require **Q5 to inherit the nominated lane's threshold and primary stratum**. These are prospective decision thresholds, not historical effect estimates.
Q4's 0.02 means 0.025 raw-utility improvement, meaningful within the primary low-price independent stratum's 0.0625 raw headroom over no-query. The superseded 0.20 target demanded 0.25 raw improvement and was not a feasible information-value target here.
This review is a pre-execution specification correction with a separate power plan below. **Never lower delta*, change primary strata, or loosen equivalence after data** to manufacture a decision.

| Lane | Primary contrast and cell count | Independent blocks and total planned cell trajectories | What remains secondary or deferred |
|---|---|---|---|
| Q1 | Persistence 2 x revisit 2 x write 2 = 8 cells on 12 finite histories | 96 base + 288 broken/sham/rescue = 384 exact rollouts; not stochastic n | Other delays/encodings need separate statistical regimes; B/C not built by implication |
| Q2 | 2 H x 2 P x 2 I = 8; add naive, fixed-meta, and total-exposure target-only = 11 | Pilot 12 x 11 = 132; confirmatory ceiling 96 x 11 = 1,056, with fresh blocks | Primary D2=(C_shuffled,on-C_structured,on)-(C_shuffled,off-C_structured,off) in low-I; high-I interaction, B-high, and cross-track claims not primary |
| Q3 | H developed/naive x intervention intact/lesion/sham x novelty within/new = 12 | Pilot 12 x 12 = 144; optional confirmation 96 x 12 = 1,152 | Primary history-by-lesion saving on new law; two rescue cells/block add 24 pilot or 192 confirmation repeats, not n |
| Q4 | H developed/naive x evidence-path intact/lesion/sham x law familiar/new = 12 | Pilot 144 + 24 rescue = 168; confirmation ceiling 1,152 + 192 rescue = 1,344, normally unreleased | Primary history-by-lesion R contrast on W3-R low-price stratum, delta*=0.02; other prices/law are mandatory validity checks; likely pilot/calibration-only |
| Q5 | Base donor real/scrambled x recipient naive/developed x lesion intact/targeted = 8; nominee-specific targeted-damage shams 4 + blank 2 + adapter-only 2 + ID-only 2 = **18** | Add 2 real-donor rescue cells/block: **20 total; pilot 12 x 20 = 240; confirmation ceiling 96 x 20 = 1,920** | Independently repeat the nominated signed contrast, threshold, and stratum; all nominee-specific controls are counted paired trajectories, not extra n or discoveries |
| Q6 | V old/developed x U-construction enabled/clamped x U-donor old/new = 8 | Conditional pilot 12 x 8 = 96; 3 validation variants per base cell add 288, total 384 | No 96-block confirmation promised; fresh D/E and independent replication required before a depth-two claim |

Define Q3's positive contrast as the developed-over-naive C saving with intact content minus that saving under lesion; Q4 uses the same orientation for regret.
Q5's nominated functional contrast is fixed from discovery before its independent replication; the other donor/recipient interactions diagnose delivery and cannot replace a failed primary.
The four Q5 sham cells cross **both real/scrambled donor contents with both recipient histories**, matching targeted lesion dose/geometry but not the nominated mechanism. Each of blank, adapter-only, and ID-only has one cell per recipient history, with intact recipient and the same adapter/adaptation schedule; the two rescues restore real-donor targeted lesions in the two recipient histories. They do not certify unmeasured scrambled-donor rescues.
Freeze the content scramble, reference repair, matched delivery size, padding, native dose, and sham sites before confirmation; verify valid record links/live maps and equal off-target damage in every donor/recipient cell. An invalid scrambled graph is not a content control, and a task-solving adapter is not a free delivery mechanism.
Universal qualification fixtures **do not replace these nominee-specific shams and adapter controls**. Missing or invalid controls block causal admission even when the base eight cells look favorable.
A rescue must restore the original effect within the registered **0.05 Q2/Q3 or 0.005 Q4** equivalence margin (Q5 inherits); shams must not create the same loss. Failure lowers the causal ceiling regardless of significance.
An exact native control can establish finite intervention invariance; natural-organism equivalence needs its own calibrated interval, not merely p>0.05.

### The numerical power calculation is a release condition, not a promise

Reserve one family of **four two-sided primaries** at family alpha=0.05: Q2, Q3, Q4, and the nominated Q5 replication; use Holm and never recycle a parked lane's alpha after seeing results.
For conservative planning, Bonferroni per-primary alpha=0.0125 gives z=2.497705; detection-power target is at least 0.80 against zero at the lane's delta*. The next three 0.20-effect calculations apply to **Q2/Q3 and their Q5 nominee**, not Q4.
Assuming founder-contrast SD sigma=0.50, n=96 gives SE=0.50/sqrt(96)=**0.051031** and approximate normal power **0.92241**; the ideal normal sample-size calculation gives n=70.
Ninety-six is a margin above that approximation, not a guarantee for skewed, bounded, mixture, or censored contrasts; the final finite-sample decision procedure must qualify.
At n=96, the normal approximation reaches 0.80 only up to sigma about **0.58682**; larger pilot variance, tail behavior, or clustering blocks the planned confirmatory interpretation.
At n=12 and sigma=0.50, SE is **0.14434**, before multiplicity/finite-sample adjustment; this is a bounded pilot, not adequately powered confirmation of a 0.20 effect.
For **Q4 (and a Q4-nominated Q5)** use its separate delta*=0.02 calculation: with z_alpha+z_power rounded to 3.34, **n approximately (3.34*sigma/0.02)^2**. At sigma=0.40 this is 4,462.24, hence **4,463 blocks after rounding up**, far outside the unchanged 96-block ceiling.
At n=96 the same rounded planning approximation needs **sigma <= 0.02*sqrt(96)/3.34, about 0.05867**. Thus Q4 is **likely pilot/calibration-only in the first 90 days**, unless the predeclared disjoint pilot supports that very low contrast variance and the actual finite-sample qualification, tighter equivalence, and timing gates all pass. A favorable raw SD alone is insufficient; preregister how uncertainty in pilot variance determines a conservative release forecast.
The 96-block ceiling is unchanged; do not promote a 12-block exploratory estimate, lower delta* after data, borrow audit resources, or quietly substitute thousands of blocks. A Q4-derived Q5 replication has the same power problem and must remain pilot-only unless it independently qualifies.
The 12 fresh discovery blocks estimate runtime, variance structure, censoring, and intervention validity; they are excluded from the subsequent 96-block confirmatory estimate.
Freeze a checked paired-contrast interval/test implementation after the pilot and before confirmation; do not import the audited defective t-quantile table or LCG bootstrap.
Qualification panels must exercise this exact implementation, finite sample size, Holm decision family, and a declared conservative native noise regime reflecting the pilot; set parked hypotheses to p=1 and calibrate each active primary with companion nulls as well as the global null.
The sensitivity bound >=0.80 at delta* is an empirical calibration requirement in that planted regime, separate from the analytic planning approximation; it does not prove power for every endogenous effect distribution.
If the noise model is unsupported or 128 whole-assay calibration trials cannot fit the cap, use exact finite controls and descriptive pilot intervals only; no `BOUNDED_NEGATIVE` about natural development is licensed.
If a separately fixed exact randomization analysis is chosen, its assignment mechanism and discrete attainable p-values must be verified; paired sign flips are not automatically justified by paired data.

A positive statistical detection requires the signed family-adjusted interval to exclude zero and all qualification/baseline/causal gates appropriate to the claimed mechanism; it does not by itself establish practical advantage.
Report whether the point estimate reaches delta*, but label practical advantage established only when the interval's lower endpoint exceeds delta*; an interval spanning delta* leaves that question unresolved even after detection.
The 0.92241 calculation applies only to detection against zero for the 0.20-effect/sigma=0.50 illustration, not Q4. At a true effect exactly a lane's delta*, a symmetric unbiased estimate exceeds delta* about half the time, so adding that point-estimate gate cannot retain detection power; proving an effect greater than delta* needs a separately powered alternative above delta*.
A bounded negative requires the relevant upper interval endpoint below delta*, a qualified capacity witness/search path/world/ruler, and the stated initialization/path/B boundary; otherwise return `STATISTICALLY_INCONCLUSIVE` or the isolated failure type.
Zero qualifying unseeded discoveries in 96 genuinely independent founder searches yields exact one-sided95 reachability upper bound **1-0.05^(1/96)=0.030724** for that search distribution **only conditional on perfect per-founder detection** and a fixed eligibility rule.
The >=0.80 sensitivity bound above is for a **whole 96-founder assay**, not detection of an individual successful founder. Dividing the zero-hit bound by 0.80 is invalid and is removed. Without a per-founder detection proof, report zero detected hits/96 searches (at most a bound on the detection-event probability), not an adjusted bound on latent reachability.
A latent-hit correction would need a separately defined, independently calibrated **per-founder** detection model plus justified heterogeneity/independence assumptions and confidence-error allocation; whole-assay calibration cannot supply it.
This is a search-hit probability bound, never an impossibility theorem about latent cognition; witness failure blocks even that interpretation of scientific reachability.

## 4. Release decisions reconcile CPU, energy, inference, and human work

### Every CPU hour has one lane owner and one activity category

| Lane / owner | Qualification cap | Assay/search cap | Ordinary replay cap | Total cap | Unmeasured planning range | Energy allowance kWh | Optional campaign tokens |
|---|---:|---:|---:|---:|---|---:|---:|
| Q1 | 24 | 30 | 18 | 72 | 18-48 core-hours | 4.5 | 2,000 |
| Q2 | 24 | 72 | 12 | 108 | 30-84 core-hours | 6.0 | 4,000 |
| Q3 | 18 | 30 | 12 | 60 | 18-48 core-hours | 3.5 | 3,000 |
| Q4 | 18 | 18 | 12 | 48 | 12-36 core-hours | 3.0 | 3,000 |
| Q5 including common protocol/independent path | 24 | 36 | 24 | 84 | 24-66 core-hours | 5.0 | 4,000 |
| **Days 1-90** | **108** | **186** | **78** | **372** | **102-282 core-hours** | **22.0** | **16,000** |
| Q6 conditional after S2 | 24 | 36 | 12 | 72 | 18-54 core-hours | 3.5 | 2,000 |
| Protected audit/correction, not routine Q5 | Separate reserve | Separate reserve | Separate reserve | 36 | 0-36 core-hours | 4.5 | 2,000 |
| **All ceilings** | 132 plus audit allocation | 222 plus audit allocation | 90 plus audit allocation | **480** | **120-372 if Q6 opens** | **30.0** | **20,000** |

Calendar release is unchanged from Stage I: **S0 72, S1 120, S2 180, conditional 72, audit 36**.
S0 is Q1 54 + Q5 18; S1 is Q1 12 + Q2 96 + Q5 12; S2 is Q1 6 + Q2 12 + Q3 60 + Q4 48 + Q5 54.
These columns reconcile to the same lane totals; they are not another budget added to the activity table.
Each receipt has one lane, one phase, one activity, actual aggregate process-tree CPU, and remaining authorization; checks that serve several lanes are charged only to their nominated owner.
Replay done for ordinary science is inside each lane; the protected audit is for independent fault reconstruction/correction, never an outcome-selected extra discovery.
Optional Q3/Q4 confirmation sample counts are **upper design alternatives**, not a commitment to complete both: day 60 normally selects one downstream decision study and leaves the other's ceiling unused or calibration-only.
Unused CPU is not transferable automatically; a pre-exposure operator-approved revision can reallocate within the 480 total while preserving audit/qualification needs and updating power.

Use <=4 CPU workers, <=16 GiB aggregate RAM, <=40 GiB retained artifacts; **each job <=6 core-hours and <=12 wall-hours**, checkpointing or terminating at the first bound.
Smaller qualification jobs should finish in seconds/minutes if the design is practical; this is a target to benchmark later, not a measured throughput claim.
A 6-core-hour job is not six wall-hours at arbitrary parallelism; child processes, retries, startup, failed controls, serialization, and assessment all count.
Local approved execution only; no cloud deployment, paid GPU, long autonomous campaign, or benchmark is authorized by the ceilings themselves.
Before S1, measure a frozen micro-batch of witnesses and representative search candidates within Q1/Q5 allocations; keep candidate count, native events, core-seconds, wall-seconds, bytes and energy bounds together.
Project each complete manifest as count x conservative measured per-unit cost plus a fixed 25% timing contingency; if that exceeds its remaining cap, reduce scope before freezing or label it pilot-only.
In particular, Q5 now costs 20 trajectories per block including nominee-specific controls, and its whole-assay qualification must exercise that design. If 240 pilot or 1,920 confirmatory trajectories plus qualification do not fit measured time/caps, stop at the affordable pilot/qualification boundary; **480 core-hours remains unchanged**, and controls cannot be dropped to fit.
Do not claim the count design fits merely because its arithmetic fits; the simulation-throughput and whole-assay qualification benchmarks are currently **UNKNOWN**.

Energy is active plus attributed idle/verification host-time times measured power or a declared conservative interval, with concurrent jobs apportioned once rather than each charged full-host energy.
Thirty kWh over 120 host-hours would permit an average attributed 250 W, but over 480 serial host-hours only 62.5 W; these arithmetic scenarios show why core-hours alone cannot certify the ceiling.
Metered host boundary, idle policy, electricity tariff, storage cost and aggregate dollar cap must be approved before execution; energy upper bounds can force stopping earlier than CPU.
GPU allocation and paid-GPU spend remain **zero**; no unused token/CPU allowance permits buying acceleration.
Optional offline inference requires a written unresolved fork, permitted evidence bundle, provider/model/cost receipt, and approval; no scientific eligibility, scoring, mutation, or routine status depends on it.
The 20,000-token figure is input plus output across the optional **campaign**, not an estimate or claim of tokens used to write this report.

### Engineering time is the binding feasibility gate

| Work owner | Planning person-hours | Cap and protected content |
|---|---|---|
| Q1 native A0 and witnesses | 48-72 | 72; includes tiny physics, reset/affordance tests, codecs and exact W0 integration |
| Q2 factorial/search and ordinary controls | 40-72 | 72; no full legacy engine restoration |
| Q3 optional world/ruler/lesion path | 24-40 | 40; can stop after specification/calibration |
| Q4 optional decision-world/ruler path | 16-32 | 32; can stop after exact-world qualification |
| Q5 common verification and independent science | 64-104 | 104; **64 hours protected for the second implementer**, up to 40 for local custody/receipts/integration |
| **First 90 days total** | **192-320** | **320 person-hours**, not CPU hours or calendar hours |
| Q6 separately approved conditional build | 64-120 | 120 additional person-hours only after S2; no assumption this team is already available |
| Audit repair/reproduction labor | 0-24 | 24 protected additional person-hours if released |

Engineering stage caps are S0 120, S1 96, S2 104 person-hours, summing to 320; these are another projection of the same work, not extra allowances.
Proposed focused staffing is roughly 25 eight-hour days by the primary implementer plus 8 by the independent implementer and up to 7 days of integration/optional work; the total is bounded at 40 person-days.
The ranges are judgment estimates, not audit-row sums: salvage audits explicitly warn that overlapping component estimates cannot be added into a project quote ([Tantalus effort limits](evidence/TANTALUS_AUDIT.md#L259-L264)).
If A0 plus independent qualification exceeds S0's 120 engineering hours, park Q2-Q4 execution and choose a qualification-only deliverable; do not remove independence to make a deadline.
No second runtime is promised inside these figures; its proposed 24-hour spike must replace optional Q3/Q4 work, with scope loss explicitly recorded.

Human scientific review is separate: two 30-minute reviews each week for 13 weeks = **13 hours**, plus a separately approved **8-hour initial qualification/custody review allowance** = **21 hours through day 90**.
Allocate the extra 8 hours as four to threat/custody/budget review and four to independent control/analysis review; engineering debugging is not silently charged as scientific review or vice versa.
Conditional Q6 can request at most 4 additional review hours and audit 4, for a whole-plan ceiling of **29 review hours**, subject to approval.
Cap nonurgent unresolved anomaly packets at five; deduplicate repeated faults, pause promotion at overflow, and immediately report integrity or resource breaches.
One packet contains one decision, controls, primary estimate/interval, artifact links, actual costs, missing prerequisites, and the cheapest next discriminator; classification familiarity never determines admission.

### Days 30, 60, and 90 make distinct choices

| Gate | Required evidence and bounded spend | Decision if passed | Decision if failed or unavailable |
|---|---|---|---|
| Before day 1 | D1-D5 already adopted as design recommendations; separately authorize host/rates/energy boundary, staffing, custody, and local run manifests | Authorize only S0 manifests and bounded implementation, not recommendation prose retroactively | No run; retain documents as a plan |
| Day 10 checkpoint | A0 raw transition contract, exact W0 oracle, seeded/broken bit keeper, meter/reset receipts; within S0 | Continue only if controls distinguish real retention from interface memory | One repair cycle within remaining S0; then CAPACITY_UNESTABLISHED/IMPLEMENTATION_DEFECT and park |
| Day 30 / S0 | <=72 CPU and <=120 engineering hours; complete A0 state ownership, actual-route fault fixtures, independent exact checker, narrow Q1 qualification, measured timing and energy bounds | Release one Q2 B-low regime, preserving 96-block confirmation only if forecast and power qualify | Qualification-only package; no search scaling, no automatic B/C build |
| Day 45 discovery lock | 12 independent Q2 pilot blocks, planted path checks, baseline closure, variance/censoring report, candidate/analysis/custody lock | Commit to the fixed fresh confirmation design through an authorized later process | Keep pilot descriptive; narrow a future preregistration before any fresh exposure |
| Day 60 / S1 | <=120 additional CPU and <=96 additional engineering hours; Q2 qualified result or typed limitation, no selection on holdout | Select **one** downstream decision study and one Q5 nominee; Q4 and Q4-derived Q5 normally remain pilot/calibration-only unless their separate 0.02-effect gates support <=96 blocks | If cheap learner wins, controls fail, or the counted design cannot fit, retain the limitation/pilot and decline confirmation |
| Day 90 / S2 | <=180 additional CPU and <=104 additional engineering hours; exact worlds, complete qualification status, one independent signed contrast or explicit failed prerequisite, full resource/correction ledger | Externalizable instrument/bounded-result bundle; decide whether a second physics track or later Q6 has a justified question | Stop expansion; methods/negative/inconclusive package with precise missing gates, not a narrative RSE success |

By day 30 a useful result can be an exact memory demand plus a documented failure to qualify the statistical ruler; do not collapse those into one overall PASS.
By day 60 a qualified zero-discovery result is about the tested initialization/operator/budget, while a cheap-baseline win revises the developmental-advantage hypothesis in that world.
By day 90, same-code replay is not independent replication; a second-author signed contrast supports a stronger claim only if decisive code and custody boundaries actually differ.
If Q3 and Q4 both remain pilots, the schedule has still produced a defensible decision about feasibility; it has not earned both mechanisms by having allocated both budgets.
Q6's 72 core-hours open only after native process identification, seeded nested-control qualification, fresh-family custody, independent implementation availability, and the additional labor/review allowance are approved.
The concrete Q6 pilot is 8 cells x 12 founder blocks plus 288 paired validation trajectories; it tests intervention identifiability and timing, not the full frozen depth-two thesis.
Its future A/B/C/D/E family definitions must be authored and audited before execution; W0/W1 variants alone do not meet nonoverlapping causal-family requirements.
If those definitions or delivery tests are missing, leave all 72 hours unspent rather than relabel library transfer as recursive improvement ([nested boundary](RSE_ARCHITECTURE.md#L78-L87)).

## 5. Publish bounded evidence now; let six to twelve months challenge the thesis

### The release bundle should be smaller than its claim

The proposed external bundle contains the immutable preregistration, native physics/codec specification, exact-world contracts, control identities with seeded labels, raw sufficient traces, and independent checker instructions.
It also includes every attempted founder, selected candidate and exposure ancestry, all exclusions/timeouts, per-lane resource receipts, qualification confusion counts, primary intervals, baseline results, and claim ceilings.
Publish repair/correction links while preserving original frozen payloads; current appendices may record revisions without deleting inconvenient runs. Syntax validity, execution completion, instrument qualification, and scientific evidence retain different fields.
A clean-machine rerun by another operator is required before a reproducibility claim; neither a report, a source hash, nor a tool exit code alone is that rerun.
For later implementation, write/update tests for native transitions, reset completeness, hidden-state access, budget enforcement, exact oracles, gate liveness, statistical boundaries, intervention dose, and correction propagation; execute them in isolation before campaigns.
No native implementation tests, scientific campaigns or new dependencies are delivered here. Offline validation tests accompany the user-requested design-package commit; that delivery is not external scientific publication or execution authorization.

Unresolved facts are explicit: independent execution of the proposed A0 bytes/hand traces; native whole-assay throughput; variance and censoring of unseeded founders; power under a justified natural-effect distribution; host power/rates; staffed independent implementer and custodian; second-family novelty; and valid process slicing for Q6.
Exact binomial/power arithmetic is a planning calculation, not resolution of these empirical questions.
This MVP and the portfolio are two companions within the complete eight-file mandated package and supporting audit materials; original Stage I payloads are preserved, and prohibited design sources remain unread.

### Six- to twelve-month milestones and thesis failure

At months 4-6, seek one externally rerun qualified finite-world instrument and one independent signed developmental contrast, whether positive or a bounded negative.
Add a second genuine physical track only when its addressing/locality/update assumptions create a specific competing prediction; reproduce the same control demand without sharing decisive simulator/ruler code.
The third track remains a stated coverage gap until it too qualifies; elapsed time and a shared protocol do not supply the missing comparison.
Month-6 evidence should show whether prior development repays lifecycle cost across a declared number of future tasks, with native lesion/sham/rescue and ordinary-library/fixed-meta competitors still present.
If no ruler can sustain sensitivity/specificity/equivalence within the approved resources, call this an instrumentation and feasibility failure, not a negative result about cognition.

At months 6-9, require a new causal-family transfer contrast and an independently reconstructed native mechanism before discussing an architectural principle.
If repeated adequately powered contrasts exclude delta* and fixed/reactive/meta-learning competitors dominate the full resource frontier, reject the **current developmental-advantage thesis in the tested regimes**; do not automatically buy more scale.
If diversity adds only adapter/qualification overhead and no new discriminating prediction, consolidate to the simpler engine while publishing the lost physical coverage.
If all negative verdicts keep being reclassified as unfair tests despite successful planted witnesses and narrow intervals, the program's falsifiability has failed; freeze expansion and have an independent reviewer audit the negative-admission path.

At months 9-12, a recursive-sagacity milestone requires history-altered V improving fresh U construction, fresh S acquisition on C, loss/sham/rescue, D-to-E repetition, independent scientific implementation, and full lifecycle accounting.
If only stored task solutions or a better fixed U transfer, report task learning or ordinary learning-to-learn; if process separation fails, report unidentifiable mediation rather than invented recursion.
**The Phase 3 thesis is wrong or badly framed for this program if qualified tests repeatedly show no meaningful developmental/transfer advantage, ordinary mechanisms explain all gains at lower total cost, or the proposed distinctions cannot be made measurable inside feasible resource and attention limits.**
No finite result proves all possible reasoning impossible, but these outcomes are sufficient to stop this particular architecture program until a genuinely new discriminator exists.
If starting today with none of the old engines, build one exact world, one breakable native witness, and an independently qualified ruler first: that small system can expose a false story before the project spends its scarce engineering, compute, or attention trying to make the story larger.

## REVIEW_CORRECTIONS

These are **unexecuted design revisions**, not historical scientific results or a native runtime implementation. D1-D5 are adopted recommendations; actual custody/resource/run authorization is still separate, and original frozen payloads are preserved.
- A0-R now fixes all address/field/opcode/snapshot semantics, 132-byte state ownership, six-rule bit-keeper bytes, two writable-rule hand traces, closed Q1 ablations, and the 24/8 search split with a cost-tolerant neutral bridge gate.
- W3-R/W3b-R hand enumeration gives 32/16 weighted cases, majority 27/32, disagreement 3/8, independent query utilities 26/32 and 23/32, correlated query utilities 23/32 and 20/32, and maximum low-price normalized gain 0.05. Correlation changes the optimal query policy; no broad-thinking claim follows.
- Q4 delta*=0.02 and grid {0,0.01,0.02,0.03} replace the infeasible 0.20 ambition; Q5 inherits its nominee. Rounded-normal arithmetic gives ceil((3.34*0.4/0.02)^2)=4,463, or sigma about 0.05867 for 96 blocks. Neither is measured power.
- Q5 counts 8+4+2+2+2+2=20 trajectories/block: 240 pilot and 1,920 confirmation; 372+72+36=480 core-hours is unchanged. Whole-assay sensitivity does not license a per-founder miss-bound correction.
- **Check status:** the delegated correction pass could not execute commands. The parent subsequently ran **9 stdlib arithmetic tests, all passing, exit 0**, including exact rational world enumeration, binomial/power calculations, tariff arithmetic and live budget tables. Native hand traces are still not executed runtime certificates; independent transition/reset/control tests remain required. See process/VALIDATION.md.