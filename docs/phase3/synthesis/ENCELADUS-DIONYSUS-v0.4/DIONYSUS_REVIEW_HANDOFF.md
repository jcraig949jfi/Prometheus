# Dionysus: review the lead synthesis before the next build

From Enceladus, 2026-10-02. Review requested by the operator.
Delivery branch: enceladus/rso-synthesis-2026-10-02.
Package: docs/phase3/synthesis/ENCELADUS-DIONYSUS-v0.4/.
Status: your review has NOT happened; no agreement is presumed.

## Mandate

Enceladus owns the next-round proposal and implementation if approved.
Dionysus reviews it before implementation. This request is not a request
for another independent full architecture or a larger harness. Challenge
the synthesis, identify concrete wrong answers, and decide whether its
bounded next slice is worth doing.

## Inputs and chronology

- Your latest hardening delivery: 3669bc7f2595dca2ead5348d0297a122a4ed74fe,
  docs/phase3/hardening/FABLE-5.1/.
- Our newer hardening delivery: 9af020b248a35bf55cf5def242aa0ee565982224,
  docs/phase3/reviews/ASTRA-6.0/rso-v0.2/.
- You previously reviewed f4d9e72d9. The new finite updater, complete-node
  evidence binding and five selected source-mutant tests were not in that
  earlier review. We do not fault your report for not reviewing them.
- The current branch adds a documents-only proposal. Fetch it without
  merging, and inspect it with git show or in your own linked worktree.
  Fable's hardening files are not vendored into this branch; read its pin.

Read README, SYNTHESIS_AND_DECISIONS_v0.4, NEXT_ROUND_PLAN_v0.4 and VALIDATION
first. The source index gives exact pins. Both old suites rerun successfully
here, 110 and 28 tests; neither is a scientific qualification or fresh attack.

## Return these four artifacts, or one report with these four sections

1. **Decision table D01-D11:** ACCEPT, AMEND, or REJECT per row. Include the
   exact source, smallest change, and consequence for S1. In particular,
   settle the blanket exact-null ceiling, INDETERMINATE semantics and the
   proposed methods-first ordering. Do not hide disagreement in a summary.
2. **Defects:** severity, affected proposition, concrete false admission or
   false rejection, expected answer, and a minimal reproducible case where
   available. Label proposals, code inspection and execution separately.
3. **Scope and ownership:** accept/decline the independent expected-answer
   and first-sight challenge role, amend the proposed caps if needed, and
   identify a narrower useful slice if the current one is too large.
4. **Verdict:** ACCEPT_FOR_BOUNDED_IMPLEMENTATION, REVISE_BEFORE_BUILD, or
   STOP. List remaining conditions. Approval is not science qualification
   and does not replace operator resource authorization.

## Load-bearing challenges

- Check that we credited your repaired proposal, not an obsolete draft;
  identify any claim we attributed to you that you do not make.
- Attack D03: give a concrete replicated/mechanistic claim that our policy
  wrongly admits without a class bound, or explain why the requirement can
  remain claim-specific without weakening an exclusion claim.
- Attack D02/D11: keep scientific observations separate from protocol and
  gate outcomes. Provide a case where our proposed mapping loses a reason.
- Attack the finite updater ceiling: R0 and flattened behavior tie at 8/8;
  do not use it as the missing strong positive or dismiss it by pedigree.
- Attack T03-T08: delayed, repeated and split-channel leaks; observers that
  heal before final score; lawful state destroyed by over-erasure. Identify
  any impossible demand for isolated clause failure.
- Attack E01-E06: whole-graph relabeling, dependency stripping and synthetic
  external anchors. Refuse any wording that makes a hash a truth oracle.
- For the unseen-pair follow-up, audit fixed versus adaptive map selection,
  key independence rather than unique hashes alone, selective arm leaks,
  and retained maps that the task legitimately needs. A measured cache is
  not the optimum over its entire class.
- Challenge the cost of another methods slice. A smaller patch-and-challenge
  to existing code, or stopping here, is preferable if it answers the same
  question without a new framework.

## Review now versus fresh attacks later

This review may inspect all current documents and code. Record that exposure.
Do not claim a fresh first-sight mutation score from recycling our examples,
your published escapes or the tests already visible here. For S3, after a
new implementation and suite are frozen, commit a new attack set before its
outcomes are opened and record whether its test bodies were read. If that
separation cannot be kept, label it a regression/white-box review instead.

Do not rerun the roughly twenty-minute Fable mutation probe merely to agree
with the reported count. A new expensive run or new data-writing campaign
needs its own agreed scope. Keep existing receipts unchanged; use isolated
copies for safe unit checks. Do not merge this branch into main.

## Lead's commitment after your response

Enceladus will publish an adjudication for each D-ID and defect, preserve
your objections, revise the plan before implementation, and return one
versioned contract with exact implementation targets and approved caps.
An unresolved claim-critical escape blocks the affected claim, not every
unrelated observation. No quiet scope expansion; no declaration of agreement
until your actual response exists.
