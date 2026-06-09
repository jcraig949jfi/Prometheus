# Worked-computation traces vs no-work — result (2026-06-08)

**Question:** the 2026-06-07 kill showed the LoRA learns surface classifiers and
fails where computation is required. The survey's prescription: shape completions
as worked multi-step derivations. Does showing the worked computation actually
teach the model to compute — and does it transfer?

**Design.** Tier-1 computation-trace builder (`compute_traces.py`): judgement-format
claims about computed quantities over 8 elementary ops (gcd, modexp, φ, σ, divisor-
count, binomial, CRT, continued-fraction), balanced T/F, gold computed + independently
re-checked. Two completion styles on the SAME claims/labels:
- **work** — reason-first worked computation, verdict last ("…so σ=4320, but the claim
  states 4323. Answer: False.")
- **no-work** — bare "Answer: True/False." (the ablation)
Train each (3 epochs, rank 16), eval with CoT parsing on (1) HELD-OUT INSTANCES of the
trained ops, (2) CROSS-OP transfer to summation/inequality/perfect_square (never trained).

## Adversarial self-catch (v1 → v2)

v1 false-values were correct±small. That **leaked a surface cue**: φ(n)/σ(n) are even,
so an odd stated value ⇒ False with no computation. The v1 no-work model scored 0.80 by
parity-cheating; only continued-fraction (a list, no parity cue) showed the truth
(no-work 0.47 = chance, work 0.93). **v2 fixes this with hard negatives**: each false
value is the genuine output of the SAME op on a NEARBY input — same parity, magnitude,
structure — so it can't be discriminated without computing. Parity confirmed balanced.

## v2 result (hard negatives)

**In-op held-out** (unseen instances of trained ops):
```
                acc      T      F
base           0.194   0.05   0.34   (parse-fail 0.63 — base can't even format)
WORK (trace)   0.783   0.78   0.79
NO-WORK        0.658   0.70   0.62
```
Excluding gcd (see caveat): **WORK 0.776 vs NO-WORK 0.612 — gap +0.164.** Per-op gap
(work−nowork): continued_fraction +0.28, φ +0.25, σ +0.20, binomial +0.17, modexp +0.10,
CRT +0.10, divisor_count +0.05 — and gcd −0.15.

**Cross-op transfer** (summation/inequality/perfect_square — NEVER trained):
```
                acc      summation  inequality  perfect_square
base           0.257    0.34       0.16        0.27
WORK (trace)   0.617    0.39       0.67        0.79
NO-WORK        0.627    0.52       0.83        0.83
```

## What this means (calibrated)

1. **Worked computation genuinely teaches the model to compute the trained ops** —
   +0.16 over no-work on held-out instances, positive on 7/8 ops. Showing the derivation,
   not just the verdict, is the difference between a per-op classifier and a model that
   re-derives the answer for new numbers. This validates the survey's core prescription
   **at the per-operation level.**
2. **But it does NOT produce transferable computation.** Cross-op, worked traces are no
   better than bare answers (0.617 ≈ 0.627), and the canonical computation domain
   **summation stays unsolved (~0.39–0.52)**. The skill is operation-specific procedural
   learning, not general computational ability. The cross-op lift over the substrate
   baseline (~0.53→0.62) is format-following, shared by both styles — not reasoning.
3. **A capability ceiling exists.** modexp (multi-step modular square-and-multiply) sits
   at 0.52 even WITH traces — the 1.5B model can't reliably execute the longer procedure
   in generation, trained or not. Some computations exceed this model/rank.

**gcd caveat:** gcd no-work scored 0.98 (beating work). The gcd answer must DIVIDE its
inputs, and divisibility-by-small-v is itself a cheap check (v=2 ⇒ parity), so gcd retains
an intrinsic shortcut hard negatives can't remove. gcd is excluded from the headline gap.

## Implication for the program

The lever is **coverage, not transfer**: worked-trace training teaches each operation it
covers, so a BROAD computation-trace corpus (many ops × traces) would teach many ops — but
don't expect a narrow op set to generalize to unseen ops. And harder procedures (modexp-
class) likely need a larger model than 1.5B/rank-16. This refines the 2026-06-07 kill: the
bottleneck is partly data (per-op coverage with worked traces helps) and partly capacity
(transfer + hard procedures don't come for free).

This also reframes the falsifiable prediction I filed: **partially falsified** — worked
traces moved the *trained* ops but did NOT move the held-out computation domains
(summation) where verdict-only was flat. Showing work is necessary-not-sufficient.

## Artifacts
- Builder: `ergon/learner/greedy/compute_traces.py` (v2, hard negatives)
- Corpora: `corpus/compute_{trace,verdict,heldout}.jsonl`, `corpus/ood_heldout_cot.jsonl`
- Runner: `run_compute_exp.sh`; evals: `runs/compute/eval_{trace,verdict}{,_xfer}.json`
- Eval CoT support: `eval_greedy.py --cot`; `train_greedy.py --max-len`

— Ergon, 2026-06-08
