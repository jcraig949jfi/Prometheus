DAEDALUS — EXECUTION ORDER 2026-09-08 (from the operator)

Baseline: archaeon/v0 at 5191c3383; engine at be65b0efa (v7 live). Your
requests: roles/Daedalus/INBOX_ARCHAEON_EXPANSION_ROADMAP_2026-09-07.md
(later sections supersede). Tests per package:
archaeon/docs/expansion/WORK_PACKAGES.md. Design decisions for A1 are in the
design packet the operator circulated (NK/CA kind contracts); do not start
A1 until that packet is accepted, do start everything else now.

DO NOW (independent of everything)
1. WP-0a. sfe/executors.py:57: refuse len(bits) != length as an invalid
   candidate beside the non-binary check, on the established error path;
   never a completed normal score. Fix the stale docstring (root vs
   derived per-repeat seed). Tests 0a-a/b/c; re-run Herakles's F-1 table
   showing refusal. Sealed fixtures keep result and identity.
2. sfclient: add `arm` to family_member(...), plus the /v2/read/* and
   measurement methods, in every client copy. Publish a shared fixture for
   Vivarium's WP-0c (identical execution spec under labels A and B -> one
   spec_hash, two member arms). You supply the contract; Vivarium integrates.

THEN, ONCE THE DESIGN PACKET IS ACCEPTED
3. WP-A1. nk_landscape_v0 executor in the engine beside BitStringExecutor,
   per the accepted contract: legal (length, k); neighbour construction;
   contribution tables and their seed derivation; normalisation to [0,1];
   contribution[] witness semantics; solved semantics for k > 0 (score = 1
   NOT assumed attainable). k = 0 reproduces additive scoring exactly and
   equals onemax only if that construction is explicitly implemented.
   Tests A1-a..e, including the exhaustively solved interacting fixture with
   incompatible local maxima and the joint permutation invariant. Register
   the two measurements (nk_landscape_v0.score, .contribution) on live M1 as
   you did for evaluate_bitstring.
4. WP-P2 schema half (generation, episode in unit_of_analysis) only after
   Harmonia names the vocabulary. Not before.

NOT ASKED: thresholds, outcome semantics, anything that makes an experiment
"work". A4 (related landscapes) waits until A3-acq has run.

REPORT FORMAT: item ID; revisions; commands run; expected vs observed;
fixture hashes; unresolved limits; next permitted action.
