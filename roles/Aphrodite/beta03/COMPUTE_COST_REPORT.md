# BETA-03 COMPUTE / COST REPORT

**Host:** M4 / HARRY1 (8 logical CPUs), CPU only. **Cloud spend: $0.00** (cap $6; no paid credentials used). No GPU.
No live models.

| Item | When (UTC) | Workers | Core-h (estimate; wall x workers) |
|---|---|---|---|
| W8 LIN 72-119 generation | 10-08 05:10 | 4 | < 0.1 |
| Foundry blocks A+B (6,912 families) | 10-08 05:10-11:44 | 4 | 26.3 |
| Known answers (K1-K5, K4, K5a-e) | 10-08 / 10-09 | 1-2 | about 1.5 |
| Leads: W5P build + tests | 10-08 | <= 2 | about 1.0 |
| Leads: g12 build + exposed smoke | 10-08 | <= 2 | about 1.5 |
| Leads: W9-H build + pilot | 10-08 | <= 2 | 1.8 |
| Leads: W9-H discovery pilot | 10-08 | <= 2 | 1.30 |
| Leads: O1 qualification | 10-08 | <= 2 | 1.13 |
| Leads: E6 runner | 10-08 | <= 2 | 0.1 |
| E1 + E2 donors, E1 starts / recipients / score | 10-08 11:44-14:18 | 4 | about 10.3 |
| E2 score + report | 10-09 05:15-05:48 | 4 | about 2.2 |
| E5-N sham / recipients (+ A3 rerun) / score | 10-09 05:48-07:34 | 4 | about 6.5 |
| W12 oracle walks | 10-09 07:37-08:18 | 4 | about 2.7 |
| **Total** | | | **about 60 core-h** |

**Rolling cap (48 core-h / 24 h):**
- The cap bound once, at about 13:07Z on 10-08 (an estimated 38.5 used, plus about 10 pending). The E1/E2 chain was
  stopped and relaunched E1-only. E2 scoring and E5-N were deferred to the 05:15Z roll-off.
- W04-W06 were compute-held windows as a result.
- **The estimated peak stayed at or below about 45 core-h.**

**Method:** wall-clock x workers (an upper bound). Per-process CPU accounting was not instrumented; that is a
recommendation for the next campaign.
