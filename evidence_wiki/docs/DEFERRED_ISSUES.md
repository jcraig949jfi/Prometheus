# Deferred issues — documented, deliberately NOT hardened

Frozen 2026-09-04 (durability/diagnostics pass, Task 3). Each of these is a
real gap. None is being changed in this pass, because changing them during
Harmonia's active integration phase risks forcing her to adapt mid-flight.
Each entry states the risk, who it can bite, and what the fix would be.

## D1 — No off-host way to check prod-view visibility

An agent on M2 sets `namespace` independently on claims, evidence and
relations; the default is `"prod"`. Miss one and the object enters the
scientific views. Verifying that today requires SQL on M1
(`ew.claims_prod` / `ew.evidence_prod` / `ew.relations_prod`), which a remote
consumer does not have.

RISK: a practice object silently becomes part of the scientific corpus, and
the writer cannot detect it from where they work.
FIX (additive, no adaptation): a read-only endpoint returning the objects a
given agent/machine has written that are currently visible in the prod views.
STATUS: deferred. Mitigation meanwhile: Harmonia's first run set
`namespace: test` correctly on every object, and Mnemosyne can audit on M1 on
request.

## D2 — Cross-namespace binding is not prohibited

Nothing stops evidence in one namespace from binding to a fossil encounter in
another: `prod` evidence may reference a `test` encounter, and vice versa.
The foreign key checks existence, not namespace agreement.

RISK: scientific evidence anchored to a practice fossil, which would be a
provenance smell that no gate currently catches.
FIX: either a hard reject, or a warning surfaced on write and on the
provenance traversal.
STATUS: deferred BY INSTRUCTION — a hard namespace-binding rule is a contract
decision and must not land during the active integration phase. Latent, not
live: Harmonia's first run was consistently `test` on both sides.

## D3 — Connection-pool fallback can open unbounded direct connections

`ew/db.py` uses `ThreadedConnectionPool(2, 16)`. If the pool is exhausted or
broken, `connect()` falls back to opening a direct psycopg2 connection, with
no ceiling on how many.

RISK: under sustained concurrency the fallback could exhaust PostgreSQL's
`max_connections` (currently 100, with ~9 in use), turning a slowdown into
service-wide failure.
FIX: bound the fallback (small semaphore or a hard cap with a 503), and log
whenever it fires so exhaustion is visible rather than inferred.
STATUS: deferred. Not close to the limit today; the fallback exists precisely
so a pool problem degrades rather than fails, and it has never been observed
firing in production traffic.

## D4 — Evidence-binding race surfaces as 500

`store.submit_evidence` checks that the referenced encounter exists, then
inserts. Two writers racing (or an encounter deleted between check and
insert — not currently possible, the substrate being append-only) would trip
the foreign key inside the INSERT and surface as a 500 rather than the clean
`422 unknown_fossil_encounter:<id>@<run>`.

RISK: an unclear error for a client that did nothing wrong. The data stays
correct either way — the FK is doing its job.
FIX: catch `psycopg2.errors.ForeignKeyViolation` around the insert and map it
to the same 422 the pre-check produces.
STATUS: deferred. Never observed; requires concurrent writers binding to the
same encounter in the same instant.

## D5 — `PacketIn` has no `namespace` field

`ClaimIn`, `EvidenceIn` and `RelationIn` accept `namespace`; `PacketIn` and
`ExperimentIn` do not, because the production views (`ew.claims_prod`,
`evidence_prod`, `relations_prod`) filter only those three object types.
Packets and experiments have no prod view to be excluded from.

RISK: low and structural rather than behavioural — but it means a test packet
is indistinguishable from a scientific packet by namespace, and a future prod
view over packets would have nothing to filter on.
FIX: add `namespace` to `PacketIn`/`ExperimentIn` and classify them in
`ew.object_namespace` for symmetry, whether or not a view uses it yet.
STATUS: deferred. Note that this is a *sending* asymmetry a producer can trip
over: sending `namespace` to `/api/v1/packets` is an unknown field and
correctly returns 422 under the fail-closed rule.

## Standing rule for all five

None of these may be "fixed" silently during Harmonia's integration phase.
D2 in particular is a contract decision, not a bug fix, and needs an explicit
ruling before it becomes an enforced rule.
