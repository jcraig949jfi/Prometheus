# C-010 W1 adjudication (Palamedes, 2026-10-07) -- the one registered repair round (PREREGISTRATION s8)

Input: rso/witness/challenge/W1/REPORT.md (Pallas, claude-fable-5-1, Q3), authoritative for its observations. No
registered subject has run; no witness outcome exists; every repair below lands before any.

Repair (all of them; each bears on the registered run or pins a registered rule):
  R1 (S-1)  evaluate: a node id presented by more than one bundle is REFUSED with a typed reason (no argument-order
            resolution); the RESULT lists which launch supplied each node.
  R2 (S-2)  evaluate: --seeds REQUIRED and takes the committed SEED_LISTS.json (make_configs): every P-RET, P-CHAN,
            P-CAL arm (NULL, SHUF, POS) must run on the registered witness list; P-OBS on it; P-ERASE on the registered
            triples; P-PRES on the registered pairs. A mismatch refuses the node (UNQUALIFIED, not negative).
  R3 (S-3)  evaluate: P-ERASE requires regimes (pre_a, pre_b) = (0, 1) per triple and S / S-LEAK on identical
            triples; P-PRES requires the warm-up regime opposite to the seed's.
  R4 (S-4)  evaluate: the node id is rebuilt from the receipt's own subject digest, arm, predicate and world and must
            equal the manifest's id; the subject digest must equal the subject the node is filed under.
  R5 (S-5)  ares_client: NULL per AMENDMENT_v1.0.1 (plasticity disabled as S-NOPL + reset_each_step).
  R6 (S-6..S-10)  pins: the post-LAST-interrupt window through the evaluator (W1 S3 shape); S-NOPL works on a copy
            (a subject with R != 0 keeps it); RUN_UNREPORTED with a re-registered manifest; P-ERASE / P-PRES oracle
            counterfeit refused; P-CAL margin at 1074 and 1077 (one-sided, FD-T014-3).
Recorded, not repaired (known escapes for RESULT.md): B4 two-back leak (not reachable under S.Runtime: the registered
runtime restores W1 at every episode reset); B6 counterfeit trace for a bundled genome (a consistently lying producer;
the contract's trust limit -- custody records bytes, not their truth).

After the repair: integration + dry run + FREEZE_W2, then a short fresh re-check by Pallas (1 sound, 1 broken, 1 edit
on R1-R5, synthetic only), then T020. The re-check is extra rigour before outcomes, not a second repair round.
