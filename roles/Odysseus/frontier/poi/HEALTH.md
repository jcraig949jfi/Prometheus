# Frontier health (Block L)

Currency: 2026-09-27, end of the first cultivation pass. Odysseus.
Numbers are descriptive, not targets. Pure ASCII.

## Counts

    harvested (internal candidate threads, raw/I1..I6)     138
    external idea entries (raw/E1..E6)                      145
    external open questions (raw/E1..E6)                   ~100
    POI threads after merging (BACKLOG.md)                   75
      created new by this pass (not in any raw file)          3  (POI-005, POI-096 from spikes; POI-022 reframed)
      merged (many raw threads -> one POI)                   ~60 raw -> 20 POI (e.g. POI-001 <- 5 raw; POI-025 <- 5)
      split                                                   2  (territory F out of D; G out of B/D)
      sharpened to SHARP                                     39
      READY (packet or instrument)                            5 + R4/R5/R6 packets (6 packets total)
      linked to existing ops threads (not duplicated)         5  (TH-001, -003, -004, -005, -006)
      answered / partly answered by a spike                   5  (POI-004 S1, POI-022 S3, POI-096 S4, POI-053 S2, POI-060 S5)
      weakened by prior art                                   4  (replicator emergence is old; interaction does
                                                                  not discover replicators; library learning;
                                                                  dissipation bounds)
      made newly tractable                                    4  (POI-020 by the BFF-2026 baseline; POI-060 by S5;
                                                                  POI-061 by S6; POI-001 by the TH-006 node replay)
      blocked by instrumentation / evidence                   2  (POI-011 lost data; POI-041 doctrine)
      new-lens candidates                                     7  (NEWLENS.md L1-L7)
    not carried forward (momentum-only or software)          ~13, listed at the end of BACKLOG.md

## Delegate reliability (measured, not assumed)

Three delegate claims were independently re-checked by spikes:
    S4 BAND0 decomposition (raw/I1 T3)     PARTLY CONFIRMED (wording wrong, 2 residual)
    S3 cliff headroom (raw/I4-04)          CONFIRMED in direction, counts corrected
    S2 SI dev re-read (raw/I3 T1-T5)       one claim REVERSED (random eviction does NOT win)
Rule adopted: a delegate's COMPUTED-HERE or INFERRED number is a candidate,
not a finding, until a separate worker recomputes it from source. Several
raw files also contain nested sub-delegate claims marked "per sub-report".

## Pathologies found

1. ENGINE CONCENTRATION: three Z80 worlds plus an auditor cover the
   replicator route; the non-reproductive routes, individuation, major
   transitions, agency, cost of computation and open-endedness have no
   designed lens (CROSSWALK). The backlog inherits this: ~30 of 75 threads
   name a Z80 engine.
2. DUPLICATED QUESTIONS WITHOUT CITATION: "existence is not accessibility"
   was found four times; "label read as property" 21 times across 15 seats.
   The frontier merges them; the program still has no shared place where a
   new seat would find them first (Artemis T5, packet R3).
3. VAGUE THREADS: ~24 POI entries remain CANDIDATE (one line); most in
   territories B and M. They are kept, not padded.
4. FAMILIAR-MODALITY PULL: the SI/WTP line frames intelligence as a bounded
   memory learner with eviction policies; its law's elimination half is a
   theorem (POI-053). LLM-in-the-loop and benchmark gravity are listed as
   traps (TERRITORIES III), not threads.
5. STALE ASSUMPTIONS: the program's AI review dates from May 2026; [CORRECTED 2026-09-28: the Z80 program HAD cited Cicala 2026 and
   Nestor's npe-p2 cites BFF 2026 -- see REPORT.md correction]; "0/5,472 mutational cliff" is cited as a cliff (it is a plateau,
   S3); critical_memories' tensor-first rules predate the September north
   star (raw/I5 s4).
6. EVIDENCE LOSS AND LOCALITY: positives that exist only in commit messages
   (Aether rcv_add/rcv_str, POI-011); most engine evidence off-repo
   (TH-006, Artemis T3). A frontier built on the record inherits its gaps.
7. MOMENTUM-ONLY QUESTIONS: ~13 raw threads (H0/H1 "nothing could fire",
   LLM-mechanism novelty, raw/I5 s5 list) exist only because a lane once
   posed them; recorded and not carried forward.

## What would keep this frontier healthy

- Each pass: consume 3-5 cheap spikes from SHARP threads (this pass: 6),
  and let their results rewrite entries (this pass: 5 entries changed).
- Every delegate number is recomputed by a second worker before it
  changes a thread's state.
- New external raid every ~3 months in the fast fields (AI, ALife soups);
  the Z80 prior art appeared within two months of this pass.
- A packet counts as READY only after a fresh worker has used it and
  listed its gaps. FIRST TRIAL (R4_A-001): the packet was NOT research-
  ready in the sense that matters -- the worker started and finished
  without asking anyone, but listed 12 gaps, the worst being prior runs
  of the same question already in the repository (C4-05, C3-SFE-02) and
  an artifact the packet claimed existed (a known summit program) that
  did not. Fix applied to ready/00_READ_FIRST.md (search for prior runs
  first; verify claimed artifacts). R1-R3, R5, R6 are therefore "READY v0,
  untried"; expect similar gaps.
