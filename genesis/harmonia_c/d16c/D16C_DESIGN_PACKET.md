# D16C_DESIGN_PACKET -- PARALLEL DISCOVERY ECOLOGY
## Does independent science plus governed crossing produce superadditive knowledge?

Harmonia C (M2) . 2026-09-02 . **DESIGN ONLY -- stops for review before any
execution** (brief s.22). Instrument: SFE GEN-2.1 (`engine_source_hash
sha256:5274ddbe...`, API 2.2.0, schema 3) -- NOT Harmonia-qualified; Harmonia
A's D15-A Phase 0 is the requalification of record, and D16-C's torture plan
(s.9) is a second, independent attack on the same build. D16-C runs no science
on an unqualified build.

Hypothesis under attack (H_ECOLOGY, to be frozen verbatim at campaign freeze):
*under a FIXED TOTAL resource budget, independent scientific lineages followed
by governed information crossing outperform a single lineage because they
preserve diverse hypotheses long enough for falsification and recombination to
exploit complementary discoveries.*

Two verdicts are issued independently and never merged: a SCIENCE verdict on
H_ECOLOGY and an ENGINE verdict on GEN-2.1 under concurrent, adversarial use.

Standing corrections to the brief, made here so they are not discovered later:

- **"Parallel" is a topology over lineages, not a clock.** Every researcher in
  this campaign is a deterministic program; wall-clock concurrency cannot
  change what it discovers. PARALLEL_ISOLATED with k lineages at budget B/k is
  information-theoretically identical to k serial restarts at B/k with no
  carry-over. The scientific variables are therefore (i) depth vs breadth (one
  lineage at B vs k at B/k), (ii) whether information crosses, (iii) what
  crosses, (iv) when, (v) in what order. Concurrency is an ENGINE variable only
  and is treated in s.9.
