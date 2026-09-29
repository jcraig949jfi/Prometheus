# W-B PLAN: what does SETRULE contribute in PTE champions?

Written 2026-09-27 BEFORE any W-B experiment. Only prior inputs: the brief,
spikes/out/s_m3.json, and a static disassembly of the two M3 genomes
(disasm.py; no simulation). Thresholds below are frozen; I will not change
them after seeing results.

## Static observation that shapes the predictions (from disasm + engine)
At tick 0 every register is zero (S, inbox, O-regs). SETRULE sets
r_next = A mod rules, so ANY SETRULE whose A operand reads a still-zero
register sends an awake site to rule 0. In both M3 genomes every rule
variant contains such a SETRULE (e.g. 0a23 r1 l12 A=PAY1, f6b6 r0 l3
A=RPORT which is always 0 there). Expected after tick 0: share at rule 0 =
awake(0.8) + 0.2*0.25 = 0.85, which is exactly s_m3's 5442/6400. So the
"bootstrap" may be a GENERIC zero-register default, not an evolved
configuration. In f6b6 rule 0 is hard-absorbing (A=RPORT=0 always);
in 0a23 rule 0 stays only if IN2_1 = 0 mod 4 (possible ongoing gate).

## Setup
Namespace 0x5E5: SEEDS = assays.world_seeds(0x5E5, 64), 32 mirror pairs.
Accuracy = lens.trial_acc over all trials unless stated. Pre-first-tick
hooks via my own copy of lens.run (probe.py) that applies a `pre(world)`
before step 1. Per-site freeze = hook after every tick that rewrites
w.r[mask] := pinned value (equivalent to SETRULE ignored at those sites,
since the program always reads r set before the tick).

Paired statistics: d = arm - normal per pair; 99% bootstrap CI (lens.ci).
- HURTS: hi99(d) < 0.
- EQUIV: lo99(d) > -0.05 (equivalence margin 0.05).
- otherwise UNRESOLVED.

## Part 1: M3 specimens (0a23398f20cc41a2, f6b623cdb23afd2c)
X1 census: r[B,N] after every tick; partner difference at ANY site/tick
   (count, not a mean); rule changes after trial 0; settling time.
X2 uniform init r:=k before tick 1, k=0..3, SETRULE frozen (freeze_rule).
X3 uniform init r:=0, SETRULE ON.
X4 control: default random init + freeze_rule from start (expect ~0.53,
   matches s_m3 E5; a mismatch means my harness is wrong).
X5 per-site: (a) readout site(s) pinned at their r0, others free;
   (b) readout free, others pinned at r0; (c) r:=0 everywhere but a
   fraction f in {0.05,0.1,0.25,0.5} of NON-readout sites pinned at a junk
   rule; (d) all non-readout junk sites pinned at one rule k in {1,2,3}
   (is the harm "some rule other than 0" or specific to which rule).
X6 repair: at mid of trial 4 randomize r uniformly (all sites); then
   (i) SETRULE on, (ii) freeze from then on. Accuracy on trials 5..11 and
   ticks to re-settle.
X7 exact reduction: rules=1 physics with rule-0 program vs rules=4 r:=0
   frozen: compare traces bitwise.
X8 transfer across physics: in 3 neighbouring physics (update_p 1.0,
   loss 0.15, lat_base 3) compare normal vs r:=0+freeze.

Predictions (bootstrap-only account): X2 k=0 EQUIV; k=1..3 ~0.5 (HURTS);
X3 EQUIV (maybe trial-0 gain); X1 partner diff = 0 at every site/tick,
no rule change after tick ~5; X5 both (a) and (b) HURT, (c) graded;
X6(i) recovers in <=3 ticks, X6(ii) HURTS; X7 bit-identical; X8 EQUIV in
all three. A result against the account: X2 k=0 HURTS or X3 differs from
X2 k=0 (the transient or ongoing SETRULE matters), any partner r
difference, or r changes after settling.

