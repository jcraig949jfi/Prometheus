# NS-01 ANALYSIS -- can a failure archive redirect mechanism generation? (Cosmos, 2026-10-11; pilot, n = 8 per arm)

All work exploratory, visible-world. No holdout, no confirmation data, no killed law revived. Every job ran under
prometheus.cosmos.supervise (8 jobs, 0 restarts). Artefacts in this directory; commits on cosmos/ns01-2026-10-11.

## CORRECTION (2026-10-11, after NS-02 stage 1; see NS-02_2026-10-11/NS01_RETRO_DESAT.json)
The headline "16 of 24 LLM proposals are behaviourally perfect memories, indistinguishable from the witnesses" is an
INSTRUMENT ARTEFACT of the NS-01 signature (defect 2 below). Re-measured with the qualified de-saturated signature
(corruption dose-response + dual cue), only 1/8 proposals per LLM arm is equivalent to a witness and the LLM arms form
6-7 distinct clusters each (D: 6). The arm comparison below is superseded on that point; F15 and the audit stand.

## 0. Answer in one paragraph (as written before the correction)
Not demonstrated. In this pilot the failure archive did not measurably redirect LLM generation toward distinct causal
structures: 16 of 24 LLM proposals (all three LLM arms) are behaviourally perfect memories, indistinguishable from the
archived register / delay-line witnesses, whatever their stated mechanism. The one failure-15 candidate came from the
negative-prompt arm (B), whose author designed it explicitly to probe a listed measurement failure (E12): the archive
redirected generation toward the INSTRUMENT's blind spots, not toward new mechanisms. The external-exclusion arm (C)
did not outperform B; its signal mostly said "equivalent to a known mechanism" and, because the engine cannot tell
perfect memories apart, it effectively rewarded imperfection. The grammar (D) explored failure space far more widely
(6 signature clusters vs 3-4) but produced no candidate. With n = 8 per arm, every comparison is a count, not a test.
FAILURE_15.md: SUPPORTED relative to the archive after surviving a preregistered merge test (required decoder capacity
grows super-linearly with relational dimension, slope 1.6) -- a known learning-theory phenomenon newly placed in the
archive as a false-negative region of its information-presence instruments.

## 1. The audit (FAILURE_ATLAS.json, frozen eb0e1c14f)
The 14 operator candidates are failures of INFERENCE PROCEDURE, not of mechanisms; the archive (incl. Atlas F1-F12,
Tityos T01-T18) has no mechanism taxonomy. Tier P (13; judge constraints): E01+E02+E07+E09 merged (circularity),
E03+E04 merged (family identity), E12 narrowed WEAK, E13/E14 predictor-level, + 3 replacements (start state,
unqualified instrument, liveness != progress). Tier M (7 mechanism classes with executable rules/witnesses) were the
candidate exclusions. 14 was not reached by inventing distinctions.

## 2. Engine qualification (ENGINE_QUALIFICATION.md)
QUALIFIED: false rejection 1/66 disguised witnesses, false acceptance 0/7 look-alike pairs. Defect found: the
behavioural signature collapses saturated memories (delayline = register = static-sensor stig) and absent memories.

## 3. Results by arm (arm_summary.json; raw: CANDIDATES.jsonl, EXCLUSION_RESULTS.jsonl, EXPERIMENT_RESULTS.jsonl)
| | A unconstrained | B negative prompt | C external exclusion | D grammar |
|---|---|---|---|---|
| KNOWN_EQUIVALENCE | 5 | 5 | 6 | 0 |
| KNOWN_FAILURE / DEGENERATE | 0 / 0 | 0 / 0 | 0 / 0 | 3 / 3 |
| VIABLE_KNOWN_STRUCTURE | 1 (linear-blind) | 0 | 0 | 1 |
| VIABLE_DISTINCT (first pass) | 2 | 3 | 2 | 1 |
| reproducibly distinct (fresh seed + 4 disguises) | 1 (A07) | 3 (B01, B05, B08) | 2 (C06, C07) | 1 (D04) |
| failure-15 candidates | 0 | 1 (B08) | 0 | 0 |
| tier-M rule hits | 1 | 0 | 0 | 14 |
| signature clusters at TAU | 3 | 4 | 4 | 6 |
| mean pairwise signature distance | .119 | .089 | .094 | .370 |
| median distance to nearest witness | .0003 | .007 | .025 | .055 |
| generation wall / tokens | 963 s / 237k | 1154 s / 265k | 1120 s / 239k | ~0 s / 0 |
| evaluation CPU | 44 s | 35 s | 36 s | 19 s |
Primary outcome (reproducibly distinct mechanisms or failure classes per effort): B 3 + 1 candidate; C 2; A 1; D 1 at
negligible generation cost. Of the 7 "reproducibly distinct", B05 resolved as a decoder-class artefact and B01 as
representation dependence (F15 test), so they are distinct BEHAVIOURS of known classes; the others (A07, C06, C07,
D04) are near-perfect memories with mild decay or a flat plateau below 1 -- distinct, not failures.

## 4. Pre-registered whole-protocol failure hypotheses (GENERATION_PROTOCOL s10) -- what the data say
- B anchors on the archive: NOT observed as feared (0 tier-M hits; median witness distance .007 vs A .0003); but B has
  the LOWEST diversity (.089) and its novelty went into probing measurements (B08 cites E12).
- C collapses on repeats: partly -- 6/8 rejected as equivalent; the signal cannot say WHY, and it pushes away from
  working mechanisms (see 5).
- D's grammar bias: D is the most diverse and the only arm visiting failure classes; 3/8 degenerate (cost of random
  composition); no candidate.
- Engine confuses implementation with physics: NOT observed for disguises (FR 1/66); but the converse defect is real:
  different physics with the same saturated behaviour is invisible (16 different LLM organisations -> 2 witnesses).
- Novelty pressure -> nonsense: not observed (0 NONEXECUTABLE in all 32; LLM code was clean and compliant).
- Contract forces one architecture: YES in behaviour. The task rewards holding one symbol; LLMs reliably build things
  that hold it. Under a success-saturated behavioural signature, mechanisms differ only in how they fail, and LLM
  generators do not fail.
- Classes too coarse: C's signals were one undifferentiated class ("equivalent") 6/8 times.
- Signature lacks power for new causal behaviour: YES for saturated memories; partly answered by the F15 test, where
  INTERVENTIONS (gauge / desync) and DECODER-CLASS contrasts separated organisations that the signature did not.

## 5. Methodological defects (own)
1. The exclusion signal rejects working memories (equivalence to "register") -> exclusion-driven search rewards
   imperfection, not causal novelty. A fair C arm must exclude on CAUSAL organisation, which needs (2).
2. The behavioural signature has no stress / intervention axes that de-saturate perfect memories (dose-response to state
   corruption and noise, symmetry interventions, capacity probes).
3. Arms are conversations of one model; "separate contexts" is not independence of priors (A, B, C all chose
   attractors, populations, conserved quantities, hysteresis).
4. One generation run per arm; no replication of the arm comparison; n = 8.
5. The F15 post-hoc capacity check was run after the preregistered test (descriptive; it lowered the claim).

## 6. What NS-01 does and does not establish
Establishes: an executable, qualified exclusion engine for tier-M classes; that LLM generation under this contract
concentrates on successful memories regardless of negative-space information; one reproducible, intervention-backed
failure class (F15, survived its merge test) in the archive's own measurement family. Does NOT establish that any arm is
better than another (n = 8), nor that F15 is new to science (it is not).
