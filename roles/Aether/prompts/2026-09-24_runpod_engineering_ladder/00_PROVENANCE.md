# AETHER RUNPOD ENGINEERING LADDER -- provenance and boot pointer

Issued by: the operator, in chat, 2026-09-24.
Received by: Aether[buckkeep-7a10ca4b] on BUCKKEEP.
Status: **STANDING DIRECTIVE, IN PROGRESS.**

`DIRECTIVE.md` beside this file is the operator's text verbatim.
`MANIFEST.md` carries the sha256 of the committed LF bytes; verify
before acting on it (base role s1 step 5):

    python -m comms.manifest verify \
      roles/Aether/prompts/2026-09-24_runpod_engineering_ladder

## What changed about this seat's job

The seat now has two responsibilities and **the second is the priority
for this round**: turn everything learned from RunPod into a reusable
Prometheus GPU experimentation system. The AETH-02 native-circuitry
experiment continues only as a realistic workload.

The explicit warning in the directive is the reason: we may be weeks
from experiments where GPU operational failure would destroy genuinely
valuable scientific time, so the flight system gets built during the
barren period rather than during the emergency.

## The order of work, as instructed

1. The three AETH-02 trajectories land, and a detailed report is
   produced and displayed.
2. Then the engineering ladder, rung by rung, each rung throwing
   slightly more at RunPod than the last and leaving reusable machinery
   behind: dry run -> tiny pod -> scale up -> long run and failure
   injection -> 2-3 pod fan-out -> a FOREIGN SEAT'S module through the
   same machinery.

## Budget, which is separate from AETH-02's

**$5 hard ceiling of incremental RunPod spend for the engineering
campaign**, with the expectation that useful spend lands substantially
below it. AETH-02's own budget is tracked separately; see
`roles/Aether/TODO.md`.

Never claim provider billing reconciliation unless actual provider
billing data was obtained. Every receipt so far has said this
explicitly, and the directive now makes it a standing rule.

## The success test that matters most

> Can a fresh seat package and launch a GPU experiment correctly
> without reading Aether's implementation?

If not, iterate. That is a platform failure, not a user error.

## What the next instance must not assume

- That a successful RunPod run means the ladder is done. The directive
  is explicit: do not stop merely because one run works.
- That documentation counts without executable tooling behind it. Every
  documented workflow needs a corresponding command or test.
- That the science is the deliverable this round. It is the workload.
