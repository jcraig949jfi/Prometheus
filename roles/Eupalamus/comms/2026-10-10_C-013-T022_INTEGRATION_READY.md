C-013-T022 INTEGRATION_READY -- Eupalamus[harry1-93a529ba], claude-opus-5-5 (Q2), harry1.

Branch eupalamus/c-013-t022 (base ae55dccaa; origin/main 38e82946a merged in, tests green on the merged tree).
Receipt: ops/campaigns/C-013/tasks/C-013-T022/attempts/A-001/RECEIPT.json. Write-up: rso/scale/runner/FIRE_TEST.md.

FIRE TEST: PASS 13/13 (run fire-1: Aether kernel 128x128, 2 partitions x 16 epochs, pinned worktree d72fb0eb9).
- Launch: in helper session 124bd1dc, whose launcher killed itself. The job kept computing after the launcher and
  that session had died.
- Kills, by this seat: the worker mid-epoch (supervisor respawned one, which replayed epoch 4: VALID), then the
  supervisor and its replacement worker mid-epoch. Nothing moved while the job was down.
- Relaunch: in a DIFFERENT helper session, 07fac962. The job resumed fire-p0 from head 4, not from genesis.
- Final run digest 1ab5132a36686f6e... == uninterrupted control. 32/32 epochs published exactly once.
- Wasted work accounted: 2 interrupted attempts, 60 ticks / >= 1.45 CPU-s (lower bound, metered to the last
  PROGRESS row) plus one 5.5 CPU-s verification replay.
- 286 CPU-s total, including the control (cap 1 core-hour). Compute never exceeded 2 processes.

C-012 alignment: identity is moonshot.epoch.model itself (make_genesis / derive_spec / execute / verify_epoch /
replay_chain), imported read only. The table of same / diverging records is in FIRE_TEST.md s5. Divergences:
- transport (local directory and JSONL vs Postgres);
- a host-local lease fence;
- contests halt with no resolver or rewind;
- validations are RESUME_CHECK rows.

Aether: kernel, recipe and digest imported read only; notice #2006; no Aether file touched.

Tests: 35 OK. Mutation check 13/13 killed. RED first at f669c3806.

Caveats (in the receipt):
- the cross-session resumption was not replayed (1-in-4 sample; the first resumption had replayed);
- the POSIX detach path was not exercised;
- there is no automatic relaunch after host loss;
- single host only;
- no checkpoint retention policy.

Proposals for you to accept or drop (not built):
(a) move the runner onto NF transport, now that C-012-T003 has closed (974275bca);
(b) a host-scheduler `launch` entry, so a dead job relaunches without any session;
(c) a checkpoint retention policy before any long or large run.
