# CW01 priority loop - boundary report, cycle 8 (CYCLE8_2026-09-19)

Direction (operator): EVOLUTIONARY ACCESSIBILITY as the primary object. P-J01 first, unchanged; mutational distance MEASURED in the VM; scaffold stripping; forensics; first-crossing genealogy; gateway structure. Computational scope only (integer programs on a bounded VM; tensor-train policies for the e08 fossils).

## 1. Reconcile and freeze

Pool 39 nodes. Batch J (P-J02..P-J09) appended, P-J01 amended (genealogy storage, separate readings). Frozen ten: P-J02, P-J01, P-J08, P-J09, P-J07, P-J03, P-J06, P-A02, P-C05, P-D08. P-J04 (forensics) and P-J05 (genealogy) fell outside the ten by the per-parent cap (T-X21 held P-J01 and P-J07); the directive mandates them as P-J01's companions, so both ran and are marked executed as companions. Order run: P-J01 (foreground first), P-J05, P-J02, P-J08, P-J07, P-J04, P-J09, P-J03, P-J06, fillers.

Substrate changes before the run (all in cw01-arch4, backwards compatible): ctxworlds gains `xor` and string `transform` ("xor:C" / "add:C"); the evolver records each kid's parent index and operator and accepts a tournament size; ctxevo returns the full final population.

## 2. Results

