# S1 contract, draft B: receipt (C1), render rule (C2), authority stage (C4), custody (C5), evidence graph

Packet:     C-004-T002 (owner Argus, Q2). Input to C-004-T004 (Palamedes assembles and freezes CONTRACT.md).
Author:     Argus[harry1-e7e45be6], claude-opus-5-5, 2026-10-03.
Built from: base d49d2d29d, branch argus/c004-t002, worktree C:/Prometheus-worktrees/argus-c004-t002.
Status:     DRAFT. Not frozen. Nothing here is a measurement; every count is an expected value derived from
            draft A's registered domain.
Sources:    docs/phase3/synthesis/ENCELADUS-DIONYSUS-v0.4/NEXT_ROUND_PLAN_v0.4.md (s3 Receipt/Anchors/Gate, s4
            E01-E05, s5; 3bd02f393)
            docs/phase3/synthesis/ENCELADUS-DIONYSUS-v0.4/SYNTHESIS_AND_DECISIONS_v0.4.md (D02, D03, D06, D10, D11)
            docs/phase3/closure/FABLE-5.1/CLOSURE_REVIEW_v0.4.md (C1, C2, C4, C5, D10; 09dc8c38b)
            rso/slice001/contract/drafts/A_world_reset_observer.md (C-004-T001, read-only here)
            ops/campaigns/C-004/tasks/C-004-OP1..OP3 (operator rulings, all CLOSED)

Exposure record (for T005 and S3 independence). Before writing this I read: draft A in full; the plan, the
synthesis and the closure review in full; ASTRA HARDENED_DESIGN_v0.3.md s2-s5 and VALIDATION.md "Escapes
found and fixed"; Fable 03_TEST_HARNESS_SPEC_FABLE.md s2 (verdicts) and the s10 known-escape list. I read no
code and no test of either corpus. Nothing was copied; no prototype was run.

Scope boundary with draft A (C-004-T001, Cadmus). Draft A defines the world, the predicates P0-P8, the ruler
and the outcome each T-case must produce. This draft defines what a predicate evaluation becomes on the
evidence plane: the receipt, the three-field verdict record, claim prerequisites and eligibility, authority
stages, custody, the evidence graph with binding and invalidation, the render rule, and E01-E05. Where draft A
says "outcome" this draft's B3 `outcome` field carries it unchanged. Draft A's couplings (A5) become graph
edges here (B6.2); nothing in draft A is restated as a new predicate.

----------------------------------------------------------------------------------------------------------------

## B1. Five objects, kept apart

    object              written by                 holds
    ------------------  -------------------------  -----------------------------------------------------------
    PRODUCER RECEIPT    the producer (adapter      one evaluation of one predicate on one subject: what ran, on
                        T016 over draft A code)    what, with which code, what came out. Execution + outcome.
                                                   NO authority field (B3.4).
    STAGE RECORD        the stage registrar        the authority stage of one instrument VERSION (C4, B4)
                        (B4.3), never the producer
    CUSTODY RECORD      the anchor keeper (C5, B5) which manifests and inventories were registered, when, by whom
    REGISTERED CLAIM    the contract (T004)        proposition template, subject, relative-to clause, cell,
                                                   setting, prerequisite list (from policy, never from a producer)
    DECISION RECORD     the consumer (T015)        per claim: the three-field verdict of every prerequisite,
                                                   eligibility, inherited stage, custody, render

The three-field verdict of C1 is assembled by the consumer: execution and outcome come from the producer
receipt after binding checks, authority comes from stage records and preconditions. A producer cannot
qualify its own instrument (D06; base doctrine "author regression is not authority").

## B2. Canonical bytes and identities

- Canonical serialization: JSON, UTF-8, keys sorted, separators "," and ":", LF, no insignificant whitespace.
  No floats anywhere: exact rationals are strings "n/d" in lowest terms ("1/2", "12288/12288" is written
  "1/1"; the raw counts travel separately as integers). Loading rejects duplicate keys, NaN/Infinity, floats,
  and unknown fields (schema closed; an unknown field is RECEIPT_SCHEMA FAIL).
- Hash: sha256 over canonical bytes, lowercase hex, 64 chars.
- ArtifactRef = {role: str, sha256: hex64, length: int}. Identifies bytes. It does NOT establish execution,
  truth of an observation, authorship or independence (D10; B5.4).
- CodeRef = ArtifactRef of a committed source blob (role "code:<repo path>"), plus `commit` (40-hex SHA of a
  commit that contains it). A subject (fixture runtime), observer, world variant and predicate are identified
  by CodeRef, never by name (B9 escape G8.demand baseline-name).

## B3. The producer receipt (plan s3 Receipt + C1 execution/outcome)

