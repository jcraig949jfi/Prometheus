# Archaeon — campaign review and refinements, 2026-09-06

The operator's frame: **one shared campaign — make the fossils usable, then
test whether using them improves experiment selection.** Two checkpoints,
M-ELIGIBLE then M-SIGNAL. This file records Archaeon's review of the plan
after the day's handoffs, with refinements the other seats should see.

## What landed today (verified by commit, not by report)

- Vivarium `b70d7a665` — spec v3 `repeat` with five declared axes; live proof of
  4 ordered observations in one world; `archaeon.probe.v0` RETIRED with meaning
  preserved; `random_walk_v0` kind added.
- Daedalus `2fa52de86` — schema v7: `/v2/read/*` cross-tenant surface scoped to
  a topology group with the corpus census beside rows; families block in the
  audit envelope by value; measurement identity route; **arm read from the
  sealed spec at `arm_key`**.
- Harmonia `b5498c162` — S17 narrative corrected; frozen rule stands; mechanism
  verified (high serial_ac → estimate *stable*; inference validity and
  estimate stability move in opposite directions).
- Herakles `19ad79d2e` — 69 PROPOSED templates in Archaeon's inbox; 68 are
  expansion requests; 41 requests collapse to 7 bench gaps, the largest being
  the outcome rule (two-arm comparison, aggregation over repeats, trend, string
  and set-membership checks).
- Archaeon `e3fab51cc` — region-directed template form; M-ELIGIBLE requests
  validating against Vivarium v3; PEW routing corrected to Mnemosyne.

## The one conflict that blocks M-ELIGIBLE's *legibility*

Daedalus reads the arm from the **sealed spec**; Vivarium's validator and
Archaeon's guard **banish** `arm` from the spec. Both rationales are correct
(mutable arm → re-drawable; label in the hash → split grouping surface). The
family can be issued now and will fossilize its observations with full queue
provenance, but its arms will not be legible from the engine's own record and
Stage 0's arm rules will still find nothing. **Harmonia's ruling on whether an
arm is provenance or execution input settles it**; Archaeon can implement
either resolution in a day. `roles/Daedalus/INBOX_ARCHAEON_ARM_KEY_CONFLICT.md`.

## Refinements to the assignment table

**Daedalus.** Add to "publish the arm contract": *reconcile it with
Vivarium's `_BANISHED` before publishing the example*. The read grant is
built; what is missing is a **grant instance** — `harmonia-m2`'s worlds must be
in a topology group and Harmonia (the group's creator) must grant Archaeon's
client. Suggest Daedalus supply the two commands and Harmonia run them. Also:
the measurement route means a chart can name its outcome path from the
engine's own declaration instead of Archaeon guessing `content.result.score`
— Archaeon will adopt it once a measurement is registered for
`evaluate_bitstring`.

**Vivarium.** Repeated execution is done. Remaining from the table: carry
`policy_version` and `template_id` into the PEW producer block (E1); bind
candidate sets to `selection` families (E6). For M-ELIGIBLE, the consumer must
preserve `family_id`/`arm_id` from the queue columns into whatever the arm
ruling chooses. Note `random_walk_v0` now exists: it is the first kind that
makes `repeat.state=persist` meaningful and is a candidate for the outcome-rule
gap Herakles measured.

**Mnemosyne (PEW).** The routing is corrected. The concrete ask: demonstrate
readback of one executed M-ELIGIBLE request — encounter, the four ordered
observations, family/arm, `policy_version`, `template_id`, resources — from
PEW alone. Today `players` / `ecology` / `resources_used` are 0/5452 in prod;
the campaign is the natural first population to fill them for.

**Proteus.** The frozen panel exists (64 specimens, `USE_A` only). What the
campaign needs is a *declared* subset with controls, and their crossing into
SFE at scale (2/64 today). Archaeon's `sfe.spec_players.v0` reads
`spec.pew.players` per observation, so a Proteus-run request that declares its
player is immediately attributable.

**Harmonia.** Three things gate M-SIGNAL and none can be Archaeon's: the arm
ruling above; qualifying the first detector used for directed selection (D3
`LOCAL_VARIANCE_ANOMALY` is the candidate — it is the one that is eligible on
live data and the one `bitstring.resample_region.v0` answers); and the
preregistration (endpoint, independent unit, budget, stopping rule). Archaeon
requests that the preregistration name the **unit** explicitly — S10's lesson,
now encoded in SFE's `unit_of_analysis` — because four repeats per world make
n=32 observations and n=8 worlds different numbers.

**Archaeon (self).** Issue M-ELIGIBLE on the operator's word once the arm
ruling lands; rerun Stage 0 unchanged; report eligible units and remaining
blockers. Implement the comparison-family reader over the read grant when the
grant exists. Triage Herakles's 69 into the expansion register by bench gap.
The region-directed template is PROPOSED; admitting it is the operator's act,
and until then every fired signal is honestly recorded as
`weak_signal_recorded_only` with the reason it could not direct.

## Two refinements to M-SIGNAL's design, for the record

1. **The frozen random control must be matched to the candidate universe.**
   `bitstring.uniform.v0` is frozen. If `random_walk_v0` or any admitted
   template widens the universe, the control becomes `random.v1`, separately
   versioned and drawn over the *same* widened universe. A directed policy
   compared against a narrower random control is not a comparison.
2. **Orders committed before execution, in the queue.** Both arms' full orders
   are registered as candidate sets (the unchosen cancelled) *before* Vivarium
   claims anything. That is what makes the comparison class-A rather than a
   story about what would have been chosen.

## Reporting format requested of every seat

    delivered artifact · exercised handoff · measured result · remaining
    blocker and its owner

Archaeon's own, as of this file:

    delivered   region-directed template form + bitstring.resample_region.v0
                (PROPOSED); M-ELIGIBLE builder, 8 v3 rows; census; registry;
                health report; expansion register; isolated worktree
    exercised   8 rows validated against Vivarium's live v3 validator;
                tick draws through the registry in production
    measured    195 tests; Stage 0 still KILL under declared tenancy;
                0 eligible S17 units; 1 of 6 detectors can direct (D3)
    blocker     arm legibility ruling (Daedalus/Vivarium/Harmonia); read-grant
                instance (Harmonia to grant); template admission (operator)
