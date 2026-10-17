# skullport_sdxl_concepts: what was and was NOT generated

Campaign ended after C5 by owner decision (2026-10-17); C6 (creatures units 1600-2095) was never flown.

| list | entries | seeds in prompts.json | generated | units |
|:--|--:|--:|--:|:--|
| racefaces | 66 | 16 | 1,056 (complete) | 0-1055 (scouts A/B, C1, C2) |
| garments | 45 | 16 | 720 (complete) | 0-719 (C3) |
| creatures | 131 | 16 | 1,600 | 0-1599 (C4, C5) |

Order is seed-major (every entry's seed 0, then every entry's seed 1, ...), so the 496 creature units NEVER
GENERATED are seed slots, not prompts: every creature has seeds k=0..11; entries 1-28 in prompts.json order
(through sk_cre_floating_skull... up to index 27) also have k=12; entries 29-131 (from sk_cre_hag, index 28) lack
k=12, and all 131 lack k=13..15. A missing creature file with k>=12 is unflown, not lost.
