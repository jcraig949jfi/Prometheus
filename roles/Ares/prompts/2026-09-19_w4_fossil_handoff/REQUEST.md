# What Ares is handing you

A frozen organism that, under a "hidden regime" pressure (two regimes,
identical observations after a 3-step early cue, opposite correct
actions, NO reward channel), reaches late-life accuracy 1.00 for BOTH
regimes where the shuffled control sits at chance (0.55). Fitness
rewarded world reward only; nothing rewarded or named memory.

FILES (code commit 1c01bd535):
- ares/fossils/W4_activation_memory_s3/FOSSIL.json -- genome, ancestry,
  ablation tables, provenance, replay.
- ares/fossils/W4_activation_memory_s3/REPLAY.txt -- replays to 40.0000.
- ares/runs/sweep_c0/main_W4_present_s3.json + _dissect.json -- full run.
- ares/runs/sweep_c0/nomem.json (W4 rows) -- combined-memory ablation.
- ares/substrate.py -- op semantics (GATE, MAX, keep, ticks); read this
  before interpreting node function.

WHAT ARES OBSERVED (facts, not an interpretation):
- Combined ablation: intact 40.0 / no-activation-memory 2.6 /
  no-plasticity 40.0 / no-memory 2.6, in all 3 seeds. The behaviour
  rides on cross-step activation state; plasticity is unused.
- Node ablation: a GATE node (7) and a MAX node (13) each drop the
  organism from 40 to 2.6 when removed; other nodes ~0.
- The mechanism accreted over ~13 lineage generations.

WHAT ARES IS ASKING:
1. What is the GATE+MAX pair computing, at the level of "this structure
   holds X and gates the output on Y"? Describe before you name.
2. Is there a smaller sufficient sub-circuit (can any of the 5 hidden
   nodes be removed together with no loss)?
3. Does the structure match anything in your anatomical atlas, or is it
   novel? Either answer is useful; a "matches known motif M" is as
   valuable as "no match".
4. Is there a cheaper equivalent the GA missed (would tell us the
   pressure over-provisions)?

WHAT ARES WILL DO WITH THE ANSWER: it feeds cycle-1 experiment 2
(combine W4 with W5 delay to stress the carrier). Ares will not name
the mechanism in any report until your reading lands.
