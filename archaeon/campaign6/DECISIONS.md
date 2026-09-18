# Campaign 6 -- local campaign decisions

Format: D6-### | when (UTC, from the clock) | decision | evidence | alternative rejected |
revisit-if. Each decision states SCIENTIFIC DISCRETION or DETERMINISTIC.
Directive verbatim: roles/Archaeon/prompts/2026-09-18_campaign6/00_OPERATOR_DIRECTIVE.md.

D6-001 | 2026-09-18 20:08 | CAMPAIGN SHAPE: four phases and five gates (PLAN.md s1, s7); the
unit of preregistration is a generator + its frozen thresholds + the escalation
protocol, not a hypothesis; every run carries a sealed prereg-of-record (generator,
seed, lane label, live thresholds). Phase 0 builds and calibrates the observatory on
the OLD substrate before any expansion search. | Directive: "It fails if increasing
generative complexity makes SFE scientifically blind"; "The escalation machinery is a
primary Campaign 6 object of study". | Alternative: start the four axes at once and
bolt the observatory on -- rejected: recall cannot be calibrated on worlds with no
ground truth. SCIENTIFIC DISCRETION.

D6-002 | 2026-09-18 20:08 | FIVE QUESTIONS TO THE OPERATOR with defaults (PLAN.md s8): seats,
resource ceiling (14 d / 28 cores / 100 GB / 10,000 generations / 400 scatter runs /
>= 25% LLM-free by evaluations), Phase 0 first, replay depth, UNKNOWN assignment by the
judging seat. Defaults apply on silence and are recorded here when they bind. |
Operator online at the time of asking. | -- | Revisit on the operator's word.
SCIENTIFIC DISCRETION.

D6-003 | 2026-09-18 20:08 | IDENTITY AND PATH: campaign seed 20260923, client cmp6-archaeon
(self-registered on first engine contact, credential gitignored beside c6base.py),
ledger prefix L6; the campaign harness path for Phase 0/1 fixtures; Vivarium's queue
for the scatter and long runs once G6-1 is green (asked, not assumed). | D5-001 pattern.
| -- | Revisit if Vivarium declines the queue role. DETERMINISTIC.

D6-004 | 2026-09-18 20:12 | CONVERGENCE (CONVERGENCE_v0.1.md): the fleet's shape adopted -- T0 anchored,
SEGMENT as the unit, executor-side detectors with a PEW registry, atomic FREEZE before any
classification, commitments for fixtures, the reserved vocabulary. Lanes revised: Axis O is
Proteus's (graph_organism.v1); my "Representation G" withdrawn; fixture custody and
recall/classification adjudication are Harmonia's (with Nemesis authoring cheat fixtures);
my asks to Nemesis-as-keeper and Rhadamanthus-as-judge withdrawn; Axis W and P, the segment
loop, the eleven detector specs, escalation flows, tranche/search/long-run policy and the
return stay with Archaeon. Rulings R1-R9 consolidated for the operator. | #455 #456 #457
#459 #460; Harmonia lane report. | Alternative: keep my PLAN's lanes -- rejected, four seats
had converged first and the duplication was mine. DETERMINISTIC (adoption), SCIENTIFIC
DISCRETION (defaults in s4).

