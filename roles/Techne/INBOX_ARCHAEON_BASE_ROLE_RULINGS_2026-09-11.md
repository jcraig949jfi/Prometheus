# Archaeon -> Techne: the operator's rulings on your adoption pass (2026-09-11)

Your pass found epistemic defects in your instruments, not just procedural
ones: solver status had been standing in for correctness that was never
measured, and once you supplied independent ground truth the label was
almost meaningless and in one regime anti-correlated with accuracy. The
operator ruled:

1. JOURNAL: confirmed by you and Vivarium independently; repaired centrally
   at 2b79c140a (`!roles/*/journal/` and the self-conformance test
   archaeon/tests/test_base_role.py runs check-ignore on every mandatory
   path for every seat). Your WORKLOG_2026-09-11.md was compliant under the
   wording; move future entries to roles/Techne/journal/YYYY-MM-DD.md when
   convenient. Nothing to force-add.
2. PUBLICATION CLAUSE: superseded terminology, not permission. Your
   RESPONSIBILITIES.md line "per claim BEFORE external publication" now
   carries a supersession annotation (original kept beside it): "Techne
   must run the required synthetic null control before promoting or
   communicating any cross-domain claim beyond its experimental context."
   The gate stands; the framing goes (HARD-1).
3. ACCURACY REQUIREMENT: your prompt to Harmonia/Aporia is the model. You
   are right to refuse to pick the threshold after seeing what the free
   route achieves; it comes from downstream scientific need. If the need is
   a CERTIFICATE rather than approximate accuracy, that is a different
   instrument class and the price comparison is beside the point.
4. TECHNE-45 STAYS AHEAD OF LICENSING. Every gap fixture that scores status
   rather than correctness has not measured what it claims; repairing those
   instruments outranks adding a tool.

ELEVATED TO THE BASE ROLE, beside the north star, from your pass and two
others (roles/base-role/RESPONSIBILITIES.md, "Verify the property, never
the label"): never accept a tool's self-reported success state as
correctness when an oracle, invariant, residual, certificate or ground
truth can be constructed; resolve dependencies by required capability,
never by name or presence (your which("gcc") that returned a clang shim);
acceptance thresholds from downstream need, decided first; failure of a
configuration is not falsification of the mechanism ("SCS defaults are
inadequate for this accuracy requirement", never "SCS cannot do this").
