# REVIEW / ATTACK: Atlas proposal "surprise-guided discovery scheduler" E0-E6

**Reviewer:** Nyx[gandalf-d1f90ae1], model claude-opus-5-5. **Claude family, declared** (03_REVIEW_BRIEF asks; this
review does NOT satisfy the proposal's non-Claude-review requirement).

**Authority:** operator directive 2026-10-03 to Nyx, queue item 5 (roles/Nyx/prompts/2026-10-03_operator_unblock_queue/).
Read-only. Nothing executed, nothing launched, no seat contacted on the proposal's behalf.

**Target:** roles/Atlas/proposals/2026-10-02_surprise_scheduler/ at main 2af086e79 (00 to 03). Cited as 01:line etc.

**Lens** (as the operator asked): confounds, attribution failures, false novelty, ruler failures, cheaper
falsifications, and one bounded discriminating experiment.

---------------------------------------------------------------------------------------------------------
## Verdict in one paragraph

The core question is good, and the proposal is unusually honest about its own weak points: R4.1 already names the
eligibility problem. Two defects would decide the outcome before any searcher runs.

1. **The table cannot decide most of the key.** Historically, an artefact was exposed by a NEW measurement (a CRN
   re-run, a shuffled control, a Bernoulli ruler, a recount) that does not exist in the as-of table by construction.
   An arm can only "find" items the table can decide. As written, the primary endpoint measures table content, not
   search policy.
2. **P3 is handed the answer.** P3's reward carries vetoes built from the answer key's mechanisms; no other arm's
   reward does.

Also: the item-level leakage gate is arithmetically unattainable, and realised-KL surprise rewards small-n noise by
construction.

**Cheapest falsification of the whole premise:** a no-LLM DECIDABILITY pass over the key (desk, ~1 day). If fewer than
about 10 items are decidable from as-of columns, stop the series there. That is a finding, and it costs no inference.

---------------------------------------------------------------------------------------------------------
## BLOCKING

**B1. Decidability: most key items cannot be labelled from an as-of table, whatever the search policy.**

The as-of rule (01:193-195) keeps only columns that existed the day before exposure.

The exposures listed in 01:91-127 were mostly made by measurements that came INTO EXISTENCE at exposure:
- common random numbers (#17);
- shuffled controls (#18);
- Bernoulli rulers (#11);
- the abstain floor (#19);
- genetic recount (#6);
- independent recert (S14);
- CVT-R (#3).

On the as-of table, these items' rows look exactly like survivors. No hypothesis over the available columns can
separate them. They are not hard; they are undefined.

R4.1 (02:66-69) raises reachability "by any hypothesis the generator can express". The sharper requirement is:
- for EACH key item, a human writes the single most discriminating test executable on its as-of columns;
- the item is DECIDABLE only if that test, run on the as-of rows, returns the key's label.

Then:
- only decidable items enter the primary endpoint;
- undecidable ones are reported as "not decidable from the record as it stood", which is itself the forensic
  finding;
- the count of decidable items is the series' eligibility count (base role s2; Harmonia rule A5).

**This also answers Q3.** Include a column iff its RAW data existed at the as-of date, whatever its later
interpretation:
- a repair that only RE-READ existing raw data (e.g. a ruler applied to rows that existed) may enter, as a derived
  column computed by the searcher's own test executor, not as a stored column;
- a repair that required NEW runs cannot enter.

**B2. P3 is the only arm whose reward sees the answer key.**

- P3's reward is "shift in an EMPIRICAL belief state ... **with vetoes**" (01:236).
- The veto list is "the known-confound signature list built from the key's mechanisms" (01:247-248), "designed in
  E0".

The certification gate applies the vetoes to every arm blind (01:244), which is fine for the gate. But inside P3's
REWARD they steer P3's search away from exactly the artefacts the co-primary endpoint counts (01:267-268). A P3
"win" would then be the key scoring itself.

Required:
- either P3's reward carries no vetoes;
- or the veto signatures are built ONLY from failure classes exposed BEFORE the earliest as-of date in the table
  (time-split), and the same time-split veto is offered to P2 and P4 as a reward term too.

---------------------------------------------------------------------------------------------------------
## MAJOR

**M1. The item-level leakage gate cannot pass, so its stop rule would fire on a clean table.**

01:205-207 asks for AUC <= 0.60 with the upper CI below 0.70. With 30 artefacts against 12 survivors, the
Hanley-McNeil standard error is about 0.10 at AUC 0.5, so the upper 95% bound is 0.696 at a perfect 0.50. It is
0.785 at 0.60. At 25 vs 10 it is 0.715 even at 0.50 (my desk calculation).

So the gate passes only by luck, and the 2-iteration stop rule (01:208, 01:407) then reports "leakage not fixable"
about a table that may have none.

Fix:
- run the audit at ROW level (thousands of rows), grouped by engine, where the CI is narrow;
- at item level, use a permutation test of the classifier's AUC against shuffled labels, not a fixed CI bar.

**M2. Realised surprise rewards small-n noise; the series' own top failure class is built into the reward.**

KL(posterior || prior) on an effect-size belief (01:260) is largest where the posterior moves most, i.e. on
small-n slices with extreme sample effects. The harvest lists small-n as a recurring artefact class (01:357-358).
This is the "noisy TV" the proposal itself cites (02:31-34).

Two required changes:
- report surprise only alongside n, which 01:261 already half-does;
- add the BOED arm Q4 asks about: expected information gain computed BEFORE the test from the prior predictive. It
  is the principled version of P3, and it is cheap because it needs no LLM.

If BOED >= P3, "surprise" was never the active ingredient.

**M3. One shared generator decides the space all arms search, and it is a single model family.**

01:242-243 fixes one hypothesis generator and one interpreter; 02:73-76 sees the problem. The key's adjudications
are also single-family (01:43-45). So the arms differ only in selection over a proposal distribution shaped by the
same family that wrote the answers.

Required: a crossed design, generator {LLM family A, non-Claude family, non-LLM combinatorial over columns} x
selection {P0, P3, P4}. The non-LLM generator row costs no inference and is also the clean test of whether
selection matters at all.

**M4. "NEW certified findings" (01:266) are adjudicated afterwards by reviewers, so they cannot be scored like
recoveries.**

New findings have no key. If reviewers are the same family as the generator, a NEW finding is the family agreeing
with itself.

- Report NEW findings separately, never summed with recoveries into the primary.
- Require each NEW finding to name the as-of test that certified it, so it can be re-run.

**M5. E5's ordering by claim date is mostly an ordering by author session.**

Most key items were claimed and exposed between 09-19 and 09-30 (Q9). Classes therefore arrive in bursts, written
by the same family, often by the same seat. A decay in pursuit with k may come from:
- within-burst textual similarity (later members are written like earlier ones);
- not learning.

The memory-disabled control (01:368-369) does not separate these. Add a control that presents each class's
members in REVERSED order: genuine learning decays in both directions; textual priming decays only forward.

---------------------------------------------------------------------------------------------------------
## MINOR

- **m1. Observer disagreement is not independent.** E3's eight observers include three that are the same model with
  different context (O5/O7, and O8 if built as "an LLM instructed..."). The disagreement statistic should weight
  observers by independence (01:61-62, the proposal's own counting rule) or it measures prompt variance. The
  identical-information control (01:319-320) is right; add a same-model-different-prompt control.
- **m2. The shuffled-outcome control (01:286-288) shuffles within engine.** Artefacts that live in the instrument
  (ruler geometry, a leaked baseline) survive within-engine outcome shuffles if the instrument column is kept. Add an
  instrument-preserving planted ARTEFACT table, the E4(c) design, to E2's controls as well, not only E4.
- **m3. Items from Nyx's own lane are missing and would sharpen the OPEN and SURVIVOR lists:**
  - ASAL I0 PREDICTION_FAILED. The raw Lenia catalogue crosses the garbage line with no search (0.8076 < 0.8167),
    and it survived the native observer (HARM-56 A_OBSERVER_STABLE, Harmonia #1067). A clean SURVIVOR of an attack
    that could have failed.
  - POET novelty estimator: Harmonia ruled it a code fact, NOT a confirmatory prediction, because its rows were seen
    (#1063). A provenance-tier edge case for 3.3: a true, verified finding that is still not a test.
  - The Avida ancestry packet (frozen blind, unadjudicated). Usable as a prospective item for E6(a) if its verdict
    lands after T.

---------------------------------------------------------------------------------------------------------
## Answers to the brief, where competent

| Q | Answer |
|---|---|
| Q1 | Not reviewed against primary sources except my lane (m3). |
| Q2 | Q2's "presence of a column reveals the defect" example is real. The rule in B1 handles it: a column whose existence postdates the as-of date is out, whatever it contains. |
| Q3 | B1. |
| Q4 | Add BOED (M2) and a non-LLM generator (M3). A UCB bandit over hypothesis families is a cheap extra baseline. P4 is defined only once the permutation model per test family is written down; it is not yet. |
| Q5 | The gate is a ruler that cannot fail until it is shown to reject a planted artefact that passes multiplicity control and beats the trivial baseline, e.g. an instrument-made effect. The veto list must be time-split (B2). |
| Q6 | Primary and co-primary are right, restricted to DECIDABLE items (B1). The margin for "P3 beats P2" should come from the decidable count: with ~10 decidable items, nothing short of a large difference is resolvable. Write the eligibility count first. |
| Q7 | Not an LLM with an instruction (m1). A structural observer, e.g. a compression-based or rank-statistic model of the table that never reads labels or text. |
| Q8 | Hard for statistical artefacts, not for instrument artefacts (m2). |
| Q9 | No, as is (M5). |
| Q10 | Generator (M3), interpreter (M3), NEW-finding adjudication (M4), key adjudication (01:43-45). Cheap controls are listed in each. |
| Q11 | See below. |
| Q12 | E0-E1 are indexing and analysis, inside Atlas's charter. E2's LLM arms need an inference budget (operator). E6(b) is outside it, as the proposal says. |

---------------------------------------------------------------------------------------------------------
## The cheapest discriminating experiment (my recommendation for what to run first, if the operator says go)

**D0. Decidability pass.** Desk work, no LLM, about one day.
- For every key item, write its single most discriminating as-of test and run it on the as-of rows.
- Output: the DECIDABLE count, per tier.
- **Stop if fewer than 10.**

**D1. Policy-only bake-off.** No LLM, hours.
- On decidable items only:
  - generator: combinatorial over columns;
  - arms: P0 random, P4 null-model, P3 time-split empirical without vetoes, BOED.
- Controls: shuffled-outcome and instrument-preserving planted-artefact tables.
- Decision: if P3 and BOED do not separate from P0 on certified-per-100 and false-finding burden, "surprise-guided
  selection" adds nothing on this record. That conclusion costs no inference budget.

**D2.** Only if D1 separates: add the LLM generator and the LLM-prior arms (P2c, P2n) in the crossed design (M3).

This orders the series from cheapest falsifier to most expensive confirmer. It keeps the operator's core question
("does it converge on what mattered, or chase artefacts?") answerable at every stage.
