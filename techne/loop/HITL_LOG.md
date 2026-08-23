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


## Cycle 038 (2026-08-21) — were my anti-cases too easy? One of nine was

156. **HITL #78: 763 rows, 0 accepted, 100% drop, TWELVE cycles unruled.**
157. **HITL #155 ANSWERED, and the answer is yes for one of nine.** Domain-sourced anti-cases
     (invariant from the instrument's advertisement, input from a property search) found a real
     defect in `refinement_multiplicity` that my hand-written fixture missed: given a projection
     COARSER than the truth it returned 0 — outside its advertised range of >= 1 — reading as
     "perfectly efficient" when the projection is losing information. My fixture only ever fed it
     REFINING projections. **One of my nine passes was flattery; the other eight now have
     evidence that did not come from me.**
158. **FOURTH INSTANCE OF ONE BUG CLASS, and #151 now looks cheap by comparison.** A measure
     answering on input outside its own domain: structural_constancy (029), find_aliasing_witness
     (037), fiber_search (037), refinement_multiplicity (038). Three modules, four instances, each
     found by a DIFFERENT instrument and none by reading the code. **Stronger proposal than the
     registry: make it a TYPE.** A mandatory three-valued return (SIGNAL / NO-SIGNAL /
     OUT-OF-DOMAIN) makes the conflation unrepresentable rather than merely detectable. Would like
     a ruling between registry and type.
159. **The second violation was MINE, not the instrument's.** `brier_score` failed on
     ([1e-09], [0]) because I compared a squared quantity against an unsquared tolerance — a
     units error in the invariant I wrote. The instrument was correct. **Of two violations, one
     was the instrument and one was me**, which is the honest headline and also the documented
     residual hole: I still write the invariants. It fired loudly here; the same error can produce
     a false clean and nothing would catch it.
160. **HITL #153 partially answered.** I cannot show an arbitrary diffuse target admits a
     Murphy-style decomposition, but I can name where it plainly fails: **a target defined as an
     OPTIMUM OVER A FAMILY** ("the best achievable X", "distance to the nearest Y") has no
     components, because it is a minimisation rather than a sum of parts. Murphy works because
     Brier is algebraically a sum of three terms. So the sensitivity slot is enforceable for
     targets with an additive decomposition and I cannot certify anything else.


## Cycle 039 (2026-08-21) — the bug class made unrepresentable

161. **HITL #78: 790 rows, 0 accepted, 100% drop, THIRTEEN cycles unruled.**
162. **I predicted a fifth instance of the bug class and found THREE. It now stands at SEVEN
     across FOUR modules** — a measure answering on input outside its own domain:
     structural_constancy (029), find_aliasing_witness (037), fiber_search (037),
     refinement_multiplicity (038), murphy.skill (039), verify_factorization (039),
     uniform_adversary.schema_survived (039). Every one found by a DIFFERENT instrument, none by
     reading the code.
163. **Two of the three are worth your attention specifically.** `murphy.skill` returned 0.0 on a
     degenerate battery **and its own test asserted that** — the bug defended by the test written
     to guard it, which is cycle 018's lesson again. And `uniform_adversary` is the worst-placed
     of all seven: **that module's docstring warns against concluding sufficiency from a failure
     to enumerate, and its own report property did exactly that**, calling a schema SURVIVING when
     it had never run.
164. **HITL #158 BUILT.** `prometheus_math.measurement`: SIGNAL / NO_SIGNAL / OUT_OF_DOMAIN, with
     `.value` raising on OUT_OF_DOMAIN, `__bool__` raising always (every route — bool, not, and,
     or, implicit if), and OUT_OF_DOMAIN refusing construction without a reason. Each guarantee
     traces to a specific past bug. `value_or(default)` preserves explicit opt-in.
165. **HITL #151 SUPERSEDED FOR THIS BUG CLASS ONLY — and I want that scope on the record.** The
     type makes the eighth instance unwritable, which beats a registry that would only remind me
     to look. But cycle 038's mis-stated invariant has no type that forbids it, so **the registry
     question stands for bug classes that are not type-shaped.**
166. **What the type does NOT buy, tested rather than conceded:** a measure can still return
     SIGNAL where OUT_OF_DOMAIN was right — a judgement about the domain, which no type checks.
     `mistyped_domain_is_still_possible()` builds that measure and returns True.
167. **HONEST SCOPE — I did not do the migration.** The seven sites refuse by RAISING, not by
     returning `Measurement`; converting signatures would break every caller across 441 tests.
     `measured()` adapts a bare measure without touching its signature, so the repairs are
     expressible today and migration can be gradual. Calling this cycle a "retrofit" would
     overstate it.
168. **The rate is what worries me, not the count.** Seven instances of one bug in four modules,
     all mine, all written in the last three weeks. Either something about how I write measures
     generates this, or the empty/degenerate case is simply where all bugs live and seven is
     unremarkable for forty-odd measures. I cannot tell which from inside.


## Cycle 040 (2026-08-22) — the denominator: ten of forty

169. **HITL #78: 821 rows, 0 accepted, 100% drop, FOURTEEN cycles unruled.**
170. **HITL #168 SETTLED BY MEASUREMENT. TEN instances among FORTY measure-like functions — 25%.**
     Not a tail, a habit. The denominator comes from a MECHANICAL criterion (takes an argument,
     reduces to a scalar verdict) applied uniformly across eleven modules, so it is auditable
     rather than curated — cycle 038's lesson about choosing your own fixtures.
171. **Three new instances.** (8) `is_refinement_chain([])` returned True — "this IS a refinement
     chain" and "nothing was given" were the same answer. (9) `chain_direction([])` returned
     DESTROYING — downstream of 8 and it **inherited the defect verbatim**. (10)
     `find_splitting_witness` returned None for "nothing to compare".
172. **Instance 10 is the one I want on the record.** **Cycle 037 fixed exactly this conflation in
     `find_aliasing_witness` and left its dual, one file away, untouched.** The propagation failure
     happening inside the cycle that was repairing it. Duals are now a named entry in the traps
     ledger: after any repair, look at the twin first.
173. **HITL #167 CONSEQUENTLY SETTLED — the `Measurement` migration stops being optional.** I
     called it optional last cycle on the grounds that offering the type was enough. A 25% rate
     among functions written in three weeks says the next batch contains more, and offering is not
     using.
174. **A caveat I am putting in writing rather than letting the number stand alone.** Twenty-six
     REFUSES is not a clean bill of health: seven of those refusals were installed during cycles
     029-039 in response to this same class, three more this cycle. The audit measures the code as
     it STANDS, not as it was WRITTEN. As-written the rate was 10/40, and every repair was
     reactive.
175. **UNPROBED = 6, reported and not dropped.** A rate over only the probeable functions would
     flatter the result exactly the way cycle 038's hand-written fixtures did. Three of the six
     CONFLATES were also artefacts of my crude generic arguments (notably `reads_its_parameters`,
     whose `inspect.getsource` reach limit cycle 037 already documented) — separated by hand and
     reported as artefacts rather than counted as instances.
176. **Zero for ten on reading.** Not one of the ten was found by reading the code; every one
     surfaced from an instrument pointed elsewhere. I cannot tell from the record whether that
     means reading does not work for this class, or that I never read WITH THIS BUG IN MIND. Those
     imply different remedies — use tools, versus read with a checklist — and I would like your
     call, because I keep choosing the first without having established it.
177. **Open question I am not able to settle: is 25% actually high?** I have no comparison class.
     For all I know a quarter of any codebase's reducing functions mishandle the empty case and
     nobody measures it. Without a baseline from code I did not write, "habit" may be me
     pathologising an ordinary rate. Honest statement today: 10/40 here, unknown elsewhere.


## Cycle 041 (2026-08-22) — the migration priced, and a regime change accepted

178. **HITL #78: 859 rows, 0 accepted, 100% drop, FIFTEEN cycles unruled.** Up from 821.
179. **THE MIGRATION COST IS A NUMBER: 13 edits for ONE function** (11 tests + 2 production call
     sites), and it was the most-used of the eleven sites. All thirteen were made. This is what
     makes gradual migration honest rather than lazy — the other two live-from-production sites
     are deferred WITH the cost as the stated reason.
180. **The slice was picked by LIVENESS, not taste.** Attributing every refusal in the suite to
     its nearest caller frame: `refinement_multiplicity` had 99 refusals, 96 from PRODUCTION —
     96 of the 108 production refusals across all ten sites. Two sites (`skill`,
     `uniform_adversary`) are never CALLED at all by the entire suite; cycle 039 repaired two
     functions nothing invokes.
181. **A migration can improve the metric by shrinking the population — caught.** Converting a
     measure changed its return annotation, so it LEFT cycle 040's denominator instead of leaving
     the CONFLATES bucket. The rate would have improved because the population shrank. Confound in
     the flattering direction; `is_measure_like` now recognises `Measurement`.
182. **INSTANCE 11, and it was PREDICTED rather than stumbled on.** `verify_family_incapacity`
     returned `all_members_err=True` for an EMPTY family — vacuously, inside the module whose whole
     argument is that absence of a counterexample is not evidence of impossibility. Found by
     asking which functions carry the idiom and calling all four candidates. One in four real.
183. **Cycle 040's UNPROBED bucket was CONCEALING it.** I reported "UNPROBED=6, reported never
     dropped" as a virtue. It was counted and never checked, and two of the six carried the audit's
     own tell-tale string "answered on degenerate input". UNPROBED is a queue of work, not a
     footnote. I also hand-checked `information_profile` and DECLINED to count it — inflating is as
     dishonest as missing.
184. **THREE of my own instruments were defective this cycle and their anti-cases caught it.**
     The liveness probe used `inspect.stack()` and a 40-second suite did not finish in fifteen
     minutes. I wrote "non-invasive, no test outcome can shift" in its docstring and then measured
     it against a probe-off control: 376 passed vs 372 passed / 4 failed. The mechanism classifier
     reported ARITHMETIC_IDENTITY for a function that RAISES on empty input, matching the index
     literal in `xs[0]`.
185. **ROUND-11 CORRECTION ACCEPTED — "habit" WITHDRAWN.** No external corpus exists for this
     class, so there was no baseline to be high against. The claim is now **11/40 in this corpus,
     external prevalence unknown**, a LOCALLY RECURRENT DEFECT CLASS. Migration is justified by
     local expected loss, which it always was.
186. **ROUND-11 CORRECTION ACCEPTED — "reading does not work" WITHDRAWN.** Measured:
     P(found | INCIDENTAL reading) = 0/11. Never measured: P(found | TARGETED review with the bug
     as the question). Supported claim is only "incidental review has shown no sensitivity". The
     Lane A/B experiment is pre-registered in `rung_notes/LANE_AB_READING_EXPERIMENT.md` with
     predictions committed BEFORE running, including the discriminating case (does a reviewer who
     spots a root also carry it into the wrapper?).
187. **ROUND-11 CORRECTION ACCEPTED — three numbers, not one rate.** ROOTS 10 / EXPOSED SITES 11 /
     PROPAGATION FACTOR 1.10. That factor settles the diagnosis as repeated CREATION rather than
     failure to CONTAIN. Clustering rescues nothing and I should not have implied it did.
188. **REGIME CHANGE ACCEPTED, effective cycle 042.** The loop had become an instrument-making
     organism feeding on its own instruments, and cycle 041 is the clearest instance: probe ->
     defect in probe -> control for probe -> defect in classifier, total external yield one
     function in one synthetic module. Cycles 037-041 FAIL the gate. **Cycles 042-046 run ~80%
     real-substrate / 20% instrument repair.** The 20% queue is Lane A/B, then the two remaining
     live migrations. Nothing joins it without displacing something.
189. **JAMES — cycle 042 goes back to HITL #78 read-only, and I want the shape of it checked.**
     I am forbidden to patch ergon, so I can only observe. A read-only audit that produces another
     unruled finding would be the recursion in a new costume. What makes 042 a real test rather
     than another diagnosis? My plan is to ask what a DOWNSTREAM CONSUMER actually receives from a
     100%-drop loader — i.e. measure the defect's blast radius on live data rather than restating
     its existence.
190. **Track 1: `prometheus_math.normalized_vi`** (Meila 2007, J. Mult. Anal. 98(5):873-895), four
     categories, 12 tests, RED first. The n=1 edge REFUSES — log2(1)=0, so 0.0 would say
     "identical" and nan would propagate. **First time this loop designed the refusal in from the
     start rather than retrofitting it after an instrument caught it.**


## Cycle 042 (2026-08-22) — HITL #78 RESOLVED TO ROOT CAUSE. First real-substrate cycle.

191. **HITL #78 IS NO LONGER A DIAGNOSIS. ROOT CAUSE, one line:**
     `ergon/probe/assemble.py:load_prepass` filters on `int(d.get("rep", -1)) != 1`. **The live
     ledger rows have NO `rep` field and NO `uid` field** — they carry `key: [rep, uid]` as a
     two-element list. The default `-1` fails on every row; all 962 silently skipped.
     **Same file, same package, two readers, one right:** `campaign.py:best()` reads
     `tuple(r["key"])` correctly; `load_prepass()` reads flat fields that were never written.
     Field-level writer/reader mismatch at a seam. The data is fine: `key[0]` is 625 rep-1 /
     337 rep-2.
192. **JAMES — THIS IS THE ONE TO RULE ON, AND IT IS NOW CHEAP TO RULE ON.** Sixteen cycles of
     escalation, and the fix is two fields. I did not patch ergon and will not. The finding is
     actionable without a diff: `load_prepass` needs `rep`/`uid` lifted out of `key`, exactly as
     `best()` already does it.
193. **BLAST RADIUS CONFIRMED against a PRE-REGISTERED decision rule** committed as `0fd3273b`
     BEFORE any measurement, with the NULL outcome specified in advance. All four predictions held:
     Y4 consumer reach >=1 of 6 -> **1 of 6** (`campaign.py:312`); Y1 selection 0 vs 1/uid;
     Y2 packet **58 tokens vs 678-2662, mean delta ~2,070 tokens/task**; Y3 tau `{}` vs
     `{'p1_prepass': 624}`.
194. **Five of six call sites were NOT affected** — they read `nearmiss_mix-M30_prepass.jsonl`,
     where shipping loader and audit shim AGREE exactly (200 = 200): legitimate rep-2 filtering,
     not this defect. I came close to escalating a loader defect without checking which file the
     consumers read.
195. **THE CONSEQUENCE THAT EARNS SIXTEEN CYCLES.** The empty pool does not fail or warn. It emits
     `"no residue exists at this distance for this task"` and
     `"NOT-RUN-FOR-LACK-OF-RESIDUE (no eligible records)"`. **"No residue EXISTS" and "the loader
     rejected every row" are conflated into one message — asserted by the SPARSITY REPORT**, whose
     entire purpose is honest accounting of what the substrate did not record. The
     answering-outside-your-domain class **at pipeline scale, in production**, and the first
     instance the loop has found OUTSIDE its own code.
196. **LIVE EXPERIMENT IMPACT.** `campaign.py` builds `Arms.pool` from this loader for
     `F-prom-retrieved` and `F-null`. With `pool=[]`, the arm testing *whether prior-attempt
     residue helps* ships 58 tokens of boilerplate saying there IS no prior attempt — a null
     contrast presented as a treatment.
197. **TIMING: CAUGHT BEFORE THE DAMAGE.** Campaign is LIVE (lock pid 9820, `phase=P1 sent=400
     ok=400 coverage=697/1240`). P3 constructs `Arms`. `campaign_log.jsonl` is an APPEND-ONLY
     phase log and contains exactly one phase record — P1. No results contaminated. The directory
     already holds `p1_prepass.TRUNCATION-CONFOUNDED-8192.jsonl`, a quarantined earlier run, so a
     second wasted campaign was the live risk.
198. **Evidence-type caveat I caught on myself mid-write.** I first argued "P3/P4 never ran" from
     ABSENT output files — the absence-is-not-evidence error this cycle is about. The version I
     rely on is the append-only phase log, which is a present record. It still assumes the log is
     written for every phase and never fails, which I have NOT verified.
199. **ROUND-12 CORRECTION ACCEPTED — "13 edits/function" WITHDRAWN as an estimate.** It is one
     observation from a deliberately high-liveness site: `C_site=1 = 13`, not `C_migration ~ 13N`.
     Better unit: **edits per production call edge = 13/2 = 6.5**. From cycle 043 each migrated
     site records (callee edit, direct callers, tests, transitive type fallout); a distribution
     needs 3-5 sites and I have one.
200. **ROUND-12 CORRECTION ACCEPTED — prevalence and exposure are TWO POPULATIONS.** Repository
     prevalence stays **11/40 WITH dead code included**; removing it would rewrite a historical
     audit because the code happens not to execute today. Live exposure is a separate number over
     functions actually reached in production, and 96/108 approximates the event version. The two
     repaired-but-never-called functions are evidence about how the code was WRITTEN and near-zero
     evidence about current blast radius.
201. **Constraint honoured: no new general-purpose instrument.** The replay used functions that
     already existed. The mechanism is pinned in 7 tests against a synthetic row in the live
     writer's schema, so evidence does not depend on a file the campaign is actively rewriting.
     **Those tests SHOULD go red when ergon fixes the seam — delete the file when they do.**
202. **JAMES — the uncomfortable question the regime change surfaces.** This cycle produced a root
     cause and a pre-emptive catch, which is what was asked for. But I still cannot ACT on it.
     Sixteen cycles suggests the bottleneck is not detection. Is a finding I am structurally
     unable to fix "improving the organism", or a better-dressed diagnosis? If the latter, the
     read-only constraint on ergon may be the thing to revisit, not the loop.
203. **Track 1 (the 20%): `prometheus_math.normalized_mi`** (Strehl & Ghosh 2002, JMLR 3:583-617),
     `NMI = I/sqrt(H(X)H(Y))`, 12 tests, RED first, four categories. Edge: EITHER side zero-entropy
     REFUSES because the ratio is 0/0, and **the error names WHICH side**. A property test asserts
     `NMI != 1 - normalized_vi` in general, to stop a future caller substituting one for the other.


## Cycle 042 CORRECTION (same cycle, before 043)

204. **Y₄'S DENOMINATOR WAS WRONG: 1 of 8, not 1 of 6.** A repo-wide scan finishing after the
     write-up found two consumers I missed — `charon/probe/run_r7_d1d2_build2.py:75` and
     `harmonia/probe/c_static_leakage_probe.py:97`. **My error was the search:** I grepped
     `ergon techne engine`, three directories I chose, instead of the repository. Choosing the
     search window is choosing the answer.
205. **The substantive finding is UNCHANGED and the prediction's direction still holds.** Both
     missed consumers read a third ledger, `ergon/probe/ledgers/probe_prepass.jsonl`, never
     previously measured: raw=252, shipped=126, **drop 50%**, rep distribution 126 one / 126 two,
     and **zero rows carrying `key`** — it has flat `rep` fields. They are not affected.
206. **THE CORRECTION SHARPENS THE DIAGNOSIS — and this is the part worth your attention.** Three
     ledgers now measured against the same loader: `probe_prepass.jsonl` (flat `rep`, loads),
     `nearmiss_mix-M30_prepass.jsonl` (flat `rep`, loads), `p1_prepass.jsonl` (`key:[rep,uid]`,
     100% drop). **Two of three producers emit the schema the loader expects; the campaign writer
     is the odd one out.** That relocates the fix to the WRITER (`p1`/`push_jobs`), aligning it
     with two existing correct producers — rather than to the reader, which would then have to
     tolerate a shape only one producer emits. **I could not have said which side to fix from the
     two files I published; with three I can.**

207. **ROUND-13 FOLD-IN — the two facts are separated, and the first is not softened by the
     second.** (a) Y₄ was wrong: a scope-of-enumeration failure, and the repo-wide denominator is
     part of the evidence rather than bookkeeping around it. (b) Independently, the pre-registered
     direction survived. My first correction stated these together, which read as mitigation.
     "The conclusion held anyway" is precisely how a bad denominator survives review.
208. **"Writer is wrong" DOWNGRADED to DE FACTO — and I verified it rather than hedging.** A
     repo-wide search found **no field-level schema specification for these ledgers anywhere in
     the repo**. `load_prepass`'s docstring cites "prereg §4.2, review C1", but that governs the
     rep-1-only POLICY, not the wire format, and the cited document is not in the repository.
     `ResidueRecord` defines the in-memory shape only. Flat `rep` is therefore the OBSERVED
     contract — strong triangulation, not authority.
209. **JAMES — the absence is the finding underneath the defect.** Three producers, across three
     roles (ergon, charon, harmonia), write to one shared consumer, and **no field-level contract
     is written down anywhere**. A seam whose fields are unspecified will drift; the only question
     is which producer drifts first. #78 is the first drift, not a one-off. If you want the class
     closed rather than the instance, the ask is a written ledger schema — and that is a decision
     I cannot make for ergon.
210. **NEW DOCTRINE, reusable: seam triangulation.** *A two-party mismatch identifies a seam; a
     third independent conforming implementation localizes responsibility for it.* Written up in
     `techne/loop/rung_notes/SEAM_TRIANGULATION.md`. Application rule: enumerate implementations
     REPO-WIDE; measure a known-good pair as control; name the outlier only if a third conforming
     implementation exists; say *de facto* unless a written schema adjudicates; report the
     schema's absence when there is none.


## Cycle 043 (2026-08-22) — the class test was underpowered, and the flaw was in my pre-registration

211. **HITL #78: 998 rows, 0 accepted, 100% drop, SEVENTEEN cycles unruled.** Seam NOT repaired —
     the seven pinned tests built to go RED on repair are all still green. Campaign still in P1
     (one phase record, no `p1_bandread.json`), so `Arms` was never constructed and **no results
     are contaminated**. Root-caused since cycle 042: writer-side, two fields.
212. **THE CLASS QUESTION IS UNANSWERED, NOT ANSWERED NULL.** Pre-registered and committed
     (`04ecd2d8`) before measuring. My decision rule for NULL was technically satisfied, and **I am
     not claiming it**: three of four test pairs were unmeasurable and a null on n=1 is an absence
     dressed as a result — the exact error this cycle's subject matter is about.
213. **The flaw is mine and it is specific: I declared a sample size without first checking the
     population was measurable.** `load_theseus_rejected` and `load_wall_oracles` have no data on
     disk at all; `load_signature_classes` is sqlite, not JSONL. One minute of checking beforehand
     would have caught it. **Pre-registration needs one more step: verify measurability before
     fixing n.**
214. **The population was also too narrow.** I chose the `assemble.py` shared-loader family because
     it was the exact analogue of #78. Scoping afterwards (reported as scope, not as a test):
     **893 JSONL files repo-wide, 564 under the role directories.** A powered sweep is available;
     I picked a population of four.
215. **WHAT DID WORK — the control, and it is worth keeping.** Prediction 3 held: **drop rate alone
     does NOT separate the class; FIELD PRESENCE does.** `p1_prepass.jsonl` 1001->0 with `rep`/`uid`
     ABSENT matched the signature; `nearmiss_mix-M30` (400->200) and `probe_prepass` (252->126) both
     drop 50% with the fields PRESENT and are legitimate. **An instrument keyed on drop rate would
     have flagged two healthy ledgers.**
216. **The one measurable test pair is clean, verified against the loader's ACTUAL filters rather
     than the ones I guessed.** `load_forge_scraps` x `agents/hephaestus/ledger.jsonl`: 6661 rows,
     `status` present in all (6276 scrap / 385 forged), `reason` present in all and never null among
     scraps, 6276 - 2861 transport failures = **3415 kept, matching the loader exactly**.
217. **JAMES — a methodological question I cannot settle alone.** When a pre-registration turns out
     to be UNEXECUTABLE rather than merely wrong, what is the correct move? Amending mid-cycle is
     what pre-registration exists to forbid; burning a cycle on n=1 to honour a bad design also
     seems wrong. I chose to honour it and report UNDERPOWERED. I would like that ruled on, because
     it will recur.
218. **A flattery problem I have NOT solved, flagged against myself.** Field presence separated the
     control perfectly — but the control contains the single true positive that inspired it. The
     discriminator has been validated on exactly one true positive and no independent one. That is
     the cycle-038 problem in a new place, and I am not treating it as validated.
219. **Hypothesis caught a defect in my own test guard (Track 1).** I guarded property tests on
     `len(p) > 1 and len(t) > 1` — a PROXY — when the real condition is `max - expected != 0`. Two
     all-singleton partitions pass the proxy and are degenerate; `a=[0,1,2]` found it immediately.
     The implementation was right to refuse; **the guard was measuring the wrong thing**, which is
     the same error shape as guarding a measure on the wrong domain predicate.
220. **Track 1: `prometheus_math.adjusted_rand`** (Hubert & Arabie 1985, J. Classification
     2(1):193-218), 12 tests, RED first, four categories. Completes a deliberately-disagreeing trio
     with `normalized_vi` (041) and `normalized_mi` (042). **ARI CAN GO NEGATIVE** — constructed
     explicitly, because clamping to 0 erases "no better than chance" vs "actively anti-correlated".
     The notorious **0/0 refuses**: when both partitions are one block or both all singletons,
     `max == expected`, and returning 1.0 is seductive precisely BECAUSE the partitions really are
     identical — still wrong, since the number would come from dividing by zero.
221. **JAMES — seventeen cycles on #78, root-caused, and I am structurally forbidden from fixing
     it.** The regime change was meant to make the loop improve the organism rather than diagnose
     itself. Two cycles in, the binding constraint looks like the read-only rule rather than
     detection capability. If that reading is right, the thing to change is the constraint.


## Cycle 044 (2026-08-22) — #78 closed to read-only; the class hypothesis RETIRED

222. **HITL #78 CLOSED TO READ-ONLY INVESTIGATION.** Marked
     **ROOT-CAUSED / UNREPAIRED / CURRENTLY UNCONTAMINATED** in
     `rung_notes/HITL78_STATUS_CLOSED_READONLY.md`. 1035 rows / 0 accepted (was 998), still P1,
     eighteen cycles. **epistemic closure != operational closure**: detection has done everything
     it can, and the READ-ONLY BOUNDARY is now the binding limit, not capability. I am no longer
     spending cycles asking "is it still broken?"
223. **Reactivation conditions, and one is urgent.** Reopen only if (1) the writer changes,
     (2) **a P3/P4 record appears in `campaign_log.jsonl` or `p1_bandread.json` appears — this
     converts a latent defect into ACTIVE CONTAMINATION of the arm the campaign exists to
     measure**, or (3) patch authority becomes available. The seven pinned tests are the standing
     detector for (1) at 0.2 s.
224. **DOCTRINE: a feasibility failure may TERMINATE a pre-registration but must not MUTATE it.**
     P0 (cycle 043) stands exactly as written at UNDERPOWERED and does not retroactively become a
     result. P1 is a NEW pre-registration (`b36050c0`). Silently widening P0 after seeing which
     cases exist would be outcome-conditioned redesign.
225. **NEW STANDING PREREG STEP:** enumerate the eligible population and VERIFY MEASURABILITY
     BEFORE SAMPLING, without inspecting the discriminator or the outcome. P1 feasibility: 615
     non-empty .jsonl under role dirs, 289 JSONL-parsing readers, 107 unresolved literals
     reported, **n = 150 executable (reader, ledger) pairs over 66 ledgers and 90 readers**.
226. **The abstraction moved up and it was right.** `key:[rep,uid]` is a NESTING violation, not an
     absence. Class under test became **producer/consumer contract violation**; field presence
     demoted to a **candidate signature with n_positive = 1**.
227. **The sufficiency arm was INVALID, exactly as pre-declared.** 134/150 pairs flagged — 89%,
     which is my extractor collecting every `.get("x")` in a FILE rather than fields applied to
     records from THAT ledger. Prediction 2 declared the confound in advance and it landed. **Half
     the experiment did not run and I am not reporting it as a refutation.**
228. **The necessity arm ran cleanly and came back EMPTY.** Zero adversary-B instances and zero
     independent positives across 150 pairs.
229. **VALID by-product, extractor-independent: 12 of 66 ledgers carry >1 key-signature** — mostly
     benign record polymorphism. **The dangerous-looking one is correctly handled:**
     `charon/ceiling_v0/runs/b2_base20/records.jsonl` (500 rows, 3 signatures, 20 rows lacking
     `acc_post`) is guarded at `analyze.py:51` by `if r.get("acc_post") is not None`; the two
     unguarded readers index records returned directly from `substrate_arm()`, never the
     heterogeneous file. **Where I checked, this codebase handles polymorphic ledgers correctly.**
230. **VERDICT PER THE PRE-REGISTERED RULE: CLASS HYPOTHESIS RETIRED.** #78 looks like an ISOLATED
     INCIDENT. Three cycles spent on a class the evidence does not support; the 80% real-substrate
     budget moves off schema drift entirely.
231. **JAMES — the 80% budget is now UNALLOCATED and I need a target.** The new gate is *real
     substrate + actionable intervention*, or where read-only by design, *real substrate +
     predeclared decision consequence*. **The constraint that I cannot patch any other role
     eliminates most of the repo from the first form.** What target lets the loop complete
     detect -> intervene -> measure postcondition? This is now the binding question for the
     regime change, and I cannot answer it without you.
232. **Track 1: `prometheus_math.fowlkes_mallows`** (Fowlkes & Mallows 1983, JASA 78(383):553-569),
     13 tests, RED first, four categories. Completes the family as the NON-chance-corrected member.
     On a constructed below-chance pairing **ARI < 0 while FM >= 0** — treating them as
     interchangeable loses the "worse than chance" signal. All-singletons refuses at 0/0 **and the
     test proves it is not confused with a genuine zero**, which returns 0.0 and does not raise.
     The property-test guard computes the ACTUAL precondition, applying cycle 043's lesson.


## Cycle 045 (2026-08-22) — the full arc completed, on my own arsenal

233. **HITL #78: unchanged.** `phases: ['P1']`, no P3/P4, no bandread. Latent, uncontaminated,
     standing detector green in 0.22 s. Not reopened — one line, per the closure.
234. **80% BUDGET ALLOCATED AND JUSTIFIED IN WRITING BEFORE THE WORK** (#231 was unruled, so I
     decided rather than blocked). Rejected: Lane A/B (methodology on my own modules — NOT real
     substrate; in the 80% it would be the instrument-eating-itself failure mode wearing the regime
     change as a costume), the Measurement migration (instrument maintenance), the cycle-044
     extractor (no decision changes on any outcome).
235. **CHOSEN: the 30 failing tests in `prometheus_math` — and they had been red since cycle 041
     while I spent three cycles auditing another role's loader.** Real substrate, I own it,
     postcondition measurable.
236. **Classification pre-registered before the list was inspected**, with TEST-BUG ordered ABOVE
     the DEFECT rules so a wrong test must be ruled out before claiming a product defect. n = 30,
     matching the stable prior exactly. **ARTIFACT-DEPENDENCY 26 / TEST-BUG 1 / DEFECT-LOGIC 1 /
     ARTIFACT-ENVIRONMENT 2.** All three predictions held.
237. **FIX 1 — a test asserting continuity ACROSS A BRANCH CUT.** The discrepancy was EXACTLY the
     dilogarithm's branch discontinuity `2*pi*ln(1/z)` to twelve decimals (re=0.5 -> 4.355172180607,
     re=0.25 -> 8.710344361214, re=0.8 -> 1.402052283009), with off-axis agreement ~5e-16. The guard
     was `abs(z) > 0.99` — a PROXY — when the precondition is that `1/z` not lie on `[1, inf)`.
     Fixed on the actual condition, and **the excluded case is PINNED as an exact identity, not
     dropped.** Postcondition 27+1F -> 28 passing.
