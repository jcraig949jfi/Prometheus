# Kickoff Prompt — Candidate A: clear the truncation confound, then decision-n

**Why this round is short and narrow.** Candidate A produced the program's first working
difficulty gradient (32.5pp span, monotone in deception structure, `UNDECIDED-NEEDS-DECISION-N`)
and its A0 rung is **the first rung ever to land in-band on the standing point rule** (0.500).
But A0 ran at **40% truncation** and A2 at **42.5%**, and A0-vs-A1 (0% truncation) is the exact
comparison the axis rests on. That is the same defect class Ergon itself caught in Step 2 part 1
— *"my token cap was measuring itself"* — recurring rung-correlated instead of arm-correlated.
Nothing in this sweep is interpretable until it is cleared. **§4's stopping rule has NOT fired
and this round cannot fire it:** re-spacing rungs inside a working axis is still Candidate A.

---

## THE PROMPT (paste everything between the rules)

---

You're Ergon @roles/Ergon on M1 — `git pull origin main` first. You are the probe's single
owner (R12). Read `ergon/probe/ledgers/axis_nearmiss_A0-A3_n40.txt` (your own sweep) and
`pivot/KICKOFF_PROMPT_probe_axis_search_terminal_2026-08-17.md` §4 (the stopping rule — in hand,
not fired, and this round cannot fire it).

**Candidate A works.** A0 50.0% / A1 25.0% / A2 17.5% / A3 20.0% — a 32.5pp span monotone in
deception structure, against magnitude (non-monotone) and depth (94.4% mean, r = +0.394). Your
§4.1 negative predicted exactly this: recognition, not execution length. A0's point estimate is
in-band on the standing rule. Two jobs, strictly ordered.

### JOB 1 — Clear the truncation confound. Nothing else is read until this lands.

`truncation_rate` was **0.400 at A0** and **0.425 at A2**, against 0.000 at A1 and 0.100 at A3.
Your own Step-2 finding: a low token cap truncates more where responses are longer, and
truncation is silent, correlated missing data. Here it is correlated with *rung*, and A0-vs-A1
is the comparison the whole axis rests on — so **A0's 50% may be a token budget rather than a
difficulty**, and A2's 17.5% may be over-stated as hard.

- Re-run **A0 and A2** (A1/A3 optional, cheap, and worth it for a clean like-for-like table) at
  a budget where truncation is ~0. Determine that budget by measurement, not by assumption —
  find the length distribution of untruncated responses on this family first; the count task
  over five integers with a per-element test is plausibly far longer than the chain family.
- Report truncation, parse-failure and timeout per rung beside accuracy, as the mandatory
  diagnostics they already are.
- **State plainly whether the axis survives the fix.** If A0 rises with headroom (truncation was
  suppressing it), the axis is *steeper* than measured and the rung spacing needs work. If A0
  holds near 0.500 untruncated, the axis is confirmed as measured and A0 is a genuine in-band
  candidate. Either is a result; the current numbers are neither.

### JOB 2 — A0 at decision-n, under the escalation rule

Only after Job 1. A0 is `UNDECIDED` (interval straddles), and the joint ruling makes
three-valued UNDECIDED **the pre-declared escalation**: re-measure at decision-n, resolving
conservatively into failure.

- **Recompute decision-n yourself.** Charon's 600/rung was derived from *Wilson* widths, and
  your own §3 ruling #3 adopted manifest-level intervals as the correct estimand (47% narrower
  on real data) with the explicit consequence that decision-n does not carry over. Derive it
  against the manifest-level estimand and the dispersion term (movable share ≥ 0.30), and show
  the derivation.
- Apply the **full** band: point estimate in [0.35, 0.60] **and** movable share ≥ 0.30. Harmonia
  B's cheat control killed a rule that controls a mean while blind to dispersion; a rung that
  passes on the mean and fails on movable share is not leveled.
- Bonferroni across whatever rungs you re-measure, per the joint ruling; no sequential stopping.

### If A0 resolves OUT under the full band

The axis still works — the rungs are simply badly spaced, all of A1–A3 sitting *below* the band
rather than above it. That is the opposite problem from the last three rounds and a much better
one. **Add an intermediate rung between A0 and A1** (e.g. semiprimes with one factor small
enough to be found by bounded trial division; composites with a single large factor plus a
moderate one; a mixed count where only some elements are deceptive) and level on that. This is
still Candidate A; **§4 does not fire on rung re-spacing inside a working axis.** Candidate B
(multi-constraint) and §4 remain untouched and in reserve.

### If A0 resolves IN under the full band

The probe has a leveled manifest for the first time. Proceed on
`roles/Ergon/KICKOFF_PROMPT_probe_execution.md` from Step 2 — pre-pass, R7 (D0 only: D0 passed
at 0.383 and stands; D1/D2 are INADMISSIBLE-NO-FAIR-NULL per Charon `1c3b4b4e`), R3 controls
live, then the pilot **at D0 scope**, with D1–D3 reported as the separately-named distance
description carrying no Δ_carry and no verdict class, exactly as you recorded in `a6434d23`.
Remember the measured planning correction: post-lenient-screen usable N is materially below
nominal — size the manifest for the *post-screen* N, and note Harmonia B's structural result
that at one solver post-screen F0 ≤ 0.50 identically.

### Constraints

No new architecture (heredity rule). No spec edits. Every rung measured and committed — a dial
whose effect you did not measure is what killed three axes; a rung whose truncation you did not
check is the same failure one level down. Suite green before push. Commit and push each job;
update `stations/M1_STATUS.md` with the corrected table, the decision-n derivation, and which
branch fired.

**One line to keep in view.** You caught this defect class once already, in the leveling run,
and recorded that it would have corrupted the pilot silently. It reappeared in the one sweep
that finally produced a working axis. That is not carelessness — it is evidence that truncation
is a standing hazard of this family and belongs in the pre-flight checklist for every rung from
here on, not in a post-hoc catch.

---

*Committed by Hephaestus (M3), 2026-08-18. Supplier-only, non-signing. The conflict-bearing
branches (forge trap battery, NL-parsing gap) remain §4 decision items for James and the
co-signers and are not reachable from this round.*
