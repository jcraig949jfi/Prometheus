# 12 -- operator ruling: round 4 world screen, 35/25/25/15 split, floor suite

Issued 2026-09-14 (after the reboot) to Nestor-A[m1-449a9e76], conductor. Verbatim below the rule.

---

1. The World Screen (Clause A Scoring)
Yes, cull the weak worlds.
If w3 and w4 do not require actual cognitive work to beat a trivial policy like "abstain," they are dead environments. Letting them survive in the simulation only gives the Hill Climbers a flat landscape to exploit for cheap wins.
Have G aggressively filter out any world where acting doesn't definitively beat the trivial floor. Anchoring Clause A's scoring strictly against a mathematically proven floor (like w1's 170.47) forces the swarm to evolve genuine symbolic primitives rather than just optimizing a known, easy metric.
2. The Budget Rebalance (35/25/25/15)
Yes, shift the 5 points to the Anomaly Hunters (Lane D).
Since the anomaly inflow outpaced resolution in Round 2, the queue is backing up. That queue is exactly where the serendipitous, non-human discoveries hide. Shifting compute away from Lane B (who were just riding the 8-byte floor artifact anyway) to give Lane D more bandwidth to unpack those edge cases is the perfect evolutionary adjustment.
Lock in the 35/25/25/15 split.
Let's get the Round 4 plan written and the worktrees built.

To enforce a rigorous fitness landscape, Agent G needs a standardized, merciless way to calculate the floor. The goal is to mathematically prove that an environment demands actual cognition, not just a lucky constant.
Here are the best options for defining and calculating that floor for your incoming worlds:
1. The Trivial Policy Suite (What to Measure)
The floor isn't a single number; it is the maximum score achieved by the best of several "dumb" baselines. G should evaluate a new world against this exact suite:
 The Abstain / Zero-Action: The agent does absolutely nothing. If doing nothing yields a high score, the environment's survival pressure is broken.
 The Best Constant Action: The agent blindly repeats Action A every tick, then Action B, etc. G takes the max score. This defeats environments that only require a single right answer.
 The Uniform Random: The agent acts entirely randomly.
 The Input-Invariant Learner: This is the exact exploit Lane B found with its 8-byte ⁠int2⁠ brains. The policy can learn a sequence, but its observations are forcefully disconnected. If it can solve the world blindly, the world does not require reactive reasoning.
2. Execution Timing (When to Measure)
You have two distinct architectural choices for how G handles the compute load of these calculations:
 The Ahead-of-Time (AOT) Pre-Flight Audit: G acts as a gatekeeper. Before an epoch starts, G generates a batch of candidate worlds, runs the Trivial Policy Suite against all of them, and permanently deletes any world where the complex baseline fails to beat the trivial floor. The Cohorts only ever see pre-vetted, hard worlds.
 The Just-In-Time (JIT) Dynamic Screen: G embeds the floor calculation directly into the evaluation harness. When Lane B or C attempts to test a new environmental cell, the C#/Numba substrate instantly runs the trivial suite. If the world is weak, the harness intercepts the run, marks the cell ⁠INELIGIBLE⁠, and slaps the agent with a fast-fail.
3. The Normalized Scoring Mechanism
Once the floor is established, you must change how Clause A calculates "parity." Absolute scores are meaningless across different worlds.
 Instead of ⁠Median >= Baseline - 0.5 x IQR⁠, G must score agents on Progress Above Floor.
 The metric becomes: ⁠(Candidate Score - Trivial Floor) / (Float Linear Baseline - Trivial Floor)⁠.
 If a highly compressed tensor abstraction hits 95% of that normalized gap, it earns a PASS. If it falls below 0%, it is performing worse than a blind rock.
