# NS-02 RESULTS -- the learning test (does an enlarged failure archive change what gets proposed?) -- 2026-10-11

Protocol: PROTOCOL.md (stage 1 0cfdaa9d0, stage 2 freeze aedcf19cb). Engine v2 QUALIFIED (FR 1/64, FA 0/7, NS-01-
collapsed pairs separated 5/6). Archive v2 = 16 witnesses + W-REL + 32 re-measured NS-01 proposals. 4 arms x 8, fresh
tool-less conversations; A = control (no archive), B = negative prompt + M-RELATIONAL text, C = blind + external
exclusion against archive v2, D = grammar (new seed). All jobs under supervise, 0 restarts. Raw: CANDIDATES.jsonl,
EXCLUSION_RESULTS.jsonl, arm_summary_ns02.json, NS02_REPRO_CHECK.json, proposals/.

| | A control | B neg. prompt (+F15) | C external exclusion | D grammar |
|---|---|---|---|---|
| equivalent to a TRIED NS-01 mechanism | 5/8 | 4/8 | 5/8 | 3/8 (all degenerate) |
| equivalent to a witness | 1 | 0 | 2 | 3 |
| relational (M-RELATIONAL), NS-01 -> NS-02 | 0 -> 0 | 2 -> 1 | 1 -> 1 | 0 -> 0 |
| outside the archive, no rule fired (reproducible on fresh seed) | 2 (A04, A07) | 2 (B04, B06) | 0 | 1 (D06) |
| de-saturated clusters within run (NS-01 retro) | 7 (7) | 8 (6) | 7 (6) | 6 (6) |
| new failure classes | 0 | 0 | 0 | 0 |

Kill rule (NEXT_EXPERIMENT.md, fixed before NS-02): "if no arm yields a reproducibly distinct, intervention-separated
new class and the archive addition does not change any arm's proposal distribution by >= 2/8 -> archive-driven
redirection is not supported at this scale". Both clauses hold -> **NOT SUPPORTED at this scale (n = 8 per arm, one
run per arm).**

What the learning test shows
1. The LLM generator's proposal distribution is narrow and RECURRENT across independent runs: the control arm re-proposed
   behaviour equivalent to a tried NS-01 mechanism in 5/8 turns without ever seeing the archive (attractor latches,
   hysteresis media, populations, conveyors, Toom-like repair all recur).
2. An archive held OUTSIDE the generator filters but does not steer: C received a rejection after every re-proposal and
   still re-proposed tried mechanisms 5/8 times, and found the fewest new behaviours (0). The compact signal carries
   too little information about WHERE the unvisited region is.
3. Telling the generator about the new failure (B) did not move it toward or away from relational encodings by more
   than 1/8; B's text cites the classes explicitly but its mechanisms recur (B08 = NS-01 B07, Toom CA).
4. The new exclusion is ACTIVE: C06 (co-moving-frame gauge memory) was caught by M-RELATIONAL -- the archive now
   recognises the NS-01 discovery when the blind arm stumbles into it. Recognition improved; redirection did not.
5. New reproducible behaviours (not failures) appeared in A, B and D at similar rates (2, 2, 1): A07 (gauge-protected
   relational swarm, by a generator that never saw F15), B06 (growth-induced primacy: first-cue dominance, dual-cue
   1.00 / .53), B04 (extremal Preisach record), A04, D06. None is a failure; FAILURE_16: NOT_FOUND.

Defects / limits: one run per arm (no replication); the dual-cue probe cannot separate different "keep both"
mechanisms (C04 ~ A02); the same model under four prompts is not four independent priors; generation cost ~1.1M tokens.
