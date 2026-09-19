# Nyx behavioral-cut plan for the ASAL low-score region
Nyx[gandalf-9e21f277], M3. PREREGISTERED, NOT YET RUN. Originally written 2026-09-19 (directive s5);
AMENDED 2026-09-19b (directive s2: two channels, the probe freeze, and the stop-condition correction).
Executes only AFTER the full-domain replication is frozen and executed (s11 order). Recorded now so it
is ready and so it cannot be shaped by replication results after the fact.

## The question (s5), not "can we cross?"
Crossings exist. The question is: WHAT DYNAMICAL OR REPRESENTATIONAL PROPERTY MAKES DISTINCT LENIA
PHENOTYPES OCCUPY THE SAME LOW-SCORE REGION? The cut is by BEHAVIOR, not by score. The job is to
discover what SEPARATES equivalently low-scoring organisms, not to force them into familiar categories.

## Unit of analysis
Preserved rollouts (frames + trajectories), keyed by stable stage/index identity (never the ambiguous
IC-CAT code: Harmonia #479 found 63 duplicated catalogue codes; index as the search did). Two strata:
  - STABLE region: rollouts that cross the reference under BOTH observers (post HARM-55/56).
  - DISCORDANT region: the flips HARM-56 preserves (crossings gained/lost, class flips). Under
    Harmonia disposition B these are not noise -- the discordance itself becomes a mechanism target.

## TWO CHANNELS (directive 2026-09-19b s2)

### DECLARED CHANNEL -- the 14 preregistered probes
Implemented and FROZEN at nyx/atlas/probes.py, source sha256
53f63df5b43d4eff58fe7820ae89767130a9a197a20d98b3e30c68a53730976d (probes.FREEZE), exercised ONLY on
synthetic fixtures (nyx/tests/test_probes.py, 17 tests). Frozen BEFORE any replication result exists.
Every probe is observer-independent by construction (no foundation model), which is the point: they
must be able to separate organisms the observer's representation maps to the same score.
  p01 coherence (coherent morphology vs turbulent texture)   p08 persistence
  p02 locomotion vs deformation                              p09 periodicity
  p03 identity half-life (stable identity vs turnover)       p10 spectral change
  p04 spatial frequency content                              p11 object/background separability
  p05 occupancy and edge density                             p12 morphology-preserving motion
  p06 temporal novelty IN PIXEL SPACE                        p13 catastrophic expansion/collapse
  p07 frame-to-frame displacement                            p14 scene-scale texture generation
p06 deliberately mirrors the ASAL score's functional form with NO learned representation, so a gap
between p06 and the ASAL scalar localises the effect IN the observer rather than in the dynamics.

### OPEN CHANNEL -- representation-light discovery
nyx/atlas/probes.py open_descriptor(): per-frame series (mass, centroid, radius of gyration)
summarised as level/variability/drift, plus the autocorrelation profile and the mean radial spectrum.
Downstream: clustering, nearest-neighbour anomaly search, trajectory/temporal/spectral signatures.
Its purpose is to expose structure the declared probes did NOT anticipate, so our own taxonomy does
not become the walls of the search.
  ANYTHING THE OPEN CHANNEL FINDS IS A NOMINATION, NOT EVIDENCE. It must earn confirmation on
  untouched data or by intervention/transplant before it is reported as a finding.

## Method (to instantiate after replication)
- Run the declared battery and the open descriptor over every low-score rollout in both strata.
- Declared channel: report which probes SEPARATE the low-score population and which do not.
- Open channel: cluster/anomaly-search the descriptors; every candidate structure is logged as a
  NOMINATION with the held-out data or the intervention that would confirm it.
- Any confirmed separator becomes a candidate MECHANISM registered in the mechanism ledger
  (nyx/atlas/gates/MECHANISMS.json) with its own id, falsifier and predicted intervention -- NOT a
  packet count. One nomination confirmed is worth more than fourteen probe values.

## STOP CONDITIONS -- corrected (directive 2026-09-19b s2)
CORRECTION to the earlier review-packet question 9.2. "The 14 probes found no separating axis" does
NOT establish "the low-score population is homogeneous." It establishes ONLY:
    PROBE_BATTERY_FOUND_NO_SEPARATOR
Do NOT kill the branch on that result alone. A stronger stop requires EITHER failure across
substantially DIFFERENT descriptions of the trajectories (the open channel, and ideally a third,
unrelated description), OR repeated inability to turn any proposed difference into a PREDICTIVE
INTERVENTION. Absence of a separator under one battery is a fact about the battery.
Conversely, if the low-score region continues to hold several genuinely different dynamical regimes,
that is the reason to go deeper: the object is the observer's many-to-one compression
(ANOM-ASAL-MANY-TO-ONE), which is potentially reusable machinery rather than "metric failure".

## What this yields for the pipeline
ONE candidate MECHANISM nominated for transplant (s7/s11): a dynamical property extracted from the
ASAL population, NOT the ASAL metric. Theophrastus tests whether that dynamic changes something native
to a receiving ecology (persistence, adaptation, exploration, recoverability, lineage survival, ...),
never CLIP score as the fitness function.

## Preconditions (do not start before all hold)
[ ] HARM-55 native Flax scores committed and verified against the frames128 manifest.
    (status 2026-09-19: original-observer column bit-identical over 395; Flax column DEFERRED on AVX
     host placement, Techne #488 -- an execution-placement issue, not a scientific one.)
[ ] HARM-55 native CONTROL ANCHORS scored through Flax (five garbage seeds, Orbium, static control),
    reported as VIEW 1 locked thresholds and VIEW 2 native anchors (directive 2026-09-19b s1).
[ ] HARM-56 object-level discordance map + one disposition A / B / C.
[ ] Full-domain replication frozen once (s4 controls satisfied; 100% of the declared domain executable
    or explicitly excluded BEFORE freeze) and executed.
[x] Probe battery frozen with code identity and definedness-checked on synthetic fixtures.
