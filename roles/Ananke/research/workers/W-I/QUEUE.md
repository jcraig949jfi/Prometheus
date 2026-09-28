# W-I QUEUE

Q1 2026-09-28 05:12Z  W-I main (PLAN.md, frozen): reader-axis swap trajectories +
   twin profiles for 33 specimens, then robustness (6 conditions x 33).
   Command: WI_DEV=cuda WI_CHUNK=64 python roles/Ananke/research/workers/W-I/main.py
   then robust.py. Needs GPU lease ~45 min, <2 GB. GPU BUSY (W-H until 06:50Z).
   Meanwhile: the SAME experiment (same seeds, arms, grid) is started on CPU with
   torch.set_num_threads(2) (no lease needed per COMMON_RULES); main.py resumes
   per specimen, so a GPU run later only fills in what CPU has not finished.
