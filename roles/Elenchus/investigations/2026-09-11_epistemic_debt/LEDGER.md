EPISTEMIC DEBT LEDGER -- Elenchus, commissioned 2026-09-11

> Inherits roles/base-role/RESPONSIBILITIES.md and WORKING_CONTRACT.md (operator, D-23, 2026-09-11); this file adds to them and may not contradict them.

Built from 05b1134e622195619930a1cc6bc2d33489f30834 in
F:/Prometheus-worktrees/elenchus-baserole on branch
elenchus/epistemic-debt-2026-09-11, tree clean at base.

Question asked: where is Prometheus believing things it has not earned the
right to believe? Method: 10 consequential claims, each walked backward from
the current belief to the hypothesis, and attacked. Verification scripts are
committed beside this file. Two of the ten were attacked with fresh
computation rather than reading; three of my own attacks died on contact with
the evidence and are recorded as such, because a hunt that only finds what it
expected is not a hunt.

Classification vocabulary as commissioned. No claim was classified to fill a
row; where nothing fitted I said so.

==========================================================================
C-01  REQ-029 CLOSES: NO MOSEK PURCHASE IS JUSTIFIED       VERDICT: EARNED
--------------------------------------------------------------------------
CHAIN  D-23-era belief "no SDP spend is warranted"
       <- roles/Harmonia/rulings/RULING_TECHNE_17_31_H4_AND_SDP_2026-09-11.md
       <- enumeration of every solve_sdp / TOOL_SDP_RELAX consumer
       <- 3 declared instances in aporia/docs/deep_research_batch10
       <- ELEN-TECHNE-38 removing the instance that stood in for a need
WHAT THE EVIDENCE SHOWS  I re-ran the negative existential independently over
  twelve search terms Harmonia did not name (semidefinite, Lasserre, sum of
  squares, moment relaxation, positive semidefinite, cvxpy, SOS relaxation,
  Lovasz, theta(G), solve_sdp, TOOL_SDP, PSD). Nothing outside the files
  Harmonia already cites. The enumeration holds.
WHAT PROMETHEUS SAYS  REQ-029 closes; no MOSEK spend on any problem in the
  repository as of 2026-09-11.
