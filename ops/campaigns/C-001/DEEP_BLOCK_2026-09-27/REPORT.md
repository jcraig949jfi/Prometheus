# Deep research block 2026-09-27 -- integrated report (Archaeon)

Directive verbatim: roles/Archaeon/prompts/2026-09-27_deep_block/.

Section files in this folder:
- A_E002_REVIEW.md
- B_B1_B6_B8.md
- C_B7.md
- D_Z80_SYNTHESIS.md (with A0_ARCHAEON_LENS.md, W1_NPE_LENS.md, W2_BEE_LENS.md)
- G_PRIOR_ART.md
- F_FRONTIER.md
- E_DELEGATION_H_ROLE.md
- block13_probe_out.json

## 1. E-002 review
Survives:
- the self-cross correction (4/16; the tie is a self-cross);
- the saturated-ruler critique of 3/48 (my own v0.2 claim was wrong: "untestable", not "not supported");
- the inert-bit test M1 (7/12 genuine crossovers flip; the worker's 10/15 blends in 3 self-crosses);
- the observation that v0.1 and v0.2 counted different referents.

Fails:
- C-OP' clause (b). It significance-tests one realized operator draw. Children byte-identical to a parent get ILL_POSED when the parents
  are close (E1b, E4), a 75-81% distinguishing share is ruled "no parent" by convention, and there is no null for asymmetric operators.
- "Nearly every recombinant has no singular parent" restates alpha.

Narrowed proposal: report per-child FLOW and DIFFERENCE shares as graded quantities, with any singular label a declared convention.
Keep self-cross collapse and NI-on-missing-evidence. PROPOSED only.

## 2. B1 / B6 / B8
All nine documented attribution errors fit THREE axes plus one operation:

| axis / operation | meaning | covers |
|---|---|---|
| CARRIER | WHO / WHERE / WHAT | B2, B3, B4, B6 |
| RELATION | FLOW = identity by descent; RESEMBLANCE = identity by state (DIFFERENCE = IBS at informative units); DEPENDENCE = necessity / sufficiency under a named intervention | B5, B8 |
| CONTRAST | the baseline a difference is relative to | B7, the self-cross, C-OP' (b) |
| aggregation | per-unit facts -> organism-level lineage | B1 |

B8 is NOT a new break. It is IBD vs IBS, already present as FF-4/FF-27, and I recommend not naming it. The distinctions map
differently per engine; nothing requires identical mechanics.

## 3. B7
- Ceiling ties among materially distinct entities are common: PTE 8 genomes; census 95 tapes / 5 architectures; Ares 56 runs / 11
  structures.
- But the engines' own teams mostly guarded against reading ties as mechanism, twice in preregistered designs.
- The one documented misreading is mine: a ruler imported into the cross-engine lens without its guard.
- Narrow statement: a task ruler at its ceiling identifies neither mechanism nor lineage; the hazard is concentrated where rulers
  cross boundaries.
- Consequence: any behavioural ARCH criterion must carry a non-saturation guard.

## 4. Z80 synthesis: what only three lenses establish
1. **Harness channels that move material get credited to organisms.** The same error was made independently by all three teams
   (transplant flags; migration copy; recombination splice). It is a design law, not a bug (TH-014).
2. **Cargo erodes while copy FUNCTION persists unless paid for** (BEE, NPE). But material identity of the machinery is conserved only
   where its encoding lacks neutral sites. NPE conserves OP_SELF / LDIR as material; Archaeon's dominant block-13 lineage retains 0.0
   founder material at every position after 14,800 epochs, despite 82% exact copies (measured this block) (TH-013).
3. **Acquisition, establishment and maintenance are distinct barriers, and acquisition is not the hardest** (all three, different
   rulers).
4. **Origins are scaffolded.** BEE: 160/160 first self-replicators were built by others' copying (verified). Archaeon: host-mediated
   propagation by material. NPE: causal copying lives in pair-tape co-execution.
5. **Correction:** NPE "host-conditioned reproduction" is WITHDRAWN. It rested on predecessor-admitted events (only 6/34 are P-11
   causal) and on a diagnostic that NPE does not certify (found by worker W1). So "three independent sightings" become two, plus
   NPE's pair-tape scaffolding.
6. **About 16% of births in Archaeon block 13 transmit material but NOT the capacity to reproduce.** By mechanism, children that are
   copiers: SELF_COPY 86.7%, HOST 47%, NEIGHBOUR 35%, ORIGINATION 0% (measured this block) (TH-015; Griesemer's challenge).

## 5. Prior art
Rediscoveries:
- FLOW / DIFFERENCE = IBD / IBS;
- B1 = the ancestral-recombination-graph view (genealogy is per locus);
- B5 / RELATION = Hall's production vs dependence (production chains, dependence does not);
- execution vs copying = von Neumann's dual use of the description;
- host-executed copying = Tierra parasites;
- scaffolded origins = Godfrey-Smith;
- cargo erosion = Spiegelman's monster;
- lineage tracking under recombination = Moreno / Dolson / Ofria (reuse it).

Challenges:
- Griesemer: the lens counts copying as reproduction.
- ARG practice: keep per-locus ancestry; don't significance-test singular parents.
- GP introns: "inert for attribution" is not "inert for evolution".

Genuinely different in Prometheus:
- code LOCATION as a misleading referent, quantified;
- one question across three independent substrates;
- per-event named-intervention counterfactuals.

## 6. Frontier (F_FRONTIER.md, threads TH-013..TH-017)

| thread | question | cheapest next step |
|---|---|---|
| TH-013 | cargo vs machinery | record machinery STATE in the same replay (is function conserved while material turns over?) |
| TH-014 | harness-leak law | synthetic leak fixtures against v0.3 |
| TH-015 | capacity transmission | the same measure in BEE / NPE |
| TH-016 | B6 at population scale | a random 20-run BEE sample on the nodes (coordinate with Bellerophon) |
| TH-017 | dependence does not chain | archival classification |

Also: TH-003 revised (cross-execution in P-11-failing overwrites), and the host-conditioned assay re-assessed NOT_READY.

## 7. Delegation
- Three isolated Claude workers (W1 NPE lens, W2 BEE lens, W3 B7 scan) on ubu001 and ubu002, each 8-13 min, from Git only. Relayed
  by git bundle, unedited.
- Isolation by an empty CLAUDE_CONFIG_DIR worked, but it silently switched the model to Sonnet 5.
- The workers' "audit Archaeon's claims" leg found three over-claims of mine.
- One 66-min deterministic replay (the block-13 probe) ran on ubu001.
- No packages were installed.
- Remaining M2 ties: the relay, and the M2-local BEE / NPE evidence (TH-006).

## 8. Role learning
- **Archaeon's value** was integration: axis reduction, cross-engine claims, attacking proposals, adjudicating worker critiques.
- **Better delegated:** reconstruction, scans, replays.
- **Should become reusable:** the observation-only VM probes and the audit-prompt pattern.
- **Caution:** Archaeon's own synthesis accumulated over-claims that only an independent adversarial worker caught; it should run
  with one attached by default.

## Also
**Probes and replays executed:**
- C-OP' edge battery (M2, < 1 s);
- block-13 probe (ubu001, 3,479 s, 456 MB);
- the three worker sessions (read-only plus small analyses).

**Failed attempts / defects (mine):**
- E4 fixture mis-specified, then fixed;
- a sampling-biased "a third of births" statement, corrected to 16%;
- the ubu worktree stagger was needed.

**Historical interpretations changed:**
- v0.2 "3/48 not supported" -> untestable;
- v0.2 "1/16 tie" -> self-cross;
- AN6 v0.1 vs v0.2 -> a referent switch, not a correction;
- NPE host-conditioned reproduction -> withdrawn;
- "B6 FF-11 repaired" -> representation only (NPE's C9-D14 remains open);
- "4 P-11 tests" -> 3 criteria + 1 diagnostic;
- BEE own/win steps "native" -> forensic-tool fields;
- lens class names are Archaeon's, not BEE's;
- host-conditioned assay -> NOT_READY.

**Challenges to operator assumptions:**
- B6 stands as cross-engine (confirmed by W2 against BEE's CURRENT code). But the host-conditioned part of the B6 story, which the
  operator welcomed as a cross-engine result, is weaker than presented: NPE's leg is withdrawn.
- B7 is not a broad engine failure. The engines guard it; the lens didn't.
- B8 should not be named; it is textbook IBD / IBS.
- Several of Prometheus's "new" concepts have mature external names. Adopting them would prevent re-deriving known pitfalls.

## Ops-pilot finding: thread ID collision (occurred during this block)
- Aether's research block (roles/Aether) opened TH-007..TH-012 on main while this block drafted its own TH-007..TH-011 on a branch.
  Git surfaced it only at merge (add/add conflicts on five files).
- This block's threads were renumbered TH-013..TH-017, with every reference updated. Worker outputs W1-W3 are unedited, and they did
  not cite thread numbers.
- The one-file-per-object layout avoids EDIT conflicts but provides no ID allocation. Two seats working in parallel will collide
  again.
- The smallest remedy the evidence justifies: allocate an ID by committing an empty stub to main before drafting (claim first). Not
  built here; recorded for TH-006 / the pilot.


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
