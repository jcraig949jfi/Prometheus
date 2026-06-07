#!/usr/bin/env bash
# Diverse-gold transfer test: does adding balanced computable-gold number-theory
# judgement data (4 domains) correct the False-prior and transfer to 3 HELD-OUT
# number-theory domains never seen in training?
set -u
PY="C:/Users/jcrai/AppData/Local/Programs/Python/Python311/python.exe"
cd "F:/Prometheus" || exit 1
G="ergon/learner/greedy"
RUNS="$G/runs/transfer"
mkdir -p "$RUNS"
LOG="$RUNS/transfer_run.log"
echo "=== transfer start $(date) ===" > "$LOG"

# 1) baseline: full model (NO ood training) on held-out OOD — includes base pass for reference
echo "=== baseline abl_full on held-out $(date) ===" | tee -a "$LOG"
"$PY" -m ergon.learner.greedy.eval_greedy --gold "$G/corpus/ood_heldout.jsonl" \
    --lora "$G/runs/ablation/abl_full" --out "$RUNS/eval_heldout_baseline.json" >> "$LOG" 2>&1

# 2) train transfer model (substrate + ood_train 4 domains)
echo "=== train lora_transfer $(date) ===" | tee -a "$LOG"
"$PY" -m ergon.learner.greedy.train_greedy --train "$G/corpus/train_transfer.jsonl" \
    --out "$RUNS/lora_transfer" --epochs 1 --rank 16 >> "$LOG" 2>&1
if [ $? -ne 0 ]; then echo "TRAIN FAILED" | tee -a "$LOG"; exit 1; fi

# 3) transfer model on held-out OOD (the transfer test) — skip base (measured in step 1)
echo "=== eval lora_transfer on held-out $(date) ===" | tee -a "$LOG"
"$PY" -m ergon.learner.greedy.eval_greedy --gold "$G/corpus/ood_heldout.jsonl" \
    --lora "$RUNS/lora_transfer" --out "$RUNS/eval_heldout_transfer.json" --skip-base >> "$LOG" 2>&1

# 4) transfer model on substrate gold (regression check) — skip base
echo "=== eval lora_transfer on substrate gold $(date) ===" | tee -a "$LOG"
"$PY" -m ergon.learner.greedy.eval_greedy --gold "$G/corpus/gold_eval_v1.jsonl" \
    --lora "$RUNS/lora_transfer" --out "$RUNS/eval_gold_transfer.json" --skip-base >> "$LOG" 2>&1

echo "=== transfer complete $(date) ===" | tee -a "$LOG"
