# Dossier G - CW01 and Archaeon Campaigns 4/5: prior lessons for NPE

Reader-historian dossier, 2026-09-30. Read-only harvest; no runs, no git writes.
Scope: computational only (integer programs on bounded VMs, GA policies, tensor-train policies, tree/tape genomes).

Sources read (all paths absolute or relative to `F:/Prometheus-worktrees/nestor-d2v13/`):

- CW01 campaign root: `roles/Nestor/campaigns/cw01-2026-09-17/`
  - `CAMPAIGN_STATE.json` (e01-e10 dispositions, headlines, limitations)
  - `DEFECTS.jsonl` (92 entries; cited by id below)
  - `loop/LOOP_RULES.md`
  - `loop/BOUNDARY_REPORT_2026-09-18.md` (cycle 1), `..._CYCLE2..CYCLE8_*.md`, `..._ARCH4_2026-09-18.md`
  - `loop/CYCLE_REPORT_CYCLE8_2026-09-19.md` (read by grep; lines 322-355 for P-J02/J03/J05/J06/J07)
  - `experiments/cw01-e05/MECHANISM_OF_NULL.md`, `experiments/cw01-e09/SUBSTRATE_RECONCILE.md`
- Archaeon: `roles/Archaeon/REVIEW_PACKET_CAMPAIGN4_2026-09-18.md`, `REVIEW_PACKET_CAMPAIGN5_2026-09-18.md`, `ENGINE_LANDSCAPE_2026-09-25.md`
- Memory notes (`C:/Users/jcrai/.claude/projects/F--prometheus/memory/`): `project_nestor_cw01_priority_loop.md`, `project_nestor_cw01_e07_closed.md`, `project_nestor_cw01_e08_closed.md`, `project_nestor_cw01_e09_closed.md`, `project_nestor_arch4_reactivation.md`, `feedback_count_fixing_damage_rulers_manufacture_coordinates.md`, `feedback_preregistered_rules_need_an_eligibility_count.md`, `feedback_frozen_instrument_is_not_validated.md`, `feedback_similarity_is_not_copying.md`.

Not read in full: the six largest cycle reports (CYCLE3-CYCLE8, 42-169 KB each), the per-experiment PREREGISTRATION/PACKAGE files for e01-e08. Their conclusions are summarised in the boundary reports and CAMPAIGN_STATE, which I used instead. Numbers below are quoted from those summaries.

---

## 0. The one framing fact to carry into NPE

**In every CW01 and Archaeon C4/C5 substrate, heredity was imposed from outside.** The evolver copied (or mutated) parents; organisms never built their children. The cycle-8 genealogy says it directly: "every birth is a mutation; 'copy' never occurs" (`CYCLE_REPORT_CYCLE8`, line 343, P-J05). So none of this history measures *endogenous* heredity. What it does measure is:

- how reachable new computation is under exogenous heredity,
- what damage and robustness look like in byte-program VMs close to NPE's Z80-like organisms,
- which instruments lie.

NPE's question (does heredity arise from programs writing programs on a pair tape?) sits one level below all of this. The findings transfer as **priors about search, valleys and rulers**, not as priors about replication. The only replication-shaped lesson from this era is the similarity-is-not-copying incident. It came from the Z80 x Atlas rehearsal that directly followed CW01, not from CW01 itself (section 2.4).

---

## 1. What CW01 and Archaeon C4/C5 established

### 1.1 CW01 experiment line e01-e09 (`CAMPAIGN_STATE.json`)

