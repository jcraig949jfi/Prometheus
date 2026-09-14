"""Cut: spin-pathfinder-priority-inversion-1997 (ancestry-aware; SOURCE_READ of the 47-line Promela model; INTERVENED by
nyx/atlas/experiments/pathfinder_ablation.py). The fossil is a MODEL inside the SPIN tarball; SPIN itself (the verifier) is
the separate fossil spin-6.5.2-holzmann and is not cut here -- it is the instrument."""
from nyx.atlas.author import Cut

M = "F:/Prometheus/vault/fossils/spin-pathfinder-priority-inversion-1997/upstream/tree/Spin-version-6.5.2/Examples/pathfinder.pml"
R = "nyx/atlas/fingerprints/spin-pathfinder-priority-inversion-1997/ablate_rule_vs_mutex.json"
c = Cut("spin-pathfinder-priority-inversion-1997", mode="ANCESTRY_AWARE",
        inspected=["Examples/pathfinder.pml (all 47 lines)", "recipe.json", "run/20260912T211155Z/runs-*.stdout.txt"],
        evidence=[("SOURCE_READ", M), ("EXECUTED", R + " baseline: errors 1 at depth 4 (Nyx run, matches Techne)"),
                  ("INTERVENED", R + " A1-A4 + control")],
        note="two processes, three shared variables, one guard clause: the whole body is smaller than this note")

rule = c.organ("fixed_priority_run_rule", human_name="`provided (h_state == idle)` -- the scheduling rule", status="ACCEPTED",
    human_interpretation="the low-priority task may run only while the high-priority task is idle (strict priority preemption)",
    mechanism="every transition of one process is guarded by a predicate over ANOTHER process's state variable; the guarded process is ineligible to take any step -- including the step that would release a resource -- whenever the predicate is false",
    input="the other process's state variable", output="eligibility of every step of the guarded process", state="none of its own (reads h_state)", update="re-evaluated before every step",
    assumptions=["the high process's 'waiting' state is NOT idle -- a waiting high task keeps the low task frozen"], interface="a Promela `provided` clause; in a real RTOS, the scheduler's ready-queue policy",
    fitness_value_in_ancestor="encodes the lander's fixed-priority scheduler in one clause", failure_landscape="with a resource held by the frozen process: deadlock (measured)",
    ablation="REMOVE (A1): errors 1 -> 0. REVERSE (A3): 0. WEAKEN so that waiting counts as yielding (A4): 0. The deadlock needs this rule AND needs 'waiting' to count as not-idle.",
    decomposability="atomic (one predicate)", composability="any process-eligibility guard", human_prior="named 'scheduling rule' by the model's own comment",
    control="CONTROL_rename_constants: identical model, renamed constants -> errors 1 (the verifier is not keying on names)", cheat="none identified: exhaustive search over 12 states",
    observability="pan reports depth and errors; trail replays the schedule", intervention_readiness="YES -- one-line edits, 1.5 s per verification",
    evidence_grade="INTERVENED", evidence_ref=R, confidence="HIGH (exhaustive verification, 6 variants, control preserved)", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="pathfinder.pml:38 `provided (h_state == idle)`",
    coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "NONE", "update_topology": "EVENT_DRIVEN", "competition": "ARBITRATES", "failure_mode": "STALLS", "stochasticity": "DETERMINISTIC", "feedback": "NONE"})

mx = c.organ("binary_mutex_test_and_set", human_name="`atomic { mutex == free -> mutex = busy }`", status="ACCEPTED",
    human_interpretation="a lock: wait until free, then take it, in one indivisible step",
    mechanism="a guard on a shared variable and the assignment that falsifies the guard are fused into one atomic step, so two processes cannot both pass; release is a plain assignment back",
    input="the shared variable", output="the process proceeds or blocks", state="one three-valued shared variable (free/busy)", update="atomic guard+set; plain reset",
    assumptions=["atomicity of the two-statement block (Promela `atomic`)"], fitness_value_in_ancestor="protects the shared data buffer between producer and consumer",
    failure_landscape="held by a process that cannot run: everyone else waiting on it is stuck (measured with the rule present)",
    ablation="REMOVE the guard (A2, `skip`): errors 1 -> 0 -- the deadlock also needs the lock; mutual exclusion is lost (not measured)",
    decomposability="atomic", composability="any shared-variable lock", human_prior="'mutex' is the model's own variable name",
    control="see rule organ", cheat="none identified", observability="mutex variable is `show`n in the trail", intervention_readiness="YES",
    evidence_grade="INTERVENED", evidence_ref=R, confidence="HIGH", portability="YES", compatibility="UNKNOWN", utility="UNKNOWN",
    source_boundary="pathfinder.pml:28,41 the two atomic blocks",
    coverage={"input_topology": "SCALAR", "output_topology": "DECISION", "state_amount": "CONSTANT", "update_topology": "EVENT_DRIVEN", "competition": "ARBITRATES", "stochasticity": "DETERMINISTIC"})

