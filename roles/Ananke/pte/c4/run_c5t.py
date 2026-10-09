"""PTE-C5T runner: the C4 runner (run_c4.py, unchanged) with the C5T seed namespace.
search_seed = H(C5T_NS = 0xC5001007, task id, cell_key, idx), so no C4 trajectory is reused.
usage: python run_c5t.py PLAN.json OUTDIR WORKER [--deadline-utc ISO] [--max-jobs N] [--device cuda]"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_c4 as RC  # noqa: E402

C5T_NS = 0xC5001007


def search_seed(cell_key, task, idx):
    return RC.C.H_int(C5T_NS, RC.TASK_ID[task], cell_key, idx)


RC.search_seed = search_seed

if __name__ == "__main__":
    RC.main()
