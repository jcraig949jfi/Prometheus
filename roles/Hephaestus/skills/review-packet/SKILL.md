---
name: review-packet
description: After any substantial block of work (a build, an experiment, a charter change, a multi-commit session), produce a detailed ASCII review package IN THE CHAT for external review, without being asked. Standing order from James (2026-09-01). Use when work has landed and before ending the turn.
---

# Review packet — standing order

(Repo copy of `~/.claude/skills/review-packet/SKILL.md`, kept with the seat so it survives a machine
change. If the two differ, the repo copy is authoritative for Hephaestus.)

**Trigger.** You have just finished a substantial block of work: something was built, measured,
re-chartered, reclassified, or committed. Do not wait to be asked. Before the closing recap, write
the packet and put it in the chat as a single fenced ASCII block the operator can cut and paste to an
external reviewer. (Also apply when the operator says "review packet", "review package", or "write
this up for external review".)

**Definition of substantial.** Any of: a commit with >100 changed lines or >3 files; an experiment
that produced a number; a state change in a queue/ledger; a ruling applied; a session with >=3
distinct phases. When unsure, write it — a short packet is cheap; a missing one is not.

## Hard rules

- **ASCII only.** No em/en dashes (use `--`), no arrows (`->`), no `≠ Δ ≥ ≤ × ·`, no smart quotes,
  no box-drawing beyond `-`, `=`, `|`, `+`. Tables as fixed-width text. Width <= 80 columns.
- **Self-contained.** A reader with no repo access must understand it. File paths appear only as
  provenance, never as the explanation.
- **Numbers are quoted exactly** and each carries a provenance grade (E3 executed this session /
  E1 regenerable / E0 prose). Never round a measured number into a nicer one.
- **Failures and non-results first-class.** What did NOT happen, what was NOT established, and what
  the author's own errors cost go in their own sections, not in a footnote.
- **Conflict of interest declared up front** when the author built what is being reviewed.
- **Questions for the reviewer** are specific, answerable, and include at least one "what would
  falsify this" and one "what should we stop".
- The packet is committed to the repo as well when the work was committed (a `.txt` under
  `roles/<Seat>/`), so replies can be adjudicated against a fixed text.

## Section skeleton (adapt headings; keep the order)

```
================================================================================
REVIEW PACKET -- <what> -- <program/seat>, <date>
Commit(s) of record: <hash(es)>   Author: <seat/model>   Invoked by: <who, quote>
================================================================================
0. WHAT THIS PACKET IS (2-4 lines) + conflict of interest, declared
1. CONTEXT (<= 8 lines for a reader with no prior exposure)
2. THE QUESTION(S) THE WORK WAS ANSWERING (verbatim where possible)
3. WHAT WAS DONE, STEP BY STEP (numbers with grades; failure positions, not just scores)
4. RESULTS (tables; two-coordinate results kept as two coordinates)
5. WHAT CHANGED IN THE REPOSITORY (files, states, scheduled jobs, cost)
6. WHAT THIS DID NOT ESTABLISH (explicit non-results, open gates, untested components)
7. AUTHOR'S OWN ERRORS AND WHAT THEY COST
8. WHAT IS OWED, AND BY WHOM
9. QUESTIONS FOR THE EXTERNAL REVIEWER (numbered; falsification + stop questions)
10. HOW TO REPRODUCE (exact commands, expected outputs, determinism/seed)
================================================================================
```

## Process

1. Gather the numbers from artifacts, not from memory: re-open the result JSON / logs.
2. Draft in the skeleton; run an ASCII check (`grep -nP '[^\x00-\x7F]'`) on the text before
   pasting; fix any non-ASCII.
3. Paste the block in the chat. Then, if the work was committed, also write it to the repo and
   commit it (small follow-up commit is fine).
4. In the closing recap, one line: "Review packet above; also committed at <path>."
