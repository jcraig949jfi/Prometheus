# Item 8 -- the "material without capacity" births followed forward (Archaeon, 2026-09-28)

**Preserved earlier estimate (deep block, sampling-weighted):** 8,763 / 54,616 = 16% of block-13 births transmit material to a
child that is not a copier by the frozen ruler. It is kept as stated.

**Question:** is that material transient cargo, dead on arrival, potentially heritable, or carried by descendants whose capability
appears later? Directive item 8; the GP-introns warning applies.

## Run
- **Probe:** archaeon/attribution/probes/item8_block13.py, on ubu002 at commit 585ec427b (5,302 s).
- **Setting:** block 13, BLOCK_128 arm, replayed to epoch 20,000.
- **Output:** C:/Prometheus-data/evidence/attribution_v0_2026-09-28/item8_out.json (sha256 9c8ea0d1ae09...).
- **Sampling:** every 40th birth from epoch 13,900 was checked with the frozen ruler: 16,348 checked, of which 2,028 non-copier
  children (12.4%) and 14,320 copier children. The first 300 of each group were tracked. They were born at epochs 14,110-15,159
  (non-copiers) and 14,038-14,447 (copiers).
- **Descent:** each child inherits the tags of its TEMPLATE cell, the one that supplied more of its material.
- **Birth-created material:** the ids first created in that birth (mutation / input / constant / computed).
- **This replaces the item-8 tracking inside the TH-013 replay.** That tracking followed ALL of a child's material, mostly lineage
  material shared with its parent, and matched copier classes by wrong names. Its fates ("377/400 persist") are void.

## Result (fates at epoch 20,000; about 5,000 epochs after the births)

| | non-copier children (n = 300) | copier children, contrast (n = 300) |
|---|---|---|
| ruler class | INERT 197, TOUCH 93, WRITER 10 | EXACT_UNGATED 254, EXACT_GATED 41, NEAR_COPIER 5 |
| DEAD_ON_ARRIVAL (never a template for any birth) | 217 (72%) | 103 (34%) |
| TRANSIENT (had descendants, none alive at 20,000) | 83 (28%) | 195 (65%) |
| PERSISTS_NO_CAPABILITY | 0 | 0 |
| CAPABILITY_IN_DESCENDANTS (alive, a copier among them) | 0 | 2 (0.7%) |
| mean descendant births, among those with any | 11.7 | 6,532 |
| children carrying birth-created material | 180 (mean 1.9 new ids per child) | 46 (mean 0.3) |
| birth-created ids alive anywhere at 20,000 (descendant or not) | 0 | 0 |

## Reading
1. **In this block, over about 5,000 epochs, the non-copier births are dead-on-arrival cargo (72%) or transient cargo (28%).**
   - None has a living descendant at 20,000.
   - None of their birth-created material survives in ANY living cell. That includes cells that did not descend from them, so
     there was no carriage by recombination or host writes.
   - No case of "material carried by descendants whose capability appears later" was observed.
2. **"Transient" needs its contrast.**
   - Copier children also mostly leave no living line (lineage coalescence: 2/300 copier lines survive in a population of about
     125 cells).
   - The difference is in the dynamics, not the end state: non-copiers are 2x as often dead on arrival (72% vs 34%). When they
     do have descendants, they leave about 12 births against about 6,500 for copiers.
   - The non-copiers' descendants exist at all because OTHER cells copy them (neighbour copy / host execution). That is scaffolded
     transmission of cargo.
3. **Non-copier children carry six times more birth-created material** (1.9 vs 0.3 new ids per child; 60% vs 15% carry any).
   - This is consistent with copy-errors and mutations breaking the capability, a proximate cause of "material without capacity".
   - 120 non-copier children have NO new material. They are incapable with inherited material only: children of non-copier
     templates, or breaks at non-new loci. Not resolved here.
4. **The GP-introns warning, answered for this horizon.** No inert payload persisted, activated later, or was carried by
   recombination within 5,000 epochs. This does not show it could not matter on a longer horizon, or in a world with
   recombination pressure. In block 13 recombinant births are 0.07% of births (440 / 655,307: SELF_COPY+RECOMBINATION 318, HOST_EXECUTION+RECOMBINATION 119, ORIGINATION+RECOMBINATION 3; TH-013 replay).

## Limits
- One block, one arm. The sampling window is epochs 14,038-15,159 (the tracked quota filled fast), so the fates describe children
  born during the lineage's expansion.
- n = 300 per group. The horizon is about 5,000 epochs.
- Descent tags follow the template majority only; minority material inherited by a child is not tagged as descent (it is covered
  by the birth-created-id check, but only for NEW ids).
- NOT adversarially reviewed (Reviews 1 and 2 predate this result).