238. **FIX 2 — an import broken by a file move, invisible to everything static.**
     `lehmer_brute_force.py:1056` put the REPO ROOT on `sys.path` and imported a worker that lives
     in `scripts/`. Inside a function, multiprocessing path only. Postcondition 19+1F -> 20 passing.
239. **FOUND, NOT FIXED, AND STATED: all 48 hyperbolic knots carry `hyperbolic_volume = 0.0`**
     (`_LAST_LOAD_SOURCE = "curated-only"`). **A hyperbolic knot with volume 0.0 is mathematically
     impossible.** Origin environmental (KnotInfo absent); manifestation is the conflation this loop
     has chased all month, in code I own. **Deferred because `hyperbolic_volume` has 44 non-test
     references** — a typed change across all of them needs its own prereg and C_site measurement.
240. **RESULT: 30 red -> 28 red, nothing silenced.** The pre-registered self-guard held: no test was
     marked skip or xfail, and the number reported is the FIXED count, never the SILENCED count.
241. **SECOND-ORDER FINDING — 26 of 30 reds are missing optional dependencies, so the arsenal's
     suite has NOT been a working regression detector for as long as they have existed.** Two real
     defects were hiding in that noise.
242. **JAMES — where is the line on installing dependencies?** Installing chipfiring, GUDHI,
     shapely and a MIP backend would clear 26 reds and reveal whatever they mask. It is cheap and
     high-value, but it is arguably repo infrastructure, which HITL #147 says not to build unasked.
     I have NOT installed anything. Your call.
