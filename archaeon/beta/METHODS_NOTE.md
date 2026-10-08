# Methods note -- seven ways an evolved "competence" was not what it looked like (Archaeon Beta, 2026-10-07/08)

For any seat that evolves programs in WSE event worlds or C6 composed worlds, or that reads old frontier results.
Each rule cites the probe in archaeon/beta/ where it bit. The tooling for rules 2-6 is in one place:
archaeon/beta/controls.py (audit_composed, audit_wse), with a self-test of 4/4 known answers.

1. **Delay lines pass for memory.** If ask timing is fixed, "remember the value" is solved by "output the input from k
   ticks ago".
   - Evidence: 7/7, 8/8 and 4/4 evolved solvers on fixed-timing rungs (B08b); 54% of competent frontier W0 organisms
     (B23).
   - RULE: score memory claims under timing jitter. Use 0-7 NOISE ticks before each ask; 0-3 ticks is beaten by
     lag-window exploits (B13 .79, B21 .82; B08K).

2. **A world that shows a clock gets solved by the clock.** Composed-world observations carry tick and position
   words.
   - Evidence: the best surviving frontier organism compares tick with its own position and sweeps the ring (B24).
   - RULE: remove clock / position words (b25 NoClock) before claiming content sensing. Removing them is what first
     produced real sensing (B25/B26).

3. **Echo worlds.** Some worlds are solved by copying an input word to the output. W-artifacts 1.000 equals the echo
   twin exactly (B23c); 11/40 family worlds are echo-solvable (B36).
   - RULE: compare against echo twins. Report transfer on echo-FREE worlds.

4. **The constant twin is not enough; the BLIND twin is the primary control.** Zero every observation word and
   re-score. A policy that does as well blind is not sensing (B26).

5. **Held-out means new episodes, at least 64 episodes x at least 4 world seeds.**
   - Two of my headlines were artifacts and are retracted:
     - training-episode scoring (B46): composed-world scores roughly halved on new episodes;
     - one shared 8-episode held-out sample (B45: "7/8 integrate evidence" became 0/8).
   - Large effects and many-world paired tests survived.

6. **A filtered held-out set inflates contrasts.** Selecting held-out worlds "where the negative control fails" made a
   small margin look large (B33).
   - RULE: always report the unfiltered set beside the filtered one. Paired tests over many worlds (B34/B36) settle it.

7. **Positive controls catch the experimenter's own world bugs.** Write the hand solution first. Hand controls caught:
   - a table inside read-only code (B05);
   - a queue program popping on NOISE ticks (B13);
   - an evidence world whose dynamics rewarded rotation, not knowledge, where the oracle scored LOWEST (B43);
   - a world family whose negative control transferred (B32 v1).

**Substantive results these rules leave standing** (CAMPAIGN_UPDATE_2026-10-08b.md):
- Content sensing evolves once the clock word is removed: 6 sensors in two worlds.
- A world DISTRIBUTION makes it transfer within the family, and 6/8 such foragers implement the general rule.
- **Memory law:** write-once state (latch, guard) is reliably reachable. Update-on-condition state is not, across VM
  (B49), world (B40/B45/B47), incentive (B22/B22b) and selection (B50).
