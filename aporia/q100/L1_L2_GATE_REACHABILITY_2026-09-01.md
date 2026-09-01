# L1 and L2 gate reachability — the decisive prediction failed, and the regex that produced it was counting the word PASS

**Measured 2026-09-01 by Aporia (M2 seat)**, against `PREREG_L1_L2_GATE_REACHABILITY.md`
committed at `10d60bb0f` **before** any row was classified. The conjunction screen shipped in
that same commit, unrun and syntax-checked only.

Registries: `REGISTRY.jsonl` and `REGISTRY_L2.jsonl`, 100 rows each, now carrying
`_gate_verdict`, `_gate_verdict_refined`, `_gate_reason`, `_gate_arm_profile` and
`_chance_floor`. **Unlike L3 and L4, these verdicts are re-derivable from the registry**, because
these two lists retained their test text.

---

## 0. Addendum, same day: a scope claim I made on evidence I had not gathered

The preregistration says *"the raw L3 and L4 lists exist nowhere in the repository; `grep -rl`
over the tree finds them only inside the two findings documents."* **The grep I had actually run
covered five directories — `aporia/ docs/ engine/ pivot/ stoa/` — and searched only for the
`L3-`/`L4-` ids I assigned myself, which a raw supplied list would not carry.** The claim was
tree-wide; the measurement was not. That is the `ENUMERATE THE INVENTORY FIRST` rule in
`resume_aporia.md`, which records seven previous scope claims of mine failing. This is the eighth
occasion and the first where I caught it after committing rather than before.

**Re-run properly, and the claim holds.** Over all **34,060 tracked files** for the id pattern,
and over all **24,098 tracked `.md`/`.txt`/`.json`/`.jsonl` files** for four content strings taken
from L3 and L4 why-columns (`Gibbard-Satterthwaite`, `Subgraph Isomorphism`, `non-Abelian group
topology`, `Petri-net reachability`):

    ids          5 files, all of them q100 registries and findings documents
    content      6 files, the same five plus docs/notebook_lm/notebooklm_dark_matter_illuminated.md,
                 which mentions Gibbard-Satterthwaite in an unrelated impossibility discussion
    untracked    0 text files in the working tree

**Residual scope limits, stated rather than implied:** four content strings, not an exhaustive
fingerprint of either list; gitignored paths not searched; binary and notebook formats not
searched. The conclusion is that the raw lists are absent from the repository, not that no copy
exists anywhere — the operator's original messages are the remaining source and recovering them
is the repair.

---

## 1. The scorecard

    L1  NO_GATE          < 5%        measured   0%        HELD
    L1  THEOREM_BLOCKED  8-18%       measured   0%        FAILED (below)
    L1  BOUNDARY_GATE    15-30%      measured  17%        HELD -- but see section 4
    L1  REACHABLE        > 55%       measured  83%        HELD

    L2  NO_GATE          > 40%       measured   9%        FAILED HARD  <-- the decisive one
    L2  THEOREM_BLOCKED  < 10%       measured   0%        HELD
    L2  BOUNDARY_GATE    10-20%      measured   4%        FAILED (below)

    4 of 7 evaluable predictions held. The one I named decisive is the one that failed worst.

    conjunction screen   fires 5-12 of 200    measured 1     FAILED (below)
    screen precision     <= half its hits     measured 0/1   held vacuously
    screen misses >= 1 hand THEOREM_BLOCKED   UNEVALUABLE -- see section 6

---

## 2. Why the decisive prediction failed, located exactly

The prediction rested on one number from `probes/structure_profile.py`: the fraction of rows whose
test text contains two or more of the tokens `pass` / `fail` / `progress`.

    L1   99%      read as "L1 states two-sided thresholds"
    L2    2%      read as "L2 states no thresholds, so its gates are missing"

**Both readings were wrong, and the same three lines of code show why:**

    L1 rows with >=2 PASS tokens : 99
    L1 rows with any FAIL token  :  7
    L2 rows with any FAIL token  :  0
    L2 arms with no text at all  : 57 of 300

**The 99% was counting the word PASS appearing in each of three arms.** Seven L1 rows in a hundred
state a FAIL threshold. Under a stricter arm-level coding — PASS and FAIL *and* a number in the
same arm — L1 has **8 genuinely two-sided arms out of 300**, not 297.

So the mechanism I predicted from does not exist at the scale I claimed. L1 is not protected by
two-sided bands; it is protected by something else, identified in section 3.

And L2's 2% did not mean "no gate". **L2 gates on DIRECTION rather than on magnitude** — the
recurring `PREDICT accuracy rises while monitor AUC falls` shape. My own preregistered definition
says NO_GATE requires no threshold **and no direction**, so a directional prediction is a gate and
those rows are not NO_GATE. The rule I froze is the rule that killed the prediction, which is the
correct outcome.

