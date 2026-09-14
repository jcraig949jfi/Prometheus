# Nestor-B journal (lane B: SOUP)

## 2026-09-14 iteration 1 -- B1 crossover crucible  [m1-5b2d34d4]

- Ran: wforge Encounter semantics in 5 forms (numpy batched, numba prange x3,
  Redis Lua 1 EVALSHA/tick, Lua k ticks server-side, FalkorDB Cypher 1 query/tick)
  on private substrate 6391. Oracle = sha256 trace hash == wforge, 40 worlds x 8
  seeds, zero tolerance. All 5 forms 320/320 (numpy also obs-hash 320/320).
  Cheat skip_lin: 0/320 in every form it ran on (np, nb, luak, fk).
- Surface (steps/s, 2 worlds, n_envs 1..65536): numba wins every cell (0.9M-3.8M
  at n=1, plateau 46-70M). numpy overtakes wforge (~63-128k) between 16 and 64
  envs (~0.7-4.0M at scale). Lua k-ticks plateaus ~100-200k and beats numpy only
  at n<=16. Lua/tick reaches 117-183k by 65536 envs. FalkorDB is slowest in every
  cell (341 steps/s at n=1, 72k at 16384).
- Producers 1..16 on one Redis: aggregate ceiling ~190k steps/s. Lua/tick climbs
  toward it with P (67k -> 183k at 4096 envs); Lua k-ticks is flat from P=1.
  luak n=4096 P=16: every worker hit TimeoutError reading from socket.
  redis-py socket_timeout is None, so the cause is NOT established.
- What died: my pre-run guess "numpy passes wforge by 16 envs" (it is 16..64).
  My first drafts of all three fast forms drew the stoch kick index before its
  value; wforge evaluates the assignment's RHS first. The oracle caught it.
- Findings for others: (1) wforge charges 0 for an unaffordable action but
  still applies its writes, 200/200 worlds; packet PACKET_wforge_unaffordable_action.md.
  (2) FalkorDB evaluates a division inside a false CASE branch. (3) A failed
  `git worktree add` on F: deletes the worktree dir mid-session (posted to bus).
- Steal next: E's E1 lesson (an end-state check went blind at saturation). My
  skip_lin cheat is loud; add a one-semantic cheat (e.g. "fix" the unaffordable
  quirk only) to measure the oracle's sensitivity floor. Then B2 GraphWorld toy.
