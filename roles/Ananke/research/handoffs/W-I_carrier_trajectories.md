# Worker I: how does causally used information move through carriers over time?

ID W-I. Output workers/W-I/. Namespace 0x5EE. Read COMMON_RULES.md and
COMMON_RULES_ARC3.md first. Budget ~4 h. GPU lease required for large
sweeps; CPU for small ones.

QUESTION
Replace "where is the bit?" with "how does causal information move through
carriers over time?". For a representative set of champions (choose it
to span physics and families; justify the choice in PLAN.md), measure
carrier identity at EVERY tick of the relevant interval (cue onset ->
readout). Report on TWO axes:
  (a) the PHYSICAL difference class from single-cue twins: which state
      differs (site registers, in-flight presence/count, in-flight payload
      value, routing, rule pointer), and who fires;
  (b) the READER-side carrier verdict from mirror-pair carrier swaps
      (FLIP / NO-EFFECT / CHANCE).
Do not infer the physical encoding from the reader's register alone.
Then look for RECURRING trajectory motifs (e.g. store -> emit -> channel ->
readout; repeated regeneration; travelling wave; temporary latch;
channel-only delay; site-only retention; source-presence). Only name a
motif if it recurs. Finally test whether trajectory class predicts
ROBUSTNESS (e.g. accuracy under +loss, +jitter, +latency, distractor
traffic, size), with the test defined in PLAN.md.

EVIDENCE (raw)
- Instrument: prometheus/ananke/lens.py (carrier_table, carriers, swap,
  cue_arrival_profile, arm_identical);
  instruments/INSTRUMENT_CARRIER_SWAP.md (failure modes F1-F8) and
  INSTRUMENT_TEMPORAL_REACH.md.
- A 166-cell single-tick census with raw tables: workers/W-F/out/
  (census_table.csv, census_s*.jsonl). A 13-specimen twin census with
  presence/fire/content counts: workers/W-C/out/x12.json, x1b_x5.json and
  wc_probe*.py.
- C1 rows: roles/Ananke/pte/c1_rows/cells.jsonl.gz.
REQUIRED: PLAN.md frozen (specimen set, tick grid, verdict rules incl.
how you handle mixtures where site_acc + chan_acc ~ 1, the motif
criteria, the robustness test) before the main runs. You MAY add a
two-axis reporting helper in YOUR directory (do not edit lens.py); the
principal may promote it later.
DELIVERABLE: the report in your final message; per-specimen trajectory
tables in out/; DISAGREEMENTS.
STOP: 4 h.