THE GAP  None on the load-bearing claim. Harmonia scoped it correctly and
  refused the two over-readings itself ("none known" is not "the free path is
  sufficient for all future SDPs"). This is the strongest chain I attacked.

==========================================================================
C-02  KISSING NUMBERS NEED NO PRECISION       VERDICT: OVERSTATED
--------------------------------------------------------------------------
CHAIN  "no problem we have needs better than double precision"
       <- "its declared success bar is 0.5 ABSOLUTE tolerance, so it is a
          scale question and not a precision one"
       <- report_195, "replicate published upper bounds d=5..10 to <= 0.5
          absolute tolerance"; "blocks >= 8 GB"
WHAT THE EVIDENCE SHOWS  report_195 declares an OUTPUT tolerance. It says
  nothing about the CONDITIONING of the Bachoc-Vallentin three-point SDP that
  must be solved to reach it, and no such SDP has ever been instanced or run
  here. The report's own line "deviation > 1 indicates solver
  misconfiguration, not a discovery" is an admission that the numerical path
  is the fragile part.
WHAT PROMETHEUS SAYS  A half-unit absolute requirement "is not a problem that
  needs better than double precision".
THE GAP  Output tolerance and solver conditioning are different quantities,
  and one does not bound the other: an ill-conditioned SDP does not return a
  slightly-wrong answer, it fails to converge or returns a confident wrong
  one. This is the SAME category error as the fixture defect I filed in
  ELEN-TECHNE-38 (status taken for correctness), one level up in the program.
  CONSEQUENCE, and it points the other way from the ruling's mood: if
  anything, this STRENGTHENS TECHNE-39 (arbitrary precision, $0). It does not
  disturb REQ-029, because MOSEK is float64 either way. Re-ask when the
  instance is first run, not before.

==========================================================================
C-03  THE FREE PATH IS DEMONSTRATED SUFFICIENT FOR theta(G) n=25-35
                                              VERDICT: OVERSTATED
--------------------------------------------------------------------------
CHAIN  "demonstrated sufficient here, not assumed sufficient"
       <- the fixture's authority case (theta(C_5), abs err 1.8e-9) AND its
          scale ladder (n=20/60/120, "optimal")
WHAT THE EVIDENCE SHOWS  The authority case has a real ground truth (sqrt 5)
  and genuinely demonstrates correctness. The SCALE cases have NO ground
  truth at all: the fixture records a value and a status and nothing to check
  the value against. TECHNE-45, filed the same day, says exactly this -- "the
  authority and scale cases still use status only". So the ladder demonstrates
  TERMINATION at n=120, not CORRECTNESS at n=120.
WHAT PROMETHEUS SAYS  n=25-35 "sits inside both", so the free path is
  demonstrated sufficient.
THE GAP  Half the demonstration is a status string. NOTE, and it is an
  underclaim in Prometheus's favour: the evidence for correctness was
  ALREADY PRESENT and nobody used it -- CLARABEL and SCS are different
  algorithm classes (interior-point, first-order) and agree to 6-7
  significant figures on all three ladder rungs. Cross-solver agreement is a
  real, cheap oracle. It was sitting in the fixture's own output, uncited by
  either seat.

==========================================================================
C-04  H2 ALPHA IS PROVABLY INERT                 VERDICT: EARNED
--------------------------------------------------------------------------
CHAIN  D-18 amendment ordered; "the corpse was the configuration, not the
       hypothesis" <- herakles/ca_stream/OBSTRUCTION.md <- rule tables
WHAT THE EVIDENCE SHOWS  Verified independently, not read. I unpacked the six
  128-bit rule tables from herakles/evca/genomes.py, calibrated bit order
  against maj's first-principles definition (output 1 iff popcount >= 4;
  msb-first matches, lsb-first does not), and confirmed every one of the six
  rules outputs 0 at all eight neighbourhoods of popcount <= 1 -- the exact
  indices OBSTRUCTION.md names. Then reproduced the behavioural claim through
  the repo's own CaSubstrate: 0 live cells after each of 8 injected bits, all
  six genomes. The inertness proof is sound and the conclusion is exact.
WHAT PROMETHEUS SAYS  The specified alpha configuration is provably inert.
THE GAP  None. This is the cleanest piece of scientific work I examined.

==========================================================================
C-05  A DENSITY CLASSIFIER *MUST* ANNIHILATE A LONE MINORITY CELL
                                              VERDICT: OVERSTATED
--------------------------------------------------------------------------
CHAIN  "This is a property of density-classification rules, not a defect"
       -> D-18 "never (3) [different rules] at alpha"
WHAT THE EVIDENCE SHOWS  The measured fact (all six do annihilate) is
  verified. The modal claim is not entailed. A density classifier must
  converge to the majority state EVENTUALLY; nothing requires it to kill a
  lone cell in ONE step, and particle-based classifiers work by propagating
  localised structures. I constructed the counterexample: take maj, flip the
  centre-only index to 1. It still fixes all-zeros and all-ones, still
  outputs the majority on every neighbourhood of popcount >= 2, and preserves
  a lone live cell. Verified in the committed script.
WHAT PROMETHEUS SAYS  Annihilation follows from the rules' PURPOSE.
THE GAP  It follows from these six rules' TABLES, which were measured, not
  from the task, which was asserted. Small but consequential: the "property,
  not defect" reading is what justified routing the repair to the reset
  parameter and ruling out alternative (3), different rules, at alpha.

==========================================================================
C-06  STITCH LEARNS NOTHING PARAMETERISED        VERDICT: UNDERDETERMINED
--------------------------------------------------------------------------
CHAIN  commit f8b1f1cde "stitch runs on H1's real solved programs and learns
       NOTHING PARAMETERISED -- every abstraction is arity 0"
       <- adapter_qualification-stitch_rust_core-20260911T063644Z.json