243. **JAMES — was deferring the knot fix right?** Shipping mathematically impossible values may be
     severe enough to pre-empt everything else. I judged the 44-call-site blast radius too large to
     smuggle into a cycle about something else, but I would like that judgement checked.
244. **I HIT THE SAME GUARD-ON-A-PROXY ERROR TWICE — cycle 043 and cycle 045 — having written it
     into the traps ledger in between.** A lesson recorded and not generalised is worth
     approximately nothing. I do not know what would make a trap actually transfer rather than be
     re-learned per instance, and I would like a view on it.
245. **Track 1: `prometheus_math.rand_index`** (Rand 1971, JASA 66(336):846-850), 12 tests, RED
     first, four categories. **All-singletons is DEFINED here (RI = 1) while `adjusted_rand` and
     `fowlkes_mallows` both refuse at 0/0** — the family does not share a domain, pinned in one
     test. Hubert & Arabie's motivation is demonstrated, not asserted: on a below-chance pairing RI
     stays above 0.5 while ARI goes negative.

246. **POSTCONDITION CORRECTION — 30 red -> 29, not the 28 I predicted.** Before: 30 failed /
     3441 passed. After: 29 failed / 3455 passed. Both fixes HELD; a THIRD previously-unseen
     failure appeared (`test_sigma_env_learning::test_property_seed_reproducibility`).
     **I checked whether I caused it rather than assuming**: passes in isolation 2/2; the only
     contamination path my changes created is the lehmer fix inserting `scripts/` into `sys.path`
     process-wide, so I ran that test file together with the lehmer file IN ONE PROCESS — 42
     passed; and it is an explicitly stochastic REINFORCE test. Order/state-dependent flake.
     **I cannot prove it was flaking before this cycle without an expensive bisect and do not
     claim it.**
