# Lane C (M4) proposal that OP-LC1 approves (verbatim)

Themis's chat message, byte for byte from the session transcript (session 0e9b1ed2-f51f-49c9-a2ea-5c93be2dfb1c),
kept beside the approval because OP-LC1 refers to it ("the proposed D3 cases", "the proposed
... bounds"). It is CONTEXT, not authority: where it differs from 02 (e.g. ACCEPTED -> PUBLISHED,
git SHA as identity), the operator's text governs.

---

## 2026-10-06T06:02:31.500Z

I've finished the bootstrap and reading. Here's where Lane C stands and my position on it.

**Boot.** Booted as `Themis[m2-0e9b1ed2]` on SPECTREX5, with comms recorded on the M1 store. Nothing in the inbox is addressed to Themis, and no task packets are ready for this seat. Astra hasn't posted anything new: her only Moonshot review is the one on design v0.2 (`7a8a3eef8`), and design v0.3 already incorporates it. Nothing is written to the repo yet. I did one housekeeping fix: the memory index was over its size limit and the line being cut off was the Moonshot pointer itself, so I trimmed it.

**Where Lane C stands.** Design v0.3 is the design of record and the kickoff doc defines deliverables D1–D5; nothing is built yet. Astra's finding F08 (epoch commit semantics) is effectively D3's spec. Her notes that "DB-free isn't the same as available" and "linear scaling is a hypothesis" correspond to the remote-outage test case and D4.

## My position

**1. Synthetic epochs must not run on `main`.** The workgraph tool's compare-and-swap (CAS) is literally `git push origin HEAD:main` on the shared repo.
- `main` takes 35–390 commits a day, peaking at 45 in one hour.
- An illustrative 24 workers on 60-second epochs would push about 1,440 times an hour. That's about 30x `main`'s peak, and every seat would download it on every fetch, permanently.
- As a rough estimate, a third to two-thirds of those pushes would collide, and the retries add more load.
- All six Linux nodes push with tokens that cover the whole Prometheus repo on your one GitHub account. If a stress test triggers GitHub rate limiting, every seat's git traffic stalls.

So I'd use a separate data plane: each epoch chain gets its own ref on a dedicated remote.

**2. Correctness should come from CAS plus determinism, with leases only as an efficiency hint.** Each successor checkpoint is built as a canonical git commit (fixed author, date and message, built with git plumbing so line-ending conversion can't change the bytes). Two honest attempts then produce the same commit SHA, so duplicates are idempotent for free. Publishing is a guarded fast-forward push, and every outcome is typed:

| Push result | Meaning |
|---|---|
| accepted | ACCEPTED |
| rejected, head is my commit | DUPLICATE (cost still charged) |
| rejected, head is a different child of my parent | DISAGREEMENT, goes to a quarantine ref |
| no acknowledgement | AMBIGUOUS: re-read the head, then resolve |

Because a lease grants nothing, an expired lease can't corrupt a chain. This also avoids clashing with the distributed-work doctrine, where workgraph leases never expire on their own.

**3. The canonical trace carries no attempt information.** Host, timings and retry counts go into per-worker receipts, and every attempt is charged. A retry is then invisible in the science record, which satisfies the design's rule that a retry must never look like an RSO content-reset intervention.

**4. Disagreement fails closed.** A contested chain halts; whoever wrote first doesn't silently win. I'd also re-run a small preregistered fraction of epochs on a different host, so the cross-host determinism test (case 7) becomes a standing monitor rather than a one-off.

**5. The D3 fault matrix runs hermetically first.** It needs seconds against a local bare repo, not the fleet. I'd add five cases:
- an ambiguous push;
- a planted disagreement, as a positive control for quarantine;
- the whole matrix with leases switched off;
- an epoch spec that names unapproved code;
- a worker with a skewed clock.

**6. D4 should preregister an operating envelope, not one number.** Two setups: a single shared ref (workgraph as it is today, emulated on a non-production remote) versus one ref per chain, swept over epoch length to find where coordination cost takes off.
- **Prediction I'm willing to lose:** the single ref fails at Launchpad-scale rates and per-chain refs don't.
- **Draft bounds:**
  - coordination time ≤5%;
  - ≤1 non-duplicate retry per 20 accepted epochs;
  - 95th-percentile claim latency ≤10% of epoch length;
  - ≤1% abandoned epochs;
  - zero rate-limit responses;
  - repo growth ≤1 GB per 30 days.
- **Cost:** one sweep is about 12 CPU core-hours, inside the work order's standing compute envelope.

One observation outside Lane C: because the node tokens can write to `main`, the design's rule that "a push grants no authority" is a convention today, not something enforced. Lane C can enforce it for its own plane (workers only run code already merged to `main`). The existing workers are not ours to change.

## What I need from you

Only one thing: **may any D4 arm run against GitHub?** It's your account, and every seat uses it. Without a yes, everything stays on a local network git repo.

My defaults unless you object:
- the data plane on a local network git repo (reversible, so not a gate under the work order);
- the single-ref arm included in D4;
- contested chains fail closed;
- the draft bounds frozen before the baseline run;
- code in a new standard-library-only `moonshot/epoch/` package, under a bounded campaign C-008 on thread TH-MOON-M4.

The first commit would be the full D3 matrix as failing tests.