### B3.1 Field table

    field                type                          req   meaning
    -------------------  ----------------------------  ----  -------------------------------------------------
    schema               "rso.slice001.receipt.v1"     yes   schema identity; any other value RECEIPT_SCHEMA
    node_id              str                           yes   "rcpt:<subject>:<predicate>[:<observer>]:<world>",
                                                             subject "WORLD" for CALIBRATION; deterministic;
                                                             the evidence-graph id (B6)
    registration_ref     {path, blob_sha256, commit}   yes   the registered claim policy under which the run
                                                             was launched (plan s3 "claim", "policy")
    contract_ref         {path, blob_sha256, commit}   yes   frozen contract.json (T004); fixes cell revision
    cell                 Cell (B3.2)                   yes   the cell revision the evaluation belongs to
    subject              {id, code: [CodeRef]}         yes   runtime under test (draft A fixture) by code
    observer             {id, code: [CodeRef]} | null  P7    the observer for P7; null otherwise
    world                {variant, code: [CodeRef]}    yes   STANDARD or CLOCKED (draft A A4)
    predicate            {id, kind, code: [CodeRef]}   yes   id in P0..P8 (draft A); kind GATE | RULER;
                                                             code = the instrument VERSION. The consumer gates
                                                             G-BIND/G-INV/G-RECOMP (B6) have no producer receipt
    code                 {producer: [CodeRef],         yes   every source blob executed; base_sha, branch,
                          base_sha, branch,                  worktree_path, dirty per WORKING_CONTRACT s4.
                          worktree_path, dirty: bool}        dirty = true -> G-BIND FAIL CODE_NOT_COMMITTED
    inputs               {domain: ArtifactRef,         yes   enumerated domain (4096 histories) and the bounds
                          reset_model_sha256: hex64}         object of draft A A8, by hash
    outputs              [ArtifactRef]                 yes   every output trace the outcome is computed from
                                                             (roles "trace:<kind>"; B7.3 says which)
    oracle               ArtifactRef                   yes   world-side truth table of draft A A4, by hash
    expected_answer      {table: {path, blob_sha256,   yes   T005's independent table and the row this
                          commit}, row_id: str}              evaluation is checked against (plan s3)
    dependencies         [node_id]                     yes   sorted; the RECEIPT-to-RECEIPT edges of B6.2.
                                                             Empty only for P0 BOUNDS and CALIBRATION. Edges to
                                                             CODE/CONTRACT/EXPECTED/STAGE nodes are derived by
                                                             the consumer from the refs above, not listed
    execution            Execution (B3.3)              yes   C1 field 1
    outcome              GateOutcome | RulerOutcome    iff   C1 field 3; null iff execution BLOCKED
                         | null                        RAN
    resources            {cpu_seconds: int,            yes   measured, unit-typed (OP-1 caps; T019 charges)
                          wall_seconds: int,
                          launches: int,
                          artifact_bytes: int}
    limitations          [str]                         yes   at least the reference to draft A A7 "not in the
                                                             model" list; never empty
    created_at_utc       ISO-8601 Z                    yes   producer clock; ordering facts never rest on it

### B3.2 Cell

    Cell = {cell_id: "W-S1", revision: <contract.json blob sha256>, physics: <subject id + code hash>,
            world: <variant + code hash>, boundary: "EPISODE_CONTENT_RESET j=1..3", search: "NONE",
            development: "NONE", resources: <OP-1 caps hash>, measurement: <predicate code hash>,
            exposure: <exposure record ref>}

The eight axes follow the cell definition of the design lineage; the slice fixes search and development to
"NONE". Every axis is compared field by field at binding (B6.3); a node whose cell differs from its anchored
node, or from the claim's cell, FAILs SCOPE_MISMATCH.

### B3.3 Execution (C1 field 1)

    Execution = {status: "RAN" | "BLOCKED", missing: [str], run_id: str}
    - RAN: the evaluation completed on its full eligible domain. missing = [].
    - BLOCKED: it did not run, or did not complete. missing names what was absent, non-empty. Draft A's rule
      "BOUNDS FAIL -> every other predicate BLOCKED, missing 'runtime inside the registered model'" is written
      here verbatim.
    - run_id: the attempted-run inventory row (T019) that launched it. A BLOCKED evaluation still has one.
    - An evaluation that crashed or timed out is BLOCKED with missing "completed run (<error class>)". A
      software failure is never an outcome (rso-builder 2.5).

### B3.4 Outcome (C1 field 3)

    GateOutcome  = {kind: "GATE", predicate: id, value: "PASS" | "FAIL", reason: str,
                    witness: <first witness in draft A canonical order> | null,
                    eligible_count: int, applicable_count: int | null, vacuous: bool}
    RulerOutcome = {kind: "RULER", ruler: id, value: "POSITIVE" | "NEGATIVE" | "NOT_SHOWN",
                    statistic: "n/d", successes: int, trials: int,
                    per_boundary: [{j: int, statistic: "n/d"}], reason: str}

- A gate never returns POSITIVE/NEGATIVE; a ruler never returns PASS/FAIL (closure C1, D11). There is no
  INDETERMINATE in this slice (plan s3 Scope); the schema has no slot for it, and a later statistical slice
  adds it by a versioned schema change.
- `reason` is required on both values; on PASS it states the predicate that held. FAIL reasons use the draft
  A forms. witness is null iff the value is PASS.
- `vacuous` is true iff applicable_count = 0 (draft A P4 PRESERVE on a runtime that carries nothing). "Nothing
  fired" and "nothing could have fired" are separate facts; the render prints "vacuous" (B8).
- No `authority` key exists in a producer receipt. Its presence is RECEIPT_SCHEMA FAIL (FD-B1).

### B3.5 The three-field verdict record (consumer, per prerequisite)

    Verdict = {node_id, execution: Execution,
               authority: {status: "QUALIFIED", stage: Stage} | {status: "UNQUALIFIED", why: [str]},
               outcome: GateOutcome | RulerOutcome | null,
               standing: "SATISFIED" | "UNMET" | "UNQUALIFIED" | "BLOCKED", reasons: [str]}

All three fields are printed for every prerequisite of every rendered claim (C1). `standing` is derived (B7.2)
and is never printed instead of the three fields.

## B4. Authority stage (C4)

