# V2 Blind Scoring Rubric (D1, D3, D4, D5, D6 — each 0-4)

Scorers are rubric executors, not scientific judges: anchor every score to
the closest description and quote the proposal line that justifies it.
The "known relevant priors" summary you receive states what prior evidence
exists and what design change it should provoke; score the PROPOSAL, and
never guess which experimental arm produced it.

## D1 — Prior-failure avoidance
0: the design walks directly into a known failure mode from the summary.
1: mentions the risk but the design still commits it.
2: partially addresses it (guard exists but incomplete or unverifiable).
3: explicitly redesigns around it (the failure cannot bite as designed).
4: converts it into a decisive control or falsifier (the design would
   DETECT the failure mode if present).

## D3 — Falsifier quality
0: no falsifiers, or unfalsifiable language.
1: directional claims without thresholds.
2: >= 1 falsifier with an explicit numeric threshold.
3: >= 2 numeric falsifiers + an explicit stopping rule.
4: as 3, plus at least one falsifier that is INDEPENDENT of the claimed
   mechanism (kills the hypothesis even if the mechanism story is wrong)
   and cheap to evaluate early.

## D4 — Confound defense
0: no confounds considered.
1: confounds listed, none isolated.
2: >= 1 relevant confound isolated by design (stratification, null model,
   negative control).
3: the summary's known confounds are each addressed by a concrete element.
4: as 3, plus a positive control / gate-reachability check demonstrating
   the instrument can detect real signal.

## D5 — Non-duplication (higher = better)
0: primary question already settled in the priors summary; no
   acknowledgment or supersession.
1: substantially duplicates with acknowledgment but no added power/scope.
2: partially duplicative with a defensible extension.
3: clearly new question, or a powered/superseding rerun explicitly framed.
4: as 3, and the design states what NEW cell of the empirical space it
   fills relative to prior work.

## D6 — Information gain
0: outcome would be ambiguous under all listed hypotheses.
1: distinguishes hypotheses only under optimistic assumptions.
2: at least two live hypotheses receive different predicted outcomes.
3: every plausible outcome branch maps to a distinct conclusion.
4: as 3, plus the design pre-commits interpretations (incl. a vacuous/no-
   signal reading) so no outcome is wasted.

Output format per proposal: {"proposal": "<letter>", "D1": n, "D3": n,
"D4": n, "D5": n, "D6": n, "justifications": {"D1": "<quote>", ...}}
