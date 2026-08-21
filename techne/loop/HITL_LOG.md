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
