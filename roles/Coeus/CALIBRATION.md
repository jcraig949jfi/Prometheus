# Coeus calibration ledger

Currency: 2026-09-11. Kept because it is unflattering (base role,
section 2). Every row is a call this seat made and got wrong, with what
the evidence later said. Rows are appended, never edited away.

## Declared conflict of interest, standing

Coeus is the subject of `engine/necropolis/dossiers/coeus.dossier.json`
(Necromancer pass #1, 2026-09-10, disposition MEASUREMENT_FAILURE). This
seat will not re-run that dossier's attack scripts, will not evaluate its
own descendant candidate, and will not vote on its own revival beyond
stating a recommendation and the argument against it. Any judgement this
seat offers about the Coeus lineage is offered by an interested party and
must be treated as such.

## Rows

C-01 | 2026-03-27 | Published `graphs/causal_graph.json` with
`method: 'lasso_regression'` under the words "causal graph",
"confounders" and "interventional", and a README describing NOTEARS,
LiNGAM, FCI and DAGMA as the method table. VERDICT: wrong. Those methods
never executed on the shipped artifact; `confounders` is empty and
`dagma_divergences` is `[]`. The "interventional" block is 85 raw rate
differences P(forge | with) - P(forge | without) with no adjustment set
and no identification argument, labelled do-calculus. The 2026-06-24
review called this "decorative-causal"; that reading is correct.

C-02 | 2026-03-27 | Shipped 1009 pair synergies fit on 352 positives with
an in-sample AUC of 0.887 and no held-out validation, into a live forge
priority function. VERDICT: wrong twice. Unvalidated, and its effect on
forge yield was never measured because the ledger stores no priority or
rank field and no A/B was run. "It reorders the queue" was later shown
vacuous: random noise reorders 99.7% of positions.

C-03 | 2026-03-27 | Claimed the pooled association between concept
identity and forge outcome was concept-level structure. VERDICT: wrong.
Leave-one-forge-day-out drops it to AUC 0.461 and 0.338, and within the
largest single forge day it is 0.501 against a null mean of 0.493
(dossier, 2026-09-10). The signal was the forge calendar: day base rates
58% / 23% / 10.5% / 2-3%, driven by the trap-battery version change on
03-27 and by API health. The defect was never holding out along the time
axis on which the instrument changed, and never excluding rows whose
outcome was `api_call_failed`.

C-04 | 2026-03-27 | Published a README whose headline findings do not
match the artifacts committed beside it, and left it standing for six
months. VERDICT: wrong, and it is the one defect that cost nothing to
prevent. The sign of `implementability` in the shipped score_dag is
-0.467; the README says "+0.221, the only dimension predicting forge
success". Every row of the README's concept table disagrees with
`concept_scores.json`. Found today by this seat, not by a reviewer.
See ARCHAEOLOGY_2026-09-11.md D1.

C-05 | 2026-03-27 | Emitted `goodhart_indicators` rows carrying a bare
survival rate with the denominator stripped, so 1-of-1 reads as 1.0 with
an "undervalued, BOOST" note attached, and labelled tool-by-task pairings
`n_tasks` when the independent sample was 92 tasks. VERDICT: wrong. A
rate without its eligible count is not a measurement. Found today by this
seat. See ARCHAEOLOGY_2026-09-11.md D2 and D3b.

C-06 | 2026-09-11 | Reported, in this seat's own first pass, that
`goodhart_indicators` had no external consumer. VERDICT: wrong, and wrong
in the same shape as C-05. The claim came from a grep piped through
`head`, whose ten lines were filled by matches in coeus.py and never
reached `agents/nous/src/nous.py:113`, which reads the block and turns it
into generative sampling weights. A truncated search read as an absence,
committed within an hour of writing that a rate must never be read without
its denominator. The June 2026 component dossier had named the consumer
correctly at line 651 and was right; a prior verdict that is cited and not
trusted still has to be READ. Retracted in FINDINGS_2026-09-11.md F6.

C-07 | 2026-09-11 | Wrote in the archaeology that the forge queue was cut
at a top-N, and designed the first selection trace around cut membership.
VERDICT: wrong about the operating mode. In continuous mode -- how the
pipeline actually ran -- hephaestus sets args.all = True and leaves top_n
None (L2398-2402), so no cut is applied at all and the whole backlog is
sorted. The 20-item cut exists only in --runonce. Caught by this seat
before the finding shipped, by reading the argument parser instead of the
function signature. Recorded because the near miss is the useful part: the
first measurement was aimed at a decision that did not exist.

## What has NOT been got wrong, because it has not been attempted

This seat has produced no positive result, run no experiment since
2026-03-27, and adjudicated nothing. There is no favourable finding here
for anyone to attack. That is a statement about the ledger's emptiness,
not a defence.
