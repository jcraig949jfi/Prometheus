# Ananke arc 2 (2026-09-27/28): PTE frontier continuation, integrated synthesis

Starting point: SYNTHESIS_2026-09-27.md (c34cbb463). Workers W-A..W-F ran
from neutral handoffs (handoffs/), each with PLAN-before-run and a LOG.
Reports are in workers/<id>/REPORT.md. This file is the integrated
judgement.

## 1 What survived independent challenge
- M2 = a strict two-hop echo, now PREDICTED, not just described (W-A). A
  zero-parameter particle model of the echo predicts 46/46 unseen
  accuracy-vs-gap curves (median MAE .02; the base-curve null passes
  12/44). One-dial physics changes and a 2-field program edit move the
  interval exactly as predicted, including a cancellation.
- M3 = transport + a one-time SETRULE bootstrap (W-B): a one-rule law is
  bit-identical to the champion.
- r (the rule pointer) is never the bit carrier: 0 FLIPs in 18 swaps.
- The in-flight carrier of M2 is genuine CONTENT, not presence (W-C twin
  census: no firing difference).
- The carrier swap and temporal reach instruments survived hardening: 10
  known-answer tests with negative controls; used across 166 cells with 0
  errors.

## 2 What changed about M2 and M3 (interpretations I held that did not survive)
- "Routing = disruption, not storage" was TOO WEAK. The specimen's routing
  write deletes hop-1 round trips and SETS THE LOWER EDGE of the useful
  interval.
- "Peak at the trained gap 6-8" was an even-gap artefact: gap 7 beats gap
  8 in 4/4 champions (readout-parity sawtooth).
- "SETRULE = bootstrap" is true for M3, but the escape is a PHYSICS
  ARTIFACT (registers are 0 at tick 0, so every SETRULE goes to rule 0).
  It does NOT generalize: in 29% of 42 qualifying cells SETRULE is a
  readout-local, per-tick CONDITIONAL BRANCH (a sign-conditioned
  excursion; sample/hold alternation).

## 3 The joint carrier (T-JC-1, W-F)
- 4781b0a1 is SOURCE-LATCHED REGENERATION. The 5 sensors latch the cue and
  keep firing. The bit is at the source until the transmission deadline
  (~readout minus max delay) and in the channel after it. The single-swap
  ~0.5 was a conflict between two pipeline stages holding the same bit.
- Census-wide, all 14 "JOINT" cells are per-trial PHASE MIXTURES
  (site_acc + chan_acc = 1.00): a handoff caught mid-transit.
- No genuinely synergistic (joint-code) carrier has been observed in PTE.
- "Where is the information?" is well posed only per tick AND per role.
  In RELAY/MAJ the carrier is a TRAJECTORY.

