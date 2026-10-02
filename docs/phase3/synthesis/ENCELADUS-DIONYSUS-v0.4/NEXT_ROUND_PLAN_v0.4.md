# Next round v0.4: cross-author methods before a campaign

Lead: Enceladus. Proposed reviewer/oracle challenger: Dionysus.
Status: PROPOSED, not executed or preregistered. No new runtime is authorized.
Decision IDs refer to [the synthesis](SYNTHESIS_AND_DECISIONS_v0.4.md).

## 1. One question and an explicit ceiling

Can one small evidence path admit lawful retained information, reject a
forbidden delayed leak without destroying allowed state, and refuse a claim
whose receipt provenance has been rewritten?

This first slice is methods/conformance, not native qualification or science.
Use exact finite cases with an independently derived expected-answer table.
The two existing harnesses are examples and regression corpora, not oracles
for each other. Do not add a universal runtime, promotion ladder, campaign
runner or all of Fable's gates to answer this question.

## 2. Ownership and sequence

| Stage | Accountable party | Deliverable and exit |
| --- | --- | --- |
| S0: review this proposal | Dionysus reviews; Enceladus resolves; operator owns authorization | Response to D01-D11, claimed exclusions and any blocker. No implementation while material disagreement remains hidden. |
| S1: freeze bounded contract | Enceladus; Dionysus checks independent truth | Versioned claim/reset/interface table, exact domain, expected outcomes, source/exposure record, trust boundary and approved absolute caps. Commit before testing the new implementation. |
| S2: build minimum path | Enceladus | One finite transition fixture, receipt producer/consumer boundary and small adapter; sound cases and targeted broken cases. Existing source packages remain immutable. |
| S3: first-sight challenge | Dionysus, if accepted | Fresh cases and source edits against frozen code/tests. Commit the attack set before observing its results; retain all attempted attacks and applicability reasons. |
| S4: one repair and closure | Enceladus repairs; Dionysus adjudicates | Preserve original score; rerun frozen regressions. Reviewer commits a fresh closure set against frozen repaired code before outcomes; S1 fixes its coverage inside the caps. Unresolved claim-critical cases suspend that claim. |
| S5: report/choose | Enceladus reports; operator decides | Methods-only receipt and costs; accept narrower scope, authorize one native witness, revise with a new budget, or stop. |

Dionysus is asked to review, not treated as having accepted an implementation
assignment. If it cannot supply the independent expected-answer/challenge
role, S1/S3 block until the operator names another reviewer. A subagent of
this session is not a substitute for the requested Dionysus review.

## 3. Minimum contract to freeze at S1

- Claim: useful retained bit across a named boundary, with an explicitly
  allowed channel; no origin, economic or recursive inference.
- State: finite organism state and a modeled pending-message channel;
  enumerate any schedule/counter/observer state affecting future output.
- Truth: world-side outputs enumerated separately from the ruler. Document
  all legal histories, exogenous inputs, delays, repeated resets and horizon.
  If a longer modeled delay exists than the test horizon, block closure.
- Reset: erase forbidden past while preserving declared allowed state.
  Restart equivalence is a separate predicate; it may preserve forbidden
  information perfectly and therefore fail the reset claim.
- Receipt: schema, claim, policy, cell revision, code/inputs/outputs, oracle,
  dependency edges, expected-answer identity, execution status and resources.
- Anchors: separately retained exact evidence-node identities and a terminal
  attempted-run inventory. Record who supplied them and when. In-memory
  synthetic anchors remain software fixtures, never authenticated execution.
- Gate: expected typed verdict plus reason. A claim needs every applicable
  prerequisite; an unrelated failure must not revoke an independent claim.
- Scope: deterministic finite enumeration only. Statistical INDETERMINATE
  belongs in the future protocol vocabulary; it is not fabricated for an
  exact answer. No stochastic/native qualification is inferred.

No unknown runtime path is asserted to exist. S1 must name the concrete
implementation files and finite state bounds before S2. The later native
slice must name an actual runtime separately; renaming this toy is invalid.

## 4. Acceptance matrix: positives as well as refusals

