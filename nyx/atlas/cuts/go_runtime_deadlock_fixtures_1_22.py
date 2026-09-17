"""Cut: go-runtime-deadlock-fixtures-1.22 (the Go runtime's testprog deadlock programs and their crash_test harness; Stage A ORGAN0 with one
pressure; SOURCE_READ on M3; position 57 of the 2026-09-17 NOT_CUT order). Read: deadlock.go 1-100 (the registrations and the first
seven programs), crash_test.go 190-230 (testDeadlock: the expected fatal string), main.go in full. NOT in the body: the detector itself
(runtime/proc.go checkdead), which is what these programs exercise. Nothing ran (Go toolchain absent on M3).
"""
from nyx.atlas.author import Cut

D = "vault:go-runtime-deadlock-fixtures-1.22/upstream/deadlock.go"; T = "vault:go-runtime-deadlock-fixtures-1.22/upstream/crash_test.go"
c = Cut("go-runtime-deadlock-fixtures-1.22", mode="ANCESTRY_AWARE", inspected=["deadlock.go 1-100", "crash_test.go 190-230", "main.go 1-35"], evidence=[("SOURCE_READ", D + ":1-100"), ("SOURCE_READ", T + ":190-230")],
        note="the body is a set of STIMULI, not a mechanism: each registered program constructs one blocking topology (every goroutine parked on a select with no cases; the main thread locked to an OS thread and parked; a locked helper plus a parked main; all goroutines exited via Goexit; thread exhaustion under a thread cap; stack overflow; recursive panics) and the harness asserts the runtime's exact fatal message. The detector that turns 'all goroutines are asleep' into a fatal error lives in runtime/proc.go, outside the body. No organ can be cut; the pressure the fixtures define is recorded")

c.reject("checkdead() and the scheduler bookkeeping it reads (sched.nmidle, nmspinning, locked M counts, timers)", reason="OTHER", evidence="NOT IN THE BODY (runtime/proc.go); the fixtures name its outputs only", note="record note for Techne: the mechanism this specimen is preserved for is not in the vault; the fixtures are the world, the runtime is the organism")
c.reject("the crash-handler, panic-traceback and Goexit-ordering programs (RecursivePanic*, GoexitInPanic, PanicAfterGoexit, PanicTraceback, GoschedInPanic, SyscallInPanic, PanicLoop)", reason="OTHER", evidence=D + ":24-41 (names)", note="stimuli for other runtime properties (panic ordering, traceback format), not deadlock")
c.reject("main.go's name -> function registry", reason="GENERIC_LANGUAGE_MECHANICS", evidence="main.go 1-35")

c.pressure("a_runtime_must_declare_deadlock_exactly_when_no_goroutine_can_ever_run_again_distinguishing_that_from_goroutines_parked_on_timers_locked_os_threads_cgo_and_thread_caps_and_must_say_so_with_one_fixed_message",
    condition="an organism schedules goroutines onto OS threads; it must detect the global state 'no runnable goroutine and none can be woken by any future event' and abort with a fixed message; near-misses exist: a goroutine locked to a thread and parked (still a deadlock), pending timers (not a deadlock), cgo calls (detection disabled), a thread cap reached (a different fatal error)", resource_or_constraint="a constant-time check at idle transitions",
    failure_condition="a false deadlock report while a timer or external event could still wake a goroutine, or a missed report (the program hangs silently)", world_punishes="counting only runnable goroutines; ignoring locked threads; ignoring timers", world_rewards="a check over idle and spinning thread counts plus locked-M accounting, gated off under cgo",
    observable_consequence="the seven deadlock programs must each abort with the exact string 'fatal error: all goroutines are asleep - deadlock!' (or the Goexit variant), and the non-deadlock programs must not; the harness reads the first line of output", vacuity_condition="a single goroutine that returns", trivial_shortcuts="a watchdog timeout (which reports late and cannot distinguish slow from stuck)",
    cheat_control="an organism told which programs deadlock must reproduce the harness's verdicts exactly; a runtime with the locked-thread accounting removed must miss LockedDeadlock / LockedDeadlock2 (the fixtures exist because it once did); a runtime that ignores timers must false-alarm on a program sleeping in time.Sleep: the world must show all three",
    cost_class="CPU-scale", source_evidence="deadlock.go 44-100; crash_test.go 196-230", purpose="PURPOSE: regression fixtures for the Go runtime's deadlock detector (Go authors 2015-)")

c.ancestry("shares_ancestor_with", "the Go runtime (golang/go, runtime/proc.go checkdead) of which these files are a test directory", note="from the record; the runtime body itself is not in the vault")
c.residue("CUT_INSTRUMENT_INSUFFICIENT", ["the mechanism under test is outside the body", "the fixtures were read; nothing ran (no Go toolchain on M3)", "record note: preserve runtime/proc.go beside the fixtures if the detector is the object of interest"], note="ORGAN0 with one PRESSURE: the fixtures are a precise world definition (seven deadlock topologies and the exact expected message), which is what the atlas can keep from them")
c.save(state="ORGAN0")