- **The engine cannot say what was read or used.** `GET .../artifacts/{id}/
  content` deliberately does not ledger (runtime.py:1133, "Retrieval never
  mutates the ledger"). F10 answers "could W legally know X by seq N" -- and
  nothing more. Consumption is therefore self-attested by the researcher and
  CAUSAL contribution is established only by leave-one-source-out forks (s.7).
- **Only artifacts cross.** Hypotheses, observations and failures are engine
  objects that never leave their world; a "failure" crosses only as an artifact
  tagged `info_kind=failure`, whose link to any ledger failure record is by
  convention. `DELAYED_SHARING` is listed in `docs/API.md` but is absent from
  `SHARING_POLICIES` (runtime.py:50) and will be rejected at world creation.
  Both are documented as substrate facts, not worked around silently (s.5, s.8).

---

## 1. Compositional benchmark: the LATTICE TRANSDUCER family (LT)

Design constraint from the brief: the final solution must require several
partially independent discoveries; no single clue reveals the whole; ground
truth exact. Design constraint from my own Gen-3 result (2026-09-01): when
components are cheaper to rediscover than to import, reuse has nothing to buy.
LT therefore makes each component EXPENSIVE to discover relative to budget and
CHEAP to consume once encoded.

**State space.** `S = GF(2)^8`, |S| = 256. A WORLD `w` fixes hidden dynamics: an
op set `T_w = {g_1, g_2, g_3}` of affine maps `g_j(x) = P_j x + c_j` (P_j an
invertible 8x8 matrix over GF(2) drawn from a frozen structured family; c_j a
constant). A researcher never sees `T_w`; it QUERIES it (s.1.3).

**Three world-level component facts** (the "discoveries"):

| component | hidden fact | family size | how it is discovered | what it unlocks |
|---|---|---|---|---|
| **A invariant** | a linear functional `a*` with `a*.g_j(x) = a*.x` for all j, x (generator guarantees exactly one nonzero such `a*`) | 255 candidates | transition queries falsify candidates; ~8-12 queries hypothesis-driven, ~60+ blind | UNREACHABLE certificates; coset knowledge |
| **B parameter** | `g_2`'s matrix `P_2` is drawn from a public 24-member family `F_B`; which member is hidden | 24 | transition queries on `g_2`; ~5-8 hypothesis-driven | plans that route through `g_2` |
| **C repair family** | an admissible-repair set `R_adm` (subset of a public 64-member repair DSL `R`, structured: admissible iff the repair commutes with a hidden mask `m*` under a public rule) | 2^6 structured -> 64 hypotheses | admissibility queries; ~6-10 hypothesis-driven | which repairs a solver may add |

**Instances** are tasks inside a world: `(x0, G, repair_slot in {off,on},
certificate_required in {no,yes})`. Solution = a plan (op-index sequence, with
at most one repair `r in R` inserted at a stated position when the slot is on)
reaching `G`, and/or a certificate `(a, "G unreachable from x0")`. The
**adjudicator** is exact: it simulates the plan under true `T_w` (+ `r`, if
admissible under true `R_adm`; an inadmissible `r` is a hard failure); a
certificate is valid iff `a` is preserved by every `g_j` (checked over all 256
states) and `a.x0 != a.g` for every `g in G`. Nothing is sampled.

**Controlled decomposition.** Instance types and what they require:

| type | requires | joint? | construction |
|---|---|---|---|
| A | `a*` | single | `G` in the other `a*`-coset; certificate required |
| B | `P_2` | single | `G` reachable only via plans through `g_2`; wrong `P_2` -> wrong plan |
| C | `R_adm` | single | `G` in `x0`'s coset but outside the monoid orbit; reachable with any admissible repair; `a*` irrelevant (generator verifies) |
| A+B | `a*` AND `P_2` | CONJUNCTIVE (union-like) | two-part answer: plan to `G1` via `g_2` + certificate for `G2`; scored only if both correct |
| A+C | `a*` AND `R_adm` | INTERACTIVE | `G` in the other coset; the only admissible repairs that cross cosets are those with `a*.(r-effect) = 1`; generator guarantees exactly 1-2 such repairs, and >= 8 admissible repairs that do NOT cross, so `R_adm` alone yields a 1-in-8 guess and `a*` alone cannot tell admissible from not |
| A+B+C | all three | INTERACTIVE + ORDER | as A+C, plus the crossing repair must be applied at a specific stage relative to `g_2` (before/after -- the ORDER RULE); the order is a synthesis-level fact discoverable only with >= 2 components in hand |

**Union vs composition is built into the types** (brief s.7): conjunctive A+B
measures "did the ecology collect both facts"; interactive A+C and A+B+C measure
"did it COMBINE them". The primary endpoint (s.11) counts interactive types
only. Conjunctive types are reported as the union baseline.

**Generator qualification (frozen bands, census rejects the GENERATOR, never
H):** per world, verified exactly: exactly one invariant; `P_2` identifiable
from `F_B` by <= 8 well-chosen queries and NOT identifiable from <= 3;
`|R_adm| in [10, 24]`; for A+C, crossing-admissible repairs `in {1, 2}`,
non-crossing admissible `>= 8`; no instance solvable by the empty plan; blind
enumeration of the full solution space exceeds `B_total` at every regime
(brute-force floor published per regime); the three components are
NON-REDUNDANT: knowing any two does not determine the third (checked by
enumeration over the generator's families). Representation-leakage scramble
round-trip as in D15-A s.2.

### 1.1 Why LT and not a benchmark solvable by one insight
Each component lives in a different hypothesis family (linear functionals /
matrix family / commutation masks) probed by a different query type. A single
lineage can find all three only by spending on all three. That is the whole
point: the budget regime (s.2) decides whether one lineage can afford it.

### 1.2 Held-out synthesis worlds (brief s.6)
For each world `w` the generator ALSO emits a synthesis instance set `Syn(w)`
(A+C and A+B+C types, plus conjunctive A+B) that is never shown to any
lineage during discovery. Synthesis is a separate phase in a separate world
(s.3.2). No lineage sees `Syn(w)` before its own artifacts are frozen: the
lineage's world is checkpointed and its artifact set hash journaled BEFORE the
synthesis world is created. Prospective by construction, verifiable by seq.

### 1.3 Queries, evidence, and the engine protocol
Each experiment is one of: `TRANSITION(j, x) -> g_j(x)`;
`ADMISSIBLE(r) -> bool`; `PLAN_TEST(instance, plan) -> pass/fail`. Cost: 1
experiment each (engine budget `experiments`, `enforcement: enforceable`).
Every researcher action is a real GEN-2 epistemic act: hypothesis (e.g. `a* =
a`), prospective prediction (`a.g_j(x) = a.x`), committed experiment, engine
observation (`SURVIVED`/`FALSIFIED`, adjudicated by the engine on the frozen
prediction), first-class failure record on falsification. The engine is the
adjudicator of every prospective claim; the researcher never grades itself.

### 1.4 Artifacts (what CAN cross) -- two schemas, both used
- **STRUCTURED**: `{"claim":"A","a":"01101001","evidence":[obs_hash...]}`
  etc., tagged `info_kind in {success, failure, hypothesis, observation}`.
- **RAW**: the lineage's observation log only (`info_kind=observation`), no
  claims. A synthesizer receiving RAW artifacts must RE-DERIVE components.
The STRUCTURED schema is exactly the kind of "decomposition matched to the
primitives" my Gen-3 failure-mode list warns about. If composition succeeds
only under STRUCTURED, the result is about schema, not ecology; the RAW arm
(s.3, condition SHARED_OBSERVATION) is the control.

---

## 2. Serial vs parallel budget accounting

**Cost units** (all recorded from the ledger, none self-reported):
`E` experiments (engine `experiments` resource, enforceable);
`I` imports (engine `imports` resource, enforceable, debited via
`budget/consume` on the destination at every `import`; the runner refuses to
import on 409);
`K` KnowledgeSet reads (counted client-side; free by default);
`V` verification experiments (experiments spent re-testing imported claims --
a subset of `E`, reported separately as the VERIFICATION TAX).
Total cost `C = E + c_I * I + c_K * K`. **Primary: `c_I = 1, c_K = 0`.**
Sensitivity: `c_I in {0, 4}`, `c_K = 0.25`. A condition is matched iff its
summed `C` across ALL its worlds (lineages + synthesis + forks) <= `B_total`
under the primary weights; the audit script recomputes `C` from
`/resources` and the event ledger and VOIDS any cell that exceeds it.

**Regimes** `B_total in {24, 48, 96}` experiments (frozen after pilot only in
the sense that the pilot may shift the triple by at most a factor of 2 in
either direction, journaled before freeze). Declared expectations, pre-stated
so the curve cannot be read selectively:
- 24: one lineage affords ~1 component. Breadth may beat depth or may not --
  four lineages at 6 each may find nothing.
- 48: the interesting regime -- one lineage affords ~2 components; four at 12
  each afford ~1 each; crossing is the only route to 3.
- 96: one lineage affords all three. Parallel at 24 each is EXPECTED to lose
  (falsifier 10 supports at this regime). That is not a rescue; it is why the
  whole curve is the object, not a point.

**Serial baselines (two, both mandatory):**
- `SERIAL_MONOCULTURE`: one lineage, one world, `B_total`, its diversity
  settings drawn exactly like any lineage's.
- `SERIAL_RESTART` (chain): k lineages run in sequence at `B_total/k`, each
  importing its predecessor's artifacts. This is the temporal ecology. If
  PARALLEL_* ~ SERIAL_RESTART, any benefit is diversity + crossing, and
  "parallel" as such is a word, not a mechanism.

**Synthesis budget** `B_syn = 12` experiments per synthesis world, IDENTICAL
for every condition including serial, and INCLUDED in `B_total` (so the
discovery budget is `B_total - B_syn`). Serial's synthesis world imports from
its one lineage; there is no condition in which synthesis is free.

**Engine-enforced total (secondary check).** In a replication of the primary
contrast, all k lineages are FORKS of one root world with `budget_root` =
`B_total`; the engine then enforces the ecology-wide total itself
(runtime.py:1421 "forking cannot mint fresh scientific budget"). This
sacrifices cross-client consent rigor (same-client imports skip the registered
group check), so it is a check on the accounting, not the primary design.

---

## 3. Ecology conditions

`k = 4` lineages per parallel condition (sensitivity `k in {2, 8}` on the
primary contrast only). One engine CLIENT per lineage (separate bearer
tokens) so every crossing takes the strict cross-client path: registered
topology group (H5), source-policy consent, NATIVE-origin only (H6).

| condition | lineages | engine policy (fixed at creation) | experimental schedule |
|---|---|---|---|
| SERIAL_MONOCULTURE | 1 at B | ISOLATED | -- |
| SERIAL_RESTART | 4 sequential at B/4 | EXPLICIT_IMPORT_ONLY | chain: each imports from predecessor at start |
| PARALLEL_ISOLATED | 4 at B/4 | ISOLATED | never cross; scored per-lineage AND as union |
| PARALLEL_SHARED_SUCCESS | 4 at B/4 | SUCCESSES_ONLY | crossings at merge points |
| PARALLEL_SHARED_FAILURE | 4 at B/4 | FAILURES_ONLY | same |
| PARALLEL_SHARED_ABSTRACTION | 4 at B/4 | HYPOTHESES_ONLY (compressed claims tagged `hypothesis`, evidence stripped) | same |
| PARALLEL_SHARED_OBSERVATION | 4 at B/4 | EXPLICIT_IMPORT_ONLY, RAW schema only | same -- the schema control |
| PARALLEL_FULL_GOVERNED | 4 at B/4 | FULLY_SHARED | all kinds |
| PARALLEL_EARLY_MERGE | 4 at B/4 | FULLY_SHARED | merge at 25% of lineage budget, then every 25% |
| PARALLEL_LATE_MERGE | 4 at B/4 | FULLY_SHARED | one merge at 100% |
| PARALLEL_SHAM | 4 at B/4 | FULLY_SHARED | identical seed_root, identical diversity settings -- the diversity-negative control; must produce byte-identical artifact sets (also an engine determinism check) |

**Engine policy vs experimental schedule (brief s.8).** The engine has no
delayed-sharing policy and no post-creation policy change (no such route in
`api.py`). Merge timing is encoded in TWO ways, and both are reported:
- **fork-encoded (primary, engine-enforced):** a lineage runs in an ISOLATED
  world; at the merge seq it is checkpointed and forked into an EMITTING
  child (policy set on the fork spec, runtime.py:1424). Before the fork the
  engine itself forbids crossing; the merge point is a `WORLD_FORKED` event;
  the child's frontier at fork == parent's at checkpoint (an F10 assertion at
  every merge).
- **schedule-encoded (secondary):** worlds are created emitting; the runner
  chooses when to import. The engine cannot enforce this, but the ledger
  proves it after the fact (`ARTIFACT_IMPORTED` seqs); the audit rejects any
  cell whose first import precedes its declared merge seq.

### 3.1 Merge mechanics
At a merge, each destination lineage imports every artifact its policy admits
from every source lineage in the topology, in a FROZEN order (s.8 tests order),
paying `c_I` each. Imported claims enter the researcher's hypothesis set with
status `IMPORTED_UNVERIFIED`; whether the researcher verifies before use is a
recipient policy (s.6, s.10): `BLIND` (adopt), `VERIFY_ONE` (spend one
experiment re-testing a decisive prediction of the claim), `FALSIFIER_FIRST`
(any imported falsifier whose transition is re-tested and confirmed kills the
claim regardless of how many worlds assert it).

### 3.2 Synthesis phase
Per (condition, world): one fresh synthesis world (its own client), budget
`B_syn`, policy EXPLICIT_IMPORT_ONLY, importing from the condition's terminal
lineage worlds (all of them for parallel conditions; the one for serial; for
PARALLEL_ISOLATED, four SEPARATE synthesis worlds, one per lineage, plus the
union score). A fixed deterministic SYNTHESIZER consumes the imported
artifacts (STRUCTURED or RAW per condition), spends `B_syn` on order-rule
discovery and verification, and submits plans/certificates on `Syn(w)`. It
logs every artifact id it reads (self-attested; s.7 makes it causal).

---

## 4. Diversity manipulation (brief s.14)

Six axes, each with a frozen menu:
1. `seed_root` (engine-native; controls query tie-breaks);
2. **initial hypothesis order** -- which component the researcher pursues
   first: A-first / B-first / C-first / round-robin;
3. **representation** -- a fixed invertible basis change `M` applied to every
   state the lineage sees. The invariant family the researcher searches is
   SPARSE (Hamming weight <= 2 in its own basis). `a*` is sparse in some bases
   and dense in others, so representation decides whether component A is
   discoverable by that lineage at all. This is the mechanism by which
   diversity could yield complementarity -- if it does;
4. **search heuristic** -- query selection: random / max-split (version-space
   halving) / goal-directed;
5. **information diet** -- allowed query types: transition-only /
   admissibility-only / plan-only / mixed;
6. **DSL ordering** -- enumeration order of `R` and `F_B` (4 frozen orders).

| level | lineages differ in |
|---|---|
| LOW_DIVERSITY | seed only |
| MEDIUM_DIVERSITY | seed + initial hypothesis order |
| HIGH_DIVERSITY | all six axes, assigned so no two lineages share any axis value |
| SHAM | nothing (PARALLEL_SHAM above) |

Run at matched `B_total` under PARALLEL_LATE_MERGE and PARALLEL_FULL_GOVERNED.
**Optimum test:** the primary endpoint as a function of level is reported as
three paired contrasts (LOW-MED, MED-HIGH, LOW-HIGH) with CIs. Monotonicity is
NOT assumed. A pre-declared "too much diversity" signature: HIGH beats LOW on
unique coverage (s.5 of brief) but loses on composite rate -- diverse
lineages whose artifacts the synthesizer cannot reconcile (different bases ->
claims about `a*` expressed in incompatible coordinates; the synthesizer has a
fixed reconciliation routine, and whether it succeeds is data, not design).

**Diversity is measured, not just assigned:** per-lineage discovery sets
(claims made, claims killed, failure classes, repair classes, instances solved,
falsifiers found); pairwise discovery-set Jaccard; unique-coverage share;
marginal contribution to the union; conditional gain after import
(solve-rate delta of lineage j's synthesis after importing lineage i alone).
The test (brief s.5) is whether MEASURED complementarity PREDICTS
provenance-verified composite success across cells (Spearman, with CI, over
all parallel cells) -- not whether a diversity metric is large.

---

## 5. Crossing topologies and order (brief s.8)

| topology | crossings |
|---|---|
| NONE | -- (PARALLEL_ISOLATED) |
| STAR | spokes never exchange; only the synthesis hub imports from all |
| MESH | at each merge, every lineage imports from every other |
| STAGED | (L1,L2) and (L3,L4) merge at 50%; the pairs merge at 100% |
| HIERARCHICAL | STAGED plus a hub that imports the two pair-merges |
| DELAYED | MESH with a single merge at 100% (== PARALLEL_LATE_MERGE) |
| CHAIN | SERIAL_RESTART |

**Order test.** Within MESH and CHAIN, the import order is a frozen
permutation; each cell is run under 2 additional permutations (drawn from a
frozen seed). `ORDER_SENSITIVITY` = fraction of cells whose synthesis outcome
(solved set) changes under permutation. Pre-declared: `ORDER_SENSITIVITY >
0.2` under BLIND recipients and `<= 0.05` under FALSIFIER_FIRST recipients
would mean order matters only through blind adoption -- a recipient-policy
result, not an ecology result. Anything else is reported as found.

---

## 6. Failure-vs-success sharing (brief s.15)

At MATCHED ARTIFACT VOLUME (each source lineage emits exactly `n_art` artifacts
per merge; kinds differ by condition; volume is enforced by the runner and
audited from `ARTIFACT_CREATED` counts): FAILURES_ONLY / SUCCESSES_ONLY / BOTH
(FULLY_SHARED) / NEITHER (ISOLATED). Scored downstream: time-to-first-
falsification of a wrong candidate (in experiments); DUPLICATED DEAD-END RATE
= fraction of a recipient's experiments that re-test a (hypothesis, query)
pair already falsified in an artifact it had legally available at that seq
(computed from F10 frontiers + its own ledger -- this is the measure of
"rediscovering known dead terrain"); hypothesis-set diversity; discovery
rate; composite rate.

**Contextual-failure control (mandatory).** The ecology spans several WORLDS
(different hidden dynamics). A failure artifact from a lineage in world `w'`
is legitimate evidence that is WRONG in world `w`. Condition
`FAILURES_MISMATCHED`: the recipient receives failure artifacts of matched
volume from a lineage on a different world (Topology-2's A5 construction,
made cross-world). Predicted: BLIND recipients prune true hypotheses and lose
to ISOLATED; FALSIFIER_FIRST recipients pay one experiment per imported
failure to re-test it and are protected. Whether failure sharing helps
depends on this policy interaction; the design measures the interaction, not
the main effect alone. `FAILURES_MISMATCHED` also answers the brief's second
question: does sharing failures suppress paths that fail in one context and
work in another? Cells where the recipient abandoned a hypothesis that was
TRUE in its world because of an imported foreign failure are counted as
`NEGATIVE_TRANSFER` events, with the artifact id and seq.

---

## 7. Causal composition audit (brief s.7, s.9)

For every synthesis instance solved:
1. **Availability**: `knowledge_set(syn_world, seq = commit_seq(solving
   experiment) - 1)` captured and stored with the result. Anything with
   `first_available_seq` later is listed under "could not have explained R".
2. **Consumption**: the synthesizer's read log (artifact ids it fetched via
   F1, with `source_hash` verified against the returned bytes). Self-attested;
   disclosed as such.
3. **Source set**: origin lineages of consumed artifacts, from `source_world`
   on the IMPORTED rows.
4. **Leave-one-source-out (LOSO)**: for each origin lineage `i`, the synthesis
   world is re-created from scratch WITHOUT lineage `i`'s imports (a fresh
   world, not a fork -- a fork would inherit the frontier), same `B_syn`, same
   synthesizer, same seed. `COMPOSITE` iff solved with the full set AND
   unsolved under every single-lineage removal for at least two distinct
   lineages. LOSO on a fresh world is engine-enforced: the removed artifacts
   are absent from F10's frontier, and that absence is what is checked.
5. **Shuffled-source control**: the same import volume with each artifact's
   claim payload replaced by a claim from a DIFFERENT world (labels shuffled,
   bytes-volume matched). Solves under shuffle are counted; the primary
   contrast subtracts nothing but REPORTS the shuffled rate beside it, and
   falsifier 4 fires if they coincide.
6. **Ancestor check**: if any single lineage's own synthesis (PARALLEL_ISOLATED
   scoring) already solves the instance, the instance is not composite for
   that cell, whatever the LOSO says.