| exp | question | disposition | load-bearing numbers |
|---|---|---|---|
| e01 | workspace emergence under necessity | COMPLETE | +9.70% ancestor-relative (worst +7.74%); intervention dependence -10.2%; evolved p_write .87, p_reenter .87, persist 45.6 steps; zero-recurrence control evolved *away* from retention (p_write .27). 5-gene policy only. |
| e02 | ancestral efficiency ratchet | NULL | +174% ancestor-relative, but p_factor fixes before p_norm 6/6: the "foundation" was an enhancement, not a precondition. Population converges in <10 generations (+203% in gens 0-9, then flat for 70). Neutral hitchhiking: neutral genes drift +.111/-.082 because elites are copied wholesale. |
| e03 | sparse computational coalitions | COMPLETE | Sparsity .24, MI excess 1.19 bits, I1 collapses 4/4. Key control: a non-conditional arm is maximally sparse and completely blind (MI 0.000). **Sparsity is not conditionality.** |
| e04 | queue/TTL ecology | INCONCLUSIVE | Triage MI .28 bits 4/4. Generality inverted: improves under less pressure (TTL half -14.8, double +5.2). |
| e05 | mixture of marginal organisms | NULL | Beats best single 12/12. Superadditivity and full load-bearing fail in the *same* replicates, 12/12 agreement across r01-r12 (7/12 pass). M3 interaction 11/12, not 4/4 as first stated. Failure is the drawn world (effects span -4.8 to +28.2; null bands 13.4-17.5). |
| e06 | representation ecology TREE vs TAPE | INCONCLUSIVE | Mutual invasibility never held; TAPE invades TREE .104 -> .740, never the reverse. D054/D055: the target was generated in TREE's native form, then the redesign flipped the advantage. |
| e07 | computational weather / damage | INCONCLUSIVE / DESIGN UNREACHABLE | Gate refused the world twice. D058: P1 needed accumulator AURC <= .90 at f=.20 but measured .944; attainable only at f >= .44. D059: evolution never reaches state use (intact .35-.45 vs hand-built .74; state dependence .05-.09). |
| e08 | rank-tax tensor evolution | INCONCLUSIVE | Burden CONTROL 1.73 / TAX .83 / AMP .93 / TAX+AMP .51 at unchanged held64 (156/155/156/171). 4 competent lineages vs a frozen minimum of 6. The pilot had shown only 2/4 competent (D065/D066). |
| e09 | algorithmic soup / composition | INCONCLUSIVE / DESIGN UNREACHABLE at reconcile | The organism's only act is `pend[target] += (action % 8) * 251` (`np_world.py:92-102`): no call, compose or reuse. 3-op chains overfit train8 (up to 1868 vs abstain 1272) and score 145-166 on held64, at or below the abstain floor 159. Scrambled op tables do as well as arithmetic ones. |

**Why "design unreachable" happened, twice, in one sentence each:**

- **e07:** the *search* never reached the state-using region the damage question needed, and the gate threshold was unattainable at the primary dose anyway.
- **e09:** the *organism representation* contained no operator for the phenomenon (no composition primitive). Writing a VM would have been inventing the answer.

Both are reachability failures of the design, discovered by cheap probes before evolution: a 2 s/run gate for e07, a 32 s probe for e09. That saved a 96-lineage EXECUTE in e07.

### 1.2 Archaeon Campaign 4: damage geometry and evolvability on the Proteus VM (`REVIEW_PACKET_CAMPAIGN4`)

- **The substrate is total.** The interpreter reduces opcodes mod 25, operands mod register/tape counts, and jumps mod tape. 932/932 parent instruction words are out of table, and P(would-be-fatal) = 1.000 on 7,146 children. There is no fault boundary, so D0/D1 cannot fire and C4-03/C4-07 closed REPRESENTATION_BLOCKED.
- **Damage is a cliff, not a slope.**
  - Displacement is bimodal: 0 or > .75, with only 1-3% in between.
  - Loss by radius 1/2/4/8/16: .522/.664/.834/.930/.989.
  - Neutral fraction falls from .467 to .004.
- **Zero beneficial edits.** D7 = 0/5,472 single edits and 0/2,280 multi-edits. Exaptive edits 34 (0.6%), 30 of them on "shelf" parents.
- **Neutral network.**
  - 188/188 walkers reach depth 16 at ~.55 acceptance.
  - Held-out exaptation .016/.032/.037/.043 at depths 2/4/8/16. The single-edit value is .006.
- **Recombination.** 0/12 crossings. Mate-splice viability .734 vs .815-.820 without splicing. Recombination "adds damage without reach".
- **Selection builds robustness as neutrality plus length.** Single-edit loss .419 / .185 / .125 (ancestral / ordinary / doubled-load descendants), with length 19 / 40 / 62. Labelled ROBUST_WITHOUT_MECHANISM.
- **Addressing.** P(broken jump | length-changing edit with a reachable jump) = .423. Insertion +.215 and movement +.193 are the damaging kinds.
- **Ecology.** Lateral rescue takes over populations without improving them. Three worlds were pre-solved by design defect.

### 1.3 Archaeon Campaign 5: escaping the neutral cliff (`REVIEW_PACKET_CAMPAIGN5`)

**Phase A: the old substrate is exhausted.**

- Deep walk to depth 64: exaptation .050 -> .064 -> .078 -> .082. Yield per evaluation (.00082-.00127) is no better than a random single edit (.0012).
- Fair lateral ecology at equal compute: 0/24 cells improved; in 14/24 the elite equals the starting parent.

**Phase B: representation B (narrow encoding, FAIL/FIZZLE on out-of-range fields).**

- Creates a real, countable local failure.
- Single-edit REAL_LOCAL_RECOVERY: 229 recoveries vs 154 insulation losses.
  - Opcode faults recover 209 / lose 15.
  - Register faults recover 25 / lose 142.
