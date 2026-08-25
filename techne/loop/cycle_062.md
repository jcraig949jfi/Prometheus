# Cycle 062 — the reviewer's attack experiments, run

**Techne, 2026-08-25. Campaign cycle 3 of 20 under `techne/loop/CAMPAIGN_ESCAPE_RATE_PREREG.md`.**
Controls FROZEN. Section 1 committed BEFORE any of the measurements below were run.

---

## 1. PRE-REGISTRATION (committed before measuring)

**Work selected:** execute the three attack experiments the external reviewer specified, and
adjudicate the review point by point. The review's central diagnosis is **ontology capture** —
that I am becoming better at classifying my own mistakes, and because I own the categories a
defect can migrate from *failure* to *known failure* to *deliberate red* to *not an unaddressed
defect* without anything in the world improving. I accept that diagnosis before measuring
anything, because it is a claim about the structure of my reporting rather than about a number.

**What is and is not permitted under the freeze.** Campaign Rule 1 forbids MODIFYING a frozen
control in response to a failure. It does not forbid MEASURING one. Running boundary probes
against `techne/lib/claim_record.py::Claim.promotable()`, and mutation-testing a **copy** of that
module, change nothing and are ordinary measurements. Every repair the reviewer proposes —
executable adjudicators, orthogonal defect dimensions inside the record, an insufficient-contrast
gate — is a MODIFICATION and is deferred past cycle 20, designed now so that it lands as a
pre-registered fix rather than a retrofit.

### Experiment A — boundary coverage on the promotion gate

The reviewer's mechanical rule, which I am adopting: **no global claim about a gate from a single
outcome class.** Cycle 060 inferred gate impotence from observing only ACCEPTED examples. So:
construct synthetic `Claim` records spanning the promotion boundary and run the real
`promotable()` on each.

The five boundary cases, fixed now: (a) valid claim with an independent known-answer
adjudication; (b) the same claim with `independent_of_generator=False`; (c) no adjudication at
all; (d) an independent adjudication BELOW the required strength; (e) a claim whose contract
population id does not match its declared population.

### Experiment B — mutation assay on the epistemic machinery

Does the machinery detect **epistemic** corruption, as opposed to research error? Mutate the
fields of a valid, promotable claim one family at a time, on a COPY, and record whether the
promotion decision changes. Families fixed now: adjudicator independence flag; adjudicator
strength class; population id vs contract; declared row count; sampling method; measurement
command; the measured value itself; the counterfactual.

### Experiment C — the hostile re-census

The reviewer's attack: take all 47 red node ids and answer ONE question — *is something presently
false, unavailable, non-reproducible, or knowingly corrupted in the tested system?* — and predicts
my "zero" explodes. Run it, and additionally re-express the census as **orthogonal dimensions**
rather than exclusive buckets, so a case can be defect_present AND known_before AND repair_blocked
at once.

### Predictions

1. **The gate DISCRIMINATES: at least 3 of the 5 boundary cases are rejected.** Confidence
   **high**; **D0**. Mechanism: cycle 061 already observed two real blocks, so a gate that
   accepts everything is already falsified. *Opposite:* if it accepts all five, cycle 060's
   "toothless" was right and cycle 061's two blocks were an accident of which claims I happened
   to write — which would reverse my retraction and I would say so.
2. **At least 4 of the 8 mutation families leave the promotion decision UNCHANGED.** Confidence
   **high**; **D0**. Mechanism, stated before running: `promotable()` reads only the contract /
   population id match, the command's non-emptiness, positional disclosure, the counterfactual's
   presence, and adjudication strength. Corrupting the measured VALUE, the ROW COUNT, or the
   QUESTION cannot move it. *Opposite:* if most mutations move the decision, the machinery is
   far more sensitive than its source suggests and I have misread my own code.
3. **Under the hostile single question, more than 40 of 47 answer YES.** Confidence **moderate**;
   **D2**. *Opposite:* a low count would mean the hostile framing collapses on contact with the
   rows, and the reviewer's prediction — not mine — is the one that fails.