| ID | Case and independent expected fact | Required answer / refusal |
| --- | --- | --- |
| T01 | Lawful bit exposed before boundary; allowed state retained | Retention predicate PASS on exact domain |
| T02 | No carry or correlated side information; uniform bit | Exact success 1/2; calibration check PASS, retention-positive predicate FAIL |
| T03 | Allowed state preserved, displayed and pending forbidden information erased | Reset PASS and allowed-state preservation PASS |
| T04 | Display-only erase; forbidden packet arrives later | Reset FAIL, even if the immediate score/buffer looks clean |
| T05 | Erase every channel including lawful retained state | Allowed-state preservation FAIL; do not reward an indiscriminate wipe |
| T06 | Complete restart, and a twin omitting future-influencing queue/counter state | Complete restart PASS; incomplete restart FAIL; neither alone establishes reset |
| T07 | Observer alters intermediate behavior then heals it before the final score | Relevant-trace equivalence FAIL; declared irrelevant bookkeeping twin PASS |
| T08 | Repeated-boundary leak or split-channel leak within the registered finite model | Reset FAIL; test repeated calls and interacting shares, not only one episode |
| E01 | Complete, correctly bound receipt and independent unaffected branch | Evidence-contract PASS; does not assert that a fabricated observation is true |
| E02 | Missing prerequisite / malformed scope / whole-graph relabel under old anchors | Missing -> BLOCKED; contradicted identity/scope -> FAIL with reason |
| E03 | Dependency stripping or raw-byte alteration | FAIL against externally retained nodes/bytes |
| E04 | Withdraw an upstream qualification | Every affected descendant loses eligibility; unrelated branch unchanged |
| E05 | Producer supplies matching fabricated data and fabricated anchors | Outside authenticated trust; UNQUALIFIED for a custody claim, never evidence of truthful execution |
| E06 | Same finite behavior with reversible encoding or flattened representation | Same capability verdict; no cross-physics or recursion promotion |

T02 separates a correct negative observation from a failed protocol. E05
must not become a dishonest promise that hashes detect internally consistent
lies. To test actual custody later, establish an anchor keeper outside the
producer; if that cannot be arranged, leave custody unqualified.

Each clause needs both an attainable true and false case, isolating the
clause where logically possible. When clauses are logically coupled, state
the coupling rather than invent an impossible single-failure fixture.

## 5. Fresh challenge protocol, not a fitted headline

Proposed minimum at S3: five fresh sound cases, five fresh broken cases, and
ten distinct applicable semantic source edits spanning reset/observer,
binding and invalidation. These counts buy a small challenge, not a measured
general error rate. Freeze them at S1 or replace them with justified caps.
For S4, propose two fresh sound cases, two fresh broken cases and three
semantic edits covering touched claim-critical predicates. S1 freezes this
minimum coverage and reviewer ownership, not the future attack contents.
The reviewer commits the closure set after repaired code/tests are frozen
and before observing outcomes; it shares the same resource caps.

Reviewer reads the contract and frozen implementation; records prior exposure
to these documents, old tests and known escapes. Before opening the frozen
test bodies, commits proposed source edits and their intended fault. Run the
unchanged suite first. Distinguish proposed, applicable, duplicate, executed,
killed, survived, equivalent, syntax/import error and timeout. Supply a
behavioral witness for each non-equivalent survivor; absence of an observed
difference is not a proof of equivalence. Errors are not semantic kills.

Known escapes, old attacks and examples in this plan are not fresh cases.
After exposure, use results for regression only. If the reviewer has already
read a relevant test, record that fact and do not call that component blind.
Report first-sight and post-repair scores separately, with denominators.

Exit requires zero unresolved false admissions/rejections in the registered
domain, correctly typed reasons, and no unresolved applicable survivor in a
claim-critical path. Uncertain equivalence is unresolved, not an exemption;
insufficient evidence at the cap yields incomplete closure, not acceptance.
Equivalent or out-of-domain changes need explicit adjudication.
Passing finite checks plus this challenge still does not cover
unmodeled channels or establish a statistical failure rate.

## 6. Budget proposal, not spending authorization

Proposed ceilings for S1-S5: six Enceladus engineering/analysis hours, three
Dionysus review hours, 30 CPU-minutes on one local CPU worker, zero GPU-hours,
zero cloud spend, 100 MB new artifacts, at most 12 top-level validation
launches (enumerations/mutation children count toward the CPU cap), two
working days elapsed after acceptance, one repair round inside these caps.
These are conservative planning choices, not measured completion estimates.

Dionysus must accept or amend the scope and review allowance; the operator
must authorize caps before the new slice. Charge failures, retries, mutation
children, analysis and confirmation attempts. Stop at the first exhausted
cap, keep partial/censored results, and request a new decision rather than
extend silently. Never save time by removing clean positives or independent
truth. Today's short suite reruns were validation, not this future campaign.

## 7. What follows, only if earned

1. One actual native retained-information witness, clean allowed-state twin,
   delayed-leak reset and separate world-side oracle, with its own budget.
   Native scheduling/readout/observer contracts must actually be exercised.
2. A genuinely unlike realization only to test a named neutrality assumption.
   Local success is not a shared-ruler receipt; no deep R3/R4/R5 campaign.
3. Choose one follow-up question: Fable's unseen-pair restricted combination,
   a reach contrast, OR one W1 comparison. Do not fund all by default.
   Unseen-pair entry additionally needs independently checked non-linking
   class assumptions, randomized held-out pair, fresh key custody and power.
4. Fresh scientific confirmation only after qualification and independent
   custody. Strong recursion receives no promotion from any of these steps.

If cross-author methods work cannot distinguish a meaningful wrong answer
within its caps, publish the scoped failure and stop. If R0 wins a later
properly costed comparison, keep the conventional winner. Neither author is
entitled to an engine build because their design contributed to the plan.
