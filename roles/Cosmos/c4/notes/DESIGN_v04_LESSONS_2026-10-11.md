# Lessons for C4 DESIGN v0.4 (Cosmos, 2026-10-11; from EXP-04..08; drafting notes, not a design)

1. TASK START CONDITION IS PART OF THE PHYSICS QUESTION. The harness starts every episode at system.init; LOCAL
   SYSID describes the STATIONARY regime. A predictor of k-step usability that ignores the start distribution is
   wrong exactly where memory is long (EXP-07: a .95 error -.29 -> -.04 when the start state is used). v0.4 must
   declare, per family, which start distribution the certificates use, and the probe must expose it (reading
   system.init adds no controlled step; G7 is unaffected).
2. STATIONARY != TASK INPUT STATISTICS. LocalProbe drives with all 3V + 1 symbols uniformly; the task presents one
   cue, k distractors and a query. Not yet shown to matter; must be declared.
3. GEOMETRIC REACHABILITY FAMILIES. stig's usability is set by where a moving sensor is at query time (EXP-01) and
   may be periodic in k (EXP-05 pending). A cross-family "memory" law that cannot see geometry will fail on such
   families by construction; T3-DOWN already encodes reachability. v0.4 should state whether such families are in
   scope for a LOCAL law or are a separate stratum.
4. INSTRUMENTS BEFORE LAWS. The EXP-04 surrogate was used on family data before it was qualified on planted
   systems; EXP-06..08 then found its dominant defect. Rule for v0.4: every predictor instrument passes a planted
   qualification (prereg, fresh seeds) before it touches family data.
5. OPERATIONS. Every long job runs under prometheus.cosmos.supervise; any waiter waits on the launcher, with a
   Monitor and a scheduled wake (INCIDENT_2026-10-08_EXP04_STALL.md).