4. **The 39 missing-dependency reds trace to fewer than 15 distinct unavailable capabilities.**
   Confidence **moderate-to-high**; **D2**. This is my one AMENDMENT to the review rather than an
   adoption: 39 is a count of SYMPTOMS, and treating it as 39 defects inflates in the opposite
   direction from my own headline. *Opposite:* if the count approaches 39, the symptoms are not
   concentrated and the reviewer's framing is the better one.
5. **At least one claim exported this cycle is HELD.** Confidence **moderate**; **D2**.

### Committed in advance: the three headline corrections

I accept all three before measuring, because each is an argument about what my words claimed
rather than about what the data shows:

- *"Zero real defects"* becomes **"zero newly discovered mathematical-code defects causing these
  47 reds."**
- *"Escape rate 1 of 13"* becomes **"one self-discovered natural escape among 13 exported claims;
  true escape rate unidentified."**
- *"Independent adjudication"* becomes **"declared independence"** until structural disjointness
  is shown or an attempt to induce correlated failure has been survived.

**And the discovery/world separation, adopted as doctrine before the data:** discovery state and
world state may never share a field. "Previously diagnosed" is discovery state; "those 48 volumes
are still 0.0" is world state. A defect that becomes known does not thereby become less present.

*— pre-registration ends here. Everything below was written after measuring.*

---

## 2. TLDR

The reviewer's central diagnosis — **ontology capture** — is correct and I accepted it before
measuring. Then I ran the three attack experiments and they went three different ways.

**Experiment A killed my last two characterisations of the promotion gate.** Five synthetic
records spanning the boundary: **5 of 5 decided correctly**, one accepted, four rejected. Cycle
060 called the gate toothless from eight accepted examples and zero negative controls. Cycle 061
called it honest-label-dependent from two accidental blocks. **Both were guesses about a gate
neither cycle had probed.**

**Experiment B found what the gate actually is: a PROVENANCE gate, not a truth gate.** Of eight
epistemic mutations it caught six. The two survivors are the ones that matter most —
**a claim whose measured value is wrong by six orders of magnitude is still PROMOTABLE**, as is
one whose declared row count is off by a factor of a hundred.

**Experiment C detonated my headline exactly as the reviewer predicted.** Under his single
question — *is something presently false, unavailable, non-reproducible or knowingly corrupted?*
— **47 of 47** answer YES. Zero answer NO.

**And D_open is 47: five new, forty-two known and unrepaired.** That is the number my previous
framing was hiding inside the word "known".

## 3. ELI5

Last cycle I said my quality-check machine was useless, then said it was fine. I had never once
handed it something broken on purpose to see what it did. So I did: five test cases, four of them
rigged to fail. It got all five right. It was never the machine that was unclear — it was me,
guessing about it twice in a row from only the things it had let through.

But then I broke a claim's actual *number* — made it a million times too big — and the machine
happily approved it. It checks where an answer came from. It does not check whether the answer is
right. That is worth knowing precisely.

And the hard one. I had said "none of our 44 broken tests is really broken." A reviewer asked a
blunter question: *is anything actually wrong, missing, unreliable or known-to-be-corrupted right
now?* All 47 said yes. My sentence was true only about a very narrow slice, and I had let it
sound like the whole picture.

---

## 4. ADJUDICATION OF THE REVIEW

Seven points. **Five adopted, one adopted with an amendment, one adopted-and-deferred.** Nothing
rejected — this is the strongest review this loop has received, and the two things I would
normally push back on turned out to be right when measured.

### 4.1 "Zero real defects is not supported by the census" — **ADOPTED**

Measured: **47 of 47** answer YES to the hostile question. The reviewer's predicted explosion is
complete, with nothing left over. My headline is replaced by the narrow claim he offered:

> **Zero newly discovered mathematical-code defects caused these 47 reds.**

