# W-F LOG  T-CT-1

A0 2026-09-27 read brief, COMMON_RULES, INSTRUMENT_CARRIER_SWAP, lens.py,
   spikes/s_ct.py + out/s_ct.json, c1b.ticks. Counted SIGNAL cells from rows
   (no simulation): 166. Wrote PLAN.md (frozen) before any run.
A1 CPU smoke 523e5f65 (1 cell, 2 threads): 64 s, class SITE (smoke file out/smoke_cpu.jsonl; not part of census). GPU lease acquired token 677c5f429901 ttl 90 min.
A2 23:16Z GPU smoke 523e5f65: 71 s (GPU slower than CPU; eager loop is launch-bound); CPU/GPU tables identical. cpu8 BUSY (W-A) so ran 2 GPU shard processes, 1 thread each (within the 2-thread rule): out/census_s{0,1}.jsonl.
A3 00:37Z census complete: 166/166 cells, 0 errors, two shards ~80 min wall. GPU lease renewed once (token bc8ce4d6f5f9) then released at 00:37Z. Ran analyze.py (frozen models).
A4 00:40Z frozen decision: tree(8 dials) CV 0.730 vs family-only 0.797, gain -0.067
   (95% over repeats -0.126..-0.028) -> "family selects". 124/166 readable
   (42 UNREADABLE, normal lo99 < 0.60). No F6 HISTORY flag (pre-cue swap never
   FLIPs), w NO-EFFECT in all 124.
A5 POST-HOC (not in PLAN, labelled exploratory): explore_nonhold.py
   (out/explore_nonhold.txt): non-HOLD readable n=39 from 11 physics points;
   no model beats ~0.40 (family 0.384, tree 0.398). One RELAY physics+env point
   holds SITE 4 / CHANNEL 4 / JOINT 4. JOINT cells: site_acc + chan_acc = 0.999
   (complementary mixture, 14/14). Pilot-overlap check: 10/12 same class; the 2
   RELAY changes (62a7fff9 CHANNEL->SITE, c16d5231 CHANNEL->JOINT) follow from my
   mid tick being 1 tick later than the pilot's (F2 handoff), declared in PLAN.
A6 REPORT.md write refused by harness; full report delivered in the final message to Ananke. GPU lease released (A3). No git operations.
