# GEN2_QUALIFICATION_PACKET

Harmonia A (M2) - SFE gen-2 qualification campaign - 2026-09-01

## 1. Executive verdict

**NOT_QUALIFIED** (unsoftened, per contract sXII). Four gates fail - two on
P1 defects (G1 prediction ordering, G2 authoritative budgets), two on P2
(G3 nested fail-closed, G8 release identity). The instrument's bones are
genuinely good: append-only per-world hash chains with locked appends,
create-only object surfaces, atomic work claims with exactly-once completion,
commit-then-raise exhaustion transitions, honest declared gaps. The failures
are specific, reproducible, and each has a crisp requalification path.
Nothing here suggests bad intent - the invariants doc even declares one of
the failing gaps itself (I8 PARTIAL). The gap between advertised and enforced
prediction-ordering is the one that must not survive to first science.

## 2. Identities

- Engine: serendipity-foundry-sfe, api v2, schema_version 1, at
  https://192.168.1.202:8811 (M1/SKULLPORT)
- Source: SerendipityFoundry/SerendipityFoundryEngine @ repo commit 15f9d02a2
  ("Daedalus: Serendipity Foundry Engine + Client, role, and
  multi-experimenter isolation") - NOTE: the RUNNING build cannot be bound to
  this commit from the wire (DFX-3); binding is by operator attestation only.
- Client: SerendipityFoundry/SerendipityFoundryClient @ same commit,
  sfclient stdlib-only.
- Qualification: plan frozen at commit 5a82d3c2d before execution; raw
  results in results/qual_battery_results.json; identities harmonia-m2 +
  throwaway probes; tokens in operator kit, never recorded.

## 3. Architectural cross-walk

Gen-2 = epistemic control plane (hypotheses/predictions/experiments/
observations/failures/budgets/ledgers/isolation). It does NOT provide
substrate capabilities: D-14D remains blocked on the gen-1 executor's S3
(site-addressed intervention); trajectory work on S4. Gen-2 can GOVERN those
experiments once backends emit bindable evidence (sXI contract noted as an
architectural gap: no backend-identity/config-hash binding fields exist yet
in experiment/observation records beyond the opaque spec).

## 4. Code/commit review findings (paths per sIV)

| path | contract | code | coverage | mismatch |
|---|---|---|---|---|
| prediction ordering | API.md: 409 on back-dating | runtime.record_observation: pred.created_seq < obs event seq | engine T11 | **guard UNREACHABLE via API** (obs event allocates highest seq; any existing pred is earlier); deeper C1 boundary (first outcome evidence) absent entirely |
| observation binding | bind via pred_id | same fn; multiple obs/exp allowed | partial | duplicate pred-binding accepted; claim counting idempotent at hyp level |
| experiment lifecycle | REGISTERED->OBSERVED | create_experiment/record_observation | smoke | no budget-consuming transition anywhere |
| budget accounting | enforceable blocks | consume_budget: commit-then-raise, durable exhausted flag | T12 | manual-only; no debit on create/claim/complete |
| unknown-field rejection | fail closed | FastAPI strict models | T15 | nested budget dict NOT strict (T16 FAIL) |
| config parsing | round-trip | budgets/spec_hash persisted | T22 | intact where typed |
| client isolation | 403 | _authorize on every op; claim scoped by client | T9/T10/T11b | none found |
| session isolation | world-scoped | exp lookup world-scoped | T11 | none found |
| update/amendment | immutable | NO mutation routes exist | T4-T8 | amendment/supersession mechanism absent (limitation, not defect) |
| ledger append/integrity | hash chain | events.append under BEGIN IMMEDIATE + UNIQUE backstop; verify() | engine T15 | none found |
| release identity | exact build | static version dict | none | DFX-3 |
| error handling | typed codes | errors.py -> handler | yes | prediction_ordering_error dead code |
| retry/idempotency | exactly-once work | complete_work idempotent per worker | engine T7 | no request-identity idempotency on epistemic POSTs |
| failure persistence | first-class | failures table + DAG + query | engine T13 / T20 | none found |
| client serialization | faithful | stdlib, no silent retry of mutating calls, no default-injection observed | harness | none found |

## 5-6. Frozen plan and full test table

Plan: FROZEN_QUAL_PLAN.md (commit 5a82d3c2d, pre-execution). Results table:
results/qual_battery_results.json. Summary: PASS 14 (T4-T12, T15, T17-T20,
T22), PASS_DECLARED 1 (T18), FAIL 4 (T1, T2, T16, T21), AMBIGUOUS 1 (T3),
FINDING 1 (T13), ABSENT 1 (T14), CONFIRMED_LIMITATION 1 (T23), BLOCKED 1
(T24). Static predictions from code review were confirmed behaviorally in
every case tested.

## 7. Q1 disposition (ruled sVI)

CONFIRMED AS IMPLEMENTATION DEFECT (DFX-1, P1). Late predictions receive
full credit (state=OBSERVED, CLAIM_SURVIVED fired) via the
exp->obs1->pred->obs2 sequence; no prospective/retrospective distinction
exists in the schema; AND the advertised 409 prediction_ordering guard is
dead code (unreachable ordering condition). Regression test required; a
documentation-only fix is ruled out by sVI.

## 8. Q2 disposition (ruled sVII)

CONFIRMED AS CONTRACT GAP (DFX-2, P1 - honestly DECLARED in the invariants
doc as I8 PARTIAL, which mitigates intent, not risk). No server-authoritative
budget-consuming transition exists: experiment registration, work claim, and
work completion none debit. A client can register/execute unbounded work on
a limit-N world by not self-metering (T13: duplicate registrations unmetered).

## 9. Defects filed to Daedalus (sVIII format)

**DFX-1 | P1 | C1/C2 prediction ordering**
REPRO: world W: POST experiment E; POST observation O1(E); POST prediction P;
POST observation O2(E, pred_id=P) -> 200, P.state=OBSERVED, CLAIM_SURVIVED.
EXPECTED: no prospective credit for P (reject the prospective binding or
record it explicitly downgraded: retrospective/post-hoc). OBSERVED: full
credit. WHY: hindsight becomes foresight - the exact dishonesty gen-2 exists
to prevent. Also: the documented 409 guard cannot fire (obs event seq always
exceeds any existing pred seq) - dead code masking the gap.
REQUIRED TEST: regression reproducing the sequence above and asserting
downgrade/rejection; plus a test that the ordering guard is reachable.
DOC: API.md's back-dating paragraph must describe the real boundary
(experiment's first outcome-bearing evidence).

**DFX-2 | P1 | C3/C4 authoritative budgets**
REPRO: limit-2 enforceable world accepts unlimited POST /experiments and
work executions; consumed stays empty absent voluntary /budget/consume.
EXPECTED: an authoritative transition (builder's choice of name) where
accepted budget-consuming action <-> atomic durable server-side debit, with
idempotency. OBSERVED: cooperative-only. WHY: free compute; the budget clause
of any preregistration is unenforceable. REQUIRED TEST: debit-on-transition +
duplicate-request no-double-debit + no free duplicate execution.

**DFX-3 | P2 | C9 release identity**
REPRO: GET /v2/version and any scientific response carry no build/commit
hash; no release header. EXPECTED: machine-readable exact release on
responses (header + version body). WHY: campaign evidence cannot be bound to
the instrument build from the wire (H-1 lesson). REQUIRED TEST: header
present on representative routes; client fails on pin mismatch.

**DFX-4 | P2 | C5 nested fail-closed**
REPRO: POST /v2/worlds with budget {"experiments": {"limit": 2,
"enforcement": "enforceable", "sneaky": 9}} -> 200. EXPECTED: 422. WHY:
nested scientific config is where estimand-relevant fields will live; the
IF-1 lesson applies at every depth. REQUIRED TEST: strict models (or
explicit whitelists) for all nested scientific config.

**DOC-1 | P3** API.md advertises unreachable enforcement (folded into DFX-1
doc change). **LIM-1..3 (declared limitations, not defects):** no
amendment/supersession records (C6/C7 met by pure immutability today); no
request-identity idempotency on epistemic POSTs; no replay engine (T24;
already declared in the honest-gaps section).

## 10-11. Daedalus fixes reviewed / regression reruns

None yet - defects filed this packet. Per sVIII, on each fix: inspect
change + regression test, rerun reproduction, attempt one nearby bypass,
record disposition here.

## 12. Remaining ambiguities

T3 duplicate pred-binding semantics (double-bind accepted; claim counting
idempotent) - needs a documented contract either way. T18's unavailable-
class over-consumption is declared behavior but worth a doc example.

## 13. Known limitations

LIM-1..3 above; sXI backend-binding fields not yet modeled; single-machine
durability (declared); trusted-LAN token model (declared).

## 14. Qualification gates

| gate | status | blocker |
|---|---|---|
| G1 prediction ordering | **FAIL** | DFX-1 |
| G2 authoritative budget transition | **FAIL** | DFX-2 |
| G3 unsupported config fails closed | **FAIL** (nested) | DFX-4 |
| G4 cross-client/session isolation | PASS | - |
| G5 mutation/amendment preserves history | PASS (immutability; LIM-1 noted) | - |
| G6 retry/idempotency | PARTIAL | work-side PASS; epistemic-side tied to DFX-2/LIM-2 |
| G7 failures attributable | PASS | - |
| G8 release identity | **FAIL** | DFX-3 |
| G9 ledger reconstruction under hostile sequences | PASS | - |
| G10 client/server agreement | PASS | - |

## 15. Final verdict

**NOT_QUALIFIED.** Requalification path: Daedalus fixes DFX-1..4 with
regression tests; Harmonia reruns T1-T3, T13, T16, T21 plus one nearby
bypass each; gates re-scored; freeze issued against a release identity that
G8 can then actually bind. No Harmonia campaign uses gen-2 as its epistemic
control plane until that freeze exists. (Sandbox use for non-evidentiary
scaffolding remains fine; nothing evidence-bearing.)

Labels: every table entry above is FACT (behavioral, or code-static where so
marked); dispositions are INFERENCE from those facts; nothing in this packet
is SPECULATION.