- Recovered children sit at displacement .015 from the parent.
- Robustness is carried by length, not dead code: dead-code ablation .435 -> .409 neutral.
- **At equal compute:** net 0 / +1 / +1 over 96 cells, and the first held-out gain over the starting best appears in none of them. Verdict BOUNDARY_CREATED_NO_DISCOVERY_GAIN.
- **Dominant fact of both phases:** "the flat elite". 100-180 generations of N=50 move nothing.
- **Flag.** C5-03 qualified only under one labelled post-hoc amendment (F3 statistic changed from fault counts to distinct sites). Phase B is void if that amendment is refused.

### 1.4 Archaeon C4 reactivated inside CW01 (T-ARCH4; `BOUNDARY_REPORT_ARCH4`, cycles 2-5)

**Locality law (P-C15, P-C04):**

- Blind scattered deletion loses more than contiguous deletion of the same k at every fraction: .564/.761/.878 vs .463/.652/.795.
- Block edits lose less than distributed edits at radius 4: .569 vs .630.
- Cycle 2 (P-D01, 57,536 rows) turned the law into a surface. Loss rises +.145 per doubling of *units lost* but only +.024 per doubling of *sites*. Operands are the soft coordinate (.36 vs .72-.75 for delete, opcode and move).

**Caveat.** Cycle 5's ruler audit (section 2.2) later showed that the length and set effects in P-D01 were count-fixing artefacts. The *operand softness* survived the ruler change (-.19). The locality comparison itself was same-k and paired; I found no record that it was re-read on a Bernoulli ruler. Treat the locality law as **measured under a count ruler and not re-audited**.

**Trap-to-NOP walks grow by acceptance, not by proposal (P-C03, P-C16, P-D03):**

- Trap-to-NOP raises acceptance from .602 to .673 and length from +.30 to +1.80.
- Length-balanced proposals still grow (+2.35).
- A no-growth acceptance rule reverses growth (-3.1 / -6.0). So does a length cost (-1.4 / -3.1) or trap-HALT (-.76).
- When growth reverses, exaptation rises from .032 to .064-.074 and structural diversity from 1.19 to 1.56-1.64. **Neutral length accumulation suppresses exaptation.**

**Other T-ARCH4 results:**

- Operand slot ordering a > b > c (register field .36, b .11, c .05) holds in every stratum and on held-out families within reached code. Promoted as a grammar-level damage mechanism (P-G07, P-H06).
- Reach is a coordinate: reached instructions lose .22-.40, unreached .04-.05.
- Pairwise site epistasis is additive (-.007, band ±.01, 708 pairs).
- Opcode-word edits are 2.3x more lethal than operand-word edits: loss .47 vs .20 (P-C05, cycle 8).

### 1.5 CW01 cycle 7-8: evolutionary accessibility (`BOUNDARY_REPORT_CYCLE7/8`, `CYCLE_REPORT_CYCLE8` l.341-355)

**Cycle 7: the critical negative result.** In context worlds A/B/C (regime 1 expects 15 - v), no seed crossed the invariant ceiling (A .60, B .59, C .50). This held even in world A, where the regime word is visible. Every top answers IDENTITY. The information is present; there is no fitness path to it.

**Cycle 8 measurements.** Successor worlds A'/B'/C' (regime 1 expects v XOR 1) were NOT crossed in 9/9 runs.

- **Answer-before-read plateau.** On 5/6 plateau genomes the answering OUT fires with all 3 ask-tick words unread (2 on the sixth). No register holds the regime. The plateau is the *initial condition* of the population (held-out .52 from generation 0), not an evolved state.
- **4-edit valley.**
  - The minimal XOR-1 witness is 4 inserted instructions (IN, IN, IN, XOR); 3 on one genome.
  - XOR-15 needs 12.
  - Every prefix of the XOR-1 witness scores 0.0 and all instructions are individually necessary.
  - Exhaustive one-edit census (12,880/genome): 0 hits, 0 beneficial, 88-93% neutral.
  - Grammar samples, 2000 one-op and 2000 two-op: 0 hits, 0 beneficial.
  - Two genomes admit no template witness at all.
- **A single witness fixes in 10/12 runs** (P-J07). One witness among 95 plateau individuals fixes by generation 7-9 (11-13 under tournament 2). It is lost 2/12, at generations 1-3, because its first offspring were all mutated. **Selection is not the obstruction; encoding topology is.**
- **Partial seeded gateway** (P-J03/P-J06, WITNESS-SEEDED, flagged):
  - A seeded XOR-1 routing makes `add 1` (one opcode word from XOR) appear as *standing variation*. It crossed at generation 0 of that stage in 1/2 seeds (.984). No plateau or fresh lineage crossed (.53-.55).
  - Constant-bearing transforms (xor 3/5/15) stay closed. They need a literal 32-bit constant: 2^-32 per uniform draw, or ~16 unrewarded bit flips.
  - Unselected, the machinery decays from .80/1.0 to .52/.48 in 60 generations.
  - Status: PROMOTION CANDIDATE "standing-variation gateway of an acquired routing", not promoted.
