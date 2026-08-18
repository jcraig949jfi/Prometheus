# STEERING — James's inbox to the loop (read every pass, never blocking)

Write anything here, any time. The loop reads this file at the START of every pass and
obeys before pulling work. Empty file = full speed on current priorities. This is how
you steer at 5-hour or 3-day granularity without ever being a gate.

Verbs the loop understands (plain English is fine; these are examples):
- REPRIORITIZE: "put the retry-queue work above the DR drain"
- KILL: "kill W-002, it's not worth it" (goes to attempt-autopsy, loop continues)
- VETO: "reverse the auto-taken decision about X"
- REDIRECT: "spend the next passes on the ladder, not the corpus"
- QUESTION: "why did B-003 confidence not move?" (answered in next pass's commit, no halt)

Processed entries get moved by the loop into STEERING_LOG.md with what was done.

---
(empty — full speed)
