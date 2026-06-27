"""run_dispatch_llm.py — crash-safe launcher for the production dispatch LLM run.

The prior production run (run_branch_c_xover) died at gen 443 with a 0-byte console
(shell-redirect zeroing) and NO crash diagnostic. This wrapper writes any traceback
to crash.log with an explicit flush so a silent death can't recur. The evolve loop
itself writes evolve_log.jsonl per-gen (the result-of-record).

Launch detached via Start-Process (see the launch block in the session notes); do NOT
shell-redirect this process's stdout in a background job.
"""
from __future__ import annotations
import sys, time, traceback
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))
from blackboard_evolve import evolve

RUN_DIR = ROOT / "run_branch_c_dispatch_llm2"
RUN_DIR.mkdir(parents=True, exist_ok=True)


def _stamp(msg):
    with open(RUN_DIR / "launcher.log", "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}\n")
        f.flush()


if __name__ == "__main__":
    # 800 gens (not 3000): deterministic converged to 0.833 by ~gen 400, and the prior
    # llm run barely used Granite (0.14 mut/gen, flat at deterministic from gen 9). 800
    # is a fair comparison — if Granite beats deterministic's 0.833 it shows here; if not,
    # we've spent ~25h not ~4 days. Watch max_acc>0.833 / max_routable_acc / genuine_routing.
    _stamp("dispatch llm run START — gens=800 pop=24 mode=llm crossover=0.3 dispatch=True")
    try:
        evolve(gens=800, pop_size=24, mode="llm", seed=20260627,
               run_dir=str(RUN_DIR), log_every=10, checkpoint_every=50,
               crossover_frac=0.3, seed_variant="default", dispatch=True)
        _stamp("dispatch llm run COMPLETE (reached gen 800)")
    except BaseException as e:
        with open(RUN_DIR / "crash.log", "a", encoding="utf-8") as f:
            f.write(f"\n=== CRASH {time.strftime('%Y-%m-%d %H:%M:%S')} : {type(e).__name__}: {e} ===\n")
            traceback.print_exc(file=f)
            f.flush()
        _stamp(f"dispatch llm run CRASHED: {type(e).__name__}: {e}")
        raise