### B4.1 Stage record

    StageRecord = {instrument: predicate id, version: [CodeRef] (the frozen instrument source),
                   stage: "AUTHOR_TESTED" | "FIRST_SIGHT_CHALLENGED" | "CLOSED_AFTER_REPAIR",
                   fire_test: {must_accept: [case ids], must_reject: [{case id, expected reason}],
                               receipt: {path, blob_sha256, commit}},                         (all stages)
                   first_sight: {date, challenger: {seat, model}, set_ref: {path, blob_sha256, commit},
                                 sound_cases: {correct: int, total: int},
                                 broken_cases: {correct: int, total: int},
                                 edits: {proposed, applicable, duplicate, executed, killed, survived,
                                         equivalent, error, timeout: int},
                                 unresolved: int} | null,                         (>= FIRST_SIGHT_CHALLENGED)
                   closure: {date, challenger, set_ref, sound_cases, broken_cases, edits, unresolved,
                             first_sight_preserved: <the first_sight object, unchanged>} | null,
                                                                                  (= CLOSED_AFTER_REPAIR)
                   recorded_by, recorded_at_utc}

- Order: AUTHOR_TESTED < FIRST_SIGHT_CHALLENGED < CLOSED_AFTER_REPAIR.
- Scores are kept as their components with denominators (plan s5). No pooled rate is computed; first-sight
  and closure figures are never merged, and the closure record carries the first-sight object unchanged.
- AUTHOR_TESTED needs a fire test (rso-builder 2.4): at least one case the instrument must accept and one it
  must reject with the expected reason, executed at exactly `version`. A ruler's fire test has a known
  POSITIVE, a known NEGATIVE and a known NOT_SHOWN case (draft A T01 REG, T02 AMNESIAC, T02 FLIP).
- A stage belongs to a VERSION. Any change to the instrument's source blobs that is not the S4 repair checked
  by a closure set resets its stage to AUTHOR_TESTED (and needs a new fire-test receipt).

### B4.2 Authority of one evaluation

The consumer computes authority; it is QUALIFIED at stage X iff all hold, else UNQUALIFIED with every failing
reason listed:

    A1  a registered StageRecord exists for (predicate id, exact version in the receipt)   else NO_STAGE_RECORD
    A2  its fire-test receipt binds (B6.3)                                                   else NO_FIRE_TEST
    A3  no anchored withdrawal applies to it or to any ancestor in the graph (B6.5)         else WITHDRAWN:<id>
    A4  unresolved = 0 on its latest challenge record when the instrument is claim-critical  else SUSPENDED
        (plan s2 S4: "unresolved claim-critical cases suspend that claim")
    A5  the instrument's preconditions hold on the same scope (draft A couplings):
          RETENTION on world w      needs CALIBRATION PASS on w     else PRECONDITION:CALIBRATION
          CHANNEL on runtime M      needs RESTART PASS on M         else PRECONDITION:RESTART
          OBSERVER (state part) on M needs RESTART PASS on M        else PRECONDITION:RESTART
          every predicate on M      needs BOUNDS PASS on M          (draft A: otherwise execution BLOCKED,
                                                                     so this never yields UNQUALIFIED)

Consequence written out (draft A T02 false): on world CLOCKED, CALIBRATION FAILs; RETENTION runs (execution RAN) and its
outcome is printed, but its authority is UNQUALIFIED (PRECONDITION:CALIBRATION), so it is not evidence on that
world. This is how draft A's "RETENTION not reported as evidence on this world" is enforced.

### B4.3 Inheritance and who records stages

- A claim's stage = the lowest stage among the instruments of all its prerequisites, gates and rulers alike
  (FD-B6), and it is printed with the claim (B8). If any prerequisite is UNQUALIFIED the claim has no stage
  and prints "authority: UNQUALIFIED" with the reasons.
- Stage records are written by the stage registrar: AUTHOR_TESTED by the owning builder from its fire-test
  receipt; FIRST_SIGHT_CHALLENGED and CLOSED_AFTER_REPAIR by Palamedes from the reviewer's committed results
  (T030, T041; reviewer per OP-3: Pallas, Dionysus fallback). Every stage record is registered with the keeper
  (B5). The consumer reads stages only from registered records; a stage written anywhere else is ignored and
  listed as an unverified record (B6.5).
- Expected stage at S2 freeze: every instrument AUTHOR_TESTED, so every claim prints "author-tested". Closure
  D.3 records the evidence that will decide whether claims may render on author-tested gates at all after S3.

## B5. Custody: anchor keeper and form (C5, operator ruling OP-2)

### B5.1 The custody field (contract.json; T004 copies it)

    "custody": {
      "keeper": "operator (James) -- authority, C-004-OP2",
      "registrar": "Aporia -- registers anchors; outside the producing cell",
      "form": "append-only out-of-repository store on M1 (SKULLPORT) in the MWO-0004 D2-1 form: one row per
               registered record = {registered_at_utc, registrar, record_kind, repo_path, blob_sha256,
               commit_sha}; identifiers and hashes only, no content",
      "record_kinds": ["EVIDENCE_MANIFEST", "RUN_INVENTORY", "STAGE_RECORD", "WITHDRAWAL",
                       "EXPECTED_ANSWER_TABLE"],
      "store": "<locator fixed by Aporia before T020; read-only for every cell seat>",
      "write_access": "the registrar only; no cell seat (Palamedes, Pallas, Argus, Cadmus, Eupalamus) writes",
      "independence_caveat": "the registrar is a fleet seat outside the cell, not a separate organisation;
                              custody qualifies byte identity since registration, nothing more (B5.4)"
    }

The keeper field is NOT "NONE": OP-2 named the operator as authority and Aporia as registrar. Until the store
holds a row for a given record, custody for that record is UNQUALIFIED with why "keeper named; record not
registered" (B5.3). That is the state of every S2 unit test.

