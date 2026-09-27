# R2 -- The no-gift soup: a design study (POI-033; territory D)

Output path: roles/<your-seat>/poi_R2/ . Reading and design, no campaign;
4-8 h. Read 00_READ_FIRST.md. This packet asks for a PREREGISTRATION DRAFT
and a feasibility pilot, not a result.

## Question
In a byte-tape soup with NO block-copy instruction, NO task reward and --
in a second variant -- NO predefined organism boundary, does anything
accumulate after replication appears, and how would we know, against a
random-walk baseline and a neutral shadow?

## Why it matters
Direct external prior art now exists: Cicala et al., arXiv:2607.09211 (v2
2026-09-02): random 32-byte Z80 programs, replication emerges, coevolves
with a polynomial task that raises interaction probability; LDIR block copy
available; runtime cost yields conditional execution; niches yield a
curriculum. Their two gifts (a block-copy op and an installed task) are
what Prometheus can remove. Replication itself is 30+ years old
(EXTERNAL.md s1); what happens AFTER it, without gifts, is open everywhere
(EXTERNAL.md s2).

## Read first
- EXTERNAL.md s1-s2, s7 (dead ends: trivial-copier collapse, shrinking
  replicators, well-mixed parasite extinction).
- raw/E1_alife_open_endedness.md PART 2-4 and its anti-gravity entries;
  raw/E2 open questions 1-2; raw/E6 s3 (conditions C1-C9).
- The three Prometheus Z80 worlds' docs (raw/I1 s1) -- what each installs.
- BEE physics v3 (prometheus/z80atlas/coupling.py header) as an example of
  an installed coupling to avoid or to use as a matched arm.

## What to produce
1. A GIFT INVENTORY: for BEE, NPE, Archaeon and Cicala 2026, list every
   installed advantage (copy ops, task reward, organism boundary, reaper,
   memory protection, mutation operator, world-made copies). Table.
2. A world specification with the gifts removed, in two variants
   (V1: organisms = tapes, no LDIR/LDD/LDI, no task; V2: one flat shared
   tape, no split, no protection, individuals identified afterwards by
   causal-lineage graphs).
3. What "accumulation" would mean there, operationally, with instruments:
   e.g. a routine written by one lineage reused by another (taint +
   knockout), rising functional complexity against a neutral-shadow run,
   a second transition (POI-039). Each with its negative/positive controls.
4. Required baselines: random sampling and random walk at matched budget;
   shuffled-interaction control.
5. A feasibility pilot (<= 1 h laptop, stdlib): can replication appear at
   all without block copy in a VM you can drive (e.g. BEE vm.py with
   ldir="off" -- check vm.execute's ldir parameter)? Report density per
   R1's method if R1 has not run.
6. A one-page preregistration draft: predictions, decision rules,
   eligible counts, kill criteria (including "no replication without
   gifts -> the gift was the result").

## Boundaries
No campaign. Nothing changed in any engine. The design may conclude "not
worth running" -- say why.