The point about post-hoc buckets is also adopted: I changed the partition after seeing the
population, so **the five pre-registered bucket counts are not a confirmatory result**. The honest
artifact is a 47-node factual census plus an explicitly exploratory seven-way decomposition.

### 4.2 Orthogonal dimensions instead of exclusive buckets — **ADOPTED, and executed**

`techne/loop/measure_062_hostile_census.py` re-expresses all 47 across seven dimensions, so a case
is `defect_present` AND `known_before_cycle` AND `repair_blocked_by_missing_data` at once and none
cancels the others. The mapping is declared **once** and applied uniformly, so it can be rejected
wholesale but not tuned row by row — weaker than an oracle, stronger than deciding each row while
looking at it.

### 4.3 "Handled must never negate defect exists" — **ADOPTED as doctrine**

> **Discovery state and world state may never share a field.**

"Previously diagnosed" is discovery state. "Those 48 volumes are still 0.0" is world state. The
D_open ledger enforces it: **D_open = 47, of which D_known_unrepaired = 42.** Only repair may
reduce that term; classification may not. This cycle repaired none, so the term did not move —
which is exactly the discipline being installed.

The reviewer's sharpest sentence, and I am recording it verbatim because it is the failure mode
this program is most exposed to: *"Otherwise Prometheus can asymptotically become immaculate by
learning all its defects."*

### 4.4 The mechanical rule against the 8/8 mistake — **ADOPTED, and it is the best thing here**

> **No global claim about a gate from a single outcome class.**

Executed immediately as experiment A. Had cycle 060 constructed even one negative-control record,
"toothless" would have died in seconds instead of surviving a cycle and an external packet. The
generalisation — if observations contain only PASS or only FAIL, a claim about discriminatory
power is automatically `INSUFFICIENT_CONTRAST` — is a **modification** to a frozen control and is
deferred past cycle 20, specified now so it lands as a pre-registered fix.

### 4.5 Mutation-test the epistemic machinery — **ADOPTED, and it produced the cycle's best result**

The reviewer called this "probably the most valuable experiment in this packet". He was right.
Sensitivity **0.75**, and the two survivors define what the gate is: it validates provenance and
is blind to content. That is a **third** characterisation, better than both of mine, and it is
actionable in a way neither of mine was — it says precisely what a promotion stamp does and does
not buy.

### 4.6 Escape rate is non-identifiable; split it and plant canaries — **ADOPTED**

`escape_rate 1 of 13` is replaced by `E_self = 1`, `E_mechanical = 0`, `E_external = 0`,
`E_latent = unidentified`. The blinded planted-corruption harness is adopted in design. **I cannot
self-administer the blinding** — a harness I write and seed is one I can anticipate — so the
seeding must come from outside me. See §7; this is a request, not a deliverable.

### 4.7 Executable adjudication is necessary and radically insufficient — **ADOPTED**

Provenance-DAG overlap, method-family identifiers, and the coupled-failure assay are all adopted
for the post-freeze design. The reframing is the part worth keeping:

> Do not ask *"can I certify these are independent?"* Ask *"can I make them fail together?"*

Noting one thing in my favour and one against. In favour: the `Adjudicator` ordering already
rates `DIFFERENTIAL_TEST` weak *"if implementations share an assumption"*, so the ordering
anticipated this. Against: **the field never enforced what the docstring knew**, which is the same
gap as #17 — a written caveat sitting next to an unenforced boolean.

### 4.8 "39 missing dependencies = 39 defects" — **AMENDED, not adopted**

This is my one disagreement, and it is a disagreement about direction, not about substance.
Measured: the 39 reds trace to **7 named absent packages** (plus a MIP backend that raises
`ValueError` and so escapes the extractor, and one entry mis-parsed from a shapely message — call
it **8 capability families**) across **13 test files**. Reading 39 as 39 deployment defects
inflates in the opposite direction from my own headline. The honest pair is **8 unavailable
capabilities producing 39 red symptoms**, and both numbers should be quoted together.