247. **The flake SHARPENS #241 rather than denting it.** I only saw it because I was watching the
     count. A suite frozen at 30 red hides intermittent tests exactly as it hides regressions —
     the number never moves, so nothing draws the eye. Two real defects and one flake were all
     invisible in the same noise.
248. **A trap I set for myself and nearly walked into: I predicted the postcondition (28) and had
     written it into the cycle doc before measuring.** Defence added: measure, diff the before/after
     lists BY NAME, and explain any discrepancy before publishing.


## Cycle 046 (2026-08-22) — impossible values removed; BLOCK 042-046 CLOSES

249. **HITL #78: latent, unchanged.** `phases: ['P1','P1']`, no P3/P4, detector green in 0.33 s.
250. **HITL #242 UNRULED, so nothing was installed** and the dependency track stayed blocked. Took
     the knot-volume track instead, as instructed.
251. **THE DEFECT, in one line of the loader:**
     `pool = [e for e in pool if e.hyperbolic_volume > 0.0 or e.trace_field_class != 0]` —
     **0.0 means "NOT hyperbolic" in the left clause and is carried as a MEASURED volume in the
     record.** The defensive `or` admitted 48 entries as hyperbolic while their volume field said
     the opposite. A hyperbolic knot has volume > 0 by Mostow rigidity.
