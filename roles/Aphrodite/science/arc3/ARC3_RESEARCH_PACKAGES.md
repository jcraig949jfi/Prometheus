# ARC3 RESEARCH-READY PACKAGES (for fresh researchers; read ARC3_WORKER_BRIEFING.md first)

Each package names its question, prerequisites, method, stop rule and resource class. None
of them needs the principal's oral context. Where a worker report already contains the
detailed design, the package points to it instead of restating it.
Resource classes: S = <= 1 core, static; M = <= 2 cores (lease); L = >= 4 cores (lease).

PKG-1  WINDOW-BY-DESIGN LEARNABILITY INSTRUMENT (T31; W2 F2 + F3)          [M -> L]
  Q  Can the learnable window be populated cleanly by stratifying families on the
     equivalence-class difficulty D, with a per-stratum escrow, or by ablating the
     init-major fallback order?
  Design: w2_learnability/REPORT.md s4, s6 (F2, F3). The signature table builds in ~3 min.
  Stop: if the window fraction at designed D stays < 0.1, report the instrument as the
     limit and stop.
  Note: F3 changes the reference walk, so it needs its own amendment before any assay
     uses it.

PKG-2  EXTENSIONAL REUSE RE-MEASUREMENT (W2 F1; W3 Part 2)                   [S]
  Q  Measured on extensional classes (library-relative D_P - D_L), not literal bodies,
     does "reuse" in C2 (and C3R once done) change level?
  Method: w2_fallback.sig_table + the C2 donor entries; per transfer family, compute
     whether the selected schema's span holds an extensional equivalent, and its D gain.
     Report the W3 levels L2 / L3a / L3b.
  Stop: none; it is a measurement.

PKG-3  NATURAL RECURRENCE VIA LINEAGE GENERATOR LIN-NX (W1 CG-1: WP-1 then WP-2)   [M -> L]
  Q  Does naturally emergent recurrence give a dose-response of ladder outcomes on
     realised recurrence X_S, pooled across inherited schemas?
  Design: w1_natural_curricula/REPORT.md s4, s7.
  Prerequisite: PKG-1 or a declared escrow that avoids the cliff (W2), otherwise
     OBSERVE/window fills will fail again (C3's lesson).
  Stop: WP-1's stop rule (fewer than 25% of seeds with X_G1 >= .10).

PKG-4  IMPROVER-EVOLUTION FEASIBILITY: GENOME TRANSFER-CORRELATION PROBE (W4)   [L]
  Q  Does any rule-only improver genome beat the ancestral improver on UNSEEN strata,
     with a gain that grows from generation 1 to 2, while a planted overfitter (P15)
     shows a develop-win / unseen-loss pattern?
  Design: w4_improver_transplant/REPORT.md (first bounded experiment). Needs a
     data-driven donor interpreter with a conformance gate, plus a chain runner.
  SEPARATE PROGRAM (P2). Never mixed into compounding dispositions.
  Stop: W4's GO/STOP rule.

PKG-5  PROMOTED-PRIMITIVE FIXTURE FOR SECOND-GENERATION COMPOUNDING (T39; Block G)   [S]
  Q  If a selected schema G2 is promoted to a one-node primitive P2(x), do G3 = wrap(P2)
     schemas gain real extent (>= 20 accumulating instances) under a node-count budget,
     and are any G3 NEW vs G2?
  Method: a modified COPY of the grammar builder that treats P2 as a primitive of depth 1;
     recompute science/arc3/second_gen/G3_REACH with instances counted by node budget.
  Stop: if G3 extent stays at atom-filler level, second-generation compounding needs more
     than promotion; report it.

PKG-6  INSTRUMENT HYGIENE: T4 / DEV QUERY ALIGNMENT + Q2 BEYOND COVERAGE (W2 F4, F5; T44)   [S/M]
  Q  How many p_* statistics and qualified solves flip when T4's counterexample queries
     (1, 2) are aligned with dev (3..97)? How many fallback first hits are spurious per
     arm?
  Deliverable: a draft instrument version (never edit tribunal_t4.py in place).

PKG-7  RULER v2.1 (W3 repairs; T44, T29)                                     [S]
  Close relations() over re-expressions; require the same witness instances for grid and
  trajectory; product None tolerance; the W5 base rate; the domain-respecting trajectory
  battery. Re-score RB-1 / K9b / C2 / C3R. Draft only.

PKG-8  PROPAGATION ACROSS GENERATIONS (Aether hypothesis via W5; T38)            [L]
  Twin G1-present / G1-absent lineages, 2-3 donor generations: does the footprint grow or
  stay flat? Run only after C3R (it uses the C3R supply design).
