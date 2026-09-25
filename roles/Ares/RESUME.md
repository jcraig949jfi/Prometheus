# Ares -- RESUME (read this first after a context reset)

Currency: 2026-09-25. Written for a fresh session with zero memory of
this seat. Read RESPONSIBILITIES.md (the entry file) for the charter,
then this file for where the science actually stands. STATUS.md is the
one-screen state; TODO.md is the queue.

## 1. Boot exactly like this

    host M2 (SPECTREX5). Comms lives on M1 for every machine:
    export EW_DB_HOST=192.168.1.202     # BEFORE any comms call
    worktree:  D:\Prometheus-worktrees\ares-base-role
    branch:    ares/base-role-adopt-2026-09-19   (KEEP IT -- the
               operator asked for it to survive the reboot)
    In the canonical checkout (D:\Prometheus) run `git fetch origin`
    only. Never pull. The worktree guard must pass: git-dir
    (.git/worktrees/ares-base-role) != git-common-dir (.git).
    python -m comms boot Ares --model <id> --capabilities any
    python -m comms sync Ares

As of 2026-09-25 the branch is FULLY MERGED into origin/main (HEAD
81c062b40 was an ancestor of origin/main 5af9d08f5) and the tree is
clean. Nothing is mid-flight. No background job, no loop, no monitor:
Ares has never registered a row in roles/base-role/MONITORS.md and
should not start one without a decision.

## 2. What Ares is, in one sentence

Ares engineers PRESSURES, not architectures: it builds tiny worlds
that make some unknown machinery advantageous, evolves generic graph
organisms in them, and reports which pressures changed the KIND of
machinery that arose. Charter verbatim:
prompts/2026-09-19_charter/ (sha256 95a55073d40c...).

## 3. Seat state: PARKED, pending one operator decision

Two cycles are closed. Cycle 2 ended with the operator's mechanical
gate rule giving CONTINUE_RECOMMENDED (gates A and B open, C shut).
Per the directive that is a RECOMMENDATION ONLY; Ares does not
self-authorise a cycle 3. The seat is parked until the operator says
continue or close. The export package is already prepared and posted,
so closing costs the program nothing.

## 4. The science, compressed (full text: ares/ARES_CYCLE2_REPORT.md)

ESTABLISHED (preregistered, 10 seeds, results sit at the structural
cap so the held-out selection defect below cannot inflate them):
 - In world W4 (hidden regime: a 3-step cue, then identical
   observations, opposite correct actions, no reward channel) some
   cross-step carrier is always required: the no-carrier arm reaches
   2.30 of a 40.0 cap in 0/10.
 - THREE carriers are each individually sufficient. Alone, each
   reaches the cap: recurrence 10/10 (median 10 generations to
   threshold), plasticity 10/10 (17.5), keep 9/10 (30, tail to 90).
   With all three available the system runs at recurrence's pace (10).
   So recurrence's dominance is a SPEED phenomenon, not a capability
   one.
 - SUBSTITUTION IS REAL. Forbid recurrence outright and all 10
   lineages still reach the cap, with plasticity load-bearing 7/10 and
   keep 3/10, at a cost of about ten generations. A 0.25/edge tax also
   substitutes (median recurrent edges 2.0 -> 0.0).
 - Under the reset/interrupt world W15 the lineages build REDUNDANCY
   rather than substituting: recurrence load-bearing 8/10 AND
   plasticity 7/10, recurrent edges up from 2.0 to 9.0. Unexplained.
 - No carrier transfers. Edge-aware transplant portable 4/9; per-pair
   carrier swap between independently evolved lineages recovers >= 0.5
   in 16/59, median 0.02.
 - No unenumerated cross-step channel exists in this substrate (a
   champion above threshold with no carrier: 0 occurrences anywhere).

