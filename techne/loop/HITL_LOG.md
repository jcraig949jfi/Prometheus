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


## Cycle 023 (2026-08-21) — sweep closes on the cap

67. **I corrected my own cycle-020 claim.** I reported empirical calibration as a genuine
    counterexample to aliasing and guessed it was EXACTLY sufficient. Measured: deficit 0.000
    (the counterexample stands) but excess 1.200 bits — four forecasters with different records
    all score ECE 0.0000. Sufficient but excessive. The surplus is what predictive calibration
    needs, so it is the good news rather than a defect.
68. **I also corrected my cycle-022 framing.** I called over-discrimination a cost. R9 carries
    0.689 excess bits because it separates decorative from circular lemmas — a distinction the
    boolean verdict does not need and a human fixing the circuit does. Excess measures
    finer-than-the-truth-function-requires, so a COARSE truth function makes deliberate
    diagnostic detail look like waste. Property of the measurement, not the circuit.
69. **A worry about the aliasing instrument's SCOPE, and I would like this attacked.** Exact-
    syntax circuits (R0, R1) are never aliased and always excessive — they cannot merge distinct
    inputs, so no impossibility is available against them. Which means the instrument used alone
    would have pronounced the two LOWEST rungs defect-free, and its apparent success at
    R3/R6/R9/R10/R11/R12 may be an artefact of those rungs having lossy projections BY
    CONSTRUCTION. If so its scope is narrower than I have been claiming since cycle 018.
70. **The one perfect reading in the ladder is at the one place canon says not to trust it.**
    R12 in-universe is the only projection measuring EXACTLY SUFFICIENT (VI = 0), and it is
    exactly the closed-universe situation canon R12 warns against. Recorded as a trap: a perfect
    sufficiency reading is a prompt to ask whether the target was the one you wanted.
71. **CAP HONOURED, and five rungs are a known gap.** Swept: R0, R1, R3, R6, R9, R10, R11, R12.
    **Unswept: R2, R4, R5, R7, R8.** I took depth over coverage as instructed and would make the
    same call again — the two corrections above came from running things properly rather than
    quickly. Cycle 024 goes to COMPOSITION regardless, first target being a two-rung chain where
    the upstream rung's measured excess bits are what the downstream rung needs (R1 -> R2).
72. **Still open and now stale enough to mention again:** the three doctrine proposals
    (competitor-relative identification v2, abstention channel, immutable-observation
    constitution) have been awaiting a single yes/no since cycle 013. The constitution now has
    three independent arguments and a concrete mechanism requirement that spans sessions.


## Cycle 024 (2026-08-21) — composition, the first seam probe

73. **THREE INDEPENDENT ARRIVALS at "you need a contract, not a metric", and I think that is now
    a finding rather than a coincidence.** (a) Completeness — no function of a record detects
    what is absent (claim v13, cycle 021). (b) Reference-class choice — a forecaster picking its
    own class can pick a flattering one (R11, cycle 020). (c) Interface entitlement — laundering
    is indistinguishable from a lossless transform to any information measure (this cycle).
    **If these are one phenomenon it should have one mechanism, and the immutable-observation
    constitution is the obvious candidate.** That would turn the proposal from a principle into
    the answer to a recurring engineering problem. This is the strongest argument I have for it
    yet and it is the fourth independent one.
74. **A detector I built this cycle and withdrew within the hour.** I reasoned a stage that
    claims to reduce while discarding nothing must be smuggling. Measured: the SOUND chain's
    `together` reports identically, because it is injective on the battery. Kept the function,
    renamed `is_injective_on`, failure recorded in its docstring rather than deleted. Recording
    it here because the pattern (build detector, measure it against the honest circuit, discover
    it fires on both) has now caught me three times and is cheap insurance every time.
75. **The composition instrument is blind to two of its own three traps** — shortcut and
    laundering chains produce profiles byte-identical to the sound chain. Aliasing, against a
    tool built four hours earlier. Three independent detectors are needed and none is redundant:
    profile / ablation / intervention, each catching exactly one trap and fooled by the others.
76. **Seam location is now a measurement.** Deficit's first rise along a chain names the stage
    where it broke (1.918 bits at `degree_only` in the locally-sound chain). This is the first
    composition result that is directly reusable on real Prometheus pipelines — the probe
    assembler, the discovery pipeline, the metabolization chain all have the shape it needs.
77. **Standing gap unchanged:** R2, R4, R5, R7, R8 unswept; sweep stays closed. And the three
    doctrine proposals have now been awaiting a yes/no since cycle 013 — item 73 above is the
    fourth independent argument for one of them.


