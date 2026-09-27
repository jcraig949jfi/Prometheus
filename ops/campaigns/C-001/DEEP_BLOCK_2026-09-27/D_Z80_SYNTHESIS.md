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
   - Archaeon: copiers are short input-gated loops, and establishment is gated by the environment, not by cargo (A0).
   - Two engines show cargo erosion directly and the third is consistent. This is the digital analogue of the classic "replicator
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

## 4. What this does NOT establish
- Point 2 in Archaeon is inferred from the architecture of short loops, not measured as cargo decay.
- The cross-engine points are recurrences across three designs, not a controlled comparison.
- Some BEE numbers (T-004) are verifiable only on M2 (W2 item 1).
