# Phase 3 joint-work proposal v0.4

Date: 2026-10-02. Lead: Enceladus / BUCKKEEP. Reviewer: Dionysus, pending.
Status: **REVIEW_READY; NOT AGREED; science NOT_VERIFIED.**

The operator asked Enceladus to review Dionysus's latest Fable 5.1 work,
synthesize first, and lead the next round for Dionysus to review. This is
that handoff, not a declaration that Dionysus has approved it. The directory
name identifies the intended collaboration, not joint authorship.

## Read in this order

1. [Synthesis and decisions](SYNTHESIS_AND_DECISIONS_v0.4.md): contributions,
   corrections, actual disagreements, and the lead's proposed resolutions.
2. [Next-round plan](NEXT_ROUND_PLAN_v0.4.md): one bounded methods slice,
   expected answers, division of work, proposed caps, exits and stops.
3. [Dionysus review handoff](DIONYSUS_REVIEW_HANDOFF.md): decision IDs and a
   concrete response contract. Review precedes implementation.
4. [Validation](VALIDATION.md): what was actually rerun and what was not.
5. [Self-contained review packet](REVIEW_PACKET_2026-10-02.md).

## Decision in brief

Keep native runtimes and common evidence contracts. Do not merge the two
reference harnesses or their verdict policies by concatenating code/tests.
First cross-review a small retention/reset and evidence-binding path, with
clean positives, delayed leaks, invalidation, and genuinely fresh attacks.
Only then authorize one actual native witness. Preserve Fable's unseen-pair
experiment as a later, bounded combination test, not a recursion test.

## Evidence available now

- Fable delivery: 3669bc7f2595dca2ead5348d0297a122a4ed74fe.
- ASTRA v0.3: 9af020b248a35bf55cf5def242aa0ee565982224.
- Both suites rerun here: Fable 110 tests; ASTRA 28 tests; both exit 0.
- These are software-regression reproductions, not independent scientific
  replication or first-sight attack scores. No new production code was made.
- Fable's 29 documented escapes and final-repair review gap remain visible.
- Our five selected mutation kills are not a competing coverage statistic.
- Original ChatGPT 5.6 harness still absent; neither substitute is that code.
- Strong recursion remains DETECTION_UNQUALIFIED.

## Provenance and scope

Branch: enceladus/rso-synthesis-2026-10-02.
Base: 9af020b248a35bf55cf5def242aa0ee565982224.
Worktree: C:/Prometheus-worktrees/enceladus-base-role.
Fetched origin/main snapshot: 563ee7c36fcd88dcf20f4a7f7e8b3902e9c30bae.
The Fable hardening subtree is unchanged between its source pin and that
snapshot. This branch deliberately starts from our existing review branch;
it does not merge main or copy Fable's whole package into this checkout.

[SOURCE_INDEX.json](SOURCE_INDEX.json) identifies inspected source bytes.
[MANIFEST.md](MANIFEST.md) identifies this delivery's content. Neither
proves authorship, truth, independence or custody.

Original sources, runtime code, existing receipts and other seats' files
remain unchanged. No cloud resources, package installs, scientific campaign,
main integration, or automatic permission for the next experiment.
