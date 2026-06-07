"""Greedy substrate consumer for Learner LoRA training data.

Walks every substrate source we can find, converts heterogeneous
records into reasoning-oriented (prompt, completion) training examples,
tiered by trust, and assembles a training-ready corpus + manifest.

Built 2026-06-03 per James directive: "build a greedy consumer that
scrapes all of the substrate you can find as LoRA training data ... see
if ingesting it moves the needle towards mathematical reasoning."

Discipline carried in regardless of greed:
- Nemesis adversarial data is EXCLUDED (it is eval-only by design).
- A held-out gold true/false slice is reserved and never trained on.
- Volume is capped + stratified per source so no single source
  re-creates the monoculture the audit flagged.
"""