## Part 2: census over C1 SIGNAL cells with rules > 1, setrule = 1,
held lo99 > 0.55 (kind evolve; 42 rows by metadata count, results unseen)
Arms per cell (namespace 0x5E5, cell's own physics and env):
 N normal; F freeze_rule from start; U_k uniform r:=k + freeze, k in all
 rules; TS transplant same world: r at end of trial 1 (tick 2*Pd-1) of
 the normal run, applied before tick 1, frozen; TX transplant cross
 world: config of pair p+1 (both partners get world 2(p+1)'s config;
 wraps); FA freeze from tick 2*Pd (after settling); census as X1.

Classification (applied in this order):
 INERT        F not HURTS (SETRULE not needed at all). Sub: EQUIV or weak.
 ONGOING      FA HURTS. Sub-tag CUE_CARRYING if partner r differs at any
              site/tick in N.
 UNIFORM_BOOT modal-rule share >= 0.99 of site-ticks after trial 1 AND
              U_modal EQUIV. Sub-tag ZERO if the modal rule is 0.
 PATTERN_BOOT not uniform, TS EQUIV; sub-tag GENERIC if TX EQUIV else
              WORLD_SPECIFIC.
 TRANSIENT    FA EQUIV but neither U_modal nor TS EQUIV (the settling
              dynamics themselves, or r history, carry something).
 UNRESOLVED   anything else.
Additionally report: CUE_CARRYING anywhere, share of cells whose modal
settled rule is 0, and best U_k vs U_modal.

Census prediction: >= 60% of non-INERT cells are UNIFORM_BOOT/ZERO (the
zero-register default); ONGOING <= 20%; CUE_CARRYING rare (<= 3 cells).

## Compute
GPU under lease (roles/Ananke/research/lease.py, owner W-B). If BUSY:
QUEUE.md + CPU with torch.set_num_threads(2).

## Addendum A (2026-09-27, written after seeing 18/42 census rows, before
## any Part-3 run): Part 3, deep dive on non-bootstrap cells
Trigger: census rows classed ONGOING (several CUE_CARRYING), TRANSIENT or
UNRESOLVED. For every such cell in the final census:
 Y1 swap r between mirror partners at the mid tick of every trial
    (c1b.ticks mid for HOLD; t0 + max(1, delta//2) otherwise, as s_ct);
    verdict by lens.swap_verdict (FLIP / NO-EFFECT / CHANCE).
 Y2 same swap for site state without r, and for in-flight arrays.
 Y3 readout-site r at the readout tick: share of scored trials where it
    differs between partners, and in-sample accuracy of the best
    rule->sign map for predicting y (reported next to normal accuracy).
 Y4 after settling (from tick 2*Pd-1) pin r at (a) the readout site only,
    (b) every other site; paired vs normal on trials 2..end.
 Y5 where partner-differing r lives: share at the readout site, at sense
    sites, elsewhere.
Decision rule: r is THE bit carrier if Y1 FLIP; a contributing carrier if
Y1 CHANCE; not a carrier if NO-EFFECT. Y4 localizes the ongoing need.

## Addendum B (after Part-3 rows for 6 cells): descriptive only, no verdicts
Y6 readout-site rule time course: per trial phase (tick mod Pd), share of
   worlds whose readout site runs a non-modal rule, split by the sign of
   y. Y7 static: which rule variants write S0 (disasm). No thresholds.

## Addendum C (after Y6/Y7 on 5 cells): write-gate test, 311c465f and faafa5b0
Y7 shows S0 is written ONLY by rule 1 in both (HOLD, readout = sense site),
and Y6 shows the readout enters rule 1 around the cue window. Hypothesis
G: rule switching is an input write-gate: rule 1 = write S0 from SENSE,
rule 0 = hold (ignore distractors). Test, readout site pinned from tick
2*Pd-1, trials 2..end, vs normal of the same env:
 Z1 pinned to the S0-writing rule (1), distractors on (env as trained):
    predict HURTS.
 Z2 same with amp_dist = 0 (no distractors): predict EQUIV vs the
    normal run of that env (gate needed only because of distractors).
 Z3 pinned to rule 0: predict HURTS with and without distractors.
G is refuted if Z2 HURTS (the rule-1-only program cannot hold even with
no distractors -> the gate does more than distractor protection).