| id | what | result |
|---|---|---|
| P-J01 | successor worlds A'/B'/C' (regime 1 expects v XOR 1), 3 seeds, controls, genealogy stored | NOT_CROSSED x3: A' .48-.52 (thr .90), B' .44-.52 (.80), C' .50 (.80, cue-follow floor); no crossing generation in 9/9; destroyed controls indistinguishable |
| P-J05 | genealogy of the 9 runs | route NOT_APPLICABLE; the lineage's held-out is .52 from generation 0 (the identity plateau is the INITIAL condition); coalescence by generation 0-62 in 6/9; every birth is a mutation |
| P-J02 | actual mutational distance, 6 plateau genomes | probes: the answering OUT fires with 3/3 ask-tick words UNREAD (2 on one genome), no register holds the regime at that moment; witnesses: XOR-1 = 4 instructions (IN, IN, IN, XOR; 3 on one), XOR-15 = 12; 2 genomes admit none; every prefix of the witness scores 0.0 (valley), all instructions individually necessary; exhaustive one-edit census 12880/genome: 0 hits, 0 beneficial; grammar 2000 one-op + 2000 two-op: 0 hits, 0 beneficial, neutral .88 / .77; route NO_ONE_OR_TWO_EDIT_HIT on xor 1 and xor 15 |
| P-J07 | invasion of ONE witness into the plateau population (A') | FIXED 10/12 (generation 7-9 at 16 asks; 7-8 at 64 asks; 11-13 under tournament 2), LOST 2/12 at generation 1-3 (first offspring miss); crossed populations hold 1.0 |
| P-J04 | forensics after crossing | NOT_APPLICABLE x3; A' instruments validated on witnesses (cue causality 1.0; XOR knockout -> 0-.13; register overrides act only at the tick boundary) |
| P-J08 | grammar B vs v0.4 neighbourhood of the plateau | identical: hit 0/0, beneficial 0/0, neutral .881/.872 |
| P-J09 | geometry of the witnesses | immune -> immune (4/4); context computation does not move the temporal geometry |
| P-J03 | scaffold ladder (WITNESS-SEEDED, flagged) xor1 -> xor3 -> xor15 -> removal -> xor5 | xor1 crossed (seeded); xor3 NOT (.69/.56, the XOR-1 relic); xor15 NOT (.58/.56; plateau .50/.56; fresh .42/.50); removal: the xor-1 machinery decays from .80/1.0 to .52/.48 in 60 unselected generations (addendum, post hoc); xor5 nobody |
| P-J06 | gateway: novel transforms add 1 and xor 5 from S2 / P2 / fresh | add 1 CROSSED by the scaffolded lineage seed 1 (.984, at generation 0 = standing variation), not by seed 2 (.70), not by P2 or fresh (.53-.55); xor 5 nobody; reuse: crossed tops read all 3 words before the OUT and hold r in register 0 (the witness's routing) |
| P-D08 / P-A02 | e08 fossil ablations (256) | rank profile re-drawn with cores re-drawn: 155-171 -> 72-91 (below floor 166.5) in every arm; mask scramble at equal bits: -> 118-128; not material (the (i) arm confounds cores with profile, as preregistered) |
| P-C05 | opcode-word vs operand-word single edits, 47 parents | loss .47 vs .20 (paired .26 outside the sign-flip band), displacement .42 vs .16, held -.21 vs -.09; every stratum ordered; MATERIAL |

## 3. What cycle 8 established

1. THE OBSTRUCTION IS TOPOLOGICAL, NOT METRIC. The plateau organism answers from persisted state BEFORE reading the ask tick (unread 3 of 3 at the answering OUT). No edit of the answer's computation can make it conditional until a read is added, and every partial read destroys the identity answer (prefix fitness 0.0). The nearest conditional program is 4 edits away across a valley of fitness 0; the one-bit successor world did not shorten it (the transform size was never the distance).
2. SELECTION IS NOT THE OBSTRUCTION. A single witness fixes in 10/12 runs within ~8 generations under the very regime that fails 9/9 times from the plateau. No population or episode dose is warranted (the directive's rule).
3. CYCLE 7's MECHANISM READING IS CORRECTED (D089). "Reads the regime word into a register, causally inert" rested on an in-sample lookup that is vacuous over near-unique values; the register held tags. The causal conclusion (0 percent transplant effect) stands; the reason is that the word is read AFTER the answer within the tick.
4. ACQUIRED MACHINERY CHANGES WHAT IS REACHABLE - PARTIALLY, AND WITH A FLAG. A seeded XOR-1 routing makes the constant-free neighbour (add 1: one opcode word from XOR) appear as standing variation that crosses a never-seen transform with zero generations of selection, while the plateau and fresh lineages stay trapped. Constant-bearing neighbours (xor 3 / 5 / 15) need a literal 32-bit word (2^-32 per draw or ~16 unrewarded bit flips) and are not opened. The machinery decays at the mutation rate when unselected (gone in 60 generations).
5. Representation (grammar B) and temporal geometry are independent of this accessibility coordinate.
6. The word kind is a locality coordinate: opcode-word edits are 2.3x more lethal than operand-word edits (P-C05), consistent with cycle 7's operand-slot ordering.

## 4. Promotion standard applied

- Context-sensitive / history-dependent / temporal-evidence mechanism: NOT PROMOTED (no evolved crossing in any world).
- Measured fitness-valley / accessibility mechanism: PROMOTED as a MEASUREMENT - "answer-before-read plateau with a 4-edit valley of fitness 0; one-edit and two-edit neighbourhoods contain no beneficial mutant; a single witness fixes" (P-J02 + P-J07, six genomes, three grammars of evidence: structured census, sampled grammar, hand witnesses with intermediates). Independent failure mode: the census (exhaustive) and the invasion (dynamics) fail in opposite directions and agree.
- Evolutionary gateway: NOT PROMOTED; PROMOTION CANDIDATE "standing-variation gateway of an acquired routing" (P-J06 1/2 seeds, seeded scaffold, crossing pre-existing at stage entry). Required next: a replicated seeded ladder (>= 4 seeds) or a natural crossing.
- Alien mechanism: none.

## 5. COORDINATE STATUS

| coordinate | status | evidence |
|---|---|---|
| answer-before-read (unread words at the answering OUT) | NEW, measured on 6 genomes | P-J02 probe |
| edit distance to the conditional (witness size; census hits) | NEW, measured | P-J02 |
| valley depth (prefix fitness) | NEW, measured | P-J02 intermediates |
| beneficial-mutant fixation time | NEW, measured | P-J07 |
| literal-constant reachability | NEW, inferred from the grammar + ladder | P-J03 / P-J06 |
| representation (grammar) | NOT a coordinate here | P-J08 |
| temporal geometry | INDEPENDENT of context computation | P-J09 |
| word kind (opcode vs operand) | locality coordinate, confirmed | P-C05 |
| e08 rank profile | confounded ablation, unresolved | P-D08 / P-A02 |

## 6. Continuation (next cycle candidates, not frozen)

- A successor world that FORCES the read: the answer in BOTH regimes must depend on an ask-tick word (e.g. the ask carries a key the answer must include), so the first step off the plateau is rewarded and the conditional becomes one edit.
- A grammar in which literal constants are reachable by steps (e.g. an operator that writes a small constant), posed to the scaffolded lineage for xor 3 / 5 / 15.
- The seeded ladder replicated with >= 4 seeds and the standing-variation reading tested directly (census the scaffolded population before each stage).
- P-I05 remains bounded / waiting.

## 7. Stasis, nodes, defects, interface, teardown

- States: T-X21 ACTIVE (obstruction located); T-R01 ACTIVE (distance measured); T-X17 ACTIVE (partial gateway); T-ARCH5 TEMPORAL_STASIS scoped (representation as an accessibility coordinate of the identity plateau); T-X05 TEMPORAL_STASIS scoped (fossil ablations that re-draw the cores); 8 nodes in stasis of 39.
- Defects: D089 (P-I02 in-sample lookup vacuous), D090 (census baseline on a different slice - fixed pre-read, reruns), D091 (P-C05 material flag could not fire - fixed, rerun). Ledger 92 entries; tally derived (close_cycle: PASS).
- Interface: loop/SPECIMENS_CYCLE8.json (4 public specimens: answer-before-read, XOR-1 witness, witness invasion, scaffold ladder). No Campaign 6 machinery touched.
- Teardown: all drivers exited (RC 0); no background python of this cycle remains; gw-venv untouched; production seats read-only; no git stash; commit gated on the writer lock.
