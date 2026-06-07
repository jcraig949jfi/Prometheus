#!/usr/bin/env bash
# Leave-one-source-out ablation: train + eval each condition on the FIXED gold set.
# Each step is a fresh process so CUDA memory is released between runs.
set -u
PY="C:/Users/jcrai/AppData/Local/Programs/Python/Python311/python.exe"
cd "F:/Prometheus" || exit 1
GOLD="ergon/learner/greedy/corpus/gold_eval_v1.jsonl"
ABL="ergon/learner/greedy/corpus/ablation"
RUNS="ergon/learner/greedy/runs/ablation"
mkdir -p "$RUNS"
LOG="$RUNS/ablation_run.log"
echo "=== ablation start $(date) ===" > "$LOG"

CONDS=(full minus_theseus minus_hephaestus minus_erebos minus_pollux minus_charon_md minus_harmonia)

for cond in "${CONDS[@]}"; do
  echo "=== [$cond] train $(date) ===" | tee -a "$LOG"
  "$PY" -m ergon.learner.greedy.train_greedy \
      --train "$ABL/train_${cond}.jsonl" \
      --out "$RUNS/abl_${cond}" --epochs 1 --rank 16 >> "$LOG" 2>&1
  if [ $? -ne 0 ]; then echo "TRAIN FAILED: $cond" | tee -a "$LOG"; continue; fi

  echo "=== [$cond] eval $(date) ===" | tee -a "$LOG"
  if [ "$cond" = "full" ]; then
    SKIP=""   # measure base once, on this gold set
  else
    SKIP="--skip-base"
  fi
  "$PY" -m ergon.learner.greedy.eval_greedy \
      --gold "$GOLD" --lora "$RUNS/abl_${cond}" \
      --out "$RUNS/abl_eval_${cond}.json" $SKIP >> "$LOG" 2>&1
  if [ $? -ne 0 ]; then echo "EVAL FAILED: $cond" | tee -a "$LOG"; continue; fi
  echo "=== [$cond] done $(date) ===" | tee -a "$LOG"
done

echo "=== ablation complete $(date) ===" | tee -a "$LOG"
