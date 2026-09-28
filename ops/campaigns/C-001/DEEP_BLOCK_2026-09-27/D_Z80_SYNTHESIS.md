# Block D -- cross-engine Z80 retrospective: what three lenses establish together (Archaeon, 2026-09-27)

Inputs:
- A0_ARCHAEON_LENS.md (Archaeon, first-hand);
- W1_NPE_LENS.md (worker W1, ubu001, isolated, from Git alone);
- W2_BEE_LENS.md (worker W2, ubu002, isolated, from Git alone).
Each engine claim below cites the lens file that reconstructs it; those files cite code and records.

## 1. The three lenses side by side

| | Archaeon (ENVGATE line) | BEE (z80atlas) | NPE (z80atlas / Cycle 9 / c9x) |
|---|---|---|---|
| WORLD | 32-byte tapes, 32-opcode VM, neighbour window, random inflow chambers; environment = the input stream | 64-byte tapes, Z80-like VM, own tape + window [L, 2L); 5 endogenous reproduction physics + EXTERNAL; energy/score coupling (v3: copy-resource ledger) | byte programs in an arena; ALLOC/BIRTH private-slot reproduction AND pair-tape co-execution; niches, reservoir, implants |
| ENTITY | cell occupant; parent chain vs genetic lineage (glin) | Org (writer / child); lineage (writer chain) vs glineage (resemblance) | Org with oid / anc / pid; body = slot; identity renamed in place on the pair tape |
| REPRODUCTION | writing >= 90% of the neighbour window (any mechanism) | a registered copy event; SR = own bytes, own code (pc < L), fidelity >= 0.9 before and after | private BIRTH (fid >= 0.9 and wrote >= half), or pair overwrite; causal only if P-11 passes (C2, C4, C5) |
| RULER that first misled | parent chain (executor label) | first_replication (junk events); material by resemblance; location-based own code | anc/oid identity certificate (H3/R0); the predecessor rule (prefilter); the recombination splice credited to the donor (Z80A-D05) |
| STRONGEST SURVIVOR | environmental blocking suppresses establishment (replicated x2); host-mediated reproduction by MATERIAL (72% of block-15 hosting births) | spontaneous own-code SR from random populations, CONFIRMED_CAUSAL (2.3% of fresh runs; needs LDIR + the NOP slide) | P-11 as an instrument; 57/1,031 causal pair events (depth <= 2); c9x: non-pair heredity only under permissive, experimenter-supplied physics |

## 2. The differences, sorted as the directive asks

**True substrate differences**
- **What makes reproduction possible at all.**
  * Archaeon: short input-gated copy loops.
  * BEE: an LDIR-class opcode plus undefined-byte-as-NOP drift into copy code.
  * NPE: pair-tape co-execution, or private-slot copying only under supplied self-location / energy / dense encoding.
- **Which B6 referent diverges.** BEE: WHERE vs WHAT (self-copied code in the window). NPE: WHO vs WHAT (threads run each other's
  code). Archaeon: both (E-001).

**Different definitions / rulers**
- "Reproduction" means three different predicates: window coverage, copy-event registration, and a slot birth or overwrite.
- "Spontaneous", "lineage" and "parent" differ (FALSE_FRIENDS FF-1..FF-34).
- These are not errors; they must be mapped before any comparison.

**Instrumentation gaps**
- BEE never persisted code material, so every WHAT claim requires a FULL replay.
- NPE persists WHO, not WHAT.
- PTE does not persist GA provenance.
- My BEE numbers rest on evidence only on M2's disk (W2 item 1; TH-006).

**Provenance / identity mistakes: the SAME class made independently by all three teams**

| mistake | Archaeon | BEE | NPE |
|---|---|---|---|
| label or location read as material | parent chain | resemblance `material`; location own code | anc/oid identity certificate |
| a harness channel copying material credited to organisms | Z80xAtlas "spontaneous" flags = seeded transplants | migration COPY under POLLINATION/RESERVOIR (0 -> 148/150 extinction when fixed) | the recombination splice credited to the donor (94% of fake replicators) |
| the first ruler fired on junk | -- | first_replication | predecessor rule vs P-11 |

## 3. What Prometheus can say ONLY because three engines looked

1. **"Harness channels that move material will be credited to organisms" is a structural hazard, not a bug of one team.** Three
   independently written worlds, three independent teams: each first-generation ruler credited an organism with copying that the
   harness or experimenter had done (transplants, migration copies, splices). One engine would call this a bug; three make it a
   design law. Every reproduction ruler needs an explicit "who could have copied this, including the harness" check.
   (Recurring despite all definitional differences.)

