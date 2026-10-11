# wforge F09 -- unpaid writes from unaffordable actions: the red regression, for the substrate owner

From Themis (Moonshot, Lane B), 2026-10-10. To: Daedalus (design v0.3 s12 names Daedalus as owner of the wforge
repair; please confirm or redirect -- see "Ownership" below). Themis does not patch wforge.

## The defect (Astra's review F09, HIGH; operator: ACCEPT, "immediate stop condition" for survival science)

SerendipityFoundry/worldfoundry/wforge/world.py, Encounter.step, phase 1 (lines 211-224 at origin/main, world.py
sha256 31d40f00...24fe, the hash Astra reviewed):

    cost = mag * m.act_cost
    if cost > self.charge[s]:
        mag, cost = 0, 0                     # cannot afford: forced abstain
    self.charge[s] -= cost
    self.actions_used[s] += mag
    for i, x in enumerate(a[:m.act_width]):  # <- reads the ORIGINAL action vector
        amt = x % 8
        if amt:
            self.pending.append((self.tick + m.delay, s, m.act_targets[i], amt * 251))

The forced abstain zeroes the magnitude and the cost, but the write loop still queues every write: an action the
slot cannot pay for moves the world for free. Nestor's independent probe (primordial/soup/b1/probe_unaffordable.py,
2026-09-14) found it in 200/200 worlds.

## The regression: test_wforge_affordability.py (this directory)

    python -m unittest roles/Themis/handoffs/wforge_F09/test_wforge_affordability.py      # from the repo root

Today: Ran 8, failures=4. The four RED tests define the fix; the four GREEN ones guard against over-correcting it.
- RED test_astras_probe: Astra's exact probe (1 register, 1 slot, cost 3, charge 1, world "review-underfunded",
  seed 0): charge [1] and actions_used [0] are already right, but the register moves by 251 vs the zero-action twin.
- RED test_a_delayed_unpaid_write_never_lands: delay 2; the unpaid write lands two ticks later.
- RED test_multi_channel_unpaid_writes: two channels, magnitude 7 > charge 5; both writes land (3x251, 4x251).
- RED test_no_unaffordable_action_moves_the_world_across_a_grid: cost x charge x magnitude x delay x width; every
  unaffordable case moves the world today.
- GREEN: an affordable action is paid and lands; an EXACTLY affordable action (cost == charge) is paid and lands; a
  paid delayed write lands on time; across a grid, every affordable action moves the world by exactly its paid
  writes (amp x 251 mod 65536) and pays amp x cost.
The minimal fix that turns it green: skip the write loop when the action is unaffordable (the same rule the
downstream replicas already implement as their `fix_unaffordable` option, e.g. primordial/soup/b1/np_world.py
L99-100).

## Semantics left to the owner (NOT asserted)

1. Abstention accounting: a true abstain (all zeros) increments `abstained`; a forced abstain does not (the
   counter is incremented before the affordability check). Decide whether a forced abstain is an abstention.
2. Exactly affordable: cost == charge passes `>`, pays, and the slot dies the same tick (charge 0 <= 0) even with
   step cost 0, while its write still lands. Decide whether that is intended.
3. `mag` sums the WHOLE action list, writes use only a[:act_width]: an over-long action list can make an
   affordable action unaffordable by entries that would never be written.

## Blast radius of the fix (please plan for it)

The fix changes trace hashes wherever an unaffordable action occurred. Known pins and copies:
- primordial/ledger/qd/world_set_r8.json L17898 pins world.py's hash, checked by primordial/metric/world_set_r8.py
  L228;
- downstream faithful replicas copy the bug on purpose ("quirks included"): primordial/soup/b1/np_world.py,
  primordial/soup/b1/absorb.py, primordial/nv/cudagraph/world.py (each with a fix_unaffordable switch);
- downstream suites check trace hashes against wforge: primordial/tests/test_u1_torch_world.py,
  primordial/nv/warp/tests/test_world.py, primordial/metric/tests/test_invariant.py.
Nestor's packet (primordial/soup/b1/PACKET_wforge_unaffordable_action.md) already advised a grammar or runtime
version bump (wforge GRAMMAR_VERSION is "wforge-grammar-0.1").

## Ownership

The records disagree: design v0.3 s12/s15 and the only wforge commit (6efa4f88d, "DAEDALUS WORLD FOUNDRY V0") say
Daedalus; roles/Daedalus/RESPONSIBILITIES.md claims SerendipityFoundry but its subtree table omits worldfoundry/;
prometheus/toolbox/ref/__init__.py says owner "Ludus"; Hestia's 2026-10-06 audit (REPORT.md L895-896) says "Owner:
Themis". If you are not the owner, say so and name who is; Themis will forward this handoff unchanged.

Gate (unchanged): no evolutionary survival search on wforge until this regression is green (OP-NF2; design v0.3 s0).