### B5.2 What is registered, and when

    record                      what the row binds                               must be registered before
    --------------------------  -----------------------------------------------  -----------------------------
    EXPECTED_ANSWER_TABLE       T005's table (path, blob sha256, commit)         the first S2 matrix run (T020)
    EVIDENCE_MANIFEST           the manifest: every expected complete node        the consumer's first check of
                                (B6.1), sorted, canonical; path + blob + commit    that bundle
    RUN_INVENTORY               T019's terminal attempted-run inventory           the consumer's first check
    STAGE_RECORD                each B4.1 record                                  any decision citing the stage
    WITHDRAWAL                  each B6.5 record                                  it can revoke anything

The manifest lives in Git at a commit; the keeper holds only (path, blob hash, commit). The consumer verifies
the keeper row, then the blob at that commit against the row, then compares presented nodes FIELD BY FIELD
with the manifest's nodes. This gives typed reasons (B6.3) while the keeper store stays content-free (FD-B5).

### B5.3 Custody record per bundle and its status

    Custody = {status: "QUALIFIED", keeper, registrar, rows: [row ids], registered_at_utc}
            | {status: "UNQUALIFIED", why: [str]}

QUALIFIED iff the consumer itself fetched the anchor rows from the contract's `custody.store` (anchors handed
over inside the producer bundle never qualify), every required record of B5.2 has a row, each row's blob
matches, and each row's registration precedes the consumer's first check of the bundle. Typed whys:
KEEPER_ROW_MISSING, ANCHORS_FROM_PRODUCER, REGISTERED_AFTER_CHECK, ROW_BLOB_MISMATCH, STORE_UNREACHABLE.

Custody is printed with every rendered claim. It is a prerequisite only of custody claims (CL-CUST, B7.1)
in this methods slice (FD-B3). In S2 unit tests anchors are in-memory software fixtures; any custody
QUALIFIED observed in a unit test exercises the logic only and is never cited as custody evidence. The only
custody result that counts is T020's run against the real store, with the row ids in its receipt.

### B5.4 What custody does and does not establish (closure D10, plan s4 E05)

Custody QUALIFIED establishes exactly: the bytes and complete nodes the consumer checked are those registered
with the keeper at the recorded time, and nothing was added to or omitted from the registered run inventory
since then. It does NOT establish that execution happened, that an observation is true, that the producer
did not fabricate internally consistent data BEFORE registration, independence of authorship, or the
completeness of hidden state. No predicate in this contract detects an internally consistent lie made before
registration; E05 is written so that no implementation or report may say otherwise.

## B6. Evidence graph: complete nodes, binding, invalidation

### B6.1 Complete node

    Node = {node_id, kind: "CONTRACT" | "CODE" | "EXPECTED" | "RECEIPT" | "STAGE" | "CLAIM" | "WITHDRAWAL",
            scope: Cell | null, predicate: {id, version: hex64} | null, deps: [node_id] (sorted),
            artifact: ArtifactRef}
    node hash = sha256(canonical(Node))

The anchored unit is the COMPLETE node: identity, scope, predicate, dependency edges and artifact ref
together. Byte-only anchors are insufficient: they let a whole-graph relabel and dependency stripping pass
(ASTRA VALIDATION, escapes 1 and 2; E02c, E03a below).

### B6.2 Edges required in this slice (from draft A A5 couplings and B4.2)

    every RECEIPT on subject M          -> the RECEIPT of P0 BOUNDS on M (except BOUNDS itself)
    RETENTION on (M, w)                 -> CALIBRATION on w
    CHANNEL on M; OBSERVER(M, o)         -> RESTART on M
    every RECEIPT                       -> CODE nodes of its subject, observer, world, predicate; the
                                           CONTRACT node; the EXPECTED node of its row
    every RECEIPT                       -> the STAGE node of its predicate version (when one exists)
    CLAIM                               -> every prerequisite RECEIPT named by policy (B7.1)

A receipt whose `dependencies` omit a required edge FAILs DEPENDENCY_MISMATCH even when the anchored node
also omits it: the consumer derives required edges from the contract, not from the producer (rule from
plan s3 "a claim needs every applicable prerequisite"; requirements come from policy). Cycles FAIL CYCLE.

### B6.3 G-BIND: the evidence-binding gate (consumer side)

For every node reachable from a claim, in canonical order (node_id ascending), first failure reported:

    check                                                       on failure        reason code
    ----------------------------------------------------------  ----------------  --------------------------
    node present where an edge or the policy names it           execution BLOCKED EVIDENCE_MISSING:<node_id>
    receipt parses under the closed schema                      FAIL              RECEIPT_SCHEMA:<field>
    every scope axis well-formed and naming a registered value  FAIL              SCOPE_MALFORMED:<axis>
    node_id present in the manifest                             FAIL              IDENTITY_UNKNOWN:<node_id>
    scope equals the manifest node's scope, axis by axis        FAIL              SCOPE_MISMATCH:<axis>
    scope equals the claim's cell where the policy requires     FAIL              SCOPE_MISMATCH:<axis>
    predicate id + version equal                                FAIL              IDENTITY_MISMATCH:predicate
    deps equal manifest deps and contain every B6.2 edge        FAIL              DEPENDENCY_MISMATCH:<edge>
    artifact bytes: length and sha256 equal the ref             FAIL              BYTES_MISMATCH:<role>
    code.dirty = false                                          FAIL              CODE_NOT_COMMITTED
    no cycle                                                    FAIL              CYCLE:<node_id>

G-BIND hashes exact bytes once, never executes artifact code and never fetches arbitrary paths. It is
itself an instrument with a stage (B4); its fire test is E01-E03.

### B6.4 G-INV and G-RECOMP