- **Independent coordinates.** Representation (grammar B, P-J08: identical neighbourhood, neutral .881/.872) and temporal geometry (P-J09) are independent of this accessibility coordinate.

### 1.6 Other CW01 loop results relevant to heritable organisation (cycles 3-6)

**Temporal-response geometry is a heritable lineage phenotype, rebuilt by the selecting world:**

- Six stable shapes over 412 programs (silhouette .90): immune, ask-time, input-schedule, start-anchored (T-X19), periodic (T-X20).
- Shapes are heritable along neutral walks and survive a grammar change.
- Under selection every shape is rebuilt to the host world's attractor in 20-40 generations (T-X21).
- Under a neutral walk a shape travels or erodes depending on the host's neutral band (P-G05, P-H01).

**Heritable units are entry-point sequences, not transplantable organs:**

- Span transplants transfer competence 0/330 (P-H04) and 0/640 (P-I03).
- In recombination the prefix donor dominates 135/135 one-point splices, and the host dominates 155/157 insertions (P-H02).
- Composition from splicing: 1.6%, with no new shapes.

**Price, sharing and load:**

- The per-unit price sets the sign of the damage effect, with a zero crossing between .0025 and .005 (P-G04).
- Deleterious load is unpurged initial junk that fitness sharing protects (P-G09: elite load 40-83% with sharing vs 0-13% without). It is absent in Proteus (P-G12).

**Weather and carried state:**

- Weather's effect on carried state is dose-dependent (P-F07): light damage raises persistent words (652 vs 270 sham), heavy damage strips them (19).
- In e01's one-parameter organism it selects state *avoidance*; in Proteus it selects more carried state.

**The CW01 constitution** (`loop/LOOP_RULES.md`): nothing scientific is killed; stasis is scoped; perturbations, not reruns; anti-gravity and serendipity slots; a set of forbidden inferences, such as INCONCLUSIVE -> weakened and NULL -> dead.

---

## 2. Methodological lessons that recur in NPE

### 2.1 Eligibility counts before freezing any rule

Memory note: `feedback_preregistered_rules_need_an_eligibility_count.md`. Four instances; the CW01 ones are:

- **e07 D058.** Threshold .90 at f=.20; the reference probe measured .944 and is attainable only at f >= .44.
- **e08 D066.** A minimum of 6 competent lineages per level frozen against a pilot showing 2/4 competent. The run got 4, and the result was INCONCLUSIVE.
- **e08 D064.** A "largest qualifying lambda" rule whose criterion (d) cannot bind at the top, so it picked the top of the sweep.
- **e07 P3 (D034 family).** Non-lethality passes vacuously when damage does not bite. D034 records a gate passing because nothing happened, three times in four experiments.

**Rule.** Report three things with every frozen rule:

- the attainable range of the statistic,
- the attainable range of the conditioner,
- the ELIGIBLE count.

Every rule needs a third branch, INSUFFICIENT_ELIGIBLE_DATA. Ship the reference probe's attainability curve with every threshold.

**NPE relevance.** Any NPE rule of the form "at least k establishment/heredity events" or "heredity rate above x" needs the pilot's attainable event rate on record first. Heredity events in pair-tape worlds are rare; the eligible count is the first-order risk.

### 2.2 Rulers that manufacture coordinates

Sources: memory note `feedback_count_fixing_damage_rulers_manufacture_coordinates.md`; `BOUNDARY_REPORT_CYCLE5`, "Ruler audit".

- Four of seven fixed-count damage claims disappeared under scattered Bernoulli(f) deletion:
  - P-D01 length dose;
  - P-E05 depth coupling (three cells);
  - most of the P-E03/P-F06 selection effect: -.144 to -.071, and 6/6 seeds to 0/6.
- The exact-count scattered ruler round(f·n) reproduced the artefacts (length -.107, tops -.19), because round(f·n)/n is larger for short programs.
- Qualification of the Bernoulli ruler (P-G01):
  - Binomial hit counts over 25,200 draws (chi-square p .49);
  - no positional clustering;
  - length-independent hit fraction (slope 2.8e-5);
  - reproducible masks;
  - clean sham path on 126/126.