REFUTED (each killed by a specific measurement):
 - "Recurrence is intrinsically better": hand-built, the DESIGNATED
   carrier (keep) scores 33.75 against recurrence's 24.56 on W4.
 - "It pays off faster at first appearance": one mutation on a
   stripped champion, 300 times, 5 lineages -- mean effect ~0 and
   probability of immediate improvement 0.00 for BOTH carriers.
 - "It is simply more reachable": an 8x mutational subsidy on keep
   raised its creation rate 4.8x and did not flip the carrier.
 - "A USABLE one is more reachable" (the best version of that idea,
   and the one I believed): one mutation makes a usable recurrent edge
   with p=0.0173 and a usable keep with p=0.0000 (0 of 8000). So I
   widened the keep mutation step until usable-keep creation (0.0231)
   EXCEEDED recurrence's, recorded the prediction ">= 3/10 keep
   load-bearing" FIRST, and got 2/10. MY PREDICTION LOST. Reachability
   is necessary and not sufficient.

SUPPORTED BUT POST-HOC (do not build on this without test 6.1):
 - BASIN WIDTH. Sweeping each carrier's own parameter on hand-wired
   organisms: keep is viable (>= 50% of its best) in 3 of 25 swept
   values, only [0.94, 0.98], pressed against its clip ceiling;
   recurrence in 14 of 23, [2.75, 6.0], and SATURATING (4.0 -> 40,
   6.0 -> 40; larger is never worse). Corroborated unplanned by
   c2_recur_unstable: jittering every recurrent edge at every
   reproduction did not dislodge recurrence (7/10, and the fastest arm
   at 5 generations) -- jitter inside a flat basin is harmless.
 - The transferable statement: A SUPPLIED PRIMITIVE IS NOT "AVAILABLE"
   TO AN EVOLUTIONARY SEARCH BECAUSE IT EXISTS, WORKS AND IS REACHABLE
   IN ONE MUTATION. IT IS AVAILABLE WHEN ITS VIABLE REGION IS WIDE AND
   ITS GRADIENT FLAT.

## 5. Instrument defects -- do NOT re-introduce these

D1 THE REPORTED CHAMPION WAS SELECTED ON THE HELD-OUT SET.
   search.run picks the final champion by argmax over the whole final
   population evaluated on the held-out episodes, so
   run["final"]["heldout"] is a max-of-128 statistic. Use
   run["log"][-1]["champ_heldout"] (the training-selected champion,
   evaluated on held-out) for anything not at the cap.
   ares/recheck_c2.py does this. NOT YET FIXED IN search.run itself --
   fixing it is TODO ARES-C2-1 and should happen before any new
   campaign.
D2 A TRANSFER CLAIM IS SCORED PER ATTEMPT, NEVER BY THE BEST ATTEMPT
   (gate C was first printed OPEN on a best-of-9-donors statistic).
D3 NODE-ONLY ABLATION IS BLIND to output-node self-loops. Use
   ares/carriers.py (edge- and SCC-aware), never the old
   search.dissect node list, for any mechanism claim.
D4 A world's shuffled control must be balanced on EVERY hidden binary
   it draws, not just the first (search.balanced_seeds_for +
   world.balance_key).
All four are in roles/Ares/calibration/LEDGER.md with the evidence.

## 6. If the operator says CONTINUE: the decisive experiment, specified

6.1 DECOUPLE THE LOAD/HOLD TRADE-OFF (the real test of basin width).
    The keep basin is narrow because of the update rule itself:
        v_new = keep*v_old + (1 - keep)*f
    As keep approaches 1 the node holds well but the input term
    (1-keep) vanishes, so it can no longer LOAD the cue. One scalar
    must do both jobs, which is exactly why the viable region is a
    sliver. A self-loop has no such trade-off.
    ARM A (decoupled leak): change the rule to v_new = keep*v_old + f
    for the arm only, so holding and loading are independent, and
    re-run c1_all (W4, 10 fresh seeds, all carriers available).
    PREDICTION TO RECORD BEFORE RUNNING: keep becomes load-bearing in
    >= 5/10 and its time-to-threshold approaches recurrence's. If keep
    still loses with a wide basin, the basin explanation is WRONG and
    the cause is something not yet named.
    ARM B (control, re-parameterisation only): keep the same update
    rule but store and mutate r with keep = 1 - exp(-r), r in [0, 8],
    step N(0, 0.5). This moves where mutations LAND without widening
    the basin. PREDICTION: keep does NOT take over (this is the
    weaker test; the report's s7.1 originally proposed only this, and
    the 2026-09-25 annotation there records the sharpening).
    Running both separates "the basin was the problem" from "the
    parameterisation was the problem".
