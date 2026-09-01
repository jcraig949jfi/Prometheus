---
name: review-packet
description: >
  Produce a detailed external-review packet as one pure-ASCII block. Invoke PROACTIVELY
  after any substantial chunk of work (a built+run experiment, campaign, pilot,
  calibration, validated slice, decisive negative, or milestone) WITHOUT being asked, and
  whenever the user asks for "a review", "review packet", or "write this up for external
  review". Delivers three ways at once: pasted in chat, written to a file, committed and
  pushed. Use when work has reached a reportable state (a result, verdict, or a
  blocked-and-diagnosed stop).
---

# Review Packet

A review packet is a **self-contained, pure-ASCII** document that an external reviewer
(or a frontier model with no repo access) can read cold and critique. It is the standing
way substantial work is reported in this program (house style from the Serendipity
Foundry D-12/D-13 review packets).

## When to produce one (proactively, without being asked)

After a work-unit reaches a **reportable state**: a built-and-run experiment, a campaign,
a pilot, a calibration, a validated slice, a decisive negative, or a milestone commit
series. A single bug-fix or file edit is NOT substantial; a campaign / pilot /
falsification / slice that produced a **result or a decision** IS. When unsure, err
toward producing it. Also produce one on explicit request ("write me a review", "review
packet", "for external review").

## Deliver three ways at once

1. **In chat** — the full packet as ONE ASCII block the user can cut and paste.
2. **In a file** — `<component>/pivot/<NAME>_REVIEW_<DATE>.md` (or the bench's
   `REVIEW_PACKET_FINAL_<NAME>.txt`), pure ASCII.
3. **Committed and pushed** — so the packet is citable/pullable on other machines.

## House style (hard rules)

- **Pure ASCII only.** No unicode. Write `eps`, `<=`, `>=`, `x` (not multiply sign),
  `->`, `--`. Verify: `LANG=C.UTF-8 grep -nP '[^\x00-\x7F]' <file>` must return nothing.
- **Box banner** `+===...===+` header with title, author (role + machine), date, "For:"
  (HITL + external reviewers), Status, and a "self-contained / no repo access needed"
  line.
- **Numbered `-----` sections.** A workable spine (adapt to the work):
  0. Summary / mandate / verdict up front
  1. What was built (and what was committed before measurement)
  2. The endpoint/claim and why it matters
  3-6. Design as executed, pilot/census, results (EXACT numbers, gates with the failing
     clause), incidents and what they validated
  7. What this does and does NOT establish (claim ceiling, explicit conditionality)
  8. The decision / recommendation (HITL's call, with Apollo's lean)
  9. Questions for the reviewer (written to resist agreement)
  10. Artifacts (paths + commit SHAs)
  END banner inviting the reviewer to say "not worth continuing" — that must always
  remain a first-class answer.

## Doctrine the packet must honour

- **Self-contained:** every load-bearing number inline; a reviewer needs no repo access.
- **Failure SHAPES, not verdict-lines.** Say HOW it failed; preserve the gradient.
- **Verified-not-trusted:** mark what was measured vs inherited; give artifact paths.
- **Record defects and process holes plainly** rather than smoothing them over.
- **Able to return "stop."** A packet that cannot recommend retirement is decorative.

## Exemplars

- `D:\Prometheus\apollo\pivot\APOLLO_S1_REVIEW_2026-09-01.md` (Apollo S1)
- `D:\Prometheus\genesis\harmonia_a\gen0\REVIEW_PACKET_FINAL_HARMONIA_A_GEN0.txt`
- Upstream: `D:\ZeusE\d12\reports\REVIEW_PACKET_FINAL_D12.txt` / `..._D13.txt`
