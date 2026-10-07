# C-010 NATIVE-RET-WITNESS-001 -- PREREGISTRATION v1.0.0 (FROZEN)

Frozen by Palamedes[harry1-679179c6] at 2026-10-07T08:33:34Z, as the first act of C-010, after C-009 closed scoped to flat
inventories (rso/binding/CLOSURE.md) and BEFORE either subject GA run, any witness episode, or any statistic on any
arm or control. Derived from rso/witness/PREREG_DRAFT.md (C-009-T015, with T016/T017/T018 folded in); the draft is
kept unchanged beside it. Changes against the draft, made before freezing: s5 adds P-FLAT; s7 fixes the artifact
interface; s3 is a registered procedure (values computed after the subject runs, mechanically); s10 freeze rules.
Its sha256 is recorded in ops/campaigns/C-010/CAMPAIGN.json.

## 0. Exposure (recorded before any witness data)

The designers have read ares/ARES_CYCLE2_REPORT.md and seen the fossil name ares/fossils/W4_activation_memory_s3:
prior Ares work found W15-evolved lineages at the fitness cap (10/10) with plasticity often load-bearing, and
W4-evolved memory in activations. A W4-evolved subject is therefore expected by the designers to tend to NEGATIVE
across W15 interrupts and a W15-evolved subject to tend to POSITIVE. To keep the design from being chosen for its
expected outcome, BOTH are registered (decision 3 of SELECTION.md is reversed here, before preregistration), each
reported separately, never pooled. Those prior runs are background, not witness evidence; none of their genomes
or seeds is used.

## 1. Question and claim (relative; closure C2)

Q: Does a frozen Ares organism retain the regime bit r of world W15 across the world's activation-reset events and
use it -- and, if so, through its declared allowed channel (plastic W1)?
Claim form (rendered only with subject digest, world variant, seed set, n, bound, delta, alpha): "In W15, subject
S answers r after the last interrupt above the registered no-carry bound (P-RET POSITIVE), mediated by plastic W1
(P-CHAN PASS)." No class, mechanism-in-general, recursion or cross-physics wording.

## 2. Subjects (frozen before any witness episode)

  S4   primary.   ares.search.run("W4", "present", Config(), P=128, G=120, eps=4, seed=20261007) -> champion genome.
  S15  secondary. ares.search.run("W15", "present", Config(), P=128, G=120, eps=4, seed=20261008) -> champion.
Config() = substrate defaults (n_hidden 8, ticks 2, topology/keep/plasticity allowed). Selection is the GA's own
(its seeds, EVAL_SEEDS); no choice among subjects after any witness outcome. Each champion's genome bytes are
hashed and committed, with the run receipt, BEFORE any witness episode. A subject run that fails (exception) is
re-run once with the same seed; never with another seed.

## 3. Witness seeds

2048 episodes per arm, balanced (1024 r = 0, 1024 r = 1, RULER.md s2), drawn by the registered generator from
seeds >= 900000, excluding EVAL_SEEDS, balanced_seeds_for(...) ranges and every episode seed the two subject GA
runs drew (recorded by the driver); the excluded set and the final list are committed before the witness runs.

## 4. Arms (adapter wrappers, rso/witness/ares_client.py; no ares/ source edit)

  for each subject X in {S4, S15}:
    X        correct resets                                     P-RET (main), P-OBS, P-PRES
    X-NOPL   plasticity disabled                                P-CHAN
    X-LEAK   delayed-leak reset (v := 0, live W1 not restored)  P-ERASE broken member
  shared:
    POS      hand-wired PLAST carrier                           P-CAL (must be POSITIVE)
    RECUR    hand-wired activation self-loop                    channel control (reported, not gating)
    NULL     reset_each_step / random population                P-CAL (no carry)
    SHUF     W15 "shuffled" (cue decoupled from r), subject S4  P-CAL (no carry)

## 5. Predicates and gates

  P-CAL   GATE (RULER.md): NULL and SHUF each correct <= k_neg = 1073 of 2048, AND POS P-RET POSITIVE. FAIL makes
          every P-RET outcome of the campaign UNQUALIFIED.
  P-OBS   GATE: rollout record=True vs record=False give identical actions on every witness seed, per subject.
  P-ERASE GATE pair on B2, paired carry-over (ERASE_PROBES.md s1, C-009-T018): 64 triples (pre_a r=0, pre_b r=1,
          probe) from seed 800000 upward; per arm, fresh runtimes run [pre_a, probe] and [pre_b, probe]; D = total
          differing probe actions (exact). X: PASS iff D = 0. X-LEAK is the fire member: P-ERASE for X is QUALIFIED
          only if X-LEAK has D > 0; otherwise DETECTION_UNQUALIFIED for X.
  P-PRES  GATE (ERASE_PROBES.md s2): 32 (warmup, seed) pairs from seed 850000 upward; [warmup, seed] with the
          correct reset vs [seed] on a fresh instance; PASS iff 0 differing actions.
  P-RET   RULER (RULER.md s3-s4): n 2048, bound 1/2, delta 1/20, alpha 1/100, k_pos 1078, k_neg 1073;
          NOT_SHOWN / POSITIVE / NEGATIVE / INDETERMINATE by that precedence. Decided once per subject.
  P-CHAN  GATE, only if X is P-RET POSITIVE (RULER.md s5.2, C-009-T017): X-NOPL on the SAME 2048 seeds, paired;
          PASS iff X-NOPL is P-RET NEGATIVE AND b >= mcnemar_threshold(b + c) (exact one-sided McNemar, alpha 1/100;
          b = X correct & X-NOPL not, c = the reverse). FAIL reasons NOPL_NOT_NEGATIVE | NO_PAIRED_ADVANTAGE.

  P-FLAT  GATE (C-009 CLOSURE.md, scope of the binding): a witness bundle is evaluated only if every RECEIPT row's
          parent_run_id is the anchored launch, every COMPLETED RECEIPT row carries receipt_sha256, and no node id
          has two RECEIPT rows. FAIL refuses the bundle: every claim from it is UNQUALIFIED (not a negative result).
  Custody GATE (CONTRACT s6): a claim is QUALIFIED only with its bundle's custody QUALIFIED (manifest and
          inventory registered with the keeper before the first check).

