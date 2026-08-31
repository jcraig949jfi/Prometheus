# L4 (DeepSeek) gate reachability — a preregistered prediction, and the one that failed

**Measured 2026-08-31 by Aporia**, against `PREREG_L4_GATE_REACHABILITY.md` committed at
`cad23ffd` **before** any row was classified. Registry: `REGISTRY_L4.jsonl`, 100 rows, complete.

---

## 1. Result, against the prereg

    FAIL   THEOREM_BLOCKED < 10%     measured 16.0%
    PASS   REACHABLE       > 50%     measured 76.0%
    PASS   UNREACHABLE     < 50%     measured 24.0%

    2 of 3 predictions held.

Full distribution, same rubric and same coder as L3, so the comparison is valid:

    list             blocked   boundary   reachable   unreachable
    L3 (Gemini)        28.0%      56.0%       16.0%         84%
    L4 (DeepSeek)      16.0%       8.0%       76.0%         24%

## 2. What the failed prediction teaches, which is more than the two that held

I predicted under 10% theorem-blocked on the strength of L4's **T3 counterexample discipline** —
the recurring "show a case where it fails; fail if found" arm that L3 almost never had.

**That discipline worked, and it worked enormously — on the wrong axis.** Boundary gates fell
from 56% to 8%, a sevenfold reduction. Every prediction I made about well-formed falsifiers was
correct.

**But a well-formed falsifier does not rescue a question that is impossible at T1.** Of the 16
blocked rows, only 8 are the type I anticipated — where the why-column concedes NP-hardness or
undecidability and T1 demands a polynomial or complete algorithm anyway (L4-017 planning,
L4-019 continuous POMDPs, L4-020 recursive HTN, L4-022 exponential Pareto sets, L4-026
latent-confounder MEC, L4-033 structural mapping, L4-078 NEXP multi-agent POMDPs, L4-079
Gibbard-Satterthwaite). My prereg guessed "fewer than ten rows" of that type; eight is correct.

**The overshoot came from a category I did not anticipate: questions blocked by a theorem the
list never mentions.**

- **L4-095** demands attention weights on irrelevant tokens be **exactly zero**. Softmax has
  full support. Unattainable by construction, and the list does not notice.
- **L4-061** asks for sample complexity `o(2^n)` for **arbitrary** Boolean functions. There are
  2^(2^n) such functions; the bound is information-theoretic.
- **L4-081** wants an unbounded task sequence at **constant memory with zero forgetting** —
  unbounded information in bounded storage.
- **L4-076** wants decentralized convergence to Nash in **all** finite stochastic games. Hart and
  Mas-Colell proved uncoupled dynamics cannot.
- **L4-029** wants an estimator both doubly robust **and** efficient under *arbitrarily*
  mis-specified nuisances. Double robustness requires at least one correct.
- **L4-042** requires a SAT solver to confirm satisfiability for **all subsets** of 1,000
  premises — 2^1000 checks.
- **L4-008** wants termination **and** completeness for higher-order proof search, which is
  decidability of an undecidable problem.
- **L4-014** wants sound **and** complete inference for all almost-surely-terminating
  probabilistic programs; exact conditioning on continuous observations is not computable.

**The generalisable lesson:** these eight share one syntactic tell — a conjunction of two
properties that a theorem says cannot co-occur (`termination AND completeness`, `sound AND
complete`, `doubly robust AND efficient`, `truthful AND welfare-maximizing`, `constant memory
AND no forgetting`, `unbounded AND exact`). **The falsifier arm cannot see this, because the
defect is in the conjunction, not in the threshold.** A T3 that hunts a counterexample to an
impossible claim will always succeed, which reads as a well-behaved test right up until you
notice the question could never have passed.

**Screening rule this yields, cheap and mechanical:** flag any question whose PASS condition
conjoins two properties, then check the pair against known impossibility results. That is a
different screen from the boundary-token regex and would have caught all eight.

## 3. What L4 does well, and should be copied

L4 is the best-posed of the four lists by a wide margin, and three habits explain it:

1. **Impossibility as a PASS condition.** L4-001 passes on an ETH-based lower bound; L4-005 on a
   Petri-net-reachability undecidability reduction; L4-011 on an information-theoretic lower
   bound; L4-064 says "prove **or disprove**". These treat a limit as a settling result rather
   than a failure — the posture this programme uses when it reports VACUOUS instead of null, and
   the thing L1, L2 and L3 between them managed only once (L3-042).
2. **Class restriction in T1.** L4-023, L4-066 and L4-091 all say "for a class of" rather than
   "for all", which converts three otherwise-blocked questions into answerable ones.
3. **Bands with an explicit progress tier.** Most rows carry pass / fail / progress rather than a
   single threshold, so a partial result is reportable instead of discarded.

## 4. Cross-list standing

    list           source     rows   blocked   unreachable   character
    L1             operator    100      --          --       capability, classical-AI lineage
    L2             Claude       100      --          --       instrument validity, empirical-ML lineage
    L3             Gemini        50    28.0%        84%       formal/architectural, largely unreachable
    L4             DeepSeek     100    16.0%        24%       complexity-theoretic, best-posed

L1 and L2 have not been hand-classified under this rubric; the mechanical boundary-token proxy
put them at 26% and 17%, which is a crude upper bound on boundary gates only and says nothing
about theorem-blocking. **That hand pass is now the outstanding work item**, and the conjunction
screen from §2 should be run over all four lists at once.

## 5. Disposition

- **L4's 76 reachable rows are the best raw material any of the four lists has produced** and
  should be the pool the Q100 loop draws from ahead of L1 and L3.
- The 16 blocked rows are recorded as category errors, not researched.
- The conjunction screen is added to the loop's reachability precondition alongside the
  attainable-range check.
- **The prediction failure stands as recorded.** It is the first preregistered prediction in this
  loop and it came back 2 of 3, which is worth more than a clean sweep would have been: the
  mechanism I proposed is real and measurable, and it protects against exactly one of the two
  ways a gate can be unreachable.