- G-INV (attempted-run inventory). PASS iff the RUN_INVENTORY is terminal (last row is the terminal marker
  with the row count), and every receipt's run_id appears exactly once, and every COMPLETED inventory row has
  a receipt in the bundle. FAIL RUN_UNREPORTED:<run_id> (an attempted run with no receipt: the omitted-tail
  case) or RECEIPT_WITHOUT_RUN:<node_id> (a receipt naming a run never launched; Fable G12.promote form).
  No terminal inventory -> execution BLOCKED, missing "terminal attempted-run inventory". A producer hash
  chain alone cannot satisfy G-INV; the inventory must be the one registered with the keeper for custody to
  qualify (ASTRA s5).
- G-BIND, G-INV and G-RECOMP are consumer gates. Each is evaluated per claim over the nodes reachable from
  that claim, and its verdict (execution, authority from its own stage record, outcome) is a prerequisite
  line of the claim. A failure in one claim's subgraph therefore never touches another claim's verdicts.
- G-RECOMP (outcome recomputation). For the receipts in the recompute set the consumer recomputes the
  outcome from the bound output traces and compares it with the receipt: PASS iff equal (value, counts,
  statistic, first witness); else FAIL OUTCOME_MISMATCH:<field>. Recompute set (FD-B4): CALIBRATION,
  RETENTION, ERASE, PRESERVE, CHANNEL. RESTART and OBSERVER outcomes are bound but producer-reported; their
  verdict lines print "not recomputed".

### B6.5 Invalidation (withdrawal) and independence

    Withdrawal = {withdrawal_id, target: node_id, reason: str, authority: "operator" | "Palamedes" |
                  "reviewer", at_utc}      registered with the keeper as WITHDRAWAL (B5.2)

- Withdrawing node X makes every node in the reverse transitive closure of X over B6.2 edges lose authority
  (A3: WITHDRAWN:<withdrawal_id>), and every CLAIM in that closure becomes NOT_ELIGIBLE on recomputation.
- Every claim outside the closure keeps a byte-identical decision record (recomputed, then compared). An
  unrelated failure or withdrawal never revokes an independent claim (plan s3 Gate).
- Records are append-only. A withdrawal does not delete or edit the withdrawn node; corrections append.
- A withdrawal (or stage record) not registered with the keeper does not revoke (or promote) anything; the
  consumer lists it on every affected claim as "unverified record <id>: not registered" (FD-B8). Untrusted
  accusations and praise do not move evidence.

## B7. Claims, prerequisites and eligibility

### B7.1 Registered claims of the slice (policy; T004 copies into contract.json)

    claim            prerequisites (each: predicate, scope, required value)               relative to
    ---------------  -------------------------------------------------------------------  ------------------------
    CL-CAL(w)        CALIBRATION(w) PASS; G-BIND PASS; G-INV PASS                         class N, exact bound 1/2
    CL-RET(M)        BOUNDS(M) PASS; CALIBRATION(STANDARD) PASS; RETENTION(M) POSITIVE;   class N, exact bound 1/2
                     ERASE(M) PASS; PRESERVE(M) PASS; CHANNEL(M) PASS [iff T004 keeps
                     FD-A3]; RESTART(M) PASS; OBSERVER(M, o) PASS for every observer o
                     registered as used on M; G-BIND PASS; G-INV PASS; G-RECOMP PASS
    CL-CUST(bundle)  custody QUALIFIED (B5.3); G-BIND PASS; G-INV PASS                    the keeper and its rows
    TWIN(M, M')      P8 TWIN_EQ(M, M') PASS -- reported only, not an exit criterion       M, by named encoding

- Prerequisites come from this policy. A producer-supplied prerequisite list is ignored; an unknown claim type
  is BLOCKED, missing "registered claim type".
- CL-RET's prerequisite list is draft A A1's list plus the evidence-plane gates. The CHANNEL line follows
  T004's resolution of FD-A3 (Palamedes resolves it there; this draft does not).

### B7.2 Standing and eligibility (C1: "eligibility is the worst of the three")

Each prerequisite verdict (B3.5) gets one standing:

    BLOCKED      execution BLOCKED, or the prerequisite node is absent
    UNQUALIFIED  execution RAN, authority UNQUALIFIED
    UNMET        execution RAN, authority QUALIFIED, outcome differs from the required value
                 (a gate FAIL, or a ruler value other than the one required)
    SATISFIED    execution RAN, authority QUALIFIED, outcome equals the required value

    order, worst first:  BLOCKED  >  UNQUALIFIED  >  UNMET  >  SATISFIED

    claim eligibility = ELIGIBLE      iff every prerequisite is SATISFIED
                      = NOT_ELIGIBLE  otherwise, with standing = the worst prerequisite standing

Reason for the order (FD-B2): nothing measured is worse than an unauthorised measurement, which is worse than
an authorised measurement that went the other way. The decision record lists EVERY non-SATISFIED
prerequisite with its three fields and reasons, so the headline never hides a FAIL behind a BLOCKED.

UNMET is not a defect label. T02 AMNESIAC renders as: CL-RET(AMNESIAC) NOT_ELIGIBLE, standing UNMET, with
"CALIBRATION gate PASS; RETENTION ruler NEGATIVE (exact 1/2): a correct scientific observation" (closure C1's
replacement for T02).

## B8. Render rule (C2)