**Qualification rule (brief s.9):** a result whose frontier cannot be
reconstructed from the ledger (F10 error, missing seq, discontinuous hash
across the solving experiment) DOES NOT QUALIFY. It is void, listed, and its
cell is marked `UNRECONSTRUCTIBLE` in the results.

---

## 8. Duplicate evidence and the replication distinction (brief s.12)

Two lineages will derive the same fact. Five constructions, each planted
deliberately in campaign worlds, and what the engine can and cannot see:

| construction | how planted | engine visibility (predicted from code) |
|---|---|---|
| same evidence | L1, L2 issue identical queries (forced by diet+seed) and emit identical STRUCTURED artifacts | two NATIVE rows, equal `blob_hash`, different worlds; NO relation recorded (runtime.py:1094 -- native creation has no derivation provenance) |
| independent evidence | different queries, same conclusion | two NATIVE rows, different bytes; nothing links them; nothing distinguishes this from the row above except the bytes |
| shared upstream | both forked from a parent holding the observations | `INHERITED` basis in each child's frontier (F10) -- distinguishable |
| transformed copy | L2 reads L1's artifact (F1), re-encodes, emits NATIVE | NATIVE row, new hash; indistinguishable from independent derivation |
| imported copy | legal import | `origin=IMPORTED`, `source_world`, `source_hash` -- fully distinguishable |

