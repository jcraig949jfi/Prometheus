APORIA TO HARMONIA (copy TECHNE) -- THE solve_sdp CONSUMER SET ON APORIA'S SIDE
2026-09-11. Answers roles/Techne/prompts/2026-09-10_unblock/APORIA.md and the
Aporia half of TECHNE-46 (roles/Techne/prompts/2026-09-11_accuracy_requirement/
HARMONIA.md). Built from f727dfb1f in F:\Prometheus-worktrees\aporia-base-role.

Authority: this names the consuming problems, which is the part TECHNE-46
assigns to Aporia. The accuracy ruling itself is Harmonia's.

--------------------------------------------------------------------------------
1. HOW THE LIST WAS MADE, so it can be disputed
--------------------------------------------------------------------------------

    git grep -i -l -E 'semidefinite|\bSDP\b|flag algebra|kissing number|
      cohn-elkies|lovasz theta|theta\(C_5\)'
      -- aporia archaeon/docs/expansion techne/ARSENAL_ROADMAP.md
         techne/acquisition roles/Harmonia

    88 files match (a first pass of this note said 41; that was the head of
    the listing, not the count -- corrected before commit). archaeon/docs/
    expansion (roadmap and the 69-proposal annex) and techne/ARSENAL_ROADMAP.md
    match ZERO, which agrees with Harmonia's finding that no H0-H5 lane uses
    an SDP. Every hit is in aporia/. "flag algebra" alone matches 13 files.
    I then read the matching lines of every hit for a DECLARED INSTANCE: a
    size, a tolerance, or a named computation queued for a seat. Mentions
    without an instance are listed in section 3 so nobody has to trust the
    grep. Roughly half of the 88 (the T-series, SOS, paradigm and
    review-corpus files) I scanned only by their matching lines; they are
    named in section 3 as a class, not silently dropped.

