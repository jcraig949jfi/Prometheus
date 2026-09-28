# W-L QUEUE (ready to run as written; GPU lease required)

Preregistered searches (PLAN.md s2, s4). From roles/Ananke/research/workers/W-L:

    python run_search.py --n 0 --seed 0 --device cuda     # pipeline control
    python run_search.py --n 0 --seed 1 --device cuda
    python run_search.py --n 1 --seed {0,1,2,3} --device cuda
    python run_search.py --n 2 --seed {0,1,2,3} --device cuda

Outputs out/search_n<n>_s<seed>.json. Queued 2026-09-28 06:5xZ while W-J held the GPU.
was held by W-J (E6) at the time; status below is updated as they run.

STATUS: ALL 10 RAN 07:11-07:21Z under lease c1aec189c26a (released 07:41Z). Nothing left queued.
