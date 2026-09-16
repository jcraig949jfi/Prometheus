# ATLAS PASS 01 -- FIRST PASS RETURN (Stage A complete on the sample)

Nyx[m2-0c0adfe1], 2026-09-16. Charter:
roles/Nyx/prompts/2026-09-13_atlas_pass_01/ (sha256 7da74389f0a7d47f...).
Built from ccb26df01 in Prometheus-worktrees/nyx-m2-0c0adfe1-boot-2026-09-16.
Every number below is copied from nyx/atlas/out/DEPTH_MAP.json and its siblings
(python -m
nyx.atlas.build); none is typed by hand. Provenance grade of every anatomy claim
in this pass: SOURCE_READ (217 of 224 organs), METADATA (4), EXECUTED (1),
INTERVENED (2). Nothing ran in this session; the bodies were re-fetched on M2
and verified against Techne's hashes (30/30 present, 28 byte-exact, 2
line-ending-explained; nyx/atlas/samples/stageA_bodies_m2_2026-09-16.json).

Conflict of interest: the same reader authored every cut and this return.
No blind cut exists yet, so the reader's human-prior dependence is UNMEASURED.

## 1. INVENTORY

    fossils available (census)        121
    fossils inspected (Stage A)        30   stratified sample, seed 20260913
    fossils decomposed                 30
    fossils ORGAN0                      0
    fossils blocked                     0
    NOT_CUT                            91
    cut states                         COARSE 21, DEEP 9

The sample was drawn before any body was opened (2026-09-13); the 25 fossils
cut this session were taken in sample order, none skipped.

## 2. ANATOMY

    candidate fragments               224
    accepted organs                   192   (SOURCE_READ of the boundary)
    candidate organs                   32   (signatures / names only)
    rejected cuts                     121
    max depth per fossil               1: 17 fossils   2: 10   3: 3
    organs per fossil                  2..15; median 7
    rejected by reason   OTHER 38 | NAME_HAS_NO_EXECUTABLE_BOUNDARY 26 |
                         GENERIC_LANGUAGE_MECHANICS 25 |
                         EFFECT_FROM_ENVIRONMENT 18 | INHERITED 5 |
                         BELOW_GRAIN 5 | STATE_IRRELEVANT 2 | CANNOT_ISOLATE 2

Every one of the 30 fossils rejected its own human package name as an organ
(NAME_HAS_NO_EXECUTABLE_BOUNDARY, 26 explicit + 4 folded into OTHER). Two
fossils carry NEGATIVE anatomy as their identity: tinycc (no IR, no optimiser)
and python-control (no numerics; everything heavy is scipy/slycot).

## 3. PRESSURES

    pressures extracted                69   (1..4 per fossil)
    pressure families (test sets)       5   reclaim_under_live_readers (4
                                            fossils, 3 domains);
                                            bounded_shared_resource
                                            (5); crash_consistency (4);
                                            symbol_corruption_fixed_redundancy
                                            (4, two provocative members);
                                            explore_vs_commit_budget (5)
    cross-domain pressure sets          5   (the same five; all TEST SETS)
    unknown-pressure cases              0   -- but 12 of 69 cost_class fields
                                            are free text instead of the
                                            charter's three classes; DEFECT in
                                            Nyx's own records, listed in 10

## 4. EXPERIMENT

    runnable fragments                  UNKNOWN (no organ has run in isolation)
    ablations executed                  1   (Pathfinder, 09-14, on M1)
    controls                            1   vacuous-indicator control on it
    failed ablations                    0
    fingerprints produced               0
    intervention-tested organs          3   (glibc rwlock / Pathfinder, prior)
    ready Stage C ablations, by reading 6   gzip level table (4 numbers, no
                                            code change); minisom kernel radius;
                                            hopfield capacity 0.14 N; rr-arbiter
                                            equivalence (64 cases, iverilog);
                                            reed-solomon tt+1 silent pass;
                                            aes/des round-count avalanche
    M2 can run                          those needing docker/WSL: UNKNOWN on
                                            this host (not attempted)

## 5. RECURRENCE
(nyx/atlas/recurrence/stageA_reading_candidates_2026-09-16.json)

    R0                                  4   lexical only
    R1                                  8   structural
    R2                                  3   input/state/update
    R3+                                 0   (needs the wind tunnel)
    cross-domain candidates             8
    semantic-similar / behaviour-far    5   Feistel vs SPN; unbounded vs
                                            windowed min-RTT; schedule vs
                                            feedback "learning rate"; Fano vs
                                            Viterbi; radamsa scores vs VSIDS
    calibration pairs                   2   RC-01 known-identical by descent
                                            (Rockliff -> Karn RS); RC-15 two
                                            circuits claimed identical (arbiter)