## 6. Outcome classes per subject (registered)

  POSITIVE               P-CAL, P-OBS, P-PRES PASS; P-ERASE pair separates; P-RET POSITIVE; P-CHAN PASS
  POSITIVE (channel unidentified)   as above but P-CHAN FAIL: "retention by an unidentified channel"
  NEGATIVE               instrument qualified (P-CAL, P-OBS, P-PRES PASS, P-ERASE separates) and P-RET NEGATIVE
  DETECTION_UNQUALIFIED  P-CAL / P-OBS / P-PRES FAIL, or P-ERASE does not separate, or P-RET INDETERMINATE or
                         NOT_SHOWN (NOT_SHOWN is reported as such inside this class)
The campaign result is the pair (S4 class, S15 class); S4 is primary. No pooling, no re-run to change a class.

## 7. Evidence, custody and the artifact interface (rso.binding; CONTRACT.md s6)

Artifact interface (fixed now so producer, driver and evaluator are built in parallel): every byte string the
evaluator reads is stored in the bundle as artifacts/<sha256> and listed in its receipt (outputs / oracle, with role
and length). Roles: trace:actions (episode x step x organism action array), oracle:regimes, oracle:reset_steps for
P-RET / P-CAL / P-CHAN / RECUR nodes; trace:actions_record and trace:actions_norecord for P-OBS; for P-ERASE
trace:probe_after_a and trace:probe_after_b per the probe list; for P-PRES trace:pres_warm and trace:pres_fresh.
Array layouts (dtype, shape) are recorded in the receipt. The evaluator recomputes every count and every outcome from
these bytes and the ruler; nothing it uses comes from a field the producer computed.


Every predicate node is a canonical receipt with a node execution row (parent_run_id, receipt_sha256) under its
top-level launch; each bundle's manifest names its launch; manifests and inventories are registered with the
keeper (Aporia) before the first check. A witness claim is QUALIFIED only with its bundle's custody QUALIFIED.

## 8. Independent challenge and stop rules

One Pallas Q3 challenge on the frozen witness path (>= 1 sound, 2 broken, 2 edits; e.g. a counterfeit P-RET input,
a leak that passes P-ERASE), committed before outcomes; one repair round; then the result is final within the
72-hour window. Stop at the first exhausted cap; keep partial results; at 2026-10-10T00:25Z the s8 stop rule.

## 9. Budget (C-010 caps: rso/witness/contract.json)

top-level launches 10; CPU 60 minutes; artifacts 200 MB; GPU 0; $0; repair rounds 1; reviewer hours 1.5.

## Draft OPEN items (resolved before this freeze)
  1. P-CHAN rule: RULER.md s5.2 (Argus, C-009-T017; the draft difference rule had size 0.045 and was replaced).
  2. P-ERASE probe set and P-PRES seeds: ERASE_PROBES.md (Cadmus, C-009-T018); seeds in [800000, 900000).
  3. Seed bookkeeping: rso/witness/run_witness.py `subject` records every GA episode seed (Eupalamus, C-009-T016);
     at freeze the recorded seeds are passed as exclusions to all three generators and the final lists committed.
Remaining at freeze: run the two registered subject GA runs FIRST (C-010's first launches), commit genome digests and
seed records, then generate and commit the witness, P-ERASE and P-PRES seed lists, then the preregistration hash.

## 10. Freeze rules

Order (each step committed before the next): this preregistration -> witness machinery frozen (FREEZE_W1) and
challenged by Pallas on synthetic / hand-wired organisms only -> the two subject GA runs (2 launches; genomes,
digests and seed records committed) -> seed lists generated by the s3 procedure and committed -> manifests and
inventories registered -> witness launches -> evaluation -> RESULT.md. No step may be repeated to change an
outcome class; a failed launch is re-run once with identical inputs and both are reported. Any change to s1-s9
after this freeze is a post-observation amendment, recorded as such, and may not touch an outcome already computed.
