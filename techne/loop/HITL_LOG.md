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