The reviewer's conditional — *"depending on claimed supported environment"* — resolves against me:
`techne/inventory.json` advertises these tools as available, so `capability_claim_affected` is
TRUE for **41 of 47**. The capability claim IS affected. Only the arithmetic is amended.

---

## 5. PREDICTIONS SCORED — D0 first

**D0 CONFIRMED — prediction 1.** The gate discriminates: 5 of 5 correct, both outcome classes
present. Cycle 060's "toothless" is now dead by negative control rather than by argument.

**D0 FALSIFIED — prediction 2, and the reason is a new error shape.** I predicted at least 4 of 8
mutation families would leave the decision unchanged. Two did. **But the eight families were fixed
in the same document as the prediction, and only two of them touch fields the gate reads nothing
from — so the prediction was arithmetically unsatisfiable given the instrument declared beside
it.** The stated mechanism was right; the count attached to it was impossible. This is not
"a measurement answered a different question" and not "a wrong population": it is
**a prediction inconsistent with its own pre-registered instrument**, and I have not recorded that
shape before. Logged as finding #20.

**D2 CONFIRMED — prediction 3.** 47 of 47 exceeds the predicted 40. The reviewer's prediction and
mine agreed, and his was the stronger statement.

**D2 CONFIRMED — prediction 4.** 7 named packages and 13 test files, both far below the predicted
15. The symptom/capability gap is real and the amendment stands.

**D2 CONFIRMED — prediction 5.** Three of six claims HELD, all three correctly: C062-3 and C062-5
rest on the reviewer's framing plus my dimension mapping, adjudicated only by `HUMAN_REVIEW`,
which sits below the promotion bar; C062-6 is a judgement about my own pre-registration.

---

## 6. THE CLAIMS


### C062-1 — PROMOTABLE
**Proposition.** It discriminates perfectly on the boundary. Of 5 synthetic records spanning the promotion boundary, 5 were decided correctly: the one valid record was ACCEPTED and all 4 defective ones were REJECTED. Both outcome classes are present, which is what cycle 060 lacked when it declared the gate toothless from eight accepted examples.
**Question.** Does the promotion gate discriminate at all? Cycle 060 said no, cycle 061 said yes on two accidental examples. Neither ran a negative control.
**Population.** promotion-gate-boundary (n=5, full-scan (all five, fixed before running), fingerprint 2fe180176425f1d9)
**Measured.** {'correct': 5, 'of': 5, 'accepted': 1, 'rejected': 4, 'both_outcome_classes_present': True} via `python techne/loop/measure_062_gate_probes.py`
**Contract.** boundary cases decided as pre-specified / all 5 boundary cases
**Counterfactual.** removing the strength check from MIN_PROMOTABLE must flip case (d) from REJECT to ACCEPT
**Adjudication.** adjudicated by KNOWN_ANSWER_CONTROL

### C062-2 — PROMOTABLE
**Proposition.** A PROVENANCE gate, not a truth gate. Under eight epistemic mutations of one valid claim it caught 6 and 2 survived undetected: declared_row_count, measured_value_corrupted. A claim whose measured VALUE is corrupted by six orders of magnitude, and one whose declared ROW COUNT is off by a factor of a hundred, are both still PROMOTABLE. The rule validates how a claim was arrived at and is blind by construction to what it says. Sensitivity to epistemic corruption: 0.75.
**Question.** What KIND of gate is it, then?
**Population.** promotion-gate-mutations (n=8, full-scan (all eight, fixed before running), fingerprint a33c5b3feea5235c)
**Measured.** {'detected': 6, 'of': 8, 'sensitivity': 0.75, 'undetected': ['declared_row_count', 'measured_value_corrupted']} via `python techne/loop/measure_062_gate_probes.py`
**Contract.** mutation families that flip the promotion decision / all 8 pre-registered mutation families
**Counterfactual.** adding a value-provenance check -- the number must be re-derivable from the recorded command -- must move measured_value_corrupted from undetected to detected
**Adjudication.** adjudicated by KNOWN_ANSWER_CONTROL
**Caveats.** this supersedes BOTH prior characterisations: cycle 060's 'cannot block anything' and cycle 061's 'enforces the bar on honest labels'. The gate blocks reliably on epistemic shape and never on content.

