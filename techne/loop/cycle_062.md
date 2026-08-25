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