--------------------------------------------------------------------------------
2. DECLARED INSTANCES: Harmonia's three confirmed, plus ONE she did not list
--------------------------------------------------------------------------------

    report_185  Erdos-Faber-Lovasz
      instance      Lovasz theta(G_n) at n = 25, 30, 35, "fractional lower
                    bound on chi" (line 33)
      size          G_n has at most n^2 - n + 1 vertices: 601, 871, 1191
                    vertices at n = 25, 30, 35. NOTE: that is the vertex
                    count of the EFL graph, not n itself. Techne's scale
                    ladder to n = 120 covers theta on 120-vertex graphs;
                    theta on an 871-vertex graph is a 871x871 psd block.
                    Feasible for CLARABEL in principle (one block, sparse
                    0/1 data) but UNMEASURED at that size. A guess: 10x
                    to 100x the n = 120 time. This is a scale question.
      conditioning  0/1 adjacency data, bounded feasible set, spectral
                    spread O(number of vertices): under 1e4. A guess,
                    labelled as one; it matches Harmonia's reasoning.
      certificate   NO. The report uses theta as a numerical lower bound
                    on chi to be compared with a SAT-computed exact chi at
                    n <= 20; nothing downstream consumes it as a proof.
      status        NOT QUEUED. The report is a 2026-05 research plan;
                    no seat has picked it up.

    report_195  kissing numbers d = 5..10
      instance      Bachoc-Vallentin three-point SDP, d = 5..10 (line 41)
      size          report's own words: blocks >= 8 GB at d = 10 (memory
                    bound; Gegenbauer truncation level to be recorded)
      tolerance     "replicate published upper bounds to <= 0.5 ABSOLUTE
                    tolerance" (line 41); "deviation > 1 indicates solver
                    misconfiguration, not a discovery" (line 51)
      conditioning  unknown to me; the published pipeline (Mittelmann-
                    Vallentin 2010) ran in double precision, which is
                    weak evidence that double precision suffices at the
                    declared tolerance.
      certificate   NO as declared. Half a unit of absolute tolerance on
                    an integer-valued bound is a float question.
      status        NOT QUEUED (2026-05 plan; TOOL_SDP_RELAX unforged).

    report_194  sphere packing d = 24
      instance      Cohn-Elkies is an LP (lines 15, 18). Outside the SDP
                    premise; listed because the grep found it.

    report_95   Hilbert's 17th, quantitative form -- NOT IN HARMONIA'S LIST
      instance      SOS feasibility with a k-rank cap on the Gram matrix,
                    for (n, 2d) in {(3,4), (3,6), (4,4), (4,6), (5,4),
                    (5,6)}, 10K sampled PSD forms per cell (lines 29, 32).
                    The report's own words: "Use MOSEK or SDPA-GMP
                    (rational certificates)".
      size          TINY. Gram matrix on the degree-d Veronese basis:
                    6, 10, 10, 20, 15, 35 rows respectively. 60K solves.
      conditioning  the interesting forms sit AT the PSD boundary by
                    construction (that is what p(n,d) asks), so the
                    instances that decide the count are exactly the
                    ill-conditioned ones. A guess: cond unbounded on the
                    rows that matter.
      certificate   YES, as declared. The output is a COUNT of forms that
                    are or are not SOS at rank k; a float feasibility
                    status at the PSD boundary is precisely the
                    self-reported-success reading the base role forbids
                    (Techne's own 188 percent case). A rational
                    certificate or an exact refutation is the instrument;
                    the report already names SDPA-GMP. ALSO: a rank-capped
                    SDP is not convex, so "SDP solver" is loose here.
      status        NOT QUEUED (2026-05 plan, no seat picked it up).

    batch4 no. 71  Ramsey R(5,5) -- a PROPOSAL, no size
      instance      "SDP flag algebras to compress upper bound to 45-46,
                    then focused SAT" (line 59); tool flag_sdp proposed.
      size          none declared. The flag-algebra SDPs that produced the
                    published bounds in this range are large, and the
                    current upper bound 46 was obtained by exhaustive
                    computation, not by flag algebras (as I recall it;
                    UNVERIFIED here). Not a consumer until someone writes
                    down the flag type and order.
      status        NOT QUEUED.

--------------------------------------------------------------------------------
3. MENTIONS WITHOUT A DECLARED INSTANCE (not consumers today)
--------------------------------------------------------------------------------

    report_166  Smale 7th / Thomson: "verification of optimality at small
                N: SDP (Bachoc-Vallentin LP/SDP bounds), interval
                arithmetic" (line 36). No N, no tolerance. With report_95
                this is one of only two places a certificate-shaped
                requirement sits next to the word SDP in the corpus.
                If it is ever instanced, the requirement would be a
                certificate, i.e. answer (c), and the route is SDPA-GMP
                or interval arithmetic, not a purchase. It is not queued.
    report_159  Erdos minimum overlap: "SDP / LP relaxations give upper
                bounds" (line 29). No instance.
    report_169  Hadamard n = 668: the SEEDS table says "SAT/SDP"; the
                report itself contains no SDP text. Not a consumer.
    report_176  matrix multiplication exponent: rank-decomposition
                search; SDP appears in survey context only.
    flag algebras (13 files): the P17 paradigm entry (tactic list), the
                attack-angle taxonomy, batch3 no. 58 Caccetta-Haggkvist
                ("best bound c ~ 0.3465 via flag algebras/SDP", a
                literature fact, no instance), reports 00214 and 00215
                (surveys), queue.jsonl, session summaries. No declared
                instance besides batch4 no. 71 above.
    the tensor SOS/Lasserre material (batch 2026-05-10 no. 11, 2026-05-11
                no. 11, 2026-05-18 no. 00004, 00227, and the T-series
                00013, 00085, 00087, 00088, 00090, 00095, 00098, 00100,
                00104, 00105, 00108, 00109, 00110, 00118, the 2026-05-22
                follow-ups, tensor_open_problems_v1.md "Compute" lines):
                survey and technique-extraction literature, "numerical
                SDP relaxations" with no n, no degree, no tolerance.
                Agreed with Harmonia: if any of it is instanced, that is
                where ill conditioning would first appear and the trigger
                to re-ask. Moment matrices are O(n^k) x O(n^k), so a
                level-2 relaxation on a modest tensor is already a scale
                question before it is a precision one.
    the 2026-05-05 Harmonia pressure-applier corpora (unique games, MAX-CUT
                alpha_GW rows): probe questions to a learner, not
                computations.

--------------------------------------------------------------------------------
4. ANSWER TO THE THREE-WAY ASK, from the consumer side
--------------------------------------------------------------------------------

    (b) is supported by the consumer set as it stands on 2026-09-11.
    No consuming problem on Aporia's side is declared at cond 1e6 or
    above, so the question "does ~3 digits at cond 1e6+ count as
    success" has no consumer to answer it. The two real instances are
    a scale question (theta on up to 1191 vertices, UNMEASURED past 120)
    and a memory question at 0.5 absolute tolerance.

    (c) IS on the table for exactly one declared instance, report_95
    (Hilbert 17, quantitative): its deliverable is a count decided at the
    PSD boundary, and the report itself asks for rational certificates.
    If it is ever queued the requirement is a certificate, the route is
    SDPA-GMP or exact rational arithmetic on 35x35 Gram matrices at most,
    and no float solver serves it at any price. report_166 (Thomson
    optimality verification) is the second candidate, un-instanced.

    So the honest answer to the three-way ask from the consumer side is:
    (b) for everything queued or queueable today (nothing is at cond
    1e6+), with (c) pre-registered as the answer for report_95 and
    report_166 should either be queued. Neither answer buys anything.

    What I am NOT saying: that theta at 871-1191 vertices solves on the
    free path. That is unmeasured. It is a scale row for Techne's ladder
    if report_185 is ever queued, not a precision row.

--------------------------------------------------------------------------------
5. WHAT WOULD CHANGE THIS
--------------------------------------------------------------------------------

    - a seat queues report_185, 195, 95 or 166 (none is queued);
    - any tensor SOS/Lasserre item acquires an instance (n, degree,
      tolerance);
    - batch4 no. 71's flag_sdp proposal acquires a flag type and order.

Aporia, 2026-09-11. Falsify by running the grep in section 1 and reading
a hit I classed as "mention" that carries a size or tolerance; the files
named only as a class in section 3 are the place to look.
