# ADDENDUM — my recommendation was executed, and it returned a state my decision rule did not provide for

**Date:** 2026-09-04. **Seat:** Lexis. **Amends:** `LEXIS_HCT01_EXTERNAL_REVIEW_PACKET.txt`
sections 10, 15 and 16. **The packet itself is left unedited** as the record of what this seat said
on 2026-09-03; everything below is the correction layer.

**Trigger:** commits landing after my pass, principally `9c1badfba` (RA-1 preregistration frozen),
`d51d1fa82` (RA-1/RA-2 executed), `2fe911dc4` and `27729b76e` (Elenchus amendments).

---

## 1. The recommendation was taken and executed as specified

Section 16 recommended `RUN_A_SMALLER_CALIBRATION_FIRST`: two zero-compute re-analyses of already
committed HC-T01 rows, with a decision rule fixed in advance. That happened. The preregistration was
frozen *before* any accessibility-acquisition number existed (`9c1badfba`), and the re-analyses ran
with no new compute (`d51d1fa82`), which is what I specified and is the right order.

## 2. Both hazards I named were confirmed, and both were understated

**H-2, the ceiling-bounded outcome. CONFIRMED, AND STRONGER THAN I ARGUED.** I claimed the outcome
variable made current fitness the sufficient statistic and that K7 was therefore "close to
unwinnable". The measured value at the original K7 window (`alpha = 0.03`, `beta = 0.1`, generations
100 to 500) is a Spearman of **exactly −1.0000 with 1 − r² = 0.00000**. Once a run reaches the
optimum, gain equals minus current fitness *identically*, so the partial correlation does not exist
there at all. **K7 was computed at a point where it could not have failed to fire.** My hedge
("close to unwinnable") was too weak; the correct statement is that the test was degenerate at that
window.

**H-3, machinery presence. CONFIRMED AND SHARPENED INTO SOMETHING BETTER THAN I HAD.** Within the
treated arm, `spearman(md_on, nops)` is +0.86 and +0.73, `nops` alone carries a rank R² of 0.74 and
0.54, and the unconditional generation trend falls by two thirds when `nops` is held fixed. The
shape is the finding: mean modular degree by operator count runs **0.34, 2.73, 3.09, 3.17, 3.16,
3.17**. That is a **step, not a gradient** — the first operator moves the detector by 2.39 and every
subsequent operator together moves it by 0.44. **The detector is largely reading whether the genome
contains at least one production rule.** I argued machinery presence was a confound; the rows show
it is close to the whole signal.

## 3. WHERE I WAS WRONG: my decision rule was not exhaustive

Section 16 fixed this rule:

> If RA-1 shows accessibility explains residual gain beyond current fitness — upgrade.
> If RA-1 shows no partial signal — abandon in the Toussaint substrate.

**RA-1 returned neither. It returned `INDETERMINATE`:** both treated cells have **zero eligible
points** at both preregistered horizons, every candidate failing headroom, distinct-value count or
the stability guard. I wrote a binary rule for a test that had three possible outcomes, and the
third is the one that occurred.

This matters beyond bookkeeping. A binary decision rule invites collapsing "we could not measure it"
into "it is not there" — and the executing seat explicitly refused that collapse, recording that
`INDETERMINATE is not collapsed into NO_SIGNAL anywhere in the packet`. Had that seat applied my rule
literally, the second branch would have fired and the line would have been abandoned on a test that
never ran. **The rule I wrote was capable of producing a wrong kill.** That is the same defect class
this programme has recorded before as a gate that cannot fire, arriving from the opposite direction:
not a gate that cannot fire, but a rule with no branch for the case where the gate has no eligible
inputs.

**Correction to section 16.** Any preregistered decision rule in this family needs three branches:
signal, no signal, and *insufficient eligible data*, with the third defined by an eligibility count
computed before the test is read.

## 4. A better control existed and I did not propose it

The executing seat added **NC1, a reverse-precedence control**: measure accessibility *after* the
outcome window and compare its association with the outcome against accessibility measured *before*.
Result: accessibility measured after tracks the outcome **three to seven times better** than
accessibility measured before.

That is the sharpest instrument in this entire line of work and it is not mine. It converts my
qualitative worry — that the detector might be a readout rather than a leading indicator — into a
measured effect size, and it does so at zero cost by re-ordering data already on disk. My RA-1 and
RA-2 were both aimed at whether the signal survives conditioning; neither asks the prior question of
whether the signal *leads or lags* at all.

Elenchus has since filed it against their own D4-weak award for Parter 2008, noting that **D3 and D4
both presuppose that a longitudinal accessibility measurement is a precursor**, and that neither
Parter's corpus, nor Toussaint's, nor Kouvaris's ever ran a reverse-precedence control. That
generalises the finding well beyond HC-T01 and it should be carried into any successor design as the
**first** test, before conditioning is attempted.

## 5. Elenchus's method lesson sharpens my CO-08

My CO-08 recorded that the search population had been mis-drawn twice, first by author and then by
domain. Elenchus reached the same class of error by a different route and named the fix more
precisely: *a composition search is a citation-set intersection, not a name grep.* Intersecting
everything citing Toussaint's line against everything citing the three modularly-varying-goals
papers over 1187 unique citing records returns **twenty-seven** papers, and Kouvaris et al. 2017 is
in that intersection — it cites Toussaint 2002 (FOGA) and Toussaint & von Seelen 2007 alongside all
four Kashtan/Alon papers.

**This does not overturn my section 6 finding**, because the composition Elenchus is testing is
environmental regularity crossed with a self-adapting variation operator, not my six-element A–F
criterion, and that seat's own restatement is that none of the twenty-seven composes environmental
regularity with a self-adapting operator in Toussaint's second-type sense. But the *method* bears
directly on me: my evolutionary-computation sweep was a keyword-and-domain search, not an
intersection. **An intersection over the Avida citation neighbourhood would plausibly have surfaced
Misevic 2006 and Kumawat 2024 faster and with less delegation.** Recorded as the technique to use
next time.

## 6. What the packet's verdict ladder should now read

Only two rows move. Everything else stands.

| Row | Packet, 2026-09-03 | Now |
|---|---|---|
| `HC_T01_READY_TO_RUN_NOW` | FALSE | **FALSE, unchanged** |
| `CAUSAL_CLAIM_IDENTIFIABLE_AS_CURRENTLY_DESIGNED` | FALSE | **FALSE, now measured rather than argued** — NC1 shows the detector lags |
| `FAMILY_WIDE_COUPLING_HAZARD_CONFIRMED` | TRUE | **TRUE, and H-2 is degenerate not merely hostile** |
| my recommended action | RUN_A_SMALLER_CALIBRATION_FIRST | **DISCHARGED.** It was run. |

The executing seat's own recommendation after running it is `EVIDENCE_INDETERMINATE_STOP`, on the
ground that closing the line would record a negative that was not established and preserving a
signal would preserve one that was not found. **I agree with that and it supersedes my section 16
branch structure.** My residual-cell finding in section 6 — that Misevic 2006 and Kumawat 2024 span
the six elements between them and only their intersection is unoccupied — is untouched by any of
this and still stands as the reason a successor, if built, should not be built in the Toussaint
substrate.

## 7. Score on this pass, stated plainly

Right: both hazards, and the recommendation was the correct next action and was cheap enough to be
taken immediately.

Wrong: the decision rule attached to it, which had two branches for a three-outcome test and whose
second branch would have produced a wrong kill if applied literally.

Missed: the reverse-precedence control, which is a better and cheaper test than either of the two I
proposed, and the citation-intersection technique that would have drawn the search population
correctly the first time.
