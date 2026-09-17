+==============================================================================+
|  REVIEW PACKET -- ATLAS PASS 01, STAGE A COMPLETE ON THE n=30 SAMPLE         |
|  Author: Nyx (Custodian of the Chop Shop), instance m2-0c0adfe1, M2          |
|  Date: 2026-09-16      Status: FIRST-PASS RETURN FILED; NOTHING RAN          |
|  For: HITL (operator) + external reviewers                                   |
|  Self-contained: every load-bearing number is inline; no repo access needed  |
+==============================================================================+

0. SUMMARY / MANDATE / VERDICT
------------------------------------------------------------------------------
Mandate (operator charter 2026-09-13, "ATLAS PASS 01"): turn Techne's vault of
~109 (now 121) preserved human programs into an ATLAS OF COMPUTATIONAL
BEHAVIOR: per fossil, a whole-system record, a machinery tree of ORGANs cut
below the famous names, REJECTED cuts, PRESSUREs stated without the organ,
composition edges, ancestry edges, residue; then ablations, fingerprints,
recurrence tests, blind cuts. Staged: A census + coarse cuts, B deeper, C
ablations, D fingerprints, E recurrence.

What this session did: Stage A on the whole pre-registered stratified sample
(30 of 121 fossils, seed 20260913, drawn 2026-09-13 before any body was
opened). 25 fossils were cut today, 5 on 09-13/14. Bodies were re-fetched on
a second machine (M2) with Techne's own tool and checked against Techne's
committed tree hashes: 30/30 present, 28 byte-exact, 2 explained (below).

Verdict I am asking the reviewer to test: the atlas now has a READ layer
(224 fragments, 192 accepted on source reading) and NO MEASURED layer (0
fingerprints, 0 blind cuts, 0 measured coverage cells). My recommendation is
to STOP cutting and start running (Stage C on six ready ablations) before
touching the 91 uncut fossils. A reviewer who thinks 30 read cuts is too thin
a base for Stage C, or too thick a base to trust without a blind check, has a
real case; both are argued in section 9.

1. WHAT WAS BUILT (and what existed before measurement)
------------------------------------------------------------------------------
Before this session (committed 09-13/14): schema nyx.atlas/0 (one JSON per
fossil; validator accepts UNKNOWN, rejects invented vocabulary), census of 121
whole-system records from Techne's record.json only, the 30-fossil sample, 5
deep cuts (glibc rwlock 9 organs, SPIN Pathfinder 2, zchaff 11, DES 4,
EISPACK 9), 1 ablation with 1 vacuous-indicator control.

