# HITL Log — questions & comments for James (non-blocking; loop continues regardless)

Newest first. Answer any of these whenever; replies get folded into the next cycle.

## Cycle 001 (2026-08-21)

1. **Cadence**: you asked 90 min; the wakeup runtime caps a single delay at 60 min, so the
   loop runs ~hourly. OK, or should I alternate a no-op wake to approximate 90?
2. **R0 baseline lane**: should the R0 retrieval circuit become a permanent baseline lane in
   the grading oracle, so every reasoner's staircase reports lift-over-retrieval? My stand:
   yes (it operationalizes the counter-baseline discriminator for Band E); will wire it in a
   later cycle unless you object.
3. **KNOWN_CONSTANTS scope**: certified module ships with pi/e only (python-flint 0.9 exposes
   few arb constants directly). Catalan/Euler need arb function calls — extend on demand or
   proactively?
4. **PySR install**: Julia backend will pull ~1 GB on first run. Fine on F:? (Assuming yes;
   will use a pinned venv.)

## Cycle 002 (2026-08-21)

5. **egglog spike**: propose adding the `egglog` Python package (e-graphs / equality
   saturation) at cycle 003-004 for R2+ circuit substrates. Cheap install, real leverage on
   rule composition. Will proceed unless you object.
6. **signature_index occupancy ranks**: the loader + rank instrument now exist. The actual
   MEASUREMENT (ranks of the real 3,311-class tensor + null percentile, interpreted) is a
   half-cycle of work — want it as its own artifact next cycle, or fold into the tensor
   charter's Walk-1 doc?

## Cycle 004 (2026-08-21)

7. **ChatGPT feedback folded in** — state-topology coordinate adopted as claim v4; their
   separation family implemented and confirmed executable same-cycle. The cycle-004 ChatGPT
   block reports back and asks three next questions (scoring rule for sound-vs-liar under
   capacity pressure; the minimal R4 ingredient; the binder-probe challenge).
8. **Scheduled-wake overlap**: this cycle ran EARLY because your reply arrived; when the
   already-scheduled wake fires it will find 004 done and proceed to 005 (rung R4).

## Cycle 005 (2026-08-21)

9. **PySR is now validated on real PARI data with null adjudication** (exact recovery,
   ratio 1.7e38). Next natural target: a table where the law is NOT known — e.g. residual
   structure in EC rank vs (conductor-detrended) invariants we hold. That crosses from
   instrument validation into actual discovery attempts, so per doctrine it should run with
   full battery discipline (prime-detrend, replication, seeds). OK to attempt in a later
   cycle, or hold until you review?
10. **Trace-vector fields**: cycle-005's R4 finding implies grading batteries should record
    `work` and `verifier_calls` per attempt. Wiring that into reasoning_phase0/grading_oracle
    is a small cross-lane change (Harmonia A owns the oracle) — I'll draft it as a proposal
    file rather than editing their code, unless you say go direct.

## Cycle 006 (2026-08-21)

11. **The ChatGPT collaboration is producing real artifacts** — round 2 gave us the
    lexicographic scoring contract, the canonical R4 kill test, and the guard-vs-generate
    coordinate, all now executable with tests. Worth continuing the relay at this cadence.
12. **Twins finding has battery implications beyond the loop**: any Prometheus battery that
    forces True/False without an abstention channel is scoring honest capacity-limited
    circuits as liars. Candidate doctrine memory after another cycle of testing.

## Cycle 007 (2026-08-21)

13. **Recurring law worth a doctrine memory?** Three instances now: every rung has a cheaper
    mechanism that is exact on a restricted battery slice (retrieval/clean, prior/stable
    rates, delta/additive). Proposed phrasing: "a battery certifies a mechanism only if its
    probe distribution leaves every known cheaper mechanism's exactness slice." One more
    instance (R6?) and I'll draft the memory file.
14. **Stash hygiene**: another agent's stashes (2) sit on main; my pull briefly popped one.
    Preserved untouched, but whoever owns "WIP README before sigma_kernel pull" and "agent
    work products in flight" should land or drop them.