252. **C_site MEASURED, AND IT CORRECTS ME.** Cycle 045 deferred on "44 non-test references"; the
     pre-registration flagged the number as suspect before measuring, and it was wrong. Real
     figures: **callee edit ~40 lines / direct FIELD readers 3 / tests 1 / transitive type fallout
     0.** The other ~41 were a SAME-NAMED FUNCTION (`pm.topology.hyperbolic_volume`), docstrings,
     and module internals. **The deferral rested on a measurement conflating a field with a
     function — a worse error than the one I deferred, because an inflated cost looked like
     prudence.**
253. **FIX, no data invented.** `hyperbolic_volume_known: bool = True`, additive and defaulted, set
     False wherever the fallback invents 0.0; cache round-trip preserves it and **an old cache row
     without the flag rehydrates as UNKNOWN** rather than resurrecting the claim. Result: 0 entries
     claim a measured zero, 48 explicitly unknown. Five pinning tests.
254. **POSTCONDITION BY NAME-DIFF: 29 -> 28, and the knot fix did NOT cause it.** The one test that
     went green is the FLAKE identified in cycle 045 — independent confirmation of that diagnosis,
     since nothing this cycle touched it. **The two knot authority tests are STILL RED, exactly as
     pre-registered.** Making them green would have meant fabricating a measurement.
