# New finite reference harness

This is a NEW, small, stdlib-only reference implementation. It is not the
absent ChatGPT harness, an audit execution of that harness, a native scientific
instrument, or a genuine strong-recursion positive. The adjacent design and
test-plan audits informed this implementation; their wider requirements are
not implicitly implemented. All PASS results mean only finite contract PASS.

## Running and execution status

From this directory, with Python 3.8 or newer, run:

`python -B -m unittest discover -v`

The final discovery inventory is 28 tests: 14 contract tests, 9 finite-world
tests, and 5 source-mutation tests. Each mutation test additionally executes its
unmodified probe once and its mutated probe once in memory; these nested runs
are not added to unittest's top-level count. Subtests are not independent trials.

Parent execution on BUCKKEEP with Python 3.13.5: 28 tests passed, exit 0,
including five source-mutant assertion kills. The delegated implementation
session had no command runner; this parent receipt supersedes that NOT RUN
handoff. See ../VALIDATION.md for the observed two-test red/green binding repair,
final validation and delivery. These are development-time tests, not a
preregistered scientific experiment or independent replication.

## Implemented scope

- Four statuses: PASS, FAIL, BLOCKED, UNQUALIFIED. Missing required facets,
  artifacts, anchors or dependencies BLOCK; supplied bad evidence FAILs;
  an anchored null detector observation is UNQUALIFIED. Strong recursion is
  always UNQUALIFIED, even with complete fixture evidence. Other unsupported
  claims BLOCK. Combined evidence priority is FAIL > BLOCKED > UNQUALIFIED >
  PASS; all collected evidence reasons are preserved. Graph structural errors
  stop evaluation at the first error; strong-recursion refusal precedes it.
- Immutable evidence/claim nodes and DAG snapshots, copied tuple containers,
  eight exact scope axes, cycle/role/scope checks, duplicate rejection,
  checker-owned fixed v1 policies, and transitive invalidation. Invalidation
  returns a new snapshot, retains the old one and leaves unrelated claims
  intact. This is not an authenticated persistent event log.
- Artifact bytes are supplied in memory. Both byte length and SHA-256 are
  checked against immutable references AND separately supplied caller anchors.
  Each external anchor is the complete expected evidence Node, including ID,
  scope, predicate and dependencies, not just an artifact hash. A whole-graph
  relabel or removed dependency cannot reuse unchanged external anchors.
  Artifacts are at most 4096 bytes; graphs at most 64 nodes; parsed JSON depth
  at most 8. Booleans, floats, duplicate object keys and malformed observations
  cannot pass as measurements. Bare PASS or reset-complete labels are not truth.
- Exact uniform-key recovery with 1..4 keys/messages; bound min(1,L/M);
  all 256 two-message/four-key deterministic encoder/decoder pairs; carry,
  fixed-answer no-carry, flip and independent-donor controls. The bound assumes
  no other key-correlated side information; no physical memory-bit inference.
- Directed 0->1->2 search, founder score given, proposals charged, fixed budget
  two for checked records. Strict/nondecreasing ascent, plateau and valley;
  unconditional chain enumeration; cold lineage (0) versus repair (2,1).
  Checked search records replay the valley trace and require a functional hit.
  A repair hit does not imply cold reach; a failed bounded search is not
  impossibility. Lineage consistency is checked, not physical custody proved.
- Four-state continuation with explicit traces; a missing checkpoint bit fails.
  Reset has an allowed bit and a forbidden in-flight bit with an actual later
  delivery route. Clean reset erases the packet while preserving allowed state;
  display-only reset leaks; indiscriminate erasure violates preservation.
- Plain and one-hot re-encoding, mapped readouts, and a first-coordinate-biased
  ruler counterexample. These are two encodings, NOT unlike native physics.
- Exact rational history-conditioned updater: calibration learns beta; B builds
  eta=1/(beta*x); U contains only frozen eta and receives no V input at C.
  Both fresh +/-1 target branches start at zero after A/B, with gradient as the
  only target-dependent observation. beta,x in {1,2} are exhausted. Clamp/swap
  controls test mediation; an open V bypass is a separate adversarial witness.
  Gradient withholding returns zero. Flattened computation is equivalent on
  the declared finite domain. Sign-gradient R0 also solves all 8 tasks: zero
  accuracy advantage, no economic claim, and no strong-recursion inference.

## API inputs, policy and trust boundary

`evaluate(graph, claim_id, blobs, anchors)` accepts validated frozen Node/Graph
objects, a claim ID, a mapping from artifact key to bytes, and a separate
mapping from artifact key to trusted evidence Node (including its Artifact).
Scope order:
physics, search, world, development, boundary, resources, measurement, exposure.
Malformed constructors raise ValueError; this is not a general untrusted parser.

Policies are exactly: retention -> retention/channel/detector;
cold_reach -> cold/detector; repair_reach -> repair/detector;
continuation -> continuation; reset -> reset; reencoding -> encoding;
updater -> updater. These are fixture contracts, NOT a scientific L-level matrix.
Expected observation tables are fixed in checker.py, not supplied by producers.
Source observations are (0,1); detector counts are (2,1,0); channel maxima are
(1,2,4). Other table row orders follow the explicit loops in test_contracts.py.
Updater columns: trained, flattened, eta=1 clamp, swapped, no-gradient, R0.

Caller/checker code and invalidation authority are trusted. Anchors must come
from outside the evidence producer for a meaningful integrity boundary. Tests
construct synthetic anchors locally; that does not establish independent
custody, authorship, preregistration or truthful execution. Consistent fabricated
data, forged ancestry plus rewritten anchors, selective omission and hidden
channels are outside this checker. Scope labels cannot certify real physics.

## Source mutants and semantic adversaries

Each of five source mutants changes one unique checker.py expression, compiles
that source in a temporary in-memory module and runs a named assertion probe.
No source file is overwritten. Module registration is removed in finally.
Compile/import/runtime errors or skips are NOT kills; exactly one assertion
failure with zero errors is required, after the unchanged probe succeeds.

| Mutant | Probe | Parent execution |
| --- | --- | --- |
| Missing facet check disabled | Missing each required facet | KILLED: assertion |
| External evidence binding skipped | Entire graph relabeled under old anchors | KILLED: assertion |
| Repair/cold comparison bypassed | Repair trace claimed cold | KILLED: assertion |
| Artifact digest comparison skipped | Same-length whitespace substitution | KILLED: assertion |
| Invalidation uses seeds only | Grandchildren and unrelated claim | KILLED: assertion |

The original scope-only mutant was replaced after adding the second defense:
external binding. Disabling only the internal scope check then changes a reason
code but does not falsely admit evidence. The final binding mutant exercises an
actual false PASS on a graph whose nodes all agree on the wrong scope.

Additional adversarial inputs include wrong retained answers, detector absence,
cycles, dangling/self-support, rewritten internal hashes, malformed JSON,
missing checkpoint state, live reset packet, biased ruler and open V bypass.
Manual constants and separately coded enumerations are cross-checks, not
independent authorship, preregistration or empirical scientific qualification.

## Not implemented

No untrusted filesystem loader, CLI writer, network, package installation,
signature/identity service, external custodian, sealed complete-run inventory,
native runtime adapters, real physical interventions, stochastic equivalence,
observer/RNG/scheduler qualification, unlike-physics panel, resource economics,
independent replication, holdout access enforcement, scientific counterfeit
detector, or strong-recursion detector. In particular this does not fulfill
the absent harness's complete H0-H9 or the main design/test documents. Tests
read checker source only to compile controlled mutants in memory; -B prevents
bytecode writes. There is no application stdout or secret/config access.