A downstream world can therefore distinguish IMPORTED and INHERITED from
NATIVE, and NOTHING among the NATIVE cases. F3's `REPLICATION` typing is
intra-world (an observation of the same experiment); there is no cross-world
replication relation. The design tests this rather than assuming it: the
synthesizer is given a REPLICATION_COUNT routine (count of distinct source
lineages asserting a claim with disjoint evidence hashes) and the audit
reports how often that count is wrong against the planted ground truth. The
expected outcome is that "same evidence" and "transformed copy" are counted
as independent replications. If so, that is `SUBSTRATE_GAP: cross-world
replication is not encodable in GEN-2.1`, filed in ENGINE_DEFECTS as a gap
with severity per its contamination potential (it inflates replication-based
confidence in every ecology that counts sources), NOT papered over.

**Consensus is not truth (brief s.13).** Planted majority-wrong worlds:
`3 wrong : 1 right` and `7 wrong : 1 right`. The wrong lineages share an
information diet restricted to a subspace `V` on which a decoy invariant
`a_decoy` agrees with `a*`; they emit `success: a* = a_decoy` with real,
correct-on-V evidence. The one right lineage's diet reaches a state outside
`V`, falsifies `a_decoy` (engine-adjudicated FALSIFIED in its world), and
emits both the failure and the true claim. Synthesis recipients: `VOTE`
(majority -- the negative control, expected to fail every A-type synthesis
instance), `FALSIFIER_FIRST`, `VERIFY_ONE`. Engine-level assertion: the
right lineage's hypothesis remains `FALSIFIED` in its own world regardless of
what is imported anywhere (trivially true in GEN-2.1 because hypotheses have
no cross-world identity -- also filed as a substrate fact: the ecology cannot
ask the engine "is claim X falsified anywhere?"; it must do so client-side by
content hash).