## Cycle 008 (2026-08-21)

15. **Operator plasticity = menu growth**: the external reviewer independently arrived at
    the gen-30-wall doctrine (menus must grow) as the ladder's missing coordinate. This is
    now the strongest bridge between the ladder study and Apollo/Hephaestus charters —
    their forge IS the plasticity axis. Recommend surfacing the crosswalk to both agents'
    next sessions (their charters, our tests).
16. **R5 in Canon**: round 3 argues Canon's R5 ("holds branches") is only a rung in its
    relational form. Canon vocabulary law says rung semantics change only by James-ratified
    amendment — flagging, not editing: proposed amendment text can be drafted on request.

## Cycle 009 (2026-08-21)

17. **Epistemic objective is the sharpest external finding so far** and it points straight
    at Prometheus: our falsification batteries score whether kills happened, never whether
    the experiments chosen were the INFORMATIVE ones. A substrate that kills efficiently but
    chooses experiments myopically looks healthy on every current metric. Recommend this as
    a candidate doctrine memory AND as a question for the metabolization probe's design
    (does the residue help choose the next experiment, or only grade the last one?).
18. **Doctrine memory draft ready on request** (HITL #13, now 4 instances): "a battery
    certifies a mechanism only if its probe distribution leaves every known cheaper
    mechanism's exactness slice — and for objective-level claims, only if it measures
    EXPECTATION over the space, since myopic strategies can win single draws."

## Cycle 010 (2026-08-21)

19. **Relay hygiene**: the last paste repeated round-3 content already folded in at 008/009.
    Three items were new (legality-gated pairs, capacity-as-property, cross-realization).
    If you are pasting from different points in the ChatGPT thread, no harm — I diff against
    what is already built and only construct the residue. If it was meant to be a NEW round,
    the round-4 questions from cycle_008.md are still outstanding on their side.

## Cycle 011 (2026-08-21)

20. **STRONG RECOMMENDATION — coordinate 8 is our own June finding generalized.** The
    external reviewer's Band-G killer (evaluator revision + RETROACTIVE revalidation) is
    exactly the formula-fossil failure I audited in June: 2,351 promotions certified under a
    superseded gate, never revalidated, max training_weight 0.33-0.52 against a 0.6 bar.
    Their construction is now an executable test suite. Two concrete asks:
    (a) should the substrate carry a `revalidate()` obligation -- i.e. every evaluator/formula
        version bump triggers a corpus re-judgement and dependency-propagated retraction?
    (b) the constitutional constraint (evaluator revisions need evaluator-INDEPENDENT
        warrant) is a doctrine-grade rule. It is the formal statement of why a failed
        experiment may not redefine failure. Candidate memory; say the word and I draft it.
21. **Doctrine memories now queued: 3** (cheaper-mechanism law at 4 instances; abstention
    channel; evaluator-revision warrant). All drafts ready on request.

## Cycle 012 (2026-08-21)

22. **THREE DOCTRINE PROPOSALS NOW DRAFTED AND WAITING** — one yes/no covers all three:
    (a) cheaper-mechanism slice (5 instances, full draft at
        techne/loop/DOCTRINE_PROPOSAL_cheaper_mechanism_slice.md),
    (b) abstention channel (cycle 006),
    (c) evaluator-revision warrant + retroactive revalidation (cycle 011, = the June
        formula-fossil incident as doctrine).
    I have offered these across four cycles; drafting rather than continuing to ask. They
    live in techne/loop/ as PROPOSALS and touch no other agent's lane until you ratify.
23. **Wake prompts are drifting stale** — the scheduler is replaying the cycle-008 prompt.
    I roll forward each time (008-012 all ran), but if you want the schedule re-based on the
    true cycle number, say so and I will reset it at the next wake.

## Cycle 013 (2026-08-21)

24. **A doctrine draft I asked you to ratify was falsified one cycle later** — v1 of the
    cheaper-mechanism law had a one-line counterexample. It is rewritten as v2
    (competitor-relative identification) and the file records the withdrawal explicitly. If
    you had ratified it on my recommendation, we would have shipped a false law; the delay
    was luck, not process. Worth considering a rule: no doctrine ratifies until it has
    survived one external adversarial pass.
25. **Two doctrine proposals now stand** (both rewritten/new this cycle):
    competitor-relative identification, and the immutable-observation bottom. The second is
    the direct fix for the 2,351-promotion class of failure and I recommend it most strongly.
26. **Prometheus-facing engineering ask** arising from 12.1: our promotion records store the
    verdict and (sometimes) the evidence, but NOT the predicates invoked, and nothing models
    negative dependencies. Both are needed before any revalidation obligation can be honoured
    incrementally at 400M-record scale. This is a schema change and therefore yours to call.

## Cycle 014 (2026-08-21)

27. **I mislabelled every rung from R2 up, for thirteen cycles.** Built against the
    superseded v0.1 table while citing Canon v2.0. Crosswalk filed; no canon edit requested;
    no files renamed (audit trail). The work stands, the labels did not. Worth noting the
    irony for the record: this is the fossil failure the loop has been writing doctrine
    about. It also argues for HITL #24's proposed rule — nothing ratifies until an external
    pass has hit it.
28. **Canon R5 (invariant detection) is still unbuilt** and canon R6 is now built. Next
    cycles should finish the canon rungs actually missing rather than continue up the
    v0.1 numbering. Proposed order: R5 invariant detection, then R9 lemma invention (needs a
    Lean oracle per canon §7 — ties to the arsenal's Lean spike, still unstarted).
29. **Substrate finding, Track 1:** zero of 56 generators ever emitted a second claim_kind
    across all insertion-order epochs. The monoculture is not drift — it is congenital. If
    generator diversity is ever tackled, this says the lever is at generator DESIGN, not at
    tuning or selection pressure over time.

## Cycle 015 (2026-08-21)

30. **Lean was already installed** (elan, Lean 4.30.0) — the arsenal scan's last open item
    cost one spike, not a procurement. `pm.lean_oracle` is live with a three-valued verdict.
    This unblocks canon R9 (lemma invention needs a proof-checker oracle per canon §7) and
    gives the metabolization probe a machine-checkable claim class, which prereg §2 excluded
    for exactly this lack of a Lean-side owner.
31. **New battery-design rule, stronger than the trap ledger's usual form:** vary the OPERATOR
    SET, not only the problem instances. Varying instances alone could not separate a
    conservation-checker from a parity shape-matcher; changing the move set did it instantly.
    Recommend folding into the competitor-relative doctrine proposal when you rule on it.
32. **Canon rung status after this cycle:** built = R0, R1, R2, R3, R4 (as loop-R8), R5, R6,
    R7 (as loop-R6), R8 (as loop-R4). Remaining: **R9 lemma invention** (now unblocked by the
    Lean oracle), R10 analogy/transfer, R11 calibrated uncertainty, R12 generative conjecture.
    R12's grader is noted in canon §7 as "built; never run" — worth a look.

## Cycle 016 (2026-08-21)

33. **Possible canon defect, needs your ruling.** Canon v2.0 §3 specifies the R9 kill test as
    proof-dependency-graph analysis (is the lemma load-bearing?) and names a circular-lemma
    trap in the same entry. Measured this cycle against Lean: deletion of a circular lemma
    breaks the proof exactly as deletion of a real one does, so the specified kill test cannot
    catch the trap the same sentence names. NOT proposing a canon amendment under §8 — flagging
    it. If you want the amendment, the minimal form is: R9 kill test = dependency analysis
    AND a bounded-budget equivalence check, artifact = lemma + load_bearing + restatement flags.
34. **The equivalence-strength dial has no principled setting yet.** Too weak and a flipped
    equation gets in; too strong (any decision procedure) and honest lemmas are rejected. Same
    shape as R6 recall/phantom and R3 lexicographic (soundness, −coverage). Three rungs now
    exhibit this; it may want a name in the doctrine rather than three separate notes.
35. **Untested gaming route, named for the record:** splitting a goal into two lemmas, neither
    individually equivalent to it, evades every check built this cycle. I did not build it
    because I could not build the defence in the same cycle, and building the attack without
    the defence would leave a false green in the suite.
36. **Still open from cycle 013:** HITL #9 (PySR against a table with no known closed form)
    remains unanswered. Not blocking; the Lean track is producing more per cycle right now.

## Cycle 017 (2026-08-21)

37. **Strength-dial pattern promoted to a claim (v11), on its fourth sighting.** "A battery
    parameter that does not read the instance cannot separate instances that differ." R10 gave
    the proof-shaped version: a feature-sensitive transfer circuit is a function of the world
    PAIR, so it is constant across techniques on that pair, while ground truth is not. No
    setting works. R6 horizon / R9 tactic budget / R3 capacity are the same defect. If you
    disagree with the promotion, it is one line to demote in LADDER_CLAIMS_LEDGER.md.
38. **Open weakness I could not close this cycle:** the R10 assumption sets are hand-authored
    per technique. A circuit that declares its own assumptions can declare exactly the ones that
    hold in the target. Mechanical extraction is plausible with the cycle-015 Lean oracle (axiom
    dependencies, or typeclass instances — Field vs CharZero vs Fintype). That would make the
    trace instrument adversarially sound rather than trusted, and it is the most valuable
    single follow-up on the board.
39. **A rung may be untestable where its conclusion is open.** R10 needs to RUN the conclusion
    in the target world to avoid phantom breaks. Where that conclusion is an open problem in the
    target, only the (unsound) trace remains. Question for you: is "candidate break, unverified"
    a legitimate third verdict, or does the rung simply not apply there? This is the abstention
    channel argument again, now at R10 — it is the third rung to want one.
40. **Still open:** HITL #9 (PySR against an unknown-law table), and the three doctrine
    proposals awaiting a single yes/no (competitor-relative identification v2, abstention
    channel, immutable-observation bottom). The abstention channel has now been independently
    demanded by R3, R6 and R10.

## Cycle 018 (2026-08-21) — external review fold-in, R11 slides to 019

41. **HITL #38 CLOSED.** Mechanical assumption extraction from Lean is built and tested:
    constant-closure traversal of the elaborated proof term, CLASS/INSTANCE/CTOR
    classification, and `check_frozen_term` for necessity without re-search. An R10 circuit's
    declared assumptions can now be audited against what its proof actually depends on.
42. **Gap found in my own checker, now under test:** `sorry` is a Lean WARNING, not an error, so
    `check_lean_source` classified a sorry-contaminated proof as PROVED. Anything that has used
    the Lean verdict lane since cycle 015 should be re-read with this in mind — in practice only
    the R9 circuits, whose proofs contain no `sorry`, but the exposure was real. The axiom lane
    (`sorryAx`) catches it and is now the mandatory companion to a PROVED verdict.
43. **Claim v11 was misnamed and is rewritten** as evaluator aliasing / observational
    non-identifiability. My "instance-blind parameter" framing pointed at dials; the R9
    deletion-only checker has no parameter at all and dies to the same argument. The reviewer's
    version is provable where mine was measured. Retrofitted to R6, R9, R10. **R3 is NOT
    retrofitted and is marked unverified in the ledger rather than counted as a fourth.**
44. **Abstention channel now demanded by a third rung.** R10's (BROKEN, UNKNOWN) state is not a
    convenience — without it the circuit manufactures a refutation of the twin-prime conjecture,
    and my cycle-017 artifact check applauded it. R3, R6 and R10 all want the same thing. This
    is the proposal I would most like a ruling on.
45. **Scheduling note:** R11 slides to cycle 019. Folding in review that corrects the rung I
    just built outranks moving to the next rung.


## Cycle 019 (2026-08-21) — external review fold-in (round 7), R11 now slides to 020

46. **I shipped a wrong repair and it lasted one cycle.** Cycle 018's "a witness must witness
    the conclusion" was too strong: assumption-side evidence is the correct artifact for an
    assumption-failure claim. Corrected to evidence TYPING. Recording it because the pattern
    matters more than the instance — the repair was built, tested green, documented, pushed, and
    wrong, and only external review caught it. My own tests could not have, because they encoded
    my own misunderstanding.
47. **New claim v12: types need a checker.** Implementing the typing over the verdict's own
    fields was defeated immediately — the collapser relabels its `conclusion_status` at the same
    moment it moves the witness. Any check that reads the circuit's self-declared fields is
    reading the attacker's testimony. `audit_verdict` re-derives every status from the world and
    is deliberately not a method on the verdict class.
48. **A limit of the audit that I could not close, and it points at your constitution
    proposal.** The audit works by querying the world. In the (BROKEN, UNKNOWN) state the world
    cannot be queried by definition, so a circuit could lie about an UNKNOWN and never be caught.
    The only check I can see is against an external immutable REGISTRY of what is known open —
    which would make the immutable-observation proposal load-bearing rather than merely
    principled. **This is now the second independent argument for that proposal.**
49. **Two of my own write-ups were loose and are corrected:** the "finest projection" argument
    needs a factorization precondition (incomparable observation sets admit no common projection
    short of the full input), and "every member errs on each witness" should be "wrong on at
    least one member of the pair". The code was correct in both cases; the prose was not.
50. **Scheduling, and a limit I am imposing on myself:** two consecutive cycles have folded in
    review rather than building a rung. That is the right call each time — a wrong repair
    outranks a new rung — but R11 goes first in cycle 020 regardless of what arrives.


## Cycle 020 (2026-08-21) — canon R11 built

51. **THIRD independent argument for the immutable-observation constitution, and it is the
    strongest.** The R11 selective reporter forecasts honestly and drops the claims it got
    wrong. Measured: Brier improves 0.125 -> 0.0375, skill 0.500 -> 0.844, and NOTHING is
    falsified. No function of a record can detect what is absent from it, so no audit of the
    evidence — however external — can catch this. Only a pre-declared claim ledger can. That is
    a mechanism the constitution proposal needs, not merely a principle. Filed as claim v13.
    The three arguments are now: circular legitimisation (cycle 013), un-auditable UNKNOWN
    (cycle 019), and un-detectable omission (this cycle).
52. **First genuine counterexample to claim v11-prime**, which I had been looking for since
    cycle 017. Empirical calibration on a fixed record cannot be aliased, because the target is
    definitionally a function of the projection. The general rule this exposes is cleaner than
    the claim itself: **aliasing is escaped exactly when the projection is sufficient for the
    target.** Predictive calibration is not, and is aliased again on the same pair.
53. **A reframing I would like ruled on.** At R11 the aliasing witness is UNBREAKABLE from
    inside the situation, and the rung is the response to it rather than a repair of it. That
    suggests rungs come in two kinds — those defined by a capability and those defined by an
    impossibility result — which is not a distinction canon v2.0 makes. NOT proposing an
    amendment under vocabulary law 8; flagging it.
54. **Same soft spot as R10, one rung up.** The reference class is hand-declared, and a
    forecaster that picks its own reference class can pick a flattering one. R10's version was
    closed by the Lean tracer; I see no equivalent here. R11 may only ever be calibrated
    RELATIVE TO a declared class, in which case the class belongs in the artifact.
55. **Canon rung status: R0-R11 all built.** Only **R12 generative conjecture** remains, and
    canon 7 records its grader as "built; never run" — so cycle 021 is R12, and the first job is
    to find that grader and run it rather than build a second one.


## Cycle 021 (2026-08-21) — canon R12 audited; FIRST PASS OF R0-R12 COMPLETE

56. **The R12 grader existed and I ran it.** harmonia/experiments/r12_grader.py, 615 lines,
    17 unit tests green, offline runner discriminates good/overfit/naive correctly. Canon 7 was
    accurate that it had never been run; running it took one command. I audited it rather than
    building a second grader.
57. **Defect found in it, and it needed the run to find:** the two scoring channels are
    asymmetrically defended. Conjecture-quality subtracts a baseline; test-quality does not. A
    FIXED probe object chosen without looking at anything averages 0.443 efficiency over five
    seeds and scores 1.000 on one of them. Not a flaw in the information theory — a missing
    baseline on one of two channels. **This is a change to harmonia's experiment, not mine, so
    I have not touched it. Your call whether Harmonia fixes it or I do.**
58. **HITL #53 ANSWERED by measurement.** Rungs do come in two kinds. R0-R10 are
    capability-defined: their aliasing witnesses are breakable by a better projection. R11 and
    R12 are impossibility-defined: the witness is unbreakable from inside, and the rung is the
    RESPONSE to it. Canon R12's own kill test ("a small closed universe") turns out to be an
    aliasing statement written in English three months before the instrument existed.
59. **FIRST PASS COMPLETE, and the honest assessment: every battery in it is synthetic.** Per
    the instrument-vs-architectural rule, the whole pass is instrument CALIBRATION, not
    architectural validation. No rung has been pointed at Theseus, the metabolization probe, or
    the signature index. Twenty-one cycles of tool-sharpening with nothing yet cut.
60. **Second-pass proposal, wants your ruling on ORDERING** (detail in cycle_021.md): (a) sweep
    all rungs with the three instruments — cheap, and every rung swept so far yielded a defect;
    (b) test COMPOSITION, since every rung was built in isolation and Prometheus's real failures
    are always at seams; (c) convert ONE rung to real substrate — R6 is the natural candidate;
    (d) force the three doctrine rulings. My worry: (a) is cheap and productive and could absorb
    the entire second pass, while (c) is the one that changes what we actually know.
61. **The constitution proposal now needs a mechanism that spans SESSIONS, not just emissions.**
    Best-of-N can be defeated by declaring N=1 having run 32 times in a previous session. I have
    been treating the immutable-observation proposal as more abstract than it is.


## Cycle 022 (2026-08-21) — second pass opens; instrument sweep

62. **Proceeded without your ruling on HITL #60** (second-pass ordering). Recorded rather than
    assumed: I took the proposed order (sweep first) and capped the sweep at two cycles, so
    cycle 024 moves to composition or real substrate whatever remains. If you want a different
    order, cycles 023-024 are the cheap place to change it.
63. **R3's outstanding ledger claim was TOO BROAD and is now narrowed, not struck.** The
    cycle-006 twins alias the FIFO pipelines and do NOT alias the LIFO ones — LIFO evicts the
    most recent arrival, so a fact declared first survives the flood. FIFO and LIFO views are
    incomparable in both directions, so incapacity holds per observation class. This is the
    first time the round-7 factorization precondition has caught something in our own existing
    work rather than in a constructed example.
64. **The aliasing instrument has a blind spot, and I would like this looked at.** It detects
    only under-discrimination (merging), which carries an impossibility. It is silent on
    over-discrimination (splitting), which carries no impossibility but a real transfer cost.
    R0's defect is the second kind, so R0 swept CLEAN under the instrument while being
    demonstrably defective. Built the dual (`find_splitting_witness`), with
    `proves_impossibility=False` as a FIELD so the distinction cannot be lost in reporting.
    **Implication for the first pass: every "no witness found" result from cycles 018-021 was
    half a sweep.** None of them were reported as clean bills of health, but none of them ran
    the other direction either.
65. **R0 second finding, cycle-013 family:** srepr(x+y) == srepr(y+x), because sympy normalises
    commutative arguments at construction. The exact-AST circuit retrieves y+x from a store
    trained on x+y without earning it — the congruence is partly the CAS's, not the circuit's.
    Not fatal; the R0 claim should not rest on it.
66. **Sweep status: R0 and R3 done this cycle; R1, R2, R4, R5, R7, R8 remain**, with one cycle
    left in the cap. If the R0 result generalises, expect the remaining sweeps to want BOTH
    directions run, which roughly doubles the per-rung cost.
