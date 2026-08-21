# Loop Cycle 012 — 2026-08-21 (stale wake rolled forward; 008-011 already ran, R6 done at 011)

**Track 1 — pm.certified extended.** KNOWN_CONSTANTS 2 -> 7: catalan, euler_gamma, log2,
glaisher, khinchin, each carrying its OEIS A-number ON THE MODULE (CONSTANT_AUTHORITIES) so
the reference travels with the value. Three new OEIS authority tests (A006752/A001620/A002162)
plus a registry-wide mpmath cross-check that CANNOT drift (it asserts the cross-check set
equals the registry set, so a future constant added without an authority fails the suite).
The existing property tests sample from the registry, so all five new constants inherited
containment / monotone-radius / composition coverage for free. **17 tests green.**

**Track 2 — rung R7 (global plan revision).** Three circuits: LocalRepairer (R6 behaviour:
repairs a doomed plan until patience runs out, never escapes), PlanReviser (R7: marks a
failed plan exhausted, terminates because the exhausted set grows monotonically),
ThrashingSwitcher (the trap: switches eagerly, remembers nothing). **8 tests green.**

Measured, not assumed: the memoryless stride-2 policy DOES abandon the failing plan — so a
naive "did it re-plan?" battery passes it — yet it never reaches the working plan and burns
10 of 12 attempts re-running strategies it already saw fail. My first draft of that test
assumed it would succeed-but-waste; it fails outright. A trap circuit's pathology must be
measured before it is described.

**5th instance of the recurring law, and the doctrine proposal is now drafted**
(`DOCTRINE_PROPOSAL_cheaper_mechanism_slice.md`): on an easy battery where the first
alternative always works, thrashing and genuine revision are observationally identical —
same answer, same attempt count, zero waste. Three doctrine proposals now sit awaiting a
single yes/no from James (cheaper-mechanism slice, abstention channel, evaluator-revision
warrant).

**Next (013):** rung R8 (representation shift) — where the egglog assessment said extraction
over a saturated e-graph becomes relevant.