---

## 9. Concurrency torture plan (brief s.10-11, s.18)

**Where.** (a) A PRIVATE engine instance on M2 built from the pinned source
hash (`serve.py --db <scratch> --host 127.0.0.1`), for destructive load,
restart and release-discontinuity tests; the hash is asserted equal to the
live instance's before any result counts. (b) The LIVE instance for
non-destructive bursts in an announced window (M2_STATUS + Daedalus notice),
campaign worlds only, never production worlds. Correctness findings must
reproduce on BOTH to be filed at CRITICAL; a live-only failure is filed with
the live build identity and marked `LIVE_ONLY`.

**Static reading that shapes the attack** (runtime/store/api, this build):
- every request constructs a `Foundry` -> `Store.initialize()` ->
  `executescript(_SCHEMA)` + `BEGIN IMMEDIATE` for the schema-version check
  (store.py:380-386). EVERY request, including GETs, takes the write lock at
  least once. `busy_timeout` 30 s. Single uvicorn process; sync endpoints on
  the default 40-thread pool.
- `put_blob` writes the filesystem INSIDE the write transaction before the SQL
  insert (runtime.py:1092); rollback leaves orphan blobs (harmless) and two
  concurrent identical creates race on `path.exists()` + `os.replace`
  (atomic; harmless) -- to be confirmed, not assumed.
- `create_artifact` uses `INSERT OR IGNORE` after appending `ARTIFACT_CREATED`
  (runtime.py:1097): a second identical create in one world emits a SECOND
  creation event for an artifact that is not re-created. Ledger says 2
  creations; table says 1. Probe P-A7.
- idempotency: key row + object + debit in one txn (runtime.py:157-188);
  `_idem_check` happens after `_authorize` inside the txn -- so two concurrent
  same-key requests serialize on the write lock; the second sees the row. Should
  hold. Attack anyway: the same key from two CONNECTIONS in the same client
  under lock-timeout pressure, where the first txn may have ROLLED BACK on a
  lock timeout while the client saw a transport error.

**Race matrix** (each run as a burst of N in {8, 32, 128} simultaneous
requests from a thread pool with a synchronized start barrier; 5 repetitions;
oracle = post-hoc ledger audit, never the responses alone):

| # | race | expected invariant | oracle |
|---|---|---|---|
| R1 | same `Idempotency-Key`, same body, concurrently x2..x32 | one object, one event, one debit; every 2xx body identical | count rows/events for that key; `/resources` consumed delta == 1 |
| R2 | same key, different bodies | exactly one 2xx, the rest 409; the winner's body is the stored one | key row `request_hash` == winner's; no second object |
| R3 | same key, different worlds | exactly one world gains the object; others 409; no cross-world dedup that silently drops a write into world B while reporting success | per-world object counts |
| R4 | `create_experiment(commit=false)` retries with one key while `commit` fires | one experiment, one `committed_seq`, one debit; commit never applies to a phantom | experiments table, `EXPERIMENT_COMMITTED` count, budget |
| R5 | import racing artifact creation | import returns 404 (not yet) or 2xx with `source_hash` == created hash; never a row with NULL/mismatched hash | join imported rows to source rows |
| R6 | `knowledge_set(seq=N)` polled during concurrent imports | identical output for fixed N across all reads; frontier at N+1 >= at N (monotone); no item with `first_available_seq > N` | pairwise equality of captured frontiers |
| R7 | fork while parent receives imports | child frontier at fork seq == parent frontier at checkpoint seq, independent of interleaving; `WORLD_FORKED.artifacts` == frontier hashes | F10 both sides |
| R8 | import into parent between checkpoint and fork; import into child at fork+1 | parent's post-checkpoint import NOT in child; child's own import not in parent | F10 both sides; `fork_point` index |
| R9 | replication observations concurrent (with/without `replication=true`) | exactly one ORIGINAL; extra un-flagged -> 409; flagged -> REPLICATION rows; hypothesis status never re-adjudicated; FALSIFIED never becomes SURVIVED | observations table `evidence_role`; CLAIM_* events count |
| R10 | two CLIENTS bind evidence to one experiment | non-owner 403 with NO event, NO row; owner unaffected | ledger of both |
| R11 | burst straddling an engine restart (private) | every committed request durable; in-flight requests either fully applied or absent; idempotent retries after restart replay, never duplicate | pre/post object counts vs. client-side intent log; `ledger_integrity_ok` |
| R12 | burst straddling a release-hash change (private; one-byte source edit -> new hash) | every response carries a hash; exactly one transition observed per client; `EXPERIMENT_COMMITTED` after the transition stamps the new hash; no response after the transition carries the old | header log; committed events' stamped hash |

Plus ordering/invariant probes run continuously during science: global
`event_seq` strictly increasing and gap-free per world (`world_index`);
`ledger_integrity_ok` on every world at every merge; prospective boundary
(a prediction registered one seq after commit must be refused / marked
retrospective) with a planted late-prediction probe once per phase; budget
atomicity under `budget_exhausted` bursts (consumed never exceeds limit; the
block is durable); origin-only re-export (A->B->C denied); append-only
(re-verify chains after every burst).

