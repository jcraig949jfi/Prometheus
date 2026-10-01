#!/usr/bin/env bash
# W-Y plant runs: 2 procs x 1 thread, CPU only (unleased, <= 2 threads)
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES= WY_THREADS=1
python wy.py PA 128 670 2,4,6,8,10,12,14 pa > logs/run_pa.log 2>&1 &
echo "PA pid $!"
python wy.py PB 128 670 2,4,6,8,10,12,14 pb > logs/run_pb.log 2>&1 &
echo "PB pid $!"
wait
