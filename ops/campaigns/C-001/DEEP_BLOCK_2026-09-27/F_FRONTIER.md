# Block F -- frontier (Archaeon, 2026-09-27)

Only questions that could change what Prometheus understands. None is launched. New Thread files: ops/threads/TH-013 .. TH-017.
Existing threads are revised in place with dated notes (TH-003 demoted; TH-002 sharpened).

| Thread | Type | Question | Why current evidence is insufficient | Engine(s) | New lens? | Cheapest discriminating next step |
|---|---|---|---|---|---|---|
| **TH-013** cargo erosion vs machinery conservation | SCIENCE / CROSS-ENGINE | Is "the copy core is conserved, cargo erodes unless paid for" a law of copy-selected byte worlds, and what is the minimal coupling that preserves cargo? | shown in NPE (C-CORE, one cell, thin margin) and BEE (endogenous task decay; v3 coupling); Archaeon only inferred | NPE, BEE; Archaeon (measure the founder-material share of established glins, already recorded) | no | DONE this block (block-13 probe): founder material 0.0 at every position (machinery and cargo). NEXT: record the members' byte STATE at the machinery positions (IBS) in the same replay; if the state is conserved while the material turns over, material IBD is the wrong carrier for 'machinery conservation' in encodings with neutral bits |
| **TH-014** harness-copy hazard as a ruler law | INSTRUMENTATION / CROSS-ENGINE | Can every reproduction ruler be required to enumerate all channels that move material (harness, migration, splice, transplant) and show zero credit leak? | three teams made the same error independently; nobody has a general check | all | no (a checklist + a synthetic leak fixture) | write one synthetic fixture per known leak (migration copy, splice, transplant) against the v0.3 validator: does the contract force an explicit non-organism carrier? |
| **TH-015** reproduction vs copying (Griesemer) | SCIENCE / NEW-LENS (partly) | Which recorded "reproductions" transmit the CAPACITY to reproduce, not just material? | the lens counts material flow; NPE predecessor births and BEE copy events often transmit material without capacity; no engine records capacity transmission per event | Archaeon (child re-run in isolation is cheap), BEE (the census of children), NPE (P-11 on the child) | maybe: a "capacity" field needs a per-child replay | DONE (block-13 probe): SELF_COPY 86.7%, HOST_EXECUTION 47.0%, NEIGHBOUR_COPY 35.3%, ORIGINATION 0% of children are copiers. NEXT: the same measure in BEE (census the children of traced births) and NPE (P-11 on the child) |
| **TH-016** code referent in evolved populations (B6 scale) | INSTRUMENTATION | How often, population-wide, does executing code's LOCATION misattribute its MATERIAL (BEE-wide; Archaeon hosting)? | 2 BEE runs chosen for richness; the Archaeon panel uses one resident | BEE (FULL replay recipe, portable to the nodes), Archaeon | no | run the T-001 recipe on a RANDOM sample of 20 BEE runs on ubu nodes (about 30 CPU-min); report the location/material divergence rate with a CI. Coordinate with Bellerophon first (overlaps TH-002) |
| **TH-017** dependence does not chain | SCIENCE (method) | Do lens errors cluster where a counterfactual-dependence result was chained like a production (flow) result (Hall)? | untested prediction from prior art | archival: the FALSE_FRIENDS ledger + historical claims | no | classify the 34 FF rows and the Block B error table by "chained dependence?"; one afternoon of reading |
| TH-003 (revised) | SCIENCE | NPE P-11-failing overwrite events are cross-execution-rich (46% vs 11%): is cross-execution the reason the donor fails to rebuild a random victim? | the "host-conditioned reproduction" framing is withdrawn (6/34 P-11-causal) | NPE | no | within the 34 preserved births, relate per-birth WHO != WHAT share to C2 draw outcomes (all in the T-003 output; no replay) |
| TH-002 (sharpened) | INSTRUMENTATION | does BEE's current `_is_self_copy` (pc < L) under-count SR from self-copied code? | 2-run probe | BEE | no | the same as TH-016's sample; count births that fail `_is_self_copy` only because of window-located own code |

## Host-conditioned assay (HOST_CONDITIONED_ASSAY_READINESS.md), re-assessed
- Its NPE arm was specified on predecessor-admitted births (W1). NPE does not count most of these as reproduction.
- Status recommendation: **NOT_READY** until the NPE arm is restated on P-11-causal events or explicitly on "overwrite events"; the
  original record stays as written.
- The Archaeon arm (by material) is unaffected. The BEE arm needs TH-016 first.


## Dated note 2026-09-28 (Archaeon, attribution v0): "founder material 0.0" is RETRACTED as unsupported
Defect in archaeon/causal_lens/deep_block/block13_probe.py (TH-007 metric):
`share = [sum(1 for c in members if w.orig[c][p] == fid*32+p) / ...]`
- The metric counted founder material only when it sat at the SAME position p.
- The founder (arrival 447492, tape 22592835581410fdf68ad092291919141850517b75b24d827228a45916f9863e) is a NEAR_COPIER. It has no
  exact self-copy on any input; its best copy has fidelity 0.9375 and a span of 30. So its material can land displaced.
- The measurement could not see displaced founder material. "0.0 at every position", "material identity turns over completely",
  and the Archaeon-vs-NPE contrast drawn from it are therefore UNSUPPORTED, not refuted.
The original text above is kept unedited. The corrected measurement (any founder id at any position, with its source position, plus
byte state, executed positions, isolated capability and knockouts through time) is archaeon/attribution/probes/th013_block13.py.
It runs on ubu002 from commit 3e6f281a1; the result goes in ops/campaigns/C-001/ATTRIBUTION_V0_2026-09-28/.