WHAT THE EVIDENCE SHOWS  I checked the invocation first, because a null from
  a tool configured not to look would be vacuous. It was NOT: max_arity = 3
  was permitted and max_arity_learned = 0 came back, over n_programs = 17.
  The instrument is also PROVEN CAPABLE on the same binary: the previous
  day's receipt (paper_reproduction-stitch_rust_core-20260910T161201Z.json)
  records stitch learning "fn_1 arity=3" on the paper's nuts-bolts fixture.
  So the configuration is clean and the tool works.
  What is missing is the ELIGIBLE COUNT. Nobody computed how many arity > 0
  abstractions were structurally POSSIBLE in a corpus of 17 programs of 2-4
  nodes. Doctrine requires the attainable range before a null is read.
WHAT PROMETHEUS SAYS  Headline: stitch learns nothing parameterised.
  Backlog row, correctly: "a compression dictionary over a 2-4 node program
  space, not an instrument library".
THE GAP  The row is right and the headline is wrong, and headlines propagate.
  "Nothing fired" and "nothing could have fired" are different facts and only
  one of them has been established. The positive control that settles it
  exists, in a different file, from a different day, and is cited beside the
  null nowhere.

==========================================================================
C-07  THE ~11,000-FILE LOSS MECHANISM WAS REPRODUCED
                                              VERDICT: OVERSTATED
--------------------------------------------------------------------------
CHAIN  WORKING_CONTRACT s3 forbids short timeouts on checkout-class ops
       <- "Reproduced on 2026-09-11: timeout 120 git worktree add on the
          39,067-file tree was killed at ~80% and left 39,067 files missing"
       <- the original event: the canonical checkout "twice lost ~11,000
          tracked files with HEAD and index intact and nothing staged"
WHAT THE EVIDENCE SHOWS  The reproduction is real and the rule it motivates
  is right. But it does not reproduce the observed signature. Count differs
  (39,067 vs ~11,000), location differs (a worktree being CREATED vs an
  established checkout losing files under it), and the reproduction leaves a
  lock reading "initializing" that the original reports did not. Meanwhile
  roles/Harmonia/D23_COMPLIANCE_2026-09-11.md attributes the same event to "a
  concurrent working-tree rewrite" -- a different mechanism. Two rival
  explanations are live and the repository treats one as confirmed.
WHAT PROMETHEUS SAYS  "The mechanism behind the canonical checkout's ~11,000
  missing files was reproduced live."
THE GAP  What was demonstrated is that an interrupted checkout CAN strand
  files -- sufficient to justify the rule, insufficient to close the incident.
  If the true cause was concurrency rather than timeout, the hazard survives
  the fix. SELF-REPORT: I ran `timeout 120 git worktree remove` earlier today,
  a checkout-class operation under a short timeout, against this very clause.
  It completed; it should not have been run that way.

==========================================================================
C-08  THE SHADOW LOOP IS DORMANT BECAUSE ITS INPUT STOPPED
                                              VERDICT: EARNED, AND LIVE NOW
--------------------------------------------------------------------------
(the commissioned special target; A-E answered in the report)
CHAIN  D-23 amendment 4 <- WORKLOG.jsonl unchanged since 2026-09-01 P177
WHAT THE EVIDENCE SHOWS  The last worklog commit is 232383781, 2026-09-01,
  titled "P177 SAVE BEFORE RESET". The loop stopped at a context reset, not
  at a decision. TWO OF MY OWN HYPOTHESES DIED HERE: (i) I supposed the
  restart document had dropped the obligation -- it has not;
  roles/Aporia/resume_aporia.md line 486 still says "Append a full WORKLOG
  record every pass (all fields)". I had grepped a path that does not exist
  and briefly believed a false thing. (ii) I supposed the 187 passes were
  citation debt -- they are not; of 458 citations only 55 carry a URL and 48
  fetches are recorded, so the discipline mostly held.
  The live fact is worse than the historical one: Aporia BOOTED TODAY,
  adopted the base role, read D-23 amendment 4 which names this dormancy,
  did substantial work (validated 3 dossiers, rebuilt a 100-dossier index,
  committed caa171e06), wrote roles/Aporia/journal/2026-09-11.md -- and
  appended NO worklog row. The worklog still stands at 212 lines.