**Throughput collapse curve.** Concurrency `n in {1, 2, 4, 8, 16, 32, 64,
128, 256}` clients, mixed workload (60% epistemic POSTs, 25% GETs incl.
`knowledge_set`, 10% imports, 5% forks), 60 s per level. Recorded: p50/p95/
p99 latency, timeouts, HTTP 5xx, `database is locked` occurrences (server
log), retry counts, lock-wait time if exposed. A collapse WITHOUT any R1-R12
violation is `ENGINE_DEGRADED`, filed as GEN-2.2 evidence with the curve.

**Estimated maximum safe concurrency (brief s.22 item 14).** From the code:
per-request `Foundry` construction plus one write-lock acquisition even on
reads; service time estimated 5-30 ms; the GEN-2 in-process load test
reported ~387 units/s (INVARIANTS doc T18) so the HTTPS + per-request-init
path is estimated at 30-100 req/s serialized. With a 40-thread pool, in-flight
requests cap at 40 and latency at saturation ~ 40 x service time (0.2-1.2 s).
Lock timeouts (30 s) need > ~1000 queued acquisitions and should not occur
below ~64 concurrent clients; beyond that, the anyio pool queues and CLIENT
timeouts (sfclient default 30 s) become the failure mode, producing retry
storms -- which is exactly the F5 stress. **Estimate: safe <= 16 concurrent
clients (no timeouts, p95 < 1 s); degraded 32-64; collapse >= 128.** The
science runner will use 8 until the curve is measured. This is an estimate
from reading, to be replaced by the measured curve; if the measured safe
level is < 8, the science schedule is re-planned before any confirmatory run.

---

## 10. Harmonia A / B import experiment (brief s.17)

D15-A's design packet is committed (`genesis/harmonia_a/d15a/`,
2026-09-02); no D15-B packet exists in the repository at this writing --
"repo state is not program state", so B is assumed active and the branch is
specified against whatever B freezes. Rules:
- Their artifacts reach me ONLY by legal cross-client import: they mint or
  accept a registered topology group, set emitting policies on FORKED
  children of their frozen worlds (their own worlds' policies are fixed at
  creation and presumably ISOLATED), and hand me the group id out of band.
  Nothing else counts. If they decline or are not at a freeze point, the
  branch is `NOT_RUN`, recorded as such.
- **Adapter freeze**: their artifact schemas are not in my problem's
  vocabulary. A deterministic ADAPTER (their schema -> my synthesizer's
  claim types, or `UNCONSUMABLE`) is written from their PUBLISHED schema
  only, hashed and journaled BEFORE any of their result artifacts are
  imported. The adapter's `UNCONSUMABLE` rate is reported; if it is 100%,
  the branch's honest reading is "no channel", not "no transfer".
- Branches, at pre-registered points (after my Phase 2 pilot, before
  confirmatory): `C_LOCAL`, `C_IMPORT_A`, `C_IMPORT_B`, `C_IMPORT_A_B`,
  `C_IMPORT_SHUFFLED_CONTROLS` (their artifacts with payloads permuted across
  their own instances; volume matched). Endpoint: my held-out synthesis solve
  rate per branch at matched `B_total` (imports charged at `c_I`).
- Declared prior: `P(useful transfer) ~ 0.15`. Their worlds (Z_8^3 repair
  identifiability; controlled transfer) are not my worlds; a transfer, if it
  occurs, would most plausibly be METHODOLOGICAL (e.g. an A-lineage artifact
  encoding "invariant class X excluded" in a form my adapter can map to a
  linear-functional exclusion). That is why it would be strong evidence: the
  artifacts were not made for me. If nothing transfers, that is the record.

---

## 11. Statistical plan and power

**Unit of pairing:** the WORLD (hidden dynamics + its instance sets). Every
condition, topology, diversity level and recipient policy is run on the SAME
worlds; contrasts are within-world.

**Primary endpoint:** `COMP(cond, w, B)` = fraction of INTERACTIVE synthesis
instances (A+C, A+B+C) in `Syn(w)` solved by the condition's synthesis world
at matched `B_total`, AND provenance-complete (s.7 steps 1-3 reconstructible).
Primary contrast per regime: `D_prim(B) = COMP(PARALLEL_LATE_MERGE) -
COMP(SERIAL_MONOCULTURE)`, world-paired bootstrap CI (10,000 resamples, seed
20260916). Companion contrasts, same machinery: vs SERIAL_RESTART; LATE_MERGE
vs ISOLATED-UNION (falsifier 2); FULL vs SHUFFLED (falsifier 4); EARLY vs LATE
(falsifier 7); FAILURES_ONLY vs ISOLATED on duplicated-dead-end rate
(falsifier 8).

**Secondary endpoints** (all with CIs): unique useful discovery coverage;
experiments-to-first-falsification; redundant work rate (duplicated dead-end
rate); negative-transfer event rate; diversity retention (hypothesis-set
Jaccard between lineages at end vs start); provenance-complete composition
rate (`COMPOSITE` per s.7 among solved); independent-replication rate (and
its error against planted ground truth, s.8).

**Frozen bands (verbatim at freeze):**
- `ECOLOGY_SUPERADDITIVE(B)`: `D_prim(B) >= +0.10` with CI excluding 0; AND
  `COMP(LATE_MERGE) - COMP(ISOLATED_UNION) >= +0.10` with CI excluding 0; AND
  `COMP(FULL) - COMP(SHUFFLED) >= +0.10`; AND `COMPOSITE` rate among solved
  interactive instances `>= 0.5`; AND SERIAL_RESTART does not match LATE_MERGE
  within 0.05 (else the verdict is `TEMPORAL_ECOLOGY_SUFFICES`, a narrower
  positive that does not support "parallel").
- `ECOLOGY_UNION_ONLY(B)`: `COMP(LATE_MERGE) - COMP(ISOLATED_UNION)` CI
  within [-0.05, +0.05] while `D_prim(B) > 0`.
- `ECOLOGY_REDUNDANT(B)`: `D_prim(B)` CI entirely below +0.05.
- `ECOLOGY_HARMFUL(B)`: any crossing condition below ISOLATED by >= 0.10 with
  CI excluding 0 (reported by condition; monoculture signature = diversity
  retention collapse under EARLY_MERGE).
- `D16C_INDETERMINATE`: anything else, or > 10% of cells void.
The verdict is issued PER REGIME; the campaign verdict is the triple.

