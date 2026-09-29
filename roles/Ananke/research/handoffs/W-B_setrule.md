# Worker B: what does SETRULE contribute in PTE champions?

ID: W-B. Output: roles/Ananke/research/workers/W-B/. Namespace: 0x5E5.
Read COMMON_RULES.md first. Budget: ~3 h.

QUESTION
In the MAJ specimens 0a23398f20cc41a2 and f6b623cdb23afd2c ("M3"), turning
SETRULE off hurts, yet the readout site's rule index does not predict the
cue. One candidate account is that SETRULE's useful role is ESCAPE FROM
RANDOM INITIAL RULES (a bootstrap). Test that account hard. Does SETRULE
supply some more specific computational configuration (which sites run
which rule, when, conditioned on what), or ongoing gating that a bootstrap
account would miss? Then ask how general the answer is across C1 champions
that have rules > 1 and setrule on.

EVIDENCE POINTERS
- Specimens: c1b_run.load(cell_id). engine.World.__init__ (r initialized
  from rng stream INIT, mod rules); engine._tick (SETRULE semantics:
  r_next = A mod rules, applied after the program; Controls.freeze_rule).
- A rule census, freeze and swap probes on the two specimens:
  roles/Ananke/research/spikes/out/s_m3.json (script spikes/s_m3.py).
  Look at the per-trial and per-tick fields, not just the summaries.
- C1b battery (freeze_rule, adaptation_off, latency, drop windows):
  roles/Ananke/pte/c1b/C1B_SUMMARY.json.
- Carrier swaps at mid-interval on 12 C1 D-wave cells:
  spikes/out/s_ct.json (script spikes/s_ct.py).
- All C1 cells: roles/Ananke/pte/c1_rows/cells.jsonl.gz (fields levels,
  env, labels, result.champion, result.held). Filter for rules > 1 and
  setrule = 1 with held lo99 > 0.55.
- Prior art on configuration vs item memory (activity-silent / task-set,
  ping probes, swap vs reset): PRIOR_ART_temporal_distributed_computation.md
  s4 and s12.

THINGS TO CONSIDER
- Initialize r to a fixed value, or to other distributions, before the
  first tick (between-tick hooks can write w.r before step 1). Does
  SETRULE still matter?
- Which rule variants the champions actually run over time, per site;
  whether different sites settle on different rules; whether any rule
  pattern differs between mirror partners at ANY site or tick.
- Transplanting the settled rule configuration across worlds and physics.
- Whether frozen-from-start failure is about the rule the readout site
  runs, or about what the other sites run (per-site freeze).
- A census across all qualifying C1 SIGNAL cells, with a classification
  scheme you define in PLAN.md BEFORE looking at the census.