The strongest cross-domain candidate by reading is RC-05: LMDB's txnid-keyed
freelist, Concurrency Kit's epoch reclamation, LevelDB's version refcounts and
SQLite's WAL read marks all gate reclamation on the oldest live reader and all
stall under one stuck reader. Human domains: database, lock-free library.

## 6. COMPOSITION

    composition edges                 298
    by label   feeds 145 | updates 35 | gates 27 | triggers 17 | competes 14 |
               selects 13 | stores 12 | schedules 9 | transforms 9 |
               restores 9 | suppresses 6 | forgets 1 | retries 1
    recurring compositions (by reading, unmeasured):
      estimator -> filter -> actuator with the plant OUTSIDE the body
        (linux-tcp x2, padasip, python-control)
      X gates reclamation of Y by the oldest reader (lmdb, ck, leveldb, sqlite)
      scheduler selects operator; operator updates scheduler score
        (radamsa, minisat VarOrder/activity)
      double buffering by parity (6 fossils, 5 domains; probably trivial)
      log first, apply second, sync between (leveldb, sqlite, lmdb commit order)
    whole-system residue   EXPLAINED 9 | PARTIALLY 16 | LARGE 4 |
                           CUT_INSTRUMENT_INSUFFICIENT 1 (sqlite, 261k lines)

## 7. BIAS

    blind cuts                          0
    ancestry-aware cuts                30
    agreements / disagreements          -- (no pair exists)
    evidence of semantic boundary bias  UNMEASURED. Observed but not measured:
       organ names in this pass were chosen to LINE UP across known-related
       fossils (aes vs des, minisat vs zchaff, rockliff vs karn); that is the
       reader importing ancestry into the cut, exactly what a blind cut would
       test. The cheapest blind protocol: the rr-arbiter (3 files, 219 lines)
       and hopfield (60 lines) with names, comments and READMEs stripped.

## 8. COVERAGE  (nyx/atlas/out/ATLAS_COVERAGE.json; 224 organs)

    measured cells in every dimension    0   (READ only; nothing ran)
    well-populated by reading            input_topology 222, output_topology
                                         222, state_amount 203, update_topology
                                         80, memory 63, stochasticity 44
    sparse by reading                    competition 29, representation_
                                         sensitivity 25, order_sensitivity 22,
                                         temporal_horizon 22, state_persistence
                                         19, resource_dependence 18, recovery
                                         18, failure_mode 16, adaptation 14,
                                         hidden_state 12, feedback 11,
                                         cooperation 11, uncertainty 6
    vocabulary never used                output GRAPH; state LOG/UNBOUNDED;
                                         feedback OPEN_LOOP; memory ARCHIVE;
                                         stochasticity ADVERSARIAL; failure
                                         DIVERGES; recovery EXTERNAL_RESET;
                                         adaptation STRUCTURE; uncertainty
                                         INTERVAL; hidden_state IGNORES
    completely unmeasured dimensions     all 19 (measured == 0)

A cell that says READ is the reader's opinion of the source. The map's
honest content is its second column: zero.