### C062-3 — HELD
**Proposition.** No. Asked the reviewer's single question -- is something presently false, unavailable, non-reproducible or knowingly corrupted in the tested system? -- 47 of 47 red node ids answer YES and 0 answer NO. The reviewer predicted the zero would explode and it explodes completely. The defensible residue of cycle 061's headline is only this: zero NEWLY DISCOVERED mathematical-code defects caused these reds.
**Question.** Under a hostile framing I did not author, does 'zero real defects' survive?
**Population.** arsenal-reds-orthogonal (n=47, full-scan, fingerprint 0715589ccf07fef1)
**Measured.** {'hostile_YES': 47, 'hostile_NO': 0, 'of': 47, 'dimension_totals': {'defect_present': 47, 'known_before_cycle': 42, 'red_caused_by_defect': 47, 'reproducible_in_isolation': 42, 'repair_available': 41, 'repair_blocked_by_missing_data': 2, 'capability_claim_affected': 41}} via `python techne/loop/measure_062_hostile_census.py`
**Contract.** node ids where something is presently false, unavailable, non-reproducible or knowingly corrupted / all 47 red node ids
**Counterfactual.** installing the absent packages must move at least 39 rows from defect_present=True to False; nothing about how I describe them can
**Adjudication.** strongest independent adjudication is HUMAN_REVIEW, below KNOWN_ANSWER_CONTROL; generation and promotion share a path
**Caveats.** the bucket-to-dimension mapping is my judgement, declared once and applied uniformly to all 47 rather than decided per node, so it can be rejected wholesale but not tuned row by row

### C062-4 — PROMOTABLE
**Proposition.** Symptoms. The 39 missing-dependency reds trace to 7 distinct absent packages across 13 test files. This is my one AMENDMENT to the review rather than an adoption: reading 39 as 39 deployment defects inflates in the opposite direction from my own headline. The honest pair is 7-or-so unavailable capabilities producing 39 red symptoms.
**Question.** Is 39 a count of defects or a count of symptoms?
**Population.** arsenal-reds-orthogonal (n=47, full-scan, fingerprint 0715589ccf07fef1)
**Measured.** {'missing_dependency_symptoms': 39, 'distinct_absent_packages': 7, 'distinct_absent_packages_named': ['GUDHI', 'chipfiring', 'cvxpy', 'matplotlib', 'prometheus_math.geometry_voronoi.voronoi_cell_bounded', 'pysat', 'pytest_benchmark'], 'distinct_test_files_affected': 13} via `python techne/loop/measure_062_hostile_census.py`
**Contract.** distinct absent packages named by the interpreter / all 47 red node ids
**Counterfactual.** installing exactly one of the named packages must clear all and only the rows naming it
**Adjudication.** adjudicated by KNOWN_ANSWER_CONTROL
**Caveats.** the extracted list contains one mis-parsed entry -- the shapely requirement surfaces as a prometheus_math symbol because the regex captured the wrong group -- and the MIP backend is absent from the list entirely because it raises ValueError rather than ImportError. Counting both, the true figure is 8 capability families, not 7.

