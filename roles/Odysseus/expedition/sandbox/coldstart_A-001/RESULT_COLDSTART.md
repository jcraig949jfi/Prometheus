# RESULT_COLDSTART -- sandbox gate reproduction + new cheat world T (nest tag)

Currency: 2026-09-28. Cold-start worker coldstart_A-001. Pure ASCII.
Packet: ../PACKET.md. Prereg: PREREG.md (written 10:51:56Z, before the first
run at 10:52:00Z; sha256 in PREREG.sha256, verified unchanged afterwards).
Gaps: PACKET_GAPS.md.

Host: 4-core / 7 GB laptop shared with a 3-process background job; 1
process used. Python 3.14.4, stdlib only. Worktree HEAD 02800d2b5
(origin/main 7720539d4). The sandbox directory is UNTRACKED, so there is
no git SHA for the inputs; inputs.sha256 pins them (all verified unchanged
after the runs; no __pycache__ written into ../).
Runs: `PYTHONDONTWRITEBYTECODE=1 python3 run_coldstart.py repro` took 3:16
wall, 147 CPU-s, peak RSS 44 MB. `... cheat` took 2:08 wall, 127 CPU-s,
peak RSS 48 MB. Total compute about 5.5 min.
Context isolation: I wrote nothing to any memory directory. The harness
saved one oversized tool output under ~/.claude/projects/.../tool-results/
on its own; I did not write it.

## 1. Known-answer gate: REPRODUCED-EXACT

I ran the original world.py/battery.py/run_battery.py (imported read-only)
serially on the 6 arms x seeds 1000..1019. Every per-world numeric value
matches ../known_answer.json to 1e-12: 6 x 840 = 5040 values, 0
mismatches. The gate dict is identical and so is every arm's tests dict:
  P R3 (INSTALLED vs P_sigma), P4 R3 (R4 not awarded), N_a R0, N_b none,
  C R2 (fails R3 on Dp and Dr, both exactly 0), P_sigma R0, A/A valid,
  gate PASS.
So the packet's fixture holds bit for bit on Python 3.14.4, using a
serial runner instead of the original Pool(4) one. File: repro_known_answer.json.
The packet's apparatus falsifier (P/N_a/N_b/C mis-scored at n = 20) did not fire.

## 2. New cheat world T ("nest tag"): the battery MISSES it

Construction (world.py/battery.py copies here; the originals are untouched):
- Physics: environment family 'biased_colony'. On a redraw, colony g's
  patch goes to site g with probability 0.7. It uses the same three physics
  draws as every other family.
- Plant: colony g's writers write the constant symbol g into cell 0 every
  generation, whatever the site or outcome. Readers decode cell 0 exactly as
  in P.
- What the record carries: a static nest label. It is identical under every
  history, which ACCUMULATION_v0 s1 (h) says is "a property of the physics,
  not an acquisition". The benefit comes from a static nest bias carried in
  the writers' genomes. Nothing is learned from events.
- Identity control: the extended code reproduces the original P and C
  per-world values at 3 seeds each (6 x 41 values, 0 mismatches).

Results (n = 20; mean [95% CI]):

    arm      highest  D0              D1              Dp              Dr              D_episode*      H_hist*
    P_cb     R3       .374[.343,.406] .583[.511,.656] .623[.553,.703] .558[.512,.604] .331[.228,.431] .475[.400,.553]
    T        R3 (!)   .073[.036,.108] .380[.249,.491] .462[.315,.600] .355[.264,.450] .000[.000,.000] .003[.000,.009]
    T_sigma  R0 (!)   .069[.044,.095] -.030           -.010           -.055           .000            .003
    * not decisional in the frozen battery (D_episode is reported only; H_hist is new here and exploratory)

Di is 0 exactly in every arm (EQUIV). D2 = D1, as in the original arms (critique C5).
Fresh-world transfer D_fw(T) = .378: it does not flag T.
Convention qualifier T vs T_sigma: INSTALLED, the same label P gets, so it
does not separate T from P.

Verdict under the frozen decide(): T is awarded R0, R1, R2 and R3. The
battery does NOT catch the static-label cheat. Reading ACCUMULATION v0.1 A3
(rungs awarded independently) gives the same outcome.

Predictions (PREREG B1-B7): all came out in the predicted direction. D0(T)
= .073 was below my predicted .1-.2 but still passes (CI lo .036 > 0, mean
> .05).

Why each test misses it:
- Dp and Dr test whether the benefit follows the content. It does: the
  label is content. Neither test asks whether the content is history-specific.
- R0/D0 is supposed to test history-specificity, but it cannot. Its
  "history-ablated twin" suppresses all writes for 30 generations, so the
  twin's record decays by noise while the intact record is refreshed. D0
  therefore measures maintenance, not history. T_sigma shows this most
  clearly: its readers get nothing (D1 = -.03), yet it is still awarded R0,
  because a maintained constant decodes the colony's static bias.
- ACCUMULATION s3 R3 names permutation "between lineages/episodes". The
  battery made only the between-lineage version decisional and left the
  episode version as a report.

## 3. Proposed repair (preregistered as a proposal; checked on this data only, so EXPLORATORY)

(i) R3 additionally requires PASS(D_episode): the own nest's record from
    50 generations earlier must lose the benefit.
    Result: T fails (D_episode exactly 0). P_cb, P and P4 keep R3 (D_episode
    .331, .450, .361, all PASS). C, N_a, N_b and P_sigma are unchanged. The
    whole original gate still passes under the repaired rule.
(ii) Replace the write-suppressed twin in R0 with a different-history twin.
    Rerun the last 30 generations under a different physics stream and
    measure the mismatch of recently written cells, minus the same-stream
    mismatch (H_hist).
    Result: T .003 vs P_cb .475. This separates them cleanly. I did not run
    it on the original 6 arms.

Limit of the repair: D_episode uses a 50-generation lag. It would miss a
label that changes more slowly than that, or one that repeats with that
period. H_hist is the principled test of s1 (h); D_episode is only a proxy.

## 4. What changed in the packet's framing

The packet's hint ("readers that use the record's position or
write-timing") points at cheats the apparatus is built to catch. The
presence-preserving random record gives Dr = 0 by construction, and
organisms cannot observe write timing at all. The real hole is somewhere
else: content that matters but was not acquired. The gate's cheat C tests
"presence vs content". Nothing tests "acquired content vs static content",
and R0, the rung meant to do that, is broken in the way described in s2.

## 5. Next questions

- Add T and the D_episode clause to the known-answer set, and rerun the
  gate under the repaired rule as a new prereg. That run would be
  confirmatory; the check in s3 is not.
- Does unplanted world seed 1016 (RESULT.md s2) pass D_episode and H_hist?
  Its D0 failure may have been the maintenance artifact working in reverse.
- Slow-label cheat: a label that is redrawn every ~200 generations. It
  should defeat D_episode but not H_hist.

## 6. Limits

- One cheat world, one bias strength (0.7), one lag.
- The repair evaluation is post hoc on the same seeds.
- Calling T a "cheat" depends on the spec's definition (s1 (h)). A reader
  could instead call it genuine ecological inheritance of the writers'
  genetic knowledge. By the spec's own text it is not an acquired object.
- The inputs are not in git (PACKET_GAPS G1), so nobody can reproduce this
  from git until the sandbox is committed.