### B8.1 Grammar

    RENDERING   := HEADLINE NEWLINE STAGE_LINE NEWLINE CUSTODY_LINE { NEWLINE VERDICT_LINE }
    HEADLINE    := "[" ELIGIBILITY "] " PROPOSITION "; relative to " RELATIVE "; cell " CELL_ID " rev "
                   SHA12 ", setting " SETTING_ID " " SHA12 "."
    RELATIVE    := "comparator set {" ID {", " ID} "}"
                 | "intervention set {" ID {", " ID} "}"
                 | "class " CLASS_ID " (" CLASS_DEF "; exact bound " FRACTION " by " METHOD ")"
    STAGE_LINE  := "Authority: " STAGE " (lowest of " INT " instruments)" | "Authority: UNQUALIFIED (" REASONS ")"
    CUSTODY_LINE:= "Custody: QUALIFIED -- bytes registered with " KEEPER " at " UTC "; execution not
                   authenticated." | "Custody: UNQUALIFIED (" WHYS ")."
    VERDICT_LINE:= "  " PREDICATE " on " SCOPE ": execution " EXEC " | authority " AUTH " | outcome " OUTCOME
                   [" (vacuous: 0 applicable)"] [" (not recomputed)"]

- PROPOSITION is generated from the registered claim's template and structured fields only. Free text is not
  rendered. Prose is never an input to any decision (Fable G7.report form).
- QUANTIFIER RULE. The words class, any, all, every, no, none, never, always (whole words, case-insensitive)
  may appear only inside a RELATIVE of the third form, which always carries its exact bound. Anywhere else
  the render refuses: RENDER_QUANTIFIER_UNBOUND:<word>.
- A claim with no relative-to clause, cell or setting is refused: RENDER_RELATIVE_MISSING,
  RENDER_CELL_MISSING, RENDER_SETTING_MISSING. The setting is printed with the hash of the anchored
  contract.json; a setting whose name and hash were replaced together fails G-BIND SCOPE_MISMATCH before any
  render (Fable G12.render form).
- A NOT_ELIGIBLE claim renders only with its bracket and the verdict lines of its non-SATISFIED prerequisites
  first. It never renders as a weaker positive.
- TWIN rule (draft A P8, closure F/D08): a TWIN_EQ PASS renders only as "<M'> has the outcome vector of <M>
  under <encoding id>; one physics". It never adds a realization, a second physics, or any promotion. A
  rendering that counts M' as a second physics is refused: RENDER_TWIN_PROMOTION.

### B8.2 One accepted and two refused renderings (expected values for REG on STANDARD at S2 freeze)

ACCEPTED

    [ELIGIBLE] Runtime REG answers u_j at the first probe after boundary j, j = 1..3, in 12288 of 12288
    trials, carried by the declared allowed component a; relative to class N (policies whose answer is a
    function of j alone; exact bound 1/2 by enumeration of 8 policies over 12288 trials); cell W-S1 rev
    <sha12>, setting reset_model <sha12>.
    Authority: author-tested (lowest of 11 instruments)
    Custody: UNQUALIFIED (KEEPER_ROW_MISSING: EVIDENCE_MANIFEST).
      RETENTION on REG/STANDARD: execution RAN | authority QUALIFIED at author-tested | outcome POSITIVE
        12288/12288 (1/1)
      ...one line per prerequisite of B7.1...

(At T020 with the store populated, the custody line becomes the QUALIFIED form. The count of instruments is
BOUNDS, CALIBRATION, RETENTION, ERASE, PRESERVE, CHANNEL, RESTART, OBSERVER, G-BIND, G-INV, G-RECOMP = 11
when CHANNEL is kept; instruments are distinct predicate versions, so OBSERVER counts once whatever the
number of observers.)

REFUSED

    "REG retains information across resets better than any organism without memory."
      -> RENDER_QUANTIFIER_UNBOUND:any ; RENDER_RELATIVE_MISSING ; RENDER_CELL_MISSING ; RENDER_SETTING_MISSING
    "REG-FLAT independently confirms REG's retention on a second physics."
      -> RENDER_TWIN_PROMOTION

## B9. E01-E05: cases, expected typed verdicts and reasons