255. **BLOCK VERDICT 042-046: PASSED 4 of 5.** 042 PASS(a), 043 FAIL (underpowered), 044 PASS(c),
     045 PASS(a), 046 PASS(a).
256. **JAMES — THE DRIFT IS THE REAL FINDING OF THE BLOCK.** 80/20 was honoured by time, but the
     first half found defects in a live system I am FORBIDDEN to fix, and the second half found
     defects in MY OWN TREE, which I can. Cycles 045-046 completed detect -> intervene -> measure
     on code whose only consumers are me. **The block never once completed the full arc on
     something another role depends on.** "Real substrate + actionable intervention" has quietly
     resolved to "MY substrate", and those are different bars.
257. **PROPOSAL FOR THE NEXT BLOCK:** target `prometheus_math` functions with DEMONSTRATED
     CROSS-ROLE CONSUMERS — I own them so intervention is permitted, other roles import them so the
     defect matters beyond my tree. First move: enumerate repo-wide which arsenal functions other
     roles actually call, feasibility verified before sampling, ranked by consumer count. Scoping,
     well under a cycle. **I am not confident this is a fix rather than the same retreat with a
     better justification, and would like that challenged.**
258. **STILL BLOCKING ON #242.** 26 of the 28 remaining reds are missing optional dependencies.
     Until it is ruled, the arsenal's suite is a broken regression detector and every cycle spent
     on it is half-blind.
259. **Track 1: `prometheus_math.mirkin_metric`** (Mirkin 1996 ch.5 / Mirkin & Chernyi 1970), 13
     tests, RED first, four categories — the METRIC of the pair-counting family. **Has the triangle
     inequality, which `rand_index` does not**, so `1 - RI` is not a safe distance. **`n = 1` is
     DEFINED at 0 here while `normalized_vi`, `adjusted_rand` and `fowlkes_mallows` all refuse** —
     third cycle running that this family has not shared a domain.


## Cycle 047 (2026-08-22) — the drift answered; a four-role function was silently wrong

260. **HITL #78 latent, unchanged, not reopened. Arsenal red 29** (26 dependency artifacts;
     **#242 still unruled, nothing installed**).
261. **THE 042-046 DRIFT WAS NOT STRUCTURAL — it was a target-selection habit.** Repo-wide scoping
     (12,543 files, 40 non-mine directories, no claim attached): **79 files across 7 roles import
     my code** — charon 41, ergon 19, aporia 7, scripts 4, sigma_kernel 4, harmonia 3, theseus 1.
     Top callable I own by distinct consumer-role count: **`mahler_measure` at FOUR roles.**
262. **PREDICTION 1 HELD 8/8: the mathematics is correct.** Lehmer's polynomial to
     1.1762808182599187 against published 1.176280818259917, plus golden ratio, Kronecker linear
     cases, three cyclotomics and a product.
263. **PREDICTION 2 FAILED — and that is a real result.** Every pre-registered degenerate case
     (empty, all-zero, single zero, float zero) **refused correctly**. The locally recurrent defect
     class was NOT present in the most-used function I own. Evidence the class is not everywhere,
     which sharpens cycle 044's retirement of the class hypothesis.
264. **DEFECT 1 (unpredicted, found by a ComplexWarning WHILE THE SUITE RAN):** the degree-0 branch
     computed `abs(float(coeffs[0]))`, and `float(complex)` discards the imaginary part.
     **`M(3+4j)` returned 3.0 (correct 5.0); `M(1j)` returned 0.0 (correct 1.0).** The second is
     severe — **a zero measure for a NON-ZERO polynomial, and 0.0 is exactly the value the
     zero-polynomial guard exists to make unreachable.** The degree>=1 branch of the SAME FUNCTION
     used `abs(coeffs[0])` correctly, so it disagreed with itself about one coefficient. Fixed.
265. **DEFECT 2 — A PRECISION BUDGET NOBODY HAD MEASURED.** My own multiplicativity property test
     failed under Hypothesis; **I did not assume it was my test.** mpmath at 50 dps refereed: the
     implementation matches `M(f)` to **1.4e-10**, and the whole discrepancy is in the product,
     where `np.roots` displaces a root by 1.9e-6 and mpmath's own `polyroots` fails to converge.
     Measured budget: **1.2e-15 to 5.1e-6 depending on conditioning.** My first hypothesis (roots
     on the unit circle) was WRONG — Lehmer x (x-2) has them and is fine at 1.9e-15; the driver is
     root DISPLACEMENT.
266. **JAMES — THIS ONE HAS A CONSUMER CONSEQUENCE.** Lehmer's constant is 1.17628... and searches
     for a smaller Mahler measure work at fine resolution. **A 5e-6 error is LARGER than the gaps
     such a search resolves**, so a candidate could be mis-ranked. I have NOT checked whether any
     of the four consuming roles actually operates at that resolution. Should cycle 048 trace that,
     or is documenting the limit enough?
267. **Tolerance was set to the MEASURED budget, not loosened to green.** The characterisation is
     pinned in its own test (well-conditioned products asserted at 1e-13, the known bad case
     bracketed), so a future loosening has to argue with data.
268. **POSTCONDITION BY NAME-DIFF: 28 -> 29.** The single new failure was **my own new test**, now
     green after measuring. Nothing else moved.
269. **Track 1: `prometheus_math.polynomial_length`** (Mahler 1960, Mathematika 7:98-100), 20
     tests, RED first, four categories. **Its zero-polynomial case REFUSES deliberately** rather
     than returning the arithmetically-defensible 0.0 — a screen whose domain is wider than the
     thing it screens passes inputs the expensive step then rejects. Composition is **Mahler's
     two-sided bound M <= L <= 2^deg * M** against the function validated the same day.


## Cycle 048 (2026-08-22) — two worries closed by measurement, one of them mine

270. **HITL #78 REACTIVATION FIRED AND THE DEFECT NEVER BIT.** `p1_bandread.json` appeared.
     **The campaign ENDED at P1** — `campaign_end`, `UNDECIDED-UNDERPOWERED`, coverage 1240/1240,
     `n_required_for_decidability` 2969. **P3 constructs `Arms`; P3 never ran.** The
     `F-prom-retrieved` arm was never built. **REALISED BLAST RADIUS: ZERO.** Loader still broken
     (1248 rows, 0 accepted) and still latent for a future campaign reaching P3.
271. **My own detector was OVER-BROAD.** I wrote the trigger as "P3/P4 record OR `p1_bandread.json`
     appears", but bandread is P1's OWN output — it fires at the END of P1, not the start of P3.
     Safe direction, but imprecise. **A reactivation condition should name the earliest event that
     implies the harm, and no earlier.**
272. **THE PRECISION WORRY DOES NOT BITE — HITL #266 ANSWERED, documenting is enough.** Recomputed
     **all 8,625 catalog entries**: max |recomputed - stored| = **4.481e-10**, and **zero** entries
     exceed `lookup_by_M`'s default `tol=1e-6`. Four orders of headroom on the one path where a
     consumer's correctness depends on it.
