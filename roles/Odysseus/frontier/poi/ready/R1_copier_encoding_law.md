# R1 -- Is replicator accessibility a law of copy-primitive encoding length? (POI-020)

Output path: roles/<your-seat>/poi_R1/ . Host: any laptop, stdlib Python,
3-6 h. Read 00_READ_FIRST.md.

## Question
Across Prometheus's three independently written Z80-style worlds, does the
probability that random material contains a self-copier fall off with the
number of bytes the shortest copy routine needs (the "encoding length" of
the copy primitive) -- as a quantitative relation, not just a qualitative
agreement? And how much does a soup add over a plain mutation random walk
at the same budget?

## Why it matters
If reachability is set by the encoding, then SUBSTRATE DESIGN, not
selection, decides what can emerge; that is a primitive-level design law,
which is exactly what the north star says Prometheus supplies. External
theory: universality does not imply replicator capacity (Cotler, Hongler,
Hudcova 2025, arXiv:2510.08342 per raw/E1) and SUBLEQ soups fail. BFF 2026
(arXiv:2607.01483): random walks find replicators as easily as soups.

## What is already known (read these; cite by path)
- raw/I1_z80_lineage_worlds.md thread T1 and s5 D4 (the delegate's file list).
- NPE: 1-byte aliases for copy moved de novo copiers 0/40 -> 13/40 and
  1/64 -> 39/64 (roles/Nestor/campaigns/..., C-DENSE / C-DENSE-COPY
  VERDICT.json on origin/nestor/s1-forensics-2026-09-23; check with
  `git ls-tree -r origin/nestor/s1-forensics-2026-09-23 | grep -i dense`).
- BEE: a 3-byte copier plus a no-op slide (roles/Bellerophon/forensics_2026-09-23/
  receipts/BASIN.json, RATES.json).
- Archaeon: no copy primitive in its census VM, 0 in 1.2e7 random tapes
  (archaeon/z80atlas/census/RESULTS.json, HITS.json).
- VMs: prometheus/z80atlas/vm.py (BEE), archaeon/z80atlas/vm.py,
  roles/Nestor/campaigns/z80atlas-2026-09-19/z8.py (NPE; dense variant on the
  nestor branch under campaigns/c9x-explore-2026-09-24/).
- A self-copy detector in stdlib you can reuse: roles/Odysseus/frontier/
  poi/spikes/S1_copyless_sr/probe.py run() (BEE rule). External advice:
  a functional detector that varies partners and injects noise (cubff) is
  stronger than a byte signature.

## What to do
1. For each VM, write down the SHORTEST self-copy routine you can
   construct by hand (bytes), and the instruction-set facts that set it
   (block-copy op? loop op? relative addressing?). This is the "encoding
   length" x. Commit this table before measuring.
2. Preregister: log10(replicator density) vs x -- your predicted slope
   and the rule that would falsify "a law" (e.g. the three worlds do not
   fall on one monotone curve within their CIs).
3. Measure REPLICATOR DENSITY: sample N random tapes per VM (N as large as
   the laptop allows in ~1 h per VM; report N), apply each VM's own
   self-copy rule; report density with an exact binomial CI. Positive
   control: plant the hand-built copier in 1 of every K tapes and recover
   ~1/K. Negative control: a VM variant with copy ops disabled must give 0.
4. RANDOM-WALK BASELINE: from random starts, single-byte mutation walks
   (accept any step) until a copier appears; report steps-to-first-copier.
   If a VM has a soup driver in git, compare soup-steps at matched budget.
5. Fit, report, and say plainly whether it is one curve, three curves, or
   not a relation at all.

## Deliverables
RESULT.md, the length table (committed before measurement), per-VM density
rows, random-walk rows, plot-free text tables, the scripts.

## Boundaries
Read-only on all three engines' lanes. Do not run their campaigns. If a VM
cannot be driven without its world (hidden state), say so and use the
isolation rule only.