## Cycle 025 (2026-08-21) — real substrate; FOR ERGON'S ATTENTION

78. **LIVE DEFECT IN ergon/probe, needs Ergon's ruling and possibly urgent.** `campaign.py`
    writes `p1_prepass.jsonl` with `key: [rep, uid]` and reads it back through `load_prepass()`,
    which filters on a TOP-LEVEL `rep` field the writer never emits. **333 rows on disk, 0
    accepted, 100% drop, on a campaign that is executing right now.** The F-prom-retrieved arm
    then ships a 58-token packet reading "(no residue recorded at this distance)" and the
    sparsity report declares the stratum UNSUPPLIED — so the experiment reads "the substrate
    recorded nothing" when the truth is "the loader could not read the ledger". I did NOT patch
    it: `load_prepass` has five other call sites (pilot_d0, r3_live, r3_supplement, run_r7_d0d1,
    static_leakage_d0) and the fix could go in either component with different consequences for
    each. **If a campaign has been scored against empty D0 packets, those results are void.**
79. **Third arrival at "absence is indistinguishable from unreadability", now in production.**
    Claim v13 was derived from a toy at cycle 021; this is the same shape in live code four
    cycles later. Proposed defence, for your ruling: a loader that RAISES on a zero-row parse of
    a non-empty file. That converts silent absence into a loud error but forces every
    legitimately empty stratum to be declared somewhere — the pre-declared ledger again, now as
    a concrete engineering requirement rather than a principle.
80. **The composition instruments do not transfer to this pipeline, and I am recording that as a
    negative result rather than finding a use for them.** Partition measures see INTER-record
    distinguishability; every stage in the probe assembler is an INTRA-record content transform;
    the axes are orthogonal. Demonstrated by replacing redaction with the identity function —
    every number the profile produced was unchanged. An instrument that cannot distinguish a
    working firewall from no firewall has nothing to say about firewalls.
81. **The redaction firewall IS sound on real data:** 120/120 rendered records carry a verdict
    token, 0/120 after redaction, measured with Ergon's own `leaks_verdict` post-condition. That
    one-line check is the correct instrument for a content transform and mine is not.
82. **Operational, offered not acted on:** redaction inflates token count ~23% (202,863 ->
    249,409 over 120 records), because the placeholder is longer than what it replaces. The
    8,000-token ceiling therefore admits roughly 6,500 tokens of pre-redaction residue. The
    assembler's redact-then-count ordering is correct; this is about what the ceiling buys.
83. **The lesson I drew, and it wants a second opinion:** I chose the instrument before I chose
    the target. The inter-record seam the instruments were built for is real — it lives in
    SELECTION and RANKING stages — but this pipeline REWRITES rather than selects. Cycle 026
    should pick a pipeline whose stages select. The harsher reading, which I do not think is
    right but will not dismiss myself, is that twenty-four cycles of synthetic work produced
    instruments fitted to synthetic shapes.


## Cycle 026 (2026-08-21) — scope statement vindicated

84. **HITL #78 STILL UNRULED AND STILL LIVE.** The 100% loader drop in ergon/probe persists:
    campaign.py writes `key: [rep, uid]`, `load_prepass` filters on a top-level `rep`, and the
    ledger has grown from 333 to 369 rows while the defect stands. Every one is dropped. The
    F-prom-retrieved arm ships an empty packet declaring the stratum UNSUPPLIED. **If any
    campaign has been scored against empty D0 packets those results are void.** Restating until
    ruled on, per instruction.
85. **Claim v14's scope statement is vindicated.** The instruments that were blind to
    render/redact (cycle 025) separate plain ordering from BC-2 stratified ordering decisively:
    deficit 4.5850 bits (= H(task) exactly, total loss) versus 0.0000, on the live pool. Same
    module, same day, same instruments. The split is now measured rather than asserted:
    partition measures read SELECT/REORDER stages and are blind to REWRITE stages.
86. **Charon's constant-packet finding reproduced on live data**, from a different direction and
    as a number rather than a narrative: 1 distinct packet head across 24 tasks, 5 records of
    369 (1.4%) covered, against 95 under BC-2. Charon measured ~0.5% of 4,581; same phenomenon.
87. **Limitation I could not remove:** BC-2 does round-robin ACROSS sources and bucket-interleave
    WITHIN each. The campaign pool is single-source, so only the shuffle half was exercised and
    my numbers are a LOWER bound on what BC-2 delivers. The Theseus and forge corpora are not on
    this machine — if you want the source-mixing half validated I need a path to them.
