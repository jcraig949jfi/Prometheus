# Worker G: does PTE contain any nontrivial retention regime? (adversarial, preregistered)

ID W-G. Output workers/W-G/. Namespace 0x5EB (and 0x5EC for a
confirmation set you never look at until your rules are frozen). Read
COMMON_RULES.md and COMMON_RULES_ARC3.md first. Budget ~4 h. CPU-first.

QUESTION
After a trial's query has passed, does any PTE champion retain information
about that trial's cue in a way that matters? Separate four levels, and
report each on its own:
  L1 PRESENT     the state still differs between single-cue twins;
  L2 DECODABLE   a held-out decoder recovers the cue from state;
  L3 EFFECTIVE   the retained information changes a future answer in
                 normal operation;
  L4 AVAILABLE   under an intervention or a changed readout/context
                 (e.g. a probe query, a readout moved to the storing site, a
                 task that rewards the old cue), the retained information can
                 be made to drive behaviour.
A permanent trace that correlates with history is L1/L2 at most, NOT
memory, unless L3 or L4 is shown. Also classify the mechanism of any
L2+ retention: true storage vs repeated regeneration vs environmental
accumulation (e.g. a plastic store integrating traffic) vs chaotic
divergence.

EVIDENCE (raw)
- A previous census and its code, PLAN, LOG and raw outputs:
  workers/W-E/ (ret_census.py, explore_hist.py, out/*.json). Its
  REPORT.md is an interpretation; see ARC3 rule 2 on reading order.
- Specimens: prometheus.ananke.c1b_run.d_wave_cells() (genome in
  extra.genome); M2 genomes spikes/out/champions_m2.json (physics/env via
  c1b_run.load("4ab2ba014aac967e")). Candidate cell ids of interest from
  the earlier census's raw outputs: f7e62fe3..., 0ad7dc00..., 6a47bd68...,
  M2 fresh3 (find the full ids in the rows or outputs).
- Engine: prometheus/ananke/engine.py (state arrays, plastic routing w,
  WIMM Kp, decay); lens.py (between-tick hooks; single-cue twins in
  cue_arrival_profile).
- Prior art on fading memory and memory capacity:
  PRIOR_ART_temporal_distributed_computation.md s3-s4.

REQUIRED
- Freeze PLAN.md (definitions of L1-L4 operationally, decoders incl.
  history-aware ones, the multiple-comparison correction, the decision
  rule) BEFORE touching the confirmation namespace.
- An adversarial stance: try to make a retention claim FAIL (e.g. show a
  decodable trace is explained by an accumulation that is not
  trial-specific, or that "availability" requires an intervention that
  itself writes the answer).
- Positive and negative control plants for each level (you may build hand
  plants in your directory).
DELIVERABLE: the report in your final message (ARC3 rule 1): verdict per
level per specimen; whether ANY nontrivial retention regime exists;
DISAGREEMENTS.
STOP: 4 h, or when the decision rule has been applied to the confirmation
set.
