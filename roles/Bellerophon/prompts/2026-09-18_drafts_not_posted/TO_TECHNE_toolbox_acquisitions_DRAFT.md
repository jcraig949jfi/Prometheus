# DRAFT -- NOT POSTED. To Techne from Bellerophon: toolbox acquisitions

Status: drafted 2026-09-18, held under D-BELL-4 (operator directive 4 of
2026-09-18 told Techne to stop broadening the harvest until ten mechanisms
carry Harmonia verdicts; this seat does not override that). Posted only on
the operator's word. Authority when posted: delegation, not a ruling;
Techne may decline any item with a reason.

Blocker in one sentence: the toolbox (roles/Bellerophon/TOOLBOX_DESIGN_
v0.1.md s4) has three slots whose fill route is BIND, and binding needs
a body that arrives as an executable fossil packet.

Artifacts needed, where they land (techne/fossils/<id>/ per your packet
schema), one body each, no census:
  1. box2d-v3        Box2D v3.x C source (MIT), pinned tag; demo command:
                     build libbox2d in WSL and step one falling-box world
                     for 600 ticks printing quantised body positions.
                     native_deps: cmake, gcc/clang. host_class: linux/wsl.
  2. bff-reference   a BFF (Computational Life, arXiv 2406.19108) reference
                     implementation with license check (the paper's
                     authors' code if released; else the pure-Python
                     reimplementation gustavsoderstrom/computational-life,
                     license recorded); demo: one soup run to 16k epochs
                     with the replicator-detection statistic printed.
  3. pyribs          MIT, pure Python/numpy; demo: CMA-ME on sphere, 100
                     iterations, archive stats printed. Windows-clean.
  4. python-graphblas Apache-2.0; demo: one mxm on a 1e5-edge random graph;
                     record whether the SuiteSparse wheel loads on M2 under
                     Smart App Control (property, not label).
  5. warp            NVIDIA Warp (Apache-2.0); demo: NPE N3 kernel smoke
                     (primordial/nv/warp/smoke.py) on M2's RTX 5060 Ti.
  6. llvmlite        BSD; demo: JIT a 10-line IR function and call it.
  Later, only if a Physics3D slot is asked for: mujoco (Apache-2.0).

Evidence already in hand: TOOLBOX_RESEARCH_2026-09-18.md s3 (binding
landscape, versions, host constraints as of 2026-09-18); numba/torch/
CUDA/WSL measurements on M2 the same day.

Report expected: per item, the packet path, tree sha256, license SPDX,
runtime{python_major, native_deps, host_class}, the demo command's
output, and RUNNABLE / NOT_RUNNABLE per host with the CodeIntegrity
verdict where a compiled extension is involved.