88. **The arsenal needs a second instrument family, and I would like a ruling before building
    one.** Selection stages: partition measures. Rewrite stages: the pipeline's own predicate,
    re-run on the output (which is what ergon already does, correctly). I do not think content
    transforms can be brought inside partition methods — you would have to partition a record's
    internal token space, which has no ground truth — but building a second family is a real
    investment and I would rather you rule than have me assume.


## Cycle 027 (2026-08-21) — third real-substrate audit

89. **HITL #78 IS GETTING WORSE, NOT STALE. 400 rows on disk, 0 accepted, 100% drop.** It was
    330 when I found it (cycle 025), 369 last cycle, 400 now. The campaign keeps writing and
    `load_prepass` keeps discarding everything. Still unruled, still unpatched by me. **Anything
    scored against D0 packets during this window is scored against empty packets.**
90. **A THIRD stage-type category, and this one is dangerous.** Cycle 025: instruments BLIND on
    rewrite stages. Cycle 026: instruments WORK on select/reorder. Cycle 027: instruments
    **INVERTED** on filter/accumulate. A falsification battery adds a verdict bit per check and
    discards nothing, so it REFINES forward while cycle 024's profile assumes coarsening.
    Measured: deficit DECREASES 1.8295 -> 0.8698 -> 0.0000, and `is_refinement_chain` returns
    False on a perfectly healthy battery. Blind is safe; inverted is not.
91. **FOR WHOEVER OWNS THE DISCOVERY PIPELINE: two of the four kill-path checks carry zero bits
    on the candidates I measured.** F1 = 0.9597 bits, F6 = 0.9082, **F9 = 0.0000, F11 = 0.0000**.
    F9 and F11 returned the same verdict for all 34 real candidates, and the terminal verdict is
    fully determined after F6. This is canon R11's hedging forecaster inside a real battery — a
    member that never fires is observationally identical to an absent one. **Caveat stated
    plainly: 34 candidates in a narrow band is a small sample and a non-firing check may be
    guarding a rare failure mode.** But if it holds on a larger candidate set, every claim that
    "survived the four-member battery" survived a two-member battery.
92. **Question I could not answer and would like ruled on:** how should battery strength be
    reported when members do not fire? Advertised strength 4, measured strength 2. R11's
    resolution/reliability pair is the closest instrument I have and it does not obviously
    transfer, because a rare-failure-mode guard legitimately has zero resolution until it fires.
93. **Three stage types found in three cycles, one per cycle, each by accident.** That rate
    suggests the taxonomy is incomplete rather than converging. I do not have a principled
    enumeration of how a stage can relate its input information to its output — "loses",
    "reorders", "adds" is a list, not a derivation.


## Cycle 028 (2026-08-21) — HITL #91 resolved, and it was structural

94. **HITL #78: 446 rows, 0 accepted, 100% drop.** 330 -> 369 -> 400 -> 446 across four cycles.
    Still unruled, still unpatched by me. Anything scored against D0 packets in this window is
    scored against empty packets.