2. **Replicative machinery is conserved while cargo erodes, unless something explicitly pays for the cargo.**
   - NPE: founder material erodes to 13-25% while OP_SELF and LDIR persist (W1, x_content / c_core). Verified in
     roles/Nestor/EXPERIMENT_GRAPH.jsonl: X-CONTENT median founder share 0.134 / 0.253; C-CORE CONFIRMED 17/27 conserve positions
     23-24 and 52-53. Margin thin (17 vs 16.2); one cell (7ae3). The founder share is a lower bound.
   - BEE: under endogenous reproduction, seeded task code decays because selection sees only the copy routine (EXTERNAL reaches
     task solutions 178 vs 2 discordant pairs); only an explicit copy-resource coupling (v3) maintained competence (W2).
   - Archaeon (MEASURED this block, block13_probe_out.json): after 14,800 epochs the dominant block-13 lineage (127 members) retains
     founder MATERIAL at 0.0 of positions, machinery (the 16 addresses the founder executes) and cargo alike. Yet 82% of its 52,757
     births were exact 32-byte self-copies. So byte-level identity-by-descent turns over completely over long runs even where function
     must persist. Plausible cause: neutral bits within executed bytes (the opcode uses 5 of 8 bits). NOT measured: whether the
     members' byte STATE at the machinery positions is conserved (IBS); the probe did not record final genomes.
   - This DIFFERS from NPE: there the founder's fully specified world-op instructions (ED 32 / ED B0) ARE conserved as material.
     "Machinery conserved as material" is granularity- and encoding-dependent, not a law. The surviving cross-engine statement is
     narrower: machinery FUNCTION is conserved while cargo erodes (BEE, NPE); material identity of the machinery persists only where
     its encoding has no neutral sites (NPE yes; Archaeon no).
   - Two engines show cargo erosion directly; the third shows complete turnover of material identity (see above). This is the digital analogue of the classic "replicator
     shrinks to its replication core" result (Spiegelman; Block G). Its recurrence across three independent Z80 designs suggests it
     is a property of copy-selected byte worlds, not of one physics.

3. **Acquisition, establishment and maintenance are different barriers, and the hard one is not acquisition.**
   - NPE maps them explicitly: acquisition gated by encoding accessibility; establishment by register-state persistence; sustained
     heredity by tape-write erosion and per-edge certification failure (W1).
   - BEE: spontaneous SR is acquired in about 2.3% of runs, but task competence is acquired only for ECHO while its MAINTENANCE is
     robust under coupling (W2).
   - Archaeon: the environment gates ESTABLISHMENT (ENVGATE), while copiers arrive as a lottery (A0).
   - Different rulers, same ordering: making one convincing copy is easier than keeping a lineage.

4. **Origins are scaffolded.**
   - BEE: all 160 grounding-round self-replication origins were BUILT by another organism's prior copy activity (W2; verified:
     GROUNDING_REPORT.md "G6 origins: 160/160 ... BUILT_BY_COPY", including 87 origins while the initial organisms were alive).
   - Archaeon: resident genomes propagate through other organisms' execution (host-mediated, by material).
   - NPE: most confirmed causal copying lives in pair-tape co-execution, not private-slot autonomy.
   - Across three substrates, autonomous self-replication appears downstream of, and often still dependent on, other entities'
     execution. In Godfrey-Smith's terms these are scaffolded reproducers first (Block G). CAVEAT: for NPE this is about the pair-tape
     architecture, not the withdrawn "host-conditioned reproduction" claim (point 5).

5. **Correction to my own cross-engine claim (from W1):**
   - The NPE "host-conditioned reproduction" signature (16/34) was built on births admitted by NPE's weak predecessor rule; only 6/34
     pass P-11.
   - Its necessity leg uses a field NPE labels "diagnostics, not criteria".
   - The C2-false events ARE the events NPE's own ruler rejects as causal replication.
   - WITHDRAWN as a reproduction claim. What survives is NPE-consistent: P-11-failing overwrite events are rich in cross-execution
     (46% vs 11%).
   - The "three independent sightings of host-conditioned reproduction" therefore reduce to TWO (Archaeon by material; BEE
     foreign-material governance, 8,166 births in r016299, M2-local evidence) plus NPE's pair-tape scaffolding (point 4).

## 3b. Capacity transmission (TH-015, measured this block, Archaeon block 13; 4,079 sampled births)
The fraction of children that are copiers on their own (frozen copier ruler), by birth mechanism:

| mechanism | children that are copiers | sample |
|---|---|---|
| SELF_COPY | 86.7% | 1,827 / 2,107 |
| HOST_EXECUTION | 47.0% | 78 / 166 |
| NEIGHBOUR_COPY | 35.3% | 133 / 377 |
| ORIGINATION | 0% | 0 / 1,429 |

- Weighting by the native births per mechanism (SELF_COPY was sampled 1/25, the others fully), about 16% of ALL births in this world
  (8763 of 54616) transmit material but NOT the capacity to reproduce. Most of those are imperfect self-copies (13.3% of SELF_COPY) and
  all 1,429 originations.
- In Griesemer's sense they are copying, not reproduction.
- The lens has no field for this. The native birth predicate (window coverage) counts them all as births.

## 4. What this does NOT establish
- Point 2 in Archaeon: function conservation at the machinery positions was not measured (state not recorded).
- The cross-engine points are recurrences across three designs, not a controlled comparison.
- Some BEE numbers (T-004) are verifiable only on M2 (W2 item 1).


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


## Dated note 2026-09-28b (Archaeon, after adversarial Review 1, R1-6): what the retraction note left out
- The founder near-copier (arrival 447,492) was FAILING: 18 births, 6 exact in situ, dead by epoch 14,072.
- The lineage was rescued by HOST EXECUTION. Inert arrival 446,966 began running the near-copier's own code at epoch 14,001
  (archaeon/envgate/ENVGATE01_REVIEW_2026-09-24.md:239-245).
- When measured at 14,800 the lineage was about 800 epochs old. Background mutation also replaces material ids.
- "No exact self-copy on any input" is an isolated-VM test; "6 exact" is an in-situ count. Both hold.
- Any re-measurement must keep host scaffolding and displacement apart; TH-013 hypothesis 5 does.
