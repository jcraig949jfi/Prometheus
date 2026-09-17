"""Cut: backoff-2.2.1 (the Python backoff library; ancestry-aware, Stage A DEEP; SOURCE_READ on M3; position 45 of the 2026-09-17
NOT_CUT order). Read: backoff/_wait_gen.py in full (89 lines), backoff/_jitter.py in full, backoff/_common.py 27-58, backoff/_sync.py
in full (the two retry loops). NOT read: _async.py (the same loops with await), _decorator.py (argument plumbing), the tests
(1,639 lines). Nothing ran; the body is pure Python with tests as an oracle: M3-runnable.
"""
from nyx.atlas.author import Cut

W = "vault:backoff-2.2.1/upstream/tree/backoff-2.2.1/backoff/_wait_gen.py"; JI = "vault:backoff-2.2.1/upstream/tree/backoff-2.2.1/backoff/_jitter.py"
CO = "vault:backoff-2.2.1/upstream/tree/backoff-2.2.1/backoff/_common.py"; SY = "vault:backoff-2.2.1/upstream/tree/backoff-2.2.1/backoff/_sync.py"
c = Cut("backoff-2.2.1", mode="ANCESTRY_AWARE", inspected=["_wait_gen.py 1-89", "_jitter.py 1-30", "_common.py 27-58", "_sync.py 1-132"], evidence=[("SOURCE_READ", W + ":1-89"), ("SOURCE_READ", JI + ":1-30"), ("SOURCE_READ", CO + ":27-58"), ("SOURCE_READ", SY + ":1-132")],
        note="the Ethernet / TCP retry rule packaged as a decorator: the wait schedule is a generator (exponential, Fibonacci, constant, or computed from the failed call's value) primed by one send(); jitter is a function of the scheduled wait (full jitter: uniform on [0, wait]); the retry loop stops on a give-up predicate, a try count, or a wall-clock budget, and never sleeps past the budget")

sched = c.organ("wait_schedule_as_a_primed_generator_capped_at_a_maximum_and_advanced_by_sending_the_failure_value", human_name="_wait_gen.expo (factor * base ** n, then max_value forever), fibo, constant, runtime (value(ret_or_exc)); _common._init_wait_gen (send(None) to prime)", status="ACCEPTED",
    mechanism="each schedule is a generator that first yields nothing (to absorb the priming send) and then yields waits on demand; expo yields factor * base^n while below the cap and the cap forever after; fibo likewise; constant iterates a value or an iterable; runtime receives the failed call's return value or exception through send() and computes the wait from it (e.g. a Retry-After header); the loop calls wait.send(value) once per failure",
    input="base, factor, max_value; per failure, the value or exception", output="seconds", state="n (the failure count) inside the generator", update="per failure", assumptions=["a generator is the right shape for a stateful schedule that may need the failure's content"],
    fitness_value_in_ancestor="one interface for every schedule, including server-directed ones", failure_landscape="by reading: expo with no cap grows without bound; the cap is the caller's responsibility", human_prior="binary exponential backoff (Metcalfe & Boggs 1976); Retry-After (RFC 7231)", evidence_ref=W + ":1-89; " + CO + ":27-32", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="_wait_gen and the priming helper",
    coverage={"input_topology": "EVENT", "output_topology": "SCALAR", "state_amount": "CONSTANT", "stochasticity": "DETERMINISTIC", "update_topology": "EVENT_DRIVEN"})

jit = c.organ("full_jitter_drawing_the_actual_wait_uniformly_from_zero_to_the_scheduled_wait", human_name="_jitter.full_jitter (random.uniform(0, value)); random_jitter (value + random()) as the pre-1.2 default; _common._next_wait applies it and clamps to the remaining max_time", status="ACCEPTED",
    mechanism="the scheduled wait is replaced by a uniform draw on [0, wait] (full jitter, the AWS 2015 analysis: lowest total work and contention among the jitter variants) or, in the older scheme, increased by up to one second; the result is then clamped so the sleep never exceeds the remaining wall-clock budget",
    input="a scheduled wait; elapsed; max_time", output="seconds to sleep", state="none", update="per failure", assumptions=["many clients retrying the same failure synchronise their retries unless the waits are randomised; spreading over the whole interval beats adding a small offset"],
    fitness_value_in_ancestor="thundering-herd avoidance; expected wait halves relative to the schedule", failure_landscape="UNKNOWN by run", human_prior="Brooker, AWS Architecture Blog 2015 'Exponential Backoff And Jitter'", evidence_ref=JI + ":6-26; " + CO + ":34-58", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the two jitter functions and _next_wait",
    coverage={"input_topology": "SCALAR", "output_topology": "SCALAR", "state_amount": "NONE", "stochasticity": "SEEDED_RANDOM"})

