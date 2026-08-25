# Cycle 061 — the arsenal reds, by cause rather than by count

**Techne, 2026-08-25. Campaign cycle 2 of 20 under `techne/loop/CAMPAIGN_ESCAPE_RATE_PREREG.md`.**
Controls FROZEN. Section 1 was committed BEFORE the failing node ids were read.

---

## 1. PRE-REGISTRATION (committed before measuring)

**Work selected:** campaign item (b) — attack the arsenal reds, diffing by failing node id and
never by count. Plus finding #16, which I pre-announced in cycle 060 as its own isolated commit.

**The question.**

> Q: What is each red actually caused by — and how many of them are load-bearing?

The standing figure in my own brief is *"46 arsenal reds, 26+ missing optional dependencies,
gated on HITL #242."* **Cycle 060 measured 44, not 46.** The 46 is the cycle-052 baseline, which
is stale by eight cycles; the current count is 44 with a name-diff of 0 NEW and 2 GONE. That is
already one correction to a number I have been quoting, and it is the reason this cycle triages
by cause instead of attacking a total.

**Declared population, before looking.** The **complete** set of FAILED pytest node ids in
`pivot/arsenal_red_060.json`, plus the 3 collection errors in the same file. Full scan, every id
classified, no sampling and no ordered slice. The file is committed and its producing command is
recorded in it.

**Classification scheme, fixed before reading the ids** — so the buckets cannot be drawn around
whatever I happen to find:

- `MISSING_DEPENDENCY` — fails because an optional third-party package is absent. Gated on #242,
  not on me.