6.2 BASIN WIDTH AS A CROSS-PRIMITIVE PREDICTOR: measure the viable
    region of every primitive the substrate offers and test whether
    basin width predicts which one evolution selects. If it does, it
    is a design rule for the program, not a fact about this toy.
6.3 WHY REDUNDANCY UNDER ATTACK (W15). The only result nobody
    predicted. Untested.

## 7. Questions for the operator (re-ask these after bootstrapping)

Q1 CONTINUE OR CLOSE? Gates A and B opened, so by your rule Ares
   earned further work, but you hold the decision and said the seat
   should surrender compute to the next engine rather than become a
   permanent programme. If continue: cycle 3 should be ONLY test 6.1
   (two arms, ~20 runs, under an hour) and then stop again.
Q2 NYX / HARMONIA / THEOPHRASTUS HAVE NEVER REPLIED. Ares has posted
   seven messages (comms #518, #519, #535, #536, #538, #539, #540)
   across two cycles asking for anatomical interpretation of the W4
   carrier and offering the instrumentation for export. Zero replies;
   a scan of ids 536-566 shows nothing addressed to Ares. Do you want
   to relay by hand, should Ares stop sending, or should the export go
   to a different consumer?
Q3 EVIDENCE-WIKI SUBMISSION has been carried unfulfilled since cycle 0
   (ARES-25). Is it worth doing for a parked seat, or should the
   report plus the run receipts stand as the durable record?
Q4 IS THE BASIN RULE WORTH TESTING OUTSIDE ARES? It is the only result
   here that might generalise to other substrates in the programme. If
   you want it tested elsewhere, it needs a consumer seat with its own
   substrate, which is a cross-lane ask only you can make.

## 8. What a fresh session should NOT do

 - Do not start cycle 3, a sweep, or a loop without an operator
   decision (charter and both directives; the seat is parked).
 - Do not re-run cycle 0 or 1 conclusions as if fresh: cycle 1's
   "plasticity 0/10 on W4" DOES NOT REPLICATE (4/10 on fresh lineages
   with edge-aware attribution); the cycle-2 instrument is the one to
   trust.
 - Do not name an evolved structure after a known mechanism before its
   behaviour is described and its ablation run (charter anti-goal).
 - Do not delete another seat's branch or worktree.

## 9. Where everything is

    ares/ARES_PRESSURE_NOTES.md      P01-P18, citations FROM MEMORY
    ares/PRESSURE_CATALOG.json       12 built + 6 candidate pressures
    ares/substrate.py                the organism + carrier constraints
    ares/worlds.py                   16 batched worlds, 3 modes each
    ares/search.py                   GA, rollout, receipts (D1 lives here)
    ares/carriers.py                 edge/SCC-aware carrier instruments
    ares/DESIGN_C0/C1/C2.md          the three preregistrations
    ares/ARES_FIRST_REPORT.md        cycle 0
    ares/ARES_CYCLE1_REPORT.md       cycle 1
    ares/ARES_CYCLE2_REPORT.md       cycle 2 (current)
    ares/recheck_c2.py               D1/D2 repair + useful-opportunity
    ares/runs/sweep_c0|c1|c2/        receipts; c2 also gates.txt,
                                     recheck.json, basin.json
    ares/fossils/                    frozen organisms + replay
    roles/Ares/journal/              dated, what actually happened
    roles/Ares/calibration/LEDGER.md 10 rows of my own wrong calls
    roles/Ares/REVIEW_PACKET_C*.txt  the three external packets
    roles/Ares/prompts/              every operator directive verbatim
                                     with MANIFESTs
