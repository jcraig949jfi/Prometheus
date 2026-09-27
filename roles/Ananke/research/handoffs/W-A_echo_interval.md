# Worker A: what sets the useful delay of the M2 HOLD specimen?

ID: W-A. Output: roles/Ananke/research/workers/W-A/. Namespace: 0x5E4.
Read COMMON_RULES.md first. Budget: ~3 h of wall time.

QUESTION
The HOLD specimen 4ab2ba014aac967e (C1 cell; "M2") and three fresh-seed
champions evolved at the same physics are accurate at the trained gap,
and their accuracy changes when the gap changes. What physically
determines the interval over which they work, and can that interval be
moved by MINIMAL alterations (of physics dials, of the program, or of
both)? Determine the mechanism yourself. Treat any existing description
of it as a hypothesis to test, not a fact.

EVIDENCE POINTERS (raw data; read them, draw your own conclusions)
- The specimen: c1b_run.load("4ab2ba014aac967e"). Fresh champion genomes:
  roles/Ananke/research/spikes/out/champions_m2.json (keys 4ab2ba01,
  fresh1-3; same physics and env as the specimen).
- A gap sweep over the 4 champions: spikes/out/s_m2b.json (script
  spikes/s_m2b.py).
- Carrier swaps and decoders at mid-gap: spikes/out/s_m2.json
  (spikes/s_m2.py; the decision rule is in SPIKES_2026-09-27_PLAN.md).
- Cue-arrival lags at the actuator from single-cue twins:
  spikes/out/s_f.json (spikes/s_f.py).
- C1b battery on the specimen (per-carrier resets, flushes, delays):
  roles/Ananke/pte/c1b/C1B_SUMMARY.json.
- Engine semantics (tick order, delay formula, sync/async wake, inbox
  accumulation): prometheus/ananke/engine.py _tick and _emit; the spec is
  roles/Ananke/pte/DESIGN.md.
- Prior art on delay lines, recirculation and bundled-data pipelines:
  roles/Ananke/research/PRIOR_ART_temporal_distributed_computation.md s1
  and s6.

THINGS TO CONSIDER (not conclusions)
- Round-trip vs single-flight vs recirculation; the role of the sync
  update period and of inbox accumulation between wakes; the latency
  distribution (base, per-hop, jitter); distractor input during the gap;
  whether the readout is a sample at one tick or an accumulation.
- Whether all 4 champions share one mechanism.
- The gold standard (prior art s7.2): a reduced model that PREDICTS the
  accuracy-vs-gap curve from the program and physics, tested against
  measured curves at physics settings the champions never saw.
- A minimal alteration that MOVES the interval as predicted is strong
  evidence. One that fails to move it is informative too.

DO NOT run new evolutionary searches beyond 4 seeds x C1 SearchSpec, and
only if a re-evolution question becomes decisive (GPU lease required).