95. **HITL #91 RESOLVED, and the sample-size caveat I recorded was answering the wrong
    objection.** Widened the candidate set to n = 81 (degrees 2-8, coefficients to ±5, 37
    reciprocal and 44 NON-reciprocal, M from 1.0000 to 9.6071 rather than one band). F9 and F11
    stay at exactly 0.0000 bits. But READING THE SOURCE settled it harder and showed the two
    zeros have different causes:
      * **F9 cannot fire on anything.** `_f9_simpler_explanation` is `return True` with no
        computation on its input; it returns True for the empty list. Structural, not statistical.
        Its docstring is honest — it exists "for post-rejection record-keeping".
      * **F11's cross-validation is vacuous by a theorem.** It compares M(coeffs) with
        M(reversed(coeffs)), and reversal maps roots α -> 1/α while swapping leading/trailing
        coefficients, so M is invariant. Verified on 40 random non-reciprocal polynomials: zero
        disagreements. Its surviving branch (vs the caller's REPORTED M) fires correctly but
        tests bookkeeping, not candidates.
96. **FOR WHOEVER OWNS THE DISCOVERY PIPELINE — the count is wrong, not the code.** Neither check
    is fraudulent; one is a record-keeper, one a caller-consistency assertion. But the kill path
    is quoted as a four-member battery and measures as a two-member discriminating test.
    **Anything that "survived the four-member battery" survived two.** F11's docstring claim of
    "two independent paths" is also false as written, which is a documentation defect with
    epistemic consequences.
97. **A finding I did not expect and which worries me more than the zeros: F6 measured 0.9082
    bits on the narrow band and 0.2285 on the wide one.** A battery's strength is not a property
    of the battery — it is a function of the candidate distribution. Every "survived the battery"
    claim is implicitly relative to the distribution it was tested on, and I do not have a
    standard way to report that. It may collapse into R11's reference-class problem (HITL #54).
98. **General lesson, offered for ruling as a possible standing rule:** when a measurement reads
    zero, READ THE SOURCE before collecting more data. A structural zero and a sampling zero look
    identical and only one is fixable by sampling. The mechanical version would be mutation
    testing — perturb the member's input space and check whether ANY input flips it — which is
    what I did by hand for F9. This restates an existing memory (a structural zero needs its own
    pre-committed vacuous reading) as an executable check rather than a habit.


## Cycle 029 (2026-08-21) — structural-constancy probe built and swept

 99. **HITL #78: 491 rows, 0 accepted, 100% drop.** 330 -> 369 -> 400 -> 446 -> 491 across five
     cycles. Still unruled, still unpatched by me.
100. **HITL #98 DISCHARGED — the standing rule is now a tool.** `prometheus_math.battery`
     gained a two-tier structural-constancy probe: an AST check for whether a member reads its
     own arguments (proof it cannot fire) and a hostile-input mutation search (proof it can),
     with an honest UNSETTLED between them. `can_fire` returns None for UNSETTLED — unknown,
     never silently fine.
101. **GOOD NEWS, and it is a real search rather than an assumption: F9 is the only
     structurally-constant member in the repo's kill batteries.** Twelve members swept across
     `discovery_pipeline`, `lehmer_brute_force` and my own R6 circuits. The substrate does not
     have a systemic dead-check problem; it has the one instance already reported at cycle 028.
102. **F11 refines rather than contradicts cycle 028.** Under a hostile probe space it reads
     VARIES; over well-formed candidates it still measures 0.000 bits. Natural sampling measures
     REALIZED discrimination, mutation testing measures CAPABILITY, and both are true. **A
     constancy verdict must always be reported with its input space.**
103. **The probe caught its own author, and I nearly published my own bug as a finding.** The
     first sweep reported two `lehmer_brute_force` members as UNSETTLED. They are not — I passed
     full coefficient lists to functions requiring length-8 HALF coefficients, all 90 calls
     raised, and the probe mapped every exception to one sentinel, making "everything errored"
     indistinguishable from "nothing ever varied". Fixed with `n_evaluated` and an
     `INVALID_PROBE` status. Recording it because the near-miss is the argument for the fix.
104. **Third arrival of the reference-class problem, and I would like a ruling on whether to
     treat it as one thing.** It has now surfaced at R11 (a forecaster picking its own reference
     class), at battery strength (F6: 0.908 bits narrow band, 0.229 wide), and here (F11
     constant on well-formed input, varies under hostile). Each time the answer depends on a
     domain nobody declared. **The candidate fix is the same each time: declare the input space
     as part of the specification**, which is the pre-declared-ledger mechanism again in a
     third costume.
105. **Known gap, stated before the results rather than after:** parameter-independence is
     SUFFICIENT for verdict-constancy, not NECESSARY. My own EagerFalsifier and CredulousAsserter
     are constant by construction but read their argument for a non-verdict purpose, so they land
     in UNSETTLED. Closing it needs dataflow tracing from parameter to returned verdict. Worth
     building or not — your call (HITL #106).


## Cycle 030 (2026-08-21) — reference-class problem: one core, two kinds

107. **HITL #78: 530 rows, 0 accepted, 100% drop.** 330 -> 369 -> 400 -> 446 -> 491 -> 530 across
     six cycles. Still unruled, still unpatched by me.
108. **HITL #104 ANSWERED, and the answer is neither of the two options I offered you.** The
     three arrivals share a real core — each is a property of an object AND an undeclared domain
     — but they split on how they behave when the domain grows, and the split is testable:
       * EXISTENTIAL claims are MONOTONE. A witness stays a witness (F11: UNSETTLED -> VARIES ->
         VARIES on every superset). Only the negative is domain-relative.
       * AGGREGATE claims are NON-MONOTONE in BOTH directions. Measured on F6: 0.0000 bits on a
         subset excluding every firing case, 0.3651 after adding them, 0.2285 on the full set —
         up then down.
     So a witnessed existential may eventually be stated absolutely; an aggregate never may.
109. **I nearly published a weaker version of this.** My first pass exhibited only DECREASES,
     which would have left open the reading "monotone downward, therefore still well-behaved". I
     had to construct the increase deliberately. **New standing habit worth ruling on: to claim
     non-monotonicity, exhibit a move in BOTH directions** — one direction is consistent with a
     bound.
110. **Mechanism built: `prometheus_math.relative_claim`.** A claim without a domain is REFUSED
     rather than defaulted; a positive existential without a witness is refused; aggregates never
     entail on any domain including their own. Content-addressed domain digests so two parties
     quoting the same number can confirm they mean the same input set.
111. **On the constitution — I am NOT inflating the count.** The declared-domain mechanism shares
     the SHAPE the immutable-observation constitution needs (an external checkable statement fixed
     before the claim is quoted) but is not the same mechanism: the constitution's job is that the
     record of predictions and outcomes cannot be rewritten, and a domain digest constrains what a
     claim MEANS, not what the record SAYS. **Four arguments for the constitution, plus one
     adjacent requirement sharing its shape.** Still your call; still not ratified.
112. **Open, and I would rather build it than trip over it: is the existential/aggregate split
     exhaustive?** A UNIVERSAL claim ("for all x in D") is the obvious third — monotone DOWNWARD,
     breakable by widening and never establishable by it. That would make the taxonomy
     three-with-a-symmetry. I have said "that feels exhaustive" twice this month and been wrong
     once, so I am flagging rather than assuming.


## Cycle 031 (2026-08-21) — claim kinds derived, not surveyed

113. **HITL #78: 572 rows, 0 accepted, 100% drop.** 330 -> 369 -> 400 -> 446 -> 491 -> 530 -> 572
     across seven cycles. Still unruled, still unpatched by me.
114. **HITL #112 ANSWERED: three was not exhaustive either — there are exactly FOUR, and they are
     a 2x2 rather than a list.** Write a claim as an aggregation over the domain's elements; its
     behaviour under domain extension is inherited from the aggregation's monotonicity, and
     "monotone up?" / "monotone down?" are independent booleans. EXISTENTIAL (T,F), UNIVERSAL
     (F,T), INVARIANT (T,T), AGGREGATE (F,F). Exhaustive by construction — no fifth kind without
     a third monotonicity direction.
115. **The measurement I would not have believed without running it: normalisation is what
     destroys monotonicity.** The SAME statistic — F6's firings — is EXISTENTIAL as a count
     (0, 3, 3, 3 as the domain grows) and AGGREGATE as a rate (0.0000, 0.1304, 0.0566, 0.0370:
     up then down). Same predicate, same data, same firings. **So "is this rate a fact about the
     object?" always answers no**, which retires a question that has recurred since cycle 028.
116. **INVARIANT closes a loop back to cycle 029.** F9 is parameter-independent, therefore
     domain-independent, therefore INVARIANT — making "F9 cannot fire" one of the very few
     claims in this entire loop that legitimately needs no domain qualifier. Everything else I
     have measured this month is relative to something.
117. **A real soft spot in my own derivation, and I would rather you found it than me later.**
     The 2x2 assumes every domain-relative claim can be written as an aggregation over
     INDEPENDENT per-element values. Irreducibly RELATIONAL claims — "the domain contains two
     elements that disagree", "this pair is the closest in D" — may not fit that normal form. If
     they do not, I have made an exhaustiveness claim about a normal form whose generality I did
     not check. Flagged rather than buried.
118. **HITL #93 (stage-type taxonomy is a list) — candidate derivation, NOT claimed.** A stage's
     type may be determined by how it moves the PARTITION of its input set: coarsens (select),
     refines (accumulate), or fixes the partition while changing contents (transform). That would
     explain why the instruments are working / inverted / blind respectively. Worth a cycle of
     its own. Honest worry: one derivation worked, and I may now be pattern-matching derivations
     onto everything.


## Cycle 032 (2026-08-21) — external review round 8 folded in

119. **HITL #78: 632 rows, 0 accepted, 100% drop, EIGHT cycles unruled.** 330 -> 369 -> 400 ->
     446 -> 491 -> 530 -> 572 -> 632. **New: the campaign has begun writing rep-2 rows** (7 of
     632) — the contamination screen. The shipping loader accepts neither rep.
120. **My cycle-022 merge/split duality was scoped too widely and is now narrowed.** It exhausts
     classification error against a FIXED target; it says nothing about a projection that induces
     exactly the right partition and destroyed what a LATER task needs. Measured on integers
     2..41: the primality projection scores VI = 0.0000 against "is it prime" and loses 1.9567
     bits against "smallest factor". **Adequacy is quantified over future targets — a different
     quantifier — so no care about the first target detects it.**
121. **New instrument: `refinement_multiplicity`** (worst-case fragmentation) beside `H(P|T)`
     (average). A rare cell shattered into singletons costs 0.3322 bits while the same shattering
     in the common cell costs 0.7851 — averages hide concentrated waste.
122. **I nearly asserted a convergence on a test that could not have falsified it.** The two
     measures are different kinds under cycle 031's 2x2 (multiplicity EXISTENTIAL, excess bits
     AGGREGATE), but my first chain made both look EXISTENTIAL because singleton-refinement
     growth only drives excess up. Per my own HITL #109 I constructed the decrease deliberately.
     **The both-directions rule earned its keep this cycle — recommend ratifying it.**
123. **Cycle 022's "prove incapacity per observation class" is superseded.** With infinitely many
     incomparable classes, enumeration cannot finish, and the fallacy to avoid is "we could not
     enumerate, therefore the family might be sufficient". A parameterised adversary constructor
     kills the family with one schema: run against R3 across 24 parameters (widths 1-12 x both
     policies), 24 witnesses. `proves_family_incapacity` is hardcoded False — the schema's
     correctness is a UNIVERSAL claim over the parameter space, so sampling refutes and never
     establishes.
124. **FOR ATTENTION — the preprocessing finding is worse than cycle 022 reported, and it may
     reach the whole bottom of the ladder.** R0's projection is `srepr o sympy-normalisation`,
     and SEVEN OF EIGHT source-level distinctions are erased before the circuit runs. If the CAS
     delivers most low-rung invariance, **R0 and R1 may be measuring sympy's normaliser rather
     than any reasoning**, and the ladder's bottom two rungs would need rebuilding on raw syntax
     trees. Large claim, not yet made — but it is the most consequential thread open.


## Cycle 033 (2026-08-21) — the cycle-031 soft spot resolves

125. **HITL #78: 641 rows, 0 accepted, 100% drop, eight cycles unruled.**
126. **HITL #117 RESOLVED — relational claims DO fit the normal form, via arity.**
     `Phi(O,D) = A({phi(O,t) : t in D^k})` for fixed k. Monotonicity survives because
     `D subset D'` implies `D^k subset D'^k`. Measured at k = 2: aliasing (exists over D^2) reads
     EXISTENTIAL, consistency (forall over D^2) reads UNIVERSAL, min pairwise distance reads
     UNIVERSAL. **The cycle-031 exhaustiveness claim survives, over a wider normal form than it
     was stated for — and it is now tested rather than assumed.**
127. **Two preconditions I had never written down, both found by testing rather than by
     thinking.** (P1) `phi` must not read the domain, especially not |D| — a predicate that does
     is normalised and lands in AGGREGATE, which is cycle 031's rate defect at arity 2. (P2) the
     value must be MEANINGFULLY ORDERED.
128. **(P2) was found by my own instrument misbehaving, and it is the worst kind of failure.**
     Asked to classify an argmin — which pair is closest, a selection rather than a magnitude —
     `probe_monotonicity` returned UNIVERSAL, purely because Python orders tuples
     lexicographically. Meaningless and confidently delivered. It now refuses non-numeric values.
129. **A PATTERN I WOULD LIKE RULED ON, because it is now three instances.** Every instrument I
     have built this month shipped with the exact defect it was built to detect:
       * cycle 029 — the constancy probe read an all-raising probe space as constancy;
       * cycle 032 — the convergence claim rested on a chain that could not have falsified it;
       * cycle 033 — the monotonicity classifier ordered unordered values.
     **All three were found by accident, not by my standing habit of testing an instrument
     against its honest case.** Candidate discipline: before trusting an instrument, construct
     the input on which it MUST report the answer you do not want, and check that it does. That
     is cheap and would have caught all three. Recommend adopting.
130. **Also this cycle: a chain that cannot cross a threshold classifies nothing.** My first
     relational chain started where every claim already fired, so all four read INVARIANT — four
     confident wrong answers. Defence added to the traps ledger: check the value sequence varies
     before reading a classification off it.


## Cycle 034 (2026-08-21) — the preprocessing thread closes, narrowly

131. **HITL #78: 684 rows, 0 accepted, 100% drop, NINE cycles unruled.**
132. **HITL #124 RESOLVED, and more narrowly than the question assumed. R0 does measure a
     normaliser; R1 and R2 do not.** R0's keyer IS `sympy.srepr` — its projection is exactly the
     CAS's normal form and it contributes nothing of its own. R1 identifies `2*x+4` with `3*x+6`
     (different sympy keys, same answer) and R2 knows that scaling a rational fixes its root;
     both are genuine many-to-one work the CAS does not do. **No rebuild on raw syntax is called
     for — there is no raw syntax.**
133. **HITL #129 (the new discipline) EARNED ITS KEEP IMMEDIATELY, and I recommend ratifying it.**
     Applied to the raw-syntax control before using it: the control failed 6/6. `ast.parse` merges
     parentheses, whitespace, comments, numeric literal spelling, radix and string quoting.
     **There is no raw baseline**, so the assigned question ("what fraction of the invariance is
     the circuit's?") was unanswerable as posed and would have produced a confident wrong number.
     Third cycle running that an instrument shipped blind in the direction it was pointed — first
     time the habit caught it BEFORE the measurement instead of after.
134. **What I am asking for on R0, rather than doing: a docstring correction, not a rewrite.**
     R0 advertises an "identity congruence" and implements "sympy normal form". Its kill test is
     still sound — renaming is the one isomorphism sympy does not collapse and renaming is
     exactly what the fresh-seed test uses — so the rung's original result stands. But I did not
     touch R0, per the standing instruction not to make a finding go away by editing the thing
     it is about.
135. **The harsher reading of R0, which I do not endorse but will not dismiss myself.** If R0 has
     no congruence of its own at all, it is not a circuit in any meaningful sense — it is a
     dictionary keyed by sympy's normal form, and the rung would be vacuous rather than merely
     mislabelled. I think "mislabelled" is right because the retrieval/abstention behaviour is
     real and testable, but that is a judgement and it should be yours.
136. **Open, and I do not know how to do it:** the layered attribution works where preprocessing
     is a cleanly separable function. Where preprocessing is entangled with the computation, I
     have no way to attribute at all. Every rung consumes some library, so this will recur.


## Cycle 035 (2026-08-21) — round-9 fold-in

137. **HITL #78: 699 rows, 0 accepted, 100% drop, TEN cycles unruled.**
138. **Cycle 033's "repair is arity" is SUPERSEDED — I was defending a premise the result never
     needed.** The 2x2 classifies by the extension relation alone; no aggregation normal form is
     required. Demonstrated on induced-subgraph connectivity, which has no fixed-arity form and
     classifies cleanly as AGGREGATE (moves UP on one chain, DOWN on another). **The four
     monotonicity classes stand and are stronger without the premise.**
139. **My cycle-033 precondition (P1) is WRONG and is retired.** It said "phi must not read |D|".
     Counterexamples: `sum 1 / |D|` reads |D| and is INVARIANT; `|D| - count_P(D)` reads |D| and
     is EXISTENTIAL. Reading |D| is neither necessary nor sufficient for non-monotonicity. It was
     a syntactic proxy for a semantic property.
140. **The stage taxonomy has FOUR motions, not three, and needs TWO coordinates.** INCOMPARABLE
     is real on live data: R10's assumption_status and conclusion_status partitions over the
     battery are [6,8] and [5,9] with neither refining the other. Also a correction to cycle 026:
     pure reordering is bijective and PRESERVING; truncation is what coarsens.
141. **A DERIVATION rather than a list, and it explains an old puzzle.** A DETERMINISTIC stage
     that is a pure function of its predecessor's output can only COARSEN or PRESERVE —
     refinement and incomparability are impossible. So a stage measuring REFINEMENT has PROVED it
     read beyond its predecessor. That is exactly why cycle 024's transform pipeline coarsened and
     cycle 027's battery refined: the battery reads the ORIGINAL candidate at every check.
142. **The discipline caught me on my own derivation.** An `f` returning `random()` measured
     REFINEMENT, apparently violating it. It does not — `random()` is not a function of its input,
     it reads the generator state, which IS information beyond the predecessor. Instance, not
     counterexample. Missing precondition: determinism.
143. **Round-10 review arrived mid-cycle and is next**, including a much better-specified version
     of the instrument contract I was about to build: POSITIVE / NEGATIVE / INVALID fixtures plus
     a sensitivity witness, with promotion refused unless all execute.


## Cycle 036 (2026-08-21) — round-10 fold-in: the instrument contract

144. **HITL #135 ANSWERED by the reviewer, and I accept it: R0 is vacuous as a reasoning
     circuit.** Pi_R0 = Pi_sympy, zero endogenous invariance — a memo table over the substrate's
     canonical form. **Keep the rung as a calibrated floor, but rename the capability to
     "retrieval under inherited canonicalization"**, and restructure its battery into two
     explicit columns: BORROWED invariance (must survive every transformation preprocessing
     already collapses) and UNEARNED invariance (must fail every transformation preprocessing
     preserves). That makes R0 a clean zero-point. **HITL #134 is now a concrete request rather
     than a flag — and it is still yours to make, since I do not edit the thing a finding is
     about.**
145. **HITL #136 ANSWERED — I had recorded "no method" and there is one, with a limit.**
     BOUNDARY attribution works where components have explicit interfaces (cycle 034's layer
     ladder). CAUSAL contribution under entanglement is counterfactual and **often not uniquely
     defined**: synergistic components each contribute 0 alone and 1 together, with no canonical
     owner. So report **dependence, not ownership** — "this invariance disappears when C is
     removed", never a percentage, unless a convention like Shapley is explicitly chosen and
     named as a convention. **Doctrine adopted: never credit downstream machinery for invariance
     already present at its input.**
146. **The instrument contract is BUILT and all four historical failures map to a slot.**
     POSITIVE / NEGATIVE / INVALID / SENSITIVITY, submission refused without all four. 029
     all-raising space -> INVALID; 032 unfalsifiable chain -> NEGATIVE absent; 033 unordered
     values -> INVALID; 034 "raw" control -> NEGATIVE. The sensitivity witness is the measurement
     analogue of an aliasing witness.
147. **IT IS CONVENTION, NOT ENFORCEMENT, AND I WANT A RULING ON WHETHER TO BUILD THE GATE.** A
     new module can still skip registration silently. Real enforcement needs a CI gate that
     enumerates measurement modules and refuses promotion for any without an executed contract —
     repo infrastructure rather than a library, so I have not built it unasked.
148. **The contract has its own anti-case and it passes cleanly.** An instrument that memorises
     the four fixtures and is blind everywhere else certifies. Necessary, not sufficient — canon
     R0's lookup-table trap one level up. Defence built: fixtures are FACTORIES and `draws > 1`
     redraws them; a one-draw memoriser fails on redraw. **A clean report on frozen fixtures
     means only that those four inputs were handled.**


## Cycle 037 (2026-08-21) — contract retrofitted to the whole arsenal

149. **HITL #78: 717 rows, 0 accepted, 100% drop, ELEVEN cycles unruled.**
150. **THE CONTRACT CAUGHT TWO REAL DEFECTS IN MY OWN SHIPPED MODULES, and this is the
     justification for building it.** `find_aliasing_witness` and `fiber_search` both returned
     `None` for "searched and found nothing" AND for "there was nothing to search" — no-signal
     conflated with out-of-domain. **It is exactly the defect cycle 029 fixed in
     `structural_constancy`, which I fixed there and never propagated next door.** The habit
     would not have caught it because I was not looking at those functions. Both now raise
     `OutOfDomain`; a test guards that the honest no-signal path still works.
151. **A PROPAGATION FAILURE, not a design failure, and I have no mechanism for it.** Nothing
     makes "this class of bug" searchable across modules. A bug-class registry is the obvious
     answer and the obvious bureaucracy-that-decays. Would like a ruling on whether it is worth
     the weight.
152. **Third refusal was a REACH LIMIT, previously undocumented:** `structural_constancy` reads
     its target's SOURCE, so it degrades to UNSETTLED wherever `inspect.getsource` fails —
     inline lambdas, exec'd strings, REPL definitions. Honest behaviour, but the docstring never
     said the instrument is unusable in dynamic contexts.
153. **ROUND-10 DIFFUSE-TARGET QUESTION ANSWERED, NEGATIVELY.** Sensitivity is NOT constructible
     for a diffuse target and the contract cannot tell. `brier_score` certified on a pair that
     moves reliability (0.0000 -> 0.0100) AND resolution (0.0000 -> 0.2500) — holding calibration
     alone is impossible for an aggregate. **A SENSITIVITY pass on a diffuse target means only
     "these inputs differ somehow".** Repair, already in the literature: decompose first.
     `murphy_reliability` holds resolution fixed at 0.0000 and moves reliability 0.4225 -> 0.0000
     — genuine isolation, which is what Murphy 1973 is FOR. **Now a stated precondition of the
     contract rather than a silent hole.**
154. **Open, no answer: does "report dependence, not ownership" COMPOSE?** If A depends on C and
     B depends on C, nothing says what happens to A+B without C. Removals do not compose; the
     joint removal is a separate experiment and there are 2^k of them. Shapley composes and is a
     convention. I did not invent a middle under time pressure.
155. **A discomfort worth recording: I wrote both the instruments and their anti-cases.** Nine of
     twelve passed first time, which I read as "the contract has teeth and the arsenal was mostly
     sound" — but the less comfortable reading is that my own fixtures were too easy. Cycle 036
     already showed fixtures are gameable. Sourcing anti-cases from someone other than the
     author is the obvious fix and needs a second author.
