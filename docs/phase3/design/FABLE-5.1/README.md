# FABLE-5.1 -- Phase 3 design package

Independent architect FABLE-5.1 (seat Dionysus), 2026-10-01. Answer to
docs/phase3/PHASE3_ARCHITECT_PROMPT.md under the operator's charter
(roles/Dionysus/prompts/2026-10-01_charter/).

## Read in this order

1. PHASE3_META_ANALYSIS.md, section 1 (one page) and the last paragraph.
2. prototype/p1_slice/README.md: what already ran, including what failed.
3. OPEN_QUESTIONS.md, section A: ten things that need the operator.
4. ENGINE_PORTFOLIO.md, section 1 (one table) and section 2 (a correction
   to my own frozen hypothesis).
5. RSE_ARCHITECTURE.md, section 1, then section 13.

Everything else is reference.

## The proposal in six lines

- Study within-lifetime construction: six relocations of information
  (HOLD, ADAPT, BUILD, COMPRESS, COMPOSE, RECURSE), as coordinates for
  measurement, not as a ladder.
- Certificates before inference: DEMAND, EXPRESSIBILITY, REACH,
  DETECTABILITY. A positive needs two, a null needs all four.
- Class exclusion: a world ships the exact best score of each restricted
  policy class; beating a bound on sealed worlds needs no interpretation.
- Descent from designed organisms; search power measured on planted targets.
- One kernel, certified worlds, a conventional reference arm, two unlike
  substrates, nine experiments, no model in any run.
- Build first: one calibration slice for BUILD. A miniature has run.

## Files

| file | what it is |
|---|---|
| PHASE3_META_ANALYSIS.md | the argument: 25 sections, answers Q1 to Q10, the 90-day plan, the final answer |
| REQUIREMENTS.md, requirements.jsonl | 158 requirements, frozen before salvage (a0e3a4d03); later changes are dated annotations |
| RSE_ARCHITECTURE.md | the architecture; sections 1 to 12 frozen with the requirements; section 13 added after salvage |
| ENGINE_PORTFOLIO.md | nine experiments with every field the prompt asks for |
| SALVAGE_MATRIX.md, salvage.jsonl | 86 decisions on existing components; 30 failure fixtures; what must be new |
| ASSUMPTIONS.md | 26 assumptions, ordered by how much falls with each (first committed 28 minutes after the freeze; not part of it) |
| FALSIFIERS.md | what would overturn the thesis, each hypothesis and each design component (same provenance as ASSUMPTIONS.md) |
| OPEN_QUESTIONS.md | what is not settled, and what needs a ruling |
| prototype/p1_slice/ | code, two preregistrations, four receipts (one of a failed gate), README |
| salvage_reports/ | seven worker reports, verbatim; 00 is an incident report on a fault in my brief |
| process/ | generators and checkers; a prior-art check; my position before and after reading the challenges document; a throughput benchmark |

## How to check it

From this directory:

    python process/requirements_to_jsonl.py --check     # 158 requirements, ids unique, four lines each
    python process/test_requirements_checker.py         # the checker's own fire tests
    python process/salvage_to_jsonl.py --check          # 86 rows; tallies in the document equal the computed ones

From the repository root, for each of this directory, process/,
salvage_reports/ and prototype/p1_slice/:

    python -m comms.manifest verify docs/phase3/design/FABLE-5.1

From prototype/p1_slice/, with numpy and numba:

    python differential_test.py     # compiled kernel against a separately written oracle
    python qualify.py --power-only  # the power gate alone
    python qualify.py               # the gate
    python reach.py                 # the search-power curve (about 7 minutes on M1)

The prototype is deterministic. Timing fields and timestamps differ between
runs; counts and verdicts should not.

## What this package is not

- Not an engine. The only code that runs is a miniature of the first
  experiment.
- Not independent of its own model family. The crawlers, the salvage
  workers and the architect are one family; in the design's own terms the
  package is independence level I1.
- Not adopted. Nothing here retires a seat, changes a charter or alters
  doctrine. Those are operator acts.
- Not error-free. Two read-only reviewers checked it against its own
  sources before it was pushed and found about 80 defects, nearly all a
  statement stronger than its source. Those are corrected. The kinds are in
  roles/Dionysus/calibration/LEDGER.md. Expect more.