**This is `feedback_measurement_carries_its_answer` firing on the instrument I built to make the
prediction.** The regex could only see numbers. I read its output as though it had seen
thresholds. The fix is the one the doctrine already states and I did not apply: state what a
metric can physically detect before predicting from it.

---

## 3. What actually protects L1, which I would not have found without the failure

L1's real discipline is not two-sided bands. **It is that L1 bounds its domains.** Every absolute
in the list arrives with an enumerable bound attached:

    Q006  zero kernel-invalid acceptance    over 1e6 proofs
    Q039  exhaustive verification           over a small domain
    Q040  zero errors                       exhaustively verified
    Q053  zero rule violations              over 1e4 updates
    Q056  unchanged solvability             over the eval set
    Q057  exact compliance                  over the restored finite rule set
    Q060  not reproducible                  within a bounded composition search
    Q080  no disagreements                  within the verified domain
    Q081  zero prohibited actions           over 1e6 trials

Nine rows where a PASS condition that reads as an unreachable absolute is in fact decidable over a
finite set the test itself names. **That is a different and better protection than a FAIL band**,
and it is precisely what L4-042 lacked when it asked a SAT solver to confirm satisfiability for
*all* subsets of 1,000 premises, and what L4-081 lacked when it asked for unbounded tasks at
constant memory.

**L1 asks L4-081's impossible question and then defuses it in its own test.** Q071's question
conjoins *"an unbounded sequence of tasks"* with *"bounded memory per task"* — the exact forbidden
pair — and its T1 bounds it to 1,000 tasks with **sublinear**, not constant, memory. The frozen
screen run over question text (exploratory, after the fact) fires on Q071 and on nothing else in
either list.

**So L1's 0% theorem-blocked is a property of its tests, not of its questions.** Scored on
ambition rather than on gates, at least three L1 rows would be blocked. The rubric scores gates,
and it should keep doing so, but the number must be quoted with that qualifier.

---

## 4. The prediction that held, held on a convention I authored mid-coding

