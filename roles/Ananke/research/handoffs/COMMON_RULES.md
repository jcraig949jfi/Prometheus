# Rules for every Ananke research worker (read before starting)

WORKTREE: F:/Prometheus-worktrees/ananke-base-role (the PTE engine is
prometheus/ananke/).

YOUR OUTPUT DIRECTORY: roles/Ananke/research/workers/<your id>/.
Write ONLY there. Do NOT git commit, push, merge or stash: Ananke commits
for you. Parallel workers share this worktree, so git writes collide.

DO NOT EDIT: prometheus/ananke/{engine.py, oracle.py, envs.py, assays.py,
search.py, c1b.py, c1b_run.py, plants.py}. These are the frozen physics
and C1/C1b code paths. Put your own probes in your output directory. You
may import prometheus.ananke.lens (between-tick interventions: swap,
roll_slots, roll_recipients, run, trial_acc, ci, swap_verdict) and you may
copy it. Interventions act only between ticks, so the physics stays
untouched.

SCIENCE HYGIENE
- Before running any experiment, write PLAN.md in your directory with
  the question, predictions and decision rules. Do not change thresholds
  after seeing results.
- Keep every Attempt in LOG.md, including bugs and failed runs.
- Worlds: use your assigned analysis namespace (below), 64 worlds = 32
  mirror pairs (lens.run handles mirroring), and 99% bootstrap over pairs
  (lens.ci).
- If the evidence contradicts a hypothesis in your brief, say so plainly.

COMPUTE AND LEASES (collision avoidance)
- Small CPU runs: call torch.set_num_threads(2) and no lease is needed.
- Any GPU use: first run
    python roles/Ananke/research/lease.py acquire gpu --owner "<your id>" --ttl-min <minutes> --envelope "<what>"
  keep the token, and run
    python roles/Ananke/research/lease.py release gpu --token <token>
  when done, when you abandon, or after a crash. Use the smallest ttl.
- If acquire prints BUSY: do NOT wait in a loop and do NOT compete. Record
  the experiment in QUEUE.md (ready to run as written) and continue with
  CPU-scale work, analysis or literature.
- Multi-core CPU (> 2 threads for > 5 min): lease cpu8 the same way.
- No cloud spend and no network services started.

SPECIMENS AND DATA
- C1 rows: roles/Ananke/pte/c1_rows/cells.jsonl.gz. Load a specimen with
  prometheus.ananke.c1b_run.load(cell_id) -> (physics, env, genome, row).
- C1b package: roles/Ananke/pte/c1b/ (C1B_SUMMARY.json, REVIEW_PACKET).
- 2026-09-27 spikes: roles/Ananke/research/spikes/ (scripts) and
  spikes/out/*.json (raw outputs). The plan and log are in
  roles/Ananke/research/SPIKES_2026-09-27_{PLAN,LOG}.md.
- Register map / decompilation: prometheus.ananke.plants.regmap(physics)
  and plants.OPS. The program fields are pre-reduced mod NOPS / n_write /
  n_read in engine.World.__init__.

FINAL DELIVERABLE: REPORT.md in your directory (<= 2 pages), with what
you tested, what held, what failed, what surprised you, and which
follow-up Threads you propose. Your final message is a 10-line summary.
