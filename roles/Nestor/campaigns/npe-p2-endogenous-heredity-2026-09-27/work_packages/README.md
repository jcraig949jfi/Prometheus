# Research-ready work packages (P2, Nestor)

Each package is self-contained. A fresh researcher (human or agent) can take it from Git and work for hours.
They share one setup, below; each package then states its own question, context, method, rulers, controls,
resources and done-criteria.

## Common setup (read once)

**Branch and worktree.** Work in a git worktree of `nestor/s1-forensics-2026-09-23` (or of main after it has
been merged). Rules:
- Never edit a file under `roles/Nestor/campaigns/z80atlas-verify-2026-09-22/`; its frozen code is protected by
  `verify_freeze`.
- Never edit a closed experiment's directory.
- New work goes in a NEW directory, and needs a new graph node (`roles/Nestor/graph.py`, `put()`).

**The substrate (NPE pair tape).**
- Two genomes of 64 bytes (7ae3/ffa6 cells) sit on one 128-byte tape. Organism a is at offset 0 and executes
  first; b is at offset 64 and executes second. Each gets a step budget ("slice").
- The VM is `z8.py`. Addresses wrap modulo 128. The fresh register state is all zeros.
- Organisms carry their registers across executions unless a runner resets them.

**Runners.**
- `x_donor_swap/run_ds.py` `runner_cls(world)` is the ATOMIC write-back runner used throughout.
- `run_ds.cells()` gives the frozen cells.

**The copy criterion.**
- A replication event is "accepted" by the predecessor criterion.
- It is CAUSAL only if P-11 (`p11.py`) certifies it: the donor rebuilds a randomized victim, donor authorship
  holds, and the donor-disabled control stays unlike the donor.

**Rulers.**
- COMPETENT genome: `x_donor_discovery/run_dd.py` `screen` / `assay_one`. This is the fresh-start P-11 assay
  from the ZERO register state, 4 then 20 seeds, rate >= 0.5.
- World-faithful copy under any state: `x_dd_nocopy_context/run_nc.py` `copies`.
- Self-state measure: `x_dd_selfstate/run_ss.py`.

**VMs.**
- Stock `z8`.
- Dense (1-byte aliases 0xE5 = LDIR, 0xE7 = LDDR): `x_dd_dense_copy/run_dc.py` `dense_z8`.
- Sham (1-byte random block write): `x_p2_sham/run_sh.py` `sham_z8`.
- ALWAYS set `world.z8` explicitly per job, and use one job per process (`maxtasksperchild=1`).

**Discipline (Nestor charter).**
- Declare every experiment (question, arms, ruler, classification rule) in its docstring and in the graph BEFORE
  running it.
- EXPLORE results never promote. A claim needs a fresh frozen CONFIRM: fresh seeds, a frozen rule, and no
  adaptive allocation.
- Guards must be able to fire; add a fail/pass self-test for any intervention.
- Theory-aware by date: do not present results as Selective-Irreversibility evidence.

**Resources.**
- Heavy runs (10 worker processes) need a CPU lease. Reuse the existing reservation table:
  `python scripts/gpu_reservation.py acquire M1 CPU-POOL-NESTOR <holder> --purpose "CPU lease ..." --ttl <s>`.
  Release it when done, and log the lease in `LEASES.jsonl`.
- Launch long runs with one-shot schtasks (`launch_*.cmd` pattern), not as children of the Bash tool.
- Never `rm -rf`; never `git stash`.

**Key evidence to read first.**
- `../npe-w1-donor-discovery-2026-09-26/W1_REPORT.md`
- `../BACKLOG.md`
- `../delegates/corpus/CORPUS_ANALYSIS.md`
- `../delegates/EXTERNAL_RESEARCH.md` (sections 2-3)
- `../delegates/CROSS_ENGINE.md` (section 7)
- `../SYNTHESIS.md`

## Packages

| id | title | resource | status |
|---|---|---|---|
| WP-1 | Entry-state decomposition and the certification circularity | LEASED | ready |
| WP-2 | Descendant-competence failure at S2 -> S3 and S4 -> S5 | LEASED + LIGHT | ready |
| WP-3 | Environment-borrowing copiers: operand provenance and lineage trajectory | LENS + LIGHT | ready |
| WP-4 | Endogenous state robustness and lineage identity | LEASED | ready (after X-P2-LINEAGE) |
| WP-5 | Acquisition rivals: presence, density, byte distribution, random-walk baseline | LEASED + LIGHT | ready |
| WP-6 | External replication-barrier synthesis and minimal-donor landscape | REPO + LIGHT | ready |