L1's BOUNDARY_GATE landed at 17%, inside the predicted 15-30%. **That is true only under the
STRICT coding.**

    STRICT   absolutes are BOUNDARY_GATE, whatever bounds them        17%   PREDICTION HELD
    REFINED  bounded-domain exception applied (section 3's nine rows)  8%   PREDICTION FAILED

I authored the bounded-domain exception **while coding, at Q039, after seeing the rows** — it is
not in the preregistration. It moves nine rows and it decides whether my own prediction passed.
Both codings ship in the registry (`_gate_verdict` and `_gate_verdict_refined`); neither is hidden.

**STRICT is the number for cross-list comparison**, because the L3 pass coded structurally
guaranteed zeros as BOUNDARY_GATE and said so in its section 2. REFINED is the better instrument.
**Reconciling the two would require re-coding L3 and L4 under the exception — and that cannot be
done, because their test text no longer exists.** The retention defect from the preregistration
is not an abstract bookkeeping complaint; it blocks the specific repair this pass shows is needed,
one pass after it was introduced.

---

## 5. The finding that outranks the distribution: the rubric is blind to L2's defect

L2 scores **87% REACHABLE, 0% theorem-blocked, 4% boundary** — nominally the best-posed list of
the four. That reading is worthless, and the registry now carries the number that shows why.

    L2 arm gate strength, 300 arms:   DIRECTIONAL 100   NONE 126   EMPTY 57   NUMERIC 17
    L1 arm gate strength, 300 arms:   NUMERIC    217    NONE  72   TWO_SIDED 8   DIRECTIONAL 3

    L2 computable chance floor:  84 of 100 rows, median 0.500, max 1.000

**Half of L2's questions pass by coin flip.** A test reading *"PREDICT accuracy rises while
monitor AUC falls"* declares a sign and no magnitude; under a null of no effect the sign is right
half the time, or one time in four when two signs are conjoined. Fifty-seven of L2's three hundred
test arms contain **no text at all**.

The reachability rubric cannot see any of this, because it asks *can the measurement land inside
the PASS region* — and a gate with no margin always can. **A list can score perfectly on gate
reachability by declaring no gate worth failing.**

    L3 and L4 fail at the CEILING   the gate is unpassable
    L2 fails at the FLOOR           the gate is unfailable

Both are failures of the same underlying property — **gate informativeness** — and the frozen
rubric measures one side of it. This is the same defect class the loop has now hit three times:
a metric with no published chance floor. **Rows naming a chance level, null, baseline or control
anywhere in their tests: L1 4 of 100, L2 18 of 100.** Neither list publishes a floor for the
thresholds it does state.

**The second axis is declared here, disclosed as forced by L2 and NOT preregistered**, and it is
what any future list should be scored on alongside reachability:

    TWO_SIDED           PASS and FAIL both stated with numbers      chance floor near zero
    ONE_SIDED_NUMERIC   a numeric PASS threshold only               floor not computable from text
    DIRECTIONAL         a sign, no magnitude                        floor 2^-k, k = conjoined signs
    NONE / EMPTY        nothing declared                            floor 1.0, cannot fail

---

## 6. The screen: one hit, one vacuous prediction, and a repeat offence

The frozen conjunction screen fired on **1 of 200 rows**, against a predicted 5-12.

**Its single hit is substantive and my hand pass missed it.** Q001's T3 asks for *"polynomial
empirical node growth with >=95% completeness"* — `completeness+efficiency`, the forbidden pair.
Under the reading where *completeness* means fraction of problems solved, the row is REACHABLE,
which is how I hand-coded it. Under the reading where it means logical completeness, polynomial
proof growth for all tautologies implies NP=coNP and the row is THEOREM_BLOCKED. **The list does
not disambiguate, and neither did I.** That is exactly the screen-versus-hand disagreement the
preregistration named as the only informative direction, and it went the way that favours the
screen.

**Why the firing rate is so low, diagnosed rather than excused:** the screen was calibrated on
eight L4 rows carrying a full question, a why-column and three prose tests, and applied to L1/L2
registry arms averaging about fifteen telegraphic words. It needs prose it does not have here.
**And the calibration rows cannot be re-read to check that, because L4's text is gone.**

**The repeat offence, recorded loudly.** My third screen prediction — *"it misses at least one
hand-labelled THEOREM_BLOCKED row"* — is **unevaluable**, because both hand passes returned zero
theorem-blocked rows. Its reference set was empty, so the predicate could only pass vacuously.
This is the P138 defect named in `resume_aporia.md`: *a footprint computed as a set-difference of
two touched-task lists was empty by construction, so the predicate reading it passed vacuously.*
It was fixed in code for that harness and I reproduced it in prose one arc later. **A prediction
about a set must state, before it is filed, the input under which that set is non-empty.**

---

## 7. Cross-list standing, with the confound stated

    list          source     rows   blocked   boundary   reachable   no-gate
    L1            operator    100        0%       17%*         83%        0%
    L2            Claude      100        0%        4%          87%        9%
    L3 [UNAUD]    Gemini       50       28%       56%          16%         --
    L4 [UNAUD]    DeepSeek    100       16%        8%          76%         --

    * STRICT coding; 8% under the bounded-domain exception (section 4).
    [UNAUD] UNAUDITABLE_SOURCE -- test text not retained, verdict not re-derivable.

**This table is confounded and I cannot deconfound it.** L3 and L4 were coded from full source
lists with why-columns; L1 and L2 from terse registry arms. Evidence density differs by roughly an
order of magnitude between the two halves of the table, and it is not possible to tell how much of
the blocked-rate gap is list quality and how much is how much text survived. **The confound is
caused by the retention defect, not merely revealed by it.**

What survives the confound: **L1 and L2 both return zero theorem-blocked rows under a rubric that
found 28% and 16% in the other two lists.** That gap is too large to be entirely density, and it
has an identified mechanism on the L1 side (bounded domains, section 3) and a different one on the
L2 side (there is nothing to block because there is barely a gate, section 5).

---

## 8. Disposition

1. **The conjunction screen is retained but demoted** to a prose-text instrument. It may be run on
   any list that ships full question and why-column text; it is not informative on terse arms.
2. **Gate reachability is no longer sufficient as a loop precondition.** Both axes are now
   required: reachability *and* gate strength with a published chance floor. A question entering a
   dossier with a DIRECTIONAL or NONE gate must have a threshold constructed for it first, and
   that construction is part of the dossier's prerequisites section.
3. **L1's 83 reachable rows and L2's 87 are not comparable pools.** L1's are gated at a stated
   magnitude and are directly usable; L2's are research *directions* whose thresholds do not yet
   exist. L1 remains the primary pool alongside L4's 76.
4. **The source-recovery repair is now blocking, not filed.** Section 4 shows a concrete repair
   that cannot be executed. Until the raw L3 and L4 lists are committed verbatim, every number
   from those two lists carries UNAUDITABLE_SOURCE.
5. **Q001 is flagged for disambiguation** before it is used, and Q071 is recorded as the one case
   where a list asked an impossible question and its own test defused it.

---

## 9. Standing caveat, unchanged and now load-bearing

The hand coding is mine, with no independent adjudicator, and under
`feedback_promotion_requires_independent_failure_mode` a same-coder audit has approximately zero
strength. **The distribution in section 7 is therefore not the result of this pass.** The results
are the three mechanical findings — the retention anti-correlation, the PASS-token miscount, and
the 0.500 median chance floor — each of which is a number a disagreeing reader can reproduce by
running the two probes in `probes/` against the two registries.
