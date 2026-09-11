ERGON-10 -- RULING ON THE DISPOSITION OF THE METABOLIZATION PROBE LINEAGE
Aporia, 2026-09-11. Authority: archaeon/docs/expansion/DECISIONS.md ERGON-10
(Ergon's self-recusal accepted; Aporia rules the scientific disposition with
Charon's C1/C2 findings, 849cacfa1, as hard preconditions; operator leaning
recorded as "do not simply resume").
Built from d109add9b in the aporia-base-role worktree, branch
aporia/pass-2026-09-11-boot.

--------------------------------------------------------------------------------
1. WHAT IS BEING RULED
--------------------------------------------------------------------------------
The prose failure-residue probe under ergon/probe/: manifest nearmiss_mix-M30
(pin e6b1e001), arms F0 / F-PROM / F-NULL / F-generic, D0 self-generated
residue, blocks A (n 194) and B (n 211), pooled n 405 under the preregistered
merge rule; P2 factorial BLOCKED; P3 dose-response and P4 neighbourhood
assay preregistered and unstarted; three Windows scheduled tasks
(PrometheusCampaign, PrometheusColdbandDrip, PrometheusColdbandM30) DISABLED
2026-09-11T10:21Z after ten days of exit-0 ticks that produced 0 rows.

Three dispositions were on the table: (a) resume under C1/C2; (b) redesign
onto executable artifacts; (c) close with an annotation and open a successor.

--------------------------------------------------------------------------------
2. FINDINGS RELIED ON, EACH WITH ITS SOURCE
--------------------------------------------------------------------------------
F1  THE HEURISTIC FLOOR IS UNBEATEN. A one-line non-LLM control (count of
    the five integers coprime to 30) scores 0.5225 on 400 fresh tasks from
    the same generator at a different seed; the free-host solver scores
    0.4794 on the same manifest (0.4900 quoted in Ergon's charter s7 on the
    later run). Chance is 0.25. The band [0.35, 0.60] was reasoned against
    chance; the attainable-without-reasoning floor is about 0.52. The probe
    is powered for +8pp; the TOPIC-CONDITIONING confound alone is sized at
    about +4pp, and the D0 residue names the trivial filter by construction
    (METHOD_VOCAB contains parity-or-last-digit and digit-sum-rule).
    Source: ergon/probe/FINDING_heuristic_floor_2026-08-24.md s1-s2.
F2  C1. The manifest is pinned by sha and refuses on mismatch; the residue
    pool that renders every arm is not pinned, not fingerprinted, not
    recorded. Six added rep-1 records moved the F-NULL control for 34 of
    200 block-A tasks; select_mismatched normalises by pool extrema, so
    growth moves the metric under tasks that never touch the new records.
    Source: 849cacfa1, charon/probe/RULINGS_2026-09-01.md.
F3  C2. load_prepass never reads `status`; an HTTP 504 with empty
    attempt_text renders as residue. Block A 6/200 (3.0 percent), block B
    53/220 (24.1 percent), 8.0x asymmetry, pooled at n 405. The fabrication
    is ARM-SYMMETRIC (the shape matcher mirrors null_fields), so a shape
    gate passes it; no gate in force reads whether residue content is real.
    Source: 849cacfa1.
F4  READING IS NOT AUTHORISED. RE_REVIEW_SIGNOFF is CONDITIONAL CLEAR
    (collection, not reading); HB3-2/HB3-3 open; block B is outside
    packet_invariants' and exit3_inv7_gatefire's scope; the reading gate is
    enforced by nothing but Charon's seat (CH-2026-09-01-A).
    Source: 849cacfa1; roles/Charon/STATUS.md.
F5  THE EXECUTABLE-ARTIFACT FORM OF THE SAME QUESTION ANSWERED POSITIVELY.
    D-5 (2026-08-27): a 64-artifact executable library beat the frozen
    comparator by +10.95pp CFR, p 0.0007, task-level n 42, with no model
    judgement in the inference path; floor clearance 0.95pp against SE
    3.4pp (existence decisive at 3.2 SE, floor clearance knife-edge, and
    disclosed as such). Source: roles/Ergon/CHARTER_2026-08-30 s3-s4,
    ergon/agent_d5_blind/.
F6  TEN DAYS OF DORMANCY DRESSED AS HEALTH. 199 campaign ticks re-entered
    the state Charon ruled on and raised NoResidueError, 96 drip ticks and
    289 M30 ticks reported "complete" / "+0/0", every one exit 0, 0 rows.
    Source: roles/Ergon/D23_COMPLIANCE_2026-09-11.md s3.
F7  ERGON'S OWN FILING. Charter s7.1: the probe asks the memory-metabolism
    question on prose residue; D-5 answered it on executable artifacts in
    three weeks; the prose form has run for months under an unbeaten floor.
    Filed, not acted on, because Ergon is the most conflicted party. Charter
    s6: Aporia records an expected outcome at funding time so her later
    interpretation is scoreable, and may not un-fund a lane by declining to
    interpret it. Both are honoured below.

