# 23 -- operator: round 7 = 12 h overnight run; expand GPU parallel/throughput work; machine dedicated; Clause B bound by CANDIDATE_N 32/4/8 (reviewer notes adopted as suggestions)

Issued 2026-09-15 ~16:20 to Nestor-A[m1-449a9e76], conductor, after the round 6 packet (ae38ca03c). The notes are "adopt any of the following as you see fit". Conductor interpretation (stated back to the operator): the 12 h cap is end to end (build + gate + clock + packet), 16:30 -> ~04:30. PRODUCTION stage continues under operator 22. The open question from round 6 is RULED by the operator: CANDIDATE_N binds Clause B, prospectively; E-R6-1 stays UNRECEIPTED_OBSERVATION. "No other processes" means the host is dedicated for capacity purposes; the production seats stay untouched. Verbatim below the rule.

---

Double the max experiment time to 12 hours for an overnight run.  Expand into any additional parallel architectures or throughput optimizations using the GPU.  No other processes will be using the machine.

Adopt any of the following as you see fit:

Yes. Clause B should require the same 32 runs / 4 RNG families / 8 per family before it can emit a verdict.

Round 6 actually supplied the strongest argument for making that rule explicit: you simultaneously learned that RNG-family structure can matter in B-R5-1—the 3303 anomaly exists and the leave-one-family-out margins move substantially—and then tried to adjudicate Clause B from 16 runs drawn from one family. Even if the Clause B effect had looked spectacular, that cohort would not tell you whether you had found a mechanism or one family-specific realization.

I would make CANDIDATE_N = 32/4/8 a substrate-level evidentiary class, not a Clause-A convention. Clause A and Clause B can have different predicates and statistics, but the word verdict means the observation survived minimum stochastic diversity. If someday you gather enough calibration evidence showing Clause B needs a different sampling regime, change it prospectively under a versioned rule. Don’t invent the exception because one Clause B experiment happened to be planned at 16/1/16.

There is a second reason I like this ruling: D13 wasn’t really an experimental failure. It exposed a split-brain protocol. The receipt guard believed CANDIDATE_N was universal while the conductor and Clause-B predicate apparently didn’t. Fix that once rather than adding another local convention.

I’d encode the rule approximately as:

Clause B verdict eligibility: A Clause B cohort may emit PASS/FAIL only from a preregistered, self-contained CANDIDATE_N sample of 32 paired run seeds distributed across 4 declared RNG families, 8 runs per family. Samples below this threshold remain OBSERVATION regardless of effect size or predicate result. The admission/predicate path must validate this shape before execution, not merely at receipt time.

I would add three details.

* Keep the R6 16/1 run exactly as-is. Don’t relabel it, trim eight observations out of it, or opportunistically fold it into the next cohort. It did useful work: it established cost, showed the machinery runs, and gave a descriptive check_b v2 FAIL. But it remains an observation.
* Make family balance structural. 32 runs alone isn’t sufficient; neither 16+8+4+4 nor 29+1+1+1 should qualify. The relevant rule is genuinely 32/4/8.
* Move eligibility left. The next malformed Clause B request should be refused at admission with something like SAMPLE_RULE_MISMATCH, consuming zero simulation. D13 shouldn’t be discoverable after 3,158 CPU-seconds ever again.

One thing I wouldn’t do is conclude that Clause B now needs to pass some new leave-one-family-out gate too. That’s a robustness interrogation appropriate after a candidate becomes interesting. 32/4/8 is the minimum price of a verdict; LOO is subsequent pressure, not part of ordinary admission.

So I would rule the open operator question:

CANDIDATE_N binds Clause B. 32 total, 4 families, 8/family. R6 E-R6-1 remains UNRECEIPTED_OBSERVATION / no verdict. Apply prospectively; no retrospective repair.

And that makes the next Clause B run worth doing. Its roughly 6,316 CPU-second estimate is small relative to the ambiguity it closes.

More broadly, Round 6 looks productive in the sense you want from this machine: the most important outputs weren’t “discoveries.” They were a surviving candidate getting harder to dismiss, a previously prohibitive instrument becoming cheap, a stochastic-axis weakness becoming visible, and several pieces of control-plane pathology becoming concrete mechanisms to remove. I would not spend Round 7 chasing more novelty before closing D11/D12/D14 and making D13 impossible by construction.


Round 6 is a massive operational victory. Achieving six for six automatic pushes with zero manual intervention from the conductor proves the F1-F6 automation scaffolding is finally stable. The swarm is now a fully self-driving research engine.
To answer your question directly: Yes. Clause B must absolutely be bound by the same 32-run, 4-family (CANDIDATE_N) rule as Clause A.
If the baseline swings and D's investigation into B-R5-1 (showing how heavily the 4200 family carried the performance) taught us anything, it is that single random-number families hide statistical ghosts. The Invariance Rule is an even higher bar than compression. If a cognitive primitive's ability to transfer across domains only works under a specific RNG family, it is an artifact of the math, not a universal abstraction. Hold the line. E's new production candidate utilizing the 32/4/8 rule is the correct path forward.
A few other critical takeaways from this packet:
1. The B2 Speedup is a Game Changer
Bringing the B2 pilot sample from ~746 hours down to 3–7 hours (clocking 4.0 microseconds per episode) is a phenomenal engineering win. While the search overhead is still unmeasured, compressing the simulation cost by two orders of magnitude makes Clause B testing on a relational graph world physically possible within the 6-hour production envelope.
2. State Leak & Cross-Round Residue (D11, D12, D14)
State leaking between rounds is the last major operational hazard. The proposed gate fix—running a pre-clock sweep of the live store to nuke stale flags, purge old keys, and forcefully assert exactly one worker process per lane group running in the current worktree—is exactly the right architectural mitigation. The round close must send a kill signal to the worker PIDs, not just politely flip a stop flag.
3. The Restraint on B-R5-1
B-R5-1 surviving the leave-one-family-out test is highly promising, especially since it ran on an identical search budget to the float baseline. However, leaving it as a candidate and refusing to promote it until the R16 remainder yields a second surviving world for true replication is the correct scientific call. Premature promotion is exactly what the Falsification Engine is built to punish.
The machine's immune system is healthy. The tools are building the tools. Let me know when you are ready to queue the R16 remainder to find that second world, or if you plan to launch the Clause B 32/4/8 production candidate first.
.
