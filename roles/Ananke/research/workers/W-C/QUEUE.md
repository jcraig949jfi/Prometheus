# W-C QUEUE (ready to run as written)

X4 (PLAN.md; deviation in LOG.md): 6 full-spec GA searches (M2's SearchSpec:
pop 96, gens 36), HOLD at M2 physics, arms A0 (as M2) and A1 (economy
e_income=2, c_emit=1, e_max=64).
Status 2026-09-27 23:05Z: GPU leased by W-B until 00:05Z, cpu8 by W-E.
On CPU one full search takes ~30 min (1 process, 2 threads), so only
A0 seed 0 and A1 seed 0 were run on CPU as an n=1 pilot (out/x4_A0_0.json,
out/x4_A1_0.json; see LOG.md). The decision needs all 6. Run on GPU:

  cd /f/Prometheus-worktrees/ananke-base-role
  python roles/Ananke/research/lease.py acquire gpu --owner W-C --ttl-min 40 --envelope "X4 6 GA searches, <=2 GB"
  for k in 0 1 2; do for a in A0 A1; do
    python roles/Ananke/research/workers/W-C/x4_evolve.py $a $k cuda; done; done
  python roles/Ananke/research/lease.py release gpu --token <token>

(cuda outputs overwrite the CPU pilot files for seed 0; results should be
bit-identical to CPU only if the engine's eager CPU and CUDA-graph paths agree,
which the engine tests assert.)

Decision rule (PLAN X4-P1, fixed): among competent A1 champions (held lo99
>= 0.60) median fire share >= 0.5 while A0 median fire share <= 0.1.
Fewer than 2 competent A1 champions = UNRESOLVED (economy too harsh).