loop = c.organ("retry_loop_terminated_by_a_giveup_predicate_a_try_count_or_a_wall_clock_budget_with_handlers_at_each_transition", human_name="_sync.retry_exception / retry_predicate (1-132): tries, elapsed, giveup(e), max_tries, max_time, StopIteration from the schedule, on_success / on_backoff / on_giveup handlers, raise_on_giveup", status="ACCEPTED",
    mechanism="call the target; on the named exception (or a predicate on the return value) decide: give up if the give-up predicate says so, the try count is reached, or the elapsed time exceeds the budget (then call the give-up handlers and re-raise or return None); otherwise ask the schedule for the next wait (a schedule that is exhausted also gives up), call the backoff handlers with the details, sleep, retry; success calls its handlers and returns",
    input="a callable and its arguments", output="the result, or a raised exception after giving up", state="tries, start time, the schedule", update="per attempt", assumptions=["failures are transient with some probability; the caller can classify permanent ones (giveup) so they are not retried"],
    fitness_value_in_ancestor="retry policy separated from the call site as a decorator", failure_landscape="by reading: max_tries counts attempts, so max_tries = 1 means no retry; the elapsed check happens before the sleep, so the final sleep is clamped by _next_wait rather than skipped", evidence_ref=SY + ":21-132", confidence="HIGH", portability="YES", compatibility="YES", utility="UNKNOWN", source_boundary="the two loop functions",
    coverage={"input_topology": "EVENT", "output_topology": "EVENT", "state_amount": "CONSTANT", "feedback": "CLOSED_LOOP", "stochasticity": "ENVIRONMENT_RANDOM", "resource_dependence": "TIME", "recovery": "RETRIES"})

c.reject("_async.py (the same loops with await and asyncio.sleep), _decorator.py (on_exception / on_predicate argument handling), the logging handlers", reason="GENERIC_LANGUAGE_MECHANICS", evidence="_async.py, _decorator.py NOT READ", note="plumbing around the three mechanisms")
c.reject("'retry with backoff' as one organ", reason="NAME_HAS_NO_EXECUTABLE_BOUNDARY", evidence="schedule, jitter and termination are separately configurable arguments")

c.edge(sched, jit, "feeds"); c.edge(jit, loop, "feeds"); c.edge(loop, sched, "feeds", note="send(value)")

c.pressure("many_clients_retrying_a_transient_failure_of_a_shared_resource_must_recover_quickly_without_synchronising_into_a_load_spike_or_retrying_forever",
    condition="N organisms hit a shared service that fails transiently; each decides when to retry; the score is time to recovery, total wasted calls and the peak concurrent retry load; some failures are permanent", resource_or_constraint="the service's capacity; a wall-clock budget per client",
    failure_condition="retries synchronised into a spike (the thundering herd), unbounded retrying of a permanent failure, or recovery slower than the failure's duration", world_punishes="fixed intervals; no jitter; no give-up", world_rewards="exponential schedules with full jitter and a give-up rule",
    observable_consequence="peak retry load and time-to-recovery for N clients with fixed / exponential / exponential-plus-full-jitter schedules on the same outage trace (Brooker's simulation)", vacuity_condition="one client", trivial_shortcuts="a coordinator that schedules retries (which the world withholds)",
    cheat_control="an organism told the outage's end time must retry exactly once at that time; N clients with no jitter must show a load spike at 2^k intervals; full jitter must flatten it: the world must show both",
    cost_class="CPU-scale", source_evidence="_wait_gen.py; _jitter.py; _sync.py; Brooker 2015 as cited in the body", purpose="PURPOSE: application-level retry (Fenner 2014-)")

c.ancestry("reimplementation_of", "binary exponential backoff (Ethernet 1976; TCP RTO) with full jitter (Brooker 2015)", note="from the record and the docstrings")
c.residue("EXPLAINED_BY_CURRENT_CUT", ["_async and _decorator unread (plumbing)", "nothing ran; tests (1,639 lines) are the oracle", "M3-RUNNABLE PACKET CANDIDATE: pure Python, no dependency; a packet on full jitter vs no jitter under N simulated clients is preregistrable with the tests as the cheat control"], note="a small body fully accounted for")
c.save(state="DEEP")