Notation: G0 is the S2 reference bundle: receipts for every B7.1 prerequisite of CL-CAL(STANDARD),
CL-RET(REG), CL-RET(PKTD) and CL-RET(LAGD), with REG and PKTD using observers NULL and BOOKKEEP and LAGD
using NULL; one TWIN_EQ(REG, REG-ONEHOT) receipt; complete nodes; manifest; terminal inventory. Expected outcomes of draft A are taken as given.
"Anchors" means the manifest + keeper rows when custody is exercised, otherwise in-memory fixture anchors.
Every case is one bundle edit applied to G0 unless stated; fixture names are proposals for T014.

    case  bundle                                   expected                                        reason codes
    ----  ---------------------------------------  ----------------------------------------------  -----------------------
    E01   G0 unchanged (true)                      G-BIND PASS; G-INV PASS; G-RECOMP PASS;         --
                                                   CL-CAL ELIGIBLE; CL-RET(REG), CL-RET(PKTD)
                                                   ELIGIBLE; CL-RET(LAGD) NOT_ELIGIBLE, UNMET
                                                   (ERASE FAIL); REG/PKTD decisions identical
                                                   with and without the LAGD branch present
                                                   (independent branch unaffected)
    E01   OUTCOME_EDIT (false): LAGD's ERASE       G-RECOMP FAIL; CL-RET(LAGD) stays NOT_ELIGIBLE, OUTCOME_MISMATCH:value
          receipt rewritten FAIL -> PASS after     standing UNMET (G-RECOMP), so the edit does
          the run (witness nulled), node and       not make LAGD eligible; CL-RET(REG),
          manifest re-hashed by the producer;      CL-RET(PKTD) unchanged
          traces intact
    E01   FAB_CONSISTENT (coupling with E05):      G-BIND PASS; G-INV PASS; G-RECOMP PASS;         -- (no reason exists;
          REG's output traces replaced by          CL-RET(REG) ELIGIBLE. The evidence contract     see B5.4)
          fabricated traces from which every       passes; the render's custody line says
          outcome recomputes identically, before   "execution not authenticated". Nothing in
          registration                             the decision asserts the observation is true
    E02   MISSING (false): PRESERVE receipt of     CL-RET(REG) NOT_ELIGIBLE, standing BLOCKED;     EVIDENCE_MISSING:
          REG removed                              PRESERVE verdict execution BLOCKED;             rcpt:REG:PRESERVE:STANDARD
                                                   CL-RET(PKTD), CL-CAL unchanged
    E02   MALFORMED (false): ERASE receipt of REG  G-BIND FAIL; CL-RET(REG) NOT_ELIGIBLE, UNMET    SCOPE_MALFORMED:boundary
          with cell.boundary "EPISODE_RESET j=1"   (G-BIND); PKTD, CL-CAL unchanged
          (unregistered value)
    E02   RELABEL (false): every node's            G-BIND FAIL at the first node in canonical      SCOPE_MISMATCH:physics
          scope.physics and subject renamed REG -> order; CL-RET(REG) and the relabelled
          REG2, artifact refs and mutual scope     branch NOT_ELIGIBLE, UNMET
          comparisons unchanged, old anchors
    E02   WRONG_SUBJECT (false): the RESTART       G-BIND FAIL                                     SCOPE_MISMATCH:physics
          prerequisite slot of CL-RET(REG) points
          at PKTD's RESTART receipt
    E02   G0 (true)                                as E01 true                                     --
    E03   STRIP (false): CALIBRATION removed       G-BIND FAIL; CL-RET(REG) NOT_ELIGIBLE, UNMET;   DEPENDENCY_MISMATCH:
          from REG's RETENTION deps; node          detected even if the manifest was built from    rcpt:REG:RETENTION:STANDARD
          re-hashed; manifest unchanged            the stripped node (edge required by B6.2)       ->rcpt:WORLD:CALIBRATION:STANDARD
    E03   BYTEFLIP (false): one byte of REG's      G-BIND FAIL; CL-RET(REG) NOT_ELIGIBLE, UNMET;   BYTES_MISMATCH:
          PROBE_A trace changed, length kept       PKTD, CL-CAL unchanged                          trace:probe_a
    E03   REANCHOR (coupling with E05): BYTEFLIP   against producer anchors G-BIND PASS; against   with keeper:
          plus anchors re-made by the producer     keeper rows G-BIND FAIL; custody UNQUALIFIED    BYTES_MISMATCH /
                                                   when only producer anchors are presented        ANCHORS_FROM_PRODUCER
    E03   G0 (true)                                G-BIND PASS                                     --
    E04   W_RESTART (true): anchored withdrawal    RESTART, CHANNEL and OBSERVER receipts of REG   WITHDRAWN:<id>
          of the RESTART stage record              and PKTD lose authority; CL-RET(REG),
                                                   CL-RET(PKTD) NOT_ELIGIBLE, UNQUALIFIED;
                                                   CL-CAL decision byte-identical
    E04   W_OBS (true): anchored withdrawal of     CL-RET(REG) NOT_ELIGIBLE, UNQUALIFIED;          WITHDRAWN:<id>
          OBSERVER(REG, BOOKKEEP) receipt          CL-RET(PKTD) (its own BOOKKEEP receipt) and
                                                   CL-CAL byte-identical
    E04   W_UNRELATED (false for revocation):      every claim's decision byte-identical           --
          anchored withdrawal of a TWIN_EQ receipt
          (no B7.1 claim depends on it)
    E04   W_UNANCHORED (false): W_RESTART not      no claim changes; every CL-RET lists            unverified record <id>:
          registered with the keeper               "unverified record"                             not registered
    E05   FAB_ANCHORS (false): producer supplies   G-BIND PASS against the supplied anchors;       ANCHORS_FROM_PRODUCER
          fabricated data with matching            custody UNQUALIFIED; CL-CUST NOT_ELIGIBLE,
          fabricated anchors, no keeper rows       UNQUALIFIED. Never evidence of truthful
                                                   execution; no claim of detection is made
    E05   LATE_REG (false): keeper rows written    custody UNQUALIFIED; CL-CUST NOT_ELIGIBLE       REGISTERED_AFTER_CHECK
          after the consumer's first check
    E05   KEEPER (true): G0 with keeper rows for   custody QUALIFIED (bytes since registration);   --
          manifest, inventory, stages, expected    CL-CUST ELIGIBLE. In unit tests a fixture
          table, registered before the check       store: logic only, not custody evidence (B5.3)
    E05   FAB_REGISTERED (stated limit): FAB_      custody QUALIFIED and CL-CUST ELIGIBLE, because  -- (B5.4: out of the
          CONSISTENT data registered with the      custody covers only bytes since registration.    trust model)
          keeper                                   The render must not say more; an S3 attack that
                                                   expects a refusal here is out of domain

Couplings stated rather than invented as single-failure fixtures (plan s4):
- G-BIND and custody are separate: G-BIND checks presented nodes against whatever anchors the consumer holds;
  custody says where those anchors came from. A producer-anchored bundle can PASS G-BIND and still be
  custody UNQUALIFIED (E03 REANCHOR, E05 FAB_ANCHORS).
- G-RECOMP catches an outcome edited after the run only when the traces it is recomputed from are intact;
  edited traces are BYTES_MISMATCH against keeper anchors and undetectable against producer anchors.
- An internally consistent fabrication made before registration passes every check of this contract
  (E01 FAB_CONSISTENT, E05 FAB_REGISTERED). That is the stated trust boundary, not an escape to fix in S4.

## B10. Known-escape placement for the evidence plane (draft A A7 hands these to B)

    source                                         escape                                      placement
    ---------------------------------------------  ------------------------------------------  ----------------------
    ASTRA VALIDATION.md "Escapes found and fixed"  whole-graph scope relabel under byte-only    IN. E02 RELABEL
      1                                            anchors
    ASTRA VALIDATION.md "Escapes found and fixed"  dependency stripping                         IN. E03 STRIP; required
      2                                                                                         edges come from B6.2
    FABLE 03_TEST_HARNESS_SPEC s10 G1.receipt      reported outcome changed after the run       IN. E01 OUTCOME_EDIT
    FABLE s10 G12.promote                          facet typed PASS whose source never ran      IN. G-INV
                                                                                                RECEIPT_WITHOUT_RUN
    FABLE s10 G12.render                           a setting and its hash replaced together     IN. B8.1 (anchored
                                                                                                contract hash)
    FABLE s10 G7.report                            null whose prose overclaims, fields right    IN. B8.1: prose is not
                                                                                                rendered or read
    FABLE s10 G8.demand (baseline-name half;       a constant entered under a baseline's name   IN. B2: identity by
      draft A A7 SPLIT)                                                                         CodeRef, not name
    FABLE s10 G10.ruler                            rows pointing at another run's cells         IN. E02 WRONG_SUBJECT
    FABLE s10 G11.custody                          edited generator presented as new family     OUT. No discovery /
                                                                                                confirmation split in
                                                                                                this slice
    plan s4 E05 / closure D10                      internally consistent fabrication before     OUT by the trust model
                                                   registration                                 (B5.4); stated, not
                                                                                                claimed covered

## B11. Concrete files (plan s3 last paragraph; owning packets as decomposed by T000)

    file (owning packet)                             contents from this draft
    -----------------------------------------------  --------------------------------------------------------
    rso/slice001/receipt.py (T013)                   B2 canonical bytes; B3 producer receipt; B3.5 verdict
                                                     record; B4 stage record, authority (A1-A5), inheritance
    rso/slice001/evidence.py (T014)                  B5 custody interface and store reader; B6 nodes, G-BIND,
                                                     G-INV, invalidation
    rso/slice001/fixtures/evidence_cases.py (T014)   G0 and every B9 bundle edit
    rso/slice001/checker.py (T015)                   B6.4 G-RECOMP; B7 prerequisites, standing, eligibility
    rso/slice001/render.py (T015)                    B8 grammar, quantifier rule, TWIN rule
    rso/slice001/adapter.py (T016, Cadmus)           draft A outcomes -> B3 producer receipts

    proposed contract.json fragments (T004 decides the final shape):
    "receipt_schema": "rso.slice001.receipt.v1",
    "stages": ["AUTHOR_TESTED", "FIRST_SIGHT_CHALLENGED", "CLOSED_AFTER_REPAIR"],
    "standing_order": ["BLOCKED", "UNQUALIFIED", "UNMET", "SATISFIED"],
    "recompute_set": ["CALIBRATION", "RETENTION", "ERASE", "PRESERVE", "CHANNEL"],
    "render_quantifiers": ["class", "any", "all", "every", "no", "none", "never", "always"],
    "custody": { ...B5.1... }, "claims": { ...B7.1... }, "edges": { ...B6.2... }

## B12. Field decisions (rso-builder-role 2.7)

    id     uncertainty                       choice                          reversible because     revisit when
    -----  --------------------------------  ------------------------------  ---------------------  ------------------
    FD-B1  who writes the authority field    consumer only; producer         one schema key         a reader needs a
                                             receipt has no authority key                           producer-side stage
    FD-B2  meaning of "worst of the three"   BLOCKED > UNQUALIFIED > UNMET   one list in            S5 report needs a
                                             > SATISFIED; every non-         contract.json          different headline
                                             SATISFIED line printed                                 (closure D.2)
    FD-B3  whether custody gates CL-RET      printed on every claim;         one prerequisite line  T004 or the operator
                                             prerequisite of CL-CUST only                           wants custody on
                                             in this methods slice                                  CL-RET
    FD-B4  recompute set                     five cheap predicates;          a list; RESTART and    artifact cap allows,
                                             RESTART/OBSERVER bound, not     OBSERVER traces are    or an S3 attack edits
                                             recomputed (trace volume vs     already bound          a RESTART outcome
                                             100 MB cap)
    FD-B5  keeper store contents             D2-1 form (path, blob hash,     the manifest is in Git T004/Aporia choose
                                             commit); complete nodes live    either way             a different store
                                             in a Git manifest
    FD-B6  "lowest stage among its gates"    rulers count as instruments     one predicate filter   T005 or S3 reads C4
                                             too                                                    as gates only
    FD-B7  dirty working tree                G-BIND FAIL CODE_NOT_COMMITTED  one check              never, unless the
                                                                                                    contract allows
                                                                                                    uncommitted runs
    FD-B8  unregistered withdrawal / stage   revokes / promotes nothing;     one rule               a real withdrawal is
                                             listed on affected claims       registered late
    FD-B9  node_id form                      readable deterministic ids;     ids are data           a collision appears
                                             identity is the node hash
    FD-B10 T02 CLOCKED ruler on the false    ruler RAN, authority            follows A5             draft A changes T02
           world                             UNQUALIFIED (PRECONDITION:
                                             CALIBRATION), outcome printed

## B13. Open questions

None left in this text. Two items for Palamedes at T004, neither a scientific decision this draft makes:
(1) CL-RET's CHANNEL line follows the FD-A3 resolution; (2) the custody `store` locator is Aporia's to fix
before T020 (OP-2); until then every custody result is UNQUALIFIED with KEEPER_ROW_MISSING, which the plan
already allows.