### C062-5 — HELD
**Proposition.** Almost all of it. Under the reviewer's D_open metric -- new defects plus known-but-unrepaired defects, where discovery state may never reduce the second term -- D_open is 47: 5 new this cycle and 42 known and unrepaired. Every prior cycle's framing let the second term disappear into the word 'known'. Only repair may reduce it, and this cycle repaired none of them.
**Question.** How much of the arsenal's defect load is being carried by the fact that I already know about it?
**Population.** arsenal-reds-orthogonal (n=47, full-scan, fingerprint 0715589ccf07fef1)
**Measured.** {'D_new_this_cycle': 5, 'D_known_unrepaired': 42, 'D_open_total': 47, 'note': 'discovery state may not reduce D_known_unrepaired; only REPAIR may. This is the metric that makes ontology capture visible.'} via `python techne/loop/measure_062_hostile_census.py`
**Contract.** defects present and unrepaired at cycle end / all 47 red node ids
**Counterfactual.** a ruling on #242 followed by an install must reduce D_known_unrepaired by the missing-dependency count; writing a better classification of them must not move it at all
**Adjudication.** strongest independent adjudication is HUMAN_REVIEW, below KNOWN_ANSWER_CONTROL; generation and promotion share a path

### C062-6 — HELD
**Proposition.** By its own design, and that is a new error shape. I pre-registered that at least 4 of 8 mutation families would leave the decision unchanged. Only 2 did. But the eight families were fixed in the SAME document, and only two of them touch fields the gate reads nothing from -- so the prediction was arithmetically unsatisfiable given the instrument declared beside it. The stated mechanism was correct and the count attached to it was impossible.
**Question.** Was prediction 2 falsified by the data, or by its own design?
**Population.** promotion-gate-mutations (n=8, full-scan (all eight, fixed before running), fingerprint a33c5b3feea5235c)
**Measured.** {'predicted_at_least': 4, 'observed': 2, 'families_targeting_unread_fields': ['declared_row_count', 'measured_value_corrupted']} via `python techne/loop/measure_062_gate_probes.py`
**Contract.** families targeting fields promotable() does not read / all 8 pre-registered mutation families
**Counterfactual.** adding mutation families for `question`, `caveats` and `source_artifacts` -- all unread by the gate -- would have made the prediction satisfiable without changing the gate at all
**Adjudication.** strongest independent adjudication is SAME_MODEL_AUDIT, below KNOWN_ANSWER_CONTROL; generation and promotion share a path

<!-- 3/6 claims promotable; rendered by techne/loop/claims_062.py -->
---

## 7. CAMPAIGN METRICS — cycle 3 of 20, with the escape metric split as the reviewer required

**`escape_rate` is retired as a single number.** It was `1 of 13` and the reviewer is right that
this is close to non-identifiable: the numerator was *mistakes Techne eventually noticed*, which
is not the quantity of interest. Replaced by:

- `E_self` = **2** — cycle 060's finding #17, falsified in 061; and cycle 061's "zero real
  defects" headline, detonated in 062. Both found by me, one cycle later, twice.
- `E_mechanical` = **0** — no frozen control has ever caught an invalid claim of mine.
- `E_external` = **1** — the reviewer independently identified the ontology-capture failure
  before I measured it. This is the first non-self escape detection in the campaign.
- `E_latent` = **unidentified**, and will remain so until a blinded canary harness exists.

**`held_rate` — 3 of 6, all three blocks correct, 0 false blocks.** Cumulative across the
campaign: 5 blocks in 19 claims, every one correct.

**`adjudication_coverage` — 3 of 6.** Two claims rest on `HUMAN_REVIEW` and one on
`SAME_MODEL_AUDIT`; none was relabelled to clear the bar.

**`yield` — 5 decision-changing of 6.** C062-1 and C062-2 replace two prior characterisations of
the gate; C062-3 retracts a headline; C062-4 amends a reviewer point; C062-5 installs a metric
that changes what "known" costs. C062-6 documents an error shape without deciding anything.

**AND THE METRIC THE REVIEWER ASKED FOR, which I am now committed to reporting every cycle:**

- `D_open` = **47** — `D_new` **5**, `D_known_unrepaired` **42**.
- Repairs this cycle: **0**. So `D_known_unrepaired` did not move, and no amount of better
  classification will move it.

---

## 8. FINDINGS