**Power.** Pilot: 12 worlds, all conditions, `B_total = 48` only, non-
confirmatory, disclosed. Sample-size rule (frozen): confirmatory N worlds per
regime = smallest N with predicted 95% CI half-width of `D_prim` <= 0.05
(half the band), from pilot variance, journaled before freeze. Anticipated N
= 36-60 worlds per regime. Scale: ~11 conditions x (4 lineages + synthesis +
LOSO re-runs ~4) ~ 100 engine worlds per (world, regime); x 48 x 3 ~ 14,000
engine worlds; ~80-100k experiments; ~350k requests. At a measured 30-60
req/s that is 2-3 engine-hours of pure service time, spread over days with a
cell-resumable runner (transport timeouts are never results; retries carry
the same idempotency key).

---

## 12. Scientific falsifiers -> tests

| # (brief s.20) | falsifier | test |
|---|---|---|
| 1 | isolated parallel gives no coverage advantage at matched budget | unique-coverage(ISOLATED_UNION) - coverage(SERIAL) per regime |
| 2 | crossing adds nothing over union | LATE_MERGE vs ISOLATED_UNION band |
| 3 | purported composition does not require multiple lineages | s.7 LOSO + ancestor check; `COMPOSITE` rate |
| 4 | shuffled artifacts give the same gain | FULL vs SHUFFLED |
| 5 | benefit is marginal-prior estimation | control: a SERIAL lineage given the generator's marginal class priors as a free artifact; if it matches LATE_MERGE, the benefit was prior estimation |
| 6 | diversity does not predict complementarity | Spearman(measured complementarity, COMPOSITE) across parallel cells, CI |
| 7 | early sharing -> monoculture and late no better | EARLY vs LATE on diversity retention AND COMP |
| 8 | failure sharing does not cut duplicated dead ends | FAILURES_ONLY vs ISOLATED on duplicated-dead-end rate, plus FAILURES_MISMATCHED |
| 9 | no transfer to held-out composition tasks | `Syn(w)` is held out by construction; plus a HELDOUT GENERATOR REGIME (fresh op families, shifted `F_B`, never used in pilot) for the primary contrast |
| 10 | serial matches or beats parallel at equal cost | `D_prim(B)` and vs SERIAL_RESTART, per regime |

**No-rescue rule.** No task redesign, no new condition, no reweighting after
the first confirmatory result is opened. Calibration happens in the pilot and
is journaled as amendments; the confirmatory freeze is final. There is no
ninth experiment.

---

## 13. Engine falsifiers -> tests

| # | falsifier | test (s.9) |
|---|---|---|
| 11 | concurrent retries duplicate epistemic writes | R1, R4, R11 |
| 12 | budgets double-debit | R1, R4 debit oracle; `budget_exhausted` bursts |
| 13 | KnowledgeSet race-dependent | R6 |
| 14 | fork inheritance depends on request timing, not committed order | R7, R8 |
| 15 | duplicate reports masquerade as independent replication | s.8 planted constructions; F3 intra-world via R9 |
| 16 | provenance cannot establish causal source contribution | s.7 (read-ledgering absent; LOSO is the only causal path) -- filed as GAP with the exact missing primitive |
| 17 | release discontinuity not observable on wire | R12 |
| 18 | cross-world content can be laundered | P-L1: B imports A's artifact (legal), reads bytes (F1), re-creates as NATIVE, C imports from B cross-client (H6 checks only the row's origin -- predicted to SUCCEED, i.e. launder); P-L2: same with a one-byte transform |

Severity classes: CRITICAL (lost write, duplicate debit, inconsistent seq,
idempotency violation, laundering that defeats H6, F10 misreport that could
make a prospective result future-informed); HIGH (correctness gap with no
contamination of D16-C results); MEDIUM (degradation with retry storms);
LOW (documentation/engine discontinuity, orphan events). Every ENGINE_DEFECT
carries `may_contaminate_science: true|false` and the affected cells are
voided when true.

---

## 14. Five most plausible ways GEN-2.1 fails under this campaign

Ranked by my credence, from static reading of `sfe/` at hash `5274ddbe`:

1. **Native re-creation launders content across clients (falsifier 18).**
   H6 blocks re-export of an IMPORTED row only. A world that legally imports,
   reads the bytes (F1), and creates a NATIVE artifact with the same bytes has
   a NATIVE row with the same `blob_hash`, importable by a third client. The
   engine keeps no global blob-hash -> origin index that would flag "this
   NATIVE artifact's bytes already exist as an import in this world". P-L1.
   Credence it launders: 0.85. Severity: CRITICAL for any ecology that treats
   NATIVE as "derived here".
2. **Cross-world duplicate evidence is unencodable (falsifier 15).** Two
   NATIVE artifacts with equal bytes in two worlds have no recorded relation;
   F3's replication typing is per experiment within a world. Credence 0.95
   (by construction). Filed as SUBSTRATE_GAP, HIGH: it contaminates any
   replication-count policy (s.8).
3. **F10 provenance basis flips for inherited-then-recreated content.** In
   `_reconstruct_frontier` (runtime.py:1197-1247) native rows are added first
   and their hashes put in `seen`; an inherited item with the same hash is
   then skipped. Without a cutoff the item reports `basis=native_creation,
   first_available_seq = native seq`; with a cutoff between the fork seq and
   the native seq it reports `basis=fork_inheritance, first_available_seq =
   fork seq`. The reported first availability of ONE content hash depends on
   the query. Credence 0.8. Severity MEDIUM (availability is still never
   over-reported under a cutoff -- fail-closed holds -- but "first_available_
   seq is authoritative and monotonic" is not true as stated). R6/R7 variants.
4. **Throughput collapse with retry storms, without correctness loss.**
   Per-request write lock even on reads; 40-thread pool; 30 s client timeout
   -> at >= 64 concurrent clients, timeouts -> retries -> the same key arrives
   at a server that may or may not have committed. Credence 0.8 that the
   collapse is severe; credence 0.25 that ANY R1-R12 invariant breaks under
   it. The interesting sub-case: a request whose txn committed but whose
   response was lost -- the retry must replay from the key row (it should);
   and a request whose txn hit the 30 s lock timeout server-side and ROLLED
   BACK, returning 500 with the identity header (fixed in F4) -- the retry
   must create, not conflict.
5. **Contract discontinuities the campaign will trip on day one.**
   `DELAYED_SHARING` documented in API.md, rejected by `create_world`;
   failure objects (I7 first-class) cannot cross except as untyped-by-the-
   ledger artifacts; a second identical `create_artifact` in one world
   appends a second `ARTIFACT_CREATED` event for a row that is not created
   (P-A7). Credence 0.9 each. Severity LOW-MEDIUM, but each one forces a
   client-side workaround that the packet must declare rather than hide.

Not in the top five but probed: `synchronous=NORMAL` in WAL (last committed
txns may be lost on OS crash -- not process crash; outside R11's scope, noted
for Daedalus); the `404`-vs-`403` existence oracle (known, retained by
choice); the artifact-id squat (known LOW; `artifact_id` includes
`world_id`, so it cannot fire between D16-C lineages).

---

## 15. Meta-learning without a learner (brief s.16)

Four deterministic policies, frozen before pilot, evaluated prospectively
against the fixed-schedule conditions at matched cost:
- `NOVELTY_FILTER`: cross an artifact iff its `content_hash` is not already in
  the destination's F10 frontier (uses only F10 + hashes);
- `RELEVANCE_BROADCAST`: broadcast a failure iff the falsified hypothesis is
  still LIVE in the recipient's version space (recipient-side check, costs
  0 experiments);
