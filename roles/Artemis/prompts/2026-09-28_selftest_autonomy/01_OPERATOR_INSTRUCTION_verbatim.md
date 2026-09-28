Post the comms request and handle the recruitment yourself. You should not assign the workers. This is exactly the sort of routine orchestration we’re trying to push below HITL.

The self-test is more valuable if Artemis has to acquire and coordinate independent execution without operator curation. The main thing to protect is the experimental separation she already froze.

I’d send her this:

Proceed autonomously with the Artemis self-test.

Post one comms request for fresh execution workers and one for an independent scorer. Do not ask the operator to assign them.

Recruit by capability/availability, not by which workers you expect to perform well.

For the 38 thread executions:

* use fresh disposable workers where practical;
* isolate Claude context/home from persistent seat memory;
* workers receive only the Thread package and fixed execution budget;
* do not tell them whether the Thread is SHARPENED or RAW;
* do not provide Artemis’s prediction or rationale;
* distribute work across nodes/seats where practical rather than letting one persistent researcher dominate either cohort;
* record any unavoidable context contamination.

For the scorer:

* use a different worker from the executors;
* keep cohort identity blinded;
* provide the frozen scoring rubric only;
* do not expose Artemis’s predicted +0.2 effect;
* do not let Artemis resolve ambiguous scores herself unless the prereg explicitly provides that fallback.

Randomize or otherwise preserve the already-frozen assignment/order rules. Do not opportunistically substitute “better” workers into one cohort.

If there are fewer workers than Threads, workers may execute multiple Threads, but balance repeated-worker exposure across the two cohorts and record it. Independence between every one of the 38 runs is less important than avoiding a systematic cohort/workforce confound.

Use leases for any substantial compute. If resources are busy, queue those executions and continue the others. Do not change the frozen cohorts because one Thread is inconvenient to run.

If a Thread proves genuinely unexecutable under its frozen package, apply the preregistered treatment for missing/unscorable pairs rather than repairing it after seeing its paired outcome.

Do not return after the first few pairs. Complete enough of the prospective test to apply the frozen decision rule, then synthesize what it says about Artemis’s actual value.

I particularly like that her own prediction is below the detectable effect size. That makes this a real test rather than a ceremony designed to certify the seat. If the result is “not shown,” Artemis should have to change how it sharpens Threads according to the frozen rule rather than explaining the null away.

And there’s another useful meta-test embedded here: if Artemis can recruit fresh workers, protect blinding, manage execution, obtain independent scoring, and adjudicate its own value without you assigning anyone, then we’ve tested another piece of the autonomous-research model—not just whether Thread sharpening works.