- Companion defects:
  - D084: a "fraction-matched" contiguous window is not dilution-neutral.
  - D085: a manipulation that destroys function (persist=none: reward .72 -> .03) is not a coordinate manipulation.
  - D086: relative-loss ruler ill-conditioned.
  - D071: a ratio ruler dividing by a ~5% margin.
  - D088: a distance criterion satisfied by a null host; sham "transfers" 86%.
  - D089: in-sample lookup accuracy over near-unique values is vacuous. This voided cycle 7's "reads the regime into a register".
  - D090: a baseline measured on a different slice from the screened items; 58% of neutral mutants read as beneficial.

**NPE relevance.** NPE's copy detectors, establishment rulers, lineage-length measures and "fraction of tape that is inherited" are rulers of exactly this kind. Anything normalised by genome length, or counting fixed windows on variable-length programs, will manufacture length/age/selection coordinates. Pair-tape organisms vary widely in length.

**Rule.** When a ruler changes the conclusion, that change *is* the result. Record ruler provenance: family, geometry, sampling law, normalisation, denominator, viability floor.

### 2.3 A frozen instrument is not a validated instrument

Memory note: `feedback_frozen_instrument_is_not_validated.md` (Hephaestus's gauntlet, where `bool()` made every vector program a witness). CW01 has the same shape:

- D091: P-C05's material flag read a key the statistic never writes, so it could not fire. Run 1 recorded a .26 paired difference above p95 as not material.
- e07's P3 passed vacuously.
- Archaeon C4-06's shelf control tested nothing, because the walkers started on the shelf (I-4).

**Rule.** Run the positive control (the instrument must say the rare thing where it must) and a cheat control *before* freezing, and smoke-run any committed-unrun runner. Ask of every assertion: what input would make it FAIL?

### 2.4 Similarity is not copying

Memory note: `feedback_similarity_is_not_copying.md`. On 09-19, in the Z80 x Atlas rehearsal (the pair-tape world that became NPE's lineage), a 90% byte-identity test fired SPONTANEOUS_REPLICATOR_FROM_RANDOM_BYTES 5 times in 3 minutes. Inspection showed `copy_bytes` 0, random junk and no copy loop. Once a population converges, any two members resemble each other.

**The fix:** gate on bytes the donor *wrote* outside its own span, snapshotted at ALLOC and differenced at BIRTH, covering at least half the child. Keep `births_similar_no_write` as its own counter.

The same lesson recurs one level deeper in the Nestor S1-S4 ruling C9-D14, "pair-tape identity is not heredity" (memory index). Archaeon's 09-25 engine landscape notes that byte-level taint attribution exposed *host-mediated reproduction*: inert tapes executing resident copier code. There are four identities per birth (executor, executed material, contributors, host), and a copy detector must say which one it measured.

### 2.5 Further recurring lessons from this era

- **Selection is not the obstruction until shown otherwise** (P-J07). Before dosing population size, episodes or generations, test whether a single planted witness fixes. If it does, the problem is encoding distance, and a compute dose is wasted.
- **Statistics that difference out the world draw replicate; raw cross-world magnitudes do not** (e05 MECHANISM_OF_NULL, Finding 3).
  - The within-set across-law DiD held 11/12.
  - Raw superadditivity held 7/12.
  - In NPE, compare heredity between arms on shared tape streams and seeds (Archaeon's paired-arm design), not across independently drawn worlds.
- **Small-sample universals get overturned.** The e05 M3 interaction was "4/4" canonically and 11/12 at replication. Report rates with n.
- **Held-out vs training decoupling.**
  - D065/D069: train8 fitness is a weak proxy for held64 across three organism families.
  - C4/C5: worlds pre-solved by the starting population; 8 of 25 candidates in C5's screen.
  - Screen every world against the starting population before running it: C5's eligibility band [3/16, .70).
- **A control must be a live process.**
  - D082: the drift arm melted to reward 0, so it was not a control.
  - e01: the no-retention control "cannot evolve", so it was a fixed baseline.
  - D076: a sham that consumed shared RNG draws was not draw-matched.
  - Every NPE sham (e.g. a copy-disabled or write-scrambled arm) must be verified draw-matched and viable.
- **Neutral hitchhiking** (e02; T-X01, 26 vs 96 generations). Wholesale elite copying drags neutral genes along and bounds how finely ordering and fixation can be read. NPE lineages under a birth primitive will show the same hitchhiking; gene-order claims need a neutral-marker floor.
- **Close at reconcile when the organism cannot express the phenomenon** (e09). Writing a preregistration for an instrument the substrate cannot supply "would be a ritual".

---

## 3. Mechanistic hypotheses from that era that could transfer to NPE

Stated as hypotheses for NPE, each with its evidentiary strength in the source era.

**H-G1. Answer-before-read / moat plateaus will dominate early NPE populations.** (Strength: measured on 6 genomes; not causal beyond the VM.)

- In CW01 the initial random-program population already sat on an invariant plateau (identity). The conditional program lay 4 coordinated instructions away across a fitness-0 valley, where every partial read destroyed the existing answer.
- The NPE analogue: a self-copier is a coordinated multi-instruction construct (read pointer, write pointer, loop, ALLOC/BIRTH).
- Prediction: a random pair-tape population sits on a non-copying plateau. Partial copy loops score no better than, or worse than, non-copiers; replication appears only via standing variation, a seed, or a world that rewards the first step.
- Test shape to reuse: the P-J02 battery (minimal witness size, prefix fitness of the witness, exhaustive one-edit census, grammar sample).

**H-G2. Selection is sufficient once a copier exists; the bottleneck is reachability.** (Strength: 10/12.)

- By analogy to P-J07, a planted minimal copier among non-copiers should fix quickly. Where endogenous heredity fails to *appear*, the cause is encoding distance, not dynamics.
- Consequence for NPE synthesis: a seeded-copier invasion assay separates "the world cannot sustain heredity" from "the world cannot discover it". Those are different findings, and the CW01 promotion rule required the unseeded crossing.

**H-G3. Standing-variation gateways around acquired machinery.** (Strength: promotion candidate, 1/2 seeds, witness-seeded.)

- A seeded routing made a constant-free one-opcode neighbour (XOR -> ADD) present before selection asked for it. Constant-bearing neighbours needed ~16 unrewarded bit flips and stayed closed.
- In NPE: once a copy loop exists, its one-edit neighbourhood may already contain variants such as a different length, a partial copy or a copy-with-modification. Those would be the gateway to richer reproductive organisation.
- Neighbours that need a specific literal (an exact length constant, an exact offset) will be much less accessible than register-to-register rewrites.
- **Literal-constant reachability** is a candidate accessibility coordinate for Z80-like ISAs, where immediate operands are bytes. On an 8-bit immediate the gap is 2^-8 rather than 2^-32, so NPE may be *more* permissive here than Proteus. Measure it rather than assume.

**H-G4. Unselected machinery decays at the mutation rate.** (Strength: one ladder, post hoc addendum.)

- The XOR-1 routing vanished in 60 unselected generations.
- NPE analogue: copy machinery that is not currently paying (e.g. a world phase where births are not rewarded, or a host-mediated regime) should erode. Heredity persistence across world switches is a direct test of whether reproduction is self-maintaining.

**H-G5. Locality of damage.** (Strength: measured under count rulers; operand softness ruler-invariant.)

- Scattered damage costs more than contiguous damage of the same size. Operands are softer than opcodes (2.3x). The register-field operand is the fragile slot. Damage lives in reached code.
- For NPE copy fidelity: a copier's errors are intrinsically *local*, since they are write errors during the copy loop. Hypothesis: point-like copy errors in operand bytes are the most tolerable heritable variation, and errors in loop-control and addressing bytes the most lethal.
- Also: P(broken jump | length change) = .423 in Proteus. Relative addressing in Z80-like jumps makes insertions and deletions dangerous, which bears on copy-with-indel.
- **Must be re-qualified on a Bernoulli ruler** before any NPE claim.

**H-G6. Length accumulation is an acceptance-filter artefact that trades against exaptation.** (Strength: controllable with two independent levers.)

- If NPE acceptance or selection admits neutral length (junk appended by imprecise copying, or tape padding), expect three things: genomes grow, apparent robustness rises (by dilution, see section 2.2) and novelty falls.
- The no-growth rule and a length price both reversed growth and raised exaptation. A price of 1/128 per unit collapsed length from 44 to 5-6 at unchanged reward (P-F10), so "the length was junk".
- In a pair-tape world, copy-length drift is a heritable variable. This mechanism predicts it inflates unless costed.

**H-G7. World attractors rebuild heritable phenotypes quickly; neutral transplant erodes them by the host band.** (Strength: promoted mechanism candidate T-X21.)

- For NPE: reproductive phenotypes (copy strategy, host dependence) are more likely set by the world than carried by ancestry. Transplant tests (neutral vs selected) tell ancestry-borne from world-borne organisation.

**H-G8. Recombination and splicing: prefix/entry dominance, no composition.** (Strength: 792 children.)

- Byte splices across programs are dominated by the entry-point donor, and composition is ~1.6%. Pair-tape interactions that splice or overwrite neighbours will mostly transmit the donor's *entry sequence*.
- This is a warning for heredity attribution: "who wrote the entry point" may be a more meaningful parent than "who contributed most bytes".

**H-G9. A local failure boundary buys single-edit recovery, not discovery.** (Strength: C5, subject to the C5-03 amendment.)

- FIZZLE-style skip semantics gave 229 recoveries vs 154 losses at the single-edit level and no discovery gain at equal compute.
- If NPE uses a total interpreter, fault semantics are unlikely to be the lever for heredity emergence. If it uses trap semantics, expect hidden executed-fault load in 46-80% of the population, carried for no gain.

---

## 4. Rulers and primitives worth reusing

| item | where | why reuse in NPE |
|---|---|---|
| Qualified scattered Bernoulli(f) damage ruler plus its five qualification checks (Binomial counts, clustering, length-independence, mask reproducibility, sham path) | CW01 P-G01; memory `feedback_count_fixing_...` | Any mutation/damage robustness claim about copiers or lineages |
| Ruler-family dose as a standing positive control (count-fixing vs fraction-fixing on the same programs; the false coordinate should appear and vanish) | P-G08; specimen SPEC-R01-FALSE-COORDINATE in `loop/SPECIMENS_CYCLE3_4.json` | Calibrate any NPE length-normalised statistic |
| P-J02 accessibility battery: minimal witness, witness-prefix fitness, exhaustive structured one-edit census, sampled one-/two-op grammar, route classification | CW01 cycle 8; specimen file `loop/SPECIMENS_CYCLE8.json` | Measure the mutational distance from the NPE plateau to the nearest copier |
| Single-witness invasion assay (plant 1 in N; count fixation and loss generations; tournament dose) | P-J07 | Separate reachability from maintenance of heredity |
| Scaffold ladder with a removal stage (seed, advance, remove, test decay; census before each stage) | P-J03/P-J06 | Gateway and decay tests, clearly flagged WITNESS-SEEDED |
| Genealogy store (every generation: pid/op/fitness, gzip) plus coalescence time | P-J05 | Lineage coalescence baseline; NPE needs the birth-level equivalent |
| Reach (HALT probe) and reached-only damage | P-G07, P-H06 | Condition copy-fidelity and damage claims on executed bytes |
| Opcode-vs-operand word edits; operand slot map | P-C05, P-E04, P-G07 | Locality coordinate for the Z80 ISA |
| Answered-before-read probe ("unread words at the answering OUT") | P-J02 | Generalises to "did the copier read its source before writing?", a causal copy check |
| Bit-identical sham, draw-matched, fail-closed sham==select check | e07, D076, D083 | Every NPE control arm |
| Pre-QUALIFY admissibility gate with known-broken fixtures that must be refused (5/5 refused, twice) | e07 | Cheap world screen before a long run |
| World screen against the starting population (eligible iff best held-out in [3/16, .70)) | C5 `WORLD_SCREEN_2026-09-18.json` | Avoid pre-solved or dead worlds |
| Within-draw DiD statistics; paired arms on shared tape streams | e05; Archaeon ENVGATE (engine landscape) | Heredity contrasts that replicate |
| Donor-wrote-bytes copy gate plus `births_similar_no_write` counter | Z80 x Atlas rehearsal (memory) | The heredity detector itself |
| Four-identity birth attribution (executor / material / contributors / host), byte-level taint | Archaeon `archaeon/z80atlas`, `lineage` (engine landscape) | Distinguishes self-replication from host-mediated reproduction |
| Loop machinery: TRAJECTORIES/EVIDENCE/STATE/PERTURBATIONS jsonl, `prioritize.py` (`requires` rule so a reread cannot run before its ruler qualifies), `close_cycle.py` derived defect tally | `loop/` | Portfolio discipline across NPE trajectories |

---

## 5. Anomalies worth preserving

1. **The plateau is the initial condition** (P-J05). Random populations started on the identity invariant at held-out .52 at generation 0, and 120 generations were pure neutral drift. Worth checking whether NPE's non-copying state is likewise present at time 0 rather than evolved.
2. **Standing-variation crossing at generation 0 of a new stage** (P-J06): an add-1-competent individual already existed before selection asked. It crossed in 1 of 2 seeds, and seed 2 stuck at .70 on the XOR-1 relic. Unreplicated.
3. **Witness loss by first-offspring mutation** (P-J07, 2/12). "Every birth is a mutation" means a lone innovator can be lost before one faithful copy exists. This is an error-threshold-like effect *inside an exogenous-heredity GA*. For NPE, where copy fidelity is endogenous, this is the obvious bridge.
4. **e05 r11:** 0/3 components individually load-bearing, yet targeted ablation costs 57.94 vs a random-removal sham of 36.53. Collective necessity without individual necessity; recorded, not probed.
5. **Delayed exclusion** (P-E06): coexistence at generation 80 (17/54) resolving by 160 (10/54). Also the non-monotone recombination-rate window (.6-.7) where rare TREE goes extinct. Time-dependent verdicts in ecological reads.
6. **Deleterious load protected by sharing** (P-G09): the elite's raw score rises under deletion in 40-83% of cases with sharing, 0-13% without; absent in Proteus. Any NPE niche/sharing mechanic may preserve junk that looks like genome content.
7. **Price sets the sign of damage** (P-F04, P-G04), with a zero crossing at a per-unit price of ~.004. Under a length price in Proteus, damage becomes a growing cost (P-F10). NPE ALLOC/energy costs may similarly set the sign of copy-error effects.
8. **Weather dose reverses the state response** (P-F07): p .25 raises persistent words (652 vs 270), p .75 strips them (19).
9. **Temporal shapes carried with function, not as organs**: 0/330 and 0/640 transplants; start-anchored and periodic shapes change answers without changing correctness (P-G11). A heritable, selectable phenotype with no fitness consequence on the census worlds.
10. **Silent W0 drift switched on by an input-less tick** (P-C14, P-D02, P-E01): one empty tick displaces answers .40-.75 in 94-100% of programs; persist=none removes it but also destroys function. Carried state and function could not be separated (T-X15 stasis).
11. **Total interpreter: 932/932 opcodes out of table** (C4). The foundry's uniform 32-bit generator meant no program ever used "defined" encodings. Q1 of the C4 packet asks whether this is a generator or an ISA property; that is directly relevant if NPE's tape inflow is uniform random bytes.
12. **C5 recovered children sit at displacement .015**: "parent plus a hole" (C5 reviewer Q2). A recovery class that may be relabelled neutrality; keep as a caution for NPE "repair" claims.
13. **Z80 triplication** (engine landscape): three independent Z80 byte-organism worlds (NPE, BEE, Archaeon) from one 09-19 directive, with no shared code. A cross-implementation differential is available if one heredity assay is run on all three.

---

## 6. How to use this in the NPE synthesis (short)

- Treat any NPE "heredity absent" result as possibly **H-G1/H-G2-shaped** (reachability, not dynamics) until a planted-copier invasion is run.
- Treat any NPE "heredity present" result as suspect until it passes the **donor-wrote-bytes gate** and the **four-identity attribution**, plus a reverse check: what would make the detector fire with no copying?
- Treat any NPE robustness or length effect as a **ruler candidate** until re-read on a qualified fraction-fixing ruler.
- Treat every frozen NPE rule as requiring an **eligibility count** and a third branch.
- The CW01 loop never observed endogenous heredity. Its evolvability findings are conditional on exogenous heredity and must not be imported as statements about emergent replication.

---

## 10-line summary

1. CW01 (e01-e09 plus loop cycles 1-8) and Archaeon C4/C5 all used *exogenous* heredity. No organism built its child ("every birth is a mutation; copy never occurs").
2. Designs went unreachable for two reasons: search never reached the needed region (e07 D059), or the organism had no primitive for the phenomenon (e09). Both were caught by cheap probes before evolution.
3. Cycle 8 located the obstruction as topological: an answer-before-read identity plateau present at generation 0, and a 4-instruction fitness-0 valley to the conditional, with 0 hits in 12,880 one-edit mutants per genome.
4. Selection was not the obstruction: a single planted witness fixed in 10/12 runs within ~8 generations. Planted-copier invasion is the analogous NPE test.
5. A seeded routing yielded a partial standing-variation gateway: add-1 crossed at generation 0 in 1/2 seeds, literal-constant neighbours stayed closed, and the machinery decayed in 60 unselected generations. Unpromoted.
6. Archaeon C4/C5: the total interpreter meant damage was a cliff with 0 beneficial edits, and neutral networks grew slowly. A real fault boundary gave single-edit recovery (229 vs 154) but no discovery gain at equal compute.
7. Locality law: scattered damage costs more than contiguous, operands are softer than opcodes (2.3x), and damage lives in reached code. Trap-NOP walks grow length through the acceptance filter, and that growth suppresses exaptation.
8. Four of seven damage claims were manufactured by count-fixing rulers. Use qualified Bernoulli(f) rulers, and treat a ruler change that changes the conclusion as the result.
9. Recurring discipline: eligibility counts and a third branch for every rule, positive/cheat controls before freezing, draw-matched live shams, and within-draw statistics.
10. For heredity specifically: similarity is not copying. Gate on donor-written bytes, attribute executor/material/contributors/host, and keep `births_similar_no_write`.

Path: `F:/Prometheus-worktrees/nestor-d2v13/roles/Nestor/inference_harvest_2026-09-30/dossiers/G_cw01_archaeon_prior_lessons.md`
