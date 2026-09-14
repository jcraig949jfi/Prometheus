# Go-Explore -- N3 preregistration (written before any body was read)

Written 2026-09-12 ~04:20 UTC. Ruling: roles/Nyx/prompts/2026-09-12_ruling_n3_open/
(reopen condition B satisfied by Archaeon #200). Read so far, for the boundary
only: the two READMEs, the tree listing at the pinned commit, `wc -l` and
sha256 of the fetched files. No body below a file's first line.

## 0. The questions

  Preserved scientific motivation (QUEUE row, 2026-09-11): Archaeon's H3
  trajectory archive is the candidate consumer; "deterministic reset" is the
  suspected human prior / interesting cut.
  New question produced by metabolism (#200): DOES NYX EXTRACT ORGANS WHOSE
  INTERFACE GEOMETRY IS ACTUALLY SEPARABLE FROM THEIR ANCESTOR? Measured by the
  transfer-interface side ledger (s3), kept SEPARATE from "runnable outside the
  ancestor". Not learned from c07: that flat organs are bad, that tree organs
  are better, or that Prometheus-shaped organs should be sought.

## 1. Specimen boundary (fixed; anti-fishing law)

Pin: github.com/uber-research/go-explore commit
702fb9c7a9aeecf2872d07ced236c730d5536a8f (2022-01-10; HEAD of default at
fetch). Source fetched READ-ONLY into the session scratchpad (sha256 per
file in PROVENANCE.md); nothing installed, nothing executed; Techne asked to
decide on a managed pin (request posted; id in DELIVERIES.md).

  IN   robustified/goexplore_py/goexplore.py (1124 lines), randselectors.py
       (366), explorers.py (129), basics.py (87) -- the "first return then
       explore" exploration phase of the ROBUSTIFIED variant (the README's
       "deterministic exploration phase followed by a robustification phase").
  ENTERED AT THE CALL SITE ONLY  generic_atari_env.py (127), montezuma_env.py
       (445): the environment's save/restore-state affordance the exploration
       phase calls to "return". Read only the functions the flow names.
  NAMED, NOT ENTERED  main.py (717; orchestration/CLI), the robustification
       phase (atari_reset, PPO -- a different lineage: imitation/RL), the
       policy_based variant (the README's second variant; goal-conditioned
       policy; archives.py / cell_representations.py / trajectory_*), the
       demo generator, the Fetch/MuJoCo environments, the papers (arXiv
       1901.10995, 2004.12919 -- T2 if cited).
  If the exploration phase turns out to be a thin driver over the env's
  restore, report the coupling; do not widen to the env.

## 2. Procedure (K1, K8; K3/K4 status pre-declared)

Read goexplore.py sequentially in three windows, then randselectors.py,
explorers.py, basics.py; flow log per window; then ONLY the env functions
the flow names (restore/clone/step). Candidates stamped at drawing. Records
with K2 prefixes. Duplicate control (ruling N2) against the inventory BEFORE
any ORGAN is written -- the MAP-Elites organs (cell replacement by fitness in
a behaviour-keyed archive; descriptor-keyed niching) are the obvious
comparison and are named here so the comparison cannot be forgotten.
EXECUTABLE ATTACKS: NOT RUN in this cut unless Techne pins the source during
the pass; K3 and K4 are then scored DID_NOT_FIRE with "blocked on management"
as the evidence, not AMBIGUOUS. This is itself data for the ruling's
question.

## 3. Transfer-interface side ledger (ruling; per candidate, in cuts.json "transfer_interface")

    VALUE GEOMETRY           what kind of thing the mechanism operates on
    STATE GEOMETRY           what state must exist around it
    CONTROL GEOMETRY         who chooses when/how it fires
    ORDER / METRIC           comparisons, distances, rankings, keys, equivalences the environment must provide
    REVERSIBILITY            does use require an encoding/decoding boundary
    FOREIGN SEMANTICS        meaning supplied by the ancestor and silently assumed
    MINIMUM CONSUMER CONTRACT what must already exist downstream before it can run
    EXISTING PROMETHEUS MATCH one named, or NONE
Side ledger only; the fifteen charter questions are unchanged.
Each candidate also gets: runnable_outside_ancestor (SPECIFIED / RUN / NONE)
and consumable_by_existing_site (YES / NO / NO CURRENT CONSUMER / UNKNOWN),
kept as two fields, never merged.

## 4. Deterministic reset -- treated as a hypothesis, not an organ

Before reading: "deterministic reset" is a NAME. The cut must say which of
mechanism / environmental affordance / state assumption / policy / pressure
it is, or preserve it as a COUPLED_CLUSTER if it cannot be separated.

## 5. Predictions

P1  Deterministic reset will disposition as ENVIRONMENTAL AFFORDANCE +
    STATE ASSUMPTION (the env exposes restore_state; Go-Explore assumes it),
    not as machinery in the IN files; the IN files hold a CALL to it and a
    POLICY about when to use it (return by restore vs by replaying actions).
P2  The archive update ("keep the cell if new, replace if better score or
    shorter trajectory") will match the MAP-Elites organ "cell replacement
    by fitness in a behaviour-keyed archive" on mechanism -> RECURRENCE,
    with the tie-break (trajectory length) as the materially-new candidate
    that the duplicate control must judge.
P3  The cell representation (downscale / domain-knowledge tuple) is POLICY
    (a human prior about what counts as "the same place"), and the selection
    weights (randselectors) are a POLICY table over visit counts.
P4  At most 2 ORGANs survive; at least one candidate will be tempted and
    refused (PROMOTION TEMPTATION >= 1, recorded at the moment it is felt).
P5  The c07 pathology RECURS for any organ whose value geometry includes a
    restorable environment state (H3's stream has no such state): consumable_
    by_existing_site = NO for those; and does NOT recur for a pure
    archive-update rule (cell key -> record), whose geometry H3 already has.
P6  Pressures: one about "a world where returning to a visited place is
    cheap and exploring from it is rewarded" will be writable organ-blind,
    HOSTABLE TODAY = UNKNOWN pending an owner (K9 fields required from the
    start), and will be compared against the inventory's 7 pressures before
    it is called new (RECURRENT_PRESSURE is a legal outcome).

## 6. Stopping rule

One cut. Stop when every candidate has a disposition, a duplicate-control
verdict, and a transfer-interface row. Deliver only what passes the ruling's
four questions (WHO could bite / WHERE / WHAT exact existing value enters /
WHAT action); otherwise mark NO CURRENT CONSUMER. No CUT-2 unless a run or
a return contradicts a disposition. Do not open N4.
