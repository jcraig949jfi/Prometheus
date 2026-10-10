# W01 (DEV) REPORT: BETA-04 ACTIVATION AND INSTRUMENT BUILD

C-015, 2026-10-10 09:27-13:27Z. Starting SHA: origin/main 5956b542e.

- **Activation:**
  - Directive saved verbatim.
  - C-015 created (the id was checked on origin first); workgraph validate OK.
  - State, ledger and the experiment plan with shared interface contract v0.
- **Required reading** (beta04/READING_DIGEST.md). Principles adopted in plan s5:
  - archive factorisation (Nyx);
  - descriptor qualification first (C-013 D1);
  - foundry rigor (Fable / WTP-05);
  - Hestia's ledger and controls.
  - Coordination with Palamedes (C-013 D1: reuse agreed, #2035) and Ensorain (C-014). Theseus input (#2032) recorded.
- **Leads delivered and merged:**
  - **TFS-1 substrate:** 15/15 tests; toy depth-2 sensitivity 8/8 with the correct primitive vs 0/8 with none or the
    wrong one.
  - **Foundry v1:** 20/20 tests.
  - **Atlas:** 14/14 tests; descriptor qualification ported from C-013 D1 (D-CERT fails everywhere, reproducing D1);
    the route predictor is uncalibrated, so it is descriptive only.
- **Known answer K-AB:** independent interpreters A vs B, 204k runs, 0 mismatches: **PASS.**
- **E1 foundry v1: NOT_QUALIFIED** (pre-freeze red team). The demand was feature selection, not composition, and the
  R1 prerequisite was circular.
  - The v2 repair rules were frozen.
  - The v2 pilot ran once: gate 2/3 worlds; admitted R2 6 / R3 5 / R4 2 / R5 0; 2 mechanism pairings.
  - **Addendum D** (frozen before production): E1 is decided on 12 secret production worlds, strict reading.
- **Process defect:** a lead killed a sibling lead's run; it was rerun, and the PID rule was restated.
- **Compute so far:** about 8 core-h (leads, reviews, conformance).
- **Next (W02):**
  - production worlds -> the E1 decision;
  - pre-register E2 (atlas) and E3 (TFS-1 2x2) on the admitted tasks, with a red team first.