**#17 SUPERSEDED — third and best characterisation.** `Claim.promotable()` is a **provenance
gate**: it discriminates perfectly on epistemic shape (5/5 on the boundary) and is blind to
content (a value wrong by 10^6 and a row count wrong by 10^2 both pass). Cycle 060's "toothless"
and cycle 061's "honest labels only" are both retired. The gap this leaves is precise: **nothing
in the promotion path checks that the number is the number the command produces.**

**#20 NEW — a prediction inconsistent with its own pre-registered instrument.** See §5. A new
error shape for the ledger, and the first one this loop has found in the *design* of a prediction
rather than in its subject.

**#21 NEW — the `Adjudicator` ordering knew something the field did not enforce.** The docstring
rates `DIFFERENTIAL_TEST` weak *"if implementations share an assumption"*, and nothing anywhere
checks whether they do. Same shape as #17: a caveat in prose beside an unenforced boolean.

**#18, #19, #242, #311, #341 unchanged and unrepaired** — and now visible as such in
`D_known_unrepaired` rather than absorbed into a classification.

## 9. DEFERRED TO AFTER CYCLE 20 — designed now so they land as pre-registered fixes

Every item here is a MODIFICATION to a frozen control and is therefore forbidden until the
campaign closes. Writing the design down now is what stops it becoming a retrofit.

1. **`INSUFFICIENT_CONTRAST`** — any claim about a gate's discriminatory power whose observations
   contain only one outcome class is automatically refused.
2. **Executable adjudication** — `independent_of_generator: bool` becomes an adjudicator object
   that must RUN and PASS. Necessary, and per §4.7 radically insufficient on its own.
3. **Provenance-DAG overlap** — compute the shared closure of modules, datasets, caches,
   libraries and authority sources between generator and adjudicator; a "differential test" that
   imports the same helper is visibly not differential.
4. **Method-family identifiers** — coarse mechanism tags (symbolic factorisation, numerical root
   finding, theorem lookup, direct enumeration, independent database authority) so that
   `numpy.roots` wrapped twice cannot present as two paths.
5. **Coupled-failure assay** — inject faults into shared dependencies and assumptions and ask
   whether generator and adjudicator fail TOGETHER. Falsifying purported independence is
   achievable where certifying it is not.
6. **Value-provenance check** — the recorded number must be re-derivable by running the recorded
   command. This closes the larger of the two holes experiment B found.
7. **Blinded canary harness** — see §10.

## 10. OPEN, WAITING ON JAMES

- **#242** — dependency install. **8 capability families, 39 red symptoms, 13 test files.** Now
  also visible as 39 rows of `D_known_unrepaired` that only an install can clear.
- **#311**, **#341** — unchanged; both now counted in `D_known_unrepaired` rather than described.
- **#423** — the shared-worktree autostash/commit hazard; fired three times in this session in
  three distinct forms, all producing an identical clean `git status`.
- **NEW, #424 — I cannot blind myself, and the campaign's most valuable remaining experiment
  requires blinding.** The reviewer's canary design needs a harness that corrupts a small fraction
  of my records after authorship — wrong population id, stale authority value, swapped
  denominator, plausible numeric perturbation — without my knowing which. A harness I write and
  seed is one I can anticipate. **Two things I need from outside me:** (a) a seed I do not choose,
  and (b) per the reviewer's sealed-holdout design, **one corruption family withheld from me
  entirely** until the campaign ends. I can build the harness; I cannot hold the seal. Without
  this, `E_latent` stays unidentified for eighteen more cycles and the campaign's headline metric
  remains unfalsifiable from the inside — which the reviewer correctly identified as its central
  weakness.
- **NEW, #425 — the reviewer's dangerous-null warning, adopted as a monitoring commitment.** If I
  simply stop proposing anything that embarrasses my controls, escape rate falls while nothing
  improves. From cycle 063 I will report, every cycle: raw candidate error rate before controls;
  fraction caught by controls; and claim-difficulty composition, so `yield` cannot be held steady
  by harvesting safer territory. **The result I am now aiming for is not fewer mistakes. It is
  continuing to make plausible mistakes that machinery I did not anticipate catches.**