This session (all on origin/main, final SHA cd3d6fe85):
  - nyx/atlas/samples/stageA_bodies_m2_2026-09-16.json  bodies receipt
  - nyx/atlas/cuts/<25 scripts>.py -> nyx/atlas/fossils/<25>.json
  - nyx/atlas/build.py  assembles the charter's eleven artifacts by projection
    (no hand-typed counts) into nyx/atlas/out/
  - nyx/atlas/recurrence/stageA_reading_candidates_2026-09-16.json
  - nyx/atlas/FIRST_PASS_RETURN_2026-09-16.md  (the charter's 10 sections)
  - census.py: Techne's 'superseded' relation marked direction-UNFIXED
  - delivery: comms #296 to Techne (offline at post time; queued)

Pre-registration status: the sample and its order were fixed on 09-13. The
organ vocabulary (coverage dimensions, rejection reasons, edge labels) was
fixed on 09-13. Nothing in the cut format changed today.

2. THE CLAIM AND WHY IT MATTERS
------------------------------------------------------------------------------
Claim (Stage A, reading only): for each of 30 human programs across 5 decades
and 20+ human domains, the machinery decomposes into a small number of
mechanisms with named input/output/state/update and a source boundary, and
the human package name is never one of them.

Why it matters for Prometheus: the program's north star is to grow, not
design, computational machinery. The atlas is the reference against which an
organism nobody designed can later be asked "have we seen behaviour like this
before?" -- and the charter forbids answering that by reading names. A READ
layer is the index for that; only a MEASURED layer can answer it. This
packet reports the index and says plainly that the answer-layer is empty.

3. DESIGN AS EXECUTED
------------------------------------------------------------------------------
Per fossil: `python -m nyx.atlas.author show <id>` (entry points from
Techne's record, file census of the body), then read the source with grep and
sed at the entry points, then write a cut script declaring organs (15 charter
fields + coverage cells + evidence ref as vault:<id>/<file>:<lines>),
rejected cuts with a reason from the fixed list, pressures (12 fields), edges
from the provisional 15-label list, ancestry edges, residue state. The script
IS the ledger; running it validates and writes the JSON. Every save re-ran
the validator over all 121 files (0 problems each time).

Grain: COARSE = subsystems and their first-level mechanisms with the entry
functions read; DEEP = every line of the body assigned (only small bodies:
rr-arbiter 219 lines, hopfield 60, tiny-aes 572, rs-1991 406, plus the 5
prior). Organ status ACCEPTED requires the boundary to have been read;
CANDIDATE = signature / name only (32 of 224).

Evidence discipline: evidence.grade per organ. SOURCE_READ 217, METADATA 4,
EXECUTED 1, INTERVENED 2 (the last three from 09-14). No organ ran today.

4. BODIES ON A SECOND HOST (the one measurement this session made)
------------------------------------------------------------------------------
Techne's vault is host-local; M2 had none. Re-fetch with Techne's
`harvest acquire`, revert Techne's tracked records after each fetch, compare
against the COMMITTED tree hash:

    fossils fetched               30/30
    tree hash matches             28
    differs                        2
      libfec-karn        127/127 files match after LF->CRLF; 0 otherwise
      corewar-redcode    31 exact, 15 match after LF->CRLF,
                         4 MISSING = tree/**/__pycache__/*.pyc

Reading: Techne's recorded hashes for git-pinned bodies are of a CRLF
checkout (harvesting host core.autocrlf=true); and one body's "immutable"
upstream tree had Python build products inside it when hashed. Source bytes
are identical modulo line endings, sufficient for reading, not for byte-level
replay. Reported to Techne (return 9a). Nyx did not edit Techne's records.

5. RESULTS (exact numbers; from nyx/atlas/out/DEPTH_MAP.json)
------------------------------------------------------------------------------
    fossils available / inspected / decomposed   121 / 30 / 30
    ORGAN0 / blocked                             0 / 0
    cut states                                   COARSE 21, DEEP 9, NOT_CUT 91
    candidate fragments                          224
    accepted / candidate organs                  192 / 32
    rejected cuts                                121
      OTHER 38, NAME_HAS_NO_EXECUTABLE_BOUNDARY 26, GENERIC_LANGUAGE 25,
      EFFECT_FROM_ENVIRONMENT 18, INHERITED_FROM_LIBRARY 5, BELOW_GRAIN 5,
      STATE_IRRELEVANT 2, CANNOT_ISOLATE 2
    max depth per fossil                         1: 17, 2: 10, 3: 3
    organs per fossil                            2..15, median 7
    pressures                                    69 (1..4 per fossil)
    composition edges                            298 (feeds 145, updates 35,
                                                 gates 27, triggers 17,
                                                 competes 14, selects 13,
                                                 stores 12, ...)
    ancestry edges                               130 (superseded 20 --
                                                 direction UNFIXED, see 6b)
    residue                                      EXPLAINED 9, PARTIAL 16,
                                                 LARGE 4, INSTRUMENT_
                                                 INSUFFICIENT 1 (sqlite)
    recurrence candidates (reading)              15: R0 4, R1 8, R2 3, R3+ 0
    fingerprints / blind cuts / measured cells   0 / 0 / 0

Two calibration pairs are planted in the recurrence file for Stage E: RC-01
(Rockliff 1991 RS -> Karn's RS: known identical by descent; an instrument
that does not score it R5 is broken) and RC-15 (two arbiter circuits the
author claims equivalent; 64 exhaustive cases decide it).

The strongest cross-domain candidate by reading, RC-05: LMDB's txnid-keyed
freelist, Concurrency Kit's epoch reclamation, LevelDB's version refcounts
and SQLite's WAL read marks all gate reclamation on the oldest live reader
and all stall under one stuck reader. Two human domains, no shared code.

6. INCIDENTS / DEFECTS FOUND (and what they validated)
------------------------------------------------------------------------------
6a. Hash portability defect (section 4): the "tree hash lets any machine
    confirm the same bytes" claim in Techne's README fails for 2 of 30
    bodies. Validated the value of re-fetching on a second host before
    trusting a freeze record.
6b. Techne's 'superseded' lineage edge has no fixed direction: 17 edges
    read; "bsd-tcp-4.2 superseded tahoe" means BY, "linux-tcp superseded
    Reno" means the reverse; sometimes the note says "direction: ...". The
    census had projected it as directed. Fixed on Nyx's side (labelled
    UNFIXED, note carried); the ancestry graph cannot be walked until the
    vocabulary is fixed on Techne's side.
6c. One record packs two whole systems (linux-tcp-congestion: CUBIC and
    BBR). Cut as two subsystems with an intra-record rival_of edge.
6d. des-reference's record calls its oracle a known-answer test; the recipe
    runs a round trip (any invertible transform passes). tiny-aes-c's
    shipped test IS a known-answer test. Recorded as a rejected cut with a
    TECHNE FEEDBACK note.
6e. Nyx's own: 12 of 69 pressure cost_class fields are free text where the
    charter allows three classes. Not rewritten; backlog NYX-47. The five
    09-13 cut scripts carry F:/ drive paths (contract s9); backlog NYX-48.
6f. Base-role self-test on M2: 1 RED (a scheduled task VivariumConsumerM2
    with no registry row) -- not Nyx's lane, already reported by Herakles
    in de6adc493 the same morning. nyx/tests 21/21 green.
6g. Depth was a function of body size, not machinery: the two largest
    bodies (sqlite 261k lines, tinycc 27k) got the shallowest cuts; the two
    smallest got complete ones. The cut instrument (one reader, one session)
    is the bottleneck. sqlite is recorded CUT_INSTRUMENT_INSUFFICIENT.

7. WHAT THIS DOES AND DOES NOT ESTABLISH
------------------------------------------------------------------------------
Establishes (at SOURCE_READ grade): that 30 bodies admit a decomposition
into named mechanisms with source boundaries; that every one of them rejects
its package name as an organ; that five pressure TEST SETS can be stated
across domains; that two bodies' identities are negative anatomy (tinycc: no
IR; python-control: no numerics).

Does NOT establish: that any organ boundary survives an intervention (0
ablations today); that any recurrence candidate is above R2; that the reader
is not importing ancestry into the cut (0 blind cuts -- and I chose organ
names to line up across known-related fossils, which is exactly the bias a
blind cut tests); that the coverage map's READ cells mean anything measured
(all 19 dimensions have measured == 0).

Claim ceiling: an index. Conditional on: one reader; no second Chopper; no
consumer has returned anything on any atlas organ.

8. DECISION / RECOMMENDATION
------------------------------------------------------------------------------
HITL's call. Nyx's lean: do NOT continue Stage A on the 91 NOT_CUT fossils
next. Run Stage C on the six ablations that need no new code, all CPU-scale,
all in Techne's existing containers:
  1. gzip: the -1..-9 level table (4 numbers, no mechanism change) ->
     ratio and wall time per level; positive control level 0; cheat control
     a pre-compressed input must show no gain.
  2. minisom: kernel radius -> quantisation vs topographic error.
  3. hopfield: pattern count past 0.14 N; the synchronous 2-cycle claim.
  4. rr-arbiter: 64 exhaustive cases across the two circuits (iverilog).
  5. reed-solomon-1991: tt+1 errors -> silent pass-through or not.
  6. aes/des: round-count sweep -> avalanche.
Then a blind cut of the two smallest fossils by a second session.
Stage A resumes only if Stage C shows the read cuts are worth extending.

The retirement option is real: if Stage C shows read boundaries do not
predict ablation outcomes (say, fewer than 4 of 6 ablations move what the
cut says they move), the read layer is decorative and the atlas should be
rebuilt from measurements outward, discarding this pass.

9. QUESTIONS FOR THE REVIEWER (written to resist agreement)
------------------------------------------------------------------------------
Q1. Is 30 read cuts too thin a base for Stage C -- should the sample be
    extended before running anything, on the argument that ablations only
    tell you about the organs you already named?
Q2. Or is it too thick to trust: should the blind cut come BEFORE Stage C,
    since ablating a biased boundary measures the bias, not the machinery?
Q3. The 'human package name is never an organ' result is 30/30. Is that a
    finding, or an artifact of the charter instructing me to cut below
    names (a rule cannot discover what it presupposes)?
Q4. RC-05 (reclaim-under-live-readers, 4 fossils) is my best cross-domain
    candidate. Name the intervention that would show it is NOT one
    mechanism. If none can be named, the candidate is unfalsifiable and
    should be demoted.
Q5. Coverage cells are 224 x 19 opinions of one reader. Should the map be
    published at all before a measured cell exists, given the base-role
    warning that green-for-the-wrong-reason instruments are this program's
    graveyard?
Q6. The two hash mismatches: sufficient for reading. Are they sufficient for
    the atlas to cite Techne's hashes as provenance at all, or must every
    evidence ref carry the hash of the file actually read on this host?
Q7. Not worth continuing? State the version of "stop" you would sign.

10. ARTIFACTS
------------------------------------------------------------------------------
    origin/main                         cd3d6fe85 (verified ancestor)
    commits (this session)              a98614f92, 9119205ef, 5 more cut
                                        batches, aca5cf4c6 (return), then
                                        two explicit merges and a delivery
                                        commit; final cd3d6fe85
    return                              nyx/atlas/FIRST_PASS_RETURN_2026-09-16.md
    artifacts                           nyx/atlas/out/*.json (11 + DEPTH_MAP)
    cuts                                nyx/atlas/cuts/*.py (30),
                                        nyx/atlas/fossils/*.json (121)
    recurrence                          nyx/atlas/recurrence/
                                        stageA_reading_candidates_2026-09-16.json
    bodies receipt                      nyx/atlas/samples/
                                        stageA_bodies_m2_2026-09-16.json
    delivery                            roles/Nyx/prompts/
                                        2026-09-16_atlas_first_pass_return/
                                        (MANIFEST; comms #296 to Techne)
    journal / status / backlog          roles/Nyx/journal/2026-09-16.md,
                                        roles/Nyx/STATUS.md,
                                        roles/Nyx/BACKLOG_H0H5.md NYX-46..52
    charter                             roles/Nyx/prompts/
                                        2026-09-13_atlas_pass_01/
                                        (sha256 7da74389f0a7d47f...)

+==============================================================================+
|  END. "Not worth continuing" is a first-class answer to this packet.        |
+==============================================================================+
