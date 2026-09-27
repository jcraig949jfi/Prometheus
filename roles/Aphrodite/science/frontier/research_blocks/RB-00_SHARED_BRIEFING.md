# RB-00 -- SHARED BRIEFING FOR ANY WORKER TAKING AN APHRODITE RESEARCH BLOCK

Read this first (10 minutes), then your block. Plain ASCII. Written 2026-09-27.

WHAT APHRODITE IS
  Aphrodite studies recursive self-improvement in an EXACT small world. Programs are integer
  folds ('fold', init, body, final) over a list of integers plus a trailing query:
    vals = nums[:-1]; first = nums[0]; last = nums[-1] (the query m)
    acc = init; for v in vals: acc = body(acc, v, first, last); return final(acc, ...)
  G4 grammar (engine/basis_v4.py): 10,842 bodies (depth-2 over acc, v, first, last, 0, 1;
  ops + - * // % gcd pow), 116 inits, 180 finals, ceiling CEIL = 10^40 (beyond it: None).
  A LIBRARY is an ordered list of entries (inits x bodies x finals), walked before the full
  G4 fallback. Search is charged 1 per candidate with an escrow of 250,000
  (engine/fair.py: KLib, Cell, search_collect). PRISTINE = H1 {0,1} x H2 (422 bodies over
  acc and v only) x 180 finals.
  G1 = the schema (acc + {H}), derived ENDOGENOUSLY by a donor. {H} is filled from LEVEL1
  (258 depth<=1 expressions) giving 161 in-space bodies. L1 = [G1 entry] + PRISTINE.
  THE IMPROVER (fixed) = a17.donor:
    solve OBSERVE families -> group solutions into whole-program semantic classes
    (member enumeration in library coverage + cert.py certificates) -> single-hole LGG
    over pairs of member bodies from distinct classes (tier3d.derive_schemas) -> select a
    candidate library by paired validation-cost savings (a17.select).
  NOVELTY RULER (tier3e.semantically_new): a schema is NEW iff some instantiation mentioning
  v has a body mechanism key (signature + conjugate on a frozen grid) outside G1's keys.
  Known defects (synthesis s2 A4): false positives on (acc - {H}) and ({H} + v); a grid
  with negative acc makes abs() variants look novel.
  TRIBUNAL (engine/meta_tribunal.py): >= 99% on extrapolation (len 20-60), stress (len 200)
  and counterexamples, AND permutation invariance of the answer. This certifies
  commutative bounded folds only.

READ, IN ORDER
  science/frontier/APHRODITE_FRONTIER_SYNTHESIS_2026-09-27.md   (all of it)
  science/frontier/BACKLOG_RSI_FRONTIER.md                       (your thread[s])
  engine/AMENDMENT_15_2026-09-24.md and AMENDMENT_17_2026-09-26.md (recursion criterion)
  pivot/APHRODITE_AMENDMENT16_CAMPAIGN_REPORT_2026-09-26.md
  science/frontier/spikes/k1..k7 *.py and their JSON outputs (patterns to copy)

HOW TO RUN THINGS (Windows host M4, Git Bash)
  - Work in a worktree on a branch; NEVER `git pull` in C:\Prometheus. Commit with
    -c user.name=<your seat> and push your branch.
  - Import engine modules as the spikes do (sys.path to roles/Aphrodite/engine).
  - Set os.environ["A17_FASTEVAL"] = "1" and call a17.worker_init() in each worker. The
    fasteval evaluator passed a 288k-pair equivalence gate (engine/A17_GATE_2026-09-26.json).
    a17.qualify is the exact-fast Q2.
  - Every process pool needs a17.worker_init as its initializer (a per-worker MARKER_DIR),
    or recipients corrupt each other.
  - After any pool, verify PIDs are gone (Get-CimInstance Win32_Process -Filter
    "Name='python.exe'"). TaskStop does not kill detached children.
  - 8 cores. A donor takes ~2-4 min; a foundry of ~400 draws takes ~20 min; K-spikes take
    1-20 min.

DISCIPLINE (non-negotiable)
  - Never modify frozen files: engine/AMENDMENT_*, a16.py, a17.py, *_RESULTS_*, A17_*.json.
  - Use forensic seeds/labels unique to your block (e.g. "RB2-..."), never campaign seeds.
  - Anything that yields a DISPOSITION must be frozen first in a dated AMENDMENT
    (committed before code runs). Forensic spikes may run without one but must say
    "forensic, not a disposition".
  - Report against the frozen criterion even when the failure is your own defect.
  - Nothing here is Campaign 1 evidence. Campaign 1 stays frozen.
  - Comms: experiments are not managed via Aporia or Cyclops. Operator rulings come from
    James.
