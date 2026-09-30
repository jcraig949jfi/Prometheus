#!/bin/bash
# usage: run.sh <script.py> [args...]  (1 thread, CPU only, no bytecode)
cd "$(dirname "$0")"
export CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 WV_THREADS=1
s=$1; shift
tag=$(basename "$s" .py)${1:+_$1}
python -B "$s" "$@" > "logs/$tag.log" 2>&1
echo "RC=$?" >> "logs/$tag.log"