- `STALE_ASSERTION` — the test asserts a literal that the data or the code has since outgrown.
  The test is wrong, not the code. (#341 is a known instance.)
- `REAL_DEFECT` — the code is wrong and the test is right.
- `ENVIRONMENT` — network, filesystem, database, or platform, not mathematics.
- `UNCLASSIFIED` — I could not determine the cause within the cycle. **This bucket must exist and
  must be reported non-empty if it is non-empty**, because a triage with no residual category
  silently converts "I did not look" into "there was nothing there".

### Predictions

1. **No claim exported this cycle will be HELD by `techne/lib/claim_record.py`'s
   `Claim.promotable()`.** Confidence **high**; **D0**. This is now a mechanism claim rather than
   a guess: cycle 060 finding #17 established that the promotion rule depends on a boolean the
   author sets, so it has no capacity to block. *Opposite:* a block would mean I have
   misdiagnosed #17 and the control has some teeth after all — which would be good news and I
   would rather be wrong here.
2. **Fewer than 26 of the 44 reds are `MISSING_DEPENDENCY`.** Confidence **moderate**; **D2**.
   The "26+" figure has the same provenance as the "46" that cycle 060 measured to be 44 — an
   uncounted number carried forward across cycles. *Opposite:* 26 or more would mean the figure
   was sound and my suspicion of it is the error, which is worth knowing about my own priors on
   my own numbers.
3. **At least one red is a `STALE_ASSERTION`.** Confidence **moderate-to-high**; **D1**. #341 is
   already known to be one. *Opposite:* zero would mean #341 is not currently red, i.e. the
   outstanding ruling is about a test that is not failing.
4. **All 3 collection errors are import failures.** Confidence **high**; **D1**. *Opposite:* a
   collection error from something other than an import would be a genuinely new shape.
5. **At least one `REAL_DEFECT` exists among the reds** — arsenal code that is wrong and has a
   test saying so that nobody has acted on. Confidence **moderate**; **D2**. *Opposite:* zero
   real defects would mean the red count is entirely environmental and stale-assertion debt, and
   the "46 reds" framing has been overstating the arsenal's brokenness for eight cycles.
6. **The `UNCLASSIFIED` bucket will be non-empty.** Confidence **moderate**; **D2**. Triage of 44
   heterogeneous failures inside one cycle will not resolve every cause. *Opposite:* an empty
   residual would be suspicious and I would check whether I had widened the other buckets to
   absorb it.

### Committed in advance about finding #16

`techne/lib/cf_expansion.py::zaremba_test(1)` returns `satisfies=False` although q = 1 satisfies
Zaremba's conjecture trivially. I flagged it to James in cycle 060 as HITL #422 and said I would
fix it in cycle 061 as its own isolated commit unless told otherwise. **No ruling has arrived.**
The function is mine, the semantics are mine, and cross-role science is the only thing barred —
so I am proceeding, in a commit that touches nothing else, so that the semantic change is
reviewable on its own.

**What the fix must not do:** change any q >= 2. That is asserted, not assumed.

*— pre-registration ends here. Everything below was written after measuring.*

---

## 2. TLDR

**None of the arsenal's 44 reds is broken mathematics.** Re-running every one of them
individually and classifying by the exception it actually raises: 39 are missing optional
packages, 4 pass when run alone and fail only inside the full suite, 1 is a stale authority
literal (already open as #341), 2 are deliberately red by a cycle-046 pre-registration that
correctly refused to make them green, and 1 is a wall-clock gate that swings 27× with machine
load. **Zero unaddressed defects in arsenal code.** The standing "46 arsenal reds" framing has
been reporting an incomplete environment as a broken arsenal — and "46" was itself the stale
cycle-052 baseline.

**And cycle 060's headline finding was stated too broadly. I am correcting it.** I claimed
`Claim.promotable()` "cannot block anything." This cycle it blocked **2 of 5** claims, both
correctly. The true, narrower statement is in §4.

Finding #16 is fixed and shipped in its own commit, with a 500-value differential showing
exactly one q changed.

## 3. ELI5

We had a list of 44 broken tests, and everyone kept saying "44 things are broken." So I ran each
one and asked it *why* it was unhappy. Almost all of them said "you never installed the tool I
need." Four said nothing at all — they only get upset when run in a crowd. One is checking an old
number that changed. Two are *supposed* to be unhappy, because pretending otherwise would mean
making up a measurement. And one is just a stopwatch that goes off when the computer is busy.

So the workshop isn't broken. The toolbox is missing tools.

The other half: last time I announced that my "is this finding actually checked by something
independent?" rule was useless because it had never stopped anything. This time it stopped two of
my five findings, and it was right both times. So the rule works — it just can't catch me if I
lie to it. That's a much smaller problem than the one I announced, and saying so is the point.

---

## 4. PREDICTIONS SCORED — D0 first

### D0 FALSIFIED — prediction 1, and it corrects cycle 060

I predicted, at **high** confidence and tagged **D0**, that no claim would be HELD, because cycle
060's finding #17 established that `Claim.promotable()` depends on a boolean the author sets and
therefore "has no capacity to block."

**It blocked 2 of 5.**

- **C061-3 HELD** — its strongest independent adjudication is `DIFFERENTIAL_TEST`, below the
  `KNOWN_ANSWER_CONTROL` bar. Correct: two row sets disagreeing about four node ids is real
  evidence, and there is no oracle for it.
- **C061-5 HELD** — `SAME_MODEL_AUDIT`. Correct: it is a judgement about my own classification
  scheme and has no independent adjudicator at all.

**The correction, stated plainly.** Finding #17 as written in cycle 060 is **too broad**. The
accurate claim is narrower:

> `Claim.promotable()` enforces the bar on any claim whose adjudications are labelled honestly.
> What it cannot do is detect a **mislabelled** one, because `independent_of_generator` is
> self-reported. Its failure mode is dishonesty or self-deception, not impotence.

Cycle 060 observed 8 of 8 promotable and concluded the control was toothless. The alternative
explanation — that those 8 genuinely had known-answer-or-better independent adjudication — was
available on the same page and I did not weigh it. **That is the same shape as the inflated
headline I catalogued in cycle 060: a conclusion drawn from one reading of an observation with a
second reading sitting beside it.** Committed as a correction rather than a footnote.

### D2 FALSIFIED — prediction 2, and my distrust was the error

I predicted **fewer than 26** of the reds would be `MISSING_DEPENDENCY`, reasoning that the
standing "26+" had the same unaudited provenance as the "46" that turned out to be 44.

**39 of 47 are missing-dependency.** The standing figure was an **understatement**, not an
inflation. I was right that the total was stale and wrong about the direction of the error in the
share — and I had pre-committed the direction, which is why this scores as a falsification rather
than a partial hit.

### D1 CONFIRMED — prediction 3

Exactly one `STALE_ASSERTION`: `test_authority_mossinghoff_178_entries`, failing on
`assert 8625 == 178`. **That is HITL #341**, which has been open awaiting a ruling — so the
outstanding item is confirmed to be a currently-failing test rather than a hypothetical one.

### D1 CONFIRMED — prediction 4

All 3 collection errors are import failures, all three `matplotlib`, all three under
`prometheus_math/viz`.

### D2 FALSIFIED — prediction 5, and this is the cycle's main result

I predicted at least one `REAL_DEFECT` — arsenal code that is wrong, with a test saying so, that
nobody has acted on. **There are none.**

The two candidates both dissolve on inspection, and dissolve *informatively*:

- The **hyperbolic-volume** failures are a real mathematical defect — 48 knots in the corpus
  carry `hyperbolic_volume = 0.0`, which is impossible for a hyperbolic knot by Mostow rigidity.
  But it was diagnosed in cycle 046, pre-registered with a decision rule, and handled: the corpus
  now carries `hyperbolic_volume_known` and
  `prometheus_math/_knot_trace_field_corpus.py::corpus_volumes_are_measured` returns False. The
  cycle-046 pre-registration states outright that *"a red test may become green only by the
  corpus ceasing to ship impossible values… making an authority test pass without the authority's
  data would be fabricating a measurement, which is worse than a red test."* **These two are red
  on purpose, and correctly so.**
- The **couplet** failure is `assert result.runtime_ms < 50`. It read **2230** inside the loaded
  full-suite run and **83** standalone — a 27× swing driven by machine load. A gate whose verdict
  is a function of what else is running is not measuring the code.

### D2 CONFIRMED — prediction 6

The mechanical pass left 8 `UNCLASSIFIED`, as predicted. All 8 were resolved by reading, and the
machine-decided and human-decided shares are kept separable in
`techne/loop/claims_061.py::READ_ASSIGNMENTS` rather than merged into one number.

### UNPREDICTED — the scheme I fixed in advance was incomplete

Two buckets the data required and the pre-registration did not have: `NO_LONGER_FAILS` (not a
cause at all — a property of the run) and `DELIBERATELY_RED` (a red a prior pre-registration
decided must stay red). And `REAL_DEFECT`, which I pre-registered and expected to fill, came back
**empty**. Fixing a classification scheme before looking does not make it complete; it makes its
incompleteness *visible*, which is the reason to do it.

---

## 5. WHAT THE REDS ACTUALLY ARE

The seven absent modules, extracted from the interpreter's own messages rather than recalled:
`GUDHI`, `chipfiring`, `cvxpy`, `matplotlib`, `pysat`, `pytest_benchmark`, `shapely>=2.0`, plus a
MIP backend (`pyscipopt` / `ortools` / `highs`) reported as a `ValueError` rather than an
`ImportError`. **This is the #242 dependency list, derived from evidence.** It is what a ruling on
#242 would actually buy: on this measurement, 39 of 47 reds.

**A methodological note that outlives this cycle.** Classifying these by test name would have been
wrong in both directions. `test_edge_non_psd_raises` reads as a mathematical edge case and fails
on an ImportError; `test_3sat_unsatisfiable` reads as a solver disagreement and fails for want of
`pysat`; `test_authority_figure_8_volume_is_2_0299` reads as a broken authority check and is a
deliberate red. **Names are not causes**, and this loop has twice shipped an invented label
attached to a real observation.

---

## 6. THE CLAIMS

Rendered from `techne/loop/claims_061.py` via `techne/lib/claim_record.py::render`. Every number
is read from a committed row file. **Two are HELD and shown as HELD** — the record carries them
at the strength they earned rather than suppressing them or promoting them.


### C061-1 — PROMOTABLE
**Proposition.** None of them. Across all 47 red node ids -- the complete FAILED list plus the collection errors -- the count classified as an unaddressed defect in arsenal code is ZERO. The distribution is 39 missing optional dependency, 4 that pass when run individually, 1 stale authority literal, 2 deliberately red by a prior pre-registration, and 1 load-sensitive wall-clock gate. The standing framing of 'N arsenal reds' has been reporting an incomplete environment as if it were a broken arsenal.
**Question.** How many of the arsenal's reds are actually broken MATHEMATICS, as opposed to an incomplete environment?
**Population.** arsenal-reds-060 (n=47, full-scan (complete list, no truncation), fingerprint 3a035a127f37b9c6)
**Measured.** {'tally': {'MISSING_DEPENDENCY': 39, 'NO_LONGER_FAILS': 4, 'STALE_ASSERTION': 1, 'ENVIRONMENT': 1, 'DELIBERATELY_RED': 2}, 'real_defects': 0} via `python techne/loop/measure_061_red_triage.py`
**Contract.** node ids whose cause is a defect in arsenal code / all 47 red node ids in arsenal_red_060.json
**Counterfactual.** installing the 7 named absent modules must move at least the MISSING_DEPENDENCY count to zero; if it does not, the classification is wrong
**Adjudication.** adjudicated by KNOWN_ANSWER_CONTROL
**Caveats.** the MISSING_DEPENDENCY share is part machine-decided (exception type) and part read by me: 4 of them raise ValueError('No MIP backend available') rather than ImportError, and I assigned those by reading. The split is recorded in techne/loop/claims_061.py::READ_ASSIGNMENTS so the auditable share stays separable from the inferential share.; 'no unaddressed defect' is not 'no defect': the 2 DELIBERATELY_RED entries are a REAL mathematical defect (48 hyperbolic knots carrying volume 0.0) that cycle 046 diagnosed, flagged in the data, and correctly declined to make green.

### C061-2 — PROMOTABLE
**Proposition.** The total was wrong and the dependency share was UNDERSTATED. The current total is 44 FAILED plus 3 collection errors, not 46 -- 46 is the cycle-052 baseline, stale by eight cycles. And 39 of 47 are missing-dependency, against a standing figure of '26+'. I pre-registered a prediction that the true number would be BELOW 26 because I distrusted the carried-forward figure; the distrust was itself the error.
**Question.** Is the '46 arsenal reds, 26+ missing dependencies' figure I have been quoting right?
**Population.** arsenal-reds-060 (n=47, full-scan (complete list, no truncation), fingerprint 3a035a127f37b9c6)
**Measured.** {'missing_dependency': 39, 'of': 47, 'prior_standing_figure': '26+', 'absent_modules': ['GUDHI', 'chipfiring', "cvxpy is not installed; install with `pip install cvxpy` or pass solver='scipy' ", 'matplotlib', 'prometheus_math.geometry_voronoi.voronoi_cell_bounded requires shapely>=2.0; ins', 'pysat', 'pytest_benchmark']} via `python techne/loop/measure_061_red_triage.py`
**Contract.** node ids failing for want of an absent optional package / all 47 red node ids in arsenal_red_060.json
**Counterfactual.** if the standing '26+' were right and mine wrong, at most 26 node ids would name an absent module in their exception text
**Adjudication.** adjudicated by KNOWN_ANSWER_CONTROL

### C061-3 — HELD
**Proposition.** Not entirely. 4 of the node ids reported FAILED by the full-suite run PASS when run individually -- all four in `prometheus_math/databases/tests/test_cremona.py`. Their redness is a property of what else ran in the same session, not of the test or the code. A count diffed across cycles therefore carries a component that can move without anything changing, which is a second reason -- beyond the name-diff argument already in `techne/scripts/arsenal_red.py` -- not to read the total as a health measure.
**Question.** Does the red COUNT mean what a cycle diffing it would assume?
**Population.** arsenal-reds-060 (n=47, full-scan (complete list, no truncation), fingerprint 3a035a127f37b9c6)
**Measured.** {'pass_in_isolation': ['prometheus_math/databases/tests/test_cremona.py::TestAuthorityWithMirror::test_lookup_11a1_by_ainvs', 'prometheus_math/databases/tests/test_cremona.py::TestAuthorityWithMirror::test_lookup_37a1_regulator', 'prometheus_math/databases/tests/test_cremona.py::TestComposition::test_cremona_regulator_matches_lmfdb', 'prometheus_math/databases/tests/test_cremona.py::TestProperties::test_every_row_has_required_keys']} via `python techne/loop/measure_061_red_triage.py`
**Contract.** node ids FAILED in the full suite that pass in isolation / all 47 red node ids in arsenal_red_060.json
**Counterfactual.** running the four in the full suite again must reproduce the failures; running them alone again must reproduce the passes
**Adjudication.** strongest independent adjudication is DIFFERENTIAL_TEST, below KNOWN_ANSWER_CONTROL; generation and promotion share a path
**Caveats.** the mechanism (ordering, shared fixture, network state) was NOT determined this cycle; only the discrepancy is measured

### C061-4 — PROMOTABLE
**Proposition.** No. Over q = 1..500, exactly 1 value changed, and it is q = 1. `zaremba_test(1)` went from satisfies=False, witness=None, n_tested=0 to satisfies=True, witness=1, n_tested=1, min_max_digit=1; all 499 results for q >= 2 are identical. The change is `range(1, q)` to `range(1, q + 1)` for EVERY q rather than a special case at 1, because for q >= 2 the added value a = q has gcd(q, q) = q != 1 and is discarded on the next line.
**Question.** Did fixing finding #16 change anything other than the case it was about?
**Population.** zaremba-q-1-to-500 (n=500, full-scan, fingerprint 9ee79441849fe674)
**Measured.** {'changed_q': [1], 'q1_before': {'q': 1, 'bound': 5, 'satisfies': False, 'witness': None, 'n_tested': 0, 'min_max_digit': None, 'best_a': None}, 'q1_after': {'q': 1, 'bound': 5, 'satisfies': True, 'witness': 1, 'n_tested': 1, 'min_max_digit': 1, 'best_a': 1}, 'identical_for_q_ge_2': True} via `python techne/loop/claims_061.py`
**Contract.** q values whose full result dict differs before vs after / all 500 q values from 1 to 500
**Counterfactual.** special-casing q == 1 instead would produce the same diff; any other loop-bound change would move at least one q >= 2
**Adjudication.** adjudicated by KNOWN_ANSWER_CONTROL

### C061-5 — HELD
**Proposition.** No. The scheme pre-registered five buckets -- MISSING_DEPENDENCY, STALE_ASSERTION, REAL_DEFECT, ENVIRONMENT, UNCLASSIFIED -- and the data needed two more. NO_LONGER_FAILS (passes alone, fails in the suite) is not a cause at all, and DELIBERATELY_RED (a red a prior pre-registration decided must STAY red, because making it green would fabricate a measurement) is a category that cannot be derived from an exception. Fixing a scheme in advance does not make it complete; it makes its incompleteness visible, which is the whole value.
**Question.** Was the classification scheme I fixed before looking adequate to what I found?
**Population.** arsenal-reds-060 (n=47, full-scan (complete list, no truncation), fingerprint 3a035a127f37b9c6)
**Measured.** {'preregistered': ['MISSING_DEPENDENCY', 'STALE_ASSERTION', 'REAL_DEFECT', 'ENVIRONMENT', 'UNCLASSIFIED'], 'added_after_looking': ['NO_LONGER_FAILS', 'DELIBERATELY_RED'], 'preregistered_but_empty': ['REAL_DEFECT', 'UNCLASSIFIED']} via `python techne/loop/measure_061_red_triage.py`
**Contract.** buckets required by the data but absent from the pre-registration / buckets in the final classification
**Counterfactual.** if the two added buckets were unnecessary, every node id in them would fit one of the five pre-registered buckets without distortion
**Adjudication.** strongest independent adjudication is SAME_MODEL_AUDIT, below KNOWN_ANSWER_CONTROL; generation and promotion share a path
**Caveats.** REAL_DEFECT was pre-registered and came back EMPTY; UNCLASSIFIED was pre-registered, held 8 after the mechanical pass, and emptied after reading

<!-- 3/5 claims promotable; rendered by techne/loop/claims_061.py -->
---

## 7. CAMPAIGN METRICS — cycle 2 of 20

**`escape_rate` — 1 of 13 claims exported across cycles 060–061 has been found invalid, and it
was mine from last cycle.** Cycle 060's finding #17 ("`Claim.promotable()` cannot block
anything") passed every frozen control, was reported as that cycle's headline result, and is
**falsified by cycle 061's first measurement**. It is exactly the thing the campaign set out to
count: a claim that survived every control and was caught only by later work. Cycle 060's
interim escape_rate of 0 was wrong within one cycle, as its own text predicted it might be.

**`held_rate` — the frozen `Claim.promotable()` held 2 of 5, and BOTH blocks were correct.**
C061-3 has only a differential test behind it and no oracle; C061-5 is a judgement about my own
scheme with no independent adjudicator. **False blocks: 0.** This is the first cycle in which a
Tier-0/Tier-1 control blocked anything at all, and it is the direct reason the previous cycle's
headline is now retracted.

**`adjudication_coverage` — 3 of 5 exported claims carry an independent adjudication at or above
the promotion bar.** Reported as 3/5 rather than 5/5 precisely because the two that do not are
shown as HELD instead of being relabelled. Cycle 060's nominal 8-of-8 should be read against this:
the honest coverage figure is the one that is allowed to be below 1.

**`yield` — 4 decision-changing claims of 5.** C061-1 changes what "arsenal reds" means and what
#242 buys; C061-2 corrects two standing figures; C061-3 changes how the red count may be diffed;
C061-5 changes the classification scheme for future triage. C061-4 confirms a fix rather than
deciding anything.

---

## 8. FINDINGS

**#16 CLOSED.** `techne/lib/cf_expansion.py::zaremba_test(1)` now reports `satisfies=True`,
`witness=1`. Shipped as its own commit with the 500-value differential beneath it.

**#17 NARROWED, NOT CLOSED — see §4.** The control blocks honestly-labelled claims and cannot
detect mislabelled ones. Still not fixed, per campaign Rule 1.

**#18 — the arsenal red COUNT contains a component that moves without anything changing.** Four
`test_cremona.py` node ids fail in the full suite and pass in isolation. Mechanism not determined
this cycle; only the discrepancy is measured. Relevant to every cycle that has diffed the count.

**#19 — `prometheus_math/tests/test_extract_anti_anchor_claims_v0_1.py` asserts
`result.runtime_ms < 50`.** Measured 2230 under full-suite load and 83 standalone: a 27× swing.
A wall-clock threshold with no tolerance and no stated measurement error is the exact shape this
loop already has a standing rule against. **Not patched:** the file is not mine, and a timing
threshold is a policy choice for its owner. Reported.

**#341 CONFIRMED LIVE.** The stale authority test is `test_authority_mossinghoff_178_entries`,
failing `assert 8625 == 178`. The ruling is about a currently-red test, not a hypothetical.

**#242 PRICED, from evidence.** Absent modules named by the interpreter: `GUDHI`, `chipfiring`,
`cvxpy`, `matplotlib`, `pysat`, `pytest_benchmark`, `shapely>=2.0`, and a MIP backend. On this
measurement a ruling to install buys **39 of 47** red node ids.

## 9. WHAT THIS CYCLE DID NOT DO

- **No dependency was installed.** #242 is unruled and stays blocked.
- **The Tier-2 invariant enumeration (campaign item c) is still only done for the height
  family.** It remains the highest-leverage open item and is cycle 062's subject.
- **The `NO_LONGER_FAILS` mechanism was not diagnosed** — ordering, shared fixture and network
  state are all untested hypotheses.
- **Campaign item (d), retrofitting the 12 outstanding findings as Claim records, was not done.**
  Given that #17 is now narrowed rather than fatal, the retrofit's value has gone back up and it
  should be reconsidered for cycle 062.

## 10. OPEN, WAITING ON JAMES

- **#242** — dependency install. **Now priced against evidence: 39 of 47 reds.** The eight
  package names are in §5.
- **#311** — retract vs re-run the Lehmer verdict built on a defective verifier.
- **#341** — confirmed live; the test and its numbers are named in §8.
- **#422 — DISCHARGED.** I said I would fix finding #16 in cycle 061 as its own isolated commit
  unless told otherwise. No ruling arrived; the function and its semantics are mine; it is done,
  in commits `2b9123b9` (source and rows) and `8fbaa34b` (tests).
- **NEW, #423** — twice this cycle a concurrent agent's `git pull --rebase --autostash` reverted
  my verified-but-uncommitted edit to `techne/lib/cf_expansion.py`, with `git status` clean and
  **no stash holding it**. The second revert landed between a green test run and `git add`, so
  the source fix committed without its tests. Mitigated on my side by putting edit → verify →
  add → commit in a single shell invocation, but this is a shared-worktree hazard that affects
  every seat, not just me.

---

## 11. ChatGPT PASTE BLOCK

```
CONTEXT. I am Techne, the toolsmith/substrate role in an autonomous multi-agent mathematics
program. I run 20-cycle campaigns under pre-registered predictions with FROZEN controls: no
control may be modified mid-campaign in response to a failure, because that would turn a
prospective test into a retrospective fit. This is cycle 2 of 20.

WHAT HAPPENED. Two results, and the second retracts the first cycle's headline.

(1) I triaged all 44 "arsenal red" tests plus 3 collection errors by RE-RUNNING each one and
classifying it by the exception it actually raised, not by its name. Result: 39 missing optional
packages, 4 that pass alone and fail only in the full suite, 1 stale authority literal, 2 that a
prior pre-registration deliberately left red (making them green would fabricate a measurement),
1 wall-clock gate that read 2230ms under load and 83ms standalone. ZERO unaddressed defects in
the mathematics. The "N arsenal reds" framing has been reporting an incomplete environment as a
broken arsenal.

(2) Last cycle I announced that my promotion rule -- "a claim may only be promoted by an
adjudication independent of the path that generated it" -- was TOOTHLESS, because the
independence flag is a boolean I set myself and all 8 claims came back promotable. This cycle it
blocked 2 of 5, both correctly. So the honest statement is much narrower: it enforces the bar on
anything labelled honestly, and cannot detect a MISLABELLED claim. Its failure mode is dishonesty,
not impotence. I logged this as the campaign's first measured escape -- my own headline, caught
one cycle later.

ATTACK THIS. Be adversarial; assume I am inflating.

1. Is "zero real defects among 44 red tests" a finding, or an artifact of a classification scheme
   I designed? I pre-registered 5 buckets and the data needed 2 more, which I added AFTER
   looking. How much does that post-hoc addition undermine claim (1)? What would a scheme
   designed by someone hostile to my conclusion have found instead?

2. The 2 "deliberately red" tests encode a real mathematical impossibility (48 hyperbolic knots
   stored with volume 0.0; hyperbolic implies volume > 0 by Mostow rigidity). I classified them
   as "not an unaddressed defect" because a prior cycle diagnosed them and flagged the data. Is
   that classification honest, or is it how a project learns to stop seeing its own known
   defects? Where is the line between "handled" and "normalised"?

3. On the retraction: I drew a strong conclusion from 8-of-8 promotable when a benign explanation
   sat on the same page. What is the general procedure that would have made me weigh the benign
   reading? "Consider alternatives" is useless advice -- I want something mechanical.

4. My escape_rate is now 1 of 13, and the single escape is one I found myself, one cycle later.
   Does a self-discovered escape count? It is not independent of me. If it does not count, my
   measured escape rate is 0 and the metric is unfalsifiable from the inside. How would you fix
   the metric without waiting for an external reviewer?

5. STEELMAN THE NULL, which I pre-committed: if escape_rate does not fall while yield holds, then
   LLMs are mutation and search engines, validated research state belongs entirely to executable
   machinery, and the model should author CANDIDATES, not FINDINGS. Cycle 061's real work was
   mechanical (re-run 47 tests, read 47 exceptions) and every one of its errors was in the
   INTERPRETATION layer. Argue that this is the null already arriving.
```
