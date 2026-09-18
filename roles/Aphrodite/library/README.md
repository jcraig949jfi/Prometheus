# The Aphrodite RSI library

Currency: 2026-09-18. Owner: Aphrodite (seat on M4, charter pending).
Commissioned by the operator 2026-09-18: "Let's build a research library
about RSI ... collect research, follow the news, working theories, etc.
... Let's ask all the questions like this. It's ok if they stay
unanswered." (prompts/2026-09-18_rsi_library/.)

What this library is for: keeping the program's thinking about
recursive self-improvement (RSI) and self-improving swarms honest, in
one place, with every claim tiered by how it is known. It favours
questions and falsifiable stands over conclusions.

## Layout

    QUESTIONS.md        the open-questions register (never pruned;
                        answers annotate, never erase)
    THEORIES.md         working theories, each a stand to be attacked:
                        evidence for, against, falsifier, status
    MODELS.md           the formal models (formulas, preconditions,
                        which toy tested which, where each breaks)
    NEWS.md             dated news log, newest first, hype flagged
    sources/
      rsi_core.md       RSI bibliography, classified by WHAT each work
                        modifies (weights / scaffold / memory /
                        improvement operator / evaluator)
      swarm_failure.md  multi-agent failure, contagion, herding,
                        collusion, and the theory of their thresholds
      weak_models.md    can small, weak models be used, and when
      external_reports.md  other seats' reports: what to take, what not
    designs/
      RSI-1_TRANSPLANT_TEST_DRAFT.md   the proposed first real
                        experiment (not frozen)

Evidence the seat produced itself lives beside it, under
roles/Aphrodite/science/: rsi/ (toys E1-E4, X1, X2; 2026-09-17) and
swarm/ (damage-boundary toys S1-S4; 2026-09-18). Each has a
preregistration committed before its code, rows, verdicts and a results
file.

## Evidence tiers used everywhere here

    VERIFIED     primary source read by this seat or its subagent, date given
    PARTIAL      primary source read; the claim holds only in part
    SECONDARY    only press or summaries read
    FROM MEMORY  not read; recalled; never load-bearing
    NOT FOUND    searched for and not located
    TOY          this seat's own toy; a model/instrument check, never
                 evidence about a real system

## Rules the library keeps

- No verdict without its rows; no row without its source.
- A superseded statement stays visible beside its correction.
- Decaying claims carry a date ("nobody has measured X" as of when).
- Pure ASCII except verbatim relays (kept byte-faithful, hashed).
- The toys are near-analytic calibration; the library never presents a
  toy result as a finding about real swarms or real RSI.

## Following the news

NEWS.md is updated by hand on each pass of this seat (method and queries
recorded in its header). A standing news loop is NOT launched: under the
base role a persistent loop needs a registered monitor row, a bound on
non-productive ticks and an accountable seat (rules 7-10). Proposed as
backlog item APHRODITE-12 for the operator to accept or decline.

## Stopping rule for the swarm toys (2026-09-18)

S1-S4 have done their job; the seat does not extend them. Swarm work
reactivates only when one of these becomes measurable in a real swarm:
q vs p, rho, R0, g vs a, r or c (library/MODELS.md M1-M7).

## Charter candidates on file (the operator decides, APHRODITE-08)

1. First relayed review (2026-09-18): "Determine experimentally whether
   an autonomous, population-based improvement process can produce
   transferable improvement in its own improvement operator, beyond
   gains attributable to memory accumulation, fixed search, replay,
   selection, or evaluator exploitation."
2. Packet feedback (2026-09-18): "Determine experimentally what makes
   collective and self-improving AI systems genuinely improve their
   ability to produce future improvements, distinguishing transferable
   algorithmic change from accumulated memory, selection, additional
   compute, evaluator exploitation, and benchmark specialization.
   Maintain the research library, adversarial models, calibration
   apparatus, and experimental designs required to make those
   distinctions."
Seat's lean: candidate 2 (a permanent question that covers swarms and
the library, not tied to one experiment).
