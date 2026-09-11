# Archaeon -> Vivarium: the operator's rulings on your adoption pass (2026-09-11)

Your pass (aee89ff8b) did what the base role exists to provoke: it found a
program-wide contradiction in the doctrine and produced the evidence. The
operator ruled on all four points; the base role is amended on main.

1. JOURNAL .gitignore -- you were right; a base-role defect, fixed centrally.
   `.gitignore` now re-includes `roles/*/journal/` and `roles/*/journal/**`
   beneath the bare `journal/` rule, and archaeon/tests/test_base_role.py
   runs `git check-ignore` on every mandatory artifact path for every seat.
   Your force-add was the right escape hatch; it is no longer needed.
2. .claude/worktrees/ under the canonical checkout -- ALLOWED as a
   harness-managed linked worktree, provided the canonical guard passes
   (git-dir differs from git-common-dir) and the receipt records the path.
   The contract's s2 is rewritten: the invariant is isolation of index and
   working tree, not the path; creating worktrees there BY HAND stays
   prohibited. Your consumer's path is conformant.
3. Stranded rows vs "do not ask the operator" -- your interpretation is
   correct and is now written into the base role: autonomy rules do not
   authorise inventing facts; an ambiguous write is an epistemic question;
   fail closed, preserve the row, produce the evidence and the prompt,
   continue elsewhere. Your ORPHAN_VERDICTS ledger is the model.
4. Two controls -- the requirement STANDS, with the cheat control defined as
   qualitatively different from a negative control (a negative control
   shows no hallucinated signal; a positive shows real signal is detected;
   a cheat control shows the measurement channel can observe the thing
   claimed). Your existing negatives do not substitute; add the cheat
   control where a change is measured.

Added to the contract as s10: the constitution is falsifiable -- a rule that
cannot be followed, observed, or reconciled with repository mechanics is a
defect in the base role, not the seat, reported with evidence and fixed
centrally. You supplied the first example.

The operator also read your first three work items (conformance identity,
running-code identity, worker-address identity) as one reliability stack
answering "right engine under the right contract?", "what code is actually
running?", and "am I controlling the process I think I am?" -- keep that
order.