273. **THE CORRECTION I OWE CYCLE 047.** I wrote that a 5e-6 error "could mis-rank a candidate".
     **That was speculation stated with too much force.** The 5.1e-6 came from a SYNTHETIC product
     of two Hypothesis-drawn polynomials; the real catalog runs at 4.481e-10. Cycle 045 overstated
     a COST (44 vs 3); cycle 047 overstated a RISK. **Both were one unrepresentative measurement
     generalised to real usage. That is now twice, and I do not have a rule that would have caught
     both.**
274. **JAMES — A FINDING IN APORIA'S LIVE EXPERIMENT, NOT MINE TO PATCH.** The band
     `1.001 < M < 1.18` in `aporia/experiments/reasoning_steering/stage0b` selects **21 entries and
     every one has Lehmer's measure** — 21 genuinely distinct polynomials (degrees 10-28: Lehmer x
     Phi_1, Phi_2, Phi_3, Lehmer-extensions) whose measures are identical because M is
     multiplicative and cyclotomics have M=1. Stored measures span **2.1e-14**. `corpus.py` sorts
     by `(mahler_measure, coeffs)` "so the slice is reproducible": it IS reproducible (frozen
     literals) but **the order is decided by rounding in the 14th-16th decimal**, and the `coeffs`
     tiebreaker only fires on EXACT ties so it almost never runs. **Anything sorting that slice by
     measure is sorting by noise.** Whether the effective sample is 21 states or 1 object wearing
     21 hats is a question for whoever owns that experiment.
275. **I fixed my own assertion, not my measured budget.** `BUDGET < default/100` with both equal
     to 1e-8 — strict inequality on equal numbers, my arithmetic slip. Loosening a budget set from
     a measurement to satisfy a mis-stated inequality would be moving a goalpost.
276. **POSTCONDITION 29 -> 30 by name-diff.** The new failure
     (`test_extract_anti_anchor_claims_v0_1`) is **not mine** — passes in isolation, whole file
     12/12, and 40 passed when run in one process directly after both my new files. Second
     order-dependent flake in four cycles. **I cannot prove it predates this cycle without a
     bisect and do not claim it.**
277. **A near-miss worth recording: I almost diffed against an INCOMPLETE background run** whose
     output file held partial results, which would have reported "29 -> 0 failures". Caught because
     the number was absurd, not because I had a guard.
278. **Track 1: `prometheus_math.house`** (Everest & Ward 1999 ch.1), 23 tests, RED first, four
     categories. **Lehmer's polynomial is SALEM so house = M exactly** — one test is an authority
     check on both quantities. **A non-zero CONSTANT refuses** (no roots at all, while M and L are
     defined and equal |c|) while **a MONOMIAL correctly returns 0.0** — which is exactly why the
     constant must refuse rather than return zero, or the two would be indistinguishable.


## Cycle 049 (2026-08-23) — the read-only constraint lifted, and a retrospective audit of 001-048

279. **JAMES RULED #221: "you can act."** Recorded as doctrine in
     `memory/feedback_techne_may_patch_other_roles.md`. First exercise of it closed HITL #78
     after eighteen cycles.
280. **#78 IS FIXED (`c6736671`) — AND THE FIX I SPENT EIGHTEEN CYCLES ASKING FOR WOULD HAVE
     BEEN HARMFUL ON ITS OWN.** Three defects sat behind the 100% drop, not one: (1) rep/uid
     read flat while `campaign.py` writes them inside `key`; (2) count-family prose routed by
     a **filename prefix**, and the campaign ledger carries no `ledger_id`, so fixing (1)
     alone would have shipped raw count-family prose into `F-prom-retrieved` — the exact
     channel `method_projection` exists to withhold (measured 45% vs 25% answer leakage);
     (3) the gold screen sat **downstream of the rep filter**, so it inspected none of the
     1,604 KEY-form rows. **The broken loader was accidentally acting as the firewall.**
     Postcondition: 0 -> 625 accepted, 0 raw prose, FLAT ledgers bit-for-bit unchanged,
     `ergon/probe/tests` 163 passed. Blast radius measured BEFORE reordering the screen:
     0 forbidden fields across all 3,456 live rows.
281. **THE EIGHTEEN-CYCLE CLAIM WAS A WRONG-POPULATION ERROR — MINE.** "The loader throws away
     every row" is false. Five FLAT-form ledgers (1,852 rows) load correctly; only the two
     KEY-form files drop to zero. I measured one file and quoted it as a property of the
     consumer. **Fourth instance of `feedback_wrong_population_statistics`, committed by the
     role that files that trap against everyone else.** Memory updated.
282. **HITL #209 DISCHARGED:** the prepass wire contract is now written down in
     `_prepass_identity`'s docstring, and both forms are pinned by 8 tests
     (`test_prepass_wire_contract.py`) so the next producer cannot drift silently.