## 9. TECHNE FEEDBACK  (from measured atlas state, not from wishes)

    a. two of 30 re-fetched bodies fail their recorded tree hash on a second
       host: libfec-karn (127/127 files match after LF->CRLF: the M1 hash is
       of a CRLF checkout) and corewar-redcode (15 CRLF files + 4 __pycache__
       .pyc build products hashed inside upstream/). Git-pin hashes depend on
       the harvesting host's core.autocrlf; build products leak into the
       immutable tree. Nyx did not edit the records.
    b. the 'superseded' lineage relation has no fixed direction: 17 edges
       read, both directions present, direction sometimes in the note
       ('direction: gzip superseded compress'). The census now labels it
       UNFIXED; the ancestry graph cannot be walked until the vocabulary says.
    c. linux-tcp-congestion packs two whole systems (CUBIC 2008, BBR 2016)
       in one record; the atlas cut them as two subsystems with an
       intra-record rival_of edge.
    d. des-reference's record says the oracle is a known-answer test; the
       executed recipe is a round trip (passes for any invertible transform).
       tiny-aes-c's shipped test IS a known-answer test; the contrast is
       useful and should be in the record.
    e. missing executable WORLDS (Stage C cannot open without them): a
       kernel + netem plant for linux-tcp-congestion (SOURCE_ONLY); a
       multi-core host for concurrencykit's contention claims; a crash
       injector between write and commit for lmdb / leveldb / sqlite (their
       whole identity is that instant and no receipt exercises it); a
       weak-memory machine for CK's fence claims (invisible on x86).
    f. missing BODIES the atlas points at: lib/win_minmax.c (BBR's filter),
       the kernel TCP core (both congestion modules are controllers of a
       plant not in the vault), scipy/slycot's Riccati and ODE solvers
       (python-control's true machinery), the GnuCOBOL runtime (every COBOL
       organ is executed by it).
    g. fossils that would most improve the atlas next, from what the sample
       could not distinguish: a coverage-guided fuzzer (AFL/libFuzzer) as the
       feedback-bearing contrast to radamsa's blind scheduler; the unsampled
       vault members that complete the pressure sets -- backoff-2.2.1 (the
       named ancestor of RC-07), bdwgc (reclamation with a collector, the
       missing member of RC-05's set), willemt-raft / cocagne-plain-paxos
       (agreement, beside memberlist's failure detector), xv6 (a scheduler
       beside the arbiter and MARS); and a second SOM / Hopfield variant to
       test whether RC-08's 'learning rate' divergence is family-wide.
    h. missing controls: no fossil in the sample ships a NEGATIVE control
       (a run that must fail); erfa and tiny-aes ship positive oracles; a
       vault-wide 'must-fail' input per fossil would let Stage C start from
       a known floor.

## 10. ARCHAEOLOGICAL SURPRISES  (reported, not interpreted)

    - gzip carries its rival's DECODER (unlzw.c) beside its own encoder and
      never encodes LZW: the patent pressure is preserved as an asymmetry in
      the file list.
    - the same 'double buffering by parity' shape appears in six fossils in
      five human domains (lmdb meta pages, fftpack C/CH, viterbi metrics,
      bbr extra_acked[2], leveldb mem_/imm_, ssw H buffers). Probably
      behaviourally trivial; recorded so the tunnel can show that.
    - radamsa's mutator scheduler has NO signal from the target: its scores
      are a biased random walk clamped to [2, 10]. It looks like a bandit
      and is not one.
    - ELIZA's 'certain counting mechanism' is a 1..4 counter that governs
      both when memories are recalled and which deflection is printed: one
      register, two behaviours.
    - the round-robin arbiter deasserts its own grant the cycle after
      granting, so a sole continuous requester is served every other cycle;
      the readme does not mention it.
    - hopfield's stopping rule (energy unchanged) cannot see a synchronous
      2-cycle (constant energy); it would return the first state of the
      cycle as converged. A reading claim; unmeasured.
    - reed-solomon-1991 passes uncorrectable data through with no flag; its
      descendant returns -1. The same anatomy, one different failure shape.
    - CK's epoch reclamation and LMDB's freelist fail the same way (one stuck
      reader stops everyone) though no line of code is shared and the
      authors' domains do not overlap.
    - COBOL's fossil is a language, not a program: every organ is executed by
      a runtime that is not in the body, and the record's own observation
      (packed decimals format correctly, EBCDIC text does not) is the atlas's
      cleanest example of a layout surviving its encoding.
    - the two largest bodies (sqlite 261k, tinycc 27k lines) gave the
      shallowest cuts; the two smallest (hopfield 60, rr-arbiter 219) gave
      complete ones. Depth in this pass is a function of the reader's
      session, not of the machinery. The cut instrument is the bottleneck
      the directive's Stage B must budget for (one subsystem per session).

## What would falsify this return

Stage C running the six ready ablations. If gzip's level table changes ratio
and time as the mechanism reading predicts, the reading is calibrated; if the
arbiter's two circuits differ on any of 64 cases, one ACCEPTED organ is wrong;
if hopfield's synchronous update does not 2-cycle on any pattern set, a
failure_landscape claim dies. A blind cut of rr-arbiter and hopfield that
disagrees with the ancestry-aware cut on boundaries is evidence of bias; one
that agrees is evidence of nothing.

## What should stop

Cutting NOT_CUT fossils at this grain without running anything. 30 read cuts
and 0 measured cells is the current ratio; the next 30 read cuts would double
the first number and leave the second at zero. Stage C on the six ready
ablations (all CPU-scale, all in Techne's containers) should precede Stage A
on the remaining 91.

## Next executable action

Stage C: the gzip level-table ablation on Techne's fossil-c-toolchain image
(ratio and wall time per level on one corpus; the table is the only variable),
with a positive control (level 0 = stored, ratio 1.0) and a cheat control
(a pre-compressed input must show no gain at any level). Requires docker via
WSL on M2: UNKNOWN whether present; first command is the check.
