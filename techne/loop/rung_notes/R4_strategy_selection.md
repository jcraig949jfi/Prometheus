# Rung R4 — Strategy Selection · Circuit Study (Loop pass 1, cycle 005)

**Canon:** Band A boundary. R4 = chooses among methods based on problem STRUCTURE; order not
supplied. Kill test (v0.1 table): a problem solvable by ≥2 methods — R4 picks by structure,
R3 picks arbitrarily.

## 1. The finding: R4 is TWO mechanisms that accuracy cannot distinguish

Built both; they tie on every accuracy probe and differ on everything else:

- **C-R4a StructuralDispatcher** — classify the AST, run exactly one program. State topology
  gains a *structure→strategy map* (a degenerate value oracle). No wasted work, no verifier
  needed; **fails closed** on unrecognized structure.
- **C-R4b VerifiedPortfolio** — try every program, believe only what the verifier accepts.
  State topology gains *branching*. Robust to unrecognized structure; pays a work
  multiplier; **impossible without a checker** (the unverified variant is a liar by design
  and is coded to abstain instead).

Consequence for batteries (this is the cycle's exportable lesson): an R4 battery that
records only accuracy cannot tell WHICH mechanism it certified — the Reasoning Trace Vector
must carry `work` (rule applications attempted) and `verifier_calls`. Both are in the
straw men's result type, and the mechanism-split test demonstrates the tie-and-separation.
This answers half of question B posed to ChatGPT (cycle 004 block): neither candidate is
"primary" — cost-oracle and branching are BOTH minimal R4 ingredients, reachable
independently, and their failure DIRECTIONS differ (closed vs robust-but-costly).

## 2. The kill, executed: base-rate inversion

`PriorSelector` (calibrated frequency prior — the gaming baseline) vs the dispatcher:
calibrated on a linear-heavy battery, tested on rational+tower problems. Prior collapses to
0/3; dispatcher 3/3, invariant by construction (it never saw base rates). The trap from
cycle 002 is now an executable test, and it generalizes: **any selector whose choice
distribution shifts when problem base rates shift (structure held fixed) is running a
prior, not reading structure.**

## 3. Traps

- **Trap 13 — prior wearing a dispatcher's clothes:** detect via base-rate inversion
  (built) and via *structure-constant/base-rate-varying* twin batteries.
- **Trap 14 — verifier leakage:** a portfolio whose "verifier" is the gold label in
  disguise turns R4 into answer-key lookup. Battery rule: verifiers must be substitution/
  re-execution checks, never dataset membership. (root_verifier here substitutes back.)
- **Trap 15 — work laundering:** a dispatcher that secretly runs the portfolio and reports
  only the winning path's work. Catch: meter rule applications inside the EXECUTOR, not by
  self-report — our `work` counts come from the pipeline layer, not the selector.

## 4. Arsenal note (same cycle)

PySR spike on REAL data landed: PARI-generated EC discriminant table (300 curves),
two-arm adjudication. ARM1 recovered `4a³ + 27b²` EXACTLY (loss 0); ARM2 shuffled-target
null floor 1.7e8; ratio 1.7e38 → RECOVERED-BEATS-NULL. Also a real integration lesson:
cypari and PySR/juliacall SEGFAULT sharing one process (signal-handler collision) —
process isolation is mandatory; the script now generates via a child process. This is the
pattern for any future PySR-over-arsenal tool.

## 5. Open questions

- Dispatcher's classifier is hand-written; the honest R4 question for LEARNED systems is
  whether their selection reads structure or prior — the inversion probe transfers directly
  to reasoning_phase0-style batteries and to grading-oracle lanes.
- R5 next (counterfactual control): state-topology prediction — branching becomes
  FIRST-CLASS state (hold two branches simultaneously and answer questions about their
  difference), vs R4's branching-as-search-then-discard. Kill test: "what changes if X
  changes" where answering requires BOTH branches' results, not the better one.

*— Techne loop, cycle 005.*