c.reject("priority-inheritance option (the model's own switch)", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY",
         evidence="record.behavioral_entry_point says 'toggle the priority-inheritance option in pathfinder.pml'; the file contains no such option, no #ifdef, no second mode; Techne's own recipe toggles nothing and verifies the model as-is",
         note="TECHNE FEEDBACK: the record names a switch the body does not have. The fix humans applied on Mars (enable priority inheritance on the mutex) is NOT in this fossil; a repaired model would be a separate specimen")
c.reject("the medium-priority task of the Pathfinder story", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY",
         evidence="the human account needs three tasks (low holds, medium preempts, high starves); the model has TWO processes and deadlocks anyway, because `provided (h_state == idle)` freezes low whenever high is merely waiting. A4 shows the deadlock vanishes when waiting counts as idle.",
         note="the model's rule over-approximates: it stands in for the medium task by treating a blocked high task as if it still occupied the CPU. Famous-name vs body divergence, recorded as a surprise")
c.reject("the SPIN verifier (state-space search, partial-order reduction, trail replay)", reason="OTHER",
         evidence="present in the same tarball and built by the recipe, but it is the INSTRUMENT that observes the model, not machinery of the specimen; it is the fossil spin-6.5.2-holzmann")
c.reject("h_state / l_state variables", reason="STATE_OBSERVATIONALLY_IRRELEVANT",
         evidence="l_state is written and never read by any guard; h_state is read only by the rule organ. l_state is display state for the trail (`show`), not machinery", note="half of the model's declared state does not participate in any transition")

c.edge(rule, mx, "gates", note="the rule decides whether the process holding the lock may reach its release step")
c.edge(mx, rule, "feeds", note="blocking on the lock puts high into 'waiting', which the rule reads as not-idle: the cycle that is the deadlock")
c.edge("ENVIRONMENT", rule, "feeds", note="in the lander the rule is the RTOS scheduler; here it is a clause")

c.pressure("hard_deadline_with_shared_resource_across_priorities",
    condition="tasks of different urgency share one resource that must be held exclusively; the urgent task must complete within a bound; a watchdog treats lateness as failure",
    resource_or_constraint="one exclusive resource + CPU time ordered by priority", failure_condition="the urgent task waits on the resource while its holder is not permitted to run",
    world_punishes="a missed deadline (the lander reset itself repeatedly)", world_rewards="the urgent task getting the resource within its bound, regardless of who holds it",
    observable_consequence="a schedule with no enabled step (pan: invalid end state at depth 4)", vacuity_condition="a single priority level, or no shared resource",
    trivial_shortcuts="give everything the same priority (loses the timing guarantee the priorities exist for)", cheat_control="the CONTROL variant (renamed constants) still deadlocks; A1-A4 each remove the deadlock by removing a real precondition",
    cost_class="12 reachable states; the failure is structural, not statistical", source_evidence="model comment lines 1-16 + record.human_failure_condition",
    purpose="PURPOSE: a spacecraft computer that shares a bus-data structure between a fast task and a slow task")

c.residue("EXPLAINED_BY_CURRENT_CUT", ["the emergent deadlock is fully accounted for by the two organs and their two composition edges: removing either organ, or breaking the feeds edge (A4), removes it",
                                     "NOT explained by this fossil: what humans did to fix it (priority inheritance) -- absent from the body"],
          note="a 2-organ fossil whose interesting object is a composition edge, not an organ")
c.save(state="DEEP")