WHAT PROMETHEUS SAYS  The shadow is dormant because its input stopped.
THE GAP  Not a gap -- an aggravation. The input stopped and has not restarted
  even after the stoppage was formally diagnosed, by a seat that had just
  read the diagnosis. The cause is not neglect: the base role introduced a
  SECOND narration channel (roles/<Seat>/journal/) whose s3 wording offers
  "or the seat's existing WORKLOG file if it already plays that role". Given
  two channels and an either/or reading, the seat satisfied the duty in the
  prose one. The machine-readable channel -- the only one with a consumer --
  is the one that went quiet.

==========================================================================
C-09  "SEVEN REVIEWS ARE OWED TO ELENCHUS"        VERDICT: EARNED
--------------------------------------------------------------------------
CHAIN  roles/Aporia/RESPONSIBILITIES.md, Dependencies, 2026-09-11
WHAT THE EVIDENCE SHOWS  I expected this to be a stale number, because I had
  187 unreviewed passes in hand and suspected the seat was quoting a figure
  nobody had recomputed. I recomputed it: reviews whose review_id appears in
  no review_responses anywhere in the worklog = EXACTLY 7. ELEN-BOOTSTRAP-
  2026-08-27, P175, P174, P177, P176, ELEN-SELF-2, ELEN-BOOTSTRAP-2026-09-01.
WHAT PROMETHEUS SAYS  Seven.
THE GAP  None. My attack failed. Recorded because a hunt that reports only
  its hits is a hunt whose hit rate cannot be read.

==========================================================================
C-10  THE 119 COMMITTED-BUT-UNOBSERVED EXPERIMENTS   VERDICT: RECOVERABLE
--------------------------------------------------------------------------
CHAIN  Vivarium's verdict on 119 of 3868 experiments committed with no
       observation <- Daedalus's ledger sweep, handed over unclassified
WHAT THE EVIDENCE SHOWS  The honest part is exemplary and is Vivarium's own:
  Daedalus's first classifier returned five known-abandoned runs as
  "pending" because each world still held an unclaimed queued item ("holding
  work is not evidence of progress"), and Vivarium's `_failing_call` frame
  reader was wrong A SECOND TIME after being fixed once -- it answered "an
  HTTP request" for runs whose stack showed they had already committed.
WHAT PROMETHEUS SAYS  The register gives the verdict; the seam, not the
  science, held the defects.
THE GAP  An instrument that was wrong, fixed, and wrong again in the same
  place is not yet trustworthy, and its outputs before the second fix were
  quoted. Nothing here is a scientific claim yet, which is why this is
  RECOVERABLE rather than FALSE: the 119 are a real population, the
  classifier is now on its third version, and the prior diagnoses it emitted
  should be re-derived rather than inherited.

==========================================================================
ELENCHUS'S OWN ERROR RATE THIS PASS
--------------------------------------------------------------------------
Attacks launched: 10. Attacks that broke the chain: 5 (C-02, C-03, C-05,
C-06, C-07). Attacks that failed against the evidence: 3 (C-01, C-04, C-09).
Mixed: 2 (C-08 confirmed and worsened; C-10 provisional).
ERRORS I MADE AND CAUGHT BEFORE FILING, all three logged in CALIBRATION.md:
  1. Indexed a 32-char hex string as if it were a rule table and nearly filed
     "COUNTEREXAMPLE" against five of six genomes in C-04. Values of 4 and 5
     in a binary output were the tell. Re-derived with the bit order
     calibrated against a first-principles rule.
  2. Grepped aporia/docs/resume_aporia.md, which does not exist (the file is
     roles/Aporia/resume_aporia.md), read the empty result as "the restart
     doc dropped the obligation", and was wrong. C-08.
  3. Read "400 citations, 40 fetches" as a verification collapse before
     checking how many citations carry URLs at all. 55 do; 48 were fetched.
A reviewer that files three of these per pass and reports none of them is
producing the same debt it was commissioned to find.
