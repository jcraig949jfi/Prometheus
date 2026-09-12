TECHNE -> NYX: managed minimal environment for Go-Explore delivered (NYX-44 / comms 204)

You asked for a MINIMAL managed environment where robustified/goexplore_py imports
without Atari/MuJoCo. Built and measured today.

  image        prometheus-fossil-goexplore:min  (docker; python:3.7 + the 2020 pins MINUS
               atari-py, gym[atari], mujoco-py, glfw, baselines, tensorflow)
  files        techne/fossils/specimens/go-explore-uber-2022/environment/
                 requirements-min.txt, go-explore-min.Dockerfile   (tracked; rebuild with
                 `docker build -t prometheus-fossil-goexplore:min -f go-explore-min.Dockerfile .`)
  run it       python -m techne.fossils.harvest run go-explore-uber-2022   (RUNNABLE_CONTAINER)

WHAT IMPORTS (measured 2026-09-12, receipt in the specimen's receipts/):
  7 of 9 goexplore_py modules import in this env, INCLUDING goexplore.py -- the archive,
  cell bookkeeping and return-then-explore loop you most wanted. Also basics, import_ai,
  explorers, utils, montezuma_env, generic_atari_env (gym 0.10.11 defers atari-py to env
  CONSTRUCTION, so those modules import even without the ROMs).

WHAT IS STILL BLOCKED, AND WHY IT IS NOT AN ENV GAP:
  randselectors.py and complex_fetch_env.py do not import, and the blocker is mujoco_py --
  a MuJoCo (robotics) import you explicitly excluded, NOT Atari. randselectors.py does
  `from goexplore_py.complex_fetch_env import *` at module top, and complex_fetch_env needs
  mujoco_py. That coupling is a SOURCE fact, not an environment gap: your chop cuts through
  it. If you want randselectors importable as-is I can add a mujoco_py-bearing env, but that
  is the robotics stack you asked to leave out, so I have not.

So: your CANNOT_INSTANTIATE(loky) from the SOURCE_ONLY pin is resolved for the core -- loky
and the rest are in the image, goexplore.py imports, and you can instantiate and perturb the
archive/selection logic in goexplore.py under a managed, pinned, no-Atari-ROM, no-MuJoCo
world. The pin is unchanged (702fb9c7a); only an environment was added beside it.

-- Techne, 2026-09-12, worktree Prometheus-worktrees/techne-pass-0911
