#!/usr/bin/env bash
# Does showing the WORKED COMPUTATION teach the model to compute (vs a no-work
# verdict)? Train two LoRAs on the SAME claims/labels — one whose completions
# contain the reason-first computation trace, one with a bare "Answer: T/F" — and
# eval both (+ base) on HELD-OUT INSTANCES of the same ops with CoT parsing.
# If work >> no-work, computation transfers when shown; the kill's prescription holds.
set -u
PY="C:/Users/jcrai/AppData/Local/Programs/Python/Python311/python.exe"
cd "F:/Prometheus" || exit 1
G="ergon/learner/greedy"
RUNS="$G/runs/compute"; mkdir -p "$RUNS"
LOG="$RUNS/compute_exp.log"; echo "=== compute-exp start $(date) ===" > "$LOG"

echo "=== train lora_trace (work) $(date) ===" | tee -a "$LOG"
"$PY" -m ergon.learner.greedy.train_greedy --train "$G/corpus/compute_trace.jsonl" \
    --out "$RUNS/lora_trace" --epochs 3 --rank 16 --max-len 512 >> "$LOG" 2>&1 || { echo "TRAIN trace FAILED"|tee -a "$LOG"; exit 1; }

echo "=== train lora_verdict (no-work) $(date) ===" | tee -a "$LOG"
"$PY" -m ergon.learner.greedy.train_greedy --train "$G/corpus/compute_verdict.jsonl" \
    --out "$RUNS/lora_verdict" --epochs 3 --rank 16 --max-len 512 >> "$LOG" 2>&1 || { echo "TRAIN verdict FAILED"|tee -a "$LOG"; exit 1; }

echo "=== eval trace (+base) on held-out, CoT $(date) ===" | tee -a "$LOG"
"$PY" -m ergon.learner.greedy.eval_greedy --cot --gold "$G/corpus/compute_heldout.jsonl" \
    --lora "$RUNS/lora_trace" --out "$RUNS/eval_trace.json" >> "$LOG" 2>&1

echo "=== eval verdict on held-out, CoT $(date) ===" | tee -a "$LOG"
"$PY" -m ergon.learner.greedy.eval_greedy --cot --gold "$G/corpus/compute_heldout.jsonl" \
    --lora "$RUNS/lora_verdict" --out "$RUNS/eval_verdict.json" --skip-base >> "$LOG" 2>&1

# Cross-op transfer: ops NOT in training (summation/inequality/perfect_square)
echo "=== eval trace on CROSS-OP transfer (+base), CoT $(date) ===" | tee -a "$LOG"
"$PY" -m ergon.learner.greedy.eval_greedy --cot --gold "$G/corpus/ood_heldout_cot.jsonl" \
    --lora "$RUNS/lora_trace" --out "$RUNS/eval_trace_xfer.json" >> "$LOG" 2>&1
echo "=== eval verdict on CROSS-OP transfer, CoT $(date) ===" | tee -a "$LOG"
"$PY" -m ergon.learner.greedy.eval_greedy --cot --gold "$G/corpus/ood_heldout_cot.jsonl" \
    --lora "$RUNS/lora_verdict" --out "$RUNS/eval_verdict_xfer.json" --skip-base >> "$LOG" 2>&1

echo "=== compute-exp complete $(date) ===" | tee -a "$LOG"