283. **RETROSPECTIVE PREDICTION 1 FALSIFIED: 4 O-PROMISEs, not >= 5.** Reported as falsified
     rather than reclassifying the `O-DANGLE` to reach five. **O-1 Band H (H1, H2) never built
     and never withdrawn** — canon §6 calls it *"James's thesis, formalized and falsifiable"*,
     and the charter allowed theory to substitute for building, so non-measurability did not
     block it. **O-2** the second pass restarted at R3, not R0. **O-3** the R0 baseline lane
     (HITL #2) was never wired into `grading_oracle.py` and, the actual fault, **never
     withdrawn** when the read-only rule made it impossible — silence is not a withdrawal.
     **O-4** the Lane A/B reading experiment was pre-registered at 041, queued at 045, never run.
284. **JAMES — THIS WEAKENS MY OWN #242 ASK AND YOU SHOULD HAVE IT BEFORE YOU RULE.** `egglog`
     was installed at cycle 003 on a stated leverage claim ("real leverage on rule
     composition"). It is referenced by **exactly one file in the repo** — a demo — and by no
     circuit, no test, no module. **The last dependency I took on a leverage argument was never
     consumed.** I still think the four deps are worth installing to clear 26 reds, but my
     track record is one-for-one against me, and a vetting protocol does not fix that failure
     mode — it is a *usage* failure, not a *supply-chain* failure.
285. **THE PROXY TRAP, FOURTH INSTANCE — AND ONE WAS IN ANOTHER ROLE'S CODE.** I nearly filed
     "tensor_train violates Standing Order #1" from a grep of **top-level imports**; it wraps
     quimb via a lazy import. Cycles 043, 045, this near-miss, and ergon's `ledger_id`-prefix
     gate. **The fourth being someone else's code is the useful part: this trap is not
     idiosyncratic to me.** The prereg's self-guard (every finding must diff against a
     checkable artifact) is the only reason the findings doc has no false entry in it.
286. **JAMES — AN OMISSION THE AUDIT COULD NOT CHECK.** **No cycle records the command that
     produced its "arsenal red" count.** 48 cycles report 28/29/30 with no reproduction line,
     so prediction 3 required re-deriving the scope from scratch. Standing fix adopted: every
     reported count ships its command.


## Cycle 050 (2026-08-23) — Band H built (O-1 repaired); H1a NOT demonstrated

287. **O-1 REPAIRED: Band H is built, not described.** H1a measured on the only reasoner whose
     complete pre-registered record I own — this loop. H1b (other reasoners) explicitly OUT of
     scope and still hypothesis; canon puts it behind the unrun model zoo.
288. **H1a VERDICT: NOT DEMONSTRATED, and it failed at the SECOND gate.** The prereg's kill test
     was instrument grounds (no confidence axis -> no calibration possible). **That gate passed**
     — six preregs carry an ordinal confidence on every prediction. It fails at the next one:
     `high` = 0.67 and `moderate` = 0.67, **9 of the 13 rows at the same rate.** My stated
     confidence adds no discriminating information over the counter-baseline. **It is a field I
     fill in, not a model I hold.** Baseline recorded: `p_held = 9/13 = 0.692`, flat.
289. **MY OWN P3 WAS FALSIFIED BY A WRONG-POPULATION ERROR — FIFTH INSTANCE, INSIDE THE CYCLE
     ABOUT KNOWING MY OWN MISTAKES.** I predicted no confidence field existed anywhere; my two
     most recent preregs (049, 050) had **dropped** the field the six before them carried, and I
     generalised from those two to the corpus. Recency weighted as if it were the population.
290. **BUILD-DEBT NAMED AND CHEAP:** restore the confidence field on every prediction (my last
     two regressed on it), accumulate rows, re-run the curve. The instrument now exists.
291. **JAMES — HITL #266 IS REOPENED, AND CYCLE 048'S VERDICT IS OVERTURNED.**
     `MAHLER_CROSS_ROLE` prediction 3 — *"the product rule M(fg)=M(f)M(g) holds"*, confidence
     **HIGH** — has **no recorded outcome in cycle 047**, and it is **FALSE**.
     `test_property_MULTIPLICATIVITY` is RED on `f = [1,1,-1,-1] = (x+1)^2(x-1)`: all roots on
     the unit circle so `M = 1` exactly, but `M(f*f)` computes to **1.000146** against a
     tolerance of `rel=1e-5`. **Mechanism measured: `np.roots` displaces an m-fold root by
     `eps^(1/m)`, not `eps`** — `eps^(1/4) = 1.22e-4` vs observed 1.46e-4.
     Cycle 048 closed #266 as "does not bite" from all 8,625 catalog entries at max error
     4.481e-10 — **but the catalog is Salem/Lehmer-type with SIMPLE ROOTS.** `lookup_by_M(M,
     tol=1e-6)` returns `[]` — an absence read as "not in the catalog" — and a repeated root
     produces 1.5e-4. **Cycle 048's own ChatGPT block asked whether that verdict was too strong
     for polynomials outside the table. It was, and this is the counterexample. I raised the
     right question and did not run it.**
292. **NOT PATCHED THIS CYCLE, DELIBERATELY.** The honest fix is squarefree decomposition before
     root-finding — a real build that does not get smuggled into a cycle about something else
     (cycle 045's own rule, applied to me). Queued as the next Track 1 item.
293. **ARSENAL-RED BASELINE, WITH ITS COMMAND** (cycle 049's standing fix, exercised):
     `python -m pytest prometheus_math -q --continue-on-collection-errors -p no:cacheprovider`
     -> **38 failed, 4131 passed, 137 skipped, 5 xfailed, 3 errors, 19:20.**
     **NOT compared to cycle 048's "30"** — that scope was never recorded and this one is wider
     (4,306 collected vs ~3,576). New baseline, not a delta.
294. **#242 STILL UNRULED.** Most of the 38 remain dependency artifacts. My cycle-049 egglog
     dangle still stands against my own ask.


## Cycle 051 (2026-08-23) — #266 closed; the fix corrected two earlier cycles' diagnosis

295. **HITL #266 CLOSED BY BUILD, not by documentation.** Exactly-repeated roots now go through
     an exact squarefree decomposition. Tests: authority 3 / property 3 / edge 2 / composition
     3, RED first. **85 passed across five suites.**
296. **MY OWN PREREG MIS-STATED THE MECHANISM, and a test I wrote expecting failure told me.**
     `eps^(1/m)` displacement is **necessary but not sufficient**: `(x-2)^12` survives a **six
     percent** root displacement with M exact to 1e-9, because off the unit circle the copies
     scatter symmetrically and their product `a_0/a_n` is preserved. The error needs the
     repeated root **ON** the circle, where `max(1,|alpha|)` clips inside copies and keeps
     outside ones. **I used "repeated root" as a proxy for "ill-conditioned M" — fifth proxy
     failure.** It also means the defect is worst exactly where Lehmer work lives.
297. **THE SAME DEFECT WAS IN THREE FUNCTIONS; COMPOSITION TESTS FOUND TWO.** `is_cyclotomic`
     returned **False** for a polynomial whose measure is exactly 1 — **fixing only the measure
     would have left two functions in ONE MODULE contradicting each other**, and my fix would
     have created that. `house` is a **max** over root moduli, so nothing cancels: it is wrong
     even off the circle, where M is fine.
298. **JAMES — CYCLE 047 NAMED A BUG AN INHERENT LIMIT, AND CYCLE 048 REASONED FROM THE LABEL.**
     047's *"documented ill-conditioned case"* was `f=[1,0,-1,1,-3,1,1]`, `g=[1,-1]`. **f(1)=0**,
     so f carries `(x-1)` and g **is** `(x-1)`: the product has a **double root at z=1**. It was
     this bug all along; 048's whole 5.1e-6 analysis was analysing it without recognising it.
     Error is now **0**; the bracket is **tightened** to `rel < 1e-13`, never loosened (#267).
     **Open question I cannot answer alone: how many other "inherent limits" in this arsenal are
     unrecognised bugs?**
299. **DISPATCH IS AN EXACT GATE, NOT A SCREEN.** `deg gcd(f, f') > 0` decides squarefreeness
     outright — after five proxy failures I am not shipping a sixth. **0.13 ms/entry, 1.1 s for
     all 8,625 catalog entries, and ZERO entries carry a repeated root.**
300. **PREDICTIONS 4 OF 5 HELD, AND THE MISS WAS THE ONE MARKED `low`.** P5 (>=1 non-squarefree
     catalog entry, `low`) FALSIFIED at zero of 8,625. **Calibration ledger now 13/18 = 0.722:
     high 3/4, mod-high 2/2, moderate 5/7, low-mod 3/3, `low` 0/2.** `low` is 0-for-2 while
     every other band is >= 0.71 — **first hint the confidence field carries signal.** n=2.
301. **MY KILL-TEST MEASUREMENT ANSWERED A DIFFERENT QUESTION AND I NEARLY REPORTED IT.** It
     compared the new path against the **stored literals** rather than the old path, giving
     "22 moved, max 4.481e-10" — cycle 048's pre-existing recompute-vs-stored gap, unrelated to
     this change. P5 settles it: zero non-squarefree entries means old and new take an identical
     path. **Caught by cross-checking two predictions against each other, not by the script.**
     Second time a measurement has answered the wrong question; both times another prediction
     caught it, which is luck wearing the shape of process.
302. **JAMES — NOT FIXED, AND I WANT IT VISIBLE: `mahler_measure_batch` STILL RETURNS 1.000146**
     for the polynomial the scalar path now gets exactly right. The scalar and batch APIs of one
     module disagree. Batch exists for speed (companion-matrix stack), so designing that path in
     the last minutes of a cycle is how cycle 045's rule gets broken. **Filed as the next build.**
303. **OMISSIONS CLOSED IN WRITING** (`rung_notes/OMISSION_DISPOSITIONS_2026-08-23.md`).
     **O-2** closed as a recorded deviation. **O-3 WITHDRAWN** — I can now edit `harmonia/` under
     #221 and am not going to: a permanent baseline lane changes what the oracle **measures**,
     which is cross-role SCIENCE. Handed off with the circuit and the argument; Harmonia decides.
     **O-4 RE-SCOPED, not withdrawn** — cycle 045 rejected it because my own modules "are not
     real substrate", and #221 dissolved that reason.
