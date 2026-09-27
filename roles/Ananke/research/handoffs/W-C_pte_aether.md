# Worker C: PTE vs Aether: where does information ride, and why?

ID: W-C. Output: roles/Ananke/research/workers/W-C/. Namespace: 0x5E6
(PTE only). Read COMMON_RULES.md first. Budget: ~4 h.

QUESTION
Two Prometheus engines report mechanisms that move a one-bit difference
through a substrate:
- PTE (Ananke): lossy, delayed packets whose payloads SUM on arrival.
- Aether (AETH-03): a lattice of "laws". There, the one law that carries a
  difference ("rcv") appears to carry it in WHICH sites fire and WHEN,
  not in written content.

Do the two engines expose complementary implementations of a deeper
distinction (for example content-bearing vs timing/identity-bearing
transport, and what physics selects one or the other)? Or is the
apparent contrast an artefact of different instruments, tasks or
definitions? If a real distinction exists, propose DISCRIMINATING
cross-engine experiments: what to run on each engine, with predictions
that could come out either way.

EVIDENCE POINTERS
- Aether (read-only; do NOT run or modify Aether code; do not contact
  Aether): on origin/main, commit 07d9a18a9 and later. Aether/AETH-03/
  (PHYSICS_DESIGN_02_2026-09-26.md and its neighbours), roles/Aether/
  STATUS.md and TODO.md. Use `git -C F:/Prometheus-worktrees/ananke-base-role
  show origin/main:<path>` if a path is missing locally.
- PTE raw evidence: roles/Ananke/research/spikes/out/*.json (carrier
  swaps: s_m2.json, s_ct.json; delays; decoders) and the scripts beside
  them; roles/Ananke/pte/c1b/C1B_SUMMARY.json; the engine semantics in
  prometheus/ananke/engine.py (superposition in _emit/delivery).
- Other seats with related instruments: Cosmos C3 P1/P2 certificate
  (roles/Cosmos/c3/ on origin/main); Archaeon causal lens FF-20
  (archaeon/causal_lens/FALSE_FRIENDS.md).
- External research: start from roles/Ananke/research/
  PRIOR_ART_temporal_distributed_computation.md (timing channels, AER,
  polychronization, network coding, superposition codes). Extend it with
  your own search where needed (event-based vs rate/value coding;
  spike-timing vs rate codes; the information capacity of timing vs
  amplitude channels under noise).

THINGS TO CONSIDER
- Map each engine's state variables onto a common set of carrier
  dimensions: content, count, timing, identity/destination, configuration.
- Which physical features (superposition, loss, noise, jitter, discrete
  firing, energy) would be expected, from first principles or the
  literature, to favour content vs timing codes?
- PTE-side experiments you can RUN (GPU lease rules apply), e.g. whether
  any PTE law carries information in timing alone. Aether-side experiments
  are PROPOSALS only.
- Say plainly if the comparison does not hold up.