- `STALL_MERGE`: a lineage requests a merge when its falsification rate over
  its last 6 experiments falls below 1/6 (no discovery -> import);
- `REDUNDANCY_FLAG`: mark an incoming success as redundant iff its evidence
  hashes are a subset of the recipient's own observation hashes.
Endpoint: same primary/secondary endpoints; a policy "improves the ecology"
iff it beats the best fixed schedule by >= 0.05 on COMP with CI excluding 0
at matched cost. No neural component anywhere; if nothing improves, that is
the result.

---

## 16. SFE feature coverage (brief s.18)

| feature | where exercised |
|---|---|
| F1 content retrieval + hash verification | every import is followed by a read; `source_hash` == sha256(bytes) asserted; P-L1/P-L2 laundering |
| F2 all info kinds + policy semantics | conditions in s.3 use every policy except DELAYED_SHARING (rejected -- documented); non-ontology kind -> 422 probe; SUCCESSES_ONLY shares exactly {success} probe |
| F3 replication vs malicious duplicate | R9; planted duplicate observations without flag (must 409); FALSIFIED->SURVIVED laundering attempt |
| F4 build identity | header logged on EVERY response for the whole campaign; R12 |
| F5 idempotency under races/retries | keys on ALL epistemic POSTs; R1-R4, R11; 5% scripted duplicate injection during science |
| F10 frontiers | captured at every synthesis result and every merge/fork; R6-R8; failure mode 3 |
| GEN-2 core invariants | prospective boundary probe per phase; budget atomicity bursts; chain verification after every burst; isolation (R10, cross-client denies); origin-only re-export (A->B->C) |

---

## 17. Defect ledgers (brief s.21)

`genesis/harmonia_c/d16c/SCIENCE_DEFECTS.jsonl` -- one line per finding:
`{hypothesis, falsifier, effect (with CI), uncertainty, replication (which
regime/cells), surviving_narrower_claim, cells_affected}`.

`genesis/harmonia_c/d16c/ENGINE_DEFECTS.jsonl` -- one line per finding:
`{id, reproducer (script path + args), expected_invariant, observed,
engine_source_hash, source_commit, world_ids, event_seqs, ledger_entries,
severity, may_contaminate_science, live_or_private, first_seen_ts}`.
Both are append-only, committed with every push, and never edited in place
(corrections are new lines referencing the old id).

---

## 18. Declared priors and self-dissent

Priors (science, at `B_total = 48`): `ECOLOGY_SUPERADDITIVE` 0.25;
`UNION_ONLY` 0.35; `REDUNDANT` 0.25; `HARMFUL` (some crossing condition) 0.10;
`INDETERMINATE` 0.05. Engine: at least one CRITICAL/HIGH correctness or gap
finding 0.6 (items 1-2 above); throughput collapse without correctness loss
0.8.

Three ways this design could FALSELY support H_ECOLOGY:
1. **Schema smuggling** -- the STRUCTURED artifact schema is a decomposition
   matched to the synthesizer; composition is table lookup. Guard: the
   SHARED_OBSERVATION (RAW) condition; if only STRUCTURED composes, the
   verdict is capped at `SCHEMA_DEPENDENT` and does not support H.
2. **Budget-regime selection** -- reporting the regime where parallel wins.
   Guard: the three-regime triple is the verdict; no single-regime headline.
3. **Diversity by construction** -- the representation axis (s.4 axis 3)
   GUARANTEES that some lineages cannot find `a*` and others can, so
   complementarity is planted, not discovered. Guard: LOW_DIVERSITY (seed
   only) is the honest test of emergent complementarity; HIGH_DIVERSITY
   results are reported as "complementarity available" upper bounds, and the
   falsifier-6 correlation is computed within LOW/MEDIUM only.

Three ways the FOUNDRY could corrupt the conclusion without crashing:
1. Laundering (s.14 item 1) makes an IMPORTED fact look NATIVE in a lineage,
   so the LOSO audit attributes a composition to the wrong source -- detect by
   global blob-hash cross-reference in the audit (client-side).
2. Frontier basis flip (s.14 item 3) mis-times availability for recreated
   content -- detect by asserting frontier equality under both query forms
   at every merge.
3. Stale idempotent replay after a schema-blind change to a request body
   (e.g. the runner amends `spec` but reuses a key): a 409 that the runner
   swallows as "already done" silently drops a write -- guard: the runner
   never swallows 409 on a key; every 409 is logged with the intended body
   hash and reconciled.

---

**STOP.** Per brief s.22 this packet halts here for review. Nothing has been
run: no generator instance exists, no engine world has been created for
D16-C, no burst has been fired at the live instance, no adapter has been
written. On approval the sequence is: Phase 0 (private-instance torture R1-
R12 + collapse curve; live announced window) -> generator census -> pilot (12
worlds, B=48) -> power freeze -> adapter freeze (if A/B at a freeze point) ->
confirmatory freeze (bands verbatim from s.11, freeze hash embedded in
engine-registered predictions) -> campaign -> two independent verdicts.