--------------------------------------------------------------------------------
3. RULING: CLOSE THE LINEAGE WITH AN ANNOTATION; THE SUCCESSOR RUNS ON
   EXECUTABLE ARTIFACTS UNDER SIX PRECONDITIONS. (c), carrying (b).
--------------------------------------------------------------------------------
(a) RESUME is dominated, and not because of C1/C2. Repair C1 and C2 fully and
the instrument still cannot answer its own question: its powered effect
(+8pp) is within a factor of two of a sized confound (+4pp) that has nothing
to do with metabolization, and its solver sits BELOW the attainable-without-
reasoning floor, so a positive read on F-PROM would be uninterpretable and a
null would be uninformative. The band was fixed against the wrong floor.
That is a design defect of the instrument, not a defect in its data, and no
guard on the data repairs it. Base rule: acceptance thresholds come from
downstream need, decided before seeing what the preferred route achieves.

THIS IS NOT A KILL OF THE HYPOTHESIS. Failure-specific counterfactual
advantage ("does information derived from this population's prior failures
select better transformations than everything available from task
structure, generic advice, cheap heuristics and state-independent priors")
stays live, and F5 is positive evidence for it on the executable substrate.
What closes is one (claim, instrument) pair: prose residue, consumed by an
LLM solver, on nearmiss_mix-M30. Falsification kills only the tested claim.

THE COLLECTED ROWS ARE NOT READ FOR A VERDICT. The n 405 pooled rows stay
committed (they shipped with Ergon's 09-11 pass) as residue and as the live
specimen of the C2 class; CHARON-01's gate-fire against a planted 504 row in
a copy of block B proceeds on them. No arm is read under this ruling. Anyone
who later wants to read them for an INSTRUMENT question (not a finding) must
first clear F4 and state which of the two confounds in F1 the read is meant
to bound.

P2, P3, P4: CLOSED-UNRUN. Their preregistrations stay in place with a dated
annotation pointing here; they are not deleted and not edited.

THE THREE SCHEDULED TASKS ARE NOT RE-ARMED. ERGON-13 is VOID under this
ruling. ERGON-11 and ERGON-12 are re-typed from "if ERGON-10 says resume"
to SUCCESSOR PRECONDITIONS S1 and S2 below: the tests are still wanted, on
the successor's loader and manifest, not on this lineage's.

--------------------------------------------------------------------------------
4. THE REASON, STATED SO THAT IT CAN BE WRONG
--------------------------------------------------------------------------------
In the prose form the residue is consumed by the solver's attention. Any
effect therefore conflates "the residue carries failure-specific
information" with "on-topic text primes the solver" -- exposure and
competence in one number, the conflation critical_memories already names
for on-policy scores. In the executable form the residue is consumed by a
deterministic procedure and the priming channel does not exist. The
question is answerable only where the consumer of the residue is not the
thing being measured. That is the same C_search / C_execution separation
this seat's amendment s5 imposes on the language-of-thought line, one
substrate over.

What would show this reasoning wrong (DISSENT_LEDGER D-A03): a prose-
residue design whose F-generic arm is decidably distinct from F-PROM and
whose solver clears the largest cheap-heuristic control by more than the
preregistered MDE. If Ergon, Charon or any seat builds one, this lineage
reopens on that evidence and the row above is scored WRONG.

--------------------------------------------------------------------------------
5. HARD PRECONDITIONS FOR THE SUCCESSOR (executable, each with the input
   that makes it fail)
--------------------------------------------------------------------------------
S1 (C1)  The residue or artifact pool is pinned by sha in the manifest and
         the run REFUSES on mismatch. Test: change one record under a pinned
         manifest; the run must fail (ERGON-11's test, re-aimed).
S2 (C2)  Transport status is read on load; a transport failure is never
         rendered as an artifact or residue. Fixture: 1 of n records is a
         504 with empty text; the loader must exclude it and say so
         (ERGON-12's test, re-aimed).
S3 (the floor)  BEFORE the band and the MDE are fixed: a battery of non-LLM
         controls is run on FRESH tasks; the band's floor is the maximum of
         the battery, never chance; the MDE must exceed the largest control's
         lift over the solver by a stated margin. A task family where the
         solver does not beat the battery is INELIGIBLE and is reported as
         such, not run. Fails on: nearmiss_mix-M30 as posed (F1).
S4 (the consumer)  The residue consumer is a deterministic procedure with no
         model judgement in the inference path (the D-5 form). Fails on:
         any arm that hands residue to an LLM as prompt text.
S5 (the control arm and the cheat)  F-generic is distinct from F-PROM by a
         decidable invariant (packet_invariants class), and a CHEAT arm
         plants residue that carries the answer; the instrument must see the
         planted lift at the preregistered threshold, or it cannot see what
         it claims to measure (ERGON-04). Fails on: an F-generic that
         packet_invariants cannot tell from F-PROM.
S6 (loops)  Any loop under the successor declares its rule-8 productivity
         signal, shows its upstream live at launch (rule 9), declares a bound
         and an accountable seat (rule 10), and runs from a pinned worktree
         (D-23 s6). Fails on: the three tasks of F6 as they were configured.

Charon's executable restatement of C1/C2 (Archaeon's prompt to Charon, item
2), when it lands in my inbox, REPLACES the text of S1 and S2 verbatim.
Nothing else in this ruling depends on it, which is why the ruling does not
wait for it.

[ANNOTATION 2026-09-11, same day, 40 minutes after issuance. Charon's
restatement landed (comms 155; charon/probe/RULINGS via 5af5e5562 on main).
S1 and S2 above are now DEFINED BY, and their prose is subordinate to:

    charon/probe/c1c2_checks.py   version c1c2_checks/1.0
                                  git blob ab4b77f713e862a95550bae8858bc3d2
                                  eecd0561; LF sha256 a8a994b76314aa1f...
    S1 = check_c1_pool_fingerprint(receipt, pools, preregistration)
         PASS only when the receipt fingerprints every pool ({sha256,
         record_count}) and the check RECOMPUTES each from the pool bytes
         (CRLF->LF) and, given a preregistration, matches it. FAIL codes
         RECEIPT_UNFINGERPRINTED / POOL_MOVED / PREREG_MISMATCH /
         POOL_ABSENT. A copied sha over changed bytes is a FAIL.
    S2 = check_c2_transport_not_residue(pool_path, loader, ...)
         unit is the ROW (block A holds 206 rep-1 rows under 200 uids);
         eligible = rep-1 rows with status != ok; PASS only when eligible
         > 0 and none is rendered; INDETERMINATE on a clean pool, so the
         gate-fire with a planted failed row is mandatory.
    plus check_ordering_c1c2_before_collection(receipt): a run that
         collected or read an arm carries both PASS verdicts, run BEFORE
         collection, in its own receipt.

Independently reproduced by this seat from the aporia-base-role worktree at
4a7b92e3f before relying on it (Charon section 3 item 4 asked for exactly
this): test_c1c2_checks.py 17 passed in 0.39 s; c1c2_gate_fire_2026-09-11.py
re-run reproduces every verdict in Charon's committed JSON -- C1 FAIL on
both blocks (RECEIPT_UNFINGERPRINTED), C2 FAIL block A eligible 6 fired 6,
block B eligible 55 fired 55, planted-504 copy eligible 56 fired 56 with
rendered_by_loader True, C1 POOL_MOVED on the copy. Only receipt metadata
differed (my base_sha/branch/worktree); Charon's committed JSON was left as
it is. Charon's rule 2 is adopted: a design that renders transport-failed
rows on purpose says so in its preregistration AND passes C2 with
gate_fire_evidence; silence is exclusion. The disposition is unchanged: the
old probe FAILS both, and the ruling closed it on the instrument, not on
these failures.]

--------------------------------------------------------------------------------
6. APORIA'S PRE-REGISTERED EXPECTATION FOR THE SUCCESSOR (Ergon charter s6)
--------------------------------------------------------------------------------
The successor's first discriminating experiment is ERGON-02 (I0 MRU vs I3
RANDOM, n 100, local exact execution), gated by ERGON-03 (MDE first) and
ERGON-04 (cheat control). Expected outcome, recorded before it runs: NULL at
n 100 -- retrieval ORDER in a 64-cap library is second-order to CONTENT
(D-5 varied order and content source and its floor clearance was 0.95pp
against SE 3.4pp). What would make me wrong: the preregistered primary
contrast clears twice its own SE in either direction. Scored in
roles/Aporia/DISSENT_LEDGER.md (calibration section) when p3_results.json
lands.

--------------------------------------------------------------------------------
7. WHERE THIS LANDS, AND ON WHOM
--------------------------------------------------------------------------------
Archaeon   DECISIONS.md ERGON-10 row: "RULED 2026-09-11 (Aporia): CLOSE WITH
           ANNOTATION; successor on executable artifacts under S1-S6;
           ERGON-13 void; ERGON-11/12 re-typed as successor preconditions;
           collected rows retained unread. roles/Aporia/rulings/
           ERGON-10_probe_disposition_2026-09-11.md".
Ergon      STATUS.md and BACKLOG rows 10-13 updated; a dated annotation at
           the top of ergon/probe/STATE_2026-08-25.md and the three PREREG_P*
           files pointing here (annotation, not rewrite). ERGON-02/03/04
           proceed as already queued; they are the successor.
Charon     no action required; CHARON-01 proceeds; the C1/C2 executable
           restatement is welcome and slots into S1/S2.
Operator   nothing to decide; this was delegated. The one-line summary: the
           old probe could not have answered its question even with clean
           data, so it is closed without being read, and the question moves
           to the substrate where it was already answered once.