## 4 Did the instruments survive hardening? Yes, with sharper boundaries
- New failure modes found by the workers and now documented:
  F5' JOINT = mixture (sum ~ 1);
  F7 PRESENCE READS AS CONTENT under superposition (a swap verdict names
     the reader's register, not the physical code; report two axes);
  F8 a counts NO-EFFECT can be unreachable (arm_identical);
  zero-default rule privilege; present-but-unused decoders;
  written-but-never-read scars.
- W-D mined 8 "could not fire" cases in 5 seats. No single reach pattern
  generalizes; three checks plus an identical-arms alarm cover all 8
  (T-X-4, a research thread, NOT a fleet rule).

## 5 What the independent workers found (one line each)
W-A: M2 is predicted by a zero-parameter model (46/46).
W-B: SETRULE is a bootstrap artifact in 64% and a per-tick branch in 29%;
     never memory.
W-C: the PTE-content vs Aether-timing contrast is REFUTED; the real axis is
     the receiver operator.
W-D: "could not fire" = RIPR (reach / infect / propagate) + wrong target +
     forced outcome.
W-E: no recoverable retention past the query (preregistered NO); frozen,
     never-read scars in non-decaying stores.
W-F: carriers: HOLD = site (81/85); RELAY/MAJ = program- and
     phase-dependent; family "selects" only via HOLD.

## 6 What the PTE <-> Aether comparison taught us
The framed contrast (Aether timing vs PTE content) does not hold. Each
side's specimen had shut the other channel, and 7/13 PTE specimens carry
the cue as WHO FIRES, like Aether's rcv. The deeper distinction is the
RECEIVER OPERATOR:
- PTE ADDS arrivals, so presence becomes content for free and a content
  difference survives background traffic additively.
- Aether ARBITRATES and REPLACES, with message-writable code, so presence
  becomes writer identity and content differences are overwritten.
Discriminating experiment (for Aether's owner): fwd vs a one-change fwd_add
across background write density. PTE-side test T-WC-2: does an emission
cost select presence codes? (Q2 ran at the end of this arc; see s8.)

## 7 How the backlog changed
Every closure split into sharper successors. Closed: T-M2-2, T-M3-1,
T-X-1, T-RET-1, T-CT-1, T-INS-1, T-TA-1, T-D3.
New:
- T-WA-1..4 (routing-aware model; design-not-evolve; recirculating
  control; odd-gap sweeps)
- T-BR-1..3 (SETRULE branch mechanics)
- T-WC-1..5 (two-axis carrier reporting; emission cost; 3 Aether
  proposals)
- T-RET-2, T-SI-SCAR, T-RET-3
- T-CT-2..5 (carrier trajectories; mixture tests; the MAJ point; relative
  threshold)
- T-JC-2..5, T-X-4, T-D1/T-D2
Reframed: T-DM-2 (no joint code observed). Poorly framed and replaced:
"is M2 memory?" -> interval kernels.

## 8 Queue and leases
Queued because of leases:
- Q1 T-CT-1: waited on W-B's GPU lease, then ran as W-F.
- Q2 X4: waited on W-F's GPU lease, then ran at the end of the arc.
The existing bus lease (primordial pm:gpu:lease) was UNREACHABLE (Redis
6390 down), so roles/Ananke/research/lease.py used the fallback: a host
lease file + a comms record.
Leases acquired and released (all via the fallback):
- W-B gpu x2;
- W-E cpu8 (taken seconds AFTER starting: a disclosed slip);
- W-A cpu8 ~5 min;
- W-F gpu (renewed once);
- Ananke gpu for Q2 (comms #768).
Nestor independently adopted the same convention (cpu8 "Nestor P2").
Rule slips, disclosed by the workers themselves: W-C ran a duplicate
4-thread search ~13 min over the no-lease envelope; W-E leased late. The
subagent harness refused every worker's REPORT.md write, and Ananke saved
each report from the worker's message.

## 9 C2 and SI01 successors (evidence-based, not launched)
- C2 successor (carrier-load mapping): the census shows that a
  single-tick carrier class in RELAY/MAJ is a PHASE reading. Any load map
  must first measure the unloaded carrier TRAJECTORY per champion (T-CT-2).
  HOLD is safe at one tick.
- SI01 successor: no nontrivial retention regime yet (T-RET-1 NO). The
  only candidates are non-decaying plastic "scars" and one possible
  w-integrator (f7e62fe3, exploratory). A preregistered T-RET-2 must
  confirm before any irreversibility design (T-SI-SCAR). W-A adds that
  M2-style carriers are physics-bounded echoes, so any SI design on PTE
  needs a recirculating control genome.

## 10 What can run next without HITL
Ready, CPU- or GPU-scale, bounded:
- T-CT-2 (carrier trajectories, ~1 h GPU)
- T-RET-2 (preregistered retention confirmation)
- T-BR-1 (decompile the SETRULE branch)
- T-WA-1/2 (routing-aware model; design-not-evolve)
- T-WC-1 (two-axis reporting)
- T-D1/T-D2 (reach counters; plant library)
- T-JC-2/5
Offer the T-WC-3..5 proposals to Aether only as information.
