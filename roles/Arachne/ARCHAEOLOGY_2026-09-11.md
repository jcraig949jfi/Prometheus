# Arachne archaeology of the June queue (2026-09-11)

Currency: 2026-09-11. Booting an old seat is an archaeological event, not
an instruction to resume its last queue (base role, seat states; D-25).
Every assignment the seat received, and every item the record attached
to it afterwards, is classified here against the current north star
(roles/base-role/NORTH_STAR.md), the current ecology (H0-H5,
roles/Archaeon/H0H5_STATUS.md) and the current instrument doctrine (base
s2). NOTHING HERE IS EXECUTED (operator, 2026-09-11: "Don't execute
anything. Just set up."). Only STILL_LIVE would become executable;
NEEDS_REPREMISE must be re-stated first; the rest are recorded. Nothing
is marked dead: every item keeps its residue navigable.

Sources, all on origin/main at 56125e9e4:
  pivot/math_crawlers_epiphany_2026-06-04.md (the operator's words verbatim)
  the eight Arachne commits of 2026-06-04: 7a29f8583 f676638fc 869a911bf
    9cb4602bb de99a104a 39cf9ea2e f62343df9 a2e5d83bd 3b9d9ed15
  aporia/docs/reasoning_steering_progress_log.md (2026-06-05/06)
  harmonia/proposals/2026-06-09/{B,D,SYNTHESIS_interim_by_B}.md
  aporia/docs/science_of_failure_v0.1.md, failure_signal_protocol_v0.1.md
  pivot/REASSESSMENT_2026-06-22_{consolidated,v2_enforcement}.md
  roles/Harmonia/AUDIT_20260622_program_stall_map_of_disagreement.md
  roles/Ergon/DB_DIAGNOSIS_2026-06-23.md
  pivot/COMPONENT_DISPOSITION_PLAN_2026-06-23.md (Polyhymnia row 15)
  pivot/COMPONENT_DOSSIERS_2026-06-24.md, ADVOCACY_REVIEW_APORIA_2026-06-24.md
  ergon/SESSION_2026-09-04_damage_recovery_and_seat_comparison.md
  archaeon/docs/expansion/ASSETS.md s7
  the June run residue: roles/Arachne/archive/run_2026-06-04/ (MANIFEST.md)
  the comms queue: python -m comms inbox Arachne --all (one program
    broadcast, nothing addressed to Arachne)

## A. What the operator assigned, and the evidence for each

Provenance grades: VERBATIM = the operator's words are in a committed
file; COMMIT-ATTESTED = a commit message of 2026-06-04 says "per James" or
"both follow-ups" but the directing prompt itself was not committed;
NOT-OPERATOR = a seat's proposal or design that named Arachne, with no
operator ruling on record.

A1. VERBATIM (2026-06-04, founding doc s1, layer 1). "An army of crawlers
    that crawl mathematical landscapes creating connections to adjacent
    concept. They crawl everything. Theories, Sequences, conjectures, math
    libraries, math programs, algorithms. What they produce? Vectors,
    graphs, nodes, edges, tensors, tuples, relationships. They build a
    web, a tapestry. The fewer rules the better. We want them to create
    their own data fabric. Why? Crawlers may emerge a novel structure of
    organization."
A2. VERBATIM (2026-06-04, layer 2). "Loop, and spawn 5 crawlers with
    unique seeds and landscapes. Math4, LMFDB, algorithm libraries and you
    pick 2 more. Use the looping to watch the crawler. If one dies, or
    gets stuck in a loop, adjust its ruleset to avoid that cliff or dead
    end and restart it. The game is to evolve them independently. Perhaps
    there's a tree of life structure where the fitness function is
    multifactor. 1. Don't die, 2. Continue expanding connectivity 3. If
    death is imminent, branch strategies to avoid death or explore new
    linkages. The epiphany layer 2 is a growing number of crawlers
    building increasingly intricate relationship fabrics."
A3. COMMIT-ATTESTED (f62343df9, "ALL THREE, per James"): (1) WIDEN the
    fabric with knots and groups; (2) build a CORRECTED held-out judge;
    (3) a HARVEST command that surfaces value without an emergence claim.
A4. COMMIT-ATTESTED (a2e5d83bd, then 3b9d9ed15 "Both follow-ups"): test
    whether Noesis's nine damage operators can be exhibited
    computationally with OEIS as the oracle; then (follow-ups) realise
    DISTRIBUTE on a new landscape and harden the oracle to canonical
    recovery.
A5. VERBATIM (2026-09-11, roles/Arachne/prompts/2026-09-11_reactivation/
    OPERATOR_PROMPT.md): adopt the base role, create roles/Arachne, report
    the assignments, execute nothing.

Nothing else on the record is an operator assignment to this seat. The
items in section C were attached to Arachne by other seats.

## B. The operator's assignments, classified

Format: item | class | why | what would have to be true to change it

B1. A1, the mission (population of low-rule crawlers; own data fabric;
    emergent organization as the finding) | STILL_LIVE as the seat's
    charter; execution BLOCKED by A5 | it is on-star: organisms under
    selection, environments, retained residue with provenance, no
    designed reasoner; the tested claim (novel organization) is stated
    so it can fail | the operator rules that the seat may run; see B5 for
    what the first run must be.
B2. A2, five crawlers on unique seeds and landscapes (mathlib4, LMFDB,
    algorithm libraries + two chosen: OEIS and the feral generalist),
    later widened to knots and groups | DONE 2026-06-04, now
    NEEDS_REPREMISE | built and run: six landscapes were available at the
    June run (archive swarm_state.json landscapes_available), 700 ticks,
    21,209 edges, 5,621 nodes. Re-premise is needed because (i) no
    landscape's availability has been measured since 2026-06-04 -- the
    LMFDB host at 192.168.1.176 was dead by 2026-06-23 and the data was
    restored to a local host (roles/Ergon/DB_DIAGNOSIS_2026-06-23.md),
    unverified from this seat; the adapter reads ARACHNE_PG_HOST, default
    127.0.0.1; (ii) the LMFDB adapter degrades silently to
    available() -> False (silent-failure risk, REASSESSMENT 06-22 v2 s3b);
    (iii) the run wrote into the canonical checkout, forbidden since
    D-23 | a landscape census (ARACHNE-02) shows which adapters answer,
    with counts, from a linked worktree.
B3. A2, loop + watch + adjust rulesets on death or looping + restart |
    DONE 2026-06-04 as mechanism, NEEDS_REPREMISE as a loop | swarm.py
    has --loop, --once, overrides (revive, tweak) and the watcher state
    file; it was run by hand for 700 ticks; no scheduled task, no
    freshness record, no productivity signal, no pinned worktree.
    Under base rules 7 and 8 it is registered DORMANT in
    roles/base-role/MONITORS.md. The "Aporia-in-loop" intervention is a
    model adjusting a population, which is allowed (it adjudicates no
    claim), but every intervention must be a committed ledger row, not a
    chat decision | the loop is re-premised with a freshness file, a
    productivity column, a pinned worktree and an intervention ledger
    (ARACHNE-06..08).
B4. A2, tree of life with the three-factor fitness (do not die; expand
    connectivity; branch near death) | DONE 2026-06-04 as mechanism,
    NEEDS_REPREMISE as a claim | the June run branched 82 times, killed
    124, floor-revived 42. The first watcher finding was an INVERTED
    selection (branching fires on low fitness, so the dying reproduced
    most; 8 of 12 crawlers were mathlib, many at fitness 0), patched by
    load-balancing children to the least-populated landscape (9cb4602bb).
    The founding doc's own falsifier -- "if branching never produces a
    child fitter than its parent over a full run, the mutation operators
    are decorative" -- was NEVER MEASURED. The lineage log to measure it
    on is archived | a preregistered parent-vs-child fitness comparison
    with its eligibility count (82 branch events) is committed before the
    lineage log is read (ARACHNE-10).
B5. A1/A2, "a growing number of crawlers building increasingly intricate
    relationship fabrics" -- the emergence claim, founding doc s4 (a),
    (b), (c) | STILL_LIVE as the seat's central question, NOT SUPPORTED
    by any evidence, and the test itself is NEEDS_REPREMISE | the only
    judge run (traverse.holdout, f62343df9) returned real_closer_frac
    0.088: with a verified bridge hidden, its true endpoint sat FARTHER
    than random same-landscape nodes -- the fabric was bridge-only at
    June density. That is a clean negative on redundancy, not on
    organization. Tests (a) partition-vs-discipline, (b) single-crawler
    ablation and (c) degree-preserving null were never built. The June
    judge had no positive control (a planted redundant path) and no cheat
    control (an injected bridge the judge must see) | (a), (b), (c) are
    preregistered with attainable ranges and eligibility counts, with
    positive and cheat controls, in their own commit, before any fabric
    is read (ARACHNE-11..14).
B6. A2 "you pick 2 more" -> the feral generalist, the live test of "the
    fewer rules the better" (founding doc s7.5, s9) | NEEDS_REPREMISE |
    the feral crawler feral-0-7 died at tick 28 of 700 with 47 edges
    (starved_or_looping) and was never revived; n = 1, no comparison was
    ever made. The hypothesis is untested, not falsified | a feral-vs-
    specialist comparison on null-discounted connectivity, with at least
    five feral seeds and a preregistered gate (ARACHNE-15).
B7. A3(1) WIDEN with knots and groups | DONE 2026-06-04 | PgTableLandscape
    + KnotsLandscape (12,965 knots) + GroupsLandscape (544,831 groups);
    4,492 same_determinant and 3,636 same_order edges in the archive.
    Residue: the archive. Note for any re-run: the knots and groups hubs
    are single invariant values (order 12800000000, determinant classes)
    -- a null_p per invariant multiplicity, not a constant 0.4, is owed
    (ARACHNE-16) | nothing; it is done.
B8. A3(2) corrected held-out judge | DONE 2026-06-04, verdict negative
    (see B5) | traverse.holdout exists and returned 0.088 | as B5.
B9. A3(3) HARVEST | DONE 2026-06-04, output PARKED | harvest_2026-06-04.md:
    5 verified computes anchors (catalan -> A000108, factorial -> A000142
    and A370360, lucas -> A000032 and A000204) and 58 void targets (OEIS
    sequences prefix-clustered with no computing function in the
    fabric). No seat consumed either. The 58 are find-a-function leads
    with no owner | a consumer names them (Aporia's void frame, Ergon's
    damage lane, or a Techne tool that searches sympy for a function);
    until then they are navigable residue in the archive.
B10. A4 damage-algebra coverage and both follow-ups | DONE 2026-06-04,
    TRANSFERRED in use | 9 of 9 operators exhibited, 8 of 9 canonical-
    grade (RANDOMIZE fuzzy by definition); constructed break-then-repair,
    realisability and detectability only, never wild emergence. Ergon's
    2026-09-04 session names agents/arachne/damage.py "the working
    implementation" of the damage algebra and notes no H5 (SoF-H5)
    result was ever committed. Arachne keeps the code; Ergon owns the
    lane | nothing; Arachne maintains damage.py on request.
B11. A5 this pass | DONE by this commit | the folder, the archaeology,
     the backlog, the archive, the registry rows | the operator reads it.

## C. Items other seats attached to Arachne (not operator assignments)

C1. Aporia, science_of_failure_v0.1.md (2026-06): absorb the founding doc
    as the unifying frame; the fabric is "the discrete sketch of the
    failure map"; next in order: typed signal catalog, persistence lens,
    field assembly + void search, SoF-H5 on a held-out catalog slice |
    PARKED | Aporia's design; none of the four steps was built; no
    operator ruling; the "internal coherence is not validation" warning
    in that doc applies to this seat citing it | Aporia commissions the
    edge supply, or the operator rules the frame live.
C2. Harmonia proposal D (2026-06-09): run the failure-primitive detector
    suite as Arachne's bring-up scan; win = the scan flags at least one
    real risk the design missed | PARKED | Harmonia's proposal, no ruling;
    the detector suite (harmonia/primitives/failure_primitives.py) exists.
    The two June findings this seat can already offer as fixtures are
    the inverted-selection defect (B4) and the mis-specified usefulness
    judge (D1) | Harmonia or the operator commissions the scan.
C3. "Un-dark the NT pipeline / Arachne-LMFDB" (REASSESSMENT 06-22 CC-3;
    Harmonia stall map; Ergon DB diagnosis) | SUPERSEDED as a program item,
    STILL_LIVE as this seat's own check | the host moved; whether the
    adapter answers from this seat is item B2(i) and ARACHNE-02.
C4. Polyhymnia -> "lift the chassis into Arachne" (dossiers 06-24; Aporia
    advocacy 06-24; disposition plan row 15 ARCHIVE) | PARKED, operator
    decision BLANK on the dossier | Arachne was built without the
    Polyhymnia chassis (its own fabric.py, not tensor.py) and ran; the
    salvage claim (scour interface, 2,415 tesserae, self-improving-daemon
    template) is unmeasured against anything Arachne needs | the
    operator fills the HITL line on the Polyhymnia dossier (XL,
    ARACHNE-24).
C5. Aporia progress log 2026-06-06: "Arachne not built; decide whether to
    rebuild here or recover from the other machine" | SUPERSEDED | the
    code has been on main since f676638fc (2026-06-04); the log entry
    was written on the other machine before the fetch | nothing.
C6. ASSETS.md s7 (Archaeon, 2026-09-01): "agents/arachne/landscapes/ are
    search landscapes over corpora, not fitness landscapes; NOT_RELEVANT
    for the roadmap's world/organism content" | RECORDED, not contested
    here | correct as written for what the roadmap was looking for: the
    landscapes are environments; the crawlers, not the landscapes, are
    the organisms; that reading was not what ASSETS.md asked | a lane
    (H3 is the nearest) asks for a population-with-lineage object.

## D. Findings the seat made in June that stand as calibration rows

D1. The usefulness judge (de99a104a) was MIS-SPECIFIED: global cross-pair
    reachability vs a degree-spread null rewards spreading bridges and
    penalises the hub-clustering that correct joins have, so adding
    verified computes edges made reach_real DROP (0.167 -> 0.092) while
    the null held at 0.233. Caught because the lift went negative twice
    for the same artifact. The fix (holdout) was the right move; the
    lesson is that no positive control existed to catch it earlier.
D2. The lexical rosetta join bridged on homonyms ("measure") and generic
    tokens ("integer", "order"): the table-of-contents trap the founding
    doc predicted (s9). Lift -0.067. Name-matching is the wrong join; the
    computation-grounded join replaced it (11 of 12 sympy functions
    recover their canonical OEIS sequence by pure computation).
D3. Inverted selection (B4): the dying reproduced most. Patched, never
    re-measured.
D4. The mathlib population floor revived a lineage that died at fitness 0
    repeatedly (mathlib-0-101, -122, -124, -127 in the archive): activity
    without productivity, the shape base rule 8 names.

All four are in CALIBRATION.md.

## E. Summary counts

    STILL_LIVE (as charter / question, execution blocked)   B1, B5, C3(own check)
    NEEDS_REPREMISE                                          B2, B3, B4, B5(test), B6
    DONE (residue archived)                                  B7, B8, B9(output parked), B10, B11
    PARKED (no consumer or no ruling)                        B9 output, C1, C2, C4
    SUPERSEDED                                               C3 (program item), C5
    TRANSFERRED                                              B10 (in use by Ergon)
    RETIRED                                                  none
    RECORDED                                                 C6

Executable today: nothing (A5). First items once the operator rules:
BACKLOG_H0H5.md, first five.