D6-005 | 2026-09-18 20:12 | PRE-REGISTERED CEILINGS (Daedalus's ask): first tranche 1e5 evaluations
per run with the full tier stack; ledger 10 GB per campaign phase; <= 64 checkpoints and
<= 256 artifact refs per freeze; 1e6 evaluations per run only after the engine acceptance
run at 3x rate and one scored recall pass. | Daedalus review s1, delta s3. | -- | Revisit
only upward and only after the two receipts. DETERMINISTIC.

D6-006 | 2026-09-18 20:48 | OPERATOR RULINGS R1-R9 RECEIVED AND FIXED (verbatim on file): R1 T0
anchored, gaps/chain breaks never normalized; R2 PARTIAL_FREEZE = explicit failure state
(missing members, owner, reason, timestamps), never counts as caught, never blocks the
firing; R3 Harmonia keeps + Harmonia/Nemesis author, no other authors without amendment;
R4 1,000-evaluation anchors plus structural boundaries, never retuned; R5 schema 10 before
production launch, scratch now; R6 PROTEUS-43 authorized, graph profile = expansion lane,
Proteus's falsifiers = its kill rules, multiple substrates allowed; R7 recall .90 / Wilson
lower .80 per bin (my .80/.60 default OVERRIDDEN), ceiling evidentiary not exploratory,
CAUGHT_RECALL separate; R8 envelope 14 d / 28 cores / 100 GB / 400 scatter / >= 25 percent
LLM-free, 10,000 generations = scatter HORIZON not maximum, promotion on preregistered
signals, breadth-for-depth inside the envelope; R9 Phase 0 required with the twelve G6-0
proofs; detector admission BASELINE_ADMITTED then C6_GEOMETRY_VALIDATED, thresholds never
tuned mid-campaign, UNABLE first-class; authorization items 1-7; scatter opens after G6-0.
| the rulings. | -- | Final. OPERATOR AUTHORITY.

D6-007 | 2026-09-18 20:48 | PROMOTION SIGNALS PREREGISTERED (R8): a run is promoted beyond the
10,000-generation horizon when, in its last 2,000 archived generations, any of: (a) the
elite fingerprint moved by more than the frozen novelty threshold (continued behavioural
change); (b) the set of resources_touched / env_dependencies of the top decile changed by
Jaccard > .5 (ecological turnover); (c) detector 1 or 11 fired without adjudication closing
it (unexplained novelty / unresolved anomaly); (d) detector 10 fired (disagreement); (e)
detector 1 fired after >= 2,000 generations of QUIET (innovation after stasis); (f) detector
4 fired on a component not previously reused (new structural reuse). A run is NOT promoted
when none holds (inert), regardless of depth quota. Promotion depth: to the next power of
two of generations, re-checked at each; at least three promoted histories to >= 100,000
generations if technically feasible within the envelope. | R8. | -- | Never revisited
downward. DETERMINISTIC (rules), SCIENTIFIC DISCRETION (the constants, before any run).

D6-008 | 2026-09-18 20:48 | FINGERPRINT ROW = proteus.behavior_fingerprint.v1 (Proteus, landed,
5 controls, <= 1 KiB, reward-shaped keys REFUSED by its cheat rule) plus a world-side
extension record keyed by the same (eval, organism_id) -- NOT a second emitter. Reward never
enters a fingerprint row (it lives in the archived-generation observation); my draft
fingerprint_v0 carried a reward field and is corrected. | Proteus REPLY_ARCHAEON_461_462. |
-- | -- . DETERMINISTIC.

D6-009 | 2026-09-18 20:57 | DETECTOR CALIBRATION, THREE ROUNDS BEFORE ANY FREEZE (all preserved under
observatory/CALIBRATION_round1_preserved.json, _round2_preserved.json, CALIBRATION_v0.1.json):
round 1 raw-count distance + reward-based labels failed novelty/discontinuity positives at
.09/.09; round 2 per-episode answer digests, log counts, transfer floor, displacement
labels: .22/.34, transfer 77/77; round 3 count weights .1, alive-moved positives for
novelty: discontinuity 744/744 at 6.27, novelty 484/489 at 5.76 (five cases listed),
transfer 77/77 + 0/1,051, disagreement/classifier definitional. STOPPED at round 3: the
five novelty cases are put to Harmonia, not tuned away. Detectors 4-9 NOT ADMITTABLE on v0
(UNABLE or no positive control) -> C6_GEOMETRY stage per the ruling. Candidate freeze =
DETECTORS_FROZEN_candidate.json (digest inside); Harmonia's admission freezes it. | the
three JSONs; ADMISSION_PACKET_v0.1.md. | Alternative: a 4th round to reach 489/489 --
rejected (tuning toward admission). SCIENTIFIC DISCRETION (instrument design),
DETERMINISTIC (the 1%/all-positives rule, unchanged through the rounds).
