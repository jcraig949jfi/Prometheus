# Worker J: do receiver semantics shape which information-processing mechanisms emerge?

ID W-J. Output workers/W-J/. Namespace 0x5EF (PTE only). Read
COMMON_RULES.md and COMMON_RULES_ARC3.md first. Budget ~4 h. Mostly
literature and theory. PTE runs only if cheap and decisive (CPU, or a
lease).

QUESTION
Two Prometheus engines differ in what a receiver does with simultaneous
arrivals: PTE SUMS them (superposition; the receiver cannot separate
senders), and Aether ARBITRATES (a winner replaces the stored byte;
messages can also rewrite receiving code). Does receiver semantics shape
which information-processing mechanisms can emerge? Sub-questions:
- Does superposition favour magnitude / count / source-mixture codes?
- Does arbitration favour timing / winner-selection codes?
- Does message-writable receiving code create a qualitatively different
  computational regime?
- Which apparent differences are artefacts of OBSERVABILITY (what each
  engine's instruments can see)?
Deliver: (1) a literature synthesis; (2) a formal or semi-formal
statement of what each semantics makes cheap or impossible; (3) a
DISCRIMINATING experiment design for PTE (runnable here) and PROPOSALS
for Aether (packaged for its owner; never run or modify Aether); (4) a
list of predictions that could fail.

EVIDENCE (raw)
- PTE engine delivery/superposition semantics: prometheus/ananke/engine.py
  (_tick delivery, _emit, collisions none/aloha/saturate, cap).
- Aether (read-only, on origin/main): Aether/AETH-03/ (e.g.
  PHYSICS_DESIGN_02_2026-09-26.md), roles/Aether/STATUS.md; use
  `git show origin/main:<path>`.
- A previous comparison's raw data and notes: workers/W-C/ (NOTES.md,
  out/, wc_probe*.py, x4_evolve.py, X4_RESULT.md). Its REPORT.md is an
  interpretation (ARC3 rule 2).
- External starting points: PRIOR_ART_temporal_distributed_computation.md
  (network coding, AER, timing channels, hyperdimensional superposition).
  Extend it: multiple-access channel theory (collision channels, the
  "sum" MAC vs the "OR"/collision MAC), physical-layer network coding,
  over-the-air computation / nomographic functions, compute-and-forward,
  CRDTs / last-writer-wins registers, arbiters in asynchronous circuits,
  winner-take-all networks, stigmergy with overwrite vs accumulate,
  cellular automata with additive vs majority/replacement rules.
DELIVERABLE: the report in your final message; longer notes in
NOTES.md; DISAGREEMENTS.
STOP: 4 h.
