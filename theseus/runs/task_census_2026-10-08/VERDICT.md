# THESEUS-31a verdict (prereg roles/Theseus/prereg/2026-10-08_task_census/, 1a2ad3157)

Run: python -m theseus.synth.task_census --tag task_census_2026-10-08 --workers 2 (wall 572 s,
CPU 1098 s; 0 blow-ups). Task: c3 cue recall, V = 4, k = 4, 400/400 episodes, seed 0;
channel 0 is a transient sensor; J = held-out ridge-readout accuracy (chance .25).

GATE: noop mean J .287 (<= .30); relay .987 (>= .45); memcomp 1.000 (>= .35). PASSES.

Census (viable v0_1 genomes; mean J / median J / share J > .35):
  A (LLM)   .964 / 1.000 / .96     E (deep+lens) .914 / 1.000 / .89
  D (deep)  .899 / 1.000 / .88     R (random)    .793 / 1.000 / .72
  C (6-way) .753 / 1.000 / .72     B (3-way)     .641 /  .616 / .51
  P (2-way) .609 /  .449 / .52     G0            .531 /  .287 / .36 (n 76)
H-TASK: D > one-shot (P+B+C) Mann-Whitney one-sided p = 6.3e-10; D > R p = .0037.
VERDICT: H-TASK SUPPORTED -- deep descendants carry a cue through 4 distractors more often
than one-shot collisions and than random programs complexity-matched to D.

Limits stated with the verdict (not reasons to discount it, reasons to test it next):
- CEILING: k = 4 is easy (medians 1.0 in five arms); differences live in the tails.
- MECHANISM UNKNOWN: a one-part relay (channel 0 -> another channel) suffices; nothing here
  says the deep advantage is compositional. R is matched to D on n_rules, C and max sources,
  which addresses the obvious "more channels" confound but not "more relays".
- The LLM arm, which designs memory on purpose, scores highest.
- One task setting, one seed, a ridge readout written by the builder.
Successor THESEUS-31b: harder settings (V 8, k 8), seed replication, and knockout
attribution (which rules carry the cue; one-part relay vs multi-part carrier) per arm.

Predictions: Q1 gate passes RIGHT; Q2 some arm >= 20% above .35 RIGHT; Q3 H-TASK not
supported WRONG (ledger).
